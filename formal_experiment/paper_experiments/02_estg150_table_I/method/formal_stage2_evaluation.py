# -*- coding: utf-8 -*-
"""Shared formal Stage 2 evaluation over the PUBLISHED formal Gold
(zero-API, G0.4 evaluation-views contract).

The published Stage 2 Gold (data/gold/stage2/estg150_formal_gold_v1.json)
stores modality as a plain string: local modality evidence spans are NOT
carried by the decision-only Gold. Consequences (explicit, never silent):

- six-field span metrics: computed with the fixed Sun literal-overlap
  contract for the five span-bearing fields (actor/action/condition/
  constraint/exception); the modality field's span metrics are reported as
  unavailable with the reason
- modality-label metrics: four-class (obligation/permission/prohibition/
  definition) accuracy and macro-F1, reported separately
- fine (clause-level) and coarse (sentence-level) views share the same
  evaluator, schema and normalization; cross-view mixing is forbidden

The evaluation input for the evaluator is derived deterministically from
the published Gold records (modality string -> {"label": ..., "evidence": []}).
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from bpc_hybrid.stage2_sun_literal_overlap import (
    evaluate_sun_literal_overlap,
)

MODALITY_CLASSES = ("obligation", "permission", "prohibition", "definition")
SPAN_FIELDS = ("actor", "action", "condition", "constraint", "exception")
#: Name of the contract-aligned pooled metric.  The G0.4 contract authorizes a
#: main report of "the sentence-level coarse five span-bearing fields plus the
#: separate four-class modality-label metrics", and states that modality
#: evidence-span metrics are "explicitly unavailable (never zeroed, never
#: aggregated)".  Therefore the pooled/overall score MUST aggregate exactly
#: these five fields.  ``SPAN_FIELDS`` is that set by construction.
POOLED_METRIC_ID = "pooled_five_span_fields"
#: Legacy six-field aggregate (the five span fields PLUS the modality span).
#: Kept as an explicitly non-canonical development-provenance field so that
#: historical capsules remain readable; it must never be reported as the
#: paper's overall score.
LEGACY_SIX_FIELD_METRIC_ID = "overall_six_field_incl_modality_span_NON_CANONICAL"


def _pool_counts(per_field: Mapping[str, Any],
                 fields: Sequence[str]) -> dict[str, int]:
    """Sum the raw match counters of ``fields`` for a pooled (micro) metric.

    Pooling uses the evaluator's own per-field counters
    (``ground_truth``/``extracted``/``matched_predictions``/
    ``matched_ground_truth``), so the pooled value is exactly the micro
    aggregate over the selected fields and is reproducible from the frozen
    evaluator output without re-running span matching.
    """
    keys = ("ground_truth", "extracted", "matched_predictions",
            "matched_ground_truth")
    totals = {k: 0 for k in keys}
    for field in fields:
        values = per_field.get(field) or {}
        for key in keys:
            value = values.get(key)
            totals[key] += value if isinstance(value, int) else 0
    return totals


def _prf_from_counts(totals: Mapping[str, int]) -> dict[str, Any]:
    extracted = totals["extracted"]
    ground_truth = totals["ground_truth"]
    precision = totals["matched_predictions"] / extracted if extracted else 0.0
    recall = totals["matched_ground_truth"] / ground_truth if ground_truth else 0.0
    f1 = (2.0 * precision * recall / (precision + recall)
          if (precision + recall) else 0.0)
    return {
        "ground_truth": ground_truth,
        "extracted": extracted,
        "matched_predictions": totals["matched_predictions"],
        "matched_ground_truth": totals["matched_ground_truth"],
        "misclassified": extracted - totals["matched_predictions"],
        "missed": ground_truth - totals["matched_ground_truth"],
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def published_gold_to_evaluator(gold_doc: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert published Gold records to evaluator-compatible records.

    modality string -> {"label": str, "evidence": []} (evidence unavailable
    in the published decision-only Gold). All other clause fields pass
    through unchanged.
    """
    out = []
    for rec in sorted(gold_doc["records"], key=lambda r: r["sample_id"]):
        clauses = []
        for clause in rec.get("clauses") or []:
            c = dict(clause)
            modality = c.get("modality")
            c["modality"] = {
                "label": modality if isinstance(modality, str) else None,
                "evidence": [],
            }
            clauses.append(c)
        out.append({"sample_id": rec["sample_id"], "clauses": clauses})
    return out


