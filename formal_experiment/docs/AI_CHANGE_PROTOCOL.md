# 实验日志与自动检查协议

> **名称说明**：本项目不把日常论文实验称为“正式项目审计”。检查脚本继续保留
> 兼容名 `audit_project.py`，含义是“自动完整性检查”。活动日志已经改成语义清楚的
> `EXPERIMENT_LOG.md`（中文人类日志）和 `EXPERIMENT_EVENTS.jsonl`（机器事件）。
> 事件 1—29 没有重写，旧人类日志冻结在 `_retired/logs/`。

## 1. 我们实际采用的制度

| 层级 | 作用 | 什么时候使用 |
|---|---|---|
| 实验日志（主制度） | 记录运行目的、代码/数据/参数、结果、错误和产物 | 每次真实实验运行；影响结果的设计/代码变更 |
| 自动完整性检查（护栏） | 防止误改 Gold、数据漂移、schema 破坏、方法越权 | 实验程序或数据协议修改批次的开始与结束，不含纯文档制品 |
| 正式里程碑复核 | 冻结数据/Gold、最终实验、论文提交前的系统检查 | 阶段冻结、导师复核、投稿前 |

自动检查不是第三方正式审计，也不应成为每天反复生成报告的工作。它只负责快速
告诉 Agent 当前能做什么、哪些结果还不能声称，以及改动有没有破坏项目不变量。

## 2. 修改前

实验程序、数据协议或评价方法变更按以下顺序阅读。纯 PPT、文字、排版等工作只需
阅读两级 AGENTS.md、与任务相关的规范和内容来源，不必遍历整个实验状态：

1. `docs/MASTER_PIPELINE.md`
2. `docs/PROJECT_AUDIT.md`（兼容文件名；内容是实时状态）
3. `docs/AGENT_RUNBOOK.md`
4. `docs/DIRECTORY_GUIDE.md`
5. `docs/EXPERIMENT_LOG.md` 的最新事件
6. 本协议
7. `docs/ROUTE_LOCK.md`
8. `configs/experiment_contract.json`
9. `configs/methods.json`

开始一个会修改代码、配置、数据协议、prompt 或评价器的连贯批次时只跑快速检查：

```powershell
python formal_experiment/scripts/audit_project.py
```

纯阅读、论文分析、PPT/Word/文字/排版及不改变程序行为的文档工作不运行项目检查。
快速检查不跑测试；它与全量代码测试是两个不同操作。

## 3. 检查与记录频率

**2026-09-10 用户明确修订：按实际影响范围验证，默认不进入全量测试。**
本节覆盖旧任务模板中“批次结束/交接必须全量”的笼统表述，历史日志不重写。

| 情况 | 要做什么 |
|---|---|
| 只读分析、回答问题 | 不跑测试，不追加实验事件 |
| PPT、Word、文字、图表、排版、纯文档 | 核对内容来源、公式/数字、渲染、文件可打开及应保留部分；按需做相关检查，不跑实验代码测试；用 scoped Git commit 记录 |
| 实验代码、配置、schema、prompt、数据协议、评价器修改 | 批次边界各一次快速完整性检查；只跑对应模块及直接受影响调用方的具名测试 |
| 连贯批次结束、任务交接、提交、推送、备份、日志追加 | 复用本批次适用验证，不因此新增全量测试；明确报告验证范围 |
| 真实实验运行 | 执行已授权门禁及必要的相关验证；运行后记录 experiment_run 与 manifest，不自动重跑全部测试 |
| 跨模块公共接口改动、整体集成、正式冻结/发布复核 | 先说明相关测试无法覆盖的具体风险和预计耗时；确需全量时，取得用户对本轮全量的明确授权再执行 |

“material change”指会影响实验路线、代码、配置、schema、prompt、数据、Gold、
evaluator、指标或正式实验产物的修改。PPT/报告文字使用已有公式或结果、文件位于
`formal_experiment/`、需要 Git 备份，均不构成执行全量代码测试的理由。改写实验
方法或结论仍须核对已有证据；没有证据则保留待办，不自行启动新实验。

### 全量测试启动条件

- 正常流程只跑一遍全量；同一工作区不得并发或重复启动等价全套测试。

`audit_project.py --with-tests`、`pytest tests` 及任何等价全套运行都属于全量测试。
启动前必须确认：

1. 用户已明确授权**本轮全量测试**。一般的“修复、验证、完成、提交、推送”不等于
   全量授权；用户已经明确授权时不重复询问。
2. 说明触发原因（具体跨模块风险、正式门禁，或用户直接要求全量）、准确范围、
   预计耗时及可复用的已有证据。本项目近期全量约 55—65 分钟，不可当作快速检查。
3. 同一工作区没有另一轮重复全量测试。有效且状态匹配的凭证可复用；过期、缺失
   或日志待追加均不授权重跑，禁止伪造/改绑凭证。

没有授权时，先交付可完成部分，报告尚缺的覆盖范围；不得声称未完成的正式门禁
已经通过。PPT 等无关制品不应被实验测试拖住。运行期间不反复轮询、堆叠无变化
消息；只报告实质进展、失败或需要用户行动的情况。

### 相关测试的成本限制

