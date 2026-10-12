# SIM 卡入网案例：A/B/C 三组开发性检测与参考问题对应

> 本节所有数字、状态、报警和修复判定均绑定同一运行 capsule：`outputs/development/sim_case_c1/run_v1/capsule.json`，由 `scripts/run_sim_case_c1_v1.py --overwrite` 生成。口径为 `development_case_study_not_formal_gold`。本节不新增 LLM/API 调用，不修改原始 BPMN、需求、Gold 或已有原始预测。

## 1. 方法接线与主评价单位

主评价单位固定为 5 条 v2 规则：r8/v2、r9/v2、r10/v2、r11/v2、r13/v2；r12 仅作背景，不计入分母。A 组是项目锁定非 LLM 基线 B0 v10a（`sun_rule_only_b0_v10a`）加冻结 Sun 式三类检测；B 组复用已有真实 LLM Part 2 预测 `OURS-FULL/repeat-01`，经 `project_external_sentence` 投影后使用与 A 相同的三类检测；C 组逐行复用 B 的 Part 2 和三类结果，追加 REPAIR-V2 C 四类扩展。公共 Part 1 记录只解析一次，由 A/B/C 共用；角色绑定仍为 Data Controller=Phone company、Data Subject=Customer。
## 2. P1 修正：抽取失败、适配选择和不适用

A 组 r9、r13 的 B0 原始抽取动作数为 0。旧实现把 missing_action 分母为 0 直接写成 `not_applicable`；本轮在案例评价层把这两项改为 `undetermined`，原因记录为 `empty_rule_action_rule_element_not_extracted`，同时保留底层 `machine_status=not_applicable`、`score=0.0`、`denominator=0`。因此 A 组逐检查计数为 3 violation / 12 undetermined / 0 not_applicable；机器状态计数单独保留 2 个 not_applicable。字段为空本身不再作为规则语义上不适用的证据。

多值字段采用已声明的 `first_valid_span_per_field_v1_with_diagnostics` 政策：投影把所有有效候选保留在 diagnostics 中，但现有检测器只消费单项。有有效显式 `actor_action_map` 时，只把显式配对动作放入 `rule.actions`；没有有效配对时，首个投影动作只保留给动作存在性检查，配对为空。未配对候选记录在 `unconsumed_candidates`，不自动视为独立义务，也不自动构造 actor-action 对。r11 A/B 的显式配对 actor 现按声明角色绑定到 Phone company，同时保留 original=the Data Controller、bound_from=Data Controller 和原始 actor_action_map；1->1 的数量相等不再掩盖该绑定回退。A 组 r10 是 P1 的直接修正对象：原始 B0 有 2 个动作、2 个条件，投影仍保留 2 个候选，但适配只消费 1 个显式配对动作和 1 个首值条件；chain 记录为 `partially_carried_by_declared_policy [raw=2→proj=2→adapted=1→consumed=1]`，不再写成 carried。A→B 的直接 changed_fields 仍归因于两次抽取，但 attribution 追加组内适配损失，不能笼统宣称差异全部来自抽取。B 组 r8 的原始 actor_action_map 含 `actor_id=null`，现记录为 `invalid_in_raw_no_valid_pair`，没有被角色启发式补成一对。
## 3. P2 修正：机器报警、参考问题与有效修复对照

机器报警全部保留；是否对应参考问题单独判断，不以类型相同且 status=violation 为准。r8 的 condition/constraint 报警缺少 30 天时间条件、终止行为和流程级作用域证据，因此记为机器报警存在但参考问题对应未证实；r9 的 missing_action 有抽取动作、模型清单缺失和远低于 gamma 的最优匹配证据，判为有证据对应；r10 的 incorrect_actor 有动作绑定证据，规则动作最优映射到 `Activate SIM card`（具体动作 ID 见 capsule），归属为 Customer，与规则要求的 Phone company 不一致，判为有证据对应；全部匹配候选逐项列出，Send SIM card 归属 Phone company，不被写成 Customer；r11 的 positive alarm 是 missing_action，但流程事实显示 `Ask for consent` 活动存在，参考问题是顺序错误，故不对应；r13 的 actor/prohibited 报警不涉及 Debt>50 门槛语义，条件/约束视角为 undetermined，故不对应。
修复件有效性独立于检测器判断。r8 主修复改为进程级事件子流程 `startEvent(isInterrupting=true, timerEventDefinition P30D)` 到 `endEvent(terminateEventDefinition)`，覆盖计时起点、计时范围、超时触发和终止范围；但冻结 Part 1 将事件子流程解析为 opaque activity，计时器和终止定义没有进入结构化 Process Record，因此该件不计入有效修复分母，只报告 BPMN 语义有效而检测链表示受限。旧 Send SIM card 任务级计时器保留为 `legacy_partial_control`，明确为部分/无效对照。r9、r10、r11 修复语义有效且进入检测链，计入有效分母。r13 的 `Debt <= 50` 标签语义有效：超过 50 被排除，等于 50 不触发本禁止；但 B 侧规则记录没有抽取 condition，条件检测不可执行，因此该件也不计入有效分母，归因为规则侧抽取缺口。最终有效修复对照为 3 件（r9、r10、r11），r8、r13 分别因表示限制和规则元素缺口排除。
## 4. 结果摘要

