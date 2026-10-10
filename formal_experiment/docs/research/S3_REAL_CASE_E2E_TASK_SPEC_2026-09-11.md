# 任务书（提案）：SIM 卡入网案例实验（S3.9-EXT-REAL-CASE，Case C）

> **状态：PROPOSED — 未授权、未登记、未执行。** 本文只是方案与验收标准，供用户审阅，
> 不是 pipeline 任务行、不是状态页、不是实验结论。批准后按 §11 做治理登记。
>
> 日期：2026-09-11　范围：`formal_experiment/`　**真实 API 调用：0**（复用已授权历史运行产物）
>
> **v5 修订（2026-09-11，用户指令：本指令替换此前待确认的执行安排）**：本任务**已获授权执行**，
> 不再等待逐项确认。主实验固定为 **当前 SIM BPMN × v2 非空规则 = 5 条**（r8/v2、r9/v2、r10/v2、r11/v2、r13/v2）；
> r12 作为"需求删除 + 外部 over-compliance"背景单列，不进分母；空文本条目（r9/v1、r12/v2）不进入抽取与检测。
> **标准答案不得依赖检测器能力**：参考判断只陈述流程与规则的语义问题，方法输出单独记录，二者分开存；
> 禁止"匹配成功才算违规""角色解析成功才算违规""检测器不支持所以不是违规""无法判断所以不算漏检"。
> r13 数值边界明确为 `debt > 50` 触发禁止、`debt = 50` 不触发、`50 < debt < 100`（例 75）为差异区间；
> 外部建议 `Debt < 500` 保留为来源冲突、不采用。角色绑定固定为
> `Data Controller → Phone company`、`Data Subject → Customer`，打分前写入运行计划。原 Q1–Q10 待确认表作废，
> 改为 §10 的"已决事项"。三组 A/B/C 必须实际运行，逐组记录组件、配置、阈值、输入与代码版本。
>
> **v4 修订（2026-09-11，按用户指令返修）**：范围收缩到 **Case C（SIM）**；取消"按类型映射评分"的做法
> （映射表降级为阅读辅助，**不是评分键**）；**不预设方法能检出全部违规**；新增 §3.5 逐项核对证据、
> §5.3 评价标准先行（核对表）、§5.4 三组 A/B/C 归因设计、§5.6 能力核实、§5.7 六态区分；
> 修正 v3 的两处事实错误（SIM 真实预测是 **10 条独立输入 × 5 轮**不是 11 条；
> "Ask for consent" **已存在**于流程中）。v3 及更早保留为本文修订历史。
>
> **v3**：新增 Case C 与 C-E2/C-E1 路线。**v2**：契约测绘证明不需要新增规则绑定器。

---

## 1. 目标

在**同一流程、同一规则版本、同一公共适配政策**下，用我方三阶段方法对 SIM 卡入网案例做逐条检测，
输出**逐条结果 + 标注图**，并解释两个创新点各自的贡献：

- **A**：Sun 式重建基线（原三类检测）。
- **B**：Stage 2 换成已有真实 LLM 抽取，保留与 A 相同的原三类检测。
- **C**：与 B 完全相同的 LLM 抽取与原三类检测，**再加入四类扩展检测**。

A→B 解释 Stage 2 的变化；B→C 解释 Stage 3 扩展的变化。**不预设 LLM 或扩展方法一定更好。**

## 2. 范围与定位

**做**

- 主案例：**Barrientos 的 Sun 派生 SIM 场景**（`references/barrientos_2026/**`，只读）。
- 补充案例：依据**本地 Sun PDF Figure 10 重建**的流程（标注为重建件）。
- 结果定位：**论文可用的开发性案例分析**。

**不做**

- 不扩大到 GDPR、emergencies、blood donation 或其他场景；**不为覆盖七类而增加案例**。
- 不称为作者原始实验复现、不称为独立测试、不称为真实企业验证。
- 不修改冻结算法、不为本案例加特判、不搜索阈值、不改 Gold、不新增 API 调用。

**四类物件的准确称谓（全文强制）**

| 物件 | 称谓 | 说明 |
|---|---|---|
| Sun 论文 §5.4 的流程 | **文献案例（literature case）** | 只有图，无可得机器可读模型 |
| Barrientos `SIM_card_scenario.bpmn` | **派生案例（derived case）** | Sun 派生，含图外元素；非 Sun 原图 |
| 按 Figure 10 重建的 BPMN | **重建模型（reconstructed model）** | 我方按图重建，非作者原文件 |
| 为对照而人工修改的流程 | **人工修改的对照模型（human-modified control）** | 必须独立命名、保留原图、披露修改 |

