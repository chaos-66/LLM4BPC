"""Focused safety and one-factor checks; fake transport only, no API/.env."""
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bpc_hybrid.modality_benchmark import boundary, llm_se


def runner():
    spec = importlib.util.spec_from_file_location("boundary_runner_test", ROOT / "scripts/run_sun_modality_boundary_v1.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_branch_changes_only_system_guidance():
    before = llm_se.request_body("synthetic", "A member may submit a form.")
    after = boundary.request_body("synthetic", "A member may submit a form.")
    addition = after["messages"][0]["content"][len(before["messages"][0]["content"]):]
    assert addition == "\n\n" + boundary.GUIDANCE.read_text(encoding="utf-8").strip()
    after["messages"][0]["content"] = before["messages"][0]["content"]
    assert before == after


def test_guidance_drift_fails_before_render(tmp_path, monkeypatch):
    wrong = tmp_path / "guidance.md"
    wrong.write_text("changed", encoding="utf-8")
    monkeypatch.setattr(boundary, "GUIDANCE", wrong)
    with pytest.raises(ValueError, match="changed after freeze"):
        boundary.request_body("s", "text")


def test_wire_matches_real_builder_without_sending():
    from bpc_hybrid.llm_client import OpenAICompatibleRequestBuilder
    from bpc_hybrid.llm_config import LLMConfig
    from bpc_hybrid.h1_transport import H1RequestPolicy
    body = boundary.request_body("s", "Synthetic text.")
    config = LLMConfig(enabled=True, provider="openai_compatible", model=llm_se.MODEL_ALIAS,
                       api_key="synthetic-test-key", base_url="https://api.deepseek.com",
                       temperature=0.0, top_p=1.0, max_tokens=4096)
    built = OpenAICompatibleRequestBuilder(config).build_payload(
        system_prompt=body["messages"][0]["content"], user_prompt=body["messages"][1]["content"])["body"]
    built = H1RequestPolicy(response_format=None).apply_to_body(built)
    assert boundary.wire_bytes(body) == json.dumps(built).encode()


def test_reservation_covers_full_completion_and_uncached_input():
    body = boundary.request_body("s", "Synthetic text.")
    rate = llm_se.PRICE_CNY_PER_MILLION["off_peak"]
    maximum = llm_se.cost_cny({"prompt_tokens": len(boundary.wire_bytes(body)),
                             "completion_tokens": 4096}, rate)
    assert boundary.reserve_cost(body, rate) > maximum


def test_chain_tampering_detected(tmp_path):
    path = tmp_path / "events.jsonl"
    boundary.append_event(path, {"kind": "started", "sample_id": "s", "reserved_cny": 0.2}, "")
    path.write_text(path.read_text().replace('"s"', '"changed"'))
    with pytest.raises(ValueError, match="hash chain"):
        boundary.read_events(path)


def test_unfinished_request_retains_budget_and_no_retry_identity(tmp_path):
    path = tmp_path / "events.jsonl"
    boundary.append_event(path, {"kind": "started", "sample_id": "s", "reserved_cny": 0.2}, "")
    ids, spent, reserved = boundary.accounting(boundary.read_events(path))
    assert (ids, spent, reserved) == ({"s"}, 0, 0.2)


@pytest.fixture
def fake_execution(tmp_path, monkeypatch):
    from bpc_hybrid import llm_client
    module = runner()
    run = tmp_path / "run"
    run.mkdir()
    body = boundary.request_body("s", "Synthetic text.")
    contract = {"authorization": {"execute_requested": True}, "max_calls": 1, "cap_cny": 20,
                "price_cny_per_million": llm_se.PRICE_CNY_PER_MILLION}
    payload = {"contract": contract, "requests": [{"sample_id": "s", "request_sha256": boundary.digest(boundary.wire_bytes(body))}]}
    plan = run / "preflight.json"
    plan.write_text(json.dumps({"payload": payload}), encoding="utf-8")
    monkeypatch.setattr(module, "RUN", run)
    monkeypatch.setattr(module, "PLAN", plan)
    monkeypatch.setattr(module, "JOURNAL", run / "local_only/events.jsonl")
    monkeypatch.setattr(module, "plan_payload", lambda: payload)
    monkeypatch.setattr(module, "environment_config", lambda: None)
    monkeypatch.setattr(module.data, "load_split_text_only", lambda _: [("s", "Synthetic text.")])
    monkeypatch.setattr(module.llm_se, "rate_for", lambda _: ("off_peak", llm_se.PRICE_CNY_PER_MILLION["off_peak"]))
    sends = []
    class Fake:
        def __init__(self, *args, **kwargs):
            self.last_decode = {"model": "deepseek-v4-pro", "usage": {"prompt_tokens": 100, "completion_tokens": 30}}
            self.last_request_body_sha256 = boundary.digest(boundary.wire_bytes(body))
        def send(self, request):
            sends.append(request.source_id)
            return SimpleNamespace(content=json.dumps({"clauses": [{"modality": {"label": "permission"}}]}))
    monkeypatch.setattr(llm_client, "RealAPITransport", Fake)
    return module, payload, sends, Fake


def test_execution_persists_raw_and_resume_never_resends(fake_execution):
    module, _, sends, _ = fake_execution
    module.execute()
    module.execute()
    events = boundary.read_events(module.JOURNAL)
    assert sends == ["s"]
    assert len(events) == 2
    assert events[-1]["label"] == "permission"
    assert json.loads(events[-1]["raw_content"])["clauses"]
    assert events[-1]["body_hash_match"]


def test_budget_refusal_happens_before_send(fake_execution):
    module, payload, sends, _ = fake_execution
    payload["contract"]["cap_cny"] = 0.00001
    module.PLAN.write_text(json.dumps({"payload": payload}), encoding="utf-8")
    module.execute()
    assert sends == []
    assert not module.JOURNAL.exists()


def test_wrong_model_records_failure_and_stops(fake_execution):
    module, _, sends, fake = fake_execution
    original = fake.send
    def wrong(self, request):
        response = original(self, request)
        self.last_decode["model"] = "different-model"
        return response
    fake.send = wrong
    module.execute()
    events = boundary.read_events(module.JOURNAL)
    assert sends == ["s"]
    assert events[-1]["label"] is None
    assert not events[-1]["model_accepted"]


def test_environment_config_never_loads_dotenv(monkeypatch):
    from bpc_hybrid import llm_config
    def forbidden(*args, **kwargs):
        pytest.fail(".env must never be loaded")
    monkeypatch.setattr(llm_config, "load_project_env_file", forbidden)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "synthetic-test-key")
    config = runner().environment_config()
    assert config.model == "deepseek-v4-pro"
    assert config.base_url == "https://api.deepseek.com"
