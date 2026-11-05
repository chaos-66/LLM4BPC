# 资格条件与有限许可的两对训练示例

本分支以 reviewer 的实际 system prompt 为前缀，末尾追加第 19 至 22 条真实德语训练例句和各自的原始句级类别。训练集原文在本地按 ID 恢复。运行以下命令可生成完整提示词和新增示例块。

```powershell
python formal_experiment/scripts/prepare_sun_modality_eligibility_shots_v1.py
```

完整文本在 `outputs/development/sun_modality_eligibility_shots_v1/composed_system_prompt.txt`，追加部分在同目录的 `added_examples.txt`。版本化的 [选例清单](selection_manifest.json) 记录编号、标签、文本哈希和选择理由。

此前归为资格、数量、期限与规范边界的 17 条旧测试错误，reviewer 版改对 1 条。因此本次只增加这一组边界的示例。选例时在 1,985 条 train 中按资格限制、申请和选择等表达阅读训练候选，人工式挑选由 Codex 完成。两对中双方都有条件，一侧强调适用资格，另一侧强调主体可行使的选择。编号在隔离核查前固定。

| 训练示例 | 资格条件（definition） | 有条件的选择（permission） |
|---|---|---|
| 19 / 20 | 变更会计年度须有经营理由及税务机关事先同意 | 欠缴条件成立时税务机关可以申请除名 |
| 21 / 22 | 计提准备金须有具体事实支持 | 满足补税条件时可以在两种方式间选择 |

原 18 条沿用冻结选择器的训练成员及规范化文本核验。新增 4 条逐一复核训练标签及文本哈希，再与 dev 420 条、test 426 条进行 ID、规范化文本及近重复检查。近重复按词序匹配比 ≥0.80、字符匹配比 ≥0.88、或至少 8 词的较短句有 ≥85% 连续出现来拒绝。命中时准备程序停止。该检查覆盖词面近似，所用 dev/test 接口仅返回 ID 和文本。教学主题参考过此前的错误诊断，后续在这两份划分上取得的成绩应按探索性回归解读。

本次交付离线 prompt。新版本的效果待测。将来对比可先检查 definition 被判作 permission 的数量及反向误判，同时报告总体改对与改错。
