"""Four-call authorization, exact feedback wire, pacing and no-repeat mechanics."""
import copy
import json
import shutil
import pytest

from bpc_hybrid import multi_model_stage2 as m
import run_stage2_structural_feedback_v1 as run
from test_multi_model_stage2 import no_live_access
from test_stage2_multi_model_all_v1 import fake_keys, response_for


@pytest.fixture(scope="module")
def bound():
    value = m.read_json(run.out_dir() / "plan.json")
    run.verify(value, m.ROOT)
    return value


def test_exact_four_preview_wires_budget_and_feedback_only(bound):
    preview = m.read_json(m.ROOT / run.PREVIEW)
    plan = bound["request_plan"]
    assert plan["requests"] == [entry["request"] for entry in preview["requests"]]
    assert [(r["provider"], r["sample_id"]) for r in plan["requests"]] == [
        ("kimi", "estg_000077"), ("kimi", "estg_000111"), ("glm", "estg_000164"), ("minimax", "estg_000164")]
    assert sum(b["max_cost"] for b in bound["budgets"].values()) < .99
    assert bound["authorization"]["max_new_calls"] == 4 and bound["authorization"]["max_combined_calls"] == 922
    assert all(r["body"]["thinking"] == {"type": "disabled"} for r in plan["requests"])
    assert all(m.digest(m.encode(r["body"])) == r["body_sha256"] for r in plan["requests"])


@pytest.mark.parametrize("change", ["budget", "body"])
def test_changed_plan_and_missing_flag_fail_before_keys_or_http(bound, change):
    value = copy.deepcopy(bound)
    if change == "budget":
        value["authorization"]["max_new_calls"] = 5
    else:
        value["request_plan"]["requests"][0]["body"]["messages"][-1]["content"] += " unauthorized"
    with pytest.raises(m.ModelRunError):
        run.verify(value, m.ROOT)
    with pytest.raises(m.ModelRunError):
        run.execute(allow_llm=False, sender=lambda *a: pytest.fail("HTTP"), credential_loader=lambda *a: pytest.fail("keys"))


@pytest.fixture
def mock_root(tmp_path, bound, monkeypatch):
    value = copy.deepcopy(bound)
    m.write_json(run.out_dir(tmp_path) / "plan.json", value)
    m.write_json(run.report_path(tmp_path, "_preflight.json"), value)
    paths = [run.parent.report_path(), m.ROOT / run.parent.initial.GOLD]
    paths += [run.parent.out_dir() / name / "combined_predictions.json" for name in run.parent.COUNTS]
    for source in paths:
        destination = tmp_path / source.relative_to(m.ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    monkeypatch.setattr(run, "verify", lambda observed, root: pytest.fail("changed mock plan") if observed != value else None)
    return tmp_path, value


def test_four_once_21_seconds_gold_after_merged_and_repeat_rejected(mock_root, monkeypatch):
    root, value = mock_root
    requests = {r["body_sha256"]: r for r in value["request_plan"]["requests"]}
    ticks, sent = [1000.0], []
    def sleeper(seconds):
        assert 0 < seconds <= 21
        ticks[0] += seconds
    def sender(profile, body, key, timeout):
        request = requests[m.digest(body)]
        sent.append((request["request_id"], ticks[0]))
        raw = json.loads(response_for(request, profile))
        if request["provider"] == "kimi":
            raw["usage"]["completion_tokens_details"] = {"reasoning_tokens": 1}
        return m.encode(raw)
    read_json = m.read_json
    def guard_gold(path):
        if path == root / run.parent.initial.GOLD:
            assert all((run.out_dir(root) / n / "combined_predictions.json").exists() for n in run.parent.COUNTS)
        return read_json(path)
    monkeypatch.setattr(m, "read_json", guard_gold)
    report = run.execute(root, allow_llm=True, sender=sender, credential_loader=fake_keys, clock=lambda: ticks[0], sleeper=sleeper)
    assert len(sent) == len({rid for rid, _ in sent}) == 4
    assert sent[1][1]-sent[0][1] >= 21
    assert report["actual_calls"] == 922 and report["actual_new_calls_in_run"] == 4 and report["all_150_valid"]
    assert all(row["valid_predictions"] == 150 for row in report["providers"].values())
    starts, finishes, head = m._load_ledger(run.out_dir(root) / "calls_ledger.jsonl", value["request_plan"])
    m._verify_saved_calls(run.out_dir(root), value["request_plan"], run.ledger_auth(value), starts, finishes)
    assert len(starts) == len(finishes) == 4
    for name in run.parent.COUNTS:
        old = m.read_json(run.parent.out_dir(root) / name / "combined_predictions.json")["records"]
        new = {r["sample_id"]: r for r in m.read_json(run.out_dir(root) / name / "combined_predictions.json")["records"]}
        assert all(new[r["sample_id"]] == r for r in old if r["request_status"] == "ok")
    with pytest.raises(m.ModelRunError):
        run.execute(root, allow_llm=True, sender=lambda *a: pytest.fail("repeat"), credential_loader=lambda *a: pytest.fail("repeat keys"))


def test_transport_exception_preserved_and_not_retried(mock_root):
    root, value = mock_root
    sent = []
    def sender(*a):
        sent.append(True)
        raise m.ModelRunError("HTTP 429: rate_limit_reached_error")
    report = run.execute(root, allow_llm=True, sender=sender, credential_loader=fake_keys)
    assert len(sent) == report["actual_new_calls_in_run"] == 1
    assert report["status"] == "partial" and len(report["remaining_failures"]) == 4
    assert report["retry"] == 0
    with pytest.raises(m.ModelRunError):
        run.execute(root, allow_llm=True, sender=lambda *a: pytest.fail("retry"), credential_loader=lambda *a: pytest.fail("keys"))
