# 语料模态 few-shot 提示词分支

任务 `SUN-MODALITY-FEWSHOT-001`：在 boundary 分支末尾追加 18 条来自
train 的德语句子及其模态标签，用示例传递该语料的分类边界。

```text
system = frozen v6 system + boundary guidance + corpus demonstrations
user   = 原用户模板、原六个合成示例、待抽取句子
```

本分支继续完成六要素抽取，使用原 JSON 合同和首个有效 clause 模态取值口径。
示范块的说明专门防止模型把任务改成只输出一个类别。模型、采样和输入保持原样。

示例配额：definition 7、obligation 5、prohibition 3、permission 3。
选择沿用已审阅的本地草案：按固定语义家族分层，层内以词数（至少六词）、
sample_id 排序，按配额选择，并以固定的相邻对比顺序展示。
典型对比包括明确适用/不适用、条件性豁免、类别否定与受限许可。

`selection_manifest.json` 版本化规则、顺序、样本编号、标签及文本哈希；
`demonstration_header.md` 是新增块的说明。运行时仅从已校验哈希的本地 train
恢复示例；dev/test 只用于文本与编号隔离检查，不使用其标签选例。
原始德语句子、拼接后的完整 prompt 只保存在被忽略的本地目录。

离线准备命令（无网络、无凭据读取、无 API 执行入口）：

```powershell
python formal_experiment/scripts/prepare_sun_modality_fewshot_v1.py
```

生成：

- `outputs/development/sun_modality_fewshot_v1/prepared_v1/fewshot_block.txt`
- `outputs/development/sun_modality_fewshot_v1/prepared_v1/composed_system_prompt.txt`
- `outputs/reports/sun_modality_fewshot_v1_preflight.json`（不含原句）

对全部 426 个测试输入检查唯一差异是 system 末尾新增示范块，绑定每条请求的
哈希，保留原六例、用户模板、抽取结构及采样参数。输入 token 增量仅用 UTF-8
字节启发式估算，不是分词器测量或费用保证。

后续若运行，主要比较 boundary + few-shot 与已有 boundary 的预测；观察
macro-F1、逐类 P/R/F1、混淆矩阵与改对/改错，尤其关注 definition 漏判及
prohibition 误报。当前准备脚本不执行推理，也不生成性能分数。
新的 426 次/¥20 只是计划上限，需独立的执行授权、当时价格核验和运行账本；
旧 boundary 批次授权不覆盖本分支。

选例家族参考过测试错误，因此仍是 test-informed 探索性分支。训练句与测试句
不重叠不等于独立盲测，也不能把结果预称为上界。18 个训练标签通过上下文提供，
未做参数训练；历史对照仍存在模型服务时间差。提升与副作用均须实际实验验证。

当前状态只见 `docs/PROJECT_AUDIT.md`；完整路线只见 `docs/MASTER_PIPELINE.md`。
