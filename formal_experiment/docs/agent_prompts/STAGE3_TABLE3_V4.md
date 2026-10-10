# DeepSeek 执行 Prompt：S3-TABLE3-V4

你是本项目的机械实施与实验执行 Agent。完整阅读本文件，再按 A→E 顺序实施。
本文是 AGENT_RUNBOOK 的静态任务卡，不是状态页。实时进度只更新 PROJECT_AUDIT，
任务完成条件归入 MASTER_PIPELINE；不要另写论文或交接总结。

## 1. 用户目标、角色和已经作出的决定

工作区：`D:\Paper\experiment\LLM4BPC`；活动改动限 `formal_experiment/`。
准备基线：`67ef832421dd0920fdc5f62f11cf615fca87893d`；分支 `paper-final-repair`，
上游 `origin/paper-final-repair`。使用包含本任务卡的最新提交，不得 reset 到历史基线。

用户只要求把实验和数据做出来，本轮不写论文、不改 PPT、不画图一/图二。
研究设计、比较口径和问题判断由 Codex 负责；你按合同写代码、测试、运行、记录、
提交和推送。不要把已决定的问题再次交给用户，也不要自行另选研究路线。
用户期望表一多数语义字段及总体优于 Sun，表二检查模块贡献，表三比较
Sun、Winter、Ours。这些是待检验的预期，不能成为修改数据或选择结果的标准。
实际不符合预期必须保留并说明。不能用占位 0/1、裁剪、删样本或伪造预测获得
“可接受”的 F1；真实极端分数须诊断，不能直接宣布表三验收成功。

用户本轮的“接受”已批准：

1. Sun/Ours 共用时间约束到顺序边的独立重建补充，具体算法锁定在第 4 节。
2. 对预检的五条新输入进行一次独立 LLM-SE 抽取：总请求上限 **5**，重试 **0**，
   总输出上限 **20,480 tokens**，保守总预算上限 **8.02 USD**。额度仅用于该抽取。
3. Codex 负责想法，DeepSeek 按严格 prompt 执行；用户手动转交本任务卡。

这不是新增消融、旧 74 句重跑、Rules+LLM Repair、其他模型或全量测试的授权。
原 `stage3_d1_preflight_v4.json` 的 authorized=false 和构造配置的 pending 字段是
授权前的历史快照，保持原字节；用新执行授权记录引用本轮决定，不篡改历史，
也不因旧快照再次询问这五次调用。真实身份/预算漂移时才停止相应调用。

## 2. 已有证据与不可混淆的结果

以下相对路径以 `formal_experiment/` 为根。

| 目标 | 权威已有证据 | 真实状态与处理 |
|---|---|---|
| 表一 | `outputs/reports/stage2_table1_paper_final_v1.{json,md}` | Ours 总体 0.8378，Sun 0.7631，+7.47 个百分点；计 Modality 后 4/6 字段更高，Actor/Exception 更低。复用，不重跑。 |
| 表二 | `outputs/reports/stage2_table2_prompt_ablation_paper_final_v2.{json,md}` | 八组已有结果，111=0.8224，100=0.8354；E/S 平均主效应为正，J 为负，不支持“所有模块都有必要”。复用，不扩调用。 |
| 表三 | `outputs/reports/stage3_reconstruction_v4_protocol.md`、`data/development/stage3_reconstruction_v4/` | 已有五条来源、20 BPMN、参考、冻结 B0 五条预测及 D1 预检；尚无 v4 三方法 checking 结果。按本任务补齐。 |

表一 Overall 只汇总五个 span 字段；Modality 是单独四分类 macro-F1，不能写成
六字段统一 micro-F1。表二 E/S/J 的 000…111 总体 F1 依次为
0.7380、0.7261、0.8107、0.8142、0.8354、0.8299、0.8268、0.8224。
四组历史同版本窗口结果加四组新调用，不是一次交错重复实验；不得把 100 换名为
完整方法。表一 Ours 和表二 111 是不同运行，不能为数字一致互换预测。
本地 dirty 的 `sep_c3_modular_ablation_v1.*` 不是上述表二的替代权威结果。

