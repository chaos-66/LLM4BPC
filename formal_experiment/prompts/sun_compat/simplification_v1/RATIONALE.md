# Stage 2 prompt 精简逐项依据与信息损失复核

本说明核对提交 `8cb31f6bd2b0c4773dcac5343e16f7bf4934ebb1` 中的 A/B 候选。
目的不是根据已完成的改动反推“删掉的一定没用”，而是说明实际改了什么、依据
来自哪里、仍保留什么、可能损失什么。**本轮不改候选文本，不新增预测或指标。**

## 1. 结论与准确命名

- A 是 **J 指令表达压缩候选**：删除发送给模型的合同指纹、合并输出纪律和自检，
  但也把显式顶层字段清单改为由固定示例承载。后者降低了显式程度，不能证明无损。
- B 是 **J 表达压缩 + S 重组、提示抽象化和语义修正的联合候选**。B 不只是删重；
  删除触发词举例、调整边界和新增角色/分类限定，均可能改变模型行为。
- 保留六个示例、输入模板、原文证据/坐标/归一化边界及分句/关系规则，是为了
  保留必要知识并减少同时变化的部分，不是因为这些内容已经被证明最优。
- 每项均可说明设计动机；目前没有证据证明任何一项新措辞提高或保持抽取性能。
  原 19 项离线检查覆盖装载、渲染、示例与入口保护，不能证明语义等价或实测收益。

静态判断分为：**表达合并**（原要求改写/集中）、**提示抽象化**（删除具体提示，
只留下功能定义）、**语义修正**（新增或改变模型的判定规则）。混合项分别标注。
“有文本/代码依据”与“有性能因果证据”是两件事；后者本批所有项都未验证。

## 2. 精简的准确范围与字符核对

| 区域 | v6 | A | B | 说明 |
|---|---:|---:|---:|---|
| System 全文字符数 | 6172 | 5676 | 4398 | A 少 496 字符，B 少 1774 字符 |
| 合同指纹 + Output 区块 | 843 | 433 | 433 | 少 410 字符；另外 86 字符来自自检合并 |
| 相对 A 的 S 区域改动 | — | — | 少 1278 字符 | 重组规则 9–19、25–27，不是删除全部 S |
| 六个示例 + Notes | 相同 | 相同 | 相同 | 按实际发送的 Examples 区块核对 |
| User template | 相同 | 相同 | 相同 | 模板占位符、示例引用方式不改 |
| 运行时 schema/校验/默认选择 | 原状态 | 相同 | 相同 | 候选只新增显式 development 入口 |

这些是装载后文本的字符计数，**不是** token 估计、完整请求压缩率、成本减少或
性能增量。A 改 Output 和规则 24；B 继承 A 后改规则 9–19、25–27。v6 的规则
6–8、20–23 保持原文。Markdown 文档头改为候选身份，不是发送给模型的系统指令。

原文与候选：
[v6](../direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md)、
[A](direct_llm_json_light_v1.md)、[B](direct_llm_json_semantic_light_v1.md)。
精确差异：[A diff](../../../outputs/evidence/s2_prompt_simplification_v1/candidate_A_system.diff)、
[B diff](../../../outputs/evidence/s2_prompt_simplification_v1/candidate_B_system.diff)。

## 3. J 逐项对照：A/B 共用

下表的编号对应 v6 的原指令，不根据新版本的段落编号推定一一等价。

