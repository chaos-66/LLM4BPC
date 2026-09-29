# 项目目录地图

本文同时面向人和 Agent，说明每个目录“放什么、当前能否使用、去哪里找”。逐文件
清单见 `FILE_CATALOG.md`；研究任务顺序见 `MASTER_PIPELINE.md`；实时进度见
`PROJECT_AUDIT.md`。

## 1. 进入项目的固定顺序

1. `MASTER_PIPELINE.md`：完整三阶段路线和任务树；
2. `PROJECT_AUDIT.md`：现在做到哪里、下一项是什么；
3. 本文：目录和文件职责；
4. `EXPERIMENT_LOG.md`：最近做过什么；
5. `../AGENTS.md` 与 `AI_CHANGE_PROTOCOL.md`：操作边界和记录方法；
6. `ROUTE_LOCK.md`、`../configs/experiment_contract.json`、
   `../configs/methods.json`：机器门禁和方法状态。

## 2. 顶层结构

| 路径 | 内容 | 使用规则 |
|---|---|---|
| `AGENTS.md` | Agent 必读合同、安全边界、检查命令 | 修改前必读 |
| `README.md` | 人类入口和当前事实摘要 | 快速入门 |
| `MANIFEST.md` | 控制面、数据面和目录职责总表 | 结构核对 |
| `configs/` | 实验合同、方法注册、路径、schema、Layer D 配置 | 活动；修改会影响门禁 |
| `data/` | 开发数据与未来冻结数据 | 按 development/formal 严格分区 |
| `docs/` | 活动路线、状态、规范、日志和研究证据 | 活动入口只留当前版本 |
| `outputs/` | 可重建报告和诊断 | 正式报告必须绑定 manifest |
| `paper/` | 论文工作稿、TODO 和主张证据矩阵 | 可并行写作；结果必须来自正式 manifest |
| `prompts/` | 版本化 prompt、少样本 fixture、dry-run 产物 | 活动；真实调用仍需授权 |
| `resources/` | marker 词表等静态资源 | 活动、版本化 |
| `scripts/` | 检查、记录、构建、验证和 runner 入口 | 活动命令入口 |
| `src/` | Python 实现 | 活动代码 |
| `tests/` | 离线回归测试和 fixture | 活动验证 |
| `_retired/` | 已退出活动流程但需追溯的材料 | 默认搜索和目录排除；仅明确追溯时查阅，不得导入或直接运行 |

`.pytest_cache/`、`__pycache__/` 和 `.tmp/` 是可再生缓存，不属于研究资产；可以
清除，也不会写入逐文件目录。`.env` 可能含密钥，任何 Agent、目录脚本和日志都
不得读取或打印。

### 工作区改名与 Git worktree

当前工作区根目录为 `D:\Paper\experiment\LLM4BPC`，远端为
`https://github.com/chaos-66/LLM4BPC.git`。目录改名后，在新根目录检查
`git remote -v`、`git worktree list --porcelain` 与各 worktree 的 `.git` 链接。
主目录中的 `.git/worktrees/*/gitdir` 和关联 worktree 的 `.git` 必须双向一致。

先备份链接信息并核对工作目录确实存在，再从新根目录执行 `git worktree repair`。
如果关联 worktree 也随父目录移动，将其**当前实际路径**作为 repair 的参数；
只修主目录无法恢复仍登记在旧位置的嵌套 worktree。修复后逐项检查
`git -C <worktree当前路径> status --short --branch`，确认 HEAD、索引及未提交修改不变。
目录改名造成的 `prunable` 不代表工作可丢弃，不应直接 prune、删除或重新检出。

已存在且仍被聊天使用的 worktree 可保留旧目录名；名称不同不影响 Git，关键是
链接指向当前主仓库。Python 的 `src/bpc_hybrid/` 和冻结证据标识也保持兼容，
不能对整个仓库执行旧名的无差别替换。历史 manifest 中的旧绝对路径仅说明当时
运行位置；确需复现时从当前根目录解析路径并另记新运行，不能改写旧证据。

## 3. 数据目录

| 路径 | 内容 | 当前地位 |
|---|---|---|
| `data/development/estg/` | EStG-150 德文源、候选翻译、旧自动标注和成员 hash | 开发/溯源；成员不可重抽 |
| `data/development/human_review/` | 五层审核工作流；Layer E 是唯一用户编辑面 | 活动审核区 |
| `data/development/gdpr50/` | GDPR 50 条开发候选和旧 Gold | 开发数据，不是正式 Gold |
| `data/development/gold_review/` | Sun Stage 2 Gold 审核候选/模板 | 开发审核材料 |
| `data/development/metadata/` | 旧开发 runner 的 manifest | 开发溯源 |
| `data/development/predictions/` | 旧开发预测 | 不进正式表格 |
| `data/input/` | 未来冻结并由所有方法共享的输入 | 当前保持空壳 |
| `data/gold/` | 未来冻结的人工 Gold | 当前保持空壳 |
| `data/predictions/` | 未来正式预测 | 只由受控 runner 写入 |
| `data/results/` | 未来正式指标和明细 | 默认禁止覆盖 |

完成的审核批次仅保留一份最终人工结果作为项目记录，不再进入待审核队列。
本批 Stage 3 结果为 `data/development/stage3_synth/stage3_binding_human_decisions_v1.json`；
审核过程、工具及备份已压缩封存。后续批次使用独立 ID 与路径，默认不搜索归档。

被替代的熟悉用审核副本和 R15.0 历史输出已经迁入 `_retired/data/`；它们不能
重新成为活动审核面或正式结果。

## 4. 文档目录

