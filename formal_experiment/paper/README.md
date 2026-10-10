# 论文写作区

这里保存论文工作稿，不保存实验结果源文件。事实和任务状态仍以
`../docs/MASTER_PIPELINE.md`、`../docs/PROJECT_AUDIT.md` 和机器合同为准。

## 方法命名（2026-10-10）

活动论文文档中的原 Direct-LLM 统一改称 **LLM-based Semantic Extraction（LLM-SE，
基于大语言模型的合规语义抽取）**；正文与表格使用 LLM-SE，英文题名使用 LLM-Based。
原来的 Direct 用于区分独立 LLM 抽取与规则先行的 LLM 修复；后者已退出后续
实验，因此不再需要用该前缀区分。此前暂用的 LLM-RE / LLM-based Rule Extraction
调整为 LLM-SE，以准确描述 Stage 2 的六类语义要素抽取任务。它与原方法相同，
不把名称调整当作新方法或新的贡献。

### 统一术语与阶段边界

| 层次 | 统一表述 | 在本文中的含义 |
|---|---|---|
| 输入 | Natural-language Compliance Requirements（自然语言合规需求） | 法律、监管、制度或业务规则中的规范性文本 |
| Stage 1 任务/输出 | Process Model Parsing and Label Semantic Extraction / Process Record | 解析 BPMN 结构，并提取活动标签等流程语义 |
| Stage 2 任务 | Regulatory Semantic Extraction（合规语义抽取） | 识别 modality、actor、action、condition、constraint、exception 六类语义要素及原文证据 |
| Stage 2 输出 | Rule Record（结构化规则记录） | 将抽取要素与关系组织成下游可消费的记录；不等同于可执行的逻辑规范 |
| Stage 2 方法 | Rules-Only / LLM-SE | 前者继承 Sun 的情态分类与句法模板抽取，后者用 LLM 生成同一语义表示；rule-based 指抽取机制 |
| Stage 3 任务/输出 | Rule–Process Matching and Violation Checking / Violation Report | 对照规则记录与流程记录，进行匹配和违规判断 |

Semantic Extraction 与 Rule Extraction 都可用于相关研究，但本文选前者作为
Stage 2 的统一任务名称，不把两者交替当作同一模块的标题。Sun 的语义信息抽取
表述及本地作者稿的细粒度定义见主稿 §3.2。modality 已计入六要素，避免写成
“modality 与六要素”；概念上的六要素与正式主表五个 span 字段的评价口径分开。

代码 ID `direct_llm`、旧代号 D1、配置中的兼容标签及历史报告、预测、manifest
保留原样；历史来源中的 Direct-LLM、此前暂用的 LLM-RE 与论文中的 LLM-SE 指同一
方法。各项结果继续绑定其原模型、prompt 和运行版本；本次只统一活动论文文档
的展示名称和术语定义，不改变实验设计、评价口径或任何数值。日期固定的旧汇报
和历史产物继续保留原名，引用它们时使用此映射。

## 第二阶段主表最终采用值（2026-09-26 用户决定）

论文 Table 1 固定采用既有
[`stage2_table1_paper_final_v1.json`](../outputs/reports/stage2_table1_paper_final_v1.json)：
**LLM-SE Overall F1 = 0.8378；Sun 方法本地重建 Rules-Only = 0.7631；
绝对差 +7.47 个百分点**。数据为同一 EStG-150、同一 Gold、粗粒度句子视图；
Overall 仅汇总 actor/action/condition/constraint/exception 五个 span 字段，
modality 四类 label 指标单列。五字段 mean F1 0.8088/0.7970 保留为次口径。

这次固定不产生新实验结果：原始精确值、预测、Gold 和 manifest 保持原样。
正文统一保留四位小数（两位四舍五入为 0.84/0.76，不写截断的 0.83/0.76）。
Sun 行明确标为本地重建，不能写成 Sun 原论文的报告值；结果只绑定原 v6/R3
Direct 快照与正式 B0 臂。后续候选、消融或新模型结果不替换此主表，不再为本表
重跑、调参或改口径。来源绑定及允许的描述性结论见
[`CLAIM_EVIDENCE_MATRIX.md`](CLAIM_EVIDENCE_MATRIX.md) C54。

## CSCWD 2027 投稿准备（2026-09-17）

