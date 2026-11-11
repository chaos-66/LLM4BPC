"""D1 span-coordinate canonicalization (D1-R1 2026-08-05; grounding repair 2026-08).

The direct-LLM model usually returns the correct ``text`` for a span but
frequently reports ``start``/``end`` offsets that are off by a few characters
on long multi-clause sentences.  This module re-anchors a span to an exact
occurrence of its own surface text.  It NEVER edits ``text``, ``normalized``,
``id``, the field a span belongs to, or any modality label: only ``start`` and
``end`` may change (or an ungroundable span may be dropped).

Grounding hierarchy (Gold-blind, deterministic)
-----------------------------------------------
Level 0  the original coordinates are exact (``source_text[start:end] == text``)
         -> ``unchanged``.
Level 1  the text occurs exactly once inside the legal search window
         (``unique_exact``)
         -> re-anchor to that occurrence.
Level 2  the text occurs more than once (``repeated exact``).  The module uses
         the model's own original offsets as the only localisation evidence and
         never consults Gold:
           * candidates that still need grounding are grouped by
             ``(clause, field, exact text)``;
           * occurrences already claimed by already-grounded spans are removed
             from the pool (one occurrence is never reused);
           * the remaining candidates and occurrences are solved as a
             deterministic one-to-one minimum-cost assignment with cost
             ``|pred_start - actual_start| + |pred_end - actual_end|``
             (the two endpoints are the model's two localisation observations);
           * a candidate is re-anchored only when it is matched to the same
             occurrence in EVERY minimum-cost optimal assignment;
           * a candidate that is tied or otherwise not uniquely determined
             stays ``unresolved`` and is dropped from the canonical array.
Level 3  zero exact occurrence, empty text, non-integer offsets, structural
         problems -> ``unresolved`` / dropped.

Fail-safe rules: no fuzzy matching, no normalisation, no case folding, no
lemmatisation, no search outside the clause window, no random tie-breaking, and
no Gold-dependent choices.  Record-level structural violations still fail
closed; unrecoverable field spans and clauses are dropped as before.

Policies
--------
``policy="legacy"`` reproduces the pre-repair D1-R1 behaviour exactly
(repeated occurrences are dropped immediately).  Historical experiments that
formed frozen evidence under that behaviour must pin it explicitly.
``policy="repair_v1"`` is the promoted default: it opts into the new hierarchy
above.  The development experiment ``d_span_grounding_repair_v1`` selected it
explicitly for the NEW arm so the only changed factor was the grounding
algorithm; promotion was authorized after that evidence was verified.

Audit
-----
The audit keeps every historical key (``status``, ``reanchored_count``,
``dropped_spans``, ``dropped_clauses``, ``dropped_edges``, ...) and adds a
per-span ``resolution_events`` trail plus aggregate counters, so that a span the
model emitted and the canonicalizer dropped is never indistinguishable from a
span the model never emitted.
"""

from __future__ import annotations

import copy
import itertools
import math
from typing import Any, Mapping

STATUS_UNCHANGED = "unchanged"
STATUS_REANCHORED = "reanchored"
STATUS_DEGRADED = "degraded"
STATUS_FAILED = "failed"

POLICY_LEGACY = "legacy"
POLICY_REPAIR = "repair_v1"
# Promoted after d_span_grounding_repair_v1 verification: see the "Policies"
# note above. Historical frozen experiments explicitly pin POLICY_LEGACY.
DEFAULT_POLICY = POLICY_REPAIR

COST_METRIC_START_END = "abs_start_plus_abs_end"
COST_METRIC_START_ONLY = "abs_start_only"
DEFAULT_COST_METRIC = COST_METRIC_START_END

_VALID_POLICIES = (POLICY_LEGACY, POLICY_REPAIR)
_VALID_COST_METRICS = (COST_METRIC_START_END, COST_METRIC_START_ONLY)

SPAN_FIELDS = ("actors", "actions", "conditions", "constraints", "exceptions")

_KIND_UNCHANGED = "unchanged"
_KIND_REANCHORED_UNIQUE = "reanchored_unique_exact"
_KIND_AMBIGUOUS_REPEATED = "ambiguous_repeated_exact"
_KIND_ZERO_OCCURRENCE = "zero_occurrence"
_KIND_EMPTY_TEXT = "empty_span_text"
_KIND_NON_INTEGER = "non_integer_offsets"
_KIND_NOT_OBJECT = "span_not_object"

