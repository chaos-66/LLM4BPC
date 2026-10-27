# -*- coding: utf-8 -*-
"""Formal Part 2 (Stage 2) main-view evaluation: ORIGINAL Gold spans.

Contract: ``configs/evaluation/g04_evaluation_views_contract_v2.json``
(user decision 2026-10-27).  View id: ``fine_gold_span``.

Why this module exists
----------------------
Until 2026-10-27 the paper's Stage 2 main report scored the coarse sentence
view, which replaced every semantic field of a sentence by the envelope
``[min(start), max(end))`` over all its annotated spans -- on the GOLD side
only, while predictions were scored unmerged.  A prediction lying between two
annotated spans therefore earned match credit without overlapping any
annotated span (824 reference spans collapsed to 459; 103/150 samples
affected).

The decision was to keep the existing non-one-to-one overlap rule and remove
the Gold-side envelope merge.  This module implements exactly that view:

- reference side: the annotated spans of the published Gold, each kept as its
  own reference span (no merge, no clip, no alignment);
- prediction side: the validated prediction spans, unmerged;
- match: non-empty character intersection, same sample and same field;
- assignment: none (a prediction may cover several Gold spans and vice versa);
- Overall: micro pooling of the evaluator's own counters over
  actor/action/condition/constraint/exception;
- modality: four-class label macro-F1, reported separately.

It is deliberately additive.  The frozen historical modules
(``formal_stage2_evaluation``, ``sep_c3_modular_evaluation``,
``stage2_sun_literal_overlap``, ``g04_coarse_view``) are byte-identical to the
versions their authorized runs used and are NOT modified here; the coarse view
stays readable through :func:`bpc_hybrid.sep_c3_modular_evaluation.evaluate_coarse`.

Table I (Sun vs LLM-SE) and Table II (E/S/J factorial) must both go through
:func:`evaluate_primary_view` so they cannot drift apart.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from bpc_hybrid.formal_stage2_evaluation import (
    POOLED_METRIC_ID,
    SPAN_FIELDS,
    evaluate_modality_labels,
    evaluate_span_metrics,
    published_gold_to_evaluator,
)
from bpc_hybrid.stage2_sun_literal_overlap import evaluate_sun_literal_overlap

#: Formal main view (contract v2): original annotated Gold spans.
PRIMARY_VIEW_ID = "fine_gold_span"
#: Historical / diagnostic view (contract v1).  Never the paper main score.
LEGACY_COARSE_VIEW_ID = "coarse_sentence_level"
CONTRACT_ID = "g04_evaluation_views_contract_v2"
CONTRACT_PATH = "configs/evaluation/g04_evaluation_views_contract_v2.json"
MATCH_RULE = "independent_same_field_any_nonempty_character_span_intersection"
COORDINATE_CONVENTION = (
    "zero-based character offsets into approved_text_en, half-open [start,end)")
#: Formal main-view metric id (Table I "Overall (Micro-F1)" / Table II F1).
PRIMARY_METRIC = "five_field_micro_f1"
DATASET_ID = "independently_reconstructed_estg_150_v1"


def primary_gold_view(gold_doc: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Reference side of the formal main view (``fine_gold_span``).

    Identity over the published Gold spans: every annotated span of every
    clause stays its own reference span.  No ``[min(start), max(end))``
    envelope, no clause merge, no sentence merge, nothing synthesized.
    """
    return published_gold_to_evaluator(gold_doc)


