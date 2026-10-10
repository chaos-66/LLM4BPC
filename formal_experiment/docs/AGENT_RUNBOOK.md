# Agent 分阶段执行手册与 Prompt 库

本文是静态派工手册：规定怎样把主 Pipeline 的任务交给 Agent、怎样验收、什么时候
必须停止。实时状态和当前派工只写在 `PROJECT_AUDIT.md`，本文不建立第二份状态页，
也不改变 `MASTER_PIPELINE.md` 的权威性。

## S3-TABLE3-V4 静态执行入口（2026-09-24 用户选择）

当前修正卡：[`agent_prompts/STAGE3_TABLE3_V4_R1.md`](agent_prompts/STAGE3_TABLE3_V4_R1.md)。
它覆盖初版已确认的实现错误和限定方法调整；原卡/原五次授权不变，不覆盖旧结果。
先 R1-A/B 离线修复冻结，再 C 原五次抽取，D 新版真实诊断；执行进度只见状态页。

完整可转交 Prompt：[`agent_prompts/STAGE3_TABLE3_V4.md`](agent_prompts/STAGE3_TABLE3_V4.md)。
本轮只做实验与数据，Codex 负责设计/验收，用户手动交给现有 DeepSeek Agent 执行。
其中五次固定 LLM-SE 已获用户接受，预算/输入边界按该任务卡，不重复请求旧许可。
本卡覆盖下方与其冲突的历史写作同步、旧 API 计划及通用工作 Agent 权限模板。
为完成强制 checkpoint，执行 Agent 可机械更新本任务的 S3 实时事实/完成状态、
目录与运行日志；这是第 1 节第 3 条的限定例外，不允许自行更改研究路线或其他任务。
当前是否已实施、是否验收，只见 PROJECT_AUDIT；静态 Prompt 的存在不代表已运行。

> **2026-09-14 用户取消决定优先**：不再派发 Rules+LLM-Repair / H1 /
> `sun_llm_fallback` 或规则先行的 LLM 修复/fallback 实验；S2.12 的 F-1/F-2/F-3
> 共 27 次已取消。旧三方法模板和旧授权仅作历史。当前比较为 Rules-Only 与
> LLM-SE，剩余 Direct 36+74=110 次；两方法执行/评价/冻结合同已于 2026-09-14
> 适配（`s2_12_two_method_contract_v1`），取消的组不再是完成依赖，不得伪造完成或
> 挪用调用额度；Direct 真实结果未出现前 completion/freeze 仍为 false。详见 AGENTS 与主 Pipeline 3.7.8。

> **2026-09-12 收尾派工入口**：9 月 30 日导师初稿、10 月 31 日 CSCWD 截止为最晚目标，能提前就提前。
> 固定主线、实质依赖和验收，满足条件即开始、完成即推进；不设阶段起止日或人为实验停止日。
> 发现问题按证据定位、最小修复、相关验证和论文同步的循环处理，只重开受影响部分。
> 当前依赖和验收以 `MASTER_PIPELINE.md` 文首「CSCWD 按依赖推进的收尾 Pipeline」为准，
> 实时任务和下一最小子任务只读 `PROJECT_AUDIT.md`。下方旧双轨路径与历史准备状态是
> 依赖/模板参考，不是重新运行已经完成实验的指令。既有 API 授权持续有效，真实调用按
> 具体合同和账本核验；新 prompt 消融另锁预算。文档/写作不启动实验测试。

## 1. 调度原则

1. 实验轨道一次只推进一个最小任务 ID；默认串行，不因 Agent 空闲而越过依赖。满足真实依赖即推进，不因日期或不相关任务等待；遇到问题在原任务下逐项修复、验证。
2. 论文轨道可以与实验轨道并行，但一次只有一个 Agent 编辑论文正文。
3. 协调 Agent 才能更新 `PROJECT_AUDIT.md`、主 Pipeline、文件目录和实验日志；工作
   Agent 只改自己的明确写入范围，交接后由协调 Agent 收口。
4. 人工审核 S2.2 由用户独占。Agent 只能验证格式、解释工具或导入用户明确提供的
   决定，不能自行接受、编辑、拒绝、标记 reviewed 或 adjudicated。
5. 任何数据缺失、许可不明、hash 不符、依赖未解锁，都应形成精确 blocker；不得
   为“完成任务”伪造数据、状态或论文结果。
