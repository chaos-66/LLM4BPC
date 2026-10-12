"""A scoped 3-method offline replay, not a full repository suite."""
import json
from pathlib import Path
import subprocess


ROOT=Path(__file__).resolve().parents[1]


def test_fresh_regeneration_and_both_native_detectors_reproduce_saved_objects():
    interpreter=ROOT.parent/'.tmp/mpnet_venv/Scripts/python.exe'
    assert interpreter.is_file(), 'configured existing MPNet runtime is required'
    command=[str(interpreter),'-X','utf8',str(ROOT/'scripts/replay_stage3_repair_v2.py'),
             '--attempt-id','actual_replay_v1']
    result=subprocess.run(command,cwd=ROOT.parent,capture_output=True,text=True,
                          encoding='utf-8',timeout=150)
    assert result.returncode==0, result.stdout+'\n'+result.stderr
    path=ROOT/'outputs/reports/stage3_reproduction_repair_20261012_v2_actual_replay_v1.json'
    report=json.loads(path.read_text(encoding='utf-8'))
    assert report['fresh_sun_ours_type_signals_exact']==690
    assert report['fresh_winter_pair_objects_exact']==3795
    assert report['fresh_winter_type_signals_exact']==11385
    assert report['sun_repaired_records_exact'] and report['sun_surgery_exact']
    assert report['llm_api_calls']==report['network_calls']==0
