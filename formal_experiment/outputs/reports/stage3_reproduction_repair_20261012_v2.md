# Part 3 基线修复后的同批真实对照

115 个 BPMN、33 条法规；参数及参考判断固定。Sun 修复范围边界及部分抽取，LLM-SE 复用原抽取并重新检查；Winter 使用本轮已完成的完整重跑。
本报告是局部修复开发实验，不认证完整 Sun/Winter 原论文复现。

| 方法 | 201 单元 P | R | F1 | 207 单元诊断 F1 |
|---|---:|---:|---:|---:|
| LLM-SE | 0.4393 | 0.6812 | 0.5341 | 0.5281 |
| Sun 局部修复重建 | 0.4023 | 0.5072 | 0.4487 | 0.4430 |
| Winter 节点修复重建 | 0.4634 | 0.5507 | 0.5033 | 0.4903 |

预期 LLM-SE > Sun > Winter 是否成立：False。所有结果保留，不作为挑选样本或修改参数的依据。

剩余复现差异：

- modality and segmentation reused from local v10a; classifier-first correct-language reconstruction unresolved
- author final weights and complete extraction rules unavailable
- maximal nonnested VPs and temporal with-complement disambiguation are disclosed reconstruction choices
- process label decomposition is unchanged and remains a separate prospective repair
- native spaCy 3.8.13 / model 3.8.0 instead of prototype 2.3.0
- previously disclosed reachability/Flow lemma repairs retained
