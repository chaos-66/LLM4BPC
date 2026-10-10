"""D1-R1 runner hardening tests: model pin, prompt-name allowlist, v3 snapshot.

The D1 pilot must run on the pinned model (deepseek-v4-pro) with a
fail-closed model check and a prompt-version switch for the paired
v3-vs-v4 comparison.  These tests verify the allowlist, the snapshot
identity, and the fail-closed decision logic without making any LLM call.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from bpc_hybrid.prompt_loader import load_prompt  # noqa: E402
from bpc_hybrid.stage2_canonical import validate_canonical  # noqa: E402
from scripts.run_direct_llm import (  # noqa: E402
    ALLOWED_PROMPT_NAMES,
    PROMPT_V3_SNAPSHOT,
    PROMPT_V5_FROZEN,
    PROMPT_V6_D1R1,
)

V4_MARKER = "MUST NOT be folded into the action span"

V5_FROZEN_SHA = "79f6f76fc9779abb87fc919e4384386ac812d40fcedaf73df0ea8ea1377af62e"


def test_prompt_name_allowlist_contains_active_and_snapshot() -> None:
    assert "direct_llm_sun_record_prompt" in ALLOWED_PROMPT_NAMES
    assert PROMPT_V3_SNAPSHOT in ALLOWED_PROMPT_NAMES
    assert PROMPT_V5_FROZEN in ALLOWED_PROMPT_NAMES
    assert PROMPT_V6_D1R1 in ALLOWED_PROMPT_NAMES


def test_v6_d1r1_is_v5_plus_field_typing_rules() -> None:
    p = load_prompt(PROMPT_V6_D1R1)
    assert "constraint covers legal references" in p.system_prompt
    assert "MUST NOT be folded into the" in p.system_prompt
    assert "reported in BOTH arrays" in p.system_prompt
    assert len(p.few_shot_examples) == 6
    assert "The taxpayer shall depreciate the acquisition costs" in p.few_shot_examples[4]["input"]
    assert "The tax office shall refund the amount" in p.few_shot_examples[5]["input"]


def test_v6_few_shot_fixtures_validate() -> None:
    p = load_prompt(PROMPT_V6_D1R1)
    for ex in p.few_shot_examples:
        rep = validate_canonical(ex["output"])
        assert rep.schema_valid and rep.cross_field_valid, ex["description"][:60]


def test_v5_frozen_is_the_july_runtime_prompt() -> None:
    p = load_prompt(PROMPT_V5_FROZEN)
    assert p.sha256 == V5_FROZEN_SHA
    assert "stage2_extraction_contract@1.0.0" in p.system_prompt
    assert "pronoun" in p.system_prompt.lower()
    assert len(p.few_shot_examples) == 4
    assert "few_shot_block" in p.user_prompt_template


def test_v3_snapshot_is_the_old_prompt() -> None:
    p = load_prompt(PROMPT_V3_SNAPSHOT)
    assert len(p.sha256) == 64
    assert V4_MARKER not in p.system_prompt
    assert "within 72 hours" in p.user_prompt_template
    # the snapshot must contain exactly the four original few-shot examples
    assert len(p.few_shot_examples) == 4


def test_v4_active_prompt_has_the_new_rules() -> None:
    p = load_prompt("direct_llm_sun_record_prompt")
    assert V4_MARKER in p.system_prompt
    assert len(p.few_shot_examples) == 6


def test_unknown_prompt_name_is_rejected_by_cli() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.run_direct_llm",
            "--prompt-name",
            "does_not_exist",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    assert completed.returncode == 2
    assert "invalid choice" in completed.stderr


def test_model_pin_mismatch_fails_closed_before_calls(tmp_path, monkeypatch, capsys) -> None:
    from types import SimpleNamespace
    from scripts import run_direct_llm as runner

    # Test the pin behind the new default's development guard, using a fake
    # configuration so this offline test never opens .env or constructs an API.
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(
        runner.LLMConfig, "from_env",
        staticmethod(lambda **kwargs: SimpleNamespace(model="offline-model")),
    )

    def forbidden(*args, **kwargs):
        pytest.fail("Model mismatch must stop before transport construction")

    monkeypatch.setattr(runner, "RealAPITransport", forbidden)
    root = tmp_path / "outputs/development/s2_prompt_cleanup_v1/new"
    monkeypatch.setattr(sys, "argv", [
        "run_direct_llm.py", "--development", "--allow-llm",
        "--model", "definitely-not-the-resolved-model",
        "--output", str(root / "out.jsonl"),
        "--manifest", str(root / "manifest.json"),
    ])
    assert runner.main() == 2
    output = capsys.readouterr().out
    assert "resolved model" in output and "fail-closed model pin" in output
