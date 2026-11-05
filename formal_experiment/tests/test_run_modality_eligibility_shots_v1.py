import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_sun_modality_eligibility_shots_v1 as run


@pytest.mark.parametrize("key,value", [
    ("cap_cny", 21), ("off_peak_only", False), ("max_calls", 427), ("retries", 1),
    ("endpoint", "https://somewhere.invalid"), ("execute_authorized", False),
])
def test_scope_cannot_expand(key, value):
    auth = run.read(run.AUTH)
    auth[key] = value
    with pytest.raises(ValueError):
        run.check_limits(auth)


@pytest.mark.skipif(not run.PLAN.exists(), reason="local preflight required")
def test_actual_engine_passes_single_frozen_arm_to_coordinator(monkeypatch):
    # Exercise the ordinary execute entry without transport. A mock coordinator
    # checks the actual bodies it would receive against immutable request hashes.
    from types import SimpleNamespace
    def loader(engine):
        engine.send_one = lambda *args: pytest.fail("unexpected transport")
        def inspect():
            payload = engine.plan_payload()
            pairs = engine.data.load_split_text_only("test")
            assert len(pairs) == 426
            assert engine.JOURNAL == run.JOURNAL
            for (sid, text), binding in zip(pairs, payload["requests"], strict=True):
                body = engine.fewshot.request_body(sid, text, block="")
                assert run.boundary.digest(run.boundary.wire_bytes(body)) == binding["fewshot_request_sha256"]
                assert run.boundary.digest(body["messages"][0]["content"].encode()) == payload["system_sha256"]
        engine.execute = inspect
    spec = SimpleNamespace(loader=SimpleNamespace(exec_module=loader))
    monkeypatch.setattr(run.importlib.util, "spec_from_file_location", lambda *a: spec)
    monkeypatch.setattr(run.importlib.util, "module_from_spec", lambda s: SimpleNamespace())
    run.execute()
