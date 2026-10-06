"""Verify persisted real-run evidence offline; never send or resume requests."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_s2_prompt_simplification_v2 as run

REPORT = ROOT / 'outputs/reports/s2_prompt_simplification_comparison_20261006_v2.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


@pytest.fixture
def evidence():
    if not REPORT.exists():
        pytest.skip('Authorized real-run result is not yet available.')
    report = read(REPORT)
    assert report['status'] == 'complete'
    return report, ROOT / report['evidence_root']


def test_all_saved_artifact_hashes_match(evidence):
    report, directory = evidence
    for filename, expected in report['artifact_bindings'].items():
        assert hashlib.sha256((directory / filename).read_bytes()).hexdigest() == expected
    assert hashlib.sha256((directory / 'plan.json').read_bytes()).hexdigest() == report['plan_sha256']
    assert report['preserved_files_unchanged'] is True
    manifest = read(directory / 'run_manifest.json')
    for relative, expected in manifest['report_bindings'].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
    for filename, expected in manifest['evidence_artifact_bindings'].items():
        assert hashlib.sha256((directory / filename).read_bytes()).hexdigest() == expected


def test_only_300_unique_ab_calls_and_complete_ledger(evidence):
    report, directory = evidence
    plan = read(directory / 'plan.json')
    raw = rows(directory / 'raw_responses.jsonl')
    ledger = rows(directory / 'calls_ledger.jsonl')
    expected = {(r['arm'], r['sample_id']): r for r in plan['requests']}
    assert len(expected) == len(raw) == 300
    assert {(r['arm'], r['sample_id']) for r in raw} == set(expected)
    assert set(plan['arms']) == {'A', 'B'}
    assert plan['authorization']['data_transfer_authorized'] is True
    assert plan['baseline_reuse']['new_api_calls'] == 0
    assert report['execution']['actual_calls'] == 300
    assert report['execution']['budget_gate']['cost_usd'] <= 9.76
    for state in ('started', 'completed'):
        entries = [r for r in ledger if r['state'] == state]
        assert len(entries) == 300
        assert {(r['arm'], r['sample_id']) for r in entries} == set(expected)
    for row in raw:
        assert row['request_body_sha256'] == expected[(row['arm'], row['sample_id'])]['body_sha256']
        assert hashlib.sha256(row['raw_response_content'].encode('utf-8')).hexdigest() == row['response_sha256']
        assert row['usage_known'] and row['returned_model'] == 'deepseek-v4-pro'
    assert report['arms']['v6']['new_api_calls'] == 0
    assert all(report['arms'][a]['new_api_calls'] == 150 for a in ('A', 'B'))


def test_shared_evaluation_reproduces_from_saved_predictions(evidence):
    report, directory = evidence
    gold = run.core._read_json(run.core.FORMAL_GOLD)
    for arm in ('v6', 'A', 'B'):
        predictions = rows(directory / f'{arm}_canonical_predictions.jsonl')
        assert len(predictions) == len({p['sample_id'] for p in predictions}) == 150
        computed = run.core.evaluate_coarse(gold, run.core.attempt_rows(predictions), method_id=f'prompt_simplification_{arm}')
        # JSON represents the evaluator's tuple of modality classes as an array.
        assert json.loads(json.dumps(computed)) == read(directory / f'{arm}_evaluation.json')
        assert report['arms'][arm]['overall_f1'] == computed['coarse_five_field_micro']['f1']
        assert report['arms'][arm]['per_field'] == computed['five_fields']
    assert report['arms']['v6']['overall_f1'] == pytest.approx(0.8224493117168078)
    changes = read(directory / 'paired_sample_changes.json')
    assert len(changes) == len({r['sample_id'] for r in changes}) == 150


def test_raw_format_and_usage_counts_are_independent_of_repair(evidence):
    report, directory = evidence
    new_raw = rows(directory / 'raw_responses.jsonl')
    for arm in ('v6', 'A', 'B'):
        raw = rows(directory / 'v6_historical_raw_responses.jsonl') if arm == 'v6' else [r for r in new_raw if r['arm'] == arm]
        strict = 0
        for row in raw:
            try:
                strict += isinstance(json.loads(row['raw_response_content']), dict)
            except ValueError:
                pass
        saved = report['arms'][arm]
        assert saved['raw_strict_json_objects'] == strict
        assert saved['raw_fenced_responses'] == sum(r['raw_response_content'].strip().startswith('```') for r in raw)
        assert saved['input_tokens'] == sum(r['usage']['prompt_tokens'] for r in raw)
        assert saved['output_tokens'] == sum(r['usage']['completion_tokens'] for r in raw)
