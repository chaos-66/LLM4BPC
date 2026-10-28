"""Shared evaluation for the Sun modality five-way supplement.

One evaluator for all five arms (CFKW / CFRNN / CFCNN / Sun / LLM-SE) so
that accuracy, macro P/R/F1, per-class P/R/F1+support, confusion matrix,
failure rate and runtime are computed by exactly the same code.

Failure semantics (fixed before any test label is read):

* ``prediction is None`` means "the method produced no usable label"
  (parser failure, API failure, empty clause list).  The sample stays in
  the denominator: it lowers accuracy and lowers the gold-class recall.
  It never contributes a false positive to any class and it is never
  replaced by a guessed or majority label.
* ``failure_rate = (#None) / n``.
* Coverage-restricted metrics are reported separately and are never
  presented as the headline number.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

LABELS: tuple[str, ...] = (
    "definition",
    "obligation",
    "permission",
    "prohibition",
)

NO_PREDICTION = "<no_prediction>"


def _per_class_counts(
    gold: Sequence[str], pred: Sequence[str | None], label: str
) -> tuple[int, int, int, int]:
    tp = fp = fn = tn = 0
    for g, p in zip(gold, pred):
        if g == label and p == label:
            tp += 1
        elif g != label and p == label:
            fp += 1
        elif g == label and p != label:
            fn += 1
        else:
            tn += 1
    return tp, fp, fn, tn


def _prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return precision, recall, f1


def confusion_matrix(
    gold: Sequence[str], pred: Sequence[str | None]
) -> dict[str, Any]:
    has_none = any(p is None for p in pred)
    columns = list(LABELS) + ([NO_PREDICTION] if has_none else [])
    rows = {label: {col: 0 for col in columns} for label in LABELS}
    for g, p in zip(gold, pred):
        rows[g][NO_PREDICTION if p is None else p] += 1
    return {
        "label_order": list(LABELS),
        "column_order": columns,
        "rows_gold_columns_predicted": [[rows[g][c] for c in columns] for g in LABELS],
        "as_dict": rows,
    }


def evaluate(
    gold: Sequence[str],
    pred: Sequence[str | None],
    *,
    runtime_seconds: float | None = None,
) -> dict[str, Any]:
    if len(gold) != len(pred):
        raise ValueError("gold and prediction lengths differ")
    if not gold:
        raise ValueError("empty evaluation population")
    unknown_gold = sorted({g for g in gold if g not in LABELS})
    if unknown_gold:
        raise ValueError(f"unknown gold labels: {unknown_gold}")
    unknown_pred = sorted(
        {p for p in pred if p is not None and p not in LABELS}
    )
    if unknown_pred:
        raise ValueError(f"unknown predicted labels: {unknown_pred}")

    n = len(gold)
    failures = sum(1 for p in pred if p is None)
    correct = sum(1 for g, p in zip(gold, pred) if g == p)
    accuracy = correct / n

    per_class: dict[str, dict[str, Any]] = {}
    for label in LABELS:
        tp, fp, fn, tn = _per_class_counts(gold, pred, label)
        precision, recall, f1 = _prf(tp, fp, fn)
        per_class[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": sum(1 for g in gold if g == label),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
        }

    macro_precision = sum(v["precision"] for v in per_class.values()) / len(LABELS)
    macro_recall = sum(v["recall"] for v in per_class.values()) / len(LABELS)
    macro_f1 = sum(v["f1"] for v in per_class.values()) / len(LABELS)

    covered = [(g, p) for g, p in zip(gold, pred) if p is not None]
    coverage_restricted: dict[str, Any] | None = None
    if covered and failures:
        cov_gold = [g for g, _ in covered]
        cov_pred = [p for _, p in covered]  # type: ignore[list-item]
        cov_eval = evaluate(cov_gold, cov_pred)  # type: ignore[arg-type]
        coverage_restricted = {
            "n": cov_eval["n"],
            "accuracy": cov_eval["accuracy"],
            "macro_precision": cov_eval["macro_precision"],
            "macro_recall": cov_eval["macro_recall"],
            "macro_f1": cov_eval["macro_f1"],
            "note": (
                "secondary diagnostic only: excludes samples with no usable "
                "prediction; never the headline number"
            ),
        }

    result: dict[str, Any] = {
        "n": n,
        "evaluated_population": "all_test_samples",
        "accuracy": accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "per_class": per_class,
        "confusion_matrix": confusion_matrix(gold, pred),
        "failures": failures,
        "failure_rate": failures / n,
        "coverage": (n - failures) / n,
    }
    if coverage_restricted is not None:
        result["coverage_restricted_secondary"] = coverage_restricted
    if runtime_seconds is not None:
        result["runtime_seconds"] = runtime_seconds
    return result


def aggregate_costs(costs: Iterable[float]) -> float:
    return float(sum(costs))


def label_distribution(labels: Iterable[str]) -> dict[str, int]:
    counts = {label: 0 for label in LABELS}
    for label in labels:
        counts[label] += 1
    return counts


def compare_to_baseline(
    results: Mapping[str, Mapping[str, Any]], baseline: str
) -> dict[str, dict[str, float]]:
    """Paired macro-F1 delta in percentage points against *baseline*."""
    base = results[baseline]["macro_f1"]
    out: dict[str, dict[str, float]] = {}
    for name, metrics in results.items():
        if name == baseline:
            continue
        out[name] = {
            "delta_macro_f1_pp": round((metrics["macro_f1"] - base) * 100, 4),
            "delta_accuracy_pp": round((metrics["accuracy"] - results[baseline]["accuracy"]) * 100, 4),
        }
    return out
