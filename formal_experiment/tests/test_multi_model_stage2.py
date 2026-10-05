"""Offline authorization, persistence and provider-contract counterexamples.

Every credential fixture lives under tmp_path; real dotenv and HTTP are forbidden.
"""

import copy
import io
import json
import shutil
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from bpc_hybrid import multi_model_stage2 as m
from bpc_hybrid import prompt_loader
import stage2_multi_model as cli


@pytest.fixture(autouse=True)
def no_live_access(monkeypatch):
    original = Path.open

    def guarded_open(path, *args, **kwargs):
        if path.resolve() == (m.ROOT / ".env").resolve():
            pytest.fail("The real .env must not be opened by tests")
        return original(path, *args, **kwargs)

    def forbidden(*args, **kwargs):
        pytest.fail("Live HTTP is forbidden")

    monkeypatch.setattr(Path, "open", guarded_open)
    monkeypatch.setattr(urllib.request.OpenerDirector, "open", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)


@pytest.fixture
def capsule(tmp_path, monkeypatch):
    baseline = m.build_plan(["qwen"], 1, "fixture")
    for relative in baseline["bindings"]:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(m.ROOT / relative, target)
    shutil.copyfile(m.ROOT / "configs/multi_model_api_keys.env.example",
                    tmp_path / "configs/multi_model_api_keys.env.example")
    monkeypatch.setattr(prompt_loader, "PROMPTS_DIR", tmp_path / "prompts/sun_compat")
    return tmp_path


def plan_for(root, providers=None, samples=1):
    return m.build_plan(providers or ["qwen"], samples, "offline_test", root=root)


def approve(plan):
    auth = m.authorization_template(plan)
    auth.update(authorized=True, user_authorization="TEST ONLY: mock requests under tmp_path",
                approved_at_utc="2026-10-05T00:00:00+00:00")
    for budget in auth["budgets"].values():
        budget.update(max_cost=100, input_per_million=1, output_per_million=1,
                      pricing_source="https://example.com/test-only-pricing",
                      pricing_verified_at_utc="2026-10-05T00:00:00+00:00")
    return auth


def fake_keys(profiles, root):
    return {p: "fake-secret-" + p for p in profiles}


def record_for(request):
    return {"schema_version": "1.0.0", "sample_id": request["sample_id"],
            "source_id": request["source_id"], "source_text": request["source_text"],
            "clauses": [], "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
            "validation": {"schema_valid": True, "cross_field_valid": True, "errors": []}}


def response_for(request, profile, **extra):
    response = {"model": profile["model"], "usage": {"prompt_tokens": 100, "completion_tokens": 100},
                "choices": [{"message": {"content": json.dumps(record_for(request))}, "finish_reason": "stop"}]}
    response.update(extra)
    return m.encode(response)


def sender_for(plan, sent):
    def sender(profile, body, key, timeout):
        request = next(r for r in plan["requests"] if m.encode(r["body"]) == body)
        sent.append(request["request_id"])
        assert key == "fake-secret-" + request["provider"]
        return response_for(request, profile)
    return sender


def execute(root, plan, auth, **kwargs):
    return m.execute_plan(plan, auth, execute=True, allow_llm=True, root=root,
                          credential_loader=fake_keys, **kwargs)


def test_same_input_and_prompt_with_provider_specific_parameters(capsule):
    names = list(m.load_catalog()["profiles"])
    plan = plan_for(capsule, names, 2)
    assert plan["planned_calls"] == 12 and plan["retry"] == 0
    assert plan["authorized"] is False and plan["metrics"] is None
    for batch in (plan["requests"][:6], plan["requests"][6:]):
        assert [r["provider"] for r in batch] == names
        assert len({m.encode(r["body"]["messages"]) for r in batch}) == 1
        assert len({r["sample_id"] for r in batch}) == 1
        for r in batch:
            assert r["body_sha256"] == m.digest(m.encode(r["body"]))
    bodies = {r["provider"]: r["body"] for r in plan["requests"][:6]}
    assert bodies["qwen"]["enable_thinking"] is False
    assert bodies["kimi"]["model"] == "kimi-k2.7-code"
    assert bodies["kimi"]["temperature"] == 1 and bodies["kimi"]["top_p"] == 0.95
    assert bodies["kimi"]["thinking"] == {"type": "enabled"}
    assert bodies["mimo"]["max_completion_tokens"] == 4096
    assert bodies["grok"]["reasoning_effort"] == "low"
    assert "temperature" not in bodies["grok"]
    assert bodies["minimax"]["model"] == "MiniMax-M3"
    assert bodies["minimax"]["thinking"] == {"type": "disabled"}
    assert bodies["minimax"]["top_p"] == 0.95
    assert bodies["glm"]["model"] == "glm-5.3-flash"
    assert bodies["glm"]["thinking"] == {"type": "enabled"}
    assert bodies["glm"]["reasoning_effort"] == "low"
    assert not any("gold" in p.lower() or Path(p).name == ".env" for p in plan["bindings"])


