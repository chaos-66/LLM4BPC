"""Check reuse and retry boundaries of the E1 continuation without transport."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_sun_modality_e1_full_v1 as run


@pytest.mark.skipif(not run.control.JOURNAL.exists(), reason="requires local frozen journals")
def test_five_e1_responses_partition_the_full_test():
    plan, pairs, _, hashes, remaining, reused, old = run.build()
    assert plan == run.prepared.read(run.PLAN)
    assert set(remaining).isdisjoint(reused)
    assert set(remaining) | set(reused) == set(pairs) == set(old)
    assert len(remaining) == 421 and len(reused) == 5
    assert all(row["wave"].startswith("E1-") and row["request_sha256"] == hashes[sid]
               for sid, row in reused.items())


def test_unsettled_request_cannot_be_resent(tmp_path, monkeypatch):
    path = tmp_path / "events.jsonl"
    monkeypatch.setattr(run, "JOURNAL", path)
    run.boundary.append_event(path, {"kind": "started", "sample_id": "one", "request_sha256": "hash"}, "")
    with pytest.raises(ValueError, match="unsettled"):
        run.checked_history(["one"], {"one": "hash"})
    with pytest.raises(ValueError, match="does not match"):
        run.checked_history(["two"], {"two": "hash"})
