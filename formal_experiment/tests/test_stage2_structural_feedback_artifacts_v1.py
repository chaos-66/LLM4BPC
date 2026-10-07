"""Persisted four-call feedback evidence, shared metrics and original result preservation."""
import math
import pytest
from bpc_hybrid import multi_model_stage2 as m
from bpc_hybrid.sep_c3_modular_evaluation import attempt_rows, evaluate_coarse
import run_stage2_structural_feedback_v1 as run
from test_multi_model_stage2 import no_live_access


@pytest.fixture(scope="module")
def evidence():
    value = m.read_json(run.out_dir() / "plan.json")
    report = m.read_json(run.report_path())
    manifest = m.read_json(run.out_dir() / "manifest.json")
    starts, finishes, head = m._load_ledger(run.out_dir() / "calls_ledger.jsonl", value["request_plan"])
    m._verify_saved_calls(run.out_dir(), value["request_plan"], run.ledger_auth(value), starts, finishes)
    return value, report, manifest, starts, finishes, head


def test_bound_parent_918_original_900_and_new_manifest_artifacts(evidence):
    value, report, manifest, starts, finishes, head = evidence
    run.verify(value, m.ROOT)
    assert len(starts) == len(finishes) == manifest["new_calls"] == report["actual_new_calls_in_run"] == 4
    assert manifest["combined_calls"] == report["actual_calls"] == 922
    assert manifest["source_bindings"] == value["source_bindings"]
    assert manifest["status"] == report["status"] == "succeeded"
    for relative, sha in manifest["artifacts"].items():
        assert m.digest((m.ROOT / relative).read_bytes()) == sha
    assert not (run.out_dir() / ".run.lock").exists()
    assert m.read_json(run.parent.report_path())["actual_calls"] == 918
    assert m.read_json(run.parent.final.report_path())["actual_calls"] == 900


def test_four_unique_frozen_wires_reasoning_policy_and_kimi_pacing(evidence):
    value, report, manifest, starts, finishes, head = evidence
    assert set(starts) == set(finishes) and len(starts) == 4
    kimi = [run.datetime.fromisoformat(s["timestamp_utc"]).timestamp() for s in starts.values() if s["provider"] == "kimi"]
    assert len(kimi) == 2 and kimi[1]-kimi[0] >= 21
    for request in value["request_plan"]["requests"]:
        finish = finishes[request["request_id"]]
        assert not finish["needs_attention"]
        response = m.read_json(run.out_dir() / finish["response_path"])
        decoded, check, prediction, audit = run.parent.parse_response(request, value["request_plan"]["profiles"][request["provider"]],
                response["raw_response_utf8"].encode("utf-8"), value["authorization"])
        assert response["prediction"] == prediction and response["nonthinking_check"] == check
        assert response["echo_recovery_audit"] == audit and not decoded["reasoning_present"]
        assert check["reported_reasoning_tokens"] in ((None, 0, 1) if request["provider"] == "kimi" else (None, 0))
        if check["reported_reasoning_tokens"] == 1:
            assert check["counter_exception_user_authorized"] and not check["one_token_meaning_verified"]
    assert report["retry"] == 0 and value["authorization"]["decision"] == run.DECISION


def test_existing_896_successes_and_untargeted_providers_unchanged(evidence):
    value, report, manifest, starts, finishes, head = evidence
    untouched = 0
    for name in run.parent.COUNTS:
        old = m.read_json(run.parent.out_dir() / name / "combined_predictions.json")["records"]
        rows = m.read_json(run.out_dir() / name / "combined_predictions.json")["records"]
        assert len(rows) == 150 and [r["sample_id"] for r in rows] == [r["sample_id"] for r in old]
        current = {r["sample_id"]: r for r in rows}
        for row in old:
            if row["request_status"] == "ok":
                assert current[row["sample_id"]] == row
                untouched += 1
        if name not in ("kimi", "glm", "minimax"):
            assert rows == old and report["providers"][name]["structural_feedback_calls"] == 0
    assert untouched == 896


