# Formal Experiment

## 论文主实验

[paper_experiments/](paper_experiments/) 按《LLM-Based Semantic Extraction for Design-Time Business Process Compliance Checking》所附 PDF 的表 I、II、III 和图 3 整理。德语情态四分类作为补充实验单列。五个子目录存放实际实验文件，查看结果可直接从下表进入。

| 实验 | 收录内容 | 首先打开 |
|---|---|---|
| 01 · BPMN 解析 | 115 个 BPMN、对应的 Process Record、解析器和记录 schema。流程样本以 `case_id` 对应表 III。 | [BPMN](paper_experiments/01_bpmn_process_records/bpmn/) · [Process Records](paper_experiments/01_bpmn_process_records/process_records.json) |
| 02 · 表 I，EStG-150 语义抽取 | 150 条推理输入、正式 Gold、Sun 与 LLM-SE 的逐条预测、提示词、后处理和评分实现。五字段合并计算 Micro-F1，情态另算 Macro-F1。 | [表 I](paper_experiments/02_estg150_table_I/table_I.json) · [输入和 Gold](paper_experiments/02_estg150_table_I/shared/) |
| 03 · 表 II，E/S/J 消融 | 8 份提示词，8 组各 150 条预测。共用 02 的 Gold 和原始 span 评分口径。每行保留样本 ID、有效性状态和预测记录。 | [表 II](paper_experiments/03_estg150_table_II_ablation/table_II.json) · [各组预测](paper_experiments/03_estg150_table_II_ablation/predictions/) |
| 04 · 表 III 和图 3，GDPR 合规检查 | 33 条法规、两种抽取器的原始与转换后 Rule Record、开发集参考标签、三种方法在 201 个单元上的判定。图 3 附 9 组阈值的逐项预测、曲线数据和矢量图。 | [表 III](paper_experiments/04_gdpr_table_III_and_fig3/table_III.json) · [逐项判定](paper_experiments/04_gdpr_table_III_and_fig3/predictions_201.jsonl) · [图 3](paper_experiments/04_gdpr_table_III_and_fig3/fig3/fig3_sun_formula_replay.pdf) |
| 05 · 德语情态四分类 | Sun 本地重建、原 22-shot、24-shot、E1 的 426 条全量结果及逐类 TP/FP/FN。S1 只有 3 条配对试测。 | [全量比较与 E1 变化](paper_experiments/05_german_modality_426/full_test_results.json) · [S1 的 3 条实际返回标签](paper_experiments/05_german_modality_426/S1_pilot.json) |

表 I 固定对比与表 II 的 `111` 各用一份独立保存的 LLM-SE 输出，五字段 Micro-F1 分别为 0.7294 和 0.7280。原始文件映射与 SHA-256 见[表 I/II 冻结清单](outputs/evidence/g04_fine_gold_span_formal_results_v2/manifest.json)。表 II 打包时从逐条预测中取出 `sample_id`、`request_status` 和 `record`，去掉请求编号等运行字段。

表 III 的 Sun 和 LLM-SE 使用 10 月 14 日修正事件对象范围后的结果，Winter 使用 10 月 12 日同一批 201 单元的预测。只在正负参考标签明确、顺序检查符合论文纳入范围的单元上计分。原始 9×9 选参可查[网格、目标及选中参数](paper_experiments/04_gdpr_table_III_and_fig3/threshold_selection.json)。保存的选参摘要没有 81 个点的逐点分数。图 3 的数据来自随后固定一轴的 9 组阈值，两条曲线共用中心点。[Sun/LLM-SE 结果来源（本机）](outputs/reports/sun_formula_replay_20261014/metrics_comparison.json) · [Winter 结果来源](outputs/reports/stage3_reproduction_repair_20261012_v2.json)

德语四分类沿用 Rule Record 顺序中首个非空情态标签。E1 的 426 条含试测复用的 5 条和后续 421 条。S1 在直接目标上仍把引导语列为第一条定义，后续许可列第二，按预设条件停止。原始德语文本、逐句配对和含训练例句的 4 份完整提示词仅在本机 `paper_experiments/05_german_modality_426/local_only/`。逐类错误和个案解释见 [E1 实验收尾记录](outputs/reports/sun_modality_e1_full_v1_completed.md)。

目录中的方法文件供对照实现；运行器继续从仓库原路径加载依赖、模型和冻结输入。实验日志在 `docs/`，历次运行在 `outputs/`，论文与汇报在 `paper/`。这次从仓库根目录移出的旧汇报、诊断稿、临时脚本和补丁日志保存在本机 `workspace_auxiliary/`。

## 项目范围

这是 `LLM4BPC` 唯一的活动实验目录。项目完整目标是重建并改进 Sun 方法的
三个组成部分：Part 1 解析 BPMN 并生成 Process Record；Part 2 从合规需求生成
Rule Record；Part 3 使用两种记录完成匹配与违规检查。Part 1 与 Part 2 是独立
并行的上游部分，编号不表示先后执行顺序。具体实施优先级见主 Pipeline。

当前展示名称统一使用 Part 1/2/3。既有 `stage*` 路径、模块、CLI、schema、
合同键和 S1/S2/S3 任务 ID 作为兼容标识保留；冻结结果、manifest、日志与原始
附件保留来源字节。统一名称和依赖映射见 `configs/paper_method_display_names_v1.json`。

