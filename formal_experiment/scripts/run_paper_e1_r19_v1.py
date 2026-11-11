"""Dispatch one bounded, resumable run from the frozen paper preflight."""
from __future__ import annotations

import argparse
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime, timedelta

import prepare_paper_e1_r19_v1 as pre
import run_sun_modality_fewshot_v1 as transport
import run_stage3_d1_v4_r1 as gdpr_parser

JOURNAL = pre.LOCAL / "local_only/events.jsonl"
PILOT = pre.LOCAL / "pilot_passed.json"
DRY = pre.ROOT / "outputs/reports/paper_e1_r19_v1_offline_validation.json"
AUTH = pre.ROOT / "configs/authorization/paper_e1_r19_v1.json"
WORKERS = 8


def keystr(key):
    return "|".join(key)


def controls_digest(controls):
    return pre.digest(pre.encoded({keystr(k): r["response_sha256"] for k,r in controls.items()}))


def budget_allows(spent, held, maximum):
    return (all(math.isfinite(x) and x >= 0 for x in (spent,held,maximum))
            and maximum > 0 and spent + held <= maximum)


def canonical(key, text, row):
    group, arm, sid = key
    if group == "german":
        return {"label": pre.llm_se.extract_modality_label(row["raw_content"])["label"]}
    if group == "gdpr":
        return gdpr_parser.convert_response_content(
            sample_id=sid, source_text=text, content=row["raw_content"],
            call_meta={"body_sha256": row["request_sha256"], "api_call_status": "ok"})
    return pre.core._prediction_row(pre.core.parse_same_response({
        "sample_id":sid, "request_id":keystr(key), "response_sha256":row["response_sha256"],
        "raw_response_content":row["raw_content"]}, arm, text), arm)


def response_check(key, text, row, request_hash):
    if transport.failed(row) or row["request_sha256"] != request_hash:
        raise ValueError(f"transport, usage, model or request binding failed: {keystr(key)}")
    if pre.digest(row["raw_content"].encode()) != row["response_sha256"]:
        raise ValueError(f"response digest differs: {keystr(key)}")
    rate = pre.llm_se.PRICE_CNY_PER_MILLION["off_peak"]
    if (not transport.usage_valid(row["usage"])
            or row["cost_cny"] != pre.llm_se.cost_cny(row["usage"],rate)):
        raise ValueError(f"billing metadata differs: {keystr(key)}")
    record = pre.llm_se._extract_json_object(row["raw_content"])
    if record and any(record.get(k) != key[2] for k in ("source_id","sample_id")):
        raise ValueError(f"response identity differs: {keystr(key)}")
    parsed = canonical(key, text, row)
    if key[0] == "german":
        if parsed["label"] != row["label"]:
            raise ValueError("modality parser disagreement")
        return parsed["label"] is not None
    return parsed["request_status"] == "ok"


def check_history(events, jobs, texts, hashes):
    starts, finished = set(), {}
    for r in events:
        key = tuple(r["sample_id"].split("|"))
        if key not in jobs or r["request_sha256"] != hashes[key]:
            raise ValueError("journal not bound to this request plan")
        if r["kind"] == "started":
            starts.add(key)
        else:
            response_check(key, texts[key[0]][key[2]], r, hashes[key])
            finished[key] = r
    if starts != set(finished):
        raise ValueError("an earlier request was reserved without a verified completion; do not resend")
    return finished


@contextmanager
def lock_run():
    """The OS releases the lock on process death; charged requests remain in the journal."""
    import os
    path = pre.LOCAL / "execution.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def safe_window(now):
    # Price the whole request at the idle rate only if its timeout is outside peak.
    return all(not pre.llm_se.is_peak(now + timedelta(minutes=n)) for n in range(5))


