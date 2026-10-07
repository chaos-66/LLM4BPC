"""Finish Kimi's 145 never-sent IDs with RPM=3 pacing, without retrying the 429."""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bpc_hybrid import multi_model_stage2 as m
from bpc_hybrid.h1_transport import decode_chat_completion_envelope
from bpc_hybrid.sep_c3_modular_evaluation import attempt_rows, evaluate_coarse
import run_stage2_multi_model_remaining_v1 as parent

RUN_ID = "kimi_rpm_remaining_20261007_v1"
AUTH = "configs/authorization/stage2_kimi_rpm_remaining_20261007_v1.json"


def out_dir(root=ROOT):
    return root / "outputs/development/stage2_multi_model_remaining_v1" / RUN_ID


def report_path(root=ROOT, suffix=".json"):
    return root / "outputs/reports" / ("stage2_" + RUN_ID + suffix)


def parent_state(root):
    batch = m.read_json(parent.out_dir(root) / "plan.json")
    parent.verify(batch, root)
    bundle = batch["selected"]["kimi"]
    auth = {"authorized": True, "plan_sha256": m.digest(m.encode(bundle["plan"])),
            "budgets": {"kimi": bundle["budget"]}, "continuation_authorization": batch["authorization"]}
    out = parent.provider_dir("kimi", root)
    starts, finishes, head = m._load_ledger(out / "calls_ledger.jsonl", bundle["plan"])
    m._verify_saved_calls(out, bundle["plan"], auth, starts, finishes)
    saved = m.read_json(out / "manifest.json")
    if (len(starts) != 4 or set(starts) != set(finishes) or (out / ".run.lock").exists()
            or saved["status"] != "partial" or saved["llm_calls"] != 4
            or saved["plan_sha256"] != auth["plan_sha256"] or saved["authorization_sha256"] != m.digest(m.encode(auth))
            or saved["ledger_head_sha256"] != head
            or saved["predictions_sha256"] != m.digest((out / "predictions.json").read_bytes())):
        raise m.ModelRunError("Kimi父续跑必须为已结束的四次、完整且一致的证据。")
    attention = [f for f in finishes.values() if f["needs_attention"]]
    if len(attention) != 1:
        raise m.ModelRunError("只允许一个已保留的RPM失败，其余三条无未决异常。")
    error = m.read_json(out / attention[0]["response_path"])["error"]
    if not (error.startswith("HTTP 429:") and "rate_limit_reached_error" in error and "max RPM: 3" in error):
        raise m.ModelRunError("父失败不属于已确认每分钟三次限流。")
    paths = [parent.out_dir(root) / "plan.json", out / "manifest.json", out / "calls_ledger.jsonl", out / "predictions.json"]
    paths += [out / f["response_path"] for f in finishes.values()]
    return batch, bundle, starts, finishes, {p.relative_to(root).as_posix(): m.digest(p.read_bytes()) for p in paths}


def expected(root, prepared_at):
    auth = m.read_json(root / AUTH)
    required = {"authorized": True, "run_id": RUN_ID, "parent_run_id": parent.RUN_ID, "provider": "kimi",
                "max_new_calls": 145, "max_combined_calls": 900, "retry": 0,
                "max_output_tokens_per_call": 4096, "max_new_output_tokens": 145 * 4096,
                "min_start_interval_seconds": 21, "parent_cooldown_seconds": 65,
                "kimi_counter_policy_authorization": "接受，保留计数差异并继续 Kimi"}
    if any(auth.get(k) != v for k, v in required.items()):
        raise m.ModelRunError("Kimi未发送集合、145上限、授权或RPM节流不匹配。")
    batch, bundle, starts, finishes, bindings = parent_state(root)
    plan = copy.deepcopy(bundle["plan"])
    plan.update(run_id=RUN_ID, samples_per_provider=145, planned_calls=145,
                parent_plan_sha256=m.digest(m.encode(bundle["plan"])),
                requests=[r for r in bundle["plan"]["requests"] if r["request_id"] not in starts])
    budget = copy.deepcopy(bundle["budget"])
    spent = sum(f["reserved_cost"] for f in finishes.values())
    budget["max_cost"] -= spent
    if len(plan["requests"]) != 145 or sum(m._reservation(r, plan, budget) for r in plan["requests"]) > budget["max_cost"]:
        raise m.ModelRunError("Kimi尚未发送项或原剩余预算不足。")
    bindings.update({p: m.digest((root / p).read_bytes()) for p in (AUTH, "scripts/run_stage2_kimi_rpm_remaining_v1.py")})
    return {"run_id": RUN_ID, "task_id": parent.parent.TASK, "prepared_at_utc": prepared_at,
            "authorization": auth, "request_plan": plan, "budget": budget,
            "source_bindings": bindings, "parent_started_ids": list(starts),
            "parent_first_started_id": batch["parent_states"]["kimi"]["started_ids"][0],
            "parent_reserved_cost": spent, "kimi_counter_policy": batch["authorization"]["kimi_counter_exception"],
            "earliest_start_epoch": max(datetime.fromisoformat(s["timestamp_utc"]).timestamp() for s in starts.values()) + 65,
            "api_calls": 0, "metrics": None}