Sun 模仿依据是 §5.3.2 的补充基准流程、删除动作/改变执行者/交换顺序的构造。
来源审计见 `outputs/reports/sun_stage3_official_asset_audit_v1.{json,md}`；可读全文
`../references/papers/extracted/sun_2024_full_text.txt` 是作者稿。本地继承包没有
原论文补充的合规流程、单错误变体和完整答案；不能声称已恢复原实验数据或作者代码。
v1 使用 control/变异辅助；v2 将目标规则带入推理；v3 新加无依据的
matching_score>tau 外门槛。这些以及 no-gate 分数均保留历史诊断身份，不复活为表三。
旧参考/已完成审核不重开；92 个旧 clause 没有规则侧顺序边，不得补造 Gold。

## 3. 基准、输入隔离与冻结清单

范围固定为 GDPR 13(3)、14(4)、18(3)、35(1)首句、36(1)五项义务，每项 1 基准
加 3 个单错误变体，共 20 BPMN。这不是 20 个独立真实业务流程；13/14 高度相似。
本构造参与方法开发，不能称为完全未见的独立测试集。参考是有原文依据的 AI 构造，
is_gold=false、human_adjudicated=false 始终保留。本轮可产出该范围表三数据，
不自动满足完整 GDPR 端到端结论或正式发布门禁。

固定参考每方法 **50** 单元：missing_action 20、incorrect_actor 15、out_of_order 15；
每类正例 5，共 15；负例 35。缺动作变体的 actor/order 预定义为 not_applicable，
共 10 单元，不是预测后排除。不得增加、删除、重抽或改写样本。

推理只接收 opaque case_id、当前 bpmn_path、process_id、五条源输入、方法预测、
冻结方法配置。禁止读取 construction_reference、target rule/type/activity、变异/
配对/族信息或对应 control；不能与其他 BPMN diff。投影只读原文与该方法预测，
连当前 BPMN 也不得读。单独完整性检查可核对参考，但不得把它送入预测函数。

执行前逐项 SHA-256 核对；构造 manifest 中每个 BPMN 的 hash 也须全部一致：

| 文件 | SHA-256 |
|---|---|
| `data/development/stage3_reconstruction_v4/manifest.json` | `e49980ef7e4fcfdb39d770082706433cf22fe143cf97cf24f2c39e555013d501` |
| `data/development/stage3_reconstruction_v4/stage2_input.json` | `4c934712d4e85316167136a46861084165c75969c113eca7d995de5ddaabd1f2` |
| `data/development/stage3_reconstruction_v4/inference_view.json` | `6248e8396ad4d8d7077b6332f51b1aa2b5de7e97188e324cb49e00bda4c1eb33` |
| `data/development/stage3_reconstruction_v4/construction_reference.json` | `3c992f98e0f5109fd5d726a923f19d895c22962ee71a16130b692bfc0f125915` |
| `data/predictions/stage3_v4_b0_frozen_v1/predictions.json` | `eee1d6447bdab21d20704df64801e81aaa642e543a0bd706b0783882009c71fa` |
| `outputs/reports/stage3_d1_preflight_v4.json` | `b79cae69bd295d1be933eb4109a44c5a88ca8579ee646833d59dd5d0411020c5` |
| `scripts/prepare_stage3_execution_v4.py` | `bceec17c04980b97c4a40694e30f7bca98eacaca07c22edd142d910c02787298` |
| `src/bpc_hybrid/sun_stage3/sun_scorer.py` | `b05b5995a60a1fc748244b854e1649cdc90b075c0d5ea5223b2a3e0fff569b7b` |
| `src/bpc_hybrid/sun_stage3/gdpr_capsule_converter.py` | `e7110c2c1ecab56f6124d918b340639e7affd17b6f253f3c525780a4f3a96436` |
| `configs/sun_stage3_development_v1.json` | `3ef60d5bda1e5103486d5269cd3740330e911c1b912367d822c7dbab729714c4` |
| `configs/winter_stage3_development_v1.json` | `45635b7108410309356545ea79d498cfa0481ba516cc2676d6c08cecd30fdb12` |

此外记录实际依赖闭包的版本/hash（解析器、similarity、Winter clause/pair、normalizer、
语言模型包等），不能只锁上述文件却改其调用实现。BPMN 已修正为 default namespace，
同步 process.name/participant.name，两实际解析器均验证可见执行者；不得再用 builder
的 --write/--refresh-unscored-models 调整流程标签。B0 已有 5/5 真实预测，直接复用。

