# 项目实时状态（兼容文件名 PROJECT_AUDIT.md）

**更新时间**：2026-10-07
**唯一活动目录**：`formal_experiment/`  
**完整路线**：`docs/MASTER_PIPELINE.md`  
**机器事实源**：`python formal_experiment/scripts/audit_project.py`（自动完整性检查）  
**执行制度**：实验日志为主、自动检查为辅、正式复核只在阶段冻结/最终运行/投稿前

本文是唯一实时状态页，只记录“现在做到哪里、下一步做什么”。研究目标、完整
Stage 1/2/3 工作分解、依赖和完成定义不在这里重复，统一见主 Pipeline。

## 默认max_tokens完整150次已验证，GitHub备份受阻：S2-THINKING-SENSITIVITY-V1（2026-10-07）

- 用户明确授权“思考模式跑150条试一下，默认maxtoken即可”，并明确批准150条法规
  文本及现有提示词向DeepSeek官方API外发。原v6/high、实际省略max_tokens（默认65536），
  此前两次单例独立保留。新关闭组/Sun调用0，不读.env、不发Gold或改固定主表。
- 完整run `thinking_default_20261007_v2_remaining_v1`：150个唯一尝试、149有效JSON、
  1条estg_000313余额并发429计为空预测，0重试、0生成额度截断。先12并发完成105并
  排空，随后5并发仅补45个未发送ID；原105完整字节继承，45条续跑全部自然stop。
- 报告 `outputs/reports/s2_thinking_thinking_default_20261007_v2_remaining_v1.{json,md}`；
  完整账本/原始响应含思考/预测/四臂评价/manifest在该run ID evidence目录。预测全保存后
  共享Gold离线评价：high F1=0.8117073948，历史0813关闭0.8224493117，差-1.0742百分点。
  原主表关闭0.8377685388和Sun0.7630963922保持；modality独立，不混入五字段pooled F1。
- actor/action/condition/exception字段F1上升，constraint 0.7578→0.6892，未匹配抽取
  68→117，整体precision下降、recall提高。同一失败ID置空的关闭诊断F1=0.8188302425，
  思考仍低0.7123百分点；此人为离线诊断不替换历史实际结果或主指标，不改Gold/旧预测。
- 149条已知usage：平均思考17426.22、答案835.17、生成18261.40 tokens；生成总量
  2720948相对历史关闭150条122251为22.257倍，约95.43%用于思考，p90生成29120、
  最大40208。返回缓存后闲时费用估算USD5.700214036/峰价USD11.400428072，未查实扣。
  那条429无usage，硬预算仍保守预留，不能认定免费。总壁钟约53.66分钟含停批与准备。
- 四项新产物验证：首次3通过、1失败（6.03秒）；唯一失败为新绑定的既有approval_review
  文件Git检出CRLF/LF。只补该精确路径LF规则，不改冻结源字节/plan/manifest/数值；
  失败事件保留，仅失败节点重跑1通过（5.57秒）。其余三项证据复用，快速完整性通过，
  非全量，未重跑API。完整experiment_run和修正change已记录，原三项用户修改字节未动。
- 本地运行/结果验真完成；GitHub原始产物push曾被自动审批拒绝（具体产物外发许可不足）。
  已询问本150条响应含思考、抽取、评价、账本和manifest向既有chaos-66/LLM4BPC备份，
  尚待回复，远端交付未完成；详情在 `outputs/reports/s2_thinking_default_20261007_v2_git_backup_review.json`。
  原105局部结果commit `6c2dd45`、续跑准备 `b1ad1a7` 和开始checkpoint `2c8f432`均保留；
  最终本地hash在本次交付报告明确，不冒称远端备份，不绕过自动审批。
- 本轮结果为固定150条、一次历史跨批敏感性对照，当前alias与历史0813仍可能有服务变化，
  生成额度不同、thinking的temperature不生效；本次主F1未改善，不推断一般思考模式效果。
  不扩大到low/多重复/独立未见测试、Rules+LLM、Stage3或全量套件。

## 已完成的单例 high 诊断（2026-10-06）

- 用户要求“给定一条数据特例，不设限制，看需要多少token”，新授权恰1次、0重试，
  同一estg_000002，原v6/high保持，仅max_tokens改为服务最大393216（不是无限；省略默认64Ki）。
  单次最大峰价估算约USD1.57，已运行前说明，无额外美元停止条件。
- run ID `high_provider_max_estg000002_20261006_v1`，入口
  `scripts/run_s2_thinking_single_high_v1.py`，独立授权
  `configs/authorization/s2_thinking_single_high_provider_max_20261006_v1.json`。
  准备4项离线核对（0.42秒）及快速完整性通过，checkpoint `9ddabd1` 已远端核验。
- 已恰1次、0重试，HTTP200/stop且最终JSON共享canonical校验通过：输入4446，
  思考13582/答案984/生成14566，含输入19012 tokens，159.29秒。
  报告 `outputs/reports/s2_thinking_single_high_provider_max_20261006_v1.{json,md}`；
  峰价无缓存USD0.06355008，返回缓存后峰价USD0.057996928/闲时USD0.028998464（估算）。
  已通过4项新的具名产物验证（1.72秒）及快速完整性，非全量；结果checkpoint按
  根AGENTS.md要求普通push，最终交付报告附远端核验哈希。不把单例当150条完成。
- 本次生成14566<16384，旧截断只表明旧轨迹用尽上限；不能认定该条固定需要>16K
  或low是必要条件。两次轨迹可变且上限不同，不能只归因随机性，不推断最小预算或分布。
- 首次API执行自动审批拒绝（进程未创建、新调用0）；核查一般规范文本无具体纳税人/
  申报数据后，同一原命令以新增低风险事实复核通过。初次拦截及解决证据均保留于
  `outputs/reports/s2_thinking_single_high_provider_max_20261006_v1_approval_review.json`。
- 本次不批准low批次、不恢复原150条；既有16K截断证据、关闭组/Sun和固定主表保留。

## 原150批次首条截断后停止，恢复方案未批准（2026-10-06）

- 用户已明确授权只新跑开启思考150条；原关闭组与Sun新调用均为0。
- 入口 `scripts/run_s2_thinking_sensitivity_v1.py`；run ID `thinking_on_20261006_v1`。
  原版v6、同一冻结EStG-150、thinking enabled/high、16384生成token/条、0重试、最多6并发。
  首条属于150条，验证响应契约后继续；真实请求只使用已有进程密钥，不读.env。
- 零API预检及9项具名离线验证已完成（10.10秒），快速完整性通过，非全量。
  最大token高峰无缓存估算USD11.4795，保护上限USD15；准备checkpoint `3964c6c`
  已普通push并核验远端一致，分支 `codex/s2-prompt-simplification-v1`。
- 已真实调用1条，0重试；HTTP200，reasoning_tokens=16384，finish_reason=length，
  最终答案为空，耗时182.661秒。程序停批，剩余149条未发；指标null，DoD未完成。
  峰价估算USD0.07074936，闲时USD0.03537468；原始响应/用量/账本/partial manifest已保存。
- 恢复预检 `outputs/reports/s2_thinking_recovery_preflight_v2.json` 尚未授权、未执行：
  推荐low固定条件完整150条，累计151次（旧失败high调用保留作诊断），建议总保护上限USD15。
  这需要补充批准失败条的一次新调用及推理强度改变；不自行重发、改旧授权或冒称完成。
- 持久证据3项检查通过（0.42秒），Git检出字节1项检查通过（2.19秒）；快速完整性通过。
  精确行尾规则保护已有SHA，未改Gold/输入/旧预测/代码字节；非全量，首次缓存差异失败留痕。
- 主表关闭R3/Sun保留0.8378/0.7631；另复用既有0813关闭0.8224493117作版本参照。
  R3早于当前0813，跨批/版本与生成预算差异明确披露，不作纯模式因果或稳定性结论。
  不替换固定表一/表二，不改旧数据、用户未提交修改或其他任务状态。

## 已完成、核验并远端备份：A/B 300 次（2026-10-06）

- 实际新调用恰300次（A/B各150）、原版新调用0、0重试；300条返回均stop，
  缺失用量0，中止0，评价失败0/0/0。API耗时361.125秒，原版150条复用历史结果。
- 固定coarse五字段pooled主F1：原版0.8224493117、A 0.8218192829（-0.06个百分点）、
  B 0.8210327164（-0.14个百分点）。本轮没有主指标收益；不作显著性或稳定性结论。
- A actor F1 0.7083→0.6220，误抽35→50；B actor提高到0.7750、action到0.9329，
  constraint下降到0.7218、exception到0.6667。B为联合改动，不能隔离单条规则因果。
- 原始无围栏JSON对象：原版107/150、A 7/150、B 6/150；A/B围栏143/144条，
  共享解析器可处理，后处理评价失败0。结构服从与语义抽取效果分别报告。
- 新用量输入1,222,988/输出239,396 tokens；保守高峰无缓存估算USD2.56235232。
  纳入返回缓存用量，高峰估算USD2.186044608、非高峰USD1.093022304；未查询实扣。
  硬预算USD9.76没有用尽，不能将其写为费用。原版/prompt/Gold/旧报告/用户修改未变。
- 报告 `outputs/reports/s2_prompt_simplification_comparison_20261006_v2.{json,md}`；
  完整响应、预测、评价、账本、逐样本变化与原版副本为
  `outputs/evidence/s2_prompt_simplification_v1/comparison_20261006_v2/`，manifest为
  同目录 `run_manifest.json`。4项具名产物检查通过（0.24秒，非全量），涵盖全部
  证据/manifest哈希、300条唯一A/B账本、三臂共享评价重算和原始格式/用量。
  首次tuple/list序列化比较误报已修正，失败日志原样保留，指标未改、无新增调用。
  experiment_run与后续验收change事件均已记录；结果commit `36422f6`，分支
  `codex/s2-prompt-simplification-v1`。用户在具体原始数据/GitHub目的地询问后回复
  “备份”，自动审批已接受该明确授权，非强制push成功；远端HEAD逐字核对为
  `11ba35b39b323c9b84dad602cbd8a9f697df62aa`，包含全部原始响应、账本与派生证据。
  原两次拒绝记录保留为历史，不再是当前blocker；解除与远端核验记录见
  `outputs/reports/s2_prompt_simplification_comparison_20261006_v2_git_backup_resolution.json`。
  本次只备份与更新状态，无新增API、实验重跑或数值修改；无关用户修改未暂存。
- 只读共享Gold评价；固定论文表一0.8378/0.7631、表二与默认prompt不替换。
  实验是单次历史跨批开发性比较，不排除服务端变化，不扩大到Rules+LLM或六家模型。

### 本轮授权、准备与中途检查点（历史事实）

- 用户最新回复“授权，进行数据运行，快点”，批准当前已说明的 A/B 300 次与具体
  英文法规文本/prompt 向 DeepSeek 官方 API 外发；授权文件
  `configs/authorization/s2_prompt_simplification_20261006_v2.json`。不重复索取许可。
- 新批次 `comparison_20261006_v2`，入口 `scripts/run_s2_prompt_simplification_v2.py`。
  A/B 各 150 次、0 重试、USD9.76 硬上限；原版新调用 0，最多并发 6 条。
  新预检 `outputs/reports/s2_prompt_simplification_comparison_20261006_v2_preflight.json`
  已离线生成，包含历史基线/授权/请求/源文件绑定。尚无真实候选指标。
- 只使用已有进程环境中的 DeepSeek key，不读 .env，不发送 Gold；完成具名离线
  门禁与准备 checkpoint 后立即执行。历史跨批比较、共享评价和完整分母保持。
  准备阶段实际 API=0 是启动前事实；9 项具名离线测试通过（8.15 秒，非全量），批次快速完整性
  通过。复用原版在共享口径下 F1=0.8224493117、失败0；新效果须待实际运行。
  准备 commit `b8c2774` 已推送并核对远端；自动审批在收到用户明确外发授权后
  已允许实际命令，现已运行。此状态检查点响应完成 84/300（A/B 各42）、中止原因
  null、缺失用量0，按高峰无缓存估算累计 USD0.72559608；数值随账本继续增加。
  当前候选性能仍 null，完成300响应后再统一评价，不把过程统计当完整实验效果。

### 历史范围纠正记录（外发待确认状态已由上述最新授权取代）

- 用户指出原版已有结果，不应重跑。当前拟运行同一 EStG-150 上 A、B 各一次，
  共 300 次新调用、原版新调用 0。旧 450 次范围与 USD14.77 不再作为当前批次。
- 已核对历史 `D-full-0813/repeat-01` 原版：相同 prompt 哈希/输入 ID，150/150
  完整请求配方指纹和响应指纹吻合，历史返回别名均为 deepseek-v4-pro。复用基线
  是跨批比较，不声称本轮同期三臂或排除服务端变化，也不替换固定论文表一/表二。
- 历史原版 150 次记录估算 USD1.35147804；两版 300 次参考约 USD2.70。
  原保守预算公式重算为 USD9.76（输入 cap 2,469,549；输出 cap 1,228,800），
  是最大 token/高峰无缓存及余量口径，不是预计实扣。当前实际调用与费用仍为 0。
- 本次只保存文字说明与范围/费用核对，未修改候选或可执行代码。新批执行器与
  预检仍待按 300 次/历史基线重新绑定；具体数据向 DeepSeek 官方 API 外发的
  明确确认未收到。旧命令不适用，不绕过旧自动审批拒绝。
- 详细区别与风险：`prompts/sun_compat/simplification_v1/COMPARISON_EXPLAINED_ZH.md`。

### 历史事实：旧 450 次执行准备及外发审批拦截（已被范围纠正取代）

- 用户本轮明确授权 prompt 实验对照；固定同一 EStG-150、DeepSeek-V4-Pro-0813，
  v6/A/B 各一次，最多 450 次、0 重试，USD 14.77 硬上限。预检已生成，源文件、
  请求字节、预算及本轮授权绑定；新性能指标仍为 null。
- 入口 `scripts/run_s2_prompt_simplification_v1.py`；唯一批次 `comparison_20261006_v1`。
  只使用进程已有密钥，不读取 `.env`；本轮授权不扩展到六家新模型或 Rules+LLM。
- 共享原后处理（显式 legacy policy）和五字段 pooled 评价，原始 JSON 合规率及用量
  另列；保存逐样本字段变化。先锁定执行准备并做具名门禁检查，再启动真实调用。
- 执行准备检查已通过：7 项具名离线检查，2.46 秒，非全量；批次快速完整性为 true。
  请求配方/哈希、未授权不加载凭据、源绑定失效、中断/完成/中止不重发和调用上限
  均已检查；此时真实 API=0，不能把程序检查当抽取效果证明。
- 输入、Gold、候选、历史结果和已有用户修改保留；固定论文表一/表二不替换。
  完整预检：`outputs/reports/s2_prompt_simplification_comparison_20261006_v1_preflight.json`。
- 2026-10-06 实际启动命令被自动审批拒绝，程序未启动，真实调用仍为 0；没有响应、
  调用账本或执行 summary。拒绝原因是实验目标已授权，但具体 EStG-150 英文文本
  与 v6/A/B prompt 向 DeepSeek 官方 API 的外发未明确批准。已向用户提出完整目的地/
  450 次/0 重试/USD14.77 确认，不绕过拦截或间接执行。审批证据及待确认范围见
  `outputs/reports/s2_prompt_simplification_comparison_20261006_v1_execution_blocker.json`。

## 续跑中、Kimi节流准备通过：S2-MODEL-SENSITIVITY-V1（2026-10-07）

- GLM/MiMo充值后149条正常继续；Kimi前三条新响应均通过约定，第四次HTTP429
  明确账号max RPM:3，保留失败不重发，145项未发送。原首条仍离线恢复有效。
- 新 `kimi_rpm_remaining_20261007_v1` 只跑剩余145项，21秒最小开始间隔、65秒父
  冷却，原900总额和0重试不变；父源/账本/预测不改。三家合并验收仍待最终运行。
- 6项新节流具名离线测试通过（79.23秒），快速完整性通过；未跑全量，未重复旧验证。
- GitHub原始产物外发许可未答复，push阻塞，本地checkpoint不等于远端备份。

## 已授权续跑准备历史：S2-MODEL-SENSITIVITY-V1（2026-10-07）

- GLM/MiMo用户已充值；Kimi用户明确接受关闭请求、空思考正文且实际1 reasoning token
  的计数差异。仅Kimi此例外，超过1或出现思考正文仍停止；不解释为占位或归零。
- `multi_model_remaining_20261007_v1`：三家各149个从未发送项，447新次、继承453、
  合计不超过900、0重试，剩余预算不增。Kimi原首条离线恢复有效、不重发；另外两家
  原余额失败保留150分母。父453份请求和产物原样保留，旧严格报告不覆盖。
- 新入口/授权具名测试13项通过（132.50秒），结束快速完整性通过，真实API=0；
  只验证新续跑范围，原验证证据复用，未跑全量。实测及最终数据验收待本次运行。
- GitHub原始产物外发许可仍待答复，push阻塞；本地checkpoint不能声称远端备份完成。

## 部分实测历史：S2-MODEL-SENSITIVITY-V1（2026-10-07；原453次批次）

- 批次 `multi_model_all_20261007_v2`，实际453/900次、0重试、用时1572.297秒。
  Qwen/Grok/MiniMax各完成150条，结构有效148/147/142；失败2/3/8保留完整分母。
  主指标为共享coarse五字段pooled F1：**0.8030 / 0.7723 / 0.7345**，modality单列。
  历史DeepSeek0.8378/Sun本地Rules-Only0.7631复核一致，未重跑或改固定表一。
- MiMo首条HTTP402/insufficient_balance；GLM首条HTTP429/code1113余额不足或
  无资源包；二者待用户充值。Kimi关闭参数下无思考正文，但返回reasoning_tokens=1，
  按严格门禁停批，不把它擅自当占位符或断言实际思考。三家各1次，性能null；
  447条尚未发送，不自动重试、改型号或放宽关闭思考条件。
- 结果 `outputs/reports/stage2_multi_model_all_20261007_v2.json/.md`，详细可读数据
  为同目录 `_analysis.md`；源、原始响应、账本、预测和共享评价绑定于全批manifest。
  `outputs/evidence/stage2_multi_model_sensitivity_v1/multi_model_all_20261007_v2/index.json`
  保存497份产物的字节相同本地副本映射；本地总498文件约30.23MB，尚未外发GitHub。
- 已报告输入2,019,480/output284,388 tokens；MiMo/GLM缺少usage，0仅表示未报告。
  国内保守估算含异常预留CNY14.3221826、Grok USD1.07430625，未核对账户实扣。
- 准备58项相关测试证据复用；真实产物6项具名离线复核通过（4.08秒）及结束
  完整性检查通过，experiment_run已追加。未跑全量；六家全量DoD仍为partial。
  三家新F1相差6.86个百分点，MiniMax低于Rules-Only；保留负结果，不改Gold追分。
  原始响应GitHub外发此前被自动审批拒绝，许可仍待答复，本批不绕过当前push阻塞。

## 已授权、执行准备历史：S2-MODEL-SENSITIVITY-V1 六家各150条（2026-10-07）

- 用户追加“全部跑出来看一下数据”：六家已确认非思考配置，各跑同一冻结150条一次，
  新调用上限900、每provider/sample一次、0重试、输出4096/条。唯一批次
  `multi_model_all_20261007_v2`，新入口 `scripts/run_stage2_multi_model_all_v1.py`。
- 全批授权文件 `configs/authorization/stage2_multi_model_all_20261007_v1.json`，六个
  单平台计划/授权独立哈希绑定；六家并行、每家顺序，共享既有非思考runner与停止规则。
  价格核对后设置国内五家CNY184.26和Grok USD6.16保护上限，非实际费用或用户指定金额。
- 先具名离线门禁与scoped准备checkpoint，再执行已授权批次。预测全部保存后才使用
  Gold进行共享五字段pooled评价，失败保留、未完成平台性能null；固定表一/表二与
  历史DeepSeek/Sun不改、不新增其调用。准备时真实API=0，实测进度以本批账本为准。
- 原始实验产物GitHub外发许可仍待回复，当前分支此前未推送提交保留，本批不绕过。
- 初次v1离线编排测试180秒超时，真实API=0；事件与预检保留。诊断为每条账本
  重复编码完整计划；v2在每次执行/读取账本计算一次冻结计划哈希，逐请求/响应/链
  校验不变，仅复验共同runner及编排具名测试，不启动全量。
- v2离线预检已通过：58项具名测试（44.97秒）与结束完整性检查均通过；模拟900次
  检查覆盖完整分母、结构失败保留、保存后Gold、已完成续跑零发送及单平台异常隔离。

## 已准备：S2-MODEL-API-SETUP 六家统一关闭思考（2026-10-07；零真实 API）

- 用户要求所有思考模式关闭，不能关闭则换同平台最新支持关闭的型号。按官方文档
  替换 Grok 4.7→4.3（reasoning_effort=none）、Kimi K2.7 Code→K2.6、GLM 5.3 Flash→5.2；
  后两者显式 thinking.type=disabled。Qwen 3.8 Max 0902、MiMo v2.6 Pro、MiniMax M3
  保留且显式关闭思考。六项 key/端点、4096 输出、180 秒和 0 重试不变。
- 目录/计划/manifest 固定 thinking_requirement=disabled；离线拒绝开启、省略开关或
  low 等冲突设置。返回思考内容、前置 think 块或非零思考用量则保存失败并停批，
  不剥掉思考后冒称关闭；缺少思考用量明细保留 null。所有旧预检因绑定变化不适用。
- 用户单独明确覆盖旧禁读规则后，本次私有检查六项均已填写，未发现空白、占位符
  或重复冲突；未显示密钥值、未修改 `.env`、未调用模型。该例外仅为本次状态检查，
  不能据此宣称 key 有效、账户权限齐备或启动真实 API。
- 本批前后快速完整性检查通过，tests/test_multi_model_stage2.py **51 passed / 4.33 秒**
  （非全量），覆盖六家关闭开关、开启/缺失/冲突拒绝、返回思考停批、授权与安全续跑。
  离线 list 六家均显示 thinking=disabled；真实 API=0，实际 `.env` 未读未改。
  未来须新预检及独立调用授权；账户权限未实测。当前分支此前原始产物 GitHub
  外发许可仍待回复，本批 scoped 本地提交不能冒称已远端备份。
- 初次准备时，千问、MiMo、Kimi、Grok、GLM、MiniMax 六个独立密钥项只追加到实际 `.env`，
  未读取或打印原有内容，文件被 Git 忽略。填写不会授权联网；未来只有本批计划、
  用户明确决定、调用/输出/核对单价/费用预算及 `--execute --allow-llm` 均通过才读 key。
- 程序 `scripts/stage2_multi_model.py`；配置 `configs/models/stage2_multi_model_v1.json`；
  填写/授权/结果与续跑说明 `docs/STAGE2_MULTI_MODEL_API_GUIDE.md`。默认 list/plan
  离线；原始响应脱敏保存，持久化账本，0 自动重试；不确定调用须人工核查。
- 实现准备 DoD：前后快速检查通过，**33 passed** 具名模拟测试（非全量）；第一次
  测试定位的 v6 示例插槽遗漏已修正，失败事件保留。真实 key 未测试、各家账户
  权限未实测，API 调用 0，无 F1/性能结论。
- 已生成本地预检 `model_preflight_20261005_v1`：6×20=120 次计划调用，授权 false，
  价格和费用上限未填写，metrics=null。这是离线准备，未来仍需明确批准具体批次。
- 本轮不改原 prompt、DeepSeek 正式臂、Gold、评价器、固定表一/表二；不运行
  Rules+LLM。后续真实 API 与模型敏感性补充实验待授权，其他主线状态保留。

## 已准备：SEP-C3-PROMPT-SIMPLIFY-V1 独立精简候选（2026-10-05；未实测）

- 用户授权在分支 `codex/s2-prompt-simplification-v1` 尝试精简，保留已有结果。
  A 压缩 J 的重复合同/格式指令；B 加上 S 压缩及 `unless` 分类、action 边界优先级
  修正。System 字符数 6172 → 5676/4398，缩短 8.0%/28.7%；六个示例及用户模板不改。
- 候选与静态设计说明：`prompts/sun_compat/simplification_v1/`；机器清单/范围：
  `outputs/reports/s2_prompt_simplification_v1.json`。真实调用 0、指标 null，尚未验证
  语义抽取收益，不替换默认 prompt 或固定表一/表二结果。
- 历史保留：`outputs/evidence/s2_prompt_simplification_v1/baseline_snapshot.json`
  保存来源提交的 15 个 prompt/结果报告/配置 Git blob，附原始文本、字节数及 SHA-256。
  已有用户数据/两份本地 modular 报告修改不覆盖、不纳入本次提交；该报告快照不等于
  所有未版本化 raw/prediction 运行材料已远端备份。
- runner 增加显式候选选项，须 development 且输出/manifest 在独立候选目录；
  原默认、拒绝覆盖、API 授权与现有 canonical 校验保留。批次前后快速完整性检查
  通过，具名离线检查 **19 passed**（非全量）；16 个原文件/用户修改的启动时哈希
  均未变化。已登记变更事件，不宣称性能验证。后续实测须新预检、调用预算与明确
  授权，不复用旧额度。新候选/证据目录仅针对自身固定 LF 检出，保证哈希可复核。
- 本子任务是 SEP-C3 下的离线候选准备，不改变原 Stage 3/命名迁移未完成状态。
- 2026-10-05 补充用户要求的逐项依据：`simplification_v1/RATIONALE.md` 对照 J 的
  合同引用、规则 1–5/24，以及 B 的规则 9–19/25–27，逐项记录动机、原文/代码/
  既有结果依据、保留内容和信息损失。明确 A 字段清单隐式化及 B 触发词减少、
  语义修正不属于全部无损删重；本次只补说明，不改候选/运行代码/旧证据，不重跑
  实验或测试，采用文档内容与原文件哈希核验及 scoped Git commit 记录。

## 进行中：LLM4BPC 全部命名迁移（2026-09-29 用户追加）

- 用户追加范围包括当前代码与配置、历史记录、冻结 manifest、归档和参考目录；
  原始证据须另存副本。此决定覆盖下方第一轮“保留旧导入/目录名”的范围选择，
  不增加 API、实验重跑、Gold 改写或全量测试授权。
- `LLM4BPC-RENAME-WORKTREES` 已完成：4 个 Codex worktree 目录和外部 Stage 3
  worktree 目录已统一新名称，对应 Git 管理目录同步；HEAD、索引和未提交内容不变。
- 已精确迁移 Codex 本地数据库中 204 行相关路径字段及 UI 工作路径，未修改聊天
  正文。原始路径记录、UI 状态和数据库改动前字段保存在
  `formal_experiment/.tmp/llm4bpc_rename/worktree_names_20260929_184857/`。
- `LLM4BPC-RENAME-BACKUP`：1,073 个受影响文件的原始字节与逐项 SHA-256 已备份
  并核验，原始数据 67,100,040 字节、计划涉及 157 个路径。长期本地副本位于
  `_retired/name_migration_originals_20260929/`；摘要在
  `outputs/reports/llm4bpc_name_migration_v1.json`。无 Gold 文件、既有用户修改或
  测试凭证进入迁移计划；原始 ZIP 包含本地/参考材料，明确不上传。
- 余项：代码包与环境变量入口迁移、历史/归档名称迁移、
  依赖绑定核对与相关验证。当前尚未声称全部内容已完成改名。

## 已完成：LLM4BPC 项目改名兼容维护（2026-09-29）

- `LLM4BPC-RENAME`：当前根目录为 `D:\Paper\experiment\LLM4BPC`，GitHub 远端
  `https://github.com/chaos-66/LLM4BPC.git` 已可访问，当前分支上游配置正确。
- 修复 12 个关联 worktree 的旧主目录链接，其中 7 个嵌套 worktree 的登记路径
  随根目录同步；全部可执行 Git status，HEAD、索引和原未提交状态保持不变。
  本地链接备份在 `formal_experiment/.tmp/llm4bpc_rename/`（仓库根目录相对路径）。
- 活动 README、Pipeline 标题、派工入口与论文标题统一为 LLM4BPC；发行包名称
  为 `llm4bpc-formal`，健康检查返回 `LLM4BPC`；清除无效的旧 CI 占位路径。
  兼容模块 `bpc_hybrid`、环境变量、冻结 schema、历史记录和实验产物保持原样。
- 验证：批次前后快速完整性检查通过；`tests/test_smoke.py` 1 passed；包元数据、
  兼容导入和根目录解析通过。目录索引补入 35 个既有版本化文件，重新生成并
  `--check` 通过；原有 3 个未跟踪文件的索引条目未扩增，其内容不纳入本次提交。
- 本项仅维护项目名称、路径和工程入口，不改变研究任务完成状态或表一固定数值；
  无真实 LLM/API、Gold 修改、实验重跑或全量测试。已有用户修改保持独立。

## 已完成：Stage 2 论文主表数值复核与最终采用（2026-09-26）

- 用户决定：第二阶段 Table 1 固定采用 Direct-LLM **0.8378** 与 Sun 方法本地
  重建 Rules-Only **0.7631**，Overall F1 差 **+7.47 个百分点**，后续不再替换。
- 唯一数值源：`outputs/reports/stage2_table1_paper_final_v1.json`，来源提交
  `87b5280e7d6be3718270290a1b380180c432b289`。同一 EStG-150、459 个粗 Gold span；
  五字段 pooled 主口径，modality label 单列；mean F1 0.8088/0.7970 为次口径。
- 本轮验证：既有报告计数的 P/R/F1 算术、Gold 与两臂预测的三项 SHA-256 绑定、
  正式 arm manifests 和历史口径修正事件核对一致；两个方法均覆盖 150 条。
  原始精确值 0.8377685388362014/0.7630963921754044，四位舍入无误。
- 方法绑定原 `direct_llm_formal_arm_v1`（v6/R3）与 `b0_formal_arm_v1`。
  后续消融、actor refinement 或 100 单模块候选不替换本表，不再为此表调参、
  重跑或改变口径。0.7631 是本地基线评测值，不是 Sun 原论文报告值。
- 完成本轮纯文档固定；未修改代码、配置、Gold、预测、评价报告或 manifest，
  无新实验/API/代码测试。验证范围不等于新增全量测试或 Stage 3 正式放行。
  写作证据入口为 `paper/CLAIM_EVIDENCE_MATRIX.md` C54、论文 §7.2。

## 当前优先级：S3-TABLE3-R5.1 定向纠错与 benchmark v2（2026-09-25）

- 状态：DATA_READY_FOR_FROZEN_SCOPE / METHODS_NOT_READY / API_AUTHORIZATION_PENDING / FORMAL_RELEASE_NOT_APPROVED。不是正式 Gold，不宣称表三成绩。
- 边界：真实 LLM/API 调用 0，未读 .env，未跑新增测试集 Stage2/Stage3 主矩阵，未做参数搜索；Sun/Ours/Winter 公式、相似度后端与阈值未改；旧预测/原始回答/旧 Gold/R1—R4 结果未改；R5 v1 数据/配置/报告保留。
- A：为 36 条要求生成逐条处置表 data/development/stage3_table3_r5_benchmark_v2/requirement_disposition.json。has_variants 全有或全无改为逐类型资格。
- 定位项：A1 S1-T1/T2 同时性不再当顺序；A2 S6-T1 风险适当性不是顺序；A3 S6-T4 撤销评估到告知 order；A4 S2-T3/T4（及同一规则下 S2-T1）permission 移出核心评分；A5 S3-T3/T4 删除虚构 Stop/Cease 并移出核心；A6 S4-T3 摘录收窄到 28(3)(a) 句并记录 char span 与 processed source 标注。
- B：source_family_id 按 Article 建族，family_id 不再等于 requirement_id；Art 13/14/35/36/33 跨集合问题消除；R1—R4 五条与已暴露条款族留 development；无 family 跨 split。修正后：36 条要求、31 条核心、5 条候选；105 核心案例；dev/test = 22/14；21 个来源族。
- C：六要素逐项绑定实际输入证据或声明外部上下文，source/context/SHA 分开记录；修正遗漏 condition；跨条款 exception 文本实际提供或标记 counts_as_in_input=false；condition/exception 分开建模、挑战 BPMN 中性且无悬空节点、例外成立=义务豁免。
- D：修正 scripts/prepare_stage3_table3_r5_execution.py 的复用判断并抽出 scripts/r5_reuse_verification.py；逐条核验。旧 14 条 Ours 预测全部经证据链验证。
- E：v2 请求清单 17 次新 Ours Direct-LLM 调用，14 条复用；0 重试；输入 token 上限 364949、输出 69632；USD 0.91 上限。5 条候选需求不在本轮请求清单。
- 验收器：scripts/validate_stage3_table3_r5_benchmark_v2.py 结构检查与内容资格审查分开报告；13 个具名反例测试全部通过。结构=pass，内容资格=pass。
- 遗留：METHODS_NOT_READY；condition/exception/prohibition/permission 真值仍 unsupported；核心测试覆盖 9 条/7 族；表三运行仍缺 API 授权。

## 历史优先级：S3-TABLE3-R3-INTEGRATION 接线/表示/后端诊断（2026-09-25）

- 状态：M1、M2 均已完成预先冻结的一轮完整诊断矩阵与独立评价；M0 只读取已保存 R2 结果，不重跑。全部标记 development/retrospective，不是独立测试验证。

- 接线修复：新增 R3 P2 adapter，Sun/Ours 共享同一份模型侧 sidecar；活动使用冻结 P2，命名事件使用同一冻结标签逻辑的 R3 扩展并单独注明。原 Stage3 直接读取完整 activity/event label 的调用链作为历史保留，不被改写。

- 事件投影：新增 `temporal_projection_v4_r3`。article18p3 的 `before` 端点由 R2 的 `the restriction of processing` 修复为 `the restriction of processing is lifted`，保留谓词 `lifted`；v1/v2/v3 及 R2 输出未改。

