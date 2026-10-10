# Formal Experiment AI Contract

This directory is the only active experiment surface.

## Current method display name (2026-10-10)

用户要求将活动论文、汇报稿、任务文档和报告中的方法名称统一为
**LLM-based Semantic Extraction（LLM-SE，基于大语言模型的合规语义抽取）**。
Stage 2 任务统一称 Semantic Extraction；Rule Record 是输出，rule-based 是
基线的抽取机制。历史标签 Direct-LLM / LLM-RE 与该方法相同；兼容 ID
`direct_llm`、D1、文件路径、冻结预测/manifest 和不可改写的旧实验事件保持原样。
当前展示名称以 `configs/paper_method_display_names_v1.json` 为准；后续论文报告
生成器使用 LLM-SE。`configs/methods.json` 是正式 benchmark 的冻结哈希来源，
其历史标签按原字节保留。不能因改名改变数值、版本绑定、
实验门禁或将旧结果移植到另一模型/prompt。活动汇报副本见 `paper/README.md`。

## User project-name migration authorization (2026-09-29)

用户要求把旧项目命名全部统一为 LLM4BPC，并明确选择“连历史记录和归档也改，
另外保存原始证据副本”。本授权允许本次命名迁移涉及历史日志、冻结 manifest、
`_retired/`、根 `archive/` 和 `references/` 中的项目名称或路径；必须先保存原始
字节与哈希，另记迁移映射。原始证据副本保持只读，不把迁移后的历史测试记录
当作新代码验证，不重写 Git 提交历史，不改实验数值或科学结论，不恢复退役代码。
这不授权读取或修改 `.env`、真实 API、实验重跑、Gold 内容修改或全量测试。
当前阶段与完成状态见 PROJECT_AUDIT；目录改名只改路径，不替换各 worktree 分支。

## User final paper decision: Stage 2 Table 1 (2026-09-26)

用户要求再次核对并固定第二阶段论文主表，后续不再改变。唯一数值来源为
`outputs/reports/stage2_table1_paper_final_v1.json`：EStG-150、coarse sentence view、
五字段 `pooled_five_span_fields` Overall F1，LLM-SE **0.8378**，Sun 方法本地
重建 Rules-Only **0.7631**，差 **+7.47 个百分点**。保留四位小数；两位舍入是
0.84/0.76，不能截断成 0.83/0.76。modality label 单列，不并入 Overall。
固定来源臂 `direct_llm_formal_arm_v1`（原 v6/R3 快照）与 `b0_formal_arm_v1`；
不再为本表调参、改变评价口径、重跑或用后续消融/actor refinement/100 候选替换。
0.7631 不是 Sun 原论文报告值；不能把 0.8378 移植到另一 prompt/模型版本。
固定的是本表的已验证结果与来源，不把 Stage 3 或其他未完成任务标为完成。
若以后发现客观证据错误，须如实报告并等待用户明确的新决定，不静默改数或隐瞒。
详细来源、计数和写作范围见 `paper/CLAIM_EVIDENCE_MATRIX.md` C54。

## Current user experiment-only delegation (2026-09-24)

本轮用户只要求实验和数据，不写论文、不改 PPT 或绘制论文图。该当前任务优先于
下方历史写作安排：Codex 负责研究设计、协议和验收，机械实现/运行由用户现有
DeepSeek Agent 按 `docs/agent_prompts/STAGE3_TABLE3_V4.md` 执行，用户手动转交。
当前追加修正入口为 `docs/agent_prompts/STAGE3_TABLE3_V4_R1.md`：原卡/授权保留，
R1 冲突条款优先。允许按该卡修正新 wrapper/评价器/请求传输、恢复 Winter 全局
角色词表合同、建立双方共用的限定句法投影 v2；旧数据/阈值/结果不改，输出另版本。
该卡不增加调用额度或自动放行正式表三；未运行方法的主指标记 null，不冒称性能 0。
用户已接受 Sun/Ours 共用的时间约束→顺序边重建补充，以及预检固定的五条新
LLM-SE 抽取：最多 5 次、0 重试、总输出 20,480 tokens、总上限 8.02 USD。
旧 preflight 的 authorized=false 是历史快照，不覆盖本轮授权；执行时另建绑定
该预检和本轮决定的授权/账本，不改历史，也不重复索取这五次许可。
其他新调用、旧实验重跑、Rules+LLM 和全量测试不在授权内。研究预期不是验收分数：
保留真实负结果与极端值，诊断其原因，不能改标签/阈值/样本追分。此范围的构造参考
仍是 AI development reference，不能自动发布 Gold 或声称完整 Sun 端到端复现。

