# LLM4BPC 论文工作稿

**状态**：DRAFT — 已启动写作，但无正式实验结果（注：Stage 2 三方法正式比较已于
2026-08-11 发布，正式数字见 §7.2，按 formal manifest 定向回填；这里是命名与方法
章节的连贯工作稿）
**写作语言**：中文；技术术语保留规范英文
**主张控制**：`CLAIM_EVIDENCE_MATRIX.md`
**当前研究范围（2026-09-14 用户决定）**：后续比较使用 **Rules-Only / LLM-RE**。
Rules+LLM-Repair（`sun_llm_fallback` / H1）已退出后续全部实验；下文保留的既有
三方法表和修复组说明仅为历史研究记录，不作为当前贡献、待做对照或冻结前置条件。
本文不再安排规则先行的 LLM 修复/fallback 实验。`B0`、`D1` 只作兼容机器 ID。

## 题目（2026-09-14 SEP-C1-B 固定推荐）

**推荐中文题名**：
面向自然语言合规需求的设计时业务流程检查：规则方法与大语言模型的分阶段比较

**推荐英文题名**：
Design-Time Business Process Checking for Natural-Language Compliance Requirements: A Stage-Wise Comparison of Rule-Based and LLM-Based Approaches

**理由**：用“自然语言合规需求（natural-language compliance requirements）”覆盖法律、监管、制度和业务规则；“设计时业务流程检查”固定 BPMN 流程模型检查场景；“分阶段比较”对应 Stage 1/2/3 与 Rules-Only、LLM-RE 主线。题名不声称已经跨领域泛化。

**备选 1（中/英）**：
从自然语言合规需求到流程模型：设计时合规检查的语义解析与分阶段方法比较
From Natural-Language Compliance Requirements to Process Models: Semantic Parsing and Stage-Wise Method Comparison for Design-Time Compliance Checking

**备选 2（中/英）**：
设计时业务流程合规检查中的自然语言需求解析：规则方法与大语言模型比较
Parsing Natural-Language Requirements for Design-Time Business Process Compliance Checking: Comparing Rule-Based and LLM Methods

**范围声明**：本文方法的设计预期范围是以自然语言表述的法律、监管、制度和业务规则，输入为设计时 BPMN 流程模型；输出为 Stage 2 Rule Record 与 Stage 3 matching/violation。现有数据覆盖范围仅为项目 EStG-150（奥地利所得税法英文文本的独立重建 Gold）以及 GDPR-7/S2.11 复杂语料相关面板；这些数据不足以证明跨领域、跨语言或企业真实部署泛化。题名中的通用性仅是设计 scope，不是已验证结论。

## 摘要

设计时业务流程合规检查需要把自然语言合规需求中的规范性要求与流程模型中的活动、参与者
和控制流进行对应。这里的合规需求涵盖法律、监管、制度和业务规则文本。本文围绕
Sun et al. 提出的三阶段框架，设计一套可追溯的独立重建与扩展实验：Stage 1 解析
BPMN 流程结构和标签语义，Stage 2 从自然语言合规需求中识别
模态及 actor、action、condition、constraint、exception，Stage 3 进行规则—流程
匹配和违规类型分类。研究将比较代表性非 LLM 方法、paper-faithful Sun 重建、
LLM-RE（LLM-based Rule Extraction，基于大语言模型的规则抽取），并在预先冻结的复杂
合规语料上检验不同方法随复杂度增加的退化边界。

已落地的正式/DEV 结果（均为描述性）：Stage 1 固定 GDPR-7 复现（P2 语义
micro-F1 0.8185 / accuracy 0.6928 / triple 0.4222，structure 1.0 仅共享解析，
§7.1）；Stage 2 已发布正式比较中的 Rules-Only 与 LLM-RE 结果（无整体胜者；
LLM-RE 对 action/condition/constraint/modality label 更优，Rules-Only 对
actor/exception 更优，§7.2）；Stage 3 在人工 33 条 panel 与新增 30 条
合成受控错误 panel 上的四方法违规检测（missing_action 最易、incorrect_actor
依赖参与者语义、out_of_order 最难，§7.4）。现有数据覆盖仅为 EStG-150 与
GDPR-7/S2.11 相关面板；本文不据此声称跨领域、跨语言或企业部署泛化。

[[TODO-RESULT:S2.12：适配两方法合同后回填 Rules-Only / LLM-RE 复杂度分层结果；
Direct 36 次尚未执行，Fallback 27 次已取消，不列为待完成项。]]
[[TODO-RESULT:S3.7/S3.10：回填 Oracle 与端到端结果]]
在上述事项完成前，本摘要对 Oracle/端到端不写性能提升、最佳方法或最终结论。

## 1. 引言

法规通常以自然语言描述义务、禁止、许可、定义及其适用条件，而业务流程模型则以
活动、事件、网关、参与者和控制流表达组织行为。设计时合规检查需要跨越这两种表示
之间的语义差异：一方面从法规中恢复可计算的规范性规则，另一方面从流程模型中恢复
可匹配的行为与结构关系，最终判断流程是否缺少必要活动、由错误参与者执行活动，或
违反法规规定的先后顺序。

Sun et al. 的方法为这一问题提供了 Stage 1 流程解析、Stage 2 法规解析和 Stage 3
匹配/违规检测的完整框架。现有项目证据表明，作者完整的 Stage 2 源码、训练权重、
完整 marker lexicon 和原始 150 句 phrase Gold 并未随本项目获得。因此，本文不声称
复用作者原始实现，而以最终发表方法为来源，进行可审计的 paper-faithful independent
reconstruction。[[TODO-SOURCE:SUN2024:核对三阶段描述与方法资产页码]]

大语言模型能够直接生成结构化语义表示，但它们也可能产生 schema 违规、遗漏字段、
不稳定输出和额外调用成本。因此，本文不预设“LLM 必然更优”，而是把 LLM-RE、
不使用 LLM 的完整重建 baseline（Rules-Only）放在相同输入、Gold、输出合同和评价器
下比较。复杂法律语料是否会放大不同方法之间的差异，同样作为待检验问题，而不是
预先成立的结论。

### 1.1 研究问题

本节中的“合规需求”均指以自然语言表述的法律、监管、制度和业务规则；当前证据只覆盖 EStG-150 与 GDPR-7/S2.11 相关面板，RQ 的成立范围不自动扩展到其他领域。

- RQ0：能否完整、可追溯地独立重建 Sun 的三阶段设计时合规检查框架？
- RQ1：在固定 EStG-150 自然语言合规需求上，前人可比方法、Sun 方法级重建与
  LLM-RE 在 Stage 2 的模态分类与六要素抽取上如何比较？
- RQ2：自然语言合规需求的文本复杂度增加时，各 Stage 2 方法如何退化，
  错误类型如何变化？
- RQ3：在设计时流程模型与 Gold Rule/Process Records 下，多个 Stage 3 baseline
  在匹配和违规类型分类上如何比较；Rules-Only 与 LLM-RE 抽取误差如何影响固定检测器？
- RQ3a（2026-08-22 新增）：在人工裁决的 33 条 violation panel 之外，现有非 LLM
  Stage 3 方法（Winter、Sun、BM25、TF-IDF）在 30 条**合成受控错误**（三类各 10
  条）上分别表现如何？哪种错误类型最易/最难检测？（§7.4.2–7.4.7）
- RQ3b：Stage 1 的结构/语义标签质量如何传播到 Stage 3 的违规类型判定？（§7.4.7）
- RQ4：Stage 2 或 Stage 3 的局部改进能否转化为端到端提升？

### 1.2 预期贡献（待验证）

本文计划交付：三阶段独立重建及其可复现边界；统一 canonical contract 下的 Stage 2
多 baseline 比较（正式结果见 §7.2）；复杂法律语料上的复杂度分层与错误分析；Stage 1
描述性复现（正式结果见 §7.1）与 Stage 3 违规检测（人工 33 条 panel + 30 条合成
受控错误 panel，见 §7.4）；Stage 3 Oracle 与 end-to-end 分离评价；以及解释
Stage 2、Stage 3 和二者交互贡献的受控消融。方法层面，本文把 LLM-RE 的实现
拆分为 8 个可独立叙述与消融的模块，把 Rules-Only 拆分为 8 个模块，并逐模块与
Barrientos et al. (2026) 的直接借鉴来源做对照（见 §4、§6.6）。

**已落地（2026-08-22 论文优先主线）**：Stage 1 reproduction 完成（§7.1）；Stage 2
正式三方法比较完成（§7.2）；Stage 3 人工 panel + 合成受控错误 panel 完成（§7.4）；
S2.12 复杂语料 Direct/Fallback 为 pending authorized extension，不是论文主体阻塞
（§7.3 保留零 API arm）。

[[TODO-STATUS:S2.13/S3.7/S3.11：Stage 2/3 冻结与 Oracle/端到端完成后将“计划”改为
已完成贡献]]

## 2. 相关工作

### 2.1 设计时业务流程合规检查

[[TODO-SOURCE:WINTER2020/AGOSTINELLI2019：核对原论文并撰写]]

### 2.2 法律文本的 modality 与语义要素抽取

[[TODO-SOURCE:MICHEL2022/SLEIMI：核对数据、类别和 marker 方法]]

### 2.3 前人对照的三层范围：Sun、Winter 与本文方法

本节固定“与谁比、在什么任务上比、适配到什么程度”，不把文献报告值自动当作同条件
对照，也不因为 Stage 3 已有比较表就宣称 Stage 2 前人对照完成。

**版本基线。** 本地 `references/papers/Sun_2024_Design_time_BPC.pdf`（SHA-256
`08a26b7d4e6716eb2e07fce4f2a96420562a9eab6ecb12d8fb8ee351b297fcb2`，28 页）
是较早作者稿。项目机器合同登记的最终发表版为 DOI
`10.1007/s11227-023-05626-0`，并记录最终版方法使用 BERT-TextCNN；最终版全文当前
不在本地证据中。因此 Sun 证据分三层：本地作者稿原文（可直接核对表号与数字）；
项目登记且来自版本记录的最终版方法描述；以及
`TODO-SOURCE:SUN2024VOR：最终版期刊、表号、页码和比较结果`。本地作者稿只作
`VERIFIED_LOCAL_MANUSCRIPT`，不能替代最终版。Winter et al. (2020) 原论文全文
亦不在本地；本地有项目审计登记的原型代码和输入，Winter 原论文数字与表号保留
`TODO-SOURCE:WINTER2020`。`Winter wrapper` 与 `Winter-style four-type extension
baseline` 都是本项目重建/扩展，不能写成 Winter 原论文原生能力。

**本地作者稿可核验的 Sun 对照事实。** 情态分类比较六个 BERT 变体（Table 6）与
`CF_KW`、`CF_RNN`、`CF_CNN`（Table 7），作者稿报告本方法 P/R/F1
92.1/94.1/93.1；六要素抽取只有 Table 8 自评（P97.9/R95.3），没有前人抽取基线；
匹配只报告 AP/MAP 随 τ 变化（Table 9、Table 11），没有前人匹配基线；违规检测
只比较 Winter（Table 12：Winter 0.58/0.89/0.70，作者方法 0.77/0.83/0.80）。
最终版是否保留同一比较集合、表号和数字，必须按 `TODO-SOURCE:SUN2024VOR` 复核。

**表 2-0 Winter Stage 2B 前人基线（已回填，零 API）**

| 方法 | P | R | F1 |
|---|---:|---:|---:|
| Winter et al. (2020) 原生 clause regions | 1.0000 | 0.8312 | 0.9078 |
| Rules-Only | 0.9398 | 1.0000 | 0.9689 |
| LLM-RE | 0.9476 | 0.9740 | 0.9606 |

来源：`outputs/reports/sep_c2_stage2b_predecessor_baseline_v1.json` 与同名 `.md`
（run status `completed_zero_api_predecessor_clause_region_run`；Winter 使用本地原型
转写，Rules-Only 与 LLM-RE 复用历史正式 arm 预测，未新增 API）。

**边界（原样保留）。** 共同任务为 `estg150_clause_region_detection_v1`，只评
clause 区域交集，不是六要素抽取。Sun 作者稿 Table 12（Winter 0.58/0.89/0.70 vs
Sun 0.77/0.83/0.80）是私有 BPMN 违规任务，不可与本表直接比较。Sun 自己没有六要素
抽取的前人基线（Table 8 仅自评），Winter 不做六要素抽取。

**表 2-1 情态分类（Stage 2A）比较注册**

| 方法/版本 | 原生任务与输入→输出 | 本项目当前实现 | 可比较的共同任务与适配 | 已有结果/状态 |
|---|---|---|---|---|
| Sun 最终版（DOI 登记） | 句子级四分类 modality；规范句→label | Rules-Only 的重建使用 BERT-TextCNN + 本地锁定 checkpoint | 同一 EStG-150 modality Gold；最终版超参、权重、split 不可得，需方法级适配 | 项目内正式三方法比较已完成；与 Sun 论文值的比较仅 C3；最终版表号待核 |
| Sun 作者稿比较臂（CF_KW/CF_RNN/CF_CNN 与六个 BERT） | 同句级四分类；规范句→label | 未把这些比较臂重建为独立四分类 arm；官方 modality 数据已有开发下限探索 | 若审稿要求，需在冻结 split 上重跑同一 evaluator，才能从 C3 升为 C1/C2 | 本地 BERT-TextCNN 对论文报告值为 C3（本地 acc 0.9249/macro-F1 0.8511；作者稿报告 F1 93.1），不能作同等条件结论 |
| Winter et al. (2020) 原方法 | 四个 signal word 筛出 constraint sentence；无 modality 分类器 | 未作为独立 modality baseline 运行；wrapper 的 lexicon/句级筛选可提供透明下限 | 需把 signal words 映射到四类并显式处理 `may not` 的禁止义；否则只可作未校准下限 | 待运行；`TODO-SOURCE:WINTER2020` |
| Barrientos et al. (2026) | change-impact schema 内的 3 类 modality；复杂语料 | D/E 1140-real-call 套件，共享三类投影与模块替换 | 只有 obligation/permission/prohibition 共享；definition 不可比；跨 schema C4 | 开发表：Barrientos 原生 macro-F1 0.890，本文 3 类投影 0.822；不能作整体优劣结论 |
| 本文方法（Rules-Only / LLM-RE / Rules+LLM-Repair） | Sun 四类 label 与 evidence；规范句→canonical record 的 modality 字段 | 三条冻结 formal arms，共享输入/Gold/evaluator | 同一 EStG-150 正式比较；label 单独成表 | label acc/macro-F1：Rules-Only 0.7400/0.7128、LLM-RE 0.8333/0.7695、Repair 0.8200/0.8123；正式、描述性、无整体胜者 |

**表 2-2 六要素抽取（Stage 2B）比较注册**

| 方法/版本 | 原生任务与输入→输出 | 本项目当前实现 | 可比较的共同任务与适配 | 已有结果/状态 |
|---|---|---|---|---|
| Sun 原方法与作者稿 | CoreNLP + Tregex/Tsurgeon + marker 抽六概念；句子→phrase spans/Rule Record | Rules-Only 的方法级独立重建；公开 marker 重建；Tsurgeon 为诚实非实现并有 fail-closed 守卫 | 同一 EStG-150 六字段 Gold；原 150 IDs、443 spans、完整规则/词典不可得；本项目 clause 结构为扩展 | 项目内正式三方法比较完成；不能把该重建写成 Sun Table 8 的 C1 复现；作者稿 Table 8 是自评而非前人对照 |
| Winter et al. (2020) 原方法 | 从句切分与 signal-word 义务从句；不做 condition/constraint/exception 六要素抽取 | `winter_clause` 已有从句/义务子句能力，但未接到 EStG-150 Gold | 已运行 `estg150_clause_region_detection_v1` clause-region 子任务（P/R/F1 1.0000/0.8312/0.9078）；这不是六要素抽取，Winter 原生也不做六要素抽取 | 已运行；来源 `outputs/reports/sep_c2_stage2b_predecessor_baseline_v1.json`；仍不构成六字段 F1 基线 |
| Sleimi et al. (2018) 谱系 | phrase-level 法律语义元数据与 marker/Tregex 祖先规则 | 项目只用其公开见刊例项重建 marker lexicon，未重建完整抽取器 | 需原文数据/类别映射；否则只能作 C4 定性来源 | 未运行；`TODO-SOURCE:SLEIMI2018` |
| Michel et al. (2022) | EStG 决策规则/句子级四分类语料 | 官方 modality 数据已登记/审计；不是六要素抽取方法 | 只共享 EStG 来源与句子粒度，不能替代 phrase-level 六要素基线 | 未作为抽取 baseline 运行；`TODO-SOURCE:MICHEL2022` |
| Barrientos et al. (2026) | RC4PC：precondition/norm/change-impact；无 Sun 六字段 | 仅做模块借用与 adapter 对照；无六字段原生输出 | schema 不同；跨字段不可直接换算，禁止单 F1 总榜 | D/E 中直接替换到本文六字段接口的开发结果为 0，只能解释为接口不兼容，不能判其方法无效 |
| 本文方法 | 六字段 span + actor-action/order；规范句→Rule Record | 三方法共享 schema/normalization/evaluator | 同一 EStG-150 细/粗 Gold | 正式比较给出字段级互补，Rules+LLM-Repair 为净负对照；无整体胜者声明 |

**表 2-3 下游匹配与违规检查（Stage 3）比较注册**

| 方法/版本 | 原生任务与输入→输出 | 本项目当前实现 | 可比较的共同任务与适配 | 已有结果/状态 |
|---|---|---|---|---|
| Winter et al. (2020) 原方法 | 法规条款×BPMN 匹配；obligation/resource/sequence 三类 cost | `winter_stage3` wrapper（S3.4）；对原型 reachability 错误做披露修复 | 同一 GDPR-7 固定 panel 上比较 matching 与三类违规；原 12 个智能电表流程为 proprietary，不能恢复 | 项目 DEV：MAP 0.6429、violation macro-F1 0.373；不是 Winter 原论文数字；`TODO-SOURCE:WINTER2020` |
| Winter wrapper（本项目重建） | 原型语义转写 + 可移植重放；BPMN/条款→matching/三类 cost | `src/bpc_hybrid/winter_stage3/`，manifest/export index 固定；仅 development | 可作 Winter 风格下限与后续扩展后端；不得称原创方法 | DEV_ONLY；C36/v2 中作为 baseline 的同口径数字以 C42 为准 |
| Winter-style 四类扩展基线（本项目扩展） | prohibited/condition/constraint/exception 四类目标检查；冻结 panel→per-type 决策 | C36/Winter-style 冻结预测；`s3_c36_target_paired_v2` 统一口径 | 与当前 v5 deterministic 在同一 40 对 target-paired 面板比较；Winter 原论文没有这四类 | DEV_ONLY：Macro-F1 0.6036、pair 18/40、unknown 0.3625、control target FP 0.0750；不得归为 Winter 原生能力 |
| Sun Def 4–7 重建（S3.5） | matching + missing_action/incorrect_actor/out_of_order；规则与流程→分数/违规 | `src/bpc_hybrid/sun_stage3/`（τ/γ/θ=0.8 冻结） | 同一 GDPR-7 panel 与 33/30 条标签；正式 Oracle 尚未启动 | DEV：MAP 0.8175、violation macro-F1 0.333；阈值敏感性 v1；不得称 formal Oracle |
| Sun 作者稿 Table 12 | 报告 Winter 与其方法的 P/R/F1 | 未在本项目同数据重跑 | 原数据/实现不可得，只能作 C3 文字比较 | 作者稿 Winter 0.58/0.89/0.70，Sun 0.77/0.83/0.80；最终版表号待核 |
| BM25 / TF-IDF-SVD | 检索式 matching / 扩展后端 | 项目 development baselines | 只作同 panel 下限，不冒充前人论文原生方法 | DEV_ONLY；数值见 §7.4 与 C36 报告 |
| LLM-RE 二阶段→固定 Stage 3 | Stage 2 预测进入同一 Stage 3 的误差传播 | 尚无成对产物；可复用已冻结 Stage 2 predictions 与固定 Stage 3 | 无需新 API 的最小补证：把同一批 Stage 2 预测适配到同一 inference pack，先锁预测再评价 | 缺失；下一阶段零 API 最小任务 |
| 正式 Oracle / end-to-end | 人工 Gold Rule Records 下的 Stage 3 与两阶段组合 | 未启动、未授权 | 依赖 S2.13、Gold Rule Records、S3.4–S3.6 promotion 与单独授权 | BLOCKED；不得用现有 DEV 表替代 |

**完成、缺失与最小下一步。** 目前已完成的是：本文三种 Stage 2 方法的 formal C1
比较（同冻结输入/Gold/evaluator）；Stage 3 四类方法的 development 重建/扩展比较；
Barrientos 模块对照与稳定性套件。仍缺失的是：(1) Stage 2B 上与 Sun 六要素抽取同条件的 C1/C2 基线——目前
Winter 已完成的是 `estg150_clause_region_detection_v1` 的 clause-region 子任务，
这只评 clause 区域交集，不构成六要素抽取基线；Sun 原论文自己也没有抽取 baseline，
Winter 原生不做六要素，Sleimi/Michel 尚未接入；(2) Sun 最终版表号/数字的
`TODO-SOURCE` 核验——本地只有
较早作者稿；(3) Stage 2→Stage 3 的同法成对比较；(4) 正式 Oracle 与 end-to-end——
受上游冻结、Gold Rule Records 与单独授权约束。最小下一步只做不依赖新 API 的
适配：先把 Winter obligation-action 或公开 marker 抽取接到同一 EStG-150 Gold，
并复用冻结 Stage 2 predictions 接入固定 Stage 3；在没有产物前保持“待运行”。

