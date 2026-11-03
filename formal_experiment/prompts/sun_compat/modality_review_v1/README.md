# 人工审读步骤提示词分支

任务 `SUN-MODALITY-REVIEW-001`。用户要求逐条分析 few-shot 剩余错误，并把
“如果仔细人工阅读，会怎样避免误判”的步骤写入 prompt。
这里的审读意见由AI提出，不是新增人工金标或已经验证的模型效果。

组合：既定 v6 + boundary + 原18条train示范 + `reviewer_guidance.md`。
原示范、模型、采样、用户模板、输出合同和评价器保持原版本；只追加审读指导。
三组短英文对比为本次合成，不是从测试集抽出的示例。

重点检查：条件与主句、法律后果与行为指令、否定作用域、资格/数量与选择权、
并列谓词与句尾约束、残缺输入及不确定性。它是文字指导，不是运行时规则分类器。
真实train示例仍由原few-shot模块从本地恢复，德语原文不进入版本库。

逐条分析的事实和假设分开：混淆矩阵、后续clause中的标签是程序核验的事实；
错误家族、阅读解释、建议修改是AI审读假设，尚未经独立人工裁决或新API验证。
示例家族和新指导均参考测试错误，本分支明确为test-informed探索性。

特别保留的限制：若独立命题分别属于不同类别，而评价只取第一个clause，
提示词不能通过倒序、删除或统一标签来“修复”分数。真正缺少上下文的片段与
近似措辞的跨类标注，也不能靠无条件补写或猜标签消除。本分支不改Gold和评价口径。

离线入口：

```powershell
python formal_experiment/scripts/analyze_sun_modality_review_v1.py
python formal_experiment/scripts/prepare_sun_modality_review_v1.py
```

分析报告：`outputs/reports/sun_modality_review_v1.{json,md}`。
准备报告：`outputs/reports/sun_modality_review_v1_preflight.json`。
完整新prompt与原句审读材料仅存于被忽略的
`outputs/development/sun_modality_review_v1/`。
本分支没有API执行入口或新费用授权；没有性能分数。
