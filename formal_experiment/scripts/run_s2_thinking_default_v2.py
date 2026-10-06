"""Authorized EStG-150 thinking run: max_tokens omitted, zero retries.

Reuse immutable v6 rendering, transport and evaluation. Never alter old runs.
"""
from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_s2_thinking_sensitivity_v1 as shared
import run_s2_thinking_single_high_v1 as transport

RUN_ID = 'thinking_default_20261007_v2'
DEFAULT_TOKENS = 65536
MAX_CALLS = 150
MAX_WORKERS = 12
AUTH_PATH = ROOT / 'configs/authorization/s2_thinking_default_20261007_v2.json'
OUT = shared.RUN_ROOT / RUN_ID
REPORT = ROOT / 'outputs/reports' / ('s2_thinking_' + RUN_ID)
send_once = transport.send_once


def body_for(sample):
    body = shared.body_for(sample)
    del body['max_tokens']
    return body


def request_bytes(sample):
    return json.dumps(body_for(sample)).encode('utf-8')


def sources():
    return [Path(__file__), AUTH_PATH, Path(transport.__file__), *shared.source_paths()]


def head():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()


def prepare():
    if OUT.exists():
        raise ValueError('Run already prepared; never overwrite saved evidence.')
    auth = shared.read_json(AUTH_PATH)
    if (auth.get('authorized') is not True or auth['run_id'] != RUN_ID or auth['max_calls'] != MAX_CALLS
            or auth['retry_cap'] != 0 or auth['max_tokens_parameter_policy'] != 'omitted'
            or auth['documented_default_generated_tokens_per_call'] != DEFAULT_TOKENS
            or auth['max_workers'] != MAX_WORKERS):
        raise ValueError('Own default-max_tokens 150-call authorization is required.')
    historical = shared.baselines()
    samples = shared.core.samples(150)
    requests = [{'sample_id': s['sample_id'], 'body_sha256': shared.sha(request_bytes(s)),
                 'estimated_input_tokens': math.ceil(len(request_bytes(s)) / 3)} for s in samples]
    input_cap = math.ceil(sum(r['estimated_input_tokens'] for r in requests) * 1.5)
    price = {'currency': 'USD', 'input_cache_miss_per_million': 1.32,
             'input_cache_hit_per_million': .044, 'output_per_million': 3.96,
             'off_peak_multiplier': .5, 'verified_date_local': '2026-10-07',
             'source_url': 'https://api-docs.deepseek.com/quick_start/pricing/'}
    maximum_cost = (input_cap * 1.32 + MAX_CALLS * DEFAULT_TOKENS * 3.96) / 1e6
    if maximum_cost * 1.2 > auth['max_usd']:
        raise ValueError('Maximum default-token reservation exceeds USD protection.')
    expected = {s['sample_id']: s['text'] for s in samples}
    mismatches = [r['sample_id'] for r in historical['off_0813']
                  if r['record']['source_text'] != expected[r['sample_id']]]
    plan = {'schema_version': 's2_thinking_default_plan@2.0.0', 'run_id': RUN_ID,
            'pipeline_task': 'S2-THINKING-SENSITIVITY-V1', 'authorization': auth,
            'prepared_at_utc': datetime.now(timezone.utc).isoformat(), 'prepared_git_commit': head(),
            'samples': 150, 'requests': requests, 'new_off_calls': 0, 'new_sun_calls': 0,
            'model': {'id': shared.MODEL, 'current_documented_release': 'DeepSeek-V4-Pro-0813',
                      'endpoint': shared.ENDPOINT},
            'generation': {'thinking': 'enabled', 'reasoning_effort': 'high', 'max_tokens': 'omitted',
                'documented_default_generated_tokens': DEFAULT_TOKENS, 'temperature_sent': 0.,
                'temperature_effective': 'ignored_in_thinking_mode', 'top_p': 1., 'stream': False,
                'response_format': None, 'max_workers': MAX_WORKERS,
                'transport_timeout_seconds': transport.TRANSPORT_TIMEOUT, 'retry': 0},
            'budget': {'call_cap': MAX_CALLS, 'input_token_cap': input_cap,
                       'output_token_cap': MAX_CALLS * DEFAULT_TOKENS, 'usd_cost_cap': auth['max_usd'],
                       'price_snapshot': price, 'maximum_token_cost_usd': maximum_cost},
            'runtime_gold_access': False, 'project_env_read': False,
            'primary_metric': 'coarse_five_field_micro_f1', 'modality_reported_separately': True,
            'secondary_historical_source_text_mismatches': mismatches,
            'source_bindings': {p.relative_to(ROOT).as_posix(): shared.sha_file(p) for p in sources()},
            'limitations': ['One new repeat; historical off reuse, not a simultaneous randomized mode comparison.',
                'Formal off R3 predates 0813; current alias can represent a changed model.',
                'Existing off_0813 uses the same documented release; server drift remains possible.',
                'off_0813 preserves the estg_000092 model-emitted source_text mismatch; sent-input fingerprints match.',
                'Thinking uses provider default 65536; historical off ceiling is 4096. Not an equal-budget causal test.',
                'temperature=0 is ignored in thinking mode; no deterministic or stability claim.',
                'Fixed existing benchmark; no independent unseen test or replacement of frozen main tables.']}
    shared.write_json(OUT / 'plan.json', plan)
    shared.write_json(Path(str(REPORT) + '_preflight.json'), plan)
    print(json.dumps({'prepared': RUN_ID, 'planned_calls': MAX_CALLS, 'network_calls': 0,
        'max_tokens_parameter': 'omitted', 'documented_default_tokens': DEFAULT_TOKENS,
        'max_token_peak_estimate_usd': maximum_cost, 'usd_guardrail': auth['max_usd']}), flush=True)
    return plan