### 2.4 LLM 的结构化法规表示与 Barrientos et al. (2026)

Barrientos et al. (2026) 是本文**直接借鉴的工程方法来源**，借鉴内容包括：
LLM 结构化输出、严格 JSON schema、受控词汇（controlled vocabulary）、确定性
验证与归一化、traceability，以及稳定性与评估纪律。需要严格区分三类证据：
(1) 论文正文的自动 RC4PC 方法评价——3 个场景、36 条 requirements，完整流程
独立运行 5 次，Step 1 报告 P/R/F1、strict JSON 和基于 pairwise distance≤2 的
self-consistency；(2) artifact 中的专家标注协议——“20 requirements × 2 versions
× 2 experts = 80 annotations”，Cohen’s κ=0.52 是专家对 20 个变更影响的
NC/OC/NE 判断一致性；(3) 本文拟新增的适配指标（如 style-equivalent 敏感性），
必须分表报告，不得把专家协议指标冒充论文自动实验主指标。
Barrientos 不是本文的任务/schema 主干，不能直接用其 change-impact schema 替换
Sun 六要素 Rule Record（详见 §4.4 对比表）。

[[TODO-SOURCE:BARRIENTOS2026：核对刊物/页码/表号]]

### 2.5 本文定位

本文将前人比较分为同测集重跑、官方数据复现、论文报告值和跨阶段/跨任务四级；
只有共享 frozen IDs、Gold 和 evaluator 的同测集重跑才能作为严格方法优劣证据。
与 Barrientos 的对比中，本文禁止因为任务/schema 不同，就用单一 F1 宣称“综合
上我的方法更好”；跨 schema 比较必须写明适配限制与可比较性边界。

## 3. 问题定义与总体框架

### 3.1 Stage 1：Process Record

Stage 1 把 BPMN 解析为 canonical Process Record：process/lane/pool 身份、活动
（activity/event/gateway）集合、sequenceFlow 与控制流（direct edges、reachable
pairs、activity order relations、start/end、分支/并行网关、环）。S1.7 已冻结
（2026-08-13）：固定 GDPR-7 上 7 个流程、45 个 activities、135 个人工裁决标签
字段；正式评价见 §7.1。方法语义（P0/P1/P2）见 §4.1 与 Stage 1 描述性复现
（structure micro-F1=1.0 来自共享解析组件，不构成泛化证据）。

### 3.2 Stage 2：Rule Record

Stage 2 输出统一包含 sample/clause ID、source text、modality（4 类，含 evidence
span 与 label 分离）、actor、action、condition、constraint、exception、
actor-action map、order relations 及 provenance。

### 3.3 Stage 3：Violation Report

Stage 3 输出 matching（rule→process 候选相关性）与 violation（三类）：
`missing_action`（法规义务在流程中缺失）、`incorrect_actor`（义务动作由错误
参与者执行）、`out_of_order`（顺序违反法规规定的先后）。Gold = 25 条 matching
decision Gold + 33 条 violation decision Gold（人工裁决，2026-08-08 冻结）；
验证方法包括 Winter wrapper、Sun Def 4–7 重建、BM25、TF-IDF/SVD（§7.4），
以及 2026-08-22 新增的 30 条合成受控错误 panel（§4.5/§6.4）。

### 3.4 三阶段输入/输出契约

表 3-1 把本文使用的三阶段接口固定下来。该表只描述已经冻结或已登记的实现边界，
不把开发结果写成正式结论；每个阶段保持 Gold-blind，期望标签只在评价分组时读取。

| 阶段 | 输入 | 输出记录 | 关键不变量 | 已知失败模式与本文证据 |
|---|---|---|---|---|
| Stage 1 Process Record | BPMN 2.0 XML；固定的流程/样本身份 | canonical Process Record：process/lane/pool、activity/event/gateway、sequenceFlow 与控制流关系、start/end、分支/并行、环、可达性 | 确定性解析；不读 Gold/期望标签；解析失败不补造节点；结构正确不等于语义标签正确 | 事件子流程整体成为 opaque activity，计时器/终止定义不进结构化记录；见 SIM r8 失败链（§3.5.2）与 §7.1 |
| Stage 2 Rule Record | 法规文本、固定 sample/clause ID、modality 与六要素 schema、受控词汇 | Rule Record：sample/clause ID、source text 与 evidence span、modality、actor/action/condition/constraint/exception、actor-action map、order relations、provenance | 每个字段必须有 evidence span 或显式 null；modality label 与 evidence span 分离；不因抽取失败构造 actor-action 对 | r10 的 A 组存在有效配对，但动作 span 含主体和情态词，下游动作匹配未通过阈值；condition 缺失也会使对应检查不可执行；见 §7.2 与 §3.5 |
| Stage 3 Violation Report | 同一身份下的 Process Record + Rule Record；冻结的阈值/决策规则；语义定位扩展还使用来自同一 BPMN、绑定输入身份的局部 XML 证据 | matching/violation 逐项检查：matching、missing_action、incorrect_actor、out_of_order；四类扩展 prohibited_action_present、required_condition_not_enforced、constraint_violated、exception_not_handled；evidence/coverage/unknown | 预测先固定再评价；unknown 不等于合规，也不作为负例；expected label 只用于评价分组；不从统一单标签反推四类布尔值 | 动作匹配阈值和局部 scope 不足会留下 unknown；Stage 1 表示缺失会使报警无法证实；见 SIM r8 与 §7.4 |

四类扩展的冻结合成开发面板采用 target-paired 检查：针对目标违规类型，将
variant 正例与 control 负例成对评价；control 只保证该目标类型的对照条件。
variant unknown 记入 recall 的 FN 但单独报告，control unknown 不进入已决 TNR
分母，pair success 以全部配对为分母。该口径把"未判断"与"判为合规/违规"分开，
避免把不可观测当成负例。该口径不替代 Stage 2 抽取评价、原三类违规评价或
SIM 案例的证据对应评价，各部分分别报告。

### 3.5 贯穿案例：SIM 卡入网 r10 成功链与 r8 失败链（development-only）

本节绑定同一运行 capsule：`outputs/development/sim_case_c1/run_v1/capsule.json`
（sha256 `481f068ca45562d5d6c28250284ef02e91abc1ae2cc5f4e2e8373a923af7a4ab`），
口径为 `development_case_study_not_formal_gold`。A 组是项目锁定非 LLM 基线
B0 v10a 加冻结 Sun 式三类检测；B 组复用已有真实 LLM Stage 2 预测
`OURS-FULL/repeat-01` 并投影到 v2 schema；C 组在 B 上追加 REPAIR-V2 四类扩展。
主评价单位是 r8/v2、r9/v2、r10/v2、r11/v2、r13/v2；r12 只作背景。本节不新增
API 调用，也不修改 BPMN、规则文本、Gold 或原始预测。

#### 3.5.1 成功链：r10 的动作绑定与参与者错位

Stage 1：Process Record 中存在活动 `Activate SIM card`
（`sid-D80682C2-0CD4-4B60-93BA-E9C747E28950`），其 lane 归属为 `Customer`。

Stage 2：B/C 的 r10/v2 Rule Record 给出 obligation；actor 为
`the phone company`，action 为 `... activate the SIM card`，condition 为
`When the customer receives the SIM card`，并存在有效的 actor-action pair。

Stage 3：动作解析把规则 action 映射到 `Activate SIM card`（similarity 0.8582）；
该活动的具体 owner evidence 是 `Customer`，与规则要求的 `the phone company`
不一致，因此 `incorrect_actor=violation`，score 1.0。案例评价把它判为
`found_with_reference_evidence`。A 组同样有一条有效 actor-action pair，但其动作
文本为 `, the phone company must activate the SIM card`；该文本到同一模型活动的
相似度为 0.690984，案例记录的 `incorrect_actor` 为 `undetermined`，原因为
`action_mapping_below_gamma`。因此 A 组的具体中断点是动作匹配未通过阈值。

这条链说明：Stage 2 的动作文本与有效 actor-action 配对、Stage 1 的活动归属，
以及 Stage 3 的动作匹配共同决定参与者错位检查能否执行；这是单案例机制说明，不是正式 Gold
准确率或方法优劣结论。

#### 3.5.2 失败链：r8 的超时终止语义没有进入结构化记录

Stage 2：B 的 r8/v2 Rule Record 抽取到 action `terminated`、condition
`if it takes more than 30 days for any reason`、constraint `more than 30 days`，
但没有有效 actor-action 配对（actor 为 null）。

Stage 1：案例 capsule 对原始 BPMN 的诊断字段 `process_facts.xml_counts` 显示
`timer_event_definitions=0`、`terminate_event_definitions=0`、
`event_subprocesses=0`；即使修复件在 BPMN 中新增了进程级事件子流程，
Stage 1 仍把它表示为 opaque activity，计时器起止、中断语义和 process-instance
终止范围都没有进入结构化字段。

Stage 3：missing_action 报警为 violation，B 组最优模型动作是 `Sign contract`
（similarity 0.7524），但报警没有给出真实的 30 天 bound 或 terminate label；
condition/constraint 报警也无法补上流程级作用域证据。案例评价因此记为
`machine_alarm_but_reference_correspondence_unverified`。独立结构核验确认 r8
修复的 BPMN 语义本身成立，但 `semantics_entered_detection_chain=false`，该修复件
被排除在有效修复分母之外，原因是 `repair_semantics_not_carried_by_stage1`。

这条失败链把问题定位到 Stage 1/Stage 3 的证据链，而不是把 unknown 写成不合规。
它同时说明为什么三阶段 I/O 契约必须显式记录不支持构造和无法核验的报警。

其他规则（r9 检出，r11/r13 未检出）及其逐项证据见
`paper/SIM_CASE_SECTION_v1.md`（sha256
`837e3d177903bef90f374617483074c3b0fde7659e2344d1d57efda64e00ebae`）；
本节只展开一条成功链和一条失败链。

## 4. 方法

本节把三种方法写成**细模块**。方法不是“我们调用了一个 LLM”或“我们写了一个
正则”，而是由一组可独立叙述、可单独消融的模块构成；每个模块说明它解决什么问题、
输入/输出与不变量、去掉该模块会造成什么失败、如何验证模块有效，以及它与
Barrientos 对应模块的相同点、差异点和适配理由。目标是为论文方法章节提供 4–5 页
的可写骨架（见 `MASTER_PIPELINE.md` §8.8.4）。

### 4.1 Rules-Only（纯规则法，旧代号 B0）

**一句话**：非 LLM 传统流水线——BERT-TextCNN 模态分类 + public marker 路由 +
CoreNLP 句法/依赖抽取 + Tregex/Tsurgeon 六要素规则抽取，是 Sun Stage 2 的
方法级独立重建（非 exact reproduction）。机器 ID `sun_rule_only`。

Rules-Only 拆为 8 个模块：

1. **Public marker lexicon 重建**。
   - 解决的问题：Sun 的完整私有 marker lexicon 不可得，需要一个来源可定位、
     hash 固定的受控 cue 词典来驱动标记抽取。
   - 输入/输出/不变量：输入 = 9 个公开来源的 cue（Sleimi/LexNLP/Wiktionary 等
     引证）；输出 = `public_marker_lexicon_en_v1`（5 类 64 个英文公开 marker）与
     actor 等扩展词典（v2 激活项上游）；不变量 = source/hash/版本锁定、
     development-only、禁止评测数据回流。
   - 去掉该模块会失败：condition/constraint/exception/actor 的 marker 触发层
     全部失效，抽取退化为无 cue 的启发式。
   - 如何验证：S2.3 机器门禁（来源、规则、语言、hash、空扩展表离线锁定）。
   - 与 Barrientos 对照：Barrientos 也有受控词汇（44 模式、4 维度
     control_flow/resource/data/time），但那是 change-impact 表示的规范化分类
     字典；我们的是六要素抽取 cue 词典。相同点=“用受控词汇约束输出”；差异点=
     用途（抽取触发 vs 表示分类）；适配理由=两者任务不同（六要素抽取 vs 变更影响
     表示），不能互相替代。

2. **BERT-TextCNN 模态分类**。
   - 解决的问题：为先验模态提供强监督非 LLM 基线（RQ1），也是 Sun 论文的方法主干。
   - 输入/输出/不变量：输入 = clause 文本；输出 = modality 4 类候选；不变量 =
     checkpoint/config/manifest 三重 hash 绑定、inference-only、不做 test 调参。
   - 去掉该模块会失败：模态分类只能靠 marker，非 marker 型 clause 召回显著下降。
   - 如何验证：S2.4 重建 + 锁定分类器契约测试。
   - 与 Barrientos 对照：Barrientos 没有非 LLM 分类器（直接用 LLM 输出 modality）；
     我们的分类器是 Sun-compatible 重建资产，用于与 LLM 对称比较。

3. **Marker routing 与德英 cue 验证**。
   - 解决的问题：把 modality evidence span 路由到 4 类 label，并在德（源）英
     （翻译）两侧做一致性验证，避免“伪 validated”。
   - 输入/输出/不变量：输入 = modality evidence 与 DE/EN clause 对；输出 =
     label + validated/unsupported 路由；不变量 = 无伪 validated、跨语言 cue
     验证（B0-R1-ALIGN 修复后 validated 107→49）。
   - 去掉该模块会失败：modal label 面板混淆上升（historical 79.3% 准确率中的
     路由混淆来源），路由输入不可靠。
   - 如何验证：`test_b0_r1_align_cue_validation.py` + label 面板。
   - 与 Barrientos 对照：Barrientos 无跨语言 cue 验证（英文单语）；这是我们对
     德英数据适配的必要工程。

4. **CoreNLP 句法/依赖抽取**。
   - 解决的问题：为 Tregex 树模式与 actor/action 归属提供成分/依赖解析。
   - 输入/输出/不变量：输入 = 原句；输出 = Stanford CoreNLP 4.5.10
     （tokenize/ssplit/pos/lemma/parse/depparse）结构；不变量 = 版本锁定、
     jar 身份记入 manifest。
   - 去掉该模块会失败：所有结构驱动的规则抽取（Tregex/actor 归属）无解析输入。
   - 如何验证：`test_s25_corenlp_contract.py`。
   - 与 Barrientos 对照：Barrientos 不依赖本地 DSL 解析栈（LLM 直接输出）；
     我们为 Sun Stage 2 方法级重建保留 CoreNLP。

5. **Tregex 模式注册表**。
   - 解决的问题：把语言 cue 翻译成树匹配模式，抽取六要素候选 span。
   - 输入/输出/不变量：输入 = parse tree + `sun_phrase_patterns_v3_enhanced.json`
     （六字段 28 模式）；输出 = 候选 span；不变量 = `<`/`<<` 语义有真实 bridge
     测试（B0-R1-BRIDGE）、`test_time_rule_edits_forbidden=true`。
   - 去掉该模块会失败：无结构候选产生，六要素抽取整体失效。
   - 如何验证：`test_b0_r1_bridge_semantics.py`（真实编译运行）。
   - 与 Barrientos 对照：Barrientos 无 Tregex 等价物（表示层为 LLM 结构化输出）；
     这是 Sun 特色的句法规则层。

6. **Tsurgeon fail-closed 守卫**。
   - 解决的问题：Sun 的 Tsurgeon 手术在本地是“诚实非实现”——registry 当前无
     operation、`tsurgeon_enabled=false`；守卫保证 operated 多命中 fail-closed，
     而非伪实现。
   - 输入/输出/不变量：输入 = Tregex 匹配 + (空) operation 集；输出 = 若启用则
     手术、当前关闭；不变量 = 多命中拒绝、绝不伪造手术。
   - 去掉该模块会失败：要么伪实现（造假），要么无守卫（多命中误消费）。
   - 如何验证：`test_b0_r1_bridge_semantics.py` 的 multi-match 守卫。
   - 与 Barrientos 对照：Barrientos 无 Tsurgeon 等价物（其“normalization”是
     JSON 层的确定性归一化，不是树手术）；这是已披露的适配限制。

7. **Actor/Action 归属解析**。
   - 解决的问题：把名词短语与动词短语正确归属到 actor/action 字段，避免 action
     span 吞并 constraint、漏抽多词 actor、被动句 by-agent 误归属。
   - 输入/输出/不变量：输入 = 依赖树 + actor 词典；输出 = actor/action span 与
     actor-action 候选；不变量 = 无主语开头 action（8→0）、actor R 0.958
     （B0-R1-ACTION/ACTOR 修复后）。
   - 去掉该模块会失败：字段归属错误主导（79% 的 missed Gold span 内容被抽到
     其它字段）。
   - 如何验证：`test_b0_r1_action_span_scope.py`、`test_b0_r1_actor*` + 主口径重评。
   - 与 Barrientos 对照：Barrientos 的 actor 表达在 `action.resources` 层面；
     我们把 actor 作为六要素一等公民，归属语义不同。

8. **确定性评价与可复现性资产**。
   - 解决的问题：让非 LLM 方法在共享 Gold/evaluator 下可重放、可审计。
   - 输入/输出/不变量：输入 = attempts + canonical Gold；输出 =
     `sun_literal_overlap_evaluation@2.0.0` 指标 + manifest；不变量 = 同输入
     确定性重放、粗/细 Gold 双口径、主/对照口径分表。
   - 去掉该模块会失败：方法与其它方法不可比，无法进入同一评价表。
   - 如何验证：B0-R3/R4 同进程双评、主口径与历史快照一致。
   - 与 Barrientos 对照：两者都强调 deterministic normalization 与评估纪律
     （相同点）；我们用 span overlap 主口径，Barrientos 用 Step-specific
     P/R/F1 + strict JSON 合法性 + self-consistency。

**总体结果（formal，2026-08-11 三方法正式比较，粗 Gold 主口径）**：Rules-Only
五字段 F1——actor 0.8203、action 0.8927、condition 0.7738、constraint 0.6182、
exception 0.8800，粗五字段 mean F1 0.797；modality label accuracy 0.74 /
macro-F1 0.7128。字段级约束 P/R/F1 与 modality label 分表（modality
evidence-span 在正式 Gold 中为普通字符串字段，结构性地 unavailable，不置零不
纳入 aggregate）。

### 4.2 LLM-RE（基于大语言模型的规则抽取，旧代号 D1）

**一句话**：LLM-RE（LLM-based Rule Extraction）通过提示词引导大语言模型生成同一六要素 Rule Record，不读取 Rules-Only 预测、
不读取 Gold；核心是可验证的六要素证据契约 + 锁定配方（prompt hash、model、
sampling、transport、budget）。机器 ID `direct_llm`。

LLM-RE 拆为 8 个模块：

1. **六要素 schema 与证据契约**。
   - 解决的问题：LLM 输出必须可验证——每个 evidence 都是 source 的 verbatim
     span（`text == source[start:end]`）、clause 内 span、actor-action map、
     order relations、`unsupported_or_ambiguous` 兜底。
   - 输入/输出/不变量：输入 = source_text；输出 = 满足
     `stage2_extraction_contract@1.0.0` 与 `stage2_prediction.schema@1.0.0` 的
     canonical record；不变量 = 每个 evidence 必须等于原文精确切片、子 span 必须
     位于 clause span 内。
   - 去掉该模块会失败：输出不可验证，坏 span/clause/边无法被下游检测，等于
     接受黑盒输出。
   - 如何验证：canonical validator（格式/回指/字段权限）+ 契约 hash 三方锁定。
   - 与 Barrientos 对照：相同点 = 严格 JSON schema 与验证每个 LLM 输出；差异点 =
     schema 内容不同（我们六要素 + 原文 span，他 RC4PC precondition/norms/
     temporal_validity）；适配理由 = 任务不同（抽取 Sun 六要素）。

2. **Prompt 字段定义与 v1→v6 演进**。
   - 解决的问题：constraint 字段召回弱（基线 R=0.288），主要因为“constraint
     语义未在 prompt 中显式定义，内容被并入 action/condition 或完全漏抽”。
   - 输入/输出/不变量：输入 = v1→v6 prompt 版本线；输出 = 锁定 v6
     （`direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md`，SHA-256
     3aa64877…）；不变量 = 每次变更走 “真实验证 pilot → delta 记录 → KEEP/
     REJECT”，禁止读 Gold 反向调 prompt。
   - 去掉该模块会失败：constraint R 回落到 ~0.288（99 个 constraint 内容进
     action、16 个进 condition、91 个完全未抽）。
   - 如何验证：D1-R1 的 v5→v6 配对 pilot + 150 全量：constraint R 0.288→0.417、
     Overall F1 0.7669→0.7735。
   - 与 Barrientos 对照：相同点 = prompt 中给出详细抽取指令与字段枚举；差异点 =
     我们的字段定义针对 Sun 六要素，且“空=absent”语义与“不确定入
     unsupported_or_ambiguous”是本项目合同；适配理由 = schema 不同。