## 4. 共用时间投影算法（在看到 D1/表三成绩前实现并冻结）

新增纯函数模块 `src/bpc_hybrid/sun_stage3/temporal_projection_v1.py`，用 wrapper
调用旧 capsule converter，保持旧 converter、B0 和已有 capsule 原字节。
同一函数、配置、依赖版本用于 Sun/Ours，无 method-name 分支。

1. 输入为经 source identity/offset/schema 验证的 canonical record 及同一原文；
   只处理 obligation clause，不能把 permission/prohibition 改为 obligation。
2. clause 已有有效且端点可解析为本 clause 预测 action 的 native order_relations 时，
   保留这些边，不再补全该 clause；无有效 native 边才用下列 fallback。
   记录 native/derived/rejected 来源和原因，不静默修正无效边。
3. 只在本 clause **预测的 conditions/constraints span 内**找完整 before、after、
   prior to marker（忽略大小写、词边界）；原文其他位置有 marker 不触发。
   重叠 span 的同一 marker 只算一次，选包含它的最短 span，平局按 start/end 排序。
   否定 marker（紧邻 not/never，或依存 neg 修饰 marker 所在从句）、所选 span
   含多个 marker、marker 位于预测 exception 内均拒绝并留原因。
   不将 when/and/during/until 等扩展为顺序语义。
4. 主动作候选为本 clause 的 predicted actions；排除完全位于任一预测
   condition/constraint/exception 内者。按相同 offset 去重后必须恰有一个候选。
   多个或没有均记拒绝原因，禁止用 BPMN 相似度、参考任务名或手工条文表选择。
5. 主端点仅用于顺序匹配：若所选时间 span 与主动作 overlap，从主动作 interval
   减去该 span，去除两端空格/标点。剩余片段中必须恰有一个含 spaCy VERB/AUX 的
   连续片段，取该片段原文；没有或多个则拒绝。不做同义替换或主动/被动改写，
   不减其他 condition 来修好预测。原 actions/actors/actor_action_pairs 仍原样用于
   缺动作/执行者评分，不把这一步变成全局动作清洗。
6. 第二端点限所选预测 span 中 marker 后的原文，用现有离线 en_core_web_sm
   在完整原文上的依存分析，不下载新模型或调用 LLM：
   - verbal before/after 从句：marker 的依存 head 为 VERB/AUX 时，取该 head 的
     连续子树原文，与 marker 后 span 求交；在首个后续条件/关系从句的完整子树
     起点截断（dep 为 advcl/relcl/acl 且不含该 head），去除末尾标点。
     交集必须保留 head，否则拒绝。
   - nominal 事件：其他情况取紧接 marker 的第一个 noun chunk（只允许跨空格）；
     可含直接相接的 `of + noun chunk` 链，不含其他介词短语、关系/条件从句或
     标点后文字。不跳过中间词寻找更好名词。根词为 NUM、纯数字或根词实体为
     DATE/TIME/QUANTITY 的时长/日期端点拒绝。无 chunk 或不能连续截取则拒绝。
   - 所有端点均为连续 source substring，存字符 offset；无条文号白名单、参考
     task label、人工词典或针对某个预测结果追加的特判。
7. before/prior to：主端点→第二端点；after：第二端点→主端点。两端相同拒绝，
   按 clause/marker offset/两端 offset 去重。多个独立 marker 分别处理，保存
   成功边及拒绝原因。无边不能伪造 satisfied。
8. 派生顺序端点可以来自 constraint，**不自动加入强制动作集合 Ar**。这是独立
   重建补充，偏离 Sun Definition 3 的 Ur⊆Ar×Ar 严格定义；双方同用，只扩展
   顺序表示，Def.5–7 实际计算与阈值不变。必须披露该差异，不称为恢复了 Sun
   原生顺序抽取，也不将共同投影单独算成 Ours 的优势。

边界/解析错误可能使投影拒绝部分边，冻结 matcher 也可能无法匹配端点。这些是
待测现象，不能看到分数后改规则。本文无法唯一决定的语义分支，保存 span/解析证据
交 Codex 决策；你不能自行选择更高分解释。

## 5. 三方法 checking 与独立评价合同

