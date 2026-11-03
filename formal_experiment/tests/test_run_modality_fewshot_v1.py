"""Fake-worker checks for bounded concurrent execution; never calls an API."""
import importlib.util
import json
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bpc_hybrid.modality_benchmark import boundary, llm_se


def runner():
    spec = importlib.util.spec_from_file_location("fewshot_execution_test", ROOT / "scripts/run_sun_modality_fewshot_v1.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def fake_run(tmp_path, monkeypatch):
    m = runner()
    pairs = [(str(i), "A user may submit a form.") for i in range(10)]
    bodies = {sid: boundary.request_body(sid, text) for sid, text in pairs}
    auth = {"max_calls": 10, "cap_cny": 20.0, "max_workers": 8,
            "price_cny_per_million": llm_se.PRICE_CNY_PER_MILLION}
    payload = {"authorization": auth, "authorization_sha256": "synthetic",
               "requests": [{"sample_id": sid, "fewshot_request_sha256": boundary.digest(boundary.wire_bytes(bodies[sid]))} for sid, _ in pairs]}
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"payload": payload}))
    monkeypatch.setattr(m, "PLAN", plan)
    monkeypatch.setattr(m, "RUN", tmp_path)
    monkeypatch.setattr(m, "JOURNAL", tmp_path / "local_only/events.jsonl")
    monkeypatch.setattr(m, "plan_payload", lambda: payload)
    monkeypatch.setattr(m.base, "environment_config", lambda: None)
    monkeypatch.setattr(m.fewshot, "load_demonstrations", lambda: ("synthetic", {}))
    monkeypatch.setattr(m.fewshot, "request_body", lambda sid, text, **kw: bodies[sid])
    monkeypatch.setattr(m.data, "load_split_text_only", lambda name: pairs)
    monkeypatch.setattr(m.llm_se, "rate_for", lambda _: ("off_peak", {}))
    sent = []
    def fake_send(config, sid, text, body, request_hash, rate):
        sent.append(sid)
        time.sleep(0.01)
        return {"kind": "finished", "sample_id": sid, "request_sha256": request_hash,
                "request_status": "ok", "usage_verified": True, "model_accepted": True,
                "body_hash_match": True, "parse_status": "ok", "cost_cny": 0.001,
                "label": "permission", "raw_content": "synthetic"}
    monkeypatch.setattr(m, "send_one", fake_send)
    return m, payload, sent, fake_send, bodies


def freeze(m, payload):
    m.PLAN.write_text(json.dumps({"payload": payload}))


def test_concurrent_journal_and_completed_resume_do_not_resend(fake_run):
    m, _, sent, _, _ = fake_run
    m.execute()
    m.execute()
    assert len(sent) == len(set(sent)) == 10
    events = boundary.read_events(m.JOURNAL)
    active = peak = 0
    for row in events:
        active += 1 if row["kind"] == "started" else -1
        peak = max(peak, active)
    assert active == 0 and 1 < peak <= 8
    assert boundary.accounting(events) == (set(sent), pytest.approx(0.01), 0)


def test_all_in_flight_reservations_count_toward_cap(fake_run):
    m, payload, sent, _, bodies = fake_run
    rate = payload["authorization"]["price_cny_per_million"]["off_peak"]
    reservation = max(boundary.reserve_cost(b, rate) for b in bodies.values())
    payload["authorization"]["cap_cny"] = reservation * 1.5
    freeze(m, payload)
    m.execute()
    held, spent = {}, 0
    for row in boundary.read_events(m.JOURNAL):
        if row["kind"] == "started":
            held[row["sample_id"]] = row["reserved_cny"]
            assert spent + sum(held.values()) <= payload["authorization"]["cap_cny"]
        else:
            held.pop(row["sample_id"])
            spent += row["cost_cny"]
    assert len(sent) == 10


def test_no_send_when_budget_or_window_disallows(fake_run, monkeypatch):
    m, payload, sent, _, _ = fake_run
    payload["authorization"]["cap_cny"] = 0.00001
    freeze(m, payload)
    m.execute()
    assert not sent and not m.JOURNAL.exists()
    payload["authorization"]["cap_cny"] = 20
    freeze(m, payload)
    monkeypatch.setattr(m.llm_se, "rate_for", lambda _: ("peak", {}))
    m.execute()
    assert not sent


def test_failure_drains_in_flight_and_blocks_resume(fake_run, monkeypatch):
    m, _, sent, fake_send, _ = fake_run
    def fail(*args):
        row = fake_send(*args)
        row["model_accepted"] = False
        row["label"] = None
        return row
    monkeypatch.setattr(m, "send_one", fail)
    m.execute()
    assert 1 <= len(sent) <= 8
    events = boundary.read_events(m.JOURNAL)
    assert sum(r["kind"] == "started" for r in events) == sum(r["kind"] == "finished" for r in events)
    with pytest.raises(ValueError, match="prior request"):
        m.execute()


def test_membership_cannot_exceed_authorized_calls(fake_run):
    m, payload, sent, _, _ = fake_run
    payload["authorization"]["max_calls"] = 9
    freeze(m, payload)
    with pytest.raises(ValueError, match="membership"):
        m.execute()
    assert not sent


@pytest.mark.parametrize("usage", [{}, {"prompt_tokens": float("nan"), "completion_tokens": 1},
    {"prompt_tokens": 10, "completion_tokens": -1},
    {"prompt_tokens": 10, "completion_tokens": 1, "prompt_cache_hit_tokens": 20},
    {"prompt_tokens": 10, "completion_tokens": 1, "prompt_cache_hit_tokens": 4, "prompt_cache_miss_tokens": 4}])
def test_invalid_usage_cannot_release_budget(usage):
    assert not runner().usage_valid(usage)


def test_real_worker_builds_bound_request_without_network(monkeypatch):
    from bpc_hybrid import llm_client
    from types import SimpleNamespace
    m = runner()
    body = boundary.request_body("s", "Synthetic source.")
    request_hash = boundary.digest(boundary.wire_bytes(body))
    class FakeTransport:
        def __init__(self, *args, **kwargs):
            self.last_decode = {"model": "deepseek-v4-pro", "usage": {"prompt_tokens": 10, "completion_tokens": 2}}
            self.last_request_body_sha256 = request_hash
        def send(self, request):
            assert request.system_prompt == body["messages"][0]["content"]
            assert request.user_prompt == body["messages"][1]["content"]
            return SimpleNamespace(content='{"clauses":[{"modality":{"label":"permission"}}]}')
    monkeypatch.setattr(llm_client, "RealAPITransport", FakeTransport)
    row = m.send_one(None, "s", "Synthetic source.", body, request_hash, llm_se.PRICE_CNY_PER_MILLION["off_peak"])
    assert row["label"] == "permission" and not m.failed(row)
    assert row["response_sha256"] == boundary.digest(row["raw_content"].encode())
