# Sun modality 五方法对比：独立补充实验（SUN-MODALITY-5WAY-001）

**状态**：本地四臂已完成；LLM-SE 真实调用按本轮授权执行中，结果以
`outputs/reports/sun_modality_five_way_v1.json` 为准。
**日期**：2026-10-28
**定位**：本实验是 S2.4 / EXP-S2A 的独立补充，**不替换** EStG-150 的 S2.10
正式主表，也**不把** Sun 论文中报告的分数放进我们的结果表。
**预注册配置**：`configs/supplement/sun_modality_five_way_v1.json`

---

## 1. 研究问题与范围

比较同一批德语句子上的四类情态（定义 definition / 义务 obligation / 允许
permission / 禁止 prohibition）句子级分类能力：

| 臂 | 方法 | 来源 |
|---|---|---|
| CFKW | 德语关键词规则，显式优先级与未命中处理 | 依据论文描述独立复现，非作者原版 |
| CFRNN | BiLSTM 句子分类器 | 依据论文描述独立复现，非作者原版 |
| CFCNN | CNN 句子分类器 | 依据论文描述独立复现，非作者原版 |
| Sun | BERT-TextCNN（Legal-BERT base uncased） | 复用本仓已训练权重推理 |
| LLM-SE | 冻结六要素提示词，取记录中的 modality 标签 | 复用论文冻结提示词与采样策略 |

明确不在范围：情态词/触发词抽取、EStG-150 Part 2 重跑、Sun 原始划分复现。
本实验**没有**新增只判断 modality 的提示词；若将来新增，必须单独命名为
“LLM modality-only”，不能标为原论文 LLM-SE。

## 2. 数据与划分

- 官方 `EStG_sent_vec.csv`：2833 句；项目按预注册隔离规则剔除 1 个文本相同但
  标签冲突的 group（2 行），主分析population 为 2831 句。
- 固定划分由 normalized-text group-aware 分配器在 seed **20260715** 下生成：
  train 1985 / dev 420 / test 426，跨 split 文本泄漏 0。
- 这是**项目重建划分**（`project_reconstructed_deterministic_group_aware_split`），
  **不是** Sun 原始划分；不得重新随机划分。
- SHA-256（构建时逐一核验，见报告 `dataset.splits`）：
  - train `a7367cd3…3b142`（1985）
  - dev `ad541915…5a8d6`（420）
  - test `2f67edad…9e871`（426）
- 测试集类别分布：definition 177 / obligation 195 / permission 39 / prohibition 15。
- 原始德文句子、向量与逐条预测只保存在本地（Git 忽略），不随仓库分发。
  官方数据许可仍为 `unknown_pending_confirmation`。

## 3. 评价协议

- 评价器唯一：`src/bpc_hybrid/modality_benchmark/metrics.py::evaluate`。
- 指标：Accuracy、宏平均 Precision/Recall/F1、分类别 P/R/F1 与 support、
  混淆矩阵、失败率、运行时间。
- **426 条全部进入统计**。失败（解析失败 / API 失败 / 无 clause）记为“无预测”：
  保留在分母，降低 accuracy 与该类 recall，不产生任何类的假阳性；不删除样本、
  不猜标签、不补正。覆盖率受限的次指标单独标注，绝不作为主表数字。
- 选择只用 dev：CFKW 的优先级/回退配置、两个神经基线的早停轮次均由 dev
  macro-F1 决定；测试集只在配置冻结后评价一次。
- 单种子（20260717），不做超参搜索，不做重复运行。

## 4. 结果（测试集 426 条）

以 `outputs/reports/sun_modality_five_way_v1.json` 为唯一数值来源。

| 方法 | Accuracy | Macro-P | Macro-R | Macro-F1 | 失败数 | 耗时(s) |
|---|---:|---:|---:|---:|---:|---:|
| CFKW | 0.6737 | 0.7090 | 0.7118 | 0.6657 | 0 | 0.3 |
| CFRNN (BiLSTM) | 0.8662 | 0.7747 | 0.7799 | 0.7734 | 0 | 160.5 |
| CFCNN (CNN) | 0.8756 | 0.8121 | 0.7552 | 0.7646 | 0 | 29.4 |
| Sun (BERT-TextCNN) | 0.9319 | 0.8753 | 0.8792 | 0.8772 | 0 | 76.1 |
| LLM-SE | 见报告 | 见报告 | 见报告 | 见报告 | 见报告 | 见报告 |