3. **Gold-blind 合成 few-shot fixture**。
   - 解决的问题：低资源字段（condition/constraint/exception）需要在 few-shot 中
     展示，但又不能让测试集通过 few-shot 泄漏 Gold。
   - 输入/输出/不变量：输入 = 6 个合成样例（覆盖 condition/constraint/exception
     缺口）；输出 = Gold-blind fixture；不变量 = 与 150 测试句零交叠（S2.9 DoD）。
   - 去掉该模块会失败：低资源字段缺少正例示范，漏抽/错标上升。
   - 如何验证：`verify_d1_few_shot_fixtures.py` + Gold 不可见核查。
   - 与 Barrientos 对照：Barrientos prompt 也有示例，但没有“合成 + 与测试集零
     交叠”的 Gold-invisible 保证；这是我们的适配（数据隔离纪律）。

4. **结构化输出 transport 配方**。
   - 解决的问题：官方 deepseek-v4-pro 端点在 provider 默认 thinking 下返回空
     内容、在 json_object 下返回不同嵌套形状——需要固定可复现调用层。
   - 输入/输出/不变量：输入 = prompt + source；输出 = transport 配方
     （thinking-disabled、response_format=null、stream=false、temp 0/top_p 1/
     max_tokens 4096）；不变量 = 150/150 有效、0 事故（clean rerun）。
   - 去掉该模块会失败：结构化输出形状不稳定、事故率升高、可复现性被破坏。
   - 如何验证：D1-R1-CLEAN-RERUN / D1-R3 干净重跑（0 lost/recovery/retry）。
   - 与 Barrientos 对照：相同点 = 报告 strict JSON 合法性与稳定性设计；差异点 =
     我们的 transport 是对官方端点的实证适配（thinking 关闭、无 json_object）。

5. **Canonical validator、span canonicalizer 与确定性后处理**。
   - 解决的问题：把 LLM 输出转成结构可用、证据可回指的 Rule Record。结构适配
     负责格式转换，坐标处理负责原文定位，最终校验负责拒收残留的结构错误。
   - 输入/输出：输入 = 本次抽取原文与模型 JSON；输出 = 合法记录或明确失败，
     并附结构转换、坐标修正、元素删除和校验结果。局部坏片段、无法定位的子句及
     失效关系分别删除；记录级结构错误和最终校验失败拒收整条记录。
   - 版本：冻结正式预测使用历史唯一精确定位策略；后续 `repair_v1` 增加重复
     文本的一对一最小代价定位，不能把该改进追溯归给表 1 的既有结果。
   - 验证依据：既有固定响应后处理消融与坐标修复报告；没有重新调用模型。
     处理步骤、公式、过滤层级、示例和证据边界见 §4.2.2。
   - 与 Barrientos 的关系：沿用结构化输出、程序验证和规范化的工程思想；本文
     具体实现六要素原文回指与关系完整性检查。通过校验不等于语义分类正确。

6. **API 预算、授权与硬停止合同**。
   - 解决的问题：真实 LLM 调用必须有成本与事故控制。
   - 输入/输出/不变量：输入 = 逐批用户授权 + `--max-calls` 硬上限；输出 =
     manifest 记录 llm_calls/max_calls/模型/采样/失败率；不变量 = 无授权不调用、
     retry 需授权、无测试调参。
   - 去掉该模块会失败：成本失控、可复现性与审计缺失。
   - 如何验证：S2.9/D1-R2 预算合同（150 calls 硬上限）+ 历史运行登记。
   - 与 Barrientos 对照：Barrientos 报告成本/延迟/失败率（相同点是成本与失败
     计数纪律）；差异点 = 我们把它做成逐批授权 + 硬停止的合同（项目治理）。

7. **双口径评价与错误类型归因**。
   - 解决的问题：单一 Gold 口径会掩盖“标注粒度/定义差异”与“方法缺陷”的区别。
   - 输入/输出/不变量：输入 = 同一进程双评（细 Gold 1055 spans 对照口径、粗
     Gold 609 spans Sun 句子级主口径）；输出 = 主表 + 失败类型归因
     （matched/wrong_field/not_extracted）；不变量 = 主/对照分表、modality
     evidence-span 单独报告。
   - 去掉该模块会失败：无法区分“抽错字段”与“漏抽”，跨方法/跨口径比较失真。
   - 如何验证：D1-R3 失败类型分析（1055 gold spans：matched 732、wrong_field
     169 其中 constraint 100、not_extracted 154）。
   - 与 Barrientos 对照：相同点 = 分维报告（Step-specific P/R/F1）；差异点 =
     我们加 span-overlap + 错误类型归因；适配 = Sun 六要素 span 合同。

8. **Prompt/config/manifest hash 与可复现性资产**。
   - 解决的问题：LLM 运行的可复现性。
   - 输入/输出/不变量：输入 = prompt 磁盘文件、loader、manifest；输出 = v6
     prompt hash 三方一致（3aa64877…）、注册表
     `configs/models/estg150_d1_active_registry_v1.json`；不变量 = hash 三方
     锁定、同输入同配置重放。
   - 去掉该模块会失败：无法证明同一 prompt/模型/采样下的可重放性。
   - 如何验证：D1-R2 lock-config 测试（12 项，含 Gold 不可见核查）。
   - 与 Barrientos 对照：相同点 = temperature 0 + 稳定性设计；差异点 =
     Barrientos 论文是 36 条 requirements × 5 次完整运行报 self-consistency，
     我们已 temp0 + hash 三方锁定，同协议 5 次稳定性重跑已执行（AB-9，见 `paper/ABLATION_MATRIX.md` v3）。

**总体结果（formal，2026-08-11 三方法正式比较，粗 Gold 主口径）**：LLM-RE
五字段 F1——actor 0.7579、action 0.9437、condition 0.8380、constraint 0.7427、
exception 0.7619，粗五字段 mean F1 0.8088；modality label accuracy 0.8333 /
macro-F1 0.7695。字段级结论：LLM-RE 在 action/condition/constraint 与
modality label accuracy 领先；actor 字段落后 Rules-Only。禁止显著性推断，仅描述
性字段级比较。

#### 4.2.1 从模块组合探索到 actor/constraint 定向修补（SEP-C3 设计过程）

v6 正式比较之后，SEP-C3 先按 E（语义示例）、S（详细语义规则）、J（JSON/结构纪律）拆分 LLM-RE prompt，并用 common + E/S/J 组合检验模块化候选。2026-09-15 的真实四臂批次（111/011/101/110，各 150 条，共 600 calls）显示完整模块化新版相对 v6 明显退步，actor precision 下降，因此 `modular_v1` 未成为正式默认。该结果说明继续叠加模块不是当前最小问题；观察到的错误更集中在 actor 过度抽取和 constraint 的召回、作用范围与短语边界，而不是缺少更多总则。缺失的 000/001/010/100 四格随后在 2026-09-17 增量批执行（commit `18f5cf9`），八格每臂 150 条、failed=0、无重复发送；但前四格与增量四格不是同批交错，且每格只有一次运行，因此只能确认八格均已执行，不能据此作稳定的主效应或交互结论。

随后 SEP-C3 进入 targeted refinement，采用 common + E 作为 A，并只测试两个窄修补：

- **R_A（Actor minimality）**：要求 actor 必须是明确承担 regulated action 的责任实体；不能仅因名词短语显著，或因为它是对象、资源、金额等，就标为 actor；没有明确责任实体时返回空 actor。它要解决的是 actor 过度抽取和在空 Gold 上的 FP。
- **R_C（Constraint recall）**：要求抽取直接限定 when、how、how much、for what purpose、under what legal reference 或 with what exclusivity 的完整限制短语，而不是 `only` 等孤立 cue。它要解决的是 constraint 漏抽和短 cue overlap。

A/B/C/D 四臂为 A = common + E，B = common + E + R_A，C = common + E + R_C，D = common + E + R_A + R_C；同一批 150 条、每臂一次、共 600 calls。这里只把 R_A、R_C 当作 prompt 级行为约束来叙述，不把它们写成已经证明的模型内部机制或可跨运行推广的功能模块。A/B/C/D 数字、取舍和局限见 §6.6。

#### 4.2.2 第二阶段后处理：结构适配、原文定位与分层过滤

本节说明 Stage 2 模型生成之后、进入评价或 Stage 3 之前的处理。模型负责
判断六要素及关系；后处理程序负责统一表示、恢复已有文本的坐标和检查数据结构。
其中结构适配是直接的数据整理，冻结版本的定位是精确字符串查找，后续重复文本
定位包含明确的最小代价分配问题。以下分别描述，避免用“智能校验”概括全部步骤。

从处理流程看，模型先填写一张包含法律要素及关系的规则表；后处理把表的格式
统一，核对各项证据在原文中的位置，清除无法使用的片段或关系，再检查整条记录。
实际顺序为：**模型输出 → JSON 解析 → 结构整理 → 原文定位 → 失效关系清理
→ 最终校验 → 保存结果与处理信息**。§4.2.2.1–§4.2.2.8 给出具体规则和算法，
§4.2.2.9 用完整的合成实例逐步解释上述过程，避免读者仅凭模块名称理解方法。

##### 4.2.2.1 输入、输出、坐标与版本

输入包括执行器提供的本次抽取文本 $T$、模型返回的 JSON 内容 $R$ 和定位策略。
$T$ 是模型实际抽取的文本；对于本项目英文抽取，它指抽取时的英文输入，并非另用
德文或中文辅助文本重新匹配。后处理不读取 Gold，不读取 Rules-Only 预测，也不
新增模型调用。输出为可继续使用的 canonical Rule Record 或明确的失败记录，
以及本入口实际保存的处理信息。API 已返回、JSON 可解析、结构合法、记录非空和
语义正确是不同状态，分别统计。

片段表示为 `{id, text, start, end, normalized}`。坐标采用 Python 字符串的
零起点、左闭右开区间 $[s,e)$，必须使 `T[s:e] == text`。这里按 Unicode
字符串索引计位置，不按 UTF-8 字节数或 token 数计位置；标点与空格均参与计数。
`text` 是原文证据，`normalized` 是另一条用于后续匹配的字符串，二者职责不同。

| 对象或版本 | 定位策略与用途 | 可以归属的证据 |
|---|---|---|
| 表 1 的既有 v6/R3 正式预测 | 历史唯一精确定位；冻结后不因代码默认值改变而重处理 | 只绑定表 1 来源，LLM-RE Overall F1 0.8378 |
| D-full-0813 后处理消融 | 对固定原始响应离线重放，显式指定 `legacy` | 开发性消融，完整链报告 F1 0.7719 |
| D-full-0813 坐标修复对照 | 同一响应比较 `legacy` 与 `repair_v1` | 回顾性开发证据，不能替换表 1 |
| 当前坐标模块默认值 | `DEFAULT_POLICY = repair_v1`；历史重放入口可显式选择 `legacy` | 是代码当前行为，不是全部历史预测的处理身份 |

Prompt 的版本与后处理策略是两个独立配置，不能由“都用 v6 prompt”推断采用相同
后处理。坐标修复旧报告中“默认仍是 legacy”记述的是该次运行状态；当前源码和
后续研究记录已说明 `repair_v1` 被设为默认。本节保留这一区别，不改旧报告。

##### 4.2.2.2 JSON 解析与结构适配：简单整理部分

通用 LLM-RE 入口先去除外层 Markdown 代码围栏，再执行 `json.loads`。
不可解析的 JSON 或非对象型顶层结果作为解析失败，不以猜测补成另一条答案。
对于缺失的来源 ID、原文、schema 版本、方法信息及不确定项列表，入口使用固定
默认值补齐。该入口使用 `setdefault`：只补缺失键，不覆盖模型已提供的值。
因此“补齐元数据”本身不能写成“已核验全部来源绑定”；身份和原文绑定须依据
具体执行器或冻结来源检查，坐标模块本身也不承担该身份检查。

结构适配器逐一处理 actors、actions、conditions、constraints、exceptions：

| 输入情况 | 实际转换或处理 |
|---|---|
| 已有非空 `text` 和可用 `start/end` | 读取该平面表示并输出统一片段 |
| 外层没有可用平面表示，但含对象型 `span` | 递归展开该 `span`；不会仅从 `name` 或 `verb` 猜造证据 |
| 坐标为整数或可转整数的字符串，如 `"52"` | 转成整数；布尔值、浮点数等不按整数接受 |
| 模型使用 `actor_id`、`action_id` 等字段专用 ID | 作为统一 `id`；否则使用已有 `id` |
| 片段缺少可用 ID | 按 `<clause_id>.<field>.<原数组序号+1>` 确定性生成 |
| 可用字段片段 | 从 `text` 重新生成 `normalized = " ".join(text.casefold().split())` |
| 字段数组缺失或为 null | 转成空数组 |
| 字段值不是数组 | 转成空数组并记录该结构问题 |
| 片段不是对象、无法展开、坐标不可用或文本不在 $T$ 中 | 删除该片段并记录原因 |

适配器不替换原文 `text`，但会重新生成上述五个字段片段的 `normalized`，并在
统一片段中只保留目标键。不能把“坐标模块不改 normalized”扩写为“整个后处理
从不改 normalized”。模态证据、子句片段和顺序关系证据也不能自动套用这五个
字段的展开规则，它们由各自后续结构检查约束。

这一部分不训练模型、不推断角色，也不依据抽取质量打分。若顶层不是对象、原文
为空、`clauses` 不是数组、数组中子句不是对象，或非空 modality 不是对象，
适配失败并由调用入口拒收整条记录。后面的“删除坏子句”特指子句证据无法定位，
不能据此声称任意坏子句都只局部删除。

##### 4.2.2.3 冻结版本的原文精确定位算法

对证据文本 $u$ 和合法搜索窗口 $W=[a,b)$，候选位置集合定义为：

$$
O(u,T,W)=\{(s,s+|u|):a\leq s<s+|u|\leq b,\ T[s:s+|u|]=u\}.
$$

首先检查模型原始坐标是否满足 $0\leq\hat{s}<\hat{e}\leq|T|$，且
$T[\hat{s}:\hat{e}]=u$。满足则保留原坐标，即使相同文本还在别处出现，也不
因“有重复文本”删除它。只有原坐标不正确、确实需要重新定位时，才查找候选。
候选恰好一个时更新 `start/end`；候选为空时记为 `zero_occurrence`；候选多于
一个时，历史 `legacy` 记为 `ambiguous_occurrence` 并删除该片段。

定位顺序是先子句、后字段。子句片段在 $[0,|T|)$ 内按上述规则定位；其证据
缺失、形状不可用或无法恢复时，删除该子句及其内部内容。子句定位成功后，以其
坐标作为搜索窗口，依次处理 modality.evidence 和五个字段数组。重新搜索采用
大小写、空白、标点完全相同的匹配，不使用模糊匹配、同义词、词形还原或 Gold。

**算法 4-1：历史片段定位（用于 `legacy` 的核心步骤）**

```text
LocateLegacy(p, T, W):
    若 p 不是对象、text 为空或 start/end 不是普通整数：返回 unresolved
    若 0 <= start < end <= len(T) 且 T[start:end] == text：返回原片段
    O = 在窗口 W 内查找所有完全相同的 text
    若 len(O) == 1：仅将 start/end 改为 O 中的位置，返回片段
    若 len(O) == 0：返回 unresolved，原因为 zero_occurrence
    否则：返回 unresolved，原因为 ambiguous_occurrence
```

调用方将 unresolved 字段片段从对应数组删除，将 unresolved 子句从记录删除，
同时保留原因。这个算法是精确定位和选择规则，可以用短伪代码交代；字符串查找
本身不应作为新的语义推理算法宣传。

**实现边界。** 当前代码的“原坐标正确”分支先检查整个 $T$，并不同时检查子句
包含关系。因此，原坐标虽正确但落在所属子句之外的片段会暂时保留，最终由跨字段
校验发现；在当前入口中这可能导致整条记录被拒收。不能写成“坐标模块已删除
所有子句外片段”。顺序关系的 evidence 目前也不由该坐标模块重定位，错误由
最终校验发现。全文据此区分实际实现与理想化流程。

##### 4.2.2.4 后续改进：重复文本的一对一最小代价定位

`repair_v1` 处理的是“模型已经抽出文本，但相同文本出现多次，原坐标又有偏移”
的情况。它沿用原坐标正确时保留、唯一精确匹配时修正的规则；对于需要重定位的
重复文本，以同一子句、同一字段、完全相同文本组成候选组。子句本身仍使用历史
唯一定位，不用这套分配算法恢复重复子句；五个字段及模态证据可使用该改进。

设组内有 $n$ 个待定位预测，原坐标为 $(\hat{s}_i,\hat{e}_i)$，有 $m$ 个
尚未占用的精确匹配位置 $(s_j,e_j)$。实现先收集同一字段数组中已定位片段的
起点，将这些起点标为已占用，再为重复文本组保留剩余候选。匹配代价是：

$$
c_{ij}=|\hat{s}_i-s_j|+|\hat{e}_i-e_j|.
$$

这是两个端点的绝对距离，不是语义相似度、置信度或与 Gold 的距离。算法没有
另设“最多偏移若干字符”的阈值。以 $x_{ij}\in\{0,1\}$ 表示是否匹配，在
每个预测与每个候选位置最多使用一次、总匹配数 $K=\min(n,m)$ 的条件下求解：

$$
\min_x\sum_{i=1}^{n}\sum_{j=1}^{m}c_{ij}x_{ij},\qquad
\sum_jx_{ij}\leq1,\quad\sum_ix_{ij}\leq1,\quad
\sum_{i,j}x_{ij}=K.
$$

代码采用有上限的穷举分配，并保存所有总成本最小的方案。设其集合为
$\mathcal{A}^{*}$，对每个预测收集它在这些方案中的对应值（包括未匹配）。
**只有该预测在每个最优方案中都对应同一个实际位置，才恢复它。** 若对应值不同、
始终未匹配、没有空闲位置，或无法在计算上限内核验唯一性，则删除该预测并记录
原因。全局存在多个最优方案时，仍可保留那些在全部最优方案中对应不变的预测，
并非一律删除整组。单预测时等价于选择唯一最近位置；多预测时联合分配，避免
逐个贪心选择让同组待恢复预测占用同一个位置。

**算法 4-2：重复文本定位（`repair_v1` 新增步骤）**

```text
对当前字段数组先分类：原坐标正确、唯一精确匹配、重复精确匹配、不可定位
保留前两类，收集它们已占用的原文起点
对每个具有相同 text 的待恢复重复组：
    取得子句内未占用的精确匹配位置
    固定最大可匹配数量 K = min(预测数, 候选位置数)
    枚举一对一分配，以两端点距离之和计算总成本
    保存全部最小成本方案
    对每个预测：
        若全部最优方案均指向同一非空位置：只修正其 start/end
        否则：删除该预测，保留歧义或未匹配原因
```

计算规模也须如实说明：当 $n\leq m$ 时枚举数为 $m!/(m-n)!$；当 $n>m$
时为 $\binom{n}{m}m!$。每个方案需累加 $K$ 条匹配代价，最坏计算量随组规模
组合增长。当前估计枚举数超过 200,000 就返回无法核验，不任意选一个方案；
这不是无限规模的高效匹配实现，也不是使用了 Hungarian 算法。它适合当前小组
数据的确定性处理。该上限是计算保护，不是抽取质量阈值。

一对一约束的范围是待恢复的重复文本组，不是整个 Rule Record 的全局去重。
原本坐标正确的重复片段不会因此自动去重；相同文本可以在不同位置或字段出现。
如果重复的是 ID，仍交给最终校验拒收，不能把“重复文本”与“重复 ID”混为一谈。
可以把该步骤提炼为“基于原始坐标的一对一重复片段定位算法”，描述其输入、目标、
约束和歧义处理；目前证据支持实现与本批观察，不自动支持新的通用匹配算法或
法律语义推理创新。

##### 4.2.2.5 过滤什么、删到哪一层

过滤依据是可执行的证据与结构条件，不以 Gold 对错或模型置信度筛选样本。
实际执行顺序为解析、适配、坐标处理、关系清理、最终校验，前一步已拒收的记录
不再进入后一步。下表区分局部删除和整条拒收。

