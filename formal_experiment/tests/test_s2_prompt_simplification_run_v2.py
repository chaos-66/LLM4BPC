"""Focused checks for real-call scope, request binding, and restart safety; no network."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('simplify_run_v2', ROOT / 'scripts/run_s2_prompt_simplification_v2.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    monkeypatch.setattr(run, 'RUN_ROOT', tmp_path / 'runs')
    monkeypatch.setattr(run, 'write_json', lambda p, v: (p.parent.mkdir(parents=True, exist_ok=True), p.write_text(json.dumps(v))))
    # Keep this test preparation's public report outside the real workspace.
    real_root = run.ROOT
    def scoped_write(path, value):
        destination = tmp_path / 'public' / path.name if str(path).startswith(str(real_root / 'outputs/reports')) else path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(value), encoding='utf-8')
    monkeypatch.setattr(run, 'write_json', scoped_write)
    plan = run.prepare()
    return plan, run.RUN_ROOT / run.RUN_ID


def test_preflight_scope_and_exact_request_recipe(prepared):
    plan, out = prepared
    assert plan['budget']['call_cap'] == len(plan['requests']) == 300
    assert plan['budget']['output_token_cap'] == 300 * 4096
    assert all(sum(r['arm'] == a for r in plan['requests']) == 150 for a in run.ARMS)
    assert plan['baseline_reuse']['new_api_calls'] == 0
    assert plan['baseline_reuse']['verified_request_fingerprints'] == 150
    assert set(plan['arms']) == {'A', 'B'} and plan['max_workers'] == 6
    sample = run.core.samples(150)[0]
    bodies = [run.body_for(a, sample) for a in run.ARMS]
    assert len({b['messages'][1]['content'] for b in bodies}) == 1
    for arm, body in zip(run.ARMS, bodies):
        assert body['model'] == 'deepseek-v4-pro'
        assert body['temperature'] == 0 and body['top_p'] == 1 and body['max_tokens'] == 4096
        assert body['thinking'] == {'type': 'disabled'}
        assert 'response_format' not in body and 'seed' not in body
        expected = next(r for r in plan['requests'] if r['arm'] == arm and r['sample_id'] == sample['sample_id'])
        assert expected['body_sha256'] == run.sha_bytes(json.dumps(body).encode('utf-8'))
    run.verify_plan(plan, True)


def test_no_authorization_never_loads_credentials(prepared, monkeypatch):
    plan, out = prepared
    monkeypatch.setattr(run, 'private_process_config', lambda: pytest.fail('credential accessed before authorization'))
    with pytest.raises(ValueError, match='authorization'):
        run.execute(plan, out, False)
    assert not (out / 'calls_ledger.jsonl').exists()


def test_changed_or_missing_source_binding_is_rejected(prepared):
    plan, _ = prepared
    first = next(iter(plan['source_bindings']))
    plan['source_bindings'][first] = '0' * 64
    with pytest.raises(ValueError, match='changed'):
        run.verify_plan(plan, True)
    del plan['source_bindings'][first]
    with pytest.raises(ValueError, match='missing'):
        run.verify_plan(plan, True)


def test_in_doubt_request_is_not_repeated(prepared, monkeypatch):
    plan, out = prepared
    run.core._append_jsonl(out / 'calls_ledger.jsonl', {'arm': 'A', 'sample_id': 'estg_pending', 'state': 'started'})
    monkeypatch.setattr(run, 'private_process_config', lambda: run.config_for())
    monkeypatch.setattr(run, 'send_once', lambda *args: pytest.fail('in-doubt request resent'))
    with pytest.raises(ValueError, match='In-doubt'):
        run.execute(plan, out, True)


def test_completed_or_aborted_run_never_resends(prepared, monkeypatch):
    plan, out = prepared
    monkeypatch.setattr(run, 'private_process_config', lambda: pytest.fail('immutable run loaded key'))
    for summary in ({'complete': True}, {'complete': False, 'abort_reason': 'missing usage'}):
        run.write_json(out / 'execution_summary.json', summary)
        with pytest.raises(ValueError, match='immutable|Aborted'):
            run.execute(plan, out, True)


def test_call_budget_counts_errors_and_refuses_extra_request():
    budget = {'call_cap': 1, 'input_token_cap': 100, 'output_token_cap': 100,
              'usd_cost_cap': 1, 'price_snapshot': {'input_cache_miss_per_million': 1.32, 'output_per_million': 3.96}}
    gate = run.core.AblationBudgetGate(budget, 'deepseek-v4-pro')
    gate.check_before_send(10, 20)
    gate.record_response({'prompt_tokens': 10, 'completion_tokens': 20}, None)
    with pytest.raises(run.core.SepC3Error, match='call cap'):
        gate.check_before_send(1, 1)


def test_raw_format_is_measured_before_shared_postprocessing():
    obj = {k: [] for k in run.KEYS}
    assert run.raw_diagnostics({'raw_response_content': json.dumps(obj)})['exact_top_level_keys']
    fenced = run.raw_diagnostics({'raw_response_content': '```json\n' + json.dumps(obj) + '\n```'})
    assert fenced['fenced'] and not fenced['strict_json_object']
    del obj['validation']
    assert run.raw_diagnostics({'raw_response_content': json.dumps(obj)})['missing_top_level_keys'] == ['validation']


def test_transfer_approval_is_required(prepared):
    plan, _ = prepared
    plan['authorization']['data_transfer_authorized'] = False
    with pytest.raises(ValueError, match='Authorization/data-transfer'):
        run.verify_plan(plan, True)


def test_batched_execution_sends_only_300_ab_calls(prepared, monkeypatch):
    plan, out = prepared
    sent = []
    monkeypatch.setattr(run, 'private_process_config', lambda: run.config_for())
    def fake_send(arm, sample, config, expected_hash):
        sent.append((arm, sample['sample_id']))
        content = '{}'
        return {'arm': arm, 'sample_id': sample['sample_id'], 'request_body_sha256': expected_hash,
                'raw_response_content': content, 'response_sha256': run.sha_bytes(content.encode()),
                'usage': {'prompt_tokens': 10, 'completion_tokens': 10},
                'returned_model': 'deepseek-v4-pro', 'request_status': 'ok', 'network_call': 1}
    monkeypatch.setattr(run, 'send_once', fake_send)
    monkeypatch.setattr(run, 'summarize', lambda p, o: {'status': 'complete'})
    assert run.execute(plan, out, True)['status'] == 'complete'
    assert len(sent) == len(set(sent)) == 300
    assert all(arm in {'A', 'B'} for arm, _ in sent)
    assert all(sum(arm == a for arm, _ in sent) == 150 for a in ['A', 'B'])
    summary = run.core._read_json(out / 'execution_summary.json')
    assert summary['complete'] and summary['actual_calls'] == 300
    assert summary['new_calls_by_arm'] == {'A': 150, 'B': 150}
