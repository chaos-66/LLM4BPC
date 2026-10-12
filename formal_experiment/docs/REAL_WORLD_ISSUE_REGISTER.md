# 实际问题登记册

本文是整个实验的**唯一实际问题登记册**，记录在真实数据、人工标注、方法实现、
运行环境和评价过程中暴露的问题及其处置证据。它不是新的 Pipeline、状态页或
handoff：任务顺序仍以 `MASTER_PIPELINE.md` 为准，实时进度仍以
`PROJECT_AUDIT.md` 为准，已验证变更仍由 `EXPERIMENT_LOG.md` /
`EXPERIMENT_EVENTS.jsonl` 追加记录。

## 1. 强制登记规则

1. 问题一经观察到就登记；即使同一批次立即解决，也不能省略问题记录。
2. 未解决问题使用 `open`；有临时绕行但根因仍在使用 `mitigated`；只有解决方法
   已实施并通过相称验证才使用 `resolved`；明确接受且将在论文中披露的限制使用
   `accepted_risk`。
3. `resolved` 必须同时写明解决方法、验证证据和对应实验事件；缺一不可。
4. 不得删除已解决或未解决问题。问题重现时，在原 ID 的状态历史中追加
   `reopened`，不得创建一个掩盖旧问题的新 ID。
5. 涉及人工 Gold 的问题可以被记录、解释和验证，但登记过程不得替用户修改决定。
6. 每次连贯修改批次结束前检查本登记册：新问题是否已登记、状态是否准确、解决
   证据是否已经补齐。

允许状态：`open` / `mitigated` / `resolved` / `accepted_risk`。

## 2. 问题索引

| ID | 首次发现 | 阶段 | 类别 | 问题摘要 | 状态 | 当前处置/解决事件 |
|---|---|---|---|---|---|---|
| RWI-0001 | 2026-07-18 | S2.2 / S2.7–S2.10 | data/method/evaluation | 句级抽样丢失跨句先行词，人工与模型可能获得不对等上下文 | `open` | 150/150 句级盘点完成：独立 82、需上下文核实 26、不独立 42；上下文 sidecar 与公平输入合同尚未锁定 |
| RWI-0002 | 2026-07-18 | S2.2 | tool | 六要素长 LLM 候选被单行界面裁切 | `resolved` | 自动换行 + 双击全文；Event 73 |
| RWI-0003 | 2026-07-18 | S2.2 | tool/data-flow | 点击“已接受”只改状态、未把候选值和 span 物化到人工结果 | `resolved` | 显式复制/fail-closed/关系校验；Event 72 |
| RWI-0004 | 2026-07-18 | Layer D | runtime/provider | DeepSeek provider-default thinking 返回空正文，首轮 Layer D 失败 | `resolved` | 固定 `thinking=disabled` 并严格验证；Event 71 |
| RWI-0005 | 2026-07-18 | governance/tests | test | 活动测试把人工 Layer E 写死为 0/150 或 freeze=false，正常审核进度导致全量检查失败 | `resolved` | Event 74 首次修复；2026-07-21 在 150/150 全量回归发现五项 stale 状态/篡改-fixture 断言并改为活动状态/门禁一致性验证 |
| RWI-0006 | 2026-07-18 | logging/runtime | tool/display | Windows legacy code page 可使 UTF-8 子进程/超长输出乱码，并曾被误判为持久化损坏 | `resolved` | Event 75 确认文件完好；2026-07-26 audit 子进程固定 UTF-8、失败诊断按控制台安全输出 |
| RWI-0007 | 2026-07-18 | S2.2 / S2.5–S2.10 | data/method/annotation | Sun 使用德文 EStG 来源却描述英语模型与规则，未说明语言转换；非德语审核者无法独立验证德文到英文 | `open` | 人工只裁决冻结英文上的六要素；语言 QA 路线尚未锁定 |
| RWI-0008 | 2026-07-19 | S2.2 / S2.8 / S2.9 | method/annotation/schema | 人工协议、D1 与 H1 对代词、隐含主体、缺失/不确定及 scope 的操作语义未形成同一可验证合同 | `resolved` | 冻结 extraction-contract v1、v5 prompts、hash bundle 与 12 条静态 pilot；Event 78 |
| RWI-0009 | 2026-07-20 | S2.2 | tool/data-flow | 六要素人工值虽已落盘，但返回记录时因单数/复数键错误显示为空；导航又依赖 FocusOut 提交 | `resolved` | 复数数组回显 + 导航前统一提交/校验；Event 79 |
| RWI-0010 | 2026-07-20 | S2.2 | provider/security | 第三方中转无法独立证明模型身份、参数透传、计价和数据处理边界 | `mitigated` | ChatAnywhere 外发停止；改用用户授权的 Codex 内置 Sol；Events 80–82 |
| RWI-0011 | 2026-07-20 | S2.2 | tool/usability | 高级审核界面要求逐字段决定、两次状态推进和手工 span，工作量与认知负担过大 | `resolved` | 单屏六要素编辑、后台 span、一次“保存并下一条”；Event 83 |
| RWI-0012 | 2026-07-20 | provenance/runtime | Windows CRLF 使预先计算的候选 bundle hash 与实际落盘文件不一致 | `resolved` | 写入后对实际文件取 hash 并加回归；Event 83 |
| RWI-0013 | 2026-07-21 | S2.7-B0-DEV / CoreNLP | runtime/method-boundary | 锁定的 Tsurgeon context prune 在真实长句上可能删除整棵句法树，导致单样本桥终止整批 | `resolved` | 保留原 bridge/rules，新建 batch bridge 将该终态记为后续字段 miss 并继续；266 句中 2 次，7 项聚焦测试与 Event 85 |

| RWI-0014 | 2026-07-21 | S2.10-E / S2.7-B0-DEV | evaluation/measurement | v1.1 evaluator 把方法本地 clause/entity ID 当成可共享身份，并要求 exact span fallback，系统性漏计近似相同的语义单元 | `resolved` | v1.2 固定全局一对一字符 span IoU≥0.5、entity 指标忽略方法本地 ID、exact segmentation 单列；adversarial/回归/exact-hash gate 与 Event 86 |
| RWI-0015 | 2026-07-21 | S2.7-B0-ENHANCED | method/routing/segmentation | B0 v1 record→clause 标签复制与过分割/单 span；v3 后仍 segmentation-bound | `mitigated` | v5 hybrid：definition-first modality、stable merge+conservative multi-modal split、dep actor/action、regex scope；modality micro F1 0.612→0.624、align F1 0.771→0.801、Table8 F1 0.443→0.492；仍未达 Sun 目标 |
| RWI-0017 | 2026-07-22 | S2.4-CAND | evaluation/governance | candidate B 与 C 各对 S2.4 test 评估一次；test 已多候选暴露，虽未用于 winner ranking，但不再是干净一次性 final test | `open` | 本轮禁止再次访问 S2.4 test；B test macro-F1=0.877 仅 exploratory/report-only；后续选择只用 train/dev |
| RWI-0016 | 2026-07-22 | S2.7-B0-ENHANCED / Phase A | evaluation/measurement | Minimax v6 Phase A 诊断无效；correction v2 修了假 classifier，但仍有 1→N DE 复制、marker-only 默认 obligation、oracle 混路由、overlap near-dup 过粗 | `mitigated` | correction v2 部分修复；v8 prereg 要求 residual Phase A 修正后才可 re-resolve |
| RWI-0018 | 2026-07-23 | S2.7-B0-ENHANCED / B2a2 | method/routing | B2a 拒绝宽松 definition 后把 record classifier 标签写回受支持子句，新增 40 条 record fallback；改为同子句三类受限解码后 definition 召回崩塌 | `mitigated` | B2a2 将总 fallback 恢复至 20、受支持子句新增 fallback=0，但 definition TP 16→2，B/C/D 门槛失败；候选作为负证据保留且不晋级，Event 105 |
| RWI-0019 | 2026-07-23 | S2.7-B0-ENHANCED / B2b | method/routing | v10-A 有 6 条对齐的 prohibition→permission 错误，但严格白名单强否定规则只覆盖 1 条 | `open` | B2b 只读诊断为 `not_instantiated`；未建生产 resolver、未预注册、未跑 All150，v10-A 保持父版本；Event 106 |
| RWI-0020 | 2026-07-25 | S2.7-B0-ENHANCED / B3b | method/routing | clause-level typed evidence 对 condition/constraint ownership 过宽：减少 constraint FP 的同时大量损失 TP，并扩大 condition FP | `open` | B3b opportunity 诊断为 `not_instantiated`；11/18 门槛失败，未建生产候选、未跑候选 All-150，v10-A/active registry 不变；Event 110 |
| RWI-0021 | 2026-07-25 | S2.7-B0-ENHANCED / B5 | provenance/concurrency | 并发 Grok 会话在唯一 All-150 运行期间覆盖冻结 prereg 与部分 B5 实现，导致 manifest 末尾记录的 prereg SHA 与启动时冻结 SHA 不一致 | `open` | 从 Codex 会话历史逐字节恢复全部冻结文件并复核 22 个绑定；不改既有 manifest、不重跑 All-150、不晋级；第二次命令调用 fail closed，v10-A/active registry 不变 |
| RWI-0022 | 2026-07-25 | EStG-150 candidate protocol / C0 | provenance/protocol | 历史内置 Sol 候选未存档隐藏 system/developer transport 与内部 API envelope，无法逐字节复现隐藏请求 | `mitigated` | 如实锁定 `historical_hidden_transport_payload_not_archived=true`；冻结唯一 external canonical serializer v1、四 adapters、fixture/hash 与 fail-closed tests；C1 已有两次失败尝试，C2–C4 未运行 |
| RWI-0023 | 2026-07-25 | EStG-150 candidate protocol / C1 | runtime/diagnostics | 两次 C1 HTTP 400 只保留状态码，runner 未读取 provider 错误正文，无法区分具体不兼容字段 | `mitigated` | 终态 HTTP 错误现限长保存 raw body/hash/request ID/retry，密钥回显则拒绝落盘；七模型矩阵已定位多类根因，但初始两份正文不可恢复；Events 118–119 |
| RWI-0024 | 2026-07-25 | EStG-150 candidate protocol / C1 | runtime/transport | ChatAnywhere gpt-4o 无 HTTP 响应地断开连接，`RemoteDisconnected` 未进入锁定网络重试分支 | `resolved` | 显式归类为可重试 transport error，始终重发同一 request bytes，并在耗尽时保存 retry reasons/终态类型；17 项聚焦回归；Event 119 |
| RWI-0025 | 2026-07-26 | EStG-150 candidate protocol / C1 | schema/provider compatibility | canonical v1 的 6 个字符串 const/enum 缺显式 type，且旧模型/DeepSeek envelope 不兼容容易诱发静默降级 | `resolved` | 保留 canonical v1，新增 strict transport adapter v1.1、递归预检和七模型 fail-closed capability allowlist；获授权 gpt-5.6-luna 单条 C1 生成 1 个 canonical-valid candidate，C1=true、C2=false；Event 121 |
| RWI-0026 | 2026-07-26 | EStG-150 candidate protocol / C2 | preregistration/provenance | C2 的 Pass B 请求内嵌同次运行新产生的 Pass A 输出，因此三条未来真实 Pass B request SHA 不可能在调用前诚实计算；旧 dry-run 还只预检第一条 Pass A | `mitigated` | 六槽位离线预检现全部落盘并锁 SHA；三条 Pass B 明确使用已验证历史 Pass A fixture、仅作 offline envelope preflight，未来真实 SHA 保持 deferred；C2=false、API=0；Event 122 |
| RWI-0027 | 2026-07-26 | EStG-150 candidate protocol / C1–C2 | accounting/provenance | 可计费 response 在 canonical candidate 或 finish-reason 校验失败时，usage 可能未进入 failure receipt | `resolved` | 两份原 failure/raw response 均不改写；SHA-bound corrections 分别恢复 C1 的 2956 tokens/0.01728755 CA 与 C2 的 7839 tokens/0.282373 CA；runner 先计 envelope usage，再检查 finish reason/candidate；mocked invalid/length 回归；Events 123–124 |
| RWI-0028 | 2026-07-26 | EStG-150 candidate protocol / C2 | generation/validation | GPT-4o Pass B 把逐字不变的译文标为 `edited`；runner 又错误地用原始英文而非同次 Pass A 文本校验 Pass B translation decision | `mitigated` | v1.5 增加 decision/text 生成前自检并让 Pass B 校验绑定同次 Pass A；旧响应仍 fail closed，57 项聚焦回归和六槽位离线 preflight 通过；真实 runtime 待新授权；Event 134 |
| RWI-0029 | 2026-07-26 | EStG-150 candidate protocol / C2 | generation/coordinates | GPT-4o 对重复 modality cue 持续给出不可直接切片的错误坐标；v1.6/v1.7 的生成前约束均未被稳定遵守 | `mitigated` | v1.7 真实运行在 3/6 calls 后因重复 `may` 坐标偏差 23>8 fail closed；v1.8 仅对相同 modality evidence cue 使用无距离上限的唯一最近精确匹配，其他重复语义 span 仍限 8 字符，零匹配/并列仍拒绝，并强化 absolute-offset/action 逐字指令；65 项聚焦回归和六槽位离线 preflight 通过；Events 135–138，后续事件待记录 |

