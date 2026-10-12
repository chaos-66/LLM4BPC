from types import SimpleNamespace
from pathlib import Path
import importlib.util

import pytest

def load():
    path=Path(__file__).resolve().parents[1]/'scripts/resume_stage3_repair_prepare_v2.py'
    spec=importlib.util.spec_from_file_location('repair_resume_test',path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_resume_rejects_frozen_input_drift_before_writes(tmp_path):
    module=SimpleNamespace(OUT=tmp_path,ROOT=tmp_path,
        read=lambda p:{'bindings':{'rule.json':'fixed'}},sha=lambda p:'changed')
    with pytest.raises(RuntimeError,match='drift'):
        load().resume(module)
    assert not list(tmp_path.iterdir())


def test_resume_rejects_existing_phase_without_overwrite(tmp_path):
    path=tmp_path/'prepare_manifest.json'
    path.write_text('original',encoding='utf-8')
    module=SimpleNamespace(OUT=tmp_path,ROOT=tmp_path,read=lambda p:{'bindings':{}})
    with pytest.raises(RuntimeError,match='never overwrite'):
        load().resume(module)
    assert path.read_text(encoding='utf-8')=='original'
