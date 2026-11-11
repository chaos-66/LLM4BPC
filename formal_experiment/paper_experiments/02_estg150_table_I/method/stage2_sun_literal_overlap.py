"""Authoritative Sun-style six-field phrase-overlap evaluation.

The primary comparison view in ``MASTER_PIPELINE.md`` section 8.6 is global
within each statement and semantic field.  A predicted span contributes to
precision when it has any non-empty character intersection with at least one
Gold span in the same field.  A Gold span contributes to recall under the
mirror rule.  Clause alignment, overlap thresholds, and one-to-one assignment
are deliberately absent.

For modality this evaluator scores evidence spans only.  Modality-label
classification belongs to a separate report.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


SCHEMA_VERSION = "sun_literal_overlap_evaluation@2.0.0"
FIELDS = ("modality", "actor", "action", "condition", "constraint", "exception")
PLURAL_KEYS = {
    "actor": "actors",
    "action": "actions",
    "condition": "conditions",
    "constraint": "constraints",
    "exception": "exceptions",
}


class SunLiteralOverlapError(ValueError):
    """Raised when evaluation inputs violate the shared contract."""


def _validated_span(value: Mapping[str, Any], *, label: str) -> tuple[int, int]:
    start = value.get("start")
    end = value.get("end")
    if (
        isinstance(start, bool)
        or isinstance(end, bool)
        or not isinstance(start, int)
        or not isinstance(end, int)
        or start < 0
        or end <= start
    ):
        raise SunLiteralOverlapError(f"{label} has an invalid [start,end) span")
    return start, end


def _field_spans(record: Mapping[str, Any], field: str) -> list[Mapping[str, Any]]:
    clauses = record.get("clauses") or []
    if not isinstance(clauses, list):
        raise SunLiteralOverlapError("record clauses must be an array")
    spans: list[Mapping[str, Any]] = []
    for clause_index, clause in enumerate(clauses):
        if not isinstance(clause, Mapping):
            raise SunLiteralOverlapError(f"clause {clause_index} is not an object")
        if field == "modality":
            modality = clause.get("modality")
            if modality is None:
                values: Any = []
            elif not isinstance(modality, Mapping):
                raise SunLiteralOverlapError(
                    f"clause {clause_index} modality must be an object"
                )
            else:
                values = modality.get("evidence") or []
        else:
            values = clause.get(PLURAL_KEYS[field]) or []
        if not isinstance(values, list):
            raise SunLiteralOverlapError(
                f"clause {clause_index} field {field} must be an array"
            )
        for span_index, span in enumerate(values):
            if not isinstance(span, Mapping):
                raise SunLiteralOverlapError(
                    f"clause {clause_index} field {field} span {span_index} is not an object"
                )
            _validated_span(
                span,
                label=f"clause {clause_index} field {field} span {span_index}",
            )
            spans.append(span)
    return spans


def _intersects(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    left_start, left_end = _validated_span(left, label="left")
    right_start, right_end = _validated_span(right, label="right")
    return max(left_start, right_start) < min(left_end, right_end)


def _records_by_id(
    records: Sequence[Mapping[str, Any]], *, label: str
) -> dict[str, Mapping[str, Any]]:
    by_id: dict[str, Mapping[str, Any]] = {}
    for row in records:
        if not isinstance(row, Mapping):
            raise SunLiteralOverlapError(f"{label} rows must be objects")
        sample_id = row.get("sample_id")
        if not isinstance(sample_id, str) or not sample_id or sample_id in by_id:
            raise SunLiteralOverlapError(
                f"{label} sample_ids must be unique non-empty strings"
            )
        by_id[sample_id] = row
    return by_id


def _prf(
    *,
    extracted: int,
    ground_truth: int,
    matched_predictions: int,
    matched_ground_truth: int,
) -> dict[str, float | int]:
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


def evaluate_sun_literal_overlap(
    gold_records: Sequence[Mapping[str, Any]],
    attempts: Sequence[Mapping[str, Any]],
    *,
    dataset_id: str,
    method_id: str,
) -> dict[str, Any]:
    """Evaluate all six fields using independent statement-level coverage."""

    if not dataset_id or not method_id:
        raise SunLiteralOverlapError("dataset_id and method_id must be non-empty")
    gold_by_id = _records_by_id(gold_records, label="Gold")
    attempt_by_id = _records_by_id(attempts, label="attempt")
    if set(attempt_by_id) != set(gold_by_id):
        missing = sorted(set(gold_by_id) - set(attempt_by_id))[:5]
        extra = sorted(set(attempt_by_id) - set(gold_by_id))[:5]
        raise SunLiteralOverlapError(
            f"attempt membership differs from Gold: missing={missing}, extra={extra}"
        )

    counts = {
        field: {
            "ground_truth": 0,
            "extracted": 0,
            "matched_predictions": 0,
            "matched_ground_truth": 0,
        }
        for field in FIELDS
    }
    invalid_attempt_count = 0
    for sample_id, gold in gold_by_id.items():
        attempt = attempt_by_id[sample_id]
        predicted = attempt.get("record")
        if attempt.get("request_status") != "ok" or not isinstance(predicted, Mapping):
            invalid_attempt_count += 1
            predicted = {"clauses": []}
        for field in FIELDS:
            gold_spans = _field_spans(gold, field)
            predicted_spans = _field_spans(predicted, field)
            counts[field]["ground_truth"] += len(gold_spans)
            counts[field]["extracted"] += len(predicted_spans)
            counts[field]["matched_predictions"] += sum(
                any(_intersects(predicted_span, gold_span) for gold_span in gold_spans)
                for predicted_span in predicted_spans
            )
            counts[field]["matched_ground_truth"] += sum(
                any(
                    _intersects(gold_span, predicted_span)
                    for predicted_span in predicted_spans
                )
                for gold_span in gold_spans
            )

    per_field = {
        field: _prf(
            extracted=values["extracted"],
            ground_truth=values["ground_truth"],
            matched_predictions=values["matched_predictions"],
            matched_ground_truth=values["matched_ground_truth"],
        )
        for field, values in counts.items()
    }
    overall = _prf(
        extracted=sum(values["extracted"] for values in counts.values()),
        ground_truth=sum(values["ground_truth"] for values in counts.values()),
        matched_predictions=sum(
            values["matched_predictions"] for values in counts.values()
        ),
        matched_ground_truth=sum(
            values["matched_ground_truth"] for values in counts.values()
        ),
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "dataset_id": dataset_id,
        "method_id": method_id,
        "sample_count": len(gold_by_id),
        "invalid_attempt_count": invalid_attempt_count,
        "evaluation_unit": "statement",
        "match_rule": "independent_same_field_any_nonempty_character_span_intersection",
        "assignment": "none_independent_overlap_coverage",
        "clause_alignment_required": False,
        "overlap_threshold": "strictly_greater_than_zero_characters",
        "modality_policy": "evidence_span_extraction_only_label_ignored",
        "reporting_role": "primary_sun_phrase_extraction_metric",
        "per_field": per_field,
        "overall": overall,
    }