## User writing priority: explain the work and contributions (2026-09-15)

用户明确要求：“目标是写清楚自己的贡献，把自己做的事情都要写清楚，把一些数据都要放在论文里”。
后续论文协作以完成一篇工作交代完整、方法具体、数据可信的应用研究初稿为目标。
逐项说明研究动机、借鉴来源、自己的设计与实现、实验观察和局限；不要只写“使用了 LLM”。
定义、配置、数据统计、设计说明和案例表都可以成为正文内容，不要求每张表证明独立创新。
先整理已有工作与数据并写出完整初稿，再根据具体缺口补必要实验；不要为追求创新数量、
表格数量或穷尽验证而自动扩大实验范围，也不要以“不是核心创新”为由省略必要说明。
相关工作完整登记，正文充分呈现，长明细放附录；与结论有关的失败和负结果也要交代。
具体章节与图表清单见 `paper/README.md` 的“工作、贡献与图表清单”；任务归入主 Pipeline
的 PW1–PW9。数字真实性、来源、完成状态与已有比较口径仍须准确；本文档记录写作要求，
不把未完成实验标为完成，不改变下方两方法范围或 API/Gold/正式发布边界。

## User publication priority: CSCWD 2027 (2026-09-17)

用户希望以 CSCWD 2027 为投稿目标，按 2026-10-31 截稿准备；本轮提供的当届通知
另列 2027-01-31 录用通知、2027-05-26 至 28 Brisbane 会议。保留已有 9 月 30 日
导师完整初稿目标。写作以说明已有工作、受控比较与有证据的观察为主，不为显眼创新
自动新增模块、实验或恢复已取消方法；这不等于放弃原创贡献或保证 C 类会议录用。
最相近文献、证据边界及当届信息核验深度见 `paper/CSCWD_POSITIONING.md`。
不得写“首次 LLM+BPC”或以改名/不同 schema 代替实质差异；完整技术记录与精简会议稿
分层组织。该笔记不是新状态页，计划/进度仍在 MASTER_PIPELINE / PROJECT_AUDIT。
本次投稿准备不新增真实 API、Gold、正式运行或全量测试授权。

## User stop decision: Rules+LLM experiments (2026-09-14)

The user's latest instruction is: “规则+LLM直接不要了，不在进行规则+LLM的任何实验”.
Do not run, resume, rerun, optimize, ablate, or newly evaluate Rules+LLM-Repair
(`sun_llm_fallback`, legacy H1), including the pending S2.12 F-1/F-2/F-3 stages
(27 calls). Do not dispatch other rule-first LLM repair/fallback experiments,
including Stage 3 hybrid fallback, under a different task name.
Preserve existing code, predictions, manifests, authorization records, and
results as historical provenance; their presence or old ready/authorized
statuses does not authorize further hybrid experiments.

The active Stage 2 comparison is Rules-Only versus LLM-SE. Independent
LLM-SE extraction evaluated through the same fixed Stage 3 detector stays
in scope. The previously proposed 137-call execution is superseded: the
remaining planned LLM-SE calls are S2.12 36 plus GDPR 74 = 110; the removed
27 calls must not be reassigned. This cancellation is not API authorization.
Do not require a cancelled hybrid arm to satisfy a future milestone; before
executing/finalizing the reduced comparison, align its machine contract and
freeze checks with this two-method scope without marking missing results done.
This instruction overrides older three-method dispatch templates and budgets.

## Completed review batches (user instruction, 2026-09-23)

用户要求：完成的审核批次封存，除明确寻找历史材料外，不得再次发现为待审核任务。

- 活动区只保留该批人工最终决定；proposal、初审稿、空白模板、临时工具和过程备份
  封存在 `_retired/review_batches/`，不作为后续批次输入、候选、测试数据或任务入口。
- 日常搜索、文件目录和审核队列排除 `_retired/`；不得常规解压、读取或重新检测归档。
  只有用户明确要求追溯该批历史时才查阅；恢复为活动材料仍需明确授权。
- 后续审核使用独立批次 ID 和路径，不复用已封存批次的默认文件名或启动入口。
- 保留历史事件，不把日志中的旧路径和“待审核”状态当作当前任务；实时状态以
  `docs/PROJECT_AUDIT.md` 为准。人工完成不自动发布 Gold 或补填缺失绑定。

## Delegated candidate resolution (2026-09-23)