## 3. 详细记录

### RWI-0029 — 重复 modality cue 使错误坐标无法唯一重锚

- **首次发现**：2026-07-26 ChatAnywhere `gpt-4o` v1.5 C2 runtime。
- **阶段/范围**：EStG-150 canonical external candidate protocol 的 Pass A modality evidence
  坐标与 portable response-coordinate boundary；不修改 canonical schema、prompt 或 Gold。
- **观察事实**：样本 0 Pass A 将两个分别包含 `shall` 的规范句合并为同一个 clause，随后把
  `modality.evidence[0].text` 仅写成 `shall`，并给出不匹配的坐标 12–17。该父 clause 内恰有
  两个逐字相同的 `shall`，因此 v1.3 起冻结的 `deterministic_exact_text_unique_reanchor` 找到
  两个候选位置，无法在不猜测模型意图的前提下选择一个。
- **影响**：JSON 结构、translation decision 与 evidence 文本本身可以合法，但错误坐标加重复
  短文本使现有 coordinate-only 规范化无法安全完成。任意选择第一处/最近处都可能把 evidence
  绑定到错误规范，构成未披露的语义修补。
- **当前处置**：v1.5 runner 正确 fail closed，没有选择任一匹配、没有修改响应、没有内容重试，
  其余五条未调用。原 preregistration/request/response/failure 均冻结且不可覆盖。
- **离线修复**：portable adapter v1.6 只在 transport-only 输出自检中增加一条规则：如果可见
  normative cue 在同一 `clause_span` 内出现多次，`modality.evidence.text` 必须扩展为包含该 cue、
  且在该 clause 内只出现一次的最短逐字连续短语；禁止猜测某次出现，重复时禁止只输出 cue。
  `deterministic_exact_text_unique_reanchor`、canonical validator、schema、serializer、prompt、
  response-repair/content-retry 禁令均保持不变，v1.5 由历史 loader 保留。
- **运行证据**：1 content call、0 retry；provider 报告 `gpt-4o`、`finish_reason=stop`；
  1,661 input + 1,128 output = 2,789 tokens，0.1080275 CA；0 valid candidates，C2 started
  但未完成，evaluation=0、P/R=null，Layer D/E/Gold 未读取。
- **离线验证**：真实 v1.5 raw response 回放仍因 `found 2` fail closed；唯一扩展短语的错误坐标可在
  不改语义的前提下确定性重锚。59 项 candidate/transport 聚焦回归通过；
  `c2_relay_gpt4o_portable_v1_6_pilot3_dry_run_v1` 的 6/6 strict transport preflight 通过，
  `request_downgrade_applied=false`，API/key/network=0、billed tokens/cost=0、C2=false、
  evaluation=0、P/R=null，Layer D/E/Gold 未读取。
- **v1.6 再次出现**：新授权运行 `c2_relay_gpt4o_portable_v1_6_pilot3_live_v1` 中，样本 0 的
  Pass A/B 均通过；样本 1 Pass A 仍把 clause 内出现两次的 `may` 作为单词 evidence，并给出
  倒置坐标 `start=116,end=115`。该坐标靠近第一个 `may`，但 v1.6 唯一精确重锚仍按冻结规则找到
  两个文本匹配并 fail closed，证明只增加模型自检指令不足以稳定解决旧模型坐标问题。
- **v1.6 运行证据**：3/6 content calls、0 retry；6,528 input + 3,813 output = 10,341 tokens，
  0.381150 CA；2 个已通过请求、`valid_candidate_count=1`，但运行没有生成 `candidates.json` 或
  成功 manifest，因此候选集合未冻结；其余三条未调用。evaluation=0、P/R=null，
  `request_downgrade_applied=false`，Layer D/E/Gold 未读取。
- **v1.7 离线修复**：新增
  `deterministic_exact_text_unique_or_bounded_nearest_start_reanchor`。仅当 span 文本在父范围内有
  多个精确匹配、model-supplied `start` 为整数、最近匹配唯一且起点偏差不超过 8 个字符时，
  才只改 `start/end`；并列、偏差超过 8、零匹配或缺少整数起点均 fail closed。receipt 记录候选数、
  选择方法和偏差。transport-only guard 同时增加逐 clause 构造顺序与重复 `may` 示例，明确把非逐字、
  clause 外或不可定位的可选字段留空并报告 ambiguity；canonical prompt/schema/serializer 不变。
- **v1.7 验证**：受限单元夹具可把两个 `may` 中距模型起点 3 字符的唯一最近项校正；v1.5 raw
  response 的第二个重复 `shall` 因最近偏差 30>8 仍 fail closed；v1.6 raw response 的重复 `may`
  可越过该坐标问题，但随后仍因 `clauses[2].conditions[0]` 零精确匹配而 fail closed，证明 v1.7
  没有删除 condition、模糊对齐或进行语义修补。62 项聚焦回归通过；
  `c2_relay_gpt4o_portable_v1_7_pilot3_dry_run_v1` 的 6/6 strict preflight 通过，
  `request_downgrade_applied=false`，API/key/network=0、billed tokens/cost=0、C2=false、
  evaluation=0、P/R=null，Layer D/E/Gold 未读取。
- **v1.7 真实复现**：新授权运行在 3/6 calls 后再次 fail closed。样本 0 Pass A/B 通过；样本 1
  Pass A 的重复 `may` 最近精确出现距模型 start 23 字符，超过 8 字符界限。运行消耗 6,897 input、
  3,679 output tokens、0.3782275 CA、0 retry；候选集未冻结、evaluation=0、P/R=null、
  Layer D/E/Gold 未读取。继续回放还发现 clause 1 action 删除了 `subject to biological growth`，
  因零精确匹配仍必须拒绝，不能仅靠坐标修复挽救旧响应。
- **v1.8 最小修复**：只对 `modality.evidence` 的相同重复 cue 允许按 model start 选择唯一最近精确
  出现且不设距离上限；相同 cue 在同一 modality label 下提供等价可见规范证据。并列、缺少整数 start、
  零匹配仍 fail closed；actor/action/condition/constraint/exception/order evidence 等其他重复 span 继续
  保持 8 字符界限。guard 另明确所有坐标是全 translation 的 absolute offset、不得复用 actor.start，
  action.text 不得删除中间修饰语或宾语。canonical prompt/schema/serializer/transport schema、B0、D1/H1
  均未改变；旧 v1.7 仍可只读回放。65 项聚焦回归和 v1.8 六槽位 strict preflight 通过。
- **状态**：`mitigated`。v1.8 离线边界已验证，但尚需在已明确授权的 35 CA 累计预算内完成真实复验。
- **对应事件**：Events 135–138；v1.7 失败与 v1.8 事件待追加。

### RWI-0028 — C2 Pass B translation decision 与实际候选文本不一致

- **首次发现**：2026-07-26 ChatAnywhere `gpt-4o` v1.4 C2 runtime。
- **阶段/范围**：EStG-150 canonical external candidate protocol 的 Pass B 生成边界与本地
  translation-decision 校验；不修改 B0、D1/H1、canonical prompt/schema/serializer 或 Gold。
- **观察事实**：样本 0 Pass A 返回 `decision=accepted`；Pass B 随后返回
  `decision=edited`，但两次 `translation.proposed_text_en` 逐字符完全相同。canonical validator
  因 `edited translation is unchanged` 正确拒绝，真实运行在 2/6 calls 后 fail closed。同时检查
  runner 发现：Pass B 即使依赖同次 Pass A 输出，validation 仍固定拿样本原始英文作比较基准；
  若 Pass A 真正改过译文，合法的 Pass B `accepted` 也可能被误拒。
- **影响**：strict JSON schema 只能约束枚举和结构，不能表达“`edited` 必须对应文本实际变化”的
  跨字段不等式；缺少显式输出自检时，旧模型可生成结构正确但语义自相矛盾的 JSON。错误的
  Pass B 比较基准还会让本地校验偏离实际被审核文本。
