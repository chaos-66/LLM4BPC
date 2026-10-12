# 本轮 Part 3 修复结果与可复现性

这轮已完成同批局部修复对照和实际重算，尚未完成完整 Sun 方法认证。

| 方法 | Precision | Recall | F1（原 201 单元） |
|---|---:|---:|---:|
| LLM-SE | 0.4393 | 0.6812 | 0.5341 |
| Sun 局部修复重建 | 0.4023 | 0.5072 | 0.4487 |
| Winter 节点修复重建 | 0.4634 | 0.5507 | 0.5033 |

同一批 115 个流程、33 条法规，同一个最终评价器；201 单元为原开发比较范围，
207 单元单列诊断，不是独立未见测试或正式 Gold。参数、数据、参考判断未改。
Sun 与 LLM-SE 共用同一个检查器、模型和转换方式，Winter 保留原方法检测机制。

已修复的确定问题包括：旧 Sun 例外范围跨主句删除 provide；删除范围后仍用
连续包络导致语义回流；角色词形和完整角色短语匹配不足；Winter 空标签与节点
索引错位。实际执行 Tsurgeon 删除并保存原文分段坐标，保留每个版本及失败记录。

Sun 仍低于 Winter 的直接计数证据集中在角色检测：Sun 的角色 TP/FP/FN 为
15/24/18，F1=0.4167；Winter 为 24/11/9，F1=0.7059。动作检测 Sun=0.4750，
Winter=0.3500。Sun 角色检查还有 18 个正例 unknown，说明抽取和动作绑定覆盖
仍有缺口；这些正例没有从分母删除。不能据此直接归因于数据本身。

Sun 的模态分类、最大非嵌套 VP/actor 处理和流程标签分解仍存在已披露的重建
差异；作者最终权重与完整抽取规则未取得。因此这里的 Sun 是局部修复重建，
不能称为 Sun 作者完整端到端结果，不能直接替换正式表三或断言论文优劣反转。

可复现性检验：已存预测重新评价得到六个完全相同的评价对象；实际重新生成
Sun 抽取、重新解析流程、运行 MPNet 和检查器，690 个 Sun/LLM-SE 类型信号
完全一致；Winter 的完整 3,795 配对/11,385 类型信号也完全一致。按照原 JSON
合同逐对象比较，数值容差为 0。LLM 抽取和 CoreNLP 解析输入复用，模态分类
未新增运行；API/网络=0。这证明本轮局部开发实验可复算，不认证完整原方法。

两次实际重算失败是比较器把 Python tuple 与 JSON array 直接比较；失败日志、
诊断与第二次代码快照全部保存。第三次按原持久化格式比较通过，没有放宽数值、
方向或违规判定。对应凭据：

- `stage3_reproduction_repair_20261012_v2.json`：所有指标和剩余方法差异。
- `stage3_reproduction_repair_20261012_v2_actual_replay_v3.json`：实际重算计数和代码哈希。
- `../evidence/stage3_reproduction_repair_20261012_v2/manifest.json`：完整来源与产物哈希。

给 GPT 的读取提示：

> 请读取 GitHub 仓库 chaos-66/LLM4BPC 的 codex/s2-prompt-simplification-v1 分支，
> 路径 formal_experiment/outputs/reports/stage3_reproduction_repair_20261012_v2.json、
> 同目录的 stage3_reproduction_repair_20261012_v2_actual_replay_v3.json 和
> formal_experiment/outputs/evidence/stage3_reproduction_repair_20261012_v2/manifest.json。
> 依据实际计数解释排名和复现范围，区分局部修复重建与完整 Sun/Winter 原论文复现。
