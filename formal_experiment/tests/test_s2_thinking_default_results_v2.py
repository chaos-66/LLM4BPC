"""Offline checks of saved real responses, fixed denominators, usage and Git bytes.

Run only after the process exits and the immutable artifacts have been staged.
No transport or generation function is called by these checks.
"""
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_s2_thinking_default_v2 as run


def normalized(value):
    return json.loads(json.dumps(value, ensure_ascii=False))


@pytest.fixture(scope='module')
def saved():
    return {
        'plan': run.shared.read_json(run.OUT / 'plan.json'),
        'manifest': run.shared.read_json(run.OUT / 'run_manifest.json'),
        'report': run.shared.read_json(run.OUT / 'result.json'),
        'raw': run.shared.core._read_jsonl(run.OUT / 'raw_responses.jsonl'),
        'ledger': run.shared.core._read_jsonl(run.OUT / 'calls_ledger.jsonl'),
    }


def test_manifest_and_git_checkout_preserve_sources_and_every_artifact(saved):
    run.verify(saved['plan'], True)
    manifest = saved['manifest']
    assert manifest['run_id'] == run.RUN_ID
    assert manifest['source_bindings'] == saved['plan']['source_bindings']
    assert manifest['execution'] == saved['report']['execution']
    assert saved['report'] == run.shared.read_json(Path(str(run.REPORT) + '.json'))
    actual = {p.name for p in run.OUT.iterdir() if p.is_file() and p.name != 'run_manifest.json'}
    assert set(manifest['artifacts']) == actual
    bindings = dict(manifest['source_bindings'])
    bindings.update({(run.OUT / name).relative_to(ROOT).as_posix(): digest
                     for name, digest in manifest['artifacts'].items()})
    for path, digest in bindings.items():
        assert run.shared.sha_file(ROOT / path) == digest, path
        git_path = 'formal_experiment/' + path
        checkout = subprocess.check_output(
            ['git', 'cat-file', '--filters', '--path=' + git_path, ':' + git_path], cwd=ROOT.parent)
        assert run.shared.sha(checkout) == digest, path
    review = run.shared.read_json(Path(str(run.REPORT) + '_approval_review.json'))
    assert review['explicit_user_disclosure_authorization']['user_statement'] == (
        '授权将这150条法规文本及现有抽取提示词发送至 DeepSeek 官方 API 并运行')
    assert review['authorized_execution_resolution']['same_original_command_accepted']


def test_unique_ledger_requests_full_envelopes_and_budget_accounting(saved):
    plan, raw, ledger = saved['plan'], saved['raw'], saved['ledger']
    summary = saved['report']['execution']
    starts = {r['sample_id']: r for r in ledger if r['state'] == 'started'}
    finishes = {r['sample_id']: r for r in ledger if r['state'] == 'completed'}
    responses = {r['sample_id']: r for r in raw}
    assert len(ledger) == 2 * len(raw)
    assert len(starts) == len(finishes) == len(responses) == len(raw)
    assert set(starts) == set(finishes) == set(responses)
    assert summary['actual_calls'] == summary['completed_calls'] == len(raw) <= 150
    assert summary['retry'] == summary['new_off_calls'] == summary['new_sun_calls'] == 0
    assert summary['runtime_gold_access'] is summary['project_env_read'] is False
    if summary['complete']:
        assert len(raw) == 150 and not summary['abort_reason']
        assert set(responses) == {s['sample_id'] for s in run.shared.core.samples(150)}
    else:
        assert summary['abort_reason'] and saved['report']['metrics'] is None
    requests = {r['sample_id']: r['body_sha256'] for r in plan['requests']}
    started_ids = set()
    for entry in ledger:
        if entry['state'] == 'started':
            assert entry['sample_id'] not in started_ids
            started_ids.add(entry['sample_id'])
        else:
            assert entry['state'] == 'completed' and entry['sample_id'] in started_ids
    for row in raw:
        sid = row['sample_id']
        assert row['network_call'] == 1
        assert row['request_body_sha256'] == starts[sid]['request_body_sha256'] == requests[sid]
        assert row['response_envelope_sha256'] == finishes[sid]['response_envelope_sha256']
        envelope = json.loads(row['raw_response_envelope_json'])
        assert row['response_envelope'] == envelope
        for field, digest in [('raw_response_content', 'response_sha256'),
                              ('reasoning_content', 'reasoning_sha256'),
                              ('raw_response_envelope_json', 'response_envelope_sha256')]:
            assert run.shared.sha(row[field].encode('utf-8')) == row[digest]
        if row['usage_known']:
            usage = row['usage']
            assert usage == envelope['usage']
            assert row['returned_model'] == envelope['model']
            assert usage['total_tokens'] == usage['prompt_tokens'] + usage['completion_tokens']
            assert usage['completion_tokens'] <= 65536 or summary['abort_reason']
            reason = usage.get('completion_tokens_details', {}).get('reasoning_tokens')
            if reason is not None:
                assert 0 <= reason <= usage['completion_tokens']
        if row['request_status'] == 'ok':
            assert row['http_status'] == 200 and row['finish_reason'] == 'stop'
            assert row['raw_response_content'].strip()
    gate = summary['budget_gate']
    assert gate['calls_made'] == len(raw)
    assert gate['input_tokens'] == sum(r['budget_usage']['prompt_tokens'] for r in raw)
    assert gate['output_tokens'] == sum(r['budget_usage']['completion_tokens'] for r in raw)
    assert gate['missing_usage_calls'] == sum(not r['usage_known'] for r in raw)
    assert gate['cost_usd'] == pytest.approx((gate['input_tokens'] * 1.32 + gate['output_tokens'] * 3.96) / 1e6)
    assert summary['truncated_calls'] == sum(r['finish_reason'] == 'length' for r in raw)
    assert summary['empty_final_calls'] == sum(not r['raw_response_content'].strip() for r in raw)
    if summary['complete']:
        assert gate['input_tokens'] <= plan['budget']['input_token_cap']
        assert gate['output_tokens'] <= plan['budget']['output_token_cap']
        assert gate['cost_usd'] <= plan['budget']['usd_cost_cap']


