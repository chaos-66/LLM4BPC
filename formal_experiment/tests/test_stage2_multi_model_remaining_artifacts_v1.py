"""Verify only this persisted continuation, offline and without loading keys."""
import math

import pytest

from bpc_hybrid import multi_model_stage2 as m
from bpc_hybrid.h1_transport import decode_chat_completion_envelope
from bpc_hybrid.sep_c3_modular_evaluation import attempt_rows, evaluate_coarse
import run_stage2_multi_model_remaining_v1 as run
from test_multi_model_stage2 import no_live_access


@pytest.fixture(scope="module")
def evidence():
    plan = m.read_json(run.out_dir() / "plan.json")
    report = m.read_json(run.report_path())
    manifest = m.read_json(run.out_dir() / "manifest.json")
    _, originals, auths, _, _ = run.parent_state(m.ROOT)
    return plan, report, manifest, originals, auths


def saved(name, plan):
    bundle = plan["selected"][name]
    auth = {"authorized": True, "plan_sha256": m.digest(m.encode(bundle["plan"])),
            "budgets": {name: bundle["budget"]}, "continuation_authorization": plan["authorization"]}
    out = run.provider_dir(name)
    starts, finishes, head = m._load_ledger(out / "calls_ledger.jsonl", bundle["plan"])
    m._verify_saved_calls(out, bundle["plan"], auth, starts, finishes)
    return bundle, starts, finishes, head


def test_bound_sources_requests_and_original_artifacts_unchanged(evidence):
    plan, report, manifest, originals, _ = evidence
    run.verify(plan, m.ROOT)
    assert manifest["source_bindings"] == plan["source_bindings"]
    assert manifest["new_calls"] == report["actual_new_calls"]
    assert manifest["combined_calls"] == report["actual_calls"]
    assert manifest["status"] == report["status"]
    for relative, sha in manifest["artifacts"].items():
        assert m.digest((m.ROOT / relative).read_bytes()) == sha, relative
    for name, bundle in plan["selected"].items():
        assert bundle["plan"]["requests"] == originals[name]["requests"][1:]
        assert len(bundle["plan"]["requests"]) == 149
        for request in bundle["plan"]["requests"]:
            assert request["body"]["thinking"] == {"type": "disabled"}
            assert m.digest(m.encode(request["body"])) == request["body_sha256"]
            assert request["body"][bundle["plan"]["profiles"][name]["output_limit_parameter"]] == 4096


def test_302_unique_new_attempts_combined_755_and_retained_first_rows(evidence):
    plan, report, _, originals, _ = evidence
    assert report["status"] == "partial"
    assert report["retry"] == plan["retry"] == 0
    assert report["actual_new_calls"] == 302 and report["actual_calls"] == 755
    total, ids = 0, set()
    for name in run.PROVIDERS:
        bundle, starts, finishes, head = saved(name, plan)
        expected_calls = 4 if name == "kimi" else 149
        assert len(starts) == len(finishes) == expected_calls and set(starts) == set(finishes)
        assert sum(f["needs_attention"] for f in finishes.values()) == (1 if name == "kimi" else 0)
        assert not (ids & set(starts))
        ids.update(starts)
        assert not (set(starts) & set(plan["parent_states"][name]["started_ids"]))
        manifest = m.read_json(run.provider_dir(name) / "manifest.json")
        assert manifest["ledger_head_sha256"] == head and manifest["llm_calls"] == expected_calls
        assert manifest["status"] == ("partial" if name == "kimi" else "succeeded")
        rows = m.read_json(run.provider_dir(name) / "combined_predictions.json")["records"]
        assert len(rows) == 150 and [r["sample_id"] for r in rows] == [r["sample_id"] for r in originals[name]["requests"]]
        assert sum(r["request_status"] == "not_attempted" for r in rows) == (145 if name == "kimi" else 0)
        assert report["providers"][name]["valid_predictions"] == sum(r["request_status"] == "ok" for r in rows)
        if name == "kimi":
            assert rows[0] == plan["kimi_first_offline_recovery"]["prediction"] and rows[0]["request_status"] == "ok"
        else:
            first = m.read_json(run.original_dir(originals[name], m.ROOT) / "predictions.json")["records"][0]
            assert rows[0] == first and rows[0]["request_status"] == "failed"
        total += len(starts)
    assert total == 302
    old = m.read_json(run.parent.report_path())
    for name in ("qwen", "grok", "minimax"):
        assert report["providers"][name] == old["providers"][name]


