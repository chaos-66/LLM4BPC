# BPC 与 LLM 参考文献阅读顺序

**截至 2026-10-12：清单共 18 篇，已取得并核验 15 篇 PDF；05、06、17 暂缺全文。**

目录：`D:\Paper\experiment\LLM4BPC\references\papers\BPC_LLM_Related_Work`。按文件名升序即可依重要性从上往下阅读；缺失编号用“获取说明.md”保留位置。

排序针对当前 LLM4BPC 论文：与方法主线和对照直接相关的工作先读，LLM 语义抽取及合规近邻随后，再读支撑技术、综述和经典形式化方法。编号表示阅读优先级；不是引用量或论文质量排名。

## 建议读法

- 先精读 01-04：Sun 的方法主线、Winter 的比较基线、Barrientos 的 LLM+BPC 近邻和 De Jure 的规则抽取。05-06 是重要近邻候选，获取全文后补读。
- 再读 07-10：语义字段依据、法规规则识别、提示模板、法规变更研究。11-12 重点读与语义匹配相关的技术。
- 13-18 按写作需要查阅；2008 年的 17 是早期形式化检查路线，当前优先级很低。它并非因新近性而入选，而是来自用户清单的历史背景文献。

## 按重要性排列

| 顺序 | 论文 | 重要性与阅读重点 | 本地文件 / 版本 |
|---|---|---|---|
| 01 | Design-time business process compliance assessment based on multi-granularity semantic information (2024) | **必读：方法主线**。先读框架图和多粒度语义定义，再读规则模板、规则与流程匹配、违规检测与评价；逐项区分继承内容和本项目改动。 | [作者稿（原有本地文件）](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/01_Sun_2024_Design-time_BPC_multi-granularity_semantic_information.pdf>) |
| 02 | Assessing the Compliance of Business Process Models with Regulatory Documents (2020) | **必读：比较基线**。关注法规文本与流程模型的匹配、角色和活动语义、覆盖度与成本的定义；用于明确 Part 3 比较基线的能力范围。 | [作者稿](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/02_Winter_2020_Assessing_compliance_of_process_models_with_regulatory_documents.pdf>) |
| 03 | Impact analysis of regulatory requirement changes on business process compliance (2026) | **必读：LLM 与 BPC 近邻**。重点读需求表示、LLM 结构化输出、验证与规范化，以及下游流程影响分析；区分法规变更任务和本项目固定需求的检查任务。 | [期刊正式版（原有本地文件）](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/03_Barrientos_2026_Impact_analysis_of_regulatory_requirement_changes.pdf>) |
| 04 | De Jure: Iterative LLM Self-Refinement for Structured Extraction of Regulatory Rules (2026) | **必读：LLM 规则抽取近邻**。重点看结构化规则表示、迭代自我修订、质量判据和评价方式；与 LLM-SE 的一次抽取及确定性后处理比较，注明这是预印本。 | [arXiv v1 预印本；稿件标注 Under review](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/04_Guliani_2026_De_Jure_LLM_self-refinement_for_regulatory_rule_extraction.pdf>) |
| 05 | Leveraging LLMs for Automated Compliance Risk Identification in Business Processes (2025) | **必读候选：直接 LLM 合规检查**。出版商摘要描述从管理规范生成流程三元组，再对齐实际流程并识别风险；全文未取得，先读公开摘要，取得后核对实验与提示词。 | [暂缺 PDF，见获取说明](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/05_Wang_2025_LLMs_for_automated_compliance_risk_identification_获取说明.md>) |
| 06 | Extracting Declarative Constraints for Process Modeling from Natural Language Descriptions with Large Language Models (2026) | **必读候选：LLM 约束抽取**。公开摘要和元数据表明任务是自然语言到 Declare 约束；取得全文后重点核对约束方向、模板范围、提示与微调、评价方式。 | [暂缺 PDF，见获取说明](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/06_Park_2026_Extracting_declarative_constraints_with_LLMs_获取说明.md>) |
| 07 | Automated Extraction of Semantic Legal Metadata Using Natural Language Processing (2018) | **精读：语义要素设计依据**。关注法律语义元数据的概念模型、字段定义、句法抽取规则和案例评价；帮助说明 Part 2 要素抽取的来源与边界。 | [作者接受稿 / postprint](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/07_Sleimi_2018_Automated_extraction_of_semantic_legal_metadata.pdf>) |
| 08 | Identification of Decision Rules from Legislative Documents Using Machine Learning and Natural Language Processing (2022) | **精读：法规决策规则识别**。关注税法文本、情态表达、决策规则分类和机器学习识别；区分句子分类与细粒度语义要素抽取。 | [HICSS 会议全文（原有本地文件）](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/08_Michel_2022_Identification_of_decision_rules_from_legislative_documents.pdf>) |
| 09 | Towards Taming Large Language Models with Prompt Templates for Legal GRL Modeling (2024) | **精读：领域提示模板**。阅读如何把法律概念和 Legal GRL 建模知识写进提示模板；可借鉴模板设计思路，区分目标模型生成与 Rule Record 抽取。 | [出版商正式版，机构库附封面](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/09_de_Kinderen_2024_Prompt_templates_for_legal_GRL_modeling.pdf>) |
| 10 | Taming the Complexity of Legal Change for Business Process Compliance (2026) | **选读：法规变更与研究定位**。先读法律变更到 BPC 的研究梳理，再看 LegalChanges4BPC 的提示和评价；帮助描述近邻研究与任务差异。 | [期刊正式版（CC BY），机构库附封面](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/10_Barrientos_2026_Taming_complexity_of_legal_change_for_BPC.pdf>) |
| 11 | Sentence-BERT: Sentence Embeddings Using Siamese BERT-Networks (2019) | **方法引用：语义匹配**。重点读句子向量、句对相似度和余弦匹配的原理；用于理解 Part 3 的语义匹配，不把语义相似直接等同于合规成立。 | [ACL 会议正式版](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/11_Reimers_2019_Sentence-BERT.pdf>) |
| 12 | MPNet: Masked and Permuted Pre-training for Language Understanding (2020) | **方法引用：编码器基础**。了解 masked/permuted 预训练的动机；这篇介绍 MPNet 基础模型，具体句向量模型和本项目配置还需引用对应模型资料。 | [NeurIPS 会议正式版](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/12_Song_2020_MPNet.pdf>) |
| 13 | Are we done with business process compliance: state of the art and challenges ahead (2018) | **背景综述：按需查阅**。先读分类框架和研究挑战；虽然发表于 2018 年，其综述检索主要覆盖 2000-2015 年，不能作为 2026 年最新进展的完整证据。 | [作者稿](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/13_Hashmi_2018_BPC_state_of_the_art_and_challenges.pdf>) |
| 14 | Evaluation of Compliance Rule Languages for Modelling Regulatory Compliance Requirements (2023) | **背景与表示：按需查阅**。关注合规语言的表达能力、规范性语义和复杂度比较；用于解释结构化抽取与可执行形式化规则的区别。 | [期刊正式版（CC BY），附文章封面](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/14_Zasada_2023_Evaluation_of_compliance_rule_languages.pdf>) |
| 15 | Formalizing and applying compliance patterns for business process compliance (2016) | **经典方法：模式化合规规则**。阅读合规模式和 CRL 的形式化基础；用于说明人工或模板式规范化的背景，与本项目语义抽取作概念比较。 | [作者接受稿，机构库附封面](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/15_Elgammal_2016_Formalizing_and_applying_compliance_patterns.pdf>) |
| 16 | Semantic Business Process Regulatory Compliance Checking Using LegalRuleML (2016) | **经典方法：法律语义表示**。看 LegalRuleML 如何表示规范并支持合规推理；它有助于理解语义表达要求，阅读它不意味着本项目实现了 LegalRuleML 推理。 | [HAL 存档作者稿，附封面](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/16_Governatori_2016_Semantic_BPC_checking_using_LegalRuleML.pdf>) |
| 17 | Efficient Compliance Checking Using BPMN-Q and Temporal Logic (2008) | **低优先级：历史路线**。2008 年的经典工作：把规则表示为 BPMN-Q 查询和时序逻辑，配合流程约简、Petri 网和模型检查验证活动及执行顺序。对 LLM-SE 的直接借鉴有限，可只读摘要与方法总览；全文暂缺。 | [暂缺 PDF，见获取说明](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/17_Awad_2008_Efficient_compliance_checking_using_BPMN-Q_and_temporal_logic_获取说明.md>) |
| 18 | Context is Key for Cybersecurity: Leveraging External Knowledge for Process Model Explanation via LLMs (2026) | **扩展阅读：外部知识与安全领域**。关注流程模型与外部安全知识的结合、上下文提示及解释评价；属于领域扩展，当前写作时间有限时可以最后读。 | [期刊正式版（开放获取）](<D:/Paper/experiment/LLM4BPC/references/papers/BPC_LLM_Related_Work/18_Koelbel_2026_Context_is_key_for_cybersecurity_process_explanation.pdf>) |

