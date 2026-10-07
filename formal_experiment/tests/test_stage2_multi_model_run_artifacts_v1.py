"""Offline verification of this authorized run's persisted artifacts; no HTTP or keys."""
import math

import pytest

from bpc_hybrid import multi_model_stage2 as m
from bpc_hybrid.sep_c3_modular_evaluation import attempt_rows, evaluate_coarse
import run_stage2_multi_model_all_v1 as batch
from test_multi_model_stage2 import no_live_access


@pytest.fixture(scope="module")
def run():
    value, plans, auths = batch.saved_plans(m.ROOT)
    report = m.read_json(batch.report_path())
    manifest = m.read_json(batch.batch_dir() / "manifest.json")
    return value, plans, auths, report, manifest


def output(plan):
    return m.ROOT / "outputs/development/stage2_multi_model_v1" / plan["run_id"]


def test_sources_artifacts_and_frozen_900_request_bodies(run):
    value, plans, auths, report, manifest = run
    batch.verify_batch(value, plans, auths)
    assert manifest["source_bindings"] == value["source_bindings"]
    assert manifest["llm_calls"] == report["actual_calls"] <= 900
    assert manifest["status"] == report["status"]
    for path, sha in manifest["artifacts"].items():
        assert m.digest((m.ROOT / path).read_bytes()) == sha, path
    reference = [r["sample_id"] for r in plans["qwen"]["requests"]]
    assert len(reference) == len(set(reference)) == 150
    for name, plan in plans.items():
        assert plan["retry"] == 0 and plan["thinking_requirement"] == "disabled"
        assert [r["sample_id"] for r in plan["requests"]] == reference
        for request in plan["requests"]:
            body = request["body"]
            assert m.digest(m.encode(body)) == request["body_sha256"]
            assert body[plan["profiles"][name]["output_limit_parameter"]] == 4096
            if name == "qwen":
                assert body["enable_thinking"] is False
            elif name == "grok":
                assert body["reasoning_effort"] == "none"
            else:
                assert body["thinking"]["type"] == "disabled"


def test_ledger_unique_attempts_fixed_denominators_and_failures(run):
    _, plans, auths, report, _ = run
    total = 0
    for name, plan in plans.items():
        out = output(plan)
        starts, finishes, head = m._load_ledger(out / "calls_ledger.jsonl", plan)
        m._verify_saved_calls(out, plan, auths[name], starts, finishes)
        assert set(starts) == set(finishes), "Uncertain calls must remain explicitly unresolved"
        saved = m.read_json(out / "manifest.json")
        assert saved["ledger_head_sha256"] == head
        assert saved["llm_calls"] == len(starts) == report["providers"][name]["attempted"]
        rows = m.read_json(out / "predictions.json")["records"]
        assert [r["sample_id"] for r in rows] == [r["sample_id"] for r in plan["requests"]]
        assert len(rows) == report["providers"][name]["denominator"] == 150
        assert m.digest((out / "predictions.json").read_bytes()) == saved["predictions_sha256"]
        assert saved["valid_predictions"] == sum(r["request_status"] == "ok" for r in rows)
        assert sum(r["request_status"] != "not_attempted" for r in rows) == len(starts)
        total += len(starts)
    assert total == report["actual_calls"]


def test_verified_nonthinking_or_explicitly_retained_stop(run):
    _, plans, _, report, _ = run
    for name, plan in plans.items():
        out = output(plan)
        _, finishes, _ = m._load_ledger(out / "calls_ledger.jsonl", plan)
        for finish in finishes.values():
            response = m.read_json(out / finish["response_path"])
            if finish["needs_attention"]:
                assert response["error"] and report["providers"][name]["metrics"] is None
            else:
                assert response["nonthinking_check"]["status"] == "no_reported_reasoning"
                assert response["nonthinking_check"]["reported_reasoning_tokens"] in (None, 0)


def test_shared_pooled_evaluation_and_historical_fixed_table(run):
    value, plans, _, report, _ = run
    assert report["primary_metric"] == value["primary_metric"] == "coarse_five_field_micro.f1"
    # The execution summary exists only after all provider threads have returned.
    assert (batch.batch_dir() / "execution_summary.json").is_file()
    gold = m.read_json(m.ROOT / batch.GOLD)
    for name, plan in plans.items():
        result = report["providers"][name]
        if result["status"] != "succeeded":
            assert result["metrics"] is None
            continue
        assert result["attempted"] == 150
        rows = m.read_json(output(plan) / "predictions.json")["records"]
        evaluation = evaluate_coarse(gold, attempt_rows(rows), method_id="multi_model_" + name)
        assert result["metrics"]["overall"] == evaluation["coarse_five_field_micro"]
        assert result["metrics"]["per_field"] == evaluation["five_fields"]
        assert result["metrics"]["modality_macro_f1"] == evaluation["modality_labels"]["macro_f1"]
        assert result["metrics"]["failed_count"] == evaluation["failed_count"]
        assert set(result["metrics"]["per_field"]) == {"actor", "action", "condition", "constraint", "exception"}
    fixed = m.read_json(m.ROOT / "outputs/reports/stage2_table1_paper_final_v1.json")
    for name, arm in (("deepseek_historical", "direct_llm"), ("sun_historical", "sun_rule_only")):
        if name in report["historical_baselines"]:
            assert report["historical_baselines"][name]["f1"] == fixed["arms"][arm]["overall_pooled_five_span_fields"]["f1"]


def test_conservative_cost_and_token_accounting_match_saved_usage(run):
    _, plans, auths, report, _ = run
    for name, plan in plans.items():
        out = output(plan)
        _, finishes, _ = m._load_ledger(out / "calls_ledger.jsonl", plan)
        result, budget = report["providers"][name], auths[name]["budgets"][name]
        assert result["account_deduction_verified"] is False
        assert result["cost_currency"] == budget["currency"]
        cost = sum(f["reserved_cost"] for f in finishes.values())
        assert math.isclose(cost, result["conservative_uncached_cost"], rel_tol=0, abs_tol=1e-12)
        assert cost <= budget["max_cost"]
        usages = [m.read_json(out / f["response_path"])["usage"] for f in finishes.values()]
        assert sum(u.get("prompt_tokens", 0) for u in usages) == result["input_tokens"]
        assert sum(u.get("completion_tokens", 0) for u in usages) == result["output_tokens"]


def test_local_evidence_capsule_is_byte_identical_and_not_published(run):
    _, _, _, report, manifest = run
    capsule = m.ROOT / "outputs/evidence/stage2_multi_model_sensitivity_v1" / batch.RUN_ID
    index = m.read_json(capsule / "index.json")
    assert index["actual_calls"] == report["actual_calls"]
    assert index["github_raw_artifact_export_authorized"] is False
    assert set(manifest["artifacts"]).issubset(index["copies"])
    for original, record in index["copies"].items():
        assert m.digest((m.ROOT / original).read_bytes()) == record["sha256"]
        assert m.digest((m.ROOT / record["copy"]).read_bytes()) == record["sha256"]