- **当前处置**：新增 portable adapter v1.5，在 transport-only invariant 中明确要求
  `proposed_text_en` 逐字不变时必须 `accepted`，只有实际至少变化一个字符才允许 `edited`；
  无 response repair 或 content retry。runner 的 Pass A/`full_extract` 继续绑定原始冻结英文，
  Pass B 改为绑定同次已验证 Pass A 的 `proposed_text_en`。v1.4 配置、失败运行和响应均保持原样，
  并由历史 loader/回归继续验证。
- **验证证据**：旧 v1.4 Pass B response 离线重放仍以同一错误 fail closed；candidate/transport
  聚焦回归 57 passed。`c2_relay_gpt4o_portable_v1_5_pilot3_dry_run_v1` 的六个请求全部通过
  strict transport preflight，`request_downgrade_applied=false`，未读取 key、未联网、0 tokens、
  0 cost、C2=false、evaluation=0、P/R=null。
- **状态**：`mitigated`。代码与离线请求边界已修复；是否足以约束真实 GPT-4o 输出仍需新的
  明确 API 授权和不可覆盖 run ID 验证，不能仅凭离线测试写为 `resolved`。
- **对应事件**：Event 134。

### RWI-0027 — canonical-invalid provider response 的 usage 未进入失败收据

- **首次发现**：2026-07-26 ChatAnywhere `gpt-5.4-nano` 单条 C1 runtime。
- **阶段/范围**：EStG-150 canonical external runner 的 provider-response accounting；不改变
  schema、prompt、request bytes、candidate validator 或阶段分流。
- **现象**：provider 返回 HTTP 成功、`finish_reason=stop`、1167 input / 1789 output tokens，
  但候选把 57 字符翻译的 `clause_span.end` 写成 58，canonical validator 正确拒绝。旧 runner
  在 candidate validation 后才提取 usage，因此 `failure.json` 写成 0 tokens、0 cost。
- **风险**：真实调用可能在候选无效时被误报为无 token/无费用，破坏预算与失败 provenance；
  不能通过覆盖原 failure 或重跑模型来掩盖。
- **处置**：保留原 preregistration/request/raw response/failure 的原字节；新增
  `accounting_correction.json`，绑定三份原证据 SHA，并从 raw response 恢复 2956 total tokens、
  0.01728755 CA。runner 现在在保存响应后先解析 envelope/usage、累计 token/cost 并执行硬上限，
  然后才解析和验证 candidate；失败收据同时保留 provider model/response ID/response SHA。
- **验证**：新增 mocked canonical-invalid response 回归，要求 failure receipt 即使 0 candidates
  仍保存 provider usage/cost；candidate/transport 聚焦回归与完整审计通过后记录 Event 123。
- **边界**：仅 1 次获授权内容调用、0 retry；未修复模型输出、未重跑 API、未评价，P/R=null，
  C1=false、C2=false；relay 模型身份仍未独立验证。
- **再次发现与解决**：同日获独立授权的 ChatAnywhere `gpt-5.6-luna` C2 在首条 Pass A
  返回 `finish_reason=length`、空正文和 1339 input + 6500 output/reasoning tokens。前一次修复虽已
  把 envelope 提取移到 canonical candidate validation 之前，但 envelope 自己仍在返回 usage 前
  拒绝非 `stop` completion，导致新 `failure.json` 再次错记 0。原失败证据保持不改写；新的
  `accounting_correction.json` 绑定 failure/preregistration/raw response/request SHA，恢复总计
  7839 tokens 与 0.282373 CA。envelope 现在只解析并返回 billable transport evidence，finish
  reason 检查移到 candidate extraction；mocked `length` 回归确认 failure receipt 会记录 model、
  response ID、finish reason、response SHA、usage 与费用。
- **第二次边界**：C2 只发生 1 次内容调用、0 retry；其余五条未调用，无 Pass B/候选/评价，
  C2 started=true 但未完成，C3/C4=false，P/R=null；没有为修复重跑 API。relay 身份仍未独立验证。
- **状态历史**：
  - 2026-07-26：C1 canonical-invalid response 暴露首次记账缺口；解决并记录 Event 123。
  - 2026-07-26：C2 `finish_reason=length` 暴露 envelope 内仍有同根缺口，RWI 重开；将 finish
    校验移至 usage 记账之后并补回归，验证后再次转为 `resolved`，记录 Event 124。

### RWI-0026 — C2 Pass B 的真实请求 SHA 依赖尚未产生的 Pass A 输出

- **首次发现**：2026-07-26 C2 offline preparation。
- **阶段/范围**：EStG-150 canonical external candidate protocol 的 C2（索引 0–2，
  每条 Pass A + Pass B）；不修改 canonical schema、serializer、prompt 或真实执行分流。
- **观察事实**：既有 `--stage c2` dry-run 只构造并预检第一个样本的 Pass A，虽然打印
  `request_count=6`，并没有生成其余五条离线 request bytes。更重要的是，冻结协议要求
  Pass B 的 `pass_a_candidate` 必须是同次运行刚生成并通过 canonical validator 的完整
  Pass A 输出；该内容在真实调用前不存在，因此三条未来真实 Pass B transport SHA
  数学上不可预先确定。若把历史 Pass A 或任意 mock 的 SHA 冒充未来真实 SHA，就会静默
  改变或虚构协议 provenance。
- **影响**：只报告一个首请求 hash 不能证明六槽位都通过 strict transport preflight；反过来
  把 fixture-bound Pass B hash 写成未来 live hash 又会产生错误的 preregistration claim。
- **当前处置**：新增 no-overwrite C2 offline preparation。它对三个 Pass A 请求和三个
  Pass B envelope 全部执行 strict transport v1.1 preflight，保存六对 semantic/transport
  bytes 与六个 offline SHA。Pass B 只为离线预检读取已冻结且重新通过 canonical schema/
  exact-span/cue validator 的历史 Pass A 三条结果；receipt 对每条明确写
  `offline_preflight_fixture_only_live_pass_a_dependent`、
  `future_live_transport_request_sha256_deferred=true`。未来真实 C2 必须使用新 run ID、
  新明确授权和同次运行的新 Pass A 输出，并在其返回后记录真实 Pass B SHA；不得复用
  本次 dry-run ID 或把 fixture SHA 当作 live SHA。
- **验证证据**：41 项 candidate/transport 聚焦回归通过；离线目录
  `c2_relay_gpt56_luna_strict_v1_1_pilot3_dry_run_v1` 保存 6/6 preflight、6 个不同 transport
  SHA、C1 prerequisite、canonical/serializer/adapter/transport hash、6-call/78,000-token/
  1.92-CA fail-closed 配置与 `request_downgrade_applied=false`。API/key/network=0，
  billed tokens=0，evaluation=0，P/R=null，C2=false。
- **状态**：`mitigated`。六个离线 envelope 已可复核；协议固有的三条 live Pass B 动态
  SHA 依赖不能也不应在 Pass A 返回前伪造。
- **状态历史**：
  - 2026-07-26：发现旧 dry-run 单请求覆盖不足与动态 hash 边界；实现依赖感知的六请求
    离线 receipt，保持真实 Pass B hash deferred；Event 122。

### RWI-0025 — C1 strict transport schema 与 provider envelope 兼容性

- **首次发现**：2026-07-25 七模型 C1 transport matrix；2026-07-26 开始离线修复。
- **阶段/范围**：EStG-150 canonical external candidate protocol，只有 C1 请求进入模型前的
  schema/envelope compatibility；不修改 B0、D1/H1 prompt，不进入 C2。
- **观察事实**：ChatAnywhere `gpt-5.6-luna` 与 `gpt-5.4-nano` 的真实 HTTP 400 首先指出
  `properties.schema_version` 的 `const` 缺显式 `type`。递归检查 canonical schema 后确认另有
  `context_sufficiency`、`translation.decision`、`$defs.modality.label`、`confidence`、
  `$defs.ambiguity.field`，共 6 个字符串 const/enum 节点存在同类问题。`gpt-4.1-nano`/
  `gpt-3.5-turbo` 不接受 `reasoning_effort`；`gpt-4o` 仅有断连证据；official
  `deepseek-v4-pro` 不接受 `developer` role，且 canonical strict response format 不能靠
  `json_object` 或 tool call 冒充。
- **影响**：直接覆盖 canonical schema 会破坏 C0 审计证据和 semantic request hash；只修第一个
  字段会让下一字段继续被 provider 拒绝；按模型静默删除 reasoning、合并消息或降级
  `json_object` 又会把不同协议伪装成同一 C1。
- **处置方法**：canonical schema 继续保持 SHA-256
  `fbbb628ad0f25639958c6d02db9bac90ed06865e634bd4e8eeb7b50ac7108ca9`，canonical
  serializer identity 继续为
  `d20ae560a627c4d3faa88439908c517e7726aabb1121128af7b9013f5512edef`。新增
  `estg150_openai_strict_transport_schema_adapter@1.1.0` 和 transport schema
  `ef8c684b2456196eac14cc7748bb687aef5ef32fd8a405c3003bd831ad380af7`，加载时证明结构差
  恰好只有上述 6 个 `type:string` addition。递归 preflight 在创建 run 目录、读取 key 或发网
  之前检查 root/object/required/additionalProperties/const-enum type/本地 `$ref`/嵌套
  `anyOf`/现有长度与数值约束。七模型 allowlist 恰好固定为三个现代 ChatAnywhere
  offline-ready 条目和四个 fail-closed 不兼容条目；所有删除 reasoning、消息合并、
  `json_object` 与 tool-call 替代均禁用。未来 response 仍只用 canonical schema 本地验证，
  receipt 同时记录 canonical/transport 两套路径、版本和 hash、实际 request hash、验证结果与
  downgrade=false。
- **验证证据**：离线修复时 57 项 C1/protocol/audit 聚焦回归通过；快速 `audit_project.py` 为
  Integrity=True、ERRORS=0，并新增
  `estg150_c1_transport_adapter_offline_ready` pass。gpt-5.6-luna dry-run 的 semantic SHA 保持
  `eb074081...c085e1`，派生 transport request SHA 为 `ac24297d...c282f`；dry-run 不读取 key、
  不发网络、不创建 run。用户另行确认既有矩阵后台 token=0、余额变化=0、未计费。随后用户
  明确授权 ChatAnywhere `gpt-5.6-luna` 仅 1 条 synthetic、13,000-token 与 0.32-CA 上限；
  `c1_relay_gpt56_luna_strict_v1_1_pilot_v1` 无重试生成 1 个候选，原始 canonical schema、
  exact span 与 normative-cue coverage 全部通过。provider usage 为 1167 input + 829 output =
  1996 tokens，按授权命令锁定的 7/42 CA-per-million 输入/输出价记录 0.042987 CA；manifest
  为 `succeeded_frozen`、C1=true、evaluation=0、P/R=null、C2=false。relay 报告的具体模型
  `gpt-5.6-luna-2026-07-09` 未经独立身份验证。
