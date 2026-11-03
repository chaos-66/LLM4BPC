"""Synthetic offline validation for paired scheduling, authorization and reports."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from bpc_hybrid.modality_benchmark import boundary, data, fewshot


def module(name):
    spec = importlib.util.spec_from_file_location(name + "_test", ROOT / "scripts" / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def test_schedule_covers_every_test_and_dev_sample_with_balanced_pair_order():
    m = module("prepare_sun_modality_validation_v1")
    test, dev = [("t", "Test sentence.")], [("b", "Second dev sentence."), ("a", "First dev sentence.")]
    result = m.schedule(test, dev)
    assert [(s, a, i) for s, a, i, _ in result] == [
        ("test", "review", "t"), ("dev", "fewshot", "a"), ("dev", "review", "a"),
        ("dev", "review", "b"), ("dev", "fewshot", "b")]
    assert m.schedule(test, dev[::-1]) == result


@pytest.mark.parametrize("dev", [[("t", "Distinct sentence.")], [("d", " TEST SENTENCE. ")]])
def test_overlap_stops_validation(dev):
    m = module("prepare_sun_modality_validation_v1")
    with pytest.raises(ValueError, match="overlap"):
        m.schedule([("t", "Test sentence.")], dev)


def authorization_fixture():
    limits = {"max_calls": 3, "cap_cny": 60.0, "max_workers": 8, "retries": 0,
              "off_peak_only": True, "endpoint": "https://api.deepseek.com", "model": "deepseek-v4-pro"}
    plan = {"suite_id": "synthetic", "contract": {"requested_limits": limits}, "requests": [1, 2, 3]}
    auth = {**limits, "suite_id": "synthetic", "execute_authorized": True,
            "user_text": "Synthetic authorization fixture; never used for execution", "approved_preflight_sha256": "bound"}
    return plan, auth


def test_matching_authorization_is_accepted():
    m = module("run_sun_modality_validation_v1")
    plan, auth = authorization_fixture()
    m.verify_authorization(auth, plan, "bound")


@pytest.mark.parametrize("key,value", [("execute_authorized", False), ("approved_preflight_sha256", "stale"),
    ("max_calls", 4), ("cap_cny", 61), ("retries", 1), ("off_peak_only", False),
    ("endpoint", "https://example.invalid"), ("user_text", "")])
def test_stale_missing_or_expanded_authorization_is_rejected(key, value):
    m = module("run_sun_modality_validation_v1")
    plan, auth = authorization_fixture()
    auth[key] = value
    with pytest.raises(ValueError):
        m.verify_authorization(auth, plan, "bound")


def test_adapter_keeps_pair_requests_separate_and_does_not_patch_shared_modules(tmp_path, monkeypatch):
    m = module("run_sun_modality_validation_v1")
    old_body = fewshot.request_body
    monkeypatch.setattr(m.fewshot, "load_demonstrations", lambda: ("Synthetic demonstrations", {}))
    monkeypatch.setattr(m.data, "load_split_text_only", lambda split: [("s", "Synthetic source.")])
    def no_labels(*args):
        pytest.fail("execution adapter must never read labels")
    monkeypatch.setattr(m.data, "load_split", no_labels)
    def body_for(arm, sid, text, block):
        return {"model": "synthetic", "max_tokens": 4096, "messages": [{"role": "system", "content": arm},
                                                    {"role": "user", "content": sid + text}]}
    monkeypatch.setattr(m.prepared, "body_for", body_for)
    preflight = tmp_path / "preflight.json"
    preflight.write_text("{}")
    monkeypatch.setattr(m.prepared, "REPORT", preflight)
    rows = [{"call_id": "dev:" + arm + ":s", "sample_id": "s", "split": "dev", "arm": arm,
             "request_sha256": boundary.digest(boundary.wire_bytes(body_for(arm, "s", "Synthetic source.", "")))}
            for arm in ("fewshot", "review")]
    current_text_loader = data.load_split_text_only
    auth = {"max_calls": 2, "cap_cny": 60, "max_workers": 2,
            "price_cny_per_million": {"off_peak": {"input_cache_miss": 4.5, "output": 13.5}}}
    engine, payload = m.make_engine({"requests": rows}, auth, "synthetic-auth")
    assert data.load_split_text_only is current_text_loader and fewshot.request_body is old_body
    assert len(set(r["sample_id"] for r in payload["requests"])) == 2
    for row in rows:
        body = engine.fewshot.request_body(row["call_id"], "Synthetic source.", block="Synthetic demonstrations")
        assert body["messages"][0]["content"] == row["arm"]
        assert body["messages"][1]["content"].startswith("s")
    with pytest.raises(ValueError, match="text mismatch"):
        engine.fewshot.request_body(rows[0]["call_id"], "Altered sentence.", block="")
    engine.RUN, engine.JOURNAL, engine.PLAN = tmp_path, tmp_path / "local/events.jsonl", tmp_path / "execution.json"
    engine.PLAN.write_text(json.dumps({"payload": payload}))
    monkeypatch.setattr(engine.base, "environment_config", lambda: None)
    monkeypatch.setattr(engine.llm_se, "rate_for", lambda _: ("off_peak", {}))
    sent = []
    def fake_send(config, call_id, text, body, request_hash, rate):
        sent.append(call_id)
        return {"kind": "finished", "sample_id": call_id, "request_sha256": request_hash,
                "request_status": "ok", "usage_verified": True, "model_accepted": True,
                "body_hash_match": True, "parse_status": "ok", "cost_cny": .001}
    monkeypatch.setattr(engine, "send_one", fake_send)
    engine.execute()
    engine.execute()
    assert set(sent) == {r["call_id"] for r in rows} and len(sent) == 2
    assert boundary.accounting(boundary.read_events(engine.JOURNAL))[1:] == (pytest.approx(.002), 0)


def test_paired_report_keeps_regressions_and_parse_failures_in_denominator(monkeypatch):
    m = module("build_sun_modality_validation_report_v1")
    original_bootstrap = m.stats.bootstrap_delta
    monkeypatch.setattr(m.stats, "bootstrap_delta", lambda g, a, b: original_bootstrap(g, a, b, repeats=20))
    labels = ["definition", "obligation", "permission", "prohibition"]
    result = m.compare(["a", "b", "c", "d"], labels,
                       ["obligation", "obligation", "permission", "definition"],
                       ["definition", None, "permission", "definition"])
    assert result["paired"]["corrected"] == 1 and result["paired"]["regressed"] == 1
    assert result["old_errors"] == result["old_correct"] == 2
    assert result["review"]["accuracy"] == .5
    assert result["per_class_f1_delta"]["obligation"] < 0
    assert "all 4 samples" in result["bootstrap"]["method"]
    assert result["changed_predictions"][1]["review"] is None


def test_paired_report_rejects_missing_population():
    m = module("build_sun_modality_validation_report_v1")
    with pytest.raises(ValueError, match="population mismatch"):
        m.compare(["s"], ["definition"], [], ["definition"])


def test_incomplete_journal_blocks_final_report_before_label_access(tmp_path, monkeypatch):
    m = module("build_sun_modality_validation_report_v1")
    plan, auth = authorization_fixture()
    plan["requests"] = [{"call_id": "dev:review:s", "request_sha256": "hash"}]
    plan["contract"]["requested_limits"]["max_calls"] = auth["max_calls"] = 1
    preflight = tmp_path / "preflight.json"; preflight.write_text("{}")
    monkeypatch.setattr(m.prepared, "REPORT", preflight)
    auth["approved_preflight_sha256"] = boundary.digest(preflight.read_bytes())
    auth_path = tmp_path / "auth.json"; auth_path.write_text(json.dumps(auth))
    requests = [{"sample_id": "dev:review:s", "fewshot_request_sha256": "hash"}]
    execution = {"payload": {"authorization": auth, "authorization_sha256": boundary.digest(auth_path.read_bytes()),
        "validation_preflight_sha256": auth["approved_preflight_sha256"], "requests": requests}}
    execution_path = tmp_path / "execution.json"; execution_path.write_text(json.dumps(execution))
    monkeypatch.setattr(m, "REPORT", tmp_path / "result")
    monkeypatch.setattr(m.prepared, "verify_frozen", lambda: plan)
    monkeypatch.setattr(m.runner, "EXECUTION_PLAN", execution_path)
    monkeypatch.setattr(m.runner, "JOURNAL", tmp_path / "missing_journal")
    def no_labels(*args):
        pytest.fail("incomplete batch must not read evaluation labels")
    monkeypatch.setattr(m.data, "load_split", no_labels)
    with pytest.raises(ValueError, match="batch incomplete"):
        m.main(auth_path)
