# S2.12 / GDPR 真实 LLM/API 授权材料（含历史版本）

## 当前范围：2026-09-14 用户取消规则＋LLM 实验

用户原话：“规则+LLM直接不要了，不在进行规则+LLM的任何实验”。因此：

- S2.12 `sun_llm_fallback` 的 F-1/F-2/F-3 共 27 次取消，历史授权文件不再允许执行
  这些阶段；不新增、重跑、消融或评价规则＋LLM 修复方法。
- 只保留 S2.12 `direct_llm` 36 次和 GDPR `direct_llm` 74 次，合计 **110 次计划**。
  被取消额度不转给 Direct；旧 137 次授权请求/发送确认句不可原样使用。
- 本次是取消与范围收窄，不是新的 API 授权，也未解除当前自动审批的外部发送阻塞。
  S2.12 两方法执行/评价/冻结合同已于 2026-09-14 适配：当前输入/请求绑定、剩余
  36+74=110 次命令和冻结条件以 `outputs/reports/s2_12_two_method_contract_v1.json`
  为准；下方旧三方法 63/137 次串行命令只保留为历史授权材料，不得原样执行。
- 原始授权、价格快照与合同保留溯源。下方 v4、§13 的 63/137 次和三方法完成定义
  均为取消前记录；§14 Direct E/S/J 消融独立计划仍未授权。

## 历史 v4 材料（以下不是当前派工）

**版本**：v4（2026-08-22 runner safety v2 完成后）
**状态**：**AUTHORIZED (2026-09-07 USER SENTENCE RECEIVED) / ZERO CALLS / READY**
**前版**：v3（2026-08-22 runner wiring）；v2（2026-08-20 价格复核）；v1（初版）
**边界**：不读取 `.env`、不调用真实 API、不改 Gold、不启动 Oracle。2026-09-07
论文收尾指令（UTF-8 SHA-256 `27426de7…`，见 §13）授权两批共 137 次调用并已生成
授权事件/auth 文件；真实调用仍为 **0**，等待进程环境凭据（runner 只读进程环境）。
本节 §0–§12 的历史状态行保留；2026-09-07 之后的权威状态见 §13。

## 0. 状态摘要（v4 要求）

| 项目 | 状态 |
|---|---|
| 真实 payload 锁（**每次调用前**重建最终 body → SHA-256 → 与锁定逐条比对 → ID/顺序核验） | ✅ `PayloadLock` + fake/real transport 通用 |
| Arm policy 与实际发送一致 | ✅ Direct（stream=false、thinking disabled、response_format=null、temp0/top_p1/4096）与 fallback（+json_object、tools_sent=false）由 `arm_policy` 强制 |
| usage 捕获（prompt/completion/returned model/finish reason/缺失状态） | ✅ 从 `transport.last_decode["usage"]` 读取；缺失即 fail-closed 并记账（2026-09-07 起事故记账后中止、绝不自动重发） |
| 成本计算（cache hit/miss 拆分；缺失时保守 cache-miss；累积 USD） | ✅ `per_call_cost` + `CumulativeState`；`cost_usd` 不再硬编码 0 |
| 每次调用前/后 caps（input/output/USD + 保守上界 + call cap） | ✅ `check_pre_call` / `check_post_call` |
| off-peak **每次调用前**检查；运行中进入 peak 即停 | ✅ `check_off_peak_only` 在 StageExecutor 每轮调用 |
| 分阶段运行（D-CAL 1 / D-REST 35；F-1/F-2/F-3 9×3）+ resume | ✅ `--stage-id`/`--auth-file`/`--resume-from-ledger`；任意 `--start` 拒绝 |
| append-only hash-chained 账本 + resume 不重复 + 篡改拒绝 | ✅ `ExecutionLedger`；resume 跳过已记账 payload（含事故记录） |
| `.env` 禁读（仅进程环境） | ✅ 两个 runner 均 `LLMConfig.from_env(project_root=ROOT, load_project_env=False)` |
| 每 arm 独立 runner hash 绑定（fallback 不再与 direct 比较） | ✅ `validate_authorization(arm, runner_hash, impl_hashes)` |
| D-CAL 单请求计费校准（schema/builder/测试；不执行） | ✅ codec + 测试 |
| 授权事件 builder（无原句拒绝；dry-run 默认） | ✅ `scripts/build_s2_12_auth_event_v1.py`；2026-09-07 已 apply 全部 5 个 stage |
| 响应落盘与终态化（raw store / finalize / 参数化 evaluate） | ✅ 2026-09-07 补齐（§13）：raw 内容只落 gitignored 目录；正式 capsule=坐标-only canonical 36/27 行 |
| 真实 API calls / billed tokens / USD | **0 / 0 / $0** |
| 授权文件 | **已创建（2026-09-07，§13）**：5×auth + 5×event + GDPR 事件 + 授权依据；`verify_s2_12_authorization_files_v1.py` 70/70 PASS |

## 1. 待运行 arms（与 preflight 锁定一致）

| Arm | 机器方法 | 说明 | 计划调用数 | max-calls |
|---|---|---|---|---|
| A1 | `direct_llm`（Direct-LLM） | 端到端生成 Rule Record，v6 prompt（SHA 3aa64877…） | 36（每条 1 次） | 36 |
| A2 | `sun_llm_fallback`（Rules+LLM-Repair，comparison-only 对照） | 仅修复 frozen plan 锁定的 27 个 clause 触发子集 | 27（clause 级） | 72（配置值；实际 27） |

## 2. 最终运行命令（分阶段；无占位符；尚未执行）

所有命令均使用固定授权文件路径（由 §4 builder 未来创建）与预注册 stage；禁止
任意 `--start`/ID 列表。

**D-CAL（校准，未来授权后）** — Direct-LLM 第 1 个锁定 payload，1 次调用：
```powershell
python formal_experiment/scripts/build_s2_12_auth_event_v1.py `
  --runtime-home D:/environment/stanford-corenlp-4.5.10 `
  --stage-id D-CAL --dry-run --usd-cap 1.00 `
  --sentence "<你的授权原句，逐字>"

python formal_experiment/scripts/run_s2_12_direct_llm_v1.py `
  --runtime-home D:/environment/stanford-corenlp-4.5.10 `
  --transport real --allow-llm `
  --auth-file formal_experiment/configs/s2_12_api_authorization_D-CAL.json `
  --stage-id D-CAL `
  --output-dir formal_experiment/data/predictions/s2_12_direct_llm_v1
```
（D-CAL 固定授权文件路径：`formal_experiment/configs/s2_12_api_authorization_D-CAL.json`
+ 事件文件 `configs/s2_12_api_authorization_event_D-CAL.json`；off-peak-only；每次调用前
检查时段；input cap ≤1,000,000、output ≤4,096、USD ≤1.00；结果属于正式锁定 arm。）

**剩余调用分阶段（校准后）**：
```powershell
# Direct D-REST（35 次；resume 账本）
python formal_experiment/scripts/run_s2_12_direct_llm_v1.py `
  --runtime-home D:/environment/stanford-corenlp-4.5.10 --transport real --allow-llm `
  --auth-file formal_experiment/configs/s2_12_api_authorization_D-REST.json `
  --stage-id D-REST `
  --resume-from-ledger formal_experiment/data/predictions/s2_12_direct_llm_v1.ledger.jsonl `
  --output-dir formal_experiment/data/predictions/s2_12_direct_llm_v1

