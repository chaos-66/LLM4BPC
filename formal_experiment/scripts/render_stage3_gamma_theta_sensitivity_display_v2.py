"""Render Sun/LLM-SE display copies from the frozen 2026-10-10 scan.

This script only reads saved artifacts and draws the figure. It does not run
extraction, inference, threshold selection, or an experiment evaluator.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "stage3_gamma_theta_sensitivity_20261010_v1"
DISPLAY_ID = SOURCE_ID + "_display_v2"
SOURCE = ROOT / "outputs/reports" / SOURCE_ID
OUTPUT = ROOT / "outputs/reports" / DISPLAY_ID
EVIDENCE = ROOT / "outputs/evidence" / SOURCE_ID


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    suffixes = (".json", ".csv", ".md", ".png", ".svg")
    for suffix in suffixes:
        if OUTPUT.with_suffix(suffix).exists():
            raise FileExistsError(OUTPUT.with_suffix(suffix))

    report = read(SOURCE.with_suffix(".json"))
    source_manifest = read(EVIDENCE / "manifest.json")
    artifacts = source_manifest["signal_artifacts"] + source_manifest["report_artifacts"]
    for artifact in artifacts:
        if sha(ROOT / artifact["path"]) != artifact["sha256"]:
            raise ValueError("Frozen artifact hash mismatch: " + artifact["path"])
    runner = ROOT / "scripts/run_stage3_gamma_theta_sensitivity_v1.py"
    reference_path = ROOT / "data/development/stage3_winter_paper_rerun_20261010_v1/evaluation_reference.json"
    display_config = ROOT / "configs/paper_method_display_names_v1.json"
    source_files = [ROOT / a["path"] for a in artifacts] + [
        EVIDENCE / "manifest.json", runner, reference_path, display_config,
    ]
    before = {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in source_files}

    display = read(display_config)["methods"]
    labels = {"sun": display["sun_rule_only"]["label"],
              "ours": display["direct_llm"]["label"]}
    assert labels == {"sun": "Sun", "ours": "LLM-SE"}
    rows = [dict(row, display_name=labels[row["method"]]) for row in report["rows"]]
    assert len(rows) == 20
    assert all({k: v for k, v in a.items() if k != "display_name"}
               == {k: v for k, v in b.items() if k != "display_name"}
               for a, b in zip(rows, report["rows"], strict=True))

    reference = {c["case_id"]: c for c in read(reference_path)["cases"]}
    signals = {theta: read(EVIDENCE / f"signals_gamma_0.55_theta_{theta:.2f}.json")["signals"]
               for theta in report["grid"]["theta"]}
    low, high = signals[0.25], signals[0.65]
    diagnostics = {}
    for method in ("sun", "ours"):
        changed = [cid for cid in low[method]
                   if low[method][cid]["incorrect_actor"]["status"]
                   != high[method][cid]["incorrect_actor"]["status"]]
        diagnostics[method] = {
            "raw_actor_status_changes": len(changed),
            "scored_actor_status_changes": sum(
                reference[cid]["reference_states"]["incorrect_actor"] in ("violated", "satisfied")
                for cid in changed),
            "changed_cases": [{"case_id": cid,
                               "reference_state": reference[cid]["reference_states"]["incorrect_actor"],
                               "status_at_theta_0.25": low[method][cid]["incorrect_actor"]["status"],
                               "status_at_theta_0.65": high[method][cid]["incorrect_actor"]["status"]}
                              for cid in changed],
        }
    scored_actor_ids = [cid for cid in low["sun"]
                        if reference[cid]["reference_states"]["incorrect_actor"] in ("violated", "satisfied")]
    assert len(scored_actor_ids) == 80
    assert all(signals[theta]["sun"][cid]["incorrect_actor"]["status"]
               == low["sun"][cid]["incorrect_actor"]["status"]
               for theta in signals for cid in scored_actor_ids)
    unknown_count = sum(low["sun"][cid]["incorrect_actor"]["status"] == "unknown"
                        for cid in scored_actor_ids)
    assert unknown_count == 48
    assert diagnostics["sun"]["raw_actor_status_changes"] == 1
    assert diagnostics["sun"]["scored_actor_status_changes"] == 0
    assert diagnostics["ours"]["raw_actor_status_changes"] == 9
    assert diagnostics["ours"]["scored_actor_status_changes"] == 7
    theta_sun_rows = [r for r in rows if r["axis"] == "theta" and r["method"] == "sun"]
    assert len({r["f1"] for r in theta_sun_rows}) == 1
    assert all((r["TP"], r["FP"], r["FN"], r["TN"]) == (37, 60, 32, 31)
               for r in theta_sun_rows)

    # Reuse only the existing drawing routine, with current display names.
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("frozen_threshold_figure", runner)
    drawing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(drawing)
    drawing.LABELS = labels
    drawing.REPORT = OUTPUT
    drawing.plot_rows(rows)

    markdown = SOURCE.with_suffix(".md").read_text(encoding="utf-8")
    markdown = markdown.replace("Sun-style Rules-Only", "Sun")
    markdown = markdown.replace("Stage 3", "Part 3").replace("Stage 2", "Part 2")
    old_flat = "- Sun 的 theta 扫描：Overall F1 0.4458–0.4458；tested values 中最大值出现在 0.25。"
    assert old_flat in markdown
    markdown = markdown.replace(old_flat,
        "- Sun 的 theta 扫描：5 个测试点的 Overall F1 均为 0.4458，全部并列；没有唯一最佳 theta。")
    note = (
        "## 第二张图为何水平\n\n"
        "θ 是执行者相似度阈值，右图固定 γ=0.55。Sun 的 80 个参与评分的角色检查中，"
        "48 个为 unknown；其余 32 个在 θ=0.25–0.65 的五个测试点上判定均未改变。"
        "所有测试点的整体 TP/FP/FN/TN 都是 37/60/32/31，因此 F1 精确相同（0.4457831325）。\n\n"
        "原始角色信号确实有 1 个变化：`case_de1137fcd3ae`（`R5-S4-T3`）的最小执行者"
        "相似度是 0.2538，θ 从 0.25 增至 0.35 时由 satisfied 变为 violated；"
        "但该单元参考状态为 not_applicable，不参与角色评分。因此水平线不表示 θ 未生效。"
        "LLM-SE 则有 9 个原始角色状态变化，其中 7 个参与评分，故右图曲线有变化。\n\n"
        "该结论只适用于这次扫描的数据和阈值范围，不意味着 Sun 对 θ 普遍不敏感。\n\n"
    )
    markdown = markdown.replace("## 解释边界\n", note + "## 解释边界\n")
    display_note = (
        "展示更新：2026-10-14。图例、表格和正文使用 Sun / LLM-SE；Sun 指 Sun et al. (2024) "
        "方法的本地独立重建。数值来自 2026-10-10 冻结扫描，未重新推理或评分；"
        "本副本不包含 2026-10-12 局部修复实验的结果。\n\n"
        f"原始来源：[{SOURCE_ID}.md]({SOURCE_ID}.md)、"
        f"[{SOURCE_ID}.json]({SOURCE_ID}.json)。\n\n"
        f"![双参数敏感性图：Sun 与 LLM-SE]({DISPLAY_ID}.png)\n\n"
    )
    markdown = markdown.replace("# Part 3 双参数敏感性实验\n\n",
                                "# Part 3 双参数敏感性实验\n\n" + display_note, 1)
    assert "Rules-Only" not in markdown and "Sun-style" not in markdown
    with OUTPUT.with_suffix(".md").open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(markdown)
    with OUTPUT.with_suffix(".csv").open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    assert all(sha(ROOT / path) == value for path, value in before.items())
    result = {
        "schema_version": "threshold_sensitivity_display@2.0.0",
        "source_run_id": SOURCE_ID, "display_id": DISPLAY_ID, "display_date": "2026-10-14",
        "scope": "presentation_only", "labels": labels, "rows": rows,
        "source_bindings": before, "source_files_unchanged": True,
        "numerical_rows_unchanged": True, "inference_calls": 0, "llm_api_calls": 0,
        "evaluator_calls": 0, "theta_status_diagnostics": diagnostics,
        "sun_scored_actor_cells": 80, "sun_unknown_actor_cells": unknown_count,
        "sun_scored_actor_statuses_equal_at_all_five_thetas": True,
        "sun_theta_overall_counts": {"TP": 37, "FP": 60, "FN": 32, "TN": 31},
        "implementation_sha256": sha(Path(__file__)),
        "command": "python formal_experiment/scripts/render_stage3_gamma_theta_sensitivity_display_v2.py",
        "artifacts": [{"path": str(OUTPUT.with_suffix(s).relative_to(ROOT)).replace("\\", "/"),
                       "sha256": sha(OUTPUT.with_suffix(s))} for s in (".md", ".csv", ".png", ".svg")],
    }
    with OUTPUT.with_suffix(".json").open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print("Display copies created: Sun / LLM-SE; all 20 numerical rows and frozen source bytes unchanged.")
    print("Sun: 1 raw actor status changed, 0 scored actor statuses changed; F1=0.4457831325 at all five theta values.")


if __name__ == "__main__":
    main()