Sun/Ours 用同一冻结 SunScorer，tau/gamma/theta=0.8，保留内部严格/非严格比较、
lemma/similarity、Def.6 existential/min、动作绑定业务对象和可达性实现。
禁止 min 改 max、删业务对象、降阈值或加 lexical/LLM fallback。
用同一 wrapper 检查全部五条规则；Def.4 排名只作诊断，**不得用 matching_score>tau
外门槛、Top1/TopK 或目标规则决定 Def.5–7 是否执行**。
旧 `stage3_sun_style_checker.SunStyleChecker.check` 含该外门槛，不直接复用；
其 `normalize_sun_signal` 和 `winter_signals` 可复用。

Winter 使用现有独立 native paragraph/model/pair 通路，gamma=0.4、delta=0.8、
现有 REACHABILITY_CORRECTED 配置，吃同样五条原文和当前 BPMN。不能用 Sun/Ours
记录冒充 Winter 抽取，不能恢复 archive 代码或新增 Winter 顺序算法。
native parser 无法规侧 flow 时保留 unknown 和原因。

每方法每 BPMN 输出全部五规则的三类信号，共 **20×5×3×3=900** 个信号。
固定 violated/satisfied/unknown 三态；失败 record/零分母为 unknown。原始证据、
分母、相似度、actor-action map、端点映射和可达性均落盘。raw_score=0 但分母=0
不得解释为合规。无法产生信号时保存失败条目，不删行；Stage2 失败的整条 rule
仍须出现在矩阵并标注失败。

先单独推理、保存预测/manifest、结束进程并 checkpoint，然后独立 evaluator
才读取 construction_reference。参考规则 ID 仅在此时选择评价范围。范围外报警
仍保存，但无参考不计 FP。因此只称**给定适用条文范围的 checking**，不称全规则
检索端到端 F1，不发布不完整 Gold 的 MAP。

必须评价每个 case 的所有预定义类型，不能只评价被变异的那一类：

| 参考 | 预测 | 计数 |
|---|---|---|
| violated | violated | TP |
| satisfied | violated | FP |
| violated | satisfied 或 unknown | FN；unknown_positive 另计为 FN 子集 |
| satisfied | satisfied | TN |
| satisfied | unknown | unknown_negative，不能称 TN 或合规判定 |
| not_applicable | 任意 | 固定排除于主分母，单列诊断，不随方法变化 |

每方法断言 TP+FN=15、FP+TN+unknown_negative=35、五项计数总和=50。
P=TP/(TP+FP)，R=TP/(TP+FN)，F1=2TP/(2TP+FP+FN)；无报警 P=null，有正例但
无 TP 时 R/F1 如实为 0。不加 epsilon，不把 null 写成 0，不平均三类 F1 代替
总体 micro-F1。各类分别报告计数、P/R/F1、unknown、observable coverage。

## 6. 执行阶段与具体验收

### A — 实现与离线验证，零真实 API

- 阅读两级 AGENTS.md 及实验必读文件；记录 git dirty，保护用户改动。
- 一次 quick integrity，核对第 3 节全部 hash；不因失败更新期望值。
- 新建 `configs/stage3_table3_v4_execution_v1.json`，机器化 scope、算法版本、
  三方法依赖/阈值、隔离、计数/unknown 策略、预算；不改旧构造配置。
- 实现投影、无外门槛 wrapper、独立 inference/evaluate CLI。先用合成 fixture
  验证行为；合成 fixture 指标不能当实际实验。
- 具名测试覆盖：Sun/Ours 相同输入投影一致；before/after 方向/native 优先；
  条件动作排除、否定/歧义拒绝、无预测 span 不造边；推理不能开参考/其他 control；
  matching_score 低仍检查；三态/固定分母/错类型 FP；矩阵完整。改变参考/目标
  标记不能改变预测，使用此类 metamorphic fixture，不写逐行镜像测试。
- 现有 `test_prepare_stage3_execution_v4.py`、`test_stage3_reconstruction_v4.py`
  可选实际相关节点复验输入/解析器；不自动跑全部 Stage3 历史测试。
- 按项目制度记录、checkpoint/push。投影与评价代码必须在第一次 D1 和首次真实
  表三成绩前冻结。机械代码缺陷修复另外版本留痕。

### B — 受控执行五次 LLM-SE，已授权

- 新 runner 建议 `scripts/run_stage3_d1_v4.py`，复用
  `prepare_stage3_execution_v4.request_bodies()` 的五个精确 payload，核对 preflight
  每条 body SHA/bytes/source SHA；不改 preparer 或实验 prompt。
