"""Complete and score the frozen E1 test arm, reusing its five pilot responses."""
import argparse
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import prepare_sun_modality_es_minimal_v1 as prepared
import run_sun_modality_eligibility_shots_v1 as control
import run_sun_modality_fewshot_v1 as transport
from bpc_hybrid.modality_benchmark import boundary, data, llm_se
from bpc_hybrid.modality_benchmark.metrics import evaluate
from prepare_sun_modality_fewshot_v1 import write_frozen

ROOT = prepared.ROOT
RUN = prepared.LOCAL / "E1_full_20261111"
JOURNAL = RUN / "events.jsonl"
REPORTS = ROOT / "outputs/reports"
PILOT = REPORTS / "sun_modality_es_minimal_v1_pilot_20261111.json"
PLAN = REPORTS / "sun_modality_e1_full_v1_preflight.json"
RESULT = REPORTS / "sun_modality_e1_full_v1_completed.json"
WORKERS = 4
MAX_CALLS = 421


def sha_file(path):
    return boundary.digest(path.read_bytes())


def check_response(row, request_hash):
    if transport.failed(row) or row["request_sha256"] != request_hash:
        raise ValueError("transport, model, usage or request binding differs")
    content = row["raw_content"]
    parsed = llm_se.extract_modality_label(content)
    if (boundary.digest(content.encode()) != row["response_sha256"]
            or parsed["label"] != row["label"] or parsed["status"] != row["parse_status"]):
        raise ValueError("response digest or historical readout differs")
    record = llm_se._extract_json_object(content)
    if record and any(record.get(k) != row["sample_id"] for k in ("sample_id", "source_id")):
        raise ValueError("returned sample identity differs")


def build():
    baseline, systems, frozen = prepared.build()
    pilot = prepared.read(PILOT)
    if frozen != prepared.read(prepared.REPORT):
        raise ValueError("E1 prompt preflight differs")
    evidence = pilot["evidence"]
    pilot_path = ROOT / evidence["pilot_journal_path"]
    if (sha_file(control.JOURNAL) != evidence["historical_22shot_journal_sha256"]
            or sha_file(pilot_path) != evidence["pilot_journal_sha256"]):
        raise ValueError("historical journal differs")
    old = {r["sample_id"]: r for r in boundary.read_events(control.JOURNAL) if r["kind"] == "finished"}
    reused = {r["sample_id"]: r for r in boundary.read_events(pilot_path)
              if r["kind"] == "finished" and r["wave"] in ("E1-1", "E1-2")}
    recorded = {r["sample_id"]: r for r in pilot["cases"] if r["wave"] in ("E1-1", "E1-2")}
    pairs = dict(data.load_split_text_only("test"))
    if set(old) != set(pairs) or len(pairs) != 426 or set(reused) != set(recorded) or len(reused) != 5:
        raise ValueError("test or pilot membership differs")
    bodies, hashes = {}, {}
    for sid, text in pairs.items():
        original = prepared.request_body(baseline, sid, text)
        if boundary.digest(boundary.wire_bytes(original)) != old[sid]["request_sha256"]:
            raise ValueError("control request differs")
        body = prepared.request_body(systems["E1"], sid, text)
        bodies[sid] = body
        hashes[sid] = boundary.digest(boundary.wire_bytes(body))
        if sid in reused:
            check_response(reused[sid], hashes[sid])
            if reused[sid]["response_sha256"] != recorded[sid]["response_sha256"]:
                raise ValueError("pilot response differs")
    remaining = [sid for sid in pairs if sid not in reused]
    if len(remaining) != MAX_CALLS:
        raise ValueError("wrong dispatch budget")
    paths = [Path(__file__), Path(transport.__file__), Path(transport.base.__file__),
             Path(llm_se.__file__), Path(boundary.__file__), Path(control.stats.__file__),
             ROOT / "src/bpc_hybrid/modality_benchmark/metrics.py", ROOT / "src/bpc_hybrid/llm_client.py",
             ROOT / "src/bpc_hybrid/h1_transport.py"]
    plan = {"suite_id": "SUN-MODALITY-E1-FULL-001", "authorization": "验证E1的整体F1，继续测试",
            "continuation_of": pilot["run_id"], "endpoint": "https://api.deepseek.com",
            "model": llm_se.MODEL_ALIAS, "max_new_calls": MAX_CALLS, "retries": 0,
            "max_workers": WORKERS, "max_output_tokens_per_call": 4096, "n": len(pairs),
            "test_sha256": data.EXPECTED["test"]["sha256"], "system_sha256": frozen["variants"]["E1"]["system_sha256"],
            "pilot_report_sha256": boundary.digest(control.serialize(pilot)),
            "pilot_journal_sha256": sha_file(pilot_path), "control_journal_sha256": sha_file(control.JOURNAL),
            "reused_response_sha256": {sid: r["response_sha256"] for sid, r in reused.items()},
            "all_request_hashes_sha256": boundary.digest(control.serialize(hashes)),
            "new_request_hashes_sha256": boundary.digest(control.serialize([hashes[sid] for sid in remaining])),
            "runtime_source_sha256_lf_utf8": {p.relative_to(ROOT).as_posix(): boundary.digest(p.read_text(encoding="utf-8").encode()) for p in paths},
            "population": "Frozen 426 test samples. Reuse five E1 responses only; preserve first non-empty label and all-sample denominator."}
    return plan, pairs, bodies, hashes, remaining, reused, old