OUTCOME_UNCHANGED = "unchanged"
OUTCOME_REANCHORED_UNIQUE = "reanchored_unique_exact"
OUTCOME_REANCHORED_REPEATED = "reanchored_repeated_exact"
OUTCOME_UNRESOLVED = "unresolved"

STRATEGY_UNCHANGED = "unchanged"
STRATEGY_UNIQUE_EXACT = "unique_exact"
STRATEGY_NEAREST = "nearest_original_offsets"
STRATEGY_GLOBAL = "global_one_to_one_assignment"
STRATEGY_NOT_APPLICABLE = "not_applicable"

# Bounded exhaustive search keeps the assignment deterministic.  Groups in this
# corpus are tiny; anything larger fails safe to "unresolved" instead of
# guessing a tie-break.
_ASSIGNMENT_ENUMERATION_CAP = 200_000


class D1SpanCanonicalizationError(ValueError):
    """Raised for structural contract violations inside a record."""


def _is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _occurrences(needle: str, source_text: str, window_start: int, window_end: int) -> list[int]:
    starts: list[int] = []
    index = window_start
    while True:
        found = source_text.find(needle, index, window_end)
        if found == -1 or found + len(needle) > window_end:
            break
        starts.append(found)
        index = found + 1
    return starts


def _span_distance(
    candidate: tuple[int, int, int],
    occurrence_start: int,
    text: str,
    cost_metric: str,
) -> int:
    """Distance between one prediction and one exact occurrence.

    ``candidate`` is ``(prediction_index, pred_start, pred_end)``.  The default
    metric uses BOTH model-provided endpoints:
    ``|pred_start - actual_start| + |pred_end - actual_end|`` with
    ``actual_end = occurrence_start + len(text)``.  The start-only metric is
    kept for sensitivity reporting only.
    """
    _index, pred_start, pred_end = candidate
    if cost_metric == COST_METRIC_START_ONLY:
        return abs(pred_start - occurrence_start)
    return abs(pred_start - occurrence_start) + abs(pred_end - (occurrence_start + len(text)))


def _enumerate_optimal_assignments(
    candidates: list[tuple[int, int, int]],
    free_occurrences: list[int],
    text: str,
    cost_metric: str,
) -> tuple[int | None, list[tuple[int | None, ...]] | None]:
    """Enumerate every minimum-cost injective prediction->occurrence matching.

    Returns ``(best_cost, assignments)`` where ``assignments`` holds every
    optimal matching (each a tuple with one occurrence index, or ``None`` for an
    unmatched prediction, per candidate).  Returns ``(None, None)`` when the
    exhaustive enumeration would exceed the safety cap, so the caller can fail
    safe to ``unresolved`` instead of guessing.
    """
    pred_count = len(candidates)
    occ_count = len(free_occurrences)
    if pred_count == 0 or occ_count == 0:
        return 0, []
    matched = min(pred_count, occ_count)
    if pred_count <= occ_count:
        total = math.perm(occ_count, matched)
    else:
        total = math.comb(pred_count, matched) * math.factorial(matched)
    if total > _ASSIGNMENT_ENUMERATION_CAP:
        return None, None

    def cost(pred_index: int, occurrence_index: int) -> int:
        return _span_distance(
            candidates[pred_index], free_occurrences[occurrence_index], text, cost_metric)

    best_cost: int | None = None
    assignments: list[tuple[int | None, ...]] = []
    if pred_count <= occ_count:
        for permutation in itertools.permutations(range(occ_count), pred_count):
            total_cost = sum(cost(i, permutation[i]) for i in range(pred_count))
            if best_cost is None or total_cost < best_cost:
                best_cost = total_cost
                assignments = [permutation]
            elif total_cost == best_cost:
                assignments.append(permutation)
    else:
        for subset in itertools.combinations(range(pred_count), occ_count):
            for permutation in itertools.permutations(range(occ_count)):
                total_cost = sum(cost(subset[j], permutation[j]) for j in range(occ_count))
                if best_cost is not None and total_cost > best_cost:
                    continue
                assignment: list[int | None] = [None] * pred_count
                for j in range(occ_count):
                    assignment[subset[j]] = permutation[j]
                frozen = tuple(assignment)
                if best_cost is None or total_cost < best_cost:
                    best_cost = total_cost
                    assignments = [frozen]
                elif total_cost == best_cost:
                    assignments.append(frozen)
    return best_cost, assignments


