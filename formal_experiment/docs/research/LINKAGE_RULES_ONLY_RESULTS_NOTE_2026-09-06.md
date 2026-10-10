# GDPR Stage-2→Stage-3 衔接结果注记：Rules-Only 臂（2026-09-06）

> ⚠ **2026-09-06 统一口径修正（本注记下方的数字/结论须以本修正为准）**：原运行器
> 的违规侧预测是“预置类型或 None”的**条件性检出**（读取 expected_violation），不是
> 分类。已用合规/违规**同一确定性五分类决策**离线重评（复用已保存分数，不读
> expected/Gold；旧结果与 manifest 保留）。统一口径结果见
> `docs/research/S3_EXT_UNIFIED_EVALUATION_NOTE_2026-09-06.md` 与
> `outputs/reports/s3_extended_unified_v1_rules_only.{json,md}`。下列修正逐条覆盖：
> 1. variant macro 条件口径→分类口径：winter 0.5208→**0.3313**、sun 0.1875（不变）、
>    bm25 0（不变）、tfidf 0.3510→**0.3321**；wrong-type 从 0 变为 winter **10**、
>    tfidf **6**——**“P=1、无 wrong-type”撤回**。
> 2. 合规误报率按方法分列：winter 0.500→0.450（降）、sun 0.125→0.050（降）、bm25
>    0→0、**tfidf 0.275→0.375（升 0.10）**——“误报率未上升”整体表述**撤回**。
> 3. 配对 5-class acc（条件口径→分类口径）：winter 0.3125→**0.2625**、sun 0.2→0.2、
>    bm25 0.15→0.15、tfidf 0.2625→0.2625；control FP 同第 2 条。
> 4. 案例 a 措辞中性化：参考确定性抽取判 article22 s1 prohibition、Rules-Only 判
>    obligation——**两者情态标签不同并改变下游可检性**；无人工裁决不得认定谁正确。
> 5. 归因限制：Rules-Only 为英文 GDPR 句经德语合同 classifier 槽的 pass-through
>    （跨语言适用限制）；first-valid-span 投影是衔接适配规则，逐字段只取第一个有效
>    span——下游差异不能全部归因于原始抽取方法本身。
> 6. 参考确定性抽取不是人工 Gold；33 条人工 Gold、40 对合成面板、正式 Oracle 分表。
> 7. 统一口径下逐样本变化（Rules-Only vs 参考，同一决策规则）：winter **10**/40、
>    sun **7**/40、bm25 **8**/40、tfidf **6**/40（winter 含 2×prohibited→condition、
>    3×prohibited→none、2×exception→constraint、1×constraint→None、1×condition→none、
>    1×exception→None；tfidf 含 **2×None→constraint 新检出**、1×none→constraint、
>    2×prohibited→condition、1×constraint→exception）；旧条件口径 7/6/6/4 仅作备用。
> 统一口径逐类型/逐方法 P/R/F1、混淆矩阵与 old_vs_new 明细见统一注记与报告 JSON。

> 本注记解释真实运行产物，不替代报告文件。机器可读结果：
> `outputs/reports/gdpr_s2_s3_linkage_v1_rules_only.{json,md}`；
> 逐方法行级产物：
> `outputs/development/gdpr_s2_s3_linkage_v1_rules_only/<method>/{predictions.jsonl,
> evaluation.json,paired_evaluation.json,substitution_changes.json,manifest.json}`。
> 全部 development-only、零 LLM/API。

## 1. 实验链（每步都有产物）

