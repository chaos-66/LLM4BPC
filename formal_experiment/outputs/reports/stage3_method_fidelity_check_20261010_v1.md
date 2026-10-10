# Stage 3 三种方法的实现忠实度核查

核查日期：2026-10-10。核查对象是现有表三的具体执行链，不把历史方法登记中的
“method-level independent reconstruction”解释成作者原实现或逐项完全一致。
本报告是方法证据报告，不是新的任务状态页。

**结论：当前 Sun 不是完整忠实的 Sun 原方法；Winter 是以公开原型为基础、带修复和
其他差异的重建，也不是论文和原型的完全复现。现有指标可以从冻结预测复算，但不能
据此认证方法忠实度，不能把排名写成原论文方法的普遍优劣。**

## 核查范围与来源

- Sun/LLM-SE 实际来源 worktree：`D:/Paper/experiment/LLM4BPC-s3-ext-pc-v1`，
  HEAD `981e09c3090f44a0da388a7363db124d9ca78815`，核查时工作树干净。
- Sun 抽取：`run_stage3_table3_r5_sun_stage2_v1.py` → `run_b0_batch_v10` →
  `build_canonical_record_v10` / `b0_v10/actor_action.py`；33 条法规、37 个 clause。
- Sun 与 LLM-SE 下游：同一个 `canonical_to_rule_record_v2`、顺序适配器、
  `SharedStage3CheckerV2` / `SunScorer`、MPNet backend、gamma=0.55、theta=0.45。
- Winter：本工作区的 `winter_clause.py`、`winter_model.py`、`winter_pair.py`、
  `winter_similarity.py`，以及完整重跑的 manifest、3,795 个 pair 的冻结预测。
- Sun 本地 PDF 是较早作者稿，核对完整相关页 §4.1、§4.2、§4.3；最终发表版页面
  DOI `10.1007/s11227-023-05626-0` 的摘要可读，但全文订阅受限。
  最终版 BERT-TextCNN 与旧稿 BERT+softmax 的版本差异已有历史证据，不能混称。
- Winter 原论文：https://eprints.cs.univie.ac.at/6508/1/compliance_assessment_paper_ER2020.pdf，
  核对 §3.1–3.3、§4；原型目录只按文本读取，不 import、不执行。
- 原始论文完整权重、规则和词典缺口继续存在；这次不能认证 Sun 最终版的全方法一致性。

伴随 JSON 保存 30 个来源文件的原始 SHA-256、115 个 BPMN 检查、4 个逐例证据、
纯函数诊断和三方法计数复算。未运行新的模型推理、API 或全量测试。

## Sun：哪些一致，哪些存在实质差异

| 项目 | 原论文可核实描述 | 当前表三实际执行 | 判断 |
|---|---|---|---|
| 句级模态分类 | 深度分类器产生四类标签；最终版为 BERT-TextCNN | marker/definition-structure 优先，分类器只作 fallback；本批 37 个 clause 全部走非分类器路线 | 实质算法差异，不是换一个 seed |
| 分类器语言 | 本地 checkpoint 声明输入为德语 | R5 runner 把同一英文同时填入 `approved_text_en` 与 `raw_text_de` | 输入合同偏离；不能说它是本批最终模态低分的原因 |
| 动作抽取 | 作者稿 §4.2.2：提取 VP，排除 modality/condition/constraint/exception，动作必须在这些概念之后处理 | `build_canonical_record_v10` 的动作来自独立依赖树 helper；未把已抽取的 scope spans 交给它排除；helper 选 ROOT/部分 modal governors，使用连续 min/max 区间和长度截断 | 已证实算法和输出均存在偏离 |
| Tregex/Tsurgeon | 句法树模板和概念移除是动作处理依据 | scope/modality 使用 Tregex 观测；最终 actor/action 改用依赖 helper；Tsurgeon operation 为空、disabled | 不能把“有 CoreNLP/Tregex”视为全部短语规则忠实实现 |
| 角色词典及形态 | 论文扩展领域角色词典；完整原词典不可得 | 本地 50 个 actor surfaces，head 必须精确在词典内；无 head 词形还原 | 明确适配与覆盖缺口，不能保证原论文的角色覆盖 |
| 流程标签语义 | 作者稿 §4.1 按 Leopold 思路拆解标签中的 action 与 business object | `SunProcessModel.actions` 直接保留整个 activity/event 名称；business object 另用简单 spaCy 依赖抽取 | 流程标签分解未完整实现；短法规动作与长流程标签比较存在粒度不一致 |
| 定义 5–7 | 缺失动作比例、动作绑定的角色集合与存在量词、顺序可达性 | 主要数学结构确实来自这些定义；角色 min/存在量词不是此次随意改成 max 的结果 | 核心公式有依据；额外 unknown/不完整映射守卫属于项目策略 |
| 定义 4 关联筛选 | 先匹配相关法规，再检查 | 当前 V2 checker 对各规则直接算三类信号；表三最终只评案例的目标规则，不以 matching score 筛选 | 合法的已知配对下游比较，但不是原论文全流程评价 |