默认只选择与本次改动有关的测试文件或节点，常规检查以 3 分钟内为目标。已知
更长时先说明原因和预计耗时。超时、无关失败或一次检查没有通过，不得自动扩展为
全量、反复重跑或顺手修复无关实验。输出“未覆盖/失败”的真实状态即可，继续完成
不受影响的交付。

## 4. 真实实验日志必须记录什么

每次实际运行至少记录：

- `run_id`、时间、Stage、方法和实验目的；
- Git commit 与 dirty 状态；
- 输入数据/Gold/split 的版本或 hash；
- 模型、prompt/rule 版本、超参数、seed、threshold；
- LLM 模型版本、temperature、调用预算、实际调用数、成本和失败数（如适用）；
- 完整运行命令；
- manifest 与输出路径；
- 主指标、运行状态、报错和异常处置；
- 该结果属于 development、pilot 还是 formal。

参数和 hash 的详细值应写入运行 manifest；机器日志负责索引 manifest，而不是把
所有字段复制进 Markdown。示例：

```powershell
python formal_experiment/scripts/record_change.py `
  --event-type experiment_run `
  --purpose "Part 2 B0 development run" `
  --test-target "tests/test_<相关模块>.py" `
  --run-id "s2-b0-seed13" `
  --stage "stage2" `
  --method "sun_rule_only" `
  --run-status succeeded `
  --run-command "python scripts/run_sun_rule_only.py --seed 13" `
  --manifest "data/results/s2-b0-seed13/manifest.json" `
  --result-summary "development only; metrics in manifest" `
  --gold audit_read_only `
  --llm-api not_called `
  --artifacts created_no_overwrite
```

## 5. 修改批次结束

纯制品/文档：完成第 3 节对应的检查后即可提交，不为生成测试凭证启动代码测试，
也不强制调用实验日志脚本。必要的内容来源或限制写入制品说明/提交消息。

实验程序/数据协议修改：选定相关测试，并执行目录与 diff 检查。下方日志命令会在
记录前执行批次结束的快速完整性检查，无需提前重复同一检查。
以下示例用于**日志记录器修改**；其他任务必须替换为其实际相关测试，不能照搬：

```powershell
python formal_experiment/scripts/generate_file_catalog.py --check
git diff --check
git status --short
```

一次运行具名相关测试并追加变更日志：

```powershell
python formal_experiment/scripts/record_change.py `
  --event-type change `
  --purpose "本次连贯修改目的" `
  --test-target tests/test_change_record.py `
  --gold audit_read_only `
  --llm-api not_called `
  --artifacts not_created_or_overwritten `
  --notes "可选说明"
```

`--test-target` 可重复指定文件/节点，只运行这些目标，禁止传测试目录、通配符或
pytest 选项。默认总超时 180 秒，可用 `--test-timeout-seconds` 显式设置已说明的
时间预算；超时记录失败，不重试、不扩大范围。不要先单独跑同一组测试，再为记
日志重复运行；本命令可将检查与记录合并一次完成。

已授权的 `audit_project.py --with-tests` 会生成与活动文件 SHA-256 匹配的临时
全量凭证；不带 `--test-target` 的 `record_change.py` 只复用有效凭证。凭证缺失/
过期时脚本返回非零，**不启动测试、不写事件**。显式传入目标时只做相关测试，不
自动升为全量。机器事件记录 `test_scope`、命令及目标，人类日志明确“相关测试
（非全量）”；不能把相关测试通过说成全量通过。`.env` 和缓存不进入状态指纹。

日志追加到以下活动路径：

- `docs/EXPERIMENT_LOG.md`：中文人类可读实验日志；
- `docs/EXPERIMENT_EVENTS.jsonl`：机器可读事件、测试证据、commit、dirty paths、
  blocker、安全声明和可选实验运行字段。

既有事件只能追加，不能重写。事件 1—29 的机器记录在更名时原样保留；迁移前的
旧人类日志位于 `_retired/logs/AUDIT_LOG_legacy_through_event_29.md`。

## 6. 不可放松的安全边界

- Agent 不得根据预测、多数票或论文聚合数字自动生成/修改 Gold；
- 用户可以继续编辑已 input-ready 的 Layer E，但只有 150/150 人工裁决后才可能冻结；
- 不得为提高指标调整 Gold、test threshold 或删除困难样本；
- 未经用户明确授权和硬调用预算，不得运行真实 LLM/API；
- `sun_rule_only` 不得调用 LLM；
- predictions、results、manifest 和正式产物默认不得覆盖；
- `references/` 与根 `archive/` 保持只读；
- 不得把 development heuristic 写成 Sun exact reproduction。

## 7. 正式里程碑复核

本次成本策略不移除 Gold、API 或正式发布门禁。`--require-final-ready` 是就绪检查，
不等于全量测试授权；如果里程碑还需要全量覆盖，仍须按第 3 节明确授权后执行。

只有以下命令返回 0，才允许启动最终正式实验：

```powershell
python formal_experiment/scripts/audit_project.py --require-final-ready
```

最终还要人工确认三组方法共享 frozen IDs、Gold、schema、normalization、evaluator
和 Part 3 配置。Part 2 与 Part 3 指标必须分开报告。这一步才接近论文语境下的
正式复核；日常开发不使用“正式审计”表述。