def _pinned_assignments(
    assignments: list[tuple[int | None, ...]],
    pred_count: int,
) -> dict[int, int]:
    """Candidate indices that map to the SAME occurrence in every optimum."""
    pinned: dict[int, int] = {}
    for index in range(pred_count):
        values = {assignment[index] for assignment in assignments}
        if len(values) == 1:
            value = next(iter(values))
            if value is not None:
                pinned[index] = int(value)
    return pinned


def _classify_span(
    span: Mapping[str, Any],
    source_text: str,
    window_start: int,
    window_end: int,
) -> tuple[str, list[int]]:
    text = span.get("text")
    start = span.get("start")
    end = span.get("end")
    if not isinstance(text, str) or not text:
        return _KIND_EMPTY_TEXT, []
    if not _is_plain_int(start) or not _is_plain_int(end):
        return _KIND_NON_INTEGER, []
    if 0 <= start < end <= len(source_text) and source_text[start:end] == text:
        return _KIND_UNCHANGED, [int(start)]
    occurrences = _occurrences(text, source_text, window_start, window_end)
    if not occurrences:
        return _KIND_ZERO_OCCURRENCE, []
    if len(occurrences) == 1:
        return _KIND_REANCHORED_UNIQUE, occurrences
    return _KIND_AMBIGUOUS_REPEATED, occurrences


def _reanchor_span_legacy(
    span: Mapping[str, Any],
    source_text: str,
    window_start: int,
    window_end: int,
) -> tuple[Mapping[str, Any], str]:
    """Pre-repair D1-R1 behaviour, preserved verbatim for the legacy policy."""
    text = span.get("text")
    start = span.get("start")
    end = span.get("end")
    if not isinstance(text, str) or not text:
        return span, "empty_span_text"
    if not _is_plain_int(start) or not _is_plain_int(end):
        return span, "non_integer_offsets"
    if 0 <= start < end <= len(source_text) and source_text[start:end] == text:
        return span, STATUS_UNCHANGED
    starts = _occurrences(text, source_text, window_start, window_end)
    if len(starts) != 1:
        return span, ("zero_occurrence" if not starts else "ambiguous_occurrence")
    fixed = dict(span)
    fixed["start"] = starts[0]
    fixed["end"] = starts[0] + len(text)
    return fixed, STATUS_REANCHORED


def _occurrence_spans(text: str, occurrences: list[int]) -> list[dict[str, int]]:
    return [{"start": start, "end": start + len(text)} for start in occurrences]


def _append_event(
    audit: dict[str, Any],
    *,
    path: str,
    clause_index: int | None,
    clause_id: Any,
    field: str,
    span_index: int | None,
    span_id: Any,
    text: Any,
    normalized: Any,
    original_start: Any,
    original_end: Any,
    candidate_occurrences: list[dict[str, int]],
    strategy: str,
    chosen: tuple[int, int] | None,
    distance: int | None,
    outcome: str,
    reason: str | None,
    cost_metric: str,
) -> None:
    audit["resolution_events"].append({
        "path": path,
        "clause_index": clause_index,
        "clause_id": clause_id,
        "field": field,
        "span_index": span_index,
        "span_id": span_id,
        "text": text,
        "normalized": normalized,
        "original_start": original_start,
        "original_end": original_end,
        "candidate_occurrences": candidate_occurrences,
        "strategy": strategy,
        "chosen": ({"start": chosen[0], "end": chosen[1]} if chosen else None),
        "distance": distance,
        "outcome": outcome,
        "reason": reason,
        "cost_metric": cost_metric,
    })