def _micro_prf(counts: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    extracted = sum(int(v.get("extracted") or 0) for v in counts.values())
    ground_truth = sum(int(v.get("ground_truth") or 0) for v in counts.values())
    matched_predictions = sum(
        int(v.get("matched_predictions") or 0) for v in counts.values())
    matched_ground_truth = sum(
        int(v.get("matched_ground_truth") or 0) for v in counts.values())
    precision = matched_predictions / extracted if extracted else 0.0
    recall = matched_ground_truth / ground_truth if ground_truth else 0.0
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    return {
        "ground_truth": ground_truth,
        "extracted": extracted,
        "matched_predictions": matched_predictions,
        "matched_ground_truth": matched_ground_truth,
        "misclassified": extracted - matched_predictions,
        "missed": ground_truth - matched_ground_truth,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def evaluate_primary_view(gold_doc: Mapping[str, Any],
                          attempts: Sequence[Mapping[str, Any]], *,
                          dataset_id: str = DATASET_ID,
                          method_id: str) -> dict[str, Any]:
    """THE formal paper main-view Stage 2 evaluation (contract v2).

    ``attempts`` are canonical envelopes
    ``{sample_id, request_status, record: {...}}``.  Failed rows must remain
    present; the frozen evaluator counts them as empty predictions.

    Returns ``span`` (the ``evaluate_span_metrics`` report on the original Gold
    spans, whose ``pooled_five_span_fields`` is the reported Overall
    Micro-F1), the five-field micro P/R/F1, and the separate four-class
    modality-label metrics.
    """
    gold_eval = primary_gold_view(gold_doc)
    span = evaluate_span_metrics(
        gold_eval, list(attempts), dataset_id=dataset_id,
        method_id=method_id, view=PRIMARY_VIEW_ID)
    if span["modality_span"]["ground_truth"]:
        raise RuntimeError(
            "the formal main view must never synthesize modality evidence "
            "spans")

    raw = evaluate_sun_literal_overlap(
        gold_eval, list(attempts), dataset_id=dataset_id,
        method_id=method_id)
    per_field = raw.get("per_field") or {}
    five = {field: dict(per_field.get(field) or {}) for field in SPAN_FIELDS}
    micro = _micro_prf(five)
    pooled = span["pooled_five_span_fields"]
    for key in ("ground_truth", "extracted", "matched_predictions",
                "matched_ground_truth", "precision", "recall", "f1"):
        if pooled.get(key) != micro.get(key):
            raise RuntimeError(
                f"primary-view evaluator parity mismatch for pooled.{key}: "
                f"official={pooled.get(key)!r} raw={micro.get(key)!r}")

    f1_values = [float(v.get("f1") or 0.0) for v in five.values()]
    mean_f1 = sum(f1_values) / len(f1_values) if f1_values else 0.0
    labels = evaluate_modality_labels(gold_eval, list(attempts))

    return {
        "schema_version": "sep_c3_primary_five_field_evaluation@2.0.0",
        "contract_id": CONTRACT_ID,
        "contract_path": CONTRACT_PATH,
        "dataset_id": dataset_id,
        "method_id": method_id,
        "view": PRIMARY_VIEW_ID,
        "view_role": "formal main report",
        "gold_view": "published_gold_spans_as_is_no_envelope_merge",
        "reference_side": "original annotated Gold spans (one per annotated span)",
        "prediction_side": "original validated prediction spans (unmerged)",
        "primary_metric": PRIMARY_METRIC,
        "overall_metric_id": POOLED_METRIC_ID,
        "primary_metric_note": (
            "micro pooled five-span-field F1 from the evaluator's own "
            "counters; identical family to the Table I Overall (Micro-F1) "
            "column; the modality label is reported separately and is never "
            "mixed into this score"),
        "match_rule": MATCH_RULE,
        "coordinate_convention": COORDINATE_CONVENTION,
        "assignment": "none_independent_overlap_coverage",
        "span": span,
        "span_fields": span["span_fields"],
        "five_fields": five,
        "five_field_micro": micro,
        "five_field_mean_f1": mean_f1,
        "overall_micro_f1": pooled["f1"],
        "modality_labels": labels,
        "modality_evidence_span": {
            "available": False,
            "policy": ("published decision-only Gold has no local modality "
                       "evidence spans; never zeroed or aggregated into the "
                       "span F1"),
        },
        "denominator": len(attempts),
        "failed_count": sum(
            1 for a in attempts if a.get("request_status") != "ok"),
        "rounding": "stored at full precision; 3 decimals for paper display",
    }
