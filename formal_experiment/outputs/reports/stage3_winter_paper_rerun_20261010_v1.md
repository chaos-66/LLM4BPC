# Stage 3：论文同口径 Winter 完整重跑

状态：开发期对照完成；不是独立未见测试或正式发布。

115 个案例（原始 113 + 顺序补充 2），33 条要求；每方法 201 个评分单元（69 正、132 负）。

| 方法 | Precision | Recall | F1 |
|---|---:|---:|---:|
| Sun-style Rules-Only | 0.3814 | 0.5362 | 0.4458 |
| LLM-RE | 0.4393 | 0.6812 | 0.5341 |
| Winter baseline | 0.4634 | 0.5507 | 0.5033 |

Sun/LLM-RE 原数值复用固定来源，Winter 从头运行全部案例×全部要求；不按预期排序调参。

Winter TP/FP/FN/TN：38/44/31/83。
历史 Winter 11187 个信号逐项比较，差异字段数 0。旧 manifest 声明 completed；无法据此判断用户另一次中断运行。

| Winter 类型 | P | R | F1 | 评分单元 |
|---|---:|---:|---:|---:|
| missing_action | 0.2979 | 0.4242 | 0.3500 | 113 |
| incorrect_actor | 0.6857 | 0.7273 | 0.7059 | 80 |
| out_of_order | 0.0000 | 0.0000 | 0.0000 | 8 |

Winter coverage=0.9602；unknown rate=0.0398。

原论文表元数据标记 113 个基础案例；其来源收敛报告的计数包含另外 2 个顺序案例。本次保留原文件，明确总数 115。

验证与限制：

5 项具名相关测试通过（1.97 秒，非全量）；experiment_run 已写入现有实验日志。
实际入口为 `python formal_experiment/scripts/run_stage3_winter_cpu_v1.py`，完整运行合同见
`outputs/evidence/stage3_winter_paper_rerun_20261010_v1/execution_manifest.json`。
CPU 入口不加载可选 torch，使用原生小模型；缓存与非缓存文档的原生分数一致。

- Same constructed development benchmark as the frozen paper table; not unseen test or formal Oracle.
- Sun/Ours numbers are reused from the hash-bound canonical source, not freshly rerun.
- Sun/Ours reuse MPNet calibrated development results; Winter retains its independent native spaCy backend and fixed gamma/delta.
- Applicable-pair checking; complete rule-selection/end-to-end performance is not claimed.
- Order denominator has only 8 cells. Unknown positives remain FN; unknown negatives are not TN.
- 本工作区既有 Stage 1 correction 完整性错误仍存在；未修改用户文件，未运行全量测试。
