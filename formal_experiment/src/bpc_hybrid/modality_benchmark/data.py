"""Dataset access for the Sun modality supplement (read-only, hash-bound).

The three split files are project-reconstructed deterministic
group-aware splits (seed 20260715) of the official Sun/Michel EStG
modality data (2,833 raw sentences -> 2,831 after the pre-registered
conflicting-label quarantine).  They are *not* Sun's original split and
must never be re-randomised here.

The split files stay Git-ignored (original German sentences are not
redistributable); this module only reads them locally.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .metrics import LABELS

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATASET_DIR = PROJECT_ROOT / "data/development/modality/sun_estg_modality_v1"
SPLIT_DIR = DATASET_DIR / "splits"

EXPECTED: dict[str, dict[str, Any]] = {
    "train": {
        "path": SPLIT_DIR / "train.jsonl",
        "rows": 1985,
        "sha256": "a7367cd35e3a5ce7263ad5b0fae4881a989761d4fba21b75bdc75b6e2b83c142",
    },
    "dev": {
        "path": SPLIT_DIR / "dev.jsonl",
        "rows": 420,
        "sha256": "ad541915d16aaef6119cb3769e6da0b89e8e8af5ec9069ac3a25680040e5a8d6",
    },
    "test": {
        "path": SPLIT_DIR / "test.jsonl",
        "rows": 426,
        "sha256": "2f67edad05e3a4d315d9ac65fc0ffd1d83dbaffd2d77a55916d6aa9a6919e871",
    },
}


class DatasetError(ValueError):
    """Fail-closed dataset contract violation."""


@dataclass(frozen=True)
class Example:
    sample_id: str
    text: str
    label: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_splits() -> dict[str, dict[str, Any]]:
    """Return the verified split inventory or raise."""
    inventory: dict[str, dict[str, Any]] = {}
    for name, spec in EXPECTED.items():
        path: Path = spec["path"]
        if not path.exists():
            raise DatasetError(f"missing split file: {path}")
        digest = sha256_file(path)
        if digest != spec["sha256"]:
            raise DatasetError(
                f"{name} split hash mismatch: {digest} != {spec['sha256']}"
            )
        rows = load_split(name)
        if len(rows) != spec["rows"]:
            raise DatasetError(
                f"{name} row count {len(rows)} != {spec['rows']}"
            )
        ids = {row.sample_id for row in rows}
        if len(ids) != len(rows):
            raise DatasetError(f"{name} duplicate sample_id")
        labels = {row.label for row in rows}
        if not labels <= set(LABELS):
            raise DatasetError(f"{name} unknown labels: {sorted(labels - set(LABELS))}")
        inventory[name] = {
            "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "rows": len(rows),
            "sha256": digest,
        }

    id_sets = {name: {row.sample_id for row in load_split(name)} for name in EXPECTED}
    for a in ("train", "dev"):
        overlap = id_sets[a] & id_sets["test"]
        if overlap:
            raise DatasetError(f"{a}/test sample_id overlap: {len(overlap)}")
    if id_sets["train"] & id_sets["dev"]:
        raise DatasetError("train/dev sample_id overlap")
    if len(id_sets["train"] | id_sets["dev"] | id_sets["test"]) != 2831:
        raise DatasetError("union of splits is not the 2,831-row main population")
    return inventory


def load_split(name: str) -> list[Example]:
    if name not in EXPECTED:
        raise DatasetError(f"unknown split: {name}")
    path: Path = EXPECTED[name]["path"]
    rows: list[Example] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise DatasetError(f"{name} line {line_number}: {exc}") from exc
            text = obj.get("text")
            label = obj.get("label")
            sample_id = obj.get("sample_id")
            if not isinstance(text, str) or not text.strip():
                raise DatasetError(f"{name} line {line_number}: empty text")
            if label not in LABELS:
                raise DatasetError(f"{name} line {line_number}: bad label {label!r}")
            if not isinstance(sample_id, str) or not sample_id:
                raise DatasetError(f"{name} line {line_number}: bad sample_id")
            rows.append(Example(sample_id=sample_id, text=text, label=label))
    return rows


def load_split_text_only(name: str) -> list[tuple[str, str]]:
    """Return ``(sample_id, text)`` pairs without reading the Gold label.

    The LLM arm must produce predictions before any label is looked at, so
    this loader deliberately ignores the ``label`` field.
    """
    if name not in EXPECTED:
        raise DatasetError(f"unknown split: {name}")
    path: Path = EXPECTED[name]["path"]
    if not path.exists():
        raise DatasetError(f"missing split file: {path}")
    if sha256_file(path) != EXPECTED[name]["sha256"]:
        raise DatasetError(f"{name} split hash mismatch")
    pairs: list[tuple[str, str]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            obj = json.loads(raw)
            sample_id, text = obj.get("sample_id"), obj.get("text")
            if not isinstance(sample_id, str) or not sample_id:
                raise DatasetError(f"{name} line {line_number}: bad sample_id")
            if not isinstance(text, str) or not text.strip():
                raise DatasetError(f"{name} line {line_number}: empty text")
            pairs.append((sample_id, text))
    if len(pairs) != EXPECTED[name]["rows"]:
        raise DatasetError(f"{name} row count {len(pairs)} != {EXPECTED[name]['rows']}")
    return pairs
def labels(rows: Sequence[Example]) -> list[str]:
    return [row.label for row in rows]


def split_summary(rows: Sequence[Example]) -> dict[str, int]:
    summary = {label: 0 for label in LABELS}
    for row in rows:
        summary[row.label] += 1
    return summary


def dataset_binding() -> Mapping[str, Any]:
    return {
        "dataset_dir": str(DATASET_DIR.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "split_origin": (
            "project_reconstructed_deterministic_group_aware_split_seed_20260715"
            "_not_sun_original_split"
        ),
        "main_analysis_population": 2831,
        "splits": {
            name: {
                "path": spec["path"].relative_to(PROJECT_ROOT).as_posix(),
                "rows": spec["rows"],
                "sha256": spec["sha256"],
            }
            for name, spec in EXPECTED.items()
        },
    }
