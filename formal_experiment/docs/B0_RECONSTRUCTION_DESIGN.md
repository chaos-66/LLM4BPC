# B0 Paper-Faithful Reconstruction Design (Sun Part 2 Baseline)

**日期**：2026-07-12
**状态**：method design 已被用户授权（2026-07-12 14:25 当面解锁，见
`_retired/docs/2026-07/CURRENT_HANDOFF_2026-07-12.md` §12 与
`docs/USER_DECISION_LOCK_2026-07-12.md` §5）；实现代码可立刻开始；本文档
**只写方法级设计**，实现代码按本设计落地时每步仍需
`audit_project.py --with-tests` + `record_change.py`。
**作用**：解 `audit_project.py` blocker `sun_stage2_baseline_not_paper_faithful`
**授权来源**：`docs/USER_DECISION_LOCK_2026-07-12.md` §5（2026-07-12 14:25 用户当面授权）。

---

## 1. 一句话目标

按 Sun et al. (2024) **最终发表版**论文（DOI `10.1007/s11227-023-05626-0`）的方法
结构，**独立重写** Part 2 法规文档解析，使其产出与 Sun 论文同结构、同接口、
同评估标准，但**不依赖** Sun 作者未公开的代码、marker、模型权重、phrase Gold。
正式名称为 `paper-faithful independent reconstruction`。

---

## 2. 范围

| 包含 | 不包含 |
|---|---|
| 句子级 4 类 modality 分类（BERT-TextCNN） | Sun 原始训练 checkpoint |
| 短语级 6 要素抽取（CoreNLP + Tregex/Tsurgeon + 公开 marker） | 任何 `references/sun_program/` 的代码复用 |
| 与 Part 3 适配的 rule record 输出 | Part 3 任何改动 |
| 在公开/官方数据上自训 + 自标评测 | 与 Sun 绝对值（0.77/0.83/0.80）争胜 |

---

## 3. 方法学架构（流程图）

```
输入：冻结的法规文本（每条 = 一句或多句，带稳定 sample_id）
            │
            ▼
┌────────────────────────────────────────────┐
│ Part 2 句子级：BERT-TextCNN                │
│ ─ 输入：单句 + 上下文                      │
│ ─ 输出：4 类 modality（obligation /         │
│   prohibition / permission / definition）   │
│ ─ 训练：官方 EStG modality CSV              │
│   （Archive.org Decision_Logic_data.zip）   │
│ ─ 评估：macro-F1、每类 P/R/F1、confusion   │
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────┐
│ Part 2 短语级：六要素抽取                  │
│ ─ 工具：Stanford CoreNLP                   │
│ ─ 规则：Tregex/Tsurgeon + 公开 marker      │
│ ─ 顺序（Sun 强约束）：                      │
│   1. modality  ← 2. condition              │
│   2. condition ← 3. constraint             │
│   3. constraint← 4. exception              │
│   4. exception ← 5. action                 │
│   6. actor 在 1-5 完成后做                 │
│ ─ 输出：六要素 spans + 字符 offset          │
│   + evidence 原文（双视图）                │
└────────────────┬───────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────┐
│ Part 2 输出：rule record                   │
│ ─ 格式：见 `configs/schemas/                │
│   stage2_prediction.schema.json@1.0.0`     │
│ ─ 字段：sample_id, modality, six_spans,    │
│   rule_record, evidence_span (原文)         │
│ ─ 接口：与 Part 3 adapter 严格对齐         │
└────────────────────────────────────────────┘
```

---

## 4. 公开来源 marker lexicon 重建

**原则**：方法结构与 Sun/Sleimi 一致（marker 定位候选 + Tregex 决定 span），来源、
版本、日期、哈希全部记录。

| 六要素 | 公开来源 | 重建方法 | 冻结时记录 |
|---|---|---|---|
| condition | 本地研究审计已逐项转录的 LexNLP public condition 表 + 论文显式例项 | 离线去重合并；固定来源快照 | source/manifest/payload SHA256 |
| constraint | 本地研究审计明确枚举的 19 个 LexNLP public constraint 摘录 | 只用明确转录项；未转录的 reported 40-pattern remainder 不猜测 | source/manifest/payload SHA256 |
| actor | 论文显式例项；Wiktionary EN dump 为后续可选扩展 | v1 不含未固定 dump 的自动扩展 | v1 source/hash；未来 dump 日期/hash 另锁 |
| modality | Sun/Sleimi 论文公开例项 | 只保留显式 public seed；definition marker 暂为空 | seed source + payload hash |
| action | 句法规则（tregex POS pattern） | 论文描述的 verb phrase 模式 | tregex 模式脚本 + commit |
| exception | 公开种子 + development-only 扩展 | 公开 trigger + 内部补充 | 明确标"development-only expansion" |