- M0/M1/M2 overall F1：Sun 0.3429/0.4324/0.4000；Ours 0.3429/0.4000/0.3333；Winter 0.5000/0.5000/0.5000（M1/M2 复用 R2）。

- Coverage：Sun 0.4600/0.6400/0.6400；Ours 0.4600/0.5200/0.5200；Winter 0.7000 不变。

- 后端对照：M1 保持原 sm 相似度；M2 仅将 Sun/Ours 相似度换为 en_core_web_lg 3.8.0 静态词向量均值+cosine，解析、P2、lemma、候选、公式、阈值完全一致。lg 未安装，允许离线下载官方 wheel。

- 资源记录：官方 wheel bytes=400658291，SHA256 `293e9547a655b25499198ab15a525b05b9407a75f10255e405e8c3854329ab63`；解压模型目录 SHA256 `cdfe8653ce0102fdd6bc7df6c8cfe87ee142ff0d10c2ab0ea94f0815f4f97883`；版本 3.8.0，license MIT；未升级/覆盖现有环境，权重/缓存不入 Git，下载耗时约 3051 秒。

- 验证：quick integrity 通过；具名 `tests/test_stage3_r3_integration.py` 8 passed；独立开发样例覆盖主动/被动、before/after/prior to、名词性事件与日期/时长、截断、否定、多个谓词、同对象不同动作、同动作不同对象、重名节点和正反顺序，并保留 1 个 P2 词表限制失败样例。

- 交付：`configs/stage3_table3_r3_m1.json`、`configs/stage3_table3_r3_m2.json`、input contract、P2 sidecars、`outputs/development/stage3_table3_r3_m1/`、`..._m2/`、`outputs/reports/stage3_table3_r3_m1.*`、`..._m2.*`、delivery/wiring/projection/backend-diff/mechanism/resource records。

- 边界：R3 是接线、表示和后端机制诊断，不是最终表三验证；M2 优越性未被预设也未成立。本轮 LLM/API 调用 0，未恢复 Rules+LLM，未改旧 Gold/阈值/分母。


## 当前优先级：S3-TABLE3-V4-R2 纠错与原因定位（2026-09-25）

- R2 已完成：在保留 v4/R1 字节证据的前提下，新增 strict `temporal_projection_v3`、非评分失败原因诊断、精确 case/rule ID 集合校验和独立 R2 评价器；真实 API 新调用为 0，复用 `stage3_v4_d1_frozen_v1`。
- R2 结果仍为 `needs_method_review`：Sun/Ours/Winter 的 `out_of_order` 15 个可评单元全部 unknown，F1=0.0000；Sun/Ours overall P/R/F1 为 0.3000/0.4000/0.3429、coverage 0.4600；Winter 为 0.5385/0.4667/0.5000、coverage 0.7000。结果与 R1 相同，说明本轮纠正了实现偏差但没有把顺序能力从不可观察变为可观察。
- R2 顺序失败原因已分开：Sun 40 个 `projection_rejected_range`、60 个 `endpoint_similarity_below_gamma`；Ours 40 个 `projection_rejected_syntax`、60 个 `endpoint_similarity_below_gamma`；Winter 100 个 `no_rule_order_relation`（均按 20 case×5 rule 的 out_of_order 信号计）。
- 关键 R2 差异：article18p3 不再由额外 advcl/ccomp 扫描选出 `is lifted`，改由限定 nominal 分支得到 `the restriction of processing`；article13p3/14p4 仍无关系，但原因分别落到 Sun range 与 Ours syntax；article35p1/36p1 仍有关系但两端映射没过 gamma。
- 交付：`outputs/development/stage3_table3_v4_r2/`、`outputs/reports/stage3_table3_v4_r2.{json,md,manifest.json}`、`outputs/reports/stage3_table3_v4_r2_cause_analysis.{json,md}`、`outputs/reports/stage3_temporal_scope_candidates_r2.{json,md}`。
- 本轮只纠正确定的实现偏差并定位卡点，**不代表最终表三完成**；三项 after/temporal 候选仍为 `candidate_not_benchmark`，未进入 50 单元，也未申请新增 API 额度。
- 旧 R1/表二判断保留在下方历史段落，不重写旧 manifest、旧期望 SHA 或旧事件。

## 历史优先级：表二解释与正式实验文件备份（2026-09-24）

- 用户最新要求先弄清 000、每条法规独立请求和模块必要性，再统一 Stage2 方法身份。
  只做实验与数据，不写论文；单模块方案仍在考虑，未将 100 替换为正式 Ours。
- 只读核查：000 实际保留任务、原文约束、分句/关系规则及 JSON 模板；J=0 仍有
  格式信息，S=0 仍有基础语义规则。不能把它们解释为完全无 prompt/格式/语义指导。
  E=1 在当次请求显式附带六个固定示例；没有把它们作为跨样本隐藏记忆。
- 八组各 150 条记录的 runner 请求摘要均与独立 system+user 构造匹配；原始回答、
  预测和账本逐项对应，未发现累积历史对话证据。摘要不是完整 HTTP 抓包；独立请求
  也不能保证无幻觉。后处理含结构适配、原文唯一精确定位和无法恢复项删除。
- 已有 pooled 五跨度字段 F1：000=0.7380、010=0.8107、100=0.8354、111=0.8224；
  Modality 独立计算。支持考虑 E-only 简化，不支持全部模块必要或 S 完全无效。
  100 为当前单次比较的候选，不能直接沿用表一原 Ours=0.8378 的数值/方法身份。
- 用户授权补传正式内容。本次保留八组原始回答、预测、账本、评价和 manifest，
  加执行摘要共 49 个既有文件；逐字节备份清单与检查证据见
  `outputs/reports/stage2_table2_evidence_backup_v1.json`。表一两方法正式 capsule 已在
  Git；新文件使用精确路径提交并保留原始字节（含历史 LF/CRLF 差异）。没有重新计分、
  运行实验、改 Gold 或调用 API。
- 不提交本地旧 `sep_c3_modular_ablation_v1` 被替换成 20 次且指标为空的报告，
  也不提交未审核的 v1/v2 构建脚本、PPT、备份和临时文件；均保留用户本地状态。
- Stage3 仍按下一节 R1 待纠错，Ours 五条新输入的预测仍缺失，表三未验收。
  既有五次授权保留；若最终 Stage2 prompt 改变，先对齐方法/请求绑定，不挪用旧授权。

## 历史 Stage3 状态：S3-TABLE3-V4-R1，Codex 复核后退回纠错（2026-09-24）

- 复核对象 2f9dd9f 已推送；保留其诊断证据，**表三未验收**。本轮 Codex 只读
  检查源代码/既有产物、重算 coverage 算术、核对请求序列化及来源，未改实验代码、
  未跑新实验/测试或真实 LLM。下一执行卡 `docs/agent_prompts/STAGE3_TABLE3_V4_R1.md`
  已准备，由用户转交 DeepSeek。
- 已确认机械问题：发送端 ensure_ascii=False 与预检 True 不同，五请求均少 18 bytes，
  补 key 也会 hash 拒绝；coverage 未扣 positive unknown，正确总体应为
  Sun 0.46 / Ours 0 / Winter 0.70（仅既有计数算术，非修复后的新实验分数）。
  Winter 使用当前单角色作为全局候选，资源违例条件不可满足，不能归为基线真实性能。
- manifest 缺推理输出 hash 绑定，evaluator 只自算 hash/信 count；推理 hash loop
  实际读取 construction_reference 字节，与“未打开参考”声明不一致。未发现标签
  实际用于评分的证据，但现有 false 字段不足以证明隔离。投影还存在 nominal
  越出预测 span、of 拼接丢失及 before 补语规则不全的问题。
- 当前会话仅检查环境变量存在性：DEEPSEEK_API_KEY/BPC_HYBRID_LLM_API_KEY 存在，
  未输出值、未读 .env；不据此推断 DeepSeek 历史执行进程的环境。仍须修复 alias
  支持和请求/预算门禁后，由执行 Agent 用原五次授权抽取。官方模型/价格本轮核对
  与预检一致；本轮实际调用仍为 0，不再将“整个项目缺 key”作为唯一 blocker。
- R1 决策：保留现样本与阈值；独立准备无标签全局角色集合、修正共同投影为 v2、
  修正评价/manifest/传输并真正执行 D1，新产物进 stage3_table3_v4_r1，不覆盖旧结果。
  未运行方法主指标 null，旧全 unknown 的算术分数仅诊断。修正后若顺序仍不可观察，
  继续 needs_method_review；自然 after 来源仅整理为后续候选，不自动扩大实验。
- 表一 3/5 span 加 Modality 为 4/6 字段更好，总体 +7.47 pp，符合多数胜、少数负；
  表二所有模块必要仍无证据。没有承诺修正后 Ours 必然最高或三类 F1 必然非极端。

## S3-TABLE3-V4 初版执行回报（历史诊断；当前判断以上节为准）

- 用户明确“只把实验和数据跑出来”，Codex 负责想法与验收，机械工作交现有
  DeepSeek Agent。完整静态执行 prompt 已准备：`docs/agent_prompts/STAGE3_TABLE3_V4.md`。
  用户手动转交后 DeepSeek 已回报实施，提交 2f9dd9f；其验收结论经上节复核修正。
- 已接受共同顺序投影和固定五条新 Direct-LLM 抽取：最多 5 次、0 重试、总输出
  20,480 tokens、上限 $8.02。授权前 preflight 保持不变，执行 Agent 另建当前授权
  记录及防重试账本。该五次无需重新许可；未授权其他调用/全量测试。
- 本轮执行回报：A 实现冻结（temporal projection、无外门槛 checker、独立
  inference/evaluator、config、authorization）；四个 v4 具名测试文件 20 passed。
  B `--check-only` 已验证五条 body/source/preflight/授权绑定，但当前进程环境缺
  `BPC_HYBRID_DeepSeek_API_KEY`/`BPC_HYBRID_LLM_API_KEY`，真实调用按合同停止：
  attempts=0、retry=0、network_calls=0、usage=0、cost=0；未读 `.env`、未搜索凭据。
  C Sun（冻结 B0）与 Winter（原文 native）矩阵完成，Ours 因缺真实 D1 预测显式
  `blocked_missing_d1_predictions`，共 900 信号中 Ours 300 个均为 unknown 诊断。
  D 独立 evaluator 已按固定 50 单元/方法完成，表三报告 `needs_method_review`：
  Sun/Ours/Winter 的极端/不可观察值保留；报告见
  `outputs/reports/stage3_table3_v4.{json,md}`。E 三表索引见
  `outputs/reports/experiment_tables_delivery_v1.json`。
- 初版建议“给进程设置 key 后直接重跑”已被 R1 替代：先纠正实现与输入合同，
  再执行五次已授权调用；不能按旧 --overwrite 命令覆盖诊断。表三尚未验收。
- 表一已支持多数要素较好、pooled 五字段总体 +7.47 pp；表二不支持全部模块必要。
  表三本轮固定五项条文/20 构造流程，参考为 AI development；不是 Sun 原始完整
  端到端实验，顺序表示补充和范围限制必须随数据交付。

## S3-RECONSTRUCT：已有构造与执行准备（2026-09-23/24，当前授权以上节为准）

- 执行准备补充（2026-09-24）：固定五条输入的 B0 零 API 入口及 D1 逐请求预检。
  新增调用计划 5 次、0 重试；代理输入+最大输出估算 $0.113921，按提供商最大
  上下文保守预算上限 $8.02。真实调用 0 次，预算不等于授权；详见
  `outputs/reports/stage3_d1_preflight_v4.md`。新代码只准备/复用既有算法，不修改检测器。
- 冻结 B0 真实运行已完成：`data/predictions/stage3_v4_b0_frozen_v1/manifest.json`，
  五条全部成功、均有义务和时间约束，顺序边全部为空；耗时 22.973 秒、零 API。
  保存的是抽取结果，不是 Table 3。双方共用的时间约束转换已获用户接受，实施规范
  见当前任务卡；原算法和已有预测不改，不用人工动作替换预测。
- BPMN 表示补齐：原生 Winter 读取 process.name，Sun 读取 participant；在首次
  Stage 3 评分前同步两者的执行者名称。来源、参考、成员及 B0 预测不变；此修复
  只解决双方能否看到实际执行者，不声称合规检测因此正确。
- 本批第一次解析器联调发现 Winter 对 `bpmn:` 前缀读成空流程；已将新模型序列化
  为官方原始 BPMN 的默认命名空间。未修改解析算法，失败测试留痕后做针对性复验。
- 已构造五项明确义务的 20 个 BPMN（5 基准 + 每类 5 个违规），AI 来源参考固定
  50 项可评价、10 项不适用。推理视图无目标法规、错误类型或参考流程。
- 范围仅为 13(3)、14(4)、18(3)、35(1)首句、36(1)的条件化 checking，不能当作
  46 篇 GDPR 自动端到端复现。当前按该范围执行并显式交代局限，不发布 Gold。
- 现行 B0 硬编码 `order_relations=[]`，不是新增条文即可解决；共同顺序信息通路
  的方法一致性仍需补齐。未生成或承诺新的 F1，未新增真实 LLM 调用。
- 输入/参考：`data/development/stage3_reconstruction_v4/`；具体协议与差异：
  `outputs/reports/stage3_reconstruction_v4_protocol.md`。

## S3-ASSET-RECOVERY：官方继承资产核对与 Table 3 重新构造（2026-09-23）

- 用户提供纠偏总结，并选择优先补齐三类：补充有明确顺序依据的条文与基准流程；
  新增 LLM 调用先准备精确输入/预算再授权。Stage 1/3 共用，Stage 2 为主要变量。
- 资产审计已完成：本地两个继承副本 57/57 一致，活动 BPMN 7/7 与来源相同；
  57 文件为 7 BPMN + 46 法规 + 4 配置/词表，没有已补充的合规模型、变体或答案。
  官方 ZIP 本轮未重新下载；历史官方身份与本轮本地字节核对分开说明。
- **v3 的零分不再具有论文性能身份**：外层 `matching_score > tau` 在可读作者稿
  中无依据，control 的完整合规性也未确认；v1/v2/v3/no-gate 均保留历史诊断。
  不删除旧结果，不将旧协议分数换名重新发布。
- 已有 matching Gold 25/63；未标的 38 项不作负例。92 个人工 rule clause 无
  规则侧顺序关系，原 Gold 与完成的绑定审核不改、不重开。
- 下一项是新 benchmark 的来源、适用范围、独立 reference、合规基准与单错误
  变体构造；仍未产生最终表三。详见 `outputs/reports/sun_stage3_official_asset_audit_v1.md`。

## Stage 3 Table 3 v3：历史全规则库诊断（性能身份已由上节撤销）

- Implemented `stage3_sun_style_checker` (Definition 4 full Rule Base matching; Def. 5–7 only on associated rules) and blinded v3 inference view/case map (`stage3_sun_style_inference_view_v3.json`, `stage3_sun_style_case_map_v3.json`).
- Ran full pipelines for Winter, Sun, and Ours over the shared 9-rule GDPR Rule Base; predictions were persisted before the separate evaluator read labels.
- Main target-seeded result on 13 eligible single-mutation pairs: Winter P/R/F1 = 0.5000/0.6154/0.5517; Sun = 0.0000/0.0000/0.0000; Ours = 0.0000/0.0000/0.0000. Full-rule-base matching prevented both Sun and Ours from selecting the labeled target rules.
- Matching AP/MAP: Ours 0.4159 MAP / 0.0000 binary recall; Sun 0.3877 / 0.1000; Winter 0.4343 / 1.0000.
- Out-of-order remains N/A (no real rule-side order relation). Complete multi-label control-vs-violation Gold for all nine rules is not available; the all-alarm/strict diagnostics are retained but marked non-publishable.
- Audit report: `outputs/reports/stage3_sun_protocol_realignment_v1.md`; final report: `outputs/reports/stage3_table3_v3_final_report.md`.

## S3-BINDING-RESOLUTION：AI 候选判定完成（2026-09-23）

- 用户授权由 AI 直接处理候选，30 项均已落定，没有新人工待审项。
  结果 `data/development/stage3_synth/stage3_binding_resolved_reference_v1.json`，
  `ai_resolution_complete`、`is_gold=false`；说明沿用
  `outputs/reports/stage3_binding_reference_assessment_v1.md`。
- 保留 25 个 action 和 22 个 actor 的人工选择。5 个空 action 已明确原因；8 个 actor
  缺口中 7 项补充 Controller 相对执行者推断、1 项只确认流程执行者。10 项顺序判为
  仅流程关系：4 项缺严格顺序依据、2 项同一动作、4 项缺端点。不新增原 Gold ID。
- 原人工文件、Gold、benchmark 均未改。按用户明确请求查阅归档候选的指定成员，
  未恢复旧批次、未生成新审核工具；AI 结论不冒充人工批准或正式 Gold。
- supplied-binding 检查器已定位为 oracle；此处参考资料可见的 AI 判定不是自动 Ours
  盲测预测。没有执行真实实验/外部 API；端到端接入与正式评价未因此完成。

## S3-BINDING-REVIEW：人工复核完成、批次已归档（2026-09-23，零 API）

- **完成状态**：用户于 2026-09-22 保存 30/30 项确认，`human_review_complete`；
  这批审核已结束，不再作为待审核任务。
- **唯一活动结果**：`data/development/stage3_synth/stage3_binding_human_decisions_v1.json`，
  与用户保存版本逐字节一致。SHA-256：
  `1434da07946484e7bae95e7af959930d3f154c375df733ae146bbdd54191ce9f`。
- **清理**：50 个过程文件已封存（含 31 份备份），旧启动入口移除；
  默认搜索和文件目录排除归档，后续批次使用独立 ID 与路径。仅明确追溯时查归档清单。
- **结果边界**：30 项均接受；5 个空 action、8 个空 actor 原样保留，
  10 项顺序均为 process-only，`is_gold=false`。本次未发布绑定 Gold，
  未运行检测/评价/API，benchmark 与已有 Gold 未修改。

## SEP-C3 targeted refinement 运行时校验修复（2026-09-19，零 API）

- **修复入口**：`scripts/run_sep_c3_targeted_refinement_v1.py` 的实际响应转换入口 `_prediction_with_provenance`，内部固定顺序为 `convert_refinement_response` → `convert_response_payload`：原始响应已先持久化 → JSON 解析 → 输入身份检查 → 现有 `d1_schema_adapter` → 现有 `d1_span_canonicalizer` → `stage2_canonical.validate_canonical()` → 保存预测与审计。
- **路径版本**：`sep_c3_targeted_refinement_runtime_validation_v1`。manifest、evaluation 和逐条 prediction envelope 记录该版本及 processing status。
- **历史“调用成功”与“接口校验通过”的区别**：旧 A/B/C/D 600-call 运行的 `request_status=ok` / 600 成功只证明 API/transport 调用返回，不证明 payload 与冻结输入绑定、也不证明 adapter/canonicalizer 后的 canonical 校验通过；旧 runner 未把输入身份检查和运行时 `validate_canonical()` 保存为独立状态。不得用旧的 `validation=true` 或“调用成功”替代 `input_binding_pass` 与 `canonical_validation_pass`。
- **输入身份检查**：仅依据冻结 `data/input/estg150_formal_inference_input_v2.json`，要求 payload 为 JSON object、`sample_id ==` 本次输入、`source_id ==` 请求协议要求的 source_id、`source_text` 与实际输入正文逐字相同；检查在 adapter/canonicalizer 前执行。缺失、追加、截断、空白差异均记为 `input_binding_failed`，不自动修正、不截断追加示例、不调用模型修复、不覆盖错误正文。
- **运行时校验**：实际调用现有 `stage2_canonical.validate_canonical()`，保存程序计算结果，模型自报的 `validation` 不决定通过。当前环境没有 `jsonschema`，backend 如实记为 `lightweight`（现有轻量结构检查 + 跨字段检查），不写“完整 JSON Schema 校验通过”。runner provenance 放在输出 envelope，不放进模型 schema 字段，也不删除模型其他未知字段。
- **失败处理**：校验不通过或异常时输出 `request_status=failed`、明确 `failure_stage` / `error` 和空 `record`；保留 `sample_id`、`request_id`、`response_sha256`、`raw_model_output` 及审计信息。失败样本继续保留在每臂 150 条完整分母中，不猜测修正非法 modality，不删除非法关系后宣称合格。
- **旧 600 canonical 只读复核**（内存副本；不重写历史文件、不重新评分）：source_text 不一致 A/B/C/D = 2/0/2/0；现有轻量结构/跨字段校验失败 = 10/9/6/7；两者并集 = 12/9/8/7，共 36 条；与参考计数一致。结构检查仅排除旧 runner 注入的顶层 `provenance`，未删除模型其他字段。
- **边界**：Prompt、候选新增句、R_A、Gold、评价器、默认模型配置均未修改；历史 raw/canonical/manifest/evaluation/分数未覆盖；本轮新增 API=0，不生成新的效果分数。修复路径与旧路径存在关键差异，未来修复路径分数不能与旧路径分数直接作同口径因果比较。

## SEP-C3 R_C 字段边界与 recovery 口径补充复核（2026-09-19，零 API）

- **新增证据**：A→C/B→D 全量 condition Gold 覆盖丢失为 9/10 条，共 19 条比较记录、13 个独立样本；其中 8 条/5 样本出现 condition-only 整段移入 constraint，3 条为已有 Gold 嵌套覆盖，4 条为 condition/constraint 范围合并，4 条没有新增重叠 constraint。19 条覆盖丢失与旧 18 条“字段全对→非全对”口径不同，已逐案对账。
- **recovery 解释再校正**：52 条既有 coarse recovery 中，49 条命中真实细粒度 constraint，37 条至少精确恢复一个细粒度 constraint，3 条仅命中合并空隙（000247 双方向、000293 A→C）。原 partial/overlap-only 中 21 条已有精确短语恢复；旧 `21/29/2` 不能直接作为单个短语完整性或新 Prompt 边界设计依据。旧计分与历史报告保留，不改 Gold 或评价器。
- **设计推进**：识别出“防止适用条件整体改标，同时保留合法嵌套限制”的局部目标；排除 temporal-only、字段绝对互斥、扩展至整个 coarse 区间和笼统短词删除。E5 已有嵌套示例，不能把重复该规则视为已证明有效的新干预。下一步只做一个局部候选的离线正反例审查，先澄清 000052/000104、000106、000776；不启动或自动缩编 API。B 仍为研究参照，正式默认仍为 v6。
- **附带接口异常**：4/600 canonical records 的 source_text 追加 E 示例（A/000044、A/000720、C/000035、C/000044），不能把 saved validation=true 当成正文复制正确的充分证据。全部 600 条的五字段 spans 均在原正文内且切片一致；condition/constraint 48 项整数计数 0 mismatch，本次未修写旧预测或重新评分。
- **产物与范围**：`outputs/reports/sep_c3_rc_boundary_attribution_v1.{json,md}`，包含逐案坐标、来源哈希、原文/细粒度 Gold 快照及 AI 待复核队列。API=0，未改活动 Prompt、Gold、程序或原评价结果；只做报告核验，不跑项目审计/测试。历史 750-call 方案仍 NO-GO，未证明新 wording 有效，也未完成 actor 机制或运行方差归因。

- 旧长候选停止推进；新增一个仅在旧 R_C 后追加 condition 保留句的离线草案。目标限于 condition 丢失，不声称解决 constraint FP 或 actor 副作用。未验证、未冻结，活动 Prompt 与正式默认配置未改，新增 API=0。

## SEP-C3 Constraint Refinement v2 调用价值审查与完整语义复核（2026-09-19，零 API）

- 该轮结论：**5 arms × 150 = 750 calls 不启动**。当时完整 recovery 语义复核后，校正依据不支持 temporal-only，也未识别单一最小候选；以 B 为研究参照收口，保留旧 R_C 的混合结果。上方补充复核进一步定位局部字段边界目标，尚不构成新 wording 或 API 的验证依据。
- 审查依据为本地证据提交 `fb96071` 的 600-call A/B/C/D 结果，以及当前 `outputs/development/sep_c3_targeted_refinement_v1` 的 600 条 canonical 预测；独立重算 150×4×5 字段计数共 18,000 项，0 mismatch，recovery/FP 枚举逐案一致。R_A 收益、R_C recall/FP 权衡和 B→D 六个 empty-Gold actor regression 的计数保留。
- 全量 Gold constraint 覆盖变化枚举得到 **52 条 recovery 比较记录 / 37 个独立 sample_id / 52 个恢复 Gold span**：A→C 27、B→D 25，跨方向 15 个样本重合。原 taxonomy 只有 40 条 / 28 个样本，漏掉 12 条 / 9 个样本。
- 校正后按实际新增命中片段做多标签语义复核：time 14、legal_reference 12、purpose 10、quantity 8、manner 8、other 25、exclusivity 2、undetermined 1；完整可解释 21 条、部分内容 29 条、仅 overlap 2 条。旧 time 33 条 = A→C 17 + B→D 16、23 个独立样本，其中大量为数量上限、法律引用、方式、范围或仅 overlap；旧 legal reference=0 结论撤回。
- 失败侧复核：A→C 未匹配预测 27→50，新出现未匹配 span 36 个、删除 13 个，净 +23；B→D 26→58，新出现 43 个、删除 11 个，净 +32。出现孤立 `only`、其他字段内容重抽为 constraint、时间短语 FP，以及 span 替换与净增加并存。
- 全部 7 条 manual-review 记录（6 个样本）保留 AI 离线复核意见，但不冒充人工裁决，原标记保持不变。B→D 的 6 个 actor regression 均为 Gold actor 空、B actor 空、D 新增 actor，属于可观察表型而非已证明的内部机制。
- 产出：`outputs/reports/sep_c3_constraint_refinement_v2_semantic_review.json` 与 `.md`；原审查报告 `sep_c3_constraint_refinement_v2_go_no_go_review.md` 保留。本批仅分析与文档；API=0，Gold/prompt/评价器/历史结果未改，不运行项目审计或测试。
- 历史证据提交 `fb96071` 的分支未配置 upstream；本轮交付提交与 push 结果在 handoff 中单独报告。

## SEP-C3 targeted refinement A/B/C/D 设计收口与论文接入（2026-09-19，零 API）

- **状态**：targeted refinement 探索已收口；A/B/C/D 是一次 600-call 开发/探索运行。B 仅为本轮研究参照，正式默认仍是 v6，B 的正式替换未完成；五臂 v2 750-call 计划 NO-GO/未执行；SEP-C3 modular_v1 的 000-111 八个 E/S/J 组合已全部执行（前一批 111/011/101/110；增量批 000/001/010/100；每臂 150 条、failed=0、无重复发送），但非同批交错、每格仅一次，批次/时间与因子单元混杂，不能据此作稳定主效应/交互结论；固定原始响应后处理归因仅本地分支 9b50729 覆盖旧 v6 与 modular 111，其余 arms 未覆盖且 adapter/canonicalizer/validator 子步骤贡献不可独立分离；重复运行不确定性仍未完成。整个 SEP-C3 不能因本轮收口标记完成。
- **同批结果**：A/B/C/D 五字段 mean F1 为 0.7246/0.7806/0.7558/0.7858；actor F1 为 0.6314/0.7672/0.6807/0.7284；constraint P/R/F1 为 A 0.8015/0.5556/0.6562、B 0.8102/0.6074/0.6943、C 0.7525/0.7185/0.7351、D 0.7553/0.7778/0.7664。每臂 150 条，共 600 calls，成功 600、失败 0；模型/采样/输入/Gold/evaluator 与既有 targeted refinement 合同一致。
- **取舍**：D 的 mean F1 高于 B，不能写 B 总分最高。保留 B 是因为 B 的 actor F1（0.7672）高于 D（0.7284），B 只用 R_A、composition 更简单，而旧 R_C 的 recall 收益伴随 precision 下降、FP 净增加和 B→D 六个空-Gold actor regression；这是考虑简洁性、actor 表现和副作用后的保守研究取舍，不是事后创造的验收阈值。
- **taxonomy 校正**：原 40 条/28 样本改为 52 条 recovery 比较记录/37 个独立 sample_id/52 个恢复 Gold span（A→C 27、B→D 25；15 个样本重合）；旧 time=33 与 legal-reference=0 撤回；校正标签为 AI 多标签复核，不是人工 Gold；完整可解释 21、部分内容 29、仅 overlap 2。
- **论文接入**：`paper/THESIS_DRAFT.md` §4.2 写入设计过程，§6.6 写入 A/B/C/D 结果、taxonomy 校正和局限；`paper/ABLATION_MATRIX.md` 增加 SEP-C3 targeted refinement 设计取舍与版本身份；`paper/CLAIM_EVIDENCE_MATRIX.md` 新增 C50-C52；`docs/MASTER_PIPELINE.md` 修订 3.7.16。
- **产物**：`outputs/reports/sep_c3_targeted_refinement_v1_execution.json`、`..._phase2_analysis.json`、`..._phase2_summary.json`；B prompt 文件 `prompts/sun_compat/modular_refinement_v1/generated/direct_llm_refinement_B_v1.md`，文件 SHA-256 `c468c631b6e454522994d6839f6a4021a259daedea7f3a2852b7b4343cd22849`，composition `207b54cc2f1123c7511451d7ead478654e550d438fe19d1031a13149b41917f1`。
- **边界**：本批整理已有证据并写作，新增 API=0；未修改 Gold、prompt、runner、评价器或正式默认配置。缺失来源仍包括被 gitignore 的 `outputs/development/sep_c3_targeted_refinement_v1/` 原始预测/raw/manifest、未提交的 `..._phase2_evidence.md` 与分析脚本 `scripts/analyze_sep_c3_targeted_refinement_v1.py`，以及未纳入当前分支的历史证据分支 `fb96071`；本次 push 不等于这些本地来源已全部远端备份。

## CSCWD 2027 投稿定位与核验（2026-09-17，文档范围）

- 用户补充当届通知：2026-10-31 截稿，2027-01-31 通知结果，2027-05-26 至 28
  Brisbane 会议。已从 EasyChair 公开登录页核到会议全称与新稿开放；官网正文未成功
  取得，具体时区、摘要节点、2027 页数/模板/匿名规则仍待核。不把往届六页自动当当届规则。
- 投稿方向评估：按应用/实证研究继续准备有合理依据；完整说明已有工作、近邻差异与
  实际发现，不把“C 类”解释为无需贡献或保证录用。保留 9 月 30 日导师完整初稿目标。
- `paper/CSCWD_POSITIONING.md` 保存文献对照、可引用范围和风险分析；主张矩阵
  C48/C49 与写作入口已接入。它是写作笔记，不是平行状态页/任务路线。
- 重点边界：Stage 1 target-aware；Stage 2 字段权衡为描述性；Oracle 隔离已有开发
  结果、正式主表仍待依赖；四类面板是目标字段受控评价；四臂消融失败不冒充八组合。
- 核验复用已有报告，未重新运行实验/API/评价器/代码测试；原有脏工作树中的实验修改
  不纳入本批。下一步沿现有 SEP-C1/PW 写作与 SEP-C2/SEP-C4 实质依赖推进。

## PW 写作目标记录（2026-09-15）

- 已记录用户目标：写清自己的贡献、完整说明已做工作，并把相关数据呈现在论文中。
- `AGENTS.md` 固定后续协作要求；`paper/README.md` 增加工作—章节—候选图表—
  依据清单及数据入文方式；`MASTER_PIPELINE.md` 修订 3.7.12 与 §12.1 接入 PW1–PW9。
- 本项完成范围是写作要求与覆盖清单的记录；正文全面展开、表格逐项回填仍待后续
  写作，不把本次记录当成论文完成或实验完成。
- 后续写作先整理现有方法、数据与结果形成完整初稿；需要补实验时对应具体缺口。
  定义、配置、统计和案例表可入正文，不为凑创新或表格数量自动扩大实验。
- 本次为纯文档变更：核对内容、链接和 Git 差异；不运行实验审计、代码测试或真实
  API，不改既有结果、Gold、实验门禁和下方两方法任务。

## SEP-C3 精简 prompt 真实四臂验证与退回（2026-09-15，实际 API=600）

- 先完成公共接口/S 边界修正：零起点右开区间坐标、ID 唯一性与引用合法性统归公共接口；S 保留要素定义、语义归属、范围、歧义和规范关系判断。实际 runner 改为读取 `modular_v1/generated/direct_llm_modular_<ESJ>_v1.md`，不再附旧示例或旧指导。
- 离线请求检查通过后，真实运行 111/011/101/110 各 150 条，共 600 次 Direct-LLM 调用；固定 EStG-150 input、冻结 Gold、coarse sentence-level 五字段 mean F1 主口径，modality label 分离。旧版完整 v6 复用同一模型发布批次 D-full-0813（无额外调用）。
- 结果（five-field mean F1）：旧版 0.7850；111=0.7262（-0.0588）；011=0.7470（删 E，+0.0208 vs 111）；101=0.7611（删 S，+0.0349 vs 111）；110=0.7355（删 J，+0.0093 vs 111）。
- 验收：所有检查失败。完整新版明显退步；三个单模块删除都未达到"完整版至少高 0.01"的贡献标准。actor 是主要退步项（precision 0.354 vs 旧版 0.573；130 predicted vs 82），`estg_000664` 111 把 "The following""taxation" 等非 actor 抽出；E 存在时 `estg_000028` condition 漏抽；J 删除后主口径未下降且 raw bare-JSON 仍 150/150，只有格式收益（新版 150/150 vs 旧版 107/150）但没有主 F1 增量。
- 处置：退回旧版 `prompts/sun_compat/direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md` 为默认 Direct-LLM prompt；`modular_v1` 保留为已实测未通过候选，不得作为正式替换，也不得据本轮结果改口径或补跑。
- 产物：`outputs/reports/sep_c3_modular_ablation_v1.{json,md}`、`outputs/reports/sep_c3_modular_ablation_analysis_v1.{json,md}`、`outputs/evidence/sep_c3_modular_ablation_v1/`。实际 API=600，失败=0，重试=0，调用上限=750；一次 shell reset 后从 59 条持久化 raw 续跑，样本未重发。



