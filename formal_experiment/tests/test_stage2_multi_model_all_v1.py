"""Full six-provider orchestration: mock-only calls, frozen denominators and gates."""
import json
import shutil
import threading

import pytest

from test_multi_model_stage2 import capsule, no_live_access, fake_keys, response_for
from bpc_hybrid import multi_model_stage2 as m
import run_stage2_multi_model_all_v1 as batch


@pytest.fixture
def prepared(capsule):
    # Copy only the versioned code/Gold/baseline bindings; no credentials or old raw responses.
    for relative in [batch.AUTH, "scripts/run_stage2_multi_model_all_v1.py", batch.GOLD,
                     *batch.BASELINES.values(), "outputs/reports/stage2_table1_paper_final_v1.json",
                     "src/bpc_hybrid/sep_c3_modular_evaluation.py",
                     "src/bpc_hybrid/formal_stage2_evaluation.py", "src/bpc_hybrid/g04_coarse_view.py",
                     "src/bpc_hybrid/stage2_sun_literal_overlap.py"]:
        target = capsule / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(m.ROOT / relative, target)
    batch.prepare(capsule)
    return capsule


def test_full_preflight_freezes_900_same_input_calls_without_network(prepared):
    value, plans, auths = batch.saved_plans(prepared)
    assert value["planned_calls"] == sum(p["planned_calls"] for p in plans.values()) == 900
    assert all(p["thinking_requirement"] == "disabled" and p["retry"] == 0 for p in plans.values())
    ids = [[r["sample_id"] for r in p["requests"]] for p in plans.values()]
    assert all(i == ids[0] and len(i) == len(set(i)) == 150 for i in ids)
    assert value["primary_metric"] == "coarse_five_field_micro.f1"
    batch.verify_batch(value, plans, auths, root=prepared)
    with pytest.raises(m.ModelRunError, match="不覆盖"):
        batch.prepare(prepared)


@pytest.mark.parametrize("change", ["flag", "authorization", "gold_binding", "provider_plan"])
def test_full_batch_gates_precede_any_credential_loading_or_http(prepared, change):
    allow = True
    if change == "flag":
        allow = False
    elif change == "authorization":
        path = prepared / batch.AUTH
        value = m.read_json(path)
        value["max_calls"] = 901
        m.write_json(path, value)
    elif change == "gold_binding":
        with (prepared / batch.GOLD).open("a", encoding="utf-8") as file:
            file.write("\n")
    else:
        path = batch.batch_dir(prepared) / "qwen/plan.json"
        value = m.read_json(path)
        value["requests"][0]["body"]["enable_thinking"] = True
        m.write_json(path, value)
    with pytest.raises(m.ModelRunError):
        batch.execute(root=prepared, allow_llm=allow,
                      sender=lambda *a: pytest.fail("HTTP before gate"),
                      credential_loader=lambda *a: pytest.fail("keys before gate"))


def test_900_mock_calls_keep_full_failures_and_completed_resume_sends_zero(prepared, monkeypatch):
    value, plans, _ = batch.saved_plans(prepared)
    by_hash = {r["body_sha256"]: (r, p["profiles"][name])
               for name, p in plans.items() for r in p["requests"]}
    sent, loaded, lock = set(), [], threading.Lock()
    def keys(profiles, root):
        loaded.append(set(profiles))
        return fake_keys(profiles, root)
    def sender(profile, body, key, timeout):
        request, registered = by_hash[m.digest(body)]
        with lock:
            assert request["request_id"] not in sent
            sent.add(request["request_id"])
        assert profile == registered and key == "fake-secret-" + request["provider"]
        raw = json.loads(response_for(request, profile))
        # One completed but structurally invalid output per provider must stay in the 150 denominator.
        if request["sample_id"] == plans[request["provider"]]["requests"][0]["sample_id"]:
            raw["choices"][0]["message"]["content"] = "invalid-json"
        return m.encode(raw)
    original = m.read_json
    def guard_gold(path):
        if path == prepared / batch.GOLD:
            assert len(sent) == 900
            for plan in plans.values():
                assert (prepared / "outputs/development/stage2_multi_model_v1" / plan["run_id"] / "predictions.json").exists()
        return original(path)
    monkeypatch.setattr(m, "read_json", guard_gold)
    report = batch.execute(root=prepared, allow_llm=True, sender=sender, credential_loader=keys)
    assert len(sent) == report["actual_calls"] == 900 and report["status"] == "succeeded"
    assert loaded == [set(batch.PROVIDERS)]
    for result in report["providers"].values():
        assert result["attempted"] == result["denominator"] == 150
        assert result["valid_predictions"] == 149 and result["metrics"]["failed_count"] == 1
        assert result["metrics"]["overall"]["f1"] == 0  # Mock empty clauses, not model performance.
    manifest = original(batch.batch_dir(prepared) / "manifest.json")
    assert all(m.digest((prepared / path).read_bytes()) == digest for path, digest in manifest["artifacts"].items())
    # All completed runs must resume without any key reads or duplicate sends.
    resumed = batch.execute(root=prepared, allow_llm=True, resume=True,
                            sender=lambda *a: pytest.fail("duplicate HTTP"),
                            credential_loader=lambda *a: pytest.fail("completed batch reads keys"))
    assert resumed["actual_calls"] == 900


def test_one_provider_thinking_response_stops_only_that_provider(prepared):
    _, plans, _ = batch.saved_plans(prepared)
    by_hash = {r["body_sha256"]: r for plan in plans.values() for r in plan["requests"]}
    def sender(profile, body, key, timeout):
        request = by_hash[m.digest(body)]
        raw = json.loads(response_for(request, profile))
        if request["provider"] == "qwen":
            raw["choices"][0]["message"]["reasoning_content"] = "unexpected thought"
        return m.encode(raw)
    report = batch.execute(root=prepared, allow_llm=True, sender=sender, credential_loader=fake_keys)
    assert report["status"] == "partial" and report["actual_calls"] == 751
    assert report["providers"]["qwen"]["attempted"] == 1
    assert report["providers"]["qwen"]["metrics"] is None
    assert all(report["providers"][p]["attempted"] == 150 for p in batch.PROVIDERS if p != "qwen")
