"""Check population loss, label leakage, and the persisted native replay."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from stage3_winter_paper_metrics_v1 import evaluate_dev_method
from run_stage3_winter_paper_rerun_v1 import (
    BUNDLE, CONFIG, OUT, REPORT, CachedNLP, read, sha, validate_inference,
    validate_predictions, verify_bindings,
)


def test_unknowns_do_not_disappear_from_denominator():
    cases = [{"case_id": "positive", "requirement_id": "r", "split": "development",
              "reference_states": {"missing_action": "violated"}},
             {"case_id": "negative", "requirement_id": "r", "split": "development",
              "reference_states": {"missing_action": "satisfied"}}]
    m = evaluate_dev_method("winter", cases, {}, {})["overall"]
    assert (m["FN"], m["TN"], m["unknown_positive"], m["unknown_negative"], m["scored_cells"]) == (1, 0, 1, 1, 2)
    assert m["coverage"] == 0


def test_inference_rejects_labels_and_partial_population():
    with pytest.raises(RuntimeError, match="forbidden inference fields"):
        validate_inference({"gold_labels_present": False, "items": [
            {"case_id": "a", "bpmn_path": "x", "process_id": "p", "reference_states": {}}
        ]}, {"rules": []})
    with pytest.raises(RuntimeError, match="incomplete Winter population"):
        validate_predictions([], {("a", "r")})


def test_cached_documents_preserve_native_winter_scores():
    from run_stage3_winter_cpu_v1 import configure_cpu
    configure_cpu()
    import spacy
    from bpc_hybrid.winter_stage3.winter_clause import parse_regulation_paragraph
    from bpc_hybrid.winter_stage3.winter_model import parse_bpmn_file_winter
    from bpc_hybrid.winter_stage3.winter_pair import WinterPair
    from bpc_hybrid.winter_stage3.winter_similarity import WinterSimilarity
    nlp = spacy.load("en_core_web_sm")
    cached = CachedNLP(nlp)
    lexicon = ROOT.parent / "references/winter_2020_model_check/model_check/input/files"
    stop, signals, sequences = [set((lexicon / name).read_text(encoding="utf-8").splitlines())
                               for name in ("stopwords.txt", "signalwords.txt", "sequencemarkers.txt")]
    item = read(BUNDLE / "inference_view.json")["items"][0]
    source = read(BUNDLE / "regulation_sources.json")["rules"][0]
    costs = []
    for pipeline in (nlp, cached):
        paragraph = parse_regulation_paragraph(source["rule_id"], source["text"], pipeline, stop, signals, sequences,
                                               only_constraints=True)
        model = parse_bpmn_file_winter(ROOT / item["bpmn_path"], pipeline, stop)
        pair = WinterPair(pipeline, WinterSimilarity(pipeline), model, paragraph,
                          {"controller", "processor", "data subject"}, 0.4, 0.8)
        costs.append((pair.fitness, pair.cost_obligation, pair.cost_resource, pair.cost_so))
    assert costs[0] == costs[1]
    assert cached("controller") is cached("controller")


def test_frozen_snapshot_and_complete_run():
    cfg, manifest = read(CONFIG), read(OUT / "run_manifest.json")
    verify_bindings(cfg["evaluation_bindings"])
    verify_bindings(cfg["code_bindings"])
    assert manifest["status"] == "completed"
    assert (manifest["cases"], manifest["rules"], manifest["pair_count"], manifest["signals"]) == (115, 33, 3795, 11385)
    assert manifest["config_sha256"] == sha(CONFIG)
    for name, digest in manifest["artifacts"].items():
        assert sha(OUT / name) == digest
    assert not manifest["gold_read_by_runner"]
    assert not manifest["evaluation_reference_read_by_runner"]
    assert manifest["llm_api_calls"] == manifest["network_calls"] == manifest["native_exception_count"] == 0
    cpu = read(OUT / "execution_manifest.json")
    assert cpu["core_run_manifest_sha256"] == sha(OUT / "run_manifest.json")
    assert cpu["runtime_launcher_sha256"] == sha(ROOT / "scripts/run_stage3_winter_cpu_v1.py")
    rows = read(OUT / "predictions.json")["records"]
    validate_predictions(rows, {(c, r) for c in manifest["case_ids"] for r in manifest["rule_ids"]})


def test_same_paper_denominator_and_fresh_metric_recalculation():
    report = read(REPORT.with_suffix(".json"))
    ref = read(BUNDLE / "evaluation_reference.json")
    rows = read(OUT / "predictions.json")["records"]
    lookup = {(r["case_id"], r["rule_id"]): r for r in rows}
    predictions = {("winter", c["case_id"], t): lookup[(c["case_id"], c["requirement_id"])]["signals"][t]
                   for c in ref["cases"] for t in ("missing_action", "incorrect_actor", "out_of_order")}
    result = evaluate_dev_method("winter", ref["cases"], predictions, ref["order_scope"])
    assert result == report["winter_metrics"]
    m = result["overall"]
    assert (m["scored_cells"], m["positive_support"], m["negative_support"]) == (201, 69, 132)
    assert m["TP"] + m["FN"] == 69
    assert m["FP"] + m["TN"] + m["unknown_negative"] == 132
    canonical = read(BUNDLE / "canonical_table3.json")
    assert report["main_table"]["Sun-style Rules-Only"] == canonical["methods"]["Sun"]
    assert report["main_table"]["LLM-RE"] == canonical["methods"]["Ours"]
    assert not report["formal_release_ready"]