逐检查计数：A 组 15 项，violation=3、satisfied=0、undetermined=12、not_applicable=0；B 组 15 项，violation=5、satisfied=2、undetermined=8、not_applicable=0；C 组 35 项，violation=10、satisfied=2、undetermined=23、not_applicable=0。机器状态计数保留 A 组 2 个 not_applicable；C 构成为 15 条 B 三类复用行加 20 条四类扩展行，B/C 原三类逐项对象完全一致。

参考问题对应计数：A 组有证据对应 0 条、有报警但对应未证实 3 条、无 positive alarm 2 条；B 组和 C 组各有证据对应 2 条、有报警但对应未证实 3 条。因此本案例不能表述为所有违规都检出；r8、r11、r13 的参考问题没有获得有证据对应的检出，其中 r8 还有表示限制，r13 还有规则侧 condition 抽取缺口，r11 的 out_of_order 端点未在 gamma=0.8 下同时映射。
有效修复对照中的 C_original -> C_repaired 变化：r9 修复后任务 `Verify correctness of customer personal data` 已进入模型并可达，但冻结 three-type 映射相似度只有 0.5884，仍判 violation；r10 修复后 `Activate SIM card` 已归入 Phone company lane，但 Sun Def6 的动作绑定候选集合仍包含活动绑定业务对象 `SIM card`，最小相似度使 incorrect_actor 保持 violation；r11 修复后 consent 到 retrieval 可达且反向不可达，但端点文本在 gamma 阈值下仍不能同时映射到流程动作，out_of_order 保持 undetermined。以上三项可以用于讨论冻结检测链的方法限制；r8 和 r13 不能用于该结论。

## 5. 边界

这是开发性单案例结果，不是正式 Gold、不是作者原始实验复现、不是独立人工准确率，也不合成七类总 F1。流程图使用 sim_original_flattened.bpmn 的只读 BPMNDI 节点、网关、连线和条件标签；缺失活动在图中使用模型中不存在的活动占位符；论文原 Figure 10 的 Violation 标签没有被当作本方法输出。参考判断只在评价阶段读取，原始 BPMN、需求、Gold 和原始预测均未修改。下方附录嵌入同一运行的完整结构化报告，表格、状态和计数与本纸质小节来自同一 capsule。

## 附录：同一运行的结构化结果报告

# SIM 卡入网案例：A/B/C 三组开发性检测结果（同一 capsule）

- run: `sim_case_c1_run_v1`；口径：**development_case_study_not_formal_gold**（非正式 Gold，非作者原始实验复现，非企业验证）。
- 主评价单位：r8/v2, r9/v2, r10/v2, r11/v2, r13/v2（5 条 v2 规则）；背景条目：r12。
- 阈值：tau=0.8, gamma=0.8, theta=0.8, gamma_ext=0.5, label_fallback=0.4。
- 公共 Part 1 记录：324091aa007882ab…；扁平化 XML 29a31cfc0fa520a7…；lanes=['Phone company', 'Another phone company', 'Customer']。
- 角色绑定（打分前声明）：{"Data Controller": "Phone company", "Data Subject": "Customer"}。

## 1. 组件对应

| 组 | Part 2 | Part 3 三类 | Part 3 四类 |
|---|---|---|---|
| A | 项目锁定非 LLM 基线 B0 v10a (`sun_rule_only_b0_v10a`) | 冻结 Sun 式 Def5–7 | 未运行 |
| B | 已有真实 LLM 预测 `OURS-FULL/repeat-01`，经 `project_external_sentence` | 与 A 同一代码和阈值 | 未运行 |
| C | 与 B 同一 Part 2 行和适配记录 | 逐行复用 B | REPAIR-V2 C 实现：`RepairedExtendedScorerV2` + `aggregate_with_comparison_gate` |

