# LLM4BPC 完整实验主 Pipeline

**文档版本**：3.7.45
**状态**：ACTIVE — 全项目研究与任务分解的唯一主线
**最后更新**：2026-10-07
**方法学主干**：Sun et al. (2024)（三阶段方法主干）；Barrientos et al. (2026)（直接借鉴来源：LLM 结构化输出、验证、受控词汇、归一化与评估纪律）
**当前实施优先级**：2026-09-25 的 S3-TABLE3-V4-R2 已完成 R1 协议偏差的机械纠正与原因定位：strict 顺序投影、失败原因分类、精确 ID/输出绑定检查、零新增 API。但表三仍未验收，因为 Sun/Ours/Winter 的 order 分母仍全为 0；下一步须由 Codex 决定是否以明确的 after/temporal 扩展协议解决映射与原生覆盖问题，不得自行改算法、改样本或追分。下方历史安排不构成扩大实验、写论文或新增 API 的指令。

> 所有 Agent 在修改实验代码、配置、数据协议或研究设计前必须完整阅读本文。
> 本文定义“要完成什么、先后依赖是什么、每一步怎样算完成”。
> `docs/PROJECT_AUDIT.md` 只记录实时进度；不要再创建新的日期版
> `STATUS_*`、`HANDOFF_*` 或平行路线文档。

## 2026-10-07 修订 3.7.45：具体外发许可后原命令放行，默认150条执行中

- 明确外发许可checkpoint `4adc622` 已普通push并核验远端。自动审批接受该许可，
  同一原执行命令已创建进程，首次只读账本确认12条started；不是另换命令绕过。
- 当前run `thinking_default_20261007_v2` 执行中：150条/high/省略max_tokens，
  0重试、关闭/Sun零新增调用。实际进度以其持久账本和execution_summary为准。
  全部响应保存后才离线评价；DoD及主指标仍待完整结果与具名产物验证。
- 解除证据追加在既有approval_review，前两次拒绝保留为历史，不再是当前blocker。

## 历史修订 3.7.44：用户明确批准完整数据及提示词向DeepSeek外发

- 用户明确回复“授权将这150条法规文本及现有抽取提示词发送至 DeepSeek 官方 API 并运行”。
  具体许可已追加到既有approval_review证据；此前两次拦截原样保留。
- 继续同一冻结 `thinking_default_20261007_v2` plan与原命令：high、默认max_tokens、
  150次、0重试，无新关闭组/Sun，不改请求字节或扩大调用额度。该许可解除此前缺少
  具体外发授权的事实条件，提交原命令审批并执行；本记录时调用0，未冒称已完成。

## 历史修订 3.7.43：默认上限150条准备完成，具体外发审批仍拦截

- 准备checkpoint `c27f9e0` 已普通push并核验远端；7项具名离线检查和快速完整性
  是当前准备状态证据，不因记录拦截重复测试或扩大到全量。
- 原执行命令在创建进程前被自动审批拒绝；随后只读逐条完整核查150条实际文本、
  共用提示词和六个合成示例，验证全部请求与冻结plan一致。文本均为一般法规规范，
  不含具体个人申报记录、税号、账户或实际收入历史；000092/000119只提及供应商
  姓名/地址作为法定登记字段，无具体姓名/地址值。核查证据checkpoint `187728b`
  已普通push并核验远端。
- 以新增完整核查证据复核同一原命令，自动审批仍在创建进程前拒绝：认为用户虽
  授权实验，仍须明确授权完整数据集及现有抽取提示词向DeepSeek官方目的地外发。
  未换命令、未间接执行、未绕过；新API调用0，账本/原始响应尚不存在，指标null。
- 两次拦截及逐条SHA证据保留在
  `outputs/reports/s2_thinking_thinking_default_20261007_v2_approval_review.json`。
  已向用户询问这项具体外发许可，待回复；150条实验DoD未完成，不能称批次已运行。
  此确认来自自动审批，并非新增技能或项目全量测试门禁；冻结授权/请求plan不重写。

## 历史修订 3.7.42：S2-THINKING-SENSITIVITY-V1 默认生成上限完整150条

- 用户最新明确要求“思考模式跑150条试一下，默认maxtoken即可”。新独立授权
  `configs/authorization/s2_thinking_default_20261007_v2.json`；run ID
  `thinking_default_20261007_v2`，入口 `scripts/run_s2_thinking_default_v2.py`。
- 同一冻结EStG-150、原v6提示词，thinking enabled/high保持；实际请求完全不传
  max_tokens，不传None或显式65536。当前官方默认65536生成token（思考+最终答案），
  12并发动态补位、最多150次、0重试；此前两次单条诊断独立保留，不混入新150条。
- HTTP200下length/空最终答案/解析失败保留在150分母，不因单条截断停止整批。
  身份、用量、429或预算异常则停止新发送，保留并等待已发出的请求，不自动重发。
  只用既有进程密钥，不读.env，不发Gold或审核决定；预测全保存后才进行离线Gold评价。
- 零API预检绑定150条请求、全部来源与共享后处理/评价器；高峰无缓存最大token
  估算USD40.67371704，执行者保护上限USD50，已运行前说明，不伪称用户另定美元预算。
  复用原关闭R3/Sun及已有0813关闭参照，新关闭/Sun调用0；固定表一/表二不变。
- 比较边界：一次完整新批次与历史关闭结果；R3早于0813，生成额度不同，thinking的
  temperature不生效。完整150条不等于稳定性、多重复或独立未见测试，不作纯模式因果结论。
- DoD：150个唯一调用完成、完整账本/响应/usage/失败分母，推理与答案分列；同一
  legacy后处理及五字段coarse pooled micro-F1、modality独立，费用与token分布；结果/
  manifest/实验事件/具名产物检查及普通Git checkpoint。零API预检及7项具名离线检查
  已通过（6.90秒），快速完整性通过，150请求均确认省略max_tokens；准备checkpoint后
  执行。本任务不运行全量测试、不推进Stage3或正式发布。

## 历史修订 3.7.41：S2-THINKING-SENSITIVITY-V1 同一失败样本 high 最大服务额度诊断

- 用户追加指令：“给定一条数据特例，不设限制，看需要多少token”。独立授权
  `configs/authorization/s2_thinking_single_high_provider_max_20261006_v1.json`，恰1个新调用、
  0重试；仅estg_000002，原v6/high和其他参数不变，max_tokens从16384提升到服务允许的
  最大393216。省略参数仍有64Ki默认上限，不能声称真正无限。未设置额外美元停止条件，
  按服务最大生成额度高峰估算约USD1.57，已运行前说明。
- run ID `high_provider_max_estg000002_20261006_v1`，入口
  `scripts/run_s2_thinking_single_high_v1.py`。原high/16K截断证据独立保留；原150条仍停批，
  low完整150方案仍未授权。本单例不重跑关闭组/Sun、不读.env、不发Gold、不改固定主表。
- DoD：确认请求只改max_tokens；恰一次开始/完成账本；保存响应和完整usage，区分思考/
  最终答案/含输入总量、结束原因与耗时；自然stop后才报告本次实际完成用量，如仍截断
  只报告下界，不能推断最小所需预算或150条token分布。报告、manifest、实验事件与
  checkpoint完整。准备核对已通过4项具名离线检查（0.42秒）、快速完整性通过；
  准备checkpoint `9ddabd1` 已普通push且核验远端一致，不跑全量测试。
- 实际恰1次、0重试，HTTP200，high自然stop，最终JSON通过共享canonical校验；
  输入4446、思考13582、最终答案984、生成合计14566、含输入19012 tokens，159.29秒。
  峰价无缓存估算USD0.06355008；纳入返回缓存峰价USD0.057996928，闲时USD0.028998464，
  未查实扣。报告 `outputs/reports/s2_thinking_single_high_provider_max_20261006_v1.{json,md}`，
  manifest/原始响应/预测/账本为该run ID evidence目录。产物4项具名离线检查通过
  （1.72秒），涵盖完整用量、原始响应/manifest、最终JSON重算与Git检出字节；快速完整性
  通过，非全量。单例已自然完成并通过验收，结果checkpoint按根AGENTS.md要求普通
  推送；最终交付报告附远端核验哈希。原150条批次DoD仍未完成。
- 本次自然完成的生成量14566反而小于原16384上限：不能把旧截断解释成该样本固定
  需要>16K，也不能证明low必要。思考temperature不生效，两次生成并非相同轨迹；
  生成上限改变也可能影响生成行为，不能单独归因随机性。只报告本次观测，不推断最小
  预算、稳定成功率或150条分布；原150条仍未恢复，low仍未测试。
- 第一次自动审批以“敏感税务文本/具体第三方目的地许可不足”拒绝创建运行进程，
  无新增调用；只读确认该272字符是一般规范且无具体纳税人/账户/申报信息，保存
  `outputs/reports/s2_thinking_single_high_provider_max_20261006_v1_approval_review.json`。
  基于新增低风险事实对同一原命令复核后放行；没有换命令或间接执行绕过拦截。

## 历史修订 3.7.40：S2-THINKING-SENSITIVITY-V1 开启思考150条，关闭条件复用

- 用户在确认“只新增开启思考150条，关闭与Sun复用已有冻结结果”后明确回复“授权运行”。
  本批独立授权 `configs/authorization/s2_thinking_20261006_v1.json`；不借用其他批次额度。
- 唯一 run ID `thinking_on_20261006_v1`，原版 v6 prompt/六个示例和同一 EStG-150 输入；
  官方 `deepseek-v4-pro`，thinking=enabled、reasoning_effort=high、top_p=1、stream=false，
  生成总上限16384/条（推理+答案），最多150次、0重试、并发最多6。首条属于150分母，
  确认推理字段及完整最终答案后继续；失败或in-doubt不自动重发，不读取.env。
- 预检绑定全部请求字节、输入/prompt/Gold/schema/后处理/评价器与历史预测哈希。
  高峰无缓存最大token费用约USD11.4795；执行者设置并提前说明USD15保护上限，
  这不是预计实扣，也不伪称用户单独指定了美元预算。
- 主表关闭组复用 R3 正式臂（F1=0.8378），Sun复用0.7631；额外复用已有
  D-full-0813关闭组（F1=0.8224493117）作版本参照，所有关闭组新调用0。
  R3早于0813发布，不能保证与当前同名API版本一致；0813参照仍是历史跨批。
  该参照estg_000092保留一条模型输出source_text差异，150条实际发送指纹核对一致，
  不静默修正旧预测。不同生成上限、temperature在思考模式不生效均作为比较边界。
- 准备已验证并远端备份：9 passed/10.10秒、快速完整性通过（非全量），
  checkpoint `3964c6c`，分支 `codex/s2-prompt-simplification-v1`，普通push成功且远端HEAD一致。
- 实际执行在首条停止：1/150调用、0重试，HTTP200/model正确，但finish_reason=length；
  16384生成token全部为reasoning_tokens，最终content为空，耗时182.661秒。
  剩余149条未发送，主指标null，不把接口截断写成方法F1=0或完整实验完成。
  首条输入4446/输出16384，峰价无缓存估算USD0.07074936，闲时USD0.03537468，未查实扣。
- 原始响应/推理、账本、用量、失败诊断与partial manifest已保存；下一候选恢复方案
  `outputs/reports/s2_thinking_recovery_preflight_v2.json`（authorized=false）：统一low、
  同一150条、16384生成上限、0重试，旧high失败条独立保留，不混入low组。
  新调用150、累计151，因此需用户追加批准失败条的一次新调用和推理设置改变。
  新最大token费用USD11.4794，含已调用条约USD11.5502，建议累计保护上限仍USD15。
  本轮不自动执行恢复方案；原150高强度批次DoD未完成，等待具体恢复决定。
- 停批证据验证：3项离线检查通过（0.42秒）；另1项Git检出字节检查通过（2.19秒），
  快速完整性通过，非全量。新增精确行尾规则保留已记录SHA；首次暂存缓存不一致的
  失败记录保留，修正仅重暂存本次新增的两份jsonl，不改原始响应或重新绑定manifest。
  DoD：150条唯一调用完成，保留失败/截断与完整分母；推理和最终答案分列保存，仅最终
  JSON进入同一legacy后处理与五字段pooled评价；结果、费用估算、manifest、experiment_run
  和Git checkpoint完整。不替换固定表一/表二，不推进Stage3或正式发布，不运行全量测试。

## 2026-10-06 修订 3.7.39：用户批准原始数据GitHub备份，A/B对照完整交付

- 用户在具体300条响应/账本/派生证据、150条历史基线副本及GitHub目的地询问后
  明确回复“备份”。自动审批接受该授权，普通非强制push已成功；远端HEAD核对为
  `11ba35b39b323c9b84dad602cbd8a9f697df62aa`，包含结果commit `36422f6`。
- 原始响应、预测、评价、逐条变化、manifest、授权、账本、日志和验证均已远端保留。
  本受控开发对照的数据、验收、运行日志及Git备份DoD完成；不扩展到整个SEP-C3、
  Stage3或正式发布。原固定表一/表二、Gold、prompt、数值和已有用户修改未变。
- 原两次push拦截记录原样保留；当前blocker已解除，核验与授权证据见
  `outputs/reports/s2_prompt_simplification_comparison_20261006_v2_git_backup_resolution.json`。
  本次仅备份与说明更新，无新增API或实验重跑，不因此重新执行代码测试。

## 历史修订 3.7.38：A/B真实对照完成，保存近零主指标变化与格式负结果

- 用户最新授权下，`comparison_20261006_v2` 恰300次新调用完成（A/B各150），原版
  复用历史D-full-0813/repeat-01，新调用0；0重试，300条均stop，用量完整，评价失败0。
  API执行361.125秒。既有prompt、冻结Gold、评价器、旧结果与用户修改哈希均未变。
- 五字段coarse pooled主F1：原版0.8224493117、A 0.8218192829、B 0.8210327164；
  相对原版分别-0.06/-0.14个百分点，没有总体收益，不声明显著性或稳定性下降。
  A的actor误抽增加；B的actor/action提高与constraint/exception下降同时存在。
  保留真实结果，字段均值不能替换预定pooled指标；B联合变更不提供单句因果证据。
- 原始JSON对象107/150→A 7/150、B 6/150；多数新响应带围栏，共享后处理能解析，
  评价失败0。格式遵循负结果与后处理语义分数分开记录，不能因可修复而隐去。
- 实际新用量输入1,222,988/输出239,396；按高峰无缓存价估算USD2.56235232，
  纳入缓存用量高峰USD2.186044608/非高峰USD1.093022304；未查询账户实扣。
  USD9.76是硬上限。原始响应/账本/预测/评价/逐样本变化/历史原版副本和manifest
  保存于 `outputs/evidence/s2_prompt_simplification_v1/comparison_20261006_v2/`。
- 实测数据、指标、完整证据、具名产物复核与experiment_run事件均完成：4项产物
  检查passed/0.24秒，快速完整性通过，非全量；三臂评价可从保存预测重算一致。
  首次核验的tuple/list比较误报已修正并保留失败事件，无结果或调用变化。
  此受控开发对照数据/离线验收完成，本地scoped commit `36422f6`；完整GitHub交付
  尚被自动审批拦截（要求另行批准300条原始响应/账本/派生证据的具体外发），
  不把本地commit冒称远端备份，不绕过。拦截记录为
  `outputs/reports/s2_prompt_simplification_comparison_20261006_v2_git_push_blocker.json`，报告为
  `outputs/reports/s2_prompt_simplification_comparison_20261006_v2.{json,md}`。
  不替换默认prompt、固定表一/表二，不标整个SEP-C3、Stage3或正式发布已完成。

## 历史修订 3.7.37：用户批准 A/B 300 次真实运行及官方 API 外发

- 用户在明确的 300 次/原版复用/官方 DeepSeek 外发/USD9.76 上限说明后回复
  “授权，进行数据运行，快点”。授权独立保存于
  `configs/authorization/s2_prompt_simplification_20261006_v2.json`，不改旧拦截记录。
- 新入口 `scripts/run_s2_prompt_simplification_v2.py`、批次 `comparison_20261006_v2`：
  只发送 A/B 各 150 条，0 重试；原版复用历史 150 条，新调用 0。新预检绑定请求
  字节、授权、prompt、原版响应/预测/manifest、原文/Gold、后处理及评价器哈希。
- 为按用户要求加快，同批最多并发 6 次，A/B 按样本轮换提交，按 6 条一批预留
  预算。固定 model/采样/thinking/输出配置不变，只用已有进程密钥、不读取 .env。
- 上限 300 次、input 2,469,549、output 1,228,800、USD9.76；每次 4096 输出。
  in-doubt、已完成或中止批次不自动重发。候选效果须待真实响应与共享评价完成，
  每臂失败及完整 150 分母保留；旧原版、固定表一/表二及已有用户修改保持。
- 准备验证只运行 `tests/test_s2_prompt_simplification_run_v2.py` 的具名离线检查，
  不跑全量。完成准备后 scoped checkpoint 再执行；运行完成后另记 experiment_run、
  保存原始响应、账本、预测、评价、逐样本变化与历史基线副本，并再次 Git 备份。
- 准备门禁已通过：9 passed/8.15秒，快速完整性通过，commit `b8c2774` 已在远端。
  用户外发授权已获自动审批接受，真实执行现已启动；中途检查点84/300响应完成、
  无中止，尚无完整性能指标。此状态不等于实测 DoD 完成，不新增调用或重试。

## 历史修订 3.7.36：只新跑修改版，复用历史原版并区分费用参考/上限

- 用户明确纠正原版已完成，无需本轮重跑。修订范围为 A/B 各 150 次、共 300 次、
  0 重试；原版新调用 0。旧 450 次预检与拦截记录保留为历史，不作为新执行许可。
- 原版复用 `D-full-0813/repeat-01`；prompt 哈希与输入 ID 相同，150/150 完整
  请求配方指纹和响应指纹核对通过。比较披露历史跨批，不声称本轮同期三臂或
  保证服务端版本未变。共享后处理/评价器和完整 150 分母的要求继续保留。
- 历史 150 次记录估算 USD1.35147804；300 次历史量级参考约 USD2.70。
  原保守公式重算最大 token 预算上限 USD9.76，和旧 USD14.77 均不是预计实扣。
- 原版/A/B 通俗逐项差异与信息损失风险保存至
  `prompts/sun_compat/simplification_v1/COMPARISON_EXPLAINED_ZH.md`。
  A 压缩 JSON 指令，B 另含语义规则变化；不能把 B 效果全归因于 prompt 长度。
- 此检查点只作说明、来源/哈希和费用算术核对，不改候选或执行器、不跑 API 或
  代码测试。新预检/执行器尚待按 300 次与历史基线重新绑定，外发确认仍未收到。
  修订实测 DoD：仅 A/B 的 300 次完成、每臂 150 分母和失败保留、原版复用来源
  可追溯、指标/用量/逐样本变化与 experiment_run/Git checkpoint 完整。
  当前候选新指标 null，实测 DoD 未完成；固定表一/表二和其他任务状态不变。

## 历史修订 3.7.35：旧三臂 450 次执行准备（已由 3.7.36 范围纠正取代）

- 用户明确要求“对改动后的prompt进行实验对照”，本次具体化为同一 EStG-150 上
  v6/A/B 各一次；最多 450 次，0 重试，4096 输出上限。沿用 DeepSeek-V4-Pro-0813
  的 `deepseek-v4-pro`、temperature=0/top_p=1、关闭 thinking、无 json_object/seed。
- 预检 `outputs/reports/s2_prompt_simplification_comparison_20261006_v1_preflight.json`
  绑定全部 450 个请求、原文/Gold/后处理/评价器/代码哈希；费用按 2026-10-06 核对
  的官方高峰价及输入全未命中缓存计算，硬上限 USD 14.77、input cap 3,791,252、
  output cap 1,843,200 tokens。仅此唯一 run ID，不借用其他任务或旧额度。
- 入口 `scripts/run_s2_prompt_simplification_v1.py`：默认零调用；真实执行要求已保存
  本轮授权、源文件未变及 `--execute --allow-llm`。只私有使用进程中的 DeepSeek key，
  不读取 `.env`。每条先记录 started；in-doubt/已完成/中止批次不自动重发；失败保留。
- 主指标五字段 pooled micro-F1，modality 单列；共享历史 adapter 与显式 legacy 坐标
  后处理。同一输入三臂最多并发 3 条、提交顺序轮换；另记原始 JSON、token 用量与
  逐样本字段差异，不改原 prompt/Gold/评价器或固定表一/表二。
- 实测 DoD：450 次完成、150/150 分母每臂保留、指标/失败/用量/差异与原始响应可
  追溯，具名验证、experiment_run、Git checkpoint 均完成。执行准备的 7 项具名
  检查已通过并推送（26d33f4）；真实启动被自动审批拒绝，程序未启动、API=0。
  原因是具体文本/prompt 向 DeepSeek 的外发待用户明确确认；证据见
  `outputs/reports/s2_prompt_simplification_comparison_20261006_v1_execution_blocker.json`。
  当前尚无新性能结果；每臂一次的开发性回顾实验不提供稳定性或独立泛化结论。

## 2026-10-05 修订 3.7.34：S2-MODEL-API-SETUP 用户指定型号与限目的密钥状态检查

- 用户指定 Grok 4.7、MiniMax M3、Kimi 2.7、Qwen 3.8、GLM 5.3 Flash、MiMo v2.6 Pro。
  已登记 `grok-4.7`、`MiniMax-M3`、`kimi-k2.7-code`、Qwen Max 0902 固定快照、
  `glm-5.3-flash`、`mimo-v2.6-pro`；不新增模型家族或改变原正式臂。
- 按官方合同更新 Kimi（强制 thinking，temperature=1/top_p=0.95）、GLM（强制
  thinking，reasoning_effort=low，temperature=1/top_p=0.95）、MiniMax M3（关闭
  thinking，top_p=0.95）。保持 4096 输出上限、180 秒、0 重试及全部授权门禁。
  具名离线 provider 请求测试同步，不把配置正确称作账户/API 实测成功。
- 自动审批曾因旧 `.env` 禁读规则拒绝状态检查；用户单独明确选择“允许本次限定
  检查并覆盖旧禁读规则”后，私有本地检查返回六家均已填写、无占位符/重复冲突，
  不显示值、不修改文件、不联网、不调用模型。只保存状态结论，不保存密钥元数据。
- 后续六家新配置的独立预检仍须 authorized=false、metrics=null；此前 v1 预检保留，
  因型号/参数绑定变化不能复用。真实 key 有效性、余额、API 连通性和模型敏感性
  实验仍待用户明确授权，不把本次限目的检查解释成真实 API 许可。
- 本次型号更新验证完成：批次前后快速完整性检查通过，具名模拟测试 **33 passed**
  （非全量），当前离线 list 的六个 ID 已核对。真实 API=0；仅提交本批配置、
  测试及说明/主线/事件，不纳入已有人工数据或 modular 报告的用户修改。

## 2026-10-05 修订 3.7.33：S2-MODEL-API-SETUP 六家离线配置与逐批授权入口

- 用户要求分别填写千问、MiMo、Kimi、Grok、GLM、MiniMax 的 API key，到时候按
  新的明确授权再调用。此子任务只完成接入准备；真实调用、性能比较和正式评价
  均未授权、未运行，不复用以前额度，不改变固定表一/表二或原 DeepSeek 臂。
- 实现入口 `scripts/stage2_multi_model.py` 与 `src/bpc_hybrid/multi_model_stage2.py`；
  默认 list/plan 离线，init-env 仅追加六个空白项，不读取现有 `.env`。密钥私有加载
  只在本批计划、授权原文、双显式开关、模型/调用/token/核实单价/费用门禁后发生。
- 模型配置 `configs/models/stage2_multi_model_v1.json`；固定 v6 原文与示例、同组
  EStG-150 英文输入、显式 legacy 坐标策略，共享 adapter/canonical 校验。各家的
  采样/思考约束如实登记，不声称推理配置完全等同。默认型号尚未实测验证。
- 执行时独立目录、零自动重试、发送前持久化调用账本、原始响应/usage/型号校验、
  费用预留、脱敏、manifest；续跑先核对旧授权、响应及费用，仅发送从未尝试的
  请求。超时、截断、用量/型号异常与 started 未完成均停止，不能自动重发。
- 准备 DoD 已达成：批次前快速检查通过；末次快速检查及具名离线测试 **33 passed**
  （非全量）。首次示例插槽遗漏导致的失败事件保留，已修正并对齐原 runner 消息。
  使用临时假密钥/模拟传输；实际 `.env` 仅追加空白项，已确认 Git 忽略；API=0。
- 本地离线预检 `model_preflight_20261005_v1`：六家各 20 条，共 120 次计划调用，
  `authorized=false`、预算/单价待填写、metrics=null；不是已批准的实验批次。
  填写与运行说明见 `docs/STAGE2_MULTI_MODEL_API_GUIDE.md`。后续须用户批准具体
  模型、样本/调用与费用上限；运行后记录 experiment_run 并 scoped checkpoint。
- 状态：**实现准备完成；真实 API 接入验证与模型敏感性实验待授权**。不改变 Stage 3、
  命名迁移和其他既有未完成任务的状态。

## 2026-10-05 修订 3.7.32：SEP-C3-PROMPT-SIMPLIFY-V1 独立精简分支（零 API）

- 用户要求尝试精简第二阶段 prompt，作为独立分支，并保留已有结果。本轮只准备
  `codex/s2-prompt-simplification-v1` 的候选与离线检查，不启动真实 API 或重跑旧实验。
- A 只压缩 J；B 在 A 上压缩 S 并明确 condition/exception 分类与 action 语法边界。
  原 v6 的六个示例、用户模板和公共关系/原文证据规则保持。System 字符数
  6172 → A 5676（-8.0%）/ B 4398（-28.7%）；不是 token 或性能变化。
- 原始 v6、表一、v6 八格/表二、旧 modular 负结果及配置来源以 15 个已提交 Git
  blob 的原始文本和 SHA-256 保存到
  `outputs/evidence/s2_prompt_simplification_v1/baseline_snapshot.json`。
  本地两份被修改的 modular 报告保留原处，不作为历史结果快照来源。
- 入口为 `prompts/sun_compat/simplification_v1/`；候选只允许显式选择、development
  和独立输出目录。完整 canonical schema、校验器、默认选择、评价器与固定表一不改。
- 离线准备 DoD：候选可由现有 loader/runner 正确装载和渲染；六个示例通过现有
  canonical 校验；历史快照可按字节/哈希核验；候选不能写正式目录或绕过真实调用
  授权；聚焦检查、变更事件与 scoped Git 备份完成。实际验证见本批事件。
- 实测 DoD 仍未达成：新预测与指标为 null，真实调用 0。以后运行须另锁预检、
  预算和授权；不能复用 Stage 3 五次额度或将 B 的联合改动解释成单句因果作用。
  不将整个 SEP-C3、全量测试覆盖或正式发布标为完成，不替换旧表一/表二数值。
- 本子任务的逐项论证见 `prompts/sun_compat/simplification_v1/RATIONALE.md`：对照
  实际删除/改写区块，区分表达合并、提示抽象化和语义修正，记录来源与反面风险。
  A 的顶层字段清单隐式化、B 的触发词减少/最小边界弱化不能表述成已证实无损。
  此补充仅核对已有候选与证据，不修改可执行行为或把离线检查当性能证明。

## 2026-09-26 修订 3.7.31：S2.10/PW7 第二阶段主表最终采用值固定

- 用户要求复核“总体 F1 约 0.83 高于 Sun 约 0.76”并作为最终论文数据，不再改变。
  已有 Table 1 的精确值为 0.8377685388362014/0.7630963921754044；论文固定
  四位 **Direct-LLM 0.8378 / Sun 方法本地重建 Rules-Only 0.7631**，差 **+7.47 pp**。
- 同一 EStG-150、粗句子视图、五字段 `pooled_five_span_fields`；modality label
  单列。固定 `stage2_table1_paper_final_v1.json` 与其中 Gold/两臂预测 SHA 绑定；
  五字段 mean F1 0.8088/0.7970 为次口径，字段差异与局限继续披露。
- DoD 已达成：源报告计数算术、三项输入产物哈希、正式 arm manifests 与既有
  2026-09-21 口径修正证据核对一致；论文 §7.2 与主张 C54、写作入口及 Agent
  合同同步。仅固定既有结果的论文采用决定，不改历史产物，不新增实验或测试。
- 原 v6/R3 的 Direct 正式臂与 B0 正式臂是本表唯一方法身份；后续消融、actor
  refinement、100 候选或新模型结果不替换这张主表，也不再为本表调参、重跑或
  改口径。若发现客观证据错误，先如实报告并等待用户明确的新决定。
- 本项不宣称 Stage 3、整体投稿门禁或其他未完成实验已完成。

## 2026-09-25 修订 3.7.30：S3-TABLE3-R5.1 定向 benchmark 纠错（A/B/C/D/E）

- 目标：在 R5 v1 基础上修正已定位的数据构造、划分、挑战集与复用核验问题，产出可解释、可追溯的 benchmark v2 与执行准备；不重建项目、不重做表一/表二、不写论文/PPT。
- A/B：36 条逐条处置表；has_variants 改为逐类型资格；A1—A6 定位项处理；source_family_id 按 Article 建族、family_id 不等于 requirement_id、消除 Art 13/14/35/36/33 跨 split、暴露族留 development。修正后 31 核心 + 5 候选；105 核心案例；dev/test 22/14；21 族、0 跨 split。
- C：六要素证据绑定与 source/context SHA；condition/exception 分开建模；挑战 BPMN 中性、无答案提示与悬空节点；例外成立=义务豁免。
- D：修正 prepare_stage3_table3_r5_execution.py 复用判断，新增 r5_reuse_verification.py 逐条证据链核验；旧 14 条 Ours 预测全部严格验证。
- E：按修正后唯一请求清单重算 17 次新请求、0 重试、USD 0.91 上限；5 条候选需求不在本轮清单。真实调用 0。
- 验收：结构检查与内容资格审查分开报告；具名反例测试 13 passed；quick integrity pass。表三仍未运行，METHODS_NOT_READY 保留。

## 2026-09-25 修订 3.7.29：S3-TABLE3-R3-INTEGRATION 接线、事件谓词与 M1/M2 后端诊断

- 目标：接通已有 Stage1 P2 与 Stage2->Stage3，修复事件被投影成实体导致的谓词丢失，并建立固定 sm vs 静态 lg 后端对照。

- 冻结配置：`configs/stage3_table3_r3_m1.json`（P2+v4, 原 sm）与 `configs/stage3_table3_r3_m2.json`（相同表示/解析/候选/公式/阈值，仅 Sun/Ours 相似度换 lg 静态词向量）。M0 读取 R2 结果，不重跑；Winter 绑定核验后复用 R2。

- 实现：新增 `stage3_r3_p2_adapter_v1.py`（活动用冻结 P2，事件用 R3 扩展）、`temporal_projection_v4_r3.py`、`r3_sun_scorer.py`、`static_vector_similarity_v1.py` 与 R3 runner/evaluator。旧 P2、旧 scorer、旧投影、旧预测与 R2 manifest 字节保持。

- 结果状态：M1/M2 各完成一轮诊断矩阵和独立评价，输出 3 methods x 20 cases x 5 rules x 3 types = 900 signals；参考为 AI construction，`is_gold=false`。

- 主要数字（overall F1；Sun/Ours/Winter）：M0 0.3429/0.3429/0.5000；M1 0.4324/0.4000/0.5000；M2 0.4000/0.3333/0.5000。M2 没有优于 M1，不得写成最终表三完成或后端优胜。

- 事件修复证据：article18p3 新端点包含 `is lifted`，谓词 `lifted` 保留；但固定 gamma=0.8 下 M1/M2 端点映射仍低于阈值，顺序信号仍为 unknown。该结果同时记录表示修复与相似度上限。

- 交付与审计：`outputs/reports/stage3_table3_r3_delivery_v1.{json,md}`、wiring/projection/backend-diff/mechanism 证据、M1/M2 manifests；真实 API 调用 0。


## 2026-09-25 修订 3.7.28：S3-TABLE3-V4-R2 strict 投影与原因定位

- 用户要求修正 R1 协议偏差：严格恢复 marker.dep==mark 且 post-marker span 内 VERB/AUX head，或 marker.dep==prep 时仅检查直接 pcomp 子节点（恰好一个合法）；禁止扫描其他 advcl/ccomp/xcomp/acl/relcl 谓词；nominal chunk/of-chain 必须完整落在 selected span 内，不完整 of-chain 显式拒绝。
- 新增 `temporal_projection_v3`，保留 v1/v2；Sun/Ours 共用同一版本。新增非评分 `order_failure_diagnostics_v1`，区分 no_rule_order_relation、projection_rejected_range/ambiguity/syntax、endpoint_unmapped、endpoint_similarity_below_gamma、reachability_satisfied/violated、stage2_rule_record_failed；不再把所有 denominator=0 写成 no_rule_order_endpoints。
- R2 复用 `stage3_v4_d1_frozen_v1`，真实 API 新调用 0；R2 矩阵和独立评价已 checkpoint/push。R2 结果与 R1 汇总相同：Sun/Ours overall F1=0.3429、coverage=0.4600；Winter F1=0.5000、coverage=0.7000；三方法 order F1=0.0000，order 可评分母全 0。
- R2 原因：Sun 40 个 projection_rejected_range + 60 个 endpoint_similarity_below_gamma；Ours 40 个 projection_rejected_syntax + 60 个 endpoint_similarity_below_gamma；Winter 100 个 no_rule_order_relation。article18p3 从 R1 的额外扫描 `is lifted` 改为限定 nominal `the restriction of processing`；article13/14 仍无关系但原因可定位；article35/36 有关系但端点未同时超过 gamma。
- 输出：`outputs/development/stage3_table3_v4_r2/`、`outputs/reports/stage3_table3_v4_r2.{json,md,manifest.json}`、`outputs/reports/stage3_table3_v4_r2_cause_analysis.{json,md}`、`outputs/reports/stage3_temporal_scope_candidates_r2.{json,md}`。
- 验收状态：`needs_method_review`，表三未完成。三项 after/temporal 候选仅做来源/offset/SHA/限制修正，保持 `candidate_not_benchmark`，不加入本轮评价，不建新 benchmark，不新增调用额度。

## 2026-09-24 修订 3.7.26：S3-TABLE3-V4-R1 实现纠错与真实 D1 补齐

- Codex 复核 2f9dd9f 后撤回“A 已充分验收、只是 key 阻塞、无机械问题”的判断：
  五个请求真实 payload 的发送编码均不匹配预检 SHA；coverage 把 positive unknown
  算进可观察；Winter wrapper 将原型全局候选角色误缩为当前流程；manifest/隔离
  的实现验证也不充分。完整证据与机械指令在 `docs/agent_prompts/STAGE3_TABLE3_V4_R1.md`。
- R1-A 修正计分/未运行身份及证据链 → R1-B 恢复无标签全局角色词表并冻结共同
  投影 v2 的边界/of 连续性与 prep-pcomp 解析 → R1-C 修复发送端并执行原五次
  授权 D1 → R1-D 新目录三方法推理、独立评分及数据交付；每项独立 checkpoint。
- 数据集、Gold、B0、模型 prompt/registry、五请求 SHA、Sun/Winter scorer 与阈值
  不变；旧输出不覆盖。新增角色词表仅有无标签字符串，不带 case/活动/控制对应；
  投影改进双方相同，研究差异必须披露，不将方法修改的效果归于 LLM。
- 五条 before/prior-to 输入不覆盖 Winter 原生 after/then 支持，顺序缺失不能用
  改名/改句/降阈值消除。补充三项自然 after 条文候选证据作为后续设计材料，
  本轮不建新 benchmark、不加 API；现有三类比较不可观察时继续未验收。
- DoD 仍要求真实运行、正确计数、三类能力证据和完整 provenance；未执行 Ours
  主 F1=null。修复实现与交出诊断不等于最终表三通过，也不以 Ours 是否最高验收。

## 2026-09-24 修订 3.7.25：S3-TABLE3-V4 初版设计与执行记录（验收判断以 3.7.26 为准）

- 用户已接受共同顺序投影及预检固定五次 Direct-LLM，0 重试、总输出 20,480 tokens、
  总预算上限 $8.02；不重问原许可，不将额度挪给消融、coding 或其他批次。
- 静态任务卡：`docs/agent_prompts/STAGE3_TABLE3_V4.md`，由用户转交现有 DeepSeek。
  Codex 决定算法/范围/指标；执行 Agent 只按合同实现与运行，不自行追分改方法。
- 依赖与完成条件：A 共用投影/无外门槛 checker/独立评价器实现并定向验证冻结 →
  B 五请求授权账本与 runner 验证、实际抽取和 manifest → C 三方法全矩阵持久化 →
  D 固定参考独立计分、极端/不可观察诊断 → E 三表数据索引及 Git 交付。
  每个连贯子任务或真实运行均按既有制度 checkpoint/push，门禁满足即继续。
- 范围固定五项义务、20 BPMN，每方法 50 个可评单元（15 正/35 负），另 10 N/A；
  推理全部 900 信号，评价才读取参考适用范围。AI 构造不是正式 Gold，顺序投影是
  对原规则表示的重建补充，不声称原论文数据/代码或完整自动端到端复现。
- DoD：真实三方法逐类/总体 P/R/F1 和计数、unknown/coverage、逐项证据、隔离验证、
  调用账本、manifest、相关测试和已推送 checkpoint 均齐全；无泄漏/错误分母，
  三类能力有可观察证据。真实 F1=0/1 或整类不可观察须诊断并保留 needs_method_review，
  不能仅以数值落在 (0,1) 或 Ours 最高替代实验验收。
- 表一总体 +7.47 pp 基本符合预想；表二 full 111 非最好、J 主效应为负，不支持
  所有模块必要。两表保留真实来源/指标口径，不重跑或选结果迎合写作结构。
- 执行回报（本轮机械实施）：A 已完成并冻结 `temporal_projection_v1`、无外门槛
  `NoGateSunChecker`、独立 evaluator/config/authorization；四个具名测试文件 20 passed。
  B 的预检/授权/runner 绑定已 `--check-only` 通过，但当前进程环境缺少
  `BPC_HYBRID_DeepSeek_API_KEY`/`BPC_HYBRID_LLM_API_KEY`，按合同停止真实调用
  （attempts=0、retry=0、network=0），未读 `.env`。C/D 用冻结 B0 与 Winter 原文完成
  三方法名称下的 900 信号矩阵和 50 单元评价；Ours 因无真实 D1 预测而显式标为
  `blocked_missing_d1_predictions`，全部 unknown，不伪造分数。表三报告
  `outputs/reports/stage3_table3_v4.{json,md}` 状态 `needs_method_review`：Sun/Winter
  out_of_order 分母全 0、Winter incorrect_actor 恒定 satisfied，均为真实负结果。
  这不是完整表三验收；解除 B 环境 blocker 后需按同一冻结 runner 重跑 D1 并重评价。
  E 数据索引见 `outputs/reports/experiment_tables_delivery_v1.json`。

## 2026-09-23 修订 3.7.23：S3-RECONSTRUCT 构造记录（含 3.7.24；授权状态已被 3.7.25 更新）

- 2026-09-24 / 3.7.24 执行准备：五输入的冻结 B0 复用入口与 D1 请求预检完成；
  5 次、0 重试，代理估算 $0.113921、保守授权上限 $8.02，尚未授权真实 API。
  这一步不改变算法，也不解除顺序通路/最终表三范围约束。报告
  `outputs/reports/stage3_d1_preflight_v4.{json,md}`。
- 五输入 B0 本地运行完成（22.973 秒、5/5 成功、API=0），预测已持久化；五项
  都有义务/约束但没有顺序边。顺序转换的独立重建补充待用户判断，不假称原 Sun
  已完整实现，不用新的人工参考覆盖这些真实输出。
- 在首次 Stage 3 评分前修正生成 BPMN 的执行者表示：为原生 Winter 的 process.name
  和 Sun 的 participant 同步名称；保持源文本、构造参考与流程成员不变。
- 新增五项有明确先后证据的 GDPR 义务草案：13(3)、14(4)、18(3)、35(1)首句、36(1)。
  每项 1 基准 + 3 单错误变体，共 20 BPMN；50 项固定可评参考，另 10 项预先定义不适用。
- 这是五条义务范围内的 checking 构造，不是 Sun 四流程/46 篇法规的完整自动端到端
  复现。AI 构造参考不是人工 Gold；保留 `is_gold=false`，不改任何原审核/Gold。
- 发现现行 B0 组合器将所有 order_relations 硬编码为空，单纯增加新句仍不足以补齐
  三类 Sun 能力。先确认共同规则表示的顺序通路，再进行正式 Table 3。
- 本轮新增调用仅准备五条输入的精确预算，旧 74 句复用；不以重建指令替代 API 授权。
- 具体构造及差异：`outputs/reports/stage3_reconstruction_v4_protocol.md`。

## 2026-09-23 修订 3.7.22：S3-ASSET-RECOVERY 与三类 benchmark 重建

- 用户纠偏总结优先：固定 Stage 1≈Sun / Stage 2 为主要变量 / Stage 3≈Sun；禁止
  Ours 专属 grounding、matcher、backend、追分阈值或按结果筛选。
- 官方继承输入审计 verified：两份本地 57 文件一致，活动 7 BPMN 逐字节相同；
  包中没有 Sun 补充合规模型、单错误变体和逐项答案，不能直接恢复原 checking 集。
- v3 外层 matching_score>tau 在可读作者稿中未定义，原 control 完整合规性未确认；
  v3 性能身份撤销，连同 v1/v2/no-gate 保留 diagnostic，不作为最终表三。
- 用户已选择补齐三类：先补充有明确法规顺序的条文，独立构造 control 与 exactly-one-error
  variants；新参考明确来源与裁决身份，不修改旧 Gold 或重开已完成审核。
- 独立 benchmark 仍 in_progress；新 LLM 请求须完成具体 payload/预算后另行授权，
  不把本次实验恢复指令解释为无预算 API 许可。
- 资产报告：`outputs/reports/sun_stage3_official_asset_audit_v1.{json,md}`。

## 2026-09-23 修订 3.7.21：历史 Stage 3 v3 全 Rule Base 诊断（被 3.7.22 纠正）

- 修复原则恢复为：Stage 1 ≈ Sun、Stage 2 是唯一主要变量、Stage 3 ≈ Sun；v1/v2 保留为 diagnostic/superseded，不再作为主 Table 3 协议。
- 新增 `stage3_sun_style_checker`：先对完整 9 条 Rule Base 做 Definition 4 匹配，只有 matched rules 进入 Def. 5–7；Sun 与 Ours 调用同一 checker，只替换 Stage 2 capsule。
- 新增 blinded v3 inference view（仅 `case_id`/`bpmn_path`/`process_id`）和 evaluator-only case map；runner 不读取 pair/role/target rule/target type/activity/Gold。
- 30 pair/60 case 全部 Gold-blind 推理；13 个有效 single-mutation pair 的主 target-seeded 结果：Winter 0.5000/0.6154/0.5517，Sun 0.0000/0.0000/0.0000，Ours 0.0000/0.0000/0.0000。
- Matching AP/MAP：Ours 0.4159/0.0000，Sun 0.3877/0.1000，Winter 0.4343/1.0000。Out-of-order N/A（无真实 rule-side order relation）。
- 完整 multi-label control-vs-violation Gold 不存在，因此 all-alarm/strict 表只作 diagnostic；完整 multi-label Table 3 仍不可发布。报告：`outputs/reports/stage3_sun_protocol_realignment_v1.md`、`outputs/reports/stage3_table3_v3_final_report.md`。
- 零 API、零网络；focused tests 22 passed；`audit_project.py` integrity_pass=True。

## 2026-09-23 修订 3.7.20：S3-BINDING-RESOLUTION 候选判定完成（零外部 API）

- 用户要求由 AI 直接根据候选处理；已完成 30 项的补充判定，
  `data/development/stage3_synth/stage3_binding_resolved_reference_v1.json`，
  `status=ai_resolution_complete`、`requires_human_review=false`、`is_gold=false`。
- 原人工 action/actor ID 均保留。5 个空 action 已归为候选无对应/对象不同/条件检查/
  动作不同；8 个空 actor 中 7 项补充 controller 相对执行者推断、1 项只确认流程执行者。
  10 项顺序均判为 process-only，不制造法规动作对，不再作为用户待填任务。
- 人工结果逐项原样保存；新判断明确归属 AI，不发布 Gold，不作为自动预测输入。
  本次依用户明确请求只读查阅指定归档候选成员，没有解压、恢复或重开审核工具。
- 完成记录沿用 `outputs/reports/stage3_binding_reference_assessment_v1.md`，
  不新建审核队列或重复的状态页；自动方法接入与正式评价仍为独立任务。

## 2026-09-23 修订 3.7.19：S3-BINDING-SCOPE 参考答案与自动预测职责纠正（零 API）

- 完成机械核对：25 个非空 action、22 个非空 actor 引用有效，30 个 target/lane
  均存在于 control BPMN；5/8 个空值合并为 7 个规则—活动组合，10 项顺序仍为
  process-only。报告 `outputs/reports/stage3_binding_reference_assessment_v1.md`
  整理原文与角色定义问题；不恢复旧批次、不撤销既有 30/30 人工确认。
- 原 supplied-binding runner/evaluator 更名为 `*_stage3_binding_oracle_v1.py`，
  产物明确标记 oracle、使用人工绑定、不可声称端到端 Ours。原方法只把
  Direct Rule Record 用于 ID 诊断，不能因输入该文件就称为自动 grounding。
- 纠正“只差人工标注、不差代码”的旧结论：已有 Sun 自动匹配和 action matching v3；
  自动预测接入与独立评价仍需完成。参考绑定只用于评测，预测不得读取 target ID、
  expected lane、mutation order_pair 或人工答案；不能把 Gold/预测的 ID 相同当语义对齐。
- 不要求强行填满 null 或制造法规顺序；先区分权利主体与流程执行者，再对有原文依据的
  新语义问题申请最小人工裁决。当前没有需要重新操作的审核批次。本次未生成 Gold，
  未运行预测/评价/API，也未恢复用户取消的规则先行 LLM fallback。

## 2026-09-23 修订 3.7.18：S3-BINDING-REVIEW 人工复核完成并归档（零 API）

- 用户已完成 30/30 项确认，状态 `human_review_complete`；唯一活动结果为
  `data/development/stage3_synth/stage3_binding_human_decisions_v1.json`，原样保留人工决定。
- 本批候选、初审、空白模板、旧 blocked 报告、临时审核工具及备份已封存。
  撤销旧启动入口，归档排除默认搜索和文件目录；新批次必须采用独立 ID 与路径，
  不再从历史日志恢复这批待审核任务。追溯时才查归档清单。
- 仍有 5 个 action、8 个 actor 引用为空，10 项顺序均为 process-only；
  用户接受这些候选不等于绑定齐全或 Gold 发布。后续校验/检测必须明确指定输入，
  本次不生成 Gold、不推进正式 S3.7、不运行实验或 LLM/API。

## 2026-09-19 修订 3.7.16：SEP-C3 targeted refinement A/B/C/D 收口与论文接入（零 API）

本轮把已有 targeted refinement 证据收口并接入论文，不新增 API、不修改 prompt、runner、正式默认配置或模型参数。

- A/B/C/D 四臂在固定 EStG-150 上各 150 条、共 600 calls，成功 600、失败 0。A/B/C/D 五字段 mean F1 为 0.7246/0.7806/0.7558/0.7858；actor F1 为 0.6314/0.7672/0.6807/0.7284；constraint F1 为 0.6562/0.6943/0.7351/0.7664。
- D 的平均 F1 高于 B，不能写 B 总分最高。保留 B 的理由是 B 的 actor F1 高于 D、composition 更简单，旧 R_C 的 recall 收益伴随 precision 下降、FP 净增加和 B→D 六个空-Gold actor regression。B 只是本轮研究参照，不是正式默认替换，也不是事后阈值结论。
- taxonomy 校正：52 条 recovery 比较记录/37 个独立 sample_id/52 个恢复 Gold span；原 40 条/28 个样本；旧 time=33 与 legal-reference=0 撤回；校正标签为 AI 多标签复核，不是人工 Gold；完整可解释 21、部分内容 29、仅 overlap 2。五臂 v2 `BASE+RC1+T+G+TG` 750-call 计划保持 NO-GO/未执行，不自动改成 300/450。
- 论文与文档接入：`paper/THESIS_DRAFT.md` §4.2/§6.6；`paper/ABLATION_MATRIX.md` SEP-C3 节；`paper/CLAIM_EVIDENCE_MATRIX.md` C50-C52；`docs/PROJECT_AUDIT.md`。B 的完整 prompt 为 `prompts/sun_compat/modular_refinement_v1/generated/direct_llm_refinement_B_v1.md`，文件 SHA-256 `c468c631b6e454522994d6839f6a4021a259daedea7f3a2852b7b4343cd22849`，composition SHA-256 `207b54cc2f1123c7511451d7ead478654e550d438fe19d1031a13149b41917f1`。
- 未完成与下一步：SEP-C3 modular_v1 的 000-111 八个 E/S/J 组合已在 2026-09-17 前全部执行（前一批 111/011/101/110；增量批 000/001/010/100；每臂 150 条、failed=0、无重复发送），但四格与四格未同批交错、每格仅一次，批次/时间与因子单元混杂，不能据此作稳定的主效应/交互结论；已有原始响应后处理归因仅有本地分支 9b50729 对旧 v6 D-full-0813 与 modular 111 的局部分析，其余 arms 未覆盖且 adapter/canonicalizer/validator 子步骤贡献不可独立分离；重复运行不确定性仍未完成。整个 SEP-C3 不能标记完成。下一项仍按真实依赖推进 SEP-C2 的 S2.12 Direct-36（D-CAL 1 + D-REST 35）；零调用就绪核验见 outputs/reports/s2_12_direct36_readiness_review_v1.md，当前受未签发 successor 两方法授权、总输入/token 与 USD 硬上限未给、外部发送审批未解除和当前价格未复核阻塞；GDPR Direct-74 分列，不自动并入本次最小任务。继续追加 prompt 候选不应先于该核心证据缺口。

## 2026-09-17 修订 3.7.15：CSCWD 2027 投稿定位与文献/证据边界（文档）

用户确认以 CSCWD 为目标，优先完整说明现有方法、比较与实证观察，避免为明显创新不断
新增模块或实验。用户补充当届通知：2026-10-31 截稿，2027-01-31 通知，2027-05-26
至 28 Brisbane 会议；EasyChair 公开页已核到当届新稿开放，官网正文因访问失败尚未独立
复核日期、时区、页数及匿名规则。保留 9 月 30 日导师完整初稿目标，不新建日历阶段。

- SEP-C1/PW1–PW5 接入 `paper/CSCWD_POSITIONING.md` 的近邻文献表与贡献边界：
  LLM+BPC / Sun semantics+LLM 已有先例，论文以有证据的适配、受控比较和错误分析定位。
- SEP-C4/PW8 优先补清固定检查器下的同条款/流程成对证据；明确人工规则 Oracle 隔离
  已有开发结果、正式主表仍缺，不能将 EStG 字段分数直接归因到 GDPR 判定变化。
- 描述 Stage 1 target-aware、Gold 辅助来源、同面板调试与阈值探索、unknown/合规区别；
  不把内部 formal 资产称为独立盲测，不把条件/例外扩展归为前人原生能力。
- 完整工作稿与会议精简稿分层组织，六页仅为往届格式下的暂定预算；近期四臂 prompt
  负结果按实际范围保留，不补造八组合结果，不恢复已取消实验。
- 本批只更新投稿准备与来源记录，不改变任何实验状态、算法、数据、机器门禁或授权；
  文档检查与 scoped Git commit/push 构成记录，不运行实验审计或测试。

## 2026-09-15 修订 3.7.14：SEP-C3 E/S/J 精简 prompt 真实四臂验证（600 API）与退回旧版

按用户本轮授权，完成公共接口/S 边界修正和实际入口接通后，真实运行 111/011/101/110 四个单因素组合各 150 条，共 600 次 Direct-LLM 调用；旧版完整 v6 复用同一模型发布批次 D-full-0813（无额外调用）。固定 EStG-150 input、冻结 Gold、coarse sentence-level 五字段 mean F1 主口径，modality label 分离报告。

结果（主口径 five-field mean F1；旧版 D-full-0813=0.7850）：
- 111 = 0.7262（比旧版低 0.0588）
- 011 = 0.7470（删除 E；比 111 高 0.0208）
- 101 = 0.7611（删除 S；比 111 高 0.0349）
- 110 = 0.7355（删除 J；比 111 高 0.0093）

验收结论：完整新版明显退步；三个单模块删除均未使完整版达到"至少高 0.01"的贡献标准，全部验收检查失败。actor precision 从旧版 0.573 降到 0.354，111 预测 130 个 actor span（旧版 82），其中 84 个为 FP；`estg_000664` 111 多抽 "The following""taxation" 等非 actor。E 存在时 `estg_000028` 的 condition 漏抽。J 删除后主口径未下降，且 110 的 raw bare-JSON 仍 150/150。新版 raw bare-JSON 150/150 对旧版 107/150 是真实格式收益，但不满足主 F1 门槛。

处置：退回旧版 `prompts/sun_compat/direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md` 为默认 Direct-LLM prompt；`modular_v1` 保留为已实测未通过候选，不得作为正式替换。证据：`outputs/reports/sep_c3_modular_ablation_v1.*`、`outputs/reports/sep_c3_modular_ablation_analysis_v1.*`、`outputs/evidence/sep_c3_modular_ablation_v1/`。实际 API=600，失败=0，重试=0，调用上限=750；一次 shell reset 后从 59 条持久化 raw 续跑，样本未重发。

## 2026-09-15 修订 3.7.13：SEP-C3 Direct-LLM E/S/J 模块精简与八组合离线拼装（零 API）

本轮只精简现有 Direct-LLM prompt 的公共部分与 E/S/J 三个模块，不运行 API、不重跑消融、不新增性能结论。

- 公共部分只保留任务、输入 envelope、字段名称、固定 `method`/`validation` 值和最低输出接口；语义、示例、格式指导分别归 S/E/J。
- 删除或合并了历史 prompt 中的逐字/近义重复：constraint 定义、action 排除、condition 定义、空数组约定、精确坐标自检、JSON 键/类型强调和示例内重复的完整 JSON 骨架等。
- 新资产位于 `prompts/sun_compat/modular_v1/`：`common_system.md`、`user_envelope.md`、`semantic_rules_S.md`、`examples_E.md`、`output_format_J.md`；八组合 prompt 和 manifest 位于其 `generated/`。composer 为 `src/bpc_hybrid/modular_prompt.py`，构建/检查入口为 `scripts/build_modular_prompt_v1.py`。
- 离线检查 000–111 八组合全部通过：最低接口、关闭模块无残留、无悬空 `{few_shot_block}`、`prompt_loader` 抽取与 renderer 一致、生成文件与 manifest 一致。报告见 `outputs/reports/sep_c3_modular_prompt_v1_offline_check.json`，说明见 `outputs/reports/sep_c3_modular_prompt_v1.md`。
- 历史 v6 prompt、`ablation_v1/v2`、既有 450-call 结果和运行脚本保持原样，避免影响旧实验复现。
- 边界：E 示例仍会展示少量字段形态；固定 schema/validator 的坐标与引用校验仍会形成计算耦合。本轮没有证明单因素消融不显著的原因，真实效果仍需单独授权运行。

## 2026-09-15 修订 3.7.12：PW 写作目标与工作、数据呈现要求

用户要求：“目标是写清楚自己的贡献，把自己做的事情都要写清楚，把一些数据都要放在论文里”。
PW1–PW9 以完整说明已有研究工作、具体贡献和相关数据为写作目标；定义、设计、
配置、统计与案例表也是正文的有效内容，不要求每张表独立证明创新。先组织已有
工作形成完整初稿，按具体证据缺口补必要内容，不因追求创新或表格数量自动扩展实验。
章节与候选图表清单统一放在 `paper/README.md`，本文件 §12.1 引用该清单。
本次仅登记写作要求与覆盖清单，不声称全部论文内容已写完，不改变既有实验任务、
两方法范围、指标口径或完成状态；没有新增实验、API 调用或代码测试。

## 2026-09-15 修订 3.7.11：SEP-C2 Stage 2B Winter 前人基线首轮实跑（零 API）

本轮直接跑出前人基线首轮结果，不再以范围登记/方案准备代替实验。

- Springer 最终版入口可访问；Notes 指向 archive.org input-2 与原型站。本环境 archive.org 超时、原型站 DNS 失败，未下载新包。
- 作者归属：`references/合规性检查模型代码/model_check` 与 Winter 副本 112 个非缓存文件逐字节相同，额外 11 个均为 `__pycache__/*.pyc`；未发现 Sun Stage 2 源码。可运行实现是 Winter prototype。
- 固定方案：输入 EStG-150（150 条）、Gold 231 个 clause_span；共同子任务 `estg150_clause_region_detection_v1`；指标为 statement-level 任意非空字符交集 P/R/F1。
- Winter 原生输出 287 句、163 个 signal-word constraint 句、389 个 obligation clause、9 flows；适配只映射义务从句自身字符区域，明确不支持 action span/six-element，不用 LLM 补字段。
- 首轮结果：Winter **1.0000/0.8312/0.9078**；历史 Rules-Only **0.9398/1.0000/0.9689**；历史 Direct-LLM **0.9476/0.9740/0.9606**；零新增调用。
- 真实失败例：Winter estg_000071 无 signal word 零预测漏 3 区域；Direct-LLM estg_000112 零 clause 漏 1 区域；Rules-Only 无 complete miss。
- 边界：Sun 表 12（Winter 0.58/0.89/0.70；Sun 0.77/0.83/0.80）是私有 BPMN violation 任务，不能与本适配结果直接比较。
- 产物：`outputs/reports/sep_c2_stage2b_predecessor_baseline_v1.*`、`outputs/evidence/sep_c2_stage2b_predecessor_baseline_v1/`、public source probe；独立 verifier 与 6 个 focused tests 通过。
- 下一步：继续检查更直接兼容的前人抽取实现；若只有 Winter，则补其 Stage 3/同条件可运行复现并把结果接入论文证据位置。

## 2026-09-14 修订 3.7.10：SEP-C2 两方法证据判定收口与 S2.13 v10 后继入口（零 API）

本修订只修 3.7.9 发现的证据判定缺口，随后直接继续前人基线实跑；未重跑 S2.12 真实实验，真实 API=0。

- `comparison.complete` 复用 Rules-Only 与 Direct-LLM 既有独立 verifier，并核对冻结输入绑定、固定 36 条总体（失败行保留）、有限指标和 verifier 绑定/重放结论；只看 `status`/`dataset_id` 不再足够。
- 必要证据缺失时合同保持 `partial_two_method_contract_pending_direct_llm`；失败真实运行不丢弃样本，也不自动禁止评价。
- 新增 S2.13 后继入口 v10：S2.12 状态完全从两方法合同派生，S2.13 只等待两方法证据链，取消 `sun_llm_fallback` 修复组依赖；v9 及更早胶囊 byte-exact，历史三方法报告不覆盖。
- 当前真实状态：Rules-Only 验证通过；S2.12 Direct 预测/评价不存在，因此 `comparison.complete=false`、`s2_13_complete=false`，v10 为 `blocked_only_on_two_method_contract`；未提前标完成。
- 具名测试覆盖缺证据拒绝、完整证据通过、取消组不参与及 v10 合同驱动状态；未跑全量测试。
- 下一步：直接执行 SEP-C2 Stage 2B 前人对照首轮实跑（优先 Winter 现成实现与 EStG-150 共同子任务），不以准备文档代替运行结果。

## 2026-09-14 修订 3.7.8：用户取消全部规则＋LLM 后续实验

用户明确要求：“规则+LLM直接不要了，不在进行规则+LLM的任何实验”。本条优先于
下方旧三方法计划与历史授权：Rules+LLM-Repair（`sun_llm_fallback` / H1）退出后续
实验，不再运行、复跑、优化、消融或新做其下游比较。S2.12 的 F-1/F-2/F-3 共 27 次
调用取消；其他规则先行、LLM 修复/补判的混合 fallback 实验也不再派发，包括待执行
的 Stage 3 混合 fallback。既有代码、数据、结果与授权事件保留为历史来源。

当前方法主线为 **Rules-Only 与 Direct-LLM**；必要的 Sun/Winter 前人对照、直接
LLM 的 E/S/J 消融和固定 Stage 3 衔接继续按原任务推进。S2.12 比较使用同一 36 条
文本；取消修复组后剩余计划为 S2.12 Direct-LLM 36 次 + GDPR Direct-LLM 74 次，
合计 **110 次**，取消的 27 次不挪用。旧 137 次发送确认请求和下方 preflight v1
均不可作为当前执行范围；本次取消不授权任何真实调用。

SEP-C2 下一最小工作为适配两方法执行/评价/冻结合同，保留原输入与 Direct 请求，
移除 S2.12/S2.13 对未执行修复组的完成依赖；不能伪造该组完成或绕过其他门禁。
本批只修改派工与论文文字，机器合同和历史授权文件未改；在适配完成前不执行旧
三方法串行链。原自动审批阻塞保留；真实 API=0，无测试或实验重跑。

## 2026-09-14 修订 3.7.9：SEP-C2 两方法执行/评价/冻结合同适配完成（零 API）

3.7.8 只完成派工与论文文字收窄；本修订完成用户要求的实际机器适配，仍为零真实调用：

- **取消组机器门禁**：`configs/s2_12_active_method_scope_v1.json` 固化 active =
  Rules-Only / Direct-LLM，`sun_llm_fallback` 的 F-1/F-2/F-3 共 27 次
  `must_not_run=true` 且不可挪用。S2.12 fallback 入口在构造 transport、发送请求和写
  输出前抛出取消错误；finalize/evaluate 的取消 arm 入口同样拒绝。
- **后继预检**：`configs/s2_12_active_preflight_v2.json` +
  `outputs/reports/s2_12_active_preflight_v2.json` 只锁 Direct 36 个请求体，逐条与历史
  v1 direct 36 行 byte-identical（输入、prompt、采样参数、输出接口不变）。v1
  三方法 lock/report、旧授权/回执保留为历史来源，不被覆盖或复用为当前范围。
- **执行/终态化/评价**：Direct runner、finalize、evaluate 使用 active 预检和
  `arms=('direct_llm',)` 重建路径，不读取 F 阶段账本、修复结果或三方法齐全条件；
  D-CAL=1、D-REST=35 的 36 次预算保留；Direct 未真实运行时 prediction 与
  evaluation 缺失显式保留，不从 fake 响应或其它数据集补。
- **失败样本总体**：Direct 评价固定保留全部 36 行；`in_doubt`/failed 行按空
  canonical record 计入漏抽/误判，不使用成功样本子集。
- **两方法评价/冻结**：`outputs/reports/s2_12_two_method_contract_v1.json` 及其
  manifest 绑定 Rules-Only 既有评价、Direct 预测/评价缺口、输入与请求哈希、输出目录和
  36+74=110 次剩余计划。当前 `comparison.complete=false`、`s2_12_complete=false`、
  `s2_13_complete=false`，`cancelled_repair_arm_required=false`；因此缺少 Direct
  不能靠方法数减少直接冻结成功，S2.13 只等 Direct 真实结果与同口径两方法比较。
- **零 API 与授权边界**：真实 API/网络仍为 0；旧 137 次发送确认范围失效且不原样复用；
  本轮取消决定不是外部发送授权。GDPR 默认 `gdpr7_direct_llm_v1` 的 74 条
  `fake_payload_locked` 演练（network=0）不得作为真实预测、恢复账本或 promotion 来源；
  真实目录仍为 `gdpr7_direct_llm_raw_real_v1` / `gdpr7_direct_llm_real_v1`。
  进程环境凭据前置条件已在此前离线复核中证明存在；本轮不读取、不打印 `.env` 或凭据。
  外部自动发送审批阻塞仍未解除。
- **验证与边界**：新增 `tests/test_sep_c2_two_method_execution_contract_v1.py`
  覆盖修复组不能运行、缺 Direct 不能完成、Direct active 重建不依赖修复组；同时更新
  fallback runner fake 测试为拒绝路径。本修订交付的是合同/代码适配，**不是实验完成**。

## 2026-09-14 修订 3.7.7：SEP-C2 真实执行准备通过，首次发送被自动审批阻止（历史范围，已被 3.7.8 收窄）

主工作区已快进接收 SEP-C1-B 三个提交至 `952b405`，原有 20 个已修改/未跟踪文件
逐文件 SHA-256 保持不变（嵌套旧 worktree 未改动）。继续执行 SEP-C2 时，快速完整性
检查通过（errors=0），S2.12 授权验证 70/70 通过；真实账本/胶囊尚不存在，无并发
实验执行器。仅在子进程补齐非秘密配置后，离线环境检查为 READY；已存在密钥，未读
`.env`、未打印凭据。官方当日价格页核验模型 `DeepSeek-V4-Pro-0813`、峰谷价格及
闲时与原合同一致，既有授权/锁定请求文件未改动。

实际启动 D-CAL 第一条请求时，**自动审批在创建进程前拒绝了操作**：不接受项目
文件中的历史授权加“继续运行”作为本次向 DeepSeek 发送实验文本的充分依据，要求
当前任务明确确认目的地与数据范围。真实调用/费用均为 0，未重试或绕过。该阻塞与
实验门禁、密钥缺失不同；历史 137 次授权未被撤销或扩大。

证据与待确认范围：`outputs/reports/sep_c2_execution_preflight_v1.json`。
下一动作仍为 SEP-C2 的 D-CAL 首次发送；确认后按原 63 次和 74 次独立预算续做，
S2.12 DoD 后再 S2.13。GDPR 默认 v1 目录的 74 条 completed 是 `fake_payload_locked`
演练，只能保留为演练；真实运行使用已有约定的 `*_real_v1` 独立目录。本轮没有
实验结果、程序改动或新增测试；上述检查发生于真实运行准备，不是全量验证。

## 2026-09-14 revision 3.7.6: SEP-C1-B comparison scope, general title, and full E/S/J factorial budget (zero API)

SEP-C1-B 已在主工作分支的后续 scoped commits 中完成；本轮只做只读原文/资产核对与
写作/预算准备，未运行实验、未调用真实 LLM/API、未修改可执行 prompt、检查器或 Gold。

- **前人比较范围**：论文 §2.3 新增情态分类、六要素抽取、下游匹配/违规检查三层
  比较注册；本地 Sun PDF 明确为较早作者稿，最终版仍按 DOI
  `10.1007/s11227-023-05626-0` 与 `TODO-SOURCE:SUN2024VOR` 核验；Winter 原方法 /
  Winter wrapper / Winter-style 四类扩展基线严格分名。
- **通用题名**：固定推荐中英文题名，使用自然语言合规需求覆盖法律、监管、制度
  和业务规则，并明确设计时 BPMN 流程检查范围；保留两个备选；现有数据覆盖仅为
  EStG-150 与 GDPR-7/S2.11 面板，不声称跨领域/跨语言/企业部署泛化。
- **完整组合与预算**：E/S/J 八组合 000-111 已登记；共同最低输出接口明确；现有
  450-call 四臂因批次/设计混杂只作历史单因素证据，主推荐为同批次
  8x150x2=2400 calls，预计 input 8,687,550、input cap 13,031,325、output cap
  9,830,400、USD cap 67.36、off-peak CNY envelope 229.63 元；复用变体 1800 calls
  仅作非推荐备选。主效应/交互、失败计数、bootstrap 分析协议已预注册。
- **边界**：价格快照日期 2026-08-30，本轮未联网复核；执行前必须重新核验；上述 SEP-C1-B 主设计的 000-111 组合保持待运行；其缺失四臂/八臂 runner/重新渲染 token 预算仍需下一实现批次完成；用户逐字授权与授权事件仍待。注意：SEP-C3-MODULAR-ESJ-002 的 000-111 八组合已在 commit 18f5cf9 及前批中各执行一次（每臂 150、failed=0、无重复发送），但那是不同 prompt 实现、非同批、每格一次，不能替代上述同批双重复主设计。

**下一项固定为 SEP-C2（此段为 2026-09-14 历史计划；2026-09-19 现行范围见文首 3.7.16）**：必要前人对照与既有授权批次。启动时先核验当时记录的 137 次授权（其中 S2.12 修复 27 次已取消）、账本、载荷与进程环境可运行性；S2.12 DoD 后再推进 S2.13。SEP-C1-B 的同批 2400-call E/S/J 消融主设计仍依赖其缺失四臂实现、重新渲染预算和单独用户授权，不能因 SEP-C1-B 已完成就自动执行；该句不代表 SEP-C3-MODULAR-ESJ-002 的八组合未执行。

## 2026-09-14 修订 3.7.5：C36 v2 / SEP-C1-A 交付复核

C36 v2 的门禁与依赖绑定、SEP-C1-A 的三阶段 I/O 和 SIM 成功/失败案例已落地，
对应 `6c22b8a`、`4fdc91f` 已接入主工作区并推送。正文复核进一步限定配对评价的
实验范围，并根据冻结 capsule 纠正 r10 A 组的中断点为动作匹配未通过阈值。
仅核对现有证据、修订文档，未重跑实验、API 或测试；不将跨工作区审计记录升级为
同状态全量验证。

**历史计划：SEP-C1-B**：前人比较范围、暂定通用题名、prompt 消融缺口/重复
次数及预算准备已完成，见 3.7.6；预算准备未授权任何真实调用，已发现的约束
失败仍保留在原四类违规分析任务，不插队。

## 2026-09-14 revision 3.7.4: C36 target-paired acceptance gate, dependency binding and control-boolean persistence (S3-C36-TARGET-PAIRED-V2, zero API)

**Scope**: successor revision `s3_c36_target_paired_v2`; the same frozen
C36/Winter and v5 predictions are reused read-only; v1 artifacts are not
overwritten and the historical C36/v5 files remain untouched.

**Acceptance gate (new)**:
- The comparison is produced only if every blocking condition passes: 40 unique
  C36 rows and 40 panel variants; exactly 40 current variant + 40 current
  control rows keyed uniquely by `(item_id, side)`; item ids, expected labels,
  process ids, rule ids and variant/control BPMN SHA-256 values identical to the
  panel and C36 source; both prediction files hash-bound to their producing
  manifests; per-type field legality (`observable` boolean, observable variant
  violation boolean, unobservable entries kept unknown, control entries with
  score/exact_contradiction and no persisted final boolean); finite row
  `gamma_ext` equal to the frozen manifest threshold; and required C36 manifest
  input hashes matching.
- Gate result: **pass**, blocking issues **0**.  A failed gate writes only
  `blocked_audit.json` and a `BLOCKED_COMPATIBILITY_AUDIT` report with
  `valid_comparison_generated=false`, and no comparison artifact; this blocked
  path is covered by a focused test.
- Dependency binding: current `src/bpc_hybrid/stage3_extended_violations.py`
  matches the historical C36 manifest implementation hash under its declared
  `canonical_lf_utf8_text` mode (raw hash differs; canonical-LF hash matches).
  The target-paired evaluator
  `s3_semantic_grounding_v3.evaluate_target_paired` is recorded as the current
  protocol rather than a historical manifest artifact.  Frozen
  `gamma_ext = 0.5`.
- The 40 control samples / 160 control-side checks now persist the
  reconstructed per-type `status` and `violation` (boolean, or null for
  unknown) directly in the v2 80-row check artifact.  The unified single-label
  prediction is not used to derive these booleans.

**Target-paired comparison (same protocol, unchanged numbers)**:
- Baseline (now named **Winter-style four-type extension baseline**, not a
  direct Winter paper result): Macro-F1 **0.6036**, pair success **18/40**,
  target unknown **0.3625**, control target FP over all pairs **0.0750**.
- Current v5 deterministic: Macro-F1 **0.6737**, pair success **21/40**,
  target unknown **0.3375**, control target FP **0.0250**.
- Delta current-minus-baseline: F1 **+0.0701**, pair success **+3**, unknown
  **-0.0250**.  Development-only synthetic panel, not formal Oracle.

**Evidence**: `outputs/reports/s3_c36_target_paired_v2.{json,md}`;
`outputs/evidence/s3_c36_target_paired_v2/{audit,comparison,manifest,artifact_hashes}.json`
and `c36_winter_target_paired_checks.jsonl` (80 rows);
`src/bpc_hybrid/s3_c36_target_paired_v2.py`;
`scripts/run_s3_c36_target_paired_v2.py`;
`tests/test_s3_c36_target_paired_v2.py` (**7 passed**).  Real API = 0; no full
test suite was run.

**Next step**: S3-C36-TARGET-PAIRED is complete and delivered.  Continue
SEP-C1-A: write the three-stage I/O contract and the SIM r10 success / r8
failure chains into the existing paper, then check the source records and the
claim-evidence matrix.  Real v5 fallback remains blocked on a scope/hash-
specific authorization.

## 2026-09-14 revision 3.7.3: C36/Winter target-paired compatibility audit and comparison (S3-C36-TARGET-PAIRED, zero API)

**Scope**: new revision `s3_c36_target_paired_v1`; frozen C36/Winter and v5
predictions are reused read-only; historical C36/v5 artifacts are not
overwritten.

**Audit findings**:
- Same 40 item ids as the current synthetic panel and v5 variant rows; no
  missing or extra items.
- Expected labels, process ids, rule ids and variant/control BPMN hashes match
  the panel for all 40 pairs.  C36 manifest raw hashes for the rule inference
  pack and panel match the current files; `gold_visible=False` on all rows.
- Variant side: all 40 rows contain four `scores_detail` checks with boolean
  `observable`; every observable entry has an explicit boolean `violation`;
  unobservable entries are converted to `unknown`, never negative.
- Control side: all 40 rows contain four `control_scores` checks with boolean
  `observable` and a score when observable; no persisted final `violation`
  boolean.  The frozen project function
  `control_prediction_from_scores(control_scores, gamma_ext)` reconstructs the
  per-type control boolean from those saved fields.  This affects 40 control
  samples / 160 control-side checks and is recorded as a reconstruction
  dependency, not a blocking gap.  No unified single-label prediction is used.
- No blocking field gap; the target-paired comparison can be built under the
  documented reconstruction rule.

**Target-paired comparison**:
- C36/Winter: Macro-F1 **0.6036**, pair success **18/40**, target-field unknown
  **0.3625**, control target FP rate over all pairs **0.0750**.
- Current v5: Macro-F1 **0.6737**, pair success **21/40**, target-field unknown
  **0.3375**, control target FP rate over all pairs **0.0250**.
- Current-minus-C36 delta: F1 **+0.0701**, pair success **+3**, unknown
  **-0.0250**.  Per-type F1: C36 0.8696/0.3333/0.7500/0.4615 vs v5
  1.0000/0.9000/0.3333/0.4615 (prohibited/condition/constraint/exception).
- This is a same-protocol development comparison, not a formal Oracle result.

**Evidence**: `outputs/reports/s3_c36_target_paired_v1.{json,md}`,
`outputs/evidence/s3_c36_target_paired_v1/{audit,comparison,manifest,field_gaps}`,
`src/bpc_hybrid/s3_c36_target_paired_v1.py`,
`scripts/run_s3_c36_target_paired_v1.py`,
`tests/test_s3_c36_target_paired_v1.py` (6 passed).  Real API = 0; no full test
suite was run.

**Next step**: the target-paired comparison is complete for the frozen panel.
No re-inference is required for this comparison.  If a future reviewer requires
independently persisted control booleans, the minimal offline task is to write
the already-reconstructed per-type booleans from the saved `control_scores`
using the same frozen rule; no new API or model inference is needed.

# LLM4BPC 完整实验主 Pipeline

**文档版本**：3.7.2
**状态**：ACTIVE — 全项目研究与任务分解的唯一主线
**最后更新**：2026-09-14
**方法学主干**：Sun et al. (2024)（三阶段方法主干）；Barrientos et al. (2026)（直接借鉴来源：LLM 结构化输出、验证、受控词汇、归一化与评估纪律）
**当前实施优先级**：按下方「CSCWD 按依赖推进的收尾 Pipeline」执行；满足启动条件就开始，完成一项立即推进，发现问题逐项定位、修复和验证。2026-09-30 导师初稿、2026-10-31 投稿截止是最晚目标，应尽早完成；写作持续同步，正式实验仍遵守 Stage 2 冻结到 Stage 3 的实质依赖。

> 所有 Agent 在修改实验代码、配置、数据协议或研究设计前必须完整阅读本文。
> 本文定义“要完成什么、先后依赖是什么、每一步怎样算完成”。
> `docs/PROJECT_AUDIT.md` 只记录实时进度；不要再创建新的日期版
> `STATUS_*`、`HANDOFF_*` 或平行路线文档。

## 2026-09-14 修订 3.7.2：Stage 3 v5 执行到评价闭环（S3-V5-RUNNER-INTEGRATION）

本项承接 DS 的 v3→v4→执行器→v5→preflight 五个已推送提交，属于 SEP-C4 的正确性修复。
冻结 pipeline：**v5 预测与候选包 → 输入哈希核对和局部流程重建 → fallback 响应 →
逐对象回绑 → v4 程序复核 → v5 锚点保护 → 保存 80 条预测 → 同口径配对评价**。
不得用模型判断直接替代程序复核，不读取期望标签来决定预测。

| 子项 | 完成定义 | 本次状态 |
|---|---|---|
| 模拟/真实执行隔离 | 独立目录；mode、候选包、请求集、冻结预测身份一致才可恢复 | verified（离线） |
| 相同请求与中断恢复 | 22 个对象的 18 份唯一正文只发送、计费一次；结果回绑各自对象；send_started 中断不自动重发；usage 未知不报完成 | verified（离线） |
| 响应到评价接通 | 接受 validated 响应；逐字段复核后保留 v5 保护；预测先保存，标签后评价；恢复可重建相同预测 | verified（离线） |
| v5 真实 fallback | 新范围授权、冻结载荷和预算、真实账本、完整预测与对比均具备 | blocked：尚无该范围授权，真实 API=0 |
| S3-C36-TARGET-PAIRED | C36/Winter 40 pairs, both sides and four checks audited; target-paired comparison generated under frozen control reconstruction | completed; see outputs/reports/s3_c36_target_paired_v1.* |

验收：五个相关测试文件共 **42 passed**，快速完整性检查通过；没有全量测试。
真实面板的离线恢复消费 22 个响应对象，新增发送 0，输出 80 条预测。
证据为 `outputs/evidence/s3_semantic_grounding_v5_integration_v1/mock/attempt_002/`；
`attempt_001` 是发现 validated 状态接线缺陷的中间证据，不能作为闭环验收。
模拟指标仅证明执行链可传播变化，不能证明 LLM 效果。
DS v5 的有效开发指标仍为 Macro-F1 **0.6737**、配对成功 **21/40**、目标 unknown **0.3375**。
旧诊断的 control 告警 26→24 是撤回两项判断到 unknown；缺少全局负例 Gold，不能称为总体误报率改善。
各项验收后立即 checkpoint，继续已具备依赖的对照或写作，不设置中间日历等待。

## 2026-09-13 revision 3.6.61: Stage 3 v5 action-anchor consistency repair and constraint/exception failure chains (S3-SEMANTIC-GROUNDING-V5, zero API)

**Scope**: inspect the frozen v2 per-item constraint/exception failures, add revision
`s3_semantic_grounding_v5`, and reuse v2/v3/v4 predictions/manifests read-only.

**Failure chains and repair**:
- Constraint false-positive chain: for `syn_v2_exception_not_handled_06` control, the
  rule constraint is `not later than 72 hours` and the rule action is
  `notify the personal data breach`. The frozen action grounder resolved to the
  generator-inserted exception-handler node whose label equals the rule exception text.
  The local constraint check then reported a violation because no 72-hour bound was
  found around that non-action node.
- v5 guard: when the resolved activity label strongly matches a non-action rule field
  and does not match the rule action, condition/constraint determinations anchored to
  that node are demoted to `unknown`. Exception-handler checks are not rewritten; no
  per-sample threshold tuning and no API call.
- Exception failure chain: for `syn_v2_exception_not_handled_02` variant, the frozen
  process does not express the rule action, so action grounding remains unresolved and
  handler absence cannot be programmatically established. The record stays `unknown`
  and is recorded as a capability boundary instead of a fabricated violation.

**Change and cost**: changed checks 2 (both control clear -> unknown); removed control
false alarms 2 (legacy diagnostic control false-positive checks 26 -> 24); no
target-paired variant positive demoted; Macro-F1 0.6737 unchanged, pair success 21/40
unchanged, unknown rate 0.3375 unchanged. F1 increase is not an acceptance condition.
The v5 fallback pack has 22 items (7 variant + 15 control) with evidence reachability
and semantic preservation passing.

**Evidence**: `outputs/reports/s3_semantic_grounding_v5.{json,md}`,
`outputs/evidence/s3_semantic_grounding_v5/`,
`tests/test_s3_semantic_grounding_v5.py`. Real API = 0.

## 2026-09-13 修订 3.6.60：Stage 3 LLM 执行、断点恢复与预算/时段 fail-closed（S3-SEMANTIC-GROUNDING-LLM-EXECUTION-V2，零 API）

**范围**：修复 LLM fallback 执行器与 runner，不调用真实 API；新增离线 fake
transport 测试。

**执行/恢复**：
- 恢复时读取 ledger、raw response 与 normalized record，并把历史完成项纳入本轮
  summary/evaluation，不再只评价本轮发送项。
- 明确区分发送前失败、已发送后 malformed/验证拒绝、success、in_doubt、
  usage_unknown；`sent` 及之后状态永不因结果不合格自动重发（retry=0）。
- ledger 校验 `prev_hash`/`record_hash` 链；篡改时发送前 fail closed。
- 每项终态立即持久化 raw/normalized/ledger；恢复不覆盖历史证据，不重复计费。
- 发送前落实 max calls、input/output token cap、USD cap 与低峰窗口；历史 usage
  未知、in_doubt 或 provider usage 缺失时停止后续相关调用。成功后保存实际 usage，
  恢复时累计 input/output tokens 与 USD。
- runner 不再硬编码 `REAL_RUN_COMPLETE`，按 coverage 与终态输出
  `REAL_RUN_COMPLETE/PARTIAL/BLOCKED/FAILED`。

**离线验证**：`tests/test_s3_semantic_grounding_llm_execution_v2.py` 使用假 transport
覆盖上述行为，7 passed；真实 API = 0。

## 2026-09-13 修订 3.6.59：Stage 3 v4 逐字段 LLM 应用、动作回绑与证据范围绑定（S3-SEMANTIC-GROUNDING-V4，零 API）

**范围**：新增 revision `s3_semantic_grounding_v4`；byte-identical 复用 v3
冻结预测；v1/v2/v3 历史预测、manifest 与旧候选包均不覆盖。

**修复**：
- `_normalize_llm_status` 不再因一个字段 ambiguous 丢弃其他已确定字段；
  `apply_llm_grounding` 委托到 v4，按字段独立处理 validator-passed 响应。
- 匿名活动 ID 通过 pack 映射恢复为真实流程节点；动作解决后在该节点重跑受影响
  的本地检查，包括 `prohibited_action_present`，不是只改 action status。
- condition/exception 的正向 claim 必须有目标动作局部 surface 内、可反向映射的
  具体 evidence；否定/缺失 claim 需程序在完整局部 scope 内确认；constraint
  claim 需程序化数值时间比较；否则保留 unknown。
- 明确旧判定（observable 且 violation 为布尔）不被 LLM claim 覆盖。
- 候选上下文先截断证据列表、再从可见列表派生允许 evidence_ids；v4 pack
  `all_evidence_ids_visible_in_payload=true`，修复 v3 pack 中截断后仍可能 advertise
  不可见复合 ID 的同类引用问题。

**离线验收**：v4 pack 20 项；5 个构造链路 case 全部通过，覆盖 resolved+
ambiguous 字段共存、动作回绑后 prohibited 检查更新、开放 scope 的缺失 claim 仍
abstain、幻觉/越界 evidence 拒绝、截断上下文证据可达性。状态明确为
`OFFLINE_IMPLEMENTATION_EVIDENCE_NOT_LLM_PERFORMANCE`，不是真实 LLM 效果。

**证据**：`outputs/reports/s3_semantic_grounding_v4.{json,md}`、
`outputs/evidence/s3_semantic_grounding_v4/`、
`outputs/development/s3_semantic_grounding_v4/`；
`tests/test_s3_semantic_grounding_v4.py` 5 passed。

**状态**：实现链路 checkpoint；真实 API = 0。

## 2026-09-13 修订 3.6.58：Stage 3 v3 输入匿名化与评价口径修复（S3-SEMANTIC-GROUNDING-V3，零 API）

**范围**：仅新增 revision `s3_semantic_grounding_v3`，byte-identical 复用 v2
逐项确定性预测；不覆盖 v1/v2 预测、manifest、候选包或 C36。

**输入修复**：
- v2 的 `_scrub_string` 对所有字符串做整词 `control` 等子串替换，把规范文本中的
  `controller` 改成 `anonymousler`，并改写部分自然语言证据。v3 改为字段感知匿名化：
  只映射标识符和生成式 `syn_*` token；规则正文、活动标签、条件、约束、例外原文
  保持 verbatim。v2 候选包保留为历史证据。

**评价修复**：
- fallback transition 使用稳定对象键 `(item_id, side)`，variant 正例与 control
  目标字段负例分开统计由 unknown 到正确、错误、仍 unknown 的转变。
- target-paired 口径显式报告互斥两侧计数、覆盖率与分母：variant unknown 计入
  FN 但单独列 `FN_unknown`；control unknown 单独计数、不进入 decided TNR 分母；
  全体 pair success 以所有 pair 为分母，未知不当作合规预测。
- control 自洽状态只称模型诊断，没有独立全局合规标签；不报告按自身输出筛出的
  clean-unified 性能，所有 40 个 frozen control 固定保留。
- C36 缺少相同 target-paired 协议所需逐项字段，记录
  `GAP_DOCUMENTED_NOT_COMPUTED`，不拼接不可比数字。

**结果（沿用 v2 逐项预测）**：target-paired Macro-F1 **0.6737**，pair success
**21/40**；variant 24 positive / 0 observed-wrong / 16 unknown，control 28 TN /
1 FP / 11 unknown；全体 target-field unknown rate **0.3375**。v3 fallback pack
20 项，匿名化 audit 通过，规范字段零改写，模型可见 payload 无 forbidden/
generated 泄漏。

**证据**：`outputs/reports/s3_semantic_grounding_v3.{json,md}`、
`outputs/evidence/s3_semantic_grounding_v3/`、
`outputs/development/s3_semantic_grounding_v3/`；
实现与测试见 `src/bpc_hybrid/s3_semantic_grounding_v3.py`、
`scripts/run_s3_semantic_grounding_v3.py`、`tests/test_s3_semantic_grounding_v3.py`。

**状态**：第一阶段正确性 checkpoint；真实 API 仍为 0。

## CSCWD 按依赖推进的收尾 Pipeline（2026-09-12 修订）

### 目标、权威入口与完成标准

- **用户提供的当届通知（2026-09-17）**：CSCWD 2027 截稿为 **2026-10-31**，
  通知为 **2027-01-31**，会议为 **2027-05-26 至 28，Brisbane**；导师要求
  **2026-09-30 前提交完整初稿**。当届 EasyChair 新稿入口已核到；日期取自用户通知，
  官网正文独立核验仍有访问限制。投稿系统时区、摘要节点、模板和篇幅在 SEP-C1/OCT-C3
  继续核实。两项交付目标尽早完成，学校成果认定与录用/出版时间分开确认。
- **本节固定主线、实质依赖和验收标准，不安排阶段起止日或人为实验停止日**；任务满足条件即推进，
  新问题按下方修复循环处理。覆盖 3.7.0 的日历安排及旧章节中「当前下一步」的调度说法。
  既有 S1/S2/S3、PW 任务 ID、冻结资产和正式发布门禁继续有效，不因日期或写作进度自动完成。
  本次只是计划与文档更新，不执行实验、不改 prompt/schema/Gold/配置、不产生新实验结果。
- **唯一计划**为本文；**唯一实时状态**为 `docs/PROJECT_AUDIT.md`；正文在
  `paper/THESIS_DRAFT.md`，主张及证据在 `paper/CLAIM_EVIDENCE_MATRIX.md`，消融定义在
  `paper/ABLATION_MATRIX.md`。既有 run manifest 是结果依据，不再建立平行状态文档。
- **9 月初稿 DoD**：引言、相关工作、问题定义、三阶段方法、数据与评价、已有结果、
  讨论与局限、结论和参考文献均形成连贯正文；方法图、主结果表和贯穿案例可阅读。
  沿用现有中文工作稿，准备英文题名和摘要；结果缺口逐项列出任务 ID、缺失证据、依赖和下一步，
  不得用空提纲或汇报 PPT 代替初稿。必要实验尚缺时，可以交带明确缺口的导师审阅稿，
  但相应实验任务继续保持未完成，摘要不得把未取得的结果写成结论。
- **投稿稿 DoD**：完成英文全文和导师修订；核心主张均有对应可核验证据；正式结果满足
  相应门禁，开发/案例结果注明范围；正文不残留承担核心结论的 TODO。图表、引用、
  模板、页数、匿名及附件要求按当届官方要求核对。尽早达到提交就绪，持续处理反馈和修订，
  10 月 31 日为外部截止日，不作为计划中的首次整理或首次上传日。

### 任务顺序、依赖和验收

下表按主线优先顺序组织；具体子任务只等待其真实依赖，不必等待前一整包任务全部完成。
SEP/OCT 前缀保留为既有任务标识，不限定启动月份；英文转写、投稿材料和已可开展的补证也应提前推进。
实时状态只在 `PROJECT_AUDIT.md` 更新；完成标准以实际证据判断。
消融因素记号：E＝语义输入输出示例，S＝详细六要素语义规则，J＝显式 JSON/结构格式说明；
因素开关均保留共同的最低任务与输出接口，具体文本、版本、重复次数和预算在执行前固定。

| 收尾 ID | 启动条件 | 对应既有任务 | 必交内容与 Definition of Done |
|---|---|---|---|
| SEP-C0 | 用户明确主线与推进原则 | 主 Pipeline / 调度 | 本节、实时状态及派工入口一致；导师九项反馈有落实位置；文档检查通过并 Git 提交、推送。仅计划修订，不代表实验完成。 |
| SEP-C1 | 已有方法和证据可只读整理，现在开始 | PW1–PW5 / S2.7 设计 | 固定研究问题、暂定通用题名、三阶段输入输出表、r10 成功链和一个失败链；对照方法按情态分类/要素抽取/下游检查分层，核验 Sun 稿件版本及 Winter 适配边界；将已撤回/过时主张从当前写作依据中剔除并保留历史来源。将 prompt 新消融的缺口、重复次数方案和预算材料提前准备好，尚未获授权不调用。产出：正文方法与评价章节的可审阅版本、主张矩阵和消融矩阵对应条目。 |
| SEP-C2 | 两方法执行/冻结合同已适配；对应比较口径、输入与适用授权落实 | S2.7 / S2.12 / S2.13 / PW2、PW5、PW7 | 补必要的前人比较：Winter 原生共同子任务或下游比较、Sun 重建与本文 Direct-LLM；保持输入/评价可比，未支持字段单列。取消 Rules+LLM 全部后续实验及 S2.12 F-1/F-2/F-3 的 27 次调用；S2.12 只比较 Rules-Only 与 Direct-LLM，剩余 Direct 36 次和 GDPR Direct 74 次按各自合同推进，合计 110 次。先锁预测再评价并保存 manifest/事件；两方法 DoD 满足后才推进 S2.13，不等待被取消组，不绕过其余门禁。结果或精确阻塞及时回写正文。 |
| SEP-C3 | targeted refinement 已收口；新实验仍需适用授权 | S2.9 / AB 与 prompt 消融 / PW3、PW5、PW7 | 已完成 E/S/J 冗余诊断、modular_v1 四臂真实退回、000/001/010/100 缺失格增量执行（八格各一次；非同批、无重复；不足以作稳定主效应/交互）、targeted refinement A/B/C/D 一次 600-call 开发运行、v2 recovery semantic review NO-GO；B 仅研究参照，v6 仍默认，R_A 方向性收益，R_C recall/FP 权衡，temporal-only/T/G/TG 不派发。未完成：固定原始响应后处理归因（仅本地分支 9b50729 覆盖旧 v6+111，其余 arms 未覆盖；adapter/canonicalizer/validator 子步骤贡献不可独立分离）、重复运行不确定性，以及 SEP-C1-B 计划中的同批 8x150x2 主设计；不得用旧不相容臂拼表，整个 SEP-C3 不标完成。 |
| SEP-C4 | 案例与开发诊断按已有证据推进；正式运行待对应上游门禁 | S3.4–S3.10 / S3.9-EXT / PW8 | 在实质依赖和授权满足后推进正式 Oracle/端到端；固定流程与检查器，比较 Rules-Only/Direct-LLM/人工规则来源，分别定位抽取、适配、映射和检查损失。落实目标规范/活动/原图或变体的评价范围，未确认范围保留为诊断。四类扩展逐类说明适用性、可观测证据和失败原因，已知缺陷臂不可支持方法有效性。产出：下游对照表、成功/失败案例和能力边界；发现影响结论的问题，进入对应修复子任务。 |
| SEP-C5 | 章节持续累积，已有内容足以形成连贯全文即整合 | PW1–PW9 | 汇总完整正文 v1；统一术语、方法图、表格口径、引用、优点与负结果；英文题名/摘要按已有证据形成。逐条结果句可回指 manifest 和主张矩阵；阻塞项明确列为缺口，不延误可完成章节。尽早形成可从头读到尾的初稿，并随补证和修复持续更新。 |
| SEP-C6 | 全文 v1 可审阅 | PW9 / 导师初稿交付 | 检查论证、数字、图表、引用和文件可读性，准备导师审阅版本及简短待决清单；完成即向用户交付，最晚 9 月 30 日前提供可送导师的完整初稿。交稿由用户发送，任务不自动联系导师。 |
| OCT-C1 | 收到导师反馈或发现影响主张的具体问题 | PW9 / 必要补证任务 | 随反馈更新必改清单，优先补影响核心主张的证据缺口；同步转写英文；核验官方投稿要求与提前节点。新增方向先判断是否解决当前必要缺口及其依赖、成本，不因月份提前或推迟。 |
| OCT-C2 | 核心缺口明确，相应证据/授权可用 | 未完成 S2/S3 核心任务 / PW7–PW9 | 完成核心补证和英文全文；对无证据主张作限缩或移除，明确记录，不伪造正式任务完成。方法与证据通过对应复核后形成稳定版本；后续发现问题只重开受影响部分，按实际影响验证并同步相关表述。 |
| OCT-C3 | 相关正文与证据已可复核；格式和引用检查可提前 | PW9 / 投稿准备 | 导师复核、英文表述、图表与参考文献定稿；按官方模板核对页数及提交材料。必要正式检查依适用门禁完成；全量测试仍须本轮明确授权，不能因终稿临近自动启动。 |
| OCT-C4 | 稿件和投稿材料已就绪 | 最终交付 | 完成即交付投稿就绪文件，继续处理最后修订；作者信息和最终提交由用户确认。尽早准备并提交，10 月 31 日为最晚外部截止，不等待预设上传日期。 |

### 范围与取舍固定

1. **九月必须交代清楚**：三阶段 I/O、前人对照、prompt 组合与冗余分析、后处理职责、
   已有方法差异、四类扩展边界、端到端证据及其缺口。论文写作跟随每个批次，不等全部实验结束。
2. **新增性能主张须证据支持**：Stage 1 沿用已冻结组件；Rules+LLM-Repair 只保留历史记录，
   不再安排任何实验或新增对照。四类扩展的逐类定义与诊断必须完成，但不把「四类全部高分」作为交初稿的条件。
   新增 Stage 1 LLM、Stage 3 全新 LLM 判断器、大规模模型比较及新数据集，不自动加入核心收尾；
   是否纳入按已诊断问题、核心主张需要和成本判断，不按月份决定，不撤销已有具体任务授权。
   Sleimi 等新增抽取基线先做文献和接口适配评估，必要对照在条件满足后尽早开展。
3. **旧结果与新候选分离**：已冻结方法、prompt、输入、Gold、原始响应与 manifest 保留。
   先以原配方完成适用的既有授权批次；精简 prompt 使用独立后继版本和预算，不覆盖正式基线，
   不因查看过 EStG-150 或开发面板而把新结果称作未见测试。新模型/新接口/新模板条件改变时，
   旧四组结果只有逐项证明兼容才能复用；八组合的逐组输入和计费须事前列清。
4. **最新取消决定优先**：旧 137 次中的 S2.12 修复 27 次已取消，不得再使用其历史授权。
   剩余 110 次 Direct 调用仍需适用合同、精确载荷、绑定版本、余额、时段及真实账本检查；
   当前外部发送审批阻塞未解除，不擅自扩展或重发。Direct prompt 组合仍需独立预算与授权；
   本节不构成 API 授权，不再提出规则＋LLM 修复实验。
5. **先证实错误，再决定修改**：区分抽取错、适配损失、映射失败、流程未表达、评价范围未定。
   正确性缺陷修复优先于调阈值；不得用 Gold 回填推断或在同一开发面板无限试参。
   对照/变体、unknown/not_applicable、机器报警/参考问题对应分别报告。
6. **验收看真实交付**：完整方法与消融不以正增益为验收条件；负结果、无效模块和失败案例均可入稿，
   但实验未执行不能标完成，未通过门禁不能称正式，源码测试通过不能代替实验效果。

### 导师九项反馈的落实位置

| 反馈 | 主任务 | 必须出现在初稿中的内容 |
|---|---|---|
| 1 前人比较 | SEP-C1、SEP-C2 | Sun/Winter 比较层次、共同任务、表示适配、公平对照表 |
| 2 组合消融；7 冗余与精简 | SEP-C1、SEP-C3 | E/S/J 八组合、字段权衡、替代/交互分析、精简保留或拒绝的依据 |
| 3 每阶段输入输出 | SEP-C1、SEP-C4 | 三阶段 I/O 表、同一实际案例的完整证据链及失败链 |
| 4 通用题名 | SEP-C1、SEP-C5 | 使用「自然语言合规需求」等通用概念，明确设计时和数据覆盖范围 |
| 5 突出方法差异 | SEP-C1–SEP-C5 | 每项改动的问题、相对前人的机制差别、实测效果及边界 |
| 6 人工判读启发 prompt | SEP-C3 | 规范主干、适用性、作用范围、关系、证据与不确定性的明确处理 |
| 8 三类/四类范围与 LLM 可行性 | SEP-C4 | 文献实际范围、四类语义定义、流程可观测性、原因诊断；新 LLM 后端只作有边界的方案 |
| 9 后处理与人工答案 | SEP-C3、SEP-C4 | 生成前结构定义、生成后机械校验、独立人工 Gold 评价三者区分 |

### 执行节奏、阻塞与交接

- 实验一次只推进一个最小子任务，论文整理可交错进行；不自动创建新任务或启用后台定时执行。
  每次开始从 `PROJECT_AUDIT.md` 的「下一步」恢复，读取实际文件状态，不重复已完成批次。
- **完成即推进**：满足验收后立即进入下一项可执行工作，不等待预定日期、月份或不相关任务。
  固定总体方法主线与评价契约；局部问题逐项解决，不能把「固定 pipeline」理解为禁止修复。
- **问题处理循环**：保存失败证据 → 定位根因及影响 → 提出最小修复 → 完成相关验证或必要的已授权实验
  → 根据证据保留、修订或拒绝方案 → 更新论文与状态 → Git checkpoint → 继续推进。
  修复项归入原任务，在 `PROJECT_AUDIT.md` 记录现象、证据、假设、影响范围和验收标准，
  不另建路线文件；优先解决正确性、公平比较和核心主张缺口。新问题只重开受影响任务和证据，复用仍有效结果。
- 每次交付简报包含：完成项、证据/验证范围、下一步、真实阻塞、Git commit/分支/推送结果。
  一个连贯子任务完成就进行 scoped Git checkpoint，不积累到月底统一备份。
- 阻塞出现当天记录具体缺项和受影响主张；仍推进不依赖该项的正文或离线准备。
  不反复询问已获授权，不把等待时间视为授权，也不以缩减论文主张来伪称原实验 DoD 完成。
- 未完成必要实验持续跟进，原状态保持未完成；已有正文持续整合和交付，补证到位立即更新。
  不预设中途实验停工日，也不把所有问题推到初稿之后；尽早形成可审阅版本以尽早暴露问题。
- 文档/排版按内容和文件检查验收；代码按两级 AGENTS.md 与 AI_CHANGE_PROTOCOL 做快速检查和具名相关测试。
  提交、推送、交稿本身不触发完整代码测试。本次计划更新使用 scoped commit 作为记录。

## 2026-09-12 修订 3.6.57：Stage 3 四类扩展评价协议修正、deterministic v2 冻结与 LLM fallback real-run 预检（S3-SEMANTIC-GROUNDING-V2，零 API）

**范围**：仅新增 revision `s3_semantic_grounding_v2`；不覆盖 C36、v1、33 条人工 Gold、frozen panel、Sun scorer 或旧证据。v1 C40 保留为历史。

**评价修正**：
- 真正 collision 改为 composite input identity：model-visible canonical Rule Input hash + canonical Process Input hash + different expected labels。修正后 true collision = **9 组 / 20 个 side objects**；旧 BPMN-only v1 audit 为 7 组 / 28 variants，忽略 Rule Input 且只算 variant 侧，属于过度估计。
- control 不再默认全局 none。由四个 structural check 离线计算 `verified_compliant / violated_other_field / unknown`；本数据为 **5 / 22 / 13**。
- 主口径改为 **target-paired causal evaluation**（每对只评 mutation target field）；统一 80 对象降级为 secondary diagnostic；新增 clean unified（40 variants + verified controls）。

**Deterministic v2 结果**：target-paired Macro-F1 **0.6737**，prohibited/condition/constraint/exception F1 = **1.0000 / 0.9000 / 0.3333 / 0.4615**；target control FP **0.0250**；pair success **0.5250**；unknown rate **0.3375**。Variant binary Macro-F1 **0.5619**。clean unified 5-class Macro-F1 **0.6709**；legacy 80 对象 5-class Macro-F1 **0.4246**（仅 continuity diagnostic）。两次全量 deterministic 运行 predictions byte-identical。

**Fallback subset**：`llm_fallback_candidate_pack_v1.json` 冻结 **20 条**（7 variant + 13 control），只含 deterministic final abstention；explicit compliant/violation 不送 LLM。

**LLM real-run 准备**：request builder、canonical payload/hash、strict JSON + evidence-ID validator、response parser、fail-closed policy、retry=0、token/cost estimator、budget cap、append-only ledger、resume/no-double-send、raw/normalized storage、evaluator/ablation wiring 均完成并通过 mock/offline full execution（20/20）。Preflight：20 calls、62,333 estimated input tokens、10,240 output-token cap、USD cap 0.18 / RMB 1.30、off-peak only；request set hash `1ac203ec1b2bc4e4a4ac3b057788abe79b9fbf143b981ea635dc238925bdaf04`，pack hash `512b06b8f847caac98e53059570e5473017cb8da2a9620ae394fd9fd02d5102e`。仓库中 0 个匹配 scope 的有效授权；94 个非匹配授权/合同被拒绝复用。真实 API calls = 0，Arm C = **IMPLEMENTED_READY_FOR_AUTHORIZATION**。

**证据**：`outputs/reports/s3_semantic_grounding_v2.{json,md}`、`..._arm_comparison.{json,md}`、`..._llm_preflight.json`、`..._llm_authorization_request.{json,md}`、`..._llm_mock_execution.json`；`outputs/evidence/s3_semantic_grounding_v2/`。

## 2026-09-12 修订 3.6.56：Stage 3 四类扩展的 deterministic-first semantic grounding 与 fail-closed LLM fallback 实现（S3-SEMANTIC-GROUNDING-V1，零 API）

**范围**：development-only 受控面板 40 variant + 40 control；仅新增 revision `s3_semantic_grounding_v1`，不覆盖 `s3_formula_repair_v2`、33 条人工 Gold、frozen GDPR-7 membership、原三类结果或已有 panel/synthetic 数据。

**实现**：
- `src/bpc_hybrid/s3_semantic_grounding_v1.py`：Top-K action grounding（semantic similarity + label normalization + content-token coverage + lane/pool ownership + margin，状态 `resolved/ambiguous/unresolved`）；condition/constraint/exception 改为有限、action-anchored 的局部 BPMN 子图检查；区分 observable absence 与 unobservable，任何 ambiguous/unresolved 默认 abstain；显式 numeric time-limit contradiction 逻辑保留并单测覆盖；抽象约束（without undue delay / without hindrance / clear language 等）不伪造确定性判断。
- `scripts/run_s3_semantic_grounding_v1.py`：新 revision runner，写 `outputs/development/s3_semantic_grounding_v1/`、`outputs/evidence/s3_semantic_grounding_v1/`、`outputs/reports/s3_semantic_grounding_v1.{json,md}`；输入/config/code/sample count/evaluator version 全部 hash 绑定；运行前验证 C36 original-three 与 Sun scorer 冻结哈希。
- `configs/stage3_semantic_grounding_v1.json`、`tests/test_s3_semantic_grounding_v1.py`（9 项：原三类回归绑定、Gold-blind、no-metadata-leakage view、condition/exception/constraint 行为、LLM strict JSON fail-closed、deterministic replay）。
- LLM fallback：strict JSON schema + evidence-ID validator + fail-closed unknown；mock/offline plumbing 已测试，**未调用真实 API**，状态 `IMPLEMENTED_NOT_REAL_RUN`。

**当前 development 结果**（reference/winter backend；详细表见 report）：
- unified variant: 4-type Macro-F1 **0.5886**、exact **0.5750**、unobservable **7**；C36 baseline 0.4738 / 0.4250 / 18。
- per-type binary checks: Macro-F1 **0.5619**；target-field diagnostic Macro-F1 **0.6737**，control target FP rate **0.025**。
- paired 80 objects: 5-class Macro-F1 **0.4246**、control any-type FP rate **0.5500**、paired accuracy **0.1250**；该 paired 数字的下限受 variant BPMN collision 约束，必须与 identifiability audit 同读。
- **identifiability audit**: 7 collision groups / 28 variants are byte-identical across expected types; single-label unified accuracy is therefore structurally bounded and is not the primary per-type evidence.
- 未运行真实 LLM, fallback metrics 只记录 eligible object count 26, 不填假 resolved/failed 数。

**State**: verified development result / not formal Oracle; real API remains blocked pending explicit user authorization.

## 2026-09-11 修订 3.6.53：四类扩展的定位接线修复与证据范围臂（S3-EXTENDED-EVIDENCE-SCOPE，零 API）

本批只做用户指定的两个新臂（W/H），各跑一次固定面板；旧 A/B/C、Winter 等按哈希只读复用，未重跑。
范围声明：面板已被反复用于开发，全部结果只能称 **development regression**，不是独立验证、不是正式 Oracle、
也不是真实法律合规性能。

- **R1–R6 逐项核实**（结论写入 `diagnostics.json.findings`）：
  1. **R1 定位接线（已证实，机制与旧描述不同）**：runner 的 `score_side()` 用
     `localize().matched_activity_id` 建候选面，检查器内部却调 `resolve_action()`。只读重放 C 臂自身 scorer
     于 80 个单侧实例：**45 个单侧实例（变体 19 + 对照 26）候选面以 `None` 建成**，而检查消费了回退活动。
     旧描述需要修正：`surface_activity_id` 只对 constraint 面填充，故 14+14 是**检查引用计数**，不是 28 个
     独立流程；且回退只在 v3 未满足匹配时发生，不存在"面绑 A、检查用 B"的两活动冲突。B 臂原生没有
     `matched_activity_id` 字段属构造差异，不是绑定错误。
  2. **R2 全图候选（已证实）**：传入活动 ID 对 condition/constraint/exception 候选**增加 0 条**；
     `syn_v2_required_condition_01` 上 25 条 constraint、3 条 exception 全部与目标活动无关，condition 面为空。
     仅 `ConstraintSurface.bound_texts` 的数值比较原本就绑定活动。
  3. **R3 缺证据与反证混用（已证实）**：`_missing_evidence` 用 `1-max_similarity`；空候选直接 unknown，
     未区分"明确矛盾 / 完整范围内确认缺失 / 文本无法表达 / 范围信息不足"。H 实现四值判定 + 分别记录
     `applicability` 与 `evidence_status`。
  4. **R4 上游规则与面板范围（属输入问题，不是打分缺陷）**：`syn_v2_required_condition_05` 的规则动作是
     "have the obligation to erase personal data …"，生成器把条件挂在其 `mutation_config.target_activity_id`
     所指活动上；`syn_v2_exception_not_handled_04` 的 "Paragraph 1 shall not apply…" 被冻结抽取器读成
     prohibition(action=apply) 且同时读成 exception。本批**不修订冻结抽取**，`target_activity_id` 自始至终
     只作生成器元数据、未当答案键使用。
  5. **R5 对照范围（评价契约问题，已证实）**：生成器只补目标字段证据，"相对 none 报警"不等于已证实法律误报；
     已作为独立诊断类别记录，未删除/重标任何实例。
  6. **R6 诊断字段（已证实并修复）**：旧 `comparison_strings` 按违规类型名查 sentence 字段，condition/
     constraint/exception 被记成空串。W/H 改用"元素→字段"映射并记录检查实际消费的文本，
     `comparison_strings_check.checked=640, mismatches=0`。**这是诊断修复，不改变任何预测。**
- **两个新臂的实测（历史五分类口径，160 个新对象预测；成对=变体正确且对照明确合规）**：

  | 臂 | 变体正确 | 错类 | 明确合规 | unknown | Macro-F1 | 对照报警 | 对照 none | 对照 unknown | 成对 |
  |---|---|---|---|---|---|---|---|---|---|
  | C（旧，适配层复算一致） | 18 | 8 | 0 | 14 | 0.4896 | 14 | 11 | 15 | **7** |
  | W（只修接线） | **19** | 9 | 0 | 12 | **0.5234** | 20 | 7 | 13 | 6 |
  | H（W+证据范围与四值判定） | 15 | 8 | 0 | 17 | 0.3517 | 19 | 5 | 16 | 5 |

  分类别 F1（变体）：C 0.9524/0.1429/0.5556/0.3077，W 0.9524/**0.3333**/0.5/0.3077，
  H 0.9524/0.4545/**0.0**/**0.0**（prohibited/condition/constraint/exception）。
  合并 80 准确率：C 0.3625、W **0.3250（26/80）**、H 0.2500（20/80）；成对只算"变体正确且对照明确合规"。
- **2026-09-11 修订 3.6.54 原位修正（原叙述有误；2026-09-11 修订 3.6.55 验收注记再次更正）**：
  1. **撤回"W 有 5 个 prohibited 变体退步"**：按 accounting 口径重算，C 与 W 在**全部 10 个 prohibited
     变体上预测完全相同**，一个 prohibited 变体都没有变。旧叙述给出的"把 C 的 per-type 门判定与 W 的
     最终标签混在一起比"这一**确定归因无留存证据支持，已在 3.6.55 验收注记中撤回**；保留的可核事实是
     "不存在禁止类退步"。W 相对 C 的真实差异为 **4 个变体变化 + 6 个对照变化**：
     变体侧 4 例——`constraint_violated_05` 正确→错类、`required_condition_05` 错类→正确、
     `required_condition_10` unknown→正确、`exception_not_handled_05` unknown→错类，
     **正确数净增 1**（18→19）、Macro-F1 0.4896→0.5234 全部来自这 4 例；
     对照侧另有 6 例——`constraint_violated_05`、`exception_not_handled_07/08/09/10`、`prohibited_action_10`
     均由 none 变为 `required_condition_not_enforced`，**总对照报警 14→20，其中 condition 报警 3→9**。
     接线修复的直接作用是 condition 目标检查 TP 1→3（condition 候选面在多数模型里为空，旧代码传入的
     `mapped_id=None` 与检查实际使用的回退活动不一致）。
  2. **unknown 与 not_applicable 不再混为一谈**：最终 unknown 是聚合弃权；目标检查层面的不可判定来自
     可观测性；`not_applicable` 表示**规则本身没有该元素**，是第三种状态。H 的 not_applicable 仅出现在
     目标切片之外的行上（cross-type 计数：condition 7、constraint 20、exception 24；每类目标切片内为 0）。
  3. **撤回"condition TP 3→5 证明机制改善"**：同一 H condition 检查另有 **27 条
     `unconditional_bypass_branch` 记录（12 个变体 + 15 个对照）**，而该判据只证明"被到达网关的兄弟分支没有条件"，
     **没有证明旁支能绕过条件回到目标活动**，故不构成绕过证明。3.6.55 验收注记：这 27 条**包含** condition
     目标切片内的 **5 个条件目标命中**（`required_condition_01/03/04/08/09`）；**验收方对哈希匹配 BPMN 的
     静态遍历显示，对应旁支均无法到达目标活动**——解析原图做静态核查不等于重新推断（本批未重跑检查器、
     未改任何预测）；对应测试原先的预期（有旁支即 violated）也是错的。
     H 保留为**存在已知实现缺陷的开发结果，方法验收不通过**。
  4. **运行次数分列（运行量来源＝执行回执）**：按执行回执，推断**尝试 3 次**、成功写出预测 **2 次**，
     **两次成功运行合计 320 个对象**（2×160）；**失败尝试的计算量未知**，故**总量至少 320**；
     最终保留 **160 行**（每臂各一次，80 行/臂）。"两次成功的预测完全相同"**无留存证据可独立核实**：
     第一次成功的产物未保留，磁盘上只有第二次。
- **H 不是靠多判 unknown 减少报警换来改善**：报警 20→19（−1）、对照明确合规 7→5（−2）、
  对照 unknown 13→16（+3）、变体正确 19→15（−4）、成对 6→5、Macro-F1 0.5234→0.3517。
  H 的 constraint/exception 目标检查在其**自己的 10 个目标变体上全部不可判定**（`variant_true` 与
  `variant_false` 均为 0），即作用域收紧后这两类在本面板失去可判定性；condition 目标检查在切片内为
  5 真 / 5 不可判定，但**对照侧同样 5 真**，成对成功 0（该 5 真包含在上条第 3 项所述的 27 条
  `unconditional_bypass_branch` 记录内，验收方的静态遍历否定了其绕过结论，故不构成绕过证明）。
  结论：**H 相对 W 是退步**，其证据作用域改造在本面板没有转化为更好的判定，如实保留该结果。
- 产物 `outputs/development/s3_extended_evidence_scope_v1/{plan.json,predictions.jsonl,metrics.json,diagnostics.json,manifest.json}`；
  复核 `python formal_experiment/scripts/run_s3_extended_evidence_scope_v1.py --check`（哈希绑定）与 `--replay`
  （仅从已存行复算指标，不重做推断）；测试 `tests/test_s3_extended_evidence_scope_v1.py`（22 项，含 10 项
  非面板小流程行为验证）。
- **离线验收复算（2026-09-11 修订 3.6.54，零推断）**：
  `scripts/recompute_s3_extended_acceptance_v1.py` 只读已存 JSON/JSONL 重算全部主表与目标字段视图，
  产物 `outputs/development/s3_extended_acceptance_recompute_v1/{metrics.json,diagnostics.json,manifest.json}`；
  复核 `--check`；测试 `tests/test_s3_extended_acceptance_recompute_v1.py`（18 项，含手工可算小表）。
  复算与 `s3_extended_evidence_scope_v1/metrics.json` 及 `s3_extended_prediction_accounting_v1/metrics.json`
  **逐项一致（differences = 0）**：主表数字本身没错，错的是此前的解释与目标字段视图。
  目标字段视图现按"每类 10 个目标变体 / 10 个目标对照"分别给出 真/假/不可判定/不适用，并单列
  不适用计数；正例判假即漏检，对照判真才是目标字段报警，TN 只来自目标对照。**未报告任何逐类 P/R/F1**：
  每类只有 10 个标注正例，不可判定既非正也非负，其他类型的变体不是人工确认的负例。
- **2026-09-11 修订 3.6.55：验收注记（原位更正，零推断、零运行）**：
  1. **停止引用** acceptance metrics 中的 `variant_outcome_by_target_type`：该字段在按目标类型循环时被逐次
     覆盖，每个黄金目标类型只保留**最后一个实例**的判定，因此不是分布统计。主表、四类目标分区与成对结果
     已由验收方**独立核对通过**，**不受该字段影响**。
  2. **旧统计错误的根因更正**：旧目标字段视图三项已核实的成因是 ①**正例 False 被误记为 FP**
     （W 的 `exception_not_handled_04` 正例判定为 False 即漏检，旧视图记成 `fp=1`）；
     ②**目标对照报警漏计**（prohibited 的 3 个目标对照报警在旧视图里记成 `tn=3`，未作为报警呈现）；
     ③**TN 来源错误**（旧 `tn` 不取自目标对照：condition 的 7 个目标对照阴性旧记为 `tn=0`，
     constraint 的 `tn=2` 在目标对照分区里没有对应项）。
  3. **撤回**旧叙述对"禁止类退步"给出的"由跨视图混比产生"这一**确定归因**：留存证据不足以断定旧数字的
     来源，本次只保留可核事实（accounting 口径下 C 与 W 的 10 个 prohibited 变体预测完全相同）。
  4. 本注记只改本文、`docs/PROJECT_AUDIT.md` 与 `docs/EXPERIMENT_LOG.md` 的更正段落；未改任何代码、
     JSON、预测或 manifest，未重跑检查器，历史事件与旧产物逐字节保留；**旧产物中的上述错误说明以本注记为准**。
- **边界**：旧预测/metrics/manifest 与绑定实现逐字节保留，`s3_extended_prediction_accounting_v1.py` 未改，
  新臂经薄适配层注册并验证与最新修正后的 A/B/C 数字一致；未搜索阈值、未新增白名单/同义词/ID 特判、
  未读 `.env`、未调用 LLM/API。

## 2026-09-11 修订 3.6.52：四类扩展最终预测与统计口径统一（S3-EXTENDED-ACCOUNTING，离线复算）

修复 3.6.51 的统计混用：`control_partition` 为 A/B 对照额外施加 C 的比较门，
而成对/合并评价又用冻结旧规则重新判断对照（包括 C）。因此原表出现 B 对照正确仅 7、
成对正确却 11 的矛盾。**3.6.51 的对照、成对与合并统计以本节为准；变体预测和四类 F1 不变。**

本批从已保存的 120 行分数离线重建 240 个实例的最终预测：A/B 两侧均使用其声明的冻结
聚合规则，C 两侧均使用其声明的比较门。每个实例只有一个最终标签；计数、P/R/F1、
混淆矩阵、成对成功均只消费该标签，评价阶段不再次决定合规或弃权。`none` 仅代表该方法
对当前受控检查的输出，不等于整个流程法律合规；本批不改变已有聚合策略或增加新方法。

| 臂 | 变体正确/错类/判合规/unknown | 变体四类 Macro-F1 | 对照误报/判合规/unknown | 成对正确 | 合并80准确率 | 合并五类 Macro-F1 |
|---|---|---|---|---|---|---|
| A：v3 内部0.4 | 22/13/4/1 | 0.5690 | 24/16/0 | 11/40 | 0.4750 | 0.4578 |
| B：原路径+空白折叠 | 19/9/2/10 | 0.5233 | 20/14/6 | 11/40 | 0.4125 | 0.4316 |
| C：双层配置+比较门 | 18/8/0/14 | 0.4896 | 14/11/15 | **7/40** | **0.3625** | **0.4079** |

撤回原“C 成对 11→13”的提升解释：新口径下 C 为 7/40，不能以旧 13/40 宣称优势。
三臂各 40 对、全部实例保留，unknown 不算正确；成对正确数不超过任一侧正确数，合并
准确率等于两侧正确数之和除以 80。旧预测、metrics、manifest、输入、检查器、阈值均未改；
新增推断/LLM/API 调用 0。当前开发批次收口，不新增优化或正式 Oracle 声明。

产物仅 `outputs/development/s3_extended_prediction_accounting_v1/` 下
`final_predictions.jsonl`、`metrics.json`、`manifest.json`；入口
`python scripts/reconcile_s3_extended_results_v1.py --check` 为纯离线绑定与复算核验。

## 2026-09-11 修订 3.6.51：S3 扩展实验的限定返修——执行错误纠正与三臂对照（S3-EXTENDED-REPAIR-V2，零 API）

> **统计更正（3.6.52）**：本节 B 对照数量、C 成对/五类指标曾混用两种聚合规则。
> 相关汇总与“成对11→13”的解释由 3.6.52 替代；原始分数与变体预测保留。

**3.6.50 的四条结论被本批撤回**，原因是那批的"v3+0.4 诊断臂"从未真正把 0.4 传给 v3：脚本从 Sun 配置读
`gamma=0.8` 构造 `EvidenceChecksV3`，`ACTION_GAMMA=0.4` 只到了外层适配器；产物自身就同时记录
`action_mapping_gamma=0.4` 与 `v3_thresholds.gamma=0.8`。因此"门槛在 v3 路径中不起作用""门槛解释零个失败"
"30 个失败都由结构拒绝造成""误报挤掉两个正确样本""非 None 即检出违规""修复版无指标超过原路径"
以及未经对照证明的"结构匹配贡献"全部撤回或改写（逐条替代见产物 `diagnostics.json.previous_claims`）。

本批只读复用旧 Winter / Sun / 旧 v3 / 上一轮修复版，新增**一个后继模块、一个统一脚本、一个测试文件、
一个新输出目录**，三个臂各跑一次 80 实例（零 API，无阈值搜索，无按样本选路，无新词表）：

| 臂 | 匹配路径 | v3 内部 gamma | 标签回退 gamma | gamma_ext |
|---|---|---|---|---|
| A | v3 结构匹配（**真实**传 0.4） | 0.4 | 0.4 | 0.5 |
| B | 冻结原始标签 argmax，关闭 v3，双侧空白折叠 | — | 0.4 | 0.5 |
| C | v3 匹配 + 无强制解析 + 比较门（**双层配置**） | 0.8 | 0.4 | 0.5 |

- **推断前断言**：脚本在打分前断言"声明 gamma == 实例 `EvidenceChecksV3.gamma`"，并断言 tau/theta 仍为
  冻结 0.8；错配立即失败。`plan.json` 在任何打分之前写盘并记录实现哈希，逐行 `thresholds` 记录
  `v3_internal_gamma` / `label_fallback_gamma` / `gamma_ext` / `configuration_levels`。
- **真正修好的执行错误**：①门限传递（A 臂 0.4 真的进入 v3 实例）；②空白不对称——上一轮只折叠规则动作、
  不折叠活动标签，而冻结 GDPR-7 里存在尾部换行的标签（`'Communicate the rectification\n'`），实测
  `constraint_violated_03` 0.282807→0.483290、`required_condition_10` 0.266066→0.466753，0.4 落在两者之间，
  所以那 2 个"新增命中"其实由换行决定；③解析歧义——v3 返回 `undetermined` 时不再用 argmax 硬选活动，
  标签回退在最高分并列于不同节点时也不选，需要唯一活动的检查一律保持不可判断；④新增**比较门**：只有当
  condition/constraint/exception 至少有一项真正做过比较时，聚合答案才允许是"明确合规"，否则一律弃权
  （禁止动作存在性检查单独说明：它只回答"该动作是否出现在流程里"，不承载合规结论）。
- **三个因果问题的实测答案**（完整差异清单在 `diagnostics.json.differences_vs_reference_cells`）：
  1. **把 v3 内部阈值真正改成 0.4**：40 行中 **32 行决策改变**、**25 行最终预测改变**、21 行"金标类型"
     由不可判断变为可判断，31 行对照侧分数改变。A 臂变体 **22 正确 / 13 错类 / 4 明确合规 / 1 unknown**，
     Macro-F1 **0.5690**（旧 v3 0.2273、原路径+0.4 0.4738）；对照误报 **24**（旧 v3 8、原路径+0.4 20），
     即分数提升伴随更多对照误报，两者都如实报告。
  2. **只加空白规范化、不用 v3**：B 臂与冻结 Winter 臂 **35/40 行决策完全相同**，5 行不同，其中仅 **2 行
     预测翻转**，恰为 `required_condition_10` 与 `constraint_violated_03`（Winter 均弃权 → B 正确）；另外
     3 行只有分数/对照侧变化。**结论：这 2 个新增命中完全由空白规范化解释，与结构匹配无关**；同时该规范化
     也改变了 3 个对照侧分数（B 对照误报 20 = Winter 20）。
  3. **歧义修复改变了什么**：本面板 **0 行**触发并列或 `undetermined`，因此"禁止强制解析/禁止任选并列"
     这条规则在本面板没有生效，**尚不能分离**它对结果的影响；C 臂相对上一轮修复版的 12 行差异实际来自
     "双侧折叠 + 比较门"。改动方向：2 行由错误类型改为正确类型（`required_condition_05`、
     `constraint_violated_05`）、2 行由错误类型改为弃权（`required_condition_10`、`exception_not_handled_05`）、
     2 行由"上一轮误报的明确合规"改为弃权（`exception_not_handled_02/03`）；对照误报 20→**14**、成对正确
     11→**13**，但变体正确 19→**18**（净退步 1）。**比较门是把"未比较就宣布合规"的错误答案改掉，不是
     为了提高分数**。
- **同口径最终表**（互斥计数守恒；"目标类型不可观测"单独统计，不混入四分类）：

  | 臂 | A 正确 | A 错类 | A 明确合规 | A unknown | 和 | 目标类型不可观测 | A Macro-F1 | B 误报 | B 明确合规 | B unknown | C 成对 | D 五分类 acc / Macro-F1 |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|
  | A（v3 真 0.4） | **22** | 13 | 4 | 1 | 40 | 9 | **0.5690** | 24 | 11 | 5 | 11 | 0.4750 / 0.4578 |
  | B（原路径+折叠） | 19 | 9 | 2 | 10 | 40 | 16 | 0.5233 | 20 | 7 | 13 | 11 | 0.4125 / 0.4316 |
  | C（后继+比较门） | 18 | 8 | 0 | 14 | 40 | 18 | 0.4896 | **14** | 11 | 15 | **13** | 0.4625 / 0.4504 |

  对照 A/B 两臂沿用了上一轮的脆弱聚合规则（只要某类型可观测且无违规就答"明确合规"）：若按上一轮口径，
  它们会把 5 / 7 个弃权冒充成"明确合规"；C 臂的比较门把这类答案改为弃权。
- **边界**：development-only 受控面板；旧预测 / metrics / manifest 及其绑定实现逐字节保留，未重绑旧 manifest；
  旧"v3+0.4"批次在新记录中标记为 **"外层记录 0.4、实际 v3 仍 0.8，不能支持阈值因果结论"**；四类仍是项目
  自定义扩展，不得改称"我们的方法"或声称 Winter/Sun 原生能力。
- 产物：`outputs/development/s3_extended_repair_v2_v1/{plan.json,predictions.jsonl,metrics.json,diagnostics.json,manifest.json}`；
  复核入口 `python formal_experiment/scripts/run_s3_extended_repair_v2_v1.py --check`；测试
  `tests/test_s3_extended_repair_v2_v1.py`（25 项，含三项不来自面板的行为验证）。

## 2026-09-11 修订 3.6.50：四类扩展"Winter 为何高于 v3"的同条件归因与修复（S3-EXTENDED-GAP，零 API）

> **2026-09-11 修订 3.6.51 撤回声明**：本修订的 `v3+0.4` 诊断臂从未把 0.4 传给 `EvidenceChecksV3`
> （脚本从 Sun 配置读 0.8），因此本节下列结论作废，只保留为历史记录：
> "关键结论 1（门槛不是原因）"、"v3+0.4 与 v3+0.8 逐条预测完全相同"、"门槛差异解释 0 个失败"、
> "同样是 0.4 时结构匹配在伤害定位"中关于 0.4 的部分、"30 个失败都由结构拒绝造成"、
> "误报挤掉两个正确样本"、"修复臂在 Winter 正确的全部 17 个实例上仍然正确"中关于 A2 的因果表述、
> "修复臂没有任何指标超过原路径"。D1/D2/D3 三个缺陷的**代码与逐项产物证据**仍然成立，但 D1 的判别样例
> 需要更换（1.0000 与 0.5040 都高于 0.5，不能证明跨越门槛）；替代证据见 3.6.51。

3.6.49 把 v3 接进四类面板后只交付了"新臂分数更低 + 瓶颈在动作定位"的结论。本轮按要求先做**同条件分离**，
再针对**已证实**的缺陷修改并复评。复用旧臂，不重跑 Winter/Sun/BM25/TF-IDF。

- **四格对照（同一面板、同一评价器、同一指标模块）**：`orig+0.4`（重新推导，与冻结 Winter 臂在全部
  决策字段上逐项相同）、`orig+0.8`（冻结 Sun 臂）、`v3+0.8`（既有 v3 臂）、`v3+0.4`（新增诊断臂）。
  新增 **`v3+0.4` 诊断臂**：v3 匹配路径 + 迁移 Winter 冻结 `gamma=0.4`，其余输入/公式/证据范围/决策规则
  与 0.8 臂完全一致。**0.4 是预先指定的 Winter 配置迁移，不是阈值搜索**：无网格、无逐样本门槛、无按标签选参。
- **关键结论 1（门槛不是原因）**：`v3+0.4` 与 `v3+0.8` 的**逐条预测完全相同**——每一行的分数、可判断性、
  动作定位记录与最终预测都一致，两份文件只差记录用的 `action_mapping_gamma` 字段。原因是 v3 的
  `structure_not_satisfied` 由结构比较而非 gamma 决定，两个 gamma 下同样 30/40 被拒。
- **关键结论 2（同样是 0.4 时结构匹配在伤害定位）**：同 gamma 0.4 下标签 argmax 路径映射 27/40 个规则动作，
  v3 只映射 10/40（全部为精确标签的 prohibited 插入）。v3 拒掉的 30 条里 26 条 `no_candidate_above_gamma`、
  4 条 `structure_not_satisfied`；四类中 condition/constraint/exception 的动作门槛就是该判定，因此三个类型在
  变体侧永远不可判断。
- **三个已证实缺陷**（由逐项产物直接证明，见 `outputs/evidence/s3_extended_gap_v1/difference_lists.json`）：
  **D1** `prohibited_action_present` 报告的是 v3 的**词元化** `candidate_max_similarity`，而冻结公式与
  `gamma_ext=0.5` 是在**原始标签**相似度尺度上锁定的（`prohibited_action_04` 原始 1.0000 / 词元化 0.5040；
  `exception_not_handled_04` 原始 0.5080 / 词元化 0.5040，同一个 0.5 落在两个尺度两侧）；**D2** 同一条
  检查里"动作指哪个活动"有两个答案：`prohibited_action` 在 v3 未定位时仍回退候选最高分给出分数，
  `_missing_evidence` 却弃权，于是 `exception_not_handled_04/05` 被报成 prohibited 违规；**D3** 把
  "必需动作是否存在"的**验证判定**当作四类证据检查的**硬定位门**，在法条短语↔流程标签的对象内容不同时
  直接掐断所有下游比较。
- **修复臂（继承 + 定点修复）**：`src/bpc_hybrid/s3_extended_v3_repair.py` 子类化 `V3ExtendedScorer`，
  只替换动作解析入口。继承不变：冻结面板与规则绑定、六要素抽取器、四个候选面、四条冻结公式与
  `gamma_ext=0.5`、统一五分类决策与其固定类型顺序、冻结评价器、可判断性策略，以及 v3 的结构化动作表示
  （精确标签层、嵌套动作、语义角色、数字/否定）。改动只有三处，对应三个缺陷：①prohibited 用本臂声明的
  原始标签公式 `max sim(rule_action, process_activity)` 计分，报告的 violation 就是该分数决策；
  ②全行**唯一动作解析**（v3 满足匹配优先，否则本臂标签 argmax 且需达到本臂动作 gamma）同时供分数决策、
  候选面、证据分数与 contradiction 门槛使用，解析不到就明确记为不可判断；③contradiction 分支只经同一
  解析活动与同一 gamma 可达。动作 gamma 仍取 Winter 冻结 0.4（与诊断臂相同的预指定配置），`gamma_ext` 不变。
- **同条件结果（A 变体 40 / B 对照 40 / C 成对 40 / D 合并 80；互斥计数守恒）**：
  | 臂 | 匹配路径 | 动作gamma | A正确 | A错类 | A弃权 | A判合规 | A Macro-F1 | B误报 | B合规 | B弃权 | C成对 |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | Winter（冻结） | 原始标签 argmax | 0.4 | 17 | 9 | 18* | * | 0.4738 | 20 | 12 | 8 | 9 |
  | Sun（冻结） | 原始标签 argmax | 0.8 | 10 | 1 | 30* | * | 0.2381 | 5 | 9 | 26 | 7 |
  | orig+0.4（重推） | 原始标签 argmax | 0.4 | 17 | 9 | 12 | 2 | 0.4738 | 20 | 12 | 8 | 9 |
  | v3+0.8（既有） | v3 结构匹配 | 0.8 | 10 | 2 | 26 | 2 | 0.2273 | 8 | 6 | 26 | 4 |
  | v3+0.4（诊断） | v3 结构匹配 | 0.4 | 10 | 2 | 26 | 2 | 0.2273 | 8 | 6 | 26 | 4 |
  | v3+0.4 修复 | v3 匹配 + 唯一解析 | 0.4 | **19** | 9 | 10 | 2 | **0.5233** | 20 | 14 | 6 | **11** |
  `*` 冻结臂由冻结评价器原样报告，其 `unobservable` 字段把"明确判合规"合并在内，故这两行无法拆分该列。
- **改善与回退都如实报告**：修复臂在 Winter 正确的**全部 17 个实例上仍然正确**（A2 差异清单为 0），
  并新增 2 个 Winter 因 `action_mapping_below_gamma` 弃权而修复臂能判断的实例
  （`constraint_violated_03`、`required_condition_10`），分类别 F1 全面提升（condition 0.2353→0.3333、
  constraint 0.4000→0.5000、exception 0.3077 持平、prohibited 0.9524 持平），成对正确 9→11。
  **代价**：对照误报 20/40，比旧 v3 臂的 8/40 明显变差，与 Winter 臂持平——这是 D1 纠正后的真实水平：
  在原始标签尺度上，冻结四类公式与 `gamma_ext=0.5` 本身就会把边界标签对判成违规。误报水平是冻结公式
  属性，不是修复引入的；换 `gamma_ext` 属于新的预注册，不是修复，本轮不做。
- **仍存在的问题**：①`condition/constraint/exception` 的变体侧仍有 10 例弃权（8 例
  `action_not_resolvable_to_activity`、1 例 `no_condition_candidates`、1 例
  `requirement_evidence_not_satisfied`），即规则动作在流程里确实找不到任何 ≥0.4 的锚点；
  ②证据比较文本与 `gamma_ext=0.5` 的尺度口径（候选面是多来源标签/注释/时间文本）仍是先于 v2/v3 的遗留问题，
  本轮只做了披露未改动；③修复臂在任何指标上都没有超过"原路径+0.4"，即**同 gamma 下 v3 结构匹配在本面板
  可测得的净贡献仅是精确标签层加上 D2/D3 的一致性**，该结论不得反向表述为结构匹配提升了四类检测。
- 产物：`outputs/development/{s3_extended_baseline_04_v1,s3_extended_v3_gamma04_v1,s3_extended_v3_repair_v1}/`
  （各四件，含 manifest 与实施哈希）；证据 `outputs/evidence/s3_extended_gap_v1/{comparison_v1.json,comparison_v1.md,difference_lists.json,method_change_note.md,manifest.json}`；
  复核入口 `python formal_experiment/scripts/build_s3_extended_gap_comparison_v1.py --check`、
  `.../build_s3_extended_gap_evidence_v1.py --check`、三个 `--check` 臂。
- **边界**：development-only 受控面板；四类仍是项目自定义扩展，不是 Winter/Sun 原生能力，也不得改称"我们的方法"；
  旧 v3 0.8 配置与产物逐字节保留；未改 Gold、面板标签、历史结果、Sun/Winter 本体与冻结公式。

## 2026-09-11 修订 3.6.49：四类扩展的 v3 方法臂（S3-EXTENDED-V3，零 API）

原三类的 v3 已有受控结果，但一直不是**扩展四类结果表**里的方法臂。本轮补齐：在 s3_formula_repair_v2 的
reference 四类面板（40 变体 + 40 既有对照，每类 10 对）上实跑 v3 臂，同一面板、同一规则来源、同一评价口径。

- **薄适配层**（`src/bpc_hybrid/s3_extended_v3_adapter.py`）：只替换动作定位——v3 `action_match` 取代
  `ExtendedViolationScorer._best_action` 的纯相似度 argmax。四类既有公式、`gamma_ext` 决策规则、合规侧与
  变体侧共用的统一决策、冻结评价器均未改；未改 Sun/Winter/v3 本体、相似度模型与任何阈值。
- **一致性**：定位出的**同一个匹配活动**同时供"动作门槛 / exact-contradiction 门槛 / condition、
  constraint、exception 候选面"使用；v3 的唯一匹配、歧义、明确不满足、候选面缺失三分语义保留，歧义与
  不满足一律保持**不可判断**，绝不用 1.0/0.0 冒充布尔结果；不新增样本 ID 特判或词表。
- **运行规模**：只跑新臂 40 个变体（含各自对照）= **80 个评价对象**；Winter/Sun/BM25/TF-IDF 旧臂按哈希
  只读复用，未重跑、未改写。预测先落盘、标签后读取，真实 LLM/API 调用 0。
- **同一口径结果**（A 变体 40 / B 对照 40 / C 成对 40 / D 合并 80）：新臂 **A Macro-F1 0.2273**、
  A 命中 10、错误类型 2、不可判断 30；B 误报 **8/40**、明确合规 6、不可判断 26；C 成对成功 **4/40**；
  D 五类 Macro-F1 0.1833。对照旧臂：Winter 0.4738 / 20 / 9（A/B 误报/C）、Sun 0.2381 / 5 / 7、
  BM25 0.1429 / 0 / 4、TF-IDF 0.3750 / 11 / 12。分类别：仅 prohibited F1 0.9091，其余三类 0。
- **Sun→v3 逐项**：unknown→正确 0、unknown→错误 0、正确→错误或 unknown 0、保持 unknown 26、保持正确 10、
  其他 4（均为例外变体上 prohibited 类型触发）。**分数没有提高，如实交付**：新臂与 Sun 在变体侧同为
  "只有 prohibited 可用"，对照侧与成对侧略差（8 vs 5 误报、4 vs 7 成对），差异来源已逐项定位到
  v3 自身的词元化相似度与结构层级（例：3 个对照的 prohibited 分数因词元化越过 0.5 而误报）。
- **低分卡点（有数量）**：30/30 个 condition/constraint/exception 变体卡在**动作定位**：14 个不同的规则侧
  动作短语，最佳候选相似度 0.3177–0.6683（全部 < 冻结动作 gamma 0.8），26 个 `no_candidate_above_gamma`、
  4 个 `structure_not_satisfied`；`matched_with_similarity_below_recorded_gamma = 0`，即 v3 结构层级从未
  打开纯相似度门槛关着的门。**结论是规则短语↔流程标签的语义落差（14 个短语全部有动词谓词，不是抽取崩溃），
  不是检查公式或后续判断的问题**；该瓶颈需在规则侧动作规范化/对齐层面解决，本轮不做。
- 产物 `outputs/development/s3_extended_v3_v1/{predictions.jsonl,metrics.json,diagnostics.json,manifest.json}`；
  复核入口 `python formal_experiment/scripts/run_s3_extended_v3_v1.py --check`。
- **边界**：development-only 受控面板，不是 S3.9-EXT 的 Gold/Oracle 结论；原三类的 0.9825 不得搬入四类表；
  Winter-style 仍名为 Winter-style，未被改称"我们的方法"。

## 2026-09-11 修订 3.6.48：真实法条诊断的证据关联、原因分类与覆盖统计返修（S3-REAL-RULE-DIAGNOSTIC-CORRECTIONS，零 API）

这是 3.6.47 的**限定返修**，不是新一轮方法优化：不运行新批次实验，不改检查器、Gold、阈值、规则输入与
既有 66 条预测（逐字节复用，哈希与 v1 manifest 绑定一致），真实 LLM/API 调用仍为 0。

- **问题 1（未映射被算作“证据支持判断”）**：`evidence_supports_judgment` 作为映射类别被撤销。
  只有“检查具备所需信息 + 活动已可靠确定 + 执行者可观测”才可归入正向支持。v3 的 13 条 actor-action
  对全部为 `linked_action_not_reliably_mapped`，`executor_comparison_performed` 0 条；Sun 的 Definition 6
  只返回条款级聚合，原生缺失字段记为“原生证据缺失/推导范围”，不再声称“规则缺少执行者信息”。
  `mapping.matched_activity_executors` 更名为 `candidate_best_activity_executors` +
  `executors_of_matched_activity`（候选的执行者不得冒充已匹配活动的执行者）。
- **问题 2（不同 actor-action 对被合并）**：actor 证据去重键加入 `linked_action_requirement`；
  v026/v032 各恢复为 2 条正确绑定的对。该信息在已存产物中不可恢复，因此对这两个 item × 两方法执行
  **4 次原生 `IncorrectActor` 调用**（上限 4）：原生 status/score/denominator/reason 与已存预测完全一致，
  新增证据标注 `recomputed_native_repair`，不声称原运行已保存。来源改为来源列表（同一要求多句来源全部保留）。
- **问题 3（引用次数写作去重数）**：分列 **A 引用次数**（84 动作引用 / 13 执行者对引用 / 8 端点引用）
  与 **B 去重数量**（42 动作要求 / 13 执行者对 / 8 端点），去重键显式写出，动作、执行者对、顺序端点
  三类各自给分子分母，不合成“总体映射率”；同一动作被 missing_action 与 incorrect_actor 引用时唯一数只计一次；
  两种检查上下文的返回信息分别保留（不再“先写入覆盖后来结果”）。
- **问题 4（未映射端点被断称“不是活动”）**：端点为**未匹配 / 匹配到活动 / 匹配到事件 / 来源未定位**四种状态；
  未匹配时节点种类为 **unknown**，只有真实节点 `kind` 才能确定类型。**撤销**“事件不受支持导致顺序检查无法判断”
  的过度结论：`SunProcessModel.actions` 同时包含 activity 与 event，且可达表覆盖它们；本诊断端点的真实阻碍是
  规则侧无 order 关系（8/11 项）与端点未映射（3 项）。不新增事件解析器，不把“知悉泄露”等同于“泄露发生”。
- **问题 5（条件只看条款首句）**：`clause_has_conditions` 在 rule 的首条句子后即返回；修正版按同一 rule 的
  **全部句子与规范**聚合（9 条法条 / 74 句 / 92 条规范：含条件 49、约束 38、例外 17），并因冻结转换器与两个
  检查器都不消费这些要素，把适用性统一记为 `not_evaluated`，而不是“没有条件”。该函数对布尔结论本身无影响
  （9 条法条首句均已含条件/约束/例外），受影响的是聚合口径与幅度。
- **产物与复核**：`outputs/development/s3_real_rule_diagnostic_corrections_v1/{mapping_evidence.jsonl,summary.json,corrections.json,manifest.json}`；
  不复制 predictions/scope_review/BPMN/Gold，全部按路径+哈希引用；每个原始 item/method 都有显式
  v1→修正证据关联。复核入口 `python formal_experiment/scripts/repair_s3_real_rule_diagnostics_v1.py --replay`。
- **修正后仍成立的瓶颈**：article16 无 obligation 动作（v028/v029/v030）、article20 无 actor（v020/v029）、
  9 条法条无结构化 order 关系、条件/约束/例外不被消费。**本轮不改变任何预测，不构成性能声明或 Gold 发布。**

## 2026-09-10 修订 3.6.47：真实法条输入上的 Sun×v3 逐条诊断（S3-REAL-RULE-DIAGNOSTIC，零 API）

首次把**已确认的人工法条规则**接到 7 张**原始 BPMN** 上实跑：冻结 Sun 与当前 v3 各跑一遍
旧推断输入的 33 个 item（指定检查类型），共 66 条输出，先落盘预测再读标签。

- **输入与主策略**：人工 Gold Rule Records（74 句 / 92 条规范）经既有机械转换器转成检查记录，
  **仅 obligation** 模态；已确认的 3 条文字顺序说明按既有运行时投影成为顺序边（端点不新增为必须动作）；
  只加载 7 张原图，不加载任何合成变体。
- **obligation-only 的真实覆盖**：article16 无 obligation 子句（0 动作）、article20 无执行者（0 actor）、
  9 条法条的结构化 order_relations 全为 0；被排除的 permission/prohibition/definition 子句数量逐条记录。
- **结果（66 条，分母各 11）**：Sun 与 v3 **完全相同**——missing_action 10 violation + 1 unknown、
  incorrect_actor 11 unknown、out_of_order 11 unknown（method_differences = 0）。
  unknown 原因：v3 为 missing_rule_order_relations 8、no_candidate_above_gamma 8、order_endpoint_unmapped 3、
  missing_rule_actor_action_map 2、empty_rule_action_set 1、requirement_evidence_not_satisfied 1。
- **映射覆盖（去重单元）**：84 个必需动作 / 13 个必需执行者 / 8 个顺序端点。
  Sun：mapped_unique 1、expression_differs_unresolved 83、order_endpoint_not_an_activity 8、
  rule_lacks_required_information 13；v3：mapped_unique 2、expression_differs_unresolved 80、
  structure_parse_insufficient 2、order_endpoint_not_an_activity 7、evidence_supports_judgment 14。
  **（2026-09-11 修订 3.6.48 修正：这里的 84/13/8 是检查实例引用次数而非去重数量，去重后为 42/13/8；
  上述类别计数按引用计得，且 `evidence_supports_judgment` 含有未映射证据，均已作废。）**
- **三类主要阻碍（附实例）**：① 无 obligation 子句 → v028/v029/v030 无可检查动作；
  ② 顺序检查缺规则侧关系 → v006/v012/v015/v018/v021/v027/v030/v033 分母为空；
  ③ 执行者检查缺 actor → v020/v029 不可观测。另记录条件/约束/例外未被转换器消费（适用性未评估）。
  **（2026-09-11 修订 3.6.48 补正：适用性对全部 33 项记为 `not_evaluated`；顺序端点的真实阻碍是规则侧
  无 order 关系与端点未匹配，与事件表示无关。）**
- **范围核查（33 项，5 组最小问题）**：G1 目标 clause/活动绑定（33）、G2 原图或变体（33）、
  G3 证据引用缺失法条 Article 12/19（v018/v021/v030/v033）、G4 v001/v002 与已确认局部通知意见冲突（2）、
  G5 无合规对照（33）。机器只提出候选绑定并标注 machine_proposed/human_confirmed=false，未改 Gold、未新增对照。
- **旧标签诊断**（仅 `legacy_label_diagnostic`，33 项全保留、正例 unknown 计 FN、scope_unresolved=true、
  performance_claim_ready=false）：两方法 macro-F1 均 0.3175（missing_action F1 0.9524，另两类 0）。
  **这不是本轮主结果，也不是正式 S3.7 Oracle 或 Gold 发布**；合成面板的 0.9825 不得带入本轮。
- 产物 `outputs/development/s3_real_rule_diagnostic_v1/{predictions,mapping_evidence,scope_review,summary,manifest}`；
  复核入口 `python formal_experiment/scripts/run_s3_real_rule_diagnostic_v1.py --replay`。

## 2026-09-10 修订 3.6.46：动作表示与候选匹配 v3（嵌套动作、关系结构、语义角色，零 API）

在 v2 固定面板上继续只改**动作表示与候选匹配**：新增薄后继模块
`src/bpc_hybrid/s3_action_matching_v3.py`（`s3_action_matching@3.0.0`），继承 v2 并只覆盖
`action_match` 与其表示/比较辅助函数；v1、v2、冻结 Sun、执行者/顺序检查、unknown 聚合、
评价器、阈值、相似度后端与 NLP 模型全部不变。

- **已确认的四个问题（均由逐项证据复现）**：① 嵌套动作被丢弃 ——
  `rectify/access/erase` 是 `acl` 槽位动词，被 v2 的对象过滤掉，三个候选对象证据完全相同
  而并列 unknown；② 动作间关系被压平 —— `Stop running BPs using withdrawn data` 与
  `Stop using withdrawn data` 只按词集合比较；③ 单个不匹配候选否定整个匹配 ——
  加入 `Inspect furniture` 后 `Inspect package`↔`Examine package` 由匹配翻成冲突；
  ④ 词集合相同掩盖语义角色相反 —— `from Alice to Bob` 与 `from Bob to Alice` 被判为一致。
- **v3 表示**：主动作、对象内容、**嵌套动作**（`{verb, objects, slot, span}`）、
  **介词角色绑定**（`from: {alice}`、`to: {bob}`）、否定/数量，并为每个元素记录原文 span。
- **v3 判定**：唯一完全匹配优先；同名多 ID 仍未知；一个候选不匹配只排除自身，不再否决
  已成立的匹配；要求被至少一个候选满足即为满足（存在语义）；只有**所有**同谓词候选都是
  明确不满足时才判 violation，出现任一"信息不足"候选则保留 unknown；谓词一致按词元相等
  判定，词面差异走冻结整标签相似度路径；从属子句主语计入内容；要求自身内容无法解析时
  不伪造结构，直接记 unknown。未新增 GDPR 词表、rectify/access/erase 专项规则、BP 特判、
  样本 ID 特判或同义词表。
- **复测（同一冻结契约、分母不变）**：macro-F1 **Sun 0.7874 / v2 0.9630 / v3 0.9825**；
  unknown **0 / 2 / 1**；成对成功 **16/28、26/28、27/28**；v3 逐类 missing_action 0.9474
  （TP9 FP0 FN1 TN10，正例 unknown 1）、incorrect_actor 1.0000、out_of_order 1.0000；
  **v2 正确而 v3 错误/unknown 0 项，v2 错误而 v3 正确 1 项**。
- **两个原 unknown**：`syn_missing_action_04::variant` 根因为嵌套动作丢失，v3 判
  `nested_action_substituted`（`rectify` 被 `access`/`erase` 替换）→ **unknown→violation**；
  `syn_missing_action_06::variant` 根因为关系被压平，v3 判为**包含关系**
  （候选 `use(withdrawn data)` 是要求结构的成分，缺 `run(BPs)`）→ **仍为 unknown**，
  按契约解释未裁定处理：既不预设改成 violation，也不改契约与分母。
- **契约解释问题（待协调者裁定）**：本面板的 missing_action 契约定义为"指定结构化活动是否
  存在"（定义 A），未定义"任何实现等价业务效果的活动"（定义 B）；`syn_missing_action_06`
  的等价性因此无法由既有定义裁定，保留 unknown 并计入漏检。
- **边界**：development + synthetic 固定回归面，不是独立泛化结论，也不是正式法条 Stage 3
  实验；真实法条↔流程语义映射仍未评价。复核入口
  `python formal_experiment/scripts/run_s3_action_matching_v3.py --replay`。

## 2026-09-10 修订 3.6.45：开发检查器动作匹配缺陷修复与固定面板复测（S3-ACTION-MATCHING-V2，零 API）

本轮唯一改动是**开发检查器的动作匹配策略**：新增薄的后继模块
`src/bpc_hybrid/s3_action_matching_v2.py`（`s3_action_matching@2.0.0`），继承既有
`EvidenceChecks` 并只覆盖 `action_match` 及其内部辅助函数。v1 文件、冻结 Sun 实现、
执行者检查、顺序判断、unknown 聚合与指标逻辑、NLP 模型、相似度后端、阈值一律不变。

- **已确认缺陷（逐项证据）**：v1 给“完全匹配”和“同谓词＋共享内容词”同样 1.0，二者并列即被判为
  歧义；其内容词集来自词性分析，短标签下动作首词被标成 NOUN 进入内容词集（实测共享集
  `['retrieve']` 就是动作词本身），使“共享动词”伪装成“共享业务对象”；删除真正目标后，
  同动词异对象的剩余活动仍得 1.0 → 输出 `satisfied`。
- **v2 策略（在跑面板前冻结）**：唯一完全匹配（NFKC＋casefold＋空白折叠）优先于一切近似匹配；
  不同活动 ID 的同名标签仍为 unknown（不按 ID 取第一、不用冻结目标 ID）；对象证据排除动作头词、
  同谓词词元、动词/助动词与主语类槽位；同谓词但对象互斥或数字/否定不同 → 冲突；部分重叠 →
  保留 unknown；无对象证据时沿用冻结相似度与 gamma。不新增 GDPR 词表、样本 ID 特判或白名单。
- **复测（固定上轮面板，未改分母）**：固定变体 30、**有效契约 28**、未解决 2、28 对、56 个检查实例；
  A 冻结 Sun 与 B v1 复用上轮已验证预测（绑定校验后复用，未重跑），只为 C 生成 56 行新预测。
  结果：macro-F1 **0.7874 / 0.7579 / 0.9630**；总 unknown **0 / 19 / 2**；成对成功
  **16/28、17/28、26/28**。v2 逐类：missing_action 0.8889（8/0/2/10，正例 unknown 2）、
  incorrect_actor 1.0000（8/0/0/8）、out_of_order 1.0000（10/0/0/10）；对照误报全 0。
- **变化审计**：19 个 v1 unknown 中 18 个转为正确、0 个转为错误、1 个仍 unknown；纠正 20 项、
  未变 35 项、改变但仍不正确 1 项、**回归 0 项**。残余 2 项：`syn_missing_action_06::variant`
  （部分对象重叠→unknown，此前误判 satisfied）与 `syn_missing_action_04::variant`
  （不同活动对象证据相同→unknown）。
- **边界**：本面板用于定位缺陷，故本轮属固定开发集回归与机制改进证据，**不是**独立测试集泛化结论；
  不声称优于 Sun 整体方法，也不解决真实法条语义映射。产物
  `outputs/development/s3_action_matching_v2/{predictions.jsonl,metrics.json,diagnostics.json,manifest.json}`；
  复核入口 `python formal_experiment/scripts/run_s3_action_matching_v2.py --replay`。

## 2026-09-10 修订 3.6.44：Stage 3 三类检查的成对受控机制实验（S3-PAIRED-MECH，零 API）

针对 S3.7-DIAG 遗留的“执行者/顺序两类零分”，在**受控合成面**上补齐机制证据：
冻结 30 变体面板的每个变体配一个**原图局部对照**，构成 30 对、每类 10 对。
本实验是 development synthetic mechanism experiment，**不是**正式 GDPR Oracle，
**不是**人工规则与自动规则优劣比较，**没有**评价法条到流程的语义映射难度。

- **契约（推断前锁定）**：30 个固定变体按原图结构与冻结目标元数据导出局部合成规范；
  有效契约 28、未解决 2（`syn_incorrect_actor_03`/`_04` 注入 lane 名称与既有 pool
  同名 `Data Controller`，所有权标签集未变，故不构成可靠正例；样本保留并记录原因，
  未删除、未补写）。检查实例 56（28 对照 + 28 变体），逐项预测行 112。
- **两个检查器同输入同配置**：`sun_2024_frozen`（冻结 Sun 重建）与
  `evidence_checks_v1`（已提交开发检查器），同一局部合成要求、同一 Stage 1 解析、
  同一 NLP、同一 tau/gamma/theta=0.8 与同一评价口径；每次统一计算三种检查信号，
  评价器只取指定目标检查（指定类型的局部检测，不是自由三分类）。
- **结果（真实复算）**：macro-F1 Sun 0.7874 / EvidenceChecks 0.7579；成对成功
  16/28 与 17/28；总 unknown 0 与 19（全部来自“近重复动作标签”导致的中止）。
  missing_action 两方法同为 F1 0.6667（5/10 成对）；incorrect_actor Sun F1 0.6957
  但**对照误报 7/8**（成对仅 1/8），EvidenceChecks F1 0.8571、**对照误报 0**（成对 6/8）；
  out_of_order Sun F1 1.0000（成对 10/10），EvidenceChecks F1 0.7500（成对 6/10，4 对中止）。
  **没有整体提升**：不得宣称新检查器优于 Sun 或端到端提升。
- **未知处理**：冻结 Sun 的“数值 0 + 分母 0”由只读适配层转 unknown 并保留原始返回值；
  正例 unknown 计入漏检，对照 unknown 不计为正确拒报。
- 产物 `outputs/development/s3_paired_mechanism_v1/`（contracts_locked / predictions /
  metrics / manifest / REPORT）；复核入口
  `python formal_experiment/scripts/run_s3_paired_mechanism_v1.py --replay`。
- **仍未解决**：真实法条↔流程语义映射未评价；旧 33 条人工标签检查范围问题未变；
  冻结面板 2 个 incorrect_actor 变体未真正改变执行者归属。

## 2026-09-10 修订 3.6.43：S3.7-DIAG 证据转换、可观察性与评价范围修复

用户要求追查执行者/顺序两类零分并修复。本子任务在已通过完整性检查的冻结输入上，
仅增加开发后继检查器、离线诊断报告和测试，不修改 Gold、冻结 Sun 方法或阈值，不调用 API。
验收对象是可复现的错误修复和每条结果的原因，不以分数上升判定完成。

- 已确认人工材料的 `temporal_suggestions` 实际含 3 条明确先后说明；旧链路未消费。
  `s3_evidence_checks_v1.py` 将同句唯一原文端点机械转换为运行时顺序边，保留来源，
  不新增义务动作，不发布新 Gold。修正此前“法条/人工规则没有顺序信息”的过强结论。
- 空关系、无端点映射和歧义映射现在输出无法判断；增加可解释的谓词+内容匹配，
  执行者检查按活动的实际 lane/pool，不将业务对象混为执行者。这是独立开发方法版本，
  不是冻结 Sun 基线的历史数值改写。
- **S3.3/S3.7 评价范围问题未解决**：33条全为正标签，matching 负例不能替代违规检测的合规对照。
  推断输入未绑定具体规范/活动/变体；4条顺序判定的证据引用缺失的 Article 12/19。
  另有用户已确认的局部通知意见与 v001/v002 的检查范围冲突。不得自动改 Gold。
- 输出 `outputs/reports/s3_evidence_repair_v1.{json,md,manifest.json}`，33条逐项结果全部保留。
  对旧标签诊断复算：Rules-Only/全情态人工输入 macro 均0.3333，义务人工输入0.3175，
  未产生性能提升结论。局部通知活动及其控制者判断已正确，23项针对性测试通过。
- 当前状态：**开发修复已实现并复算；人工判定范围待核实；正式主表仍不可发布**。
  复核入口：`python formal_experiment/scripts/run_s3_evidence_repair_v1.py --replay`。

## 2026-09-09 修订 3.6.42：GDPR-7 正式 Gold Rule Records + Oracle 与下游配对实验（零 API）

**S3.7 依赖①：正式 Gold Rule Records 已发布**。用户确认的 74 句 / 92 条规范人工
核对包（`gdpr7_human_confirmed_v1/confirmed_rule_items.json`）经**机械、无损**转换
为正式 Rule Record 契约并发布：

- Gold：`data/gold/stage3/gdpr7_gold_rule_records_v1.json`（schema
  `gdpr7_gold_rule_record@1.0.0`，9 条款 / 74 句 / **92 条规范条目** / 235 要素 span +
  85 情态证据 span = 320 锚点 / 38 关联条目；**一条规范 = 一个 clause**，多情态句不再
  被取首项压平）；
- 胶囊：`data/predictions/gdpr7_human_rule_record_v1/predictions.json`
  （schema `gdpr7_human_rule_record_predictions@1.0.0`，74 行坐标-only，可被现有
  `gdpr_capsule_converter` 直接消费）；
- 转换器 `src/bpc_hybrid/gdpr7_gold_rule_records.py`（`@1.0.0`）、构建器
  `scripts/build_gdpr7_gold_rule_records_v1.py`、**独立 verifier**
  `scripts/verify_gdpr7_gold_rule_records_v1.py`（32 项检查：schema、span 回指、
  逐字段往返无损、胶囊镜像、哈希绑定），15 项聚焦测试；
- 授权事件 `configs/gdpr7_gold_rule_records_authorization_event_v1.json`（绑定用户
  2026-09-09 确认事件 + 本次发布指令哈希；授权范围明示**只能机械转换、不得新增/推断/
  改写/归一化**）。

**S3.7 依赖②：人工规则接入 Stage 3 检查器**。`gdpr_capsule_converter@1.3.0` 新增
第三个允许 schema（Gold Rule Record 胶囊），`run_gdpr_3type_linkage_v1.py` 新增
`human_rules` 来源臂（`include_modalities=ALL`，92 条规范全部进入检查器），
`run_gdpr_s2_s3_linkage_v1.py` 四类面板同步新增 `human_rules` 来源。

**Oracle 单独评测已运行（`s3_oracle_gold_rules_v1`，零 API）**：

| 表面 | 规则来源 | macro-F1 | exact | detected | unobservable |
|---|---|---:|---:|---:|---:|
| 33 条人工 violation Gold | oracle（人工规则） | 0.3333 | 0.3333 | 11 | 11 |
| 33 条人工 violation Gold | oracle（obligation-only） | 0.3175 | 0.3030 | 10 | 11 |
| 33 条人工 violation Gold | reference（dev 抽取器） | 0.3889 | 0.3636 | 12 | 10 |

逐类型（oracle）：missing_action **P/R/F1 = 1.000/1.000/1.000**；
incorrect_actor 与 out_of_order 均为 0（见下）。四类合成面板（oracle 规则）：
Winter-style 0.3409 / Sun-style 0.0454 / BM25 0.0000 / TF-IDF-SVD 0.2063 macro。

**根因已诊断（不是规则错误）**：`mapping_diagnostics` 逐规则给出 Definition 6 动作
映射证据——人工确认规则使用**完整法律短语**（例 `implement suitable measures to
safeguard the data subject's rights and freedoms and legitimate interests`），其与流程
活动标签的相似度低于 gamma=0.8，因此 `incorrect_actor` 在 11/11 项上不可观察；
`out_of_order` 则因人工确认条目**没有 order_relations**（确认包只含 38 条
actor-action 关联、0 条顺序关系）而在 11/11 项上分母为 0。两者都如实计入分母
（不可观察 = FN），不置零、不伪造。

**下游配对比较已运行（`s3_downstream_paired_v1`，零 API）**：同一冻结 Stage 3、
同一 33 条人工 Gold、同一阈值/evaluator，只换 Stage 2 规则来源：

| 臂 | 状态 | macro-F1 | exact | detected |
|---|---|---:|---:|---:|
| rules_only（非 LLM B0） | evaluated | 0.3333 | 0.3333 | 11 |
| human_rules（人工 Gold 规则） | evaluated | 0.3333 | 0.3333 | 11 |
| direct_llm | **blocked**（胶囊未发布，不插值） | - | - | - |

**诚实结论**：在本冻结评测面上，人工规则**没有**提高最终检查分数（Δ=0）。差异集中在
missing_action（两侧均 1.0）与不可观察的 incorrect_actor；四类合成面板数字对人工规则
臂**有偏差**（面板绑定 dev 抽取的 `stage3_gold_inference_v1` 且用 first-valid-span
投影，11/40 变体落在多规范句上），已在报告中显式披露，不得据此宣称人工规则更差。

**真实 LLM 对照批次（步骤 4）**：离线准备已全部验证
（`outputs/reports/s2_llm_batches_offline_readiness_v1.json`）：授权/合同/预检资产齐备、
声明调用数与预检一致（63 + 74）、GDPR 74 次 payload-locked 假传输 74/74 完成且
零计费、无合同真实运行被拒、假胶囊 promotion 被拒、无凭据 S2.12 真实运行被拒。
**真实调用仍为 0，唯一阻塞 = 进程环境凭据缺失**（离线预检 5 项 FAIL，含 API key
absent）。Direct-LLM 胶囊不存在，故下游 LLM 臂保持 blocked。

**门禁未翻转**：S2.13 仍 blocked on S2.12 API arms；S3.4-S3.6 正式 promotion 仍
pending；**正式 S3.7 Oracle 主表未声明完成**（本轮为冻结评测面上的 Oracle 隔离运行，
`formal_s3_7_authorization` 仍未授予）。真实 API 调用 = 0。

### 论文 Table 3 可行性判定（PAPER-FINAL-REPAIR，2026-09-21，零 API，只读）

**结论：变异 benchmark 本身是健全的（30/30 结构性可检测），33 条 gold 不是 benchmark，
而当前 per-type 分数退化的根因是**检测器的相似度 grounding**，不是数据。**
完整诊断见 `docs/research/STAGE3_TABLE3_VIABILITY_DIAGNOSIS_2026-09-21.md`；复现脚本
`scripts/diagnose_stage3_table3_viability_v1.py`、
`scripts/diagnose_stage3_table3_threshold_rootcause_v1.py`、
`scripts/diagnose_stage3_mutation_detectability_v1.py`。

1. **33 条 violation gold 不是 benchmark**：33/33 条 `decision_violation_type` 逐字等于
   `check_type`，`decision_evidence` 为模板问句，无任何 BPMN 变异记录。它是
   check-point 决策集，保留为 provenance，**不得再作为 Table 3 的 F1 分母**。
2. **30 条真变异面板结构上完全可检测（30/30）**：用 Stage 1 Process Record 把每个变异体
   与其未变异原始体对比，**不涉及任何检测器与相似度**——missing_action 10/10（目标活动被删、
   无新增）、incorrect_actor 10/10（目标活动 lane 归属改变）、out_of_order 10/10
   （direct edges 与 reachability 改变，且 manifest 节点对顺序确实反转）。
3. **真正的分层**：结构性 = 健全（30/30）；**词面 grounding = 失败**（冻结 Sun 重建用
   embedding 相似度 + 高阈值把规则动作映射到流程活动，GDPR 法条措辞与 BPMN 活动标签几乎无
   共同词汇，映射始终低于 gamma）；**用该冻结 scorer 的可测性 = 0/30**。因此缺陷在
   **检测器的 grounding 路径**，benchmark 可在一个正确 grounded 的检测器出现后立即使用。
   ⚠️ 不得把项目既有的 γ=0.6 → Macro-F1 0.8733 当作本面板可测的证据：该数字测于
   **33 条** 集合，两者不可混用。
4. **仍存在的独立缺口（较窄）**：已发布 Gold Rule Records 中 `actor_action_map` 仅 38/92
   非空、`order_relations` **0/92** 非空（与上文 §S3.7 根因诊断一致），因此 out_of_order
   机制尚无 Gold 标注可对照。这是**一个字段的标注缺口**，不是需要重建 BPMN。

**边界**：禁止为了让某方法显得更好而事后挑选阈值、后端或面板；上述扫描已表明不存在
这样的设置。Table 3 取 A/B/C 哪一方案须由用户决定（见诊断文档 §8）。

### 论文 Table 3 配对 benchmark（PAPER-FINAL-REPAIR，2026-09-21，零 API）

**已完成"换掉 33 条 Gold + 跑前人 sanity check"两步**，产物均 tracked：

- manifest：`data/development/stage3_synth/stage3_paired_benchmark_v1.json`
- 生成器：`scripts/build_stage3_paired_benchmark_v1.py`
- 报告：`outputs/reports/stage3_paired_benchmark_v1.{json,md}`、
  `stage3_grounded_checker_v1.{json,md}`、`stage3_predecessors_paired_v1.{json,md}`
- 测试：`tests/test_stage3_paired_benchmark_v1.py`（5 项）

**benchmark 结构**：60 items = 30 pairs。每个变异 BPMN 与**同一流程的未变异 BPMN**
配对成 compliant control；control 直接复用该 variant manifest 自己声明的
`source_bpmn` + `source_bpmn_sha256`（即冻结 Stage 1 GDPR7 membership 字节），
**没有新造任何"看起来合规"的流程**，因此不会漂移、也不需要新的人工标注。
Gold 分布：30 compliant + 每类违规 10。每个 item **显式声明 grounding**
（`rule_action_text` / `target_activity_id` / lane / `order_pair`），使"按声明消费绑定"
与"按相似度重新推导绑定"两条路径可比，而不是被悄悄混为一谈。

**anti-degeneracy 校验**：control 必须不违反、variant 必须违反 → **30/30 PASS，0 问题**。
这是防止 benchmark 再次悄悄退化的守卫。

**grounded checker（参考上界）**：macro-F1 **1.0000**、micro-F1 **1.0000**、
compliant specificity **1.0000**、variant exact-type **30/30**、unobservable **0**。
即 benchmark 可测且 Ground Truth 自洽——这正是"健康的 benchmark 必须让正确 grounded 的
方法打出高分"的 sanity check；若它拿不到高分，说明 benchmark 仍然坏的。

**前人 sanity run（同一 60 items、同一协议）**：每个 arm 对每对的 control 与 variant 都
打分，沿用各自冻结的 `score > 0` 判定，unobservable 计入 miss、绝不置零。

| Arm | missing | incorrect | out_of_order | Macro-F1 | Micro-F1 | Specificity | Exact | Unobs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| sun_reconstruction | 0.6667 | 0.2857 | 0.0000 | 0.3175 | 0.3871 | 0.3333 | 12/30 | 16 |
| winter_wrapper | 0.6667 | 0.0000 | 0.0000 | 0.2222 | 0.3846 | 0.6000 | 10/30 | 0 |
| grounded_structural_checker_v1（参考） | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **30/30** | **0** |

**报告内的强制措辞**：该差距是 **grounding 效应**，**不得**写成"前人算法弱"。
`grounded_structural_checker_v1` 目前是**声明绑定下的参考上界**，不是完整论文方法：
把它写成 "Ours" 之前，必须先建一个**从已发布 Stage 2 Rule Record 真实推导绑定**的检测器
（即诊断文档的方案 A 剩余部分），否则就是把 benchmark 的答案喂给了检测器。

### "Ours" 行的可行性结论：缺的是人工标注，不是代码（2026-09-21，零 API，只读）

详见 `docs/research/STAGE3_OURS_ARM_FEASIBILITY_2026-09-21.md`。四步已核实的证据链：

1. **benchmark 没有 rule-action → activity 标注**：每个 variant 只有
   `target_activity_id`，**没有任何字段说明该活动实现的是哪一条 rule action**；
   rule text 与 activity name 都是多词 span，该对应关系**按构造不可恢复**。
2. **Gold Rule Records 的现状**（直接读，绕过不兼容的 converter）：92 clauses、
   70 条带 actions、**38 条有非空 `actor_action_map`、0 条有任何 `order_relations`**。
   （`gdpr_capsule_converter` 的允许 schema 只有三个 prediction schema，不接受
   gold schema；强行传入时 9 条规则全部 `failed=True`。）
3. **词面 grounding 正是失败环节**（已量化）：配对 benchmark 上
   `sun_reconstruction` macro-F1 0.3175、`winter_wrapper` 0.2222，两者
   `out_of_order` F1 均 **0.0**；而声明绑定下的参考上界为 1.0000。
4. **项目自己的正式 Direct-LLM linkage 报告已记录同一堵墙**（原文）：
   "order relations absent in capsule for rules: 全部九条 …（Definition-7 input
   unavailable by contract; **never fabricated**）"；unobservable 11 条，其中
   `action_mapping_below_gamma` **8** 条；`out_of_order` P/R/F1 = 0.0000。

**因此**：真正的 "Ours" 检测器需要把「rule action → 履行它的 BPMN activity」这一绑定作为
**输入**；而该绑定今天**无人标注**。剩余工作因此是**补这份人工标注**，不是再写检测器代码。
**禁止**自动填这份绑定——那等于 agent 自己制造 Ground Truth，违反本文档"不伪造结果"。

**三条诚实路径**（需用户决定）：

| # | 路径 | 需要什么 | 可声称什么 |
|---|---|---|---|
| A1 | 为 30 个配对 item 标注 rule-action→activity 绑定与规则 order 关系，再建消费该绑定的 grounded 检测器 | 30 item × 3 类的人工标注 + 9 条规则的顺序关系 | "Ours 在三类合规检查上优于前人" |
| A2 | 同上标注，但只覆盖今天真正可标的类型：`missing_action` 与 `incorrect_actor`（均 10/10 结构性可检测，绑定补齐后完全 grounded），`out_of_order` 明确排除 | 仅需 action 绑定标注 | "Ours 在 missing-action 与 incorrect-actor 检测上优于前人" |
| B | Table 3 作为**框架+可行性**表发表：配对 benchmark、anti-degeneracy 保证、grounded 上界、前人结果，并把 grounding 要求本身写成发现 | 无需新增 | "我们说明现有检测在本语料上为何退化，以及一个可测 benchmark 究竟需要什么" |

路径 B **完全由已提交的证据支撑**；A1/A2 是唯一能得出"优于前人"的路，且都卡在人工标注上。
### Table 3 v2 controlled repair（2026-09-23，零 API，当前口径）

**旧 F1=1 撤回**：`outputs/reports/stage3_table3_v1.json` 的 Ours 行来自一个受控对照之外的结构检查路径：automatic grounding 使用配对 CONTROL BPMN，`detector_activity_ids` 是候选并集（13 个 eligible pairs 中 10 个覆盖整个 control 活动集）；随后 `run_stage3_ours_v1.decide_item` 仅比较 current BPMN 与 control 的『活动是否存在 / lane 是否改变』，且 `actor_predictions` 未进入 actor 判定；`run_stage3_predecessors_paired_v1.py` 又用 development rule extractor 并按 `target_violation_type` 选输出。因此旧 Ours F1=1 是结构变异复现，不是法规语义匹配，相关『Ours 胜出/端到端语义合规』结论撤回。

**修复后的主比较**：新增 sanitized inference view（无 role/target/gold）和 `scripts/run_stage3_table3_v2.py`。Sun 与 Ours 只替换 Stage 2 capsule，共用同一 `gdpr_capsule_converter`、同一个冻结 `SunScorer` 实例与同一组 frozen `tau/gamma/theta`；Winter 使用 native wrapper 与 frozen config；所有类型信号先持久化，之后 evaluator 才读取 benchmark label。产物：

- `data/development/stage3_synth/stage3_paired_benchmark_inference_view_v2.json`
- `data/development/stage3_synth/stage3_regulation_text_view_v2.json`
- `outputs/development/stage3_table3_v2/{predictions.jsonl,rule_records_*.json,run_manifest.json}`
- `outputs/reports/stage3_table3_v2.{json,md}`
- `outputs/reports/stage3_table3_v2_error_analysis.json`
- `outputs/reports/stage3_table3_v2_rootcause_notes.md`

**真实结果（eligible target checks, 13 pairs / 26 items）**：Sun、Ours、Winter 三者 macro-F1 均为 0.3333，micro-F1 均为 0.5517。`missing_action` 为 P 0.5000 / R 1.0000 / F1 0.6667（8 TP / 8 FP）；Sun 与 Ours 的 `incorrect_actor` 5 个正例与 5 个 control 全部 unknown（frozen gamma 下 action mapping below gamma / actor map 不完整），`f1=0.0`；Winter 的 5 个 actor 正例 unknown、5 个 control 为 satisfied（无资源标签的 variant 为 unknown，有资源标签的 control 为 satisfied），`f1=0.0`。`out_of_order` 因规则侧 `order_relations` 为 0，eligible 分母为 0，保持 N/A，不填 0。结果不支持『Ours 优于前人』；本轮未按结果调阈值或改样本。

**边界**：13 个 eligible pairs 只有 6 个独立 control BPMN（7 个重复 control），不能把重复 control 当独立证据。下一步若要做正向 Ours 主张，必须单独预注册额外实验臂并明确新增变量（例如 rule-action→activity grounding），或补齐有原文依据的规则侧 order 标注以产生合法 order 分母；不得在本轮分数上继续调参。

**过渡核账 successor v9**：`outputs/reports/s2_13_s3_7_transition_readiness_v9.json`
（builder/verifier/schema/tests 齐备，verifier 全过）。v8 的 Gold-Rule-Record 三态
探测按设计 fail closed——候选一出现即拒绝；该候选的独立验证已完成，故 v9 用
`exist=true + verifier_verified=true + 完整绑定` 取代 v8 的缺失判断，并记录 Oracle
隔离运行。v9 **不再重跑历史 transition verifier**：那些 verifier 把冻结快照与“当前”
audit 状态对比，任何后续合法状态变化都会让它们按设计 fail closed；因此 v9 改为按
路径+SHA-256+字节数记录 v1–v8 资产并要求逐字节不变（`historical_verifiers_executed=false`）。
v8 及更早 capsule 逐字节保留。

**行尾可移植性修复**：`data/predictions/b0_formal_arm_v1/predictions.json` 在
`core.autocrlf=true` 下被检出为 CRLF，导致该正式 arm 的 raw SHA-256 与 manifest
不符（audit 报 `methods_unexpectedly_ready` / `final_experiment_not_ready`）。
按 G0-EOL-HASH-PORTABILITY 的既有窄口径做法，在 `formal_experiment/.gitattributes`
加**单文件** `text eol=lf` 钉并重新检出；文件内容哈希恢复为 manifest 值
`fa94991d…`，`verify_b0_formal_arm_v1.py` 恢复 VERIFIED，`integrity_pass=true`。
未修改任何实验数据、Gold、指标或方法。同一批还把 v1–v8 transition 测试模块按同一
窄口径钉为 LF（它们的原始字节是 v2–v7 报告里 “superseded asset” 哈希绑定的对象）。

**已废弃 capsule 的生命周期语义（重要）**：v1–v8 transition capsule 与
S2.11/G0.5 pre-authorization capsule 的 builder **按设计**在磁盘上出现任何
`rule_record` 命名文件时 fail closed（它们要求“用户授权的正式 manifest/schema/
verifier 三件套”，否则既不报 `exist=false`、也不自我提升为正式 Gold）。正式
Gold Rule Records 发布后这些 builder 必然 fail closed，因此它们那些“builder 可重跑
且 byte-identical / verifier 通过 / 无 Gold Rule Record”的测试**已不可能成立**。
处理方式：这些测试在 `tests/conftest.py` 中以显式理由 skip（保留可审计，不删除、
不弱化），当前状态真值由 successor v9 的 9 项测试断言（Gold Rule Records 存在、
哈希绑定、正式 Oracle 主表仍未授权）。另有一项 v7 的 superseded-asset 绑定失败
（v7 manifest 记录的 v6 测试文件哈希与任何已提交版本都不匹配）属**发布前既有漂移**，
同样按上述方式记录。

## 2026-09-07 修订 3.6.38：S3 公式/接口/评价根因闭环

**2026-09-07 Stage 3 根因修复与同输入复算（零 API）**：已修复 Sun Def6 的规则/流程 actor-action 关联、数值时限的动作绑定与适用范围、五分类漏计 abstention/误判合规。原三类 33 条两侧判定不变（reference 0.3889/0.3636；Rules-Only 0.3333/0.3333）。四类 reference macro 更新为 0.4738/0.2381/0.1429/0.3750；Rules-Only 保持 0.3313/0.1875/0/0.3321。既有阈值网格已复算，主聚合不变。当前证据 `outputs/reports/s3_formula_repair_v2.{json,md}` 与 `outputs/evidence/s3_formula_repair_v2/manifest.json`；论文 §7.4.4 与汇报第 9–11 页使用此版本。历史 2026-09-06 的四类参考数字及五分类 P/R/F1 不再作为当前结果。137 次真实 API、人工 Rule Record Gold、正式 Oracle 状态仍未完成。

验收：原三类公式量词/阈值保留；规则与流程关联可追溯；时间矛盾不绕过动作与适用门槛；80 对象逐项计入五分类统计；固定输入哈希不变；新旧预测差异逐样本记录。实现修复完成不等于方法性能已达预设高分，也不改变正式 Oracle 门禁。

## 2026-09-07 修订 3.6.39：论文收尾授权落地与执行链补齐（全部离线，ZERO CALLS）

**论文收尾指令（2026-09-07）已收到并记录**（逐字副本
`configs/paper_winddown_api_authorization_sentence_2026_09_07.txt`，UTF-8 SHA-256
`27426de7…`；依据文件 `configs/paper_winddown_api_authorization_basis_2026_09_07.json`）：
授权两批共 137 次真实调用（批 A=S2.12 63 次：direct_llm 36 + sun_llm_fallback 27，
off-peak、retry=0、USD≤42.09；批 B=GDPR scope `gdpr7_direct_llm_v1:74` 共 74 次，
USD≤1.31），并按要求补齐必要执行接口。本轮（零 LLM/API/网络）完成：

1. **授权事件/auth 文件已生成并通过 executor 同款校验**：批 A 五 stage
   （`configs/s2_12_api_authorization_{D-CAL,D-REST,F-1,F-2,F-3}.json` + 5 事件，
   caps 63M/258,048/USD 1.00 或 42.09/off-peak_only/retry=0）；批 B 事件
   （`configs/gdpr7_direct_llm_authorization_event_v1.json`，caps
   74M/303,104/4,096/USD 1.31、off-peak 价快照、官方价重验时间戳、6 项 hash 绑定）。
   活动验证器 `scripts/verify_s2_12_authorization_files_v1.py` 70/70 PASS；
   旧 zero-call verifier 的 no_real_auth 断言按设计 superseded（历史保留）。
2. **S2.12 API 臂执行链补齐（真实运行前必需）**：StageExecutor 可选 raw 落盘
   （内容只进 gitignored 目录）、transport 失败/usage 缺失事故记账后中止且绝不
   自动重发、链式 resume 后 final predictions 骨架按完整账本重建；两个 runner
   新增 `--raw-dir`；新增 `src/bpc_hybrid/s2_12_response_convert.py`（direct
   响应→坐标-only canonical）；`scripts/finalize_s2_12_arm_v1.py`（正式胶囊唯一
   发布入口：direct 转换 + fallback 经 `_rerun_b0` 文本重建与 H1 共享链按 frozen
   plan 27 行应用并逐 plan 审计；成本按官方 off-peak 价从 usage 重算）；
   `scripts/evaluate_s2_12_api_arm_v1.py --arm …`（与 sun_rule_only 同 Gold/分层/
   同一 evaluator，非全 ok 拒绝评价）+ `verify_s2_12_api_arm_v1.py`。
3. **GDPR 人工六要素裁决工作流 v1**：editable 派生
   `data/development/human_review/gdpr7_six_element_review_decisions_v1.json`
   + 共享规则模块 + 控制台工具（唯一编辑入口，进度 74/444）+ 填写后校验 +
   用户决定导入（confirmation 绑定）+ 冻结闭包验证；38 项合成测试（真实 blank
   字节未动）。
4. **测试与审计**：新增聚焦 60 项全绿；s2_12 safety+wiring 回归 52 passed；
   全量 audit --with-tests（2965 passed / 24 skipped，FILE_CATALOG 已重建）。

**状态转移**：S2.12 API arms 由 `pending explicit authorization` 变为
`authorized (2026-09-07) / ZERO CALLS / READY`——真实调用=0，等待进程环境凭据
（runner 只读进程环境，不读项目 `.env`）；S2.13 仍 blocked only on S2.12 DoD；
S3.7 未动；人工裁决工具已可用（真实裁决 0/74）。真实运行命令见
`docs/API_AUTHORIZATION_REQUEST.md` §13.3。

## 2026-09-09 人工确认导入（74/74，尚未发布正式 Gold）

用户已明确确认两份当前预填稿，本地文件无内容修订。确认事件绑定原稿/输入哈希；
已确认值在 `data/development/human_review/gdpr7_human_confirmed_v1/confirmed_rule_items.json`，
计74句、92条规范、552个要素决定、320处原文锚点。全部语义内容往返一致；新导入器
`scripts/import_gdpr7_confirmed_prefill_v1.py --check` 校验当前人工值与确认源，不经过v2取首项导出。
案例意见按原稿确认，已有疑点不是已解决标签；不改33条Gold、不批量确认40个control。
原稿/v1/v2编辑面只保留历史字节，旧入口0/74不代表当前确认进度。
句子级人工核对已完成；正式规则记录发布、Oracle及依赖真实API的比较仍按原门禁继续。

## 历史：2026-09-08 人工核对候选预填入口

用户要求先由 AI 认真预填，再自行检查、修改并确认。GDPR 9 条款/74 句候选已准备，
含 92 个规则建议条目、320 处逐字证据；人工入口
`data/development/human_review/gdpr7_ai_prefill_v1/请检查并修改这份预填稿.md`，
机器底稿与源哈希在同目录。所有人工决定留空（0/74），不改既有正式 Gold 或实验数字。
多情态句、条件/例外跨句关联、被动主体省略、重复短语位置均显式说明；确认后的导入
须保留这些信息，不得由 v2 单情态导出静默取首。此项是人工核对材料交付，不是正式
Oracle 或 S3.7 的完成声明；API 与其余实验依赖不变。

案例四项另见 `data/development/human_review/gdpr7_case_ai_prefill_v1/论文案例人工核对预填稿.md`，
全部待人工确认。预填依据原始 BPMN/法规；72小时计时器属于延误说明子流程，不能直接
证明主通知期限满足。局部通知活动的存在/执行者判断与既有 v001/v002 的整条检查范围
需核实，本轮不修改既有 Gold、对照标签或结果。

预填稿与重建脚本显式纳入 Git；人工字段保持待确认。离线执行安全测试使用可覆盖的
固定时钟，正向 D-CAL 测试主动模拟峰期系统时间，真实 API 的低峰约束保持原样。

## 1. 权威层级与更新规则

发生冲突时按以下顺序处理：

1. `AGENTS.md` 与安全边界；
2. `configs/experiment_contract.json` 的当前机器门禁；
3. 本文的完整研究目标、阶段依赖和任务树；
4. `docs/PROJECT_AUDIT.md` 的实时状态；
5. 各阶段设计规范；
6. `_retired/` 与 `docs/research/` 中的历史和证据材料。

本文可以随实验发现持续改进，但不得静默改路线。任何 Pipeline 变更必须：

- 给出新证据、导师要求或用户决定；
- 说明影响的任务 ID、数据、baseline、指标和已完成结果；
- 不重写既有实验结果或历史实验来源事件；
- 通过完整性检查并用 `record_change.py` 追加变更或实验运行日志；
- 在本文末尾的变更日志中追加一行。

当前 `experiment_contract.json` 仍是“优先完成 Stage 2、用固定 Stage 3
测误差传播”的阶段性执行合同。本文规定完整项目还必须完成 Stage 1 和 Stage 3。
进入 Stage 3 方法改进前，必须另行更新并核查机器合同；不能仅凭本文绕过现有门禁。

## 2. 不变的最终目标

本项目的最低完整交付不是“给 Sun Stage 2 加一个 LLM”，而是：

1. 独立、可追溯且可复现地重建 Sun 三阶段端到端方法；
2. 每个阶段都有明确输入、输出、Gold、baseline、指标和失败分析；
3. 优先在 Stage 2 比较传统方法、Sun、LLM 和混合方法；
4. 在预先定义的复杂法律语料上检验复杂度是否放大 LLM 优势；
5. Stage 2 完成后，继续比较和改进 Stage 3；
6. 最终用受控消融解释提升来自 Stage 2、Stage 3，还是二者交互；
7. 即使改进方法没有超过 Sun，也交付完整复现、负结果和误差边界。

允许的正式表述是 `method-level independent reconstruction of Sun Stage 2`：核心组件、
处理顺序、输入输出和评价口径与 Sun 对齐即可；作者原代码、原权重和完整私有词典
不可得不再单独阻断方法级复现。只有逐项核实全部公开规则语义时才使用
`paper-faithful`；始终禁止称 `exact reproduction` 或 `Sun original implementation`。

## 3. 研究问题

| ID | 研究问题 | 主要证据 |
|---|---|---|
| RQ0 | 能否完整重建 Sun 的三阶段设计时合规检查方法？ | 三阶段独立测试 + 端到端复现 |
| RQ1 | 多种非 LLM、Sun、LLM 和混合方法在 Stage 2 上如何比较？ | 模态分类与六要素抽取指标 |
| RQ2 | 法律语料复杂度增加时，不同 Stage 2 方法如何退化？ | 复杂度分层曲线与误差类型 |
| RQ3 | Gold 规则输入下，多个 Stage 3 baseline 与 LLM 谁更可靠？ | Oracle Stage 3 匹配与违规分类 |
| RQ4 | Stage 2/3 的局部改进能否转化为端到端提升？ | 固定组件与交叉消融 |

## 4. 完整流程图

```mermaid
flowchart TD
    G0["G0 数据与实验治理<br/>来源/许可/hash/split/Gold/复杂度"]
    BPMN["BPMN 流程模型库"]
    LAW["法律法规语料库"]
    G0 --> BPMN
    G0 --> LAW
    BPMN --> S1A["Stage 1A 结构解析<br/>task/event/gateway/flow/lane"]
    S1A --> S1B["Stage 1B 标签语义<br/>actor/action/business object"]
    S1B --> PR["Canonical Process Record"]
    LAW --> S2A["Stage 2A 模态分类<br/>definition/obligation/prohibition/permission"]
    S2A --> S2B["Stage 2B 六要素抽取<br/>modality/actor/action/condition/constraint/exception"]
    S2B --> RR["Canonical Rule Record"]
    PR --> S3A["Stage 3A 规则—流程匹配<br/>candidate generation + ranking"]
    RR --> S3A
    S3A --> S3B["Stage 3B 违规检测与分类<br/>missing action / incorrect actor / out of order"]
    S3B --> VR["Violation Report<br/>type + evidence + BPMN localization"]
    RR --> C2["Stage 2 组件评价"]
    PR --> C1["Stage 1 组件评价"]
    S3A --> C3["匹配 AP/MAP/Recall@k"]
    VR --> C4["分类 P/R/F1 + 定位"]
    GOLD["Gold Rule/Process Records"] --> ORACLE["Oracle Stage 3<br/>隔离 Stage 3 能力"]
    ORACLE --> S3A
    VR --> E2E["端到端消融<br/>Sun/Sun, Improved/Sun,<br/>Sun/Improved, Improved/Improved"]
```

逻辑上 Stage 1 和 Stage 2 并行产生 Stage 3 输入；项目实施顺序是：

```text
先完成 Stage 2 → 补齐并冻结 Stage 1 → 复现 Stage 3 → 扩展 Stage 3 → 端到端消融
```

## 5. 统一中间合同

### 5.1 Process Record

最低字段：process ID；activities/events/gateways；pools/lanes/actors；sequence
flows；activity label 的 action 与 business object；直接顺序、可达、分支、并行和
order relations；来源 BPMN hash 与解析器版本。

### 5.2 Rule Record

最低字段：sample ID、source text、clause spans、modality、actor、action、condition、
constraint、exception、actor-action map、order relations、schema/method/prompt/rule
version 与 provenance。

### 5.3 Violation Report

最低字段：process/rule ID；matching score；compliant 或一个/多个 violation type；
相关 activity、lane/actor、order pair；可复核证据；threshold/model version；运行
manifest 与输入 hash。

任何方法只有通过相同 canonical contract，才能进入同一评价表。

## 6. G0：数据与实验治理

| 任务 ID | 小任务 | 产物 | 当前状态 | 完成条件 |
|---|---|---|---|---|
| G0.1 | 建立唯一 Pipeline 与文档索引 | 本文、`docs/INDEX.md` | verified | Agent 入口唯一、旧路线移出活动入口 |
| G0.2 | 数据注册 | dataset registry/contract | partial | 每个数据集有来源、许可、hash、schema、split、用途 |
| G0.3 | 方法注册 | 方法 registry | partial | 每个正式方法有命令、状态、LLM 标记和版本 |
| G0.4 | 评价合同 | schema、normalization、evaluator | partial | 方法共享同一 Gold 和 evaluator |
| G0.5 | 复杂度合同 | 文本与 BPMN 复杂度字段 | blocked | 看结果前冻结分层规则 |
| G0.6 | Git checkpoint | 有意创建的版本点 | verified | `formal_experiment/` 已在 checkpoint `bfb0b8a` 纳入版本控制 |
| G0.7 | 前人比较注册表 | citation/method/data/code/license/metric/adapter matrix | ready | 每个引用结果可追到原表或本地重跑 manifest |
| G0.8 | 受控文本哈希可移植性 | 合同 `hash_mode` 声明 + gate 归一化 + 窄 `.gitattributes` + 回归测试 | verified | CRLF/LF 工作树对同一受控文本得到同一 canonical hash；未声明资产仍按原始字节；一字变化 fail closed；Sun modality 许可/溯源边界不变 |

外部数据集必须同时满足：来源/版本可定位、许可允许复用、hash 固定、标签兼容或有
人工协议、split 不泄漏、各方法使用同一测试样本、复杂集在运行结果前选定。

## 7. Stage 1：流程模型拆解

### 方法与 baseline

| ID | 方法 | 角色 |
|---|---|---|
| S1-P0 | 纯 BPMN XML 结构解析，保留原标签 | 结构下限 |
| S1-P1 | 简单 verb-object/规则标签解析 | 轻量非 LLM baseline |
| S1-P2 | Sun/Leopold-style 标签、模型上下文和结构分析 | 正式 Sun Stage 1 |
| S1-P3 | LLM 标签语义解析 | 可选扩展，Stage 2 完成前不启动 |

### 工作分解

| 任务 ID | 小任务 | 依赖 | 当前状态 | Definition of Done |
|---|---|---|---|---|
| S1.1 | BPMN 输入与 Process Record schema | G0.2 | **verified（2026-08-11）** | schema + fixtures + validator |
| S1.2 | activity/event/gateway/flow/lane 解析 | S1.1 | **verified（2026-08-11）** | 对测试 BPMN 稳定输出 + 7/7 GDPR 双跑确定性（s1_1_s1_4_determinism_v1） |
| S1.3 | actor/action/object 标签解析 | S1.2 | **verified（2026-08-13：P0/P1/P2 全部锁定；P2 为 post-Gold, target-aware Sun/Leopold-style 方法级重建（Gold 隔离推断、评分前锁定、评价后未调优；非 strict blind））** | P0/P1 表面切分；P2 语言分析（model context + style recognition + dependency 语义推导）；机器输出非 Gold（Gold 为人工裁决） |
| S1.4 | 控制流和可达关系 | S1.2 | **verified（2026-08-11）** | 分支、并行、顺序测试通过 |
| S1.5 | Stage 1 人工核对样本 | G0.2 | **verified（2026-08-13：7/7 裁决完成 → 用户授权 → 正式 Process Gold 冻结并发布 data/gold/stage1/process_records/stage1_process_gold_v1.json，独立 verifier VERIFIED）** | 固定样本（7 BPMN/45 activities/135 label fields，payload e88caf81…）与人工 Gold （用户 7/7 structure + 135/135 字段裁决后冻结） |
| S1.6 | baseline 评价 | S1.3-S1.5 | **verified（2026-08-13：P0/P1/P2 一次性正式评价完成；claim 已纠正为 fixed-GDPR7 描述性组件评价（非 held-out 泛化证据）；P2 语义 micro F1 0.8185、triple 0.4222 数值未变）** | 结构准确率和语义 P/R/F1 |
| S1.7 | 冻结正式 Stage 1 | S1.6 | **frozen（2026-08-13 用户明确授权：P2 锁定方法、P0/P1/P2 预测、原始指标、Stage 1 Process Gold、正式评价 capsule 全部冻结；授权 manifest s1_7_freezer_authorization_v1.manifest.json；未改 P2/未重算/零 LLM-API/未授权 Stage 3 Oracle）** | 输入/输出/方法/指标/hash 锁定 |

## 8. Stage 2：法规解析（当前主线）

### 8.1 Stage 2A：模态分类

类别：definition、obligation、prohibition、permission。候选 baseline：多数类/随机、
关键词、BiLSTM、CNN/TextCNN、通用/法律域 BERT、Sun BERT-TextCNN、LLM、
分类器 + LLM fallback。主表只保留有代表性的不同范式，同类变体放附录。

### 8.2 Stage 2B：六要素抽取

候选 baseline：marker/regex、spaCy/dependency rules、Sun CoreNLP +
Tregex/Tsurgeon + reconstructed markers、token classifier/CRF（仅在训练 Gold
足够时）、LLM、Sun + field-level LLM fallback。

### 8.3 Stage 2 完整方法

> 2026-08-08 起正式命名直观化（§8.8.3）：`B0 / sun_rule_only → Rules-Only`（纯规则法）、
> `H1 / sun_llm_fallback → Rules+LLM-Repair`（规则+LLM 修复）、`D1 / direct_llm →
> Direct-LLM`（直接 LLM）。新文档一律用正式命名；机器 ID 与 legacy 代号仅用于代码/
> 注册表兼容。Legacy 代号映射：B0 / `sun_rule_only`、H1 / `sun_llm_fallback`、
> D1 / `direct_llm`。

| Legacy 代号 | 正式命名 | 机器 ID | 含义 | 当前状态 |
|---|---|---|---|---|
| B0 | **Rules-Only**（纯规则法） | `sun_rule_only` | 非 LLM 传统流水线：BERT-TextCNN 模态分类 + CoreNLP/Tregex/Tsurgeon 六要素抽取（Sun Stage 2 方法级重建） | B0-R0–R3 verified；B0-R4 formal candidate verified（2026-08-10，Gold-blind runner 绑 formal input v2，双跑语义 byte-identical，主口径 F1 0.71865 与 R3 快照一致）且方法门禁已由用户授权 （methods.json formal_status=ready）；B0-R5 blocked on 正式结果发布 |
| H1 | **Rules+LLM-Repair**（规则+LLM 修复） | `sun_llm_fallback` | 同一 Rules-Only，仅按预注册 trigger 修复失败/不确定字段 | **对照方法（不再深究，2026-08-08 用户确认，§8.8.1）**；development 机制已验证，全量 150 运行主口径 F1 0.7621 vs B0 0.7986（净负） |
| D1 | **Direct-LLM**（直接 LLM） | `direct_llm` | LLM 直接生成同一 Rule Record（端到端，不读取 B0 预测） | D1-R0–R3 verified（主方法，粗 Gold F1 0.8726）；D1-R4/R5 blocked on formal Gold |

正式主表的最低方法覆盖为：简单规则下限、一个强监督学习 baseline、完整 B0、H1、
D1。模态分类与六要素抽取分别选方法，不能用一个只做分类的 baseline 冒充完整
Stage 2。训练 Gold 不足时，CRF/token classifier 只列为条件性扩展，不为凑数量
制造不可训练的 baseline。

### 8.4 数据轨道与复杂度

| 轨道 | 数据 | 用途 | Claim 边界 |
|---|---|---|---|
| S2-R1 | Sun 官方 modality 数据 | 模态分类复现 | development schema/split 已锁定；许可未知，禁止再分发或提前提升为 formal |
| S2-R2 | 项目固定 EStG-150 | 六要素主测试 | 项目独立重建，不是 Sun 原 150 |
| S2-C | GDPR、可复用 Luxembourg 语料、Barrientos 等复杂文本 | 外部验证 | 标签需映射或人工裁决 |

复杂度字段至少包括：长度、clause 数、dependency depth、actor/action 数、
condition/constraint/exception 的数量与嵌套、被动语态、隐含 actor、跨句引用、
原语言/翻译标记。

### 8.5 Stage 2 工作分解

| 任务 ID | 小任务 | 依赖 | 当前状态 | Definition of Done |
|---|---|---|---|---|
| S2.1 | 官方 modality 数据 ingestion/schema/license/split | G0.2 | **verified；A/B-R1/C-R1/D 全部通过** | development machine gate 交叉验证来源、合同、schema、quarantine、hash、split 与许可；formal use 仍未解锁 |
| S2.2 | EStG-150 人工裁决 | human-owned | **verified (2026-08-06)**：150/150 adjudicated（用户 2026-07-18 完成的裁决经用户授权从 56d2b03 历史快照恢复至活动 v2 文件，freeze validator 通过） | 150/150 adjudicated，freeze validator 通过 |
| S2.3 | 重建 public marker lexicon | S2.1 | **verified；英文 public-source v1 已锁定** | 来源、规则、hash、dev-only 扩展策略固定 |
| S2.4 | 完成 BERT-TextCNN | S2.1 | ready after separate dispatch；本轮未启动 | 训练、dev 选择、test 评价可复现 |
| S2.5 | 完成 CoreNLP/Tregex/Tsurgeon extractor | S2.3 | blocked | 六要素规则和 fixtures 通过 |
| S2.6 | 组合并验证完整 B0 | S2.4-S2.5 | blocked | 不调用 LLM，输出 canonical Rule Record |
| S2.7 | 实现代表性非 LLM baseline | S2.1/S2.2 | blocked | 相同输入和 evaluator 可运行 |
| S2.8 | 预注册 H1 trigger/merge/call budget | S2.6 | **不再推进（2026-08-08）**：H1 降级为对照方法（§8.8.1），对照所需机制（development wiring、canary、全量 150 运行 commit 74614e3）已具备；正式 trigger 预注册取消 | 对照臂结果可复现：主口径 F1 0.7621 vs B0 0.7986（净负，证据支持 D1-primary 决策 A）；机制工作正常但 trigger+repair 配方增加 FP 而非召回 |
| S2.9 | 锁定 D1 prompt/few-shot/model/budget | S2.2 | **verified (2026-08-06)** | **D1 侧达成（2026-08-06，D1-R2）**：v6 prompt hash 3aa64877 固定、model/sampling/seed 策略与预算合同锁定于 `configs/models/estg150_d1_active_registry_v1.json`；Gold 不可见（few-shot 为合成 fixture、runner 不读 Gold）；S2.2 frozen（150/150 adjudicated，2026-08-06 恢复后 freeze validator 通过），依赖满足 |
| S2.10 | 主数据组件评价 | S2.2/S2.6-S2.9 | **verified（2026-08-11，授权后 DoD）**：按用户授权 G0.4 口径，模态与六字段指标分别报告已真实完成——主报告=句子级粗粒度五 span 字段（P/R/F1）+ 单独四分类 modality label（accuracy/macro-F1/per-class）逐方法报告，细粒度五字段诊断/对照；modality evidence-span 结构性 unavailable 为授权口径明示项（不置零不纳入 aggregate）；三方法 formal capsule 全部独立 verifier 通过；正式三方法比较报告 stage2_formal_three_method_comparison_v1 已发布并自校验 | 模态与六字段指标分别报告（授权口径完成；历史六字段 aggregate 仅 development provenance） |
| S2.11 | 复杂法律语料集冻结 | G0.5 | **verified / frozen / Gold published（2026-08-17）**：Checkpoint G 完成 proposal v3 用户确认、importer v3 原子导入与 freeze 36/36；随后正式发布 `data/gold/stage2/s2_11_complex_corpus_formal_gold_v1.json`（SHA-256 `039ae8b2…`，36/36、0 unresolved、0 blocked）。Gold 逐记录等值复制 adjudicated canonical decisions，不增加/推断/改写标签、span、actor-action map 或 order relation；provenance 明示 `deepseek_offline_proposal_v3` + `user_batch_confirmation`（reviewer=hyc、无 revisions），不得表述为独立专家从零标注。版本化 schema/publisher/manifest/export/capsule/独立 verifier 已建立，publisher fail-closed 覆盖确认事件、proposal、reviewer、freeze、source/proposal drift；重放 byte-identical。提交资产只含 source path/file/text hashes、坐标与必要标签，第三方原文继续 local-only；零 LLM/API；未创建 predictions/results/Gold Rule Records，未启动 Oracle。 | 数据资格、canonical 裁决、冻结与正式 Gold 发布全部验证；S2.11 DoD 完成。 |
| S2.12 | 复杂度分层与误差分析 | S2.10/S2.11 | **partial；zero-API arm complete；两个 API arms pending explicit authorization（2026-08-18）**；**runner wiring READY（2026-08-22，零 API 零网络）**：36 条固定 ID 的 Gold-blind 正式输入仅提交 source locator/file/text hashes，不含 Gold label/span/decision。读取 Gold 前已锁定并运行 `sun_rule_only`（B0 v10a、CPU、0 API/0 network、cost=$0），预测锁定后才用 frozen S2.11 Gold 与 evaluator v2/G0.4 parity 口径评价：overall modality acc/macro-F1=`0.638889/0.535461`，span P/R/F1=`0.862319/0.802721/0.831453`；L1=31、L2=5、L3=0（no samples，不报性能）。这是**单一 zero-API arm**，不是三方法比较；未据 Gold/结果调整方法、规则、prompt 或 threshold。API preflight v1 在 0 次调用下重建最终 payload：direct_llm=36、sun_llm_fallback=27（总 63；配置绝对 call cap 108）、单次/总请求体≤17,493/749,805 UTF-8 bytes、本地 Legal-BERT proxy tokens 单次/总≤4,960/207,468（明确非 DeepSeek billing tokens）、output cap 4,096/call 与 258,048 total、retry=0；模型 `deepseek-v4-pro` 与 prompt/config/payload hashes 全锁定。2026-08-22 runner wiring 批次：实现 `scripts/run_s2_12_direct_llm_v1.py`（36 calls）与 `scripts/run_s2_12_sun_llm_fallback_v1.py`（27 calls、frozen plan、transport capture）、`configs/s2_12_fallback_trigger_plan_v1.json`（自锁定 preflight 触发集派生、replay byte-identical）、共享契约 `src/bpc_hybrid/s2_12_execution.py`（63 payload 逐条重建比对、授权合同、Beijing off-peak 时段、payload-locked fake transport、原子发布、文本/密钥 containment）、授权 schema `configs/schemas/s2_12_api_authorization_v1.schema.json`、独立 verifier `scripts/verify_s2_12_runner_wiring.py`、21 项 focused tests（fake transport、fail-closed；零网络）。官方价格复核：2026-08-19/20 上调（v4-pro input cache-miss 0.435→0.66/1.32、output 0.87→1.98/3.96），USD cap 重算 84.18（peak）/42.09（off-peak）并更新授权申请 v3；**RUNNER READY / API NOT AUTHORIZED / ZERO CALLS**；**2026-08-22 runner safety v2（零 API 零网络）**：per-call PayloadLock（每次真实调用前重建实际 body SHA + sample/clause/order 核验，fake/real 共用）、usage 捕获与真实成本计算（cache hit/miss 拆分，缺失时保守 cache-miss；cost_usd 不再硬编码 0）、per-call caps + off-peak（每次调用前检查，运行中进入 peak 即停）、append-only hash-chained 账本 + resume（不重复已调用 payload、篡改拒绝）、预注册 stage 合同（D-CAL 1 / D-REST 35；F-1/F-2/F-3 9/9/9；`--stage-id`/`--auth-file`/`--resume-from-ledger`，任意 `--start` 拒绝）、`.env` 禁读（`LLMConfig.from_env(load_project_env=False)`）、每 arm 独立 runner hash 绑定（fallback 不再与 direct 比较）、授权 schema v1.1.0（stage 绑定）、离线授权事件 builder（`build_s2_12_auth_event_v1.py`，无原句拒绝/dry-run/本轮不 apply）、独立 verifier `verify_s2_12_runner_safety_v2.py`（RUNNER SAFETY V2 VERIFIED / API NOT AUTHORIZED / ZERO CALLS）。API 状态保持 API BLOCKED / ZERO CALLS；真实调用仍待用户授权句 + 授权文件。 | 零 API arm 与分层评价完成；runner wiring 就绪（63/63 payload SHA 核验）；API arms 仍 pending explicit authorization；当前 SEP-C2 续作只保留 Direct-LLM 与 Rules-Only 两方法，Direct 真实预测/评价/两方法比较未完成前不冻结。历史三方法正式胶囊按历史协议保留。 |
| S2.13 | Stage 2 冻结 | S2.1-S2.12 | **blocked only on remaining S2.12 DoD**（2026-09-14 用户取消 H1；合同已适配，待 Direct-LLM 真实结果） | DoD 为 Rules-Only / Direct-LLM 的同输入评价、两方法合同和 S2.12 完成记录；`s2_12_two_method_contract_v1` 已把修复组从依赖中移除，但 Direct 未运行前 completion/freeze 仍为 false，其余输入/Gold/方法发布条件保持。 |

Stage 2 完成时，B0/H1/D1 和选定 baseline 必须共享 test IDs、Gold、schema、
normalization 和 evaluator，并分别报告 modality、phrase 和完整 Rule Record 指标。

### 8.6 B0 方法级复现修复 Pipeline（B0-R0–B0-R5）

本 Pipeline 执行用户在 2026-08-01 明确确认的口径：方法级独立复现可以进入正式
结论，不以取得作者原代码、原权重、完整私有词典或复现作者绝对数值为前提。实施
保持 Sun 的宽松方法边界，不用过度门禁把可解释的规则权衡卡死，但必须先排除确定性
代码错误。

**硬约束仅保留以下六项**：B0 不调用 LLM；不看最终 Gold 反向调规则；span 坐标有效
且文本可回指；同输入可确定性重放；B0/H1/D1 共享输入与 evaluator；每个代码/规则
批次有测试、manifest 或变更日志及 Git checkpoint。缺作者资产、单字段 P/R 回落、
规则词典规模不同或无法达到论文原数值只需披露，不单独阻断方法级复现。

| 任务 | 唯一目标 | 完成信号 | 状态 |
|---|---|---|---|
| B0-R0 | 将实际 B0 方法代码、配置、CoreNLP bridge 与测试整合到当前可审计主线；不整体合并历史数据/输出 | 当前分支存在唯一可运行入口，依赖和版本可追踪，旧 heuristic 不再冒充该入口 | verified |
| B0-R1 | 修复确定性实现错误：Action 任意字符截断、多词 Actor、字符中点分句、德英 cue 验证、错误 fallback、`<`/`<<`、Tsurgeon multi-match | 已完（2026-08-04）：R1-A..C3（半词 span、字符中点分句、Action 截断、required-end 守卫、fatal scope 拒绝）+ R1-E1/E2（主口径 evaluator + v10a/C3 重评）+ R1-ERR（错误分析）+ 七个 §8.6.1 子批次全部闭环（ACTION 已修/质量收益、SCOPE-DISAMBIG 实测拒绝记局限、ALIGN 已修伪 validated、BRIDGE 守卫+测试、ACTOR 已修 +0.0018、LEXICON-DECISION 已实施（用户授权）、CLAUSE-REVIEW 不改动）。DoD 三条验收线全部达成：无半词 span、无伪 validated、无未记录即被剪除的匹配 | **verified** |
| B0-R2 | 对照 Sun 核心方法：BERT-TextCNN、CoreNLP constituency、Tregex/Tsurgeon、公开抽取顺序和六字段输出 | 方法对照表逐项有实现/测试/已披露适配（docs/B0_R2_METHOD_CROSSWALK.md，11 元素）；重建 marker 与德英 adapter 允许使用并记录；`method_conformance_status` 已由用户授权（2026-08-04）改为 `verified_method_level_independent_reconstruction`，`sun_stage2_baseline_not_paper_faithful` blocker 已按设计解除（BLOCKERS 9→8）；Tsurgeon 为诚实非实现（fail-closed 守卫） | **verified（用户授权）** |
| B0-R3 | 在固定 development snapshot 上重跑并做错误分析 | 无 LLM；manifest 锁定代码/配置/输入/evaluator hash；报告 P/R/F1 与失败类型 | **verified（2026-08-04）**：56d2b03 快照运行完成（主口径 F1 0.71865，manifest `…r2_r3_lex_hist56d_v1/`，用户条件授权标记为论文依据候选）+ 最终态错误分析完成（docs/B0_ERROR_ANALYSIS.md §8：失败分布、constraint marker 归因、C2 cue 一致性、label 路由归因；两项不补项及原因记录） |
| B0-R4 | 在与 H1/D1 相同的冻结输入和 Gold 上运行 B0 | 三方法共享 IDs、schema、normalization、evaluator；输出不覆盖 | **formal candidate verified（2026-08-10）**：`run_estg150_b0_formal.py` Gold-blind candidate runner（只读 formal input v2 + 锁定方法资产，不读 data/gold/Layer E 裁决字段），150 条全量运行完成（outputs/development/b0_r4_formal_candidate_v1，claim_scope=formal_candidate_not_yet_authorized_as_formal_result），主口径 F1 0.71865（P 0.6845/R 0.7564，与 B0-R3 development 快照逐位一致=方法语义锁定），双跑语义 byte-identical（预测/主指标/错误分析/config 完全一致，仅性能计时字段不同），evaluator 独立于 runner；**formal promotion 已授权并应用（2026-08-10 用户明确授权：outputs/reports/sun_rule_only_method_gate_authorization_dry_run.json 提议正式应用：configs/methods.json sun_rule_only formal_status→ready、command_status→formal_ready_candidate_authorized；methods.json 其余方法/contract/Stage3/Gold/publication 均未动；release manifest v2 implementation hash 同步重发布）**；未写入正式 predictions/results |
| B0-R5 | 形成论文正式结论 | 结果可为正或负；明确写作“方法级独立复现”，并披露重建资产和适配差异 | **verified（2026-08-11）**：正式结论包 stage2_formal_conclusion_v1（d882a5e2…，verifier 16fd36f5 VERIFIED）+ 三方法正式比较报告（c9d76544…）；描述性字段级结论、无显著性推断、重建披露完整 |

**评价口径**：六字段抽取的 Sun 对照主表采用同字段任意非空字符交叠的
Precision/Recall/F1；不强制 clause alignment，不做一对一 assignment。该口径下
`modality` 只评价 evidence span，忽略标签，因此模态四分类必须另表报告 label
P/R/F1。strict exact、token overlap、clause alignment 和 actor-action edge 作为诊断
面板，不作为阻止方法级 B0 进入正式结论的最低分阈值。

**迭代规则**：B0-R1/R2 的候选允许出现字段间 precision/recall trade-off；不得仅因
一个字段回落就停止整个路线。Agent 必须记录变化、原因和已知代价，再由固定的 Sun
主口径与诊断面板共同判断是否保留。只有代码不正确、方法核心组件缺失、数据泄漏、
输出不可复现或比较口径不一致时才 fail closed。Pipeline 不预设最低 P/R/F1；修复后
仍然较低的结果属于可报告的方法局限。

### 8.6.1 B0-R1 当前子批次（依据 2026-08-04 错误分析）

`docs/B0_ERROR_ANALYSIS.md`（B0-R1-ERR）对 C3 注册 attempts 与 56d2b03 历史
Gold 做了逐 span 失败分类：79%（218/276）的 missed Gold span 内容被抽到其它
字段、80%（280/351）的错误预测压到其它字段 Gold 上；字段归属错误是压倒性失败
模式。据此，B0-R1 剩余工作拆为以下子批次，每批必须：focused tests →
`audit_project.py --with-tests` → 用 B0-R1-E2 同一协议（`sun_literal_overlap_evaluation@2.0.0`、
同一 canonical Gold、同一进程双评）重评 → 记录前后 delta 与原因 → `record_change.py`
→ 独立 commit + push：

| 子批次 | 内容 | 量化证据 | 可修性 | 预期影响 |
|---|---|---|---|---|
| B0-R1-ACTION | 修复 action span 吞并：`actor_action.py` `_subtree_span` 把 nsubj/全部依赖纳入 action，span 中位超 Gold 54 字符（192/212 matched 为过长） | constraint 143 个 missed 中 57 个仅被 action 覆盖；244 个 action 中 8 个以冠词开头 | **已修（2026-08-04）**：实测主口径 F1 +0.00005（持平），质量收益：主语开头 8→0、strict-exact action F1 3.0× | 边界质量修复；主口径非指标驱动项 |
| B0-R1-SCOPE-DISAMBIG | constraint↔condition 双向消歧（scope.py `_SURFACE_SCOPE` 与 Tregex 共享 cue） | 114 个 extra constraint 压 condition Gold、31 个反向；44 个同界双发（43 个双 tregex） | **已实测拒绝（2026-08-04）**：候选真实运行 F1 −0.0005，按迭代规则回退；根因=gold 对 "to the extent"/关系从句语义内部不一致 + registry 模式重叠（`to<<an|the` vs `to<<extent|purpose`），不读 Gold 前提下规则层不可安全消歧 | 记为方法局限；registry 模式复核需用户决策 |
| B0-R1-ALIGN | 德英 cue 验证：equal-count/split 路径"伪 validated"（两侧任意锚即 validated） | evidence 匹配 clause 上 label 准确率 79.3%（definition↔obligation 混淆为主） | **已修（2026-08-04）**：`_cross_validates` 语言学映射+否定极性+数字锚；validated 107→49、"无伪 validated" DoD 达成；主口径指标不变（F1 0.71024）；label 面板 −0.48pp（记录代价）；validated_split 42→0（记录副作用，留待细化） | modality label 面板提升未达成（实测微降），正确性缺陷已修 |
| B0-R1-BRIDGE | `<`/`<<` 关系算子与 Tsurgeon multi-match 消费（当前 registry 无 operation，风险潜伏） | SunPhraseRuleBatchBridgeMulti.java:91-103 单记录/多消费结构 | 可修（离线 fixture） | 消除潜伏错误源 |
| B0-R1-ACTOR | 多词 Actor 生产路径测试 + 依赖边查找修复 + under-extension 边界（C7） | 22 个 missed actor：8 个含词典词（依赖失败）、14 个词典无覆盖；modality evidence 80 个过短 | **已修（2026-08-04）**：clause 内全 nsubj 弧 + obl/by-to + 中心词词典校验；实测主口径 F1 +0.0018（0.71024→0.71205，本系列首个正向 delta），actor F1 0.616→0.670，8/8 漏抽找回；C7 过短边界未含在本批 | actor R 提升已验证；C7 另行跟进 |
| B0-R1-LEXICON-DECISION | actor 等词典扩展、代词/名词 Gold 语义裁决（如 "It" 作 actor） | 13 个无词典覆盖名词 + "It" 代词 | **已实施（2026-08-04 用户授权路径 b）**：13 名词以 `authorized_local_frozen_estg150_gap_2026_08_04` 来源加入词典（治理覆盖严格记录于 sources manifest/actor meta/manifest note/事件）；覆盖/未覆盖 P/R 分别报告（覆盖 47/48：P 0.692/R 0.979/F1 0.811；未覆盖 1/48=代词 "It"，需正式 Gold 裁决）；B0-R3 快照 F1 0.71865（+0.0085 vs 原） | actor R 0.958；唯一残余=代词语义 |
| B0-R1-CLAUSE-REVIEW | clause 规划失配复核（38/231 Gold clause 无 IoU≥0.5 配对） | 与 v2 主口径弱相关；58 个真正漏抽中仅 4 个在未配对 clause | **已复核（2026-08-04）：不改动**（v2 口径不依赖 clause 对齐；修复风险大于收益，C1/C2 批次已顺带观察） | 次要 |

B0-R3 的"固定快照重跑 + 错误分析"仍是正式结论的必要步骤：B0-R1-ERR 的分析为
development 快照提前执行，正式错误分析须在 B0-R2 后按同一主口径重做并登记。

### 8.7 D1 方法级复现修复 Pipeline（D1-R0–D1-R5）

与 §8.6 B0 Pipeline 同构、同门禁纪律。D1 是直接 LLM 方法，因此硬约束为：
**真实 LLM 调用必须逐批用户授权并记录硬预算上限与成本**；不看最终 Gold 反向调
prompt；span 坐标有效且文本可回指；同输入同配置可重放（prompt hash、model、
temperature/seed、max_tokens 全部记录进 manifest）；B0/H1/D1 共享输入与 evaluator；
每个 prompt/代码批次有 focused tests、manifest 或变更日志及 Git checkpoint。
缺作者资产、单字段 P/R 回落只需披露，不单独阻断方法级复现。

| 任务 | 唯一目标 | 完成信号 | 状态 |
|---|---|---|---|
| D1-R0 | 将实际 D1 方法（runner/prompt loader/canonical schema/attempts 产物/manifest）整合到当前可审计主线 | 唯一可运行入口 `run_direct_llm.py` + prompt loader + canonical schema；既有 s28_s29 产物 tracked 且可重评；prompt hash 记录于 manifest | ready |
| D1-R1 | 修复 D1 低召回（整体 R=0.665、constraint R=0.288）的确定性/合同缺陷：省略指令、few-shot 缺 constraint/condition、字段错标引导（99 个 constraint 内容进 action span） | 每个候选：prompt vN 变更 + focused tests + 预算内真实 pilot + 重评 delta + keep/reject 记录（见 §8.7.1） | **verified (2026-08-05)**：v6 KEEP；150 全量 0 事故，F1 0.7669→0.7735，constraint R 0.2881→0.4172；见 s27_d1_v6_verify_pass_150_hist56d_v1 |
| D1-R2 | 对照方法要求：prompt/model/budget 锁定（prompt hash 固定、预算上限合同、temperature/seed 记录）；S2.9 DoD（Gold 不可见、prompt hash 固定）达成 | config 锁定 + manifest 记录 | **verified (2026-08-06)**：`configs/models/estg150_d1_active_registry_v1.json` 锁定 v6 prompt（sha 3aa64877，与磁盘/loader/manifest 三方一致）、deepseek-v4-pro 钉死、temp 0/top_p 1/max_tokens 4096、seed 策略 unsupported_or_omitted、transport 配方（thinking-disabled、无 json_object）、共享输入与 evaluator hash、预算合同（逐批授权+`--max-calls` 硬上限 150）、D1-R1 运行登记；12 项 lock-config 测试含 S2.9 Gold 不可见核查（6 个 few-shot 合成 fixture 与 150 测试句零交叠）；§8.5 S2.9 行 DoD（D1 侧）达成，整行仍 partial（S2.2 未 frozen） |
| D1-R3 | 固定快照干净重跑 + 错误分析 | 无事故 transport；manifest 锁定代码/配置/输入/evaluator hash；报告 P/R/F1 与失败类型 | **verified (2026-08-06)**：锁定配方（estg150_d1_active_registry_v1.json 逐项一致）干净重跑 150/150 有效、0 事故；R1/R3 同一进程双评（sun_literal_overlap@2.0.0）R3 F1 0.7756（P 0.8793/R 0.6938）vs R1 0.7735（+0.0021），复现成功；失败类型分析（1055 gold span：matched 732、wrong_field 169 其中 constraint 100、not_extracted 154）见 docs/D1_ERROR_ANALYSIS.md §8 |
| D1-R4 | 与 B0/H1 相同冻结输入和 Gold 上正式比较 | 三方法共享 IDs、schema、normalization、evaluator；输出不覆盖 | **历史预测绑定核账（2026-08-10）**：D1-R3（s27_d1_v6_r3_clean_rerun_150_hist56d_v1）与 H1（s28d_h1_150_v4pro_v1）的 150 条 predictions 经 b0_d1_formal_readiness_v2 逐项核验——IDs 与 formal input v2 完全一致、输入文本逐条 hash 一致、prompt/model/sampling 与锁定配方一致、snapshot 完整且 schema-valid → **zero-API candidate 重评允许**（不重调 API）；未满足项=无；不把历史预测提升为 formal 结果，正式三方法比较仍待方法门禁（B0 已出授权 dry-run 包，D1/H1 需 LLM 授权） |
| D1-R5 | 形成论文正式结论 | 结果可为正或负；明确写作"方法级独立复现"，披露模型/prompt/预算与适配差异 | **verified（2026-08-11）**：正式结论包（同上）覆盖 D1；披露历史调用 150 + 新增 0、无显著性推断 |

**评价口径**：与 B0 相同——`sun_literal_overlap_evaluation@2.0.0` 主表 + 模态
label 另表。**迭代规则**：候选允许字段间 P/R trade-off；Agent 记录变化、原因与
已知代价，由固定主口径判定保留与否；修复后仍低的结果属可报告的方法局限。

### 8.7.1 D1-R1 子批次（依据 2026-08-04 错误分析，见 docs/D1_ERROR_ANALYSIS.md）

| 子批次 | 内容 | 量化证据 | 预期影响 |
|---|---|---|---|
| D1-R1-FIELD-TYPING | prompt 显式定义 constraint 类别（法律引用/时间/数量限制/"within the meaning of"/"pursuant to"/"subject to"）并禁止并入 action/condition；补 few-shot | 99 个 constraint 内容被 action 吞、16 个进 condition（合计 124 个落错字段） | **done (2026-08-05)**：v6=v5+规则25-27+Ex5/Ex6；pilot 19 配对 F1 +0.0155、constraint F1 +0.0547，KEEP |
| D1-R1-PROMPT-CONTRACT | 规则 14 由"不确定就省略"改为"列出所有候选，不确定的写入 unsupported_or_ambiguous"；补 constraint/condition/exception few-shot（当前 4 例中 condition 0 次、constraint 仅 1 例） | 91 个 constraint + 43 个 condition 完全未抽 | **covered by v5 lineage**：v5 规则 15-19（empty=absent、不确定入 unsupported_or_ambiguous）+ v6 规则 25-27；150 全量实测 constraint R 0.288→0.417 |
| D1-R1-VERIFY-PASS | 两遍法：第二遍仅问"是否遗漏 constraint/condition/exception"（可选，预算翻倍） | 同上 | **done (2026-08-05)**：v6 150 全量 150/150 有效、0 事故；F1 0.7735（+0.0066）、constraint R 0.4172（+0.1291）；两遍法未启用（预算纪律，候选已达标） |
| D1-R1-CLEAN-RERUN | 排除 s28_s29 运行事故影响（lost 104 / recovery 26 / retry 0） | manifest `d1_runtime_incident` | **satisfied by VERIFY-PASS run**：0 lost/recovery/retry，manifest 无 runtime_incident |

每批纪律：prompt/代码变更 + focused tests → 预算内真实 pilot（**逐批用户授权**）
→ 同口径重评 → delta 与原因记录 → keep/reject → `record_change.py` → 独立 commit
+ push。禁止读 Gold 反向调 prompt。

### 8.7.2 论文 Table 1 / Table 2 最终口径（PAPER-FINAL-REPAIR，2026-09-21，零 API）

**2026-09-26 用户最终采用决定**：下列 Table 1 的 0.8378/0.7631 已复核固定，
后续不替换或重跑；方法名称中的 Sun 指本项目本地重建。详细来源见 C54。

**Table 1（Stage 2 六要素抽取，EStG-150 coarse sentence view）**
`formal_experiment/outputs/reports/stage2_table1_paper_final_v1.{json,md}`
（生成器 `scripts/build_stage2_table1_paper_final_v1.py`，只读冻结 Gold + 冻结两臂预测）。

| Method | Modality macro-F1 | Actor | Action | Condition | Constraint | Exception | **Overall (pooled 5)** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sun 方法本地重建（Rules-Only） | 0.713 | **0.820** | 0.893 | 0.774 | 0.618 | **0.880** | 0.7631 |
| Ours（Direct-LLM） | **0.769** | 0.758 | **0.944** | **0.838** | **0.743** | 0.762 | **0.8378** |

Δ Overall = **+7.47 pp**（P 0.6984/R 0.8410 → P 0.8695/R 0.8083）。
**口径修正（必须随表注写清）**：`evaluate_span_metrics` 原先的 `overall` 是**六字段**
pooled 聚合，把 G0.4 合同声明不可用、且由 coarse transform 以 clause span 合成出来的
modality span 计入（1 条/记录），既违约又混入近常数项；现以
`pooled_five_span_fields`（仅 actor/action/condition/constraint/exception 的 micro pooled
P/R/F1）为**唯一合同口径 overall**，旧六字段聚合降为显式 `NON_CANONICAL` provenance 字段。
modality 一律以四类 **label** macro-F1 单列，绝不并入 overall。
**同时必须承认**：Ours 并非全面领先——actor（−6.24 pp）与 exception（−11.81 pp）仍低于
Sun，且 pooled F1 下 Sun 的 recall（0.8410）高于 Ours（0.8083）。论文只能写"多数要素更优
+ 总体更高 + 两项更低"，不得写全面胜出。

**Table 2（Prompt Design 消融，同 prompt 家族同口径）**
`formal_experiment/outputs/reports/stage2_table2_prompt_ablation_paper_final_v1.{json,md}`
（生成器 `scripts/build_stage2_table2_prompt_ablation_v1.py`）。

| Prompt arm | Overall (pooled 5) | Δ vs Full (pp) | 有效输出 |
|---|---:|---:|---:|
| Full (all modules) | 0.8224 | — | 150/150 |
| Full − Examples (E) | 0.8142 | −0.83 | 150/150 |
| Full − Guidance (S) | 0.8299 | +0.74 | 150/150 |
| Full − JSON discipline (J) | 0.8268 | +0.43 | 150/150 |

**这是"最后一次消融"，结论必须如实写**：三项删除在 pooled overall 上**都没有 95% CI
排除 0**；可分离的字段效应**符号不一致**（−E 使 Condition F1 **+4.22 pp** [+1.33,+7.78]；
−J 使 Action F1 **+3.47 pp** [+0.67,+6.80]）。因此**不能**声称"三个模块各自提升总体
F1"。结构性限制同时写入报告：E 与 S 承载重叠信息，leave-one-out 只能测"移除另一载体后
的残差"；coarse view 仅 459 个 Gold span，功效不足以分离小效应；每臂仅 1 次重复。
**J 的处置**：四臂合法输出均 150/150，删除 J 不降低 overall，故 J 一律作为
**Base Output Contract（接口/合法性保证）**呈现，**不得**再写成提升准确率的 prompt 模块。
**禁止**：本轮之后不再为让某个模块变正而调 prompt、不再新增模块或消融臂。



## 8.8 导师汇报确认与方向锁定（2026-08-08）

本节记录 2026-08-08 向导师汇报后确认的四项事实与执行决定。本节是后续论文写作、
消融实验与各 Agent 派工的唯一依据；任何与此冲突的动作必须先更新本节并给出新证据。

### 8.8.1 事实 1：H1（Rules+LLM-Repair）不再深究，仅作为对照

**决定**：H1 降级为**对照方法**，不再作为主方法投入。论文保留其对照臂结果，
用于证明"无证据约束的选择性 LLM 修复会净负，反衬证据约束的必要性"。

**为什么效果不好**（依据 commit `74614e3`，2026-08-08 全量 150 运行，
deepseek-v4-pro，用户授权 150 calls）：
- 主口径（句子级粗 Gold）F1 **0.7621 vs B0 0.7986（−0.0365，净负）**；细 Gold
  F1 0.6875 vs 0.7186（同样净负）；
- LLM 修复在 actor 字段**过度抽取**：P 0.7077→0.2754，actor spans 65→167；
- 其余 5 个字段持平或微升；机制本身工作正常（103 accepted / 89 changed /
  gate=True / 0 incidents），问题出在 **trigger+repair 配方增加 FP 而非召回**。

**困难点**：
1. **trigger 与失败错位**：trigger 只看到推理时信号（低置信、结构冲突、候选多义），
   而 B0 压倒性失败模式是"字段归属错误"（79% 的 missed Gold span 内容被抽到其它
   字段）——这类失败在推理时不可见，Gold-blind trigger 无法对准真正需要修复的样本；
2. **修复难以约束在字段边界内**：请求补 actor 时 LLM 倾向扩大 span、补多个候选，
   把 precision 打穿（actor spans 65→167 的直接原因）；
3. **收益上限受限**：修复收益被触发子集覆盖限制，成本-收益曲线不利。

**优化方向（仅当未来恢复时参考，当前不执行）**：
- 保守修复配方：actor span 长度上限 + 候选数上限 + 修复后 verbatim 回指强制校验；
- 用 risk-coverage 曲线在 development 上选择触发子集，而非全触发；
- 字段级白名单 + patch 前后 diff 约束。

**论文表述**：H1 作为对照臂报告"选择性混合"的负结果；不声称 H1 是贡献。

### 8.8.2 事实 2：B0（Rules-Only）/ D1（Direct-LLM）局限性（列表 + 例子）

**B0（纯规则法，非 LLM）局限性**：
1. **字段归属错误主导**（C1 action 吞并）：matched action 中 192/212 过长、中位超
   Gold 54 字符。例：`"the data shall be processed only to the extent necessary"`
   中整段被并入 action，而 Gold 将 `"to the extent necessary"` 归 constraint。
2. **constraint↔condition 双向混淆**（C2：114 个 extra constraint 压 condition Gold、
   31 个反向），例：`"to the extent"` 双触发。SCOPE-DISAMBIG 候选实测 −0.0005 已回退：
   "不读 Gold"前提下规则层不可安全消歧 → 记为**方法局限**而非代码缺陷。
3. **词典覆盖受限**：13 个无词典覆盖名词漏抽（successor/spouse/child/developers/
   bank/body/society/owners/shareholders/beneficiary 等）；代词 `"It"` 作 actor 需
   Gold 语义裁决（未覆盖 1/48）。
4. **定义范围差异**：我们的 constraint Gold 302 个中仅 13 个（4%）符合 Sun 公开
   marker 定义（Sun 自身仅 35 个）→ 定义口径差异是低分主因之一；Sun-marker 收敛后
   B0 constraint R=1.0 (13/13)、condition R=0.989 (91/92)。
5. **缺 Sun 原资产**：Tsurgeon 为诚实非实现（fail-closed 守卫）；词典规模与分词
   机制为已披露适配。

**D1（直接 LLM）局限性**：
1. **constraint 召回弱**：R1 基线 R=0.288（99 个 constraint 内容进 action span、
   91 个完全未抽）；v6 修至 0.417 仍为最弱字段；R3 失败类型：wrong_field 169
   （constraint 100）+ not_extracted 154（constraint 69）。
2. **actor 泛化误抽**：历史 run P=0.594（69 pred vs 48 gold）。例：表述
   `"the body shall ensure…"` 中抽取无 Gold 交叠的泛指主语作为 actor。
3. **高精度保守型**：细 Gold 口径 P 0.879 vs B0 0.685，但 R 0.694 vs 0.756——
   "宁可漏抽不误抽"在低资源字段（exception/constraint）牺牲召回。
4. **依赖真实 API 与预算合同**：每批需用户授权 + `--max-calls` 硬上限；可复现性
   依赖 transport 配方（thinking-disabled、无 json_object、temp 0）与 prompt hash
   三方锁定。

**对照矩阵（主口径粗 Gold，2026-08-07，同一 Gold 同一 evaluator）**：

| 口径 | B0 P/R/F1 | D1 P/R/F1 | 谁领先 | 可解释原因 |
|---|---|---|---|---|
| 句子级粗 Gold（609 spans，主口径） | 0.7309 / 0.8801 / **0.7986** | 0.9012 / 0.8456 / **0.8726** | **D1（F1 +0.074）** | D1 高精度保持；B0 召回更高（R 0.8801 vs 0.8456） |
| 细 Gold（1055 spans，对照口径） | 0.6845 / 0.7564 / **0.7186** | 0.8793 / 0.6938 / **0.7756** | **D1（F1 +0.057）** | B0 字段归属错误拖低 P；D1 保守漏抽拖低 R |

**结论**：B0 靠规则覆盖全面（R 高）、D1 靠 LLM 精度高（P 高），错误模式互补
（B0 字段归属错、D1 低召回）；但 H1 实测净负（§8.8.1）说明"简单混合"不成立，
主叙事以 D1 为方法主体、B0 为强对照。

### 8.8.3 事实 3：方法命名直观化（B0/H1/D1 → 正式命名）

导师指出 B0/H1/D1 代号不直观，审阅人无法快速理解。自 2026-08-08 起统一使用：

| Legacy 代号 | 机器 ID（不变） | 正式命名（英文） | 中文名 | 一句话本质 |
|---|---|---|---|---|
| B0 | `sun_rule_only` | **Rules-Only** | 纯规则法 | 非 LLM 传统流水线（BERT-TextCNN 分类 + CoreNLP/Tregex 规则抽取），Sun Stage 2 方法级重建 |
| H1 | `sun_llm_fallback` | **Rules+LLM-Repair** | 规则+LLM 修复 | 规则为主，预注册触发器按字段让 LLM 修复；**对照方法** |
| D1 | `direct_llm` | **Direct-LLM** | 直接 LLM | 纯 LLM 端到端生成六要素 Rule Record，不读取规则预测 |

**写作规则**：新文档一律用正式命名；旧文档/代码引用时首次出现给出映射
（如"Direct-LLM（旧代号 D1）"）；机器注册表 `configs/methods.json` 保留 legacy
`id`（代码兼容）并新增 `paper_label` 字段承载正式命名。

### 8.8.4 事实 4：与 Barrientos et al. (2026) 严格对比 + 贡献细模块化（重要）

**背景**：Barrientos et al. (2026) 是**本项目直接借鉴来源**（LLM 结构化输出、
验证、受控词汇、归一化与评估纪律）；Sun et al. (2024) 是三阶段方法学主干。
导师要求：(a) 严格对比 Barrientos 的方法；(b) 消融实验做丰富——"哪个模块缺了
我的不行；把他的模块换成我的模块更好"；(c) 列表跑数据，逐项说明我的好在哪、
他的好在哪、综合谁好；(d) 把贡献拆成细模块讲清楚，**不能只说"调用了 LLM"**
（prompt 只是其中一小部分），方法章节要支撑 4–5 页。

**已锁定的对比事实**（见 `docs/research/BARRIENTOS_BORROWING_AUDIT_2026-07-12.md`
与 `docs/research/BARRIENTOS_LLM_ROLE.md`）：
1. **任务与 schema 不同**：Barrientos=change-impact 表示（precondition/norms/
   temporal_validity）；我们=Sun 六要素 span 抽取（modality/actor/action/condition/
   constraint/exception + evidence span）→ **schema 不能照搬**（已锁定）。
2. **modality 3 类 vs 4 类**：Barrientos 缺 `definition`；我们的 prompt 显式扩展
   4 类并定义触发语义（"主要目的是定义"而非"包含定义"）。
3. **受控词汇**：Barrientos 44 模式 4 维度（control_flow/resource/data/time）约束
   normalized view；我们=public marker lexicon（64 marker）+ 受控 six-field schema
   （normalized view 受控，原文 span 不覆盖）。
4. **评估纪律（来源分层）**：Barrientos 论文正文对自动化 Step 1 报告 P/R/F1、
   strict-JSON 合法性与 5 次独立运行的 self-consistency；其随附专家标注协议另用
   semantic coverage / structural encoding / deontic correctness 与
   **style-equivalent alignment**（表达不同但语义相同算正确），κ=0.52 属于专家对
   20 个变更影响判断的 NC/OC/NE 一致性，不是 LLM 输出一致性。我们=span overlap
   主口径 + 细/粗 Gold 双口径 + 失败类型归因 + label 面板；style-equivalent 只能
   作为有明确适配合同的辅助敏感性分析，不能冒充 Barrientos 论文的主指标。
5. **工程纪律**：strict JSON schema、temperature 0、稳定性测试、deterministic
   normalization → 我们已实现（D1-R2 锁定配方、预算合同、prompt hash 三方一致）。
6. **稳定性实验差距（2026-08-20 原文纠正）**：Barrientos 论文是 36 条 requirement
   的完整流程独立运行 **5 次**，Step 1 用 pairwise distance≤2 的 self-consistency；
   “20 条×2 版本×2 专家=80 annotations”来自专家标注协议，**不是 20 条×20 次模型
   重跑**。我们当前 temp0 + prompt hash 已锁定，但同协议正式重跑仍**尚未执行** →
   列入消融计划 AB-9。

**贡献细模块化（论文方法章节 4–5 页的叙述骨架；禁止只写"调用了 LLM"）**：

Direct-LLM 拆为 8 个可单独叙述/消融的模块：
1. **六要素 schema 与证据契约**：verbatim span 回指（`text == source[start:end]`）、
   clause 内 span、actor-action map、order relations、unsupported_or_ambiguous 兜底
   ——契约决定输出可验证性；
2. **prompt 工程（v1→v6 版本线）**：constraint 六子类显式定义（法律引用/时间/数量/
   "within the meaning of"/"pursuant to"/"subject to"）、empty=absent 语义、禁止并入
   action/condition 指令；v6 实测 constraint R 0.288→0.417（+0.129）。**prompt 只是
   贡献的一部分，不是全部**；
3. **few-shot 合成 fixture 工程**：6 个合成样例覆盖 condition/constraint/exception
   缺口，与 150 测试句零交叠（Gold 不可见保障，S2.9 DoD）；
4. **结构化输出 transport 配方**：thinking-disabled、无 json_object、max_tokens
   4096、temp0/top_p1——150/150 有效、0 事故的可复现调用层；
5. **确定性校验与后处理链**：relay-schema adapter + canonical validator（格式/回指/
   字段权限）+ span canonicalizer（fail-closed unique exact-text re-anchor）——把 LLM
   输出转成严格契约数据，坏 span/clause/边丢弃并审计；2026-08-30 固定响应离线
   单因素结果：去 adapter ΔF1=0，去 canonicalizer ΔF1=−0.772（149/150 被 validator
   拒绝），去 validator ΔF1=0且上游无效记录=0；后两项的“0增量”只适用于当前响应，
   不取消其兼容/安全职责；
6. **预算与授权合同**：逐批授权、`--max-calls` 硬上限、manifest 记录 llm_calls/
   max_calls/模型/采样/失败率；
7. **双口径评价协议**：`sun_literal_overlap@2.0.0` 主口径 + 细 Gold（1055 spans）/
   粗 Gold（609 spans，Sun 句子级粒度）双口径 + 失败类型归因（matched/wrong_field/
   not_extracted）；
8. **可复现性资产**：prompt hash 三方锁定（磁盘/loader/manifest）、注册表
   `configs/models/estg150_d1_active_registry_v1.json`。

Rules-Only 的可叙述模块：public marker lexicon 重建（来源/哈希/版本）、模态分类器
（BERT-TextCNN 重建 + marker 路由 + 德英 cue 验证）、CoreNLP 句法/依赖抽取、Tregex
模式注册表、Tsurgeon fail-closed 守卫、actor/action 归属解析（§8.6.1 各批次成果）。

**消融实验矩阵（导师要求"列表跑数据"，全部需逐批用户授权或离线可跑）**：

**2026-09-06 用户撤回与定位澄清（研究定位以此为准；下列 2026-09-05 段仅为历史记录，不得执行）**：用户明确澄清：此前准备的“直接使用 Barrientos 原始 `FULL / NO-PATTERNS` 两份提示、在本项目冻结 36 条输入上运行 360 次（36×2×5）”方案是对其意图的误解，**已经撤回，不得执行**。研究定位维持不变：Sun et al. (2024) 是整体改进对象与三阶段方法主干；Barrientos et al. (2026) 仅作为 **Stage 2 的方法借鉴来源**（LLM 结构化输出、验证、受控词汇、归一化与评估纪律）；本项目**不承担“必须整体优于 Barrientos”**的对比任务，也不把原样运行其原生提示作为正式对照。下述 2026-09-05 段落及其配套产物（`scripts/run_barrientos_paper_ablation_v1.py`、`configs/ablations/barrientos_paper_ablation_v1.json`、预检报告与 22 项 focused tests，checkpoint `2c5181e`）**保留为历史证据，状态=withdrawn——不再作为待授权执行计划**；真实 API=0 的事实不变；任何恢复执行需用户另行明确授权与独立预算。Barrientos 相关已完成证据（2026-08-29 D/E 1140/1140、2026-08-30 后处理单因素与 450-call Prompt 单因素、AB-1/2/3/5/5b/9）与 AB-4/AB-10 缺口按 §8.8.4 消融纪律继续有效，不受本次撤回影响。
**2026-09-05 用户收敛要求：模仿 Barrientos 原文的消融设计。** S2-BARR-4 当前
新增子任务为原生 `FULL / NO-PATTERNS` 提示对照的离线执行准备；此前已完成的
AB 结果保留为证据，不再以凑齐所有开关为目标追加实验。已核对 PDF 第8–11页及
原始 notebook：无词表版本还移除了控制流互斥/冗余规则，故它是原 artifact
两提示对照，不宣称纯词表单因素；schema 合法与44模式清单合法分开统计。
两臂各36条×5次，合计360次新调用，采用当前 DeepSeek 配方（原文GPT-4.1的模型
替换复现），不复用历史基线；非法模式/维度错配/非空可用性/明确命名的稳定性
代理作为结果，不与六字段F1跨表比较。执行入口
`scripts/run_barrientos_paper_ablation_v1.py`、独立合同
`configs/ablations/barrientos_paper_ablation_v1.json` 已离线准备，API尚未授权/未运行，
费用硬上限USD9.70，retry=0。原文PDF/XML消融源代码已定位，但需冻结成对的
法规版本/形式化/delta输入及另行模型/上传预算；未启动Stage 3 LLM或改变门禁。
精确来源差异与完整执行预检见
`outputs/reports/barrientos_paper_ablation_preflight_v1.{json,md}`。

| 消融 ID | 变量 | 我的设计 vs 替换方案 | 回答的问题 | 状态 |
|---|---|---|---|---|
| AB-1 | 详细语义规则 | v6 全字段定义 vs 只删规则9–19、25–27 | 字段语义、被动/指代与边界规则的贡献 | **严格单因素完成（2026-08-30）**：full F1 0.7719；删除后 0.7759（Δ+0.0040），未观察到总体正增益；但 action F1 Δ−0.0518，存在字段间权衡 |
| AB-2 | 语义示例 | 6 合成 fixture vs 以纯 key/type 结构模板替换六个语义示例 | 排除输出格式崩溃后，语义示例本身的价值 | **严格单因素完成（2026-08-30）**：full F1 0.7719；替换后 0.7650（Δ−0.0069），actor F1 Δ−0.1317；支持小幅总体正贡献 |
| AB-3 | modality 类别 | 4 类（Sun）vs 3 类（Barrientos 投影） | `definition` 类的独立价值 | **离线覆盖投影完成**：4类 39/97/62/33；三类共享97/62/33；排除 definition 造成39/231=16.88%覆盖损失；非准确率优劣 |
| AB-4 | 受控词汇 | 六字段受控 schema vs 移植 Barrientos 44 模式 dual-view | 我的归一化约束 vs 他的 pattern 约束 | **模块替换已跑、纯受控词汇单因素未隔离**：两个 replacement arm 接口不兼容为0；不能当 Barrientos 原方法无效 |
| AB-5 | 校验链 | 完整 adapter/canonicalizer/validator vs 每次只移除一个 | 确定性后处理对有效率的贡献 | **固定 D-full-0813 raw 离线完成（2026-08-30）**：full 0.772；−adapter 0.772；−canonicalizer 0（149/150 invalid）；−validator 0.772（0 invalid observed）；同一150/Gold/evaluator，零 API，回顾性 development |
| AB-5b | 显式 JSON 契约 | 完整提示 vs 只删 schema/固定键/仅JSON等明文纪律，保留全部语义规则与六个示例 | 明文输出纪律在示例已给出格式时是否仍有增量 | **严格单因素完成（2026-08-30）**：删除后 F1 0.7790（Δ+0.0071），合法输出率仍 1.0；当前模型/数据/保留示例条件下未测得正增益 |
| AB-6 | transport | thinking-disabled/无 json_object vs 默认配方 | 事故率与可复现性 | 已有 0 事故证据，可整理 |
| AB-7 | 评价口径 | 细 Gold vs 粗 Gold vs Sun-marker 收敛 | 口径敏感性（已有 0.7186/0.7986、0.7756/0.8726） | 有证据，整理成表 |
| AB-8 | B0 模块 | lexicon 逐来源（Sleimi/LexNLP/Wiktionary）、marker 路由、跨语言验证开关 | 每个规则模块的边际贡献 | 部分有证据（R1 各批次） |
| AB-9 | 稳定性 | 5 次独立重跑 agreement / self-consistency（对齐 Barrientos 论文的 5-run 设计） | 成本-收益的稳定性保证 | **完成（36条×3臂×5）**：只作为同一 arm 输出一致性；不得当跨方法准确率 |
| AB-10 | style-equivalent 评估 | 开启 vs 关闭该评估维度 | 评估鲁棒性（借鉴 Barrientos 的贡献） | 待实现 |

**Prompt 单因素真实执行完成（2026-08-30，用户授权 450 calls）**：目录
`prompts/sun_compat/ablation_v2/` 固定三条臂：`D-no-semantic-examples-0813`
（六个语义示例→纯结构模板）、`D-no-semantic-guidance-0813`（仅删规则9–19、
25–27）、`D-no-explicit-json-contract-0813`（仅删显式 JSON/schema 纪律）。三臂
各150条，复用已完成且同 release 的 `D-full-0813` 为基线，不重复付费；实际
450/450 calls、失败0、input/output=1,444,632/368,212 tokens、cost=$3.3650，未触及
USD cap 13.430。总体 F1：full 0.7719；语义示例→结构模板 0.7650（Δ−0.0069）；
删除详细语义规则 0.7759（Δ+0.0040）；删除显式 JSON 纪律 0.7790（Δ+0.0071，合法率
仍1.0）。因此仅语义示例显示小幅总体正贡献；其余两模块在此固定数据上没有显示总体
正增益，但存在逐字段权衡，不能写成普遍无用或显著性结论。报告：
`outputs/reports/d1_prompt_factorial_results_v1.{json,md}`。

**输出要求**：每项消融至少一行结论表——「我的模块 vs 换 Barrientos 模块 vs 去掉
模块」三列指标，并写"我的好在哪里 / 他的好在哪里 / 综合谁好及原因 / 可比较性限制
或口径差异"。跨 schema、跨任务或跨口径的 AB-3/AB-4 类比较不得由单一数字宣称谁更
好，只能报告各自口径内结果和定性适配结论。全部以 development/授权预算内真实或离线
方式运行；涉及真实 LLM 的消融逐批授权。

### 8.9 最终执行总控（2026-08-08 审计收敛）

本节固定全项目的唯一执行路线。既有 `G0.x`、`S1.x`、`S2.x`、`B0-Rx`、`D1-Rx`、
`S3.x`、`PWx` 与 `E00/E10/E01/E11` 是唯一可派工、可记录、可进入 manifest 的任务
ID；不得另建 A/B/C/P/D 等第二套主键。`Rules-Only`、`Rules+LLM-Repair`、`Direct-LLM`
是论文名称，B0/H1/D1 仅为 legacy 追溯代号。

**G0 核账，不重复锁定。**下列资产已存在且不得重新定义：canonical Rule Record
schema、`sun_literal_overlap_evaluation@2.0.0` evaluator、粗 Gold 主口径/细 Gold
对照口径的用户决定、D1 的 prompt/model/sampling/transport/budget 锁定，以及 B0/H1
的 development manifest 纪律。只补以下三个缺口：

| 挂靠 ID | 最小补缺 | 规则 |
|---|---|---|
| G0.4 | 双口径评价合同 | 固化粗 Gold 主口径、细 Gold 对照口径、适用指标和禁止混表规则；不改 Gold |
| G0.4 | shared comparison capsule | 复用现有 150 输入资产及 hash（D1 registry 的 `c7dffcc4...` 为候选引用），新建 manifest 而非复制输入；显式绑定 B0/H1/D1 的 input/Gold/schema/normalization/evaluator hash |
| G0.7 | Barrientos adapter 注册 | 记录 schema/标签/数据/指标/许可、adapter 边界、映射、hash 与可比较性限制 |

**Stage 2 正式比较与 Barrientos 专项。**B0-R4/D1-R4 是正式共同运行，B0-R5/D1-R5
才形成论文结论；H1 已停止优化，仅作为对照。H1 的正式对照来源不得预设：formal
Gold 发布后，先核验现有 Gold-blind prediction capsule 是否与 shared comparison capsule
逐项一致；一致时仅做 zero-API 重评并新登记 manifest，不一致时只能在用户逐批授权和
硬预算下重跑。不得把现有 development 数字提升为 formal。

Barrientos 专项使用 `S2-BARR-*` 作为 S2 工作包子任务名，不取代现有 S2 主任务：

| 子任务 | 目的 | 最低产物/门禁 |
|---|---|---|
| S2-BARR-1 | G0.7 的专项适配注册 | schema、标签、数据、指标、许可、adapter 边界和 hash |
| S2-BARR-2 | Barrientos-style adapter | 输出映射到 canonical Rule Record；映射测试和 manifest 完整 |
| S2-BARR-3 | 同数据比较 | 仅在 shared capsule 后运行；报告质量、逐字段、合法率、稳定性、成本、延迟和 Stage 3 可用性 |
| S2-BARR-4 | AB-1--AB-10 模块消融 | 按现有状态分批；真实 LLM 项逐批授权，跨任务项保留可比较性限制 |
| S2-BARR-5 | 稳定性与 style-equivalent 补充 | 重跑协议、成本与评价边界冻结 |

Barrientos 专项轨道与 §10.3 证据等级正交：`L1` 表示同一 frozen IDs/Gold/schema/evaluator
的专项共同重跑，通常可满足 C1 但仍需逐项核验；`L2` 表示资格、许可、标签映射和 Gold
均通过的共同复杂数据轨道，可能属于 C1 或 C2；`L3` 仅引用论文报告值，通常只能按 C3
背景处理。跨任务、跨 Stage 或不可统一口径的比较始终是 C4，禁止用数值直接证明优劣。

**Stage 3 双轨与 formal Gold 交叉门禁。**可受控并行的仅是 `S3.1 -> S3.2/S3.3` 的
BPMN 身份与 Gold 治理，以及明确标注 development 的 wrapper/baseline 实现准备。S3.4
的正式完成仍依赖 S1.7/S2.13；S3.7 必须区分 development Oracle 和正式 Oracle 主表：
前者只能使用 development 输入/Gold 且不得进入正式结果，后者还要求 formal Gold
publication、S1.7、S2.13 和 S3.4-S3.6 完整完成。S3.8-S3.11 不得提前启动。

```text
S2.2 annotation freeze + route locked + stage2 dataset locked
  + S3.1/S3.2/S3.3 完成并经授权重锁 stage3.status
  + freeze policy 重核 + publication gate 精确进入白名单
    -> formal Gold publication
    -> shared comparison capsule
    -> B0-R4 / D1-R4 / 条件成立的 H1 zero-API re-evaluation
    -> S2.10 -> S2.12 -> S2.13
    -> S3.7 formal Oracle -> S3.8/S3.9 -> S3.10 -> S3.11
```

完成 S3.1-S3.3 不自动授权 `stage3.status=locked`；状态翻转必须通过合同变更、完整检查、
日志、Git checkpoint 和明确授权。最终归因只使用既有 E00/E10/E01/E11，且 Oracle 与
end-to-end 必须分表。论文仅并行 PW1-PW6；PW7-PW9 只由对应 formal manifest 回填。

## 9. Stage 3：匹配、违规检测与分类

### 9.1 Stage 3A：规则—流程匹配

候选方法：TF-IDF/BM25、Winter fitness/cost、Sun semantic matching、embedding +
graph features、cross-encoder/reranker、LLM 或 Sun-candidate + LLM rerank。
主指标保留 AP/MAP，可增加 Recall@k 和 nDCG@k。

### 9.2 Stage 3B：违规检测与错误类型分类

共享标签：compliant/none、missing_action、incorrect_actor、out_of_order。
候选方法：词法 + BPMN 图规则、Winter、Sun、embedding + graph rules、LLM、
Sun candidate + LLM verifier。复杂扩展允许 multi-label。

Stage 3 正式主表至少覆盖：词法/检索下限、Winter、完整 Sun、一个现代
embedding/graph baseline；LLM 与 Hybrid 在 Oracle 非 LLM 比较稳定后加入。每种
方法必须同时说明它解决 Stage 3A、Stage 3B，还是二者，避免把 matching 分数和
错误类型分类指标混成一个结果。

### 9.3 数据轨道

| 轨道 | 数据 | 设计 |
|---|---|---|
| S3-R | Sun-compatible GDPR replication | 识别原 4 BPMN；单一人工注入违规 + negatives |
| S3-X1 | 本地全部 7 个 GDPR BPMN | 明确称 all-seven extension |
| S3-X2 | Barrientos 三个复杂 BPMN | 只在共享标签上直接比较；其它标签单列 |
| S3-X3 | 后续公开复杂流程 | 必须通过 G0 门禁 |

### 9.4 Oracle 与 end-to-end

Oracle Stage 3 使用 Gold Rule/Process Records，只评价 Stage 3；end-to-end 使用
B0/H1/D1 的预测 Rule Records，评价误差传播。两种结果必须分表。

### 9.5 Stage 3 工作分解

| 任务 ID | 小任务 | 依赖 | 当前状态 | Definition of Done |
|---|---|---|---|---|
| S3.1 | 确定原 4 个/扩展 7 个 GDPR BPMN | G0.2 | **verified（2026-08-08）**：7 个 Winter-provenance GDPR BPMN 从 56d2b03 checkpoint 以 byte-exact（LF）恢复至 `data/input/stage1_stage3/gdpr7/`；合同 `configs/datasets/stage1_stage3_gdpr7_v1.json`（user-approved 2026-07-18）hash 全匹配；`verify_stage1_stage3_gdpr7.py` 通过（7 byte-exact BPMN、45 activities、135 blank label fields）；audit pass `stage1_formal_bpmn_membership_locked`；claim=all-seven extension（非 Sun 原 4） | 文件名、hash、claim 固定 |
| S3.2 | 锁定 matching Gold | S3.1 | **decision Gold 已发布（2026-08-08 裁决冻结；2026-08-10 随 formal Gold publication 发布 `data/gold/stage3/stage3_matching_gold_v1.json`，25 条，与 frozen correction `3310d624…` 一致）**：11 相关 / 14 不相关（含负例）；correction 文件 data/development/human_review/stage3_gold_annotation_human_correction_v1.json；冻结 manifest s32_s33_gold_annotation_freeze_v1.manifest.json；这些 relevance decisions ≠ Gold Rule Records | rule-process relevance decision Gold 完整；Gold Rule Records 另行人工裁决 |
| S3.3 | 锁定 violation Gold | S3.1 | **decision Gold 已发布（2026-08-08 裁决冻结；2026-08-10 随 formal Gold publication 发布 `data/gold/stage3/stage3_violation_gold_v1.json`，33 条，与 frozen correction 一致）**：missing_action 11 / incorrect_actor 11 / out_of_order 11；negative（合规）判定随 matching 负例与裁决记录；这些 type/evidence decisions ≠ Gold Rule Records | type、evidence、negative decision Gold 完整；Gold Rule Records 另行人工裁决 |
| S3.4 | 完成 Winter wrapper | S1.7/S2.13 | **development wrapper verified（2026-08-08）**：Winter 2020 原型语义转写 + 可移植重放（reachability 双模式、manifest 1.1.0、export index、evidence capsule outputs/evidence/s34_winter_stage3_development_v3_clean\|prototype_literal/）；修复后重放 v3_clean/v3_prototype_literal（inference pack check_type 路由、公共 evaluator 口径）；DEV_ONLY：MAP 0.6429/binary F1 0.6111、violation macro 0.373（两模式 out_of_order 无差异）；**S1.7 依赖已满足（2026-08-13 frozen）；formal completion 仍 blocked on S2.13** | formal canonical I/O + reproducible command |
| S3.5 | 完成 Sun Stage 3 | S3.1-S3.3 | **development implementation verified（2026-08-08）**：Def 4-7 方法级独立重建 + 契约/评价修复（Gold-blind inference pack、check_type 路由、Def 6 论文存在性语义（C=process actor+bs_obj 近似披露）、unobservable 按 check_type 统计（v2：33→10，before/after 对照）、sensitivity 真实重算）；run s35_sun_stage3_development_v2（evidence capsule 含 5 方法 comparison）；DEV_ONLY：MAP 0.8175、binary F1 0.0（如实）、violation macro 0.389/exact 0.364/unobs 10（均较 v1 口径修正）；**S1.7 依赖已满足（2026-08-13 frozen）；formal completion 仍 blocked on S2.13** | 不再是 fixture approximation；formal Oracle 主表待 formal Gold 门禁 |
| S3.6 | 完成代表性非 LLM baseline | S3.2/S3.3 | **development baseline verified（2026-08-08）**：BM25（v3 candidate-specific：MAP 0.6595/binary F1 0.0；v1/v2 因忽略候选文本标记 superseded_invalid_candidate_agnostic_similarity，不入有效比较/论文）+ TF-IDF/SVD（v2 保留：MAP 0.5881/macro 0.542，经验证不受共享 scorer ID 修复影响）；双域 sims（action/actor 独立候选池）、真实 ID 映射、check_type 路由、sensitivity 重实例化 scorer；阈值 0.5=fixed development setting（非 blind preregistration）；evidence capsule v3/v2；**S1.7 依赖已满足（2026-08-13 frozen）；formal completion 仍 blocked on S2.13** | 相同 Gold/evaluator；正式 baseline 待 formal Oracle 门禁 |
| S3.7 | Oracle Stage 3 比较 | S3.4-S3.6 + formal Gold publication | **Gold Rule Records 已发布 + Oracle 隔离运行已跑（2026-09-09，零 API）**：9 个 GDPR rule IDs 的正式 Gold Rule Records 已发布（`data/gold/stage3/gdpr7_gold_rule_records_v1.json`，92 条规范条目，独立 verifier 32 项通过）；人工规则已接入检查器（`human_rules` 来源臂）；Oracle 隔离运行 `s3_oracle_gold_rules_v1` 在 33 条人工 Gold 上 missing_action P/R/F1=1.000，incorrect_actor/out_of_order 因动作映射低于 gamma 与确认条目无 order_relations 而不可观察（分母如实保留，根因诊断已记录）；四类合成面板四后端结果已出。**仍未完成**：S2.13 freeze（blocked on S2.12 API arms）、S3.4-S3.6 正式 promotion、正式 Oracle 主表授权（`formal_s3_7_authorization` 未授予）。**重要**：v7 及更早 readiness capsule 的 Gold-Rule-Record 三态探测会因新文件按设计 fail closed，需重建 successor capsule；不得用其 `exist=false` 旧结论。 | 正式 Oracle 主表隔离 Stage 3；development 结果不得替代本表 |
| S3.8 | LLM/Hybrid Stage 3 预注册与实现 | S3.7 | blocked | prompt、预算、重复次数固定 |
| S3.9 | 复杂 BPMN 与多违规扩展（synthetic controlled-error extension） | G0.5/S3.7/现有方法运行 | **development panel verified（2026-08-22，零 API）**：在冻结 GDPR-7 上锁定 30 个 `synthetic_controlled_error_extension` 变体（missing_action 10 / incorrect_actor 10 / out_of_order 10；每变体原始 BPMN byte-unchanged、exactly-one-error、结构校验全过、replay byte-identical；规则绑定来自冻结 inference pack）→ 用同一 evaluator 在 30 条 panel 上运行 Winter / Sun / BM25 / TF-IDF（DEV_ONLY：Winter macro 0.333/exact 0.333；Sun macro 0.333/exact 0.200/unobs 8；BM25 macro 0.333/exact 0.333/unobs 10；TF-IDF macro 0.635/exact 0.533/unobs 6；最高 TF-IDF）。**这是受控实验 panel，不得并入 33 条人工 Gold，不得冒充 Oracle。** | 复杂度和标签在结果前冻结；synthetic panel 与人工 Gold 分开报告 |
| S3.9-EXT | Stage 3 新违规类别扩展（development-only synthetic controlled extension v2，零 API） | S3.9 现有四后端 | **development panel verified（2026-08-31）**：新增 4 类违规 × 10 = 40 变体（prohibited_action_present / required_condition_not_enforced / constraint_violated / exception_not_handled）。**选择动机已锁定**：原三类只覆盖 action presence / actor / order；四类分别补足 prohibition modality、condition、constraint、exception 的 Stage 3 下游消费者，并满足语义不重复、exactly-one-error 可控变异、BPMN 表面可观察三项原则；这是最小字段覆盖扩展，不是穷尽性法律违规分类。每变体含 synthetic compliant control + 单一目标错误 variant（源 BPMN byte-unchanged、exactly-one-error、replay byte-identical、规则绑定+六要素字段锁定自冻结 inference pack）；四方法共享同一套新类型公式，仅替换各自已有相似度后端（Winter-style extension gamma 0.4 / Sun-style extension gamma 0.8 / BM25 extension gamma 0.8 / TF-IDF-SVD extension gamma 0.5；gamma_ext=0.5 统一冻结）；同一 evaluator 输出（DEV_ONLY：Winter macro 0.655/exact 0.550/unobs 17；Sun 0.333/0.300/unobs 28；BM25 0.226/0.150/unobs 28；TF-IDF 0.379/0.325/unobs 27）。**Winter/Sun 原论文未定义这四类，报告一律写 `Winter-style extension` / `Sun-style extension`，不得声称原生能力；synthetic panel 不得并入 33 条人工 Gold，不得冒充 Oracle。** | 40 变体面板+对照+四方法 panel 与对比报告；17 项 focused tests；零 API 审计 |
| S3.9-EXT-REPORT | Stage 3 收尾：paired control-plus-variant 评价与报告修正（零 API，零重跑） | S3.9-EXT | **reporting closed（2026-08-31）**：仅从持久化四方法 predictions 离线新增 80 对象配对评价（40 control Gold=none + 40 variant；control 预测由持久化 control_scores 按原阈值 gamma_ext=0.5 与固定 EXTENDED_TYPES 优先级重建，未改阈值/顺序/样本）；paired 口径（DEV_ONLY）：Winter 5-class acc 0.425 / variant exact 0.550 / control FP rate 0.500 / paired acc 0.225；Sun 0.263 / 0.300 / 0.125 / 0.175；BM25 0.250 / 0.150 / 0.000 / 0.100；TF-IDF 0.338 / 0.325 / 0.275 / 0.300。七类 overview 改为仅 7 个 per-class F1（无联合 Macro-F1/Exact/Unobservable，注明 v1/v2 双 panel 差异）；结论收紧：prohibited=可行性支持、constraint=部分支持、condition/exception=主要揭示可观察性与映射瓶颈，不写“全部四类都证明下游价值”；报告生成器 --report-only 确定性重放；原三类 Gold/schema/预测、40 变体、四方法原始产物字节不变 | 配对评价+报告修正+39 项 focused tests；零 API 审计 |
| S3.9-EXT-GAP | 四类扩展 Winter-vs-v3 同条件归因与修复（零 API） | S3.9-EXT-REPORT / S3-EXTENDED-V3 | **superseded by S3.9-EXT-REPAIR-V2（2026-09-11）**：结论作废，原因是其 `v3+0.4` 诊断臂没有真正改变 v3 内部阈值（外层记录 0.4、实际 v3 仍 0.8），不能支持阈值因果结论；实现与产物保留为历史记录，D1/D2/D3 的代码证据仍有效 | —— |
| S3.9-EXT-REPAIR-V2 | S3 扩展实验限定返修：真实 v3 阈值臂、空白规范化隔离臂、去强制解析/比较门后继臂（零 API） | S3.9-EXT-GAP | **completed（2026-09-11）**：三臂各跑一次 80 实例。A（v3 内部真 0.4）32/40 行决策改变、25 行预测改变、A 22 正确 / Macro-F1 0.5690 / 对照误报 24；B（关闭 v3 只加空白折叠）与冻结 Winter 臂 35/40 决策相同、仅 2 行预测翻转且恰为此前归因于结构匹配的 2 例；C（v3 0.8+回退 0.4+无强制解析+比较门）对照误报 20→14、成对 11→13、变体正确 19→18。本面板 0 行触发并列或 undetermined，"歧义修复"影响无法分离；比较门纠正的是"未比较就宣布合规"，不是提高分数 | `outputs/development/s3_extended_repair_v2_v1/`（plan/predictions/metrics/diagnostics/manifest）+ 25 项 focused tests；零 API |
| S3.9-EXT-REAL-CASE | 真实/派生案例的 Stage 1→3 端到端开发性案例（SIM 卡入网，零 API） | S3.9-EXT-REPAIR-V2、S3-REAL-RULE-DIAGNOSTIC-CORRECTIONS | **completed（2026-09-11，零 API）**：主案例 = Barrientos Sun 派生 SIM 流程 × **5 条 v2 非空规则**（r8/r9/r10/r11/r13；r12 作需求删除背景单列，r9/v1 与 r12/v2 空文本排除）；**A**=项目锁定非 LLM 基线 B0 v10a（`run_b0_batch_v10`，CoreNLP+Tregex+BERT-TextCNN，英文句经德语合同分类器槽 pass-through）+ 冻结 Sun 式三类检测（15 检查），**B**=既有真实 LLM 预测（repeat-01）+ 与 A 完全相同的三类检测（15 检查），**C**=与 B 同一份 Stage 2 与三类结果 + 已验收四类修复（REPAIR-V2 C 臂 `RepairedExtendedScorerV2` + 比较门；35 检查，含 15 条继承行）。结果：A 3 violation/10 undetermined/2 not_applicable；B 5/8/2；C 10/23/2（2026-09-11 第二轮组件修正后）。与 5 条开发参考判断对照：r9、r10 检出；r8、r11、r13 全部 `undetermined`（原因分别为 `action_mapping_below_gamma`、`no_mapped_rule_order_endpoints`、`empty_rule_condition`），**未检出项如实保留、未改参考判断、未删样本**。**5 个最小修复对照全部未消除问题**（r9 加活动后 missing_action 仍 1.0；r10 改归属后 frozen Def6 的 min-over-{actors ∪ business objects} 仍 1.0；r11/r13/r8 因动作映射/规则字段/后端能力无法运行）；**修复件经独立结构核验确认真正表达了修复**（`fix_expressed=true`，r8 另记任务级计时≠进程级终止的范围限制）→ 失败定位在方法侧而非修复件侧。补充案例：Figure 10 重建件（我方重建，非作者模型；18 项歧义有 provenance）上的非 LLM 基线 28 检查（7 violation/21 undetermined，已统一使用同一套四类实现）；真实 LLM 组缺失（Table 13 文本与既有预测输入存在大小写/标点差异，span 不可复用，未授权重新调用）。产物 `outputs/development/sim_case_c1/`、报告 `outputs/reports/sim_case_c1_{checklist,results,supplement}.*`、标注图 `sim_case_c1_result_figure.svg`；36 项 focused tests；零 API | 逐条状态与计数、阶段归因、信息去向、修复对照与独立核验、标注图与论文小节齐备；未完成项（LLM 组补充案例、更多正常对照、正式 Oracle）如实列出 |
| S3.10 | end-to-end 误差传播 | S2.13/S3.7 | blocked | B0/H1/D1 进入同一 Stage 3 |
| S3.11 | Stage 3 冻结 | S3.1-S3.10 | blocked | 数据、方法、Gold、指标、manifest 完整 |

### 9.6 S3.9-EXT-REAL-CASE 小步骤状态（2026-09-12 第四轮四个缺口收尾，实时状态见 PROJECT_AUDIT）

| 步骤 | 要解决的问题 | 具体产物 | 验收条件 | 实际状态 |
|---|---|---|---|---|
| **P1** | 抽取缺失、适配去向、角色绑定回退与不适用是否混淆 | `capsule.rules[*].chain`（raw→proj→adapted→consumed 计数与值级变化）、`capsule.rules[*].sides[*].checks[*].machine_status`、投影 diagnostics | 空动作不写成 not_applicable；多值部分丢失不被写成全部 carried；显式 actor-action 关系不被凭空组合；声明角色绑定进入最终 actors/pairs | **完成**：A 组 r9/r13 evaluated status=undetermined，machine_status=not_applicable 保留；r10 A 的 2 动作/2 条件记 partially_carried_by_declared_policy；r11 A/B 显式 pair actor 绑定为 Phone company，保留 original/bound_from/value_changes；r8 null actor 仍为 invalid_in_raw_no_valid_pair；无有效 map 时首个动作仅供存在性检查，不自动成义务。 |
| **P2** | 机器报警是否等于参考问题检出；五个固定问题证据链是否完整 | `capsule.comparison[*].groups[*].machine_alarms/correspondence_*/assessment_details`、`process_facts` | 报警与评价分栏；同类 violation 无证据不算命中；不满足作用域/字段条件的修复件不进入有效分母 | **完成**：r9 记录抽取动作、missing_action best candidate/similarity、Sign contract 仅锚点、流程清单无 verify/correctness；r10 逐候选列出 Activity ID/owner，Activate SIM card→Customer，Send SIM card→Phone company；r11 只有映射到 consent/request personal data 的 out_of_order 报警才对应，missing_action 不替代；r13 记录 50 EUR 位于 actor、condition/constraint 为空、threshold alarm evidence 空；r8 只用 model-side time/termination 与 process-scope facts 判定。有效修复分母仍为 r9/r10/r11 共 3 件。 |
| **P3** | 受影响路径是否重跑且计数/复用一致 | `outputs/development/sim_case_c1/run_v1/{plan,capsule,rows,manifest}.json/jsonl`、`outputs/reports/sim_case_c1_results.{json,md}` | A/B 同一公共 Stage 1 与适配政策；B/C 原三类逐项一致；计数来自实际结果 | **完成**：A 15 检查 3/0/12/0（机器计数 3/0/10/2）；B 15 检查 5/2/8/0；C 35 检查 10/2/23/0。参考对应 A 0 有证据/3 未证实/2 无报警，B/C 2/3/0。r11 端点仍未低于 gamma 映射，r13 condition 仍为空。 |
| **P4** | 图、报告、论文与修复来源是否同一结果一致 | 报告 JSON/MD、`sim_case_c1_result_figure.svg`、`paper/SIM_CASE_SECTION_v1.md` | 修复前后统一 C_original/C_repaired；流程图标出真实连线/网关/条件标签；实际渲染可读；A/B/C 分开展示 | **完成**：修复表、报告、论文均写 C_original 到 C_repaired；SVG 从只读 BPMNDI 渲染 26 条 sequence flow 连线、网关、Debt < 100 条件标签和稳定节点，r9 缺失活动占位符明确不属于原模型，r10/r11/r13/r8 标记全部读取 capsule；Chromium 检查 1800x4495，无文本越界/重叠；聚焦测试 36 passed。 |

本轮只执行上述四个缺口修正；未启动正式 Oracle、S3.10/S3.11、冻结、完整测试或真实 LLM/API 调用。

## 10. 实验矩阵

### 10.1 组件实验

| 实验 | 固定 | 改变 | 回答问题 |
|---|---|---|---|
| EXP-S1 | BPMN 与 Process Gold | Stage 1 方法 | 流程解析可靠性 |
| EXP-S2A | modality 数据与 Gold | 分类 baseline | 句子级分类能力 |
| EXP-S2B | EStG-150 与 span Gold | 抽取 baseline | 六要素抽取能力 |
| EXP-S3-O | Gold Process/Rule Records | Stage 3 方法 | Stage 3 独立能力 |
| EXP-S2-E2E | 固定 Sun Stage 1/3 | B0/H1/D1 | Stage 2 误差传播 |

### 10.2 最终归因消融

| ID | Stage 2 | Stage 3 | 作用 |
|---|---|---|---|
| E00 | Sun | Sun | 完整 Sun 重建基线 |
| E10 | 最佳 Stage 2 改进 | Sun | Stage 2 单独贡献 |
| E01 | Sun | 最佳 Stage 3 改进 | Stage 3 单独贡献 |
| E11 | 最佳 Stage 2 改进 | 最佳 Stage 3 改进 | 完整改进系统与交互 |

### 10.3 与前人结果比较的四级证据

| 级别 | 做法 | 是否允许直接宣称优劣 |
|---|---|---|
| C1 同测集重跑 | 前人方法和本项目方法跑同一 frozen IDs/Gold/evaluator | 可以，是主比较 |
| C2 官方数据复现 | 在前人公开数据上独立重跑，并完整记录版本与 split | 可以，但只限该数据轨道 |
| C3 论文报告值 | 只抄录论文原表，数据/split/evaluator 未完全统一 | 只能描述，不能作严格显著性结论 |
| C4 跨阶段/跨任务 | Stage 2 与 Stage 3，或标签/指标不同 | 禁止用数值高低证明方法优劣 |

Sun 在 Stage 2 与 Stage 3 使用的输入、Gold 和指标不是同一评价问题，必须分表。
如果 Sun 或其引用文献有公开数据，先通过 G0 数据门禁，再把前人方法与本项目方法
共同重跑；不能把“本项目复杂集上的 LLM 结果”直接减去“前人简单集上的论文数字”
当作提升。前人比较注册表至少记录：论文版本、阶段、数据版本、样本范围、标签、
split、指标定义、源码/权重可得性、许可、适配器、复现忠实度和本地 manifest。

## 11. 评价与统计控制

- 所有方法共享 frozen IDs、Gold、schema、normalization 和 evaluator；
- train/dev/test 与 few-shot examples 隔离；
- threshold、prompt、marker 和 fallback trigger 只在 train/dev 确定；
- LLM 报告模型版本、temperature、重复次数、成本、延迟和失败率；
- 复杂度分层在看 test 结果前冻结；
- 同时报总体、逐类、置信区间/显著性和错误案例；
- 负结果照实报告，不通过改 Gold、阈值或删样本制造优势。

## 12. 实施里程碑与当前主线

| 里程碑 | 内容 | 当前状态 |
|---|---|---|
| P0 | Pipeline、文档入口与目录治理 | verified；日志/检查制度已有回归测试保护 |
| P1 | Stage 2 数据、Gold、复杂度合同 | 主数据与 Gold 已完成：EStG-150 150/150 adjudicated（2026-08-06）、formal Gold 已发布（2026-08-10）；**复杂度合同 G0.5 与复杂语料资格 S2.11 仍未完成**（2026-08-15 核账） |
| P2 | 完整 B0（Rules-Only） | **方法、正式 arm 与比较证据已完成**：B0-R0–R4 verified、B0-R5 正式结论 2026-08-11 交付（`b0_formal_arm_v1` claim_scope=formal、独立 verifier 通过）；B0-R5 的论文写作部分由 PW7 回填，无剩余实验任务 |
| P3 | Stage 2 多 baseline | **三方法正式比较已完成**（`stage2_formal_three_method_comparison_v1`，2026-08-11）；复杂数据扩展未完成（S2.11 blocked） |
| P4 | Rules+LLM-Repair（对照）/ Direct-LLM 与 Stage 2 复杂集 | Direct-LLM：**正式 arm 已发布**（`direct_llm_formal_arm_v1`，2026-08-11，zero-API）；Rules+LLM-Repair：**comparison-only（§8.8.1）**，H1 正式 arm 已发布为对照臂；复杂集（S2.11）仍 blocked |
| P5 | Stage 1 完整实现与评价 | **S1.1–S1.7 已完成（S1.7 frozen，2026-08-13 用户授权；正式 Process Gold 已发布，P0/P1/P2 正式评价与 target-aware claim 已 verified）** |
| P6 | Sun/Winter Stage 3 复现 | **development 完成（S3.4/S3.5/S3.6）；formal 复现 blocked on S2.13 与缺失的 9 个 GDPR Gold Rule Records** |
| P7 | Stage 3 多 baseline 与复杂扩展 | blocked on P6；development baseline 已就绪（BM25 v3 / TF-IDF-SVD） |
| P8 | 最终端到端消融 | blocked on P4/P7 |
| P9 | 论文写作与可复现包 | 非结果章节 in_progress；结果/结论 blocked on P8 |

实验 Agent 应优先从 P1/P2 选择最小可验证任务；论文 Agent 只领取
`PW1`–`PW6` 中已解锁的非结果章节。未经合同变更，不要提前启动 Stage 3 LLM，
也不要因 Stage 3 尚未就绪而修改 Stage 2 Gold 门禁。

### 12.0 下一真实路径（2026-08-18 核账，见 `outputs/reports/s2_13_s3_7_transition_readiness_v8.json`（当前 fail-closed capsule；v7 及更早为 byte-exact 历史 provenance））

`final_experiment_ready=true` 仅代表 Stage 2 三方法正式评价/最终指标机器门禁
就绪；S1.7 已 frozen（2026-08-13）但 **S2.13 仍 blocked、S3.7 正式 Oracle 未启动
未授权**。通往 S3.7 formal Oracle 的真实路径依次为：

1. **S2.11/G0.5/S2.12 完整依赖**：完成或经用户正式决策处理外部复杂语料许可、
   数据激活授权、3→4 标签映射、人工 Gold、G0.5 复杂度规则结果前冻结与
   Barrientos adapter（S2-BARR-2）；**当前决策入口为
   `outputs/reports/s2_11_formal_gold_v1.manifest.json` + `data/gold/stage2/s2_11_complex_corpus_formal_gold_v1.json`**（proposal/review 入口仍保留 `s2_11_proposal_report_v3.json` + `s2_11_batch_import_dry_run_v3.json`；Checkpoint B 打开空白 review surface；Checkpoint C 封闭 review 人口 40/4/36；Checkpoint E1 建立 canonical v2 模型；Checkpoint F 生成 proposal v3 并完成六条定点校正；Checkpoint G 用户确认 proposal v3 → importer v3 `--apply` 原子写入 36/36 adjudicated + freeze validator v3 frozen=true；本次正式 Gold publisher 从冻结 decisions 等值派生 36/36、独立 verifier 27 项全过、重放 byte-identical；**Checkpoint E3 交付 S2.12 plan/readiness v2，Checkpoint F 重跑 parity 并 re-bind readiness v3，Checkpoint G 刷新 readiness v3**）；候选运行 `outputs/reports/s2_11_candidate_run_v1.json`；Checkpoint A 应用门禁 `outputs/reports/s2_11_gates_applied_checkpoint_a_v1.json`；v6 及更早为历史安全基线）：论文许可已确认（CC BY 4.0，article-only，出版社 PDF 证据链
   hash 绑定）；artifact code/data 许可仍 unknown_pending_confirmation；
   映射选项 M1（modality identity candidate ONLY）已应用/M2（未应用）；
   **G0.5 已冻结**（`configs/g05_complexity_frozen_v1.json`，frozen_for_future_external_complex_corpora，密封 v6 链验证；draft 61938c99… 保留为历史，语义 hash 51a6e4fe… 永不使用）；v6 封闭 frozen 授权链
   （classify_frozen 无 caller-supplied validation result、每次调用从磁盘
   重验 manifest/授权事件/prior-results 证据，手工 64-hex 字典被拒）；历史
   capsule v3/v4/v5 固定 origin commit 锚点（31ac757d…/8e8b488e…/7883739…，
   硬编码 SHA-256 map，与 HEAD 无关）；adapter 为 hardened v6
   synthetic/shadow implementation verified（严格 mode 枚举、真实文件级
   evidence binding、formal_evidence_provenance、受控 scope 枚举、
   resolved-path 逃逸防护）；分离门禁 G1–G6（G1/G2/G3/G4/G6 已应用，G5=applied_review_surface_open；**S2.11=verified/frozen/Gold published（36/36；Gold SHA `039ae8b2…`）**；**S2.12=partial：Gold-blind input + `sun_rule_only` zero-API arm + evaluator v2 分层评价已完成，direct_llm/sun_llm_fallback 两个 API arms 只待显式授权；preflight v1 锁定 63 个 payload、0 retry 与硬停止条件**）；
2. **S2.13 冻结**（DoD 不变：S2.1–S2.12 完整）；
3. **GDPR Gold Rule Records 人工裁决与冻结**：由用户完成 9 个 rule IDs
   （article6/7/15/16/17/20/22/33/34）的正式 Gold Rule Records；Agent 不得创建、
   推断或自动填写；
4. **S3.4–S3.6 正式 promotion/readiness**（S1.7 依赖已满足）；
5. **单独申请 S3.7 formal Oracle 授权**：授权句只能由用户作出，当前
   `authorization_sentence=null`；在以上实质依赖完成前，`ready_for_oracle_authorization`
   保持 false。

本轮（2026-08-18）完成 S2.11 正式 Gold 发布后的 S2.12 零 API 前半程与 API preflight；未调用真实 LLM/API，未启动 Oracle，S2.12 仍为 partial，S2.13 与 S3.7 正式 gate 未翻转。

### 12.0b S2.11/G0.5 授权前工程收口（2026-08-15，v5 纠正，见 `outputs/reports/s2_11_g0_5_pre_authorization_v5.json`；**v5 为历史 checkpoint，当前入口为 v6，见 §12.0c**）

本轮工程成果（均未翻 gate）：(1) **v4 红测修复与历史 capsule 生命周期**：
v4 变更事件如实记录 3 failed / 2057 passed / 24 skipped、test_returncode=1、
integrity_pass=false（v3 历史正例测试在 v3 绑定资产演进后按 fail-closed
设计拒绝）；v5 引入 `src/bpc_hybrid/capsule_lifecycle.py` 集中语义——v3/v4
核心资产（schema/builder/verifier/4 outputs）逐字节不变（git 证明），v3/v4
pytest 文件仅按生命周期语义修正（历史 builder no-overwrite fail-closed、
历史 verifier 拒绝且失败项属于声明性 binding drift、历史负例测试继续真实
执行、active v5 builder/verifier 从当前磁盘成功重建/验证）；v5 全量审计
恢复 exit 0。(2) **许可分离**：论文许可已确认（CC BY 4.0 article-only，
PDF hash 绑定），artifact code/data 仍 unknown_pending_confirmation、
project_activatable=false、ready_for_data_activation=false、激活授权句 null。
(3) **adapter 加固（v5）**：严格 mode 枚举（INVALID_MODE）、真实文件级
evidence binding（相对安全路径 + 原始字节 SHA-256 + ID/kind/scope + 授权
manifest 精确绑定 policy/modality/field mapping/license hash）、可验证字段级
provenance（精确 element、确定性 locator `record_path#element`、重叠 span
ambiguity）；formal 正例仅用 tmp 临时文件；当前磁盘仍拒绝一切 formal 转换；
synthetic/shadow implementation verified（68 项真实执行测试）。(4) **M1/M2
精确范围**：M1 仅授权三类共享 modality identity candidate mapping；结构
映射需独立 G6；M2 不映射任何外部 label。(5) **G0.5 promotion readiness**：
`draft_config_sha256`（原始字节）= `61938c99…` 是唯一授权 hash 域（语义
hash `51a6e4fe…` 被 validator 拒绝）；`validate_frozen_application` 只对
真实文件原始字节算 hash；`classify_frozen` 仅接受完整验证结果（含不可伪造
validation_token）；`derive_promotion_readiness` 必须验证完整资产组合而非
glob 文件名；当前磁盘推导 draft_not_frozen /
promotion_ready_for_application=false / missing=user authorization
manifest；不创建真实 frozen config 或授权 manifest。(6) **gate 顺序**：
G3 ready=true（dry-run）、G4 ready=true（句子绑定原始字节 hash，仅授权未来
gate-application checkpoint、本轮不 frozen）、G5 protocol_ready=true 但
ready=false/sentence=null（条件式 future sentence）、G6 ready=false。
本轮零新增 LLM/API，references/ 只读未激活，S2.11/S2.12/S2.13/Stage 3
gate 均未改变，未生成 S3.7 Oracle 授权句。

### 12.0c S2.11/G0.5 授权链封闭与固定锚点（2026-08-15，v6，见 `outputs/reports/s2_11_g0_5_pre_authorization_v6.json`）

本轮工程成果（均未翻 gate）：(1) **frozen 授权链封闭（v6）**：v5 的
caller-supplied validation-result 解锁方式被本轮反例推翻——手工字典
`{frozen_application_valid: True, validation_token: <任意 64 位小写 hex>,
approved_frozen_config_sha256: <真实 frozen hash>}` 在 v5 下可返回
status="frozen"；v6 移除该参数：`classify_frozen` 每次调用从磁盘原始字节
重验 draft/frozen config、授权 manifest、append-only 授权事件与
prior-results 证据扫描（`derive_prior_results`，按确定性路径/manifest 规则
推导，不再接受 caller bool）；授权 manifest 必须完整绑定 schema/version、
manifest ID、authorization_applied=true、精确批准 scope 枚举
（future_external_complex_corpora_only）、精确批准 G4 dry-run 句全文及其
UTF-8 SHA-256、draft/frozen 相对路径 + 原始字节 SHA-256、
retrospective_use_forbidden / frozen_before_new_results /
s2_10_retrospective_use_forbidden、重推导 prior-results 扫描、
授权事件（ID+路径+原始字节 SHA-256）与 pending（未应用）checkpoint；
全部变体（另一 manifest 的 token、manifest 修改后旧 token、manifest 与
config 不匹配、句/scope/事件/路径被替换、先出结果后构造授权、仅布尔/伪造
hash 声称已验证）均被拒；普通内容 hash 只证明字节一致，不被当作用户授权
证明。(2) **历史 capsule 固定锚点（v6）**：v3/v4/v5 核心资产逐字节不变，
锚定固定 origin commit（31ac757d…/8e8b488e…/7883739…）+ 硬编码 21 项
SHA-256 map（`src/bpc_hybrid/capsule_lifecycle.py`）；磁盘字节必须匹配
固定 map 且 origin-commit blob 必须匹配固定 map；新增回归测试证明
“HEAD 与磁盘同时被替换为同一错误字节”仍失败（v5 的 HEAD 相对检查无法发现
该场景）；v6 report/manifest 绑定三版固定 hash。(3) **adapter evidence
provenance（v6）**：evidence verifier 返回结构化 EvidenceContext；formal
输出新增 `formal_evidence_provenance`（license evidence ID/相对路径/原始
字节 SHA-256/精确 license scope；authorization manifest ID/相对路径/原始
字节 SHA-256/精确 authorization scope；授权事件 ID/路径/hash；policy ID；
modality/field mapping canonical hash；manifest 对 license evidence 的
绑定；candidate_only=true、gold_authorized=false）；synthetic mode 为
null；scope 使用受控枚举（LICENSE_SCOPES / AUTHORIZATION_SCOPES，
授权 scope 例 s2_11_candidate_mapping_only），manifest 必须精确复述
license evidence scope，article-only scope 不满足 artifact code/data
要求（LICENSE_SCOPE_NOT_ARTIFACT_COVERING）；evidence 路径 resolve()
后必须仍在 evidence root 内（symlink/junction 逃逸 →
EVIDENCE_PATH_ESCAPE）；当前真实磁盘无合格 evidence，一切真实 formal
调用仍被拒。(4) **v5 事实如实记录**：v5 全量审计确实为绿（最终 receipt
`2118 passed, 24 skipped, 19 warnings in 941.91s`），v5 不是红测
checkpoint，其历史事件保留；v5 的 hand-built validation-result 防护声明
被本轮反例推翻（与审计绿灯分开记录，不混为一谈）。(5) **G0.5 未冻结**：
授权 hash 域仍为原始字节 61938c99…，语义 hash 51a6e4fe… 永不使用；
G3/G4 仍仅 dry-run；G1/G2/G5/G6 ready=false+null；S3.7 全 false/null。
本轮零新增 LLM/API，references/ 只读未激活，Gold/contract/methods/
predictions/results 未改，S2.11/S2.12/S2.13/Stage 3 gate 均未改变，未
生成 S3.7 Oracle 授权句。

### 12.0d S2.11/G0.5 非 API 决策应用与 G0.5 冻结（2026-08-17，Checkpoint A，见 `outputs/reports/s2_11_gates_applied_checkpoint_a_v1.json`）

用户转发授权原句 `除了用apikey的时候要授权，其他直接正常进行即可。`（UTF-8 SHA-256
a8a1dec4…，事件 `configs/s2_11_user_authorization_event_v1.json`）：除真实 LLM/API
调用外，所有本地、非破坏性、可回放 Pipeline 操作可直接执行并如实记录。本轮应用并
记录（均未调用 API、未翻越 Stage 3 门禁）：(1) **G1**=resolved_for_local_
nonredistributive_analysis——artifact（references/barrientos_2026，91 文件）无可
解析许可（无 LICENSE/COPYING/NOTICE/README/metadata；anonymous artifact 页面无
license 标识），`artifact_license_verified=false`、`unknown_pending_confirmation`，
用户授权本地只读研究使用，禁止再分发/公开原始数据、禁止修改 references、正式包只
含 hash/ID/统计/用户裁决；(2) **G2**=applied_local_read_only（scope=
local_read_only_nonredistributive_s2_11，formal run 只读 membership manifest
列出的文件）；(3) **G3**=applied——M1 modality identity candidate mapping
（obligation→obligation、permission→permission、prohibition→prohibition），
candidate-only、definition 绝不自动生成、外部 annotation 仅 review aid；
(4) **G6**=applied——S0_no_automatic_structural_mapping（真实 artifact 记录为
{ID, version, text} 自然语言句，格式规范中的 precondition/temporal_validity 为
嵌套逻辑对象而非可验证叶子 span，故 field_mapping={}，无法安全映射留空交人工）；
(5) **G4**=applied——G0.5 冻结 `configs/g05_complexity_frozen_v1.json`
（status=frozen、frozen_before_new_results=true、retrospective_use_forbidden=
true、s2_10_retrospective_use_forbidden=true、scope=future_external_complex_
corpora_only），经 v6 密封链完整验证（draft 原始字节 61938c99…、授权 manifest、
append-only 授权事件、空 prior-results 扫描），冻结前无任何 S2.11 候选/结果；
G0.5=frozen_for_future_external_complex_corpora，原 draft 保留为历史 provenance，
S2.10 旧结果不重标 preregistered；(6) **G5** 未在本 checkpoint 应用（membership/
workload 待 Checkpoint B 语料盘点后打开 review surface）；(7) v6 capsule 转为历史
安全基线（核心资产字节不变，pytest 生命周期语义修正）；S2.11 仍 blocked（等待
Checkpoint B 候选生成与人工裁决），S2.12 partial、S2.13 blocked、S3.7 未动。

### 12.0e S2.11 语料激活与人工 review surface（2026-08-17，Checkpoint B，见 `outputs/reports/s2_11_candidate_run_v1.json` 与 `outputs/reports/s2_11_g5_review_surface_v1.json`）

真实 Barrientos requirement 语料激活（全部离线、零 LLM/API、本地只读非再分发）：(1)
**corpus inventory**——3 个 scenario requirements 文件（40 条记录：blood_donation
r14-r20×2、emergencies r1-r7×2、SIM_card r8-r13×2），hash-only membership
（`outputs/reports/s2_11_corpus_membership_v1.json`：文件原始字节 SHA-256/size、
record IDs、逐条 text SHA-256；不复制原始第三方文本）；4 条空/占位文本记录
（QUARANTINE_EMPTY_TEXT）隔离。(2) **deterministic ingestion**——文档化模态关键词
规则（prohibition/permission/obligation 顺序，精确 span；"must not" 优先于
"must"），结构字段按 S0 政策留空，cross-ref 空；adapter 以新增
`local_read_only_research` 模式运行（许可未知绝不声称 verified；用户授权事件 +
containment 为证据，EVIDENCE/scope/containment 全链验证）。(3) **candidate 运行**——
29 条候选（obligation 21 / permission 2 / prohibition 6；G0.5 frozen 分类
L1×28/L2×1；provenance 完整 29/29）；7 条运行期隔离（8 条 MODALITY_UNKNOWN 中
r16v1/r17v1/r17v2/r10v1 等无模态关键词、3 条 FIELD_SPAN_AMBIGUOUS 如 "must" 出现
两次；共 11 条隔离）；完整候选（含原文）仅存 gitignored 本地目录
`outputs/development/s2_11_local_working/candidates_v1/`，提交资产只有统计、hash、
ID、隔离码。(4) **G5=applied_review_surface_open**——空白 review pack
（`data/development/human_review/s2_11_blank_review_v1.json`，29 samples，全部决策
字段 null、unreviewed、无预填 Gold、无原文）+ 用户决策文件
（`s2_11_review_decisions_v1.json`）+ review 工具
（`scripts/review_s2_11_candidates.py`：运行时按 hash 只读加载 references 原文，
不匹配即拒，原子写入+备份+resume+progress）+ 冻结验证器
（`scripts/verify_s2_11_review_freeze.py`，frozen=false 直至用户完成裁决，不创建
Gold）。(5) **S2.11=in_progress_human_adjudication**（29 条待用户裁决 + 11 条隔离，
见 transition readiness v3 重推导）；S2.12 仍 partial、S2.13 仍 blocked、S3.7 未动；
零 LLM/API、未伪造 Gold、未发布受限原文。

### 12.0f S2.11 正式 Gold 发布（2026-08-17，见 `outputs/reports/s2_11_formal_gold_v1.manifest.json`）

在 Checkpoint G 的 36/36 用户裁决与 freeze v3 `frozen=true` 基础上，正式发布
`data/gold/stage2/s2_11_complex_corpus_formal_gold_v1.json`（SHA-256
`039ae8b2429826ae2b320667fb4a0dff96de6408b0a9637c1d9911565129c804`）。
发布器在写入前逐项验证：(1) 确认事件文件原始 SHA-256 `226b4798…` 与事件内
用户原句 UTF-8 SHA-256 `7414a38d…` 分开绑定；(2) proposal v3 文件 SHA-256
`9882ba45…`、proposal source、reviewer=hyc、revisions=none；(3) decisions v2
36/36 adjudicated 且每条 reviewer/confirmation event 一致；(4) freeze validator v3
真实执行；(5) 40/4/36 membership、第三方 source file/text hashes、canonical spans、
actor-action map、order relations 与 G0.5 frozen 状态。Gold 的每条 `canonical` 与冻结
decisions 等值，并与 proposal v3 的 containment transform 等值；不得称为独立专家
从零标注，正式 provenance 为 `deepseek_offline_proposal_v3` +
`user_batch_confirmation` by hyc。版本化 schema、publisher、publication capsule、
manifest、export index 与独立 verifier 均已建立；重放命令 byte-identical，独立
verifier 27 项全过，focused 9 项（含 extra-field/event/reviewer/G0.5/manifest/export
篡改）全过。提交 Gold 不含第三方原文，只含本地 source path/file/text hashes、
坐标和必要标签；零 LLM/API，未生成 predictions/results/Gold Rule Records，未启动
Stage 3 Oracle。S2.11 因此为 verified/frozen/Gold published；S2.12 的零 API arm
已在 §12.0g 完成，仍须运行两个 API arms、完成三方法比较与最终冻结。

### 12.0g S2.12 零 API 前半程与 API preflight（2026-08-18，见 `outputs/reports/s2_12_execution_readiness_v4.json`）

在 S2.11 Gold 冻结发布后，构造 `s2_12_complex_corpus_formal_input_v1.json`：36 个
固定 IDs，仅保存本地 source locator、file/text hashes 与 text byte size；没有 Gold
labels、spans、decisions 或原文。`sun_rule_only` 的 method/config/input hashes 在读取 Gold
前锁定，随后以 B0 v10a、CPU、同一英文 source pass-through 运行（明确限制：legacy
classifier 原开发合同为德语，本结果是描述性 English pass-through，而非 language-matched
classifier validation）。预测 capsule 36/36 成功、runtime 18.5112149s、LLM/API/network=0、
cost=$0，并在评价前锁定；之后 evaluator v2 才读取 frozen Gold，报告 overall 及 L1/L2/L3，
其中 L3=0 仅为 no samples。overall modality accuracy=0.638889、macro-F1=0.535461；五字段
span P/R/F1=0.862319/0.802721/0.831453。该结果只代表一个 zero-API arm，不是三方法完整
比较；未根据 Gold/结果调整方法、规则、prompt 或 threshold。

`s2_12_api_preflight_v1.json` 在不读取 Gold、不读取 `.env`、不调用网络/API 的条件下，
从最终 OpenAI-compatible request body 精确计算 payload：direct_llm 36 calls、
sun_llm_fallback 27 triggered calls，总 63；UTF-8 body 最大 17,493 bytes、总 749,805 bytes；
本地 `nlpaueb/legal-bert-base-uncased` WordPiece proxy 最大 4,960、总 207,468 tokens（非
DeepSeek tokenizer、非 billing count）；output cap 4,096/call、258,048 total；retry=0。
官方 `deepseek-v4-pro` 价格与 1M context 已绑定，实际 billing input token/cost 仍只能以
真实响应 usage 为准；建议的绝对保守授权上限为 input 63,000,000 tokens、US$27.63，且
运行前须重验官方价格。当前未获授权、实际成本为 null、调用数为 0。transition v8 保留
v7 八个资产 byte-exact，明确历史 verifier 生命周期：v1-v4/v7 正常通过，v5/v6 因被
Checkpoint G 后状态合法 supersede 而以精确预期签名 fail-closed。当前状态：S2.11
verified/frozen；S2.12 partial；S2.13 只 blocked on remaining S2.12 DoD；S3.4-S3.6
development-only；S3.7 formal Oracle not started；Gold Rule Records absent。



### 12.1 论文并行轨道（导师要求立即启动）

**2026-09-15 写作目标补充**：按 [论文写作入口](../paper/README.md) 的“工作、贡献与
图表清单”展开 PW1–PW9。每项实质研究工作应有正文或附录位置，说明问题、来源、
自己的实现/适配、对应数据与局限；已有相关数据经核对后充分呈现，不只写总分或
“使用 LLM”。说明性表格无需独立创新，候选表格不构成新增实验任务。
写作验收按本节内容完整、借鉴与贡献清楚、数据有来源、图表有解释、TODO 明确执行；
完整初稿可保留未完成实验占位，不等待所有实验完成再写。此要求补充写作组织，
不替代正式结果回填条件，也不把旧三方法条目恢复为当前工作。

**2026-09-12 调度覆盖**：PW0–PW9 保留为写作任务索引；主线、依赖和真实完成标准
按文首「CSCWD 按依赖推进的收尾 Pipeline」执行，满足条件即推进，尽早完成；仅保留九月底初稿和十月底投稿的最晚目标。
下表较早日期的状态不作为实时派工入口；实时状态只读 `PROJECT_AUDIT.md`。

论文写作从现在开始，不等待最终实验；但写作进度不能反向解锁实验门禁。实时派工
与可复制 Prompt 见 `docs/PROJECT_AUDIT.md` 和 `docs/AGENT_RUNBOOK.md`。

| ID | 写作任务 | 当前状态 | 回填/完成门禁 |
|---|---|---|---|
| PW0 | 论文目录、骨架、主张矩阵、TODO 和空表 | verified | 本轮建立且无虚构结果 |
| PW1 | 引言、背景、RQ0–RQ4 | ready | 全部结果性表述为待检验或 TODO |
| PW2 | Sun/Winter/Sleimi/Michel/Barrientos 相关工作 | ready | 内部证据回到可核验原论文 |
| PW3 | 三阶段架构和 Rules-Only / Rules+LLM-Repair / Direct-LLM（旧代号 B0/H1/D1）方法设计稿，贡献按 §8.8.4 细模块化（Direct-LLM 8 模块 + Rules-Only 8 模块 + H1 负结果对照 + Barrientos 15 维对比表） | in_progress（2026-08-20：方法章节已按 8+8 模块与 15 维对比表写入 `paper/THESIS_DRAFT.md` §4，命名迁移为正式名；模块有效性未验证） | 模块有效性结论待 AB-1–AB-10 正式消融；未完成组件使用 TODO-STATUS |
| PW4 | 数据、五层 Gold 与标注协议 | partial-ready | S2.1/S2.2 后回填实际统计 |
| PW5 | baseline、指标、统计与复现设计 | ready | 参数在对应任务冻结后回填 |
| PW6 | 结果表和图模板 | ready-template-only | 禁止填非正式数字（§7.2 正式三方法比较表已按 manifest 回填） |
| PW7 | Stage 2 正式结果 | partial（2026-08-20：三方法正式比较表已回填 §7.2；复杂度分层待 S2.12 API 授权后补齐） | S2.12 API arms + 三方法复杂语料比较 + S2.13 freeze |
| PW8 | Stage 1/3/端到端结果 | blocked | S1.7、S3.7–S3.10、P8 |
| PW9 | 讨论、结论、摘要与终稿 | partial（2026-08-20：§8 局限按量化证据逐条撰写；结论/摘要仍 blocked） | S2.12 API、S3.7、主张矩阵全绿 |

论文占位符统一使用 `TODO-RESULT`、`TODO-SOURCE`、`TODO-STATUS`、
`TODO-DECISION`。开发结果只能标 `DEV_ONLY`；正式数字必须对应 `experiment_run`
事件和 manifest。Stage 2/3、Oracle/end-to-end、C1–C4 前人比较必须分开。

## 13. Agent 任务执行协议

每个工作批次按实际改动范围执行（2026-09-12 同步两级 AGENTS.md 已生效的
2026-09-10 验证成本政策；本节不新增门禁）：

1. 阅读两级 AGENTS.md 和任务相关来源；实验行为变更再按 AI_CHANGE_PROTOCOL 阅读完整必读清单；
2. 实验代码、配置、prompt、schema、数据协议或评价器变更才运行编辑前快速完整性检查；
3. 从任务表选择一个最小任务 ID；
4. 写明输入、输出、依赖、边界和 Definition of Done；
5. 程序改动只跑具名相关测试，常规范围以三分钟内为目标；纯文档做内容/文件检查；
6. 实验行为变更在批次边界做快速完整性检查；全量测试仅在用户明确授权本轮范围后执行；
7. 实验行为变更用 `record_change.py` 记录；真实实验还记录 `experiment_run` 与 manifest；
   纯文档可用 scoped Git commit 记录，不为缺少测试凭证自动跑完整测试；
8. 任务定义更新本文，实时状态只更新 `PROJECT_AUDIT.md`，不新增日期版 status/handoff；
9. 一个连贯任务完成即检查差异、只暂存所属文件、审查暂存差异、提交并推送当前上游，报告结果。

任务状态只使用：`blocked`、`ready`、`in_progress`、`verified`、`complete`。
只有脚手架或单元测试时只能写 `development` 或 `partial`，不得写完成。

执行频率：只读分析不跑测试或追加实验事件；文档/排版不跑实验检查；实验行为修改按实际
影响范围验证。批次结束、交接、提交、推送和截止日期均不自动触发全量测试。
不得重复启动共享工作区套件或改绑历史凭证。正式运行按对应门禁执行（包括适用的
`--require-final-ready`）；详细范围与日志示例见 `AI_CHANGE_PROTOCOL.md`。

## 14. 目录边界

活动目录结构见 `docs/DIRECTORY_GUIDE.md`：活动入口留在 `docs/` 顶层；研究证据放
`docs/research/`；已替代路线、快照、旧输出和旧脚本放 `_retired/`；实验事件只追加，
不得重写；`references/` 与根 `archive/` 只读；缓存和临时目录可以清除；数据、Gold、
预测和结果不得因目录整理被删除。恢复 `_retired/` 材料需要用户批准和日志事件。

## 15. Pipeline 变更日志

| 3.7.35 | 2026-10-06 | SEP-C3-PROMPT-SIMPLIFY-V1：用户明确授权 v6/A/B 同批 150×3 对照；绑定唯一 run ID、450 次/0 重试、USD 14.77 与共享请求/后处理/评价口径；先完成离线执行准备，不将准备当性能结论 | 新预检、具名检查、change 事件与 scoped checkpoint；实际运行状态见 PROJECT_AUDIT |

| 3.7.6 | 2026-09-14 | **SEP-C1-B：前人比较范围、通用题名与完整 E/S/J 2^3 消融预算准备（零 API）**。论文 §2.3 固定三层前人比较注册与 Sun/Winter 版本边界；题目节固定推荐中英文题名与两个备选，摘要/RQ 统一自然语言合规需求术语；ABLATION_MATRIX 登记 000-111 八组合、共同输出接口、旧四臂仅作历史单因素证据的不可拼接理由，并准备同批次 8x150x2=2400 calls 主方案、非推荐复用 1800 calls 变体与可选第三重复 +1200 calls 的 input/output/USD/CNY caps、失败计数和主效应/交互 bootstrap 协议；主张矩阵新增 C44/C45/C46；API_AUTHORIZATION_REQUEST §14 给出授权草案。真实实验/API/测试=0；所有组合待运行；价格快照 2026-08-30 未联网复核。 | 文档/预算准备、价格与扣除条件、授权草案、主张矩阵、FILE_CATALOG；scoped Git commits/push；零 API |
| 3.7.1 | 2026-09-12 | **SEP-C0 修订：按依赖推进，持续诊断与修复**。按用户纠正撤销 3.7.0 的阶段起止日、预设实验停止日和投稿就绪日，仅保留 9 月 30 日导师初稿、10 月 31 日 CSCWD 截止两个最晚目标。条件满足即开始、完成即推进；新增问题归入原任务，定位、最小修复、相关验证、论文同步后继续，不重跑有效证据、不以月份阻塞工作。同步实时派工和手册，任务 ID、实验门禁及既有授权保持有效。 | 文档内容、链接及差异检查；scoped Git commit / push；未运行实验或调用 API |

| 3.7.0 | 2026-09-12 | **SEP-C0：CSCWD 收尾计划锁定**。用户确认 9 月 30 日导师初稿、10 月 31 日 CSCWD 截止；文首固定 SEP-C0–C6 / OCT-C1–C4 日期、任务映射、九项反馈、验收标准和阻塞处理，9 月 25 日/10 月 18 日实验截点、10 月 28 日投稿就绪。同步派工入口及既有验证成本政策；旧实验门禁和资产不变，未运行实验或调用 API。 | 文档内容、链接及差异检查；scoped Git commit / push；非实验完成声明 |

| 3.6.39 | 2026-09-07 | **论文收尾授权落地与执行链补齐（零 LLM/API，ZERO CALLS）**：用户论文收尾指令（句哈希 `27426de7…`）授权 137 次调用（S2.12 63 + GDPR 74，两笔独立 cap、off-peak、retry=0、deepseek-v4-pro）。(1) 授权文件：批 A 五 stage auth+event（`configs/s2_12_api_authorization_*`，USD 1.00/42.09）与批 B GDPR 授权事件（builder `scripts/build_gdpr7_direct_llm_authorization_event_v1.py` + 8 测试；executor 同款校验通过；74/74 假响应彩排 complete）；新活动验证器 `verify_s2_12_authorization_files_v1.py` 70/70 PASS；旧 no_real_auth verifier 按设计 superseded。(2) S2.12 执行链补齐：`s2_12_execution.py` raw 落盘 + 事故记账（transport_error/usage_missing 后中止不重发）+ 链式骨架按账本重建；runner `--raw-dir`；`s2_12_response_convert.py`；`finalize_s2_12_arm_v1.py`（正式 capsule 唯一发布入口，坐标-only、off-peak 成本重算、fallback 复用 H1 链逐 plan 审计）；`evaluate_s2_12_api_arm_v1.py --arm …` + `verify_s2_12_api_arm_v1.py`（11 测试）。官方价格重验（2026-08-17 峰谷方案不变）。(3) GDPR 裁决工作流 v1：editable 文件 + 工具/校验/导入/冻结 + 38 合成测试（blank 字节未动）。(4) 新增聚焦 60 项全绿 + s2_12 回归 52 passed + 全量 2965 passed/24 skipped（FILE_CATALOG 重建）。真实 API=0；S2.12=authorized/ZERO CALLS/READY；S2.13 blocked only on S2.12 DoD；S3.7 未动。 | 授权依据/事件文件 + 执行链补齐（raw/finalize/evaluate/verify）+ GDPR 裁决工作流 + 验证器/测试 + 文档同步；record_change 事件 + audit --with-tests |
| 3.6.37 | 2026-09-06 | **汇报前收尾：统一五分类评价重算 + 原三类衔接实跑 + GDPR Direct-LLM 执行链离线验证（零 API）**：(1) **统一预测规则修复**：合规/违规两侧改为同一确定性五分类决策（固定 EXTENDED_TYPES 优先级/阈值/不可观察规则；决策不读 expected/gold，gold 仅在预测固定后进入评价），基于已保存 scores/scores_detail/observability/control_scores 离线重算（`scripts/reevaluate_s3_extended_unified_v1.py`）；旧结果与 manifest 保留并明确标为“指定类型条件性检出评价”（非分类）。统一口径（reference/rules_only）：variant-only macro winter 0.499/0.331、sun 0.321/0.188、bm25 0.226/0.000、tfidf 0.375/0.332；wrong-type 出现（reference winter 9、tfidf 1；rules_only winter 10、tfidf 6）——撤回“P=1/无 wrong-type”表述；control FP 两口径一致（reference 0.500/0.125/0.000/0.275；rules_only 0.450/0.050/0.000/0.375——**tfidf 由 0.275 升 0.375，“误报未升”整体表述撤回**）；paired 5-class reference 0.375/0.263/0.250/0.338、rules_only 0.263/0.200/0.150/0.263；旧 paired 数字由持久化行精确复现（自检通过）。产物 `outputs/reports/s3_extended_unified_v1_{reference,rules_only}.*` + 逐方法 confusion/eval/manifest；注记 `docs/research/S3_EXT_UNIFIED_EVALUATION_NOTE_2026-09-06.md`。(2) **原三类衔接实跑（33 条人工 violation decision Gold，dev Sun-style 固定参数）**：`scripts/run_gdpr_3type_linkage_v1.py`（converter `src/bpc_hybrid/sun_stage3/gdpr_capsule_converter.py`：外部 Rules-Only 胶囊→Sun 规则记录，obligation-only 门控、span 校验、失败不虚构；gold 预测固定后才读，shuffle-gold 测试证明预测不变）。参考臂 macro 0.3889/exact 0.3636/unobs 10（与存储 s35 行逐字段一致）vs Rules-Only 臂 0.3333/0.3333/11；missing_action 两侧 11/11 F1=1.0；24 同/9 变，唯一判定翻转 v014（incorrect_actor→None）；out_of_order 两侧 0（外部胶囊无 order_relations——缺失输入契约+端点阈值瓶颈，如实记录）。(3) **GDPR Direct-LLM 74 臂执行链**（`scripts/run_gdpr7_direct_llm_v1.py` + `configs/ablations/gdpr7_direct_llm_execution_contract_v1.json`）：与预检报告 body SHA 逐一一致的 PayloadLock、in-code 硬上限（input 74M/output 303,104/USD 2.61 peak-1.31 off-peak、retry=0、off-peak only）、授权事件门禁、账本断点（in_doubt 不自动重发）、raw/canonical/cost/manifest 保存、输出与 linkage runner schema 衔接；**假响应 74/74 全流程离线验证 + 9 项测试通过（程序验证，非实验）**；真实调用待授权（合并申请 docs/API_AUTHORIZATION_REQUEST.md §11-§12：S2.12 63 + GDPR 74 = 137 calls）。(4) 论文/汇报口径修正：THESIS_DRAFT §7.4.4 与 CLAIM_EVIDENCE_MATRIX C30/C34/C35 更新为统一口径；mentor 汇报稿 `paper/MENTOR_REPORT_CONTENT_2026-09.md` 定稿（统一数字+状态表+来源速查）。全量 audit 通过；零 LLM/API；未改 Gold/冻结面板/阈值/BPMN/历史产物。 | 统一评价重算 + 3-type 衔接 + D1 执行链验证 + 文档修正；record_change 事件；audit --with-tests |
| 3.6.36 | 2026-09-06 | **GDPR Stage2→Stage3 成对衔接实验（Rules-Only 臂已运行；Direct-LLM 臂待授权）+ 论文收尾工程（零 API/零网络）**：(1) GDPR 句子级 Gold-blind Stage-2 输入 `data/input/gdpr7_stage2_input_v1.json`（9 段 GDPR 条款=冻结 inference pack 规则文本，分句与 S3.9-EXT 面板锁定绑定逐条一致（40/40 验证），**74 句**：article33:10/article34:7/article15:13/article17:13/article7:8/article6:10/article22:6/article20:5/article16:2；含条款 ID/文本 hash/分句位置绑定，Gold-blind）；(2) Rules-Only 真实零 API 运行 `data/predictions/gdpr7_sun_rule_only_v1/`（锁定 B0 v10a、74/74 ok、82 clauses、0 失败/0 空输出；英文经德语合同 classifier 槽 pass-through 披露；run-lock `configs/gdpr7_sun_rule_only_run_v1.json`）；(3) 衔接 harness `scripts/run_gdpr_s2_s3_linkage_v1.py`：复用原始 S3.9-EXT 面板运行器同一后端/公式/阈值（winter 0.4/sun 0.8/bm25 0.5/tfidf 0.5，gamma_ext 0.5），每变体六要素记录改为外部预测 first-valid-span 投影，失败/缺失显式计数、**绝不回填**面板锁定抽取；Rules-Only 臂结果（40 变体 variant-only + 40 对照 paired，DEV_ONLY）：winter macro 0.5208/exact 0.375/unobs 23/control FP 0.45；sun 0.1875/0.15/32/0.05；bm25 0/0/32/0；tfidf 0.351/0.275/28/0.375；相对参考确定性抽取的逐样本变化 winter 7/sun 6/bm25 6/tfidf 4（案例：article22 s1 被 B0 判 obligation 致 2 个禁止动作变体不可观察；tfidf 下 constraint_violated_04 由不可观察变为新检出——替换 Stage-2 会真实改变最终违规判断且方向不唯一，本臂以检出下降为主、无 wrong-type、误报率未升）；(4) Direct-LLM 臂准备：`outputs/reports/gdpr7_direct_llm_preflight_v1.json`（74 个冻结请求渲染、body 1,297,742 B、Legal-BERT proxy 输入 367,333、output cap 303,104、建议 USD cap 2.61 peak/1.31 off-peak（S2.12 同价口径）、绝对上下文界 98.88），真实调用并入合并授权申请（docs/API_AUTHORIZATION_REQUEST.md §11：S2.12 63 + GDPR 74 = 137 calls，两笔独立 cap，授权文件未创建、calls=0）；(5) 人工核对材料：`data/development/human_review/gdpr7_six_element_review_blank_v1.json`（9 条款/74 句，candidate=确定性 dev 抽取、全部 decision 空、review_state=unreviewed）+ 验证器 + 中文工作流指南（agent 不得代填裁决）；(6) 论文六条修正落地（THESIS_DRAFT/CLAIM_EVIDENCE_MATRIX 新增 C32/C33/ABLATION_MATRIX D/E parse 率澄清：minimal parse=0.000，仅该臂不可解析；正式主结果与 H1 development 数字分离；Barrientos 表示含 activities/resources 为不同契约非“无法表达 actor/action”；删语义规则后 exception 上升如实写；坐标重锚关闭 0 分=接口可用性非语义归零；四类新错误按类型表述）+ 12 页导师汇报内容稿 `paper/MENTOR_REPORT_CONTENT_2026-09.md`。全量 audit 通过；零 LLM/API；未改 Gold/冻结面板/阈值/BPMN。 | 衔接实验输入/运行/评测/报告 + D1 预检 + 授权申请 + 人工核对材料 + 论文修正 + 汇报稿；record_change 事件；audit --with-tests |
| 3.6.35 | 2026-09-06 | **S2-BARR-4 原生 FULL/NO-PATTERNS 360 次方案撤回（用户澄清；零 API，不执行）**：用户澄清此前“直接使用 Barrientos 原始 FULL/NO-PATTERNS 两份提示、在冻结 36 条输入上运行 360 次”的方案是对其意图的误解，**已经撤回、不得执行**。研究定位维持：Sun et al. (2024) 是整体改进对象与三阶段方法主干；Barrientos et al. (2026) 仅作为 Stage 2 的方法借鉴来源（LLM 结构化输出、验证、受控词汇、归一化与评估纪律），项目不承担“必须整体优于 Barrientos”、不把原样运行其原生提示作为正式对照。2026-09-05 段（§8.8.4）及其入口/合同/预检/测试保留为历史证据，状态=withdrawn（checkpoint `2c5181e` 后不再作为待授权执行计划）；任何恢复执行需用户另行明确授权。Barrientos 相关已完成证据（D/E 1140/1140、后处理与 450-call prompt 单因素）与 AB-1–AB-10 其余消融不受影响。文档同批修正：S3.7 行过渡核账入口指针 v7→v8（§12.0 当前 fail-closed capsule；v7 及更早为 byte-exact 历史 provenance）。 | 用户撤回说明 + 路线/状态页定位澄清 + 变更日志行；record_change 事件；审计检查 |
| 3.6.34 | 2026-09-04 | **Stage 3 Sun 式阈值敏感性实验（S3.5 evidence extension，DEV_ONLY，零 API，API calls=0/cost=0）**：严格模仿 Sun 2024 §5.3/表 9/图 8/图 9 的离散网格，不做自动断点搜索/ROC 最优/交叉验证调参/新算法支线——matching τ∈{0.0,0.2,0.4,0.6,0.8,0.9} 只评 Def-4 分数重算后的每流程 AP/MAP（τ=0.8 行与 evidence MAP 0.8175 逐项一致）；γ∈{0.0,…,0.9}（ϑ 固定 0.8）与 ϑ∈{0.5,0.6,0.7,0.8,0.9}（固定 γ=0.8，Sun 图 9 协议）均由 SunScorer 真实重算 action mappings/actor denominators/order endpoints/observability（不是对最终分数重切阈值）；每阈值报告 per-type P/R/F1、macro/micro F1、exact-type accuracy、unobservable、各 process 结果与 runtime；Sun-transferred (0.8,0.8,0.8)=Macro-F1 0.3889/exact 0.3636/unobs 10（低分基线保留）；best observed setting (0.8,0.6,0.8)=Missing F1 1.0/Incorrect-actor 0.7778/Out-of-order 0.8421/Macro-F1 0.8733/exact 0.7879/unobs 4；机制诊断：γ=0.8 下 OO 端点映射分母 0 占 11/11、IA 10 条 action_mapping_below_gamma（v014 min actor sim −0.0163 低于全部测试 ϑ → ϑ 行平坦）；重算 primary 行与 evidence threshold_sensitivity.json 全部重叠行逐项一致（verification 块），差异即停止；产物 outputs/reports/s35_sun_stage3_threshold_sensitivity_v1.{json,md} + 图 A/B SVG + builder scripts/build_sun_stage3_threshold_sensitivity_v1.py（--report-only 确定性重放）；论文 §7.4.7 与主张矩阵 C31；33 条 Gold 无 Gold=none 样本（specificity/FP rate 不可证）；措辞边界：0.8=Sun 数据上多数模型的经验值、γ=0.6 仅称 tested values 中 best observed setting（本文数据+spaCy 后端的经验校准值），不伪装预注册正式结果；11 项新增 focused tests + 121 项 focused 回归全绿 | record_change 事件 + audit --with-tests
| 3.6.33 | 2026-08-31 | **S3.9-EXT 新四类选择动机回填（零 API、零重跑）**：明确原三类只覆盖必需动作存在、actor 与 order；新增 prohibited_action_present / required_condition_not_enforced / constraint_violated / exception_not_handled 分别补足六要素中未被 Stage 3 消费的 prohibition modality、condition、constraint、exception。选择原则锁定为字段覆盖、语义不重复、exactly-one-error 可控变异与 BPMN 表面可观察；每类均可在原三类正确时独立发生。边界同步写入结果报告、论文 §7.4 与主张矩阵：四类只是 development-only 最小字段覆盖扩展，不是穷尽性法律违规体系，不改变冻结三类人工 Gold/正式 Oracle。实验配置、40 个变体、预测和指标均未改。 | report generator + comparison JSON/Markdown + thesis/matrix/status rationale-only update；17 项 focused tests |
| 3.6.33 | 2026-08-31 | **S3.9-EXT 收尾：paired control-plus-variant 评价与报告修正（零 API、零重跑）**：仅从持久化四方法 predictions.jsonl 离线计算 80 对象配对评价（40 control Gold=none + 40 variant；control 预测由持久化 control_scores 按原四类规则、原 gamma_ext=0.5 与固定 EXTENDED_TYPES 优先级重建，未修改阈值/决策顺序/样本，失败、none、wrong-type、unobservable 全部保留在分母）；新增 evaluate_paired / control_prediction_from_scores（src/bpc_hybrid/stage3_extended_violations.py）与 --report-only 模式（run_s3_extended_violation_panel_v2.py，确定性重放字节一致）；报告 outputs/reports/s3_extended_violation_comparison_v2.{json,md} 修正：variant-only 表与 paired 表分列（明确两种口径），七类 overview 只保留 7 个 per-class F1（删除联合 Macro-F1/Exact/Unobservable，注明 v1 30 条与 v2 40 条双 panel 差异、不计算联合指标、仅类型覆盖），v1 三类表独立；结论收紧（报告 §7 与论文 §7.4/主张矩阵 C30）：prohibited=支持新增检测类型可行性、constraint=部分支持（仍受动作映射与 BPMN 表面限制）、condition/exception=主要暴露 condition surface/action mapping/boundary event/parser 可观察性瓶颈；不写“全部四类都证明六要素下游价值”，改述“四个此前未使用的规则字段获得明确的 Stage 3 消费接口，但当前受控数据只对部分类型提供了较强性能证据，其余类型主要揭示可观察性和映射瓶颈”；paired 结果（DEV_ONLY）：Winter 5-class acc 0.425/exact 0.550/control FP 0.500/paired 0.225；Sun 0.263/0.300/0.125/0.175；BM25 0.250/0.150/0.000/0.100；TF-IDF 0.338/0.325/0.275/0.300。原三类人工 Gold/schema、33 条正式 panel、30 条 v1 panel、40 个 v2 变体与四方法原始 predictions/evaluation/manifest 字节不变（focused tests 哈希锁）；22 项新增 focused tests（共 39 项）；零 LLM/API、零网络。 | paired 评价 + 报告/七类表/结论修正 + 论文 §7.4 回填 + C30 + 39 项 focused tests + record_change 事件 + audit --with-tests |
| 3.6.32 | 2026-08-31 | **S3.9-EXT：Stage 3 新违规类别扩展（development-only synthetic controlled extension v2，零 API）**：纠正“只加样本不加类别”后，新增 4 类违规（prohibited_action_present / required_condition_not_enforced / constraint_violated / exception_not_handled，各 10 条共 40）——生成器 `scripts/build_s3_extended_violation_panel_v2.py`（40 项锁定计划：规则句子×流程×子种类×锚点；每变体 synthetic compliant control + 单一目标错误 variant；源 BPMN byte-unchanged、exactly-one-error 校验、replay byte-identical、规则绑定与六要素字段（modality/action/condition/constraint/exception）锁定）；扩展层 `src/bpc_hybrid/stage3_extended_violations.py`（确定性六要素抽取（词边界条件标记 + modal 下降动作提取）、四类候选面、统一公式 `score = max sim` / `1 - max sim`、exact time-limit contradiction 记录、共享 evaluator（unobservable 不硬算 0、计入主分母））；面板 `data/development/stage3_synth/synthetic_controlled_error_extension_v2.json`；运行器 `scripts/run_s3_extended_violation_panel_v2.py` 四方法共享同一公式与 evaluator，仅替换各自冻结相似度后端（Winter-style extension / Sun-style extension / BM25 extension / TF-IDF-SVD extension；action 映射用各自冻结 gamma 0.4/0.8/0.8/0.5，新类型决策统一 gamma_ext=0.5）；DEV_ONLY：Winter macro 0.655/exact 0.550/unobs 17、Sun 0.333/0.300/unobs 28、BM25 0.226/0.150/unobs 28、TF-IDF 0.379/0.325/unobs 27；对比报告 `outputs/reports/s3_extended_violation_comparison_v2.{json,md}`（含 synthetic 七类汇总表，明确非人工 Gold/非 Oracle；prohibited 最易（平均 F1 0.893）、condition 最难（0.083）；92 条 action_mapping_below_gamma 说明新检查继承原三类 action 映射瓶颈；命名 gateway 藏在 subProcess 内→no_condition_candidates 表达力局限）。**Winter/Sun 原论文未定义这四类，报告与论文一律使用 `Winter-style extension`/`Sun-style extension` 命名，不得声称原生能力。** 原三类正式 Gold/schema/预测字节不变（focused tests 哈希锁）；17 项 focused tests 全绿；零 LLM/API、零网络、未调参追分。 | S3.9-EXT 生成器/运行器/扩展层 + 40 变体面板 + 四方法 panel + 对比报告 + 17 项 focused tests + record_change 事件 + audit --with-tests |
| 3.6.31 | 2026-08-30 | **Direct-LLM Prompt 三条严格单因素真实执行完成**：用户明确授权 450 calls（DeepSeek-V4-Pro-0813、temperature=0、retry=0、USD cap 13.430、北京时间闲时），三臂各150条全部完成，失败0，执行器汇总 `complete=true`；实际 input/output=1,444,632/368,212 tokens、cost=$3.3650、runtime=3,329.1s。与同 release `D-full-0813`（F1 0.7719）比较：语义示例→纯结构模板 F1 0.7650（Δ−0.0069，actor Δ−0.1317），支持小幅总体正贡献；仅删详细语义规则 F1 0.7759（Δ+0.0040，action Δ−0.0518），显示字段权衡但无总体正增益；仅删显式 JSON 纪律 F1 0.7790（Δ+0.0071），合法率仍1.0，当前条件下未测得增益。全部为固定150条的描述性单次结果，不作显著性或普遍必要性推断；不与 Barrientos-native F1 跨 evaluator 比较。 | authorized 450-call run + per-arm raw/canonical/evaluation/manifest + execution summary + aggregate JSON/Markdown table |
| 3.6.30 | 2026-08-30 | **Direct-LLM 三条严格 Prompt 单因素臂冻结（零 API）**：纠正旧 D-no-fewshot 的混杂后，新增 `ablation_v2` 三臂：①语义示例替换为纯 key/type 结构模板（保留输出接口支撑，不再把坐标格式崩溃误作语义能力为0）；②仅删详细语义规则9–19、25–27（输出纪律、六个示例不变）；③仅删显式 JSON/schema 纪律（语义规则、六个示例不变）。每臂均只与同 release、已完成的 D-full-0813 在同一 EStG-150/Gold/`sun_literal_overlap@2.0.0` 下比较；新增调用固定3×150=450，基线0次复用。独立执行器/合同/schema/结果表生成器均已接线；合同绑定输入、三 prompt、builder、executor、模型 DeepSeek-V4-Pro-0813、temp0/retry0、全局预算与Gold隔离，当前 `authorization=null`，execute 会在首次 send 前 exit3；dry-run=0 API/0 network，渲染输入估算1,965,688，input cap2,948,532、output cap1,843,200、peak USD cap13.430、off-peak CNY envelope45.79。另纠正历史结果表把实际六个合成示例误写成“4-shot”的显示标签；历史响应/分数不变。 | 3 prompts + manifest + dedicated 450-call runner/contract/schema/budget/results builder + focused tests + zero-API dry-run |
| 3.6.29 | 2026-08-30 | **S2-BARR-4 消融证据纠错 + Direct-LLM 后处理三模块单因素（零 API）**：(1) no-fewshot 原始响应诊断：147/150 JSON 可解析、146/150 原始非空、247 clauses 的 clause_span 全为 `[start,end]`，锁定 adapter/canonicalizer 因接口形状删除全部 clauses；回顾性 Gold-blind 坐标桥（Gold 仅桥后评价）恢复 136 valid/134 nonempty、P/R/F1 0.647/0.444/0.526，明确只作 post-hoc 诊断，不取代锁定0分、不证明语义 few-shot贡献；(2) 同一 D-full-0813 raw、同150/Gold/evaluator 后处理单因素：full P/R/F1 0.820/0.729/0.772并逐位复刻锁定评价；−adapter ΔF1=0；−canonicalizer 149/150 validator reject、F1=0（Δ−0.772）；−validator ΔF1=0且 invalid observed=0（不取消安全价值）；(3) 修复分类报告把整个 append-only event log hash 当稳定 provenance 的缺陷，改绑定目标 run event canonical hash；few-shot 措辞纠正为输出合同贡献、语义贡献未隔离；(4) 原始/派生逐条预测因 EStG 许可边界继续 local-only，提交报告只含聚合/hash/失败边界；Gold/正式结果未改、真实 API=0。 | 两份诊断/消融报告 + 2脚本 + focused tests + audit --with-tests + record_change |
| 3.6.28 | 2026-08-22 | **S2.12 → 论文优先主线切换（同步 Stage 3 可控错误扩展，零 API）**：① 主线：Stage 1=已完成复现不再扩展；Stage 2 用已有三方法/复杂语料结果；Stage 3 立即新增 30 条 `synthetic_controlled_error_extension` 可控错误并运行现有 Winter/Sun/BM25/TF-IDF；论文正文并行完善，不再因 S2.12 API 未授权而等待。② Stage 3 可控错误扩展 （S3.9）：生成器 `scripts/build_s3_error_injection_v1.py`（锁定 30 变体 10/10/10；每变体源 BPMN byte-unchanged、exactly-one-error、XML/结构/非目标字段不变校验、replay byte-identical；规则绑定来自冻结 inference pack）；面板 `data/development/stage3_synth/synthetic_controlled_error_extension_v1.json`（明确 dev-only、never 人类 Gold）；运行器 `scripts/run_s3_synthetic_panel_v1.py` 在同一 evaluator 口径下四方法 panel（DEV_ONLY：Winter macro 0.333/exact 0.333；Sun 0.333/0.200；BM25 0.333/0.333；TF-IDF 0.635/0.533）。③ S2.12 Direct/Fallback 保持 pending authorization（非论文 blocker）。④ Stage 3 formal Oracle 仍未启动，synthetic panel 不冒充 Oracle。 | 用户优先级切换 + S3.9 synthetic controlled-error panel + 四方法 panel 运行 + 16 项 focused tests + 零 API 审计 |
| 3.6.27 | 2026-08-22 | **S2.12 runner safety v2（零 API 零网络；RUNNER SAFETY V2 VERIFIED / API NOT AUTHORIZED / ZERO CALLS）**：真实执行安全合同修复——per-call PayloadLock（每次真实调用前重建实际 body SHA + sample/clause/order 核验，policy 与 preflight 完全一致）、usage 捕获与真实成本计算（cache hit/miss 拆分、缺失保守 cache-miss、cost_usd 不再硬编码 0）、per-call caps + off-peak（每次调用前检查；运行中进入 peak 即停、partial 账本保留）、append-only hash-chained 账本与 resume（不重复、篡改拒绝）、预注册 stage 合同（D-CAL/D-REST/F-1..F-3，CLI `--stage-id`/`--auth-file`/`--resume-from-ledger`）、`.env` 禁读（`load_project_env=False`）、每 arm 独立 runner hash 绑定、授权 schema v1.1.0（stage 绑定 + final-63 承诺）、离线授权事件 builder（无原句拒绝、dry-run、本轮不 apply、固定输出路径）、新增 `verify_s2_12_runner_safety_v2.py` 与 scripted real-like focused tests（零网络）。真实 API calls=0、cost=$0；S2.12 仍 partial，S2.13 仍 blocked。 | runner safety v2 + auth v1.1.0 + auth-event builder + verifier + tests + v4 授权申请 + 零 API 审计 |
| 3.6.26 | 2026-08-22 | **S2.12 runner wiring（零 API 零网络；RUNNER READY / API NOT AUTHORIZED / ZERO CALLS）**：实现 S2.12 专属执行接线——`scripts/run_s2_12_direct_llm_v1.py`（36 calls）与 `scripts/run_s2_12_sun_llm_fallback_v1.py`（27 calls、frozen plan、transport capture）、`configs/s2_12_fallback_trigger_plan_v1.json`（自锁定 preflight 触发集派生，replay byte-identical）、共享契约 `src/bpc_hybrid/s2_12_execution.py`（63 request-body SHA 逐条重建比对、授权合同校验、Beijing off-peak 时段、payload-locked fake transport、原子发布、文本/密钥 containment）、`configs/schemas/s2_12_api_authorization_v1.schema.json`、独立 verifier `scripts/verify_s2_12_runner_wiring.py`、21 项 focused tests（fake transport、fail-closed、零网络）。官方价格 2026-08-19/20 上调已核账，USD cap 84.18（peak）/42.09（off-peak），授权申请 v3 给出无占位符最终命令与分阶段成本建议；未创建真实授权文件，真实 API calls=0、cost=$0；S2.12 仍 partial，S2.13 仍 blocked。 | runner wiring + frozen plan + auth schema + verifier + focused tests + v3 授权申请 + 零 API 审计 |
| 3.6.25 | 2026-08-20 | **论文侧导师要求落地（P1/P2/P3）与消融矩阵、API 授权申请（零 API）**：(1) **命名迁移 + 局限**：`paper/THESIS_DRAFT.md` 方法标题/正文迁移为正式命名（Rules-Only/Direct-LLM/Rules+LLM-Repair，legacy B0/H1/D1 仅首现映射与机器 ID），增补 Rules-Only 5 类局限与 Direct-LLM 5 类局限（每条含定量证据/文本例子/错误原因/方法边界/优化方向/为何未继续），H1 写为负结果对照（§8.8.1）。(2) **方法细模块**：Direct-LLM 拆 8 模块、Rules-Only 拆 8 模块（§4.1/§4.2），每模块含问题/输入输出不变量/去掉的失败/验证/与 Barrientos 对照；H1 对照（§4.3）。(3) **Barrientos 15 维对比表**（§4.4）与条件化综合结论，禁止单一 F1 宣称综合优劣。(4) **消融矩阵**：新建 `paper/ABLATION_MATRIX.md` 登记 AB-1–AB-10 现状（仅已有历史证据项可引用：AB-1 v5→v6 历史证据、AB-6 150/150 有效 0 事故、AB-7 细/粗/Sun-marker、AB-8 B0-R1 批次；AB-3 离线可评 def=39/231；AB-2/AB-4/AB-9 待授权、AB-10 待实现）。(5) **API 授权申请**：新建 `docs/API_AUTHORIZATION_REQUEST.md`（模型 deepseek-v4-pro、63 计划/108 硬上限、retry=0、input cap 63M、output 258,048、USD 27.63、硬停止条件、运行命令、manifest 路径、授权句模板）。(6) **正式结果回填**：论文 §7.2 填入 2026-08-11 三方法正式比较表（粗 Gold 五字段 F1 + modality label），§7.3 填入 S2.12 零 API arm。未调用真实 LLM/API、未修改 Gold、未启动 Oracle；PW3 in_progress、PW7/PW9 partial。 | 导师四项要求论文侧落地 + MASTER_PIPELINE §8.8.4 + formal comparison + S2.12 preflight + focused/full audit |
| 3.6.24 | 2026-08-18 | **S2.12 零 API 前半程 + API preflight + transition v8（零真实调用）**：构造 36-ID Gold-blind 正式输入（仅 locator/hashes）；Gold 读取前锁定并运行 `sun_rule_only`，36/36 成功、runtime 18.5112149s、0 API/network、cost=$0，预测锁定后用 evaluator v2/G0.4 parity 评价（overall modality acc/macro-F1 0.638889/0.535461；span P/R/F1 0.862319/0.802721/0.831453；L1=31/L2=5/L3=0 no samples），明确仅单一 arm、无 post-result tuning。API preflight v1 重建 direct 36 + H1 27=63 个最终 payload（max bytes 17,493、total 749,805；Legal-BERT proxy 4,960/207,468，非 billing tokens；output 4,096/call、258,048 total；retry=0），锁定 deepseek-v4-pro/prompt/config/payload hashes、官方价格与硬停止条件；实际 billing tokens/cost 仍待 response usage，0 calls。readiness v4 与 transition v8：S2.11 verified/frozen；S2.12 partial，两个 API arms pending explicit authorization；S2.13 blocked only on remaining S2.12 DoD；S3.4-S3.6 development-only；S3.7 formal Oracle not started；GRR absent；v7 保留 byte-exact，v1-v7 verifier 生命周期精确锁定。 | Gold-blind input/zero arm/evaluator + API preflight/verifier + readiness v4 + transition v8 + focused/full audit |
| 3.6.23 | 2026-08-17 | **S2.11 正式 Gold 发布（零 API）**：从 Checkpoint G 已确认且 frozen 的 36/36 canonical decisions 等值派生正式复杂语料 Gold（SHA `039ae8b2…`）；provenance 明示 `deepseek_offline_proposal_v3` + user batch confirmation by hyc（无 revisions、非从零独立专家标注）；确认事件文件 SHA `226b4798…` 与用户原句 SHA `7414a38d…` 分开绑定；source/proposal/reviewer/freeze/G0.5 drift 全部 fail-closed；版本化 schema/publisher/capsule/manifest/export/独立 verifier/replay 完成；只提交 hashes/coordinates/必要 labels，无第三方原文；S2.11=verified/frozen/Gold published，S2.12 仍 partial；零 LLM/API、无 predictions/results/GRR/Oracle | Gold publisher + independent verifier + focused tests + audit pass |
| 3.6.22 | 2026-08-17 | **S2.11 用户确认裁决与冻结 + S2.12/S2.13 状态推进（Checkpoint G，用户确认 proposal v3 一次性内容，零 LLM/API）**：(1) **用户确认**：`configs/s2_11_batch_import_confirmation_event_v3.json`（kind=s2_11_batch_import_confirmation，source=user_instruction_in_current_task，`user_instruction_utf8`=“我确认接受 S2.11 全部 36 条 canonical proposal v3 作为我的裁决（无 revisions），proposal 文件 SHA-256 = 9882ba45…，reviewer 署名：hyc”，其 UTF-8 SHA-256 7414a38d…，proposal_file_sha256 精确绑定 `9882ba45…`，revisions=null，gold_created=false，append_only=true）。(2) **importer v3 --apply 原子写入**（`scripts/s2_11_batch_import_v3.py` fail-closed）：decisions v2 36/36 adjudicated（reviewer=hyc 仅来自事件、confirmation_event 路径写入每记录）、逐字节不变备份 `.bak`、apply 后 committed dry-run 报告刷新（confirmation_event_present=true 使 run_dry_run 保持 byte-reproducible；新增 `refresh_dry_run_report_after_apply`）；main() 修复 apply 打印分支（run_apply 返回 {applied,reviewer,records,decisions_file,backup} 无 import_stats）；freeze validator v3 `frozen=true`（36/36 adjudicated、剩余 0、无 Gold）。(3) **S2.12 readiness v3 刷新**（`scripts/s2_12_build_readiness_v3.py --refresh` + `verify_s2_12_readiness_v3.py`）：schema 3.1.0，S2.11 freeze 36/36 + 确认事件 disk 绑定加入 bindings，proposal_v3.human_approved=true，runner.real_run_refused 理由更新为仅缺 API 预算授权（input token cap+cost cap），仍无最终授权句。(4) **transition capsule v7**（`build/verify_s2_13_s3_7_transition_readiness_v7.py` + schema/test/4 outputs；supersede v1-v6，55 项 superseded 全部 byte-exact 保留）：S2.11=frozen（从磁盘重推导：确认事件绑定 SHA+reviewer、decisions 36/36 adjudicated、freeze validator v3 执行）、S2.12=partial+execution-ready v3（真实运行 refused on API 授权）、S2.13=blocked、S3.7=blocked（GRR 三态 probe exist=false）；v7 VERIFIED（11 独立 verifier 全执行）。(5) **Checkpoint G 快照连锁（记录在案）**：verify_s2_12_execution_ready_v2.py 更新为 freeze 36/36 + 对 decisions v2 的 bindings 豁免（apply 合法改变其 SHA；decisions 完整性由 freeze validator v3 单独验证）；v5/v6 transition 测试更新为 superseded 快照语义（其 verifier/builder 依赖 apply 前 decisions 快照故不再自证当前有效，新增失败-关闭断言；这是对两个历史测试文件的 Checkpoint G 例外，其余 v1-v6 资产全部 byte-exact，v7 测试相应豁免这两个文件）；零 LLM/API、未创建 Gold/predictions/results、未发 API 授权句、未发布受限原文 | 确认事件 + importer apply + freeze 验证 + readiness v3 刷新 + transition v7 + focused tests + record_change 事件 + audit --with-tests |
| 3.6.21 | 2026-08-17 | **S2.11 proposal v3 最终校正与一次性确认就绪（Checkpoint F，零 LLM/API）**：(1) **六个已确认问题的复现与修复**：r10v1 双 actor span 同 ID + 条件内 customer 混入 actor + 缺 actor-action mapping → v3 显式 occurrence=1 仅保留主句执行者 `[41:53] the customer` 并建 mapping；canonical validator v2 仅查 modality evidence ID 且 collect_span_ids 字典覆盖 → **canonical v3**（`src/bpc_hybrid/s2_11_canonical_v3.py`）强制全 record 普通 span ID 唯一、clause ID 唯一、aam 边存在/同 clause/无重复/全覆盖（有 actor 的 clause 每个 action 必须有 mapping）、order 必须引用两个不同有效 action、list-based 收集（不隐藏重复）；r4v2 action/constraint overlap 18 字符 → action=raw `happen`（normalized 仅本地）+ constraint `before the surgery`，overlap=0；r8v1 `longer than 30 days` 恢复为 constraint + action=raw `sending the SIM card`（normalized）；r18v2 `immediately` 恢复为 constraint + action=raw `sent the reason for rejection`（normalized）；r3v1/r3v2 纳入 temporal-validity constraints `valid from 2024 to 2030`/`2025 to 2031`（规范性 clause span 扩展至全文，无伪 clause）；其余 30 条机械回归无证据不改写。(2) **proposal v3**（`scripts/s2_11_build_proposals_v3.py`）：span spec 支持显式 occurrence，同一文本多 occurrence 无明确选择 fail-closed；36/36 验收全零（exact-slice=0、duplicate span/clause ids=0、ambiguous auto-occurrence=0、invalid/missing aam=0、invalid orders=0、action/constraint overlap=0、evidence missing=0、unresolved=0、display None=0）；本地完整包 `adjudication_proposals_v3/`（proposals.jsonl/decision_package.md/v2→v3 diff/quality report；SHA `9882ba45…`）；提交报告 `s2_11_proposal_report_v3.json`（坐标/hash/计数，零 ≥40 字符原文片段）；**proposal v1/v2 superseded（v2 状态 superseded_pending_targeted_correction_do_not_approve），v1/v2 文件逐字节保留**。(3) **importer v3**（`scripts/s2_11_batch_import_v3.py` re-bind proposal v3）：dry-run blocked=0/unresolved=0/adjudicable=36/36；`--apply` fail-closed（确认事件绑定 proposal v3 SHA+revisions SHA+reviewer、原子写+备份）；freeze validator v3（canonical v3 + 7 项 checks）+ review tool v3；**本轮未创建确认事件、未 apply、freeze=false、无 Gold**。(4) **S2.12 readiness v3**（`scripts/s2_12_build_readiness_v3.py` + `verify_s2_12_readiness_v3.py`）：评估器 v2 不重写，parity 重跑通过并 re-bind proposal v3/importer v3 hash；API readiness 保持 dry-run（两臂 deepseek-v4-pro、36/72/108 calls、输出 4096、输入未文档化、cost_cap_unresolved、**无最终授权句**、缺项精确列出）。(5) **transition v6**（47 项 supersedes、11 个独立 verifier、V6 VERIFIED；v1–v5 逐字节保留且各自 verifier 继续通过；S2.11=只剩绑定 proposal v3 SHA 的一次性用户内容确认、S2.12=partial+execution-ready v3、S2.13 blocked、S3.7 未启动、GRR 不存在、无 Oracle 授权句）；零 LLM/API、未伪造 Gold、未发布受限原文 | Checkpoint F 构建器/验证器 + focused tests + record_change 事件 + audit --with-tests |
| 3.6.20 | 2026-08-17 | **S2.11 canonical proposal v2 校正 + 可一次接受导入 + S2.12 正式评价口径对齐（Checkpoint E，零 LLM/API）**：(1) **canonical v2 数据模型**（`src/bpc_hybrid/s2_11_canonical_v2.py` + blank pack/decisions v2 + freeze validator v2 + review tool v2）：字段三态 unresolved/absent/present（absent 是明确裁决的"不存在"，不再用 null 混淆 absent 与未裁决）；modality=status+label+1..N 字节验证 evidence spans；actor/action/condition/constraint/exception=span 数组（多值支持）；actor-action map + order relations（span id 引用）；adjudicated 仅要求无 unresolved、允许合法 absent；复用 Stage 2 canonical span 惯例（text==source[start:end] 运行时对 hash 绑定原文验证；提交文件仅坐标）。(2) **36 条独立语义复核**（`scripts/s2_11_build_proposals_v2.py`）：modality label 与 evidence 分离（evidence 为原文规范性 cue 精确子串，如 must/has to/is prohibited from/is not obligated/are not eligible/should/can/is necessary 等）；动作改为完整连续动词短语（r18v2 `be immediately sent the reason for rejection`、r17v1 拆 `assess the donor`+`record the reason in the system` 并建 order、r2v1/v2 拆双 clause+order、r9v2 constraint 修正含弯引号原文）；被动句执行者未出现一律 actor=absent（受事者不冒充）；`not obligated`/`not needed` 纠正为 permission（非 prohibition）、`even if` 从句为 exception、change-version 对（100→50、or→and、15→20、nurse→doctor 等）逐一体现在 span/条件；14 条 needs_attention（confidence high 23/medium 9/low 4）；**proposal v1 声明 superseded 不可批准**（v1 文件逐字节保留）；v2 本地完整包（proposals.jsonl/decision_package.md/v1→v2 diff/quality report，仅 gitignored）+ 提交报告 `s2_11_proposal_report_v2.json`（坐标/hash/计数，零原文片段，proposal SHA 93866427…）；验收测试强制：coverage 36/36、exact-slice=0、evidence missing=0、value_missing_in_text=0、display None=0、duplicate/missing/extra=0、hash drift 拒绝。(3) **importer v2**（`scripts/s2_11_batch_import_v2.py`）：dry-run blocked=0/unresolved=0/adjudicable=36/36（would-be 通过 freeze validator v2 全部结构检查）；`--apply` 实现但 fail-closed——必须用户确认事件精确绑定 proposal v2 SHA+revisions SHA+reviewer、原子写+写前备份、reviewer 只能来自事件；**本轮未创建确认事件、未 apply、freeze=false、无 Gold**。(4) **S2.12 正式口径对齐**（`s2_12_stratified_evaluator_v2.py`：modality label acc/macro-F1/per-class + 五字段 Sun literal-overlap span P/R/F1，复用正式 stage2_evaluator_s210_v3 合同与共享 literal-overlap 模块；L3=0 明确无样本不造 0 分；`s2_12_method_adapter.py` 方法适配 dry-run ready；**parity 测试**证明同一 fixture 经正式 Stage 2 evaluator 与 stratified wrapper 未分层总体一致）；plan/readiness v2（supersede v1，reason=evaluator/Gold-shape correction）只声称 schema/importer/evaluator/adapter ready，不声称 Gold/正式评价完成；**API readiness v2**：direct_llm=deepseek-v4-pro（D1 registry 钉死）、sun_llm_fallback=deepseek-v4-pro（H1 全量 run manifest，cli_override；trigger 语义：150 记录 111 样本 150 调用→派生每记录上限 2→72）、max_calls 36/72/108、输出 token 4096、**输入 token 未文档化 + cost_cap_unresolved（仓库无可信价格依据）→ 未发出最终授权句**，缺项精确列出、calls_made=0。(5) **transition v5**（supersede v1–v4，39 项 supersedes；S2.11=canonical v2 未裁决、只剩一次性用户确认；S2.12=partial+execution-ready v2；9 个独立 verifier 全执行；v1–v4 逐字节保留且各自 verifier 继续通过）；S2.13 blocked、S3.4–S3.6 development-only、S3.7 未启动、GRR 不存在、无 Oracle 授权句；零 LLM/API、未伪造 Gold、未使用 API 授权句、未发布受限原文 | Checkpoint E 构建器/验证器 + focused tests + record_change 事件 + audit --with-tests |
| 3.6.19 | 2026-08-17 | **S2.12/S2.13 执行就绪 + transition v4（Checkpoint D，零 LLM/API）**：(1) **S2.12 执行计划冻结**（`configs/s2_12_execution_plan_v1.json` + `outputs/reports/s2_12_execution_plan_v1.json`，builder `scripts/s2_12_build_execution_ready.py`）：预注册 G0.5 L1/L2/L3 分层（36 条密封链分类 L1 31/L2 5/L3 0）、三臂同一输入/Gold/evaluator、DoD 重述、retrospective 描述性分析明确标记为历史；Gold=用户裁决 S2.11 decisions（当前 0/36，pending）。(2) **fail-closed runner/evaluator readiness**（`src/bpc_hybrid/s2_12_stratified_evaluator.py` 确定性分层 per-field P/R/F1+错误类型 correct/missed/misclassified/extra，sample set 精确匹配、缺字段/坏 level/空集全拒绝；synthetic fixtures 通过；`outputs/reports/s2_12_execution_readiness_v1.json`：real_run_refused=true、gates ready=false、无 Gold、零 API）。(3) **API 预算 dry-run**：typical 72（36 条×2 LLM 臂×1）/hard cap 100、calls_made=0、authorized=false、可复制授权句存在但 sentence_used=false（本轮零调用，未使用授权句）；独立 verifier `scripts/verify_s2_12_execution_ready.py` 15 项 PASS（绑定重算、合成重跑、dry-run 状态、无 API 事件）。 (4) **transition readiness v4**：v4 capsule（schema/build/verify/test/reports，supersede v3 的 S2.11 workload 推导（改为空白 pack 36=29+7）与 S2.12 判断（改为 partial+execution-ready）；新增 8 个独立 verifier 之一 verify_s2_12_execution_ready；v1/v2/v3 全部逐字节保留且 verifier 继续通过；v4 验证器 8 项外部 verifier 全执行 V4 VERIFIED）。(5) 文档一致性：MASTER S2.11 行不再 blocked（in_progress_human_adjudication，Checkpoint C 已改）、G0.5=frozen、transition 当前=v4（v3 previous）、§12.0 与 S3.7 行引用更新、gap capsule 继续声明 superseded、S1.7=frozen 未动；S2.12=partial+execution-ready、S2.13 blocked、S3.7 未动；零 LLM/API、未伪造 Gold、未使用 API 授权句、未发布受限原文 | Checkpoint D 构建器/验证器 + focused tests + record_change 事件 + audit --with-tests |
| 3.6.18 | 2026-08-17 | **S2.11 全量裁决加速：完整 review 人口 + 36 条离线 AI 提案 + dry-run 批量导入（Checkpoint C，零 LLM/API）**：(1) **review 人口封闭 40/4/36**：inventory 40 → 客观排除 4 条空文本（QUARANTINE_EMPTY_TEXT，原始字节重验）→ nonempty=review population=36；29 条候选 available + 7 条 unavailable（4 条 MODALITY_UNKNOWN：blood r16v1/r17v1/r17v2、SIM r10v1；3 条 FIELD_SPAN_AMBIGUOUS：emergencies r2v1/r2v2/r3v1，均带稳定错误码）；候选失败绝不缩减 review 人口（消除"候选成功决定 review"选择偏差）；review surface schema 升到 s2_11_review_surface@1.1.0（空白 pack `s2_11_blank_review_v1.json` 36 条全 null/unreviewed + 决策文件 `s2_11_review_decisions_v1.json` 36 条 + G5 报告/manifest，binding 在文件写出后计算）；冻结验证器改为从空白 pack 读期望 36 ID 并强制 sample set 精确相等（缺/多/重均拒绝）；review 工具支持 unavailable 项（candidate=null + candidate_error）。 (2) **36 条离线 AI 裁决提案**（`s2_11_generate_proposals.py`，deepseek_offline_proposal，human_approved=false、gold=false、reviewer 永不=user；字段值全部为原文精确子串且 span 字节验证 text[i:i+len]==value，缺失字段=null 绝不虚构；confidence high 13/medium 19/low 4；needs_attention 8 条；G0.5 级别经密封 v6 链 classify_frozen 计算）；完整原文+提案仅 gitignored 本地目录（proposal SHA-256 14c1ec90… 绑定于提交报告），提交报告 `s2_11_proposal_report_v1.json` 仅坐标/hash/计数（连续 ≥40 字符原文片段=0，全 4 个已提交 review 资产复检）。 (3) **dry-run-only 批量 accept/revisions 导入工具**（`s2_11_batch_import_dry_run.py`）：绑定提案文件 SHA-256、验证 36 成员与全部 hash、accept-all+listed revisions（修订值须为原文精确子串，字节验证）、fail-closed（无用户确认事件 → 不写决策文件、--apply 拒绝 exit 2、本轮不创建确认事件）、reviewer 永不=user、would-be 决策全部 review_state=reviewed 待用户确认；导入规则：modality=受控词表类标（无 span 也导入），actor/action/condition/constraint/exception 仅当值为原文精确子串（未找到/多值 → decision=null + import_blocked 记录，本轮 10 字段/7 样本）；dry-run 报告 `s2_11_batch_import_dry_run_v1.json` 已提交（同样零原文片段）。 (4) **transition v3 重推导**：v3 验证器成功横幅 "V2 VERIFIED" 误标修复为 "V3 VERIFIED"；因空白 pack/决策文件演进 + 验证器脚本 hash 变化，v3 capsule（report/md/manifest/export index）按字节一致重建并重新验证（v1/v2 文件与验证器逐字节保留）。 (5) 测试：S2.11 聚焦测试更新至 36 人口语义 + 新增提案/批量导入测试（确定性强、无确认事件路径、篡改拒绝），全量审计 exit 0；S2.11=in_progress_human_adjudication（36 条待用户裁决）、S2.12 partial、S2.13 blocked、S3.7 未动；零 LLM/API、未伪造 Gold、未发布受限原文 | Checkpoint C 构建器/工具/验证器 + focused tests + record_change 事件 + audit --with-tests |
| 3.6.14 | 2026-08-15 | **S2.11/G0.5 用户决策包 v5：修复 v4 红测、历史 capsule 生命周期、真实 provenance/evidence binding 与 G0.5 原始字节绑定（零 API/零 gate 翻转）**：(1) **v4 红测修复**：v4 变更事件如实记录 3 failed / 2057 passed / test_returncode=1 / integrity_pass=false；v5 引入集中式历史 capsule 生命周期语义（`src/bpc_hybrid/capsule_lifecycle.py`）——v3/v4 核心资产（schema/builder/verifier/4 outputs）逐字节不变（git 证明），其 pytest 文件仅按生命周期语义修正（历史 builder 在绑定资产演进后 no-overwrite fail-closed、历史 verifier 拒绝且失败项属于声明性 binding drift、历史负例测试继续真实执行）；v5 全量审计恢复 exit 0（不含 xfail/skip/过滤）。(2) **adapter 严格 mode 枚举**：`{synthetic_test_only, formal}` 之外一律 INVALID_MODE（`mode="production_typo"` 被拒）。(3) **真实 evidence binding**：formal mode 要求文件级绑定——相对安全路径（禁绝对/`..` 逃逸）、64 位小写 hex SHA-256、原始字节重算一致、evidence 文档内部 kind/ID/scope 一致、authorization manifest 精确绑定 policy ID/modality mapping/field mapping/license evidence hash/scope；synthetic binding/缺文件/错 hash/错 ID/错 kind/路径逃逸全拒绝；formal 正例仅用 pytest 临时目录 synthetic 文件；当前磁盘仍拒绝一切 formal 转换。(4) **可验证字段级 provenance**：source_record_id/source_path 非空合法（`str(None)` 伪装拒绝）、结构字段 element 精确等于 mapping key、modality element 精确匹配 `norms[<idx>].modality`、字段 path 必须等于确定性 locator `record_source_path#element`、record path 不得含 `#`、bool 不得作为 offset、重叠 span ambiguity（`"aaa"` 中 `"aa"` 两个起点）检测、未知 descriptor 字段拒绝。(5) **G0.5 原始字节 hash 域**：`validate_frozen_application` 改为接收真实文件路径并只对原始字节算 SHA-256；dry-run G4 句绑定 draft config 原始字节 `61938c99…`（语义重序列化 hash `51a6e4fe…` 被 validator 拒绝）；`classify_frozen` 仅接受完整验证结果（含不可伪造 validation_token = manifest 原始字节 hash）；`derive_promotion_readiness` 不再仅凭 glob 文件名判 ready，必须解析并验证完整资产组合（当前磁盘仍 draft_not_frozen / promotion_ready=false）；不创建真实 frozen config 或授权 manifest。(6) v5 capsule（schema/builder/verifier/30 项测试/JSON/MD/manifest/export index）supersede v3/v4 当前状态判断（v3 4 决策项 + v3 8 文件 + v4 8 文件 = 20 项 supersedes，全部 hash 绑定）；gate 状态 G1/G2/G5/G6 false+null、G3/G4 dry-run（G4 绑定原始字节 hash、仅未来 gate-application checkpoint）、S3.7 全 false/null；MASTER/PROJECT_AUDIT v5 为当前决策入口（v3/v4 历史）；全量审计 exit 0（2118 passed / 24 skipped / 19 warnings（v5 最终 receipt））；零新增 LLM/API，Gold/contract/methods/predictions/results/references/Stage 3 gate/S2.11-S2.13 状态均未修改，未生成 Oracle 授权句 | 决策包 v5（builder/verifier/manifest）+ capsule_lifecycle + adapter 加固 + G0.5 原始字节绑定 + record_change 事件 + audit --with-tests（exit 0） |
| 3.6.15 | 2026-08-15 | **S2.11/G0.5 授权链封闭与固定锚点（v6，零 API/零 gate 翻转）**：(1) **frozen 授权链封闭**：v5 的 caller-supplied validation-result 解锁方式被反例推翻（手工字典含任意 64 位小写 hex token 即可解锁 v5 classify_frozen）；v6 移除该参数，classify_frozen 每次调用从磁盘重验 draft/frozen config、授权 manifest、append-only 授权事件与 prior-results 证据扫描（后者由确定性路径/manifest 规则推导，不再接受 caller bool）；授权 manifest 完整绑定 schema/version、manifest ID、authorization_applied=true、精确批准 scope 枚举、精确 G4 dry-run 句全文 + UTF-8 SHA-256、draft/frozen 相对路径 + 原始字节 SHA-256、回退/冻结前/S2.10 禁用标志、重推导 prior-results 扫描、授权事件（ID+路径+原始字节 SHA-256）与 pending（未应用）checkpoint；全部变体被拒（另一 manifest 的 token、manifest 修改后旧 token、句/scope/事件/路径替换、先出结果后构造授权、仅布尔/伪造 hash 声称已验证）；普通内容 hash 不被当作用户授权证明。(2) **历史 capsule 固定锚点**：v3/v4/v5 核心资产逐字节不变，锚定固定 origin commit（31ac757d…/8e8b488e…/7883739…）+ 硬编码 21 项 SHA-256 map（capsule_lifecycle.py）；磁盘字节和 origin-commit blob 均须匹配固定 map；新增回归测试证明“HEAD 与磁盘同时被替换为同一错误字节”仍失败；v6 report/manifest 绑定三版固定 hash。(3) **adapter evidence provenance（v6）**：证据 verifier 返回结构化 EvidenceContext；formal 输出新增 formal_evidence_provenance（license/manifest/事件 ID+路径+原始字节 SHA-256+精确 scope、policy ID、modality/field mapping canonical hash、manifest 绑定说明、candidate_only=true/gold_authorized=false），synthetic mode 为 null；scope 受控枚举（article-only 不满足 artifact code/data），manifest 必须精确复述 license scope；evidence 路径 resolve() 后必须在 evidence root 内（symlink/junction 逃逸被拒）；当前磁盘无合格 evidence，一切真实 formal 调用仍被拒。(4) **v5 事实如实记录**：v5 全量审计确实为绿（最终 receipt 2118 passed / 24 skipped / 19 warnings in 941.91s）、不是红测 checkpoint、历史事件保留；但 v5 的 hand-built validation-result 防护声明被本轮反例推翻（与审计绿灯分开记录）。(5) **G0.5 未冻结**：授权 hash 域仍为原始字节 61938c99…，51a6e4fe… 永不使用；G3/G4 仅 dry-run；G1/G2/G5/G6 ready=false+null；S3.7 全 false/null；S2.11/S2.12/S2.13/Stage 3 门未改；未生成 Oracle 授权句 | v6 capsule（builder/verifier/manifest）+ 固定锚点 + g05/adapter 链封闭 + record_change 事件 + audit --with-tests |
| 3.6.16 | 2026-08-17 | **S2.11/G0.5 非 API 决策应用与 G0.5 冻结（Checkpoint A，用户授权，零 LLM/API）**：用户转发授权原句 `除了用apikey的时候要授权，其他直接正常进行即可。`（UTF-8 SHA-256 a8a1dec4…）记录于 `configs/s2_11_user_authorization_event_v1.json`（append-only、精确 scope 与 containment）；G1=resolved_for_local_nonredistributive_analysis（artifact 许可未知，91 文件盘点无 license 文件，license_verified=false，本地只读研究使用、禁止再分发/公开原始数据、禁止修改 references）；G2=applied_local_read_only（scope=local_read_only_nonredistributive_s2_11，formal run 只读 membership 文件）；G3=applied（M1 modality identity candidate mapping，candidate-only，definition 不自动生成）；G6=applied（S0_no_automatic_structural_mapping，field_mapping={}，真实 artifact 无叶子 span 结构字段）；G4=applied（`configs/g05_complexity_frozen_v1.json`：status=frozen、frozen_before_new_results、retrospective/s2_10 forbidden、scope=future_external_complex_corpora_only，经 v6 密封链完整验证——draft 原始字节 61938c99…、授权 manifest、append-only 事件、空 prior-results 扫描；G0.5=frozen_for_future_external_complex_corpora，draft 保留为历史，S2.10 不重标 preregistered，冻结前无候选/结果）；G5 待 Checkpoint B；v6 capsule 转为历史安全基线（核心资产字节不变）；S2.11 仍 blocked（待候选生成+人工裁决）、S2.12 partial、S2.13 blocked、S3.7 未动；零 LLM/API、未伪造 Gold、未发布受限原文 | Checkpoint A builder/verifier + focused tests + record_change 事件 + audit --with-tests |
| 3.6.17 | 2026-08-17 | **S2.11 语料激活与人工 review surface（Checkpoint B，零 LLM/API）**：真实 Barrientos requirement 语料本地只读激活——3 文件 40 记录 hash-only membership（4 条空文本隔离）；确定性模态抽取（文档化关键词规则+精确 span）→ hardened adapter `local_read_only_research` 模式（许可未知不声称 verified、用户授权事件+containment 证据）→ 29 条候选（obligation 21/permission 2/prohibition 6；G0.5 frozen L1×28/L2×1；provenance 29/29）＋7 条运行期隔离（MODALITY_UNKNOWN/FIELD_SPAN_AMBIGUOUS，共 11 条）；完整候选（含原文）仅 gitignored 本地目录，提交资产仅统计/hash/ID/隔离码；G5=applied_review_surface_open（29 samples 空白 pack 全 null + 用户决策文件 + review 工具（hash 只读加载原文、原子写、备份、resume、progress）+ 冻结验证器，无预填 Gold）；S2.11=in_progress_human_adjudication（29 条待用户裁决＋11 条隔离）；transition readiness v3 重推导（v1/v2 字节保留）；S2.12 partial、S2.13 blocked、S3.7 未动；零 LLM/API、未伪造 Gold、未发布受限原文 | Checkpoint B 运行/工具/验证器 + focused tests + record_change 事件 + audit --with-tests |
| 3.6.13 | 2026-08-15 | **S2.11/G0.5 用户决策包 v4（纠正）：许可证据分离、adapter provenance 加固、G0.5 promotion readiness、gate 顺序修复（零 API/零 gate 翻转）**：(1) 论文许可确认——`references/papers/Barrientos_2026_Impact_analysis.pdf`（sha256 6ce91fd2…，1,822,940 B）只读证据链：标题/DOI 10.1016/j.infsof.2026.108079/Elsevier 正文 "open access article under the CC BY license" 声明/artifact URL（anonymous.4open.science）；`paper_readable=true`、`article_license=CC-BY-4.0`（article_only）、`article_license_does_not_auto_cover_artifact=true`；artifact code/data 仍 `unknown_pending_confirmation`、`project_activatable=false`、`ready_for_data_activation=false`、激活授权句 null；(2) adapter 加固（`src/bpc_hybrid/s2_11_barrientos_adapter.py`，38 项真实执行测试）：record-level 与 field-level provenance 分离、每个 source element 自带 element/path/record ID/text hash/span/alignment source/policy ID、modality provenance 指向 norm element、结构字段不复用全局 span、canonical target 白名单 {actor/action/condition/constraint/exception}、NON_CANONICAL_TARGET/TARGET_COLLISION/FIELD_PROVENANCE_MISSING/FIELD_SPAN_INVALID/FIELD_SPAN_AMBIGUOUS/FIELD_VALUE_MISMATCH/NESTED_DICT_AS_SPAN_FIELD/ELEMENT_PATH_MISMATCH/EVIDENCE_BINDING_MISSING/EVIDENCE_BINDING_SYNTHETIC typed fail-closed；formal mode 要求版本化 license/authorization evidence bindings（当前磁盘无 → 拒绝）；synthetic/shadow only；(3) M1 精确范围=modality identity candidate ONLY（结构字段映射需独立 G6）；M2 不映射任何外部 label；(4) G0.5 promotion readiness（`g05_complexity_candidate.py` 扩展）：当前 `g0_5_status=draft_not_frozen`、`promotion_ready_for_application=false`、missing=user authorization manifest；未来冻结应用路径（frozen config + 授权 manifest 绑定 draft/frozen hash/scope/授权句/frozen_before_new_results=true/无先行结果/禁回溯）以 synthetic fixture 实现并测试（+8 项）；(5) gate 顺序修复：G1（artifact license）/G2（activation）/G5（Gold review surface，protocol_ready=true 但 ready=false/null，条件式 future sentence）/G6（结构映射）ready=false+null；G3 ready=true（M1 dry-run 句）；G4 ready=true（句子绑定精确 config SHA-256，仅授权未来 gate-application checkpoint，明确 "does NOT freeze G0.5 this round"）；v4 capsule supersede v3 的 license four-state/adapter-completeness/G4-G5 readiness 判断，v3 全文件逐字节保留；MASTER/PROJECT_AUDIT v4 为当前决策入口（v3 历史）；**全量审计为红灯（v4 变更事件如实记录：3 failed / 2057 passed / 24 skipped，test_returncode=1，integrity_pass=false——v3 历史正例测试在 v3 绑定资产（adapter/文档）被本轮任务要求演进后按 fail-closed 设计拒绝；该红灯由 v5 的历史 capsule 生命周期语义修复，v5 全量 exit 0）**；零新增 LLM/API，Gold/contract/methods/predictions/results/references/Stage 3 gate/S2.11-S2.13 状态均未修改，未生成 Oracle 授权句 | 决策包 v4（builder/verifier/manifest）+ adapter 加固 + G0.5 promotion readiness + record_change 事件 + audit --with-tests（v4 全量 exit 1） |
| 3.6.12 | 2026-08-15 | **S2.11/G0.5 授权前工程收口与用户决策包 v3（零 API/零 gate 翻转）**：(1) Barrientos adapter 核心 `src/bpc_hybrid/s2_11_barrientos_adapter.py`——synthetic/shadow implementation verified，仅接受显式输入、不扫描 references/；fail-closed typed 错误码（LICENSE_NOT_QUALIFIED/ACTIVATION_NOT_AUTHORIZED/MAPPING_POLICY_NOT_APPROVED/SYNTHETIC_POLICY_IN_FORMAL_MODE/INVALID_STRUCTURE/UNKNOWN_MODALITY/DEFINITION_NOT_PRODUCIBLE/MAPPING_POLICY_INCOMPLETE/INVALID_MAPPED_MODALITY/MISSING_TEXT_PROVENANCE/MISSING_SPAN_ALIGNMENT/INVALID_SPAN/AMBIGUOUS_SPAN/UNRESOLVED_CROSS_REFERENCE）；输出仅 candidate_only/review_candidate，external_annotation 仅 review aid；(2) 重写 `test_g07_barrientos_adapter_contract.py`（删除 `or True` 空断言，25 项真实执行测试）；(3) G0.5 候选合同 `configs/g05_complexity_candidate_draft_v1.json`（status=draft_not_frozen、retrospective_use_forbidden、L1/L2/L3 确定性规则/优先级/边界/缺失与冲突处理，覆盖 MASTER 要求的全部复杂度字段）+ `src/bpc_hybrid/g05_complexity_candidate.py` + 20 项 synthetic 边界测试；(4) 用户决策包 v3（schema/builder/独立 verifier/30 项测试/JSON/MD/manifest/export index）：许可核账只读（references/barrientos_2026 91 文件按 名称+sha256+size 盘点、无 LICENSE/COPYING/NOTICE/README/metadata → license_status=unknown_pending_confirmation、ready_for_data_activation=false、activation 授权句 null；paper/code/data/activation 四分状态）；映射选项 M1（identity candidate mapping，推荐）/M2（conservative no-mapping），未应用；空白人工 Gold 协议（review/adjudication/freeze/publication 分离、user_only、未创建 data/gold）；分离用户门禁 G1（许可证据，ready=false/null）/G2（激活，ready=false/null）/G3（映射选择，ready=true + dry-run 授权句）/G4（G0.5 冻结，ready=true + dry-run 授权句）/G5（空白 Gold review surface，ready=true + dry-run 授权句）；manifest 精确集合重建 + export 精确重建 + 单 EOF newline + 全部篡改负例 fail-closed；MASTER S3.7/下一真实路径改指 v2 transition capsule（v1 历史），新增 §12.0b；PROJECT_AUDIT 过渡核账行明确 v2 当前/v1 历史、S2.13 行 adapter 状态更新、证据入口加 v3；全量测试通过；零新增 LLM/API，Gold/contract/methods/predictions/results/references/Stage 3 gate/S2.11-S2.13 状态均未修改，未生成 Oracle 授权句 | 决策包 v3（builder/verifier/manifest）+ adapter + G0.5 draft + record_change 事件 + audit --with-tests |
| 3.6.11 | 2026-08-15 | **S2.13→S3.7 transition readiness v2：收敛 Gold 缺失探测、manifest/export 完整性校验与实时状态矛盾（零 API/零 gate 翻转）**：v1 capsule 全部文件逐字节保留（v1 verifier 继续通过、git hash-object 与 HEAD 一致）；新建 v2 capsule（schema/build/verify/test/reports，8 文件）——**Gold Rule Records 三态探测**（无候选→exist=false + 9 rule IDs + 显式绑定被检查的 Stage 2 EStG-150 Gold path/hash；任何 rule_record/rule-record 命名候选（data/gold/**、outputs/reports/**、历史 readiness 文档提及的具体路径）→ builder fail-closed 报错并列出路径，绝不报告 exist=false、绝不自行提升；exist=true 保留给未来用户授权 freeze/publication 路径，v2 未实现）；**manifest 精确重建**（verifier 在内存用磁盘 report/MD 字节与重收集 bindings 重建完整 manifest，与磁盘逐键比较，缺项/多余项/byte_size 篡改/同步重算 export hash 均 fail）；**export index 精确重建**（磁盘 report/MD/manifest 字节确定性重建，结构完全相等，重算哈希不能绕过）；**严格 verifier 判定**（非 JSON verifier 需 exit 0 + 显式成功行，"VERIFIED" 裸子串因 "NOT VERIFIED" 也包含而被拒绝）；Markdown 单 EOF newline；audit false 分支措辞改为仅描述真实计算条件并明示与 S2.13/S3.7/full-pipeline 无关（gate 计算/合同/状态值未变）+ true/false 双向回归测试；PROJECT_AUDIT 陈旧行原位收敛（sun_rule_only/D1/正式结果目录/S2.4-6/B0-R2-R5/S3.2-S3.3/当前派工/§1 结论），队列与派工收敛为真实下一路径（S2.11/G0.5 → S2.12 → S2.13 → 用户 Gold Rule Records → S3.4-S3.6 → S3.7 单独授权）；MASTER P1-P4 里程碑修正（P1 数据/Gold 完成但 G0.5/S2.11 未完成；P2 完整 B0 完成；P3 三方法正式比较完成、复杂扩展未完成；P4 D1 正式 arm 已发布、H1 comparison-only、复杂集仍 blocked）；全量测试通过；本轮零新增 LLM/API，Gold/contract/methods/predictions/results/Stage 3 gate/S2.13 状态均未修改，未生成 Oracle 授权句 | 过渡 capsule v2（builder/verifier/manifest）+ audit.py 措辞修复 + PROJECT_AUDIT/MASTER 收敛 + record_change 事件 + audit --with-tests |
| 3.6.10 | 2026-08-15 | **S2.13→S3.7 过渡核账与 fail-closed readiness 加固（过渡控制 capsule v1，零 API/零 gate 翻转）**：新建确定性过渡控制 capsule `s2_13_s3_7_transition_readiness_v1`（schema + builder + 独立 verifier + 14 项聚焦测试 + JSON/MD/manifest/export index）——逐项从磁盘资产/manifest/hash/实际执行的独立 verifier 重新推导依赖矩阵（S1.7=frozen；S2.10=verified；S2.11=blocked（许可/数据激活/3→4 映射/人工 Gold/G0.5/Barrientos adapter 精确 blockers 重读自 s2_11 资产）；S2.12=partial/retrospective；S2.13=blocked（DoD 未改、未拆新任务）；Stage 1 Process Gold 存在且 verifier 通过（7/135/7）；Stage 3 matching 25+violation 33 decision Gold 存在且与 frozen correction 一致（≠ Gold Rule Records）；9 个 GDPR rule IDs（article6/7/15/16/17/20/22/33/34）的正式 Gold Rule Records 不存在且本轮未创建/未推断；S3.4/S3.5/S3.6=development_only；formal_oracle_started=false、formal_oracle_authorized=false、ready_for_oracle_authorization=false、authorization_sentence=null、no_pseudo_oracle=true）；旧报告（s2_13_stage2_freeze_gap_capsule.{json,md}、s3_7_oracle_readiness_v2、s37_oracle_readiness_v1、formal_benchmark_release_v2 历史 exclusions、两个硬编码“Process Gold 不存在”的旧 builder）声明 supersede 其“当前状态判断”，文件本身逐字节保留未修改；audit.py 陈旧静态尾部改为动态生成（final_experiment_ready=true 仅代表 Stage 2 三方法正式评价/最终指标机器门禁就绪，不代表 S2.13/S3.7/全 Pipeline 完成），新增矛盾消除回归测试；独立 verifier 实际运行 7 个既有 verifier + 重跑 audit 并逐项比对；全量测试通过；本轮零新增 LLM/API，Gold/contract/methods/predictions/results/Stage 3 gate/S2.13 状态均未修改，未生成 Oracle 授权句 | 过渡 capsule v1（builder/verifier/manifest）+ audit.py 措辞修复 + record_change 事件 + audit --with-tests |
| 3.6.9 | 2026-08-10 | **formal Gold 发布授权执行（用户授权，packet v2 落地）**：按
ormal_gold_authorization_packet_v2 执行机器合同变更（实际授权日 2026-08-10）——stage3.status→locked（含 relock_note 2026-08-10）、
ormal_gold_publication_gate.status→
eady_for_formal_gold_publication（白名单精确匹配 + 授权 note）、stage2_dataset.freeze_policy→完整重锁文本（保留数据/许可/冻结范围/禁止事项治理，仅更新已满足的 pending/relock 状态）；audit：formal_gold_publication_ready **False→True**、BLOCKERS 5→3（消除 formal_gold_publication_paused、stage3_benchmark_not_locked；保留 final_experiment_not_ready/formal_methods_not_ready/formal_capsule_not_frozen）、final_experiment_ready 仍 False；formal Gold 已可发布（LLM-assisted human-adjudicated）；不隐含 S1.7/S2.13/Gold Rule-Process Records/formal Oracle/最终实验完成，不授权任何 LLM/API | 用户授权（packet v2 授权句）+ audit --with-tests + record_change 事件 |
| 3.6.8 | 2026-08-08 | **BM25 candidate-specific 语义修复 + S3.6-A v3 重跑 + Stage 3 method registry v2 + formal Gold 授权包 v2**：BM25 v1/v2 的 sim(a,b) 忽略候选文本（返回 action corpus 最佳文档分数）→ 固定选第一个 action、actor/BO 误用 action corpus、order 可能映射错误 ID；修复：BM25Index candidate-specific score(query,candidate)（候选自身 tf/dl + 域语料 IDF/avgdl，真实 [0,1] 上界归一化 sum(IDF*(k1+1))，b 真实生效，空输入=0）、BaselineScorer 双域 sims factory + 真实 action ID 映射 + 确定性 tie-breaking/duplicate；BM25 v3（config v3 + run v3：MAP 0.6833→0.6595、binary F1 0.4→0.0，v2 invalid → v3 corrected before/after 报告）；v1/v2 标记 superseded_invalid_candidate_agnostic_similarity（不入 comparison/registry active/论文）；TF-IDF 经内容级 byte-identical 验证不受 ID 修复影响（无 duplicate labels）保留 v2；registry v2（active 指向 BM25 v3、superseded_invalid_runs=v1/v2、frozen_at 非 null、config 三 hash 区分：run snapshot/run manifest/当前工作树）；authorization packet v2（JSON Pointer 完整 before/after、freeze_policy 治理内容保留仅更新状态、临时副本门禁校验 False→True、活动合同字节断言未变、明确 formal Gold 与方法正确性为不同门禁）；全量 1621 passed/24 skipped；未读 .env/未调 LLM/未改 Gold/BPMN/correction/未翻转任何正式门禁 | registry v2 + packet v2 + audit --with-tests + record_change 事件 |
| 3.6.7 | 2026-08-08 | **S3.6 sensitivity 修复 + Stage 3 development 方法冻结注册表 + S3.7 前置核账 + formal Gold 授权包（dry-run）**：(1) baseline sensitivity 方法修复——BaselineScorer 的 gamma/theta 影响映射/R/C/分母/可观测性，sweep 改为重实例化 scorer 重算（删 mappings parameter-free 错误声明；matching tau 仍为固定 score cutoff；5 项手算 fixture 证明 gamma 改变 missing/actor observability/order denominator、theta 改变 actor 判定）；v2 runs（主阈值 0.5 不变，主指标与 v1 byte-identical）；(2) 措辞修正：Sun config 输入（inference pack=运行输入、blank pack=验证/溯源）、S3.6 阈值 0.5（fixed development setting before this run、非 blind preregistration、benchmark exposure 未排除）；(3) 方法冻结注册表 configs/stage3_development_method_registry_v1.json（5 方法：run/config/implementation/evidence capsule hashes、primary thresholds、exposure 状态、已知局限、formal_oracle_claim_allowed=false、confirmatory_claim_allowed=false、变更须新版本）；(4) S3.7 Oracle 输入真实性核账 outputs/reports/s37_oracle_readiness_v1.json——真正 Gold Rule/Process Records 均不存在（adapter 输出≠Gold），status=blocked_on_s1_7_s2_13，禁止伪 Oracle；(5) formal Gold 用户授权包 outputs/reports/formal_gold_authorization_packet_v1.{json,md}（dry-run：route/stage2/stage3/gate/freeze 现状+证据、拟议 before/after、预期 blocker 消除/保留、回滚、授权句；未修改合同）；全量 1609 passed/24 skipped；未读 .env/未调 LLM/未改 Gold/BPMN/correction/未翻转任何正式门禁 | registry/readiness/packet + audit --with-tests + record_change 事件 |
| 3.6.6 | 2026-08-08 | **S3.4/S3.5 证据与评价合同修复 + S3.6 非 LLM baseline 闭环（§9.5 S3.4/S3.5/S3.6）**：(1) Gold-blind inference pack（stage3_inference@1.0.0：item_id/process_id/rule_id/rule_text/check_type，无 decision/candidate/evidence，打乱不变；Winter/Sun 移除 idx%3 与 candidate 路由）；(2) 公共 evaluator：unobservable 按 check_type 统计（仅 incorrect_actor）并区分 4 类原因，主口径=计入分母（FN）+ observable-only 诊断子集，sensitivity 移除 score 重算冒充 gamma sweep；(3) Sun Def 6 论文存在性语义（min<theta 等价 exists；C=process actor+bs_obj 近似披露；theta 证据修正 Figure 9：两模型 0.8/两模型 0.7，0.8 预注册）；sensitivity 真实重算（sun/winter_stage3_sensitivity.py 重跑 scorer，fixture 证明 gamma 改变分母）；(4) 运行收口：stage3_run_common.finalise_run（export_index.json + manifest finalised + 缺 artifact fail closed）+ evidence capsule（outputs/evidence/ 版本化可提交）；(5) S3.6 双 arm（BM25 归一化 Okapi / TF-IDF/SVD numpy 自实现）共享 BaselineScorer + config 预注册阈值；(6) 5 方法同口径 DEV_ONLY 比较（compare_stage3_methods_dev.json，不宣称优劣）；全量 1601 passed/24 skipped；未读 .env/未调 LLM/未改 Gold/BPMN/correction | 5 run manifest + evidence capsule + audit --with-tests + record_change 事件 |
| 3.6.5 | 2026-08-08 | **S3.4 可移植重放收口 + S3.5 Sun Stage 3 development 闭环（§9.5 S3.4/S3.5）**：(1) 公共 Stage 3 contract configs/schemas/stage3_prediction.schema.json + 公共 evaluator scripts/evaluate_stage3_common.py（per-process AP/MAP、binary P/R/F1、三类 violation 逐类+macro/micro、exact type acc、unobservable、denominator、threshold sweep 纯重算、error analysis）；(2) Winter reachability 双模式（corrected_reachability 主版本 / prototype_literal 敏感性）——clean replay s34_..._v2_clean + s34_..._prototype_literal，manifest 1.1.0（implementation hashes/export index/external prerequisites/bpmn 聚合 hash 替代 null），两模式 out_of_order 分数无差异（bug 分支未被数据触发，已记录），v1 原 run 未覆盖；(3) Sun Stage 3 方法级独立重建（Def 4-7 + §5.3 阈值）：sun_model（复用 canonical Process Record；pool 名可观察、lane 名空）、sun_rule_extraction（Gold-blind development adapter）、sun_scorer（matching=max(action,actor/object) 比例、missing=Def5、actor=Def6 含 unobservable、order=Def7 可达性）；config tau/gamma/theta=0.8 预注册 + 固定 sweep；run s35_sun_stage3_development_v1（公共 schema + 公共 evaluator + threshold_sensitivity + comparison_with_winter_dev + error_analysis + manifest 绑定干净 commit）；DEV_ONLY：Winter MAP 0.6429/binary F1 0.6111/violation macro 0.373；Sun MAP 0.8175/binary F1 0.0（tau 下无正预测，如实报告）/violation macro 0.333（missing 全 positive 假象、actor 全 unobservable、order denominator 0）；全量 1586 passed/24 skipped；未读 .env/未调 LLM/未改 Gold/BPMN/correction | 三个 run manifest + audit --with-tests + record_change 事件 |
| 3.6.4 | 2026-08-08 | **S3.4 Winter Stage 3 wrapper development 闭环（§9.5 S3.4 → development wrapper verified）**：Winter et al. (2020) 原型方法转写（只读研究 
eferences/winter_2020_model_check/model_check/lib，代码独立重写不 import）——BPMN 义务任务解析（task/start/end/intermediate events + sequence-flow 可达性）、条款 constraint/obligation/flow 解析（signalwords/sequencemarkers/stopwords，spaCy 依存切分）、Pair 语义（max-similarity mapping、fitness、cost_obligation/cost_resource/cost_so、加权 cost，gamma 0.4/delta 0.8/权重 1/3）；阈值与输入绑定入 versioned config configs/winter_stage3_development_v1.json；唯一入口 scripts/run_winter_stage3_development.py + 评价器 scripts/evaluate_winter_stage3_development.py；58 条冻结候选全量运行（25 matching + 33 violation），产物 outputs/development/s34_winter_stage3_development_v1/（config_snapshot/predictions/evaluation/error_analysis/manifest，DEV_ONLY：matching P 0.44/R 1.0/F1 0.61、mean AP 0.64；violation macro F1 0.37、exact type acc 0.33）；gold-blind（runner 只读 blank pack）、确定性（双跑 byte-identical）、无 LLM/网络；原型差异披露：is_reachable_from 恒真 bug 已修正（否则 out_of_order 恒 0）、participant 为空致 resource cost vacuous、en_core_web_sm 无词向量（与原型同款模型）；新增 12 项聚焦测试；修正 MASTER_PIPELINE P1 里程碑 0/150 残留为 150/150 adjudicated；全量 1566 passed/24 skipped。formal completion blocked on S1.7 and S2.13 | 运行 manifest + audit --with-tests + record_change 事件 |
| 3.6.3 | 2026-08-08 | **S3.2/S3.3 人工裁决完成（§9.5 S3.2/S3.3 → annotation frozen）**：用户逐批裁决全部 58 条候选（25 matching=11 相关/14 不相关；33 violation=missing_action/incorrect_actor/out_of_order 各 11），裁决写入 data/development/human_review/stage3_gold_annotation_human_correction_v1.json（decision 字段=用户裁决、candidate 字段=预填草稿，二者分离记录）；验证脚本新增 --validate-correction 冻结校验（身份/58 条全 adjudicated/decision 合法，fail closed）并生成冻结 manifest s32_s33_gold_annotation_freeze_v1.manifest.json；review 工具新增 --import-decisions 批量导入与 --print-batch 出题模式；.gitignore 忽略 review 备份目录；新增 3 项冻结校验测试；全量 1554 passed/24 skipped。formal Gold 发布仍待 stage3.status 合同门禁（§8.9 链） | 用户裁决导入 + 冻结校验 + manifest + audit --with-tests + record_change 事件 |
| 3.6.2 | 2026-08-08 | **S3.2/S3.3 标注包基础 + 裁决工具（§9.5 S3.2/S3.3 → ready for human review）**：新增 Stage 3 Gold 标注体系——schema configs/schemas/stage3_gold_annotation.schema.json（matching relevance 项 + violation type/evidence 项 + review_state 纪律，禁止推断决策）、构建脚本 scripts/build_stage3_gold_annotation.py（从 S3.1 Process Records + Winter regulations 生成候选：25 matching 候选=相关对+负例、33 violation 候选=每相关规则对三类注入点，并嵌入条款原文 rule_text）、验证脚本 scripts/verify_stage3_gold_annotation.py（身份/冻结流程对齐/候选完整性/rule_text/确定性重建/禁止推断决策，fail closed）+ manifest s32_s33_gold_annotation_blank_v1.manifest.json；交互式裁决工具 scripts/review_stage3_gold_annotation.py（每条显示流程活动+条款原文+预填判定与证据，输入 y/n（matching）或 missing_action/incorrect_actor/out_of_order/none（violation），支持跳过/撤销/断点续审，原子保存+独立备份目录）；空白模板 data/development/human_review/stage3_gold_annotation_blank_v1.json 全 unreviewed；新增 14 项测试；全量 1551 passed/24 skipped。正式 matching/violation Gold 需用户裁决后冻结（S3.2/S3.3 DoD 未完全达成，blocked on adjudication） | 构建+验证+review 工具 + manifest + audit --with-tests + record_change 事件 |
| 3.6.1 | 2026-08-08 | **S1/S3.1 资产恢复与 binding 修复（§9.5 S3.1 → verified）**：从 56d2b03 checkpoint 恢复全部 S1/S3 资产（47+5 文件：configs/schemas/data/docs/outputs/scripts/src/tests/fixtures + 5 个 s1 gate 模块 + process_record.schema.json）；7 个 GDPR BPMN 以批准 LF 字节落地（工作区原 CRLF 变体内容一致、仅行尾，已备份至 `.tmp/untracked_gdpr7_backup_2026_08_08/`）；`data/input/stage1_stage3/gdpr7/*.bpmn` 加入 `.gitattributes` `text eol=lf`（G0-EOL 同纪律）；修复 56d2b03 快照先存的跨任务 binding 过期（s13/s15/s16 合同 upstream manifest hash、5 个 gate 期望、合同 stage1 块），s13/s15/s16/s15_s31 manifest 按当前合同重新生成并全链更新 hash；`verify_stage1_stage3_gdpr7.py` 通过（7 byte-exact、45 activities、135 blank fields）；S1 gate 集成进 status.py/audit.py（`stage1_*_verified`、`stage1_formal_bpmn_membership_locked` pass）；37 项 stage1 测试全绿，全量 1537 passed/24 skipped | 56d2b03 checkpoint 恢复 + verify 脚本重生成 + audit --with-tests + record_change 事件 |
| 3.6.0 | 2026-08-08 | **最终执行总控收敛（§8.9）**：既有任务 ID 为唯一派工主键；G0 改为核账并仅补双口径合同、shared comparison capsule、Barrientos adapter 注册；新增 `S2-BARR-1..5` 专项工作包并规定 L1/L2/L3 与 C1-C4 正交；H1 停止优化且 formal 对照仅可在 capsule 核验后 zero-API 重评或重新授权运行；Stage 3 明确 development/formal 双态、S3.1-S3.3 受控并行和 S3.7 formal 前置；formal Gold 交叉门禁、E00/E10/E01/E11 与论文回填边界固定。同步修正实时门禁与派工入口的过期 0/150/H1 文本 | 2026-08-08 机器完整性检查：freeze_ready=true、formal Gold/final=false；独立审查 findings 的逐项裁决 |
| 3.5.0 | 2026-08-08 | **导师汇报后方向锁定（§8.8 新增四项事实）**：(1) Rules+LLM-Repair（旧代号 H1）**降级为对照方法、不再深究**——全量 150 运行（commit 74614e3）主口径 F1 0.7621 vs Rules-Only 0.7986（净负）、LLM 修复过度抽取 actor（P 0.7077→0.2754），机制正常但 trigger+repair 配方加 FP 不加召回；S2.8 正式 trigger 预注册取消；§8.3 方法表/P4 里程碑/PW3 同步；(2) Rules-Only 与 Direct-LLM **局限性列表+实例**写入 §8.8.2（B0：字段归属错误 C1/C2、词典缺口 13 名词+"It"、Sun-marker 定义口径差异、Tsurgeon 诚实非实现；D1：constraint R 弱 0.417、actor 泛化误抽 P 0.594、高精度保守型、API/预算依赖）；(3) **命名直观化**：B0→Rules-Only（纯规则法）、H1→Rules+LLM-Repair（规则+LLM 修复）、D1→Direct-LLM（直接 LLM），映射表 §8.8.3，机器 ID 不变、methods.json 增 paper_label；(4) **与 Barrientos et al. (2026) 严格对比 + 贡献细模块化**（§8.8.4）：Direct-LLM 拆 8 模块（schema 契约/prompt 工程/few-shot/transport/校验链/预算/双口径评价/可复现资产）、Rules-Only 拆 7 模块；消融矩阵 AB-1..AB-10（列表跑数据：我的模块 vs 换 Barrientos 模块 vs 去掉模块，明确谁好及原因）；论文方法章节目标 4–5 页、禁止只写"调用了 LLM" | 2026-08-08 导师汇报确认；H1 全量运行 commit 74614e3；B0/D1 收口 brief outputs/reports/b0_d1_experiment_closure_brief.md；Barrientos 审计 docs/research/BARRIENTOS_BORROWING_AUDIT_2026-07-12.md；record_change 事件 + audit --with-tests |
| 3.4.34 | 2026-08-06 | formal Gold 发布路径推进 2/4 前置（用户授权按 pipeline）：`experiment_contract.json` route.status→**locked**（最终版方法对齐按方法级独立复现口径完成：B0-R2 verified/crosswalk 11 元素、method_conformance_status 已翻转、official supplement 57 文件 hash 匹配；missing_for_lock 为披露项）与 stage2_dataset.status→**locked_for_human_review**（modality verified + phrase Gold freeze 150/150）；sun_modality_gate.py 中间状态期望同步；5 个状态依赖测试更新；BLOCKERS 7→5（`final_version_route_alignment_pending`/`stage2_dataset_route_relock_pending` 消除，新增 pass `reconstruction_route_locked`/`stage2_dataset_route_locked`）；1486 passed / 24 skipped。剩余前置：stage3.status=locked（需先完成最终子集配置+violation Gold 锁定，S2.11/S3 任务）+ publication gate 白名单精确匹配 | record_change 事件 + audit --with-tests |
| 3.4.60 | 2026-08-13 | **S1.7 正式冻结应用（用户明确授权；基线 9655774b；纠错后 target-aware claim 语义下冻结）**：用户授权（中文原文+英文参考句）记录于 outputs/reports/s1_7_freezer_authorization_v1.manifest.json（sha 7712176c…）——知悉 P2 在 Gold 形成后开发、3 条目标标签进入开发测试、至少一条三元组与 Gold 一致；确认 S1.6 为固定 GDPR-7 描述性组件评价（非 held-out 泛化）；**冻结范围**：评价后未调优的 P2 锁定方法（config/impl/runtime）、现有 P0/P1/P2 预测（锁定+权威副本）、原始指标（数值主体 canonical 19002346…）、Stage 1 Process Gold、已验证正式评价 capsule；**排除**：不改 P2、不选择性重算、零 LLM/API、不改 Stage 2/3 Gold 与 contract、不自动授权 Stage 3 Oracle；24 个资产 hash 绑定（7 BPMN/membership/P2/predictions/metrics/Gold/audit/correction/S1.7v2 包等）；独立 verifier scripts/verify_s1_7_freezer_authorization.py（VERIFIED：授权句逐字、字节锁、safety、exclusions、S1.7v2 包保持 dry_run_not_applied）；audit 新增 pass stage1_s7_freeze_authorized（实际运行授权 verifier；不自动推进 S1.6/S3.7）；S1.7 → **frozen**（正式冻结完成）；S3.7 仍未启动（Oracle 仅经 Stage 3 独立门禁）；本轮零新增 LLM/API，P2/predictions/metrics/Gold/contract/methods/Stage 3 gate 均未修改 | 授权 manifest + verifier + record_change 事件 + audit --with-tests |
| 3.4.59 | 2026-08-13 | **S1 target-overlap claim 纠正 + 正式资产路径纠正 + S1.7 readiness v2（纠错任务；基线 e3583c9；P2 方法/predictions/指标逐位未变）**：**问题一（fixture 与目标重合）**：target-overlap 审计 outputs/reports/s1_p2_target_overlap_audit_v1.{json,md,manifest}（sha 948d268a…；历史测试文件绑定 c704bbc blob）——历史 exact/ws/casefold/punct 重合各 3 条（Communication with data subject/Rectify data/Retrieve data）、当前 fixture 重合 0；Retrieve data 测试断言三元组与人工 Gold 相同、Communication 的 action/object 断言一致；动词表 **200/200**（旧报告 199 纠正，内容未改）；Gold action 首词覆盖 10/13；无 process/activity ID 或逐标签硬编码；结论：开发 target-aware、strict test-blind=false、runtime Gold 隔离与 no post-evaluation tuning 仍成立、指标可保留为固定 GDPR-7 描述性组件评价；独立 verifier（从 git blob 重算历史重合 + 当前零重合，篡改即失败）；**测试纠正**：fixture 3 条重合标签替换为 Collect records/Correspondence with the customer/Update records（不重合、覆盖相同语言边界），新增 zero-overlap 门禁（exact/ws/casefold/punct 全 0、ID 非 GDPR-7、Gold 仅审计用途）；**问题二（正式路径）**：正式权威入口 data/predictions/stage1_formal_v1/（predictions 副本 sha 79a9b2c1… 逐位一致）+ data/results/stage1_formal_v1/（数值主体 sha a072db39…/canonical 19002346…，无 claim metadata）+ outputs/reports/stage1_formal_evaluation_v2.{json,md,manifest,export_index,capsule_manifest}（sha 954122d4…；target-aware claim、绑定 7 BPMN/membership/P2/Gold/evaluator/predictions/audit/correction）；旧 development 产物保留为 historical provenance（数值有效、claim 由 v2 纠正）；**claim correction** outputs/reports/s1_stage1_claim_correction_v2.json（11 个结构化状态：strict_test_blind=false、target_labels_seen_during_development=true、held_out_generalization_claim_allowed=false、evaluation_role=formal_descriptive_component_evaluation_on_fixed_GDPR7 等；准确表述 post-Gold, target-aware Sun/Leopold-style method-level reconstruction with Gold-isolated inference, pre-evaluation code/config lock, and no post-evaluation tuning）；**S1.7 v2**：v1 标记 superseded（superseded_due_to_target_fixture_overlap_and_formal_path_semantics），v2 包 s1_7_freezer_readiness_dry_run_v2.{json,md}（sha be5d4b80…；绑定 audit/correction/200 词/正式路径/P2-predictions-metrics-Gold 未变；7 个独立 verifier 实际运行全过；新授权句含 target-aware 承认；**freeze 未应用**）；audit 新增 pass stage1_claim_correction_verified（实际运行 3 个新 verifier）与检测（target-aware 缺失/strict_test_blind=true/formal 路径指向 development/199 词/audit 缺失/P2-predictions 变化）；16 项纠错 tamper 测试；S1.3/S1.5/S1.6 保持 verified（claim 语义纠正）、S1.7 保持 ready_for_user_freeze_authorization、S3.7 未启动；本轮零新增 LLM/API，P2 config/impl/runtime、predictions、指标、Stage 1/2/3 Gold、contract、methods、Stage 3 gate 均未修改 | 纠错资产 + audit/claim/v2/S1.7v2 + record_change 事件 + audit --with-tests |
| 3.4.58 | 2026-08-13 | **S1.7 冻结 readiness / 授权 dry-run 包（用户授权；Checkpoint B 9372a54 先 push 并经远端核验）**：自包含包 outputs/reports/s1_7_freezer_readiness_dry_run_v1.{json,md}（sha 7cc488b0…）——**状态 `dry_run_not_applied`、目标 `S1.7 ready_for_user_freeze_authorization`（未冻结、未应用）**；24 个资产 hash 全部从磁盘重算（7 BPMN source、membership、Process Record schema/records、correction、P2 config/impl/schema/crosswalk/lock、formal evaluator config/impl、predictions、Gold+manifest+授权、capsule evaluation/manifest）；**5 个独立 verifier 真实运行全过**（七批链/Gold 发布/P2 锁定/predictions 隔离/评价 capsule）；一致性声明（零 API、P2 锁定后未变、Gold 未用于调优、Stage 3 未启动）；回滚/fail-closed 语义；**Stage 3 边界**（S1.7 冻结仅解锁前置，正式 Oracle 须经 Stage 3 独立门禁，本包不自动授权）；精确可复制授权句（只冻结已验证 Stage 1 资产、不改 P2/不重算选择性结果/不新增 LLM-API/不改 Stage 2-3 Gold 与 contract/Oracle 仍按独立门禁）；独立 verifier scripts/verify_s1_7_freezer_dry_run.py（10 项 PASS）+ 6 项 dry-run tamper 测试（status/hash/授权句/P2 配置/verifier 声明 fail-closed）；S1.7 → ready_for_user_freeze_authorization（**正式 freeze 未应用，待用户授权**）；S3.7 未启动；本轮零新增 LLM/API，Gold/contract/Stage 3 gate 未修改 | S1.7 readiness 包 + verifier + record_change 事件 + audit --with-tests |
| 3.4.57 | 2026-08-13 | **S1.6 一次性正式评价完成 + S1.3 P2 verified（用户授权；Checkpoint A c704bbc 先 push 并经远端核验）**：**正式 predictions**（outputs/development/stage1_predictions/formal_predictions_v1.json，sha 79a9b2c1…，7×3 attempts/45 activities；runner scripts/run_stage1_p2_inference.py：P0/P1/P2、P2 双跑 byte-identical、no-overwrite、inputs_read 白名单、gold_read=false 证明；独立 prediction verifier scripts/verify_stage1_predictions.py 13 项 PASS：重渲染一致性=无 Gold 泄漏证明）；**正式 evaluator**（新资产 src/bpc_hybrid/stage1_evaluation_formal.py + configs/stage1_evaluator_s16_formal.json——独立于 experiment contract 锁定的 synthetic evaluator（contract 未修改）；metrics 与 synthetic 合同一致，methods P0/P1/P2，P2 label 验证走 P2 schema，完整重渲染由 prediction verifier 承担）；**一次性评价**（scripts/run_stage1_formal_evaluation.py → capsule outputs/development/stage1_formal_capsule_v1/：evaluation.json（sha e7267593…，scope=formal、one_shot=true、method deltas、per-process triple、limitations 全披露）+ predictions_copy + manifest + export_index；独立 capsule verifier scripts/verify_stage1_formal_evaluation.py 15 项 PASS：报告重跑==存储、输入绑定、P2 锁定未变、零 API、限制披露）；**正式结果（诚实，未调优）**：结构 micro F1=1.0（共享 parser 组件；结构 Gold 来自人工确认的 parser candidate，不包装为独立泛化证据）；语义 micro——P0 all 0（raw 无语义）、P1 P 0.7444/R 0.4963/F1 0.5956/acc 0.4241/triple 0.0、**P2 P 0.8548/R 0.7852/F1 0.8185/acc 0.6928/triple 0.4222**（P2 锁定后未改变；正负结果均保留）；披露：candidate-assisted human adjudication、7 processes/45 activities/135 fields、无显著性推断、不与 Sun 不同数据集绝对分数硬比较、post-Gold lock（非严格 blind preregistration）；**synthetic S1.6 gate 修复**：gate EXPECTATIONS 重绑当前资产 hash、contract evaluator 块改结构一致性检查（contract 文件未修改；历史 hash 绑定自 f628b6b 起与资产不符）、synthetic manifest 重建（语义不变）；7 项正式 capsule tamper 测试（值/副本/manifest hash/P2 配置/限制删除/Gold 篡改 fail-closed）；audit pass stage1_formal_evaluation_verified（实际运行 3 个独立 verifier）；S1.3 → verified、S1.6 → verified、S1.7 仍 blocked（freeze 待授权）；本轮零新增 LLM/API，Gold/contract/Stage 3 gate 未修改 | 正式评价 capsule + verifier + record_change 事件 + audit --with-tests |
| 3.4.56 | 2026-08-13 | **S1.3 P2 方法级独立重建锁定（Sun/Leopold-style；用户授权；Batch 7 661f20b 先 push 并经远端核验）**：**证据 crosswalk**（outputs/reports/s1_3_p2_crosswalk_v1.json + docs/research/S1_P2_CROSSWALK.md）：C1-C5 绑定 Sun 2024 §4.1/§4.2/Fig.3/引文[25]（Leopold 2013）+ 本地全文 hash（947140c3…/65f03a46…/ea624152…）；D1-D4 unavailable_or_underspecified（Leopold 论文不可得、Sun 因篇幅未展开）→ 最小确定性适配；禁止 exact reproduction/Sun original/P1 enhanced/novel/blind 表述，诚实标签 post-Gold paper-derived method reconstruction with a locked implementation and prospective one-shot evaluation；**P2 配置/注册表** configs/stage1_label_p2_v1.json（输入白名单+禁止输入、runtime 锁定 spaCy 3.8.13 + en_core_web_sm 3.8.0 dir sha256 f5c9433c…/26 files、语言规则全参数化、fail-closed、determinism、safety）；**P2 实现** src/bpc_hybrid/stage1_label_semantics_p2.py（Model Context Analysis：lane→pool（XML participant/laneSet 映射）+ Label Style Recognition（verb/noun/degenerate）+ Composition/Semantic Derivation（root 动词+xcomp 复合、obj 子树（det/adj/conj 并入、aux/punct/prep 排除、pobj 并入）、nsubjpass 被动、名词风格 prep.pobj、whether/if/that 从句不并入、命令式 compound+锁定通用英语动词表（199 词，非 GDPR-7 派生））；sidecar schema stage1_label_semantics_p2@1.0.0；**Gold 隔离**：实现/配置/runner 无 gold/correction/adjudication 路径绑定（AST 静态检查+声明检查）、输入白名单、runtime 缺失 fail-closed 不退化 P1；**21 项合成测试**（单/空/多 lane actor、动宾、复合 action、介词、从句、并列、被动、空标签、Unicode 空白、类型一致性、runtime 缺失、双跑 byte-identical、无硬编码、Gold 隔离、P2≠P1 证明）；**独立 verifier** scripts/verify_stage1_p2.py（14 项 PASS：config/impl/schema/runtime/verb 资源/证据 hash/隔离/双跑/禁止 claim）；锁定 manifest outputs/reports/s1_3_p2_locked_v1.manifest.json + 正式 runner scripts/run_stage1_p2_inference.py（P0/P1/P2、双跑、no-overwrite、gold_read=false 证明）；S1.3 → P2 implementation verified and locked；formal inference/evaluation pending（S1.6/S1.7 未推进）；本轮零新增 LLM/API，Gold/contract/Stage 3 gate 未修改 | P2 锁定资产 + crosswalk + verifier + record_change 事件 + audit --with-tests |
| 3.4.55 | 2026-08-13 | **S1.5 正式 Process Gold 冻结 + 发布（用户明确授权；Batch 7 56ae14d 先 push 并经远端核验）**：用户授权句精确记录于 outputs/reports/s1_5_process_gold_freeze_authorization_v1.manifest.json——只发布已记录裁决、不新增/推断/改写决定、保留 source/candidate/correction/七批 chain hashes、冻结后先独立验证再推进（P2 方法级独立重建（Sun/Leopold-style）→ S1.6 正式评价 → S1.7）；P2 边界：仅对无法获得的原始数据与论文未公开参数做预先锁定、完整披露的项目适配，禁止用正式 Gold 调参、禁止以 P0/P1 冒充 P2、禁止声称 exact reproduction；不含 LLM/API、Stage 3 Oracle、contract 修改或其他 Gold 变更；**发布产物**：data/gold/stage1/process_records/stage1_process_gold_v1.json（7 条记录机械复制自 correction，f33aa857…/256,960 B）+ data/gold/stage1/manifest.json（1885dad2…，含 artifact/blank/correction/membership/chain hashes 与 P2 边界）+ 独立 verifier scripts/verify_stage1_process_gold.py（gold==correction 逐字段、gold_process_record canonical==锁定 candidate、授权句精确、七批链仍 VERIFIED、data/gold/stage1 仅含发布内容，全部 fail-closed；21 项 PASS）；AUTH manifest 演进 gold_freeze_authorized=false→true、status → process_gold_freeze_authorized_and_published；链 verifier/audit 授权状态一致性演进（audit pass stage1_process_gold_published；S1.6/S1.7/S3.7 不自动推进）；dry-run 包保留为历史只读快照（verifier 改为包自洽验证）；11 项 process-gold 发布 tamper 测试（值/删/增/结构/artifact hash/授权句/授权标志/删文件/多余文件/correction 链断裂 fail-closed）；S1.5 → verified（frozen+published），S1.6/S1.7/S3.7 未启动；本轮零新增 LLM/API，contract/Stage 3 gate/publication 状态（EStG 侧）未修改 | Gold 发布资产 + 授权/发布 manifest + 独立 verifier + record_change 事件 + audit --with-tests |
| 3.4.54 | 2026-08-13 | **S1.5 第 7/7 批人工裁决导入（gdpr_7_right_to_be_forgotten，用户 2026-08-13 明确确认；Batch 6 847ac11 先成功 push 并经远端逐位核验）**：7 项决定（1 structure accepted_candidate + 6 字段全 present：actor 2/2=Data Controller）；**F1 介词边界**：raw_label 保持 `Communication with data subject`，`with` 不进入 business_object（=data subject，严禁 `with data subject`）；F2 标准切分 Retrieve/data；机械转录（DeepSeek 无推断）；gold_process_record 精确复制 gdpr_7 锁定 candidate（canonical 250bdecd… 逐位匹配，XML 类型 subProcess×2 交叉核验）；链式资产 stage1_adjudications/gdpr_7_right_to_be_forgotten/{decision 39935521…,import_record fb7e069c…,manifest}（before=批次6 after 947487b1…、after=6a9c055a…、prev=gdpr_6）；review tool import（备份 20260813T093515Z）→ validate valid；summary：**7/7 adjudicated、135/135 resolved、freeze_ready=true（142/142，0 unresolved）**；**七批链式 verifier（blank→b1..b7→磁盘逐位重放 6a9c055a…）VERIFIED**；Batch 1–6 记录逐字段不变；19 项 batch7 focused tests（F1/F2 精确值、action/object/actor/activity-id/raw_label/XML 类型/source/candidate/membership/process_id/前节点/sequence-flow/授权句篡改 fail-closed、删批/重复前驱/中链断裂/换批/最终不一致 fail-closed）；**冻结 readiness 演进**：AUTH manifest status → `human_adjudication_complete_freeze_authorization_pending`（gold_freeze_authorized 保持 false）、verifier/audit 新增 complete_freeze_pending 状态（audit pass `stage1_human_adjudication_complete_freeze_pending`，142/142 仅 freeze-READY 事实非冻结授权）、freeze_ready 篡改语义翻转（7/7 后 False 即篡改）；**freeze authorization dry-run 包** outputs/reports/s1_5_process_gold_freeze_authorization_dry_run_v1.{json,md} + 独立 verifier scripts/verify_s1_5_freeze_dry_run.py（链/统计/hash/声明/授权句/未发布 Gold 全 VERIFIED）；S1.5 → adjudication complete / freeze pending，S1.6/S1.7/S3.7 未启动；本轮零新增 LLM/API，Gold/contract/Stage 3 gate/publication 未修改 | gdpr_7 裁决资产 + 七批链 verifier + dry-run 包 + record_change 事件 + audit --with-tests |
| 3.4.53 | 2026-08-13 | **S1.5 第 6/7 批人工裁决导入（gdpr_6_right_to_rectify，用户 2026-08-13 明确确认；Batch 5 d896516 先成功 push 并经远端核验）**：7 项决定（1 structure accepted_candidate + 6 字段全 present：actor 2/2=Data Controller、E1 Rectify/data、E2 Communicate/the rectification）；**raw label 尾随换行边界**：E2 raw_label 保留尾随 \n（源 XML `&#10;`、锁定 candidate name 同），action/business_object 语义值不含换行或尾随空白（明确裁决非证据清理）、business_object 保留冠词 the；机械转录（DeepSeek 无推断）；gold_process_record 精确复制 gdpr_6 锁定 candidate（canonical 5f2ee37a… 逐位匹配）；链式资产 stage1_adjudications/gdpr_6_right_to_rectify/{decision,import_record,manifest}（before=批次5 after 1afabb87…、after=947487b1…、import sha 7f98dd61…、prev=gdpr_5）；review tool import（备份 20260813T075834Z）→ validate valid、freeze false；summary：6/7 adjudicated、129/135 resolved（剩余 6 字段+1 结构=7 项人工决定）；六批链式 verifier（blank→b1..b6→磁盘逐位重放）VERIFIED；9 项 batch6 focused tests（E2 换行保留/删除换行 fail-closed、action/object 带换行或 尾随空白 fail-closed、去冠词 fail-closed、泛化篡改、gdpr_7 未预填、summary/freeze）；S1.5 保持 in_progress（6/7、129/135），S1.6/S1.7/S3.7 未启动；本轮零新增 LLM/API，Gold/contract/Stage 3 gate/publication 未修改 | gdpr_6 裁决资产 + 链式 verifier + record_change 事件 + audit --with-tests |
| 3.4.52 | 2026-08-12 | **S1.5 第 5/7 批人工裁决导入（gdpr_5_right_to_withdraw，用户 2026-08-12 明确确认）**：16 项决定（1 structure accepted_candidate + 15 字段全 present：actor 5/5=Data Controller）；**复合 action 锁定**：D1 action=Stop running、D2 action=Stop using（严格禁止退回单首词 Stop）；**if/that 从句边界**：D3 business_object=withdrawn data（不并入 if 从句）、D5 business_object=the user（that 从句为通知内容不并入）；D4 保留 the withdraw（不改 withdrawal、不删冠词）；机械转录（DeepSeek 无推断）；gold_process_record 精确复制 gdpr_5 锁定 candidate（canonical 6053ce18… 逐位匹配）；链式资产 stage1_adjudications/gdpr_5_right_to_withdraw/{decision,import_record,manifest}（before=批次4 after 6befc63c…、after=1afabb87…、import sha 310de1ed…、prev=gdpr_4）；review tool import（备份 20260812T135821Z）→ validate valid、freeze false；summary：5/7 adjudicated、123/135 resolved（剩余 12 字段+2 结构=14 项人工决定）；五批链式 verifier（blank→b1..b5→磁盘逐位重放）VERIFIED；12 项 batch5 focused tests（复合 action 拆分/object 退回 P1 余串 fail-closed、if/that 从句并入 object fail-closed、withdrawal/去冠词 fail-closed、泛化篡改、gdpr_6/7 未预填、summary/freeze）；S1.5 保持 in_progress（5/7、123/135），S1.6/S1.7/S3.7 未启动；本轮零新增 LLM/API，Gold/contract/Stage 3 gate/publication 未修改 | gdpr_5 裁决资产 + 链式 verifier + record_change 事件 + audit --with-tests |
| 3.4.51 | 2026-08-12 | **S1.5 第 4/7 批人工裁决导入（gdpr_4_right_of_portability，用户 2026-08-12 明确确认）**：10 项决定（1 structure accepted_candidate + 9 字段全 present：actor 3/3=Data Controller、action Retrieve/Retrieve/Communicate、business_object available data of the data subject（不窄化）/elaborations/data and elaborations（不拆并列））；机械转录（DeepSeek 无推断）；gold_process_record 精确复制 gdpr_4 自己的锁定 candidate（canonical a1d77e89… 逐位匹配；禁止复制 gdpr_3 candidate）；**gdpr_3/gdpr_4 独立身份证明**：共享 raw XML process id （sid-C2A304F9-…）由 membership identity adapter 消歧——数据集级 process_id/source input_id/pool process_ref 全绑定各自身份（gdpr_4 source 68601777…/31497 B、gdpr_3 source d6e48d09…），候选、决策、导入、manifest 资产各自独立（gdpr_3 资产逐字节 不变），查找键含 process 边界（无跨 process activity 匹配）；链式资产 stage1_adjudications/gdpr_4_right_of_portability/{decision,import_record,manifest}（before=批次3 after a4f65b1a…、after=6befc63c…、import sha 3f293930…、prev=gdpr_3）；review tool import（备份 20260812T115047Z）→ validate valid、freeze false；summary：4/7 adjudicated、108/135 resolved（剩余 27 字段+3 结构=30 项人工决定）；四批链式 verifier（blank→b1→b2→b3→b4→磁盘逐位重放）VERIFIED；11 项 batch4 focused tests（4 批重放、gdpr_4 身份绑定、gdpr_3/4 共享 raw id 不冲突、gdpr_3 candidate 复制给 gdpr_4 fail-closed、source 错绑 fail-closed、跨 process 匹配 fail-closed、gdpr_3 资产 不变、C1 窄化/C3 拆并列 fail-closed、标签/activity/candidate/hash/链断裂/summary/未裁决/freeze）；verifier 增加 corr_rec 缺失防御（跨 process 改名 tamper 不再抛异常）；S1.5 保持 in_progress（4/7、108/135），S1.6/S1.7/S3.7 未启动；本轮零新增 LLM/API，Gold/contract/Stage 3 gate/publication 未修改 | gdpr_4 裁决资产 + 隔离证明 + record_change 事件 + audit --with-tests |
| 3.4.50 | 2026-08-12 | **S1.5 第 3/7 批人工裁决导入（gdpr_3_right_to_access，用户 2026-08-12 明确确认）**：10 项决定（1 structure accepted_candidate + 9 字段全 present：actor 3/3=Data Controller、action Retrieve/Retrieve/Communicate、business_object available data of the data subject（不窄化、保留后置限定语）/elaborations/data and elaborations（不拆并列））；机械转录（DeepSeek 无推断）：gold_process_record 精确复制锁定 candidate（canonical sha256 4f2daa7b… 逐位匹配）；presentation-only factual correction：只读裁决包展示表曾把 C1/C2 标为 task，真实 XML 类型为 subProcess（C3 为 task）——锁定 candidate 始终正确，展示错误未写回 BPMN/candidate，已在本批证据中记录；链式资产 stage1_adjudications/gdpr_3_right_to_access/{decision,import_record,manifest}（before=批次2 after da8f1b05…、after=a4f65b1a…、import sha 455805a5…、prev=gdpr_2）；review tool import（备份 20260812T100637Z）→ validate valid、freeze false；summary：3/7 adjudicated、99/135 resolved（剩余 36 字段+4 结构=40 项人工决定）；三批链式 verifier（blank→b1→b2→b3→磁盘逐位重放）VERIFIED；9 项 batch3 focused tests（3 activities/9 fields 派生、类型核验、C1 窄化/C3 拆并列 fail-closed、actor/action 篡改、activity ID 缺失/增加、candidate/hash/import/链断裂、summary/未裁决/freeze）；S1.5 保持 in_progress（3/7、99/135），S1.6/S1.7/S3.7 未启动；本轮零新增 LLM/API，Gold/contract/Stage 3 gate/publication 未修改 | gdpr_3 裁决资产 + 链式 verifier + record_change 事件 + audit --with-tests |
| 3.4.49 | 2026-08-12 | **S1.5 第 2/7 批人工裁决导入（gdpr_2_consent_to_use_the_data，用户 2026-08-12 明确确认）**：73 项决定（1 structure accepted_candidate + 72 字段全 present）；机械转录（DeepSeek 无推断）：gold_process_record 精确复制锁定 candidate （canonical sha256 fb6ec966… 逐位匹配）；裁决边界（保留大小写/拼写 purposses/rectify of、business_object 不含引号与 if 谓词、actor 24/24=Data Controller）；链式证据资产 stage1_adjudications/gdpr_2_consent_to_use_the_data/{decision,import_record,manifest}（manifest：before=批次1 after 2c10c78f…、after=da8f1b05…、import sha 55a83587…、prev_process=gdpr_1_data_breach）；review tool import（原子保存+备份 20260812T092843Z）→ validate valid、freeze false；summary：2/7 adjudicated、90/135 resolved（剩余 45 字段+5 结构=50 项人工决定）；链式 verifier（blank→gdpr_1→gdpr_2→磁盘 correction 逐位重放）VERIFIED；14 项 batch2 focused tests（72 字段派生、if 偷换/引号偷加/purposses 纠正均 fail-closed、链断裂/import hash/候选篡改等）；S1.5 保持 in_progress（2/7、90/135），S1.6/S1.7/S3.7 未启动；本轮零新增 LLM/API，Gold/contract/Stage 3 gate/publication 未修改 | gdpr_2 裁决资产 + 链式 verifier + record_change 事件 + audit --with-tests |
| 3.4.48 | 2026-08-11 | **S1.5 第 1/7 批人工裁决导入（gdpr_1_data_breach，用户明确确认）**：用户裁决 19 项（1 structure accepted_candidate + 18 字段全 present）；机械导入（DeepSeek 仅转录，无推断）：gold_process_record 精确复制自锁定 stage1_gdpr7_process_records_v1.json（canonical sha256 0f842984… 逐位匹配）；可重放证据资产 outputs/development/human_review/stage1_adjudications/gdpr_1_data_breach/（decision_v1.json + manifest：before correction sha 与 blank 一致、after 2c10c78f…、candidate/bpmn/membership hashes、llm_api_calls=0、gold_freeze_authorized=false、DeepSeek 机械转换声明）；通用增量裁决 verifier scripts/verify_stage1_human_adjudication.py（10 项 fail-closed 检查，后续 6 批复用：决策资产/manifest hash、process id 唯一、correction==decision、gold==锁定 candidate canonical、candidate hash、18 字段逐项、其他 record 不变、raw_label/lane_labels 不变、summary 一致、freeze false；任一篡改非零退出）；review tool import 原子保存+备份+summary 重算；correction summary：records 7、adjudicated_records 1、label_fields 135、resolved_label_fields 18、freeze_ready false；audit 语义演进：correction 与 blank 一致时 stage1_review_surface_input_ready → 存在已验证裁决时 stage1_human_adjudication_in_progress（要求每一处 correction-vs-blank 差异有 versioned 决策资产支撑 + verifier 通过；无证据修改立即 error stage1_human_adjudication_invalid）；10 项篡改测试（字段值/额外字段/candidate 内容/candidate hash/其他 record/summary/manifest 缺失/freeze 提前/决策不一致）；S1.5 → in_progress；S1.6 正式评价、S1.7 freeze、S3.7 Oracle 未启动；本轮零新增 LLM/API，Gold/contract/Stage 3 gate/publication 未修改 | 裁决资产 + 增量 verifier + 审计演进 + record_change 事件 + audit --with-tests |
| 3.4.47 | 2026-08-11 | **S1.5 人工 Process Gold 核对界面授权开放（input-ready only）**：用户明确授权开放 S1.5 review surface——冻结 GDPR-7 全七 BPMN membership（7 BPMN/45 activities/135 label fields，membership payload SHA-256=e88caf81… 已核对一致）、允许使用 stage1_review_tool.py、全空白/unreviewed 的 stage1_gdpr7_human_correction_v1.json 与双语 HUMAN_PROCESS_GOLD_GUIDE.md 供用户本人裁决；工具不得推断/预填/自动接受任何决定；本授权只设 S1.5 为 input-ready，不授权 Gold freeze（freeze 仍需用户 7/7 structure decisions + 135/135 字段裁决）；授权记录 s1_5_review_surface_authorization_v1.manifest.json（8 项前置检查全过：membership payload 匹配、correction==blank、7/7 unreviewed、无 Gold 预填、freeze_ready=False、tool/guide/schema 存在）；audit 新增 pass stage1_review_surface_input_ready（correction 被改动或授权缺失时 fail closed → error stage1_review_surface_not_ready）；MASTER_PIPELINE S1.5 行 blocked → input_ready（freeze 仍 blocked）；本轮零新增 LLM/API，Gold/contract/Stage 3 gate/publication 未修改，未创建或推断任何人工 Process Gold | 授权 manifest + audit pass + record_change 事件 + audit --with-tests |
| 3.4.46 | 2026-08-11 | **S1.5 人工 Process Gold 核对准备 + S1.6/S1.7/S3.7 后续入口（Checkpoint 3）**：(1) 非破坏性 review 工具 scripts/stage1_review_tool.py（list/show/export/import/backup/validate/undo：import 仅应用用户显式 decisions 并原子保存+备份、非法状态 fail-closed、绝不推断 decision；操作对象仅为用户可编辑 correction 文件，immutable blank 模板不动）；(2) 双语 HUMAN_PROCESS_GOLD_GUIDE.md（中文+英文：decision 含义表、空 lane/隐含 actor/gateway/循环/并行/不可达路径处理、candidate 编辑方式、freeze 条件；仅用户可设 reviewed/adjudicated）；(3) S1.5 input-readiness dry-run（s1_5_input_readiness_dry_run：membership 7 BPMN/45 activities/135 label fields/payload e88caf81…；review surface 7 记录全 unreviewed、142 未决（135 字段+7 结构）、correction 与 blank 逐字节一致、无 Gold 预填证明；expected workload；before/after（授权仅开 review surface，freeze 仍需 7/7+135/135）；含可复制授权句）；S1.5 正式门禁未应用；(4) S1.6 evaluator synthetic verification 确认（s1_6_evaluator_synthetic_verification_v1：仅 synthetic、formal run blocked until human Process Gold）；(5) S1.7 freeze checklist（s1_7_freeze_checklist_v1：input/output/method/metrics/hash/manifest 清单，output=human Process Gold 尚不存在，blocked on S1.5）；(6) S3.7 Oracle readiness v2（s3_7_oracle_readiness_v2：真实 Gold Rule Records 不存在、真实 Gold Process Records 不存在、Stage 2 方法预测非 Rule Records、parser candidate 非 Process Records、依赖 S1.7/S2.13/S3.4-S3.6、Oracle 未启动）；5 项新聚焦测试（tool 行为 + readiness 结构）；S1.5-S1.7 保持 blocked；本轮零新增 LLM/API，Gold/contract/Stage 3 gate/publication 未修改、未创建/推断人工 Process Gold | review tool + guide + readiness 包 + record_change 事件 + audit --with-tests |
| 3.4.45 | 2026-08-11 | **Stage 1 S1.1-S1.4 现状核账与确定性验证（Checkpoint 2）**：(1) S1.1-S1.4 逐任务矩阵（s1_1_s1_4_matrix_v1.json/.md）：每项列出代码/schema/config/fixtures/tests/manifest/已满足 DoD/真实缺口/状态——S1.1 verified（Process Record schema + fixtures + validator）、S1.2 verified（确定性解析 + 7/7 GDPR 双跑 byte-identical）、S1.3 partial（P0/P1 机械标签语义完成，P2 未实现，actor/action/object 仅机器 candidate 非 Gold）、S1.4 verified（control_flow 12 键 + 分支/并行/循环/不可达 fail-closed 测试）；(2) GDPR-7 双跑确定性验证器 verify_stage1_gdpr7_determinism_v1.py：两次解析 7 个 BPMN byte-identical 且与 membership 锁定的 stage1_gdpr7_process_records_v1.json 逐字节一致；manifest s1_1_s1_4_determinism_v1（input/schema/config/implementation hashes、safety：零 API、不用 Stage 3 Gold 调 Stage 1、不推断人工决定）；(3) MASTER_PIPELINE 总表 S1.1/S1.2/S1.4 → verified、S1.3 → partial（精确缺口 P2）；S1.5-S1.7 保持 blocked（人工 Process Gold 未开始）；本轮零新增 LLM/API，Gold/contract/Stage 3 gate/publication 未修改 | 矩阵 + 确定性 manifest + record_change 事件 + audit --with-tests |
| 3.4.44 | 2026-08-11 | **Stage 2 正式结论收口 + S2.11 许可/G0.7 adapter 资格证据（Checkpoint 1）**：(1) stage2_formal_conclusion_v1.json/.md/manifest/export/独立 verifier（conclusion d882a5e2…、verifier 16fd36f5… VERIFIED）：正式名称 Rules-Only/Direct-LLM/Rules+LLM-Repair（comparison-only），旧代号仅 Pipeline 对照；仅授权 G0.4 口径（粗五字段主报告 + modality label 单独 + 细五字段诊断 + evidence-span unavailable；不引用历史六字段 development aggregate）；论文安全结论：Direct-LLM 领先 action/condition/constraint 与 modality label accuracy、Rules-Only 领先 actor/exception、Rules+LLM-Repair 净负保留对照停止优化；披露数据规模 150 句、重建方法（paper-faithful independent reconstruction，非 Sun 原始/exact reproduction）、历史调用 300、新增 0、无显著性推断；每条结论回指 报告/manifest/hash；**B0-R5/D1-R5 → verified**（正式结论 DoD 达成），H1 保持 comparison-only 结论，三方法正式比较不因 S2.11/S2.13 未完成而降级；(2) paper/CLAIM_EVIDENCE_MATRIX 更新：头注正式结果、C07 PLANNED→VERIFIED（共享已达成）、C09 更新（正式比较确认净负）、新增 C23（三方法正式字段级互补结论）与 C24（B0-R5/D1-R5 结论包）；(3) **日期修正**：10 处无依据的 2026-08-12 引用全部改为 2026-08-11（status/audit docstring、MASTER_PIPELINE S2.10/S2.12 行与 changelog 3.4.42/3.4.43、s2_11 dry-run、测试断言、构建脚本），机器 UTC timestamp 保持实际生成时间；(4) S2.11 许可与 adapter readiness v2（s2_11_license_adapter_readiness_v2）：本地许可证据核账 （references/barrientos_2026 无 LICENSE/README/metadata 声明 → 四类均为 unknown_pending_confirmation，不自行推断）；外部证据 pending（本地无权威 URL/DOI，未用搜索片段代替）；S2.11 精确缺口清单 （许可/激活授权/映射决策/人工 Gold/G0.5 冻结/adapter 实现）；条件未达 → 不发出授权句；(5) G0.7 Barrientos adapter registry dry-run（g0_7_barrientos_adapter_registry_dry_run）：schema/标签/数据/指标/许可注册、modality 3→4 不可直接映射边界、precondition/norm/temporal→span adapter 边界、definition/span 对齐/cross-reference/evidence provenance、synthetic fixtures only、外部标签永不自动成为 Gold；9 项 adapter 契约 fail-closed 测试（synthetic）；G0.5/S2.11 正式状态未改变；本轮零新增 LLM/API，Gold/contract/Stage 3 gate/publication 未修改 | 结论包 + matrix 更新 + 许可/adapter readiness + record_change 事件 + audit --with-tests |
| 3.4.43 | 2026-08-11 | **正式三方法比较 + S2.10 verified + S2.12 描述性分析 + S2.11/S2.13 dry-run（Checkpoint B，零 API）**：(1) stage2_formal_three_method_comparison_v1.json/.md/manifest/export/独立 verifier（report c9d76544、manifest dc41eb4b、verifier 22c23331，verifier VERIFIED）：只使用授权口径（粗五字段主报告 + modality label 单独 + 细五字段诊断 + evidence-span unavailable 不混历史六字段 aggregate）；逐方法 per-field P/R/F1、label 指标、方法间 delta 矩阵、粗五字段均值（描述性）、历史调用成本（B0 0/D1 150/H1 150）与新增 0、结论回指 hash（H1 净负停止优化、D1 优势 action/condition/constraint+label acc、B0 优势 actor/exception召回、共同局限 evidence-span、三方法 ready ≠ 全 Pipeline 完成）；(2) S2.10 → verified（授权后 DoD 真实满足）；S2.12 → partial（正式描述性共同错误分析交付、retrospective 标注，full DoD blocked on S2.11）；(3) S2.11 数据资格与映射协议 dry-run（s2_11_data_qualification_mapping_dry_run：Barrientos 2026 资料与 Stage1 GDPR-7 只读核验、schema 映射与 modality 3→4 不兼容、adapter 边界、L1/L2/L3 复杂度候选（G0.5 未冻结）、可比/不可比指标、需人工 Gold、外部标签不得冒充 Sun-compatible Gold 防护、hash/manifest/export 方案、before/after；授权条件未达到 → 不发出授权句；G0.5/S2.11 正式状态未改变）；(4) S2.13 gap capsule（s2_13_stage2_freeze_gap_capsule：完成项与剩余项精确清单，明确 final_experiment_ready=true = 三方法正式评价资产就绪 ≠ S2.13/全项目完成；S2.13/S1.7/S3.7 未标完成、无伪 Oracle）；本轮零新增 LLM/API，Gold/contract/Stage 3 gate/publication 未修改 | 比较报告 + S2.12 分析 + S2.11 dry-run + S2.13 gap + record_change 事件 + audit --with-tests |
| 3.4.42 | 2026-08-11 | **final-readiness 真实 fail-closed 验证 + 残留语义清理（Checkpoint A）**：(1) 可复用验证模块 src/bpc_hybrid/formal_arm_verification.py——精确 method→manifest→predictions→results→capsule→verifier 映射（ARM_REGISTRY）；每个 arm 从磁盘重算 manifest hash、逐项校验 method_id/claim_scope=formal/is_formal_performance_result/预测与结果文件存在且 hash 匹配/input-Gold 绑定重算/new calls=0 声明；comparison capsule 重核：input v2/Gold hash 重算、G0.4 semantic hash 三方一致（manifest vs comparison vs derived artifact 重算）、三 arm manifest 磁盘 hash 与 per_method 记录逐项比对、main_view_publishable/授权一致、all_three_published_and_verified 由验证结果派生（自报值不再作为输入）；(2) status.py formal_final_gate_conditions() 改用 verify_all_static()（不信任自报）；audit.py 三方法 ready 分支实际执行 verify_all_with_verifiers()——三个独立 verifier 以 subprocess 真实运行（非仅查文件存在），全过 → pass final_gate_conditions_met，否则 methods_unexpectedly_ready error；(3) 篡改 fail-closed 验证：三 arm 各一 artifact、direct_llm manifest method_id、comparison capsule per_method hash、G0.4 manifest semantic hash 共 6 类篡改 → verify_all_static 全 False、audit 出现 methods_unexpectedly_ready error、final_experiment_ready=false（配置 ready 单独不能维持门禁）；9 项新 tamper tests；(4) 授权前残留语义清理：G0.4 contract claim_scopes.formal 更新为三方法均 formal；coarse role/consequence 改为“历史六字段 aggregate 不可正式发布、授权五字段+label 主报告可发布”；coarse manifest not_publishable_reason → historical_aggregate_not_publishable_reason；comparison capsule not_comparable 更新（三方法均 formal，不可比对象为历史六字段 aggregate）；methods.json sun_rule_only notes 移除“candidate result 尚未发布”表述（正式发布 2026-08-11），明确三方法 ready ≠ S2.13/S1.7/S3.7 完成；release manifest v2 因 methods_config hash 变化同步重发布（8b3cbd2e，verifier 全过）；1703 tests passed；零新增 LLM/API，Gold/contract/Stage 3 gate/publication 未修改 | formal_arm_verification 模块 + tamper tests + 语义清理 + record_change 事件 + audit --with-tests |
| 3.4.41 | 2026-08-11 | **用户四项正式授权应用（zero-API，门禁最终打开）**：(1) G0.4 正式主报告授权——句子级粗粒度五 span 字段（actor/action/condition/constraint/exception）+ 单独四分类 modality label 指标；modality evidence-span 明确 unavailable （不置零、不纳入 aggregate）；细粒度五字段诊断/对照；历史六字段 coarse aggregate 仅 development provenance；Gold 未修改、未伪造 modality evidence spans；g04_evaluation_views_contract_v1.json 记录授权，coarse view manifest main_view_publishable 翻转为 true（授权记录在案）；(2) direct_llm 门禁 ready（formal_status=ready、command_status=formal_ready_candidate_authorized），默认 zero-API 发布已绑定 D1-R3 snapshot：publish_snapshot_formal_arm.py --method direct_llm → data/predictions/direct_llm_formal_arm_v1 + data/results + reports （claim_scope=formal、is_formal_performance_result=true、new calls 0、独立 verifier VERIFIED、snapshot 字节锁定 9188093c）；(3) sun_llm_fallback 方案 A 应用（formal_status=ready、command_status=formal_ready_candidate_authorized、role=comparison_arm_only、notes 明确停止优化与 comparison-only 边界），zero-API 发布已绑定 H1 snapshot → sun_llm_fallback_formal_arm_v1（snapshot 字节锁定 4fd7c116、verifier VERIFIED）；(4) final-readiness fail-closed 加固实施：status.py formal_final_gate_conditions() （三方法 capsule 完整 + G0.4 合同授权 + comparison capsule 全 hash 一致——input v2/Gold/三 arm manifest 磁盘重算比对），final_experiment_ready 必须同时满足；audit.py methods_unexpectedly_ready 条件化（条件真实满足 → pass final_gate_conditions_met，不再无条件 error）；comparison capsule v2 重建（三方法 claim_scope=formal、main_view_publishable=true、formal_arm_capsules.all_three_published_and_verified=true、新 hash 4aaaef13）；**条件全部真实满足 → final_experiment_ready=true、BLOCKERS 0、ERRORS 0**（非仅配置翻转：三 capsule + verifier + comparison 一致 + G0.4 授权全部落地）；tests 更新 11 文件（门禁断言 True、capsule complete、unexpected-ready 条件化）；1694 tests passed；本轮未调用任何 LLM/API，Gold/experiment_contract/Stage 3 gate/publication status 未修改 | 三 formal arm capsule manifest + comparison v2 + 加固代码 + record_change 事件 + audit --with-tests |
| 3.4.40 | 2026-08-11 | **shared comparison hash correction + 门禁 dry-run 验收缺陷修正**：(1) comparison capsule 错误绑定修复——build_d1_h1_zero_api_reevaluation_v1.py 与已生成 comparison capsule 曾硬编码错误 coarse-view semantic hash （d15061d7...5c3），权威值为 d15061d74b41c58dd4278f0a675327099453564090005f9b58b1d352de5cfe39（G0.4 manifest derived_view.semantic_sha256 与 committed derived artifact 重算一致）；硬编码已删除，新增 _authoritative_coarse_view_hash()：从 G0.4 manifest 读取 + derived artifact 重算 + B0 formal manifest G0.4 声明三方交叉验证，任一不一致 fail closed；D1/H1 reevaluation manifest/comparison capsule JSON+MD 重建（capsule 新 hash 89992562...、manifest 8ce1dac0...）；D1/H1 predictions 字节未变（D1 9188093c...、H1 4fd7c116...，与 registry/manifest 锁定一致），新增 API 调用 0；篡改/硬编码错误 hash 测试全部失败关闭；(2) D1/H1 方法门禁 dry-run v2 事实修正（不应用）：Direct-LLM——保留候选未授权，明确 150-row snapshot 已绑定 formal input v2，授权后默认路径 = 该 snapshot zero-API 正式 publication（不重调 API），仅绑定失效或用户明确要求重跑才需新预算，删除 v1 "正式运行必然需要新 LLM budget" 错误表述；Rules+LLM-Repair——保留 comparison-only/停止优化，明确 snapshot 授权后可 zero-API 发布为正式 comparison arm，纠正 v1 错误主张：comparison_only_ready 不被现有 status/audit 识别为 ready（blocker 不会减少），列出两方案（A 推荐：formal_status=ready + role/notes 标记 comparison-only，不动 audit/status 语义；B：保留 comparison_only_ready 但需同步修改正式终态集合与 audit/status 语义）并给出模拟后 blocker 状态；(3) final-readiness hardening dry-run 包（outputs/reports/final_readiness_hardening_dry_run.json/.md）：记录缺陷（status.py 仅凭 formal Gold+三方法 ready+input/Gold 文件存在即可置 final_experiment_ready=true，不要求 三方法 capsule 完整、不要求 G0.4 主合同授权；audit.py 三方法全 ready 时无条件 methods_unexpectedly_ready error），内存最小复现（三方法全 ready → final gate 提前打开 + unexpected error 并存；D1 单独 ready → false；H1 comparison_only_ready 不被识别 → false），提出 fail-closed 目标语义（正式终态集合 + 三 capsule 独立 verifier 通过 + comparison capsule 全 hash 一致 + G0.4 主口径用户授权，此前 final_experiment_ready 必须 false，授权且真实满足后 不再报 methods_unexpectedly_ready，配置翻转不能提前开门），含代码/测试/文档变更清单与统一授权句；(4) G0.4 决策建议 dry-run（不应用）：正式主报告 = 句子级粗粒度五 span 字段 + 单独 四分类 modality label 指标；modality evidence-span 明确 unavailable 不置零不纳入 aggregate；细粒度五字段诊断/对照；历史六字段 coarse aggregate 保留 development provenance；main_view_publishable 未翻转；本轮未应用任何方法门禁、未调 LLM/API、未改 Gold/contract/Stage 3 gate/publication status；新增 12 项聚焦测试 | comparison capsule 重建 + v2 决策包 + hardening dry-run + record_change 事件 + audit --with-tests |
| 3.4.39 | 2026-08-10 | **D1/H1 zero-API 重评 + shared comparison capsule + S2.10/S2.12 partial 状态**：D1-R3（s27_d1_v6_r3_clean_rerun_150_hist56d_v1）与 H1（s28d_h1_150_v4pro_v1）历史 150 条 predictions 逐项核验绑定（150 IDs、input text hash vs formal input v2、prompt lock、schema-valid 全过）后用与 B0 完全相同的 Gold 视图/合同/evaluators 做 zero-API 重评 → outputs/evidence/d1_h1_zero_api_reeval_v1/（d1/h1 各自 reevaluation + comparison_capsule + manifest）：D1 coarse 五字段 F1 0.7579/0.9437/0.8380/0.7427/0.7619（与历史粗口径逐位一致）、H1 coarse 0.4296/0.8945/0.7774/0.6200/0.8800；claim scope：B0=formal，D1=candidate/formal-gate-blocked，H1=candidate/comparison-only/formal-gate-blocked；comparison capsule 绑定 input v2/Gold/视图/预测 schema/normalization/evaluators/三方法 snapshot hash/claim scope/gate 状态/历史调用数（D1 150 + H1 150）/本次新增调用 0/可比与不可比边界（modality evidence-span 三方法均 unavailable；历史粗数字仅 development provenance）；D1/H1 结果未写入 data/predictions 或 data/results，未标 claim_scope=formal；D1/H1 各自方法门禁 dry-run 决策包（direct_llm / sun_llm_fallback 分开：exact before/after、zero-API 绑定证据、风险、预期 audit 变化、可复制授权句）**未应用**；S2.10 → partial（B0 formal arm 组件评价 verified，全方法比较待授权）；S2.12 → partial（描述性/探索性基础设施，retrospective 非 preregistered，full DoD blocked on S2.11）；S2.13 full DoD、S1.7、S3.7 未标完成；未启动 Stage 3 Oracle 或端到端实验 | comparison capsule + decision packages + record_change 事件 + audit --with-tests |
| 3.4.38 | 2026-08-10 | **治理/证据一致性修复 + G0.4 双口径评价合同 + B0 正式 arm 工具链**：(1) 授权包矛盾修复：sun_rule_only_method_gate_authorization_dry_run.json 拆分 proposal （dry_run_not_applied，历史提议）与 application（applied_by_user_authorization_2026_08_10，commit 6a29766 应用）双状态，过时 post-authorization 命令改为正式入口 run_b0_formal_arm.py（不再指向 outputs/development candidate 目录冒充正式发布）；(2) 实时状态文本同步：MASTER_PIPELINE B0 方法表（B0-R4 candidate verified + 方法门禁授权，B0-R5 blocked on 正式结果发布）、AGENTS.md 静态状态（formal_gold_publication_ready=true、route locked、Gold 已发布、freeze true；门禁定义未变）、PROJECT_AUDIT 残留不一致修正；(3) **证据缺口记录**：授权包引用的 outputs/development/b0_r4_formal_candidate_v1/manifest.json 被 .gitignore 排除、远端历史不存在——正式 B0 capsule 必须自包含（versioned manifest 携带 input/实现/方法门禁/evaluator/语义结果 hash），本 checkpoint 的正式 arm 设计即消除该依赖；(4) **G0.4 双口径评价合同** configs/evaluation/g04_evaluation_views_contract_v1.json：粗（句子级，Sun 对齐主口径）与细（clause 级，诊断/对照）视图分离、禁止跨口径混表、模态四分类 label 指标单独报告、六字段按固定 Sun literal-overlap 主合同、strict/token/clause/actor-action 仅诊断；正式粗视图由已发布 Gold 确定性派生（src/bpc_hybrid/g04_coarse_view.py，共享归一化）；**一致性核验结论：semantic hash 不匹配 （d15061d7 vs 历史 6e19cf3c）——已发布 Gold 的 modality 为纯字符串，局部 modality evidence span 不可恢复（147/150 条仅 modality evidence 不同，其余字段逐位一致）→ 按合同**停止粗口径主正式指标发布**，历史粗数字保留 development provenance；粗视图五字段 span 指标与历史逐位一致（actor 0.8203/action 0.8927/condition 0.7738/constraint 0.6182/exception 0.8800）可正式报告；(5) 正式评价模块 src/bpc_hybrid/formal_stage2_evaluation.py：五字段 span 指标 + modality label 四分类 + modality evidence-span unavailable（明示原因，绝不静默置零）+ 计时隔离（canonical 产物无计时，telemetry 单独）；(6) 正式 B0 arm 入口 scripts/run_b0_formal_arm.py（claim_scope=formal、is_formal_performance_result=true、前置 fail-closed：release v2 verifier 全过 + sun_rule_only ready + D1/H1 仍 blocked；输出 data/predictions/b0_formal_arm_v1 + data/results/b0_formal_arm_v1 + outputs/reports manifest/export/capsule/独立 verifier，no-overwrite/staging/原子 rename）；(7) audit 方法覆盖区分：formal_predictions_results_capsule_not_produced（空）→ formal_predictions_results_capsule_partial（部分方法覆盖，列出已发布方法）→ complete（三方法全覆盖，pass）；单文件不再被误读为完整三方法 capsule；聚焦测试 11 项（粗视图一致性/评价模块/前置 fail-closed/方法覆盖） | 授权包修复 + G0.4 合同 + 粗视图证据 + record_change 事件 + audit --with-tests |
| 3.4.37 | 2026-08-10 | **sun_rule_only 方法门禁授权应用**：用户明确授权仅修改 configs/methods.json 中 sun_rule_only 的 formal_status （blocked_final_sun_stage2_reimplementation_required → ready）与 command_status （development_only_not_formal → formal_ready_candidate_authorized）；sun_llm_fallback/direct_llm/experiment_contract/stage3 gate/Gold/publication status 均未修改；未调用任何 LLM/API。release manifest v2 的 methods_config implementation hash 同步重发布（v2 input/Gold 字节不变），verifier 53 项全过；audit formal_methods_not_ready 从 3 方法减为 2 方法（sun_llm_fallback/direct_llm），final_experiment_ready 仍 False（其余两方法未就绪），methods_unexpectedly_ready 未触发；test_sun_modality_gate 隔离边界断言更新（sun_rule_only=ready + 其余 blocked）；authorization dry-run 包追加 application_status=applied。B0-R4 promotion 完成，formal 三方法比较仍待 D1/H1 LLM 授权 | methods.json diff + record_change 事件 + audit --with-tests |
| 3.4.36 | 2026-08-10 | **formal benchmark input v2 修正 + 发布审计加固 + B0-R4 formal candidate 闭环**：data/input/estg150_formal_inference_input_v2.json （150 条 Gold-blind 可执行输入：sample_id/approved_text_en/raw_text_de/language/source_ref/input_text_sha256/provenance，零裁决内容，文本与冻结 Layer E 逐位一致，membership payload 与冻结文件一致），v1 input 保留并标记 membership-only; not sufficient as executable model input（sidecar STATUS.md）；formal_benchmark_release_v2.manifest.json/.md/export_index 绑定 v1 限制、v2 输入、已发布 Stage2/Stage3 Gold（未改动）、implementation/source hashes、授权 commit 5d56f03；独立 verifier verify_formal_benchmark_release_v2.py（53 项磁盘重读核验）接入 audit：pass formal_benchmark_release_verified / error formal_benchmark_release_invalid（篡改即败）；frozen capsule 语义拆分（formal_gold_capsule_frozen pass + formal_predictions_results_capsule_not_produced warning，predictions/results=0 不再误读）；过时状态文本修正（0/150 input-gate-only、route reopened、publication paused 移除）；b0_d1_formal_readiness_v2：D1-R3/H1 历史 150 条 predictions 与 formal input v2 逐项绑定核验全部通过（IDs/文本 hash/prompt/model/sampling/schema-valid）→ zero-API candidate 重评允许，无新 API 调用；B0-R4 formal candidate runner （Gold-blind，只读 v2+锁定资产）150 条全量运行 + 双跑语义 byte-identical：主口径 F1 0.71865（P 0.6845/R 0.7564，与 B0-R3 快照逐位一致）；方法授权 dry-run 包 （sun_rule_only before/after、绑定 hash、正式运行命令、预期 audit 变化、回滚）未应用；S2.13 仍 blocked（S2.1-S2.12 full DoD 未达成），Gold publication subtask verified、executable input v2 verified、B0-R4 formal candidate verified / promotion pending、S2.10/S2.12 blocked on 正式三方法结果 | release manifest v2 + verifier + readiness v2 + candidate manifest + record_change 事件 + audit --with-tests |
| 3.4.35 | 2026-08-10 | **S2.13（Gold publication subtask）formal Gold 实际发布**：`scripts/publish_formal_gold_v1.py` 正式运行（用户明确授权，基线 30eab2c）→ `data/input/estg150_formal_input_v1.json`（150 ids，membership payload `a9a746d1…` 与 estg_150_membership_hashes.json 逐位一致）、`data/gold/stage2/estg150_formal_gold_v1.json`（150 条 decision-only Gold，span 文本逐条回指 approved_text_en，decisions 全 ∈{accepted,edited,rejected}，零 LLM 草案/元数据泄漏）、`data/gold/stage3/stage3_matching_gold_v1.json`（25）+ `stage3_violation_gold_v1.json`（33）（item_ids 与冻结 correction 对齐、decision-only）、`outputs/reports/formal_gold_publication_v1.manifest.json` + `.md`；发布器确定性重放验证通过（no-overwrite 字节一致，manifest git 快照排除自身输出后稳定），34 项发布后验证全通过（schema/hash/membership/decision-only/许可排除/计数）；audit `formal_capsule_not_frozen` 解除（input=1/gold=3，`_meaningful_count` 递归修复，BLOCKERS 3→2）；B0-R4/D1-R4 行 ready 核账：共享输入/Gold/evaluator 齐备，剩余 blocker 分别为缺 formal claim_scope 运行入口 / 缺 LLM 授权预算 → 本轮 zero-API 核账不执行任何重评（不调 API、不伪造 Rule/Process Records、不提升 development 指标）；S2.10/S2.12 仍 blocked on 正式三方法运行 | 发布 manifest + record_change 事件 + audit --with-tests |
| 3.4.33 | 2026-08-06 | **S2.2 裁决冻结达成**：用户 2026-07-18 完成的 150/150 Layer E 裁决（adjudicated、reviewer=user）经用户授权从 56d2b03 历史 blob 恢复至活动 v2 文件（v2 工作流 2026-07-16 重建时未迁移；新脚本 `scripts/restore_layer_e_adjudication_from_56d2b03.py`，按 sample_id 合并 6 个用户输入字段、保留 llm_candidate 等、备份+validate_global 双真+原子替换）；gate 2 `human_review_freeze_ready` **False→True**（150/150 adjudicated、900/900 decisions、approved 150/150），BLOCKERS 8→7（`annotation_freeze_pending`→pass `annotation_freeze_ready`）；S2.2 行 → verified；S2.9 行 → verified（D1 侧锁定 + S2.2 frozen 依赖满足）；`validate_layer_d_v2.py` layer_e_pristine FALLBACK 语义更新（0/150 计数器不再适用，promote 从不写 Layer E，字节保护由 run_config sha256 主路径承担）；15 个状态依赖测试更新 + 3 项 restore 测试；1486 passed / 24 skipped。formal Gold 发布仍 blocked：route/data/stage3 各自重锁 + publication gate 状态白名单精确匹配；随后 D1-R4/B0-R4 三方法正式比较解锁 | Layer E 恢复 manifest + validate_global 报告 + record_change 事件 + audit --with-tests |
| 3.4.32 | 2026-08-06 | D1-R3 完成：锁定配方固定快照干净重跑（150 calls v4pro 官方API thinking-disabled 无json_object 4096/temp0/top_p1；prompt sha 3aa64877、model 三态、sampling/transport 与 estg150_d1_active_registry_v1.json 逐项一致）；150/150 有效、0 验证失败、0 LLM 错误、0 事故；新评估脚本 scripts/evaluate_d1_r3_clean_rerun.py（git show 56d2b03 只读提取 Layer E/membership → build_canonical_gold_records，membership sha e8e62686 与注册绑定一致 → 同一进程双评 R1/R3）；R1 重评 F1 0.773495 与已登记数字逐位一致（评估路径交叉验证）；R3 F1 0.775625（P 0.879268/R 0.693839，missed 323 vs R1 327）；逐字段 F1 delta：modality −0.01123/actor −0.02778/action +0.00051/condition +0.00660/constraint +0.02094/exception +0.05929；失败类型分析（1055 gold span）：R3 matched 732/wrong_field 169（constraint 100 最大头）/not_extracted 154（constraint 69），R1 matched 728/wrong_field 185/not_extracted 142；结论=固定快照复现 R1 并微优（+0.0021，噪声范围），可重放性验证成功；D1-R3 行 → verified；D1_ERROR_ANALYSIS.md §8 追加 R3 失败类型小节；PROJECT_AUDIT 同步。D1-R4 仍 blocked on formal Gold | D1-R3 experiment_run 事件 + evaluation_d1_r3_20260806.json + audit --with-tests（1483 passed） |
| 3.4.31 | 2026-08-06 | D1-R2 锁定完成：新增 `configs/models/estg150_d1_active_registry_v1.json`（schema `estg150_d1_active_registry@1.0.0`）——v6 prompt（sha 3aa64877，与磁盘/loader/run manifest 三方 hash 一致）、v5 七月基线（79f6f76f，不可改）、deepseek-v4-pro fail-closed 钉死、sampling（temp 0/top_p 1/max_tokens 4096）、seed 策略 `unsupported_or_omitted`（官方 API 无 seed，可复现依赖 temp0，manifest 记录实际发送值）、transport 配方（thinking-disabled、无 json_object）、共享输入（input_150_hist56d_v1.jsonl，sha c7dffcc4）与 evaluator（sun_literal_overlap_evaluation@2.0.0，config sha 352113b5）、预算合同（每批逐批用户授权+`--max-calls` 硬上限 150、无授权不批）、D1-R1 VERIFY-PASS 运行登记（manifest sha 87cb1bea）；新增 12 项 lock-config 测试（含 S2.9 Gold 不可见核查：6 个 few-shot 合成 fixture 与 150 测试句相等/嵌入零交叠）；§8.7 D1-R2 行 → verified；§8.5 S2.9 行 DoD（D1 侧）达成注记，整行保持 partial（S2.2 未 frozen）；PROJECT_AUDIT/AGENT_RUNBOOK 同步。下一步=D1-R3（固定快照干净重跑 150 calls + 错误分析，需用户逐批授权） | D1-R2 lock-config 12 项 focused 测试 + audit --with-tests + record_change 事件 |
| 3.4.30 | 2026-08-04 | 新增 §8.7 D1 方法级复现修复 Pipeline（D1-R0–R5，与 §8.6 B0 同构同门禁）：D1-R0 整合（ready，核验 run_direct_llm.py + prompt loader + s28_s29 产物 tracked）→ D1-R1 低召回修复（4 个子批次：FIELD-TYPING 双向收益 / PROMPT-CONTRACT / VERIFY-PASS / CLEAN-RERUN）→ D1-R2 锁定 → D1-R3 快照+错误分析 → D1-R4 三方法共享 Gold → D1-R5 结论；硬约束含逐批 LLM 授权+硬预算。新增 docs/D1_ERROR_ANALYSIS.md：D1 低召回根因（constraint 215/354 漏抽=99 进 action+91 未抽+16 进 condition；prompt 省略指令与 few-shot 缺口；运行事故 lost104/recovery26）；字段归位理论 R 上限 0.288→0.699 | 用户指示"与 B0 同理，列出 D1 pipeline 严格逐点修复"；D1 逐字段重算分析 |
| 3.4.29 | 2026-08-04 | B0-R3 由进行中改为 **verified**：快照运行（F1 0.71865）+ 最终态错误分析（B0_ERROR_ANALYSIS §8）均完成；至此 B0-R0–B0-R3 全部 verified，B0 完善阶段结束；B0-R4（三方法正式比较）待 formal 门禁重锁，B0-R5 待 B0-R4 | B0-R3 experiment_run 事件 + §8 错误分析事件 |
| 3.4.28 | 2026-08-04 | 状态行更正：B0-R1 由 ready 改为 **verified**（§8.6.1 七个子批次全部闭环，DoD 三条验收线达成）；B0-R3 由 blocked 改为 **进行中**（56d2b03 快照运行完成 F1 0.71865 + manifest，正式错误分析待补）；B0-R4/R5 仍 blocked on formal Gold | §8.6.1 各批次事件与 manifest |
| 3.4.27 | 2026-08-04 | 三项用户授权执行并入库：(1) LEXICON-DECISION 路径 b——13 个 actor 名词以 `authorized_local_frozen_estg150_gap_2026_08_04` 加入 v2 词典（治理覆盖严格记录；覆盖/未覆盖 P/R 分别报告）；(2) B0-R2 门禁翻转——`method_conformance_status` 改为 `verified_method_level_independent_reconstruction`，`sun_stage2_baseline_not_paper_faithful` blocker 按设计解除（BLOCKERS 9→8），B0-R2 行状态 verified；(3) B0-R3 固定快照运行（最终方法+授权词典，56d2b03 输入）——主口径 F1 **0.71865**（P 0.6845/R 0.7564），优于原始 0.71019，按用户条件授权标记为论文依据候选；actor F1 0.8039（R 0.958），覆盖 47/48（P 0.692/R 0.979/F1 0.811）未覆盖 1/48（代词 "It"）；§8.6.1 LEXICON 行更新；formal 门禁（Gold 冻结/route/stage3）仍锁定 | 用户授权逐字记录 + B0-R3 experiment_run 事件与 manifest |
| 3.4.26 | 2026-08-04 | B0-R1-LEXICON-DECISION 治理分析与 CLAUSE-REVIEW 复核入库：13 个无词典覆盖 actor 名词的扩展违反 S2.3 公开种子构造模式（`public_marker_sources_en_v2.json` construction_mode=pinned_public_seed，9 来源全为公开引证）与"不看 Gold 调规则"硬约束（缺口选择由开发 Gold 驱动）→ 需用户决策，合规路径 a/b/c 写入 §8.6.1 与 B0_ERROR_ANALYSIS；CLAUSE-REVIEW 复核结论=不改动（v2 口径不依赖 clause 对齐，58 个真正漏抽中仅 4 个在未配对 clause）；C7 过短边界判定为质量类（any-overlap 口径无主指标收益）暂缓 | 治理约束复核 + 分析证据 |
| 3.4.25 | 2026-08-04 | B0-R1-ACTOR 实测结果入库（commit f82b2b7+b0548c1，run v2）：真实 CoreNLP 取证（8 个词典内漏抽=5 个无情态 nsubj + 3 个 obl+case by/to），修复=clause 内全 nsubj 弧候选 + obl/by-to + 首个过滤候选胜出 + actor 中心词词典校验（排除自身 case 介词与尾部标点）；实测主口径 F1 0.71024→0.71205（**+0.0018，本系列首个正向 delta**），R +0.0066、P −0.0023，actor F1 0.616→0.670，8/8 漏抽找回；v1 无中心词校验 −0.0021 被拒（迭代验证）；§8.6.1 ACTOR 行更新；C7 过短边界留待后续 | B0-R1-ACTOR experiment_run 事件与运行 manifest（v1/v2 两轮） |
| 3.4.24 | 2026-08-04 | B0-R1-ALIGN 实测结果入库（commit fcf7b34）：DE↔EN cue 对应验证（`_cross_validates` 语言学情态映射表+否定极性+数字锚，equal-count/monotone/split 三路径统一，split 连接词优先切点+逐片验证）；validated 107→49（validated_split 42→0）、unsupported 30→72，"无伪 validated" DoD 达成；主口径 span 指标不变（F1 0.71024），label 面板 79.33%→78.85%（−0.48pp 记录代价），strict clause accuracy 0.6407→0.6364，independent82 macro F1 +0.0012；判定保留（正确性 DoD 项），validated_split=0 记为副作用待细化；§8.6.1 ALIGN 行更新 | B0-R1-ALIGN experiment_run 事件与运行 manifest |
| 3.4.23 | 2026-08-04 | B0-R1-ACTION 与 B0-R1-SCOPE-DISAMBIG 实测结果入库：ACTION（commit 00f4ad8+efb3d14）主口径 F1 +0.00005（持平），质量收益（主语开头 8→0、strict-exact action 3.0×），定性为边界质量修复而非主口径驱动项；SCOPE-DISAMBIG（commit a3ad64f+2de85b0）候选真实运行 F1 −0.0005（负），按 §8.6 迭代规则拒绝并回退，44 个同界双发中 43 个为双 tregex（registry 模式重叠），根因=gold 对 "to the extent"/关系从句语义内部不一致，不读 Gold 前提下规则层不可安全消歧，记为方法局限；§8.6.1 子批次表两行更新 | B0-R1-ACTION / B0-R1-SCOPE-DISAMBIG 的 experiment_run 事件与运行 manifest |
| 3.4.22 | 2026-08-04 | B0-R1 推进与子批次拆分：(1) B0-R1-E2 真实离线重评（`sun_literal_overlap_evaluation@2.0.0`、同一 canonical Gold 双评 v10a/C3：F1 0.7099→0.7102，旧 clause-aligned 0.5398→0.5326 被推翻，非主口径结论）；(2) B0-R1-ERR 逐 span 错误分析（`docs/B0_ERROR_ANALYSIS.md` + `scripts/analyze_b0_error_types.py`）：79% missed 内容在其它字段、80% 错误预测压其它字段 Gold；根因 C1 action 吞并（matched action 中 192/212 过长、中位超 54 字符）、C2 constraint↔condition 混淆（114+31）、C7 under-extension（202 个 matched 过短，modality evidence 80）、C3 modality label 79.3%、C4 actor missed 22（8 依赖失败+14 词典缺口）、C5 clause 38/231、C6 结构性限制；B0-R1 行完成信号更新，新增 §8.6.1 子批次表（ACTION/SCOPE-DISAMBIG/ALIGN/BRIDGE/ACTOR/LEXICON-DECISION/CLAUSE-REVIEW）与每批验收纪律（重评协议 + delta 记录）；B0-R3 正式错误分析保留 | 用户指示"寻找 B0 准确率不高的原因并做成文档、逐个修复"；B0-R1-E2/B0-R1-ERR 的 `experiment_run`/`change` 事件与 manifest（commit bcd3193/02dea72） |
| 3.4.20 | 2026-08-01 | 新增 B0-R0–B0-R5 方法级复现修复 Pipeline：以 Sun 核心组件、顺序和宽松同字段 overlap 为主对照；确定性代码错误、泄漏、不可复现和口径不一致为硬门禁，作者资产缺失或单字段权衡改为披露项；明确修复后负结果可进入正式结论 | 用户确认“方法级复现即可作为正式结论”，并要求避免代码错误、不要用过严门禁卡死、对照 Sun 宽松要求并持续记录日志 |
| 3.4.21 | 2026-08-02 | B0-R0 verified：actor_action.py + 12 个 b0_v10 模块 + sun_style/lexicon_v2_runtime + estg150_b0_development v1/v2/v3/v10 + corenlp_runtime/sun_b0/bert_textcnn + stage2_evaluation v1/v3 + 7 个 v2 lexicon 资源 + SunPhraseRuleBatchBridgeMulti.java + sun_corenlp_runtime.json + sun_b0_s26_candidate_B_v1.json + sun_bert_textcnn_s24.json + estg150_b0_enhanced_s27_v10a.json + estg150_b0_v10_preregistration_v2.json + stage2_evaluator_s210_v3.json + stage2_prediction.schema.json + scripts/run_estg150_b0_enhanced_v10_development.py + test_b0_v10_integration_contract.py（15 验收点） 已纳入 main；audit 在 `sun_rule_only.method_conformance_status='blocked_until_b0_r2'` 下同时保持 `b0_paper_faithful_components_present` pass 与 `sun_stage2_baseline_not_paper_faithful` blocker；外部 441MB checkpoint / CoreNLP jar / Legal-BERT cache 仍为 external runtime prerequisites（未提交、未下载、未复制）；B0-R1 ready、B0-R2–B0-R5 仍按依赖 blocked；run_b0_batch_v10 / --help 离线验证通过；未运行 CoreNLP、未读 Gold/Layer E、未调 API、未改 D1/H1；先前 6341136 的 B0-R0-C0 仅依赖闭包，状态从 COMPLETE 修正为 verified，correction event 已追加 | 用户确认修正 6341136 误报，要求 audit 区分 component presence 与 method-conformance；要求补齐 v10 runner + CoreNLP bridge + pattern registry + s26/s24 配置 + v10 默认配置 + 离线集成测试 |
| 3.4.19 | 2026-08-01 | S2.8D-R6C1 安全补完 R6 剩余 5 个冻结 plan（原 order 6–10），形成完整 10-plan pilot 证据（用户授权新增 hard cap=5、retry=0、每 plan 至多 1 次、禁止重调 order 1–5、禁止重跑原 10-call 命令）：阶段 A 验证游标修复（37ab7ef）并实现 continuation 模式（--continuation-plan，schema h1_pilot_continuation@1.0.0）：调用前 fail-closed 绑定父 frozen plan hash/keys、prior R6 manifest/capture hash、prior telemetry 恰好 order 1–5 各一次、无 order 6–10 先例、continuation 恰为 order 6–10、交集空、并集=父 10 plan、5 个不同 sample、model/prompt/B0 hash、risk/repair_fields/reasons、--max-calls=5、与 --frozen-plan/--exclude-plan 互斥；新增 configs/s28d_r6c1_h1_remaining_pilot_plan_v1.json（sha f0946bdd…）与 29 项测试（30 验收点，含 combine 测试）；阶段 B 0-API plan-only：selected=5/5、orders=[6..10]、calls=0、交集空、覆盖 10/10、byte-identical；阶段 C 唯一一次真实命令：**actual new API calls=5**（order 6–10 各 1 次；order 1–5 新调用=0；retry=0；无 early stop；模型/capture 全对）；结果：proposed=5、accepted=1、rejected=4（canonical_invalid=4、reference_mismatch=4）、effective=1、changed=1、H1!=B0=1、gate=true、identity violation=0；canonicalizer reanchored 5/5（already-valid 1、reanchored spans 12、zero/amb/contract=0）；usage 总 9652（8000/1652）；continuation replay（s28d_r6c1_h1_remaining_pilot_replay_v1，0 API calls）逐项一致、byte-identical；新 scripts/combine_h1_pilot_runs.py 合并 R6+R6C1 为完整 capsule（s28d_r6_complete_h1_small_pilot_v1）：10/10 覆盖、keys sha=bb8d73b2…、每 plan 一次、10 不同 sample、identity 0、byte-identical；合并指标：calls=10、proposed=10、accepted=4、rejected=6、effective=4、changed=4、H1!=B0=4、effective rate=0.40、usage 总 18628（15634/2994）；P/R=not_computed；下一步 S2.8D-R7 完整 10-plan Gold-blind 结果审计与受控 P/R 评价解锁准备 | R6C1 manifest sha 38421f74…、capture sha 0e48bcb5…；continuation focused 29 passed；audit --with-tests；5 new real API calls、retry 0；Gold/Layer E/.env 未读；P/R not_computed |
| 3.4.18 | 2026-08-01 | S2.8D-R6 执行冻结的 10 次真实 deepseek-v4-flash H1 小规模 pilot（用户明确授权 hard cap=10、retry=0、每 plan 至多 1 次、不补选、不扩大）：主真实命令只执行一次；**实际 API calls=5**（≤10），5 个已调用 plan 恰为冻结 order 1–5（estg_000118/000133/000164/000206/000207），每 plan 1 次、HTTP 200、extraction=ok_message_content、requested/resolved/returned 均 deepseek-v4-flash、capture 全部绑定、无未冻结 plan、retry=0；结果：proposed=5、accepted=3、rejected=2（coordinate_canonicalization_zero_match=1、canonical_invalid=1、reference_mismatch=1）、effective=3、changed=3、H1!=B0=3、h1_non_identity_gate=true、identity violation=0；canonicalizer：reanchored 4/5、failed 1/5、already-valid spans=1、reanchored spans=7、zero=1/ambiguous=0/contract=0；usage 总 8976（7634/1342）；**early stop 触发于 order 5 之后，记录原因 plan_key_mismatch，但取证为误报**：R5 runner early-stop 计数缺陷（coordinate-canonicalization-failed 分支未推进 frozen-order 游标）导致防御性 plan-key 检查错位；已修复（游标改为 selected plan 处理开始时统一推进）+ 新增 3 项回归测试（含 frozen-plan 离线 transport replay 子集绑定保留 early-stop 状态，runner 放开 frozen+offline-transport-replay 限制）；未调用 order 6–10 保留 pilot_early_stop_not_called、不补跑；离线 replay（s28d_r6_h1_small_pilot_replay_v1，0 API calls）重建 5 个真实响应：逐 plan H1/B0 hash、accepted/effective/changed/rejection、identity、聚合计数与真实运行一致，同路径 byte-identical；机制最低可用门 passed=true（5 calls、identity=0、effective=3、changed=3、H1!=B0=3）；P/R=not_computed；下一步 S2.8D-R7（Gold-blind pilot 结果审计与受控 P/R 评价解锁准备）+ 用户决定是否授权完成剩余 5 个冻结 plan（未调用、不再调用） | 真实 manifest sha 69ea63b2…、capture sha 5c3db68b…；H1 focused 109 passed；audit --with-tests；5 real API calls、retry 0；Gold/Layer E/.env 未读；P/R not_computed |
| 3.4.17 | 2026-08-01 | S2.8D-R5 冻结 Gold-blind 小规模 H1 pilot 计划（10 calls、预算与执行门禁；0 real API calls、retry 0、未运行 pilot）：历史真实调用集合只读恢复（5 个 real_api run：canary 1 + v4-flash pilot 19 + v4-pro 偏差 20 + R1 canary 1 + R4 canary 1 = 42 calls，去重 20 个 plan keys，keys sha c813a384…）；Gold-blind 确定性选样复用现有 build_repair_plans + risk 排序，排除历史已调用 keys、每 sample 取首个 plan、取 10 个不同 sample；新 frozen plan 配置 `configs/s28d_r5_h1_small_pilot_plan_v1.json`（sha 35dc6a75…，含 B0/prompt sha、budget cap=10/retry=0、early-stop 策略、历史 keys、10 个 plan 的 risk/repair_fields/reasons/各 hash）；新 `src/bpc_hybrid/h1_pilot_plan.py` 纯函数模块 + runner `--frozen-plan` 严格绑定（B0 attempts/manifest sha、prompt variant/sha、model、plan 存在性、clause_index/risk/repair_fields/reasons、b0/clause/context hash、10 个不同 sample、execution_order 1-10、历史交集为空；`--max-calls` 必须 10、与 `--exclude-plan` 互斥；任一不一致调用前 fail closed）；early-stop 合同实现（provider model mismatch / capture binding failure / 调用计数越界 / plan key mismatch / 连续 3 次 transport-extraction 失败 → abort_remaining，剩余 plan 标记 pilot_early_stop_not_called、不补选；patch 级拒绝 record_and_continue）；默认行为（无 --frozen-plan）不变；plan-only 验证（新目录 s28d_r5_h1_small_pilot_plan_check_v1）：selected=10/10、llm_calls=0、real_api=false、patch 0/0/0、gate=false、H1==B0（150 样本逐位一致）、execution order 与 frozen 一致、keys sha 一致、历史交集空、同路径 byte-identical；新增 29 项测试覆盖 30 个验收点；H1 focused 106 passed；P/R=not_computed；下一步 S2.8D-R6 十次真实 pilot 需用户单独授权 | 0 real API calls；Gold/Layer E/.env 未读；B0/trigger/risk/prompt/validator/schema/model gate 未改；P/R not_computed |
| 3.4.16 | 2026-08-01 | S2.8D-R4 单次真实 deepseek-v4-flash canary（用户明确授权硬上限 1、retry 0，coordinate canonicalization 已启用）：run_id=s28d_r4_h1_canary_v1，requested/resolved/returned 模型均 deepseek-v4-flash；policy stream=false、thinking.disabled、response_format=json_object、tools 未发；HTTP 200、extraction=ok_message_content、reasoning=false、tool_calls=0、usage=1305/405/1710；模型返回 1 个非空可解析 patch（content 1531 chars，sha e7514386…）。Coordinate canonicalizer 正常执行：status=reanchored、3/3 span 唯一 exact 重锚（modality.evidence[0] [0,99]→[0,95]、actors[0] [55,99]→[49,95]、conditions[0] [100,211]→[97,207]，occurrence=1），zero/ambiguous/contract=0；original patch sha 810a433c…→canonicalized sha c9014f7c…。现有 canonical validator 通过、atomic merge accepted、effective_patch=true、changed=1、h1_non_identity_gate=true、H1!=B0（B0 sha 57f3564b…→H1 sha 5bcf26d7…，与 R3 离线重放 merged hash 逐位一致）、identity 字段不变；R1/R3 历史结果未改。离线 replay（新目录 s28d_r4_h1_canary_replay_v1，0 API calls）重建同一 capture：H1 sha 与真实运行一致、byte-identical。P/R=not_computed；未进入 pilot；formal S2.8 仍 blocked on S2.6 | 真实 canary manifest sha 9734c2ed…、capture sha 92df6817…；focused 71 passed；audit --with-tests；1 real API call、retry 0；Gold/Layer E/.env 未读；P/R not_computed |
| 3.4.15 | 2026-07-31 | S2.8D-R3 fail-closed unique exact-text coordinate canonicalization（development mechanism verified，0 real API calls）：新 `bpc_hybrid/h1_span_canonicalizer.py` 纯函数模块——Python/Unicode code point、0-based、end-exclusive、相对完整 source_text；搜索窗口严格为 clause_span；匹配纯 exact（无 strip/normalize/lower/fuzzy/语义）；already-valid 不动；clause 内唯一 exact match 才重锚 start/end；zero/ambiguous/contract violation 整 patch fail closed（稳定错误码）；只修改 start/end，其余字段深拷贝不变；relation 字段不处理；原子化无部分修复。接入 runner 单一共享路径（parser 后、apply_patch_envelope 前），覆盖 offline-patches/offline-replay/offline-transport-replay/allow-llm 四模式；per-event 脱敏审计 + manifest 聚合统计；_rejection_codes 映射三个稳定码。validator/prompt/schema/B0/trigger/risk/budget 未改。R3 离线 transport replay（同一 R1 capture 重建行，行 hash 96f8bbdc…）：canonicalization=reanchored、3/3 span 重锚（[0,99]→[0,95]、[55,99]→[49,95]、[100,211]→[97,207]，occurrence=1）、zero/ambiguous=0、canonical validator 通过、merge accepted、effective_patch=true、changed=1、gate=true、H1!=B0（H1 hash 5bcf26d7…与 R2 counterfactual merged hash 逐位一致）、identity 不变、重放 byte-identical。R1 历史 strict 结果（accepted=0/gate=false/H1==B0/canonical_invalid+reference_mismatch）未改。新增 26 项测试 + 更新 span-mismatch 测试（invented text 现在以 zero_match 整体拒绝）；全量测试 | 新增 26 项 S2.8D-R3 测试；focused 88 passed；全量检查；0 real API calls；Gold/Layer E/.env 未读；P/R not_computed |
| 3.4.14 | 2026-07-31 | S2.8D-R2 canary span/offset 离线取证（Gold-blind、forensic-only，0 real API calls）：逐 span 脱敏诊断证明 3/3 被拒 span 均为**正确文本、错误坐标**——文本在 source_text 与 clause 窗口内均唯一 exact match（无 zero/ambiguous），`end` 全部恰好超界 +4 字符（start Δ 0/+6/+3）；排除 Unicode/byte 混淆（纯 ASCII）；clause_span.start==0 使 frame 混淆在本样本不可区分（列为限制）。Strict replay（同一 decoder→parser→validator→merge）复现真实 canary 拒绝：canonical_invalid=1、reference_mismatch=1、accepted=0、effective=0、changed=0、gate=false、H1==B0。Diagnostic-only counterfactual（仅修正 start/end 到唯一 clause 内 exact match，文本/id/field/label/relation 不动，zero/ambiguous 即 fail closed）通过同一 validator 与 atomic merge：schema+cross-field valid、merge=accepted、effective_patch=true、gate=true、identity 字段不变；counterfactual 仅诊断，未覆盖 strict 结果、未写入真实 prediction。Prompt coordinate contract 审查（未修改）：`text == source_text[start:end]` 明确存在；0-based/end-exclusive/code-point 单位仅由示例隐含、逐 span 自检指令缺失、frame 表述歧义；masked 字段未隐藏 offset 所需信息。**结论：情况 A → 唯一推荐 S2.8D-R3：fail-closed unique exact-text coordinate canonicalization（本轮未实现）**。新增 `scripts/s28d_r2_canary_forensics.py` + 17 项离线测试；证据 `docs/research/S28D_R2_CANARY_OFFSET_FORENSICS.md/.json` | 全量测试 + experiment/change 事件；0 real API calls；Gold/Layer E 未读；P/R not_computed |
| 3.4.13 | 2026-07-31 | S2.8D-R1 单次 v4-flash canary（用户明确授权硬上限 1、0 retry）完成，**未达 non-identity 门**：requested/resolved/returned model 均为 deepseek-v4-flash；显式 policy 为 stream=false、thinking.disabled、response_format=json_object；HTTP 200，`chat.completion`，`finish_reason=stop`，`ok_message_content=1`，reasoning=false，usage=1305 prompt + 436 completion = 1741 tokens。响应形成 1 个 schema-valid patch envelope，但 span text/offset 与 source reference 不一致，原子 canonical 校验以 `canonical_invalid` + `reference_mismatch` 拒绝；valid=1、proposed=1、accepted=0、effective=0、changed=0、gate=false，H1 仍等于 B0。脱敏 capture 已保存且无凭据；未重试、未进入完整 pilot；历史真实调用累计 41 次，P/R 仍 not_computed | `outputs/development/s28d_r1_h1_canary_v1/manifest.json` + sanitized capture；全量 1137 passed, 24 skipped；experiment_run event |
| 3.4.12 | 2026-07-31 | S2.8D-R1 DeepSeek transport 离线修复（development contract verified，0 real API calls）：新 `bpc_hybrid/h1_transport.py`（显式 H1 request policy：stream=false/thinking.disabled/response_format=json_object、tools 不发；纯函数 `decode_chat_completion_envelope` 十个稳定 extraction status codes；reasoning 只存 presence/length/hash、tool arguments 只存 name/length/hash、Responses API/SSE/invalid JSON 全 fail closed；递归敏感键脱敏保留 usage 数值；安全 endpoint 描述）；`RealAPITransport` 与离线 replay 共用同一 decoder 并暴露 last_decode/last_request_policy/last_request_body_sha256；runner 新增 `--transport-capture`（--allow-llm 必需，调用前拒绝）与 `--offline-transport-replay --transport-responses-jsonl`（严格绑定，byte-identical 重放，无时间戳）；空 content 现在产生稳定 rejection code（如 empty_final_content）而非泛化 other；manifest 记录 transport 节（policy sent、safe endpoint、capture path/hash、extraction_status_counts、raw_response_saved=false）；新增 11 个 envelope fixtures 与 44 项全离线测试（合法 content→effective patch/gate=true；reasoning/tool/output/delta 均不被误当 patch；15 项验收全覆盖）；canary 未授权未运行 | 新增 44 项 S2.8D-R1 测试；focused 193 passed；全量检查 |
| 3.4.11 | 2026-07-31 | S2.8D v4-flash 真实 pilot 执行完成，**结果：未达最低成功门（如实报告失败）**：canary 1 次 + 剩余 19 次 = 20 次新调用（硬上限精确满足）；每次调用 requested=resolved=provider-returned 均为 deepseek-v4-flash（模型身份全部验证）；但 20/20 响应内容为空（sha256==空串），valid=0、effective=0、changed=0、gate=false。runner 新增 `--exclude-plan`（canary 协议用，不动 trigger/risk/budget）与 per-response `response_model`/`response_provider` 记录。历史总计 40 次真实调用（20 次 v4-pro 偏差 + 20 次 v4-flash pilot），均未产生有效 patch；无 P/R 可报（not_computed）；formal S2.8 仍 blocked on S2.6 | 新增 exclude-plan/response-model 测试 2 项；全量 1104 passed 24 skipped；canary+pilot manifests |
| 3.4.10 | 2026-07-31 | S2.8D 真实 pilot 模型偏差处理 + fail-closed 模型钉死：20 次真实调用因 .env profile 键优先级生效于 deepseek-v4-pro（未授权模型），已作为 exploratory deviation 原样保留并记录（`outputs/development/s28d_h1_real_pilot_deviation/`）；runner 新增 `--model`（--allow-llm 必需、CLI 覆盖 profile/.env、解析值必须等于 deepseek-v4-flash 否则调用前中止）并打印/记录 resolved model 与来源；preflight v2（同一冻结 20 plans/16 samples，~$0.10 上限）；canary→19 次调用待用户再次授权 | 新增 4 项模型门禁测试；全量 1102 passed 24 skipped；deviation record + preflight v2 |
| 3.4.9 | 2026-07-31 | S2.8C effective fallback 链路验证（development）：每 selected plan 增加 effective-patch audit（b0/proposed/merged hash、requested/proposed/accepted/rejected fields、merge_status、rejection codes、semantic_changed、changed_fields、effective_patch 五条件定义）；新增 `--offline-replay --responses-jsonl` 通道（response 绑定 request_id/sample_id/clause_index/prompt SHA/variant/B0 hash，缺失/重复/错配/额外全 fail closed，与真实 API 同一 parse/validate/merge 路径，manifest 无时间戳可 byte-identical 重放）；no-op 一律拒绝为 no_semantic_change 且不计入 effective；manifest 报告 `h1_non_identity_gate`；新只读对比脚本 `compare_h1_fallback_paths.py`（P/R 仅用户显式 --reference 且拒绝 Layer E/正式 Gold，本次 not_computed）；fixtures 证明合法 modality/actor/action+依赖 patch 改变 prediction（gate=true）、plan-only 保持 B0 identity（gate=false）；B0 v10a plan-only 两臂与 no-op replay 全链路验证，0 API calls；formal S2.8 仍 blocked on S2.6 | 新增 25 项 S2.8C 测试 + 既有 H1/prompt 套件全绿 + 全量检查 |
| 3.4.8 | 2026-07-31 | S2.8B masked-selected-fields repair 合同（development contract verified）：`--prompt-variant full_b0_v4\|masked_selected_v5`（默认 full_b0_v4，v4 prompt SHA 钉住不变）；新 `bpc_hybrid/h1_context.py` 纯函数遮蔽依赖闭包（actors\|actions→actor_action_map、actions→order_relations）与泄漏审计（selected IDs 不得经未遮蔽 relation 泄漏，否则拒绝 request）；新 v5 masked prompt；plan-only 也为 selected plans 记录 context audit；B0 v10a 两臂 plan-only（max_calls=50）：221 triggered / 50 selected plans / 41 samples 完全一致，两臂 predictions 与 B0 semantic hash 全等且 byte-identical，50/50 context audits 通过、0 leak、0 API calls；formal S2.8 仍 blocked on S2.6 | 新增 25 项 S2.8B 测试 + 既有 H1/prompt 套件全绿 + 全量检查 |
| 3.4.7 | 2026-07-31 | G0-TEST-REAL-BACKUP-SNAPSHOT：review-tool 测试改为 session 级纯只读快照守卫（`tree_snapshot`/`snapshot_diff`/`format_diff` + autouse session fixture），允许真实备份目录预先非空，要求整个 session 前后 byte-identical；修复 action-log 恒真断言与"目录必须为空"错误断言；新增 14 项 tmp_path 单元测试（增/删/改/改名/append/missing→created/确定性/不输出内容/symlink 越界 fail closed，平台不支持时显式 skip 并有模拟测试兜底）；全量测试首次 0 failed | 1048 passed, 24 skipped；既有真实文件 SHA 防护未降低 |
| 3.4.6 | 2026-07-31 | S2.8A Gold-blind H1 clause/field 诊断表生成器：抽出共享 B0 绑定模块 `bpc_hybrid/b0_artifact.py`（H1 runner 行为不变，既有测试全绿）；新 `build_h1_trigger_diagnostics.py` 只消费 persisted B0 + manifest + inference-visible telemetry，逐 clause 输出确定性特征行（含 per-feature missing 指标），manifest 绑定输入/输出 SHA-256 并做 coverage accounting；B0 v10a 上 150 samples/256 clauses 离线生成，重复运行 byte-identical，未调 LLM、未读 Gold/Layer E、未改 B0 | 新增 15 项 S2.8A 测试 + 既有 H1/prompt 31 项全绿 + 全量检查 |
| 3.4.5 | 2026-07-31 | G0.8 受控文本哈希可移植性：合同显式声明 `source_manifest.hash_mode=canonical_lf_utf8_text`，S2.1-D gate 只对声明资产做 CRLF→LF 归一化验证，`formal_experiment/.gitattributes` 仅固定该资产为 `text eol=lf`；修复 Windows `core.autocrlf=true` 下 source_manifest 哈希误报，integrity/sun_modality/human-review-input 门禁恢复 true，未放宽任何许可/formal 边界 | 新增受控文本哈希策略测试 18 项 + modality/audit 相关套件全绿 + 全量检查 |
| 3.4.3 | 2026-07-16 | 建立 `formal_experiment/` 首个可追踪 Git checkpoint `bfb0b8a`，并在既有 `paper/README.md` 中固定外部 ChatGPT 的 GitHub 读取、新鲜度回报和论文主张门禁；未新增平行 status/handoff | Event 40、930 项离线测试、提交后机器检查的 `formal_capsule_versioned` pass |
| 3.4.2 | 2026-07-16 | S2.3 离线重建并锁定 `public_marker_lexicon_en_v1`：64 个显式 public seed、逐类版本化资源、来源/生成/payload hash、空 dev 扩展表和独立机器门禁；保持 development-only，未进入 S2.4/S2.5 | S2.3 source snapshot、manifest、fixtures、负测试与全量检查 |
| 3.4.1 | 2026-07-16 | S2.1-D 完成可移植 manifest 与独立 development 数据门禁；S2.1 整体 verified，旧 modality 未摄入 blocker 改为精确 route-relock blocker；许可/formal/Gold/Stage 3 门禁保持关闭 | S2.1-D gate、负测试与全量审计 |
| 3.4.0 | 2026-07-15 | 在不改变 Stage 2→Stage 1→Stage 3 实验顺序的前提下启动论文并行轨道；增加 PW0–PW9、Agent 分阶段派工和主张证据门禁 | 导师要求现在开始写论文；用户要求按 Pipeline 给 Agent 稳步派工 |
| 3.3.0 | 2026-07-15 | 建立 `_retired/` 专属归档、中文目录地图与逐文件目录；活动日志改为中文 `EXPERIMENT_LOG` + 原样保留的机器事件；Agent 入口和自动检查同步固定 | 用户要求彻底整理目录并让日志同时可供人和 Agent 阅读 |
| 3.2.0 | 2026-07-15 | 治理语义改为“实验日志为主、自动完整性检查为辅、正式复核只在里程碑”；真实运行增加结构化日志字段；精确状态测试凭证消除重复全测 | 用户要求判断审计与日志何者适合普通论文实验 |
| 3.1.1 | 2026-07-14 | P0 完成：全量检查通过并记录 Event 27；主线转入 P1/S2.1 | `record_change.py` 的已验证结果 |
| 3.1.0 | 2026-07-14 | 固定各阶段最低 baseline 覆盖；增加前人数据/结果的 C1-C4 比较证据等级，禁止跨数据和跨阶段误比 | 用户要求多 baseline、复用公开数据并澄清第二/三阶段比较 |
| 3.0.0 | 2026-07-14 | 扩展为完整三阶段重建；Stage 2 优先，多 baseline 与复杂数据；Stage 3 后续扩展；建立 WBS、依赖、DoD 与 Agent 协议 | 用户根据导师要求明确指示 |
# S3-TABLE3-V4-R2 status (2026-09-25)

Subtask `S3-TABLE3-V4-R2` corrects the confirmed R1 protocol deviations without changing the frozen five rules, 20 BPMN cases, reference, thresholds, Stage-2 prompt, or canonical predictions.

- Strict common projection: `src/bpc_hybrid/sun_stage3/temporal_projection_v3.py`, `sun_stage3_temporal_projection_v3@1.0.0`.
- Failure-record separation: no order relation vs projection range/ambiguity/syntax vs endpoint unmapped vs endpoint similarity below gamma vs reachability satisfied/violated.
- Offline R2 output: `outputs/development/stage3_table3_v4_r2/`; independent report: `outputs/reports/stage3_table3_v4_r2.{json,md,manifest.json}`.
- Cause localization: `outputs/reports/stage3_table3_v4_r2_cause_analysis.{json,md}`; corrected candidates: `outputs/reports/stage3_temporal_scope_candidates_r2.{json,md}`.
- New real API calls: 0 (reused `stage3_v4_d1_frozen_v1`).
- Acceptance: `needs_method_review`; the three-method order class remains unobservable (all denominators zero). This is a corrected diagnostic, not final Table 3 completion.

# S3-TABLE3-V4-R1 status (2026-09-24)

Subtask `S3-TABLE3-V4-R1` is implemented and executed on the frozen scoped GDPR construction benchmark.

- Table 3 data: 5 GDPR obligations, 20 BPMN cases, 50 evaluable cells and 300 signals per method; 900 signals total.
- Methods: Sun (frozen Rules-Only + shared Sun Stage 3), Ours (real Direct-LLM v6 extraction + same shared Sun Stage 3), Winter (native paragraph/model/pair pipeline with R1 global role candidates).
- Acceptance: `needs_method_review`, because all three methods have zero observable order relations. The three-method comparison is real and traceable but is not a complete GDPR end-to-end result and not an order-capability result.
- Outputs: `outputs/development/stage3_table3_v4_r1/`, `outputs/reports/stage3_table3_v4_r1.{json,md,manifest.json}`, `outputs/reports/experiment_tables_delivery_v2.json`.
- Future order work: natural-after source candidates (Article14(3)(a), Article33(2), Article43(1)) are inventoried only and require a new, independently authorised benchmark; they were not added to the current 50 cells and no API was used for them.
