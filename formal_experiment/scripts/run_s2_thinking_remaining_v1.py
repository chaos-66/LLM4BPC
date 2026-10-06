"""Finish only never-sent IDs within the original authorized 150-call budget.

Keep the drained parent run immutable, including its balance-concurrency 429.
Use identical request bytes; throttle fresh dispatch, never retry an ID.
"""
from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_s2_thinking_default_v2 as parent

RUN_ID = 'thinking_default_20261007_v2_remaining_v1'
PARENT_OUT = parent.OUT
OUT = parent.shared.RUN_ROOT / RUN_ID
REPORT = ROOT / 'outputs/reports' / ('s2_thinking_' + RUN_ID)
AUTH = ROOT / 'configs/authorization/s2_thinking_default_remaining_20261007_v1.json'
MAX_WORKERS = 5
send_once = parent.send_once


def balance_limit(row):
    error = row.get('response_envelope', {}).get('error') or {}
    message = error.get('message', '') if isinstance(error, dict) else ''
    if row['http_status'] == 429 and 'based on your remaining balance' in message:
        match = re.search(r'concurrency limit of (\d+)', message)
        if match:
            return int(match.group(1))
    return None


def sources():
    return [Path(__file__), AUTH, *parent.sources(),
            *[PARENT_OUT / name for name in ('plan.json', 'calls_ledger.jsonl',
                 'raw_responses.jsonl', 'execution_summary.json', 'run_manifest.json',
                 'result.json', 'git_execution_context.json')],
            Path(str(parent.REPORT) + '_approval_review.json')]


def parent_state():
    plan = parent.shared.read_json(PARENT_OUT / 'plan.json')
    parent.verify(plan, True)
    summary = parent.shared.read_json(PARENT_OUT / 'execution_summary.json')
    raw = parent.shared.core._read_jsonl(PARENT_OUT / 'raw_responses.jsonl')
    ledger = parent.shared.core._read_jsonl(PARENT_OUT / 'calls_ledger.jsonl')
    manifest = parent.shared.read_json(PARENT_OUT / 'run_manifest.json')
    for name, digest in manifest['artifacts'].items():
        if parent.shared.sha_file(PARENT_OUT / name) != digest:
            raise ValueError('Parent artifact changed: ' + name)
    starts = [r for r in ledger if r['state'] == 'started']
    ends = [r for r in ledger if r['state'] == 'completed']
    ids = {r['sample_id'] for r in raw}
    if (summary['complete'] or not summary['abort_reason'] or not 0 < len(raw) < 150
            or summary['actual_calls'] != summary['completed_calls'] or len(raw) != summary['actual_calls']
            or len(ids) != len(raw) or len(starts) != len(ends) or len(starts) != len(raw)
            or {r['sample_id'] for r in starts} != ids or {r['sample_id'] for r in ends} != ids):
        raise ValueError('Parent must be fully drained, unique and partial; no in-doubt sends.')
    requests = {r['sample_id']: r['body_sha256'] for r in plan['requests']}
    start_map = {r['sample_id']: r for r in starts}
    end_map = {r['sample_id']: r for r in ends}
    for row in raw:
        sid = row['sample_id']
        if (sid not in requests or row['request_body_sha256'] != requests[sid]
                or start_map[sid]['request_body_sha256'] != requests[sid]
                or row['response_envelope_sha256'] != end_map[sid]['response_envelope_sha256']
                or parent.shared.sha(row['raw_response_envelope_json'].encode()) != row['response_envelope_sha256']):
            raise ValueError('Parent response/ledger binding failed.')
        if parent.fatal_reason(row) and not (balance_limit(row) is not None and balance_limit(row) > 0):
            raise ValueError('Only the identified balance-concurrency 429 allows fresh-ID continuation.')
    return plan, summary, raw, ledger


