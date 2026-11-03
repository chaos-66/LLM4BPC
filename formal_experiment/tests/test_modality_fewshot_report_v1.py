"""Offline report accounting and paired-statistic checks on synthetic examples."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fewshot_report_test", ROOT / "scripts/build_sun_modality_fewshot_report_v1.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_paired_counts_keep_missing_predictions_as_errors():
    gold = ["definition", "obligation", "permission", "prohibition"]
    old = [None, "obligation", "permission", "definition"]
    new = ["definition", None, "permission", "prohibition"]
    result = m.paired(gold, old, new)
    assert result["corrected"] == 2 and result["regressed"] == 1
    assert result["by_gold_class"]["obligation"]["regressed"] == 1
    assert result["mcnemar_accuracy_p_exact_two_sided"] == 1.0


def test_f1_vector_and_zero_delta_bootstrap_match_evaluator():
    gold = list(m.LABELS)
    pred = [None, "obligation", "definition", "prohibition"]
    metrics = m.evaluate(gold, pred)
    vector = m.f1_vector([0, 1, 2, 3], [-1, 1, 0, 3])
    assert vector == [metrics["per_class"][c]["f1"] for c in m.LABELS]
    assert all(interval == [0.0, 0.0] for interval in m.bootstrap_delta(gold, pred, pred, repeats=100)["ci95"].values())


def journal_fixture():
    rate = m.llm_se.PRICE_CNY_PER_MILLION["off_peak"]
    raw = json.dumps({"clauses": [{"modality": {"label": "permission"}}]})
    usage = {"prompt_tokens": 100, "completion_tokens": 10}
    start = {"kind": "started", "sample_id": "s", "request_sha256": "request",
             "timestamp": "2026-11-03T05:00:00+00:00", "reserved_cny": 0.2, "price_window": "off_peak"}
    finish = {"kind": "finished", "sample_id": "s", "request_sha256": "request",
              "request_status": "ok", "usage_verified": True, "model_accepted": True,
              "body_hash_match": True, "returned_model": "deepseek-v4-pro", "raw_content": raw,
              "response_sha256": m.boundary.digest(raw.encode()), "label": "permission", "parse_status": "ok",
              "usage": usage, "cost_cny": m.llm_se.cost_cny(usage, rate)}
    requests = [{"sample_id": "s", "fewshot_request_sha256": "request"}]
    auth = {"max_calls": 1, "max_workers": 1, "cap_cny": 20, "price_cny_per_million": m.llm_se.PRICE_CNY_PER_MILLION}
    return [start, finish], requests, auth


def test_complete_audit_and_incomplete_rejection():
    events, requests, auth = journal_fixture()
    finished, audit = m.verify_journal(events, requests, auth)
    assert list(finished) == ["s"] and audit["peak_in_flight"] == 1
    with pytest.raises(ValueError, match="incomplete"):
        m.verify_journal(events[:1], requests, auth)


@pytest.mark.parametrize("field,value,match", [
    ("cost_cny", 4, "cost mismatch"), ("response_sha256", "wrong", "response hash"),
    ("label", "definition", "parsing"), ("returned_model", "different", "returned model")])
def test_audit_rejects_corrupted_evidence(field, value, match):
    events, requests, auth = journal_fixture()
    events[1][field] = value
    with pytest.raises(ValueError, match=match):
        m.verify_journal(events, requests, auth)


def test_budget_and_empty_output_semantics():
    events, requests, auth = journal_fixture()
    tiny = dict(auth, cap_cny=0.01)
    with pytest.raises(ValueError, match="reservation"):
        m.verify_journal(events, requests, tiny)
    events[1].update(raw_content="", response_sha256=m.boundary.digest(b""), label=None, parse_status="no_content")
    _, audit = m.verify_journal(events, requests, auth)
    assert audit["parse_status_counts"] == {"no_content": 1}