## 2. 五条规则的逐项实际输出

> `status` 是修正抽取失败后的评价状态；`machine_status` 保留冻结公式在分母为 0 等情形下的原始机器状态。A 组 r9/r13 的 `empty_rule_action` 不再写成 `not_applicable`。

| 规则 | 组 | missing_action | incorrect_actor | out_of_order | prohibited | condition | constraint | exception |
|---|---|---|---|---|---|---|---|---|
| r8/v2 | A | violation (1.0) | undetermined | undetermined (0.0) | — | — | — | — |
| r8/v2 | B | violation (1.0) | undetermined | undetermined (0.0) | — | — | — | — |
| r8/v2 | C | violation (1.0) | undetermined | undetermined (0.0) | undetermined | violation (1.0) | violation (0.674966) | undetermined |
| r9/v2 | A | undetermined (0.0); raw_machine=not_applicable; empty_rule_action_rule_element_not_extracted | undetermined | undetermined (0.0) | — | — | — | — |
| r9/v2 | B | violation (1.0) | undetermined | undetermined (0.0) | — | — | — | — |
| r9/v2 | C | violation (1.0) | undetermined | undetermined (0.0) | undetermined | undetermined | undetermined | undetermined |
| r10/v2 | A | violation (1.0) | undetermined | undetermined (0.0) | — | — | — | — |
| r10/v2 | B | satisfied (0.0) | violation (1.0) | undetermined (0.0) | — | — | — | — |
| r10/v2 | C | satisfied (0.0) | violation (1.0) | undetermined (0.0) | undetermined | violation (0.92683) | violation (0.623876) | undetermined |
| r11/v2 | A | violation (1.0) | undetermined | undetermined (0.0) | — | — | — | — |
| r11/v2 | B | violation (1.0) | undetermined | undetermined (0.0) | — | — | — | — |
| r11/v2 | C | violation (1.0) | undetermined | undetermined (0.0) | undetermined | undetermined | undetermined | undetermined |
| r13/v2 | A | undetermined (0.0); raw_machine=not_applicable; empty_rule_action_rule_element_not_extracted | undetermined | undetermined (0.0) | — | — | — | — |
| r13/v2 | B | satisfied (0.0) | violation (1.0) | undetermined (0.0) | — | — | — | — |
| r13/v2 | C | satisfied (0.0) | violation (1.0) | undetermined (0.0) | violation (0.628643) | undetermined | undetermined | undetermined |

## 3. 机器报警与参考问题对应（评价栏与检测器输出分栏）

> 只有同时具备动作绑定、流程事实、时间/终止语义等可核验证据的报警才计为对应检出；类型相同且 `status=violation` 本身不算证据。

