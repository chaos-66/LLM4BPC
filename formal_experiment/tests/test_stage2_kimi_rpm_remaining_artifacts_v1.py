"""Verify the final 900-attempt merge and new Kimi responses offline."""
from datetime import datetime
import math

import pytest

from bpc_hybrid import multi_model_stage2 as m
from bpc_hybrid.h1_transport import decode_chat_completion_envelope
from bpc_hybrid.sep_c3_modular_evaluation import attempt_rows, evaluate_coarse
import run_stage2_kimi_rpm_remaining_v1 as run
from test_multi_model_stage2 import no_live_access


@pytest.fixture(scope="module")
def evidence():
    value = m.read_json(run.out_dir() / "plan.json")
    report = m.read_json(run.report_path())
    manifest = m.read_json(run.out_dir() / "manifest.json")
    starts, finishes, head = m._load_ledger(run.out_dir() / "calls_ledger.jsonl", value["request_plan"])
    return value, report, manifest, starts, finishes, head


def test_hash_bindings_new_and_parent_artifacts_unchanged(evidence):
    value, report, manifest, starts, finishes, head = evidence
    run.verify(value, m.ROOT)
    m._verify_saved_calls(run.out_dir(), value["request_plan"], run.ledger_auth(value), starts, finishes)
    assert manifest["source_bindings"] == value["source_bindings"]
    assert manifest["new_calls"] == 145 and manifest["combined_calls"] == report["actual_calls"] == 900
    assert manifest["parent_manifest_sha256"] == m.digest((run.parent.out_dir() / "manifest.json").read_bytes())
    parent = m.read_json(run.parent.out_dir() / "manifest.json")
    for current in (manifest, parent):
        for relative, sha in current["artifacts"].items():
            assert m.digest((m.ROOT / relative).read_bytes()) == sha, relative
    saved = m.read_json(run.out_dir() / "provider_manifest.json")
    assert saved["ledger_head_sha256"] == head and saved["llm_calls"] == len(starts) == len(finishes) == 145
    assert not any(f["needs_attention"] for f in finishes.values())


def test_900_unique_attempts_same_150_ids_and_no_repeated_429(evidence):
    value, report, _, starts, _, _ = evidence
    assert report["status"] == "succeeded" and report["retry"] == 0
    assert report["actual_new_calls"] == 447 and report["actual_new_calls_in_run"] == 145
    assert not (set(starts) & set(value["parent_started_ids"]))
    assert value["parent_first_started_id"] not in starts
    previous = m.read_json(run.parent.report_path())
    assert previous["actual_calls"] + len(starts) == report["actual_calls"] == 900
    for name in ("qwen", "grok", "minimax", "glm", "mimo"):
        assert report["providers"][name] == previous["providers"][name]
    rows = m.read_json(run.out_dir() / "combined_predictions.json")["records"]
    old_rows = m.read_json(run.parent.provider_dir("kimi") / "combined_predictions.json")["records"]
    assert len(rows) == 150 and [r["sample_id"] for r in rows] == [r["sample_id"] for r in old_rows]
    assert rows[:5] == old_rows[:5]
    assert rows[0]["request_status"] == "ok" and rows[4]["request_status"] == "failed"
    assert rows[4]["sample_id"] == "estg_000021"
    assert all(r["request_status"] != "not_attempted" for r in rows)
    assert all(r["attempted"] == r["denominator"] == 150 for r in report["providers"].values())


