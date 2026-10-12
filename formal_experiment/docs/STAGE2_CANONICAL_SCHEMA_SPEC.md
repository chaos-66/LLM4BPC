# Part 2 Canonical Prediction Schema Spec

> **目的**：统一 Part 2 输出契约（D1 / H1 / B0 全部共用）。
> **版本**：v1.0.0（2026-07-12）
> **JSON Schema**：`configs/schemas/stage2_prediction.schema.json`
> **Python validator**：`src/bpc_hybrid/stage2_canonical.py`
> **Wave 1.1 §2 交付**

---

## 1. 为什么需要这个 schema

在 Wave 1 之前，至少有 4 套互不兼容的 Part 2 输出表示：

| 表示 | 文件 | 特点 |
|---|---|---|
| `MultiClauseExtractionResponse` | `src/bpc_hybrid/schema.py` 0.1.0 | 每个 clause 每字段最多一个 `FieldSpan`（**单 span，不支持多 actor/action**） |
| Human Gold review | `configs/schemas/human_gold_review.schema.json` 1.0.0 | 数组式 spans（支持多 actor/action），但混入 review metadata |
| `SunRuleRecord` | `src/bpc_hybrid/sun_compat/schema.py` | 字符串型，无 span，无法追溯证据 |
| D1/H1 prompt 输出 | `prompts/sun_compat/direct_llm_sun_record_prompt.md` | 扁平六字符串，无 span、无 ID、无 clause 边界 |

**后果**：
- B0 跑出来的记录无法直接跟 LLM 记录对齐
- LLM 输出的"action 1"、"action 2"在 Gold 端是同一个 actor 引用，ID 互不认识
- prompt 里的 few-shot 例子没字符 offset，跑出来就破 schema
- Part 3 拿不到细粒度证据，只能用 lemmatized string 匹配

**canonical schema 的目标**：一个、所有方法共用、机器能严格校验、人类能一眼读懂。

---

## 2. 顶层结构

