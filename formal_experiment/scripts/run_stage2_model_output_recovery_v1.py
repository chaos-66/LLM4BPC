"""Authorized 15 echo-only recoveries and at most 18 unchanged supplementary calls."""
from __future__ import annotations

import argparse
import copy
from concurrent.futures import ThreadPoolExecutor
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
import run_stage2_multi_model_all_v1 as initial
import run_stage2_multi_model_remaining_v1 as middle
import run_stage2_kimi_rpm_remaining_v1 as final

RUN_ID = "model_output_recovery_20261007_v1"
TASK = "S2-MODEL-OUTPUT-RECOVERY-V1"
AUTH = "configs/authorization/stage2_model_output_recovery_20261007_v1.json"
PREFIX = "outputs/reports/stage2_multi_model_failure_diagnosis_20261007_v1"
PREVIEW = PREFIX + "_recovery18_preflight.json"
DIAGNOSIS = PREFIX + ".json"
DECISION = "恢复15条格式差异，再授权补跑其余18条（推荐）"
COUNTS = {"qwen": 1, "mimo": 2, "kimi": 3, "grok": 1, "glm": 6, "minimax": 5}
QUOTE_MAP = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})


def out_dir(root=ROOT):
    return root / "outputs/development/stage2_multi_model_remaining_v1" / RUN_ID


def report_path(root=ROOT, suffix=".json"):
    return root / "outputs/reports" / ("stage2_" + RUN_ID + suffix)


def presentation(text):
    return " ".join(text.translate(QUOTE_MAP).split())


def recover_echo(request, content):
    """Only change redundant source_text, after verifying IDs and presentation equivalence."""
    original = m.canonical_prediction(request, content)
    if original.get("failure_stage") != "input_binding":
        return original, None
    text = content.strip()
    if text.startswith("```json\n") and text.endswith("```"):
        text = text[8:-3].strip()
    payload = json.loads(text)
    echo = payload.get("source_text")
    if (payload.get("sample_id") != request["sample_id"] or payload.get("source_id") != request["source_id"]
            or not isinstance(echo, str) or presentation(echo) != presentation(request["source_text"])):
        return original, None
    before = copy.deepcopy(payload)
    payload["source_text"] = request["source_text"]
    recovered = m.canonical_prediction(request, m.encode(payload).decode("utf-8"))
    if recovered["request_status"] != "ok":
        return original, None
    assert {k: v for k, v in before.items() if k != "source_text"} == {k: v for k, v in payload.items() if k != "source_text"}
    audit = {"policy": "source_echo_quotes_whitespace_only@1", "changed_fields": ["source_text"],
             "original_echo": echo, "restored_echo": request["source_text"],
             "extraction_fields_unchanged": True, "original_content_sha256": m.digest(content.encode("utf-8")),
             "recovered_payload_sha256": m.digest(m.encode(payload)), "gold_used": False}
    recovered["source_echo_recovery"] = audit
    return recovered, audit


def parse_response(request, profile, raw, auth):
    decoded, check, strict = middle.parse_response(request, profile, raw, auth)
    prediction, audit = recover_echo(request, decoded["content"])
    return decoded, check, prediction, audit


def baseline_path(name, originals, root):
    if name == "kimi":
        return final.out_dir(root) / "combined_predictions.json"
    if name in ("glm", "mimo"):
        return middle.provider_dir(name, root) / "combined_predictions.json"
    return middle.original_dir(originals[name], root) / "predictions.json"


