"""Offline checks of the actual plain messages and response integration."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from bpc_hybrid.llm_config import LLMConfig
from bpc_hybrid.plain_prompt import (
    PLAIN_PROMPT_NAME, READABLE_REASONS, prepare_plain_prediction,
)
from bpc_hybrid.prompt_loader import load_prompt
from bpc_hybrid.stage2_canonical import validate_canonical
from scripts import build_plain_prompt_v1 as builder


@pytest.fixture
def runner(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location(
        "plain_prompt_runner_test", ROOT / "scripts/run_direct_llm.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("Offline checks must not read env or construct a real transport")

    monkeypatch.setattr(module.LLMConfig, "from_env", staticmethod(forbidden))
    monkeypatch.setattr(module, "RealAPITransport", forbidden)
    return module


def test_actual_rendered_messages_have_no_internal_identifiers(runner):
    prompt = load_prompt(PLAIN_PROMPT_NAME)
    examples = runner._few_shot_block(prompt)
    source = 'The controller must report {risk}.\nUnless consent is withdrawn: ü.'
    user = prompt.user_prompt_template.format(source_text=source, few_shot_block=examples)
    sent = prompt.system_prompt + "\n" + user
    assert "Target text:\n" + source in user
    assert "Example 6" in examples and "six synthetic examples" in user
    assert not re.search(r"[0-9a-f]{32,}|@[0-9]|synthetic_[a-z_]+\d+", sent)
    for marker in (
        "SHA", "stage2_extraction_contract", "stage2_prediction.schema",
        "schema_version", "schema_source", "schema_valid", "cross_field_valid",
        "D1-R1", "target_text_only", "reference_status=", "independence_status=",
        "semantic_scope_ambiguous_in_target", "clause_boundary_ambiguous",
        "context_required", "canonical", "Sun-compatible", "contract behavior",
    ):
        assert marker not in sent
    assert prompt.extras == {}


def test_builder_reproduces_complete_prompt():
    assert load_prompt(PLAIN_PROMPT_NAME).raw_text == builder.render()


def _without_ids(value):
    if isinstance(value, dict):
        return {
            key: _without_ids(child)
            for key, child in value.items()
            if key not in {"id", "clause_id", "actor_id", "action_id", "before_action_id", "after_action_id"}
        }
    if isinstance(value, list):
        return [_without_ids(child) for child in value]
    return value


@pytest.mark.parametrize("index", range(6))
def test_examples_keep_original_semantics_offsets_and_valid_relations(index):
    original = load_prompt("direct_llm_sun_record_prompt_v6_d1r1_2026_08_05")
    plain = load_prompt(PLAIN_PROMPT_NAME)
    assert len(plain.few_shot_examples) == 6
    old, new = original.few_shot_examples[index], plain.few_shot_examples[index]
    assert new["input"] == old["input"]
    assert _without_ids(new["output"]["clauses"]) == _without_ids(old["output"]["clauses"])
    decoded = deepcopy(new["output"])
    record = prepare_plain_prediction(
        decoded, sample_id="example", source_text=old["output"]["source_text"]
    )
    assert record["unsupported_or_ambiguous"] == old["output"]["unsupported_or_ambiguous"]
    assert record["validation"]["schema_valid"] is False
    result = validate_canonical(record)
    assert result.schema_valid and result.cross_field_valid, result.errors
    assert decoded == new["output"]  # metadata attachment must not mutate raw output


@pytest.mark.parametrize("readable,internal", READABLE_REASONS.items())
def test_readable_reasons_keep_existing_downstream_status(readable, internal):
    payload = {"clauses": [], "unsupported_or_ambiguous": [{"field": "actor", "reason": readable}]}
    result = prepare_plain_prediction(payload, sample_id="example", source_text="It must report.")
    assert result["unsupported_or_ambiguous"][0]["reason"] == internal
    assert payload["unsupported_or_ambiguous"][0]["reason"] == readable


@pytest.mark.parametrize("payload", [
    [], {"clauses": []}, {"clauses": {}, "unsupported_or_ambiguous": []},
    {"clauses": [], "unsupported_or_ambiguous": "none"},
    {"clauses": [], "unsupported_or_ambiguous": [None]},
    {"clauses": [], "unsupported_or_ambiguous": [{"field": "actor", "reason": []}]},
    {"clauses": [], "unsupported_or_ambiguous": [{"field": "actor", "reason": "guess"}]},
    {"clauses": [], "unsupported_or_ambiguous": [], "validation": {"schema_valid": True}},
])
def test_invalid_envelopes_and_model_supplied_bookkeeping_fail_closed(payload):
    with pytest.raises(ValueError):
        prepare_plain_prediction(payload, sample_id="example", source_text="It must report.")


def test_metadata_attachment_does_not_hide_invalid_span():
    plain = load_prompt(PLAIN_PROMPT_NAME).few_shot_examples[0]
    payload = deepcopy(plain["output"])
    payload["clauses"][0]["actors"][0]["start"] = 1
    record = prepare_plain_prediction(
        payload, sample_id="example", source_text=json.loads(plain["input"])
    )
    result = validate_canonical(record)
    assert not result.cross_field_valid
    assert record["clauses"][0]["actors"][0]["start"] == 1


@pytest.mark.parametrize("unsafe", ["missing_development", "formal_output", "formal_manifest", "path_escape"])
def test_default_plain_prompt_cannot_write_formal_or_escaping_paths(unsafe, runner, monkeypatch, capsys):
    assert runner.PROMPTName == PLAIN_PROMPT_NAME
    root = runner.ROOT / "outputs/development/s2_prompt_cleanup_v1"
    output, manifest = root / "new/predictions.jsonl", root / "new/manifest.json"
    args = ["run_direct_llm.py", "--allow-llm"]
    if unsafe != "missing_development":
        args.append("--development")
    if unsafe == "formal_output":
        output = runner.ROOT / "data/predictions/old.jsonl"
    if unsafe == "formal_manifest":
        manifest = runner.ROOT / "data/predictions/old.manifest.json"
    if unsafe == "path_escape":
        output = root / "../outside.jsonl"
    monkeypatch.setattr(sys, "argv", args + ["--output", str(output), "--manifest", str(manifest)])
    assert runner.main() == 2
    assert "plain prompt requires" in capsys.readouterr().out
    assert not output.exists() and not manifest.exists()


def test_plain_prompt_still_requires_real_call_authorization(runner, monkeypatch, capsys):
    root = runner.ROOT / "outputs/development/s2_prompt_cleanup_v1"
    monkeypatch.setattr(sys, "argv", [
        "run_direct_llm.py", "--development", "--output", str(root / "new/predictions.jsonl"),
        "--manifest", str(root / "new/manifest.json"),
    ])
    assert runner.main() == 2
    assert "real LLM calls require explicit authorization" in capsys.readouterr().out


def test_runner_processes_plain_response_through_existing_validation(runner, monkeypatch):
    prompt = load_prompt(PLAIN_PROMPT_NAME)
    example = prompt.few_shot_examples[0]
    source_text = json.loads(example["input"])
    input_path = runner.ROOT / "input.jsonl"
    input_path.write_text(json.dumps({"sample_id": "example", "text": source_text}) + "\n", encoding="utf-8")
    root = runner.ROOT / "outputs/development/s2_prompt_cleanup_v1/new"
    output, manifest = root / "predictions.jsonl", root / "manifest.json"
    config = LLMConfig(enabled=True, provider="openai_compatible", model="offline-model", api_key="offline-placeholder")
    monkeypatch.setattr(runner.LLMConfig, "from_env", staticmethod(lambda **kwargs: config))
    requests = []

    class FakeTransport:
        last_request_policy = {}

        def __init__(self, *args, **kwargs):
            pass

        def send(self, request):
            requests.append(request)
            return SimpleNamespace(model="offline-model", content=json.dumps(example["output"]))

    monkeypatch.setattr(runner, "RealAPITransport", FakeTransport)
    monkeypatch.setattr(sys, "argv", [
        "run_direct_llm.py", "--development", "--allow-llm", "--max-calls", "1",
        "--input", str(input_path), "--output", str(output), "--manifest", str(manifest),
    ])
    assert runner.main() == 0
    assert len(requests) == 1
    assert requests[0].system_prompt == prompt.system_prompt
    assert "Example 6" in requests[0].user_prompt
    assert "stage2_prediction.schema" not in requests[0].user_prompt
    record = json.loads(output.read_text(encoding="utf-8"))
    assert record["source_text"] == source_text and record["sample_id"] == "example"
    assert record["validation"] == {"schema_valid": True, "cross_field_valid": True, "errors": []}
    saved_manifest = json.loads(manifest.read_text(encoding="utf-8"))
    assert saved_manifest["mode"] == "development"
    assert saved_manifest["prompts"][0]["sha256"] == prompt.sha256
