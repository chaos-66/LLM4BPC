"""Execute the authorized, frozen sentence candidate and report both readouts.

Reuses the existing budget-reserving coordinator and official transport. The
prepared prompt/parser/evaluator are immutable. No .env, automatic retry, Gold
at execution time, or prompt changes. Raw German/returns remain local only.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
import prepare_sun_modality_sentence_v1 as prepared
import run_sun_modality_boundary_v1 as base
import run_sun_modality_fewshot_v1 as coordinator
from continue_sun_modality_validation_v1 import paced
from prepare_sun_modality_fewshot_v1 import write_frozen
from bpc_hybrid.modality_benchmark import boundary, data, llm_se, sentence
from bpc_hybrid.modality_benchmark.metrics import LABELS

AUTH = ROOT / "configs/authorization/sun_modality_sentence_20261110_v1.json"
RUN = prepared.LOCAL / "execution_v1"
PLAN = RUN / "execution_preflight.json"
JOURNAL = RUN / "local_only/events.jsonl"
FREEZE = ROOT / "outputs/reports/sun_modality_sentence_v1_execution_preflight.json"
RESULT = ROOT / "outputs/reports/sun_modality_sentence_v1_completed.json"
APPROVED = "9b608fcb0423f9bf836d06b082fcdd8765633b045281901d149bff13d649123d"
LIMITS = dict(suite_id=sentence.SUITE_ID, execute_authorized=True, max_calls=426,
              cap_cny=35.0, max_workers=4, retries=0, off_peak_only=True,
              minimum_dispatch_interval_seconds=1.0, endpoint="https://api.deepseek.com",
              model=llm_se.MODEL_ALIAS, price_cny_per_million=llm_se.PRICE_CNY_PER_MILLION)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def authorize(auth, preflight_sha):
    expected = dict(LIMITS, approved_preflight_sha256=APPROVED,
                    sampling=dict(temperature=0.0, top_p=1.0, max_tokens=4096,
                                  stream=False, thinking={"type": "disabled"}))
    if (preflight_sha != APPROVED or any(auth.get(k) != v for k, v in expected.items())
            or not auth.get("user_text")):
        raise ValueError("fresh authorization must match the approved candidate and limits")


def verify_prepared():
    """Load only text/IDs; do not invoke prepared.build()'s historical Gold review."""
    frozen = read(prepared.REPORT)
    auth = read(AUTH)
    authorize(auth, boundary.digest(prepared.REPORT.read_bytes()))
    for name, digest in frozen["source_sha256_lf_utf8"].items():
        if boundary.digest((ROOT / name).read_text(encoding="utf-8").encode()) != digest:
            raise ValueError("delivered source changed: " + name)
    system, examples, _, _ = sentence.compose_prompt()  # train-only labels
    if boundary.digest(system.encode()) != frozen["system_prompt_sha256_utf8"]:
        raise ValueError("frozen system differs")
    pairs = data.load_split_text_only("test")
    local = read(prepared.LOCAL / "requests.json")
    requests = frozen["requests"]
    if not len(pairs) == len(local) == len(requests) == 426:
        raise ValueError("expected all 426 prepared requests")
    bodies, request_ids = {}, {}
    for (sid, text), saved, binding in zip(pairs, local, requests, strict=True):
        rid = binding["request_id"]
        body = sentence.request_body(rid, text, system=system, examples=examples)
        if (saved != {"sample_id": sid, "request_id": rid, "body": body}
                or binding["sample_id"] != sid
                or boundary.digest(text.encode()) != binding["source_text_sha256"]
                or boundary.digest(boundary.wire_bytes(body)) != binding["request_sha256"]):
            raise ValueError("request bytes/identity differ from approved candidate")
        bodies[sid], request_ids[sid] = body, rid
    if len(bodies) != 426 or len(set(request_ids.values())) != 426:
        raise ValueError("duplicate target ID")
    sources = [Path(__file__), ROOT / "scripts/run_sun_modality_fewshot_v1.py",
               ROOT / "scripts/run_sun_modality_boundary_v1.py",
               ROOT / "scripts/continue_sun_modality_validation_v1.py",
               ROOT / "src/bpc_hybrid/llm_client.py", ROOT / "src/bpc_hybrid/h1_transport.py",
               ROOT / "src/bpc_hybrid/llm_config.py", ROOT / "tests/test_run_modality_sentence_v1.py"]
    payload = {"authorization": auth, "authorization_sha256": boundary.digest(AUTH.read_bytes()),
               "approved_preflight_sha256": APPROVED,
               "requests": [{"sample_id": r["sample_id"], "request_id": r["request_id"],
                             "fewshot_request_sha256": r["request_sha256"]} for r in requests],
               "source_sha256_lf_utf8": {p.relative_to(ROOT).as_posix(): boundary.digest(p.read_text(encoding="utf-8").encode()) for p in sources}}
    return pairs, bodies, request_ids, payload


