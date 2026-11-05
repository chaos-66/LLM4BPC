"""Guard train provenance, rejection of held-out copies and the frozen comparison."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prepare_sun_modality_eligibility_shots_v1 as prep


@pytest.mark.parametrize("candidate", [
    "ONE two three four five six seven eight nine ten!",
    "one two three four revised six seven eight nine ten",
    "introduction contains a separate premise one two three four five six seven eight nine ten and a long conclusion with additional details",
])
def test_held_out_copies_and_embedded_excerpts_are_rejected(candidate):
    shot = prep.data.Example("train-id", "one two three four five six seven eight nine ten", "permission")
    with pytest.raises(ValueError, match="held-out overlap"):
        prep.check_isolation([shot], [("different-id", candidate)])


@pytest.mark.parametrize("mutation", ["held-out-id", "changed-label", "changed-text", "repeat-old"])
def test_fixed_manifest_cannot_import_a_different_example(mutation):
    labels = ["definition", "permission"] * 2
    rows = [prep.data.Example(str(i), f"training example number {i}", label) for i, label in enumerate(labels)]
    specs = [dict(sample_id=r.sample_id, label=r.label, text_sha256=prep.boundary.digest(r.text.encode())) for r in rows]
    inherited = set()
    if mutation == "held-out-id":
        specs[0]["sample_id"] = "outside-train"
    elif mutation == "changed-label":
        rows[0] = prep.data.Example(rows[0].sample_id, rows[0].text, "permission")
    elif mutation == "changed-text":
        specs[0]["text_sha256"] = "unexpected"
    else:
        inherited.add(rows[0].sample_id)
    with pytest.raises(ValueError):
        prep.resolve_examples(rows, specs, inherited)


@pytest.mark.skipif(any(not x["path"].exists() for x in prep.data.EXPECTED.values()), reason="local corpus required")
def test_real_prompt_is_parent_plus_verbatim_train_pairs_and_only_train_labels(monkeypatch):
    load = prep.data.load_split
    train = {r.sample_id: r for r in load("train")}

    def train_only(name):
        assert name == "train"
        return load(name)

    monkeypatch.setattr(prep.data, "load_split", train_only)
    composed, block, report = prep.build()
    frozen_parent = prep.review_prompt.request_body("witness", "Witness.")["messages"][0]["content"]
    assert composed == frozen_parent + "\n\n" + block
    manifest = json.loads(prep.MANIFEST.read_text(encoding="utf-8"))
    assert block.splitlines()[2:] == [
        f'{i}. "{train[s["sample_id"]].text}" -> {train[s["sample_id"]].label}'
        for i, s in enumerate(manifest["examples"], 19)
    ]
    assert report == json.loads(prep.REPORT.read_text(encoding="utf-8"))