def expected(root, prepared_at):
    auth, preview, diagnosis = (m.read_json(root / p) for p in (AUTH, PREVIEW, DIAGNOSIS))
    required = {"authorized": True, "run_id": RUN_ID, "decision": DECISION, "max_new_calls": 18,
                "max_combined_calls": 918, "retry": 0, "max_output_tokens_per_call": 4096,
                "max_new_output_tokens": 73728, "kimi_min_start_interval_seconds": 21,
                "currency_caps": {"CNY": 3.83, "USD": 0.05}, "offline_recoveries": 15,
                "kimi_counter_policy_authorization": "接受，保留计数差异并继续 Kimi"}
    if any(auth.get(k) != v for k, v in required.items()) or auth.get("preview_sha256") != m.digest((root / PREVIEW).read_bytes()):
        raise m.ModelRunError("15+18授权、费用、关闭思考或预检绑定不匹配。")
    global_plan, originals, original_auths = initial.saved_plans(root)
    initial.verify_batch(global_plan, originals, original_auths, root=root)
    final.verify(m.read_json(final.out_dir(root) / "plan.json"), root)
    bindings = {}
    for directory in (initial.batch_dir(root), middle.out_dir(root), final.out_dir(root)):
        mf_path = directory / "manifest.json"
        mf = m.read_json(mf_path)
        if (directory / ".run.lock").exists():
            raise m.ModelRunError("父运行未关闭。")
        for relative, sha in mf["artifacts"].items():
            if m.digest((root / relative).read_bytes()) != sha:
                raise m.ModelRunError("父产物哈希变化：" + relative)
            bindings[relative] = sha
        bindings[mf_path.relative_to(root).as_posix()] = m.digest(mf_path.read_bytes())
    baseline = m.read_json(final.report_path(root))
    if baseline["actual_calls"] != 900 or baseline["status"] != "succeeded" or preview["parent_manifest_sha256"] != bindings[(final.out_dir(root) / "manifest.json").relative_to(root).as_posix()]:
        raise m.ModelRunError("必须继承已闭合900次父运行。")
    paths = {name: baseline_path(name, originals, root).relative_to(root).as_posix() for name in COUNTS}
    rows = {name: {r["sample_id"]: r for r in m.read_json(root / p)["records"]} for name, p in paths.items()}
    selected, targets, costs = {}, set(), {"CNY": 0.0, "USD": 0.0}
    for name, count in COUNTS.items():
        entries = [e for e in preview["requests"] if e["provider"] == name]
        if len(entries) != count:
            raise m.ModelRunError("补跑列表必须恰18项。")
        requests = []
        budget = copy.deepcopy(original_auths[name]["budgets"][name])
        for entry in entries:
            request = entry["request"]
            source_request = next(r for r in originals[name]["requests"] if r["sample_id"] == entry["sample_id"])
            if request != source_request or entry["profile"] != originals[name]["profiles"][name] or rows[name][entry["sample_id"]]["request_status"] != "failed":
                raise m.ModelRunError("只允许失败集合及原样请求。")
            if entry["frozen_price_budget"] != budget or m.digest(m.encode(request["body"])) != request["body_sha256"]:
                raise m.ModelRunError("冻结价格或请求字节变化。")
            requests.append(copy.deepcopy(request))
            targets.add((name, entry["sample_id"]))
        plan = {**copy.deepcopy(originals[name]), "run_id": RUN_ID + "_" + name,
                "requests": requests, "planned_calls": count, "samples_per_provider": count}
        budget["max_cost"] = sum(m._reservation(r, plan, budget) for r in requests)
        costs[budget["currency"]] += budget["max_cost"]
        selected[name] = {"plan": plan, "budget": budget}
    failures = {(f["provider"], f["sample_id"]): f for f in diagnosis["failures"]}
    recoveries = []
    for candidate in preview["offline_presentation_recovery_candidates"]:
        name, sid = candidate["provider"], candidate["sample_id"]
        case = failures[(name, sid)]
        request = next(r for r in originals[name]["requests"] if r["sample_id"] == sid)
        raw_path = root / case["response_path"]
        if (name, sid) in targets or rows[name][sid]["request_status"] != "failed" or m.digest(raw_path.read_bytes()) != candidate["response_sha256"]:
            raise m.ModelRunError("离线恢复候选、原失败或原响应改变。")
        response = m.read_json(raw_path)
        decoded, check, prediction, audit = parse_response(request, originals[name]["profiles"][name], response["raw_response_utf8"].encode("utf-8"), auth)
        if prediction["request_status"] != "ok" or audit is None:
            raise m.ModelRunError("离线恢复必须仅回显格式变化并通过原结构校验。")
        recoveries.append({"provider": name, "sample_id": sid, "prediction": prediction,
                           "source_response_path": case["response_path"], "source_response_sha256": candidate["response_sha256"],
                           "nonthinking_check": check, "additional_api_calls": 0})
        targets.add((name, sid))
    if len(recoveries) != 15 or len(targets) != 33 or targets != set(failures):
        raise m.ModelRunError("恢复加补跑必须覆盖恰33个父失败。")
    if any(costs[c] > auth["currency_caps"][c] for c in costs):
        raise m.ModelRunError("新费用上限不足。")
    for path in (AUTH, PREVIEW, DIAGNOSIS, PREFIX + "_reattempt_preflight.json", "scripts/run_stage2_model_output_recovery_v1.py"):
        bindings[path] = m.digest((root / path).read_bytes())
    if preview["source_diagnosis_sha256"] != bindings[DIAGNOSIS] or preview["source_full_33_preflight_sha256"] != bindings[PREFIX + "_reattempt_preflight.json"]:
        raise m.ModelRunError("诊断和预检来源哈希变化。")
    return {"run_id": RUN_ID, "task_id": TASK, "prepared_at_utc": prepared_at, "authorization": auth,
            "selected": selected, "offline_recoveries": recoveries, "baseline_paths": paths,
            "source_bindings": bindings, "parent_run_id": final.RUN_ID, "reserved_costs": costs,
            "api_calls": 0, "metrics": None, "primary_metric": baseline["primary_metric"]}