def test_actual_pacing_and_kimi_counter_evidence_without_reasoning_content(evidence):
    value, _, _, starts, finishes, _ = evidence
    times = sorted(datetime.fromisoformat(s["timestamp_utc"]).timestamp() for s in starts.values())
    assert times[0] >= value["earliest_start_epoch"]
    assert all(b - a >= 21 for a, b in zip(times, times[1:]))
    requests = {r["request_id"]: r for r in value["request_plan"]["requests"]}
    for rid, finish in finishes.items():
        response = m.read_json(run.out_dir() / finish["response_path"])
        decoded = decode_chat_completion_envelope(response["raw_response_utf8"].encode("utf-8"))
        assert not decoded["reasoning_present"] and not decoded["content"].lstrip().startswith("<think>")
        expected = run.parent.check_nonthinking("kimi", requests[rid], decoded, value["authorization"])
        assert expected == response["nonthinking_check"]
        assert expected["reported_reasoning_tokens"] == response["usage"].get("reasoning_tokens")
        assert expected["reported_reasoning_tokens"] in (None, 0, 1)
        assert requests[rid]["body"]["thinking"] == {"type": "disabled"}
        if expected["reported_reasoning_tokens"] == 1:
            assert expected["counter_exception_user_authorized"] and not expected["one_token_meaning_verified"]


def test_final_kimi_shared_pooled_score_failed_denominator_and_historical_table(evidence):
    _, report, _, _, _, _ = evidence
    assert report["primary_metric"] == "coarse_five_field_micro.f1"
    rows = m.read_json(run.out_dir() / "combined_predictions.json")["records"]
    gold = m.read_json(m.ROOT / run.parent.parent.GOLD)
    evaluation = evaluate_coarse(gold, attempt_rows(rows), method_id="multi_model_kimi")
    metrics = report["providers"]["kimi"]["metrics"]
    assert metrics["overall"] == evaluation["coarse_five_field_micro"]
    assert metrics["per_field"] == evaluation["five_fields"]
    assert metrics["modality_macro_f1"] == evaluation["modality_labels"]["macro_f1"]
    assert metrics["failed_count"] == evaluation["failed_count"] == 150 - report["providers"]["kimi"]["valid_predictions"]
    fixed = m.read_json(m.ROOT / "outputs/reports/stage2_table1_paper_final_v1.json")
    for name, arm in (("deepseek_historical", "direct_llm"), ("sun_historical", "sun_rule_only")):
        assert report["historical_baselines"][name]["f1"] == fixed["arms"][arm]["overall_pooled_five_span_fields"]["f1"]


def test_final_kimi_tokens_costs_and_original_budget(evidence):
    value, report, _, _, finishes, _ = evidence
    base = m.read_json(run.parent.report_path())["providers"]["kimi"]
    row = report["providers"]["kimi"]
    usages = [m.read_json(run.out_dir() / f["response_path"])["usage"] for f in finishes.values()]
    assert row["input_tokens"] == base["input_tokens"] + sum(u.get("prompt_tokens", 0) for u in usages)
    assert row["output_tokens"] == base["output_tokens"] + sum(u.get("completion_tokens", 0) for u in usages)
    spent = sum(f["reserved_cost"] for f in finishes.values())
    assert math.isclose(row["conservative_uncached_cost"], base["conservative_uncached_cost"] + spent, rel_tol=0, abs_tol=1e-12)
    assert spent <= value["budget"]["max_cost"]
    assert not row["account_deduction_verified"] and row["cost_currency"] == "CNY"


def test_final_capsule_byte_identical_and_linked_to_preserved_parent(evidence):
    _, report, manifest, _, _, _ = evidence
    capsule = m.ROOT / "outputs/evidence/stage2_multi_model_remaining_v1" / run.RUN_ID
    index = m.read_json(capsule / "index.json")
    assert index["actual_calls"] == report["actual_calls"] == 900
    assert index["actual_new_calls"] == 145
    assert index["github_raw_artifact_export_authorized"] is False
    assert set(manifest["artifacts"]).issubset(index["copies"])
    for relative, item in index["copies"].items():
        assert ".env" not in relative and "data/gold/" not in relative
        assert m.digest((m.ROOT / relative).read_bytes()) == item["sha256"]
        assert m.digest((m.ROOT / item["copy"]).read_bytes()) == item["sha256"]
