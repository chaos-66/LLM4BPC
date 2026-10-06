# high思考默认生成上限：EStG-150完整对比

状态：partial；新调用105/150；0重试；关闭组/Sun新调用0。

原v6/high保持；请求不传max_tokens，按官方默认65536生成上限执行。主指标为五字段coarse pooled micro-F1；modality独立。


length截断0条；空最终答案1条；壁钟耗时1297.424秒。

费用按返回usage和公开价格估算，未查账户实扣：
{"known_usage_calls": 104, "input_tokens": 463919, "output_tokens_including_reasoning": 1891198, "cache_hit_input_tokens": 133888, "peak_no_cache_estimate_usd": 8.10151716, "peak_reported_cache_estimate_usd": 7.930676072, "off_peak_reported_cache_estimate_usd": 3.965338036, "account_deduction_verified": false, "usd_guardrail": 50.0}

比较边界：

- One new repeat; historical off reuse, not a simultaneous randomized mode comparison.
- Formal off R3 predates 0813; current alias can represent a changed model.
- Existing off_0813 uses the same documented release; server drift remains possible.
- off_0813 preserves the estg_000092 model-emitted source_text mismatch; sent-input fingerprints match.
- Thinking uses provider default 65536; historical off ceiling is 4096. Not an equal-budget causal test.
- temperature=0 is ignored in thinking mode; no deterministic or stability claim.
- Fixed existing benchmark; no independent unseen test or replacement of frozen main tables.

原16K截断及单例393216诊断独立保留，未混入这150条。证据目录：outputs/evidence/s2_thinking_sensitivity_v1/thinking_default_20261007_v2
