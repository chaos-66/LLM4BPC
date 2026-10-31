"""Frozen v6 + modality boundary guidance; exploratory historical paired control.

--preflight: offline, no credentials. --execute: at most 426 requests / CNY 20.
--report: offline aggregation of saved responses. Never loads a .env file.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bpc_hybrid.modality_benchmark import boundary, data, llm_se
from bpc_hybrid.modality_benchmark.metrics import LABELS, evaluate

RUN = ROOT / "outputs/development/sun_modality_boundary_v1"
PLAN = RUN / "preflight.json"
JOURNAL = RUN / "local_only/events.jsonl"
REPORT = ROOT / "outputs/reports/sun_modality_boundary_v1"
ACCEPTED_MODELS = {"deepseek-v4-pro", "DeepSeek-V4-Pro-0813"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_new(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def plan_payload() -> dict[str, Any]:
    contract = boundary.read_contract()
    pairs = data.load_split_text_only("test")
    paths = ["scripts/run_sun_modality_boundary_v1.py",
             "src/bpc_hybrid/modality_benchmark/boundary.py",
             "src/bpc_hybrid/modality_benchmark/llm_se.py",
             "src/bpc_hybrid/modality_benchmark/data.py",
             "src/bpc_hybrid/modality_benchmark/metrics.py",
             "src/bpc_hybrid/llm_client.py", "src/bpc_hybrid/h1_transport.py",
             "src/bpc_hybrid/llm_config.py", "src/bpc_hybrid/prompt_loader.py"]
    requests = []
    for sid, text in pairs:
        body = boundary.request_body(sid, text)
        requests.append({"sample_id": sid,
                         "request_sha256": boundary.digest(boundary.wire_bytes(body)),
                         "estimated_input_tokens": llm_se.estimate_input_tokens(body)})
    for key in ("historical_llm", "historical_sun", "historical_report"):
        spec = contract[key]
        if boundary.digest((ROOT / spec["path"]).read_bytes()) != spec["sha256"]:
            raise ValueError("historical evidence drift: " + key)
    return {"contract": contract, "requests": requests,
            "source_sha256_lf_utf8": {p: boundary.digest((ROOT / p).read_text(encoding="utf-8").encode())
                                      for p in paths},
            "test_sha256": data.EXPECTED["test"]["sha256"],
            "max_calls": contract["max_calls"], "cap_cny": contract["cap_cny"],
            "sampling": {"temperature": 0, "top_p": 1, "max_tokens": 4096,
                         "thinking": "disabled", "retry": 0}}


def preflight() -> None:
    plan = plan_payload()
    tokens = sum(x["estimated_input_tokens"] for x in plan["requests"])
    old = read_jsonl(ROOT / plan["contract"]["historical_llm"]["path"])
    mean_out = sum(x["usage"]["completion_tokens"] for x in old) / len(old)
    rate = plan["contract"]["price_cny_per_million"]["off_peak"]
    estimate = (tokens * rate["input_cache_miss"] + len(old) * mean_out * rate["output"]) / 1e6
    doc = {"created_at": now(), "payload": plan,
           "payload_sha256": boundary.digest(json.dumps(plan, sort_keys=True, ensure_ascii=False).encode()),
           "expected_cost_cny_no_cache": estimate,
           "estimate_note": "参考旧臂平均输出长度的估算，不是最坏总价；每次发送前预留完整4096输出额度。",
           "claim_scope": "test-informed exploratory comparison; historical control, not concurrent A/B",
           "real_api_calls": 0}
    if PLAN.exists():
        existing = json.loads(PLAN.read_text(encoding="utf-8"))
        if existing["payload"] != plan:
            raise ValueError("preflight already frozen at a different state")
    else:
        write_new(PLAN, doc)
    print(json.dumps({"preflight": str(PLAN), "calls": len(plan["requests"]),
                      "estimated_cny": round(estimate, 4), "cap_cny": plan["cap_cny"],
                      "real_api_calls": 0}, ensure_ascii=False), flush=True)


def environment_config():
    from bpc_hybrid.llm_config import LLMConfig
    # Explicit process-environment credentials for the official provider only.
    # No profile loader, .env fallback, endpoint override, or key output.
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("DEEPSEEK_API_KEY is absent from the process environment")
    config = LLMConfig(enabled=True, provider="openai_compatible", model=llm_se.MODEL_ALIAS,
                       api_key=key, base_url="https://api.deepseek.com", timeout_seconds=180,
                       temperature=0.0, top_p=1.0, max_tokens=4096)
    config.validate()
    return config


def execute() -> None:
    from bpc_hybrid.h1_transport import H1RequestPolicy
    from bpc_hybrid.llm_client import LLMRequest, RealAPITransport
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    payload = plan_payload()
    if payload != plan["payload"]:
        raise ValueError("preflight does not bind the current code/prompt/data")
    contract = payload["contract"]
    if not contract["authorization"]["execute_requested"]:
        raise ValueError("execution is not authorized")
    config = environment_config()
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    lock = RUN / "execution.lock"
    # Exclusive process lock prevents simultaneous sends from duplicate launches.
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(descriptor)
    status, started_at = "completed", now()
    try:
        events = boundary.read_events(JOURNAL)
        attempted, spent, uncertain = boundary.accounting(events)
        pairs = data.load_split_text_only("test")
        known = {sid for sid, _ in pairs}
        if not attempted <= known or len(attempted) > contract["max_calls"]:
            raise ValueError("unexpected journal population")
        if uncertain:
            raise ValueError("unsettled request exists; automatic retry/resume forbidden")
        previous = events[-1]["event_hash"] if events else ""
        expected = {x["sample_id"]: x["request_sha256"] for x in payload["requests"]}
        for sid, text in pairs:
            if sid in attempted:
                continue
            moment = datetime.now(llm_se.BEIJING)
            window, _ = llm_se.rate_for(moment)
            if window != "off_peak":
                status = "stopped_outside_off_peak"
                break
            rate = contract["price_cny_per_million"][window]
            body = boundary.request_body(sid, text)
            request_hash = boundary.digest(boundary.wire_bytes(body))
            if request_hash != expected[sid]:
                raise ValueError("request body drift")
            reservation = boundary.reserve_cost(body, rate)
            if spent + reservation > contract["cap_cny"]:
                status = "stopped_before_budget_exceeded"
                break
            previous = boundary.append_event(JOURNAL,
                {"kind": "started", "sample_id": sid, "timestamp": now(),
                 "request_sha256": request_hash, "reserved_cny": reservation,
                 "price_window": window}, previous)
            attempted.add(sid)
            transport = RealAPITransport(config, timeout_seconds=180,
                policy=H1RequestPolicy(stream=False, thinking={"type": "disabled"}, response_format=None))
            tick = time.monotonic()
            content, error, http_status = "", None, None
            try:
                response = transport.send(LLMRequest(source_id=sid, source_text=text,
                    system_prompt=body["messages"][0]["content"],
                    user_prompt=body["messages"][1]["content"]))
                content = response.content or ""
            except Exception as exc:
                # Retain safe error class/status, never raw exception repr/body/headers.
                error = type(exc).__name__
                http_status = getattr(exc.__cause__, "code", None)
            decoded = transport.last_decode or {}
            usage = decoded.get("usage") or {}
            usage_ok = all(isinstance(usage.get(k), (int, float)) and usage[k] >= 0
                           for k in ("prompt_tokens", "completion_tokens"))
            cost = llm_se.cost_cny(usage, rate) if usage_ok else 0.0
            spent += cost
            parsed = llm_se.extract_modality_label(content) if content else {
                "label": None, "status": "no_content", "clauses": 0}
            model_ok = decoded.get("model") in ACCEPTED_MODELS
            body_ok = transport.last_request_body_sha256 == request_hash
            row = {"kind": "finished", "sample_id": sid, "timestamp": now(),
                   "request_sha256": request_hash, "body_hash_match": body_ok,
                   "returned_model": decoded.get("model"), "model_accepted": model_ok,
                   "request_status": "ok" if error is None else "error", "error_type": error,
                   "http_status": http_status, "parse_status": parsed["status"],
                   "label": parsed["label"] if model_ok and body_ok and error is None else None,
                   "clauses": parsed["clauses"], "raw_content": content,
                   "response_sha256": boundary.digest(content.encode()),
                   "usage": usage, "usage_verified": usage_ok, "cost_cny": cost,
                   "latency_seconds": time.monotonic() - tick}
            previous = boundary.append_event(JOURNAL, row, previous)
            print(json.dumps({"finished": len(attempted), "total": len(pairs),
                              "spent_cny": round(spent, 4), "status": row["request_status"],
                              "parse": parsed["status"], "http_status": http_status}), flush=True)
            if error or not usage_ok or not model_ok or not body_ok or cost > reservation:
                status = "stopped_request_or_accounting_failure"
                break
        summary = {"started_at": started_at, "finished_at": now(), "status": status,
                   "attempted": len(attempted), "spent_cny": spent, "cap_cny": contract["cap_cny"],
                   "preflight_sha256": boundary.digest(PLAN.read_bytes()),
                   "journal_sha256": boundary.digest(JOURNAL.read_bytes()) if JOURNAL.exists() else None}
        write_new(RUN / ("execution_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + ".json"), summary)
        print(json.dumps(summary, ensure_ascii=False), flush=True)
    finally:
        lock.unlink()


def report() -> None:
    contract = boundary.read_contract()
    # Evaluation reads labels ONLY after inference. This command never sends requests.
    rows = data.load_split("test")
    order, gold = [x.sample_id for x in rows], [x.label for x in rows]
    events = boundary.read_events(JOURNAL)
    attempted, cost, uncertain = boundary.accounting(events)
    finished = {x["sample_id"]: x for x in events if x["kind"] == "finished"}
    baseline = {x["sample_id"]: x["label"] for x in read_jsonl(ROOT / contract["historical_llm"]["path"])}
    sun = {x["sample_id"]: x["predicted"] for x in read_jsonl(ROOT / contract["historical_sun"]["path"])}
    variant = {sid: x["label"] for sid, x in finished.items()}
    completed = len(attempted) == len(finished) == len(order)
    metrics = {name: evaluate(gold, [preds.get(sid) for sid in order])
               for name, preds in (("baseline", baseline), ("boundary", variant), ("sun", sun))}
    transitions = {label: {"corrected": 0, "regressed": 0, "both_correct": 0, "both_wrong": 0}
                   for label in LABELS}
    for sid, g in zip(order, gold):
        a, b = baseline.get(sid) == g, variant.get(sid) == g
        key = "both_correct" if a and b else "corrected" if b else "regressed" if a else "both_wrong"
        transitions[g][key] += 1
    result = {"suite_id": contract["suite_id"], "created_at": now(),
              "claim_scope": contract["claim_scope"], "completed": completed,
              "attempted": len(attempted), "finished": len(finished),
              "uncalled": len(order) - len(attempted), "actual_known_cost_cny": cost,
              "unsettled_reservation_cny": uncertain, "metrics": metrics,
              "paired_correctness_by_gold_class": transitions,
              "contract": contract, "preflight_sha256": boundary.digest(PLAN.read_bytes()),
              "journal_sha256": boundary.digest(JOURNAL.read_bytes()) if JOURNAL.exists() else None,
              "limitations": ["看过该测试集错误后设计的探索性分支，不是独立盲测。",
                              "旧v6和Sun使用历史预测，未做同期基线重跑；模型服务的时间差仍可能影响对照。",
                              "只追加四类边界说明；模型、输入、采样、六要素JSON和首个clause口径保持一致。",
                              "未调用和失败均计入426分母；不替换原补充表或论文主表。"]}
    if not completed:
        result["limitations"].append("本次未完整执行，boundary分数仅为缺失计失败的进度诊断，不能作效果结论。")
    write_new(REPORT.with_suffix(".json"), result)
    lines = ["# 四类 modality 边界提示词分支（探索性对照）", "",
             f"- 完成：{completed}；调用 {len(attempted)}/426；已知费用 ¥{cost:.4f}；未结算预留 ¥{uncertain:.4f}。",
             "- 只新增四类语义边界与否定范围说明；原v6提示词保持冻结。", "",
             "| 方法 | Accuracy | Macro-F1 | definition F1 | obligation F1 | permission F1 | prohibition F1 |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for key, label in (("baseline", "原v6（历史）"), ("boundary", "v6＋边界说明"), ("sun", "Sun（历史）")):
        m = metrics[key]
        values = [m["accuracy"], m["macro_f1"]] + [m["per_class"][c]["f1"] for c in LABELS]
        lines.append("| " + label + " | " + " | ".join(f"{v:.4f}" for v in values) + " |")
    lines += ["", "| 类别 | 原v6 P/R | 分支 P/R | 原v6 FP | 分支 FP | 改对 | 改错 |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for cls in LABELS:
        a, b = metrics["baseline"]["per_class"][cls], metrics["boundary"]["per_class"][cls]
        t = transitions[cls]
        lines.append(f"| {cls} | {a['precision']:.4f}/{a['recall']:.4f} | {b['precision']:.4f}/{b['recall']:.4f} | {a['fp']} | {b['fp']} | {t['corrected']} | {t['regressed']} |")
    lines += [""] + ["- " + note for note in result["limitations"]]
    with REPORT.with_suffix(".md").open("x", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    print(json.dumps({"report": str(REPORT), "completed": completed, "calls": len(attempted),
                      "macro_f1": metrics["boundary"]["macro_f1"], "cost_cny": cost}), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--report", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        preflight()
    elif args.execute:
        execute()
    else:
        report()


if __name__ == "__main__":
    main()
