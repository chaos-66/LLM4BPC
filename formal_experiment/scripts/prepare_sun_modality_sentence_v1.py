"""Prepare one frozen candidate and inspect stored evidence, entirely offline.

No execute option, transport, credential loading, retries or model inference.
Raw German, composed prompts, request bodies and response extracts stay local.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bpc_hybrid.datasets.sun_modality_importer import normalize_for_dedup
from bpc_hybrid.modality_benchmark import boundary, data, llm_se, sentence
from bpc_hybrid.modality_benchmark.metrics import evaluate
from prepare_sun_modality_eligibility_shots_v1 import check_isolation
from prepare_sun_modality_fewshot_v1 import write_frozen

LOCAL = ROOT / "outputs/development/sun_modality_sentence_v1"
REPORT = ROOT / "outputs/reports/sun_modality_sentence_v1_preflight.json"
REVIEW = ROOT / "outputs/reports/sun_modality_sentence_v1_baseline_review.json"
CONTRACT = ROOT / "configs/supplement/sun_modality_sentence_v1.json"
CONTROL = ROOT / "outputs/reports/sun_modality_eligibility_shots_v1_completed.json"
JOURNAL = ROOT / "outputs/development/sun_modality_eligibility_shots_v1/execution_v1/local_only/events.jsonl"
OLD_DIAGNOSIS = ROOT / "outputs/reports/sun_modality_residual_diagnosis_v1.json"


def serialize(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def assert_offline_policy(policy):
    if policy["execute_authorized"] is not False:
        raise ValueError("this offline tool cannot grant or consume execution authorization")
    if (policy["planned_requests"] != 426 or policy["retries"] != 0
            or policy["sampling"]["model"] != llm_se.MODEL_ALIAS
            or policy["pricing"]["cny_per_million_tokens"] != llm_se.PRICE_CNY_PER_MILLION):
        raise ValueError("candidate policy/model/price mismatch")


def verify_control():
    """Read-only historical replay; never rescore old outputs under the new API."""
    reference = sentence.read_json(CONTROL)
    if boundary.digest(JOURNAL.read_bytes()) != reference["journal_sha256"]:
        raise ValueError("historical 22-shot journal drift")
    events = boundary.read_events(JOURNAL)
    done = {r["sample_id"]: r for r in events if r["kind"] == "finished"}
    rows = data.load_split("test")
    if data.sha256_file(data.EXPECTED["test"]["path"]) != data.EXPECTED["test"]["sha256"]:
        raise ValueError("test data drift")
    if len(done) != 426 or set(done) != {r.sample_id for r in rows}:
        raise ValueError("incomplete historical membership")
    for row in rows:
        response = done[row.sample_id]
        if boundary.digest(response["raw_content"].encode()) != response["response_sha256"]:
            raise ValueError("historical response hash mismatch")
        if llm_se.extract_modality_label(response["raw_content"])["label"] != response["label"]:
            raise ValueError("historical first-clause readout drift")
    metrics = evaluate([r.label for r in rows], [done[r.sample_id]["label"] for r in rows])
    if metrics != reference["eligibility_shots"]:
        raise ValueError("historical metrics do not reproduce")
    return rows, done, metrics


def inspect_baseline(rows, done, metrics):
    old = sentence.read_json(OLD_DIAGNOSIS)
    lookup = {c["sample_id"]: c for c in old["cases"] if c["split"] == "test"}
    # These are AI review interpretations, not model-internal mechanisms.
    updated = {
        "sun_modality_2e41dabd46f1c416": ("fragment", "可见许可结构缺少完整主谓补足，当前 action 文本也不是一个精确原文片段。不能靠拼出缺失动作恢复句级断言；记录输入不确定性。"),
        "sun_modality_fdc9485a3ed1b40f": ("status_reading", "当前仍将法律关系认定标为 obligation。应比较关系被认定的状态与执行评估的要求；这是 AI 语义解释，不能仅凭认定动词统一归为 D。"),
        "sun_modality_5dd905d7bef7684c": ("status_reading", "当前证据已覆盖被动征收谓词，不再是仅普通助动词。可见主断言描述征收方式，尾部仍残缺；状态与行为指令需分辨。"),
        "sun_modality_68a7b0d9b95fb81e": ("predicate_coverage", "当前只有一个 definition clause，其 action 含列作债权的执行指令。旧 reviewer 的 D/O 分离和首标签丢失解释已不适用；本次解释为不同情态动作共用标签。"),
        "sun_modality_e281d33605497ded": ("projection", "当前已分别输出维持状态 D 和后续禁止 P。旧 reviewer 的禁止漏抽解释不再成立；首标签投影丢失后续 P，但不能据 Gold 自动提升它。"),
        "sun_modality_7890eade5f0098ac": ("boundary_unresolved", "22-shot 新增回归：条件性费用计入被标 definition，原标签 obligation；资格限制与执行指令的语料边界待解，条件本身不能决定为 D。"),
        "sun_modality_6d46f2ca8400b2bc": ("condition_split", "22-shot 新增回归：引导语单列 definition，许可位于下一 clause。引导语应结合后续主断言，不宜作为独立规则；它不是可信的独立多命题投影例。"),
        "sun_modality_19490870e3fe6c41": ("predicate_coverage", "同一 obligation clause 的两个 action 分别涉及制作和不核查；不同规范作用被共用标签。输出事实支持覆盖检查，内部成因未知。"),
        "sun_modality_f5037bcc56922965": ("condition_split", "前置转移条件仍单列 definition，后续主指令为 obligation；解释为条件误拆而非两个独立规则间的纯投影损失。"),
    }
    cases, local = [], []
    for row in rows:
        response = done[row.sample_id]
        if response["label"] == row.label:
            continue
        obj = llm_se._extract_json_object(response["raw_content"])
        clauses = obj.get("clauses", [])
        previous = lookup.get(row.sample_id)
        group, inference = updated.get(row.sample_id, (
            previous["primary_diagnostic_group"] if previous else "unassigned",
            previous["observation_zh"] if previous else "需核对",
        ))
        labels = [c.get("modality", {}).get("label") for c in clauses]
        item = {
            "sample_id": row.sample_id, "source_text_sha256": boundary.digest(row.text.encode()),
            "response_sha256": response["response_sha256"],
            "observed": {"original_sentence_label": row.label, "first_clause_label": response["label"],
                         "clause_labels_in_returned_order": labels, "clause_count": len(clauses),
                         "action_counts": [len(c.get("actions", [])) for c in clauses],
                         "condition_counts": [len(c.get("conditions", [])) for c in clauses],
                         "original_label_present_after_first": row.label in labels[1:]},
            "ai_primary_group": group, "ai_interpretation_zh": inference,
            "interpretation_status": "Codex AI explanatory review; not human adjudication or proven internal mechanism",
            "old_reviewer_case_id": previous["case_id"] if previous else None,
            "old_reviewer_clause_labels": previous["clause_labels_in_source_order"] if previous else None,
        }
        cases.append(item)
        local.append(dict(item, source_text=row.text, raw_response=response["raw_content"]))
    counts = dict(Counter(c["ai_primary_group"] for c in cases))
    expected = {"boundary_unresolved": 16, "status_reading": 7, "projection": 3,
                "condition_split": 2, "predicate_coverage": 2, "fragment": 3}
    if len(cases) != 33 or counts != expected:
        raise ValueError("review membership/category counts require explicit reinspection")
    current_ids = {c["sample_id"] for c in cases}
    probes = []
    train = data.load_split("train")
    for old_probe in old["train_pattern_probes"]:
        matches = [r for r in train if re.search(old_probe["regex"], r.text)]
        probes.append({"probe": old_probe["probe"], "count": len(matches),
                       "label_counts": dict(Counter(r.label for r in matches)),
                       "matches": [{"sample_id": r.sample_id, "label": r.label,
                                    "text_sha256": boundary.digest(r.text.encode())} for r in matches]})
        if len(matches) != old_probe["count"] or probes[-1]["label_counts"] != old_probe["labels"]:
            raise ValueError("training probe changed")
    review = {"suite_id": sentence.SUITE_ID, "api_calls": 0,
              "evidence_kind": "existing 22-shot responses, original labels and AI interpretation kept separate",
              "control_journal_sha256": boundary.digest(JOURNAL.read_bytes()),
              "control_report_sha256": boundary.digest(CONTROL.read_bytes()),
              "old_diagnosis_sha256": boundary.digest(OLD_DIAGNOSIS.read_bytes()),
              "historical_metrics_unchanged": metrics, "historical_correct": 393, "current_errors": 33,
              "reviewer_errors": 34, "reviewer_errors_now_correct": sorted(set(lookup) - current_ids),
              "new_errors_vs_reviewer": sorted(current_ids - set(lookup)),
              "ai_primary_group_counts": counts, "cases": cases,
              "train_boundary_probes": probes,
              "probe_limit": "Whole-sentence lexical retrieval, not clause annotations or an automatic class rule. Matches never enter requests as additional demonstrations.",
              "mechanism_limit": "Observations cannot establish model-internal causes or candidate performance. No Gold changes."}
    return review, local


def build():
    policy = sentence.read_json(CONTRACT)
    assert_offline_policy(policy)
    system, examples, selected, manifest = sentence.compose_prompt()
    parent_18 = sentence.read_json(ROOT / "prompts/sun_compat/modality_fewshot_v1/selection_manifest.json")["selections"]
    parent_4 = sentence.read_json(ROOT / "prompts/sun_compat/modality_eligibility_shots_v1/selection_manifest.json")["examples"]
    parents = parent_18 + parent_4
    replacements = {17: "sun_modality_863058f4cad7ea4e", 15: "sun_modality_c8712b2d00865a9d",
                    4: "sun_modality_f56a47d5cde6fdc7", 7: "sun_modality_c33e7e546525587d"}
    if {x["parent_position"] for x in manifest["examples"]} != set(range(1, 23)):
        raise ValueError("parent demonstration membership changed")
    for item in manifest["examples"]:
        position = item["parent_position"]
        parent = parents[position - 1]
        if (item["sample_id"] != replacements.get(position, parent["sample_id"])
                or item["label"] != parent["label"]
                or item["replacement_of"] != (parent["sample_id"] if position in replacements else None)):
            raise ValueError("more than the four specified definition replacements")
    pairs_by_split = {s: data.load_split_text_only(s) for s in ("dev", "test")}
    new_ids = {s["sample_id"] for s in manifest["examples"] if s["replacement_of"]}
    additions = [r for r in selected if r.sample_id in new_ids]
    # Original 18 retained examples receive the historical exact/normalized check;
    # all four replacements additionally receive the frozen stricter near check.
    for split, held in pairs_by_split.items():
        check_isolation(additions, held)
        held_ids = {sid for sid, _ in held}
        held_texts = {normalize_for_dedup(t) for _, t in held}
        if any(r.sample_id in held_ids or normalize_for_dedup(r.text) in held_texts for r in selected):
            raise ValueError("selected demonstration overlaps held-out membership/text")
    for obj in examples:
        rr = obj["rule_record"]
        checked = sentence.parse_response(json.dumps(obj), request_id=rr["sample_id"], source_text=rr["source_text"])
        if checked["status"] != "ok" or checked["rule_record_validation"]["errors"]:
            raise ValueError("synthetic envelope fixture failed")
    bodies, requests = [], []
    settings = policy["sampling"]
    rate = policy["pricing"]["cny_per_million_tokens"]["off_peak"]
    for i, (sid, text) in enumerate(pairs_by_split["test"], 1):
        request_id = f"input_{i:06d}"
        body = sentence.request_body(request_id, text, system=system, examples=examples)
        for key in ("model", "temperature", "top_p", "max_tokens", "stream", "thinking"):
            if body[key] != settings[key]:
                raise ValueError("sampling drift")
        if "sun_modality_" in json.dumps(body):
            raise ValueError("dataset ID leaked into request")
        requests.append({"sample_id": sid, "request_id": request_id,
                         "source_text_sha256": boundary.digest(text.encode()),
                         "request_sha256": boundary.digest(boundary.wire_bytes(body)),
                         "estimated_input_tokens": llm_se.estimate_input_tokens(body),
                         "per_send_reservation_cny": boundary.reserve_cost(body, rate)})
        bodies.append({"sample_id": sid, "request_id": request_id, "body": body})
    if len(requests) != 426 or len({r["sample_id"] for r in requests}) != 426:
        raise ValueError("expected all 426 test requests")
    # Historical analysis is deliberately downstream of completed request construction.
    rows, done, metrics = verify_control()
    review, local_review = inspect_baseline(rows, done, metrics)
    mean_output = sum(r["usage"]["completion_tokens"] for r in done.values()) / 426
    estimated_output = mean_output + 256  # declared allowance, not measured candidate usage
    input_tokens = sum(r["estimated_input_tokens"] for r in requests)
    estimate = (input_tokens * rate["input_cache_miss"] + 426 * estimated_output * rate["output"]) / 1e6
    source_paths = [Path(__file__), CONTRACT, sentence.PROMPT_DIR / "system_prompt.md",
                   sentence.PROMPT_DIR / "modality_guidance.md", sentence.PROMPT_DIR / "selection_manifest.json",
                   sentence.PROMPT_DIR / "format_examples.json", ROOT / "configs/schemas/sun_sentence_modality_v1.schema.json",
                   ROOT / "src/bpc_hybrid/modality_benchmark/sentence.py",
                   ROOT / "src/bpc_hybrid/modality_benchmark/metrics.py",
                   ROOT / "src/bpc_hybrid/modality_benchmark/llm_se.py",
                   ROOT / "src/bpc_hybrid/modality_benchmark/data.py",
                   ROOT / "src/bpc_hybrid/modality_benchmark/boundary.py",
                   ROOT / "src/bpc_hybrid/stage2_canonical.py",
                   ROOT / "configs/schemas/stage2_prediction.schema.json",
                   ROOT / "scripts/prepare_sun_modality_eligibility_shots_v1.py",
                   ROOT / "scripts/prepare_sun_modality_fewshot_v1.py",
                   ROOT / "prompts/sun_compat/modality_fewshot_v1/selection_manifest.json",
                   ROOT / "prompts/sun_compat/modality_eligibility_shots_v1/selection_manifest.json",
                   llm_se.PROMPT_PATH,
                   ROOT / "src/bpc_hybrid/datasets/sun_modality_importer.py",
                   ROOT / "tests/test_modality_sentence_v1.py"]
    preflight = {"suite_id": sentence.SUITE_ID, "candidate_name": sentence.NAME,
                 "status": "offline_prepared_awaiting_batch_budget_authorization",
                 "api_calls": 0, "execute_authorized": False, "performance_metrics": None,
                 "policy": policy, "requests": requests,
                 "source_sha256_lf_utf8": {p.relative_to(ROOT).as_posix(): boundary.digest(p.read_text(encoding="utf-8").encode()) for p in source_paths},
                 "splits": data.dataset_binding(), "demonstrations": 22,
                 "class_totals": manifest["class_totals"],
                 "isolation": {"new_examples": 4, "retained_examples": 18,
                               "all_22_exact_id_or_normalized_text_hits": 0,
                               "new_near_duplicate_hits": 0,
                               "new_near_comparisons": {s: len(p) * 4 for s, p in pairs_by_split.items()},
                               "near_rule": "same prepare_sun_modality_eligibility_shots_v1.near_match; token ratio >= .80, contiguous >= .85 of shorter >= 8 tokens, or character ratio >= .88",
                               "retained_18_near_check": "not newly claimed; same exact/normalized isolation as parent",
                               "selector_held_out_labels_read": False},
                 "system_prompt_sha256_utf8": boundary.digest(system.encode()),
                 "synthetic_examples": 6, "baseline_review_sha256": boundary.digest(serialize(review)),
                 "budget_estimate": {"method": "UTF-8 JSON bytes / 3 rounded up; no tokenizer, all cache miss, 22-shot mean completion + 256 new-envelope tokens",
                                     "historical_mean_output_tokens": mean_output,
                                     "assumed_output_tokens_per_call": estimated_output,
                                     "estimated_input_tokens_total": input_tokens,
                                     "estimated_total_cny": estimate,
                                     "proposed_cap_cny": policy["proposed_cap_cny"],
                                     "full_reservation_sum_cny": sum(r["per_send_reservation_cny"] for r in requests),
                                     "per_call_reservation_range_cny": [min(r["per_send_reservation_cny"] for r in requests), max(r["per_send_reservation_cny"] for r in requests)],
                                     "cap_guarantees_completion": False,
                                     "note": "Estimate is not a charge or upper bound. Cap is only a proposal; a future run stops before exceeding it even if fewer than 426 are issued."}}
    return preflight, system, examples, bodies, review, local_review


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify existing frozen preparation without writing")
    args = parser.parse_args()
    report, system, examples, bodies, review, local_review = build()
    template = sentence.request_body("{request_id}", "{source_text}", system=system, examples=examples)
    artifacts = {
        LOCAL / "composed_system_prompt.txt": (system + "\n").encode(),
        LOCAL / "complete_prompt_template.json": serialize(template),
        LOCAL / "requests.json": serialize(bodies),
        LOCAL / "baseline_cases_local.json": serialize(local_review),
        REPORT: serialize(report), REVIEW: serialize(review),
    }
    for path, raw in artifacts.items():
        if args.check:
            if not path.exists() or path.read_bytes() != raw:
                raise ValueError("frozen candidate differs: " + str(path))
        else:
            write_frozen(path, raw)
    print(json.dumps({"status": report["status"], "requests": len(bodies), "examples": 22,
                      "api_calls": 0, "estimated_cny": report["budget_estimate"]["estimated_total_cny"],
                      "preflight_sha256": boundary.digest(serialize(report))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