def _process_span_list_legacy(
    spans: list[Any],
    *,
    source_text: str,
    window_start: int,
    window_end: int,
    field: str,
    event_prefix: str,
    clause_index: int,
    clause_id: Any,
    audit: dict[str, Any],
) -> list[Any]:
    kept: list[Any] = []
    for span_index, span in enumerate(spans):
        audit["field_span_count"] += 1
        path = f"{event_prefix}[{span_index}]"
        if not isinstance(span, Mapping):
            audit["dropped_spans"].append(path)
            audit["unresolved_spans"] += 1
            _append_event(audit, path=path, clause_index=clause_index, clause_id=clause_id,
                          field=field, span_index=span_index, span_id=None, text=None,
                          normalized=None, original_start=None, original_end=None,
                          candidate_occurrences=[], strategy=STRATEGY_NOT_APPLICABLE,
                          chosen=None, distance=None, outcome=OUTCOME_UNRESOLVED,
                          reason=_KIND_NOT_OBJECT, cost_metric=COST_METRIC_START_END)
            continue
        fixed, outcome = _reanchor_span_legacy(span, source_text, window_start, window_end)
        text = span.get("text")
        occurrences = _occurrences(text, source_text, window_start, window_end) if isinstance(text, str) and text else []
        candidates = _occurrence_spans(text, occurrences) if isinstance(text, str) else []
        if outcome == STATUS_UNCHANGED:
            kept.append(fixed)
            audit["unchanged_spans"] += 1
            _append_event(audit, path=path, clause_index=clause_index, clause_id=clause_id,
                          field=field, span_index=span_index, span_id=span.get("id"),
                          text=text, normalized=span.get("normalized"),
                          original_start=span.get("start"), original_end=span.get("end"),
                          candidate_occurrences=candidates, strategy=STRATEGY_UNCHANGED,
                          chosen=(fixed.get("start"), fixed.get("end")), distance=0,
                          outcome=OUTCOME_UNCHANGED, reason=None,
                          cost_metric=COST_METRIC_START_END)
        elif outcome == STATUS_REANCHORED:
            kept.append(fixed)
            audit["reanchored_count"] += 1
            audit["reanchored_unique_exact"] += 1
            chosen = (int(fixed["start"]), int(fixed["end"]))
            _append_event(audit, path=path, clause_index=clause_index, clause_id=clause_id,
                          field=field, span_index=span_index, span_id=span.get("id"),
                          text=text, normalized=span.get("normalized"),
                          original_start=span.get("start"), original_end=span.get("end"),
                          candidate_occurrences=candidates, strategy=STRATEGY_UNIQUE_EXACT,
                          chosen=chosen,
                          distance=_span_distance(
                              (span_index, int(span["start"]), int(span["end"])),
                              chosen[0], text, COST_METRIC_START_END),
                          outcome=OUTCOME_REANCHORED_UNIQUE, reason=None,
                          cost_metric=COST_METRIC_START_END)
        else:
            audit["dropped_spans"].append(path)
            audit["unresolved_spans"] += 1
            if outcome == "ambiguous_occurrence":
                audit["repeated_occurrence_cases"] += 1
                audit["repeated_occurrence_unresolved"] += 1
            _append_event(audit, path=path, clause_index=clause_index, clause_id=clause_id,
                          field=field, span_index=span_index, span_id=span.get("id"),
                          text=text, normalized=span.get("normalized"),
                          original_start=span.get("start"), original_end=span.get("end"),
                          candidate_occurrences=candidates, strategy=STRATEGY_NOT_APPLICABLE,
                          chosen=None, distance=None, outcome=OUTCOME_UNRESOLVED,
                          reason=outcome, cost_metric=COST_METRIC_START_END)
    return kept