- **状态**：`resolved`。现代 ChatAnywhere strict profile 的 schema 根因已由真实 C1 消除，且
  原始 canonical validator 通过；已知不兼容模型在 key/network 前 fail closed，不再通过静默
  降级伪装成同一协议。`gpt-5-nano` 的历史 503、`gpt-4o` 的历史断连以及其它 provider 的
  固有能力边界仍是独立 runtime/profile 事实，不影响本修复的 resolved 状态。
- **状态历史**：
  - 2026-07-25：七模型矩阵定位多类 transport failure；0 candidates/evaluations，C2 未开始。
  - 2026-07-26：strict transport v1.1 离线 adapter/preflight/receipt 落地，状态为
    `mitigated`，等待单条 synthetic 的新授权验证。
  - 2026-07-26：获新授权的 gpt-5.6-luna 单条 C1 runtime 成功，1 个候选通过原始 canonical
    validator；1996 tokens、0.042987 CA、0 retry、P/R=null、C2=false；Event 121 后转为
    `resolved`。

### RWI-0024 — `RemoteDisconnected` 未进入锁定的网络重试分支

- **首次发现**：2026-07-25。
- **阶段/范围**：EStG-150 C1 ChatAnywhere `gpt-4o` 诊断重跑。
- **观察事实**：中转在约 280 秒后关闭 TLS/HTTP 连接而没有返回 HTTP response；Python 抛出
  `http.client.RemoteDisconnected`。旧 transport helper 只捕获 `URLError`、`TimeoutError`
  与 `socket.timeout`，因此该 run 直接以 `error_type=RemoteDisconnected`、`retry_count=0`
  fail closed，没有执行协议允许的相同字节网络重试。
- **影响**：这不会产生错误候选，但会把可重试的 relay/network failure 错记为普通失败，并
  丢失应有的 retry provenance。该次 gpt-4o 结果只能说明中转断连，不能判断 schema 或模型
  兼容性。
- **解决方法**：将 `RemoteDisconnected` 显式加入网络错误分支；每次只重发完全相同的
  request bytes。重试预算耗尽时改抛 `RetryableTransportError`，在 `failure.json` 保存已经
  发生的 retry reasons 与 terminal network error type。已完成的 gpt-4o run 不覆盖、不伪造
  retry，也没有在本轮 6-call 授权之外再次调用。
- **验证证据**：17 项聚焦回归新增 synthetic relay disconnect→相同字节重发→成功响应，
  并逐 hash 绑定七份 failure/request/error artifacts 与 matrix manifest；
  C0 serializer SHA 仍为
  `d20ae560a627c4d3faa88439908c517e7726aabb1121128af7b9013f5512edef`，gpt-4o
  transport SHA 仍为
  `601f0e88e569dcf826acd57799d72db99c3bddcdb9d39b462e7ae1c7a7fbea27`；完整验证与
  Event 119 绑定。
- **状态**：`resolved`。本地异常分类与 provenance 已修复；该次外部中转为何断连仍是
  provider 运行期现象，不据此声称 gpt-4o 接受或拒绝 canonical schema。
- **状态历史**：
  - 2026-07-25：真实 C1 暴露缺口；同批次修复并通过离线 identical-byte retry 回归。

### RWI-0023 — 终态 HTTP 错误正文丢失使跨模型 400 无法定位具体字段

- **首次发现**：2026-07-25。
- **阶段/范围**：EStG-150 canonical external candidate protocol，C1 transport pilot。
- **观察事实**：官方 DeepSeek `deepseek-v4-pro` 与 ChatAnywhere 中转 `gpt-4o` 各按冻结
  envelope 调用一条 synthetic，均返回 HTTP 400。旧 runner 把 `urllib.HTTPError` 直接转换为
  `ProtocolIncompatible`，却没有读取其 file-like response body；两份 `failure.json` 因此只有
  状态码，没有 provider 的字段级错误信息。现有证据只能证明请求在 transport/API 层被拒绝，
  不能证明是模型安全拒答，也不能在 `reasoning_effort`、strict schema 子集、消息角色或中转
  alias 之间选定单一根因。
- **影响**：继续盲测更多模型只会堆积相同的 HTTP 400；即使最新模型失败，也无法判断是模型
  能力、provider/relay 兼容性还是本地 envelope 问题，还会浪费调用和费用预算。
- **当前处置**：新增 `ProviderHTTPError` 诊断载体。后续终态 HTTP 响应最多读取并保存原始
  1 MiB body，同时在 `failure.json` 记录 status、落盘相对路径、实际保存字节数、SHA-256、
  truncation、白名单 request ID 与此前 retry reasons。若 raw body 含实际 API key 字节则只记
  hash/长度与 `credential_echo_detected=true`，拒绝落盘。该变更不修改 semantic request、
  prompt、schema、serializer、transport body 或 retry 判定。
- **验证证据**：15 项聚焦回归覆盖 HTTP 400 正文/request ID、raw artifact 精确字节、retry
  记录与 credential-echo 阻断；C0 serializer SHA 仍为
  `d20ae560a627c4d3faa88439908c517e7726aabb1121128af7b9013f5512edef`，同一 `gpt-4o`
  C1 transport SHA 仍与既有真实请求完全一致，为
  `601f0e88e569dcf826acd57799d72db99c3bddcdb9d39b462e7ae1c7a7fbea27`；完整验证与
  Event 118 绑定。
- **状态**：`mitigated`。未来错误已可精确诊断，但旧两次 HTTP body 无法事后恢复；必须由
  用户重新给出 provider/model、调用数、总 token 与费用上限后，才能发出新的 C1 请求。
- **状态历史**：
  - 2026-07-25：在比较两次 C1 失败时发现诊断正文未存档；实现无请求漂移的诊断捕获并通过
    离线验证，旧响应根因仍未知，状态为 `mitigated`。
  - 2026-07-25：获授权的七模型 C1 矩阵实际验证诊断链；六个带 HTTP 响应的失败均保存
    body/hash，其中最新中转模型定位到 schema strict-subset 问题，DeepSeek 定位到消息角色
    问题，旧非推理模型定位到参数问题。初始两份旧 response body 仍不可恢复，状态保持
    `mitigated`。

### RWI-0022 — 历史隐藏 transport payload 未存档

- **首次发现**：2026-07-25。
- **阶段/范围**：EStG-150 原始候选生成协议复现，C0 协议锁定。
- **观察事实**：历史目录 `codex_internal_gpt56sol_full150_v1/` 保存了 run config、
  batch outputs、aggregate 与 manifest；三份 prompt、output schema、A/B/C 和 membership
  也仍可逐字节核验。一次范围受限搜索未找到内置 Codex 调用的完整 request messages、
  隐藏 system prompt 或内部 API envelope。历史专用外部 runner 只保存了后来准备的
  ChatAnywhere system/user 请求构造，不能冒充内置 Sol 隐藏 transport。
- **影响**：不能诚实声称 byte-exact 复现 Codex 内部 request，也不能把 provider-specific
  envelope 差异误写成原历史协议。若各 provider 自行拼 prompt/schema，又会引入不可控的
  方法差异。
- **当前处置**：配置和 prereg 明确写
  `historical_hidden_transport_payload_not_archived=true`；冻结
  `estg150_canonical_external_serializer@1.0.0`，统一 system/developer/user 顺序、原 prompt/
  schema bytes、字段顺序、UTF-8/LF、Layer-A sample 顺序、0–2 双轮/3–149 单轮、response
  extraction、strict validation 与 retry。中转、DeepSeek、Qwen、xAI 只通过 adapter 改
  transport 外层；旧 ChatAnywhere 专用入口真实执行已 fail closed 退役。
- **验证证据**：八项指定 hash 全匹配；serializer SHA
  `d20ae560a627c4d3faa88439908c517e7726aabb1121128af7b9013f5512edef`；UTF-8/LF
  fixture SHA `eb074081cc52d22025e263e3f94b2165f95493f511ddc454b9ea5f5923c085e1`；
  定向回归覆盖 provider semantic payload 等价、D/E/Gold 数据不可进入 user payload、
  分流、schema/prompt hash、德文字符/换行/offset 与 no-network dry-run。
- **状态**：`mitigated`。不可恢复的历史隐藏信息仍缺失；external v1 只从现在起保证
  可重复、provider-neutral，不能消除历史 provenance 缺口。C1–C4 仍须独立用户授权。
- **状态历史**：
  - 2026-07-25：发现并如实登记；C0 external serializer 缓解完成，未运行真实 API。

### RWI-0021 — 并发 Agent 写入破坏 B5 preregistration 的运行期不变性

- **首次发现**：2026-07-25
- **阶段/范围**：S2.7-B0-ENHANCED development，B5 唯一 All-150 与预注册 provenance。
- **观察事实**：Codex 在 UTC 08:51 前验证 prereg SHA
  `2b3062da26a27bb40677b45ad2d38de73a2b56a726f52294bcd7916a7f1626ac` 及其全部
  22 个绑定后启动唯一命令。Grok/OpenCode 会话于 UTC 08:58 覆盖 config、prereg 和部分
  B5 源码，并于 09:15 撤回；撤回删除了 4 个冻结文件、把 runner 留在旧版本。运行
  manifest 在结束时重读磁盘 prereg，故记录 SHA
  `38a11ea0b941f81c56b3f20362ca8ef537f7d998837e63ecf9585ce6669fac9a`，与启动时冻结
  SHA 不一致。Grok 于 09:03 再次调用同一命令，但约 5 秒即 fail closed，未产生第二次
  All-150。运行期后段仍会读取的 registry 与 Java bridge 在两个会话中恰为同一冻结
  hash；Python 模块和 config 已在进程启动时加载，但这不能消除 prereg 不变性缺口。
- **影响**：五个输出内部 hash 自洽、结构与性能指标可作诊断，但不能声称为严格满足
  “prereg 在 All-150 全程冻结”的可接受候选；尤其不得通过事后改 manifest 来伪造一致性。
- **当前处置**：从 Codex 本地会话历史重放原始全文和补丁，只在 prospective bytes 与
  原冻结 size/SHA 完全相等时恢复；当前 prereg、runner、registry、bridge、actor/action
  consumer 及其余绑定全部通过原 verifier。既有 manifest 与五件输出不修改，All-150
  不重跑，不创建 B5v2/B5a/correction，不晋级，父版本继续为 v10-A。
- **尚未解除的根因**：共享工作区缺少阶段级 single-writer/lockfile；在未来获得单独授权
  前，不应让多个 Agent 同时写同一冻结候选。当前 B5 证据的 prereg SHA 失配不可在本轮
  修复，只能如实保留。