@pytest.mark.parametrize("change", ["false", "statement", "flag", "hash", "providers", "calls", "output", "price", "budget", "body", "binding"])
def test_gate_rejects_before_keys_or_send(capsule, change):
    plan = plan_for(capsule)
    auth = approve(plan)
    execute_flag = True
    if change == "false": auth["authorized"] = False
    elif change == "statement": auth["user_authorization"] = ""
    elif change == "flag": execute_flag = False
    elif change == "hash": auth["plan_sha256"] = "wrong"
    elif change == "providers": auth["providers"] = ["grok"]
    elif change == "calls": auth["max_calls"] += 1
    elif change == "output": auth["max_total_output_tokens"] += 1
    elif change == "price": auth["budgets"]["qwen"]["input_per_million"] = None
    elif change == "budget": auth["budgets"]["qwen"]["max_cost"] = 0.000001
    elif change == "body":
        plan["requests"][0]["body"]["model"] = "another-model"
        auth["plan_sha256"] = m.digest(m.encode(plan))
    elif change == "binding":
        plan["bindings"][".env"] = "must-never-read"
        auth["plan_sha256"] = m.digest(m.encode(plan))
    accessed = []
    with pytest.raises(m.ModelRunError):
        m.execute_plan(plan, auth, execute=execute_flag, allow_llm=True, root=capsule,
                       sender=lambda *a: accessed.append("HTTP"),
                       credential_loader=lambda *a: accessed.append("keys"))
    assert accessed == []


@pytest.mark.parametrize("relative", ["configs/models/stage2_multi_model_v1.json", "src/bpc_hybrid/d1_schema_adapter.py", "prompts/sun_compat/direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md"])
def test_source_change_invalidates_authorization(capsule, relative):
    plan = plan_for(capsule)
    with (capsule / relative).open("a", encoding="utf-8") as f:
        f.write("\n")
    with pytest.raises(m.ModelRunError, match="变化"):
        execute(capsule, plan, approve(plan), sender=lambda *a: pytest.fail("no HTTP"))


