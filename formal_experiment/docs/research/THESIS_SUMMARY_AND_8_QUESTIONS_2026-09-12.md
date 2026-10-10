# 论文收尾总结 + 八个问题的证据与方案（只读分析，零 API、零改动）

**日期**：2026-09-12
**性质**：只读分析文档。本文不产生新的实验事实，不修改任何 Gold / 预测 / 合同 /
门禁。所有数字均来自仓库既有产物，逐条给出文件与行号。
**证据等级**：凡引用均为 `VERIFIED_PROJECT_FACT` 或 `VERIFIED_PRIMARY_SOURCE`；
凡本文件新提出的推论标 `INFERENCE`；凡建议行动标 `PROPOSAL`（未授权、未执行）。

---

## 0. 项目现状（一段话）

三阶段框架（Sun et al. 2024）的方法级独立重建已完成并可审计：Stage 1 在固定
GDPR-7 上完成描述性复现并冻结（`data/gold/stage1/process_records/
stage1_process_gold_v1.json`，2026-08-13）；Stage 2 完成正式三方法比较
（Rules-Only / LLM-SE / Rules+LLM-Repair，`outputs/reports/
stage2_formal_three_method_comparison_v1.json`，2026-08-11）；Stage 3 完成四方法
非 LLM 对照、33 条人工 panel、30+40 条合成受控错误面板、阈值敏感性、以及四类违规
的扩展实验。四个完整性门禁当前均为 true（`docs/PROJECT_AUDIT.md` L591–605），但
`final_experiment_ready=true` **只表示 Stage 2 三方法正式评价的机器门禁就绪**，
不代表 S2.13 / S3.7 / 端到端完成。

**仍然没有的东西**：端到端 E00/E10/E01/E11 全部未执行；S2.12 复杂语料只有
Rules-Only 单臂；S3.7 正式 Oracle 主表未授权；`paper/CLAIM_EVIDENCE_MATRIX.md`
中**没有任何一条以正证据等级声明"本文方法相对前人具有新颖性"**，且 C26（8+8 模块
方法章节）状态为 `PLANNED_METHOD`，明确禁止写"模块有效性已验证"。

**同时要知道的两个"前人现状"**（本文件新增核验，详见 §1.4）：**Sun 自己也没有
六要素抽取（Stage 2B）的前人对比**，其论文只对 modality 做了 6 BERT + 3 经典
分类器的对比、对违规检测只对比了 Winter；**Winter 也从未做六要素抽取**。所以
"Stage 2B 缺前人基线"是整个领域的空白，不只是本项目的遗漏。

---

## 1. 前人对比：为什么"第二阶段没有 Winter 对比"这个说法需要修正

### 1.1 结论

**"模仿 Sun 做了哪些前人对比"这条思路是对的，而且直接可执行。** Sun 在违规检测
环节对比的唯一前人就是 **Winter et al. (2020)**（Table 12）。本项目 Stage 3 已经
做了 Winter 对比（§3.3 表 A），所以"模仿"的落点应该在**还没有 Winter 的地方**，
也就是 Stage 2 一侧。

但要先说清一个容易搞错的地方：**Winter 并不是 Stage 2（六要素语义解析）的前人。**
在当前全部可得材料里，只有 Sun 做过"从规范文本恢复结构化 Rule Record"这件事，
Winter 的"条款处理"只是用 4 个 signalword 筛句 + spaCy 相似度。

**不过用户的直觉指向了一个真实缺口，只是形式不同**：Winter 在**流程侧的义务/
顺序证据**和**"义务动作识别"这一层**确实是可比较的前人——不是"六要素 F1 对比"，
而是"义务动作集合匹配对比"。下面给证据。

**同时还有一个更强的发现（§1.4）：Sun 自己也没有六要素抽取的前人对比。**
所以"Stage 2B 缺前人基线"是整个领域的空白，不只是本项目的遗漏——这既是缺口，
也是一条可以写进贡献的结论。

### 1.2 证据：Winter 的第二阶段到底做了什么

Winter 原型仓库 `references/winter_2020_model_check/model_check/`（112 个文件）：

| 证据 | 内容 |
|---|---|
| `input/files/signalwords.txt` | **只有 4 个词**：`shall` / `must` / `should` / `may` |
| `input/files/sequencemarkers.txt` | **只有 13 个词**：then, after, afterward(s), subsequently, based on this, thus（含首字母大写重复项） |
| `input/files/stopwords.txt` | 通用停用词表 |
| `input/files/gdpr.config` | `only_constraints: True`、`gamma: 0.4`、`delta: 0.8` |
| `input/regulations/gdpr/article*.txt` | **纯文本条款**，无标注、无六要素、无语义结构 |
| `lib/classes/Pair.py` L18–21 | 恰好三个成本函数：`cost_obligation`、`cost_resource`、`cost_so`，加权和权重 1/3 |
| `lib/classes/Pair.py` L28–57 | `calculate_mapping`：条款义务文本 ↔ 模型义务任务做 **max spaCy 相似度** |
| `lib/classes/Pair.py` L114–119 | `check_resource_violation`：比较条款文本里出现的资源名与模型任务所属 participant |
| `lib/classes/Pair.py` L144–158 | `check_flow_violation`：用 `is_reachable_from` 判断可达关系 |

**Winter 没有任何 modality 分类器、没有条件/约束/例外的抽取、没有 modality
evidence span、没有受控 schema、没有坐标回指。** 它的"regulation parsing"就是：
用 4 个 signalwords 筛出含情态动词的句子，用 13 个 sequence markers 猜顺序，
其余全部靠句级 spaCy 相似度。

### 1.3 证据：Sun 的官方包里，第二阶段源码根本不在

`docs/research/SUN_WINTER_CODE_SEPARATION_AUDIT.md` L5–22：

> 导师说明 `references/合规性检查模型代码/` 由 Sun 论文作者提供……
> 其中 `model_check/` 的文件内容是 Winter et al. (2020) prototype 的直接副本，
> 不是 Sun 最终版 Stage 2 源码。
> 112 个相对路径与 SHA-256 全部相同；导师包额外 11 个文件全部为 `__pycache__/*.pyc`。
> 包中有 spaCy、`Pair` fitness/cost、7 个 GDPR BPMN、Articles 5–50、`gamma`/`delta`；
> **没有最终 Sun Stage 2 所需的 BERT-TextCNN、CoreNLP、Tregex/Tsurgeon Java
> pipeline、六概念完整实现或训练模型。**

我已经独立核对了文件清单：`references/合规性检查模型代码/model_check/` 与
`references/winter_2020_model_check/model_check/` 的目录树完全一致
（`lib/main.py`、`lib/functions.py`、`lib/classes/{BPMN,Clause,Document_Collection,
Flow,Mapping,Pair,Paragraph,Process,Sentence,SimilarityComputer}.py`、7 个 BPMN、
41 个 article.txt、三个词表、`results/gdpr_gamma{00,04,06,08}/`）。

**这条证据的推论（`INFERENCE`，但证据链完整）**：Sun 的已发布工件**没有覆盖
Stage 2**，作者交给导师的包在 Stage 3 上就是 Winter 原型。这同时解释了问题 8
（为什么只有三类违规），见 §2。

### 1.4 关键修正：**Sun 自己也没有 Stage 2B（六要素抽取）的前人对比**

核验 Sun 论文全文（作者稿，`references/papers/extracted/sun_2024_full_text.txt`）
后，"前人对比"的真实分布是：

| Sun 的环节 | Sun 对比了什么 | 出处 |
|---|---|---|
| modality 分类（我们的 2A） | **6 个 BERT 变体**（base/large × uncased/cased + bert-legal-uncased/cased，F1 84.1%–89.3%）**+ 3 个经典分类器** `CF_KW` 60.8% / `CF_RNN`(BiLSTM) 90.9% / `CF_CNN` 90.2%，Sun 自报 93.1% | 全文 L653–708（Table 6/7） |
| **六要素抽取（我们的 2B）** | **零前人对比**——Table 8 只有自评（GT 443 / 抽出 431 / matched 422，P 97.9% R 95.3%） | 全文 L717–770 |
| matching（3A） | **零前人方法**，只做自己的 τ 扫描（Dataset C MAP@0.8=0.801；Dataset D MAP@0.8=0.840） | 全文 L812–871 |
| **违规检测（3B）** | **恰好一个前人：Winter et al. (2020)**，Winter 0.58/0.89/0.70 vs Sun 0.77/0.83/0.80 | 全文 L872–893（Table 12） |

Sun 对 Winter 的评语（原文，L872–889）：Winter "uses keyword to identify sentence
types and applies **all clauses** as what needs to be checked **without in-depth
extraction of phrases**"——召回更高、精度更低，"significantly increases the
subsequent manual checking effort"。

**结论（比原判断更强）**：**整个前人谱系里都没有 Stage 2B 的可比基线**——Sun 没有，
Winter 没有，Sleimi / Michel / Barrientos 都没有被 Sun 当作方法对比过（它们只是
方法来源或数据来源）。所以"补前人对比"不是补一行数字，而是**填一个前人留下的
空白**；这本身就是一条可写进贡献的结论。

### 1.5 那么"补前人对比"的正确形式是什么

| 建议对比 | 前人来源 | 为什么成立 | 现有资产 |
|---|---|---|---|
| A. 义务动作集合匹配（obligation-set matching） | **Winter** | Winter 确实从规范文本产出一个"义务动作集合"（signalwords 筛句 + spaCy 从句切分），可与 Rule Record 的 action 集合在同一 150 条 / 同一 Gold 上比较 | 已有 `src/bpc_hybrid/winter_stage3/`（含 `winter_clause.py` L142–153、`winter_pair.py`）；`configs/winter_stage3_development_v1.json`；只需把 clause 侧指向 EStG-150 英文 |
| B. modality 分类：signal-word 下限 | **Winter**（4 词） vs **BERT-TextCNN**（本重建） vs **LLM-SE** | 4 个 signalword 直接给出一个诚实的 modality 下限；`may` 同时覆盖 permission 与 "may not"=prohibition，这个失败模式本身就是可报告结论 | 4 词表已在仓库；EStG-150 Gold 有 modality 标签 |
| C. 六要素抽取：marker/Tregex 谱系 | **Sun**（已在）+ **Sleimi et al.** + **Michel et al. 2022** | 只有这条谱系做过 phrase-level 法律语义抽取；Michel 2022 正是 EStG 语料的原始出处 | `docs/research/SUN_REFERENCE_SNOWBALL_AND_MARKER_AUDIT.md` L100–114（Sleimi 2018 在 150 条陈述上 1,177 短语 / 1,202 标注）；`references/papers/Michel_2022_Decision_rules.pdf` |

