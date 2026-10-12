# S3.9-EXT 统一五分类决策重评注记（2026-09-06）

> 2026-09-07：本文保留历史口径。当前修复后结果见 `outputs/reports/s3_formula_repair_v2.md`；原五分类分类 P/R/F1 漏计部分样本，已由新版本取代；旧原始预测不修改。

## 0. 为什么重评

原 S3.9-EXT 运行器生成**违规侧（variant）**预测的方式是：读取面板预置的
`expected_violation`，若该预置类型可观察且违规则输出该类型，否则 None
（`run_s3_extended_violation_panel_v2.run_method`）。因此：
- variant-only 表实际是**“指定类型的条件性检出评价”**，不是自动分类精度；
  P=1、无 wrong-type 不能作为分类能力证据；
- 配对评价中**合规侧（control）**却用四类分数按固定优先级综合（
  `control_prediction_from_scores`）——两侧决策规则不同，不能视为统一五分类。

修复：**两侧统一使用同一确定性决策**（固定 EXTENDED_TYPES 优先级；不可观察类型
跳过；prohibited `score>=gamma_ext`、condition/constraint/exception
`score>gamma_ext` 或精确时限矛盾；所有类型不可观察 → None；无可观察违规 → none）。
决策函数不读 `expected_violation`/Gold/样本 ID；Gold 只在预测固定后进入评价。
全部基于**已保存**的 scores/scores_detail/observability/control_scores 离线重算，
不重跑 Stage 2、不调用 LLM、不修改任何旧产物。

产物：
- `outputs/development/s3_extended_unified_v1/{reference,rules_only}/<method>/`
  （逐样本统一预测 predictions.jsonl（旧条件预测保留为
  `predicted_conditional_old`）、evaluation_variant_only.json、
  paired_evaluation.json、confusion_matrix.json、old_vs_new.json、manifest.json）
- `outputs/reports/s3_extended_unified_v1_{reference,rules_only}.{json,md}`
- 重跑脚本 `scripts/reevaluate_s3_extended_unified_v1.py`
  （`--source reference|rules_only`）

旧结果与 manifest 一律保留；旧数字仅在注记/备用材料中按“条件性检出”引用。

## 1. 统一口径下 variant-only（40 变体，4 类，unobservable/无违规一律计入分母）

| method | macro-F1 | exact | wrong-type | unobservable | 参考抽取 | Sun 臂 |
|---|---|---:|---:|---:|---|---:|
| winter | 参考 | 0.4989 | 0.450 | 9 | 17 | — |
| winter | Sun | 0.3313 | 0.275 | **10** | 23 | — |
| sun | 参考 | 0.3214 | 0.300 | 1 | 28 | — |
| sun | Sun | 0.1875 | 0.150 | 0 | 32 | — |
| bm25 | 参考 | 0.2262 | 0.150 | 0 | 28 | — |
| bm25 | Sun | 0.0000 | 0.000 | 0 | 32 | — |
| tfidf_svd | 参考 | 0.3750 | 0.325 | 1 | 27 | — |
| tfidf_svd | Sun | 0.3321 | 0.275 | **6** | 28 | — |

逐类型（variant-only，统一口径，P/R/F1）：
- 参考 winter：prohibited 0.91/1.00/**0.95**；condition 0.29/0.20/0.24；
  constraint 0.67/0.40/0.50；exception 0.67/0.20/0.31。
- Sun winter：prohibited 1.00/0.60/**0.75**；condition 0.25/0.20/0.22；
  constraint 0.43/0.30/0.35；exception 0/0/0。
- Sun tfidf：prohibited 1.00/0.80/**0.89**；constraint 0.50/0.20/0.29；
  exception 0.33/0.10/0.15；condition 0。
- 其余方法类型值见报告 JSON。

## 2. 统一口径下配对（40 合规对照 + 40 变体 = 80）

| method | 5-class acc（参考→Sun） | control FP（参考→Sun） | none 类 F1（参考→Sun） |
|---|---|---|---|
| winter | 0.375 → 0.2625 | **0.500 → 0.450** | 0.545 → 0.526 |
| sun | 0.2625 → 0.20 | 0.125 → 0.050 | 0.783 → 0.909 |
| bm25 | 0.250 → 0.15 | 0.000 → 0.000 | 1.000 → 1.000 |
| tfidf_svd | 0.3375 → 0.2625 | **0.275 → 0.375** | 0.718 → 0.571 |

predicted-None 明细（Sun）：对照侧 none_gold 12/28/28/15（winter/sun/bm25/
tfidf，即未误报但未判合规），违规侧 19/34/40/23 条未判出类型（其中
“可观察合规判定”（违规变体被判 none）6/6/12/5 条、全不可观察其余）。

## 3. 旧口径 vs 新口径差异（结论保留/撤回）

| 原结论 | 状态 |
|---|---|
| 参考抽取 winter variant macro 0.655 / exact 0.550 | 保留为**条件性检出**数字；分类口径下为 0.4989/0.450 |
| Sun winter variant macro 0.5208/exact 0.375 | 条件性检出口径保留；分类口径 0.3313/0.275 |
| “检出列 P=1.0、无 wrong-type” | **撤回**：统一决策下 reference winter wrong-type=9、Sun winter=10、tfidf=6；逐类型 P 见 §1（不再有全局 P=1 断言） |
| “合规对照误报率未上升”（winter 0.50→0.45、sun 0.125→0.05、bm25 0→0 是事实，但 tfidf 0.275→0.375） | **部分撤回**：tfidf 的 Sun 合规误报率较参考**上升 0.10**；“误报率未上升”不可再整体表述，按方法分列 |
| 五类配对 5-class acc：reference 0.425/0.2625/0.25/0.3375（与储存一致，旧口径自检通过）；Sun 0.3125/0.2/0.15/0.2625 | 旧的 paired 数字=旧口径；统一口径数字见 §2 |
| 案例 a（article22 s1）：“参考判 prohibition、Sun 判 obligation → 禁止类检查不可观察” | 措辞改为**中性**：两种方法的情态标签不同并改变下游可检性；未经人工裁决不得认定参考正确 / Sun 错误 |
| “四类扩展检出可行性：prohibited 最易” | 分类口径下仍成立（prohibited F1 在 unified 下仍最高或并列最高） |

自检：统一脚本重算的旧 paired 5-class 与已存储报告逐方法一致（reference：
0.425/0.2625/0.25/0.3375；rules_only：0.3125/0.2/0.15/0.2625），证明评价器与
持久化行一致，差异只来自决策规则。

## 4. 边界与归因限制

- 全部为 DEV_ONLY 受控合成面板（40 变体 + 40 对照）；非人工 Gold、非正式 Oracle；
  不与 33 条人工违规 Gold 合并。
- 参考确定性抽取不是人工 Gold。
- Sun 为英文 GDPR 句经德语合同 classifier 槽的 **pass-through（跨语言适用
  限制）**——下游差异不得一概归因于“LLM 方法创新”或“参考方法优越”。
- first-valid-span 投影只取每字段第一个有效 span（其余片段仅入 diagnostics），
  属**衔接适配规则**；下游损失不能全部归因于原始抽取方法。
- 合规/违规两侧同一决策函数（`s3_extended_unified.unified_prediction` →
  `control_prediction_from_scores`），统一规则先于评价；验证测试保证仅改 Gold 不
  改预测、失败/不可观察样本计入分母。