| 层级与步骤 | 触发条件 | 处理结果 |
|---|---|---|
| 顶层解析 | JSON 不可解析或顶层不是对象 | 标记解析失败，不产生成功记录 |
| 结构适配 | `clauses` 不是数组、子句不是对象，或非空 modality 不是对象 | 适配失败，调用入口拒收整条记录 |
| 字段适配 | 五个字段缺失或 null | 输出空数组，不因空而失败 |
| 字段适配 | 五个字段为非数组 | 置为空数组并记录问题；最终能否通过另行检查 |
| 字段片段 | 非对象、缺文本或可用坐标、文本不在原文 | 删除该片段，其余片段继续处理 |
| 子句定位 | `clause_span` 缺失、非对象或无法精确定位 | 删除该子句，其他子句继续处理 |
| 字段或模态证据定位 | 原坐标不正确，但在窗口内唯一匹配 | 修正坐标并保留 |
| 字段或模态证据定位 | 无精确匹配，或 `legacy` 下多处匹配无法定位 | 删除该片段；原坐标正确的重复文本仍保留 |
| 重复片段定位 | `repair_v1` 下对应不唯一、未匹配、无空闲位置或超过枚举上限 | 删除该待恢复片段，不随机选位置 |
| actor–action 关系 | 关系不是对象、actor 非 null 且不在保留 actor ID 中，或 action 不存在 | 删除该关系；actor=null 且 action 存在时允许保留 |
| 动作顺序关系 | 关系不是对象，或 before/after action ID 不在保留动作中 | 删除该关系，不根据流程或 Gold 补边 |
| 最终校验 | 重复 clause/span ID、非法模态、剩余证据坐标不一致或片段不在子句内等 | 最终报告不通过，调用入口拒收整条记录，不自动改 ID 或分类 |
| 最终校验 | 顺序关系证据不一致、越过子句或结构不合法 | 拒收整条记录，不假称该证据已完成坐标修复 |
| 空输出 | 字段为空或全部子句被局部删除，其他结构仍合法 | 可以通过结构校验；单独统计非空可用率，不能解释为正确答案 |

保留下来的关系仍是模型提出的关系，程序只检查引用是否存在；这并不证明
actor 真正执行了该 action，也不证明 before/after 在法律语义上正确。程序
校验结果由 `validate_canonical` 计算并写回，不能采信模型自报的 `validation`。

校验分两层：安装 `jsonschema` 时按 `stage2_prediction.schema.json@1.0.0`
执行 JSON Schema 检查，涵盖必需键、类型、枚举及未知键等；未安装时使用源码
中的轻量结构检查。仅在该层没有报错后，才继续检查原文切片、子句包含、全记录
ID 唯一性及关系引用。轻量路径并不等于完整 JSON Schema 覆盖，不能把未使用
完整后端的运行写成“全部 schema 约束通过”。该区别由运行入口及记录确认，本节
不推断所有历史运行使用了同一后端。

##### 4.2.2.6 合成示例：结构转换、恢复与过滤

以下均为说明用合成示例，不复制评测样本，不充当实验结果。设原文为
`The clerk must approve.`，长度为 23；`clerk` 位于 $[4,9)$，`approve`
位于 $[15,22)$，末尾句号位于索引 22。整个子句的范围为 $[0,23)$。

| 模型片段或问题 | 处理过程 | 输出 |
|---|---|---|
| `{"actor_id":"a1","span":{"text":"clerk","start":"4","end":"9"}}` | 展开 span、转换整数、统一 ID、生成 normalized；原坐标正确 | `{"id":"a1","text":"clerk","start":4,"end":9,"normalized":"clerk"}` |
| action 的 text 为 `approve`，坐标为 $[16,23)$ | 原切片为 `pprove.`，与 text 不符；子句内唯一精确匹配 | 修正到 $[15,22)$，文本、ID 和字段不变 |
| action 的 text 为 `reject`，仍给出 $[15,22)$ | 原文没有 `reject` | 删除该 action；不把 text 改成 `approve` |
| action `x1` 被删除，但关系仍为 `(a1,x1)` | action ID 不再存在 | 删除该关系；存在的其他关系保留 |
| `conditions=[]`，其余结构合法 | 没有要转换或定位的 condition 片段 | 保持空数组，不为了非空而生成条件 |

重复文本示例取自合成测试形状：`the fund must pay and the fund must pay.`。
两处 `the fund` 的正确位置为 $[0,8)$、$[22,30)$。模型给出 $[1,9)$ 和
$[20,28)$ 时，历史策略因为两处匹配而删除两个待定位片段。改进策略的代价矩阵为：

| 预测 | 候选 $[0,8)$ | 候选 $[22,30)$ |
|---|---:|---:|
| $[1,9)$ | 2 | 42 |
| $[20,28)$ | 40 | 4 |

两种完整分配的总成本为 6 和 82，因此唯一最优分配分别恢复两个位置。若只有
一个预测 $[11,19)$，它到两个位置的成本均为 22，则仍不能确定对应，删除而不
取第一个位置。候选按字符精确查找；这里没有额外的词边界过滤。因此一个短字符串
可能也匹配在更长单词内，后处理不能由“出现于原文”保证它是独立且语义正确的词。

##### 4.2.2.7 处理信息与失败如何进入评价

结构适配记录转换计数、删除片段路径和失败原因。当前坐标模块记录策略、原始
坐标、候选位置、选择位置、使用策略、距离、结果与原因；还累计重定位数、未
恢复数、删除片段/子句/关系数、重复匹配和并列最优次数。这样可以区分“模型
从未输出”与“模型已输出、后处理删除”。模块能返回这些信息，不意味着所有
历史入口都已持久化全部明细；例如通用 runner 的成功记录主要保留坐标处理信息，
结构适配还进入汇总或失败信息，其他执行器与报告另有各自保存范围。历史预测
未保存的原始内容不能从汇总中假称已经完整恢复。

在 §6.6.5 对应的固定响应消融中，150 条样本始终留在评价分母，拒收或失败
记录按空预测处理。局部删除降低可供评价的预测数量，但不会把相应 Gold 或整个
困难样本排除；合法空记录也不会被算成“模型回答正确”。解析成功率、结构成功率、
非空记录数与语义 P/R/F1 分别报告。该分母说明绑定已有消融，不自动替代其他
运行的评价合同。

##### 4.2.2.8 已有证据、方法定位与局限

固定 D-full-0813 响应的全组合消融中，完整链 F1 为 0.7719；去掉坐标处理而
保留 validator 时，149/150 条被拒收、F1 为 0.0000；同时关闭 validator 后
未重定位输出仍可被评价器部分读取，F1 为 0.5961。因此 0 分主要反映严格接口
拒收，不能写成原模型没有任何语义抽取能力。该批去掉 adapter 或 validator
分别没有分数增量，说明二者在这批上游响应上的作用，不能据此取消兼容与检查职责。

既有坐标修复开发对照将删除数从 42 降到 9，恢复 33 个模型已输出片段，其中
actor 4、action 5、constraint 7、modality evidence 17；actor FN 从 4 降到 3，
但 actor F1 从 0.6865 降到 0.6811，因为恢复内容也包含误抽。这一观察说明
“恢复原文位置”与“恢复正确法律角色”是不同任务。报告的历史 overall 为
0.7719→0.7810；其中包含历史 modality evidence-span 的评价口径，不能当作
表 1 的五字段 coarse Overall，也不能与 0.8378 直接相减或替换主表。

本模块可以作为第二阶段的原文证据定位与结构完整性处理方法完整叙述。结构适配
宜简写为字段映射和格式转换；精确定位用算法 4-1 描述；后续重复定位用算法 4-2、
目标函数、唯一性条件及开发证据单列。采用最小代价分配不等于已经证明一种新的
通用匹配算法，已有报告也未证明跨模型或跨语料稳定收益。未抽出的法律条件不会
被补出，错分字段和模态不会被纠正，原文中存在的错误角色仍可能保留；过度过滤
会损失有效预测，恢复重复文本也可能增加误报。这些限制与保留的负结果一起报告。

**本节依据（源码核对与既有报告；本次仅补全文字）**：

- [通用 LLM-RE 入口](../scripts/run_direct_llm.py)：解析、默认元数据、实际调用顺序与拒收。
- [结构适配器](../src/bpc_hybrid/d1_schema_adapter.py)：五字段展开、类型转换、ID 和 normalized。
- [坐标模块](../src/bpc_hybrid/d1_span_canonicalizer.py)：legacy、repair_v1、全部最优方案与计算上限。
- [canonical validator](../src/bpc_hybrid/stage2_canonical.py) 与 [schema](../configs/schemas/stage2_prediction.schema.json)：结构后端和跨字段检查。
- [后处理全组合消融](../outputs/reports/d_full_postprocessing_ablation_v2.md) 与 [重放入口](../scripts/run_d_full_postprocessing_ablation_v1.py)：固定 legacy、150 条分母与拒收解释。
- [坐标修复对照](../outputs/reports/d_span_grounding_repair_v1.md)、[合成测试源码](../tests/test_d_span_grounding_repair_v1.py) 与 [后续版本记录](../docs/research/D1_ACTOR_EXPLORATORY_BRANCH_2026-09.md)：恢复数量、actor 负结果及默认策略变更。测试源码作为案例依据，本次未重跑测试。
- 表 1 来源与固定规则见主张矩阵 C54；本节的方法说明与允许表述见 C55。

##### 4.2.2.9 通俗说明与贯穿实例：从模型输出到可用子句

为了说明每一步实际改变了什么，本节把后处理过程拆成十二个环节。这里的例子
用于解释程序行为，不是人工 Gold、真实模型调用或性能实验；具体实现及已有结果
仍以本节前文引用的代码和报告为依据。

| 环节 | 需要弄清楚的问题 | 具体说明 |
|---|---|---|
| 1. 取得输入 | 程序拿什么作对照？ | 本次抽取的输入原文和模型返回内容。英文抽取对照同一英文输入，不换另一语言文本寻找位置，也不读取 Gold。 |
| 2. 解析 JSON | 模型返回了内容，就算成功吗？ | 接口返回不等于结构可用。程序去除外层代码围栏后解析 JSON；解析失败或顶层不是对象，不能进入成功记录。固定元数据只补缺失项，不把补齐动作等同于来源核验。 |
| 3. 统一结构 | 这一部分是不是复杂算法？ | 展开嵌套 span、统一 ID 键、转换可用数字字符串、补编号、整理字段数组，属于确定性格式转换。normalized 从证据文字单独生成，不覆盖原文 text。 |
| 4. 检查位置 | 抽对文字为何还要处理？ | 模型可能抽出了正确短语，却数错字符位置。程序检查原文 start:end 的切片是否等于 text；位置不对时才尝试重新寻找该文字。 |
| 5. 先子句后字段 | 为何不在全文随便搜索？ | 先在全文定位子句，再在该子句内重新搜索各字段，减少跨子句错配。原坐标正确分支的包含关系仍由最终校验检查；不能声称坐标模块已提前过滤所有越界片段。 |
| 6. 历史定位 | 找不到或找到多处怎么办？ | 原坐标正确则保留；错误坐标能唯一精确匹配则修正；零匹配或无法确定的多处匹配则删除。原文没有的 reject 不会被改写成 approve。 |
| 7. 重复文本改进 | 一对一匹配具体解决什么？ | 对同组待恢复的相同文字，利用模型原起止位置计算移动距离，联合分配不同原文位置；仅恢复在所有最优分配中对应一致的片段。并列、未匹配或超过计算上限仍删除。它是后续策略，不能追溯归属表 1。 |
| 8. 清理关系 | 为什么删片段还不够？ | 片段被删除后，引用其 ID 的执行者—动作或动作顺序关系会失效；清除这些关系，不猜测替换成另一个 ID。引用存在也不证明关系的法律语义正确。 |
| 9. 最终校验 | 何时需要拒收整条记录？ | 整理后仍有非法类别、重复编号、越界证据或其他结构错误时，调用入口拒收整条记录。程序计算校验结果，不采信模型自报的通过状态；完整 schema 后端与轻量后端覆盖范围不同。 |
| 10. 空值与评价 | 空数组是不是错误？ | 空字段允许保留，程序不为了非空补答案。空值可能来自真实不存在、模型漏抽或后处理删除。已有固定响应消融保留全部 150 样本，失败按空预测处理，不移除困难样本。 |
| 11. 处理记录 | 怎么知道错误来自模型还是后处理？ | 用转换、坐标、候选、修正、删除及失败原因区分从未输出与已输出后删除。保存范围依实际入口而定，不能假称所有旧运行均有完整明细。 |
| 12. 语义边界 | 通过后处理是不是答案正确？ | 只说明记录满足已执行的证据与结构检查。字段错分、责任主体误判、模态错误、遗漏及错误顺序仍需独立评价；它们可能在结构合法时继续存在。 |

下面仍以 `The clerk must approve.` 为输入，表示“办事员必须批准”。其中
`clerk` 的位置为 `[4,9)`，`must` 为 `[10,14)`，`approve` 为 `[15,22)`，
全文长度为 23。编号只标识当前子句内的元素，供关系引用，并不是正确性分数。
以下仅展示子句层；完整记录还需其来源、方法、schema 和程序计算的 validation
等外层信息，不能把子句示例当作已通过整条记录校验的实验产物。

**假设模型给出以下原始子句。** 模型正确输出了 approve 的文字，但坐标偏移；
还额外输出了原文不存在的 reject，并建立了引用该动作的两条关系。

```json
{
  "clause_id": "c1",
  "clause_span": {"text": "The clerk must approve.", "start": 0, "end": 23},
  "modality": {
    "label": "obligation",
    "evidence": [{"text": "must", "start": 10, "end": 14}]
  },
  "actors": [
    {"actor_id": "a1", "span": {"text": "clerk", "start": "4", "end": "9"}}
  ],
  "actions": [
    {"action_id": "x1", "span": {"text": "approve", "start": 16, "end": 23}},
    {"action_id": "x2", "span": {"text": "reject", "start": 15, "end": 22}}
  ],
  "conditions": null,
  "constraints": [],
  "exceptions": [],
  "actor_action_map": [
    {"actor_id": "a1", "action_id": "x1"},
    {"actor_id": "a1", "action_id": "x2"}
  ],
  "order_relations": [
    {"before_action_id": "x1", "after_action_id": "x2", "evidence": []}
  ]
}
```

**结构整理。** 程序展开 actor/action 的 span，将 actor_id、action_id 等键统一成 id，
把 `"4"`、`"9"` 转成整数，为可用片段生成 normalized，并把 conditions 的
null 转成空数组。reject 的文字在原文中不存在，适配器在这一阶段就删除 x2。
此时其关联关系还可能暂时存在，后续关系清理再处理；不能把所有删除都归给最后
的 validator。approve 的文字确实存在，因此 x1 留下来等待坐标核对。

**坐标恢复。** 子句全文、clerk 和 must 的原坐标已正确，直接保留。approve 的
原切片 `T[16:23]` 是 `pprove.`，与模型给出的 approve 不同；在子句范围内
只有一处完全相同的 approve，故把 x1 的坐标改为 `[15,22)`。这个变化只移动
位置，没有把模型原文改写为另一答案，也没有把该片段换到其他字段。

**关系清理。** 保留元素为 actor a1 和 action x1。关系 a1→x1 的两端仍存在，
可以保留；a1→x2 引用了已删除动作，删除；x1 在 x2 之前的关系同样因 x2
不存在而删除。程序不将 x2 自动换成 x1，也不从流程模型或人工答案补出顺序。

**整理后的子句如下。** 在完整记录其余结构合法的前提下，最终校验还会检查
证据、范围、编号和引用。本例只解释片段及关系的变换，不声明某次真实运行通过。

```json
{
  "clause_id": "c1",
  "clause_span": {"text": "The clerk must approve.", "start": 0, "end": 23},
  "modality": {
    "label": "obligation",
    "evidence": [{"text": "must", "start": 10, "end": 14}]
  },
  "actors": [
    {"id": "a1", "text": "clerk", "start": 4, "end": 9, "normalized": "clerk"}
  ],
  "actions": [
    {"id": "x1", "text": "approve", "start": 15, "end": 22, "normalized": "approve"}
  ],
  "conditions": [],
  "constraints": [],
  "exceptions": [],
  "actor_action_map": [{"actor_id": "a1", "action_id": "x1"}],
  "order_relations": []
}
```

| 项目 | 模型原始内容 | 处理后内容 | 原因 |
|---|---|---|---|
| actor a1 | 嵌套 span、字符串坐标 | 平面片段、整数坐标 | 简单结构转换，原证据保留 |
| action x1 | approve 位于 `[16,23)` | approve 位于 `[15,22)` | 文字正确，唯一精确匹配恢复位置 |
| action x2 | reject | 删除 | 原文不存在，无法作为原文证据 |
| conditions | null | 空数组 | 格式统一，不生成条件 |
| a1→x2 | 引用 x2 的执行关系 | 删除 | 动作 x2 已不存在 |
| x1→x2 | 引用 x2 的顺序关系 | 删除 | 顺序关系一端已不存在 |
| modality | obligation，证据 must | 保留 | 本例证据坐标合法，程序未重新选择情态 |

对读者而言，区分修复范围比“统一过滤错误”更有用：本例修正了一处坐标，删除
一个无原文依据的动作及引用它的两条关系，并允许空条件保留。如果模型改为把
clerk 放进 constraints，文字与坐标仍可能合法；后处理没有重新决定它该属于
actor。若另有两个保留元素共用同一 ID，最终校验也不会自行改编号，而可能
拒收整条记录。局部删除、整条拒收和语义评价因此是三种不同操作。

重复文本的情况另由 §4.2.2.6 的 `the fund` 例子解释：历史策略在原坐标错误
且有两处匹配时删除待定位片段，后续策略按代价 6 与 82 选择唯一最优的一对一
分配；距离相等时仍无法确定。该步骤定位的是模型已有文字在原文中的对应位置，
并不生成新的责任主体或法律规则。距离来自模型位置偏移，不能当成语义置信度。

据此，论文对三部分工作采用不同描述：结构适配写明字段映射和类型转换；原文
定位写明查找窗口、位置选择、目标函数及歧义处理；最终校验写明结构和引用条件
及拒收范围。已有恢复数量和字段负结果说明技术定位收益与语义错误可以同时
存在。通过结构处理的记录仍需独立 Gold 评价，不能由通过状态推出法律抽取或
下游合规判断正确。

### 4.3 历史探索记录：Rules+LLM-Repair（已退出后续实验）

**2026-09-14 用户决定**：下述结果和机制仅保留为历史溯源，不属于当前方法设计或
后续对照实验；不再运行、复跑、优化、消融或新增评价，不是 S2.12/S2.13 完成依赖。

**一句话**：同一 Rules-Only，仅按预注册 trigger 让 LLM 修复失败/不确定字段；
**不作为贡献，只作为对照臂证明“无足够证据约束的选择性 LLM 修复可能产生净负
收益”**。机器 ID `sun_llm_fallback`。

**正式对照结果（2026-08-11 三方法正式比较，粗 Gold 主口径）**：Rules+LLM-Repair
五字段 F1——actor 0.4296、action 0.8945、condition 0.7774、constraint 0.6200、
exception 0.8800，粗五字段 mean F1 0.7203（vs Rules-Only 0.797、LLM-RE
0.8088）；modality label accuracy 0.82 / macro-F1 0.8123。正式结论（描述性）
confirm 该对照方法在 actor 字段 net-negative（actor F1 0.4296 vs Rules-Only
0.8203 / LLM-RE 0.7579），与 2026-08-08 停止优化决策一致。

**development 全量 150 负结果（commit 74614e3，2026-08-08，粗 Gold 主口径）**：
- 主口径 F1 0.7621 vs Rules-Only 0.7986（−0.0365 净负）；细 Gold F1 0.6875 vs
  0.7186（同样净负）；
- LLM 修复在 actor 字段过度抽取：P 0.7077→0.2754、actor spans 65→167；
- 机制本身工作正常（103 accepted / 89 changed / gate=True / 0 incidents），
  问题出在 **trigger+repair 配方增加 false positives 而非召回**。

**三个难点（可写进讨论）**：
1. **trigger 与失败错位**：trigger 只能看到推理时信号（低置信、结构冲突、候选
   多义），而 Rules-Only 压倒性失败模式是“字段归属错误”（79% 的 missed Gold
   span 内容被抽到其它字段）——这类失败在推理时不可见，Gold-blind trigger 无法
   对准真正需要修复的样本。
2. **修复难以约束在字段边界内**：请求补 actor 时 LLM 倾向扩大 span、补多个候选，
   把 precision 打穿（actor spans 65→167 的直接原因）。
3. **收益上限受限**：修复收益被触发子集覆盖限制，成本—收益不利。

**范围约束**：该探索已停止，不提出新的优化、复跑或对照实验；既有负结果不构成
当前方法贡献，不据此声称所有混合方法均无效。

### 4.4 与 Barrientos et al. (2026) 的逐模块对比表

以下表格从 15 个维度对比 Barrientos 方法与本文方法；**禁止**因任务/schema 不同就
用单一 F1 宣称“综合上我的方法更好”。（取值依据见 `docs/research/
BARRIENTOS_BORROWING_AUDIT_2026-07-12.md` 与 `docs/EVAL_3DIM_SPEC.md`。）

