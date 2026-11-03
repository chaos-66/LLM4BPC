# few-shot剩余54条错误：AI审读与提示词修改依据

这是保存预测的离线分析。逐条解释由AI提出，未进行独立人工裁决；没有修改Gold或调用API。

| 审读家族（解释性归类） | 条数 |
|---|---:|
| 资格、数量、期限与规范边界（含歧义） | 17 |
| 法律后果、状态或陈述被读成义务/许可/禁止 | 23 |
| 输入不完整、主断言不足 | 3 |
| 独立多命题投影为第一clause标签 | 3 |
| 指令被范围吸收或标注边界不明确 | 4 |
| 前置条件被拆成独立规则 | 1 |
| 并列谓词或句尾规范作用域遗漏 | 2 |
| 申请触发的选择权未被识别 | 1 |

程序核实：426条中18条有多个clause；54个错误中有5条。其中4条的金标类别已出现在后续clause，首有效clause投影没有使用它。
逐条审读将其中1条归为前置条件误拆，另3条归为独立多命题投影限制；两类修法不同。

训练集对照（以下仅为透明词组匹配候选，不是已证明的全句规则）：

| 标记家族 | train各类计数 |
|---|---|
| commencement | {"definition": 54, "obligation": 6} |
| liability | {"definition": 3} |
| automatic_amount | {"definition": 17} |
| status_waiver_or_no_effect | {"definition": 27, "obligation": 2} |
| declarative_applicability | {"definition": 14} |
| negative_consideration | {"definition": 1, "obligation": 1, "prohibition": 6} |
| negative_application | {"obligation": 2, "prohibition": 10} |
| upon_request | {"definition": 4, "obligation": 7, "permission": 8} |
| conditional_only | {"definition": 45, "obligation": 11, "permission": 6} |

建议写入新prompt的审读步骤：

1. 先定位完整主断言，把条件保留在conditions中，识别德语无wenn的倒装条件。
2. 区分法律状态/自动结果与要求主体行动；生效、责任归属、自动金额变化不能只因法律约束力就标义务。
3. 查否定作用域：不发生、不受影响、免除义务与禁止实施动作分开。
4. 查资格与选择：数量、期限或条件不自动决定definition；明确申请选择也不必出现kann。
5. 扫描并列谓词和句尾独立义务/禁止，保留真实clause顺序，不用固定类别优先级。
6. 残缺输入不补词猜标签；短句有完整适用断言时也不因缺actor/action丢弃。

新分支不改第一有效clause评价器；多命题投影限制仍然存在。效果必须另行授权运行后判断。

- 错误家族与拟人工审读步骤是AI解释假设，不是已验证的模型内部原因或新增人工金标。
- train标记统计是词组匹配候选，未隔离每个标记在主句/从句中的角色，不能直接视为分类规则的精确率。
- 参考同一测试集错误后设计prompt，存在选择偏差；无独立盲测或新性能证据。
- 后续clause已有金标类别不代表可无损改成句级首标签；不通过重排、删除或统一独立命题取巧。
- 输入残缺和跨类近似措辞只能列为待复核问题，不修改Gold或虚构缺失上下文。