def prepare(root=ROOT):
    if out_dir(root).exists():
        raise m.ModelRunError("恢复目录已存在，拒绝覆盖。")
    value = expected(root, m.now())
    m.write_json(out_dir(root) / "plan.json", value, exclusive=True)
    m.write_json(out_dir(root) / "offline_recoveries.json", {"records": value["offline_recoveries"], "api_calls": 0}, exclusive=True)
    m.write_json(report_path(root, "_preflight.json"), value, exclusive=True)
    print(json.dumps({"prepared": RUN_ID, "offline_recoveries": 15, "new_calls": 18, "api_calls": 0}), flush=True)
    return value


def verify(value, root):
    if m.encode(value) != m.encode(expected(root, value["prepared_at_utc"])):
        raise m.ModelRunError("新授权、源码、请求或父证据变化，拒绝密钥读取及调用。")


def ledger_auth(value, name):
    bundle = value["selected"][name]
    return {"authorized": True, "plan_sha256": m.digest(m.encode(bundle["plan"])),
            "budgets": {name: bundle["budget"]}, "recovery_authorization": value["authorization"]}


def run_provider(name, value, root, sender, keys, clock, sleeper):
    bundle = value["selected"][name]
    plan, budget = bundle["plan"], bundle["budget"]
    out = out_dir(root) / name
    out.mkdir(parents=True, exist_ok=False)
    ledger, auth = out / "calls_ledger.jsonl", ledger_auth(value, name)
    starts, finishes, head = {}, {}, ""
    next_start, spent = 0.0, 0.0
    for request in plan["requests"]:
        body, reserve = m.encode(request["body"]), m._reservation(request, plan, budget)
        if m.digest(body) != request["body_sha256"] or len(starts) >= COUNTS[name] or spent + reserve > budget["max_cost"] + 1e-12:
            raise m.ModelRunError("请求字节、次数或费用超出授权。")
        if name == "kimi":
            final.wait_until(next_start, clock, sleeper)
        timestamp = datetime.fromtimestamp(clock(), timezone.utc).isoformat()
        base = {"provider": name, "request_id": request["request_id"], "sample_id": request["sample_id"],
                "plan_sha256": auth["plan_sha256"], "body_sha256": request["body_sha256"],
                "authorization_sha256": m.digest(m.encode(auth)), "timestamp_utc": timestamp,
                "reserved_cost": reserve, "currency": budget["currency"]}
        head = m._append_ledger(ledger, {**base, "event": "started"}, head)
        starts[request["request_id"]] = base
        next_start = clock() + 21
        raw_text, usage, returned, error, audit = "", {}, None, None, None
        check, attention = {"status": "not_verified", "reported_reasoning_tokens": None}, False
        try:
            raw = sender(plan["profiles"][name], body, keys[name], plan["timeout_seconds"])
            raw_text = raw.decode("utf-8", errors="replace")
            decoded, check, prediction, audit = parse_response(request, plan["profiles"][name], raw, value["authorization"])
            usage, returned = decoded["usage"], decoded["model"]
            reserve = (usage["prompt_tokens"] * budget["input_per_million"] + usage["completion_tokens"] * budget["output_per_million"]) / 1_000_000
        except Exception as exc:
            attention = True
            error = str(exc) if isinstance(exc, m.ModelRunError) else "补跑异常（" + type(exc).__name__ + "）。"
            prediction = {"provider": name, "sample_id": request["sample_id"], "request_id": request["request_id"],
                          "request_status": "failed", "failure_stage": "transport_or_usage", "record": {}}
        response_path = out / "responses" / (name + "_" + request["sample_id"] + ".json")
        m.write_json(response_path, m.redact({"request_id": request["request_id"], "raw_response_utf8": raw_text,
                     "usage": usage, "returned_model": returned, "nonthinking_check": check, "error": error,
                     "prediction": prediction, "echo_recovery_audit": audit}, list(keys.values())), exclusive=True)
        finish = {**base, "event": "finished", "timestamp_utc": m.now(), "reserved_cost": reserve,
                  "needs_attention": attention, "response_path": response_path.relative_to(out).as_posix(),
                  "response_sha256": m.digest(response_path.read_bytes()), "request_status": prediction["request_status"]}
        head = m._append_ledger(ledger, finish, head)
        finishes[request["request_id"]] = finish
        spent += reserve
        print(json.dumps({"provider": name, "sample_id": request["sample_id"], "status": prediction["request_status"],
                          "failure_stage": prediction.get("failure_stage"), "calls": len(starts)}), flush=True)
        if attention:
            break
    rows = [m.read_json(out / finishes[r["request_id"]]["response_path"])["prediction"]
            if r["request_id"] in finishes else {"provider": name, "sample_id": r["sample_id"], "request_id": r["request_id"],
            "request_status": "not_attempted", "record": {}} for r in plan["requests"]]
    m.write_json(out / "predictions.json", {"records": rows, "claim_scope": "development_only"}, exclusive=True)
    result = {"status": "succeeded" if len(finishes) == COUNTS[name] and not attention else "partial",
              "llm_calls": len(starts), "valid_predictions": sum(r["request_status"] == "ok" for r in rows),
              "plan_sha256": auth["plan_sha256"], "authorization_sha256": m.digest(m.encode(auth)),
              "ledger_head_sha256": head, "predictions_sha256": m.digest((out / "predictions.json").read_bytes()),
              "conservative_uncached_cost": spent, "currency": budget["currency"], "retry": 0}
    m.write_json(out / "provider_manifest.json", result, exclusive=True)
    return result