6. `integrity_pass=true` 只表示可继续开发；只有相应任务的 Definition of Done 和
   上游门禁全部通过，协调 Agent 才能派发下一任务。
7. 测试范围以两级 AGENTS.md 和 AI_CHANGE_PROTOCOL 第 3 节的 2026-09-10 成本策略
   为准，覆盖旧任务文本中的全量要求。纯制品/文档不跑实验测试；程序改动默认
   具名相关测试。提交、推送、完成批次不触发全量；全量须用户明确授权本轮执行。

## 2. 当前双轨安排

```text
实验轨道（串行）
S2.1-A 来源/许可/原始文件证据
  → S2.1-B 数据合同、schema 与离线 importer
  → S2.1-C 真实 CSV 核查、canonicalization 与 split
  → S2.1-D 自动门禁与状态收口
  → S2.3 → S2.4 → S2.5 → S2.6（完整 B0）
  → S2.7/S2.9 → S2.10
  → G0.5/S2.11 → S2.12 → S2.13
  → Stage 1 + S3.1-S3.3 数据治理 → Stage 3 formal Oracle → 端到端消融

论文轨道（与实验并行）
PW0 骨架/主张账本
  → PW1 引言与研究问题
  → PW2 相关工作
  → PW3 方法设计稿
  → PW4 数据与标注协议
  → PW5 实验设计
  → PW6 空结果表
  → PW7/PW8 正式结果回填
  → PW9 讨论、结论、摘要与终稿
```

当前事实：`Decision_Logic_data.zip` 已在本地通过来源身份核验；S2.1-A、
S2.1-B-R1、S2.1-C-R1 和 S2.1-D 均已 verified，2,831 行 development analysis
population 及其 project-reconstructed split 已由独立机器门禁锁定。许可仍为
`unknown_pending_confirmation`，因此不得再分发、提升为 formal Gold 或直接进入训练/
评价。S2.3 已 verified 并严格停在 public marker resource；S2.4 只有在另行派发且
单独收口许可未知与 ready 的现有矛盾后才能启动。论文 PW1 可以在不写任何结果性
主张的前提下开始。

## 3. 所有工作 Agent 共用的 Prompt 前缀

复制下面的前缀，再追加第 5—8 节对应任务卡。当前任务的完整可复制 Prompt 已在
第 4 节给出。

```text
你是 LLM4BPC 项目的工作 Agent。本轮只执行指定的一个 Pipeline 任务 ID，
不得顺手推进下游任务。

工作区：D:\Paper\experiment\LLM4BPC
所有活动写入只能位于 formal_experiment/。

先完整阅读并服从：
1. formal_experiment/AGENTS.md
2. formal_experiment/docs/MASTER_PIPELINE.md
3. formal_experiment/docs/PROJECT_AUDIT.md
4. formal_experiment/docs/DIRECTORY_GUIDE.md
5. formal_experiment/docs/EXPERIMENT_LOG.md 最新事件
6. formal_experiment/docs/AI_CHANGE_PROTOCOL.md
7. formal_experiment/docs/ROUTE_LOCK.md
8. formal_experiment/configs/experiment_contract.json
9. formal_experiment/configs/methods.json
10. formal_experiment/docs/AGENT_RUNBOOK.md

实验程序修改在批次边界运行快速完整性检查，默认只运行具名相关测试。
纯制品/文档只做内容、渲染及文件检查。完成批次、交接、提交、推送或记录日志均
不触发全量；全量必须有用户对本轮的明确授权并预告原因与耗时，禁止重复运行。
实验变更按 AI_CHANGE_PROTOCOL 记录范围，日志脚本不得因缺少凭证自动跑全量。
不得读取或打印 .env；不得调用真实 LLM/API；
不得自动修改 Gold，不得覆盖正式产物，不得修改 references/、根
archive/ 或 _retired/。

开始前先复述：任务 ID、唯一目标、已满足依赖、输入、写入范围、禁止项和 DoD。
若依赖不满足，停止并给出证据，不得自行解锁。交付时列出：改动文件、相关测试、
验证范围及未覆盖项、产物状态（development/pilot/formal）、仍存 blocker、建议的下一任务 ID。
```

## 4. 当前可直接派发的完整 Prompt

### 4.1 Agent-E1：S2.1-A 官方 modality 数据来源证据