## 3. 输入事实（逐项核对证据，2026-09-11）

### 3.1 绑定与哈希

| 物件 | 路径 | 事实 |
|---|---|---|
| 流程模型 | `references/barrientos_2026/artifact_input/process_models/SIM_card_scenario/SIM_card_scenario.bpmn` | sha256 `338c8144…`，67,048 B；3 个 process/participant（Customer、Phone company、Another phone company）；3 个**无名 lane**；11 个 task + 1 个 subProcess（Store Data）；4 exclusive + 2 parallel gateway（**全部无名**）；**timer 事件 = 0**；**boundary event = 0**；`conditionExpression` = **0**；带标签 sequence flow = **4** 条：`Not requested`、`Requested`、`Granted`（状态标签）与 **`Debt < 100`（唯一数值条件）** |
| 需求（规则） | `.../requirements/SIM_card_scenario/SIM_card_scenario.json` | sha256 `e13d9a2a…`；12 条 = r8–r13 × v1/v2；**r9/v1 与 r12/v2 文本为空** |
| 外部答案键 | `.../evaluation/ground_truth/step_3_baseline.json` | sha256 `96b3c1e8…`；每条需求 `deviations[] = {type, bpmn_element, element_label}` + `mitigation_action` |
| 变更答案键 | `.../evaluation/ground_truth/step_2_baseline.json` | 每条需求 `changes[]`：r8 情态 P→O、r9 add_requirement、r10 change_in_role、r11 情态 P→O + switch_compliance_pattern、r12 delete_requirement、r13 change_in_data |
| 需求表示 | `.../evaluation/ground_truth/step_1_baseline.json` | 每条需求 `versions{version_1,version_2}{precondition,norm}`；**r8–r13 的 `both_versions` 全为 false** |
| 真实 LLM 预测 | `outputs/development/barrientos_ablation_suite_v2/OURS-FULL/repeat-01..05/canonical_predictions.jsonl` | **SIM 独立输入 10 条/轮 × 5 轮重复**（r8v1、r8v2、r9v2、r10v1、r10v2、r11v1、r11v2、r12v1、r13v1、r13v2）；r9v1 与 r12v2 因空文本未调用 |
| Sun 本地 PDF | `references/papers/Sun_2024_Design_time_BPC.pdf`（+ 抽取文本） | 合同登记为**预印本**；**正式版不可取得**（Springer 付费墙/机构认证，本轮核对失败） |

### 3.2 流程结构（实测）

`New client acquired → Request personal data →(catch)→ gateway → Ask portability / Ask old number → Ask portability third company →(deny)→ Delete personal data；→(else)→ Assign new number → Sign contract →(parallel)→ Request payment → Payment received`，
`Sign contract →(parallel)→ Store Data → **Ask for consent** → Send SIM card`，`Request payment → Payment received → Send SIM card`；
`Activate SIM card` 位于 **Customer** 泳道（未被 `Send SIM card` 的后续触发）。

**关键结论**：`Ask for consent` **已存在**（sid-9D265428，Phone company 泳道），但位于 `Store Data` **之后**。

### 3.3 需求版本内容（实测，短片段）

| ID | v1 | v2 | 变更类型 |
|---|---|---|---|
| r8 | 可超过 30 天寄卡（permission） | 超过 30 天必须终止流程（obligation + 时限） | 情态 P→O |
| r9 | **空** | 收到个人信息后须核验其正确性 | add_requirement |
| r10 | 由**客户**负责激活 SIM 卡 | 由**电话公司**激活 SIM 卡 | change_in_role |
| r11 | 电话公司**无义务**征得同意 | **取数前**须向数据主体取得同意 | 情态 P→O + switch_compliance_pattern |
| r12 | 第三方拒绝携号转网时须删除个人数据 | **空**（需求删除） | delete_requirement |
| r13 | 欠款**超过 100 EUR** 不得领取新 SIM 卡 | 欠款**超过 50 EUR** 不得领取新 SIM 卡 | change_in_data |

### 3.4 外部答案键（原文，实测）