def _process_span_list_repair(
    spans: list[Any],
    *,
    source_text: str,
    window_start: int,
    window_end: int,
    field: str,
    event_prefix: str,
    clause_index: int,
    clause_id: Any,
    audit: dict[str, Any],
    cost_metric: str,
) -> list[Any]:
    decisions: list[dict[str, Any]] = []
    for span_index, span in enumerate(spans):
        audit["field_span_count"] += 1
        path = f"{event_prefix}[{span_index}]"
        if not isinstance(span, Mapping):
            decisions.append({"kind": _KIND_NOT_OBJECT, "span": None, "path": path,
                              "span_index": span_index, "occurrences": []})
            continue
        kind, occurrences = _classify_span(span, source_text, window_start, window_end)
        decisions.append({"kind": kind, "span": span, "path": path,
                          "span_index": span_index, "occurrences": occurrences})

    claimed: set[int] = set()
    for decision in decisions:
        if decision["kind"] == _KIND_UNCHANGED:
            claimed.add(int(decision["span"]["start"]))
        elif decision["kind"] == _KIND_REANCHORED_UNIQUE:
            claimed.add(int(decision["occurrences"][0]))

    groups: dict[str, list[int]] = {}
    for index, decision in enumerate(decisions):
        if decision["kind"] == _KIND_AMBIGUOUS_REPEATED:
            groups.setdefault(decision["span"]["text"], []).append(index)

    for text, indices in groups.items():
        audit["repeated_occurrence_cases"] += len(indices)
        if len(indices) > 1:
            audit["one_to_one_assignment_cases"] += 1
        free_occurrences = [
            start for start in _occurrences(text, source_text, window_start, window_end)
            if start not in claimed
        ]
        candidates = [
            (index, int(decisions[index]["span"]["start"]), int(decisions[index]["span"]["end"]))
            for index in indices
        ]
        strategy = STRATEGY_NEAREST if len(indices) == 1 else STRATEGY_GLOBAL
        if not free_occurrences:
            for index in indices:
                decisions[index]["resolution"] = {
                    "outcome": OUTCOME_UNRESOLVED, "strategy": strategy,
                    "chosen": None, "distance": None, "reason": "no_free_occurrence",
                }
            continue
        _best_cost, assignments = _enumerate_optimal_assignments(
            candidates, free_occurrences, text, cost_metric)
        if assignments is None:
            for index in indices:
                decisions[index]["resolution"] = {
                    "outcome": OUTCOME_UNRESOLVED, "strategy": strategy,
                    "chosen": None, "distance": None,
                    "reason": "assignment_uniqueness_unverifiable",
                }
            continue
        if len(assignments) > 1:
            audit["assignment_ambiguities"] += 1
        pinned = _pinned_assignments(assignments, len(candidates))
        for candidate_index, index in enumerate(indices):
            values = {assignment[candidate_index] for assignment in assignments}
            if len(values) > 1:
                audit["tie_cases"] += 1
            if candidate_index in pinned:
                occurrence = free_occurrences[pinned[candidate_index]]
                decisions[index]["resolution"] = {
                    "outcome": OUTCOME_REANCHORED_REPEATED, "strategy": strategy,
                    "chosen": (occurrence, occurrence + len(text)),
                    "distance": _span_distance(candidates[candidate_index], occurrence, text, cost_metric),
                    "reason": None,
                }
            else:
                if len(values) > 1:
                    reason = "equal_minimum_cost_assignment"
                elif len(candidates) > len(free_occurrences):
                    reason = "insufficient_free_occurrences_for_all_predictions"
                else:
                    reason = "assignment_not_uniquely_determined"
                decisions[index]["resolution"] = {
                    "outcome": OUTCOME_UNRESOLVED, "strategy": strategy,
                    "chosen": None, "distance": None, "reason": reason,
                }

    kept: list[Any] = []
    for index, decision in enumerate(decisions):
        kind = decision["kind"]
        span = decision["span"]
        path = decision["path"]
        span_index = decision["span_index"]
        text = span.get("text") if isinstance(span, Mapping) else None
        normalized = span.get("normalized") if isinstance(span, Mapping) else None
        span_id = span.get("id") if isinstance(span, Mapping) else None
        original_start = span.get("start") if isinstance(span, Mapping) else None
        original_end = span.get("end") if isinstance(span, Mapping) else None
        candidates = (_occurrence_spans(text, decision["occurrences"])
                      if isinstance(text, str) and text else [])
        if kind in (_KIND_NOT_OBJECT, _KIND_EMPTY_TEXT, _KIND_NON_INTEGER, _KIND_ZERO_OCCURRENCE):
            audit["dropped_spans"].append(path)
            audit["unresolved_spans"] += 1
            _append_event(audit, path=path, clause_index=clause_index, clause_id=clause_id,
                          field=field, span_index=span_index, span_id=span_id, text=text,
                          normalized=normalized, original_start=original_start,
                          original_end=original_end, candidate_occurrences=candidates,
                          strategy=STRATEGY_NOT_APPLICABLE, chosen=None, distance=None,
                          outcome=OUTCOME_UNRESOLVED, reason=kind, cost_metric=cost_metric)
            continue
        if kind == _KIND_UNCHANGED:
            kept.append(span)
            audit["unchanged_spans"] += 1
            chosen = (int(span["start"]), int(span["end"]))
            _append_event(audit, path=path, clause_index=clause_index, clause_id=clause_id,
                          field=field, span_index=span_index, span_id=span_id, text=text,
                          normalized=normalized, original_start=original_start,
                          original_end=original_end, candidate_occurrences=candidates,
                          strategy=STRATEGY_UNCHANGED, chosen=chosen, distance=0,
                          outcome=OUTCOME_UNCHANGED, reason=None, cost_metric=cost_metric)
            continue
        if kind == _KIND_REANCHORED_UNIQUE:
            occurrence = decision["occurrences"][0]
            fixed = dict(span)
            fixed["start"] = occurrence
            fixed["end"] = occurrence + len(text)
            kept.append(fixed)
            audit["reanchored_count"] += 1
            audit["reanchored_unique_exact"] += 1
            _append_event(audit, path=path, clause_index=clause_index, clause_id=clause_id,
                          field=field, span_index=span_index, span_id=span_id, text=text,
                          normalized=normalized, original_start=original_start,
                          original_end=original_end, candidate_occurrences=candidates,
                          strategy=STRATEGY_UNIQUE_EXACT,
                          chosen=(int(fixed["start"]), int(fixed["end"])),
                          distance=_span_distance(
                              (span_index, int(original_start), int(original_end)),
                              occurrence, text, cost_metric),
                          outcome=OUTCOME_REANCHORED_UNIQUE, reason=None,
                          cost_metric=cost_metric)
            continue
        if kind == _KIND_AMBIGUOUS_REPEATED:
            resolution = decision["resolution"]
            if resolution["outcome"] == OUTCOME_REANCHORED_REPEATED:
                fixed = dict(span)
                fixed["start"], fixed["end"] = resolution["chosen"]
                kept.append(fixed)
                audit["reanchored_count"] += 1
                audit["reanchored_repeated_exact"] += 1
                audit["repeated_occurrence_recovered"] += 1
                _append_event(audit, path=path, clause_index=clause_index, clause_id=clause_id,
                              field=field, span_index=span_index, span_id=span_id, text=text,
                              normalized=normalized, original_start=original_start,
                              original_end=original_end, candidate_occurrences=candidates,
                              strategy=resolution["strategy"],
                              chosen=resolution["chosen"],
                              distance=resolution["distance"],
                              outcome=OUTCOME_REANCHORED_REPEATED, reason=None,
                              cost_metric=cost_metric)
            else:
                audit["dropped_spans"].append(path)
                audit["unresolved_spans"] += 1
                audit["repeated_occurrence_unresolved"] += 1
                _append_event(audit, path=path, clause_index=clause_index, clause_id=clause_id,
                              field=field, span_index=span_index, span_id=span_id, text=text,
                              normalized=normalized, original_start=original_start,
                              original_end=original_end, candidate_occurrences=candidates,
                              strategy=resolution["strategy"], chosen=None, distance=None,
                              outcome=OUTCOME_UNRESOLVED, reason=resolution["reason"],
                              cost_metric=cost_metric)
            continue
        raise D1SpanCanonicalizationError(f"unknown span decision kind: {kind!r}")
    return kept


