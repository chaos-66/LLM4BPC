"""Mock-only never-sent continuation, preserving the versioned 453-call parent."""
import copy
import json
from pathlib import Path
import shutil
import threading

import pytest

from bpc_hybrid import multi_model_stage2 as m
from bpc_hybrid import prompt_loader
import run_stage2_multi_model_all_v1 as parent
import run_stage2_multi_model_remaining_v1 as remaining
from test_multi_model_stage2 import no_live_access, fake_keys, response_for


@pytest.fixture(scope="module")
def frozen_parent(tmp_path_factory):
    root = tmp_path_factory.mktemp("parent")
    capsule = m.ROOT / "outputs/evidence/stage2_multi_model_sensitivity_v1" / parent.RUN_ID
    index = m.read_json(capsule / "index.json")
    for original, record in index["copies"].items():
        source, target = m.ROOT / record["copy"], root / original
        assert m.digest(source.read_bytes()) == record["sha256"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    value, plans, _ = parent.saved_plans(root)
    files = dict(value["source_bindings"])
    for plan in plans.values():
        files.update(plan["bindings"])
    for relative, sha in files.items():
        source, target = m.ROOT / relative, root / relative
        assert m.digest(source.read_bytes()) == sha
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for relative in (remaining.AUTH, "scripts/run_stage2_multi_model_remaining_v1.py"):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(m.ROOT / relative, target)
    return root


@pytest.fixture
def prepared(frozen_parent, tmp_path, monkeypatch):
    shutil.copytree(frozen_parent, tmp_path, dirs_exist_ok=True)
    monkeypatch.setattr(prompt_loader, "PROMPTS_DIR", tmp_path / "prompts/sun_compat")
    remaining.prepare(tmp_path)
    return tmp_path


def test_447_plan_freezes_only_never_attempted_same_wire_bodies(prepared):
    plan = m.read_json(remaining.out_dir(prepared) / "plan.json")
    remaining.verify(plan, prepared)
    _, original, _, _, _ = remaining.parent_state(prepared)
    assert plan["planned_new_calls"] == sum(len(b["plan"]["requests"]) for b in plan["selected"].values()) == 447
    for name, bundle in plan["selected"].items():
        assert bundle["plan"]["requests"] == original[name]["requests"][1:]
        assert bundle["budget"]["max_cost"] + bundle["parent_reserved_cost"] == pytest.approx(
            parent.saved_plans(prepared)[2][name]["budgets"][name]["max_cost"])
    recovery = plan["kimi_first_offline_recovery"]
    assert recovery["additional_api_calls"] == 0 and recovery["prediction"]["request_status"] == "ok"
    assert recovery["nonthinking_check"]["reported_reasoning_tokens"] == 1
    assert recovery["nonthinking_check"]["one_token_meaning_verified"] is False
    with pytest.raises(m.ModelRunError, match="不覆盖"):
        remaining.prepare(prepared)


@pytest.mark.parametrize("change", ["flag", "authorization", "plan", "parent_response"])
def test_tamper_or_missing_execute_flag_rejected_before_keys_and_http(prepared, change):
    if change == "authorization":
        path = prepared / remaining.AUTH
        value = m.read_json(path)
        value["max_new_calls"] = 448
        m.write_json(path, value)
    elif change == "plan":
        path = remaining.out_dir(prepared) / "plan.json"
        value = m.read_json(path)
        value["selected"]["glm"]["plan"]["requests"][0]["body"]["thinking"]["type"] = "enabled"
        m.write_json(path, value)
    elif change == "parent_response":
        path = prepared / "outputs/development/stage2_multi_model_v1" / (parent.RUN_ID + "_mimo") / "responses/mimo_estg_000002.json"
        with path.open("a", encoding="utf-8") as handle:
            handle.write("\n")
    with pytest.raises(m.ModelRunError):
        remaining.execute(prepared, allow_llm=change != "flag",
            sender=lambda *a: pytest.fail("HTTP before gate"),
            credential_loader=lambda *a: pytest.fail("Keys before gate"))


@pytest.mark.parametrize("provider,count,reasoning,prefix,accepted", [
    ("kimi", 1, False, "{}", True), ("kimi", 2, False, "{}", False),
    ("kimi", 1, True, "{}", False), ("kimi", 1, False, "<think>thought", False),
    ("glm", 1, False, "{}", False), ("kimi", 0, False, "{}", True)])
def test_counter_exception_is_kimi_only_empty_reasoning_and_retains_one(provider, count, reasoning, prefix, accepted):
    auth = m.read_json(m.ROOT / remaining.AUTH)
    request = {"provider": provider, "body": {"model": "kimi-k2.6", "thinking": {"type": "disabled"}}}
    decoded = {"usage": {"reasoning_tokens": count}, "reasoning_present": reasoning, "content": prefix}
    if accepted:
        result = remaining.check_nonthinking(provider, request, decoded, auth)
        assert result["reported_reasoning_tokens"] == count
    else:
        with pytest.raises(m.ModelRunError):
            remaining.check_nonthinking(provider, request, decoded, auth)


def test_full_447_mock_keep_parent_immutable_merge_150_and_completed_resume_zero(prepared, monkeypatch):
    plan = m.read_json(remaining.out_dir(prepared) / "plan.json")
    original_manifest = m.read_json(parent.batch_dir(prepared) / "manifest.json")
    by_hash = {r["body_sha256"]: r for b in plan["selected"].values() for r in b["plan"]["requests"]}
    sent, loaded, lock = set(), [], threading.Lock()
    def keys(profiles, root):
        loaded.append(set(profiles))
        return fake_keys(profiles, root)
    def sender(profile, body, key, timeout):
        request = by_hash[m.digest(body)]
        with lock:
            assert request["request_id"] not in sent
            assert request["request_id"] not in plan["parent_states"][request["provider"]]["started_ids"]
            sent.add(request["request_id"])
        raw = json.loads(response_for(request, profile))
        if request["provider"] == "kimi":
            raw["usage"]["completion_tokens_details"] = {"reasoning_tokens": 1}
        if request["sample_id"] == plan["selected"][request["provider"]]["plan"]["requests"][0]["sample_id"]:
            raw["choices"][0]["message"]["content"] = "invalid-json"
        return m.encode(raw)
    original_read = m.read_json
    def guard_gold(path):
        if path == prepared / parent.GOLD:
            assert len(sent) == 447
            assert all((remaining.provider_dir(p, prepared) / "combined_predictions.json").is_file() for p in remaining.PROVIDERS)
        return original_read(path)
    monkeypatch.setattr(m, "read_json", guard_gold)
    report = remaining.execute(prepared, allow_llm=True, sender=sender, credential_loader=keys)
    assert report["status"] == "succeeded" and report["actual_new_calls"] == len(sent) == 447
    assert report["actual_calls"] == 900 and loaded == [set(remaining.PROVIDERS)]
    for name in remaining.PROVIDERS:
        row = report["providers"][name]
        assert row["attempted"] == row["denominator"] == 150
        assert row["valid_predictions"] == (149 if name == "kimi" else 148)
        assert row["metrics"]["failed_count"] == (1 if name == "kimi" else 2)
    for relative, sha in original_manifest["artifacts"].items():
        assert m.digest((prepared / relative).read_bytes()) == sha
    resumed = remaining.execute(prepared, allow_llm=True, resume=True,
        sender=lambda *a: pytest.fail("Duplicate HTTP"), credential_loader=lambda *a: pytest.fail("Completed resume reads keys"))
    assert resumed["actual_calls"] == 900


def test_larger_kimi_reasoning_stops_only_kimi_no_retry(prepared):
    plan = m.read_json(remaining.out_dir(prepared) / "plan.json")
    requests = {r["body_sha256"]: r for b in plan["selected"].values() for r in b["plan"]["requests"]}
    def sender(profile, body, key, timeout):
        request = requests[m.digest(body)]
        raw = json.loads(response_for(request, profile))
        if request["provider"] == "kimi":
            raw["usage"]["completion_tokens_details"] = {"reasoning_tokens": 2}
        return m.encode(raw)
    report = remaining.execute(prepared, allow_llm=True, sender=sender, credential_loader=fake_keys)
    assert report["status"] == "partial" and report["actual_new_calls"] == 299
    assert report["providers"]["kimi"]["attempted"] == 2
    assert report["providers"]["kimi"]["metrics"] is None
    assert all(report["providers"][p]["attempted"] == 150 for p in ("glm", "mimo"))