| ID | type | bpmn_element | element_label | mitigation（摘） |
|---|---|---|---|---|
| r8 | non_compliant | `missing_timer` | process termination | 加 timer，超过 30 天终止 |
| r9 | non_compliant | `missing_activity` | **Sign contract** | 在 "Sign contract" **之前**增加核验客户个人信息的活动 |
| r10 | non_compliant | `wrong_role` | Activate SIM card | 应由电话公司执行 |
| r11 | non_compliant | `missing_activity` | **Request personal data** | 电话公司应执行一个名为 "ask for consent" 的新任务 |
| r12 | over_compliant | `redundant_activity` | Delete personal data | （无） |
| r13 | non_compliant | `XOR_condition_modification` | **Debt < 100** | 应把 `Debt < 100` 改为 **`Debt < 500`** |

**该表是外部来源的原始标注，不是我们的 Gold，也不是评分键。**

### 3.5 七项核对结论（用户指令第二部分逐项）

1. **r9 `element_label = Sign contract` 是定位参照，不是缺失动作**（已证实）。
   真正缺失的是 `mitigation_action` 指明的**核验个人信息活动**，`Sign contract` 只提供插入位置基准。
   → 不得把 `Sign contract` 当作缺失动作；映射到我们的 `missing_action` 必须以
   "核验正确性"这一动作要求为单位，并显式记录插入位置语义。
2. **r11 的活动已存在但位置错误**（已证实）。`Ask for consent` 存在于 Phone company 泳道，
   但流序为 `Store Data → Ask for consent`；外部标注仍写 `missing_activity`。
   → 必须区分**活动完全缺失 / 前置位置缺失 / 顺序错误**三种情形；不得机械映射为 `missing_action`；
   **不得为符合答案而删除或移动现有活动**。
3. **r13 数值冲突**（已证实）。需求 v2 阈值 = **50 EUR**；流程条件标签 = `Debt < 100`；
   外部 mitigation 写 `Debt < 500`。三处互不一致。
   → 保留原始文件不改；记录冲突；比较时必须显式说明**大于 / 小于 / 等于边界**
   （"exceeding 50" 是严格大于；标签 `Debt < 100` 是严格小于；边界值不属于任何一侧）。
4. **`step_3_baseline.json` 是"需求 v1→v2 变化对流程的影响"评价，不是静态合规检查的天然答案键**（已证实）。
   证据：r12/v2 为空（需求删除）而其偏差是 `over_compliant/redundant_activity`；r9/v1 为空而偏差是"缺活动"；
   r10 的 mitigation 对应 **v2** 文本。→ 明确绑定：**流程文件（sha `338c8144…`，单一版本）× 需求版本 v2**；
   评价单位 = 每条需求（id），不是每个版本对；`both_versions` 在 r8–r13 全为 false，
   **不能解释为"该需求在 v1/v2 都存在"**；空文本（r9/v1、r12/v2）**不得作为普通规则进入抽取与检测**。
5. **SIM 真实预测计数更正**（已证实）：**10 条独立输入 × 5 轮重复 = 50 行**，不是 11 条。
   → 报告必须分别给出**独立输入数（10）、版本数（10 个 (id,version) 组合）、重复次数（5）**；
   重复运行不得当独立样本，不得择优挑选某一轮。
6. **抽取/表示问题（已证实，不得用答案键补齐）**：
   - **全部 10 条预测的 `order_relations` 均为 0**（不只是 r11）——该臂无任何顺序信息；
   - r13 v1/v2：欠款门槛落在 **actor span**（"Customers with outstanding debt exceeding 50 €"），
     `conditions`/`constraints` 为空 → 数值边界不可用；
   - r9 v2：actor 抽取为代词 **"it"** → 执行者不可用；
   - r8 v2：captured `action='terminated'`（被动分词）、`condition='if it takes more than 30 days…'`、
     `constraint='more than 30 days'`，但 **actor 为空**；
   - r11 v2：`condition='Before retrieving…'` 存在，但无 `order_relations`；actor = `the Data Controller`
     （场景角色绑定问题，见 §5.5）。
7. **Sun 正文与 Figure 10 的 R2/R4 分类不一致**（已证实，本地预印本）：
   正文（p.23，L957–973）称 R1、R4 = missing action、R2 = out-of-order、R3 = incorrect actor；
   Figure 10（p.24）标注 V1/R1、V2/R2 = Missing Action、V3/R3 = Incorrect Actor、V4/R4 = Out-of-order。
   → 保留两种原始说法；**正式版本轮核对失败（付费墙）**，因此**不得声称正式版有同样问题**，
   也不得把两套冲突标签当作两套可靠 Gold。

