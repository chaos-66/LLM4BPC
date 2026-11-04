# 冻结提示词后的验证方案

任务 `SUN-MODALITY-VALIDATE-001`。本轮用户要求继续改进；已准备执行与分析代码，
当前没有新增API授权、调用或性能结果。保持已经审阅的reviewer提示词原字节。

| 比较 | 新调用 | 用途 |
|---|---:|---|
| test：reviewer vs 已保存few-shot | 426 | 检查54条旧错修复与372条旧对回归；已知测试错误的探索性对照 |
| dev：few-shot vs reviewer，同期两臂 | 420 + 420 | 冻结prompt后的配对留出验证 |

dev按样本编号排序，每对相邻提交，先后顺序交替；8路并发不保证完成顺序。
全部1266个请求预先绑定，不按错误、两模型分歧或Gold选择样本。没有Sun→LLM修补、
oracle挑选或固定标签优先级。真实示例仍为原18条train句，无新增dev/test示例。

运行器仅读取文本；批次完成并通过账本核验后，独立报告器才读取dev/test标签。
运行中不看成绩、不修改prompt、不根据阶段成绩提前停止；预算、时间窗、传输或
记录异常则停止新发并收齐在途返回。每个“划分/提示词/样本”最多一次，零重试。
未结算或失败调用禁止自动续跑；完整结算的已完成调用不重发。部分批次不生成最终成绩。

主验证是dev的配对Macro-F1差值及bootstrap区间（B=10000、seed=20261103）；
同时报告accuracy的McNemar检验、四类P/R/F1/support/FP/FN、改对/改错、共同错误及
解析失败。区间跨0表示改进证据不足；总体上升不等于四类都改善，不隐藏负结果。
test对照使用历史调用，服务时间不同，不能给出严格同期因果解释。

dev过去用于监督基线选模型，文本也用于本地重复检查。现有版本化材料未显示它的
标签参与这两版LLM提示词调参，因此这里只称“LLM提示词的留出验证”。同语料dev
不是全项目从未使用的新测试集。若根据dev结果继续改prompt，后续独立泛化主张
需要另有未参与调整的数据。原句残缺、首有效clause投影和标注歧义仍保留。

拟申请：官方 `https://api.deepseek.com`，`deepseek-v4-pro`，1266次，人民币80元
总上限，8路并发，零重试，仅空闲时段。价格与模型版本于2026-11-03核验官方文档；
费用估算见预检，运行器用累计费用+所有在途预留守住上限。原句、示范和完整返回
仅在Git忽略目录保留，版本化文件只保存ID、标签、统计、哈希与通用说明。

```powershell
# 离线准备，不发送请求、不读取环境凭据
python formal_experiment/scripts/prepare_sun_modality_validation_v1.py

# 仅在用户另行批准，并生成绑定预检的新授权文件后执行
python formal_experiment/scripts/run_sun_modality_validation_v1.py --execute --authorization <new-authorization.json>
python formal_experiment/scripts/build_sun_modality_validation_report_v1.py --authorization <new-authorization.json>
```

当前准备合同：`configs/supplement/sun_modality_validation_v2.json`。
当前预检：`outputs/reports/sun_modality_validation_v1_preflight_v2.json`。
首次v1准备按60元拟上限生成，完成预检后发现无缓存估算61.12元超过该值；
v2将拟上限改为80元，不变更请求。首次合同和预检保留为未执行历史，不作为运行入口。
运行器隔离加载已测试的旧few-shot协调器，仅适配请求来源和独立目录，不修改旧源码；
复用统一预算预留、单写者哈希链账本、零重试及停止后收集在途返回的行为。

2026-11-04运行中断与监督式恢复：原运行器在第734条批次遇到1条HTTP429后按约定
停止，没有自动续跑或重试。独立入口`continue_sun_modality_validation_v1.py`仅从
原1266条授权清单扣除所有已尝试ID，发送剩余532条；原账本和停止快照保留，
并发降为4、发送间隔至少1秒，未知费用完整预留，合并总预算仍为80元。
这是对已发生传输中断的显式恢复步骤，不扩大数据、调用数量或改变prompt。
所有计划调用各尝试一次后才给成绩；429按无预测保留dev420条主分母，419条
有响应配对只作单独敏感性诊断。入口再次失败时仍停止，不自动循环恢复。
