# Human Process Gold Guide (S1.5) / 人工 Process Gold 核对指南（S1.5）

This guide tells the USER what to verify for the Part 1 human Process Gold.
It complements the (gate-locked) `docs/STAGE1_HUMAN_GOLD_GUIDE.md` protocol
with a concise bilingual review walkthrough. Nothing here replaces human
decisions: the agent only prepares and validates.

本指南告诉用户 Part 1 人工 Process Gold 需要核对什么。它是
`docs/STAGE1_HUMAN_GOLD_GUIDE.md`（门禁锁定协议）的简明双语补充。一切决定只能由用户做出。

## What you are reviewing / 你要核对什么

For each of the 7 GDPR BPMN files (45 activities, 135 label fields) you
review the machine-parsed Process Record (structure) and the three label
fields per activity (actor / action / business_object).

对 7 个 GDPR BPMN（45 个活动、135 个标签字段），你核对机器解析的 Process Record
（结构）与每个活动的三个标签字段（actor / action / business_object）。

## Decision meanings / 每种 decision 的含义

| Field 字段 | States 状态 | Meaning 含义 |
|---|---|---|
| review_state | unreviewed / reviewed / adjudicated | overall record status 记录整体状态 |
| structure_annotation.decision | unreviewed / accepted_candidate / corrected / needs_adjudication | is the parsed structure right? 解析结构是否正确（即使完全正确也须显式选 accepted_candidate） |
| label field (actor/action/business_object).status | unreviewed / present / absent / needs_adjudication | is the label present in the Gold, absent, or disputed? 标签在 Gold 中存在/不存在/有分歧 |

## What to look at / 具体要看什么

- **Empty lanes / 空 lane**: GDPR-7 lanes have no name; actors come from the
  pool/participant names — verify the pool-level actor assignment.
  空 lane：GDPR-7 的 lane 无名称；actor 来自 pool/participant 名——请核对 pool 级 actor 归属。
- **Implicit actors / 隐含 actor**: if an activity has no explicit actor,
  decide `absent` unless the context clearly implies one; do not guess.
  活动无显式 actor 时选 `absent`，除非上下文明确隐含；不要猜测。
- **Gateways / 网关**: verify exclusive/parallel gateways and their
  incoming/outgoing flows.
  核对 exclusive/parallel 网关及其进出流。
- **Loops / 循环**: reachability cycles are machine-detected — confirm they
  are real process loops, not parsing artifacts.
  可达性循环由机器检测——请确认是真实流程循环而非解析产物。
- **Parallel / 并行**: parallel splits/joins must keep their parallelism;
  do not reorder to sequential.
  并行分叉/汇合必须保持并行，不要改成顺序。
- **Unreachable paths / 不可达路径**: machine-flagged unreachable nodes —
  confirm or correct.
  机器标记的不可达节点——请确认或纠正。
- **Candidate errors / 候选错误**: edit via `import` with explicit
  `corrected` gold_process_record; the tool never auto-fills.
  通过 `import` 显式提供 corrected gold_process_record；工具绝不自动填写。

## Tool usage / 工具用法

```
python scripts/stage1_review_tool.py list
python scripts/stage1_review_tool.py show gdpr_1_data_breach
python scripts/stage1_review_tool.py import my_decisions.json   # atomic save + backup
python scripts/stage1_review_tool.py validate
python scripts/stage1_review_tool.py backup | undo
```

## Freeze conditions / 冻结条件

`freeze_ready=true` requires: 7/7 records `adjudicated`; structure decisions
in {accepted_candidate, corrected}; 135/135 label fields resolved
(present/absent) with consistent values; `review_summary` recomputed and
consistent. Only the user may set these states.

冻结条件：7/7 记录 adjudicated；结构决定 ∈ {accepted_candidate, corrected}；
135/135 标签字段 resolved 且值一致；review_summary 重算一致。只有用户能设置这些状态。
