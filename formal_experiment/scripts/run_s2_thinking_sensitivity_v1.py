"""Authorized 150-call thinking sensitivity run; historical off arms are reused.

All runtime inputs are frozen and Gold-blind. The first of the 150 requests
checks the response contract; it is retained in the evaluation, never resent.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
for directory in (ROOT / 'src', ROOT / 'scripts'):
    sys.path.insert(0, str(directory))
import run_sep_c3_modular_ablation_v1 as core
from bpc_hybrid.prompt_loader import load_prompt
from bpc_hybrid.stage2_canonical import validate_canonical

RUN_ID = 'thinking_on_20261006_v1'
TASK = 'S2-THINKING-SENSITIVITY-V1'
PROMPT = 'direct_llm_sun_record_prompt_v6_d1r1_2026_08_05'
AUTH_PATH = ROOT / 'configs/authorization/s2_thinking_20261006_v1.json'
RUN_ROOT = ROOT / 'outputs/evidence/s2_thinking_sensitivity_v1'
REPORT_ROOT = ROOT / 'outputs/reports'
ENDPOINT = 'https://api.deepseek.com/v1/chat/completions'
MODEL = 'deepseek-v4-pro'
MAX_CALLS = 150
MAX_TOKENS = 16384
MAX_WORKERS = 6
TIMEOUT = 600
R3_ROOT = ROOT / 'outputs/development/s27_d1_v6_r3_clean_rerun_150_hist56d_v1'
OFF_0813_ROOT = ROOT / 'outputs/development/barrientos_ablation_suite_v2/D-full-0813/repeat-01'
FORMAL_OFF = ROOT / 'data/predictions/direct_llm_formal_arm_v1/predictions.json'
SUN_OFF = ROOT / 'data/predictions/b0_formal_arm_v1/predictions.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    return sha(Path(path).read_bytes())


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path, value):
    core._write_json(Path(path), value)


def body_for(sample):
    prompt = load_prompt(PROMPT)
    raw = prompt.raw_text
    examples = raw[raw.index('## Examples'):raw.index('## Notes')].strip()
    user = prompt.user_prompt_template.format(sample_id=sample['sample_id'],
        source_id=sample['sample_id'], source_text=sample['text'], few_shot_block=examples)
    return {'model': MODEL, 'messages': [{'role': 'system', 'content': prompt.system_prompt},
        {'role': 'user', 'content': user}], 'temperature': 0.0, 'top_p': 1.0,
        'max_tokens': MAX_TOKENS, 'stream': False, 'thinking': {'type': 'enabled'},
        'reasoning_effort': 'high'}


def request_bytes(sample):
    return json.dumps(body_for(sample)).encode('utf-8')


def baselines():
    samples = core.samples(150)
    expected = {s['sample_id']: s['text'] for s in samples}
    result = {'off_formal': read_json(FORMAL_OFF)['records'],
              'sun': read_json(SUN_OFF)['records'],
              'off_0813': core._read_jsonl(OFF_0813_ROOT / 'canonical_predictions.jsonl')}
    for name, rows in result.items():
        if len(rows) != 150 or {r['sample_id'] for r in rows} != set(expected):
            raise ValueError('Historical baseline membership mismatch: ' + name)
        for row in rows:
            if row.get('request_status') != 'ok' or (name != 'off_0813' and row['record'].get('source_text') != expected[row['sample_id']]):
                raise ValueError('Historical baseline source text mismatch: ' + name)
    old_input = core._read_jsonl(ROOT / 'outputs/development/s27_d1_pilot_20_hist56d_v1/input_150_hist56d_v1.jsonl')
    if {r['sample_id']: r['text'] for r in old_input} != expected:
        raise ValueError('Formal input differs from historical R3 input.')
    r3_manifest = read_json(R3_ROOT / 'manifest.json')
    if r3_manifest['prompts'][0]['sha256'] != load_prompt(PROMPT).sha256:
        raise ValueError('Historical R3 prompt mismatch.')
    off_manifest = read_json(OFF_0813_ROOT / 'manifest.json')
    if off_manifest['prompt_sha256'] != sha_file(load_prompt(PROMPT).path):
        raise ValueError('0813 baseline prompt mismatch.')
    raw = core._read_jsonl(OFF_0813_ROOT / 'raw_responses.jsonl')
    raw_map = {r['sample_id']: r for r in raw}
    if len(raw) != 150 or set(raw_map) != set(expected):
        raise ValueError('0813 raw baseline incomplete.')
    for sample in samples:
        row = raw_map[sample['sample_id']]
        body = body_for(sample)
        # Historical fingerprint uses sorted, UTF-8 JSON and the disabled policy.
        old_body = core.base._req_body(body['messages'][0]['content'], body['messages'][1]['content'])
        digest = sha(json.dumps(old_body, ensure_ascii=False, sort_keys=True).encode('utf-8'))
        if (digest != row['request_body_sha256'] or row['returned_model'] != MODEL
                or sha(row['raw_response_content'].encode('utf-8')) != row['response_sha256']):
            raise ValueError('0813 historical message/response fingerprint mismatch.')
    return result


def source_paths():
    return [Path(__file__), AUTH_PATH, core.ESTG_INPUT, core.FORMAL_GOLD,
        load_prompt(PROMPT).path, FORMAL_OFF, SUN_OFF, R3_ROOT / 'manifest.json',
        ROOT / 'outputs/development/s27_d1_pilot_20_hist56d_v1/input_150_hist56d_v1.jsonl',
        OFF_0813_ROOT / 'manifest.json', OFF_0813_ROOT / 'raw_responses.jsonl',
        OFF_0813_ROOT / 'canonical_predictions.jsonl',
        ROOT / 'outputs/reports/stage2_table1_paper_final_v1.json',
        ROOT / 'outputs/reports/stage2_table2_prompt_ablation_paper_final_v2.json',
        ROOT / 'scripts/run_sep_c3_modular_ablation_v1.py',
        ROOT / 'scripts/run_barrientos_ablation_suite_v2.py',
        ROOT / 'configs/schemas/stage2_prediction.schema.json',
        *[ROOT / 'src/bpc_hybrid' / name for name in ('prompt_loader.py',
            'd1_schema_adapter.py', 'd1_span_canonicalizer.py', 'stage2_canonical.py',
            'sep_c3_modular_evaluation.py', 'formal_stage2_evaluation.py',
            'g04_coarse_view.py', 'stage2_sun_literal_overlap.py')]]


def prepare():
    out = RUN_ROOT / RUN_ID
    if out.exists():
        raise ValueError('Run already prepared; use the saved plan, never overwrite it.')
    auth = read_json(AUTH_PATH)
    if auth.get('authorized') is not True or auth.get('run_id') != RUN_ID or auth.get('max_calls') != MAX_CALLS or auth.get('user_statement') != '授权运行':
        raise ValueError('This run requires its own saved 150-call user authorization.')
    historical = baselines()  # no Gold semantics loaded; request/input consistency only
    sample_texts = {s['sample_id']: s['text'] for s in core.samples(150)}
    secondary_source_mismatches = [r['sample_id'] for r in historical['off_0813']
        if r['record'].get('source_text') != sample_texts[r['sample_id']]]
    requests = [{'sample_id': s['sample_id'], 'body_sha256': sha(request_bytes(s)),
                 'estimated_input_tokens': math.ceil(len(request_bytes(s)) / 3)}
                for s in core.samples(150)]
    input_cap = math.ceil(sum(r['estimated_input_tokens'] for r in requests) * 1.5)
    token_max_cost = (input_cap * 1.32 + MAX_CALLS * MAX_TOKENS * 3.96) / 1e6
    if token_max_cost * 1.2 > auth['max_usd']:
        raise ValueError('Maximum token reservation exceeds the recorded USD guardrail.')
    plan = {'schema_version': 's2_thinking_sensitivity_plan@1.0.0', 'run_id': RUN_ID,
        'pipeline_task': TASK, 'prepared_at_utc': datetime.now(timezone.utc).isoformat(),
        'prepared_git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'claim_scope': 'development_retrospective_fixed_estg150', 'authorization': auth,
        'model': {'id': MODEL, 'current_documented_release': 'DeepSeek-V4-Pro-0813', 'endpoint': ENDPOINT},
        'generation': {'thinking': 'enabled', 'reasoning_effort': 'high',
            'temperature_sent': 0.0, 'temperature_effective': 'ignored_by_provider_in_thinking_mode',
            'top_p': 1.0, 'max_tokens_reasoning_plus_final': MAX_TOKENS,
            'historical_off_max_tokens': 4096, 'stream': False, 'response_format': None,
            'timeout_seconds': TIMEOUT, 'retry': 0, 'max_workers': MAX_WORKERS},
        'budget': {'call_cap': MAX_CALLS, 'input_token_cap': input_cap,
            'output_token_cap': MAX_CALLS * MAX_TOKENS, 'usd_cost_cap': auth['max_usd'],
            'maximum_token_cost_usd': token_max_cost,
            'price_snapshot': {'currency': 'USD', 'input_cache_miss_per_million': 1.32,
                'input_cache_hit_per_million': 0.044, 'output_per_million': 3.96,
                'off_peak_multiplier': 0.5, 'verified_date_local': '2026-10-06',
                'source_url': 'https://api-docs.deepseek.com/quick_start/pricing/'},
            'missing_usage_policy': 'reserve estimated input/full generated-token cap and stop; no resend'},
        'requests': requests, 'samples': 150, 'new_off_calls': 0, 'new_sun_calls': 0,
        'runtime_gold_access': False, 'project_env_read': False,
        'secondary_historical_payload_source_text_mismatches': secondary_source_mismatches,
        'primary_metric': 'coarse_five_field_micro_f1', 'modality_reported_separately': True,
        'postprocessing': 'shared historical parser/adapter + explicit legacy canonicalizer + canonical validation',
        'source_bindings': {p.relative_to(ROOT).as_posix(): sha_file(p) for p in source_paths()},
        'limitations': ['single new repeat; historical off reuse, not contemporaneous randomized mode comparison',
            'formal off R3 was run before 0813 release; current alias can represent a changed model',
            'existing off_0813 is an additional same documented release reference; server drift remains possible',
            'off_0813 preserves one historical model-emitted source_text mismatch (estg_000092); all 150 sent request fingerprints match input; historical payloads are never silently corrected',
            'on generation ceiling is 16384 versus historical 4096; measures configured operating-mode sensitivity, not equal-budget causal effect',
            'temperature=0 is ignored in thinking mode; no claim of deterministic generation',
            'no independent unseen test and no replacement of frozen main Table 1/Table 2']}
    write_json(out / 'plan.json', plan)
    write_json(REPORT_ROOT / ('s2_thinking_' + RUN_ID + '_preflight.json'), plan)
    print(json.dumps({'run_id': RUN_ID, 'planned_calls': MAX_CALLS, 'new_off_calls': 0,
        'maximum_token_cost_usd': round(token_max_cost, 4), 'usd_guardrail': auth['max_usd'], 'network_calls': 0}), flush=True)
    return plan


def verify_plan(plan, allow_llm):
    if not allow_llm or plan.get('run_id') != RUN_ID or plan.get('authorization') != read_json(AUTH_PATH):
        raise ValueError('Saved authorization and explicit --allow-llm are required.')
    if plan['authorization'].get('authorized') is not True or plan['authorization']['max_calls'] != MAX_CALLS:
        raise ValueError('Authorization disabled or call cap changed.')
    if set(plan['source_bindings']) != {p.relative_to(ROOT).as_posix() for p in source_paths()}:
        raise ValueError('Source binding set changed.')
    for path, digest in plan['source_bindings'].items():
        if sha_file(ROOT / path) != digest:
            raise ValueError('Frozen source changed: ' + path)
    expected = [{'sample_id': s['sample_id'], 'body_sha256': sha(request_bytes(s)),
        'estimated_input_tokens': math.ceil(len(request_bytes(s)) / 3)} for s in core.samples(150)]
    if plan['requests'] != expected or len(expected) != MAX_CALLS or len({r['sample_id'] for r in expected}) != MAX_CALLS:
        raise ValueError('Frozen 150-request set changed.')
    cap = math.ceil(sum(r['estimated_input_tokens'] for r in expected) * 1.5)
    if (plan['budget']['call_cap'] != MAX_CALLS or plan['budget']['input_token_cap'] != cap
            or plan['budget']['output_token_cap'] != MAX_CALLS * MAX_TOKENS
            or plan['budget']['usd_cost_cap'] != plan['authorization']['max_usd']
            or plan['budget']['price_snapshot']['input_cache_miss_per_million'] != 1.32
            or plan['budget']['price_snapshot']['output_per_million'] != 3.96):
        raise ValueError('Budget binding changed.')


def process_key():
    key = os.environ.get('BPC_HYBRID_DeepSeek_API_KEY') or os.environ.get('DEEPSEEK_API_KEY')
    if not key and (os.environ.get('BPC_HYBRID_LLM_MODEL') == MODEL or os.environ.get('BPC_HYBRID_LLM_BASE_URL', '').startswith('https://api.deepseek.com')):
        key = os.environ.get('BPC_HYBRID_LLM_API_KEY')
    if not key:
        raise ValueError('No process-environment DeepSeek credential; .env is never read.')
    return key


def response_row(sample, body, raw_body, status, seconds, key=''):
    captured = raw_body.replace(key.encode('utf-8'), b'[REDACTED]') if key else raw_body
    try:
        envelope = json.loads(captured)
    except (ValueError, UnicodeError):
        envelope = {}
    choice = (envelope.get('choices') or [{}])[0]
    message = choice.get('message') or {}
    content = message.get('content') or ''
    reasoning = message.get('reasoning_content') or ''
    usage = envelope.get('usage') or {}
    return {'sample_id': sample['sample_id'], 'request_id': envelope.get('id') or sample['sample_id'],
        'request_status': 'ok' if status == 200 and isinstance(content, str) and content.strip() and choice.get('finish_reason') == 'stop' else 'failed',
        'http_status': status, 'request_body_sha256': sha(body),
        'raw_response_content': content, 'response_sha256': sha(content.encode('utf-8')),
        'reasoning_content': reasoning, 'reasoning_sha256': sha(reasoning.encode('utf-8')),
        'response_envelope': envelope, 'raw_response_envelope_json': captured.decode('utf-8', errors='replace'),
        'response_envelope_sha256': sha(captured),
        'captured_envelope_redacted': captured != raw_body, 'returned_model': envelope.get('model'),
        'system_fingerprint': envelope.get('system_fingerprint'), 'finish_reason': choice.get('finish_reason'),
        'usage': usage, 'runtime_seconds': round(seconds, 3), 'network_call': 1,
        'usage_known': all(type(usage.get(k)) is int and usage[k] >= 0 for k in ('prompt_tokens', 'completion_tokens')),
        'completed_at_utc': datetime.now(timezone.utc).isoformat()}


def send_once(sample, body, key):
    started = time.monotonic()
    request = urllib.request.Request(ENDPOINT, data=body, method='POST',
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json',
                 'User-Agent': 'LLM4BPC-authorized-experiment/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            raw = response.read()
            status = response.status
        return response_row(sample, body, raw, status, time.monotonic() - started, key)
    except Exception as exc:
        row = response_row(sample, body, b'{}', getattr(exc, 'code', None), time.monotonic() - started)
        row['error'] = type(exc).__name__ + ': transport failed; details redacted'
        return row


def restore(out, plan):
    summary_path = out / 'execution_summary.json'
    if summary_path.exists():
        summary = read_json(summary_path)
        if summary.get('complete') or summary.get('abort_reason'):
            raise ValueError('Completed/aborted run cannot execute again; no automatic resend.')
    raw = core._read_jsonl(out / 'raw_responses.jsonl')
    ledger = core._read_jsonl(out / 'calls_ledger.jsonl')
    mapping = {r['sample_id']: r for r in raw}
    request_map = {r['sample_id']: r for r in plan['requests']}
    if len(mapping) != len(raw) or len(raw) > MAX_CALLS:
        raise ValueError('Duplicate/excess persisted requests.')
    starts = [r for r in ledger if r['state'] == 'started']
    if len({r['sample_id'] for r in starts}) != len(starts) or any(r['sample_id'] not in mapping for r in starts):
        raise ValueError('In-doubt/duplicate request; manual resolution needed, never resend.')
    if set(mapping) != {r['sample_id'] for r in starts}:
        raise ValueError('Response has no matching started ledger.')
    gate = core.AblationBudgetGate(plan['budget'], MODEL)
    for row in raw:
        if row['sample_id'] not in request_map or row['request_body_sha256'] != request_map[row['sample_id']]['body_sha256'] or row['response_sha256'] != sha(row['raw_response_content'].encode('utf-8')):
            raise ValueError('Persisted response binding changed.')
        if not row['usage_known'] or row['returned_model'] != MODEL:
            raise ValueError('Persisted incomplete usage/model; stop, never resend.')
        gate.record_response(row['budget_usage'], row['returned_model'])
    return raw, gate


def row_abort(row, first=False):
    if not row['usage_known'] or row['returned_model'] != MODEL:
        return 'Transport/usage/model contract failed; no subsequent sends or retries.'
    if first and (row['request_status'] != 'ok' or not row['reasoning_content']):
        return 'First authorized response did not confirm reasoning plus a completed final answer.'
    return None


def execute(plan, out, allow_llm):
    verify_plan(plan, allow_llm)
    raw, gate = restore(out, plan)
    key = process_key()
    samples = [s for s in core.samples(150) if s['sample_id'] not in {r['sample_id'] for r in raw}]
    request_map = {r['sample_id']: r for r in plan['requests']}
    started = time.monotonic()
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--short', '--', 'formal_experiment'], cwd=ROOT, text=True, encoding='utf-8').splitlines()
    abort = None
    batches = ([samples[:1]] + [samples[i:i + MAX_WORKERS] for i in range(1, len(samples), MAX_WORKERS)]) if not raw else [samples[i:i + MAX_WORKERS] for i in range(0, len(samples), MAX_WORKERS)]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for batch in batches:
            if not batch:
                continue
            if gate.calls_made + len(batch) > MAX_CALLS:
                raise ValueError('Call cap would be exceeded.')
            gate.check_before_send(sum(request_map[s['sample_id']]['estimated_input_tokens'] for s in batch), len(batch) * MAX_TOKENS)
            futures = []
            for sample in batch:
                body = request_bytes(sample)
                if sha(body) != request_map[sample['sample_id']]['body_sha256']:
                    raise ValueError('Actual request differs from frozen preflight.')
                core._append_jsonl(out / 'calls_ledger.jsonl', {'sample_id': sample['sample_id'],
                    'state': 'started', 'request_body_sha256': sha(body), 'started_at_utc': datetime.now(timezone.utc).isoformat()})
                futures.append((sample, pool.submit(send_once, sample, body, key)))
            for sample, future in futures:
                row = future.result()
                row['budget_usage'] = row['usage'] if row['usage_known'] else {'prompt_tokens': request_map[sample['sample_id']]['estimated_input_tokens'], 'completion_tokens': MAX_TOKENS}
                core._append_jsonl(out / 'raw_responses.jsonl', row)
                core._append_jsonl(out / 'calls_ledger.jsonl', {'sample_id': sample['sample_id'], 'state': 'completed', 'response_sha256': row['response_sha256']})
                raw.append(row)
                try:
                    gate.record_response(row['budget_usage'], row['returned_model'])
                except core.SepC3Error as exc:
                    abort = str(exc)
                abort = abort or row_abort(row, first=len(raw) == 1)
            summary = {'run_id': RUN_ID, 'complete': len(raw) == MAX_CALLS and not abort,
                'actual_calls': len(raw), 'planned_calls': MAX_CALLS, 'new_off_calls': 0, 'new_sun_calls': 0,
                'retry': 0, 'abort_reason': abort, 'budget_gate': gate.to_dict(),
                'execution_git_commit': commit, 'execution_dirty_paths': dirty,
                'runtime_seconds_this_invocation': round(time.monotonic() - started, 3),
                'runtime_gold_access': False, 'project_env_read': False,
                'reasoning_present_calls': sum(bool(r['reasoning_content']) for r in raw),
                'truncated_calls': sum(r['finish_reason'] == 'length' for r in raw)}
            write_json(out / 'execution_summary.json', summary)
            print(json.dumps({'completed': len(raw), 'planned': MAX_CALLS,
                'estimated_peak_no_cache_usd': gate.cost_usd, 'abort_reason': abort}), flush=True)
            if abort:
                break
    return summarize(plan, out)


def predictions_from_raw(raw, row_map):
    rows = []
    for response in raw:
        if response['request_status'] != 'ok':
            rows.append({'sample_id': response['sample_id'], 'request_status': 'failed', 'record': {}, 'error': 'final_answer_or_transport_failure'})
            continue
        parsed = core.base.parse_same_response(response, 'thinking_on', row_map[response['sample_id']]['text'])
        pred = core.base._prediction_row(parsed, 'thinking_on')
        if pred['request_status'] == 'ok':
            check = validate_canonical(pred['record'])
            if not (check.schema_valid and check.cross_field_valid):
                pred = {'sample_id': pred['sample_id'], 'request_status': 'failed', 'record': {}, 'error': 'canonical_validation_failed'}
        rows.append(pred)
    return rows


def summarize(plan, out):
    verify_plan(plan, True)
    summary = read_json(out / 'execution_summary.json')
    report = {'schema_version': 's2_thinking_sensitivity_result@1.0.0', 'run_id': RUN_ID,
        'pipeline_task': TASK, 'status': 'complete' if summary['complete'] else 'partial',
        'claim_scope': plan['claim_scope'], 'primary_metric': plan['primary_metric'],
        'execution': summary, 'model': plan['model'], 'generation': plan['generation'],
        'limitations': plan['limitations'], 'arms': {}, 'metrics': None}
    if summary['complete']:
        raw = core._read_jsonl(out / 'raw_responses.jsonl')
        if len(raw) != MAX_CALLS or len({r['sample_id'] for r in raw}) != MAX_CALLS:
            raise ValueError('Final 150 response set is incomplete/duplicated.')
        row_map = {s['sample_id']: s for s in core.samples(150)}
        predictions = predictions_from_raw(raw, row_map)
        core._write_json(out / 'thinking_on_predictions.json', {'records': predictions})
        # Semantic Gold is read only after every new prediction has been saved.
        gold = read_json(core.FORMAL_GOLD)
        arms = {'thinking_on': predictions, **baselines()}
        for name, rows in arms.items():
            evaluation = core.evaluate_coarse(gold, core.attempt_rows(rows), method_id=name)
            write_json(out / (name + '_evaluation.json'), evaluation)
            fields = evaluation['coarse_five_field_micro']
            report['arms'][name] = {'historical_reuse': name != 'thinking_on',
                'new_api_calls': MAX_CALLS if name == 'thinking_on' else 0,
                'denominator': 150, 'overall': fields, 'per_field': evaluation['five_fields'],
                'modality_macro_f1': evaluation['modality_labels']['macro_f1'], 'failed_count': evaluation['failed_count']}
        main = read_json(ROOT / 'outputs/reports/stage2_table1_paper_final_v1.json')
        for name, source_arm in [('off_formal', 'direct_llm'), ('sun', 'sun_rule_only')]:
            if report['arms'][name]['overall']['f1'] != main['arms'][source_arm]['overall_pooled_five_span_fields']['f1']:
                raise ValueError('Historical evaluation no longer matches frozen Table 1.')
        report['metrics'] = {'thinking_on_f1': report['arms']['thinking_on']['overall']['f1'],
            'delta_vs_formal_off_pp': 100 * (report['arms']['thinking_on']['overall']['f1'] - report['arms']['off_formal']['overall']['f1']),
            'delta_vs_0813_off_pp': 100 * (report['arms']['thinking_on']['overall']['f1'] - report['arms']['off_0813']['overall']['f1'])}
        hit = sum(r['usage'].get('prompt_cache_hit_tokens', 0) for r in raw)
        input_tokens = summary['budget_gate']['input_tokens']
        output_tokens = summary['budget_gate']['output_tokens']
        peak_with_cache = ((input_tokens - hit) * 1.32 + hit * 0.044 + output_tokens * 3.96) / 1e6
        report['cost'] = {'input_tokens': input_tokens, 'output_tokens_including_reasoning': output_tokens,
            'cache_hit_input_tokens': hit, 'peak_no_cache_estimate_usd': summary['budget_gate']['cost_usd'],
            'peak_with_reported_cache_estimate_usd': peak_with_cache,
            'off_peak_with_reported_cache_estimate_usd': peak_with_cache * 0.5,
            'account_deduction_verified': False, 'usd_guardrail': plan['budget']['usd_cost_cap']}
        diagnostics = [{'sample_id': r['sample_id'], 'reasoning_characters': len(r['reasoning_content']),
            'final_answer_characters': len(r['raw_response_content']), 'finish_reason': r['finish_reason'],
            'runtime_seconds': r['runtime_seconds'], 'usage': r['usage']} for r in raw]
        write_json(out / 'response_diagnostics.json', diagnostics)
    write_json(out / 'result.json', report)
    bindings = {p.name: sha_file(p) for p in out.iterdir() if p.is_file() and p.name != 'run_manifest.json'}
    write_json(out / 'run_manifest.json', {'schema_version': 's2_thinking_run_manifest@1.0.0',
        'run_id': RUN_ID, 'status': report['status'], 'execution': summary,
        'claim_scope': plan['claim_scope'], 'source_bindings': plan['source_bindings'], 'artifacts': bindings})
    write_json(REPORT_ROOT / ('s2_thinking_' + RUN_ID + '.json'), report)
    lines = ['# 开启思考敏感性对比（固定 EStG-150）', '',
        '状态：' + report['status'] + '；新调用 ' + str(summary['actual_calls']) + '/150；关闭组和 Sun 新调用均为 0。', '',
        '主指标：coarse 五字段 pooled micro-F1；modality 独立报告。', '']
    if report['metrics']:
        lines += ['| 条件 | 新调用 | Overall F1 | Modality macro-F1 | 失败/150 |', '|---|---:|---:|---:|---:|']
        for name, arm in report['arms'].items():
            lines.append(f"| {name} | {arm['new_api_calls']} | {arm['overall']['f1']:.4f} | {arm['modality_macro_f1']:.4f} | {arm['failed_count']} |")
        lines += ['', f"相对主表关闭组：{report['metrics']['delta_vs_formal_off_pp']:+.4f} 个百分点；相对已有0813关闭组：{report['metrics']['delta_vs_0813_off_pp']:+.4f} 个百分点。",
            '', '费用为返回用量与公开单价估算，未查询账户实扣：', json.dumps(report['cost'], ensure_ascii=False), '']
    lines += ['比较边界：', *['- ' + item for item in report['limitations']], '',
        '完整请求绑定、原始响应（推理与最终答案分列）、调用账本、预测、评价和 manifest 保存于：', out.relative_to(ROOT).as_posix(), '']
    (REPORT_ROOT / ('s2_thinking_' + RUN_ID + '.md')).write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'status': report['status'], 'actual_calls': summary['actual_calls'], 'metrics': report['metrics']}, ensure_ascii=False), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--allow-llm', action='store_true')
    parser.add_argument('--summarize', action='store_true')
    parser.add_argument('--max-calls', type=int, default=150)
    args = parser.parse_args()
    if args.max_calls != MAX_CALLS:
        raise ValueError('This authorization fixes --max-calls 150.')
    out = RUN_ROOT / RUN_ID
    if args.prepare:
        if args.execute or args.summarize:
            raise ValueError('Preparation is an independent zero-API checkpoint.')
        prepare()
    elif args.execute:
        execute(read_json(out / 'plan.json'), out, args.allow_llm)
    elif args.summarize:
        summarize(read_json(out / 'plan.json'), out)
    else:
        print('Default is zero API. Use --prepare, --execute --allow-llm, or --summarize.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
