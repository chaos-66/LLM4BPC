# SEP-C3 Prompt Design：组件消融的结论、失败原因与模块结构定论（2026-09-20）

- record_id: `SEP_C3_PROMPT_DESIGN_OUTCOME_AND_FAILURE_RECORD_2026-09-20`
- status: `research_record_complete_offline`
- generated_at: `2026-09-20`（本地时区）
- network / LLM calls in this record: **0**
- scope: 只汇总、量化并定性已完成的真实实验结果与既有 Gate 产物；未修改任何
  prompt、Gold、预测、评价器、配置或历史报告。
- 目的：把"三模块消融为什么不好、后面怎么处理、论文怎么写才不含糊"固定成
  可引用记录，避免以口头总结结束。

## 0. 本记录回答的四个问题

1. 三模块（E/S/J）分解实验到底得到了什么，失败在哪一步？
2. 失败是否有可复核的结构性原因，而不是"效果不好"？
3. 三模块这个结构还要不要保留？改成两模块是否可行？
4. 论文里应当怎样写才清楚：哪些能写、哪些不能写、哪些必须标边界？

---

## 1. 实验事实（全部为已执行的真实记录）

### 1.1 时间线与调用

| 轮次 | 内容 | 真实调用 | 报告 |
|---|---|---:|---|
| R0 | 原始 v6 完整 prompt 基线（D-full-0813） | 450（历史批次中 150） | `outputs/reports/d1_prompt_factorial_results_v1.{json,md}` |
| R1 | 模块化 common + E/S/J 单因素四臂 111/011/101/110 | 600 | `outputs/reports/sep_c3_modular_ablation_v1.*`、`sep_c3_modular_ablation_analysis_v1.*` |
| R2 | 补齐 000/001/010/100 四格，合成完整八格 | 600 | `outputs/reports/sep_c3_modular_ablation_v2.json`、`sep_c3_modular_full8_protocol_audit_v1.md` |
| R3 | targeted refinement A/B/C/D（R_A / R_C） | 600 | `outputs/reports/sep_c3_targeted_refinement_v1_*.{json,md}` |
| R4 | condition-preservation RC_KEEP | 450 | `outputs/reports/sep_c3_condition_preservation_v1_final_report.{md,json}` |
| R5 | definition targeted refinement + 全 150 确认（R_DEF） | 84 + 150 | `outputs/reports/sep_c3_definition_*_v1_*.md` |

主指标统一为 `coarse_five_field_mean_f1`（actor/action/condition/constraint/exception
五项粗口径 F1 的算术平均）；micro P/R/F1 与 modality label 指标分开报告，不并入主指标。
每格 n=150，失败计数 0。

### 1.2 八格主结果（R1 + R2）

| E S J | mean F1 | micro F1 | modality acc | 批次绑定 |
|---|---:|---:|---:|---|
| 1 0 0 | **0.7788** | 0.8153 | 0.8133 | current_implementation_binding |
| 1 0 1 | 0.7611 | 0.8144 | 0.8133 | original_execution_binding |
| 0 1 1 | 0.7470 | 0.8032 | 0.8267 | original_execution_binding |
| 1 1 0 | 0.7355 | 0.7970 | 0.8133 | original_execution_binding |
| 0 1 0 | 0.7278 | 0.7991 | 0.8200 | current_implementation_binding |
| 1 1 1 | 0.7262 | 0.7902 | 0.8200 | original_execution_binding |
| 0 0 0 | 0.6367 | 0.6473 | 0.7733 | current_implementation_binding |
| 0 0 1 | 0.6184 | 0.6617 | 0.7800 | current_implementation_binding |

逐字段 F1：

| E S J | actor | action | condition | constraint | exception |
|---|---:|---:|---:|---:|---:|
| 1 1 1 | 0.5158 | 0.9287 | 0.8133 | 0.7416 | 0.6316 |
| 0 1 1 | 0.5132 | 0.9128 | 0.8306 | 0.7723 | 0.7059 |
| 1 0 1 | 0.6757 | 0.9285 | 0.8468 | 0.6876 | 0.6667 |
| 1 1 0 | 0.4770 | 0.9250 | 0.8226 | 0.7770 | 0.6761 |
| 1 0 0 | 0.6194 | 0.9255 | 0.8472 | 0.7240 | 0.7778 |
| 0 1 0 | 0.4903 | 0.9258 | 0.8566 | 0.7412 | 0.6250 |
| 0 0 1 | 0.3055 | 0.8281 | 0.8492 | 0.4726 | 0.6364 |
| 0 0 0 | 0.2786 | 0.8481 | 0.8426 | 0.4145 | 0.8000 |

