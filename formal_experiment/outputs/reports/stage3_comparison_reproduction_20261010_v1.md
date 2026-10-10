# 两组 Stage 3 结果的严谨性与再次复算

日期：2026-10-10；所属任务：S3-COMPARISON-CHECK-V1。

在已确认的顺序纳入问题上，207 单元的第二组更合理：将源文本已经明确为动作先后关系的
R5-S7-T1、R5-S8-T1 纳入三方共同评分，不因 Sun/LLM-RE 未抽齐端点而排除。
选择依据是任务语义和共同范围，不是 F1 大小或预期排名。
第二组只修正两个已确认的遗漏，完整范围的独立语义核验仍未完成，暂不替换 canonical 表。

| 比较点 | 第一组：201 单元 | 第二组：207 单元 |
|---|---|---|
| 顺序范围依据 | 包含依赖抽取结果的排除理由 | 纳入两个已明确的动作先后要求 |
| 三方数据、参考和最终计分 | 一致 | 一致 |
| 当前结果定位 | 原开发表，可复算 | 修正范围的诊断结果，可复算 |
| 完整源语义范围已经独立核验 | 否 | 否 |
| 本次从 Git 固定证据再次计分 | 完全一致 | 完全一致 |

| 方法 | 第一组 F1 | 第二组 F1 |
|---|---:|---:|
| LLM-RE | 0.5341 | 0.5281 |
| Winter | 0.5033 | 0.5065 |
| Sun | 0.4458 | 0.4405 |

## 已完成的复算验证

本次在新 Python 进程中，直接从固定 Git 提交
`57e1e5c07a0cb0d0ba6e697b036a33fd86640298` 读取 5 个已提交文件的内容：
共同参考、原 Sun/LLM-RE 逐案例信号、Winter 重跑逐对预测、评价器和先前核查记录。
没有读取临时工作树、绝对路径预测文件或当前未提交的数据。

每组的三方评价结果对象均与先前保存对象完全相等。
另用独立的计数实现复核 TP/FP/FN/TN、unknown、正负支持和 F1，也全部一致。
完整计数、固定文件路径及 SHA-256 见同名 JSON。

复算代码只依赖 Git 与 Python 标准库；不需要加载模型、API 密钥或网络。
固定代码版本、输入、逐案例预测和评分范围，能够重复得到这两组计分结果。

## 复现边界

本次验证的是保存预测之后的评价复现，没有从法规/BPMN重新运行三方全部推理。
Winter 此前已有完整原生重跑且信号一致的证据；Sun/LLM-RE 本轮没有重新抽取。
因此不能把这里的验证写成“三方重新生成预测后完全一致”。
若要求完整推理复现，还须固定本地模型权重、运行环境、抽取/转换/检查实现及参数；
LLM 部分另需明确模型版本、请求配置和随机性处理，真实新调用仍需授权。

两组差距小，并不证明范围选择合理；评价器正确与样本纳入合理也分别需要证据。
下一步应先依据源文本独立固定完整顺序范围，再复用已冻结预测重算另版本开发表。

## 可重复执行的只读命令

在仓库根目录用 PowerShell 执行以下命令。读取固定提交的 Git 对象，
对两组结果和独立计数执行一致性断言，并输出 JSON；不写文件、不调用模型/API。