**注意 S2.7 仍是 `blocked`**：`MASTER_PIPELINE.md` L864 把"实现一个代表性非 LLM
baseline"（六要素任务）保持为 blocked，`EXPERIMENT_LOG.md` L495 记 "phrase/full
S2.7 blocked"。这是"Stage 2B 无前人对比"在管线上的直接体现。

### 1.6 已经存在的、容易被忽略的前人对比资产（别再重复做）

`docs/research/` 之外，仓库里**已经**有下列 Stage 2 对比，写论文时应直接引用而不是
重跑：

| # | 对比 | 数字 | 出处 |
|---|---|---|---|
| 1 | 三个非 LLM modality 下限（majority / keyword / Multinomial NB），Sun 官方数据 426 条 test | accuracy/macro-F1 = 0.4577/0.1570、0.4836/0.4142、**0.7840/0.5688** | `EXPERIMENT_LOG.md` L489–504 |
| 2 | 本地 BERT-TextCNN vs **Sun 论文报告值**（C3 级） | 本地 acc 0.9249 / macro-F1 0.8511（P 87.5 / R 87.9 / F1 87.7）vs Sun Table 7 P92.1/R94.1/F193.1 → **差 −4.6/−6.2/−5.4 pp**，弱在 permission/prohibition | `EXPERIMENT_LOG.md` L344–350、L2853 |
| 3 | **Barrientos 原生 vs 本文**，共享 3 类 modality 目标 | Barrientos macro-F1 **0.890**（ob 1.000 / per 0.781 / pro 0.889）vs 本文 **0.822**（1.000 / 0.667 / 0.800） | `outputs/reports/barrientos_de_tables_v1.md` L45–52（1,140 real calls） |
| 4 | 模块替换（OURS-FULL vs OURS-BARRIENTOS-MODULE） | 0.874（SD 0.003）vs **0.000**；modality label macro-F1 0.617 vs 0.000 | 同上 L29–43 |

**必写的边界声明**（否则会被审稿人直接打回）："Winter et al. (2020) 未定义 Stage 2
Rule Record，其条款处理是 4 个 signal words 的义务句筛选与 13 个 sequence markers
的顺序线索；本文的 Winter 对比仅限于**义务动作集合**与**情态词下限**两个可比层，
不构成 Sun 六要素抽取的方法对比。" 这一句同时把"我们做了前人没做的事"讲清楚了。

### 1.7 直接可用的动作清单（`PROPOSAL`，未执行）

1. **零 API、约 1 人日**：把 `winter_stage3` 的 clause 侧接到 EStG-150 英文输入，
   产出 Winter 义务动作集合，在同一粗/细 Gold 上算 action 字段的 P/R/F1，与
   Rules-Only（0.8927 粗 action F1）和 LLM-SE（0.9437）并列成一行。
2. **零 API、约 0.5 人日**：用 4 个 signalword 做 modality 预测，报 4 类 label
   accuracy / macro-F1，与 Rules-Only（0.7400 / 0.7128）、LLM-SE（0.8333 /
   0.7695）并列。**注意**：需先声明 `may not` 的处理规则（否则该下限不公平）。
3. **写作、0 计算**：在 §2.3 补 Sleimi / Michel / Leopold / Agostinelli 的关系段
   （当前是 `[[TODO-SOURCE:...]]`，`paper/THESIS_DRAFT.md` L97、L101、L105）。

---

## 2. 为什么 Sun 与 Winter 都只研究三种违规类型

> **先声明证据边界**：仓库里**没有**任何文档记录"Sun 的作者为什么选这三类"。
> 仓库只记录了"这三类消费了什么、没消费什么"（`RESEARCH_EVIDENCE_REVIEW_
> 2026-09-06.md` L74–83、`run_s3_extended_violation_panel_v2.py` L101–128 的
> `SELECTION_RATIONALE`）。**下文的成因解释是本文件的 `INFERENCE`**，但每一步都
> 有代码或数据支撑，可以安全地写进论文的"讨论"而不是"相关工作"。

### 2.1 直接证据：那三类就是 Winter 原型里恰好写下的三个成本函数

`references/winter_2020_model_check/model_check/lib/classes/Pair.py`：

```
L18:  self.cost_obligation  = self.cost_obligation(self.gamma)     # → missing_action
L19:  self.cost_resource    = self.cost_resource(self.gamma, self.delta)  # → incorrect_actor
L20:  self.cost_so          = self.cost_so(self.gamma)             # → out_of_order
L21:  self.cost = self.cost_score(1/3, 1/3, 1/3)   # weights = w_o, w_a, w_so
```

本项目的映射是显式的、已锁定的：

`configs/schemas/stage3_prediction.schema.json` L14–16：
> `missing_action_score`: "Winter=cost_obligation; Sun=Definition 5 action violation"
> `incorrect_actor_score`: "Winter=cost_resource; Sun=Definition 6 actor violation"
> `out_of_order_score`: "Winter=cost_so; Sun=Definition 7 order violation"

且 Sun 侧的重建 `src/bpc_hybrid/sun_stage3/sun_scorer.py` 是 Definition 4–7
（L37 matching_score、L102 missing_action、L127 incorrect_actor、L199 out_of_order）。
**Winter 的 3 个成本函数与 Sun 的 Definition 5–7 一一对应，不是巧合**；结合
§1.3 的"Sun 官方包里 Stage 3 就是 Winter 原型"，最简洁的解释是：三类违规是
**同一份代码的三个函数**，Sun 做的是把它形式化进论文（Def 4–7），而不是独立地
论证"违规类型只有三类"。

### 2.2 机制层面的真正原因：三类违规是"Rule Record × BPMN 计算图"上的闭包

看 Sun 的 matching 公式（`sun_scorer.py` L37–67）：

```
matching(r, m, τ) = max( Dr,m 中 sim>τ 的比例 , Or,m 中 sim>τ 的比例 )
```

其中 `Dr,m` = 规则动作集合，`Or,m` = 规则 actor 集合。**条件、约束、例外完全不
参与 matching，也不参与任何后续检查。** 于是：

| 违规类型 | 需要的规则侧证据 | 需要的流程侧证据 | 现有表示是否提供 |
|---|---|---|---|
| missing_action | action 集合 | 任务/事件 label 集合 + 动作词表 + γ 阈值 | ✅ 都提供 |
| incorrect_actor | actor 集合 + actor-action 配对 | lane/participant 名 + 活动到 actor 的绑定 | ✅ 提供（但 GDPR-7 lane 名为空） |
| out_of_order | order_relations（有序任务对） | sequence flow + `is_reachable` | ✅ 提供 |
| （未实现）| condition / constraint / exception | gateway conditionExpression、timer、data object、boundary/error event | ❌ 规则侧为空；流程侧"是否存在该表面"本身就是判断难点 |

**一句话机制**：**三类违规恰好是"Rule Record 里被解析了的字段 × BPMN 里可观察的
表面"的闭包。** 前两类的共同前提是 action 匹配成立（γ 门槛），第三类额外需要
order_relations。**凡是要用 condition/constraint/exception 才能判的违规，在
Sun 的公式里根本无处插入**，因为这三个字段从未成为匹配的一等公民。

这一点在本项目的数据上有直接印证：
- `sun_scorer.py` L142–167：actor 检查的第一道门就是
  `action_mapping_below_gamma` → 返回 `unavailable`，不是返回 0；
- `docs/PROJECT_AUDIT.md` L252–262：四类扩展里 **30/30** 个 condition/constraint/
  exception 变体**全部卡在 action localization**，最佳候选相似度
  0.3177–0.6683，全部低于冻结的 γ=0.8（26 条 `no_candidate_above_gamma` +
  4 条 `structure_not_satisfied`）；**0 例**是"结构打开了相似度关上的门"；
- `docs/PROJECT_AUDIT.md` L348–352：S3.7 Oracle 隔离跑里，`incorrect_actor`
  **11/11** 不可观测、`out_of_order` **11/11** 不可观测。

也就是说：**不是这三类"效果最好"，而是这三类是当时唯一能挂上计算的地方。**

### 2.3 "其他违规类型效果很差"的真实原因（本项目已实测）

用户听说的"其他类型效果很差"在本项目里已经**被做成了实验**，结论比"效果差"更
精确。四类扩展是 2026-08-31 起按"未被 Stage 3 消费的 Rule Record 字段"选出的
（`paper/THESIS_DRAFT.md` §7.4.1，L734–752）：

| 新类型 | 使用的证据 | 实测（`outputs/reports/s3_formula_repair_v2.json`；`paper/THESIS_DRAFT.md` §7.4.4，L791–822） |
|---|---|---|
| prohibited_action_present | prohibition modality + action | **可行性成立**：Winter-style F1 0.952、Sun-style 0.952、TF-IDF 1.000；四方法均值约 0.893 |
| required_condition_not_enforced | condition + action | **最难**：Sun-style 0.000、BM25 0.000、TF-IDF 0.000、Winter-style 0.235；29/30 目标类型不可观测（30/40） |
| constraint_violated | constraint + action | 部分支持：Winter-style 0.400、TF-IDF 0.333 |
| exception_not_handled | exception + action | 基本不可用：Winter-style 0.308、Sun/BM25 0.000、TF-IDF 0.167 |