## 0. 当前派工：规则＋LLM 已取消（2026-09-14，覆盖下方历史状态）

用户原话：“规则+LLM直接不要了，不在进行规则+LLM的任何实验”。

- **取消** Rules+LLM-Repair / `sun_llm_fallback` / H1 的所有后续实验，包括 S2.12
  F-1/F-2/F-3 的 27 次调用、复跑、优化、消融及新增下游评价；不派发其他规则＋LLM
  修复/fallback 实验，包括此前待授权的 Stage 3 混合 fallback。
- **保留当前主线**：Rules-Only 对 Direct-LLM、必要前人比较、Direct 的 E/S/J
  消融及其固定 Stage 3 衔接。历史混合结果只作溯源，不删除、不重评、不冒充当前方法。
- **调用范围**：S2.12 Direct 36 + GDPR Direct 74 = 110 次计划；旧 137 次方案及
  发送确认请求已失效，27 次修复预算不挪用。本指令不构成真实调用授权，发送/费用仍为 0。
- **SEP-C2 两方法执行/评价/冻结合同已适配完成（2026-09-14，零 API）**：
  `configs/s2_12_active_method_scope_v1.json` 记录 active=Rules-Only/Direct-LLM；
  `configs/s2_12_active_preflight_v2.json` +
  `outputs/reports/s2_12_active_preflight_v2.json` 只锁 Direct 36 个请求体（D-CAL 1 +
  D-REST 35），与历史 v1 direct 36 行逐字节相同；v1 三方法 lock/report 保留为历史来源。
  `scripts/run_s2_12_sun_llm_fallback_v1.py` 在构造 transport、发送请求和写输出前拒绝，
  F-1/F-2/F-3 27 次取消且不挪用。
- **两方法冻结条件已具名】**：`outputs/reports/s2_12_two_method_contract_v1.json`
  与同目录 manifest 绑定 Rules-Only 既有评价、Direct 输出目录、输入/请求哈希和
  36+74=110 次剩余计划；Direct 未真实运行时 `comparison.complete=false`、
  `s2_12_complete=false`、`s2_13_complete=false`，取消的修复组
  `cancelled_repair_arm_required=false`，不得用减少方法数宣称冻结完成。
- **失败样本总体**：Direct 评价固定保留全部 36 行；`in_doubt`/failed 行按空
  canonical record 计入漏抽/误判，不比较成功样本子集。
- 真实 API=0；未创建收费授权；GDPR 默认 `gdpr7_direct_llm_v1` 的 74 条仍为
  `fake_payload_locked` 演练、network=0，不作为真实预测/恢复/promotion 来源；
  真实目录沿用 `gdpr7_direct_llm_raw_real_v1` / `gdpr7_direct_llm_real_v1`。
  旧 137 次方案及发送确认仍失效；当前取消不构成外部发送授权，自动审批阻塞未解除。
- 本批为实验代码、机器合同、具名测试与文档更新；未运行实验 API，未改 Gold 或历史
  预测/授权文件；停用规则仍见 `formal_experiment/AGENTS.md`。

## 0.2 SEP-C2 Stage 2B Winter 前人基线首轮实跑（2026-09-15，零 API）

- 已核实 `references/合规性检查模型代码/model_check` 是 Winter prototype（112 个非缓存文件与 Winter 副本一致），不是 Sun Stage 2；未找到更直接兼容的 Sun 抽取实现。
- 已在 EStG-150（150 条）与正式 Gold（231 个 clause_span）上固定并运行 `estg150_clause_region_detection_v1`；共同任务只评 clause region，不把义务从句冒充 action span。
- 实跑：Winter 1.0000/0.8312/0.9078；历史 Rules-Only 0.9398/1.0000/0.9689；历史 Direct-LLM 0.9476/0.9740/0.9606；新增 LLM/API=0。
- 真实失败例：Winter `estg_000071` 无 signal word 零预测漏 3 区域；Direct-LLM `estg_000112` 零 clause 漏 1 区域。
- 产物：`outputs/reports/sep_c2_stage2b_predecessor_baseline_v1.*`、`outputs/evidence/sep_c2_stage2b_predecessor_baseline_v1/`、public source probe；独立 verifier 与 6 个 focused tests 通过。
- 边界：Sun 原表 12（0.58/0.89/0.70 vs 0.77/0.83/0.80）是私有 BPMN violation 任务，不能与本适配结果直接比较。
- 下一步：继续检查/运行更直接兼容的前人实现，并把本轮结果接入论文证据位置。

## 0.1 SEP-C2 两方法证据收口与 S2.13 v10 后继入口（2026-09-14，零 API）

- `build_s2_12_two_method_contract_v1.py` 已把 `comparison.complete` 改为证据判定：复用 Rules-Only 与 Direct-LLM 既有独立 verifier，并核对冻结输入绑定、36 条固定总体、有限指标和 verifier 重放/绑定结论；只看 `status`/`dataset_id` 不足以完成。
- 当前实际证据：Rules-Only 验证通过；`data/predictions/s2_12_direct_llm_v1` 与 `data/results/s2_12_direct_llm_v1` 不存在，因此合同仍 partial，`comparison.complete=false`、`s2_12_complete=false`；S2.12 真实实验未提前标完成，真实 API=0。
- 新增 S2.13 后继入口 v10 及 schema/outputs：S2.12 状态从两方法合同派生，S2.13 只等待两方法证据，不再等待 `sun_llm_fallback`；v9 及更早胶囊 byte-exact。
- 具名测试覆盖缺证据拒绝、完整证据通过、取消组不参与和 v10 合同状态；builder replay 与 v10 verifier 通过；未跑全量测试。
- **Direct-36 零调用就绪核验（2026-09-19）**：`outputs/reports/s2_12_direct36_readiness_review_v1.md`。Rules-Only 36 条完整可验；Direct 无可复用 raw/partial/失败/in_doubt 记录；输入/prompt/model/Gold/evaluator 绑定一致；但 successor 两方法授权缺失、总输入 token 与 USD 硬上限未给、外部发送审批和当前价格复核未过；旧 137/D-CAL/D-REST 授权绑定旧 runner+已取消 fallback，不能复用。总体 **BLOCKED**（仅就绪判断，本轮零调用）。
- 下一步：继续 SEP-C2 Stage 2B 前人基线首轮实跑，不以准备报告代替结果。

## 0. SEP-C2 取消前断点（2026-09-14，历史 137 次范围）

**状态：执行准备已通过；D-CAL 首条真实发送被自动审批阻止，S2.12 未完成。**

- 主工作区已从 `2ca65cd` 快进至远端已备份的 `952b405`；原有 20 个相关已修改/
  未跟踪文件的 SHA-256 不变，嵌套旧 worktree 未动。
- S2.12 原授权验证 **70/70 PASS**，快速完整性检查 **pass / errors=0**；真实账本
  和胶囊尚不存在，无其他同批次 Python 执行进程。既有 63+74 次授权范围及 hash 不变。
- 进程已能识别现有密钥；补齐临时 enabled/provider/model/base_url/max_tokens 等
  非秘密配置后，离线检查 **API ENV READY**。未读 `.env`，未打印密钥；不能继续沿用
  “只缺凭据”的旧结论。配置只在本次子进程有效，接续运行须在同一进程设置。
- 已从 DeepSeek 官方当日价格页重新核验 V4-Pro-0813 与原定价格/闲时；请求模型、
  prompt、样本与原授权不变。
- D-CAL 命令在创建进程前被自动审批拒绝：需要当前任务明确确认向 DeepSeek 发送
  锁定实验文本，文件中的历史授权未被该审批系统接受。**发送 0、费用 0、未重试。**
  等待的是该外部发送确认；不把它记成模型失败或已消耗一次 API。
- `outputs/development/gdpr7_direct_llm_v1` 的 74 条 completed 是
  `fake_payload_locked` / network=0；不可当真实结果、不可用于真实续跑或 promotion。
  实际 GDPR 输出按 §13.3 使用 `gdpr7_direct_llm_raw_real_v1` / `gdpr7_direct_llm_real_v1`。

**证据/确认范围**：`outputs/reports/sep_c2_execution_preflight_v1.json`。本 checkpoint
只保存检查结果与阻塞，不创建新 API 授权，不改 Gold、代码或历史预测；无新增测试。
**下一项不变**：SEP-C2，接续 D-CAL → D-REST → F-1/F-2/F-3 → 同口径评价；GDPR
批次及下游成对比较按既有合同执行。S2.13 和 v5 fallback 状态不提升；SEP-C3 modular_v1 八组合已在后续增量批各执行一次，但仍非同批/无重复，不能提升为稳定主效应/交互结论。

## 0. 交付复核与当前下一项（2026-09-14）

- 已在主工作区接收 `6c22b8a`（C36 v2）和 `4fdc91f`（SEP-C1-A），并普通推送至
  `origin/codex/b0-r1-a-span-boundaries`；两个原本仅本地的 checkpoint 均已远端备份。
- C36 v2 的 6 个产物、4 个实现文件、8 个冻结输入及两个依赖的登记哈希核对通过。
  7 项相关测试沿用 DS 已记录证据；其快速完整性检查在另一工作区执行的限制保留，
  不宣称此次重新完成全量或同状态整体验证。本轮未运行实验/API/测试。
- SEP-C1-A 正文收尾：target-paired 限定为四类扩展合成开发面板；补充 Stage 3
  语义定位扩展所用同源局部 XML 证据；r10 A 组有一条有效配对，实际中断原因为
  `action_mapping_below_gamma`（0.690984），已纠正“抽取失败或未配对”的归因；
  r8 的 `xml_counts` 明确来自 capsule 的原始 BPMN 诊断，非 Process Record 字段。
- C36 v1 的派生 80 行记录已保存 control 布尔/未知值；v2 的新增贡献是兼容性门禁
  与依赖/阈值绑定，下方历史文字中“补上 v1 持久化缺口”不再作为当前主张。

**唯一下一项：SEP-C2（必要前人对照与既有授权批次）。**
SEP-C1-B 已完成：前人比较范围、通用题名与完整 E/S/J 2^3 消融预算准备已写入
现有正文、主张矩阵和消融矩阵；该 SEP-C1-B 同批双重复 2400-call 主设计本身真实实验/API/测试均为 0，其八组合保持待运行。另：SEP-C3 modular_v1 八组合已有单次真实执行（commit 18f5cf9 及前批），但非同批、每格一次，不能混写为该主设计已完成。
SEP-C2 启动时先核验既有 137 次授权、账本、载荷与进程环境可运行性；不重开已完成
的 C36 比较或 SEP-C1-A，不插入新的约束优化或全量测试。

## 0. 当前验收：SEP-C1-B（2026-09-14，零真实 API）

**Status**: VERIFIED_WRITING_INTEGRATION / BUDGET_PREPARATION（paper + read-only
asset check；无新实验、无真实 API、无可执行 prompt/检查器/Gold 修改）。

**本轮完成什么**
- 前人比较范围：`paper/THESIS_DRAFT.md` §2.3、§4.6、§6.5；三层比较注册、Sun
  本地作者稿/最终版 DOI 边界、Winter 原方法/wrapper/四类扩展命名边界，并明确
  Stage 2 外部抽取对照仍未完成。
- 通用题名：`THESIS_DRAFT.md` 题目节固定推荐中英文题名与两个备选；摘要/RQ 统一
  自然语言合规需求术语；现有数据覆盖仅 EStG-150 与 GDPR-7/S2.11。
- 完整组合与预算：`paper/ABLATION_MATRIX.md` SEP-C1-B 节和
  `outputs/reports/sep_c1b_factorial_budget_plan_v1.md`（八组合、E/S/J 定义、共同
  接口、推荐 2400 calls、非推荐复用 1800 calls、价格/日期/未核实声明）；授权草案
  见 `docs/API_AUTHORIZATION_REQUEST.md` §14。
- 主张矩阵新增 C44/C45/C46；上述 SEP-C1-B 计划的八组合真实结果仍待运行；SEP-C3 modular_v1 八组合已有单次结果，不得混写为该计划已完成。

**边界**
- 未创建授权事件，未调用真实 LLM/API；未新增或修改 executable prompt、检查器、
  Gold；`build/runner` 扩展和重新渲染 token 预算仍未实现。
- 价格快照记录于 2026-08-30，本轮未联网复核；执行前必须再核验。

**提交与推送**
- `a13ec04`（B1 前人比较范围）和 `70bcc18`（B2 通用题名）已推送至
  `origin/codex/b0-r1-a-span-boundaries`；B3 与本状态更新同一 scoped commit，
  完成后由交接报告 SHA。
- 主 sandbox 对 `formal_experiment` 无写权限，本轮在临时注册 worktree
  `.codex_worktree_sep_c1b` 完成编辑/提交；远端备份以 push 为准。

## 0. 当前写作验收：SEP-C1-A（2026-09-14，零真实 API）

**Status**: VERIFIED_WRITING_INTEGRATION（paper writing + read-only source check；
无新实验、无真实 API）。

**本轮完成什么**
- `paper/THESIS_DRAFT.md` 新增 §3.4 三阶段输入/输出契约：Stage 1 Process Record、
  Stage 2 Rule Record、Stage 3 Violation Report 的输入、输出记录、不变量和已知
  失败模式；明确 Gold-blind、unknown 不等于合规、expected label 只用于评价分组。
- 新增 §3.5 贯穿案例（development-only）：SIM 卡入网 r10 成功链（动作映射到
  `Activate SIM card`，owner `Customer`，required actor `the phone company`，
  `incorrect_actor=violation`，case 评价 `found_with_reference_evidence`）与
  r8 失败链（Stage 1 无 timer/terminate/event_subprocess 结构化字段；Stage 3
  报警为 `machine_alarm_but_reference_correspondence_unverified`；修复件
  `semantics_entered_detection_chain=false`）。
- 本节绑定同一 case capsule
  `outputs/development/sim_case_c1/run_v1/capsule.json`
  （sha256 `481f068c...`），并引用 `paper/SIM_CASE_SECTION_v1.md`。
- 只读源核对产物 `outputs/reports/sep_c1a_source_check_v1.json`（sha256
  `98796fd932bd1e5d9b76cd56f1ebf3749d98568b1be58926730f07f450a20aad`）逐项校验上述
  r10/r8 值与 capsule 一致。
- `paper/CLAIM_EVIDENCE_MATRIX.md` 新增 C42（C36 v2 门禁/收尾）与 C43
  （SEP-C1-A 写作接线），禁止把 development 案例写成正式 Gold、Oracle 或方法优劣。

**边界**
- 无新实验、无真实 API、无 Gold 修改；未运行全量测试。
- SEP-C1-B 当时仍待完成；现已完成，见上方当前验收。
- 正式 Oracle/端到端与真实 v5 fallback 的依赖不变。

**下一步**：继续 SEP-C2（见上）。

## 0. 当前验收：S3-C36-TARGET-PAIRED v2（2026-09-14，零真实 API）

**Status**: VERIFIED_DEVELOPMENT_COMPARISON_V2（development-only synthetic
panel；冻结预测只读复用；无真实 API）。

**本轮关闭的缺口**
- v1 的 control 侧只有 `observable`/`score`，没有持久化最终布尔 `violation`。
  v2 在同一 40 个 control 样本 / 160 个 control-side 检查上，用冻结函数
  `control_prediction_from_scores(control_scores, gamma_ext)` 重建后，把
  per-type `status` 与 `violation`（布尔或 unknown=null）直接写入
  `c36_winter_target_paired_checks.jsonl` 的 80 条检查记录；不需要再生成
  单独文件，也不从统一单标签结果反推。
- 兼容性从审计升级为前置门禁：样本集合/唯一键、expected label、
  process_id/rule_id、两侧 BPMN SHA-256、C36 manifest 必需输入哈希、两侧
  prediction 文件哈希、四类字段形态、行级 `gamma_ext` 与 manifest 阈值的
  绑定、重建依赖哈希，任一不满足即 **blocked**，不写 comparison。
- 依赖绑定：`src/bpc_hybrid/stage3_extended_violations.py` 当前文件与 C36
  manifest 的实现哈希在 `canonical_lf_utf8_text` 模式下匹配；冻结阈值
  `gamma_ext=0.5`；v5 target-paired evaluator 明确登记为当前协议，不冒充
  历史 C36 产物。
- 基线名称改为 **Winter-style four-type extension baseline**，避免被读成
  Winter 原论文结果。

**实际验收结果**
- Gate：**pass**；blocking issues **0**；依赖重建
  `verified_frozen_match=true`；80 条 v2 检查记录中的 control 布尔值已持久化。
- 同协议比较（40 对）：C36/Winter-style baseline Macro-F1 **0.6036**、pair
  **18/40**、target unknown **0.3625**、control target FP **0.0750**；当前
  v5 deterministic Macro-F1 **0.6737**、pair **21/40**、target unknown
  **0.3375**、control target FP **0.0250**；delta F1 **+0.0701**、pair
  **+3**、unknown **-0.0250**。
- 这只说明当前冻结开发面板上的同口径差异，不是 formal Oracle，不是真实
  API 结果，也不是直接 Winter 论文数字。

**生成了什么**
- `outputs/reports/s3_c36_target_paired_v2.{json,md}`
- `outputs/evidence/s3_c36_target_paired_v2/audit.json`
- `outputs/evidence/s3_c36_target_paired_v2/c36_winter_target_paired_checks.jsonl`
  （80 条，含持久化 control 布尔/未知状态）
- `outputs/evidence/s3_c36_target_paired_v2/comparison.json`
- `outputs/evidence/s3_c36_target_paired_v2/manifest.json`
- `outputs/evidence/s3_c36_target_paired_v2/artifact_hashes.json`
- `src/bpc_hybrid/s3_c36_target_paired_v2.py`
- `scripts/run_s3_c36_target_paired_v2.py`
- `tests/test_s3_c36_target_paired_v2.py`（**7 passed**）

**边界**
- 未运行全量测试；只运行本任务具名测试。
- v1 的 `s3_c36_target_paired_v1` 产物保留为历史版本，不覆盖；v2 是当前入口。
- 真实 v5 fallback 仍无覆盖 v5 scope/hash 的授权，真实 API=0。

**下一步**：C36 target-paired 验收护栏、依赖绑定与交付收尾完成；继续
SEP-C1-A，把三阶段 I/O 与 SIM r10 成功链 / r8 失败链写入现有论文，并核对
原始记录与主张矩阵。

## 0. 历史验收：S3-C36-TARGET-PAIRED v1（2026-09-14，零真实 API；已被 v2 取代）

**Status**: VERIFIED_DEVELOPMENT_COMPARISON (development-only synthetic panel;
frozen-prediction reuse; no real API).

**实际查到什么**
- C36/Winter 保存的 40 条逐项预测与当前 synthetic panel 的 40 个 variant/control
  对完全同集：item_id、expected label、process_id、rule_id、variant/control BPMN
  SHA-256 全部匹配。
- C36 manifest 中 rule inference pack 与 panel 的 raw SHA-256 与当前文件匹配；
  全部行 `gold_visible=False`。
- variant 侧 40×4 检查全部有显式 `observable`/`violation`；observable=true 的
  条目全部有布尔 `violation`；observable=false 保留为 unknown。
- control 侧 40×4 检查有 `observable`/`score`/`reason`/`exact_contradiction`，
  但没有持久化最终布尔 `violation`。本比较使用项目冻结函数
  `control_prediction_from_scores(control_scores, gamma_ext)` 从上述字段重建
  per-type 布尔值；影响 40 个 control 样本 / 160 个 control-side 检查。
  这不是从统一单标签结果反推，也不是 Gold 参与预测。
- 无 blocking field gap；比较可在该 reconstruction dependency 下成立。

**比较结果（同一 target-paired 口径，40 对）**
| 方法 | Macro-F1 | pair success | target unknown | control target FP |
|---|---:|---:|---:|---:|
| C36/Winter | 0.6036 | 18/40 | 0.3625 | 0.0750 |
| 当前 v5 deterministic | 0.6737 | 21/40 | 0.3375 | 0.0250 |
| 当前减 C36 | +0.0701 | +3 | -0.0250 | -0.0500 |

per-type F1（prohibited/condition/constraint/exception）：C36
0.8696/0.3333/0.7500/0.4615；v5 1.0000/0.9000/0.3333/0.4615。
这是开发面板上的同口径比较，不是 formal Oracle，也不是真实 API 结果。

**生成了什么**
- `outputs/reports/s3_c36_target_paired_v1.{json,md}`
- `outputs/evidence/s3_c36_target_paired_v1/audit.json`
- `outputs/evidence/s3_c36_target_paired_v1/c36_winter_target_paired_checks.jsonl`
  （80 条 variant/control 检查行）
- `outputs/evidence/s3_c36_target_paired_v1/comparison.json`
- `outputs/evidence/s3_c36_target_paired_v1/field_gaps.json`
- `outputs/evidence/s3_c36_target_paired_v1/manifest.json`
- `src/bpc_hybrid/s3_c36_target_paired_v1.py`
- `scripts/run_s3_c36_target_paired_v1.py`
- `tests/test_s3_c36_target_paired_v1.py`（6 passed）

**剩余缺口/边界**
- control 侧最终布尔 `violation` 未持久化；当前比较依赖冻结决策规则重建。
  若要求完全独立的字段级持久证据，最小补跑是：在同一 40 个 control 检查上，
  用已保存的 `control_scores` 和同一 frozen rule 写出 per-type 布尔值/状态；
  不需要重新推理，也不需要新 API。
- C36 manifest 未列出 Stage 1 structural contract 输入；本比较不需要重新解析，
  因为被比较的是已冻结的 per-check 预测字段，且 panel/BPMN/rule inference pack
  身份已匹配。
- 未运行全量测试；仅运行本任务具名测试。

**下一步**：本 S3-C36-TARGET-PAIRED 已完成；可继续 S3-V5 真实 fallback 授权
流程（仍在等待覆盖 v5 scope/hash 的明确授权），或按 SEP-C1 继续三阶段 I/O
与成功/失败案例写作。

## 0. 当前验收：S3-V5-RUNNER-INTEGRATION（2026-09-14，零真实 API）

**状态：VERIFIED_OFFLINE_INTEGRATION；Stage 3 整体尚未完成。**

- 已将主工作区从 `45513f3` 快进到 DS 的远端 `51040ca`，保留原有本地修改；
  DS v3/v4/v5 的 34 个登记产物哈希全部匹配。
- DS 完成了匿名化修复、两侧对象键、评价口径、逐字段响应应用、动作/证据回绑、
  执行恢复及 v5 错误锚点保护；这批内容确有落地，但最新入口仍缺少完整预测和评价接线。
- 本次接通冻结输入→响应→本地复核→v5 保护→80 条预测→配对评价；模拟/真实目录
  独立并绑定输入身份；22 个候选对象实际只有 18 份唯一请求，相同正文共享响应、
  保留各自对象 ID 且只计费一次；发送开始后中断不重发，usage 未知不宣称完成。
- 五个相关测试文件 **42 passed in 0.87s**，快速完整性检查通过；没有执行全量测试。
  机器字段 `final_experiment_ready=True` 是已有门禁结果，不代表 Stage 3 Oracle 或真实 fallback 已完成。
- 最终离线恢复：**0 新发送、18 历史响应、22 个响应对象被消费、80 条预测**；21 项
  检查发生变化，mock Macro-F1 0.7773、配对 28/40、unknown 0.2375 **仅属假响应接线证据**。
  DS v5 的实际开发效果仍是 F1 **0.6737**、配对 **21/40**、unknown **0.3375**。
- 接受证据：`outputs/evidence/s3_semantic_grounding_v5_integration_v1/mock/attempt_002/`。
  `attempt_001` 保留为接入器未消费 validated 状态的失败过程证据，不作为闭环验收。
  原始 v2/v3/v4/v5 预测、manifest、Gold 和用户原有修改未覆盖。
- preflight 中的 22 是对象请求条目数/保守调用上限；当前执行策略按 18 份唯一正文发送。
  原候选包与请求正文哈希未变，真实 API=0；旧 v2 授权不能挪用。费用沿用旧 preflight
  的静态估计，本次没有重新核验供应商价格，不应当作实时报价。

**Next suggested action: S3-C36-TARGET-PAIRED compatibility audit is complete.**
能否支持同口径评价；可以只读重评分才生成表，否则提交字段级缺口与最小补跑清单。
不得从旧单标签指标反推四类检查，不为了填表改 Gold、改分母或把 unknown 算作合规。
真实 v5 fallback 另待范围授权；等待时可继续 SEP-C1-A 的三阶段 I/O 和成功/失败案例写作。
后续较早记录为历史状态，冲突时以本节及下方当前派工表为准。

## 0. Latest v5 LLM preflight: s3_semantic_grounding_llm_v2 (2026-09-13, zero API)

**Status**: READY_FOR_AUTHORIZATION_DECISION / BLOCKED_NO_MATCHING_AUTHORIZATION.

- Candidate pack: **22 items** (7 variant + 15 control), v5 pack hash
  `915750b068a45f98be56b0e48c6ef0722d95e8d5bda870cbcdb1f1f4e2ae54f2`.
- Request set: **22 calls**, rebuilt from the v5 pack with the final
  prompt/executor code; request-set hash
  `fdd72c0191afdb24975550d9297951385aedca91d69c3722952a6f49eb123c53`.
- Expected input tokens: **69,032**; input cap **138,064**; total output-token
  cap **11,264** (512 per call).
- Cost: peak estimate **USD 0.1357**, off-peak estimate **USD 0.0679**, requested
  cap **USD 0.20 / RMB 1.44**.
- Off-peak only: UTC windows **00:00-01:00 / 04:00-06:00 / 10:00-24:00**.
- Matching existing v5 scope+hash authorizations: **0**. Old v2 pack/request
  hashes are explicitly not reused. Real API calls = 0.
- Suggested authorization sentence SHA-256:
  `f6eda1b245c078d3def5e3d0b736df5a60eb75b2de97ecc4da984471abfc38da`.

**Artifacts**: `outputs/reports/s3_semantic_grounding_v5_llm_preflight.json`,
`s3_semantic_grounding_v5_llm_authorization_request.{json,md}`,
`outputs/evidence/s3_semantic_grounding_v5/llm_preflight_v2.json`,
`llm_preflight_request_set_v2.json`,
`llm_preflight_canonical_requests_v2.jsonl`, `llm_authorization_request_v2.json`,
`scripts/build_s3_semantic_grounding_v5_llm_preflight.py`,
`scripts/run_s3_semantic_grounding_llm_v2.py`.

**Authorization boundary**: this is a request, not an authorization. A real call
still requires the user's exact sentence and a new unconsumed authorization
event; the old 20-item v2 hashes and any unrelated carried authorization are not
valid for this payload.

## 0. Latest checkpoint: s3_semantic_grounding_v5 (2026-09-13, zero API)

**Status**: VERIFIED_DEVELOPMENT_DETECTION_REPAIR. Frozen v2 predictions are
read-only reused after artifact-hash verification; no API call.

**Concrete failure chains**

1. **Constraint false positive (fixed)** — `syn_v2_exception_not_handled_06`
   control. Rule field: `constraint="not later than 72 hours"`, action
   `"notify the personal data breach"`. The frozen action grounder resolved to
   the generator-inserted node whose label is the rule **exception** text
   because the process has no action node equal to the rule action. The local
   constraint check then saw no 72-hour bound around that non-action node and
   emitted `constraint_violated=True`
   (`explicit_time_bound_absent_from_closed_action_scope`). Repair: when the
   resolved label strongly matches a non-action rule field and not the rule
   action, condition/constraint determinations anchored to that node are
   demoted to `unknown`. No API and no per-sample threshold change.
2. **Exception abstention / capability boundary** —
   `syn_v2_exception_not_handled_02` variant. The frozen process does not
   express the rule action; action grounding is unresolved
   (`no_activity_with_semantic_or_lexical_signal`), so handler absence cannot
   be programmatically established. The record keeps `unknown` and an explicit
   capability boundary instead of fabricating a violation.

**Detection change / cost**
- Changed checks: **2** (both control-side clear determinations demoted to
  unknown).
- Withdrawn control alarm checks: **2** (legacy diagnostic 26 -> 24;
  demoted to unknown, not independently verified global false positives).
- Demoted target-paired variant positives: **0**.
- Target-paired Macro-F1: **0.6737 -> 0.6737**; pair success **21/40 -> 21/40**;
  target-field unknown rate **0.3375 -> 0.3375**. F1 was not required to rise.
- v5 fallback pack: 22 items (7 variant + 15 control), all advertised evidence
  ids visible, semantics preserved.

**Artifacts**
- `src/bpc_hybrid/s3_semantic_grounding_v5.py`
- `scripts/run_s3_semantic_grounding_v5.py`
- `configs/stage3_semantic_grounding_v5.json`
- `tests/test_s3_semantic_grounding_v5.py`
- `outputs/evidence/s3_semantic_grounding_v5/`
- `outputs/development/s3_semantic_grounding_v5/`
- `outputs/reports/s3_semantic_grounding_v5.{json,md}`

**Boundary**: development-only synthetic panel, deterministic guard, no formal
Oracle or human Gold.
## 0. Latest checkpoint: s3_semantic_grounding_llm_execution_v2 (2026-09-13, offline fake transport)

**Status**: VERIFIED_OFFLINE_EXECUTION_SEMANTICS. No real API calls.

**Fixed**
- Recovery now loads the append-only ledger, saved raw responses and
  normalized records; resumed summaries include historical completed items as
  well as current-round sends.
- Terminal states distinguish `pre_send_failed`, `send_started/sent`,
  `malformed`, `rejected`, `succeeded`, `in_doubt` and
  `usage_unknown`. Any request whose ledger says it was sent is never
  auto-resent, including malformed/rejected/in-doubt outcomes.
- Ledger reads validate the `prev_hash`/`record_hash` chain. A tampered ledger
  fails closed before any new send.
- Every terminal item is persisted immediately (raw response, normalized
  record and ledger state); resume does not overwrite prior raw/normalized
  evidence.
- Before every send the executor enforces call count, input/output-token
  caps, USD cap and off-peak windows. Unknown earlier usage, in-doubt sends or
  missing provider usage halt further sends under the contract.
- Successful provider usage is saved and reused on resume. Actual
  input/output tokens and USD cost are accumulated from stored records.
- The runner now writes `REAL_RUN_<status>` using the executor's
  `complete/partial/blocked/failed` classification instead of hardcoding
  `REAL_RUN_COMPLETE`.

**Offline validation**
- `tests/test_s3_semantic_grounding_llm_execution_v2.py` uses fake transports
  only and covers: complete + resume history, malformed/rejected no-resend,
  generic failure `in_doubt` halting later sends, retryable pre-send failure,
  max-call/off-peak blocking before send, actual usage persistence, and
  tampered-ledger fail-closed behavior. 7 passed.
- No real LLM/API or network call was made.

**Boundary**: execution semantics only; no real-run metrics are claimed.

## 0. Latest revision: s3_semantic_grounding_v4 (2026-09-13, zero API)

**Status**: OFFLINE_IMPLEMENTATION_EVIDENCE. This revision repairs how a
validator-passed LLM response is consumed. It does not claim real-model
performance; real API calls remain 0.

**What changed**
- `_normalize_llm_status` no longer returns whole-response `ambiguous` when a
  different field is resolved; a validated response is applied field by field.
- `apply_llm_grounding` now delegates to the v4 field-wise applicator: an
  anonymous activity id is reverse-mapped through the pack's deterministic
  map, bound to the real process node, and the affected local checks
  (`prohibited_action_present`, condition, constraint, exception) are
  re-executed on that node.
- Positive condition/exception claims require non-empty evidence ids that
  exist in the target action's local surface; absence claims are accepted only
  when the program re-check closes the scope; constraint claims require a
  programmatic numeric time comparison. Otherwise the deterministic unknown
  remains.
- Clear deterministic checks are preserved and are never overwritten by an LLM
  claim.
- Candidate context now derives allowed evidence ids from the actually
  visible post-truncation evidence lists. The v4 pack reports
  `all_evidence_ids_visible_in_payload=true`. The historical v3 pack is not
  overwritten.

**Offline acceptance**
- Frozen v3 predictions reused by hash.
- v4 candidate pack: 20 items; all advertised evidence ids visible in the
  model payload; all rule actor/action/condition/constraint/exception fields
  preserved verbatim.
- Five constructed end-to-end cases pass in
  `outputs/evidence/s3_semantic_grounding_v4/offline_grounding_demo.json`:
  action+condition progress while an ambiguous constraint abstains;
  action reverse-mapping updates the prohibited check; an unclosed absence
  claim abstains; hallucinated/out-of-surface evidence is rejected; a
  truncated context never advertises cut-off evidence.
- Status of these cases is explicitly
  `OFFLINE_IMPLEMENTATION_EVIDENCE_NOT_LLM_PERFORMANCE`.

**Artifacts**
- `src/bpc_hybrid/s3_semantic_grounding_v4.py`
- `scripts/run_s3_semantic_grounding_v4.py`
- `configs/stage3_semantic_grounding_v4.json`
- `tests/test_s3_semantic_grounding_v4.py`
- `outputs/evidence/s3_semantic_grounding_v4/`
- `outputs/development/s3_semantic_grounding_v4/`
- `outputs/reports/s3_semantic_grounding_v4.{json,md}`

**Boundary**: constructed cases prove implementation wiring only; they are not
a real LLM run and must not be cited as an accuracy improvement.

## 0. Latest revision: s3_semantic_grounding_v3 (2026-09-13, zero API)

**Status**: VERIFIED_DEVELOPMENT_PROTOCOL_REPAIR. This checkpoint reuses the
frozen v2 deterministic predictions byte-for-byte after artifact-hash
verification and repairs the input pack and evaluation accounting. No real API
call was made.

**Input repair**
- New `_scrub_string` failure identified: the v2 blanket substring replacement
  changed `controller` to `anonymousler` in 12 rule fields and also rewrote
  natural-language evidence. The v2 pack is historical and is not overwritten.