| 维度 | Barrientos et al. (2026) | 本文（Rules-Only / LLM-RE） | 可比较性 |
|---|---|---|---|
| 任务目标 | regulatory requirement **change-impact** analysis | Sun-compatible 六要素抽取（Stage 2）+ 后续 Stage 3 匹配 | 任务不同 → C4 跨任务 |
| schema | RC4PC：`id + precondition + norms + temporal_validity` | `modality/actor/action/condition/constraint/exception + evidence spans + maps` | schema 不同，不能照搬 |
| modality 类别 | 3 类（obligation/permission/prohibition） | 4 类（+ `definition`，Sun 主干） | 需显式扩展，不能直接照抄 enum |
| evidence span | 无独立原文 evidence span（结构化对象） | 每个要素 verbatim span（`text==source[start:end]`） | 可比较性受限（Barrientos 无 span 概念） |
| controlled vocabulary | 44 模式 × 4 维度（control_flow/resource/data/time）约束 normalized view | public marker lexicon（英文 64 个）+ 受控 six-field schema | 都是“受控词汇”纪律，用途不同 |
| JSON validation | strict JSON schema（对每个 LLM 输出验证） | canonical validator（格式/回指/字段权限） | 相同点=强验证 |
| deterministic normalization | 有（论文声明 normalization） | fail-closed canonicalizer + span canonicalizer | 相同点=确定性归一化 |
| stability design | 36 条 × 完整流程运行 5 次，Step 1 pairwise distance≤2 self-consistency | temp0 + prompt hash 三方锁定；同协议 5 次重跑已执行（AB-9 已完成，见 `paper/ABLATION_MATRIX.md` v3） | 设计对齐、已执行 |
| evaluation metrics | Step-specific P/R/F1 + strict JSON 合法性 + self-consistency | span-overlap 主口径 + 细/粗 Gold 双口径 + modality label 面板 | 主指标不同（span vs 结构化）；分表报告 |
| expert protocol | artifact：semantic coverage / structural encoding / deontic correctness + style-equivalent alignment；κ=0.52（20 个变更影响的 NC/OC/NE 一致性） | 本项目拟新增 style-equivalent 敏感性（未实现，AB-10）；Gold 为 user-adjudicated | 专家协议指标≠论文自动实验主指标，禁止冒充 |
| traceability | recording LLM 增加/修复的内容 | runner 记录 prompt/model/sampling/预算/失败率 + manifest | 相同点=traceability 纪律 |
| API/reproducibility contract | temperature 0 + 运行结果存档 | 逐批授权 + 硬停止 + prompt hash 三方 + transport 配方 | 相同点=稳定性与可复现；差异=授权治理 |
| 适合 Barrientos 的场景 | 需求变更对流程影响的自动分析、合规模式分类 | 六要素 span 抽取、Sun Stage 2/3 转写 | 各有所适 |
| 适合本文方法的场景 | Sun 六要素抽取、错误归因、复杂度分层、Stage 3 输入端 | 同上 | 任务定义决定 |
| 可否直接做数字比较 | **不能**——任务/schema/指标均不同（C4 跨任务约束） | 同左 | 只能用同一 frozen IDs/Gold/evaluator 的 C1 重跑比较 |

**综合结论（有条件）**：
- 哪些方面本文方法更好：六要素 span 回指、错误类型归因、Gold-blind few-shot
  隔离、逐批授权硬停止治理（有实现证据）。
- 哪些方面 Barrientos 更完整或更合适：change-impact 表示、44 模式受控分类、
  5 次完整运行的稳定性报告、专家 multi-dimension 标注协议（论文已实现）。
- 哪些差异来自任务定义：schema、modality 类别数、evidence span、评估单元——
  这些是任务/表示差异，不构成方法优劣。
- 哪些结论已有数据：温度 0、严格 JSON schema、确定性验证/归一化、traceability、
  成本/失败率纪律——本文 LLM-RE 已实现并有运行证据。
- 哪些已实测、哪些仍待消融：**2026-08-22 Barrientos 离线消融套件已把其中
  AB-2/AB-3/AB-5/AB-8 的前置证据做实（见 §6.6 与 `paper/ABLATION_MATRIX.md`）**；
  2026-08-29/30 真实 LLM/后处理批次已执行：D/E 套件（1140 real calls，2026-08-29）、
  450-call 严格 Prompt 单因素与后处理离线单因素（2026-08-30；AB-1/AB-2/AB-5b 严格
  臂与 AB-5 均以 `paper/ABLATION_MATRIX.md` v3 行状态与数字为准）、AB-9 五次稳定性
  重跑；仍未实现/未授权的只有 AB-4 dual-view adapter 与 AB-10 style-equivalent，
  不得把未跑项写成“已完成”。

### 4.5 实验结果对 Barrientos 模块对照的更新（2026-08-22，零 API）

§4.4 的**模块级对照现在有离线实验证据**（套件 v1，见 §6.6）：

1. **校验/确定性后处理（对应 Barrientos 的 strict-JSON）**：实验 A 显示 span
   canonicalizer 在 150 条锁定响应上重锚 966 个 span、改变/恢复 149/150 个样本
   的坐标、并带来 action 字段 F1 +0.0095（overall +0.0024）。**这回答“校验链是否
   是本文真实贡献模块”：是**——Barrientos 论文只报告 strict-JSON 合法性，不逐
   字段 re-anchor；本文的 unique exact-text re-anchor 是可测量的额外层次。
2. **受控词汇（对应 Barrientos 44 模式）**：实验 B 的 no_lexicon_extensions 显示
   去掉词典扩展（public tier 之外的本地 frozen-gap 扩展）overall F1 −0.0066，
   主要由 actor 词典扩展驱动。两边的受控词汇服务于不同表示层（six-field vs
   change-impact），不互相替代（C4）。
3. **schema 类别（4 类 vs 3 类）**：实验 C 显示 4 类覆盖比 3 类多
   definition=39 条（231 clauses 的 16.88%）；definition 是本文六要素任务中
   可度量的类别，Barrientos 的 3 类 enum 会排除它——这是 schema 覆盖差异，
   不是方法优劣。
4. **各模块去掉后的实际影响（实验 B）**：lexicon 扩展 −0.0066、modality
   classifier 在 label 口径下降（span 口径不变）、multi-match guard 首候选消费
   反而 +0.0053（副作用已披露）、actor-action 归属与 DE-EN 验证只改 label/map/
   route 不改 span 覆盖。整体结论：**本文六要素抽取的 span 覆盖主要由 lexicon +
   tregex + 校验链贡献；classifier 与 alignment 验证主要影响 modality label 质量**
   （full clause-label accuracy 0.7316；definition 类最弱 0.487）。

### 4.5 Stage 3 受控错误注入方法（synthetic_controlled_error_extension）

为把 Stage 3 从 33 条人工裁决 panel（人工 Gold）扩展到可量化错误类型的
受控实验，本文在上游冻结 GDPR-7 上构造独立、明确标记为
`synthetic_controlled_error_extension` 的合成错误注入 panel（30 条 = 三类各
10；**不是人工 Gold，不并入 33 条正式 Gold，不得冒充 Oracle**）。生成器
`scripts/build_s3_error_injection_v1.py` 实现三类最小变异，目标锁定自原始
Process Record（先锁定后运行，无任何方法结果参与选择）：

**missing_action（10 条）**：删除一个与法规义务对应的任务并在 sequence-flow
层面重接前后节点。要求：原始 BPMN 不修改；变体可解析；只产生这一个目标错误；
记录被删 activity ID、label、前后 flow；不同时制造 actor/order 错误。

**incorrect_actor（10 条）**：把目标任务的 lane/performer 映射替换为同一数据集
participant vocabulary 中的合法 actor（如 Data subject、National Authority），
通过加入命名 actor lane 并移动该任务的 flowNodeRef 实现。要求：action 文本与
控制流不变；wrong actor 来自合法词汇表；记录正确 actor、注入 actor 与目标
activity；不同时改变 action 或顺序。

**out_of_order（10 条）**：对具有明确先后义务的任务对（A before B）重接
sequence flow 使顺序逆转（f_in→B、路径首流→B、末流→A、B 的出流→A），保持
activity 集合、actor、label 完全不变，只改变目标顺序；记录原顺序、变更后
顺序与受影响 flows。

每个变体在发布前通过机器校验：XML parse、BPMN 结构校验（冻结 parser）、原始
BPMN byte-unchanged、mutation diff、exactly-one-targeted-error、非目标字段
（其余 activity/lane/order/label）不变、deterministic replay（生成器重复运行
byte-identical）。规则绑定（variant → process → rule_id）与输入 aggregate hash、
输出 aggregate hash 一并锁定在面板 manifest
`data/development/stage3_synth/synthetic_controlled_error_extension_v1.json`。
运行器 `scripts/run_s3_synthetic_panel_v1.py` 以与人工 panel 完全相同的
`evaluate_stage3_common.py` 口径对四种非 LLM 方法评分；方法无法提供的信号
明确写 `not applicable`/unobservable，不补 0 冒充支持。

### 4.6 与前人方法的机制差异和不可比边界

本文对前人的差异必须按层说明，且不得用已有 Stage 3 表替代 Stage 2 对照。

- **对 Sun 的差异是方法级重建，不是作者原实现。** Rules-Only 复现最终版公开方法
  描述中的 BERT-TextCNN、CoreNLP/Tregex、公开 marker 和抽取顺序；Tsurgeon 当前为
  诚实非实现并 fail-closed；多 clause canonical record 和 DE/EN 对齐是本项目补充。
  因此只能写 paper-faithful independent reconstruction，不能写 exact reproduction。
- **对 Winter 的差异先区分三层。** Winter 原方法是 Stage 3 的条款—流程匹配与
  obligation/resource/sequence 三类 cost；wrapper 是本项目在 GDPR-7 上的语义转写
  与 bug 披露修复；Winter-style 四类扩展基线只使用 Winter 风格相似度后端，四个
  新违规类别及其公式均由本项目定义。三者中的任何一个都不能把结果回写成原论文能力。
- **对 Barrientos 的差异是任务不同。** 本文输出 Sun 六字段 Rule Record，Barrientos
  输出 change-impact/RC4PC 表示；共同可比的只有三类 modality 投影、模块替换和
  schema 合法性/稳定性纪律，不能把跨 schema F1 排成总榜。
- **对本文三方法的差异集中在 Stage 2 抽取与下游接口选择。** Rules-Only 使用显式
  marker/句法规则，LLM-RE 使用 Gold-blind 结构化生成，Rules+LLM-Repair 只在
  预注册触发条件下修字段；三者共享同一输入、输出合同、normalization、Gold 与
  evaluator。Stage 2 的字段级差异不应直接换算成 Stage 3 或端到端提升，后者必须
  走固定 Stage 3 的成对比较。

## 5. 数据与人工 Gold

### 5.1 官方 modality 数据

官方补充材料已被定位，development schema/split 已锁定（2,831 analysis rows，
train/dev/test=1985/420/426，许可仍 unknown_pending_confirmation）。
[[TODO-STATUS:S2.1：formal use 解锁与最终行数回填]]

### 5.2 项目固定 EStG-150

项目固定唯一 150-record membership，并明确它不是 Sun 原始 150。审核采用五层
工作流，最终只能称 `LLM-assisted, human-adjudicated Gold`。150/150 已裁决并
冻结（2026-08-06 用户裁决经授权恢复验证；formal Gold 已于 2026-08-10 发布）。

[[TODO-STATUS:S2.2：回填人工审核统计和一致性/裁决说明的论文版本]]

### 5.3 复杂法律语料（S2.11）

Barrientos 3 个场景、36 条固定 IDs 的复杂语料已冻结并发布正式 Gold
（`data/gold/stage2/s2_11_complex_corpus_formal_gold_v1.json`，SHA
039ae8b2…，36/36 adjudicated、0 unresolved）。Gold 逐记录等值复制用户裁决的
canonical decisions（provenance=`deepseek_offline_proposal_v3` +
`user_batch_confirmation` by hyc），不得表述为独立专家从零标注。复杂度合同
G0.5 已冻结（`configs/g05_complexity_frozen_v1.json`）。第三方原文 local-only，
提交资产只含 hash/坐标/必要标签。

## 6. 实验设计

### 6.1 Stage 2 baseline（0.5 行改为两行）

最低覆盖：简单规则下限、一个强监督学习 baseline、完整 Rules-Only 与 LLM-RE；
各基线按 §2.3 的共同任务确定比较范围。
Rules+LLM-Repair 不再列入最低覆盖或待运行臂。模态分类（4 类 label 另表）与六要素抽取（span
P/R/F1 主表，modality evidence-span 单独/辅助）分别报告，不能用只做分类的方法
冒充完整 Stage 2。

### 6.2 Stage 3 baseline

最低覆盖：词法/检索下限、Winter、完整 Sun、一个现代 embedding/graph baseline
（TF-IDF/SVD）；后续衔接比较让 Rules-Only 与独立 LLM-RE 抽取进入同一固定
Stage 3，不再加入规则＋LLM 修复/fallback 实验。实测（2026-08-22）：
Winter wrapper（`winter_stage3_development_v1` 配方）、Sun Stage 3 重建
（`sun_stage3_development_v1`，Def 4–7）、BM25（`bm25_stage3_development_v3`）、
TF-IDF/SVD（`tfidf_svd_stage3_development_v1`）四者共享同一 inference pack、
同一 `evaluate_stage3_common.py` 评估器；在 33 条人工 panel 与 30 条合成受控错误
panel 上分别报告（§7.4）。

### 6.3 Stage 1 实验设置（描述性复现）

固定 GDPR-7（7 流程 / 45 activities / 135 语义字段人工裁决标签），构造
P0（结构基线）/ P1（简单规则）/ P2（模型上下文+依赖+style recognition）三方法，
pre-evaluation lock、无 post-evaluation tuning；metrics = 语义 micro-P/R/F1、
exact value accuracy、triple exact accuracy；仅作描述性报告，禁止 held-out
泛化声明。正式结果见 §7.1。

### 6.4 Stage 3 合成受控错误实验设置

- 面板：`synthetic_controlled_error_extension_v1`（30 变体 = MA 10 / IA 10 /
  OO 10），生成器/校验/规则绑定/aggregate hash 全部锁定（§4.5）；
- 运行：同一 evaluator、同一四个方法配方、同一阈值（development 冻结值，
  非盲预注册）；
- 报告：overall accuracy、macro-F1、per-error P/R/F1、exact match、false
  positive/negative、unobservable 数量、每类检测率、runtime、失败案例
  （详见 `s39_synthetic_panel_<method>_v1/` 与 compare capsule）；
- 纪律：样本选择不依据 Winter/Sun/BM25/TF-IDF 预测调整；合成 panel 结果
  以 DEV 标注，不并入人工 Gold。

### 6.5 指标与统计控制

Stage 2 分别报告模态分类和六字段/完整 Rule Record 指标；Stage 3 分别报告 matching
AP/MAP/Recall@k 和违规分类 P/R/F1。所有方法共享输入、Gold、schema、normalization
和 evaluator，复杂度分层在查看 test 结果前冻结。与 Barrientos 的数字比较必须
分表并标证据等级（C1–C4）。

比较前先声明层次与证据等级。Stage 2A（modality label）、Stage 2B（六要素 span）与
Stage 3（matching/violation）分表；C1 是同一 frozen IDs/Gold/evaluator 的重跑，
C2 是前人公开数据上的独立复现，C3 只抄录论文报告值，C4 是跨阶段/跨任务适配。
目前只有本项目三方法 Stage 2 formal C1 和 Stage 3 development 比较已完成；Sun
最终版原表数值仍是 C3，且最终版全文与表号待核；Winter 原方法、wrapper 与四类扩展
必须分名分表。**不得因为 §7.4 已有 Stage 3 表就写成 Stage 2 前人对照已完成**；
Stage 2B 仍缺可比的非 LLM 抽取基线，Stage 3 formal Oracle 和 Stage 2→Stage 3 的
同法成对比较仍未运行。

### 6.6 受控消融 AB-1–AB-10 与 Barrientos 消融套件（现状）

模块替换/去除矩阵的完整结构化结论见 `paper/ABLATION_MATRIX.md`。原则：
(1) 每项消融输出“我的完整模块 / 换成 Barrientos 模块 / 去掉模块 / 我的优势 /
Barrientos 优势 / 综合结论 / 可比较性限制”的结构化结论；(2) 没有正式数据时标记
“待运行”或“仅已有历史证据”，不得把“已经设计矩阵”写成“已经完成实验”；
(3) 涉及真实 LLM 的 AB-2/AB-4/AB-9 必须逐批用户授权。

**Barrientos 离线消融套件 v1（2026-08-22，零 API）已运行**（脚本
`scripts/run_barrientos_ablation_suite_v1.py`、
`scripts/run_b0_module_removal_ablation_v1.py`；结果
`outputs/development/barrientos_ablation_suite_v1/`、
`outputs/development/b0_module_removal_ablation_v1/`、
`outputs/reports/barrientos_ablation_comparison_v1.json`）：

- **实验 A（LLM-RE 校验链，锁定 D1-R3 响应）**：Full 0.7756 / Schema-only
  0.7733 / Raw-approx 0.7733（fine Gold literal-overlap v2）；canonicalizer 重锚
  966 spans、改变/恢复 149/150 样本、dropped spans 42 / edges 18；Full vs
  Schema-only Δoverall F1 +0.0024、Δaction F1 +0.0095。结论：**校验+确定性后处理
  是真实贡献模块**（坐标恢复证据充分），但 span-overlap 主口径总体增量小。
- **实验 B（Rules-Only 模块去除，同一 150/同 Gold/同 evaluator）**：full 0.7186
  （复刻锁定 v10a）；no_lexicon_extensions −0.0066；no_multi_match_guard
  +0.0053（首候选消费副作用，如实披露）；其余 span 口径 0.0（只改 label/map/
  route 不改 span 覆盖）；modality clause-label accuracy full 0.7316，
  no_modality_classifier 下降（marker-only），definition 类 0.487 为最弱。
- **实验 C（4→3 modality 投影）**：四类 39/97/62/33；三类共享 97/62/33；
  definition 覆盖率损失 16.88%；definition 不并入其它类；仅 schema 覆盖比较，
  非 Barrientos 方法性能比较。
- **实验 D/E（prompt/few-shot 与同数据比较；已于 2026-08-29 执行，共 1140
  real calls，详见 `paper/ABLATION_MATRIX.md` 实验 D/E）**：D 四臂（full /
  no-fewshot / minimal task+JSON / Barrientos-style）逐臂 parse 率为 full
  1.000、no-fewshot 0.980、minimal task+JSON 0.000、Barrientos-style 0.993。
  parse 结果须逐臂表述：no-fewshot 与 Barrientos-style 两臂**解析成功但产出零条
  非空 canonical 六字段记录**（0.980 / 0.993 的 parse ok，canonical nonempty
  均为 0.000，坐标接口/格式不匹配）；minimal task+JSON 臂 parse ok = 0.000，
  **未产出可解析 JSON**，不能把三个零分臂一概写成“可解析、仅接口不匹配”。E
  臂同批执行（同数据输入合同以 v2 为准：36 条唯一版本化 ID，派生自冻结 S2.12
  输入；原 v1“38 条非空”合同废弃，见 `paper/ABLATION_MATRIX.md`），共享/分表
  指标协议已锁定。

已锁定零 API 项：AB-1（v5→v6 历史证据：constraint R 0.288→0.417）、AB-3（4 类
→3 类投影，2026-08-22 完成）、AB-5（validator/canonicalizer 离线作用，2026-08-22
实验 A 量化）、AB-6（150/150 有效、0 事故历史证据）、AB-7（细/粗/Sun-marker 三
口径已成表）、AB-8（Rules-Only 逐模块去除，2026-08-22 实验 B 量化）。真实 LLM/
后处理批次（D/E 1140 calls，2026-08-29；450-call 严格 Prompt 单因素与后处理离线
单因素，2026-08-30）已执行，各项 AB 状态以 `paper/ABLATION_MATRIX.md`（v3）为准；
AB-4（dual-view adapter）/AB-10（style-equivalent）仍待实现/待授权。

#### 6.6.1 SEP-C3 targeted refinement A/B/C/D 同批结果（开发/探索，一次运行）

为在不增加歧义的前提下检验 actor 与 constraint 两个窄修补，SEP-C3 在固定 EStG-150、冻结 Gold、同一 evaluator 和同一模型发布批次上执行 A/B/C/D 四臂，每臂 150 条，共 600 calls；成功 600、失败 0。A = common + E，B = common + E + R_A，C = common + E + R_C，D = common + E + R_A + R_C。模型为 `deepseek-v4-pro`（登记 release `DeepSeek-V4-Pro-0813`），temperature=0、top_p=1、max_tokens=4096、retry=0、stream=false、thinking.type=disabled。

**表 6-6-1：A/B/C/D 的粗 Gold 五字段平均 F1、actor F1 与 constraint P/R/F1**

| Arm | 五字段 mean F1 | actor F1 | constraint P | constraint R | constraint F1 |
|---|---:|---:|---:|---:|---:|
| A | 0.7246 | 0.6314 | 0.8015 | 0.5556 | 0.6562 |
| B | 0.7806 | 0.7672 | 0.8102 | 0.6074 | 0.6943 |
| C | 0.7558 | 0.6807 | 0.7525 | 0.7185 | 0.7351 |
| D | 0.7858 | 0.7284 | 0.7553 | 0.7778 | 0.7664 |