# Fallback F-1 / F-2 / F-3（9/9/9；每阶段各一份授权文件，链式 resume）
python formal_experiment/scripts/run_s2_12_sun_llm_fallback_v1.py `
  --runtime-home D:/environment/stanford-corenlp-4.5.10 --transport real --allow-llm `
  --auth-file formal_experiment/configs/s2_12_api_authorization_F-1.json `
  --stage-id F-1 --output-dir formal_experiment/data/predictions/s2_12_sun_llm_fallback_v1
```

**Stage 结构 / 每阶段 cap**：

| Stage | Arm | payloads | call cap | 时段 | 建议 USD cap |
|---|---|---|---|---|---|
| D-CAL | direct | 1 | 1 | off-peak only | ≤1.00 |
| D-REST | direct | 35 | 35 | any（授权决定） | 按剩余预算 |
| F-1/F-2/F-3 | fallback | 9/9/9 | 9/9/9 | any（授权决定） | 按剩余预算 |
| 全局（每份授权文件） | — | — | — | — | global caps：input ≤63,000,000、output ≤258,048、USD ≤84.18（或批准值） |

**成本计算方法（授权绑定价格快照）**：
`累计成本 = cache_hit_tokens×hit_price + cache_miss_tokens×miss_price +
output_tokens×output_price`（每 1M tokens 换算）；provider 不返回 cache hit/miss
拆分时，全部 input 按**保守 cache-miss 价格**计（授权合同规定）。`cost_usd`
由真实 response usage 累积，禁止硬编码 0。

**恢复合同**：每成功响应后立即 append-only hash-chained 账本
（`<output-dir>.ledger.jsonl`，位于 capsule 同目录外侧）；resume 校验 hash 链、
拒绝重复调用已记录 payload、从下一个预注册 payload 继续、retry 恒 0、
不得据已有输出修改后续请求；partial 账本必须标 partial，正式 final predictions
只在整 arm（36/27）完成后发布。

## 3. 请求参数、硬上限与价格（v2 → v3 保持一致，待用户批准）

- **模型**：`deepseek-v4-pro`（官方页面模型版本 `DeepSeek-V4-Pro-0813`；模型 ID
  钉死 deepseek-v4-pro，1M context、最大输出 384K；配方恒用 max_tokens=4096）。
- **请求数量**：63（direct 36 + fallback 27）；绝对配置硬上限 108；retry=**0**。
- **output-token cap**：单次 4,096；总计 **258,048**（direct 147,456 + fallback
  110,592）。
- **input-token cap（待批准）**：`max_billed_input_tokens_total = 63,000,000`
  （官方 1M context × 63 calls 的极端保守上界；**不是**预计消费，见 §6 分阶段建议）。
- **USD cap（待批准；v2 按官方新价重算）**：**84.18（peak）/ 42.09（off-peak）**
  ——官方价已于 2026-08-19/20 上调（v4-pro input cache-miss 0.435→0.66/1.32、
  output 0.87→1.98/3.96，每 1M tokens）；v1 的 27.63 已作废。
- **请求体字节**：单次 ≤ 17,493；总计 ≤ 749,805（锁定 payload）。
- **sampling/transport**：temperature=0、top_p=1、max_tokens=4096、
  seed=unsupported_or_omitted；Direct-LLM：stream=false、thinking.disabled、
  response_format=null；Fallback：stream=false、thinking.disabled、
  response_format=json_object（tools_sent=false）。
- **时段**：off-peak-only 授权时，调用前检查北京时间；peak=09:00–12:00、
  14:00–18:00（UTC+8），进入 peak 立即停止（runner 内置 `check_off_peak_only`）。
- **价格复核**：运行前必须再次重验官方价格；若再变动需重新批准 cap。

## 4. 授权文件 schema（`configs/schemas/s2_12_api_authorization_v1.schema.json`）

必需字段（任一缺失 → 第一次 transport 调用前拒绝）：

| 字段 | 含义 |
|---|---|
| `schema_version` | `s2_12_api_authorization@1.1.0` |
| `authorization_sentence_utf8_sha256` | 用户授权句 UTF-8 的 SHA-256 |
| `authorization_event_file` / `_sha256` | 授权事件文件路径 + 原始字节 SHA-256 |
| `model` | `deepseek-v4-pro` |
| `calls` | `{direct_llm: 36, sun_llm_fallback: 27}` |
| `stage_id` | `D-CAL` / `D-REST` / `F-1` / `F-2` / `F-3` |
| `stage_payload_hashes` | 本 stage 的 payload SHA-256（预注册 subset，任意子集拒绝） |
| `stage_call_cap` | 本 stage 调用上限 |
| `global_input_token_cap` / `global_output_token_cap` / `global_usd_cost_cap` | 累计全局上界 |
| `allowed_windows` | `any_time` 或 `off_peak_only`（每次调用前检查） |
| `price_snapshot` / `price_checked_at_utc` | 官方价格快照对象（schema `s2_12_price_snapshot@1.0.0`）＋核验时间 |
| `runner_implementation_hashes` | direct/fallback runner + `s2_12_execution` + `llm_client` + `h1_transport` 各自 SHA-256（按 arm 校验对应 runner） |
| `input_config_prompt_hashes` | input / preflight-lock / direct-prompt / fallback-prompt 的 SHA-256 |
| `prev_stage_ledger_hash` | 前一 stage 账本末条 hash（首 stage 为空串） |
| `final_63_payload_hashes` | 恰好 63 个 request-body SHA-256（最终 63 集合承诺） |
| `retry` | `0` |
| `gold_isolation` | `api_arms_must_not_read_gold: true`（+ evaluation_only_after_predictions_are_locked） |

授权事件 builder：`scripts/build_s2_12_auth_event_v1.py`（**无用户原句拒绝；
默认 dry-run；本轮不 apply**）。未来真实创建后固定路径为
`formal_experiment/configs/s2_12_api_authorization_<STAGE>.json` +
`configs/s2_12_api_authorization_event_<STAGE>.json`（无占位符）。

## 5. runner 与绑定资产 hash（v4，磁盘实际值；verifier 随时重取）

