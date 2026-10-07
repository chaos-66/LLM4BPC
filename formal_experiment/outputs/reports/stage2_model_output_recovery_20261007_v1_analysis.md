# 六家模型格式恢复与补跑结果解读

本次用户授权的15条离线恢复及18次补跑已完成；六家全部150条有效尚未完成。
原首轮900次及固定论文主表均保留，新条件另列，不把恢复后数据冒充首轮成功率。

| 模型 | 首轮有效/150 | 当前有效/150 | 首轮五字段pooled F1 | 当前F1 | 差值（百分点） | modality macro F1 |
|---|---:|---:|---:|---:|---:|---:|
| qwen3.8-max-2026-09-02 | 148 | 150 | 0.8030 | 0.8078 | +0.480 | 0.8234 |
| mimo-v2.6-pro | 147 | 150 | 0.8184 | 0.8191 | +0.073 | 0.8222 |
| kimi-k2.6 | 141 | 148 | 0.7464 | 0.7511 | +0.477 | 0.7616 |
| grok-4.3 | 147 | 150 | 0.7723 | 0.7738 | +0.148 | 0.7582 |
| glm-5.2 | 142 | 149 | 0.7833 | 0.7949 | +1.159 | 0.7168 |
| MiniMax-M3 | 142 | 149 | 0.7345 | 0.7413 | +0.686 | 0.8032 |

所有评价仍使用同一完整150条分母，失败作为空预测，不用有效子集缩小分母。Overall是五字段pooled F1，modality单列，不取分字段平均。
历史固定DeepSeek150/150有效，F1=0.8378；Sun本地重建固定F1=0.7631，两者未重跑或改数。

15条离线恢复只还原重复回显source_text的引号/空白；原抽取字段不变。18次沿用原请求体和模型：14条有效，4条再次结构失败；未出现新增余额或RPM失败。共896/900个provider/sample预测有效，累计API918次。
新请求也适用相同的仅回显格式恢复规则，保持所有平台规则一致。

## 剩余4条的实际错误

- kimi/estg_000077：clauses[3].modality.label must be one of ('obligation', 'prohibition', 'permission', 'definition'), got 'condition'
- kimi/estg_000111：clauses[0].conditions[0] not inside clause_span
- glm/estg_000164：clauses[1].actions[0].id duplicate: 'p01'；clauses[1].constraints[0].id duplicate: 'c01'；clauses[2].actions[0].id duplicate: 'p01'；clauses[2].conditions[0].id duplicate: 'd01'；clauses[2].constraints[0].id duplicate: 'c01'；clauses[3].actions[0].id duplicate: 'p01'；clauses[3].conditions[0].id duplicate: 'd01'；clauses[3].constraints[0].id duplicate: 'c01'；clauses[3].constraints[1].id duplicate: 'c02'
- minimax/estg_000164：clauses[1].conditions[0].id duplicate: 'd01'；clauses[2].actions[0].id duplicate: 'p01'；clauses[2].conditions[0].id duplicate: 'd01'；clauses[2].constraints[0].id duplicate: 'c01'；clauses[2].constraints[1].id duplicate: 'c02'

两个estg_000164为跨clause重复ID，属于序列化身份问题；Kimi000077生成了枚举外的condition标签，Kimi000111的condition跨度越过clause_span。当前授权只允许15条source_text格式恢复和18个原样补跑，未授权修改上述ID、标签或clause边界，故均保留失败。不能从Gold猜标签或修改Gold使之通过。
18次新增额度已用完。继续补齐需要另行选定结构处理规则或额外调用额度，不能利用费用尚有余量自动增加次数。

## 用量和解释范围

新增费用按官方冻结非缓存价格与返回用量估算CNY0.797801900+USD0.00791125，低于授权CNY3.83/USD0.05；账户实扣未验证。实际API壁钟81.34秒，0自动重试。
Kimi thinking.type=disabled，无返回思考正文，实际1 reasoning token计数按用户已接受例外保留；不归零、不解释该1 token语义。
恢复与补跑后的最高F1为MiMo0.8191，其次Qwen0.8078；两者仍低于历史固定DeepSeek0.8378。这只是固定150条与当前服务/参数/协议的描述性观察，未重复采样或作纯模型因果、显著性推断。
新报告的planned_calls=900沿用原覆盖规模；本批新调用预算恰18、累计上限918见独立授权、plan和manifest，不将旧900预算视为允许918。

原900所有产物及867原成功预测保持；新响应、账本、合并预测、评估与manifest另存。GitHub原始产物外发许可仍未确认，自动审批拒绝push保持，不声称远端备份。
