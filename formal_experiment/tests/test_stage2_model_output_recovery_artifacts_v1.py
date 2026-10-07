"""Verify persisted authorized recovery artifacts; never load keys or send HTTP."""
import math
import json

import pytest

from bpc_hybrid import multi_model_stage2 as m
from bpc_hybrid.sep_c3_modular_evaluation import attempt_rows, evaluate_coarse
import run_stage2_model_output_recovery_v1 as run
from test_multi_model_stage2 import no_live_access


@pytest.fixture(scope="module")
def evidence():
    value = m.read_json(run.out_dir() / "plan.json")
    report = m.read_json(run.report_path())
    manifest = m.read_json(run.out_dir() / "manifest.json")
    return value, report, manifest


def saved(name, value):
    directory = run.out_dir() / name
    bundle = value["selected"][name]
    starts, finishes, head = m._load_ledger(directory / "calls_ledger.jsonl", bundle["plan"])
    m._verify_saved_calls(directory, bundle["plan"], run.ledger_auth(value, name), starts, finishes)
    return directory, bundle, starts, finishes, head


def test_bound_sources_parent_900_and_all_artifacts_unchanged(evidence):
    value, report, manifest = evidence
    run.verify(value, m.ROOT)
    assert manifest["source_bindings"] == value["source_bindings"]
    assert manifest["new_calls"] == report["actual_new_calls_in_run"] == 18
    assert manifest["combined_calls"] == report["actual_calls"] == 918
    assert manifest["status"] == report["status"] == "succeeded"
    assert manifest["offline_recoveries"] == report["offline_recoveries"] == 15
    for relative, sha in manifest["artifacts"].items():
        assert m.digest((m.ROOT / relative).read_bytes()) == sha, relative
    assert not list(run.out_dir().rglob(".run.lock"))
    assert m.read_json(run.final.report_path())["actual_calls"] == 900


def test_18_unique_original_requests_21_second_kimi_and_nonthinking_evidence(evidence):
    value, report, _ = evidence
    identities = set()
    for name in run.COUNTS:
        directory, bundle, starts, finishes, head = saved(name, value)
        assert len(starts) == len(finishes) == run.COUNTS[name]
        assert set(starts) == set(finishes)
        assert not (identities & set(starts))
        identities.update(starts)
        if name == "kimi":
            ticks = [run.datetime.fromisoformat(s["timestamp_utc"]).timestamp() for s in starts.values()]
            assert all(b-a >= 21 for a, b in zip(ticks, ticks[1:]))
        for request in bundle["plan"]["requests"]:
            finish = finishes[request["request_id"]]
            assert not finish["needs_attention"]
            saved_response = m.read_json(directory / finish["response_path"])
            decoded, check, prediction, audit = run.parse_response(request, bundle["plan"]["profiles"][name],
                       saved_response["raw_response_utf8"].encode("utf-8"), value["authorization"])
            assert saved_response["prediction"] == prediction
            assert saved_response["nonthinking_check"] == check
            assert saved_response["echo_recovery_audit"] == audit
            assert not decoded["reasoning_present"]
            assert check["reported_reasoning_tokens"] in ((None, 0, 1) if name == "kimi" else (None, 0))
            if check["reported_reasoning_tokens"] == 1:
                assert check["counter_exception_user_authorized"] and not check["one_token_meaning_verified"]
    assert len(identities) == 18 and report["retry"] == 0


def test_offline_15_echo_only_and_unchanged_867_successful_baseline_rows(evidence):
    value, report, _ = evidence
    originals = run.initial.saved_plans(m.ROOT)[1]
    for recovery in value["offline_recoveries"]:
        name, sid = recovery["provider"], recovery["sample_id"]
        path = m.ROOT / recovery["source_response_path"]
        assert m.digest(path.read_bytes()) == recovery["source_response_sha256"]
        request = next(r for r in originals[name]["requests"] if r["sample_id"] == sid)
        response = m.read_json(path)
        decoded = run.middle.decode_chat_completion_envelope(response["raw_response_utf8"].encode("utf-8"))
        strict = m.canonical_prediction(request, decoded["content"])
        assert strict["request_status"] == "failed" and strict["failure_stage"] == "input_binding"
        prediction, audit = run.recover_echo(request, decoded["content"])
        assert prediction == recovery["prediction"] and prediction["request_status"] == "ok"
        assert audit["changed_fields"] == ["source_text"] and audit["extraction_fields_unchanged"] and not audit["gold_used"]
        assert run.presentation(audit["original_echo"]) == run.presentation(audit["restored_echo"])
        assert recovery["additional_api_calls"] == 0
    untouched = 0
    for name in run.COUNTS:
        old = m.read_json(m.ROOT / value["baseline_paths"][name])["records"]
        new = {r["sample_id"]: r for r in m.read_json(run.out_dir() / name / "combined_predictions.json")["records"]}
        for row in old:
            if row["request_status"] == "ok":
                assert new[row["sample_id"]] == row
                untouched += 1
    assert untouched == 867