| 资产 | SHA-256（完整） |
|---|---|
| `src/bpc_hybrid/s2_12_execution.py` | `53ad3d8ded9e404d17ae65b8dcfe7f77dce82c90b6ca02c03f9947319545d773`（2026-09-07 补齐 raw 落盘/事故记账/链式骨架后重算；旧值 `df391a03…` 为历史） |
| `scripts/run_s2_12_direct_llm_v1.py` | `57c7cb9b4f66297e086871a32503163861ef0a7bbea9b57450c148ab38dd08f5`（2026-09-07 增加 `--raw-dir` 后重算；旧值 `919444ec…` 为历史） |
| `scripts/run_s2_12_sun_llm_fallback_v1.py` | `1f5c0e5f5475e0635e99b913ecfa7629c6869588fcf0515384afb3bcdf522b52`（2026-09-07 增加 `--raw-dir` 后重算；旧值 `13f7d775…` 为历史） |
| `scripts/build_s2_12_auth_event_v1.py` | `c7f4f2644de0b854738f2e40a388c1316a726d5a3b30c48bbb1c241d495e1484` |
| `configs/s2_12_fallback_trigger_plan_v1.json` | `857149a6c5f4beb608969c2af119708f44db5f4575ac4d7f840bf2b58224cd72` |
| `configs/schemas/s2_12_api_authorization_v1.schema.json` | `524d9c48bae181adff292e2d08d946d2e89162e239a78ff3eb7732cdb5fe00f1` |
| `configs/s2_12_api_arms_preflight_v1.json`（锁） | `3b62ba6658531a09469c7ecdecacc5797674ed795d62c55f389600586b2f221c` |
| `outputs/reports/s2_12_api_preflight_v1.json` | `c7d33f956464f54b9b76145a1874d9111e3e41f1a904bc3751edc8b8e3c90314` |
| `data/input/s2_12_complex_corpus_formal_input_v1.json` | `892d4284ea70c38f82a47f821c13622f1b07744253429e466038ddb5db96660e` |
| direct prompt v6 | `3aa64877cd4c4dae9f13cb40d102c3c9b04cc9bee5d478c34ad04621c0ede895` |
| fallback prompt | `00fe02996914e17f30962147d7a9f2c71a92d2479ba4eff343583a139bb1537b` |
| `llm_client.py`（transport/policy 实现） | `232284dadc2b1f867ee885db1d111360f005b29a52662619af2dffee4f128e24` |
| `h1_transport.py`（policy 实现） | `f9efba42509eb85be522a45ee9ee4cf728ec1437945dfb4189bd7f4cc0d45b77` |

授权文件中的 `runner_implementation_hashes` 必须分别绑定 direct/fallback runner、
`s2_12_execution`、`llm_client`、`h1_transport` 的上表实际 SHA-256；校验时按当前
arm 只比较对应 runner hash（fallback 不再与 direct 比较）。任何不匹配 → 第一次
transport 调用前拒绝。运行 `verify_s2_12_runner_safety_v2.py` 可随时重取。

授权文件中的 `runner_implementation_hashes` 必须以 `run_s2_12_direct_llm_v1.py` /
`run_s2_12_sun_llm_fallback_v1.py` 的上表实际 SHA-256 填写（任何不匹配 → 第一次
transport 调用前拒绝；运行 `verify_s2_12_runner_wiring.py` 可随时重取）。

## 6. 分阶段成本建议（v3；零调用离线估计）

**现状**：63M input cap 是“每调用耗满 1M context”的极端上界，不是合理预计消费。
官方 `deepseek-v4-pro` tokenizer 本地不可用（无官方离线分词资产），**官方计费
input tokens 只能从真实响应 usage 获得**。本地 Legal-BERT WordPiece proxy 总计
207,468 tokens、UTF-8 请求体总计 749,805 bytes —— 两者都不是 billing count。

**离线可证明的保守规划上界**（planning only）：
- 按“max(2×proxy, bytes/1.8)”的经验上界，63 个请求体合计 ≈ **416,559 input
  tokens**（远小于 63M）；output 恒为 258,048。
- 若以该规划上界按官方新价（peak cache-miss input $1.32/M、output $3.96/M）：
  input ≈ $0.55 + output ≈ $1.02 ≈ **$1.57（peak）**；off-peak ≈ $0.28 + $0.51
  ≈ **$0.79**。**以上为规划估算，不是计费承诺。**

**建议的执行授权方案**：
1. **单请求计费校准（第 1 次调用）**：先只发 1 个已锁定请求体（direct_llm 第 1
   条），从真实响应的 `usage.prompt_tokens/completion_tokens` 拿到官方 tokenizer
   的精确换算比；据此把 63M / $84.18 换成“按真实 token 换算后的合理上界”。
2. **分阶段授权（剩余 62 次）**：校准后分 2–3 个小阶段（如 20+20+22 或按预算
   比例），每阶段结束核对累计 input/output tokens 与 USD；任一阶段超出按新比例
   折算的 cap 即硬停止。
3. **peak/off-peak 硬停止**：若只批准 off-peak（peak=北京时间 09:00–12:00、
   14:00–18:00），runner 在每次调用前检查时段，进入 peak 立即停止（已实现
   `check_off_peak_only`）。cap 取 42.09（off-peak）或 84.18（any_time）。
4. **官方价格重验**：每次真实运行前重验官方价格页，价格变动则重算并再次征得同意。

## 7. 已实现工程（runner safety v2，零 API 零网络）

- 共享契约 `src/bpc_hybrid/s2_12_execution.py`（v2）：锁/输入/报告核验、63 payload
  逐条重建比对、**per-call PayloadLock**（fake 与 real transport 共用）、usage/成本
  计算（`per_call_cost`/`CumulativeState`）、**per-call caps + off-peak**
  （`check_pre_call`/`check_post_call`）、**append-only hash-chained 账本**
  （`ExecutionLedger` + resume）、**StageExecutor**（含 stage subset、
  resume-from-ledger、partial 状态）、`publish_stage_capsule`（final predictions
  仅整 arm 完成后发布）、授权 v1.1.0 校验（每 arm 独立 runner hash）。
- `run_s2_12_direct_llm_v1.py`：`--stage-id D-CAL|D-REST`、`--auth-file`、
  `--resume-from-ledger`；real 路径 `LLMConfig.from_env(project_root=ROOT,
  load_project_env=False)`（不读项目 `.env`）。
- `run_s2_12_sun_llm_fallback_v1.py`：`--stage-id F-1|F-2|F-3`（9/9/9 分区）、
  comparison-only；同样禁读项目 `.env`，独立 runner hash 绑定。
- `scripts/build_s2_12_auth_event_v1.py`：离线授权事件 builder（无原句拒绝、
  默认 dry-run、本轮不 apply；未来固定输出路径见 §4）。
- 授权 schema v1.1.0（stage 绑定）；frozen plan（27 条）不变。
- 独立 verifier `verify_s2_12_runner_safety_v2.py`：**RUNNER SAFETY V2 VERIFIED /
  API NOT AUTHORIZED / ZERO CALLS**。
- focused tests：`test_s2_12_runner_safety_v2.py`（scripted real-like transport、
  30+ 场景、零网络）+ `test_s2_12_runner_wiring.py`（更新到 v2 接口）。

## 8. 硬停止条件（v4；含 v2 新增项）

1. 无逐条匹配的用户 API 授权（授权文件缺失/字段缺失/hash 不匹配）；
2. 返回 model ≠ deepseek-v4-pro；
3. input/source/prompt/config/implementation/payload hash 任何漂移
   （**每次真实调用前重算实际 body SHA**，非仅启动时）；
4. call、request-body byte、input-token、output-token 或 USD cap 任一将超
   （**调用前保守上界 + 响应后真实累积双重检查**）；
5. retry≠0；
6. Gold/decisions/proposals/Oracle/Gold Rule Records 对任一 arm 可见；
7. 官方价格无法在运行前重验；
8. 未预注册 runtime incident（lost/recovery/retry 记录并停顿）；
9. off-peak-only 授权在 **每次调用前** 检查北京时间；运行中进入 peak 立即停止；
10. provider usage 缺失/损坏 → fail closed（不猜测 token 数）。

## 9. 授权句模板（v4；复制即用，须用户亲自发出并创建授权文件）