对照：**原始 v6 完整 prompt 在同一 evaluator 下为 0.7850**（高于全部八格）。

### 1.3 效应分解（描述性；含批次混杂）

E=1 均值 0.7504 / E=0 均值 0.6823；S=1 均值 0.7298 / S=0 均值 0.6794；
J=1 均值 0.7134 / J=0 均值 0.7149。

| 效应 | 估计 | 可解释性 |
|---|---:|---|
| 主效应 E | +0.0681 | 描述性（批次混杂） |
| 主效应 S | +0.0504 | 描述性（批次混杂） |
| 主效应 J | +0.0015 | 描述性（批次混杂） |
| 交互 E×S | −0.0745 | 跨批估计，不得作因果 |
| 交互 E×J | +0.0010 | 描述性 |
| 交互 S×J | +0.0004 | 描述性 |
| 三阶 E×S×J | +0.0002 | 描述性 |

**同批内唯一可用于因果解释的配对**（均为 current_implementation_binding 或
original_execution_binding 内部）：

| 配对 | 同批? | Δmean F1 | 含义 |
|---|---|---:|---|
| 000 → 100 | 是 | **+0.1420** | 仅加 E 的效果 |
| 000 → 010 | 是 | **+0.0910** | 仅加 S 的效果 |
| 010 → 110 | 是 | **+0.0510** | 已有 S 时再加 E |
| **100 → 110** | **是** | **−0.0432** | **已有 E 时再加 S：净负** |
| 101 → 111 | 是 | −0.0349 | 已有 E+J 时再加 S：净负 |
| 000 → 001 | 是 | −0.0184 | 仅加 J：无收益 |

### 1.4 同批配对误差归因（关键证据）

| 配对 | 主要修复 | 主要回归 |
|---|---|---|
| 000 → 100 | constraint +53 Gold 命中；unmatched pred：actor −188、action −43 | — |
| 000 → 010 | constraint +54 Gold 命中；actor unmatched −149 | — |
| 100 → 110 | actor 修复 7 个样本字段 | **actor 回归 38 个样本字段** |
| 101 → 111 | actor 修复 13 | actor 回归 19；unmatched actor 43 → 84 |

即：**聚合均值的微小变化背后，是大幅互相抵消的字段级变化。**
`111` 的 actor 过抽（预测 130 个 actor span，旧 v6 为 82 个）单项即占新旧均值差的约 65%。

### 1.5 后续三条修补线（R3/R4/R5）

| 线 | 候选 | 目标字段结果 | 代价 | 处置 |
|---|---|---|---|---|
| R3 | R_A（actor 最小性） | actor F1 0.6314 → **0.7672**；空-Gold 非空 actor 预测 36 → 19 | 组合后总分仍不优于 v6 | 保留为研究参照 B，未晋升 |
| R3 | R_C（constraint 召回） | constraint R 0.6074 → **0.7778** | P 0.8102 → 0.7553；FP 净增 | 保留为研究参照 D，未晋升 |
| R4 | RC_KEEP（condition 保留） | condition F1 +0.0206（95% CI 含 0） | five-field mean F1 −0.0048；actor F1 −0.048；actor FP +6 | **不保留**，回 BASE |
| R5 | R_DEF（definition 语义） | definition F1 0.4615 → **0.7200**（CI 不含 0）；modality macro-F1 +0.109 | micro F1 −0.0084；action/condition/constraint F1 全为负；非 definition 误判率 0.52% → 4.69% | **DO NOT PROMOTE**，回 A |

**登记结论：六个候选（E、S、J、R_A、R_C、R_DEF）没有任何一个达到"整体优于现有
默认配方"的验收标准；默认 LLM-SE prompt 仍为
`prompts/sun_compat/direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md`。**

---

## 2. 失败原因（四条结构性瓶颈，逐条附证据）

### 瓶颈 1：信息在模块之间冗余——E 与 S 不携带独立信息

