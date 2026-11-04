"""Never-attempted scope, retained uncertain budget, and send pacing."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def runner():
    spec = importlib.util.spec_from_file_location("validation_continuation_test", ROOT / "scripts/continue_sun_modality_validation_v1.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture():
    requests = [{"call_id": sid, "request_sha256": sid + "-hash"} for sid in ("failed", "good", "never_sent")]
    events = []
    for sid, reserve, cost, valid in (("failed", .2, 0, False), ("good", .8, .5, True)):
        events += [{"kind": "started", "sample_id": sid, "request_sha256": sid + "-hash", "reserved_cny": reserve},
                   {"kind": "finished", "sample_id": sid, "request_sha256": sid + "-hash", "cost_cny": cost, "usage_verified": valid}]
    return requests, events


def test_completed_and_failed_calls_are_both_excluded_and_unknown_cost_is_retained():
    m = runner(); requests, events = fixture()
    remaining, cap = m.remaining_scope(requests, events, 80)
    assert [r["call_id"] for r in remaining] == ["never_sent"]
    assert cap == pytest.approx(79.3)


def test_started_without_completion_is_also_excluded_and_fully_reserved():
    m = runner(); requests, events = fixture()
    events = [r for r in events if not (r["kind"] == "finished" and r["sample_id"] == "failed")]
    remaining, cap = m.remaining_scope(requests, events, 80)
    assert [r["call_id"] for r in remaining] == ["never_sent"]
    assert cap == pytest.approx(79.3)


@pytest.mark.parametrize("change", ["duplicate", "hash", "outside"])
def test_scope_drift_cannot_create_a_new_grant(change):
    m = runner(); requests, events = fixture()
    if change == "duplicate": requests.append(requests[0])
    elif change == "hash": events[0]["request_sha256"] = "changed"
    else: events[0]["sample_id"] = "outside-original-approval"
    with pytest.raises(ValueError): m.remaining_scope(requests, events, 80)


def test_remaining_budget_cannot_be_reset_to_original_cap():
    m = runner(); requests, events = fixture()
    with pytest.raises(ValueError, match="budget"):
        m.remaining_scope(requests, events, .6)


def test_pacing_is_applied_once_per_call_without_retry():
    m = runner(); now, sent = [0.0], []
    def sleep(seconds): now[0] += seconds
    def send(value): sent.append((value, now[0])); return value
    wrapped = m.paced(send, clock=lambda: now[0], sleep=sleep, allowed=lambda: True)
    for value in range(4): assert wrapped(value) == value
    assert sent == [(0, 0.0), (1, 1.0), (2, 2.0), (3, 3.0)]


def test_window_is_checked_after_waiting_and_before_transport():
    m = runner(); now, sent = [0.0], []
    def sleep(seconds): now[0] += seconds
    wrapped = m.paced(lambda: sent.append(now[0]), clock=lambda: now[0], sleep=sleep,
                      allowed=lambda: now[0] < .5)
    wrapped()
    with pytest.raises(RuntimeError, match="before transport"):
        wrapped()
    assert sent == [0.0]


def test_parent_ledger_mutation_is_rejected_before_recovery(tmp_path):
    m = runner(); path = tmp_path / "parent.jsonl"
    path.write_text("changed parent ledger")
    with pytest.raises(ValueError, match="parent ledger drift"):
        m.verify_parent({}, {}, {"journal_path": str(path), "journal_sha256": "frozen-other-bytes"})


def test_partial_continuation_cannot_read_gold_or_emit_scores(tmp_path, monkeypatch):
    m = runner()
    continuation = {"requests": [{"call_id": "new", "request_sha256": "hash"}],
                    "derived_limits": {"cap_cny": 10, "max_calls": 1, "max_workers": 4},
                    "original_authorization_sha256": "auth", "original_preflight_sha256": "original"}
    def write(name, value):
        path = tmp_path / name; path.write_text(json.dumps(value)); return path
    monkeypatch.setattr(m, "REPORT", tmp_path / "report")
    monkeypatch.setattr(m, "verify_plan", lambda: continuation)
    monkeypatch.setattr(m.prepared, "REPORT", write("preflight.json", {}))
    monkeypatch.setattr(m, "AUTH", write("auth.json", {}))
    monkeypatch.setattr(m, "INTERRUPTION", write("interruption.json", {}))
    monkeypatch.setattr(m, "verify_parent", lambda *args: ({}, {}, [], 10))
    monkeypatch.setattr(m, "JOURNAL", tmp_path / "missing-events.jsonl")
    payload = {"authorization": continuation["derived_limits"], "authorization_sha256": "auth",
               "validation_preflight_sha256": "original",
               "requests": [{"sample_id": "new", "fewshot_request_sha256": "hash"}]}
    monkeypatch.setattr(m, "EXECUTION_PLAN", write("execution.json", {"payload": payload}))
    monkeypatch.setattr(m.data, "load_split", lambda _: pytest.fail("Gold must remain unread until full coverage"))
    with pytest.raises(ValueError, match="batch incomplete"):
        m.report()
    assert not (tmp_path / "report.json").exists()
