"""The small prompt edits preserve original 22-shot task and label semantics."""
import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prepare_sun_modality_es_minimal_v1 as prep


def test_variants_are_isolated_and_keep_original_interface(monkeypatch):
    load = prep.data.load_split
    def train_only(name):
        assert name == "train"
        return load(name)
    monkeypatch.setattr(prep.data, "load_split", train_only)
    baseline, systems, report = prep.build()
    changes = prep.read(prep.CHANGES)
    train = {r.sample_id: r for r in load("train")}
    edit = changes["E1"]
    old, new = (train[edit[k]["sample_id"]] for k in ("old", "new"))
    assert systems["E1"].replace(f'15. "{new.text}" -> {new.label}', f'15. "{old.text}" -> {old.label}', 1) == baseline
    assert systems["S1"].replace(changes["S1"]["after"], changes["S1"]["before"], 1) == baseline
    e, s = (report["variants"][k] for k in ("E1", "S1"))
    assert e["train_example_count"] == s["train_example_count"] == 22
    assert e["class_totals"] == s["class_totals"]
    assert sum(a != b for a, b in zip(e["train_example_ids"], s["train_example_ids"])) == 1
    assert report["new_example_vs_held_out_comparisons"] == {"dev": 420, "test": 426}
    expected = prep.request_body(baseline, "synthetic", "A user may submit a form.")
    for system in systems.values():
        body = prep.request_body(system, "synthetic", "A user may submit a form.")
        body["messages"][0]["content"] = baseline
        assert body == expected
    # The original label reader ignores span-coordinate errors and retains the first label.
    response = {"clauses": [{"modality": {"label": "permission", "evidence": [{"text": "may", "start": 999, "end": 1002}]}},
                            {"modality": {"label": "prohibition"}}]}
    assert prep.llm_se.extract_modality_label(json.dumps(response))["label"] == "permission"


@pytest.mark.parametrize("field,value", [("sample_id", "absent"), ("label", "permission"), ("text_sha256", "changed")])
def test_changed_train_id_label_or_text_is_rejected(field, value):
    changes = prep.read(prep.CHANGES)
    spec = copy.deepcopy(changes["E1"]["new"])
    train = {r.sample_id: r for r in prep.data.load_split("train")}
    spec[field] = value
    with pytest.raises(ValueError, match="training membership"):
        prep.resolve_train_row(train, spec)
