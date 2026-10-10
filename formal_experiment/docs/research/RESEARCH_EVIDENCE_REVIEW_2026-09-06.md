# 研究证据核查与梳理：背景·方法·实验·总结（2026-09-06）

> 本文是一次**研究层面的事实核查与证据梳理**，不是新的平行路线图，也不是实时状态页。
> 实时状态仍以 `docs/PROJECT_AUDIT.md` 为准，完整任务树仍以 `docs/MASTER_PIPELINE.md` 为准。
> 本文回答四个问题：研究是什么、方法怎么连、每个主张有没有对应实验证据、还剩什么必须做。
> 所有数字均回指可核查产物（报告/评测 JSON/预测/事件日志），本文不产生新实验数字。

## 0. 本次核查的范围与结论摘要

- 核查基线：项目实际代码、配置、数据、预测、评测报告与实验事件日志（`EXPERIMENT_LOG.md` /
  `EXPERIMENT_EVENTS.jsonl`，最新事件 #315，2026-09-05）。
- 本次明确纠正：2026-09-05 准备的“直接使用 Barrientos 原始 FULL/NO-PATTERNS 两份提示、
  在冻结 36 条输入上运行 360 次（36×2×5）”方案**已被用户撤回、不得执行**；主路线
  （MASTER_PIPELINE §8.8.4/§15）、状态页（PROJECT_AUDIT §1）与论文消融矩阵
  （paper/ABLATION_MATRIX）已原位标注撤回，历史文本与产物（入口脚本、独立合同、预检
  报告、focused tests，checkpoint `2c5181e`）**原样保留为证据**。
- 四大核查结论：
  1. Stage 2 主对比与严格单因素消融已有**正式/授权真实证据**，覆盖研究主张的绝大部分；
  2. **Stage 2 → Stage 3 同法衔接的成对比较没有任何已执行产物**（无论正式或 development）；
     这与 RQ4/E10/E00–E11/S3.10 的计划一致，属于“尚未执行”而非“结果不好”；
  3. Stage 3 四类新错误的证据是**受控合成实验**（40 变体 + 40 对照），定义/字段映射/
     BPMN 表面完整，但按类型看只有部分类型有较强检出证据，误报率需要如实报告；
  4. 现有消融**够回答 Stage 2 内部模块贡献问题**；不必要、也不应再为凑模块清单追加实验。

---

## 一、背景：研究是什么，为什么这样做

### 1.1 Sun 的三阶段框架解决什么问题

Sun et al. (2024)（Design-time business process compliance assessment based on
multi-granularity semantic information）提出**设计期业务流程合规检查**的三阶段流水线：

1. **Stage 1 流程解析**：把 BPMN 流程模型解析成结构化 Process Record（活动、事件、
   网关、泳道/执行者、顺序与控制流关系）；
2. **Stage 2 法规解析**：把法律/法规句子解析成结构化 Rule Record（六要素：
   modality 情态、actor 执行者、action 动作、condition 条件、constraint 约束、
   exception 例外），并附原文位置（evidence span）；
3. **Stage 3 匹配与违规检测**：把 Rule Record 与 Process Record 做规则—流程匹配，
   再判断流程是否违反规则（原类型：缺动作 missing_action、执行者错误 incorrect_actor、
   顺序错误 out_of_order），产出 Violation Report。

一句话：**把“法条怎么说”和“流程怎么做”都变成结构，再自动对账**。合规检查从此不依赖
人工逐条比对。

### 1.2 Stage 2 为什么值得用 LLM 替代（本研究的切入点）

Sun 的 Stage 2 是传统 NLP 流水线（BERT-TextCNN 情态分类 + CoreNLP/Tregex/Tsurgeon
短语抽取 + 领域词典）。它有两个众所周知的软肋，也正是本项目在 Stage 2 上做方法比较的
动机：

- 规则/词典覆盖有限：没进词典的说法（如把 `successor/spouse/beneficiary` 当 actor）
  直接漏抽；constraint↔condition 一类边界靠手工 cue 很难消歧；
- 工程链条长、定制深：换一部法律、换一种语言表述就要重调规则。

本项目不是简单“给 Sun 加个 LLM”，而是做了三组方法的**同条件比较**（同一冻结输入、
同一 Gold、同一 schema、同一 evaluator）：

| 方法（正式名 / 机器 ID） | 是什么 | 角色 |
|---|---|---|
| Rules-Only（`sun_rule_only`，旧代号 B0） | 非 LLM 的 Sun Stage 2 方法级独立重建（重建口径经用户授权，不是作者原代码） | 基线 |
| Rules+LLM-Repair（`sun_llm_fallback`，旧代号 H1） | 规则为主、只在预注册 trigger 下让 LLM 修字段 | 对照臂（负结果，不再优化） |
| LLM-SE（`direct_llm`，旧代号 D1） | LLM 直接端到端生成同一六要素 Rule Record | 主方法 |

