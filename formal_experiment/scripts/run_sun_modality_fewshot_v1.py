"""Authorized, bounded few-shot execution; preserves the prepared request bytes.

The coordinator alone writes the journal and reserves budget. Workers each send
one request, without retries. No .env loading or held-out label access.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import prepare_sun_modality_fewshot_v1 as prepared
import run_sun_modality_boundary_v1 as base
from bpc_hybrid.modality_benchmark import boundary, data, fewshot, llm_se

AUTH = ROOT / "configs/authorization/sun_modality_fewshot_20261103_v1.json"
RUN = ROOT / "outputs/development/sun_modality_fewshot_v1/execution_v1"
PLAN = ROOT / "outputs/reports/sun_modality_fewshot_v1_execution_preflight.json"
JOURNAL = RUN / "local_only/events.jsonl"


def plan_payload() -> dict:
    auth = json.loads(AUTH.read_text(encoding="utf-8"))
    if (auth["execute_authorized"] is not True or auth["max_calls"] != 426
            or auth["cap_cny"] != 20.0 or auth["retries"] != 0
            or auth["max_workers"] != 8 or auth["off_peak_only"] is not True
            or auth["endpoint"] != "https://api.deepseek.com"
            or auth["model"] != llm_se.MODEL_ALIAS):
        raise ValueError("authorization does not match this bounded run")
    if boundary.digest(prepared.REPORT.read_bytes()) != auth["prepared_preflight_sha256"]:
        raise ValueError("prepared preflight differs from authorization")
    plan, _, _ = prepared.build_plan()
    frozen = json.loads(prepared.REPORT.read_text(encoding="utf-8"))
    if plan != frozen["payload"]:
        raise ValueError("prepared prompt/code/data drift")
    paths = ["scripts/run_sun_modality_fewshot_v1.py", "scripts/run_sun_modality_boundary_v1.py",
             "src/bpc_hybrid/llm_client.py", "src/bpc_hybrid/h1_transport.py",
             "src/bpc_hybrid/llm_config.py"]
    return {"authorization": auth, "authorization_sha256": boundary.digest(AUTH.read_bytes()),
            "prepared_payload_sha256": frozen["payload_sha256"],
            "requests": plan["requests"],
            "runtime_source_sha256_lf_utf8": {p: boundary.digest((ROOT / p).read_text(encoding="utf-8").encode()) for p in paths}}


def preflight() -> None:
    payload = plan_payload()
    block, _ = fewshot.load_demonstrations()
    total_input = sum(llm_se.estimate_input_tokens(fewshot.request_body(sid, text, block=block))
                      for sid, text in data.load_split_text_only("test"))
    old = boundary.read_events(ROOT / "outputs/development/sun_modality_boundary_v1/local_only/events.jsonl")
    completed = [x for x in old if x["kind"] == "finished"]
    mean_output = sum(x["usage"]["completion_tokens"] for x in completed) / len(completed)
    rate = payload["authorization"]["price_cny_per_million"]["off_peak"]
    estimate = (total_input * rate["input_cache_miss"] + 426 * mean_output * rate["output"]) / 1e6
    if PLAN.exists():
        if json.loads(PLAN.read_text(encoding="utf-8"))["payload"] != payload:
            raise ValueError("execution preflight is already frozen at another state")
    else:
        base.write_new(PLAN, {"created_at": base.now(), "payload": payload,
                              "estimated_cny_no_cache": estimate,
                              "estimate_note": "UTF-8 input estimate + historical mean output, not worst-case total; full per-call reservation enforced.",
                              "real_api_calls": 0})
    print(json.dumps({"calls": 426, "max_workers": 8, "estimated_cny_no_cache": estimate,
                      "cap_cny": 20, "preflight": str(PLAN), "real_api_calls": 0}), flush=True)


def usage_valid(usage: dict) -> bool:
    def nonnegative(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0
    if not all(nonnegative(usage.get(key)) for key in ("prompt_tokens", "completion_tokens")):
        return False
    for key in ("prompt_cache_hit_tokens", "prompt_cache_miss_tokens"):
        if key in usage and (not nonnegative(usage[key]) or usage[key] > usage["prompt_tokens"]):
            return False
    if all(key in usage for key in ("prompt_cache_hit_tokens", "prompt_cache_miss_tokens")):
        return usage["prompt_cache_hit_tokens"] + usage["prompt_cache_miss_tokens"] == usage["prompt_tokens"]
    return True


def send_one(config, sid: str, text: str, body: dict, request_hash: str, rate: dict) -> dict:
    from bpc_hybrid.h1_transport import H1RequestPolicy
    from bpc_hybrid.llm_client import LLMRequest, RealAPITransport
    transport = RealAPITransport(config, timeout_seconds=180,
        policy=H1RequestPolicy(stream=False, thinking={"type": "disabled"}, response_format=None))
    tick = time.monotonic()
    content, error, http_status = "", None, None
    try:
        response = transport.send(LLMRequest(source_id=sid, source_text=text,
            system_prompt=body["messages"][0]["content"], user_prompt=body["messages"][1]["content"]))
        content = response.content or ""
    except Exception as exc:
        error = type(exc).__name__
        http_status = getattr(exc.__cause__, "code", None)
    decoded = transport.last_decode or {}
    usage = decoded.get("usage") or {}
    usage_ok = usage_valid(usage)
    cost = llm_se.cost_cny(usage, rate) if usage_ok else 0.0
    parsed = llm_se.extract_modality_label(content) if content else {"label": None, "status": "no_content", "clauses": 0}
    model_ok = decoded.get("model") in base.ACCEPTED_MODELS
    body_ok = transport.last_request_body_sha256 == request_hash
    return {"kind": "finished", "sample_id": sid, "timestamp": base.now(),
            "request_sha256": request_hash, "body_hash_match": body_ok,
            "returned_model": decoded.get("model"), "model_accepted": model_ok,
            "request_status": "ok" if error is None else "error", "error_type": error,
            "http_status": http_status, "parse_status": parsed["status"],
            "label": parsed["label"] if model_ok and body_ok and error is None else None,
            "clauses": parsed["clauses"], "raw_content": content,
            "response_sha256": boundary.digest(content.encode()), "usage": usage,
            "usage_verified": usage_ok, "cost_cny": cost, "latency_seconds": time.monotonic() - tick}


def failed(row: dict) -> bool:
    return (row["request_status"] != "ok" or not row["usage_verified"]
            or not row["model_accepted"] or not row["body_hash_match"])


def execute() -> None:
    payload = plan_payload()
    if payload != json.loads(PLAN.read_text(encoding="utf-8"))["payload"]:
        raise ValueError("execution preflight drift")
    auth = payload["authorization"]
    block, _ = fewshot.load_demonstrations()
    pairs = data.load_split_text_only("test")
    expected = {x["sample_id"]: x["fewshot_request_sha256"] for x in payload["requests"]}
    if len(pairs) != len(expected) or {sid for sid, _ in pairs} != set(expected) or len(pairs) > auth["max_calls"]:
        raise ValueError("request membership exceeds or differs from authorization")
    config = base.environment_config()
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    lock = RUN / "execution.lock"
    os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    started_at = base.now()
    status = "completed"
    try:
        events = boundary.read_events(JOURNAL)
        attempted, spent, uncertain = boundary.accounting(events)
        if not attempted <= set(expected) or uncertain or any(failed(r) for r in events if r["kind"] == "finished"):
            raise ValueError("unexpected, unsettled, or failed prior request; automatic retry/resume forbidden")
        for row in events:
            if row["request_sha256"] != expected[row["sample_id"]]:
                raise ValueError("journal request binding mismatch")
        previous = events[-1]["event_hash"] if events else ""
        pending = iter([(sid, text) for sid, text in pairs if sid not in attempted])
        next_pair = next(pending, None)
        in_flight = {}
        finished_count = sum(r["kind"] == "finished" for r in events)
        with ThreadPoolExecutor(max_workers=auth["max_workers"]) as pool:
            while next_pair is not None or in_flight:
                while status == "completed" and next_pair is not None and len(in_flight) < auth["max_workers"]:
                    window, _ = llm_se.rate_for(datetime.now(llm_se.BEIJING))
                    if window != "off_peak":
                        status = "stopped_outside_off_peak"
                        break
                    sid, text = next_pair
                    body = fewshot.request_body(sid, text, block=block)
                    request_hash = boundary.digest(boundary.wire_bytes(body))
                    if request_hash != expected[sid]:
                        raise ValueError("request body drift")
                    rate = auth["price_cny_per_million"][window]
                    reservation = boundary.reserve_cost(body, rate)
                    held = sum(item[1] for item in in_flight.values())
                    if spent + held + reservation > auth["cap_cny"]:
                        # Wait for existing reservations to settle before refusing the next call.
                        if not in_flight:
                            status = "stopped_before_budget_exceeded"
                        break
                    previous = boundary.append_event(JOURNAL,
                        {"kind": "started", "sample_id": sid, "timestamp": base.now(),
                         "request_sha256": request_hash, "reserved_cny": reservation, "price_window": window}, previous)
                    attempted.add(sid)
                    future = pool.submit(send_one, config, sid, text, body, request_hash, rate)
                    in_flight[future] = (sid, reservation)
                    next_pair = next(pending, None)
                if not in_flight:
                    break
                done, _ = wait(in_flight, return_when=FIRST_COMPLETED)
                for future in done:
                    sid, reservation = in_flight.pop(future)
                    row = future.result()
                    if row["sample_id"] != sid:
                        raise ValueError("worker identity mismatch")
                    previous = boundary.append_event(JOURNAL, row, previous)
                    spent += row["cost_cny"]
                    finished_count += 1
                    if failed(row) or row["cost_cny"] > reservation:
                        status = "stopped_request_or_accounting_failure"
                    print(json.dumps({"finished": finished_count, "attempted": len(attempted),
                                      "total": len(pairs), "spent_cny": round(spent, 4),
                                      "parse": row["parse_status"], "status": row["request_status"]}), flush=True)
                if status != "completed":
                    next_pair = None  # drain already-issued requests, never start another
        summary = {"started_at": started_at, "finished_at": base.now(), "status": status,
                   "attempted": len(attempted), "finished": finished_count, "spent_cny": spent,
                   "cap_cny": auth["cap_cny"], "max_workers": auth["max_workers"],
                   "preflight_sha256": boundary.digest(PLAN.read_bytes()),
                   "authorization_sha256": payload["authorization_sha256"],
                   "journal_sha256": boundary.digest(JOURNAL.read_bytes()) if JOURNAL.exists() else None}
        base.write_new(RUN / ("execution_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + ".json"), summary)
        print(json.dumps(summary), flush=True)
    finally:
        lock.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    preflight() if args.preflight else execute()
