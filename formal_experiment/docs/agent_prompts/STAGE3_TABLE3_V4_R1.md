# DeepSeek 修正执行 Prompt：S3-TABLE3-V4-R1

完整阅读本文，再执行。你负责机械实现、具名验证、已授权运行和数据交付；Codex
已作出下述方法判断。只做实验与数据，不写论文。工作区
`D:\Paper\experiment\LLM4BPC`，活动改动仅在 `formal_experiment/`。
本卡补充并优先于 `STAGE3_TABLE3_V4.md` 的冲突部分；原任务卡和历史授权保持原字节。
实时状态仍只在 PROJECT_AUDIT，路线在 MASTER_PIPELINE，不另造状态/交接页。

## 1. 审查结论与已确认的证据

审查对象：`2f9dd9f8002163ada2036bd0bb166e918035483e`。
该提交保存了真实本地诊断，但不能接受“没有机械错误、只差 key、A–E 均完成”。
以下行号指审查时版本，修正后以函数名定位；相对路径以 formal_experiment 为根。

| 问题 | 证据 | 本轮必须处理 |
|---|---|---|
| 请求预检与发送字节不一致 | `run_stage3_d1_v4.py` 的 verify_preflight_and_bodies 用 json.dumps 默认 ensure_ascii=True，FrozenBodyHttpTransport.send 第 250 行用 False。五条真实冻结 body 均不相等：预检长度 17625/17624/17460/17684/17559，发送端均少 18 bytes。 | key 存在仍会在发送前失败；统一使用预检原始字节，不能修改预检 SHA 来迁就错误编码。 |
| key 变量支持不全 | `_env_api_key` 只认两个 BPC 名称，不认 DEEPSEEK_API_KEY。Codex 审查进程中 DEEPSEEK_API_KEY 与 BPC_HYBRID_LLM_API_KEY 存在，只检查存在性，未输出值。 | 不将过去某执行进程缺变量当成整个项目无 key。加入规范变量并只检查执行进程；不让用户粘贴秘密。 |
| coverage 公式错误 | `evaluate_stage3_table3_v4.py:72` 将包含 unknown_positive 的 FN 计入 observable。 | Ours 全 unknown 却报 0.30；公式应为 (cells−unknown_positive−unknown_negative)/cells。 |
| Winter executor 接线错误 | `run_stage3_table3_v4.py:198` 把当前模型参与者当整个 resource_set。原 `../references/winter_2020_model_check/model_check/lib/main.py:92–135` 在所有模型上累积 resource_set，再传给 Pair。 | 当前单执行者模型中 a 与 model_resource 相同；Pair 同时要求前者在条文、后者不在条文，无法报错。不能称作已证明 Winter 的真实能力不足。 |
| 推理读取了参考文件字节 | load_inputs 遍历 config.hash_bindings；其中含 construction_reference，_sha_file 实际 read_bytes。 | 没有证据表明标签参与计算，但“从未读参考文件”和 false 声明不实；把参考完整性检查移出推理进程。 |
| evaluator 没有验证其声称的 manifest 链 | 只现算 predictions/signals SHA，没有与推理前已保存的输出 SHA 比较；run_manifest 根本无 outputs hashes。只信 count=900，重复键可被 dict 覆盖。 | 真正冻结输出、核对全部唯一键和状态一致性，拒绝篡改/重复/缺项，不能靠布尔声明证明隔离。 |
| nominal 投影违反原文边界 | temporal_projection_v1._nominal_endpoint 不接收所选 span 上界，且 value=' '.join(chunks) 丢掉 of，与记录的 source offsets 不一致。 | 第二端点必须位于预测 span 内且 text==source[start:end]；超界拒绝。 |
| before 补语覆盖不足 | article18p3 的 before.head=informed 在 marker 前；实际后半句有 lifted，旧算法只认 marker.head 因而拒绝。 | 这是 Codex 上版设计的句法覆盖缺口，本卡锁定第 3 节的限定改进，不能另行追分。 |

只用已有计数重算 coverage（不是重跑实验）：

| 方法 | Missing | Actor | Order | Overall |
|---|---:|---:|---:|---:|
| Sun | 1.0000 | 0.2000 | 0.0000 | 0.4600 |
| Ours（未运行） | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Winter | 1.0000 | 1.0000 | 0.0000 | 0.7000 |

