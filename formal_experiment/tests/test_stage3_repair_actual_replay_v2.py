"""A scoped 3-method offline replay, not a full repository suite."""
import json
from pathlib import Path
import subprocess
import importlib.util
import hashlib


ROOT=Path(__file__).resolve().parents[1]


def test_fresh_regeneration_and_both_native_detectors_reproduce_saved_objects():
    path=ROOT/'outputs/reports/stage3_reproduction_repair_20261012_v2_actual_replay_v3.json'
    # Reuse this exact-state actual replay; an immutable evidence file must not
    # turn every later test invocation into an overwrite failure or duplicate run.
    if path.exists():
        report=json.loads(path.read_text(encoding='utf-8'))
        assert report['status']=='succeeded'
        assert report['replay_runner_sha256']==hashlib.sha256(
            (ROOT/'scripts/replay_stage3_repair_v2.py').read_bytes()).hexdigest()
        spec=importlib.util.spec_from_file_location('repair_exact_state',ROOT/'scripts/run_stage3_reproduction_repair_v2.py')
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.verify_preparation()
        assert report['source_manifest_sha256']==module.sha(module.OUT/'manifest.json')
        assert report['config_sha256']==module.sha(module.CONFIG)
    else:
        _run_actual_replay()
        report=json.loads(path.read_text(encoding='utf-8'))
    assert report['fresh_sun_ours_type_signals_exact']==690
    assert report['fresh_winter_pair_objects_exact']==3795
    assert report['fresh_winter_type_signals_exact']==11385
    assert report['sun_repaired_records_exact'] and report['sun_surgery_exact']
    assert report['llm_api_calls']==report['network_calls']==0


def _run_actual_replay():
    interpreter=ROOT.parent/'.tmp/mpnet_venv/Scripts/python.exe'
    assert interpreter.is_file(), 'configured existing MPNet runtime is required'
    command=[str(interpreter),'-X','utf8',str(ROOT/'scripts/replay_stage3_repair_v2.py'),
             '--attempt-id','actual_replay_v3']
    result=subprocess.run(command,cwd=ROOT.parent,capture_output=True,text=True,
                          encoding='utf-8',timeout=150)
    assert result.returncode==0, result.stdout+'\n'+result.stderr


def test_json_comparison_preserves_values_and_order_without_float_tolerance():
    spec=importlib.util.spec_from_file_location('replay_json_view',ROOT/'scripts/replay_stage3_repair_v2.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.json_view({'constraint':('a','b'),'score':0.4})=={'constraint':['a','b'],'score':0.4}
    assert module.json_view({'constraint':('b','a'),'score':0.4})!={'constraint':['a','b'],'score':0.4}
    assert module.json_view({'score':0.400000001})!={'score':0.4}