实际配置 `estg150_b0_enhanced_s27_v10a.json` 本身写了 `paper_faithful_b0: false`、
`tsurgeon_enabled: false` 和 marker-first。已有历史准入允许“有披露的独立重建”，
不等于这些实际差异可以省略。

### 已进入冻结预测的具体问题

1. **R5-D-01 / D-02，动作和条件没有正确分离。**
   Sun 同时把 `intends to further process ...` 标成 condition 内的内容和 action；
   真正的通知义务动作则只剩 `provide`。在 baseline `case_9c6fcd32f03c`，
   `provide` 对现有完整通知任务的相似度仅 0.2764，低于 0.55，产生缺失动作误报。
   因此该例误报的直接触发因素是动作过短，不是仅凭“条件动作被保留”就能解释。
   D-02 baseline `case_f7bb207445df` 同样误报；LLM-SE 的完整通知短语相似度 0.6321，
   该例没有误报。D-01 的 LLM-SE 也因另一条额外 action 误报，不能声称 LLM 总能解决。
2. **R5-D-03，时间约束还在 action 内。**
   Sun action 为 `be informed by the controller before the restriction of processing is lifted.`，
   包含同时已经抽作 constraint 的 `before ...`。这直接证明 scope 未被按所述顺序移除。
   LLM-SE 的 `be informed` 又过短：baseline 相似度 0.2335，反而由 LLM-SE 误报。
   更细的短语与整段任务名搭配，并不自动提高语义匹配质量。
3. **角色词典门控确实拒绝关键 GDPR 表达。**
   用原 helper 和冻结词典做纯函数诊断：`the controller` 接受；`The data subject`
   （head=subject）拒绝；`certification bodies`（head=bodies）拒绝；
   `certification body`（head=body）接受。冻结 D-08 的 actors 为空，角色项 unknown。
   这证明词典和形态策略存在缺口；没有据此断言所有角色缺失都只由词典造成。
4. **角色公式和候选业务对象也会影响 LLM-SE。**
   D-08 baseline 中 LLM-SE 提取 `The data subject`，但匹配任务的流程角色是 Controller，
   候选还含业务对象，最小相似度为 0.1917，最终角色误报；Winter 则判 satisfied。
   共享检查器仍会受不同抽取结果影响，LLM-SE 不是每例、每类都占优。

原表 Sun 的 33 个角色违规正例中，20 个漏报全部是 unknown：11 个没有规则 actor、
1 个 actor-action map 不完整、8 个动作映射未过 gamma。LLM-SE 对应只有 6 个。
**因此当前 Sun 低分存在可定位的抽取/匹配瓶颈，不能先假定原论文方法天然弱。**

### 分类器语言的因果边界

英文进入德语声明的 classifier 是确认的偏离。记录级分类器 33 条均为 definition，
但最终 37 个 clause 是 obligation 34、definition 2、permission 1；路线分别是
marker-obligation、definition-structure、marker-permission，没有 classifier fallback。
先前 2,220 次纯路由诊断已确认，单改 classifier 输出或 alignment 不改变这批最终标签。
因此修复语言合同是忠实度工作，却不能承诺只修这一点就提高现有 F1。

## Winter：更接近公开原型，仍不能称完全复现

