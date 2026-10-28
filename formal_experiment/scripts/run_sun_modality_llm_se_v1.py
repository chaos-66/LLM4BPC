"""Run the LLM-SE arm on the Sun modality test sentences (real API calls).

Two phases, both offline-safe until ``--execute`` is passed:

    --preflight  render all 426 requests, estimate input tokens, project
                 the cost with the official CNY price table and write the
                 plan.  No network.
    --execute    send exactly one request per test sample, append every
                 call to a hash-chained ledger, enforce the hard CNY cap
                 before each send, and never retry.

Gold is never read here: the input loader ignores the label field and the
predictions are written before any evaluation happens.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bpc_hybrid.modality_benchmark import data as data_mod  # noqa: E402
from bpc_hybrid.modality_benchmark import llm_se  # noqa: E402

DEFAULT_RUN_ID = "s28_sun_modality_five_way_v1"
OUTPUT_ROOT = ROOT / "outputs/development"
ACCEPTED_MODELS = {"deepseek-v4-pro", "DeepSeek-V4-Pro-0813"}
MAX_CONSECUTIVE_ERRORS = 5


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if raw.strip():
                rows.append(json.loads(raw))
    return rows


def append_jsonl(path: Path, row: Mapping[str, Any]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def build_plan(pairs: Sequence[tuple[str, str]]) -> dict[str, Any]:
    requests = []
    total_tokens = 0
    for sample_id, text in pairs:
        body = llm_se.request_body(sample_id, text)
        tokens = llm_se.estimate_input_tokens(body)
        total_tokens += tokens
        requests.append(
            {
                "sample_id": sample_id,
                "estimated_input_tokens": tokens,
                "request_body_sha256": sha256_bytes(
                    json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")
                ),
            }
        )
    return {
        "schema_version": "sun_modality_llm_se_plan@1.0.0",
        "created_at": now_utc(),
        "prompt": {
            "name": llm_se.PROMPT_NAME,
            "path": llm_se.PROMPT_PATH.relative_to(ROOT).as_posix(),
            "sha256": llm_se.PROMPT_SHA256,
            "max_output_tokens": llm_se.MAX_OUTPUT_TOKENS,
        },
        "model": {
            "requested_alias": llm_se.MODEL_ALIAS,
            "documented_release": llm_se.DOCUMENTED_RELEASE,
        },
        "sampling": {"temperature": 0.0, "top_p": 1.0, "retry": 0, "thinking": "disabled"},
        "calls": len(requests),
        "estimated_input_tokens_total": total_tokens,
        "estimated_input_tokens_mean": total_tokens / len(requests),
        "requests": requests,
        "input_language": "de",
        "input_deviation_note": (
            "frozen prompt was authored for the English EStG-150 text; this "
            "run applies it to the German Sun sentences so that every arm "
            "sees the same German original"
        ),
    }


def project_cost(plan: Mapping[str, Any], rate: Mapping[str, float], reserve_out: int) -> dict[str, float]:
    calls = plan["calls"]
    mean_in = plan["estimated_input_tokens_mean"]
    per_call = (mean_in * rate["input_cache_miss"] + reserve_out * rate["output"]) / 1_000_000
    expected_out = 716  # observed mean completion length of the frozen English arm
    per_call_expected = (
        mean_in * rate["input_cache_miss"] + expected_out * rate["output"]
    ) / 1_000_000
    return {
        "per_call_reserved_cny": per_call,
        "total_reserved_cny": per_call * calls,
        "per_call_expected_cny": per_call_expected,
        "total_expected_cny": per_call_expected * calls,
    }


def cmd_preflight(run_dir: Path, cap_cny: float, reserve_out: int) -> int:
    pairs = data_mod.load_split_text_only("test")
    plan = build_plan(pairs)
    plan["prompt_overlap"] = llm_se.prompt_overlap_report([text for _, text in pairs])
    moment = datetime.now(llm_se.BEIJING)
    window, rate = llm_se.rate_for(moment)
    plan["price"] = {
        "window_at_preflight": window,
        "beijing_time": moment.isoformat(),
        "rate_cny_per_million": rate,
        "source": llm_se.PRICE_SOURCE_URL,
        "verified_at": llm_se.PRICE_VERIFIED_AT,
        "reserve_output_tokens": reserve_out,
    }
    plan["projection"] = {
        "off_peak": project_cost(plan, llm_se.PRICE_CNY_PER_MILLION["off_peak"], reserve_out),
        "peak": project_cost(plan, llm_se.PRICE_CNY_PER_MILLION["peak"], reserve_out),
    }
    plan["budget_cap_cny"] = cap_cny
    plan["fits_off_peak"] = plan["projection"]["off_peak"]["total_reserved_cny"] <= cap_cny
    plan["fits_peak"] = plan["projection"]["peak"]["total_reserved_cny"] <= cap_cny
    write_json(run_dir / "preflight.json", plan)
    print(json.dumps({k: v for k, v in plan.items() if k != "requests"}, ensure_ascii=False, indent=2))
    return 0


def _verify_preflight(plan: Mapping[str, Any], pairs: Sequence[tuple[str, str]]) -> None:
    if plan.get("calls") != len(pairs):
        raise SystemExit("preflight call count does not match the test population")
    replayed = build_plan(pairs)
    if [r["request_body_sha256"] for r in replayed["requests"]] != [
        r["request_body_sha256"] for r in plan["requests"]
    ]:
        raise SystemExit("preflight request hashes do not replay, the prompt or data drifted")
    overlap = plan.get("prompt_overlap") or {}
    if overlap.get("raw_text_overlap") or overlap.get("normalized_text_overlap"):
        raise SystemExit("few-shot examples overlap the test set; refusing to run")


class _SimulatedTransport:
    """Offline transport used only by ``--simulate`` to exercise the loop."""

    def __init__(self) -> None:
        self.last_decode: dict[str, Any] = {}
        self.last_request_body_sha256: str | None = None

    def send(self, request: Any) -> Any:
        from bpc_hybrid.llm_client import LLMResponse

        self.last_decode = {
            "status": "ok_message_content",
            "model": "deepseek-v4-pro",
            "usage": {
                "prompt_tokens": 6000,
                "completion_tokens": 700,
                "prompt_cache_hit_tokens": 0,
                "prompt_cache_miss_tokens": 6000,
            },
        }
        self.last_request_body_sha256 = None
        content = json.dumps(
            {
                "schema_version": "1.0.0",
                "sample_id": request.source_id,
                "source_id": request.source_id,
                "source_text": request.source_text,
                "clauses": [
                    {
                        "clause_id": "c01",
                        "clause_span": {"text": request.source_text, "start": 0, "end": len(request.source_text)},
                        "modality": {"label": "obligation", "evidence": []},
                        "actors": [],
                        "actions": [],
                        "conditions": [],
                        "constraints": [],
                        "exceptions": [],
                        "actor_action_map": [],
                        "order_relations": [],
                    }
                ],
                "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
                "validation": {"schema_valid": True, "cross_field_valid": True, "errors": []},
                "unsupported_or_ambiguous": [],
            }
        )
        return LLMResponse(content=content, provider="simulated", model="deepseek-v4-pro")


def cmd_execute(run_dir: Path, cap_cny: float, reserve_out: int, allow_peak: bool,
                simulate: int = 0) -> int:
    from bpc_hybrid.h1_transport import H1RequestPolicy
    from bpc_hybrid.llm_client import LLMRequest, RealAPITransport
    from bpc_hybrid.llm_config import get_llm_config

    preflight_path = run_dir / "preflight.json"
    if not preflight_path.exists():
        raise SystemExit("run --preflight first")
    plan = json.loads(preflight_path.read_text(encoding="utf-8"))
    pairs = data_mod.load_split_text_only("test")
    _verify_preflight(plan, pairs)

    moment = datetime.now(llm_se.BEIJING)
    window, rate = llm_se.rate_for(moment)
    if window == "peak" and not allow_peak and not simulate:
        raise SystemExit(
            "peak pricing window active; the 20 CNY cap only covers the batch "
            "at off-peak rates. Re-run after 18:00 Beijing or pass --allow-peak."
        )

    response_path = run_dir / "llm_se_responses.jsonl"
    ledger_path = run_dir / "llm_se_ledger.jsonl"
    existing = {row["sample_id"] for row in read_jsonl(response_path)}
    pending = [(sid, text) for sid, text in pairs if sid not in existing]
    if simulate:
        pending = pending[:simulate]
    if len(existing) + len(pending) != len(pairs) and not simulate:
        raise SystemExit("response ledger does not match the test population")

    if simulate:
        transport: Any = _SimulatedTransport()
    else:
        config = get_llm_config(
            profile="deepseek",
            project_root=ROOT,
            timeout_seconds=180.0,
            max_tokens=llm_se.MAX_OUTPUT_TOKENS,
        )
        policy = H1RequestPolicy(
            stream=False,
            thinking={"type": "disabled"},
            response_format=None,
        )
        transport = RealAPITransport(
            config=config, timeout_seconds=180.0, policy=policy
        )
    gate = llm_se.CostGate(cap_cny=cap_cny, reserve_output_tokens=reserve_out)
    prev_hash = ""
    for row in read_jsonl(ledger_path):
        gate.spent_cny += float(row.get("cost_cny") or 0.0)
        gate.calls += 1
        prev_hash = row.get("entry_hash", prev_hash)

    started = time.perf_counter()
    consecutive_errors = 0
    status = "completed"
    returned_models: set[str] = set()
    first_window = window

    for sample_id, text in pending:
        moment = datetime.now(llm_se.BEIJING)
        window, rate = llm_se.rate_for(moment)
        body = llm_se.request_body(sample_id, text)
        body_bytes = json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")
        tokens = llm_se.estimate_input_tokens(body)
        try:
            reservation = gate.reserve(tokens, rate, moment)
        except llm_se.BudgetExceeded as exc:
            status = f"budget_stopped: {exc}"
            break

        error = None
        content = ""
        usage: dict[str, Any] = {}
        decode: dict[str, Any] = {}
        try:
            response = transport.send(
                LLMRequest(
                    source_id=sample_id,
                    source_text=text,
                    system_prompt=body["messages"][0]["content"],
                    user_prompt=body["messages"][1]["content"],
                )
            )
            content = response.content or ""
            decode = getattr(transport, "last_decode", None) or {}
            usage = dict(decode.get("usage") or {})
        except Exception as exc:  # noqa: BLE001 - recorded, never retried
            error = f"{type(exc).__name__}: {exc}"
            consecutive_errors += 1

        actual = gate.settle(usage, rate, reservation)
        gate.calls += 1
        parsed = llm_se.extract_modality_label(content) if content else {
            "label": None,
            "status": "api_error",
            "clauses": 0,
        }
        returned = decode.get("model")
        if isinstance(returned, str) and returned:
            returned_models.add(returned)

        body_sha = sha256_bytes(body_bytes)
        record = {
            "sample_id": sample_id,
            "request_body_sha256": body_sha,
            "estimated_input_tokens": tokens,
            "price_window": window,
            "usage": usage,
            "cost_cny": actual,
            "request_status": "ok" if error is None else "error",
            "error": error,
            "parse_status": parsed["status"],
            "label": parsed["label"],
            "clauses": parsed["clauses"],
            "returned_model": returned,
            "response_sha256": sha256_bytes(content.encode("utf-8")),
            "provider_request_body_sha256": getattr(
                transport, "last_request_body_sha256", None
            ),
            "body_hash_match": getattr(
                transport, "last_request_body_sha256", None
            ) == body_sha,
            "timestamp_utc": now_utc(),
        }
        append_jsonl(response_path, record)
        entry = {
            "seq": gate.calls,
            "sample_id": sample_id,
            "request_body_sha256": record["request_body_sha256"],
            "cost_cny": actual,
            "cumulative_cny": round(gate.spent_cny, 6),
            "price_window": window,
            "request_status": record["request_status"],
            "prev_hash": prev_hash,
        }
        entry["entry_hash"] = sha256_bytes(
            json.dumps(entry, ensure_ascii=False, sort_keys=True).encode("utf-8")
        )
        prev_hash = entry["entry_hash"]
        append_jsonl(ledger_path, entry)

        if error is None:
            consecutive_errors = 0
        elif consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
            status = f"stopped_after_{consecutive_errors}_consecutive_errors"
            break

        if gate.calls % 25 == 0:
            print(
                f"[llm_se] {gate.calls}/{len(pairs)} spent={gate.spent_cny:.3f} CNY "
                f"window={window}",
                flush=True,
            )

    summary = {
        "schema_version": "sun_modality_llm_se_run@1.0.0",
        "run_id": run_dir.name,
        "status": status,
        "created_at": now_utc(),
        "calls": gate.calls,
        "planned_calls": len(pairs),
        "spent_cny": gate.spent_cny,
        "cap_cny": cap_cny,
        "reserve_output_tokens": reserve_out,
        "elapsed_seconds": time.perf_counter() - started,
        "returned_models": sorted(returned_models),
        "model_accepted": bool(returned_models) and returned_models <= ACCEPTED_MODELS,
        "first_price_window": first_window,
        "final_price_window": window,
        "price_rate": rate,
        "no_retry": True,
        "prompt_sha256": llm_se.PROMPT_SHA256,
        "body_hash_mismatch_count": sum(
            1 for row in read_jsonl(response_path) if row.get("body_hash_match") is False
        ),
    }
    write_json(run_dir / "llm_se_run.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if status == "completed" else 2


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--allow-peak", action="store_true")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--cap-cny", type=float, default=20.0)
    parser.add_argument("--reserve-output-tokens", type=int, default=1200)
    parser.add_argument("--simulate", type=int, default=0,
                        help="offline loop exercise with a simulated transport")
    args = parser.parse_args(argv)

    if not (args.preflight or args.execute):
        parser.error("choose --preflight or --execute")
    run_dir = OUTPUT_ROOT / args.run_id / "llm_se"
    run_dir.mkdir(parents=True, exist_ok=True)

    if args.preflight:
        return cmd_preflight(run_dir, args.cap_cny, args.reserve_output_tokens)
    return cmd_execute(
        run_dir, args.cap_cny, args.reserve_output_tokens, args.allow_peak,
        simulate=args.simulate,
    )


if __name__ == "__main__":
    raise SystemExit(main())
