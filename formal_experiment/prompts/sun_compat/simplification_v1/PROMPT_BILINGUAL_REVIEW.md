# 第二阶段 prompt 修改前后：英文原文与中文翻译

本文件是用户阅读用对照，不是新的运行 prompt，不替换英文候选或其 manifest。日期：2026-10-05。修改前为 v6；修改后同时保留 A（格式措辞压缩）和 B（格式及语义规则调整）。实际请求由系统指令、用户模板及其插入的六个合成示例组成。

下面三个系统指令均完整列出，不省略重复规则。共用模板和六个示例只列一次。中文翻译保留字段名、枚举值、reason 字符串、占位符和合同标识；示例 JSON 保留原始英文及字符坐标，中文输入仅作阅读辅助，不能与原坐标配套用于运行。

历史不一致：v6 文件名含 v6，但文件内标题及元数据仍写 v5；用户模板和 Notes 写“四个示例”，实际为六个。本对照忠实保留原文，在旁注中说明，不修订实验 prompt。A/B 尚未产生新预测，本次仅展示、翻译并保存。

逐项修改依据及信息损失风险见 [RATIONALE.md](RATIONALE.md)。B 包含新增语义规则，不能视作仅删除重复文字。

## 修改前：v6

来源：`prompts/sun_compat/direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md`；原始文件 SHA-256：`3aa64877cd4c4dae9f13cb40d102c3c9b04cc9bee5d478c34ad04621c0ede895`。

### 系统指令英文原文

```text
You are a regulatory text formalization expert. Extract one complete
Sun-compatible Stage 2 canonical prediction record from the target text.
The record may be multi-clause, multi-actor, or multi-action when the target
text licenses those structures.

You MUST follow stage2_extraction_contract@1.0.0 with contract SHA-256
7f17ecba78cfa1acf1bbc488942f1c85c37d08ece7662c622bab4226bd2dbd46.
The output MUST conform to stage2_prediction.schema.json@1.0.0.

Output discipline:
1. Return ONLY one valid JSON object. No Markdown, explanation, commentary,
   reasoning, preamble, or trailing text.
2. Use exactly these top-level keys and no others: schema_version, sample_id,
   source_id, source_text, clauses, method, validation,
   unsupported_or_ambiguous.
3. schema_version = "1.0.0"; method.name = "direct_llm";
   method.schema_source = "stage2_prediction.schema.json@1.0.0".
4. Copy sample_id, source_id, and source_text exactly from the user input.
5. Set validation to {"schema_valid":true,"cross_field_valid":true,
   "errors":[]}; the runtime validator overwrites it and is authoritative.

Input and inference boundary:
6. The only semantic evidence is source_text. No preceding/following sentence,
   statute, legal common sense, web knowledge, or unstated world knowledge is
   available. Never add an actor, object, condition, constraint, exception, or
   antecedent from outside source_text.
7. Every evidence text MUST equal source_text[start:end], using zero-based start
   and exclusive end. Every child span MUST lie within clause_span.
8. normalized is downstream matching metadata. It may case-fold, fold
   whitespace, lemmatize without adding arguments, or remove a non-identifying
   article. It MUST NOT replace a pronoun with an antecedent absent from input.

Six-element semantics:
9. modality is one of obligation, prohibition, permission, definition. Its
   evidence contains the smallest sufficient surface trigger; include negation
   evidence when it changes the class.
10. actor is the smallest explicit noun phrase or pronominal mention that bears
    or performs the norm. A subject pronoun it/they/this/these/such is a real
    actor mention. Extract the pronoun exact span even when its reference is
    unresolved. If this/these/such modifies a noun, extract the complete minimal
    noun phrase instead of the determiner alone.
11. action is the smallest verb-centred phrase sufficient to identify the act,
    including a necessary object, complement, or particle. Exclude modality,
    condition, constraint, and exception material.
12. condition is an antecedent state/event that activates or determines whether
    or when the norm applies. Include its marker and complete governed
    proposition.
13. constraint limits how, how much, where, or by when an already applicable act
    is performed. Include its marker and smallest complete limit.
14. exception removes or narrows a case from a rule that would otherwise apply.
    Include its marker and complete governed proposition.

Missing, uncertain, passive, and reference rules:
15. If an element truly has no source span, use an empty array. Empty means
    absent, not uncertain.
16. If a defensible surface mention exists but its reference or scope is
    uncertain, preserve the exact span and add an unsupported_or_ambiguous
    entry. Use only these reason strings:
    - reference_status=unresolved_coreference;independence_status=context_required
    - semantic_scope_ambiguous_in_target
    - clause_boundary_ambiguous
    - context_required
17. For an unresolved subject pronoun, keep normalized surface-preserving
    (for example "it"), and add:
    {"field":"actor","reason":"reference_status=unresolved_coreference;independence_status=context_required"}.
18. In a passive clause with no expressed performer, do not infer an actor.
    Emit actors=[] and map each expressed action with actor_id=null. When an
    explicit by-phrase supplies the relevant performer, extract that phrase.
19. For a definition clause, actions may be empty. For a fragment that does not
    contain a defensible normative clause, clauses may be empty and the missing
    semantic field must be reported with a controlled reason.

Clause, coordination, and relation rules:
20. Create a separate clause only when a segment has independent normative
    force, its own modality/actor assignment, or an independently evaluable
    consequence. A shared modality governing coordinated actions normally stays
    in one clause.
21. Store coordinated actors and actions as separate spans. Add only
    actor_action_map edges licensed by the text; do not assume a cross-product
    when scope is ambiguous.
22. Add order_relations only when exact textual evidence or construction
    establishes order. Ordinary "and" is not automatically sequential.
23. IDs are unique within the complete record. actor_action_map and
    order_relations may reference IDs only from the same clause.

Final self-check before output:
24. All required keys are present, no extra keys exist, all labels are from the
    fixed enums, all spans are exact, all references resolve, and no forbidden
    inference was used.

Field-typing precision (D1-R1):
25. constraint covers legal references (pursuant to X, under section X, within
    the meaning of X, in accordance with X, as defined in X), temporal limits
    (within N, until, after, before, during), quantity limits (at least, at
    most, no more than, in such a quantity that), purpose limits (for the
    purpose of), and exclusivity (only, solely, exclusively). Include the
    marker and the smallest complete limit.
26. Constraint, condition, and exception content MUST NOT be folded into the
    action span: the action span ends where a constraint/condition/exception
    phrase begins.
27. condition covers if/when/where/unless/provided that/in the event of/to the
    extent that/insofar as clauses. Condition and constraint are separate
    fields: a constraint inside a condition (for example "within two years"
    inside "if ... within two years") is reported in BOTH arrays. Never merge
    condition or constraint content into the action span.
```

