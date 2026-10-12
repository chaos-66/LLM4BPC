# Reproduction Protocol

本协议描述 route v2 重新锁定并达到 final-ready 之后的正式复现流程。当前尚不可执行。

## 1. Freeze Contract

冻结前写入 manifest：数据来源、许可、sample IDs、SHA-256、annotation schema、split/seed、三组方法命令、代码 commit、依赖版本、模型、prompt、temperature、调用上限、threshold 和 evaluator version。

## 2. Shared Inputs

三组方法读取 `formal_experiment/data/input/` 中同一文件；Gold 只能位于 `formal_experiment/data/gold/`，runner 不得读取 Gold。

## 3. Methods

- `sun_rule_only`：遗留 ID；正式含义是完整 final-version Sun Part 2
  （BERT-TextCNN + CoreNLP/Tregex/Tsurgeon），无 LLM。
- `sun_llm_fallback`：先运行同一完整 baseline，仅按预注册 trigger 调 LLM。
- `direct_llm`：每个输入一次 direct structured extraction，不运行规则。

所有输出写入不同文件并带 manifest。已存在目标文件时默认拒绝覆盖。

## 4. Validation

每个 prediction 必须通过：

- JSON/schema version。
- controlled modality vocabulary。
- source ID 唯一且与 input 完全相等。
- phrase span 在原文范围内且 text 与 span 一致。
- multi-clause ID/parent ID 一致。
- deterministic normalization。
- Sun rule tuple 与六字段一致。
- LLM provenance/call/error metadata 完整。

## 5. Part 2 Evaluation

统一 evaluator 计算每 concept 的 extracted、matched/TP、misclassified/FP、missed/FN、P/R/F1，同时给出 micro/macro。不得在看到结果后修改 partial-match threshold。

## 6. Part 3 Evaluation

固定同一 BPMN parser、similarity engine、gamma/delta threshold 和 Gold。三组 Part 2 records 分别运行 matching 与 checking，输出 AP/MAP 和三类 violation P/R/F1。

## 7. Audit Sequence

```powershell
python formal_experiment/scripts/audit_project.py --require-final-ready
python formal_experiment/scripts/audit_project.py --with-tests
python formal_experiment/scripts/run_formal_pipeline.py --list-commands
```

只有第一条返回 0 后，才可以在用户明确确认真实 LLM 调用范围后执行正式 runner。

每次 material change 还必须通过 `scripts/record_change.py` 写入
`EXPERIMENT_LOG.md` 与 `EXPERIMENT_EVENTS.jsonl`。正式 manifest 应引用对应事件时间、
Git commit 与测试摘要。

## 8. Reporting Boundary

报告必须区分 exact Sun、paper-faithful reconstruction、direct LLM control 和 Barrientos-inspired engineering。Part 2 指标与 Part 3 AP/MAP/violation 指标分表报告；所有 failed/skipped/API-error/schema-invalid 样本计入覆盖说明。
