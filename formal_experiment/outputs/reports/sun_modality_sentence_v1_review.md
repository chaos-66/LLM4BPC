# SUN-MODALITY-FINAL-REVIEW-001：LLM-SE 显式句级模态候选

2026-11-10。本次只准备这一个候选，真实 API 调用 **0**。模型效果尚未测量。
保留历史 22-shot 对照：test 426 条、正确 393 条、Macro-F1 **0.8697879915324909**，
禁止 TP/FP/FN **12/7/3**，无预测 1 条。Sun 本地重建 Macro-F1 为
**0.8772277372431857**。历史 24-shot 禁止判断逐条不变，原验收未通过；不替换对照。

## 交付与复现

- 完整组合 system prompt（含真实 22 条德语示例，仅本地）：
  `outputs/development/sun_modality_sentence_v1/composed_system_prompt.txt`。
- 完整 system/user 模板（含六个新封装的合成格式示例，仅本地）：
  `outputs/development/sun_modality_sentence_v1/complete_prompt_template.json`。
- 全 426 个实际请求体与不含标签的 ID 映射（仅本地）：
  `outputs/development/sun_modality_sentence_v1/requests.json`。
- 可版本化提示、教学说明及 ID/标签/哈希：
  `prompts/sun_compat/modality_sentence_v1/`。原文在本地按固定 train ID 加载。
- [输出 schema](../../configs/schemas/sun_sentence_modality_v1.schema.json)、
  [预先固定的取值/预算/失败策略](../../configs/supplement/sun_modality_sentence_v1.json)、
  [调用预检及逐请求哈希](sun_modality_sentence_v1_preflight.json)、
  [当前 33 条错误复核](sun_modality_sentence_v1_baseline_review.json)。

在仓库根目录运行：

```powershell
python -X utf8 formal_experiment/scripts/prepare_sun_modality_sentence_v1.py
python -X utf8 formal_experiment/scripts/prepare_sun_modality_sentence_v1.py --check
```

准备工具无 execute 模式、不导入发送器、不加载凭据；第二条命令重建并逐字节核对已存制品。
模型请求中只有该次待分类原句、固定 train 示范和合成格式示例。原 test ID 替换为
`input_000001` 等局部序号；不传入其他 test 句子、test 标签、诊断 ID、Sun 预测或错误统计。
复核和训练词面探查在请求构造完成后独立进行，其结果不参与选例或请求渲染。

## 相对保留 22-shot 的具体差异

| 方面 | 保留对照 | 本候选 |
|---|---|---|
| 返回接口 | 单个旧 canonical record | 新版本 envelope，内含旧合同的 `rule_record` 及独立 `sentence_modality` |
| 句级主取值 | 第一条有效 clause 标签 | 模型显式输出的 `sentence_modality.label` |
| 同次返回诊断 | 原主取值 | 仍调用原 `llm_se.extract_modality_label()`，只读取嵌套 record |
| 模态指导 | boundary + reviewer 多段叠加 | 一份整句阅读、命题/条件/否定/并列检查与句级决定的合并指导 |
| 输出指令 | system 与 user 均要求只返回旧对象 | system 的顶层键要求和 user 的返回指令均替换；六个合成示例改为完整新封装 |
| train 示例 | 22 条 | 仍 22 条，四项 D→D 替换，其余 18 条保留；相关示例相邻呈现 |
| 教学说明 | 原句和句级标签 | 增加明确署名 Codex AI 的短说明，不冒充人工语料标注 |
| 模型与采样 | deepseek-v4-pro / 0 / 1 / 4096 / thinking disabled | 完全沿用；无新增 response_format、seed 或分类器调用 |

六要素的字段、跨度、缺失值、受控歧义、actor/action 映射和顺序关系规则沿用母提示词。
移除了旧 boundary/reviewer/header 中“不得增加字段”“这不是新输出格式”“只返回原 JSON”
等冲突指令，未把用户给出的段落简单追加到它们之后。旧 reviewer 的六条英文合成语义对照
不再作为独立段落叠加；其必要判别内容融入统一指导。母提示词的六个六要素格式示例保留
内层 record，并增加 AI 编写的句级标签和证据；它们不是新增真实 train shots。
多命题合成示例用 obligation 作为该示例整句解释，标记 mixed；它不建立 O 优先于 D 的规则。