分类别 F1：

| 方法 | definition | obligation | permission | prohibition |
|---|---:|---:|---:|---:|
| CFKW | 0.7051 | 0.5848 | 0.8211 | 0.5517 |
| CFRNN | 0.8703 | 0.9003 | 0.8046 | 0.5185 |
| CFCNN | 0.8876 | 0.9021 | 0.8140 | 0.4545 |
| Sun | 0.9322 | 0.9666 | 0.8101 | 0.8000 |
| LLM-SE | 见报告 | 见报告 | 见报告 | 见报告 |

可观察到的现象（描述性，不做显著性主张）：

1. 关键词规则在 definition 上靠“默认类”取得表面召回，代价是把 109 条真实
   obligation 判成 definition；obligation F1 仅 0.58。这是关键词规则的典型
   失败模式，也解释了它为何显著低于三类神经网络方法。
2. 两个从零训练的神经基线在 dev 上接近（0.8419 / 0.8416），测试集上
   BiLSTM 的 Macro-F1 略高于 CNN（0.7734 vs 0.7646），但 CNN 的 accuracy
   更高（0.8756 vs 0.8662），差异集中在 prohibition 这个 15 条的小类。
3. 预训练 Legal-BERT 的 BERT-TextCNN 在四类上都更强，prohibition F1 0.80，
   明显高于两个从零训练基线（0.52 / 0.45），与“预训练语言模型在德语法律
   小样本分类上占优”的预期一致。
4. 三方法在 permission 上差距不大（0.80–0.82），主要差距来自 prohibition 与
   obligation。

## 5. 与论文/作者实现的差异（必读）

### 5.1 CFKW / CFRNN / CFCNN

论文只给出方法类别与相对结论，**没有**公开作者代码、词典、词向量表或完整超参。
本实验按论文描述独立实现，缺失细节与自定参数如下：

| 项目 | 论文是否有 | 本实验取值 |
|---|---|---|
| CFKW 关键词表 | 无 | 由本实验按德语法条用语编写（见 `cfkw.py` 的 `CUES`） |
| CFKW 优先级 / 未命中处理 | 无 | 4 个预声明候选，dev 选定 `prohibition > permission > obligation > definition`，未命中回落 definition |
| 否定作用域 | 无 | 情态词后 4 个 token 内出现否定词 → prohibition |
| 词向量 | 无 | 从训练集自训练，embedding 128，min_freq 2，词表 2537 |
| BiLSTM | 无 | 单层双向，hidden 128，mean+max 池化，dropout 0.3 |
| CNN | 无 | 卷积核 2/3/4，各 128 filter，global max，dropout 0.3 |
| 训练 | 无 | Adam，lr 2e-3，batch 32，最多 25 epoch，dev macro-F1 早停（patience 4） |
| 类别权重 | 无 | 不加权交叉熵（与 S2.4 基础配置一致，便于对照） |

因此这三行只能称为**独立复现**，不能写成作者原版系统，也不能把差异归因于
“论文方法本身更差”。

### 5.2 Sun

- 使用 `configs/models/sun_bert_textcnn_s24.json`（formal 版 BERT-TextCNN，
  Legal-BERT base uncased，卷积核 2/3/4 × 128）与 S2.6 绑定的候选 B 检查点
  `s24_candidate_B_invsqrt_weighted_seed20260717_v1/best_model.pt`。
- 该检查点在 train（1985）上训练、dev 选轮（best epoch 5/7），**未重新训练**。
- 与 S2.4 基础配置的差异：候选 B 使用 **inverse-sqrt 类别频率加权交叉熵**
  （类别权重 definition 0.535 / obligation 0.518 / permission 1.137 /
  prohibition 1.810），基础配置声明的是未加权交叉熵。本表按项目实际绑定的
  检查点报告，并在报告 `implementation_difference` 中注明。
- 复现校验：本次推理得到 Macro-F1 0.8772277372431857，与已记录测试指标
  完全一致（差值 < 1e-9），否则脚本 fail closed。

### 5.3 LLM-SE

- 提示词、schema、采样策略沿用冻结配置：
  `direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md`
  （SHA-256 `3aa64877…0ede895`）、temperature 0、top_p 1、max_tokens 4096、
  thinking disabled、无重试、每个测试样本最多一次请求。
