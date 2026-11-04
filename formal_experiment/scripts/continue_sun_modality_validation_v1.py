"""Supervised continuation of never-attempted calls, under the original grant.

The original runner/ledger remain frozen. Its one HTTP429 is never retried and
its entire unresolved reservation remains charged against the global budget.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import prepare_sun_modality_validation_v1 as prepared
import run_sun_modality_validation_v1 as original
import build_sun_modality_fewshot_report_v1 as stats
from build_sun_modality_validation_report_v1 import compare
from prepare_sun_modality_fewshot_v1 import write_frozen
from bpc_hybrid.modality_benchmark import boundary, data, llm_se
from bpc_hybrid.modality_benchmark.metrics import LABELS, evaluate

AUTH = ROOT / "configs/authorization/sun_modality_validation_20261104_v1.json"
INTERRUPTION = ROOT / "outputs/reports/sun_modality_validation_v1_interruption.json"
PLAN = ROOT / "outputs/reports/sun_modality_validation_v1_continuation_preflight.json"
RUN = ROOT / "outputs/development/sun_modality_validation_v1/continuation_v1"
JOURNAL = RUN / "local_only/events.jsonl"
EXECUTION_PLAN = RUN / "execution_preflight.json"
REPORT = ROOT / "outputs/reports/sun_modality_validation_v1_completed"


def remaining_scope(requests, events, cap_cny):
    expected = {r["call_id"]: r["request_sha256"] for r in requests}
    if len(expected) != len(requests):
        raise ValueError("duplicate planned call")
    attempted, spent, uncertain = boundary.accounting(events)
    for row in events:
        if row["sample_id"] not in expected or row["request_sha256"] != expected[row["sample_id"]]:
            raise ValueError("parent request mismatch")
    remaining = [r for r in requests if r["call_id"] not in attempted]
    available = cap_cny - spent - uncertain
    if available <= 0:
        raise ValueError("no global budget remains")
    return remaining, available


def verify_parent(plan, auth, snapshot):
    path = ROOT / snapshot["journal_path"]
    if boundary.digest(path.read_bytes()) != snapshot["journal_sha256"]:
        raise ValueError("parent ledger drift")
    events = boundary.read_events(path)
    starts = {r["sample_id"]: r for r in events if r["kind"] == "started"}
    done = {r["sample_id"]: r for r in events if r["kind"] == "finished"}
    if set(starts) != set(done) or len(done) != 734:
        raise ValueError("parent completion population mismatch")
    bad = [r for r in done.values() if stats.run.failed(r)]
    if len(bad) != 1:
        raise ValueError("only the recorded single HTTP429 is permitted")
    failure = bad[0]
    if not (failure["sample_id"] == snapshot["failed_request"]["sample_id"]
            and failure["http_status"] == 429 and failure["request_status"] == "error"
            and failure["body_hash_match"] and failure["raw_content"] == ""
            and failure["response_sha256"] == boundary.digest(b"")
            and failure["label"] is None and not failure["usage_verified"]
            and failure["usage"] == {} and failure["cost_cny"] == 0):
        raise ValueError("recorded failure changed")
    failed_id = failure["sample_id"]
    good_requests = [{"sample_id": r["call_id"], "fewshot_request_sha256": r["request_sha256"]}
                     for r in plan["requests"] if r["call_id"] in done and r["call_id"] != failed_id]
    good_events = [r for r in events if r["sample_id"] != failed_id]
    _, audit = stats.verify_journal(good_events, good_requests, auth)
    # Check the global reservation trace, retaining the unresolved failure hold.
    held, spent = {}, 0.0
    for row in events:
        if row["kind"] == "started":
            if llm_se.rate_for(datetime.fromisoformat(row["timestamp"]))[0] != "off_peak":
                raise ValueError("parent request outside off-peak")
            held[row["sample_id"]] = row["reserved_cny"]
        elif row["sample_id"] != failed_id:
            spent += row["cost_cny"]
            held.pop(row["sample_id"])
        if spent + sum(held.values()) > auth["cap_cny"] + 1e-10:
            raise ValueError("initial global reservation exceeds authorization")
    remaining, available = remaining_scope(plan["requests"], events, auth["cap_cny"])
    if remaining != snapshot["remaining_requests"] or len(remaining) != 532:
        raise ValueError("never-attempted set differs from interruption snapshot")
    if abs(available - snapshot["remaining_global_budget_cny"]) > 1e-10:
        raise ValueError("remaining budget drift")
    return done, audit, remaining, available


def build_plan():
    plan = prepared.verify_frozen()
    auth = json.loads(AUTH.read_text(encoding="utf-8"))
    original.verify_authorization(auth, plan, boundary.digest(prepared.REPORT.read_bytes()))
    snapshot = json.loads(INTERRUPTION.read_text(encoding="utf-8"))
    if boundary.digest(AUTH.read_bytes()) != snapshot["authorization_sha256"]:
        raise ValueError("original grant drift")
    done, audit, remaining, available = verify_parent(plan, auth, snapshot)
    derived = dict(auth, max_calls=len(remaining), cap_cny=available, max_workers=4,
                   continuation_note="Subset of original approval only; initial known costs AND unresolved reservation deducted.")
    return {"suite_id": plan["suite_id"], "requests": remaining, "derived_limits": derived,
            "original_authorization_sha256": boundary.digest(AUTH.read_bytes()),
            "original_preflight_sha256": boundary.digest(prepared.REPORT.read_bytes()),
            "interruption_sha256": boundary.digest(INTERRUPTION.read_bytes()),
            "parent_journal_sha256": snapshot["journal_sha256"],
            "source_sha256_lf_utf8": boundary.digest(Path(__file__).read_text(encoding="utf-8").encode()),
            "known_parent_cost_cny": snapshot["known_cost_cny"],
            "retained_uncertain_cny": snapshot["unsettled_reservation_cny"],
            "minimum_dispatch_interval_seconds": 1.0, "initial_failed_call_retained_as_no_prediction": True,
            "no_new_user_budget": True, "already_attempted_calls_never_resent": len(done),
            "collection_status": "prepared_no_continuation_calls", "performance_metrics": None}


def verify_plan():
    frozen = json.loads(PLAN.read_text(encoding="utf-8"))
    if build_plan() != frozen:
        raise ValueError("continuation plan drift")
    return frozen


def paced(send, interval=1.0, clock=time.monotonic, sleep=time.sleep, allowed=None):
    lock, next_time = threading.Lock(), [0.0]
    def dispatch(*args):
        with lock:
            delay = next_time[0] - clock()
            if delay > 0:
                sleep(delay)
            next_time[0] = clock() + interval
        if allowed is not None and not allowed():
            raise RuntimeError("off-peak window closed before transport; no request sent")
        return send(*args)
    return dispatch


def execute():
    plan = verify_plan()
    engine, payload = original.make_engine({"requests": plan["requests"]}, plan["derived_limits"],
                                          plan["original_authorization_sha256"])
    engine.RUN, engine.JOURNAL, engine.PLAN = RUN, JOURNAL, EXECUTION_PLAN
    engine.send_one = paced(engine.send_one, allowed=lambda: llm_se.rate_for(datetime.now(llm_se.BEIJING))[0] == "off_peak")
    write_frozen(EXECUTION_PLAN, (json.dumps({"payload": payload}, ensure_ascii=False, indent=2) + "\n").encode())
    engine.execute()


def report():
    if REPORT.with_suffix(".json").exists() or REPORT.with_suffix(".md").exists():
        raise ValueError("completed report already exists")
    continuation = verify_plan()
    full_plan = json.loads(prepared.REPORT.read_text(encoding="utf-8"))
    auth = json.loads(AUTH.read_text(encoding="utf-8"))
    snapshot = json.loads(INTERRUPTION.read_text(encoding="utf-8"))
    initial, initial_audit, _, _ = verify_parent(full_plan, auth, snapshot)
    requests = [{"sample_id": r["call_id"], "fewshot_request_sha256": r["request_sha256"]} for r in continuation["requests"]]
    execution = json.loads(EXECUTION_PLAN.read_text(encoding="utf-8"))["payload"]
    if execution != {"authorization": continuation["derived_limits"],
                     "authorization_sha256": continuation["original_authorization_sha256"],
                     "validation_preflight_sha256": continuation["original_preflight_sha256"], "requests": requests}:
        raise ValueError("continuation execution binding mismatch")
    final, final_audit = stats.verify_journal(boundary.read_events(JOURNAL), requests, continuation["derived_limits"])
    if set(initial) & set(final) or set(initial) | set(final) != {r["call_id"] for r in full_plan["requests"]}:
        raise ValueError("combined attempts repeat or omit original calls")
    finished = {**initial, **final}
    cost = snapshot["known_cost_cny"] + final_audit["actual_cost_cny"]
    bound = cost + snapshot["unsettled_reservation_cny"]
    if bound > auth["cap_cny"]:
        raise ValueError("global cost including unresolved hold exceeds cap")
    historical = ROOT / full_plan["contract"]["bindings"]["historical_journal"]["path"]
    old_test = {r["sample_id"]: r["label"] for r in boundary.read_events(historical) if r["kind"] == "finished"}
    comparisons = {}
    # Only now, after all 1266 calls have been attempted and validated, read labels.
    for split in ("test", "dev"):
        rows = data.load_split(split)
        ids, gold = [r.sample_id for r in rows], [r.label for r in rows]
        old = [old_test[sid] if split == "test" else finished["dev:fewshot:" + sid]["label"] for sid in ids]
        new = [finished[split + ":review:" + sid]["label"] for sid in ids]
        comparisons[split] = compare(ids, gold, old, new)
        if split == "dev":
            failed_source = snapshot["failed_request"]["sample_id"].split(":", 2)[2]
            keep = [i for i, sid in enumerate(ids) if sid != failed_source]
            before = evaluate([gold[i] for i in keep], [old[i] for i in keep])
            after = evaluate([gold[i] for i in keep], [new[i] for i in keep])
            sensitivity = {"n": len(keep), "fewshot": before, "review": after,
                           "delta_macro_f1": after["macro_f1"] - before["macro_f1"],
                           "scope": "Failure-only sensitivity excludes the single 429 pair; primary retains all420."}
    reference = json.loads((ROOT / full_plan["contract"]["bindings"]["historical_result"]["path"]).read_text(encoding="utf-8"))["metrics"]["fewshot"]
    if comparisons["test"]["fewshot"] != reference:
        raise ValueError("historical metrics do not reproduce")
    result = {"suite_id": full_plan["suite_id"], "all_planned_calls_attempted": 1266, "retries": 0,
              "failed_transport_calls": 1, "known_cost_cny": cost, "retained_uncertain_cny": snapshot["unsettled_reservation_cny"],
              "cost_upper_bound_with_hold_cny": bound, "comparisons": comparisons,
              "dev_response_only_sensitivity": sensitivity, "initial_successful_calls_audit": initial_audit,
              "continuation_audit": final_audit, "failed_request": snapshot["failed_request"],
              "original_preflight_sha256": continuation["original_preflight_sha256"],
              "original_authorization_sha256": continuation["original_authorization_sha256"],
              "initial_journal_sha256": snapshot["journal_sha256"], "continuation_journal_sha256": boundary.digest(JOURNAL.read_bytes()),
              "continuation_preflight_sha256": boundary.digest(PLAN.read_bytes()),
              "limitations": full_plan["contract"]["limitations"] + [
                  "首次734条因429停止，监督式续跑仅发532条未尝试请求；并发8降4并限制发送间隔，未改prompt。",
                  "原429无预测计入dev few-shot主指标分母；419条有响应配对只作失败敏感性诊断，不替换420条主结果。",
                  "429没有返回计费信息，费用报告为已知金额及保守预留上界，不能断言该条免费。"]}
    lines = ["# reviewer提示词：完整调用人口与配对验证", "",
             f"1266个计划调用各尝试一次、零重试；1条429失败保留分母。已知费用¥{cost:.6f}，加未结算预留后的上界¥{bound:.6f}。", "",
             "| 划分 | few-shot Macro-F1 | reviewer Macro-F1 | 差值 | 改对 | 改错 |", "|---|---:|---:|---:|---:|---:|"]
    for split, c in comparisons.items():
        lines.append(f"| {split} | {c['fewshot']['macro_f1']:.4f} | {c['review']['macro_f1']:.4f} | {c['delta_macro_f1']:+.4f} | {c['paired']['corrected']} | {c['paired']['regressed']} |")
    lines += ["", "| 划分/类别 | few-shot F1 | reviewer F1 |", "|---|---:|---:|"]
    for split, c in comparisons.items():
        for label in LABELS:
            lines.append(f"| {split}/{label} | {c['fewshot']['per_class'][label]['f1']:.4f} | {c['review']['per_class'][label]['f1']:.4f} |")
    for split, c in comparisons.items():
        lo, hi = c['bootstrap']['ci95']['macro_f1']
        lines.append(f"\n{split}配对Macro-F1差值95%区间：[{lo:+.4f}, {hi:+.4f}]。\n")
    lines += [f"dev去除唯一429配对的敏感性差值：{sensitivity['delta_macro_f1']:+.4f}，n=419。", ""]
    lines += ["- " + note for note in result["limitations"]]
    write_frozen(REPORT.with_suffix(".json"), (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode())
    write_frozen(REPORT.with_suffix(".md"), ("\n".join(lines) + "\n").encode())
    print(json.dumps({"known_cost_cny": cost, "upper_with_hold_cny": bound,
                      "comparisons": {s: {"old_macro_f1": c["fewshot"]["macro_f1"], "new_macro_f1": c["review"]["macro_f1"],
                                          "corrected": c["paired"]["corrected"], "regressed": c["paired"]["regressed"],
                                          "ci95": c["bootstrap"]["ci95"]["macro_f1"]} for s, c in comparisons.items()}}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preflight", "execute", "report"))
    mode = parser.parse_args().mode
    if mode == "preflight":
        plan = build_plan()
        write_frozen(PLAN, (json.dumps(plan, ensure_ascii=False, indent=2) + "\n").encode())
        print(json.dumps({"remaining_calls": len(plan["requests"]), "remaining_cap_cny": plan["derived_limits"]["cap_cny"],
                          "already_attempted_calls_not_resent": plan["already_attempted_calls_never_resent"]}))
    else:
        execute() if mode == "execute" else report()
