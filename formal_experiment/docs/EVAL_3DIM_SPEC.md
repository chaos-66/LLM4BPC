# Part 2 Evaluation Spec (Wave 1.1 v2)

> **版本**：v2 (2026-07-12)
> **依据**：Barrientos artifact 的专家标注协议（不是论文自动方法主表）+ `docs/research/BARRIENTOS_BORROWING_AUDIT_2026-07-12.md` §3.1 的 2026-08-20 来源分层纠正 + Wave 1.1 §5 修正
> **目的**：定义 Part 2 输出的评估指标体系，包括主指标、3 维度的准确拆分、和语义等价性测试方式
> **范围**：仅 spec；**不**实现 `three_dim_eval.py`（Wave 2 才开始）
> **配套**：`docs/STYLE_EQUIVALENT_SPEC.md`（评估体系内的 normalization-aware matching 部分）
> **Wave**：Wave 1.1 spec 阶段

---

## 1. 旧版 v1 的错误（必须改的）

旧 v1 的 semantic coverage 定义是 `prediction non-null / 6`，这是**错的**：

* 它把"预测了不存在的字段"算作"覆盖" → **奖励 hallucination**
* 它把"Gold 不要求该字段"算作"漏抽" → **惩罚正确 null**
* 它不能区分"系统决定该字段不存在" vs "系统没找到该字段"

旧 v1 的 structural encoding 把 `TP/(TP+FP+FN)` 称为 **accuracy**——这是**错的**：这个公式是 Jaccard / edge IoU，不是 accuracy。

旧 v1 的 "correct order pairs / predicted order pairs" 只算 **precision**，漏了 recall / F1。

旧 v1 的 clause_id uniqueness 是 **validation invariant**，不是准确率指标——它必须是 1（或者样本拒绝）。

旧 v1 的 deontic 单元是"整句顶层 modality"，这**不对**：multi-clause 句中不同 clause 有不同 modality，单元必须是 clause。

---

## 2. 主指标（必须保留）

这些是 Part 2 的核心指标，**与 Sun 论文保持一致**，便于审稿人对照。

### 2.1 Modality 4 类分类

| 指标 | 公式 | 用途 |
|---|---|---|
| Macro-F1 | 4 类 F1 算术平均 | 主报告数字 |
| Per-class P/R/F1 | 4 类分别 | 哪类最差 |
| Confusion matrix | 4×4 | 哪两类易混 |
| Per-class support | 4 类样本数 | 解释 F1 异常 |

- 4 类固定：`obligation`, `prohibition`, `permission`, `definition`
- 单元：**clause**（不是整句）
- 缺失类（某类 support = 0）规则：F1 = 0、recall = 0、precision = NaN → 报告中显式标 N/A

### 2.2 六要素抽取

每个要素单独算：

| 要素 | 指标 |
|---|---|
| modality | 4 类 macro-F1 + 4 类 P/R + 4×4 confusion（见 §2.1） |
| actor | exact span P/R/F1 + token overlap P/R/F1 |
| action | exact span P/R/F1 + token overlap P/R/F1 |
| condition | exact span P/R/F1 + token overlap P/R/F1 |
| constraint | exact span P/R/F1 + token overlap P/R/F1 |
| exception | exact span P/R/F1 + token overlap P/R/F1 |

exact span = text == gold.text AND start == gold.start AND end == gold.end
token overlap = IoU of token sets (Jaccard)

micro 和 macro **分别报告**：
- micro：所有样本所有 token 一起算
- macro：按样本平均

### 2.3 报告表（主表）

| Method | obl-F1 | pro-F1 | perm-F1 | def-F1 | macro-F1 | actor span P/R/F1 | action span P/R/F1 | ... |
|---|---|---|---|---|---|---|---|---|
| B0 | | | | | | | | |
| H1 | | | | | | | | |
| D1 | | | | | | | | |

主表是 **"primary metrics"**。3 维度（§3）和 style-equivalent（§4）是 **"secondary metrics"**，在副表 / 补充材料里。

---

## 3. 3 维度分项（修正后的定义）

### 3.1 Semantic Coverage（覆盖度）— 必须拆分

旧定义 `prediction non-null / 6` 是错的。新定义拆成 6 个独立指标：