- New field-aware anonymisation maps only identifiers and generated `syn_*`
  tokens; rule/action/condition/constraint/exception text and activity labels
  are preserved verbatim. The v3 pack reports
  `semantic_fields_preserved_for_all_items=true`, zero forbidden/generated
  hits in the model-visible payload, and deterministic real->anonymous maps.

**Evaluation repair**
- `fallback_transition_metrics` is keyed by `(item_id, side)` and reports
  variant `unknown->correct/wrong/still-unknown` separately from control
  `unknown->correct/wrong/still-unknown`; control false alarms are never
  counted as variant successes.
- Target-paired metrics now expose mutually exclusive side outcomes,
  coverage, and explicit denominators. Variant unknown is an FN but is
  reported as `FN_unknown`; control unknown is outside the decided TNR
  denominator and is reported as its own count. Pair success uses all pairs.
- Control self-consistency status is now a model diagnostic only. No
  independent global-compliance labels are claimed and no clean-unified
  metric is computed; all 40 frozen controls remain in the same fixed
  evaluation scope for every method.
- C36 target-paired comparison is recorded as
  `GAP_DOCUMENTED_NOT_COMPUTED` because the C36 capsule lacks the required
  per-side target-field observable/violation records and composite identity;
  old C36 numbers are not spliced into the v3 table.

**Deterministic accounting (identical v2 predictions)**
- Target-paired Macro-F1 **0.6737**; pair success **21/40**.
- Variant side: 24 positive, 0 observed-negative wrong, 16 unknown
  (coverage 0.6000).
- Control side: 28 negative, 1 false alarm, 11 unknown (coverage 0.7250);
  FP rate 0.0250 over all pairs, 0.0345 over decided controls.
- Overall target-field unknown rate **0.3375** over all side checks.

**Artifacts**
- `src/bpc_hybrid/s3_semantic_grounding_v3.py`
- `scripts/run_s3_semantic_grounding_v3.py`
- `configs/stage3_semantic_grounding_v3.json`
- `tests/test_s3_semantic_grounding_v3.py`
- `outputs/evidence/s3_semantic_grounding_v3/`
- `outputs/development/s3_semantic_grounding_v3/`
- `outputs/reports/s3_semantic_grounding_v3.{json,md}`

**Boundary**: development-only synthetic controlled panel; LLM fallback pack
is still not a real-run result, and this revision is not formal Oracle or
human Gold.

## 0. Latest revision: s3_semantic_grounding_v2 (2026-09-12, zero API)

**Status**: VERIFIED_PROJECT_FACT (development-only synthetic controlled panel). The v2 revision repairs the evaluation protocol around the unchanged v1 deterministic scorer and freezes the LLM fallback subset. No real API call was made.

**Evaluation corrections**
- True collision identity is now `canonical_rule_input_hash + canonical_process_input_hash` over the model-visible Rule Input and Process Record/XML. True collision requires identical composite input and different expected labels.
- Corrected true collisions: **9 groups / 20 side objects**. The old BPMN-only v1 audit reported 7 variant groups / 28 variants; it overestimated because it ignored the Rule Input and counted only the variant side.
- Controls are no longer treated as globally none. Offline global-compliance status from the four structural checks gave **5 verified_compliant / 22 violated_other_field / 13 unknown** controls.
- Primary evaluation is now **target-paired causal**: only `checks[target_field]` is scored per pair. The legacy 80-object unified view is retained as a secondary diagnostic.

**Deterministic v2 result (reference/winter backend)**
- Target-paired: Macro-F1 **0.6737**; per-type F1 prohibited **1.0000**, condition **0.9000**, constraint **0.3333**, exception **0.4615**; control target-field FP rate **0.0250**; pair success **21/40 = 0.5250**; target-field unknown rate **0.3375**.
- Variant binary checks: Macro-F1 **0.5619**.
- Clean unified (40 variants + 5 verified compliant controls): 5-class Macro-F1 **0.6709**; 4-type Macro-F1 **0.5886**.
- Legacy 80-object diagnostic: 5-class Macro-F1 **0.4246**; 4-type Macro-F1 **0.4752**; it is not a pure none-Gold benchmark.
- Deterministic replay: two full runs produced byte-identical `predictions.jsonl` (SHA-256 `a6c70b1301b83d9cf4f9e6ea24a33e677a6608e9fc2c3efb1fd9a8869350eb85`).

**Fallback subset and LLM preparation**
- Frozen fallback candidate pack: **20 items** (7 variant + 13 control), restricted to final deterministic abstentions (`predicted_violation_type = None`) with documented semantic ambiguity; clear deterministic compliant/violation objects are excluded.
- Strict executor is implemented: canonical request builder, payload hash, strict JSON validator, evidence-ID validation, response parser, fail-closed policy, retry=0, token/cost estimator, budget caps, append-only execution ledger, resume/no-double-send protection, raw-response storage, normalized grounding storage, and program-side evaluator/ablation wiring.
- Full mock/offline execution succeeded: 20/20 requests, 18 ambiguous / 2 resolved, 0 malformed, 0 rejected, 0 in-doubt. This is plumbing evidence only and is not an experimental LLM result.
- Preflight: 20 calls, 62,333 estimated input tokens, 10,240 total output-token cap, USD cap 0.18 (peak-contingency) / RMB 1.30, retry=0, off-peak only; request set SHA-256 `1ac203ec1b2bc4e4a4ac3b057788abe79b9fbf143b981ea635dc238925bdaf04`; candidate pack SHA-256 `512b06b8f847caac98e53059570e5473017cb8da2a9620ae394fd9fd02d5102e`.
- Authorization check: 0 matching `S3-SEMANTIC-GROUNDING-V2-FALLBACK` authorizations; 94 non-matching authorization/contract records were seen and rejected. Existing S2.12/GDPR authorizations are explicitly not reused.
- Arm C status: **IMPLEMENTED_READY_FOR_AUTHORIZATION**; real API calls = 0.

**Paths**
- `outputs/reports/s3_semantic_grounding_v2.{json,md}`
- `outputs/reports/s3_semantic_grounding_v2_arm_comparison.{json,md}`
- `outputs/reports/s3_semantic_grounding_v2_llm_preflight.json`
- `outputs/reports/s3_semantic_grounding_v2_llm_authorization_request.{json,md}`
- `outputs/reports/s3_semantic_grounding_v2_llm_mock_execution.json`
- `outputs/evidence/s3_semantic_grounding_v2/{manifest,metrics,predictions,artifact_hashes,llm_fallback_candidate_pack_v1,llm_preflight,llm_authorization_request_v1}.{json,jsonl}`
- `src/bpc_hybrid/s3_semantic_grounding_v2.py`
- `src/bpc_hybrid/s3_semantic_grounding_llm_v1.py`
- `scripts/run_s3_semantic_grounding_v2.py`
- `scripts/run_s3_semantic_grounding_llm_v1.py`
- `scripts/build_s3_semantic_grounding_llm_authorization_v1.py`
- `configs/stage3_semantic_grounding_v2.json`
- `tests/test_s3_semantic_grounding_v2.py`

**Boundary**: development-only synthetic panel; not formal Oracle, not human Gold, not native Winter/Sun capability for the four extension types. The LLM arm has no real-run metrics.

## 0. Latest revision: s3_semantic_grounding_v1 (2026-09-12, zero API)

**Status**: VERIFIED_PROJECT_FACT (development-only synthetic controlled panel). The real API is not authorized; the strict LLM semantic-grounding fallback is **IMPLEMENTED / NOT REAL-RUN** (0 calls, 0 network).

**What changed (new implementation only; no frozen evidence overwritten)**:
- New deterministic-first module `src/bpc_hybrid/s3_semantic_grounding_v1.py`: multi-signal top-K action grounding (`resolved/ambiguous/unresolved`), action-anchored local BPMN surfaces for condition/constraint/exception, explicit `observable absence` vs `unobservable`, and programmatic final decisions.
- New runner `scripts/run_s3_semantic_grounding_v1.py`, config `configs/stage3_semantic_grounding_v1.json`, focused tests `tests/test_s3_semantic_grounding_v1.py`.
- New revision artifacts only: `outputs/development/s3_semantic_grounding_v1/`, `outputs/evidence/s3_semantic_grounding_v1/`, `outputs/reports/s3_semantic_grounding_v1.{json,md}`.
- Frozen original-three evidence and `src/bpc_hybrid/sun_stage3/sun_scorer.py` are hash-verified against the C36 manifest; the historical `s3_formula_repair_v2` artifacts are byte-unchanged.

**Deterministic result (reference/winter similarity backend, 40 variants + 40 controls)**:
- Unified variant evaluation: 4-type Macro-F1 **0.5886**, exact type accuracy **0.5750**, unobservable **7**.
- Per-type binary structural checks over all 40 variants: Macro-F1 **0.5619** (prohibited 1.0000 / condition 0.5143 / constraint 0.3333 / exception 0.4000).
- Target-field diagnostic (only the expected mutated field is scored on each pair): Macro-F1 **0.6737**, control target false-positive rate **0.025**.
- Paired 80-object view: 5-class Macro-F1 **0.4246**, 5-class accuracy **0.3500**, control any-type FP rate **0.5500**, paired accuracy **0.1250**, unobservable **20**.
- Baseline comparison against C36 `reference/winter`: unified variant Macro-F1 0.4738 -> 0.5886 (+0.1148), exact 0.4250 -> 0.5750 (+0.1500); paired 5-class Macro-F1 0.3900 -> 0.4246 (+0.0346); paired accuracy 0.2250 -> 0.1250 (-0.1000, documented trade-off).

**Root-cause treatment**:
- Action grounding no longer uses a single top-1 hard threshold only: top semantic candidates, top lexical-coverage candidates, exact normalized labels, actor/ownership context and top1-top2 margins are recorded; ambiguous/unresolved action grounding no longer becomes a violation.
- Condition/constraint/exception checks consume finite action-anchored subgraphs. `not_enforced`/`not_handled`/missing-numeric-bound are emitted only for closed local surfaces; a non-matching conditionExpression or a dedicated but semantically ambiguous handler blocks a negative verdict.
- The explicit numeric time-limit contradiction path is retained and was tested on 72h vs 48h/96h. Unsupported abstract constraints (`without undue delay`, `without hindrance`, clear-language/form/usage restrictions) stay ambiguous/unknown; no `1 - similarity` logical verdict is reported for them.

**Scientific limitation (must be reported with the metrics)**:
- The frozen panel has **7 byte-identical variant-input collision groups containing 28 variants** because different target controls added different mechanisms on top of the same source BPMN. A single-side deterministic method must make identical predictions inside a collision group, so the unified single-label accuracy has a structural ceiling below 1. The per-type binary-check and target-field diagnostics are the valid type-level views; the paired unified number is retained only for comparability with C36.
- Exception recall remains limited by action grounding (`apply`, `referred to`, weak lexical overlap) and by the unresolved `where technically feasible` branch cases; no per-sample rules were added.
- The condition control-target diagnostic contains one known panel artifact: for `syn_v2_required_condition_02` the conditionExpression is attached to the first process flow rather than a locally resolvable action target.

**Reproduce**:
```powershell
python formal_experiment/scripts/run_s3_semantic_grounding_v1.py --overwrite
python -m pytest -q -p no:cacheprovider formal_experiment/tests/test_s3_semantic_grounding_v1.py
python formal_experiment/scripts/audit_project.py
```

**Next gate**: real LLM fallback requires explicit user authorization and a locked call budget. Until then the fallback is only implementation + mock/offline tests; no LLM performance claim is made.

## 1. 当前结论

### 当前派工：CSCWD 收尾（2026-09-12）

