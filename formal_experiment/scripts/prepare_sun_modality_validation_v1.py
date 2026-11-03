"""Freeze a test diagnostic and a paired dev validation, without API or labels."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import prepare_sun_modality_review_v1 as review_prepared
from prepare_sun_modality_fewshot_v1 import write_frozen
from bpc_hybrid.modality_benchmark import boundary, data, fewshot, llm_se, review_prompt

REPORT = ROOT / "outputs/reports/sun_modality_validation_v1_preflight_v2.json"
CONTRACT = ROOT / "configs/supplement/sun_modality_validation_v2.json"
SOURCES = [
    "scripts/prepare_sun_modality_validation_v1.py",
    "scripts/run_sun_modality_validation_v1.py",
    "scripts/build_sun_modality_validation_report_v1.py",
    "scripts/run_sun_modality_fewshot_v1.py",
    "scripts/run_sun_modality_boundary_v1.py",
    "scripts/build_sun_modality_fewshot_report_v1.py",
    "scripts/build_sun_modality_boundary_stats_v1.py",
    "src/bpc_hybrid/modality_benchmark/metrics.py",
    "src/bpc_hybrid/llm_client.py", "src/bpc_hybrid/llm_config.py",
    "src/bpc_hybrid/h1_transport.py",
]


def read_contract():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for key, spec in contract["bindings"].items():
        if boundary.digest((ROOT / spec["path"]).read_bytes()) != spec["sha256"]:
            raise ValueError("validation binding drift: " + key)
    if contract["execution_authorized"] is not False:
        raise ValueError("preparation contract is not execution authorization")
    return contract


def schedule(test, dev):
    """Every sample participates; no error filtering, labels or adaptive choice."""
    if {sid for sid, _ in test} & {sid for sid, _ in dev}:
        raise ValueError("test/dev identifier overlap")
    if {fewshot.normalize_for_dedup(t) for _, t in test} & {fewshot.normalize_for_dedup(t) for _, t in dev}:
        raise ValueError("test/dev normalized text overlap")
    result = [("test", "review", sid, text) for sid, text in test]
    for index, (sid, text) in enumerate(sorted(dev)):
        arms = ("fewshot", "review") if index % 2 == 0 else ("review", "fewshot")
        result.extend(("dev", arm, sid, text) for arm in arms)
    return result


def body_for(arm, sid, text, block):
    if arm not in ("fewshot", "review"):
        raise ValueError("unknown prompt arm")
    module = fewshot if arm == "fewshot" else review_prompt
    return module.request_body(sid, text, block=block)


def build_payload():
    contract = read_contract()
    for name, spec in data.EXPECTED.items():
        if data.sha256_file(spec["path"]) != spec["sha256"]:
            raise ValueError("split drift: " + name)
    review_plan, _ = review_prepared.build_plan()
    frozen_review = json.loads(review_prepared.REPORT.read_text(encoding="utf-8"))
    if review_plan != frozen_review:
        raise ValueError("frozen review preflight drift")
    expected_test = {r["sample_id"]: r["review_request_sha256"] for r in review_plan["requests"]}
    test, dev = data.load_split_text_only("test"), data.load_split_text_only("dev")
    if len(test) != 426 or len(dev) != 420 or len({s for s, _ in dev}) != 420:
        raise ValueError("population mismatch")
    block, _ = fewshot.load_demonstrations()
    requests, token_totals = [], Counter()
    for split, arm, sid, text in schedule(test, dev):
        body = body_for(arm, sid, text, block)
        request_hash = boundary.digest(boundary.wire_bytes(body))
        if split == "test" and request_hash != expected_test[sid]:
            raise ValueError("test review request drift")
        if arm == "review":
            parent_body = body_for("fewshot", sid, text, block)
            check = dict(body, messages=[dict(m) for m in body["messages"]])
            guidance = (ROOT / review_prompt.read_contract()["guidance"]["path"]).read_text(encoding="utf-8").strip()
            if check["messages"][0]["content"] != parent_body["messages"][0]["content"] + "\n\n" + guidance:
                raise ValueError("unexpected prompt addition")
            check["messages"][0]["content"] = parent_body["messages"][0]["content"]
            if check != parent_body:
                raise ValueError("non-system request difference")
        call_id = split + ":" + arm + ":" + sid
        estimated_tokens = llm_se.estimate_input_tokens(body)
        token_totals[split + ":" + arm] += estimated_tokens
        requests.append({"call_id": call_id, "sample_id": sid, "split": split, "arm": arm,
                         "request_sha256": request_hash, "estimated_input_tokens": estimated_tokens})
    counts = dict(Counter(r["split"] + ":" + r["arm"] for r in requests))
    if counts != contract["planned_calls"] or len({r["call_id"] for r in requests}) != 1266:
        raise ValueError("call schedule differs from contract")
    historical_journal = ROOT / contract["bindings"]["historical_journal"]["path"]
    finished = [r for r in boundary.read_events(historical_journal) if r["kind"] == "finished"]
    mean_output = sum(r["usage"]["completion_tokens"] for r in finished) / len(finished)
    rate = contract["requested_limits"]["price_cny_per_million"]["off_peak"]
    estimates = {k: (tokens * rate["input_cache_miss"] + counts[k] * mean_output * rate["output"]) / 1e6
                 for k, tokens in token_totals.items()}
    return {"suite_id": contract["suite_id"], "contract": contract,
            "contract_sha256": boundary.digest(CONTRACT.read_bytes()), "requests": requests,
            "runtime_sources_sha256_lf_utf8": {p: boundary.digest((ROOT / p).read_text(encoding="utf-8").encode()) for p in SOURCES},
            "parent_source_bindings": {**review_plan["parent_source_bindings"], **review_plan["source_sha256_lf_utf8"]},
            "estimates_cny_no_cache": estimates, "estimated_total_cny": sum(estimates.values()),
            "estimate_basis": "UTF-8 input heuristic, frozen old few-shot mean completion length; not a cost guarantee",
            "checks": {"test_review_requests_match": 426, "dev_pairs": 420, "dev_labels_read_for_preparation": False,
                       "all_samples_included": True, "only_system_addition": True},
            "real_api_calls": 0, "performance_metrics": None}


def verify_frozen():
    plan = json.loads(REPORT.read_text(encoding="utf-8"))
    if build_payload() != plan:
        raise ValueError("validation preflight no longer reproduces")
    return plan


def main():
    payload = build_payload()
    write_frozen(REPORT, (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode())
    print(json.dumps({"calls": len(payload["requests"]), "estimates_cny": payload["estimates_cny_no_cache"],
                      "estimated_total_cny": payload["estimated_total_cny"], "real_api_calls": 0,
                      "preflight_sha256": boundary.digest(REPORT.read_bytes())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
