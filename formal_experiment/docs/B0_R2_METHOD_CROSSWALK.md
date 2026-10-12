# B0-R2 方法对照表（Sun 核心方法 vs 本项目重建）

> 任务：B0-R2（component-vs-method cross-walk，文档部分）
> 状态：development only；`method_conformance_status` 仍为 `blocked_until_b0_r2`，本表不改变任何门禁
> 依据：`MASTER_PIPELINE.md` §8.6 B0-R2 行；`docs/B0_RECONSTRUCTION_DESIGN.md`；Sun et al. (2024) 的公开方法描述（DOI 10.1007/s11227-023-05626-0，方法级独立复现口径，非 exact reproduction）

## 1. 对照表

| # | Sun 方法元素 | 本项目实现 | 证据（file / tests） | 适配与披露 |
|---|---|---|---|---|
| 1 | BERT-TextCNN 模态分类器 | `BertTextCNN` + 锁定 S2.4 checkpoint（Legal-BERT base uncased 编码器 + TextCNN 头），inference-only 加载 | `src/bpc_hybrid/sun_style/bert_textcnn.py`、`sun_style/sun_b0.py:117-206`（`LockedBertTextCNNInference`，checkpoint/config/manifest 三重 hash 绑定）；`tests/test_s24_bert_textcnn.py` | 训练过程未复现（无原权重）；使用本地训练 checkpoint（s24_candidate_B），披露为重建资产 |
| 2 | CoreNLP constituency 解析 | Stanford CoreNLP 4.5.10，annotators=tokenize/ssplit/pos/lemma/parse/depparse | `src/bpc_hybrid/sun_style/corenlp_runtime.py`、`estg150_b0_development.py:280-389`；`tests/test_s25_corenlp_contract.py` | 版本锁定 4.5.10（Sun 论文未公布其版本）；runtime identity（jar sha）记录进 manifest |
| 3 | Tregex 短语模式 | `sun_phrase_patterns_v3_enhanced.json`（六字段 28 个模式，`<`/`<<` 语义有真实 bridge 测试） | `resources/corenlp/sun_phrase_patterns_v3_enhanced.json`；`tests/test_b0_r1_bridge_semantics.py`（真实编译运行 bridge 断言 child/descendant 与 multi-match） | 模式为按 Sun/公开 cue 重建；`test_time_rule_edits_forbidden=true` |
| 4 | Tsurgeon 手术 | `SunPhraseRuleBatchBridgeMulti.java` 支持 operation；registry 当前 operation 全空、`tsurgeon_enabled=false`；operated 多命中 fail-closed 守卫 | `tools/corenlp/SunPhraseRuleBatchBridgeMulti.java`（B0-R1-BRIDGE 守卫）；`tests/test_b0_r1_bridge_semantics.py` | **诚实非实现披露**：v10a 配置 `tsurgeon_note='Honest non-implementation: operations empty; Multi bridge collect-only'`；需用户决定是否引入 operation |
| 5 | 公开抽取顺序 | `extraction_order = [modality, condition, constraint, exception, action, actor]`，`overlap_resolution=smallest_sufficient_then_leftmost` | registry `ordering_policy`；`estg150_b0_development_v10.py` compose 路径 | 一致 |
| 6 | 六字段输出 schema | canonical Rule Record（modality evidence+label、actor、action、condition、constraint、exception + clause 结构） | `configs/schemas/stage2_prediction.schema.json`、`STAGE2_CANONICAL_SCHEMA_SPEC.md`；`tests/test_schema.py` 等 | 一致；多 clause 结构为扩展（Sun 论文以句为单位） |
| 7 | 评价口径（六字段 span 抽取） | `sun_literal_overlap_evaluation@2.0.0`：statement 级、同字段任意非空字符交叠、无 clause alignment、无一对一 | `src/bpc_hybrid/stage2_sun_literal_overlap.py`、`configs/evaluation/sun_table8_literal_overlap_v2.json`；`tests/test_stage2_sun_literal_overlap.py` | §8.6 主口径；strict exact/token/clause-aligned 仅诊断 |
| 8 | 模态四分类 label | 独立面板：marker 路由 + clause/record 分类器路由 + DE/EN 对齐验证（`_cross_validates`，B0-R1-ALIGN） | `b0_v10/modality.py`、`definition_resolver.py`、`alignment.py`；`tests/test_b0_r1_align_cue_validation.py` | 四分类 label 另表报告（§8.6 要求）；分类器为本地重建资产 |
| 9 | 词典/marker 方法 | `public_marker_lexicon_en_v2`（5 类 161 激活项），构造模式 pinned_public_seed（9 个公开来源） | `resources/lexicon/*_en_v2.json` + manifest + sources manifest；`tests/test_sun_modality_gate.py` 等 | 词典为公开重建、dev-only；规模差异仅披露（S2.3） |
| 10 | 句子/clause 分割 | `plan_clause_units_v4` + `split_german_units` + DE/EN 对齐（本项目为 Sun Part 2 流程的补充机制） | `b0_v10/segmentation.py`、`estg150_b0_development_v3.py`；`tests/test_b0_r1_a_span_boundaries.py` | 披露为独立重建机制（Sun 论文未公布分句细节） |
| 11 | actor/action 归属 | 依赖子树 + 词典中心词门控 + action 头/nsubj/obl-by-to 候选（B0-R1-ACTION/ACTOR） | `b0_v10/actor_action.py`；`tests/test_b0_r1_action_span_scope.py`、`test_b0_r1_actor*` | 披露为重建机制（Sun 未公布 actor/action 细节） |

## 2. 结论与门禁

- **已实现并有测试**：#1-#3、#5-#8、#10-#11（核心组件、抽取顺序、六字段输出、主口径 evaluator 均落地且经真实运行验证）。
- **披露项**：#4 Tsurgeon 为诚实非实现（registry operation 空 + fail-closed 守卫）；#9 词典规模与方法细节差异仅披露。
- **门禁不变**：本表不改变 `sun_rule_only.method_conformance_status`；该字段仍为 `blocked_until_b0_r2`，其变更**需用户显式授权**（`configs/methods.json` notes 与 §8.6 B0-R2 行明文）。B0-R3（固定 snapshot 运行 + 正式错误分析）同样需用户另行授权。