`docs/` 顶层只放仍然生效的路线、状态、规范、日志和索引。重要类别如下：

| 类别 | 文件 / 目录 | 说明 |
|---|---|---|
| 主线 | `MASTER_PIPELINE.md` | 唯一完整 Pipeline，可在实验中原位升级版本 |
| 状态 | `PROJECT_AUDIT.md` | 兼容文件名；内容是唯一实时状态页 |
| 导航 | `INDEX.md`、`DIRECTORY_GUIDE.md`、`FILE_CATALOG.md` | 文档地图、目录职责、逐文件清单 |
| 日志 | `EXPERIMENT_LOG.md`、`EXPERIMENT_EVENTS.jsonl` | 中文人类日志 + 原始机器事件 |
| 治理 | `AI_CHANGE_PROTOCOL.md`、`ROUTE_LOCK.md`、`REPRODUCTION_PROTOCOL.md` | 修改、门禁、复现规则 |
| Stage 2 | `B0_RECONSTRUCTION_DESIGN.md`、`STAGE2_*`、`EVAL_3DIM_SPEC.md` 等 | baseline、schema、LLM 和评价设计 |
| Gold | `HUMAN_GOLD_*`、`ANNOTATION_PROTOCOL.md`、`ESTG150_DATA_MAP.md` | 审核规则和数据映射 |
| 研究证据 | `research/` | Sun、Winter、Barrientos 的来源核查；不是任务入口 |
| Agent 派工 | `AGENT_RUNBOOK.md`、`agent_prompts/` | 手册及其较长的静态可复制 Prompt；不建平行状态/交接页，实时派工仍在 `PROJECT_AUDIT.md` |

旧状态、旧交接、旧路线和旧 changeset 统一在 `_retired/docs/` 与
`_retired/changes/`，不再在 `docs/` 建 `history/` 或 `changes/` 平行入口。

## 5. 脚本目录

| 类别 | 典型脚本 | 作用 |
|---|---|---|
| 完整性与日志 | `audit_project.py`、`record_change.py`、`status.py` | 快速检查、全测凭证、追加事件 |
| 目录维护 | `generate_file_catalog.py` | 重建中文逐文件目录，不读取 `.env` |
| 人工 Gold | `build_*review*`、`validate_*review*`、`estg150_review_tool.py` | 构建、审核、验证五层数据 |
| Stage 2 | `check_sun_baseline.py`、`run_sun_rule_only.py`、`run_sun_llm_fallback.py`、`run_direct_llm.py` | baseline 和 LLM 方法入口 |
| Stage 3 | `audit_stage2_to_stage3.py`、`run_stage3_fixture_harness.py` | 适配与离线 fixture 验证 |
| Layer D | `run_llm_zh_aid.py`、`validate_layer_d_v2.py`、`promote_layer_d_v2.py` | 中文辅助层；真实调用必须先获授权 |

`_retired/scripts/` 中的脚本只服务于已退役文件，不属于活动命令集合。

## 6. 代码与测试

- `src/bpc_hybrid/`：Stage 1/2/3 业务实现、Sun 风格规则、LLM 接口、评价和 schema。
- `src/formal_experiment/`：项目路径、合同状态、完整性检查和 EStG-150 审核服务。
- `paper/`：论文连续工作稿和主张证据矩阵；不能反向定义实验状态。
- `tests/fixtures/`：离线 BPMN、Sun-compatible、few-shot 等固定样例。
- `tests/test_*.py`：所有活动回归测试；归档材料若仍承担历史防回归证据，测试必须
  明确从 `_retired/` 读取并标注“历史证据”。

修改文件集合后运行 `python scripts/generate_file_catalog.py` 重建目录；只检查是否
过期可运行 `python scripts/generate_file_catalog.py --check`。

## 7. 新文件应该放哪里

- 新活动实现进 `src/`，命令入口进 `scripts/`，测试进 `tests/`。
- 论文正文、TODO 和主张矩阵进 `paper/`；正式结果只从 manifest 定向回填。
- 新研究证据进 `docs/research/`；新的当前规范直接更新已有活动文档。
- 临时输出进 `.tmp/` 或 `outputs/development/`，不得混进 formal 数据目录。
- 被替代但需要追溯的文件迁入 `_retired/`，同步更新 `_retired/MANIFEST.md`、
  `FILE_CATALOG.md` 和实验日志；恢复时需要用户批准。
- 不确定去向时先查本文和 `MANIFEST.md`，不要新建平行 status、handoff、pipeline、
  history 或 changes 目录。

## Stage 3 R1 artifacts (2026-09-24)

- `configs/stage3_table3_v4_execution_r1.json` freezes the R1 matrix contract.
- `src/bpc_hybrid/sun_stage3/temporal_projection_v2.py` and `src/bpc_hybrid/winter_stage3/global_roles.py` implement R1-B.
- `scripts/run_stage3_table3_v4_r1.py` / `scripts/evaluate_stage3_table3_v4_r1.py` run and independently evaluate Table 3 R1.
- `scripts/run_stage3_d1_v4_r1.py` is the repair of the five-call Direct-LLM extraction runner.
- `data/predictions/stage3_v4_d1_frozen_v1/` stores real D1 raw responses, ledger, canonical predictions, and manifest.
- `outputs/development/stage3_table3_v4_r1/` stores the 900-signal inference matrix.
- `outputs/reports/stage3_table3_v4_r1.{json,md,manifest.json}` and `outputs/reports/experiment_tables_delivery_v2.json` are the evaluation and data index.
- `outputs/reports/stage3_temporal_scope_candidates_r1.{json,md}` are future natural-after candidate notes, not current benchmark data.