```powershell
@'
import hashlib,json,subprocess
commit='57e1e5c07a0cb0d0ba6e697b036a33fd86640298'
prefix='formal_experiment/'
def blob(path):
    return subprocess.check_output(['git','show',commit+':'+prefix+path])
def load(path):
    return json.loads(blob(path))
paths={
'reference':'data/development/stage3_winter_paper_rerun_20261010_v1/evaluation_reference.json',
'sun_ours':'outputs/evidence/stage3_comparison_check_20261010_v1/sun_ours_selected_dev_signals_v1.json',
'winter':'outputs/evidence/stage3_winter_paper_rerun_20261010_v1/predictions.json',
'previous_check':'outputs/reports/stage3_comparison_check_20261010_v1.json',
'evaluator':'scripts/stage3_winter_paper_metrics_v1.py'}
data={name:blob(path) for name,path in paths.items()}
ref=json.loads(data['reference']);shared=json.loads(data['sun_ours'])
pairs={(r['case_id'],r['rule_id']):r['signals'] for r in json.loads(data['winter'])['records']}
previous=json.loads(data['previous_check'])
ns={};exec(compile(data['evaluator'],paths['evaluator'],'exec'),ns)
assert len(ref['cases'])==115 and len(pairs)==3795
signals={m:{(m,c,t):s for c,types in shared['signals'][m].items() for t,s in types.items()} for m in ['sun','ours']}
signals['winter']={('winter',c['case_id'],t):s for c in ref['cases'] for t,s in pairs[(c['case_id'],c['requirement_id'])].items()}
expanded=dict(ref['order_scope'])
for rid in previous['order_scope_sensitivity']['source_explicit_added_rules']:
    expanded[rid]=ns['MAIN_ORDER_TYPE']
result={}
for scenario,scope in [('original_201',ref['order_scope']),('expanded_207',expanded)]:
    result[scenario]={}
    for m,sig in signals.items():
        actual=ns['evaluate_dev_method'](m,ref['cases'],sig,scope)
        saved=previous['recomputed_metrics'][m] if scenario=='original_201' else previous['order_scope_sensitivity']['metrics'][m]
        assert actual==saved,(scenario,m,'original evaluator mismatch')
        # A separate count implementation checks the original evaluator.
        counts={k:0 for k in ['TP','FP','FN','TN','unknown_positive','unknown_negative','scored_cells','positive_support','negative_support']}
        for c in ref['cases']:
            for t in ['missing_action','incorrect_actor','out_of_order']:
                if t=='out_of_order' and scope.get(c['requirement_id'])!='TYPE_A_explicit_action_precedence':continue
                expected=c['reference_states'].get(t,'not_scored')
                if expected not in ['violated','satisfied']:continue
                status=sig[(m,c['case_id'],t)]['status']
                counts['scored_cells']+=1
                if expected=='violated':
                    counts['positive_support']+=1
                    counts['TP' if status=='violated' else 'FN']+=1
                    if status=='unknown':counts['unknown_positive']+=1
                else:
                    counts['negative_support']+=1
                    counts[{'violated':'FP','satisfied':'TN','unknown':'unknown_negative'}[status]]+=1
        assert all(actual['overall'][k]==v for k,v in counts.items()),(scenario,m,'independent count mismatch')
        f1=2*counts['TP']/(2*counts['TP']+counts['FP']+counts['FN'])
        assert abs(f1-actual['overall']['f1'])<1e-14
        result[scenario][m]={**counts,'precision':actual['overall']['precision'],'recall':actual['overall']['recall'],'f1':actual['overall']['f1'],'entire_saved_evaluation_equal':True,'independent_counts_equal':True}
report={'schema_version':'stage3_comparison_reproduction@1.0.0',
 'task_id':'S3-COMPARISON-CHECK-V1-REPRODUCTION','date_local':'2026-10-10',
 'source_git_commit':commit,'source_files':{name:{'path':prefix+paths[name],'sha256':hashlib.sha256(value).hexdigest()} for name,value in data.items()},
 'execution':'Fresh Python process; source data and evaluator loaded exclusively from Git commit blobs; no temporary worktree or absolute artifact paths used.',
 'source_file_count':len(data),'real_llm_api_calls':0,'model_inference_runs':0,'reference_modified':False,'full_tests_run':False,
 'validated_boundary':'Frozen-prediction evaluator replay and independent count recomputation. New Stage 1/2/3 inference and provider-level output repeatability were not tested.',
 'scope_added_rules':previous['order_scope_sensitivity']['source_explicit_added_rules'],'results':result,
 'conclusion':'Both scope variants reproduce exactly from committed evidence. Expanded scope removes two documented extraction-dependent exclusions; full source-semantic scope review remains pending.'}
print(json.dumps(report,ensure_ascii=True,sort_keys=True))
'@ | python -
```

这是只读分析与报告制品，未改变实验代码、配置、参考标签或原表。
没有运行项目检查、测试套件或新模型推理；scoped Git commit 用作本次记录。