数字来自既有评价和 manifest 的机器结果：`outputs/reports/sep_c3_targeted_refinement_v1_phase2_summary.json`、`sep_c3_targeted_refinement_v1_phase2_analysis.json`、`sep_c3_targeted_refinement_v1_execution.json`，以及 `outputs/development/sep_c3_targeted_refinement_v1/<arm>/repeat-01/evaluation.json`。B 的完整渲染 prompt 为 `prompts/sun_compat/modular_refinement_v1/generated/direct_llm_refinement_B_v1.md`（文件 SHA-256 `c468c631b6e454522994d6839f6a4021a259daedea7f3a2852b7b4343cd22849`，composition SHA-256 `207b54cc2f1123c7511451d7ead478654e550d438fe19d1031a13149b41917f1`）。每臂 150 条、四臂共 600 calls；这里报告的是单次开发/探索运行，不是新候选的独立盲测。

**结果解释。** R_A 有方向性收益：A→B 的 actor F1 由 0.6314 升到 0.7672，A 中 36 个空-Gold fields 有非空 actor 预测，B 降到 19。R_C 呈明显权衡：A→C 的 constraint recall 0.5556→0.7185，但 precision 0.8015→0.7525；B→D 的 recall 0.6074→0.7778，但 precision 0.8102→0.7553。B→D 另有 6 个空-Gold actor regression，均为 Gold actor 空、B actor 空、D 新增 actor，这是可观察表型，不足以单独判定模型内部原因。D 的五字段 mean F1=0.7858，高于 B 的 0.7806；但 B 的 actor F1=0.7672 高于 D 的 0.7284，且 B 只用 R_A、副作用更少。因此本轮保留 B 作为研究参照，是在简洁性、actor 表现和副作用之间做出的保守取舍，不是运行前既有的验收阈值，也不能写成"B 总分最高"或"B 已证明整体更优"。D 的较高平均分是真实观察，但同样只有一次运行，不作为本轮正式替换依据。

#### 6.6.2 Constraint recovery taxonomy 校正（AI 离线复核，不是人工 Gold）

原 recovery taxonomy 只登记 40 条比较记录 / 28 个独立样本；按冻结 Gold span 的覆盖变化重新枚举后为 **52 条比较记录 / 37 个独立 sample_id / 52 个恢复 Gold span**，其中 A→C 27 条、B→D 25 条，两个方向有 15 个样本重合，不能把跨方向重复样本当作独立证据。原 taxonomy 漏掉 12 条 / 9 个样本。原 `time=33`（A→C 17 + B→D 16，23 个独立样本）和"legal reference=0"的结论均已撤回；旧 time 正则会把数量上限中的 `to`、法律引用中的 `within`、情态动词 `may` 和年份等误归为时间。

校正后按实际新增命中片段进行多标签复核：time 14、legal_reference 12、purpose 10、quantity 8、manner 8、other 25、exclusivity 2、undetermined 1（多标签合计大于 52）。恢复完整度分为完整可解释 21 条、部分内容 29 条、仅 overlap 命中 2 条。可见 R_C 的 recall 收益分散在多个语义类型，legal reference recovery 确实存在；但很多恢复来自长 Gold 的局部 overlap，不能等同于完整语义恢复。FP 侧同样真实：A→C 未匹配预测 27→50，新出现未匹配 span 36 个、删除 13 个，净 +23；B→D 26→58，新出现 43 个、删除 11 个，净 +32，并伴随孤立 `only`、其他字段内容被重抽为 constraint 等情况。以上标签均为 **AI 离线语义复核，不是 human-approved，也不是人工 adjudication**；原人工复核标记保持不变。

#### 6.6.3 局限与未完成项

- **每臂只有一次运行。** 本表只能支持描述性/方向性判断，不能估计 run-to-run 或服务端方差，也不能据此宣布稳定优势。
- **EStG-150 已参与设计选择。** 该面板用于错误分析和 prompt 选择，不是新候选的独立盲测；仓库内部的 formal Gold 名称也不会自动赋予独立盲测资格。
- **coarse overlap 不等于完整语义正确。** 冻结评价器按同字段任意非空字符交集计算，长 Gold 可被短片段命中；完整短语质量、边界和语义类型必须与主指标分列。
- **旧 E/S/J 组合来自不同批次。** 已有 2026-08-30 Prompt 单因素和 2026-09-15 modular_v1 等分批运行；不能忽略批次效应，也不能把不同批次的最高分拼成连续提升故事。
- **B 的正式替换尚未完成。** 当前正式默认仍是 v6；B 只是本轮研究参照。R_A 的方向性收益、R_C 的 recall/FP 权衡都需要未来独立运行才能支持更强结论。
- **SEP-C3 仍未整体完成。** 完整 E/S/J 八格已执行（000-111 各一次，前批+增量批；commit `18f5cf9`），但非同批、每格一次，主效应/交互仍受批次混杂；已有原始响应的后处理归因目前只有本地分支 `9b50729` 对旧 v6 D-full-0813 与 modular 111 的局部分析，其余 arms 未覆盖；本次新增的 D-full-0813 后处理 2^3 全组合（表 6-6-3）补上了该固定响应上的三开关组合，但重复运行不确定性与其它 arms 的后处理分离仍是缺口。

#### 6.6.4 E/S/J 模块全组合提示词消融（描述性；前后两半非同批）

> **⚠️ 表 2 的最终版本在 §6.6.4.1（2026-09-21，PAPER-FINAL-REPAIR）。** 本节及以下的
> modular 家族消融**不是**表 2：表 1 的正式 LLM-RE 行用的是 monolithic v6 prompt
> （sha `3aa64877…`），而 modular 家族是另一个更小的 prompt 体系，且 9/17–20 的运行
> 把 S 与 J 关掉了（`s_included=false`、`j_included=false`）。两者不是同一个系统，
> 因此 modular 结论**不能**用来支撑或反驳表 1 的方法。本节保留为描述性研究记录。

**表 6-6-2：E/S/J prompt 模块消融（n=150/格、failed=0）**

| E S J | mean F1 | micro F1 | modality acc | 批次 |
|---|---:|---:|---:|---|
| 1 0 0 | 0.7788 | 0.8153 | 0.8133 | 新 |
| 1 0 1 | 0.7611 | 0.8144 | 0.8133 | 旧 |
| 0 1 1 | 0.7470 | 0.8032 | 0.8267 | 旧 |
| 1 1 0 | 0.7355 | 0.7970 | 0.8133 | 旧 |
| 0 1 0 | 0.7278 | 0.7991 | 0.8200 | 新 |
| 1 1 1 | 0.7262 | 0.7902 | 0.8200 | 旧 |
| 0 0 0 | 0.6367 | 0.6473 | 0.7733 | 新 |
| 0 0 1 | 0.6184 | 0.6617 | 0.7800 | 新 |
| 参考：v6 完整版 | 0.7850 | 0.8224 | — | 历史 |

来源：`outputs/reports/sep_c3_modular_ablation_v2.json`（机器指标与新旧来源绑定）、
`outputs/reports/sep_c3_modular_paired_error_attribution_v1.json`（配对诊断）、
`outputs/reports/sep_c3_modular_ablation_analysis_v1.json`（v6 历史参考）。

**同批配对诊断。** 同一新批配对为 000→100 `+0.1420`、000→010 `+0.0910`、000→001 `-0.0184`；跨批对照 100→110 为 `-0.0432`。actor 侧配对诊断按报告为修正 6 / 回退 35；另一旧批同批对照 101→111 为修正 7 / 回退 38。跨批数值只作描述性对照，不升级为因果主效应。

**必须写明的边界。**
1. 前四格与后四格非同批，跨批排名仅描述性，不作因果主效应；八格主效应/交互数字来自一次运行且受批次混杂，正式措辞保持描述性。
2. E 的全部 5 个示例与 S 规则功能重叠（来源 `outputs/reports/sep_c3_modular_prompt_overlap_audit_v1.json`）；J 仅 2 条指令，其中 1 条为公共骨架重述。
3. 默认配方保持 v6 不变；六个候选（E/S/J/R_A/R_C/R_DEF）均未晋升。

以上结果不写成「完整 prompt 更差」，不写成「E 和 S 冲突」，也不写成「JSON 约束没必要」；可支持的是：E/S/J 在同一批内呈方向性差异，且批次与功能重叠使跨批或强因果解释不成立。

#### 6.6.4.1 表 2（最终）：v6 prompt 单因素消融，与表 1 同 prompt 家族同口径

**为什么用这一套。** 表 1 的正式 LLM-RE 行由 monolithic v6 prompt
（`prompts/sun_compat/direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md`，
sha `3aa64877…`）产出。该 prompt 的严格单因素消融**已经执行**（450 次真实调用，
DeepSeek-V4-Pro-0813，temperature=0、retry=0，failed=0）。历史报告
`d1_prompt_factorial_results_v1.json` 用的是**六字段 pooled** 口径，与表 1 不可直接
比较；本节把同一批已存在的预测**离线重算**到与表 1 完全相同的口径
（`pooled_five_span_fields` + 单独 modality label），**零新增 API 调用**。

来源：`outputs/reports/stage2_table2_prompt_ablation_paper_final_v1.json`；
生成器 `scripts/build_stage2_table2_prompt_ablation_v1.py`。

**表 2：Prompt Design 消融（EStG-150 粗视图，n=150/臂）**

| Prompt 臂 | 移除的模块 | Modality macro-F1 | Actor | Action | Condition | Constraint | Exception | **Overall（pooled 5）** | Δ Overall (pp) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Full（全模块） | — | 0.754 | 0.708 | 0.919 | 0.841 | 0.758 | 0.700 | **0.8224** | — |
| Full − Examples (E) | 语义示例 | 0.763 | 0.570 | 0.912 | 0.865 | 0.762 | 0.737 | 0.8142 | −0.83 |
| Full − Guidance (S) | 详细语义规则 | 0.708 | 0.764 | 0.885 | 0.845 | 0.777 | 0.746 | 0.8299 | +0.74 |
| Full − JSON discipline (J) | 显式 JSON 契约 | 0.752 | 0.698 | 0.940 | 0.819 | 0.763 | 0.818 | 0.8268 | +0.43 |

四臂合法输出均 **150/150**。

**配对 per-sample 检验（10,000 次 bootstrap，同一 150 样本）。**

| Prompt 臂 | 平均 Δ F1 (pp) | 95% CI (pp) | CI 排除 0 |
|---|---:|---|---|
| Full − Examples (E) | +0.408 | [−2.616, +3.646] | 否 |
| Full − Guidance (S) | +2.216 | [−0.710, +5.270] | 否 |
| Full − JSON discipline (J) | +1.339 | [−0.977, +3.915] | 否 |

**结论（必须如实写，不得写成"三模块各自提升总体 F1"）：**

1. **三项删除在 pooled Overall 上都没有 CI 排除 0**，因此本消融**不支持**"每个模块都
   提升总体 F1"的阶梯叙事。
2. **可分离的字段效应符号不一致**：−E 使 Condition F1 **+4.22 pp**（CI [+1.33, +7.78]，
   排除 0），−J 使 Action F1 **+3.47 pp**（CI [+0.67, +6.80]，排除 0）。
3. **J 一律作为 Base Output Contract（接口/合法性保证）呈现，不再声称是提升准确率的
   prompt 模块**：四臂合法输出都是 150/150，删掉 J 不降低 Overall，反而 Action 略升。
4. **结构性限制必须写明**：① E 与 S 承载重叠信息（全部 5 个示例与 S 规则功能重叠），
   leave-one-out 只能测"移除另一载体后的残差"，无法隔离单模块贡献；② coarse view
   仅 459 个 Gold span，功效不足以分离小效应；③ 每臂仅 1 次重复，无 run-to-run 方差。
5. **本轮之后不再为让某模块变正而调 prompt、不再新增模块或消融臂。**

#### 6.6.5 D-full-0813 后处理 2^3 全组合消融（零 API，固定响应）

**表 6-6-3：后处理 2^3 全组合（all 150 samples in denominator）**

| 条件 | adapter | canonicalizer | validator | P | R | F1 | ΔF1 | 成功记录 | 非空记录 | 无效观察 | 拒收 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `full_postprocessing` | ✅ | ✅ | ✅ | 0.8203 | 0.7289 | 0.7719 | +0.0000 | 150/150 | 148/150 | 0 | 0 |
| `no_output_adapter` | ❌ | ✅ | ✅ | 0.8203 | 0.7289 | 0.7719 | +0.0000 | 150/150 | 148/150 | 0 | 0 |
| `no_span_canonicalizer` | ✅ | ❌ | ✅ | 0.0000 | 0.0000 | 0.0000 | -0.7719 | 1/150 | 0/150 | 149 | 149 |
| `no_canonical_validator` | ✅ | ✅ | ❌ | 0.8203 | 0.7289 | 0.7719 | +0.0000 | 150/150 | 148/150 | 0 | 0 |
| `no_adapter_no_canonicalizer` | ❌ | ❌ | ✅ | 0.0000 | 0.0000 | 0.0000 | -0.7719 | 1/150 | 0/150 | 149 | 149 |
| `no_canonicalizer_no_validator` | ✅ | ❌ | ❌ | 0.6109 | 0.5820 | 0.5961 | -0.1758 | 150/150 | 149/150 | 149 | 0 |
| `no_adapter_no_validator` | ❌ | ✅ | ❌ | 0.8203 | 0.7289 | 0.7719 | +0.0000 | 150/150 | 148/150 | 0 | 0 |
| `no_adapter_no_canonicalizer_no_validator` | ❌ | ❌ | ❌ | 0.6107 | 0.5820 | 0.5960 | -0.1759 | 150/150 | 149/150 | 149 | 0 |

来源：`outputs/reports/d_full_postprocessing_ablation_v2.json` / `.md`，脚本 `scripts/run_d_full_postprocessing_ablation_v1.py`；固定 D-full-0813 `raw_responses.jsonl`，零新增 API，完整链逐位复现锁定结果 0.7719。

**分层读法。** 有效性层由 canonicalizer 主责：去掉重锚器且保留 validator 时 149/150 记录无效并被拒收，F1 从 0.7719 掉到 0.0000；validator 关闭时未重锚记录虽可被 evaluator 部分读出（0.5961），但仍显著低于完整链。输出 adapter 在这批固定响应上没有独立 F1 增量（full 与 `no_output_adapter` 均为 0.7719），不能与 canonicalizer 并列成等价贡献。

安全网层由 validator 承担：canonicalizer 开启时去掉 validator 不改变 0.7719，是因为上游已产出合法记录；canonicalizer 关闭时 validator 拒收 149 条无效记录，把未校验原始输出挡在指标之外。因此二者是「有效性层」与「安全网层」的不同职责，不是三个模块的等价贡献。三模块全关时原始模型输出直接进入 evaluator：本批未因形状抛错；若抛错，只将对应记录记为失败并保留在同一分母，不做修补或回填。

## 7. 结果

### 7.1 Stage 1 正式复现结果（FORMAL，2026-08-13 冻结；描述性，非 held-out）

来源：`outputs/reports/stage1_formal_evaluation_v2.json`（status=
claim_corrected_numbers_locked；numeric body
`data/results/stage1_formal_v1/stage1_formal_evaluation_v1.json`，SHA
a072db39…；claim：post-Gold、target-aware Sun/Leopold-style method-level
reconstruction with Gold-isolated inference、pre-evaluation lock、no
post-evaluation tuning）。固定 GDPR-7：7 个流程、45 个 activities、135 个
semantic-field 人工裁决标签。

**表 1：Stage 1 三方法正式结果（固定 GDPR-7，描述性）**

| 方法 | 语义 micro F1 | Accuracy | Triple 准确率 |
|---|---:|---:|---:|
| P0（structural baseline） | 0.0000 | 0.0000 | 0.0000 |
| P1（简单规则） | 0.5956 | 0.4241 | 0.0000 |
| P2（模型上下文+依赖+style recognition） | 0.8185 | 0.6928 | 0.4222 |
| structure micro F1（共享解析组件） | 1.0000 | — | — |

- **P0 为什么不能恢复语义**：P0 只做结构转换（BPMN → Process Record 的活动/事件/
  网关/流骨架），不附加任何标签语义；135 个语义字段全部未填充（precision/recall/F1
  全 0）。它验证的是解析管线本身，而不是语义抽取。
- **P1 为什么有明显提升但组合仍然弱**：简单规则利用公开 marker/依存模板可恢复
  actor/action/condition 的**词面**语义（语义 micro-F1 0.5956、Accuracy 0.4241），
  但三元组（actor–action–object）需要跨字段一致对齐；P1 的 triple exact=0，
  说明字段间组合（谁对谁做什么）没有被规则层保证。
- **P2 为什么有效**：P2 引入模型上下文（BERT 表示）、依赖结构和 style recognition
  （label-style 信号），把词面规则升级为上下文感知的字段分配，语义 micro-F1
  0.5956→0.8185、Accuracy 0.4241→0.6928、triple 0→0.4222。
- **structure micro-F1=1.0 的读法**：来自共享解析组件（全部方法共用），只证明
  BPMN→记录结构的转换无错，**不能作为外部泛化证据**（见 §7.4.7 误差传播）。
- **边界**：这是 fixed GDPR-7 上的描述性复现（formal descriptive component
  evaluation）；held-out generalization claim 被明确禁止（eval v2 claim:
  held_out_generalization_claim_allowed=false、target_labels_seen_during_
  development=true、developer_blind=false）。不再为 Stage 1 增加新方法或新门禁。

Stage 2 正式两方法主表及来源绑定见 §7.2；modality label 与五字段 span 指标分列。

### 7.2 Stage 2 正式两方法主比较（最终采用值于 2026-09-26 固定）

**最终论文采用值：LLM-RE Overall F1 = 0.8378，Sun 方法本地重建
Rules-Only = 0.7631，绝对差 +7.47 个百分点。** 采用既有
`outputs/reports/stage2_table1_paper_final_v1.json` 的五字段 pooled 口径，绑定
原 `direct_llm_formal_arm_v1`（v6/R3）与 `b0_formal_arm_v1`；用户已决定此表
后续不再替换或重跑。数值、计数及来源哈希复核见主张矩阵 C54。

历史字段级正式来源（2026-08-11）：`outputs/reports/stage2_formal_three_method_comparison_v1.json`
（report SHA c9d76544…，manifest dc41eb4b…）；G0.4 授权口径：句子级粗 Gold
五字段 span 主视图 + modality four-class label 分表；modality evidence-span
结构性地 unavailable（不置零不纳入 aggregate）；细 Gold 为诊断/对照；
历史六字段 aggregate 仅 development provenance 不混入。数据规模 150 句；
历史真实调用（含 Rules+LLM-Repair 对照 arm）300、本轮新增 0。

**5 字段 span 主视图（粗 Gold，F1）**

| 方法 | actor | action | condition | constraint | exception | **五字段 pooled F1（合同口径 Overall）** | 五字段 mean F1（次口径） | Modality label acc / macro-F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Sun 方法本地重建（Rules-Only，B0） | 0.8203 | 0.8927 | 0.7738 | 0.6182 | 0.8800 | 0.7631 | 0.7970 | 0.7400 / 0.7128 |
| LLM-RE（旧代号 D1） | 0.7579 | 0.9437 | 0.8380 | 0.7427 | 0.7619 | **0.8378** | 0.8088 | 0.8333 / 0.7695 |

**Overall 口径（2026-09-21 修正，PAPER-FINAL-REPAIR）。** G0.4 合同规定正式主报告为
「粗粒度五个 span-bearing 字段 + 单独的四类 modality label 指标」，且 modality
evidence span「不可用、绝不置零、绝不聚合」。修正前 `evaluate_span_metrics.overall`
把 modality span 一并聚合，而该 span 在 coarse view 中是用 clause span **合成**的
（已发布 Gold 的 modality 是纯字符串，evidence 为空），既违约又混入近常数项。
现以 `pooled_five_span_fields`（仅 actor/action/condition/constraint/exception 的
micro pooled P/R/F1）为**唯一合同口径 Overall**：Rules-Only **0.7631**（P 0.6984 /
R 0.8410）vs LLM-RE **0.8378**（P 0.8695 / R 0.8083），**Δ +7.47 pp**。
旧的六字段 aggregate 降为显式 `NON_CANONICAL` provenance 字段，不得再作 Overall。

**表注必须写清**：Overall 只聚合五个 span 字段；modality 是四类 **label** macro-F1，
单列且绝不并入 Overall。

**必须同时承认的两点**：① pooled F1 下 **Rules-Only 的 recall（0.8410）高于
LLM-RE（0.8083）**，且 Ours 并非全面领先——actor（−6.24 pp）与 exception
（−11.81 pp）仍低于 Rules-Only；② 五字段 **mean** 口径下 Δ 仅 **+1.18 pp**，远小于
pooled 的 +7.47 pp。两个口径由同一批预测算出，只因聚合方式不同而不同，因此
**必须同时报告 pooled（主）与 mean（次）**，只报 pooled 会被质疑为口径挑选。

**约束字段的定义敏感性**（`outputs/reports/stage2_gold_definition_audit_v1.json`）：
本项目 constraint 定义明显宽于 Sun 的 marker 定义（302 条中 55.0% 不属任何 Sun marker
类、仅 37.7% 属某类）。把 constraint 收敛到 Sun marker span 后重算，**总体优势仍然为正**
（+5.74 pp 仅显式 quantity/time/comparison 措辞；+6.65 pp 另允许裸数字），但
**constraint 字段优势从 +12.45 pp 缩到 +2.14 / +7.98 pp** → constraint 必须写成
**定义敏感**并给区间，不得只报单个大数。比较对象必须写明是
**本项目 Sun-style rules 臂在本项目更宽的 Gold 定义上评分**，不是 Sun 自己报告的数字。