- **Gate 证据**（`outputs/reports/sep_c3_modular_prompt_overlap_audit_v1.json`
  的 `overlap_audit.e_s_functional_overlap`）：E 的**全部五个示例**都被判定为与
  S 规则**功能重叠**，且 `literal_contradiction=false`：

  | E | 重叠的 S | 共享功能 |
  |---|---|---|
  | E01 | S03, S10 | actor 表层保留（含未解析代词主语） |
  | E02 | S04, S06, S10 | 被动语态动作映射 + constraint 抽取 |
  | E03 | S02, S07 | prohibition 模态 + exception 抽取 |
  | E04 | S11, S12 | definition/obligation 从句切分 |
  | E05 | S05, S06, S08 | condition/constraint 嵌套与字段划分 |

- **含义**：E 没有提供 S 之外的语义信息，只是把 S 的抽象规则换成具体示范。
  这解释了 `100`（E）与 `010`（S）为什么都相对 `000` 明显改善、而两者叠加为负：
  **同一份指导有两个载体，删掉任何一个都会被另一个兜住**——单因素消融测到的是
  "删 A 之后的残差"，不是"A 的贡献"。
- **辅证**：模块体量差异近 10 倍（示例 2,487 tokens vs 语义规则 758 vs JSON 纪律
  266），但 ΔF1 量级相同（−0.0069 / +0.0040 / +0.0071）。
- **不可过度声明**：这是功能重叠与样本级关联，**不是**逐 token 因果归因；
  未做重复运行，不能排除生成波动。

### 瓶颈 2：J 的职责几乎被公共骨架覆盖

- **Gate 证据**（同文件 `overlap_audit.j_common_relationship`）：J 只有 2 条指令。
  - `J01`（bare JSON、无 Markdown 围栏、无前后文）是**真正新增**的约束；
  - `J02`（返回完整对象而非散文式拒绝）被判定为 **rewording_only**，与 C01/C13 重叠。
- **实测**：`000` 已有 schema 骨架时，去掉 J 的 raw bare-JSON 率为 000:114/150、
  100:146/150、010:149/150，但 canonical adapter 会把带围栏的响应救回来，
  八格 **canonical schema/cross-field 失败均为 0**。
- **含义**：J 改善的是**原始响应形态**，不是抽取质量或 canonical 可靠性。
  该结论必须限定在"共同保留基线结构化输出接口"这一前提下。

### 瓶颈 3：五个字段共用同一次生成与同一套坐标契约，任何局部加压都会外溢

- **证据**：R_C 提 constraint 召回 → actor/精度受损；R_DEF 提 definition →
  action/condition/constraint F1 全下降；RC_KEEP 提 condition → actor F1 −0.048。
  三条独立修补线呈现同一种"提一个、掉一片"的模式。
- **机制解释（INFERENCE，需标注）**：一次生成同时满足五个 span 字段的边界要求；
  对某一字段加压时，相邻字段的边界判定随之偏移，因此聚合均值难以提升。
- **辅证**：`100 → 110` 中 actor 修 7 坏 38；`101 → 111` 中 actor 修 13 坏 19。

### 瓶颈 4：评价口径把边界与粒度差异计为错误，且校验链没有中间态

- **边界敏感性**：LLM-SE 的 constraint 粗口径 F1 = 0.7427，细粒度口径
  F1 = 0.5481；差值来自 span 切分粒度，而非语义错误。
- **Gold 局部不一致（已登记的不可学习噪声）**：
  - cue `to the extent` 在 Gold 中 gold-condition 14 条 / gold-constraint 2 条；
  - `estg_000505 c2` 与 `estg_000509 c2` 被登记为 `POTENTIAL_GOLD_INCONSISTENCY`；
  - apply/applies 家族 7 definition vs 5 非 definition，无稳定 Gold 判别式
    （`outputs/reports/sep_c3_definition_prompt_design_gate.md` 标为
    `NEEDS_GOLD_ADJUDICATION`）。
- **fail-closed 放大**：去掉坐标重锚器后 149/150 记录判为无效，F1 由 0.772 直接
  变为 **0.000**。模块贡献被压成 0/1，**没有"轻微退化"这一档**。
- **含义**：聚合指标的微小差异里混入了口径差异与不可学习噪声，这既解释了为什么
  "再加一段规则"提不动分数，也构成对补丁有效性的**独立稀释源**。