def prepare():
    if OUT.exists():
        raise ValueError('Never overwrite an existing continuation.')
    original, summary, raw, _ = parent_state()
    auth = parent.shared.read_json(AUTH)
    seen = {r['sample_id'] for r in raw}
    remaining = [r['sample_id'] for r in original['requests'] if r['sample_id'] not in seen]
    if (auth.get('authorized') is not True or auth['inherited_calls'] != len(raw)
            or auth['max_new_calls'] != len(remaining) or auth['max_combined_calls'] != 150
            or auth['retry_cap'] != 0 or auth['max_workers'] != MAX_WORKERS):
        raise ValueError('Continuation must stay within the existing 150-call user authorization.')
    plan = dict(original)
    plan.update({'run_id': RUN_ID, 'schema_version': 's2_thinking_remaining_plan@1.0.0',
        'authorization': auth, 'prepared_at_utc': datetime.now(timezone.utc).isoformat(),
        'prepared_git_commit': parent.head(), 'inherited_run_id': summary['run_id'],
        'inherited_calls': len(raw), 'max_new_calls': len(remaining), 'remaining_ids': remaining,
        'generation': dict(original['generation'], max_workers=MAX_WORKERS,
            inherited_max_workers=original['generation']['max_workers'],
            balance_concurrency_policy='retain failed row; halve reported limit for fresh IDs only'),
        'source_bindings': {p.relative_to(ROOT).as_posix(): parent.shared.sha_file(p) for p in sources()},
        'limitations': original['limitations'] + [
            '105 parent calls retained, including its balance-concurrency 429; only 45 never-sent IDs dispatched.',
            'Transport concurrency lowered from 12 to 5; further balance limits throttle fresh IDs, never retries.',
            'Missing 429 usage is conservatively reserved in the budget; public-price cost estimates cover known usage only.']})
    parent.shared.write_json(OUT / 'plan.json', plan)
    parent.shared.write_json(Path(str(REPORT) + '_preflight.json'), plan)
    print(json.dumps({'prepared': RUN_ID, 'inherited_calls': len(raw), 'new_call_cap': len(remaining),
                      'combined_call_cap': 150, 'workers': MAX_WORKERS, 'network_calls': 0}), flush=True)
    return plan


def verify(plan, allow_llm):
    original, _, raw, _ = parent_state()
    auth = parent.shared.read_json(AUTH)
    bindings = {p.relative_to(ROOT).as_posix(): parent.shared.sha_file(p) for p in sources()}
    seen = {r['sample_id'] for r in raw}
    remaining = [r['sample_id'] for r in original['requests'] if r['sample_id'] not in seen]
    if (not allow_llm or plan['run_id'] != RUN_ID or not auth['authorized']
            or plan['authorization'] != auth or plan['source_bindings'] != bindings
            or plan['remaining_ids'] != remaining or plan['max_new_calls'] != len(remaining)
            or plan['inherited_calls'] != len(raw) or plan['requests'] != original['requests']
            or plan['budget'] != original['budget'] or plan['generation']['max_workers'] != MAX_WORKERS):
        raise ValueError('Continuation authorization, frozen bindings or combined budget changed.')


def summarize(plan):
    old = parent.OUT, parent.REPORT, parent.RUN_ID
    parent.OUT, parent.REPORT, parent.RUN_ID = OUT, REPORT, RUN_ID
    try:
        return parent.summarize(plan)
    finally:
        parent.OUT, parent.REPORT, parent.RUN_ID = old


