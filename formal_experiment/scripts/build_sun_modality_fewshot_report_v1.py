"""Offline paired evaluation of the completed, authorized few-shot batch."""
from __future__ import annotations

import json
import random
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import run_sun_modality_fewshot_v1 as run
import build_sun_modality_boundary_stats_v1 as stats
from bpc_hybrid.modality_benchmark import boundary, data, fewshot, llm_se
from bpc_hybrid.modality_benchmark.metrics import LABELS, evaluate

REPORT = ROOT / "outputs/reports/sun_modality_fewshot_v1"
B = 10_000
SEED = 20261103


def paired(gold, old, new):
    groups = {c: {"corrected": 0, "regressed": 0, "both_correct": 0, "both_wrong": 0} for c in LABELS}
    for g, a, b in zip(gold, old, new):
        ca, cb = a == g, b == g
        key = "both_correct" if ca and cb else "corrected" if cb else "regressed" if ca else "both_wrong"
        groups[g][key] += 1
    corrected = sum(x["corrected"] for x in groups.values())
    regressed = sum(x["regressed"] for x in groups.values())
    return {"corrected": corrected, "regressed": regressed, "by_gold_class": groups,
            "mcnemar_accuracy_p_exact_two_sided": stats.mcnemar_exact_two_sided(corrected, regressed),
            "test_scope": "paired accuracy, not macro-F1; exploratory unadjusted p-value"}


def f1_vector(gold, pred):
    tp, fp, fn = [0] * 4, [0] * 4, [0] * 4
    for g, p in zip(gold, pred):
        if g == p:
            tp[g] += 1
        else:
            fn[g] += 1
            if p >= 0:
                fp[p] += 1
    return [stats.prf(tp[i], fp[i], fn[i]) for i in range(4)]


def bootstrap_delta(gold, old, new, repeats=B):
    label_index = {c: i for i, c in enumerate(LABELS)}
    g = [label_index[x] for x in gold]
    a = [-1 if x is None else label_index[x] for x in old]
    b = [-1 if x is None else label_index[x] for x in new]
    for pred, encoded in ((old, a), (new, b)):
        reference = evaluate(gold, pred)
        got = f1_vector(g, encoded)
        assert all(abs(got[i] - reference["per_class"][c]["f1"]) < 1e-12 for i, c in enumerate(LABELS))
    samples = {c: [] for c in (*LABELS, "macro_f1")}
    rng = random.Random(SEED)
    for _ in range(repeats):
        idx = rng.choices(range(len(g)), k=len(g))
        gi = [g[i] for i in idx]
        va, vb = f1_vector(gi, [a[i] for i in idx]), f1_vector(gi, [b[i] for i in idx])
        for i, c in enumerate(LABELS):
            samples[c].append(vb[i] - va[i])
        samples["macro_f1"].append((sum(vb) - sum(va)) / 4)
    return {"method": "paired nonparametric percentile bootstrap; all 426 including failures",
            "B": repeats, "seed": SEED, "delta": "fewshot minus boundary",
            "ci95": {c: stats.percentile_ci(v) for c, v in samples.items()}}


