"""Offline checks for the authorized one-call diagnostic; transport is mocked."""
import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_s2_thinking_single_high_v1 as run


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    monkeypatch.setattr(run, 'OUT', tmp_path / 'evidence')
    monkeypatch.setattr(run, 'REPORT', tmp_path / 'reports' / 'single')
    return run.prepare()


def test_same_failed_sample_request_changes_only_provider_ceiling():
    old = run.previous.body_for(run.sample())
    new = run.body_for(run.sample())
    assert [k for k in old if old[k] != new[k]] == ['max_tokens']
    assert new['max_tokens'] == 393216 and new['reasoning_effort'] == 'high'
    assert run.sample()['sample_id'] == 'estg_000002'


def test_authorization_and_frozen_request_are_enforced(prepared):
    run.verify(prepared, True)
    with pytest.raises(ValueError):
        run.verify(prepared, False)
    bad = copy.deepcopy(prepared)
    bad['max_calls'] = 2
    with pytest.raises(ValueError):
        run.verify(bad, True)
    bad = copy.deepcopy(prepared)
    bad['request_body_sha256'] = 'wrong'
    with pytest.raises(ValueError):
        run.verify(bad, True)


def test_in_doubt_and_completed_calls_cannot_resend(prepared, monkeypatch):
    monkeypatch.setattr(run.previous, 'process_key', lambda: 'fake-key')
    calls = []
    def fake(item, body, key):
        calls.append(item['sample_id'])
        envelope = {'model': run.previous.MODEL, 'choices': [{'message': {'content': '{"synthetic":true}',
            'reasoning_content': 'synthetic'}, 'finish_reason': 'stop'}],
            'usage': {'prompt_tokens': 100, 'completion_tokens': 30000, 'total_tokens': 30100,
                      'completion_tokens_details': {'reasoning_tokens': 28000}}}
        return run.previous.response_row(item, body, json.dumps(envelope).encode(), 200, 1)
    monkeypatch.setattr(run, 'send_once', fake)
    monkeypatch.setattr(run, 'summarize', lambda plan: 'saved')
    assert run.execute(prepared, True) == 'saved'
    assert calls == ['estg_000002']
    with pytest.raises(ValueError, match='no resend'):
        run.execute(prepared, True)
    (run.OUT / 'raw_responses.jsonl').unlink()
    with pytest.raises(ValueError, match='no resend'):
        run.execute(prepared, True)
    assert len(calls) == 1


def test_token_breakdown_does_not_treat_truncation_as_completion():
    envelope = {'model': run.previous.MODEL, 'choices': [{'message': {'content': '',
        'reasoning_content': 'synthetic reasoning'}, 'finish_reason': 'length'}],
        'usage': {'prompt_tokens': 100, 'completion_tokens': 393216, 'total_tokens': 393316,
                  'completion_tokens_details': {'reasoning_tokens': 393216}}}
    row = run.previous.response_row(run.sample(), b'{}', json.dumps(envelope).encode(), 200, 1)
    stats = run.measurements(row)
    assert stats['reasoning_tokens'] == 393216 and stats['final_answer_tokens'] == 0
    assert not stats['natural_completion'] and 'unknown' in stats['interpretation']
    row['usage'] = {}
    row['usage_known'] = False
    stats = run.measurements(row)
    assert stats['final_answer_tokens'] is None and stats['peak_no_cache_estimate_usd'] is None