```json
{
  "schema_version": "1.0.0",
  "sample_id": "estg_000001",
  "source_id": "EStG § 6 Abs. 1",
  "source_text": "...完整法规句子...",
  "clauses": [ { "clause_id": "estg_000001_c01", "...": "..." } ],
  "method": { "name": "sun_rule_only", "schema_source": "stage2_prediction.schema.json@1.0.0" },
  "validation": { "schema_valid": true, "cross_field_valid": true, "errors": [] },
  "unsupported_or_ambiguous": [
    { "field": "exception", "reason": "no exception marker in this sentence" }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `schema_version` | const `"1.0.0"` | ✓ | 严格匹配，不允许兼容旧版本 |
| `sample_id` | string non-empty | ✓ | 跨数据集稳定 ID（精确值由 frozen input manifest 决定） |
| `source_id` | string non-empty | ✓ | 来源定位符（如 `EStG § 6 Abs. 1` 或 `gdpr_art_33`） |
| `source_text` | string non-empty | ✓ | 完整源文本；所有 span 字符 offset 都基于此 |
| `clauses` | array | ✓ | 0-N 个 clause；空数组表示"无规范性子句" |
| `method` | object | ✓ | 见 §3 |
| `validation` | object | ✓ | validator 写入；不允许 producer 伪造 |
| `unsupported_or_ambiguous` | array | ✗ | 显式记录无法抽取的字段 + 原因 |

**additionalProperties = false**：顶层、method、validation、clause、span 都不允许额外字段。

---

## 3. method 对象

```json
{
  "name": "sun_rule_only" | "sun_llm_fallback" | "direct_llm",
  "schema_source": "stage2_prediction.schema.json@1.0.0"
}
```

`schema_source` 是契约自描述符；以后 schema 升级到 2.0.0 时，老记录通过此字段识别版本。

---

## 4. span 体系

canonical schema 有 4 类 span：

| 类型 | 字段 | 用途 |
|---|---|---|
| `span` | `text`, `start`, `end` | 最小证据单元（modality.evidence、clause_span、order_relations.evidence） |
| `identifiedSpan` | `span` + `id` | 带稳定 ID 的 span（actor/action/condition/constraint/exception） |
| `supportedSpan` | `identifiedSpan` + `normalized` | 同上 + 独立的 normalized value |

**统一规则**：
- `text` 必须严格等于 `source_text[start:end]`（Python slice 语义，end 不含）
- `start < end <= len(source_text)`
- 所有 `id` 在一条 record 内唯一
- `normalized` 可以与 `text` 不同（大小写、lemma、缩写、停用词等）但**不**能伪装成 raw text 修改证据

---

## 5. clause 结构

```json
{
  "clause_id": "estg_000001_c01",
  "clause_span": { "text": "The controller shall ...", "start": 0, "end": 51 },
  "modality": {
    "label": "obligation",
    "evidence": [ { "text": "shall", "start": 13, "end": 18 } ]
  },
  "actors":      [ { "id": "a01", "text": "The controller", "start": 0, "end": 12, "normalized": "controller" } ],
  "actions":     [ { "id": "p01", "text": "notify the authority", "start": 19, "end": 41, "normalized": "notify authority" } ],
  "conditions":  [ { "id": "c01", "text": "in case of breach", "start": 42, "end": 58, "normalized": "in case of breach" } ],
  "constraints": [],
  "exceptions":  [],
  "actor_action_map": [ { "actor_id": "a01", "action_id": "p01" } ],
  "order_relations": []
}
```

**关键设计**：
- `modality` 仍是 4 类 enum（`obligation`, `prohibition`, `permission`, `definition`）
- 5 个 field（actor/action/condition/constraint/exception）全部为**数组**，支持多 actor / 多 action
- `actor_action_map` 用 `actor_id` / `action_id` 引用 actors/actions 数组里的 id
- `order_relations` 用 `before_action_id` / `after_action_id` 引用 actions 数组里的 id
- `clause_id` 格式不限，但**全 record 唯一**；精确 ID 集合由 frozen input manifest 决定

---

## 6. 未解决的设计决策（unresolved blockers）

### 6.1 `actions` 是否允许为空

**问题**：当 `modality.label == "definition"`（"X means..." 类定义句）时，整句是定义，没有明确 action。

**当前 schema 决定**：`actions: minItems: 0`（允许空数组）

**理由**：
- v1 human_gold_review schema 强制 `actions: minItems: 1`——但这是**标注**契约，对预测太严
- Sun 论文证据尚不足以明确：definition 是否必须有一个 placeholder action
- Part 3 adapter 收到空 actions 时，应跳过 missing-action 检查（这是 Part 3 自己的事）

**Unresolved blocker**：等待 Sun 最终版全文 + Part 3 配置冻结后再决。当前**保守允许空**。

### 6.2 5/6-digit sample_id 冲突

**问题**：
- v1 human review pack 用 6 位 ID（`estg_000001` ~ `estg_000150`）
- v2 草案用 5 位 ID（`estg_00001` ~ `estg_00150`）

**当前 schema 决定**：`sample_id` 只要求 non-empty string，不强制 pattern。**精确 ID 集合由 frozen input manifest 决定**。

**理由**：
- ID 是数据契约，不应耦合到 schema
- 多个 pack 可共存：v1 走 v1 ID，v2 走 v2 ID，schema 同时接受
- producer 必须从 input manifest 取 ID，**不允许**自创 ID

**Unresolved blocker**：v2 input manifest 何时冻结、是否取代 v1。

### 6.3 v1 review pack 是否迁移

**决定**：**不迁移**。v1 旧 review pack 保留为 development-only 数据。
- v1 旧 schema `human_gold_review.schema.json@1.0.0` 保留，但仅用于读 v1 数据
- canonical schema `stage2_prediction.schema.json@1.0.0` 是**所有 B0/H1/D1 输出**的契约
- Human Gold review pack v2（如果新建）将使用一个新的 review schema（**不是** canonical schema），把 canonical payload 包装一层 + 加 review metadata

---

## 7. 跨字段验证规则（Python 实现）

JSON Schema 表达不了的，Python validator 强制：

| 规则 | 失败时 |
|---|---|
| `text == source_text[start:end]` | 记录 error，`cross_field_valid=false` |
| 子 span 位于 clause_span 内 | 记录 error |
| 同一 record 内 `clause_id` 唯一 | 记录 error |
| 同一 record 内 span `id` 唯一 | 记录 error |
| `actor_action_map[i].actor_id ∈ actors[].id` ∪ {null} | 记录 error |
| `actor_action_map[i].action_id ∈ actions[].id` | 记录 error |
| `order_relations[i].before/after_action_id ∈ actions[].id` | 记录 error |
| `modality.label ∈ 4 类` | 记录 error（schema 也会卡） |
| `modality.evidence` 非空 | 记录 error |
| `method.name ∈ 3 个方法 id` | 记录 error |
| `validation` 字段只允许 validator 写入 | producer 写会被覆盖 |

**实现**：`src/bpc_hybrid/stage2_canonical.py::validate_canonical()`

---

## 8. 与 v1 human_gold_review schema 的关系

| 项 | v1 human_gold_review 1.0.0 | canonical stage2_prediction 1.0.0 |
|---|---|---|
| 用途 | 人工 Gold 审核包 | Part 2 预测输出 |
| 顶层字段 | `text_review`, `annotation_review`, `do_not_auto_score` | `method`, `validation` |
| Review 状态机 | ✅ 内嵌 | ❌ 没有（review 走独立 schema） |
| 字符 offset | ✅ | ✅ |
| 多 actor / 多 action | ✅ 数组 | ✅ 数组 |
| normalized 字段 | ❌ | ✅ supportedSpan |
| unsupported_or_ambiguous | ❌ | ✅ 显式记录 |
| 跨字段 validator | 简化版 | 严格版（见 §7） |
| 来自 production data | ✅（待 v2 路由锁定） | ✅（B0/H1/D1 输出） |

**关系**：v2 human review pack（如果新建）会**包装**一个 canonical payload 作为 `prediction`，外加 review metadata。即 review schema = canonical payload + review state machine + extra fields。

**禁止**：把 review schema 与 prediction schema 合并到同一对象（任务 §2 明确禁止）。

---

## 9. 与 B0/H1/D1 三组方法的对接

| 方法 | 输入 | 输出 | 调用 validator |
|---|---|---|---|
| B0（`sun_rule_only`） | 法规句子 | canonical payload | `validate_canonical()` |
| H1（`sun_llm_fallback`） | 法规句子 + rule 预测 | canonical payload（rule + LLM 合并） | `validate_canonical()` |
| D1（`direct_llm`） | 法规句子 | canonical payload | `validate_canonical()` |

**H1 合并规则**（task §3.3）：
- H1 不是生成完整 6 字段，**只**是 repair patch
- patch 结构：`{sample_id, clause_id, repair_field, replacement_span_array_or_modality, repair_reason, provenance}`
- H1 runner 把 patch 应用到 B0 预测上，**生成 canonical payload**，然后过 validator
- prompt 文件 + repair patch contract 是 prompt loader 加载的，**不是**硬编码字符串

---

## 10. 测试覆盖

测试位置：`tests/test_stage2_prediction_schema.py`

| 测试 | 覆盖规则 |
|---|---|
| `test_schema_loads` | JSON Schema 文件存在且可 load |
| `test_canonical_minimal` | 最小合法 record 通过 |
| `test_canonical_full_obligation` | 完整 obligation + 5 字段 + 1 actor_action_map |
| `test_canonical_multi_clause` | 多个 clause |
| `test_canonical_multi_actor` | 多 actor + 多 actor_action_map edge |
| `test_canonical_definition_no_action` | definition 可 actions=[] |
| `test_invalid_span_text_mismatch` | text != source_text[start:end] → error |
| `test_invalid_span_out_of_bounds` | end > len(source_text) → error |
| `test_child_span_outside_clause` | 子 span 不在 clause 内 → error |
| `test_duplicate_clause_id` | clause_id 重复 → error |
| `test_duplicate_span_id` | span id 重复 → error |
| `test_bad_actor_id_reference` | actor_id 不在 actors[] → error |
| `test_bad_action_id_reference` | action_id 不在 actions[] → error |
| `test_bad_order_relation_id` | order id 不在 actions[] → error |
| `test_extra_key_rejected` | 顶层加额外键 → schema 拒收 |
| `test_invalid_modality_label` | modality.label 不在 4 类 → error |
| `test_modality_evidence_empty` | modality.evidence=[] → error |
| `test_unknown_method_name` | method.name 不在 3 个 → error |
| `test_normalized_can_differ` | normalized != text 允许 |
| `test_validation_field_overwritten_by_validator` | producer 写 validation → 被覆盖 |
| `test_sample_id_minlength_1` | sample_id="" → error |
| `test_source_id_minlength_1` | source_id="" → error |
| `test_batch_validator_counts` | validate_canonical_batch 计数正确 |

---

## 11. DoD（完成定义）

- [x] `configs/schemas/stage2_prediction.schema.json` 存在
- [x] `src/bpc_hybrid/stage2_canonical.py` 实现 schema load + cross-field + validate_canonical + validate_canonical_batch
- [ ] `tests/test_stage2_prediction_schema.py` 23 个测试全过
- [ ] D1/H1 prompt 改用 canonical 输出（§3）
- [ ] B0 输出迁移到 canonical（未来 B0 实施时）
- [ ] audit integrity pass 加 canonical schema 检查（§8）

---

## 12. 仍保留的 blocker

- v2 human review pack 何时冻结
- v1 vs v2 sample_id 集何时合并
- definition 的 action 规则（见 §6.1）
- Part 3 adapter 如何处理空 actions 的 clause

这些**不是** canonical schema 本体的 blocker，是项目级未决议题。


## Empty-vs-error semantics (user decision, 2026-08-05)

Empty is not an error. The six semantic elements (modality evidence, actor,
action, condition, constraint, exception) may be partially empty; Gold does
not imply every element is present. modality.evidence and
orderRelation.evidence are arrays with minItems: 0 (empty means the
producer could not identify a surface trigger). D1-R1 pipeline behavior:
unrecoverable field spans and clauses are dropped with an audit trail
(dropped_spans / dropped_clauses) instead of failing the whole record;
only record-level structural violations fail closed.