> 我授权在 S2.12 复杂语料上按预注册 stage 运行
> Direct-LLM（`direct_llm`，D-CAL 1 次 / D-REST 35 次）和
> Rules+LLM-Repair（`sun_llm_fallback`，F-1/F-2/F-3 各 9 次）的真实 DeepSeek API，
> 模型仅限 `deepseek-v4-pro`，严格使用 `s2_12_api_preflight_v1.json` 锁定的
> 63 个请求体（单次 ≤ 17,493 bytes、总计 ≤ 749,805 bytes），`retry = 0`；全局
> output tokens ≤ 258,048（单次 ≤ 4,096）；总计费 input tokens ≤ 63,000,000；
> 总 USD 成本 ≤ **84.18**（若仅 off-peak 运行可改为 ≤ 42.09：北京 09:00–12:00、
> 14:00–18:00 之外，每次调用前检查）；D-CAL 单请求 USD ≤ 1.00、input ≤ 1,000,000、
> off-peak only；运行前重验官方价格；任一模型/输入/source/prompt/config/payload/
> hash 漂移、实际 body SHA 与锁定不符、Gold 隔离违背、cap 将超或 peak 时段
> （off-peak-only 时）均在调用前硬停止；不得调用 Oracle，不读取 `.env`。我知晓
> 实际 billing input tokens 与 cost 只能来自真实响应 usage；授权事件与授权文件
> 由 `build_s2_12_auth_event_v1.py` 在收到本句后生成（dry-run 先示）。

**用户还需**：(1) 逐字提供授权原句（builder 计算句 hash 与事件文件 hash）；
(2) 批准/调整每阶段 cap；然后执行 §2 命令（`--auth-file` 指向固定输出路径）。

## 10. 本申请之外的阻塞

- S2.13 freeze 与 Stage 3 / 9 个 GDPR Gold Rule Records / S3.7 Oracle 授权均为
  独立事项，不随本申请自动解锁。
- 未获授权前：0 calls、cost=null、不读取 `.env`；runner 默认 fake transport；
  API 状态保持 `API BLOCKED / ZERO CALLS`。

## 11. 2026-09-06 论文收尾合并 API 授权申请

> 本节为论文收尾阶段新增的**合并授权申请**（两批分开计费与 cap）。前面 §1–§10
> 的内容与数字**原样保留、不受影响**。本申请仍然 ZERO API / ZERO CALLS：不读取
> `.env`、不改 Gold、不启动 Oracle；本次准备**不创建任何授权文件**，实际调用保持 0，
> 直到用户逐字发出授权句并另行批准/创建授权文件。

### 11.1 合并请求一览（两批，合计 137 次调用）

| 批次 | 内容 | 输入 | 调用数 | 模型 / prompt / retry | cap（引用报告） |
|---|---|---|---|---|---|
| **A（unchanged，S2.12 复杂语料）** | `direct_llm` 36 次 + `sun_llm_fallback` 27 次 = **63 次**；计划与 caps **不变** | `data/input/s2_12_complex_corpus_formal_input_v1.json`（sha256 `892d4284…`，36 records） | 63 | `deepseek-v4-pro`；direct 用 v6 prompt（sha `3aa64877…`）、fallback 用 `rule_first_llm_fallback_prompt`（sha `00fe0299…`）；retry=0 | 与既有请求完全一致（见 §2–§3 与 `outputs/reports/s2_12_execution_readiness_v4.json` + `outputs/reports/s2_12_api_preflight_v1.json`）：请求体 ≤17,493 B/次、总计 ≤749,805 B；global input ≤**63,000,000**、output ≤**258,048**（单次 ≤4,096）、USD ≤**84.18（peak）** / ≤**42.09（off-peak-only）**；官方价格运行前必须重新核验 |
| **B（new，GDPR 衔接 Direct-LLM 臂）** | GDPR Stage-2→Stage-3 衔接的 `direct_llm` 臂：每句 1 次 = **74 次**；**不含** `sun_llm_fallback`（GDPR 衔接只需 direct_llm vs rules_only 配对）；本批**不覆盖**任何其它语料 | `data/input/gdpr7_stage2_input_v1.json`（sha256 `558b8013…`；9 条 GDPR 规则文本、**74 句**、Gold-blind；每句输入 = 该句 `approved_text_en`） | 74 | `deepseek-v4-pro`（发布别名 DeepSeek-V4-Pro-0813）；锁定的 D1 配方：prompt v6（sha `3aa64877…`）、temperature 0、top_p 1、max_tokens 4096、stream=false、thinking disabled、response_format=None；retry=0；**off-peak only**（每次调用前检查北京时间 peak 09:00–12:00 / 14:00–18:00） | 由 `outputs/reports/gdpr7_direct_llm_preflight_v1.json` 渲染并锁定（74 个请求体，逐条 body SHA/字节数/句子 hash 绑定，无原句提交）：请求体 ≤18,459 B/次、总计 1,297,742 B；Legal-BERT proxy 共 367,333 tokens（**规划代理，非计费**；官方 tokenizer 本地不可用，真实 billing input 只能来自响应 usage）；global input cap（保守公式 74×1M context）≤**74,000,000**、output ≤**303,104**（74×4,096）、USD ≤**2.61**（官方 2026-08-19/20 peak 价 input cache-miss $1.32/M、output $3.96/M 按 planning 上界 734,666 tokens + 20% margin 计算；off-peak 折半价下 ≤**1.31**）；官方价格运行前必须重新核验 |

**合计**：63 + 74 = **137 次调用**；每批各自独立 cap（见上表），**不合并成单一总 USD
cap**（若需单一保守加总上界 ≈ US$84.18 + US$2.61 ≈ **US$86.79**，仅供预算参考）。

Batch B 的估算公式与 1.2× margin 依据（与既有实践一致）：

```
per-call body bytes   = UTF-8 length of json.dumps(final_body)      # S2.12 payload lock 约定
local_proxy_tokens    = Legal-BERT WordPiece over system+"\n"+user  # 规划代理，非 billing
planning_input_bound  = max(2 × proxy_total, body_bytes_total / 1.8) # S2.12 申请 §6 经验上界
recommended_usd_cap   = ceil((planning_input_bound×1.32 + 303,104×3.96)/1e6 × 1.2 × 100)/100
                        # = US$2.61（peak）；off-peak 价（0.66/1.98）下 = US$1.31
```

其中 ×1.2（20% USD margin）与
`scripts/run_barrientos_paper_ablation_v1.py`（`budget.calculation: "20% USD margin"`）
及 `scripts/build_d1_prompt_factorial_contract_v1.py`（`usd_cap = ceil(peak_cost × 1.2)`）
的既有预算做法一致；peak 单价 $1.32/$3.96 与 §3 记录的 S2.12 v3 请求同一官方价。

### 11.2 失败处理声明（两批通用，沿用 S2.12 executor 纪律）

- **存疑条目绝不自动重发**：retry 恒 0；超时/丢失/ambiguous 的响应只记入账本并上报，
  不据已有输出修改后续请求；恢复只从下一个预注册 payload 继续，且须先复核账本。
- **调用后硬停止**：provider usage 缺失/损坏 → fail closed（不猜 token 数）；返回
  model ≠ `deepseek-v4-pro` → 中止；累计 input/output/USD 或 call cap 任一将超 → 停止。
- **partial 运行保留账本**：append-only hash-chained 账本（`.ledger.jsonl`）绝不覆盖，
  resume 校验 hash 链、拒绝重复调用已记录 payload；partial 必须标 partial，正式
  final predictions 只在整臂完成（A：36/27；B：74/74）后发布。
