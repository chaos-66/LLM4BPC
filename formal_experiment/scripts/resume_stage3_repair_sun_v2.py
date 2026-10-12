"""Resume v2 Sun after snapshot-relative schema lookup failed.

Only configure the frozen structural parser's resource root. Its schema hash,
contract and input validation remain enforced. --fresh supports a fresh Sun
phase; default resumes the existing extraction/conversion/equivalence files.
"""
from __future__ import annotations

import os
import sys
import time

sys.dont_write_bytecode=True


def bind_structural_resources(parser, root):
    parser.ROOT=root
    return parser.load_stage1_contract(root/'configs/stage1_structural_s11_s14.json')


def main(fresh=False):
    import run_stage3_reproduction_repair_v2 as run
    run.verify_preparation()
    run.activate_snapshot()
    import bpc_hybrid.stage1_process as parser
    contract=bind_structural_resources(parser,run.ROOT)
    if fresh:
        run.sun()
        return
    if (run.OUT/'sun_manifest.json').exists():
        raise FileExistsError('Sun phase already complete')
    started=time.perf_counter()
    equivalence=run.read(run.OUT/'encoder_equivalence.json')
    if not equivalence['passed'] or equivalence['pair_count']!=50:
        raise RuntimeError('encoder equivalence not passed')
    prior_names=['sun_repaired_records.json','sun_surgery_evidence.json',
                 'converted_records.json','encoder_equivalence.json']
    run.write_new(run.OUT/'sun_resume_bindings.json',{
        'bindings':{n:run.sha(run.OUT/n) for n in prior_names},
        'resume_runner_sha256':run.sha(__file__),
        'structural_schema_sha256':contract['process_record_schema']['sha256'],
        'interrupted_at':'schema lookup under moved source_snapshot root',
        'resource_root_relocated_only':True,'schema_checks_retained':True,
        'command':'mpnet_venv/python -X utf8 resume_stage3_repair_sun_v2.py'})
    os.environ['HF_HUB_OFFLINE']='1'
    os.environ['TRANSFORMERS_OFFLINE']='1'
    import torch
    torch.set_num_threads(2)
    import spacy
    from bpc_hybrid.local_mpnet_backend_v1 import LocalMPNetBackend
    from bpc_hybrid.stage3_v2.semantic_matcher_v2 import SharedSemanticMatcherV2,normalize_text_v2
    from bpc_hybrid.stage3_v2.checker_v2 import SharedStage3CheckerV2
    from bpc_hybrid.sun_stage3.sun_model import SunProcessModel
    nlp=spacy.load('en_core_web_sm')
    modeldir=run.ROOT.parent/'.tmp/hf_cache/hub/models--sentence-transformers--all-mpnet-base-v2/snapshots/e8c3b32edf5434bc2275fc9bab85f82640a19130'
    backend=LocalMPNetBackend(modeldir)
    matcher=SharedSemanticMatcherV2(backend)
    converted=run.read(run.OUT/'converted_records.json')
    originals={r['requirement_id']:r['record'] for r in run.read(run.OUT/'ours_original_records.json')['records']}
    old=run.read(run.ROOT/'outputs/evidence/stage3_gamma_theta_sensitivity_20261010_v1/converted_records.json')['ours']
    for rid in originals:
        for field in ('actions','actors','actor_action_pairs','order_relations','failed'):
            if converted['ours'][rid][field]!=old[rid][field]:
                raise RuntimeError('LLM conversion drift: '+rid+'/'+field)
    checker=SharedStage3CheckerV2(matcher,nlp,**run.read(run.CONFIG)['sun_ours_thresholds'])
    targets=run.read(run.OUT/'known_applicability.json')['targets']
    view={r['case_id']:r for r in run.read(run.INPUT/'inference_view.json')['items']}
    models={cid:SunProcessModel(item['process_id'],parser.parse_bpmn_file(run.ROOT/item['bpmn_path'],
        contract=contract),nlp) for cid,item in view.items()}
    # Warm only texts that the frozen scorer will compare, using the same lemma
    # transform. Batch padding is masked and does not affect the pooled vector.
    texts=set()
    for records in converted.values():
        for record in records.values():
            texts.update(record['actions']); texts.update(record['actors'])
    for model in models.values():
        texts.update(a['name'] for a in model.actions if a['name'])
        texts.update(model.actors)
        texts.update(b['object'] for b in model.business_objects)
    lemma=lambda t:normalize_text_v2(checker.scorer._lemma(t))
    backend.embed(sorted({lemma(t) for t in texts if t}))
    signals={m:{} for m in converted}
    for index,target in enumerate(targets,1):
        cid,rid=target['case_id'],target['requirement_id']
        for method in converted:
            signals[method][cid]=checker.check_rule_record(converted[method][rid],models[cid])
        if index%20==0:
            print(f'Sun/LLM-SE checking: {index}/{len(targets)}',flush=True)
    run.write_new(run.OUT/'sun_ours_signals.json',{'signals':signals})
    run.record_phase('sun',started,{'cases':len(targets),'rules':33,
        'LLM_conversion_substantive_equality':True,'encoder_equivalence_pairs':50,
        'backend':backend.identity(),'spacy_version':spacy.__version__,
        'nlp_model_version':nlp.meta['version'],'signals_sha256':run.sha(run.OUT/'sun_ours_signals.json'),
        'resume_runner_sha256':run.sha(__file__),'schema_checks_retained':True,
        'resource_root_relocated_only':True})
    print('Sun/LLM-SE inference complete; inputs, parameters and evaluator unchanged.',flush=True)


if __name__=='__main__':
    if sys.argv[1:] not in ([],['--fresh']):
        raise SystemExit('optional --fresh only')
    main(fresh=sys.argv[1:]==['--fresh'])
