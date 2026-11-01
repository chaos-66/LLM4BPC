"""Train-only corpus demonstrations appended to the frozen boundary prompt.

German sentences are loaded locally, never embedded in versioned source files.
Held-out text is used only for overlap checks; held-out labels are not accessed.
"""
from __future__ import annotations

import json
from collections import Counter
from typing import Any

from bpc_hybrid.datasets.sun_modality_importer import normalize_for_dedup

from . import boundary, data

ROOT = boundary.ROOT
CONTRACT = ROOT / "configs/supplement/sun_modality_fewshot_v1.json"


def read_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    parent = boundary.read_contract()
    for key in ("parent_prompt_sha256", "guidance_sha256"):
        if contract[key] != parent[key]:
            raise ValueError("few-shot parent binding changed: " + key)
    for key in ("header", "selection_manifest"):
        spec = contract[key]
        if boundary.digest((ROOT / spec["path"]).read_bytes()) != spec["sha256"]:
            raise ValueError("few-shot artifact hash mismatch: " + key)
    if contract["splits"] != {
        name: {"rows": spec["rows"], "sha256": spec["sha256"]}
        for name, spec in data.EXPECTED.items()
    }:
        raise ValueError("few-shot split binding changed")
    return contract


def stratum(row: data.Example, markers: dict[str, list[str]]) -> str | None:
    has = lambda family: any(marker in row.text for marker in markers[family])
    if row.label == "definition":
        for family, group in (("classic", "D-classic"), ("applicability", "D-applic"),
                              ("conditional", "D-exemptcond"), ("arithmetic", "D-arith"),
                              ("negation", "D-neg")):
            if has(family):
                return group
    elif row.label == "obligation":
        return "O-applic" if has("applicability") else "O-other"
    elif row.label == "prohibition":
        return "P"
    elif row.label == "permission":
        return "M"
    return None


def select_examples(train: list[data.Example], held_out: list[tuple[str, str]],
                    manifest: dict[str, Any]) -> list[data.Example]:
    """Replay the fixed draft rule; refuse overlap, shortage, or changed picks."""
    ids = [r.sample_id for r in train]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate train sample_id")
    held_ids = {sid for sid, _ in held_out}
    held_texts = {normalize_for_dedup(text) for _, text in held_out}
    if any(r.sample_id in held_ids or normalize_for_dedup(r.text) in held_texts for r in train):
        raise ValueError("train/held-out overlap")
    rule = manifest["selection_rule"]
    groups = {key: [] for key in rule["quota"]}
    for row in train:
        group = stratum(row, rule["strata_markers"])
        if group in groups and len(row.text.split()) >= 6:
            groups[group].append(row)
    picks = {}
    for group, quota in rule["quota"].items():
        candidates = sorted(groups[group], key=lambda r: (len(r.text.split()), r.sample_id))
        if len(candidates) < quota:
            raise ValueError("insufficient train examples: " + group)
        picks[group] = candidates[:quota]
    selected = [picks[group][index] for group, index in manifest["presentation_order"]]
    actual = [{"position": i, "stratum": stratum(row, rule["strata_markers"]),
               "sample_id": row.sample_id, "label": row.label,
               "word_count": len(row.text.split()),
               "text_sha256_utf8_lf": boundary.digest((row.text + "\n").encode("utf-8"))}
              for i, row in enumerate(selected, 1)]
    if actual != manifest["selections"]:
        raise ValueError("selected examples differ from frozen manifest")
    if len({r.sample_id for r in selected}) != len(selected):
        raise ValueError("duplicate demonstration")
    if dict(Counter(r.label for r in selected)) != manifest["class_totals"]:
        raise ValueError("demonstration class quota mismatch")
    return selected


def load_demonstrations() -> tuple[str, dict[str, Any]]:
    contract = read_contract()
    manifest = json.loads((ROOT / contract["selection_manifest"]["path"]).read_text(encoding="utf-8"))
    # Verify the train bytes before reading its labels. Dev/test loader discards labels.
    train_spec = data.EXPECTED["train"]
    if data.sha256_file(train_spec["path"]) != train_spec["sha256"]:
        raise ValueError("train split hash mismatch")
    train = data.load_split("train")
    if len(train) != train_spec["rows"]:
        raise ValueError("train row count mismatch")
    held_out = data.load_split_text_only("dev") + data.load_split_text_only("test")
    selected = select_examples(train, held_out, manifest)
    header = (ROOT / contract["header"]["path"]).read_text(encoding="utf-8").strip()
    lines = [header, ""] + [f'{i}. "{row.text}" -> {row.label}'
                            for i, row in enumerate(selected, 1)]
    block = "\n".join(lines) + "\n"
    if boundary.digest(block.encode("utf-8")) != contract["demonstration_block_sha256"]:
        raise ValueError("rendered demonstration block hash mismatch")
    return block, manifest


def request_body(sample_id: str, text: str, *, block: str | None = None) -> dict[str, Any]:
    contract = read_contract()
    if block is None:
        block, _ = load_demonstrations()
    if boundary.digest(block.encode("utf-8")) != contract["demonstration_block_sha256"]:
        raise ValueError("request demonstration block hash mismatch")
    body = boundary.request_body(sample_id, text)
    body["messages"][0]["content"] += "\n\n" + block.strip()
    return body