**位置声明（2026-09-06 用户澄清后固定）**：Sun 是整体改进对象与三阶段主干；Barrientos
et al. (2026) 只是 **Stage 2 的方法借鉴来源**——本项目借鉴其“LLM 结构化输出 + 校验 +
受控词汇/受控 schema + 归一化与评价纪律”的思路（例如 LLM-SE 的 strict JSON 输出
契约、verbatim span 回指校验、确定性后处理链、预算与可复现纪律），**但没有照抄其
prompt、输出结构或整个系统**（其 change-impact 表示、precondition/norm/44 模式与我们
的 Sun 六要素 schema 不同，属于 C4 跨任务，不能直接换算）。研究定位不是“必须整体优于
Barrientos”，因此**不把“原样运行 Barrientos 原生提示、跑 360 次”当作要执行的实验**
（该方案已于 2026-09-05 被误准备、2026-09-06 撤回，见 §0 与 `MASTER_PIPELINE.md` §8.8.4）。

### 1.3 Stage 3 为什么需要扩展错误类型

原三类违规只消费六要素里的 **action（缺失）、actor（错误）、顺序关系**；而六要素里
prohibition 情态、condition、constraint、exception 四个部分在 Stage 3 没有消费者——
法条里明说“禁止做 X”“只有满足条件才做”“72 小时内完成”“除非有例外”，流程模型里
若出现被禁止动作、忽略条件、超时限、无例外分支，原检测器看不见。因此 S3.9-EXT 在
受控合成层面补了四类：`prohibited_action_present`（禁止动作出现）、
`required_condition_not_enforced`（必要条件未落实）、`constraint_violated`（约束被违反）、
`exception_not_handled`（例外未处理）。这是**最小字段覆盖扩展**（每个新类型给一个
此前未用的六要素字段一个下游消费者），不是穷尽式违规分类。

---

## 二、方法：三个阶段怎么连起来

### 2.1 流程图（简化）

```text
法律法规语料 ──► Stage 2A 情态分类 ──► Stage 2B 六要素抽取 ──► Rule Record（六要素+原文位置）
                    (definition/obligation/prohibition/permission)      │
BPMN 流程库 ──► Stage 1 结构解析+标签语义 ──► Process Record（活动/执行者/顺序）│
                                                                          ▼
                                                  Stage 3A 规则—流程匹配（候选+排序）
                                                                          │
                                                  Stage 3B 违规检测与分类（缺动作/错执行者/错顺序
                                                                          │  +扩展：禁止动作/条件未落实/约束违反/例外未处理）
                                                                          ▼
                                                              Violation Report（类型+证据+定位）
```

实施顺序（项目实际）：先 Stage 2（当前主线，已完成三方法正式比较）→ Stage 1（已冻结）→
Stage 3（development 完成；formal Oracle/端到端被门禁锁定）。

### 2.2 三阶段输入—处理—输出与连接（对照表）

| 阶段 | 输入 | 处理 | 输出 | 数据与评价 |
|---|---|---|---|---|
| Stage 1 | 7 个 GDPR-7 BPMN（byte-exact 冻结，45 活动/135 标签字段） | P0 原样解析 / P1 轻量规则 / P2 Sun/Leopold-style 标签语义（已冻结，post-Gold target-aware） | Process Record（正式 Process Gold 已发布 7 条，2026-08-13 冻结） | 固定 GDPR-7 描述性组件评价（P2 语义 micro F1 0.8185）；**不是 held-out 泛化证据** |
| Stage 2 | EStG-150 句子（150 条正式 Gold-blind 输入 v2）+ 复杂语料（S2.11 36 条 Barrientos requirements，已冻结 Gold） | B0 规则重建 / D1 LLM 直抽 / H1 规则+LLM 修复 | Rule Record（六要素 span + modality 标签 + actor-action/order；150 条三方法正式 predictions 已发布） | 粗 Gold（609 spans，Sun 句子级主口径）/ 细 Gold（1055 spans 对照）；modality label 另表；禁止混表 |
| Stage 3 | Process Record（GDPR-7）+ Rule Record | Winter 式 / Sun Def4-7 式 / BM25 / TF-IDF-SVD（development） | 匹配（AP/MAP）+ 违规类型（P/R/F1）+ unobservable | 33 条 violation decision Gold + 25 条 matching decision Gold（≠ Gold Rule Records）；dev-only |
| 端到端 | Stage 1 输出 + Stage 2 输出 → 同一 Stage 3 | E00/E10/E01/E11 归因消融 | 误差传播对比 | **未执行**（见 §3.5） |

### 2.3 沿用 Sun / 借鉴 Barrientos / 本项目修改与扩展

| 部分 | 来源 | 说明 |
|---|---|---|
| 三阶段框架、中间合同（Process/Rule/Violation）、Stage 2 六要素定义、句子级粗/细双口径评价 | **沿用 Sun**（方法级独立重建；B0 是重建的基线） | Stage 1 的 P2 也按 Sun/Leopold 风格重建；全部不得称 exact reproduction |
| Stage 1 流程模型解析方法 | **沿用 Sun 的思路**，不是本研究创新点 | 实现中的重建/适配差异（如 Tsurgeon 为 fail-closed 诚实非实现、词典规模与分词机制）如实披露 |
| LLM-SE 的“LLM 结构化输出 + 校验 + 受控词汇/schema + 归一化纪律”设计思路 | **借鉴 Barrientos**（只借鉴思路与纪律，不照抄其 prompt/输出结构/系统） | 我们仍输出 Sun 六要素；modality 4 类（Barrientos 3 类，无 definition）；normalized view 受控但原文 span 回指；Barrientos 原生表示仅用于受控 adapter 对照 |
| Rules-Only 之外的两个 Stage 2 对照/主方法（D1/H1） | **本项目实现** | 共享同一输入/Gold/evaluator；H1 已降级为负结果对照 |
| Stage 3 违规检测扩展四类错误 | **本项目扩展**（Winter/Sun 原论文未定义；一律称 Winter-style/Sun-style extension） | 受控合成面板 + 配对评价，dev-only |
| 坐标重锚、canonical validator、预算/授权合同、事件日志、fail-closed 门禁 | **本项目工程** | 属可复现/安全机制，**不是核心创新消融对象**（见 §3.3 说明） |

