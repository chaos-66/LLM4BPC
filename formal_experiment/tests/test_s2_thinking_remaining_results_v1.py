"""Apply the four saved-artifact checks to the combined, never-retried run."""
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import run_s2_thinking_remaining_v1 as run
import test_s2_thinking_default_results_v2 as checks


@pytest.fixture(scope='module')
def saved():
    old = checks.run
    checks.run = SimpleNamespace(OUT=run.OUT, REPORT=run.REPORT, RUN_ID=run.RUN_ID,
        verify=run.verify, shared=run.parent.shared, transport=run.parent.transport)
    try:
        yield {'plan': run.parent.shared.read_json(run.OUT / 'plan.json'),
               'manifest': run.parent.shared.read_json(run.OUT / 'run_manifest.json'),
               'report': run.parent.shared.read_json(run.OUT / 'result.json'),
               'raw': run.parent.shared.core._read_jsonl(run.OUT / 'raw_responses.jsonl'),
               'ledger': run.parent.shared.core._read_jsonl(run.OUT / 'calls_ledger.jsonl')}
    finally:
        checks.run = old


def test_combined_manifest_sources_and_checkout_bytes(saved):
    checks.test_manifest_and_git_checkout_preserve_sources_and_every_artifact(saved)
    for name in ('raw_responses.jsonl', 'calls_ledger.jsonl'):
        assert (run.OUT / name).read_bytes().startswith((run.PARENT_OUT / name).read_bytes())


def test_combined_unique_ledger_and_remaining_only_dispatch(saved):
    checks.test_unique_ledger_requests_full_envelopes_and_budget_accounting(saved)
    old = run.parent.shared.core._read_jsonl(run.PARENT_OUT / 'raw_responses.jsonl')
    old_ids = {r['sample_id'] for r in old}
    new_rows = saved['raw'][len(old):]
    assert len(old) == saved['plan']['inherited_calls'] == 105
    assert not old_ids.intersection(r['sample_id'] for r in new_rows)
    assert len(new_rows) <= saved['plan']['max_new_calls'] == 45
    if saved['report']['execution']['complete']:
        assert len(new_rows) == 45
        assert {r['sample_id'] for r in new_rows} == set(saved['plan']['remaining_ids'])
    failed = [r for r in saved['raw'] if r['sample_id'] == 'estg_000313']
    assert len(failed) == 1 and failed[0]['http_status'] == 429


def test_combined_predictions_failure_denominator_and_four_shared_evaluations(saved):
    checks.test_predictions_and_all_four_evaluations_reproduce_with_fixed_150_denominator(saved)


def test_combined_reasoning_final_usage_distributions_and_cost(saved):
    checks.test_reasoning_final_distributions_historical_ratio_and_public_price_estimates(saved)
