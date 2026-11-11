"""Exercise the paid rerun's real request builder, parsers and restart boundaries offline."""
import io
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "scripts"))
import run_paper_e1_r19_v1 as run
from bpc_hybrid.modality_benchmark import data
from score_paper_e1_r19_v1 import german_metrics, population


def test_exact_plan_and_offline_wire(monkeypatch):
    pre = run.pre
    plan, pairs, bodies, controls = pre.build()
    assert plan == pre.read(pre.REPORT)
    original = (pre.ROOT / "outputs/development/sun_modality_es_minimal_v1/E1_system_prompt.txt").read_text(encoding="utf-8")
    new_system = bodies["estg","111",pairs["estg"][0][0]]["messages"][0]["content"]
    assert len(new_system.splitlines()) == len(original.splitlines())
    assert [a.split(".")[0] for a,b in zip(original.splitlines(),new_system.splitlines()) if a!=b] == ["19"]
    assert {k[1] for k in controls} == {"000","001"} and len(controls)==300
    groups = {k[:2] for k in bodies.keys() - controls.keys()}
    assert len(groups) == 8 and len(bodies) == 1659
    monkeypatch.setenv("DEEPSEEK_API_KEY","offline-test-placeholder")
    config = run.transport.base.environment_config()
    captured = []
    for group,arm in sorted(groups):
        sid, source = pairs[group][0]
        def local_response(request, timeout):
            captured.append(request.data)
            assert timeout == 180 and request.full_url == "https://api.deepseek.com/chat/completions"
            content = json.dumps({"sample_id":sid,"source_id":sid,"clauses":[{"modality":{"label":"definition"}}]})
            response = io.BytesIO(json.dumps({"model":"deepseek-v4-pro","choices":[{"message":{"content":content},
                    "finish_reason":"stop"}],"usage":{"prompt_tokens":20,"completion_tokens":10}}).encode())
            response.headers = {"Content-Type":"application/json"}
            response.status = 200
            return response
        monkeypatch.setattr(urllib.request,"urlopen",local_response)
        body = bodies[group,arm,sid]
        wire = pre.boundary.wire_bytes(body)
        r = run.transport.send_one(config,sid,source,body,pre.digest(wire),pre.llm_se.PRICE_CNY_PER_MILLION["off_peak"])
        assert captured[-1] == wire and not run.transport.failed(r)
        assert r["cost_cny"] <= pre.boundary.reserve_cost(body,pre.llm_se.PRICE_CNY_PER_MILLION["off_peak"])
        assert r["label"] == "definition"
    assert len(captured) == 8
    texts = dict(pairs["gdpr"])
    for line in pre.GDPR_IDS.read_text(encoding="utf-8-sig").splitlines():
        native = json.loads(line)["record"]
        sid = native["sample_id"]
        # Nine stored canonical records omit their source text. Reconstruct the
        # required wire envelope for this fixture only, using the frozen input.
        fixture = dict(native)
        fixture.setdefault("source_text",texts[sid])
        replay = run.canonical(("gdpr","111",sid),texts[sid],
                               {"raw_content":json.dumps(fixture),"request_sha256":"offline"})
        assert replay["request_status"] == "ok" and replay["record"]["sample_id"] == sid


def test_resume_rejects_uncertain_duplicate_or_tampered_events(tmp_path):
    journal = tmp_path / "events"
    key = ("german","111","id")
    start = {"kind":"started","sample_id":run.keystr(key),"request_sha256":"r"}
    first = run.pre.boundary.append_event(journal,start,"")
    with pytest.raises(ValueError,match="without a verified completion"):
        run.check_history(run.pre.boundary.read_events(journal),{key}, {},{key:"r"})
    run.pre.boundary.append_event(journal,start,first)
    with pytest.raises(ValueError,match="duplicate"):
        run.pre.boundary.read_events(journal)
    journal.write_bytes(journal.read_bytes().replace(b"started", b"altered"))
    with pytest.raises(ValueError,match="hash chain"):
        run.pre.boundary.read_events(journal)


def test_cost_and_window_boundaries():
    assert run.budget_allows(5.25,.75,6)
    for args in ((5.25,.8,6),(0,1,float("nan")),(0,1,float("inf")),(-1,1,6)):
        assert not run.budget_allows(*args)
    tz = run.pre.llm_se.BEIJING
    assert run.safe_window(datetime(2026,11,12,8,55,tzinfo=tz))
    assert not run.safe_window(datetime(2026,11,12,8,56,tzinfo=tz))
    assert not run.safe_window(datetime(2026,11,12,14,15,tzinfo=tz))
    assert run.safe_window(datetime(2026,11,12,18,0,tzinfo=tz))


def test_modality_readout_keeps_invalid_evidence_and_all_samples():
    key = ("german","111","a")
    clauses = [{"modality":{"label":None}},{"modality":{"label":"prohibition","evidence":[{"start":999}]}},
               {"modality":{"label":"permission"}}]
    assert run.canonical(key,"",{"raw_content":json.dumps({"clauses":clauses})}) == {"label":"prohibition"}
    gold = dict(zip("abcd",data.LABELS))
    labels = dict(gold,a=None)
    result = german_metrics(labels,gold,{"d"})
    assert result["primary_426"]["n"] == 4 and result["primary_426"]["missing"] == 1
    assert result["primary_426"]["per_class"][gold["a"]]["fn"] == 1
    with pytest.raises(ValueError,match="duplicate"):
        population([{"sample_id":"a"},{"sample_id":"a"}],{"a","b"})
