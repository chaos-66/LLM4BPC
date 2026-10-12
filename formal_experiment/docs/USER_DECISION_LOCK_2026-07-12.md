# 用户实验决策锁定（2026-07-12）

本文件记录用户已明确接受的复现边界和后续实验原则，供所有后续 Agent 在设计、
实现、审核和报告时遵循。它只锁定研究路线，不表示数据、Gold、方法或 Part 3 已
达到正式运行门禁。

> **2026-07-12 14:25 用户当面更新**：导师要求立刻开始 B0 paper-faithful 重建
> 实现（与用户审核新数据并行）。本文件第 5 节同步更新：B0 实现代码已授权开始，
> 但真实 LLM 调用、Gold 自动产生、正式数据写入仍需单独授权。详见第 5 节。
> 此更新由 AI 助手在用户口头授权下执行，机器事件现保存在
> `docs/EXPERIMENT_EVENTS.jsonl`，当时的人类日志原文保存在
> `_retired/logs/AUDIT_LOG_legacy_through_event_29.md`。

## 1. 已确认的五项决定

### D1：使用公开来源重建 marker

不再等待 Sun 完整原始 marker lexicon。允许使用 Sleimi、LexNLP、Wiktionary/
Wiktextract 等公开来源，按照 Sun/Sleimi 的生成和句法使用方式重建 marker。

要求：

- 方法结构必须与 Sun 一致：marker 只用于定位候选，再结合 CoreNLP、
  Tregex/Tsurgeon 和依存/成分句法确定 span；
- 记录每一类 marker 的来源、版本、生成规则、冻结日期和哈希；
- 正式名称使用 `public-source reconstructed marker lexicon`；
- 不声称它是 Sun original marker lexicon；
- marker 只能在 development split 上扩展，正式 test 不得看结果后补词。

### D2：由用户进行人工 Gold 判断

用户愿意判断法规句子中 modality、actor、action、condition、constraint、
exception 的抽取是否正确，并形成正式 Gold。

要求：

- Agent 可以准备空白审核包、候选 span 和审核工具，但不得自动批准 Gold；
- 用户逐条确认、修改或拒绝候选；
- 候选抽取结果只是标注辅助，不是 Gold；
- 在正式数据、英文译文、span schema 和多分句规则锁定前，不启动正式审核；
- 人工审核结果冻结后，三种方法共享同一份 Gold。

### D3：按论文独立重写 Sun Part 2

不再以取得 Sun 完整源码为前置条件。允许根据最终论文和关键方法引用独立实现：

1. BERT-TextCNN 四类 modality 分类；
2. CoreNLP preprocessing；
3. Tregex/Tsurgeon + reconstructed marker lexicon；
4. 按 Sun 规定的顺序抽取六要素并构造 rule record。

数据可以与 Sun 原始 phrase 数据不同，但方法、顺序、输入输出语义和 Part 3 接口
必须一致。报告名称为 `paper-faithful independent reconstruction`，禁止写成
`exact reproduction` 或 `Sun original code`。

### D4：模型按 Sun 论文结构重新训练

不要求取得或复现 Sun 的原 checkpoint。使用 Sun 最终版描述的 BERT-TextCNN
结构，在锁定的数据和 split 上重新训练即可。

要求：记录预训练模型名称/版本、TextCNN 结构、学习率、batch size、epoch、seed、
split 和 checkpoint hash；不得暗示权重与 Sun 作者相同。

### D5：德文 EStG 翻译为英文

工作语言锁定为英文：保留德文原文，通过固定翻译流程生成英文文本，Part 2 的
六要素抽取和人工审核以英文译文为主，并允许审核者查看德文原文。

要求：

- 每条记录保存 German source、English translation、翻译方法/模型/版本和状态；
- 正式审核前由用户确认译文，尤其是 modal、negation、condition、exception 和
  actor/action 边界；
