"""One authorized 150-item run per provider, using the frozen non-thinking runner.

Offline by default. Six providers may run concurrently; each sends serially.
Failed/uncertain requests are never retried. Gold is used only after saved outputs.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bpc_hybrid import multi_model_stage2 as m
from bpc_hybrid.sep_c3_modular_evaluation import attempt_rows, evaluate_coarse

RUN_ID = "multi_model_all_20261007_v2"
TASK = "S2-MODEL-SENSITIVITY-V1"
PROVIDERS = ["qwen", "mimo", "kimi", "grok", "glm", "minimax"]
AUTH = "configs/authorization/stage2_multi_model_all_20261007_v1.json"
GOLD = "data/gold/stage2/estg150_formal_gold_v1.json"
BASELINES = {"deepseek_historical": "data/predictions/direct_llm_formal_arm_v1/predictions.json",
             "sun_historical": "data/predictions/b0_formal_arm_v1/predictions.json"}


def batch_dir(root=ROOT):
    return root / "outputs/development/stage2_multi_model_full_v1" / RUN_ID


def report_path(root=ROOT, suffix=".json"):
    return root / "outputs/reports" / ("stage2_" + RUN_ID + suffix)


def sources(root):
    relative = [AUTH, "scripts/run_stage2_multi_model_all_v1.py", GOLD, *BASELINES.values(),
                "outputs/reports/stage2_table1_paper_final_v1.json",
                "src/bpc_hybrid/sep_c3_modular_evaluation.py",
                "src/bpc_hybrid/formal_stage2_evaluation.py", "src/bpc_hybrid/g04_coarse_view.py",
                "src/bpc_hybrid/stage2_sun_literal_overlap.py"]
    return {p: m.digest((root / p).read_bytes()) for p in relative}


def prepare(root=ROOT):
    out = batch_dir(root)
    if out.exists():
        raise m.ModelRunError("本批目录已存在；不覆盖准备或历史调用。")
    auth = m.read_json(root / AUTH)
    plans, authorizations = {}, {}
    input_sets, messages = [], []
    for provider in PROVIDERS:
        plan = m.build_plan([provider], 150, RUN_ID + "_" + provider, root=root)
        value = m.authorization_template(plan)
        value.update(authorized=auth["authorized"], user_authorization=auth["user_authorization"],
                     approved_at_utc=m.now())
        value["budgets"][provider] = dict(auth["budgets"][provider],
             pricing_verified_at_utc=m.now())
        m.verify_authorization(plan, value, execute=True, allow_llm=True, root=root)
        plans[provider], authorizations[provider] = plan, value
        input_sets.append([r["sample_id"] for r in plan["requests"]])
        messages.append([m.digest(m.encode(r["body"]["messages"])) for r in plan["requests"]])
    if any(ids != input_sets[0] for ids in input_sets) or any(h != messages[0] for h in messages):
        raise m.ModelRunError("六家必须使用完全相同的150条输入与提示词。")
    batch = {"schema_version": "stage2_multi_model_full_plan@1.0.0", "task_id": TASK,
             "run_id": RUN_ID, "prepared_at_utc": m.now(), "authorization": auth,
             "source_bindings": sources(root), "providers": PROVIDERS,
             "planned_calls": 900, "samples_per_provider": 150, "retry": 0,
             "primary_metric": "coarse_five_field_micro.f1", "metrics": None,
             "provider_plans": {p: m.digest(m.encode(v)) for p, v in plans.items()},
             "provider_authorizations": {p: m.digest(m.encode(v)) for p, v in authorizations.items()},
             "sample_ids_sha256": m.digest(m.encode(input_sets[0])),
             "message_hashes_sha256": m.digest(m.encode(messages[0]))}
    verify_batch(batch, plans, authorizations, root=root)
    for provider in PROVIDERS:
        m.write_json(out / provider / "plan.json", plans[provider], exclusive=True)
        m.write_json(out / provider / "authorization.json", authorizations[provider], exclusive=True)
    m.write_json(out / "plan.json", batch, exclusive=True)
    m.write_json(report_path(root, "_preflight.json"), batch, exclusive=True)
    print(json.dumps({"prepared": RUN_ID, "planned_calls": 900, "api_calls": 0}, ensure_ascii=False), flush=True)
    return batch


def verify_batch(batch, plans, authorizations, *, root=ROOT):
    auth = m.read_json(root / AUTH)
    if (batch.get("run_id") != RUN_ID or batch.get("task_id") != TASK
            or auth != batch.get("authorization") or auth.get("authorized") is not True
            or auth.get("providers") != PROVIDERS or batch.get("providers") != PROVIDERS
            or auth.get("max_calls") != 900 or auth.get("samples_per_provider") != 150
            or auth.get("retry") != 0 or auth.get("thinking_requirement") != "disabled"
            or auth.get("max_output_tokens_per_call") != 4096
            or auth.get("max_total_output_tokens") != 900 * 4096
            or auth.get("max_workers") != 6 or auth.get("max_workers_per_provider") != 1
            or batch.get("source_bindings") != sources(root)):
        raise m.ModelRunError("六家全量授权或绑定变化；拒绝加载密钥和调用。")
    for provider in PROVIDERS:
        plan, value = plans[provider], authorizations[provider]
        if (plan["providers"] != [provider] or plan["samples_per_provider"] != 150
                or plan["run_id"] != RUN_ID + "_" + provider
                or m.digest(m.encode(plan)) != batch["provider_plans"][provider]
                or m.digest(m.encode(value)) != batch["provider_authorizations"][provider]):
            raise m.ModelRunError("分平台计划或授权哈希不匹配。")
        m.verify_authorization(plan, value, execute=True, allow_llm=True, root=root)


def saved_plans(root):
    out = batch_dir(root)
    return (m.read_json(out / "plan.json"),
            {p: m.read_json(out / p / "plan.json") for p in PROVIDERS},
            {p: m.read_json(out / p / "authorization.json") for p in PROVIDERS})


def execute(*, root=ROOT, allow_llm=False, resume=False, sender=m.send_http,
            credential_loader=m.load_credentials):
    if not allow_llm:
        raise m.ModelRunError("真实运行必须提供 --execute --allow-llm。")
    batch, plans, authorizations = saved_plans(root)
    verify_batch(batch, plans, authorizations, root=root)
    started = time.monotonic()
    credentials, credential_lock = {}, threading.Lock()
    all_profiles = {p: plans[p]["profiles"][p] for p in PROVIDERS}
    def private_keys(profiles, selected_root):
        with credential_lock:
            if not credentials:
                credentials.update(credential_loader(all_profiles, selected_root))
            return {p: credentials[p] for p in profiles}
    statuses = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(m.execute_plan, plans[p], authorizations[p], execute=True,
                   allow_llm=True, resume=resume, root=root, sender=sender,
                   credential_loader=private_keys): p for p in PROVIDERS}
        for future in as_completed(futures):
            provider = futures[future]
            try:
                manifest = future.result()
                statuses[provider] = {k: manifest[k] for k in ("status", "llm_calls", "valid_predictions")}
            except Exception as error:
                statuses[provider] = {"status": "blocked", "error_type": type(error).__name__}
                if isinstance(error, m.ModelRunError):
                    statuses[provider]["error"] = str(error)
            print(json.dumps({"provider": provider, **statuses[provider]}, ensure_ascii=False), flush=True)
    m.write_json(batch_dir(root) / "execution_summary.json",
                 {"run_id": RUN_ID, "providers": statuses, "retry": 0,
                  "runtime_seconds": round(time.monotonic() - started, 3)})
    return summarize(root=root)


def summarize(*, root=ROOT):
    batch, plans, authorizations = saved_plans(root)
    verify_batch(batch, plans, authorizations, root=root)
    report = {"schema_version": "stage2_multi_model_full_result@1.0.0", "task_id": TASK,
              "run_id": RUN_ID, "claim_scope": "development_only", "primary_metric": batch["primary_metric"],
              "planned_calls": 900, "actual_calls": 0, "retry": 0, "providers": {},
              "historical_baselines": {}, "limitations": batch["authorization"]["limitations"]}
    execution = batch_dir(root) / "execution_summary.json"
    if execution.exists():
        report["execution"] = m.read_json(execution)
    complete_predictions = {}
    artifacts = {}
    for provider in PROVIDERS:
        out = root / "outputs/development/stage2_multi_model_v1" / plans[provider]["run_id"]
        starts, finishes, head = m._load_ledger(out / "calls_ledger.jsonl", plans[provider])
        report["actual_calls"] += len(starts)
        if not (out / "manifest.json").exists():
            report["providers"][provider] = {"model": plans[provider]["profiles"][provider]["model"],
                 "status": "partial" if starts else "blocked", "attempted": len(starts),
                 "denominator": 150, "metrics": None}
            continue
        manifest = m.read_json(out / "manifest.json")
        m._verify_saved_calls(out, plans[provider], authorizations[provider], starts, finishes)
        if (manifest["plan_sha256"] != m.digest(m.encode(plans[provider]))
                or manifest["authorization_sha256"] != m.digest(m.encode(authorizations[provider]))
                or manifest["ledger_head_sha256"] != head or manifest["llm_calls"] != len(starts)
                or manifest["predictions_sha256"] != m.digest((out / "predictions.json").read_bytes())):
            raise m.ModelRunError("评价前响应、账本或预测绑定不匹配。")
        rows = m.read_json(out / "predictions.json")["records"]
        if [r["sample_id"] for r in rows] != [r["sample_id"] for r in plans[provider]["requests"]]:
            raise m.ModelRunError("必须保留同一150条完整分母。")
        usage = [m.read_json(out / finish["response_path"])["usage"] for finish in finishes.values()]
        report["providers"][provider] = {"model": plans[provider]["profiles"][provider]["model"],
             "status": manifest["status"], "denominator": 150, "attempted": len(starts),
             "valid_predictions": manifest["valid_predictions"], "metrics": None,
             "input_tokens": sum(u.get("prompt_tokens", 0) for u in usage),
             "output_tokens": sum(u.get("completion_tokens", 0) for u in usage),
             "cost_currency": authorizations[provider]["budgets"][provider]["currency"],
             "conservative_uncached_cost": manifest["conservative_uncached_cost_by_provider"][provider],
             "account_deduction_verified": False}
        if manifest["status"] == "succeeded" and len(starts) == len(finishes) == 150:
            complete_predictions[provider] = rows
        for path in out.rglob("*.json*"):
            artifacts[path.relative_to(root).as_posix()] = m.digest(path.read_bytes())
    # All predictions are persisted and hash-checked before the first semantic Gold read.
    if complete_predictions:
        gold = m.read_json(root / GOLD)
        for name, rows in complete_predictions.items():
            evaluation = evaluate_coarse(gold, attempt_rows(rows), method_id="multi_model_" + name)
            evaluation["primary_metric"] = batch["primary_metric"]
            evaluation["primary_metric_note"] = "本批主指标为coarse五字段pooled P/R/F1；五字段F1均值仅作诊断，modality独立。"
            evaluation_path = batch_dir(root) / name / "evaluation.json"
            m.write_json(evaluation_path, evaluation)
            artifacts[evaluation_path.relative_to(root).as_posix()] = m.digest(evaluation_path.read_bytes())
            report["providers"][name]["metrics"] = {"overall": evaluation["coarse_five_field_micro"],
                "per_field": evaluation["five_fields"], "modality_macro_f1": evaluation["modality_labels"]["macro_f1"],
                "failed_count": evaluation["failed_count"]}
        for name, path in BASELINES.items():
            evaluation = evaluate_coarse(gold, attempt_rows(m.read_json(root / path)["records"]), method_id=name)
            report["historical_baselines"][name] = evaluation["coarse_five_field_micro"]
        fixed = m.read_json(root / "outputs/reports/stage2_table1_paper_final_v1.json")
        for name, arm in (("deepseek_historical", "direct_llm"), ("sun_historical", "sun_rule_only")):
            if report["historical_baselines"][name]["f1"] != fixed["arms"][arm]["overall_pooled_five_span_fields"]["f1"]:
                raise m.ModelRunError("历史基线共享评价与固定表一不匹配；不改旧结果。")
    report["status"] = "succeeded" if len(complete_predictions) == 6 else "partial"
    m.write_json(report_path(root), report)
    lines = ["# 六家关闭思考：EStG-150模型补充比较", "",
             f"状态：{report['status']}；实际新调用 {report['actual_calls']}/900，0重试。", "",
             "同一150条、原v6提示词；主指标为coarse五字段pooled P/R/F1，modality独立。未完成平台的性能为null。", "",
             "| 平台 | 型号 | 调用/150 | 有效输出 | P | R | F1 |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for provider, row in report["providers"].items():
        metric = row["metrics"]
        score = " | ".join(f"{metric['overall'][k]:.4f}" for k in ("precision", "recall", "f1")) if metric else "null | null | null"
        lines.append(f"| {provider} | {row['model']} | {row['attempted']} | {row.get('valid_predictions', 0)} | {score} |")
    lines += ["", "费用为公开价格下的保守未命中缓存估算，缺失用量保留预留；未核对账户实扣。", "",
              *["- " + item for item in report["limitations"]]]
    report_path(root, ".md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    artifacts[report_path(root).relative_to(root).as_posix()] = m.digest(report_path(root).read_bytes())
    artifacts[report_path(root, ".md").relative_to(root).as_posix()] = m.digest(report_path(root, ".md").read_bytes())
    for path in batch_dir(root).rglob("*.json"):
        if path != batch_dir(root) / "manifest.json":
            artifacts[path.relative_to(root).as_posix()] = m.digest(path.read_bytes())
    m.write_json(batch_dir(root) / "manifest.json", {"task_id": TASK, "run_id": RUN_ID,
         "status": report["status"], "llm_calls": report["actual_calls"], "retry": 0,
         "source_bindings": batch["source_bindings"], "artifacts": artifacts,
         "report": report_path(root).relative_to(root).as_posix()})
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
        print(json.dumps({"status": result["status"], "actual_calls": result["actual_calls"]}), flush=True)
    elif args.summarize:
        result = summarize()
        print(json.dumps({"status": result["status"], "actual_calls": result["actual_calls"]}), flush=True)
    else:
        prepare()


if __name__ == "__main__":
    main()
