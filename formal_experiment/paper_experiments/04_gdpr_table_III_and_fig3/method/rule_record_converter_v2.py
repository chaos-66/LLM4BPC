# -*- coding: utf-8 -*-
"""Canonical Stage-2 record -> shared Stage-3-v2 rule record.

The converter keeps the frozen Stage-2 label semantics and the Sun Definitions
5-7 action/actor denominator.  It replaces only the order-relation adapter:
native Stage-2 order relations are preserved when present, and otherwise
``SharedActionOrderProjectionV2`` derives only action-action edges whose
endpoints are already-validated Stage-2 action spans.
"""

from __future__ import annotations

from typing import Any, Mapping

from .action_order_projection_v2 import (
    SharedActionOrderProjectionV2,
    extract_stage2_actions,
    normalize_native_order_relations,
)

SCHEMA_VERSION = "stage3_v2_rule_record_converter@1.0.0"


class RuleRecordConversionError(RuntimeError):
    pass


def canonical_to_rule_record_v2(record: Mapping[str, Any] | None,
                                source_text: str,
                                rule_id: str,
                                nlp: Any,
                                *,
                                projection: SharedActionOrderProjectionV2 | None = None,
                                order_adapter: Any | None = None,
                                ) -> dict[str, Any]:
    """Convert one frozen Stage-2 canonical record to a Sun-scorer record.

    No label repair is performed.  Invalid spans are dropped and recorded in the
    audit; actor-action links are retained only when both IDs resolve to valid
    included spans.
    """
    if not isinstance(source_text, str):
        raise RuleRecordConversionError("source_text must be a string")
    projection = projection or SharedActionOrderProjectionV2()

    actions: list[str] = []
    actors: list[str] = []
    actor_action_pairs: list[dict[str, str]] = []
    action_elements: list[dict[str, Any]] = []
    dropped: list[str] = []
    included_clauses = 0

    if not isinstance(record, Mapping):
        return {
            "rule_id": str(rule_id),
            "actions": [],
            "actors": [],
            "actor_action_pairs": [],
            "order_relations": [],
            "failed": True,
            "failure_reasons": ["missing_or_invalid_record"],
            "conversion_audit": {
                "included_clauses": 0,
                "dropped_spans": [],
                "order_projection": {"status": "not_attempted"},
            },
        }

    for clause_index, clause in enumerate(record.get("clauses") or []):
        if not isinstance(clause, Mapping):
            dropped.append(f"clauses[{clause_index}]")
            continue
        modality = clause.get("modality")
        label = modality.get("label") if isinstance(modality, Mapping) else None
        if label != "obligation":
            continue
        clause_id = str(clause.get("clause_id") or f"clause_{clause_index}")
        included_clauses += 1

        action_by_id: dict[Any, str] = {}
        actor_by_id: dict[Any, str] = {}
        for field, target, id_map in (
            ("actions", actions, action_by_id),
            ("actors", actors, actor_by_id),
        ):
            for span_index, span in enumerate(clause.get(field) or []):
                if not isinstance(span, Mapping):
                    dropped.append(f"clauses[{clause_index}].{field}[{span_index}]")
                    continue
                start = span.get("start")
                end = span.get("end")
                if not isinstance(start, int) or isinstance(start, bool):
                    dropped.append(f"clauses[{clause_index}].{field}[{span_index}]")
                    continue
                if not isinstance(end, int) or isinstance(end, bool):
                    dropped.append(f"clauses[{clause_index}].{field}[{span_index}]")
                    continue
                if not (0 <= start < end <= len(source_text)):
                    dropped.append(f"clauses[{clause_index}].{field}[{span_index}]")
                    continue
                text = source_text[start:end]
                if not text.strip():
                    dropped.append(f"clauses[{clause_index}].{field}[{span_index}]")
                    continue
                target.append(text)
                span_id = span.get("id")
                id_map[span_id] = text
                if field == "actions":
                    action_elements.append({
                        "action_id": str(span_id or f"{clause_id}.action.{len(action_elements) + 1}"),
                        "text": text,
                        "start": int(start),
                        "end": int(end),
                        "clause_id": clause_id,
                    })

        for link_index, link in enumerate(clause.get("actor_action_map") or []):
            if not isinstance(link, Mapping):
                dropped.append(f"clauses[{clause_index}].actor_action_map[{link_index}]")
                continue
            actor = actor_by_id.get(link.get("actor_id"))
            action = action_by_id.get(link.get("action_id"))
            if actor and action:
                actor_action_pairs.append({"actor": actor, "action": action})

    action_lookup = {item["action_id"]: item["text"] for item in action_elements}
    native_relations = normalize_native_order_relations(record, action_lookup)
    if order_adapter is not None:
        projection_result = order_adapter.project(
            source_text,
            record,
            nlp=nlp,
            rule_id=str(rule_id),
            action_elements=action_elements,
            native_relations=native_relations,
        )
    else:
        projection_result = projection.project(
            source_text,
            record,
            nlp=nlp,
            rule_id=str(rule_id),
            action_elements=action_elements,
            native_relations=native_relations,
        )
    order_relations = [
        [edge["before_text"], edge["after_text"]]
        for edge in projection_result.get("edges") or []
        if edge.get("before_text") and edge.get("after_text")
    ]

    return {
        "rule_id": str(rule_id),
        "actions": actions,
        "actors": actors,
        "actor_action_pairs": actor_action_pairs,
        "order_relations": order_relations,
        "failed": False,
        "failure_reasons": dropped,
        "conversion_audit": {
            "schema_version": SCHEMA_VERSION,
            "included_clauses": included_clauses,
            "dropped_spans": dropped,
            "native_order_relation_count": len(native_relations),
            "order_projection": projection_result,
        },
    }


__all__ = [
    "SCHEMA_VERSION",
    "RuleRecordConversionError",
    "canonical_to_rule_record_v2",
]
