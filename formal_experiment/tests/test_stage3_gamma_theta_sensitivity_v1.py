"""Focused verification of frozen inputs and independently counted scan results."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "stage3_gamma_theta_sensitivity_20261010_v1"
OUT = ROOT / "outputs/evidence" / RUN_ID


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


@pytest.fixture(scope="module")
def report():
    return read(ROOT / "outputs/reports" / (RUN_ID + ".json"))


def test_nine_settings_are_two_single_factor_scans():
    path = ROOT / "scripts/run_stage3_gamma_theta_sensitivity_v1.py"
    spec = importlib.util.spec_from_file_location("s3_gamma_theta_run", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    points = module.points()
    assert len(points) == len(set(points)) == 9
    assert points[0] == (0.55, 0.45)
    assert all(g == 0.55 or t == 0.45 for g, t in points)
    assert {g for g, t in points if t == 0.45} == {0.35, 0.45, 0.55, 0.65, 0.75}
    assert {t for g, t in points if g == 0.55} == {0.25, 0.35, 0.45, 0.55, 0.65}


def test_eighteen_evaluations_fixed_population_and_no_api(report):
    assert report["unique_settings"] == 9
    assert report["method_evaluations"] == 18
    assert len(report["rows"]) == 20
    assert report["llm_api_calls"] == report["network_calls"] == 0
    assert report["primary_results_changed"] is False
    assert report["order_scope_changed"] is False
    for point in report["results"]:
        for result in point["methods"].values():
            assert result["overall"]["scored_cells"] == 201
            assert result["overall"]["positive_support"] == 69
            assert result["overall"]["negative_support"] == 132
    # Theta only changes actor checks, not action or order checks.
    theta_points = [p for p in report["results"] if p["gamma"] == 0.55]
    for method in ("sun", "ours"):
        for typ in ("missing_action", "out_of_order"):
            blocks = [p["methods"][method]["per_type"][typ] for p in theta_points]
            assert all(b == blocks[0] for b in blocks)


def test_independent_cell_counts_match_all_eighteen_evaluations(report):
    reference = read(ROOT / "data/development/stage3_winter_paper_rerun_20261010_v1/evaluation_reference.json")
    for point in report["results"]:
        signals = read(OUT / f"signals_gamma_{point['gamma']:.2f}_theta_{point['theta']:.2f}.json")["signals"]
        for method in ("sun", "ours"):
            by_type = {}
            for typ in ("missing_action", "incorrect_actor", "out_of_order"):
                counts = {k: 0 for k in ("TP", "FP", "FN", "TN", "unknown_positive", "unknown_negative")}
                for case in reference["cases"]:
                    if typ == "out_of_order" and reference["order_scope"].get(case["requirement_id"]) != "TYPE_A_explicit_action_precedence":
                        continue
                    expected = case["reference_states"].get(typ)
                    if expected not in ("violated", "satisfied"):
                        continue
                    actual = signals[method][case["case_id"]][typ]["status"]
                    if expected == "violated":
                        counts["TP" if actual == "violated" else "FN"] += 1
                        counts["unknown_positive"] += int(actual == "unknown")
                    elif actual == "violated":
                        counts["FP"] += 1
                    elif actual == "satisfied":
                        counts["TN"] += 1
                    else:
                        counts["unknown_negative"] += 1
                block = point["methods"][method]["per_type"][typ]
                assert {k: block[k] for k in counts} == counts
                by_type[typ] = counts
                denom = 2 * counts["TP"] + counts["FP"] + counts["FN"]
                assert block["f1"] == pytest.approx(2 * counts["TP"] / denom if denom else 0)
            overall = point["methods"][method]["overall"]
            pooled = {k: sum(c[k] for c in by_type.values()) for k in by_type["missing_action"]}
            assert {k: overall[k] for k in pooled} == pooled
            denom = 2 * pooled["TP"] + pooled["FP"] + pooled["FN"]
            assert overall["f1"] == pytest.approx(2 * pooled["TP"] / denom if denom else 0)


def test_baseline_all_signal_objects_equal_frozen_evidence(report):
    frozen = read(ROOT / "outputs/evidence/stage3_comparison_check_20261010_v1/sun_ours_selected_dev_signals_v1.json")
    actual = read(OUT / "signals_gamma_0.55_theta_0.45.json")
    assert actual["signals"] == frozen["signals"]
    assert sum(len(types) for cases in actual["signals"].values() for types in cases.values()) == 690
    assert report["baseline_complete_signal_equality"] is True


def test_theta_changes_signals_even_when_sun_scored_curve_is_flat():
    low = read(OUT / "signals_gamma_0.55_theta_0.25.json")["signals"]
    high = read(OUT / "signals_gamma_0.55_theta_0.65.json")["signals"]
    reference = {c["case_id"]: c for c in read(ROOT / "data/development/stage3_winter_paper_rerun_20261010_v1/evaluation_reference.json")["cases"]}
    changes = {}
    for method in ("sun", "ours"):
        changes[method] = [cid for cid in low[method]
                           if low[method][cid]["incorrect_actor"]["status"] != high[method][cid]["incorrect_actor"]["status"]]
    assert changes["sun"] == ["case_de1137fcd3ae"]
    assert reference[changes["sun"][0]]["reference_states"]["incorrect_actor"] == "not_applicable"
    assert len(changes["ours"]) == 9
    assert sum(reference[cid]["reference_states"]["incorrect_actor"] in ("violated", "satisfied")
               for cid in changes["ours"]) == 7


def test_manifest_artifacts_and_inputs_are_unchanged():
    import hashlib
    manifest = read(OUT / "manifest.json")
    for binding in manifest["input_bindings"].values():
        assert hashlib.sha256(Path(binding["path"]).read_bytes()).hexdigest() == binding["sha256"]
    for artifact in manifest["signal_artifacts"] + manifest["report_artifacts"]:
        assert hashlib.sha256((ROOT / artifact["path"]).read_bytes()).hexdigest() == artifact["sha256"]
    applicability = read(OUT / "known_applicability.json")
    assert applicability["reference_states_included"] is False
    assert all(set(row) == {"case_id", "requirement_id"} for row in applicability["targets"])
