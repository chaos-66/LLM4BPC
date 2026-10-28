"""Run the four local arms of the Sun modality five-way supplement.

Arms:
    cfkw   German keyword rules with an explicit priority and fallback
    cfrnn  BiLSTM sentence classifier (corpus-trained embeddings)
    cfcnn  Kim-style CNN sentence classifier (corpus-trained embeddings)
    sun    existing S2.4/S2.6 BERT-TextCNN checkpoint (inference only)

The LLM-SE arm has its own runner (``run_sun_modality_llm_se_v1.py``)
because it performs real API calls.

Nothing here reads test labels before the corresponding predictions are
produced: CFKW priority/fallback and neural hyperparameters are selected on
the dev split only, and the neural models are trained on train only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bpc_hybrid.modality_benchmark import data as data_mod  # noqa: E402
from bpc_hybrid.modality_benchmark.cfkw import (  # noqa: E402
    KeywordClassifier,
    select_on_dev,
)
from bpc_hybrid.modality_benchmark.metrics import evaluate  # noqa: E402
from bpc_hybrid.modality_benchmark import neural  # noqa: E402

DEFAULT_RUN_ID = "s28_sun_modality_five_way_v1"
OUTPUT_ROOT = ROOT / "outputs/development"
S26_CONFIG = ROOT / "configs/models/sun_b0_s26_candidate_B_v1.json"
S24_RUN_MANIFEST = (
    ROOT
    / "outputs/reports"
    / "s24_candidate_B_invsqrt_weighted_seed20260717_v1.adapter_s24_schema.manifest.json"
)
S24_TEST_MACRO_F1 = 0.8772277372431857


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def row_rows(
    examples: Sequence[data_mod.Example], predictions: Sequence[str | None]
) -> list[dict[str, Any]]:
    return [
        {
            "sample_id": example.sample_id,
            "gold": example.label,
            "predicted": prediction,
            "correct": example.label == prediction,
        }
        for example, prediction in zip(examples, predictions)
    ]


def assert_same_population(a: Sequence[data_mod.Example], b: Sequence[data_mod.Example]) -> None:
    if [x.sample_id for x in a] != [x.sample_id for x in b]:
        raise RuntimeError("test population order changed between arms")


def run_cfkw(run_dir: Path) -> dict[str, Any]:
    train = data_mod.load_split("train")
    dev = data_mod.load_split("dev")
    test = data_mod.load_split("test")

    dev_rows = [{"text": row.text, "label": row.label} for row in dev]
    selected, dev_scores = select_on_dev(dev_rows)
    classifier = KeywordClassifier.from_candidate(selected)

    started = time.perf_counter()
    train_pred = classifier.predict([row.text for row in train])
    dev_pred = classifier.predict([row.text for row in dev])
    test_pred = classifier.predict([row.text for row in test])
    elapsed = time.perf_counter() - started

    train_metrics = evaluate([row.label for row in train], train_pred)
    dev_metrics = evaluate([row.label for row in dev], dev_pred)
    test_metrics = evaluate([row.label for row in test], test_pred, runtime_seconds=elapsed)

    decision_rows = [
        {
            "sample_id": row.sample_id,
            "gold": row.label,
            "predicted": pred,
            "tier": classifier.decide(row.text).tier,
            "cue": " ".join(classifier.decide(row.text).cue or ()),
        }
        for row, pred in zip(test, test_pred)
    ]

    write_jsonl(run_dir / "local_only/test_predictions.jsonl", row_rows(test, test_pred))
    write_jsonl(run_dir / "local_only/test_rule_trace.jsonl", decision_rows)
    write_json(
        run_dir / "cfkw.json",
        {
            "method": "cfkw",
            "display_name": "CFKW（德语关键词规则，独立复现）",
            "selected_candidate": selected,
            "dev_candidate_scores": dev_scores,
            "dev_metrics": dev_metrics,
            "train_metrics": train_metrics,
            "test_metrics": test_metrics,
            "selection_split": "dev",
            "test_used_for_selection": False,
            "classifier": classifier.describe(),
        },
    )
    return {"method": "cfkw", "test_metrics": test_metrics, "dev_metrics": dev_metrics,
            "selected_candidate": selected, "runtime_seconds": elapsed}


def _run_neural(
    kind: str, run_dir: Path, overrides: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    train = data_mod.load_split("train")
    dev = data_mod.load_split("dev")
    test = data_mod.load_split("test")
    train_rows = [{"text": row.text, "label": row.label} for row in train]
    dev_rows = [{"text": row.text, "label": row.label} for row in dev]

    started = time.perf_counter()
    result = neural.train(kind, train_rows, dev_rows, overrides)
    dev_pred, _, dev_infer = neural.predict_labels(result, [row.text for row in dev])
    test_pred, test_scores, test_infer = neural.predict_labels(
        result, [row.text for row in test]
    )
    total = time.perf_counter() - started

    test_metrics = evaluate(
        [row.label for row in test], test_pred, runtime_seconds=test_infer
    )
    dev_metrics = evaluate([row.label for row in dev], dev_pred)
    test_metrics["search_time_seconds"] = total - test_infer - dev_infer
    test_metrics["dev_inference_seconds"] = dev_infer

    model_path = run_dir / "local_only" / f"{kind}_model.pt"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    import torch

    torch.save(
        {
            "state_dict": result.model.state_dict(),
            "vocab": result.vocab,
            "config": result.config,
            "best_epoch": result.best_epoch,
        },
        model_path,
    )

    write_jsonl(run_dir / "local_only/test_predictions.jsonl", row_rows(test, test_pred))
    write_json(
        run_dir / f"{kind}.json",
        {
            "method": kind,
            "display_name": (
                "CFRNN（BiLSTM 句子分类器，独立复现）"
                if kind == "cfrnn"
                else "CFCNN（CNN 句子分类器，独立复现）"
            ),
            "config": result.config,
            "vocab_size": len(result.vocab),
            "best_epoch": result.best_epoch,
            "epochs_completed": result.epochs_completed,
            "history": result.history,
            "training_seconds": result.training_seconds,
            "dev_metrics": dev_metrics,
            "test_metrics": test_metrics,
            "model_path_local_only": model_path.relative_to(ROOT).as_posix(),
            "model_sha256": sha256_file(model_path),
            "selection_metric": "dev_macro_f1",
            "test_used_for_selection": False,
            "single_seed": result.config["seed"],
        },
    )
    return {
        "method": kind,
        "test_metrics": test_metrics,
        "dev_metrics": dev_metrics,
        "training_seconds": result.training_seconds,
        "runtime_seconds": total,
        "best_epoch": result.best_epoch,
    }


def run_sun(run_dir: Path) -> dict[str, Any]:
    s26_config = json.loads(S26_CONFIG.read_text(encoding="utf-8"))
    from bpc_hybrid.sun_style.sun_b0 import LockedBertTextCNNInference

    test = data_mod.load_split("test")
    started = time.perf_counter()
    inference = LockedBertTextCNNInference.load(ROOT, s26_config, device="cpu")
    predictions = inference.predict([row.text for row in test])
    elapsed = time.perf_counter() - started
    test_pred = [p.label for p in predictions]
    test_metrics = evaluate(
        [row.label for row in test], test_pred, runtime_seconds=elapsed
    )

    reference = json.loads(S24_RUN_MANIFEST.read_text(encoding="utf-8"))
    reference_metrics = reference["test"]["metrics"]
    reproduced = abs(test_metrics["macro_f1"] - S24_TEST_MACRO_F1) < 1e-9
    if not reproduced:
        raise RuntimeError(
            "Sun checkpoint inference does not reproduce the recorded test "
            f"macro-F1: {test_metrics['macro_f1']} != {S24_TEST_MACRO_F1}"
        )

    write_jsonl(run_dir / "local_only/test_predictions.jsonl", row_rows(test, test_pred))
    write_json(
        run_dir / "sun.json",
        {
            "method": "sun",
            "display_name": "Sun（BERT-TextCNN，本仓已训练权重推理）",
            "checkpoint": s26_config["classifier"]["checkpoint"],
            "classifier_config": s26_config["classifier"]["config"],
            "run_manifest": s26_config["classifier"]["run_manifest"],
            "reused_weights": True,
            "retrained_here": False,
            "recorded_test_metrics": reference_metrics,
            "test_metrics": test_metrics,
            "reproduced_recorded_macro_f1": reproduced,
            "implementation_difference": (
                "candidate B uses inverse-sqrt class-frequency weighted "
                "cross-entropy; the S2.4 base config declares unweighted "
                "cross-entropy. This checkpoint is the one the project binds "
                "for the Sun Part 2 baseline."
            ),
            "training_seed": 20260717,
            "trained_on_split": "train (1985 rows), dev-selected best epoch",
        },
    )
    return {
        "method": "sun",
        "test_metrics": test_metrics,
        "runtime_seconds": elapsed,
        "reproduced_recorded_macro_f1": reproduced,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--methods",
        default="cfkw,cfrnn,cfcnn,sun",
        help="comma separated subset of cfkw,cfrnn,cfcnn,sun",
    )
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--force", action="store_true", help="overwrite method json only")
    parser.add_argument("--max-epochs", type=int, default=None)
    args = parser.parse_args(argv)

    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    unknown = [m for m in methods if m not in {"cfkw", "cfrnn", "cfcnn", "sun"}]
    if unknown:
        raise SystemExit(f"unknown methods: {unknown}")

    inventory = data_mod.verify_splits()
    run_dir = OUTPUT_ROOT / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "local_only").mkdir(exist_ok=True)

    summary_path = run_dir / "run_manifest.json"
    summary: dict[str, Any] = {
        "schema_version": "sun_modality_local_arms@1.0.0",
        "run_id": args.run_id,
        "created_at": now(),
        "dataset": data_mod.dataset_binding(),
        "verified_splits": inventory,
        "test_population_rows": inventory["test"]["rows"],
        "methods": {},
        "environment": {
            "python": sys.version.split()[0],
        },
        "safety": {
            "gold_modified": False,
            "estg150_results_modified": False,
            "llm_api_called": False,
            "network_called": False,
            "third_party_data_committed": False,
        },
    }

    overrides = {}
    if args.max_epochs is not None:
        overrides["max_epochs"] = args.max_epochs

    for method in methods:
        print(f"[{method}] starting", flush=True)
        method_dir = run_dir / method
        method_dir.mkdir(parents=True, exist_ok=True)
        (method_dir / "local_only").mkdir(exist_ok=True)
        if method == "cfkw":
            outcome = run_cfkw(method_dir)
        elif method in {"cfrnn", "cfcnn"}:
            outcome = _run_neural(method, method_dir, overrides or None)
        else:
            outcome = run_sun(method_dir)
        summary["methods"][method] = outcome
        metrics = outcome["test_metrics"]
        print(
            f"[{method}] test macro-F1={metrics['macro_f1']:.6f} "
            f"acc={metrics['accuracy']:.6f} n={metrics['n']}",
            flush=True,
        )

    summary["finished_at"] = now()
    if summary_path.exists():
        if not args.force:
            raise SystemExit(f"refusing to overwrite {summary_path}")
        summary_path.unlink()
    write_json(summary_path, summary)
    print(f"wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