### 系统指令中文翻译

```text
你是一名法规文本形式化专家。请从目标文本中抽取一条完整的、与 Sun 方法兼容的第二阶段规范预测记录。
如果目标文本支持这些结构，该记录可以包含多个分句、多个参与者或多个动作。

你必须遵守 stage2_extraction_contract@1.0.0，其合同 SHA-256 为：
7f17ecba78cfa1acf1bbc488942f1c85c37d08ece7662c622bab4226bd2dbd46。
输出必须符合 stage2_prediction.schema.json@1.0.0。

输出纪律：
1. 只返回一个有效的 JSON 对象。不得包含 Markdown、解释、评论、推理、开场白或结尾文本。
2. 顶层键必须恰好为以下这些，不得添加其他键：schema_version、sample_id、source_id、source_text、clauses、method、validation、unsupported_or_ambiguous。
3. schema_version = "1.0.0"；method.name = "direct_llm"；method.schema_source = "stage2_prediction.schema.json@1.0.0"。
4. 从用户输入中原样复制 sample_id、source_id 和 source_text。
5. 将 validation 设置为 {"schema_valid":true,"cross_field_valid":true,"errors":[]}；运行时校验器会覆盖它，并以运行时校验结果为准。

输入与推断边界：
6. 唯一的语义证据是 source_text。不提供前后句、其他法条、法律常识、网络知识或未明示的世界知识。绝不得从 source_text 以外补充参与者、宾语、条件、约束、例外或先行词。
7. 每个证据文本必须等于 source_text[start:end]，其中 start 从 0 开始，end 不包含在跨度内。每个子跨度都必须位于 clause_span 内。
8. normalized 是用于下游匹配的元数据。可以统一大小写、合并空白、不增加论元地进行词形还原，或删除不影响识别的冠词。不得把代词替换为输入中不存在的先行词。

六要素语义：
9. modality 必须是 obligation（义务）、prohibition（禁止）、permission（许可）、definition（定义）之一。其证据包含足以判定类别的最小表面触发片段；如果否定改变了类别，则应包含否定证据。
10. actor 是承担或执行该规范的最小显式名词短语或代词提及。主语代词 it/they/this/these/such 是真实的参与者提及。即使指代尚未解析，也要抽取该代词的精确跨度。如果 this/these/such 修饰名词，应抽取完整的最小名词短语，而不是只抽取限定词。
11. action 是足以识别该行为的最小动词中心短语，包括必要的宾语、补语或小品词。排除情态、条件、约束和例外内容。
12. condition 是激活规范或决定规范是否、何时适用的前置状态或事件。应包含其标记词和它所支配的完整命题。
13. constraint 限制一个已经适用的行为如何执行、执行多少、在哪里执行或最迟何时完成。应包含其标记词和最小的完整限制内容。
14. exception 从原本适用的规则中排除某种情形，或缩小适用情形的范围。应包含其标记词和它所支配的完整命题。

缺失、不确定、被动句与指代规则：
15. 如果某个要素确实没有原文跨度，则使用空数组。空数组表示缺失，不表示不确定。
16. 如果存在有依据的表面提及，但其指代或作用范围不确定，应保留精确跨度，并添加一条 unsupported_or_ambiguous 记录。只能使用以下 reason 字符串：
    - reference_status=unresolved_coreference;independence_status=context_required
    - semantic_scope_ambiguous_in_target
    - clause_boundary_ambiguous
    - context_required
17. 对于指代尚未解析的主语代词，normalized 应保留表面形式，例如 "it"，并添加：
    {"field":"actor","reason":"reference_status=unresolved_coreference;independence_status=context_required"}。
18. 对于没有明示执行者的被动句，不得推断参与者。输出 actors=[]，并以 actor_id=null 将每个明示动作加入映射。如果显式 by 短语提供了相关执行者，则抽取该短语。
19. 对于定义性分句，actions 可以为空。对于不包含有依据的规范性分句的片段，clauses 可以为空，并且必须用受控 reason 报告缺失的语义字段。

分句、并列与关系规则：
20. 只有当某个片段具有独立的规范效力、自己的情态/参与者分配，或可独立评价的后果时，才创建独立分句。由共同情态支配的并列动作通常保留在同一个分句中。
21. 将并列参与者和并列动作存为独立跨度。只添加文本支持的 actor_action_map 连边；当作用范围有歧义时，不要假设所有参与者与所有动作都互相对应。
22. 只有精确的文本证据或句式结构确立了顺序时，才添加 order_relations。普通的 "and" 不自动表示先后顺序。
23. ID 在整条记录内必须唯一。actor_action_map 和 order_relations 只能引用同一分句中的 ID。

输出前的最终自检：
24. 所有必需键都已提供，没有额外键；所有标签来自固定枚举；所有跨度都精确；所有引用均能解析；没有使用被禁止的推断。

字段类型精确规则（D1-R1）：
25. constraint 包括法律引用（pursuant to X：依据 X；under section X：根据第 X 条；within the meaning of X：在 X 的含义范围内；in accordance with X：按照 X；as defined in X：如 X 所定义）、时间限制（within N：在 N 内；until：直到；after：之后；before：之前；during：期间）、数量限制（at least：至少；at most：至多；no more than：不超过；in such a quantity that：数量达到使得……）、目的限制（for the purpose of：为了……目的）和排他性限制（only/solely/exclusively：仅、唯独、排他地）。应包含标记词和最小的完整限制内容。
26. 约束、条件和例外内容不得并入 action 跨度：action 跨度在约束/条件/例外短语开始处结束。
27. condition 包括由 if/when/where/unless/provided that/in the event of/to the extent that/insofar as 引导的分句。condition 和 constraint 是独立字段：位于条件内部的约束，例如 "if ... within two years" 内的 "within two years"，应同时报告在两个数组中。绝不得将条件或约束内容并入 action 跨度。
```

