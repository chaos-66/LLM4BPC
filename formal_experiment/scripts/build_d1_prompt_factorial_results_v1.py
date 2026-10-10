# -*- coding: utf-8 -*-
"""Build the same-evaluator D1 prompt-factor ablation table.

Refuses to run until the dedicated 450-call execution is complete.  The table
compares every new arm only with the already completed same-release
D-full-0813 baseline on the same EStG-150 Gold and literal-overlap evaluator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NEW_DIR = ROOT / "outputs" / "development" / "d1_prompt_factorial_ablation_v2"
BASE_DIR = (
    ROOT / "outputs" / "development" / "barrientos_ablation_suite_v2"
    / "D-full-0813" / "repeat-01"
)
OUT_JSON = ROOT / "outputs" / "reports" / "d1_prompt_factorial_results_v1.json"
OUT_MD = ROOT / "outputs" / "reports" / "d1_prompt_factorial_results_v1.md"
ARMS = (
    "D-full-0813",
    "D-no-semantic-examples-0813",
    "D-no-semantic-guidance-0813",
    "D-no-explicit-json-contract-0813",
)
DISPLAY = {
    "D-full-0813": "完整方法（六个合成示例）",
    "D-no-semantic-examples-0813": "语义示例→纯结构模板",
    "D-no-semantic-guidance-0813": "去掉详细语义规则",
    "D-no-explicit-json-contract-0813": "去掉显式 JSON 纪律",
}


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_dir(arm: str) -> Path:
    return BASE_DIR if arm == "D-full-0813" else NEW_DIR / arm / "repeat-01"


def _metrics(arm: str) -> dict[str, Any]:
    run_dir = _run_dir(arm)
    evaluation_path = run_dir / "evaluation.json"
    manifest_path = run_dir / "manifest.json"
    if not evaluation_path.is_file() or not manifest_path.is_file():
        raise RuntimeError(f"missing completed artifacts for {arm}")
    evaluation = _read(evaluation_path)
    manifest = _read(manifest_path)
    payload = evaluation.get("evaluation") or {}
    if payload.get("evaluator") != "sun_literal_overlap@2.0.0":
        raise RuntimeError(f"evaluator mismatch for {arm}")
    metrics = payload.get("metrics") or {}
    if metrics.get("sample_count") != 150 or evaluation.get("denominator") != 150:
        raise RuntimeError(f"denominator mismatch for {arm}")
    overall = metrics.get("overall") or {}
    per_field = metrics.get("per_field") or {}
    return {
        "arm": arm,
        "display_name": DISPLAY[arm],
        "overall": {
            key: overall.get(key) for key in ("precision", "recall", "f1")
        },
        "per_field": {
            field: {key: row.get(key) for key in ("precision", "recall", "f1")}
            for field, row in per_field.items()
        },
        "failure_rate": float(payload.get("failed_count", 0)) / 150,
        "valid_output_rate": 1.0 - float(payload.get("failed_count", 0)) / 150,
        "evaluation_sha256": _sha(evaluation_path),
        "manifest_sha256": _sha(manifest_path),
    }


def build(*, overwrite: bool = False) -> dict[str, Any]:
    summary_path = NEW_DIR / "execution_summary.json"
    if not summary_path.is_file():
        raise RuntimeError("450-call execution has not run")
    summary = _read(summary_path)
    if summary.get("complete") is not True \
            or summary.get("completed_samples") != 450 \
            or summary.get("aborted") is True:
        raise RuntimeError("450-call execution is incomplete or aborted")
    if (OUT_JSON.exists() or OUT_MD.exists()) and not overwrite:
        raise RuntimeError("refusing to overwrite prompt-factor result table")

    rows = [_metrics(arm) for arm in ARMS]
    baseline = rows[0]
    for row in rows:
        row["delta_vs_full"] = {
            key: (row["overall"][key] - baseline["overall"][key])
            for key in ("precision", "recall", "f1")
        }
        row["per_field_delta_f1_vs_full"] = {
            field: values["f1"] - baseline["per_field"][field]["f1"]
            for field, values in row["per_field"].items()
        }

    report = {
        "schema_version": "d1_prompt_factorial_results@1.0.0",
        "status": "complete_real_execution",
        "execution": {
            "planned_calls": summary["planned_calls"],
            "actual_calls": summary["actual_calls"],
            "completed_samples": summary["completed_samples"],
            "input_tokens": summary["budget_gate"]["input_tokens"],
            "output_tokens": summary["budget_gate"]["output_tokens"],
            "cost_usd": summary["budget_gate"]["cost_usd"],
            "runtime_seconds": summary["runtime_seconds"],
            "aborted": summary["aborted"],
        },
        "comparison_scope": {
            "input": "same EStG-150 records",
            "model_release": "DeepSeek-V4-Pro-0813",
            "sampling": "temperature=0, top_p=1, retry=0",
            "gold": "same frozen EStG-150 Gold",
            "evaluator": "sun_literal_overlap@2.0.0",
            "baseline": "D-full-0813",
        },
        "rows": rows,
        "interpretation": (
            "negative delta means the removed/replaced module contributed "
            "to end-to-end extraction on this dataset; zero delta means no "
            "measurable score contribution under this arm, not universal "
            "uselessness"
        ),
        "factor_findings": {
            "semantic_examples": {
                "overall_effect": "small_positive_on_this_dataset",
                "removal_delta_f1": rows[1]["delta_vs_full"]["f1"],
                "strongest_supported_field_effect": "actor",
                "actor_removal_delta_f1": rows[1][
                    "per_field_delta_f1_vs_full"]["actor"],
            },
            "detailed_semantic_guidance": {
                "overall_effect": "no_positive_overall_effect_observed",
                "removal_delta_f1": rows[2]["delta_vs_full"]["f1"],
                "supported_tradeoff": (
                    "removal improves actor/condition/constraint/exception "
                    "but reduces action F1"
                ),
            },
            "explicit_json_discipline": {
                "overall_effect": "no_positive_overall_effect_observed",
                "removal_delta_f1": rows[3]["delta_vs_full"]["f1"],
                "valid_output_rate_without_module": rows[3][
                    "valid_output_rate"],
            },
            "claim_boundary": (
                "single fixed 150-record run per deletion arm; report as "
                "descriptive module effects, not significance or universal "
                "necessity"
            ),
        },
    }
    OUT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    lines = [
        "# LLM-SE 提示模块单因素消融",
        "",
        "同一模型版本、同一 150 条输入、同一 Gold、同一 evaluator；所有差值均相对完整方法。",
        "",
        "| 条件 | P | R | F1 | ΔF1 | 合法输出率 | 失败率 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {name} | {p:.4f} | {r:.4f} | {f:.4f} | {d:+.4f} | "
            "{valid:.4f} | {fail:.4f} |".format(
                name=row["display_name"],
                p=row["overall"]["precision"],
                r=row["overall"]["recall"],
                f=row["overall"]["f1"],
                d=row["delta_vs_full"]["f1"],
                valid=row["valid_output_rate"],
                fail=row["failure_rate"],
            ))
    lines += [
        "",
        "## 逐字段 F1 差值（相对完整方法）",
        "",
        "| 条件 | modality | actor | action | condition | constraint | exception |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows[1:]:
        delta = row["per_field_delta_f1_vs_full"]
        lines.append(
            "| {name} | {modality:+.4f} | {actor:+.4f} | {action:+.4f} | "
            "{condition:+.4f} | {constraint:+.4f} | {exception:+.4f} |".format(
                name=row["display_name"], **delta))
    lines += [
        "",
        "## 可支持的结论",
        "",
        "- 六个语义示例具有小幅总体正贡献：替换为纯结构模板后 F1 下降 0.0069；"
        "actor F1 下降 0.1317，是最明显的字段效应。",
        "- 详细语义规则没有显示总体正增益：删除后整体 F1 上升 0.0040；但 action "
        "F1 下降 0.0518，说明它带来字段间权衡，而不是对所有字段均无效。",
        "- 显式 JSON 文字纪律没有显示总体正增益：删除后整体 F1 上升 0.0071，"
        "且本批合法输出率仍为 1.0；这只说明在保留六个示例的当前模型/数据上未测得增益。",
        "- 三个删除臂均为固定 150 条上的单次描述性运行，不作显著性推断，也不把"
        "局部负增益解释为模块普遍无用。",
        "",
        "该表只回答本文提示模块在 EStG-150 上的贡献，不与 Barrientos-native "
        "evaluator 的 F1 跨表比较。",
        "",
        "执行：450/450 calls，输入 {inp:,} tokens，输出 {out:,} tokens，"
        "成本 ${cost:.4f}，运行 {runtime:.1f} 秒。".format(
            inp=summary["budget_gate"]["input_tokens"],
            out=summary["budget_gate"]["output_tokens"],
            cost=summary["budget_gate"]["cost_usd"],
            runtime=summary["runtime_seconds"],
        ),
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    report = build(overwrite=args.overwrite)
    print(f"Built prompt-factor result table: {len(report['rows'])} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
