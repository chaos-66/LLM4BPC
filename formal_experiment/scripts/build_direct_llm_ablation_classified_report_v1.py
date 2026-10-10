# -*- coding: utf-8 -*-
"""Classify the completed Barrientos D/E results by experiment purpose.

This is a zero-API, read-only derivation.  It does not rescore predictions and
does not read Gold.  It separates one-factor internal ablation, multi-module
sensitivity, module replacement, and external/shared-target comparison so the
existing 1140-call run is not presented as one undifferentiated ablation table.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_TABLES = ROOT / "outputs/reports/barrientos_de_tables_v1.json"
EVENTS = ROOT / "docs/EXPERIMENT_EVENTS.jsonl"
REPORT_JSON = (
    ROOT / "outputs/reports/"
    "direct_llm_ablation_existing_results_classified_v1.json"
)
REPORT_MD = (
    ROOT / "outputs/reports/"
    "direct_llm_ablation_existing_results_classified_v1.md"
)
RUN_ID = "barrientos-de-0813-1140-v1"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _event_sha256(event: dict[str, Any]) -> str:
    """Stable hash of the selected run event, not the append-only log file.

    Hashing the whole ``EXPERIMENT_EVENTS.jsonl`` made this report stale after
    every unrelated later event.  The scientific provenance is the selected
    immutable run event, so bind that exact object instead.
    """
    payload = json.dumps(
        event, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _run_event(path: Path) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        experiment = event.get("experiment") or {}
        if experiment.get("run_id") == RUN_ID:
            matches.append(event)
    if len(matches) != 1:
        raise RuntimeError(
            f"expected one {RUN_ID} event, found {len(matches)}")
    event = matches[0]
    if (event.get("experiment") or {}).get("status") != "succeeded":
        raise RuntimeError(f"{RUN_ID} is not a succeeded experiment event")
    return event


def _accounting(event: dict[str, Any]) -> dict[str, Any]:
    text = (event.get("experiment") or {}).get("result_summary", "")
    calls = re.search(r"(\d+)/(\d+) actual calls", text)
    tokens = re.search(r"input=(\d+), output=(\d+) tokens", text)
    peak = re.search(r"peak ledger USD ([0-9.]+)", text)
    offpeak = re.search(r"off-peak estimate USD ([0-9.]+)", text)
    if not all((calls, tokens, peak, offpeak)):
        raise RuntimeError("run event lacks structured accounting evidence")
    return {
        "actual_calls": int(calls.group(1)),
        "planned_calls": int(calls.group(2)),
        "input_tokens": int(tokens.group(1)),
        "output_tokens": int(tokens.group(2)),
        "conservative_peak_ledger_usd": float(peak.group(1)),
        "off_peak_estimate_usd": float(offpeak.group(1)),
        "complete": True,
        "in_doubt": 0,
        "call_allocation": {
            "internal_one_factor_reference_and_removal": 300,
            "multi_module_sensitivity": 150,
            "prompt_contract_replacement_estg150": 150,
            "barrientos_native_external_comparator": 180,
            "ours_full_same_data_reference": 180,
            "barrientos_module_swap_same_data": 180,
        },
    }


def _d_metrics(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "overall": {
            "precision": row["overall_p"],
            "recall": row["overall_r"],
            "f1": row["overall_f1"],
        },
        "field_f1": {
            field: row[f"{field}_f1"]
            for field in (
                "actor", "action", "condition", "constraint", "exception")
        },
        "parse_success_rate": row["parse_success_rate"],
        "nonempty_canonical_clause_rate": (
            row["nonempty_canonical_clause_rate"]),
        "failure_rate": row["failure_rate"],
    }


def build_report(
    source_tables: Path = SOURCE_TABLES,
    events: Path = EVENTS,
) -> dict[str, Any]:
    source = _load_json(source_tables)
    if source.get("schema_version") != "barrientos_de_tables@1.2.0":
        raise RuntimeError("unexpected Barrientos D/E table schema")
    tables = source["tables"]
    d = tables["D_prompt_ablation_0813"]
    a = tables["A_barrientos_native"]
    b = tables["B_ours_native"]
    c = tables["C_shared_target"]
    event = _run_event(events)
    accounting = _accounting(event)
    if accounting["actual_calls"] != 1140:
        raise RuntimeError("the classified report requires the fixed 1140 run")
    if sum(accounting["call_allocation"].values()) != 1140:
        raise RuntimeError("classified call allocation does not sum to 1140")

    full = d["rows"]["D-full-0813"]
    no_fewshot = d["rows"]["D-no-fewshot-0813"]
    minimal = d["rows"]["D-minimal-0813"]
    barr_style = d["rows"]["D-barrientos-style-0813"]
    ours_full = b["arms"]["OURS-FULL"]["aggregate"]
    swap = b["arms"]["OURS-BARRIENTOS-MODULE"]["aggregate"]

    return {
        "schema_version": (
            "direct_llm_ablation_existing_results_classified@1.0.0"),
        "status": "classified_existing_results_only_no_new_execution",
        "scope": {
            "run_id": RUN_ID,
            "model": "DeepSeek-V4-Pro-0813",
            "new_api_calls_for_this_report": 0,
            "gold_read_for_this_report": False,
            "rescore_performed": False,
            "stage3_bpmn_evaluation_performed": False,
            "purpose": (
                "separate already-run evidence by scientific comparison "
                "type before any additional ablation is designed"),
        },
        "provenance": {
            "source_tables": str(source_tables.relative_to(ROOT)).replace(
                "\\", "/"),
            "source_tables_sha256": _sha256(source_tables),
            "experiment_events": str(events.relative_to(ROOT)).replace(
                "\\", "/"),
            "source_event_sha256": _event_sha256(event),
            "source_event_timestamp_utc": event["timestamp_utc"],
            "source_event_git_commit": event["git_commit"],
        },
        "run_accounting": accounting,
        "classification_rule": {
            "core_internal_ablation": (
                "same model, data, Gold, evaluator and pipeline; change "
                "exactly one named component"),
            "multi_module_sensitivity": (
                "several components are weakened or removed together; useful "
                "for stress testing but not for single-module attribution"),
            "module_replacement": (
                "replace an interface or prompt module with the Barrientos "
                "design while holding the surrounding evaluation fixed"),
            "external_comparison": (
                "evaluate each method in its native schema or on a predeclared "
                "shared target; never compare native F1 across evaluators"),
        },
        "categories": {
            "1_core_internal_one_factor_ablation": {
                "status": "partially_complete",
                "dataset": "EStG-150",
                "evaluator": d["evaluator"],
                "repeats": 1,
                "calls": 300,
                "baseline": {
                    "arm": "D-full-0813",
                    "display_name": full["display_name"],
                    "metrics": _d_metrics(full),
                },
                "single_removed_component": {
                    "component": "few-shot examples",
                    "arm": "D-no-fewshot-0813",
                    "display_name": no_fewshot["display_name"],
                    "metrics": _d_metrics(no_fewshot),
                    "delta_vs_full": {
                        key: d["delta_vs_full_0813"][
                            "D-no-fewshot-0813"][key]
                        for key in (
                            "overall_p", "overall_r", "overall_f1",
                            "parse_success_rate",
                            "nonempty_canonical_clause_rate", "failure_rate")
                    },
                },
                "supported_conclusion": (
                    "Under the fixed 0813 pipeline, removing only the few-shot "
                    "examples collapses usable canonical six-field output: "
                    "overall F1 falls from 0.771908 to 0 and the nonempty "
                    "canonical-clause rate from 0.986667 to 0."),
                "interpretation_limit": (
                    "The 0 F1 is a strict end-to-end output-contract result. "
                    "Parse success remains 0.98 and the later interface "
                    "diagnosis found nonempty raw clauses, so this arm mixes "
                    "semantic-example removal with loss of demonstrated JSON/"
                    "coordinate conventions. It must not be described as proof "
                    "that the model produced no semantic content or as an "
                    "isolated semantic contribution of few-shot examples."),
            },
            "2_multi_module_sensitivity_not_core_ablation": {
                "status": "complete_for_existing_arm",
                "dataset": "EStG-150",
                "evaluator": d["evaluator"],
                "repeats": 1,
                "calls": 150,
                "arm": "D-minimal-0813",
                "display_name": minimal["display_name"],
                "metrics": _d_metrics(minimal),
                "supported_conclusion": (
                    "The extreme minimal prompt fails completely under the "
                    "strict pipeline (parse success 0, failure rate 1)."),
                "interpretation_limit": (
                    "This arm changes several prompt components together, so "
                    "it cannot identify which individual module caused the "
                    "failure and is not a core one-factor ablation."),
            },
            "3_module_replacement": {
                "status": "complete_for_two_existing_replacement_tests",
                "estg150_prompt_contract_replacement": {
                    "dataset": "EStG-150",
                    "evaluator": d["evaluator"],
                    "repeats": 1,
                    "calls": 150,
                    "reference_arm": "D-full-0813",
                    "replacement_arm": "D-barrientos-style-0813",
                    "metrics": _d_metrics(barr_style),
                    "delta_overall_f1": d["delta_vs_full_0813"][
                        "D-barrientos-style-0813"]["overall_f1"],
                    "supported_conclusion": (
                        "The Barrientos-style replacement does not produce a "
                        "usable record for the current six-field pipeline: "
                        "parse success is 0.993333 but nonempty canonical rate "
                        "and strict F1 are 0."),
                },
                "same_data_barrientos_module_swap": {
                    "dataset": "S2.11 complex corpus (36 requirements)",
                    "evaluator": b["evaluator"],
                    "repeats": 5,
                    "calls": 360,
                    "full": {
                        "arm": "OURS-FULL",
                        "overall_f1": ours_full["overall_f1"],
                        "field_f1": {
                            field: ours_full[f"{field}_f1"]
                            for field in (
                                "actor", "action", "condition", "constraint",
                                "exception")
                        },
                        "parse_success_rate": ours_full[
                            "parse_success_rate"],
                        "nonempty_canonical_clause_rate": ours_full[
                            "nonempty_canonical_clause_rate"],
                    },
                    "replacement": {
                        "arm": "OURS-BARRIENTOS-MODULE",
                        "overall_f1": swap["overall_f1"],
                        "parse_success_rate": swap["parse_success_rate"],
                        "nonempty_canonical_clause_rate": swap[
                            "nonempty_canonical_clause_rate"],
                    },
                    "delta_swap_minus_full": b["delta_swap_minus_full"],
                    "supported_conclusion": (
                        "On the same 36-item six-field Gold and evaluator, "
                        "OURS-FULL reaches mean overall F1 0.874 (SD 0.003), "
                        "whereas the module-swapped output has strict F1 0 and "
                        "nonempty canonical rate 0."),
                    "interpretation_limit": (
                        "This establishes interface/task-fit failure for the "
                        "replacement. It does not establish that the complete "
                        "Barrientos method is generally ineffective."),
                },
            },
            "4_external_native_and_shared_target_comparison": {
                "status": "complete_for_existing_comparators",
                "barrientos_native": {
                    "dataset": "Barrientos 36 requirements",
                    "evaluator": a["evaluator"],
                    "repeats": 5,
                    "calls": 180,
                    "precondition_f1": a["aggregate"]["precondition_f1"],
                    "norm_f1": a["aggregate"]["norm_f1"],
                    "strict_json_validity": a["aggregate"][
                        "strict_json_validity"],
                    "output_coverage": a["aggregate"]["output_coverage"],
                    "failure_rate": a["aggregate"]["failure_rate"],
                    "self_consistency": a["self_consistency"],
                },
                "shared_three_class_modality": {
                    "dataset": "S2.11 complex corpus (36 requirements)",
                    "evaluator": (
                        "same shared-target Gold and metric via deterministic "
                        "adapters"),
                    "arms": {
                        arm: c["modality"]["arms"][arm]
                        for arm in (
                            "BARR-FULL", "OURS-FULL",
                            "OURS-BARRIENTOS-MODULE")
                    },
                    "supported_conclusion": (
                        "On the expressible shared three-class modality target, "
                        "BARR-FULL has macro-F1 0.890 (SD 0.031), above "
                        "OURS-FULL at 0.822 (SD 0). Barrientos is stronger on "
                        "this narrower shared target."),
                    "not_expressible_or_alignable": c["not_expressible"],
                },
                "comparability_limit": (
                    "Barrientos-native precondition/norm F1 and Ours-native "
                    "six-field F1 use different schemas and evaluators and "
                    "must never be directly ranked."),
            },
        },
        "not_yet_run_core_internal_ablations": [
            {
                "component_id": "field_definitions_and_six_element_schema",
                "display_name": "六要素字段定义与输出模式",
                "status": "not_run_as_one_factor_arm",
            },
            {
                "component_id": "span_evidence_anchoring",
                "display_name": "原文证据与位置锚定规则",
                "status": "not_run_as_one_factor_arm",
            },
            {
                "component_id": "strict_json_schema_discipline",
                "display_name": "严格 JSON 结构约束",
                "status": "not_run_as_one_factor_arm",
            },
            {
                "component_id": "canonicalizer",
                "display_name": "坐标重锚与规范化器",
                "status": "not_run_on_current_0813_full_raw_as_one_factor_arm",
                "suggested_mode": "offline replay; no new API call required",
            },
            {
                "component_id": "validator",
                "display_name": "结构与字段校验器",
                "status": "not_run_on_current_0813_full_raw_as_one_factor_arm",
                "suggested_mode": "offline replay; no new API call required",
            },
            {
                "component_id": "output_adapter",
                "display_name": "模型输出到六字段记录的适配器",
                "status": "not_run_on_current_0813_full_raw_as_one_factor_arm",
                "suggested_mode": "offline replay; no new API call required",
            },
        ],
        "bottom_line": {
            "what_is_already_clear": [
                "Few-shot examples are necessary for adherence to the current "
                "strict LLM-SE output interface; their independent semantic "
                "contribution is not isolated by this arm.",
                "The full six-field method is substantially better fitted to "
                "the project's six-field, BPMN-facing interface than either "
                "tested "
                "Barrientos-style replacement.",
                "Barrientos is stronger on the narrower shared three-class "
                "modality target and works well in its own native schema.",
            ],
            "what_is_not_yet_clear": (
                "The independent contribution of the remaining LLM-SE "
                "modules cannot be attributed until the listed one-factor "
                "removals are run."),
            "global_winner_claim_allowed": False,
            "stage3_performance_claim_allowed_from_this_run": False,
        },
    }


def _mean_sd(value: dict[str, Any]) -> str:
    return f"{value['mean']:.3f} ± {value['sd']:.3f}"


def to_markdown(report: dict[str, Any]) -> str:
    cats = report["categories"]
    core = cats["1_core_internal_one_factor_ablation"]
    stress = cats["2_multi_module_sensitivity_not_core_ablation"]
    repl = cats["3_module_replacement"]
    ext = cats["4_external_native_and_shared_target_comparison"]
    bswap = repl["same_data_barrientos_module_swap"]
    shared = ext["shared_three_class_modality"]["arms"]
    acc = report["run_accounting"]

    lines = [
        "# LLM-SE / Barrientos 已有实验结果分类整理 v1",
        "",
        "> 本报告只重组已经完成的 1140 次调用结果；本次新增 API 调用为 0，"
        "未读取 Gold，也未重新评分。",
        "",
        "## 一、先把四种实验分开",
        "",
        "| 类别 | 回答的问题 | 已有实验 | 当前状态 |",
        "|---|---|---|---|",
        "| 内部一因素消融 | 只拿掉本文一个模块，会怎样？ | 完整方法 vs 去掉 few-shot | 部分完成 |",
        "| 多模块压力测试 | 同时大幅简化后，系统还能不能工作？ | 极简 prompt | 已有结果，但不能归因单模块 |",
        "| 模块替换 | 把本文模块换成 Barrientos 风格，会怎样？ | 两个 replacement arms | 已完成现有替换实验 |",
        "| 外部/共享对照 | 两套方法各自擅长什么？ | Barrientos-native + 共享三类 modality | 已完成现有对照 |",
        "",
        "## 二、真正属于本文内部消融的现有结果",
        "",
        "同一模型、EStG-150、同一 Gold、同一 evaluator，只去掉 few-shot。",
        "",
        "| 条件 | Overall P | Overall R | Overall F1 | JSON/relay 可解析 | 非空 canonical | 失败率 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in (core["baseline"], core["single_removed_component"]):
        m = row["metrics"]
        lines.append(
            f"| {row['display_name']} | {m['overall']['precision']:.3f} | "
            f"{m['overall']['recall']:.3f} | {m['overall']['f1']:.3f} | "
            f"{m['parse_success_rate']:.3f} | "
            f"{m['nonempty_canonical_clause_rate']:.3f} | "
            f"{m['failure_rate']:.3f} |")
    lines += [
        "",
        "结论：去掉 few-shot 后，Overall F1 从 0.772 降到 0，非空 canonical "
        "记录率从 0.987 降到 0。它证明 few-shot 对当前严格输出接口的遵循非常"
        "重要，但尚未单独证明其语义贡献。",
        "",
        "边界：可解析率仍有 0.980，后续接口诊断还发现146条原始响应包含非空"
        "clauses；因此 0 F1 表示输出无法进入本文严格六字段表示，不能简单写成"
        "“模型完全不懂语义”。",
        "",
        "字段层面的完整方法 F1：actor 0.687、action 0.860、condition 0.784、"
        "constraint 0.597、exception 0.636。",
        "",
        "## 三、已有但不能当作单模块消融的结果",
        "",
        "### 3.1 多模块压力测试",
        "",
        f"极简 prompt：F1 {stress['metrics']['overall']['f1']:.3f}，"
        f"可解析率 {stress['metrics']['parse_success_rate']:.3f}，"
        f"失败率 {stress['metrics']['failure_rate']:.3f}。它证明过度简化会使"
        "系统完全失败，但因为同时改变多个组成部分，不能说明究竟是哪一个模块造成。",
        "",
        "### 3.2 Barrientos 模块替换",
        "",
        "| 数据与替换 | 本文完整方法 | 替换后 | 结果解释 |",
        "|---|---:|---:|---|",
        "| EStG-150：换成 Barrientos 风格提示约束 | F1 0.772 | F1 0；"
        "可解析 0.993；非空 canonical 0 | 输出接口与本文六字段链不匹配 |",
        f"| 36 条复杂语料×5：换成 Barrientos 模块 | F1 "
        f"{_mean_sd(bswap['full']['overall_f1'])} | F1 "
        f"{_mean_sd(bswap['replacement']['overall_f1'])}；非空 canonical 0 | "
        "同一 Gold/evaluator 下，本文模块更适配本文任务 |",
        "",
        "这两个 0 分不能写成“Barrientos 方法本身无效”，只能写成“把它直接"
        "替换进本文六字段接口后不兼容”。",
        "",
        "## 四、Barrientos 与本文各自擅长什么",
        "",
        "Barrientos 在自己的原生任务上：precondition F1 "
        f"{_mean_sd(ext['barrientos_native']['precondition_f1'])}，norm F1 "
        f"{_mean_sd(ext['barrientos_native']['norm_f1'])}，严格 JSON 合法率 1.000，"
        "输出覆盖率 1.000，五次一致性 0.881。",
        "",
        "在唯一合法的跨方法共同目标——三类 modality——上：",
        "",
        "| 方法 | obligation F1 | permission F1 | prohibition F1 | Macro-F1 |",
        "|---|---:|---:|---:|---:|",
    ]
    for arm, label in (
        ("BARR-FULL", "Barrientos 原生方法"),
        ("OURS-FULL", "本文完整方法"),
        ("OURS-BARRIENTOS-MODULE", "本文框架 + Barrientos 模块替换"),
    ):
        value = shared[arm]
        lines.append(
            f"| {label} | "
            f"{value['per_class']['obligation']['f1']['mean']:.3f} | "
            f"{value['per_class']['permission']['f1']['mean']:.3f} | "
            f"{value['per_class']['prohibition']['f1']['mean']:.3f} | "
            f"{value['macro_f1']['mean']:.3f} |")
    lines += [
        "",
        "这里 Barrientos 的 Macro-F1 0.890 高于本文 0.822，说明它在较窄的三类"
        "模态目标上更强。本文在本批中显示的是六字段抽取及面向后续 BPMN 合规的"
        "接口适配优势；actor、"
        "action、exception、definition 等不能在 Barrientos schema 中直接表达，"
        "所以不能把两边 native F1 强行排成总榜。",
        "本批没有运行 Stage 3，因此不能据此声称已经提高 BPMN 违规检测准确率。",
        "",
        "## 五、1140 次调用是怎样分配的",
        "",
        "| 用途 | 调用数 |",
        "|---|---:|",
        "| 内部一因素：Full + 去 few-shot | 300 |",
        "| 多模块压力：minimal | 150 |",
        "| EStG-150 模块替换：Barrientos-style | 150 |",
        "| Barrientos-native：36×5 | 180 |",
        "| OURS-FULL：36×5 | 180 |",
        "| OURS-Barrientos-module：36×5 | 180 |",
        "| 合计 | 1140 |",
        "",
        f"实际 token：输入 {acc['input_tokens']:,}，输出 "
        f"{acc['output_tokens']:,}；闲时估算成本 ${acc['off_peak_estimate_usd']:.2f}。",
        "",
        "## 六、为了把“我的消融实验”真正做丰富，还缺什么",
        "",
        "下面这些必须逐个只删一个模块，才是导师所说的核心内部消融：",
        "",
    ]
    for item in report["not_yet_run_core_internal_ablations"]:
        suffix = ("（可直接用当前 raw response 离线重放，不需要新 API）"
                  if item.get("suggested_mode") else "")
        lines.append(f"- {item['display_name']}：未完成一因素消融{suffix}")
    lines += [
        "",
        "## 七、现在可以安全说到什么程度",
        "",
        "- 已经能说：few-shot 是当前严格输出接口的关键模块，但其独立语义贡献"
        "尚未隔离；本文完整模块比两个"
        "Barrientos 替换版本更适合本文六字段、面向 BPMN 的输出接口。",
        "- 也必须说：Barrientos 在共享三类 modality 上更好，在自己的 schema 中"
        "也稳定有效。",
        "- 还不能说：本文每个模块都已经分别证明有效，或本文在所有任务上全面"
        "优于 Barrientos；本批也没有评价 Stage 3 违规检测效果。",
        "",
        "**当前判断：1140 次结果不是白跑，但只有其中 Full vs 去 few-shot 是现成的"
        "核心一因素消融；其余应分别归入压力测试、模块替换和外部对照。**",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        if not args.overwrite and (REPORT_JSON.exists() or REPORT_MD.exists()):
            raise RuntimeError("refusing to overwrite classified report v1")
        report = build_report()
        REPORT_JSON.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        REPORT_MD.write_text(to_markdown(report) + "\n", encoding="utf-8")
        print(
            "classified report written: "
            f"{REPORT_JSON.relative_to(ROOT)} / {REPORT_MD.relative_to(ROOT)}")
        return 0
    except (KeyError, OSError, RuntimeError, ValueError) as exc:
        print(f"refused: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
