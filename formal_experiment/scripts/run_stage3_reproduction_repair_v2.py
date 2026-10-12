"""Offline, versioned repair experiment on the frozen Part 3 population.

Run phases separately: prepare, parse, sun, winter, evaluate, verify.
No model/API download, label repair, threshold selection or old-output overwrite.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode=True

ROOT=Path(__file__).resolve().parents[1]
RUN_ID='stage3_reproduction_repair_20261012_v2'
OUT=ROOT/'outputs/evidence'/RUN_ID
REPORT=ROOT/'outputs/reports'/RUN_ID
INPUT=ROOT/'data/development/stage3_winter_paper_rerun_20261010_v1'
CONFIG=ROOT/'configs'/f'{RUN_ID}.json'
SOURCE_COMMIT='981e09c3090f44a0da388a7363db124d9ca78815'
TYPES=('missing_action','incorrect_actor','out_of_order')
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'scripts'))


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path,value):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2)
        f.write('\n')


def git_blob(path):
    return subprocess.check_output(['git','show',SOURCE_COMMIT+':formal_experiment/'+path],cwd=ROOT)


def activate_snapshot():
    import bpc_hybrid
    bpc_hybrid.__path__.insert(0,str(OUT/'source_snapshot/bpc_hybrid'))


def record_phase(name,started,details):
    write_new(OUT/f'{name}_manifest.json',{
        'run_id':RUN_ID,'phase':name,'status':'succeeded','details':details,
        'generated_at_utc':datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds':time.perf_counter()-started,'llm_api_calls':0,'network_calls':0,
        'config_sha256':sha(CONFIG),'runner_sha256':sha(__file__),
        'repair_sha256':sha(ROOT/'src/bpc_hybrid/stage3_reproduction_repairs_v1.py'),
        'reference_states_used_for_inference':False,
        'git_status_porcelain':subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),
        'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()})


def verify_preparation():
    prep=read(OUT/'preparation.json')
    for path,digest in prep['bindings'].items():
        if sha(ROOT/path)!=digest:
            raise RuntimeError('frozen input/code changed: '+path)
    reuse=read(OUT/'phase_reuse_bindings.json')
    for path,digest in reuse['bindings'].items():
        if sha(ROOT/path)!=digest:
            raise RuntimeError('reused inference artifact changed: '+path)
    return prep


def prepare():
    if OUT.exists():
        raise FileExistsError('use a new run ID; output directory already exists')
    started=time.perf_counter()
    cfg=read(CONFIG)
    if cfg['llm_api_calls_cap']!=0 or cfg['parameter_search_allowed']:
        raise RuntimeError('offline fixed-parameter design required')
    bindings={CONFIG.relative_to(ROOT).as_posix():sha(CONFIG),
              Path(__file__).relative_to(ROOT).as_posix():sha(__file__)}
    for rel in ['src/bpc_hybrid/stage3_reproduction_repairs_v1.py',
                'tools/corenlp/SunPart3PhraseRepairBridgeV1.java','resources/lexicon/actor_markers_en_v2.json',
                'src/bpc_hybrid/stage3_scope_repairs_v2.py','src/bpc_hybrid/local_mpnet_backend_v1.py',
                'resources/lexicon/condition_markers_en_v2.json',
                'resources/lexicon/constraint_markers_en_v2.json',
                'resources/lexicon/exception_markers_en_v2.json',
                'configs/stage1_structural_s11_s14.json','scripts/stage3_winter_paper_metrics_v1.py']:
        bindings[rel]=sha(ROOT/rel)
    for p in INPUT.rglob('*'):
        if p.is_file(): bindings[p.relative_to(ROOT).as_posix()]=sha(p)
    for directory in ('src/bpc_hybrid/winter_stage3',):
        for p in (ROOT/directory).glob('*.py'):
            bindings[p.relative_to(ROOT).as_posix()]=sha(p)
    for rel in ['src/bpc_hybrid/stage1_process.py','src/bpc_hybrid/stage3_sun_style_checker.py',
                'scripts/run_stage3_winter_paper_rerun_v1.py',
                'src/bpc_hybrid/estg150_b0_development_v10.py']:
        bindings[rel]=sha(ROOT/rel)
    OUT.mkdir(parents=True)
    for method,rel in [('sun','data/predictions/stage3_table3_r5_sun_rule_only_v1/predictions.json'),
                       ('ours','data/predictions/stage3_table3_r5_ours_stage2_formal_v1/predictions.json')]:
        data=git_blob(rel)
        path=OUT/f'{method}_original_records.json'
        path.write_bytes(data)
        bindings[path.relative_to(ROOT).as_posix()]=sha(path)
    prep=read(ROOT/'outputs/evidence/stage3_gamma_theta_sensitivity_20261010_v1/preparation.json')
    for rel in prep['source_code_bindings']:
        if not rel.startswith('src/bpc_hybrid/'):
            raise ValueError('unexpected snapshot source')
        target=OUT/'source_snapshot'/rel.removeprefix('src/')
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(git_blob(rel))
        bindings[target.relative_to(ROOT).as_posix()]=sha(target)
    # Known applicability only; reference states never reach either inference.
    reference=read(INPUT/'evaluation_reference.json')
    targets=[{'case_id':c['case_id'],'requirement_id':c['requirement_id']} for c in reference['cases']]
    write_new(OUT/'known_applicability.json',{'targets':targets,'reference_states_included':False})
    bindings[(OUT/'known_applicability.json').relative_to(ROOT).as_posix()]=sha(OUT/'known_applicability.json')
    write_new(OUT/'preparation.json',{'run_id':RUN_ID,'source_commit':SOURCE_COMMIT,
                                   'bindings':bindings,'design':cfg})
    record_phase('prepare',started,{'cases':len(targets),'rules':33})
    previous=ROOT/'outputs/evidence/stage3_reproduction_repair_20261012_v1'
    previous_manifests={phase:read(previous/f'{phase}_manifest.json') for phase in ('parse','winter')}
    for phase in previous_manifests:
        if previous_manifests[phase]['status']!='succeeded':
            raise RuntimeError('prior phase incomplete: '+phase)
    for name in ['corenlp_annotations.json','corenlp_scope_observations.json','winter_predictions.json']:
        shutil.copyfile(previous/name,OUT/name)
        bindings[(OUT/name).relative_to(ROOT).as_posix()]=sha(OUT/name)
    if sha(OUT/'corenlp_annotations.json')!=previous_manifests['parse']['details']['annotation_sha256']:
        raise RuntimeError('prior annotation hash drift')
    if sha(OUT/'winter_predictions.json')!=previous_manifests['winter']['details']['predictions_sha256']:
        raise RuntimeError('prior Winter prediction hash drift')
    # The first preparation record precedes copied artifacts; bind them separately
    # without replacing the immutable preparation snapshot.
    write_new(OUT/'phase_reuse_bindings.json',{'bindings':{str((OUT/n).relative_to(ROOT).as_posix()):sha(OUT/n)
        for n in ['corenlp_annotations.json','corenlp_scope_observations.json','winter_predictions.json']},
        'source_parse_manifest_sha256':sha(previous/'parse_manifest.json'),
        'source_winter_manifest_sha256':sha(previous/'winter_manifest.json')})
    for phase in ('parse','winter'):
        record_phase(phase,started,{'reused_completed_offline_phase':True,
            'source_run':'stage3_reproduction_repair_20261012_v1',
            'source_manifest_sha256':sha(previous/f'{phase}_manifest.json'),
            'source_details':previous_manifests[phase]['details']})
    print('Prepared v2 fixed inputs; reused successful 33-rule parsing and complete Winter rerun.',flush=True)


def parse():
    verify_preparation()
    started=time.perf_counter()
    from bpc_hybrid.estg150_b0_development_v10 import run_corenlp_batch_v10
    sources=read(INPUT/'regulation_sources.json')['rules']
    work=ROOT/'.tmp'/RUN_ID/'parser'
    if work.exists(): raise FileExistsError('parser attempt already exists')
    work.mkdir(parents=True)
    annotations,cases,runtime=run_corenlp_batch_v10(ROOT,[{'sample_id':r['rule_id'],'approved_text_en':r['text']}
        for r in sources],runtime_home=Path('D:/environment/stanford-corenlp-4.5.10'),work_dir=work,
        patterns_rel='resources/corenlp/sun_phrase_patterns_v3_enhanced.json')
    write_new(OUT/'corenlp_annotations.json',annotations)
    write_new(OUT/'corenlp_scope_observations.json',cases)
    record_phase('parse',started,{'records':len(annotations),'runtime':runtime,
                                'annotation_sha256':sha(OUT/'corenlp_annotations.json')})
    print(f'Fresh CoreNLP parsing complete: {len(annotations)} requirements.',flush=True)


def make_sun_records():
    from bpc_hybrid.stage3_reproduction_repairs_v1 import mask_tokens,rebuild_clause
    source={r['rule_id']:r['text'] for r in read(INPUT/'regulation_sources.json')['rules']}
    original=read(OUT/'sun_original_records.json')['records']
    annotations=read(OUT/'corenlp_annotations.json')
    from bpc_hybrid.stage3_scope_repairs_v2 import replace_scopes
    markers={field:[e['surface'].casefold() for e in read(ROOT/f'resources/lexicon/{name}_markers_en_v2.json')['entries']]
        for field,name in [('conditions','condition'),('constraints','constraint'),('exceptions','exception')]}
    jobs=[]
    for row in original:
        rid=row['requirement_id']
        for ci,clause in enumerate(row['record']['clauses']):
            for si,sentence in enumerate(annotations[rid]['sentences']):
                a,b=clause['clause_span']['start'],clause['clause_span']['end']
                if sentence['tokens'][-1]['characterOffsetEnd']<=a or sentence['tokens'][0]['characterOffsetBegin']>=b:
                    continue
                clause_v2=replace_scopes(clause,sentence,source[rid],markers)
                jobs.append({'key':f'{rid}|{ci}|{si}','rule_id':rid,'clause':clause_v2,
                             'sentence':sentence,'masks':mask_tokens(sentence,clause_v2)})
    work=ROOT/'.tmp'/RUN_ID/'surgery'
    work.mkdir(parents=True,exist_ok=False)
    classes=work/'classes'
    classes.mkdir()
    runtime=Path('D:/environment/stanford-corenlp-4.5.10')
    cp=os.pathsep.join(str(p) for p in sorted(runtime.glob('*.jar')))
    bridge=ROOT/'tools/corenlp/SunPart3PhraseRepairBridgeV1.java'
    subprocess.run(['javac','--release','8','-encoding','UTF-8','-cp',cp,'-d',str(classes),str(bridge)],
                   check=True,capture_output=True,timeout=60)
    inputs=work/'trees.tsv'
    inputs.write_text('\n'.join(j['key']+'\t'+','.join(map(str,j['masks']))+'\t'+
                                ' '.join(j['sentence']['parse'].split()) for j in jobs)+'\n',encoding='utf-8')
    result=subprocess.run(['java','-cp',str(classes)+os.pathsep+cp,'SunPart3PhraseRepairBridgeV1',str(inputs)],
                          check=True,capture_output=True,text=True,encoding='utf-8',timeout=60)
    candidates={j['key']:[] for j in jobs}
    for line in result.stdout.splitlines():
        key,field,indexes=line.split('\t')
        candidates[key].append({'field':field,'indexes':[int(x) for x in indexes.split(',')]})
    roles=read(ROOT/'resources/lexicon/actor_markers_en_v2.json')['entries']
    surfaces=frozenset((r.get('normalized') or r['surface']).casefold() for r in roles if r.get('activation') is not False)
    rebuilt={r['requirement_id']:copy.deepcopy(r['record']) for r in original}
    for record in rebuilt.values(): record['clauses']=[]
    for job in jobs:
        clause=copy.deepcopy(job['clause'])
        clause['clause_id']=job['key']
        record=rebuild_clause(clause,source[job['rule_id']],job['sentence'],candidates[job['key']],surfaces)
        record['repair_audit']['modality_scope_reused']=False
        record['repair_audit']['modality_classification_reused']=True
        rebuilt[job['rule_id']]['clauses'].append(record)
    write_new(OUT/'sun_repaired_records.json',rebuilt)
    write_new(OUT/'sun_surgery_evidence.json',{'jobs':[{'key':j['key'],'masked_original_tokens':j['masks'],
        'candidates':candidates[j['key']]} for j in jobs],'bridge_stderr':result.stderr})
    print(result.stderr.strip(),flush=True)
    return rebuilt


def sun():
    verify_preparation()
    if (OUT/'sun_manifest.json').exists(): raise FileExistsError('Sun inference already complete')
    started=time.perf_counter()
    os.environ['HF_HUB_OFFLINE']='1'
    os.environ['TRANSFORMERS_OFFLINE']='1'
    activate_snapshot()
    import torch
    torch.set_num_threads(2)
    import spacy
    from bpc_hybrid.stage3_v2.semantic_matcher_v2 import SharedSemanticMatcherV2,normalize_text_v2
    from bpc_hybrid.local_mpnet_backend_v1 import LocalMPNetBackend
    from bpc_hybrid.stage3_v2.rule_order_adapter_v3 import SharedRuleOrderAdapterV3
    from bpc_hybrid.stage3_v2.checker_v2 import SharedStage3CheckerV2
    from bpc_hybrid.stage3_reproduction_repairs_v1 import convert_segmented
    from bpc_hybrid.stage1_process import load_stage1_contract,parse_bpmn_file
    from bpc_hybrid.sun_stage3.sun_model import SunProcessModel
    repaired=make_sun_records()
    sources={r['rule_id']:r['text'] for r in read(INPUT/'regulation_sources.json')['rules']}
    originals={r['requirement_id']:r['record'] for r in read(OUT/'ours_original_records.json')['records']}
    nlp=spacy.load('en_core_web_sm')
    modeldir=ROOT.parent/'.tmp/hf_cache/hub/models--sentence-transformers--all-mpnet-base-v2/snapshots/e8c3b32edf5434bc2275fc9bab85f82640a19130'
    backend=LocalMPNetBackend(modeldir)
    matcher=SharedSemanticMatcherV2(backend)
    # Model-equivalence check against old rounded per-action evidence, not Gold.
    old_signals=read(ROOT/'outputs/evidence/stage3_gamma_theta_sensitivity_20261010_v1/signals_gamma_0.55_theta_0.45.json')['signals']
    pairs={}
    for method in old_signals.values():
        for signals in method.values():
            for detail in signals['missing_action']['evidence']['details']:
                a,b=detail['rule_action'],detail['best_model_action']
                if a and b:
                    pairs[(a,b)]=detail['similarity']
    pairs=list(pairs.items())[:50]
    lemma=lambda t:normalize_text_v2(' '.join(w.lemma_ if w.lemma_!='-PRON-' else w.text
        for w in nlp(t) if not w.is_punct and not w.is_space))
    checks=[]
    for (a,b),expected in pairs:
        actual=matcher.similarity(lemma(a),lemma(b))
        checks.append({'left':a,'right':b,'old_rounded_similarity':expected,
                       'new_similarity':actual,'absolute_error':abs(actual-expected)})
    max_error=max(x['absolute_error'] for x in checks)
    write_new(OUT/'encoder_equivalence.json',{'pair_count':len(checks),'checks':checks,
        'tolerance':0.000051,'max_absolute_error':max_error,'passed':max_error<=0.000051,
        'comparison_reference':'old MPNet rounded similarities; no compliance labels'})
    if len(checks)!=50 or max_error>0.000051:
        raise RuntimeError('local encoder equivalence failed')
    print('Local MPNet equivalence: 50 pairs within rounding tolerance.',flush=True)
    adapter=SharedRuleOrderAdapterV3(matcher)
    converted={method:{rid:convert_segmented(record,sources[rid],rid,nlp,adapter) for rid,record in records.items()}
               for method,records in [('sun',repaired),('ours',originals)]}
    # Verify the new generic converter preserves all substantive old LLM fields.
    old=read(ROOT/'outputs/evidence/stage3_gamma_theta_sensitivity_20261010_v1/converted_records.json')['ours']
    for rid in originals:
        for field in ('actions','actors','actor_action_pairs','order_relations','failed'):
            if converted['ours'][rid][field]!=old[rid][field]:
                raise RuntimeError(f'LLM converter changed {rid}/{field}')
    write_new(OUT/'converted_records.json',converted)
    cfg=read(CONFIG)['sun_ours_thresholds']
    checker=SharedStage3CheckerV2(matcher,nlp,**cfg)
    contract=load_stage1_contract(ROOT/'configs/stage1_structural_s11_s14.json')
    targets=read(OUT/'known_applicability.json')['targets']
    view={r['case_id']:r for r in read(INPUT/'inference_view.json')['items']}
    signals={method:{} for method in converted}
    for index,target in enumerate(targets,1):
        cid,rid=target['case_id'],target['requirement_id']
        item=view[cid]
        model=SunProcessModel(item['process_id'],parse_bpmn_file(ROOT/item['bpmn_path'],contract=contract),nlp)
        for method in converted:
            signals[method][cid]=checker.check_rule_record(converted[method][rid],model)
        if index%20==0: print(f'Sun/LLM-SE checking: {index}/{len(targets)}',flush=True)
    write_new(OUT/'sun_ours_signals.json',{'signals':signals})
    write_new(OUT/'similarity_cache.json',{'identity':backend.identity(),
        'vectors':{text:vector.tolist() for text,vector in backend.cache.items()}})
    record_phase('sun',started,{'cases':len(targets),'rules':len(repaired),'LLM_conversion_substantive_equality':True,
        'backend':matcher.identity(),'encoder_equivalence_pairs':50,'torch_version':torch.__version__,'spacy_version':spacy.__version__,
        'nlp_model_version':nlp.meta.get('version'),'signals_sha256':sha(OUT/'sun_ours_signals.json')})
    print('Sun/LLM-SE repaired checking complete.',flush=True)


def winter():
    verify_preparation()
    if (OUT/'winter_manifest.json').exists(): raise FileExistsError('Winter already complete')
    started=time.perf_counter()
    sys.modules['torch']=None
    import spacy
    from run_stage3_winter_paper_rerun_v1 import CachedNLP,validate_predictions
    from bpc_hybrid.winter_stage3.global_roles import collect_global_role_candidates
    from bpc_hybrid.winter_stage3.winter_clause import parse_regulation_paragraph
    from bpc_hybrid.winter_stage3.winter_model import parse_bpmn_file_winter,REACHABILITY_CORRECTED
    from bpc_hybrid.winter_stage3.winter_pair import WinterPair
    from bpc_hybrid.winter_stage3.winter_similarity import WinterSimilarity
    from bpc_hybrid.stage3_sun_style_checker import winter_signals
    from bpc_hybrid.stage3_reproduction_repairs_v1 import align_winter_model
    nlp=CachedNLP(spacy.load('en_core_web_sm'))
    view=read(INPUT/'inference_view.json')
    sources=read(INPUT/'regulation_sources.json')['rules']
    roles=collect_global_role_candidates(view,ROOT)
    resources=set(roles['roles'])
    lex=ROOT.parent/'references/winter_2020_model_check/model_check/input/files'
    names=('stopwords.txt','signalwords.txt','sequencemarkers.txt')
    stop,sw,seq=[set((lex/name).read_text(encoding='utf-8').splitlines()) for name in names]
    paragraphs={r['rule_id']:parse_regulation_paragraph(r['rule_id'],r['text'],nlp,stop,sw,seq,only_constraints=True)
                for r in sources}
    sim=WinterSimilarity(nlp)
    cfg=read(CONFIG)['winter_thresholds']
    rows=[]
    removed={}
    for index,item in enumerate(sorted(view['items'],key=lambda r:r['case_id']),1):
        model=parse_bpmn_file_winter(ROOT/item['bpmn_path'],nlp,stop,reachability_mode=REACHABILITY_CORRECTED)
        removed[item['case_id']]=align_winter_model(model)
        for rid,paragraph in sorted(paragraphs.items()):
            pair=WinterPair(nlp,sim,model,paragraph,resources,**cfg)
            rows.append({'case_id':item['case_id'],'rule_id':rid,
                         'signals':winter_signals(pair=pair,model=model,paragraph=paragraph,resource_set=resources)})
        if index%20==0: print(f'Winter checking: {index}/{len(view["items"])}',flush=True)
    validate_predictions(rows,{(c['case_id'],r['rule_id']) for c in view['items'] for r in sources})
    write_new(OUT/'winter_predictions.json',{'records':rows,'reference_states_used':False})
    record_phase('winter',started,{'pair_count':len(rows),'removed_empty_nodes':removed,'global_roles':roles,
        'lexicon_sha256':{name:sha(lex/name) for name in names},'spacy_version':spacy.__version__,
        'nlp_model_version':nlp.nlp.meta.get('version'),'predictions_sha256':sha(OUT/'winter_predictions.json')})
    print('Winter repaired inference complete.',flush=True)


def evaluate_results():
    from stage3_winter_paper_metrics_v1 import evaluate_dev_method
    reference=read(INPUT/'evaluation_reference.json')
    doc=read(OUT/'sun_ours_signals.json')['signals']
    winterrows=read(OUT/'winter_predictions.json')['records']
    lookup={(r['case_id'],r['rule_id']):r for r in winterrows}
    doc['winter']={c['case_id']:lookup[(c['case_id'],c['requirement_id'])]['signals'] for c in reference['cases']}
    scopes={'201_original':reference['order_scope'],'207_diagnostic':dict(reference['order_scope'])}
    for rid in ('R5-S7-T1','R5-S8-T1'): scopes['207_diagnostic'][rid]='TYPE_A_explicit_action_precedence'
    results={}
    for scope,order_scope in scopes.items():
        results[scope]={method:evaluate_dev_method(method,reference['cases'],
            {(method,cid,typ):row[typ] for cid,row in signals.items() for typ in TYPES},order_scope)
            for method,signals in doc.items()}
    return results


def evaluate():
    verify_preparation()
    started=time.perf_counter()
    for phase in ('parse','sun','winter'):
        manifest=read(OUT/f'{phase}_manifest.json')
        if manifest['status']!='succeeded': raise RuntimeError('incomplete '+phase)
    results=evaluate_results()
    expected=False
    f={m:results['201_original'][m]['overall']['f1'] for m in results['201_original']}
    expected=f['ours']>f['sun']>f['winter']
    report={'run_id':RUN_ID,'scope':'development_only','results':results,'expected_ranking_supported':expected,
            'complete_paper_reproduction_certified':False,'design':read(CONFIG),'llm_api_calls':0,
            'limitations':read(CONFIG)['remaining_sun_limitations']+read(CONFIG)['remaining_winter_limitations']}
    write_new(REPORT.with_suffix('.json'),report)
    lines=['# Part 3 基线修复后的同批真实对照','',
           '115 个 BPMN、33 条法规；参数及参考判断固定。Sun 修复范围边界及部分抽取，LLM-SE 复用原抽取并重新检查；Winter 使用本轮已完成的完整重跑。',
           '本报告是局部修复开发实验，不认证完整 Sun/Winter 原论文复现。','',
           '| 方法 | 201 单元 P | R | F1 | 207 单元诊断 F1 |','|---|---:|---:|---:|---:|']
    for method,label in [('ours','LLM-SE'),('sun','Sun 局部修复重建'),('winter','Winter 节点修复重建')]:
        m=results['201_original'][method]['overall']
        lines.append(f'| {label} | {m["precision"]:.4f} | {m["recall"]:.4f} | {m["f1"]:.4f} | {results["207_diagnostic"][method]["overall"]["f1"]:.4f} |')
    lines+=['',f'预期 LLM-SE > Sun > Winter 是否成立：{expected}。所有结果保留，不作为挑选样本或修改参数的依据。',
            '', '剩余复现差异：','']+['- '+s for s in report['limitations']]
    REPORT.with_suffix('.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    record_phase('evaluation',started,{'expected_ranking_supported':expected,
                                     'report_sha256':sha(REPORT.with_suffix('.json'))})
    artifacts={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
    write_new(OUT/'manifest.json',{'run_id':RUN_ID,'status':'succeeded','scope':'development_only',
        'command':'run_stage3_reproduction_repair_v2.py prepare / sun / evaluate / verify; prepare explicitly reuses completed v1 parse and Winter phases',
        'artifacts':artifacts,'config_sha256':sha(CONFIG),'llm_api_calls':0,'network_calls':0,
        'complete_paper_reproduction_certified':False,'expected_ranking_supported':expected})
    print(json.dumps({'primary_f1':f,'expected_ranking_supported':expected},ensure_ascii=False),flush=True)


def verify():
    verify_preparation()
    manifest=read(OUT/'manifest.json')
    for rel,digest in manifest['artifacts'].items():
        if sha(OUT/rel)!=digest: raise RuntimeError('artifact changed: '+rel)
    actual=evaluate_results()
    if actual!=read(REPORT.with_suffix('.json'))['results']:
        raise RuntimeError('saved prediction reproduction failed')
    for scope,methods in actual.items():
        expected=201 if scope=='201_original' else 207
        for method,result in methods.items():
            m=result['overall']
            if m['scored_cells']!=expected: raise RuntimeError('denominator drift')
            f1=2*m['TP']/(2*m['TP']+m['FP']+m['FN'])
            if abs(f1-m['f1'])>1e-12: raise RuntimeError('independent F1 count check failed')
    print('Verified all hashes, six evaluation objects and independent F1 counts.',flush=True)


if __name__=='__main__':
    operations={'prepare':prepare,'parse':parse,'sun':sun,'winter':winter,'evaluate':evaluate,'verify':verify}
    if len(sys.argv)!=2 or sys.argv[1] not in operations:
        raise SystemExit('choose prepare, parse, sun, winter, evaluate or verify')
    operations[sys.argv[1]]()
