# 四类判定边界提示词分支

任务：`SUN-MODALITY-BOUNDARY-001`，对应 S2.4 / EXP-S2A 的独立探索性补充。
用户于 2026-10-31 要求创建分支并试验其效果。

唯一提示词改动：在冻结 v6 system prompt 后追加
`boundary_guidance.md`。用户消息、六个原示例、六要素 JSON 输出、德语输入、
模型 `deepseek-v4-pro`、temperature=0、top_p=1、max_tokens=4096、
thinking=disabled、首个带标签 clause 的取值方式均保留。
这不是 modality-only 提示词；不替换原 v6 或 EStG-150 论文主表。

追加内容明确义务、禁止、许可、定义的语义边界，区分否定行为与否定状态/分类/
适用性/义务存在，并处理主句与条件、例外中的情态。没有复制受限测试集原句作示例。

本次已看过 426 条测试集中的错误，因此结果只能解释为 test-informed exploratory
comparison。原 v6 和 Sun 使用已存历史预测；不声称同期随机对照、盲测泛化或严格
单因素因果证明。一次冻结、一次运行，不按本轮结果继续追调。

执行合同：`configs/supplement/sun_modality_boundary_v1.json`。
最多新增 426 次真实调用、零重试；执行器自设费用上限 ¥20，只在空闲时段执行。
价格于 2026-10-31 核验自 [DeepSeek 官方价格页](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)。
每次调用按全部4096输出额度、UTF-8字节级保守输入上界预留，失败/中断不自动重试。
凭据只取进程环境 `DEEPSEEK_API_KEY`，不读取 `.env`。

```powershell
python formal_experiment/scripts/run_sun_modality_boundary_v1.py --preflight
python formal_experiment/scripts/run_sun_modality_boundary_v1.py --execute
python formal_experiment/scripts/run_sun_modality_boundary_v1.py --report
```

完整返回内容、逐条预测、预算和哈希链账本仅保存在被忽略的
`outputs/development/sun_modality_boundary_v1/`。
可提交的汇总报告为 `outputs/reports/sun_modality_boundary_v1.{json,md}`。
实时进度只见 `docs/PROJECT_AUDIT.md`，完整路线只见 `docs/MASTER_PIPELINE.md`。
