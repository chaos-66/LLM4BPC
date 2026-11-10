"""Focused fake-transport checks for the authorized sentence execution wrapper."""
import copy
import json
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_sun_modality_sentence_v1 as run


@pytest.mark.parametrize("key,value", [("max_calls", 427), ("cap_cny", 36), ("max_workers", 5),
    ("retries", 1), ("off_peak_only", False), ("execute_authorized", False),
    ("model", "another-model"), ("approved_preflight_sha256", "wrong")])
def test_authorization_cannot_expand_or_switch_candidate(key, value):
    auth = run.read(run.AUTH)
    auth[key] = value
    with pytest.raises(ValueError, match="authorization"):
        run.authorize(auth, run.APPROVED)


def fixture():
    obj = run.read(run.sentence.PROMPT_DIR / "format_examples.json")[3]
    rr = obj["rule_record"]
    sid, rid, text = "dataset-synthetic", rr["sample_id"], rr["source_text"]
    body = run.sentence.request_body(rid, text, system="Synthetic only.", examples=[])
    sha = run.boundary.digest(run.boundary.wire_bytes(body))
    row = {"kind": "finished", "sample_id": rid, "timestamp": "2026-11-10T10:00:01+00:00",
           "request_sha256": sha, "body_hash_match": True, "returned_model": "deepseek-v4-pro",
           "model_accepted": True, "request_status": "ok", "error_type": None, "http_status": None,
           "raw_content": json.dumps(obj), "usage": {"prompt_tokens": 10, "completion_tokens": 2},
           "usage_verified": True, "latency_seconds": 0.1}
    row["response_sha256"] = run.boundary.digest(row["raw_content"].encode())
    row["cost_cny"] = run.llm_se.cost_cny(row["usage"], run.LIMITS["price_cny_per_million"]["off_peak"])
    return sid, rid, text, body, row


def test_adapter_keeps_primary_and_first_clause_separate():
    sid, rid, text, _, row = fixture()
    result = run.adapt_finished(row, sample_id=sid, request_id=rid, source_text=text)
    assert result["sample_id"] == sid and result["request_id"] == rid
    assert result["label"] == "obligation" and result["first_clause_label"] == "definition"
    assert result["raw_content"] == row["raw_content"]
    assert result["clauses"] == 2
    assert result["rule_record_validation"]["errors"] == []


@pytest.mark.parametrize("bad_field", ["model_accepted", "body_hash_match", "usage_verified"])
def test_request_or_accounting_failure_is_no_prediction(bad_field):
    sid, rid, text, _, row = fixture()
    row[bad_field] = False
    result = run.adapt_finished(row, sample_id=sid, request_id=rid, source_text=text)
    assert result["label"] is None and result["first_clause_label"] is None


def test_exact_wire_body_is_checked_before_transport():
    from bpc_hybrid.llm_config import LLMConfig
    _, _, _, body, row = fixture()
    config = LLMConfig(enabled=True, provider="openai_compatible", model="deepseek-v4-pro",
                       api_key="synthetic-not-a-secret", base_url="https://api.deepseek.com",
                       temperature=0.0, top_p=1.0, max_tokens=4096)
    run.verify_transport_body(config, body, row["request_sha256"])
    with pytest.raises(ValueError, match="different request bytes"):
        run.verify_transport_body(config, body, "wrong")


def test_journal_replay_checks_response_parse_and_budget():
    sid, rid, text, body, raw = fixture()
    auth = run.read(run.AUTH)
    start = {"kind": "started", "sample_id": sid, "request_sha256": raw["request_sha256"],
             "timestamp": "2026-11-10T10:00:00+00:00", "price_window": "off_peak",
             "reserved_cny": run.boundary.reserve_cost(body, auth["price_cny_per_million"]["off_peak"])}
    finished = run.adapt_finished(raw, sample_id=sid, request_id=rid, source_text=text)
    events = [start, finished]
    _, audit = run.verify_journal(events, [(sid, text)], {sid: body}, {sid: rid}, auth)
    assert audit["completed"] and audit["actual_known_cost_cny"] == raw["cost_cny"]
    bad = copy.deepcopy(events)
    bad[1]["label"] = "permission"
    with pytest.raises(ValueError, match="parsing"):
        run.verify_journal(bad, [(sid, text)], {sid: body}, {sid: rid}, auth)
    bad = copy.deepcopy(events)
    bad[0]["timestamp"] = "2026-11-10T07:00:00+00:00"
    with pytest.raises(ValueError, match="window"):
        run.verify_journal(bad, [(sid, text)], {sid: body}, {sid: rid}, auth)
    missing = run.verify_journal([], [(sid, text)], {sid: body}, {sid: rid}, auth)[1]
    assert not missing["completed"] and missing["uncalled"] == 1


