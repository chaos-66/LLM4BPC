"""Offline review evidence and request-boundary checks; no model-score claims."""
import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bpc_hybrid.modality_benchmark import boundary, data, fewshot, review_prompt


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("binding", ["guidance", "parent_preflight", "parent_result", "error_review"])
def test_changed_bound_input_is_rejected(tmp_path, monkeypatch, binding):
    contract = review_prompt.read_contract()
    changed = tmp_path / "changed.txt"
    changed.write_text("Different content", encoding="utf-8")
    contract[binding]["path"] = str(changed)
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    monkeypatch.setattr(review_prompt, "CONTRACT", contract_path)
    with pytest.raises(ValueError, match="binding mismatch: " + binding):
        review_prompt.read_contract()


def test_review_appends_only_system_and_keeps_the_original_train_block(monkeypatch):
    before = {"model": "synthetic-model", "temperature": 0, "top_p": 1,
              "max_tokens": 4096, "thinking": {"type": "disabled"},
              "messages": [{"role": "system", "content": "Original instructions and demonstrations."},
                           {"role": "user", "content": "Synthetic source sentence."}]}
    calls = []
    def parent_body(sid, text, *, block):
        calls.append((sid, text, block))
        return copy.deepcopy(before)
    monkeypatch.setattr(fewshot, "request_body", parent_body)
    contract = review_prompt.read_contract()
    guidance = (ROOT / contract["guidance"]["path"]).read_text(encoding="utf-8").strip()
    after = review_prompt.request_body("synthetic-id", "Synthetic source sentence.", block="Original block")
    assert calls == [("synthetic-id", "Synthetic source sentence.", "Original block")]
    assert after["messages"][0]["content"] == before["messages"][0]["content"] + "\n\n" + guidance
    after["messages"][0]["content"] = before["messages"][0]["content"]
    assert after == before


def test_liability_marker_has_word_boundaries_and_does_not_match_company_nouns():
    analysis = script("analyze_sun_modality_review_v1")
    synthetic = [data.Example("liability", "synthetic haftet synthetic", "definition"),
                 data.Example("company", "synthetic gesellschaften synthetic", "obligation")]
    found = analysis.marker_summary(synthetic)["liability"]
    assert found["sample_ids"] == ["liability"]
    assert found["label_counts"] == {"definition": 1}


def review_fixture():
    row = {"sample_id": "synthetic", "gold": "definition", "fewshot": "obligation",
           "boundary": "obligation", "v6": None, "sun": "definition"}
    return {"cases": [row], "human_adjudication_performed": False, "gold_changes": False}, {
        "fewshot_errors": [copy.deepcopy(row)]}


def test_error_review_accepts_exact_parent_labels():
    analysis = script("analyze_sun_modality_review_v1")
    review, parent = review_fixture()
    assert set(analysis.verify_cases(review, parent)) == {"synthetic"}


@pytest.mark.parametrize("mutation", ["duplicate", "label", "human", "gold"])
def test_error_review_rejects_changed_coverage_labels_or_adjudication(mutation):
    analysis = script("analyze_sun_modality_review_v1")
    review, parent = review_fixture()
    if mutation == "duplicate":
        review["cases"].append(copy.deepcopy(review["cases"][0]))
    elif mutation == "label":
        review["cases"][0]["gold"] = "permission"
    elif mutation == "human":
        review["human_adjudication_performed"] = True
    else:
        review["gold_changes"] = True
    with pytest.raises(ValueError):
        analysis.verify_cases(review, parent)


def test_parent_source_drift_is_rejected_but_line_endings_are_normalized(tmp_path, monkeypatch):
    prepare = script("prepare_sun_modality_review_v1")
    monkeypatch.setattr(prepare, "ROOT", tmp_path)
    path = tmp_path / "parent.py"
    path.write_bytes(b"original\r\n")
    bindings = {"parent.py": boundary.digest(b"original\n")}
    prepare.verify_parent_sources(bindings)
    path.write_bytes(b"modified\n")
    with pytest.raises(ValueError, match="parent source drift"):
        prepare.verify_parent_sources(bindings)