| 规则 | 组 | 机器报警（原始输出） | 对应判断 | 有证据对应的报警 | 评价证据链 |
|---|---|---|---|---|---|
| r8/v2 | A | missing_action=violation/1.0  | machine_alarm_but_reference_correspondence_unverified | — | missing_action: machine alarm retained, but no model-side alarm value supplies an actual 30-day bound or terminate label; process-scope fields are absent. Reference correspondence remains unverified. r8 requires time, termination, and process-scope evidence from explicit sources; keyword co-occurrence in the alarm object is not used. |
| r8/v2 | B | missing_action=violation/1.0  | machine_alarm_but_reference_correspondence_unverified | — | missing_action: machine alarm retained, but no model-side alarm value supplies an actual 30-day bound or terminate label; process-scope fields are absent. Reference correspondence remains unverified. r8 requires time, termination, and process-scope evidence from explicit sources; keyword co-occurrence in the alarm object is not used. |
| r8/v2 | C | missing_action=violation/1.0 ；required_condition_not_enforced=violation/1.0 best=None max_sim=0.0 ；constraint_violated=violation/0.674966 best='sid-2673F7BE-190B-4A29-B042-F26FE1273508 sid-E965697A-165F-4586-B050-908E907A73E2 sid-dcc02dd6-4d40-4a5c-9c7a-e7f2289d157a sid-23CD283E-EBC8-4855-94D0-525EC56A6361 sid-dcc02dd6-4d40-4a5c-9c7a-e7f2289d157a' max_sim=0.325034  | machine_alarm_but_reference_correspondence_unverified | — | missing_action: machine alarm retained, but no model-side alarm value supplies an actual 30-day bound or terminate label; process-scope fields are absent. Reference correspondence remains unverified. required_condition_not_enforced: machine alarm retained, but no model-side alarm value supplies an actual 30-day bound or terminate label; process-scope fields are absent. Reference correspondence remains unverified. constraint_violated: machine alarm retained, but no model-side alarm value supplies an actual 30-day bound or terminate label; process-scope fields are absent. Reference correspondence remains unverified. r8 requires time, termination, and process-scope evidence from explicit sources; keyword co-occurrence in the alarm object is not used. |
| r9/v2 | A | 无 positive alarm | no_positive_machine_alarm | — | r9 correspondence needs an extracted action, a missing_action alarm with a concrete best candidate/similarity, and an activity inventory lacking verify/correctness semantics; Sign contract is only an anchor. |
| r9/v2 | B | missing_action=violation/1.0  | found_with_reference_evidence | missing_action | Extracted verification action is checked by missing_action; best process candidate is Ask portability third company at similarity 0.4219, and the original activity inventory has no verify/correctness activity. Sign contract (sid-6B3F7867-7939-43B6-8F6E-8B8A12ECCB7C) is only the positional anchor, not the missing action. |
| r9/v2 | C | missing_action=violation/1.0  | found_with_reference_evidence | missing_action | Extracted verification action is checked by missing_action; best process candidate is Ask portability third company at similarity 0.4219, and the original activity inventory has no verify/correctness activity. Sign contract (sid-6B3F7867-7939-43B6-8F6E-8B8A12ECCB7C) is only the positional anchor, not the missing action. |
| r10/v2 | A | missing_action=violation/1.0  | machine_alarm_but_reference_correspondence_unverified | — | r10 correspondence needs the rule action to bind to Activate SIM card, with concrete owner Customer and a required actor that is not an owner. A union of all matched candidates is not used. |
| r10/v2 | B | incorrect_actor=violation/1.0  | found_with_reference_evidence | incorrect_actor | Rule action maps to Activate SIM card (sid-D80682C2-0CD4-4B60-93BA-E9C747E28950); its concrete owner evidence is ['Customer']; required actor is the phone company. This is the fixed r10 actor-mismatch evidence. Other matched candidates are listed separately and are not attributed to Customer. |
| r10/v2 | C | incorrect_actor=violation/1.0 ；required_condition_not_enforced=violation/0.92683 best='Requested' max_sim=0.07317 ；constraint_violated=violation/0.623876 best='Receive SIM card' max_sim=0.376124  | found_with_reference_evidence | incorrect_actor | Rule action maps to Activate SIM card (sid-D80682C2-0CD4-4B60-93BA-E9C747E28950); its concrete owner evidence is ['Customer']; required actor is the phone company. This is the fixed r10 actor-mismatch evidence. Other matched candidates are listed separately and are not attributed to Customer. |
| r11/v2 | A | missing_action=violation/1.0  | machine_alarm_but_reference_correspondence_unverified | — | r11 correspondence requires a positive out_of_order alarm whose mapped endpoints include consent and request personal data. The present missing_action alarm is retained as a machine alarm but cannot substitute for the order issue; consent activity present=True, retrieval activity present=True. |
| r11/v2 | B | missing_action=violation/1.0  | machine_alarm_but_reference_correspondence_unverified | — | r11 correspondence requires a positive out_of_order alarm whose mapped endpoints include consent and request personal data. The present missing_action alarm is retained as a machine alarm but cannot substitute for the order issue; consent activity present=True, retrieval activity present=True. |
| r11/v2 | C | missing_action=violation/1.0  | machine_alarm_but_reference_correspondence_unverified | — | r11 correspondence requires a positive out_of_order alarm whose mapped endpoints include consent and request personal data. The present missing_action alarm is retained as a machine alarm but cannot substitute for the order issue; consent activity present=True, retrieval activity present=True. |
| r13/v2 | A | 无 positive alarm | no_positive_machine_alarm | — | No condition/constraint alarm contains the locatable 50 EUR rule threshold, the model Debt < 100 threshold, and an alarm-level mapping between them. Single numbers, isolated number co-occurrence, and similarity-score digits are not accepted. Actor threshold text is recorded as a field-attribution gap, not copied into condition/constraint. Other alarms are []. |
| r13/v2 | B | incorrect_actor=violation/1.0  | machine_alarm_but_reference_correspondence_unverified | — | No condition/constraint alarm contains the locatable 50 EUR rule threshold, the model Debt < 100 threshold, and an alarm-level mapping between them. Single numbers, isolated number co-occurrence, and similarity-score digits are not accepted. Actor threshold text is recorded as a field-attribution gap, not copied into condition/constraint. Other alarms are ['incorrect_actor']. |
| r13/v2 | C | incorrect_actor=violation/1.0 ；prohibited_action_present=violation/0.628643 best='Ask portability third company' max_sim=0.628643  | machine_alarm_but_reference_correspondence_unverified | — | No condition/constraint alarm contains the locatable 50 EUR rule threshold, the model Debt < 100 threshold, and an alarm-level mapping between them. Single numbers, isolated number co-occurrence, and similarity-score digits are not accepted. Actor threshold text is recorded as a field-attribution gap, not copied into condition/constraint. Other alarms are ['incorrect_actor', 'prohibited_action_present']. |

