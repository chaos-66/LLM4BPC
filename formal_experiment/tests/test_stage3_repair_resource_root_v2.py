from pathlib import Path
import importlib.util,json

import pytest
from bpc_hybrid import stage1_process


ROOT=Path(__file__).resolve().parents[1]

def load():
    path=ROOT/'scripts/resume_stage3_repair_sun_v2.py'
    spec=importlib.util.spec_from_file_location('resource_root_test',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_relocated_snapshot_resources_keep_frozen_schema_check(tmp_path,monkeypatch):
    monkeypatch.setattr(stage1_process,'ROOT',tmp_path)
    with pytest.raises(stage1_process.Stage1ProcessError,match='schema binding'):
        stage1_process.load_stage1_contract(ROOT/'configs/stage1_structural_s11_s14.json')
    contract=load().bind_structural_resources(stage1_process,ROOT)
    assert contract['process_record_schema']['schema_version']==stage1_process.SCHEMA_VERSION


def test_relocation_does_not_accept_wrong_schema_hash(tmp_path,monkeypatch):
    monkeypatch.setattr(stage1_process,'ROOT',ROOT)
    contract=json.loads((ROOT/'configs/stage1_structural_s11_s14.json').read_text(encoding='utf-8'))
    contract['process_record_schema']['path']=str(ROOT/contract['process_record_schema']['path'])
    contract['process_record_schema']['sha256']='0'*64
    (tmp_path/'configs').mkdir()
    (tmp_path/'configs/stage1_structural_s11_s14.json').write_text(json.dumps(contract),encoding='utf-8')
    with pytest.raises(stage1_process.Stage1ProcessError,match='schema binding'):
        load().bind_structural_resources(stage1_process,tmp_path)
