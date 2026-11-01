"""Focused offline checks: data separation, frozen labels, and request shape."""
import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bpc_hybrid.modality_benchmark import boundary, data, fewshot


def small_selection():
    # Synthetic text only; the first two candidates tie in length and sort by ID.
    train = [data.Example("b", "A member may request a copy.", "permission"),
             data.Example("a", "A person may request a copy.", "permission"),
             data.Example("c", "A member may request a longer printed copy.", "permission")]
    chosen = train[1]
    manifest = {
        "selection_rule": {"quota": {"M": 1}, "strata_markers": {}},
        "presentation_order": [["M", 0]], "class_totals": {"permission": 1},
        "selections": [{"position": 1, "stratum": "M", "sample_id": "a",
                        "label": "permission", "word_count": 6,
                        "text_sha256_utf8_lf": boundary.digest((chosen.text + "\n").encode())}]}
    return train, manifest


def test_selection_is_order_invariant_and_matches_frozen_manifest():
    train, manifest = small_selection()
    assert [r.sample_id for r in fewshot.select_examples(train, [], manifest)] == ["a"]
    assert fewshot.select_examples(train[::-1], [], manifest) == fewshot.select_examples(train, [], manifest)


@pytest.mark.parametrize("overlap", ["id", "normalized_text"])
def test_held_out_overlap_stops_selection(overlap):
    train, manifest = small_selection()
    held = [("a", "A completely different sentence.")] if overlap == "id" else [
        ("test", "  A PERSON MAY REQUEST A COPY.  ")]
    with pytest.raises(ValueError, match="overlap"):
        fewshot.select_examples(train, held, manifest)


def test_changed_label_or_missing_train_candidate_is_rejected():
    train, manifest = small_selection()
    changed = copy.deepcopy(manifest)
    changed["selections"][0]["label"] = "prohibition"
    with pytest.raises(ValueError, match="frozen manifest"):
        fewshot.select_examples(train, [], changed)
    with pytest.raises(ValueError, match="insufficient"):
        fewshot.select_examples([], [], manifest)


def test_header_drift_is_rejected(tmp_path, monkeypatch):
    contract = fewshot.read_contract()
    header = tmp_path / "header.md"
    header.write_text("Changed header", encoding="utf-8")
    contract["header"]["path"] = str(header)
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")
    monkeypatch.setattr(fewshot, "CONTRACT", path)
    with pytest.raises(ValueError, match="artifact hash mismatch: header"):
        fewshot.read_contract()


def test_only_system_append_changes_and_wire_matches_transport(monkeypatch):
    from bpc_hybrid.h1_transport import H1RequestPolicy
    from bpc_hybrid.llm_client import OpenAICompatibleRequestBuilder
    from bpc_hybrid.llm_config import LLMConfig
    block = 'Synthetic corpus demonstration.\n1. "A user may submit a form." -> permission\n'
    contract = fewshot.read_contract()
    contract["demonstration_block_sha256"] = boundary.digest(block.encode())
    monkeypatch.setattr(fewshot, "read_contract", lambda: contract)
    before = boundary.request_body("synthetic", "A user may submit a form.")
    after = fewshot.request_body("synthetic", "A user may submit a form.", block=block)
    assert after["messages"][0]["content"] == before["messages"][0]["content"] + "\n\n" + block.strip()
    assert after["messages"][1] == before["messages"][1]
    config = LLMConfig(enabled=True, provider="openai_compatible", model="deepseek-v4-pro",
                       api_key="synthetic-test-key", base_url="https://api.deepseek.com",
                       temperature=0.0, top_p=1.0, max_tokens=4096)
    built = OpenAICompatibleRequestBuilder(config).build_payload(
        system_prompt=after["messages"][0]["content"], user_prompt=after["messages"][1]["content"])["body"]
    built = H1RequestPolicy(response_format=None).apply_to_body(built)
    assert boundary.wire_bytes(after) == json.dumps(built).encode()
    after["messages"][0]["content"] = before["messages"][0]["content"]
    assert before == after
    with pytest.raises(ValueError, match="block hash mismatch"):
        fewshot.request_body("synthetic", "text", block=block + "changed")


def test_loader_checks_train_hash_before_reading_labels(monkeypatch):
    monkeypatch.setattr(data, "sha256_file", lambda path: "wrong")
    def forbidden(*args):
        pytest.fail("labels must not be loaded after a hash mismatch")
    monkeypatch.setattr(data, "load_split", forbidden)
    with pytest.raises(ValueError, match="train split hash mismatch"):
        fewshot.load_demonstrations()


def test_loader_uses_labels_from_train_only(tmp_path, monkeypatch):
    train, manifest = small_selection()
    header = tmp_path / "header.md"
    header.write_text("Synthetic header", encoding="utf-8")
    selection = tmp_path / "selection.json"
    selection.write_text(json.dumps(manifest), encoding="utf-8")
    block = 'Synthetic header\n\n1. "A person may request a copy." -> permission\n'
    contract = {"header": {"path": str(header)}, "selection_manifest": {"path": str(selection)},
                "demonstration_block_sha256": boundary.digest(block.encode())}
    monkeypatch.setattr(fewshot, "read_contract", lambda: contract)
    monkeypatch.setattr(data, "EXPECTED", {"train": {"path": tmp_path / "train", "sha256": "ok", "rows": 3}})
    monkeypatch.setattr(data, "sha256_file", lambda path: "ok")
    def train_labels_only(name):
        assert name == "train", "held-out labels must not be accessed"
        return train
    held_calls = []
    def text_only(name):
        held_calls.append(name)
        return [(name, "An unrelated held out sentence.")]
    monkeypatch.setattr(data, "load_split", train_labels_only)
    monkeypatch.setattr(data, "load_split_text_only", text_only)
    assert fewshot.load_demonstrations()[0] == block
    assert held_calls == ["dev", "test"]


def test_preparation_refuses_to_overwrite_an_existing_different_artifact(tmp_path):
    spec = importlib.util.spec_from_file_location("fewshot_prepare_test", ROOT / "scripts/prepare_sun_modality_fewshot_v1.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    path = tmp_path / "artifact.txt"
    module.write_frozen(path, b"original")
    module.write_frozen(path, b"original")
    with pytest.raises(ValueError, match="refusing to overwrite"):
        module.write_frozen(path, b"replacement")
    assert path.read_bytes() == b"original"
