# 论文案例准备注记：SIM 卡入网（Sun）与 GDPR 下游案例（2026-09-08）

> 状态：**准备完成，待真实结果回填与用户标准答案确认**。本注记为纯离线文献/资产
> 核对产物（零 API、零人工裁决）。案例数字只在真实运行/人工确认后写入论文与主张矩阵。
> 关联任务：2026-09-07 论文收尾指令 §七；资源核对基于只读调研（2026-09-07）。

## 1. 案例 A（优先）：Sun“电话公司获取新客户/SIM 卡”案例 —— 真实来源与版本

**论文来源（版本 of record）**：Sun et al. (2024) *Design-time business process
compliance assessment based on multi-granularity semantic information*（DOI
10.1007/s11227-023-05626-0）。本地证据：
- `references/papers/Sun_2024_Design_time_BPC.pdf`（+ duplicate 副本）；
- 提取全文 `references/papers/extracted/sun_2024_full_text.txt`：
  - §5.4 Case Study：L923–973；场景=电话公司获取新客户流程（引 Agostinelli et al. 2019），
    建模为 Figure 10 流程；
  - Table 13 规则要素（L940–956，排版塌缩文本）：R1 超 30 天必须终止流程；
    R2 收到客户个人信息后必须核验其正确性（义务）；R3 客户收到 SIM 卡时公司必须激活
    （义务，incorrect-actor 示例“由公司而非客户激活”）；R4 GDPR：取得个人数据前先取得
    同意；
  - 违规判定示例 L957–973：R1/R4=missing action、R2=out-of-order、R3=incorrect actor。
- **注意（2026-09-07 调研）**：本地 Sun 副本中**未找到**“欠款客户领取 SIM 卡的禁止规则”
  表述（telecom/arrears/欠款等零命中）——论文若写该例必须以实际文本为准或标注为用户
  补充的业务背景，不得冒充 Sun 原文。
- 官方 supplement：`Decision_Logic_data.zip`（archive.org item input-2，SHA-1
  0346f84a…；本地 raw 目录 gitignored）；`input 2.zip`（57 个 Stage-3 文件）本地**未落盘**，
  仅文档登记（sha 与导师包一致）。两者均不得改写本项目 150 条冻结样本/36 条复杂语料。

**Barrientos SIM_card_scenario 的关系（引用边界）**：
- 语料在 `references/barrientos_2026/.../SIM_card_scenario/`（requirements json +
  bpmn + step1/2/3 ground truth）；活跃记录 r8–r13 × v1/v2（10 条）+ 2 条隔离空文本；
  hash-only 统计 `outputs/reports/s2_11_corpus_membership_v1.json`。
- “Barrientos 流程改自 Sun、不能直接称 Sun 原图”的**逐字出处不存在**；可引证据链：
  (i) Barrientos 论文自述数据集 based on Sun[23]（`references/papers/extracted/
  barrientos_2026_full_text.txt` L1208–1213/L1251；[23] L1895）；(ii) SIM v2 记录与
  Sun Table 13 规则逐词一致 4/4；(iii) Barrientos BPMN 含 Sun 叙事外元素（Ask for
  consent、Debt<100 XOR、portability 子流程等）。论文表述应为“基于上述证据的推论”，
  不得写成 Barrientos 文档自身断言。
- OURS-FULL 消融（`outputs/development/barrientos_ablation_suite_v2/OURS-FULL/
  repeat-01..05`，36 条含 SIM 的真实 LLM 预测，run=barrientos-de-0813-1140-v1，
  2026-08-29 授权）属于另一执行链/claim_scope=development_only，**不能拼入 S2.12
  正式运行**；只能作模块替换/借鉴对照证据引用（含 SIM 真实预测的事实可写）。

## 2. 案例 B（推荐主体，已运行数据）：GDPR 7 流程下游案例（article33/34 主锚点）

- 已冻结资产：7 个 BPMN（`data/input/stage1_stage3/gdpr7/`）、33 条三类 violation
  decision Gold + 25 条 matching Gold（`data/gold/stage3/`，decision-only ≠ Gold Rule
  Records）、9 条款/74 句 Gold-blind 输入（`data/input/gdpr7_stage2_input_v1.json`）、
  Rules-Only 74/74 胶囊（`data/predictions/gdpr7_sun_rule_only_v1/`）、统一口径与修复
  数字（`outputs/reports/s3_extended_unified_v1_*`、`s3_formula_repair_v2.*`）、
  S3.9-EXT 40 对四类扩展面板（DEV_ONLY）。
