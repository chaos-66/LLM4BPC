# CSCWD 投稿定位、相关工作与证据边界

核验日期：2026-09-17；本轮本地起点：`b4400ec9f2550f46a3162a801c5eaf1ded79d919`，
分支 `codex/b0-r1-a-span-boundaries`。本文是写作依据与文献核查笔记，不是新的任务表、
实时状态页或实验报告。进度以 [MASTER_PIPELINE](../docs/MASTER_PIPELINE.md) 和
[PROJECT_AUDIT](../docs/PROJECT_AUDIT.md) 为准；科学主张以
[CLAIM_EVIDENCE_MATRIX](CLAIM_EVIDENCE_MATRIX.md) 和原始 manifest 为准。
本轮只读核验已有证据，不重新运行实验、评价器或真实 API，不作全代码正确性保证。

## 1. 用户目标与投稿判断

2026-09-17 用户希望以 CSCWD 2027 为投稿目标，按今年十月底准备，完整说明已有工作，
不为追求显眼创新不断堆新模块；同时希望评估实验风险、减少与已有论文的实质重合。
保留现有 2026-09-30 导师完整初稿目标，任务继续按真实依赖推进。

评估结论：主题适合按 CSCWD 应用/实证研究方向准备；现有工作值得继续形成完整稿件。
这不是录用预测，也不是“C 类不需要原创贡献”。已有技术的受控比较、明确的工程适配和
有证据的错误/能力边界分析，可以构成研究贡献；仅描述做过很多工作、换用 LLM 或更换
字段名称，不能单独建立贡献。实验规模、形式化校验和 Git 留痕也不自动证明科学结论。

## 2. 官方会议信息：年份必须分清

| 项目 | 本轮核验结果 | 写作/准备时的用法 |
|---|---|---|
| CCF 分类 | CCF 官方 CSCWD 条目位于人机交互与普适计算的 C 类会议目录 [V1] | 可说明 CCF-C 定位；不据此推断录用率或校内保研认定 |
| 主题 | 2026 届官方范围包括业务流程管理和 LLM [V2] | 主题有匹配依据；引言应说明流程设计者如何使用结构化证据识别合规问题，不虚构协同用户研究 |
| 篇幅与审稿 | 2026 届为英文、IEEE 格式、6 页含图和参考文献，single-blind；评审涉及原创性、意义、相关性、表达 [V2] | 可用六页作为暂定压缩练习；2027 届页数、模板与匿名规则均待当届核实 |
| 2026 届日期 | 原始 CFP 截止 2025-10-31 [V3]；官网更新截止为 2025-11-30，会议 2026-05-13 至 15 [V2] | 不把这一届的日期写成今年十月底 |
| 2027 届日期 | 用户在本轮提供当届通知：2026-10-31 截稿，2027-01-31 通知结果，2027-05-26 至 28 在澳大利亚 Brisbane 开会 [V4] | 按这份当届通知准备；日期来源是用户提供的通知，未冒称网页正文独立复核 |
| 2027 投稿入口 | 已从 EasyChair 登录页独立核到 CSCWD 2027 全称及新稿提交已开放 [V5] | 当届与入口已确认；未登录、未投稿。具体时区、摘要节点、篇幅与匿名要求仍待官网/系统正文核实 |
| 保研成果认定 | 未提供学校政策、成果截止日及录用/见刊要求 | 投稿、录用、出版和学校认可分别确认；“保研神会”不作为证据 |

