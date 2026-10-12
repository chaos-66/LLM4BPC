# CSCWD 2027 完整文字阅读包

目标：带作者逐节完成论文修改，而不是第一轮直接生成整篇。
本文件把版本说明、全文审阅、英文替换稿、18 篇 BibTeX 和原稿辅助文字集中起来，避免网页版模型只读到一个摘要就开始猜测。

## A. 先理解材料身份

- 原稿为作者上传的六页 2027_CSCWD (16).pdf；[原样 PDF](source_2027_CSCWD_16.pdf) 是公式、图表和版式的依据。
- 现有审阅和替换稿基准提交为 1f00f155474329a0f73eb5c162688301d5e5414d；它们是候选修改，不是作者已接受的终稿。
- 本文件末尾包含原稿分栏文本。它保留原文错误；下标、公式、表格可能提取失真，必须对照 PDF。
- 2026-10-12 起，活动修订统一使用 Part 1 / Part 2 / Part 3；Part 1 和 Part 2 独立并行，共同输入 Part 3。原稿附录保留原文，后续整合修订时同步更新原稿图中的名称与关系。
- 两篇已发表 CSCWD 论文只借鉴结构，不能借用不相关研究内容或凑引用。
- 仓库旧 TeX 已与上传 PDF 部分不同，不能冒充当前准确源文件。
- 先报告实际读取范围。无法打开链接或 PDF 时，请作者提供本文件和原稿，不要声称已经读取。

## B. 修改中不可丢失的事实

- 方法展示名 LLM-SE；历史 Direct-LLM / LLM-RE 和兼容 ID 不改写实验身份。
- 原 II Related Work 并入 I Introduction，目标为五节结构。
- 正文实际引用 18 篇；引用服务于具体论述，不能用 nocite 凑数。
- Table I 固定 0.8378 vs 0.7631，+7.47 pp，五字段 pooled overlap F1；modality 单列。分别统计命中预测和命中参考区域。
- Table I v6/R3 与 Table II modular_v1 的 111 不是相同提示词快照，不能把 0.8224 当成主表配置的重复。
- 主表历史后处理采用唯一精确定位，不是后来 repair_v1 的重复片段分配；定位正确不保证语义正确。
- 基线正式称 Sun et al. (2024)，简称 Sun，首次说明为本地独立重建；历史名称 Rules-Only 仅保留在来源。基线包含 BERT-TextCNN 模态分类器，分数来自本项目运行。
- 原稿 Table III 的 0.5341 vs 0.4458 是 GDPR 开发比较；同一 benchmark 参与开发/校准，不是独立未见测试。
- 后续 Winter 对照单独存在；到实验一节再和作者明确是否纳入，不能默默替换原稿。
- 本轮为写作：不授权 API、实验重跑、Gold 修改或调参。缺证据的内容标待核实，不编造。

## C. 每轮如何推进

按 标题与摘要 → 合并引言 → 问题定义与框架 → Part 1 → Part 2 → Part 3 → 实验/局限 → 结论 → 全文回查 推进。每次一个可完成的小节。
每轮给出：修改位置；中文问题解释；中文逻辑；可替换英文/LaTeX；删/换/留的具体操作；证据与待核实点；2—3 个验收点。等待作者反馈后继续。
第一轮确认阅读范围与研究理解，列最重要的 5 个问题；材料足够就开始标题与摘要。完整交互要求见 [WEB_GPT_PROMPT.md](WEB_GPT_PROMPT.md)。

## D. 固定版本的证据入口

以下链接固定到已有提交，避免读取用户工作区中尚未提交的改动。它们用于核对事实，不会自动把历史任务或实验授权变成本轮命令。