- **官方价格重验**：每次真实运行前重验官方价格页；价格变动即重算并再次征得同意。
- **Gold 隔离**：两批 API 臂均不得读取 Gold/decisions/proposals/Oracle/Gold Rule
  Records；Batch B 输入 pack 本身 Gold-blind（仅法条文本与句子 hash）。

### 11.3 授权句模板（复制即用；须用户亲自逐字发出并另行创建授权文件）

> 我授权合并运行论文收尾 API 批次，共 **137 次**调用，模型仅限
> `deepseek-v4-pro`（DeepSeek-V4-Pro-0813），`retry = 0`：
> **Batch A（S2.12 复杂语料，unchanged）**：`direct_llm` 36 次 +
> `sun_llm_fallback` 27 次，严格使用 `s2_12_api_preflight_v1.json` 锁定的 63 个
> 请求体（单次 ≤17,493 B、总计 ≤749,805 B），global input ≤63,000,000、
> output ≤258,048（单次 ≤4,096）、USD ≤84.18（仅 off-peak 运行则 ≤42.09）；
> **Batch B（GDPR Stage-2→Stage-3 衔接 Direct-LLM 臂）**：对
> `gdpr7_stage2_input_v1.json` 的 74 个 `approved_text_en` 句子每句 1 次调用，
> 仅 `direct_llm`（不含 `sun_llm_fallback`），严格使用
> `gdpr7_direct_llm_preflight_v1.json` 锁定的 74 个请求体，global input
> ≤74,000,000、output ≤303,104（单次 ≤4,096）、USD ≤2.61（peak 规划价 +20%
> margin；off-peak 折半价下 ≤1.31），**off-peak only**（北京时间 09:00–12:00 /
> 14:00–18:00 之外，每次调用前检查）；运行前重验官方价格；两批任一模型/返回模型、
> 输入、source、prompt、config、payload/hash、官方价格、Gold 隔离或 cap/时段违背
> → 调用前硬停止；存疑条目不自动重发；partial 运行保留账本；不读取 `.env`、不调用
> Oracle。我知晓实际 billing input tokens 与 cost 只能来自真实响应 usage；本准备未
> 创建任何授权文件，授权事件与授权文件须由对应 builder 在收到本句后生成。

English mirror:

> I authorize the merged paper-wind-down API batches with **137 total calls**
> on `deepseek-v4-pro` (DeepSeek-V4-Pro-0813) only, `retry = 0`:
> **Batch A (S2.12 complex corpus, unchanged)**: 36 `direct_llm` + 27
> `sun_llm_fallback` calls strictly using the 63 locked request bodies of
> `s2_12_api_preflight_v1.json`, global input ≤63,000,000, output ≤258,048,
> USD ≤84.18 (≤42.09 if off-peak-only); **Batch B (GDPR Stage-2→Stage-3
> linkage Direct-LLM arm)**: 74 calls, one per `approved_text_en` sentence of
> `gdpr7_stage2_input_v1.json` (direct_llm only; no sun_llm_fallback),
> strictly using the 74 locked request bodies of
> `gdpr7_direct_llm_preflight_v1.json`, global input ≤74,000,000, output
> ≤303,104, USD ≤2.61 (off-peak half-price alternative ≤1.31), off-peak only;
> official prices re-verified before the run; any model/input/source/prompt/
> config/payload/hash/price/Gold-isolation/cap/window violation hard-stops
> before the call; in-doubt entries are never auto-resent; partial runs keep
> their ledgers; no `.env` read and no Oracle. This preparation created no
> authorization file; the authorization event/file must be generated by the
> corresponding builder only after I issue this sentence.

**明确声明**：本合并申请（2026-09-06）未创建、也不要求创建任何授权文件；
两批 `authorized: false`、`calls_made: 0` 将一直保持，直到用户授权。

## 12. 2026-09-06 executor contract for GDPR 74-call batch

> 本节记录 GDPR 74-call Direct-LLM 批次的**可执行链与执行契约**（零 API / 零网络 /
> 零 `.env` 验证已完成；真实调用仍 pending 用户授权句 + 授权事件文件）。前面 §1–§11
> 内容与数字**原样保留、不受影响**。本节不修改任何既有文件，仅新增三个交付物：
> executor 脚本、执行契约、离线验证测试，以及本 doc 追加。

### 12.1 交付物

| 文件 | 作用 |
|---|---|
| `scripts/run_gdpr7_direct_llm_v1.py` | GDPR Stage-2 Direct-LLM 74-call 真实 executor（fake/real 双 transport、per-call payload lock、caps、off-peak、append-only hash-chained ledger + resume、raw JSONL、canonical 预测 capsule） |
| `configs/ablations/gdpr7_direct_llm_execution_contract_v1.json` | 执行契约：bound commit `6263f08`、74-call 固定计划（preflight report 行、按 sample_id 顺序）、model/sampling/transport pins、hash set（input/preflight/registry/prompt/executor）、caps、authorization=null + 授权句模板（scope `gdpr7_direct_llm_v1:74`） |
| `tests/test_gdpr7_direct_llm_executor_v1.py` | 离线 fake-transport 全 74 请求验证（8 场景 a–h，零网络） |

### 12.2 Executor 入口命令

Fake 验证（74/74、零网络、cost=0；程序验证专用，非实验结果）：

```powershell
python formal_experiment/scripts/run_gdpr7_direct_llm_v1.py --fake-transport
# 等价别名: --runtime-dry-run
# 默认输出: outputs/development/gdpr7_direct_llm_raw_v1/
#           (raw_responses.jsonl + ledger.jsonl) 和
#           outputs/development/gdpr7_direct_llm_v1/
#           (predictions.json / telemetry.json / cost.json / manifest.json)
```

真实运行（**用户授权后**；授权事件文件缺失 → 第一次 send 前硬拒绝）：

```powershell
python formal_experiment/scripts/run_gdpr7_direct_llm_v1.py `
  --contract-file formal_experiment/configs/ablations/gdpr7_direct_llm_execution_contract_v1.json `
  --authorization-file <gdpr7-direct-llm-authorization-event-file>
```

Resume（partial/aborted 后只重发从未尝试的请求；completed / in_doubt 绝不重发）：

```powershell
python formal_experiment/scripts/run_gdpr7_direct_llm_v1.py --fake-transport --resume
python formal_experiment/scripts/run_gdpr7_direct_llm_v1.py `
  --contract-file formal_experiment/configs/ablations/gdpr7_direct_llm_execution_contract_v1.json `
  --authorization-file <gdpr7-direct-llm-authorization-event-file> --resume
```

Contract 文件路径：`formal_experiment/configs/ablations/gdpr7_direct_llm_execution_contract_v1.json`
（schema `gdpr7_direct_llm_execution_contract@1.0.0`；bound commit
`6263f08bd5cfe54f21a826b28ce5f1bc48c97967`）。

### 12.3 代码内硬上限（in code，非仅文档）

- calls = 74（一次/句）；retry = 0；model pin `deepseek-v4-pro`
  （published alias `DeepSeek-V4-Pro-0813`）；temperature 0、top_p 1、
  max_tokens 4,096；stream=false、thinking disabled、response_format=None
  （全部经每次调用的 payload-lock body SHA 与 preflight 报告锁定逐条一致而强制）。
