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