def test_shared_full_150_pooled_metrics_actual_validity_and_fixed_table(evidence):
    value, report, manifest, starts, finishes, head = evidence
    gold = m.read_json(m.ROOT / run.parent.initial.GOLD)
    remaining = []
    for name in run.parent.COUNTS:
        rows = m.read_json(run.out_dir() / name / "combined_predictions.json")["records"]
        evaluation = evaluate_coarse(gold, attempt_rows(rows), method_id="multi_model_" + name)
        row = report["providers"][name]
        assert row["metrics"]["overall"] == evaluation["coarse_five_field_micro"]
        assert row["metrics"]["per_field"] == evaluation["five_fields"]
        assert row["metrics"]["modality_macro_f1"] == evaluation["modality_labels"]["macro_f1"]
        assert row["metrics"]["failed_count"] == evaluation["failed_count"] == 150-row["valid_predictions"]
        remaining += [{"provider": name, "sample_id": r["sample_id"], "failure_stage": r.get("failure_stage")}
                      for r in rows if r["request_status"] != "ok"]
    assert report["remaining_failures"] == remaining
    assert report["all_150_valid"] == manifest["all_150_valid"] == (len(remaining) == 0)
    assert report["primary_metric"] == "coarse_five_field_micro.f1"
    previous = m.read_json(run.parent.report_path())
    assert report["historical_baselines"] == previous["historical_baselines"]
    fixed = m.read_json(m.ROOT / "outputs/reports/stage2_table1_paper_final_v1.json")
    for name, arm in (("deepseek_historical", "direct_llm"), ("sun_historical", "sun_rule_only")):
        assert report["historical_baselines"][name]["f1"] == fixed["arms"][arm]["overall_pooled_five_span_fields"]["f1"]


def test_usage_cost_cap_and_all_capsule_bytes(evidence):
    value, report, manifest, starts, finishes, head = evidence
    amount = sum(f["reserved_cost"] for f in finishes.values())
    assert math.isclose(report["additional_costs"]["CNY"], amount, rel_tol=0, abs_tol=1e-12) and amount <= .99
    previous = m.read_json(run.parent.report_path())
    assert math.isclose(report["combined_supplementary_costs"]["CNY"], amount+previous["additional_costs"]["CNY"], abs_tol=1e-12)
    assert report["combined_supplementary_costs"]["USD"] == previous["additional_costs"]["USD"]
    for name in run.parent.COUNTS:
        row = report["providers"][name]
        chosen = [f for f in finishes.values() if f["provider"] == name]
        usages = [m.read_json(run.out_dir() / f["response_path"])["usage"] for f in chosen]
        assert row["attempted"] == previous["providers"][name]["attempted"] + len(chosen)
        assert math.isclose(row["conservative_uncached_cost"], previous["providers"][name]["conservative_uncached_cost"]+sum(f["reserved_cost"] for f in chosen), abs_tol=1e-12)
        for field, token in (("input_tokens", "prompt_tokens"), ("output_tokens", "completion_tokens")):
            assert row[field] == previous["providers"][name][field] + sum(u.get(token, 0) for u in usages)
        assert not row["account_deduction_verified"]
    capsule = m.ROOT / "outputs/evidence/stage2_multi_model_remaining_v1" / run.RUN_ID
    index = m.read_json(capsule / "index.json")
    assert index["actual_calls"] == 922 and index["actual_new_calls"] == 4
    assert set(manifest["artifacts"]).issubset(index["copies"])
    assert not index["published"] and not index["github_raw_artifact_export_authorized"]
    for relative, item in index["copies"].items():
        assert ".env" not in relative and "data/gold/" not in relative
        assert m.digest((m.ROOT / relative).read_bytes()) == item["sha256"]
        assert m.digest((m.ROOT / item["copy"]).read_bytes()) == item["sha256"]