- global input ≤ **74,000,000**（74 × 官方 1M context 的保守 proxy-equivalent 上界，
  见 preflight 报告）；output 单次 ≤ **4,096**、总计 ≤ **303,104**；
  USD ≤ **2.61（peak）/ 1.31（off-peak）**（规划上界 + 20% margin 的 preflight 推荐值）。
  planning（Legal-BERT proxy）tokens 是**规划代理，不是 billing tokens**；真实 billing
  input 只能来自真实响应 usage；官方价格运行前必须重验（授权事件含价格快照 + 重验时间戳）。
- 每次 send 前：授权事件校验（缺 → 硬拒绝）、off-peak（北京时间 peak 09:00–12:00 /
  14:00–18:00，周一–五）逐次检查、call/input/output/USD caps（含本请求规划上界
  的保守预检）；每次响应后：usage 捕获、returned model 校验、真实累计 caps 复查。
  返回模型不符 → 中止；usage 缺失 / decode 非 ok → **in_doubt**（绝不自动重发）。

### 12.4 授权事件要求 + 可复制的授权句模板

真实执行在存在并验证以下授权事件文件前一律拒绝（缺 → 第一次 send 前硬停止、无任何
输出发布）：schema `gdpr7_direct_llm_authorization_event@1.0.0`，含用户授权原句及其
UTF-8 SHA-256、**scope 恰为 `gdpr7_direct_llm_v1:74`**、模型/别名/retry、calls=74、
allowed_windows=`off_peak_only`、off-peak 官方价格快照 + `official_price_reverified_at_utc`、
caps 与代码内硬上限一致、hash_set 与契约逐条一致（含契约文件自身 SHA）、Gold 隔离声明。

可复制的授权句模板（须用户亲自逐字发出并据此生成授权事件文件；scope 固定为
`gdpr7_direct_llm_v1:74`）：

> 我授权在 GDPR Stage-2→Stage-3 衔接的 Direct-LLM 臂上（scope
> `gdpr7_direct_llm_v1:74`）对 `gdpr7_stage2_input_v1.json` 的 74 个
> `approved_text_en` 句子每句调用 1 次 `deepseek-v4-pro` 真实 API（DeepSeek-V4-Pro-0813），
> 共 74 次、retry=0、off-peak only（北京时间 09:00–12:00 / 14:00–18:00 之外，
> 每次调用前检查）；输入仅限 `gdpr7_direct_llm_preflight_v1.json` 锁定的 74 个请求体；
> global input ≤74,000,000、output ≤303,104（单次 ≤4,096）、USD ≤1.31（off-peak 规划价
> +20% margin；绝不超 2.61）；运行前重验官方价格；任一模型/返回模型/输入/source/prompt/
> config/payload/hash/官方价格/Gold 隔离/cap/时段违背 → 调用前硬停止；存疑条目不自动
> 重发；partial 运行保留账本；不读取 `.env`、不调用 Oracle。

English mirror:

> I authorize running the GDPR Stage-2->Stage-3 linkage Direct-LLM arm (scope
> `gdpr7_direct_llm_v1:74`): 74 real `deepseek-v4-pro` API calls (published
> alias DeepSeek-V4-Pro-0813), one per `approved_text_en` sentence of
> `gdpr7_stage2_input_v1.json`, retry=0, off-peak only (outside Beijing
> 09:00-12:00 / 14:00-18:00, checked before every call); input limited to the
> 74 locked request bodies of `gdpr7_direct_llm_preflight_v1.json`; global
> input <=74,000,000, output <=303,104 (per call <=4,096), USD <=1.31
> (off-peak planning price +20% margin; never above 2.61); official prices
> re-verified before the run; any model/returned-model/input/source/prompt/
> config/payload/hash/price/Gold-isolation/cap/window violation hard-stops
> before the call; in-doubt entries are never auto-resent; partial runs keep
> their ledgers; no `.env` read, no Oracle.

### 12.5 验证状态

- **Fake verification（程序验证，非实验结果）：74/74 requests attempted，
  74/74 ledger `completed`，74/74 canonical prediction rows `ok`
  （error_category 全 null），in_doubt=0、failed=0，cost_usd=0.00，
  零网络、零 API、不读取 `.env`；capsule 完整发布（predictions/telemetry/cost/
  manifest），manifest 记录 arm capsule path/schema/计数/cost/runtime 与
  reproduce 命令。**
- 测试文件 9/9 passed（场景 a–h：fake 全量、无授权拒绝、USD cap 预检、in_doubt +
  resume 只发余量、payload drift fail-closed、returned-model mismatch abort、
  Gold/文本隔离、linkage schema dry-load）。
- 真实调用数 = 0；未创建任何授权事件文件；`authorized: false` 保持到用户授权。


## 13. 2026-09-07 授权落地与执行链补齐（论文收尾批）

> 本节记录论文收尾阶段（2026-09-07）的状态转移：用户实际发出授权指令后，授权
> 事件/auth 文件已生成并通过 executor 同款校验；两批真实调用仍为 0（等待进程
> 环境凭据）。历史断言“授权文件未创建 / API NOT AUTHORIZED”的旧 verifier
> （`verify_s2_12_runner_safety_v2.py`、`verify_s2_12_runner_wiring.py`）在其
> `no_real_auth` 检查上按设计进入 superseded 语义（保留为授权前状态 provenance，
> 不再作为活动入口）；活动入口为 `scripts/verify_s2_12_authorization_files_v1.py`
> （70/70 PASS，绑定当前磁盘 hash 与用户 caps）。

### 13.1 授权依据与授权文件（全部已提交/待提交于同一 checkpoint）

- 用户原始指令逐字副本 `configs/paper_winddown_api_authorization_sentence_2026_09_07.txt`
  与授权依据 `configs/paper_winddown_api_authorization_basis_2026_09_07.json`；
  原句 UTF-8 SHA-256 = `27426de7a03cc8c75eae5d57ebbd11860b2ce229f7afdd55bce4fa9a08bc0dd6`。
- 批 A：`configs/s2_12_api_authorization_{D-CAL,D-REST,F-1,F-2,F-3}.json` +
  `configs/s2_12_api_authorization_event_{D-CAL,D-REST,F-1,F-2,F-3}.json`；
  每份 caps：input 63,000,000 / output 258,048（单次 4,096）/ retry=0 /
  allowed_windows=off_peak_only；USD：D-CAL=1.00、其余=42.09（用户授权 off-peak
  上界；D-CAL 含在 63 次内）。价格快照为保守 peak 价（0.044/1.32/3.96），运行时
  累计成本为保守上界；**最终成本报告由 finalize 按官方 off-peak 价
  （0.022/0.66/1.98 每百万 tokens）从真实 usage 重算**。
- 批 B：`configs/gdpr7_direct_llm_authorization_event_v1.json`（builder
  `scripts/build_gdpr7_direct_llm_authorization_event_v1.py` + 8 项测试）；
  scope=`gdpr7_direct_llm_v1:74`、caps 74,000,000/303,104/4,096/USD=1.31、
  off-peak 价快照（与 executor 常量逐项相等）、`official_price_reverified_at_utc`
  2026-09-07T12:05Z、hash_set 绑定 6 项磁盘资产；已用 executor
  `validate_contract`+`validate_authorization_event` 实测通过；74/74 假响应彩排
  complete（fresh dev 目录）。