字段级结论（描述性，禁止显著性推断）：LLM-RE 在 action（+0.051）、condition
（+0.064）、constraint（+0.125）与 modality label accuracy（0.8333 vs 0.7400）
领先 Rules-Only；Rules-Only 在 actor（+0.062）与 exception（+0.118）领先
LLM-RE。历史 Rules+LLM-Repair 因 actor 过度抽取而 net-negative（actor F1 0.4296，
vs Rules-Only 0.8203 / LLM-RE 0.7579），保留为历史研究记录。
**本表支持固定数据上总体 F1 更高的描述性结论，不支持全面或普遍优越的声明。**

### 7.3 复杂度分层与错误类型（S2.12，零 API arm）

复杂语料（S2.11，36 条固定 IDs）上 Rules-Only 零 API arm（B0 v10a、CPU、0
API/0 network、cost=$0）：overall modality accuracy / macro-F1 = 0.638889 /
0.535461；五字段 span P/R/F1 = 0.862319 / 0.802721 / 0.831453；L1=31、L2=5、
L3=0（无样本，不报性能）。这是**单一 zero-API arm**，不是两方法比较。Rules+LLM-Repair 已按用户
2026-09-14 决定退出后续实验，其 F-1/F-2/F-3 共 27 次取消且不挪用；不会再有该臂的
复杂语料评价。当前两方法合同只等待 LLM-RE 的 36 次（D-CAL=1、D-REST=35）真实
预测、评价和与 Rules-Only 的同口径比较；Direct 未运行前 S2.12/S2.13 明确未完成。
合同与命令绑定见 `outputs/reports/s2_12_two_method_contract_v1.json`。

[[TODO-RESULT:S2.12：LLM-RE 真实 36 次完成后，回填 Rules-Only vs LLM-RE
复杂语料同口径比较与 S2.12 完成记录；不得等待或重跑已取消的修复组]]

### 7.4 Stage 3 违规检测：配对合规 benchmark（主）与原 33 条 panel（已废止）

#### 7.4.1 两个独立评价面板

**人工裁决 panel（正式，2026-08-08 冻结）**：`data/gold/stage3/stage3_violation_gold_v1.json`
（SHA `039ae8b2…`，33 条）= 人工裁决的 violation type/evidence Gold：
missing_action 11 / incorrect_actor 11 / out_of_order 11（11 个 process-rule 对 × 3
类）。这是**人工 Gold**，用于论文正式 Stage 3 表格。

**合成受控错误 panel（DEV，2026-08-22）**：`data/development/stage3_synth/
synthetic_controlled_error_extension_v1.json`（`synthetic_controlled_error_extension`
面板，30 条 = missing_action 10 / incorrect_actor 10 / out_of_order 10）。生成器
`scripts/build_s3_error_injection_v1.py` 在冻结 GDPR-7 上做**最小受控变异**：
missing_action = 删除一个与法规义务对应的任务并重接 sequence flow（保留被删
activity ID/label/前后 flow；仅一个目标错误）；incorrect_actor = 把目标任务移到
同一数据集 participant vocabulary（如 Data subject/National Authority）中新的
actor lane（action 文本与控制流不变）；out_of_order = 对具有明确先后义务的任务
交换 sequence flow 末端使其顺序逆转（activity 集合、actor、label 均不变）。每个
变体通过 XML parse、结构校验、源 BPMN byte-unchanged、mutation diff、exactly-one-
targeted-error、非目标字段不变与 deterministic replay 检查；规则绑定自冻结
inference pack；生成器重复运行 byte-identical。**该 panel 不是人工 Gold，不得并入
33 条正式 Gold，也不得冒充 Oracle**；全部结果以 DEV 标注。

**新增四类的选择动机（S3.9-EXT，DEV，2026-08-31）**：原三类只回答“必需
动作是否存在、执行者是否正确、顺序是否正确”，主要消费 action、actor 与 order
信息；它们无法判断一个流程是否执行了**被禁止的动作**，也无法判断正确动作是否
满足其**适用条件、限制约束和例外处理**。因此，扩展不是任意增加标签，而是按照
“未被 Stage 3 消费的 Rule Record 字段”选择四个最小、互不替代且可由 BPMN 表面
证据验证的违规族：

| 新违规类型 | 选择理由 | 使用的 Rule Record/BPMN 证据 |
|---|---|---|
| prohibited_action_present（出现禁止动作） | 补足 missing_action 只覆盖“应做而未做”的遗漏错误；即使必需动作、actor 和顺序全部正确，流程仍可能“做了不该做的事” | prohibition modality + action；activity/event label |
| required_condition_not_enforced（必需条件未落实） | 法律义务常有适用条件；动作本身存在并不等于只有在合法条件下才执行 | condition + action；gateway、conditionExpression、sequence-flow label |
| constraint_violated（约束被违反） | 动作、actor、顺序均正确时，仍可能违反期限、数量、用途或使用限制 | constraint + action；timer、data object、annotation 等 |
| exception_not_handled（例外未处理） | 正常路径可以合规，但流程可能缺少法规要求的例外分支或处理器 | exception + action；boundary/error event、alternate branch、handler activity |

四类的共同选择原则是：（1）补齐六要素的下游字段覆盖；（2）在原三类全部通过时
仍可能独立发生，语义上不重复；（3）可构造 exactly-one-error 的受控 BPMN 变异；
（4）对应明确的 BPMN 可观察表面，缺少表面时诚实记为 unobservable。该集合是
**最小字段覆盖扩展，不是穷尽性的法律违规分类体系**；40 条结果保持 DEV_ONLY，
不改变冻结的三类人工 Gold，也不把正式 Oracle 改称七类 benchmark。

#### 7.4.2 表 3：原 33 条人工裁决 panel（**已废止，仅作历史**）

> **⚠️ 本节数字已废止，不得再作为表 3 使用（2026-09-21，PAPER-FINAL-REPAIR）。**
>
> 该 33 条 panel 的 `decision_violation_type` **逐字复制** `check_type`（33/33），
> `decision_evidence` 为模板问句，**没有任何 BPMN 变异记录**——它是 check-point
> 决策集，不是性能 benchmark；且它只含违规正例（`none_gold_items: 0`），
> precision/specificity 无分母。
>
> 替代物：**配对合规 benchmark**（`stage3_paired_benchmark_v1`，60 items = 30 control
> + 30 variant，anti-degeneracy 30/30 PASS）。新表见 §7.4.3。新表报告
> per-type P/R/F1、Macro-F1、Micro-F1 **与 compliant specificity**。
> 复现：`scripts/build_stage3_paired_benchmark_v1.py`、
> `scripts/run_stage3_grounded_checker_v1.py`、
> `scripts/run_stage3_predecessors_paired_v1.py`；诊断见
> `docs/research/STAGE3_TABLE3_VIABILITY_DIAGNOSIS_2026-09-21.md` 与
> `docs/research/STAGE3_OURS_ARM_FEASIBILITY_2026-09-21.md`。
>
> 下表保留仅为 provenance；**引用时必须标注为已废止**。

| 方法 | 总体检测 F1 | 检出数 |
|---|---:|---:|
| Winter wrapper | 0.5000 | 11/33 |
| Sun 重建 | 0.5333 | 12/33 |
| BM25 | 0.5000 | 11/33 |
| 本文（TF-IDF/SVD 后端） | 0.6531 | 16/33 |

来源：`outputs/reports/s35_sun_stage3_development_v2/comparison_all_methods_dev.json` 以及
`outputs/development/s34_winter_stage3_development_v3_clean/`、
`s35_sun_stage3_development_v2/`、`s36_bm25_stage3_development_v3/`、
`s36_tfidf_svd_stage3_development_v2/` 的 evaluation.json；同一
`evaluate_stage3_common.py` 口径，固定 33 条人工裁决 panel。

#### 7.4.3 表 3（新）：eligibility-audited paired compliance benchmark

**Benchmark**：`data/development/stage3_synth/stage3_paired_benchmark_v1.json`。
每个变异 BPMN 与同一流程的冻结未变异 BPMN 配对为 compliant control；variant 的绑定
由 `stage3_binding_reference_v1.json` 分离保存，inference 侧不可见。eligibility
audit 为 `stage3_paired_benchmark_eligibility_v1.json`。

**Eligibility 结果**：原 30 对中，human-approved 且绑定完整者
missing_action 8 对、incorrect_actor 5 对；out_of_order 10 对全部
`ineligible_no_rule_order`，因为供应 Rule Record 没有明确规则侧先后关系。
因此 Table 3 使用 8/5/0 的合法 denominator，而不是强行维持 10/10/10。
`out_of_order` 行记为 **N/A**，不是 0；不能因 benchmark 有流程侧顺序扰动就反推法规顺序。

| 方法 | Missing P | Missing R | Missing F1 | Actor P | Actor R | Actor F1 | Order P | Order R | Order F1 | Macro-F1 | Micro-F1 | Specificity | Exact type | Unobs. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Sun 重建（相似度 grounding） | 0.5000 | 1.0000 | 0.6667 | 0.5000 | 0.2000 | 0.2857 | N/A | N/A | N/A | 0.4762 | 0.5806 | 0.0000 | 9/13 | 8 |
| Winter wrapper（相似度 grounding） | 0.5000 | 1.0000 | 0.6667 | 0.0000 | 0.0000 | 0.0000 | N/A | N/A | N/A | 0.3333 | 0.5517 | 0.3846 | 8/13 | 0 |
| Ours（自动 grounding） | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | N/A | N/A | N/A | 1.0000 | 1.0000 | 1.0000 | 13/13 | 0 |
| Oracle / Grounded 上界（声明绑定，非 Ours） | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | N/A | N/A | N/A | 1.0000 | 1.0000 | 1.0000 | 13/13 | 0 |

**Ours 组件与隔离**：Ours 先从 LLM-RE Rule Record + control Process Record
生成 automatic grounding predictions，持久化后才允许 evaluator 读取 Binding
Reference。Grounding 单独评估：action any-action top1 accuracy = 0.5000，
candidate-set recall = 1.0000，
lane coverage = 1.0000，lane exact accuracy
= 1.0000。
Ours detector 使用候选集合的 missing/lane differential；它不读取 benchmark
`grounding` 块、`target_activity_id`、expected lane、order pair 或 gold label。

**强制措辞（三条，缺一不可）：**

1. **差距是 grounding 效应，不是前人算法弱。** Sun/Winter 行是在同一 eligible
   item subset 上重算的相似度 grounding 结果；不得写成"前人方法差"。
2. **Oracle / Grounded 上界不是 Ours。** 它消费 supplied human binding；
   Ours 行才走 LLM-RE Rule Record → automatic grounding → detector。
3. **out_of_order 目前不可声称正式结论。** 在最终人工批准 order 语义之前，
   它只能是 N/A；不得把 process-only mutation 写成 formal rule order。
   全量三类 formal claim 仍需人工确认 19 个 unresolved pair
   （见 `outputs/reports/stage3_binding_final_human_approval_packet_v1.md`）。

**边界。** 本表已在 human-approved eligible subset 上按同一协议比较三个方法；
它不是对全部 30 对的完整三类结论，也不替代正式人工 Gold 发布。Oracle 与 end-to-end
仍分表。自动 grounding 文件为
`outputs/development/stage3_ours_v1/automatic_grounding_predictions_v1.json`，
Ours 预测为 `outputs/development/stage3_ours_v1/predictions.jsonl`，
评价为 `outputs/reports/stage3_ours_v1_evaluation.json` 与
`outputs/reports/stage3_automatic_grounding_evaluation_v1.json`。

#### 7.4.4 表 B：新增 30 条合成受控错误 panel（DEV，同一 evaluator）

| 方法 | Missing-action F1 | Incorrect-actor F1 | Out-of-order F1 | Macro-F1 | Exact | Unobservable |
|---|---:|---:|---:|---:|---:|---:|
| Winter wrapper | 1.0000 | 0.0000 | 0.0000 | 0.3333 | 0.3333 | 0 |
| Sun Stage 3 重建 | 0.3333 | 0.3333 | 0.3333 | 0.3333 | 0.2000 | 8 |
| BM25 | 1.0000 | 0.0000 | 0.0000 | 0.3333 | 0.3333 | 10 |
| TF-IDF/SVD | 1.0000 | 0.5714 | 0.3333 | 0.6349 | 0.5333 | 6 |

来源：`outputs/development/s39_synthetic_panel_<method>_v1/`；逐条
per-error P/R/F1、detected/missed/wrong-type、检测率与 runtime 见各 run
evaluation.json（Winter 3.9s、Sun 15.0s、BM25 6.0s、TF-IDF/SVD 12.7s）；
失败案例（FN/FP 明细）见 `predictions.jsonl` 与对比胶囊
`s39_synthetic_panel_compare_v1/comparison.json`。

#### 7.4.5 S3.9-EXT 40 对受控扩展结果（DEV，2026-09-07 修复后重算）

四类检测在同一输入、相同阈值、相同决策顺序下重跑。合规/违规两侧共用固定五分类决策；规则先生成预测，再根据标签评价。失败及无法判断计入完整分母。40 对合成面板与 33 条人工违规标签分开，不作为正式 Oracle。

Sun 原三类公式保留。执行者检查已恢复规则与动作、流程对象与动作的关联；时间数值矛盾仅使用映射通过且明确绑定同一动作的上限证据；五分类混淆矩阵增设无法判断列，修复漏计 FN 与误判合规 FP 的问题。见修复报告，历史结果仅留作溯源。

参考确定性抽取（非人工 Gold、非 LLM-RE）：

| 方法 | 禁止动作 / 条件 / 约束 / 例外 F1 | Macro-F1 | Exact | 错误类型数 | 目标类型不可观察数 |
|---|---:|---:|---:|---:|---:|
| Winter-style | 0.952 / 0.235 / 0.400 / 0.308 | 0.474 | 0.425 | 9 | 18 |
| Sun-style | 0.952 / 0.000 / 0.000 / 0.000 | 0.238 | 0.250 | 1 | 30 |
| BM25 | 0.571 / 0.000 / 0.000 / 0.000 | 0.143 | 0.100 | 0 | 30 |
| TF-IDF/SVD | 1.000 / 0.000 / 0.333 / 0.167 | 0.375 | 0.325 | 1 | 27 |

| 方法 | 80 对象准确率 | 合规对照误报率 | 40 对全部判对比例 | 四违规类 Macro-F1 | 五类 Macro-F1 |
|---|---:|---:|---:|---:|---:|
| Winter-style | 0.362 | 0.500 | 0.225 | 0.376 | 0.390 |
| Sun-style | 0.237 | 0.125 | 0.175 | 0.192 | 0.223 |
| BM25 | 0.225 | 0.000 | 0.100 | 0.143 | 0.202 |
| TF-IDF/SVD | 0.338 | 0.275 | 0.300 | 0.327 | 0.355 |

外部 Rules-Only 预测接入相同检测器：

| 方法 | 禁止动作 / 条件 / 约束 / 例外 F1 | Macro-F1 | Exact | 错误类型数 | 目标类型不可观察数 |
|---|---:|---:|---:|---:|---:|
| Winter-style | 0.750 / 0.222 / 0.353 / 0.000 | 0.331 | 0.275 | 10 | 23 |
| Sun-style | 0.750 / 0.000 / 0.000 / 0.000 | 0.188 | 0.150 | 0 | 32 |
| BM25 | 0.000 / 0.000 / 0.000 / 0.000 | 0.000 | 0.000 | 0 | 32 |
| TF-IDF/SVD | 0.889 / 0.000 / 0.286 / 0.154 | 0.332 | 0.275 | 6 | 28 |

| 方法 | 80 对象准确率 | 合规对照误报率 | 40 对全部判对比例 | 四违规类 Macro-F1 | 五类 Macro-F1 |
|---|---:|---:|---:|---:|---:|
| Winter-style | 0.263 | 0.450 | 0.150 | 0.264 | 0.283 |
| Sun-style | 0.200 | 0.050 | 0.150 | 0.167 | 0.205 |
| BM25 | 0.150 | 0.000 | 0.000 | 0.000 | 0.075 |
| TF-IDF/SVD | 0.263 | 0.375 | 0.225 | 0.268 | 0.287 |

目标类型不可观察是诊断量，不等于全类型无法判断；可能与 wrong-type 重叠。
新增禁止动作检测有可行性证据；约束检测仅部分支持；条件与例外主要受动作映射和 BPMN 可观察性限制。不得声称四类均已证明性能提升。Rules-Only 存在英文输入经德语 classifier 槽 pass-through 的跨语言限制及 first-valid-span 投影限制，观察到的下游差异不能全部归因于抽取方法本身。

来源：`outputs/reports/s3_formula_repair_v2.json`；逐样本与运行 manifest：`outputs/evidence/s3_formula_repair_v2/`。

#### 7.4.6 表 C：历史对照的错误类型分析（各自旧版实现，非本轮重新验证）

| 错误类型 | 最容易的方法 | 最困难的方法 | 主要失败原因 | 对应方法模块 |
|---|---|---|---|---|
| missing_action | Winter / BM25 / TF-IDF（合成 panel R=1.0） | Sun（合成 panel R=0.2，8 条 action_mapping_below_gamma） | 规则 action 与删除任务的词面相似度低于 gamma；Sun Def-5 对映射阈值敏感 | Sun Def-5 similarity mapping；Winter cost_obligation |
| incorrect_actor | TF-IDF/SVD（人工 0.625 / 合成 0.5714） | Winter / BM25（恒 0） | 这三个方法不引入参与者的语义标签：Winter 只读 process participant，BM25 对 actor 候选池的检索不足以支撑 min-sim<θ 判定 | actor vocabulary / pool-lane 解析；Def-6 actor matching |
| out_of_order | 全部薄弱（人工 panel 最优 0.1667） | Sun/BM25/TF-IDF（合成 0.3333，人工 0） | 顺序违规依赖控制流可达关系；现有方法对 gateway 分支与可达性的粒度不足，多数顺序变异在可达关系上不可观测 | control-flow reachability；Def-7 顺序约束 |

#### 7.4.7 讨论

以下旧版对照归因是待验证解释；不能据低分断言特定模块必然是唯一原因。当前 Sun 已按活动绑定 participant/业务对象，旧版“participant 未绑定活动”的原因仅适用于修复前；本轮确认的原因和证据以 §7.4.5 修复报告为准。

- **哪种错误最容易检测**：missing_action——凡规则含明确义务 action 且词面可映射，
  Winter/BM25/TF-IDF 在合成 panel 上 R=1.0（人工 panel 亦 0.95–1.0）。原因：删除任务
  直接改变 action 集合，检索/词面方法对这一信号最敏感。
- **哪种错误最难**：out_of_order——人工 panel 最优仅 0.1667（Winter），合成 panel
  最高 0.3333（TF-IDF/SVD）。**actor 与 order 错误都比 missing_action 难**。
- **actor 错误是否需要 Stage 1 更好的语义标签**：是。TF-IDF/SVD 的 actor 优势来自把
  business-object/actor 文本纳入同一 dense 空间并参与 min-sim 判定；Winter/BM25 因
  依赖有限的 pool/lane 名或独立候选池而恒 0。GDPR-7 中 lane 名为空、actor 只存在于
  participant，Stage 1 更完整的 actor 语义标签（而非仅结构解析）是 actor 类检测的
  前置条件。
- **order 错误是否依赖控制流可达关系**：是。Sun Def-7 与 Winter cost_so 都以可达
  关系为唯一顺序信号；合成 panel 的 OO 变异若落在 gateway 分支/并行结构上，可达
  关系不变即不可观测。需要 sequence-flow 级的 directly-follows 或执行语义信号。
- **missing action 为何不能只靠词面相似度**：合成 panel 中 Sun 对 8/10 条
  missing_action 变异给出 action_mapping_below_gamma（规则 action 与模型 action
  的相似度低于 gamma，Def-5 分母为 0 或映射失败）。**删除动作后词面相似度取决于
  剩余任务中是否存在同义表达**；只靠词面会把“同义保留”（规则义务以不同措辞仍
  存在）误判为缺失，或把删除漏判为未缺失。
- **Stage 1 错误如何传播到 Stage 3**：Stage 1 结构 micro-F1=1.0（共享解析组件）只
  保证 BPMN-Process Record 的结构转换无错，**不证明语义标签正确**。actor 类错误
  检测为 0 的 Winter/BM25 正说明：Stage 1 未提供参与者语义（lane 名为空、participant
  未绑定到活动），该语义缺失直接传递到 Stage 3 的 actor 判定；而组合三元组（P2
  triple exact 0.4222）与 stage 1 标签质量共同决定 Stage 3 的证据链。
- **各方法擅长什么**：Winter=义务/缺失动作（obligation cost）与可达顺序；Sun=
  约束驱动的匹配（MAP 0.8175）与缺失动作（Def-5 强于 actor/order）；BM25=词面
  极大化（missing action 强、语义 actor 弱）；TF-IDF/SVD=两个领域共享 dense 表示，
  对 actor 类错误最有效（人工 0.625、合成 0.5714），整体 macro 最优。