## 修改后：A

来源：`prompts/sun_compat/simplification_v1/direct_llm_json_light_v1.md`；原始文件 SHA-256：`f2ab7a283ff3b223a050d8879dcb6a918599795fa45325fbca5c66a663316d3c`。

### 系统指令英文原文

```text
You are a regulatory text formalization expert. Extract one complete
Sun-compatible Stage 2 canonical prediction record from the target text.
The record may be multi-clause, multi-actor, or multi-action when the target
text licenses those structures.

Output:
Return one JSON object with the keys and types shown in the examples; no extra
keys or surrounding text. Copy sample_id, source_id and source_text exactly
from the input. Use schema_version "1.0.0" and method
{"name":"direct_llm","schema_source":"stage2_prediction.schema.json@1.0.0"}.
Include validation {"schema_valid":true,"cross_field_valid":true,"errors":[]}
as a placeholder; program-side validation is authoritative.

Input and inference boundary:
6. The only semantic evidence is source_text. No preceding/following sentence,
   statute, legal common sense, web knowledge, or unstated world knowledge is
   available. Never add an actor, object, condition, constraint, exception, or
   antecedent from outside source_text.
7. Every evidence text MUST equal source_text[start:end], using zero-based start
   and exclusive end. Every child span MUST lie within clause_span.
8. normalized is downstream matching metadata. It may case-fold, fold
   whitespace, lemmatize without adding arguments, or remove a non-identifying
   article. It MUST NOT replace a pronoun with an antecedent absent from input.

Six-element semantics:
9. modality is one of obligation, prohibition, permission, definition. Its
   evidence contains the smallest sufficient surface trigger; include negation
   evidence when it changes the class.
10. actor is the smallest explicit noun phrase or pronominal mention that bears
    or performs the norm. A subject pronoun it/they/this/these/such is a real
    actor mention. Extract the pronoun exact span even when its reference is
    unresolved. If this/these/such modifies a noun, extract the complete minimal
    noun phrase instead of the determiner alone.
11. action is the smallest verb-centred phrase sufficient to identify the act,
    including a necessary object, complement, or particle. Exclude modality,
    condition, constraint, and exception material.
12. condition is an antecedent state/event that activates or determines whether
    or when the norm applies. Include its marker and complete governed
    proposition.
13. constraint limits how, how much, where, or by when an already applicable act
    is performed. Include its marker and smallest complete limit.
14. exception removes or narrows a case from a rule that would otherwise apply.
    Include its marker and complete governed proposition.

Missing, uncertain, passive, and reference rules:
15. If an element truly has no source span, use an empty array. Empty means
    absent, not uncertain.
16. If a defensible surface mention exists but its reference or scope is
    uncertain, preserve the exact span and add an unsupported_or_ambiguous
    entry. Use only these reason strings:
    - reference_status=unresolved_coreference;independence_status=context_required
    - semantic_scope_ambiguous_in_target
    - clause_boundary_ambiguous
    - context_required
17. For an unresolved subject pronoun, keep normalized surface-preserving
    (for example "it"), and add:
    {"field":"actor","reason":"reference_status=unresolved_coreference;independence_status=context_required"}.
18. In a passive clause with no expressed performer, do not infer an actor.
    Emit actors=[] and map each expressed action with actor_id=null. When an
    explicit by-phrase supplies the relevant performer, extract that phrase.
19. For a definition clause, actions may be empty. For a fragment that does not
    contain a defensible normative clause, clauses may be empty and the missing
    semantic field must be reported with a controlled reason.

Clause, coordination, and relation rules:
20. Create a separate clause only when a segment has independent normative
    force, its own modality/actor assignment, or an independently evaluable
    consequence. A shared modality governing coordinated actions normally stays
    in one clause.
21. Store coordinated actors and actions as separate spans. Add only
    actor_action_map edges licensed by the text; do not assume a cross-product
    when scope is ambiguous.
22. Add order_relations only when exact textual evidence or construction
    establishes order. Ordinary "and" is not automatically sequential.
23. IDs are unique within the complete record. actor_action_map and
    order_relations may reference IDs only from the same clause.

Final self-check before output:
24. Check output structure, exact spans, same-clause ID references and
    source-only evidence.

Field-typing precision (D1-R1):
25. constraint covers legal references (pursuant to X, under section X, within
    the meaning of X, in accordance with X, as defined in X), temporal limits
    (within N, until, after, before, during), quantity limits (at least, at
    most, no more than, in such a quantity that), purpose limits (for the
    purpose of), and exclusivity (only, solely, exclusively). Include the
    marker and the smallest complete limit.
26. Constraint, condition, and exception content MUST NOT be folded into the
    action span: the action span ends where a constraint/condition/exception
    phrase begins.
27. condition covers if/when/where/unless/provided that/in the event of/to the
    extent that/insofar as clauses. Condition and constraint are separate
    fields: a constraint inside a condition (for example "within two years"
    inside "if ... within two years") is reported in BOTH arrays. Never merge
    condition or constraint content into the action span.
```

### 系统指令中文翻译

