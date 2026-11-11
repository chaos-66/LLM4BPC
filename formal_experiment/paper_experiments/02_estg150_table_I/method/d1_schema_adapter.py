"""D1 relay-schema adapter (D1-R1, 2026-08-05).

The deepseek-v4-pro model occasionally returns spans in nested per-field
containers (``actors=[{actor_id, name, span:{start,end,text}}]``,
``actions=[{action_id, verb, span, object}]``).  This module maps that
format back to the canonical ``{id, text, start, end, normalized}`` spans
DETERMINISTICALLY:

* a span container with flat ``text``/``start``/``end`` passes through;
* a span container with a nested ``span`` mapping is unfolded;
* empty ``normalized`` is filled with ``" ".join(text.casefold().split())``;
* a missing deterministic ``id`` is assigned ``<clause_id>.<field>.<rank>``;
* per user decision 2026-08-05 (empty is legal; bad elements must not kill a
  record), a span that cannot be mapped (missing/non-object container,
  non-integer offsets, text not in source) is DROPPED from its array and the
  record survives; every drop is recorded in the audit;
* only record-level structural violations (record not an object, empty
  source text, ``clauses`` not a list, non-object clause or modality) still
  fail closed.
"""

from __future__ import annotations

import copy
from typing import Any, Mapping

STATUS_UNCHANGED = "unchanged"
STATUS_ADAPTED = "adapted"
STATUS_DEGRADED = "degraded"
STATUS_FAILED = "failed"

FIELD_TO_PLURAL = {
    "actor": "actors",
    "action": "actions",
    "condition": "conditions",
    "constraint": "constraints",
    "exception": "exceptions",
}

MODEL_ID_KEYS = {
    "actors": ("actor_id", "id"),
    "actions": ("action_id", "id"),
    "conditions": ("condition_id", "id"),
    "constraints": ("constraint_id", "id"),
    "exceptions": ("exception_id", "id"),
}


def _is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _coerce_offset(value: Any) -> int | None:
    """Deterministic int coercion: ints pass; int-coercible numeric strings
    (e.g. ``"52"``) convert; anything else fails."""
    if _is_plain_int(value):
        return value
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value)
    return None


def _normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def _unfold_span(container: Any, label: str) -> tuple[dict[str, Any] | None, str | None]:
    """Return (canonical span dict, None) or (None, reason)."""
    if not isinstance(container, Mapping):
        return None, f"{label}_not_object"
    text = container.get("text")
    start = _coerce_offset(container.get("start"))
    end = _coerce_offset(container.get("end"))
    if isinstance(text, str) and text and start is not None and end is not None:
        return {
            "text": text,
            "start": start,
            "end": end,
            "normalized": _normalized(text),
        }, None
    nested = container.get("span")
    if isinstance(nested, Mapping):
        return _unfold_span(nested, f"{label}.span")
    return None, f"{label}_no_flat_or_nested_span"


def _adapt_field_spans(
    clause: Mapping[str, Any],
    field: str,
    source_text: str,
    dropped: list[str],
) -> list[dict[str, Any]]:
    plural = FIELD_TO_PLURAL[field]
    spans = clause.get(plural)
    if spans is None:
        return []
    if not isinstance(spans, list):
        dropped.append(f"clauses[].{plural}_not_list")
        return []
    out: list[dict[str, Any]] = []
    for index, item in enumerate(spans):
        span, reason = _unfold_span(item, f"{plural}[{index}]")
        if reason is not None:
            dropped.append(reason)
            continue
        if span["text"] not in source_text:
            dropped.append(f"{plural}[{index}]_text_not_in_source")
            continue
        span = dict(span)
        id_keys = MODEL_ID_KEYS[plural]
        span_id = next((item[k] for k in id_keys if isinstance(item.get(k), str) and item[k]), None)
        if span_id:
            span["id"] = span_id
        else:
            span["id"] = f"{clause.get('clause_id', 'clause')}.{field}.{index + 1}"
        out.append(span)
    return out


def adapt_relay_record(record: Any, source_text: Any) -> tuple[Any, dict[str, Any]]:
    """Map a relay-format direct-LLM record to the canonical shape.

    Returns ``(adapted_record, audit)``; on failure the original record is
    returned unchanged with ``audit["status"] == "failed"`` and stable
    reasons.
    """
    audit: dict[str, Any] = {
        "attempted": True,
        "status": STATUS_UNCHANGED,
        "spans_adapted": 0,
        "dropped_spans": [],
        "failed_reasons": [],
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
    if not isinstance(clauses, list):
        audit["status"] = STATUS_FAILED
        audit["failed_reasons"].append("clauses_not_list")
        return record, audit

    for ci, clause in enumerate(clauses):
        if not isinstance(clause, Mapping):
            audit["status"] = STATUS_FAILED
            audit["failed_reasons"].append(f"clauses[{ci}]_not_object")
            return record, audit
        for field in FIELD_TO_PLURAL:
            adapted = _adapt_field_spans(clause, field, source_text, audit["dropped_spans"])
            clause[FIELD_TO_PLURAL[field]] = adapted
            audit["spans_adapted"] += len(adapted)
        modality = clause.get("modality")
        if modality is not None and not isinstance(modality, Mapping):
            audit["status"] = STATUS_FAILED
            audit["failed_reasons"].append(f"clauses[{ci}]_modality_not_object")
            return record, audit

    if audit["dropped_spans"]:
        audit["status"] = STATUS_DEGRADED
    else:
        audit["status"] = STATUS_ADAPTED if audit["spans_adapted"] else STATUS_UNCHANGED
    return out, audit
