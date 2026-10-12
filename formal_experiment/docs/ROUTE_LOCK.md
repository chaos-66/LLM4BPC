# EStG-150 唯一数据集 + LLM-assisted 人工 Gold 工作流路线锁

> **文档边界（2026-07-14）**：全项目 Part 1/2/3 目标、基线矩阵、任务分解与
> 里程碑以 `MASTER_PIPELINE.md` 为唯一主线。本文只锁定 EStG-150、人工 Gold
> 和当前执行门禁；它不授权真实 LLM/API，也不代替 Part 3 扩展的后续合同重锁。

> 状态：2026-07-13 11:30 路线 v2 工作流"启动门禁"与"冻结门禁"分离。
> 启动门禁（`human_review_input_ready`）在 0/150 时即可为 true——意味
> 着数据来源、150 条 membership、英文翻译、六要素 schema、审核工具已经
> 锁定，用户可以立刻开始逐条人工审核。冻结门禁（`human_review_freeze_ready`）
> 在 150 条全部人工裁决完成后才允许声明正式 Gold。这两个门禁刻意分开：输入
> 已就绪 ≠ 审核已完成，写作或下游运行不能把两者混为一谈。
>
> 2026-07-12 21:30 v1 工作流退役为 workflow draft；v2 工作流上线
> 作为 active editing surface。完整路线锁在 v2 下生效，但 route v2 仍
> 开放等待最终发表版 Sun Part 2 实现。
>
> **2026-08-06 route v2 重新锁定（用户授权治理决策）**：最终版方法对齐已按
> 方法级独立复现口径完成（B0-R2 verified + `docs/B0_R2_METHOD_CROSSWALK.md`
> 11 元素 + `method_conformance_status=verified_method_level_independent_reconstruction`
> （2026-08-04 用户授权）+ official Sun supplement 57 文件 hash 匹配 + mentor
> provenance）；`experiment_contract.json` `route.status=locked`、
> `stage2_dataset.status=locked_for_human_review`（phrase Gold freeze 150/150
> 达成，2026-08-06 恢复用户裁决）。formal Gold 发布仍差 Part 3 锁定 +
> publication gate 白名单匹配。

## 1. 数据集单源（不可变）

唯一 membership：

```text
data/development/estg/estg_selected_150_de.jsonl
```

150 个 legacy record_id 来自 `data/development/estg/estg_150_membership_hashes.json`。
SHA-256 记录在同一个文件 `selected_membership.membership_payload_sha256` 中。

**禁止**：
- 重新抽样、替换 sample membership
- 创建并行 "old 150 / new 150"
- 修改原始德文/英文候选/LLM 候选

**允许**：
- 同一 150 的不同处理层（5 层数据模型，见 `docs/HUMAN_GOLD_GUIDE.md` §1）
- 旧 layer C 候选源 `estg_gold_150_llm_draft.jsonl` 重命名为
  `estg_150_llm_six_element_candidates_v1.jsonl`，明确为 legacy LLM
  candidate 而非 Gold

## 2. LLM-assisted, human-adjudicated Gold 路线

- LLM 候选（layer C）由用户单独授权的真实 LLM 运行产生；本任务使用
  旧 draft 作为初始候选，并**未调用真实 LLM**
- 用户通过 `scripts/estg150_review_tool.py` 在 layer E 上做人工修正
- 每个六要素字段必须由人显式决策（accepted/edited/rejected/needs_adjudication）
- 复制候选不等于批准
- 工具在每条 span 的字符位置超出 clause_span / 与 approved_text_en 不
  一致 / id 重复时拒绝保存
- 标记 reviewed/adjudicated 前 validator 必须通过
- 最终 Gold 在 layer E freeze_ready=true 后由 `audit_project.py` 确认
  + 在论文中称为 "LLM-assisted, human-adjudicated Gold"

## 3. 中文 + 英文回译辅助（仅辅助）

- layer D 字段目前全 null（"尚未生成中文核对辅助"）
- **不调用真实 LLM** 自动填充
- 中文和英文回译**不进入**：
  - 英文 span 决定
  - 正式 Gold offset
  - Part 2 / Part 3 evaluator
  - 自动批准
- 未来若要填充，需用户单独授权 + `--max-calls N` 预算 + audit event 留痕

## 4. 与 route v2 的关系

- 路线 v2（`docs/ROUTE_LOCK.md`）锁的是 B0/H1/D1 三组方法 + Part 3
  + 输出 schema + evaluator
- 人工 Gold 来源（route v2 之前写"由用户审核"，现在改为"LLM-assisted,
  human-adjudicated"）是 route v2 的子约束，不影响其它
- 三组方法仍 blocked（见 audit `formal_methods_not_ready`）

## 5. 不变量（必须保持）

- `membership_payload_sha256` 与 `estg_150_membership_hashes.json` 完全一致
- layer A/B/C/D SHA-256 在每次 save 时不变
- 唯一人工编辑文件 = `data/development/human_review/estg_150_human_correction_v1.json`
- layer E 初始 150/150 needs_review, 0 approved_en, 0 decided fields
- 旧 `estg_150_canonical_review_v1.json` 标记 retired，**不被新工作流
  写覆盖**
- references/ 和 archive/ 永远只读
- 真实 LLM/API 不会在 layer E 工具中调用
- **单条资格校验 ≠ 全局聚合校验**: 工具的 "本条已复核" /
  "本条已裁决" 按钮使用单条资格校验,只检查当前 record;全局
  `review_ready` / `freeze_ready` 只用于状态栏和 audit,不阻塞
  第一条记录的标记

