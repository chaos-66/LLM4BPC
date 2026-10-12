# -*- coding: utf-8 -*-
"""Shared explicit action-order projection v2 (TYPE A only for main metric).

The projection is deliberately conservative:

* native Stage-2 ``order_relations`` always win;
* only already-extracted Stage-2 action elements can become endpoints;
* a nominal phrase can never be promoted to an action;
* endpoint selection is deterministic and ambiguity produces no edge;
* no Gold, reference label, target activity, mutation, or method prediction is
  consulted.

The main Table 3-v2 out-of-order scope is TYPE A (explicit action -> action
precedence).  TYPE B is preserved as an extended diagnostic and TYPE C remains
unsupported/not-scored; this module generates edges without assigning the
scope classification, which is loaded from the frozen source-semantics
manifest.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, asdict
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_VERSION = "stage3_v2_order_projection@1.0.0"

# Pre-registered marker set and direction.  ``left_before_right`` means the
# action on the left of the marker precedes the action on the right.
MARKER_SPECS: tuple[tuple[str, str, str], ...] = (
    ("prior to", "left_before_right", r"\bprior\s+to\b"),
    ("in advance of", "left_before_right", r"\bin\s+advance\s+of\b"),
    ("before", "left_before_right", r"\bbefore\b"),
    ("preceding", "left_before_right", r"\bpreceding\b"),
    ("after", "right_before_left", r"\bafter\b"),
    ("following", "right_before_left", r"\bfollowing\b"),
    ("subsequent to", "right_before_left", r"\bsubsequent\s+to\b"),
)

NATIVE_PRECEDENCE = True
MAIN_ORDER_TYPE = "TYPE_A_explicit_action_precedence"
EXTENDED_ORDER_TYPE = "TYPE_B_trigger_precedence"
UNSUPPORTED_ORDER_TYPE = "TYPE_C_deadline_arithmetic_only"


@dataclass(frozen=True)
class Stage2ActionElement:
    action_id: str
    text: str
    start: int
    end: int
    clause_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class OrderProjectionError(RuntimeError):
    pass


def _sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def extract_stage2_actions(record: Mapping[str, Any] | None,
                           *, obligation_only: bool = True) -> list[Stage2ActionElement]:
    """Flatten valid action spans from a canonical Stage-2 record.

    Invalid or out-of-clause spans are ignored.  No action is invented and no
    nominal phrase is converted into an action.
    """
    record = record or {}
    actions: list[Stage2ActionElement] = []
    for clause_index, clause in enumerate(record.get("clauses") or []):
        if not isinstance(clause, Mapping):
            continue
        if obligation_only:
            modality = clause.get("modality")
            label = modality.get("label") if isinstance(modality, Mapping) else None
            if label != "obligation":
                continue
        clause_id = str(clause.get("clause_id") or f"clause_{clause_index}")
        for action_index, action in enumerate(clause.get("actions") or []):
            if not isinstance(action, Mapping):
                continue
            start = action.get("start")
            end = action.get("end")
            if not isinstance(start, int) or isinstance(start, bool):
                continue
            if not isinstance(end, int) or isinstance(end, bool):
                continue
            if start < 0 or end <= start:
                continue
            text = action.get("text")
            if not isinstance(text, str) or not text.strip():
                continue
            action_id = str(action.get("id") or f"{clause_id}.action.{action_index + 1}")
            actions.append(Stage2ActionElement(action_id=action_id, text=text,
                                               start=start, end=end, clause_id=clause_id))
    # Stable deterministic ordering; duplicates with the same ID are collapsed
    # only when their spans and text are identical.
    unique: dict[tuple[str, int, int, str], Stage2ActionElement] = {}
    for action in actions:
        unique[(action.action_id, action.start, action.end, action.text)] = action
    return sorted(unique.values(), key=lambda a: (a.start, a.end, a.action_id))


def normalize_native_order_relations(record: Mapping[str, Any] | None,
                                     action_lookup: Mapping[str, str] | None = None
                                     ) -> list[dict[str, Any]]:
    """Normalise native Stage-2 order relations without repairing them.

    Supported shapes include ``{before_span_id, after_span_id}``,
    ``{first_action, second_action}``, ``{before, after}``, and two-item
    string lists/tuples.  Unknown or incomplete entries are skipped.
    """
    action_lookup = action_lookup or {}
    output: list[dict[str, Any]] = []
    record = record or {}
    candidates: list[Any] = []
    if isinstance(record.get("order_relations"), list):
        candidates.extend(record["order_relations"])
    for clause in record.get("clauses") or []:
        if isinstance(clause, Mapping) and isinstance(clause.get("order_relations"), list):
            candidates.extend(clause["order_relations"])
    for entry in candidates:
        before_text = after_text = None
        before_id = after_id = None
        if isinstance(entry, Mapping):
            before_id = entry.get("before_span_id") or entry.get("before_action_id") or entry.get("before_id")
            after_id = entry.get("after_span_id") or entry.get("after_action_id") or entry.get("after_id")
            before_text = entry.get("before_text") or entry.get("first_action") or entry.get("before")
            after_text = entry.get("after_text") or entry.get("second_action") or entry.get("after")
            if before_id and not before_text:
                before_text = action_lookup.get(str(before_id))
            if after_id and not after_text:
                after_text = action_lookup.get(str(after_id))
        elif isinstance(entry, (list, tuple)) and len(entry) == 2:
            before_text, after_text = entry[0], entry[1]
        if not isinstance(before_text, str) or not isinstance(after_text, str):
            continue
        if not before_text.strip() or not after_text.strip():
            continue
        output.append({
            "before_action_id": str(before_id) if before_id is not None else None,
            "after_action_id": str(after_id) if after_id is not None else None,
            "before_text": before_text,
            "after_text": after_text,
            "source": "native_stage2_order_relation",
        })
    return output


def _selected_endpoint(candidates: Sequence[Stage2ActionElement],
                       marker_start: int,
                       marker_end: int,
                       *,
                       side: str,
                       sentence_start: int,
                       sentence_end: int,
                       max_document_distance: int = 400
                       ) -> tuple[Stage2ActionElement | None, dict[str, Any]]:
    """Return a unique nearest candidate or ``None`` with an audit record."""
    audit: dict[str, Any] = {
        "side": side,
        "candidate_count": 0,
        "selected_action_id": None,
        "selected_text": None,
        "selection_reason": None,
        "candidate_distances": [],
    }
    eligible: list[tuple[int, Stage2ActionElement]] = []
    for action in candidates:
        if action.end <= action.start:
            continue
        if side == "left":
            if action.end > marker_start:
                continue
            distance = marker_start - action.end
        elif side == "right":
            if action.start < marker_end:
                continue
            distance = action.start - marker_end
        else:
            raise OrderProjectionError(f"unknown side: {side!r}")
        if distance < 0 or distance > max_document_distance:
            continue
        if action.start < sentence_start or action.end > sentence_end:
            continue
        eligible.append((distance, action))
    audit["candidate_count"] = len(eligible)
    if not eligible:
        audit["selection_reason"] = "no_eligible_existing_action_endpoint"
        return None, audit
    eligible.sort(key=lambda item: (item[0], item[1].start, item[1].end, item[1].action_id))
    distances = sorted({dist for dist, _ in eligible})
    audit["candidate_distances"] = [
        {
            "action_id": action.action_id,
            "text": action.text,
            "distance": dist,
            "span": [action.start, action.end],
        }
        for dist, action in eligible
    ]
    if len(distances) > 1:
        best_distance = distances[0]
        tied = [action for dist, action in eligible if dist == best_distance]
        if len(tied) > 1:
            audit["selection_reason"] = "ambiguous_tie_for_nearest_candidate"
            return None, audit
        # A strict unique minimum is allowed by the pre-registered nearest-rule.
        selected = next(action for dist, action in eligible if dist == best_distance)
    else:
        tied = [action for dist, action in eligible]
        if len(tied) != 1:
            audit["selection_reason"] = "ambiguous_multiple_candidates_same_distance"
            return None, audit
        selected = tied[0]
    audit["selected_action_id"] = selected.action_id
    audit["selected_text"] = selected.text
    audit["selection_reason"] = "unique_nearest_existing_stage2_action"
    return selected, audit


class SharedActionOrderProjectionV2:
    """Deterministic action-bound order projection shared by Sun and Ours."""

    schema_version = SCHEMA_VERSION
    marker_specs = MARKER_SPECS

    def __init__(self, *, max_document_distance: int = 400):
        self.max_document_distance = int(max_document_distance)
        self._marker_patterns = [
            (name, orientation, re.compile(pattern, flags=re.IGNORECASE))
            for name, orientation, pattern in self.marker_specs
        ]

    # ------------------------------------------------------------------ public
    def project(self,
                source_text: str,
                record: Mapping[str, Any] | None = None,
                *,
                nlp: Any = None,
                rule_id: str = "",
                action_elements: Sequence[Stage2ActionElement | Mapping[str, Any]] | None = None,
                native_relations: Sequence[Mapping[str, Any]] | None = None
                ) -> dict[str, Any]:
        """Project order edges from one source text and one Stage-2 record.

        ``action_elements`` may be supplied by a caller that already extracted
        validated spans.  Otherwise action spans are read from ``record``.
        """
        if not isinstance(source_text, str):
            raise OrderProjectionError("source_text must be a string")
        actions = self._coerce_actions(action_elements) if action_elements is not None else extract_stage2_actions(record)
        action_lookup = {action.action_id: action.text for action in actions}
        native = list(native_relations) if native_relations is not None else normalize_native_order_relations(record, action_lookup)

        base: dict[str, Any] = {
            "schema_version": self.schema_version,
            "rule_id": str(rule_id),
            "source_text_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
            "action_count": len(actions),
            "native_relation_count": len(native),
            "native_precedence": NATIVE_PRECEDENCE,
            "endpoint_policy": "existing_stage2_action_only",
            "nominal_endpoint_policy": "forbidden",
            "actions": [action.to_dict() for action in actions],
            "marker_set": [name for name, _, _ in self.marker_specs],
            "markers": [],
            "edges": [],
            "edge_pairs": [],
            "status": None,
            "status_reason": None,
        }
        if native:
            edges = []
            for entry in native:
                edges.append({
                    "edge_id": f"{rule_id}:native:{len(edges) + 1}",
                    "before_action_id": entry.get("before_action_id"),
                    "after_action_id": entry.get("after_action_id"),
                    "before_text": entry.get("before_text"),
                    "after_text": entry.get("after_text"),
                    "marker": None,
                    "marker_span": None,
                    "orientation": "native_stage2",
                    "source": "native_stage2_order_relation",
                    "endpoint_policy": "native_stage2_action_reference",
                })
            base["edges"] = edges
            base["edge_pairs"] = [[e["before_text"], e["after_text"]] for e in edges]
            base["status"] = "native_preserved"
            base["status_reason"] = "native_order_relations_non_empty"
            return base

        if nlp is None:
            raise OrderProjectionError("spaCy nlp is required when native relations are absent")
        doc = nlp(source_text)
        marker_audits: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        seen: set[tuple[str | None, str | None, str, str]] = set()
        for marker_name, orientation, pattern in self._marker_patterns:
            for match in pattern.finditer(source_text):
                marker_start, marker_end = match.span()
                marker_token = doc.char_span(marker_start, marker_end, alignment_mode="expand")
                if marker_token is None:
                    marker_audits.append({
                        "marker": marker_name,
                        "marker_span": [marker_start, marker_end],
                        "orientation": orientation,
                        "status": "marker_token_not_found",
                        "edges_generated": 0,
                    })
                    continue
                sent = marker_token.sent
                sentence_start = int(sent.start_char)
                sentence_end = int(sent.end_char)
                left, left_audit = _selected_endpoint(
                    actions, marker_start, marker_end, side="left",
                    sentence_start=sentence_start, sentence_end=sentence_end,
                    max_document_distance=self.max_document_distance,
                )
                right, right_audit = _selected_endpoint(
                    actions, marker_start, marker_end, side="right",
                    sentence_start=sentence_start, sentence_end=sentence_end,
                    max_document_distance=self.max_document_distance,
                )
                audit = {
                    "marker": marker_name,
                    "marker_span": [marker_start, marker_end],
                    "orientation": orientation,
                    "sentence_span": [sentence_start, sentence_end],
                    "left_endpoint": left_audit,
                    "right_endpoint": right_audit,
                    "edges_generated": 0,
                    "status": None,
                }
                if left is None or right is None:
                    audit["status"] = "no_edge_endpoint_missing_or_ambiguous"
                    marker_audits.append(audit)
                    continue
                if left.action_id == right.action_id:
                    audit["status"] = "no_edge_same_endpoint"
                    marker_audits.append(audit)
                    continue
                if orientation == "left_before_right":
                    before, after = left, right
                elif orientation == "right_before_left":
                    before, after = right, left
                else:
                    audit["status"] = "no_edge_unknown_orientation"
                    marker_audits.append(audit)
                    continue
                dedupe_key = (before.action_id, after.action_id, marker_name, orientation)
                if dedupe_key in seen:
                    audit["status"] = "duplicate_edge_skipped"
                    marker_audits.append(audit)
                    continue
                seen.add(dedupe_key)
                edge = {
                    "edge_id": f"{rule_id}:order:{len(edges) + 1}",
                    "before_action_id": before.action_id,
                    "after_action_id": after.action_id,
                    "before_text": before.text,
                    "after_text": after.text,
                    "before_span": [before.start, before.end],
                    "after_span": [after.start, after.end],
                    "marker": marker_name,
                    "marker_span": [marker_start, marker_end],
                    "orientation": orientation,
                    "source": "shared_action_order_projection_v2",
                    "endpoint_policy": "existing_stage2_action_only",
                }
                edges.append(edge)
                audit["edges_generated"] = 1
                audit["status"] = "edge_generated"
                marker_audits.append(audit)
        base["markers"] = marker_audits
        base["edges"] = edges
        base["edge_pairs"] = [[e["before_text"], e["after_text"]] for e in edges]
        if not marker_audits:
            base["status"] = "no_marker_found"
            base["status_reason"] = "marker_set_absent"
        elif not edges:
            base["status"] = "no_edge"
            base["status_reason"] = "no_marker_had_two_bound_stage2_actions"
        else:
            base["status"] = "projected"
            base["status_reason"] = "at_least_one_marker_bound_two_existing_stage2_actions"
        return base

    @staticmethod
    def _coerce_actions(action_elements: Sequence[Stage2ActionElement | Mapping[str, Any]]
                        ) -> list[Stage2ActionElement]:
        actions: list[Stage2ActionElement] = []
        for item in action_elements:
            if isinstance(item, Stage2ActionElement):
                actions.append(item)
                continue
            if not isinstance(item, Mapping):
                continue
            actions.append(Stage2ActionElement(
                action_id=str(item.get("action_id") or item.get("id") or ""),
                text=str(item.get("text") or ""),
                start=int(item.get("start")),
                end=int(item.get("end")),
                clause_id=str(item.get("clause_id") or ""),
            ))
        return sorted(actions, key=lambda a: (a.start, a.end, a.action_id))


def project_record_order_relations_v2(record: Mapping[str, Any] | None,
                                      source_text: str,
                                      nlp: Any,
                                      *,
                                      rule_id: str = "",
                                      action_elements: Sequence[Stage2ActionElement | Mapping[str, Any]] | None = None,
                                      native_relations: Sequence[Mapping[str, Any]] | None = None
                                      ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compatibility function returning ``(edges, audit)``."""
    projection = SharedActionOrderProjectionV2()
    result = projection.project(
        source_text,
        record,
        nlp=nlp,
        rule_id=rule_id,
        action_elements=action_elements,
        native_relations=native_relations,
    )
    return list(result.get("edges") or []), result


