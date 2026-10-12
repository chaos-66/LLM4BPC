# Gold Annotation Protocol

**状态：v2 Layer E 输入门已就绪，用户可以立即继续人工审核；当前仍为 0/150
adjudicated，因此不得冻结或发布正式 Gold。唯一活动编辑面是
`data/development/human_review/estg_150_human_correction_v1.json`。路线、数据、
Part 3 和正式 Gold 发布白名单仍未共同重锁。**

## Unit

每条原始法规句子有稳定 `sample_id`。若一句包含多个 normative clauses，则每个 clause 使用稳定 `clause_id`，并保留 parent `sample_id`。不得为了适配某个模型输出而改变 clause 数量。

## Phrase Annotation

六字段为：

- `modality`：obligation/prohibition/permission/definition。
- `actor`：执行或承担规范的最小显式主体。
- `action`：最小可匹配的 verb + object/action phrase。
- `condition`：规则适用的 if/when/where 条件。
- `constraint`：时间、数量、范围、方式或法条限制。
- `exception`：unless/except/without prejudice 等例外。

每个非空字段至少保存：

```json
{
  "value": "within 72 hours",
  "start": 42,
  "end": 57
}
```

`approved_text_en[start:end]` 必须与 `value` 一致。没有显式 span 时使用空数组或 `actor_id: null`，不得凭常识补造文本。

Modality 的类别值与原文 modal span 应分开保存，避免把 `obligation` 当成原文 span。

## Sun Rule Record

从审核后的 clauses deterministic 地构造：

`r=(tr,Ar,Pr,Cr,Or,Er,Ur,fr)`

- `tr`：rule type。
- `Ar/Pr/Cr/Or/Er`：action/actor/condition/constraint/exception sets。
- `Ur`：action order relations。
- `fr`：actor-to-action mapping。

rule record 应由 Gold 派生，不应再单独手填一份容易矛盾的值；人工只需确认派生结果。

## Review

每条记录必须包含 reviewer、reviewed_at、confidence、notes、status。建议 10% 以上由第二位审核者独立复核；分歧按书面 adjudication 规则解决。

当前审核包故意不包含模型预测，避免锚定偏差。审核者必须以人工批准的文本和 annotation guideline 为准。

## Validation

最终 validator 必须检查：全量 ID 覆盖、唯一 ID、合法 modality、span 边界、span 文本一致、clause 覆盖、actor-action map、review metadata 和未审核行数量为 0。
