"""CFRNN (BiLSTM) and CFCNN (CNN) sentence classifiers.

Independent reimplementations of the two neural baselines Sun et al.
(2024) compared against.  No author code, no pretrained embeddings and no
author hyperparameters are available, so the architecture is the standard
Kim-style CNN / BiLSTM sentence encoder with **corpus-trained embeddings**
and explicitly declared, dev-selected hyperparameters.  These are not the
authors' original systems and are never described as such.

Fairness rules enforced here:

* vocabulary is built from the training split only;
* early stopping and epoch selection use the dev split macro-F1 only;
* the test split is predicted once after the best dev epoch is restored;
* one seed for the whole supplement (no seed search).
"""

from __future__ import annotations

import math
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from .cfkw import tokenize
from .metrics import LABELS, evaluate

PAD, UNK = "<pad>", "<unk>"


@dataclass
class TextDataset(Dataset):
    encoded: list[list[int]]
    labels: list[int]

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        return (
            torch.tensor(self.encoded[index], dtype=torch.long),
            torch.tensor(self.labels[index], dtype=torch.long),
        )


def build_vocab(texts: Sequence[str], min_freq: int = 2) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for text in texts:
        counter.update(tokenize(text))
    vocab: dict[str, int] = {PAD: 0, UNK: 1}
    for token, freq in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])):
        if freq >= min_freq:
            vocab[token] = len(vocab)
    return vocab


def encode_texts(
    texts: Sequence[str], vocab: Mapping[str, int], max_len: int
) -> list[list[int]]:
    encoded: list[list[int]] = []
    for text in texts:
        ids = [vocab.get(token, vocab[UNK]) for token in tokenize(text)][:max_len]
        if not ids:
            ids = [vocab[UNK]]
        encoded.append(ids)
    return encoded


def _pad_batch(batch: Sequence[tuple[torch.Tensor, torch.Tensor]]) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    lengths = [int(x.size(0)) for x, _ in batch]
    max_len = max(lengths)
    padded = torch.zeros((len(batch), max_len), dtype=torch.long)
    for i, (x, _) in enumerate(batch):
        padded[i, : x.size(0)] = x
    labels = torch.stack([y for _, y in batch])
    mask = (padded != 0).long()
    return padded, mask, labels