## 版本与引用注意事项

- 作者稿、接受稿、机构库封面和预印本均已单列；页数与期刊印刷页数不一致时，通常是版本或封面的差异。保持下载文件原字节，不裁剪封面、不重新生成论文 PDF。
- Sun 当前保存的是原有作者稿；不把它描述为出版商正式版。De Jure 为 arXiv v1 预印本，不据此声称已通过同行评审。
- Elgammal 的用户 BibTeX 写作 “appling”；机构库题名用 “applying”，稿件正文亦可见 “Formalising”。本指南采用机构库题名，原始 BibTeX 按字节保存。
- 2008 年 Awad 的方法是 BPMN-Q 查询、时序逻辑和模型检查，用于检查流程活动及执行顺序；对当前 LLM-SE 的直接方法借鉴有限，建议只读摘要、框架图及与本文相关的段落。[出版商摘要](https://link.springer.com/chapter/10.1007/978-3-540-85758-7_24)。
- 本指南的排序和借鉴建议是针对本项目的阅读判断，未取得全文的 05、06、17 只依据公开摘要/元数据，不伪称完成全文审阅。

## 尚未取得的全文

| 编号 | 当前可核实的情况 | 正式入口 |
|---|---|---|
| 05 | 出版商订阅章节；DOI PDF 地址返回摘要 HTML；未查到可下载公开作者稿。 | [出版商 / DOI](https://link.springer.com/chapter/10.1007/978-981-96-6963-9_32) |
| 06 | 出版商标为非开放获取；PDF 下载 HTTP 403；RWTH / Fraunhofer 记录未提供公开全文。 | [出版商 / DOI](https://www.sciencedirect.com/science/article/pii/S0167923626000163) |
| 17 | 出版商订阅章节；CiteSeer 旧链接归档后 HTTP 404；ResearchGate 作者公开共享 PDF 在当前网络返回 HTTP 403。 | [出版商 / DOI](https://link.springer.com/chapter/10.1007/978-3-540-85758-7_24) |

已按 DOI、精确题名、作者与机构库查找；Google Scholar 的精确题名补查在当前网络返回 HTTP 429（异常流量限制）。这表示本轮无法继续访问 Scholar，并不能证明它没有收录可下载的其他版本。没有购买论文或使用机构登录；未取得的文件保留明确缺口。

## 文献目录操作记录

- 用户在本聊天明确要求：找到所贴清单的 PDF，存入 references/papers/ck，给 ck 改一个合适的名称，并按重要性排序。这是本次目录更名、加入文献和创建阅读索引的授权。
- 已检查原 ck 目录为空，随后在 references/papers 内更名为 BPC_LLM_Related_Work。原有其他文献保持原字节；Sun、Michel、Barrientos 三份现有 PDF 复制后核对 SHA-256 与来源一致。
- 新增 PDF 与获取说明只用于个人文献阅读；不从 references 导入或运行实验代码。文献管理操作不改变 MASTER_PIPELINE、实验状态、Gold、模型配置或已有结果。
- 核验 15 个文件的 PDF 文件头、全部页面解析和文本、首页题名、作者对应及页面数，渲染首尾页；另生成首页检查拼图。SHA-256、下载源、版本与缺失项见 collection_manifest.json。
- 本次属文献/文档整理，仅做文件与内容核验，不运行 audit_project.py、pytest 或任何真实 LLM/API 批次。
- 根 .gitignore 排除了 references/ 和 *.pdf；PDF 仅在本机保存。formal_experiment/literature/reading_list_20261012 的指南、来源 BibTeX 与 manifest 作 scoped Git checkpoint，不上传论文全文。
