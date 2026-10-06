"""Authorized A/B experiment with a reused historical v6 baseline; zero retries."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
for directory in (ROOT / 'src', ROOT / 'scripts'):
    sys.path.insert(0, str(directory))
import run_sep_c3_modular_ablation_v1 as core
from bpc_hybrid.prompt_loader import load_prompt
from bpc_hybrid.llm_client import OpenAICompatibleRequestBuilder

ARMS = {
    'A': 'simplification_v1/direct_llm_json_light_v1',
    'B': 'simplification_v1/direct_llm_json_semantic_light_v1',
}
RUN_ID = 'comparison_20261006_v2'
BASELINE_PROMPT = 'direct_llm_sun_record_prompt_v6_d1r1_2026_08_05'
BASELINE_ROOT = ROOT / 'outputs/development/barrientos_ablation_suite_v2/D-full-0813/repeat-01'
AUTH_PATH = ROOT / 'configs/authorization/s2_prompt_simplification_20261006_v2.json'
MAX_WORKERS = 6
USER_DECISION = '授权，进行数据运行，快点'
RUN_ROOT = ROOT / 'outputs/development/s2_prompt_simplification_v1'
POLICY = core.H1RequestPolicy(stream=False, thinking={'type': 'disabled'}, response_format=None)
KEYS = {'schema_version', 'sample_id', 'source_id', 'source_text', 'clauses', 'method', 'validation', 'unsupported_or_ambiguous'}


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    return sha_bytes(Path(path).read_bytes())


def write_json(path, value):
    core._write_json(Path(path), value)


def config_for(api_key='offline-placeholder'):
    return core.LLMConfig(enabled=True, provider='openai_compatible', model=core.MODEL_ALIAS,
                          api_key=api_key, base_url='https://api.deepseek.com/v1',
                          temperature=0.0, top_p=1.0, max_tokens=4096,
                          seed=None, seed_supported=False, timeout_seconds=180.0)


def render(arm, sample):
    prompt = load_prompt(BASELINE_PROMPT if arm == 'v6' else ARMS[arm])
    raw = prompt.raw_text
    examples = raw[raw.index('## Examples'):raw.index('## Notes')].strip()
    user = prompt.user_prompt_template.format(sample_id=sample['sample_id'],
            source_id=sample['sample_id'], source_text=sample['text'], few_shot_block=examples)
    return prompt.system_prompt, user


def body_for(arm, sample):
    system, user = render(arm, sample)
    body = OpenAICompatibleRequestBuilder(config_for()).build_payload(
        system_prompt=system, user_prompt=user)['body']
    return POLICY.apply_to_body(body)


def binding_paths():
    paths = [core.ESTG_INPUT, core.FORMAL_GOLD, Path(__file__),
             ROOT / 'configs/stage2_evaluator_s210_v3.json',
             ROOT / 'configs/schemas/stage2_prediction.schema.json',
             ROOT / 'scripts/run_sep_c3_modular_ablation_v1.py',
             ROOT / 'scripts/run_barrientos_ablation_suite_v2.py']
    paths += [ROOT / 'src/bpc_hybrid' / name for name in (
        'd1_schema_adapter.py', 'd1_span_canonicalizer.py', 'llm_client.py',
        'h1_transport.py', 'sep_c3_modular_evaluation.py', 'g04_coarse_view.py',
        'formal_stage2_evaluation.py', 'stage2_sun_literal_overlap.py')]
    paths += [load_prompt(name).path for name in [BASELINE_PROMPT, *ARMS.values()]]
    paths += [AUTH_PATH] + [BASELINE_ROOT / n for n in ('manifest.json', 'raw_responses.jsonl', 'canonical_predictions.jsonl', 'evaluation.json')]
    return paths


def baseline_binding():
    rows = core.samples(150)
    raw = core._read_jsonl(BASELINE_ROOT / 'raw_responses.jsonl')
    canonical = core._read_jsonl(BASELINE_ROOT / 'canonical_predictions.jsonl')
    manifest = core._read_json(BASELINE_ROOT / 'manifest.json')
    if len(raw) != 150 or len(canonical) != 150:
        raise ValueError('Historical baseline must contain all 150 samples.')
    by_id = {r['sample_id']: r for r in raw}
    if len(by_id) != 150 or set(by_id) != {r['sample_id'] for r in rows} or {r['sample_id'] for r in canonical} != set(by_id):
        raise ValueError('Historical baseline membership changed.')
    if manifest['prompt_sha256'] != sha_file(load_prompt(BASELINE_PROMPT).path):
        raise ValueError('Historical baseline prompt changed.')
    for sample in rows:
        system, user = render('v6', sample)
        fingerprint = sha_bytes(json.dumps(core.base._req_body(system, user), ensure_ascii=False, sort_keys=True).encode('utf-8'))
        old = by_id[sample['sample_id']]
        if fingerprint != old['request_body_sha256'] or old['returned_model'] != core.MODEL_ALIAS:
            raise ValueError('Historical baseline request/model recipe mismatch.')
        if sha_bytes(old['raw_response_content'].encode('utf-8')) != old['response_sha256']:
            raise ValueError('Historical response hash mismatch.')
    for row in canonical:
        if row['response_sha256'] != by_id[row['sample_id']]['response_sha256']:
            raise ValueError('Historical canonical/response binding mismatch.')
    return {'arm': 'v6', 'source_arm': 'D-full-0813', 'repeat_id': 'repeat-01',
            'source_root': str(BASELINE_ROOT.relative_to(ROOT)).replace('\\', '/'),
            'prompt_name': BASELINE_PROMPT, 'samples': 150, 'new_api_calls': 0,
            'verified_request_fingerprints': 150,
            'historical_estimated_usd': manifest['cost'],
            'comparison_scope': 'historical cross-batch baseline; server changes cannot be excluded'}


def prepare(run_id=RUN_ID):
    if run_id != RUN_ID:
        raise ValueError('Current user authorization covers this one run ID only.')
    out = RUN_ROOT / run_id
    if out.exists():
        raise ValueError('Preparation refuses an existing run directory; use the saved plan.')
    authorization = core._read_json(AUTH_PATH)
    if authorization.get('authorized') is not True or authorization.get('data_transfer_authorized') is not True or authorization.get('run_id') != RUN_ID or authorization.get('user_statement') != USER_DECISION:
        raise ValueError('Current authorization and data transfer approval are required.')
    baseline = baseline_binding()
    rows = core.samples(150)
    prompts = [load_prompt(name) for name in ARMS.values()]
    assert len({p.user_prompt_template for p in prompts}) == 1
    assert len({p.raw_text[p.raw_text.index('## Examples'):p.raw_text.index('## Notes')] for p in prompts}) == 1
    requests = []
    for sample in rows:
        for arm in ARMS:
            body_bytes = json.dumps(body_for(arm, sample)).encode('utf-8')
            requests.append({'arm': arm, 'sample_id': sample['sample_id'],
                             'body_sha256': sha_bytes(body_bytes),
                             'estimated_input_tokens': math.ceil(len(body_bytes) / 3)})
    estimated = sum(r['estimated_input_tokens'] for r in requests)
    input_cap = math.ceil(estimated * 1.5)
    output_cap = 300 * 4096
    usd_cap = math.ceil((input_cap * 1.32 + output_cap * 3.96) / 1e6 * 1.2 * 100) / 100
    if usd_cap > authorization['max_usd']:
        raise ValueError('Computed budget exceeds authorized USD cap.')
    budget = {'planned_calls': 300, 'call_cap': 300, 'input_token_cap': input_cap,
              'output_token_cap': output_cap, 'usd_cost_cap': usd_cap,
              'price_snapshot': {'currency': 'USD', 'input_cache_miss_per_million': 1.32,
                  'output_per_million': 3.96, 'mode_used_for_gate': 'peak_all_input_cache_miss',
                  'verified_date_local': '2026-10-06',
                  'source_url': 'https://api-docs.deepseek.com/quick_start/pricing/',
                  'corroborating_cny_url': 'https://api-docs.deepseek.com/zh-cn/quick_start/pricing/'},
              'estimated_input_tokens': estimated,
              'estimate_policy': 'ceil(serialized request UTF-8 bytes/3); input cap 1.5x; USD cap 1.2x maximum token budget',
              'missing_usage_policy': 'reserve estimated input and full 4096 output; abort further sends; cost remains an upper estimate'}
    preserved = [ROOT / 'outputs/reports' / name for name in (
        'stage2_table1_paper_final_v1.json', 'stage2_table1_paper_final_v1.md',
        'stage2_table2_prompt_ablation_paper_final_v2.json', 'stage2_table2_prompt_ablation_paper_final_v2.md',
        'v6_factorial_ablation_v1.json', 'v6_factorial_ablation_v1.md',
        'sep_c3_modular_ablation_v1.json', 'sep_c3_modular_ablation_v1.md')]
    preserved += [ROOT / 'data/development/human_review/stage1_gdpr7_human_correction_v1.json']
    plan = {'schema_version': 's2_prompt_simplification_comparison@1.0.0', 'run_id': run_id,
            'prepared_at_utc': datetime.now(timezone.utc).isoformat(),
            'prepared_git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'claim_scope': 'development_retrospective_fixed_estg150',
            'model': {'id': core.MODEL_ALIAS, 'documented_release': core.MODEL_RELEASE,
                      'base_url': 'https://api.deepseek.com/v1'},
            'sampling': {'temperature': 0.0, 'top_p': 1.0, 'max_tokens': 4096, 'retry': 0,
                         'thinking': {'type': 'disabled'}, 'stream': False,
                         'response_format': None, 'seed': None},
            'arms': ARMS, 'samples_per_arm': 150, 'repeats': 1, 'max_workers': MAX_WORKERS,
            'ordering': 'rotate A/B submission order per sample; finish each 6-call batch (3 source samples) before the next batch',
            'primary_metric': 'coarse_five_field_micro_f1', 'modality_reported_separately': True,
            'postprocessing': 'shared parse_same_response + adapter + explicitly pinned POLICY_LEGACY canonicalizer',
            'runtime_gold_access': False, 'project_env_read': False,
            'budget': budget, 'requests': requests, 'baseline_reuse': baseline,
            'source_bindings': {str(p.relative_to(ROOT)).replace('\\', '/'): sha_file(p) for p in binding_paths()},
            'preserved_files': {str(p.relative_to(ROOT)).replace('\\', '/'): sha_file(p) for p in preserved},
            'authorization': authorization,
            'limitations': ['one new repeat per A/B; historical v6 reused, cross-batch descriptive comparison',
                           'B combines wording compression with semantic rule changes',
                           'no replacement of fixed paper Table 1/Table 2; no Rules+LLM; no new model families']}
    write_json(out / 'plan.json', plan)
    write_json(out / 'budget.json', budget)
    write_json(ROOT / 'outputs/reports' / f's2_prompt_simplification_{run_id}_preflight.json', plan)
    print(json.dumps({'run_id': run_id, 'planned_calls': 300, 'usd_cap': usd_cap,
                      'input_token_cap': input_cap, 'network_calls': 0}, ensure_ascii=False), flush=True)
    return plan


def verify_plan(plan, allow_llm):
    if not allow_llm or plan.get('authorization', {}).get('authorized') is not True:
        raise ValueError('Real calls require saved user authorization and --allow-llm.')
    if plan['run_id'] != RUN_ID or plan['authorization'].get('user_statement') != USER_DECISION:
        raise ValueError('Current authorization is bound to one run and user statement.')
    if plan['authorization'] != core._read_json(AUTH_PATH) or plan['authorization'].get('data_transfer_authorized') is not True:
        raise ValueError('Authorization/data-transfer binding changed.')
    if plan.get('baseline_reuse') != baseline_binding() or plan.get('max_workers') != MAX_WORKERS:
        raise ValueError('Historical baseline/concurrency binding changed.')
    budget = plan['budget']
    estimate = sum(r['estimated_input_tokens'] for r in plan['requests'])
    input_cap = math.ceil(estimate * 1.5)
    max_usd = math.ceil((input_cap * 1.32 + 300 * 4096 * 3.96) / 1e6 * 1.2 * 100) / 100
    if budget['input_token_cap'] != input_cap or budget['output_token_cap'] != 300 * 4096 or budget['usd_cost_cap'] != max_usd or plan['authorization']['max_usd'] != max_usd or plan['authorization']['max_calls'] != 300:
        raise ValueError('Recorded token/cost budget changed.')
    if plan['arms'] != ARMS or plan['sampling'] != {'temperature': 0.0, 'top_p': 1.0, 'max_tokens': 4096,
            'retry': 0, 'thinking': {'type': 'disabled'}, 'stream': False, 'response_format': None, 'seed': None}:
        raise ValueError('Arm/sampling binding changed.')
    if len(plan['requests']) != 300 or plan['budget']['call_cap'] != 300:
        raise ValueError('Request/call budget binding changed.')
    expected_paths = {str(p.relative_to(ROOT)).replace('\\', '/') for p in binding_paths()}
    if set(plan['source_bindings']) != expected_paths:
        raise ValueError('Required source bindings are missing or changed.')
    if len({(r['arm'], r['sample_id']) for r in plan['requests']}) != 300:
        raise ValueError('Duplicate request in the preflight.')
    for path, expected in {**plan['source_bindings'], **plan['preserved_files']}.items():
        if sha_file(ROOT / path) != expected:
            raise ValueError(f'Frozen source or preserved file changed: {path}')


def private_process_config():
    key = os.environ.get('BPC_HYBRID_DeepSeek_API_KEY') or os.environ.get('DEEPSEEK_API_KEY')
    if not key:
        flat_model = os.environ.get('BPC_HYBRID_LLM_MODEL', '')
        flat_url = os.environ.get('BPC_HYBRID_LLM_BASE_URL', '')
        if flat_model == core.MODEL_ALIAS or flat_url.startswith('https://api.deepseek.com'):
            key = os.environ.get('BPC_HYBRID_LLM_API_KEY')
    if not key:
        raise ValueError('DeepSeek process-environment credential missing; project .env is never read.')
    return config_for(key)


def send_once(arm, sample, config, expected_hash):
    transport = core.RealAPITransport(config, timeout_seconds=180.0, policy=POLICY)
    system, user = render(arm, sample)
    started = time.monotonic()
    try:
        response = transport.send(core.LLMRequest(source_id=sample['sample_id'], source_text=sample['text'],
            system_prompt=system, user_prompt=user))
        decode = transport.last_decode or {}
        content = response.content or ''
        row = {'request_status': 'ok' if decode.get('status') == 'ok_message_content' else 'error',
               'raw_response_content': content, 'returned_model': decode.get('model'),
               'usage': decode.get('usage') or {}, 'finish_reason': response.finish_reason,
               'request_id': decode.get('request_id') or f'{arm}:{sample["sample_id"]}',
               'error': None}
    except Exception as exc:
        row = {'request_status': 'error', 'raw_response_content': '', 'returned_model': None,
               'usage': {}, 'finish_reason': None, 'request_id': f'{arm}:{sample["sample_id"]}',
               'error': type(exc).__name__ + ': transport failed (details redacted)'}
    row.update({'arm': arm, 'sample_id': sample['sample_id'],
                'request_body_sha256': transport.last_request_body_sha256,
                'expected_request_body_sha256': expected_hash,
                'response_sha256': sha_bytes(row['raw_response_content'].encode('utf-8')),
                'runtime_seconds': round(time.monotonic() - started, 3), 'network_call': 1})
    return row


def raw_diagnostics(row):
    content = row['raw_response_content'].strip()
    try:
        payload = json.loads(content)
        strict_object = isinstance(payload, dict)
    except (ValueError, TypeError):
        payload, strict_object = {}, False
    return {'strict_json_object': strict_object, 'fenced': content.startswith('```'),
            'exact_top_level_keys': strict_object and set(payload) == KEYS,
            'missing_top_level_keys': sorted(KEYS - set(payload)) if strict_object else None}


def execute(plan, out, allow_llm=False):
    verify_plan(plan, allow_llm)
    if (out / 'execution_summary.json').exists():
        old = core._read_json(out / 'execution_summary.json')
        if old.get('complete'):
            raise ValueError('Completed run is immutable; use --summarize for offline analysis.')
        if old.get('abort_reason'):
            raise ValueError('Aborted run cannot resume without explicit resolution; no automatic resend.')
    config = private_process_config()
    raw_path, ledger_path = out / 'raw_responses.jsonl', out / 'calls_ledger.jsonl'
    raw = core._read_jsonl(raw_path)
    by_key = {(r['arm'], r['sample_id']): r for r in raw}
    if len(raw) != len(by_key):
        raise ValueError('Duplicate persisted call; refusing resume.')
    ledger = core._read_jsonl(ledger_path)
    if any((r['arm'], r['sample_id']) not in by_key for r in ledger if r['state'] == 'started'):
        raise ValueError('In-doubt request requires manual resolution; no automatic resend.')
    request_map = {(r['arm'], r['sample_id']): r for r in plan['requests']}
    gate = core.AblationBudgetGate(plan['budget'], core.MODEL_ALIAS)
    for row in raw:
        if row['request_body_sha256'] != request_map[(row['arm'], row['sample_id'])]['body_sha256'] or row['response_sha256'] != sha_bytes(row['raw_response_content'].encode('utf-8')):
            raise ValueError('Persisted response binding failed; refusing resume.')
        gate.record_response(row['budget_usage'], row['returned_model'])
    rows = core.samples(150)
    abort_reason = None
    execution_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    started = time.monotonic()
    tasks = []
    for i, sample in enumerate(rows):
        arms = list(ARMS)
        arms = arms[i % len(arms):] + arms[:i % len(arms)]
        tasks.extend((arm, sample) for arm in arms if (arm, sample['sample_id']) not in by_key)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for i in range(0, len(tasks), MAX_WORKERS):
            pending = tasks[i:i + MAX_WORKERS]
            estimates = [request_map[(arm, sample['sample_id'])]['estimated_input_tokens'] for arm, sample in pending]
            if gate.calls_made + len(pending) > gate.call_cap:
                raise ValueError('Batch would exceed call cap.')
            gate.check_before_send(sum(estimates), len(pending) * 4096)
            futures = []
            for arm, sample in pending:
                request = request_map[(arm, sample['sample_id'])]
                actual = sha_bytes(json.dumps(body_for(arm, sample)).encode('utf-8'))
                if actual != request['body_sha256']:
                    raise ValueError('Rendered request differs from preflight.')
                core._append_jsonl(ledger_path, {'arm': arm, 'sample_id': sample['sample_id'],
                    'state': 'started', 'request_body_sha256': actual,
                    'started_at_utc': datetime.now(timezone.utc).isoformat()})
                futures.append((arm, request, pool.submit(send_once, arm, sample, config, actual)))
            for arm, request, future in futures:
                row = future.result()
                sample = {'sample_id': request['sample_id']}
                usage = row['usage']
                known = all(isinstance(usage.get(k), int) for k in ('prompt_tokens', 'completion_tokens'))
                row['usage_known'] = known
                row['budget_usage'] = usage if known else {'prompt_tokens': request['estimated_input_tokens'], 'completion_tokens': 4096}
                row['raw_diagnostics'] = raw_diagnostics(row)
                core._append_jsonl(raw_path, row)
                core._append_jsonl(ledger_path, {'arm': arm, 'sample_id': sample['sample_id'], 'state': 'completed',
                                                'response_sha256': row['response_sha256']})
                raw.append(row)
                by_key[(arm, sample['sample_id'])] = row
                try:
                    gate.record_response(row['budget_usage'], row['returned_model'])
                except core.SepC3Error as exc:
                    abort_reason = str(exc)
                if row['request_body_sha256'] != request['body_sha256']:
                    abort_reason = 'Transport request hash differs from preflight.'
                if not known or row['returned_model'] is None:
                    abort_reason = 'Missing usage/model; stop before further sends; preserve attempted batch.'
            summary = {'run_id': plan['run_id'], 'complete': len(raw) == 300 and abort_reason is None,
                       'execution_git_commit': execution_commit,
                       'actual_calls': len(raw), 'completed_call_batches': i // MAX_WORKERS + 1, 'new_calls_by_arm': {a: sum(r['arm'] == a for r in raw) for a in ARMS},
                       'budget_gate': gate.to_dict(), 'abort_reason': abort_reason,
                       'usage_unknown_calls': sum(not r['usage_known'] for r in raw),
                       'runtime_seconds_this_invocation': round(time.monotonic() - started, 3),
                       'project_env_read': False, 'runtime_gold_access': False}
            write_json(out / 'execution_summary.json', summary)
            print(json.dumps({'completed': len(raw), 'planned': 300, 'estimated_peak_usd': gate.cost_usd, 'abort_reason': abort_reason}, ensure_ascii=False), flush=True)
            if abort_reason:
                break
    return summarize(plan, out)


def summarize(plan, out):
    summary = core._read_json(out / 'execution_summary.json')
    report = {'schema_version': 's2_prompt_simplification_result@1.0.0', 'run_id': plan['run_id'],
              'status': 'complete' if summary['complete'] else 'partial',
              'claim_scope': plan['claim_scope'], 'primary_metric': plan['primary_metric'],
              'model': plan['model'], 'sampling': plan['sampling'], 'execution': summary,
              'plan_sha256': sha_file(out / 'plan.json'), 'arms': {}, 'limitations': plan['limitations'], 'baseline_reuse': plan['baseline_reuse']}
    if not summary['complete']:
        report['performance_metrics'] = None
        write_json(ROOT / 'outputs/reports' / f's2_prompt_simplification_{plan["run_id"]}.json', report)
        print(json.dumps({'status': 'partial', 'actual_calls': summary['actual_calls'], 'reason': summary['abort_reason']}), flush=True)
        return report
    raw = core._read_jsonl(out / 'raw_responses.jsonl')
    assert len(raw) == 300 and len({(r['arm'], r['sample_id']) for r in raw}) == 300
    for path, expected in plan['source_bindings'].items():
        if sha_file(ROOT / path) != expected:
            raise ValueError('Source binding changed before evaluation: ' + path)
    gold = core._read_json(core.FORMAL_GOLD)  # first semantic Gold read; all predictions now fixed
    row_map = {row['sample_id']: row for row in core.samples(150)}
    evidence = ROOT / 'outputs/evidence/s2_prompt_simplification_v1' / plan['run_id']
    evidence.mkdir(parents=True, exist_ok=True)
    bindings = {}
    for filename in ('plan.json', 'budget.json', 'execution_summary.json', 'raw_responses.jsonl', 'calls_ledger.jsonl'):
        shutil.copyfile(out / filename, evidence / filename)
        bindings[filename] = sha_file(evidence / filename)
    predictions_by_arm = {}
    for filename in ('manifest.json', 'raw_responses.jsonl', 'canonical_predictions.jsonl', 'evaluation.json'):
        dest = evidence / ('v6_historical_' + filename)
        shutil.copyfile(BASELINE_ROOT / filename, dest)
        bindings[dest.name] = sha_file(dest)
    for arm in ['v6', *ARMS]:
        arm_raw = core._read_jsonl(BASELINE_ROOT / 'raw_responses.jsonl') if arm == 'v6' else [r for r in raw if r['arm'] == arm]
        if arm == 'v6':
            for r in arm_raw:
                r['raw_diagnostics'] = raw_diagnostics(r)
        predictions = core._read_jsonl(BASELINE_ROOT / 'canonical_predictions.jsonl') if arm == 'v6' else [core.base._prediction_row(core.base.parse_same_response(r, arm, row_map[r['sample_id']]['text']), arm) for r in arm_raw]
        predictions_by_arm[arm] = {p['sample_id']: p for p in predictions}
        evaluation = core.evaluate_coarse(gold, core.attempt_rows(predictions), method_id=f'prompt_simplification_{arm}')
        field = evaluation['coarse_five_field_micro']
        report['arms'][arm] = {'prompt_name': BASELINE_PROMPT if arm == 'v6' else ARMS[arm], 'denominator': 150, 'historical_reuse': arm == 'v6', 'new_api_calls': 0 if arm == 'v6' else 150,
            'overall_precision': field['precision'], 'overall_recall': field['recall'], 'overall_f1': field['f1'],
            'mean_five_field_f1': evaluation['coarse_five_field_mean_f1'],
            'modality_macro_f1': evaluation['modality_labels']['macro_f1'], 'failed_count': evaluation['failed_count'],
            'per_field': evaluation['five_fields'],
            'raw_strict_json_objects': sum(r['raw_diagnostics']['strict_json_object'] for r in arm_raw),
            'raw_exact_top_level_keys': sum(r['raw_diagnostics']['exact_top_level_keys'] for r in arm_raw),
            'raw_fenced_responses': sum(r['raw_diagnostics']['fenced'] for r in arm_raw),
            'input_tokens': sum(r['usage'].get('prompt_tokens', 0) for r in arm_raw),
            'output_tokens': sum(r['usage'].get('completion_tokens', 0) for r in arm_raw)}
        prediction_path = evidence / f'{arm}_canonical_predictions.jsonl'
        prediction_path.write_text(''.join(json.dumps(p, ensure_ascii=False) + '\n' for p in predictions), encoding='utf-8', newline='\n')
        write_json(evidence / f'{arm}_evaluation.json', evaluation)
        bindings[prediction_path.name] = sha_file(prediction_path)
        bindings[f'{arm}_evaluation.json'] = sha_file(evidence / f'{arm}_evaluation.json')
    baseline = report['arms']['v6']['overall_f1']
    for arm in ['v6', *ARMS]:
        report['arms'][arm]['delta_overall_vs_v6'] = report['arms'][arm]['overall_f1'] - baseline
    changes = []
    for sid, source in row_map.items():
        extracts = {}
        for arm in ['v6', *ARMS]:
            rec = predictions_by_arm[arm][sid].get('record') or {}
            extracts[arm] = {field: [s['text'] for c in rec.get('clauses', []) for s in c.get(plural, [])]
                             for field, plural in [('actor', 'actors'), ('action', 'actions'), ('condition', 'conditions'), ('constraint', 'constraints'), ('exception', 'exceptions')]}
            extracts[arm]['modality'] = [c.get('modality', {}).get('label') for c in rec.get('clauses', [])]
        changes.append({'sample_id': sid, 'source_text': source['text'], 'extracts': extracts,
                        'changed_fields': {arm: [f for f in extracts[arm] if extracts[arm][f] != extracts['v6'][f]] for arm in ('A', 'B')}})
    write_json(evidence / 'paired_sample_changes.json', changes)
    bindings['paired_sample_changes.json'] = sha_file(evidence / 'paired_sample_changes.json')
    report['artifact_bindings'] = bindings
    report['evidence_root'] = str(evidence.relative_to(ROOT)).replace('\\', '/')
    report['preserved_files_unchanged'] = all(sha_file(ROOT / p) == h for p, h in plan['preserved_files'].items())
    if not report['preserved_files_unchanged']:
        raise ValueError('A protected prior result or user file changed.')
    stem = ROOT / 'outputs/reports' / f's2_prompt_simplification_{plan["run_id"]}'
    write_json(stem.with_suffix('.json'), report)
    lines = ['# v6/A/B prompt 精简对照', '',
             '开发性、回顾性固定 EStG-150 对照；A/B 各新跑一次，原版复用历史 D-full-0813。跨批比较不能排除服务端变化。B 同时包含措辞和语义规则变更，不能归因于单句。', '',
             '| 臂 | Overall P | Overall R | Overall F1 | 相对 v6 | Actor | Action | Condition | Constraint | Exception | Modality macro-F1 | 失败 |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for arm, a in report['arms'].items():
        vals = [a['overall_precision'], a['overall_recall'], a['overall_f1'], a['delta_overall_vs_v6']]
        vals += [a['per_field'][f]['f1'] for f in ('actor', 'action', 'condition', 'constraint', 'exception')]
        vals += [a['modality_macro_f1']]
        lines.append('| ' + arm + ' | ' + ' | '.join(f'{v:.4f}' for v in vals) + f' | {a["failed_count"]} |')
    lines += ['', '原始 JSON 和用量（未经后处理）：', '', '| 臂 | 严格 JSON 对象 | 顶层键完全一致 | Markdown 围栏 | 输入 tokens | 输出 tokens |', '|---|---:|---:|---:|---:|---:|']
    for arm, a in report['arms'].items():
        lines.append(f'| {arm} | {a["raw_strict_json_objects"]}/150 | {a["raw_exact_top_level_keys"]}/150 | {a["raw_fenced_responses"]} | {a["input_tokens"]} | {a["output_tokens"]} |')
    lines += ['', f'真实调用：{summary["actual_calls"]}；0 重试；费用按全部输入未命中缓存及高峰价计上界估计 USD {summary["budget_gate"]["cost_usd"]:.4f}，不是账户实扣。',
              f'逐样本差异与全部原始响应、预测、评价、计划、账本：`{report["evidence_root"]}`。',
              '固定论文表一/表二、历史结果及既有用户修改未改。本轮不支持稳定性或独立泛化结论。']
    stem.with_suffix('.md').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'complete', 'arms': {arm: {k: a[k] for k in ('overall_f1', 'delta_overall_vs_v6', 'failed_count')} for arm, a in report['arms'].items()}}, ensure_ascii=False), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', default=RUN_ID)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--summarize', action='store_true')
    parser.add_argument('--allow-llm', action='store_true')
    args = parser.parse_args()
    if args.run_id != RUN_ID:
        parser.error('Only the newly authorized comparison_20261006_v2 is executable.')
    if sum((args.prepare, args.execute, args.summarize)) != 1:
        parser.error('Choose --prepare, --execute or --summarize.')
    if args.prepare:
        prepare(args.run_id)
        return 0
    out = RUN_ROOT / args.run_id
    plan = core._read_json(out / 'plan.json')
    if plan['run_id'] != args.run_id:
        raise ValueError('Run directory/plan mismatch.')
    result = execute(plan, out, args.allow_llm) if args.execute else summarize(plan, out)
    return 0 if result['status'] == 'complete' else 2


if __name__ == '__main__':
    raise SystemExit(main())