def verify(plan, allow_llm):
    if not allow_llm or plan['run_id'] != RUN_ID or plan['authorization'] != shared.read_json(AUTH_PATH):
        raise ValueError('Own saved authorization plus explicit --allow-llm are required.')
    if plan['authorization']['authorized'] is not True:
        raise ValueError('Authorization is disabled.')
    bindings = {p.relative_to(ROOT).as_posix(): shared.sha_file(p) for p in sources()}
    requests = [{'sample_id': s['sample_id'], 'body_sha256': shared.sha(request_bytes(s)),
                 'estimated_input_tokens': math.ceil(len(request_bytes(s)) / 3)} for s in shared.core.samples(150)]
    budget = plan['budget']
    if (bindings != plan['source_bindings'] or requests != plan['requests']
            or budget['call_cap'] != MAX_CALLS or budget['output_token_cap'] != MAX_CALLS * DEFAULT_TOKENS
            or budget['input_token_cap'] != math.ceil(sum(r['estimated_input_tokens'] for r in requests) * 1.5)
            or budget['usd_cost_cap'] != plan['authorization']['max_usd']
            or budget['price_snapshot']['input_cache_miss_per_million'] != 1.32
            or budget['price_snapshot']['output_per_million'] != 3.96
            or plan['generation']['max_tokens'] != 'omitted'):
        raise ValueError('Frozen request, source or budget binding changed.')
    if len({r['sample_id'] for r in requests}) != MAX_CALLS:
        raise ValueError('Expected exactly 150 unique input IDs.')


def restore(plan):
    saved = OUT / 'execution_summary.json'
    if saved.exists() and (shared.read_json(saved)['complete'] or shared.read_json(saved)['abort_reason']):
        raise ValueError('Run already completed/aborted; no automatic resend.')
    raw = shared.core._read_jsonl(OUT / 'raw_responses.jsonl')
    ledger = shared.core._read_jsonl(OUT / 'calls_ledger.jsonl')
    starts = [r for r in ledger if r['state'] == 'started']
    completions = [r for r in ledger if r['state'] == 'completed']
    ids = [r['sample_id'] for r in raw]
    if (len(set(ids)) != len(ids) or len(ids) > MAX_CALLS or len(starts) != len(raw)
            or len(completions) != len(raw) or len({r['sample_id'] for r in starts}) != len(starts)
            or set(ids) != {r['sample_id'] for r in starts}
            or set(ids) != {r['sample_id'] for r in completions}):
        raise ValueError('In-doubt or duplicate persisted call; never resend.')
    reqs = {r['sample_id']: r for r in plan['requests']}
    gate = shared.core.AblationBudgetGate(plan['budget'], shared.MODEL)
    for r in raw:
        if (r['sample_id'] not in reqs or r['request_body_sha256'] != reqs[r['sample_id']]['body_sha256']
                or r['response_envelope_sha256'] != shared.sha(r['raw_response_envelope_json'].encode('utf-8'))):
            raise ValueError('Persisted response binding changed.')
        gate.record_response(r['budget_usage'], r['returned_model'])
    return raw, gate