- 模型 deepseek-v4-pro，记录发布版本 DeepSeek-V4-Pro-0813；temperature=0，
  top_p=1，每次 max_tokens=4096，thinking disabled，stream=false，response_format/
  seed 按预检省略。prompt SHA：
  `3aa64877cd4c4dae9f13cb40d102c3c9b04cc9bee5d478c34ad04621c0ede895`；registry SHA：
  `31f3358d089611b85a4a50d36444a4c59f6d965abbf0b8770aeb73db13642749`。
- 新建 `configs/authorization/stage3_d1_v4_user_authorization_v1.json`，引用本任务卡、
  用户“接受”、预检 SHA、五样本和严格预算；署名 AI 对真实授权的记录，不伪造
  签名或逐条人工裁决。若路径已有，验证并复用，不覆盖/重置额度。
- 调用前核对官方模型/价格 `https://api-docs.deepseek.com/quick_start/pricing/`，
  记录时间/来源、是否满足预检身份与预算。$0.113921 是代理估算，不是账单；
  $8.02 是总上限。身份/价格变化使合同失效或无法核实时停止真实调用并报告，
  不能换模型/代理服务、关 TLS 或扩预算。
- key 只从当前进程已有环境变量读取使用；不打印，不读 `formal_experiment/.env`，
  不泄露认证头。缺环境变量则报告配置 blocker，不搜索凭据。不得用 API 做
  coding/chat、模型探测、试提示或连通性测试。
- 五个指定 sample_id：gdpr_article13p3_s001、gdpr_article14p4_s001、
  gdpr_article18p3_s001、gdpr_article35p1_s001、gdpr_article36p1_s001，各至多一次。
  禁止 SDK/HTTP 自动重试、JSON 修复调用、额外确认请求。串行；发 HTTP 前持久化
  attempt，跨进程锁及跨重启账本防重复。超时/失败也消耗额度；未知扣费、预算/
  身份漂移时保留状态并停止；重启不能重发 attempted 样本。
- 先用离线 mock transport 测试 5-call cap、重启/失败不重试、超预算不 dispatch、
  body/source hash 拦截和响应绑定失败。测试不访问真实网络。
- 新输出 `data/predictions/stage3_v4_d1_frozen_v1/`：每条原始响应先安全落盘后解析。
  存 provider request/model/usage、HTTP 结果、耗时、ledger、费用口径、raw SHA、
  canonical predictions、失败/转换明细、manifest。不覆盖已有预测。
  响应 sample_id/source_id/source_text 先绑定，再用现有 d1_schema_adapter +
  d1_span_canonicalizer + stage2_canonical 验证，不能手改抽取内容。
  可参考 `run_sep_c3_targeted_refinement_v1.py` 的纯转换函数，但不执行其旧批量入口；
  若复用 Sun sanitize，不得把 D1 method 错标成 Sun。
- runner/授权记录先通过相关检查、记录并 checkpoint；再执行已授权五次。
  真实运行结束另记 experiment_run/manifest 并 checkpoint/push。未全成功可继续
  离线生成显式失败的诊断矩阵，但不能宣布完整抽取验收成功。

### C — 三方法完整矩阵，只跑本地 Stage 3

- Sun 用已有 B0 五条真实预测，Ours 用 B 的真实 D1，Winter 用原文。不重跑 B0，
  不用人工参考替换预测，不从表一/二挑更高分 arm。
- 新目录 `outputs/development/stage3_table3_v4/` 存三方法投影/表示/推理输出，
  manifest 绑定代码提交、dirty paths、依赖/模型/input/config SHA、计时和命令。
- 先确认实际解析流程非空、执行者可见、推理无标签访问，再推理 900 个信号及失败
  原因。预计本地运行明显超过短检查时，先说明时长。保存矩阵/manifest，关闭推理
  进程，记录事件、checkpoint/push，然后进入 D。

### D — 表三与失败定位，零真实 API

- 独立 evaluator 先核验预测 manifest/hash，再读参考，按固定 50 单元计算结果；
  产出 `outputs/reports/stage3_table3_v4.{json,md}` 及 manifest。