def verify_journal(events, requests, auth):
    """Check request identity, raw responses, usage, time window, and peak reservation."""
    expected = {x["sample_id"]: x["fewshot_request_sha256"] for x in requests}
    starts, finishes, held = {}, {}, {}
    spent, peak_reserved_total, peak_in_flight = 0.0, 0.0, 0
    for row in events:
        sid = row["sample_id"]
        if row["request_sha256"] != expected[sid]:
            raise ValueError("request binding mismatch")
        if row["kind"] == "started":
            if sid in starts:
                raise ValueError("duplicate start")
            starts[sid] = row
            held[sid] = row["reserved_cny"]
            if llm_se.rate_for(datetime.fromisoformat(row["timestamp"]))[0] != "off_peak":
                raise ValueError("request outside off-peak window")
            peak_reserved_total = max(peak_reserved_total, spent + sum(held.values()))
            peak_in_flight = max(peak_in_flight, len(held))
            if spent + sum(held.values()) > auth["cap_cny"] + 1e-10:
                raise ValueError("concurrent reservation exceeds cap")
        else:
            if sid not in starts or sid in finishes or run.failed(row):
                raise ValueError("failed or unmatched completion")
            if boundary.digest(row["raw_content"].encode()) != row["response_sha256"]:
                raise ValueError("response hash mismatch")
            if row["returned_model"] not in run.base.ACCEPTED_MODELS:
                raise ValueError("unexpected returned model")
            parsed = llm_se.extract_modality_label(row["raw_content"]) if row["raw_content"] else {"label": None, "status": "no_content"}
            if (row["label"], row["parse_status"]) != (parsed["label"], parsed["status"]):
                raise ValueError("saved parsing disagrees with raw output")
            if not run.usage_valid(row["usage"]):
                raise ValueError("invalid provider usage")
            price = auth["price_cny_per_million"][starts[sid]["price_window"]]
            cost = llm_se.cost_cny(row["usage"], price)
            if abs(cost - row["cost_cny"]) > 1e-12 or cost > held[sid]:
                raise ValueError("cost mismatch or reservation underestimate")
            spent += cost
            held.pop(sid)
            finishes[sid] = row
    if set(starts) != set(finishes) or set(starts) != set(expected) or held:
        raise ValueError("batch incomplete; refusing final performance report")
    if len(starts) > auth["max_calls"] or peak_in_flight > auth["max_workers"]:
        raise ValueError("call or concurrency limit exceeded")
    return finishes, {"attempted": len(starts), "finished": len(finishes), "actual_cost_cny": spent,
                      "peak_spent_plus_reserved_cny": peak_reserved_total, "peak_in_flight": peak_in_flight,
                      "all_request_hashes_match": True, "all_response_hashes_match": True,
                      "all_usage_verified": True, "all_requests_off_peak": True,
                      "parse_status_counts": dict(Counter(x["parse_status"] for x in finishes.values())),
                      "returned_models": dict(Counter(x["returned_model"] for x in finishes.values()))}