**关键纪律**：
- S2.3 v1 每类 marker 存为 `resources/lexicon/{category}_markers_en_v1.json`，含 `_meta` 字段（来源、版本、语言与 SHA256）；总 manifest 为 `public_marker_lexicon_en_v1.manifest.json`
- 正式 test split 上**不得**看结果后补词
- lexicon 只能随 split 一起冻结

**S2.3 实现状态（2026-07-16）**：v1 已离线锁定 64 个 marker（7/25/19/5/8），
development 扩展表为空；完整来源与 hash 见
`docs/research/PUBLIC_MARKER_LEXICON_RECONSTRUCTION.md`。这只是 development resource，
未启动 S2.4/S2.5，也未处理许可与 S2.4 ready 的现有矛盾。

---

## 5. BERT-TextCNN 训练方案

| 项 | 决定 | 理由 |
|---|---|---|
| 预训练模型 | bert-base-cased 或 bert-base-multilingual-cased | 公开、社区支持强、可复现 |
| TextCNN 结构 | Sun 论文描述：卷积核 2/3/4-gram，max-pooling，concat → softmax | 与论文一致 |
| 学习率 | 2e-5（Adam） | 行业经验值 |
| Batch size | 32 | 显存允许 |
| Epoch | 5-10 + early stop on dev F1 | 标准做法 |
| Seed | 42 / 123 / 2024（三次跑取均值） | 稳定性 |
| 训练数据 | 官方 EStG modality CSV（2833 句） | Sun 论文同一数据源 |
| Split | 80/10/10（train/dev/test） | 固定 seed 抽取 |
| 评估 | macro-F1 + 4 类 P/R/F1 + confusion | 与 Sun 论文 Table 9-10 对齐 |

**记录项**：每次跑都记 `git commit + seed + 数据 SHA + 模型 checkpoint SHA + TensorBoard 摘要`。

---

## 6. 六要素抽取（短语级）

### 6.1 工具栈
- **Stanford CoreNLP 4.5.x**：tokenize、POS、lemma、depparse、constituency（tregex 依赖 constituency tree）
- **Tregex/Tsurgeon**：Sun 论文描述的树模式（Treebank 标签）
- 标注语料：与训练数据冻结后保持一致

### 6.2 抽取顺序（Sun 强约束）
1. **modality**（用句子级输出 + 候选 marker 复核）
2. **condition**（标记候选后，依赖句法锁定 scope）
3. **constraint**（同 condition，但触发词不同）
4. **exception**（独立成字段，不并入 condition）
5. **action**（在 1-4 抽取/移除后才能跑；论文原话："action must be extracted after modality/condition/constraint/exception are identified/removed"）
6. **actor**（最后做；候选从 dependency parse 拿，结合 Sleimi 词典消歧）

### 6.3 输出 schema（双视图）
```json
{
  "label": "actor",
  "text": "the data controller",
  "start": 12,
  "end": 31,
  "normalized": "data_controller",
  "confidence": 0.0
}
```
- `text` 严格等于 `source[start:end]`
- `normalized` 用 controlled vocabulary
- `confidence` 留接口（暂可固定）

### 6.4 关键消融
- B0-a：仅 Sun 论文示例 marker
- B0-b：+ LexNLP condition/constraint
- B0-c：+ Wiktionary actor
- B0-d：+ development-only exception 扩展

---

## 7. rule record 输出

每个 sample 输出一个 rule record，字段：
- `sample_id`（与 input 一致）
- `sentence_text`（冻结的英文译文）
- `modality`（4 类）
- `spans`：六要素 span 数组（每元素含 label/text/start/end/normalized）
- `actor_action_map`：[{actor_id, action_id}]
- `order_relations`：[{"before_action_id", "after_action_id", "evidence"}]
- `_meta`：模型版本、lexicon commit、运行时间、置信度

**接口契约**：与 `bpc_hybrid.sun_compat.stage3_adapter.Stage3Adapter` 严格对齐。

---

## 8. 评估指标