def test_full_150_shared_pooled_metrics_remaining_failures_and_fixed_table(evidence):
    value, report, _ = evidence
    gold = m.read_json(m.ROOT / run.initial.GOLD)
    old_report = m.read_json(run.final.report_path())
    failed = []
    for name in run.COUNTS:
        rows = m.read_json(run.out_dir() / name / "combined_predictions.json")["records"]
        assert len(rows) == len({r["sample_id"] for r in rows}) == 150
        original_ids = [r["sample_id"] for r in m.read_json(m.ROOT / value["baseline_paths"][name])["records"]]
        assert [r["sample_id"] for r in rows] == original_ids
        evaluation = evaluate_coarse(gold, attempt_rows(rows), method_id="multi_model_" + name)
        row = report["providers"][name]
        assert row["metrics"]["overall"] == evaluation["coarse_five_field_micro"]
        assert row["metrics"]["per_field"] == evaluation["five_fields"]
        assert row["metrics"]["modality_macro_f1"] == evaluation["modality_labels"]["macro_f1"]
        assert row["metrics"]["failed_count"] == 150-row["valid_predictions"] == evaluation["failed_count"]
        assert row["first_pass_valid_predictions"] == old_report["providers"][name]["valid_predictions"]
        failed += [{"provider": name, "sample_id": r["sample_id"], "failure_stage": r.get("failure_stage")}
                   for r in rows if r["request_status"] != "ok"]
    assert report["remaining_failures"] == failed
    assert report["all_150_valid"] == (len(failed) == 0)
    assert report["primary_metric"] == "coarse_five_field_micro.f1"
    assert report["historical_baselines"] == old_report["historical_baselines"]
    fixed = m.read_json(m.ROOT / "outputs/reports/stage2_table1_paper_final_v1.json")
    for name, arm in (("deepseek_historical", "direct_llm"), ("sun_historical", "sun_rule_only")):
        assert report["historical_baselines"][name]["f1"] == fixed["arms"][arm]["overall_pooled_five_span_fields"]["f1"]


def test_new_costs_usage_currency_caps_and_byte_identical_capsule(evidence):
    value, report, manifest = evidence
    costs = {"CNY": 0.0, "USD": 0.0}
    old_report = m.read_json(run.final.report_path())
    for name in run.COUNTS:
        directory, bundle, starts, finishes, head = saved(name, value)
        amount = sum(f["reserved_cost"] for f in finishes.values())
        costs[bundle["budget"]["currency"]] += amount
        assert amount <= bundle["budget"]["max_cost"]
        row = report["providers"][name]
        assert row["attempted"] == 150 + run.COUNTS[name]
        assert math.isclose(row["conservative_uncached_cost"], old_report["providers"][name]["conservative_uncached_cost"] + amount, abs_tol=1e-12)
        usages = [m.read_json(directory / f["response_path"])["usage"] for f in finishes.values()]
        for field, token in (("input_tokens", "prompt_tokens"), ("output_tokens", "completion_tokens")):
            assert row[field] == old_report["providers"][name][field] + sum(u.get(token, 0) for u in usages)
        assert not row["account_deduction_verified"]
    assert all(math.isclose(report["additional_costs"][c], costs[c], rel_tol=0, abs_tol=1e-12) for c in costs)
    assert all(costs[c] <= value["authorization"]["currency_caps"][c] for c in costs)
    capsule = m.ROOT / "outputs/evidence/stage2_multi_model_remaining_v1" / run.RUN_ID
    index = m.read_json(capsule / "index.json")
    assert index["actual_calls"] == 918 and index["actual_new_calls"] == 18
    assert not index["published"] and not index["github_raw_artifact_export_authorized"]
    assert set(manifest["artifacts"]).issubset(index["copies"])
    for relative, item in index["copies"].items():
        assert ".env" not in relative and "data/gold/" not in relative
        assert m.digest((m.ROOT / relative).read_bytes()) == item["sha256"]
        assert m.digest((m.ROOT / item["copy"]).read_bytes()) == item["sha256"]
