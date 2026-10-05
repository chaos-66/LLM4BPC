# Stage 2 prompt 精简候选 v1

任务：`SEP-C3-PROMPT-SIMPLIFY-V1`。用户于 2026-10-05 要求在分支中尝试精简并保留已有结果。
分支为 `codex/s2-prompt-simplification-v1`；这是一批未执行的开发候选。

| 版本 | 本次变化 | System 字符数 | 相对 v6 压缩 |
|---|---|---:|---:|
| 原 v6 | 历史对照，另存原始文本与结果 | 6,172 | — |
| A：`direct_llm_json_light_v1.md` | 压缩 J 的合同哈希、重复格式要求和自检措辞 | 5,676 | 8.0% |
| B：`direct_llm_json_semantic_light_v1.md` | A + 合并 S 重复说明、明确 condition/exception 与 action 边界 | 4,398 | 28.7% |

这里统计的是装载后 system 文本的字符数，不是 token 数或整次请求的压缩率。
六个历史合成示例、完整 Examples 区块、用户模板和 Notes 保持一致；因此例子带来的
结构/语义引导仍在。模板和 Notes 的历史措辞写“四个”，实际装载六个；这处旧措辞
本批故意保留，避免同时修改示例呈现方式。

## 精简取舍

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
Direct-LLM 0.8378 / Rules-Only 0.7631 不转移到候选。默认 prompt 选择不变。

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
