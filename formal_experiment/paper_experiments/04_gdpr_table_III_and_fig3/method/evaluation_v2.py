# -*- coding: utf-8 -*-
"""Development-only metrics for Stage 3-v2 calibration.

This evaluator is intentionally narrow: it scores only the target-bound
development cases used by the pre-registered calibration protocol.  It never
loads or returns test metrics.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

TYPES = ("missing_action", "incorrect_actor", "out_of_order")
MAIN_ORDER_TYPE = "TYPE_A_explicit_action_precedence"


class DevelopmentEvaluationError(RuntimeError):
    pass


def empty_counts() -> dict[str, int]:
    return {
        "TP": 0,
        "FP": 0,
        "FN": 0,
        "TN": 0,
        "unknown_positive": 0,
        "unknown_negative": 0,
        "scored_cells": 0,
        "positive_support": 0,
        "negative_support": 0,
        "not_applicable": 0,
        "not_scored": 0,
    }


def prf(counts: Mapping[str, int]) -> dict[str, Any]:
    tp = int(counts.get("TP", 0))
    fp = int(counts.get("FP", 0))
    fn = int(counts.get("FN", 0))
    tn = int(counts.get("TN", 0))
    # Standard zero_division=0 convention: an undefined precision/recall is
    # reported as 0.0, not as null.  This keeps a class with positive support
    # from disappearing from macro-F1 merely because no positive was predicted.
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) > 0 else 0.0)
    return {
        "TP": tp, "FP": fp, "FN": fn, "TN": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def metric_block(counts: Mapping[str, int]) -> dict[str, Any]:
    out = {key: int(value) for key, value in counts.items()}
    out.update(prf(counts))
    scored = out.get("scored_cells", 0)
    unknown = out.get("unknown_positive", 0) + out.get("unknown_negative", 0)
    out["coverage"] = ((scored - unknown) / scored) if scored else None
    out["unknown_rate"] = (unknown / scored) if scored else None
    return out


def _expected_state(case: Mapping[str, Any], check_type: str) -> str:
    reference_states = case.get("reference_states") or case.get("expected_reference_state") or {}
    if not isinstance(reference_states, Mapping):
        raise DevelopmentEvaluationError(f"missing reference states for {case.get('case_id')}")
    return str(reference_states.get(check_type) or "not_scored")


def evaluate_dev_method(method: str,
                        cases: Sequence[Mapping[str, Any]],
                        signals: Mapping[tuple[str, str, str], Mapping[str, Any]],
                        order_scope: Mapping[str, str],
                        *,
                        fail_on_test: bool = True
                        ) -> dict[str, Any]:
    """Evaluate one method on development cases.

    ``signals`` is keyed by ``(method, case_id, check_type)`` because each
    reference case is target-bound to one requirement.  If ``fail_on_test`` is
    true, any case with split != development raises before metric computation.
    """
    if fail_on_test:
        bad = sorted(str(case.get("case_id")) for case in cases if str(case.get("split")) != "development")
        if bad:
            raise DevelopmentEvaluationError(f"test/non-development cases in calibration: {bad}")
    overall = empty_counts()
    per_type = {check_type: empty_counts() for check_type in TYPES}
    unknown_reasons: Counter = Counter()
    false_positives: list[dict[str, Any]] = []
    false_negatives: list[dict[str, Any]] = []
    for case in sorted(cases, key=lambda item: str(item.get("case_id"))):
        case_id = str(case.get("case_id"))
        requirement_id = str(case.get("requirement_id"))
        for check_type in TYPES:
            if check_type == "out_of_order":
                order_type = str(order_scope.get(requirement_id) or "")
                if order_type != MAIN_ORDER_TYPE:
                    per_type[check_type]["not_scored"] += 1
                    overall["not_scored"] += 1
                    continue
            expected = _expected_state(case, check_type)
            if expected == "not_applicable":
                per_type[check_type]["not_applicable"] += 1
                overall["not_applicable"] += 1
                continue
            if expected == "not_scored":
                per_type[check_type]["not_scored"] += 1
                overall["not_scored"] += 1
                continue
            if expected not in ("violated", "satisfied"):
                raise DevelopmentEvaluationError(
                    f"unexpected reference state {expected!r} for {case_id}/{check_type}"
                )
            signal = signals.get((method, case_id, check_type)) or {}
            status = str(signal.get("status") or "unknown")
            if status not in ("violated", "satisfied", "unknown"):
                status = "unknown"
            reason = signal.get("reason")
            for target in (per_type[check_type], overall):
                target["scored_cells"] += 1
                if expected == "violated":
                    target["positive_support"] += 1
                    if status == "violated":
                        target["TP"] += 1
                    elif status == "unknown":
                        target["FN"] += 1
                        target["unknown_positive"] += 1
                    else:
                        target["FN"] += 1
                else:
                    target["negative_support"] += 1
                    if status == "violated":
                        target["FP"] += 1
                    elif status == "satisfied":
                        target["TN"] += 1
                    else:
                        target["unknown_negative"] += 1
            if status == "unknown":
                unknown_reasons[f"{check_type}:{reason or 'unknown'}"] += 1
            if expected == "satisfied" and status == "violated" and len(false_positives) < 50:
                false_positives.append({
                    "case_id": case_id,
                    "requirement_id": requirement_id,
                    "check_type": check_type,
                    "reason": reason,
                    "raw_score": signal.get("raw_score"),
                    "denominator": signal.get("denominator"),
                })
            if expected == "violated" and status != "violated" and len(false_negatives) < 50:
                false_negatives.append({
                    "case_id": case_id,
                    "requirement_id": requirement_id,
                    "check_type": check_type,
                    "status": status,
                    "reason": reason,
                    "raw_score": signal.get("raw_score"),
                    "denominator": signal.get("denominator"),
                })
    per_type_metrics = {check_type: metric_block(per_type[check_type]) for check_type in TYPES}
    return {
        "method": method,
        "overall": metric_block(overall),
        "per_type": per_type_metrics,
        "unknown_reason_counts": dict(sorted(unknown_reasons.items())),
        "false_positive_examples": false_positives,
        "false_negative_examples": false_negatives,
        "macro_f1": _macro_f1(per_type_metrics, overall),
        "micro_f1": prf(overall).get("f1"),
    }


def _macro_f1(per_type: Mapping[str, Mapping[str, Any]], overall: Mapping[str, Any]) -> float:
    values = [float(per_type[check_type]["f1"]) for check_type in TYPES]
    return sum(values) / len(values)


def combined_objective(results: Mapping[str, Mapping[str, Any]]) -> float:
    """Pre-registered method-neutral objective: mean of method Macro-F1."""
    values = [results[method]["macro_f1"] for method in ("sun", "ours")
              if results.get(method, {}).get("macro_f1") is not None]
    if not values:
        return float("-inf")
    return sum(float(value) for value in values) / len(values)


def calibration_tie_break_key(method_name: str,
                              results: Mapping[str, Mapping[str, Any]],
                              *,
                              gamma: float,
                              theta: float) -> tuple[Any, ...]:
    """Higher tuple is better, matching the pre-registered tie-break order."""
    combined = combined_objective(results)
    min_macro = min(
        (float(results[m]["macro_f1"]) for m in ("sun", "ours")
         if results.get(m, {}).get("macro_f1") is not None),
        default=float("-inf"),
    )
    unknown_rates = [
        float(results[m]["overall"].get("unknown_rate") or 0.0)
        for m in ("sun", "ours") if results.get(m)
    ]
    mean_unknown = sum(unknown_rates) / len(unknown_rates) if unknown_rates else float("inf")
    precisions = [
        float(results[m]["overall"].get("precision") or 0.0)
        for m in ("sun", "ours") if results.get(m)
    ]
    mean_precision = sum(precisions) / len(precisions) if precisions else 0.0
    return (combined, min_macro, -mean_unknown, mean_precision, gamma + theta)


__all__ = [
    "TYPES",
    "MAIN_ORDER_TYPE",
    "DevelopmentEvaluationError",
    "empty_counts",
    "prf",
    "metric_block",
    "evaluate_dev_method",
    "combined_objective",
    "calibration_tie_break_key",
]
