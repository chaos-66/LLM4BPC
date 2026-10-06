"""Offline safety/measurement checks; real HTTP is always replaced in tests."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('thinking_run', ROOT / 'scripts/run_s2_thinking_sensitivity_v1.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    monkeypatch.setattr(run, 'RUN_ROOT', tmp_path / 'runs')
    monkeypatch.setattr(run, 'REPORT_ROOT', tmp_path / 'reports')
    # Bind all real read-only dependencies, but save test plans only in tmp_path.
    plan = run.prepare()
    return plan, run.RUN_ROOT / run.RUN_ID


def envelope(content='{}', reasoning='Reasoning for a synthetic test.', model=run.MODEL, finish='stop', usage=None):
    return json.dumps({'id': 'fake-response', 'model': model,
        'choices': [{'message': {'content': content, 'reasoning_content': reasoning}, 'finish_reason': finish}],
        'usage': {'prompt_tokens': 100, 'completion_tokens': 200} if usage is None else usage}).encode()


def test_messages_match_original_and_only_runtime_mode_changes():
    from bpc_hybrid.prompt_loader import load_prompt
    import run_direct_llm as original
    sample = run.core.samples(150)[0]
    prompt = load_prompt(run.PROMPT)
    body = run.body_for(sample)
    user = prompt.user_prompt_template.format(sample_id=sample['sample_id'], source_id=sample['sample_id'],
        source_text=sample['text'], few_shot_block=original._few_shot_block(prompt))
    assert body['messages'] == [{'role': 'system', 'content': prompt.system_prompt}, {'role': 'user', 'content': user}]
    assert body['thinking'] == {'type': 'enabled'} and body['reasoning_effort'] == 'high'
    assert body['max_tokens'] == 16384 and 'tools' not in body and 'response_format' not in body
    assert run.baselines().keys() == {'off_formal', 'off_0813', 'sun'}


def test_exact_150_scope_and_frozen_plan_tamper_rejected(prepared):
    plan, out = prepared
    run.verify_plan(plan, True)
    assert len(plan['requests']) == plan['budget']['call_cap'] == 150
    assert plan['new_off_calls'] == plan['new_sun_calls'] == 0
    for field, value in [('call_cap', 151), ('usd_cost_cap', 16), ('output_token_cap', 9999999)]:
        bad = copy.deepcopy(plan)
        bad['budget'][field] = value
        with pytest.raises(ValueError):
            run.verify_plan(bad, True)
    bad = copy.deepcopy(plan)
    bad['requests'][0]['body_sha256'] = 'wrong'
    with pytest.raises(ValueError):
        run.verify_plan(bad, True)
    with pytest.raises(ValueError):
        run.verify_plan(plan, False)


def test_missing_process_key_does_not_read_env_file(monkeypatch):
    for name in ('BPC_HYBRID_DeepSeek_API_KEY', 'DEEPSEEK_API_KEY', 'BPC_HYBRID_LLM_API_KEY'):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(ValueError, match='never read'):
        run.process_key()


def test_reasoning_and_final_are_saved_separately_and_truncation_fails():
    sample = {'sample_id': 'synthetic', 'text': 'Synthetic input.'}
    body = b'{}'
    row = run.response_row(sample, body, envelope(content='{"final":true}', reasoning='NOT A JSON ANSWER'), 200, 1)
    assert row['raw_response_content'] == '{"final":true}'
    assert row['reasoning_content'] == 'NOT A JSON ANSWER'
    assert row['response_envelope_sha256'] == run.sha(row['raw_response_envelope_json'].encode())
    truncated = run.response_row(sample, body, envelope(finish='length'), 200, 1)
    assert truncated['request_status'] == 'failed'
    pred = run.predictions_from_raw([truncated], {'synthetic': sample})[0]
    assert pred['request_status'] == 'failed' and pred['record'] == {}
    absent = run.response_row(sample, body, envelope(usage={}), 200, 1)
    assert run.row_abort(absent) and not absent['usage_known']
    wrong = run.response_row(sample, body, envelope(model='another-model'), 200, 1)
    assert run.row_abort(wrong)


def test_redaction_never_persists_the_credential():
    sample = {'sample_id': 'synthetic'}
    row = run.response_row(sample, b'{}', envelope(content='synthetic-key-value'), 200, 1, 'synthetic-key-value')
    assert 'synthetic-key-value' not in json.dumps(row)
    assert row['captured_envelope_redacted']


def test_in_doubt_and_completed_runs_never_resend(prepared):
    plan, out = prepared
    run.core._append_jsonl(out / 'calls_ledger.jsonl', {'sample_id': plan['requests'][0]['sample_id'], 'state': 'started'})
    with pytest.raises(ValueError, match='In-doubt'):
        run.restore(out, plan)
    run.write_json(out / 'execution_summary.json', {'complete': True})
    with pytest.raises(ValueError, match='cannot execute again'):
        run.restore(out, plan)


def test_first_authorized_sample_is_counted_and_failure_stops_without_retry(prepared, monkeypatch):
    plan, out = prepared
    calls = []
    monkeypatch.setattr(run, 'process_key', lambda: 'fake-key')
    def fake_send(sample, body, key):
        calls.append(sample['sample_id'])
        return run.response_row(sample, body, envelope(reasoning=''), 200, 0.1)
    monkeypatch.setattr(run, 'send_once', fake_send)
    monkeypatch.setattr(run, 'summarize', lambda plan, out: run.read_json(out / 'execution_summary.json'))
    summary = run.execute(plan, out, True)
    assert len(calls) == summary['actual_calls'] == 1
    assert summary['abort_reason'] and not summary['complete']
    assert len(run.core._read_jsonl(out / 'raw_responses.jsonl')) == 1
    assert len(run.core._read_jsonl(out / 'calls_ledger.jsonl')) == 2


def test_success_exactly_150_calls_no_baseline_or_retry_calls(prepared, monkeypatch):
    plan, out = prepared
    calls = []
    monkeypatch.setattr(run, 'process_key', lambda: 'fake-key')
    def fake_send(sample, body, key):
        calls.append(sample['sample_id'])
        return run.response_row(sample, body, envelope(), 200, 0.1)
    monkeypatch.setattr(run, 'send_once', fake_send)
    monkeypatch.setattr(run, 'summarize', lambda plan, out: run.read_json(out / 'execution_summary.json'))
    summary = run.execute(plan, out, True)
    assert summary['complete'] and len(calls) == len(set(calls)) == 150
    assert summary['retry'] == summary['new_off_calls'] == summary['new_sun_calls'] == 0
    assert summary['budget_gate']['calls_made'] == 150


def test_historical_formal_and_sun_reproduce_main_table():
    gold = run.read_json(run.core.FORMAL_GOLD)
    main = run.read_json(ROOT / 'outputs/reports/stage2_table1_paper_final_v1.json')
    arms = run.baselines()
    for arm, main_key in [('off_formal', 'direct_llm'), ('sun', 'sun_rule_only')]:
        evaluation = run.core.evaluate_coarse(gold, run.core.attempt_rows(arms[arm]), method_id=arm)
        assert evaluation['denominator'] == 150
        assert evaluation['coarse_five_field_micro']['f1'] == main['arms'][main_key]['overall_pooled_five_span_fields']['f1']