- 官方价格重验（2026-09-07）：官方定价页（api-docs.deepseek.com/zh-cn/quick_start/
  pricing/）与 2026-08-17 生效的峰谷方案一致（deepseek-v4-pro：peak cache-hit
  $0.044/M、cache-miss $1.32/M、output $3.96/M；off-peak 半价；周末全天 off-peak；
  工作日 peak=北京时间 09:00–12:00、14:00–18:00）。未发现 2026-08-19/20 记录之后
  的价格变动，cap 沿用用户授权值（42.09 / 1.31）。

### 13.2 执行链补齐（真实运行前必须的离线实现，已测试）

- `src/bpc_hybrid/s2_12_execution.py`（hash 见 §5）：StageExecutor 可选
  `raw_dir` 参数（逐成功响应 append `content` 到 gitignored raw 目录，
  `<STAGE>.jsonl`）；transport 失败/usage 缺失按事故记账（decode_status 带
  transport_error/usage_missing 前缀）后中止、**绝不自动重发**；链式 resume
  后 `publish_stage_capsule` 的 predictions 骨架按完整账本重建（修复 D-REST/F-3
  只含本 stage 行的缺陷）。
- `scripts/run_s2_12_direct_llm_v1.py` / `run_s2_12_sun_llm_fallback_v1.py`：
  新增 `--raw-dir`。
- `src/bpc_hybrid/s2_12_response_convert.py`：direct 响应→坐标-only canonical
  （镜像 GDPR 转换链）；fallback envelope 解析。
- `scripts/finalize_s2_12_arm_v1.py`（819 行）：正式胶囊唯一发布入口
  （predictions/telemetry/cost/manifest，坐标-only、无文本/Gold 键、status=
  predictions_locked_before_gold_evaluation、拒绝覆盖）；direct=逐行转换
  （失败显式 in_doubt/failed 行）；fallback=`_rerun_b0` 文本重建后按 frozen plan
  27 行经 H1 共享链（canonicalize_patch_coordinates + apply_patch_envelope）应用
  并逐 plan 审计（accepted/rejected/unresolved）；成本按官方 off-peak 价重算。
- `scripts/evaluate_s2_12_api_arm_v1.py --arm {direct_llm,sun_llm_fallback}`：
  与 sun_rule_only 评价同 Gold（039ae8b2…）/分层（0cd725b4…，L1:31/L2:5/L3:0）/
  同一 evaluator；非全 ok 胶囊拒绝评价（fail-closed）。
- `scripts/verify_s2_12_api_arm_v1.py`：评价 capsule 独立重放验证。
- GDPR 人工裁决工作流 v1（与 API 无关的收尾面）：editable 派生
  `data/development/human_review/gdpr7_six_element_review_decisions_v1.json` +
  `src/bpc_hybrid/gdpr7_review_rules_v1.py` + 工具/校验/导入/冻结 4 脚本 + 38 项
  合成测试（真实 blank/裁决文件零触碰）。
- 测试：新增聚焦 60 项全绿（GDPR builder 8、S2.12 authorization files 3、
  S2.12 arm finalization 11、GDPR review workflow 38）；s2_12 safety+wiring 回归
  52 passed；`verify_s2_12_authorization_files_v1.py` 70/70。

### 13.3 真实运行命令（等待进程环境凭据后执行；每 stage 独立输出目录）

> **环境配置（唯一可信方式 = flat 键全集；两个真实执行器均用
> `LLMConfig.from_env(project_root=ROOT, load_project_env=False)` 只读进程环境，
> 项目 `.env` 永不打开）**。实测（2026-09-07 离线）：
> provider 必须是白名单枚举 `openai_compatible`；只设 `BPC_HYBRID_DeepSeek_*`
> 前缀变量无效（白名单无 ENABLED/MAX_TOKENS/TEMPERATURE，且未设
> `BPC_HYBRID_LLM_PROFILE` 时前缀根本不参与解析——单独提供这些变量会解析为
> enabled=false/provider=mock/model=mock/max_tokens=1024，执行器将硬拒）。
> 配置就绪性请先跑离线预检（不调用 API、不读 .env、不打印密钥）：
> `python scripts/check_api_env_ready_v1.py`（在 formal_experiment 下运行；
> 缺失任何一项即 exit 2 并列出该项）。

```powershell
# 进程环境（勿写入仓库，勿在聊天发送密钥值）——flat 键全集：
$env:BPC_HYBRID_LLM_ENABLED   = 'true'
$env:BPC_HYBRID_LLM_PROVIDER  = 'openai_compatible'   # 枚举白名单；仅此值有效
$env:BPC_HYBRID_LLM_MODEL     = 'deepseek-v4-pro'
$env:BPC_HYBRID_LLM_BASE_URL  = 'https://api.deepseek.com/v1'
$env:BPC_HYBRID_LLM_API_KEY   = '<由用户在宿主/会话环境注入的安全值>'
$env:BPC_HYBRID_LLM_MAX_TOKENS= '4096'
$env:BPC_HYBRID_LLM_TEMPERATURE='0'
$env:BPC_HYBRID_LLM_TOP_P     = '1'
python formal_experiment/scripts/check_api_env_ready_v1.py   # 期望：API ENV READY / exit 0
```

> **执行目录约定**：以下命令**在 `formal_experiment/` 目录下运行**（`cd
> formal_experiment`）；所有 `outputs/development/...` 相对路径都相对
> `formal_experiment/`，`Path.resolve()` 后全部落在 `formal_experiment/` 内，
> 不会越出活动范围写仓库根。从仓库根运行同一命令会把相对路径解析到仓库根，
> 属错误用法（2026-09-07 修正）。
>
> 预算纪律（原授权不变）：**Batch A 的 42.09 美元是整个 direct+fallback 63 次
> 的总上界**，不是每 stage/每方法各 42.09——各 stage 授权文件里
> `global_usd_cost_cap` 填的是同一 42.09（D-CAL=1.00），executor 从链式 live
> ledger 重建累计态，任何 stage 启动前发现累计已超即拒绝；最终胶囊 cost 由
> finalize 按官方 off-peak 价重算。

```powershell
# Batch A（off-peak 逐次检查；每 stage 独立 --output-dir/--raw-dir；链式 --resume-from-ledger）
python scripts/run_s2_12_direct_llm_v1.py --transport real --allow-llm `
  --auth-file configs/s2_12_api_authorization_D-CAL.json --stage-id D-CAL `
  --output-dir outputs/development/s2_12_direct_llm_stage_dcal_v1 `
  --raw-dir outputs/development/s2_12_direct_llm_raw_dcal_v1
python scripts/run_s2_12_direct_llm_v1.py --transport real --allow-llm `
  --auth-file configs/s2_12_api_authorization_D-REST.json --stage-id D-REST `
  --output-dir outputs/development/s2_12_direct_llm_stage_drest_v1 `
  --raw-dir outputs/development/s2_12_direct_llm_raw_drest_v1 `
  --resume-from-ledger outputs/development/s2_12_direct_llm_stage_dcal_v1.ledger.jsonl
