"""Focused recovery policy, authorization gates, supplement ledger and shared evaluation."""
import copy
import json
import shutil

import pytest

from bpc_hybrid import multi_model_stage2 as m
import run_stage2_model_output_recovery_v1 as run
from test_multi_model_stage2 import no_live_access
from test_stage2_multi_model_all_v1 import fake_keys, response_for


@pytest.fixture(scope="module")
def bound():
    value = m.read_json(run.out_dir() / "plan.json")
    run.verify(value, m.ROOT)
    return value


def test_bound_15_offline_and_18_unchanged_requests_no_overlap(bound):
    assert len(bound["offline_recoveries"]) == 15
    assert all(r["additional_api_calls"] == 0 and r["prediction"]["request_status"] == "ok" for r in bound["offline_recoveries"])
    old = run.initial.saved_plans(m.ROOT)[1]
    offline = {(r["provider"], r["sample_id"]) for r in bound["offline_recoveries"]}
    new = set()
    for name, bundle in bound["selected"].items():
        assert len(bundle["plan"]["requests"]) == run.COUNTS[name]
        for request in bundle["plan"]["requests"]:
            assert request == next(r for r in old[name]["requests"] if r["request_id"] == request["request_id"])
            assert m.digest(m.encode(request["body"])) == request["body_sha256"]
            new.add((name, request["sample_id"]))
    assert len(new) == 18 and not (new & offline)
    assert bound["reserved_costs"]["CNY"] < 3.83 and bound["reserved_costs"]["USD"] < .05


@pytest.mark.parametrize("change", ["budget", "request", "pacing"])
def test_mutated_plan_fails_before_keys_or_http(bound, tmp_path, change):
    value = copy.deepcopy(bound)
    if change == "budget":
        value["authorization"]["max_new_calls"] = 19
    elif change == "pacing":
        value["authorization"]["kimi_min_start_interval_seconds"] = 1
    else:
        value["selected"]["qwen"]["plan"]["requests"][0]["body"]["max_tokens"] = 8192
    with pytest.raises(m.ModelRunError):
        run.verify(value, m.ROOT)
    with pytest.raises(m.ModelRunError):
        run.execute(allow_llm=False, sender=lambda *a: pytest.fail("HTTP"), credential_loader=lambda *a: pytest.fail("keys"))


@pytest.mark.parametrize("change", ["word", "source_id", "sample_id", "label"])
def test_echo_policy_rejects_semantic_or_identity_or_structure_changes(bound, change):
    request = bound["selected"]["qwen"]["plan"]["requests"][0]
    raw = json.loads(response_for(request, bound["selected"]["qwen"]["plan"]["profiles"]["qwen"]))
    payload = json.loads(raw["choices"][0]["message"]["content"])
    if change == "word":
        payload["source_text"] += " altered"
    elif change in ("source_id", "sample_id"):
        payload[change] = "wrong"
    else:
        candidate = bound["offline_recoveries"][0]
        originals = run.initial.saved_plans(m.ROOT)[1]
        request = next(r for r in originals[candidate["provider"]]["requests"] if r["sample_id"] == candidate["sample_id"])
        response = m.read_json(m.ROOT / candidate["source_response_path"])
        decoded = run.middle.decode_chat_completion_envelope(response["raw_response_utf8"].encode("utf-8"))
        text = decoded["content"].strip()
        if text.startswith("```json\n") and text.endswith("```"):
            text = text[8:-3].strip()
        payload = json.loads(text)
        payload["clauses"][0]["modality"]["label"] = "condition"
    prediction, audit = run.recover_echo(request, json.dumps(payload))
    assert prediction["request_status"] == "failed" and audit is None