| 步骤 | 输入 | 处理 | 产物 |
|---|---|---|---|
| GDPR Stage-2 输入 | 冻结 inference pack 的 9 段 GDPR 条款（article6/7/15/16/17/20/22/33/34，`data/development/human_review/stage3_gold_inference_v1.json`，sha256 4182c1f6…） | 与 S3.9-EXT 面板锁定绑定完全一致的分句（spaCy en_core_web_sm；已对 40 个变体绑定逐条验证 0 失配） | `data/input/gdpr7_stage2_input_v1.json`：9 规则 / **74 句**（article33:10, article34:7, article15:13, article17:13, article7:8, article6:10, article22:6, article20:5, article16:2），Gold-blind，sha256 558b8013… |
| Rules-Only 真实预测 | 上述 74 句 | 锁定 B0 v10a（`estg150_b0_development_v10.run_b0_batch_v10`，与 S2.12 零 API 臂同一方法/配方/模型权重；英文句经德语合同 classifier 槽 pass-through——披露限制） | `data/predictions/gdpr7_sun_rule_only_v1/`：74/74 ok、82 clauses、0 空输出、0 失败；clause 情态标签 obligation 47 / prohibition 18 / definition 9 / permission 8；耗时 1459 s（CoreNLP per-file JVM），零 API |
| Stage-3 消费外部预测 | 上面 74 句预测 + 冻结 40 变体面板（`synthetic_controlled_error_extension_v2.json`）+ 面板自带 control/variant BPMN | 与原始 S3.9-EXT 运行器**同一**后端（Winter-style/Sun-style/BM25/TF-IDF-SVD）、同一 scorer 公式、gamma_ext=0.5、同一 per-method action gamma（winter 0.4/sun 0.8/bm25 0.5/tfidf 0.5，与既有运行 manifest 一致）；每变体绑定句的六要素记录改由外部预测经 first-valid-span 投影生成；失败/缺失一律记为显式原因，**绝不回填**面板锁定抽取 | `gdpr_s2_s3_linkage_v1_rules_only/` 四方法行级产物 + 汇总报告 |

复现命令：

```powershell
python formal_experiment/scripts/build_gdpr7_stage2_input_v1.py          # 已生成（no-overwrite）
python formal_experiment/scripts/run_gdpr7_sun_rule_only_v1.py --runtime-home D:/environment/stanford-corenlp-4.5.10 --device cpu   # 已运行（no-overwrite）
python formal_experiment/scripts/run_gdpr_s2_s3_linkage_v1.py --arm rules_only --overwrite   # 重放（覆盖派生报告）
```

## 2. 结果（Rules-Only 臂；参考行 = 既有确定性抽取面板运行，仅作上下文）

40 变体 variant-only + 80 对象配对（40 对照 Gold=none + 40 变体）：

| method | arm variant macro | arm exact | arm unobs | arm control FP | arm paired acc | 参考 macro | 参考 exact | 参考 unobs | 参考 control FP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| winter | 0.5208 | 0.3750 | 23 | 0.4500 | 0.1500 | 0.655 | 0.550 | 17 | 0.500 |
| sun | 0.1875 | 0.1500 | 32 | 0.0500 | 0.1500 | 0.333 | 0.300 | 28 | 0.125 |
| bm25 | 0.0000 | 0.0000 | 32 | 0.0000 | 0.0000 | 0.226 | 0.150 | 28 | 0.000 |
| tfidf_svd | 0.3510 | 0.2750 | 28 | 0.3750 | 0.2250 | 0.379 | 0.325 | 27 | 0.275 |

逐类型（arm，variant-only，P/R/F1 + 检出支持）：

| type | winter | sun | bm25 | tfidf_svd |
|---|---:|---:|---:|---:|
| prohibited_action_present (10) | 1.000/0.600/0.750 | 1.000/0.600/0.750 | 0/0/0 | 1.000/0.800/0.889 |
| required_condition_not_enforced (10) | 1.000/0.200/0.333 | 0/0/0 | 0/0/0 | 0/0/0 |
| constraint_violated (10) | 1.000/0.500/0.667 | 0/0/0 | 0/0/0 | 1.000/0.200/0.333 |
| exception_not_handled (10) | 1.000/0.200/0.333 | 0/0/0 | 0/0/0 | 1.000/0.100/0.182 |

