"""Four authorized structural-feedback requests; preserve both preceding result versions."""
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
from bpc_hybrid.sep_c3_modular_evaluation import attempt_rows, evaluate_coarse
import run_stage2_model_output_recovery_v1 as parent

RUN_ID = "structural_feedback_20261007_v1"
TASK = "S2-MODEL-STRUCTURAL-FEEDBACK-V1"
AUTH = "configs/authorization/stage2_structural_feedback_20261007_v1.json"
PREVIEW = "outputs/reports/stage2_model_output_recovery_20261007_v1_remaining4_preflight.json"
DECISION = "授权4次带错误反馈补跑（推荐）"


def out_dir(root=ROOT):
    return root / "outputs/development/stage2_multi_model_remaining_v1" / RUN_ID


def report_path(root=ROOT, suffix=".json"):
    return root / "outputs/reports" / ("stage2_" + RUN_ID + suffix)


def expected(root, prepared_at):
    auth, preview = m.read_json(root / AUTH), m.read_json(root / PREVIEW)
    required = {"authorized": True, "run_id": RUN_ID, "decision": DECISION, "max_new_calls": 4,
                "max_combined_calls": 922, "max_new_output_tokens": 16384, "max_output_tokens_per_call": 4096,
                "retry": 0, "currency_caps": {"CNY": 0.99}, "kimi_min_start_interval_seconds": 21,
                "kimi_counter_policy_authorization": "接受，保留计数差异并继续 Kimi"}
    if any(auth.get(k) != v for k, v in required.items()) or auth.get("preview_sha256") != m.digest((root / PREVIEW).read_bytes()):
        raise m.ModelRunError("4次新授权、费用或预检绑定不匹配。")
    previous = m.read_json(parent.out_dir(root) / "plan.json")
    parent.verify(previous, root)
    mf_path = parent.out_dir(root) / "manifest.json"
    mf, report = m.read_json(mf_path), m.read_json(parent.report_path(root))
    if (parent.out_dir(root) / ".run.lock").exists() or mf["status"] != "succeeded" or mf["combined_calls"] != 918 or report["actual_calls"] != 918:
        raise m.ModelRunError("必须继承已关闭918次父结果。")
    bindings = {}
    for relative, sha in mf["artifacts"].items():
        if m.digest((root / relative).read_bytes()) != sha:
            raise m.ModelRunError("父恢复产物变化：" + relative)
        bindings[relative] = sha
    bindings[mf_path.relative_to(root).as_posix()] = m.digest(mf_path.read_bytes())
    if bindings[mf_path.relative_to(root).as_posix()] != preview["parent_manifest_sha256"]:
        raise m.ModelRunError("剩余4项预检父manifest变化。")
    failed = {(r["provider"], r["sample_id"]) for r in report["remaining_failures"]}
    profiles, budgets, requests, seen = {}, {}, [], set()
    for entry in preview["requests"]:
        name, sid = entry["provider"], entry["sample_id"]
        bundle = previous["selected"][name]
        original = next(r for r in bundle["plan"]["requests"] if r["sample_id"] == sid)
        request = entry["request"]
        body = request["body"]
        if ((name, sid) not in failed or (name, sid) in seen or entry["profile"] != bundle["plan"]["profiles"][name]
                or len(body["messages"]) != len(original["body"]["messages"]) + 1
                or body["messages"][:-1] != original["body"]["messages"]
                or {k: v for k, v in body.items() if k != "messages"} != {k: v for k, v in original["body"].items() if k != "messages"}
                or {k: v for k, v in request.items() if k not in ("body", "body_sha256", "input_token_reservation")} != {k: v for k, v in original.items() if k not in ("body", "body_sha256", "input_token_reservation")}
                or m.digest(m.encode(body)) != request["body_sha256"] or request["input_token_reservation"] != len(m.encode(body)) + 4096):
            raise m.ModelRunError("只允许剩余4原失败与预检冻结的单条合同反馈。")
        path = root / entry["parent_failed_response_path"]
        if m.digest(path.read_bytes()) != entry["parent_failed_response_sha256"]:
            raise m.ModelRunError("反馈所据父响应改变。")
        seen.add((name, sid))
        profiles[name] = entry["profile"]
        budgets[name] = copy.deepcopy(bundle["budget"])
        requests.append(request)
    if seen != failed or len(requests) != 4:
        raise m.ModelRunError("请求必须恰覆盖4个失败。")
    plan = {"run_id": RUN_ID, "requests": requests, "profiles": profiles, "planned_calls": 4,
            "max_output_tokens_per_call": 4096, "retry": 0, "timeout_seconds": 180}
    for name, budget in budgets.items():
        budget["max_cost"] = sum(m._reservation(r, plan, budget) for r in requests if r["provider"] == name)
    if sum(b["max_cost"] for b in budgets.values()) > .99 or any(b["currency"] != "CNY" for b in budgets.values()):
        raise m.ModelRunError("新人民币费用保护不足。")
    for path in (AUTH, PREVIEW, "scripts/run_stage2_structural_feedback_v1.py"):
        bindings[path] = m.digest((root / path).read_bytes())
    return {"run_id": RUN_ID, "task_id": TASK, "prepared_at_utc": prepared_at, "authorization": auth,
            "request_plan": plan, "budgets": budgets, "source_bindings": bindings, "api_calls": 0, "metrics": None}