| 项 | 原要求与实际变化 | 为什么选择这样改：可核对依据 | 保留要求与风险 |
|---|---|---|---|
| J-H 合同引用 | 移除发送给模型的合同 ID/SHA-256 及单独的 schema 遵守宣告；头注和 schema_source 仍保留。 | `prompt_loader.load_prompt` / `build_manifest_entry` 由程序计算、登记实际 prompt 指纹；模型没有被提供合同正文，仅有一个指纹不能让它检查合同内容。因此选择把证据绑定放在程序和清单中。 | 未删除实际 schema 或程序绑定。仍保留 schema_version/method 值。**不能断言**长指纹会干扰模型，或移除遵守宣告没有影响。 |
| J-1 输出纪律 | “ONLY JSON + No Markdown/explanation/commentary/reasoning/preamble/trailing text” 合并为一个 JSON object、no surrounding text。 | 多个禁止项共同表达外部包装限制，单对象要求和无外围文本足以表达这一目标；样例也全部使用对象结构。 | 继续要求单个 JSON，JSON 自身不允许注释。模型遵循率可能下降；输出禁止解释不等于禁止内部推理，不能把删词写成“释放了思考”。 |
| J-2 顶层字段 | 删除逐字列出的八个顶层字段，改为“keys and types shown in the examples; no extra keys”。 | 六个保留示例包含该清单，提供了同一接口的具体形状。此项选择用示例承载已有结构信息，减少重复呈现。 | **这是显式程度降低，不是纯同义删重。**依赖 E 始终存在；若省略示例或模型模仿不完整，可能缺字段。程序校验只能检测其 backend 可覆盖的部分，不能替代给模型的清楚指令。 |
| J-3 固定元数据 | schema_version、method.name、method.schema_source 从编号条款合并成一行固定对象。 | 固定值与原文/六个示例一致，无需多处展开同一值。 | 值仍是 1.0.0/direct_llm/stage2_prediction.schema.json@1.0.0。没有实现“由程序新补元数据”，也没有改变 adapter。 |
| J-4 输入回显 | 原 sample_id/source_id/source_text 精确复制要求，移到短 Output 段。 | 这是接口身份绑定，选择保留，只改变位置/措辞。 | 精确复制三个输入字段仍必需；不容许截断正文、修正来源或加入外部上下文。 |
| J-5 validation | 固定 validation 对象合并成一行，明确 placeholder 与 program-side authoritative。 | 原条款已说明 runtime validator overwrites/is authoritative；示例与 runner 的 `validate_canonical(payload)` 是直接依据。 | 固定输出值及程序权威均保留；模型自报 true 不是验证证据。现有校验器也明确不评价语义正确性。 |
| J-24 自检 | 原“required keys/no extra keys/fixed enums/exact spans/references/no forbidden inference” 合并为结构、精确 spans、同句 ID 引用和 source-only evidence。 | 输出段与 S 枚举、原文边界、ID 规则已分别表达这些要求，选择在自检中归纳。 | 删除了自检中对 required keys、extra keys、枚举的再次逐项提醒；这些提醒可能仍有实际价值。只能说指令目标可追溯，不能说自检效用不变。 |

J-H/J-5 的代码依据：
[prompt_loader.py](../../../src/bpc_hybrid/prompt_loader.py) 的 `load_prompt`、
`build_manifest_entry`；[run_direct_llm.py](../../../scripts/run_direct_llm.py) 的
`_few_shot_block`、`validate_canonical` 调用和 manifest 构建；
[stage2_canonical.py](../../../src/bpc_hybrid/stage2_canonical.py) 的模块职责说明。
运行时的校验 backend 以环境为准；不把原聚焦检查写成完整 JSON Schema 或语义验证。

## 4. S 逐项对照：仅 B