- 模型：`deepseek-v4-pro`（官方文档对应发布版 DeepSeek-V4-Pro-0813），
  调用前核对官方价格页；不可用时如实报告，不擅自换模型。
- **语言偏差**：该冻结提示词是为 EStG-150 的英文文本编写的，本轮按“所有方法
  使用相同德语原文”的要求直接输入德语原句。这是真实偏差，如实报告，不修改
  提示词、不做翻译后再输入。
- modality 标签取自记录中第一个带非空标签的 clause，与项目评价器
  `_pred_modality_label` 的取法一致，未引入新的聚合规则。

## 6. 费用与预算

- 硬上限 ¥20.00，含预检与失败请求；最多 426 次真实调用。
- 每次发送前按“估算输入 token + 预留 1200 输出 token”预留费用，累计
  （已花费 + 在途预留）超过上限即停止，不自动重试。
- 价格按官方人民币表（2026-10-28 核实）：高峰 输入 9.0 / 输出 27.0 元每百万
  token；空闲 4.5 / 13.5。高峰时段为北京时间工作日 9:00–12:00、14:00–18:00。
- 离线预检：426 次调用，平均估算输入 5830 token；空闲时段预留合计 ¥18.08
  （预计实际约 ¥15.29），高峰时段预留合计 ¥36.16 —— 因此本轮**只在空闲时段
  执行**，以满足 ¥20 上限；高峰不执行，也不通过删样本或改提示词凑预算。
- 实际调用次数与实际费用见报告 `llm_budget`。

## 7. 局限

1. 426 条测试集是项目重建划分，不是 Sun 原始划分。
2. 该测试集此前已被 S2.4 候选评价（2026-07-22）与 S2.7 对齐核验（2026-08-08）
   使用过，对 Sun 臂不是“从未触碰”的测试集；本表所有结果均按此披露。
3. 单种子、单次运行，无重复实验、无显著性检验、无置信区间。
4. CFKW/CFRNN/CFCNN 为独立复现，超参由本实验确定，绝对分数不能当作论文数值复刻。
5. 官方数据许可未知，只在本地使用；逐条结果与原文不进入仓库。
6. LLM-SE 的提示词语言（英文指令）与输入语言（德语）不一致，可能低估该方法
   在德语上的真实能力；本轮不通过改提示词或翻译来修正这一偏差。

## 8. 复现

```bash
cd formal_experiment

# 1) 本地四臂（CFKW / CNN / BiLSTM / Sun 推理），约 4–5 分钟（CPU）
python scripts/run_sun_modality_five_way_v1.py --methods cfkw,cfcnn,cfrnn,sun

# 2) LLM-SE 离线预检（零网络、零费用）
python scripts/run_sun_modality_llm_se_v1.py --preflight

# 3) LLM-SE 真实调用（空闲时段；硬上限 ¥20，无重试，每样本一次）
python scripts/run_sun_modality_llm_se_v1.py --execute

# 4) 汇总报告（重算全部指标）
python scripts/build_sun_modality_five_way_report_v1.py
```

针对性测试：

```bash
python -m pytest tests/test_modality_five_way_v1.py -q
```

## 9. 产物索引

| 路径 | 内容 | 是否入库 |
|---|---|---|
| `outputs/reports/sun_modality_five_way_v1.json` | 聚合报告（唯一数值来源） | 是 |
| `outputs/reports/sun_modality_five_way_v1.md` | 对比表 | 是 |
| `outputs/development/s28_sun_modality_five_way_v1/` | 各臂配置、历史、逐条预测、LLM 账本 | 否（本地） |
| `configs/supplement/sun_modality_five_way_v1.json` | 预注册配置 | 是 |
| `src/bpc_hybrid/modality_benchmark/` | 评价器、数据绑定、CFKW、神经基线、LLM-SE 支撑 | 是 |
| `scripts/run_sun_modality_five_way_v1.py` | 本地四臂运行器 | 是 |
| `scripts/run_sun_modality_llm_se_v1.py` | LLM-SE 预检 / 执行 | 是 |
| `scripts/build_sun_modality_five_way_report_v1.py` | 报告生成器 | 是 |
| `tests/test_modality_five_way_v1.py` | 针对性测试 | 是 |