本候选合并了输出接口、指导和四条示范的改动。后续即使提高，也只能归因于整个候选，
不能声称某一条指导或示范已被单独证明有效。

## 新输出合同与评分边界

```text
schema_version = "sun_sentence_modality@1.0.0"
rule_record = 原 stage2_prediction.schema.json@1.0.0 的完整对象
sentence_modality = {
  label: definition | obligation | permission | prohibition | null,
  evidence: [{text, start, end}, ...],
  uncertainty: [incomplete_input | mixed_independent_modalities |
                corpus_boundary_ambiguous, ...]
}
```

evidence 必须是输入中的精确短片段，采用 Python 字符坐标 `[start,end)`；可用多个片段覆盖
分离谓词与否定。非 null 至少有一条证据；null 必须含 incomplete_input，允许空证据。
确定时 uncertainty 为 `[]`。有可辩护主断言但细节缺失时，允许非 null 加 incomplete_input。
这些标记是输出不确定性，不是第五类，也不是删样本依据。

解析器拒绝未知 envelope 版本、重复 JSON 键、源文本/ID 不匹配、未知标签/标记和不精确的
句级证据；兼容一层完整 JSON 代码围栏，拒绝夹带前后说明的非 JSON 返回。
完整 Rule Record 在独立副本上调用既有 `validate_canonical`，由其覆盖 validation。
它的结构和跨度诊断单列，**不因六要素跨度失准而取消另一个有效的句级标签**。
这是事前明确的接口决策：主问题是句级分类，不能隐式换成“六要素全正确才给情态分”。
当前环境沿用既有无 jsonschema 包的结构检查及跨字段校验路径，不声称额外完成了
JSON Schema 包的全规则验证，也不改变共享 canonical 校验器。

两项取值各自独立：句级字段失败时主预测为 None，但可继续保留合法封装内的旧首标签
诊断；请求失败、整体 JSON/envelope 失败或身份绑定失败时，两项均无预测。
旧首标签诊断保留原函数的标签投影语义，不因 record 的跨度诊断改变结果。
它不按 Gold 选 clause、不用 Sun 补标、不设 P>O>M>D，也不会把句级标签反写给 clause。

所有 **426** 条固定进入两项指标分母，包括 null、解析失败、请求失败。若将来预算/传输
中断，未发出的 ID 也以无预测出现在明确标注的部分运行诊断中，不能称为完成运行。
评分调用原 `modality_benchmark.metrics.evaluate`；无预测降低准确率及 Gold 类 recall，
不凭空给其他类添加 FP。覆盖子集分数只可作次要诊断。历史 0.869788 始终是旧首标签定义，
不以新解析器回算或替换。两者分数差还包含接口/取值改变，不能写作纯 prompt 改进。

## 当前 33 条错误：事实与解释分开

已重新验证历史账本哈希链、全 426 条 raw response 哈希、旧标签投影与既有指标。
旧 residual 的 reviewer 有 34 条错误；22-shot 改对其中 3 条、新增 2 条，当前为 33 条。
机器报告逐条保存原标签、当前首标签、返回 clause 标签/动作数/条件数、输入与返回哈希；
AI 主分类及解释另列字段，不把它们称为已证实的模型内部成因。