@pytest.fixture
def mock_root(tmp_path, bound, monkeypatch):
    value = copy.deepcopy(bound)
    m.write_json(run.out_dir(tmp_path) / "plan.json", value)
    m.write_json(run.report_path(tmp_path, "_preflight.json"), value)
    paths = [m.ROOT / p for p in value["baseline_paths"].values()]
    paths += [run.final.report_path(), m.ROOT / run.initial.GOLD]
    for source in paths:
        target = tmp_path / source.relative_to(m.ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    # Execution mechanics use a copied fixed plan; actual immutable-parent gates are tested above.
    monkeypatch.setattr(run, "verify", lambda observed, root: pytest.fail("mutated mock plan") if observed != value else None)
    return tmp_path, value


def test_18_once_paced_and_all_merged_saved_before_gold_and_no_repeat(mock_root, monkeypatch):
    root, value = mock_root
    requests = {r["body_sha256"]: r for b in value["selected"].values() for r in b["plan"]["requests"]}
    ticks, sent = [1000.0], []
    def clock():
        return ticks[0]
    def sleeper(seconds):
        assert 0 < seconds <= 21
        ticks[0] += seconds
    def sender(profile, body, key, timeout):
        request = requests[m.digest(body)]
        sent.append((request["request_id"], clock()))
        payload = json.loads(response_for(request, profile))
        if request["provider"] == "kimi":
            payload["usage"]["completion_tokens_details"] = {"reasoning_tokens": 1}
        return m.encode(payload)
    read_json = m.read_json
    def check_gold(path):
        if path == root / run.initial.GOLD:
            assert all((run.out_dir(root) / name / "combined_predictions.json").exists() for name in run.COUNTS)
        return read_json(path)
    monkeypatch.setattr(m, "read_json", check_gold)
    result = run.execute(root, allow_llm=True, sender=sender, credential_loader=fake_keys, clock=clock, sleeper=sleeper)
    assert result["actual_new_calls_in_run"] == 18 and result["actual_calls"] == 918 and result["all_150_valid"]
    assert len(sent) == len({rid for rid, _ in sent}) == 18
    kimi = [t for rid, t in sent if rid.startswith("kimi:")]
    assert len(kimi) == 3 and all(b-a >= 21 for a, b in zip(kimi, kimi[1:]))
    for name, bundle in value["selected"].items():
        out = run.out_dir(root) / name
        starts, finishes, head = m._load_ledger(out / "calls_ledger.jsonl", bundle["plan"])
        m._verify_saved_calls(out, bundle["plan"], run.ledger_auth(value, name), starts, finishes)
        assert len(starts) == len(finishes) == run.COUNTS[name]
        assert result["providers"][name]["valid_predictions"] == 150
    with pytest.raises(m.ModelRunError):
        run.execute(root, allow_llm=True, sender=lambda *a: pytest.fail("duplicate"), credential_loader=lambda *a: pytest.fail("repeat keys"))


def test_transport_failures_stop_without_automatic_retry_and_retain_original(mock_root):
    root, value = mock_root
    calls = []
    def sender(profile, body, key, timeout):
        calls.append(m.digest(body))
        raise m.ModelRunError("HTTP 429: rate_limit_reached_error")
    result = run.execute(root, allow_llm=True, sender=sender, credential_loader=fake_keys)
    assert len(calls) == len(set(calls)) == 6
    assert result["actual_new_calls_in_run"] == 6 and result["status"] == "partial"
    assert len(result["remaining_failures"]) == 18
    assert result["retry"] == 0 and result["first_pass_results_preserved"]


def test_kimi_more_than_one_or_reasoning_text_is_rejected(bound):
    request = bound["selected"]["kimi"]["plan"]["requests"][0]
    profile = bound["selected"]["kimi"]["plan"]["profiles"]["kimi"]
    for count, text in ((2, ""), (1, "hidden reasoning")):
        raw = json.loads(response_for(request, profile))
        raw["usage"]["completion_tokens_details"] = {"reasoning_tokens": count}
        raw["choices"][0]["message"]["reasoning_content"] = text
        with pytest.raises(m.ModelRunError):
            run.parse_response(request, profile, m.encode(raw), bound["authorization"])
