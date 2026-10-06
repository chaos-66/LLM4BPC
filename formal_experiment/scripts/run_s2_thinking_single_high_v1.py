"""One explicitly authorized diagnostic, at the provider's generation maximum.

Default preparation and summary are offline. The saved ledger prohibits resend.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_s2_thinking_sensitivity_v1 as previous

RUN_ID = 'high_provider_max_estg000002_20261006_v1'
SAMPLE_ID = 'estg_000002'
PROVIDER_MAX_TOKENS = 393216
TRANSPORT_TIMEOUT = 7200
AUTH_PATH = ROOT / 'configs/authorization/s2_thinking_single_high_provider_max_20261006_v1.json'
OUT = previous.RUN_ROOT / RUN_ID
OLD_OUT = previous.RUN_ROOT / previous.RUN_ID
REPORT = ROOT / 'outputs/reports/s2_thinking_single_high_provider_max_20261006_v1'


def sample():
    return next(s for s in previous.core.samples(150) if s['sample_id'] == SAMPLE_ID)


def body_for(item):
    body = previous.body_for(item)
    body['max_tokens'] = PROVIDER_MAX_TOKENS
    return body


def body_bytes():
    return json.dumps(body_for(sample())).encode('utf-8')


def sources():
    deps = [p for p in previous.source_paths() if p.relative_to(ROOT).parts[0] in ('scripts', 'src')]
    return [Path(__file__), AUTH_PATH, previous.core.ESTG_INPUT,
            previous.load_prompt(previous.PROMPT).path,
            ROOT / 'configs/schemas/stage2_prediction.schema.json',
            OLD_OUT / 'plan.json', OLD_OUT / 'raw_responses.jsonl', *deps]


def git_head():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()


def prepare():
    if OUT.exists():
        raise ValueError('Diagnostic already prepared; saved evidence must not be overwritten.')
    auth = previous.read_json(AUTH_PATH)
    if (auth.get('authorized') is not True or auth['run_id'] != RUN_ID
            or auth['sample_id'] != SAMPLE_ID or auth['max_calls'] != 1 or auth['retry_cap'] != 0
            or auth['max_generated_tokens_per_call'] != PROVIDER_MAX_TOKENS):
        raise ValueError('Own one-call provider-maximum authorization is required.')
    old_plan = previous.read_json(OLD_OUT / 'plan.json')
    old_raw = previous.core._read_jsonl(OLD_OUT / 'raw_responses.jsonl')
    old_request = next(r for r in old_plan['requests'] if r['sample_id'] == SAMPLE_ID)
    if (previous.sha(previous.request_bytes(sample())) != old_request['body_sha256']
            or len(old_raw) != 1 or old_raw[0]['sample_id'] != SAMPLE_ID
            or old_raw[0]['finish_reason'] != 'length'):
        raise ValueError('Original failed request/input binding changed.')
    estimate = (len(body_bytes()) + 2) // 3
    plan = {'schema_version': 's2_thinking_single_plan@1.0.0', 'run_id': RUN_ID,
            'pipeline_task': 'S2-THINKING-SENSITIVITY-V1', 'authorization': auth,
            'sample_id': SAMPLE_ID, 'prepared_at_utc': datetime.now(timezone.utc).isoformat(),
            'prepared_git_commit': git_head(), 'request_body_sha256': previous.sha(body_bytes()),
            'request_settings': {k: v for k, v in body_for(sample()).items() if k != 'messages'},
            'changed_request_keys': ['max_tokens'], 'previous_max_tokens': 16384,
            'provider_max_tokens': PROVIDER_MAX_TOKENS, 'omitted_parameter_default_tokens': 65536,
            'transport_timeout_seconds': TRANSPORT_TIMEOUT, 'max_calls': 1, 'retry_cap': 0,
            'estimated_input_tokens': estimate, 'peak_no_cache_max_token_estimate_usd':
                (estimate * 1.5 * 1.32 + PROVIDER_MAX_TOKENS * 3.96) / 1e6,
            'price_snapshot': old_plan['budget']['price_snapshot'],
            'api_parameter_documentation': 'https://api-docs.deepseek.com/api/create-chat-completion/',
            'runtime_gold_access': False, 'project_env_read': False,
            'scope': 'single_case_generation_budget_diagnostic; no 150-record evaluation',
            'source_bindings': {p.relative_to(ROOT).as_posix(): previous.sha_file(p) for p in sources()}}
    previous.write_json(OUT / 'plan.json', plan)
    previous.write_json(Path(str(REPORT) + '_preflight.json'), plan)
    print(json.dumps({'prepared': RUN_ID, 'planned_calls': 1,
                      'provider_max_tokens': PROVIDER_MAX_TOKENS, 'network_calls': 0}), flush=True)
    return plan


def verify(plan, allow_llm):
    if not allow_llm or plan['run_id'] != RUN_ID or plan['authorization'] != previous.read_json(AUTH_PATH):
        raise ValueError('Saved authorization and explicit --allow-llm are required.')
    if plan['max_calls'] != 1 or plan['retry_cap'] != 0 or plan['provider_max_tokens'] != PROVIDER_MAX_TOKENS:
        raise ValueError('Single-call policy changed.')
    if plan['authorization']['authorized'] is not True:
        raise ValueError('Authorization is disabled.')
    if plan['request_settings'] != {k: v for k, v in body_for(sample()).items() if k != 'messages'}:
        raise ValueError('Saved request settings changed.')
    bindings = {p.relative_to(ROOT).as_posix(): previous.sha_file(p) for p in sources()}
    if bindings != plan['source_bindings'] or previous.sha(body_bytes()) != plan['request_body_sha256']:
        raise ValueError('Frozen diagnostic request or sources changed.')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, 'Redirect refused', headers, fp)


def send_once(item, body, key):
    start = time.monotonic()
    req = urllib.request.Request(previous.ENDPOINT, data=body, method='POST', headers={
        'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json',
        'User-Agent': 'LLM4BPC-authorized-single-diagnostic/1.0'})
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=TRANSPORT_TIMEOUT) as response:
            raw = response.read()
            status = response.status
        return previous.response_row(item, body, raw, status, time.monotonic() - start, key)
    except urllib.error.HTTPError as exc:
        return previous.response_row(item, body, exc.read(), exc.code, time.monotonic() - start, key)
    except Exception as exc:
        row = previous.response_row(item, body, b'{}', None, time.monotonic() - start)
        row['error'] = type(exc).__name__ + ': transport failed; details redacted; no retry'
        return row


def measurements(row):
    usage = row['usage']
    completion = usage.get('completion_tokens')
    reasoning = usage.get('completion_tokens_details', {}).get('reasoning_tokens')
    final = completion - reasoning if type(completion) is int and type(reasoning) is int else None
    known = row['usage_known'] and type(reasoning) is int
    natural = (row['request_status'] == 'ok' and row['returned_model'] == previous.MODEL)
    peak = ((usage['prompt_tokens'] * 1.32 + completion * 3.96) / 1e6) if row['usage_known'] else None
    hit = usage.get('prompt_cache_hit_tokens', usage.get('prompt_tokens_details', {}).get('cached_tokens', 0))
    cached_peak = (((usage['prompt_tokens'] - hit) * 1.32 + hit * .044 + completion * 3.96) / 1e6) if row['usage_known'] else None
    return {'http_status': row['http_status'], 'returned_model': row['returned_model'],
            'finish_reason': row['finish_reason'], 'natural_completion': natural,
            'prompt_tokens': usage.get('prompt_tokens'), 'reasoning_tokens': reasoning,
            'final_answer_tokens': final, 'generated_tokens_total': completion,
            'total_tokens_including_prompt': usage.get('total_tokens'),
            'exact_token_breakdown_known': known, 'final_answer_characters': len(row['raw_response_content']),
            'runtime_seconds': row['runtime_seconds'], 'peak_no_cache_estimate_usd': peak,
            'peak_reported_cache_estimate_usd': cached_peak,
            'off_peak_reported_cache_estimate_usd': cached_peak * .5 if cached_peak is not None else None,
            'account_deduction_verified': False,
            'interpretation': ('Observed tokens for this one natural completion; not a minimum or 150-sample distribution.'
                               if natural else 'Natural completion not observed; exact tokens needed remain unknown.')}


def summarize(plan):
    raw = previous.core._read_jsonl(OUT / 'raw_responses.jsonl')
    ledger = previous.core._read_jsonl(OUT / 'calls_ledger.jsonl')
    if len(raw) != 1 or [r['state'] for r in ledger] != ['started', 'completed']:
        raise ValueError('Exactly one saved response and start/completion ledger are required.')
    row = raw[0]
    report = {'schema_version': 's2_thinking_single_result@1.0.0', 'run_id': RUN_ID,
              'status': 'complete' if measurements(row)['natural_completion'] else 'failed',
              'actual_calls': 1, 'retry': 0, 'sample_id': SAMPLE_ID, 'new_off_calls': 0, 'new_sun_calls': 0,
              'settings': plan['request_settings'], 'measurements': measurements(row),
              'execution_git_commit': ledger[0]['execution_git_commit'],
              'runtime_gold_access': False, 'project_env_read': False, 'performance_metrics': None}
    if row['request_status'] == 'ok':
        prediction = previous.predictions_from_raw(raw, {SAMPLE_ID: sample()})[0]
        previous.write_json(OUT / 'final_prediction.json', prediction)
        report['final_json_canonical_valid'] = prediction['request_status'] == 'ok'
        report['final_json_validation_error'] = prediction.get('error')
    else:
        report['final_json_canonical_valid'] = False
    previous.write_json(OUT / 'result.json', report)
    artifacts = {p.name: previous.sha_file(p) for p in OUT.iterdir() if p.is_file() and p.name != 'run_manifest.json'}
    previous.write_json(OUT / 'run_manifest.json', {'schema_version': 's2_thinking_single_manifest@1.0.0',
        'run_id': RUN_ID, 'status': report['status'], 'source_bindings': plan['source_bindings'],
        'artifacts': artifacts, 'actual_calls': 1, 'retry': 0})
    previous.write_json(Path(str(REPORT) + '.json'), report)
    m = report['measurements']
    lines = ['# 同一失败样本 high 思考：服务最大生成上限诊断', '',
             f'样本：{SAMPLE_ID}；新调用1次，0重试；原v6/high不变，仅max_tokens从16384改为393216。', '',
             f'结束原因：{m["finish_reason"]}；自然完成：{m["natural_completion"]}；最终JSON通过共享规范校验：{report["final_json_canonical_valid"]}。', '',
             '| 用量 | tokens |', '|---|---:|',
             f'| 输入 | {m["prompt_tokens"]} |', f'| 思考 | {m["reasoning_tokens"]} |',
             f'| 最终答案 | {m["final_answer_tokens"]} |', f'| 生成合计 | {m["generated_tokens_total"]} |',
             f'| 含输入合计 | {m["total_tokens_including_prompt"]} |', '',
             f'耗时：{m["runtime_seconds"]}秒。峰价无缓存估算USD{m["peak_no_cache_estimate_usd"]}；报告缓存后峰价USD{m["peak_reported_cache_estimate_usd"]}、闲时USD{m["off_peak_reported_cache_estimate_usd"]}；未查账户实扣。', '',
             '服务仍有上限，未承诺真正无限。只反映一次新随机生成的实际用量，不是最小所需预算；如仍length，只能得到下界。', '',
             '此次不测low、不自动恢复150条，不评估单条F1或替换固定主表。原high/16K失败证据保留。']
    Path(str(REPORT) + '.md').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(report, ensure_ascii=False), flush=True)
    return report


def execute(plan, allow_llm):
    verify(plan, allow_llm)
    if (OUT / 'calls_ledger.jsonl').exists() or (OUT / 'raw_responses.jsonl').exists():
        raise ValueError('Diagnostic already started or completed; no resend is authorized.')
    key = previous.process_key()
    body = body_bytes()
    previous.core._append_jsonl(OUT / 'calls_ledger.jsonl', {'sample_id': SAMPLE_ID, 'state': 'started',
        'request_body_sha256': previous.sha(body), 'execution_git_commit': git_head(),
        'started_at_utc': datetime.now(timezone.utc).isoformat()})
    row = send_once(sample(), body, key)
    previous.core._append_jsonl(OUT / 'raw_responses.jsonl', row)
    previous.core._append_jsonl(OUT / 'calls_ledger.jsonl', {'sample_id': SAMPLE_ID, 'state': 'completed',
        'response_envelope_sha256': row['response_envelope_sha256']})
    return summarize(plan)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--execute', action='store_true')
    mode.add_argument('--summarize', action='store_true')
    parser.add_argument('--allow-llm', action='store_true')
    args = parser.parse_args()
    if args.execute or args.summarize:
        plan = previous.read_json(OUT / 'plan.json')
        execute(plan, args.allow_llm) if args.execute else summarize(plan)
    else:
        prepare()


if __name__ == '__main__':
    main()