| 失败观察与 AI 工作分类 | 数量 | 人的判别步骤 | 本次可执行的指令或示范 |
|---|---:|---|---|
| 标签与语料边界不一致；原因未决 | 16 | 比较完整谓词、主体选择、资格范围及支持/反例 | 完整谓词/局部否定/资格与选择检查；边界不明标 corpus_boundary_ambiguous；有限许可和明确禁止示范保留 |
| 状态、计算关系或参数限制被读作指令/选项（AI 解释） | 7 | 先确定主语是什么，谓词陈述状态/关系还是要求操作 | 对应适用声明、抵减关系、法律认定和扣除范围四条 train 替换，与 O/M 对照 |
| 独立多命题已有不同标签，首条丢失后续标签 | 3 | 保留每项命题，自行作整句决定；不凭顺序选类 | 新 sentence_modality；mixed_independent_modalities；原 clause 顺序不变 |
| 前置条件或引导语被拆为独立 D | 2 | 连接动词前置条件与后续断言，读完引导语的内容 | 区分引导语与完整对应适用声明，条件依附其主断言 |
| 不同模态动作共用一个 clause 标签 | 2 | 检查每个并列谓词及局部否定，核对 action 与命题标签 | 逐个 action 检查；不同规范作用用相应 clause 表达 |
| 输入残缺或缺外层主断言（AI 解释） | 3 | 确定可见片段是否还有可辩护主断言 | 有断言则分类并标不确定；无断言才 null；不补原文 |

两项旧解释明确更新：`sun_modality_e281d33605497ded` 当前已输出 D/P，不能继续称“漏抽禁止”；
`sun_modality_68a7b0d9b95fb81e` 当前只一个 D，action 内包含义务指令，不能继续称旧 D/O
已分开后的投影丢失。`sun_modality_5dd905d7bef7684c` 当前模态证据已是完整被动谓词，
不能继续引用“仅普通助动词”的旧观察。新增的许可回归 `sun_modality_6d46f2ca8400b2bc`
属于引导语误拆。逐条 AI 解释仍可被后续复核推翻；不会声称新 prompt 能修好全部 33 条。

## 四项 train 替换及保护对照

| 原位置→新位置 | 新样本 ID | 原始标签 | 教学目的与相邻对照 |
|---|---|---|---|
| 17→2 | sun_modality_863058f4cad7ea4e | definition | 完整对应适用声明；新 3 是原 obligation 的适用执行指令 |
| 15→5 | sun_modality_c8712b2d00865a9d | definition | 预扣款抵减税款的关系；新 6 是原 obligation 的舍入计算指令 |
| 4→11 | sun_modality_f56a47d5cde6fdc7 | definition | 雇佣关系认定；新 12 是原 obligation 的估值执行指令 |
| 7→8 | sun_modality_c33e7e546525587d | definition | 扣除适用范围；新 9 是原 permission 的额度限制许可 |

四条 ID 在读取 held-out 前固定，原标签和当前文本 SHA-256 已核对；不按测试错误近邻选择。
完整哈希、被替换 ID、原/新位置、AI 教学说明及来源在 selection_manifest 中。
22 条类别分布保持 **D=9/O=5/M=5/P=3**。其余 18 条 ID、标签全部保留。
原最高额度、截止期、仅一次、带条件选择/授权的 permission，以及原明确禁止均得到保留。
示范相邻次序是教学编排，不授权模型重排目标句的 clause。

四条替换对 dev 的 1,680 次、test 的 1,704 次比对均无 ID、归一化文本或既有 near-match
规则命中。全部 22 条另通过原有 ID/归一化精确隔离；不把它误报为全部 22 条新增近重复检查。
near-match 规则与上一轮相同，版本绑定指向原实现。held-out 标签不进入选择/隔离函数。

扣除范围示例存在比较数值/对象缺失，AI 说明明确披露：可见部分仍陈述扣除的适用范围，
只支持有限的教学对照，不能恢复完整公式。其他原保留示范中的缺失节号/数值也不被补写。
教学用途不等于新增 clause Gold，也不保证模型会正确迁移。

## 仍未解决的训练边界

按旧诊断的固定词面检索规则在当前 train 重新核验，结果未变：

| 检索族 | 数量与原句级标签 | 能支持与不能支持的结论 |
|---|---|---|
| 不予计入 | 8：D1/O1/P6 | 否定计算横跨三类，不能“一律 D”或“见否定即 P” |
| 关系/状态认定谓词 | 3：D1/O1/P1 | 必须读完整句及主断言，不能把单个认定动词固定为 D |
| 被动抵减/计入关系 | 7：D3/M4 | 新 D 示例只说明该句的原始口径，不能把整个被动模式强制为 D |
| 对应适用声明 | 14：D14 | 支持新增完整声明示范；不覆盖引导语或应当执行适用的 O |
| 仅在条件成立时允许 | 10：D10 | 与已保留的有条件 M 对照；条件本身不是 D 判据 |
| 最高额度 | 2：M2 | 保护有限许可；不能把任何金额上限映射为 M |
| 适用前提 | 1：O1 | 资格表述也可能被语料标 O，不能强称通用语义完全解释原标签 |