| 原规则 | 实际变化与类型 | 为什么选择这样改：文本/实例依据 | 保留内容、信息损失与风险 |
|---|---|---|---|
| 9 modality | 改为短标签定义；表达合并。 | 四类枚举、最小触发证据与改变类别的否定词是原规则的核心；六个示例覆盖四类。 | 四类和否定证据保留；位置、列表风格的变化也可能改变遵循率。 |
| 10 actor | 合并最小名词短语、主语代词和被动句规则；删 it/they 两个显式举例；新增 object/actor 角色对比。 | 原文已定义承担/执行规范者，规则 17/18 又重复代词/被动情况；示例 1/2 展示对应处理。选择把角色、代词和语态集中。 | this/these/such+noun、未解析主语代词保留。**新增 object 排除语句不是逐字删重**，也没有隔离验证；其绝对措辞与“subject pronoun”抽象可能对复杂/反身或介词代词角色产生误读，必须单列关注。 |
| 11 action | 短写动词中心+必要宾语/补语/小品词；把排除规则改为 separately expressed 限定，并加入 grammatical scope。 | 原 11 要求必要宾语/补语，原 26 同时要求遇限定短语就结束；插入修饰与后置宾语会使机械截断和完整动作目标产生张力。选择语法范围作为依据。 | 必要动作内容和独立限定字段继续保留。**这是边界规则修正**；可能增大 action span 或包含原本排除的修饰，尚无针对该措辞的错误修复证据。 |
| 12 condition | 保留触发/适用功能、标记和完整命题；表达合并。 | 与原 27 的前提功能及嵌套要求有关，选择把定义集中在一处。 | 原功能仍在；关键词枚举的删除单独见规则 27，不能称全部信息不变。 |
| 13 constraint | 与规则 25 合并成限制作法、量、地点、时间、目的/排他性及法律引用。 | 原 13 给功能，25 给类别，含义部分重叠；集中可避免读者在两个位置拼合定义。 | B 只写 complete limit，**没有再显式写 smallest complete limit**；最小边界提示被弱化，可能导致过长跨度。这是当前候选的真实信息损失。 |
| 14 exception | 保留“否则适用规则的排除情形”，增加功能分类优先级。 | 原 14 的排除功能、示例 3 的 unless 例外，与原 27 的 unless→condition 列举有需要澄清的优先级。 | 未直接保留原词 narrows；“排除情形”能解释部分收窄，但不保证覆盖所有收窄用法。**定义抽象化和分类修正混合**，不能写成同义替换已证实。 |
| 15 absence | “truly has no source span / empty means absent, not uncertain” 压缩为 [] for absent，另段保留不确定 span。 | 原 15/16 连续说明“缺失”和“有证据但不确定”的区别，选择一起呈现。 | 空数组缺失含义保留。删除再次强调 not uncertain 可能增加保守漏抽，离线结构检查无法识别这种语义退步。 |
| 16 uncertain | 四个 reason 值由逐行列表改为逗号分隔说明。 | reason 值没有变化；短列举仍包含原四个精确字符串。 | 值与保留 span 的要求在，但原“Use only”强调弱化、格式示范更少；可能输出别的 reason 或把多个值拼成一串。 |
| 17 unresolved pronoun | 合并原文归一化、actor reason 和不补外部先行词；移除内嵌 JSON 小例子。 | actor 定义和规则 8 已含这些目标，示例 1 有完整 unsupported entry；选择少重复一次对象模板。 | surface-preserving、actor 字段和首个 reason 保留。更依赖示例 1 的结构提示；属于表达合并伴随显式示范减少。 |
| 18 passive | 移到 actor 段；保留无执行者 actors=[]/actor_id=null，删除 explicit by-phrase 的表面形式提示。 | 这是 actor 角色的特殊情况；示例 2 已展示无执行者的处理。 | 有明确执行者仍提取，但 **by-phrase 提示被抽象掉**，示例 2 不能证明带 by-phrase 情况不退步。 |
| 19 definition/fragment | 合并至字段分区段。 | 定义可无 action、无可辩护规范分句可为空和 controlled reason 是原要求；示例 4 演示定义分句。 | 相关空数组与理由要求保留；没有用示例 4 证明所有 fragment 行为等价。 |
| 25 constraint categories | 功能类别合并到 constraint；部分法律短语保留，其余触发词表删除；提示抽象化。 | 原 13/25 有功能重复；选择依赖“法律/时间/数量/目的/排他性”语义定义和固定示例，减少类别说明的重复呈现。 | **触发词表不是纯重复信息。**删除 in accordance with/as defined in；within N/until/after/before/during；at least/at most/no more than/in such a quantity that；for the purpose of；only/solely/exclusively 的显式举例。可能降低上述类别召回；没有逐类新验证。 |
| 26 field partition | 不折叠独立限定字段目标保留，机械“action ends where … begins” 换为语法范围。 | 原 11/26 都说明 action 与限定字段的边界；结合原 11 的必要宾语目标，选择避免只按 marker 截断。 | 字段分开仍必需；grammatical scope/separately expressed 改变了指令，需检查 action 宽度和 condition/constraint/exception 漏抽，不能视为删除重复句。 |
| 27 condition/nesting | 删除 condition 触发词列举；保留嵌套双字段规则；对排除型 unless 明确 exception 优先。 | v6 示例 3 将 unless consent 放 exception，规则 27 却把 unless 直接列入 condition。选择功能定义，避免把一个 marker 自动映射成两个字段。示例 6 展示嵌套 constraint。 | if/when/where/provided that/in the event of/to the extent that/insofar as 的提示被抽象掉；可能漏前提。unless 新优先级是**语义修正**，不代表全部 unless 都是 exception；嵌套条件/限制双字段规则原样保留。 |