def execute(root=ROOT, allow_llm=False, sender=m.send_http, credential_loader=m.load_credentials,
            clock=time.time, sleeper=time.sleep):
    if not allow_llm:
        raise m.ModelRunError("真实调用须 --execute --allow-llm。")
    value = m.read_json(out_dir(root) / "plan.json")
    verify(value, root)
    out, lock = out_dir(root), out_dir(root) / ".run.lock"
    if lock.exists() or any((out / name).exists() for name in COUNTS) or (out / "execution_summary.json").exists():
        raise m.ModelRunError("已开始批次拒绝重复调用；无自动恢复或重试。")
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(fd)
    try:
        profiles = {name: b["plan"]["profiles"][name] for name, b in value["selected"].items()}
        keys = credential_loader(profiles, root)
        began = clock()
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = {name: pool.submit(run_provider, name, value, root, sender, keys, clock, sleeper) for name in COUNTS}
            results = {name: future.result() for name, future in futures.items()}
        result = {"run_id": RUN_ID, "providers": results, "actual_new_calls": sum(r["llm_calls"] for r in results.values()),
                  "status": "succeeded" if all(r["status"] == "succeeded" for r in results.values()) else "partial",
                  "runtime_seconds": round(clock() - began, 3), "retry": 0}
        m.write_json(out / "execution_summary.json", result, exclusive=True)
    finally:
        lock.unlink(missing_ok=True)
    return summarize(root)


