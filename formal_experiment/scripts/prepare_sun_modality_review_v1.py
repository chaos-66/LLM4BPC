"""Offline review-prompt preparation, with 426 parent request bindings checked."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from bpc_hybrid.modality_benchmark import boundary, data, fewshot, llm_se, review_prompt
from prepare_sun_modality_fewshot_v1 import write_frozen

REPORT = ROOT / "outputs/reports/sun_modality_review_v1_preflight.json"
LOCAL = ROOT / "outputs/development/sun_modality_review_v1"


def verify_parent_sources(bindings):
    for path, expected in bindings.items():
        actual = boundary.digest((ROOT / path).read_text(encoding="utf-8").encode())
        if actual != expected:
            raise ValueError("parent source drift: " + path)


def build_plan():
    contract = review_prompt.read_contract()
    parent = json.loads((ROOT / contract["parent_preflight"]["path"]).read_text(encoding="utf-8"))
    verify_parent_sources(parent["payload"]["source_sha256_lf_utf8"])
    expected = {x["sample_id"]: x["fewshot_request_sha256"] for x in parent["payload"]["requests"]}
    block, _ = fewshot.load_demonstrations()
    guidance = (ROOT / contract["guidance"]["path"]).read_text(encoding="utf-8").strip()
    pairs = data.load_split_text_only("test")
    if len(pairs) != 426 or len(expected) != 426 or {sid for sid, _ in pairs} != set(expected):
        raise ValueError("review branch population mismatch")
    requests, system = [], None
    for sid, text in pairs:
        before = fewshot.request_body(sid, text, block=block)
        if boundary.digest(boundary.wire_bytes(before)) != expected[sid]:
            raise ValueError("parent few-shot request drift")
        after = review_prompt.request_body(sid, text, block=block)
        current_system = after["messages"][0]["content"]
        if current_system != before["messages"][0]["content"] + "\n\n" + guidance:
            raise ValueError("unexpected review composition")
        if system is not None and system != current_system:
            raise ValueError("review prefix differs across samples")
        system = current_system
        wire_hash = boundary.digest(boundary.wire_bytes(after))
        added = llm_se.estimate_input_tokens(after) - llm_se.estimate_input_tokens(before)
        after["messages"][0]["content"] = before["messages"][0]["content"]
        if after != before:
            raise ValueError("review branch changes more than the system addition")
        requests.append({"sample_id": sid, "parent_request_sha256": expected[sid],
                         "review_request_sha256": wire_hash, "estimated_added_input_tokens": added})
    paths = ["scripts/prepare_sun_modality_review_v1.py", "src/bpc_hybrid/modality_benchmark/review_prompt.py"]
    return {"suite_id": contract["suite_id"], "contract": contract, "requests": requests,
            "source_sha256_lf_utf8": {p: boundary.digest((ROOT / p).read_text(encoding="utf-8").encode()) for p in paths},
            "parent_source_bindings": parent["payload"]["source_sha256_lf_utf8"],
            "system_prompt_sha256": boundary.digest(system.encode()),
            "checks": {"all_426_parent_requests_match": True, "only_system_appended": True,
                       "train_examples_unchanged": 18, "test_sentence_examples_added": 0,
                       "gold_changed": False, "evaluator_changed": False},
            "status": "offline_prepared_not_executed", "real_api_calls": 0, "performance_metrics": None}, system


def main():
    plan, system = build_plan()
    write_frozen(LOCAL / "composed_system_prompt.txt", (system + "\n").encode())
    write_frozen(REPORT, (json.dumps(plan, ensure_ascii=False, indent=2) + "\n").encode())
    increments = [r["estimated_added_input_tokens"] for r in plan["requests"]]
    print(json.dumps({"requests_checked": len(plan["requests"]), "input_increment_estimate_range": [min(increments), max(increments)],
                      "real_api_calls": 0, "performance_metrics": None, "preview": str(LOCAL / "composed_system_prompt.txt")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
