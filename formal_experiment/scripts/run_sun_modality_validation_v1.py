"""Explicit-authorization adapter for the frozen concurrent, zero-retry runner.

The old execution code is loaded in an isolated module, not edited. Composite
call IDs keep the dev pair separate in its existing budget/hash-chain journal.
No process-wide data/prompt module is patched and no dev/test labels are read.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import prepare_sun_modality_validation_v1 as prepared
from prepare_sun_modality_fewshot_v1 import write_frozen
from bpc_hybrid.modality_benchmark import boundary, data, fewshot

RUN = ROOT / "outputs/development/sun_modality_validation_v1/execution_v1"
JOURNAL = RUN / "local_only/events.jsonl"
EXECUTION_PLAN = RUN / "execution_preflight.json"


def verify_authorization(auth, plan, plan_sha):
    if auth.get("execute_authorized") is not True or not auth.get("user_text"):
        raise ValueError("new explicit batch authorization is required")
    if auth.get("approved_preflight_sha256") != plan_sha or auth.get("suite_id") != plan["suite_id"]:
        raise ValueError("authorization preflight mismatch")
    for key, value in plan["contract"]["requested_limits"].items():
        if auth.get(key) != value:
            raise ValueError("authorization limit mismatch: " + key)
    if len(plan["requests"]) != auth["max_calls"]:
        raise ValueError("authorization population mismatch")


def make_engine(plan, auth, auth_sha):
    spec = importlib.util.spec_from_file_location("modality_validation_execution_engine",
                                                ROOT / "scripts/run_sun_modality_fewshot_v1.py")
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    block, _ = fewshot.load_demonstrations()
    texts = {name: dict(data.load_split_text_only(name)) for name in ("test", "dev")}
    rows = {r["call_id"]: r for r in plan["requests"]}
    if len(rows) != len(plan["requests"]):
        raise ValueError("duplicate call identifier")
    pairs = [(r["call_id"], texts[r["split"]][r["sample_id"]]) for r in plan["requests"]]

    def request_body(call_id, text, *, block):
        row = rows[call_id]
        if text != texts[row["split"]][row["sample_id"]]:
            raise ValueError("scheduled text mismatch")
        body = prepared.body_for(row["arm"], row["sample_id"], text, block)
        if boundary.digest(boundary.wire_bytes(body)) != row["request_sha256"]:
            raise ValueError("scheduled request mismatch")
        return body

    payload = {"authorization": auth, "authorization_sha256": auth_sha,
               "validation_preflight_sha256": boundary.digest(prepared.REPORT.read_bytes()),
               "requests": [{"sample_id": r["call_id"], "fewshot_request_sha256": r["request_sha256"]}
                            for r in plan["requests"]]}
    # Compatibility names are private to the engine; plan metadata retains split/arm/source ID.
    engine.data = SimpleNamespace(load_split_text_only=lambda _: pairs)
    engine.fewshot = SimpleNamespace(load_demonstrations=lambda: (block, {}), request_body=request_body)
    engine.plan_payload = lambda: payload
    engine.RUN, engine.JOURNAL, engine.PLAN = RUN, JOURNAL, EXECUTION_PLAN
    return engine, payload


def execute(authorization_path):
    plan = prepared.verify_frozen()
    auth_raw = Path(authorization_path).read_bytes()
    auth = json.loads(auth_raw)
    verify_authorization(auth, plan, boundary.digest(prepared.REPORT.read_bytes()))
    engine, payload = make_engine(plan, auth, boundary.digest(auth_raw))
    write_frozen(EXECUTION_PLAN, (json.dumps({"payload": payload}, ensure_ascii=False, indent=2) + "\n").encode())
    engine.execute()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    args = parser.parse_args()
    execute(args.authorization)