用户明确要求 AI 直接根据候选解决剩余判断，不将机械整理或可判断的候选再次推回人工。
可生成有证据、明确署名 AI 的补充判定；原人工决定保持不变，不伪称新增判断获得人工
逐项批准，不自动发布正式 Gold。当前 Stage 3 补充判定已完成，结果见
`data/development/stage3_synth/stage3_binding_resolved_reference_v1.json`，
不得因保留 null、无对应或 process-only 就重新创建待用户审核的同批任务。
本轮查阅归档候选是用户明确指定的追溯；默认归档排除规则继续生效。

## Required Reading

The full list below applies to experiment-affecting work. For artifact/prose/
formatting-only work, read both AGENTS.md contracts and the task's relevant
sources; do not traverse the entire experiment state or trigger its checks.

1. `docs/MASTER_PIPELINE.md`
2. `docs/PROJECT_AUDIT.md`
3. `docs/AGENT_RUNBOOK.md`
4. `docs/DIRECTORY_GUIDE.md`
5. `docs/EXPERIMENT_LOG.md`（至少阅读最新事件）
6. `docs/AI_CHANGE_PROTOCOL.md`
7. `docs/ROUTE_LOCK.md`
8. `configs/experiment_contract.json`
9. `configs/methods.json`

`docs/MASTER_PIPELINE.md` is the sole whole-project roadmap and work-breakdown
structure. `docs/PROJECT_AUDIT.md` is the sole live status page. Update those two
files in place; do not create another dated status, handoff, or competing
pipeline document.

`docs/DIRECTORY_GUIDE.md` explains where every class of file belongs;
`docs/FILE_CATALOG.md` is the generated active-file index (archives excluded). Retired material
under `_retired/` is read-only provenance and must never be imported or used as
an active task entry.

`docs/AGENT_RUNBOOK.md` defines task dispatch and copy-ready prompts. Live task
status remains only in `docs/PROJECT_AUDIT.md`. When writing the paper, also
read `paper/README.md` and `paper/CLAIM_EVIDENCE_MATRIX.md`; results without a
formal manifest must remain explicit TODOs.

Before editing human-review data, also read `docs/HUMAN_GOLD_GUIDE.md`.

Sun et al. (2024) supplies the complete three-stage methodological backbone.
Winter et al. (2020) supplies a Stage 3 comparison baseline. Barrientos et al.
(2026) is a candidate source for complex legal data and LLM structured-output,
validation, controlled-vocabulary, and normalization ideas; its labels must not
be treated as Sun-compatible without an explicit adapter and provenance check.

## Mandatory Check and Experiment Log

Governance note: this checkpoint is not institutional or artifact-only, and the full suite is not run twice in the same workspace without a new explicit authorization.

The legacy `audit_*` filenames refer to offline integrity checks and experiment
logs, not third-party audits. The root `AGENTS.md` Validation Scope and Cost
policy and `docs/AI_CHANGE_PROTOCOL.md` govern test selection. This 2026-09-10
policy overrides older blanket full-test instructions in task templates.

PPT/prose/formatting/documentation-only work needs its own content/render/file
checks, not an experiment audit, code tests, or an experiment event. A scoped
Git commit records such work. Formula/claim checking uses existing sources;
it does not authorize running experiments.

For experiment-affecting code/config/schema/prompt/data/evaluator changes,
run the quick check once at the batch boundaries:

```powershell
python formal_experiment/scripts/audit_project.py
```

or, from this directory:

```powershell
python scripts/audit_project.py
```

Select named tests for the changed behavior and its callers. A routine commit,
push, checkpoint, milestone update, event, or handoff does not require full
tests. Full tests (`audit_project.py --with-tests` or equivalent) require
explicit user authorization for this task, a concrete reason, and an expected
duration. Existing authorization need not be requested twice. Never run a
duplicate suite in the shared workspace or escalate because a receipt is stale.

For experiment-affecting changes/runs, `scripts/record_change.py` can run
explicit `--test-target tests/test_example.py` selections (3-minute default
timeout) or reuse a matching full-test receipt. Without either it exits
without running tests or writing logs. Record test scope accurately; focused
verification is not full-suite verification. Human-facing fields stay Chinese;
declare Gold, LLM/API, and artifact handling. See `docs/AI_CHANGE_PROTOCOL.md`.

`integrity_pass: true` permits continued controlled development. It does not
permit final claims. Final metrics require:

```powershell
python scripts/audit_project.py --require-final-ready
```

## Boundaries

- Do not import from `../archive` or `../references`.
- Do not import, execute, or use `_retired/` as an active experiment source.
- Do not auto-fill or alter human Gold.
- Do not let `sun_rule_only` call an LLM.
- Do not run a real LLM/API batch without explicit authorization and a recorded
  call budget.
