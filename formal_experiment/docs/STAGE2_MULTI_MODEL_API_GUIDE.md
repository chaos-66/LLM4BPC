# 第二阶段多模型密钥配置与授权调用

入口：`scripts/stage2_multi_model.py`。只用 Python 标准库，支持千问、MiMo、Kimi、
Grok、GLM、MiniMax；模型配置在 `configs/models/stage2_multi_model_v1.json`。
填入密钥不会授权联网。程序默认离线；本次交付没有真实 API 调用。

## 1. 填写密钥

在 `formal_experiment/.env` 末尾的六个空白项中填写对应平台的 API key。
没有密钥的项目可以留空，以后只选已填写的模型运行。

```dotenv
LLM4BPC_QWEN_API_KEY=
LLM4BPC_MIMO_API_KEY=
LLM4BPC_KIMI_API_KEY=
LLM4BPC_GROK_API_KEY=
LLM4BPC_GLM_API_KEY=
LLM4BPC_MINIMAX_API_KEY=
```

已有 DeepSeek 配置继续供原程序使用。此入口不改旧模型配置、不读取 Gold、不覆盖
旧预测或论文固定表。真实 `.env` 被 Git 忽略，不纳入提交。填完后直接告诉执行者
哪些模型可用，密钥不用粘贴到聊天里。

初始化命令只追加空白项，不读取已有文件。使用本地标记避免重复初始化：

```powershell
python formal_experiment/scripts/stage2_multi_model.py init-env
```

## 2. 离线列出模型与准备计划

以下命令在项目根目录执行，不读取 `.env`、不测试 key、不联网：

```powershell
python formal_experiment/scripts/stage2_multi_model.py list
python formal_experiment/scripts/stage2_multi_model.py plan --providers all --samples 20 --run-id model_pilot_01
```

也可用 `--providers qwen,mimo,grok` 只选三家。六家各 20 条是 **120 次计划调用**，
实际调用仍是 0；这只是准备计划，不代表已批准该批样本或费用。`--samples` 范围
1–150，固定取冻结 EStG-150 推理输入的前 N 个相同 ID。前 N 条只作连通性/开发
试跑，不把它称为代表性随机样本；模型稳定性结论需要另行确定采样与评价设计。

产物写入 `outputs/development/stage2_multi_model_v1/<run_id>/`：

- `plan.json`：型号、端点、采样/思考参数、每个请求正文及 SHA-256、代码/输入/
  v6 prompt/schema 绑定、输出上限；默认 `authorized=false`。
- `authorization.template.json`：默认 `authorized=false`，本次用户授权原文、批准
  时间、计划 SHA、各家核实单价和费用上限均待填写。

旧 run ID 不能覆盖。改型号、端点、参数、代码、输入或 prompt 后，重新生成计划并
取得新授权；不得重用以前 Stage 2/3 的调用额度。

## 3. 用户明确批准后才运行

执行者先核实模型的账户权限、API 单价与币种，说明计划调用数和各家费用上限，再
根据用户针对该批计划的明确决定建立 `authorization.json`。填写 key、“都试试”
或已有历史授权都不自动填充本次授权。程序无法直接识别聊天中的决定，授权原文
由执行者如实记录，不能自行将模板改成 true 当作用户批准。

下面是**以后获得授权才执行**的命令结构：

```powershell
python formal_experiment/scripts/stage2_multi_model.py run `
  --plan formal_experiment/outputs/development/stage2_multi_model_v1/model_pilot_01/plan.json `
  --authorization formal_experiment/outputs/development/stage2_multi_model_v1/model_pilot_01/authorization.json `
  --execute --allow-llm
