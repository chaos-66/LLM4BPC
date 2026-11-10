# 显式句级候选执行复核：输出合同失败，保留历史对照

任务 `SUN-MODALITY-FINAL-REVIEW-001` 的唯一候选已按用户“可以跑”“继续”的授权完成。
本轮收集与报告完成；结果不支持替换历史 22-shot。正式主表不受影响。

## 冻结结果

全部426条进入分母，主取值始终为通过预定输出合同校验的 `sentence_modality.label`。
不放宽证据校验，不用首clause或Sun预测填补句级失败，不重排或改写clause。

| 取值 | 正确数/426 | Macro-P | Macro-R | Macro-F1 | 无预测 | 相对历史改对/改错 | 禁止TP/FP/FN |
|---|---:|---:|---:|---:|---:|---:|---:|
| 历史22-shot原取值 | 393 | 0.844110 | 0.903542 | 0.869788 | 1 | — | 12/7/3 |
| 本候选句级主取值 | 12 | 0.541667 | 0.032073 | 0.053099 | 409 | 0/381 | 1/5/14 |
| 本候选同返回首clause诊断 | 364 | 0.746712 | 0.857584 | 0.775741 | 1 | 3/32 | 12/21/3 |

完整四类P/R/F1、主混淆矩阵见 [执行报告](sun_modality_sentence_v1_completed.md)；
双取值完整混淆矩阵、逐ID变化及未舍入指标见 [冻结结果JSON](sun_modality_sentence_v1_completed.json)。
首clause诊断也低于历史对照，不能用该诊断替换主指标来宣称候选成功。

## 直接观察与解释边界

- 426次传输均成功。17条句级输出通过校验并提供标签，1条合法null，408条
  因 `sentence evidence must be an exact, nonempty source span` 被拒。
- 这408条均给出合法类别名、证据字段及整数坐标，但至少一段证据的坐标不能切出所给文本。
  其中407条的所有证据文本本身都是原文子串；另1条至少有一段证据也不是原文子串。
  这些是返回与原文直接比较得到的事实，不是对模型内部原因的证明。
- 本候选的冻结接口把证据字符坐标正确作为主标签有效的条件。因而主分数同时反映
  分类结果与输出合同可用性；大量无预测直接压低召回率。不能把0.053099独立解释为
  模型纯分类能力，也不能事后去掉该条件改报主分数。
- 离线测试验证的是构造器、解析器、分母和预算逻辑遵守固定规则；它没有证明模型能够
  稳定生成正确字符坐标。此次实测揭示了这一未被离线接口测试证明的能力缺口。
- 424条Rule Record未通过既有完整校验。按预定政策，该校验独立披露，不连带否决
  已通过句级校验的标签，也不改变旧首clause诊断的取值语义。
- 句级有效取值与首clause相差408条，全部是“句级无预测、首clause有预测”。
  其余18条为同标签或双方null。另对原始JSON做不评分的字段对比，有6条原始句级label
  与首clause不同；这6条均未通过句级证据校验。不能把408误写为408次有效模态判断改变。
  6条ID与原始字段对比保存在 [观察JSON](sun_modality_sentence_v1_execution_observations.json)，
  不基于这些未通过校验的字段计算另一套分数。
- 原始输出中的不确定性标记：mixed_independent_modalities 13次、incomplete_input 4次、
  corpus_boundary_ambiguous 3次。冻结结果JSON中的uncertainty_counts仅统计通过句级
  校验的输出（incomplete_input 2次），两者统计范围不同。

接口、指导、示例和主取值同时改变；不能把与历史的差值归因于单个提示段。
dev/test此前参与过诊断，本批仍属于test-informed探索性结果，不证明未见数据泛化。
保留历史22-shot；本任务不追加候选或重试，也不修改Gold或既有结果。

## 运行与证据

运行时间：2026-11-10北京时间20:25:32—20:38:23。模型返回别名均为 `deepseek-v4-pro`；
temperature=0、top_p=1、max_tokens=4096、stream=false、thinking=disabled，未改模型或采样。
426次调用，最高4并发，零重试、零请求失败，全部在已授权空闲时段。

按返回用量和已核实空闲时段单价计费为 **¥9.6668145**，硬上限¥35；未结算预留为0，
全过程“已花费＋在途预留”最高¥10.334331。输入2,775,676 tokens（缓存命中1,624,320、
未命中1,151,356），输出314,227 tokens。此处为用量计价核算，不是另行获取的账户账单。

执行命令：

```powershell
python -X utf8 -u formal_experiment/scripts/run_sun_modality_sentence_v1.py execute --wait-for-off-peak
python -X utf8 formal_experiment/scripts/run_sun_modality_sentence_v1.py report
```

候选准备提交：`901f64207dc4f7b40c0d57f129cb0d50e1d5e6e2`。
执行前验证与推送提交：`ef360cd4e9183f5f9d3384d711a61458c519e9b5`。
冻结结果记录执行提交、授权/预检/源码/账本哈希；每个请求和响应的字节绑定、
全426成员关系、计费、并发、空闲时段及无重试约束均已回放核对。

本地原始账本（Git忽略，不上传德语原文/完整响应）：
`outputs/development/sun_modality_sentence_v1/execution_v1/local_only/events.jsonl`。
SHA-256：`33e6b91b2c6978e2b1767623dafe72d8eeaf6bb44f2f33a5526756ea7f5caa32`。

验证范围：执行前具名测试28 passed、1 skipped（真实结果尚不存在）；运行后使用
`tests/test_run_modality_sentence_v1.py::test_completed_report_matches_saved_responses`
核对已存结果，1 passed in 8.69s；批次结束快速完整性检查通过。
具体凭据见本任务的追加实验事件。未启动全量测试。