unobservable 原因（arm；四方法合计 115 个不可观察中的主因）：`action_mapping_below_gamma` 74、`empty_rule_exception` 20（5 个例外变体 ×4 方法，绑定句为 article20 s2、article34 s3/s4）、`rule_modality_not_prohibition` 8（article22 s1 的 2 个变体 ×4 方法）、`empty_rule_condition` 4、`empty_rule_constraint` 4、`no_condition_candidates` 5。

## 3. 与参考确定性抽取的逐样本变化（同一检测器，只换 Stage-2 规则记录）

| method | 相同 | 改变 | 主要变化 |
|---|---:|---:|---|
| winter | 33/40 | 7 | 4×禁止检出丢失（→None）、2×constraint 丢失、1×exception 丢失 |
| sun | 34/40 | 6 | 4×禁止丢失、2×constraint 丢失 |
| bm25 | 34/40 | 6 | 同上（其禁止类基线本就受后端刻度限制） |
| tfidf_svd | 36/40 | 4 | 2×禁止丢失、1×constraint 丢失、**1 个新检出**（见案例 b） |

**案例 a（情态标签替换效应）**：变体 syn_v2_prohibited_action_01/02 绑定 article22 第 1 句（“The data subject shall have the right **not to be** subject to a decision based solely on automated processing…”）。参考确定性抽取判该句 modality=prohibition；Rules-Only（B0 v10a，英语经德语合同 classifier 槽的 pass-through）整句单 clause 判 **obligation**（clause 长度 226）→ 禁止动作检查以 `rule_modality_not_prohibition` 不可观察。4 个方法 ×2 变体 = 8 个不可观察全部由此而来：**Stage 2 情态标签错误在 Stage 3 直接表现为“该查的违规不再可查”**。

**案例 b（替换反而恢复可观察性）**：变体 syn_v2_constraint_violated_04（gdpr_1_data_breach × article34）在参考抽取的 action 文本下 tfidf action 相似度 <0.5（`action_mapping_below_gamma`，不可观察）；换成 Rules-Only 预测的 action span 文本后 action 可映射，约束检查恢复可观察并正确检出 `constraint_violated`（参考→臂 = None→检出）。**替换 Stage-2 的效应方向不唯一**。

**案例 c（字段缺失效应）**：3 个例外类绑定句（article20 s2、article34 s3/s4；覆盖 5 个例外变体）的 Rules-Only 预测没有 exception span（82 个 clause 只有 15 个 exception spans）→ `empty_rule_exception` 不可观察 20 个；例外类检出在替换后主要死于规则侧字段为空，而非检测公式。

## 4. 结论与边界（本臂可支持的说法）

1. “只替换 Stage 2（同一法规文本、同一流程模型、同一 Stage 3 检测器与阈值）会真实改变最终违规判断”已获得**可直接运行复现**的证据，且效应以**检出下降为主**（Rules-Only 预测的字段覆盖与情态标签不同于参考确定性抽取），同时也有恢复可观察性的反向案例——效应方向不唯一。
2. 检出的**精度保持高**：所有被检出的类型列 P=1.0，没有任何 wrong-type 预测；下降主要来自不可观察（空规则字段/动作映射/情态不符）而非误报。合规对照误报率未上升（winter 0.45 vs 参考 0.50 等）。
3. 边界：① 本臂是 Rules-Only（B0 v10a）在英文 GDPR 句上的**描述性 pass-through**（德语合同 classifier），情态类结论受此限制；② 评价载体是 40 对**受控合成**样本（DEV_ONLY），不是人工 Gold、不是 formal Oracle，不得与 33 条人工 Gold 合并；③ “参考确定性抽取”不是 Stage-2 方法臂，仅作上下文；④ LLM-SE 臂的真实调用尚未授权（输入与 74 个冻结请求已备，见授权申请）；⑤ 未修改任何冻结 BPMN/面板/阈值/Gold。
4. 可写进论文的表述建议：本结果支持“Stage 2 预测质量（字段覆盖、情态标签）向下游违规检测传播，替换抽取方法会改变检测结论（此受控设置下以漏检为主、无误报上升）”这一 development 证据；不宜写“LLM 替换必然提升端到端”或给出未运行的 LLM-SE 数字。
