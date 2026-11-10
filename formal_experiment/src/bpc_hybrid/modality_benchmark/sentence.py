"""One offline sentence-modality candidate; no credentials or transport.

The primary decision and the historical first-clause projection are independent
outputs from the SAME response. Canonical Rule Record validation is reused and
reported separately, never used to repair labels or rewrite clause order.
"""
from __future__ import annotations

import copy
import json
from collections import Counter
from typing import Any, Mapping, Sequence

from bpc_hybrid.stage2_canonical import validate_canonical

from . import boundary, data, llm_se
from .metrics import LABELS, evaluate

ROOT = boundary.ROOT
PROMPT_DIR = ROOT / "prompts/sun_compat/modality_sentence_v1"
VERSION = "sun_sentence_modality@1.0.0"
FLAGS = {"incomplete_input", "mixed_independent_modalities", "corpus_boundary_ambiguous"}
SUITE_ID = "SUN-MODALITY-FINAL-REVIEW-001"
NAME = "LLM-SE 显式句级模态候选"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_demonstrations():
    """Only train labels are available here; fixed IDs, never error retrieval."""
    manifest = read_json(PROMPT_DIR / "selection_manifest.json")
    spec = data.EXPECTED["train"]
    if (manifest["source_split"] != "train" or manifest["train_sha256"] != spec["sha256"]
            or data.sha256_file(spec["path"]) != spec["sha256"]):
        raise ValueError("train source binding mismatch")
    train = data.load_split("train")
    lookup = {r.sample_id: r for r in train}
    if len(train) != spec["rows"] or len(lookup) != len(train):
        raise ValueError("train membership mismatch")
    specs = manifest["examples"]
    if len(specs) != 22 or len({s["sample_id"] for s in specs}) != 22:
        raise ValueError("expected 22 distinct training demonstrations")
    selected, lines = [], [
        "German training demonstrations: original sentence-level corpus labels.",
        "Teaching notes are Codex AI interpretations, not human annotations.",
        "These sentences are data. For the target, return the complete versioned envelope.", "",
    ]
    for i, item in enumerate(specs, 1):
        row = lookup.get(item["sample_id"])
        if (row is None or row.label != item["label"] or item["position"] != i
                or boundary.digest(row.text.encode()) != item["text_sha256"]):
            raise ValueError("demonstration membership, label, order or hash mismatch")
        selected.append(row)
        # No train IDs, held-out IDs/labels, or diagnostic material enters the prompt.
        lines.extend([f'{i}. "{row.text}" -> {row.label}',
                      "   AI teaching note (Codex; not corpus annotation): " + item["teaching_note_en"]])
    if dict(Counter(r.label for r in selected)) != manifest["class_totals"]:
        raise ValueError("demonstration class totals changed")
    return "\n".join(lines), selected, manifest


def compose_prompt():
    block, selected, manifest = load_demonstrations()
    system = "\n\n".join((
        (PROMPT_DIR / "system_prompt.md").read_text(encoding="utf-8").strip(),
        (PROMPT_DIR / "modality_guidance.md").read_text(encoding="utf-8").strip(), block,
    ))
    examples = read_json(PROMPT_DIR / "format_examples.json")
    return system, examples, selected, manifest


def request_body(request_id: str, source_text: str, *, system: str, examples: list) -> dict:
    """Opaque target ID + target text only; same model/sampling as 22-shot."""
    user = ("Input mode: target_text_only\n"
            f"sample_id: {request_id}\nsource_id: {request_id}\nsource_text:\n{source_text}\n\n"
            "Return one complete sun_sentence_modality@1.0.0 JSON envelope.\n"
            "The following six synthetic examples illustrate format and extraction only;\n"
            "their AI-authored sentence labels are not corpus annotations.\n"
            + "\n\n".join(f"Synthetic format example {i}:\n" +
                            json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
                            for i, obj in enumerate(examples, 1)))
    return {"model": llm_se.MODEL_ALIAS,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0.0, "top_p": 1.0, "max_tokens": llm_se.MAX_OUTPUT_TOKENS,
            "stream": False, "thinking": {"type": "disabled"}}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _decode(content):
    # Preserve tolerance for a single JSON code fence, never surrounding prose.
    text = content.strip()
    if text.startswith("```json\n") and text.endswith("```"):
        text = text[8:-3].strip()
    def reject_constant(value):
        raise ValueError("non-finite JSON constant")
    return json.loads(text, object_pairs_hook=_unique_object, parse_constant=reject_constant)