### 2.5 一句话总结失败原因

**不是措辞没写好，而是（a）E 与 S 携带同一份信息、（b）J 的职责已被公共骨架覆盖、
（c）五个字段的边界在同一次生成里互相争夺、（d）评价口径与 Gold 噪声把边界差异
也计成错误。** 四条同时成立时，继续在同一语料上追加或删减文本块，只能得到
字段间的再分配，而不是整体提升。

---

## 3. 模块结构定论：三模块就这样了吗？要不要改两模块？

### 3.1 结论（直接回答）

**不建议把"三模块"改成"两模块"作为论文主线，也不建议保留"三模块分解"这一提法。**

理由不是"两模块一定更差"，而是：

1. **删 J 得到两模块（E+S）在结构上合理，且与实测方向一致**：J 只有 1 条真正新增
   约束、在共享接口下无可测收益。若一定要保留模块化叙述，**J 应降级为所有版本
   共有的固定部分，不再作为实验因子**——这一点在 `sep_c3_modular_ablation_root_cause_v1.md`
   §0.5 已作为候选 B 提出。
2. **但删 J 并不能解决核心问题**：核心问题是 E 与 S **互不独立**（五个示例全部
   与 S 功能重叠），两个因子的主效应无法分离。**把三因子砍成两因子，不会让这两
   个因子变得可分离**，只是少了一个已知无效的因子。
3. **因此"两模块"只应作为一条设计说明，而不是新的实验主张**：论文可以写
   "我们把输出纪律固定为公共接口的一部分，只保留语义规则与示例两个可变因素"，
   但**不得**据此声称"两模块结构已被验证"。

### 3.2 论文中该采用的结构（明确、不含糊）

| 论文位置 | 写法 | 禁止写法 |
|---|---|---|
| 方法章 | 完整描述**当前生效的默认配方 v6**（含 6 个完整 JSON 示例与规则 1–27），说明其职责划分 | 不要把 modular_v1 的 E/S/J 当作"我们的方法"介绍 |
| 实验章主表 | 报告**八格组合结果**，标注批次绑定列；主结论用同批配对 | 不要把跨批排名写成因果主效应 |
| 实验章分析 | 用 §2 四条瓶颈解释"为什么模块叠加不增益" | 不要写"消融失败"或"prompt 无效" |
| 消融设计说明 | 说明共同骨架固定了什么、三个开关各增删什么文本块 | 不要写"J 证明 JSON 约束没必要" |
| 结论/讨论 | 明确"六个候选均未晋升，默认配方保持 v6" | 不要含糊写"取得了一定改进" |

### 3.3 必须逐字避开与推荐替代表述

| 避免 | 使用 |
|---|---|
| 完整 prompt 更差 | 完整配置在当前实验中没有描述性地优于若干更简配置 |
| E 和 S 冲突 | 消融结果显示示例与显式规则之间存在非加性关系 |
| JSON 约束没必要 | 在共同保留的基线结构化输出接口下，额外的输出组织模块未带来一致可测的收益 |
| 单因素消融无效 | 聚合均值的微小变化背后是大幅互相抵消的字段级变化 |
| 两模块结构更好 | 我们把输出纪律固定为公共接口，仅将语义规则与示例作为可变因素 |

---

## 4. 负结果 / 数据不好看的报告模板

论文报告不利数据时，每条至少包含五要素。以下为可直接套用的空表（示例行取自
本记录的实测数据）：

| 候选 | 目标字段结果 | 代价字段结果 | 判定 | 失败原因归类 |
|---|---|---|---|---|
| R_C | constraint R +0.1704 | constraint P −0.0549；FP 净增 | 不晋升 | 瓶颈 3（字段外溢） |
| R_DEF | definition F1 +0.2585（CI 不含 0） | micro F1 −0.0084；action/condition/constraint 全负；误判率 +4.17pp | 不晋升 | 瓶颈 3 + 瓶颈 4 |
| RC_KEEP | condition F1 +0.0206（CI 含 0） | mean F1 −0.0048；actor F1 −0.048 | 不保留 | 瓶颈 3 + 证据不足 |
| J | 无正收益 | 无 | 不晋升 | 瓶颈 2（职责被覆盖） |