同时 S3-PAIRED-MECH（`docs/PROJECT_AUDIT.md` L312–317）与统一重评
（`docs/research/S3_EXT_UNIFIED_EVALUATION_NOTE_2026-09-06.md` §1–§2）给出：
Winter-style 检出最好但**在 40 条合规对照上误报率 0.500**——"能发现问题 ≠ 不误伤
合规流程"。

**所以真正的失败链条是（三段，每段都有数据）**：
1. **动作映射失败**：30/30 条件/约束/例外变体卡在 γ 门；
2. **规则侧证据缺失**：`empty_rule_condition` / `no_mapped_rule_order_endpoints`
   是实际报出的 reason（`MASTER_PIPELINE.md` L1280 的 SIM 真实案例诊断）；
3. **流程侧不可观察**：即使前两步过了，"这个 BPMN 里有没有能承载该条件的表面"
   仍需判断，被诚实记为 unobservable（Sun-style 28/30）。

**最新的修复轮（2026-09-11）也给出同向证据**：真正把 v3 内部 γ 改成 0.4 的 A 臂
把 Macro-F1 做到 **0.5690**（旧 v3 0.2273、原路径+0.4 0.4738），但**对照误报同时
涨到 24**（旧 v3 8、原路径+0.4 20）；C 臂把对照误报从 20 压到 **14**、成对从 11
升到 **13**，代价是变体正确 **19→18（净退步 1）**。项目自己的措辞是
"未能在压低对照误报的同时超过原路径"（`PROJECT_AUDIT.md` L159–181）。
**即：放开阈值能提分但误报失控，收紧误报就掉正确数——这是一个真实的精度/召回
权衡，不是实现缺陷。**

另外有两条**方法学污染**必须一起写，否则结论会被高估：
- Rules-Only 是**英文 GDPR 句经德语合同 classifier 槽的 pass-through**（跨语言
  适用限制）；
- `first-valid-span` 投影**只取每字段第一个有效 span**（属衔接适配规则）。
  （`docs/research/S3_EXT_UNIFIED_EVALUATION_NOTE_2026-09-06.md` §4 L89–92）

### 2.4 引入 LLM 可行吗——可行，但要卡住"证据可得性"，不是"检测能力"

`INFERENCE`（基于 §2.3 的三段失败链）：

LLM 能做的是**补第一段和第二段**，而不是直接判违规：
1. **把 condition 变成可计算对象**：现在规则侧 `conditions` 是**原文 span**
   （见 §3.2 例），没有任何谓词结构，所以
   `required_condition_not_enforced` 在数学上无法判定。让 LLM 输出结构化条件
   （谓词 + 参数 + 类型：时限/阈值/存在性/授权），这一项是可验证的；
2. **语义等价比对**：把 BPMN 侧 `conditionExpression`、timer、data object、
   boundary event 归一化到同一谓词空间，让 LLM 判**蕴含**而非相似度阈值；
   LLM-SE 在 action（0.9437 vs 0.8927）和 constraint（0.7427 vs 0.6182 粗）
   上已经证明它在同类比对上有优势（`paper/THESIS_DRAFT.md` §7.2 L687–697）；
3. **"不可观测"判断本身应当成为可学习决策**：当前是固定规则 + 事后 reason。
   本项目已经试过四值判定（satisfied/violated/unknown/not_applicable，分离
   `applicability` 与 `evidence_status`，`docs/PROJECT_AUDIT.md` L27），但 H 臂
   被判定为**有已知实现缺陷、方法验收不通过**（27 条
   `unconditional_bypass_branch`，静态遍历否定其绕过结论，L56–60）。

**必须先补的前置**（否则 LLM 会把"判断不可能"变成"编一个判断"）：
- 条件谓词 schema（谁定义、如何 hash、如何校验）；
- 一个条件真值校准集（人工判过的"该流程是否满足该条件"实例），否则无法区分
  "漏检"与"条件本身不可判"；
- 诚实约束：LLM 的每条判定必须附 BPMN 侧可回指的原文/元素 ID，否则退回黑盒。

**建议的第一步（`PROPOSAL`）**：只做 1 类（`required_condition_not_enforced`），
只报**第一阶段指标**——"从规则文本成功合成可计算条件的比例"（现在这个数字是
0），**不报违规 F1**。这个指标零争议、可离线判、且直接暴露瓶颈。若该比例上不去，
后续 F1 讨论没有意义。

---

## 3. 每个阶段的输入 / 输出（含真实实例）

### 3.1 Stage 1：BPMN → Process Record

**输入**（真实文件）：
`formal_experiment/data/input/stage1_stage3/gdpr7/gdpr_{1..7}_*.bpmn`，
BPMN 2.0 XML，7 个流程；首个文件
`gdpr_1_data_breach.bpmn`，byte_size 72747，
sha256 `578204666b669c109cec40eb9468c8a80ec2fb7a9261288628789daac1089e17`
（见 `data/gold/stage1/process_records/stage1_process_gold_v1.json` 的
`records[0].source`）。

**输出**：`process_record@1.0.0`。真实字段清单（同一文件 `records[0].
structure_annotation.gold_process_record`）：

```text
schema_version, process_id, source{input_id, path, sha256, byte_size,
  bpmn_namespace}, method{name, parser_version, label_semantics},
pools[], lanes[], activities[], events[], gateways[], sequence_flows[],
control_flow{...}
```

每个元素的真实值（节选，已去除 PowerShell 对象展开）：

```json
"activities": [{"id":"sid-0F3D7191-...","name":"Notify national authority","type":"task"}, ...]
"events":     [{"id":"sid-337FA953-...","name":"Data breach occurred","type":"startEvent"}, ...]
"gateways":   [{"id":"sid-2A55ADCB-...","name":"","type":"parallelGateway"}, ...]
"sequence_flows":[{"id":"sid-1FC7DEFC-...","source_ref":"sid-2A55ADCB-...",
                   "target_ref":"sid-CC421101-...","condition_expression":"","is_default":false}, ...]
```

**语义标签**（Stage 1 的第二条输出，与结构分离）在同一 record 的
`label_annotations`（135 个人工裁决字段 / 7 流程 / 45 activities）。

**Stage 1 的"语义"到底标了什么——用真实活动名说明**（这是论文里最直观的一段）：
`gdpr_1_data_breach` 的 6 个 activity 是 `Notify national authority`（task）、
`Retrieve breached subjects`（task）、`Data loss limitation`（subProcess）、
`Handle delay`（subProcess）、`Communication with data subject`（subProcess）、
`Retrieve breached data`（task）；2 个 event 是 `Data breach occurred`（startEvent）
与 `Management of \ndata breaches\n completed`（endEvent，**注意标签里有换行符**——
这正是后来导致 Winter/Sun 匹配分数从 0.2828 跳到 0.4833 的那个空白问题，
`PROJECT_AUDIT.md` L154–156）；2 个 gateway 都是无名 `parallelGateway`。
**lane 名与 pool 名的区别是 Stage 3 actor 检测的根本约束**：pool 名可观察
（`Data Controller`），但 7 个流程的 **lane 名全为空**——所以 actor 语义只能来自
participant，`Winter`/`BM25` 的 actor 检测因此恒为 0（§3.3、§7.4.6）。

**规模与正式结果**（`paper/THESIS_DRAFT.md` §7.1，L640–672）：

| 方法 | 语义 micro F1 | Accuracy | Triple 准确率 |
|---|---:|---:|---:|
| P0 结构基线 | 0.0000 | 0.0000 | 0.0000 |
| P1 简单规则 | 0.5956 | 0.4241 | 0.0000 |
| P2 模型上下文+依赖+style recognition | **0.8185** | **0.6928** | **0.4222** |
| structure micro F1（共享解析组件） | 1.0000 | — | — |

**必须一起写的边界**：descriptive component evaluation，`held_out_
generalization_claim_allowed=false`、`target_labels_seen_during_development=true`、
`developer_blind=false`（L669–672）；`structure micro-F1=1.0` 只证明 BPMN→记录
结构转换无错，**不是泛化证据**。

### 3.2 Stage 2：规范文本 → Rule Record

**输入 A（主实验，EStG-150）**：
`formal_experiment/data/input/estg150_formal_inference_input_v2.json`，
`schema_version=estg150_formal_inference_input@2.0.0`，`count=150`，
`membership_payload_sha256=8573e105...`，`claim="Gold-blind executable model input;
NO adjudication content"`。**每条记录只有 6 个字段**（真实样例）：

```json
{
  "sample_id": "estg_000002",
  "language": "en_translated_from_de",
  "raw_text_de": "Buchführende Land- und Forstwirte und protokollierte Gewerbetreibende (§ 5) dürfen jedoch ...",
  "approved_text_en": "Bookkeeping farmers and foresters and registered traders (Section 5) may, however, have a business year deviating from the calendar year; ...",
  "input_text_sha256": "8f8c2f1de5e7a609bc7f714c771b4a1a374a9a3ec42e9d76cae6d573f6ded314",
  "source_ref": {"german_source": "data/development/estg/estg_selected_150_de.jsonl",
                 "layer_e_record": "data/development/human_review/estg_150_human_correction_v1.json",
                 "legacy_record_id": 2},
  "provenance": {"adjudication_fields_excluded": true, "gold_visible": false,
                 "source_layer": "A (raw German) + E approved English text"}
}
```

**输入 B（Stage 3 的规则输入）**：GDPR Articles 5–50 纯文本
（`references/winter_2020_model_check/model_check/input/regulations/gdpr/
article{5..50}.txt`），经人工裁决成
`data/gold/stage3/gdpr7_gold_rule_records_v1.json`
（`gdpr7_gold_rule_record@1.0.0`，`is_gold=true`，74 条 sentence / 92 条规范项）。

**输出**：`stage2_prediction.schema.json@1.0.0`。真实 Gold 实例
（`data/gold/stage2/estg150_formal_gold_v1.json`，`records[0]`，同一 sample_id）：