def summarize(root=ROOT):
    out = out_dir(root)
    if (out / ".run.lock").exists() or (out / "manifest.json").exists():
        raise m.ModelRunError("运行未关闭或已汇总；拒绝覆盖。")
    value = m.read_json(out / "plan.json")
    verify(value, root)
    execution = m.read_json(out / "execution_summary.json")
    report = copy.deepcopy(m.read_json(final.report_path(root)))
    report.update(run_id=RUN_ID, task_id=TASK, parent_run_id=final.RUN_ID, condition="offline_echo_recovery_and_one_supplement",
                  actual_new_calls_in_run=execution["actual_new_calls"], actual_calls=900 + execution["actual_new_calls"],
                  offline_recoveries=15, status=execution["status"], first_pass_results_preserved=True,
                  additional_costs={"CNY": 0.0, "USD": 0.0}, remaining_failures=[], execution=execution)
    report.pop("actual_new_calls", None)
    all_rows = {}
    for name, bundle in value["selected"].items():
        directory = out / name
        auth = ledger_auth(value, name)
        starts, finishes, head = m._load_ledger(directory / "calls_ledger.jsonl", bundle["plan"])
        m._verify_saved_calls(directory, bundle["plan"], auth, starts, finishes)
        saved = m.read_json(directory / "provider_manifest.json")
        if (set(starts) != set(finishes) or saved["llm_calls"] != len(starts) or saved["ledger_head_sha256"] != head
                or saved["plan_sha256"] != auth["plan_sha256"] or saved["authorization_sha256"] != m.digest(m.encode(auth))
                or saved["predictions_sha256"] != m.digest((directory / "predictions.json").read_bytes())
                or saved != execution["providers"][name]):
            raise m.ModelRunError("补跑调用证据不一致。")
        rows = copy.deepcopy(m.read_json(root / value["baseline_paths"][name])["records"])
        patches = {r["sample_id"]: r["prediction"] for r in value["offline_recoveries"] if r["provider"] == name}
        for r in m.read_json(directory / "predictions.json")["records"]:
            if r["request_status"] != "not_attempted":
                patches[r["sample_id"]] = r
        combined = [patches.get(r["sample_id"], r) for r in rows]
        if len(combined) != 150 or len({r["sample_id"] for r in combined}) != 150:
            raise m.ModelRunError("150分母与ID集合不一致。")
        m.write_json(directory / "combined_predictions.json", {"records": combined, "claim_scope": "development_only",
                     "condition": report["condition"]}, exclusive=True)
        all_rows[name] = combined
        row = report["providers"][name]
        row.update(first_pass_valid_predictions=row["valid_predictions"], attempted=row["attempted"] + len(starts),
                   supplementary_calls=len(starts), offline_echo_recoveries=sum(r["provider"] == name for r in value["offline_recoveries"]),
                   valid_predictions=sum(r["request_status"] == "ok" for r in combined), status=saved["status"])
        row["conservative_uncached_cost"] += saved["conservative_uncached_cost"]
        report["additional_costs"][saved["currency"]] += saved["conservative_uncached_cost"]
        usages = [m.read_json(directory / f["response_path"])["usage"] for f in finishes.values()]
        row["input_tokens"] += sum(u.get("prompt_tokens", 0) for u in usages)
        row["output_tokens"] += sum(u.get("completion_tokens", 0) for u in usages)
        report["remaining_failures"] += [{"provider": name, "sample_id": r["sample_id"], "failure_stage": r.get("failure_stage")}
                                          for r in combined if r["request_status"] != "ok"]
    if report["actual_calls"] > 918 or any(report["additional_costs"][c] > value["authorization"]["currency_caps"][c] for c in report["additional_costs"]):
        raise m.ModelRunError("新累计次数或费用超出授权。")
    # Every merged prediction file is persisted before the first semantic Gold read.
    gold = m.read_json(root / initial.GOLD)
    for name, rows in all_rows.items():
        evaluation = evaluate_coarse(gold, attempt_rows(rows), method_id="multi_model_" + name)
        evaluation["primary_metric"] = report["primary_metric"]
        m.write_json(out / name / "evaluation.json", evaluation, exclusive=True)
        report["providers"][name]["metrics"] = {"overall": evaluation["coarse_five_field_micro"], "per_field": evaluation["five_fields"],
              "modality_macro_f1": evaluation["modality_labels"]["macro_f1"], "failed_count": evaluation["failed_count"]}
    report["all_150_valid"] = not report["remaining_failures"]
    report["limitations"].append("新条件：用户批准15条仅回显引号/空白离线恢复，18条原样各新尝试一次；同一回显格式规则适用于新响应，抽取字段与原adapter/evaluator保持。原首轮900次和固定主表不变，不冒充首次成功率。")
    m.write_json(report_path(root), report, exclusive=True)
    lines = ["# 六家非思考模型：15条格式恢复与18次补跑", "", f"本批实际{execution['actual_new_calls']}/18次，累计{report['actual_calls']}次；离线恢复15条。", "",
             "| 平台 | 原有效 | 离线恢复 | 补跑 | 当前有效/150 | 五字段pooled F1 | 失败 |", "|---|---:|---:|---:|---:|---:|---:|"]
    for name, row in report["providers"].items():
        lines.append(f"| {name} | {row['first_pass_valid_predictions']} | {row['offline_echo_recoveries']} | {row['supplementary_calls']} | {row['valid_predictions']} | {row['metrics']['overall']['f1']:.4f} | {row['metrics']['failed_count']} |")
    lines += ["", "新增保守费用估算：" + json.dumps(report["additional_costs"]) + "；账户实扣未核对。", "", "剩余失败：" + json.dumps(report["remaining_failures"], ensure_ascii=False), "", *["- " + s for s in report["limitations"]]]
    report_path(root, ".md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    artifacts = {p.relative_to(root).as_posix(): m.digest(p.read_bytes()) for p in out.rglob("*.json*")}
    for p in (report_path(root), report_path(root, ".md"), report_path(root, "_preflight.json")):
        artifacts[p.relative_to(root).as_posix()] = m.digest(p.read_bytes())
    manifest = {"run_id": RUN_ID, "task_id": TASK, "status": report["status"], "all_150_valid": report["all_150_valid"],
                "new_calls": execution["actual_new_calls"], "combined_calls": report["actual_calls"], "offline_recoveries": 15,
                "retry": 0, "source_bindings": value["source_bindings"], "artifacts": artifacts}
    m.write_json(out / "manifest.json", manifest, exclusive=True)
    print(json.dumps({"run_id": RUN_ID, "new_calls": manifest["new_calls"], "valid": {n: r["valid_predictions"] for n, r in report["providers"].items()},
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
