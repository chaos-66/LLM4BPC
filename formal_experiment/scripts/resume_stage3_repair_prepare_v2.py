"""Resume only the interrupted metadata tail of v2 prepare, never rewrite it.

Invoke with Python -X utf8: Git status emits UTF-8 while Windows Python's
legacy text decoding is GBK. All frozen inputs and code must still match.
"""
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

sys.dont_write_bytecode=True


def resume(module):
    started=time.perf_counter()
    prep=module.read(module.OUT/'preparation.json')
    for relative,digest in prep['bindings'].items():
        if module.sha(module.ROOT/relative)!=digest:
            raise RuntimeError('frozen preparation drift: '+relative)
    expected=['prepare_manifest.json','parse_manifest.json','winter_manifest.json',
              'corenlp_annotations.json','corenlp_scope_observations.json','winter_predictions.json',
              'phase_reuse_bindings.json']
    if any((module.OUT/name).exists() for name in expected):
        raise RuntimeError('resume tail already exists; never overwrite')
    previous=module.ROOT/'outputs/evidence/stage3_reproduction_repair_20261012_v1'
    manifests={phase:module.read(previous/f'{phase}_manifest.json') for phase in ('parse','winter')}
    for phase in manifests:
        if manifests[phase]['status']!='succeeded':
            raise RuntimeError('incomplete prior phase: '+phase)
    for name in expected[3:6]:
        shutil.copyfile(previous/name,module.OUT/name)
    if module.sha(module.OUT/'corenlp_annotations.json')!=manifests['parse']['details']['annotation_sha256']:
        raise RuntimeError('annotation hash drift')
    if module.sha(module.OUT/'winter_predictions.json')!=manifests['winter']['details']['predictions_sha256']:
        raise RuntimeError('prediction hash drift')
    module.write_new(module.OUT/'phase_reuse_bindings.json',{
        'bindings':{str((module.OUT/n).relative_to(module.ROOT).as_posix()):module.sha(module.OUT/n)
                    for n in expected[3:6]},
        'source_parse_manifest_sha256':module.sha(previous/'parse_manifest.json'),
        'source_winter_manifest_sha256':module.sha(previous/'winter_manifest.json')})
    module.record_phase('prepare',started,{'cases':115,'rules':33,
        'resumed_metadata_only_after_GBK_Git_status_decode_failure':True,
        'frozen_preparation_sha256':module.sha(module.OUT/'preparation.json'),
        'resume_runner_sha256':module.sha(__file__),
        'command':'python -X utf8 formal_experiment/scripts/resume_stage3_repair_prepare_v2.py'})
    for phase in ('parse','winter'):
        module.record_phase(phase,started,{'reused_completed_offline_phase':True,
            'source_run':'stage3_reproduction_repair_20261012_v1',
            'source_manifest_sha256':module.sha(previous/f'{phase}_manifest.json'),
            'source_details':manifests[phase]['details']})
    module.verify_preparation()
    print('Preparation resumed: hashes unchanged, parse33 and Winter3795 bound.',flush=True)


if __name__=='__main__':
    import run_stage3_reproduction_repair_v2 as module
    resume(module)