### 2.4 六要素如何被 Stage 3 消费

Stage 3 原三类消费：action（缺失→missing_action）、actor（错误→incorrect_actor）、
action 间的顺序（错误→out_of_order）。扩展四类分别消费：prohibition 情态 + action
（→ 禁止动作出现）、condition + action（→ 条件未落实）、constraint + action（→ 约束
违反，含时限矛盾）、exception + action（→ 例外未处理）。也就是说：**Stage 2 抽得准
不准，决定 Stage 3 能查什么**——这正是“Stage 2 替换是否影响最终检测”这一下游问题的
来源（contract 的 downstream_question；§3.5 会说明它为什么还没有被实验回答）。

---

## 三、实验：主张 ↔ 证据核对

### 3.0 实验事实分层（先分清“做过什么”）

| 层 | 定义 | 本项目实例 |
|---|---|---|
| 真实实验（已完成） | 真实数据/真实（或离线确定性的正式）运行，有 manifest/事件 | 三方法正式比较（150 条，0 新增 API，历史 300 次真实调用）、D1 早期 150 次真实运行、D/E 套件 **1140/1140 次真实调用**（2026-08-29 授权）、**450/450 次 prompt 单因素真实调用**（2026-08-30，USD 3.37） |
| 离线重评 / 受控合成 | 固定原始响应/固定 BPMN 的离线重放或合成面板，0 API | 后处理三模块单因素（D-full-0813 raw 重放）、S3.9 30 变体、S3.9-EXT 40 变体+40 对照、阈值敏感性网格、S2.12 B0 zero-API arm |
| 计划/准备但未执行 | 代码/合同/预检就绪，授权为空或已撤回 | S2.12 两个 API arms（63 calls，授权缺项）、**S2-BARR-4 360 次原生提示方案（已撤回）**、PDF/XML 消融（未启动） |
| 单元测试/模拟调用 | 假响应、fixture、dry-run | 22 项 360 次假响应链测试、31 次 authorized_called 之外的 all fake |
| 仍缺失的证据 | 见 §3.5/§3.6 | 同法 S2→S3 成对比较、S3.7 formal Oracle、GDPR Gold Rule Records 等 |

⚠️ 纪律提醒：测试通过数 ≠ 实验样本数；计划 ≠ 结果；`development` ≠ `formal`。

### 3.1 主对比：Sun 式语义抽取 vs 我的 LLM 抽取（研究问题 1 的核心）

**回答的问题**：在相同数据（EStG-150 正式输入 v2）、相同输出要求（六要素 span）、相同
评价方式（同一粗/细 Gold、同一 evaluator）下，Sun 式语义抽取与 LLM 抽取分别有什么优势
和不足。

**证据**：`outputs/reports/stage2_formal_three_method_comparison_v1.{json,md}` +
`data/predictions/{b0,direct_llm,sun_llm_fallback}_formal_arm_v1/` +
`data/results/*_formal_arm_v1/evaluation_coarse.json`（本次已逐字段核对存储值与报告一致；
独立 verifier VERIFIED；正式结论包 `stage2_formal_conclusion_v1`）。

**结果（句子级粗 Gold 逐字段 F1，正式）**：

| 字段 | Rules-Only | LLM-SE | Rules+LLM-Repair | 谁领先（描述性） |
|---|---:|---:|---:|---|
| actor | 0.820 | 0.758 | 0.430 | Rules-Only |
| action | 0.893 | 0.944 | 0.895 | LLM-SE |
| condition | 0.774 | 0.838 | 0.777 | LLM-SE |
| constraint | 0.618 | 0.743 | 0.620 | LLM-SE |
| exception | 0.880 | 0.762 | 0.880 | Rules-Only（与 H1 平） |
| modality 标签 accuracy | 0.740 | 0.833 | 0.820 | LLM-SE |
| modality label macro-F1 | 0.713 | 0.769 | 0.812 | Rules+LLM-Repair（macro-F1 最高但 span 净负；LLM-SE 在 label accuracy 领先） |
| 五字段算术平均 F1（描述性） | 0.797 | 0.809 | 0.720 | LLM-SE |

**可以支持的说法**（正式报告结论，字段级、无显著性推断）：
- LLM-SE 在 action/condition/constraint 三个字段与 modality 标签准确率上领先；
  Rules-Only 在 actor、exception 上领先（召回高：actor R 0.976 vs 0.878；exception R 1.0）；
- 两方法错误模式互补：规则法以**字段归属错误**为主（constraint 内容进了 action/condition，
  或 constraint↔condition 混淆），LLM 以**保守漏抽**为主（P 高 R 低，尤其低资源字段）；
- Rules+LLM-Repair 是净负对照（actor P 0.708→0.275，spans 65→167，过度抽取）：**无证据
  约束的选择性 LLM 修复加 FP 不加召回**——这个负结果本身是论文要保留的证据。

