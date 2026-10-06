"""Offline validation of the saved one-case token measurement and Git bytes."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_s2_thinking_single_high_v1 as run


def test_manifest_sources_and_artifacts_are_unchanged():
    manifest = run.previous.read_json(run.OUT / 'run_manifest.json')
    assert manifest['actual_calls'] == 1 and manifest['retry'] == 0
    for path, digest in manifest['source_bindings'].items():
        assert run.previous.sha_file(ROOT / path) == digest, path
    for name, digest in manifest['artifacts'].items():
        assert run.previous.sha_file(run.OUT / name) == digest, name
    run.verify(run.previous.read_json(run.OUT / 'plan.json'), True)


def test_saved_response_ledger_and_exact_token_measurement():
    plan = run.previous.read_json(run.OUT / 'plan.json')
    ledger = run.previous.core._read_jsonl(run.OUT / 'calls_ledger.jsonl')
    raw = run.previous.core._read_jsonl(run.OUT / 'raw_responses.jsonl')
    assert len(raw) == 1 and [r['state'] for r in ledger] == ['started', 'completed']
    assert {r['sample_id'] for r in ledger + raw} == {run.SAMPLE_ID}
    row = raw[0]
    assert row['network_call'] == 1
    assert row['request_body_sha256'] == ledger[0]['request_body_sha256'] == plan['request_body_sha256']
    assert row['response_envelope_sha256'] == ledger[1]['response_envelope_sha256']
    assert row['response_envelope'] == json.loads(row['raw_response_envelope_json'])
    for text_field, hash_field in [('raw_response_content', 'response_sha256'),
                                   ('reasoning_content', 'reasoning_sha256'),
                                   ('raw_response_envelope_json', 'response_envelope_sha256')]:
        assert run.previous.sha(row[text_field].encode('utf-8')) == row[hash_field]
    report = run.previous.read_json(run.OUT / 'result.json')
    assert report['measurements'] == run.measurements(row)
    assert report == run.previous.read_json(Path(str(run.REPORT) + '.json'))
    assert report['actual_calls'] == 1 and report['retry'] == 0
    assert report['new_off_calls'] == report['new_sun_calls'] == 0
    assert report['performance_metrics'] is None
    if row['usage_known']:
        u = row['usage']
        assert u['completion_tokens'] <= plan['provider_max_tokens']
        assert u['total_tokens'] == u['prompt_tokens'] + u['completion_tokens']
        reasoning = u.get('completion_tokens_details', {}).get('reasoning_tokens')
        if reasoning is not None:
            assert 0 <= reasoning <= u['completion_tokens']
            assert report['measurements']['final_answer_tokens'] + reasoning == u['completion_tokens']
    if report['measurements']['natural_completion']:
        assert row['finish_reason'] == 'stop' and row['raw_response_content'].strip()
        assert report['status'] == 'complete' and row['returned_model'] == run.previous.MODEL
    else:
        assert report['status'] == 'failed'


def test_final_answer_validation_is_reproducible_without_gold():
    row = run.previous.core._read_jsonl(run.OUT / 'raw_responses.jsonl')[0]
    report = run.previous.read_json(run.OUT / 'result.json')
    if row['request_status'] == 'ok':
        prediction = run.previous.predictions_from_raw([row], {run.SAMPLE_ID: run.sample()})[0]
        normalized = json.loads(json.dumps(prediction, ensure_ascii=False))
        assert normalized == run.previous.read_json(run.OUT / 'final_prediction.json')
        assert report['final_json_canonical_valid'] == (prediction['request_status'] == 'ok')
    else:
        assert not report['final_json_canonical_valid']


def test_git_checkout_preserves_all_manifest_bytes():
    manifest = run.previous.read_json(run.OUT / 'run_manifest.json')
    bindings = dict(manifest['source_bindings'])
    bindings.update({(run.OUT / name).relative_to(ROOT).as_posix(): digest
                     for name, digest in manifest['artifacts'].items()})
    for path, digest in bindings.items():
        git_path = 'formal_experiment/' + path
        raw = subprocess.check_output(['git', 'cat-file', '--filters', '--path=' + git_path,
                                       ':' + git_path], cwd=ROOT.parent)
        assert run.previous.sha(raw) == digest, path