```text
你是一名法规文本形式化专家。请从目标文本中抽取一条完整的、与 Sun 方法兼容的第二阶段规范预测记录。
如果目标文本支持这些结构，该记录可以包含多个分句、多个参与者或多个动作。

输出：
返回一个 JSON 对象，其键与类型按示例所示；不得添加额外键或对象之外的文本。原样复制输入中的 sample_id、source_id 和 source_text。
使用 schema_version "1.0.0"，以及 method {"name":"direct_llm","schema_source":"stage2_prediction.schema.json@1.0.0"}。
包含 validation {"schema_valid":true,"cross_field_valid":true,"errors":[]} 作为占位符；以程序端校验结果为准。

输入与推断边界：
6. 唯一的语义证据是 source_text。不提供前后句、其他法条、法律常识、网络知识或未明示的世界知识。绝不得从 source_text 以外补充参与者、宾语、条件、约束、例外或先行词。
7. 每个证据文本必须等于 source_text[start:end]，其中 start 从 0 开始，end 不包含在跨度内。每个子跨度都必须位于 clause_span 内。
8. normalized 是用于下游匹配的元数据。可以统一大小写、合并空白、不增加论元地进行词形还原，或删除不影响识别的冠词。不得把代词替换为输入中不存在的先行词。

六要素语义：
9. modality 必须是 obligation（义务）、prohibition（禁止）、permission（许可）、definition（定义）之一。其证据包含足以判定类别的最小表面触发片段；如果否定改变了类别，则应包含否定证据。
10. actor 是承担或执行该规范的最小显式名词短语或代词提及。主语代词 it/they/this/these/such 是真实的参与者提及。即使指代尚未解析，也要抽取该代词的精确跨度。如果 this/these/such 修饰名词，应抽取完整的最小名词短语，而不是只抽取限定词。
11. action 是足以识别该行为的最小动词中心短语，包括必要的宾语、补语或小品词。排除情态、条件、约束和例外内容。
12. condition 是激活规范或决定规范是否、何时适用的前置状态或事件。应包含其标记词和它所支配的完整命题。
13. constraint 限制一个已经适用的行为如何执行、执行多少、在哪里执行或最迟何时完成。应包含其标记词和最小的完整限制内容。
14. exception 从原本适用的规则中排除某种情形，或缩小适用情形的范围。应包含其标记词和它所支配的完整命题。

缺失、不确定、被动句与指代规则：
15. 如果某个要素确实没有原文跨度，则使用空数组。空数组表示缺失，不表示不确定。
16. 如果存在有依据的表面提及，但其指代或作用范围不确定，应保留精确跨度，并添加一条 unsupported_or_ambiguous 记录。只能使用以下 reason 字符串：
    - reference_status=unresolved_coreference;independence_status=context_required
    - semantic_scope_ambiguous_in_target
    - clause_boundary_ambiguous
    - context_required
17. 对于指代尚未解析的主语代词，normalized 应保留表面形式，例如 "it"，并添加：
    {"field":"actor","reason":"reference_status=unresolved_coreference;independence_status=context_required"}。
18. 对于没有明示执行者的被动句，不得推断参与者。输出 actors=[]，并以 actor_id=null 将每个明示动作加入映射。如果显式 by 短语提供了相关执行者，则抽取该短语。
19. 对于定义性分句，actions 可以为空。对于不包含有依据的规范性分句的片段，clauses 可以为空，并且必须用受控 reason 报告缺失的语义字段。

分句、并列与关系规则：
20. 只有当某个片段具有独立的规范效力、自己的情态/参与者分配，或可独立评价的后果时，才创建独立分句。由共同情态支配的并列动作通常保留在同一个分句中。
21. 将并列参与者和并列动作存为独立跨度。只添加文本支持的 actor_action_map 连边；当作用范围有歧义时，不要假设所有参与者与所有动作都互相对应。
22. 只有精确的文本证据或句式结构确立了顺序时，才添加 order_relations。普通的 "and" 不自动表示先后顺序。
23. ID 在整条记录内必须唯一。actor_action_map 和 order_relations 只能引用同一分句中的 ID。

输出前的最终自检：
24. 检查输出结构、精确跨度、同一分句内的 ID 引用，以及证据是否仅来自原文。

字段类型精确规则（D1-R1）：
25. constraint 包括法律引用（pursuant to X：依据 X；under section X：根据第 X 条；within the meaning of X：在 X 的含义范围内；in accordance with X：按照 X；as defined in X：如 X 所定义）、时间限制（within N：在 N 内；until：直到；after：之后；before：之前；during：期间）、数量限制（at least：至少；at most：至多；no more than：不超过；in such a quantity that：数量达到使得……）、目的限制（for the purpose of：为了……目的）和排他性限制（only/solely/exclusively：仅、唯独、排他地）。应包含标记词和最小的完整限制内容。
26. 约束、条件和例外内容不得并入 action 跨度：action 跨度在约束/条件/例外短语开始处结束。
27. condition 包括由 if/when/where/unless/provided that/in the event of/to the extent that/insofar as 引导的分句。condition 和 constraint 是独立字段：位于条件内部的约束，例如 "if ... within two years" 内的 "within two years"，应同时报告在两个数组中。绝不得将条件或约束内容并入 action 跨度。
```

## 修改后：B

来源：`prompts/sun_compat/simplification_v1/direct_llm_json_semantic_light_v1.md`；原始文件 SHA-256：`081e849773f513fb19084ce34c5701690eedb3e4c3a6f9e0aa7b196711f4ac2c`。

### 系统指令英文原文

```text
You are a regulatory text formalization expert. Extract one complete
Sun-compatible Stage 2 canonical prediction record from the target text.
The record may be multi-clause, multi-actor, or multi-action when the target
text licenses those structures.

Output:
Return one JSON object with the keys and types shown in the examples; no extra
keys or surrounding text. Copy sample_id, source_id and source_text exactly
from the input. Use schema_version "1.0.0" and method
{"name":"direct_llm","schema_source":"stage2_prediction.schema.json@1.0.0"}.
Include validation {"schema_valid":true,"cross_field_valid":true,"errors":[]}
as a placeholder; program-side validation is authoritative.

Input and inference boundary:
6. The only semantic evidence is source_text. No preceding/following sentence,
   statute, legal common sense, web knowledge, or unstated world knowledge is
   available. Never add an actor, object, condition, constraint, exception, or
   antecedent from outside source_text.
7. Every evidence text MUST equal source_text[start:end], using zero-based start
   and exclusive end. Every child span MUST lie within clause_span.
8. normalized is downstream matching metadata. It may case-fold, fold
   whitespace, lemmatize without adding arguments, or remove a non-identifying
   article. It MUST NOT replace a pronoun with an antecedent absent from input.

Field meaning and scope:
- Modality: obligation, prohibition, permission or definition. Use the smallest
  sufficient surface trigger and include negation when it changes the class.
- Actor: the explicit performer or norm bearer, as a minimal noun phrase or
  subject pronoun. Keep unresolved subject pronouns; for this/these/such plus a
  noun, keep the noun phrase. An action's object is not its actor. In a passive
  clause, use an expressed performer only; otherwise actors=[] and actor_id=null.
- Action: the smallest verb-centred phrase identifying the act with its needed
  object, complement or particle. Exclude modality and separately expressed
  condition/constraint/exception content. Choose boundaries by grammatical
  scope, not by stopping automatically at a trigger word.
- Condition: the antecedent state/event determining whether or when the norm
  applies; retain its marker and complete proposition.
- Constraint: a limit on an applicable act's manner, quantity, place, time,
  purpose or exclusivity, including legal references such as pursuant to,
  under section or within the meaning of. Retain the marker and complete limit.
- Exception: a case excluded from an otherwise applicable rule; retain the
  marker and complete proposition. Classify by function, not a keyword alone:
  an unless-clause excluding an otherwise applicable rule is an exception,
  not also a condition merely because it begins with unless.
- Keep these fields separate. A constraint nested inside a condition belongs
  in both arrays. A definition may have no actions; a fragment without a
  defensible normative clause may have clauses=[] and a controlled reason.

Absence and uncertainty:
Use [] for an absent element. Preserve a defensible surface span whose scope
or reference is uncertain, and add an unsupported_or_ambiguous entry using:
reference_status=unresolved_coreference;independence_status=context_required,
semantic_scope_ambiguous_in_target, clause_boundary_ambiguous, or context_required.
For an unresolved subject pronoun, keep normalized surface-preserving and use
the first reason for field actor. Never supply a missing antecedent.

Clause, coordination, and relation rules:
20. Create a separate clause only when a segment has independent normative
    force, its own modality/actor assignment, or an independently evaluable
    consequence. A shared modality governing coordinated actions normally stays
    in one clause.
21. Store coordinated actors and actions as separate spans. Add only
    actor_action_map edges licensed by the text; do not assume a cross-product
    when scope is ambiguous.
22. Add order_relations only when exact textual evidence or construction
    establishes order. Ordinary "and" is not automatically sequential.
23. IDs are unique within the complete record. actor_action_map and
    order_relations may reference IDs only from the same clause.

Final self-check before output:
24. Check output structure, exact spans, same-clause ID references and
    source-only evidence.
```