### 3.6 类别映射表的定位（v4 更正）

v3 的"外部 `bpmn_element` → 我们七类"映射表**降级为阅读辅助**：
**不得作为评分键、不得用于生成期望结果、不得用于反推缺失字段**。
评分只依据 §5.3 的核对表（逐条、含来源与理由）。

## 4. 输入与复用清单

| 用途 | 路径 / 符号 | 复用方式 |
|---|---|---|
| 流程模型对象 | `sun_stage3/sun_model.py` `SunProcessModel(process_id, record, nlp)` | 原样复用 |
| 流程解析（用于把 references 内 BPMN 变成 Process Record） | `stage1_process.parse_bpmn_bytes/validate_process_record` + 冻结结构合同 | 原样复用；**不把 BPMN 复制进仓库**，只读原路径并记录哈希 |
| 三类检查器 | `sun_stage3/sun_scorer.py`（Sun 式）、`s3_action_matching_v3.EvidenceChecksV3` | A 用 Sun 式；B/C 与其保持一致 |
| 四类检查器 | `stage3_extended_violations.py`、`s3_extended_evidence_scope_v1.ScopedEvidenceScorer` | 仅 C 组启用 |
| 规则侧（A 组） | 由 r8–r13 **v2** 规则文本经**公共适配政策**构造的 rule record | 新实现，policy 见 §5.5 |
| 规则侧（B/C 组） | `outputs/development/barrientos_ablation_suite_v2/OURS-FULL/repeat-0N/canonical_predictions.jsonl` | **仅在规则文本、版本、来源核验一致后复用**；不可复用条目明确列出 |
| 评价口径 | `evaluate_stage3_common`、`s3_extended_unified`、`control_prediction_from_scores` | 复用，不新造指标体系 |

**复用前置条件（逐条核验，不通过即列入"不可复用"清单）**：
预测的 `sample_id` 必须能对应到 (rule_id, version) 与当前需求文本哈希；文本或版本不一致者不得复用；
**不得用人工参考抽取冒充真实预测**。

## 5. 方法

### 5.1 三组定义（固定不变量）

| 组 | Stage 2（规则记录来源） | 原三类检测 | 四类扩展检测 |
|---|---|---|---|
| **A** | 由 v2 规则文本按公共适配政策构造 | Sun 式重建（`sun_2024_frozen` 语义） | ✗ |
| **B** | 已有真实 LLM 抽取（OURS-FULL） | **与 A 逐字相同** | ✗ |
| **C** | **与 B 逐字相同** | **与 B 逐字相同** | ✓ 四类 |

固定不变量：同一流程文件与哈希、同一需求版本（v2）、同一适配政策、同一评价口径。
**除表中被替换的组件外，其它检测器改动一律不得混入 A→B 或 B→C 的归因。**

### 5.2 输出结构（逐条）

每条 (需求, 检查类型) 输出：`status ∈ {violation, compliant, unobservable, not_applicable}` +
`reason_code` + `evidence`（元素 ID / 文本片段 / 哈希）+ `stage_attribution`
（该结果是抽取导致、适配导致、还是检测导致）。运行前写 `plan.json` 并绑定实现哈希；
预测先落盘，再读答案键；支持 `--check` 与 `--replay`。

### 5.3 评价标准先行（核对表，交付物 #2）

**在运行比较之前**建立逐条核对表，至少含：

`规则 ID 与版本 | 流程版本 | 规则含义 | 实际流程证据 | 外部原始标注 | 冲突说明 | 建议预期结果 | 理由 | 是否需用户确认`

- 外部答案键、专家标注、Winter 输出**分别保存来源**，先确认评价对象与口径是否可比；
- **不把专家意见当作额外的方法实验组**；**不因为文件机器可读就称其更可靠**；
- 争议条目给出具体建议并集中交用户确认（§10）；**Agent 不替用户确认人工答案、不改 Gold、不设人工批准状态**；
- 等待确认期间继续完成不依赖答案的工作（输入核验、适配、输出结构、实现）。

### 5.4 归因要求

阶段差异表必须把每一处变化归到：**抽取 / 适配 / 检测**之一，并给出逐条证据；
无法归因的记为 `unattributed`，不得默认归因于方法创新。