def canonicalize_record_coordinates(
    record: Any,
    source_text: Any,
    *,
    policy: str = DEFAULT_POLICY,
    cost_metric: str = DEFAULT_COST_METRIC,
) -> tuple[Any, dict[str, Any]]:
    """Canonicalize every span coordinate in a direct-LLM canonical record.

    Returns ``(canonicalized_record, audit)``.  Field-span and clause-level
    problems degrade the record (elements dropped, audit records every drop);
    only record-level structural violations fail closed.

    ``policy`` selects ``legacy`` (historical pre-repair behaviour) or
    ``repair_v1`` (the promoted default grounding repair); ``cost_metric``
    selects the repeated-occurrence distance (sensitivity only; the repair
    default uses both endpoints).
    """
    if policy not in _VALID_POLICIES:
        raise D1SpanCanonicalizationError(f"unknown policy: {policy!r}")
    if cost_metric not in _VALID_COST_METRICS:
        raise D1SpanCanonicalizationError(f"unknown cost metric: {cost_metric!r}")

    audit: dict[str, Any] = {
        "attempted": True,
        "status": STATUS_UNCHANGED,
        "policy": policy,
        "cost_metric": cost_metric,
        "clause_span_count": 0,
        "field_span_count": 0,
        "reanchored_count": 0,
        "dropped_spans": [],
        "dropped_clauses": [],
        "dropped_edges": [],
        "failed_reasons": [],
        "resolution_events": [],
        "unchanged_spans": 0,
        "unresolved_spans": 0,
        "reanchored_unique_exact": 0,
        "reanchored_repeated_exact": 0,
        "repeated_occurrence_cases": 0,
        "repeated_occurrence_recovered": 0,
        "repeated_occurrence_unresolved": 0,
        "tie_cases": 0,
        "one_to_one_assignment_cases": 0,
        "assignment_ambiguities": 0,
    }
    if not isinstance(record, Mapping):
        audit["status"] = STATUS_FAILED
        audit["failed_reasons"].append("record_not_object")
        return record, audit
    if not isinstance(source_text, str) or not source_text:
        audit["status"] = STATUS_FAILED
        audit["failed_reasons"].append("empty_source_text")
        return record, audit

    out = copy.deepcopy(record)
    clauses = out.get("clauses")
    if clauses is None:
        out["clauses"] = []
        return out, audit
    if not isinstance(clauses, list):
        audit["status"] = STATUS_FAILED
        audit["failed_reasons"].append("clauses_not_list")
        return record, audit

    def degraded() -> None:
        if audit["status"] != STATUS_FAILED and (
            audit["dropped_spans"] or audit["dropped_clauses"] or audit["dropped_edges"]
        ):
            audit["status"] = STATUS_DEGRADED

    kept: list[Any] = []
    for ci, clause in enumerate(clauses):
        clause_id = clause.get("clause_id") if isinstance(clause, Mapping) else None
        if not isinstance(clause, Mapping):
            audit["dropped_clauses"].append(ci)
            _append_event(audit, path=f"clauses[{ci}]", clause_index=ci, clause_id=clause_id,
                          field="clause", span_index=None, span_id=None, text=None,
                          normalized=None, original_start=None, original_end=None,
                          candidate_occurrences=[], strategy=STRATEGY_NOT_APPLICABLE,
                          chosen=None, distance=None, outcome=OUTCOME_UNRESOLVED,
                          reason="clause_not_object", cost_metric=cost_metric)
            degraded()
            continue
        cs = clause.get("clause_span")
        if cs is None:
            audit["dropped_clauses"].append(ci)
            _append_event(audit, path=f"clauses[{ci}].clause_span", clause_index=ci,
                          clause_id=clause_id, field="clause_span", span_index=None,
                          span_id=None, text=None, normalized=None, original_start=None,
                          original_end=None, candidate_occurrences=[],
                          strategy=STRATEGY_NOT_APPLICABLE, chosen=None, distance=None,
                          outcome=OUTCOME_UNRESOLVED, reason="missing_clause_span",
                          cost_metric=cost_metric)
            degraded()
            continue
        if not isinstance(cs, Mapping):
            audit["dropped_clauses"].append(ci)
            _append_event(audit, path=f"clauses[{ci}].clause_span", clause_index=ci,
                          clause_id=clause_id, field="clause_span", span_index=None,
                          span_id=None, text=None, normalized=None, original_start=None,
                          original_end=None, candidate_occurrences=[],
                          strategy=STRATEGY_NOT_APPLICABLE, chosen=None, distance=None,
                          outcome=OUTCOME_UNRESOLVED, reason="clause_span_not_object",
                          cost_metric=cost_metric)
            degraded()
            continue
        # Clause spans keep the original, deliberately conservative contract
        # (unique exact re-anchor; otherwise the clause is dropped).  The
        # repeated-occurrence repair is scoped to field/modality spans.
        fixed_cs, outcome = _reanchor_span_legacy(cs, source_text, 0, len(source_text))
        cs_text = cs.get("text")
        cs_occurrences = (_occurrences(cs_text, source_text, 0, len(source_text))
                          if isinstance(cs_text, str) and cs_text else [])
        if outcome not in (STATUS_UNCHANGED, STATUS_REANCHORED):
            audit["dropped_clauses"].append(ci)
            _append_event(audit, path=f"clauses[{ci}].clause_span", clause_index=ci,
                          clause_id=clause_id, field="clause_span", span_index=None,
                          span_id=None, text=cs_text, normalized=cs.get("normalized"),
                          original_start=cs.get("start"), original_end=cs.get("end"),
                          candidate_occurrences=_occurrence_spans(cs_text, cs_occurrences)
                          if isinstance(cs_text, str) else [],
                          strategy=STRATEGY_NOT_APPLICABLE, chosen=None, distance=None,
                          outcome=OUTCOME_UNRESOLVED, reason=outcome, cost_metric=cost_metric)
            degraded()
            continue
        audit["clause_span_count"] += 1
        if outcome == STATUS_REANCHORED:
            audit["reanchored_count"] += 1
            audit["reanchored_unique_exact"] += 1
        cs_chosen = (int(fixed_cs["start"]), int(fixed_cs["end"]))
        _append_event(audit, path=f"clauses[{ci}].clause_span", clause_index=ci,
                      clause_id=clause_id, field="clause_span", span_index=None,
                      span_id=None, text=cs_text, normalized=cs.get("normalized"),
                      original_start=cs.get("start"), original_end=cs.get("end"),
                      candidate_occurrences=_occurrence_spans(cs_text, cs_occurrences)
                      if isinstance(cs_text, str) else [],
                      strategy=STRATEGY_UNCHANGED if outcome == STATUS_UNCHANGED else STRATEGY_UNIQUE_EXACT,
                      chosen=cs_chosen, distance=0 if outcome == STATUS_UNCHANGED else None,
                      outcome=OUTCOME_UNCHANGED if outcome == STATUS_UNCHANGED else OUTCOME_REANCHORED_UNIQUE,
                      reason=None, cost_metric=cost_metric)
        if not _is_plain_int(fixed_cs.get("start")) or not _is_plain_int(fixed_cs.get("end")):
            audit["dropped_clauses"].append(ci)
            degraded()
            continue
        clause["clause_span"] = fixed_cs
        window_start, window_end = int(fixed_cs["start"]), int(fixed_cs["end"])

        modality = clause.get("modality")
        if isinstance(modality, Mapping):
            evidence = modality.get("evidence")
            if isinstance(evidence, list):
                if policy == POLICY_LEGACY:
                    kept_evidence = _process_span_list_legacy(
                        evidence, source_text=source_text, window_start=window_start,
                        window_end=window_end, field="modality.evidence",
                        event_prefix=f"clauses[{ci}].modality.evidence",
                        clause_index=ci, clause_id=clause_id, audit=audit)
                else:
                    kept_evidence = _process_span_list_repair(
                        evidence, source_text=source_text, window_start=window_start,
                        window_end=window_end, field="modality.evidence",
                        event_prefix=f"clauses[{ci}].modality.evidence",
                        clause_index=ci, clause_id=clause_id, audit=audit,
                        cost_metric=cost_metric)
                modality["evidence"] = kept_evidence

        for field in SPAN_FIELDS:
            spans = clause.get(field)
            if spans is None:
                continue
            if not isinstance(spans, list):
                audit["dropped_clauses"].append(ci)
                degraded()
                continue
            if policy == POLICY_LEGACY:
                kept_spans = _process_span_list_legacy(
                    spans, source_text=source_text, window_start=window_start,
                    window_end=window_end, field=field,
                    event_prefix=f"clauses[{ci}].{field}",
                    clause_index=ci, clause_id=clause_id, audit=audit)
            else:
                kept_spans = _process_span_list_repair(
                    spans, source_text=source_text, window_start=window_start,
                    window_end=window_end, field=field,
                    event_prefix=f"clauses[{ci}].{field}",
                    clause_index=ci, clause_id=clause_id, audit=audit,
                    cost_metric=cost_metric)
            clause[field] = kept_spans

        actor_ids = {s.get("id") for s in (clause.get("actors") or [])}
        action_ids = {s.get("id") for s in (clause.get("actions") or [])}
        kept_edges: list[Any] = []
        for ei, edge in enumerate(clause.get("actor_action_map") or []):
            if isinstance(edge, Mapping) and (
                edge.get("actor_id") is None or edge.get("actor_id") in actor_ids
            ) and edge.get("action_id") in action_ids:
                kept_edges.append(edge)
            else:
                audit["dropped_edges"].append(f"clauses[{ci}].actor_action_map[{ei}]")
                degraded()
        clause["actor_action_map"] = kept_edges
        kept_relations: list[Any] = []
        for oi, rel in enumerate(clause.get("order_relations") or []):
            if isinstance(rel, Mapping) and rel.get("before_action_id") in action_ids and rel.get("after_action_id") in action_ids:
                kept_relations.append(rel)
            else:
                audit["dropped_edges"].append(f"clauses[{ci}].order_relations[{oi}]")
                degraded()
        clause["order_relations"] = kept_relations
        kept.append(clause)

    out["clauses"] = kept
    # Any field-span drop degrades the record exactly like the pre-repair code.
    degraded()
    if audit["status"] == STATUS_UNCHANGED and audit["reanchored_count"]:
        audit["status"] = STATUS_REANCHORED
    return out, audit