| 指标 | 公式 | 含义 |
|---|---|---|
| **Gold-required presence recall** | (# gold-required fields predicted) / (# gold-required fields) | **不**漏抽 Gold 要求的字段 |
| **Predicted-field precision** | (# predicted fields that are gold-required) / (# predicted fields) | **不** hallucinate 字段 |
| **Hallucinated-field rate** | 1 - precision | predicted 但 gold 不要求 |
| **Complete-record rate** | (# records where all gold-required fields are present) / (# records) | 整条记录完整 |
| **Schema-valid rate** | (# records passing schema) / (# records) | 记录格式合法 |
| **Unsupported/ambiguous rate** | (# records with non-empty `unsupported_or_ambiguous`) / (# records) | 系统说"不知道"的比例 |
| **Invalid/API-error rate** | (# API errors) / (# requests) | 调用失败率 |

**关键**：Gold 中**不适用的字段**不计入 gold-required。**系统决定不输出**不算 hallucination（如果它在 `unsupported_or_ambiguous` 里说明）。

例如：
- 句 1 是 definition，Gold actors=[]，actions=[]。B0 输出 actors=[]，actions=[]。→ gold-required=0，全部正确
- 句 1 是 obligation，Gold actors=[a1, a2]。B0 输出 actors=[a1]。→ recall=0.5, precision=1.0
- 句 1 是 obligation，Gold actors=[a1]。B0 输出 actors=[a1, a3]（a3 是 hallucination）。→ recall=1.0, precision=0.5

### 3.2 Structural Encoding（结构编码）— 必须改

**不是** accuracy，是 **edge-based**：

| 子指标 | 公式 | 含义 |
|---|---|---|
| **Actor-action edge P/R/F1** | precision/recall/F1 over actor_action_map edges | actor→action 配对 |
| **Order-relation edge P/R/F1** | precision/recall/F1 over order_relations edges | 顺序关系 |
| **Clause segmentation exact-match rate** | (# clauses with exact set of spans matching gold) / (# clauses) | 拆句 |
| **Clause span overlap / IoU** | mean IoU between pred clause_span and gold clause_span | 拆句边界 |
| **Schema-valid rate** | (# records passing schema) / (# records) | （重复列在 §3.1，单列在此） |

`TP/(TP+FP+FN)` 必须命名为 **Jaccard / edge IoU**，不能叫 accuracy。

`correct order pairs / predicted order pairs` 只是 precision，必须补 recall/F1：
- precision = (# correct order pairs) / (# predicted order pairs)
- recall = (# correct order pairs) / (# gold order pairs)
- F1 = 2 * P * R / (P + R)

clause_id uniqueness 是 **validation invariant**，不是准确率：
- 任何一对 clause 内重复 id → 记录 invalid
- 不参与 P/R/F1 报告

**clause/entity 对齐算法**（明确规则）：
- **不**按预测数组位置直接对齐
- **不**要求预测 ID 和 Gold ID 字面相同
- 允许的匹配策略（多选一，spec 锁定）：
  1. **Gold-id first**：Gold 用自己的 actor_id/action_id，预测按 Gold ID 匹配（需要 prompt 输出一致 ID 风格）
  2. **Span-based**：忽略 ID，按 span（text + start + end）与 Gold 对齐
  3. **Hybrid**：先 ID，ID 缺失则 span
- **未决议题**：实现时**只选一种**并明确报告，**不**混合多策略
- 锁定的默认选择：**Hybrid**（先 ID，ID 不存在时退到 span）

### 3.3 Deontic Correctness（道义正确性）— 单元改

- 4 类固定 labels
- 单元：**clause**，不是整句
- 缺失类（support = 0）规则：F1 = 0、recall = 0、precision = NaN → 报告显式标 N/A
- 每类 support 必须报告（避免 macro-F1 被大样本类拉偏）
- evaluation 范围：所有 gold clause

---

## 4. 报告组合

### 4.1 主表

| Method | obl-F1 | pro-F1 | perm-F1 | def-F1 | macro-F1 | actor span F1 | action span F1 | ... |
|---|---|---|---|---|---|---|---|---|

（见 §2.3）

### 4.2 副表 A：3 维度

| Method | gold-required recall | predicted-field precision | complete-record rate | schema-valid rate | unsupported rate | invalid/api rate |
|---|---|---|---|---|---|---|

### 4.3 副表 B：结构编码

| Method | actor-action edge F1 | order-relation edge F1 | clause seg exact-match | clause span IoU | schema-valid rate |
|---|---|---|---|---|---|

### 4.4 副表 C：deontic 详情

| Method | obl P/R/F1 | pro P/R/F1 | perm P/R/F1 | def P/R/F1 | macro-F1 | per-class support |
|---|---|---|---|---|---|---|

### 4.5 副表 D：normalization-aware matching

见 `docs/STYLE_EQUIVALENT_SPEC.md` §3-4。

**注意**：副表 D 是**敏感性分析**，不是主结果。

---

## 5. Wave 2 实施优先级

1. 主表（§2）最先做
2. 副表 A（§3.1）第二
3. 副表 C（§3.3）第三
4. 副表 B（§3.2）第四（需要 clause/entity 对齐算法决策）
5. 副表 D（§4.5）最后

---

## 6. 仍未解决的设计决策（unresolved）

- **clause/entity 对齐算法**：选择 Hybrid（先 ID 后 span）作为默认
- **缺失类 macro-F1**：F1=0 还是不计入？目前定为 F1=0 + 报告 N/A
- **Part 3 是否需要单独 1 张表**：B0/H1/D1 三组分别送入同一冻结 Part 3，看下游增量。这是另一个 spec（`docs/ROUTE_LOCK.md` 提到）— 跟本 spec 分开

---

## 7. 与 Barrientos 的对比

借鉴：artifact 专家协议的 3 维度（semantic / structural / deontic）+
style-equivalent 概念。Barrientos 论文对自动 RC4PC 的主评价实际是 Step-specific
P/R/F1、strict-JSON 合法性与 36 requirements × 5 次运行的 self-consistency；本 spec
是项目适配设计，不能写成 Barrientos 已直接采用的自动评价器。

不借鉴：
- "output 是什么"（用 Sun 4 类，不用 Barrientos 3 类）
- "哪个类做主类"（Sun 的 obligation / definition 是主类，Barrientos 的 obligation / permission 是主类）
- "评估单元"（Sun 的单元是 clause，Barrientos 的单元是 requirement）

引用方式：
> "We adopt Barrientos et al. (2026)'s 3-dimension evaluation discipline
> (semantic coverage, structural encoding, deontic correctness) and
> the distinction between style-equivalent alignment and partial
> misalignment. We do NOT adopt the RC4PC schema; we evaluate against
> Sun et al. (2024)'s 4-class modality and 6-element extraction."