## 5.1 启动门禁 vs 冻结门禁（2026-07-13 拆分，2026-07-13 11:30 四门禁再对齐）

为了消除 audit 中"用户现在可以编辑"与"不得开始人工审核"同时出现的
矛盾表述，并把"可以开始审核"和"可以发布正式 Gold"两个不同语义彻底分开，
路线锁维护四个正交状态：

| # | 状态 | audit 字段 | 0/150 时 | 150/150 adjudicated 时 | 命令 |
|---|---|---|---|---|---|
| 1 | 启动门禁（input ready） | `human_review_input_ready` | **true** | true | `python formal_experiment/scripts/audit_project.py --require-human-review-ready` |
| 2 | 注释冻结门禁（annotation frozen） | `human_review_freeze_ready` | false | **true** | `python formal_experiment/scripts/validate_human_correction.py` 的 `freeze_ready` 行 |
| 3 | 正式 Gold 可发布门禁 | `formal_gold_publication_ready` | false | 仅在 route/dataset/stage3/freeze_policy **同时**重新锁定时才 true | audit 报告 |
| 4 | 最终实验可运行门禁 | `final_experiment_ready` | false | 仅在 gate 3 + 三方法就绪 + 冻结 input/gold 时才 true | `python formal_experiment/scripts/audit_project.py --require-final-ready` |

- 启动门禁（gate 1）为 true 即代表：数据来源、150 条 membership、英文翻译、
  六要素 schema、审核工具、authoritative contract
  `human_review_gate.status` 全部就位；用户可以开始人工审核。route
  v2 是否重新锁定不影响 gate 1。
- 注释冻结门禁（gate 2）为 true 即代表：150 条全部 adjudicated；
  这是声明正式 Gold 的**必要不充分**条件。
- 正式 Gold 可发布门禁（gate 3）只有在 gate 2 + route.status=locked
  + stage2_dataset.status=locked_for_human_review + stage3.status=locked
  + `formal_gold_publication_gate.status` 精确属于机器合同的
  `allowed_publication_statuses` 白名单时才为 true。**保守策略**：任何一项缺失、
  非 locked 或不在白名单，都使 gate 3 保持 false，不允许猜测放行。
- 最终实验可运行门禁（gate 4）在 gate 3 之外再要求：三方法全部就绪、
  冻结 input/gold 已写入。当前 0/150 时一定为 false。
- `audit.human_review_ready` 是 gate 1 的 DEPRECATED 别名，保留是为了
  不破坏 `--require-human-review-ready` 命令名。**新代码**需要
  "ready to publish Gold" 必须使用 `human_review_freeze_ready` /
  `formal_gold_publication_ready` / `final_experiment_ready`，不要依赖
  这个别名。

## 6. 工具与脚本入口

- 数据层生成：`scripts/build_estg150_review_layers.py`
- 人工修正工具：`scripts/estg150_review_tool.py`（薄壳,只调 service）
- 校验：`scripts/validate_human_correction.py`（v2 layer E 全局聚合）
- 旧 v1 sanity check：`scripts/validate_canonical_review.py`（仅 dev 用）
- 路径常量：`src/formal_experiment/paths.py`（HUMAN_CORRECTION_FILE 等）
- **Service 层**（v2 新增）：`src/formal_experiment/estg150_service.py`
  - `HumanCorrectionService` 纯逻辑层: `save_draft` / `validate_current_record`
    / `mark_reviewed` / `mark_adjudicated` / `create_backup` / `append_action_log`
    / `undo` / `accept_translation` / `edit_translation` / `accept_field` /
    `edit_field` / `reject_field`
- **Validator 层**（v2 新增）：`src/formal_experiment/estg150_validator.py`
  - `validate_record_format` / `validate_record_for_review` / `validate_global`
- 审计：自动通过 `audit_project.py` 跑

## 7. 论文必须披露的项

- 5 层数据模型（特别是 layer C 来自 `estg_gold_150_llm_draft.jsonl`）
- 复制不等于批准
- 工具的 4-way modality 强制选择 + 显式 field decision
- 如未来 LLM 候选由 D1 同一模型产生，必须披露并增加盲审样本
- 中文辅助不参与 Gold
- 当前 Layer D 仍为 `not_generated`,**不**得声称"中文回译审核流程
  ready";需在 `docs/LLM_BUDGET_PROPOSAL_2026-07-12.md` 给出设计草案
  + 用户单独授权后,才能 fill Layer D

## 8. 后续审批项

- 中文 / 英文回译真实 LLM 调用:需用户单独授权 + 选定具体模型(非
  `annotation-only-default` placeholder) + `--max-calls 200` per
  batch × 至少 4 batch(1 Layer C + 3 Layer D)
- 真实 LLM 重跑 layer C:需用户单独授权
- 旧 `estg_gold_150_v1_backup.jsonl` / `estg_gold_150_v2_distribution_targeted.jsonl`：
  仍为 development provenance，不进入 layer C
- 真实 LLM 产物**只**写 `data/development/estg/llm_candidate_runs/<run_id>/`,
  **不**写 `data/input/` / `data/gold/` / `data/predictions/` / `data/results/`
- runner 本身**未实现**,目前只有设计草案