def prepare(root=ROOT):
    if out_dir(root).exists():
        raise m.ModelRunError("RPM续跑目录已存在；拒绝覆盖。")
    value = expected(root, m.now())
    m.write_json(out_dir(root) / "plan.json", value, exclusive=True)
    m.write_json(report_path(root, "_preflight.json"), value, exclusive=True)
    print(json.dumps({"prepared": RUN_ID, "never_sent_calls": 145, "api_calls": 0,
                      "min_start_interval_seconds": 21}), flush=True)
    return value


def verify(value, root):
    if m.encode(value) != m.encode(expected(root, value["prepared_at_utc"])):
        raise m.ModelRunError("RPM续跑绑定或父证据变化；拒绝读取key和发送。")


def wait_until(deadline, clock=time.time, sleeper=time.sleep):
    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            return
        sleeper(min(remaining, 21))


def ledger_auth(value):
    return {"authorized": True, "plan_sha256": m.digest(m.encode(value["request_plan"])),
            "budgets": {"kimi": value["budget"]}, "continuation_authorization": value["authorization"]}


def execute(root=ROOT, allow_llm=False, resume=False, sender=m.send_http,
            credential_loader=m.load_credentials, clock=time.time, sleeper=time.sleep):
    if not allow_llm:
        raise m.ModelRunError("真实RPM续跑须 --execute --allow-llm。")
    value = m.read_json(out_dir(root) / "plan.json")
    verify(value, root)
    plan, budget, out = value["request_plan"], value["budget"], out_dir(root)
    auth, ledger, lock = ledger_auth(value), out / "calls_ledger.jsonl", out / ".run.lock"
    if lock.exists() or (ledger.exists() and not resume):
        raise m.ModelRunError("RPM续跑已存在或有锁；拒绝重复调用。")
    starts, finishes, head = m._load_ledger(ledger, plan)
    m._verify_saved_calls(out, plan, auth, starts, finishes)
    if set(starts) != set(finishes) or any(f["needs_attention"] for f in finishes.values()):
        raise m.ModelRunError("已尝试的未决或异常请求禁止自动重发。")
    if list(out.glob("responses/*.json")) and not ledger.exists():
        raise m.ModelRunError("已有响应却缺少账本，拒绝发送。")
    if (out / "provider_manifest.json").exists() and not ledger.exists():
        raise m.ModelRunError("已有manifest却缺少账本，拒绝发送。")
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(fd)
    try:
        keys = credential_loader({"kimi": plan["profiles"]["kimi"]}, root) if len(starts) < 145 else {}
        spent = sum(f["reserved_cost"] for f in finishes.values())
        next_start = max([value["earliest_start_epoch"], *[
            datetime.fromisoformat(s["timestamp_utc"]).timestamp() + 21 for s in starts.values()]])
        began = clock()
        for request in plan["requests"]:
            rid = request["request_id"]
            if rid in starts:
                continue
            if rid in value["parent_started_ids"] or rid == value["parent_first_started_id"]:
                raise m.ModelRunError("父已发送ID禁止再次调用。")
            body, reserve = m.encode(request["body"]), m._reservation(request, plan, budget)
            if m.digest(body) != request["body_sha256"] or len(starts) >= 145 or spent + reserve > budget["max_cost"]:
                raise m.ModelRunError("请求字节或次数/原预算门禁失败。")
            wait_until(next_start, clock, sleeper)
            base = {"provider": "kimi", "request_id": rid, "sample_id": request["sample_id"],
                    "plan_sha256": auth["plan_sha256"], "body_sha256": request["body_sha256"],
                    "authorization_sha256": m.digest(m.encode(auth)), "timestamp_utc": datetime.fromtimestamp(clock(), timezone.utc).isoformat(),
                    "reserved_cost": reserve, "currency": budget["currency"]}
            head = m._append_ledger(ledger, {**base, "event": "started"}, head)
            starts[rid] = base
            next_start = clock() + 21
            raw_text, usage, returned, error = "", {}, None, None
            check, attention = {"status": "not_verified", "reported_reasoning_tokens": None}, False
            try:
                raw = sender(plan["profiles"]["kimi"], body, keys["kimi"], plan["timeout_seconds"])
                raw_text = raw.decode("utf-8", errors="replace")
                decoded = decode_chat_completion_envelope(raw)
                usage, returned = decoded.get("usage", {}), decoded.get("model")
                _, check, prediction = parent.parse_response(request, plan["profiles"]["kimi"], raw, value["authorization"])
                reserve = (usage["prompt_tokens"] * budget["input_per_million"] + usage["completion_tokens"] * budget["output_per_million"]) / 1_000_000
            except Exception as exc:
                attention = True
                error = str(exc) if isinstance(exc, m.ModelRunError) else "RPM续跑异常（" + type(exc).__name__ + "）。"
                prediction = {"provider": "kimi", "sample_id": request["sample_id"], "request_id": rid,
                              "request_status": "failed", "failure_stage": "transport_or_usage", "record": {}}
            response = out / "responses" / ("kimi_" + request["sample_id"] + ".json")
            m.write_json(response, m.redact({"request_id": rid, "raw_response_utf8": raw_text,
                "usage": usage, "returned_model": returned, "nonthinking_check": check,
                "error": error, "prediction": prediction}, list(keys.values())), exclusive=True)
            finish = {**base, "event": "finished", "timestamp_utc": m.now(), "reserved_cost": reserve,
                      "needs_attention": attention, "response_path": response.relative_to(out).as_posix(),
                      "response_sha256": m.digest(response.read_bytes()), "request_status": prediction["request_status"]}
            head = m._append_ledger(ledger, finish, head)
            finishes[rid] = finish
            spent += reserve
            if attention:
                break
        rows = [m.read_json(out / finishes[r["request_id"]]["response_path"])["prediction"]
                if r["request_id"] in finishes else {"provider": "kimi", "sample_id": r["sample_id"],
                "request_id": r["request_id"], "request_status": "not_attempted", "record": {}} for r in plan["requests"]]
        m.write_json(out / "predictions.json", {"records": rows, "claim_scope": "development_only"})
        result = {"run_id": RUN_ID, "status": "succeeded" if len(finishes) == 145 and not any(f["needs_attention"] for f in finishes.values()) else "partial",
                  "llm_calls": len(starts), "plan_sha256": auth["plan_sha256"], "authorization_sha256": m.digest(m.encode(auth)),
                  "ledger_head_sha256": head, "predictions_sha256": m.digest((out / "predictions.json").read_bytes()),
                  "conservative_uncached_cost": spent, "valid_predictions": sum(r["request_status"] == "ok" for r in rows),
                  "retry": 0, "runtime_seconds": round(clock() - began, 3), "min_start_interval_seconds": 21}
        m.write_json(out / "provider_manifest.json", result)
        return result
    finally:
        lock.unlink(missing_ok=True)