特别说明：B 的角色对比、最小 constraint 边界提示弱化、触发词提示减少，都不能
仅凭“文本短了”认为合理有效。以上给出尝试动机，同时明确标出没有效果证据的
地方；它们仍是待验证候选，不是已经通过语义验收的改进。

## 5. 已有结果如何支持研究动机，不能支持什么

| 已有证据 | 支持的设计动机 | 不能据此声称 |
|---|---|---|
| v6：110→111，pooled F1 0.8268→0.8224（加 J） | 值得检查强化输出纪律的增量收益，保留结构目标并尝试更短表达。 | J 必然有害；删除合同哈希或字段清单导致提升；新 A 能达到 0.8268。 |
| v6：000→010，0.7380→0.8107；100→110，0.8354→0.8268（加 S） | S 在缺示例时帮助明显；与示例并存时效果可能不同。因此保留功能定义和 E，尝试重组而非删除整个 S。 | S 无用；重叠已证明导致下降；B 的新优先级有效。单次/跨批结果不是稳定因果主效应。 |
| v6：000→100，0.7380→0.8354（加 E） | 保留现有示例，避免同时压缩 E 与 S/J，减少改动包的变化范围。 | 六个示例均有独立贡献、最优，或能够完全替代显式字段/触发词清单。 |
| 旧 modular 逐项 overlap 报告存在 E/S 功能重叠与 actor/constraint 多抽案例 | 提醒检查重复指导、角色误用与完整限定短语，说明保留真实负结果的重要性。 | 报告中的 modular S 与本次 v6 S 相同；那些错误由 B 删除的某一句造成。旧报告 no_literal_contradiction_found 不能用于否定 v6 的 unless 优先级歧义。 |
| 原 19 个聚焦检查通过，六个样例的 canonical 校验通过 | 说明候选可装载/渲染、保留示例结构/坐标、运行入口保护有效。 | 新模型输出结构必然有效、抽取语义等价、性能提升或全量测试覆盖。 |

数值来源：[v6 factorial](../../../outputs/reports/v6_factorial_ablation_v1.md)。
案例/重叠来源：[modular overlap audit](../../../outputs/reports/sep_c3_modular_prompt_overlap_audit_v1.md)。
旧负结果来源：[modular analysis](../../../outputs/reports/sep_c3_modular_ablation_analysis_v1.md)。
旧报告与本次 v6 是不同 prompt 体系，引用范围在上表明确区分；工作区被改写的
两份 modular 主报告不作为数值依据。原版本见已保存的 baseline_snapshot。

外部研究 Tam et al., EMNLP 2024 在部分推理任务中观察到格式限制下的性能下降，
可支持“格式纪律不保证正收益”的一般研究动机；其任务/模型/约束机制不同，不能
替我们证明 J 某句有害、字段抽取适合放松，或 B 的语义修正有效。
[论文原始来源](https://aclanthology.org/2024.emnlp-industry.91/)。

## 6. 保留与后续判定标准

原文证据、精确坐标、source 身份、枚举/结构目标、空值含义、未解析引用、被动
执行者规则、嵌套双字段、分句、并列与文本顺序证据继续保留；程序 schema、
adapter/canonicalizer、评价口径、Gold 和默认选择没有因本说明而修改。

未来若有另行授权的运行，除固定 pooled 主 F1 和独立 modality 外，还应记录：
格式/缺键/枚举/身份失败；actor 多抽与被动/by-phrase/代词；action 宽度与必要
宾语；condition/exception 分配；完整 constraint 的边界和规则 25 所列各类别。
这只是按既有改动确定诊断对象，不新增样本、阈值、调用预算或实验计划。

若目标是证明“纯长度压缩”的作用，B 的当前联合改动不能回答该问题，A 的字段
清单隐式化也要披露。需要另行版本化、保留所有类别提示/最小边界/角色范围的
等目标表达候选，或单独分离语义修正；本轮不静默改写已保存的 A/B。

判断某项可否采用，应同时看目标结构是否保留、实际信息提示是否减少以及相应
错误是否变化，不能预设每个模块必须使 F1 增加，也不能为了正结果删除负结果。
