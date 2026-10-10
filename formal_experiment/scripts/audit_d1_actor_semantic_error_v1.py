# -*- coding: utf-8 -*-
"""Read-only Actor semantic error audit for the fixed D-full-0813 run.

This script performs Phase B of the 2026-09 D1 Actor audit:

* no LLM/API calls;
* no Prompt changes;
* no Gold changes;
* no prediction changes;
* no actor-semantic repair.

It inventories every Actor TP/FP/FN under the promoted ``repair_v1``
canonicalizer, audits cross-field projection at character-span level, and
records prompt-rule / factorial evidence links for later research design.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for _path in (SRC, SCRIPTS):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from bpc_hybrid.d1_span_canonicalizer import (  # noqa: E402
    DEFAULT_POLICY,
    POLICY_REPAIR,
)
from bpc_hybrid.stage2_sun_literal_overlap import (  # noqa: E402
    evaluate_sun_literal_overlap,
)
import run_barrientos_ablation_suite_v2 as runner  # noqa: E402
import run_d_span_grounding_repair_v1 as grounding  # noqa: E402

PREDICTION_PATH = (
    ROOT / "outputs/development/d_span_grounding_repair_v1/new/"
    "canonical_predictions.jsonl"
)
REPORT_JSON = ROOT / "outputs/reports/d1_actor_semantic_error_audit_v1.json"
REPORT_MD = ROOT / "outputs/reports/d1_actor_semantic_error_audit_v1.md"
FACTORIAL_DIR = ROOT / "outputs/development/d1_prompt_factorial_ablation_v2"
FULL_DIR = (
    ROOT / "outputs/development/barrientos_ablation_suite_v2/"
    "D-full-0813/repeat-01"
)
FACTORIAL_ARMS = (
    "D-full-0813",
    "D-no-semantic-examples-0813",
    "D-no-semantic-guidance-0813",
    "D-no-explicit-json-contract-0813",
)
RULES_ONLY_PATH = ROOT / "data/predictions/b0_formal_arm_v1/predictions.json"

SPAN_FIELDS = ("actors", "actions", "conditions", "constraints", "exceptions")
FIELD_LABEL = {
    "actors": "actor",
    "actions": "action",
    "conditions": "condition",
    "constraints": "constraint",
    "exceptions": "exception",
    "modality.evidence": "modality",
}
PRONOUNS = frozenset({
    "it", "they", "this", "these", "such", "that", "those", "them",
    "he", "she", "we", "you", "i", "its", "their", "his", "her",
})
PROMPT_PRONOUNS = frozenset({"it", "they", "this", "these", "such"})
LEGAL_ROLE_INDICATORS = (
    "taxpayer", "employee", "employer", "recipient", "beneficiary",
    "bank", "authority", "controller", "processor", "applicant",
    "shareholder", "owner", "spouse", "child", "insured person",
    "persons with limited tax liability", "building society",
    "municipality", "tax office",
)
OBJECT_HEAD_MARKERS = (
    "agreement", "contribution", "fund", "list", "building", "period",
    "allowance", "contract", "commitment", "share", "amount", "tax",
    "income", "profit", "difference", "value", "benefit", "entitlement",
    "expense", "outlay", "transfer", "reserve", "gain", "security",
    "section", "item", "subsection", "following", "cost", "payment",
    "statement", "balance", "asset", "liability", "order", "claim",
    "application", "insurance", "pension",
)
_OBJECT_HEAD_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(word) + "s?" for word in OBJECT_HEAD_MARKERS) + r")\b")
FN_LABELS = {
    "FN-A": "ABSENT_FROM_ALL_MODEL_SEMANTIC_SPANS",
    "FN-B": "EMBEDDED_IN_CONDITION",
    "FN-C": "EMBEDDED_IN_CONSTRAINT",
    "FN-D": "EMBEDDED_IN_ACTION",
    "FN-E": "EMBEDDED_IN_EXCEPTION",
    "FN-F": "WRONG_ACTOR_BOUNDARY",
    "FN-G": "DUPLICATE_OCCURRENCE_COVERAGE",
    "FN-H": "CLAUSE_SEGMENTATION_SCOPE",
    "FN-I": "OTHER",
}
FP_LABELS = {
    "FP-A": "PRONOUN_DEMONSTRATIVE",
    "FP-B": "NON_ROLE_GRAMMATICAL_SUBJECT",
    "FP-C": "LEGAL_NORMATIVE_ROLE_BUT_GOLD_UNANNOTATED",
    "FP-D": "WRONG_OCCURRENCE_DUPLICATE",
    "FP-E": "OVERLONG_UNDER_SPECIFIC_ACTOR_SPAN",
    "FP-F": "CLAUSE_SCOPE_ERROR",
    "FP-G": "OTHER",
}


class ActorAuditError(ValueError):
    """Fail-closed audit input error."""


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ActorAuditError(f"missing JSONL artifact: {path}")
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ActorAuditError(f"JSONL row is not an object: {path}")
            rows.append(value)
    return rows


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ActorAuditError(f"expected JSON object: {path}")
    return value


def _norm_text(text: Any) -> str:
    return " ".join(str(text or "").casefold().split())


def _clause_span(clause: Mapping[str, Any]) -> Mapping[str, Any] | None:
    span = clause.get("clause_span")
    return span if isinstance(span, Mapping) else None


def _valid_span(span: Mapping[str, Any]) -> bool:
    start, end = span.get("start"), span.get("end")
    return (
        isinstance(start, int) and not isinstance(start, bool)
        and isinstance(end, int) and not isinstance(end, bool)
        and 0 <= start < end
    )


def _intersects(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    if not _valid_span(left) or not _valid_span(right):
        return False
    return max(int(left["start"]), int(right["start"])) < min(
        int(left["end"]), int(right["end"]))


def _contains(container: Mapping[str, Any], inner: Mapping[str, Any]) -> bool:
    if not _valid_span(container) or not _valid_span(inner):
        return False
    return (
        int(container["start"]) <= int(inner["start"])
        and int(inner["end"]) <= int(container["end"])
    )


def _relation(left: Mapping[str, Any], right: Mapping[str, Any]) -> str:
    if not _intersects(left, right):
        return "none"
    if _contains(left, right):
        return "left_contains_right"
    if _contains(right, left):
        return "right_contains_left"
    return "partial_overlap"


def _span_record(span: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": span.get("id"),
        "text": span.get("text"),
        "normalized": span.get("normalized"),
        "start": span.get("start"),
        "end": span.get("end"),
        "coordinates": [span.get("start"), span.get("end")],
    }


def _record_semantic_spans(
    record: Mapping[str, Any],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for clause_index, clause in enumerate(record.get("clauses") or []):
        if not isinstance(clause, Mapping):
            continue
        clause_ctx = {
            "clause_index": clause_index,
            "clause_id": clause.get("clause_id"),
            "clause_span": _span_record(_clause_span(clause) or {}),
        }
        for field in SPAN_FIELDS:
            for span_index, span in enumerate(clause.get(field) or []):
                if isinstance(span, Mapping):
                    out.append({
                        "field": field,
                        "field_label": FIELD_LABEL[field],
                        "span_index": span_index,
                        "clause": clause_ctx,
                        "span": _span_record(span),
                    })
        modality = clause.get("modality")
        if isinstance(modality, Mapping):
            for span_index, span in enumerate(modality.get("evidence") or []):
                if isinstance(span, Mapping):
                    out.append({
                        "field": "modality.evidence",
                        "field_label": "modality",
                        "span_index": span_index,
                        "clause": clause_ctx,
                        "span": _span_record(span),
                    })
    return out


def _flatten_field(record: Mapping[str, Any], field: str) -> list[dict[str, Any]]:
    return [
        item["span"]
        for item in _record_semantic_spans(record)
        if item["field"] == field
    ]


def _span_overlap_any(gold_span: Mapping[str, Any],
                      spans: Sequence[Mapping[str, Any]]) -> bool:
    return any(_intersects(gold_span, span) for span in spans)


def _clause_containing(record: Mapping[str, Any],
                       span: Mapping[str, Any]) -> dict[str, Any] | None:
    clauses = record.get("clauses") or []
    for index, clause in enumerate(clauses):
        if not isinstance(clause, Mapping):
            continue
        cs = _clause_span(clause)
        if cs is not None and _contains(cs, span):
            return {"clause_index": index, "clause_id": clause.get("clause_id"),
                    "clause_span": _span_record(cs)}
    for index, clause in enumerate(clauses):
        if not isinstance(clause, Mapping):
            continue
        cs = _clause_span(clause)
        if cs is not None and _intersects(cs, span):
            return {"clause_index": index, "clause_id": clause.get("clause_id"),
                    "clause_span": _span_record(cs)}
    return None


def _is_pronoun(text: str) -> bool:
    return _norm_text(text) in PRONOUNS


def _is_prompt_pronoun(text: str) -> bool:
    return _norm_text(text) in PROMPT_PRONOUNS


def _looks_like_legal_role(text: str) -> bool:
    normalized = _norm_text(text)
    if not normalized:
        return False
    if "building society" in normalized:
        return True
    if "limited tax liability" in normalized:
        return True
    if not any(term in normalized for term in LEGAL_ROLE_INDICATORS):
        return False
    # If the phrase is clearly an object/quantity/temporal span, do not turn
    # it into a legal-role candidate merely because a role word is embedded.
    return not bool(_OBJECT_HEAD_RE.search(normalized))


def _looks_like_non_role_subject(text: str) -> bool:
    return bool(_norm_text(text))


def _gold_actor_cases(gold_record: Mapping[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for clause_index, clause in enumerate(gold_record.get("clauses") or []):
        if not isinstance(clause, Mapping):
            continue
        clause_ctx = {
            "clause_index": clause_index,
            "clause_id": clause.get("clause_id"),
            "clause_span": _span_record(_clause_span(clause) or {}),
        }
        for span_index, span in enumerate(clause.get("actors") or []):
            if isinstance(span, Mapping):
                out.append({
                    "field": "actor",
                    "span_index": span_index,
                    "clause": clause_ctx,
                    "span": _span_record(span),
                })
    return out


def _pred_actor_cases(pred_record: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        item for item in _record_semantic_spans(pred_record)
        if item["field"] == "actors"
    ]


def _overlap_details(
    gold_span: Mapping[str, Any],
    record: Mapping[str, Any],
    *,
    include_actors: bool = False,
) -> dict[str, list[dict[str, Any]]]:
    fields = [
        "conditions", "constraints", "actions", "exceptions",
        "modality.evidence",
    ]
    if include_actors:
        fields.insert(0, "actors")
    details: dict[str, list[dict[str, Any]]] = {FIELD_LABEL[f]: [] for f in fields}
    for item in _record_semantic_spans(record):
        if item["field"] not in fields:
            continue
        relation = _relation(gold_span, item["span"])
        if relation == "none":
            continue
        details[FIELD_LABEL[item["field"]]].append({
            "relation": relation,
            "predicted_span": item["span"],
            "clause": item["clause"],
        })
    return details


def _has_cross_field_overlap(details: Mapping[str, Sequence[Any]]) -> bool:
    return any(
        bool(details.get(field))
        for field in ("condition", "constraint", "action", "exception", "modality")
    )


def classify_fn_case(
    *,
    sample_id: str,
    gold_record: Mapping[str, Any],
    pred_record: Mapping[str, Any],
    source_text: str,
    gold_actor: Mapping[str, Any],
) -> dict[str, Any]:
    """Classify one Gold Actor that has no overlapping predicted actor."""
    gold_span = gold_actor
    gold_case = {
        "sample_id": sample_id,
        "field": "actor",
        "gold_actor": _span_record(gold_span),
        "gold_span": [gold_span.get("start"), gold_span.get("end")],
        "coordinates": [gold_span.get("start"), gold_span.get("end")],
        "text": gold_span.get("text"),
        "source_text": source_text,
        "gold_clause": _clause_containing(gold_record, gold_span),
    }
    pred_actors = [item["span"] for item in _pred_actor_cases(pred_record)]
    same_surface = [
        span for span in pred_actors
        if _norm_text(span.get("text")) == _norm_text(gold_span.get("text"))
    ]
    boundary_candidates = [
        span for span in pred_actors
        if span not in same_surface
        and _norm_text(span.get("text"))
        and (
            _norm_text(span.get("text")) in _norm_text(gold_span.get("text"))
            or _norm_text(gold_span.get("text")) in _norm_text(span.get("text"))
        )
    ]
    details = _overlap_details(gold_span, pred_record, include_actors=False)
    actor_overlap = any(_intersects(gold_span, p) for p in pred_actors)
    condition_overlap = bool(details.get("condition"))
    constraint_overlap = bool(details.get("constraint"))
    action_overlap = bool(details.get("action"))
    exception_overlap = bool(details.get("exception"))
    modality_overlap = bool(details.get("modality"))
    cross_field_present = any((
        condition_overlap, constraint_overlap, action_overlap,
        exception_overlap, modality_overlap,
    ))
    predicted_clause_windows = [
        _clause_span(clause)
        for clause in pred_record.get("clauses") or []
        if isinstance(clause, Mapping) and _clause_span(clause) is not None
    ]
    clause_scope_miss = not any(
        _intersects(gold_span, cs) for cs in predicted_clause_windows
        if isinstance(cs, Mapping)
    )
    if same_surface:
        taxonomy = "FN-G_DUPLICATE_OCCURRENCE_COVERAGE"
        basis = (
            "A predicted actor span with the same normalized surface exists "
            "elsewhere in the record but does not overlap this Gold occurrence."
        )
        confidence = "high"
    elif boundary_candidates:
        taxonomy = "FN-F_WRONG_ACTOR_BOUNDARY"
        basis = (
            "A non-overlapping predicted actor surface is a normalized "
            "containment partner of the Gold surface; exact overlap must be "
            "reviewed before treating it as a true semantic omission."
        )
        confidence = "needs_review"
    elif condition_overlap:
        taxonomy = "FN-B_EMBEDDED_IN_CONDITION"
        basis = "Character-span overlap with a predicted condition span: " + _relation_summary(details["condition"])
        confidence = "high" if any(x["relation"] == "right_contains_left" for x in details["condition"]) else "medium"
    elif constraint_overlap:
        taxonomy = "FN-C_EMBEDDED_IN_CONSTRAINT"
        basis = "Character-span overlap with a predicted constraint span: " + _relation_summary(details["constraint"])
        confidence = "high" if any(x["relation"] == "right_contains_left" for x in details["constraint"]) else "medium"
    elif action_overlap:
        taxonomy = "FN-D_EMBEDDED_IN_ACTION"
        basis = "Character-span overlap with a predicted action span: " + _relation_summary(details["action"])
        confidence = "high" if any(x["relation"] == "right_contains_left" for x in details["action"]) else "medium"
    elif exception_overlap:
        taxonomy = "FN-E_EMBEDDED_IN_EXCEPTION"
        basis = "Character-span overlap with a predicted exception span: " + _relation_summary(details["exception"])
        confidence = "high" if any(x["relation"] == "right_contains_left" for x in details["exception"]) else "medium"
    elif modality_overlap:
        taxonomy = "FN-I_OTHER"
        basis = "Character-span overlap with predicted modality evidence only."
        confidence = "medium"
    elif clause_scope_miss:
        taxonomy = "FN-H_CLAUSE_SEGMENTATION_SCOPE"
        basis = "No predicted clause span intersects the Gold actor span."
        confidence = "medium"
    elif not cross_field_present and not actor_overlap:
        taxonomy = "FN-A_ABSENT_FROM_ALL_MODEL_SEMANTIC_SPANS"
        basis = "No emitted semantic span (actor or other field) intersects the Gold actor span."
        confidence = "deterministic"
    else:
        taxonomy = "FN-I_OTHER"
        basis = "No taxonomy rule matched; manual review required."
        confidence = "needs_review"
    return {
        **gold_case,
        "taxonomy": taxonomy,
        "classification_basis": basis,
        "confidence": confidence,
        "actor_overlap": actor_overlap,
        "condition_overlap": condition_overlap,
        "constraint_overlap": constraint_overlap,
        "action_overlap": action_overlap,
        "exception_overlap": exception_overlap,
        "modality_overlap": modality_overlap,
        "cross_field_overlap": cross_field_present,
        "clause_scope_miss": clause_scope_miss,
        "same_surface_predicted_elsewhere": bool(same_surface),
        "same_surface_predicted_actor_spans": [_span_record(x) for x in same_surface],
        "boundary_candidate_actor_spans": [_span_record(x) for x in boundary_candidates],
        "overlap_details": details,
    }


def _relation_summary(rows: Sequence[Mapping[str, Any]]) -> str:
    return ", ".join(sorted({str(row.get("relation")) for row in rows}))


def classify_fp_case(
    *,
    sample_id: str,
    gold_record: Mapping[str, Any],
    pred_record: Mapping[str, Any],
    source_text: str,
    pred_actor: Mapping[str, Any],
) -> dict[str, Any]:
    text = _norm_text(pred_actor.get("text"))
    gold_actors = [item["span"] for item in _gold_actor_cases(gold_record)]
    same_surface_gold = [
        gold for gold in gold_actors
        if _norm_text(gold.get("text")) == text
    ]
    clause_scope_miss = False
    predicted_clause = _clause_containing(pred_record, pred_actor)
    if predicted_clause is not None:
        cs = predicted_clause.get("clause_span") or {}
        clause_scope_miss = not any(
            _intersects(cs, _clause_span(clause) or {})
            for clause in gold_record.get("clauses") or []
            if isinstance(clause, Mapping)
        )
    if same_surface_gold:
        taxonomy = "FP-D_WRONG_OCCURRENCE_DUPLICATE"
        basis = "Same normalized surface as a Gold actor elsewhere in the record, but zero character overlap with any Gold actor."
        confidence = "high"
        appears = "Same actor surface as a Gold annotation, at a different occurrence."
        gold_review = False
    elif _is_pronoun(text):
        taxonomy = "FP-A_PRONOUN_DEMONSTRATIVE"
        basis = "Predicted actor surface is an exact pronoun/demonstrative."
        confidence = "deterministic"
        appears = "Subject pronoun/demonstrative emitted as an actor mention."
        gold_review = False
    elif _looks_like_legal_role(text):
        taxonomy = "FP-C_LEGAL_NORMATIVE_ROLE_BUT_GOLD_UNANNOTATED"
        basis = "Predicted actor surface has a legal/normative role head but no overlapping Gold actor annotation."
        confidence = "medium"
        appears = "Legal/normative role-like noun phrase with no benchmark Gold actor annotation in this statement."
        gold_review = True
    elif _looks_like_non_role_subject(text):
        taxonomy = "FP-B_NON_ROLE_GRAMMATICAL_SUBJECT"
        basis = "Predicted actor surface is a non-pronominal grammatical subject/noun phrase with no legal-role head in the current actor ontology."
        confidence = "medium"
        appears = "Grammatical subject/noun phrase accepted as actor although the benchmark Gold does not annotate it as actor here."
        gold_review = False
    elif clause_scope_miss:
        taxonomy = "FP-F_CLAUSE_SCOPE_ERROR"
        basis = "Predicted actor clause span does not overlap any Gold clause span."
        confidence = "medium"
        appears = "Actor-like mention in a clause that is not aligned with the benchmark clause segmentation."
        gold_review = False
    else:
        taxonomy = "FP-G_OTHER"
        basis = "No automated taxonomy rule matched; manual review required."
        confidence = "needs_review"
        appears = "Unclassified actor-like prediction."
        gold_review = False
    return {
        "sample_id": sample_id,
        "field": "actor",
        "predicted_actor": _span_record(pred_actor),
        "pred_span": [pred_actor.get("start"), pred_actor.get("end")],
        "coordinates": [pred_actor.get("start"), pred_actor.get("end")],
        "text": pred_actor.get("text"),
        "source_text": source_text,
        "predicted_clause": predicted_clause,
        "gold_actors_in_record": [_span_record(g) for g in gold_actors],
        "gold_overlap": False,
        "taxonomy": taxonomy,
        "classification_basis": basis,
        "confidence": confidence,
        "same_surface_as_gold_actor_elsewhere": bool(same_surface_gold),
        "gold_review_candidate": gold_review,
        "why_prediction_appears_actor_like": appears,
    }


def build_actor_inventory(
    predictions: Sequence[Mapping[str, Any]],
    gold_by_id: Mapping[str, Mapping[str, Any]],
    source_by_id: Mapping[str, str],
) -> dict[str, Any]:
    """Build TP/FP/FN cases without mutating any input object."""
    prediction_by_id = {str(row.get("sample_id")): row for row in predictions}
    if set(prediction_by_id) != set(gold_by_id):
        raise ActorAuditError("prediction/Gold membership mismatch")
    attempts = [
        {
            "sample_id": sid,
            "request_status": row.get("request_status"),
            "record": row.get("record") or {},
        }
        for sid, row in prediction_by_id.items()
    ]
    metrics = evaluate_sun_literal_overlap(
        list(gold_by_id.values()), attempts,
        dataset_id="estg150_frozen_D_full_0813",
        method_id="direct_llm_repair_v1",
    )["per_field"]["actor"]

    tp_cases: list[dict[str, Any]] = []
    fp_cases: list[dict[str, Any]] = []
    fn_cases: list[dict[str, Any]] = []
    tp_gold_cases: list[dict[str, Any]] = []
    for sid in sorted(gold_by_id):
        gold = gold_by_id[sid]
        pred = prediction_by_id[sid].get("record") or {}
        source_text = source_by_id.get(sid) or gold.get("source_text") or ""
        gold_actors = [item["span"] for item in _gold_actor_cases(gold)]
        pred_actors = [item["span"] for item in _pred_actor_cases(pred)]
        for gold_actor in gold_actors:
            matches = [p for p in pred_actors if _intersects(gold_actor, p)]
            if matches:
                tp_gold_cases.append({
                    "sample_id": sid,
                    "field": "actor",
                    "gold_actor": _span_record(gold_actor),
                    "matched_predicted_actors": [_span_record(p) for p in matches],
                    "source_text": source_text,
                    "gold_clause": _clause_containing(gold, gold_actor),
                })
            else:
                fn_cases.append(classify_fn_case(
                    sample_id=sid, gold_record=gold, pred_record=pred,
                    source_text=source_text, gold_actor=gold_actor))
        for pred_actor in pred_actors:
            matches = [g for g in gold_actors if _intersects(g, pred_actor)]
            if matches:
                tp_cases.append({
                    "sample_id": sid,
                    "field": "actor",
                    "predicted_actor": _span_record(pred_actor),
                    "matched_gold_actors": [_span_record(g) for g in matches],
                    "source_text": source_text,
                    "predicted_clause": _clause_containing(pred, pred_actor),
                    "surface_type": _classify_tp_surface(pred_actor),
                })
            else:
                fp_cases.append(classify_fp_case(
                    sample_id=sid, gold_record=gold, pred_record=pred,
                    source_text=source_text, pred_actor=pred_actor))
    if len(tp_cases) != int(metrics["matched_predictions"]):
        raise ActorAuditError("Actor TP case count does not match evaluator")
    if len(fp_cases) != int(metrics["extracted"] - metrics["matched_predictions"]):
        raise ActorAuditError("Actor FP case count does not match evaluator")
    if len(fn_cases) != int(metrics["ground_truth"] - metrics["matched_ground_truth"]):
        raise ActorAuditError("Actor FN case count does not match evaluator")
    # TP/FP counts are prediction-side; annotate the evaluator's recall-side count.
    return {
        "metrics": metrics,
        "tp_count": len(tp_cases),
        "fp_count": len(fp_cases),
        "fn_count": len(fn_cases),
        "matched_gold_count": len(tp_gold_cases),
        "tp_cases": tp_cases,
        "fp_cases": fp_cases,
        "fn_cases": fn_cases,
        "tp_gold_cases": tp_gold_cases,
    }


def _classify_tp_surface(span: Mapping[str, Any]) -> dict[str, Any]:
    text = _norm_text(span.get("text"))
    if _is_pronoun(text):
        return {"surface_type": "pronoun", "basis": "exact pronoun/demonstrative"}
    if any(w in text for w in ("office", "authority", "ministry", "court",
                               "municipality", "agency", "commission",
                               "government", "federal", "directorate")):
        return {"surface_type": "institution", "basis": "institution head lexicon"}
    if any(w in text for w in ("person", "employee", "taxpayer", "spouse",
                               "child", "recipient", "beneficiary", "owner",
                               "shareholder", "applicant", "individual")):
        return {"surface_type": "person/legal role", "basis": "person-role head lexicon"}
    if any(w in text for w in ("society", "bank", "fund", "company",
                               "association", "corporation")):
        return {"surface_type": "organization", "basis": "organization head lexicon"}
    if any(w in text for w in ("contribution", "income", "profit", "asset",
                               "value", "period", "amount", "cost", "expense",
                               "fund", "agreement", "list", "building")):
        return {"surface_type": "abstract/legal object", "basis": "object head lexicon"}
    return {"surface_type": "legal-role NP/other", "basis": "fallback surface heuristic"}


def _taxonomy_counts(cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts = Counter(str(case.get("taxonomy")) for case in cases)
    total = len(cases)
    return {
        "counts": dict(sorted(counts.items())),
        "shares": {
            key: (value / total if total else None)
            for key, value in sorted(counts.items())
        },
        "total": total,
        "labels": {**FN_LABELS, **FP_LABELS},
    }


def _pronoun_analysis(inventory: Mapping[str, Any]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    for case in inventory["tp_cases"] + inventory["fp_cases"]:
        predicted = case.get("predicted_actor") or {}
        text = predicted.get("text")
        if not _is_pronoun(text):
            continue
        cases.append({
            "sample_id": case.get("sample_id"),
            "pronoun": text,
            "coordinates": predicted.get("coordinates"),
            "gold_overlap": bool(case.get("matched_gold_actors")),
            "tp_fp": "TP" if case.get("matched_gold_actors") else "FP",
            "clause_context": case.get("predicted_clause"),
            "source_text": case.get("source_text"),
            "taxonomy": case.get("taxonomy"),
        })
    total = len(cases)
    tp = sum(1 for case in cases if case["tp_fp"] == "TP")
    fp = total - tp
    return {
        "total": total,
        "tp": tp,
        "fp": fp,
        "precision": (tp / total if total else None),
        "prompt_pronoun_total": sum(
            1 for case in cases if _is_prompt_pronoun(case.get("pronoun"))),
        "prompt_pronoun_tp": sum(
            1 for case in cases
            if _is_prompt_pronoun(case.get("pronoun")) and case["tp_fp"] == "TP"),
        "prompt_pronoun_fp": sum(
            1 for case in cases
            if _is_prompt_pronoun(case.get("pronoun")) and case["tp_fp"] == "FP"),
        "surface_distribution": dict(sorted(Counter(
            str(case.get("pronoun")) for case in cases).items())),
        "cases": cases,
    }


def _tp_surface_audit(inventory: Mapping[str, Any]) -> dict[str, Any]:
    counts = Counter()
    rows: list[dict[str, Any]] = []
    for case in inventory["tp_cases"]:
        surface = case.get("surface_type") or _classify_tp_surface(
            case.get("predicted_actor") or {})
        counts[surface["surface_type"]] += 1
        rows.append({
            "sample_id": case.get("sample_id"),
            "predicted_actor": case.get("predicted_actor"),
            "matched_gold_actors": case.get("matched_gold_actors"),
            "surface_type": surface,
            "source_text": case.get("source_text"),
        })
    return {
        "surface_type_counts": dict(sorted(counts.items())),
        "cases": rows,
    }


def _prompt_metadata() -> dict[str, Any]:
    prompt_path = runner._prompt_for("D-full-0813")
    text = prompt_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    rules: list[dict[str, Any]] = []
    for start, end in ((56, 61), (82, 85), (85, 89), (145, 183)):
        snippet = "\n".join(lines[start - 1:end])
        rules.append({
            "line_start": start,
            "line_end": end,
            "text": snippet,
        })
    return {
        "path": str(prompt_path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": _sha256_file(prompt_path),
        "rules": rules,
    }


def _predictions_for_arm(arm: str) -> list[dict[str, Any]]:
    if arm == "D-full-0813":
        path = FULL_DIR / "canonical_predictions.jsonl"
    else:
        path = FACTORIAL_DIR / arm / "repeat-01/canonical_predictions.jsonl"
    return _load_jsonl(path)


def _actor_occurrences(
    predictions: Sequence[Mapping[str, Any]],
    gold_by_id: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in predictions:
        sid = str(row.get("sample_id"))
        gold = gold_by_id.get(sid) or {}
        gold_actors = [item["span"] for item in _gold_actor_cases(gold)]
        record = row.get("record") or {}
        for item in _pred_actor_cases(record):
            span = item["span"]
            out.append({
                "sample_id": sid,
                "text": span.get("text"),
                "normalized": _norm_text(span.get("text")),
                "start": span.get("start"),
                "end": span.get("end"),
                "tp": any(_intersects(g, span) for g in gold_actors),
            })
    return out


def _actor_metrics_for_rows(
    predictions: Sequence[Mapping[str, Any]],
    gold_by_id: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    attempts = [
        {"sample_id": row.get("sample_id"),
         "request_status": row.get("request_status"),
         "record": row.get("record") or {}}
        for row in predictions
    ]
    return evaluate_sun_literal_overlap(
        list(gold_by_id.values()), attempts,
        dataset_id="estg150_frozen_D_full_0813",
        method_id="actor_factorial_delta",
    )["per_field"]["actor"]


def _factorial_actor_delta(
    gold_by_id: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    occurrences: dict[str, list[dict[str, Any]]] = {}
    for arm in FACTORIAL_ARMS:
        rows = _predictions_for_arm(arm)
        metrics[arm] = _actor_metrics_for_rows(rows, gold_by_id)
        occurrences[arm] = _actor_occurrences(rows, gold_by_id)

    full = occurrences["D-full-0813"]
    ng = occurrences["D-no-semantic-guidance-0813"]
    full_counts: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"count": 0, "tp": 0, "fp": 0})
    ng_counts: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"count": 0, "tp": 0, "fp": 0})
    for event in full:
        row = full_counts[(event["sample_id"], event["normalized"])]
        row["count"] += 1
        row["tp" if event["tp"] else "fp"] += 1
    for event in ng:
        row = ng_counts[(event["sample_id"], event["normalized"])]
        row["count"] += 1
        row["tp" if event["tp"] else "fp"] += 1

    lost: list[dict[str, Any]] = []
    gained: list[dict[str, Any]] = []
    for key in sorted(set(full_counts) | set(ng_counts)):
        sid, surface = key
        full_row = full_counts.get(key, {"count": 0, "tp": 0, "fp": 0})
        ng_row = ng_counts.get(key, {"count": 0, "tp": 0, "fp": 0})
        if full_row["count"] > ng_row["count"]:
            lost.append({
                "sample_id": sid,
                "surface": surface,
                "full_count": full_row["count"],
                "no_guidance_count": ng_row["count"],
                "delta": ng_row["count"] - full_row["count"],
                "full_tp_count": full_row["tp"],
                "full_fp_count": full_row["fp"],
                "interpretation": (
                    "harmful_loss" if full_row["tp"] else "beneficial_removal"
                    if full_row["fp"] and not full_row["tp"] else "mixed_or_unclear"
                ),
            })
        if ng_row["count"] > full_row["count"]:
            gained.append({
                "sample_id": sid,
                "surface": surface,
                "full_count": full_row["count"],
                "no_guidance_count": ng_row["count"],
                "delta": ng_row["count"] - full_row["count"],
                "no_guidance_tp_count": ng_row["tp"],
                "no_guidance_fp_count": ng_row["fp"],
                "interpretation": (
                    "beneficial_gain" if ng_row["tp"] and not ng_row["fp"]
                    else "harmful_gain" if ng_row["fp"] and not ng_row["tp"]
                    else "mixed_or_unclear"
                ),
            })

    full_metrics = metrics["D-full-0813"]
    ng_metrics = metrics["D-no-semantic-guidance-0813"]
    return {
        "basis": "frozen existing factorial canonical predictions; legacy canonicalizer policy; no new model calls",
        "arms": {
            arm: {
                "prediction_path": (
                    "outputs/development/barrientos_ablation_suite_v2/"
                    "D-full-0813/repeat-01/canonical_predictions.jsonl"
                    if arm == "D-full-0813" else
                    "outputs/development/d1_prompt_factorial_ablation_v2/"
                    f"{arm}/repeat-01/canonical_predictions.jsonl"
                ),
                "actor_metrics": metrics[arm],
            }
            for arm in FACTORIAL_ARMS
        },
        "full_to_no_guidance": {
            "full_actor_predictions_count": full_metrics["extracted"],
            "no_guidance_actor_predictions_count": ng_metrics["extracted"],
            "delta_prediction_count": ng_metrics["extracted"] - full_metrics["extracted"],
            "delta_matched_predictions_tp_side": (
                ng_metrics["matched_predictions"] - full_metrics["matched_predictions"]),
            "delta_fp": (
                (ng_metrics["extracted"] - ng_metrics["matched_predictions"])
                - (full_metrics["extracted"] - full_metrics["matched_predictions"])),
            "delta_matched_ground_truth_recall_side": (
                ng_metrics["matched_ground_truth"] - full_metrics["matched_ground_truth"]),
            "delta_fn": (
                (ng_metrics["ground_truth"] - ng_metrics["matched_ground_truth"])
                - (full_metrics["ground_truth"] - full_metrics["matched_ground_truth"])),
            "lost_surfaces": lost,
            "gained_surfaces": gained,
            "lost_surface_count": sum(row["full_count"] - row["no_guidance_count"] for row in lost),
            "gained_surface_count": sum(row["no_guidance_count"] - row["full_count"] for row in gained),
            "beneficial_removal_count": sum(
                row["full_fp_count"] - row["no_guidance_count"]
                for row in lost if row["full_tp_count"] == 0),
            "harmful_loss_count": sum(
                row["full_count"] - row["no_guidance_count"]
                for row in lost if row["full_tp_count"] > 0),
        },
    }


def _load_rules_only_by_id() -> dict[str, Mapping[str, Any]]:
    if not RULES_ONLY_PATH.is_file():
        return {}
    doc = _load_json(RULES_ONLY_PATH)
    return {row["sample_id"]: row for row in doc.get("records") or []}


def _rules_only_actor_overlap(
    rules_only: Mapping[str, Mapping[str, Any]],
    sample_id: str,
    span: Mapping[str, Any],
) -> bool:
    record = (rules_only.get(sample_id) or {}).get("record") or {}
    return any(
        _intersects(span, item["span"])
        for item in _pred_actor_cases(record)
    )


def _gold_review_candidates(
    inventory: Mapping[str, Any],
) -> list[dict[str, Any]]:
    rules_only = _load_rules_only_by_id()
    out: list[dict[str, Any]] = []
    for case in inventory["fp_cases"]:
        if not case.get("gold_review_candidate"):
            continue
        out.append({
            **case,
            "rules_only_behavior_post_hoc": {
                "available": bool(rules_only),
                "captured_by_any_char_overlap": _rules_only_actor_overlap(
                    rules_only, str(case["sample_id"]),
                    case["predicted_actor"]),
                "note": (
                    "Post-hoc method-difference observation only; not used to "
                    "modify LLM-SE."
                ),
            },
        })
    return out


def _rules_only_mechanism_comparison(
    inventory: Mapping[str, Any],
) -> dict[str, Any]:
    rules_only = _load_rules_only_by_id()
    post_hoc: list[dict[str, Any]] = []
    for case in inventory["fn_cases"]:
        sid = str(case["sample_id"])
        post_hoc.append({
            "sample_id": sid,
            "gold_actor": case["gold_actor"],
            "direct_llm_fn_taxonomy": case["taxonomy"],
            "rules_only_captured_by_any_char_overlap": (
                _rules_only_actor_overlap(
                    rules_only, sid, case["gold_actor"])),
        })
    return {
        "source_files": [
            "src/bpc_hybrid/b0_v10/actor_action.py",
            "docs/B0_R2_METHOD_CROSSWALK.md",
            "docs/B0_ERROR_ANALYSIS.md",
        ],
        "mechanism": {
            "candidate_generation": (
                "Dependency scan for nsubj/nsubj:pass, obl:agent/nmod:agent, "
                "and obl/nmod with by/to case; candidates are gated by the "
                "same action-head relation."
            ),
            "subtree_extraction": (
                "Actor span is the dependency subtree of the candidate head, "
                "excluding its own case preposition and trailing punctuation."
            ),
            "lexicon_gating": (
                "filter_actor_span requires at least one actor-lexicon surface "
                "and, when a head word is known, the head itself must be in the "
                "actor lexicon."
            ),
            "head_token_blacklist": (
                "_NON_ACTOR explicitly rejects it/this/these/those/they/... and "
                "abstract object heads such as profit/income/difference/amount/"
                "period/year/tax/section."
            ),
            "candidate_rejection": (
                "A candidate that fails the actor filter is rejected and the "
                "next subject/agent candidate is tried; no edge is emitted."
            ),
        },
        "direct_llm_fp_filtering_answer": (
            "The pronoun/demonstrative FPs would be rejected by _NON_ACTOR and "
            "the actor-lexicon check. Most non-role grammatical-subject FPs "
            "would be rejected because their head is absent from the actor "
            "lexicon; object heads such as agreement, contribution(s), fund(s), "
            "list, building, period, allowance and pension commitments are not "
            "accepted as actor heads."
        ),
        "direct_llm_fn_capture_answer": (
            "The three LLM-SE FNs are condition-embedded subject/agent "
            "mentions. Rules-Only's clause-wide nsubj/nsubj:pass candidate scan "
            "(C4 in B0_ERROR_ANALYSIS) should naturally see these dependency "
            "subjects even when the actor text is projected into LLM-SE's "
            "condition field."
        ),
        "post_hoc_examples_only_no_direct_llm_modification": post_hoc,
    }


def _prompt_rule_mapping(
    prompt_metadata: Mapping[str, Any],
    inventory: Mapping[str, Any],
    pronoun: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "rule_id": "actor_definition_rule_10",
            "prompt_rule": (
                "actor is the smallest explicit noun phrase or pronominal "
                "mention that bears or performs the norm; a subject pronoun "
                "it/they/this/these/such is a real actor mention."
            ),
            "observed_evidence": {
                "prompt_pronoun_total": pronoun["prompt_pronoun_total"],
                "prompt_pronoun_tp": pronoun["prompt_pronoun_tp"],
                "prompt_pronoun_fp": pronoun["prompt_pronoun_fp"],
                "non_role_fp": (
                    inventory["fp_taxonomy"]["counts"].get(
                        "FP-B_NON_ROLE_GRAMMATICAL_SUBJECT", 0)),
            },
            "evidence_strength": "directly_consistent_with_pronoun_output; correlated_with_non_role_subjects",
            "potential_issue": (
                "The rule licenses pronoun output even when the reference is "
                "unresolved; in this fixed run it enables one pronoun TP but "
                "also emits nine pronoun/demonstrative FPs."
            ),
        },
        {
            "rule_id": "unresolved_pronoun_rule_17",
            "prompt_rule": (
                "For an unresolved subject pronoun, keep normalized surface-"
                "preserving and add a controlled unsupported_or_ambiguous entry."
            ),
            "observed_evidence": {
                "pronoun_total": pronoun["total"],
                "pronoun_tp": pronoun["tp"],
                "pronoun_fp": pronoun["fp"],
                "pronoun_surface_distribution": pronoun["surface_distribution"],
            },
            "evidence_strength": "directly_consistent_with_observed_pronoun_prediction",
            "potential_issue": (
                "The model follows the instruction and emits unresolved "
                "pronouns as actors; one overlaps Gold, but nine are FPs."
            ),
        },
        {
            "rule_id": "passive_no_performer_rule_18",
            "prompt_rule": (
                "In a passive clause with no expressed performer do not infer "
                "an actor; actors=[] and map actions with actor_id=null."
            ),
            "observed_evidence": {
                "non_role_fp_cases": inventory["fp_taxonomy"]["counts"].get(
                    "FP-B_NON_ROLE_GRAMMATICAL_SUBJECT", 0),
            },
            "evidence_strength": "not_directly_tested_by_actor_error_taxonomy",
            "potential_issue": (
                "No direct evidence of failure; retained only as a contrast "
                "rule for the next prompt-design round."
            ),
        },
        {
            "rule_id": "cross_field_projection_rules_10_12_27",
            "prompt_rule": (
                "Actor is defined as an explicit actor mention; condition is a "
                "separate antecedent field. The prompt does not explicitly "
                "require re-projecting actor mentions out of condition spans "
                "into actors."
            ),
            "observed_evidence": {
                "actor_fn_cross_field_presence": sum(
                    1 for case in inventory["fn_cases"]
                    if case["cross_field_overlap"]),
                "actor_fn_total": inventory["fn_count"],
                "cross_field_presence_rate": inventory["cross_field_presence_rate"],
            },
            "evidence_strength": "correlated_with/FN evidence; no single-factor causal claim",
            "potential_issue": (
                "Three Gold actors are inside emitted condition spans; this is "
                "a field-projection gap, not necessarily a recognition gap."
            ),
        },
    ]


def _metadata(
    predictions: Sequence[Mapping[str, Any]],
    gold_by_id: Mapping[str, Mapping[str, Any]],
    prompt_metadata: Mapping[str, Any],
) -> dict[str, Any]:
    gold_blob = json.dumps(list(gold_by_id.values()), ensure_ascii=False,
                           sort_keys=True).encode("utf-8")
    return {
        "schema_version": "d1_actor_semantic_error_audit@1.0.0",
        "status": "read_only_development_actor_error_audit",
        "source_arm": "D-full-0813",
        "sample_count": len(predictions),
        "prediction_source": str(PREDICTION_PATH.relative_to(ROOT)),
        "prediction_source_kind": "repair_v1_new_arm_canonical_predictions",
        "prediction_sha256": _sha256_file(PREDICTION_PATH),
        "input_fingerprints": {
            "raw_responses_path": str((FULL_DIR / "raw_responses.jsonl").relative_to(ROOT)),
            "raw_responses_sha256": _sha256_file(FULL_DIR / "raw_responses.jsonl"),
            "locked_canonical_predictions_path": str((FULL_DIR / "canonical_predictions.jsonl").relative_to(ROOT)),
            "locked_canonical_predictions_sha256": _sha256_file(FULL_DIR / "canonical_predictions.jsonl"),
            "locked_evaluation_path": str((FULL_DIR / "evaluation.json").relative_to(ROOT)),
            "locked_evaluation_sha256": _sha256_file(FULL_DIR / "evaluation.json"),
            "source_input_path": str(runner.ESTG_INPUT.relative_to(ROOT)),
            "source_input_sha256": _sha256_file(runner.ESTG_INPUT),
            "span_canonicalizer_path": "src/bpc_hybrid/d1_span_canonicalizer.py",
            "span_canonicalizer_sha256": _sha256_file(SRC / "bpc_hybrid/d1_span_canonicalizer.py"),
            "schema_adapter_path": "src/bpc_hybrid/d1_schema_adapter.py",
            "schema_adapter_sha256": _sha256_file(SRC / "bpc_hybrid/d1_schema_adapter.py"),
        },
        "gold_source": {
            "builder": "build_canonical_gold_records",
            "pinned_commit": "56d2b03",
            "gold_record_count": len(gold_by_id),
            "gold_canonical_sha256": hashlib.sha256(gold_blob).hexdigest(),
        },
        "evaluator": {
            "version": "sun_literal_overlap_evaluation@2.0.0",
            "match_rule": "independent_same_field_any_nonempty_character_span_intersection",
            "clause_alignment_required": False,
            "assignment": "none_independent_overlap_coverage",
        },
        "canonicalizer_policy": POLICY_REPAIR,
        "canonicalizer_default_policy": DEFAULT_POLICY,
        "prompt": {
            "path": prompt_metadata["path"],
            "sha256": prompt_metadata["sha256"],
        },
        "new_api_calls": 0,
        "prompt_modified": False,
        "gold_modified": False,
        "predictions_modified": False,
        "actor_semantic_rules_added": False,
        "condition_to_actor_implemented": False,
        "rules_only_used_to_modify_direct_llm": False,
        "gold_used_to_tune_algorithm": False,
    }


def run_audit() -> dict[str, Any]:
    predictions = _load_jsonl(PREDICTION_PATH)
    source_by_id = {row["sample_id"]: row["text"] for row in runner._estg_samples()}
    gold_by_id = grounding.build_gold_by_id()
    prompt_metadata = _prompt_metadata()
    inventory = build_actor_inventory(predictions, gold_by_id, source_by_id)
    inventory["fn_taxonomy"] = _taxonomy_counts(inventory["fn_cases"])
    inventory["fp_taxonomy"] = _taxonomy_counts(inventory["fp_cases"])
    inventory["cross_field_presence_rate"] = (
        sum(1 for case in inventory["fn_cases"] if case["cross_field_overlap"])
        / inventory["fn_count"] if inventory["fn_count"] else None
    )
    pronoun = _pronoun_analysis(inventory)
    report = {
        "metadata": _metadata(predictions, gold_by_id, prompt_metadata),
        "actor_metrics": inventory["metrics"],
        "tp_count": inventory["tp_count"],
        "fp_count": inventory["fp_count"],
        "fn_count": inventory["fn_count"],
        "matched_gold_count": inventory["matched_gold_count"],
        "tp_cases": inventory["tp_cases"],
        "fp_cases": inventory["fp_cases"],
        "fn_cases": inventory["fn_cases"],
        "tp_gold_cases": inventory["tp_gold_cases"],
        "fn_taxonomy": inventory["fn_taxonomy"],
        "fp_taxonomy": inventory["fp_taxonomy"],
        "cross_field_projection_analysis": {
            "cross_field_presence_rate": inventory["cross_field_presence_rate"],
            "embedded_in_condition_count": inventory["fn_taxonomy"]["counts"].get(
                "FN-B_EMBEDDED_IN_CONDITION", 0),
            "embedded_in_constraint_count": inventory["fn_taxonomy"]["counts"].get(
                "FN-C_EMBEDDED_IN_CONSTRAINT", 0),
            "embedded_in_action_count": inventory["fn_taxonomy"]["counts"].get(
                "FN-D_EMBEDDED_IN_ACTION", 0),
            "embedded_in_exception_count": inventory["fn_taxonomy"]["counts"].get(
                "FN-E_EMBEDDED_IN_EXCEPTION", 0),
            "absent_from_all_semantic_spans_count": inventory["fn_taxonomy"]["counts"].get(
                "FN-A_ABSENT_FROM_ALL_MODEL_SEMANTIC_SPANS", 0),
        },
        "pronoun_analysis": pronoun,
        "tp_surface_audit": _tp_surface_audit(inventory),
        "rules_only_mechanism_comparison": _rules_only_mechanism_comparison(inventory),
        "prompt_metadata": prompt_metadata,
        "prompt_rule_mapping": _prompt_rule_mapping(prompt_metadata, inventory, pronoun),
        "factorial_actor_delta_analysis": _factorial_actor_delta(gold_by_id),
        "gold_review_candidates": _gold_review_candidates(inventory),
        "limitations": [
            "Single fixed development run (D-full-0813); not a formal or universal claim.",
            "FN/FP taxonomy uses character-span rules plus surface heuristics; every case carries classification_basis and confidence.",
            "Non-role grammatical subject and ontology-disagreement categories are heuristic and may need human review.",
            "Gold is read-only and was not changed; suspicious Gold is reported only as gold_review_candidate.",
            "Rules-Only behavior is shown only as post-hoc method-difference evidence and was not used to edit LLM-SE predictions or rules.",
            "Factorial actor delta uses the existing frozen factorial canonical predictions, which were generated under the pre-promotion legacy policy; it is a within-factorial comparison only.",
        ],
        "safety": {
            "new_llm_api_calls": 0,
            "prompt_modified": False,
            "gold_modified": False,
            "predictions_modified": False,
            "actor_semantic_rules_added": False,
            "condition_to_actor_implemented": False,
            "rules_only_used_to_modify_direct_llm": False,
            "gold_used_to_tune_algorithm": False,
        },
    }
    return report


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def to_markdown(report: Mapping[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Actor semantic error audit v1")
    lines.append("")
    lines.append("> Read-only development audit. No new API calls, no Prompt changes, no Gold changes, no prediction changes, no actor rule changes.")
    lines.append("")
    lines.append("## Actor metrics")
    lines.append("")
    metrics = report["actor_metrics"]
    lines.append("| field | value |")
    lines.append("|---|---:|")
    for key in ("ground_truth", "extracted", "matched_predictions",
                "matched_ground_truth", "precision", "recall", "f1"):
        lines.append(f"| {key} | {_fmt(metrics.get(key))} |")
    lines.append(f"| tp_count (prediction side) | {report['tp_count']} |")
    lines.append(f"| fp_count | {report['fp_count']} |")
    lines.append(f"| fn_count | {report['fn_count']} |")
    lines.append("")
    lines.append("## FN taxonomy")
    lines.append("")
    lines.append("| taxonomy | count | share | sample IDs |")
    lines.append("|---|---:|---:|---|")
    fn_by_tax: dict[str, list[str]] = defaultdict(list)
    for case in report["fn_cases"]:
        fn_by_tax[case["taxonomy"]].append(case["sample_id"])
    for tax, count in report["fn_taxonomy"]["counts"].items():
        share = report["fn_taxonomy"]["shares"].get(tax)
        lines.append(f"| {tax} | {count} | {_fmt(share)} | {', '.join(fn_by_tax[tax])} |")
    lines.append("")
    lines.append("## Cross-field projection")
    lines.append("")
    lines.append(f"- cross_field_presence_rate: {_fmt(report['cross_field_projection_analysis']['cross_field_presence_rate'])}")
    lines.append(f"- embedded in condition: {report['cross_field_projection_analysis']['embedded_in_condition_count']}")
    lines.append(f"- embedded in constraint: {report['cross_field_projection_analysis']['embedded_in_constraint_count']}")
    lines.append(f"- embedded in action: {report['cross_field_projection_analysis']['embedded_in_action_count']}")
    lines.append(f"- embedded in exception: {report['cross_field_projection_analysis']['embedded_in_exception_count']}")
    lines.append("")
    lines.append("## FP taxonomy")
    lines.append("")
    lines.append("| taxonomy | count | share | representative examples |")
    lines.append("|---|---:|---:|---|")
    fp_by_tax: dict[str, list[str]] = defaultdict(list)
    for case in report["fp_cases"]:
        fp_by_tax[case["taxonomy"]].append(str(case.get("text")))
    for tax, count in report["fp_taxonomy"]["counts"].items():
        share = report["fp_taxonomy"]["shares"].get(tax)
        examples = "; ".join(sorted(set(fp_by_tax[tax]))[:6])
        lines.append(f"| {tax} | {count} | {_fmt(share)} | {examples} |")
    lines.append("")
    lines.append("## Pronoun analysis")
    lines.append("")
    lines.append(f"- total: {report['pronoun_analysis']['total']}")
    lines.append(f"- prompt-pronoun total: {report['pronoun_analysis']['prompt_pronoun_total']}")
    lines.append(f"- prompt-pronoun TP: {report['pronoun_analysis']['prompt_pronoun_tp']}")
    lines.append(f"- prompt-pronoun FP: {report['pronoun_analysis']['prompt_pronoun_fp']}")
    lines.append(f"- precision: {_fmt(report['pronoun_analysis']['precision'])}")
    lines.append(f"- surface distribution: {report['pronoun_analysis']['surface_distribution']}")
    lines.append("")
    lines.append("## Prompt rule → observed evidence")
    lines.append("")
    lines.append("| rule | evidence | strength | potential issue |")
    lines.append("|---|---|---|---|")
    for item in report["prompt_rule_mapping"]:
        lines.append(
            f"| {item['rule_id']} | {json.dumps(item['observed_evidence'], ensure_ascii=False)} | "
            f"{item['evidence_strength']} | {item['potential_issue']} |")
    lines.append("")
    lines.append("## Factorial Actor delta (Full → No semantic guidance)")
    lines.append("")
    delta = report["factorial_actor_delta_analysis"]["full_to_no_guidance"]
    for key in ("full_actor_predictions_count", "no_guidance_actor_predictions_count",
                "delta_prediction_count", "delta_matched_predictions_tp_side",
                "delta_fp", "delta_matched_ground_truth_recall_side", "delta_fn",
                "lost_surface_count", "gained_surface_count",
                "beneficial_removal_count", "harmful_loss_count"):
        lines.append(f"- {key}: {delta[key]}")
    lines.append("")
    lines.append("## Gold review candidates")
    lines.append("")
    if report["gold_review_candidates"]:
        for case in report["gold_review_candidates"]:
            lines.append(f"- `{case['sample_id']}`: {case['text']} ({case['taxonomy']})")
    else:
        lines.append("none")
    lines.append("")
    lines.append("## Limitations")
    lines.append("")
    for item in report["limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if not args.overwrite and (REPORT_JSON.exists() or REPORT_MD.exists()):
        print("refusing to overwrite existing actor audit reports")
        return 2
    report = run_audit()
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    REPORT_MD.write_text(to_markdown(report), encoding="utf-8")
    print(json.dumps({
        "actor_metrics": report["actor_metrics"],
        "tp_count": report["tp_count"],
        "fp_count": report["fp_count"],
        "fn_count": report["fn_count"],
        "fn_taxonomy": report["fn_taxonomy"]["counts"],
        "fp_taxonomy": report["fp_taxonomy"]["counts"],
        "cross_field_presence_rate": report["cross_field_projection_analysis"]["cross_field_presence_rate"],
        "pronoun": {k: report["pronoun_analysis"][k] for k in
                    ("total", "tp", "fp", "precision")},
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
