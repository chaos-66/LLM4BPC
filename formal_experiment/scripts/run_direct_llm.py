"""Guarded direct-LLM extraction with a plain model-facing prompt.

The default plain prompt produces semantic content only. The runner attaches
record identity and internal metadata, then applies the existing adapters and
validator. Plain-prompt outputs are development-only until separately evaluated.
Historical prompts remain selectable for reproducing their recorded recipes;
their text and processing are preserved. Prompt hashes belong in the manifest.

Real API calls require explicit user authorization and ``--allow-llm``.
No real call is made here.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bpc_hybrid.llm_client import LLMClientError, LLMRequest, RealAPITransport
from bpc_hybrid.llm_config import LLMConfig
from bpc_hybrid.prompt_loader import build_manifest_entry, load_prompt
from bpc_hybrid.plain_prompt import PLAIN_PROMPT_NAME, prepare_plain_prediction
from bpc_hybrid.stage2_canonical import validate_canonical

# Status reads — these are read-only, not LLM calls
from formal_experiment.audit import collect_project_audit
from formal_experiment.paths import (
    FORMAL_PREDICTIONS_DIR,
    FORMAL_RESULTS_DIR,
    FROZEN_GOLD_DIR,
    FROZEN_INPUT_DIR,
    DEVELOPMENT_DIR,
)

PROMPTName = PLAIN_PROMPT_NAME
PROMPT_LEGACY = "direct_llm_sun_record_prompt"
PROMPT_V3_SNAPSHOT = "direct_llm_sun_record_prompt_v3_2026_07_12"
PROMPT_V5_FROZEN = "direct_llm_sun_record_prompt_v5_2026_07_29_frozen"
PROMPT_V6_D1R1 = "direct_llm_sun_record_prompt_v6_d1r1_2026_08_05"
PROMPT_SOLCAND_PILOT = "direct_llm_sun_record_prompt_solcand_pilot_2026_08_07"
SIMPLIFICATION_PROMPT_NAMES = (
    "simplification_v1/direct_llm_json_light_v1",
    "simplification_v1/direct_llm_json_semantic_light_v1",
)
ALLOWED_PROMPT_NAMES = (
    PROMPTName,
    PROMPT_LEGACY,
    PROMPT_V3_SNAPSHOT,
    PROMPT_V5_FROZEN,
    PROMPT_V6_D1R1,
    PROMPT_SOLCAND_PILOT,
    *SIMPLIFICATION_PROMPT_NAMES,
)

DEFAULT_INPUT = ROOT / "data/input/estg150_input_v1.jsonl"
DEFAULT_OUTPUT = ROOT / "data/predictions/direct_llm_predictions.jsonl"
DEFAULT_MANIFEST = ROOT / "data/predictions/direct_llm_manifest.json"

FORMAL_DIRS = (
    FROZEN_INPUT_DIR,
    FROZEN_GOLD_DIR,
    FORMAL_PREDICTIONS_DIR,
    FORMAL_RESULTS_DIR,
)


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _gate_formal_write(target: Path) -> tuple[bool, str]:
    """Return (allowed, reason). False when the write must be refused.

    Formal artifact directories refuse writes unless (a) the route is
    locked, (b) the method is ready, and (c) explicit ``--development``
    is **not** in effect. Development paths are always allowed but
    flagged as development in the manifest.
    """
    is_formal = any(_is_under(target, fd) for fd in FORMAL_DIRS)
    if not is_formal:
        return True, "non-formal path"
    audit = collect_project_audit()
    if not audit["integrity_pass"]:
        return False, "audit integrity_pass is false"
    if audit["final_experiment_ready"]:
        return True, "audit final_experiment_ready is true"
    return False, (
        "formal write refused: route is not final-ready. "
        "Pass --development and write to outputs/development or "
        "data/development instead."
    )


def _load_input(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            row = json.loads(raw)
            if not isinstance(row.get("sample_id"), str) or not isinstance(row.get("text"), str):
                raise ValueError(f"line {line_number}: expected sample_id and text")
            rows.append(row)
    if not rows:
        raise ValueError("input is empty")
    if len({row["sample_id"] for row in rows}) != len(rows):
        raise ValueError("duplicate sample IDs")
    return rows


def _few_shot_block(prompt: object) -> str:
    """Render the few-shot block sent to the LLM.

    Uses the raw ``## Examples`` section of the prompt file (the exact
    rendering that reproduced the July s28_s29 canonical output), so the
    examples reach the model verbatim with their verified offsets.
    """
    raw = getattr(prompt, "raw_text", "")
    start = raw.find("## Examples")
    end = raw.find("## Notes", start)
    if start == -1:
        return ""
    if end == -1:
        end = len(raw)
    return raw[start:end].strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--allow-llm",
        action="store_true",
        help="Explicitly authorize real LLM calls; required for any non-mock run.",
    )
    parser.add_argument(
        "--max-calls",
        type=int,
        default=150,
        help="Hard upper bound on LLM calls (default 150).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Explicitly allow replacing existing output and manifest files.",
    )
    parser.add_argument(
        "--development",
        action="store_true",
        help="Run as development-only; manifest records dev mode. Required for any "
        "write to outputs/development or data/development.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Fail-closed model pin: the resolved provider model must equal this "
        "exact value, otherwise the run aborts before any call. The returned model "
        "is verified per response and recorded in the manifest.",
    )
    parser.add_argument(
        "--prompt-name",
        type=str,
        default=PROMPTName,
        choices=ALLOWED_PROMPT_NAMES,
        help="Prompt file stem to load (allowlisted).",
    )
    parser.add_argument(
        "--json-object-response",
        action="store_true",
        help="Send response_format={type: json_object} (default: omitted; the "
        "reproduced July recipe uses thinking-disabled without json_object).",
    )
    parser.add_argument(
        "--transport-timeout",
        type=float,
        default=180.0,
        help="Per-request timeout in seconds (default 180; July's longest call "
        "took ~162 s).",
    )
    args = parser.parse_args()

    if args.prompt_name == PLAIN_PROMPT_NAME:
        plain_root = ROOT / "outputs/development/s2_prompt_cleanup_v1"
        if not args.development or any(
            not _is_under(path, plain_root) for path in (args.output, args.manifest)
        ):
            print(
                "Refusing to run: plain prompt requires --development and new "
                "output/manifest paths under outputs/development/s2_prompt_cleanup_v1."
            )
            return 2

    # New prompt candidates stay opt-in and cannot write into frozen capsules.
    if args.prompt_name in SIMPLIFICATION_PROMPT_NAMES:
        candidate_root = ROOT / "outputs/development/s2_prompt_simplification_v1"
        if not args.development or any(
            not _is_under(path, candidate_root) for path in (args.output, args.manifest)
        ):
            print(
                "Refusing to run: simplification candidates require --development "
                "and new output/manifest paths under "
                "outputs/development/s2_prompt_simplification_v1."
            )
            return 2

    # 1. Load prompt from disk
    prompt = load_prompt(args.prompt_name)

    # 2. Refuse to overwrite existing artifacts unless --overwrite
    for path in (args.output, args.manifest):
        if path.exists() and not args.overwrite:
            print(f"Refusing to overwrite existing artifact: {path}")
            return 2

    # 3. Gate formal writes
    for path in (args.output, args.manifest):
        allowed, reason = _gate_formal_write(path)
        if not allowed:
            print(f"Refusing to write {path}: {reason}")
            return 2
        if not allowed and not args.development:
            print(f"Refusing to write formal path {path} without --development.")
            return 2

    # 4. LLM authorization gate
    if not args.allow_llm:
        print("Refusing to run: real LLM calls require explicit authorization and --allow-llm.")
        return 2
    if args.max_calls < 1:
        print("Refusing to run: --max-calls must be positive.")
        return 2

    # 5. LLM config + fail-closed model pin (before any input I/O)
    config = LLMConfig.from_env(project_root=ROOT)
    if args.model is not None and config.model != args.model:
        print(
            f"Refusing to run: resolved model {config.model!r} != requested "
            f"{args.model!r} (fail-closed model pin)."
        )
        return 2
    if not config.enabled or config.provider == "mock":
        print("Refusing to run: a real LLM provider is not enabled.")
        return 2
    # D1-R1 (2026-08-05): the reproduced July recipe is thinking-disabled
    # WITHOUT a json_object response_format (the official deepseek-v4-pro
    # endpoint returns empty content under provider-default thinking and a
    # different nested shape under json_object). response_format is only
    # requested when --json-object-response is passed explicitly.
    from bpc_hybrid.h1_transport import H1RequestPolicy

    transport = RealAPITransport(
        config,
        timeout_seconds=args.transport_timeout,
        policy=H1RequestPolicy(
            stream=False,
            thinking={"type": "disabled"},
            response_format={"type": "json_object"} if args.json_object_response else None,
        ),
    )

    # 6. Load and validate input
    try:
        rows = _load_input(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Invalid frozen input: {exc}")
        return 3
    if len(rows) > args.max_calls:
        print(f"Refusing to run: {len(rows)} records exceed --max-calls={args.max_calls}.")
        return 3

    # 7. Process samples
    results: list[dict] = []
    responses: list[dict] = []
    validation_failures: list[dict] = []
    llm_errors: list[dict] = []
    returned_models: set[str] = set()
    span_audit_summary: dict[str, int] = {
        "records": 0, "reanchored": 0, "clause_spans": 0, "field_spans": 0,
        "dropped_spans": 0, "dropped_clauses": 0, "adapted_spans": 0,
    }
    # Build the prompt body ONCE and reuse for all rows
    from bpc_hybrid.llm_client import OpenAICompatibleRequestBuilder
    builder = OpenAICompatibleRequestBuilder(config)
    sent_sampling = builder.sent_sampling_params()
    few_shot_block = _few_shot_block(prompt)
    for row in rows:
        sample_id = row["sample_id"]
        source_text = row["text"]
        user_prompt = prompt.user_prompt_template.format(
            sample_id=sample_id,
            source_id=sample_id,
            source_text=source_text,
            few_shot_block=few_shot_block,
        )
        request = LLMRequest(
            source_id=sample_id,
            source_text=source_text,
            system_prompt=prompt.system_prompt,
            user_prompt=user_prompt,
        )
        try:
            response = transport.send(request)
        except LLMClientError as exc:
            llm_errors.append({"sample_id": sample_id, "error": str(exc)})
            continue
        returned = getattr(response, "model", None)
        if returned:
            returned_models.add(str(returned))
            # Fail closed: every response must come back from the pinned model.
            if args.model is not None and str(returned) != args.model:
                print(
                    f"Aborting: response model {returned!r} != pinned {args.model!r} "
                    f"(sample {sample_id})."
                )
                return 3

        raw_text = response.content.strip()
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            raw_text = "\n".join(lines[1:-1])
        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            llm_errors.append({"sample_id": sample_id, "error": f"non-JSON: {exc}"})
            continue
        if not isinstance(payload, dict):
            llm_errors.append({"sample_id": sample_id, "error": "payload not a dict"})
            continue

        if args.prompt_name == PLAIN_PROMPT_NAME:
            try:
                payload = prepare_plain_prediction(
                    payload, sample_id=sample_id, source_text=source_text
                )
            except ValueError as exc:
                llm_errors.append({"sample_id": sample_id, "error": f"invalid plain output: {exc}"})
                continue

        # Inject source_id if the LLM omitted it
        payload.setdefault("source_id", sample_id)
        payload.setdefault("sample_id", sample_id)
        payload.setdefault("source_text", source_text)
        payload.setdefault("schema_version", "1.0.0")
        payload.setdefault("method", {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"})
        payload.setdefault("unsupported_or_ambiguous", [])

        # D1-R1 (2026-08-05): the adapter maps relay-specific nested
        # conventions back to canonical spans; span coordinates are then
        # re-anchored to the unique exact occurrence of their text.
        # Empty-vs-error policy (user decision 2026-08-05): empty elements
        # are legal; unrecoverable field spans and clauses are DROPPED with
        # an audit trail instead of failing the whole record; only
        # record-level structural violations fail closed.
        from bpc_hybrid.d1_schema_adapter import adapt_relay_record
        from bpc_hybrid.d1_span_canonicalizer import canonicalize_record_coordinates

        payload, adapt_audit = adapt_relay_record(payload, source_text)
        if adapt_audit["status"] == "failed":
            errs = [f"relay_schema_adaptation_failed: {', '.join(adapt_audit['failed_reasons'])}"]
            validation_failures.append(
                {"sample_id": sample_id, "errors": errs, "relay_schema_adaptation": adapt_audit}
            )
            responses.append(
                {"sample_id": sample_id, "request_status": "ok", "error_category": "relay_schema_adaptation_failed", "errors": errs, "record": payload}
            )
            continue
        payload, span_audit = canonicalize_record_coordinates(payload, source_text)
        if span_audit["status"] == "failed":
            errs = [f"span_canonicalization_failed: {', '.join(span_audit['failed_reasons'])}"]
            validation_failures.append(
                {"sample_id": sample_id, "errors": errs, "span_canonicalization": span_audit}
            )
            responses.append(
                {"sample_id": sample_id, "request_status": "ok", "error_category": "span_canonicalization_failed", "errors": errs, "span_canonicalization": span_audit, "record": payload}
            )
            continue

        # Validate against canonical schema + cross-field rules
        report = validate_canonical(payload)
        if not (report.schema_valid and report.cross_field_valid):
            errs = list(report.errors)
            validation_failures.append({"sample_id": sample_id, "errors": errs})
            responses.append(
                {"sample_id": sample_id, "request_status": "ok", "error_category": "canonical_validation_failed", "errors": errs, "span_canonicalization": span_audit, "record": payload}
            )
            continue
        results.append(payload)
        responses.append(
            {"sample_id": sample_id, "request_status": "ok", "error_category": None, "errors": [], "span_canonicalization": span_audit, "record": payload}
        )
        span_audit_summary["records"] += 1
        span_audit_summary["reanchored"] += span_audit["reanchored_count"]
        span_audit_summary["clause_spans"] += span_audit["clause_span_count"]
        span_audit_summary["field_spans"] += span_audit["field_span_count"]
        span_audit_summary["dropped_spans"] += len(span_audit.get("dropped_spans", []))
        span_audit_summary["dropped_clauses"] += len(span_audit.get("dropped_clauses", []))
        span_audit_summary["adapted_spans"] += adapt_audit["spans_adapted"]

    # 8. Write outputs
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for record in results:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    with (args.output.parent / "d1_responses.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for entry in responses:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    manifest = {
        "schema_version": "1.0.0",
        "stage": "formal_stage2",
        "method": "direct_llm",
        "mode": "development" if args.development else "formal",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input_path": str(args.input),
        "output_path": str(args.output),
        "sample_count_input": len(rows),
        "sample_count_written": len(results),
        "sample_count_validation_failed": len(validation_failures),
        "sample_count_llm_error": len(llm_errors),
        "llm_calls": len(rows),
        "max_calls": args.max_calls,
        "llm_provider": config.provider,
        "llm_model": config.model,
        "llm_models": {
            "requested": args.model,
            "resolved": config.model,
            "returned": sorted(returned_models),
        },
        "transport_policy": transport.last_request_policy,
        "sampling": sent_sampling,
        "prompts": [build_manifest_entry(prompt)],
        "real_api": True,
        "gold_read_by_runner": False,
        "rule_front_end_used": False,
        "validation_failures": validation_failures,
        "llm_errors": llm_errors,
        "responses_file": str(args.output.parent / "d1_responses.jsonl"),
        "span_canonicalization": span_audit_summary,
    }
    args.manifest.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"Wrote {len(results)} direct-LLM predictions (canonical v1.0.0) and manifest.")
    print(f"Validation failures: {len(validation_failures)}; LLM errors: {len(llm_errors)}.")
    print(f"Prompt SHA-256: {prompt.sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
