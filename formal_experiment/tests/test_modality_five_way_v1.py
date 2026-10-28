"""Focused tests for the Sun modality five-way supplement.

Covers only the new supplement surface:

* the shared evaluator's failure accounting and metric arithmetic;
* CFKW priority, fallback and negated-permission behaviour;
* the hash-bound dataset loaders and the label-blind text loader;
* the LLM-SE cost gate, price window and label extraction, without any
  network call.

No `.env` read, no API call, no Gold mutation, no experiment rerun.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bpc_hybrid.modality_benchmark import cfkw, data, llm_se  # noqa: E402
from bpc_hybrid.modality_benchmark.metrics import (  # noqa: E402
    LABELS,
    NO_PREDICTION,
    evaluate,
)


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------


def test_evaluate_perfect_predictions() -> None:
    gold = ["definition", "obligation", "permission", "prohibition"]
    result = evaluate(gold, list(gold))
    assert result["accuracy"] == 1.0
    assert result["macro_f1"] == 1.0
    assert result["failures"] == 0
    assert result["n"] == 4


def test_failed_samples_stay_in_denominator() -> None:
    gold = ["obligation", "obligation", "permission", "prohibition"]
    pred = ["obligation", None, None, "prohibition"]
    result = evaluate(gold, pred)
    assert result["n"] == 4
    assert result["failures"] == 2
    assert result["failure_rate"] == pytest.approx(0.5)
    assert result["accuracy"] == pytest.approx(0.5)
    # No-prediction rows are false negatives, never false positives.
    assert result["per_class"]["obligation"]["fp"] == 0
    assert result["per_class"]["obligation"]["recall"] == pytest.approx(0.5)
    assert result["per_class"]["permission"]["precision"] == 0.0
    assert result["coverage_restricted_secondary"]["n"] == 2


def test_confusion_matrix_has_no_prediction_column() -> None:
    result = evaluate(["definition", "obligation"], ["definition", None])
    matrix = result["confusion_matrix"]
    assert NO_PREDICTION in matrix["column_order"]
    assert matrix["as_dict"]["obligation"][NO_PREDICTION] == 1
    assert len(matrix["label_order"]) == 4


def test_evaluate_rejects_unknown_labels() -> None:
    with pytest.raises(ValueError):
        evaluate(["definition"], ["nonsense"])
    with pytest.raises(ValueError):
        evaluate(["nonsense"], ["definition"])


# ---------------------------------------------------------------------------
# CFKW
# ---------------------------------------------------------------------------


def test_cfkw_priority_prohibition_before_permission() -> None:
    classifier = cfkw.KeywordClassifier(
        priority=["prohibition", "permission", "obligation", "definition"],
        fallback="obligation",
    )
    decision = classifier.decide("der steuerpflichtige darf nicht abziehen")
    assert decision.label == "prohibition"
    assert decision.cue == ("darf", "nicht")


def test_cfkw_negated_permission_window() -> None:
    classifier = cfkw.KeywordClassifier(
        priority=["prohibition", "permission", "obligation", "definition"],
        fallback="obligation",
    )
    decision = classifier.decide("die rentenbeträge dürfen sich nicht vermindern")
    assert decision.label == "prohibition"


def test_cfkw_fallback_is_explicit() -> None:
    classifier = cfkw.KeywordClassifier(
        priority=["prohibition", "permission", "obligation", "definition"],
        fallback="definition",
    )
    decision = classifier.decide("völlig neutraler satz ohne signalwörter")
    assert decision.label == "definition"
    assert decision.tier is None


def test_cfkw_priority_must_be_total_order() -> None:
    with pytest.raises(ValueError):
        cfkw.KeywordClassifier(priority=["prohibition", "permission"], fallback="obligation")


def test_cfkw_candidates_are_complete_and_deterministic() -> None:
    for name, spec in cfkw.CANDIDATES.items():
        assert sorted(spec["priority"]) == sorted(LABELS), name
        assert spec["fallback"] in LABELS


# ---------------------------------------------------------------------------
# Dataset binding
# ---------------------------------------------------------------------------


def test_splits_verify_and_do_not_overlap() -> None:
    inventory = data.verify_splits()
    assert inventory["test"]["rows"] == 426
    assert inventory["train"]["rows"] == 1985
    assert inventory["dev"]["rows"] == 420


def test_text_only_loader_ignores_labels() -> None:
    pairs = data.load_split_text_only("test")
    assert len(pairs) == 426
    sample_id, text = pairs[0]
    assert isinstance(sample_id, str) and sample_id
    assert isinstance(text, str) and text.strip()


# ---------------------------------------------------------------------------
# LLM-SE budget and parsing
# ---------------------------------------------------------------------------


def test_peak_window_boundaries() -> None:
    def at(hour: int, minute: int = 0) -> datetime:
        return datetime(2026, 10, 28, hour, minute, tzinfo=llm_se.BEIJING)

    assert llm_se.is_peak(at(9, 0)) is True
    assert llm_se.is_peak(at(11, 59)) is True
    assert llm_se.is_peak(at(12, 0)) is False
    assert llm_se.is_peak(at(13, 59)) is False
    assert llm_se.is_peak(at(14, 0)) is True
    assert llm_se.is_peak(at(17, 59)) is True
    assert llm_se.is_peak(at(18, 0)) is False
    assert llm_se.is_peak(at(2, 0)) is False


def test_weekend_is_off_peak() -> None:
    saturday = datetime(2026, 10, 31, 10, 0, tzinfo=llm_se.BEIJING)
    assert llm_se.is_peak(saturday) is False


def test_cost_gate_refuses_before_send() -> None:
    gate = llm_se.CostGate(cap_cny=1.0, reserve_output_tokens=1200)
    rate = llm_se.PRICE_CNY_PER_MILLION["peak"]
    now = datetime(2026, 10, 28, 10, 0, tzinfo=llm_se.BEIJING)
    with pytest.raises(llm_se.BudgetExceeded):
        gate.reserve(200_000, rate, now)


def test_cost_gate_settles_actual_usage() -> None:
    gate = llm_se.CostGate(cap_cny=20.0, reserve_output_tokens=1200)
    rate = llm_se.PRICE_CNY_PER_MILLION["off_peak"]
    now = datetime(2026, 10, 28, 19, 0, tzinfo=llm_se.BEIJING)
    reservation = gate.reserve(6000, rate, now)
    actual = gate.settle(
        {"prompt_tokens": 6000, "prompt_cache_hit_tokens": 0,
         "prompt_cache_miss_tokens": 6000, "completion_tokens": 800},
        rate,
        reservation,
    )
    expected = (6000 * 4.5 + 800 * 13.5) / 1_000_000
    assert actual == pytest.approx(expected)
    assert gate.spent_cny == pytest.approx(expected)
    assert gate.reserved_cny == 0.0


def test_cost_uses_cache_miss_when_split_missing() -> None:
    rate = llm_se.PRICE_CNY_PER_MILLION["peak"]
    with_split = llm_se.cost_cny(
        {"prompt_tokens": 1000, "prompt_cache_hit_tokens": 0,
         "prompt_cache_miss_tokens": 1000, "completion_tokens": 100},
        rate,
    )
    without_split = llm_se.cost_cny(
        {"prompt_tokens": 1000, "completion_tokens": 100}, rate
    )
    assert with_split == pytest.approx(without_split)


def test_extract_modality_label_paths() -> None:
    ok = json.dumps({"clauses": [{"modality": {"label": "obligation"}}]})
    assert llm_se.extract_modality_label(ok)["label"] == "obligation"
    assert llm_se.extract_modality_label("not json")["status"] == "invalid_json"
    assert llm_se.extract_modality_label(json.dumps({"clauses": []}))["status"] == "no_clauses"
    bad = json.dumps({"clauses": [{"modality": {"label": "unknown_thing"}}]})
    assert llm_se.extract_modality_label(bad)["status"] == "invalid_label"
    empty = json.dumps({"clauses": [{"modality": {}}]})
    assert llm_se.extract_modality_label(empty)["status"] == "no_label"


def test_frozen_prompt_hash_matches() -> None:
    prompt, system, few_shot = llm_se.load_frozen_prompt()
    assert llm_se.PROMPT_SHA256 and len(llm_se.PROMPT_SHA256) == 64
    assert "modality is one of" in system
    assert "Example 1" in few_shot


def test_request_body_is_frozen_sampling() -> None:
    body = llm_se.request_body("sample_x", "der satz")
    assert body["model"] == llm_se.MODEL_ALIAS
    assert body["temperature"] == 0.0
    assert body["top_p"] == 1.0
    assert body["max_tokens"] == llm_se.MAX_OUTPUT_TOKENS
    assert body["thinking"] == {"type": "disabled"}


def test_request_body_serialisations_are_canonically_equal() -> None:
    """The two recorded digests differ only by JSON key order, not payload."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "verify_bodies", ROOT / "scripts/verify_llm_se_request_bodies_v1.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    body = llm_se.request_body("sample_y", "Der Antrag ist zu stellen.")
    legacy = module.legacy_bytes(body)
    wire = module.wire_bytes(body)
    assert legacy != wire
    assert json.loads(legacy) == json.loads(wire)
    assert list(json.loads(wire)) == list(module.WIRE_ORDER) or set(
        json.loads(wire)
    ) == set(module.WIRE_ORDER)