**报告纪律：**
1. 每条负结果都要给出**目标字段**与**代价字段**两侧数字，不只报总分。
2. 单次运行必须写明"每格一次生成、无重复"，不得做显著性声明。
3. 跨批对比必须写明批次/时间混杂，只有同批配对才是因果证据。
4. 与结论有关的失败必须保留在正文，长明细放附录，不得删除负结果。
5. 引用 Gold 不一致点时，必须同时说明这是登记在案的标注口径问题，
   不是模型失败。

---

## 5. 尚未完成、且不得含糊带过的缺口

| 缺口 | 现状 | 影响的主张 |
|---|---|---|
| 同批 2³ 全因子 | **未运行**（设计+预算已备，2400 calls，USD cap 67.36，未授权） | 因果级主效应/交互 |
| 每格重复运行 | **未运行**（八格每格仅一次） | 稳定性与显著性 |
| 词法重叠量化 | 已有 Gate 的功能重叠清单，**未做 n-gram 覆盖率矩阵** | 冗余强度的定量表述 |
| 信息守恒精简版 `L` | **未构建** | "合并为单一载体后是否提升" |
| 跨语料验证 | **未运行** | 结论的可推广范围 |

**表述要求**：以上五项在论文中必须显式标为未完成，不得用已有八格结果替代，
也不得因表述需要而省略。

---

## 6. 证据绑定

| 证据 | 路径 | 备注 |
|---|---|---|
| 单因素分析与验收 | `outputs/reports/sep_c3_modular_ablation_analysis_v1.md` | 四臂 + 验收 fail |
| 八格主报告 | `outputs/reports/sep_c3_modular_ablation_v2.json` | n=150/格，failed=0 |
| 协议与批次审计 | `outputs/reports/sep_c3_modular_full8_protocol_audit_v1.md` | 批次绑定声明 |
| 配对误差归因 | `outputs/reports/sep_c3_modular_paired_error_attribution_v1.json` | 同批配对来源 |
| 指令清单与重叠 Gate | `outputs/reports/sep_c3_modular_prompt_overlap_audit_v1.json` | 本记录 §2 瓶颈 1/2 的直接来源 |
| 根因诊断 | `sep_c3_modular_ablation_root_cause_v1.md`（仓库根） | actor 过抽与组合冲突 |
| 八格发现与诊断 | `docs/research/SEP_C3_MODULAR_ABLATION_FINDINGS_AND_DIAGNOSIS_2026-09-17.md` | 论文安全措辞来源 |
| targeted refinement | `outputs/reports/sep_c3_targeted_refinement_v1_phase2_summary.json` | R_A / R_C |
| condition-preservation | `outputs/reports/sep_c3_condition_preservation_v1_final_report.md` | RC_KEEP 未保留 |
| definition refinement | `outputs/reports/sep_c3_definition_full150_confirmation_v1_decision_report.md` | R_DEF DO NOT PROMOTE |
| 默认配方登记 | `configs/models/estg150_d1_active_registry_v1.json` | v6，`superseded_by: null` |
| 模块 README（含否决状态） | `prompts/sun_compat/modular_v1/README.md` | rejected for default use |

## 7. 中文摘要（供论文讨论章直接引用）

> 本文对 LLM-SE 抽取提示词做了组件级受控消融：把提示词拆为语义示例（E）、
> 显式语义规则（S）与输出组织纪律（J）三个可独立开关的模块，在固定 EStG-150
> 输入、冻结 Gold 与同一评价器下执行全部八个组合（每格 150 条）。结果显示完整
> 配置并未优于若干更简配置，且新增语义规则在已有示例时会带来净负收益。成对误差
> 归因表明，聚合均值的微小变化背后是大幅互相抵消的字段级变化：E 与 S 各自单独
> 加入均相对公共骨架有显著改善，但二者叠加呈负向非加性关系；指令清单审计进一步
> 显示 E 的全部示例与 S 规则功能重叠且无字面矛盾，J 的职责则已被公共骨架的
> 结构化输出接口覆盖。据此本文认为，在共享坐标契约与固定评价口径下，提示词模块
> 之间携带的信息高度冗余，单纯的文本增删只会造成字段间的再分配，而难以提升整体
> 抽取质量。本文如实报告了三条后续定向修补（actor 最小性、constraint 召回、
> definition 语义）的字段级收益与代价，均未达到晋升为默认配方的验收标准，默认
> 配方保持不变。