```

计划绑定、明确授权、调用/输出预算和核对过的价格全部通过后，才在运行进程内部
读取所选模型的密钥。所有所选密钥必须齐备，第一笔请求前即检查；未选模型可以
留空。进程环境中的非空同名变量优先于 `.env`；同一 `.env` 内重复且冲突的非空项
会拒绝运行。不执行变量插值，不把 key 写进日志或修改进程全局环境。

每次最多输出 4096 tokens，超时 180 秒，**自动重试 0 次**，顺序交错调用各家相同
样本。输入费用按请求 UTF-8 字节数加 4096 做保守预留；这不是准确 tokenizer
计数。价格采用所选服务层级下包含全部可计费输出/思考 tokens 的未命中缓存单价，
不把折扣当作额外额度。发送前检查费用预留；返回 usage 后再核对额度。
这是客户端停止规则，最终费用仍以平台账单为准。

模型实际返回 ID、usage、完成原因和输入 ID/原文必须能核对。网络错误、超时、
空响应、截断、用量缺失/超额或型号不符会停止，保留该次费用预留并标记待核查，
不自动补调用。完整响应内 JSON/字段/坐标校验失败会保存失败记录，禁止伪装成
正确抽取；结构合法也不等于语义正确。

## 4. 输出与续跑

- `authorization_snapshot.json`：本次授权快照。
- `calls_ledger.jsonl`：发送前 fsync 的 started 事件和保存后的 finished 事件，
  含请求/授权/响应哈希、用量费用预留及链式哈希。
- `responses/`：各请求的原始响应文本、usage、返回型号、转换检查和错误。
  保存前屏蔽所选 key；HTTP 错误同时屏蔽回显的 Bearer 凭据。
- `predictions.json`：成功、失败及未尝试记录。
- `manifest.json`：调用数、有效结构数量、保守费用、代码/输入/profile 绑定，
  `claim_scope=development_only`、`metrics=null`；没有评分或性能结论。

`--resume` 先验证旧授权、账本与响应字节/费用，再发送**从未尝试**的请求；已完成
的批次续跑是 0 新调用。已有 started 无 finished、待核查请求或遗留运行锁时拒绝
自动继续，必须先人工核对平台请求和账单，不能通过删账本/锁绕过未知调用。
原始响应使用独占新建，续跑只重建本批聚合预测与 manifest，不改历史臂。

运行结束（包括 partial）后，执行者按 `AI_CHANGE_PROTOCOL.md` 记录带 manifest
索引的 `experiment_run` 事件，按根 AGENTS 的具名验证和 Git checkpoint 规则
提交、推送可版本化证据。忽略的本地逐条响应、实际 `.env` 和受限数据不上传。

## 当前默认型号及官方依据

这些是 2026-10-05 用户指定后更新的可编辑默认配置，**还没有真实账户/API 验证**。
授权前重新核对可用型号、端点与单价。API key 应属于对应 API 平台和地域；
Coding Plan key 不一定支持通用 Chat Completions。

| 家族 | 默认型号 | 请求设置与官方依据 |
|---|---|---|
| 千问 | `qwen3.8-max-2026-09-02` | 关闭 thinking，temperature=0，top_p=1；[Chat Completions](https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-openai-chat-completions) / [型号](https://www.alibabacloud.com/help/en/model-studio/qwen3-8-max) |
| MiMo | `mimo-v2.6-pro` | 关闭 thinking，temperature=0，top_p=1；[API](https://mimo.mi.com/docs/en-US/api/chat/openai-api) / [超参](https://mimo.mi.com/docs/zh-CN/api/guidance/model-hyperparameters) |
| Kimi | `kimi-k2.7-code` | 强制开启 thinking，按平台约束 temperature=1，top_p=0.95；[官方指南](https://platform.kimi.com/docs/guide/kimi-k2-7-code-quickstart) |
| Grok | `grok-4.7` | reasoning_effort=low，省略采样参数；[官方型号页](https://docs.x.ai/developers/models/grok-4.7) |
| GLM | `glm-5.3-flash` | 国内 BigModel 端点，强制开启 thinking，reasoning_effort=low，temperature=1，top_p=0.95；[官方型号页](https://docs.z.ai/guides/vlm/glm-5.3-flash) / [GLM-5.3 参数迁移](https://docs.z.ai/guides/llm/glm-5.3)；国内账户可用性仍未实测 |
| MiniMax | `MiniMax-M3` | 国内 `api.minimax.cn` 端点，关闭 thinking，temperature=0，top_p=0.95；[国内兼容 API](https://platform.minimax.cn/docs/api-reference/text-openai-api) |

用户的“Qwen 3.8”沿用已有 Max 0902 固定快照，不自行改成 Flash/Plus。用户的
“Kimi 2.7”按官方通用 API 名称映射为 `kimi-k2.7-code`；它是 Code 版，不能关闭
思考，不能宣称与非思考的 2.6 在推理配置上相同。GLM 5.3 Flash 也强制思考。
输出上限仍是 4096；该上限和 180 秒超时尚未做真实连通性验证，强制思考模型
如返回截断/超时会保存失败并停止，不扩大 token 额度或自动补调用。

用户单独明确批准覆盖旧禁读规则后，本次仅私有检查了六项填写状态，六家均已
填写，无空白/占位符/重复冲突；没有显示任何 key，没有调用模型，没有改 `.env`。
此结论不证明 key、余额、账户地域或型号权限有效；该例外只适用于本次状态检查，
不构成后续真实 API 授权。此前 v1 离线预检因配置变更已不适用于现在的请求；
更新配置后的预检须使用新 run ID 并另获调用及费用授权。

MiniMax 的完整前置 `<think>…</think>` 保存于原始响应，提取 JSON 时只去掉一个
完整的前置块。所有家族使用同一 v6 原文、示例、用户模板和英文输入；共享原有
adapter、显式 `legacy` 坐标策略与 canonical 校验。各家参数/思考约束不同，
因此这只能比较登记好的**模型与推理配置组合**，不能声称全平台 temperature 或
推理预算已严格相同。新入口亦不是对历史 v6/R3 传输的逐字节重放。

已有 DeepSeek 正式臂、表一 0.8378/0.7631 与表二继续作为原来源结果。
本工具仅为后续独立模型补充实验准备，不自动切换默认方法、修改提示词、运行
Rules+LLM、评价 Gold 或替换已固定的论文表。