**最晚目标已经用户确认**：2026-09-30 交导师完整初稿；CSCWD 2027 于 2026-10-31
截稿（用户 2026-09-17 提供当届通知），2027-01-31 通知结果；具体当届规则见文首核验。
能提前就提前；各项按真实依赖和验收推进，不设固定起止日、月份限制或中途实验停止日。
完整计划、Definition of Done 和反馈映射只在
[`MASTER_PIPELINE.md` 文首收尾 Pipeline](MASTER_PIPELINE.md#cscwd-按依赖推进的收尾-pipeline2026-09-12-修订)。
本表是唯一实时派工入口，覆盖下方较早事件及旧任务表中的「当前下一步」。

| 收尾任务 | 启动条件 | 实时状态 | 本次事实 / 下一步 |
|---|---|---|---|
| SEP-C0 计划修订 | 用户已明确推进原则 | verified（文档范围） | 主 Pipeline、状态和手册改为按依赖推进、尽早完成、逐项诊断修复；撤销中间日历安排。本批未执行实验，Git 备份结果在交接中报告。 |
| S3-V5-RUNNER-INTEGRATION | DS v5 冻结结果与请求包已有 | verified（离线） | 接通 80 条预测及评价，22 对象共享 18 份响应，恢复新增发送 0，42 项相关测试通过；真实调用仍为 0。 |
| S3-C36-TARGET-PAIRED | 冻结 C36 与 v5 预测已有 | verified（v2 门禁，已推送） | 验收护栏与依赖绑定通过；见 outputs/reports/s3_c36_target_paired_v2.*；SEP-C1-A/B 已完成，下一项 SEP-C2。 |
| SEP-C1 写作与比较口径 | 已有方法和案例可整理 | verified：SEP-C1-A+B | SEP-C1-A 已完成：论文 §3.4/§3.5 写入三阶段 I/O 与 SIM r10 成功链/r8 失败链，C42/C43 入主张矩阵；无新实验/API。SEP-C1-B 已完成：前人比较范围、通用题名、八组合消融与预算准备（C44-C46）；该 SEP-C1-B 同批双重复设计的八组合真实结果仍待运行；另 SEP-C3 modular_v1 八格已各执行一次但非同批、无重复，不能混写。 |
| SEP-C2 必要对照与剩余 Direct 批次 | 两方法合同已适配；运行仍需实际证据与适用权限 | 修复组取消；Direct 结果待执行 | v10 衔接报告中 Rules-Only 36 条已验证，Direct 缺完整预测/评价；保留 Direct 36 + GDPR 74 = 110 次既有计划。执行任务按真实账本和现有授权检查，本轮不重验凭据或外部发送状态；不恢复修复组。 |
| SEP-C3 prompt 组合与后处理归因 | 诊断已有；新运行仍需适用授权 | targeted refinement 已收口；八格已执行一次但非同批/无重复；后处理归因仅旧 v6+111 局部；重复运行未完成 | 2026-09-19 完成 A/B/C/D 一次 600-call 开发运行；modular_v1 000-111 已由前批+增量批各执行一次（commit 18f5cf9，1200 completed samples；批次混杂，不能作稳定主效应/交互）；后处理归因仅本地分支 9b50729 覆盖旧 v6+111，其余 arms 未覆盖且 adapter/canonicalizer/validator 子步骤贡献不可独立分离；B 仅研究参照，正式默认仍为 v6；旧 R_C 保留混合结果；五臂 v2 未执行；详见文首、sep_c3_constraint_refinement_v2_semantic_review 与 sep_c3_postprocessing_attribution_v1。 |
| SEP-C4 下游与四类边界 | 案例/开发诊断已有证据；正式运行需上游门禁 | 诊断可推进 / 正式运行 blocked | 正式 Oracle/端到端仍依赖实质门禁；案例与范围诊断及时写入正文，新问题进入对应修复项，不等待日历截点。 |
| SEP-C5 全文 v1 | 已有章节和证据可持续整合 | ready | 现有正文从现在逐段完善，尽早形成可通读全文；必要结果缺口具名列出，后续补证和修复及时回写。 |
| SEP-C6 导师初稿 | 全文 v1 可审阅 | blocked（待全文） | 完成即交付给用户，最晚 9 月 30 日前提供完整初稿，由用户送导师。 |
| OCT-C1–C4 投稿收尾 | 各自反馈、证据和稿件条件满足 | 按子项依赖推进 | 英文、引用和投稿要求可提前准备；反馈到达即修订，核心证据与稿件就绪即复核和交付，不等待十月。10 月 31 日为最晚外部截止。 |

**发现新问题时**：保存失败证据，定位根因和影响，在原任务下记录最小修复与验收标准；
修复后做相关验证、同步正文和状态，完成 Git 备份后继续。只重开受影响部分，复用仍有效的证据。
正确性、公平比较和核心主张的问题优先处理；等待外部依赖时推进不受影响的工作。

**开始下一项时必须保留的事实**：

- Stage 1 已冻结；既有 Stage 2 三方法结果保留为历史来源；Rules+LLM-Repair 已退出
  后续全部实验。当前两方法比较尚需补齐，不等于 S2.13 或 S3.7 已完成。
- 已存文档记录 2026-09-07 授权 S2.12 63 + GDPR 74 次，后续离线准备记录的阻塞为进程环境凭据。
  本次没有调用执行器或检查凭据，**不把历史 ZERO CALLS / 缺凭据当作今天已重新验证的状态**；
  下一运行任务按真实账本和现有授权核验，授权不重复询问，新 prompt 批次不挪用旧额度。
- GDPR 人工规则已发布；33 条旧违规标签与实际规范/活动/流程版本的范围问题仍需区分，
  不能重复要求已经完成的整批人工裁决，也不能把范围未定诊断直接升级为正式 Oracle。
- 最新 SIM 案例的当前说明以 `paper/SIM_CASE_SECTION_v1.md` 和
  `outputs/development/sim_case_c1/run_v1/capsule.json` 为依据；旧主张矩阵/汇报稿中
  「两组都只检出 r9/r10」「五个修复件均有效」等表述不能直接沿用。
  当前 A 组有证据对应参考问题 0 条，B/C 各 2 条；有效修复对照 3 件，另外两件有表示/抽取限制。
- 四类扩展 H 臂有已知路径判断缺陷，属于开发结果；不得用其结果证明机制改善。
  此后 v3–v5 和本轮入口修复均有独立证据，不替旧 H 臂改写历史结果；mock 不产生真实 LLM 指标。

**写作推进规则**：每个最小任务结束就把可用内容写回现有正文、必要时同步主张矩阵，
完成 scoped Git checkpoint；简报只报完成、证据、下一步、阻塞和提交/推送结果。
下一任务：SEP-C2 两方法合同适配与剩余 Direct 比较。C36 v2、SEP-C1-A/B 已提交并推送；规则＋LLM 混合 fallback 不再派发。
完成就推进下一项可执行工作；遇到影响当前结论的问题先纳入修复循环。
不重做项目总评、不另建路线、不自动启动真实 API。

**2026-09-11 四类扩展定位接线修复与证据范围臂（S3-EXTENDED-EVIDENCE-SCOPE，零 API）**：
本批只做用户指定的两个新臂，各跑一次固定面板（160 个新对象预测）；旧 A/B/C、Winter 等按哈希只读复用。
**范围声明：面板已被反复用于开发，结果只能称 development regression，不是独立验证、不是正式 Oracle，
也不是真实法律合规性能。**

- **R1 定位接线（已证实，机制与旧描述不同）**：runner 用 `localize().matched_activity_id` 建候选面，
  检查器内部却调 `resolve_action()`。只读重放 C 臂 scorer 于 80 个单侧实例：**45 个单侧实例
  （变体 19 + 对照 26）候选面以 `None` 建成**，而检查消费了回退活动。`surface_activity_id` 只对 constraint
  面填充，14+14 是**检查引用计数**，不是 28 个独立流程；且回退只在 v3 未满足匹配时发生，不存在
  "面绑 A、检查用 B"的两活动冲突；B 臂原生缺 `matched_activity_id` 字段不是绑定错误。
- **R2 全图候选（已证实）**：传入活动 ID 对 condition/constraint/exception 候选**增加 0 条**
  （`required_condition_01`：25 条 constraint、3 条 exception 全部与目标活动无关，condition 面为空）。
- **R3 缺证据与反证混用（已证实）**：`_missing_evidence` 用 `1-max_similarity`，空候选直接 unknown；
  H 实现 `satisfied/violated/unknown/not_applicable` 四值 + 分离 `applicability` 与 `evidence_status`。
- **R4 上游输入问题（非打分缺陷）**：`required_condition_05` 的规则动作是"删除个人数据"，生成器把条件挂在
  其 `mutation_config.target_activity_id` 所指活动；`exception_not_handled_04` 的 "Paragraph 1 shall not
  apply…" 被冻结抽取器读成 prohibition(action=apply) 且同时读成 exception。本批不修订冻结抽取，
  `target_activity_id` 只作生成器元数据、未当答案键使用。
- **R5 对照范围（评价契约问题，已证实）**：生成器只补目标字段证据，对照报警不等于已证实法律误报；
  作为独立诊断类别记录，未删除/重标任何实例。
- **R6 诊断字段（已证实并修复）**：旧 `comparison_strings` 按类型名查字段导致 condition/constraint/
  exception 记成空串；改用"元素→字段"映射并断言记录文本等于实际消费文本（640 条检查，0 不一致）。
  **诊断修复，不影响预测。**

| 臂 | 变体正确 | 错类 | 明确合规 | unknown | Macro-F1 | 对照报警 | 对照 none | 对照 unknown | 成对 |
|---|---|---|---|---|---|---|---|---|---|
| C（旧，适配层复算一致） | 18 | 8 | 0 | 14 | 0.4896 | 14 | 11 | 15 | **7** |
| W（只修接线） | **19** | 9 | 0 | 12 | **0.5234** | 20 | 7 | 13 | 6 |
| H（W+证据范围与四值判定） | 15 | 8 | 0 | 17 | 0.3517 | 19 | 5 | 16 | 5 |

合并 80 准确率：C 0.3625、W **0.3250（26/80）**、H 0.2500（20/80）。分类别 F1（变体）：
C 0.9524/0.1429/0.5556/0.3077，W 0.9524/**0.3333**/0.5/0.3077，H 0.9524/0.4545/**0.0**/**0.0**。

- **2026-09-11 修订 3.6.54 原位修正（原叙述有误；3.6.55 验收注记再次更正）**：①**撤回"W 有 5 个 prohibited
  变体退步"**——按 accounting 口径 C 与 W 在全部 10 个 prohibited 变体上预测完全相同；旧叙述给出的
  "跨视图混比"**确定归因无留存证据支持，已撤回**。W 的真实差异是 **4 个变体变化 + 6 个对照变化**：
  变体侧 `constraint_violated_05` 正确→错类、`required_condition_05` 错类→正确、`required_condition_10`
  unknown→正确、`exception_not_handled_05` unknown→错类，**正确数净增 1**；
  对照侧 6 例均变为 condition 报警，**总对照报警 14→20，其中 condition 报警 3→9**。
  接线修复的直接作用是 condition 目标检查 TP 1→3。
  ②**unknown / not_applicable 分列**：最终 unknown 是聚合弃权，目标检查不可判定来自可观测性，
  `not_applicable` 是"规则没有该元素"的第三种状态；H 的 not_applicable 只在目标切片之外出现
  （cross-type：condition 7 / constraint 20 / exception 24）。③**撤回"condition TP 3→5 证明机制改善"**：
  H 另有 **27 条 `unconditional_bypass_branch` 记录（12 变体 + 15 对照）**，该判据未证明旁支可绕过条件
  回到目标活动；这 27 条**包含** condition 目标切片的 **5 个条件目标命中**，而**验收方对哈希匹配 BPMN
  的静态遍历显示，对应旁支均无法到达目标活动**（解析原图做静态核查不等于重新推断），对应测试预期也是错的；
  H 保留为**有已知实现缺陷的开发结果，方法验收不通过**。
  ④**运行次数分列（运行量来源＝执行回执）**：尝试 3 次、成功 2 次，**两次成功运行合计 320 个对象**；
  **失败尝试计算量未知**，故**总量至少 320**；最终保留 160 行。"两次成功预测完全相同"无留存证据、
  无法独立核实（第一次成功的产物未保留）。
- **离线验收复算（零推断）**：`scripts/recompute_s3_extended_acceptance_v1.py` 只读已存 JSON/JSONL 重算，
  产物 `outputs/development/s3_extended_acceptance_recompute_v1/`；与 scope 及 accounting 两份已存 metrics
  **逐项一致（differences = 0）**——主表数字本身没错，错在此前的解释与目标字段视图。目标字段视图改为
  "每类 10 目标变体 / 10 目标对照"的真/假/不可判定/不适用分区 + 单列不适用计数，且**不给逐类 P/R/F1**
  （每类仅 10 个标注正例，不可判定既非正也非负，其他类型变体不是人工确认负例）。**停止引用**其中的
  `variant_outcome_by_target_type`：该字段循环写入被覆盖，每个目标类型只剩**最后一个实例**；主表、
  目标分区与成对结果已独立核对通过，**不受影响**。
- **2026-09-11 验收注记（3.6.55）**：旧目标字段视图统计错误的三项已核实成因是 ①正例 False 被误记为 FP
  （W 的 `exception_not_handled_04` 判定 False 即漏检，旧记 `fp=1`）；②目标对照报警漏计（prohibited 的
  3 个目标对照报警旧记成 `tn=3`，未作报警呈现）；③TN 来源错误（condition 的 7 个目标对照阴性旧记
  `tn=0`，constraint 的 `tn=2` 在目标对照分区无对应项）。**撤回**"禁止类退步由跨视图混比产生"这一
  无证据的确定归因。旧产物中的上述错误说明以本注记为准。
- **W 的改善可与接线修复直接对应**：修复后 condition 候选面按最终活动构建，condition F1 0.1429→0.3333；
  代价是对照侧 condition 报警 3→9（总对照报警 14→20）。**W 的退步**：`constraint_violated_05`
  （正确→错类）、`exception_not_handled_05`（unknown→错类）；收益：`required_condition_05`（错类→正确）、
  `required_condition_10`（unknown→正确）。正确数净增 1。
- **H 是相对 W 的退步，不是靠多判 unknown 换低报警**：报警 20→19（−1）、对照明确合规 7→5（−2）、
  对照 unknown 13→16（+3）、变体正确 19→15（−4）、成对 6→5、Macro-F1 0.5234→0.3517；
  H 的 constraint/exception 目标检查在各自 10 个目标变体上真/假均为 0（全部不可判定），
  condition 目标切片 5 真/5 不可判定但**对照侧同样 5 真**、成对 0；该 5 真包含在 27 条
  `unconditional_bypass_branch` 记录内，验收方的静态遍历否定了其绕过结论，故不构成绕过证明。
  如实保留，不继续试参数。
- 产物 `outputs/development/s3_extended_evidence_scope_v1/`（plan/predictions/metrics/diagnostics/manifest）；
  复核 `python formal_experiment/scripts/run_s3_extended_evidence_scope_v1.py --check` 与 `--replay`；
  测试 `tests/test_s3_extended_evidence_scope_v1.py`（22 项，其中 10 项为非面板小流程行为验证）。
  旧产物与绑定实现逐字节保留；`s3_extended_prediction_accounting_v1.py` 未改，新臂经薄适配层注册，
  并与最新修正后的 A/B/C 数字逐项一致。

**2026-09-11 S3-EXTENDED-ACCOUNTING 统计修复并收口**：仅复算已存三臂分数，未运行
检测器或 LLM/API。A/B 原图与变体均按其冻结规则，C 两侧均按声明的比较门，所有指标
只读取一份 240 实例最终预测。A/B/C 对照“误报/判合规/unknown”分别为
24/16/0、20/14/6、14/11/15；成对成功 11/40、11/40、**7/40**；合并五分类
准确率 0.4750、0.4125、**0.3625**，Macro-F1 0.4578、0.4316、**0.4079**。
变体四类 F1 不变（0.5690/0.5233/0.4896）。旧表 B 合规7却成对11、C成对13的
统计及对应优势解释作废，替代结果见 `outputs/development/s3_extended_prediction_accounting_v1/`。
旧输入与产物逐字节保留；开发批次结束，后续优化与正式评价仍需另行任务。

**2026-09-10 真实法条输入上的 Sun×v3 逐条诊断（S3-REAL-RULE-DIAGNOSTIC，零 API）**：
首次把已确认人工法条规则接到 7 张原始 BPMN 实跑。人工 Gold Rule Records（74 句/92 条规范）经既有机械
转换器（**仅 obligation**）转成检查记录，已确认的 3 条文字顺序说明按既有运行时投影为顺序边；
冻结 Sun 与 v3 各跑旧推断输入的 **33 个 item**（指定检查类型），共 **66 条输出**，
预测先落盘、标签后读取。**结果两者完全相同**：missing_action 10 violation + 1 unknown、
incorrect_actor 11 unknown、out_of_order 11 unknown（method_differences = 0）。
映射覆盖按两套口径分开报告（该口径由 2026-09-11 返修修正，见下）：**检查实例引用次数** 84 动作引用 /
13 执行者对引用 / 8 端点引用；**去重后数量** 42 动作要求 / 13 执行者对 / 8 端点。v1 旧写法把引用次数写作
去重数（Sun mapped_unique 1、expression_differs 83、端点非活动 8、规则缺信息 13；v3 mapped_unique 2、
expression_differs 80、结构解析不足 2、端点非活动 7、证据支持判断 14），且把 11 条 mapped=false、
violated=false 的未映射执行者证据计入“证据支持判断”——两项均已作废。**三类主要阻碍**：① article16 无
obligation 子句 → v028/v029/v030 无可检查动作（article20 无 actor → v020/v029 执行者不可观测）；
② 顺序检查缺规则侧关系 → v006/v012/v015/v018/v021/v027/v030/v033 分母为空（9 条法条结构化 order 全为 0，
仅 3 条已确认说明生效）；③ 条件/约束/例外不被冻结转换器消费 → 适用性 not_evaluated（全部 33 项）。
**范围核查 33 项 / 5 组最小问题**：G1 目标 clause 与活动绑定（33）、G2 原图或变体（33）、
G3 证据引用缺失法条 Article 12/19（v018/v021/v030/v033）、G4 v001/v002 与已确认局部通知意见冲突（2）、
G5 缺合规对照（33）。机器只给候选绑定并标注 machine_proposed/human_confirmed=false，未改 Gold、
未新增对照、未切换定义。旧标签诊断仅置于 `legacy_label_diagnostic`（33 项全保留、正例 unknown 计 FN、
scope_unresolved=true、performance_claim_ready=false）：两方法 macro-F1 均 0.3175。
**本轮是 development diagnostic，不是正式 S3.7 Oracle promotion、不是 Gold 发布；合成面板 0.9825 未带入。**
产物 `outputs/development/s3_real_rule_diagnostic_v1/`；复核命令
`python formal_experiment/scripts/run_s3_real_rule_diagnostic_v1.py --replay`。

**2026-09-11 真实法条诊断的限定返修（S3-REAL-RULE-DIAGNOSTIC-CORRECTIONS，零 API）**：只修证据关联、
原因分类与覆盖统计，**不改检查器/Gold/阈值/规则输入/预测**，66 条预测逐字节复用（与 v1 manifest 绑定哈希
一致）。五项修正：① 未映射证据不再算“证据支持判断”——v3 的 13 条 actor-action 对全部为
`linked_action_not_reliably_mapped`，已能完成执行者比较 0 条，Sun 侧记录原生条款级聚合，不再把
`violated=false` 当正向证据；② actor 证据身份加入 linked action requirement，v026/v032 各恢复为 2 条正确
绑定的对（**4 次原生 IncorrectActor 调用**，仅这两个 item×两方法；原生 status/score/denominator/reason
与已存预测完全一致，新增证据标注为 recomputed_native_repair），来源由“首条命中”改为来源列表；
③ 引用次数与去重数量分列，动作/执行者对/顺序端点三类各自给分子分母，去重键显式写出，不同检查上下文的
返回信息分别保留（不再“先写入覆盖后来结果”）；④ 未匹配端点的节点种类记为 **unknown**，不再断称“不是活动”，
并撤销“事件不受支持导致顺序检查无法判断”的过度结论（冻结候选表同时含 activity 与 event）；
⑤ 条件扫描按同一 rule 的**全部句子**聚合，适用性统一记为 `not_evaluated`。修正后仍成立的映射瓶颈：
article16 无 obligation 动作、article20 无 actor、9 条法条无结构化 order（8/11 顺序 item 无规则侧关系）、
条件/约束/例外不被消费。产物 `outputs/development/s3_real_rule_diagnostic_corrections_v1/`；复核命令
`python formal_experiment/scripts/repair_s3_real_rule_diagnostics_v1.py --replay`。

**2026-09-11 S3 扩展实验限定返修：真实 v3 阈值臂、空白规范化隔离臂、比较门后继臂（S3-EXTENDED-REPAIR-V2，零 API）**：
上一轮的"v3+0.4 诊断臂"**从未真正改变 v3 的阈值**——脚本从 Sun 配置读 `gamma=0.8` 构造 `EvidenceChecksV3`，
`ACTION_GAMMA=0.4` 只到外层适配器，产物自身同时记录 `action_mapping_gamma=0.4` 与
`v3_thresholds.gamma=0.8`。因此上一轮"门槛无影响""门槛解释零个失败""30 个失败都由结构拒绝造成"
"误报挤掉两个正确样本""非 None 即检出违规""修复版无指标超过原路径"以及未经对照证明的"结构匹配贡献"
**全部撤回**。本批只读复用旧 Winter / Sun / 旧 v3 / 上一轮修复版，新增一个后继模块、一个统一脚本、
一个测试文件、一个新输出目录，三个臂各跑一次 80 实例（零 API；`plan.json` 在打分前写盘并固定实现哈希；
推断前断言"声明 gamma == 实例 `EvidenceChecksV3.gamma`"且 tau/theta 仍为 0.8，错配即失败）。

| 臂 | 匹配路径 | v3 内部 gamma | 标签回退 gamma | gamma_ext |
|---|---|---|---|---|
| A | v3 结构匹配（真实传 0.4） | 0.4 | 0.4 | 0.5 |
| B | 冻结原始标签 argmax（关闭 v3）+ 双侧空白折叠 | — | 0.4 | 0.5 |
| C | v3 匹配 + 无强制解析 + 比较门（双层配置） | 0.8 | 0.4 | 0.5 |

- **真正修好的执行错误**：①阈值真的传进 v3 实例；②空白不对称——上一轮只折叠规则动作、不折叠活动标签，
  而冻结 GDPR-7 含尾部换行标签（`'Communicate the rectification\n'`），实测 0.282807→0.483290 与
  0.266066→0.466753，0.4 落在两者之间；③v3 返回 `undetermined` 时不再用 argmax 硬选活动，标签回退在最高分
  并列于不同节点时也不选，需要唯一活动的检查一律不可判断；④新增比较门——只有 condition/constraint/exception
  至少一项真正比较过，聚合答案才可以是"明确合规"，否则弃权（禁止动作存在性检查单独说明，不承载合规结论）。
- **三个因果问题**：**①** 真正把 v3 内部阈值改成 0.4：**32/40 行决策改变、25 行预测改变**，21 行金标类型
  由不可判断变为可判断，31 行对照侧分数改变；A 臂变体 **22 正确 / 13 错类 / 4 明确合规 / 1 unknown**，
  Macro-F1 **0.5690**（旧 v3 0.2273、原路径+0.4 0.4738），对照误报 **24**（旧 v3 8、原路径+0.4 20）——
  分数提升伴随更多误报。**②** 只加空白规范化、不用 v3：B 臂与冻结 Winter 臂 **35/40 决策相同**，仅
  **2 行预测翻转**且恰为 `required_condition_10` 与 `constraint_violated_03`，**这 2 例完全由空白处理解释，
  与结构匹配无关**；同时规范化也改了 3 个对照侧分数（B 误报 20 = Winter 20）。**③** 歧义修复：本面板
  **0 行**触发并列或 `undetermined`，"禁止强制解析/禁止任选并列"这条规则**在本面板没有生效，尚不能分离**；
  C 臂相对上一轮修复版的 12 行差异实际来自"双侧折叠 + 比较门"，其中 2 行改对、2 行改为弃权、2 行由
  "误报的明确合规"改为弃权，对照误报 20→**14**、成对 11→**13**，但变体正确 19→**18**（净退步 1）。
- **同口径最终表**（互斥守恒；目标类型不可观测单独统计）：

  | 臂 | A 正确 | A 错类 | A 明确合规 | A unknown | 目标类型不可观测 | A Macro-F1 | B 误报 | B 明确合规 | B unknown | C 成对 | D 五分类 acc / Macro-F1 |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | A（v3 真 0.4） | **22** | 13 | 4 | 1 | 9 | **0.5690** | 24 | 11 | 5 | 11 | 0.4750 / 0.4578 |
  | B（原路径+折叠） | 19 | 9 | 2 | 10 | 16 | 0.5233 | 20 | 7 | 13 | 11 | 0.4125 / 0.4316 |
  | C（后继+比较门） | 18 | 8 | 0 | 14 | 18 | 0.4896 | **14** | 11 | 15 | **13** | 0.4625 / 0.4504 |

  各臂每行都满足 正确+错类+明确合规+unknown=40、误报+明确合规+unknown=40；"目标类型不可观测"是另一列。
  上一轮的脆弱聚合会把 A/B 臂的 5/7 个弃权冒充成"明确合规"，比较门将其改为弃权。
- **替换的错误解释**："v3+0.4 与 v3+0.8 输出相同"来自**参数没生效**，不是"门槛无影响"；误报改变的是**精确率**，
  不改变任何 TP（禁止动作类型各臂 TP 均为 10）；字符串 `none` 是"明确合规"而非检出违规；"修复版无指标超过
  原路径"与 19>17、0.5233>0.4738 直接矛盾，正确表述是"未能在压低对照误报的同时超过原路径"；D1 的判别样例
  改为 `exception_not_handled_04`（v3 未定位却由回退分支给出分数），1.0000 与 0.5040 都高于 0.5，不能证明跨越门槛。
- 产物 `outputs/development/s3_extended_repair_v2_v1/{plan.json,predictions.jsonl,metrics.json,diagnostics.json,manifest.json}`；
  复核命令 `python formal_experiment/scripts/run_s3_extended_repair_v2_v1.py --check`。旧产物与绑定实现逐字节保留，
  旧 manifest 未重绑，旧"v3+0.4"批次标记为"外层记录 0.4、实际 v3 仍 0.8，不能支持阈值因果结论"。

**2026-09-11 四类扩展 Winter-vs-v3 同条件归因与修复（S3-EXTENDED-GAP，零 API）[结论已撤回，保留为历史记录]**：
上一轮只交付了"v3 分数更低、瓶颈在动作定位"。本轮先做**同条件分离**再修**已证实缺陷**，复用全部旧臂
（未重跑 Winter/Sun/BM25/TF-IDF），新增两个臂：`orig+0.4` 重推格（当前代码状态下重新推导，与冻结 Winter 臂
在每一个决策字段上逐项相同，同时校验 0.8 重推能逐字节复现冻结 Sun 臂）与 **`v3+0.4` 诊断臂**
（v3 匹配路径 + 迁移 Winter 冻结 `gamma=0.4`；0.4 是**预先指定的 Winter 配置迁移**，非阈值搜索：
无网格、无逐样本门槛、无按标签选参）。

- **门槛不是原因，它在 v3 路径里根本不起作用**：`v3+0.4` 与既有 `v3+0.8` 的**逐条预测完全相同**——
  每行的分数、可判断性、动作定位记录与最终预测一致，两份文件只差记录用的 `action_mapping_gamma`。
  原因是 v3 的 `structure_not_satisfied` 由结构比较而非 gamma 判定，两个 gamma 下都拒掉同样 30/40。
- **同 gamma 0.4 下结构匹配在伤害定位**：标签 argmax 路径映射 **27/40** 个规则动作，v3 只映射 **10/40**
  （全部是精确标签的 prohibited 插入）；v3 拒掉的 30 条中 26 条 `no_candidate_above_gamma`、4 条
  `structure_not_satisfied`。condition/constraint/exception 的动作门槛就是这个判定，因此这三类在变体侧
  永远不可判断。
- **三个已证实缺陷（逐项产物直接证明）**：**D1** `prohibited_action_present` 报告 v3 的**词元化**
  `candidate_max_similarity`，而冻结公式与 `gamma_ext=0.5` 锁在**原始标签**相似度尺度
  （`prohibited_action_04` 原始 1.0000 / 词元化 0.5040；`exception_not_handled_04` 原始 0.5080 /
  词元化 0.5040——同一个 0.5 落在两尺度两侧）；**D2** 同一条检查里"动作指哪个活动"有两个答案：
  `prohibited_action` 在 v3 未定位时仍回退候选最高分给出分数，`_missing_evidence` 却弃权，于是
  `exception_not_handled_04/05` 被报成 prohibited 违规；**D3** 把"必需动作是否存在"的**验证判定**当作
  四类证据检查的**硬定位门**，法条短语与流程标签对象内容不同时直接掐断全部下游比较。
- **修复臂 `s3_extended_v3_repair@1.0.0`**（`src/bpc_hybrid/s3_extended_v3_repair.py`，子类化
  `V3ExtendedScorer`，只替换动作解析入口）：继承冻结面板/规则绑定/六要素抽取器/四个候选面/四条公式/
  `gamma_ext`/统一五分类/评价器/可判断性策略与 v3 结构化表示；改动三处对应三个缺陷——① prohibited 用本臂
  声明的原始标签公式 `max sim(rule_action, process_activity)` 计分且报告布尔即该分数决策；② 全行**唯一
  动作解析**（v3 满足匹配优先，否则本臂标签 argmax 且需达本臂动作 gamma）同时供分数决策、候选面、证据分数与
  contradiction 门槛使用，解析不到就明确记不可判断；③ contradiction 只经同一解析活动与同一 gamma 可达。
- **同条件结果（互斥计数守恒）**：

  | 臂 | 匹配路径 | 动作gamma | A正确 | A错类 | A弃权 | A判合规 | A Macro-F1 | B误报 | B合规 | B弃权 | C成对 |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | Winter（冻结） | 原始标签 argmax | 0.4 | 17 | 9 | 18* | * | 0.4738 | 20 | 12 | 8 | 9 |
  | Sun（冻结） | 原始标签 argmax | 0.8 | 10 | 1 | 30* | * | 0.2381 | 5 | 9 | 26 | 7 |
  | orig+0.4（重推） | 原始标签 argmax | 0.4 | 17 | 9 | 12 | 2 | 0.4738 | 20 | 12 | 8 | 9 |
  | v3+0.8（既有） | v3 结构匹配 | 0.8 | 10 | 2 | 26 | 2 | 0.2273 | 8 | 6 | 26 | 4 |
  | v3+0.4（诊断） | v3 结构匹配 | 0.4 | 10 | 2 | 26 | 2 | 0.2273 | 8 | 6 | 26 | 4 |
  | v3+0.4 修复 | v3 匹配 + 唯一解析 | 0.4 | **19** | 9 | 10 | 2 | **0.5233** | 20 | 14 | 6 | **11** |

  `*` 冻结臂由冻结评价器原样报告，其 `unobservable` 字段把"明确判合规"合并在内，故这两行无法拆分该列；
  重新推导的行把两者分开计数。
- **改善与回退同时如实报告**：修复臂在 Winter 正确的**全部 17 个实例上仍然正确**（A2 清单为 0），并新增 2 个
  Winter 因 `action_mapping_below_gamma` 弃权而修复臂能判断的实例（`constraint_violated_03`、
  `required_condition_10`）；分类别 F1：condition 0.2353→0.3333、constraint 0.4000→0.5000、
  exception 0.3077 持平、prohibited 0.9524 持平。**代价**：对照误报 **20/40**，比旧 v3 臂的 8/40 明显变差，
  与 Winter 臂持平——这是 D1 纠正后的真实水平，误报来自冻结公式与 `gamma_ext=0.5` 本身
  （在原始标签尺度上把边界标签对判成违规），不是修复引入；换 `gamma_ext` 属于新的预注册，本轮不做。
- **仍未解决**：① 三类证据检查在变体侧仍有 10 例弃权（8 例 `action_not_resolvable_to_activity`、
  1 例 `no_condition_candidates`、1 例 `requirement_evidence_not_satisfied`），即规则动作在流程中确实找不到
  任何 ≥0.4 的锚点；② 证据比较文本与 `gamma_ext` 的尺度口径（候选面混合多来源标签/注释/时间文本）是 v2 之前
  的遗留问题，本轮只披露未改；③ 修复臂没有任何指标超过"原路径+0.4"，即**同 gamma 下 v3 结构匹配在本面板
  可测得的净贡献仅是精确标签层加 D2/D3 一致性**，不得反向表述为结构匹配提升了四类检测。
- 产物：`outputs/development/{s3_extended_baseline_04_v1,s3_extended_v3_gamma04_v1,s3_extended_v3_repair_v1}/`
  （各四件含 manifest 与实施哈希）；证据 `outputs/evidence/s3_extended_gap_v1/`
  （`comparison_v1.json/.md`、`difference_lists.json`、`method_change_note.md`、`manifest.json`）；
  复核命令 `python formal_experiment/scripts/build_s3_extended_gap_comparison_v1.py --check`、
  `.../build_s3_extended_gap_evidence_v1.py --check`、三个臂各自的 `--check`。
- **边界**：development-only 受控面板；四类仍是项目自定义扩展，不是 Winter/Sun 原生能力，也不得改称
  "我们的方法"；旧 v3 0.8 配置与产物逐字节保留；未改 Gold、面板标签、历史结果、Sun/Winter 本体与冻结公式。

**2026-09-11 四类扩展的 v3 方法臂（S3-EXTENDED-V3，零 API）**：把既有 v3 动作匹配接到四类扩展检查上，
在**同一冻结面板**（40 变体 + 40 既有对照，每类 10 对）与 `s3_formula_repair_v2` 的 reference 规则来源上
完成一次真实比较。薄适配层 `src/bpc_hybrid/s3_extended_v3_adapter.py` 只替换动作定位（v3
`action_match` 取代 `ExtendedViolationScorer._best_action` 的纯相似度 argmax）：四类公式、`gamma_ext`
决策规则、冻结评价器均未改；定位出的**同一个活动**供分数门槛、exact-contradiction 门槛与
condition/constraint/exception 候选面共用；v3 的唯一匹配/歧义/明确不满足三分语义保留（歧义与不满足保持
不可判断，布尔结果不写成 1.0/0.0）。**结果（同口径四视图，A 变体 40 / B 对照 40 / C 成对 40 / D 合并 80）**：
新臂 A Macro-F1 **0.2273**（Winter 0.4738、Sun 0.2381），四类中仅 prohibited F1 0.9091（10/10 命中，
2 个错误类型），condition/constraint/exception 三类仍全为 0；B 误报 8/40（Sun 5、Winter 20）、明确合规 6、
不可判断 26；C 成对成功 4/40（Sun 7、Winter 9）；D 五类 Macro-F1 0.1833。Sun→v3 逐项：unknown→正确 0、
unknown→错误 0、正确→错误/unknown 0、保持 unknown 26、保持正确 10、其他 4。
**低分卡点（有数量）**：30/30 个 condition/constraint/exception 变体在**动作定位**这一步就被挡住——
涉及 14 个不同的规则侧动作短语，最佳候选相似度 0.3177–0.6683（全部低于冻结动作 gamma 0.8），
26 个 `no_candidate_above_gamma`、4 个 `structure_not_satisfied`，且 **0 例**由 v3 结构层级打开了纯相似度
门槛关着的门（`matched_with_similarity_below_recorded_gamma=0`），即 v3 的结构匹配未能补偿规则短语与
流程标签之间的语义落差（例：`have the right to obtain from the controller confirmation …` → 最佳候选
`Retrieve available data of the data subject` 0.6341；`apply` → `Ask consent` 0.5040）。产物
`outputs/development/s3_extended_v3_v1/`；复核命令 `python formal_experiment/scripts/run_s3_extended_v3_v1.py --check`。

**2026-09-10 动作表示与候选匹配 v3（S3-ACTION-MATCHING-V3，零 API）**：在同一冻结成对面板上
只改动作表示与候选匹配（新增 `src/bpc_hybrid/s3_action_matching_v3.py`，继承 v2）。
已确认并处理四个问题：**嵌套动作丢失**（`rectify/access/erase` 为 `acl` 槽位动词，被 v2 对象
过滤掉后三个候选对象证据相同而并列 unknown）、**动作关系被压平**（`Stop running BPs using
withdrawn data` vs `Stop using withdrawn data`）、**单个不匹配候选否决整个匹配**
（加入 `Inspect furniture` 后原匹配翻成冲突）、**语义角色互换未识别**
（`from Alice to Bob` vs `from Bob to Alice`）。v3 表示主动作＋对象＋嵌套动作
（verb/objects/slot/span）＋介词角色绑定＋否定/数量，并记录原文 span。
真实结果（落盘预测复算）：macro-F1 **Sun 0.7874 / v2 0.9630 / v3 0.9825**；unknown **0/2/1**；
成对成功 **16/28、26/28、27/28**；v3 逐类 missing_action 0.9474（TP9 FP0 FN1 TN10）、
incorrect_actor 1.0000、out_of_order 1.0000；**v2 正确而 v3 错误/unknown 0 项**，
v2 错误而 v3 正确 1 项。两个原 unknown：`syn_missing_action_04::variant` 根因为嵌套动作丢失
→ unknown→violation；`syn_missing_action_06::variant` 根因为关系被压平，v3 判为包含关系
（候选是要求结构的成分）→ 仍 unknown，且按契约解释未裁定处理。**契约解释问题**：面板契约
只定义"指定结构化活动是否存在"（定义 A），未定义"等价业务效果活动"（定义 B）；
`syn_missing_action_06` 的等价性无法由既有定义裁定，分母与契约均未改，该项计入漏检。
有效契约仍 28/30、28 对、56 实例；v1/v2 列为复用已验证预测（哈希绑定校验后引用，未重跑）。
产物 `outputs/development/s3_action_matching_v3/`；复核命令
`python formal_experiment/scripts/run_s3_action_matching_v3.py --replay`。

**2026-09-10 开发检查器动作匹配缺陷修复与复测（S3-ACTION-MATCHING-V2，零 API）**：
只替换动作匹配策略、其余检查逻辑不变，在**冻结的上轮成对面板**上复测（固定 30 变体、
**有效契约仍 28**、未解决仍 2、28 对、56 个检查实例；未改分母、未修两个无效 actor 变体）。
已确认缺陷：v1 把“完全匹配”和“同谓词＋共享内容词”都赋 1.0 因而并列判为歧义；其内容词集来自
词性分析，短标签下**动作首词被标成 NOUN 进入内容词集**（实测共享集 `['retrieve']` 即动作词本身），
于是“共享动词”伪装成“共享业务对象”；删除真正目标后，同动词异对象的剩余活动仍得 1.0 并产出
`satisfied`（`syn_missing_action_01::variant`）。
v2 新增 `src/bpc_hybrid/s3_action_matching_v2.py`（`s3_action_matching@2.0.0`，仅继承并覆盖
`action_match` 及内部辅助函数）：唯一完全匹配（NFKC＋casefold＋空白规范化）优先于一切近似匹配；
不同活动 ID 的同名标签仍歧义；对象证据排除动作头词、动词与主语类槽位；同谓词但对象互斥（或数字／
否定不同）判为冲突；部分重叠保留 unknown；不新增词表、ID 特判或白名单。
真实结果（由逐项预测复算）：macro-F1 **Sun 0.7874 / v1 0.7579 / v2 0.9630**；总 unknown
**0 / 19 / 2**；成对成功 **16/28、17/28、26/28**；v2 每类 **missing_action F1 0.8889（TP8 FP0 FN2 TN10）、
incorrect_actor 1.0000（8/0/0/8）、out_of_order 1.0000（10/0/0/10）**。
19 个 v1 unknown 中 **18 个转为正确判断、0 个转为错误、1 个仍 unknown**；“目标删除却判满足”的
漏检由 3 项降到 1 项（2 项纠正为 violation）；**回归 0 项**。残余 2 个错误：
`syn_missing_action_06::variant`（部分对象重叠→unknown）与 `syn_missing_action_04::variant`
（不同活动具有相同对象证据→unknown）。A／B 两列复用上轮已验证预测并做绑定校验，未重跑；
本轮属**固定开发集回归与机制改进证据**，不是独立测试集泛化结论，也不声称优于 Sun 整体方法。
产物 `outputs/development/s3_action_matching_v2/`；复核命令
`python formal_experiment/scripts/run_s3_action_matching_v2.py --replay`。

**2026-09-10 S3 三类检查成对受控机制实验（S3-PAIRED-MECH，零 API）**：为中期汇报提供
可直接引用的机制证据。固定 30 变体面板的每个变体配一个原图局部对照 → 30 对、每类 10 对；
契约由原图结构与冻结目标元数据在**推断前**导出并锁定：**有效契约 28、未解决 2**
（`syn_incorrect_actor_03/04` 注入的 lane 名称等于既有 pool `Data Controller`，所有权标签集
未变，不构成可靠正例；两项样本保留、原因记录、未删除未补写）。检查实例 56、逐项预测 112 行。
两个检查器 `sun_2024_frozen` 与 `evidence_checks_v1` 使用完全相同的局部合成要求、原图/变体、
Stage 1 解析、NLP、tau/gamma/theta=0.8 与评价口径。真实结果：macro-F1 **0.7874 vs 0.7579**、
成对成功 **16/28 vs 17/28**、总 unknown **0 vs 19**（全部为近重复标签引起的中止）；
incorrect_actor 上 Sun 对照误报 7/8（成对 1/8），EvidenceChecks 对照误报 0（成对 6/8）；
out_of_order 上 Sun 成对 10/10，EvidenceChecks 6/10（4 对中止）。
**结论是诚实的“无整体提升”**：动作名称直接取自原图，本实验排除了法条语义映射难度，
只验证检查机制；真实法条映射与旧 33 条评价范围问题均未解决。
产物 `outputs/development/s3_paired_mechanism_v1/`；复核命令
`python formal_experiment/scripts/run_s3_paired_mechanism_v1.py --replay`。

**2026-09-10 S3.7 零分根因核实与开发修复**：`outputs/reports/s3_evidence_repair_v1.{json,md}`
及对应 manifest 已生成。此前“确认材料没有顺序信息”的说法不准确：结构化
`order_relations` 确为空，但原样保留的 `temporal_suggestions` 含 **3 条已确认文字顺序说明**。
新运行时转换只接受明确方向、同句唯一原文端点，恢复这 3 条边，端点不新增为必须执行的动作。
新开发检查器 `src/bpc_hybrid/s3_evidence_checks_v1.py` 区分满足/违规/无法判断，
空关系或未映射端点不再返回数值 0；增加同谓词+内容词的可追溯匹配，执行者按匹配活动及
lane/pool 检查，不将业务对象当执行者。冻结 Sun 实现、阈值、Gold 和旧报告均未改。

**必须先解决的评价问题**：旧 33 条输入未绑定目标活动/规范片段/变体，且全部是正标签。
`v018/v021/v030` 的说明依赖未输入的 Article 12，`v033` 依赖未输入的 Article 19。
用户已确认的局部通知意见认为动作存在、执行者正确，与 `v001/v002` 旧标签的范围尚未对齐。
新检查器在该局部活动上给出动作/执行者均满足，与已确认意见一致；不能据此替换整条法规 Gold。
**旧 33 条分数目前只作范围待核实的诊断，不作为分类性能、正式 Oracle 或端到端提升证据**。
复算保留全部样本：Rules-Only 和全情态人工输入仍为 macro 0.3333，双方有 22 条无法判断；
义务输入人工臂为 0.3175。未以提高分数作为修复验收条件。23 项独立合成/产物绑定测试通过，
确定性重放与全量验证在本次日志中记录。下一步需要明确原图/变体和每条判定的检查范围。

**2026-09-09 收尾五步已落地（零 API，真实调用仍为 0）**：

1. **正式 Gold Rule Records 已发布**：用户确认的 74 句 / 92 条规范经机械无损转换
   为 `data/gold/stage3/gdpr7_gold_rule_records_v1.json`（独立 verifier 32 项通过，
   15 项聚焦测试；多情态句不再取首项压平）；配套 Stage-3 胶囊
   `data/predictions/gdpr7_human_rule_record_v1/`。复核命令：
   `python formal_experiment/scripts/verify_gdpr7_gold_rule_records_v1.py`。
2. **人工规则已接入检查器**：`gdpr_capsule_converter@1.3.0` 允许第三个 schema；
   `run_gdpr_3type_linkage_v1.py --arm human_rules` 与四类面板 `human_rules` 来源
   可用（92 条规范全部进入检查器）。
3. **Oracle 隔离运行已跑**（`outputs/reports/s3_oracle_gold_rules_v1.{json,md}`）：
   33 条人工 Gold 上 oracle macro 0.3333（missing_action P/R/F1=1.000）、
   obligation-only 0.3175、dev 参考臂 0.3889；incorrect_actor 11/11 与
   out_of_order 11/11 不可观察（根因：完整法律短语动作映射 < gamma 0.8；确认条目
   无 order_relations），不可观察按 FN 计入分母，不置零。
4. **真实 LLM 批次离线准备完成、真实调用仍 0**：
   `outputs/reports/s2_llm_batches_offline_readiness_v1.json` 记录 63 + 74 声明调用数、
   授权/合同/预检资产齐备、GDPR 74 次假传输 74/74 且零计费、三类拒绝路径全部
   fail-closed。**唯一阻塞 = 进程环境凭据缺失**（预检 5 项 FAIL，含 API key absent）。
5. **下游配对比较已跑**（`outputs/reports/s3_downstream_paired_v1.{json,md}`）：
   同一冻结 Stage 3 下 rules_only 与 human_rules 均为 macro 0.3333 / exact 0.3333 /
   detected 11（Δ=0）；direct_llm 臂 blocked（胶囊不存在，不插值）。四类合成面板对
   人工规则臂有偏差（绑定 dev 抽取 + first-valid-span 投影），已在报告显式披露。

**诚实边界**：本轮**没有**证明“人工规则优于非 LLM 基线”，也**没有**证明方法优于
Sun；正式 S3.7 Oracle 主表、S2.13 冻结、S3.4-S3.6 正式 promotion 均未完成。

**已废弃 capsule 的生命周期语义**：v1–v8 transition 与 S2.11/G0.5 pre-authorization
capsule 的 builder 按设计在磁盘出现任何 `rule_record` 命名文件时 fail closed；正式
Gold Rule Records 发布后，这些 capsule 那些“builder 可重跑 / verifier 通过 / 无
Gold Rule Record”的测试已不可能成立。它们现在在 `tests/conftest.py` 中带显式理由
skip（保留可审计、不删除不弱化）；当前状态真值由 successor v9 的 9 项测试断言。
另有 1 项 v7 superseded-asset 绑定失败为**发布前既有漂移**（v7 manifest 记录的 v6
测试文件哈希与任何已提交版本都不匹配），同样记录在案。

**过渡核账已刷新为 v9**（`outputs/reports/s2_13_s3_7_transition_readiness_v9.json`，
verifier 全过）：v8 的 Gold-Rule-Record 缺失判断已被“已发布 + 独立 verifier 通过 +
完整绑定”取代；v9 不再重跑历史 verifier（它们按设计对后续合法状态变化 fail closed），
改为按哈希逐字节绑定 v1–v8 资产；v8 及更早 capsule 逐字节保留。**并修复一处行尾
可移植性问题**：
`data/predictions/b0_formal_arm_v1/predictions.json` 在 `core.autocrlf=true` 下被检出为
CRLF，使该正式 arm 的 raw SHA 与 manifest 不符并导致 `final_experiment_ready=false`；
按既有窄口径在 `.gitattributes` 加单文件 `text eol=lf` 钉并重新检出后恢复
`fa94991d…`，`verify_b0_formal_arm_v1.py` VERIFIED、`integrity_pass=true`。
未改动任何实验数据、Gold、指标或方法。

**2026-09-09 GDPR 人工确认已导入**：用户收到两份预填稿后明确回复“可以我已经进行人工确认完毕”。
原稿与 `a1a93e7` 所交付字节一致，按当前内容确认；事件
`data/development/human_review/gdpr7_prefill_confirmation_20260909.json` 绑定两稿、机器底稿与输入哈希。
当前人工值入口为 `data/development/human_review/gdpr7_human_confirmed_v1/confirmed_rule_items.json`：
**74/74句、92规范条目、552个要素决定、320原文锚点**；往返对账验证不丢失情态、坐标、关联或说明。
案例4项意见按稿确认；整图合规、原Gold检查范围、延误计时器与主通知期限的疑点按原意保留，
不自动变成 none/timeout 标签。旧稿与旧v1/v2裁决面不覆盖，其0/74是旧入口的历史状态。
当前复核命令：`python formal_experiment/scripts/import_gdpr7_confirmed_prefill_v1.py --check`。
该目录为已确认人工输入；正式 Gold Rule Records 已由其派生发布（见上），
Oracle 隔离运行已跑，正式 Oracle 主表与真实API仍待门禁/凭据；既有Gold/结果不改。

**历史：2026-09-08 GDPR 人工候选预填（已由上方2026-09-09确认导入推进）**：
9 条款/74 句均已逐句准备，共 92 个建议条目、320 处原文字符锚点；入口为
`data/development/human_review/gdpr7_ai_prefill_v1/请检查并修改这份预填稿.md`，
同目录 `proposals.json`/`manifest.json` 为来源绑定底稿。每句含中文释义、六要素、
歧义/上下文/顺序说明及空白人工修改栏。旧候选、v1/v2 decisions、Gold 和方法预测不改；
人工确认 0/74，未冻结、未导入、未增加实验 API 调用。复合情态与重复短语坐标完整保留，
当前 v2 导出器的取首标签/唯一出现定位不足以无损导入本稿，人工确认后不得静默降级。
另有 `data/development/human_review/gdpr7_case_ai_prefill_v1/论文案例人工核对预填稿.md`：
案例选择、原流程局部/整体合规范围、合成对照期限绑定、第22条争议共4项，全部待确认。
直接读图发现 `72 hours` 属于延误说明子流程；不可直接据此确认主通知按时完成。
原图通知活动/执行者的局部判断与既有 v001/v002 检查范围需人工核实，未改已有 Gold。
预填文件可先供用户核对。两项假响应 CLI 固定时钟改动已随 `53d91c7` 保存；本轮继续
补全脚本化假响应测试的默认时钟，修复峰期发现的另外 7 项时间依赖，并在一个正向测试
中主动模拟峰期系统时钟；显式跨入峰期的拒绝测试、真实执行器/预算/低峰限制保留。
Task A+B、C、D 已分别由另一任务提交为 `4abc0ee`、`2859f4b`、`53d91c7`。
本轮将上述 AI 候选稿按用户常设 Git 保存要求显式纳入版本控制（另一任务此前仅为避免
代提交而把它忽略；此处仍是待人工确认的公开法规候选，不是人工 Gold）。

**2026-09-08（Task A–D 已分批验证并提交；离线时钟剩余修复随预填交付核查）**：
用户 2026-09-08 复核确认四个问题并指示修复；全部离线完成（零 LLM/API）：
(1) **Task A 行尾指纹修复**：`formal_experiment/.gitattributes` 对授权绑定资产加窄范围
`text eol=lf` 钉（run_s2_12×2、s2_12_execution.py、授权原句 txt、basis JSON、5 个授权事件
文件），工作区字节归一为 LF；LF blob 与授权内嵌指纹一致（`verify_s2_12_authorization_files_v1.py`
70/70 PASS；此前 core.autocrlf=true checkout 把 LF 资产转 CRLF 致 5 stage runner-hash
mismatch，已消除）；新增回归测试断言钉住文件在 checkout 后仍为原始 LF 字节。
(2) **Task B 运行文档修正**：§13.3 改为 flat 键全集 + `PROVIDER=openai_compatible`（枚举白名单；
实测单独 `BPC_HYBRID_DeepSeek_*` 前缀无效——无 PROFILE 时不参与解析）+ 离线预检工具
`scripts/check_api_env_ready_v1.py`（不打印密钥/不读 .env；实测缺项即 exit 2 并列出）；命令改为
在 `formal_experiment/` 工作目录执行（相对路径全部落在活动范围内）；§13.4 落实为可执行步骤。
**当前唯一缺项=进程环境密钥值**（由宿主/仓库外 env 文件注入；非敏感配置已全部补齐并实测）。
(3) **Task C 裁决结构 v1.1**：v2 editable（schema `gdpr7_six_element_review_editable@1.1.0`，
`data/development/human_review/gdpr7_six_element_review_decisions_v2.json`，74 句/9 条款/
identity 与 blank 一致；v1 文件 byte-exact 保留）新增 rule_items（多规范元素，每项六块全决）、
actor_action_map（隐含 1:1 + 显式跨项边）、order_relations（句内动作先后）；导出
`export_canonical_records_v2` 生成 Rules-Only 同形坐标-only canonical 行（telemetry 非静默）；
工具/校验/导入/冻结 schema 分派升级（v1 仍可校验、只读提示升级）；53 项合成测试全绿
（含多执行者×多动作、一执行者多动作、先 A 后 B、无执行者/无顺序、镜像一致性、Stage-3
first-valid-span 消费）。**唯一正式编辑入口=`scripts/gdpr7_review_tool_v1.py`（默认 v2）**；
真实裁决 0/74。
(4) **Task D Direct-LLM 接入 Stage 3**：`gdpr_capsule_converter.py` 双 schema 自动探测
（sun_rule_only/direct_llm 同形行）+ 显式 pin；`run_gdpr_3type_linkage_v1.py` 增 direct_llm
来源（74/74 ok 门控、`--allow-missing-arm`、`--arm all`、changes_vs_reference + 机器 reason
七枚举 `gdpr_change_classifier.py`）；四类扩展链路确认 direct_llm 消费 + 机器 reason；
`run_s3_formula_repair_v2.py`/`reevaluate_s3_extended_unified_v1.py` 来源参数化（统一五分类，
不退回条件性检出旧口径）；promotion 可执行化 `scripts/promote_gdpr7_direct_llm_arm_v1.py`
（真实运行门禁/74 ok/containment/原子发布+promotion manifest，§13.4 闭环）。26 项新测试绿；
修复证据绑定测试按“历史胶囊生命周期”语义更新（漂移集恰为 Task D 声明的 5 个文件，证据产物
byte-exact；successor 正式 repair 运行将再基线）。
**状态**：Task A–D 代码/测试已分批提交（A+B=`4abc0ee`、C=`2859f4b`、D=`53d91c7`）；
真实 API=0（等待进程环境密钥）；裁决 0/74；论文案例注记
`docs/research/PAPER_CASE_SIM_GDPR_PREP_2026-09-08.md` 已备（三层标准答案清单待用户）。

**2026-09-07b 论文收尾授权落地与执行链补齐（零 LLM/API，ZERO CALLS）**：用户论文收尾指令
（句哈希 `27426de7…`，副本 `configs/paper_winddown_api_authorization_sentence_2026_09_07.txt`）
授权 137 次真实调用（S2.12 63 + GDPR 74，独立 cap、off-peak、retry=0）。本轮离线完成：
(1) **授权文件已创建并通过 executor 同款校验**——批 A 五 stage
`configs/s2_12_api_authorization_{D-CAL,D-REST,F-1,F-2,F-3}.json`（USD 1.00/42.09、off-peak_only、
63M/258,048、retry=0）+ 批 B `configs/gdpr7_direct_llm_authorization_event_v1.json`
（scope `gdpr7_direct_llm_v1:74`、74M/303,104/1.31、off-peak 价快照、官方价重验时间戳）；
活动验证器 `scripts/verify_s2_12_authorization_files_v1.py` 70/70 PASS；旧 no_real_auth
verifier 按设计 superseded（历史保留）。(2) **S2.12 执行链补齐**：raw 内容落盘（gitignored）、
transport 失败/usage 缺失事故记账后中止且绝不自动重发、链式 resume 后骨架按完整账本重建；
`finalize_s2_12_arm_v1.py`（正式胶囊唯一发布入口，坐标-only、成本按官方 off-peak 价重算、
fallback 复用 H1 链逐 plan 审计）、`evaluate_s2_12_api_arm_v1.py --arm …`、
`verify_s2_12_api_arm_v1.py`、`s2_12_response_convert.py`。(3) **GDPR 人工六要素裁决工作流 v1**
可用：唯一编辑入口 `scripts/gdpr7_review_tool_v1.py`（进度 74/444）、editable
`gdpr7_six_element_review_decisions_v1.json`、填写后校验/导入/冻结（38 项合成测试；blank 字节未动）。
(4) 官方价格重验（2026-08-17 峰谷方案未变；off-peak 半价）。新增聚焦 60 项全绿 + s2_12 回归
52 passed + 全量 2965 passed/24 skipped（FILE_CATALOG 重建）。**状态**：S2.12=authorized/ZERO
CALLS/READY（真实调用 0，等待进程环境凭据）；S2.13 blocked only on S2.12 DoD；GDPR 裁决工具
已可用（真实裁决 0/74）；S3.7 未动。真实运行命令：`docs/API_AUTHORIZATION_REQUEST.md` §13.3。
本段之前的 2026-09-07（3.6.38）及更早段落为历史结论，保留。

**2026-09-07 Stage 3 根因修复与同输入复算（零 API）**：已修复 Sun Def6 的规则/流程 actor-action 关联、数值时限的动作绑定与适用范围、五分类漏计 abstention/误判合规。原三类 33 条两侧判定不变（reference 0.3889/0.3636；Rules-Only 0.3333/0.3333）。四类 reference macro 更新为 0.4738/0.2381/0.1429/0.3750；Rules-Only 保持 0.3313/0.1875/0/0.3321。既有阈值网格已复算，主聚合不变。当前证据 `outputs/reports/s3_formula_repair_v2.{json,md}` 与 `outputs/evidence/s3_formula_repair_v2/manifest.json`；论文 §7.4.4 与汇报第 9–11 页使用此版本。历史 2026-09-06 的四类参考数字及五分类 P/R/F1 不再作为当前结果。137 次真实 API、人工 Rule Record Gold、正式 Oracle 状态仍未完成。

**2026-09-06c 汇报前收尾（零 LLM/API；统一评价已离线运行，旧结果保留）**：
(1) **统一五分类评价修复并重算**：合规/违规两侧同一确定性决策（不读 expected/gold；
gold 仅预测固定后评价），基于保存分数离线重算 reference 与 Rules-Only 臂（
`scripts/reevaluate_s3_extended_unified_v1.py`）。统一口径 variant-only macro：
reference winter 0.499/sun 0.321/bm25 0.226/tfidf 0.375；rules_only
0.331/0.188/0.000/0.332；wrong-type 不再为 0（reference winter 9、tfidf 1；
rules_only winter 10、tfidf 6）——撤回“P=1/无 wrong-type”；control FP 两口径一致：
reference 0.500/0.125/0.000/0.275；rules_only 0.450/0.050/0.000/0.375
（tfidf 0.275→0.375 升 0.10，“误报未升”撤回）。旧产物保留并标注为“指定类型
条件性检出”。详见 `docs/research/S3_EXT_UNIFIED_EVALUATION_NOTE_2026-09-06.md`。
(2) **原三类衔接已实跑**（33 条人工 violation decision Gold，dev Sun-style 固定
参数；`scripts/run_gdpr_3type_linkage_v1.py`）：参考 macro 0.3889/exact 0.3636 vs
Rules-Only 0.3333/0.3333；missing_action 两侧 11/11；24 同/9 变，唯一翻转 v014；
out_of_order 两侧 0（外部胶囊无 order_relations=缺失输入契约，如实记录）。
(3) **GDPR Direct-LLM 74 臂执行链实现并通过离线假响应全流程验证**（74/74；
`run_gdpr7_direct_llm_v1.py` + 执行合同 + 9 项测试；in-code 硬上限 input 74M/
output 303,104/USD 2.61-1.31；断点/账本/指纹/授权门禁齐全）；真实调用待授权
（合并申请 §11-§12：S2.12 63 + GDPR 74 = 137 calls）。
(4) THESIS §7.4.4/主张矩阵 C30/C34/C35 与 mentor 汇报稿（`paper/MENTOR_REPORT_
CONTENT_2026-09.md`）已统一口径；MASTER 3.6.37。**仍需用户事项仅两项**：API 授权
（137 calls 两笔独立 cap）与 9 段条款/74 句人工裁决（材料已备）；正式 Oracle 未
完成状态如实保留。

**2026-09-06b 论文收尾执行进展（全部零 LLM/API/网络；规则与授权边界未变）**：
(1) **GDPR Stage2→Stage3 成对衔接实验（Rules-Only 臂）已运行并产出真实结果**
（dev/受控合成口径）：句子级 Gold-blind 输入 9 条款/74 句
（`data/input/gdpr7_stage2_input_v1.json`，分句与 S3.9-EXT 锁定绑定 40/40 一致）；
Rules-Only 真实零 API 预测 74/74（`data/predictions/gdpr7_sun_rule_only_v1/`）；
同一固定 Stage-3 四类型检测器消费外部预测（`scripts/run_gdpr_s2_s3_linkage_v1.py`，
失败不回填）：variant macro winter 0.5208/sun 0.1875/bm25 0/tfidf 0.351，对照 FP
0.45/0.05/0/0.375；与参考确定性抽取逐样本变化 7/6/6/4（例：article22 s1 被 B0 判
obligation 使 2 个禁止变体不可观察；tfidf 一例由不可观察变为新检出）。分析与案例：
`docs/research/LINKAGE_RULES_ONLY_RESULTS_NOTE_2026-09-06.md`。
(2) **Direct-LLM 臂**：74 个冻结请求与预算已备（`outputs/reports/gdpr7_direct_llm_preflight_v1.json`），
并入合并授权申请 `docs/API_AUTHORIZATION_REQUEST.md` §11（S2.12 63 + GDPR 74 = 137 calls）；
**真实 API=0，等待授权**。
(3) **GDPR 人工核对材料已备**：`data/development/human_review/gdpr7_six_element_review_blank_v1.json`
（9 条款/74 句，candidate=确定性 dev 抽取，决策全空）+ 验证器 + 中文工作流指南；
正式 Oracle 仍需该人工裁决与门禁（未完成项如实保留）。
(4) 论文六条修正已落地（THESIS_DRAFT/CLAIM_EVIDENCE_MATRIX C32/C33/ABLATION_MATRIX）；
12 页导师汇报内容稿 `paper/MENTOR_REPORT_CONTENT_2026-09.md` 已交付。状态页与主路线
已同步（MASTER 3.6.36）。S2.12/S2.13/S3.7 门禁语义不变：S2.12 两个 API arms 与 S3.7
仍 await 授权/人工前置。

**2026-09-06 撤回说明与研究定位澄清（研究定位以此为准）**：用户澄清此前“直接使用
Barrientos 原始 FULL/NO-PATTERNS 两份提示、在本项目冻结 36 条输入上运行 360 次
（36×2×5）”的方案是对其意图的误解，**已经撤回、不得执行**。研究定位维持：Sun et al.
(2024) 是整体改进对象与三阶段方法主干；Barrientos et al. (2026) 仅作为 **Stage 2 的
方法借鉴来源**（LLM 结构化输出、验证、受控词汇、归一化与评估纪律）；本项目**不承担
“必须整体优于 Barrientos”**，也不把原样运行其原生提示作为正式对照。下列 2026-09-05
段及其入口脚本/独立合同/预检报告/22 项 focused tests（checkpoint `2c5181e`）保留为
历史证据，状态 **withdrawn**——真实 API=0 不变，不再作为待授权执行计划；任何执行需
用户另行明确授权与独立预算。Barrientos 相关已完成证据继续有效、不受撤回影响：
2026-08-29 D/E 1140/1140 真实运行（含 BARR-FULL 原生臂）、2026-08-30 后处理单因素与
450-call Prompt 单因素（AB-1/2/3/5/5b/9 有实测）；AB-4（纯受控词汇）与 AB-10
（style-equivalent 敏感性）仍为未隔离缺口。详细证据梳理见
`docs/research/RESEARCH_EVIDENCE_REVIEW_2026-09-06.md`。

> 历史记录（2026-09-05 原文；2026-09-06 用户撤回，仅存档，不得执行）：

**2026-09-05 S2-BARR-4 原文消融复核与执行准备**：按用户要求收敛到 Barrientos
原文/随附 artifact。已定位第9页词表及PDF/XML两项消融，并核实两份词表提示
实际同时改变“44模式清单+控制流冗余限制”；不再误称纯词表单因素。原生
FULL/NO-PATTERNS 新入口与合同离线准备：36×2×5=360次，USD cap 9.70，retry=0，
无历史基线复用；重点评价名单外模式与命名/可用性，不套用六字段F1。22项focused
测试通过（含360次假响应链、未授权拒绝、账本校验）；**真实API=0，尚待该独立
预算授权，未产生新性能结果**。PDF/XML代码已定位，仍需成对上游输入、可读PDF
模型/文件上传预算及独立Stage 3门禁；未启动。源核对与命令见
`outputs/reports/barrientos_paper_ablation_preflight_v1.md`。已有消融及正式结果未改。

项目目标是完整重建并改进 Sun 的三阶段流程，而不是只做一个 Stage 2 小实验：

1. 完成 Stage 1 流程模型结构与标签语义解析；
2. 在 Stage 2 完成 Sun、传统方法、直接 LLM 和 Hybrid 的同条件比较；
3. 用主数据和更复杂法律语料验证复杂度退化与 LLM 优势边界；
4. 在 Stage 3 完成多 baseline 的规则—流程匹配、违规检测和错误类型分类；
5. 分开报告 Oracle Stage 3 与端到端误差传播，并做 Stage 2/3 交叉消融。

实施顺序锁定为：**先完成 Stage 2，再补齐 Stage 1，最后复现并扩展 Stage 3**。
当前机器合同仍是 Stage 2 优先、Stage 3 固定的阶段性合同；启动 Stage 3 改进前
必须另行修改并审计合同。

用户于 2026-08-01 确认：B0（Rules-Only）采用 `method-level independent
reconstruction` 口径，满足 Sun 核心组件、处理顺序、统一输入输出和统一 evaluator
后可进入正式结论；不再要求作者原代码、原权重、完整私有词典或论文绝对数值一致。
B0-R0–R5 已全部完成（各批次 verified，R5 正式结论包 2026-08-11 交付；Rules-Only 正式 arm 已发布并独立验证）。当前真实主线为：**S2.11/G0.5 外部复杂语料资格与映射 → S2.12 full DoD → S2.13 freeze → 用户裁决并冻结 9 个 GDPR Gold Rule Records → S3.4–S3.6 formal promotion → S3.7 单独授权**；S3.7 授权句仍未生成。

**2026-08-08 导师汇报确认（详见 `MASTER_PIPELINE.md` §8.8）**：
1. **Rules+LLM-Repair（旧代号 H1）不再深究，仅作对照**——全量 150 运行主口径
   F1 0.7621 vs Rules-Only 0.7986（净负），机制正常但 trigger+repair 配方加 FP
   不加召回；S2.8 正式 trigger 预注册取消；
2. **Rules-Only / Direct-LLM 局限性**已列表+举例写入 §8.8.2（含 B0 字段归属错误、
   词典缺口、Sun-marker 口径差异；D1 constraint 召回弱、actor 泛化误抽、保守漏抽）；
3. **命名直观化**：B0→**Rules-Only**（纯规则法）、H1→**Rules+LLM-Repair**（规则+
   LLM 修复）、D1→**Direct-LLM**（直接 LLM）；机器 ID 不变；
4. **与 Barrientos et al. (2026) 严格对比 + 贡献细模块化**：Direct-LLM 拆 8 模块、
   Rules-Only 拆 7 模块；消融矩阵 AB-1..AB-10 待跑（我的模块 vs 换 Barrientos
   模块 vs 去掉模块）；论文方法章节目标 4–5 页。

**2026-08-20 按用户原要求逐项验收（“已记录”不等于“研究已完成”）**：

| 用户要求 | 当前验收 | 证据与剩余缺口 |
|---|---|---|
| H1 不再深究，仅作对照；解释为何差、难点与优化方向 | **已完成** | §8.8.1 已给出全量 150 负结果、actor 过抽、Gold-blind trigger 错位、字段边界约束与仅供未来参考的保守优化方向；正式结论已固定为 comparison-only，不再派发优化。 |
| 列出并举例解释 B0 / D1 局限 | **已完成（实验/证据文档 + 论文回填，2026-08-20）** | §8.8.2、`B0_ERROR_ANALYSIS.md`、`D1_ERROR_ANALYSIS.md` 已有数字和例子；`paper/THESIS_DRAFT.md` §8 已按量化证据逐条回填（Rules-Only 5 类、Direct-LLM 5 类：每条含定量证据/文本例子/错误原因/方法边界/优化方向/为何未继续）；H1 写为负结果对照。 |
| B0/H1/D1 改为直观命名 | **已完成（注册表 + 论文正文迁移，2026-08-20）** | 正式名为 Rules-Only / Rules+LLM-Repair / Direct-LLM，机器 ID 仅为兼容保留；`paper/THESIS_DRAFT.md` 方法标题/正文已改正式名（legacy B0/H1/D1 仅首现映射与 §7.1 模板机器 ID 行、§7.2 正式表附注），PW3 状态更新为 in_progress。 |
| 严格对比 Barrientos、做模块替换/移除消融、把贡献写成 4–5 页 | **1140 次 D/E、零 API 后处理单因素、450 次 Prompt 单因素均已完成** | 2026-08-29 已完成 DeepSeek-V4-Pro-0813 固定计划 1140/1140 调用；2026-08-30 完成严格 Prompt 单因素 450/450（失败0，cost=$3.3650）。同一 0813 模型/同一 EStG-150/Gold/evaluator 下：full F1 0.7719；语义示例替换为结构模板 0.7650（Δ−0.0069，actor Δ−0.1317），支持小幅正贡献；删除详细语义规则 0.7759（Δ+0.0040，action Δ−0.0518），显示字段权衡而非总体增益；删除显式 JSON 纪律 0.7790（Δ+0.0071，合法率仍1.0），当前条件下未测得增益。既有 Barrientos 结果继续分为模块替换、native 评价和共享目标，不跨 evaluator 比 F1；接口不兼容的0分不解释成 Barrientos 普遍无效。报告：`d1_prompt_factorial_results_v1.{json,md}`、`d_no_fewshot_interface_diagnosis_v1.md`、`d_full_postprocessing_ablation_v1.md`。 |

因此，第 4 项的**方法拆分、真实 D/E 数据、后处理单因素和 Prompt 单因素均已有实测证据**。
1140 次运行回答多模块压力、模块替换、Barrientos-native 和共享三类目标；零 API 重放
回答 adapter/canonicalizer/validator；新增 450 次严格单因素回答语义示例、字段语义规则
和显式 JSON 纪律。仍需论文层综合组织以及尚未隔离的 AB-4 纯受控词汇、AB-10 辅助
style-equivalent 敏感性（如决定保留），不能把它们写成已完成。
后续 Agent 不得把 minimal 或模块替换写成一因素内部消融，不得把“已有 1140 次调用”
写成“所有模块均已消融完成”，也不得把 Barrientos 的 native F1 与本文六字段 F1
跨 evaluator 排名。

根据导师最新要求，论文非结果章节从现在与实验并行：先写引言、相关工作、方法、
数据/标注流程和实验设计；结果、摘要结论和“LLM 优势”只保留显式 TODO，直到正式
manifest 解锁。论文工作稿位于 `paper/`，不能反向定义实验状态。

## 2. 当前门禁

| 门禁 | 当前值 | 含义 |
|---|---:|---|
| `integrity_pass` | true | 2026-07-31 G0-EOL-HASH-PORTABILITY 后机器检查通过：合同显式声明 `source_manifest.hash_mode=canonical_lf_utf8_text`，gate 对该受控文本按 CRLF→LF 归一化验证，LF/CRLF 工作树均可验证同一受控内容；未声明资产仍按原始字节 |
| `formal_capsule_versioned` | true | `formal_experiment/` 已进入 Git checkpoint `bfb0b8a`；不代表 input/Gold/结果已冻结 |
| `sun_modality_development_data_verified` | true | S2.1-D 门禁恢复通过；2,831 行 analysis population、quarantine、split 与许可边界均未变 |
| `public_marker_lexicon_verified` | true | S2.3 英文 public-source v1 的 64 个 marker、来源/生成/hash/空扩展表通过离线机器门禁；development-only，未激活 S2.4+ |
| `human_review_input_ready` | true | Layer E 输入门禁已满足；历史 "0/150 可开始"语义不等于当前审核进度 |
| `human_review_freeze_ready` | true | 150/150 adjudicated（2026-08-06 经授权恢复）；freeze validator 通过，仍不足以发布 formal Gold |
| `formal_gold_publication_ready` | **true** | 用户 2026-08-10 按 formal_gold_authorization_packet_v2 授权：stage3.status=locked、publication gate=ready_for_formal_gold_publication（白名单精确匹配）、freeze_policy 重锁（治理/许可/禁止约束保留）；formal Gold 已发布（尚不代表 S1.7/S2.13/Gold Rule-Process Records/Oracle/最终实验完成） |
| `final_experiment_ready` | **true（仅机器门禁）** | 正式方法、冻结输入/Gold 与三方法正式 capsule 机器门禁就绪；**仅代表 Stage 2 三方法正式评价/最终指标机器门禁就绪，不代表 S2.13、S3.7 或完整 MASTER_PIPELINE 完成**（2026-08-15 过渡核账：S2.13 仍 blocked、正式 Oracle 未启动未授权；当前 fail-closed 入口为 `outputs/reports/s2_13_s3_7_transition_readiness_v8.json`，v7 及更早为 byte-exact 历史 provenance） |

每次修改后的最新值以机器检查输出为准；若本表与机器检查冲突，以机器检查为准并
立即修正本页。

## 3. 已有资产与真实边界

| 资产 | 当前状态 | 允许的表述 |
|---|---|---|
| EStG-150 五层审核工作流 | annotation frozen，150/150 adjudicated；formal Gold 已发布（2026-08-10，Gold publication subtask） | LLM-assisted、human-adjudicated Gold；不得在 publication gate 前称 formal Gold |
| 现有 `sun_rule_only` | **B0-R0–R5 全部 verified（2026-08-11）**：`method_conformance_status=verified_method_level_independent_reconstruction`（2026-08-04 用户授权）；`formal_status=ready`、`command_status=formal_ready_candidate_authorized`（2026-08-10 用户授权）；正式 arm 已发布 （`data/predictions/b0_formal_arm_v1`，claim_scope=formal，独立 verifier VERIFIED）；正式三方法比较报告 与正式结论包已交付；`sun_stage2_baseline_not_paper_faithful` blocker 已按设计解除 | 历史 provenance：B0-R0 组件集成 → R1 七子批次实测（ACTION/ALIGN/ACTOR 等）→ R2 method crosswalk → R3 快照（细 Gold F1 0.71865 / 粗 0.7986）→ R4 formal candidate + 方法门禁授权 → R5 正式结论；runner 仍是 development reconstruction，禁止声称 Sun original/exact reproduction |
| Rules-Only（旧代号 B0；BERT-TextCNN + CoreNLP/Tregex/Tsurgeon） | B0-R0–R5 verified（R1 七子批次闭环 2026-08-04；R2 method-level conformance 用户授权 2026-08-04；R3 56d2b03 快照细 Gold F1 0.71865、句子级粗 Gold 主口径 F1 0.7986（2026-08-07 用户决策口径对齐 Sun）） | 允许方法级独立复现（非 exact）；B0 v10 code/config/CoreNLP bridge/runner 已纳入 main，旧 heuristic 不再冒充 B0 入口；audit 区分 component presence（pass: `b0_paper_faithful_components_present`）与 method conformance（pass: `verified_method_level_independent_reconstruction`，2026-08-04 用户授权，见 `configs/methods.json` 与 docs/B0_R2_METHOD_CROSSWALK.md）；441MB checkpoint / CoreNLP jar / Legal-BERT cache 仍为 external runtime prerequisites（未提交、未下载） |
| Rules+LLM-Repair（旧代号 H1；Sun + LLM fallback） | **对照方法（2026-08-08 用户确认，不再深究，§8.8.1）**；development 机制与全量 150 运行（commit 74614e3）：主口径 F1 0.7621 vs Rules-Only 0.7986（净负）、LLM 修复过度抽取 actor（P 0.7077→0.2754、spans 65→167） | runner 强制读取并 SHA 绑定落盘 B0，不再内部重跑；field-level patch 原子应用并记录 accepted/rejected/no-op（103 accepted / 89 changed / gate=True / 0 incidents）；机制正常但 trigger+repair 配方加 FP 不加召回 → 论文中仅作对照臂，不作贡献 |
| Direct-LLM（旧代号 D1；direct LLM） | 历史分支 development run 已登记 P/R；D1-R0 整合 verified、D1-R1 四子批次 verified（150 全量 F1 0.7735、constraint R 0.4172、0 事故）、**D1-R2 锁定 verified（2026-08-06）**（v6 prompt sha 3aa64877 固定、deepseek-v4-pro/temp0/top_p1/4096、预算合同，见 `configs/models/estg150_d1_active_registry_v1.json`）、**D1-R3 快照重跑 verified（2026-08-06）**（细 Gold F1 0.7756 / P 0.8793 / R 0.6938，0 事故）、**句子级粗 Gold 归因 verified（2026-08-07，用户决策口径对齐 Sun，粗 Gold 为主口径）**（F1 0.8726，与 B0 同 Gold 同口径）；**主方法（2026-08-08 导师汇报后确认，§8.8.4）**；**formal arm 已正式发布（2026-08-11，`direct_llm_formal_arm_v1`，zero-API 绑定 D1-R3 snapshot，独立 verifier VERIFIED）；正式三方法比较覆盖 D1** | 可引用为历史开发证据与 D1-R1/R2/R3 development 结果及归因实验；不得冒充当前冻结 capsule 的正式指标；贡献细模块化（8 模块）与消融矩阵 AB-1..AB-10 见 §8.8.4 |
| Stage 1 | S1.1-S1.6 合同/解析/标注协议/评价器资产已从 56d2b03 checkpoint 恢复并重新绑定（2026-08-08）；37 项 stage1 测试全绿；audit pass：`stage1_structural_process_record_verified`/`stage1_label_semantics_p0_p1_verified`/`stage1_annotation_protocol_verified`/`stage1_evaluator_contract_verified`。**S1.5 人工裁决 7/7 批全部完成并正式冻结发布（2026-08-13）**：7/7 records adjudicated、135/135 label fields resolved、7/7 structures accepted_candidate、142/142 human decisions resolved、0 unresolved；七批链式 verifier（blank→b1..b7→磁盘逐位）VERIFIED；用户明确授权冻结（授权 manifest `s1_5_process_gold_freeze_authorization_v1.manifest.json`）；**正式 Stage 1 Process Gold 已发布**（`data/gold/stage1/process_records/stage1_process_gold_v1.json`，独立 verifier `verify_stage1_process_gold.py` VERIFIED）。**S1.3 P2 + S1.6 正式评价（2026-08-13）**：P2=Sun/Leopold-style 方法级重建（跨walk+锁定 config/实现/runtime），P0/P1/P2 正式评价完成（P2 语义 micro F1 0.8185）；**claim 已纠正（2026-08-13 纠错）**：target-overlap 审计（历史 3 条重合、当前 0）+ claim correction v2（target-aware、strict_test_blind=false、held-out 泛化禁止、fixed-GDPR7 描述性组件评价）+ 正式 v2 路径（`data/predictions/stage1_formal_v1/`、`data/results/stage1_formal_v1/`）；audit pass `stage1_formal_evaluation_verified`/`stage1_claim_correction_verified`；**S1.7 正式冻结已完成（2026-08-13 用户明确授权）**：授权 manifest `s1_7_freezer_authorization_v1.manifest.json`（P2 锁定方法/P0-P1-P2 预测/原始指标/Stage 1 Process Gold/评价 capsule 全部冻结；未改 P2、未选择性重算、零 LLM-API、未授权 Stage 3 Oracle）；audit pass `stage1_s7_freeze_authorized`；S3.7 Oracle 仍须经 Stage 3 独立门禁 | 合成 BPMN 上验证的 development 合同与机制；S1.5 正式 Process Gold 已冻结发布（2026-08-13）；S1.3/S1.6 verified（target-aware claim）；S1.7 frozen（2026-08-13 用户授权）；S3.7 Oracle 待 Stage 3 独立门禁 |
| Stage 3 | **S3.1 verified（2026-08-08）**：7 个 Winter-provenance GDPR BPMN 以 byte-exact（LF）恢复至 `data/input/stage1_stage3/gdpr7/`；合同 `stage1_stage3_gdpr7_v1.json` hash 全匹配；`verify_stage1_stage3_gdpr7.py` 通过（7 byte-exact、45 activities、135 blank label fields）；audit pass `stage1_formal_bpmn_membership_locked`（claim=all-seven extension，非 Sun 原 4）。**S3.2/S3.3 decision Gold 已发布（2026-08-10，随 formal Gold publication）**：matching 25 条 + violation 33 条（`data/gold/stage3/stage3_matching_gold_v1.json` / `stage3_violation_gold_v1.json`，与 frozen correction `3310d624…` 一致，冻结 manifest `s32_s33_gold_annotation_freeze_v1.manifest.json`）；**这些 matching/violation decisions ≠ Gold Rule Records**。**S3.4/S3.5/S3.6 development verified（2026-08-08，DEV_ONLY，evidence capsule 已版本化）**：Winter wrapper / Sun Def 4-7 重建 / BM25 v3 + TF-IDF-SVD baseline；**S1.7 依赖已满足（2026-08-13 frozen），formal completion 仍 blocked on S2.13**。**S3.7 formal Oracle 未启动、未授权**（2026-08-15 过渡核账：`formal_oracle_started=false`、`formal_oracle_authorized=false`、`ready_for_oracle_authorization=false`、`authorization_sentence=null`、`no_pseudo_oracle=true`；9 个 GDPR rule IDs article6/7/15/16/17/20/22/33/34 的正式 Gold Rule Records 不存在，本轮未创建/未推断） | S3.1 文件名/hash/claim 已固定；S3.2/S3.3 decision Gold 已发布（非 Gold Rule Records）；S3.4-S3.6 为 development baseline，尚未进入 formal Oracle 主表；正式 Oracle 待 S2.13 + 人工 Gold Rule Records + S3.4-S3.6 formal promotion + 用户单独授权 |
| 正式结果目录 | **Stage 2 三方法正式 capsule 已冻结发布**（`data/predictions`、`data/results` 下 `*_formal_arm_v1`，claim_scope=formal，独立 verifier 全过）；**Stage 3 formal 结果未冻结** | 禁止把 development Stage 3 数字写成 formal；不得声称 Stage 3/端到端最终实验结果 |
| Sun modality development 数据 | verified；2,831 analysis rows | 只允许本地 development 使用；许可未知、禁止再分发，不是 Sun original split |
| public marker lexicon v1 | verified；7/25/19/5/8，共 64 个 | 英文 public-source reconstruction、development-only；不是 Sun original/full lexicon，不能据此训练或评价 |

Sun 最终版、公开数据、引用链和代码来源证据统一放在 `docs/research/`；历史路线和
过期交接统一放在 `_retired/docs/2026-07/`，不得再作为实时指令。

### 3.1 历史分支 D1 Precision/Recall 登记

来源：`experiment/paper-validation-r1` 的 commit `b5f05b8`，run
`s28_s29_deepseek_v4pro_sun_literal_v1`，150 samples，repeat=1。指标文件 canonical-LF
SHA-256 为 `25628188f17eae054b2537aa1f1bef562bcd6a35995b7b03f263e0a1836ab4bc`。

| 字段 | Precision | Recall |
|---|---:|---:|
| Overall | 90.68% | 66.45% |
| Action | 95.02% | 85.02% |
| Actor | 59.42% | 87.50% |
| Condition | 91.11% | 69.16% |
| Constraint | 84.54% | 28.81% |
| Exception | 100.00% | 38.46% |
| Modality evidence span | 97.27% | 90.48% |

口径是 `sun_table8_literal_overlap_evaluation@2.0.0`：statement 级、同字段任意非空
字符交叠、无 clause alignment、无一对一 assignment；`modality` 忽略类别标签，只看
evidence span。Overall F1=76.69%，`invalid_attempt_count=1`。manifest 状态仍是
`succeeded_development_not_formal`；本登记未重跑模型、未调用 API，也未将该结果提升为
当前 formal capsule。

## 4. 2026-09-07 历史工作队列（修复组已取消，当前派工见文首）

当前真实下一路径（2026-09-07b 刷新；S2.11 已完成并发布正式 Gold——见 MASTER
§12.0f/§12.0g 与本页历史行，不再列为待办）：

1. **S2.12 full DoD（批次 A，63 次）**：状态 `authorized (2026-09-07)/ZERO CALLS/READY`
   ——授权事件/auth 文件齐备（§13.3 命令），真实运行只差进程环境凭据。运行序：
   D-CAL → D-REST（链式 resume）→ F-1/F-2/F-3（链式）→
   `finalize_s2_12_arm_v1.py --arm direct_llm|sun_llm_fallback` →
   `evaluate_s2_12_api_arm_v1.py --arm …`（同 Gold/分层/同一 evaluator）→
   三方法总体+分层（L1/L2/L3；L3=0 如实）+模态/要素/完整记录/失败分列 +
   错误类型与逐样本变化 → 达到 DoD 后 S2.13 freeze（S2.13 只 blocked on 本项）。
2. **批次 B（GDPR 74 次 Direct-LLM）**：授权事件齐备（scope `gdpr7_direct_llm_v1:74`）；
   真实运行 → development capsule（executor 拒绝写 formal 路径）→ 独立显式 promotion
   至 `data/predictions/gdpr7_direct_llm_v1` → 下游成对比较（33 条人工违规/30 条 v1/
   40 对 v2 分开报告 + control FP + 逐样本变化与来源归类）；不空转等人工 Gold。
3. **GDPR 人工六要素裁决（74 句）**：工具已可用——唯一编辑入口
   `scripts/gdpr7_review_tool_v1.py`（`--next` 逐句；`--progress` 显示 74/已完成/剩余
   与 444 字段进度；`--show <sample_id>`），editable
   `data/development/human_review/gdpr7_six_element_review_decisions_v1.json`；
   校验/导入/冻结配套就绪（合成测试全绿，blank 字节未动）。真实裁决完成数=0/74，
   等待用户核对（每句可看原句+候选+提示后 a/r/e 确认或修正；不得由 Agent 代填）。
4. **Direct-LLM 接入原三类/四类扩展的最小适配**（真预测产生后执行）：3-type converter
   schema 参数化 + runner 第三来源；统一评价加 direct_llm 来源；阈值/优先级单点核对
   （γ_ext 文档矛盾修正）；变化原因“抽取/适配/检测”机器归类。
5. **用户裁决完成后的正式评价链**：校验→导入→生成正式 Gold Rule Records（9 条款/74 句
   对应核验）→ 前置条件全满足后按锁定方案办理 Gold 发布/阶段冻结与 S3.7 正式 Oracle
   授权记录与零 API 运行；Oracle 与 end-to-end 分表；此前不提前标记就绪/完成。
6. **论文案例与交付**：Sun SIM 案例核对结论已备（references 提取文本 §5.4/表13/图10题注；
   “欠款客户领取 SIM 卡”表述本地未找到，以实际文本为准）；推荐 GDPR article33/34
   (gdpr_1) 为主案例锚点、article22 s1 情态翻转作方法差异小案例（标准答案确认项待用户）；
   THESIS_DRAFT/CLAIM_EVIDENCE_MATRIX/MENTOR_REPORT_CONTENT_2026-09 随真实结果回填；
   GitHub main 同步（禁强推）。
7. **真实 API 运行前置**：进程环境凭据（`BPC_HYBRID_DeepSeek_*` 白名单键；runner 禁读
   项目 `.env`）。未就绪时继续完成不依赖真实调用的实现/比较/图表/写作（按 2026-09-07
   指令第九节）。

下表为历史完成记录（provenance）。

| 顺序 | Pipeline 任务 | 当前动作 | 完成信号 |
|---:|---|---|---|
| 1 | P0 / G0.6 | **已完成**：主 Pipeline、日志/检查制度与 Git checkpoint 有回归测试保护；G0-TEST-REAL-BACKUP-SNAPSHOT 后全量测试 0 failed（1048 passed, 24 skipped） | Agent 入口、目录、日志字段和自动检查已固定；checkpoint `bfb0b8a` 可追踪；真实用户备份由 session 级只读快照守卫保护（允许预先非空，要求 session 前后 byte-identical） |
| 2 | S2.1-A | **verified**（2026-07-15 字节核验通过）| raw 字节已 byte-match：size 191,874,718、SHA-1 `0346f84a246b7049d5aef58bcb33471435bee106`、ZIP integrity testzip 通过、3 个预期成员全部存在且路径安全、EStG_raw.txt SHA-256 与 2026-07-11 审计记录一致；许可仍 `unknown_pending_confirmation`（B2 仍 open），B1 已 resolved。S2.1-B 可派发但本轮不实际进入 |
| 2.1 | S2.1-B | **verified**（2026-07-15；R1 contract repair） | 合同/schema/importer/CLI/15 个 synthetic fixtures 已修正：显式 source ID 重复 fail closed；无 ID 时显式 row-index fallback 并入 manifest；normalized-text group-aware split；标签冲突 `label_conflict` fail closed；唯一小类别阈值为 3 个 group；ZIP SHA-1/SHA-256 独立核验；5 个确定性文件含 manifest byte-identical；manifest 不含运行时、self-child 或 placeholder；synthetic one-hot 与 official pending schema 分离。R1 定向测试 54 passed；首次全量检查 840 passed, 22 skipped，0 integrity errors |
| 2.2 | S2.1-C | **verified — R1 pre-result conflict quarantine + development import**（2026-07-16） | raw 2,833 行、CSV 字节和原标签均未修改；只有精确匹配 source/normalized/raw-text hash、row 616/1221、逐行 permission/obligation 标签与 section hash 的唯一 group 被整体 quarantine。主 analysis population=2,831，分布 1190/1273/264/104；train/dev/test=1985/420/426，group-aware、无泄漏、并集完整；七个产物独立重放 byte-identical；sensitivity full-source variant 仅预注册未运行 |
| 3 | S2.1-B-R1 | **verified** | R1 合同与实现缺陷已修复并由后续真实数据与机器门禁回归保护 |
| 4 | S2.1-D / S2.1 | **verified / overall verified** | manifest 路径已项目相对化；独立 gate 交叉验证 ZIP、合同、schema、quarantine、records/splits、membership/artifact hash、ignore 与许可。records/split hash 未变；B2/B3 许可边界仍 open，formal Gold 与 final experiment 不解锁 |
| 5 | S2.2 | **verified（2026-08-06）**：150/150 adjudicated（用户 2026-07-18 裁决经授权从 56d2b03 恢复至活动 v2 文件，freeze validator 通过） | 150/150 adjudicated，freeze validator 通过 |
| 6 | S2.3 | **verified**：`public_marker_lexicon_en_v1` 已离线锁定；64 个 marker、source/manifest/payload hash、空扩展表和机器门禁通过 | 来源、规则、语言、hash 与 dev-only 扩展策略固定 |
| 6.1 | S2.4-S2.6 | **已覆盖（2026-08-11 核账）**：BERT-TextCNN 模态分类、CoreNLP/Tregex/Tsurgeon 抽取与完整 B0 流水线由正式 Rules-Only 方法（MASTER_PIPELINE §8.6）实现并验证；无独立剩余任务 | 正式三方法 capsule 与正式比较报告为证 |
| 6.2 | B0-R0–B0-R5 | **B0-R0 verified**（2026-08-02 commit 之后）：actor_action.py + 12 个 b0_v10 模块 + sun_style/lexicon_v2_runtime + estg150_b0_development v1/v2/v3/v10 + corenlp_runtime/sun_b0/bert_textcnn + stage2_evaluation v1/v3 + 7 个 v2 lexicon 资源 + SunPhraseRuleBatchBridgeMulti.java + sun_corenlp_runtime.json + sun_b0_s26_candidate_B_v1.json + sun_bert_textcnn_s24.json + estg150_b0_enhanced_s27_v10a.json + estg150_b0_v10_preregistration_v2.json + stage2_evaluator_s210_v3.json + stage2_prediction.schema.json + scripts/run_estg150_b0_enhanced_v10_development.py + test_b0_v10_integration_contract.py（15 验收点） 已纳入 main；audit 区分 component presence（pass）与 method-conformance（blocker，必须由 B0-R2 才能解除）；B0-R1 ready（后续 R2/R3/R4/R5 逐批 verified，2026-08-04 → 2026-08-11）；未运行 CoreNLP、未读 Gold/Layer E、未调 API、未改 D1/H1（历史批次当时状态）；先前 6341136 的 B0-R0-C0 仅依赖闭包，状态从误报 COMPLETE 修正为 verified，correction event 已追加。**B0-R1 五批已完成并实测**（2026-08-04，全部在隔离 worktree + 56d2b03 历史输入 + 真实 CoreNLP 下验证，主口径 sun_literal_overlap_evaluation@2.0.0）：R1-A..C3（token-safe span）→ E1/E2（主口径 evaluator + v10a/C3 重评：F1 0.71019/0.71024，旧 0.5398→0.5326 推翻）→ ERR（错误分析文档，docs/B0_ERROR_ANALYSIS.md）→ **ACTION**（F1 持平，质量收益：主语吞并 8→0、strict-exact 3×）→ **SCOPE-DISAMBIG**（候选实测 −0.0005 拒绝回退，记方法局限）→ **ALIGN**（伪 validated 消除 DoD 达成，主口径不变，label 面板 −0.48pp 记录代价）→ **BRIDGE**（`<`/`<<` 语义测试 + operated 多命中 fail-closed 守卫）→ **ACTOR**（clause 内全 nsubj 弧 + obl/by-to + 中心词词典校验；**主口径 F1 +0.0018，系列首个正向**，actor F1 0.616→0.670，8/8 词典内漏抽找回）。当前 B0-R3 快照细 Gold F1=**0.71865**（P 0.6845 / R 0.7564，用户条件授权为论文依据候选）；**2026-08-07 用户决策：评价口径对齐 Sun 句子级粒度，句子级粗 Gold（609 spans）为主口径，B0 粗口径 F1=0.7986（P 0.7309 / R 0.8801）、D1 粗口径 F1=0.8726（P 0.9012 / R 0.8456），细 Gold 降为对照口径**。B0-R2 method-conformance 已由用户授权解除（2026-08-04，`method_conformance_status`=`verified_method_level_independent_reconstruction`）；LEXICON-DECISION 已实施（2026-08-04 用户授权路径 b，13 名词入词典）；CLAUSE-REVIEW 已复核不改动；C7 过短边界留待正式 Gold 后按需再议。**S2.13 Gold publication subtask 已发布（2026-08-10，发布 manifest outputs/reports/formal_gold_publication_v1.manifest.json，确定性重放 + 34 项验证全通过）**；B0-R4 ready 核账：冻结输入/Gold/共享 evaluator/schema/normalization 齐备（zero-API 满足），剩余 blocker=缺 formal claim_scope 运行入口（现有 runner 硬编码 development）→ 本轮不执行重评；B0-R4 formal candidate **verified**（2026-08-10：Gold-blind runner 只读 formal input v2，150 条全量 + 双跑语义 byte-identical，主口径 F1 0.71865 与 B0-R3 快照逐位一致，promotion 已授权应用（2026-08-10 用户明确授权：methods.json sun_rule_only formal_status→ready、command_status→formal_ready_candidate_authorized，其余未动，零 API））；**B0-R5 verified（2026-08-11，正式结论包 stage2_formal_conclusion_v1）** | B0 方法级实现可重放、B0-R1 确定性缺陷逐批实测（正/负结果均记录）、变更均有日志和 Git checkpoint；修复后低分可作为正式负结果 |
| 6.3 | D1-R0–D1-R5 | **D1-R0 verified**（runner/prompt loader/canonical schema/s28_s29 产物 tracked 可重评）→ **D1-R1 verified**（2026-08-05，四子批次 FIELD-TYPING/PROMPT-CONTRACT/VERIFY-PASS/CLEAN-RERUN 闭环：v6= v5+规则25-27+示例5-6 KEEP；150 全量 0 事故，主口径 F1 0.7669→**0.7735**、constraint R 0.2881→**0.4172**，P 0.8799（−0.0269 披露 trade-off）；空不为错语义，坏 span/clause/边丢弃+审计）→ **D1-R2 锁定 verified**（2026-08-06）：`configs/models/estg150_d1_active_registry_v1.json` 固定 v6 prompt hash 3aa64877（磁盘/loader/manifest 三方一致）、模型钉死 deepseek-v4-pro、sampling temp0/top_p1/max_tokens4096、seed 策略 unsupported_or_omitted、transport 配方（thinking-disabled 无 json_object）、共享输入/evaluator hash、预算合同（逐批授权+`--max-calls` 硬上限 150）；12 项 lock-config 测试含 S2.9 Gold 不可见核查（6 个合成 fixture 与 150 测试句零交叠）；§8.5 S2.9 DoD（D1 侧）达成、整行仍 partial。**D1-R3 快照重跑 verified**（2026-08-06，用户授权 150 calls）：锁定配方逐项一致干净重跑，150/150 有效、0 事故；同一进程双评 R1/R3（sun_literal_overlap@2.0.0）R3 F1 **0.7756**（P 0.8793/R 0.6938）vs R1 0.7735（+0.0021，复现成功）；失败类型分析（1055 gold span：wrong_field 169 其中 constraint 100、not_extracted 154）见 docs/D1_ERROR_ANALYSIS.md §8；产物 outputs/development/s27_d1_v6_r3_clean_rerun_150_hist56d_v1/；**句子级粗 Gold 归因 verified**（2026-08-07，与 B0 同粗 Gold 同口径：F1 0.8726 / P 0.9012 / R 0.8456，见 outputs/development/s27_d1_coarse_gold_sentence_granularity_v1/）。**S2.13 Gold publication subtask 已发布（2026-08-10）**；D1-R4 ready 核账：冻结输入/Gold/共享组件齐备，剩余 blocker=LLM 调用授权与预算（本轮 zero-API 核账不调用 API、不伪造）→ 不执行；D1-R4 历史预测绑定核账（2026-08-10）：D1-R3 与 H1 的 150 条 predictions 与 formal input v2 逐项绑定（IDs/文本 hash/prompt/model/sampling/schema-valid 全过）→ zero-API candidate 重评允许；D1/H1 zero-API candidate 重评完成（2026-08-10，同 Gold/双口径视图/evaluators，comparison capsule outputs/evidence/d1_h1_zero_api_reeval_v1；D1 coarse 五字段与历史逐位一致；D1/H1 均 candidate/formal-gate-blocked，未写入正式目录）；2026-08-11 用户授权：D1/H1 门禁 ready（H1 为 comparison_arm_only），D1-R3/H1 snapshot 零 API 正式发布（direct_llm_formal_arm_v1 / sun_llm_fallback_formal_arm_v1，verifier 全过）；正式三方法比较报告完成（stage2_formal_three_method_comparison_v1），S2.10 verified（授权后 DoD），S2.12 描述性分析（retrospective），S2.11 dry-run + S2.13 gap capsule 已备；final_experiment_ready=true（fail-closed 条件真实满足，三方法 ready ≠ 全 Pipeline 完成）；D1-R5 verified（2026-08-11 正式结论包 stage2_formal_conclusion_v1） | D1-R3 experiment_run 事件 + 双评 evaluation JSON + audit --with-tests；150 次调用由用户逐批授权，manifest 记录 llm_calls/max_calls |
| 7 | S2.7-S2.12 | H1 development wiring 已修复；S2.8A/B/C development verified；S2.8D-R1 transport 离线修复 verified；S2.8D-R1 单次 v4-flash canary（硬上限 1、0 retry）因 span reference mismatch 被原子拒绝（valid=1、accepted=0、effective=0、gate=false、H1==B0），历史真实调用累计 41 次。**S2.8D-R2 离线取证**（0 real API calls）：3/3 被拒 span 为正确文本+错误坐标（clause 内唯一 exact match），结论=情况 A。**S2.8D-R3 已实现**（0 real API calls）：fail-closed unique exact-text coordinate canonicalization（`bpc_hybrid/h1_span_canonicalizer.py`，单一共享路径接入四模式；zero/ambiguous/contract 整 patch 拒绝；只改 start/end；仍过现有 validator 与 atomic merge）；同一 R1 capture 的 R3 离线 transport replay：reanchored 3/3、validator 通过、merge accepted、effective_patch=true、changed=1、**gate=true、H1!=B0**、identity 不变；R1 历史 strict 结果未改。**S2.8D-R4 真实 canary 成功**（1 real API call、retry 0，用户明确授权）：requested/resolved/returned=deepseek-v4-flash；HTTP 200、ok_message_content、reasoning=false、tool_calls=0、usage=1305/405/1710；非空 patch→canonicalizer reanchored 3/3（zero/ambiguous/contract=0）→canonical validator 通过→merge accepted→effective_patch=true、changed=1、**gate=true、H1!=B0**、identity 不变；离线 replay（s28d_r4_h1_canary_replay_v1）H1 sha 与真实运行一致、byte-identical；R1/R3 历史结果未改。**S2.8D-R5 已冻结**（0 real API calls、retry 0、未运行 pilot）：历史真实调用集合恢复=42 calls / 20 唯一 plan keys（sha c813a384…）；Gold-blind 确定性选样 10 个不同 sample plan（排除全部历史已调用 keys，复用现有 risk 排序）；frozen plan 配置 `configs/s28d_r5_h1_small_pilot_plan_v1.json`（sha 35dc6a75…，cap=10/retry=0/early-stop 合同）；runner `--frozen-plan` 严格绑定 fail closed + early-stop 实现（provider model / capture / count / plan key / 连续 3 次失败 abort；patch 级拒绝 continue）；plan-only 验证：selected=10/10、llm_calls=0、gate=false、H1==B0、execution order 与 keys hash 一致、历史交集空、byte-identical；新增 29 项测试（30 验收点），H1 focused 106 passed；默认行为不变。**S2.8D-R6 已执行**（用户明确授权，主真实命令仅一次）：实际 API calls=5（冻结 order 1–5：estg_000118/000133/000164/000206/000207），每 plan 1 次、retry=0、模型/capture 全对、无未冻结 plan；proposed=5、accepted=3、rejected=2、effective=3、changed=3、gate=true、H1!=B0=3、identity violation=0；canonicalizer reanchored 4/failed 1；usage 总 8976。**early stop 于 order 5 后误报 plan_key_mismatch**（R5 runner 计数缺陷，已修复+回归测试；真实调用无违规）；未调用 order 6–10 保留 not-called、不补跑。离线 replay（s28d_r6_h1_small_pilot_replay_v1，0 API calls）与真实运行逐项一致、byte-identical；机制最低可用门 passed=true。**S2.8D-R6C1 已补完**（用户授权只补 order 6–10；新增 actual API calls=5、retry=0、order 1–5 新调用=0、无 early stop）：estg_000232/000285/000302/000414 被拒（canonical_invalid+reference_mismatch）、estg_000716 accepted/effective；proposed=5、accepted=1、rejected=4、effective=1、changed=1、gate=true、identity violation=0；continuation replay 一致且 byte-identical；合并 R6+R6C1 为完整 10-plan capsule（s28d_r6_complete_h1_small_pilot_v1）：**10/10 覆盖 complete**、keys sha=bb8d73b2…、每 plan 一次、10 不同 sample；合并指标 calls=10、accepted=4、rejected=6、effective=4、changed=4、H1!=B0=4、identity=0、usage 总 18628。**formal S2.8 仍 blocked on S2.6；不得自动重试或进入完整 pilot** | 具备申请 S2.8D-R7（完整 10-plan Gold-blind 结果审计与受控 P/R 评价解锁准备）；P/R 仍 not_computed。**2026-08-08 H1 降级为对照（§8.8.1）**：全量 150 运行（commit 74614e3，用户授权 150 calls，deepseek-v4-pro）主口径粗 Gold F1 **0.7621 vs Rules-Only 0.7986（净负 −0.0365）**、细 Gold 0.6875 vs 0.7186；LLM 修复过度抽取 actor（P 0.7077→0.2754、spans 65→167），其余 5 字段持平或微升；机制正常（103 accepted / 89 changed / gate=True / 0 incidents）但 trigger+repair 配方加 FP 不加召回；证据支持决策 A（Direct-LLM 为主方法）；**H1 不再深究，仅作论文对照臂**；S2.8 正式 trigger 预注册取消 |
| 8 | S3.1 | **verified（2026-08-08）**：S1/S3.1 资产从 56d2b03 checkpoint 恢复（configs/schemas/data/docs/outputs/scripts/src/tests + 5 个 s1 gate 模块）；7 个 GDPR BPMN byte-exact（LF）落地并加入 `.gitattributes` eol=lf；修复 56d2b03 快照先存的跨任务 binding 过期（s13/s15/s16 合同 upstream hash、5 个 gate 期望、合同 stage1 块），manifest 按当前合同重新生成并全链更新；`verify_stage1_stage3_gdpr7.py` 通过；audit pass `stage1_formal_bpmn_membership_locked`；37 项 stage1 测试全绿 | 文件名、hash、claim 固定（合同 `stage1_stage3_gdpr7_v1.json` user-approved 2026-07-18 + 验证 manifest `s15_s31_gdpr7_membership_v1.manifest.json`） |
| 9 | S3.2/S3.3 | **annotation frozen（2026-08-08）**：58 条候选全部由用户裁决（matching 25=11 相关/14 不相关；violation 33=三类各 11）；裁决存 `data/development/human_review/stage3_gold_annotation_human_correction_v1.json`（decision 与 candidate 分离）；冻结 manifest `s32_s33_gold_annotation_freeze_v1.manifest.json`；工具：`review_stage3_gold_annotation.py`（交互/批量出题+导入）、`build/verify_stage3_gold_annotation.py`；**decision Gold 已发布（2026-08-10 随 formal Gold publication：matching 25 + violation 33，与 frozen correction 一致，≠ Gold Rule Records）** | 用户裁决完成；decision Gold 已发布；Gold Rule Records 另行人工裁决 |
| 10 | S3.4 | **development wrapper verified + 收口（2026-08-08）**：Winter baseline 转写 + 可移植重放（reachability 双模式、manifest 1.1.0、export index）；修复后重放 v3_clean/v3_prototype_literal（inference pack check_type 路由）；DEV_ONLY：MAP 0.6429、binary F1 0.6111、violation macro 0.373；evidence capsule `outputs/evidence/s34_winter_stage3_development_v3_clean|prototype_literal/`；S1.7 依赖已满足（2026-08-13 frozen）；formal completion blocked on S2.13 | 正式 canonical I/O + reproducible command（DoD 正式完成仍 blocked on S2.13；S1.7 已满足） |
| 11 | S3.5 | **development implementation verified（2026-08-08）**：Sun Def 4-7 重建 + 证据修复（inference pack/check_type/Def 6 存在性语义/unobservable 口径/sensitivity 真实重算）；run v2（不覆盖 v1，before/after 对照：unobs 33→10、macro 0.333→0.389、exact 0.333→0.364）；DEV_ONLY：MAP 0.8175、binary F1 0.0 如实；evidence capsule `outputs/evidence/s35_sun_stage3_development_v2/`（含 5 方法 comparison）；S1.7 依赖已满足（2026-08-13 frozen）；formal completion blocked on S2.13 | 不再是 fixture approximation；formal Oracle 主表待 formal Gold 门禁 |
| 12 | S3.6 | **development baseline verified（2026-08-08）**：BM25 + TF-IDF/SVD 双 arm；sensitivity 修复（gamma/theta 重实例化 scorer 重算，v2 runs 主指标与 v1 byte-identical）；DEV_ONLY：BM25 MAP 0.6833/macro 0.333；TF-IDF MAP 0.5881/macro 0.542；evidence capsule v2；阈值 0.5=fixed development setting（非 blind preregistration）；S1.7 依赖已满足（2026-08-13 frozen）；formal completion blocked on S2.13 | 相同 Gold/evaluator；正式 baseline 待 formal Oracle 门禁 |
| 12.1 | S2.13→S3.7 过渡核账 | **完成（2026-08-15 起，2026-08-17 更新）**：**v6 capsule 为当前 fail-closed 入口**（`outputs/reports/s2_13_s3_7_transition_readiness_v6.*`：GRR 三态探测、manifest/export 精确重建、严格 verifier 判定、11 个独立 verifier 执行、S2.11=canonical 未裁决（proposal v1/v2 superseded、proposal v3 当前未确认、importer v3 blocked=0）、S2.12=partial+execution-ready v3）；**v5 为上一版本**（`…_v5.*`，字节未改，v5 verifier 继续通过）；**v1/v2/v3/v4 保留为历史版本**（字节未改，各自 verifier 继续通过）；依赖矩阵从磁盘资产/manifest/hash/实际执行的独立 verifier 逐项重推导（S1.7=frozen、S2.10=verified、S2.11=in_progress_human_adjudication（只剩绑定 proposal v3 SHA 的一次性用户内容确认）、S2.12=partial+execution-ready v3、S2.13=blocked、S3.4-S3.6=development_only）；9 个 GDPR Gold Rule Records 不存在；Oracle 控制全 false；旧报告声明 supersede 但文件逐字节保留；零 gate 翻转 | v6 独立 verifier V6 VERIFIED；v3-v6 聚焦测试通过；全量 audit --with-tests 通过 |
| 12.2 | S2.11/G0.5 授权前工程收口 | **完成（2026-08-15，用户决策包 v5；v3/v4 为历史 checkpoint 字节保留；当前入口为 v6，见 12.3）**：`outputs/reports/s2_11_g0_5_pre_authorization_v5.*`——**v4 红测已修复**（v4 变更事件如实记录 3 failed/2057 passed/test_returncode=1/integrity_pass=false；v5 以历史 capsule 生命周期语义（`src/bpc_hybrid/capsule_lifecycle.py`）恢复全量 exit 0，v3/v4 核心资产逐字节不变）；论文许可已确认（CC BY 4.0 article-only，出版社 PDF 证据链 hash 绑定），artifact code/data 许可仍 unknown_pending_confirmation；adapter 为 **hardened v5 synthetic/shadow implementation verified**（严格 mode 枚举 INVALID_MODE、真实文件级 evidence binding、可验证字段级 provenance，68 项真实执行测试，formal activation 仍 blocked）；G0.5 候选合同 **draft_not_frozen** 且 promotion readiness=false（授权 hash 域=原始字节 61938c99…，语义 hash 51a6e4fe… 被拒）；映射选项 M1（modality identity candidate ONLY）/M2 未应用；门禁 G1/G2/G5/G6 ready=false+null、G3/G4 ready=true+dry-run（G4 绑定原始字节 hash 且只授权未来 gate-application checkpoint）；零 gate 翻转 | v5 独立 verifier VERIFIED；v5 focused 测试通过；全量 audit exit 0（2118 passed / 24 skipped / 19 warnings） |
| 12.3 | S2.11/G0.5 授权链封闭与固定锚点 | **完成（2026-08-15，v6；v3/v4/v5 为历史 checkpoint 字节保留；当前入口为 Checkpoint A 应用资产，见 12.4）**：`outputs/reports/s2_11_g0_5_pre_authorization_v6.*`——**frozen 授权链封闭**（v5 的 caller-supplied validation-result 解锁被反例推翻：手工字典含任意 64-hex token 即可解锁 v5 classify_frozen；v6 移除该参数，classify_frozen 每次调用从磁盘原始字节重验 draft/frozen config、授权 manifest、append-only 授权事件与 prior-results 证据扫描（derive_prior_results 按确定性路径/manifest 规则推导，不接受 caller bool）；manifest 完整绑定 schema/version、manifest ID、authorization_applied=true、精确批准 scope 枚举、精确 G4 dry-run 句全文+UTF-8 SHA-256、draft/frozen 相对路径+原始字节 SHA-256、retrospective/frozen-before/S2.10 标志、重推导 prior-results 扫描、授权事件（ID+路径+原始字节 SHA-256）与 pending checkpoint；全部变体被拒）；**历史 capsule 固定锚点**（v3/v4/v5 核心资产逐字节不变，锚定固定 origin commit 31ac757d…/8e8b488e…/7883739… + 硬编码 21 项 SHA-256 map；HEAD 与磁盘同错字节场景仍失败；v6 report/manifest 绑定三版固定 hash）；**adapter evidence provenance**（EvidenceContext + formal_evidence_provenance 输出、受控 scope 枚举、article-only 不满足 artifact、resolve 后 containment 防 symlink/junction 逃逸；当前磁盘仍拒绝一切真实 formal 调用）；v5 全量审计确实为绿（最终 receipt 2118 passed/24 skipped/19 warnings in 941.91s，非红测 checkpoint，历史事件保留），但其 hand-built validation-result 防护声明被本轮反例推翻（与绿灯分开记录）；G0.5 仍 draft_not_frozen（61938c99…，51a6e4fe… 永不使用）、G3/G4 仅 dry-run、G1/G2/G5/G6 false+null、S3.7 全 false/null；零 gate 翻转 | v6 独立 verifier VERIFIED；v6 focused 测试通过；全量 audit exit 0（两次） |
| 12.4 | S2.11/G0.5 非 API 决策应用与 G0.5 冻结（Checkpoint A） | **完成（2026-08-17，用户授权，零 LLM/API）**：`outputs/reports/s2_11_gates_applied_checkpoint_a_v1.json`——用户转发授权原句 `除了用apikey的时候要授权，其他直接正常进行即可。`（UTF-8 SHA-256 a8a1dec4…）记录于 `configs/s2_11_user_authorization_event_v1.json`（append-only、精确 scope、containment）；**G1**=resolved_for_local_nonredistributive_analysis（artifact 许可未知：91 文件盘点无 license 文件、anonymous 页面无 license 标识；license_verified=false；用户授权本地只读研究使用；禁止再分发/公开原始数据；禁止修改 references；正式包仅 hash/ID/统计/用户裁决）；**G2**=applied_local_read_only（scope=local_read_only_nonredistributive_s2_11；formal run 只读 membership manifest 文件）；**G3**=applied（M1 modality identity candidate mapping：obligation/permission/prohibition→identity；candidate-only；definition 不自动生成；外部 annotation 仅 review aid）；**G6**=applied（S0_no_automatic_structural_mapping：真实 artifact 记录为 {ID, version, text} 自然语言句，无叶子 span 结构字段，field_mapping={}，留空交人工）；**G4**=applied（`configs/g05_complexity_frozen_v1.json`：status=frozen、frozen_before_new_results=true、retrospective_use_forbidden=true、s2_10_retrospective_use_forbidden=true、scope=future_external_complex_corpora_only；经 v6 密封链完整验证：draft 原始字节 61938c99…、授权 manifest、append-only 授权事件、空 prior-results 扫描；G0.5=frozen_for_future_external_complex_corpora；draft 保留为历史；S2.10 不重标 preregistered；冻结前无候选/结果）；**G5**=not_applied_until_checkpoint_b；v6 capsule 转为历史安全基线（核心资产字节不变，pytest 生命周期语义修正）；S2.11 仍 blocked（待 Checkpoint B）、S2.12 partial、S2.13 blocked、S3.7 未动 | Checkpoint A verifier VERIFIED；focused 测试通过；record_change 事件 |
| 12.5 | S2.11 语料激活与人工 review surface（Checkpoint B） | **完成（2026-08-17，零 LLM/API）**：真实 Barrientos requirement 语料本地只读激活——**corpus inventory**（3 文件 40 记录，hash-only membership `outputs/reports/s2_11_corpus_membership_v1.json`，4 条空文本隔离，不复制原文）；**deterministic ingestion**（文档化模态关键词规则+精确 span；结构按 S0 留空；adapter 新增 `local_read_only_research` 模式——许可未知绝不声称 verified、用户授权事件+containment 证据全链验证）；**candidate 运行**（29 条候选：obligation 21/permission 2/prohibition 6；G0.5 frozen L1×28/L2×1；provenance 29/29；7 条运行期隔离 MODALITY_UNKNOWN/FIELD_SPAN_AMBIGUOUS，共 11 条；完整候选含原文仅 gitignored 本地目录，提交资产仅统计/hash/ID/隔离码）；**G5=applied_review_surface_open**（29 samples 空白 pack `data/development/human_review/s2_11_blank_review_v1.json` 全 null/unreviewed/无预填 Gold/无原文 + 用户决策文件 `s2_11_review_decisions_v1.json` + review 工具 `scripts/review_s2_11_candidates.py`（hash 只读加载原文、原子写、备份、resume、progress）+ 冻结验证器 `scripts/verify_s2_11_review_freeze.py`）；**S2.11=in_progress_human_adjudication**（29 条待用户裁决+11 条隔离）；transition readiness **v3** 重推导（v1/v2 字节保留）；S2.12 partial、S2.13 blocked、S3.7 未动；零 LLM/API、未伪造 Gold、未发布受限原文 | Checkpoint B 运行/工具/验证器 + focused 测试 + record_change 事件 + audit --with-tests |
| 12.6 | S2.11 全量裁决加速（Checkpoint C） | **完成（2026-08-17，零 LLM/API）**：**review 人口封闭 40/4/36**——inventory 40、客观排除 4（QUARANTINE_EMPTY_TEXT，原始字节重验）、nonempty=review population=36；29 available + 7 unavailable（MODALITY_UNKNOWN 4：blood r16v1/r17v1/r17v2、SIM r10v1；FIELD_SPAN_AMBIGUOUS 3：emergencies r2v1/r2v2/r3v1），候选失败绝不缩减 review 面；空白 pack/决策文件/G5 报告重建为 36 条（surface schema 1.1.0，binding 在写出后计算），冻结验证器读 pack 期望 36 并强制 sample set 精确相等，review 工具支持 unavailable 项；**36 条离线 AI 裁决提案**（`s2_11_generate_proposals.py`：deepseek_offline_proposal、human_approved=false/gold=false/reviewer 永不=user、值=原文精确子串+span 字节验证、缺=null 不虚构、confidence high 13/medium 19/low 4、needs_attention 8、G0.5 级别经密封 v6 链；完整原文仅 gitignored 本地、proposal SHA-256 14c1ec90… 绑定提交报告 `s2_11_proposal_report_v1.json`，零 ≥40 字符原文片段）；**dry-run-only 批量 accept/revisions 导入**（`s2_11_batch_import_dry_run.py` + 报告 `s2_11_batch_import_dry_run_v1.json`：绑定提案 SHA-256、36 成员+hash 全验、修订值须原文精确子串、无用户确认事件→不写决策文件且 --apply 拒绝（exit 2）、reviewer 永不=user、would-be 全部 review_state=reviewed 待确认；导入 blocked 10 字段/7 样本：modality 为受控词表类标、其余字段仅原文精确子串可导入）；**transition v3 重推导**（v3 验证器横幅 V2→V3 修复；v3 capsule 因 pack/决策/验证器 hash 演进按字节一致重建并验证；v1/v2 逐字节保留）；**S2.11=in_progress_human_adjudication（36 条待用户裁决）**；S2.12 partial、S2.13 blocked、S3.7 未动；零 LLM/API、未伪造 Gold、未发布受限原文 | Checkpoint C 构建器/工具/验证器 + focused 测试 + record_change 事件 + audit --with-tests |
| 12.7 | S2.12/S2.13 执行就绪（Checkpoint D） | **完成（2026-08-17，零 LLM/API）**：**S2.12 执行计划冻结**（`configs/s2_12_execution_plan_v1.json` + `outputs/reports/s2_12_execution_plan_v1.json`：预注册 G0.5 L1/L2/L3 分层（36 条密封链分类 L1 31/L2 5/L3 0）、三臂同一输入/Gold/evaluator、DoD 重述、retrospective 描述性分析保持历史；Gold=用户裁决 pending）；**fail-closed runner/evaluator readiness**（`src/bpc_hybrid/s2_12_stratified_evaluator.py`：确定性分层 per-field P/R/F1 + 错误类型 correct/missed/misclassified/extra，sample set 精确匹配/缺字段/坏 level/空集全拒绝；synthetic fixtures 通过；`outputs/reports/s2_12_execution_readiness_v1.json`：real_run_refused=true、S2.11 freeze 0/36、API 授权事件不存在、无 Gold、零 API）；**API 预算 dry-run**（typical 72/hard cap 100、calls_made=0、authorized=false、可复制授权句 present 但 sentence_used=false——本轮零调用未使用）；**transition readiness v4**（v4 capsule supersede v3 的 S2.11 workload 推导（36=29+7 空白 pack）与 S2.12 判断（partial+execution-ready）；新增独立 verifier verify_s2_12_execution_ready（8 个执行）；v1/v2/v3 逐字节保留且各自 verifier 继续通过；v4 V4 VERIFIED）；文档一致性（S2.11 行不再 blocked、G0.5=frozen、transition 当前=v4/v3 previous、gap capsule superseded、S1.7=frozen）；S2.12=partial+execution-ready、S2.13 blocked、S3.7 未动；零 LLM/API、未伪造 Gold、未使用 API 授权句、未发布受限原文 | Checkpoint D 构建器/验证器 + focused 测试 + record_change 事件 + audit --with-tests |
| 12.8 | S2.11 canonical v2 校正 + 一次性导入 + S2.12 正式口径对齐（Checkpoint E） | **完成（2026-08-17，零 LLM/API）**：**canonical v2 模型**（`src/bpc_hybrid/s2_11_canonical_v2.py`：unresolved/absent/present 三态、modality=label+evidence spans、多 span 字段、actor-action map、order relations；blank pack/decisions v2 `data/development/human_review/s2_11_blank_review_v2.json` + `s2_11_review_decisions_v2.json`；freeze validator v2 `scripts/verify_s2_11_review_freeze_v2.py`；review tool v2 `scripts/review_s2_11_v2.py`）；**36 条独立语义复核**（`scripts/s2_11_build_proposals_v2.py`：proposal v1 superseded 不可批准；v2 本地完整包 `outputs/development/s2_11_local_working/adjudication_proposals_v2/`（proposals.jsonl/decision_package.md/v1→v2 diff/quality report）；提交报告 `s2_11_proposal_report_v2.json`（proposal SHA 93866427…）；验收：coverage 36/36、exact-slice=0、evidence missing=0、value_missing_in_text=0、display None=0、multi-value 结构合法）；**importer v2**（`scripts/s2_11_batch_import_v2.py`：dry-run blocked=0/unresolved=0/adjudicable=36/36；`--apply` fail-closed（确认事件绑定 proposal v2 SHA+revisions SHA+reviewer、原子写+备份）；本轮未创建确认事件、未 apply、freeze=false、无 Gold）；**S2.12 正式口径对齐**（`src/bpc_hybrid/s2_12_stratified_evaluator_v2.py`：modality label acc/macro-F1/per-class + 五字段 span P/R/F1 复用正式合同；parity 与正式 evaluator 一致；`s2_12_method_adapter.py`；plan/readiness v2 supersede v1；`outputs/reports/s2_12_api_readiness_v2.json`：两臂 deepseek-v4-pro、36/72/108 calls、输出 4096、输入未文档化、cost_cap_unresolved、**未发出最终授权句**、缺项精确列出）；**transition v5**（39 项 supersedes、9 个独立 verifier、V5 VERIFIED；v1–v4 逐字节保留且各自 verifier 继续通过）；S2.11=in_progress_human_adjudication（只剩一次性用户内容确认）、S2.12=partial+execution-ready v2、S2.13 blocked、S3.7 未动；零 LLM/API、未伪造 Gold、未使用 API 授权句、未发布受限原文 | Checkpoint E 构建器/验证器 + focused 测试 + record_change 事件 + audit --with-tests |
| 12.9 | S2.11 proposal v3 最终校正与一次性确认就绪（Checkpoint F） | **完成（2026-08-17，零 LLM/API）**：六个已确认问题全部复现并修复——r10v1 双 actor 同 ID/条件内 customer 混入/缺 mapping → 显式 occurrence=1 + aam；canonical validator v3（`src/bpc_hybrid/s2_11_canonical_v3.py`：普通 span ID 全 record 唯一、clause ID 唯一、aam 存在/同 clause/无重复/全覆盖、order 两个不同 action、list-based 收集）；r4v2/r8v1/r18v2 action/constraint overlap=0（raw span + normalized 仅本地）；r3v1/r3v2 temporal-validity constraints（clause span 扩展至全文）；其余 30 条机械回归无证据不改写；**proposal v3**（`scripts/s2_11_build_proposals_v3.py`：explicit-occurrence spec、ambiguous 多命中 fail-closed；36/36 验收全零；SHA `9882ba45…`；本地完整包 `adjudication_proposals_v3/`；提交报告 `s2_11_proposal_report_v3.json` 零 ≥40 字符原文片段；**proposal v1/v2 superseded（v2=superseded_pending_targeted_correction_do_not_approve），v1/v2 逐字节保留**）；**importer v3**（dry-run blocked=0/unresolved=0/adjudicable=36；--apply fail-closed 绑定 proposal v3 SHA+revisions SHA+reviewer；本轮未创建确认事件、未 apply、freeze=false、无 Gold）；**freeze validator v3 + review tool v3**（canonical v3 + 7 checks）；**S2.12 readiness v3**（parity 重跑通过、re-bind proposal v3/importer v3；API dry-run 无最终授权句、缺项精确列出）；**transition v6**（47 项 supersedes、11 个独立 verifier、V6 VERIFIED；v1–v5 逐字节保留且各自 verifier 继续通过）；S2.11=只剩绑定 proposal v3 SHA 的一次性用户内容确认、S2.12=partial+execution-ready v3、S2.13 blocked、S3.7 未动；零 LLM/API、未伪造 Gold、未发布受限原文 | Checkpoint F 构建器/验证器 + focused 测试 + record_change 事件 + audit --with-tests |
| 13 | S2.13 | **blocked（2026-08-15 核账）**：Stage 2 冻结 DoD（S2.1–S2.12 完整）未达成；精确 blockers：S2.11 blocked（外部复杂语料 artifact 许可 unknown_pending_confirmation（论文 CC BY 4.0 仅 article-only）、数据激活授权未授予、3→4 标签映射未裁决、人工 Gold 未开始、G0.5 复杂度规则 draft_not_frozen（promotion readiness=false）、Barrientos adapter hardened synthetic/shadow implementation verified——formal activation 仍 blocked）+ S2.12 full DoD 未达成（仅 retrospective 描述性部分）；`final_experiment_ready=true` 不代表 S2.13 完成；DoD 未改、未拆新任务 | 数据、方法、Gold、指标、成本、manifest 完整（全部达成前保持 blocked） |
| 14 | PW1 | **下一论文任务**：引言与 RQ0–RQ4 | 无结果性过度主张；主张矩阵同步 |

Stage 1 和 Stage 3 的后续任务见主 Pipeline §8.9：S3.1-S3.3 数据治理及明确标注的
development 准备可受控并行；Stage 3 LLM/Hybrid、正式 Oracle、端到端均不得抢跑。

## 5. 当前派工

| 角色 | 任务 | 状态 | 写入范围 | Prompt |
|---|---|---|---|---|
| 协调 Agent | 维护门禁、验收和日志 | in_progress | shared docs/log only | `docs/AGENT_RUNBOOK.md` §§1–3 |
| Agent-E1 | S2.1-A 官方数据来源证据 | **verified** (2026-07-15 字节级核验通过；许可仍 unknown_pending_confirmation；B2 仍 open) | `data/development/sun_modality/`、`docs/research/SUN_MODALITY_DATASET_INGESTION.md`、manifest、`scripts/verify_sun_modality_zip.py`、tests | §4.1 |
| 当前执行 Agent | S2.11 proposal v3 最终校正与一次性确认就绪（2026-08-17，Checkpoint F） | **完成**：六个问题复现+修复（r10v1 消歧+aam、overlap=0×3、validity constraints×2、validator v3 强化）+ proposal v3（36/36 验收全零、SHA `9882ba45…`、v1/v2 superseded）+ importer v3（dry-run 0/0/36；--apply fail-closed 未执行）+ freeze/review v3 + S2.12 readiness v3（parity 重跑）+ transition v6（v1–v5 字节保留） | 只写 `formal_experiment/` 内 capsule/docs/scripts/tests/configs/src/data/development/human_review；references/ 只读未激活；未改 Gold/合同/Stage 3 门禁，零 LLM/API，未创建确认事件，未使用 API 授权句，未发布受限原文 | 下一真实路径：**用户一次性内容确认**（绑定 proposal v3 SHA `9882ba45…` 与 reviewer 署名；随后 `scripts/s2_11_batch_import_v3.py --apply` → `scripts/verify_s2_11_review_freeze_v3.py`）→ 用户对 S2.12 API 缺项（输入 token cap、cost cap）作决定并授权 → S2.12 真实运行 → S2.13 → Gold Rule Records（用户）→ S3.4–S3.6 → S3.7 单独授权 |
| 当前执行 Agent | S3.9 synthetic controlled-error extension（2026-08-22，零 API） | **完成（development panel verified）**：冻结 30 个可控错误变体（MA 10/IA 10/OO 10；源 BPMN byte-unchanged、exactly-one-error、结构校验、replay byte-identical；规则绑定自冻结 inference pack）→ 同一 evaluator 下四方法 panel（Winter/Sun/BM25/TF-IDF；DEV_ONLY macro 0.333/0.333/0.333/0.635）；16 项 focused tests 全绿；面板明确 dev-only、never 人类 Gold、不得冒充 Oracle。主线切换：Stage 1 不再扩展、Stage 2 用已有结果、论文并行、S2.12 保持 pending authorization（非 blocker） | 未改 Gold/合同/Stage 3 门禁；零 LLM/API 零网络；.bak 未触碰；正式预测目录未写入 | 下一步（论文 Checkpoint B）：论文正文回填（Stage 1/2/3 方法结果、错误类型讨论、误差传播、Threats/Limitations/Conclusion） |
| 当前执行 Agent | S3.9-EXT Stage 3 新违规类别扩展（2026-08-31，零 API） | **完成（development-only synthetic controlled extension v2 verified）**：新增 4 类违规 ×10 = 40 变体（prohibited_action_present / required_condition_not_enforced / constraint_violated / exception_not_handled）。选择理由已记录：原三类只覆盖动作存在/actor/顺序；四类分别补足 prohibition modality、condition、constraint、exception，且每类在原三类均正确时仍可独立发生、可做 exactly-one-error 变异并对应明确 BPMN 表面；因此是最小字段覆盖扩展而非任意补标签或穷尽分类。每变体 synthetic compliant control + 单一目标错误 variant（源 BPMN byte-unchanged、exactly-one-error、replay byte-identical、六要素字段锁定）；四方法共享同一新类型公式、仅替换各自冻结相似度后端（Winter-style extension / Sun-style extension / BM25 extension / TF-IDF-SVD extension；gamma_ext=0.5 统一冻结）；DEV_ONLY macro/exact/unobs：Winter 0.655/0.550/17、Sun 0.333/0.300/28、BM25 0.226/0.150/28、TF-IDF 0.379/0.325/27；对比报告 outputs/reports/s3_extended_violation_comparison_v2.{json,md}；17 项 focused tests 全绿；原三类 Gold/schema/预测字节不变 | 未改 Gold/合同/Stage 3 门禁/原三类产物；零 LLM/API 零网络；未调参追分；四类选择动机与边界已写入 config/report/论文；Winter/Sun 命名边界已写入报告（非原论文原生能力） | 下一步：论文侧仅按需引用 synthetic 结论（明确 dev-only 边界），不扩展 Stage 1/2/其他实验 |
| 当前执行 Agent | S3.9-EXT 收尾：paired control-plus-variant 评价与报告修正（2026-08-31，零 API、零重跑） | **完成（reporting closed）**：仅从持久化四方法 predictions 离线新增 80 对象配对评价（40 control Gold=none + 40 variant；control 预测由持久化 control_scores 按原阈值与固定优先级重建）；paired 口径（DEV_ONLY）Winter/Sun/BM25/TF-IDF：5-class acc 0.425/0.263/0.250/0.338、variant exact 0.550/0.300/0.150/0.325、control FP rate 0.500/0.125/0.000/0.275、paired acc 0.225/0.175/0.100/0.300；七类 overview 仅 7 个 per-class F1（无联合指标）；结论收紧（prohibited=可行性支持、constraint=部分支持、condition/exception=可观察性/映射瓶颈）；论文 §7.4 与主张矩阵 C30 回填；39 项 focused tests；报告生成 --report-only 确定性重放 | 未改 Gold/样本/阈值/四方法原始预测；零 LLM/API 零网络；原三类与 v1/v2 面板字节不变 | Stage 3 实验可正式收尾；论文/PPT 直接引用时区分 33 条人工 Gold、30 条 v1、40 对 v2 三套口径 |
| 当前执行 Agent | Stage 3 Sun 式阈值敏感性实验（S3.5 evidence extension，2026-09-04，零 API） | **完成（DEV_ONLY，Sun-style sensitivity verified）**：严格按 Sun 2024 §5.3/图 8/图 9 的离散网格离线重算（τ∈{0.0,0.2,0.4,0.6,0.8,0.9} 只评 matching AP/MAP；γ 同网格、ϑ 固定 0.8；ϑ∈{0.5,0.6,0.7,0.8,0.9} 固定 γ=0.8），每个 γ/ϑ 均由 SunScorer 真实重算 mappings/denominators/order endpoints/observability，缓存 Rule/Process Records，不重跑生成、不调用 LLM；Sun-transferred (0.8,0.8,0.8) Macro-F1 0.3889/exact 0.3636/unobs 10（低分基线保留）；best observed (0.8,0.6,0.8) Macro-F1 0.8733/exact 0.7879/unobs 4（Missing 1.0、Incorrect-actor 0.7778、Out-of-order 0.8421）；重算 primary 行与全部重叠行与 evidence `s35_sun_stage3_development_v2` 逐项一致；报告 JSON/MD + 图 A（γ，missing+out-of-order，Sun 图 8 口径，Precision 为主 + Recall/F1 补充面板）+ 图 B（ϑ@γ=0.8，incorrect actor，Sun 图 9 口径）+ 论文 §7.4.7 + 主张矩阵 C31；11 项新增 focused tests（阈值集合/指标重算/原始结果与 Gold 字节不变/零 API/确定性重放） | 未改 Gold/样本/预测/公式/既有 evidence；零 LLM/API、cost=0；33 条无 Gold=none 合规样本（不能证明 specificity/FP rate）；γ=0.6 仅称 tested values 中 best observed setting（非全局最优/非 Sun 固定阈值/非 held-out 最优） | 下一步：正式 Oracle 与端到端仍待 S3.7/S3.10；论文引用时区分 33 条人工 Gold 与 DEV 敏感性产物 |
| 当前执行 Agent | S3.9-EXT-REAL-CASE 真实案例端到端（SIM 卡入网，2026-09-11，零 API） | **完成（development 案例交付）**：主案例 = Barrientos Sun 派生 SIM 流程 × 5 条 v2 规则；公共 Stage 1 记录 + 声明的协作图扁平化适配；A/B/C 三组实跑（A 15 检查 5 violation/9 undetermined/1 satisfied；B 15 检查 5/8/2；C 35 检查 8/25/2，含 15 条继承自 B 的三类行）；与 5 条开发参考判断对照：r9/r10 检出，r8/r11/r13 无法判断（原因 `action_mapping_below_gamma`/`no_mapped_rule_order_endpoints`/`empty_rule_condition`），**未检出项如实保留**；5 个最小修复对照**全部未消除问题**（含 frozen Def6 的 min-over-{actors ∪ business objects} 与无词向量后端）；重复运行 5/5 逐条一致；补充案例 Figure 10 重建件（18 项歧义有 provenance）跑非 LLM 基线 28 检查（4/24），**真实 LLM 组缺失且原因已记录** | 只写 `formal_experiment/`；references/ 只读未复制原文；未改 Gold/冻结实现/门禁；零 LLM/API 零网络 | 下一步：结果标注图与论文小节（子任务进行中）、更多误报对照与正式 Oracle 仍待独立授权 |
| 当前执行 Agent | S3.9-EXT-REAL-CASE 真实案例端到端（SIM 卡入网，P1/P2/P4 四个缺口收尾，2026-09-12 第四轮，零 API） | **完成**：P1 修正显式 actor-action 配对路径的角色绑定回退，r11 A/B 最终 actors/pairs 均为 Phone company，同时保留 original=the Data Controller、bound_from=Data Controller 与 value-level change；r8 null actor 仍为 invalid_in_raw_no_valid_pair，不补造配对；政策说明改为有有效显式映射才消费配对动作，无有效映射时首个投影动作仅供动作存在性检查。P2 把五条固定参考问题改为证据绑定评价：r9 记录 Sign contract 只是定位锚点、流程清单无 verify/correctness 活动；r10 逐项列出 matched candidates，Activate SIM card 的具体 ID 归属 Customer，Send SIM card 单独归属 Phone company；r11 只有 out_of_order 报警映射 consent 与 request personal data 顺序时才对应，missing_action 不替代；r13 记录 50 EUR 文本位于 actor、condition/constraint 为空，threshold alarm evidence 为空；r8 只从 model-side 时间/终止字段与 process-scope facts 判定。P3 复用 A/B 抽取与预测，计数仍为 A 15 3/0/12/0、B 15 5/2/8/0、C 35 10/2/23/0；B/C 原三类逐项一致；参考对应 A 0/3/2，B/C 2/3/0。P4 修复表统一读取 C_original/C_repaired，流程图从只读 BPMNDI 恢复 26 条 sequence flow 连线、网关、条件标签与稳定节点，r9 缺失活动用明确占位符，r10/r11/r13/r8 标注动态读取 capsule；Chromium 实际渲染 1800x4495，无文本越界/重叠；报告、论文、SVG 同步更新。聚焦测试 36 passed。 | 只写 `formal_experiment/`；references/ 与既有预测只读；零 LLM/API；未调阈值、未新增别名或特判；r8 Stage 1 表示限制、r13 empty condition、r11 gamma/端点映射限制仍如实保留。 |
| 当前执行 Agent | PAPER-FINAL-REPAIR：三张论文表的最终口径修复（2026-09-21，零 API；分支 `paper-final-repair`） | **Table 1 完成**：`formal_stage2_evaluation.evaluate_span_metrics` 的 `overall` 原为**六字段** pooled 聚合，把 G0.4 合同明令不可用、且由 coarse transform 用 clause span 合成出来的 modality span 计入；现改为 `pooled_five_span_fields`（仅 actor/action/condition/constraint/exception 的 micro pooled P/R/F1）作为唯一合同口径 overall，旧六字段聚合保留为显式 `NON_CANONICAL` provenance 字段。重算结果：Sun rules-only pooled F1 **0.7631**（P 0.6984/R 0.8410）vs Direct-LLM **0.8378**（P 0.8695/R 0.8083），Δ **+7.47 pp**；字段级 action +5.10 / condition +6.42 / constraint +12.45 pp 归 Ours，actor −6.24 / exception −11.81 pp 归 Sun；modality label macro-F1 0.7128 vs 0.7695。产物 `outputs/reports/stage2_table1_paper_final_v1.{json,md}`（脚本 `scripts/build_stage2_table1_paper_final_v1.py`）。**Table 2 完成**：旧消融报告用六字段 pooled 口径，与 Table 1 不可直接比较；现从已执行的 450 次真实调用（DeepSeek-V4-Pro-0813）的持久化 canonical predictions **离线重算**到与 Table 1 同 prompt 家族（monolithic v6, sha `3aa64877…`）同口径，并加 10,000 次 paired bootstrap。Overall：Full 0.8224 / −E 0.8142 / −S 0.8299 / −J 0.8268，四臂均 150/150 有效。**如实结论**：三项删除在 pooled overall 上**都没有 CI 排除 0**；可分离的字段效应**符号不一致**（−E 使 Condition F1 +4.22 pp [+1.33,+7.78]；−J 使 Action F1 +3.47 pp [+0.67,+6.80]），且 leave-one-out 因 E/S 信息重叠无法隔离单模块。产物 `outputs/reports/stage2_table2_prompt_ablation_paper_final_v1.{json,md}`。**Table 3 判定为现有产物不可测**：见下一条。 | 只写 `formal_experiment/`；未改 Gold/面板/既有预测/正式 capsule；零 LLM/API 零网络；未按结果调阈值或改 prompt；旧六字段数字一律标为 development provenance | 下一步：Table 3 三选一决策（见 `docs/research/STAGE3_TABLE3_VIABILITY_DIAGNOSIS_2026-09-21.md` §7），以及把 Table 1/2 回填论文 §7.2/§7.3 |
| 当前执行 Agent | PAPER-FINAL-REPAIR：Stage 3 Table 3 可行性诊断（2026-09-21，零 API，只读）**含自我更正** | **分层结论**：① 33 条 violation gold 的 `decision_violation_type` 逐字复制 `check_type`、`decision_evidence` 为模板句、无任何 BPMN 变异 → 是 check-point 决策集，不是性能 benchmark，不得再作 Table 3 的 F1 分母。② **结构可检测性 30/30**：用 Stage 1 Process Record 把每个变异体与其未变异原始体对比（不涉检测器与相似度）——missing_action 10/10、incorrect_actor 10/10、out_of_order 10/10。③ 但用冻结 Sun 重建打分时 **0/30 可分离**（原始体本已被判违规；out_of_order 分母 10/10 为 0；incorrect_actor 8/10 `action_mapping_below_gamma`），gamma 网格 {0.2,0.4,0.6,0.8,0.9} 最多 1/30 → 那是**检测器 grounding 缺陷**（GDPR 法条措辞与 BPMN 活动标签几无共同词汇），**不是数据缺陷**。④ 仍存独立缺口：Gold Rule Records 的 `order_relations` **0/92** 非空（`actor_action_map` 38/92）。**自我更正记录**：首版诊断误判"面板不可测"，根因是探针把 manifest 的 `f_first_id`/`f_last_id`（实为 sequence-flow id）当节点 id 查节点级 reachability，且把 `control_flow.reachable_pairs`（对象数组）当元组迭代，两错同向制造 out_of_order 10/10 的假"无变化"；已修正并留痕。脚本 `scripts/diagnose_stage3_table3_viability_v1.py`、`..._threshold_rootcause_v1.py`、`..._mutation_detectability_v1.py`；详见 `docs/research/STAGE3_TABLE3_VIABILITY_DIAGNOSIS_2026-09-21.md`。 | 只读：未写 Gold/面板/预测/结果；零 LLM/API；未为让某方法好看而挑阈值或后端；更正过程完整保留在 commit 与事件日志 | 已由下一行的配对 benchmark 承接 |
| 当前执行 Agent | PAPER-FINAL-REPAIR：Stage 3 配对 benchmark 建成 + grounded 参考上界 + 前人 sanity run（2026-09-21，零 API） | **完成（objective item 4 前两步）**：旧 30 条面板无 compliant 样本，precision/specificity 无分母、per-type F1 全线退化；现建 **60 items = 30 pairs**（`data/development/stage3_synth/stage3_paired_benchmark_v1.json`），每个变异 BPMN 配同一流程的**未变异 BPMN** 作 compliant control，control 复用 variant manifest 自己声明的 `source_bpmn`+sha（冻结 Stage 1 GDPR7 字节），**未新造合规流程**，故不需新人工标注也不会漂移；gold = 30 compliant + 每类 10；每 item **显式声明 grounding**，使"消费绑定"与"相似度重推绑定"两路可比。**anti-degeneracy 30/30 PASS**（control 不违反、variant 必违反）。**grounded 参考上界** macro-F1 **1.0000**/micro-F1 1.0000/specificity 1.0000/exact 30/30/unobs 0 → benchmark 可测且 Gold 自洽（健康 benchmark 的必要 sanity check）。**前人同一 60 items 同协议**：sun_reconstruction macro 0.3175（micro 0.3871、spec 0.3333、exact 12/30、unobs 16、out_of_order 0.0）；winter_wrapper macro 0.2222（micro 0.3846、spec 0.6000、exact 10/30、out_of_order 0.0）。报告内写明该差距是 **grounding 效应**，不得写成"前人算法弱"。产物 `outputs/reports/stage3_{paired_benchmark,grounded_checker,predecessors_paired}_v1.*`；生成器/runner `scripts/build_stage3_paired_benchmark_v1.py`、`scripts/run_stage3_grounded_checker_v1.py`、`scripts/run_stage3_predecessors_paired_v1.py`；测试 `tests/test_stage3_paired_benchmark_v1.py`（5 项）。 | 只读既有产物：30 条面板与冻结 BPMN 字节未改；只新增文件；零 LLM/API 零网络；未调阈值追分；unobservable 计入 miss 不置零 | **仍缺**：`grounded_structural_checker_v1` 目前是**声明绑定下的参考上界**，把它写成 "Ours" 前必须先建**从已发布 Stage 2 Rule Record 真实推导 actor-action / order 绑定**的检测器（方案 A 剩余部分），且 out_of_order 还需补 Gold 的 order 关系标注（现 0/92 非空）；随后才能出 Table 3 的 Ours 行 |
| Agent-P1 | PW1 引言与研究问题 | ready | `paper/THESIS_DRAFT.md`、主张矩阵 | §4.2 |
| Agent-R1 | 论文科学主张只读复核 | blocked on PW1 draft | 无写入 | §4.3 |
| 用户 | S2.2 Layer E 人工裁决 | verified，150/150 adjudicated | 仅 Layer E | freeze validator 通过；formal Gold 已于 2026-08-10 发布（用户授权）；Gold Rule Records 另行裁决 |

实验 Agent 默认串行；论文 Agent 可以与一个实验 Agent 并行，但不得编辑 shared
状态页。协调 Agent 在工作 Agent 交接后统一更新本页、Pipeline、catalog 和日志。

## 6. 当前禁止

- 不把现有 heuristic 叫作 Sun 完整复现或 Sun 原始代码；
- 不自动填写、修改或通过预测反推人工 Gold；
- 不运行真实 LLM/API，除非用户再次明确授权且预算、模型、prompt 已锁定；
- 不把 development 结果复制成 formal 结果；
- 不用不同 test IDs、Gold、schema 或 evaluator 制造 baseline 比较；
- 不新增第二份 pipeline、日期版 status 或 handoff；
- 不改动 `references/` 或根 `archive/`，也不恢复其中代码为活动实现。

## 7. 证据入口

- 文档地图：`docs/INDEX.md`
- 目录职责与逐文件清单：`docs/DIRECTORY_GUIDE.md`、`docs/FILE_CATALOG.md`
- Sun 数据与最终版审计：`docs/research/SUN_FINAL_VERSION_AND_DATA_AUDIT.md`
- S2.3 public marker 重建：`docs/research/PUBLIC_MARKER_LEXICON_RECONSTRUCTION.md`
- S2.8D-R2 canary span/offset 取证：`docs/research/S28D_R2_CANARY_OFFSET_FORENSICS.md`、`docs/research/S28D_R2_CANARY_OFFSET_FORENSICS.json`
- S2.8D-R3 coordinate canonicalization：`docs/research/S28D_R3_COORDINATE_CANONICALIZATION.md`、`docs/research/S28D_R3_COORDINATE_CANONICALIZATION.json`
- Sun baseline 边界：`docs/research/SUN_BASELINE_AUDIT.md`
- Winter/Sun 代码分离：`docs/research/SUN_WINTER_CODE_SEPARATION_AUDIT.md`
- Barrientos 借用边界：`docs/research/BARRIENTOS_BORROWING_AUDIT_2026-07-12.md`
- 历史交接：`_retired/docs/2026-07/CURRENT_HANDOFF_2026-07-12.md`
- 追加式实验日志：`docs/EXPERIMENT_LOG.md`、`docs/EXPERIMENT_EVENTS.jsonl`
- Agent 派工与 Prompt：`docs/AGENT_RUNBOOK.md`
- S2.13→S3.7 过渡核账（2026-08-18 更新）：**当前（fail-closed）** `outputs/reports/s2_13_s3_7_transition_readiness_v8.json`（+ `.md` / `.manifest.json` / `_export_index.json`；schema `configs/schemas/s2_13_s3_7_transition_readiness_v8.schema.json`；builder `scripts/build_s2_13_s3_7_transition_readiness_v8.py`；verifier `scripts/verify_s2_13_s3_7_transition_readiness_v8.py`）；v1–v7 为 byte-exact 历史版本（各自保留，v5/v6 按其 superseded 快照语义 fail-closed）
- S2.12 执行就绪 v3（2026-08-17，Checkpoint F，**当前入口**）：`configs/s2_12_execution_plan_v2.json`（冻结预注册计划）+ `outputs/reports/s2_12_execution_plan_v2.json` + `outputs/reports/s2_12_execution_readiness_v2.json` + `outputs/reports/s2_12_execution_readiness_v3.json`（parity 重跑、re-bind proposal v3/importer v3；builder `scripts/s2_12_build_readiness_v3.py`；verifier `scripts/verify_s2_12_readiness_v3.py`）+ `outputs/reports/s2_12_api_readiness_v2.json`（两臂 deepseek-v4-pro、36/72/108 calls、输出 4096、输入未文档化、cost_cap_unresolved、无最终授权句）；评估器 `src/bpc_hybrid/s2_12_stratified_evaluator_v2.py`（正式口径+parity）；方法适配 `src/bpc_hybrid/s2_12_method_adapter.py`；v1 plan/readiness 保留为历史（superseded）；描述性分析保持历史/retrospective
- S2.11 canonical v3（2026-08-17，Checkpoint F，**当前入口**）：`outputs/reports/s2_11_proposal_report_v3.json` + `outputs/reports/s2_11_batch_import_dry_run_v3.json`（+ `data/development/human_review/s2_11_blank_review_v2.json`（canonical，36 条全 unresolved）+ `s2_11_review_decisions_v2.json`；提案构建 `scripts/s2_11_build_proposals_v3.py`；importer v3 `scripts/s2_11_batch_import_v3.py`；canonical validator v3 `src/bpc_hybrid/s2_11_canonical_v3.py`；freeze validator v3 `scripts/verify_s2_11_review_freeze_v3.py`；review tool v3 `scripts/review_s2_11_v3.py`；测试 `tests/test_s2_11_canonical_v3.py`）；**proposal v1/v2 已 superseded 不可批准**（`s2_11_proposal_report_v1.json`/`_v2.json` 与本地包逐字节保留）；v1/v2 空白 pack/决策文件保留为历史；Checkpoint A 应用门禁 `outputs/reports/s2_11_gates_applied_checkpoint_a_v1.json`（用户授权事件 `configs/s2_11_user_authorization_event_v1.json`、G0.5 冻结 `configs/g05_complexity_frozen_v1.json`、M1 政策 `configs/s2_11_mapping_policy_m1_v1.json`）；v6 及更早为历史安全基线（核心资产字节未改）
- 历史（superseded 当前状态判断，文件保留）：`outputs/reports/s2_13_stage2_freeze_gap_capsule.{json,md}`、`outputs/reports/s3_7_oracle_readiness_v2.json`、`outputs/reports/s37_oracle_readiness_v1.json`
- 论文工作稿与主张矩阵：`paper/THESIS_DRAFT.md`、`paper/CLAIM_EVIDENCE_MATRIX.md`

## 8. 2026-09-23 Table 3 v2 repair（当前）

- 旧 `outputs/reports/stage3_table3_v1.json` 的 Ours F1=1.0 **已撤回**：其 automatic
  grounding 以配对 control BPMN 为参考，候选并集在 13 个 eligible pairs 中有 10 个覆盖
  整个 control；`run_stage3_ours_v1.decide_item` 仅检查『control 活动是否在当前图缺失 /
  lane 是否改变』，`actor_predictions` 未进入 actor 判定；predecessor runner 另用
  development rule extractor 并按 `target_violation_type` 选输出。
- 修复主比较：Sun 与 Ours 只替换 Stage 2 capsule，共用同一个 `gdpr_capsule_converter`、
  同一个冻结 `SunScorer` 实例与 frozen thresholds；Winter 使用 native wrapper；input view
  无 role/target/gold；所有信号先持久化再由 evaluator 读 label。
- 运行产物：`outputs/development/stage3_table3_v2/`（predictions、rule records、manifest）；
  `outputs/reports/stage3_table3_v2.{json,md}`、`stage3_table3_v2_error_analysis.json`、
  `stage3_table3_v2_rootcause_notes.md`。
- 真实结果（13 pairs / 26 items；out_of_order N/A）：Sun/Ours/Winter 三者 macro-F1 均
  0.3333、micro-F1 均 0.5517；missing_action P=0.5000/R=1.0000/F1=0.6667（8 TP/8 FP）；
  Sun/Ours actor 5 正例 + 5 control 全部 unknown、F1=0.0；Winter actor 5 正例 unknown、
  5 control satisfied、F1=0.0。Ours 未胜出；未调阈值或改样本。
- 独立证据：13 个 eligible controls 仅 6 个唯一 BPMN（7 个重复 control）。
- 验收判断：实验已真实完成且旧泄漏 F1=1 口径已修复；正向 Ours 主张不满足。下一项若要
  继续，只能单独预注册额外 grounding 实验臂并说明新增变量，或补齐有原文依据的 order
  标注产生合法 order 分母，不得围绕本轮分数调参。
# S3-TABLE3-V4-R2 status (2026-09-25)

Status: `needs_method_review` (R2 fixes the confirmed R1 projection/failure-record defects; Table 3 is still not accepted because all three methods have no observable order denominator).

R2 deliverables:
- Strict shared projection: `src/bpc_hybrid/sun_stage3/temporal_projection_v3.py` (`sun_stage3_temporal_projection_v3@1.0.0`).
- Non-scoring failure diagnostics: `src/bpc_hybrid/sun_stage3/order_failure_diagnostics_v1.py`.
- Offline matrix: `outputs/development/stage3_table3_v4_r2/`.
- Independent report: `outputs/reports/stage3_table3_v4_r2.{json,md,manifest.json}`.
- Cause localization and corrected candidates: `outputs/reports/stage3_table3_v4_r2_cause_analysis.{json,md}`, `outputs/reports/stage3_temporal_scope_candidates_r2.{json,md}`.
- Actual new API calls: 0. D1 real predictions reused from `data/predictions/stage3_v4_d1_frozen_v1/`.

R2 metrics (same arithmetic as R1):

| Method | Missing F1 | Actor F1 | Order F1 | Overall P | Overall R | Overall F1 | Coverage | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Sun | 0.4545 | 0.2500 | 0.0000 | 0.3000 | 0.4000 | 0.3429 | 0.4600 | available |
| Ours | 0.4545 | 0.2500 | 0.0000 | 0.3000 | 0.4000 | 0.3429 | 0.4600 | available |
| Winter | 0.4286 | 0.8889 | 0.0000 | 0.5385 | 0.4667 | 0.5000 | 0.7000 | available_native |

R2 order-failure categories (20 case×5 rule signals per method): Sun 40 projection_rejected_range + 60 endpoint_similarity_below_gamma; Ours 40 projection_rejected_syntax + 60 endpoint_similarity_below_gamma; Winter 100 no_rule_order_relation. R2 still does not turn these into satisfied/violated; the remaining blocker is endpoint mapping/threshold plus native after/then coverage.

# S3-TABLE3-V4-R1 status (2026-09-24)

Status: `needs_method_review` (all three methods have real Table 3 data; order class is still unobservable for all three).

Confirmed Table 3 R1 scoped results (AI construction reference; `is_gold=false`, `human_adjudicated=false`):

| Method | Missing F1 | Actor F1 | Order F1 | Overall P | Overall R | Overall F1 | Coverage | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Sun | 0.4545 | 0.2500 | 0.0000 | 0.3000 | 0.4000 | 0.3429 | 0.4600 | available |
| Ours (Direct-LLM v6 + same Sun Stage 3) | 0.4545 | 0.2500 | 0.0000 | 0.3000 | 0.4000 | 0.3429 | 0.4600 | available |
| Winter (native) | 0.4286 | 0.8889 | 0.0000 | 0.5385 | 0.4667 | 0.5000 | 0.7000 | available_native |

R1-A/B/C/D:
- R1-A: observable coverage corrected to `(cells - unknown_positive - unknown_negative)/cells`; blocked methods publish null P/R/F1 with diagnostic arithmetic separated; inference output hashes and manifest bindings validated before reference read.
- R1-B: `temporal_projection_v2` bounds nominal endpoints by the selected span and preserves exact source substrings; before/after can use a post-marker clausal predicate (article18p3 `lifted`); Winter receives a global role-candidate set built only from the 20 inference-view BPMN process names.
- R1-C: five real Direct-LLM calls completed (`deepseek-v4-pro`, response model `deepseek-v4-pro`), 0 retries, 21,866 prompt tokens + 3,419 completion tokens, conservative cost 0.04240236 USD. Raw responses, ledger, canonical predictions, and manifest are under `data/predictions/stage3_v4_d1_frozen_v1/`.
- R1-D: 900 signals and 50 evaluable cells per method persisted before evaluation; independent evaluator produced `outputs/reports/stage3_table3_v4_r1.{json,md,manifest.json}`.

Remaining limitation: all three methods leave `out_of_order` entirely unknown. The current five source excerpts use `before`/`prior to`, which is insufficient to establish the ordered-event expressions needed by the native Winter sequence mechanism. Article14(3)(a), Article33(2), and Article43(1) natural-after candidates are inventoried in `outputs/reports/stage3_temporal_scope_candidates_r1.{json,md}` and are **not** part of the current benchmark. No scores were altered to avoid zero/extreme values.