- **验证证据**：当前 project audit Integrity=True、ERRORS=0；全部 22 个 prereg binding
  通过；四个 manifest 子产物 hash 自洽；唯一实际 All-150 输出时间为 UTC 09:02，Grok
  第二次命令仅持续约 5 秒且未覆盖输出。
- **对应事件**：本轮最终 B5 事件。
- **状态历史**：
  - 2026-07-25：发现并发覆盖与不完整撤回，登记为 `open`；完成逐字节恢复，但运行期
    prereg 不变性已经破坏，状态不能标为 resolved。

### RWI-0020 — clause-level typed evidence 不足以安全重分配 condition/constraint ownership

- **首次发现**：2026-07-25。
- **阶段/范围**：S2.7-B0-ENHANCED development，B3b typed condition–constraint ownership。
- **观察事实**：固定 v10-A 的 580 条 condition/constraint span 经 CoreNLP 4.5.10、固定 v3 Tregex、lexicon v2 与 v10 scope 重放完全一致。冻结规则产生 constraint→condition 79 次 firing、condition→constraint 8 次 firing；实际改变 87 spans/53 records，其中 59 条因 target exact/overlap 等价而只删除 source。268 个 ambiguity 实例 100% 保持，capacity fail-closed=0，span boundary/new raw span/非目标字段变化均为 0。
- **影响**：虽然 constraint FP 减少 57、overall FP 减少 35，但 constraint TP 损失 22；condition TP 反而减少 2、FP 增加 22；overall TP/FP/FN 从 458/415/366 变为 434/380/390，F1 从 0.539776 降至 0.529915。presence recall 下降 0.037915、complete-record 下降 0.12，hallucinated-field rate 上升 0.001144。说明 current clause 的 condition evidence 无法安全决定 clause 内所有 constraint span 的 ownership。
- **处置方法**：严格执行停止条件，决定 `not_instantiated`。保留只读 Gold opportunity diagnostic；没有创建 `typed_ownership_b3b.py`、生产 runner/config/prereg 或候选输出，没有运行候选 All-150，没有修改 Gold、v10-A、lexicon、Tregex、bridge、scope、evaluator 或 active registry，也没有调参、重跑性能候选或启动下一阶段。
- **验证证据**：诊断 manifest 绑定固定父版/lexicon/scope/evaluator/Tregex/bridge；24 项预运行定向测试与诊断产物自洽/无生产候选测试通过，完整测试和完整性结果由 Event 110 绑定。
- **状态**：`open`。当前 typed evidence 粒度不足以实例化为生产 ownership resolver；development Gold 诊断不是独立泛化结果，B3c/actor/marker expansion/Tsurgeon/BERT 均未启动。

### RWI-0019 — 白名单强否定范围不足以实例化 B2b prohibition 修复

- **首次发现**：2026-07-23。
- **阶段/范围**：S2.7-B0-ENHANCED development，B2b prohibition↔permission
  只读诊断。
- **观察事实**：固定 v10-A 中有 6 条对齐的 Gold prohibition→pred permission，另有
  Gold prohibition→pred obligation 2 条、unmatched Gold prohibition 10 条和 extra
  predicted prohibition 6 条。严格按预先限定的 `may/shall/must not`、否定被动许可、
  `no <subject> may/shall`、`prohibited/forbidden from` 白名单重算后，6 条目标错误中
  仅 1 条为 `no-subject modal`；其余 5 条没有可用的白名单 clause-local 信号。
- **影响**：固定规则预计只触发 1 条，可恢复 prohibition TP 上限为 1，低于“至少 3
  条共享允许强信号”的实例化门槛。若把 `may … neither/nor` 或 `may … no longer`
  擅自加入，会越过本轮明确的证据族边界。
- **处置方法**：诊断写为 `not_instantiated`，保留聚合桶和完整 SHA-256 绑定；没有创建
  生产 resolver/config/runner/tests，没有预注册或运行 All150，也没有修改 v10-A、
  active registry、Gold、evaluator、lexicon、Tregex 或 BERT。
- **验证证据**：诊断 manifest
  `e0cdc8956eafb76c97a915460b2fcf62f53a8b671eb04f00d27cae0c92de9d44`；
  summary `571fc2977fc9017d4ec049311142f764e121a2c73ab0919c0010cc9513d43886`；
  v10-A/B2a/B2a2 回归 47 passed。全量测试和完整性结果由 Event 106 绑定。
- **状态**：`open`。现有允许证据不足以支持 B2b 泛化规则；本轮按停止条件结束，不以
  development Gold 诊断冒充独立泛化结果。

### RWI-0018 — B2a definition 拒绝路线复制 record 标签，子句受限解码又损失真实定义

- **首次发现**：2026-07-23。
- **阶段/范围**：S2.7-B0-ENHANCED development，B2a 负证据与 B2a2 单一增量假设。
- **观察事实**：相对固定父项 v10-A，B2a 新增 40 条 `record_level_classifier_fallback`；其中 29 条同时出现 clause classifier=`definition`、record classifier=`definition`，仍因未满足严格结构而走 record 回退。只读路线诊断确认 40/40 条都能从同一已对齐德文子句恢复合法四分类概率向量，且没有使用 record 文本生成子句概率。
- **影响**：B2a 的路线名和实际决策层级矛盾，受支持子句重新依赖 record 标签；但把所有被拒 definition 强制解码为 obligation/permission/prohibition 会把其中仍属真实 definition 的条目一并移除。
- **处置方法**：预注册 B2a2 唯一规则：保持 v10-A、强定义、德英 definition 锚点和显式道义标记不变；只在受支持子句的 classifier definition 被拒时，对同子句概率向量的 obligation/permission/prohibition 做无附加阈值 argmax；无合法子句向量时精确保留 v10-A；禁止 record 覆盖、样本 ID 规则、占位输入、调参、第二候选和重跑。
- **验证证据**：路线诊断 40/40 概率向量有效；聚焦测试 47 项通过。唯一 All150 中受限路线=40、总 record fallback=20、受支持子句 fallback=0、占位=0，A1–A5 全通过；predicted/aligned=256/195，alignment、exact segmentation、Table8、字段、coverage、actor-action edges、schema 均与 v10-A 精确一致，E1–E9 全通过。但 definition TP/FP/FN=2/13/37、P/R/F1=0.13333/0.05128/0.07407，整体 modality TP=142、P/R/F1=0.55469/0.61472/0.58316，B/C/D 失败。
- **状态**：`mitigated`。路线复制缺陷已由 B2a2 候选消除，但性能门槛失败证明该受限解码不是可晋级修复；B2a2 以负证据保留，未修改 active registry、阈值或规则，也未重跑。对应 Event 105。

### RWI-0014 — 方法本地 ID 与 exact boundary 造成 B0 评价系统性低计

- **首次发现**：2026-07-21。
- **阶段/范围**：S2.10-E evaluator；S2.7-B0 development re-evaluation。
- **观察事实**：冻结 Gold 的 231 个 clause 与 B0 预测没有共享 clause ID；v1.1 只能再用完全一致 raw span，最终只对齐 40 个 clause。82 条单 Gold/single-pred 记录中，79 条字符 span IoU≥0.95，但只有 21 条完全一致，典型差异是句末标点。旧报告因此把可对齐 clause 及其所有 entity/modality 当成大量 missing/extra。
- **影响**：旧 all-150 modality accuracy/macro-F1=0.103896/0.090583 不是可信的 B0 性能估计；它混合了方法错误与 evaluator 身份/边界错误。若直接据此选择 H1/D1、写论文或与文献值比较，会夸大失败。
- **解决方法**：新增 `stage2_evaluator_contract@1.2.0`。record 仍按 exact sample ID；clause 使用固定、方法无关、全局最大总权重的一对一字符-span IoU，对齐阈值在重算前固定为 0.5；entity ID 明确视为 method-local，strict/safe/token 三类指标分别按 raw span、安全规范化文本和正 token IoU 匹配。exact clause segmentation 继续独立报告，禁止数组位置、阈值搜索和论文分数目标化。v1.1 报告保留为被替代的 development provenance，不删除或覆盖。
- **验证证据**：8 项 evaluator 回归/对抗测试与 4 项 exact-gate 测试通过；synthetic exact metrics 不变；不同 ID + 单字符 boundary 对抗例 exact match=0 但 semantic alignment=1；共享 ID 的不相交 span 被拒绝；输入和 clause 数组顺序不影响报告。immutable B0 attempts 未重跑模型即重算：all-150 clause alignment P/R/F1=0.680451/0.783550/0.728370，modality micro P/R/F1=0.394737/0.454545/0.422535，macro-F1=0.406801；0 LLM/API、0 network。exact-hash gates 通过。对应 Event 86。
- **状态**：`resolved`。修复只解决 measurement defect；B0 对 actor/action/constraint/exception 的真实抽取不足仍存在，formal Gold publication 与 RWI-0001/RWI-0007 门禁不变。







### RWI-0017 — S2.4 test 被多候选暴露

- **首次发现**：2026-07-22。
- **阶段/范围**：S2.4-CAND / B0 enhanced classifier selection。
- **观察事实**：`train_s24_bert_textcnn_candidates.py` 对 candidate B 与 C 均在 best-dev 后执行了一次 test 评估；selection 排序仅用 dev macro-F1，但 test 已暴露。
- **影响**：S2.4 test 不再是干净的一次性最终确认；后续不得再用 test 选模型/seed/epoch/loss/sampler。
- **解决方法（进行中）**：v8 preregistration 禁止本轮访问 S2.4 test；B 的 test 0.877 仅 exploratory/report-only；若需稳定性只允许 train/dev multi-seed。
- **验证证据**：candidate B/C manifests 均含 `test.evaluation_count=1` 与 `used_for_selection=false`。
- **状态**：`open`。

### RWI-0016 — Minimax v6 Phase A 诊断无效（伪造 classifier_only / 未运行 oracle / 错误 overlap）

- **首次发现**：2026-07-22。
- **阶段/范围**：S2.7-B0-ENHANCED development diagnostics。
- **观察事实**：
  1. `analyze_estg150_b0_v6_components.py` 的 `classifier_only` 使用 `ModalityPrediction(stored_hybrid_label, 0.6)`，使 classifier_only 与 hybrid 指标人为相同。
  2. Gold clause segmentation oracle 依赖可选 `--gold-source-records`，默认未生成 oracle artifact，却被汇报为“四路消融”。
  3. overlap audit 读取不存在的 `data/development/sun_modality/{train,dev,test}.jsonl`（0 行），并用 Gold `source_text`（approved English）与 sample_id 关联，仍输出 exact/normalized/substring=0。
