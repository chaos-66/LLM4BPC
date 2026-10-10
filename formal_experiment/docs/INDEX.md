# 文档索引

本文只负责导航。研究主线以 `MASTER_PIPELINE.md` 为准，实时状态以
`PROJECT_AUDIT.md` 和机器完整性检查为准。

## Agent 必读

1. `MASTER_PIPELINE.md` — 三阶段目标、流程图、任务树、依赖和完成标准；
2. `PROJECT_AUDIT.md` — 当前实时状态、当前焦点和 blocker；
3. `AGENT_RUNBOOK.md` — 分阶段派工规则、当前任务 Prompt 模板；
4. `DIRECTORY_GUIDE.md` — 每个目录和文件类别的职责；
5. `EXPERIMENT_LOG.md` — 中文人类可读实验日志；
6. `AI_CHANGE_PROTOCOL.md` — 实验日志、自动检查和记录要求；
7. `ROUTE_LOCK.md` — 当前 EStG-150、Gold 和门禁不变量；
8. `../configs/experiment_contract.json` — 当前阶段机器合同；
9. `../configs/methods.json` — 当前 Stage 2 方法注册表。

编辑人工审核数据前还必须读 `HUMAN_GOLD_GUIDE.md`。

## 论文写作

- `../paper/THESIS_DRAFT.md` — 已启动的中文连续工作稿与结果空表；
- `../paper/CLAIM_EVIDENCE_MATRIX.md` — 主张状态、证据、允许时态和解锁任务；
- `../paper/README.md` — TODO、回填和只读主张复核规则。

## 活动设计规范

- `B0_RECONSTRUCTION_DESIGN.md` — Sun Stage 2 独立重建；
- `STAGE2_CANONICAL_SCHEMA_SPEC.md` — Rule Record 合同；
- `STAGE2_LLM_INNOVATION_DESIGN.md` — H1/D1 设计；
- `EVAL_3DIM_SPEC.md`、`STYLE_EQUIVALENT_SPEC.md` — 语义与结构评价；
- `ANNOTATION_PROTOCOL.md`、`HUMAN_GOLD_GUIDE.md`、
  `HUMAN_GOLD_REVIEW_PACK_SCHEMA_v2.md` — 人工 Gold；
- `ESTG150_DATA_MAP.md` — 唯一 EStG-150 数据地图；
- `LLM_BUDGET_PROPOSAL_2026-07-12.md` — 预算设计，不代表已授权调用；
- `REPRODUCTION_PROTOCOL.md` — 可复现运行要求；
- `USER_DECISION_LOCK_2026-07-12.md` — 具体用户决定和权限边界。

## 研究证据

`research/` 保存 Sun、Winter、Barrientos 的方法、数据和代码身份核查。它们是证据，
不是活动任务入口。

- `research/SUN_MODALITY_DATASET_INGESTION.md` — Sun modality 来源、schema、quarantine、
  development split、许可边界与 S2.1-D 机器门禁证据；
- `../src/formal_experiment/sun_modality_gate.py` — audit/status 共用的独立 fail-closed
  development 数据门禁实现。
- `research/PUBLIC_MARKER_LEXICON_RECONSTRUCTION.md` — S2.3 public marker 来源表、
  生成规则、语言/扩展边界、版本化文件与 hash；
- `../src/bpc_hybrid/sun_style/public_marker_lexicon.py` — S2.3 离线确定性生成、加载与
  fail-closed 机器门禁实现。
- `research/D1_ACTOR_EXPLORATORY_BRANCH_2026-09.md` — LLM-SE Actor 字段
  development-only 探索性支线归档；不是正式 Stage 2 主结果。

## 目录与逐文件导航

- `DIRECTORY_GUIDE.md` — 中文目录地图和新文件放置规则；
- `FILE_CATALOG.md` — 脚本生成的完整逐文件清单；
- `../_retired/` — 已替代路线、日期快照、旧输出和旧脚本的专属只读归档。

未来 Agent 可以追溯 `_retired/`，但不得依据其中材料启动任务、导入代码或覆盖
当前 Pipeline。迁移和恢复规则见 `../_retired/README.md`。

## 实验来源日志与检查历史

- `EXPERIMENT_LOG.md` — 追加式中文人类日志；
- `EXPERIMENT_EVENTS.jsonl` — 追加式机器 change/run/milestone 事件；
- `_retired/logs/AUDIT_LOG_legacy_through_event_29.md` — 事件 1—29 的旧版人类日志；
- `_retired/changes/2026-07/` — 已退出活动流程的历史变更集。