def checked_history(remaining, hashes):
    events = boundary.read_events(JOURNAL)
    finished = {}
    for row in events:
        sid = row["sample_id"]
        if sid not in remaining or row["request_sha256"] != hashes[sid]:
            raise ValueError("journal does not match planned requests")
        if row["kind"] == "finished":
            check_response(row, hashes[sid])
            finished[sid] = row
    if len(events) != 2 * len(finished):
        raise ValueError("unsettled request; do not resend")
    return events, finished


def execute(pairs, bodies, hashes, remaining):
    config = transport.base.environment_config()
    RUN.mkdir(parents=True, exist_ok=True)
    lock = RUN / "execution.lock"
    with lock.open("x") as handle:
        handle.write(transport.base.now())
    try:
        events, finished = checked_history(remaining, hashes)
        null_streak = 0
        for row in events:
            if row["kind"] == "finished":
                null_streak = null_streak + 1 if row["label"] is None else 0
                if null_streak >= 2:
                    raise ValueError("consecutive unusable outputs in journal; inspect before continuing")
        pending = [sid for sid in remaining if sid not in finished]
        previous = events[-1]["event_hash"] if events else ""
        done = len(finished)
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            for offset in range(0, len(pending), WORKERS):
                futures = []
                for sid in pending[offset:offset + WORKERS]:
                    window, rate = llm_se.rate_for(datetime.now(llm_se.BEIJING))
                    previous = boundary.append_event(JOURNAL, {"kind": "started", "sample_id": sid,
                        "timestamp": transport.base.now(), "request_sha256": hashes[sid],
                        "price_window": window, "reserved_cny": boundary.reserve_cost(bodies[sid], rate)}, previous)
                    futures.append(pool.submit(transport.send_one, config, sid, pairs[sid], bodies[sid], hashes[sid], rate))
                issue = None
                for future in as_completed(futures):
                    row = future.result()
                    previous = boundary.append_event(JOURNAL, row, previous)
                    try:
                        check_response(row, hashes[row["sample_id"]])
                    except ValueError as exc:
                        issue = str(exc)
                    null_streak = null_streak + 1 if row["label"] is None else 0
                    if null_streak >= 2:
                        issue = issue or "consecutive unusable outputs"
                    done += 1
                if issue:
                    raise ValueError(f"stopped after {done} completions: {issue}")
                if done <= WORKERS or done % 40 < WORKERS or done == MAX_CALLS:
                    print(f"{done}/{MAX_CALLS} new requests settled", flush=True)
    finally:
        lock.unlink()