```json
{
  "sample_id": "estg_000002",
  "approved_text_en": "Bookkeeping farmers and foresters ... in which the business year ends.",
  "clauses": [{
    "clause_id": "estg_000002_c01",
    "clause_span": {"start": 0, "end": 272, "text": "Bookkeeping farmers ... ends."},
    "modality": "obligation",
    "actors":  [{"id":"estg_000002_c01_sp001","start":12,"end":56,
                 "text":"farmers and foresters and registered traders"}],
    "actions": [{"id":"estg_000002_c01_sp003","start":152,"end":271,
                 "text":"the profit shall be taken into account in determining the income for that calendar year in which the business year ends"}],
    "conditions":[{"id":"estg_000002_c01_sp002","start":83,"end":136,
                 "text":"have a business year deviating from the calendar year"}],
    "constraints": [], "exceptions": [],
    "actor_action_map": [], "order_relations": []
  }],
  "decisions": {"translation":"accepted","modality":"edited","actor":"edited",
                "action":"edited","condition":"edited",
                "constraint":"rejected","exception":"accepted"},
  "source_hashes": {"layer_e_record_sha256": "f9433f3e..."}
}
```

**要把三条"工程语义"写进论文**（这是与前人真正不同的地方）：
1. **`text == source_text[start:end]` 是硬不变量**（`prompt` 规则 7；
   `sun_compat/direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md` L47–48）；
2. **空 = absent，不确定 = `unsupported_or_ambiguous`**（同文件 L74–82，
   reason 是受控字符串）；
3. **modality 的 label 与 evidence span 分离**（L54–56；
   `gdpr7_gold_rule_records_v1.json` 里 `modality.evidence` 是单独数组）。

**正式结果**（`paper/THESIS_DRAFT.md` §7.2，L683–697；粗 Gold，5 字段 F1）：

| 方法 | actor | action | condition | constraint | exception | mean | label acc / macro-F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Rules-Only | **0.8203** | 0.8927 | 0.7738 | 0.6182 | **0.8800** | 0.797 | 0.7400 / 0.7128 |
| LLM-SE | 0.7579 | **0.9437** | **0.8380** | **0.7427** | 0.7619 | **0.8088** | **0.8333** / 0.7695 |
| Rules+LLM-Repair（对照） | 0.4296 | 0.8945 | 0.7774 | 0.6200 | 0.8800 | 0.7203 | 0.8200 / **0.8123** |

**结论必须写成"无整体胜者"**（字段级互有胜负，禁止显著性推断）。

### 3.3 Stage 3：Rule Record × Process Record → Violation Report

**输入三件套**：
1. Rule Record（`data/gold/stage3/gdpr7_gold_rule_records_v1.json`，
   `gdpr7_gold_rule_record@1.0.0`，74 条，真实样例见下）；
2. Process Record（§3.1 输出；Stage 3 消费 action 名、actor 名、可达关系）；
3. 参数 `(τ, γ, ϑ) = (0.8, 0.8, 0.8)`（预注册）。

真实 Rule Record 条目：

```json
{ "sample_id":"gdpr_article15_s001", "rule_id":"article15", "sentence_idx":0,
  "char_span":[0,278], "review_state":"human_confirmed",
  "sentence_text":"The data subject shall have the right to obtain from the controller confirmation ...",
  "clauses":[{
     "clause_id":"gdpr_article15_s001.c1", "item_id":"gdpr_article15_s001.p1",
     "clause_span":{"start":0,"end":277},
     "modality":{"label":"permission",
                 "evidence":[{"text":"shall have the right","start":17,"end":37}]},
     "actors":[{"id":"gdpr_article15_s001.c1.actor.1","text":"The data subject","start":0,"end":16}],
     "actions":[{"id":"gdpr_article15_s001.c1.action.1","start":41,"end":157,
                 "text":"obtain from the controller confirmation as to whether or not personal data concerning him or her are being processed"}],
     "conditions":[], "constraints":[], "exceptions":[],
     "actor_action_map":[{"actor_id":"...c1.actor.1","action_id":"...c1.action.1"}]
  }]}
```

**输出**：`stage3_prediction@1.0.0`（两个 task：`matching` / `violation`）。
真实输出行（`outputs/development/gdpr_3type_linkage_v1_reference/
predictions.jsonl`，row 1）：

```json
{ "task":"violation", "item_id":"v001",
  "process_id":"gdpr_1_data_breach", "rule_id":"article33",
  "check_type":"missing_action",
  "missing_action_score": 1.0, "incorrect_actor_score": 0.0,
  "out_of_order_score": 0.0,
  "predicted_violation_type": "missing_action",
  "incorrect_actor_observable": false,
  "incorrect_actor_reason": "action_mapping_below_gamma",
  "scores": {"missing_action":1.0, "missing_action_denominator":10,
             "incorrect_actor":0.0, "incorrect_actor_denominator":0,
             "incorrect_actor_observable":false,
             "incorrect_actor_reason":"action_mapping_below_gamma",
             "out_of_order":0.0, "out_of_order_denominator":0},
  "method_provenance":"sun_2024 Def5-7 gamma=0.8 theta=0.8; arm=reference; ...",
  "threshold": 0.8, "gold_visible": false,
  "source_hashes":{"process_record":"gdpr_1_data_breach","rule_record":"article33"} }
```

**Gold 形态**（`data/gold/stage3/stage3_violation_gold_v1.json`，
`stage3_formal_gold@1.0.0`，33 条）：每条 `{item_id, process_id, rule_id,
check_type, decision_violation_type, decision_evidence}`，例：

```json
{"item_id":"v001","process_id":"gdpr_1_data_breach","rule_id":"article33",
 "check_type":"missing_action","decision_violation_type":"missing_action",
 "decision_evidence":"Art 33(1) obliges the controller to notify the supervisory authority without undue delay after becoming aware of a breach; candidate: is the notification activity present after breach detection?"}
```

**正式结果**（33 条人工 panel，`paper/THESIS_DRAFT.md` §7.4.2，L756–761）：

| 方法 | Missing-action F1 | Incorrect-actor F1 | Out-of-order F1 | Macro-F1 | Exact | Unobservable |
|---|---:|---:|---:|---:|---:|---:|
| Winter wrapper | 0.9524 | 0.0000 | 0.1667 | 0.3730 | 0.3333 | 0 |
| Sun Stage 3 重建 | 1.0000 | 0.1667 | 0.0000 | 0.3889 | 0.3636 | 10 |
| BM25 | 1.0000 | 0.0000 | 0.0000 | 0.3333 | 0.3333 | 11 |
| TF-IDF/SVD | 1.0000 | 0.6250 | 0.0000 | 0.5417 | 0.4848 | 6 |

以及**必须一起报**的阈值发现：Sun 迁移配置 (0.8,0.8,0.8) Macro-F1 **0.3889**，
本文数据上 best-observed (0.8,**0.6**,0.8) Macro-F1 **0.8733**、exact 0.7879、
unobservable 10→4（`paper/THESIS_DRAFT.md` §7.4.7，L886–901）。措辞只能用
"tested values 中的 best observed setting"，禁止称"全局最优 / Sun 固定阈值 /
held-out 最优"（L903–914）。

---

## 4. Prompt 三模块消融：现有数字、冗余诊断、排列组合方案

### 4.1 现有实测（`outputs/reports/d1_prompt_factorial_results_v1.md` L5–27）

同一模型 `DeepSeek-V4-Pro-0813`、同一 150 条输入、同一 Gold、同一 evaluator；
450/450 calls，1,444,632 输入 token，368,212 输出 token，**成本 $3.3650**，
3329.1 秒，失败 0。

| 条件 | P | R | F1 | ΔF1 | 合法率 |
|---|---:|---:|---:|---:|---:|
| 完整方法（6 个合成语义示例） | 0.8203 | 0.7289 | 0.7719 | — | 1.0000 |
| 语义示例 → 纯结构模板 | 0.7808 | 0.7498 | 0.7650 | **−0.0069** | 1.0000 |
| 去掉详细语义规则（规则 9–19、25–27） | 0.8306 | 0.7280 | 0.7759 | **+0.0040** | 1.0000 |
| 去掉显式 JSON 纪律（规则 1–5 + 契约引文） | 0.8221 | 0.7403 | 0.7790 | **+0.0071** | 1.0000 |

逐字段 ΔF1（L14–18）：

| 条件 | modality | actor | action | condition | constraint | exception |
|---|---:|---:|---:|---:|---:|---:|
| 语义示例→结构模板 | +0.0047 | **−0.1317** | −0.0038 | +0.0231 | −0.0034 | +0.0303 |
| 去掉语义规则 | −0.0003 | +0.0463 | **−0.0518** | +0.0146 | +0.0182 | +0.1059 |
| 去掉 JSON 纪律 | +0.0139 | −0.0161 | +0.0234 | −0.0093 | +0.0036 | **+0.1136** |

臂定义见 `prompts/sun_compat/ablation_v2/manifest.json` L14–37（含每臂
sha256 与 `source_prompt_sha256=3aa64877…`）。

### 4.1b 三模块的**精确体量**（真实计费 prompt token，来自每臂 `raw_responses.jsonl` 的 `usage`）

| 臂 | calls | prompt tok/call | Δ vs full | 计费 USD | USD/call |
|---|---:|---:|---:|---:|---:|
| `D-full-0813` | 150 | 4,380.6 | — | 1.35147804 | 0.009010 |
| 语义示例 → 结构模板 | 150 | 1,893.6 | **−2,487.0（−56.8%）** | 0.88316052 | 0.005888 |
| 去掉详细语义规则 | 150 | 3,622.6 | **−758.0（−17.3%）** | 1.19667372 | 0.007978 |
| 去掉显式 JSON 纪律 | 150 | 4,114.6 | **−266.0（−6.1%）** | 1.28519952 | 0.008568 |
| **合计** | **450** | — | — | **3.36503376** | **0.007478** |