def prepare():
    pairs, _, _, payload = verify_prepared()
    full = {"payload": payload}
    write_frozen(PLAN, prepared.serialize(full))
    public = {"suite_id": sentence.SUITE_ID, "planned_requests": len(pairs), "api_calls": 0,
              "authorization_sha256": payload["authorization_sha256"],
              "candidate_preflight_sha256": APPROVED,
              "execution_preflight_sha256": boundary.digest(prepared.serialize(full)),
              "source_sha256_lf_utf8": payload["source_sha256_lf_utf8"],
              "limits": LIMITS, "status": "authorized_awaiting_off_peak"}
    write_frozen(FREEZE, prepared.serialize(public))
    print(json.dumps({"count": len(pairs), "cap_cny": 35, "api_calls": 0,
                      "execution_preflight_sha256": public["execution_preflight_sha256"]}))


def frozen_plan():
    pairs, bodies, ids, payload = verify_prepared()
    if (read(PLAN) != {"payload": payload}
            or boundary.digest(PLAN.read_bytes()) != read(FREEZE)["execution_preflight_sha256"]):
        raise ValueError("execution source/preflight drift")
    return pairs, bodies, ids, payload


def verify_transport_body(config, body, expected_hash):
    from bpc_hybrid.llm_client import OpenAICompatibleRequestBuilder
    from bpc_hybrid.h1_transport import H1RequestPolicy
    if config.base_url != "https://api.deepseek.com" or config.model != llm_se.MODEL_ALIAS:
        raise ValueError("provider/model differs from authorization")
    actual = OpenAICompatibleRequestBuilder(config).build_body(
        body["messages"][0]["content"], body["messages"][1]["content"])
    actual = H1RequestPolicy(stream=False, thinking={"type": "disabled"}, response_format=None).apply_to_body(actual)
    if boundary.digest(json.dumps(actual).encode()) != expected_hash:
        raise ValueError("transport would send different request bytes")


def adapt_finished(row, *, sample_id, request_id, source_text):
    row = dict(row, sample_id=sample_id, request_id=request_id)
    ok = not coordinator.failed(row)
    parsed = sentence.parse_response(row["raw_content"], request_id=request_id,
                                     source_text=source_text, request_ok=ok)
    clauses = (parsed["rule_record"] or {}).get("clauses", [])
    row.update(label=parsed["label"], parse_status=parsed["status"],
               first_clause_label=parsed["first_clause_label"],
               first_clause_status=parsed["first_clause_status"],
               sentence_uncertainty=parsed["uncertainty"],
               sentence_errors=parsed["sentence_errors"],
               rule_record_validation=parsed["rule_record_validation"],
               clauses=len(clauses) if isinstance(clauses, list) else 0)
    return row