- 推荐叙事锚点：**article33（gdpr_1_data_breach）**为主案例（义务活动缺失/顺序/执行者，
  Gold v001–v003 + m001），**article34（gdpr_1）**与 **article22 s1 情态翻转**为方法差异
  小案例（统一口径 10/7/8/6 逐样本变化；文章 LINKAGE_RULES_ONLY_RESULTS_NOTE
  案例 a/b/c）。
- 解释结构（分贡献，不预先承诺）：
  1. Sun 方法重建基线是 Rules-Only：在 33 条三类 Gold 上的开发口径表现为
     macro 0.3333 / exact 0.3333；保留跨语言 pass-through 和适配限制。
     reference 确定性抽取（0.3889 / 0.3636）仅作开发诊断，不能当成 Sun 方法臂；
  2. 用 LLM-SE 替换 Stage 2（GDPR 臂待真实运行），对比同配置 Rules-Only 后
     解释最终判定变化及抽取/适配/检测原因（Task D 已提供接口，尚无该臂实验数字）；
  3. 加 Stage 3 四类扩展（S3.9-EXT DEV_ONLY 40 对）在何种意义上扩展覆盖面，受
     可观察性/映射瓶颈限制的如实表述。

## 3. 标准答案（三层，需人工确认——给用户的清单）

**本轮人工编辑入口（2026-09-08 更新）**：用户已要求 AI 先认真预填，再自行检查修改确认。
句子级请直接编辑 `data/development/human_review/gdpr7_ai_prefill_v1/请检查并修改这份预填稿.md`；
案例四项请编辑 `data/development/human_review/gdpr7_case_ai_prefill_v1/论文案例人工核对预填稿.md`。
两者均为待确认候选，不推进人工进度。下表所述 v2 工具是后续导入工具，本轮不要与 Markdown
同时维护两份决定。复合情态/坐标/关系需无损对账后再导入。
案例预填发现延误计时器与主通知期限不能直接等同；原流程局部任务判断与既有三类 Gold 的
检查范围也需确认。故下表“正常对照无违规”是待证明事项，不能仅凭 control 目录名批量确认。

论文案例任何“检出 N/M、漏检、误报、谁更对”都必须有可引用的标准答案。本项目标准答案
分三层，各层现缺项如下：

| 层 | 内容 | 现状 | 需要确认的最少项 |
|---|---|---|---|
| L1 句子级六要素 | 案例句子的 modality/actor/action/… 最终值 | GDPR 74 句裁决面已就绪（v2 工具），**0/74**；Barrientos 36 句已有正式 Gold（可复用，reviewer=hyc，无独立专家背书） | 用唯一编辑入口 `formal_experiment/scripts/gdpr7_review_tool_v1.py --next`（默认 v2 文件 `data/development/human_review/gdpr7_six_element_review_decisions_v2.json`）核对；最小集可先只做案例条款（如 article33 10 句 + article34 7 句 + article22 6 句 ≈ 23 句），其余 51 句不阻塞开发口径比较 |
| L2 流程级违规判定 | 每个待检对象“有/无违规、何类违规” | 33 条三类违规 Gold 可当“违规变体”答案；**“正常对照无违规”无人工 Gold 样本** | 对案例中每个正常对照对象做一次人工 compliant/none 确认（文件级确认事件即可，可逐对象批量给出） |
| L3 争议判定 | 案例中涉及“参考错/Rules-Only 错/LLM-SE 更对”的句 | 未裁决 | 至少 article22 s1 的 modality 终裁（prohibition vs obligation）；裁决前论文只用中性表述“标签不同→可检性改变” |

**用户可直接给出**（哪种形式都行，Agent 只导入不推断）：
1. 选定 1–2 个 (流程, 条款) 作论文案例（推荐 gdpr_1×article33 + article22 s1 小案例）；
2. 用 v2 工具完成对应条款的句子级裁决（或给我一份按 v2 schema 填好的决定文件 + 确认事件）；
3. 对案例用到的正常对照对象确认“无违规”；
4. 争议句（article22 s1 等）的最终裁决。

## 4. 后续写入（不在本注记冒充完成）

- 真实 LLM-SE/Rules-Only 成对下游结果与逐样本差异 → 案例逐条表（检出/漏检/误报/
  流程位置）+ 流程图（自制，基于 `data/input/stage1_stage3/gdpr7/gdpr_1_data_breach.bpmn`
  与冻结 inference pack 规则文本）；
- Sun SIM 案例如需新数据激活/新裁决/额外 API：列出最小依赖并单独申请，不挪用 137 次预算
  （当前判断：SIM 侧 36 句句子级答案已有 Gold，可先做“同一语料下方法与 Stage 3 扩展贡献”
  的复现说明；不承诺全部检出）。