- [写作术语与阶段边界](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/paper/README.md)
- [主张与证据（重点 C54/C55/C56）](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/paper/CLAIM_EVIDENCE_MATRIX.md)
- [长稿方法解释（重点 4.2.2）](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/paper/THESIS_DRAFT.md)
- [Table I 冻结数值与命中计数](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/outputs/reports/stage2_table1_paper_final_v1.json)
- [主表 LLM-SE 来源 manifest](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/outputs/reports/direct_llm_formal_arm_v1.manifest.json)
- [主表基线来源 manifest](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/outputs/reports/b0_formal_arm_v1.manifest.json)
- [主表来源配置快照](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/data/results/direct_llm_formal_arm_v1/config_snapshot.json)
- [modular_111 提示词身份](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/outputs/evidence/sep_c3_modular_ablation_v1/arms/111/manifest.json)
- [增量消融批次和模型登记](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/outputs/evidence/sep_c3_modular_ablation_v2/manifest.json)
- [结构适配实现](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/src/bpc_hybrid/d1_schema_adapter.py)
- [坐标定位当前实现（注意 legacy / repair_v1）](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/src/bpc_hybrid/d1_span_canonicalizer.py)
- [最终校验实现](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/src/bpc_hybrid/stage2_canonical.py)
- [执行顺序参考（当前代码不自动等于历史运行）](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/scripts/run_direct_llm.py)
- [后处理开发消融](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/outputs/reports/d_full_postprocessing_ablation_v2.md)
- [后续 Winter 开发比较（不得自动替换原稿范围）](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/outputs/reports/stage3_winter_paper_rerun_20261010_v1.md)
- [已有公式修正文档（不等于上传 PDF 源）](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/paper/cscwd2027/FORMULA_CORRECTION_NOTES.md)
- [旧 TeX，仅供参考](https://github.com/chaos-66/LLM4BPC/blob/1f00f155474329a0f73eb5c162688301d5e5414d/formal_experiment/paper/cscwd2027/2027_CSCWD_formula_corrected.tex)

如果来源彼此冲突，指出具体文件与冲突，并根据运行绑定追溯；不要自行选较高分数或把代码当前默认值追溯到旧运行。

## E. 逐页审阅与引用位置

来源文件：[REVIEW_AND_USE.md](REVIEW_AND_USE.md)。以下完整嵌入，未把建议自动套用到原稿。

<!-- BEGIN_SOURCE REVIEW_AND_USE.md -->
````markdown
# 2027_CSCWD (16) 全文审阅与可替换修订稿

审阅日期：2026-10-11。对象是用户上传的六页 PDF，不是把仓库中的旧 TeX 当成同一版。以下页码均为 PDF 页码。两篇学长学姐论文只提供结构参照，不作为本文研究内容或参考文献的来源。

## 1. 直接判断

目前是“研究路线能读懂，但方法和实验还没有完全解释闭合”的版本。

- 可以理解：法规文本和 BPMN 分别处理，LLM 抽取六类语义，统一为 Rule Record，再检查三类违规；实验分为抽取比较、提示词组合和下游检查。
- 尚未充分理解：后处理的执行顺序、定位算法和失败处理；六类语义如何参与三类检查；若干公式符号；主表与消融的版本关系；抽取指标的实际计数方式。
- 需要直接纠正：坐标重定位与“坐标不变”的矛盾、actors/order 的符号冲突、公式未出现的 minimum-form 说明、把两个不同提示词版本仅解释为不同运行，以及用共同 TP/FP/FN 描述实际采用双向命中计数的抽取指标。
- 18 篇可以合理安排。本目录已经给出合并引言中的 16 篇实际引用，以及相似度模型处的 2 篇实际引用；不是仅向 bib 添加 10 条。

本次提供的是可替换文字和审阅材料，没有声称已经修改并重新编译上传的 PDF。仓库旧源文件Part 3 的文字已与上传 PDF 不同；当前环境也没有可用的 TeX 编译器，因此不能把片段检查冒充最终六页排版验收。

## 2. 两篇已发表论文应当借鉴什么

| 结构特征 | 2025 论文 | 2026 论文 | 对你的论文的用法 |
|---|---|---|---|
| 引言 | 背景、既有方法、具体不足、本文方案、贡献、章节安排 | 按方法演进组织既有工作，导出具体缺口，再给方案和贡献 | 把 Related Work 的实质论述融合进引言，删去重复介绍 Winter/Sun 和 LLM 的段落 |
| 方法前的准备 | II Motivation and Framework，用例子说明问题和框架 | II Preliminary 后接 III Framework，先定义后解释模块 | II Problem Formulation and Framework，补最必要的字段定义和一个贯穿例子 |
| 核心方法 | 对目标问题定义、建模、说明求解过程 | 对框架中的主要模块逐项说明 | 给你实际改变的 Part 2 足够篇幅，写出后处理规则或伪代码 |
| 实验 | 实验设置、比较结果、结果分析 | 设置、性能比较、消融和参数分析 | 保持抽取比较、提示词分析、下游比较，但把数据和版本说清楚 |
| 结论 | 回到问题与观察，再写未来工作 | 回到主要模块与实验观察，再写未来工作 | 总结已经得到的观察，并保留弱项与开发集限制 |

不能从他们的文章借来你的研究动机、算法名称、结果解释或无关引用。也不必照搬他们的章节数量。

建议最终五部分：

1. Introduction：背景 → 传统形式化方法 → 文本语义抽取 → LLM 相关工作 → 本文具体问题 → 方法概述与贡献。
2. Problem Formulation and Framework：输入输出、六类字段的简明定义、三部分关系。
3. Methodology：A Process Model Parsing；B Compliance Requirement Parsing；C Compliance Checking。
4. Experiments and Results：设置、抽取比较、提示词组合、下游检查、局限。
5. Conclusion。

合并不是删除标题后直接拼接。现有 I/II 的文献叙述高度重复，应该按上述逻辑重写。完整英文替换内容见 introduction.tex；后续章节的 label 可以保留，由 LaTeX 自动重新编号。正文硬编码的“Section V-D”等引用也须随之更新，优先改为 \ref。

## 3. 18 篇文献分别支撑哪一句话

下面序号按新引言首次出现顺序排列，最终编号由引用样式生成。原有 8 篇保留，新增 10 篇。没有加入两篇学长学姐的论文。

| 顺序 | 文献 / BibTeX key | 对应论述与位置 | 来源 |
|---|---|---|---|
| 1 | Hashmi 2018 / hashmi2018we | 引言第 1 段：BPC 的任务和研究背景 | https://doi.org/10.1007/s10115-017-1142-1 |
| 2 | Zasada 2023 / zasada2023evaluation | 引言第 1 段：合规规则表示语言 | https://doi.org/10.3390/software2010004 |
| 3 | Awad 2008 / awad2008efficient【新增】 | 引言第 2 段：BPMN-Q 与时序逻辑检查这一具体路线 | https://doi.org/10.1007/978-3-540-85758-7_24 |
| 4 | Elgammal 2016 / elgammal2016formalizing【新增】 | 同段：基于模式的合规语言，不声称本文采用其算法 | https://doi.org/10.1007/s10270-014-0395-3 |
| 5 | Governatori 2016 / governatori2016semantic【新增】 | 同段：LegalRuleML 形式化法规与检查 | https://doi.org/10.1007/978-3-319-49004-5_48 |
| 6 | Sleimi 2018 / sleimi2018automated【新增】 | 同段：从法律文本抽取语义元数据；不说其字段与本文完全一致 | https://orbilu.uni.lu/handle/10993/36228 |
| 7 | Michel 2022 / michel2022identification【新增】 | 同段：识别法规中的决策规则；不把其数据等同于本文六字段 Gold | https://hdl.handle.net/10125/80097 |
| 8 | Winter 2020 / winter2020assessing | 同段：直接面向监管文档和流程模型的合规评估 | https://doi.org/10.1007/978-3-030-62522-1_14 |
| 9 | Sun 2024 / sun2024design | 同段及方法：六类语义表示和既有检查框架的来源 | https://doi.org/10.1007/s11227-023-05626-0 |
| 10 | de Kinderen 2024 / de2024towards | 引言第 3 段：提示词模板用于法律 GRL 建模 | https://doi.org/10.1007/978-3-031-61007-3_17 |
| 11 | Barrientos 2026 / barrientos2026impact | 同段：法规变更的合规影响分析 | https://doi.org/10.1016/j.infsof.2026.108079 |
| 12 | Barrientos 2026 / barrientos2026taming | 同段：法律变更处理，不能把本文全部后处理归给它 | https://doi.org/10.1007/s12599-026-01008-x |
| 13 | Guliani 2026 / guliani2026dejure | 同段：迭代自修正的结构化法规抽取；明确是预印本 | https://arxiv.org/abs/2604.02276 |
| 14 | Wang 2025 / wang2025leveraging【新增】 | 同段：LLM 生成流程三元组，用于合规风险识别；必须讨论的相近工作之一 | https://doi.org/10.1007/978-981-96-6963-9_32 |
| 15 | Park 2026 / park2026extracting【新增】 | 同段：自然语言到 Declare 约束；区别在目标表示和任务 | https://doi.org/10.1016/j.dss.2026.114627 |
| 16 | Kölbel 2026 / koelbel2026context【新增】 | 同段：BPMN 与外部安全知识结合的解释和合规评估 | https://doi.org/10.1007/s10207-026-01245-x |
| 17 | Reimers 2019 / reimers2019sentence【新增】 | Part 3 相似度模型说明：Sentence-BERT 句向量框架 | https://aclanthology.org/D19-1410/ |
| 18 | Song 2020 / song2020mpnet【新增】 | 同处：实际 all-mpnet-base-v2 的基础架构；精确 checkpoint 另给模型卡脚注 | https://proceedings.neurips.cc/paper/2020/hash/c3a690be93aa602ee2dc0ccab5b7b67e-Abstract.html |

筛选依据是“本文这句话需要什么证据”，而不是“Sun 引用了谁”。通过 Sun 的参考文献找到原始文献完全可以；直接引用之前仍须核实原始来源中相应的内容。只看过 Sun 的总结时，不应把它写成自己核验过原文的具体实验结论。

核验深度与边界：

- 条目信息和替换句所需的研究目标、方法概述，依据出版社页面、作者公开稿、机构库、ACL/NeurIPS 官方页面或 arXiv 原始记录核对。
- 对部分付费论文，本次可获取的内容仅为原始出版页面的摘要/方法概述，例如 Awad、Elgammal、Wang；因此替换稿只概述明确写出的任务与方法，不比较未读取的具体结果、限制或实验设置。
- Michel 的机构库条目支持其研究任务与文献信息；这里没有把其法规数据来源、标注或分类结果移植成本文的事实。
- Sun 最终版的出版社信息与项目已有作者稿材料需要区分，不能声称本次已经逐页核验最终版所有公式与超参数。
- Kölbel 的出版页面有 2026-09-07 更正链接；此处仅使用已更新原文的总体任务描述，不据此引述具体性能。
- 上述概述支持本文的定位，不能支持“首次使用 LLM 进行 BPC”或“其他方法均没有证据校验”等排他性结论。
- Barrientos 的 Taming 一文已更新为 68(5):1147–1172，并补 DOI；不再保留旧的 1–26。
- Elgammal 的标题在出版社登记为 “appling”，bib 按该标题保留。
- Wang 是 ICONIP 2024 会议论文集中的 2025 年出版章节；bib 年份用 2025。
- De Jure 按 arXiv 预印本登记，不冒充已经发表的期刊文章。

## 4. Part 2 后处理：现在缺什么，应该怎么写

PDF 第 2 页右栏到第 3 页开头只有一段概述。已有的校验项目是对的，但未说明执行过程，因此还不能回答“算法到底做了什么”。

### 4.1 必须修正的两句话

“重定位错误 span”意味着 start/end 会改变，后一句却写 source offsets remain unchanged。应改为：

> The source and evidence strings remain unchanged, while erroneous coordinates may be corrected.

另一个问题是 normalized。不能笼统写成原值全部保留。当前结构适配器对五个字段片段实际执行 casefold 和空白折叠，重新生成 normalized；坐标模块才只改坐标、不改 text/normalized。

### 4.2 按实际实现解释处理链

| 环节 | 实际操作 | 失败处理 |
|---|---|---|
| JSON 解析 / 结构适配 | 解析对象、展开嵌套 span、可用数字字符串转整数、补确定性 ID、生成 normalized | 无法映射的字段元素局部删除；顶层或关键记录结构错误拒收 |
| 先定位子句 | 对子句证据核验原坐标；必要时在完整抽取输入中找唯一完全相同文本 | 无法定位的子句删除，不能把它写成任意坏结构子句均局部保留 |
| 再定位字段和模态证据 | 原坐标正确则保留；否则在所属子句范围搜索原文精确出现位置 | 唯一则改坐标，零处或多处则 unresolved 并删除片段 |
| 清理关系 | 删除引用已删除 actor/action 的关联及顺序关系 | 不猜造新端点；接口允许的空 actor 端点按既有合同处理 |
| 最终校验 | 字段/类型、模态枚举、原文一致、子句包含、ID 唯一、关系引用合法 | 仍有不合法结构时整条记录拒收；缺失预测不应从实验分母消失 |

算法的准确名称可以是“基于原文唯一精确匹配的证据定位”，实质是确定性字符串查找与规则检查。它不是语义相似度修复，不调用新的 LLM，也不以 Gold 找答案。

要把“校验”分清楚：

1. 程序结构校验：输出能否正确接入后续模块。
2. 证据定位校验：text 是否确实出现在给定坐标。
3. 实验质量评价：对照参考标注计算 P/R/F1。

前两种通过不代表第三种正确。例如 clerk 可以被准确定位，但抽为 constraint 仍是语义错误。

### 4.3 需要保留的实现细节

- 零起点、左闭右开，按 Unicode 字符串位置计数，不按 token 或 UTF-8 字节数。
- 原坐标已经正确时，即使相同文本出现多次也保留；“多次出现就删除”只适用于需要重新定位且无法唯一定位的情况。
- 原坐标一致性检查先在完整输入上做，子句包含性在最终校验做。不能声称定位步骤已经删除全部子句外片段。
- ordering-relation evidence 由最终校验检查，不能声称当前坐标模块给所有证据类型都做重定位。
- 若未固定安装并启用完整 jsonschema 后端，不能把轻量结构检查写成完整 JSON Schema 验证。最终投稿需写明实际运行环境。

### 4.4 后来新增的重复文本定位不属于主表算法

当前代码还有 repair_v1：同一子句、字段和相同文本分组，以模型原始起止坐标距离为代价，求一对一最小代价分配，只保留在所有最优解中位置都相同的候选。

实际实现使用有上限的穷举，不是匈牙利算法。它是后续开发版本；不能为了使论文“看起来有算法”，把它加入对主表 0.8378 的解释。已有开发对照恢复部分片段但 actor F1 下降，也不能说每一步均提高语义准确率。

本次 part2_postprocessing.tex 给出历史唯一精确定位的可替换文字、定义、伪代码和一个合成例子。无需新增实验即可把当前主方法解释清楚。

## 5. 从头到尾的审阅

| 位置 | 清楚程度 / 具体问题 | 修改建议 |
|---|---|---|
| 第 1 页标题、摘要 | 主题清楚；摘要主要说明“要做什么”，没有核心观察 | 补样本量、主表结果及限制，勿把三部分框架本身作为新发明 |
| 第 1–2 页 Introduction / Related Work | 重复，最相近的 LLM 流程合规工作覆盖不够 | 使用合并引言；按任务和表示区别定位，不声称“别人没有做” |
| 第 2 页 Problem Formulation | 有输入输出名称，缺字段的操作性定义 | 用一个紧凑表区分 modality、actor、action、condition、constraint、exception，尤其 condition 与 constraint |
| 第 2 页 Framework | 三部分关系明确；六字段输出与三类检查之间的关系不够明确 | 说明哪些字段直接进入当前检查，哪些仅保留在记录中；抽取了六类并不代表验证了六类违规 |
| 第 2 页 Part 1 | “fixed linguistic analysis”过于概括 | 补 BPMN 标签如何取得动作、对象、参与者；可达性如何计算以及网关、循环、缺失标签如何处理。应按实际冻结实现填写 |
| 第 2–3 页 Part 2 | 提示词模块较清楚，后处理不足且有矛盾 | 采用本目录替换段；明确 raw output、adaptation、alignment、validation 的区别 |
| 第 3–4 页 Part 3 | 符号与说明没有同步，影响读者判断实际算法 | 见下一节逐项纠正；不要仅复制 Sun 公式后省略所有定义 |
| 第 4–5 页实验设置 | 数据量和任务已给出，Gold 来源与版本身份还不充分 | 补重建和人工裁定流程、输入语言/翻译情况、重复与失败处理、每组配置 |
| 第 5 页 Table I | 对优势和弱项的讨论诚实；指标说明与冻结统计不一致 | 改为双向命中计数的 pooled overlap F1，modality 单列；统一四位小数 |
| 第 5 页 Table II | 8 个组合和基础契约说明较好 | 清楚说明与 Table I 的提示词版本不同、跨两批执行且每格一次；交互只是观察，不能暗示统计稳定性 |
| 第 5 页 Table III | 已说明开发集和阈值校准；这是应保留的限制 | 解释 115 cases 如何形成 201 个适用单元，以及预配对评估与全量规则检索是否不同 |
| 第 5–6 页错误分析 | 已限制到 missing-action 的 FP，边界较好 | 补分类依据与至少一个例子；50/70 是方法–案例单元，不是 50 个独立案例 |
| 第 6 页结论、引用 | 结论与主要观察大体一致；仍使用旧名称与三位小数 | 统一 LLM-SE、0.8378/0.7631；18 篇与正文逐一对应 |

### 5.1 Part 3 中必须修正的符号问题

1. 第 3 页开头将 U_r 定义为 actors，公式 (8) 却用 U_r 表示顺序约束；公式 (4) 用到的 P_r 没有同处定义。应统一为 A_r=动作、P_r=主体、U_r=顺序关系。
2. 文字使用过程 p，公式使用 m；D、O、R、C、U、S 的下标也混用。全节选择同一套符号。
3. 公式 (1) 是 m_O，后面的空集说明却写 m_U。
4. 实验 θ 与公式 ϑ 应统一或明确说明对应关系。
5. f_r、f_m、F_m、A_m、E_m、R_m、bs_obj 必须说明输入输出与意义。仅写“沿用 Sun 的定义”不能让本文自足。
6. 公式 (1) 分子要说明是在统计满足阈值的配对数量。若保留 Sun 原式，至少用文字明确计数含义；规范写法可用指示函数，但不得顺便改变判定逻辑。
7. Missing-action 文字引入最大相似度函数 s，公式却仍通过 D 和 B 表示；“没有候选也计为 missing”的空集政策没有从公式中体现。应单列实现边界和空集处理，解释它与原始公式的关系。
8. 第 3 页末至第 4 页开头仍写“this minimum test”“minimum form”，但实际展示的是存在量词公式。应删除过时说明或给出实际采用的等价式，不要擅自把存在低相似度候选改成所有候选均不相似。
9. 顺序检查使用单向可达、反向不可达，应说明这是本文采用的静态结构准则。它不自动等价于包含网关、循环的全部执行轨迹满足时序规范。
10. 需要说明违规分数何时转成违规判定、规则选择阈值如何作用，以及空集合返回 unknown 而不是 compliant 的政策。阈值恰好相等时采用 >、>= 还是 < 也应与实现一致。

仓库中的 2027_CSCWD_formula_corrected.tex 已修正其中部分文字，所以“上传 PDF 存在的问题”与“旧 TeX 当前状态”不能混为一谈。本审阅没有覆盖旧文件或自行改变冻结检查器。

### 5.2 实验描述中的实质问题

**抽取指标不是普通的一对一 TP 计数。**

冻结主表为双向命中统计。LLM-SE 的匹配预测数为 513/590，匹配 Gold 数为 371/459，分别形成 precision=0.86949、recall=0.80828，F1=0.8377685。这两个匹配数不相同，不能把它们写成同一个 TP 再套用 TP/(TP+FP)、TP/(TP+FN)。应在正文写实际 pooled precision/recall，再由二者计算 F1。method_and_evaluation_notes.tex 提供替换文字。此处只纠正说明，不修改指标或数值。

**表 I 与表 II 不只是随机输出不同。**

主表固定在 v6/R3，提示词 SHA 开头 3aa64877；表 II 的 111 属于 modular_v1，生成提示词 SHA 开头 38144b75。不能解释成“同一个 full prompt 的另一次运行”，也不能用表 II 的最佳 100 替换主表。主表登记的模型 ID 是 deepseek-v4-pro；后续消融 manifest 有 documented_release=DeepSeek-V4-Pro-0813。当前证据不支持把这个后续 release 名称追溯写给全部历史主表运行。

**基线命名：Sun（2026-10-12 已确认）。**

项目重建基线包含 BERT-TextCNN 模态分类器。只写“句法分析和人工规则”不完整。活动稿统一称 Sun et al. (2024)，简称 Sun，首次说明是本地独立重建。它是非 LLM 基线，包含学习型分类组件；结果来自本项目运行，不能归为原作者代码或原论文分数。原稿附录中的旧称 Rules-Only 作为来源保留。

**六字段的抽取实验与下游验证范围不同。**

表 I 说明六类语义的抽取表现，表 III 只评估指定三类检查。需要区分表示能力与已评估能力。对 condition/constraint/exception，应按实际下游使用路径逐项说明，不能让读者自行推断它们都被完整判定。

**GDPR 201 单元的构成要补可追溯说明。**

已有 113 missing-action + 80 incorrect-actor + 8 out-of-order=201 的数目是清楚的。还需说明为什么某个 case 适用某一检查类型、同一 process 是否出现在多个 case 中、正负构造方法，以及给定规则–流程配对是否跳过通用规则检索。没有这些信息，就无法准确理解 Table III 在验证哪个任务。保留“开发与校准使用同一 benchmark”的原有限制。

### 5.3 可用的摘要替换草稿

Design-time business process compliance checking requires regulatory requirements to be connected with process-model semantics. This paper investigates LLM-based Semantic Extraction (LLM-SE) within an existing three-part compliance-checking framework. LLM-SE generates Rule Records containing modality, actor, action, condition, constraint, and exception information, followed by deterministic structural adaptation, evidence alignment, and validation. On a reconstructed benchmark of 150 requirements, LLM-SE achieves a pooled overlap F1 of 0.8378 over five span-bearing fields, compared with 0.7631 for a reconstructed Sun baseline, while the baseline remains stronger for actor and exception extraction. A separate prompt factorial analysis examines examples, semantic guidance, and output-discipline instructions. On a GDPR-based development benchmark, the resulting records yield downstream F1 scores of 0.5341 and 0.4458 under the same checking pipeline. These results reveal field-dependent extraction benefits and remaining rule–process alignment limitations; the downstream benchmark is not an independently held-out test.

此草稿只使用原稿及冻结材料已经出现的结果，不加入新的实验结论。是否放全部数值可按版面进一步压缩。

## 6. 文件使用顺序与尚待完成项

1. 用 introduction.tex 替换原 Introduction 和 Related Work 两节。
2. 用 part2_postprocessing.tex 替换 Part 2 最后那一段；伪代码可按版面取舍，但保留文字中的算法规则。
3. 将 method_and_evaluation_notes.tex 的五段分别放入对应位置，不要把它整体作为新章节插入。
4. 合并 references_18.bib；保留原有键名，使用正常 \cite，不用 \nocite{*}。例如 \bibliographystyle{IEEEtran} 与 \bibliography{references_18}；实际文件路径按工程设置。
5. 全文、图内、表内统一 LLM-SE。这是展示名统一，不改变历史实验 ID、模型或数值。
6. 按第 5.1 节修正文字符号并核对冻结 Part 3 代码；按第 5.2 节补数据来源与每组配置。没有核实的配置不要填猜测值。
7. 在实际当前 TeX 工程编译，检查引用 18 篇、章节交叉引用、字体、公式、图表和页数。不要通过压缩到不可读字号解决版面。
8. 主表保持四位小数和固定来源；无需为以上文字修订重跑实验。

优先级最高的是：公式–文字一致、指标定义、实验身份、后处理算法。引言合并和引用补齐已经有可直接使用的稿件；上述剩余方法与来源细节完成后，才能把全文称为解释完整的投稿稿。

## 7. 核验所依据的本地材料

全部为只读核对，未运行新实验、调用 LLM API 或改 Gold。

- paper/CLAIM_EVIDENCE_MATRIX.md：C54 主表来源、C55 后处理版本与边界。
- paper/THESIS_DRAFT.md：§4.2.2 历史与当前后处理区别、操作细节与合成例子。
- src/bpc_hybrid/d1_schema_adapter.py：结构适配与 normalized 的实际生成。
- src/bpc_hybrid/d1_span_canonicalizer.py：legacy / repair_v1 的差异、范围与关系清理。
- src/bpc_hybrid/stage2_canonical.py：结构后端、证据、包含、唯一性与引用校验。
- scripts/run_direct_llm.py：adapter → canonicalizer → validator 的执行顺序。
- outputs/reports/stage2_table1_paper_final_v1.json：主表数值、计数与评估视图。
- outputs/reports/direct_llm_formal_arm_v1.manifest.json、data/results/direct_llm_formal_arm_v1/config_snapshot.json：主表冻结身份。
- outputs/evidence/sep_c3_modular_ablation_v1/arms/111/manifest.json：modular_111 提示词与样本数。
- outputs/evidence/sep_c3_modular_ablation_v2/manifest.json：后续消融模型登记与执行配置。
- outputs/reports/d_full_postprocessing_ablation_v2.md：后处理回顾性证据及其使用边界。

上传文件身份：

| 文件 | SHA-256 |
|---|---|
| 2025_CSCWD_Collaboration-Aware Service Composition Optimization for Production Factors Under Industrial Internet(1).pdf | 30b77e78b20aa0cde0dbed8144380c97cc07782ece62629f84bf7ed4dac89256 |
| 2026_CSCWD_Aligning Graphs and Sequences-A Contrastive Learning Approach for Next Event Prediction(1).pdf | be8d89a4a188360e5904e9aed6c07cdfcb415afb73e93da1c1508094a8ef0702 |
| 2027_CSCWD (16).pdf | f2ce8d2b020a41e71e56aca175b8568631e5ba1a1beb37a1b815d24641bf1948 |

本轮只新增本目录中的审阅与替换文件，不修改上传 PDF、旧 TeX、原图、已有实验报告及用户正在改动的文件。文献条目/引用键、LaTeX 片段结构和关键数值可做静态核验；这不等于完整工程已通过编译或版式验收。


## 8. 本轮静态核验结果

- BibTeX 条目 18 个，替换片段实际引用的独立键 18 个；缺失键 0，未使用条目 0。
- 三个 TeX 片段的括号与环境配对检查通过；后续章节 label 在仓库参考源中存在。
- 合成示例的 [15,22) / [16,23) 切片核对通过。
- 主表原始计数和四位小数与冻结 JSON 一致。
- 未进行 TeX 编译、最终页数或版式验收；未运行代码测试、项目审计或任何新实验。
- 这是 PW3/PW5 文档修订 checkpoint，不代表实验完成状态或全文投稿验收通过。
````
<!-- END_SOURCE REVIEW_AND_USE.md -->

## F. 合并引言候选稿

来源文件：[introduction.tex](introduction.tex)。以下完整嵌入，未把建议自动套用到原稿。

<!-- BEGIN_SOURCE introduction.tex -->
````latex
% Replace the complete Introduction AND Related Work with this section.
% Keep later labels sec:3, sec:4, sec:5, sec:6 unchanged; numbering updates.
% 16 distinct citations here; method_and_evaluation_notes.tex supplies two more.
\section{Introduction}
\label{sec:1}

Business process compliance (BPC) concerns the conformance of business processes to applicable laws, regulations, standards, and organizational policies~\cite{hashmi2018we}. Design-time checking seeks to identify potential violations before execution. A central difficulty is connecting requirements written in natural language with the activities, responsibilities, and control flow represented in process models. Surveys of compliance approaches and rule languages describe a range of representations for this purpose~\cite{hashmi2018we,zasada2023evaluation}.

Formal approaches provide explicit representations for automated checking. Awad et al.~\cite{awad2008efficient} combine BPMN-Q with temporal logic, Elgammal et al.~\cite{elgammal2016formalizing} develop a pattern-based compliance language, and Governatori et al.~\cite{governatori2016semantic} investigate regulatory compliance checking using LegalRuleML. These approaches motivate a complementary question: how can the semantics required by a checker be obtained from regulatory text? Sleimi et al.~\cite{sleimi2018automated} study NLP-based extraction of semantic legal metadata, while Michel et al.~\cite{michel2022identification} investigate the identification of decision rules in legislative documents. Within design-time BPC, Winter et al.~\cite{winter2020assessing} assess process models against regulatory documents. Sun et al.~\cite{sun2024design} further combine multi-granularity regulatory semantics, including modality, actor, action, condition, constraint, and exception, with process-model information. Their representation provides the basis for the extraction task studied here.

Large language models (LLMs) offer another mechanism for interpreting regulatory text. De Kinderen and Winter~\cite{de2024towards} investigate prompt templates for legal GRL modeling. Barrientos et al. study regulatory-change impact analysis~\cite{barrientos2026impact} and the complexity of legal change for BPC~\cite{barrientos2026taming}. De Jure uses iterative LLM self-refinement for structured regulatory-rule extraction~\cite{guliani2026dejure}. LLMs have also been applied more directly to process-related tasks: Wang et al.~\cite{wang2025leveraging} generate process triple sequences from specifications for compliance risk identification; Park et al.~\cite{park2026extracting} extract declarative process constraints from natural-language descriptions; and K\"olbel et al.~\cite{koelbel2026context} combine BPMN models with external security knowledge for explanation and compliance assessment.

These studies establish relevant uses of LLMs, but their outputs and evaluation tasks differ. Our question is more specific: how does LLM-based semantic extraction behave when evaluated against a reconstructed non-LLM extractor under the same six-element BPC representation, reference annotations, and evaluation procedure, and how do the resulting records affect a fixed downstream checker? Separating extraction from checking makes both field-level errors and downstream limitations observable, without attributing changes in the checker to the extractor.

We investigate LLM-based Semantic Extraction (LLM-SE) within a three-part design-time BPC framework. Part~1 parses BPMN models into Process Records, while Part~2 independently transforms regulatory requirements into Rule Records. These are parallel upstream branches with no input dependency between them; Part~3 consumes both records for compliance checking. LLM-SE generates candidate records in a single call, followed by deterministic structural adaptation, evidence alignment, and validation. The records are then supplied to a shared checker for missing-action, incorrect-actor, and out-of-order violations. Our contributions are:
\begin{itemize}
    \item An implementation of LLM-SE for an existing fine-grained BPC representation, with source-linked evidence and an explicit deterministic postprocessing procedure.
    \item A controlled extraction comparison against a reconstructed Sun baseline, together with a factorial analysis of semantic examples, semantic guidance, and additional output-discipline instructions.
    \item A downstream comparison using the same checking pipeline on a separate GDPR-based development benchmark, identifying both performance differences and remaining rule--process alignment limitations.
\end{itemize}

Section~\ref{sec:3} presents the problem formulation and framework. Section~\ref{sec:4} describes the methodology. Section~\ref{sec:5} reports the experiments and results, and Section~\ref{sec:6} concludes the paper.
````
<!-- END_SOURCE introduction.tex -->

## G. Part 2后处理候选稿

来源文件：[part2_postprocessing.tex](part2_postprocessing.tex)。以下完整嵌入，未把建议自动套用到原稿。

<!-- BEGIN_SOURCE part2_postprocessing.tex -->
````latex
% Replacement for Output Validation and Normalization in Part 2.
% Describes the historical unique-exact policy associated with Table I.
% Requires amsmath; optional pseudocode requires algorithm + algorithmic.

\textbf{Deterministic Postprocessing.}
The candidate JSON record is processed without further LLM calls, reference annotations, or baseline predictions. We distinguish structural adaptation, evidence alignment, and final validation. The procedure below describes the historical unique-exact alignment policy used for the frozen main comparison; later alignment variants must be reported separately.

First, the adapter converts flat or nested field spans into a common representation, converts supported integer-valued coordinate strings, and assigns deterministic identifiers when they are missing. For the five span-bearing fields, it computes \texttt{normalized} by case folding and collapsing whitespace in the evidence text. The evidence text itself is preserved. Unusable field elements are removed locally, whereas an invalid record-level structure causes rejection.

Second, evidence coordinates are checked against the extraction input string \(T\), using zero-based Unicode character indices and exclusive end positions. A span with text \(u\) and coordinates \([s,e)\) is already grounded when \(0\leq s<e\leq |T|\) and \(T[s:e]=u\). Otherwise, the algorithm searches for exact occurrences of \(u\) within a permitted window \(W=[a,b)\):
\begin{equation}
\mathcal{O}(u,T,W)=\{s:a\leq s<s+|u|\leq b,\ T[s:s+|u|]=u\}.
\end{equation}
Only a unique occurrence permits coordinate correction. Zero or multiple occurrences leave the span unresolved. An already correct span is retained even if its text occurs elsewhere. Clause spans are aligned against the complete input first; field spans and modality evidence are then aligned within the retained clause. Unresolved clauses or field spans are removed. Relations whose required endpoints have been removed are also deleted, without inventing replacement relations.

Finally, structural and cross-field validation checks required fields and types, legal modality labels, exact evidence correspondence, clause containment, identifier uniqueness, and relation references. Remaining violations cause record rejection. Clause containment is checked here even for spans whose original coordinates matched the input. Ordering-relation evidence is checked by this final validator rather than repaired by the coordinate-alignment step. These checks establish structural usability and evidence traceability; they do not establish that a correctly located phrase has the correct semantic role.

For illustration, in \texttt{The clerk must approve.}, \texttt{approve} occupies \([15,22)\). A prediction reporting \([16,23)\) is corrected to \([15,22)\), because the text occurs exactly once. The source and evidence strings remain unchanged, while the erroneous coordinates change. This synthetic example explains the mechanism and is not an experimental observation.

% Optional: include when space permits; final containment is outside this helper.
\begin{algorithm}[t]
\caption{Historical unique-exact evidence alignment}
\label{alg:legacy-grounding}
\begin{algorithmic}[1]
\REQUIRE Span \(p=(u,s,e)\), input \(T\), search window \(W\)
\IF{\(p\) is malformed, \(u\) is empty, or offsets are not integers}
    \RETURN unresolved
\ENDIF
\IF{\(0\leq s<e\leq |T|\) and \(T[s:e]=u\)}
    \RETURN \(p\)
\ENDIF
\STATE Find all exact starts \(O=\mathcal{O}(u,T,W)\)
\IF{\(|O|=1\)}
    \STATE Set \(s\) to the unique start and \(e=s+|u|\)
    \RETURN \((u,s,e)\)
\ENDIF
\RETURN unresolved
\end{algorithmic}
\end{algorithm}
````
<!-- END_SOURCE part2_postprocessing.tex -->

## H. 方法与实验说明的五处候选替换

来源文件：[method_and_evaluation_notes.tex](method_and_evaluation_notes.tex)。以下完整嵌入，未把建议自动套用到原稿。

<!-- BEGIN_SOURCE method_and_evaluation_notes.tex -->
````latex
% These are SEPARATE replacements/insertions, not one continuous section.
% INSERTION 1: add beside the embedding model in the Part 3 setup.
% These two distinct citations bring the total to 18.
Semantic similarity is computed using the
\texttt{sentence-transformers/all-mpnet-base-v2} checkpoint, an MPNet-based
sentence embedding model in the Sentence-BERT framework~\cite{reimers2019sentence,song2020mpnet}.
The exact checkpoint is documented in its model card.\footnote{\url{https://huggingface.co/sentence-transformers/all-mpnet-base-v2}}

% REPLACEMENT 2: Part 2 metric. Preserves the frozen evaluation procedure.
Part~2 uses the frozen coarse sentence-level overlap view. Within each sample
and semantic field, an extracted span is counted as matched if it overlaps at
least one reference region; a reference region is counted as matched if it
overlaps at least one extracted span. These are separate counts, rather than
a one-to-one matching. Pooling over actor, action, condition, constraint, and
exception, precision and recall are
\begin{equation}
P=\frac{N_{\mathrm{matched\ predictions}}}{N_{\mathrm{predictions}}},\qquad
R=\frac{N_{\mathrm{matched\ references}}}{N_{\mathrm{references}}},
\end{equation}
and pooled F1 is \(2PR/(P+R)\). Modality is evaluated separately using
four-class Macro-F1 and is excluded from this pooled span score.
Non-empty overlap measures partial evidence recovery; it does not establish
exact boundaries or complete semantic correctness.

% REPLACEMENT 3: main-table versus prompt-ablation identity.
% Verify per-run settings separately; do not infer an unrecorded release.
Table~I uses the frozen v6/R3 extraction snapshot registered as
\texttt{deepseek-v4-pro}, whereas Table~II evaluates the separate modular
E/S/J prompt family. The full modular configuration~111 is therefore not the
same prompt snapshot as the Table~I extractor. The eight configurations were
each evaluated once across two execution batches; their differences are
descriptive and do not establish stability across repeated runs. The basic
task and schema requirements remain present in configuration~000.

% REPLACEMENT 4: non-LLM baseline.
\textbf{Sun baseline.} We use Sun to denote our independent local
reconstruction of the approach of Sun et al. (2024)~\cite{sun2024design}.
It combines a BERT-TextCNN modality classifier with syntactic analysis
and manually specified extraction rules. Sun is the non-LLM baseline
in our comparison. Its scores are measured in this study using the
local reconstruction; they are not scores reported in the original paper.

% REPLACEMENT 5: compact limitations paragraph after the results.
The findings have several limits. The extraction benchmark contains 150
requirements with reconstructed reference annotations, and the overlap metric
does not require exact span boundaries. The prompt configurations have one
observed run each. The downstream GDPR benchmark was also used during
development and threshold calibration, so its scores do not estimate
performance on an independently held-out test set. Finally, higher extraction
scores do not remove errors in aligning rule semantics with BPMN labels, and
the three evaluated violation types do not demonstrate complete checking of
every semantic element in the Rule Record.
````
<!-- END_SOURCE method_and_evaluation_notes.tex -->

## I. 18 篇 BibTeX

来源文件：[references_18.bib](references_18.bib)。以下完整嵌入，未把建议自动套用到原稿。

<!-- BEGIN_SOURCE references_18.bib -->
````bibtex
% Exactly 18 works. Cite at the mapped claims, not using nocite{*}.
% Elgammal's publisher title is spelled 'appling'.
% ICONIP 2024 proceedings chapter Wang et al. was published in 2025.

@article{hashmi2018we,
  title = {Are we done with business process compliance: state of the art and challenges ahead},
  author = {Hashmi, Mustafa and Governatori, Guido and Lam, Ho-Pun and Wynn, Moe Thandar},
  journal = {Knowledge and Information Systems},
  year = {2018},
  volume = {57},
  number = {1},
  pages = {79--133},
  doi = {10.1007/s10115-017-1142-1}
}

@article{zasada2023evaluation,
  title = {Evaluation of compliance rule languages for modelling regulatory compliance requirements},
  author = {Zasada, Andrea and Hashmi, Mustafa and Fellmann, Michael and Knuplesch, David},
  journal = {Software},
  year = {2023},
  volume = {2},
  number = {1},
  pages = {71--120},
  doi = {10.3390/software2010004}
}

@inproceedings{awad2008efficient,
  title = {Efficient Compliance Checking Using {BPMN-Q} and Temporal Logic},
  author = {Awad, Ahmed and Decker, Gero and Weske, Mathias},
  booktitle = {Business Process Management},
  year = {2008},
  pages = {326--341},
  publisher = {Springer},
  doi = {10.1007/978-3-540-85758-7_24}
}

@article{elgammal2016formalizing,
  title = {Formalizing and appling compliance patterns for business process compliance},
  author = {Elgammal, Amal and Turetken, Oktay and van den Heuvel, Willem-Jan and Papazoglou, Mike},
  journal = {Software and Systems Modeling},
  year = {2016},
  volume = {15},
  number = {1},
  pages = {119--146},
  doi = {10.1007/s10270-014-0395-3}
}

@inproceedings{governatori2016semantic,
  title = {Semantic Business Process Regulatory Compliance Checking Using {LegalRuleML}},
  author = {Governatori, Guido and Hashmi, Mustafa and Lam, Ho-Pun and Villata, Serena and Palmirani, Monica},
  booktitle = {Knowledge Engineering and Knowledge Management},
  year = {2016},
  pages = {746--761},
  publisher = {Springer},
  doi = {10.1007/978-3-319-49004-5_48}
}

@inproceedings{sleimi2018automated,
  title = {Automated Extraction of Semantic Legal Metadata Using Natural Language Processing},
  author = {Sleimi, Amin and Sannier, Nicolas and Sabetzadeh, Mehrdad and Briand, Lionel and Dann, John},
  booktitle = {2018 IEEE 26th International Requirements Engineering Conference (RE)},
  year = {2018},
  pages = {124--135},
  publisher = {IEEE},
  doi = {10.1109/RE.2018.00022}
}

@inproceedings{michel2022identification,
  title = {Identification of Decision Rules from Legislative Documents Using Machine Learning and Natural Language Processing},
  author = {Michel, Maximilian and Djurica, Djordje and Mendling, Jan},
  booktitle = {Proceedings of the 55th Hawaii International Conference on System Sciences},
  year = {2022},
  pages = {6247--6256},
  url = {https://hdl.handle.net/10125/80097}
}

@inproceedings{winter2020assessing,
  title = {Assessing the compliance of business process models with regulatory documents},
  author = {Winter, Karolin and van der Aa, Han and Rinderle-Ma, Stefanie and Weidlich, Matthias},
  booktitle = {Conceptual Modeling},
  year = {2020},
  pages = {189--203},
  publisher = {Springer},
  doi = {10.1007/978-3-030-62522-1_14}
}

@article{sun2024design,
  title = {Design-time business process compliance assessment based on multi-granularity semantic information},
  author = {Sun, Xiaoxiao and Yang, Siqing and Zhao, Chenying and Yu, Dongjin},
  journal = {The Journal of Supercomputing},
  year = {2024},
  volume = {80},
  number = {4},
  pages = {4943--4971},
  doi = {10.1007/s11227-023-05626-0}
}

@inproceedings{de2024towards,
  title = {Towards Taming Large Language Models with Prompt Templates for Legal {GRL} Modeling},
  author = {de Kinderen, Sybren and Winter, Karolin},
  booktitle = {Enterprise, Business-Process and Information Systems Modeling},
  year = {2024},
  pages = {213--228},
  publisher = {Springer},
  doi = {10.1007/978-3-031-61007-3_17}
}

@article{barrientos2026impact,
  title = {Impact analysis of regulatory requirement changes on business process compliance},
  author = {Barrientos, Marisol and Winter, Karolin and Rinderle-Ma, Stefanie},
  journal = {Information and Software Technology},
  year = {2026},
  volume = {194},
  pages = {108079},
  doi = {10.1016/j.infsof.2026.108079}
}

@article{barrientos2026taming,
  title = {Taming the Complexity of Legal Change for Business Process Compliance},
  author = {Barrientos, Marisol and Loebbecke, Johannes and Winter, Karolin and Rinderle-Ma, Stefanie},
  journal = {Business \& Information Systems Engineering},
  year = {2026},
  volume = {68},
  number = {5},
  pages = {1147--1172},
  doi = {10.1007/s12599-026-01008-x}
}

@article{guliani2026dejure,
  title = {{De Jure}: Iterative {LLM} Self-Refinement for Structured Extraction of Regulatory Rules},
  author = {Guliani, Keerat and Gill, Deepkamal and Landsman, David and Eshraghi, Nima and Kumar, Krishna and Gondara, Lovedeep},
  journal = {arXiv preprint arXiv:2604.02276},
  year = {2026},
  url = {https://arxiv.org/abs/2604.02276}
}

@inproceedings{wang2025leveraging,
  title = {Leveraging {LLMs} for Automated Compliance Risk Identification in Business Processes},
  author = {Wang, Yue and Yi, Ningyuan and Chang, Wenjing and Yu, Jianjun},
  booktitle = {Neural Information Processing},
  year = {2025},
  series = {Communications in Computer and Information Science},
  volume = {2287},
  pages = {456--471},
  publisher = {Springer},
  doi = {10.1007/978-981-96-6963-9_32}
}

@article{park2026extracting,
  title = {Extracting declarative constraints for process modeling from natural language descriptions with large language models},
  author = {Park, Gyunam and Kofferath, Julian and Cho, Minsu},
  journal = {Decision Support Systems},
  year = {2026},
  volume = {203},
  pages = {114627},
  doi = {10.1016/j.dss.2026.114627}
}

@article{koelbel2026context,
  title = {Context is key for cybersecurity: leveraging external knowledge for process model explanation via {LLMs}},
  author = {K{\"o}lbel, Linda Maria and Poss, Leo and Sch{\"o}nig, Stefan},
  journal = {International Journal of Information Security},
  year = {2026},
  volume = {25},
  pages = {108},
  doi = {10.1007/s10207-026-01245-x}
}

@inproceedings{reimers2019sentence,
  title = {{Sentence-BERT}: Sentence Embeddings using Siamese {BERT}-Networks},
  author = {Reimers, Nils and Gurevych, Iryna},
  booktitle = {Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP)},
  year = {2019},
  pages = {3982--3992},
  publisher = {Association for Computational Linguistics},
  doi = {10.18653/v1/D19-1410},
  url = {https://aclanthology.org/D19-1410/}
}

@inproceedings{song2020mpnet,
  title = {{MPNet}: Masked and Permuted Pre-training for Language Understanding},
  author = {Song, Kaitao and Tan, Xu and Qin, Tao and Lu, Jianfeng and Liu, Tie-Yan},
  booktitle = {Advances in Neural Information Processing Systems},
  year = {2020},
  volume = {33},
  pages = {16857--16867},
  url = {https://proceedings.neurips.cc/paper/2020/hash/c3a690be93aa602ee2dc0ccab5b7b67e-Abstract.html}
}
````
<!-- END_SOURCE references_18.bib -->

## J. 原稿辅助阅读文本（未经修正，数学排版以 PDF 为准）

来源文件：[source_2027_CSCWD_16.md](source_2027_CSCWD_16.md)。以下完整嵌入，未把建议自动套用到原稿。

<!-- BEGIN_SOURCE source_2027_CSCWD_16.md -->
````markdown
# 2027 原稿：按页、按栏提取的辅助阅读文本

> 来源为同目录 source_2027_CSCWD_16.pdf，六页，未经修订。
> SHA-256: f2ce8d2b020a41e71e56aca175b8568631e5ba1a1beb37a1b815d24641bf1948
> 这是机器提取文本，不是 LaTeX 源码。保留原稿中的错误供定位；数学上下标、公式、表格和图内文字可能失真，必须以原 PDF 为准。
> 每页先读左栏、再读右栏；跨栏页眉/标题单独列出。页末图注只作定位。
> 不要把这里的 Direct-LLM 等历史名称当成新的命名要求；修订时按阅读包的 LLM-SE 约定。

## PDF 第 1 页

### 跨栏标题与作者信息

Design-Time Business Process Compliance
    Checking with Large Language Models

          Yingchao Huo, Xiaoqing Chen, Jiahao Ma, Guosheng KangB, Wen Li, Jiayan Xiang
1Hunan Provincial Key Lab. for Services Computing and Novel Software Technology, HNUST, Xiangtan, Hunan, China
    2School of Computer Science and Engineering, Hunan University of Science and Technology, Xiangtan, China
 Email: {huoyingchao666, xiaoqingchen696, jiahaoma2627, guoshengkang, wenli0023cs, jiayanxiang02}@gmail.com

### 左栏

```text
Abstract—Design-time  business  process  compliance (BPC)
checking aims  to  identify potential  violations before process
execution. Existing approaches often rely on manually designed
linguistic rules and  syntactic patterns  to transform natural-
language  compliance  requirements  into  machine-processable
representations. This paper investigates large language model
(LLM)-based semantic extraction for design-time BPC check-
ing. Natural-language compliance requirements are transformed
into structured Rule Records containing modality, actor, action,
condition, constraint, and exception information. We compare
Direct-LLM with a reconstructed Rules-Only approach under
a common semantic representation and evaluation setting. We
further analyze the effects of prompt configurations and examine
how the resulting Rule Records influence downstream compliance
checking.
  Index  Terms—Business  Process  Compliance,  Design-Time
Compliance Checking, Large Language Models, Compliance
Requirement Parsing, Violation Detection

                           I. INTRODUCTION
  Business process compliance (BPC) aims to ensure that
business processes conform to applicable laws, regulations,
standards, and organizational policies [1]. Design-time BPC
checking identifies potential violations before process exe-
cution, but a major challenge is the semantic gap between
natural-language compliance requirements and formal process
models. Many existing approaches rely on compliance con-
straints that have already been formalized, making the trans-
formation of regulatory text into machine-processable repre-
sentations an important and often labor-intensive step [1, 2].
  To reduce this effort, Winter et al. [3] investigated com-
pliance assessment directly from regulatory documents. Sun
et al. [4] further proposed a design-time BPC framework that
extracts fine-grained regulatory semantics, including modality,
actor, action, condition, constraint, and exception, and matches
them with process-model information for violation detection.
Their semantic extraction combines syntactic analysis and
manually designed linguistic rules. While explicit and inter-
pretable, such extraction depends on predefined patterns and
linguistic resources.
  Recent work has explored Large Language Models (LLMs)
for legal requirement modeling, structured regulatory-rule ex-
traction, and BPC-related analysis [5–8]. Although some of
these studies adopt BPC-relevant semantics or extract fine-
grained regulatory information, their primary objectives differ
from directly comparing LLM-based and rule-based extrac-
tion of individual compliance requirements within a common
```

### 右栏

```text
design-time BPC setting.  It therefore remains useful to ex-
amine how Direct-LLM extraction behaves under the same
target representation and evaluation setting as a reconstructed
non-LLM baseline, and how the resulting Rule Records affect
downstream BPMN compliance checking.
  In this paper, we investigate Direct-LLM semantic extrac-
tion within this design-time BPC setting. Natural-language
compliance requirements are transformed into structured Rule
Records, while BPMN process models are converted into
structured process information for downstream matching and
violation analysis. We compare Direct-LLM with an inde-
pendent Rules-Only reconstruction under common inputs, se-
mantic representations, reference annotations, and evaluation
procedures. We further analyze the effects of different prompt
configurations and examine how the resulting Rule Records
influence downstream compliance checking.
  The main contributions of this work are:
  • We apply Direct-LLM extraction to an existing  fine-
     grained BPC semantic representation and generate struc-
     tured Rule Records for downstream compliance checking.
  • We conduct a controlled comparison between Rules-Only
    and Direct-LLM extraction, analyze their strengths and
     limitations at the semantic-element level, and examine
     the effects of different prompt configurations.
  • We connect the extracted Rule Records with downstream
    compliance checking and evaluate their effects on the
     three original violation types: missing action, incorrect
     actor, and out-of-order execution.
  The remainder of this paper is organized as follows. Sec-
tion II reviews related work. Section III presents the problem
formulation and framework. Section IV describes the method-
ology. Section V reports the experiments and  results, and
Section VI concludes the paper.

                        II. RELATED WORK

  Design-time business process compliance checking has been
studied using logic-based, pattern-based, and other formal
compliance representations [1, 2]. These approaches provide
precise and machine-processable constraints, but regulatory re-
quirements generally need to be formalized before automated
checking can be performed. To reduce this manual  effort,
Winter et al. [3] investigated compliance assessment directly
from regulatory documents. Sun et al. [4] further proposed a
design-time BPC approach that extracts fine-grained semantic
```

## PDF 第 2 页

### 左栏

```text
information from regulatory text and combines it with process-
model information for violation detection.
  Recent work has explored large language models (LLMs)
for legal and regulatory modeling. De Kinderen and Winter [5]
studied prompt-based generation of legal requirement models.
Barrientos et al. [6, 7] investigated regulatory-change detection
and its relevance or impact on business process compliance,
including BPC-relevant semantics related to the representation
of Sun et al. [4]. Guliani et al. [8] proposed De Jure, an LLM-
based pipeline for fine-grained structured extraction of regu-
latory rules with iterative evaluation and repair. These studies
demonstrate the potential of LLMs for regulatory analysis, but
their primary objectives differ from directly extracting individ-
ual compliance requirements under a shared Sun-style BPC
representation and comparing the resulting Rule Records in
the same design-time BPMN compliance-checking pipeline. In
contrast, this work conducts a controlled comparison between
a reconstructed non-LLM extractor and Direct-LLM under the
same target representation and evaluator, and further examines
their downstream compliance-checking outcomes.

      III. PROBLEM FORMULATION AND FRAMEWORK

A. Problem Formulation

  Following the design-time BPC setting of Sun et al. [4], we
consider a BPMN process model P and a natural-language
compliance requirement q. The process model is transformed
into a Process Record P, which contains process elements,
participants or actors, control-flow relations, and label seman-
tics. The compliance requirement is transformed into a Rule
Record R, which contains modality, actor, action, condition,
constraint, exception, and supporting evidence. Design-time
compliance checking then uses (P, R) for rule–process match-
ing and violation analysis.

B. Overall Framework

  As illustrated in Fig. 1, the proposed framework consists of
three stages: Process Model Parsing, Compliance Requirement
Parsing, and Compliance Checking. Stage 1 parses the BPMN
process model and organizes the extracted process elements,
participants, control-flow relations, and label semantics into a
structured Process Record. Independently, Stage 2 uses Direct-
LLM semantic extraction to transform the natural-language
compliance requirement into a structured Rule Record contain-
ing fine-grained compliance semantics. Stage 3 combines the
Process Record and Rule Record for rule–process matching
and detects missing-action, incorrect-actor, and out-of-order
violations. The detailed Direct-LLM procedure in Stage 2 is
presented in Section IV-B.

                   IV. METHODOLOGY

A. Process Model Parsing

  Following Sun et al. [4], Stage 1 uses a deterministic BPMN
parser to extract process elements, participant information,
```

### 右栏

```text
sequence flows, and textual labels. Sequence flows are fur-
ther used to derive control-flow edges, transitive reachabil-
ity, and activity-order relations. Actor, action, and business-
object semantics are obtained from process labels using a
fixed linguistic analysis procedure following the process-label
analysis strategy of Sun et al. The extracted information is
organized into a structured Process Record containing activ-
ities, participants, control-flow relations, and label semantics
for downstream compliance checking.

B. Compliance Requirement Parsing

  Stage 2 transforms each natural-language compliance re-
quirement into a structured Rule Record. Following the se-
mantic representation of Sun et al. [4], each record is orga-
nized into clauses containing modality, actor, action, condition,
constraint, and exception information. Span-bearing elements
are represented by source-anchored evidence spans with stable
identifiers and normalized values for downstream matching.
Character offsets use zero-based start and exclusive end posi-
tions, and the recorded evidence text must correspond exactly
to the associated source span. Actor–action associations ref-
erence the identifiers of extracted actors and actions, while
ordering relations reference the identifiers of their before/after
action endpoints.
  Prompt Design. As shown in Fig. 2, the prompt consists
of a shared base layer and three configurable components.
The shared base layer defines the extraction task, target Rule
Record schema, source and evidence representation, span and
identifier requirements, and the basic structural output inter-
face. It is retained throughout all prompt configurations. On
top of this base layer, E provides synthetic worked examples,
S provides detailed semantic interpretation guidance, and J
provides additional JSON and output-discipline instructions.
Only E, S, and J are varied in the factorial experiment, while
the shared base layer remains fixed.
  Direct-LLM Semantic Extraction. Given the requirement
and prompt, Direct-LLM directly generates structured seman-
tic elements, supporting evidence, and relations without using
predictions from the rule-based baseline or reference annota-
tions. The generated information is organized into a candidate
Rule Record under a unified JSON representation. This design
allows semantic extraction to be performed within a single
LLM  call while preserving the fine-grained representation
required by downstream compliance checking.
  Output  Validation and Normalization. The generated
candidate record is processed by a deterministic validation and
normalization procedure before being used in Stage 3. The
procedure checks schema conformance, exact correspondence
between evidence  text and source  offsets, containment of
element spans within their clauses, uniqueness of element
identifiers, and  referential consistency of actor–action and
ordering relations.  If an evidence span  is misaligned,  it  is
re-anchored only when the reported text has a unique exact
occurrence  in the corresponding source clause; otherwise,
the unrecoverable element  is removed. Normalized values
are retained for downstream semantic matching, while the
```

## PDF 第 3 页

### 左栏

```text
original evidence text and source offsets remain unchanged.
This procedure repairs structural and alignment errors without
introducing new semantic interpretations.

C. Compliance Checking

  Stage 3 combines the Process Record and Rule Record
for rule–process matching and violation detection. Following
Sun et al. [4], we retain the three original violation types:
missing action, incorrect actor, and out-of-order execution.
Let Ar and Ur denote the actions and actors contained in
rule r, respectively, and let sim(xr, xp) denote the semantic
similarity between a  rule-side element and a process-side
element. Thresholds τ, γ, and θ are used for rule–process
matching, action mapping, and actor comparison, respectively.
  Rule–Process Matching. Each rule action is matched to its
most similar process-side action, forming the candidate map-
ping set Dr,p. Rule actors are matched analogously, forming
Or,p. The action and actor matching ratios and the overall
rule–process matching score are defined as

               ∑︂    sim(ar, am) > τ
                     (ar,am)∈Dr,m
     mA(r, m, τ) =                                               ,
                               |Dr,m|
               ∑︂    sim(or, om) > τ       (1)
                      (or,om)∈Or,m
     mO(r, m, τ) =                                              ,
                               |Or,m|
       F(r, m, τ) = max{mA(r, m, τ), mO(r, m, τ)}.

When Ar =  ∅, mA(r, p; τ)  is defined as 0; analogously,
mU(r, p; τ) = 0 when Ur =  ∅. The resulting mappings
provide the basis for the three downstream violation checks.
  Missing-Action  Violation.  For  each  required  rule  ac-
tion ar ∈Ar,  let s(ar, p) = maxap∈Ap sim(ar, ap), with
```

### 右栏

```text
s(ar, p) = 0 when Ap = ∅. For |Ar| > 0, the missing-action
score is

      Br,m,γ = {(ar, am) ∈Dr,m | sim(ar, am) < γ}.   (2)


                                        |Br,m,γ|
          action violation(r, m, γ) =              .         (3)
                                        |Ar|

Thus, a rule action with no process-side candidate is counted
as missing. If Ar = ∅, the case is unevaluable for missing-
action checking and no decision is produced.
  Incorrect-Actor Violation. Actor checking  is performed
after  the corresponding  rule  action has been  successfully
mapped  to a process  activity. Let Rr,p,γ  denote the  rule
actors associated with successfully mapped actions and Cr,p,γ
the union of actor or business-object candidates bound to
those matched activities. Following the Sun-style definition,
for |Rr,p,γ| > 0 and Cr,p,γ ̸= ∅,

         Rr,m,γ = {︁ g ∈Pr | ∃(ar, am) ∈Dr,m,
                                                              (4)
                 fr(g) = ar ∧sim(ar, am) > γ }︁ .

         Cr,m,γ = {︁ r ∈bs obj(Am ∪Em) ∪Rm |
               ∃g ∈Rr,m,γ,                            (5)
                 sim(fr(g), fm(r)) > γ }︁ .

            Ir,m,γ,ϑ = {︁ r ∈Rr,m,γ | ∃r′ ∈Cr,m,γ,
                                                              (6)
                   sim(r, r′) < ϑ}︁ .

                                             |Ir,m,γ,ϑ|
         actor violation(r, m, γ, ϑ) =               .        (7)
                                         |Rr,m,γ|

For non-empty Cr,p,γ, this minimum test is equivalent to the
existential condition ∃up ∈Cr,p,γ  : sim(ur, up) < θ in Sun
```

### 图与图注（图形以原 PDF 为准）

Fig. 1: Overall framework for design-time business process compliance checking.

## PDF 第 4 页

### 左栏

```text
et al. [4]; the minimum form is used as an implementation-
equivalent rewriting. If the required actor, actor–action associ-
ation, or corresponding process-side candidate is unavailable,
the case is unevaluable for actor checking and no decision is
produced.
  Out-of-Order Violation. Ordering checks are performed
for rule-side ordering relations whose endpoints can both be
mapped to process  activities. Let Ur,p,γ denote the set of
evaluable ordering relations and Sr,p,γ ⊆Ur,p,γ the subset
satisfied by the process control flow. For |Ur,p,γ| > 0, the
out-of-order score is
      Ur,m,γ = {︁ (ur, u′r) ∈Ur |
           ∃{︁ (ur, um) ∈Dr,m, (u′r, u′m) ∈Dr,m }︁ ,    (8)
             sim(ur, um) > γ ∧sim(u′r, u′m) > γ }︁ .

      Sr,m,γ = {︁ (ur, u′r) ∈Ur,m,γ |
           ∃{︁ (ur, um) ∈Dr,m, (u′r, u′m) ∈Dr,m }︁ ,    (9)
            (um, u′m) ∈Fm ∧(u′m, um) /∈Fm }︁ .

                                 |Ur,m,γ| −|Sr,m,γ|
    order violation(r, m, γ) =                              .    (10)
                                      |Ur,m,γ|

An ordering relation is satisfied when the first mapped activity
can reach the second activity in the process control flow while
reverse reachability does not hold. If |Ur,p,γ| = 0, the case is
treated as unevaluable for out-of-order checking and no order-
violation decision is produced.

             V. EXPERIMENTS AND RESULTS

  We evaluate the proposed approach from three perspectives.
First, we compare Rules-Only and Direct-LLM  for  fine-
grained semantic extraction. Second, we analyze how different
prompt components affect Direct-LLM through a full factorial
experiment. Finally, we examine whether the extracted Rule
```

### 右栏

```text
Records lead to different downstream compliance-checking
performance.

A. Experimental Setup

  Stage  2  evaluation. We  use an  independently  recon-
structed EStG-150 benchmark containing 150 compliance re-
quirements. Its reference annotations form an LLM-assisted,
human-adjudicated Gold standard constructed for this study
rather than the original unpublished annotations of Sun et
al. [4]. Rules-Only and Direct-LLM are evaluated against the
same frozen Gold and evaluator. For actor, action, condition,
constraint, and exception, a prediction matches a Gold span
when  their character  intervals have a non-empty overlap;
Overall Micro-F1 pools TP, FP, and FN over these five fields.
Modality is evaluated separately by four-class Macro-F1 and
is excluded from the overall score.
  Rules-Only baseline. Rules-Only is an independent recon-
struction of the Stage 2 approach described by Sun et al. [4],
based on syntactic analysis and manually designed linguistic
rules. It is treated as a reconstructed baseline rather than the
original implementation. Both methods use the same frozen
inputs, Gold annotations, target representation, and evaluator.
  Direct-LLM and prompt configurations. All Direct-LLM
experiments use DeepSeek-V4-Pro-0813 with temperature 0,
top-p 1.0, and a maximum output length of 4096 tokens.
Table I and Table II are separate frozen runs; the provider
exposes no supported random seed, so  all differences are
interpreted descriptively without statistical-significance claims.
The shared prompt base remains fixed, while E, S, and J
denote semantic examples, semantic guidance, and additional
output discipline. Configuration 111 is the intact frozen full
prompt, the other configurations are controlled factorial vari-
ants, and 000 retains the shared base rather than representing
an unprompted LLM.
```

### 图与图注（图形以原 PDF 为准）

Fig. 2: Detailed workflow of Stage 2.

## PDF 第 5 页

### 左栏

```text
TABLE I: Semantic extraction performance of Rules-Only and
Direct-LLM.

          Element              Rules-Only   Direct-LLM

           Modality (Macro-F1)      0.713          0.769
           Actor                    0.820          0.758
           Action                   0.893          0.944
           Condition                 0.774          0.838
            Constraint                0.618          0.743
           Exception                0.880          0.762
           Overall (Micro-F1)∗       0.763          0.838
∗Pooled over actor, action, condition, constraint, and exception; modality is
                                excluded.


  Stage 3 evaluation. Stage 3 uses a separately constructed
GDPR-based benchmark because downstream checking re-
quires paired compliance requirements and BPMN models.
Nine GDPR rule texts are segmented into 74 sentences and
paired with 115 case records, yielding 201 applicable case–
type cells per method: 113 missing-action, 80 incorrect-actor,
and 8 out-of-order cells. These cells are fixed independently
of method outputs; an unevaluable prediction remains in the
evaluation, counting as FN for a violated reference and as
unknown rather than TN for a satisfied reference. Overall
precision,  recall, and F1  in Table  III pool  TP,  FP, and
FN over these cells. After development-stage calibration us-
ing a shared objective across both methods, Sentence-BERT
all-mpnet-base-v2 was selected with τ = 0.8, γ =
0.55, and θ = 0.45. Because the same benchmark was used
during development and calibration, the results are descriptive
rather than an independently held-out test.

B. Semantic Parsing Results

  Table I shows that the two approaches have different field-
level strengths. Direct-LLM achieves higher F1 for action,
condition, and  constraint, and  higher modality macro-F1,
whereas Rules-Only performs better for actor and exception.
The largest Direct-LLM gain occurs for constraint extraction,
increasing from 0.618 to 0.743. Overall pooled F1 over the five
span-bearing fields increases from 0.763 to 0.838, an absolute
improvement of approximately 7.5 percentage points.
  The results therefore do not indicate uniform superiority
across all semantic elements. Rules-Only remains stronger for
actor and exception extraction, while Direct-LLM performs
better on most of the remaining semantic fields. These field-
level results characterize the extraction behavior of the two
methods on EStG-150; the downstream experiment in Sec-
tion V-D is evaluated separately on the GDPR-based bench-
mark.

C. Prompt Factorial Analysis

  Table II shows a non-additive interaction among the prompt
components. Enabling E improves F1 in  all four matched
comparisons, making semantic examples the most consistently
beneficial component. In contrast, S provides substantial gains
when examples are absent but slightly decreases F1 when
```

### 右栏

```text
TABLE II: Factorial analysis of Direct-LLM prompt compo-
nents.

            E   S   J    F1   ∆F1 vs. 111

                0   0   0   0.7380      -0.0844
                0   0   1   0.7261      -0.0963
                0   1   0   0.8107      -0.0117
                0   1   1   0.8142      -0.0082
                1   0   0   0.8354     +0.0130
                1   0   1   0.8299      +0.0075
                1   1   0   0.8268      +0.0044
                1   1   1   0.8224      0.0000

TABLE III: Performance comparison of downstream compli-
ance checking.

        Method                Precision   Recall    F1

           Sun-style Rules-Only     0.3814     0.5362   0.4458
         Direct-LLM             0.4393     0.6812   0.5341


E is already present, suggesting partial overlap between ex-
amples and detailed semantic guidance. The effect of J  is
comparatively small and inconsistent. This does not imply that
structured output requirements are unnecessary, because the
shared schema and basic output constraints remain active in
every configuration.
  Configuration 100 achieves the highest observed F1 of
0.8354, whereas the intact full-prompt configuration 111 ob-
tains 0.8224. Thus, increasing prompt detail does not mono-
tonically improve extraction performance. Because the  full
prompt was frozen before the factorial experiment, configu-
ration 100 is treated as an ablation observation rather than a
post-hoc replacement of the main method.

D. Downstream Compliance Checking

  Rules-Only and Direct-LLM are applied to the same GDPR
compliance texts, and their resulting Rule Records are pro-
cessed by the same frozen Stage 3 pipeline. Table III reports
pooled performance over the 201 applicable evaluation cells.
Direct-LLM achieves an overall F1 of 0.5341 compared with
0.4458 for Rules-Only, an absolute gain of 8.83 percentage
points. Recall increases from 0.5362 to 0.6812 and precision
from 0.3814 to 0.4393. At the violation-type level, missing-
action F1 increases from 0.4554 to 0.4935 and incorrect-actor
F1 from 0.4262 to 0.5684, while both methods obtain 0.5000
for out-of-order checking.
  These downstream scores should not be directly compared
with the Stage 2 extraction scores because the two experi-
ments use different benchmarks, tasks, and evaluation units.
Downstream checking additionally requires the extracted com-
pliance semantics to be aligned with BPMN activity labels
and process-control information. A post-hoc analysis of the
frozen missing-action results identifies 50 of 70 false-positive
method–case cells (71.4%) as mapping-related and 20 (28.6%)
as broadly scope-related. Only 11 of the  latter satisfy the
stricter criterion for safely removable scope errors. Since this
analysis concerns missing-action false positives only, it should
not be interpreted as a decomposition of all Stage 3 errors. The
```

## PDF 第 6 页

### 左栏

```text
results nevertheless identify rule–process semantic alignment
as a major remaining limitation.

                   VI. CONCLUSION

  This paper  investigates Direct-LLM semantic  extraction
within a three-stage design-time BPC framework. Rules-Only
and Direct-LLM produce the same structured Rule Record
representation, enabling controlled comparison in Stage 2 and
downstream evaluation under the same Stage 3 pipeline. On
EStG-150, Direct-LLM performs better for modality, action,
condition, and constraint, while Rules-Only remains stronger
for actor and exception; Overall Micro-F1 over the five span-
bearing fields increases from 0.763 to 0.838. The factorial
analysis further shows that semantic examples provide the
most consistent prompt benefit, while detailed semantic guid-
ance and  additional output  discipline  exhibit non-additive
effects.
  On  the  separate GDPR-based development benchmark,
Direct-LLM Rule Records yield a downstream F1 of 0.5341
compared with 0.4458 for Rules-Only under the same check-
ing pipeline. These results should not be interpreted as a direct
field-level transfer of the EStG-150 results. The downstream
analysis identifies rule–process semantic alignment, particu-
larly the alignment between extracted compliance actions and
BPMN activity labels, as an important remaining challenge.
Future work will therefore focus on improving this alignment
and evaluating the approach on independently held-out bench-
marks.

             ACKNOWLEDGMENT

  This work  is  partially supported by the Hunan Provin-
cial Natural Science Foundation of China under Grant No:
2026JJ50519. Guosheng Kang is the corresponding author.

                 REFERENCES

[1] M. Hashmi, G. Governatori, H.-P. Lam, and M. T. Wynn,
    “Are we done with business process compliance: state of
    the art and challenges ahead,” Knowledge and Information
    Systems, vol. 57, no. 1, pp. 79–133, 2018.
[2] A. Zasada, M. Hashmi, M. Fellmann, and D. Knuplesch,
    “Evaluation of compliance rule languages for modelling
    regulatory compliance requirements,” Software,  vol.  2,
    no. 1, pp. 71–120, 2023.
[3] K. Winter, H. van der Aa, S. Rinderle-Ma, and M. Wei-
    dlich, “Assessing the compliance of business process mod-
    els with regulatory documents,” in Conceptual Modeling.
    Springer, 2020, pp. 189–203.
[4] X. Sun, S. Yang, C. Zhao, and D. Yu, “Design-time
    business process compliance assessment based on multi-
    granularity semantic information,” The Journal of Super-
    computing, vol. 80, no. 4, pp. 4943–4971, 2024.
[5] S. de Kinderen and K. Winter, “Towards taming large
    language models with prompt templates for legal grl mod-
    eling,” in Enterprise, Business-Process and Information
    Systems Modeling.  Springer, 2024, pp. 213–228.
```

### 右栏

```text
[6] M. Barrientos, K. Winter, and S. Rinderle-Ma, “Impact
    analysis of regulatory requirement changes on business
    process compliance,” Information and Software Technol-
    ogy, vol. 194, p. 108079, 2026.
[7] M. Barrientos, J. Loebbecke, K. Winter, and S. Rinderle-
   Ma, “Taming the complexity of legal change for business
    process compliance,” Business & Information Systems
    Engineering, pp. 1–26, 2026.
[8] K. Guliani, D. Gill, D. Landsman, N. Eshraghi, K. Kumar,
   and L. Gondara, “De jure: Iterative llm self-refinement for
    structured extraction of regulatory rules,” arXiv preprint
    arXiv:2604.02276, 2026.
```
````
<!-- END_SOURCE source_2027_CSCWD_16.md -->

## K. 交付边界

此包是逐节写作的阅读材料，不是已经完成并编译的修订论文。不要声称已替作者修改 Overleaf、完成图表排版或通过实验发布门禁。
目录中的 18 个条目与替换稿的 18 个实际引用键已核对；公式、实验事实、引文内容和版面仍应在逐节修改及最终整合时分别核验。