def execute(plan, allow_llm):
    verify(plan, allow_llm)
    if (OUT / 'calls_ledger.jsonl').exists() or (OUT / 'raw_responses.jsonl').exists():
        raise ValueError('Continuation already started; no automatic resend.')
    original, old_summary, raw, ledger = parent_state()
    for name in ('calls_ledger.jsonl', 'raw_responses.jsonl'):
        (OUT / name).write_bytes((PARENT_OUT / name).read_bytes())
    gate = parent.shared.core.AblationBudgetGate(plan['budget'], parent.shared.MODEL)
    for row in raw:
        gate.missing_usage_calls += not row['usage_known']
        gate.record_response(row['budget_usage'], row['returned_model'])
    requests = {r['sample_id']: r for r in plan['requests']}
    samples = {s['sample_id']: s for s in parent.shared.core.samples(150)}
    todo = iter([samples[sid] for sid in plan['remaining_ids']])
    key = parent.shared.process_key()
    commit = parent.head()
    dirty = subprocess.check_output(['git', 'status', '--short', '--', 'formal_experiment'],
        cwd=ROOT.parent, text=True, encoding='utf-8').splitlines()
    origin_start = datetime.fromisoformat(ledger[0]['started_at_utc'])
    started = time.monotonic()
    sent = len(raw)
    abort = None
    exhausted = False
    target_workers = MAX_WORKERS
    futures = {}
    changes = [{'reason': 'parent balance concurrency limit 11; use five workers for never-sent IDs',
                'workers': target_workers}]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        while futures or not exhausted:
            while not abort and not exhausted and len(futures) < target_workers:
                item = next(todo, None)
                if item is None:
                    exhausted = True
                    break
                if sent >= 150:
                    raise ValueError('Combined call cap would be exceeded.')
                reserved = sum(requests[s['sample_id']]['estimated_input_tokens'] for s in futures.values())
                try:
                    gate.check_before_send(reserved + requests[item['sample_id']]['estimated_input_tokens'],
                                           (len(futures) + 1) * parent.DEFAULT_TOKENS)
                except parent.shared.core.SepC3Error as exc:
                    abort = str(exc)
                    break
                body = parent.request_bytes(item)
                if parent.shared.sha(body) != requests[item['sample_id']]['body_sha256']:
                    raise ValueError('Request differs from original 150-call plan.')
                parent.shared.core._append_jsonl(OUT / 'calls_ledger.jsonl', {
                    'sample_id': item['sample_id'], 'state': 'started',
                    'request_body_sha256': parent.shared.sha(body),
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
                    'prompt_tokens': requests[item['sample_id']]['estimated_input_tokens'],
                    'completion_tokens': parent.DEFAULT_TOKENS}
                parent.shared.core._append_jsonl(OUT / 'raw_responses.jsonl', row)
                parent.shared.core._append_jsonl(OUT / 'calls_ledger.jsonl', {
                    'sample_id': item['sample_id'], 'state': 'completed',
                    'response_envelope_sha256': row['response_envelope_sha256']})
                raw.append(row)
                gate.missing_usage_calls += not row['usage_known']
                try:
                    gate.record_response(row['budget_usage'], row['returned_model'])
                except parent.shared.core.SepC3Error as exc:
                    abort = abort or str(exc)
                limit = balance_limit(row)
                if limit is not None and limit > 0:
                    target_workers = min(target_workers, max(1, limit // 2))
                    changes.append({'sample_id': item['sample_id'], 'reported_limit': limit,
                                    'workers': target_workers, 'failed_id_retried': False})
                else:
                    abort = abort or parent.fatal_reason(row)
            summary = {'run_id': RUN_ID, 'complete': len(raw) == 150 and not abort,
                'actual_calls': sent, 'completed_calls': len(raw), 'planned_calls': 150,
                'inherited_calls': plan['inherited_calls'], 'new_calls': sent - plan['inherited_calls'],
                'retry': 0, 'new_off_calls': 0, 'new_sun_calls': 0, 'abort_reason': abort,
                'budget_gate': gate.to_dict(), 'execution_git_commit': commit, 'execution_dirty_paths': dirty,
                'runtime_seconds_this_invocation': round((datetime.now(timezone.utc) - origin_start).total_seconds(), 3),
                'continuation_runtime_seconds': round(time.monotonic() - started, 3),
                'inherited_runtime_seconds': old_summary['runtime_seconds_this_invocation'],
                'runtime_gold_access': False, 'project_env_read': False, 'dispatch_transitions': changes,
                'truncated_calls': sum(r['finish_reason'] == 'length' for r in raw),
                'empty_final_calls': sum(not r['raw_response_content'].strip() for r in raw)}
            parent.shared.write_json(OUT / 'execution_summary.json', summary)
            print(json.dumps({'completed': len(raw), 'started': sent, 'planned': 150,
                'workers': target_workers, 'truncated': summary['truncated_calls'],
                'missing_usage': gate.missing_usage_calls, 'abort_reason': abort}), flush=True)
    return summarize(plan)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--allow-llm', action='store_true')
    args = parser.parse_args()
    if args.execute:
        execute(parent.shared.read_json(OUT / 'plan.json'), args.allow_llm)
    else:
        prepare()


if __name__ == '__main__':
    main()