```text
你是 Agent-E1，只执行 Pipeline S2.1-A：固定 Sun 官方 modality 数据的来源、许可
状态和原始文件身份。不要解析标签、生成 split、训练模型或进入 S2.1-B。

工作区：D:\Paper\experiment\LLM4BPC
所有活动写入只能位于 formal_experiment/。

完整阅读 formal_experiment/AGENTS.md 及其 Required Reading，另外阅读：
- docs/research/SUN_FINAL_VERSION_AND_DATA_AUDIT.md
- docs/research/SUN_REFERENCE_SNOWBALL_AND_MARKER_AUDIT.md
- configs/paths.json

修改前运行 `python formal_experiment/scripts/audit_project.py`。

已知证据：
- 官方入口：https://archive.org/details/input-2
- 包名：Decision_Logic_data.zip
- 已记录官方 SHA-1：0346f84a246b7049d5aef58bcb33471435bee106
- 预期成员：EStG_raw.txt、EStG_sent_vec.csv、estg.html
- 当前工作区没有 ZIP 或 CSV 实体。

本轮目标：
1. 核对本地是否已有官方包；没有就明确记录 missing，不得伪造。
2. 只从权威官方页面核对下载身份、文件元数据和许可/再分发状态。许可无法确认时写
   `unknown_pending_confirmation`，不得推断“可正式使用”。
3. 只有在工具权限和当前任务授权允许安全取得官方包时，才把原始开发副本放入
   `data/development/sun_modality/raw/`；绝不写 references/ 或 formal 数据目录。
4. 对实际取得的包和成员计算 SHA-1/SHA-256；已知 SHA-1 不匹配立即停止。
5. 新建 `data/development/sun_modality/source_manifest.json` 和
   `docs/research/SUN_MODALITY_DATASET_INGESTION.md`，记录 URL、获取时间、文件名、
   大小、hash、许可原文/未知状态、当前缺口和下一步。
6. 增加只验证来源 manifest 与原始字节一致性的最小测试。

禁止：不接触 EStG-150 Layer A–E；不把论文的 2,833 条统计当作本地数据；不预设
CSV 列或标签含义；不训练；不调用 LLM；不修改任何 readiness/locked 状态；不宣布
S2.1 完成。

DoD：来源可定位；实际取得文件的 hash 可复核；许可状态诚实；原始数据只在
development；相关测试通过；只能把 S2.1-A 标为 verified。若没有取得官方包，交付
精确 blocker，并保持 S2.1-A 未完成。

完成批次后按 AGENTS.md 选择相关检查、更新文件目录并按需记录中文变更事件；
不得因批次结束自行进入全量测试。
```

### 4.2 Agent-P1：PW1 引言与研究问题

```text
你是 Agent-P1，只执行论文任务 PW1：完善中文引言和 RQ0–RQ4。只允许编辑
formal_experiment/paper/THESIS_DRAFT.md 与 CLAIM_EVIDENCE_MATRIX.md，不修改实验
代码、数据、Gold、配置、主 Pipeline 或实时状态页。

工作区：D:\Paper\experiment\LLM4BPC
先完整阅读 formal_experiment/AGENTS.md、docs/AGENT_RUNBOOK.md、paper/README.md、
paper/THESIS_DRAFT.md、paper/CLAIM_EVIDENCE_MATRIX.md、MASTER_PIPELINE §§2–4、
PROJECT_AUDIT 和 docs/research/。内部研究审计只能作为证据导航；正式文献主张必须
回到本地可核验的原论文。无法核验页码或表号时写 TODO-SOURCE，禁止猜测。

引言必须覆盖：design-time BPC 问题；Stage 1/2/3 关系；Sun 方法的作用和不可得
资产；比较传统方法、paper-faithful Sun 重建、Direct LLM 和 selective Hybrid 的
动机；复杂法律语料是待检验问题而不是既定优势；RQ0–RQ4。

统一占位符：
- [[TODO-RESULT:任务ID：需要回填的结果]]
- [[TODO-SOURCE:文献键：需要核对的原始页码/表号]]
- [[TODO-STATUS:任务ID：完成后把设计时态改为实现时态]]
- [[TODO-DECISION:任务ID：需要冻结的研究决定]]

禁止：不得声称已经 exact reproduction；不得把当前 heuristic 称正式 Sun baseline；
不得声称正式 Gold、正式实验或 LLM 优势已经完成；不得把 EStG-150 写成 Sun 原始
150；不得把 LLM-assisted Gold 写成纯人工 Gold；不得跨数据或跨 Stage 比数字。

DoD：引言形成可读初稿；每个结果性句子都是待检验时态或显式 TODO；新增主张同步
登记到 CLAIM_EVIDENCE_MATRIX；不填任何实验数字。完成后交给只读主张审查 Agent，
由协调 Agent 统一验证和记录。
```