用户明确以 CSCWD 为目标，希望把已做工作讲清楚，避免因文献重叠焦虑而不断增加新模块。
本轮提供的当届通知为：2026-10-31 截稿、2027-01-31 通知结果、2027-05-26 至 28
Brisbane 会议；EasyChair 公开登录页已核实当届新稿入口开放。具体时区、篇幅、模板与
匿名规则仍待当届正文核验，不把往届六页要求自动当成 2027 硬要求。

[CSCWD_POSITIONING.md](CSCWD_POSITIONING.md) 保存文献重叠对照、来源核验深度、
现有证据的使用边界、贡献候选和暂定六页组织方式。本文及该笔记均不替代主 Pipeline
和实时状态，不登记另一套任务进度，不授权新实验。保留 2026-09-30 导师初稿目标，
沿用当前分阶段比较题名；用实证发现支撑增量，不能把“讲清楚”解释为“不需要贡献”。

## 用户确认的写作目标（2026-09-15）

> “需要把这些事情给说明清楚，记录下来。目标是写清楚自己的贡献，把自己做的事情都要写清楚，把一些数据都要放在论文里。”

当前目标是通过完成第一篇论文，学会把一项应用研究讲清楚、做完整。优先把已做的
方法、实现、数据准备、比较实验与案例整理成完整初稿；创新表述聚焦已有工作的具体
增量，不以持续增加模块、模型、数据集或验证规模作为开始写作的条件。

### 工作与贡献怎样写

- 每项实质研究工作都交代：解决什么问题、前人怎样做、本文沿用了什么、自己设计或
  实现了什么、输入输出是什么、用什么数据观察效果、还有什么限制。
- 方法章节展开实际设计；引言中的贡献可归纳为方法适配与实现、数据与比较评价、
  实验观察与应用边界几个方面。具体贡献句以已完成工作和对应证据为依据。
- 每个后处理步骤都按“实际错误或格式要求—原因与影响—选择的处理及理由—已有
  证据—适用版本与未解决错误”说明。区分试运行观察、后续回顾性错误归因与预先
  设置的结构检查，不把所有步骤虚构成错误分析后的改进；动机对照见正文 §4.2.2。
- 六要素定义、提示词设计、原文证据定位、输出处理、阶段衔接都值得说明。采用已有
  技术时注明来源；不把每个工程步骤都宣称为独立创新或已经验证有效的模块。
- 论文充分呈现相关数据，不只保留一个总分。数据构成、分字段结果、错误分布、
  参数与案例都可帮助解释工作；与结论有关的失败和负结果也要报告。
- 图表可以承担定义、说明设计、交代设置、展示结果或解释案例的作用。学习 Sun 的
  组织方式，不要求逐表复制或重跑其全部模型对照；表格数量由内容和篇幅决定。

### 工作、贡献与图表清单

下表是 PW1–PW9 的写作覆盖清单与证据导航，不是新的实验完成状态表。章节对应
现有 [THESIS_DRAFT.md](THESIS_DRAFT.md)；结果是否可用以
[CLAIM_EVIDENCE_MATRIX.md](CLAIM_EVIDENCE_MATRIX.md) 的对应证据及实时状态为准。
表名为候选内容，可合并或改为图，不设固定表格配额。