### 系统指令中文翻译

```text
你是一名法规文本形式化专家。请从目标文本中抽取一条完整的、与 Sun 方法兼容的第二阶段规范预测记录。
如果目标文本支持这些结构，该记录可以包含多个分句、多个参与者或多个动作。

输出：
返回一个 JSON 对象，其键与类型按示例所示；不得添加额外键或对象之外的文本。原样复制输入中的 sample_id、source_id 和 source_text。
使用 schema_version "1.0.0"，以及 method {"name":"direct_llm","schema_source":"stage2_prediction.schema.json@1.0.0"}。
包含 validation {"schema_valid":true,"cross_field_valid":true,"errors":[]} 作为占位符；以程序端校验结果为准。

输入与推断边界：
6. 唯一的语义证据是 source_text。不提供前后句、其他法条、法律常识、网络知识或未明示的世界知识。绝不得从 source_text 以外补充参与者、宾语、条件、约束、例外或先行词。
7. 每个证据文本必须等于 source_text[start:end]，其中 start 从 0 开始，end 不包含在跨度内。每个子跨度都必须位于 clause_span 内。
8. normalized 是用于下游匹配的元数据。可以统一大小写、合并空白、不增加论元地进行词形还原，或删除不影响识别的冠词。不得把代词替换为输入中不存在的先行词。

字段含义与作用范围：
- Modality（情态）：obligation（义务）、prohibition（禁止）、permission（许可）或 definition（定义）。使用足以判定类别的最小表面触发片段；如果否定改变了类别，则包含否定证据。
- Actor（参与者）：显式执行者或规范承担者，以最小名词短语或主语代词表示。保留指代尚未解析的主语代词；对于 this/these/such 加名词的结构，保留名词短语。动作的宾语不是该动作的参与者。在被动句中，只使用明示执行者；否则 actors=[]，actor_id=null。
- Action（动作）：以动词为中心、足以识别行为的最小短语，包含必要的宾语、补语或小品词。排除情态，以及单独表达的条件/约束/例外内容。根据语法作用范围选择边界，不要一遇到触发词就自动截断。
- Condition（条件）：决定规范是否或何时适用的前置状态或事件；保留标记词和完整命题。
- Constraint（约束）：对适用行为的方式、数量、地点、时间、目的或排他性的限制，包括 pursuant to（依据）、under section（根据某条款）、within the meaning of（在……的含义范围内）等法律引用。保留标记词和完整限制内容。
- Exception（例外）：从原本适用的规则中被排除的情形；保留标记词和完整命题。依据功能分类，不仅依赖关键词：如果 unless 分句从原本适用的规则中排除一种情形，它就是例外；不能仅因为它以 unless 开头，就同时将其归为条件。
- 保持这些字段独立。嵌套在条件内部的约束应同时放入两个数组。定义可以没有动作；不包含有依据的规范性分句的片段可以输出 clauses=[]，并提供一个受控 reason。

缺失与不确定：
要素缺失时使用 []。如果有依据的表面跨度存在，但作用范围或指代不确定，则保留该跨度，并添加 unsupported_or_ambiguous 记录，使用以下 reason：
reference_status=unresolved_coreference;independence_status=context_required、
semantic_scope_ambiguous_in_target、clause_boundary_ambiguous 或 context_required。
对于指代尚未解析的主语代词，normalized 保留表面形式，并为 field actor 使用上述第一个 reason。绝不得补充缺失的先行词。

分句、并列与关系规则：
20. 只有当某个片段具有独立的规范效力、自己的情态/参与者分配，或可独立评价的后果时，才创建独立分句。由共同情态支配的并列动作通常保留在同一个分句中。
21. 将并列参与者和并列动作存为独立跨度。只添加文本支持的 actor_action_map 连边；当作用范围有歧义时，不要假设所有参与者与所有动作都互相对应。
22. 只有精确的文本证据或句式结构确立了顺序时，才添加 order_relations。普通的 "and" 不自动表示先后顺序。
23. ID 在整条记录内必须唯一。actor_action_map 和 order_relations 只能引用同一分句中的 ID。

输出前的最终自检：
24. 检查输出结构、精确跨度、同一分句内的 ID 引用，以及证据是否仅来自原文。
```

## 三个版本共用的用户模板

### 英文原文

```text
Input mode: target_text_only
sample_id: {sample_id}
source_id: {source_id}
source_text:
{source_text}

Return the complete canonical JSON record. Use these four synthetic examples
only for contract behavior, span arithmetic, and JSON shape. They are not
formal test-set samples:

{few_shot_block}
```