### 5.5 公共适配政策（先声明、统一使用、记录在案）

- **场景角色绑定**：GDPR 类角色到场景角色的绑定（如 `Data Controller → Phone company`）必须在**看到任何
  预测结果之前**声明为固定策略，全组统一使用并写入 `plan.json`；**不得按结果添加特判**。
- 该政策独立于预期违规标签；Sun 论文本身也声明做过同类人工转换（正文 L968–973）。
- 任何针对单条需求的额外绑定都必须走同一流程并单独记录。

### 5.6 检测能力核实（不得只做接线）

逐项核实并记录结论（支持 / 部分支持 / 不支持 + 证据）：

1. **条件触发的流程终止**（r8：超过 30 天 → 终止）；
2. **带数值边界的条件性禁止**（r13：欠款阈值 + 严格/非严格边界）；
3. **同意与取数之间的先后关系**（r11：取数前须同意）；
4. **跨参与者的活动归属**（r10：Activate SIM card 属 Customer 泳道）。

**现有时间上限比较不得自动等同于"超过 30 天则终止"检查**：时限比较只说明"存在一个数值边界未被满足"，
不等于"缺少终止分支"这一流程结构缺失。缺少所需语义时**如实记录能力限制**，
**不修改冻结算法、不加案例特判**。

### 5.7 六态区分（评价与报告强制）

每条必须归入且只归入一态：

1. 规则本身不要求该检查（`not_applicable`）；
2. **抽取遗漏**导致信息不足；
3. **适配丢失**信息；
4. **流程表达不足**（模型没有该表面）；
5. **检测器能力不足**；
6. 有证据的**违规或满足**。

禁止：把空预测字段直接当"规则不适用"；把"无法判断"当合规；评价已确认违规条目时把"无法判断"
从分母中**悄悄删除**（分母与不可判计数必须同时呈现）。

## 6. 交付物

1. **修订后的任务书**（本文，原地修订）；
2. **逐条来源、版本与预期结果核对表**（§5.3）；
3. **A/B/C 三组真实运行结果**：含检测依据、漏检、误报、无法判断及原因；
4. **阶段差异表**：解释变化来自抽取、适配还是检测（§5.4）；
5. **类 Figure 10 结果图**：标注**来自实际输出**（不是抄论文标注）；
6. **论文可用案例说明**：明确结果适用范围与不可声称事项。

**输入纯净性（强制）**：预测输入不得包含标准答案、外部偏差标签或图中的 Violation 标注；
修复建议不得进入判定输入。

**误报检查优先**：优先利用已有正常对照（C-E2 的对照对象 / 未修改原图）检查误报。
**若确需构造修复模型**：只创建**独立的开发派生件**，保留原图、披露修改内容，并在比较前确定预期结果。

**报告口径**：单案例以逐条结果与计数为主；**不拼接"七类总 F1"**；不预设 LLM 或扩展方法更好。

## 7. 限制与不可声称

### 7.1 已知限制

- 外部答案键面向"需求变化"语境，不是静态检查答案；r9/r11 的 `missing_activity` 与 r13 的 mitigation
  经核对**与当前模型/需求不一致**（§3.5）。
- 模型**无 timer、无 boundary event、无 conditionExpression**；条件只以 sequence-flow 标签存在
  （4 条带标签 flow，其中仅 `Debt < 100` 为数值条件，另 3 条为状态标签）。
- 无"合规对照"人工 Gold；Barrientos 语料许可证为 `unknown_pending_confirmation`（本地只读、不可再分发）。
- Sun 案例的机器可读模型不存在；C-E1 是重建件；正式版不可取得。

### 7.2 不可声称

- 不称作者原始实验复现、不称独立测试、不称真实企业验证；
- 不称"我们的方法在真实案件上有效 / 优于 Sun / 优于 Winter / 优于 Barrientos"；
- 不称"四类都已在真实数据上验证"；
- 不称正式 Oracle、真实法律合规结论；
- 不把案例结果并入 33 条人工 Gold、40 对合成面板或 36 条 Barrientos 正式 Gold 的任何表格。

## 8. 分批计划（每批独立 checkpoint）

