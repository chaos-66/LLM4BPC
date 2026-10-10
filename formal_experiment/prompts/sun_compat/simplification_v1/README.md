# Stage 2 prompt 精简候选 v1

任务：`SEP-C3-PROMPT-SIMPLIFY-V1`。用户于 2026-10-05 要求在分支中尝试精简并保留已有结果。
分支为 `codex/s2-prompt-simplification-v1`；这是一批未执行的开发候选。

| 版本 | 本次变化 | System 字符数 | 相对 v6 压缩 |
|---|---|---:|---:|
| 原 v6 | 历史对照，另存原始文本与结果 | 6,172 | — |
| A：`direct_llm_json_light_v1.md` | 压缩 J 的合同哈希、重复格式要求和自检措辞 | 5,676 | 8.0% |
| B：`direct_llm_json_semantic_light_v1.md` | A + 合并 S 重复说明、明确 condition/exception 与 action 边界 | 4,398 | 28.7% |

这里统计的是装载后 system 文本的字符数，不是 token 数或整次请求的压缩率。
三份系统指令的完整英文原文、逐条中文翻译、共用用户模板及六个完整示例见
[PROMPT_BILINGUAL_REVIEW.md](PROMPT_BILINGUAL_REVIEW.md)。该文件仅供阅读，不作为运行 prompt。
六个历史合成示例、完整 Examples 区块、用户模板和 Notes 保持一致；因此例子带来的
结构/语义引导仍在。模板和 Notes 的历史措辞写“四个”，实际装载六个；这处旧措辞
本批故意保留，避免同时修改示例呈现方式。

## 精简取舍

逐条原指令、处理方式、依据、保留内容与风险见
[RATIONALE.md](RATIONALE.md)。这是对已保存候选的完整复核，不改变 A/B 文本。
其中 A 将显式顶层字段清单交由示例承载，存在显式程度降低；B 则混合了说明
重组、触发词提示抽象化和语义修正，不能把所有改动称作无损删重。

A 保留 S 与公共规则，只压缩显式 JSON 指令。完整 canonical schema、枚举、原文
身份绑定、字符坐标、ID 引用及程序校验要求继续存在。固定 method/validation 等
元数据仍由模型按示例输出；本批不修改 adapter/canonicalizer，避免把后处理变化
混入 prompt 比较。validation 是占位符，程序实际计算的校验结果仍为权威。

B 按语义功能定义 condition、constraint 与 exception：`unless` 不自动使例外同时
进入 condition。action 的边界依据语法范围，避免“一遇到关键词就截断”；保留
必要宾语/补语、被动句无明确执行者时 actor 为空、未解析代词保留原文、嵌套
constraint 在 condition/constraint 双字段呈现、定义句、分句/并列及关系规则。

B 同时包含 S 的压缩和分类歧义修正。将来 A/B 的差值只能归于这个改动包，不能
单独证明 `unless` 或某一句措辞的因果作用；如果需分离，另建具名候选和预检。
具体触发词列表、constraint 的 smallest 提示、显式 by-phrase 提示均有弱化，
actor/object 的限定则是新增表达；这些风险在逐项表单列，尚无新语义效果证据。

## 历史结果保存

`outputs/evidence/s2_prompt_simplification_v1/baseline_snapshot.json` 保存来源提交
`37e5bf8` 对应的 15 个 Git blob：原 v6 prompt、表一报告、v6 八格消融/表二报告、
旧 modular 消融及错误分析、组装清单、评价配置、schema 和原 runner。
每项记录原始 UTF-8 内容、字节数、Git blob ID、SHA-256 和启动时工作树 SHA-256。
准确完整的提交号见 manifest，不以此处短号作为机器绑定。
新候选与证据目录分别声明 LF 检出，确保跨平台保存时其原始字节哈希稳定；快照
字符串中的原始 Git blob 换行不作归一化，仍可还原并核验。

工作区两份 `sep_c3_modular_ablation_v1` 报告已有用户修改；快照取 Git 中的历史
已提交版本，本地修改保留、不覆盖、不混入本次提交。该快照保存报告和 prompt
来源，不能宣称所有未版本化 raw responses/predictions 都已远程备份。

本候选没有新预测，指标为 `null`，调用数为 0。历史正负结果保持原值，固定表一
LLM-SE 0.8378 / Rules-Only 0.7631 不转移到候选。默认 prompt 选择不变。

## 显式装载与运行边界

现有 `bpc_hybrid.prompt_loader.load_prompt` 可以离线装载以下名称：

