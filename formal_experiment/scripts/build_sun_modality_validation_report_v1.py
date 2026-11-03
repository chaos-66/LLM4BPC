"""Evaluate a complete validation batch; incomplete runs never get final scores."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import prepare_sun_modality_validation_v1 as prepared
import run_sun_modality_validation_v1 as runner
import build_sun_modality_fewshot_report_v1 as stats
from prepare_sun_modality_fewshot_v1 import write_frozen
from bpc_hybrid.modality_benchmark import boundary, data
from bpc_hybrid.modality_benchmark.metrics import LABELS, evaluate

REPORT = ROOT / "outputs/reports/sun_modality_validation_v1"


def compare(ids, gold, old, new):
    if not (len(ids) == len(gold) == len(old) == len(new)) or len(ids) != len(set(ids)):
        raise ValueError("paired population mismatch")
    before, after = evaluate(gold, old), evaluate(gold, new)
    paired = stats.paired(gold, old, new)
    ci = stats.bootstrap_delta(gold, old, new)
    ci["method"] = "paired percentile bootstrap; all " + str(len(ids)) + " samples including parse failures"
    ci["delta"] = "review minus fewshot"
    changed = [{"sample_id": sid, "gold": g, "fewshot": a, "review": b,
                "transition": "corrected" if b == g else "regressed" if a == g else "both_wrong"}
               for sid, g, a, b in zip(ids, gold, old, new) if a != b]
    return {"fewshot": before, "review": after, "delta_macro_f1": after["macro_f1"] - before["macro_f1"],
            "paired": paired, "bootstrap": ci, "changed_predictions": changed,
            "per_class_f1_delta": {c: after["per_class"][c]["f1"] - before["per_class"][c]["f1"] for c in LABELS},
            "old_errors": sum(a != g for a, g in zip(old, gold)),
            "old_correct": sum(a == g for a, g in zip(old, gold)),
            "interpretation": "Report gains and losses jointly; positive total does not imply every class improved."}


def main(authorization_path):
    if REPORT.with_suffix(".json").exists() or REPORT.with_suffix(".md").exists():
        raise ValueError("final report already exists")
    plan = prepared.verify_frozen()
    auth_raw = Path(authorization_path).read_bytes()
    auth = json.loads(auth_raw)
    runner.verify_authorization(auth, plan, boundary.digest(prepared.REPORT.read_bytes()))
    execution_plan = json.loads(runner.EXECUTION_PLAN.read_text(encoding="utf-8"))["payload"]
    request_rows = [{"sample_id": r["call_id"], "fewshot_request_sha256": r["request_sha256"]} for r in plan["requests"]]
    expected_execution = {"authorization": auth, "authorization_sha256": boundary.digest(auth_raw),
                          "validation_preflight_sha256": boundary.digest(prepared.REPORT.read_bytes()),
                          "requests": request_rows}
    if execution_plan != expected_execution:
        raise ValueError("execution plan drift")
    # Full coverage/usage/hash/budget audit precedes reading held-out labels.
    finished, audit = stats.verify_journal(boundary.read_events(runner.JOURNAL), request_rows, auth)
    historical = ROOT / plan["contract"]["bindings"]["historical_journal"]["path"]
    old_test = {r["sample_id"]: r["label"] for r in boundary.read_events(historical) if r["kind"] == "finished"}
    comparisons = {}
    for split in ("test", "dev"):
        rows = data.load_split(split)
        ids, gold = [r.sample_id for r in rows], [r.label for r in rows]
        old = [old_test[sid] if split == "test" else finished["dev:fewshot:" + sid]["label"] for sid in ids]
        new = [finished[split + ":review:" + sid]["label"] for sid in ids]
        comparisons[split] = compare(ids, gold, old, new)
    historical_metrics = json.loads((ROOT / plan["contract"]["bindings"]["historical_result"]["path"]).read_text(encoding="utf-8"))["metrics"]["fewshot"]
    if comparisons["test"]["fewshot"] != historical_metrics:
        raise ValueError("historical few-shot metrics do not reproduce")
    result = {"suite_id": plan["suite_id"], "completed": True, "execution_audit": audit,
              "comparisons": comparisons, "new_api_calls": audit["attempted"],
              "journal_sha256": boundary.digest(runner.JOURNAL.read_bytes()),
              "preflight_sha256": boundary.digest(prepared.REPORT.read_bytes()),
              "authorization_sha256": boundary.digest(auth_raw),
              "limitations": plan["contract"]["limitations"]}
    lines = ["# reviewer提示词验证：实际运行结果", "",
             "test为已见错误的探索性历史对照；dev为冻结prompt后的同期双臂留出验证。", "",
             "| 划分 | few-shot Macro-F1 | reviewer Macro-F1 | 差值 | 改对 | 改错 |", "|---|---:|---:|---:|---:|---:|"]
    for split, c in comparisons.items():
        lines.append(f"| {split} | {c['fewshot']['macro_f1']:.4f} | {c['review']['macro_f1']:.4f} | {c['delta_macro_f1']:+.4f} | {c['paired']['corrected']} | {c['paired']['regressed']} |")
    lines += ["", "两组四类完整P/R/F1、FP/FN、变化编号和配对区间见JSON；不得只引用改对数量。", ""]
    lines += ["- " + note for note in result["limitations"]]
    write_frozen(REPORT.with_suffix(".json"), (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode())
    write_frozen(REPORT.with_suffix(".md"), ("\n".join(lines) + "\n").encode())
    print(json.dumps({split: {k: value[k] for k in ("delta_macro_f1", "old_errors", "old_correct")}
                      for split, value in comparisons.items()}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorization", type=Path, required=True)
    main(parser.parse_args().authorization)
