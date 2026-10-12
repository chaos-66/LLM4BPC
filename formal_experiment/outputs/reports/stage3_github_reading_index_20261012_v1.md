# Part 3 既有实验的 GitHub 阅读入口

本页只索引已经运行、核查并保存的证据，不是新实验或新的任务状态页。
日期：2026-10-12。

- 仓库：chaos-66/LLM4BPC。
- 分支：`codex/s2-prompt-simplification-v1`。
- 下列实验文件固定在提交 `58151e9d80212737354c539ea2c6be61fe55cc0f`；链接不随分支后续修改变化。
- 展示名 LLM-SE 对应历史报告中的 LLM-RE / Direct-LLM，历史文件内容保持原样。

## 建议阅读顺序

| 要读的内容 | 人类/网页可读报告 | 机器明细 |
|---|---|---|
| Winter 完整重跑与原表 | [Markdown](https://raw.githubusercontent.com/chaos-66/LLM4BPC/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/outputs/reports/stage3_winter_paper_rerun_20261010_v1.md) | [JSON](https://raw.githubusercontent.com/chaos-66/LLM4BPC/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/outputs/reports/stage3_winter_paper_rerun_20261010_v1.json) |
| 共同评价器、评分范围与排名诊断 | [Markdown](https://raw.githubusercontent.com/chaos-66/LLM4BPC/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/outputs/reports/stage3_comparison_check_20261010_v1.md) | [JSON](https://raw.githubusercontent.com/chaos-66/LLM4BPC/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/outputs/reports/stage3_comparison_check_20261010_v1.json) |
| 201/207 两组结果的冻结预测复算 | [Markdown](https://raw.githubusercontent.com/chaos-66/LLM4BPC/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/outputs/reports/stage3_comparison_reproduction_20261010_v1.md) | [JSON](https://raw.githubusercontent.com/chaos-66/LLM4BPC/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/outputs/reports/stage3_comparison_reproduction_20261010_v1.json) |
| Sun/Winter 方法重建忠实度核查 | [Markdown](https://raw.githubusercontent.com/chaos-66/LLM4BPC/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/outputs/reports/stage3_method_fidelity_check_20261010_v1.md) | [JSON](https://raw.githubusercontent.com/chaos-66/LLM4BPC/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/outputs/reports/stage3_method_fidelity_check_20261010_v1.json) |

先读 Markdown，再按需要读同名 JSON。以上链接是固定提交的 raw 文本；
也可使用 GitHub 连接器，按仓库、提交和路径读取。
新数据讨论另见[来源可行性报告](https://raw.githubusercontent.com/chaos-66/LLM4BPC/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/outputs/reports/stage3_new_batch_feasibility_20261012_v1.md)，
它不是已运行的新数据结果。

## 结果身份与边界

| 方法 | 原表 201 单元 F1 | 扩展范围诊断 207 单元 F1 |
|---|---:|---:|
| LLM-SE | 0.5341 | 0.5281 |
| Sun 本地重建 | 0.4458 | 0.4405 |
| Winter 本地重建 | 0.5033 | 0.5065 |

两组都来自相同的 115 个 BPMN 案例、33 条法规要求；201 单元有 69 正/132 负，
207 单元有 71 正/136 负。207 组只是纳入两个已确认顺序要求的范围诊断，
没有重新生成预测，也没有替换原表。

Winter 已完整原生重跑；Sun/LLM-SE 复用固定来源输出。再次复算验证的是保存预测后的
评价复现，不是三方从头重新生成预测。共同最终评价器的计分与方法别名检查一致，
但完整样本纳入独立性尚未完成核验；方法重建偏离详见忠实度报告。
这些是开发结果，不能认证为原论文完全复现、独立未见测试或正式发布结果。

## 按需定位原始证据

- Winter 执行合同（环境、代码/输入哈希、命令、调用数）：[outputs/evidence/stage3_winter_paper_rerun_20261010_v1/execution_manifest.json](https://github.com/chaos-66/LLM4BPC/blob/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/outputs/evidence/stage3_winter_paper_rerun_20261010_v1/execution_manifest.json)。
- Winter 运行 manifest：[outputs/evidence/stage3_winter_paper_rerun_20261010_v1/run_manifest.json](https://github.com/chaos-66/LLM4BPC/blob/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/outputs/evidence/stage3_winter_paper_rerun_20261010_v1/run_manifest.json)。
- Winter 全部 3,795 个规则—流程 pair 的预测（约 20 MB，按需读取）：[outputs/evidence/stage3_winter_paper_rerun_20261010_v1/predictions.json](https://github.com/chaos-66/LLM4BPC/blob/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/outputs/evidence/stage3_winter_paper_rerun_20261010_v1/predictions.json)。
- Sun/LLM-SE 原有逐案例信号副本：[outputs/evidence/stage3_comparison_check_20261010_v1/sun_ours_selected_dev_signals_v1.json](https://github.com/chaos-66/LLM4BPC/blob/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/outputs/evidence/stage3_comparison_check_20261010_v1/sun_ours_selected_dev_signals_v1.json)。
- 共同开发参考与评分单元：[data/development/stage3_winter_paper_rerun_20261010_v1/evaluation_reference.json](https://github.com/chaos-66/LLM4BPC/blob/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/data/development/stage3_winter_paper_rerun_20261010_v1/evaluation_reference.json)。
- 共同法规输入快照：[data/development/stage3_winter_paper_rerun_20261010_v1/regulation_sources.json](https://github.com/chaos-66/LLM4BPC/blob/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/data/development/stage3_winter_paper_rerun_20261010_v1/regulation_sources.json)。
- 115 个 BPMN 文件：[输入目录](https://github.com/chaos-66/LLM4BPC/tree/58151e9d80212737354c539ea2c6be61fe55cc0f/formal_experiment/data/development/stage3_winter_paper_rerun_20261010_v1/bpmn)。

本次只读核对了上述四类报告、两个证据目录、输入快照及新批次可行性报告，共 140 个文件；
本地 SHA-256 与固定提交中的文件字节全部一致。未重跑实验、调用 API、改标签或运行测试套件。
GitHub 分支指向该提交已由 `git ls-remote` 核验。

如无法读取仓库，明确说明访问失败并要求提供相关文件；不要把无法读取的内容当作已核查。
如要判断排名原因，请引用具体文件和案例，区分已验证事实、实现偏差、诊断结果与待验证推断。