三臂成本相加 = 3.36503376，与报告值逐分一致（按峰时价 $1.32/M 输入 cache-miss
+ $3.96/M 输出核算，属保守门禁价）。

**这张表本身就是"冗余"的第一个量化证据**：模块体量相差近 10 倍
（2,487 : 758 : 266 tokens），但 ΔF1 的量级几乎相同（−0.0069 / +0.0040 /
+0.0071）。**如果三个模块各自携带独立的必要信息，删掉 57% 的 prompt 与删掉 6%
的 prompt 不应该产生同量级的效果。**

### 4.2 你的怀疑是对的：**模块之间确实信息冗余**，而且有五条可引用的证据

**证据 0（最强，逐字重复）：模块之间不是"语义相似"，是字面重复。**

| 模块 A 的原文 | 模块 B 的原文 | 位置 |
|---|---|---|
| 规则 17：`{"field":"actor","reason":"reference_status=unresolved_coreference;independence_status=context_required"}` | Example 1 输出 | baseline L85 ↔ L172，**逐字符相同** |
| 规则 27：`a constraint inside a condition (for example "within two years" inside "if ... within two years")` | Example 6 的 input 与输出 | baseline L123–124 ↔ L330–331，**同一对字符串** |
| 规则 18："passive clause … Emit actors=[] and map each expressed action with actor_id=null" | Example 2 标题即 "passive clause without an expressed actor"，输出 `"actors": []` + 两条 `actor_id: null` | L86–88 ↔ L191、L202–205 |
| 规则 25："legal references (… **in accordance with X** …)" | Example 5 的 constraint 就是 `"in accordance with Section 11(1)"` | L112–117 ↔ L302 |
| 规则 11 + 规则 26："Exclude modality, condition, constraint…" / "MUST NOT be folded into the action span" | Example 5 标题："obligation with legal-reference constraint (**constraint is NOT part of the action**)" | L62–64、L118–120 ↔ L285 |
| 规则 3："schema_version = \"1.0.0\"; method.name = \"direct_llm\"…" | 六个示例逐个原样输出 | L36–37 ↔ L151、L169 |
| 规则 5：`validation` 的完整字面量 | 六个示例原样输出 | L39–40 ↔ L170 |
| 规则 2：8 个顶层键的枚举 | 每个示例都是该键集的完整实例 | L33–35 ↔ L150–173 |

**证据 1（最强）：结构模板臂自己就"复述"了另外两个模块。**

`prompts/sun_compat/ablation_v2/direct_llm_no_semantic_examples_prompt_v2.md`
L127–171 的"纯结构模板"里有：

```json
"label": "<obligation|prohibition|permission|definition>"   ← modality 4 类枚举
"actor_action_map": [{"actor_id":"<actor id or null>","action_id":"<action id>"}]
"actions": [], "conditions": [], "constraints": [], "exceptions": []   ← 六个字段名与互斥
{"text": "<exact substring>", "start": 0, "end": 0}          ← text==source[start:end]
```

- `actor_action_map` 的 `actor_id`/`action_id` 成对结构**本身就说明了**
  "actor 与 action 必须建立关联"→ 这就是语义规则规则 21 的内容；
- 四个**互不相同的**数组名**本身就说明了** condition/constraint/exception 是
  三个独立字段 → 这就是规则 26/27 的内容；
- `<exact substring> + start/end` **本身就说明了**坐标回指 → 这就是规则 7；
- modality 的枚举**本身就说明了** 4 类标签 → 这就是规则 9。

**所以"语义示例→结构模板"这一臂并没有抽掉 JSON 纪律，也没有抽掉字段语义的
全部信息，它只抽掉了"字段边界的语言示范"。** 这与观测完全一致：合法率仍
1.0000，只有 actor 大掉（−0.1317，因为 actor 的"代词提及也是 actor""被动句
不推断 actor"这两条只能靠例子示范）。

**证据 2：JSON 臂的零效应是"被示例兜住"的直接结果。**
`manifest.json` L30–36 明确写：该臂"removes the explicit contract introduction and
numbered rules 1–5 … keep all semantic rules and **all six examples**"。
六个示例里每一个都是合法 JSON，键名、枚举、坐标全部示范到位。因此合法率保持
1.0000、F1 反而 +0.0071（少了一段与控制流无关的文本）是可以预期的，
不是"纪律没用"。**该臂的构念是"显式文字纪律的增量"，不是"JSON 纪律的增量"。**

**证据 3：逐字段 ΔF1 呈现"此消彼长"而非"同步下降"——这是再分配指纹。**
六个字段 ΔF1 之和：

| 臂 | Σ ΔF1（6 字段） | 解释 |
|---|---:|---|
| 语义示例→结构模板 | **+0.052** | 几乎不损失总量 → 纯再分配，actor 掉 0.132 而 exception/condition 补回 |
| 去掉语义规则 | **+0.132** | 总量还略增 → 语义规则的主要作用是**分配**而不是**提供**信息 |
| 去掉 JSON 纪律 | **+0.129** | 同上，且 action/exception 上升最多 |

**注意口径**：`Σ ΔF1` 只在同一 6 字段集合内做诊断性比较（各字段分母不同，
不是严格守恒量），**不得**写成"信息守恒定律"，只能写成"再分配指纹"。

**证据 4：模块之间的信息重复有三种可分辨的形式**（`INFERENCE`，但每条都能指
到原文）：
- **定义重复**：规则 13（constraint 定义）↔ 规则 25（constraint 五类清单）；
  规则 11（action 排除 condition/constraint/exception）↔ 规则 26 ↔ 规则 27
  —— 同一约束在**三条规则**里各写一遍
  （`direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md` L62–71、L111–125）；
  规则 12 ↔ 规则 27 第一句；规则 17 ⊂ 规则 16；规则 15 与 18 都重述空数组约定；
  规则 7（`text==source[start:end]`）被规则 24（"all spans are exact"）重述；
- **结构重复**：结构模板 ↔ 规则 1–5（JSON 纪律）↔ 规则 24（final self-check）
  —— JSON 合法性被**三处**约束；
- **模块 A 自我重复**：同一条"不得把 condition/constraint/exception 并进 action"
  写了 **3 遍**（规则 11、26、27）；
- **计算耦合（会掩盖模块效果）**：所有字段共用一套 `text==source[start:end]`
  校验链。任何臂若把 span 边界搞坏，**整个 patch 被 fail-closed 拒绝**
  （`ABLATION_MATRIX.md` L111：`−canonicalizer` → 149/150 invalid → **F1 = 0**）。
  于是"轻微退化"与"完全失效"之间没有中间态，模块的真实贡献被**放大成 0/1**。

**证据 5：仓库里已经写下了冗余假设，只是没有量化。**
`MASTER_PIPELINE.md` L1145 的 AB-5b 行，"回答的问题"一栏字面就是：
> 明文输出纪律在示例已给出格式时是否仍有增量

以及 `outputs/reports/d_no_fewshot_interface_diagnosis_v1.md` L36–41：
> **目前不能单独归因"few-shot 提升语义理解"，因为示例同时演示了字段语义和精确
> JSON/坐标格式。**

**但仓库里没有任何地方量化过模块间的重叠，也没有任何排列组合设计**
（`MASTER_PIPELINE.md`、`ABLATION_MATRIX.md`、`PROJECT_AUDIT.md` 全文搜索
`冗余|redundan|collinear|interaction|组合消融|排列|combinatorial|全因子` 无命中，
"冗余"一词只用于描述 Barrientos 的 44 模式）。**所以 §4.4 的 Step 0/Step 1
是真正的新工作。**

### 4.2b 解读时必须一起写出的四个混杂与限制（否则结论会被审稿人推翻）

| # | 问题 | 证据 | 影响 |
|---|---|---|---|
| 1 | **"去掉详细语义规则"臂同时删掉了一个小节标题** | 基线 L93 `Clause, coordination, and relation rules:` 被删，但规则 20–23 保留 → 规则 20–23 悬空在规则 8 之后 | 该臂**不是**干净的"只删规则 9–19、25–27"，与 manifest 的 `operation` 措辞不符 |
| 2 | **规则 27 与本文 Gold 的定义直接冲突** | 规则 27 断言 `to the extent that` ⇒ condition；但 Gold 把 `"to the extent necessary"` 归 **constraint**（`B0_ERROR_ANALYSIS.md` §8.3：cue `to the extent` → gold-condition 14 / gold-constraint 2；`MASTER_PIPELINE.md` L1003–1004） | **在 prompt 里加更多 cue 规则在这个边界上是会掉分的**，"加更多人工推理"不是无条件正收益 |
| 3 | **本批没有测 modality 4 类 label 准确率** | `evaluation.json` 写着 `"modality_policy": "evidence_span_extraction_only_label_ignored"` | 表里的 `modality` 行是 **evidence span 的 F1**，不是分类准确率；**不得**据此声称 modality 分类结论 |
| 4 | **每臂只有 1 次固定顺序的 150 条运行，无重复、无乱序、无 seed** | 每臂只有 `repeat-01`；样本按输入文件固定顺序（`estg_000002 … estg_000861`），四臂相同；runner 无 shuffle 逻辑 | 项目自己已标为 "single fixed 150-record run per deletion arm; descriptive module effects, not significance"；§4.4 的全因子方案若要报交互项，**必须**补重复或至少补乱序 |
| 5 | **示例资产与实际渲染不一致** | `prompts/sun_compat/direct_llm_few_shot_fixtures.json`（6 条）中第 1–4 条的输入与真实渲染的六个示例**不同**（如 fixtures 第 4 条 = "The controller shall first assess the risk, then notify the supervisory authority."，而渲染的 Example 4 是 definition 句）；渲染逻辑是取原文 `## Examples`…`## Notes` 之间的**原始文本**（`scripts/run_direct_llm.py` L116–128） | fixtures JSON 只是 schema 校验用构建产物；**论文若引用"6 个合成 fixture"应指向 prompt 内的六个示例，不是那个 JSON** |
| 6 | **prompt 文件自身有两处旧标注残留** | 文件头 `version: 5`、标题 `# Direct LLM Sun Record Prompt v5`（而文件名是 v6，L4、L9）；用户模板 L137 与 Notes L345 写 "these **four** synthetic examples" 而实际是六个（已在 `MASTER_PIPELINE.md` 3.6.30 更正过，但残留仍在） | 写作前应修掉或加脚注，避免审稿人抓 |


