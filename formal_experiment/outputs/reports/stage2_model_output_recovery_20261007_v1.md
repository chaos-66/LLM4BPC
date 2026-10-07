# 六家非思考模型：15条格式恢复与18次补跑

本批实际18/18次，累计918次；离线恢复15条。

| 平台 | 原有效 | 离线恢复 | 补跑 | 当前有效/150 | 五字段pooled F1 | 失败 |
|---|---:|---:|---:|---:|---:|---:|
| qwen | 148 | 1 | 1 | 150 | 0.8078 | 0 |
| mimo | 147 | 1 | 2 | 150 | 0.8191 | 0 |
| kimi | 141 | 6 | 3 | 148 | 0.7511 | 2 |
| grok | 147 | 2 | 1 | 150 | 0.7738 | 0 |
| glm | 142 | 2 | 6 | 149 | 0.7949 | 1 |
| minimax | 142 | 3 | 5 | 149 | 0.7413 | 1 |

新增保守费用估算：{"CNY": 0.7978019000000001, "USD": 0.00791125}；账户实扣未核对。

剩余失败：[{"provider": "kimi", "sample_id": "estg_000077", "failure_stage": "canonical_validation"}, {"provider": "kimi", "sample_id": "estg_000111", "failure_stage": "canonical_validation"}, {"provider": "glm", "sample_id": "estg_000164", "failure_stage": "canonical_validation"}, {"provider": "minimax", "sample_id": "estg_000164", "failure_stage": "canonical_validation"}]

- 固定150条的单次模型与平台配置比较，不证明独立泛化、统计显著性或稳定性。
- 所有模型关闭思考，各家采样约束不同，temperature并非严格相同。
- 历史DeepSeek/Sun只复用，不新增其调用，不替换固定论文表一或表二。
- API运行授权与原始产物GitHub外发备份许可分别记录，后者仍待明确许可。
- Kimi仅1 token且无思考正文的计数差异由用户明确接受，实际计数保留，不宣称该token为占位符；原严格失败证据保留。
- GLM/MiMo首条余额失败保留在150分母；充值后仅续跑149从未尝试项，不隐去基础设施失败。
- Kimi一次HTTP429/RPM=3保留失败且不重发；其余145个未发送项开始间隔至少21秒，0重试。
- 新条件：用户批准15条仅回显引号/空白离线恢复，18条原样各新尝试一次；同一回显格式规则适用于新响应，抽取字段与原adapter/evaluator保持。原首轮900次和固定主表不变，不冒充首次成功率。