例如“不予计入”训练命中中的 `sun_modality_f3596ec70572acbb` 为 D，
`sun_modality_1bbd5e0ee435259c` 为 O，`sun_modality_f32e7cae7a031a7c` 为 P。
D 例是更长的计算句，句级标签不直接标注其中每个否定 clause；O/P 两个负向处理句
也不能靠这个词组独立区分。这些支持/反例仅作离线证据，不作为额外 shots 塞入请求。
剩余语料边界记为 corpus_boundary_ambiguous，不改 Gold、不用 Sun 当真值、不硬编规则。

## 请求、预算和失败处置

单候选 **426 次** test 请求；不加 dev、不重跑历史对照或 Sun。沿用
`deepseek-v4-pro`（文档版本 DeepSeek-V4-Pro-0813）、temperature=0、top_p=1、
max_tokens=4096、thinking disabled、非流式、无 seed。拟 4 并发、仅北京时间空闲时段、
零重试。官方模型版本和价格于 2026-11-10 核对，空闲时段百万 token 输入命中/未命中/输出
为 ¥0.15/¥4.5/¥13.5；执行前再次核对。[DeepSeek 官方价格](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)

最终请求将合成 JSON 示例紧凑序列化，避免无意义缩进开销；输入估算 **4,173,475 tokens**
（JSON UTF-8 字节/3，非 tokenizer 实测）。输出假设采用旧 22-shot 平均 619.155 加新字段
256，即每条约 875.155 tokens。全部输入按缓存未命中估算 **¥23.8136535**。
这不是报价上限或实付费用，已有缓存时可能更低，实际生成更长时也可能更高。
拟批准硬上限 **¥35**；本次授权额度仍为 **0**。

逐请求保留完整 4096 输出额度，加输入 wire 字节上界和 1024 余量，按未命中费率预留
**¥0.192078–¥0.194652**。全 426 次这种保守预留之和为 **¥82.1765925**，并不一次性
收取；并发请求结算后释放预留。¥35 不保证 426 次全部完成，达到上限前必须停发。

后续新授权应绑定本 suite、交付预检 SHA-256、426 次/零重试/上限/模型/价格表。
旧批次授权不能复用。发出前复核请求字节及代码/数据绑定；记录 started/finished、
原始返回、用量、模型和账本哈希。传输、模型、请求字节或计费异常停止新请求并收齐
已发请求；不自动重试，也不自动重发已 started 的不确定请求。解析失败/null 保留分母。
只在后续授权回合接入发送器并做执行前绑定检查，本次工具不含发送路径。

## 离线验证与后续报告口径

少量合成测试覆盖请求采样、封装解析、句级证据/不确定性、两个取值的独立性、
不改 clause、canonical 校验复用以及 426 分母内的缺失/失败/null。
相关测试由 record_change.py 一次运行并记录，另复用共享评价器的三个具名分母/混淆矩阵
测试和既有 canonical 校验测试；**56 passed（3.07 秒）**，批次结束快速完整性检查通过，
不运行全量测试。实验事件保存了具名目标及实际验证范围。
train 来源和隔离、33 条旧错误复核、426 个请求字节绑定由离线准备器检查。
这些检查只能证明构造和接口行为，不能证明分类性能提升或提示语义被模型稳定执行。

若获本批执行授权，事前固定主指标为全 426 的四分类 Macro-F1，并同时完整报告：
整体及四类 P/R/F1、混淆矩阵、相对历史 22-shot 的改对/改错、禁止 TP/FP/FN、
无预测数、同批首 clause 诊断及两项取值的逐 ID 差异、canonical 校验情况和费用。
不在见到成绩后换主指标或删困难样本；不自动升级候选。由于 dev/test 已用于诊断，
后续结果按探索性结果解释。新增显式字段解决决策接口，正确性仍需真实测量。
