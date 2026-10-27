# -*- coding: utf-8 -*-
"""Focused tests for the contract-v2 formal main view (original Gold spans).

User decision 2026-10-27: the Stage 2 paper main report uses the ORIGINAL
annotated Gold spans.  The superseded coarse view merged every semantic field
of a sentence into one ``[min(start), max(end))`` envelope on the GOLD side
only, so a prediction sitting between two annotated spans earned match credit
without overlapping any annotated span.

Covered here:

1. a Gold gap cannot produce a match (real audit case ``estg_000504``)
2. several Gold spans of one field stay independent (no auto-envelope)
3. a genuine overlap still matches under the unchanged overlap rule
4. the ``[start, end)`` right-open boundary is strict
5. Table I and Table II share one evaluation definition
6. the historical coarse view stays readable and is never used by the new
   paper entry points
7. Part 3 (Stage 3) is not in the changed call chain
"""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for candidate in (ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from bpc_hybrid.formal_stage2_evaluation import (  # noqa: E402
    predictions_to_evaluator,
)
from bpc_hybrid.g04_coarse_view import build_coarse_view  # noqa: E402
from bpc_hybrid.sep_c3_modular_evaluation import evaluate_coarse  # noqa: E402
from bpc_hybrid.sep_c3_primary_evaluation import (  # noqa: E402
    CONTRACT_PATH,
    LEGACY_COARSE_VIEW_ID,
    MATCH_RULE,
    PRIMARY_VIEW_ID,
    evaluate_primary_view,
    primary_gold_view,
)
from bpc_hybrid.stage2_sun_literal_overlap import (  # noqa: E402
    evaluate_sun_literal_overlap,
)

GOLD_PATH = ROOT / "data" / "gold" / "stage2" / "estg150_formal_gold_v1.json"
LLM_SE_PATH = (ROOT / "data" / "predictions" / "direct_llm_formal_arm_v1"
               / "predictions.json")
PATIENT = "estg_000504"


def _gold_doc() -> dict:
    return json.loads(GOLD_PATH.read_text(encoding="utf-8"))


def _llm_se_attempt() -> dict:
    records = json.loads(LLM_SE_PATH.read_text(encoding="utf-8"))["records"]
    return next(r for r in records if r["sample_id"] == PATIENT)


def _one(gold_records, attempt, field: str) -> dict:
    report = evaluate_sun_literal_overlap(
        [gold_records[0]] if isinstance(gold_records, list) else [gold_records],
        [attempt],
        dataset_id="independently_reconstructed_estg_150_v1",
        method_id="unit",
    )
    return report["per_field"][field]


def _single(records: list[dict], sample_id: str) -> dict:
    return next(r for r in records if r["sample_id"] == sample_id)


# --------------------------------------------------------------------- test 1
def test_prediction_in_gold_gap_gets_no_match_credit() -> None:
    """estg_000504: Gold actors are [0,12) and [241,253); LLM-SE predicts the
    pronoun "it" at [227,229).  It sits inside the superseded envelope [0,253)
    but overlaps no annotated actor, so it must NOT be counted as matched."""
    gold_doc = _gold_doc()
    attempt = _llm_se_attempt()

    primary_gold = [ _single(primary_gold_view(gold_doc), PATIENT)]
    coarse_gold = [_single(build_coarse_view(gold_doc), PATIENT)]

    # the prediction really is the unannotated gap
    pred_actors = [
        (s["start"], s["end"])
        for clause in attempt["record"]["clauses"]
        for s in (clause.get("actors") or [])]
    assert (227, 229) in pred_actors
    assert attempt["record"]["source_text"][227:229] == "it"

    fine = _one(primary_gold, attempt, "actor")
    coarse = _one(coarse_gold, attempt, "actor")

    assert fine["extracted"] == 2
    assert fine["matched_predictions"] == 1, (
        "the gap prediction must not be credited on the original Gold spans")
    assert coarse["matched_predictions"] == 2, (
        "sanity: the superseded envelope view did credit the gap prediction")


# --------------------------------------------------------------------- test 2
def test_multiple_gold_spans_of_one_field_stay_independent() -> None:
    gold_doc = _gold_doc()
    rec = _single(primary_gold_view(gold_doc), PATIENT)
    actor_spans = sorted(
        (s["start"], s["end"])
        for clause in rec["clauses"] for s in (clause.get("actors") or []))
    assert actor_spans == [(0, 12), (241, 253)], (
        "the primary Gold view must keep every annotated span separate")

    coarse = _single(build_coarse_view(gold_doc), PATIENT)
    coarse_spans = [(s["start"], s["end"])
                    for s in coarse["clauses"][0]["actors"]]
    assert coarse_spans == [(0, 253)], "legacy coarse view keeps the envelope"

    # global reference-span counts (contract v2 records 824 vs 459)
    def count(records: list[dict]) -> int:
        return sum(
            sum(len(clause.get(plural) or [])
                for clause in r.get("clauses") or [])
            for r in records
            for plural in ("actors", "actions", "conditions", "constraints",
                           "exceptions"))

    assert count(primary_gold_view(gold_doc)) == 824
    assert count(build_coarse_view(gold_doc)) == 459


# --------------------------------------------------------------------- test 3
def test_genuine_overlap_still_matches() -> None:
    gold = {"sample_id": "s1", "clauses": [
        {"actors": [{"start": 0, "end": 12},
                    {"start": 241, "end": 253}]}]}
    attempt = {"sample_id": "s1", "request_status": "ok", "record": {"clauses": [
        {"actors": [{"start": 0, "end": 12},     # exact
                    {"start": 10, "end": 20},    # partial overlap of [0,12)
                    {"start": 250, "end": 260},  # partial overlap of [241,253)
                    {"start": 227, "end": 229}]}]}}  # in the gap
    field = _one([gold], attempt, "actor")
    assert field["ground_truth"] == 2
    assert field["extracted"] == 4
    assert field["matched_predictions"] == 3
    assert field["matched_ground_truth"] == 2
    # independence: two predictions may both cover the same Gold span
    assert field["precision"] == pytest.approx(0.75)
    assert field["recall"] == pytest.approx(1.0)


# --------------------------------------------------------------------- test 4
def test_half_open_interval_boundary_is_strict() -> None:
    gold = {"sample_id": "s2", "clauses": [
        {"actors": [{"start": 10, "end": 20}]}]}

    touching = {"sample_id": "s2", "request_status": "ok", "record": {
        "clauses": [{"actors": [{"start": 0, "end": 10},
                                {"start": 20, "end": 30}]}]}}
    field = _one([gold], touching, "actor")
    assert field["matched_predictions"] == 0, (
        "[start,end): touching endpoints share no character")
    assert field["matched_ground_truth"] == 0

    one_char = {"sample_id": "s2", "request_status": "ok", "record": {
        "clauses": [{"actors": [{"start": 9, "end": 11}]}]}}
    assert _one([gold], one_char, "actor")["matched_predictions"] == 1
    assert _one([gold], one_char, "actor")["matched_ground_truth"] == 1


# --------------------------------------------------------------------- test 5
def test_table1_and_table2_share_the_same_definition() -> None:
    import importlib.util

    def load(module_name: str, filename: str):
        spec = importlib.util.spec_from_file_location(
            module_name, ROOT / "scripts" / filename)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    table1 = load("t1_builder_view", "build_stage2_table1_paper_final_v1.py")
    table2 = load("t2_builder_view", "run_v6_factorial_ablation_v1.py")

    assert (ROOT / CONTRACT_PATH).is_file()
    assert table1.PRIMARY_VIEW_ID == PRIMARY_VIEW_ID == table2.PRIMARY_VIEW_ID
    # both paper entry points default to the formal main view
    assert table1.collect.__defaults__ == (PRIMARY_VIEW_ID,)
    assert inspect.signature(table2._build_report).parameters["view"].default \
        == PRIMARY_VIEW_ID
    assert table2.out_paths(PRIMARY_VIEW_ID) == table2.OUT_PATHS[PRIMARY_VIEW_ID]

    # and they produce identical numbers for the same frozen predictions
    gold_doc = _gold_doc()
    attempts = predictions_to_evaluator(
        json.loads(LLM_SE_PATH.read_text(encoding="utf-8"))["records"])
    via_table1 = table1.collect(PRIMARY_VIEW_ID)
    via_table2 = table2.evaluate_arm(
        gold_doc, attempts, method_id="direct_llm", view=PRIMARY_VIEW_ID)
    shared = evaluate_primary_view(
        gold_doc, attempts, dataset_id="independently_reconstructed_estg_150_v1",
        method_id="direct_llm")
    assert shared["view"] == PRIMARY_VIEW_ID
    assert shared["match_rule"] == MATCH_RULE
    t1_arm = via_table1["arms"]["direct_llm"]["overall_pooled_five_span_fields"]
    for key in ("precision", "recall", "f1", "ground_truth", "extracted"):
        assert t1_arm[key] == shared["span"]["pooled_five_span_fields"][key]
        assert via_table2["five_field_micro"][key] == \
            shared["span"]["pooled_five_span_fields"][key]


# --------------------------------------------------------------------- test 6
def test_historical_coarse_view_readable_and_not_used_by_primary() -> None:
    gold_doc = _gold_doc()
    attempts = predictions_to_evaluator(
        json.loads(LLM_SE_PATH.read_text(encoding="utf-8"))["records"])

    # (a) the historical view still reproduces its published numbers
    legacy = evaluate_coarse(gold_doc, attempts, method_id="direct_llm")
    assert legacy["view"] == LEGACY_COARSE_VIEW_ID
    assert round(legacy["coarse_five_field_micro"]["f1"], 4) == 0.8378
    assert legacy["coarse_five_field_micro"]["ground_truth"] == 459

    # (b) the formal entry point does not reach the envelope transform at all
    import bpc_hybrid.sep_c3_primary_evaluation as primary_mod
    source = Path(primary_mod.__file__).read_text(encoding="utf-8")
    code_lines = [line for line in source.splitlines()
                  if line.strip().startswith(("import ", "from "))]
    assert not [line for line in code_lines if "g04_coarse_view" in line]
    assert not [line for line in code_lines if "build_coarse_view" in line]

    result = evaluate_primary_view(gold_doc, attempts, method_id="direct_llm")
    assert result["view"] == PRIMARY_VIEW_ID
    assert round(result["five_field_micro"]["f1"], 4) == 0.7294
    assert result["five_field_micro"]["ground_truth"] == 824


def test_frozen_historical_modules_are_byte_identical() -> None:
    """The modules the authorized historical runs were pinned to must not
    change, so every coarse number stays reproducible from its own code."""
    import hashlib

    budget = json.loads(
        (ROOT / "configs" / "sep_c3_modular_ablation_budget_v2.json")
        .read_text(encoding="utf-8"))["evaluator_binding"]
    for key_path, key_sha in (
            ("coarse_metric_module", "coarse_metric_sha256"),
            ("frozen_evaluator_module", "frozen_evaluator_sha256")):
        path = ROOT / budget[key_path]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == budget[key_sha], (
            f"{budget[key_path]} drifted from its frozen binding")


# --------------------------------------------------------------------- test 7
def test_stage3_not_in_the_changed_call_chain() -> None:
    changed = ("g04_coarse_view", "formal_stage2_evaluation",
               "sep_c3_modular_evaluation", "stage2_sun_literal_overlap")
    offenders = []
    for path in sorted((SRC / "bpc_hybrid").glob("*.py")):
        name = path.name
        if not name.startswith(("s3_", "s3")):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for module in changed:
            if f"bpc_hybrid.{module}" in text or f"from bpc_hybrid import {module}" in text:
                offenders.append(f"{name} -> {module}")
    assert offenders == [], (
        "Part 3 modules must not depend on the Stage 2 evaluation modules: "
        f"{offenders}")

    # the Stage 2 evaluation modules do not reach into Part 3 either
    for path in (SRC / "bpc_hybrid" / "formal_stage2_evaluation.py",
                 SRC / "bpc_hybrid" / "sep_c3_modular_evaluation.py",
                 SRC / "bpc_hybrid" / "g04_coarse_view.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        assert "import bpc_hybrid.s3" not in text
        assert "from bpc_hybrid.s3" not in text


# --------------------------------------------------------------------- freeze
def test_frozen_capsule_matches_the_published_reports() -> None:
    capsule = (ROOT / "outputs" / "evidence"
               / "g04_fine_gold_span_formal_results_v2" / "results.json")
    table1 = ROOT / "outputs" / "reports" / "stage2_table1_paper_final_v2.json"
    table2 = (ROOT / "outputs" / "reports"
              / "stage2_table2_prompt_ablation_paper_final_v3.json")
    for path in (capsule, table1, table2):
        if not path.exists():
            pytest.skip(f"artifact unavailable: {path.name}")

    frozen = json.loads(capsule.read_text(encoding="utf-8"))
    t1 = json.loads(table1.read_text(encoding="utf-8"))
    t2 = json.loads(table2.read_text(encoding="utf-8"))

    assert t1["view"] == t2["view"] == PRIMARY_VIEW_ID
    for method_id, row in frozen["table1"].items():
        assert abs(t1["arms"][method_id]["overall_pooled_five_span_fields"]["f1"]
                   - row["overall_micro_f1_unrounded"]) < 1e-12
    for arm, row in frozen["table2"].items():
        assert abs(t2["arms"][arm]["overall_micro_f1"]
                   - row["micro_f1_unrounded"]) < 1e-12

    # the historical coarse capsules are still present and still coarse
    history1 = ROOT / "outputs" / "reports" / "stage2_table1_paper_final_v1.json"
    history2 = (ROOT / "outputs" / "reports"
                / "stage2_table2_prompt_ablation_paper_final_v2.json")
    h1 = json.loads(history1.read_text(encoding="utf-8"))
    h2 = json.loads(history2.read_text(encoding="utf-8"))
    assert h1["view"] == LEGACY_COARSE_VIEW_ID
    # the historical Table II capsule predates the ``view`` field; its coarse
    # identity is pinned by its metric id and its 459 reference spans
    assert h2["primary_metric"] == "coarse_five_field_micro_f1"
    assert h2["arms"]["111"]["coarse_five_field_micro_f1"] == pytest.approx(
        0.8224493117168078)