## 4. 信息传递与部分丢失（原始抽取→投影→规则记录→检测器消费）

判定：`full_carry`=各层数量一致；`partially_carried_by_declared_policy`=出现多值截断；`lost_in_adaptation`=抽取/投影有值但规则记录丢失；`not_extracted`=原始即无；`derived_by_declared_policy`=顺序关系由事先声明的 temporal policy 派生。

| 规则 | 组 | actions | actors | conditions | constraints | exceptions | order_relations | actor_action_pairs |
|---|---|---|---|---|---|---|---|---|
| r8/v2 | A | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | full_carry [raw=1→proj=1→adapted=1→consumed=0; not_used_by_group_pipeline] | full_carry [raw=1→proj=1→adapted=1→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | not_extracted |
| r8/v2 | B | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | full_carry [raw=1→proj=1→adapted=1→consumed=0; not_used_by_group_pipeline] | full_carry [raw=1→proj=1→adapted=1→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | invalid_in_raw_no_valid_pair |
| r8/v2 | C | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | invalid_in_raw_no_valid_pair |
| r9/v2 | A | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | full_carry [raw=1→proj=1→adapted=1→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | not_extracted |
| r9/v2 | B | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | derived_by_declared_policy [raw=0→proj=0→adapted=1→consumed=1; fully_consumed] | full_carry |
| r9/v2 | C | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | derived_by_declared_policy [raw=0→proj=0→adapted=1→consumed=1; fully_consumed] | full_carry |
| r10/v2 | A | partially_carried_by_declared_policy [raw=2→proj=2→adapted=1→consumed=1; partially_consumed_relative_to_projected] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | partially_carried_by_declared_policy [raw=2→proj=2→adapted=1→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | full_carry |
| r10/v2 | B | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=0; not_used_by_group_pipeline] | full_carry [raw=1→proj=1→adapted=1→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | full_carry |
| r10/v2 | C | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | full_carry |
| r11/v2 | A | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | full_carry [raw=1→proj=1→adapted=1→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | full_carry |
| r11/v2 | B | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | derived_by_declared_policy [raw=0→proj=0→adapted=1→consumed=1; fully_consumed] | full_carry |
| r11/v2 | C | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | derived_by_declared_policy [raw=0→proj=0→adapted=1→consumed=1; fully_consumed] | full_carry |
| r13/v2 | A | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | full_carry [raw=1→proj=1→adapted=1→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | not_extracted |
| r13/v2 | B | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; not_used_by_group_pipeline] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | full_carry |
| r13/v2 | C | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | full_carry [raw=1→proj=1→adapted=1→consumed=1; fully_consumed] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | not_extracted [raw=0→proj=0→adapted=0→consumed=0; no_value_to_consume] | full_carry |

### 4.1 值级变化与角色绑定（防止 1->1 计数掩盖回退）

| 规则 | 组 | 字段/配对 | original | final | source | reason |
|---|---|---|---|---|---|---|
| r9/v2 | B | order_relations | None | ('receiving the customer’s personal information', 'verify the correctness of their personal information') | — | binding_or_declared_derivation |
| r9/v2 | C | order_relations | None | ('receiving the customer’s personal information', 'verify the correctness of their personal information') | — | binding_or_declared_derivation |
| r10/v2 | A | actions | use the SIM card normally | None | — | not_selected_or_not_consumed |
| r10/v2 | A | conditions | that the customer can use the SIM card normally | None | — | not_selected_or_not_consumed |
| r11/v2 | A | actors | the Data Controller | Phone company | Data Controller | declared_role_binding |
| r11/v2 | A | actor_action_pairs | the Data Controller | Phone company | Data Controller | declared_role_binding |
| r11/v2 | B | actors | the Data Controller | Phone company | Data Controller | declared_role_binding |
| r11/v2 | B | order_relations | None | ('ask the Data Subject for consent', 'retrieving any kind of personal data from the Data Subject') | — | binding_or_declared_derivation |
| r11/v2 | B | actor_action_pairs | the Data Controller | Phone company | Data Controller | declared_role_binding |
| r11/v2 | C | actors | the Data Controller | Phone company | Data Controller | declared_role_binding |
| r11/v2 | C | order_relations | None | ('ask the Data Subject for consent', 'retrieving any kind of personal data from the Data Subject') | — | binding_or_declared_derivation |
| r11/v2 | C | actor_action_pairs | the Data Controller | Phone company | Data Controller | declared_role_binding |

### 4.2 A→B 归因

| 规则 | A→B changed_fields | 直接差异归因 | 组内适配损失 |
|---|---|---|---|
| r8/v2 | actions, constraint | extraction | 无 |
| r9/v2 | actions, actor_action_pairs, actors, condition, constraint, modality, order_relations | extraction | 无 |
| r10/v2 | actions, actor_action_pairs, constraint | extraction | A/actions=partially_carried_by_declared_policy (2→2→1); A/conditions=partially_carried_by_declared_policy (2→2→1) |
| r11/v2 | actor_action_pairs, condition, constraint, order_relations | extraction | 无 |
| r13/v2 | actions, actor_action_pairs, actors, constraint, modality | extraction | 无 |

## 5. 修复对照：有效、部分/无效与可评价性

> `effective_repair_control=true` 要求：修复语义独立成立、修复信息确实进入检测链、对应规则元素可用、修复后检查可执行。r8 的过程级事件子流程在冻结 Part 1 中为 opaque activity，计时/终止作用域不能进入结构化检测链；旧任务级修复保留为部分/无效对照。

| 修复 | 规则 | 视角 | 修复语义有效 | 进入检测链 | 有效分母 | 排除原因 | C_original | C_repaired | 问题移除 |
|---|---|---|---|---|---|---|---|---|---|
| r8_timeout_termination | r8 | constraint_violated | True | False | False | repair_semantics_not_carried_by_stage1 | violation (0.674966) | violation (0.674966) | False |
| r9_add_verification | r9 | missing_action | True | True | True | — | violation (1.0) | violation (1.0) | False |
| r10_activation_owner | r10 | incorrect_actor | True | True | True | — | violation (1.0) | violation (1.0) | False |
| r11_consent_before_retrieval | r11 | out_of_order | True | True | True | — | undetermined (0.0) | undetermined (0.0) | False |
| r13_threshold_50 | r13 | required_condition_not_enforced | True | True | False | empty_rule_condition | undetermined (None) | undetermined (None) | False |

### 5.1 r8 旧任务级对照（保留但不进入有效分母）

- 旧件 `r8_timeout_termination_task_scoped_legacy`：`scope_matches_rule_semantics=False`；有效分母=False；C_original violation -> C_repaired violation。

## 6. 计数（逐检测项，不是七类总 F1，也不混用规则数）

| 组 | checks | violation | satisfied | undetermined | not_applicable | machine_status 计数 |
|---|---|---|---|---|---|---|
| A | 15 | 3 | 0 | 12 | 0 | {"violation": 3, "undetermined": 10, "not_applicable": 2} |
| B | 15 | 5 | 2 | 8 | 0 | {"violation": 5, "undetermined": 8, "satisfied": 2} |
| C | 35 | 10 | 2 | 23 | 0 | {"violation": 10, "undetermined": 23, "satisfied": 2} |

### 6.1 参考问题对应计数

| 组 | 参考问题数 | 有证据对应检出 | 有报警但对应未证实 | 无 positive alarm |
|---|---|---|---|---|
| A | 5 | 0 | 3 | 2 |
| B | 5 | 2 | 3 | 0 |
| C | 5 | 2 | 3 | 0 |

### 6.2 有效修复对照计数

- 主修复件：5。
- 有效修复对照分母：3。
- 排除：{"r8_timeout_termination": "repair_semantics_not_carried_by_stage1", "r13_threshold_50": "empty_rule_condition"}。

## 7. 边界

- 这是开发性单案例结果，不是正式 Gold、不是独立人工准确率、不是作者原始实验复现。
- 单案例只给逐条与逐检查计数，不合成七类总 F1。
- B 组复用已有 repeat-01 预测；重复运行只作稳定性证据，不作为新增独立样本。
- 原始 BPMN、需求、Gold、预测均未修改；参考判断只在评价阶段读取。