### 4.3 还要注意一个更根本的原因：**当前消融没有抽掉"信息"，只抽掉了"边界"**

三个臂都没有改变**任务定义**：
- 语义示例臂仍给了全部 6 个键 + 枚举；
- 语义规则臂保留规则 1–8、20–24 与**全部六个示例**；
- JSON 臂保留全部语义规则与**全部六个示例**。

也就是说，模型在每一臂里都能从**至少一个载体**得到需要的信息。这正是"消融不
独立"的操作定义：**只要模块 A 与模块 B 冗余，删 A 的效果就会被 B 兜住，
单因素实验测到的是"删 A 之后的残差"，不是"A 的贡献"。** 这是排列组合消融
（factorial）在方法上正确的直接理由，不是"想多跑几组"。

### 4.4 排列组合消融方案（`PROPOSAL`，未授权、未执行）

**Step 0（零 API，1–2 小时）：先量化冗余，不花钱。**
产出四张表（前三张全新，第四张已可直接从 §4.1b 填入）：
- 每个模块的**行数 / 字符数 / 实测计费 token 数 / 占全 prompt 比例**（§4.1b 已有）；
- 模块两两之间的**词法重叠与 n-gram 覆盖率**（模块 A 的关键短语有多少同时出现
  在模块 B）——§4.2 证据 0 已手工找出 8 处逐字重复，这一步把"逐字重复"扩展成
  "近似重复"的量化；
- **字段 × 模块的覆盖矩阵**（哪个模块为哪个字段提供了哪种信息）；
- **实测 ΔF1 矩阵**（§4.1 已有）。

这张矩阵要放进论文，它本身就是"为什么单因素消融不显著"的解释，**比 F1 更能
说服审稿人**。

**Step 1（零 API）：先做信息守恒精简，把冗余合并成"单一载体"。**
目标：得到 `L`（精简版）——每个字段的每个语义约束在 prompt 里**只出现一次**。
要求与 F 在 Step 0 矩阵上"字段覆盖等价"。精简的候选（基于 §4.2 证据 4）：
- 删规则 13（保留更完整的规则 25），或反之；
- 规则 11 的"排除"从句、规则 26、规则 27 合并为一条；
- 规则 1–5 与规则 24 合并为一条（两处都在说 JSON 合法性与自检）；
- 六个示例**不删**，但把其中重复示范的字段边界去重（例如示例 5 与规则 25
  都在示范 legal-reference constraint，可只留一处）。

**Step 2（真实 LLM，需新授权）：在精简集上跑 2³ 全因子。**

> **重要：当前没有任何可用于消融的预授权预算。** 唯一的活跃授权是 2026-09-07
> 的"论文收尾"137 calls（Batch A S2.12 = 63、Batch B GDPR = 74），其授权句**逐字
> 写明**"任何新的收费调用均不在本次137次授权内"（`configs/
> paper_winddown_api_authorization_sentence_2026_09_07.txt`）。而且这 137 次是
> **按 payload hash 钉死**的（`configs/gdpr7_direct_llm_authorization_event_v1.json`
> 的 `hash_set`），新 prompt 会产生不同请求体，执行器会在第一次发送前硬停止。
> 137 次目前**一次都没花**（`outputs/development/gdpr7_direct_llm_v1/
> manifest.json`：`transport: fake_payload_locked`、`cost_usd: 0.0`、
> `real_authorized: false`）。
> 450-call 消融那一批有自己的授权（`outputs/reports/
> d1_prompt_factorial_authorization_event_v1.json`，suite
> `S2-D1-PROMPT-FACTORIAL-001`，USD cap 13.430），**已用尽**。

**成本估算（`INFER`，按真实 token 增量与 $0.007478/call 加权）**：

| 方案 | calls | 峰时 | 闲时 |
|---|---:|---:|---:|
| 只补缺失的 4 个交互格（−A−B, −A−C, −B−C, −A−B−C） | 600 | ≈ **$3.4** | ≈ $1.7 |
| `F` vs `L` 全因子（2 因子 × 2 水平 = 4 臂） | 600 | ≈ $3.4 | ≈ $1.7 |
| 完整 2³（8 臂，含复用 F 作为 1 臂 → 7 臂新跑） | 1050 | ≈ **$6.0** | ≈ $3.0 |
| 含重复（8 臂 × 3 次）以支持交互项推断 | 3600 | ≈ $20 | ≈ $10 |

（成本是可靠的：token 可加性是分词器性质。但**分数不可加**——这正是本实验要测的
东西，所以成本可估、预期不可预设。）

需要的新资产（`AGENT_RUNBOOK`/`AGENTS.md` 要求）：新 suite ID、新
`*_execution_contract_v*.json`（绑定 commit、臂清单、模型、采样、hash、
`ceil(peak_cost × 1.2)` 余量的预算）、新预算报告、**新的逐字用户授权句 + 授权
event**、以及新的臂构建脚本（现有 `scripts/build_d1_prompt_factorial_arms_v2.py`
只构建 v2 的三臂）。

**Step 3：预注册解释规则**（必须先写下来再看数据，否则事后解释没有价值）：

| 观察 | 结论 |
|---|---|
| F、L 都出现"任一因子都无效应" | 存在共同冗余载体，信息不由三模块中任何一个独占 |
| F 无效应、L 出现显著效应或交互项 | 冗余确实掩盖了贡献；写"冗余是消融不显著的原因" |
| F、L 都出现显著主效应且无交互 | 模块近似独立，原单因素结论成立，只报原结论 |
| 出现显著交互项（如 `rules × examples`） | 必须报交互，禁止报"平均主效应" |

**Step 4（零 API 的替代方案，若预算不足）**：用 **L8(2⁷) 正交表**只跑 8 臂中的
一组正交子集，在成本不变的前提下可分离 3 个主效应 + 若干二阶交互（牺牲三阶
以上）。三因子时全因子就是 8 臂，正交表不省；因此三因子直接全因子，正交表留给
未来扩展到 4 个以上模块时使用。

**Step 5：逐字段预注册预期效应**（避免事后挑字段讲故事）：

| 臂 | 预注册预期（若有真贡献） |
|---|---|
| −语义示例 | actor Δ ≈ −0.10 ~ −0.15（现测 −0.1317 ✅） |
| −语义规则 | action Δ ≈ −0.05，exception/condition 可能转正（现测 action −0.0518 ✅） |
| −JSON 纪律 | 合法率下降，或 action 结构错误上升（现测合法率不变 ❌ → 判定为"被示例兜住"） |

---

## 5. Prompt 还能怎么提升（人工是怎么想的）

从项目已有的 error analysis 与 Gold 原文反推人工判据，下面是**可直接加进
prompt 的具体内容**（每条都给了真实 Gold 依据，`PROPOSAL`，需走授权 pilot）：

### 5.0 先看现有六个示例覆盖了哪些 cue 家族（直接决定"该补什么"）

直接清点 v6 的 `## Examples`：

| cue 家族（规则 25/27 声明） | 六个示例里示范了几次 |
|---|---|
| legal reference（`in accordance with`） | **1**（Example 5） |
| temporal（`within N`） | **2**（Example 2 `within 72 hours`、Example 6 `within two years`） |
| duration（`for N`） | **1**（Example 2 `for 5 years`） |
| quantity（`at least` / `at most` / `no more than` / `in such a quantity that`） | **0** |
| purpose（`for the purpose of`） | **0** |
| exclusivity（`only` / `solely` / `exclusively`） | **0** |
| condition（`if`） | **2**（Example 1、Example 6） |
| condition（`unless`） | 作为 exception 示范（Example 3） |
| 多条件并列 | **0** |
| `order_relations` 非空 | **0**（六个示例**全部**是 `[]`） |

**结论**：规则 25 声明 5 个 constraint 家族，示例只示范了 2 个（legal reference +
temporal/duration）；规则 21–23（order_relations / 并列）**完全没有示范**。
**这正是"加内容"的最优位置**——它是三个模块里唯一**不能**从其它模块反推的部分
（见 §4.2 证据 0），而覆盖率恰好最低。详见 §5.2。

### 5.1 字段边界的"最小充分"原则（针对最弱的 constraint，302/1055 占比最高）

先从项目自己的错误分析取数（`docs/D1_ERROR_ANALYSIS.md`）：

- D1 整体 P=0.907 / R=0.665 / F1=0.767；354 个漏抽 Gold span 中 **constraint 占
  215 个（61%）**，其中 **99 个内容其实被抽到了（落进 action span）**、91 个完全
  没抽、16 个进了 condition（§1 L10）；
- 只把 124 个"已抽到但落错字段"的内容归位，constraint R 就从 **0.288 → 0.699**（§1 L12）；
- R3 逐字段失败类型：**constraint 302 gold spans → matched 133 / wrong_field 100 /
  not_extracted 69**（§8 L115–122）；
- **一条必须更正的旧说法**：`D1_ERROR_ANALYSIS.md` L36 写"few-shot 中 constraint
  仅出现 1 次、condition 出现 0 次"——那是 **v4 时代的 prompt**。我直接清点 v6：
  **constraint 出现在 3 个示例（4 个 span）、condition 出现在 2 个示例（2 个 span）、
  exception 1 次**。所以"示例里没有 constraint/condition"这个理由**在 v6 上已不成立**，
  不能再作为 5.2 的论据；真正的缺口是 **cue 家族的覆盖不全**（见 §5.0）与
  **`order_relations` 零示范**。