def test_predictions_and_all_four_evaluations_reproduce_with_fixed_150_denominator(saved):
    report = saved['report']
    if not report['execution']['complete']:
        assert report['arms'] == {} and report['metrics'] is None
        assert not (run.OUT / 'thinking_on_predictions.json').exists()
        return
    samples = run.shared.core.samples(150)
    mapping = {s['sample_id']: s for s in samples}
    raw_by_id = {r['sample_id']: r for r in saved['raw']}
    ordered = [raw_by_id[s['sample_id']] for s in samples]
    predictions = run.shared.predictions_from_raw(ordered, mapping)
    assert normalized(predictions) == run.shared.read_json(run.OUT / 'thinking_on_predictions.json')['records']
    for row, prediction in zip(ordered, predictions):
        if row['request_status'] != 'ok':
            assert prediction['request_status'] == 'failed' and prediction['record'] == {}
    gold = run.shared.read_json(run.shared.core.FORMAL_GOLD)
    for arm, rows in {'thinking_on': predictions, **run.shared.baselines()}.items():
        evaluation = run.shared.core.evaluate_coarse(gold, run.shared.core.attempt_rows(rows), method_id=arm)
        assert normalized(evaluation) == run.shared.read_json(run.OUT / (arm + '_evaluation.json'))
        reported = report['arms'][arm]
        assert reported['denominator'] == 150
        assert reported['new_api_calls'] == (150 if arm == 'thinking_on' else 0)
        assert reported['failed_count'] == evaluation['failed_count']
        assert reported['overall'] == evaluation['coarse_five_field_micro']
        assert reported['per_field'] == evaluation['five_fields']
        assert reported['modality_macro_f1'] == evaluation['modality_labels']['macro_f1']
    main = run.shared.read_json(ROOT / 'outputs/reports/stage2_table1_paper_final_v1.json')
    for arm, key in [('off_formal', 'direct_llm'), ('sun', 'sun_rule_only')]:
        assert report['arms'][arm]['overall']['f1'] == main['arms'][key]['overall_pooled_five_span_fields']['f1']
    on = report['arms']['thinking_on']['overall']['f1']
    assert report['metrics']['thinking_on_f1'] == on
    assert report['metrics']['delta_vs_formal_off_pp'] == pytest.approx(100 * (on - report['arms']['off_formal']['overall']['f1']))
    assert report['metrics']['delta_vs_0813_off_pp'] == pytest.approx(100 * (on - report['arms']['off_0813']['overall']['f1']))


def test_reasoning_final_distributions_historical_ratio_and_public_price_estimates(saved):
    report, raw = saved['report'], saved['raw']
    known = [r['usage'] for r in raw if r['usage_known']]
    cost = report['cost']
    inp = sum(u['prompt_tokens'] for u in known)
    generated = sum(u['completion_tokens'] for u in known)
    hit = sum(u.get('prompt_cache_hit_tokens', u.get('prompt_tokens_details', {}).get('cached_tokens', 0)) for u in known)
    assert cost['known_usage_calls'] == len(known)
    assert cost['input_tokens'] == inp and cost['output_tokens_including_reasoning'] == generated
    assert cost['cache_hit_input_tokens'] == hit and 0 <= hit <= inp
    assert cost['peak_no_cache_estimate_usd'] == pytest.approx((inp * 1.32 + generated * 3.96) / 1e6)
    peak = ((inp - hit) * 1.32 + hit * .044 + generated * 3.96) / 1e6
    assert cost['peak_reported_cache_estimate_usd'] == pytest.approx(peak)
    assert cost['off_peak_reported_cache_estimate_usd'] == pytest.approx(peak / 2)
    assert cost['account_deduction_verified'] is False
    if not report['execution']['complete']:
        return
    diagnostics = run.shared.read_json(run.OUT / 'response_diagnostics.json')
    assert len(diagnostics) == 150 and len({d['sample_id'] for d in diagnostics}) == 150
    by_id = {r['sample_id']: r for r in raw}
    for d in diagnostics:
        assert d == dict(run.transport.measurements(by_id[d['sample_id']]), sample_id=d['sample_id'])
        if d['exact_token_breakdown_known']:
            assert d['reasoning_tokens'] + d['final_answer_tokens'] == d['generated_tokens_total']
    for field, stat in report['token_statistics'].items():
        values = [d[field] for d in diagnostics if type(d[field]) is int]
        if not values:
            assert stat is None
            continue
        ordered = sorted(values)
        assert stat == {'count': len(values), 'total': sum(values), 'mean': statistics.mean(values),
                        'median': statistics.median(values), 'p90_nearest_rank': ordered[math.ceil(.9 * len(values)) - 1],
                        'max': max(values)}
    off = run.shared.core._read_jsonl(run.shared.OFF_0813_ROOT / 'raw_responses.jsonl')
    historical = report['historical_off_0813_output_statistics']
    off_total = sum(r['usage']['completion_tokens'] for r in off)
    assert historical['count'] == len(off) == 150 and historical['total'] == off_total
    assert report['generated_token_ratio_vs_0813_off'] == pytest.approx(generated / off_total)