旧计数导出的 Sun 0.3429 / Winter 0.2500 F1 不因 coverage 修正而自动变化；Winter
接线修正后才会有新的真实计数。Ours 未执行，主结果应为“未运行/null”，不是性能 0。
可以保留旧全 unknown 的诊断计数，但须与方法性能分开。
表一 3/5 span 字段胜、加 Modality 后 4/6 胜，确实符合“多数更高、少数更低”，
不能像上次交付第 4 节那样写“不符合多数更高”。表二仍不支持全部模块必要。

## 2. 不变边界与本轮版本

保留旧 v4 输入、20 BPMN、构造参考、B0、五条 D1 payload、prompt/model/registry、
SunScorer/旧 converter、WinterPair/native paragraph parser/词表及其阈值原字节。
禁止通过 --overwrite 覆盖旧 outputs/development/stage3_table3_v4 或旧报告；它们是
本轮纠错证据。禁止用 .gitattributes 改动或更换期望 SHA 掩盖输入漂移。

新配置：`configs/stage3_table3_v4_execution_r1.json`；新推理产物：
`outputs/development/stage3_table3_v4_r1/`；新报告：
`outputs/reports/stage3_table3_v4_r1.{json,md,manifest.json}`；新数据索引：
`outputs/reports/experiment_tables_delivery_v2.json`。
可以修正尚未真实调用的 run_stage3_d1_v4.py 与新 v4 runner/evaluator，必须记录代码
版本；不得改旧运行 manifest 的代码绑定。顺序改进用新模块 temporal_projection_v2.py，
保留 v1 供历史复现。测试跟随实际新模块/调用方，不跑全量。

原五次授权持续有效，总请求仍至多 5、0 重试、总输出 20,480、总预算 $8.02。
本卡不新增第六次，不重跑旧 74 条或表一/二；无 Rules+LLM/其他 API/全量测试许可。

## 3. Codex 已决定的方法修正，不再把选择交给用户

### 3.1 Winter 恢复原型的全局角色候选词表

新增独立只读准备步骤：只从 inference_view 列出的这 20 个模型读取 process.name，
输出去重、lower/strip 后的全局角色字符串集合及源模型 SHA。必须忽略参考、错误类型、
pair/control/family；artifact 中不要给 detector 任何角色→case/活动/参考对应关系。
这一批按现有文件应导出 controller/data subject，不能在程序里硬编码这两个答案。
流程内当前执行者仍来自当前模型。将全局集合传给 WinterPair，所有 case 使用同一份。

这是恢复原型“集合级候选角色”输入合同，修正旧 wrapper 的单模型局部集合错误；
相对于上版“所有输入仅当前 BPMN”，明确增加一个无标签、无顺序结构的全局词表。
当前 detector 仍不能打开其他模型、control 或参考；全局词表不指示哪种角色正确。
该词表可作为所有方法共享的公开输入，Sun/Ours 无需使用它，不改变其评分方法。
不更改 Pair 的 gamma/delta、资源条件或相似度来保证非零。
用手工合成 fixture 加确定性 fake sim 证明：正确角色通过、错误角色触发、低动作
匹配不强行触发；真实数据的结果由原 frozen backend 决定，不预设 actor F1。

### 3.2 共同 temporal_projection_v2 的限定规则

沿用旧卡全部输入隔离、modality、native 优先、预测 marker、排除/歧义/否定规则，
只作以下明确修改，Sun/Ours 用同一版本；不触碰 mandatory actions 或 matcher：

1. nominal 端点接收 selected_span，上下界同时约束 chunk 和 of-chain。任何所需
   chunk 越界都拒绝，不能截断半个词或去邻近原文捞额外事件。text 直接取
   source[start:end]，保留中间 of；每个输出端点测试该恒等式和 span containment。
2. before/after 的事件 head：先检查 marker 为 mark 且 head 是 marker 后 span 内
   的 VERB/AUX，使用它；否则若 marker 为 prep，检查其直接子节点 dep=pcomp、
   POS=VERB/AUX 且在 span 内，必须恰好一个才选作 head。不能选 marker 前的主动作。
   后续 verbal subtree 求交/去后继从句沿用旧卡，并要求 head 保留。没有这样的
   verbal complement 才尝试 bounded nominal 分支；多个补语直接拒绝。
3. prior to 沿用 bounded nominal 分支。所有 text 均为原文连续片段；不转述
   processing 为流程任务名，不扩 marker 词表，不按条文号特判。
4. 每条 derived edge 保存语法分支、head/marker/endpoint offsets、原始预测 span
   和拒绝原因。支持形态的通用合成 fixture 在第一次新评分前冻结，不用目标 F1 选规则。