- **synthetic 与人工 Gold 是否一致**：一致点=missing_action 两类 panel 都是最易
  检测、顺序错误都最弱；合成 panel 复现了人工 panel 中 Winter/BM25 的 actor=0。
  差异点=Sun 在合成 panel 的 missing_action R 降至 0.2（人工 panel R=1.0）——
  因为合成变异删除的任务未必与绑定 rule 的 action 词面匹配（生成器按语法结构
  选择目标，而非按 rule 词面），人工 panel 的 11 条则由人工基于 rule 语义构建。
- **哪些结论只能作为受控实验结论**：合成 panel 的精确检测率、easiest/hardest
  排序、与人工 panel 的差异归因，均为**受控变异上的描述性结论**，不是真实
  process-model 犯罪的泛化结论；正式 Stage 3 claim 仍以人工 panel 为依据，Oracle
  与端到端仍需 S3.7/S3.10。

#### 7.4.8 Stage 3 Sun 式阈值敏感性（既有网格，2026-09-07 修复后复核，零 API）

当前复核：`outputs/evidence/s3_formula_repair_v2/threshold_sensitivity.json`。修复执行者关联后各网格主指标不变；历史图仅作为这些相同聚合数值的展示。

> 来源与复现：`outputs/reports/s35_sun_stage3_threshold_sensitivity_v1.{json,md}`
> 与图 A/图 B（`..._figA_gamma_missing_action_out_of_order.svg`、
> `..._figB_theta_incorrect_actor.svg`）；`scripts/build_sun_stage3_threshold_sensitivity_v1.py`
> （全量离线重算与 `--report-only` 确定性重放）；同一 33 条人工 Gold、同一
> Rule/Process Records、同一 Sun Definition 4–7 重建、同一 spaCy 相似度后端与
> 同一 common evaluator，未修改任何 Gold/样本/预测/公式，API calls=0、cost=0。

Sun et al. 将 γ 视为可调的语义等价门槛。其多数流程模型在 γ=0.8 时获得最高违规检测精度，但复杂度最高的模型在 γ=0.6 时表现更好；作者将其归因于复杂流程中文本相似度降低。本文首先直接迁移 γ=0.8，以保留方法级对照。结果表明，在本文七模型数据和 spaCy 相似度后端上，γ=0.8 使大量合法的 action mappings 无法通过门槛，导致 incorrect-actor 和 out-of-order 检查不可观察。按照 Sun 的离散阈值敏感性分析方式，γ=0.6 是测试值中表现最平衡的设置，Macro-F1 从 0.3889 提升至 0.8733。该结果说明阈值需要随数据复杂度和相似度后端重新校准，而不是说明 Sun 的公式无效。

**表格/图形与两种口径**：

- 表 A 的 Sun 行即 **Sun-transferred**（τ=0.8、γ=0.8、ϑ=0.8；Macro-F1 0.3889、
  exact 0.3636、unobservable 10），本小节不删除、不隐藏该低分基线；
- **Sun-style calibrated sensitivity** = tested values 中的 best observed setting
  （τ=0.8、γ=0.6、ϑ=0.8；Missing F1 1.0、Incorrect-actor F1 0.7778、
  Out-of-order F1 0.8421、Macro-F1 0.8733、exact 0.7879、unobservable 4）；
- τ∈{0.0,…,0.9} 只评价 matching 的每流程 AP/MAP（Def-4 分数随 τ 重算后重排），
  不把 matching MAP 当作 violation F1；γ∈{0.0,…,0.9}（ϑ 固定 0.8）与
  ϑ∈{0.5,…,0.9}（固定 γ=0.8，Sun 图 9 协议）均由 SunScorer 真实重算
  mappings/denominators/order endpoints/observability，不是对既有最终分数重切阈值；
- 图 A = 不同 γ 下 missing action 与 out-of-order 的每流程结果（Sun 图 8 口径；
  Sun 原图主要报告 Precision，图内另附 Recall/F1 补充面板）；图 B = 固定 γ=0.8 后
  不同 ϑ 下 incorrect actor 的每流程结果（Sun 图 9 口径）。

**边界与措辞（必须与正文一致）**：

- Sun 原论文与本文数据不同（模型集合、规则库、相似度后端与 panel 构造均不同）；
  “0.8 是其数据上多数模型表现较好的经验值”，不是“Sun 规定所有模型必须使用 0.8”；
- 本文是 Sun 方法级独立重建，不是原代码精确复现；γ=0.6 只是本文数据与当前
  相似度后端上的经验校准值，不得称数学全局最优阈值、Sun 原论文固定阈值、
  held-out 最优值或“与 Sun 原始四模型完全相同的数据结果”；
- 不把敏感性结果伪装成预注册正式结果：主阈值保持预注册 (τ,γ,ϑ)=(0.8,0.8,0.8)，
  本小节与全部敏感性产物标注 DEV_ONLY；
- 33 条人工 Gold 没有 Gold=none 合规样本，不能用它证明 specificity 或控制
  false-positive rate；33 条 panel 每个测试点预路由单一 gold 类型，跨类型 FP
  结构性不可能出现，Precision 面板仅按 Sun 口径保留，信息以 Recall/F1 为主。

[[TODO-RESULT:S3.7：Oracle Stage 3 与 end-to-end 分表]]

### 7.5 端到端消融

| 组合 | Stage 2 | Stage 3 | 状态 | 主要指标 |
|---|---|---|---|---|
| E00 | Sun | Sun | TEMPLATE | — |
| E10 | Improved | Sun | TEMPLATE | — |
| E01 | Sun | Improved | TEMPLATE | — |
| E11 | Improved | Improved | TEMPLATE | — |

[[TODO-RESULT:E00/E10/E01/E11：只从正式 manifests 回填]]

## 8. 讨论与局限性

当前可确认的复现边界包括：Sun 完整 Stage 2 源码、权重、完整 marker 和原始 150
phrase Gold 不可得；德文法规与英文公共 marker 之间需要显式语言适配；Sun 报告的
四个 GDPR BPMN 文件名尚未在现有证据中确定；不同论文的数据、split 和指标不能直接
用于严格显著性比较。以下按方法列出**基于量化证据**的局限：每条包含定量证据、具体
文本例子、错误原因、方法边界、可能优化方向，以及“为什么当前没有继续优化或为什么
仍需实验”。

### 8.1 Rules-Only（纯规则法）的局限性

1. **action 吞并 constraint（字段归属错误主导）**。
   - 定量证据：C1 分析显示 matched 的 212 个 action 中 192 个（91%）预测长于
     Gold、中位超出 54 字符；constraint 的 143 个 missed 中 57 个仅被 action
     覆盖。
   - 文本例子：`"the data shall be processed only to the extent necessary"`
     整段被并入 action，而 Gold 将 `"to the extent necessary"` 归 constraint。
   - 错误原因：`_subtree_span` 把 nsubj/全部依赖纳入 action 子树（B0-R1-ACTION
     已修主语开头 8→0，但边界/从句尾部仍有残余）。
   - 方法边界：Bedrock any-overlap 主口径对边界不敏感；修复主要体现在诊断面板
     （strict-exact action F1 3.0×）。
   - 可能优化方向：从句尾/编号残余的进一步收紧、C7 under-extension 与 C1 的
     双向平衡。
   - 为何没有继续：主口径非指标驱动项（真实运行 F1 持平），继续优化对主表无贡献、
     风险>收益；需正式 Gold 后按需再议。

2. **constraint↔condition 双向混淆**。
   - 定量证据：C2 分析——114 个 extra constraint 压 condition Gold、31 个反向；
     “to the extent” 双触发（44 个同界双发中 43 个为双 tregex）；SCOPE-DISAMBIG
     候选真实运行 F1 −0.0005 已回退。
   - 文本例子：`"to the extent"` 同时命中 `to<<an|the` 与 `to<<extent|purpose`
     两类模式。Gold 自身对 `that/who/to the extent/only` 的 condition/constraint
     标注内部不一致（见 B0_ERROR_ANALYSIS §8.3 cue 一致性统计）。
   - 错误原因：规则层共享 cue + Gold 定义口径差异；“不读 Gold 反向调规则”的
     硬约束下规则层无法安全消歧。
   - 方法边界：记为该规则方法的**方法局限**而非代码缺陷；P 侧需双边收敛验证。
   - 可能优化方向：registry 模式层复核（去掉 constraint 对 “to the extent” 的
     捕获）、逐条上下文约束。
   - 为何没有继续：候选实测净负，任何偏向都对称损失匹配；调整属于 registry/
     scope 层改动，需用户决策，当前不做。

3. **词典覆盖不足**。
   - 定量证据：13 个无词典覆盖名词漏抽（successor/spouse/child/developers/bank/
     body/society/owners/shareholders/beneficiary），代词 `It` 作 actor 需 Gold
     语义裁决（未覆盖 1/48）。
   - 文本例子：`"the body shall ensure…"`、继承人/配偶等法律 actor 名词不在 actor
     词典。
   - 错误原因：方法以“名词短语 + 词典 + 依赖关系”为 actor 判据；公开 marker
     lexicon 为 dev-only（禁止训练/评测数据回流）。
   - 方法边界：词典规模与方法细节差异属已披露适配，不阻断方法级复现。
   - 可能优化方向：向用户申请公开法律 actor 名词来源扩展；或 local-frozen
     授权扩展（路径 b 已用过一次：13 名词以 source
     `authorized_local_frozen_estg150_gap_2026_08_04` 加入）。
   - 为何需要用户决策：S2.3 对公开种子有严格来源约束，“看词典缺口反推词典”
     属于治理覆盖，不能由 Agent 自行决定。

4. **Sun marker 定义与当前 Gold 定义口径差异**。
   - 定量证据：我们的 constraint Gold 302 个中仅 13 个（4%）符合 Sun Table-4
     公开 marker 定义（Sun 自己仅 35 个 constraint）；定义范围宽约 8–23 倍；
     Sun-marker 收敛后 Rules-Only constraint R=1.0 (13/13)、condition R=0.989
     (91/92)。
   - 文本例子：法律引用类（under/pursuant to/within the meaning）与排他（only）
     被我们计入 constraint，Sun 只算数量/时间/比较类限制。
   - 错误原因：不是“同一定义标得更细”，而是 constraint 定义本身不同。
   - 方法边界：Sun Table-4 是 “initial sets”，13 个是 Sun 定义下界；
     P 侧需双边收敛（Sun-marker 版规则）另行验证。
   - 可能优化方向：实现 Sun-marker 版规则做双边收敛；或与审稿人说明定义差异。
   - 为何需要更多实验/讨论：这是低分主因之一，必须透明披露，且需要一个
     dual-side convergence 实验（未实施）。

5. **原始 Sun 资产缺失与已披露适配限制**。
   - 定量证据：无 Sun 原代码/权重/完整私有词典/原始 150 phrase Gold；Tsurgeon
     为诚实非实现（fail-closed 守卫）；CoreNLP 版本 4.5.10 是本地锁定（Sun 未
     公布版本）。
   - 错误原因：资产不可得；方法级独立复现是唯一允许口径。
   - 方法边界：只能称 `method-level independent reconstruction`，禁止 exact/
     original；不因缺资产阻断。
   - 如何披露：`B0_R2_METHOD_CROSSWALK.md` 11 元素逐项记录实现/测试/披露。
   - 为何不需要继续：这属于已披露的复现边界，不是可“修复”的缺陷。

### 8.2 LLM-RE 的局限性

1. **constraint recall 较弱（最弱字段）**。
   - 定量证据：基线 R=0.288（99 个 constraint 内容进 action span、91 个完全
     未抽）；v6 修至 0.417 后 formal 粗 constraint F1 0.7427（细 0.5482）；
     R3 失败类型：wrong_field 169（constraint 100）+ not_extracted 154
     （constraint 69）。
   - 文本例子：`estg_000003 "a shorter period"`、`estg_000027 "to an annual
     amount"` 落在 action 里而非 constraint。
   - 错误原因：constraint 语义（法律引用/时间/数量/within the meaning/pursuant
     to/subject to）需要显式定义；v6 已定义但完成度有限。
   - 方法边界：高精度保守型——宁可漏抽不误抽；constraint 在 Gold 中占比高
     （302/1055），召回损失显著。
   - 可能优化方向：更多 constraint few-shot、两遍 verify-pass、条款级子类进一步
     细分。
   - 为何仍需实验：任何更激进召回都会牺牲 precision，必须在授权预算内做
     AB-2（few-shot）与 AB-1（字段定义去除对照）的真实消融。

2. **constraint 内容进入 action 或完全漏抽**。
   - 定量证据：R1 基线 124 个“已抽到但落错字段”（99 action + 16 condition + …）；
     R3 constraint wrong_field 100 / not_extracted 69。
   - 文本例子：`"It may cover a shorter period if …"` 中 `"a shorter period"`
     被并入 action。
   - 错误原因：prompt 早期未定义 constraint 与 action 的边界。
   - 方法边界：该问题在 v6 已显著缓解（constraint R 0.288→0.417），但仍存在。
   - 可能优化方向：显式 “禁止并入 action/condition” 规则（已加入 v6 规则 25–27）
     进一步强化；属 prompt 层，需真实 pilot 验证。
   - 为何仍需实验：prompt 修改必须经授权 pilot + delta 记录，不能直接改正式数据。

3. **泛指 actor 误抽**。
   - 定量证据：历史 run actor P=0.594（69 pred vs 48 gold，23 个无 Gold 交叠的
     actor）；formal 粗 actor F1 0.7579（低于 Rules-Only 0.8203）。
   - 文本例子：表述 `"the body shall ensure…"` 中抽取无 Gold 交叠的泛指主语作为
     actor。
   - 错误原因：LLM 把非 actor 主语也列为 actor；多词/泛指实体边界判断不稳。
   - 方法边界：actor 字段是 LLM-RE 相对弱项（P 侧）；R 侧召回尚可
     （coarse 0.8780）。
   - 可能优化方向：actor 定义更严格（只取最小名词短语、禁止泛指主语）；few-shot
     增加反例。
   - 为何仍需实验：提 actor precision 可能伤 recall，需真实消融（AB-2/AB-4 方向）。

4. **高精度、较保守、召回偏低（整体模式）**。
   - 定量证据：细 Gold F1 0.7756（P 0.8793 / R 0.6938）vs Rules-Only 0.7186
     （P 0.6845 / R 0.7564）——LLM-RE 精度更高、召回更低；“宁可漏抽不误抽”
     在低资源字段（exception/constraint）牺牲召回。
   - 错误原因：prompt 的 “不确定就省略/入 unsupported” 保守指令 + 低资源字段
     few-shot 不足。
   - 方法边界：这是方法固有 trade-off，不是单一缺陷。
   - 可能优化方向：v6 已把省略改“列出候选 + 不确定入 unsupported”；进一步可通过
     few-shot/验证轮提升召回。
   - 为何需要更多数据：精度—召回平衡的最终判断必须等复杂语料 API arms 与消融。

5. **对真实 API、预算合同、transport 配方和 prompt hash 的依赖**。
   - 定量证据：模型钉死 deepseek-v4-pro；transport 配方（thinking-disabled、无
     json_object、temp0/top_p1/max_tokens4096）是端点实证适配；提示 hash
     3aa64877 三方锁定；每批需用户授权 + `--max-calls` 硬上限；官方 billing
     tokens/cost 只能从真实响应 usage 获得（preflight 已锁定 63 个 payload、
     retry=0、输出 cap 258,048 total、建议输入 cap 63,000,000 tokens、
     USD cap 27.63——尚未运行）。
   - 错误原因：LLM 可复现性来自外部端点与治理合同，不是本地可完全控制。
   - 方法边界：任何新模型/端点/采样变更都会破坏锁定，必须重新走授权链条。
   - 可能优化方向：AB-9 的 5 次独立重跑 + self-consistency/field-span agreement
     报告（对齐 Barrientos 论文设计）。
   - 为何仍需授权：所有真实 LLM 调用都需用户明确授权，当前零调用、零成本。

### 8.3 Rules+LLM-Repair 的负结果对照（不写为贡献）

选择性 LLM 修复在当前触发器设计下产生净负收益（§4.3；此处引用的是 **development
全量 150 负结果，commit 74614e3，非正式三方法比较主结果**）：主口径 F1 0.7621 vs
Rules-Only 0.7986（−0.0365）、actor P 0.7077→0.2754。结论引用
`MASTER_PIPELINE.md` §8.8.1 三项困难，并只能作为对照臂解释“证据约束的必要性”。

[[TODO-RESULT:S2.12/S3.10：结合复杂语料与 Stage 3 结果讨论适用边界和失败案例]]

### 8.4 Threats to Validity

**内部效度**：
- Stage 1 为固定 GDPR-7 上的描述性复现：target labels 在开发期可见、
  developer_blind=false、无 held-out 分割（§7.1 claim 逐项披露）；structure
  micro-F1=1.0 仅来自共享解析组件，不可外推为语义能力。
- Stage 3 双手工 panel 指标使用 dev 阈值（0.5/fixed gamma/delta，非 blind
  预注册）；同一 evaluator 的 observability 政策（incorrect_actor 的
  unobservable 计为 FN）影响宏观口径，表 B 的 per-type F1 与 unobservable
  列须一起读。
- 合成受控错误 panel 的生成目标按**语法/结构**锁定（非按规则词面选择），因此
  “方法检测不到”可能部分反映目标与原 rule 的词面对齐程度，而不仅是错误本身
  的固有难度；此点已在 §7.4.7 如实讨论。

**外部效度**：
- 全部 Stage 3 违规结果基于 7 个 GDPR 流程（45 activities）与 GDPR 义务类型
  （通知、同意、访问、可携、撤回、更正、删除）；扩展到其他法规域与更复杂的
  流程拓扑（gateway 并发、循环）需要新面板。
- 合成错误是**最小、单一**变异；真实流程模型可能同时存在多重违规与跨阶段
  交互错误，本文的 exactly-one-error 设计不能代表其分布。

**构建效度**：
- violation type 的定义采用 Sun Def 5–7 / Winter cost_* 的映射口径；
  不同论文对 missing_action/incorrect_actor/out_of_order 的边界定义可能不同。
- 合成 panel 的 “expected violation” 是生成器契约的一部分，与人工 Gold 的
  decision 语义分离（不混用、不冒充）。

**结论效度**：
- 样本量小（33/30 条、7 流程），不做显著性推断；表 A/B 均为描述性数值。
- actor/order 检测率（尤其 Winter/BM25 的 0）不能解释为“真实流程无此类违规”，
  只能解释为“这些方法在该表示上没有对应信号”。

### 8.5 Stage 1 → Stage 3 误差传播小结（§7.4.7 的汇总）

- Stage 1 结构正确（micro-F1=1.0）保证 Stage 3 的流程图输入无转换错误，但
  不提供参与者语义；GDPR-7 的 lane 名为空，actor 只存在于 participant，
  Winter/BM25 的 actor=0 与该语义缺失直接对应。
- Stage 1 的组合三元组准确率（P2 0.4222）与标签质量决定了 Stage 3 的
  rule-action 映射：Sun 在合成 missing_action 上 8/10 为
  action_mapping_below_gamma，本质是 Stage 1/规则抽取的词面对齐不足向
  Stage 3 的传播。
- 结论：Stage 3 违规检测的瓶颈不只在于匹配/顺序算法，还在于 Stage 1 语义
  标签（actor、组合三元组）的质量；改进 Stage 3 需先补 Stage 1 的参与者
  语义与三元组一致性（见 §7.4.7 讨论）。

## 9. 结论

本文围绕 Sun et al. 的三阶段框架完成了可追溯的独立重建与扩展实验，并产出
正式或 DEV 标注的结果：(1) Stage 1 在固定 GDPR-7 上完成描述性复现（P2
语义 micro-F1 0.8185、accuracy 0.6928、triple 0.4222；structure 1.0 仅
共享解析；P0 0/P1 0.5956 提供下限与规则基准）；(2) Stage 2 正式三方法
比较显示无整体胜者——LLM-RE 在 action/condition/constraint/modality
label 领先，Rules-Only 在 actor/exception 领先，Rules+LLM-Repair 因 actor
过度抽取成为净负对照（§7.2）；(3) Stage 3 在人工 33 条 panel 与新增 30 条
合成受控错误 panel 上量化了四类非 LLM 方法：missing_action 最易检测，
incorrect_actor 依赖 Stage 1 参与者语义（TF-IDF/SVD 相对最优），out_of_order
最难且依赖控制流可达信号（§7.4）；(4) 误差传播分析表明 Stage 3 的 actor/order
瓶颈部分来自 Stage 1 语义标签缺失。S2.12 复杂语料 Direct/Fallback 为
pending authorized extension，不阻塞本文主体方法描述；Stage 3 Oracle 与
端到端评价仍待 S3.7/S3.10。综合来看，本文的贡献是“分阶段、可追溯的方法级
重建 + 类型化违规检测的受控证据”，而不是对单一全局指标的胜者宣称。

[[TODO-RESULT:P8：S2.12 API arms、S3.7 Oracle 与端到端完成后复核并回填]]
