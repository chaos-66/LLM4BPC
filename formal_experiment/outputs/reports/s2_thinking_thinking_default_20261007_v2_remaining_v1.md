# high思考默认生成上限：EStG-150完整对比

状态：complete；新调用150/150；0重试；关闭组/Sun新调用0。

原v6/high保持；请求不传max_tokens，按官方默认65536生成上限执行。主指标为五字段coarse pooled micro-F1；modality独立。

| 条件 | 新调用 | Overall F1 | Modality macro-F1 | 失败/150 |
|---|---:|---:|---:|---:|
| thinking_on | 150 | 0.8117 | 0.7919 | 1 |
| off_formal | 0 | 0.8378 | 0.7695 | 0 |
| sun | 0 | 0.7631 | 0.7128 | 0 |
| off_0813 | 0 | 0.8224 | 0.7537 | 0 |

相对原主表关闭：-2.6061个百分点；相对0813历史关闭：-1.0742个百分点。

Token统计（p90使用nearest-rank）：

| 项目 | 总量 | 均值 | 中位数 | p90 | 最大值 |
|---|---:|---:|---:|---:|---:|
| reasoning_tokens | 2596507 | 17426.22 | 16499 | 27404 | 37344 |
| final_answer_tokens | 124441 | 835.17 | 685 | 1358 | 2864 |
| generated_tokens_total | 2720948 | 18261.40 | 17335 | 29120 | 40208 |
| prompt_tokens | 664517 | 4459.85 | 4446 | 4529 | 4643 |

生成token总量相对已有0813关闭：22.257倍。

length截断0条；空最终答案1条；壁钟耗时3219.528秒。

费用按返回usage和公开价格估算，未查账户实扣：
{"known_usage_calls": 149, "input_tokens": 664517, "output_tokens_including_reasoning": 2720948, "cache_hit_input_tokens": 197248, "peak_no_cache_estimate_usd": 11.65211652, "peak_reported_cache_estimate_usd": 11.400428072, "off_peak_reported_cache_estimate_usd": 5.700214036, "account_deduction_verified": false, "usd_guardrail": 50.0}

比较边界：

- One new repeat; historical off reuse, not a simultaneous randomized mode comparison.
- Formal off R3 predates 0813; current alias can represent a changed model.
- Existing off_0813 uses the same documented release; server drift remains possible.
- off_0813 preserves the estg_000092 model-emitted source_text mismatch; sent-input fingerprints match.
- Thinking uses provider default 65536; historical off ceiling is 4096. Not an equal-budget causal test.
- temperature=0 is ignored in thinking mode; no deterministic or stability claim.
- Fixed existing benchmark; no independent unseen test or replacement of frozen main tables.
- 105 parent calls retained, including its balance-concurrency 429; only 45 never-sent IDs dispatched.
- Transport concurrency lowered from 12 to 5; further balance limits throttle fresh IDs, never retries.
- Missing 429 usage is conservatively reserved in the budget; public-price cost estimates cover known usage only.

原16K截断及单例393216诊断独立保留，未混入这150条。证据目录：outputs/evidence/s2_thinking_sensitivity_v1/thinking_default_20261007_v2_remaining_v1

## 分字段与失败诊断

| 字段 | 历史0813关闭 F1 | 本次high F1 | 变化（百分点） |
|---|---:|---:|---:|
| actor | 0.7083 | 0.7213 | +1.30 |
| action | 0.9185 | 0.9534 | +3.49 |
| condition | 0.8405 | 0.8587 | +1.81 |
| constraint | 0.7578 | 0.6892 | -6.86 |
| exception | 0.7000 | 0.7778 | +7.78 |

主要观察：actor/action/condition/exception的F1上升，constraint从0.7578降到0.6892；未匹配constraint抽取68→117。整体precision从0.8150降到0.7807，recall从0.8301升到0.8453，五字段pooled F1下降。未匹配按既定Gold和coarse规则统计，不直接等同于法律语义错误。

为检查单条限流是否完全解释差异，另做同一失败ID置空的离线诊断：将历史关闭的estg_000313也作为空预测，其F1=0.8188；本次思考仍为0.8117，相差-0.71个百分点。这是人为置空的诊断值，不是历史关闭的真实结果，不替换主指标，不改旧预测或Gold。

149条有效响应全部为纯JSON对象并通过canonical校验；历史0813关闭150条中107条为纯JSON对象，其他输出由相同共享解析器处理。语法服从改善与主F1变化分别报告。

149条已知usage：平均思考17426.22、最终答案835.17、总生成18261.40 tokens；历史关闭150条平均输出815.01。总生成约22.26倍，约95.43%用于思考。已知usage返回缓存后闲时估算USD5.700214036、峰价USD11.400428072，未核实账单；那条429无usage，硬预算保守预留，未假定其实际费用为0。

从第一次派发至全部结束约53.66分钟，包含限流排空、封存/续跑准备间隔；续跑API阶段约20.80分钟。该壁钟时间不作与历史关闭组的等并发速度比较。

本次是单批历史对照的操作配置敏感性结果；没有观察到开启high思考带来的主F1收益。固定论文表一/表二保留。诊断机器证据：outputs/reports/s2_thinking_thinking_default_20261007_v2_remaining_v1_diagnostics.json