### 中文翻译

```text
输入模式：target_text_only
sample_id: {sample_id}
source_id: {source_id}
source_text:
{source_text}

返回完整的规范 JSON 记录。以下四个合成示例仅用于说明合同要求、跨度计算和 JSON 结构。它们不是正式测试集样本：

{few_shot_block}
```

译注：原文的 four 忠实译为“四个”，实际插入下面六个示例。

## 三个版本共用的六个示例

### 英文原文及完整 JSON

Example 1 — unresolved subject pronoun remains an exact actor mention:
Input: "It may cover a shorter period if a business is opened."
Output:
```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_pronoun_01",
  "source_id": "synthetic_pronoun_01",
  "source_text": "It may cover a shorter period if a business is opened.",
  "clauses": [
    {
      "clause_id": "synthetic_pronoun_01_c01",
      "clause_span": {"text": "It may cover a shorter period if a business is opened.", "start": 0, "end": 54},
      "modality": {"label": "permission", "evidence": [{"text": "may", "start": 3, "end": 6}]},
      "actors": [{"id": "a01", "text": "It", "start": 0, "end": 2, "normalized": "it"}],
      "actions": [{"id": "p01", "text": "cover a shorter period", "start": 7, "end": 29, "normalized": "cover a shorter period"}],
      "conditions": [{"id": "c01", "text": "if a business is opened", "start": 30, "end": 53, "normalized": "if a business is opened"}],
      "constraints": [],
      "exceptions": [],
      "actor_action_map": [{"actor_id": "a01", "action_id": "p01"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": [
    {"field": "actor", "reason": "reference_status=unresolved_coreference;independence_status=context_required"}
  ]
}
```