- Do not overwrite predictions, manifests, Gold, or results by default.
- Do not call the reconstruction exact Sun or Sun original.
- Keep all new experiment code, tests, prompts, data contracts, and reports
  inside this directory.
- The user is authorized to begin editing the v2 `estg_150_human_correction_v1.json`
  file NOW as long as `--require-human-review-ready` is green. This is the
  **input** gate (data + schema + tool locked, 150 sample_ids stable, format-valid
  editing surface). The **freeze** gate (150/150 adjudicated) is reported
  separately as `human_review_freeze_ready`; as of 2026-08-06 it is
  **true** (150/150 adjudicated, annotation frozen; the two gates are
  intentionally distinct: input-ready does NOT require any record to be
  reviewed, and freeze-ready is a **necessary but NOT sufficient** condition
  for declaring formal Gold). Declaring formal Gold also requires
  `route.status==locked`
  AND `stage2_dataset.status==locked_for_human_review` AND
  `stage3.status==locked` AND
  `formal_gold_publication_gate.status` exactly matching the contract's
  `allowed_publication_statuses` whitelist (default
  `["ready_for_formal_gold_publication"]`; see `configs/experiment_contract.json`).
  The deprecated `human_review_ready` alias mirrors `human_review_input_ready`
  and must NOT be used to decide whether formal Gold can be published.

## EStG-150 5-layer data model (v2 workflow, 2026-07-12 21:30)

The single EStG-150 dataset is now split into 5 layers. Only Layer E is
editable by the user; Layers A/B/C/D are immutable. See
`docs/HUMAN_GOLD_GUIDE.md` for the full guide and
`data/development/human_review/ESTG150_REVIEW_WORKFLOW_V1.md` for the
data-flow diagram.

| Layer | Path | Role | Editable? |
|---|---|---|---|
| A. German source | `data/development/estg/estg_selected_150_de.jsonl` | 150 legacy record_ids, raw German | NO |
| B. English translation | `data/development/human_review/estg_150_translation_en_v1.jsonl` | LLM-produced English candidate | NO |
| C. LLM six-element candidate | `data/development/human_review/estg_150_llm_six_element_candidates_v1.jsonl` | modality/actor/action/condition/constraint/exception from legacy LLM draft | NO |
| D. Chinese aid | `data/development/human_review/estg_150_review_aids_zh_v1.jsonl` (placeholder provenance, all null) — active file is selected by `configs/estg150_layer_d.json` `active_path` (e.g. `estg_150_review_aids_zh_v2.jsonl` once authorized LLM run completes 150/150) | text_zh + back_translation_en; v1 is the all-null placeholder, v2 is the filled version on the SAME 150 sample_ids | NO |
| E. Human correction | `data/development/human_review/estg_150_human_correction_v1.json` | user-editable; `llm_candidate` is immutable copy from layer C | **YES** |

Final Gold is `LLM-assisted, human-adjudicated Gold`. The paper MUST
NOT claim it is "from-scratch human Gold" or "without LLM assistance".

## Final-review state semantics (Layer E)

- `format_valid: true` — schema + per-record structural checks
  (span text matches `approved_text_en[start:end]`, span inside
  clause_span, IDs unique within clause, actor_action_map and
  order_relations reference existing IDs, modality is one of 4
  classes, raw DE hash matches source)
- `review_ready: true` — every record has approved_text_en (or
  translation decision=rejected), review_state ∈ {reviewed,
  adjudicated}, all 7 decisions (translation + 6 fields) ∈
  {accepted, edited, rejected, needs_adjudication}
- `freeze_ready: true` — review_state=adjudicated, all decisions
  ∈ {accepted, edited, rejected}, all per-clause modality
  decisions ∈ {accepted, edited, rejected}

The v1 canonical review file
`data/development/human_review/estg_150_canonical_review_v1.json` is
**retired as workflow draft** and kept as provenance only. The old
single-pane tool has been replaced by a two-tab v2 tool that opens
the human_correction file by default.

### Four orthogonal integrity gates (2026-07-13 4-gate split, Event 22; Event 23 harden)

The canonical integrity checker reports four distinct booleans
that are intentionally not collapsed into one. They are stored in
`audit["..."]` and surfaced by `audit_project.py` in this order:

| # | Gate | Current state | Source of truth | Command |
|---|------|---------------|-----------------|---------|
| 1 | `human_review_input_ready` | **true** | `experiment_contract.human_review_gate.status` + membership + structural preconditions | `--require-human-review-ready` |
| 2 | `human_review_freeze_ready` | **true** (150/150 adjudicated) | v2 human_correction per-record adjudicated count | `validate_human_correction.py` `freeze_ready` |
| 3 | `formal_gold_publication_ready` | **true** (2026-08-10 user-authorized formal Gold publication; gate definition unchanged) | gate 2 + `route.status==locked` + `stage2_dataset.status==locked_for_human_review` + `stage3.status==locked` + `formal_gold_publication_gate.status` exact match against `allowed_publication_statuses` whitelist | conservative — any missing or non-locked field, OR non-whitelisted status, keeps it false |
| 4 | `final_experiment_ready` | false | gate 3 + method readiness + frozen input/gold | `--require-final-ready` |

Gate 1 is true at 0/150 once the data sources, schemas, tool, v2
file, authoritative contract gate status, and membership
cross-check are all in place. The user can begin editing
`data/development/human_review/estg_150_human_correction_v1.json`
NOW. **Gate 2 is true only after 150/150 adjudicated; it is a
necessary but NOT sufficient condition for gate 3.** Even if gate 2
becomes true, gate 3 still requires route / data / stage3 /
freeze_policy to each be individually re-locked AND the
formal_gold_publication_gate.status to be an exact match against
the contract's `allowed_publication_statuses` whitelist
(default `["ready_for_formal_gold_publication"]`; the previous
"not blocked and not unknown" fail-open heuristic was removed in
Event 23). Gate 4 adds method readiness and frozen input/gold.
The deprecated alias `audit["human_review_ready"]` mirrors gate 1
(semantic: "user can start the human review NOW"), NOT gate 3.

Event 23 also makes the v2 strict validator the **single source of
truth** for `format_valid` / `review_ready` / `freeze_ready` in
both `status.py` and `audit.py`. Any status / check divergence on
the same v2 file is now a single-source-of-truth violation.

Route was reopened on 2026-07-13 after discovery of final-version method
differences and the official Sun dataset supplement, and re-locked on
2026-08-06 (user-authorized governance; `route.status=locked`). The
150-record EStG-150 v2 human_correction file is the active editing surface
and is NOT a development pack. Gates 3/4 additionally require the stage2
dataset, stage3 and freeze/publication policy locks, which are all re-locked
as of 2026-08-10.

### EStG-150 membership is permanently locked (2026-07-13)

The 150 sample_ids in the active editing file
`data/development/human_review/estg_150_human_correction_v1.json`
are the **same** 150 record_ids as in
`data/development/estg/estg_selected_150_de.jsonl`, with membership
payload sha256=`8573e105d2bc167c6aa0a92c16f79a3aaf725baadfea86f0b5d2b1ea68b1e0d7`
locked in `data/development/estg/estg_150_membership_hashes.json`.
This 150 is:

- **NOT** Sun's original 150 sentence phrase Gold (443 spans).
- **NOT** an exact reproduction of any external dataset.
- The project's `independently_reconstructed_estg_150_v1`
  benchmark, published as `LLM-assisted, human-adjudicated Gold`
  on 2026-08-10 (Stage 2 / Stage 3 Gold artifacts under
  `data/gold/`, executable Gold-blind input v2 under
  `data/input/`, publication manifests under `outputs/reports/`).

Once the user begins editing Layer E, this 150 cannot be
re-sampled, re-seeded, swapped with the legacy development pack,
or replaced with a parallel "new 150" derived from the official
Sun supplement. The official Sun Archive.org supplement
(`Decision_Logic_data.zip`, `input 2.zip`) is reserved for
**method, modality data, and baseline alignment** use only; it
MUST NOT be used to overwrite any of the 150 active sample_ids.
Re-sampling, creating a parallel old/new 150, or migrating any
user-entered human_correction result between two different 150s
is FORBIDDEN. The legacy review pack
(`estg150_review_pack_v1.jsonl` /
`estg_150_canonical_review_v1.json`) and the OCR-derived
`estg_selected_150_en_llm_translated.jsonl` are
**development-only provenance**; they are NOT alternative 150s.
The four orthogonal gates above are unchanged by this rule.



```powershell
python scripts/audit_project.py --require-human-review-ready   # checks gate 1
python scripts/audit_project.py --require-final-ready         # checks gate 4
```

Only a human may change review states to `approved`, `reviewed`, or
`adjudicated`. Agents may validate, explain, and import explicitly supplied
human decisions, but may not infer them.

The three final methods must share frozen input IDs, locked human Gold, output
schema, normalization, evaluator, and Stage 3 configuration:

- `sun_rule_only` (legacy ID for the complete non-LLM Sun Stage 2 baseline,
  not the current heuristic runner)
- `sun_llm_fallback`
- `direct_llm`
