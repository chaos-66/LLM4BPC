"""Regenerate v2 Sun from cached CoreNLP; rerun both detectors and Winter.

No changed parameters, sample selection, reference states, API or download.
This checks reproducibility of this repair study, not complete paper fidelity.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.dont_write_bytecode=True


def json_view(value):
    """Compare exact persisted JSON values; tuples are serialized as arrays."""
    return json.loads(json.dumps(value,ensure_ascii=False,allow_nan=False))


def replay(attempt_id):
    import run_stage3_reproduction_repair_v2 as run
    from resume_stage3_repair_sun_v2 import bind_structural_resources
    started=time.perf_counter()
    run.verify_preparation()
    run.verify()
    result_path=run.ROOT/f'outputs/reports/{run.RUN_ID}_{attempt_id}.json'
    if result_path.exists():
        raise FileExistsError('replay output exists; select a new attempt ID')
    run.activate_snapshot()
    os.environ['HF_HUB_OFFLINE']='1'
    os.environ['TRANSFORMERS_OFFLINE']='1'
    import torch
    torch.set_num_threads(2)
    import spacy
    import bpc_hybrid.stage1_process as parser
    from bpc_hybrid.stage3_reproduction_repairs_v1 import convert_segmented,align_winter_model
    from bpc_hybrid.local_mpnet_backend_v1 import LocalMPNetBackend
    from bpc_hybrid.stage3_v2.semantic_matcher_v2 import SharedSemanticMatcherV2,normalize_text_v2
    from bpc_hybrid.stage3_v2.rule_order_adapter_v3 import SharedRuleOrderAdapterV3
    from bpc_hybrid.stage3_v2.checker_v2 import SharedStage3CheckerV2
    from bpc_hybrid.sun_stage3.sun_model import SunProcessModel
    from run_stage3_winter_paper_rerun_v1 import CachedNLP,validate_predictions
    from bpc_hybrid.winter_stage3.global_roles import collect_global_role_candidates
    from bpc_hybrid.winter_stage3.winter_clause import parse_regulation_paragraph
    from bpc_hybrid.winter_stage3.winter_model import parse_bpmn_file_winter,REACHABILITY_CORRECTED
    from bpc_hybrid.winter_stage3.winter_pair import WinterPair
    from bpc_hybrid.winter_stage3.winter_similarity import WinterSimilarity
    from bpc_hybrid.stage3_sun_style_checker import winter_signals
    contract=bind_structural_resources(parser,run.ROOT)
    nlp=spacy.load('en_core_web_sm')
    captured={}
    original_writer=run.write_new

    def capture(path,value):
        if Path(path).parent!=run.OUT or Path(path).name not in ('sun_repaired_records.json','sun_surgery_evidence.json'):
            raise RuntimeError('unexpected extraction output')
        captured[Path(path).name]=value

    run.write_new=capture
    original_id=run.RUN_ID
    run.RUN_ID=original_id+'_'+attempt_id
    try:
        repaired=run.make_sun_records()
    finally:
        run.write_new=original_writer
        run.RUN_ID=original_id
    for name,value in captured.items():
        if value!=run.read(run.OUT/name):
            raise RuntimeError('regenerated extraction drift: '+name)
    sources=run.read(run.INPUT/'regulation_sources.json')['rules']
    texts={r['rule_id']:r['text'] for r in sources}
    ours={r['requirement_id']:r['record'] for r in run.read(run.OUT/'ours_original_records.json')['records']}
    modeldir=run.ROOT.parent/'.tmp/hf_cache/hub/models--sentence-transformers--all-mpnet-base-v2/snapshots/e8c3b32edf5434bc2275fc9bab85f82640a19130'
    backend=LocalMPNetBackend(modeldir)
    if backend.identity()!=run.read(run.OUT/'sun_manifest.json')['details']['backend']:
        raise RuntimeError('encoder identity drift')
    matcher=SharedSemanticMatcherV2(backend)
    adapter=SharedRuleOrderAdapterV3(matcher)
    converted={m:{rid:convert_segmented(record,texts[rid],rid,nlp,adapter)
                  for rid,record in records.items()} for m,records in [('sun',repaired),('ours',ours)]}
    old_converted=run.read(run.OUT/'converted_records.json')
    for method,records in converted.items():
        for rid,record in records.items():
            for field in ('actions','actors','actor_action_pairs','order_relations','failed'):
                if record[field]!=old_converted[method][rid][field]:
                    raise RuntimeError('conversion drift: '+method+'/'+rid+'/'+field)
    checker=SharedStage3CheckerV2(matcher,nlp,**run.read(run.CONFIG)['sun_ours_thresholds'])
    view=run.read(run.INPUT/'inference_view.json')
    models={i['case_id']:SunProcessModel(i['process_id'],parser.parse_bpmn_file(run.ROOT/i['bpmn_path'],
        contract=contract),nlp) for i in view['items']}
    warm=set()
    for records in converted.values():
        for record in records.values():
            warm.update(record['actions']); warm.update(record['actors'])
    for model in models.values():
        warm.update(a['name'] for a in model.actions if a['name'])
        warm.update(model.actors); warm.update(b['object'] for b in model.business_objects)
    backend.embed(sorted({normalize_text_v2(checker.scorer._lemma(t)) for t in warm if t}))
    expected=run.read(run.OUT/'sun_ours_signals.json')['signals']
    # Persisted JSON arrays and in-memory tuple evidence have the same contract.
    probe_id='case_0f67bfdd277b'
    probe_target=next(t for t in run.read(run.OUT/'known_applicability.json')['targets'] if t['case_id']==probe_id)
    probe=checker.check_rule_record(converted['sun'][probe_target['requirement_id']],models[probe_id])
    run.write_new(result_path.with_name(result_path.stem+'_cache_diagnostic.json'),{
        'probe_case':probe_id,'conversion_and_detector_cache_shared':probe,
        'original_separate_detector_phase':expected['sun'][probe_id],
        'probe_in_memory_equality':probe==expected['sun'][probe_id],
        'probe_persisted_JSON_exact_equality':json_view(probe)==expected['sun'][probe_id],
        'resolution':'compare the exact persisted JSON representation; no float tolerance',
        'scoring_formula_thresholds_and_reference_unchanged':True})
    compared=0
    for target in run.read(run.OUT/'known_applicability.json')['targets']:
        cid,rid=target['case_id'],target['requirement_id']
        for method in converted:
            signals=json_view(checker.check_rule_record(converted[method][rid],models[cid]))
            if signals!=expected[method][cid]:
                raise RuntimeError('fresh detector signal drift: '+method+'/'+cid)
            compared+=3
    print('Fresh Sun/LLM-SE: all 690 type signals exactly match.',flush=True)
    cached=CachedNLP(nlp)
    lex=run.ROOT.parent/'references/winter_2020_model_check/model_check/input/files'
    stop,sw,seq=[set((lex/n).read_text(encoding='utf-8').splitlines())
                 for n in ('stopwords.txt','signalwords.txt','sequencemarkers.txt')]
    paragraphs={r['rule_id']:parse_regulation_paragraph(r['rule_id'],r['text'],cached,stop,sw,seq,
                                                      only_constraints=True) for r in sources}
    roles=set(collect_global_role_candidates(view,run.ROOT)['roles'])
    sim=WinterSimilarity(cached)
    rows=[]
    for item in sorted(view['items'],key=lambda r:r['case_id']):
        model=parse_bpmn_file_winter(run.ROOT/item['bpmn_path'],cached,stop,reachability_mode=REACHABILITY_CORRECTED)
        align_winter_model(model)
        for rid,paragraph in sorted(paragraphs.items()):
            pair=WinterPair(cached,sim,model,paragraph,roles,**run.read(run.CONFIG)['winter_thresholds'])
            rows.append({'case_id':item['case_id'],'rule_id':rid,
                'signals':winter_signals(pair=pair,model=model,paragraph=paragraph,resource_set=roles)})
    validate_predictions(rows,{(i['case_id'],r['rule_id']) for i in view['items'] for r in sources})
    if json_view(rows)!=run.read(run.OUT/'winter_predictions.json')['records']:
        raise RuntimeError('fresh native Winter predictions drift')
    report={'run_id':original_id+'_'+attempt_id,'status':'succeeded','scope':'development_reproducibility',
        'fresh_sun_from_cached_corenlp':True,'sun_repaired_records_exact':True,'sun_surgery_exact':True,
        'fresh_sun_ours_type_signals_exact':compared,'fresh_winter_pair_objects_exact':len(rows),
        'fresh_winter_type_signals_exact':len(rows)*3,'six_evaluation_objects_replayed':True,
        'llm_api_calls':0,'network_calls':0,'llm_extraction_reused':True,'fresh_classifier_inference':False,
        'complete_paper_reproduction_certified':False,'elapsed_seconds':time.perf_counter()-started,
        'config_sha256':run.sha(run.CONFIG),'source_manifest_sha256':run.sha(run.OUT/'manifest.json'),
        'replay_runner_sha256':run.sha(__file__),'git_commit':run.subprocess.check_output(
            ['git','rev-parse','HEAD'],cwd=run.ROOT,text=True).strip(),
        'command':'mpnet_venv/python -X utf8 replay_stage3_repair_v2.py --attempt-id '+attempt_id,
        'exact_persisted_JSON_comparison':True,'numeric_tolerance':0,
        'diagnostic_probe_JSON_exact':json_view(probe)==expected['sun'][probe_id]}
    run.write_new(result_path,report)
    print('Fresh Winter: all 3795 pair objects exactly match.',flush=True)
    print(str(result_path),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--attempt-id',required=True)
    args=parser.parse_args()
    if not args.attempt_id.replace('_','').isalnum():
        parser.error('attempt ID must be alphanumeric with underscores')
    replay(args.attempt_id)