- **影响**：不能对 classifier vs marker vs hybrid 做因果归因；不能估计 segmentation ceiling；不能判断 EStG-150 与 S2.4 modality 数据泄漏/重叠。
- **解决方法**：新增只读纠正脚本 `scripts/analyze_estg150_b0_phase_a_correction_v1.py` 与产物目录 `outputs/development/s27_estg150_b0_phase_a_correction_v2/ (v1 provisional retained)`。不删除 v6 或旧 diagnostic 目录；明确标记 invalid。
- **验证证据**：真实 classifier_only F1=0.439 与 hybrid F1=0.624（锁定 v5）相差 87 个 clause；Gold-seg hybrid F1=0.788 且 pred=gold=231；S2.4 split 实际加载 train/dev/test=1985/420/426；exact/normalized overlap=0，near-dup=52。focused tests 4 passed。
- **状态**：`mitigated` / partially_resolved（假 classifier 与路径错误已纠正；仍缺 aligned-only coverage、marker abstention-aware 指标、v5-routing-fixed oracle、可靠 near-dup）。完成 v8 residual 诊断并验证前不得 re-resolve。
  - 2026-07-22：落地 `s27_estg150_b0_phase_a_residual_v3`（aligned-only F1=0.277, unsupported=184/256, marker supported F1=0.662 abstain=67, gold v5-routing F1=0.784 vs v8-hyp 0.788）；状态仍 `mitigated`。
  - 2026-07-22：确认 v8-A `de_for_clf.append('.')` 缺陷与 v8-C no-op；correction manifest `s27_estg150_b0_v8_status_correction_v2`；不得用 v8-A 做 alignment 归因。
- **状态历史**：
  - 2026-07-22：初标 resolved。
  - 2026-07-22：审查发现 residual 缺陷，降为 mitigated。
- **状态历史**：
  - 2026-07-22：发现并纠正，状态 `resolved`。

### RWI-0015 — B0 record→clause 标签复制与过分割/单 span 抽取缺陷

- **首次发现**：2026-07-21。
- **阶段/范围**：S2.7-B0-DEV / B0 enhanced development。
- **观察事实**：`run_b0_batch()` 对每条 Layer E 记录只对整段 `raw_text_de` 调一次 S2.4 分类器，再将同一标签复制到该记录全部 CoreNLP 英文句；34 条 multi-modality 记录因此系统性失真。预测 266 句 vs Gold 231 clause；bridge/parser/composer 每字段只保留一个 match；actor 过宽、constraint/exception 规则过窄。
- **影响**：S2.4 组件 test macro-F1≈0.85 在 EStG-150 端到端降到 modality micro F1≈0.42；complete-record rate 仅 0.06。
- **解决方法（部分）**：新增 versioned `b0_enhanced`（不冒充 paper-faithful B0）：句级 DE 单元对齐 + 英文 public-marker 优先 modality；CoreNLP 列表碎片 merge 与协调模态 split；`SunPhraseRuleBatchBridgeMulti` 多非重叠 match；v2 增强 Tregex；actor 过滤；独立 `sun_table8_any_overlap_diagnostic`。旧 v1 产物完整保留。
- **验证证据**：v3/v4/v5/v6 development runs 已版本化保留。最新 `s27_estg150_b0_enhanced_v5`：modality micro P/R/F1=0.594/0.658/0.624、clause alignment F1=0.801、complete-record=0.347、Table8 any-overlap F1=0.492；v4 因过激 multi-predicate 欠分割回退已保留为负向证据；v6 用 v4 patterns (51) + v2 lexicon (161 entries) 替代 v3 (29) + v1 (64) 的组合并改写 phrase resolver，结果是 **回归**：modality micro F1 0.593 (-0.031)、clause alignment F1 0.769 (-0.032)、exact F1 0.127 (-0.017)、predicted 258 (+2) / aligned 188 (-7)；v6 保留为负向 evidence，v5 仍为 current best；0 LLM/API；未改 Layer E/Gold。
- **状态**：`mitigated`。v5 相对 v3 在 alignment/complete-record/Table8/exception 有改进，modality 小幅提升；v6 的扩展（更大 lexicon 与 patterns、clause nucleus 规则、更严 actor 过滤）反而引起 definition/permission 过召回与 alignment 退化；v7 小幅晋级；v8-A 因 placeholder `.` classifier 输入不可归因；v8-C 为 B 的 no-op 重复；v8 status correction v2 + active_registry_v1 已落盘；provisional best 仍为 v7（modality micro F1 0.624→0.628，align/Table8 持平）；相对 Sun Table7（F1≥0.831）仍差约 20pp，Table8 overall 仍差约 40pp；主要剩余：definition↔obligation 混淆、constraint 召回、actor 过召回、segmentation ceiling≈0.76/0.84；RWI-0001/0007 仍 open。
- **状态历史**：
  - 2026-07-21：`open`，由 v1 record→clause 标签复制与过分割/单 span 抽取缺陷发现。
  - 2026-07-21：v3/v4/v5 已分阶段落地、v4 负向保留；状态改为 `mitigated`。
  - 2026-07-21：v6 (b0_enhanced_v6) 跑完但相对 v5 整体回归；按 RWI 规则不创建新问题，在原 ID 状态历史中追加 v6 失败证据；状态保持 `mitigated`，v5 仍为 current best。

### RWI-0013 — Tsurgeon 完整树删除使真实 B0 批处理终止

- **首次发现**：2026-07-21
- **阶段/范围**：S2.7-B0-DEV；CoreNLP/Tregex/Tsurgeon 六要素批处理。
- **观察事实**：首次 EStG-150 B0 development run 在全局第 220 个 CoreNLP 句子上命中
  constraint 后，`prune constraint` 返回 `null`；原单 fixture bridge 抛出
  `Tsurgeon removed the complete tree`，使整批 fail closed，且没有发布半成品。
- **影响**：如果没有显式边界，单个合法但极端的 constituency match 会让前面已完成的
  219 句全部作废；如果静默跳过又会掩盖规则失败并改变后续 action/actor 语义。
- **解决方法**：不修改已锁定的 `SunPhraseRuleBridge.java` 和 12 条规则；新增 development
  batch bridge。完整树被剪空时仍计入 surgery，当前命中字段保留，后续字段显式输出
  miss，记录 `terminal_tree_removal_count`，然后继续下一句。
- **验证证据**：聚焦测试 7 passed；重跑覆盖 150 records / 266 sentences，全部 150
  canonical attempts 成功，`terminal_tree_removal_count=2`；exact-hash gate 绑定 bridge、
  config、runner、manifest 和 150/82 两份 evaluator 结果。对应 Event 85。
- **状态**：`resolved`。该修复只支撑 development B0，不解除 RWI-0001/RWI-0007，
  也不把结果提升为 formal performance result。

### RWI-0001 — 句级抽样造成跨句上下文和代词先行词丢失

- **首次发现**：2026-07-18
- **阶段/范围**：S2.2 人工 Gold；后续 B0/H1/D1 输入与 S2.10 评价公平性
- **观察事实**：`estg_000003` 的活动德文记录从
  `Einen kürzeren Zeitraum darf es dann umfassen ...` 开始，英文候选为
  `It may cover a shorter period ...`。当前样本没有保留同一法条上一句；官方
  EStG §2(6) 的上一句说明 `Wirtschaftsjahr` 通常覆盖十二个月，因此
  `es/It` 回指 financial year，`shorter` 的比较基准是十二个月。
- **本地证据**：
  `data/development/human_review/estg_150_human_correction_v1.json`
  中 `sample_id=estg_000003`；D1/H1 当前 prompt 和 runner 只接收当前
  `source_text`，没有 preceding/following context 字段。150 条逐条审查结果位于
  `outputs/development/estg150_independence_audit_v1/`，包含工作簿、逐行 JSONL 与
  source/output hash manifest；该报告是只读审核辅助，不是 Gold。
- **影响**：若人工依据外部上一句消解 Gold，而 B0/H1/D1 只看到当前句，模型会被
  要求预测输入中不可观察的信息；若不消解，actor、比较基准和独立规则语义又不完整。
  这会影响翻译、span、actor/action Gold、方法公平性和结果解释。
- **当前临时处置**：句级盘点将 150 条分为独立 82、需上下文核实 26、不独立 42。
  后两类不得依据报告自动填充 Layer E；人工审核时将缺失先行词、比较基准、列表主句、
  截断或外部范围依赖留作 `needs_adjudication` 并写入 review notes。可以继续审核独立
  记录；这些记录可以进入 sentence-only English annotation freeze，但在问题未闭合时
  不得据此发布 formal Gold 或运行正式 B0/H1/D1 比较。
- **状态**：`open`
- **尚未解决的设计项**：
  1. 已完成 150/150 句级独立性与上下文依赖盘点，并生成只读审核辅助报告；
  2. 决定并锁定 preceding/following/section context sidecar 及来源 hash；
  3. 保证 B0/H1/D1 获得同一可见信息，或预注册 sentence-only 与
     context-assisted 两条评价轨道；
  4. 规定 target span 与 context-derived evidence 的不同来源表示；
  5. 在不改变既有 150 membership 的前提下更新输入与评价合同。
- **解决方法**：尚无；不得填写为已解决。
- **阶段性验证证据**：逐行 JSONL 恰好 150 个唯一 `sample_id`，分类计数为
  82/26/42；XLSX 四个工作表可重新导入，摘要公式值与逐行计数一致，公式错误扫描为
  0，并已逐表渲染复核。未修改 Layer E，未调用真实 LLM/API。根因仍待 context
  sidecar、来源 hash、目标 span/context evidence 表示与方法公平输入合同共同闭合，
  因此不得写为已解决。
- **状态历史**：
  - 2026-07-18：`open`，由人工审核 `estg_000003` 时发现并确认当前方法输入只有
    单句 `source_text`。
  - 2026-07-18：完成 150/150 句级盘点（独立 82、需上下文核实 26、不独立 42），
    状态仍为 `open`；盘点结果只作人工审核辅助，没有写入 Gold。

### RWI-0002 — 六要素长候选在 GUI 中被裁切

- **首次发现**：2026-07-18
- **阶段/范围**：S2.2 人工审核工具
- **观察事实**：六要素表格使用不会换行的单行标签，主体、行为和约束候选只能显示
  前半段，用户无法可靠核对完整候选。
- **影响**：可能导致误接受、误修改或依赖上方原始 JSON，增加人工错误。
- **状态**：`resolved`
- **解决方法**：候选单元格改为只读自动换行文本，普通候选显示 1–3 行；双击打开
  可滚动、可复制的完整候选全文，并重新分配表格列宽。
- **验证证据**：审核工具聚焦测试 45 passed；全量 1102 passed、22 skipped；
  完整性检查通过。
- **对应事件**：Event 73。
- **状态历史**：
  - 2026-07-18：发现并于同一批次 `resolved`。

### RWI-0003 — 接受决策与人工结果物化断链

