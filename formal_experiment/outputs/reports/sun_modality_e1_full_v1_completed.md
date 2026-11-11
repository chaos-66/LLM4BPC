# E1 在 426 条德语样本上的 Macro-F1 为 0.871371

E1 将原 22-shot 的第 15 条训练示例替换为一条完整的税款抵减定义。相对同批历史 22-shot，判对数从 393 增至 396，4 条改对、1 条回归，Macro-F1 增加 0.158 个百分点。10,000 次逐句配对 bootstrap 的差值 95% 区间为 −0.886 至 +1.001 个百分点。选例参考过本测试集的错误，这批结果可用于描述实际变化，跨样本收益仍有不确定性。

| 指标 | 原 22-shot | E1 |
|---|---:|---:|
| 判对数 | 393/426 | 396/426 |
| Macro-F1 | 0.869788 | 0.871371 |
| definition F1 | 0.911765 | 0.921283 |
| obligation F1 | 0.956743 | 0.966752 |
| permission F1 | 0.904762 | 0.891566 |
| prohibition F1 | 0.705882 | 0.705882 |

禁止类的 7 条误报和 3 条漏报逐条相同，TP/FP/FN 均为 12/7/3。Sun 本地重建在同一测试集上的 Macro-F1 为 0.877228，高于 E1 约 0.586 个百分点。[Sun 重建结果](sun_modality_five_way_v1.json)

## 五条首标签变化

样本 ID 省略共同前缀 `sun_modality_`。每个版本均读取原 Rule Record 首个非空模态。两版均有一条空规则，保留在 426 条分母内。

| 样本 ID | 语料标签 | 原 22-shot → E1 | 句义与结果 |
|---|---|---|---|
| `5c7ac6760deb9439` | definition | obligation → definition | 预缴款抵减所得税债，直接目标改对。复用 E1 小批返回。 |
| `a18989112132a992` | definition | obligation → definition | 分配款减少账户余额，改对。复用 E1 小批返回。 |
| `fdc9485a3ed1b40f` | definition | obligation → definition | 特定情形下认定存在雇佣关系，改对。 |
| `f5037bcc56922965` | obligation | definition → obligation | 在请求权转移条件下，差额须在五年中均匀扣除，改对。 |
| `e10c26a6829f26c0` | permission | permission → definition | 停业时依申请可免于确认有关隐含储备，回归。 |

与历史 24-shot 账本逐句对齐，425/426 条首标签相同。唯一差异是直接目标 `5c7ac6760deb9439`，24-shot 判为义务，E1 判为定义。其余三条改对和一条回归也曾出现在 24-shot。仅凭这些历史对照无法确定每条翻转的原因。[24-shot 逐句变化](sun_modality_prohibition_shots_v1_completed.md)

## 执行与核对

复用 5 条已按请求和返回哈希核验的 E1 小批结果，新增 421 次官方 `deepseek-v4-pro` 请求，零重试。新增请求中有 2 条由错变对、1 条回归。按服务端用量和项目费率估算，新增费用 ¥18.915759，复用的 5 条 E1 历史费用 ¥0.2576052。全部 426 条分别有一份 E1 返回，已从原始返回独立核对首标签、逐类 TP/FP/FN 和整体 Macro-F1。[完整指标、配对比较与账本哈希](sun_modality_e1_full_v1_completed.json) · [预检](sun_modality_e1_full_v1_preflight.json) · [小批结果](sun_modality_es_minimal_v1_pilot_20261111.json)