def predictions_to_evaluator(attempts: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """B0/D1/H1 attempts envelopes -> evaluator attempts (envelope shape kept:
    {sample_id, request_status, record, error_category, runtime})."""
    return list(attempts)


def evaluate_span_metrics(gold_eval_records: Sequence[Mapping[str, Any]],
                          attempts: Sequence[Mapping[str, Any]], *,
                          dataset_id: str, method_id: str,
                          view: str) -> dict[str, Any]:
    """Six-field Sun literal-overlap evaluation with explicit modality handling.

    Returns per-field metrics for the five span-bearing fields plus an
    explicit 'modality_span' availability declaration.

    Two aggregate fields are emitted:

    - ``pooled_five_span_fields`` -- THE contract-aligned aggregate
      (micro/pooled P/R/F1 over actor/action/condition/constraint/exception).
      This is the only aggregate the paper may report as its overall score.
    - ``overall_six_field_incl_modality_span_NON_CANONICAL`` -- the legacy
      six-field aggregate retained for provenance only.  It folds in the
      modality *span* counters, which the G0.4 contract declares unavailable
      and forbids aggregating, and which the coarse transform fills with a
      synthetic clause-span fallback.  Never report this value as a result.
    """
    report = evaluate_sun_literal_overlap(
        gold_eval_records, list(attempts), dataset_id=dataset_id,
        method_id=method_id)
    per_field = report.get("per_field", {})
    span_fields = {}
    for field in SPAN_FIELDS:
        v = per_field.get(field, {})
        span_fields[field] = {
            "ground_truth": v.get("ground_truth"),
            "extracted": v.get("extracted"),
            "precision": v.get("precision"),
            "recall": v.get("recall"),
            "f1": v.get("f1"),
        }
    modality_field = per_field.get("modality", {})
    pooled = _prf_from_counts(_pool_counts(per_field, SPAN_FIELDS))
    legacy = report.get("overall", {})
    return {
        "schema_version": "formal_stage2_span_metrics@1.1.0",
        "view": view,
        "dataset_id": dataset_id,
        "method_id": method_id,
        "match_rule": "independent_same_field_any_nonempty_character_span_intersection",
        "pooled_metric_id": POOLED_METRIC_ID,
        "pooled_aggregation": "micro_pooled_over_five_span_bearing_fields",
        "pooled_five_span_fields": pooled,
        "span_fields": span_fields,
        "modality_span": {
            "available": False,
            "reason": ("published formal Gold stores modality as a plain "
                       "string; local modality evidence spans are not "
                       "carried by the decision-only Gold"),
            "aggregated_into_any_main_metric": False,
            "ground_truth": modality_field.get("ground_truth", 0),
            "extracted": modality_field.get("extracted", 0),
        },
        LEGACY_SIX_FIELD_METRIC_ID: {
            "precision": legacy.get("precision"),
            "recall": legacy.get("recall"),
            "f1": legacy.get("f1"),
            "ground_truth": legacy.get("ground_truth"),
            "extracted": legacy.get("extracted"),
            "canonical": False,
            "reason": ("legacy six-field aggregate including the unavailable "
                       "modality span; provenance only, never a reported "
                       "result"),
        },
        "no_cross_view_mixing": True,
    }


def _gold_modality_label(gold_eval_records: Mapping[str, Mapping[str, Any]],
                         sample_id: str) -> str | None:
    rec = gold_eval_records.get(sample_id)
    for clause in (rec or {}).get("clauses") or []:
        label = (clause.get("modality") or {}).get("label")
        if isinstance(label, str) and label:
            return label
    return None


def _pred_modality_label(attempt: Mapping[str, Any]) -> str | None:
    record = attempt.get("record") or {}
    for clause in record.get("clauses") or []:
        label = (clause.get("modality") or {}).get("label")
        if isinstance(label, str) and label:
            return label
    return None


def evaluate_modality_labels(gold_eval_records: Sequence[Mapping[str, Any]],
                             attempts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Four-class modality label accuracy / macro-F1 (reported separately,
    never mixed into the six-field span table)."""
    gold_by_id = {r["sample_id"]: r for r in gold_eval_records}
    attempt_by_id = {a["sample_id"]: a for a in attempts}
    pairs = []
    for sid in sorted(gold_by_id):
        gold_label = _gold_modality_label(gold_by_id, sid)
        pred_label = _pred_modality_label(attempt_by_id.get(sid, {}))
        pairs.append({"sample_id": sid, "gold": gold_label, "predicted": pred_label})

    correct = sum(1 for p in pairs if p["gold"] == p["predicted"])
    n = len(pairs)
    accuracy = correct / n if n else None

    # macro-F1 over the four classes (gold class as reference)
    f1_scores = []
    for cls in MODALITY_CLASSES:
        tp = sum(1 for p in pairs if p["gold"] == cls and p["predicted"] == cls)
        fp = sum(1 for p in pairs if p["gold"] != cls and p["predicted"] == cls)
        fn = sum(1 for p in pairs if p["gold"] == cls and p["predicted"] != cls)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        f1_scores.append({"class": cls, "precision": prec, "recall": rec, "f1": f1})
    macro_f1 = sum(s["f1"] for s in f1_scores) / len(f1_scores) if f1_scores else None
    return {
        "schema_version": "formal_stage2_modality_labels@1.0.0",
        "classes": MODALITY_CLASSES,
        "records": n,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "per_class": f1_scores,
        "separate_from_span_metrics": True,
        "unlabeled_predictions": sum(1 for p in pairs if p["predicted"] is None),
    }


def strip_timing(attempts: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Canonical prediction records WITHOUT unstable timing fields.

    Keeps {sample_id, request_status, record, error_category}; runtime timing
    (latency_ms etc.) is isolated into telemetry and never enters canonical
    artifacts.
    """
    out = []
    for a in attempts:
        out.append({
            "sample_id": a["sample_id"],
            "request_status": a.get("request_status"),
            "record": a.get("record"),
            "error_category": a.get("error_category"),
        })
    return out


def telemetry_only(attempts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Isolated timing/cost telemetry (non-canonical)."""
    latencies = [a.get("runtime", {}).get("latency_ms") for a in attempts
                 if isinstance(a.get("runtime", {}).get("latency_ms"), (int, float))]
    total = sum(latencies)
    return {
        "schema_version": "formal_stage2_telemetry@1.0.0",
        "rows": len(attempts),
        "latency_ms_total": total,
        "latency_ms_mean": total / len(latencies) if latencies else None,
        "llm_call_performed_any": any(
            a.get("runtime", {}).get("llm_call_performed") for a in attempts),
        "note": "performance telemetry only; never part of canonical artifacts",
    }