| 层级 | 指标 | 用途 |
|---|---|---|
| 句子级 | 4 类 macro-F1 + confusion | modality 分类质量 |
| 短语级 | 6 要素 exact span P/R/F1 | 抽取精度（按字段 + macro/micro） |
| 短语级 | 6 要素 token-overlap P/R/F1 | 边界容错 |
| 整体 | 5 次跑 stability（field agreement） | 稳定性 |
| 整体 | coverage + invalid rate + API fail | 数据健康度 |
| 跨阶段 | Part 3 AP/MAP + violation P/R/F1 | 下游影响 |

**缺失/无效/API 失败必须计入 coverage，不从分母删除**。

---

## 9. 与当前 heuristic runner 的差异

`scripts/run_sun_rule_only.py` 当前用**关键词 + spaCy 启发式**抽取六要素，**不是**最终论文描述的 BERT-TextCNN + CoreNLP/Tregex/Tsurgeon。重构后将：

| 项 | 当前 | 重构后 |
|---|---|---|
| 句子级 | 无（默认用 keyword fallback） | BERT-TextCNN 4 类 |
| 句法 | spaCy dep | CoreNLP constituency + dep |
| 树规则 | 无 | Tregex/Tsurgeon 模式 |
| 词典 | 内置 keyword 列表 | 公开来源重建 + provenance |
| 训练 | 无 | 自训 + checkpoint hash |

**正式 baseline = 重构后版本**。当前 runner 标 `development_only_not_formal`。

---

## 10. 实现优先级（建议 4-6 周单人工作量）

| 周次 | 任务 | 里程碑 | 解锁的 blocker |
|---|---|---|---|
| W1 | 写 `marker_lexicon` 模块（公开来源 + provenance） | 4 类词典冻结 | 资源贡献可声明 |
| W1 | 写句子级 data loader + BERT-TextCNN 训练脚本 | 模型训出 dev F1 | 部分 `sun_stage2_baseline_not_paper_faithful` |
| W2 | 写 CoreNLP wrapper + Tregex/Tsurgeon 模式库 | 句子级 + 短语级独立跑通 | 完整 `sun_stage2_baseline_not_paper_faithful` |
| W3 | 实现六要素抽取（按 Sun 顺序） | 单元测试过 | 方法学一致 |
| W4 | rule record 输出 + Part 3 adapter 联调 | 端到端 1 句 | 端到端通 |
| W5 | 在 150 句 + GDPR-50 上跑全量 + 评估 | 36 组消融完整 | 可比 H1/D1 增量 |
| W6 | failure case study + 文档 + 论文初稿 | paper ready | 全部 blocker 解除 |

**实际进度根据 audit/数据/导师反馈调整**。每周末跑 `audit --with-tests` + 记一行。

---

## 11. 风险与缓解

| 风险 | 缓解 |
|---|---|
| CoreNLP 装不上 / 太慢 | 备选：自写轻量 constituency parser；只跑关键句 |
| Tregex 模式写不出来 | 退到 Tregex-light（只匹配核心 POS 模式） |
| BERT-TextCNN F1 不达论文水平 | 报告真实数字，**不强求**和 Sun 0.80 接近；强调 paper-faithful |
| 训练数据 license 模糊 | 用前先和导师 + 论文 license 确认；记录 license |
| 用户审核时间长 | B 线与 A 线并行；旧 pack 副本可作为熟悉文本 |

---

## 12. 与"不允许声称"边界

**允许的称呼**：
- `paper-faithful independent reconstruction of the final published Sun Part 2`
- `B0 baseline (paper-faithful reconstruction, no Sun code or weights)`
- `BERT-TextCNN retrained from scratch on official EStG modality data`

**禁止的称呼**：
- `we reproduce Sun et al. (2024)`（除非有 Sun 原始代码/权重）
- `Sun's original Part 2 baseline`（Sun 没公开新 Part 2）
- `we matched Sun's reported 0.77/0.83/0.80`（数据不同，不能直接比）
- 导师包 = Sun 完整源码

---

## 13. 下一步

| 任务 | 谁 | 何时 |
|---|---|---|
| 文档审阅（提供反馈） | 导师 / 用户 | 1-2 周内 |
| 按反馈修改本文档 | AI | 收到反馈后 |
| 收到反馈后开始 A2（marker lexicon 模块） | AI | 已授权，可开始 |

---

**机器记录**：本文档存在 `docs/B0_RECONSTRUCTION_DESIGN.md`；变更需走
`audit_project.py --with-tests` + `record_change.py`。
