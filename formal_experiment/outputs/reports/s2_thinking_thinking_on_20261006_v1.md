# 开启思考敏感性对比（固定 EStG-150）

状态：partial；新调用 1/150；关闭组和 Sun 新调用均为 0。

主指标：coarse 五字段 pooled micro-F1；modality 独立报告。

比较边界：

- single new repeat; historical off reuse, not contemporaneous randomized mode comparison
- formal off R3 was run before 0813 release; current alias can represent a changed model
- existing off_0813 is an additional same documented release reference; server drift remains possible
- off_0813 preserves one historical model-emitted source_text mismatch (estg_000092); all 150 sent request fingerprints match input; historical payloads are never silently corrected
- on generation ceiling is 16384 versus historical 4096; measures configured operating-mode sensitivity, not equal-budget causal effect
- temperature=0 is ignored in thinking mode; no claim of deterministic generation
- no independent unseen test and no replacement of frozen main Table 1/Table 2

完整请求绑定、原始响应（推理与最终答案分列）、调用账本、停批诊断和 manifest 保存于：
outputs/evidence/s2_thinking_sensitivity_v1/thinking_on_20261006_v1

本次没有可用的最终预测，尚未形成150条性能评价。

验证：3项持久证据检查通过，另1项Git检出字节检查通过；快速完整性通过，未跑全量测试。首次Git暂存缓存行尾差异的失败记录保留，修正后原始SHA一致，未重新绑定manifest。

首条停止原因：HTTP 200，返回型号正确；high思考耗尽16384个生成token，全部为reasoning_tokens，finish_reason=length，最终答案为空。不是网络/密钥/解析故障。

实际调用1/150，0重试，剩余149条未发送；当前没有完整性能指标，不记F1=0。输入4446/输出16384，峰价无缓存估算USD0.07074936、闲时USD0.03537468；账户实扣未查询。

原始证据与失败诊断已保存。恢复预检：s2_thinking_recovery_preflight_v2.json（尚未授权/执行）；建议统一low条件完整150条，保留high失败诊断，累计调用将为151次，需用户追加批准。含已有调用的最大token峰价估算USD11.5502，总保护上限建议USD15。