- `simplification_v1/direct_llm_json_light_v1`
- `simplification_v1/direct_llm_json_semantic_light_v1`

`run_direct_llm.py --prompt-name` 增加这两个显式选项；候选须传 `--development`，
output 和 manifest 均须位于 `outputs/development/s2_prompt_simplification_v1/`。
不提供候选到正式冻结目录的入口；已有拒绝覆盖和真实调用授权门禁继续有效。
本轮只检查装载、渲染、示例结构/坐标、历史快照及调用入口门禁，不读取 `.env`。

将来运行需先另锁准确输入/prompt/model/后处理/评价器、预算与授权；不复用旧五次
Stage 3 授权，不追加八格重跑或取消的 Rules+LLM 实验。主口径仍为固定 coarse
五字段 pooled micro-F1，modality 单列。未运行前不声称精简提高了性能，也不将
整个 SEP-C3、正式发布或全量覆盖标为完成。

## 2026-10-06 当前对照范围：复用原版，只新跑 A/B

本批实际运行现已完成：300次新调用、0重试，约6分1秒；原版复用150条。
共享pooled主F1为原版0.8224、A 0.8218、B 0.8210，没有总体提升。
原始JSON对象为107/150、7/150、6/150，围栏可由现有解析器处理，评价失败均0。
报告 `outputs/reports/s2_prompt_simplification_comparison_20261006_v2.{json,md}`；
完整证据与manifest保存于 `outputs/evidence/s2_prompt_simplification_v1/comparison_20261006_v2/`。
保留真实负/近零结果，当前候选不替换默认或固定论文表一/表二。

用户随后明确回复“授权，进行数据运行，快点”，已批准这个范围与官方 API 外发。
新的授权/预检分别为 `configs/authorization/s2_prompt_simplification_20261006_v2.json`
与 `outputs/reports/s2_prompt_simplification_comparison_20261006_v2_preflight.json`；
执行入口为 `python formal_experiment/scripts/run_s2_prompt_simplification_v2.py --execute --allow-llm`。
最多并发 6 次以加快，0 重试、300 次/USD9.76 上限，原版不重跑。当前事实只见
PROJECT_AUDIT；下文“待确认/待新入口”的描述保留为授权前历史事实。

用户纠正原版不需重跑。当前范围为同一 EStG-150 上 A、B 各一次，共 300 次新调用，
复用 `D-full-0813/repeat-01` 的原版结果；已核对 150/150 请求配方与响应指纹、
prompt 哈希和输入 ID 一致。历史原版的记录估算费用 USD 1.35147804；300 次参考
约 USD 2.70，按原保守公式的预算上限重算为 USD 9.76（不是实扣）。

完整通俗差异、信息损失风险与费用核对见 `COMPARISON_EXPLAINED_ZH.md`。
本次只作说明与范围修订，旧 450 次 runner/预检不适用于新范围；新执行器/预检
还须按 300 次与历史基线重新绑定。当前无外发确认、无真实调用或候选新指标。

## 历史记录：2026-10-06 旧 450 次执行准备（已被用户范围纠正取代）

用户已明确要求对改动后的 prompt 进行实验对照。本轮唯一批次
`comparison_20261006_v1` 为 v6/A/B 同一 EStG-150 各一次，450 次上限、0 重试、
USD 14.77 上限。新的授权/请求/源哈希见
`outputs/reports/s2_prompt_simplification_comparison_20261006_v1_preflight.json`；
上方“未执行”及零调用是候选准备时的历史事实，当前实时状态只见 PROJECT_AUDIT。

入口 `python formal_experiment/scripts/run_s2_prompt_simplification_v1.py --execute --allow-llm`。
执行只使用进程已有 DeepSeek 密钥，不读取 `.env`；缺失则停。保留每条请求开始账本、
原始响应、共享后处理预测和完整分母；中止/in-doubt/已完成批次不自动重发。
三臂主口径为 pooled 五字段 micro-F1，原始 JSON、modality、用量另列。无额外模型
或稳定性重复；B 的结果只能归于联合改动，不据此判断单句因果。

本轮首次启动被自动审批拒绝，程序未启动，API=0。实验目标已获授权；具体冻结英文
文本与 prompt 发送至 DeepSeek 官方 API 的外发确认待用户回复。拦截记录见
`outputs/reports/s2_prompt_simplification_comparison_20261006_v1_execution_blocker.json`。
不得以其他命令或间接执行绕过。此旧准备不能用于当前 300 次范围，即使收到外发
确认，也须使用重新绑定的新批准备；保留本段和旧文件作为历史记录。
