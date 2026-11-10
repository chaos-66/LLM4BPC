# 原22-shot的E／S最小修改：逐项自查与离线交付

任务：`SUN-MODALITY-ES-MINIMAL-001`。用户要求只做能够说明如何帮助判断正确性的
恰当小修改，每项先重新审视意义。这里将该要求作为修改前自查，而非扩大输出或评分要求。
以原22-shot（393/426、Macro-F1 0.8697879915324909）为对照，准备两个独立版本：
E1只替换一个真实训练示例；S1只补一处语义区别。两者未合并、未调用模型、没有新成绩。

## 每项修改前的自查

统一问题：**这个修改是否有具体依据帮助模型提高判断正确性，同时避免把原本正确的句子带偏？**

| 项目 | 现有问题与依据 | 为什么值得修改 | 可能的反作用与限制 | 本次决定 |
|---|---|---|---|---|
| E1，第15条算术示例 | 原train句缺失具体金额，示例不能清楚展示一个完整计算关系；22-shot仍把税款抵减等关系读成义务 | 替换为train中谓词完整的税款抵减关系，原标签仍为definition，给出更清楚的计算关系示范 | 可能把真正的计算执行指令也吸收到definition；保留原有取整、估值和计税等obligation示例，后续需检查反向误判。效果未知 | 只做1条D→D替换，不增加shot，不改其他21条或排序 |
| S1，区分引导语和独立适用声明 | 当前22-shot有引导语单列definition、后续permission被首标签读取丢掉的返回；现有语义指引讲了条件，却未明确说明这一引导结构 | 说明“下列规定适用”需结合下文判断，避免生成一个没有独立规范内容的首条定义 | 不能把完整适用声明也当成引导语；同时写明完整“规定相应适用”可以独立断言。此修改不处理真正独立多命题的句级聚合 | 只增加该区别，保留既有条件、否定、并列、顺序及六要素说明 |

依据为既有原22-shot返回的观察与AI解释，不是模型内部机制的证明。原33条核对见
`sun_modality_sentence_v1_baseline_review.json`；它绑定原22-shot账本，来自已撤销候选
之前的基线复核，这里仅复用其事实观察，不恢复被撤销的接口、坐标否决或发送器。

## E1：仅替换一条示例

位置15保持不变，总数22、类别数量D/O/M/P=9/5/5/3保持不变。

| | train ID | 原标签 | UTF-8文本SHA-256 |
|---|---|---|---|
| 原例 | `sun_modality_27b2552450dda62f` | definition | `d236e8fd096556a2a049d76f5ba461e8511cf7e66630804343b273587ff9014f` |
| 新例 | `sun_modality_c8712b2d00865a9d` | definition | `d0f2ab03da60bbf0ac3a2a3a0368cb0689b447a35b2d56789d1a1db73ea8d943` |

新例的选择理由是计算关系这一错误类型与原示例完整性；不根据逐条测试句的相似度排序
选例。新例对dev420和test426仅作文本隔离检查，共846次，精确/近重复零命中；
读取train原标签，构造器不读dev/test标签。其余21条保持不变并复用旧精确隔离证据，
不把该继承证据写成重新做过全部近重复检查。原德语文本只保留本地忽略目录。

## S1：仅补这一处区别

在原语义复核第1项、既有德语条件句说明之前加入：

> An introduction such as "gilt Folgendes" points to the following content;
> classify that content instead of making the introduction a separate rule.
> A complete assertion such as "die Vorschrift gilt entsprechend" can state
> applicability on its own. Decide from the complete construction.

这些是AI撰写的通用结构说明，不是新增人工标注或真实训练示例。所有22条真实shot原样
保留；不重排独立clause，不设固定模态优先级，不用Gold挑clause。

## 未选用的修改

现有S层已经说明了条件、局部否定、并列谓词和自动效果与行为指令的区别。本轮不再
叠加同义提醒，不重写整份指导，也不把有歧义的否定表达硬编码成某一类别。
不增加新的句级输出字段，不改JSON接口、标签读取或评分器，不加入任何坐标否决。
不一次替换四条例子或合并E1/S1，避免把效果混在一起。

## 交付与验证范围

版本化修改源：`prompts/sun_compat/modality_es_minimal_v1/changes.json`，含每项自查、
来源哈希及S段落的精确before/after。准备器只有离线生成与检查模式：

```powershell
python -X utf8 formal_experiment/scripts/prepare_sun_modality_es_minimal_v1.py
python -X utf8 formal_experiment/scripts/prepare_sun_modality_es_minimal_v1.py --check
```

完整prompt和保持原输出格式的请求模板仅存本地：

- `outputs/development/sun_modality_es_minimal_v1/E1_system_prompt.txt`
- `outputs/development/sun_modality_es_minimal_v1/S1_system_prompt.txt`
- 同目录 `E1_request_template.json`、`S1_request_template.json`。

新模板使用占位符，不包含待测样本或其标签。模型、采样、user消息、原六个合成格式
示例、原Rule Record输出和 `llm_se.extract_modality_label` 取值均沿用旧流程。
原标签读取不因证据坐标错误而否决模态。机器预检见
[预检JSON](sun_modality_es_minimal_v1_preflight.json)。

具名检查仅验证单一改动隔离、训练来源、原请求接口及原标签语义，不据离线检查推断
F1改善。原22-shot以及已撤销候选的历史证据保持不变。API调用0，未启动全量测试。
后续若获得独立运行授权，应先小批确认有无目标修复和明显回归；系统性异常出现即停，
不会因为预定总量而继续无效调用。完整比较仍以全部样本的Macro-F1净收益为准，
各类和改对/改错一并披露，不以局部成功替代整体成绩。此前dev/test参与诊断，
后续这些数据上的改进仍属于探索性结果。