def main():
    if REPORT.with_suffix(".json").exists() or REPORT.with_suffix(".md").exists():
        raise ValueError("report exists; refusing overwrite")
    payload = run.plan_payload()
    if payload != json.loads(run.PLAN.read_text(encoding="utf-8"))["payload"]:
        raise ValueError("execution source/plan drift")
    finished, audit = verify_journal(boundary.read_events(run.JOURNAL), payload["requests"], payload["authorization"])
    contract = fewshot.read_contract()
    parent_path = ROOT / contract["historical_boundary"]["path"]
    parent = json.loads(parent_path.read_text(encoding="utf-8"))
    old_journal = ROOT / "outputs/development/sun_modality_boundary_v1/local_only/events.jsonl"
    if boundary.digest(old_journal.read_bytes()) != parent["journal_sha256"]:
        raise ValueError("historical boundary journal drift")
    controls = {"boundary": {x["sample_id"]: x["label"] for x in boundary.read_events(old_journal) if x["kind"] == "finished"}}
    for name, key, field in (("v6", "historical_llm", "label"), ("sun", "historical_sun", "predicted")):
        spec = parent["contract"][key]
        path = ROOT / spec["path"]
        if boundary.digest(path.read_bytes()) != spec["sha256"]:
            raise ValueError("historical control drift: " + name)
        controls[name] = {x["sample_id"]: x[field] for x in run.base.read_jsonl(path)}
    rows = data.load_split("test")  # Evaluation only, after all inference is complete.
    ids, gold = [x.sample_id for x in rows], [x.label for x in rows]
    for name, preds in controls.items():
        if set(preds) != set(ids):
            raise ValueError("historical population mismatch: " + name)
    controls["fewshot"] = {sid: x["label"] for sid, x in finished.items()}
    predictions = {name: [pred.get(sid) for sid in ids] for name, pred in controls.items()}
    metrics = {name: evaluate(gold, pred) for name, pred in predictions.items()}
    for name, key in (("boundary", "boundary"), ("v6", "baseline"), ("sun", "sun")):
        if metrics[name] != parent["metrics"][key]:
            raise ValueError("historical metrics do not reproduce: " + name)
    comparisons = {name: paired(gold, predictions[name], predictions["fewshot"]) for name in ("boundary", "v6", "sun")}
    bootstrap = bootstrap_delta(gold, predictions["boundary"], predictions["fewshot"])
    changed = [{"sample_id": sid, "gold": g, **{k: pred[i] for k, pred in predictions.items()}}
               for i, (sid, g) in enumerate(zip(ids, gold)) if predictions["boundary"][i] != predictions["fewshot"][i]]
    errors = [{"sample_id": sid, "gold": g, **{k: pred[i] for k, pred in predictions.items()}}
              for i, (sid, g) in enumerate(zip(ids, gold)) if predictions["fewshot"][i] != g]
    result = {"suite_id": contract["suite_id"], "created_at": run.base.now(), "completed": True,
              "claim_scope": contract["claim_scope"], "execution_audit": audit, "metrics": metrics,
              "paired_fewshot_vs_control": comparisons, "bootstrap_delta_vs_boundary": bootstrap,
              "changed_predictions_vs_boundary": changed, "fewshot_errors": errors,
              "journal_sha256": boundary.digest(run.JOURNAL.read_bytes()),
              "execution_preflight_sha256": boundary.digest(run.PLAN.read_bytes()),
              "prepared_preflight_sha256": payload["authorization"]["prepared_preflight_sha256"],
              "authorization_sha256": payload["authorization_sha256"],
              "historical_boundary_report_sha256": boundary.digest(parent_path.read_bytes()),
              "evaluation_sources_sha256_lf_utf8": {p: boundary.digest((ROOT / p).read_text(encoding="utf-8").encode()) for p in
                  ("scripts/build_sun_modality_fewshot_report_v1.py", "scripts/build_sun_modality_boundary_stats_v1.py", "src/bpc_hybrid/modality_benchmark/metrics.py")},
              "limitations": ["选例家族参考了测试错误，属于探索性结果，不是独立盲测或已证明的上界。",
                  "对照使用历史预测；模型服务时间与本次8路并发/缓存状态不同，不能视为严格同期因果实验。",
                  "全部426条计入分母；解析无有效标签按失败处理，不重试或猜测标签。",
                  "McNemar检验针对accuracy，bootstrap针对F1差值；均为测试集内的不确定性描述，不消除选择偏差。",
                  "Sun是本地独立重建；本结果不替换冻结论文主表。"]}
    run.base.write_new(REPORT.with_suffix(".json"), result)
    lines = ["# 18例语料 few-shot 探索性对照", "",
             f"- 完成426/426次、零重试；费用¥{audit['actual_cost_cny']:.6f}；解析状态{audit['parse_status_counts']}。",
             "- 相对boundary仅追加已冻结的18例示范块；全部请求字节与预检一致。", "",
             "| 方法 | Accuracy | Macro-F1 | definition F1 | obligation F1 | permission F1 | prohibition F1 |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for name in ("v6", "boundary", "fewshot", "sun"):
        m = metrics[name]
        values = [m["accuracy"], m["macro_f1"]] + [m["per_class"][c]["f1"] for c in LABELS]
        lines.append("| " + name + " | " + " | ".join(f"{x:.4f}" for x in values) + " |")
    lines += ["", "| 类别 | boundary P/R | few-shot P/R | FP变化 | 改对 | 改错 |",
              "|---|---:|---:|---:|---:|---:|"]
    for c in LABELS:
        a, b = metrics["boundary"]["per_class"][c], metrics["fewshot"]["per_class"][c]
        t = comparisons["boundary"]["by_gold_class"][c]
        lines.append(f"| {c} | {a['precision']:.4f}/{a['recall']:.4f} | {b['precision']:.4f}/{b['recall']:.4f} | {a['fp']}→{b['fp']} | {t['corrected']} | {t['regressed']} |")
    lines += ["", "| 对照 | few-shot改对 | few-shot改错 | McNemar双侧p（accuracy） |", "|---|---:|---:|---:|"]
    for name, comp in comparisons.items():
        lines.append(f"| {name} | {comp['corrected']} | {comp['regressed']} | {comp['mcnemar_accuracy_p_exact_two_sided']:.6g} |")
    delta = metrics["fewshot"]["macro_f1"] - metrics["boundary"]["macro_f1"]
    lo, hi = bootstrap["ci95"]["macro_f1"]
    lines += ["", f"- 相对boundary的Macro-F1差值：{delta:+.4f}；配对bootstrap 95%CI [{lo:+.4f}, {hi:+.4f}]（B={B}，seed={SEED}）。",
              f"- few-shot错误共{len(errors)}条；逐条编号、标签与改动见JSON，不含德语原句。", ""]
    lines += ["- " + note for note in result["limitations"]]
    with REPORT.with_suffix(".md").open("x", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    print(json.dumps({"report": str(REPORT), "audit": audit, "macro_f1": metrics["fewshot"]["macro_f1"],
                      "delta_vs_boundary": delta, "paired_vs_boundary": comparisons["boundary"], "ci95": [lo, hi]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
