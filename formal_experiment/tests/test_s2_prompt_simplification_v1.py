"""Offline candidate integrity and the actual direct-runner safety boundary."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bpc_hybrid.prompt_loader import load_prompt, render_user_prompt
from bpc_hybrid.stage2_canonical import validate_canonical

CANDIDATE_DIR = ROOT / "prompts/sun_compat/simplification_v1"
MANIFEST = json.loads((CANDIDATE_DIR / "manifest.json").read_text(encoding="utf-8"))
SNAPSHOT = json.loads((ROOT / MANIFEST["baseline_snapshot"]).read_text(encoding="utf-8"))
NAMES = [row["prompt_name"] for row in MANIFEST["variants"]]
BASELINE_PATH = "prompts/sun_compat/direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md"
BASELINE_TEXT = next(row["content_utf8"] for row in SNAPSHOT["artifacts"]
                     if row["source_path"] == BASELINE_PATH).replace("\r\n", "\n")


@pytest.fixture
def runner(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location(
        "s2_prompt_simplification_test_runner", ROOT / "scripts/run_direct_llm.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("Offline candidate checks must not read env or construct API transport")

    monkeypatch.setattr(module.LLMConfig, "from_env", staticmethod(forbidden))
    monkeypatch.setattr(module, "RealAPITransport", forbidden)
    return module


def test_snapshot_preserves_original_bytes_and_result_provenance():
    raw = (ROOT / MANIFEST["baseline_snapshot"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == MANIFEST["baseline_snapshot_sha256"]
    assert len(SNAPSHOT["artifacts"]) == 15
    for row in SNAPSHOT["artifacts"]:
        original = row["content_utf8"].encode("utf-8")
        assert len(original) == row["byte_count"]
        assert hashlib.sha256(original).hexdigest() == row["sha256"]
        assert row["source_commit"] == MANIFEST["baseline_commit"]
        assert len(row["git_blob"]) == 40
    reports = {row["source_path"] for row in SNAPSHOT["artifacts"]}
    assert "outputs/reports/stage2_table1_paper_final_v1.json" in reports
    assert "outputs/reports/v6_factorial_ablation_v1.json" in reports
    assert "outputs/reports/sep_c3_modular_ablation_analysis_v1.json" in reports


@pytest.mark.parametrize("name", NAMES)
def test_loaded_candidate_keeps_exact_example_block_and_valid_spans(name):
    prompt = load_prompt(name)
    row = next(row for row in MANIFEST["variants"] if row["prompt_name"] == name)
    assert prompt.sha256 == row["prompt_sha256"]
    assert hashlib.sha256(prompt.path.read_bytes()).hexdigest() == row["raw_bytes_sha256"]
    assert prompt.raw_text.split("## Examples", 1)[1] == BASELINE_TEXT.split("## Examples", 1)[1]
    assert len(prompt.few_shot_examples) == 6
    for example in prompt.few_shot_examples:
        validation = validate_canonical(example["output"])
        assert validation.schema_valid and validation.cross_field_valid, validation.errors


@pytest.mark.parametrize("name", NAMES)
def test_real_runner_renders_all_examples_and_literal_input(name, runner):
    prompt = load_prompt(name)
    source_text = 'The controller must report {risk}.\nUnless the person consents: ü.'
    examples = runner._few_shot_block(prompt)
    expected = BASELINE_TEXT[BASELINE_TEXT.index("## Examples"):BASELINE_TEXT.index("## Notes")].strip()
    assert examples == expected
    rendered = render_user_prompt(
        prompt.user_prompt_template, sample_id="synthetic_bind_01", source_id="synthetic_source_01",
        source_text=source_text, few_shot_block=examples,
    )
    assert "source_text:\n" + source_text in rendered
    assert "sample_id: synthetic_bind_01" in rendered
    assert "source_id: synthetic_source_01" in rendered
    assert "Example 6" in rendered
    assert "{few_shot_block}" not in rendered


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("unsafe", ["missing_development", "formal_output", "formal_manifest", "path_escape"])
def test_candidate_guard_rejects_unsafe_paths_before_env_or_api(name, unsafe, runner, monkeypatch, capsys):
    root = runner.ROOT / "outputs/development/s2_prompt_simplification_v1"
    output, manifest = root / "new/predictions.jsonl", root / "new/manifest.json"
    args = ["run_direct_llm.py", "--prompt-name", name, "--allow-llm"]
    if unsafe != "missing_development":
        args.append("--development")
    if unsafe == "formal_output":
        output = runner.ROOT / "data/predictions/old.jsonl"
    if unsafe == "formal_manifest":
        manifest = runner.ROOT / "data/predictions/old.manifest.json"
    if unsafe == "path_escape":
        output = root / "../outside.jsonl"
    args += ["--output", str(output), "--manifest", str(manifest)]
    monkeypatch.setattr(sys, "argv", args)
    assert runner.main() == 2
    assert "simplification candidates require" in capsys.readouterr().out
    assert not output.exists() and not manifest.exists()


@pytest.mark.parametrize("name", NAMES)
def test_valid_candidate_still_requires_real_call_authorization(name, runner, monkeypatch, capsys):
    root = runner.ROOT / "outputs/development/s2_prompt_simplification_v1"
    output, manifest = root / "new/predictions.jsonl", root / "new/manifest.json"
    monkeypatch.setattr(sys, "argv", [
        "run_direct_llm.py", "--prompt-name", name, "--development",
        "--output", str(output), "--manifest", str(manifest),
    ])
    assert runner.main() == 2
    assert "real LLM calls require explicit authorization" in capsys.readouterr().out
    assert not output.exists() and not manifest.exists()


def test_runner_keeps_original_default_and_old_allowlist(runner):
    baseline_runner = next(row["content_utf8"] for row in SNAPSHOT["artifacts"]
                           if row["source_path"] == "scripts/run_direct_llm.py")
    original_default = next(ast.literal_eval(node.value) for node in ast.parse(baseline_runner).body
                            if isinstance(node, ast.Assign)
                            and any(isinstance(t, ast.Name) and t.id == "PROMPTName" for t in node.targets))
    assert runner.PROMPTName == original_default
    assert runner.PROMPT_V6_D1R1 in runner.ALLOWED_PROMPT_NAMES
    assert set(NAMES).issubset(runner.ALLOWED_PROMPT_NAMES)