**反例/失败案例（解释“为什么差”）**：
- Rules-Only constraint 弱的主因之一是**定义口径差异**：本项目 Gold 的 302 个 constraint
  里只有 13 个（4%）符合 Sun 公开 marker 的定义（Sun 自身也只有 35 个）；用 Sun-marker
  收敛口径后 B0 constraint R=1.0 (13/13)、condition R=0.989 (91/92)。**低分不等于
  “抽不到”，部分是标签定义范围宽 8–23 倍的口径问题**（归因证据，dev 口径，C19）。
- LLM-SE 的 exception R 仅 0.727（10/11 gold），actor 泛化误抽在历史 run 里有
  P=0.594 的记录；constraint 始终是其最弱字段（R 0.288→0.417 的历史修复轨迹见 D1-R1）。
- 把“句子级粗 Gold”的数值（如早期归因 0.7986/0.8726）与“正式比较”逐字段数值混用会
  造成数字不一致：两者来自不同 Gold 快照/登记口径。**论文统一引用正式比较报告**
  （2026-08-11）的逐字段数字；更早的归因数字只作 development 背景。

### 3.2 Stage 2 消融：我的 LLM 方案里的关键设计各自起什么作用

已有**严格单因素**证据（同一模型 DeepSeek-V4-Pro-0813、同一 150 条输入、同一 Gold、
同一 evaluator；450/450 次真实调用，失败 0，USD 3.37；报告
`d1_prompt_factorial_results_v1.{json,md}`；基线 D-full-0813 F1=0.7719）：

| 消融（删/换什么） | 总体 F1 | ΔF1 | 逐字段要点 | 可支持的结论 |
|---|---:|---:|---|---|
| 完整方法 | 0.7719 | — | — | 基线 |
| 六个语义示例 → 纯结构模板 | 0.7650 | −0.0069 | actor F1 −0.1317（最大字段效应）；modality/condition/exception 略升 | 六个语义示例有**小幅总体正贡献**，actor 字段尤其依赖示例 |
| 去掉详细语义规则（规则 9–19、25–27） | 0.7759 | **+0.0040** | action F1 −0.0518，其他字段（exception +0.1059 等）上升 | 详细语义规则**未显示总体正增益**，但保护 action 字段 → 是字段间权衡，不是普遍无用 |
| 去掉显式 JSON 文字纪律 | 0.7790 | **+0.0071** | 合法输出率仍 1.0（150/150） | 在“保留六个示例”的当前模型/数据上**未测得增益**；不能推广为纪律普遍无用 |

后处理链（固定 D-full-0813 原始响应**离线重放**，0 新增 API；`d_full_postprocessing_ablation_v1`）：

| 去掉模块 | F1 | 说明 |
|---|---:|---|
| （完整链） | 0.772 | 150/150 成功、148 非空、0 invalid |
| 输出适配器 relay_schema_adapter | 0.772 | Δ=0：在这批响应上无额外分数增量 |
| **坐标重锚器 span_canonicalizer** | **0.000** | validator 拒掉 149/150——坐标接口一旦失配，整个记录报废；这是**接口正确性模块**，证据是“拿掉就全灭” |
| canonical validator | 0.772 | 0 条上游无效被观测到：Δ=0 只说明这批响应已合法，不取消其安全职责 |

另有一组历史模块证据（AB-8/B0-R1 批次 + 模块去除实验 B）：Rules-Only 的 actor 词典
扩展、modal classifier、multi-match guard 等各自 ±量级如实登记（含“去掉 guard 反而
+0.0053”的副作用披露）。

**明确缺口（已有实验答不了的问题）**：
- **AB-4 纯受控词汇单因素**（把“我的六字段受控 schema + marker”整体替换成 Barrientos
  44 模式 dual-view）尚未隔离：现有两个 replacement arm 因 schema 接口不兼容得 0（其
  raw 响应能解析、部分合其原 schema，但产不出我方六字段记录），**0 分只能说明接口不
  兼容，不能说明 Barrientos 方法无效**；
- **AB-10 style-equivalent 敏感性**（“表达不同但语义相同算正确”）未实现，属可选辅助。
- 是否需要补：见 §4.2——最小必要清单里这两项都**不是必须**（可如实标为局限/未隔离）。

**工程机制不算创新消融**：transport 配方（thinking-disabled/无 json_object/temp0）、
预算合同、日志账本等属于可复现性/安全机制；已有 150/150、450/450、1140/1140 零事故
证据即可（AB-6），不需要为它们再跑“去掉机制”的消融。

### 3.3 与 Barrientos 相关的已完成证据（借鉴对照，不是“整体 PK”）

**D/E 套件**（2026-08-29，用户授权，DeepSeek-V4-Pro-0813，1140/1140 真实调用，USD 6.11
记账成本，`barrientos_de_tables_v1.{json,md}`），四个分表各有职责、禁止互比 F1：
- **Table D（我方 prompt/few-shot 消融，EStG-150）**：full 0.772；去 few-shot、极简提示、
  换 Barrientos 风格结构约束三条臂 strict canonical F1=0（接口不兼容，raw 可解析率
  0.98–1.0，非空 canonical 0）。同一批 raw 的离线诊断证明 no-fewshot 的 0 分主要是
  **坐标接口崩溃**（247 个 clause 的 span 形状与 adapter 预期不符），不是语义能力为 0。