def projection_freeze_manifest(*, projection: SharedActionOrderProjectionV2,
                               order_scope_manifest_sha256: str,
                               development_type_a_cases: Sequence[str]) -> dict[str, Any]:
    """Build the pre-registered order-projection freeze manifest."""
    return {
        "schema_version": "stage3_v2_order_projection_freeze@1.0.0",
        "status": "ORDER_PROJECTION_FROZEN",
        "supported_main_type": MAIN_ORDER_TYPE,
        "extended_diagnostic_type": EXTENDED_ORDER_TYPE,
        "unsupported_not_scored_type": UNSUPPORTED_ORDER_TYPE,
        "native_precedence": NATIVE_PRECEDENCE,
        "marker_set": [
            {"marker": name, "orientation": orientation, "pattern": pattern}
            for name, orientation, pattern in projection.marker_specs
        ],
        "endpoint_rules": {
            "must_bind_existing_stage2_action": True,
            "nominal_phrase_endpoint_forbidden": True,
            "left_endpoint": "action span ends at or before marker start",
            "right_endpoint": "action span starts at or after marker end",
            "same_sentence_required": True,
            "unique_nearest_deterministic": True,
            "tie_or_ambiguous_action": "no edge",
            "zero_or_one_side_endpoint": "no edge",
            "max_character_distance": projection.max_document_distance,
        },
        "pronoun_gerund_policy": "no sample-specific rule; endpoints must already be Stage-2 action spans",
        "gold_used": False,
        "reference_used": False,
        "prediction_used": False,
        "order_scope_manifest_sha256": order_scope_manifest_sha256,
        "development_type_a_cases": list(development_type_a_cases),
        "type_b_exclusion_rationale": (
            "Sun Definition 7 represents action-action precedence U_r subset A_r x A_r; "
            "TYPE_B trigger/event -> action is outside the native definition and is "
            "preserved as EXTENDED_TEMPORAL_DIAGNOSTIC."
        ),
        "type_c_exclusion_rationale": (
            "deadline arithmetic remains UNSUPPORTED_NOT_SCORED and is outside the "
            "main Table 3-v2 out-of-order metric."
        ),
        "implementation_sha256": _sha256({
            "schema_version": SCHEMA_VERSION,
            "marker_specs": MARKER_SPECS,
            "max_document_distance": projection.max_document_distance,
        }),
    }


__all__ = [
    "SCHEMA_VERSION",
    "MARKER_SPECS",
    "NATIVE_PRECEDENCE",
    "MAIN_ORDER_TYPE",
    "EXTENDED_ORDER_TYPE",
    "UNSUPPORTED_ORDER_TYPE",
    "Stage2ActionElement",
    "OrderProjectionError",
    "extract_stage2_actions",
    "normalize_native_order_relations",
    "SharedActionOrderProjectionV2",
    "project_record_order_relations_v2",
    "projection_freeze_manifest",
]