- **首次发现**：2026-07-18
- **阶段/范围**：S2.2 Layer C → Layer E 人工审核
- **观察事实**：旧工具点击字段“已接受”只更新 decision，候选值与精确 span 没有
  复制到 `human_correction`；右侧 JSON 又表现为可编辑但修改不会被收集。
- **影响**：界面可能显示“已接受”，实际人工结果仍为空，形成无效 Gold。
- **状态**：`resolved`
- **解决方法**：逐字段接受和整条接受都由用户点击后显式物化不可变候选与精确
  span；缺少可靠 span 时 fail closed；拒绝清空旧人工值；右侧改为只读预览；关系
  JSON 增加保存与引用校验。
- **验证证据**：聚焦测试 44 passed；全量 1101 passed、22 skipped；没有自动修改
  reviewed/adjudicated 状态。
- **对应事件**：Event 72。
- **状态历史**：
  - 2026-07-18：发现并于同一批次 `resolved`。

### RWI-0004 — DeepSeek thinking 模式返回空正文

- **首次发现**：2026-07-18
- **阶段/范围**：Layer D 中文辅助与盲回译生成
- **观察事实**：首个 `deepseek-v4-flash` provider-default thinking pilot 返回空正文，
  导致 Layer D 记录无法完成；失败 run 原样保留为 provenance。
- **影响**：若只检查 HTTP 成功而不检查正文完整性，可能把空中文/回译错误激活为
  审核辅助层。
- **状态**：`resolved`
- **解决方法**：固定 `thinking_mode=disabled`，补强 run_config、顺序、SHA、150/150
  完整性和 promotion 校验；失败运行不覆盖，成功 v2 原子激活。
- **验证证据**：成功 run 150/150 中文、150/150 盲回译，25 项严格校验通过。
- **对应事件**：Event 71。
- **状态历史**：
  - 2026-07-18：首轮失败后定位；第二轮禁用 thinking 并验证，状态 `resolved`。

### RWI-0005 — 活动测试把人工审核进度错误写死为 0/150

- **首次发现**：2026-07-18
- **阶段/范围**：全项目回归测试；S2.2 Layer E 人工审核
- **观察事实**：用户完成首条裁决后，Layer E 合法进度变为 `adjudicated=1/150`；
  `test_formal_project_audit.py` 和 `test_layer_d_runner_and_validator.py` 仍断言必须
  `adjudicated == 0`，因此全量检查出现 2 个失败。2026-07-21 用户完成 150/150 后，
  `test_formal_project_audit.py` 与 `test_s26_sun_b0.py` 又保留 `freeze=false` /
  `annotation_freeze_pending` 的旧状态断言；另两项 hash 篡改测试依赖文件仍含
  `unreviewed`/`needs_review`。全量回归共出现 5 个同类真实失败。
- **影响**：正常人工进度被误报成项目损坏；若为通过测试而恢复 0/150，会直接覆盖
  用户 Gold，违反人工结果不可由 Agent 回退的边界。
- **状态**：`resolved`
- **解决方法**：移除对活动人工进度的固定零值假设，改为验证 150 条 membership、
  合法状态集合、唯一 sample ID，以及 `review_ready`/`freeze_ready` 与实际完成度的一致性。
  测试不再要求用户停留在某个进度，也不会修改 Layer E。
- **验证证据**：首次修复后相关测试连同登记册结构回归共 13 passed；2026-07-21
  首轮修复后 S2.2/audit/S2.6/contract 聚焦回归 36 passed；全量发现的剩余五项
  也改为读取当前已决状态并构造状态无关篡改，最终由本次 S2.2 freeze
  事件和全量门禁绑定。
- **对应事件**：Event 74；2026-07-21 S2.2 annotation-freeze 事件。
- **状态历史**：
  - 2026-07-18：发现并修正测试语义，等待验证，状态 `mitigated`。
  - 2026-07-18：聚焦回归 13 passed，状态改为 `resolved`。
  - 2026-07-21：150/150 后发现同类 stale freeze 断言，问题复现并临时重开；改为
    验证当前 validator/gate 事实后 36 项聚焦回归通过，状态恢复为 `resolved`。

### RWI-0006 — 终端乱码被误判为持久化日志损坏

- **首次发现**：2026-07-18
- **阶段/范围**：变更事件记录后的 PowerShell/工具输出显示
- **观察事实**：读取 Event 74 和人类日志的超长混合输出时，终端回显把正常中文显示为
  `æ.../å...` 形式，初看像命令行参数和追加日志已经损坏。
- **再次出现**：2026-07-26 首次 C1 修复全量检查中，两个 GUI `--help` 子进程按 Windows
  legacy code page 输出中文，而 pytest 固定用 UTF-8 解码，形成 U+FFFD 并造成 2 个测试
  失败；`audit_project.py` 随后又因 GBK 无法编码 U+FFFD 而在打印失败正文时崩溃。工具源
  文件和用户数据均未损坏。
- **影响**：如果直接按终端画面判断，可能错误修改追加式历史或为不存在的数据损坏
  引入不必要的编码修复。
- **状态**：`resolved`
- **解决方法**：不修改既有 Event 74；改用 `rg` 对持久化文件执行正常中文和典型
  mojibake 模式的双向精确检查，以文件内容而不是一次终端渲染作为判据。以后遇到
  同类显示先做文件级核验，再决定是否需要修复。
- **2026-07-26 补强**：强制完整性检查启动的 pytest 及其嵌套 Python 子进程使用
  `PYTHONUTF8=1`；audit 打印诊断前按当前控制台编码执行 `errors=replace` 的显示层转换。
  不改两个审核工具、不改 Layer E，也不把显示问题写回任何数据文件。
- **验证证据**：正常中文在 `EXPERIMENT_LOG.md` 第 664/674 行和
  `EXPERIMENT_EVENTS.jsonl` Event 74 命中；典型乱码模式命中数为 0。
- **对应事件**：Event 75。
- **状态历史**：
  - 2026-07-18：显示异常出现后先疑似 open；文件级核验确认持久化内容完好，
    同批次 `resolved`。
  - 2026-07-26：全量检查中的嵌套子进程编码使问题 reopened；测试入口与诊断输出完成
    显式编码加固后重新 resolved，验证绑定本批次完整检查/change event。

### RWI-0007 — 德文来源、英语方法与非德语人工审核之间的语言缺口

- **首次发现**：2026-07-18
- **阶段/范围**：S2.2 EStG-150 人工 Gold；S2.5 英语 phrase extractor；后续
  B0/H1/D1 公平比较与论文主张
- **观察事实**：Michel 2022 的 EStG 原始语料是德文。Sun 2024 的 phrase-level
  方法明确描述 “sentence structure of English language”，使用英语 marker、英语例句、
  Stanford CoreNLP 句法树和英语 BERT 模型；但论文在“同样使用 Austrian income tax
  law”与这些英语组件之间没有说明翻译、人工改写或其他语言转换步骤。因此，现有
  证据既不能证明直接在原始德文上抽取，也不能证明使用了哪一种德译英流程。
- **额外事实**：当前 Layer D 中文辅助由英文候选生成，再从中文回译为英文；它能
  帮助中文审核者理解和检查英文内部漂移，但不能独立验证最上游德文到英文是否忠实。
- **影响**：不会德语的审核者不能对德译英忠实度作人工保证。若把“接受英文候选”
  写成“人工验证了德文翻译”，会夸大 Gold 质量；若要求用户直接在德文上标 span，
  又不可执行。Sun 的 443 phrase 指标也不能与本项目翻译轨道直接称为同数据复现。
- **当前临时处置**：人工审核范围限定为**冻结英文工作文本上的六要素和英文 span**；
  点击接受英文候选表示采用该英文作为工作文本，不表示审核者证明其与德文完全等价。
  英文内部清楚的记录可以继续；疑似错译、代词/比较基准缺失或必须懂德文才能裁决的
  记录标 `needs_adjudication`。论文在问题解决前只能称
  `LLM-translated English working text with human-adjudicated English spans`，不得称
  `human-verified German-to-English translation`。
- **状态**：`open`
- **尚未解决的设计选择**：
  1. 以原生英文法规作为 phrase-level 主评价集，把 EStG-150 降为跨语言适配轨道；或
  2. 保留 EStG-150 主轨道，但增加相互独立的德→英、德→中翻译以及德语能力审核者
     对全部记录或预注册抽样与所有疑难记录的复核；
  3. 无论选择哪条路线，都要在结果前锁定模型可见语言、翻译 provenance、人工审核
     能力边界和可报告主张。
- **解决方法**：尚无；需要先锁定上述语言 QA / 主次数据轨道选择。
- **验证证据**：Sun 论文 §4.2.2、§5.1–§5.2 的英语方法描述与 EStG 数据描述；
  本项目 `SUN_REFERENCE_SNOWBALL_AND_MARKER_AUDIT.md` 的既有语言缺口审计；当前
  Layer D prompt/data flow。
- **状态历史**：
  - 2026-07-18：确认用户不具备德语审核能力，状态 `open`；允许继续英文工作文本
    内部的六要素审核，但禁止把它表述为德译英人工验证。

### RWI-0008 — 人工、D1 与 H1 的六要素操作语义未统一

- **首次发现**：2026-07-19
- **阶段/范围**：S2.2 人工 Gold、S2.8 H1、S2.9 D1、canonical schema 与 Part 3
  admission
- **观察事实**：既有材料虽然共同列出 modality/actor/action/condition/constraint/
  exception，但没有以一个版本化合同统一最小 span、exact/normalized 边界、代词
  `It/they/this/these/such`、无显式 actor 的被动句、missing 与 uncertain、并列/多
  clause、condition/constraint/exception scope，以及 H1 如何在局部 patch 中保留
  `unsupported_or_ambiguous`。这会使同一句在人工、D1、H1 间产生方法外差异。
- **影响**：若不先冻结，后续差异可能来自提示词/标注定义漂移，而不是方法能力；无
  句内先行词的 `It` 还可能被静默补成外部主体，或在 H1 merge 后丢失不可进 Part 3
  的状态。
- **状态**：`resolved`
- **解决方法**：新增 `stage2_extraction_contract@1.0.0` 与人读合同，明确 sentence-only
  输入、六字段最小精确 span、受控不确定性、代词保留、被动隐含 actor 禁止推断、
  clause/coordination、方法可见性、统一评价与 Part 3 admission。D1/H1 同步为 v5；
  H1 envelope 完整替换顶层 ambiguity list；现有 canonical schema 因已支持 exact/
  normalized 和受控元数据而保持 byte-identical。12 条既有 EStG 记录只作为 hash-bound
  静态覆盖 pilot，不成为 Gold、few-shot 或性能样本。
