"""Continue only the 447 never-attempted requests; preserve all original evidence.

Offline by default. The Kimi-only one-token counter exception requires the
explicit recorded user decision; empty reasoning and disabled requests remain mandatory.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
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
import run_stage2_multi_model_all_v1 as parent

RUN_ID = "multi_model_remaining_20261007_v1"
PROVIDERS = ["glm", "mimo", "kimi"]
AUTH = "configs/authorization/stage2_multi_model_remaining_20261007_v1.json"


def out_dir(root=ROOT):
    return root / "outputs/development/stage2_multi_model_remaining_v1" / RUN_ID


def report_path(root=ROOT, suffix=".json"):
    return root / "outputs/reports" / ("stage2_" + RUN_ID + suffix)


def provider_dir(provider, root=ROOT):
    return out_dir(root) / provider


def original_dir(plan, root):
    return root / "outputs/development/stage2_multi_model_v1" / plan["run_id"]


def check_nonthinking(provider, request, decoded, auth):
    count = decoded.get("usage", {}).get("reasoning_tokens")
    if provider == "kimi" and type(count) is int and count == 1:
        if (not auth.get("kimi_counter_policy_authorization")
                or request["body"].get("model") != "kimi-k2.6"
                or request["body"].get("thinking") != {"type": "disabled"}
                or decoded.get("reasoning_present")
                or decoded.get("content", "").lstrip().startswith("<think>")):
            raise m.ModelRunError("Kimi单token计数例外不符合已确认条件；停止且不重试。")
        return {"status": "request_disabled_empty_reasoning_user_accepted_counter1",
                "reasoning_content_present": False, "reported_reasoning_tokens": 1,
                "counter_exception_user_authorized": True,
                "one_token_meaning_verified": False}
    return m.verify_nonthinking_response(decoded)


def parse_response(request, profile, raw, auth):
    decoded = decode_chat_completion_envelope(raw)
    usage = decoded.get("usage", {})
    if decoded.get("model") not in profile["accepted_returned_models"]:
        raise m.ModelRunError("返回型号与原冻结型号不匹配。")
    pt, ct = usage.get("prompt_tokens"), usage.get("completion_tokens")
    if (type(pt) is not int or type(ct) is not int or pt < 0 or ct < 0
            or pt > request["input_token_reservation"] or ct > 4096):
        raise m.ModelRunError("usage缺失、不合法或超出冻结预算；停止且不重试。")
    if decoded.get("status") != "ok_message_content" or decoded.get("finish_reason") != "stop":
        raise m.ModelRunError("响应为空或不完整；停止且不重试。")
    check = check_nonthinking(request["provider"], request, decoded, auth)
    return decoded, check, m.canonical_prediction(request, decoded["content"])


def parent_state(root):
    value, plans, auths = parent.saved_plans(root)
    parent.verify_batch(value, plans, auths, root=root)
    manifest_path = parent.batch_dir(root) / "manifest.json"
    manifest = m.read_json(manifest_path)
    if manifest["llm_calls"] != 453 or manifest["status"] != "partial":
        raise m.ModelRunError("父批次必须是已确认453次且已结束的partial状态。")
    for relative, expected in manifest["artifacts"].items():
        if m.digest((root / relative).read_bytes()) != expected:
            raise m.ModelRunError("父批次产物发生变化；拒绝续跑。")
    states = {}
    total = 0
    for name, plan in plans.items():
        old = original_dir(plan, root)
        starts, finishes, head = m._load_ledger(old / "calls_ledger.jsonl", plan)
        m._verify_saved_calls(old, plan, auths[name], starts, finishes)
        if set(starts) != set(finishes) or (old / ".run.lock").exists():
            raise m.ModelRunError("父批次存在未决调用或运行锁；拒绝续跑。")
        total += len(starts)
        if name in PROVIDERS:
            first = plan["requests"][0]
            if set(starts) != {first["request_id"]}:
                raise m.ModelRunError("只允许三家已确认首条停止、其余149条未发送的续跑。")
            finish = finishes[first["request_id"]]
            saved = m.read_json(old / finish["response_path"])
            error = saved.get("error") or ""
            if name == "glm" and not (error.startswith("HTTP 429:") and '"1113"' in error):
                raise m.ModelRunError("GLM父失败不属于已确认余额问题。")
            if name == "mimo" and not (error.startswith("HTTP 402:") and "insufficient_balance" in error):
                raise m.ModelRunError("MiMo父失败不属于已确认余额问题。")
            states[name] = {"started_ids": list(starts), "ledger_head": head,
                            "inherited_reserved_cost": finish["reserved_cost"]}
    if total != 453:
        raise m.ModelRunError("父调用合计不匹配。")
    return value, plans, auths, states, manifest_path


def expected(root, prepared_at):
    auth = m.read_json(root / AUTH)
    if (auth.get("authorized") is not True or auth.get("run_id") != RUN_ID
            or auth.get("parent_run_id") != parent.RUN_ID or auth.get("providers") != PROVIDERS
            or auth.get("max_new_calls") != 447 or auth.get("inherited_calls") != 453
            or auth.get("max_combined_calls") != 900 or auth.get("retry") != 0
            or auth.get("new_calls_per_provider") != 149 or auth.get("max_workers") != 3
            or auth.get("max_workers_per_provider") != 1
            or auth.get("max_output_tokens_per_call") != 4096
            or auth.get("max_new_output_tokens") != 447 * 4096
            or auth.get("thinking_requirement") != "disabled"
            or auth.get("kimi_counter_policy_authorization") != "接受，保留计数差异并继续 Kimi"
            or auth.get("kimi_counter_exception") != {
                "model": "kimi-k2.6", "required_request_thinking_type": "disabled",
                "required_empty_reasoning_content": True, "allowed_reported_reasoning_tokens": [0, 1],
                "retain_actual_reported_count": True, "claim_one_token_is_placeholder": False,
                "documentation": "https://platform.kimi.com/docs/guide/kimi-k2-6-quickstart"}):
        raise m.ModelRunError("续跑授权、447上限或Kimi例外口径不匹配；拒绝加载key。")
    value, originals, original_auths, states, manifest_path = parent_state(root)
    selected = {}
    for name in PROVIDERS:
        source = originals[name]
        plan = copy.deepcopy(source)
        plan.update(schema_version="stage2_multi_model_never_sent_plan@1.0.0",
                    run_id=RUN_ID + "_" + name, samples_per_provider=149, planned_calls=149,
                    parent_plan_sha256=m.digest(m.encode(source)), requests=[
                        r for r in source["requests"] if r["request_id"] not in states[name]["started_ids"]])
        budget = copy.deepcopy(original_auths[name]["budgets"][name])
        budget["max_cost"] -= states[name]["inherited_reserved_cost"]
        if len(plan["requests"]) != 149 or sum(m._reservation(r, plan, budget) for r in plan["requests"]) > budget["max_cost"]:
            raise m.ModelRunError("尚未发送集合或剩余原费用上限不足。")
        selected[name] = {"plan": plan, "budget": budget,
                          "parent_reserved_cost": states[name]["inherited_reserved_cost"]}
    # Validate the already received Kimi answer offline, under the new explicit decision.
    first = originals["kimi"]["requests"][0]
    old_response = original_dir(originals["kimi"], root) / "responses" / ("kimi_" + first["sample_id"] + ".json")
    saved = m.read_json(old_response)
    decoded, check, recovered = parse_response(first, originals["kimi"]["profiles"]["kimi"],
                                              saved["raw_response_utf8"].encode("utf-8"), auth)
    paths = [AUTH, "scripts/run_stage2_multi_model_remaining_v1.py", manifest_path.relative_to(root).as_posix()]
    return {"schema_version": "stage2_multi_model_remaining_plan@1.0.0", "task_id": parent.TASK,
            "run_id": RUN_ID, "prepared_at_utc": prepared_at, "authorization": auth,
            "parent_run_id": parent.RUN_ID, "parent_plan_sha256": m.digest(m.encode(value)),
            "inherited_calls": 453, "planned_new_calls": 447, "combined_call_cap": 900,
            "retry": 0, "primary_metric": "coarse_five_field_micro.f1",
            "source_bindings": {p: m.digest((root / p).read_bytes()) for p in paths},
            "selected": selected, "parent_states": states,
            "kimi_first_offline_recovery": {"source_response_sha256": m.digest(old_response.read_bytes()),
                "prediction": recovered, "nonthinking_check": check, "usage": decoded["usage"],
                "additional_api_calls": 0}, "metrics": None}


def prepare(root=ROOT):
    if out_dir(root).exists():
        raise m.ModelRunError("续跑目录已存在；不覆盖。")
    plan = expected(root, m.now())
    m.write_json(out_dir(root) / "plan.json", plan, exclusive=True)
    m.write_json(report_path(root, "_preflight.json"), plan, exclusive=True)
    print(json.dumps({"prepared": RUN_ID, "new_calls": 447, "inherited_calls": 453,
                      "kimi_first_recovered_offline": True, "api_calls": 0}), flush=True)
    return plan


def verify(plan, root):
    if m.encode(expected(root, plan.get("prepared_at_utc"))) != m.encode(plan):
        raise m.ModelRunError("续跑绑定、原始请求字节或已发送ID变化；拒绝加载key和HTTP。")


def run_provider(name, batch, root, sender, keys, resume):
    bundle = batch["selected"][name]
    plan, budget = bundle["plan"], bundle["budget"]
    auth = {"authorized": True, "plan_sha256": m.digest(m.encode(plan)), "budgets": {name: budget},
            "continuation_authorization": batch["authorization"]}
    plan_hash, auth_hash = m.digest(m.encode(plan)), m.digest(m.encode(auth))
    out = provider_dir(name, root)
    out.mkdir(parents=True, exist_ok=True)
    lock = out / ".run.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise m.ModelRunError("续跑锁已存在；拒绝重复调用。") from None
    os.close(fd)
    try:
        ledger = out / "calls_ledger.jsonl"
        if ledger.exists() and not resume:
            raise m.ModelRunError("已有调用，仅允许显式resume检查；不会覆盖。")
        starts, finishes, head = m._load_ledger(ledger, plan)
        m._verify_saved_calls(out, plan, auth, starts, finishes)
        if set(starts) != set(finishes) or any(f["needs_attention"] for f in finishes.values()):
            raise m.ModelRunError("存在未决或需核查的已尝试请求；不能自动重发。")
        spent = sum(f["reserved_cost"] for f in finishes.values())
        for request in plan["requests"]:
            rid = request["request_id"]
            if rid in starts:
                continue
            if rid in batch["parent_states"][name]["started_ids"]:
                raise m.ModelRunError("父批次已尝试ID禁止再次发送。")
            body = m.encode(request["body"])
            reserve = m._reservation(request, plan, budget)
            if m.digest(body) != request["body_sha256"] or len(starts) >= 149 or spent + reserve > budget["max_cost"]:
                raise m.ModelRunError("发送前请求或149次数/原剩余费用门禁失败。")
            base = {"request_id": rid, "provider": name, "sample_id": request["sample_id"],
                    "plan_sha256": plan_hash, "body_sha256": request["body_sha256"],
                    "authorization_sha256": auth_hash, "timestamp_utc": m.now(),
                    "reserved_cost": reserve, "currency": budget["currency"]}
            head = m._append_ledger(ledger, {**base, "event": "started"}, head)
            starts[rid] = base
            raw_text, error, usage, returned, check = "", None, {}, None, {"status": "not_verified", "reported_reasoning_tokens": None}
            attention = False
            try:
                raw = sender(plan["profiles"][name], body, keys[name], plan["timeout_seconds"])
                raw_text = raw.decode("utf-8", errors="replace")
                envelope = decode_chat_completion_envelope(raw)
                usage, returned = envelope.get("usage", {}), envelope.get("model")
                _, check, prediction = parse_response(request, plan["profiles"][name], raw, batch["authorization"])
                reserve = (usage["prompt_tokens"] * budget["input_per_million"] + usage["completion_tokens"] * budget["output_per_million"]) / 1_000_000
            except Exception as exc:
                attention = True
                error = str(exc) if isinstance(exc, m.ModelRunError) else "续跑异常（" + type(exc).__name__ + "）。"
                prediction = {"provider": name, "sample_id": request["sample_id"], "request_id": rid,
                              "request_status": "failed", "failure_stage": "transport_or_usage", "record": {}}
            path = out / "responses" / (name + "_" + request["sample_id"] + ".json")
            m.write_json(path, m.redact({"request_id": rid, "raw_response_utf8": raw_text,
                "usage": usage, "returned_model": returned, "nonthinking_check": check,
                "error": error, "prediction": prediction}, list(keys.values())), exclusive=True)
            finish = {**base, "event": "finished", "reserved_cost": reserve, "needs_attention": attention,
                      "response_path": path.relative_to(out).as_posix(), "response_sha256": m.digest(path.read_bytes()),
                      "request_status": prediction["request_status"]}
            head = m._append_ledger(ledger, finish, head)
            finishes[rid] = finish
            spent += reserve
            if attention:
                break
        rows = [m.read_json(out / finishes[r["request_id"]]["response_path"])["prediction"]
                if r["request_id"] in finishes else {"provider": name, "sample_id": r["sample_id"],
                    "request_id": r["request_id"], "request_status": "not_attempted", "record": {}}
                for r in plan["requests"]]
        m.write_json(out / "predictions.json", {"records": rows, "claim_scope": "development_only"})
        complete = len(finishes) == 149 and not any(f["needs_attention"] for f in finishes.values())
        manifest = {"run_id": plan["run_id"], "status": "succeeded" if complete else "partial",
                    "llm_calls": len(starts), "plan_sha256": plan_hash, "authorization_sha256": auth_hash,
                    "ledger_head_sha256": head, "conservative_uncached_cost": spent,
                    "predictions_sha256": m.digest((out / "predictions.json").read_bytes()),
                    "valid_predictions": sum(r["request_status"] == "ok" for r in rows), "retry": 0}
        m.write_json(out / "manifest.json", manifest)
        return manifest
    finally:
        lock.unlink(missing_ok=True)


def execute(root=ROOT, allow_llm=False, resume=False, sender=m.send_http, credential_loader=m.load_credentials):
    if not allow_llm:
        raise m.ModelRunError("真实续跑须 --execute --allow-llm。")
    plan = m.read_json(out_dir(root) / "plan.json")
    verify(plan, root)
    # All resume states are checked before loading any key; completed resume reads no keys.
    pending = False
    for name in PROVIDERS:
        bundle = plan["selected"][name]
        auth = {"authorized": True, "plan_sha256": m.digest(m.encode(bundle["plan"])),
                "budgets": {name: bundle["budget"]}, "continuation_authorization": plan["authorization"]}
        out = provider_dir(name, root)
        ledger = out / "calls_ledger.jsonl"
        if (out / ".run.lock").exists() or (ledger.exists() and not resume):
            raise m.ModelRunError("续跑已存在或有锁；拒绝加载key。")
        if (out / "manifest.json").exists() and not ledger.exists():
            raise m.ModelRunError("续跑产物存在但账本缺失。")
        starts, finishes, _ = m._load_ledger(ledger, bundle["plan"])
        m._verify_saved_calls(out, bundle["plan"], auth, starts, finishes)
        if set(starts) != set(finishes) or any(f["needs_attention"] for f in finishes.values()):
            raise m.ModelRunError("存在已尝试的未决/异常请求；禁止自动重发。")
        pending |= len(starts) < 149
    keys = credential_loader({p: plan["selected"][p]["plan"]["profiles"][p] for p in PROVIDERS}, root) if pending else {}
    started, statuses = time.monotonic(), {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(run_provider, p, plan, root, sender, keys, resume): p for p in PROVIDERS}
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                statuses[name] = {k: result[k] for k in ("status", "llm_calls", "valid_predictions")}
            except Exception as exc:
                statuses[name] = {"status": "blocked", "error_type": type(exc).__name__}
            print(json.dumps({"provider": name, **statuses[name]}, ensure_ascii=False), flush=True)
    m.write_json(out_dir(root) / "execution_summary.json", {"providers": statuses, "retry": 0,
                  "runtime_seconds": round(time.monotonic() - started, 3)})
    return summarize(root)


def summarize(root=ROOT):
    plan = m.read_json(out_dir(root) / "plan.json")
    verify(plan, root)
    _, originals, _, _, _ = parent_state(root)
    old_report = m.read_json(parent.report_path(root))
    report = copy.deepcopy(old_report)
    report.update(run_id=RUN_ID, parent_run_id=parent.RUN_ID, actual_new_calls=0, actual_calls=453,
                  retry=0, kimi_counter_policy=plan["authorization"]["kimi_counter_exception"],
                  execution=m.read_json(out_dir(root) / "execution_summary.json"))
    complete = {}
    for name in PROVIDERS:
        out, bundle = provider_dir(name, root), plan["selected"][name]
        starts, finishes, head = m._load_ledger(out / "calls_ledger.jsonl", bundle["plan"])
        auth = {"authorized": True, "plan_sha256": m.digest(m.encode(bundle["plan"])),
                "budgets": {name: bundle["budget"]}, "continuation_authorization": plan["authorization"]}
        m._verify_saved_calls(out, bundle["plan"], auth, starts, finishes)
        report["actual_new_calls"] += len(starts)
        report["actual_calls"] += len(starts)
        row = report["providers"][name]
        row["attempted"] = 1 + len(starts)
        row["status"], row["metrics"] = "partial", None
        if not (out / "manifest.json").exists():
            continue
        saved = m.read_json(out / "manifest.json")
        if (saved["plan_sha256"] != m.digest(m.encode(bundle["plan"])) or saved["ledger_head_sha256"] != head
                or saved["authorization_sha256"] != m.digest(m.encode(auth))
                or saved["llm_calls"] != len(starts)
                or saved["predictions_sha256"] != m.digest((out / "predictions.json").read_bytes())):
            raise m.ModelRunError("续跑manifest与原始证据不匹配。")
        first = m.read_json(original_dir(originals[name], root) / "predictions.json")["records"][0]
        if name == "kimi":
            first = plan["kimi_first_offline_recovery"]["prediction"]
            row["first_answer_recovered_offline"] = True
        rows = [first, *m.read_json(out / "predictions.json")["records"]]
        if [r["sample_id"] for r in rows] != [r["sample_id"] for r in originals[name]["requests"]]:
            raise m.ModelRunError("合并后必须为相同150条、完整分母。")
        m.write_json(out / "combined_predictions.json", {"records": rows, "claim_scope": "development_only"})
        usage = [m.read_json(out / f["response_path"])["usage"] for f in finishes.values()]
        row["input_tokens"] += sum(u.get("prompt_tokens", 0) for u in usage)
        row["output_tokens"] += sum(u.get("completion_tokens", 0) for u in usage)
        row["conservative_uncached_cost"] += saved["conservative_uncached_cost"]
        row["valid_predictions"] = sum(r["request_status"] == "ok" for r in rows)
        row["retained_parent_transport_failure"] = name in {"glm", "mimo"}
        if saved["status"] == "succeeded" and len(starts) == len(finishes) == 149:
            row["status"] = "succeeded"
            complete[name] = rows
    # New predictions are saved and checked before semantic Gold use.
    if complete:
        gold = m.read_json(root / parent.GOLD)
        for name, rows in complete.items():
            result = evaluate_coarse(gold, attempt_rows(rows), method_id="multi_model_" + name)
            result["primary_metric"] = report["primary_metric"]
            m.write_json(provider_dir(name, root) / "evaluation.json", result)
            report["providers"][name]["metrics"] = {"overall": result["coarse_five_field_micro"],
                "per_field": result["five_fields"], "modality_macro_f1": result["modality_labels"]["macro_f1"],
                "failed_count": result["failed_count"]}
    report["status"] = "succeeded" if len(complete) == 3 else "partial"
    report["limitations"] += ["Kimi仅1 token且无思考正文的计数差异由用户明确接受，实际计数保留，不宣称该token为占位符；原严格失败证据保留。",
        "GLM/MiMo首条余额失败保留在150分母；充值后仅续跑149从未尝试项，不隐去基础设施失败。"]
    m.write_json(report_path(root), report)
    lines = ["# 六家非思考模型比较：续跑合并结果", "", f"状态{report['status']}；合计{report['actual_calls']}/900次、续跑{report['actual_new_calls']}/447次、0重试。", "",
             "同一EStG-150/原v6/coarse五字段pooled；结构和余额失败保留150分母，modality单列。", "",
             "| 平台 | 模型 | 调用/150 | 有效 | P | R | F1 | 失败 |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for name, row in report["providers"].items():
        metric = row["metrics"]
        scores = " | ".join(f"{metric['overall'][k]:.4f}" for k in ("precision", "recall", "f1")) if metric else "null | null | null"
        lines.append(f"| {name} | {row['model']} | {row['attempted']} | {row['valid_predictions']} | {scores} | {metric['failed_count'] if metric else '未完成'} |")
    lines += ["", *["- " + s for s in report["limitations"]], "",
              "保守费用包含原异常预留，未核对账户实扣；历史DeepSeek/Sun原固定结果复用。"]
    report_path(root, ".md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    artifacts = {p.relative_to(root).as_posix(): m.digest(p.read_bytes()) for p in out_dir(root).rglob("*.json*")
                 if p != out_dir(root) / "manifest.json"}
    for path in (report_path(root), report_path(root, ".md")):
        artifacts[path.relative_to(root).as_posix()] = m.digest(path.read_bytes())
    m.write_json(out_dir(root) / "manifest.json", {"task_id": parent.TASK, "run_id": RUN_ID,
        "parent_run_id": parent.RUN_ID, "parent_manifest_sha256": plan["source_bindings"][
            (parent.batch_dir(root) / "manifest.json").relative_to(root).as_posix()],
        "status": report["status"], "new_calls": report["actual_new_calls"], "combined_calls": report["actual_calls"],
        "source_bindings": plan["source_bindings"], "artifacts": artifacts, "retry": 0})
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
    elif args.summarize:
        result = summarize()
    else:
        prepare()
        return
    print(json.dumps({"status": result["status"], "new_calls": result["actual_new_calls"],
                      "combined_calls": result["actual_calls"]}), flush=True)


if __name__ == "__main__":
    main()