# F-1/F-2/F-3 同理（每 stage 独立 raw/capsule 目录，链式 resume，同 --usd 总上界 42.09）
python scripts/finalize_s2_12_arm_v1.py --arm direct_llm `
  --raw-dir outputs/development/s2_12_direct_llm_raw_dcal_v1 `
  --raw-dir outputs/development/s2_12_direct_llm_raw_drest_v1 `
  --ledger outputs/development/s2_12_direct_llm_stage_drest_v1.ledger.jsonl
python scripts/evaluate_s2_12_api_arm_v1.py --arm direct_llm --evaluate
# Batch B（GDPR；executor 只写 dev 目录，正式 arm capsule 由后续显式 promotion 步骤发布）
python scripts/run_gdpr7_direct_llm_v1.py `
  --contract-file configs/ablations/gdpr7_direct_llm_execution_contract_v1.json `
  --authorization-file configs/gdpr7_direct_llm_authorization_event_v1.json `
  --raw-dir outputs/development/gdpr7_direct_llm_raw_real_v1 `
  --capsule-dir outputs/development/gdpr7_direct_llm_real_v1
```

每批完成后：direct/fallback→`finalize_s2_12_arm_v1.py --arm …` +
`evaluate_s2_12_api_arm_v1.py --arm …`；GDPR 74→显式 promotion 至
`data/predictions/gdpr7_direct_llm_v1`（可执行步骤见 §13.4/D 批实现）→
`run_gdpr_s2_s3_linkage_v1.py` 消费 → 成对比较与变化案例报告。

### 13.4 promotion 与验收钩子（2026-09-08 已实现为可执行步骤）

- S2.12 API arm：`scripts/finalize_s2_12_arm_v1.py` 即正式 capsule 发布入口
  （`data/predictions/s2_12_direct_llm_v1` / `data/predictions/s2_12_sun_llm_fallback_v1`，
  坐标-only），随后 `scripts/evaluate_s2_12_api_arm_v1.py --arm direct_llm|sun_llm_fallback`。
- GDPR 74：`scripts/promote_gdpr7_direct_llm_arm_v1.py`（默认 dev capsule
  `outputs/development/gdpr7_direct_llm_real_v1` → 目标
  `data/predictions/gdpr7_direct_llm_v1`；`--dry-run` 默认/`--apply`）：
  校验 telemetry.status==complete、74/74 ok 且 error_category 全 null、
  真实运行门禁（拒绝 fake rehearsal）、schema identity、manifest↔文件 sha、
  文本/Gold 键 containment、input/preflight 绑定；目标不存在才原子发布 +
  promotion manifest（`gdpr7_direct_llm_promotion@1.0.0`），并打印下一步衔接命令。
- 衔接命令（promotion 后执行，Task D 已接通）：
  `scripts/run_gdpr_3type_linkage_v1.py`（`--arm all|reference,rules_only,direct_llm`，
  direct 胶囊经参数化 converter 双 schema 探测消费；`--allow-missing-arm` 可跳过
  缺失来源继续其它来源）；
  `scripts/run_gdpr_s2_s3_linkage_v1.py`（四类扩展，ARM_PATHS["direct_llm"] 就绪，
  substitution_changes 带机器 reason）；
  `scripts/run_s3_formula_repair_v2.py --sources reference,rules_only,direct_llm
  --direct-capsule <path>` 与 `scripts/reevaluate_s3_extended_unified_v1.py`
  （统一五分类来源参数化；direct 源要求胶囊存在且 74/74 ok 才计入）。
- 每次提交后按第五节验收钩子重跑：
  `python scripts/verify_s2_12_authorization_files_v1.py`（70/70 PASS）与
  `python -m pytest tests/test_s2_12_authorization_files_v1.py -q`，
  并核验 `.gitattributes` 钉住的 LF 资产在 `git checkout` 后仍为原始 LF 字节
  （回归测试已内置）。
## 14. SEP-C1-B 完整 E/S/J 2^3 Prompt 消融预算与授权草案（2026-09-14，零 API）

**状态**：prepared_not_run。本节只准备授权材料；未创建授权事件，未调用真实 API，
未修改可执行 prompt、检查器或 Gold。上一项 SEP-C1-B 交付见
`outputs/reports/sep_c1b_factorial_budget_plan_v1.md` 与 `paper/ABLATION_MATRIX.md`
SEP-C1-B 节。

**范围与调用数**：同一批次重跑 8 个 E/S/J 组合 x 固定 EStG-150 150 条 x 2 repeats
= **2400 新增 calls**。2026-08-30 的四条单因素臂（600 calls）配置匹配，但只覆盖
`111/011/101/110` 四个格子且与高阶层因子模式/批次混杂，因此**主推荐不扣除**
旧 600 用作因子单元；非推荐复用变体若复核通过可扣为 repeat-01，新增 1800 calls，
但不得用于主交互因果解释。

**固定资产与采样**：输入
`data/input/estg150_formal_inference_input_v2.json`（SHA256
`52a73aa1109970b6c4fbc17214b0828ed0dd64b330001e884cdc803b1ce81dc2`）；evaluator
`sun_literal_overlap_evaluation@2.0.0`（config SHA256
`352113b568c6075c8b01dafa5fdf2e5ab4a1454bb10933cd2f9c27f5c008cc3f`）；Gold 以冻结
commit `56d2b03` 的 Layer E + membership 构建，正式件 `estg150_formal_gold_v1.json`
SHA256 `c31a514a6b58b640ed020c380c0b7bed136dc9574b2c98c98dedec1ecdb57100`。模型
`deepseek-v4-pro`（release `DeepSeek-V4-Pro-0813`），temperature=0、top_p=1、
max_tokens=4096、retry=0、stream=false、thinking disabled、response_format=null；
仅 off-peak；API arm 不读 Gold。

**预算 caps**：预计 input 8,687,550 tokens；input cap 13,031,325；output cap
9,830,400；USD cap **67.36**（peak 价格快照 2026-08-30）；off-peak CNY envelope
**229.63 元**。预期成本（外推参考，非上限）约 $16.11 / 54.92 元。价格来源
`https://api-docs.deepseek.com/zh-cn/quick_start/pricing/`；本轮 2026-09-14
**未联网复核**，执行前必须再次核验，价格或模型 release 变化则停止并重新授权。
可选第三重复 +1200 calls / +$8.05 预期不在本授权内，另需单独授权。

**失败与分析约定**：失败包括 API error、空响应、非 JSON、schema/cross-field
invalid、identity mismatch、无法进入 canonical six-field record；失败保留在 150
分母，逐 arm/repeat 记 `failed_count`/`valid_output_rate`/`invalid_attempt_count`。
按 E,S,J 拟合全因子模型，主效应为边际均值差、交互为差中之差；按 150 sample_id
整簇 bootstrap（B=10,000）报告 95% CI；失败率 >5% 标记不稳定，>10% 暂停该组合
因子解释；不做未预注册 p 值声明。

**授权草案句（用户亲自逐字发出后才创建授权事件）**：
`我明确授权执行 SEP-C1-B 完整 E/S/J 2^3 Prompt 消融实验：2400 calls，模型 deepseek-v4-pro（DeepSeek-V4-Pro-0813），temperature=0、top_p=1、max_tokens=4096、retry=0；固定 EStG-150 v2 输入与冻结 Stage 2 Gold/evaluator；USD 硬上限 67.36（peak）、off-peak 229.63 元；仅在北京时间闲时执行，超过任一上限立即停止，不自动续跑。`

**下一实现批次（仍未执行）**：新增缺失四臂；生成八臂 manifest/prompt hashes；
扩展 runner 到 8x2 并接入授权、账本、off-peak、失败停止门；重新渲染 token 预算并
跑零 API dry-run。通过后等待用户逐字授权；所有 000-111 真实运行/评价保持待运行。
