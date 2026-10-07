"""Focused RPM pacing, never-sent gate and zero-repeat checks; no live access."""
import json
import shutil

import pytest

from bpc_hybrid import multi_model_stage2 as m, prompt_loader
import run_stage2_kimi_rpm_remaining_v1 as run
from test_multi_model_stage2 import no_live_access
from test_stage2_multi_model_all_v1 import fake_keys, response_for
from test_stage2_multi_model_remaining_v1 import frozen_parent


@pytest.fixture
def prepared(tmp_path, frozen_parent, monkeypatch):
    shutil.copytree(frozen_parent, tmp_path, dirs_exist_ok=True)
    paths = [run.parent.out_dir() / "plan.json"]
    paths += list(run.parent.provider_dir("kimi").rglob("*.json*"))
    paths += [m.ROOT / run.AUTH, m.ROOT / "scripts/run_stage2_kimi_rpm_remaining_v1.py"]
    for source in paths:
        target = tmp_path / source.relative_to(m.ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    monkeypatch.setattr(prompt_loader, "PROMPTS_DIR", tmp_path / "prompts/sun_compat")
    run.prepare(tmp_path)
    return tmp_path


def test_only_145_never_sent_same_bytes_and_remaining_budget(prepared):
    value = m.read_json(run.out_dir(prepared) / "plan.json")
    batch, bundle, starts, finishes, _ = run.parent_state(prepared)
    assert len(value["request_plan"]["requests"]) == 145
    assert not (set(value["parent_started_ids"]) & {r["request_id"] for r in value["request_plan"]["requests"]})
    assert value["request_plan"]["requests"] == bundle["plan"]["requests"][4:]
    assert value["budget"]["max_cost"] + sum(f["reserved_cost"] for f in finishes.values()) == bundle["budget"]["max_cost"]
    assert value["authorization"]["retry"] == 0 and value["authorization"]["max_combined_calls"] == 900


@pytest.mark.parametrize("change", ["flag", "pacing", "parent_response"])
def test_gate_precedes_keys_and_http(prepared, change):
    if change == "pacing":
        path = prepared / run.AUTH
        value = m.read_json(path)
        value["min_start_interval_seconds"] = 1
        m.write_json(path, value)
    if change == "parent_response":
        path = run.parent.provider_dir("kimi", prepared) / "responses/kimi_estg_000021.json"
        path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(m.ModelRunError):
        run.execute(prepared, allow_llm=change != "flag", sender=lambda *a: pytest.fail("HTTP before gate"),
                    credential_loader=lambda *a: pytest.fail("Key read before gate"))


def test_pacing_145_unique_calls_parent_cooldown_and_completed_resume_no_access(prepared):
    value = m.read_json(run.out_dir(prepared) / "plan.json")
    requests = {r["body_sha256"]: r for r in value["request_plan"]["requests"]}
    ticks = [value["earliest_start_epoch"] - 65]
    sent, loaded, slept = [], [], []
    def clock():
        return ticks[0]
    def sleeper(seconds):
        assert 0 < seconds <= 21
        slept.append(seconds)
        ticks[0] += seconds
    def sender(profile, body, key, timeout):
        request = requests[m.digest(body)]
        assert request["request_id"] not in value["parent_started_ids"]
        sent.append((request["request_id"], clock()))
        raw = json.loads(response_for(request, profile))
        raw["usage"]["completion_tokens_details"] = {"reasoning_tokens": 1}
        return m.encode(raw)
    def keys(profiles, root):
        loaded.append(set(profiles))
        return fake_keys(profiles, root)
    result = run.execute(prepared, allow_llm=True, sender=sender, credential_loader=keys, clock=clock, sleeper=sleeper)
    assert result["status"] == "succeeded" and result["llm_calls"] == 145
    assert len(sent) == len({rid for rid, _ in sent}) == 145 and loaded == [{"kimi"}]
    assert sent[0][1] >= value["earliest_start_epoch"]
    assert all(b[1] - a[1] >= 21 for a, b in zip(sent, sent[1:]))
    rows = m.read_json(run.out_dir(prepared) / "predictions.json")["records"]
    assert all(r["request_status"] == "ok" for r in rows)
    resumed = run.execute(prepared, allow_llm=True, resume=True, sender=lambda *a: pytest.fail("Duplicate call"),
                         credential_loader=lambda *a: pytest.fail("Completed run reads keys"), clock=clock, sleeper=sleeper)
    assert resumed["llm_calls"] == 145


def test_repeated_rate_failure_stops_once_and_cannot_resume(prepared):
    value = m.read_json(run.out_dir(prepared) / "plan.json")
    sent = []
    def sender(*args):
        sent.append(True)
        raise m.ModelRunError('HTTP 429: {"type":"rate_limit_reached_error"}')
    result = run.execute(prepared, allow_llm=True, sender=sender, credential_loader=fake_keys,
                         clock=lambda: value["earliest_start_epoch"] + 100, sleeper=lambda s: pytest.fail("Unexpected sleep"))
    assert result["status"] == "partial" and result["llm_calls"] == len(sent) == 1
    with pytest.raises(m.ModelRunError):
        run.execute(prepared, allow_llm=True, resume=True, sender=lambda *a: pytest.fail("Retry"),
                    credential_loader=lambda *a: pytest.fail("Keys before rejected resume"))
