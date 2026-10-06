"""Fake transport only: fresh-ID continuation, combined budget and throttling."""
import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_s2_thinking_remaining_v1 as run


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    monkeypatch.setattr(run, 'OUT', tmp_path / 'run')
    monkeypatch.setattr(run, 'REPORT', tmp_path / 'report')
    monkeypatch.setattr(run.parent.shared, 'process_key', lambda: 'fake-key')
    monkeypatch.setattr(run, 'summarize', lambda p: run.parent.shared.read_json(run.OUT / 'execution_summary.json'))
    return run.prepare()


def response(item, body, *, status=200, limit=None):
    value = {'model': run.parent.shared.MODEL, 'choices': [
        {'finish_reason': 'stop', 'message': {'content': '{}', 'reasoning_content': 'fake'}}],
        'usage': {'prompt_tokens': 100, 'completion_tokens': 200, 'total_tokens': 300,
                  'completion_tokens_details': {'reasoning_tokens': 150}}}
    if status != 200:
        value = {'error': {'message': (f'concurrency limit of {limit} based on your remaining balance'
                                     if limit is not None else 'Unauthorized')}}
    return run.parent.shared.response_row(item, body, json.dumps(value).encode(), status, .01)


def test_exact_45_fresh_ids_and_150_combined_no_retries(prepared, monkeypatch):
    calls = []
    def fake(item, body, key):
        assert key == 'fake-key' and 'max_tokens' not in json.loads(body)
        assert body == run.parent.request_bytes(item)
        calls.append(item['sample_id'])
        assert any(r['sample_id'] == item['sample_id'] and r['state'] == 'started'
                   for r in run.parent.shared.core._read_jsonl(run.OUT / 'calls_ledger.jsonl'))
        return response(item, body)
    monkeypatch.setattr(run, 'send_once', fake)
    summary = run.execute(prepared, True)
    old_ids = {r['sample_id'] for r in run.parent.shared.core._read_jsonl(run.PARENT_OUT / 'raw_responses.jsonl')}
    assert len(calls) == len(set(calls)) == 45 and not old_ids.intersection(calls)
    assert 'estg_000313' not in calls
    assert summary['complete'] and summary['actual_calls'] == summary['completed_calls'] == 150
    assert summary['new_calls'] == 45 and summary['inherited_calls'] == 105
    assert summary['retry'] == 0 and summary['budget_gate']['missing_usage_calls'] == 1
    assert (run.OUT / 'raw_responses.jsonl').read_bytes().startswith((run.PARENT_OUT / 'raw_responses.jsonl').read_bytes())
    with pytest.raises(ValueError, match='already started'):
        run.execute(prepared, True)


def test_balance_429_lowers_fresh_dispatch_and_keeps_failed_id(prepared, monkeypatch):
    first = prepared['remaining_ids'][0]
    calls = []
    def fake(item, body, key):
        calls.append(item['sample_id'])
        return response(item, body, status=429, limit=2) if item['sample_id'] == first else response(item, body)
    monkeypatch.setattr(run, 'send_once', fake)
    summary = run.execute(prepared, True)
    assert summary['complete'] and len(calls) == len(set(calls)) == 45
    assert calls.count(first) == 1 and summary['budget_gate']['missing_usage_calls'] == 2
    assert summary['dispatch_transitions'][-1]['workers'] == 1
    raw = run.parent.shared.core._read_jsonl(run.OUT / 'raw_responses.jsonl')
    failed = next(r for r in raw if r['sample_id'] == first)
    assert failed['request_status'] == 'failed' and failed['budget_usage']['completion_tokens'] == 65536


def test_other_api_failure_stops_fresh_ids_and_drains_inflight(prepared, monkeypatch):
    first = prepared['remaining_ids'][0]
    calls = []
    def fake(item, body, key):
        calls.append(item['sample_id'])
        return response(item, body, status=401) if item['sample_id'] == first else response(item, body)
    monkeypatch.setattr(run, 'send_once', fake)
    summary = run.execute(prepared, True)
    assert not summary['complete'] and summary['abort_reason']
    assert 1 <= len(calls) <= run.MAX_WORKERS
    assert summary['actual_calls'] == summary['completed_calls'] == 105 + len(calls)
    assert summary['retry'] == 0


def test_changed_combined_budget_or_remaining_membership_refuses(prepared):
    run.verify(prepared, True)
    with pytest.raises(ValueError):
        run.verify(prepared, False)
    for key, value in [('max_new_calls', 46), ('inherited_calls', 104), ('remaining_ids', ['estg_000313'])]:
        bad = copy.deepcopy(prepared)
        bad[key] = value
        with pytest.raises(ValueError):
            run.verify(bad, True)
    bad = copy.deepcopy(prepared)
    bad['budget']['call_cap'] = 151
    with pytest.raises(ValueError):
        run.verify(bad, True)