| 现 prompt 的说法 | 人工实际怎么判（Gold 依据） | 建议加入的措辞 |
|---|---|---|
| 规则 25：constraint 含"the marker and the smallest complete limit" | `estg_000002`：`"have a business year deviating from the calendar year"` 判为 **condition**；`"the profit shall be taken into account in determining the income for that calendar year in which the business year ends"` 判为 **action**（含 that 从句），constraints **空** | 明确"**当限定从句是动作成立的前提状态时归 condition；只有当它限制已适用动作的 how/how much/where/by when 时才归 constraint**" |
| 规则 11：action 含"necessary object, complement, or particle" | `estg_000578`：action 边界在 `"the employee shall pay to the employer the amount required to cover the wage tax"` 处**截断**，`"to the extent that it is not covered by the cash wage"` 归 constraint；`"If the wages consist wholly or partly of non-cash benefits …"` 归 condition | 加入**同一句的完整切分示范**（现在六个示例都是短合成句，没有"长句三段切分"的例子） |
| 规则 27：condition/constraint 可同时报 | `estg_000635`：`"Upon request"` 判 condition；`"for the purpose of determining the tax circumstances …"` 判 constraint | 保留规则 27，并把本句作为**真实（非合成）示范**——但**必须声明它不是 150 条测试集成员、也不是 Gold 回读**（治理约束：禁止读 Gold 反向调 prompt） |

### 5.2 "限定 vs 报告"的区分（这些边界现在完全没有规则）

Gold 里反复出现但 prompt **一个字都没写**的模式：

| 模式 | Gold 依据 | 建议规则 |
|---|---|---|
| `for the purpose of X` / `to ascertain Y` | `estg_000599`：`"for the purpose of determining the tax circumstances …"` → constraint；`estg_000601`：`"any information"` 与 `"to ascertain their tax situation"` → **两条** constraint | "目的状语归 constraint，且当目的由两个不连续片段表达时**分别列出**" |
| `indicating/specifying + 列举` | `estg_000635`：`"indicating the amount of the capital yields and the tax amount, the payment date, and the period …"` → constraint | "`-ing` 分词列举式补充说明归 constraint，不并入 action" |
| `shall not apply` / `does not apply` | `estg_000786`：action = `"does not apply"`，condition = `"as long as the sponsoring undertaking suspends the contribution payments"`，modality = **definition**；`estg_000800`：condition = `"as long as …"` | "`shall not apply / does not apply` 是**动作**；`as long as / if …` 引入 condition；**整句可能是 definition 而非 prohibition 或 obligation**" |
| 后置条件从句 | `estg_000713`：两个 `if …` 从句 → **两条** condition；`estg_000812`：`"For commercial enterprises (Section 2) that are required to keep books …"` 与 `"for trading and business cooperatives"` → **两条** condition | "同一句的并列适用条件**逐条列出**，不合并" |
| 法条引用 | `estg_000800`：`"(Section 4(4) no. 2 of the Income Tax Act 1988)"` → constraint | 已有规则 25 覆盖，但可加入"括号形式引用也归 constraint" |

### 5.3 反例（negative few-shot）——当前 prompt 完全没有

`paper/THESIS_DRAFT.md` §8.1 L955–968 记录：`"to the extent"` **同时**命中
`to<<an|the` 与 `to<<extent|purpose` 两个 tregex（44 个同界双发中 43 个为双
tregex），且 Gold 自身对 `that/who/to the extent/only` 的 condition/constraint
标注**内部不一致**。Gold 侧的 cue 一致性统计
（`docs/B0_ERROR_ANALYSIS.md` §8.3）：`that` 6 condition / 5 constraint；
`who` 3/2；**`to the extent` 14/2**；`only` 2/3；`when` 3/1；`after` 1/1。

> ⚠ **加 cue 之前必须先处理这个冲突**：prompt 规则 27 断言
> `to the extent that` ⇒ **condition**，但本文 Gold 把
> `"to the extent necessary"` 判为 **constraint**
> （`MASTER_PIPELINE.md` L1003–1004；`B0_ERROR_ANALYSIS.md` §8.3）。
> **按规则 27 写得更"明确"反而会掉分**，因为它与自己的 Gold 约定相反。
> 正确做法是先决定这个边界的归属（改 prompt 还是改口径），再谈加 cue。

这正是一个高价值反例：

```text
反例：不要把模态动词本身、也不要把它管辖的动词短语的宾语并列项当作 constraint。
反例：当 "to the extent that" 引导的是动作成立的前提时归 condition；
      只有当它限定已适用动作的程度范围时才归 constraint。
反例：被动句中未出现的执行者不得推断为 actor；不要从上下句或法律常识补 actor。
```

最后一条已经在规则 18 里有正面表述（L86–88），但**没有反例示范**。

另外，Sun Table-4 收敛实验已经给出了**可用的双口径 cue 表**
（`docs/B0_ERROR_ANALYSIS.md` §10 L250–253，逐字取自论文）：
condition = `if` / `in case of` / `provided that` / `in the context of` / `who` /
`whose` / `which`；constraint = `before` / `after` / `at least` / `at most` /
`equal to` / `greatest` / `smallest` / `last of` / `least of`。用这套 cue 收敛后，
Gold condition 214→92、constraint 302→**13**，Rules-Only 的
**constraint R 0.526→1.000 (13/13)、condition R 0.762→0.989 (91/92)**。
**这张表可以直接作为"人工是怎么想的"的权威依据写进 §5.1**，比自造 cue 更安全。

### 5.4 加入"两遍自检"（当前规则 24 只是单遍 checklist）

建议把规则 24 拆成**两次独立扫描**：
- 第一遍只查"六个字段是否各自最小充分"；
- 第二遍只查"action 是否吞并了 constraint/condition/exception"。

理由：`paper/THESIS_DRAFT.md` §8.2 L1011–1025 显示 constraint 的历史失败是
`wrong_field 169（其中 constraint 100）+ not_extracted 154（其中 constraint 69）`，
两类失败**机制不同**（吞并 vs 漏抽），单遍 checklist 无法同时覆盖。

---

## 6. 论文名字

### 6.1 导师的意见在证据上成立

项目的实际数据源横跨四种规范类型，**不都是"法律条文"**：

| 语料 | 规范类型 | 语言 | 规模 | 来源 |
|---|---|---|---|---|
| EStG（德国所得税法） | **税法/法条** | 德 → 英 | 150 条记录 | `data/input/estg150_formal_inference_input_v2.json` |
| GDPR Articles 5–50 | **条例/regulation** | 英 | 74 句 / 92 规范项 | `data/gold/stage3/gdpr7_gold_rule_records_v1.json` |
| GDPR-7 BPMN 流程 | **流程模型**（非规范文本） | 英 | 7 流程 / 45 活动 | `data/gold/stage1/.../stage1_process_gold_v1.json` |
| S2.11 复杂语料 | **业务/系统需求（requirements）** | 英 | 36 条固定 ID | `data/gold/stage2/s2_11_complex_corpus_formal_gold_v1.json` |
| 官方 modality 数据 | 句子级四分类 | **德** | 2,831 行（1985/420/426） | `docs/research/SUN_MODALITY_DATASET_INGESTION.md` |

S2.11 的语料来自 **Barrientos et al. (2026)**，其对象是 regulatory
**requirements** 的变更影响，不是法条本身。所以标题若写"法律条文/法条"，会
**比实际内容更窄**；导师的判断是对的。

### 6.2 已锁定的术语资产（改名时必须保持一致）

- 构件名：`Process Record` / `Rule Record` / `Violation Report`
  （`MASTER_PIPELINE.md` §5「统一中间合同」）；
- 方法名：**Rules-Only / LLM-SE / Rules+LLM-Repair**
  （`paper/THESIS_DRAFT.md` L8–10；`configs/methods.json`）；
- 任务名：`design-time compliance checking`；
- 禁止表述：不得称 "exact Sun"/"Sun original"，只能称
  `method-level independent reconstruction`；Gold 只能称
  `LLM-assisted, human-adjudicated Gold`。

### 6.3 题目候选（推荐 A）

**A（推荐）：面向设计时流程合规检查的规范文本结构化解析与可验证规则表示：
分阶段方法比较与受控重建**

英文：*Structured Parsing of Normative Text into Verifiable Rule Representations
for Design-Time Process Compliance Checking: A Staged Method Comparison*

理由：把"法规"换成中性的**"规范文本"**，覆盖法条/条例/需求三类；把真正的
方法贡献（**结构化 + 可验证**，即 verbatim span 契约 + fail-closed 回指）放进
副标题；"分阶段方法比较"保留了三阶段比较的主张。

**B：设计时流程合规检查中规范文本的语义解析与违规检测：从规则方法到大语言
模型的分阶段实证研究**

英文：*Semantic Parsing of Normative Text and Violation Detection for
Design-Time Process Compliance Checking: A Staged Empirical Study from
Rule-Based Methods to Large Language Models*

理由：更"实证研究"取向，适合期刊；把 LLM 放进标题。

**C（保守，改动最小）：面向设计时业务流程合规检查的规范语义解析：传统方法、
大语言模型与混合方法的分阶段比较**

**D（方法论取向）：可验证的规范—流程对齐：设计时合规检查中的证据契约、受控
重建与分阶段消融**

> **一个必须做的写作决定**：正文第 1 段应显式定义 **normative text** 的范围
> （statutes / regulations / policies / contracts / requirements），并说明本文
> 实例覆盖其中的 statute（EStG）、regulation（GDPR）与 requirement（S2.11）。
> 这样标题的通用性才有正文支撑，否则只是换词。

---

## 7. 如何在论文中强化"与已有方法的不同"

**先说一件必须知道的事**：`paper/CLAIM_EVIDENCE_MATRIX.md` 里**没有任何一条
以正证据等级声明本文方法的新颖性**；C26（8+8 模块）状态是 `PLANNED_METHOD`，
并明确禁止写"模块有效性已验证（待 AB-1–AB-10 正式消融）"（L38）。所以"强化
自己的不同"当前**不是写作问题，是证据问题**：先补 §4.4 的消融，再写主张。