def fatal_reason(row):
    if row['http_status'] in (401, 403, 429) or not row['usage_known'] or row['returned_model'] != shared.MODEL:
        return 'API identity, rate limit or usage contract failed; stop new sends, no retry.'
    if row['usage']['completion_tokens'] > DEFAULT_TOKENS:
        return 'Observed generation exceeds documented default; stop new sends.'
    return None


def execute(plan, allow_llm):
    verify(plan, allow_llm)
    raw, gate = restore(plan)
    key = shared.process_key()
    seen = {r['sample_id'] for r in raw}
    todo = iter([s for s in shared.core.samples(150) if s['sample_id'] not in seen])
    request_map = {r['sample_id']: r for r in plan['requests']}
    start = time.monotonic()
    commit = head()
    dirty = subprocess.check_output(['git', 'status', '--short', '--', 'formal_experiment'],
        cwd=ROOT, text=True, encoding='utf-8').splitlines()
    abort = None
    sent = len(raw)
    futures = {}
    exhausted = False
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        while futures or not exhausted:
            while not abort and not exhausted and len(futures) < MAX_WORKERS:
                item = next(todo, None)
                if item is None:
                    exhausted = True
                    break
                if sent >= MAX_CALLS:
                    raise ValueError('Call cap would be exceeded.')
                reserve_input = sum(request_map[s['sample_id']]['estimated_input_tokens'] for s in futures.values())
                try:
                    gate.check_before_send(reserve_input + request_map[item['sample_id']]['estimated_input_tokens'],
                                           (len(futures) + 1) * DEFAULT_TOKENS)
                except shared.core.SepC3Error as exc:
                    abort = str(exc)
                    break
                body = request_bytes(item)
                if shared.sha(body) != request_map[item['sample_id']]['body_sha256']:
                    raise ValueError('Actual request differs from preflight.')
                shared.core._append_jsonl(OUT / 'calls_ledger.jsonl', {'sample_id': item['sample_id'],
                    'state': 'started', 'request_body_sha256': shared.sha(body),
                    'started_at_utc': datetime.now(timezone.utc).isoformat()})
                futures[pool.submit(send_once, item, body, key)] = item
                sent += 1
            if not futures:
                break
            done, _ = wait(futures, return_when=FIRST_COMPLETED)
            for future in done:
                item = futures.pop(future)
                row = future.result()
                row['budget_usage'] = row['usage'] if row['usage_known'] else {
                    'prompt_tokens': request_map[item['sample_id']]['estimated_input_tokens'],
                    'completion_tokens': DEFAULT_TOKENS}
                shared.core._append_jsonl(OUT / 'raw_responses.jsonl', row)
                shared.core._append_jsonl(OUT / 'calls_ledger.jsonl', {'sample_id': item['sample_id'],
                    'state': 'completed', 'response_envelope_sha256': row['response_envelope_sha256']})
                raw.append(row)
                if not row['usage_known']:
                    gate.missing_usage_calls += 1
                try:
                    gate.record_response(row['budget_usage'], row['returned_model'])
                except shared.core.SepC3Error as exc:
                    abort = abort or str(exc)
                abort = abort or fatal_reason(row)
            summary = {'run_id': RUN_ID, 'complete': len(raw) == MAX_CALLS and not abort,
                'actual_calls': sent, 'completed_calls': len(raw), 'planned_calls': MAX_CALLS,
                'retry': 0, 'new_off_calls': 0, 'new_sun_calls': 0, 'abort_reason': abort,
                'budget_gate': gate.to_dict(), 'execution_git_commit': commit, 'execution_dirty_paths': dirty,
                'runtime_seconds_this_invocation': round(time.monotonic() - start, 3),
                'runtime_gold_access': False, 'project_env_read': False,
                'truncated_calls': sum(r['finish_reason'] == 'length' for r in raw),
                'empty_final_calls': sum(not r['raw_response_content'].strip() for r in raw)}
            shared.write_json(OUT / 'execution_summary.json', summary)
            print(json.dumps({'completed': len(raw), 'started': sent, 'planned': MAX_CALLS,
                'truncated': summary['truncated_calls'], 'estimated_peak_no_cache_usd': gate.cost_usd,
                'abort_reason': abort}), flush=True)
    return summarize(plan)


