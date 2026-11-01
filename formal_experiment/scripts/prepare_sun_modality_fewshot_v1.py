"""Offline prompt preparation only: no transport, credentials, or API mode."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bpc_hybrid.modality_benchmark import boundary, data, fewshot, llm_se

LOCAL = ROOT / "outputs/development/sun_modality_fewshot_v1/prepared_v1"
REPORT = ROOT / "outputs/reports/sun_modality_fewshot_v1_preflight.json"


def write_frozen(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError("refusing to overwrite a different prepared artifact: " + str(path))
        return
    with path.open("xb") as handle:
        handle.write(raw)


def build_plan() -> tuple[dict, str, str]:
    contract = fewshot.read_contract()
    block, manifest = fewshot.load_demonstrations()
    pairs = data.load_split_text_only("test")
    if len(pairs) != 426 or len({sid for sid, _ in pairs}) != 426:
        raise ValueError("test membership is not 426 unique samples")
    requests = []
    system = None
    for sid, text in pairs:
        before = boundary.request_body(sid, text)
        after = fewshot.request_body(sid, text, block=block)
        new_system = after["messages"][0]["content"]
        after_for_check = dict(after, messages=[dict(m) for m in after["messages"]])
        after_for_check["messages"][0]["content"] = before["messages"][0]["content"]
        if after_for_check != before or new_system != before["messages"][0]["content"] + "\n\n" + block.strip():
            raise ValueError("few-shot branch changes more than the appended system block")
        if system is not None and system != new_system:
            raise ValueError("demonstration prefix varies across samples")
        system = new_system
        requests.append({"sample_id": sid,
                         "boundary_request_sha256": boundary.digest(boundary.wire_bytes(before)),
                         "fewshot_request_sha256": boundary.digest(boundary.wire_bytes(after)),
                         "estimated_added_input_tokens": llm_se.estimate_input_tokens(after) - llm_se.estimate_input_tokens(before)})
    historical = contract["historical_boundary"]
    if boundary.digest((ROOT / historical["path"]).read_bytes()) != historical["sha256"]:
        raise ValueError("historical boundary report drift")
    paths = ["scripts/prepare_sun_modality_fewshot_v1.py",
             "src/bpc_hybrid/modality_benchmark/fewshot.py",
             "src/bpc_hybrid/modality_benchmark/boundary.py",
             "src/bpc_hybrid/modality_benchmark/data.py",
             "src/bpc_hybrid/modality_benchmark/llm_se.py",
             "src/bpc_hybrid/datasets/sun_modality_importer.py",
             "src/bpc_hybrid/prompt_loader.py"]
    return {"suite_id": contract["suite_id"], "status": "offline_prepared_not_executed",
            "claim_scope": contract["claim_scope"], "contract": contract,
            "source_sha256_lf_utf8": {p: boundary.digest((ROOT / p).read_text(encoding="utf-8").encode("utf-8")) for p in paths},
            "requests": requests, "examples": len(manifest["selections"]),
            "class_totals": manifest["class_totals"],
            "system_prompt_sha256_utf8": boundary.digest(system.encode("utf-8")),
            "checks": {"all_demonstrations_from_train": True,
                       "train_held_out_normalized_text_overlap": 0,
                       "held_out_labels_used_for_selection": False,
                       "only_system_append_changed_on_all_426_requests": True},
            "token_estimate_method": "difference of UTF-8 JSON byte length / 3 rounded up; not a tokenizer measurement",
            "real_api_calls": 0, "performance_metrics": None}, block, system


def main() -> None:
    plan, block, system = build_plan()
    payload_hash = boundary.digest(json.dumps(plan, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    existing = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else None
    if existing is not None and existing["payload"] != plan:
        raise ValueError("preflight already frozen at a different state")
    doc = existing or {"created_at": datetime.now(timezone.utc).isoformat(),
                       "payload_sha256": payload_hash, "payload": plan}
    write_frozen(LOCAL / "fewshot_block.txt", block.encode("utf-8"))
    write_frozen(LOCAL / "composed_system_prompt.txt", (system + "\n").encode("utf-8"))
    write_frozen(REPORT, (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    increments = [x["estimated_added_input_tokens"] for x in plan["requests"]]
    print(json.dumps({"report": str(REPORT), "examples": plan["examples"], "requests_checked": len(plan["requests"]),
                      "estimated_added_input_tokens_range": [min(increments), max(increments)],
                      "real_api_calls": 0, "status": plan["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