- **Table A（Barrientos-native 自评，36 条×5 次）**：precondition/norm F1 0.771/0.825
  均值、validity=1.0、coverage=1.0、fail=0、self-consistency=0.88——说明**在它自己的
  表示上、用它的评价器，原系统工作正常**。
- **Table C（共享目标，同一 Gold 同一度量函数，确定性 adapter）**：3 类 modality
  macro-F1：Barrientos 原生 0.890 vs 我方 0.822（prohibition 0.889 vs 0.800、permission
  0.781 vs 0.667、obligation 1.0=1.0）。**如实报告：在 36 条复杂语料的共享情态目标上，
  原生提示反而略好**；与此同时 actor/action/exception 等在 Barrientos schema 中
  not_expressible——即我们的六要素结构携带其表示表达不了的信息，两者无法“综合成一个
  数”。
- **Table B（我方评价器内模块替换）**：OURS-FULL 36×5 均值 F1 0.874（SD 0.003，稳定），
  换 Barrientos 模块 0.000（非空 canonical 率 0）。

**叙述准则**（写论文时）：这套证据用于“借鉴了什么、换上去为什么不行/哪里不兼容、
共享口径上谁强谁弱”，**不是**“我们整体优于 Barrientos”的证据；反过来的情况（Table C
共享情态目标对方更高）照实写。

### 3.4 已被撤回的 360 次方案（本次纠正，仅记录）

2026-09-05 曾准备“用 Barrientos 原始 FULL/NO-PATTERNS 两份提示在冻结 36 条上各 5 次
=360 次调用”的入口/合同/预检（checkpoint `2c5181e`，真实 API=0）。用户 2026-09-06
澄清这是对“借鉴其思路”的误解并**撤回**：研究定位是 Sun 为主干、Barrientos 为 Stage 2
借鉴来源，不做原生提示的原样对照执行。路线/状态/论文矩阵已原位标注；入口脚本与合同
作为历史证据保留，不再派工、不再等待授权。

### 3.5 优先核查项：Stage 2 → Stage 3 衔接（成对比较）现状

**要回答的问题**：Stage 2 的替换（Rules-Only vs LLM-SE 抽取）是否影响最终违规检测，
而不只是改变抽取分数。

**核验过程与结论**：
1. 项目里存在两组“同一 Stage 3 检测器”的运行（dev 的 Winter/Sun/BM25/TF-IDF 及其
   S3.9/S3.9-EXT 扩展），它们的规则输入全部来自**冻结 inference pack 的 9 段 GDPR
   条款文本**（article6/7/15/16/17/20/22/33/34；本次核验：58 个 matching/violation 项，
   9 段唯一 rule_text，每段 349–4,268 字符，绑定 7 个 GDPR-7 流程），即**规则侧是 GDPR
   条款、流程侧是 GDPR-7**——同法同域；
2. Stage 2 三方法的正式 predictions 全部在 **EStG-150**（税法句子）上，**没有任何
   EStG 预测被接到 GDPR 流程上**（也不允许：法规/流程/标签不对应）；而 GDPR 条款上
   **不存在任何 Stage 2 方法（B0/D1/H1）的预测产物**——`data/predictions/` 与
   `outputs/development/` 中没有这类文件；
3. 因此“把 Sun 式抽取与 LLM 抽取分别喂给同一个固定 Stage 3 检测器、比较下游违规
   检测结果”的成对比较**既无正式产物也无 development 产物**；S3.10（end-to-end 误差
   传播）、E00/E10/E01/E11、EXP-S2-E2E 在路线图上全部 blocked，与核验一致；
4. 9 个 GDPR rule 的正式 **Gold Rule Records（六要素人工裁决）不存在**——这是 Oracle
   与语料级 Stage 2 评价的前提，只能由用户裁决，Agent 不得创建/推断；
5. 相关门禁状态（fail-closed capsule `s2_13_s3_7_transition_readiness_v8.json`）：
   S2.11=frozen、S2.12=partial（两 API arms 未授权）、S2.13=blocked、S3.4–S3.6=dev-only、
   S3.7=not started。

**缺口表（同法衔接比较的最小前置）**：

| # | 缺口 | 现状 | 谁可补 |
|---|---|---|---|
| 1 | GDPR 条款句子级 Gold-blind Stage 2 输入合同（9 段条款需先确定性分句，类似 EStG-150 输入 v2 结构：source locator + 文本 hash + approved 句子文本） | 不存在；分句结果只隐式存在于 S3.9-EXT 面板的 rule bindings（sentence_idx/sentence_text） | 离线工程可做（零 API），需先定分句器与输入 schema |
| 2 | Rules-Only 在该输入上的预测 | 未运行（可零 API 跑，但要披露其 classifier 为德语合同、英文条款是 pass-through 的描述性限制，同 S2.12 零 API 臂的披露口径） | 离线可做 |
| 3 | LLM-SE / Rules+LLM-Repair 在该输入上的预测 | 未运行；需要**新的 API 授权与预算**（本提示不构成授权）；prompt 需按复杂语料口径复核 | 需用户授权 |
| 4 | 9 段条款的六要素 Gold Rule Records（人工裁决） | 不存在 | 用户 |
| 5 | 消费“预测 Rule Record”的固定 Stage 3 检测器适配与评价合同（把 E00/E10/E01/E11 落到可运行 runner） | 设计在路线图（§9.4/§10.2），无 runner | 离线工程（在用户对 §3.5-1/2 认可后） |
| 6 | 与 33 条 violation decision Gold（原三类）对齐的评价口径；新四类合成面板上同样做 S2 输入替换 | 33 条 Gold 存在；评价口径未定义 | 与 #5 一起 |