def token_stats(values):
    if not values:
        return None
    ordered = sorted(values)
    return {'count': len(values), 'total': sum(values), 'mean': statistics.mean(values),
            'median': statistics.median(values), 'p90_nearest_rank': ordered[math.ceil(.9 * len(values)) - 1],
            'max': max(values)}


def summarize(plan):
    summary = shared.read_json(OUT / 'execution_summary.json')
    raw = shared.core._read_jsonl(OUT / 'raw_responses.jsonl')
    report = {'schema_version': 's2_thinking_default_result@2.0.0', 'run_id': RUN_ID,
        'pipeline_task': plan['pipeline_task'], 'status': 'complete' if summary['complete'] else 'partial',
        'execution': summary, 'model': plan['model'], 'generation': plan['generation'],
        'primary_metric': plan['primary_metric'], 'limitations': plan['limitations'], 'arms': {}, 'metrics': None}
    if summary['complete']:
        if len(raw) != MAX_CALLS or len({r['sample_id'] for r in raw}) != MAX_CALLS:
            raise ValueError('Full 150-call response set required for performance evaluation.')
        by_id = {r['sample_id']: r for r in raw}
        raw = [by_id[s['sample_id']] for s in shared.core.samples(150)]
        rows = shared.predictions_from_raw(raw, {s['sample_id']: s for s in shared.core.samples(150)})
        shared.write_json(OUT / 'thinking_on_predictions.json', {'records': rows})
        gold = shared.read_json(shared.core.FORMAL_GOLD)  # only after all predictions saved
        for arm, predictions in {'thinking_on': rows, **shared.baselines()}.items():
            evaluation = shared.core.evaluate_coarse(gold, shared.core.attempt_rows(predictions), method_id=arm)
            shared.write_json(OUT / (arm + '_evaluation.json'), evaluation)
            report['arms'][arm] = {'denominator': 150, 'new_api_calls': 150 if arm == 'thinking_on' else 0,
                'overall': evaluation['coarse_five_field_micro'], 'per_field': evaluation['five_fields'],
                'modality_macro_f1': evaluation['modality_labels']['macro_f1'], 'failed_count': evaluation['failed_count']}
        main = shared.read_json(ROOT / 'outputs/reports/stage2_table1_paper_final_v1.json')
        for arm, key in [('off_formal', 'direct_llm'), ('sun', 'sun_rule_only')]:
            if report['arms'][arm]['overall']['f1'] != main['arms'][key]['overall_pooled_five_span_fields']['f1']:
                raise ValueError('Historical evaluation differs from fixed Table 1.')
        f1 = report['arms']['thinking_on']['overall']['f1']
        report['metrics'] = {'thinking_on_f1': f1,
            'delta_vs_formal_off_pp': 100 * (f1 - report['arms']['off_formal']['overall']['f1']),
            'delta_vs_0813_off_pp': 100 * (f1 - report['arms']['off_0813']['overall']['f1'])}
        diagnostics = [dict(transport.measurements(r), sample_id=r['sample_id']) for r in raw]
        shared.write_json(OUT / 'response_diagnostics.json', diagnostics)
        report['token_statistics'] = {k: token_stats([r[k] for r in diagnostics if type(r[k]) is int])
            for k in ('reasoning_tokens', 'final_answer_tokens', 'generated_tokens_total', 'prompt_tokens')}
        off_raw = shared.core._read_jsonl(shared.OFF_0813_ROOT / 'raw_responses.jsonl')
        off_tokens = [r['usage']['completion_tokens'] for r in off_raw]
        report['historical_off_0813_output_statistics'] = token_stats(off_tokens)
        report['generated_token_ratio_vs_0813_off'] = report['token_statistics']['generated_tokens_total']['total'] / sum(off_tokens)
    known = [r for r in raw if r['usage_known']]
    inp = sum(r['usage']['prompt_tokens'] for r in known)
    output = sum(r['usage']['completion_tokens'] for r in known)
    hit = sum(r['usage'].get('prompt_cache_hit_tokens', r['usage'].get('prompt_tokens_details', {}).get('cached_tokens', 0)) for r in known)
    peak = ((inp - hit) * 1.32 + hit * .044 + output * 3.96) / 1e6
    report['cost'] = {'known_usage_calls': len(known), 'input_tokens': inp, 'output_tokens_including_reasoning': output,
        'cache_hit_input_tokens': hit, 'peak_no_cache_estimate_usd': (inp * 1.32 + output * 3.96) / 1e6,
        'peak_reported_cache_estimate_usd': peak, 'off_peak_reported_cache_estimate_usd': peak * .5,
        'account_deduction_verified': False, 'usd_guardrail': plan['budget']['usd_cost_cap']}
    shared.write_json(OUT / 'result.json', report)
    artifacts = {p.name: shared.sha_file(p) for p in OUT.iterdir() if p.is_file() and p.name != 'run_manifest.json'}
    shared.write_json(OUT / 'run_manifest.json', {'schema_version': 's2_thinking_default_manifest@2.0.0',
        'run_id': RUN_ID, 'status': report['status'], 'source_bindings': plan['source_bindings'],
        'artifacts': artifacts, 'execution': summary})
    shared.write_json(Path(str(REPORT) + '.json'), report)
    lines = ['# high思考默认生成上限：EStG-150完整对比', '',
        f'状态：{report["status"]}；新调用{summary["actual_calls"]}/150；0重试；关闭组/Sun新调用0。', '',
        '原v6/high保持；请求不传max_tokens，按官方默认65536生成上限执行。主指标为五字段coarse pooled micro-F1；modality独立。', '']
    if report['metrics']:
        lines += ['| 条件 | 新调用 | Overall F1 | Modality macro-F1 | 失败/150 |', '|---|---:|---:|---:|---:|']
        for arm, value in report['arms'].items():
            lines.append(f'| {arm} | {value["new_api_calls"]} | {value["overall"]["f1"]:.4f} | {value["modality_macro_f1"]:.4f} | {value["failed_count"]} |')
        lines += ['', f'相对原主表关闭：{report["metrics"]["delta_vs_formal_off_pp"]:+.4f}个百分点；相对0813历史关闭：{report["metrics"]["delta_vs_0813_off_pp"]:+.4f}个百分点。', '',
            'Token统计（p90使用nearest-rank）：', '', '| 项目 | 总量 | 均值 | 中位数 | p90 | 最大值 |', '|---|---:|---:|---:|---:|---:|']
        for name, stat in report['token_statistics'].items():
            if stat:
                lines.append(f'| {name} | {stat["total"]} | {stat["mean"]:.2f} | {stat["median"]} | {stat["p90_nearest_rank"]} | {stat["max"]} |')
        lines += ['', f'生成token总量相对已有0813关闭：{report["generated_token_ratio_vs_0813_off"]:.3f}倍。']
    lines += ['', f'length截断{summary["truncated_calls"]}条；空最终答案{summary["empty_final_calls"]}条；壁钟耗时{summary["runtime_seconds_this_invocation"]}秒。', '',
        '费用按返回usage和公开价格估算，未查账户实扣：', json.dumps(report['cost'], ensure_ascii=False), '',
        '比较边界：', '', *['- ' + item for item in report['limitations']], '',
        '原16K截断及单例393216诊断独立保留，未混入这150条。证据目录：' + OUT.relative_to(ROOT).as_posix()]
    Path(str(REPORT) + '.md').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status': report['status'], 'actual_calls': summary['actual_calls'],
                      'metrics': report['metrics'], 'cost': report['cost']}, ensure_ascii=False), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--execute', action='store_true')
    mode.add_argument('--summarize', action='store_true')
    parser.add_argument('--allow-llm', action='store_true')
    args = parser.parse_args()
    if args.execute or args.summarize:
        plan = shared.read_json(OUT / 'plan.json')
        execute(plan, args.allow_llm) if args.execute else summarize(plan)
    else:
        prepare()


if __name__ == '__main__':
    main()