def test_nonthinking_evidence_and_actual_kimi_counter_retained(evidence):
    plan, _, _, originals, _ = evidence
    assert plan["authorization"]["kimi_counter_policy_authorization"] == "接受，保留计数差异并继续 Kimi"
    recovery = plan["kimi_first_offline_recovery"]
    assert recovery["additional_api_calls"] == 0
    assert recovery["usage"]["reasoning_tokens"] == recovery["nonthinking_check"]["reported_reasoning_tokens"] == 1
    assert recovery["nonthinking_check"]["one_token_meaning_verified"] is False
    for name in run.PROVIDERS:
        bundle, _, finishes, _ = saved(name, plan)
        requests = {r["request_id"]: r for r in bundle["plan"]["requests"]}
        for rid, finish in finishes.items():
            response = m.read_json(run.provider_dir(name) / finish["response_path"])
            if finish["needs_attention"]:
                assert name == "kimi" and "max RPM: 3" in response["error"]
                assert response["error"].startswith("HTTP 429:") and not response["raw_response_utf8"]
                continue
            decoded = decode_chat_completion_envelope(response["raw_response_utf8"].encode("utf-8"))
            expected = run.check_nonthinking(name, requests[rid], decoded, plan["authorization"])
            assert response["nonthinking_check"] == expected
            assert response["usage"].get("reasoning_tokens") == expected["reported_reasoning_tokens"]
            assert not decoded["reasoning_present"] and not decoded["content"].lstrip().startswith("<think>")
            assert expected["reported_reasoning_tokens"] in ((None, 0, 1) if name == "kimi" else (None, 0))
            if expected["reported_reasoning_tokens"] == 1:
                assert expected["counter_exception_user_authorized"] and not expected["one_token_meaning_verified"]
    old = m.read_json(run.original_dir(originals["kimi"], m.ROOT) / "responses/kimi_estg_000002.json")
    assert old["error"] and old["prediction"]["request_status"] == "failed"


def test_shared_pooled_evaluation_failed_denominator_and_fixed_table(evidence):
    plan, report, _, originals, _ = evidence
    assert plan["primary_metric"] == report["primary_metric"] == "coarse_five_field_micro.f1"
    assert (run.out_dir() / "execution_summary.json").is_file()
    gold = m.read_json(m.ROOT / run.parent.GOLD)
    for name, result in report["providers"].items():
        if name == "kimi":
            assert result["attempted"] == 5 and result["valid_predictions"] == 4 and result["metrics"] is None
            continue
        assert result["attempted"] == result["denominator"] == 150
        path = run.provider_dir(name) / "combined_predictions.json" if name in run.PROVIDERS else run.original_dir(originals[name], m.ROOT) / "predictions.json"
        rows = m.read_json(path)["records"]
        evaluation = evaluate_coarse(gold, attempt_rows(rows), method_id="multi_model_" + name)
        assert result["metrics"]["overall"] == evaluation["coarse_five_field_micro"]
        assert result["metrics"]["per_field"] == evaluation["five_fields"]
        assert result["metrics"]["modality_macro_f1"] == evaluation["modality_labels"]["macro_f1"]
        assert result["metrics"]["failed_count"] == evaluation["failed_count"] == 150 - result["valid_predictions"]
    fixed = m.read_json(m.ROOT / "outputs/reports/stage2_table1_paper_final_v1.json")
    for name, arm in (("deepseek_historical", "direct_llm"), ("sun_historical", "sun_rule_only")):
        assert report["historical_baselines"][name]["f1"] == fixed["arms"][arm]["overall_pooled_five_span_fields"]["f1"]


def test_usage_costs_with_parent_reservations_and_original_caps(evidence):
    plan, report, _, originals, auths = evidence
    for name in run.PROVIDERS:
        bundle, _, finishes, _ = saved(name, plan)
        old_starts, old_finishes, _ = m._load_ledger(run.original_dir(originals[name], m.ROOT) / "calls_ledger.jsonl", originals[name])
        assert len(old_starts) == len(old_finishes) == 1
        row = report["providers"][name]
        usages = [m.read_json(run.provider_dir(name) / f["response_path"])["usage"] for f in finishes.values()]
        usages += [m.read_json(run.original_dir(originals[name], m.ROOT) / f["response_path"])["usage"] for f in old_finishes.values()]
        assert sum(u.get("prompt_tokens", 0) for u in usages) == row["input_tokens"]
        assert sum(u.get("completion_tokens", 0) for u in usages) == row["output_tokens"]
        cost = bundle["parent_reserved_cost"] + sum(f["reserved_cost"] for f in finishes.values())
        assert math.isclose(cost, row["conservative_uncached_cost"], abs_tol=1e-12, rel_tol=0)
        assert cost <= auths[name]["budgets"][name]["max_cost"]
        assert row["cost_currency"] == bundle["budget"]["currency"] and not row["account_deduction_verified"]
        assert math.isclose(bundle["budget"]["max_cost"] + bundle["parent_reserved_cost"], auths[name]["budgets"][name]["max_cost"], abs_tol=1e-12, rel_tol=0)


def test_new_and_parent_capsules_byte_identical_without_gold_or_credentials(evidence):
    _, report, manifest, _, _ = evidence
    paths = [("stage2_multi_model_remaining_v1", run.RUN_ID, manifest),
             ("stage2_multi_model_sensitivity_v1", run.parent.RUN_ID,
              m.read_json(run.parent.batch_dir() / "manifest.json"))]
    for group, run_id, current_manifest in paths:
        capsule = m.ROOT / "outputs/evidence" / group / run_id
        index = m.read_json(capsule / "index.json")
        assert index["github_raw_artifact_export_authorized"] is False
        assert set(current_manifest["artifacts"]).issubset(index["copies"])
        for relative, item in index["copies"].items():
            assert ".env" not in relative and "data/gold/" not in relative
            assert m.digest((m.ROOT / relative).read_bytes()) == item["sha256"]
            assert m.digest((m.ROOT / item["copy"]).read_bytes()) == item["sha256"]
        if run_id == run.RUN_ID:
            assert index["actual_calls"] == report["actual_calls"] == 755
            assert index["actual_new_calls"] == 302