| 已有工作或待补内容 | 应写清楚的事项 | 对应章节 | 候选图表或数据 | 现有依据与回填要求 |
|---|---|---|---|---|
| 总体框架与前人方法关系 | Sun/Winter/Barrientos 各提供什么；本文沿用、替换和适配的部分 | §1.2、§2、§3、§4.6 | 三阶段流程图；本文与前人的方法对应表 | 主张矩阵 C01–C04、C44；前人方法事实回到原论文，本文完成状态单独核对 |
| 六要素与结构化表示 | 字段定义、易混淆边界、原文证据、actor-action 关系与阶段输入输出 | §3.2–§3.4、§4.2 | 六要素定义与实例表；一条规则的完整结构化实例 | 现有方法正文与运行所用 schema；示意例标明用途，不充当实验结果 |
| Stage 1 流程解析 | BPMN 结构、标签语义如何转换成 Process Record；实现范围与局限 | §3.1、§6.3、§7.1 | 输入输出示例；结构与语义指标表 | §7.1 对应的正式报告与 manifest；结构、语义和案例观察分清 |
| Rules-Only 重建 | 情态分类、规则与标记词抽取、字段处理和相对 Sun 的重建边界 | §4.1、§6.1 | 方法组成、规则示例和实际模型配置表 | 运行所用配置、公开方法来源和重建证据；不因 Sun 有多种 BERT 表就新增全套训练 |
| LLM-SE 设计与实现 | 字段说明、示例、输出要求、原文证据校验、确定性后处理及各自用途 | §4.2、§4.4–§4.5 | 提示词组成与用途表；输出处理示例；实际调用配置表 | 已运行版本的 prompt/config/manifest；写明实现，不由模块存在推断有效性 |
| 数据准备与人工裁决 | 来源、样本数量、语言、字段分布、标注流程与不同数据集用途 | §5、§6 | 数据集统计表；Gold 字段分布表；标注流程图 | 冻结数据及发布记录；注明 LLM-assisted, human-adjudicated，不复制受限第三方原文 |
| Stage 2 比较 | 同输入与同口径下的 Rules-Only/LLM-SE 表现；可兼容的前人共同子任务 | §6.1、§6.5、§7.2 | 情态 label 指标表；五字段 span P/R/F1 与样本数表；前人适配子任务另表 | C23、C44、C47 及其来源；正式结果、开发适配结果、前人论文报告值分开 |
| 设计分析与错误诊断 | 已做的消融/设计对照；字段混淆、漏抽、复杂度或阈值变化的影响 | §6.6、§7.3、§8 | 已有消融结果表；错误类型与案例表；适用的参数/复杂度图 | ABLATION_MATRIX 与对应报告；未运行的组合和复杂集结果保留 TODO，不从历史单因素结果拼出新实验 |
| Stage 3 与阶段衔接 | 规则如何匹配流程、如何判断违规、哪些上游错误影响下游 | §3.3、§6.2、§7.4–§7.5 | 匹配结果表；违规分类表；Oracle 与端到端分别成表 | 对应报告和 manifest；DEV_ONLY 面板标明范围，尚缺正式结果的表继续留空 |
| 应用案例与局限 | 一条输入如何得到抽取、匹配与检查结果；成功与失败原因 | §3.5、§8 | SIM 贯穿案例图；原文—输出—检查—解释对照表 | C39、C43 与现有案例来源；展示案例不等于证明总体性能 |
| 运行开销与历史探索 | 在有可靠记录时交代调用数、失败数、耗时与成本；说明影响主线选择的历史观察 | §6、§8 或附录 | 简短开销表；相关历史探索说明 | 仅用实际运行日志/manifest；估算与实测分开，已取消的 Rules+LLM 仅作历史来源 |

### 数据入文与完整初稿的执行方式

1. 先按上述清单盘点并展开已有材料；正文讲清主要设计与结果，完整提示词、长配置、
   逐项明细放附录或可公开的补充材料，并在正文给出位置。完整记录研究工作不等于
   把每条调试日志放进论文。
2. 结果来源在主张矩阵或工作稿注释中对应到报告与 manifest；正文保留读者理解所需的
   数据集、样本数、方法、指标口径和正式/开发范围，不堆放内部日志。表后说明观察
   及适用范围；输入、Gold 或指标口径不兼容时，不拼成一个公平比较表。
3. 先写已经能写清楚的章节，不等待所有实验完成。已有数值经源文件核对后写入；
   计划、估算和未运行结果显式标注，不能为填满表格补造数据。
4. 初稿中出现具体缺口时，再说明缺什么、影响哪一句主张，以及已有数据能否回答；
   必要时缩小主张或安排补充实验。写作清单本身不新增模型训练、真实 API 调用、
   全量测试或其他实验要求，原有实验任务仍按主 Pipeline 推进。
5. 每次写作交付核对：本节工作讲清了吗，自己的改动和借鉴分清了吗，已有相关数据
   有呈现位置了吗，表图在正文有解释吗，未完成事项是否明确。结果回填继续遵循
   下方主张矩阵与来源复核规则，不因这份清单建立而宣称正文或实验已经全部完成。

## 外部 ChatGPT 的 GitHub 入口

当 ChatGPT 通过 GitHub 协助论文写作时，本文件是唯一的论文协作入口，但不是新的
状态页。每次开始写作或收到“本地实验已更新”的消息后，必须重新读取当前 GitHub
分支上的下列文件，不得把历史对话记忆当作项目现状：