### 4.3 Agent-R1：只读论文主张审查

```text
你是 Agent-R1，只读审查，不编辑文件、不跑全量测试。阅读 AGENTS.md、机器合同、
PROJECT_AUDIT、paper/CLAIM_EVIDENCE_MATRIX.md 和待审章节。逐句检查 planned method
是否被写成 completed、development 是否被写成 formal、是否声称 exact/original
Sun、是否把 LLM-assisted Gold 写成纯人工、是否把 C2/C3/C4 写成 C1、是否提前
声称 LLM 优势、是否混淆 Stage 2/3。按严重度输出“原句—证据问题—安全替换句—
所需 TODO/解锁任务”。不得自行补数字、页码或来源。
```

## 5. S2.1 后续任务卡

以下任务默认串行。即使 S2.1-A 与 S2.1-B 技术上可在不重叠文件时并行，本项目为
降低冲突默认先完成 A，再派发 B。

### S2.1-B：合同、schema 与离线 importer

- 依赖：S2.1-A 的来源事实已固定；真实 CSV 可以仍缺失。
- 写入：`configs/datasets/`、`configs/schemas/dataset_manifest.schema.json`、
  `src/bpc_hybrid/datasets/`、`scripts/ingest_sun_modality.py`、合成 fixtures/tests。
- 目标：标准库 `csv/hashlib` 实现 ZIP/CSV inspect/import、默认拒绝覆盖、显式
  source ID 唯一性、稳定 ID、normalized-text group-aware split、标签冲突 fail closed、
  唯一小类别阈值、独立 SHA-1/SHA-256 核验、确定性 manifest 与 membership hash。
- adapter 边界：`strict_one_hot` 只属于 synthetic fixtures；官方 CSV schema、label
  mode 与整数 0–3 映射全部保持 `pending_s2_1_c`，不得猜测。实现只预留可注入
  label adapter seam，不在 B/R1 中增加官方 integer-code mapping。
- manifest 边界：不含运行时当前时间；`output_files` 只列实际派生数据 child，
  不自列 manifest，不允许 placeholder；manifest 自身 hash 由外部 receipt/日志记录。
- 小类别唯一公式：`active_nonzero_splits * min_per_class_in_smallest_split`，单位为
  normalized-text group；当前阈值 3，低于阈值全进 train 并 warning，不丢类别/样本。
- 边界：所有未知真实列写 pending；fixture 不能冒充官方数据；不改 Gold/readiness；不训练。
- DoD：`--inspect-only` 不写数据；train/dev/test 无交集且并集完整；相同 normalized
  text 不跨 split；同输入/合同/seed 的 records、三个 split 和 manifest 均字节一致。

### S2.1-C：真实官方 CSV 核查与 development 生成

- 依赖：A/B verified；官方 ZIP 已由用户提供或在 A 中合法取得。
- 输入：实际 `Decision_Logic_data.zip`，先核验已知 SHA-1。
- 输出：`data/development/modality/sun_estg_modality_v1/records.jsonl`、manifest、
  versioned splits；全部默认 no-overwrite。
- 必查：真实列、编码、行数、类别支持、向量列用途、许可和 split；任何不一致保留
  blocker，不写 formal 目录。
- DoD：真实 manifest、hash、schema、label count 和 split disjointness 全可复核。

### S2.1-D：机器门禁与状态收口

- 依赖：C verified。
- 写入：contract 的 modality 子状态、`audit.py`、相关测试、唯一实时状态页。
- 边界：顶层 Stage 2 数据路线仍保持 reopened；S2.2 仍由人工决定；不得解锁 B0、
  formal Gold、Stage 3 或 final-ready。
- DoD：机器检查验证 manifest/hash/row/label/split/license；S2.1 标 verified；全测和
  中文日志事件完成。
- 当前状态：**verified**。可移植 manifest、独立 gate、负测试、合同与实时状态已收口；
  `sun_modality_development_data_verified=true`，但 human freeze、formal Gold、Stage 3
  和 final experiment 门禁仍关闭。后续不得把本节作为进入 S2.3/S2.4 的隐式授权。

## 6. Stage 2 方法任务卡

每次只派发一个任务卡，工作 Agent 必须把第 3 节通用前缀一起复制进 Prompt。

