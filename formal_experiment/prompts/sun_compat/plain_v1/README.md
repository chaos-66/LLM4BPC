# 可直接阅读的法规抽取提示词

模型接收的完整正文在 `direct_llm_plain_record_prompt_v1.md`：系统指令、
目标原文模板和六个合成示例。正文仅描述抽取任务、六要素定义、作用范围、
字符坐标、分句、关系、歧义和 JSON 结构，不依赖外部合同文件。

默认入口为 `scripts/run_direct_llm.py`。新版要求开发模式和另存的输出，
写入 `outputs/development/s2_prompt_cleanup_v1/`；真实调用另需适用的明确授权。

## 模型与程序各自负责什么

模型只返回 `clauses` 和 `unsupported_or_ambiguous`。程序从请求绑定样本 ID
和原文，补充方法与数据结构版本；校验器填写实际检查结果。版本哈希保存在
运行 manifest 中，不发给模型。程序仍使用原来的六要素、坐标和关系校验。

| 模型使用的普通英文理由 | 含义 |
|---|---|
| unresolved reference | 指代不明确，需要上下文 |
| ambiguous scope | 语义作用范围不明确 |
| ambiguous clause boundary | 分句边界不明确 |
| context required | 需要目标原文之外的信息 |

程序把这四种理由转换为已有内部状态，保持下游接口兼容，不推断任何新要素。
示例编号改为 clause1、actor1、action1 等，原示例输入、语义选择和字符坐标保留。

## 历史结果的来源

新版依据原 v6 的抽取规则清理，输入/输出管理字段交给程序，歧义理由改为普通
英文；不能先假定这些修改对模型行为没有影响。原 v6、其他历史提示词和已记录
结果保留用于复现，历史入口需显式选择，不能把旧版指标归到新版上。
冻结的正式结果与其原始版本绑定继续有效；默认入口的清理不重写这些绑定。

旧来源：`../direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md`。
实现：`src/bpc_hybrid/plain_prompt.py` 和 `scripts/run_direct_llm.py`。
离线构建：`python formal_experiment/scripts/build_plain_prompt_v1.py --check`。