| 项目 | 本次代码对照结论 | 与当前排名的关系 |
|---|---|---|
| signal words、依赖分 clause、最高相似任务、missing/resource cost | 主链条和原型一致；不接收 Sun/LLM 抽取 | 这些是 Winter 自己的内部方法，不能强制套入 Sun 的 actor-action schema |
| 全局角色集合 | 原型 main 从所有 BPMN `process@name` 收集；当前从同一 115 个盲输入收集 7 个角色 | 符合原型逻辑，未使用 Gold；不是违规增加答案 |
| 模型版本 | 原型记录 spaCy 2.3.0 / en_core_web_sm 2.3.0；当前是 3.8.13 / 3.8.0 | 算法家族相同，解析和相似度数值不能声明原版本完全一致 |
| 可达性 | 原型使用 `reachability[targetid]`；当前改为 `reachability[sourceid]` | 已披露的原型 bug 修复，是版本差异 |
| Flow condition 词形处理 | 原型 Clause 分支只保留 literal `PRON`，非 Clause 分支会正常取词形；当前统一取正常词形，并采用 `-PRON-` 分支 | 又一项真实差异，不能只说唯一变化是可达性修复 |
| 同名 participant 合并 | 原型 dict 赋值会覆盖；当前 extend 合并 | 在这 115 个 BPMN 中没有同名 participant，因此该差异不作用于本批 |
| 空标签和节点 ID | 原型及当前都把空标签从 label list 去掉，却仍保留对应 DOM node；随后用同一索引取两列 | 两者共同保留的具体实现缺陷，影响顺序节点绑定 |
| 顺序抽取 | 原型及当前的部分 marker 路线把同一个 obligation 用作 condition 和 consequence | 原型字面行为与论文描述的两端顺序关系并不完全一致 |
| 无角色证据的 0 cost | 原型没发现角色违规即 0 cost；当前 wrapper 映射为 satisfied | 与 Sun unknown 的表达有别；已检查的两个目标 cell 改 unknown 后整体 F1 不变 |

**空标签问题已经检查到真实输入。**115/115 BPMN 都有名为空的 End，节点列表保留它，
标签列表跳过它。用活动实现的纯 mapping 方法和固定相似度诊断，任务标签 `inform`
确实可能返回 `End` 的节点，而正确对应是 `Activity_1`。这不是仅凭静态阅读猜测。
missing/resource cost 主要用 label 和 process resource，不能把该问题直接归因于它们的
现有 F1；顺序成本需要 node ID，必须在新版本中独立检查。

Winter 原表 8 个顺序评分项全部 unknown，所以这些顺序实现问题不能解释原表
Winter 高于 Sun。扩展顺序诊断的行为仍不能被认证成论文忠实的顺序检查。

原论文 §3.3 的叙述、印出的 cost 公式和公开原型之间也存在需区分的语义问题：
式 (4) 分子写的是顺序满足条件，式 (5) 的谓词使用角色高相似度，却称 cost 高表示违规。
不能默认逐字照抄公式、修正文义和照原型执行三个目标同时等价。后续版本必须明确
采用论文意图还是原型行为，并保存原版本，不能借此改阈值或追预期排名。

## 当前排名具体来自哪里

以下是保持原表 201 个评分 cell、69 个正例、132 个负例的复算。
三种方法使用相同的最终计数规则；unknown 正例计 FN。

| 方法 | 动作缺失 F1 | 角色错误 F1 | 顺序错误 F1 | TP | FP | FN | 总体 micro F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sun 本地 v10a 重建 | 0.4554 | 0.4262 | 0.5000 | 37 | 60 | 32 | 0.4458 |
| Winter 本地原型重建及修复 | 0.3500 | 0.7059 | 0.0000 | 38 | 44 | 31 | 0.5033 |
| LLM-SE＋共享 Sun 风格检查器 | 0.4935 | 0.5684 | 0.5000 | 47 | 60 | 22 | 0.5341 |

- Winter 比 Sun：角色 TP 多 11、动作缺失 TP 少 9、顺序 TP 少 1；总体 TP 多 1，FP 少 16。
  其总体优势主要出现在角色项，不能泛称它的所有抽取和检查都优于 Sun。
- LLM-SE 比 Winter：动作缺失 TP 多 5、角色 TP 多 3、顺序 TP 多 1；总体 TP 多 9、FP 多 16。
  它的召回更高、精度反而更低；F1 分别为 `94/(94+60+22)` 与 `76/(76+44+31)`。
  它高于 Winter 是计数的真实结果，不能推出每一类或每一例都更好。
- Sun 原论文的实验条件与这里不同，而当前还有以上实现差异。因此不能只用“数据不同”
  为排名背书，也不能因为原论文 Sun 高于 Winter 就要求本地分数按该顺序出现。
