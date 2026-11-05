# 22 条训练示例与 reviewer 版的 426 条配对结果

北京时间 2026-11-05 12:44 至 12:54，DeepSeek 官方 API 完成 426 次请求，总费用 ¥9.5435388，重试 0 次。425 条返回有效情态，1 条返回空规则并计入 426 条分母。账本中的请求、返回、用量与费用均已核对。此次只运行新增四条例子的候选臂，对照来自前一天已完成的同模型 reviewer 运行。

| test 指标 | reviewer（18 条真实训练示例） | 新版（22 条真实训练示例） |
|---|---:|---:|
| Macro-F1 | 0.8667 | 0.8698 |
| 正确数 | 392/426 | 393/426 |
| definition F1 | 0.9075 | 0.9118 |
| obligation F1 | 0.9570 | 0.9567 |
| permission F1 | 0.8966 | 0.9048 |
| prohibition F1 | 0.7059 | 0.7059 |

Macro-F1 差值为 +0.31 个百分点，10,000 次配对 bootstrap 的 95% 区间为 −0.98 至 +1.63 个百分点。准确率的精确 McNemar 双侧检验 p=1.00。数据与小幅改善或小幅下降均相容。选例主题参考过该测试集的历史错误，此处用于探索性回归比较。

原来识别的 17 条资格与限制边界样本，从答对 1 条增至 3 条。全体 definition→permission 错误从 9 条降至 7 条，permission→definition 错误从 0 条增至 1 条。新旧首标签仅 5 条发生变化，方向都是改判为 definition。

| 样本 ID 后缀 | 原标签预测 → 新标签预测 | 语料标签及判分 |
|---|---|---|
| `de8ae0a7de8610f6` | permission → definition | 改对。特定面积条件下适用计税方法，属于原 17 条。 |
| `16f796b5340d99ce` | obligation → definition | 改对。特定情况下会计准则具有决定效力。 |
| `ebcf85dc92f6a19b` | permission → definition | 改对。限定可计入的经营费用范围，属于原 17 条。 |
| `7890eade5f0098ac` | obligation → definition | 改错。满足资料和报送条件时须计入特定费用，语料标签为义务。 |
| `6d46f2ca8400b2bc` | permission → definition | 改错。附有例外的费用扣除许可，语料标签为许可。 |

禁止类仍命中 12/15，误报 7 条。上述变化表明在这批样本上，更多句子被归入 definition；跨样本的稳定收益仍待独立验证。

[完整配对统计及账本哈希](sun_modality_eligibility_shots_v1_completed.json) · [执行前冻结记录](sun_modality_eligibility_shots_v1_execution_preflight.json)