1. `formal_experiment/AGENTS.md`：安全边界与必读规则；
2. `formal_experiment/configs/experiment_contract.json`：机器门禁；
3. `formal_experiment/docs/MASTER_PIPELINE.md`：唯一完整路线与任务依赖；
4. `formal_experiment/docs/PROJECT_AUDIT.md`：唯一实时状态页；
5. `formal_experiment/docs/EXPERIMENT_LOG.md`：最新已验证变更；
6. `formal_experiment/paper/CLAIM_EVIDENCE_MATRIX.md`：论文主张的证据与解锁条件；
7. `formal_experiment/paper/THESIS_DRAFT.md`：当前论文工作稿。

开始指导前，ChatGPT 应先向用户报告：实际读取的仓库/分支与 commit SHA（若连接器
可提供）、`PROJECT_AUDIT.md` 的更新时间、`EXPERIMENT_LOG.md` 的最新事件，以及
`human_review_input_ready`、`human_review_freeze_ready`、
`formal_gold_publication_ready`、`final_experiment_ready` 四个门禁。无法访问文件或
无法确认版本时，必须明确说“尚未完成仓库同步”，不能根据旧对话继续推断进度。

发生冲突时，按 `AGENTS.md` → 机器合同 → `MASTER_PIPELINE.md` →
`PROJECT_AUDIT.md` → `CLAIM_EVIDENCE_MATRIX.md` → 论文草稿的顺序取值。只读取
`formal_experiment/` 的活动文件；`_retired/`、根 `references/` 和根 `archive/`
只用于溯源，不得作为当前状态或可直接写入论文的结果。

GitHub 同步是“每次 push 后可刷新”，不是秒级实时共享。本地未提交或未推送的改动
对 ChatGPT 不可见；用户告知有新进度时，ChatGPT 必须重新读取上述文件。

## 推荐协作节奏

1. 先完成上述版本与门禁回报；
2. 从 `MASTER_PIPELINE.md` 的 PW1–PW9 中选择当前已解锁的一个最小写作任务；
3. 一次只教学和处理一个小节，先解释论证目标、证据边界和段落结构；
4. 用户写作后再逐段修改，并把缺失证据保留为标准 TODO；
5. 新增结果性句子前先检查 `CLAIM_EVIDENCE_MATRIX.md`；
6. 没有 `experiment_run` 事件和 formal manifest 时，不得把 development 数字写成
   正式结果，也不得提前撰写性能优劣、摘要结论或最终贡献。

## 文件

- `THESIS_DRAFT.md`：中文论文连续工作稿、章节骨架和结果空表。
- `CLAIM_EVIDENCE_MATRIX.md`：每项科学主张的证据、时态、解锁任务和禁止表述。
- `ABLATION_MATRIX.md`：AB-1–AB-10 受控消融矩阵现状（我的模块 vs 换 Barrientos
  模块 vs 去掉模块；仅有历史证据项可引用，未跑项必须标“待运行/待授权”）。
- （治理文档）`docs/API_AUTHORIZATION_REQUEST.md`：S2.12 复杂语料真实 LLM/API
  精确授权申请（0 调用；获得用户授权前不得运行）。

## 写作规则

1. 一次只有一个 Agent 编辑正文；另一个 Agent 可以只读复核。
2. 内部 `docs/research/` 只作证据导航，正式引用必须回到可核验的原论文。
3. 无法核验页码、表号或数字时保留 `TODO-SOURCE`，禁止猜测。
4. 没有正式 manifest 的结果不得写入论文；development 数字只能标 `DEV_ONLY`。
5. Stage 2 与 Stage 3 分表，Oracle 与 end-to-end 分表，C1–C4 证据等级不得混写。
6. Gold 只能称 `LLM-assisted, human-adjudicated Gold`；Sun 方法只能称
   `paper-faithful independent reconstruction`。

## 占位符

- `[[TODO-RESULT:任务ID：说明]]`
- `[[TODO-SOURCE:文献键：说明]]`
- `[[TODO-STATUS:任务ID：说明]]`
- `[[TODO-DECISION:任务ID：说明]]`

结果回填时必须同时更新正文和 `CLAIM_EVIDENCE_MATRIX.md`，并由只读 Agent 对照
对应 `experiment_run` 与 manifest 复核。