- Gold span 基于冻结的英文译文字符偏移；译文修改后必须使旧 span 失效并重新审；
- 三种 Part 2 方法读取完全相同的冻结英文译文；
- 翻译是公开报告的数据适配步骤，不得说 Sun 原论文明确采用了同一翻译流程。

## 2. Part 3 在 Sun 中到底比较了什么

当前可读 Sun 作者稿的 Part 3 包含两类评价：

1. **Matching 评价**：在 12 个智能电表 process models 上报告不同阈值下每个模型
   的 AP 和整体 MAP；在 4 个 GDPR BPMN 上再次报告 AP/MAP。这主要验证 Sun 自己
   的 matching score 和阈值，不是完整的前人方法对照。
2. **Violation checking 对比**：Sun 明确与 Winter et al. (2020) 比较。Table 12
   报告：

| 方法 | Precision | Recall | F1 |
|---|---:|---:|---:|
| Winter et al. (2020) | 0.58 | 0.89 | 0.70 |
| Sun 方法 | 0.77 | 0.83 | 0.80 |

Sun 的解释是：Winter 对更多 clause 进行检查，因此 recall 较高，但 false positive
更多；Sun 的 statement-level 和 phrase-level 解析提高了 precision。

证据位置：`references/papers/extracted/sun_2024_full_text.txt` 中 Section 5.3、
Tables 9--12。该文件来自较早作者稿；最终发表版可获得后仍需核对表号和数字是否
发生变化。

## 3. 本研究的 Part 3 是否必须比较

### 必须做的比较

本研究必须让三种 Part 2 输出进入**同一个冻结的 Sun Part 3**，然后比较：

- B0：Sun Part 2 独立重建；
- H1：同一 Sun Part 2 + LLM fallback；
- D1：纯 LLM 替换 Part 2。

原因是研究目标不仅是“六要素 P/R 更高”，而是验证更好的 Part 2 是否真的改善
最终合规检查。只报告 Part 2 指标不能证明下游价值。

Part 3 必须冻结以下内容：BPMN 集合、法规输入、matching 算法、相似度模型、
threshold、三类 violation 规则、Gold 和 evaluator。三组之间只允许 Part 2 输出
不同。

### 与 Sun 论文数字的关系

如果使用的数据与 Sun 不完全相同，就**不应直接把本研究数值与 Sun Table 12 的
0.77/0.83/0.80 做胜负比较**。这些数字只能作为文献参考，因为 dataset、翻译、
marker、Gold 和 BPMN subset 不同。

本研究的主要因果比较是：在本研究同一数据和同一 Part 3 中，H1/D1 相对于 B0
提升多少。建议报告绝对值和增量，例如：

`Delta downstream F1 = F1(H1 or D1) - F1(B0)`。

### 是否还需要 Winter baseline

Winter baseline 是推荐的次要比较，不是证明 LLM 创新的最低必要条件：

- 若导师包中的 Winter prototype 可以在同一冻结数据和 Gold 上可靠运行，则加入
  W0，有助于复现 Sun 的论文叙事：Winter -> Sun -> Sun+LLM/Direct LLM；
- 若 Winter 与新数据、翻译或 Gold 无法公平对齐，则只引用 Sun 的文献结果，不把
  0.58/0.89/0.70 混入本研究主结果表；
- 不能把导师包/Winter 代码称为 Sun Part 2。

因此最低必做是 B0/H1/D1 的端到端 Part 3 对比；W0 是增强型外部 baseline。

## 4. 如何证明 Part 2 的提高传递到了 Part 3

正式结果至少分三张表：

1. Part 2：四类 modality 和六要素 exact/overlap span P/R/F1；
2. Part 3：matching AP/MAP、三类 violation 的 P/R/F1；
3. 传播分析：逐字段统计 Part 2 错误是否造成 Part 3 FP/FN。