### 7.1 可直接写成"我们 vs 前人"的十条差异（每条附证据）

| # | 前人做法 | 本文做法 | 证据 | 强度 |
|---|---|---|---|---|
| 1 | 谓词用**子串包含**（`if a.lower() in paragraph`） | 强制 `text == source[start:end]` + **fail-closed 唯一精确文本重锚** | Winter `Pair.py` L117；prompt 规则 7；`ABLATION_MATRIX.md` L111（删 canonicalizer → 149/150 invalid、F1=0） | 强（有负对照） |
| 2 | modality = **4 个 signalword 的句子筛选**（`shall/must/should/may`） | 4 类 **label 与 evidence span 分离** + 非 LLM 分类器 + LLM 对照 | Winter `signalwords.txt`；`THESIS_DRAFT.md` §7.2 | 强 |
| 3 | 匹配 = **spaCy 相似度 + 固定 γ**；本文迁移 γ=0.8 时 Macro-F1 仅 0.3889 | 全文报告阈值敏感性；γ=0.6 时 Macro-F1 0.8733（并明确标为 tested-values best-observed） | `THESIS_DRAFT.md` §7.4.7 L886–901 | 强（但必须写清 DEV_ONLY/33 条） |
| 4 | 只报 3 类违规 | 3 类 + **4 类最小字段覆盖扩展**，exactly-one-error 合成注入 | §7.4.1 L734–752；§7.4.4 | 中（四类结果混杂，须如实报 0.083 的条件类） |
| 5 | 官方包**没有 Stage 2 源码**（包内就是 Winter 原型） | **可审计的方法级独立重建**（11 元素 crosswalk、Tsurgeon 诚实非实现 + fail-closed 守卫） | `SUN_WINTER_CODE_SEPARATION_AUDIT.md`；`B0_R2_METHOD_CROSSWALK.md` | 强（是"前人做不到"的诚实边界） |
| 6 | 只报 strict JSON 合法率 | 加**逐字段坐标级重锚**：重锚 966 spans、恢复/改变 **149/150** 样本、action F1 **+0.0095** | `ABLATION_MATRIX.md` L45–52 | 中（overall 仅 +0.0024，须一并写） |
| 7 | few-shot 未声明与测试集隔离 | **Gold-blind 合成 fixture + 与 150 条零交叠的机器门禁**（exact/ws/casefold/punct 全 0） | `MASTER_PIPELINE.md` L1098–1099、changelog 3.6.25 | 强 |
| 8 | 单一口径 | **粗/细双 Gold 口径 + Sun-marker 收敛**三口径分表 | `ABLATION_MATRIX.md` L120–129 | 中 |
| 9 | 成本/延迟事后统计 | **逐批授权 + `--max-calls` 硬停止 + manifest 记 llm_calls/max_calls** | `MASTER_PIPELINE.md` L1108–1109；`PROJECT_AUDIT.md` L447–465 | 弱（工程治理，明确不做消融，`RESEARCH_EVIDENCE_REVIEW` L400） |
| 10 | 各自报总数 | **matched / wrong_field / not_extracted 三类错误归因** | 1055 gold spans：matched 732、wrong_field 169（constraint 100）、not_extracted 154 | 强 |

### 7.2 写法建议

1. **不要用单一 F1 宣称整体更优**——跨任务/跨 schema 属 C4，禁止
   （`ABLATION_MATRIX.md` L32–33；`CLAIM_EVIDENCE_MATRIX.md` C18）。
2. **用"能力维度表"替代"总分表"**：把上表做成 10 行的"能力 × 谁有 × 证据"，
   这比 F1 更难被反驳。
3. **把负结果写成方法学贡献**：Rules+LLM-Repair 的净负（粗 F1 0.7621 vs
   0.7986；actor P 0.7077→0.2754）→"**无足够证据约束的选择性 LLM 修复会产生
   净负收益**"，这是可发表的结论，且比又一篇"LLM 更好"更有价值。
4. **诚实披露清单**（审稿人会查）：`no_multi_match_guard` **+0.0053**（去掉
   守卫反而变好）、`no_de_en_alignment_validation` **+0.0000**、
   三个 D 臂 canonical 非空率 **0.000**、`Σ ΔF1` 是再分配指纹不是守恒量。

---

## 8. 一页版行动清单

| 优先级 | 事项 | 需要什么 | 预计成本 |
|---|---|---|---|
| P0 | §4.4 Step 0：prompt 冗余机器量化（模块 × 字段覆盖矩阵 + 两两 n-gram 重叠 + 已测 token 体量表） | 零 API，纯离线 | 1–2 小时 |
| P0 | §4.4 Step 1：信息守恒精简 → 得到 `L` | 零 API | 半天 |
| P0 | §1.5：Winter 义务动作集合对比（Stage 2B 的可比层） | 零 API（复用 `winter_stage3`） | 1 人日 |
| P0 | §4.2b：修掉 4 个混杂项（悬空规则 20–23 的标题、规则 27 与 Gold 冲突、v5/"four examples" 残留、fixtures JSON 与实际渲染不一致） | 零 API，改 prompt 与文档 | 半天 |
| P1 | §4.4 Step 2：`F` vs `L` 全因子（缺失 4 格 600 calls ≈$3.4；完整 2³ 1050 calls ≈$6.0） | **需新的用户授权句 + 预算合同；当前无任何可用于消融的授权** | 约 $3.4–6.0 |
| P1 | §2.4：`required_condition_not_enforced` 的"条件合成率"单一指标 | 零 API（离线判） | 1 人日 |
| P1 | §6.3 题目定稿 + §7.2 能力维度表 | 写作 | 1 人日 |
| P2 | §5：prompt 补边界规则与反例，走授权 pilot（**注意 §4.2b 第 2 项，加 cue 有掉分风险**） | 需 API 授权 | 约 $1/臂 |
| P2 | §1.5 第 2 项：signal-word modality 下限 | 零 API | 半天 |
| P3 | 端到端 E00/E10/E01/E11（当前**完全没有任何产物**） | 离线 runner 不存在，需先实现 | 数人日 |
| P3 | S3.7 正式 Oracle 主表 | 需授权句 + 门禁链 | 待定 |

**当前唯一硬阻塞**：真实 API 的**进程环境凭据缺失**（`PROJECT_AUDIT.md` L356
"预检 5 项 FAIL，含 API key absent"）。已授权未执行：batch A 63 calls、
batch B 74 calls（L652、L659）；这两批**不含**任何消融调用。

---

## 9. 本文件没有做的事

- **唯一改动 = 创建本文件**（`formal_experiment/docs/research/`，属研究材料，
  不在 `dot-points` 或门禁路径上）；未运行任何测试或实验；未调用任何 LLM/API；
- 未读取 `formal_experiment/.env`；
- 未改 Gold、prediction、manifest、合同或门禁；
- **未提交、未推送**：工作区在本次会话前已有未提交改动
  （含 `formal_experiment/data/development/human_review/
  stage1_gdpr7_human_correction_v1.json` 的修改，以及若干 `.bak`/probe 文件与
  `paper/presentations/bpc_hybrid_revised_20260912.pptx`），按工作区规则
  **未做 blanket staging**。当前分支 `codex/b0-r1-a-span-boundaries`，
  upstream `origin/codex/b0-r1-a-span-boundaries`，HEAD `8e7beff`。
  是否把本文件与既有改动一起提交，请用户决定；
- 所有 `PROPOSAL` 项均**未执行**，且涉及真实 LLM 的项**未获授权**
  （§4.4 Step 2 当前没有任何可用预算）。

## 10. 一句话回答你原来的八个问题

1. **前人对比**：Winter 不是 Stage 2 的前人（他只有 4 个 signalword），但
   Sun 在 Stage 3 唯一对比的前人**就是** Winter；补法是把 Winter 的**义务动作
   集合**接到 Stage 2B 做可比层对比。更强的发现：**Sun 自己也没有 Stage 2B 的
   前人对比**，这是领域空白（§1.4）。
2. **三类违规的成因**：那三类**就是** Winter `Pair.py` 里恰好写下的三个成本函数
   （`cost_obligation`/`cost_resource`/`cost_so`），而 Sun 官方包里 Stage 3 就是
   Winter 原型。机制上，三类是"Rule Record 已解析字段 × BPMN 可观察表面"的闭包
   （§2.1–2.2）。其他类型"效果差"的三段真实原因 + 引入 LLM 的可行路径见 §2.3–2.4。
3. **每阶段输入输出**：三阶段各自的真实 schema、真实数据实例、现有指标与必须
   一起写的边界，见 §3；论文可直接引用。
4. **论文名字**：导师的意见在证据上成立（数据源横跨税法/条例/需求三类）；推荐
   §6.3 候选 A（"规范文本结构化解析与可验证规则表示"）。
5. **强调自己的不同**：10 条可写成"我们 vs 前人"的差异，每条带证据与强度评级，
   见 §7.1；**但要先知道 `CLAIM_EVIDENCE_MATRIX.md` 里目前没有任何一条以正证据
   等级声明新颖性**，这是证据问题不是写作问题。
6. **prompt 提升**：六个示例只示范了 5 类 constraint cue 中的 2 类、
   `order_relations` **零示范**——这是最优加料位置；同时有 4 处会掉分的坑
   （§5.0、§5.3、§4.2b）。
7. **三模块是否冗余**：**是**，而且已找到 8 处**逐字重复**；体量相差 10 倍
   （2487 : 758 : 266 tokens）却产生同量级 ΔF1；消融测到的是"残差"不是"贡献"。
   排列组合方案见 §4.4，成本仅 $3.4–6.0，但**当前无授权**。
8. **为什么只有三类 + LLM 可行吗**：见第 2 条；LLM 的切入点不是"判违规"，而是
   **把 condition 合成可计算谓词**（现在这个比例是 0），见 §2.4。
