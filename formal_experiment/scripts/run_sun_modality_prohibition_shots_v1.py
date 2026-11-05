"""Prepare a train contrast, run only with its own authorization, score all paired outputs."""
import argparse
import importlib.util
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import run_sun_modality_eligibility_shots_v1 as parent
from prepare_sun_modality_fewshot_v1 import write_frozen
from prepare_sun_modality_eligibility_shots_v1 import check_isolation
from bpc_hybrid.modality_benchmark import boundary, data, llm_se
from bpc_hybrid.modality_benchmark.metrics import LABELS, evaluate
from bpc_hybrid.datasets.sun_modality_importer import normalize_for_dedup

ROOT = parent.ROOT
MANIFEST = ROOT / "prompts/sun_compat/modality_prohibition_shots_v1/selection_manifest.json"
LOCAL = ROOT / "outputs/development/sun_modality_prohibition_shots_v1"
RUN = LOCAL / "execution_v1"
PLAN = RUN / "execution_preflight.json"
JOURNAL = RUN / "local_only/events.jsonl"
FREEZE = parent.BASE / "sun_modality_prohibition_shots_v1_preflight.json"
RESULT = parent.BASE / "sun_modality_prohibition_shots_v1_completed.json"
P = "prohibition"
SUITE = "SUN-MODALITY-PROHIBITION-SHOTS-001"
LIMITS = dict(max_calls=426, cap_cny=20, max_workers=4, retries=0, off_peak_only=True,
              endpoint="https://api.deepseek.com", model=llm_se.MODEL_ALIAS,
              price_cny_per_million=llm_se.PRICE_CNY_PER_MILLION)


def train_pair(manifest):
    if manifest["source_split"] != "train" or manifest["suite_id"] != SUITE:
        raise ValueError("wrong example source or suite")
    spec = data.EXPECTED["train"]
    if data.sha256_file(spec["path"]) != spec["sha256"]:
        raise ValueError("train split drift")
    train = {r.sample_id: r for r in data.load_split("train")}
    _, original = parent.fewshot.load_demonstrations()
    inherited = [s["sample_id"] for s in original["selections"] + parent.read(parent.prepared.MANIFEST)["examples"]]
    used = {normalize_for_dedup(train[s].text) for s in inherited}
    additions = manifest["examples"]
    if [(s["position"], s["label"]) for s in additions] != [(23, P), (24, "definition")]:
        raise ValueError("unexpected contrast")
    rows = []
    for s in additions:
        row = train.get(s["sample_id"])
        if row is None or row.label != s["label"] or boundary.digest(row.text.encode()) != s["text_sha256"]:
            raise ValueError("training membership, gold label or text drift")
        norm = normalize_for_dedup(row.text)
        if norm in used:
            raise ValueError("duplicate corpus example")
        used.add(norm)
        rows.append(row)
    for split in ("dev", "test"):
        check_isolation(rows, data.load_split_text_only(split))
    return rows


def build():
    manifest = parent.read(MANIFEST)
    if boundary.digest(parent.RESULT.read_bytes()) != manifest["parent_result_sha256"]:
        raise ValueError("previous result drift")
    rows = train_pair(manifest)
    pairs, bodies, old = parent.frozen_plan()
    if old["system_sha256"] != manifest["parent_system_sha256"]:
        raise ValueError("previous system prompt drift")
    suffix = "\n".join(f'{i}. "{r.text}" -> {r.label}' for i, r in enumerate(rows, 23))
    requests = []
    for sid, _ in pairs:
        body = bodies[sid]
        body["messages"][0]["content"] += "\n" + suffix
        requests.append({"sample_id": sid, "fewshot_request_sha256": boundary.digest(boundary.wire_bytes(body))})
    system = bodies[pairs[0][0]]["messages"][0]["content"]
    record = {"suite_id": SUITE, "status": "offline_prepared", "planned_calls": len(requests),
              "limits": LIMITS, "system_sha256": boundary.digest(system.encode()),
              "train_sha256": data.EXPECTED["train"]["sha256"],
              "fixed_request_list_sha256": boundary.digest(parent.serialize(requests)),
              "parent_result_sha256": manifest["parent_result_sha256"],
              "selection_manifest_sha256_lf": boundary.digest(MANIFEST.read_text(encoding="utf-8").encode()),
              "runner_sha256_lf": boundary.digest(Path(__file__).read_text(encoding="utf-8").encode()),
              "additional_train_examples": 2, "new_total": 24, "new_prohibition_count": 4,
              "new_examples_times_dev_test_rows": 2 * (420 + 426), "near_overlap_hits": 0,
              "acceptance": manifest["acceptance"], "new_performance": None}
    return pairs, bodies, requests, system, record