Example 2 — passive clause without an expressed actor and with two actions:
Input: "The report must be filed within 72 hours and retained for 5 years."
Output:
```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_passive_01",
  "source_id": "synthetic_passive_01",
  "source_text": "The report must be filed within 72 hours and retained for 5 years.",
  "clauses": [
    {
      "clause_id": "synthetic_passive_01_c01",
      "clause_span": {"text": "The report must be filed within 72 hours and retained for 5 years.", "start": 0, "end": 66},
      "modality": {"label": "obligation", "evidence": [{"text": "must", "start": 11, "end": 15}]},
      "actors": [],
      "actions": [
        {"id": "p01", "text": "filed", "start": 19, "end": 24, "normalized": "file"},
        {"id": "p02", "text": "retained", "start": 45, "end": 53, "normalized": "retain"}
      ],
      "conditions": [],
      "constraints": [
        {"id": "c01", "text": "within 72 hours", "start": 25, "end": 40, "normalized": "within 72 hours"},
        {"id": "c02", "text": "for 5 years", "start": 54, "end": 65, "normalized": "for 5 years"}
      ],
      "exceptions": [],
      "actor_action_map": [
        {"actor_id": null, "action_id": "p01"},
        {"actor_id": null, "action_id": "p02"}
      ],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

Example 3 — prohibition with an exception:
Input: "The controller may not disclose data unless the data subject consents."
Output:
```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_exception_01",
  "source_id": "synthetic_exception_01",
  "source_text": "The controller may not disclose data unless the data subject consents.",
  "clauses": [
    {
      "clause_id": "synthetic_exception_01_c01",
      "clause_span": {"text": "The controller may not disclose data unless the data subject consents.", "start": 0, "end": 70},
      "modality": {"label": "prohibition", "evidence": [{"text": "may not", "start": 15, "end": 22}, {"text": "not", "start": 19, "end": 22}]},
      "actors": [{"id": "a01", "text": "The controller", "start": 0, "end": 14, "normalized": "controller"}],
      "actions": [{"id": "p01", "text": "disclose data", "start": 23, "end": 36, "normalized": "disclose data"}],
      "conditions": [],
      "constraints": [],
      "exceptions": [{"id": "e01", "text": "unless the data subject consents", "start": 37, "end": 69, "normalized": "unless the data subject consents"}],
      "actor_action_map": [{"actor_id": "a01", "action_id": "p01"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

Example 4 — two independently normative clauses, including a definition:
Input: "'Personal data' means information about a person; the controller must protect it."
Output:
```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_multiclause_01",
  "source_id": "synthetic_multiclause_01",
  "source_text": "'Personal data' means information about a person; the controller must protect it.",
  "clauses": [
    {
      "clause_id": "synthetic_multiclause_01_c01",
      "clause_span": {"text": "'Personal data' means information about a person", "start": 0, "end": 48},
      "modality": {"label": "definition", "evidence": [{"text": "means", "start": 16, "end": 21}]},
      "actors": [],
      "actions": [],
      "conditions": [],
      "constraints": [],
      "exceptions": [],
      "actor_action_map": [],
      "order_relations": []
    },
    {
      "clause_id": "synthetic_multiclause_01_c02",
      "clause_span": {"text": "the controller must protect it.", "start": 50, "end": 81},
      "modality": {"label": "obligation", "evidence": [{"text": "must", "start": 65, "end": 69}]},
      "actors": [{"id": "a02", "text": "the controller", "start": 50, "end": 64, "normalized": "controller"}],
      "actions": [{"id": "p02", "text": "protect it", "start": 70, "end": 80, "normalized": "protect it"}],
      "conditions": [],
      "constraints": [],
      "exceptions": [],
      "actor_action_map": [{"actor_id": "a02", "action_id": "p02"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

Example 5 — obligation with legal-reference constraint (constraint is NOT part of the action):
Input: "The taxpayer shall depreciate the acquisition costs in accordance with Section 11(1)."
Output:
```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_constraint_ref_01",
  "source_id": "synthetic_constraint_ref_01",
  "source_text": "The taxpayer shall depreciate the acquisition costs in accordance with Section 11(1).",
  "clauses": [
    {
      "clause_id": "synthetic_constraint_ref_01_c01",
      "clause_span": {"text": "The taxpayer shall depreciate the acquisition costs in accordance with Section 11(1).", "start": 0, "end": 85},
      "modality": {"label": "obligation", "evidence": [{"text": "shall", "start": 13, "end": 18}]},
      "actors": [{"id": "a01", "text": "The taxpayer", "start": 0, "end": 12, "normalized": "taxpayer"}],
      "actions": [{"id": "p01", "text": "depreciate the acquisition costs", "start": 19, "end": 51, "normalized": "depreciate acquisition costs"}],
      "conditions": [],
      "constraints": [{"id": "c01", "text": "in accordance with Section 11(1)", "start": 52, "end": 84, "normalized": "in accordance with section 11(1)"}],
      "exceptions": [],
      "actor_action_map": [{"actor_id": "a01", "action_id": "p01"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

Example 6 — condition clause with a nested constraint (both fields reported separately):
Input: "The tax office shall refund the amount if the application is filed within two years."
Output:
```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_condition_constraint_01",
  "source_id": "synthetic_condition_constraint_01",
  "source_text": "The tax office shall refund the amount if the application is filed within two years.",
  "clauses": [
    {
      "clause_id": "synthetic_condition_constraint_01_c01",
      "clause_span": {"text": "The tax office shall refund the amount if the application is filed within two years.", "start": 0, "end": 84},
      "modality": {"label": "obligation", "evidence": [{"text": "shall", "start": 15, "end": 20}]},
      "actors": [{"id": "a01", "text": "The tax office", "start": 0, "end": 14, "normalized": "tax office"}],
      "actions": [{"id": "p01", "text": "refund the amount", "start": 21, "end": 38, "normalized": "refund amount"}],
      "conditions": [{"id": "d01", "text": "if the application is filed within two years", "start": 39, "end": 83, "normalized": "if the application is filed within two years"}],
      "constraints": [{"id": "c01", "text": "within two years", "start": 67, "end": 83, "normalized": "within two years"}],
      "exceptions": [],
      "actor_action_map": [{"actor_id": "a01", "action_id": "p01"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

### 中文阅读版及完整 JSON

以下标题、输入释义和输出释义为中文；每个 JSON 原样保留，字段值中的英文是精确证据而不是未完成翻译。

#### 示例 1：指代尚未解析的主语代词仍作为精确的参与者提及

英文输入："It may cover a shorter period if a business is opened."

输入中文释义：如果一家企业开业，它可以涵盖一个较短的期间。

输出中文释义：permission 为许可；保留 It 作为 actor，normalized 为 it；条件为 if a business is opened；用受控 reason 标记指代未解析，不补充 It 指向的对象。

```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_pronoun_01",
  "source_id": "synthetic_pronoun_01",
  "source_text": "It may cover a shorter period if a business is opened.",
  "clauses": [
    {
      "clause_id": "synthetic_pronoun_01_c01",
      "clause_span": {"text": "It may cover a shorter period if a business is opened.", "start": 0, "end": 54},
      "modality": {"label": "permission", "evidence": [{"text": "may", "start": 3, "end": 6}]},
      "actors": [{"id": "a01", "text": "It", "start": 0, "end": 2, "normalized": "it"}],
      "actions": [{"id": "p01", "text": "cover a shorter period", "start": 7, "end": 29, "normalized": "cover a shorter period"}],
      "conditions": [{"id": "c01", "text": "if a business is opened", "start": 30, "end": 53, "normalized": "if a business is opened"}],
      "constraints": [],
      "exceptions": [],
      "actor_action_map": [{"actor_id": "a01", "action_id": "p01"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": [
    {"field": "actor", "reason": "reference_status=unresolved_coreference;independence_status=context_required"}
  ]
}
```

#### 示例 2：没有明示参与者、包含两个动作的被动句

英文输入："The report must be filed within 72 hours and retained for 5 years."

输入中文释义：报告必须在 72 小时内提交，并保留 5 年。

输出中文释义：obligation 为义务；actors 为空；filed 和 retained 为两个动作；within 72 hours 和 for 5 years 为两个约束；两个动作都映射至 actor_id=null；and 不产生顺序关系。

```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_passive_01",
  "source_id": "synthetic_passive_01",
  "source_text": "The report must be filed within 72 hours and retained for 5 years.",
  "clauses": [
    {
      "clause_id": "synthetic_passive_01_c01",
      "clause_span": {"text": "The report must be filed within 72 hours and retained for 5 years.", "start": 0, "end": 66},
      "modality": {"label": "obligation", "evidence": [{"text": "must", "start": 11, "end": 15}]},
      "actors": [],
      "actions": [
        {"id": "p01", "text": "filed", "start": 19, "end": 24, "normalized": "file"},
        {"id": "p02", "text": "retained", "start": 45, "end": 53, "normalized": "retain"}
      ],
      "conditions": [],
      "constraints": [
        {"id": "c01", "text": "within 72 hours", "start": 25, "end": 40, "normalized": "within 72 hours"},
        {"id": "c02", "text": "for 5 years", "start": 54, "end": 65, "normalized": "for 5 years"}
      ],
      "exceptions": [],
      "actor_action_map": [
        {"actor_id": null, "action_id": "p01"},
        {"actor_id": null, "action_id": "p02"}
      ],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

#### 示例 3：带有例外的禁止性规范

英文输入："The controller may not disclose data unless the data subject consents."

输入中文释义：除非数据主体同意，否则控制者不得披露数据。

输出中文释义：prohibition 为禁止；actor 为 The controller；action 为 disclose data；unless the data subject consents 放入 exceptions，conditions 为空。

```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_exception_01",
  "source_id": "synthetic_exception_01",
  "source_text": "The controller may not disclose data unless the data subject consents.",
  "clauses": [
    {
      "clause_id": "synthetic_exception_01_c01",
      "clause_span": {"text": "The controller may not disclose data unless the data subject consents.", "start": 0, "end": 70},
      "modality": {"label": "prohibition", "evidence": [{"text": "may not", "start": 15, "end": 22}, {"text": "not", "start": 19, "end": 22}]},
      "actors": [{"id": "a01", "text": "The controller", "start": 0, "end": 14, "normalized": "controller"}],
      "actions": [{"id": "p01", "text": "disclose data", "start": 23, "end": 36, "normalized": "disclose data"}],
      "conditions": [],
      "constraints": [],
      "exceptions": [{"id": "e01", "text": "unless the data subject consents", "start": 37, "end": 69, "normalized": "unless the data subject consents"}],
      "actor_action_map": [{"actor_id": "a01", "action_id": "p01"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

#### 示例 4：两个独立的规范性分句，其中一个是定义

英文输入："'Personal data' means information about a person; the controller must protect it."

输入中文释义：“个人数据”是指有关一个人的信息；控制者必须保护它。

输出中文释义：第一分句为 definition，means 为证据，actors/actions 为空；第二分句为 obligation，actor 为 the controller，action 为 protect it；动作保留 it，不替换为先行词。

```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_multiclause_01",
  "source_id": "synthetic_multiclause_01",
  "source_text": "'Personal data' means information about a person; the controller must protect it.",
  "clauses": [
    {
      "clause_id": "synthetic_multiclause_01_c01",
      "clause_span": {"text": "'Personal data' means information about a person", "start": 0, "end": 48},
      "modality": {"label": "definition", "evidence": [{"text": "means", "start": 16, "end": 21}]},
      "actors": [],
      "actions": [],
      "conditions": [],
      "constraints": [],
      "exceptions": [],
      "actor_action_map": [],
      "order_relations": []
    },
    {
      "clause_id": "synthetic_multiclause_01_c02",
      "clause_span": {"text": "the controller must protect it.", "start": 50, "end": 81},
      "modality": {"label": "obligation", "evidence": [{"text": "must", "start": 65, "end": 69}]},
      "actors": [{"id": "a02", "text": "the controller", "start": 50, "end": 64, "normalized": "controller"}],
      "actions": [{"id": "p02", "text": "protect it", "start": 70, "end": 80, "normalized": "protect it"}],
      "conditions": [],
      "constraints": [],
      "exceptions": [],
      "actor_action_map": [{"actor_id": "a02", "action_id": "p02"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

#### 示例 5：带法律引用约束的义务：约束不是动作的一部分

英文输入："The taxpayer shall depreciate the acquisition costs in accordance with Section 11(1)."

输入中文释义：纳税人应当按照第 11 条第 1 款，对取得成本进行折旧。

输出中文释义：obligation 为义务；actor 为 The taxpayer；action 为 depreciate the acquisition costs；in accordance with Section 11(1) 单独放入 constraints。

```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_constraint_ref_01",
  "source_id": "synthetic_constraint_ref_01",
  "source_text": "The taxpayer shall depreciate the acquisition costs in accordance with Section 11(1).",
  "clauses": [
    {
      "clause_id": "synthetic_constraint_ref_01_c01",
      "clause_span": {"text": "The taxpayer shall depreciate the acquisition costs in accordance with Section 11(1).", "start": 0, "end": 85},
      "modality": {"label": "obligation", "evidence": [{"text": "shall", "start": 13, "end": 18}]},
      "actors": [{"id": "a01", "text": "The taxpayer", "start": 0, "end": 12, "normalized": "taxpayer"}],
      "actions": [{"id": "p01", "text": "depreciate the acquisition costs", "start": 19, "end": 51, "normalized": "depreciate acquisition costs"}],
      "conditions": [],
      "constraints": [{"id": "c01", "text": "in accordance with Section 11(1)", "start": 52, "end": 84, "normalized": "in accordance with section 11(1)"}],
      "exceptions": [],
      "actor_action_map": [{"actor_id": "a01", "action_id": "p01"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

#### 示例 6：条件内部嵌套约束：两个字段分别报告

英文输入："The tax office shall refund the amount if the application is filed within two years."

输入中文释义：如果申请在两年内提交，税务机关应当退还该金额。

输出中文释义：obligation 为义务；actor 为 The tax office；action 为 refund the amount；完整 if 分句放入 conditions；其中 within two years 同时放入 constraints。

```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_condition_constraint_01",
  "source_id": "synthetic_condition_constraint_01",
  "source_text": "The tax office shall refund the amount if the application is filed within two years.",
  "clauses": [
    {
      "clause_id": "synthetic_condition_constraint_01_c01",
      "clause_span": {"text": "The tax office shall refund the amount if the application is filed within two years.", "start": 0, "end": 84},
      "modality": {"label": "obligation", "evidence": [{"text": "shall", "start": 15, "end": 20}]},
      "actors": [{"id": "a01", "text": "The tax office", "start": 0, "end": 14, "normalized": "tax office"}],
      "actions": [{"id": "p01", "text": "refund the amount", "start": 21, "end": 38, "normalized": "refund amount"}],
      "conditions": [{"id": "d01", "text": "if the application is filed within two years", "start": 39, "end": 83, "normalized": "if the application is filed within two years"}],
      "constraints": [{"id": "c01", "text": "within two years", "start": 67, "end": 83, "normalized": "within two years"}],
      "exceptions": [],
      "actor_action_map": [{"actor_id": "a01", "action_id": "p01"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

## 三个版本共用的 Notes

### 英文原文

- These four examples are synthetic and are not members of the 12-record pilot or the
  EStG-150 formal evaluation set.
- Barrientos is used only for strict structured-output discipline, fixed labels,
  validation, normalization, and traceability. RC4PC fields are not used.
- Prompt sampling parameters remain runtime configuration, not instructions trusted from
  this Markdown file.

### 中文翻译

- 这四个示例是合成示例，不属于 12 条记录的 pilot，也不属于 EStG-150 正式评估集。

- Barrientos 仅用于严格的结构化输出纪律、固定标签、校验、规范化和可追溯性。不使用 RC4PC 字段。

- prompt 的采样参数仍属于运行时配置，不能将本 Markdown 文件中的采样说明视为可信指令。

译注：此处“四个”同样是原文历史措辞，实际为六个。Notes 是源文件说明，不是系统指令正文。

## 字段和受控 reason 的中文含义

| 原文标识 | 中文含义 |
|---|---|
| modality / actor / action | 情态 / 参与者 / 动作 |
| condition / constraint / exception | 条件 / 约束 / 例外 |
| clause_span / start / end | 分句跨度 / 起点（包含）/ 终点（不包含）|
| normalized | 用于匹配的规范化表达 |
| actor_action_map / order_relations | 参与者与动作映射 / 顺序关系 |
| unsupported_or_ambiguous | 不受支持或存在歧义的项目 |
| reference_status=unresolved_coreference;independence_status=context_required | 指代未解析；独立解释需要上下文 |
| semantic_scope_ambiguous_in_target | 目标文本内的语义作用范围有歧义 |
| clause_boundary_ambiguous | 分句边界有歧义 |
| context_required | 需要上下文 |