def test_init_env_appends_blank_slots_without_reading_existing_file(capsule, monkeypatch):
    target = capsule / ".env"
    target.write_text("EXISTING_TEST_KEY=old-test-value", encoding="utf-8")
    original = Path.open
    def append_only(path, mode="r", *args, **kwargs):
        if path == target:
            assert mode == "a"
        return original(path, mode, *args, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(Path, "open", append_only)
        assert "追加" in m.init_env(capsule)
        assert "已初始化" in m.init_env(capsule)
    text = target.read_text(encoding="utf-8")
    assert text.startswith("EXISTING_TEST_KEY=old-test-value")
    assert text.count("LLM4BPC_QWEN_API_KEY=") == 1


def test_private_loader_quotes_blanks_process_override_and_no_mutation(capsule, monkeypatch):
    profiles = m.load_catalog()["profiles"]
    selected = {k: profiles[k] for k in ["qwen", "mimo"]}
    for p in profiles.values(): monkeypatch.delenv(p["api_key_env"], raising=False)
    (capsule / ".env").write_text('export LLM4BPC_QWEN_API_KEY="test-qwen"\nLLM4BPC_QWEN_API_KEY=\nLLM4BPC_MIMO_API_KEY=test-mimo # comment\nUNSELECTED_SECRET=test-unused\n', encoding="utf-8")
    monkeypatch.setenv("LLM4BPC_QWEN_API_KEY", "test-override")
    assert m.load_credentials(selected, capsule) == {"qwen": "test-override", "mimo": "test-mimo"}
    assert "UNSELECTED_SECRET" not in m.os.environ
    (capsule / ".env").write_text("LLM4BPC_QWEN_API_KEY=test-one\nLLM4BPC_QWEN_API_KEY=test-two", encoding="utf-8")
    with pytest.raises(m.ModelRunError) as exc: m.load_credentials(selected, capsule)
    assert "test-one" not in str(exc.value) and "test-two" not in str(exc.value)


def test_every_selected_key_required_before_first_send(capsule, monkeypatch):
    plan = plan_for(capsule, ["qwen", "mimo"])
    for p in plan["profiles"].values(): monkeypatch.delenv(p["api_key_env"], raising=False)
    (capsule / ".env").write_text("LLM4BPC_QWEN_API_KEY=test-only-one\n", encoding="utf-8")
    with pytest.raises(m.ModelRunError, match="MIMO"):
        m.execute_plan(plan, approve(plan), execute=True, allow_llm=True, root=capsule,
                       credential_loader=m.load_credentials, sender=lambda *a: pytest.fail("no HTTP"))
    assert not list(capsule.rglob("calls_ledger.jsonl"))


def test_success_preserves_raw_usage_identity_and_completed_resume_is_zero_send(capsule):
    plan = plan_for(capsule, ["qwen", "mimo"])
    sent = []
    result = execute(capsule, plan, approve(plan), sender=sender_for(plan, sent))
    assert sent == [r["request_id"] for r in plan["requests"]]
    assert result["llm_calls"] == result["valid_predictions"] == 2
    assert result["status"] == "succeeded" and result["metrics"] is None
    assert result["conservative_uncached_cost_by_provider"]["qwen"] == 0.0002
    out = capsule / "outputs/development/stage2_multi_model_v1/offline_test"
    for path in out.rglob("*.json*"):
        assert "fake-secret-" not in path.read_text(encoding="utf-8")
    result = m.execute_plan(plan, approve(plan), execute=True, allow_llm=True, resume=True,
                            root=capsule, sender=lambda *a: pytest.fail("duplicate send"),
                            credential_loader=lambda *a: pytest.fail("completed run needs no keys"))
    assert result["llm_calls"] == 2
    with pytest.raises(m.ModelRunError, match="resume"):
        execute(capsule, plan, approve(plan), sender=lambda *a: pytest.fail("no send"))


@pytest.mark.parametrize("kind", ["timeout", "model", "usage", "length"])
def test_uncertain_call_stops_without_retry_or_resume(capsule, kind):
    plan = plan_for(capsule, samples=2)
    sent = []
    def sender(profile, body, key, timeout):
        sent.append(body)
        if kind == "timeout": raise TimeoutError("must-hide-" + key)
        raw = json.loads(response_for(plan["requests"][0], profile))
        if kind == "model": raw["model"] = "unauthorized-model"
        if kind == "usage": raw["usage"]["completion_tokens"] = 4097
        if kind == "length": raw["choices"][0]["finish_reason"] = "length"
        return m.encode(raw)
    result = execute(capsule, plan, approve(plan), sender=sender)
    assert result["status"] == "partial" and result["llm_calls"] == 1 and len(sent) == 1
    with pytest.raises(m.ModelRunError, match="人工核查"):
        execute(capsule, plan, approve(plan), resume=True, sender=lambda *a: pytest.fail("no retry"))


def interrupt_between_calls(root, plan, monkeypatch):
    original = m._append_ledger
    def interrupted(path, event, previous):
        if event["event"] == "started" and event["request_id"] == plan["requests"][1]["request_id"]:
            raise KeyboardInterrupt("test interruption BEFORE the second request starts")
        return original(path, event, previous)
    with monkeypatch.context() as patch:
        patch.setattr(m, "_append_ledger", interrupted)
        with pytest.raises(KeyboardInterrupt):
            execute(root, plan, approve(plan), sender=sender_for(plan, []))


def test_resume_only_never_attempted_requests(capsule, monkeypatch):
    plan = plan_for(capsule, samples=2)
    interrupt_between_calls(capsule, plan, monkeypatch)
    sent = []
    result = execute(capsule, plan, approve(plan), resume=True, sender=sender_for(plan, sent))
    assert sent == [plan["requests"][1]["request_id"]]
    assert result["llm_calls"] == 2


@pytest.mark.parametrize("kind", ["response", "ledger", "authorization", "orphan", "inflight", "lock"])
def test_resume_checks_previous_artifacts_before_any_new_send(capsule, monkeypatch, kind):
    plan = plan_for(capsule, samples=2)
    interrupt_between_calls(capsule, plan, monkeypatch)
    out = capsule / "outputs/development/stage2_multi_model_v1/offline_test"
    if kind == "response": next((out / "responses").glob("*.json")).write_text("{}", encoding="utf-8")
    elif kind == "ledger":
        with (out / "calls_ledger.jsonl").open("a", encoding="utf-8") as f: f.write("{}\n")
    elif kind == "authorization": (out / "authorization_snapshot.json").write_text("{}", encoding="utf-8")
    elif kind == "orphan":
        (out / "responses" / f"qwen_{plan['requests'][1]['sample_id']}.json").write_text("{}", encoding="utf-8")
    elif kind == "inflight":
        path = out / "calls_ledger.jsonl"
        path.write_text(path.read_text(encoding="utf-8").splitlines()[0] + "\n", encoding="utf-8")
    elif kind == "lock": (out / ".run.lock").touch()
    accessed = []
    with pytest.raises(m.ModelRunError):
        m.execute_plan(plan, approve(plan), execute=True, allow_llm=True, resume=True,
                       root=capsule, sender=lambda *a: accessed.append("HTTP"),
                       credential_loader=lambda *a: accessed.append("keys"))
    assert accessed == []


def test_input_binding_and_complete_think_prefix(capsule):
    request = plan_for(capsule)["requests"][0]
    record = record_for(request)
    assert m.canonical_prediction(request, "<think>reasoning</think>\n" + json.dumps(record))["request_status"] == "ok"
    record["source_text"] += "changed"
    assert m.canonical_prediction(request, json.dumps(record))["failure_stage"] == "input_binding"
    assert m.canonical_prediction(request, "<think>unfinished")["failure_stage"] == "json_parse"


def test_http_error_redaction_and_no_redirect(monkeypatch):
    class FakeOpener:
        def open(self, request, timeout):
            raise urllib.error.HTTPError(request.full_url, 400, "fake failure", {}, io.BytesIO(b'{"error":"Bearer test-http-secret"}'))
    monkeypatch.setattr(urllib.request, "build_opener", lambda *a: FakeOpener())
    with pytest.raises(m.ModelRunError) as exc:
        m.send_http(m.load_catalog()["profiles"]["qwen"], b"{}", "test-http-secret", 1)
    assert "test-http-secret" not in str(exc.value) and "HTTP 400" in str(exc.value)
    with pytest.raises(m.ModelRunError, match="重定向"):
        m._NoRedirect().redirect_request(None, None, 307, "", {}, "https://example.com")


def test_cli_defaults_offline_and_run_flags_fail_before_file_reads(capsule, monkeypatch, capsys):
    assert cli.main([]) == 0
    assert "API 调用 0" in capsys.readouterr().out
    assert cli.main(["run", "--plan", "not-existing.json", "--authorization", "not-existing.json"]) == 2
    assert "不会读取密钥" in capsys.readouterr().err
    original = m.build_plan
    monkeypatch.setattr(m, "build_plan", lambda providers, samples, rid: original(providers, samples, rid, root=capsule))
    monkeypatch.setattr(m, "RUNS", capsule / "offline_plans")
    argv = ["plan", "--providers", "all", "--samples", "1", "--run-id", "cli_test"]
    assert cli.main(argv) == 0
    assert m.read_json(m.RUNS / "cli_test/authorization.template.json")["authorized"] is False
    assert cli.main(argv) == 2  # No overwrite.
