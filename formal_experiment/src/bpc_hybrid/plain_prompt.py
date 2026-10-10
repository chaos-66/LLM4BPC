"""Attach experiment metadata to plain model output, without changing spans.

The model produces semantic clauses and readable uncertainty reasons only.
Record identity, method/version metadata, and validation belong to the runner.
Historical prompts and their response processing do not use this adapter.
"""

from __future__ import annotations

from copy import deepcopy

from bpc_hybrid.stage2_canonical import SCHEMA_SOURCE, SCHEMA_VERSION


PLAIN_PROMPT_NAME = "plain_v1/direct_llm_plain_record_prompt_v1"
READABLE_REASONS = {
    "unresolved reference": (
        "reference_status=unresolved_coreference;independence_status=context_required"
    ),
    "ambiguous scope": "semantic_scope_ambiguous_in_target",
    "ambiguous clause boundary": "clause_boundary_ambiguous",
    "context required": "context_required",
}


def prepare_plain_prediction(
    payload: dict, *, sample_id: str, source_text: str
) -> dict:
    """Bind a plain response to its input and add internal metadata.

    Reject malformed envelopes and unknown reasons. This function does not
    infer, repair, remove, or relabel any semantic span or relation. The usual
    downstream adapter and validator still check the resulting record.
    """
    if not isinstance(payload, dict) or set(payload) != {
        "clauses", "unsupported_or_ambiguous"
    }:
        raise ValueError("expected only clauses and unsupported_or_ambiguous")
    if not isinstance(payload["clauses"], list):
        raise ValueError("clauses must be an array")
    if not isinstance(payload["unsupported_or_ambiguous"], list):
        raise ValueError("unsupported_or_ambiguous must be an array")

    record = deepcopy(payload)
    for entry in record["unsupported_or_ambiguous"]:
        if not isinstance(entry, dict) or set(entry) != {"field", "reason"}:
            raise ValueError("uncertainty entries require only field and reason")
        reason = entry["reason"]
        if not isinstance(reason, str) or reason not in READABLE_REASONS:
            raise ValueError("unknown uncertainty reason")
        entry["reason"] = READABLE_REASONS[reason]

    record.update({
        "schema_version": SCHEMA_VERSION,
        "sample_id": sample_id,
        "source_id": sample_id,
        "source_text": source_text,
        "method": {"name": "direct_llm", "schema_source": SCHEMA_SOURCE},
        # The validator replaces this placeholder with its actual result.
        "validation": {
            "schema_valid": False,
            "cross_field_valid": False,
            "errors": ["Not yet validated"],
        },
    })
    return record