def prepare(root=ROOT):
    if out_dir(root).exists():
        raise m.ModelRunError("新反馈目录已存在，拒绝覆盖。")
    value = expected(root, m.now())
    m.write_json(out_dir(root) / "plan.json", value, exclusive=True)
    m.write_json(report_path(root, "_preflight.json"), value, exclusive=True)
    print(json.dumps({"prepared": RUN_ID, "new_calls": 4, "api_calls": 0}), flush=True)
    return value


def verify(value, root):
    if m.encode(value) != m.encode(expected(root, value["prepared_at_utc"])):
        raise m.ModelRunError("新绑定改变，拒绝读取密钥和发送。")


def ledger_auth(value):
    return {"authorized": True, "plan_sha256": m.digest(m.encode(value["request_plan"])),
            "budgets": value["budgets"], "feedback_authorization": value["authorization"]}


def execute(root=ROOT, allow_llm=False, sender=m.send_http, credential_loader=m.load_credentials,
            clock=time.time, sleeper=time.sleep):
    if not allow_llm:
        raise m.ModelRunError("真实反馈补跑须 --execute --allow-llm。")
    out = out_dir(root)
    value = m.read_json(out / "plan.json")
    verify(value, root)
    plan, auth = value["request_plan"], ledger_auth(value)
    ledger, lock = out / "calls_ledger.jsonl", out / ".run.lock"
    if lock.exists() or ledger.exists() or (out / "run_result.json").exists() or list(out.glob("responses/*.json")):
        raise m.ModelRunError("已尝试反馈批次禁止再次调用。")
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(fd)
    try:
        keys = credential_loader(plan["profiles"], root)
        began, next_kimi, spent, head = clock(), 0.0, 0.0, ""
        rows, calls, attention = [], 0, False
        for request in plan["requests"]:
            name = request["provider"]
            budget, body = value["budgets"][name], m.encode(request["body"])
            reserve = m._reservation(request, plan, budget)
            if calls >= 4 or spent + reserve > .99 or m.digest(body) != request["body_sha256"]:
                raise m.ModelRunError("次数、费用或请求字节门禁失败。")
            if name == "kimi":
                parent.final.wait_until(next_kimi, clock, sleeper)
            base = {"provider": name, "request_id": request["request_id"], "sample_id": request["sample_id"],
                    "plan_sha256": auth["plan_sha256"], "body_sha256": request["body_sha256"],
                    "authorization_sha256": m.digest(m.encode(auth)), "timestamp_utc": datetime.fromtimestamp(clock(), timezone.utc).isoformat(),
                    "reserved_cost": reserve, "currency": "CNY"}
            head = m._append_ledger(ledger, {**base, "event": "started"}, head)
            calls += 1
            if name == "kimi":
                next_kimi = clock() + 21
            raw_text, usage, returned, error, audit = "", {}, None, None, None
            check = {"status": "not_verified", "reported_reasoning_tokens": None}
            try:
                raw = sender(plan["profiles"][name], body, keys[name], 180)
                raw_text = raw.decode("utf-8", errors="replace")
                decoded, check, prediction, audit = parent.parse_response(request, plan["profiles"][name], raw, value["authorization"])
                usage, returned = decoded["usage"], decoded["model"]
                reserve = (usage["prompt_tokens"] * budget["input_per_million"] + usage["completion_tokens"] * budget["output_per_million"]) / 1_000_000
            except Exception as exc:
                attention = True
                error = str(exc) if isinstance(exc, m.ModelRunError) else "结构反馈异常（" + type(exc).__name__ + "）。"
                prediction = {"provider": name, "sample_id": request["sample_id"], "request_id": request["request_id"],
                              "request_status": "failed", "failure_stage": "transport_or_usage", "record": {}}
            path = out / "responses" / (name + "_" + request["sample_id"] + ".json")
            m.write_json(path, m.redact({"request_id": request["request_id"], "raw_response_utf8": raw_text, "usage": usage,
                         "returned_model": returned, "nonthinking_check": check, "error": error, "prediction": prediction,
                         "echo_recovery_audit": audit}, list(keys.values())), exclusive=True)
            head = m._append_ledger(ledger, {**base, "event": "finished", "timestamp_utc": m.now(), "reserved_cost": reserve,
                   "needs_attention": attention, "response_path": path.relative_to(out).as_posix(),
                   "response_sha256": m.digest(path.read_bytes()), "request_status": prediction["request_status"]}, head)
            spent += reserve
            rows.append(prediction)
            print(json.dumps({"provider": name, "sample_id": request["sample_id"], "status": prediction["request_status"],
                              "failure_stage": prediction.get("failure_stage"), "calls": calls}), flush=True)
            if attention:
                break
        m.write_json(out / "predictions.json", {"records": rows, "claim_scope": "development_only"}, exclusive=True)
        result = {"status": "succeeded" if calls == 4 and not attention else "partial", "llm_calls": calls,
                  "plan_sha256": auth["plan_sha256"], "authorization_sha256": m.digest(m.encode(auth)), "ledger_head_sha256": head,
                  "predictions_sha256": m.digest((out / "predictions.json").read_bytes()), "conservative_uncached_cost": spent,
                  "runtime_seconds": round(clock() - began, 3), "retry": 0}
        m.write_json(out / "run_result.json", result, exclusive=True)
    finally:
        lock.unlink(missing_ok=True)
    return summarize(root)