| 批次 | 内容 | 交付 |
|---|---|---|
| **C0** | 本任务书 v4 + 七项核对证据 + 逐条核对表 | 交付物 #1、#2；争议条目清单（§10） |
| **C1** | 输入绑定与适配：流程记录、规则记录（A 组政策）、可复用预测清单、输出结构与 schema | 可复核的输入胶囊（哈希绑定） |
| **C2** | A/B/C 三组运行（先存预测，后读答案键） | 交付物 #3 |
| **C3** | 阶段差异表 + 能力核实报告（§5.6）+ 六态归类 | 交付物 #4 |
| **C4** | 类 Figure 10 结果图（据实际输出）+ 论文案例说明 | 交付物 #5、#6 |
| **C5** | （补充）C-E1：Figure 10 重建 + Table 13 R1–R4，两种论文读法分别报告 | 重建件与复刻结果 |

## 9. 执行边界

- 遵守根目录与 `formal_experiment/AGENTS.md`；所有活动实验改动在 `formal_experiment/`；
  `references/`、`archive/` **只读**；不把受限原文、原图或禁止再分发的材料提交进仓库；
  提交产物只允许 ID / 标签 / **短片段（<40 字符）** / 计数 / 哈希 / 判定，完整文本只落 local-only 目录。
- 本轮**不新增真实 LLM/API 调用**，不挪用历史预算，不读不打印 `.env`。
- 文档改动只做内容检查；实现改动按变更范围做**快速完整性检查 + 相关聚焦测试**；
  本指令**不授权全量测试**，也不授权绕过 Gold、数据激活或阶段冻结门禁。
- 每个完整批次：记录事件、明确暂存、提交并**非强制**推送到当前分支配置上游；
  保留用户无关修改与 `.bak` 文件；**推送被阻塞时报告本地提交哈希与具体原因，不声称已远程备份**。

## 10. 已决事项（用户 2026-09-11 指令直接采用，原 Q1–Q10 待确认表作废）

| 事项 | 决定 |
|---|---|
| 执行授权 | 本案例所需的常规实现、适配、development 输出 schema、任务登记、离线运行、分析与图表、论文素材**均已授权** |
| 任务 ID | `S3.9-EXT-REAL-CASE`；在 MASTER_PIPELINE / AGENT_RUNBOOK / PROJECT_AUDIT 原地登记 |
| 主实验规则集 | 当前 SIM BPMN × v2 非空规则 = **5 条**（r8/v2、r9/v2、r10/v2、r11/v2、r13/v2） |
| r12 处理 | 作为"需求删除 + 外部 over-compliance"背景单列，**不进 5 条分母**，不作合规证据 |
| 空文本条目 | r9/v1、r12/v2 **不进入**普通语义抽取与检测 |
| r9 检查对象 | 缺失动作 = "核验客户个人信息"；`Sign contract` 仅为定位参照 |
| r11 定性 | 同意活动存在但位于取数/存数之后 → **前置位置/顺序问题**，不按活动缺失评分 |
| r13 边界 | `debt > 50` 触发禁止；`debt = 50` 不触发；`50 < debt < 100`（例 75）为差异区间；外部 `Debt < 500` 不采用 |
| 参考判断口径 | 开发参考判断，非正式 Gold、非用户逐条人工标注；与检测器能力**解耦** |
| 角色绑定 | `Data Controller → Phone company`、`Data Subject → Customer`；打分前写入计划，全组统一，禁止按结果加特判 |
| 预测复用 | 5 轮历史预测先核验来源/版本/完整性；**预先固定 repeat-01 为主展示**，其余 4 轮只作稳定性，不择优 |
| Sun 冲突标签 | 两种读法均保留为文献原始声明，均不作可靠 Gold；**取得正式版不是继续执行的前提** |
| 正常对照 | 授权在本案例内创建少量独立 development 修复对照（每项最多一个最小修复件） |
| 指标口径 | 不合成七类总 F1；5 轮重复不作 25 个独立样本；无有效正常对照时不得宣称零误报 |

### 10.1 逐条记录要求（①②③④⑤）

每条规则必须分别记录：**① 流程与规则的语义问题**（与检测器无关）、**② 本轮采用的开发参考判断及其来源**、
**③ 方法实际输出**、**④ 两者是否一致**、**⑤ 差异来自哪一阶段**（extraction / adaptation / detection /
process_expressiveness / rule_not_applicable / unattributed）。① ② 存于
`data/development/sim_case_c1/case_items_v2.json`，③④⑤ 只由运行胶囊填充，**不得回填**。

## 11. 问题与处理表（P4，2026-09-11 第二轮）