def summarize(root=ROOT):
    value = m.read_json(out_dir(root) / "plan.json")
    verify(value, root)
    parent_manifest = m.read_json(parent.out_dir(root) / "manifest.json")
    for relative, sha in parent_manifest["artifacts"].items():
        if m.digest((root / relative).read_bytes()) != sha:
            raise m.ModelRunError("三家父续跑结果改变，拒绝合并。")
    report = copy.deepcopy(m.read_json(parent.report_path(root)))
    plan = value["request_plan"]
    starts, finishes, head = m._load_ledger(out_dir(root) / "calls_ledger.jsonl", plan)
    m._verify_saved_calls(out_dir(root), plan, ledger_auth(value), starts, finishes)
    saved = m.read_json(out_dir(root) / "provider_manifest.json")
    if (saved["ledger_head_sha256"] != head or saved["llm_calls"] != len(starts)
            or saved["plan_sha256"] != m.digest(m.encode(plan))
            or saved["authorization_sha256"] != m.digest(m.encode(ledger_auth(value)))
            or saved["predictions_sha256"] != m.digest((out_dir(root) / "predictions.json").read_bytes())):
        raise m.ModelRunError("RPM续跑manifest不一致。")
    rows = m.read_json(parent.provider_dir("kimi", root) / "combined_predictions.json")["records"]
    new = {r["sample_id"]: r for r in m.read_json(out_dir(root) / "predictions.json")["records"]}
    combined = [new.get(r["sample_id"], r) for r in rows]
    if len(combined) != 150 or len({r["sample_id"] for r in combined}) != 150:
        raise m.ModelRunError("Kimi合并必须保留相同150分母。")
    m.write_json(out_dir(root) / "combined_predictions.json", {"records": combined, "claim_scope": "development_only"})
    row = report["providers"]["kimi"]
    row["attempted"] += len(starts)
    row["valid_predictions"] = sum(r["request_status"] == "ok" for r in combined)
    usage = [m.read_json(out_dir(root) / f["response_path"])["usage"] for f in finishes.values()]
    row["input_tokens"] += sum(u.get("prompt_tokens", 0) for u in usage)
    row["output_tokens"] += sum(u.get("completion_tokens", 0) for u in usage)
    row["conservative_uncached_cost"] += saved["conservative_uncached_cost"]
    if saved["status"] == "succeeded" and len(starts) == 145:
        row["status"] = "succeeded"
        gold = m.read_json(root / parent.parent.GOLD)
        evaluation = evaluate_coarse(gold, attempt_rows(combined), method_id="multi_model_kimi")
        evaluation["primary_metric"] = report["primary_metric"]
        m.write_json(out_dir(root) / "evaluation.json", evaluation)
        row["metrics"] = {"overall": evaluation["coarse_five_field_micro"], "per_field": evaluation["five_fields"],
                          "modality_macro_f1": evaluation["modality_labels"]["macro_f1"], "failed_count": evaluation["failed_count"]}
    report.update(run_id=RUN_ID, parent_run_id=parent.RUN_ID, actual_calls=report["actual_calls"] + len(starts),
                  actual_new_calls=report["actual_new_calls"] + len(starts), actual_new_calls_in_run=len(starts),
                  status="succeeded" if all(r["status"] == "succeeded" for r in report["providers"].values()) else "partial")
    if report["actual_calls"] > 900 or report["actual_new_calls"] > 447:
        raise m.ModelRunError("合并调用数超出原授权。")
    report["limitations"].append("Kimi一次HTTP429/RPM=3保留失败且不重发；其余145个未发送项开始间隔至少21秒，0重试。")
    m.write_json(report_path(root), report)
    lines = ["# 六家非思考模型比较：充值与Kimi节流后合并结果", "", f"状态{report['status']}；合计{report['actual_calls']}/900，追加{report['actual_new_calls']}/447，0重试。", "",
             "| 平台 | 模型 | 调用 | 有效 | P | R | F1 | 失败 |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for name, row in report["providers"].items():
        metric = row["metrics"]
        scores = " | ".join(f"{metric['overall'][k]:.4f}" for k in ("precision", "recall", "f1")) if metric else "null | null | null"
        lines.append(f"| {name} | {row['model']} | {row['attempted']} | {row['valid_predictions']} | {scores} | {metric['failed_count'] if metric else '未完成'} |")
    lines += ["", *["- " + s for s in report["limitations"]]]
    report_path(root, ".md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    artifacts = {p.relative_to(root).as_posix(): m.digest(p.read_bytes()) for p in out_dir(root).rglob("*.json*") if p != out_dir(root) / "manifest.json"}
    for p in (report_path(root), report_path(root, ".md")):
        artifacts[p.relative_to(root).as_posix()] = m.digest(p.read_bytes())
    manifest = {"task_id": parent.parent.TASK, "run_id": RUN_ID, "status": report["status"],
                "source_bindings": value["source_bindings"], "parent_manifest_sha256": m.digest((parent.out_dir(root) / "manifest.json").read_bytes()),
                "new_calls": len(starts), "combined_calls": report["actual_calls"], "retry": 0, "artifacts": artifacts}
    m.write_json(out_dir(root) / "manifest.json", manifest)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--summarize", action="store_true")
    parser.add_argument("--allow-llm", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.execute:
        result = execute(allow_llm=args.allow_llm, resume=args.resume)
        print(json.dumps(result), flush=True)
        if (parent.out_dir() / "manifest.json").exists():
            summarize()
    elif args.summarize:
        print(json.dumps({"status": summarize()["status"]}), flush=True)
    else:
        prepare()


if __name__ == "__main__":
    main()
