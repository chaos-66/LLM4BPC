"""Prepare, execute or score the single fixed 22-shot test arm."""
import argparse
import importlib.util
import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import prepare_sun_modality_eligibility_shots_v1 as prepared
import build_sun_modality_fewshot_report_v1 as stats
from continue_sun_modality_validation_v1 import paced
from prepare_sun_modality_fewshot_v1 import write_frozen
from bpc_hybrid.modality_benchmark import boundary, data, fewshot, llm_se, review_prompt
from bpc_hybrid.modality_benchmark.metrics import evaluate

ROOT = prepared.ROOT
RUN = prepared.LOCAL / "execution_v1"
PLAN = RUN / "execution_preflight.json"
JOURNAL = RUN / "local_only/events.jsonl"
AUTH = ROOT / "configs/authorization/sun_modality_eligibility_20261105_v1.json"
BASE = ROOT / "outputs/reports"
FREEZE = BASE / "sun_modality_eligibility_shots_v1_execution_preflight.json"
RESULT = BASE / "sun_modality_eligibility_shots_v1_completed.json"
CONTROL = BASE / "sun_modality_validation_v1_completed.json"
CONTROL_JOURNAL = ROOT / "outputs/development/sun_modality_validation_v1/execution_v1/local_only/events.jsonl"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def serialize(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def check_limits(auth):
    required = dict(suite_id="SUN-MODALITY-ELIGIBILITY-SHOTS-001", execute_authorized=True,
                    max_calls=426, cap_cny=20, max_workers=4, retries=0, off_peak_only=True,
                    endpoint="https://api.deepseek.com", model=llm_se.MODEL_ALIAS,
                    price_cny_per_million=llm_se.PRICE_CNY_PER_MILLION)
    if any(auth.get(k) != v for k, v in required.items()) or not auth.get("user_text"):
        raise ValueError("authorization limits differ from the single test run")


def plan():
    auth = read(AUTH)
    check_limits(auth)
    if boundary.digest(prepared.REPORT.read_bytes()) != auth["approved_prompt_preflight_sha256"]:
        raise ValueError("prompt preflight binding mismatch")
    system, _, preflight = prepared.build()
    if preflight != read(prepared.REPORT):
        raise ValueError("22-shot prompt differs from the delivered version")
    parent_block, _ = fewshot.load_demonstrations()
    old_hashes = {r["sample_id"]: r["review_request_sha256"]
                  for r in read(BASE / "sun_modality_review_v1_preflight.json")["requests"]}
    pairs = data.load_split_text_only("test")
    if len(pairs) != auth["max_calls"] or {s for s, _ in pairs} != set(old_hashes):
        raise ValueError("test membership mismatch")
    bodies, requests = {}, []
    for sid, text in pairs:
        body = review_prompt.request_body(sid, text, block=parent_block)
        if boundary.digest(boundary.wire_bytes(body)) != old_hashes[sid]:
            raise ValueError("control request drift")
        body["messages"][0]["content"] = system
        bodies[sid] = body
        requests.append({"sample_id": sid, "fewshot_request_sha256": boundary.digest(boundary.wire_bytes(body))})
    sources = [Path(__file__), prepared.MANIFEST, Path(stats.__file__),
               ROOT / "scripts/run_sun_modality_fewshot_v1.py", ROOT / "scripts/run_sun_modality_boundary_v1.py",
               ROOT / "scripts/continue_sun_modality_validation_v1.py", ROOT / "src/bpc_hybrid/llm_client.py",
               ROOT / "src/bpc_hybrid/h1_transport.py"]
    payload = {"authorization": auth, "authorization_sha256": boundary.digest(AUTH.read_bytes()),
               "system_sha256": preflight["composed_system_sha256"], "requests": requests,
               "source_sha256_lf": {p.relative_to(ROOT).as_posix(): boundary.digest(p.read_text(encoding="utf-8").encode()) for p in sources}}
    return pairs, bodies, payload


def check_control():
    reference = read(CONTROL)
    if boundary.digest(CONTROL_JOURNAL.read_bytes()) != reference["initial_journal_sha256"]:
        raise ValueError("historical reviewer evidence drift")
    return reference


def freeze():
    pairs, _, payload = plan()
    check_control()
    full = {"payload": payload}
    write_frozen(PLAN, serialize(full))
    public = {"suite_id": payload["authorization"]["suite_id"], "count": len(pairs),
              "execution_preflight_sha256": boundary.digest(serialize(full)),
              "control_sha256": boundary.digest(CONTROL.read_bytes()),
              "prompt_sha256": payload["system_sha256"], "api_calls_so_far": 0}
    write_frozen(FREEZE, serialize(public))
    print(json.dumps(public))


def frozen_plan():
    pairs, bodies, payload = plan()
    public = read(FREEZE)
    if (boundary.digest(PLAN.read_bytes()) != public["execution_preflight_sha256"]
            or read(PLAN) != {"payload": payload} or boundary.digest(CONTROL.read_bytes()) != public["control_sha256"]):
        raise ValueError("execution preflight drift")
    return pairs, bodies, payload


def execute():
    pairs, bodies, payload = frozen_plan()
    spec = importlib.util.spec_from_file_location("eligibility_engine", ROOT / "scripts/run_sun_modality_fewshot_v1.py")
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    engine.RUN, engine.PLAN, engine.JOURNAL = RUN, PLAN, JOURNAL
    engine.data = SimpleNamespace(load_split_text_only=lambda _: pairs)
    engine.fewshot = SimpleNamespace(load_demonstrations=lambda: ("", {}), request_body=lambda sid, text, *, block: bodies[sid])
    engine.plan_payload = lambda: payload
    engine.send_one = paced(engine.send_one, allowed=lambda: llm_se.rate_for(datetime.now(llm_se.BEIJING))[0] == "off_peak")
    engine.execute()


def confusions(gold, pred):
    return {a + "_to_" + b: sum(g == a and p == b for g, p in zip(gold, pred))
            for a, b in [("definition", "permission"), ("permission", "definition")]}


def report():
    pairs, _, payload = frozen_plan()
    finished, audit = stats.verify_journal(boundary.read_events(JOURNAL), payload["requests"], payload["authorization"])
    reference = check_control()
    historical = {r["sample_id"]: r["label"] for r in boundary.read_events(CONTROL_JOURNAL) if r["kind"] == "finished"}
    rows = data.load_split("test")
    ids = [r.sample_id for r in rows]
    if ids != [sid for sid, _ in pairs]:
        raise ValueError("test order mismatch")
    gold = [r.label for r in rows]
    old = [historical["test:review:" + sid] for sid in ids]
    new = [finished[sid]["label"] for sid in ids]
    before, after = evaluate(gold, old), evaluate(gold, new)
    if before != reference["comparisons"]["test"]["review"]:
        raise ValueError("existing reviewer metrics do not reproduce")
    changes = [{"sample_id": s, "gold": g, "old": a, "new": b}
               for s, g, a, b in zip(ids, gold, old, new) if a != b]
    family = {r["sample_id"] for r in read(BASE / "sun_modality_review_v1.json")["reviewed_cases"]
              if r["primary_family"] == "eligibility_limit_boundary"}
    if len(family) != 17 or not family <= set(ids):
        raise ValueError("fixed error family mismatch")
    ci = stats.bootstrap_delta(gold, old, new)
    ci["delta"] = "22-shot minus reviewer"
    result = {"suite_id": payload["authorization"]["suite_id"], "scope": "test-informed exploratory historical comparison",
              "control": before, "eligibility_shots": after, "paired": stats.paired(gold, old, new),
              "delta_macro_f1": after["macro_f1"] - before["macro_f1"], "bootstrap": ci,
              "boundary_confusions": {"control": confusions(gold, old), "new": confusions(gold, new)},
              "original_17_family": {"n": 17, "control_correct": sum(s in family and g == a for s,g,a in zip(ids,gold,old)),
                                     "new_correct": sum(s in family and g == b for s,g,b in zip(ids,gold,new))},
              "changed_predictions": changes, "audit": audit, "retry_count": 0,
              "journal_sha256": boundary.digest(JOURNAL.read_bytes()), "control_journal_sha256": reference["initial_journal_sha256"],
              "preflight_sha256": boundary.digest(PLAN.read_bytes()), "public_preflight_sha256": boundary.digest(FREEZE.read_bytes()),
              "authorization_sha256": payload["authorization_sha256"]}
    write_frozen(RESULT, serialize(result))
    print(json.dumps({k:result[k] for k in ("delta_macro_f1", "paired", "boundary_confusions", "original_17_family", "audit")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "execute", "report"])
    mode = parser.parse_args().mode
    {"prepare": freeze, "execute": execute, "report": report}[mode]()