def summarize(root=ROOT):
    out = out_dir(root)
    if (out / ".run.lock").exists() or (out / "manifest.json").exists():
        raise m.ModelRunError("运行未关闭或已汇总，拒绝覆盖。")
    value = m.read_json(out / "plan.json")
    verify(value, root)
    plan, auth = value["request_plan"], ledger_auth(value)
    starts, finishes, head = m._load_ledger(out / "calls_ledger.jsonl", plan)
    m._verify_saved_calls(out, plan, auth, starts, finishes)
    result = m.read_json(out / "run_result.json")
    if (set(starts) != set(finishes) or result["llm_calls"] != len(starts) or result["ledger_head_sha256"] != head
            or result["plan_sha256"] != auth["plan_sha256"] or result["authorization_sha256"] != m.digest(m.encode(auth))
            or result["predictions_sha256"] != m.digest((out / "predictions.json").read_bytes())):
        raise m.ModelRunError("反馈调用证据不一致。")
    report = copy.deepcopy(m.read_json(parent.report_path(root)))
    previous_cost = report["additional_costs"]
    report.update(schema_version="stage2_structural_feedback_result@1.0.0", run_id=RUN_ID, task_id=TASK,
                  parent_run_id=parent.RUN_ID, condition="source_echo_recovery_original_supplement_then_structural_feedback",
                  planned_calls=922, planned_new_calls=4, actual_calls=918 + len(starts), actual_new_calls_in_run=len(starts),
                  status=result["status"], additional_costs={"CNY": result["conservative_uncached_cost"]},
                  previous_supplementary_costs=previous_cost, combined_supplementary_costs={"CNY": previous_cost["CNY"] + result["conservative_uncached_cost"], "USD": previous_cost["USD"]},
                  offline_recoveries_in_run=0, remaining_failures=[], execution=result)
    if report["actual_calls"] > 922 or result["conservative_uncached_cost"] > .99:
        raise m.ModelRunError("新调用或费用超过4次/CNY0.99。")
    patches = {(r["provider"], r["sample_id"]): r for r in m.read_json(out / "predictions.json")["records"]}
    all_rows = {}
    for name in parent.COUNTS:
        rows = m.read_json(parent.out_dir(root) / name / "combined_predictions.json")["records"]
        combined = [patches.get((name, r["sample_id"]), r) for r in rows]
        if len(combined) != 150 or [r["sample_id"] for r in combined] != [r["sample_id"] for r in rows]:
            raise m.ModelRunError("共享150分母或身份变化。")
        m.write_json(out / name / "combined_predictions.json", {"records": combined, "claim_scope": "development_only", "condition": report["condition"]}, exclusive=True)
        all_rows[name] = combined
        row = report["providers"][name]
        chosen = [f for f in finishes.values() if f["provider"] == name]
        usages = [m.read_json(out / f["response_path"])["usage"] for f in chosen]
        row.update(previous_recovery_valid_predictions=row["valid_predictions"], structural_feedback_calls=len(chosen),
                   attempted=row["attempted"] + len(chosen), supplementary_calls=row["supplementary_calls"] + len(chosen),
                   valid_predictions=sum(r["request_status"] == "ok" for r in combined))
        row["conservative_uncached_cost"] += sum(f["reserved_cost"] for f in chosen)
        row["input_tokens"] += sum(u.get("prompt_tokens", 0) for u in usages)
        row["output_tokens"] += sum(u.get("completion_tokens", 0) for u in usages)
        report["remaining_failures"] += [{"provider": name, "sample_id": r["sample_id"], "failure_stage": r.get("failure_stage")}
                                          for r in combined if r["request_status"] != "ok"]
    gold = m.read_json(root / parent.initial.GOLD)
    for name, rows in all_rows.items():
        evaluation = evaluate_coarse(gold, attempt_rows(rows), method_id="multi_model_" + name)
        m.write_json(out / name / "evaluation.json", evaluation, exclusive=True)
        report["providers"][name]["metrics"] = {"overall": evaluation["coarse_five_field_micro"], "per_field": evaluation["five_fields"],
              "modality_macro_f1": evaluation["modality_labels"]["macro_f1"], "failed_count": evaluation["failed_count"]}
    report["all_150_valid"] = not report["remaining_failures"]
    report["limitations"] = ["固定150条与模型/平台配置的描述性比较，无重复采样、纯模型因果或显著性结论。",
        "保留首轮900、15回显格式恢复加18原样补跑与固定DeepSeek/Sun表；本轮4个原失败新增合同错误反馈，另列工程恢复条件，不冒充首轮成功率。",
        "全部关闭思考；Kimi保留用户接受的空思考正文且1 token计数例外，不解释该1 token语义。",
        "完整六家预测保存后才读Gold共享150分母五字段pooled评价，modality独立；Gold未发API或修改。",
        "每个选定原失败恰一次新增调用、0自动重试，Kimi至少21秒；费用估算非账户实扣。",
        "GitHub原始产物外发许可仍待确认，push自动审批阻塞未解除。"]
    m.write_json(report_path(root), report, exclusive=True)
    lines = ["# 六家非思考模型：四条结构错误反馈补跑", "", f"本轮{len(starts)}/4次，累计{report['actual_calls']}次；全150有效：{report['all_150_valid']}。", "",
             "| 平台 | 之前有效 | 本轮调用 | 当前有效/150 | 五字段pooled F1 | 失败 |", "|---|---:|---:|---:|---:|---:|"]
    for name, row in report["providers"].items():
        lines.append(f"| {name} | {row['previous_recovery_valid_predictions']} | {row['structural_feedback_calls']} | {row['valid_predictions']} | {row['metrics']['overall']['f1']:.4f} | {row['metrics']['failed_count']} |")
    lines += ["", "新增估算费用：" + json.dumps(report["additional_costs"]) + "；账户实扣未核对。", "剩余失败：" + json.dumps(report["remaining_failures"], ensure_ascii=False), "", *["- " + s for s in report["limitations"]]]
    report_path(root, ".md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    artifacts = {p.relative_to(root).as_posix(): m.digest(p.read_bytes()) for p in out.rglob("*.json*")}
    for p in (report_path(root), report_path(root, ".md"), report_path(root, "_preflight.json")):
        artifacts[p.relative_to(root).as_posix()] = m.digest(p.read_bytes())
    manifest = {"run_id": RUN_ID, "task_id": TASK, "status": result["status"], "all_150_valid": report["all_150_valid"],
                "new_calls": len(starts), "combined_calls": report["actual_calls"], "retry": 0,
                "source_bindings": value["source_bindings"], "artifacts": artifacts}
    m.write_json(out / "manifest.json", manifest, exclusive=True)
    print(json.dumps({"run_id": RUN_ID, "new_calls": len(starts), "valid": {n: r["valid_predictions"] for n, r in report["providers"].items()},
                      "remaining_failures": report["remaining_failures"], "additional_costs": report["additional_costs"]}), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--execute", action="store_true")
    group.add_argument("--summarize", action="store_true")
    parser.add_argument("--allow-llm", action="store_true")
    args = parser.parse_args()
    try:
        if args.prepare:
            prepare()
        elif args.execute:
            execute(allow_llm=args.allow_llm)
        else:
            summarize()
    except m.ModelRunError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