def make_engine(pairs, bodies, request_ids, payload):
    spec = importlib.util.spec_from_file_location("sentence_execution_engine", ROOT / "scripts/run_sun_modality_fewshot_v1.py")
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    engine.RUN, engine.JOURNAL, engine.PLAN = RUN, JOURNAL, PLAN
    engine.data = SimpleNamespace(load_split_text_only=lambda _: pairs)
    engine.fewshot = SimpleNamespace(load_demonstrations=lambda: ("", {}),
                                    request_body=lambda sid, text, *, block: bodies[sid])
    engine.plan_payload = lambda: payload
    raw_send = paced(engine.send_one, interval=payload["authorization"]["minimum_dispatch_interval_seconds"],
                     allowed=lambda: llm_se.rate_for(datetime.now(llm_se.BEIJING))[0] == "off_peak")

    def send(config, sid, text, body, request_hash, rate):
        try:
            verify_transport_body(config, body, request_hash)
            row = raw_send(config, request_ids[sid], text, body, request_hash, rate)
        except Exception as exc:
            # Safe class only, no credential/body/header/exception text in logs.
            row = {"kind": "finished", "timestamp": base.now(), "request_sha256": request_hash,
                   "body_hash_match": False, "returned_model": None, "model_accepted": False,
                   "request_status": "error", "error_type": type(exc).__name__, "http_status": None,
                   "raw_content": "", "response_sha256": boundary.digest(b""), "usage": {},
                   "usage_verified": False, "cost_cny": 0.0, "latency_seconds": 0.0}
        return adapt_finished(row, sample_id=sid, request_id=request_ids[sid], source_text=text)
    engine.send_one = send
    return engine


