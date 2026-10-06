"""Independent persisted-evidence checks for the one authorized thinking run.

These tests are offline and verify either complete results or a recorded stop.
"""
import importlib.util
import json
from pathlib import Path
import sys
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('thinking_result_check', ROOT / 'scripts/run_s2_thinking_sensitivity_v1.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
OUT = run.RUN_ROOT / run.RUN_ID


def test_git_checkout_bytes_preserve_saved_manifest_hashes():
    manifest = run.read_json(OUT / 'run_manifest.json')
    bindings = dict(manifest['source_bindings'])
    bindings.update({(OUT / name).relative_to(ROOT).as_posix(): digest
                     for name, digest in manifest['artifacts'].items()})
    for path, digest in bindings.items():
        git_path = 'formal_experiment/' + path
        checkout_bytes = subprocess.check_output(
            ['git', 'cat-file', '--filters', '--path=' + git_path, ':' + git_path],
            cwd=ROOT.parent,
        )
        assert run.sha(checkout_bytes) == digest, path


def normalized(value):
    return json.loads(json.dumps(value, ensure_ascii=False))


def test_persisted_manifest_and_frozen_sources_match():
    manifest = run.read_json(OUT / 'run_manifest.json')
    assert manifest['status'] in ('complete', 'partial')
    for path, digest in manifest['source_bindings'].items():
        assert run.sha_file(ROOT / path) == digest, path
    for filename, digest in manifest['artifacts'].items():
        assert run.sha_file(OUT / filename) == digest, filename
    plan = run.read_json(OUT / 'plan.json')
    run.verify_plan(plan, True)
    assert plan['new_off_calls'] == plan['new_sun_calls'] == 0


def test_150_unique_requests_ledger_response_envelope_and_usage_bindings():
    plan = run.read_json(OUT / 'plan.json')
    raw = run.core._read_jsonl(OUT / 'raw_responses.jsonl')
    ledger = run.core._read_jsonl(OUT / 'calls_ledger.jsonl')
    starts = [r for r in ledger if r['state'] == 'started']
    completions = [r for r in ledger if r['state'] == 'completed']
    summary = run.read_json(OUT / 'execution_summary.json')
    count = summary['actual_calls']
    assert len(plan['requests']) == 150
    assert len(raw) == len(starts) == len(completions) == count
    assert 0 < count <= 150
    expected = {r['sample_id']: r for r in plan['requests']}
    assert len({r['sample_id'] for r in starts}) == count
    assert {r['sample_id'] for r in raw} == {r['sample_id'] for r in completions}
    assert {r['sample_id'] for r in raw} <= set(expected)
    for row in raw:
        assert row['request_body_sha256'] == expected[row['sample_id']]['body_sha256']
        assert row['response_sha256'] == run.sha(row['raw_response_content'].encode('utf-8'))
        assert row['reasoning_sha256'] == run.sha(row['reasoning_content'].encode('utf-8'))
        assert row['response_envelope_sha256'] == run.sha(row['raw_response_envelope_json'].encode('utf-8'))
        assert row['response_envelope'] == json.loads(row['raw_response_envelope_json'])
        assert row['usage_known'] and row['returned_model'] == run.MODEL
        assert row['network_call'] == 1
    assert summary['actual_calls'] == summary['budget_gate']['calls_made'] == count
    assert (count == 150 and not summary['abort_reason']) == summary['complete']
    assert summary['retry'] == summary['new_off_calls'] == summary['new_sun_calls'] == 0
    assert summary['budget_gate']['input_tokens'] == sum(r['usage']['prompt_tokens'] for r in raw)
    assert summary['budget_gate']['output_tokens'] == sum(r['usage']['completion_tokens'] for r in raw)
    assert summary['budget_gate']['cost_usd'] <= plan['budget']['usd_cost_cap']


def test_predictions_metrics_failures_and_cost_recompute_from_saved_evidence():
    report = run.read_json(OUT / 'result.json')
    raw = run.core._read_jsonl(OUT / 'raw_responses.jsonl')
    if report['status'] == 'partial':
        assert report['metrics'] is None and report['arms'] == {}
        assert report['execution']['abort_reason']
        if report['execution']['actual_calls'] == 1:
            assert raw[0]['finish_reason'] == 'length'
            assert raw[0]['usage']['completion_tokens'] == 16384
            assert raw[0]['usage']['completion_tokens_details']['reasoning_tokens'] == 16384
            assert raw[0]['raw_response_content'] == ''
        return
    row_map = {s['sample_id']: s for s in run.core.samples(150)}
    predictions = run.read_json(OUT / 'thinking_on_predictions.json')['records']
    assert normalized(run.predictions_from_raw(raw, row_map)) == predictions
    gold = run.read_json(run.core.FORMAL_GOLD)
    for arm, rows in {'thinking_on': predictions, **run.baselines()}.items():
        evaluation = run.core.evaluate_coarse(gold, run.core.attempt_rows(rows), method_id=arm)
        assert normalized(evaluation) == run.read_json(OUT / (arm + '_evaluation.json'))
        assert evaluation['denominator'] == report['arms'][arm]['denominator'] == 150
        assert evaluation['coarse_five_field_micro'] == report['arms'][arm]['overall']
        assert evaluation['failed_count'] == report['arms'][arm]['failed_count']
    inp = sum(r['usage']['prompt_tokens'] for r in raw)
    output = sum(r['usage']['completion_tokens'] for r in raw)
    hit = sum(r['usage'].get('prompt_cache_hit_tokens', 0) for r in raw)
    assert report['cost']['peak_no_cache_estimate_usd'] == pytest.approx((inp * 1.32 + output * 3.96) / 1e6)
    assert report['cost']['peak_with_reported_cache_estimate_usd'] == pytest.approx(((inp-hit) * 1.32 + hit * 0.044 + output * 3.96) / 1e6)
    assert report['cost']['account_deduction_verified'] is False