def report(plan, pairs, hashes, remaining, reused, old):
    events, fresh = checked_history(remaining, hashes)
    combined = {**reused, **fresh}
    if set(fresh) != set(remaining) or set(combined) != set(pairs):
        raise ValueError("full-test score requires all 426 rows")
    rows = data.load_split("test")
    ids, gold = [r.sample_id for r in rows], [r.label for r in rows]
    if ids != list(pairs):
        raise ValueError("scoring order differs from frozen input")
    old_labels, new_labels = [old[i]["label"] for i in ids], [combined[i]["label"] for i in ids]
    before, after = evaluate(gold, old_labels), evaluate(gold, new_labels)
    if before != prepared.read(control.RESULT)["eligibility_shots"]:
        raise ValueError("historical control does not reproduce")
    interval = control.stats.bootstrap_delta(gold, old_labels, new_labels)
    interval["delta"] = "E1 minus original 22-shot"
    changes = [{"sample_id": i, "gold": g, "original_22shot": a, "E1": b, "reused_pilot": i in reused}
               for i, g, a, b in zip(ids, gold, old_labels, new_labels) if a != b]
    result = {"suite_id": plan["suite_id"], "method": "direct_llm", "scope": "test-informed historical paired comparison",
              "stage": "Part 2", "model": plan["model"], "system_sha256": plan["system_sha256"],
              "test_sha256": plan["test_sha256"], "max_new_calls": MAX_CALLS, "new_calls": len(fresh),
              "reused_E1": len(reused), "n": len(combined), "retry_count": 0,
              "new_started_utc": events[0]["timestamp"], "new_finished_utc": events[-1]["timestamp"],
              "control_journal_sha256": plan["control_journal_sha256"], "pilot_journal_sha256": plan["pilot_journal_sha256"],
              "new_journal_local_path": JOURNAL.relative_to(ROOT).as_posix(), "new_journal_sha256": sha_file(JOURNAL),
              "preflight_sha256_lf": boundary.digest(control.serialize(plan)),
              "settings": {k: prepared.read(prepared.REPORT)["unchanged_request_fields"][k] for k in ("temperature","top_p","stream","max_tokens","thinking")},
              "new_call_estimated_cost_cny_at_project_rates": round(sum(r["cost_cny"] for r in fresh.values()),8),
              "reused_E1_historical_cost_cny_at_project_rates": round(sum(r["cost_cny"] for r in reused.values()),8),
              "new_usage": {k: sum(r["usage"][k] for r in fresh.values()) for k in ("prompt_tokens","completion_tokens","prompt_cache_hit_tokens","prompt_cache_miss_tokens")},
              "new_returned_models": dict(Counter(r["returned_model"] for r in fresh.values())),
              "parse_status_all": dict(Counter(r["parse_status"] for r in combined.values())),
              "control": before, "E1": after, "delta_macro_f1": after["macro_f1"]-before["macro_f1"],
              "paired": control.stats.paired(gold, old_labels, new_labels), "paired_bootstrap": interval,
              "changed_first_labels": changes}
    write_frozen(RESULT,control.serialize(result))
    print(json.dumps({k:result[k] for k in ("new_calls","delta_macro_f1","paired","new_call_estimated_cost_cny_at_project_rates")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "execute", "report"))
    mode = parser.parse_args().mode
    plan, pairs, bodies, hashes, remaining, reused, old = build()
    if mode == "prepare":
        write_frozen(PLAN, control.serialize(plan))
        print(f"Bound {len(remaining)} new requests and {len(reused)} existing E1 responses; zero sends.")
    elif prepared.read(PLAN) != plan:
        raise SystemExit("execution preflight drift")
    elif mode == "execute":
        execute(pairs, bodies, hashes, remaining)
    else:
        report(plan, pairs, hashes, remaining, reused, old)
