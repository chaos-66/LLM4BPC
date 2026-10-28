# Sun modality 五方法对比（独立补充实验）

- suite: `SUN-MODALITY-5WAY-001`
- 生成时间（UTC）: `2026-10-28T10:45:12.390919+00:00`
- 数据: `data/development/modality/sun_estg_modality_v1`，固定划分 1985/420/426，seed 20260715，测试集 426 条全部进入统计
- 主指标: 四分类 Macro-F1；同一评价器 `src/bpc_hybrid/modality_benchmark/metrics.py::evaluate`
- EStG-150 主表（S2.10）未被替换，本表为独立补充

## 主表（测试集 426 条）

| 方法 | Accuracy | Macro-P | Macro-R | Macro-F1 | 失败数 | 失败率 | 运行时间(s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| CFKW | 0.6737 | 0.7090 | 0.7118 | 0.6657 | 0 | 0.0000 | 0.28 |
| CFRNN (BiLSTM) | 0.8662 | 0.7747 | 0.7799 | 0.7734 | 0 | 0.0000 | 160.51 |
| CFCNN (CNN) | 0.8756 | 0.8121 | 0.7552 | 0.7646 | 0 | 0.0000 | 29.40 |
| Sun (BERT-TextCNN) | 0.9319 | 0.8753 | 0.8792 | 0.8772 | 0 | 0.0000 | 76.06 |
| LLM-SE | 0.6925 | 0.6486 | 0.7646 | 0.6137 | 2 | 0.0047 | 2520.16 |

注：CFKW 的运行时间是 test 推理耗时；CFRNN/CFCNN 为训练 + 推理；Sun 为 426 条推理；LLM-SE 为 426 次串行真实 API 调用墙钟时间（42 分钟），不与本地算力耗时直接可比。

## 分类别 F1（support 为测试集真值条数）

| 方法 | definition (177) | obligation (195) | permission (39) | prohibition (15) |
|---|---:|---:|---:|---:|
| CFKW | 0.7051 | 0.5848 | 0.8211 | 0.5517 |
| CFRNN (BiLSTM) | 0.8703 | 0.9003 | 0.8046 | 0.5185 |
| CFCNN (CNN) | 0.8876 | 0.9021 | 0.8140 | 0.4545 |
| Sun (BERT-TextCNN) | 0.9322 | 0.9666 | 0.8101 | 0.8000 |
| LLM-SE | 0.4589 | 0.8366 | 0.7525 | 0.4068 |

## 与 Sun 的差值（Macro-F1 百分点，正数表示更高）

| 方法 | Δ Macro-F1 (pp) | Δ Accuracy (pp) |
|---|---:|---:|
| CFKW | -21.1549 | -25.8216 |
| CFRNN (BiLSTM) | -10.3805 | -6.5728 |
| CFCNN (CNN) | -11.2677 | -5.6338 |
| LLM-SE | -26.3545 | -23.9437 |

## LLM-SE 真实调用与费用

- 调用次数: 426（计划 426，无重试）
- 实际费用: ¥9.8428（上限 ¥20.00）
- 返回模型: deepseek-v4-pro
- 解析状态分布: {"ok": 424, "no_clauses": 2}
- 请求状态分布: {"ok": 426}
- 失败样本（保留在分母，未删样本/未猜标签）: 2 / 426（failure_rate=0.0047）
- 未发出调用（计入 `<no_prediction>`，未补标签）: 0
- 价格窗口: off_peak → off_peak
- 请求体对账: ok=True，checked=426，failures=0（记录字段 body_hash_match 全为 false 属记账口径差异，见 `llm_se/body_reconciliation.json`）

## 实现与原论文的差异（必读）

- CFKW / CFRNN / CFCNN 是按论文描述独立复现的：作者未公开代码、词表、词向量表与超参，因此三者只称“独立复现”，从不写成作者原版系统。
- CFKW 的规则优先级与未命中回退类由 dev 划分在 4 个预声明候选中选定，选定结果随该臂一并记录；测试标签未参与选择。
- Sun 是项目自建的 BERT-TextCNN（Legal-BERT base uncased），在同一 train 划分上训练；本表任何位置都没有引用论文报告分数。
- 绑定的 Sun 检查点（候选 B）使用 inverse-sqrt 类别频率加权交叉熵，而 S2.4 基础配置声明的是未加权交叉熵；本表报告的是项目实际绑定的检查点。
- LLM-SE 沿用冻结的 EStG-150 提示词、schema 与采样策略（temperature 0、top_p 1、max_tokens 4096、thinking disabled、无重试），模型 deepseek-v4-pro（DeepSeek-V4-Pro-0813）。
- 冻结的 LLM-SE 提示词原本面向英文 EStG-150 文本，本实验向其输入德语原句，因为所有方法必须看到同一份德语原文；这一语言错配是真实偏差，如实报告且不做修正。
- 冻结提示词输出的是“规则记录（多 clause）”，句级 modality 取记录中第一个带非空标签的 clause，与项目既有评价器 `_pred_modality_label` 的取法一致；这不是直接的句级 modality 判定，是该方法在本任务上的代理口径。
- 失败样本（请求成功但输出无可解析 clause）保留在分母中，既不删除样本也不补猜标签。
- 本表没有使用任何只判断 modality 的提示词；若另写此类提示词，必须单独命名为 “LLM modality-only”，不得标为原论文 LLM-SE。

## 局限

- 426 条测试集是项目重建的确定性划分（seed 20260715），不是 Sun 的原始划分。
- 同一测试集此前已被 S2.4 候选评价（2026-07-22）与 S2.7 对齐核验（2026-08-08）使用过，对 Sun 臂并非“从未触碰”的测试集；所有方法均为单种子、单次运行。
- 官方 modality 数据许可仍为 unknown_pending_confirmation；原文、向量与逐条预测仅保留在本地，不重新分发。
- 每个方法只报告一个种子、一次运行，不做显著性检验，也不声称置信区间。

## 复现命令

```bash
cd formal_experiment
python scripts/run_sun_modality_five_way_v1.py --methods cfkw,cfcnn,cfrnn,sun
python scripts/run_sun_modality_llm_se_v1.py --preflight
python scripts/run_sun_modality_llm_se_v1.py --execute   # off-peak window
python scripts/build_sun_modality_five_way_report_v1.py
```