class BiLSTMClassifier(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 128,
        hidden_dim: int = 128,
        dropout: float = 0.3,
        num_labels: int = 4,
    ) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim,
            hidden_dim,
            batch_first=True,
            bidirectional=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_dim * 4, num_labels)

    def forward(self, x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        emb = self.dropout(self.embedding(x))
        out, _ = self.lstm(emb)
        float_mask = mask.unsqueeze(-1).float()
        summed = (out * float_mask).sum(dim=1)
        counts = float_mask.sum(dim=1).clamp(min=1.0)
        mean = summed / counts
        masked = out.masked_fill(float_mask == 0, -1e9)
        maxed = masked.max(dim=1).values
        pooled = torch.cat([mean, maxed], dim=-1)
        return self.classifier(self.dropout(pooled))


class CNNClassifier(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 128,
        filters: int = 128,
        kernel_sizes: Sequence[int] = (2, 3, 4),
        dropout: float = 0.3,
        num_labels: int = 4,
    ) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.convs = nn.ModuleList(
            [nn.Conv1d(embed_dim, filters, kernel_size=k) for k in kernel_sizes]
        )
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(filters * len(kernel_sizes), num_labels)

    def forward(self, x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        emb = self.dropout(self.embedding(x)).transpose(1, 2)
        features = []
        for conv in self.convs:
            conv_out = torch.relu(conv(emb))
            features.append(conv_out.max(dim=2).values)
        pooled = torch.cat(features, dim=-1)
        return self.classifier(self.dropout(pooled))


DEFAULT_CONFIG: dict[str, Any] = {
    "embed_dim": 128,
    "hidden_dim": 128,
    "filters": 128,
    "kernel_sizes": [2, 3, 4],
    "dropout": 0.3,
    "batch_size": 32,
    "learning_rate": 0.002,
    "max_epochs": 25,
    "early_stopping_patience": 4,
    "early_stopping_min_delta": 0.0,
    "max_sequence_length": 128,
    "min_token_frequency": 2,
    "loss": "unweighted_cross_entropy",
    "optimizer": "Adam",
    "seed": 20260717,
}


@dataclass
class TrainingResult:
    method: str
    model: nn.Module
    vocab: dict[str, int]
    best_epoch: int
    epochs_completed: int
    history: list[dict[str, Any]] = field(default_factory=list)
    training_seconds: float = 0.0
    config: dict[str, Any] = field(default_factory=dict)


def _build_model(kind: str, vocab_size: int, config: Mapping[str, Any]) -> nn.Module:
    if kind == "cfrnn":
        return BiLSTMClassifier(
            vocab_size,
            embed_dim=config["embed_dim"],
            hidden_dim=config["hidden_dim"],
            dropout=config["dropout"],
        )
    if kind == "cfcnn":
        return CNNClassifier(
            vocab_size,
            embed_dim=config["embed_dim"],
            filters=config["filters"],
            kernel_sizes=config["kernel_sizes"],
            dropout=config["dropout"],
        )
    raise ValueError(f"unknown neural method: {kind}")


def _predict_scores(
    model: nn.Module,
    encoded: Sequence[Sequence[int]],
    batch_size: int,
) -> list[list[float]]:
    model.eval()
    dataset = TextDataset(encoded=[list(x) for x in encoded], labels=[0] * len(encoded))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, collate_fn=_pad_batch)
    scores: list[list[float]] = []
    with torch.no_grad():
        for x, mask, _ in loader:
            logits = model(x, mask)
            scores.extend(torch.softmax(logits, dim=-1).tolist())
    return scores


def train(
    kind: str,
    train_rows: Sequence[Mapping[str, str]],
    dev_rows: Sequence[Mapping[str, str]],
    config: Mapping[str, Any] | None = None,
) -> TrainingResult:
    cfg = dict(DEFAULT_CONFIG)
    if config:
        cfg.update(config)
    torch.manual_seed(int(cfg["seed"]))
    started = time.perf_counter()

    train_texts = [row["text"] for row in train_rows]
    dev_texts = [row["text"] for row in dev_rows]
    label_index = {label: i for i, label in enumerate(LABELS)}

    vocab = build_vocab(train_texts, min_freq=int(cfg["min_token_frequency"]))
    train_encoded = encode_texts(train_texts, vocab, int(cfg["max_sequence_length"]))
    dev_encoded = encode_texts(dev_texts, vocab, int(cfg["max_sequence_length"]))

    train_dataset = TextDataset(
        encoded=train_encoded,
        labels=[label_index[row["label"]] for row in train_rows],
    )
    loader = DataLoader(
        train_dataset,
        batch_size=int(cfg["batch_size"]),
        shuffle=True,
        collate_fn=_pad_batch,
        generator=torch.Generator().manual_seed(int(cfg["seed"])),
    )

    model = _build_model(kind, len(vocab), cfg)
    optimizer = torch.optim.Adam(model.parameters(), lr=float(cfg["learning_rate"]))
    loss_fn = nn.CrossEntropyLoss()

    dev_gold = [row["label"] for row in dev_rows]
    history: list[dict[str, Any]] = []
    best_f1 = -math.inf
    best_epoch = 0
    best_state = None
    stale = 0

    for epoch in range(1, int(cfg["max_epochs"]) + 1):
        model.train()
        epoch_loss = 0.0
        seen = 0
        for x, mask, y in loader:
            optimizer.zero_grad()
            logits = model(x, mask)
            loss = loss_fn(logits, y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
            epoch_loss += float(loss.item()) * int(y.size(0))
            seen += int(y.size(0))
        dev_scores = _predict_scores(model, dev_encoded, int(cfg["batch_size"]))
        dev_pred = [LABELS[max(range(4), key=lambda i: row[i])] for row in dev_scores]
        dev_metrics = evaluate(dev_gold, dev_pred)
        record = {
            "epoch": epoch,
            "train_loss": epoch_loss / max(seen, 1),
            "dev_macro_f1": dev_metrics["macro_f1"],
            "dev_accuracy": dev_metrics["accuracy"],
        }
        history.append(record)
        if dev_metrics["macro_f1"] > best_f1 + float(cfg["early_stopping_min_delta"]):
            best_f1 = dev_metrics["macro_f1"]
            best_epoch = epoch
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
            if stale >= int(cfg["early_stopping_patience"]):
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    return TrainingResult(
        method=kind,
        model=model,
        vocab=vocab,
        best_epoch=best_epoch,
        epochs_completed=len(history),
        history=history,
        training_seconds=time.perf_counter() - started,
        config=cfg,
    )


def predict_labels(
    result: TrainingResult, texts: Sequence[str]
) -> tuple[list[str], list[list[float]], float]:
    started = time.perf_counter()
    cfg = result.config
    encoded = encode_texts(texts, result.vocab, int(cfg["max_sequence_length"]))
    scores = _predict_scores(result.model, encoded, int(cfg["batch_size"]))
    labels = [LABELS[max(range(4), key=lambda i: row[i])] for row in scores]
    return labels, scores, time.perf_counter() - started