- [V1：CCF 官方 CSCWD 条目](https://www.ccf.org.cn/Academic_Evaluation/HCIAndPC/zgjsjxhtjgjxshy/cl/2017-05-10/593713.shtml)。本轮读到官方域名搜索索引正文；直接打开返回错误，未核验学校采用的目录版本。
- [V2：CSCWD 2026 承办方官网](https://fyust.edu.cn/gjhyqk/cscwd2026/)。本轮读取官网正文。
- [V3：CSCWD 2026 原始 CFP](https://fyust.edu.cn/gjhyqk/cscwd2026/cfp.pdf)。本轮读取索引文本；日期已被官网更新。
- [V4：用户提供的 CSCWD 2027 官网](http://2027.cscwd.org/)与[会议网站](https://scwd2027.dailyeliteevents.com.au/)。用户通知逐项给出上述日期；本轮网页工具未取得正文，直接读取分别遇到 HTTP 406 / TLS EOF，故不声称独立读到截止日期或格式规则。
- [V5：CSCWD 2027 EasyChair](https://easychair.org/conferences/?conf=cscwd2027)。本轮直接读取公开登录页，核到会议全称及新稿开放提示；无需账户操作。

本轮最初仅检索到往届网页，随后用户补充当届通知，因而已有明确的 2027 投稿目标与日期。
网页读取失败不影响按通知准备；待可读取当届正文时在原 Pipeline/状态页补全规则。
不要因往届延期而推迟准备；若学校的成果认定早于 2027-01-31，这次投稿不能预先当作
已录用成果。学校具体规则尚未提供，不作是否赶得上保研的结论。

## 3. 与近期工作的重叠：承认借鉴，比较研究问题

这是一轮针对用户提供文献的核验，不是穷尽查新。“没有找到完全相同的流程”不等于证明
新颖性；用不同字段、数据或模块名称，也不能规避实质相同的研究问题。

| 文献与核验深度 | 已有工作/重叠 | 本文可讨论的区别及尚需的证据 |
|---|---|---|
| Xiaoxiao Sun et al., *Design-time business process compliance assessment based on multi-granularity semantic information*, 2024 卷期；出版社摘要与元数据 [R1] | 深度学习与规则模板抽取多粒度法规语义，匹配流程并检查三类控制流违规 | 三阶段是继承主干。本文为独立重建和解析方法受控比较；不能称原作者系统精确复现。最终版表号/超参与本地作者稿的对应仍需原文核实 |
| Barrientos et al., *Taming the Complexity of Legal Change for Business Process Compliance*, 2026；HTML 全文 §6.1–6.2 [R2] | LegalChanges4BPC 采用 Sun 语义，比较法规新旧版本，以 LLM 生成结构化变化并判断 BPC 相关性 | 正文明确具体流程影响分析不在实现范围。本文若完成固定检查器下的解析替换与误差传播，研究对象有区别；仅“Sun 语义＋LLM＋JSON”已非独有 |
| Wang et al., *Leveraging LLMs for Automated Compliance Risk Identification in Business Processes*, 2025（ICONIP 2024）；出版社摘要 [R3] | 规范文本经 LLM 转为 process triple sequences，再比较标准流程与实际流程 | 整体架构接近；应补读全文的表示、检查机制与实验。本轮不能断言其没有字段级分析或没有相关功能，也不推定其是否直接采用 Sun |
| Kölbel et al., *Context is key for cybersecurity: leveraging external knowledge for process model explanation via LLMs*, 2026；HTML 方法/评价正文 [R4] | BPMN 与安全标准上下文支持 LLM 合规问答，研究提示策略与评价 | 本文可研究显式记录与固定检查器的误差传播。其 74.6% 对应特定问答评价，不能与本文抽取 F1 比大小；确定性检查也不自动意味着语义正确或总体更可靠 |
| Jingyun Sun et al., *A Compliance Checking Framework Based on Retrieval Augmented Generation*, COLING 2025；ACL 官方摘要 [R5] | RAG、Eventic Graph 与中英文文本合规检查 | 应承认 LLM 与结构化法规知识结合已有先例；本轮摘要未提供足够证据排除所有 BPMN/流程表示细节。Jingyun Sun 与主干作者 Xiaoxiao Sun 是不同作者 |
| Barrientos et al., *Impact analysis of regulatory requirement changes on business process compliance*, 2026；出版社摘要及本地既有原文核查 [R6] | RC4PC 以 LLM 与算法组合分析法规变化、流程合规偏离及解释 | 本来就是项目的结构化输出/校验方法来源；与 LegalChanges4BPC 是两篇工作。本文不承诺整体超过 RC4PC，也不以跨 schema 适配零分证明其方法差 |

- [R1：Sun 最终发表页](https://link.springer.com/article/10.1007/s11227-023-05626-0)：在线发表 2023-09-22，卷期为 2024；本轮没有读到订阅全文。
- [R2：LegalChanges4BPC](https://link.springer.com/article/10.1007/s12599-026-01008-x)：2026-07-27 发表；重点核对 §6.1、§6.2.1、§6.2.2。
- [R3：AFPCRL](https://link.springer.com/chapter/10.1007/978-981-96-6963-9_32)：2025-06-14 在线，pp. 456–471。
- [R4：Context is key](https://link.springer.com/article/10.1007/s10207-026-01245-x)：重点核对 §6 的任务与评价单位。
- [R5：COLING 2025](https://aclanthology.org/2025.coling-main.178/)：pp. 2603–2615；全文链接由该页提供。
- [R6：RC4PC](https://doi.org/10.1016/j.infsof.2026.108079)：Information and Software Technology 194, 108079；本地导航见 [BARRIENTOS_LLM_ROLE](../docs/research/BARRIENTOS_LLM_ROLE.md)。

不要使用“首次 LLM+BPC”“首次结合 LLM 与 BPMN”“首次用 Sun semantics＋LLM”
“首次考虑 condition/exception”或“结构化输出本身保证正确”等表述。
也不要通过回避引用最相近论文来制造差异。与每篇文章的比较至少交代：研究问题、
输入、中间表示、检查机制、评价单位及本文有证据的增量。

## 4. 现有实验能支撑什么

下表是本轮文档审阅所用证据快照；所有数字引用既有报告，没有新计算、新实验或状态升级。

| 证据 | 可写的事实/价值 | 必须保留的限制 |
|---|---|---|
| [Stage 2 正式报告](../outputs/reports/stage2_formal_three_method_comparison_v1.md)，C23–C25 | EStG-150 上 Rules-Only 与 LLM-SE 的同输入/Gold/评价器比较；五字段均值 0.7970 / 0.8088，字段优势各异 | 描述性结果，无整体胜者或显著性结论；均值是五字段 F1 算术均值，modality accuracy 单列；历史 Repair 只作来源，不恢复后续实验 |
| [Stage 1 v2](../outputs/reports/stage1_formal_evaluation_v2.md) | GDPR-7 的组件评价与重建；已有语义与结构结果 | 明确 post-Gold、target-aware、strict_test_blind=false；运行不读 Gold 不等于开发未见标签；结构 1.0 不是独立泛化证据 |
| [SEP-C3 四臂消融](../outputs/reports/sep_c3_modular_ablation_analysis_v1.md) | 600 次真实调用已完成；modular v1 未通过验收，旧 v6 保留；可报告该具体改写的失败 | 四臂不是完整八组合；一次失败不证明所有模块化提示都无效；0813 旧 v6 的 0.7850 不能与正式 D1 的 0.8088 混成同一批次 |
| [两方法/Oracle 衔接快照 v10](../outputs/reports/s2_13_s3_7_transition_readiness_v10.md) | 人工 Rule Records 已发布，开发面板已有 Oracle 隔离结果，可以诊断检查器瓶颈 | Direct 两批实际结果仍缺；正式主表未启动。不能写成“完全没做 Oracle”，也不能写成“正式 Oracle/端到端已经完成” |
| [四类 target-paired v2](../outputs/reports/s3_c36_target_paired_v2.md)，C41–C42 | 40 对受控面板上已记录 F1、配对成功、unknown 与 control target FP | 开发/合成/目标字段评价；control 不是全流程合规证明；Winter-style 四类基线为项目扩展，非 Winter 原生能力 |
| [Winter 共同子任务](../outputs/reports/sep_c2_stage2b_predecessor_baseline_v1.md)，C47 | 可交代前人原型到 clause-region detection 的显式适配 | clause-region 指标不是六要素抽取 F1，也不是 Sun 论文违规检测结果；不可拼接总榜 |

最稳妥的核心研究问题是：在统一法规语义表示下，传统解析和 LLM-SE 的错误如何
不同；在固定流程输入、适配与检查器下，这些差异如何影响具体判定。后半问必须等实际
成对证据形成后回答；“抽取得分更高不一定改善判定”目前只能作为待验证问题。

## 5. 会影响结论的风险与处理原则

1. **开发与独立测试边界。** 现有材料披露过 Stage 1 目标标签暴露、EStG 本地词典补充、
   prompt 迭代及同面板阈值探索。逐个最终报告交代选型、调试、人工裁决、冻结与评价时序，
   不把内部 formal 标记等同于 unseen held-out test。若只支持固定样本的描述性研究，就
   限定结论；若要泛化主张，再明确新增独立证据需求。本记录不授权重抽 EStG-150 或新实验。
2. **Gold 来源与粒度。** 披露 LLM-assisted, human-adjudicated；报告已有的人工复核
   范围、字段支持数、翻译和 clause/句子粒度。不虚构双人标注、一致性系数或法律专家资格。
3. **基线公平性。** Rules-Only 包含情态分类器，不应让读者误以为整条方法仅关键词规则；
   原作者缺失资产与未实现部分如实列出。较弱 parser、接口不兼容或选择性阈值不能包装成
   LLM 的天然优势。引用近期工作不意味着必须把所有不同任务的框架都重跑成比较臂。
4. **下游范围与可观察性。** 无证据、unknown、不适用、未映射与合规分开。
   原 33 条全为违规的 panel 不能估计 specificity；四类面板的目标字段合规不能解释为
   整个流程合规。排除 unknown 后的分数只能作为诊断，同时报告原分母与覆盖率。
5. **关联与归因。** EStG-150 的抽取分数不能直接解释 GDPR 的判定变化；必须使用同一
   条款、流程版本和评价标签的成对预测。不能把 EStG 预测接到 GDPR 后声称零 API 闭环。
   原三类检查器不自动消费 condition/constraint/exception；若要论证这些字段的下游价值，
   必须指出实际消费它们的扩展检查、适用前提和受控证据。
6. **稳定性和模块有效性。** JSON 有效不等于语义准确；单次运行/单次消融不等于稳定提升。
   已有重复或 bootstrap 证据只有在模型批次、prompt、输入与评价口径匹配时才可引用。
   接口失败臂与语义失败臂分开；不把跨 schema 零分当公平的性能差距。
7. **文献与版本。** Sun 作者稿与最终版的表号/数字不可互换；摘要未提某能力不能证明
   原论文没有该能力。近期工作的“未做某事”需全文支撑。提交前按这张文献表再核查新增近邻，
   不宣称穷尽检索或保证零重合。

## 6. 论文组织准备：不新增实验路线

沿用工作稿题名“面向自然语言合规需求的设计时业务流程检查：规则方法与大语言模型的
分阶段比较”。贡献候选分三层，完成证据与拟做工作不能混写：

- **表示与实现说明**：在继承的语义框架中适配 Rules-Only/LLM-SE，交代原文证据、
  校验、归一化与检查接口；明确采用已有技术和自行实现的部分。
- **受控实证结果**：报告同数据口径下的字段权衡和错误分布；解释变化，保留失败结果，
  不要求 LLM 全面胜出，也不把每个工程模块列为独立创新。
- **下游影响与适用边界**：以固定检查器上的成对结果区分抽取、适配、映射和可观察性
  瓶颈；在相关任务实际完成前只写研究问题与实验设计。

可采用的引言定位句（不包含尚未得到的结果）：

> 已有研究探索了基于大语言模型的法规结构化、合规问答及法规变化影响分析。本文围绕
> 继承的多粒度法规语义表示，比较传统解析与直接 LLM 解析在相同评价口径下的字段表现，
> 并研究其与固定流程检查机制之间的衔接及能力边界。

六页仅作为往届格式下的暂定篇幅预算：摘要/引言/贡献 0.75 页，相关工作 0.6 页，
问题定义与方法 1.25 页，数据/协议 0.8 页，结果/下游/错误案例 1.65 页，
局限/结论 0.35 页，参考文献 0.6 页，总计 6 页。最终依当届要求和实际版面调整。
完整技术说明保留在工作稿；会议正文优先使用一张流程图、一张主要字段表、一张同口径
下游表和一个成功/失败案例，不设必须填满的图表数量。

## 7. 接入既有任务与投稿判断条件

任务依赖、进度和时间目标仍只在主 Pipeline/实时状态页维护。本笔记为以下工作提供依据：

- SEP-C1 / PW1–PW5：把最接近的文献和借鉴边界写入引言/相关工作；先形成连贯稿件，
  不等待全部补证。全文待核的细节保留 TODO-SOURCE。
- SEP-C2 / S2.12–S2.13：按原合同补齐实际两方法证据；110 次是既有计划量，不能从本文
  推导出新授权或新的可发送状态。不恢复 Repair、Stage 3 fallback 或已撤回的复现方案。
- SEP-C4 / PW8：优先回答固定检测器下的成对差异；复用匹配的已有资产，有实际缺口才
  请求必要补证。四类扩展保持可审查的探索范围，不为扩大创新数量追加新类型。
- SEP-C5–C6 / OCT-C1–C4：持续写作、导师反馈、英文与当届格式核验；按最晚目标尽早
  完成，不新增中途强制停止实验日期，不以日期替代实验门禁。

达到以下条件时，才将稿件称为“可提交”：核心论点清楚、近邻差异有来源、每张结果表能
追溯到一致的样本/版本/评价器、核心结论无待填结果、开发/测试与合规/unknown 边界明确，
并完成导师审阅及当届投稿要求核对。若下游证据仍不足，应与导师选择诚实缩小论文主张，
或完成对应补证；不能把“下游改进”留在摘要里却用无关面板填表。