**结论**：衔接验证**尚未执行且不缺少“做了但没效果”的证据**——缺的是上述前置。最小
必要方案就是按 #1→#2→#3→#5→#6 顺序把 9 段条款做成可运行的 S2→S3 误差传播评测（先
dev、后按门禁 formal），其中 #4 决定能否同时评 Stage 2 语料级质量与 Oracle。**不能**用
EStG-150 的抽取结果冒充该评测，也**不能**把确定性抽取当作 LLM 输出。

### 3.6 Stage 3 类型扩展证据是否充分

**定义与区别**（`src/bpc_hybrid/stage3_extended_violations.py` + 面板
`data/development/stage3_synth/synthetic_controlled_error_extension_v2.json`，本次核验
40 变体 = 4 类×10，control+variant 成对、源 BPMN byte-unchanged、exactly-one-error）：

| 新类型 | 与三类原类型的区别 | 消费的六要素字段 | BPMN 检测面 | 变体手段（本次核验 mutation_config） |
|---|---|---|---|---|
| prohibited_action_present | 原类型管“该做的没做”；它管“**明令禁止的却做了**”（commission） | modality=prohibition + action | 活动/事件标签 | 插入被禁止任务 + 重连 flow（10 条，anchor/inserted task） |
| required_condition_not_enforced | 动作/actor/顺序都对的流程仍可能没落实触发条件 | condition + action | 网关标签/条件表达式/流标签/相邻控制节点 | 改条件表达式与 flow（10 条） |
| constraint_violated | 正确动作仍可能超时限/超量/用途越界 | constraint + action | timer/data-object/annotation | 时限矛盾（timer 2）、注解/数据对象改写（8 条） |
| exception_not_handled | 法条给例外，流程没有分支/处理器 | exception + action | boundary/error 事件、备选分支、handler | boundary 事件 5 条 + 分支/handler 5 条 |

**效果（全部 DEV_ONLY 受控合成，零 API；`s3_extended_violation_comparison_v2`）**：
- **variant-only（40 变体能否被检出）**：Winter-style 扩展 macro-F1 0.655/exact 0.550；
  Sun-style 0.333/0.300；BM25 0.226/0.150；TF-IDF 0.379/0.325。prohibited 最容易（平均 F1
  0.893），condition 最难（0.083）。
- **配对口径（40 合规对照 + 40 变体；会不会误报合规流程）**：control FP rate
  Winter 0.500 / Sun 0.125 / BM25 0.000 / TF-IDF 0.275；paired acc 0.225/0.175/0.100/0.300；
  5 类 acc 0.425/0.263/0.250/0.338。**也就是说：检测能力强的 Winter 式扩展在 40 个合规
  对照上误报一半**——能发现问题 ≠ 不误伤合规流程，两者必须同表呈现。
- **瓶颈（为何弱）**：unobservable 主因 action_mapping_below_gamma（92 条）——新四类
  继承原三类的动作映射瓶颈；冻结 GDPR-7 文件里无 conditionExpression、无 boundary
  event，命名网关藏在 subProcess 内（parser 视为不透明活动），所以 condition/exception
  的合规表面在很多变体上根本不可见（no_condition_candidates 等）；BM25 后端长标签分数
  天然 <0.5 属后端刻度性质，不是面板伪影。
- **边界（如实写）**：Winter/Sun 原论文未定义这四类，一律称 “-style extension”；40+40
  是**受控合成**，不是人工 Gold、不是 formal Oracle；**不能因为增加了类别就说检测能力
  全面提升**——按类别：prohibited=可行性支持、constraint=部分支持、condition/exception
  =主要揭示可观察性与映射瓶颈。33 条人工 Gold 无 Gold=none 样本，误报率在 33 条口径
  上不可证（33 条上只有 40 对配对口径提供了 control FP 证据）。

**充分性判断**：对“四类扩展在受控层面可行、哪些类型有证据、瓶颈在哪、会不会误报”
**证据已经足够**；对“四类在真实/正式 Oracle 上检测效果”**没有证据也不应有**（Oracle
未启动）。不需要再为这四类追加受控变体。

### 3.7 研究问题—证据总表