def prepare():
    _, _, _, system, record = build()
    write_frozen(LOCAL / "composed_system_prompt.txt", (system + "\n").encode())
    write_frozen(FREEZE, parent.serialize(record))
    print(f"Prepared {record['planned_calls']} local requests; zero API calls.")


def verified_plan():
    pairs, bodies, requests, _, record = build()
    if record != parent.read(FREEZE):
        raise ValueError("frozen plan differs")
    return pairs, bodies, requests


def authorize(auth, preflight_sha):
    expected = dict(LIMITS, suite_id=SUITE, execute_authorized=True, approved_preflight_sha256=preflight_sha)
    if any(auth.get(k) != v for k, v in expected.items()) or not auth.get("user_text"):
        raise ValueError("a fresh authorization bound to this 24-shot preflight is required")


def execute(auth_path):
    pairs, bodies, requests = verified_plan()
    auth = parent.read(auth_path)
    authorize(auth, boundary.digest(FREEZE.read_bytes()))
    payload = {"authorization": auth, "authorization_sha256": boundary.digest(auth_path.read_bytes()),
               "requests": requests, "public_preflight_sha256": boundary.digest(FREEZE.read_bytes())}
    spec = importlib.util.spec_from_file_location("prohibition_engine", ROOT / "scripts/run_sun_modality_fewshot_v1.py")
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    engine.RUN, engine.JOURNAL, engine.PLAN = RUN, JOURNAL, PLAN
    engine.data = SimpleNamespace(load_split_text_only=lambda _: pairs)
    engine.fewshot = SimpleNamespace(load_demonstrations=lambda: ("", {}), request_body=lambda sid,text,*,block: bodies[sid])
    engine.plan_payload = lambda: payload
    engine.send_one = parent.paced(engine.send_one, allowed=lambda: llm_se.rate_for(datetime.now(llm_se.BEIJING))[0] == "off_peak")
    write_frozen(PLAN, parent.serialize({"payload": payload}))
    engine.execute()


def assess(ids, gold, old, new):
    if len(set(ids)) != len(ids) or not len(ids) == len(gold) == len(old) == len(new):
        raise ValueError("unaligned paired predictions")
    before, after = evaluate(gold, old), evaluate(gold, new)
    changes = [{"id": sid, "gold": g, "old": a, "new": b,
                "allowed": a != g and b == g and P in (a, b)}
               for sid,g,a,b in zip(ids,gold,old,new) if a != b]
    pa, pb = before["per_class"][P], after["per_class"][P]
    checks = {"fewer_prohibition_false_positives": pb["fp"] < pa["fp"],
              "higher_prohibition_f1": pb["f1"] > pa["f1"],
              "only_prohibition_related_corrections": all(c["allowed"] for c in changes),
              "other_precision_recall_f1_preserved": all(
                  after["per_class"][c][m] >= before["per_class"][c][m]
                  for c in LABELS if c != P for m in ("precision","recall","f1"))}
    return {"control": before, "candidate": after, "changes": changes,
            "checks": checks, "meets_all_requirements_on_this_split": all(checks.values())}


def report(auth_path):
    pairs, _, requests = verified_plan()
    auth = parent.read(auth_path)
    preflight_sha = boundary.digest(FREEZE.read_bytes())
    authorize(auth, preflight_sha)
    if parent.read(PLAN)["payload"] != {"authorization": auth, "authorization_sha256": boundary.digest(auth_path.read_bytes()),
                                        "requests": requests, "public_preflight_sha256": preflight_sha}:
        raise ValueError("actual execution differs from the agreed plan")
    finished, audit = parent.stats.verify_journal(boundary.read_events(JOURNAL), requests, auth)
    reference = parent.read(parent.RESULT)
    if boundary.digest(parent.JOURNAL.read_bytes()) != reference["journal_sha256"]:
        raise ValueError("22-shot journal drift")
    control = {r["sample_id"]:r["label"] for r in boundary.read_events(parent.JOURNAL) if r["kind"]=="finished"}
    rows = data.load_split("test")
    ids = [r.sample_id for r in rows]
    if ids != [s for s,_ in pairs] or set(ids) != set(control):
        raise ValueError("test population drift")
    result = assess(ids, [r.label for r in rows], [control[s] for s in ids], [finished[s]["label"] for s in ids])
    if result["control"] != reference["eligibility_shots"]:
        raise ValueError("baseline scores differ")
    result.update(audit=audit, suite_id=SUITE, journal_sha256=boundary.digest(JOURNAL.read_bytes()),
                  execution_plan_sha256=boundary.digest(PLAN.read_bytes()), control_journal_sha256=reference["journal_sha256"])
    write_frozen(RESULT, parent.serialize(result))
    print(result["checks"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "execute", "report"])
    parser.add_argument("--authorization", type=Path)
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare()
    elif args.authorization is None:
        parser.error("execute/report require --authorization")
    else:
        (execute if args.mode == "execute" else report)(args.authorization)