## 方法展示名称

项目文档与 GitHub 仓库中的基线统一称 **Sun et al. (2024)**，简称 **Sun**；
首次出现注明是依据公开方法进行的**本地独立重建**。当前 Part 2 比较为
**Sun / LLM-SE**。Sun 包含 BERT-TextCNN 情态分类器、句法分析与人工抽取规则。

| 当前展示名 | 历史展示名 | 兼容 ID |
|---|---|---|
| Sun（本地重建） | Rules-Only / Sun-style Rules-Only | `sun_rule_only` / B0 |
| LLM-SE | Direct-LLM / LLM-RE | `direct_llm` / D1 |

统一映射见 [方法展示名称配置](configs/paper_method_display_names_v1.json)。
冻结注册表 `configs/methods.json`、冻结运行源码、已存报告、预测、
manifest 与历史日志保留来源名称和字节；引用时使用上述映射，不改指标或运行绑定。
Sun 的实验分数来自本项目重建，不能归为原作者代码的结果或原论文报告值。

## 项目名称与路径

项目名称为 `LLM4BPC`，当前工作区为 `D:\Paper\experiment\LLM4BPC`，Git 远端为
`https://github.com/chaos-66/LLM4BPC.git`。发行包名称为 `llm4bpc-formal`。
从仓库根目录执行下方命令；程序使用源码位置推导路径，不依赖工作区文件夹名称。

Python 导入名 `bpc_hybrid`、已有 `BPC_HYBRID_*` 环境变量和冻结 schema 的 `$id`
保持兼容。历史日志、授权原文、manifest、实验产物及既有文件名保留当时的标识，
不因项目改名重写证据或重新运行实验。Git worktree 的检查与修复见
`docs/DIRECTORY_GUIDE.md` 的“工作区改名与 Git worktree”。

## 唯一入口

Agent 和人类都按以下顺序进入：

1. `docs/MASTER_PIPELINE.md`：唯一完整路线、任务树、依赖和完成定义；
2. `docs/PROJECT_AUDIT.md`：唯一实时状态与当前任务；
3. `docs/AGENT_RUNBOOK.md`：按任务依赖派工规则和可复制 Prompt；
4. `docs/DIRECTORY_GUIDE.md`：每个目录的职责和文件去向；
5. `docs/EXPERIMENT_LOG.md`：中文实验日志和最新已验证变更；
6. `AGENTS.md`：强制操作边界；
7. `docs/AI_CHANGE_PROTOCOL.md`：实验日志、自动检查和记录协议；
8. `paper/README.md`：外部 ChatGPT 通过 GitHub 协作写作的固定入口；
9. `paper/THESIS_DRAFT.md`：已启动的论文工作稿；
10. `docs/INDEX.md`：其余文档地图；
11. `docs/FILE_CATALOG.md`：自动生成的逐文件目录。

不要新建平行 pipeline、日期版 status 或 handoff。实验中出现新证据时，原位更新
主 Pipeline 的版本号、任务状态、依赖、完成定义和 changelog。

外部 ChatGPT 不会自动看到本地未推送的改动。每次 GitHub checkpoint 更新后，让
它从 `paper/README.md` 重新读取权威文件并报告实际 commit/状态日期/最新事件；聊天
记忆不能替代仓库事实。

## 当前事实

- EStG-150 人工审核输入门已就绪，但仍是 0/150 adjudicated；
- 现有 `sun_rule_only` 是 development heuristic，不是完整 Sun baseline；
- S2.3 `public_marker_lexicon_en_v1` 已离线 verified，但仍是 development-only，
  未激活 extractor、训练或评价；
- B0、H1、正式 D1、Part 1 和 Part 3 均未完成；
- 未经用户明确授权，不运行真实 LLM/API；
- 没有 formal Gold，也没有可用于最终论文结论的正式结果。

最新状态以自动完整性检查为准（脚本保留历史兼容名 `audit_project.py`）：

```powershell
python formal_experiment/scripts/audit_project.py
```

上面仅为快速完整性检查，不运行测试。PPT、文字、排版等纯文档工作无需执行。
实验程序修改默认只跑相关测试；`--with-tests` 会运行整个测试集，通常耗时较长，
必须得到用户对本轮全量测试的明确授权。提交、推送和记录日志不会自动触发全量。
具体范围见 `AGENTS.md` 与 `docs/AI_CHANGE_PROTOCOL.md`。

启动已授权的人工审核工具：

```powershell
python formal_experiment/scripts/estg150_review_tool.py
```

## 目录边界

```text
configs/       机器可读合同、方法与 schema
data/          development 与未来冻结的 input/gold/predictions/results
docs/          主路线、实时状态、规范、日志与研究证据
outputs/       报告；正式报告必须可追溯
paper/         论文工作稿与科学主张证据矩阵
prompts/       受版本控制的 prompt 与 fixtures
resources/     词表等静态资源
scripts/       自动检查、日志、构建、验证与运行入口
src/           活动实现
tests/         离线测试与 fixtures
_retired/      已退出活动流程但需追溯的专属只读归档
```

`references/` 和根 `archive/` 是只读 provenance；所有活动修改留在本目录。
`.env` 不得读取或进入日志；`.tmp`、`.pytest_cache`、`__pycache__` 是可再生缓存。