article13/14 的 provide 被 B0 的 exception [80,177)/[80,176) 包住，属于真实上游
抽取错误；不要去掉 exception 排除规则救分。article35/36 名词事件与流程活动在
冻结 similarity 下低于 gamma 是另一问题；本卡不降低阈值或改成专门关键词匹配。

### 3.3 Winter 顺序缺失的判断与后续范围

原型 sequencemarkers 包含 after/then 等，却没有 before/prior to，且单 obligation
直接无 flow。本五条全部采用 before/prior to，因此“有法规顺序依据”并不意味着
Winter 能从这些原句抽出 flow。这个样本覆盖缺口由 Codex 的上轮设计承担，不能
把 actor 接线错误和 order 支持范围混为“算法都没问题”。
本轮不把 before 偷换成 after、不新增 Winter 算法，不为避免零而删 order 类。
完成修正后的真实诊断及五条 D1 后，如果仍不可观察就保持未验收。
作为下一步的机械准备，单独整理三个自然 after 来源候选：Article14(3)(a)、
Article33(2)、Article43(1) 首句。只提取原文定位/hash、义务/两个事件/执行者、
适用/例外/时限与现范围差异，标 candidate_not_benchmark，不抽取、不建新 BPMN、
不生成答案或性能，不调用 API。14 的时限、33 的无不当延误、43 的认证主体不得
被简单删除来伪造“只剩顺序”。候选语义由 Codex 审核，再定独立扩展协议与精确预算；
不要以实际 F1/是否能提高 Winter 得分筛选候选，也不要说已解决三类正式比较。

## 4. 执行任务与验收（按顺序；完成一项立即 checkpoint）

### R1-A：修正评价与证据链，零 API

- 开始按两级 AGENTS 和 AI_CHANGE_PROTOCOL 做 quick integrity，保护原 dirty。
- 先为现存 v4 诊断生成只读文件/hash inventory，锁住全部旧输出，不覆盖。
- coverage 改为 1−unknown_total/cells；相应 unknown_rate 与 coverage 和为 1。
  FN 仍包含 positive unknown，F1 主公式不变。未运行/blocked 方法的主 P/R/F1
  为 null、status=not_run；如果保留全 unknown 算术分数，放独立 diagnostic 字段。
- 独立 precheck 可读参考做 hash 核验，但 inference 进程及其 hash loop 不得打开
  参考。新增不含参考的 inference 文件白名单与 BPMN hash 表；不要把整个含有
  target/参考标签的构造 manifest 解析内容送入推理。一次预测只读当前模型和全局词表。
- 推理 manifest 写 predictions/signals/rule_records/角色词表 SHA、实际输入/模型文件/
  代码依赖 hash、包版本、命令和 git commit；实际保存输出后、打开 evaluator 前冻结。
  evaluator 将读取的输出与这些既有 SHA 对照，不能只是算一遍然后写入新报告。
- 硬验证 3×20×5×3 个唯一键与 60 个唯一 method/case、各字段/值/状态和 flattened
  signals 与 nested predictions 一致；杜绝重复覆盖、缺项默认 unknown、未知 status
  默默吞掉。与输入白名单和冻结 20 case/5 rule 对照，不只信文件自报 count。
- N/A 行仍保存实际预测与证据，主分母固定排除；不能把诊断字段全擦成 null。
- 定向测试应含全 unknown coverage=0、正例 unknown 不算可观察、未运行方法 null、
  tampered 文件拒绝、重复/缺单元/乱 status 拒绝、flattened/nested 不一致拒绝；
  用文件访问 spy/白名单验证推理不能读参考，不能只 assert 代码写死的 false。
- 记录验证并提交推送；旧事件若不准确，追加纠正说明，不重写历史事件。

### R1-B：角色集合与顺序投影修正，零 API

- 按第 3 节实现全局角色 artifact 与 v2 投影，source/model/threshold 不变。
- 用不含真实 benchmark 参考的合成 fixture 验证角色判定与 mark/prep-pcomp 分支、
  nominal bounds/of 连续性、native 优先和异常拒绝；共享函数的 Sun/Ours 同输入
  同输出。不可将既有缺陷 fixture 的“恒不报错”固化成期望行为。
- 冻结新执行配置与代码 SHA，记录本卡相对旧方法的限定差异，提交推送。

### R1-C：修复并执行原五次 D1，授权额度不增加

- 调整 key 选择为 DEEPSEEK_API_KEY 优先，兼容 BPC_HYBRID_DeepSeek_API_KEY、
  BPC_HYBRID_LLM_API_KEY。只从执行进程继承，日志只记变量名/存在性，绝不记值。
  不读 .env 或 OS 凭据库；当前确实均缺时才报告该进程配置 blocker。
