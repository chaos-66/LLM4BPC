# 从这里开始：CSCWD 2027 逐节修订阅读包

这是交给网页版 GPT 的论文写作材料包，基于作者上传的六页 2027 原稿。用户要求：借鉴学长学姐论文的结构、把 Related Work 合并进 Introduction、实际引用 18 篇文献、解释清楚 Part 2 后处理，并从头到尾逐节修改。

2026-10-12 起，活动修订使用 Part 1 / Part 2 / Part 3：前两部分独立并行，并共同为 Part 3 提供输入。原稿 PDF、辅助提取文本及阅读包中的原稿附录保留原文；应用候选修订时同步更新原稿图中的展示名称与并行关系。

**最快使用方式：**把 [完整协作提示词](WEB_GPT_PROMPT.md) 复制到网页版对话；模型先读取 [完整文字阅读包](WEB_GPT_READING_PACK.md)，需要核对公式与图时读取 [2027 原稿 PDF](source_2027_CSCWD_16.pdf)。

## 阅读顺序

| 顺序 | 文件 | 用途 |
|---|---|---|
| 1 | [WEB_GPT_PROMPT.md](WEB_GPT_PROMPT.md) | 逐节协作规则、开始方式与每轮输出格式 |
| 2 | [WEB_GPT_READING_PACK.md](WEB_GPT_READING_PACK.md) | 单文件阅读入口：版本与事实边界、全文审阅、替换片段、18 篇 BibTeX、证据入口 |
| 3 | [source_2027_CSCWD_16.pdf](source_2027_CSCWD_16.pdf) | 用户自己的原稿，原样保留；公式、图、表和页码以此为准 |
| 4 | [source_2027_CSCWD_16.md](source_2027_CSCWD_16.md) | 原稿按页、左栏→右栏提取的辅助文字，未修正原稿错误 |
| 按需 | [REVIEW_AND_USE.md](REVIEW_AND_USE.md) | 逐页问题、18 篇引用对应论述、代码核对与修改建议 |
| 按需 | [introduction.tex](introduction.tex) | 合并 Introduction / Related Work 的英文草稿 |
| 按需 | [part2_postprocessing.tex](part2_postprocessing.tex) | 后处理替换稿、历史定位伪代码和合成例子 |
| 按需 | [method_and_evaluation_notes.tex](method_and_evaluation_notes.tex) | 五处独立插入/替换说明，不应整段作为新章节 |
| 按需 | [references_18.bib](references_18.bib) | 18 个文献条目；具体引用位置见审阅表 |

[完整文字包 Raw 入口](https://raw.githubusercontent.com/chaos-66/LLM4BPC/refs/heads/codex/s2-prompt-simplification-v1/formal_experiment/paper/cscwd2027/revision_20261011/WEB_GPT_READING_PACK.md) · [原稿文字 Raw 入口](https://raw.githubusercontent.com/chaos-66/LLM4BPC/refs/heads/codex/s2-prompt-simplification-v1/formal_experiment/paper/cscwd2027/revision_20261011/source_2027_CSCWD_16.md)

## 版本与证据优先级

- 原稿：用户上传的 2027_CSCWD (16).pdf，SHA-256 为 f2ce8d2b020a41e71e56aca175b8568631e5ba1a1beb37a1b815d24641bf1948，6 页。本目录 PDF 是字节一致副本。
- 已有审阅与四个替换文件的基准提交：1f00f155474329a0f73eb5c162688301d5e5414d。本次补充阅读入口、协作提示词、整合包及原稿，不代表原 PDF 已经修订。
- 仓库 2027_CSCWD_formula_corrected.tex 是相关旧源，文字不完全等于这份 PDF。只有作者提供的对应当前源文件才能作为完整替换操作的准确基础。
- 本包里的 TeX 是候选替换稿，尚未整合编译；18 篇引用键和数值已静态核对，不等于最终排版验收。
- 论文事实以对应冻结运行、引用原文为依据；建议可讨论，不能用“按建议改了”代替事实核验。
- 学长学姐的 2025/2026 论文只提供结构参照，结构比较已在审阅中说明。本次没有把他们的出版 PDF 加入仓库。

## 关键事实卡

| 项目 | 本轮应保持的边界 |
|---|---|
| 方法名 | LLM-based Semantic Extraction / LLM-SE；基线 Sun et al. (2024)，简称 Sun，首次说明本地重建；历史 ID 与冻结文件不改 |
| Table I | EStG-150，五个 span 字段 pooled overlap F1：0.8378 vs 0.7631，差 7.47 pp；modality 单列 |
| 指标计数 | 命中预测与命中参考区域分别计数，不是假定共同 TP 的一对一匹配 |
| Table I / II | v6/R3 与 modular_v1 两套提示词快照；111=0.8224 不能冒充主表的同配置重复 |
| 后处理 | 主表用历史唯一精确定位；当前 repair_v1 不能追溯用于解释旧结果 |
| 基线 | 本地 Sun 重建包含 BERT-TextCNN；其分数不是 Sun 原论文值 |
| Table III 原稿 | 0.5341 vs 0.4458，单独 GDPR 开发比较，不能称独立未见测试 |
| 范围 | 抽取六类语义与评估三类违规不同；必须解释具体使用路径 |
| 授权 | 写作、引用、公式说明；不授权新实验、API、Gold 修改或调参 |

## 逐节协作方式

先读材料并识别实际版本，然后按“标题与摘要 → 合并引言 → 问题定义与框架 → 三部分方法 → 实验与局限 → 结论 → 全文一致性”推进。每次只处理一个可完成的小节，输出中文问题解释、中文逻辑、可替换英文/LaTeX、明确替换位置和验收点；等作者反馈后继续。完整约定见 WEB_GPT_PROMPT.md。

这是阅读与写作顺序，不是另建的实验状态表。实验真实状态仍只由项目已有 MASTER_PIPELINE / PROJECT_AUDIT 管理。

## 无法读取链接时

GitHub 文件已推送不等于每个网页版会话都能读取它。若模型报告无法访问、读取被截断或无法看 PDF，先让它明确已读范围。作者可下载并直接在该会话上传 WEB_GPT_READING_PACK.md 与 source_2027_CSCWD_16.pdf；只缺公式片段时，再提供该页或对应 LaTeX。不要让模型用文件名和旧摘要猜全文。

## 补充材料的核验

- 原稿 PDF 副本需保持上述 SHA-256。
- 原稿文字版按页分栏，只辅助定位；公式字符可能失真，不能据此改数学条件。
- 完整文字包中的五个既有修订文件以 UTF-8 原文嵌入，证据入口固定到已存在提交。
- 这次材料准备没有修改实验代码、运行新实验或修改已有结果。

本次静态核验：6 个嵌入文件内容一致；20 个相对链接有对应文件；17 个固定提交证据入口存在；18 个 BibTeX 条目与 18 个实际引用键一致；原稿 6 页且副本 SHA-256 一致。这里只检查文档和来源，不运行实验或代码测试。

目录内 .gitignore 只为作者此次要求交接的原稿 PDF 设置单文件例外；其他学术 PDF 的仓库忽略规则保持有效。