| # | 问题表现 | 发生阶段 | 根因证据 | 处理方式 | 验证结果 | 是否关闭 | 影响的主线步骤 |
|---|---|---|---|---|---|---|---|
| 1 | A 组用简化确定性抽取器代表 Sun 式基线 | P1 组件错配 | `capsule.plan.groups.A` 旧值为 "non-LLM deterministic adapter" | 接入项目锁定非 LLM 基线 B0 v10a（`run_b0_batch_v10`，PROFILE_V10A，CoreNLP+Tregex+BERT-TextCNN） | A 计数由 5/9/1 变为 **3/10/2**；`sides.A.stage2_meta.source=sun_rule_only_b0_v10a` | **已关闭** | P2、P3 |
| 2 | C 组调用旧 `ExtendedViolationScorer`，未用已验收修复 | P1 组件错配 | pipeline 3.6.51/3.6.52：REPAIR-V2 的 C 臂（v3 定位 + 比较门）是当前口径 | 改用 `RepairedExtendedScorerV2`（v3=EvidenceChecksV3 γ0.8、标签回退 0.4、γ_ext 0.5）+ `aggregate_with_comparison_gate` | C 计数由 8/25/2 变为 **10/23/2**；gate 现能区分“比较过/未比较”（r8、r10 各 2 次证据比较，r9/r11/r13 为 0） | **已关闭** | P2、P3 |
| 3 | r9/r11 的顺序关系在三组都缺失 | P1 适配缺陷 | 旧正则要求 before/after 片段含逗号，而抽取结果是 `After receiving the customer’s personal information`（无逗号） | 改为逗号可选（`comma_optional_v2`），并提供有逗号 / 无逗号 / 非顺序条件三类验证 | r9/r11 的 B 组记录出现 `order_relations`（`derived_by_declared_policy`）；检查仍报 `no_mapped_rule_order_endpoints` | **适配部分已关闭；剩余为映射能力限制**（见 #5） | P2、P3 |
| 4 | 修复件被二次扁平化，与原图处理不一致 | P1 适配缺陷 | 修复输入已是扁平化 XML，`_parse_flattened` 再次调用 `flatten_collaboration` | 加 `already_flattened=True` 分支 | 5 个修复件的独立结构核验 `fix_expressed` 全为 **true** | **已关闭** | P4 |
| 5 | r8 修复件的计时范围与规则语义不符 | P4 修复语义 | 修复把 30 天计时器挂在发卡任务上，规则要求的是整流程超时终止 | 保留最小修复件，但显式记录 `scope=task_scoped_timeout`、`scope_matches_rule_semantics=false` 与前提说明 | 独立核验 `fix_expressed=true`、`scope_matches_rule_semantics=false`；检测前后均为 `violation`（方法侧） | **已关闭（作为已声明的部分表达）** | P5 |
| 6 | r13 的“是否检出”存在报告/图/论文不一致风险 | P4 一致性 | 参考视角（条件）未检出，但另有附带检出（`incorrect_actor`、`prohibited_action_present`） | 以运行胶囊为唯一口径，三处统一 | 结果表、图、论文小节均写“参考问题未检出；附带检出 incorrect_actor 与 prohibited” | **已关闭** | P5 |
| 7 | 相似度后端被描述为“字符串相似” | P1 事实错误 | `WinterSimilarity._similarity` 走 `Doc.similarity`（spaCy W007：无静态词向量，基于 tensor） | 更正为“无静态词向量的 tensor 相似度”；不改模型、不降阈值 | `plan.components.similarity_backend` 记录实际类与行为 | **已关闭** | P4、P5 |
| 8 | 协作图扁平化丢弃消息流 | P1 适配限制 | 扁平化只保留 process 子元素；消息流位于 collaboration 下 | 参与者边界以命名泳道保留；消息流未建模，作为已知适配限制记录 | 活动归属（r10）在修复前后可区分，说明归属信息未丢失 | **已关闭（记录为限制）** | P4 |

## 12. 批准后要做的治理动作
1. `docs/MASTER_PIPELINE.md` §9.5 增加任务行（依赖、DoD、边界与本文一致）；
2. `docs/AGENT_RUNBOOK.md` 增加 copy-ready prompt；
3. `docs/PROJECT_AUDIT.md` 当前派工行登记；
4. 每批结束：focused tests + `record_change.py` 事件 + scoped Git commit + push；
5. 本文降级为该任务的附件设计说明。