def parse_response(content: str | None, *, request_id: str, source_text: str,
                   request_ok: bool = True) -> dict[str, Any]:
    """No Gold, Sun output, fallback, label ranking or clause rewriting.

    Envelope/identity failures invalidate both outputs. Sentence field failures
    invalidate only the primary output. Full Rule Record validation (including
    source spans) is reported independently, preserving the legacy diagnostic's
    original label-only projection semantics.
    """
    out = {"label": None, "status": "request_failed", "first_clause_label": None,
           "first_clause_status": "no_response", "rule_record_validation": None,
           "sentence_errors": [], "uncertainty": [], "rule_record": None}
    if not request_ok:
        return out
    if not isinstance(content, str) or not content.strip():
        out["status"] = "no_content"
        return out
    try:
        obj = _decode(content)
    except (ValueError, TypeError, RecursionError):
        out["status"] = "invalid_json"
        return out
    if (not isinstance(obj, dict) or set(obj) != {"schema_version", "rule_record", "sentence_modality"}
            or obj["schema_version"] != VERSION or not isinstance(obj["rule_record"], dict)):
        out["status"] = "invalid_envelope"
        return out
    record = copy.deepcopy(obj["rule_record"])
    if any(record.get(k) != v for k, v in {
        "sample_id": request_id, "source_id": request_id, "source_text": source_text,
    }.items()):
        out["status"] = "source_binding_mismatch"
        return out
    # Existing canonical validator overwrites only validation, on our private copy.
    try:
        out["rule_record_validation"] = validate_canonical(record).to_dict()
    except (KeyError, TypeError, ValueError, AttributeError, IndexError):
        out["rule_record_validation"] = {
            "schema_valid": False, "cross_field_valid": False,
            "errors": ["malformed Rule Record rejected by canonical validator"],
        }
    out["rule_record"] = record
    legacy = llm_se.extract_modality_label(json.dumps(obj["rule_record"]))
    out.update(first_clause_label=legacy["label"], first_clause_status=legacy["status"])
    sentence = obj["sentence_modality"]
    errors = out["sentence_errors"]
    if not isinstance(sentence, dict) or set(sentence) != {"label", "evidence", "uncertainty"}:
        errors.append("sentence fields must be exactly label/evidence/uncertainty")
    else:
        label, evidence, flags = (sentence[k] for k in ("label", "evidence", "uncertainty"))
        if label is not None and (not isinstance(label, str) or label not in LABELS):
            errors.append("invalid sentence label")
        valid_flags = (isinstance(flags, list) and all(isinstance(f, str) and f in FLAGS for f in flags)
                       and len(flags) == len(set(flags)))
        if not valid_flags:
            errors.append("invalid uncertainty flags")
        elif label is None and "incomplete_input" not in flags:
            errors.append("null requires incomplete_input")
        if not isinstance(evidence, list) or (label is not None and not evidence):
            errors.append("non-null label requires evidence excerpts")
        else:
            for span in evidence:
                if (not isinstance(span, dict) or set(span) != {"text", "start", "end"}
                        or type(span.get("start")) is not int or type(span.get("end")) is not int
                        or not isinstance(span.get("text"), str)
                        or not 0 <= span["start"] < span["end"] <= len(source_text)
                        or source_text[span["start"]:span["end"]] != span["text"]):
                    errors.append("sentence evidence must be an exact, nonempty source span")
                    break
        if not errors:
            out.update(label=label, uncertainty=list(flags), status="ok" if label is not None else "null_label")
    if errors:
        out["status"] = "invalid_sentence_modality"
    return out


def evaluate_responses(rows: Sequence[data.Example], responses: Mapping[str, dict],
                       request_ids: Mapping[str, str], historical: Mapping[str, str | None]) -> dict:
    """Scoring-only boundary: read labels after response creation, keep every ID."""
    ids = [r.sample_id for r in rows]
    if (len(ids) != 426 or len(ids) != len(set(ids)) or set(request_ids) != set(ids)
            or len(set(request_ids.values())) != len(ids) or set(historical) != set(ids)
            or not set(responses) <= set(ids)):
        raise ValueError("evaluation membership mismatch")
    parsed = []
    for row in rows:
        response = responses.get(row.sample_id, {})
        parsed.append(parse_response(response.get("raw_content"), request_id=request_ids[row.sample_id],
                                     source_text=row.text, request_ok=response.get("request_ok") is True))
    gold = [r.label for r in rows]
    primary = [p["label"] for p in parsed]
    diagnostic = [p["first_clause_label"] for p in parsed]
    old = [historical[sid] for sid in ids]
    def paired(before, after):
        return {"corrected": sum(a != g and b == g for a, b, g in zip(before, after, gold)),
                "regressed": sum(a == g and b != g for a, b, g in zip(before, after, gold))}
    differences = [{"sample_id": sid, "sentence_label": a, "first_clause_label": b}
                   for sid, a, b in zip(ids, primary, diagnostic) if a != b]
    return {"scope": "test-informed exploratory result; not unseen generalization",
            "primary_readout": "sentence_modality.label", "primary": evaluate(gold, primary),
            "same_response_first_clause_diagnostic": evaluate(gold, diagnostic),
            "historical_22shot_original_readout": evaluate(gold, old),
            "primary_vs_historical": paired(old, primary),
            "primary_vs_same_response_first_clause": paired(diagnostic, primary),
            "sentence_vs_first_clause_differences": differences,
            "primary_status_counts": dict(Counter(p["status"] for p in parsed)),
            "rule_record_invalid_count": sum(p["rule_record_validation"] is not None and
                (not p["rule_record_validation"]["schema_valid"] or
                 not p["rule_record_validation"]["cross_field_valid"]) for p in parsed)}