通俗解释：如果 actor 提取更准，应主要改善 incorrect-actor；action 漏检减少，应
主要改善 missing-action；action 顺序/condition scope 更准，应主要改善
out-of-order 或规则匹配。若 Part 2 F1 上升而 Part 3 不变，也必须如实报告，说明
提高发生在对下游无影响的字段/样本，或 Part 3 threshold/匹配算法成为瓶颈。

## 5. 当前已授权与未授权的动作（2026-07-12 14:25 + 17:15 更新）

### 已授权（用户当面授权）

- **开始 B0 paper-faithful 重建代码**（基于导师 2026-07-12 当面要求）
  - 仍需每步走 `python scripts/audit_project.py --with-tests` + `python scripts/record_change.py`
  - 词典、span schema、multi-clause 协议、数据/审核协议的设计仍需先与用户对齐
  - 不要求路线 v2 全部重锁后才开始"前置设计代码"（设计代码不污染正式数据，可并行）
- **17:15：用户开始逐条审核唯一 150 EStG 记录**（基于
  2026-07-12 17:15 用户最终决定；新审核入口 =
  `data/development/human_review/estg_150_canonical_review_v1.json`）
  - 旧 `estg150_review_pack_v1.jsonl` 与 user-override 副本**不再**作
    为正式编辑入口，保留为 development provenance。
  - 旧三个自动 Gold 文件（`llm_draft` / `v1_backup` /
    `v2_distribution_targeted`）保留为 development provenance，**不**
    预填进新 canonical review。
  - 任何替换 sample membership、重新抽样、产生"old 150 / new 150"
    并行路线都是**禁止**的。
  - 唯一 membership = `estg_selected_150_de.jsonl` 的 150 个 legacy
    `record_id`；membership_payload_sha256 =
    `8573e105d2bc167c6aa0a92c16f79a3aaf725baadfea86f0b5d2b1ea68b1e0d7`。
  - 用户工具：`python scripts/estg150_review_tool.py`
  - 用户校验：`python scripts/validate_canonical_review.py`
  - 用户阅读：`docs/ESTG150_DATA_MAP.md` + `docs/HUMAN_GOLD_GUIDE.md`

### 仍未授权（需单独用户授权）

- 真实翻译 / LLM / API 批处理（必须显式 `--allow-llm --max-calls N` + 审计记录）
- 自动产生或批准 Gold（仍由用户本人逐条判断）
- 直接写入 `data/gold/`、`data/predictions/`、`data/results/` 下的正式产出
- 跳过 `audit_project.py` 或 `record_change.py` 流程
- 删除/移动 `archive/` 或 `references/` 下任何文件
- **重新抽样** EStG 150 / 替换 sample membership / 产生"old 150 / new 150"
  并行路线（17:15 用户决定）
- 静默修改 `estg_150_canonical_review_v1.json` 的 v1 数据；若需 v2，
  必须建立新文件 + 新 membership_payload_sha256（17:15 用户决定）
- 启动 Wave 2 Part 2 评估器（`three_dim_eval.py` /
  `style_equivalence`）直到 B0 / H1 / D1 实际实现 + 数据审核完成

### 本节更新不表示

- 路线 v2 已重锁（仍 reopened）
- Part 3 BPMN subset、threshold 和 violation Gold 已冻结
- 150 句人工 Gold 已完成（canonical review 仍 150/150 needs_review）
- 任何最终指标可发表
- EStG-150 v1 是 Sun 论文原始 150（称为
  **independently reconstructed EStG-150 benchmark**）

### 解除方式

后续若路线 v2 完全重锁、Part 3 配置冻结、官方 modality 数据正式引入并通过 audit，
可取消本节"未授权"列表。届时新一份 `USER_DECISION_LOCK` 取代本文件。

---

下一位 Agent 应先阅读本文件、`ROUTE_LOCK.md`、
`SUN_REFERENCE_SNOWBALL_AND_MARKER_AUDIT.md` 和
`STAGE2_LLM_INNOVATION_DESIGN.md`，再提出数据/审核包和实现计划。
