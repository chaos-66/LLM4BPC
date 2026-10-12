"""Local MPNet using the cached model's declared pooling and normalization.

Equivalent inference through Transformers, without optional sklearn imports.
No package installation, security-policy change, or model download.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


class LocalMPNetBackend:
    def __init__(self, path):
        import torch
        from transformers import AutoTokenizer
        from transformers.models.mpnet.modeling_mpnet import MPNetModel
        self.path = Path(path)
        read = lambda name: json.loads((self.path / name).read_text(encoding="utf-8"))
        modules = read("modules.json")
        if [m["type"].split(".")[-1] for m in modules] != ["Transformer", "Pooling", "Normalize"]:
            raise ValueError("unsupported model modules")
        pooling = read("1_Pooling/config.json")
        if not pooling["pooling_mode_mean_tokens"] or any(pooling.get(k, False) for k in
                ("pooling_mode_cls_token", "pooling_mode_max_tokens", "pooling_mode_mean_sqrt_len_tokens")):
            raise ValueError("unsupported model pooling")
        config = read("sentence_bert_config.json")
        self.max_length = config["max_seq_length"]
        if config.get("do_lower_case", False):
            raise ValueError("unsupported tokenization preprocessing")
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.path), local_files_only=True)
        self.model = MPNetModel.from_pretrained(str(self.path), local_files_only=True,
                                              use_safetensors=True).eval()
        self.cache = {}
        names = ["config.json", "modules.json", "1_Pooling/config.json", "sentence_bert_config.json",
                 "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "vocab.txt",
                 "model.safetensors"]
        self.hashes = {n: hashlib.sha256((self.path/n).read_bytes()).hexdigest() for n in names}
        self.torch_version = torch.__version__

    def identity(self):
        values = {"short_name": "st_mpnet", "kind": "transformers_local",
                  "mode": "attention_mask_mean_pooling_l2_cosine", "vector_dim": 768,
                  "max_seq_length": self.max_length, "model_path": str(self.path.resolve()),
                  "artifact_sha256": self.hashes, "torch_version": self.torch_version}
        values["backend_identity_sha256"] = hashlib.sha256(
            json.dumps(values, sort_keys=True).encode()).hexdigest()
        return values

    def embed(self, texts):
        import numpy as np
        import torch
        missing = list(dict.fromkeys(t for t in texts if t not in self.cache))
        for start in range(0, len(missing), 16):
            batch = missing[start:start+16]
            encoded = self.tokenizer(batch, padding=True, truncation=True,
                                     max_length=self.max_length, return_tensors="pt")
            with torch.inference_mode():
                hidden = self.model(**encoded).last_hidden_state
                mask = encoded["attention_mask"].unsqueeze(-1).to(hidden.dtype)
                pooled = (hidden*mask).sum(1) / mask.sum(1).clamp(min=1e-9)
                vectors = torch.nn.functional.normalize(pooled, p=2, dim=1).cpu().numpy()
            self.cache.update({t: np.asarray(v, dtype="float32") for t, v in zip(batch, vectors)})
        return [self.cache[t] for t in texts]

    def similarity(self, left, right):
        import numpy as np
        if left == right:
            return 1.0
        a, b = self.embed([left, right])
        return max(0.0, min(1.0, float(np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b)))))