def run():
    plan, pairs, bodies, controls = pre.build()
    proof, auth = pre.read(DRY), pre.read(AUTH)
    if (plan != pre.read(pre.REPORT) or not proof["passed"]
            or proof["requests_sha256"] != plan["requests_sha256"]
            or auth["preflight_sha256"] != pre.digest(pre.REPORT.read_bytes())
            or auth["validation_sha256"] != pre.digest(DRY.read_bytes())
            or auth["max_new_calls"] != plan["estimated_max_new_calls"]
            or auth["endpoint"] != plan["endpoint"] or auth["mode"] != "off_peak_only"
            or proof["control_responses_sha256"] != controls_digest(controls)
            or not budget_allows(0,0,auth["max_cost_cny"]) or auth["automatic_retries"] != 0):
        raise ValueError("authorization or offline validation does not match the frozen requests")
    for path, expected in proof["code_sha256"].items():
        if pre.digest((pre.ROOT/path).read_text(encoding="utf-8").encode()) != expected:
            raise ValueError(f"validated code differs: {path}")
    jobs = {k:b for k,b in bodies.items() if k not in controls}
    hashes = {k:pre.digest(pre.boundary.wire_bytes(b)) for k,b in jobs.items()}
    texts = {k:dict(v) for k,v in pairs.items()}
    bygroup = {}
    for key in jobs:
        bygroup.setdefault(key[:2], []).append(key)
    pilot = [v[0] for v in bygroup.values()]
    config = transport.base.environment_config()
    with lock_run(), ThreadPoolExecutor(max_workers=WORKERS) as pool:
        JOURNAL.parent.mkdir(parents=True, exist_ok=True)
        events = pre.boundary.read_events(JOURNAL)
        previous = events[-1]["event_hash"] if events else ""
        finished = check_history(events,jobs,texts,hashes)
        spent = sum(r["cost_cny"] for r in finished.values())
        def send_batch(keys):
            nonlocal previous, spent
            keys = [k for k in keys if k not in finished]
            if not keys:
                return
            now = datetime.now(pre.llm_se.BEIJING)
            while not safe_window(now):
                print("Waiting for the off-peak price window", flush=True)
                time.sleep(60)
                now = datetime.now(pre.llm_se.BEIJING)
            rate = pre.llm_se.PRICE_CNY_PER_MILLION["off_peak"]
            holds = {k:pre.boundary.reserve_cost(jobs[k],rate) for k in keys}
            if not budget_allows(spent,sum(holds.values()),auth["max_cost_cny"]):
                if len(keys) > 1:
                    for k in keys:
                        send_batch([k])
                    return
                raise ValueError(f"incremental cost cap reached before dispatch; spent CNY {spent:.4f}")
            futures = {}
            for key in keys:
                sid = key[2]
                previous = pre.boundary.append_event(JOURNAL, {
                    "kind":"started","sample_id":keystr(key),"timestamp":transport.base.now(),
                    "request_sha256":hashes[key],"reserved_cny":holds[key],"price_window":"off_peak"},previous)
                future = pool.submit(transport.send_one, config, sid, texts[key[0]][sid],jobs[key],hashes[key],rate)
                futures[future] = key
            issues = []
            for future in as_completed(futures):
                key = futures[future]
                r = future.result()
                r["sample_id"] = keystr(key)
                previous = pre.boundary.append_event(JOURNAL,r,previous)
                finished[key] = r
                spent += r["cost_cny"]
                try:
                    response_check(key,texts[key[0]][key[2]],r,hashes[key])
                    if r["cost_cny"] > holds[key]:
                        raise ValueError("actual cost exceeded reservation")
                except ValueError as exc:
                    issues.append(str(exc))
            if issues:
                raise ValueError("; ".join(issues))
        for key in pilot:
            send_batch([key])
            if not response_check(key,texts[key[0]][key[2]],finished[key],hashes[key]):
                raise ValueError(f"inspect first real response for {keystr(key)} before bulk dispatch")
        pre.frozen(PILOT,pre.encoded({keystr(k):finished[k]["response_sha256"] for k in pilot}))
        print(f"Pilot passed: {len(pilot)} reusable responses",flush=True)
        for group, keys in bygroup.items():
            for i in range(0,len(keys),WORKERS):
                batch=keys[i:i+WORKERS]
                send_batch(batch)
                if len(batch)>1 and all(not response_check(k,texts[k[0]][k[2]],finished[k],hashes[k]) for k in batch):
                    raise ValueError(f"systematic unusable responses in {group}")
                if i % (8*WORKERS) == 0:
                    print(f"{len(finished)}/{len(jobs)} settled, CNY {spent:.4f}",flush=True)
        if set(finished) != set(jobs):
            raise ValueError("missing requests")
        print(f"Complete: {len(finished)} new responses, CNY {spent:.6f}",flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    run()