| 研究问题 | 对应实验 | 数据与指标 | 状态 | 可支持结论 |
|---|---|---|---|---|
| RQ1：Stage 2 传统/Sun/LLM 比较 | 三方法正式比较（2026-08-11） | EStG-150/150 条；粗+细 Gold；逐字段 P/R/F1+modality label | ✅ 完成（formal） | D1 领先 action/condition/constraint 与标签；B0 领先 actor/exception；H1 净负；无整体胜者声明 |
| Stage 2 消融：语义规则/示例/JSON 纪律 | 450-call 严格单因素（2026-08-30） | 同一 150/Gold/evaluator；ΔF1+逐字段 | ✅ 完成（真实运行） | 示例小幅正贡献（actor 最敏感）；语义规则/JSON 纪律无总体增益但有字段权衡；单次描述性 |
| Stage 2 消融：后处理模块 | D-full-0813 raw 离线单因素 | 同一 150/Gold/evaluator，0 API | ✅ 完成（离线重放） | canonicalizer 不可或缺（去掉 149/150 报废）；adapter/validator Δ0 仅此响应集 |
| Stage 2 消融：模块替换/借鉴对照 | D/E 1140-call（2026-08-29） | EStG-150（D）+36 条复杂语料（E）；四表分表 | ✅ 完成（真实运行） | 接口不兼容 0 分≠无效；共享情态目标上原生提示反而略高；六要素表达其表示表达不了的信息 |
| RQ2 复杂语料放大差异 | S2.12 三方法复杂语料比较 | 36 条（Barrientos requirements） | ⏸ 只完成 B0 zero-API arm；D1/H1 待授权 | 单一 arm 描述性结果（modality acc 0.639、span F1 0.831）；**不能**说三方法谁强 |
| RQ3 Stage 3 baseline/Oracle | S3.4–S3.6 dev + 阈值敏感性 | 33/25 decision Gold、7 流程 | ⏸ development 完成；formal Oracle blocked | dev 只供内部参考；阈值 0.6 为 tested best，非预注册 |
| RQ4 / 下游问题：Stage 2 替换 → Stage 3 检测 | E00/E10/E01/E11、S3.10 | 同法 Rule/Process Records → 33 条 Gold | ❌ 未执行（缺 §3.5 前置） | 无结论可写 |
| Stage 3 类型扩展 | S3.9-EXT 40+40（零 API） | GDPR-7 合成受控面板 | ✅ 完成（dev-only） | 按类型分列：部分强、部分仅揭示瓶颈；控制误报率如实（Winter 0.5） |
| 复杂度退化曲线（RQ2 的另一半） | G0.5 分层已冻结；L1/L2/L3 运行 | S2.12 36 条分层 | ⏸ 未完成（L3=0 无样本；两 API arms 未授权） | 不可报告 |

---

## 四、总结：证明了什么、还剩什么、论文怎么写

### 4.1 逐项回答

**① 当前实验已经证明了什么（可写进论文的正式结论）**
1. 在 EStG-150/150 条、同一 Gold 与 evaluator 下，LLM-SE 与 Rules-Only（Sun 方法级
   重建）**字段级互补**（D1：action/condition/constraint/标签；B0：actor/exception/
   高召回）；没有“一种方法全面胜出”的正式声明——这是 2026-08-11 正式比较与正式结论包
   支持的（描述性、无显著性推断）。
2. 无证据约束的 Rules+LLM-Repair 是**净负对照**（全量 150 运行 F1 0.7621 vs 0.7986，
   actor P 崩塌）——支持“修复必须被证据约束”的论证。
3. LLM-SE 的六个语义合成示例有**小幅总体正贡献**（Δ−0.0069，actor Δ−0.1317）；
   详细语义规则与显式 JSON 纪律在当前模型/数据上**无总体正增益**（Δ+0.0040/+0.0071），
   但存在字段级正作用（action、exception）——因此**如实写“未测得增益”，不写“无用”**。
4. 坐标重锚器是后处理链的**功能必需件**（去掉 → 149/150 无效、F1 归零）；adapter/
   validator 在这批响应上 Δ0，只作兼容/安全职责叙述。
5. Barrientos 借鉴边界：其 schema/表示与我们不同 → 模块替换的 0 分是接口不兼容证据；
   共享 3 类情态目标上原生提示 macro-F1 0.890 vs 我方 0.822（36 条复杂语料）——照实写。
6. Stage 3 四类扩展在**受控合成**层面：禁止动作类检出可行（F1 0.893 均值）；约束类部分
   可行；条件/例外类主要受 BPMN 表面与动作映射限制；合规对照误报率 0.000–0.500 按方法
   如实报告。
7. 三方法共享同一冻结输入/Gold/schema/evaluator 的**正式机器门禁就绪**（final gate
   true 仅指 Stage 2 正式评价门禁，不代表 S2.13/S3.7/全 Pipeline）。

**② 哪些结果只是初步支持（development/单次/归因）**
- 早期粗/细口径归因数字（0.7986/0.8726、0.7186/0.7756）、Sun-marker 收敛（constraint
  R=1.0/13）是 development 归因；D1-R1→R3 的修复轨迹是 development 证据；
- 后处理/诊断离线重放是回顾性证据；450-call 与各消融均为**单次描述性**运行（无显著性）；
- S2.12 B0 zero-API arm（36 条复杂语料）是单臂描述性；Stage 3 的 S3.4–S3.6、S3.9、
  S3.9-EXT、阈值敏感性全部 DEV_ONLY；阈值 γ=0.6 只是 tested best，不是预注册/最优声明；
- Stage 1 P2 评价是固定 GDPR-7 描述性组件评价（post-Gold、target-aware、非 held-out）。

**③ 哪些主张还没有证据（禁止写成结论）**
- “Stage 2 用 LLM 替换会改善（或损害）最终违规检测”——**无任何同法成对实验**（§3.5）；
- “复杂语料放大 LLM 优势”——S2.12 只有单臂，未完成；
- “Stage 3 Oracle/正式性能、端到端提升 E10/E11”——Oracle 未启动；
- “四类新错误全面提升检测”——与 40+40 数据矛盾（按类型差异大、误报率不低）；
- 任何把 EStG 抽取结果接到 GDPR 流程、或把 dev 数字当 formal 的表述。

