"""Reproducible, offline evidence for the AI review of 54 residual errors.

No sentence text enters versioned reports. Review interpretations are explicitly
separate from mechanically verified counts; no Gold is changed.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bpc_hybrid.modality_benchmark import boundary, data, llm_se

CASES = ROOT / "configs/supplement/sun_modality_review_cases_v1.json"
PARENT = ROOT / "outputs/reports/sun_modality_fewshot_v1.json"
JOURNAL = ROOT / "outputs/development/sun_modality_fewshot_v1/execution_v1/local_only/events.jsonl"
REPORT = ROOT / "outputs/reports/sun_modality_review_v1"
LOCAL = ROOT / "outputs/development/sun_modality_review_v1"

MARKERS = {
    "commencement": r"\bin kraft\b",
    "liability": r"\bhaft(?:et|en)\b",
    "automatic_amount": r"\b(?:erhöht|vermindert|verkürzt|verringert|erhöhen|vermindern) sich\b",
    "status_waiver_or_no_effect": r"\b(?:befreit|unberührt)\b|\bnicht berührt\b|\berfolgt nicht\b",
    "declarative_applicability": r"\b(?:gilt|gelten)\b.*\b(?:sinngemäß|entsprechend)\b",
    "negative_consideration": r"\bnicht zu berücksichtigen\b",
    "negative_application": r"\bnicht anzuwenden\b",
    "upon_request": r"\bauf antrag\b",
    "conditional_only": r"\bnur\b.*\b(?:wenn|soweit|insoweit)\b|\b(?:wenn|soweit|insoweit)\b.*\bnur\b",
}
FAMILY_NAMES = {
    "legal_effect_or_status": "法律后果、状态或陈述被读成义务/许可/禁止",
    "eligibility_limit_boundary": "资格、数量、期限与规范边界（含歧义）",
    "input_fragment": "输入不完整、主断言不足",
    "condition_split": "前置条件被拆成独立规则",
    "multi_proposition_projection": "独立多命题投影为第一clause标签",
    "coordinated_predicate_scope": "并列谓词或句尾规范作用域遗漏",
    "directive_or_annotation_boundary": "指令被范围吸收或标注边界不明确",
    "implicit_option": "申请触发的选择权未被识别",
}


def write_new(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def verify_cases(review, parent):
    cases = review["cases"]
    indexed = {x["sample_id"]: x for x in cases}
    if len(cases) != len(indexed) or len(cases) != len(parent["fewshot_errors"]):
        raise ValueError("review must cover each error exactly once")
    fields = ("sample_id", "gold", "fewshot", "boundary", "v6", "sun")
    if {tuple(x[k] for k in fields) for x in cases} != {tuple(x[k] for k in fields) for x in parent["fewshot_errors"]}:
        raise ValueError("review membership or saved labels differ from parent")
    if review["human_adjudication_performed"] or review["gold_changes"]:
        raise ValueError("AI review cannot claim human adjudication or Gold edits")
    return indexed


def marker_summary(train):
    return {name: {"pattern": pattern,
                   "label_counts": dict(Counter(row.label for row in train if re.search(pattern, row.text))),
                   "sample_ids": [row.sample_id for row in train if re.search(pattern, row.text)]}
            for name, pattern in MARKERS.items()}


def build_evidence():
    review = json.loads(CASES.read_text(encoding="utf-8"))
    if boundary.digest(PARENT.read_bytes()) != review["parent_report_sha256"]:
        raise ValueError("parent report drift")
    if boundary.digest(JOURNAL.read_bytes()) != review["parent_journal_sha256"]:
        raise ValueError("parent journal drift")
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    cases = verify_cases(review, parent)
    for name, spec in data.EXPECTED.items():
        if data.sha256_file(spec["path"]) != spec["sha256"]:
            raise ValueError("split drift: " + name)
    test = {row.sample_id: row for row in data.load_split("test")}
    finished = {x["sample_id"]: x for x in boundary.read_events(JOURNAL) if x["kind"] == "finished"}
    if set(finished) != set(test):
        raise ValueError("journal population mismatch")
    actual_errors = {sid for sid, row in finished.items() if row["label"] != test[sid].label}
    if actual_errors != set(cases):
        raise ValueError("review no longer matches recomputed errors")
    multiple, multi_errors, later_gold = [], [], []
    evidence, local_cases = [], []
    for sid, row in finished.items():
        if boundary.digest(row["raw_content"].encode()) != row["response_sha256"]:
            raise ValueError("raw output hash mismatch")
        obj = llm_se._extract_json_object(row["raw_content"]) or {}
        clauses = obj.get("clauses", [])
        labels = [c.get("modality", {}).get("label") for c in clauses]
        if len(labels) > 1:
            multiple.append(sid)
            if sid in cases:
                multi_errors.append(sid)
        if sid not in cases:
            continue
        later = test[sid].label in labels[1:]
        if later:
            later_gold.append(sid)
        evidence.append({**cases[sid], "clause_labels_in_order": labels, "gold_label_present_in_later_clause": later,
                         "parse_status": row["parse_status"], "raw_response_sha256": row["response_sha256"]})
        local_cases.append({**cases[sid], "source_text": test[sid].text, "model_record": obj})
    evidence.sort(key=lambda x: x["review_index"])
    local_cases.sort(key=lambda x: x["review_index"])
    result = {"suite_id": "SUN-MODALITY-REVIEW-001", "parent_macro_f1": parent["metrics"]["fewshot"]["macro_f1"],
              "review_author": review["author"], "human_adjudication_performed": False, "gold_changes": False,
              "error_count": len(cases), "confusion_matrix": parent["metrics"]["fewshot"]["confusion_matrix"],
              "review_family_counts": dict(Counter(x["primary_family"] for x in cases.values())),
              "family_counts_are_ai_interpretations": True,
              "structural_facts": {"multi_clause_all": len(multiple), "multi_clause_errors": len(multi_errors),
                                   "gold_label_present_later_count": len(later_gold), "gold_label_present_later_ids": later_gold},
              "training_marker_evidence": marker_summary(data.load_split("train")), "reviewed_cases": evidence,
              "bindings": {"parent_report_sha256": review["parent_report_sha256"],
                           "parent_journal_sha256": review["parent_journal_sha256"],
                           "review_cases_sha256": boundary.digest(CASES.read_bytes()),
                           "analysis_source_sha256_lf_utf8": boundary.digest(Path(__file__).read_text(encoding="utf-8").encode()),
                           "split_sha256": {name: spec["sha256"] for name, spec in data.EXPECTED.items()}},
              "limitations": ["错误家族与拟人工审读步骤是AI解释假设，不是已验证的模型内部原因或新增人工金标。",
                  "train标记统计是词组匹配候选，未隔离每个标记在主句/从句中的角色，不能直接视为分类规则的精确率。",
                  "参考同一测试集错误后设计prompt，存在选择偏差；无独立盲测或新性能证据。",
                  "后续clause已有金标类别不代表可无损改成句级首标签；不通过重排、删除或统一独立命题取巧。",
                  "输入残缺和跨类近似措辞只能列为待复核问题，不修改Gold或虚构缺失上下文。"],
              "new_api_calls": 0, "new_performance_metrics": None}
    return result, local_cases


def main():
    result, local_cases = build_evidence()
    for path in (REPORT.with_suffix(".json"), REPORT.with_suffix(".md"), LOCAL / "case_review_local.json"):
        if path.exists():
            raise ValueError("refusing to overwrite existing review: " + str(path))
    write_new(REPORT.with_suffix(".json"), result)
    write_new(LOCAL / "case_review_local.json", local_cases)
    lines = ["# few-shot剩余54条错误：AI审读与提示词修改依据", "",
             "这是保存预测的离线分析。逐条解释由AI提出，未进行独立人工裁决；没有修改Gold或调用API。", "",
             "| 审读家族（解释性归类） | 条数 |", "|---|---:|"]
    for key, count in result["review_family_counts"].items():
        lines.append(f"| {FAMILY_NAMES[key]} | {count} |")
    facts = result["structural_facts"]
    lines += ["", f"程序核实：426条中{facts['multi_clause_all']}条有多个clause；54个错误中有{facts['multi_clause_errors']}条。"
              f"其中{facts['gold_label_present_later_count']}条的金标类别已出现在后续clause，首有效clause投影没有使用它。",
              "逐条审读将其中1条归为前置条件误拆，另3条归为独立多命题投影限制；两类修法不同。", "",
              "训练集对照（以下仅为透明词组匹配候选，不是已证明的全句规则）：", "",
              "| 标记家族 | train各类计数 |", "|---|---|"]
    for name, row in result["training_marker_evidence"].items():
        lines.append(f"| {name} | {json.dumps(row['label_counts'], ensure_ascii=False)} |")
    lines += ["", "建议写入新prompt的审读步骤：", "",
              "1. 先定位完整主断言，把条件保留在conditions中，识别德语无wenn的倒装条件。",
              "2. 区分法律状态/自动结果与要求主体行动；生效、责任归属、自动金额变化不能只因法律约束力就标义务。",
              "3. 查否定作用域：不发生、不受影响、免除义务与禁止实施动作分开。",
              "4. 查资格与选择：数量、期限或条件不自动决定definition；明确申请选择也不必出现kann。",
              "5. 扫描并列谓词和句尾独立义务/禁止，保留真实clause顺序，不用固定类别优先级。",
              "6. 残缺输入不补词猜标签；短句有完整适用断言时也不因缺actor/action丢弃。", "",
              "新分支不改第一有效clause评价器；多命题投影限制仍然存在。效果必须另行授权运行后判断。", ""]
    lines += ["- " + note for note in result["limitations"]]
    with REPORT.with_suffix(".md").open("x", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    print(json.dumps({"errors_reviewed": result["error_count"], "families": result["review_family_counts"],
                      "structural_facts": facts, "new_api_calls": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
