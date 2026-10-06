"""Focused offline gates; fake transport only, including first-case truncation."""
import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_s2_thinking_default_v2 as run


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    monkeypatch.setattr(run, 'OUT', tmp_path / 'run')
    monkeypatch.setattr(run, 'REPORT', tmp_path / 'report' / 'default')
    return run.prepare()


def response(item, body, *, finish='stop', content='{}', model=None, usage=None, status=200):
    return run.shared.response_row(item, body, json.dumps({
        'model': run.shared.MODEL if model is None else model,
        'choices': [{'finish_reason': finish, 'message': {'content': content,
                                                       'reasoning_content': 'Synthetic reasoning.'}}],
        'usage': {'prompt_tokens': 100, 'completion_tokens': 200, 'total_tokens': 300,
                  'completion_tokens_details': {'reasoning_tokens': 150}} if usage is None else usage,
    }).encode(), status, .01)


def test_same_messages_high_and_default_parameter_omission():
    for item in run.shared.core.samples(150):
        old = run.shared.body_for(item)
        new = json.loads(run.request_bytes(item))
        del old['max_tokens']
        assert new == old
        assert 'max_tokens' not in new and 'max_completion_tokens' not in new
        assert new['thinking'] == {'type': 'enabled'} and new['reasoning_effort'] == 'high'


def test_authorization_all_150_bindings_and_budget_tamper_are_checked(prepared):
    run.verify(prepared, True)
    assert len(prepared['requests']) == 150
    assert prepared['budget']['output_token_cap'] == 150 * 65536
    with pytest.raises(ValueError):
        run.verify(prepared, False)
    for path, key, value in [('budget', 'call_cap', 151), ('budget', 'usd_cost_cap', 51),
                             ('budget', 'output_token_cap', 99999999),
                             ('generation', 'max_tokens', 65536)]:
        bad = copy.deepcopy(prepared)
        bad[path][key] = value
        with pytest.raises(ValueError):
            run.verify(bad, True)
    bad = copy.deepcopy(prepared)
    bad['requests'][0]['body_sha256'] = 'changed'
    with pytest.raises(ValueError):
        run.verify(bad, True)


def test_first_case_length_is_counted_and_exact_150_continue_without_retry(prepared, monkeypatch):
    calls = []
    first = prepared['requests'][0]['sample_id']
    monkeypatch.setattr(run.shared, 'process_key', lambda: 'fake-key')
    def fake(item, body, key):
        calls.append(item['sample_id'])
        assert 'max_tokens' not in json.loads(body)
        ledger = run.shared.core._read_jsonl(run.OUT / 'calls_ledger.jsonl')
        assert any(r['sample_id'] == item['sample_id'] and r['state'] == 'started' for r in ledger)
        if item['sample_id'] == first:
            return response(item, body, finish='length', content='')
        return response(item, body)
    monkeypatch.setattr(run, 'send_once', fake)
    monkeypatch.setattr(run, 'summarize', lambda plan: run.shared.read_json(run.OUT / 'execution_summary.json'))
    summary = run.execute(prepared, True)
    assert len(calls) == len(set(calls)) == 150
    assert summary['complete'] and summary['actual_calls'] == summary['completed_calls'] == 150
    assert summary['truncated_calls'] == summary['empty_final_calls'] == 1
    assert summary['retry'] == summary['new_off_calls'] == summary['new_sun_calls'] == 0
    assert len(run.shared.core._read_jsonl(run.OUT / 'raw_responses.jsonl')) == 150
    with pytest.raises(ValueError, match='completed/aborted'):
        run.execute(prepared, True)


def test_fatal_api_contract_stops_new_sends_and_drains_existing_calls(prepared, monkeypatch):
    calls = []
    first = prepared['requests'][0]['sample_id']
    monkeypatch.setattr(run.shared, 'process_key', lambda: 'fake-key')
    def fake(item, body, key):
        calls.append(item['sample_id'])
        return response(item, body, status=401, usage={}) if item['sample_id'] == first else response(item, body)
    monkeypatch.setattr(run, 'send_once', fake)
    monkeypatch.setattr(run, 'summarize', lambda plan: run.shared.read_json(run.OUT / 'execution_summary.json'))
    summary = run.execute(prepared, True)
    assert 0 < len(calls) <= run.MAX_WORKERS < 150
    assert summary['actual_calls'] == summary['completed_calls'] == len(calls)
    assert summary['abort_reason'] and not summary['complete']
    assert summary['budget_gate']['missing_usage_calls'] == 1
    assert len(run.shared.core._read_jsonl(run.OUT / 'raw_responses.jsonl')) == len(calls)


def test_in_doubt_ledger_refuses_resend(prepared):
    run.shared.core._append_jsonl(run.OUT / 'calls_ledger.jsonl', {
        'sample_id': prepared['requests'][0]['sample_id'], 'state': 'started'})
    with pytest.raises(ValueError, match='In-doubt'):
        run.restore(prepared)


def test_only_successful_final_content_enters_shared_parser():
    item = run.shared.core.samples(150)[0]
    row = response(item, b'{}', content='', finish='length')
    pred = run.shared.predictions_from_raw([row], {item['sample_id']: item})[0]
    assert pred['request_status'] == 'failed' and pred['record'] == {}
    assert run.fatal_reason(row) is None
    row['usage']['completion_tokens'] = 65537
    assert run.fatal_reason(row)


def test_nearest_rank_percentiles_are_explicit():
    stats = run.token_stats(list(range(1, 151)))
    assert stats['count'] == 150 and stats['total'] == 11325
    assert stats['median'] == 75.5 and stats['p90_nearest_rank'] == 135 and stats['max'] == 150