- **验证证据**：合同与 bundle hash 回归、D1 四个手工 synthetic canonical 示例、H1
  unresolved-`It` metadata merge 正负路径、pilot ID/source-text hash/coverage/no-prompt-
  leakage 检查；S2.8 v6 与 S2.9 v5 离线 manifest exact-hash gate。最终全量测试计数由
  Event 78 绑定。
- **对应事件**：Event 78。
- **状态历史**：
  - 2026-07-19：发现跨入口语义未完全同源，登记为 `open`；
  - 2026-07-19：合同、提示词、merge、pilot、bundle 与 gate 同批次锁定，改为
    `resolved`。RWI-0001 和 RWI-0007 不受此状态变更影响，继续 `open`。

### RWI-0009 — 六要素人工值导航后显示为空且存在未提交风险

- **首次发现**：2026-07-20
- **阶段/范围**：S2.2 EStG-150 Layer E 人工审核工具
- **观察事实**：用户输入 action 并切换记录后，人工值输入框显示为空。文件级核验
  证明该 action 已作为 `human_correction.clauses[].actions[]` 正常落盘；GUI 重新加载
  却用单数键 `action` 读取。actor、condition、constraint、exception 存在同类单数/
  复数映射错误。同时，上一条/下一条/下一条待审只收集最终英文，六要素仍依赖输入框
  `FocusOut` 的事件顺序，直接导航存在未提交风险。
- **影响**：已保存的人工结果会在界面上看似消失，干扰用户来回检错；尚未触发
  `FocusOut` 的值还可能真的未写入 Layer E。若用户据此重复录入或改判，会增加人工
  Gold 错误风险。
- **状态**：`resolved`
- **解决方法**：统一用显式映射从 `actors/actions/conditions/constraints/exceptions`
  数组恢复人工值及字段决策；上一条、下一条和下一条待审在切换前统一收集英文、六
  要素、关系与备注并保存。人工值无法形成唯一 exact span 或关系 JSON 无效时阻止
  导航、聚焦错误字段并保留当前输入；未变化字段不重复调用 edit，避免把 accepted/
  rejected 静默改为 edited。“保存”“已复核”“已裁决”也复用同一提交屏障。
- **验证证据**：新增无窗口 GUI 回归，覆盖五个复数 span 字段回显、导航前 action
  落盘、无 exact span 时停留当前记录；审核工具聚焦测试 48 passed。全量验证计数由
  Event 79 绑定。测试仅使用临时工作区，没有修改用户 Layer E 决定。
- **对应事件**：Event 79。
- **状态历史**：
  - 2026-07-20：用户在真实审核中报告导航后人工值为空，登记为 `open`；
  - 2026-07-20：完成复数键回显和导航提交屏障并通过聚焦回归，改为 `resolved`。

### RWI-0010 — 第三方中转无法独立证明模型身份、参数透传与计价单位

- **首次发现**：2026-07-20
- **阶段/范围**：S2.2 EStG-150 AI 裁决候选；ChatAnywhere OpenAI-compatible
  中转；`gpt-5.6-sol`
- **观察事实**：用户在中国大陆无法使用原始 OpenAI API，拟使用第三方中转。服务页
  展示 `gpt-5.6-sol`、输入 `0.035/1K Tokens [7阶梯计价]`、输出
  `0.21/1K Tokens`，并给出完整端点
  `https://api.chatanywhere.tech/v1/chat/completions`，但截图没有可独立核验的币种，
  中转返回的 model 字段也只能代表中转方声明，不能从客户端密码学证明实际后端模型；
  `reasoning_effort=high` 与 strict JSON Schema 是否完整透传同样必须经付费小试验证。
- **影响**：若直接批跑 150 条，可能在未知币种/阶梯下超预算，或在中转静默降级参数、
  替换模型时生成不可复现的候选。第三方还增加数据处理、服务可用性与地域合规风险。
- **状态**：`mitigated`
- **当前处置**：建立独立 development-only 双轮候选通道，固定请求
  `gpt-5.6-sol`、`reasoning_effort=high`、strict JSON Schema，禁止参数降级并要求返回
  model ID 精确匹配；端点同时接受 `/v1` 与完整 `/v1/chat/completions`，规范化后只请求
  一次。脚本不读取 DeepSeek Layer D 或 Layer E，不写人工状态；密钥只通过隐藏输入或
  用户指定环境变量读取，不进命令行、日志或文件。真实调用另需确认第三方风险、
  非人工输出性质、实时币种、输入/输出单价、总预算和调用上限。pilot 限 1–5 条，
  不会自动继续 150 条。
- **尚未解除的根因**：第三方模型身份和实际后端不能由本项目独立证明；服务条款、
  数据处理边界和截图计价单位仍需用户在账户页确认。只有 3–5 条 pilot 验证响应 model、
  strict schema、reasoning 参数、usage 和账单增量后，才能决定是否单独授权全量运行；
  即使通过也只能记录为第三方中转声称的模型身份。
- **托管环境实测**：用户先确认第三方风险、币种/单价和 3 条/15 CNY 预算，又在获知
  将外发德文原句、冻结英文、旧六要素草稿及首轮输出后再次明确授权。Codex 托管策略
  仍拒绝向不受信任的 ChatAnywhere 中转外发私有工作区数据；两次启动均在创建 run
  目录、读取密钥或发出 HTTP 请求前停止。不得用手工命令、间接进程或其他方式绕过。
  用户随后明确授权安全替代：两个相互独立的 Codex 内置 `gpt-5.6-sol` 子代理在同一
  工作区完成前 3 条 Pass A/Pass B development pilot。Pass A 只读 Layer A/B；Pass B
  只读 A/B、hash-locked Pass A 和相关 Layer C，均未读 D/E。3/3 两轮输出和根代理复验
  均通过 strict schema、exact span 与关系引用校验；未调用外部 API，外部中转费用为 0。
- **验证证据**：离线端点规范化、请求体、三层 membership join、密钥/预算/全量闸门、
  JSON Schema 子集与 exact-span/关系交叉校验回归；本批次未调用真实 API，最终测试
  计数由对应实验事件绑定。
- **对应事件**：Event 80（离线准备）、Event 81（中转策略拒绝）、Event 82（内置 Sol
  双轮 3 条 development pilot）。
- **状态历史**：
  - 2026-07-20：根据用户提供的中转配置与计价截图登记为 `open`；
  - 2026-07-20：完成 fail-closed pilot 通道和离线回归，改为 `mitigated`；模型身份与
    参数透传根因在真实 pilot 前后均不能视为 `resolved`；
  - 2026-07-20：用户两次知情授权后，托管策略仍在密钥读取/API 调用前拒绝第三方
    数据外发；ChatAnywhere 路线在本环境中停止，不作绕行，状态保持 `mitigated`；
  - 2026-07-20：用户明确授权内置 Sol 子代理替代路线；3 条双轮 pilot 3/3 严格有效，
    但第三方中转不可验证的根因并未消失，状态保持 `mitigated`。

### RWI-0011 — 高级审核状态机和手工 span 给简单六要素修正增加无效负担

- **首次发现**：2026-07-20
- **阶段/范围**：S2.2 EStG-150 Layer E 人工修改界面
- **观察事实**：用户实际使用后明确指出，旧两标签页工具同时暴露翻译决定、六字段
  accepted/edited/rejected/needs-adjudication、reviewed/adjudicated、关系 JSON 和手工 span
  控件。对“Sol 先提取，用户只改少量错误”的任务而言，这些控件把同一条最终确认
  拆成多次点击，界面拥挤，容易让用户把精力花在工作流状态而非法律语义上。
- **影响**：150 条审核的点击数和认知负担显著增加；用户可能因 offset、ID 或状态机
  操作失误而不是语义判断失误造成无效记录，也可能因此放弃完成 150 条。
- **状态**：`resolved`
- **解决方法**：新增 `estg150_simple_review_tool.py` 作为推荐入口。界面只显示法规英文、
  Sol 拆出的全部 clause、modality 和五类 span 文本；每个 span 一行，offset 与 ID 由后台
  精确定位并 fail closed。用户只有“上一条”“稍后再看”“查看德文原文”和
  “保存并下一条”；最后一个按钮是对当前显示结果的一次明确最终决定，service 在内存
  中依次执行既有两个门禁，再备份、原子写入和全局校验。未点击时 Sol 候选不写 Layer E；
  已完成的用户记录从 Layer E 优先回显，不被 Sol 静默覆盖。旧高级工具保留为疑难情况
  的备用入口。
- **验证证据**：聚焦测试覆盖 strict 候选加载、无改动重建、正文不存在的 span 拒绝、
  一键物化、不可变 Layer C 保持、真实 Layer E 防污染、无旧状态按钮和 headless help；
  150 条 aggregate 另经 schema、sample 顺序、exact span、关系引用和规范性 cue 覆盖检查。
  最终全量测试计数与 aggregate hash 由 Event 83 绑定。
- **对应事件**：Event 83。
- **状态历史**：
  - 2026-07-20：用户报告旧工具过于复杂、难看且增加无效工作量，登记为 `open`；
  - 2026-07-20：单屏工具、后台 span 和单击完成路径实现并通过验证，改为 `resolved`。

### RWI-0012 — Windows 换行转换使 aggregate manifest 的 bundle hash 不等于落盘文件

- **首次发现**：2026-07-20
- **阶段/范围**：内置 Sol 150 条 aggregate 的 provenance manifest
- **观察事实**：合并器先对内存中的 LF JSON bytes 计算 SHA-256，再用
  `Path.write_text` 写文件。Windows 文本写入把换行落为 CRLF，导致 manifest 记录
  `3bc656...`，而实际 `ai_review_candidates.json` 为 `98fdda...`；150 条 schema、span
  和 membership 均已通过，错误只在产物身份记录。
- **影响**：后续 exact-hash gate 会把正确候选误报为被篡改，或者在未重新计算时错误
  绑定不存在的文件字节，破坏运行复现证据。
- **状态**：`resolved`
- **解决方法**：aggregate 写入后使用项目 `sha256_path` 对实际文件字节计算 hash，再
  写 manifest；保留构建阶段的内容验证，但不再把预写入的规范化内存 bytes 当作落盘
  身份。重复 `--write` 必须验证现有产物 byte/text 一致且不得覆盖漂移文件。
- **验证证据**：新增 full-bundle 回归同时检查 150 个唯一 sample_id 与 Layer E
  membership 同集、manifest 计数 150/150，并断言 manifest hash 等于实际文件
  SHA-256；修复后聚焦测试 7 passed。
- **对应事件**：Event 83。
- **状态历史**：
  - 2026-07-20：full-bundle 回归首次发现 hash 不等，登记为 `open`；
  - 2026-07-20：改为写后实际文件 hash 并通过回归，改为 `resolved`。
