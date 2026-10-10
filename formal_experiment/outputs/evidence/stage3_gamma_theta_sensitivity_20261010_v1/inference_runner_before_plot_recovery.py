"""Offline, one-factor gamma/theta sensitivity over frozen paper inputs.

The paper-source checker is snapshotted separately from the active implementation.
No Stage 2 extraction, LLM/API request, model download, or primary-result update.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "stage3_gamma_theta_sensitivity_20261010_v1"
OUT = ROOT / "outputs/evidence" / RUN_ID
REPORT = ROOT / "outputs/reports" / RUN_ID
INPUT = ROOT / "data/development/stage3_winter_paper_rerun_20261010_v1"
SOURCE = ROOT.parent.parent / "LLM4BPC-s3-ext-pc-v1/formal_experiment"
GAMMAS = (0.35, 0.45, 0.55, 0.65, 0.75)
THETAS = (0.25, 0.35, 0.45, 0.55, 0.65)
BASELINE = (0.55, 0.45)
METHODS = ("sun", "ours")
LABELS = {"sun": "Sun-style Rules-Only", "ours": "LLM-SE"}
TYPES = ("missing_action", "incorrect_actor", "out_of_order")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_new(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def points():
    """Baseline first; nine unique settings, ten plotted axis positions."""
    return [BASELINE] + [(g, BASELINE[1]) for g in GAMMAS if g != BASELINE[0]] + [
        (BASELINE[0], t) for t in THETAS if t != BASELINE[1]
    ]


def signal_key(method: str, case_id: str, check_type: str):
    return method, case_id, check_type


def evaluate_saved(doc, reference, evaluator):
    results = {}
    for method in METHODS:
        signals = {
            signal_key(method, cid, typ): item[typ]
            for cid, item in doc["signals"][method].items() for typ in TYPES
        }
        results[method] = evaluator.evaluate_dev_method(
            method, reference["cases"], signals, reference["order_scope"]
        )
    return results


def check_baseline(actual, expected, generated, frozen):
    """Check all metrics and all 690 baseline signal decisions, not just F1."""
    for method in METHODS:
        for block in ["overall", *TYPES]:
            a = actual[method]["overall"] if block == "overall" else actual[method]["per_type"][block]
            e = expected[method]["overall"] if block == "overall" else expected[method]["per_type"][block]
            for key in ("TP", "FP", "FN", "TN", "scored_cells", "positive_support", "negative_support",
                        "unknown_positive", "unknown_negative", "precision", "recall", "f1"):
                if a[key] != e[key]:
                    raise RuntimeError(f"baseline metric mismatch {method}/{block}/{key}: {a[key]} != {e[key]}")
        for cid, frozen_types in frozen["signals"][method].items():
            for typ in TYPES:
                new = generated["signals"][method][cid][typ]
                old = frozen_types[typ]
                if new != old:
                    raise RuntimeError(f"baseline signal mismatch {method}/{cid}/{typ}")


def infer(checker, converted, models, targets, gamma, theta):
    """Receives known applicability only; reference states never reach checker."""
    checker.set_thresholds(gamma=gamma, theta=theta)
    signals = {m: {} for m in METHODS}
    for row in targets:
        cid, rid = row["case_id"], row["requirement_id"]
        for method in METHODS:
            checked = checker.check_rule_record(converted[method][rid], models[cid])
            signals[method][cid] = {typ: checked[typ] for typ in TYPES}
    return {"gamma": gamma, "theta": theta, "signals": signals}


def make_rows(results):
    rows = []
    for axis, values in (("gamma", GAMMAS), ("theta", THETAS)):
        for value in values:
            setting = (value, BASELINE[1]) if axis == "gamma" else (BASELINE[0], value)
            for method in METHODS:
                result = results[setting][method]
                overall = result["overall"]
                row = {"axis": axis, "value": value, "gamma": setting[0], "theta": setting[1],
                       "method": method, "display_name": LABELS[method],
                       **{k: overall[k] for k in ("precision", "recall", "f1", "TP", "FP", "FN", "TN",
                                                 "scored_cells", "coverage", "unknown_rate",
                                                 "unknown_positive", "unknown_negative")},
                       "macro_f1": result["macro_f1"]}
                for typ in TYPES:
                    row[typ + "_f1"] = result["per_type"][typ]["f1"]
                rows.append(row)
    return rows


def make_markdown(report):
    lines = ["# Stage 3 双参数敏感性实验", "",
             "任务：S3-GAMMA-THETA-SENSITIVITY-V1；开发分析；2026-10-10。", "",
             "复用原 Stage 2 预测和 BPMN，固定 MPNet、检查器、参考及原表评价范围。"
             "γ 扫描时 θ=0.45；θ 扫描时 γ=0.55。9 个不同配置、18 个方法评价，"
             "基准在两条曲线中共用；新增 LLM/API/网络调用均为 0。", "",
             "基准 690 个逐案例信号与原信号完整对象一致，整体/分类型计数与指标完全一致。", "",
             "## 总体结果", "",
             "| 扫描 | 值 | Sun P | Sun R | Sun F1 | LLM-SE P | LLM-SE R | LLM-SE F1 |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    rows = report["rows"]
    for axis, values in (("gamma", GAMMAS), ("theta", THETAS)):
        for value in values:
            pair = {r["method"]: r for r in rows if r["axis"] == axis and r["value"] == value}
            cells = [axis, f"{value:.2f}"]
            for method in METHODS:
                cells += [f"{pair[method][k]:.4f}" for k in ("precision", "recall", "f1")]
            lines.append("| " + " | ".join(cells) + " |")
    lines += ["", "## 分类型 F1 与覆盖率", "",
              "| 扫描 | 值 | 方法 | 缺失动作 F1 | 错误角色 F1 | 顺序 F1 | Macro F1 | 覆盖率 |",
              "|---|---:|---|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append("| " + " | ".join([row["axis"], f"{row['value']:.2f}", row["display_name"],
                     *[f"{row[t + '_f1']:.4f}" for t in TYPES], f"{row['macro_f1']:.4f}",
                     f"{row['coverage']:.4f}"]) + " |")
    lines += ["", "## 参数效应", ""]
    for axis in ("gamma", "theta"):
        for method in METHODS:
            subset = [r for r in rows if r["axis"] == axis and r["method"] == method]
            best = max(subset, key=lambda r: r["f1"])
            worst = min(subset, key=lambda r: r["f1"])
            lines.append(f"- {LABELS[method]} 的 {axis} 扫描：Overall F1 {worst['f1']:.4f}–"
                         f"{best['f1']:.4f}；tested values 中最大值出现在 {best['value']:.2f}。")
    lines += ["", "## 解释边界", "",
              "- 固定原表 201 个评价单元，69 正、132 负；unknown 正例计 FN，负例单独记录。",
              "- 已使用的构造开发集，已有模型/阈值选择暴露；不是独立未见测试。",
              "- 原顺序评价范围存在已知的端点依赖纳入问题；本实验为参数隔离而保持该范围，"
              "不据此解决范围问题或更新主表。",
              "- 原检查器含共用角色文本规范化，使用原代码独立快照；当前生产实现和旧结果未改。",
              "- 两条单参数扫描未检验 γ×θ 交互；不宣称全局最优、不自动选择新默认值。",
              "- 新版清理提示词没有参与本次实验，不能把本结果移植为新版提示词性能。", ""]
    return "\n".join(lines)


def plot_rows(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.65), sharey=True)
    for ax, axis, fixed in zip(axes, ("gamma", "theta"), ("theta = 0.45", "gamma = 0.55")):
        for method, color, marker in (("sun", "#777777", "s"), ("ours", "#1261a0", "o")):
            subset = [r for r in rows if r["axis"] == axis and r["method"] == method]
            ax.plot([r["value"] for r in subset], [r["f1"] for r in subset],
                    color=color, marker=marker, linewidth=1.6, markersize=4, label=LABELS[method])
        ax.set_xlabel(r"$\gamma$" if axis == "gamma" else r"$\theta$")
        ax.set_title(fixed, fontsize=10)
        ax.set_xticks(GAMMAS if axis == "gamma" else THETAS)
        ax.grid(alpha=0.22)
        ax.set_ylim(max(0.0, min(r["f1"] for r in rows) - 0.04),
                    min(1.0, max(r["f1"] for r in rows) + 0.04))
        ax.axvline(BASELINE[0] if axis == "gamma" else BASELINE[1], color="#cccccc", linestyle=":")
    axes[0].set_ylabel("Overall pooled F1")
    axes[1].legend(fontsize=8, loc="best")
    fig.tight_layout()
    for suffix in (".png", ".svg"):
        path = REPORT.with_suffix(suffix)
        if path.exists():
            raise FileExistsError(path)
        fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main():
    started = time.perf_counter()
    if REPORT.with_suffix(".json").exists() or (OUT / "manifest.json").exists():
        raise FileExistsError("Completed run already exists; use a new version instead of overwriting")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT / "scripts"))
    import bpc_hybrid
    bpc_hybrid.__path__.insert(0, str(OUT / "source_snapshot/bpc_hybrid"))
    import torch
    torch.set_num_threads(2)
    import spacy
    from bpc_hybrid.stage3_v2.semantic_matcher_v2 import (ST_MPNET, SharedSemanticMatcherV2,
                                                       SentenceTransformerBackend)
    from bpc_hybrid.stage3_v2.rule_order_adapter_v3 import SharedRuleOrderAdapterV3
    from bpc_hybrid.stage3_v2.rule_record_converter_v2 import canonical_to_rule_record_v2
    from bpc_hybrid.stage3_v2.checker_v2 import SharedStage3CheckerV2
    from bpc_hybrid.stage1_process import load_stage1_contract, parse_bpmn_file
    from bpc_hybrid.sun_stage3.sun_model import SunProcessModel
    import stage3_winter_paper_metrics_v1 as evaluator

    preparation = read(OUT / "preparation.json")
    for item in preparation["source_code_bindings"].values():
        if "snapshot" in item and sha(ROOT / item["snapshot"]) != item["sha256"]:
            raise RuntimeError("source snapshot changed")
    validation = read(ROOT / "outputs/reports/stage3_comparison_check_20261010_v1.json")
    paths = {"reference": INPUT / "evaluation_reference.json", "sources": INPUT / "regulation_sources.json",
             "inference": INPUT / "inference_view.json", "convergence": INPUT / "convergence_report.json",
             "sun": SOURCE / "data/predictions/stage3_table3_r5_sun_rule_only_v1/predictions.json",
             "ours": SOURCE / "data/predictions/stage3_table3_r5_ours_stage2_formal_v1/predictions.json",
             "frozen_signals": ROOT / "outputs/evidence/stage3_comparison_check_20261010_v1/sun_ours_selected_dev_signals_v1.json"}
    for key, binding in (("reference", "evaluation_reference"), ("convergence", "convergence_report"),
                         ("sun", "sun_predictions"), ("ours", "ours_predictions"),
                         ("frozen_signals", "preserved_sun_ours_signals")):
        if sha(paths[key]) != validation["bindings"][binding]["sha256"]:
            raise RuntimeError(f"bound input changed: {key}")
    bindings = {k: {"path": str(p), "sha256": sha(p)} for k, p in paths.items()}
    reference = read(paths["reference"])
    targets = [{"case_id": c["case_id"], "requirement_id": c["requirement_id"]} for c in reference["cases"]]
    applicability = {"targets": targets, "reference_states_included": False}
    applicability_path = OUT / "known_applicability.json"
    if applicability_path.exists():
        if read(applicability_path) != applicability:
            raise RuntimeError("prepared applicability changed")
    else:
        write_new(applicability_path, applicability)
    source_texts = {r["rule_id"]: r["text"] for r in read(paths["sources"])["rules"]}
    predictions = {m: {r["requirement_id"]: r["record"] for r in read(paths[m])["records"]} for m in METHODS}
    for rule in read(paths["sources"])["rules"]:
        if hashlib.sha256(rule["text"].encode("utf-8")).hexdigest() != rule["text_sha256"]:
            raise RuntimeError("source text hash mismatch")
    for case in reference["cases"]:
        if case["split"] != "development":
            raise RuntimeError("non-development reference case")
    nlp = spacy.load("en_core_web_sm")
    model_dir = ROOT.parent / ".tmp/hf_cache/hub/models--sentence-transformers--all-mpnet-base-v2/snapshots/e8c3b32edf5434bc2275fc9bab85f82640a19130"
    matcher = SharedSemanticMatcherV2(SentenceTransformerBackend(ST_MPNET, model_dir))
    adapter = SharedRuleOrderAdapterV3(matcher)
    print("Local MPNet loaded; converting frozen records and BPMN.", flush=True)
    converted = {m: {rid: canonical_to_rule_record_v2(rec, source_texts[rid], rid, nlp, order_adapter=adapter)
                     for rid, rec in predictions[m].items()} for m in METHODS}
    write_new(OUT / "converted_records.json", converted)
    contract = load_stage1_contract(ROOT / "configs/stage1_structural_s11_s14.json")
    models = {}
    for row in read(paths["inference"])["items"]:
        path = ROOT / row["bpmn_path"]
        bindings["bpmn:" + row["case_id"]] = {"path": str(path), "sha256": sha(path)}
        models[row["case_id"]] = SunProcessModel(row["process_id"], parse_bpmn_file(path, contract=contract), nlp)
    checker = SharedStage3CheckerV2(matcher, nlp, tau=0.8, gamma=BASELINE[0], theta=BASELINE[1])
    results, artifacts = {}, []
    expected = read(paths["convergence"])["legacy_development_report"]["dev_result"]
    frozen = read(paths["frozen_signals"])
    for index, (gamma, theta) in enumerate(points()):
        doc = infer(checker, converted, models, targets, gamma, theta)
        path = OUT / f"signals_gamma_{gamma:.2f}_theta_{theta:.2f}.json"
        write_new(path, doc)
        result = evaluate_saved(read(path), reference, evaluator)
        if index == 0:
            check_baseline(result, expected, doc, frozen)
            print("Baseline fully reproduced: 690 signals; Sun F1=0.4457831325, LLM-SE F1=0.5340909091.", flush=True)
        results[(gamma, theta)] = result
        artifacts.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(path)})
        print(f"gamma={gamma:.2f}, theta={theta:.2f}: Sun={result['sun']['micro_f1']:.6f}, LLM-SE={result['ours']['micro_f1']:.6f}", flush=True)
    rows = make_rows(results)
    report = {"schema_version": "stage3_gamma_theta_sensitivity@1.0.0", "run_id": RUN_ID,
              "task_id": "S3-GAMMA-THETA-SENSITIVITY-V1", "scope": "development_only",
              "baseline": {"gamma": BASELINE[0], "theta": BASELINE[1]},
              "grid": {"gamma": list(GAMMAS), "theta": list(THETAS)}, "design": "one_factor_at_a_time",
              "unique_settings": 9, "method_evaluations": 18, "display_rows": 20,
              "case_count": len(targets), "scored_cells_per_method": 201,
              "baseline_complete_signal_equality": True, "baseline_metric_equality": True,
              "llm_api_calls": 0, "network_calls": 0, "rows": rows,
              "results": [{"gamma": g, "theta": t, "methods": results[(g, t)]} for g, t in points()],
              "order_scope_changed": False, "primary_results_changed": False,
              "held_out_generalization_claim_allowed": False, "interaction_tested": False}
    write_new(REPORT.with_suffix(".json"), report)
    with REPORT.with_suffix(".csv").open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    with REPORT.with_suffix(".md").open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(make_markdown(report))
    plot_rows(rows)
    cache_rows = [{"key": list(key), "similarity": value} for key, value in matcher._cache.items()]
    write_new(OUT / "similarity_cache.json", {"backend": matcher.identity(), "pairs": cache_rows})
    for item in bindings.values():
        if sha(Path(item["path"])) != item["sha256"]:
            raise RuntimeError("input mutated during run: " + item["path"])
    manifest = {"schema_version": "stage3_gamma_theta_sensitivity_manifest@1.0.0", "run_id": RUN_ID,
                "task_id": report["task_id"], "status": "succeeded", "scope": "development_only",
                "command": ".tmp/mpnet_venv/Scripts/python.exe formal_experiment/scripts/run_stage3_gamma_theta_sensitivity_v1.py",
                "python_executable": sys.executable,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "source_preparation_sha256": sha(OUT / "preparation.json"), "input_bindings": bindings,
                "implementation_sha256": sha(Path(__file__)), "evaluator_sha256": sha(Path(evaluator.__file__)),
                "backend": matcher.identity(), "matcher_stats": matcher.stats(),
                "torch_version": torch.__version__, "spacy_version": spacy.__version__,
                "elapsed_seconds": time.perf_counter() - started, "signal_artifacts": artifacts,
                "baseline_signal_equality": True, "baseline_metric_equality": True,
                "unique_settings": 9, "method_evaluations": 18, "llm_api_calls": 0, "network_calls": 0,
                "gold_modified": False, "old_results_modified": False,
                "reference_role": "Read-only development reference; known target applicability passed without reference states",
                "limitations": ["Exposed constructed development benchmark", "Original order eligibility issue retained",
                                "One-factor scan; no interaction claim; primary defaults unchanged"]}
    manifest["report_artifacts"] = [{"path": str(REPORT.with_suffix(s).relative_to(ROOT)).replace("\\", "/"),
                                     "sha256": sha(REPORT.with_suffix(s))} for s in (".json", ".csv", ".md", ".png", ".svg")]
    write_new(OUT / "manifest.json", manifest)
    print(f"Completed 18 evaluations in {manifest['elapsed_seconds']:.1f}s; LLM/API=0.", flush=True)


if __name__ == "__main__":
    main()