- 第二组补充顺序范围的分数见已有核查报告；此次未改变范围。补入两条规则不会自动
  修复基线忠实度，也不会解决原表已确认的动作/角色问题。

## 应如何使用这次结果

1. 现有数字保留为冻结的本地重建比较，不改分、Gold、样本或参数来追排序。
2. 要回答“Sun 原方法为何低于 Winter”，先在独立新版本修正/明确 Sun 的动作 scope
   排除、角色词典与形态、流程标签语义分解和正确语言的分类器策略；逐例验证后才重跑。
3. Winter 的 node-label 对齐、Flow 和原型/论文语义差异也要在独立新版本明确处理，
   保留当前原型版本作敏感性参照；不能只修 Sun 而把 Winter 未检查的问题掩盖过去。
4. 统一输入、reference、评分范围和最终 evaluator，再检查新版本输出。方法内部的
   阈值或表示可以各自合理设置，但差异必须符合预先明确的方法合同。
5. 冻结预测的计数复现已再次通过；三种方法从零重新生成预测的完整复现尚未认证。
   Stage 2 已锁定主表不因本次 Stage 3 核查而改变。此次没有额外 API、Gold 或全量测试授权。

本次只新增方法核查报告及证据；实验代码、配置、旧预测、旧指标和用户未提交的其他
修改均保持原样。文档检查和 scoped Git checkpoint 是本批次验证与记录范围。

## 离线重做新增诊断

总体指标的冻结预测复算仍使用已验证的
[完整计数复现命令](D:/Paper/experiment/LLM4BPC/formal_experiment/outputs/reports/stage3_comparison_reproduction_20261010_v1.md)。
下面的 PowerShell 命令只读取明确 commit 的 Git blobs，执行项目自身的两个纯函数，
不读取工作树版本、不加载模型、不写文件、不访问网络，也不执行 references 中的原型。
核查时已实际执行，得到 `[true,false,false,true]` 和错误绑定的 `End`。
前提是此仓库仍包含这两个已保留的提交对象，工作目录为仓库根目录。

```powershell
@'
import ast,json,re,subprocess
from types import SimpleNamespace
SUN_COMMIT='981e09c3090f44a0da388a7363db124d9ca78815'
WINTER_COMMIT='263b1ca3f3a3f4a330f9fc0d9e25003b86d97ffe'
def blob(commit,path):
 return subprocess.check_output(['git','show',commit+':formal_experiment/'+path]).decode('utf-8')
source=blob(SUN_COMMIT,'src/bpc_hybrid/b0_v10/actor_action.py')
tree=ast.parse(source)
f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='filter_actor_span')
n=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_NON_ACTOR' for t in n.targets))
ns={'re':re,'LexiconV2Runtime':object,'Any':object}
exec(compile(ast.Module(body=[n,f],type_ignores=[]),'frozen_actor_filter','exec'),ns)
doc=json.loads(blob(SUN_COMMIT,'resources/lexicon/actor_markers_en_v2.json'))
surfaces=frozenset(r.get('normalized') or r['surface'].casefold() for r in doc['entries'] if r.get('activation') is not False)
lex=SimpleNamespace(actor_surfaces=surfaces)
probes=[]
for phrase,head in [('the controller','controller'),('The data subject','subject'),('certification bodies','bodies'),('certification body','body')]:
 probes.append(ns['filter_actor_span'](phrase,0,len(phrase),lex,head_word=head) is not None)
assert probes==[True,False,False,True]
tree=ast.parse(blob(WINTER_COMMIT,'src/bpc_hybrid/winter_stage3/winter_pair.py'))
cl=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='WinterPair')
f=next(n for n in cl.body if isinstance(n,ast.FunctionDef) and n.name=='_max_text_obligation_to_model')
ns={}
exec(compile(ast.Module(body=[f],type_ignores=[]),'frozen_mapping','exec'),ns)
fake=SimpleNamespace(sim=SimpleNamespace(text_model_obligation=lambda a,b:1.0 if b==['inform'] else .1))
result=ns['_max_text_obligation_to_model'](fake,SimpleNamespace(lemmatized='inform'),{'Controller':['Start','End','Activity_1','Activity_2']},{'Controller':[['context'],['inform'],['lift']]})
assert result[0]=='End' and result[1]==['inform']
print(json.dumps({'actor_acceptance':probes,'mapped_node_id':result[0],'mapped_label':result[1],'expected_node_id':'Activity_1'}))
'@ | python -
```