def test_execution_loader_never_reads_test_gold(monkeypatch):
    original = run.data.load_split
    def train_only(name):
        assert name == "train"
        return original(name)
    monkeypatch.setattr(run.data, "load_split", train_only)
    pairs, bodies, ids, payload = run.verify_prepared()
    assert len(pairs) == len(bodies) == len(ids) == len(payload["requests"]) == 426
    assert payload["authorization"]["cap_cny"] == 35


def test_real_coordinator_receives_frozen_bodies_and_adapter(monkeypatch, tmp_path):
    from bpc_hybrid import llm_client
    sid, rid, text, body, raw = fixture()
    auth = dict(run.read(run.AUTH), max_calls=1)
    payload = {"authorization": auth, "authorization_sha256": "synthetic",
               "requests": [{"sample_id": sid, "fewshot_request_sha256": raw["request_sha256"]}]}
    monkeypatch.setattr(run, "RUN", tmp_path)
    monkeypatch.setattr(run, "PLAN", tmp_path / "plan.json")
    monkeypatch.setattr(run, "JOURNAL", tmp_path / "events.jsonl")
    run.PLAN.write_text(json.dumps({"payload": payload}))
    engine = run.make_engine([(sid, text)], {sid: body}, {sid: rid}, payload)
    monkeypatch.setattr(run.llm_se, "rate_for", lambda _: ("off_peak", {}))
    monkeypatch.setattr(engine.base, "environment_config", lambda: None)
    monkeypatch.setattr(run, "verify_transport_body", lambda *args: None)
    calls = []
    class FakeTransport:
        def __init__(self, *args, **kw):
            self.last_decode = {"model": "deepseek-v4-pro", "usage": raw["usage"]}
            self.last_request_body_sha256 = raw["request_sha256"]
        def send(self, request):
            calls.append(request.source_id)
            assert request.system_prompt == body["messages"][0]["content"]
            assert request.user_prompt == body["messages"][1]["content"]
            return SimpleNamespace(content=raw["raw_content"])
    monkeypatch.setattr(llm_client, "RealAPITransport", FakeTransport)
    engine.execute()
    engine.execute()  # existing completed attempt is never resent
    assert calls == [rid]
    done = run.boundary.read_events(run.JOURNAL)[-1]
    assert done["label"] == "obligation" and done["first_clause_label"] == "definition"


def test_malformed_record_clause_list_does_not_crash_worker():
    sid, rid, text, _, row = fixture()
    obj = json.loads(row["raw_content"])
    obj["rule_record"]["clauses"] = None
    row["raw_content"] = json.dumps(obj)
    result = run.adapt_finished(row, sample_id=sid, request_id=rid, source_text=text)
    assert result["clauses"] == 0 and result["first_clause_label"] is None


@pytest.mark.skipif(not run.RESULT.exists(), reason="authorized batch not completed yet")
def test_completed_report_matches_saved_responses():
    pairs, bodies, ids, payload = run.frozen_plan()
    done, audit = run.verify_journal(run.boundary.read_events(run.JOURNAL), pairs, bodies, ids, payload["authorization"])
    rows, old, _ = run.prepared.verify_control()
    result = run.sentence.evaluate_responses(rows,
        {sid: {"raw_content": r["raw_content"], "request_ok": not run.coordinator.failed(r)} for sid,r in done.items()},
        ids, {sid:r["label"] for sid,r in old.items()})
    stored = run.read(run.RESULT)
    assert all(stored[k] == v for k,v in result.items())
    assert stored["audit"] == audit
    assert audit["completed"] and audit["attempted"] == audit["finished"] == 426
    assert audit["actual_known_cost_cny"] <= 35 and audit["retry_count"] == 0