| ID | 唯一目标 | 必须完成的产物 | 进入下一步的门禁 |
|---|---|---|---|
| S2.2-V | 只验证用户 Layer E 进度 | validator 报告；不得改记录 | 用户自行达到 150/150 |
| S2.3 | public marker 重建 | 来源表、生成规则、hash、版本化词表、fixtures | 来源/语言/扩展策略固定 |
| S2.4 | BERT-TextCNN | 可重建训练、dev 选择、test evaluator、manifest | S2.1 verified；无 test 调参 |
| S2.5 | CoreNLP/Tregex/Tsurgeon | 版本固定、规则、顺序约束、六字段 fixtures | S2.3 verified |
| S2.6 | 完整 B0 | 分类+抽取组合、canonical Rule Record、no-LLM 证明 | S2.4/S2.5 verified |
| S2.7 | 代表性非 LLM baseline | 简单规则 + 强监督代表，统一 evaluator | S2.1/S2.2 满足依赖 |
| S2.8 | Rules+LLM-Repair 对照 | **不再推进**（§8.8.1）；保留现有可复现负结果，禁止新增 trigger/repair 优化 | formal 对照仅在 shared capsule 核验后 zero-API 重评，或另行授权重跑 |
| S2.9 | D1 锁定 | prompt/few-shot/model/temperature/budget hash | **D1 侧已锁定（2026-08-06，D1-R2）**：v6 prompt hash 3aa64877、deepseek-v4-pro/temp0/top_p1/4096、seed 策略与预算合同在 `configs/models/estg150_d1_active_registry_v1.json`；S2.2 已冻结；新的 API 运行仍另行授权 |
| S2.10 | 主数据评价 | modality、六字段、完整记录分开报告 | B0/H1/D1 同 IDs/Gold/eval |
| G0.5 | 复杂度合同 | 结果前冻结文本/BPMN复杂度字段和 bins | 不得看复杂集 test 结果 |
| S2.11 | 复杂语料冻结 | 来源/许可/hash/标签映射/人工协议 | G0.5 verified |
| S2.12 | 复杂度与错误分析 | 退化曲线、预注册错误类型、覆盖/失败数 | S2.10/S2.11 verified |
| S2.13 | Stage 2 冻结 | 数据/Gold/方法/指标/成本/manifests | S2.1–S2.12 全部通过 |

补充边界：S2.9 的锁定不等于授权真实 LLM；所有新的真实运行必须另有用户明确授权、
模型和硬调用预算。S2.8 已停止优化，不能据此派发新 H1 调用。S2.10/S2.12 的论文数字只能来自 `experiment_run` 事件和
formal manifest。不同数据、split、Gold 或 evaluator 的论文值只属于 C2/C3/C4，
不能写成 C1 严格优劣。

S2.3 当前状态（2026-07-16）：`public_marker_lexicon_en_v1` 已 verified，英文显式
public seed 共 64 个，development 扩展 count=0；source/manifest/combined payload
hash 已由机器门禁锁定。Wiktionary actor dump 未在本轮伪造或补取，旧 heuristic
词表未被当成 S2.3 产物。后续任务不得静默覆盖 v1 或用 test/Gold/结果补词。

## 7. Stage 1、Stage 3 与端到端 Prompt 卡

### Stage 1：S1.1—S1.7

```text
只执行协调 Agent 指定的一个 S1.x。Stage 1 只有在 Stage 2 core 达到主 Pipeline
门禁后开始。按 S1.1 schema → S1.2 结构解析 → S1.3 标签语义/S1.4 控制流 →
S1.5 人工 Gold → S1.6 baseline 评价 → S1.7 冻结串行推进。不得用历史资产冒充
冻结组件，不得在 S1.5 中自动产生人工 Gold。每个方法共享 Process Record schema、
fixtures、normalization 和 evaluator。
```

### Stage 3：S3.1—S3.11

```text
只执行协调 Agent 指定的一个 S3.x。S3.1-S3.3 的 BPMN 身份、matching/violation Gold
治理可在 Stage 2 收口前受控推进；明确标注 development 的 wrapper/baseline 准备也可
并行。S3.4 正式完成仍需 S1.7/S2.13，S3.7 正式 Oracle 主表还需 formal Gold publication；
S3.8+ 必须等正式 Oracle、机器合同更新和相应授权。Oracle Stage 3 先于 LLM/Hybrid，
Oracle 与 end-to-end 必须分表；matching 与 violation classification 也必须分开。
不得把 fixture scaffold 称完整复现，不得把 all-seven extension 写成 Sun 原4。
```