def execute(wait_for_off_peak=False):
    RUN.mkdir(parents=True, exist_ok=True)
    waiting_lock = RUN / "dispatch_owner.lock"
    os.close(os.open(waiting_lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    try:
        # Lock ownership is acquired before waiting; no credentials or sends while waiting.
        frozen_plan()
        if wait_for_off_peak and llm_se.rate_for(datetime.now(llm_se.BEIJING))[0] != "off_peak":
            print(json.dumps({"status": "waiting_for_off_peak", "not_before_beijing": "2026-11-10T18:00:00+08:00", "api_calls": 0}), flush=True)
            while llm_se.rate_for(datetime.now(llm_se.BEIJING))[0] != "off_peak":
                time.sleep(30)
        pairs, bodies, request_ids, payload = frozen_plan()
        engine = make_engine(pairs, bodies, request_ids, payload)
        engine.execute()
    finally:
        waiting_lock.unlink()


def verify_journal(events, pairs, bodies, request_ids, auth):
    texts = dict(pairs)
    expected = {sid: boundary.digest(boundary.wire_bytes(b)) for sid, b in bodies.items()}
    starts, done, held = {}, {}, {}
    spent, peak_total, peak_workers = 0.0, 0.0, 0
    for row in events:
        sid = row["sample_id"]
        if sid not in expected or row["request_sha256"] != expected[sid]:
            raise ValueError("unknown request or hash mismatch")
        if row["kind"] == "started":
            if sid in starts:
                raise ValueError("duplicate attempt")
            if (row["price_window"] != "off_peak"
                    or llm_se.rate_for(datetime.fromisoformat(row["timestamp"]))[0] != "off_peak"):
                raise ValueError("dispatch outside approved window")
            reserve = boundary.reserve_cost(bodies[sid], auth["price_cny_per_million"]["off_peak"])
            if abs(reserve - row["reserved_cny"]) > 1e-12:
                raise ValueError("reservation mismatch")
            starts[sid], held[sid] = row, reserve
            peak_total = max(peak_total, spent + sum(held.values()))
            peak_workers = max(peak_workers, len(held))
            if spent + sum(held.values()) > auth["cap_cny"] + 1e-10:
                raise ValueError("authorized budget exceeded")
        else:
            if sid not in starts or sid in done or row["request_id"] != request_ids[sid]:
                raise ValueError("completion identity mismatch")
            if boundary.digest(row["raw_content"].encode()) != row["response_sha256"]:
                raise ValueError("response hash mismatch")
            replay = adapt_finished(row, sample_id=sid, request_id=request_ids[sid], source_text=texts[sid])
            for key in ("label", "parse_status", "first_clause_label", "first_clause_status",
                        "sentence_uncertainty", "sentence_errors", "rule_record_validation", "clauses"):
                if row[key] != replay[key]:
                    raise ValueError("saved parsing differs from frozen adapter")
            if row["usage_verified"] != coordinator.usage_valid(row["usage"]):
                raise ValueError("usage verification mismatch")
            if row["model_accepted"] != (row["returned_model"] in base.ACCEPTED_MODELS):
                raise ValueError("returned model validation mismatch")
            if row["usage_verified"]:
                cost = llm_se.cost_cny(row["usage"], auth["price_cny_per_million"]["off_peak"])
                if abs(cost-row["cost_cny"]) > 1e-12 or cost > held[sid]:
                    raise ValueError("cost/reservation mismatch")
                spent += cost
                held.pop(sid)
            elif row["cost_cny"] != 0:
                raise ValueError("unknown usage cannot be reported as known cost")
            done[sid] = row
    if len(starts) > auth["max_calls"] or peak_workers > auth["max_workers"]:
        raise ValueError("call/concurrency scope exceeded")
    return done, {"attempted": len(starts), "finished": len(done), "uncalled": len(pairs)-len(starts),
                  "actual_known_cost_cny": spent, "unsettled_reservation_cny": sum(held.values()),
                  "peak_spent_plus_reserved_cny": peak_total, "peak_in_flight": peak_workers,
                  "completed": set(starts) == set(done) == set(texts) and not held,
                  "all_request_hashes_match": True, "all_response_hashes_match": True,
                  "all_requests_off_peak": True, "retry_count": 0,
                  "request_failure_count": sum(coordinator.failed(x) for x in done.values()),
                  "parse_status_counts": dict(Counter(x["parse_status"] for x in done.values())),
                  "returned_models": dict(Counter(str(x["returned_model"]) for x in done.values()))}


def report():
    pairs, bodies, request_ids, payload = frozen_plan()
    done, audit = verify_journal(boundary.read_events(JOURNAL), pairs, bodies, request_ids, payload["authorization"])
    # Test labels become available only here, after collection; never in execute().
    rows, historical_done, historical_metrics = prepared.verify_control()
    historical = {sid: r["label"] for sid, r in historical_done.items()}
    responses = {sid: {"raw_content": r["raw_content"], "request_ok": not coordinator.failed(r)} for sid, r in done.items()}
    result = sentence.evaluate_responses(rows, responses, request_ids, historical)
    if result["historical_22shot_original_readout"] != historical_metrics:
        raise ValueError("control metrics mismatch")
    gold = {r.sample_id: r.label for r in rows}
    changes = []
    for sid, _ in pairs:
        predicted = done.get(sid, {}).get("label")
        if predicted != historical[sid]:
            changes.append({"sample_id": sid, "gold": gold[sid], "old": historical[sid], "new": predicted,
                            "change": "corrected" if predicted == gold[sid] else "regressed" if historical[sid] == gold[sid] else "both_wrong_changed"})
    result.update(suite_id=sentence.SUITE_ID, candidate_name=sentence.NAME, audit=audit,
                  changed_predictions=changes,
                  uncertainty_counts=dict(Counter(f for r in done.values() for f in r["sentence_uncertainty"])),
                  created_at=base.now(), authorization_sha256=payload["authorization_sha256"],
                  candidate_preflight_sha256=APPROVED,
                  execution_preflight_sha256=boundary.digest(PLAN.read_bytes()),
                  journal_sha256=boundary.digest(JOURNAL.read_bytes()) if JOURNAL.exists() else None,
                  control_journal_sha256=boundary.digest(prepared.JOURNAL.read_bytes()),
                  source_sha256_lf_utf8=payload["source_sha256_lf_utf8"],
                  git_commit=subprocess.check_output(["git", "-c", "core.fsmonitor=false", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  delta_macro_f1=result["primary"]["macro_f1"]-historical_metrics["macro_f1"],
                  correct_count=round(result["primary"]["accuracy"]*426))
    if not audit["completed"]:
        result["scope"] = "partial collection; all-426 missing-as-failure diagnostic only, not a performance conclusion"
    destination = RESULT if audit["completed"] else RESULT.with_name("sun_modality_sentence_v1_partial_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + ".json")
    write_frozen(destination, prepared.serialize(result))
    lines = ["# LLM-SE 显式句级模态候选：执行结果", "",
             f"完成 {audit['finished']}/426；已知费用 ¥{audit['actual_known_cost_cny']:.7f}；未结算预留 ¥{audit['unsettled_reservation_cny']:.7f}；零重试。",
             "主结果按预先固定的 sentence_modality.label；同返回首 clause 为诊断。探索性历史对照，不代表未见数据泛化。", "",
             "| 取值 | 正确数 | Accuracy | Macro-P | Macro-R | Macro-F1 | 无预测 |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for key, title in [("historical_22shot_original_readout", "历史22-shot"), ("primary", "显式句级（主）"),
                       ("same_response_first_clause_diagnostic", "同返回首clause（诊断）")]:
        m = result[key]
        lines.append(f"| {title} | {round(m['accuracy']*426)} | {m['accuracy']:.6f} | {m['macro_precision']:.6f} | {m['macro_recall']:.6f} | {m['macro_f1']:.6f} | {m['failures']} |")
    lines += ["", "| 类别 | 历史P/R/F1 | 句级P/R/F1 | 首clause P/R/F1 | 句级TP/FP/FN |", "|---|---|---|---|---|"]
    for label in LABELS:
        cells = ["/".join(f"{result[k]['per_class'][label][m]:.6f}" for m in ("precision", "recall", "f1"))
                 for k in ("historical_22shot_original_readout", "primary", "same_response_first_clause_diagnostic")]
        c = result["primary"]["per_class"][label]
        lines.append(f"| {label} | " + " | ".join(cells) + f" | {c['tp']}/{c['fp']}/{c['fn']} |")
    matrix = result["primary"]["confusion_matrix"]
    lines += ["", "句级主结果混淆矩阵：行是原标签，列是预测。", "",
              "| 原标签 | " + " | ".join(matrix["column_order"]) + " |",
              "|---|" + "---:|" * len(matrix["column_order"])]
    for label, counts in zip(LABELS, matrix["rows_gold_columns_predicted"]):
        lines.append("| " + label + " | " + " | ".join(map(str, counts)) + " |")
    p = result["primary_vs_historical"]
    lines += ["", f"相对历史22-shot：改对 {p['corrected']}，改错 {p['regressed']}；Macro-F1 差 {result['delta_macro_f1']:+.8f}。",
              f"句级与同返回首clause标签不同 {len(result['sentence_vs_first_clause_differences'])} 条；Rule Record 校验未通过 {result['rule_record_invalid_count']} 条，按预定政策独立披露，不改变句级主取值。",
              "", f"不确定性标记计数：{result['uncertainty_counts']}。解析状态：{audit['parse_status_counts']}。",
              "", "原始返回和德语原文仅本地；逐ID变化、完整指标、哈希和费用见同名 JSON。",
              "接口、取值、指导和示范均随候选改变，不能把差值归因到某个单独提示段。历史分数不重写，不自动升级候选。"]
    if not audit["completed"]:
        lines += ["", "本批未完整收集；上表仅是未调用/失败计入分母的进度诊断，不作性能结论。"]
    write_frozen(destination.with_suffix(".md"), ("\n".join(lines)+"\n").encode())
    print(json.dumps({"report": str(destination), "audit": audit, "macro_f1": result["primary"]["macro_f1"],
                      "paired": p}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "execute", "report"])
    parser.add_argument("--wait-for-off-peak", action="store_true")
    args = parser.parse_args()
    if args.mode == "execute":
        execute(args.wait_for_off_peak)
    else:
        {"prepare": prepare, "report": report}[args.mode]()