**④ 现有消融是否够用**
够用。AB-1/2/5/5b（prompt 语义模块与后处理模块）已有严格单因素；AB-3 离线覆盖投影、
AB-6 零事故、AB-7 口径敏感性、AB-8 规则模块批次、AB-9 稳定性均已结项；AB-4 纯受控词汇
与 AB-10 style-equivalent 是**可选**补充而非缺口（跨 schema 本来只能定性叙述）。结论：
**不再为了凑 AB 编号或模块清单追加实验**；工程机制（预算/账本/日志）不做消融。

**⑤ 剩余必要工作**

【必须完成】（最小路径，按依赖排序）
1. 维持门禁线：S2.11 已 frozen → 用户一次性内容确认（proposal v3 已就绪）→ S2.12 两
   API arms 授权与运行（63 calls，授权缺项已列出）→ S2.13 冻结；这些是正式结论与
   S3.7 的前提，属既有主线，不需要新实验设计；
2. 用户裁决并冻结 9 个 GDPR 条款的 Gold Rule Records（人工，Agent 不得代做）；
3. S2→S3 同法衔接评测的**离线前置准备**（§3.5 缺口 #1/#2/#5/#6）：9 段条款的句子级
   Gold-blind 输入合同 + B0 zero-API 预测 + 固定 Stage 3 消费“预测 Rule Record”的
   runner/评价合同（先 dev 口径、零 API、不冒充 formal）——**本次会话未执行**（本次只完成
   核查与准备说明），需要你确认后再动工；
4. S3.7 formal Oracle 单独授权与运行（依赖 1+2+3 的正式侧）；
5. 论文按 §4.2 表述回填正式结果（PW7/PW9），主张矩阵同步（C 表增行）。

【可选增强】（不是必须）
- S3.9-EXT 若想补“条件/例外”的正面证据：给冻结模型补充可解析的条件/例外表面（如把
  命名网关移出 subProcess 或扩展解析器）后再跑同面板——但**这属于扩大解析范围的新
  实验设计，需要你的决定**；
- AB-4 纯受控词汇隔离与 AB-10 style-equivalent 敏感性（如需支撑方法章节的“受控词汇
  贡献”表述）；
- Stage 2 复杂度退化曲线（需 S2.12 API 臂完成后按 L1/L2/L3 报告）。

### 4.2 论文应如何准确表述贡献与局限（措辞清单）

- 定位句：三阶段主干与改进对象 = Sun；Barrientos = Stage 2 LLM 方案（LLM-SE）的
  “结构化输出+校验+受控词汇+评价纪律”借鉴来源；**不写“整体优于 Barrientos”**；
- Rules-Only = Sun Stage 2 的 *method-level independent reconstruction*（非 exact、
  非作者原代码；Tsurgeon 诚实非实现、词典/分词适配披露）；EStG-150 = 项目独立重建
  benchmark（非 Sun 原 150/443 spans）；Gold = LLM-assisted, human-adjudicated；
- 正式数字只引 `stage2_formal_three_method_comparison_v1`（2026-08-11）与各 manifest；
  消融/后处理数字标注“单次描述性/离线回顾”；S3.9-EXT 一律 DEV_ONLY 且按类型分列、
  附 control FP；Stage 1 评价写 fixed-GDPR7 描述性（非 held-out）；
- 禁止句：不得用 EStG 数字接 GDPR 流程；不得把 dev 当 formal；不得把接口不兼容的 0
  分写成对方方法无效；不得因 450/450 成功声称“全部模块已验证”；不得把 1140 次调用
  说成“所有模块均消融”；不得把 33 条人工 Gold、30 条 v1、40 对 v2 三套口径合并；
- 局限段必须有：无同法端到端证据、Oracle 未启动、Gold Rule Records 缺失、单次运行无
  显著性、合成面板非真实场景、BM25 后端刻度、BPMN 解析表面限制、EStG 许可限制。

---

## 5. 关键证据文件索引（本次核对过）

- 正式三方法比较：`outputs/reports/stage2_formal_three_method_comparison_v1.{json,md}`
  （manifest dc41eb4b、verifier VERIFIED）；评测存储：`data/results/*_formal_arm_v1/`
- Prompt 单因素：`outputs/reports/d1_prompt_factorial_results_v1.{json,md}`（事件 #311，
  450/450、USD 3.365）；后处理单因素：`outputs/reports/d_full_postprocessing_ablation_v1.md`
- D/E 套件：`outputs/reports/barrientos_de_tables_v1.{json,md}`（事件 #307，1140/1140）
- S3.9-EXT：`outputs/reports/s3_extended_violation_comparison_v2.{json,md}`、面板
  `data/development/stage3_synth/synthetic_controlled_error_extension_v2.json`（事件 #312/#313）
- 衔接门禁：`outputs/reports/s2_13_s3_7_transition_readiness_v8.*`、inference pack
  `data/development/human_review/stage3_gold_inference_v1.json`（58 项/9 段条款/7 流程）
- 撤回记录：`MASTER_PIPELINE.md` §8.8.4/§15(3.6.35)、`PROJECT_AUDIT.md` §1、
  `paper/ABLATION_MATRIX.md` 顶部（2026-09-06）；准备产物保留于 checkpoint `2c5181e`