### 真实案例端到端：S3.9-EXT-REAL-CASE（SIM 卡入网，零 API）

```text
任务：S3.9-EXT-REAL-CASE。在 formal_experiment/ 内维护与复跑 SIM 卡入网案例的开发性端到端实验。
必读：docs/MASTER_PIPELINE.md §9.5（S3.9-EXT-REAL-CASE 行）、docs/PROJECT_AUDIT.md 当前派工、
docs/research/S3_REAL_CASE_E2E_TASK_SPEC_2026-09-11.md（v5 及 §10 已决事项）。
固定设计：
- 主案例 = references/barrientos_2026 的 Sun 派生 SIM 流程 × 5 条 v2 非空规则
  （r8/r9/r10/r11/r13）；r12 作背景单列；r9/v1 与 r12/v2 空文本不进入检测。
- 公共 Stage 1 记录一份，三组消费；协作图需经声明的扁平化适配（泳道即参与者名）。
- A=非 LLM 确定性抽取 + 冻结 Sun 式三类；B=既有真实 LLM 预测（repeat-01）+ 与 A 相同三类；
  C=与 B 同一 Stage 2 与三类结果 + 四类扩展。
- 角色绑定与顺序关系推导政策必须在打分前写入 plan 并全组统一；参考判断与检测能力解耦。
命令：
  python scripts/run_sim_case_c1_v1.py --check|--overwrite
  python scripts/run_sim_case_c1_supplement_v1.py --check|--overwrite
  python scripts/build_sim_case_checklist_v1.py --check|--overwrite
  python -m pytest tests/test_sim_case_c1_run_v1.py tests/test_sim_case_checklist_v1.py -q
边界：零 LLM/API；references/ 与 archive/ 只读且不复制原文进仓库；修复对照只作独立开发派生件并披露；
      不合成七类总 F1；不把 5 轮重复当独立样本；未检出与无法判断必须如实保留。
```

### 端到端归因：E00/E10/E01/E11

```text
只在 Stage 2 和 Stage 3 均冻结后执行。固定输入、Gold、Process/Rule Record schema、
normalization 和 evaluator，运行 E00、E10、E01、E11，分别回答 Stage 2、Stage 3
和交互贡献。不得只报告最佳组合；失败、invalid、成本和覆盖率必须进入 manifest。
```

## 8. 论文任务卡

| ID | 现在可做什么 | 解锁/验收条件 |
|---|---|---|
| PW0 | 目录、骨架、主张账本、TODO 和空表 | 本轮建立；不得含结果数字 |
| PW1 | 引言、背景、RQ0–RQ4 | 使用待检验时态 |
| PW2 | Sun/Winter/Sleimi/Michel/Barrientos 相关工作 | 原论文核验；无证据写 TODO-SOURCE |
| PW3 | 三阶段总体架构与 B0/H1/D1 设计稿 | 未完成组件写 TODO-STATUS |
| PW4 | 数据来源、五层 Gold 和人工协议 | S2.1/S2.2 后定向回填统计 |
| PW5 | baseline、指标、统计与复现设计 | 对应合同锁定后回填参数 |
| PW6 | 结果表/图空模板 | 只能是 TEMPLATE，不填数字 |
| PW7 | Stage 2 正式结果 | S2.10/S2.12/S2.13 + manifest |
| PW8 | Stage 1/3/端到端结果 | S1.7、S3.7–S3.10、P8 |
| PW9 | 讨论、局限、结论、摘要和终稿 | 主张账本全有正式证据 |

论文回填规则：每次正式实验只做一次定向回填；核对 `experiment_run` 与 manifest；
表格状态从 TEMPLATE 改为 FORMAL_VERIFIED；同时回填样本数、support、失败数、区间、
模型/evaluator 版本；再由 Agent-R1 只读复核。开发结果只能标 DEV_ONLY。

## 9. 工作 Agent 交接模板

```text
任务 ID：
结论：verified / partial / blocked（只用 Pipeline 允许状态）
实际改动：
输入及 hash：
输出及状态（development/pilot/formal）：
相关测试：
验证范围（制品/相关/已授权全量）及未覆盖项：
Gold：未改 / 用户明确授权导入
LLM/API：未调用 / 用户授权详情
仍存 blocker：
未触碰的并发文件：
建议下一任务 ID：
```