- 表格至少含 Method、Missing/Actor/Order F1、Overall P/R/F1、TP/FP/FN/TN/
  Unknown-negative、各类 unknown/coverage；JSON 保留未舍入值，Markdown 至少四位
  小数。逐项记录 case/rule/type、参考、预测、计数归属及证据。
- 检查整类恒定预测、任一方法任一类别/总体 F1=0/1、分母=0、端点映射同一活动、
  空流程、不可见执行者、参考泄漏、错误分母。保留真实极端数，但验收设为
  needs_method_review，区分机械错误、真实能力缺口、样本过小/过易、参考错误的
  证据，不能直接发布“可靠表三已完成”。
- 可由协议/接口证明的漏传字段、错路径/解析/计数等机械错误可在冻结数据上修复，
  定向复验、另版本保存每轮结果；不能改算法/阈值/流程/参考追分。需新研究设计时
  给 Codex 最小证据和影响范围，不让用户代做技术判断。
- 即使都在 (0,1) 也不自动通过：须三方法独立、Sun/Ours 共用 backend、三类能力
  有实际可观察证据、无泄漏、计数正确；整类没有法规顺序或有效映射仍属未补齐。
  Ours 非最好、表二模块无增益须如实报告，不能隐藏或找 best seed。
- 明确第 2–5 节的差异，不宣称完整复现原始运行、正式人工 Gold、20 个独立真实
  流程、完整自动端到端或普遍优于前人。

### E — 数据交付与验收回报

- 复用权威表一/二，连同表三建立 `outputs/reports/experiment_tables_delivery_v1.json`
  数据索引：源 manifest/hash、指标名称、样本/分母、运行身份、完成项和不支持的
  预期。不是新实时状态页，不重跑旧实验、不写论文、不填拟议结果。
- 更新 MASTER_PIPELINE 的 S3-TABLE3-V4 子任务和 PROJECT_AUDIT 的真实状态；
  只做出诊断就写“诊断完成、表三未验收”。本任务允许机械更新限定 S3 事实、目录
  和日志，作为 AGENT_RUNBOOK 协调者规则的窄例外；不改变路线/其他任务/发布门禁。
- 最终回复包含：三表结果/来源；表三逐类及总体计数/指标/unknown；与用户预想
  不一致处；实际 attempts/success/fail/retry/usage/费用（未知写未知）；输出/
  manifest 路径；具名检查及未跑全量；各 checkpoint 提交/分支/push；本构造范围
  是否验收、仍缺什么。不能只回“脚本写好了”。

## 7. 写入范围、测试成本与 Git

新实现/runner/evaluator/tests/config/授权/预测/输出只在上述 v4 专用路径，辅助文件
可按同一前缀建立；不改冻结 extractor/scorer/converter、模型 prompt/registry、
旧样本/Gold/人工决定/manifest/历史结果。依赖复用已安装版本。超出第 4/5 节的
算法改动先交 Codex 判断，不恢复 references/archive/_retired 代码。

准备时已存在的用户 dirty 文件须保护、不暂存：
`data/development/human_review/stage1_gdpr7_human_correction_v1.json`、
`outputs/reports/sep_c3_modular_ablation_v1.json` 及同名 .md；另有根临时脚本/工作树/
PPT、formal 的 .bak/PPT 和 `scripts/build_v6_factorial_arms_v1.py`、v2.py。
以执行时 git status 实际清单为准，不清理/回滚/覆盖这些资产。

每个连贯子任务/真实运行结束按根 AGENTS：检查 diff→范围验证→显式路径 git add→
cached diff→commit→非 force push→核对远端。不攒到最后一次，不 blanket stage。
未完成的安全 checkpoint 标明 WIP；push 阻塞保留提交并报告 hash/原因，不称已备份。

实验改动按 AI_CHANGE_PROTOCOL 在边界做 quick integrity；用
`record_change.py --test-target <具名文件或节点>` 合并相关检查与日志，不为日志重复
同组测试，不伪造/改绑 receipt。新文件维护 FILE_CATALOG。
**无全量测试授权**：禁止 pytest tests、audit_project.py --with-tests 或等价全套。
相关检查通常 3 分钟内；已知更长先说明，超时/无关失败不扩全量。

门禁满足直接推进下一阶段，不反复问“是否继续”。真正卡住先完成不受影响工作、
保存并提交可复现结果，再把具体方法问题/外部 blocker 交回 Codex。