- 所有实际 HTTP body 必须直接使用与 preflight 同序列化的 bytes；核对并保留
  既有五个 body SHA/bytes。测试拦截 urllib 请求，逐个核对真实五 payload 的
  request.data，必须包含非 ASCII 情形；只有 mock.send happy path 不足。
- 在创建任何 attempt 前完成全部五个 payload/身份/预算/hash 离线验证。把
  attempted（保守预发送预约）、http_dispatch、response_received、validated 的
  数量分开，不能把发送前 hash 拒绝或 budget 拒绝伪报成真实调用/付费。
  崩溃无法判断是否发出的预约不得重发；调用预算仍按最保守可能请求数保留。
- 真实调用的账本/锁按原 authorization_record_id 全局唯一，不受 --out-dir 变更
  重置。真实路径固定原 data/predictions/stage3_v4_d1_frozen_v1；测试 transport
  可用 temp，不能让另一路径绕过五次上限。明确处理尚未 attempted 的剩余样本，
  不重发已有请求；账本不可整体清空。若实际已耗额度，以现有账本为准。
- 官方身份与价格须有 dispatch 前实际证据，不能只复制 9 月 23 日快照。Codex
  于 2026-09-24 核对官方页仍为 deepseek-v4-pro / DeepSeek-V4-Pro-0813、1M context、
  高峰输入 cache miss $1.32/M、hit $0.044/M、输出 $3.96/M，预算未变：
  https://api-docs.deepseek.com/quick_start/pricing/ 。执行时保存核验时间/URL/值并
  校验尚适用；本次无须改模型或新增授权。不同版本/预算失效则停止相应真实调用。
- 防预算越界：预留下一次最坏输入/输出费用，五次累计输入不超过预检 5,000,000、
  输出不超过 20,480；同时受 5-call/$8.02 cap 限制。验证实际 usage 合法非负且
  不超过上下文/输出合同；模型响应身份漂移、usage/扣费未知就停止后续 dispatch。
- 原始响应 bytes 先落盘，再 decode/转换；HTTP 错误/解码失败也保留安全的响应
  状态与 raw SHA，未知费用写未知，不能因异常把已发生请求费用记 0。禁止重试。
  响应 model 必须验证，不能只在 manifest 写常量 RELEASE 宣称已验证。
- 授权 binding 需核对 preflight/task_card/prompt/registry 的实际 SHA，以及新增
  R1 方法记录，不改原授权与旧卡；新授权补充记录不能产生另一份五次额度。
- 具名离线检查全部通过后先 checkpoint，再执行剩余的已授权五条；保存原始响应、
  canonical/失败、逐请求 ledger、usage/费用、完整 manifest，然后单独 checkpoint。
  不因本构造 Winter order 仍未知取消已授权的真实 D1 数据收集，不把未运行当零分。

### R1-D：新矩阵、独立评分和交付

- 新 r1 目录运行 Sun/Ours/Winter 全矩阵，配置与代码先冻结。先持久化并核对全部
  输出 SHA、记录事件、checkpoint；再独立 evaluator 读参考并生成 r1 报告。
- 输出每方法三类和总体 P/R/F1、计数、unknown/coverage、逐项证据、实际运行状态。
  R1 与旧版比较分别说明 coverage 公式修复、Winter 输入修复、共同投影版本差异；
  不能将三种变化揉成“我们的模型提升”。表一/二只引用原结果。
- 旧极端结果和所有修正记录保留。若仍极端/不可观察，如实列明哪个通路、哪种原因，
  不能继续自动改算法/样本追分；三类比较仍未满足则 needs_method_review。
- 完成第 3.3 节的三个来源候选证据整理，保存在
  outputs/reports/stage3_temporal_scope_candidates_r1.{json,md}，不混入现有 50 单元。
- 更新唯一实时状态、主 Pipeline 的 R1 子任务、目录、数据索引和日志。交付真实
  指标/状态、调用账本、候选差异、各 checkpoint hash/push、具名测试与未跑全量。
  不把 audit_project 的通用 final_experiment_ready 当成本任务验收，也不把单个
  commit 描述为已经逐阶段冻结。本轮禁止将所有 R1-A…D 留到最后一次提交。

每个阶段完成按实际范围验证，不重复全套或已匹配的测试；默认相关检查 3 分钟内。
保护用户既有 dirty，不 blanket staging，不动旧 Gold/归档/人工决定，不强推。
门禁满足直接推进；真实外部 blocker 只阻塞依赖工作，其余先完成并保存。
