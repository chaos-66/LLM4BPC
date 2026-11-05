import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_sun_modality_prohibition_shots_v1 as run


P, D, O, M = "prohibition", "definition", "obligation", "permission"


def score(gold, old, new):
    return run.assess(list(range(len(gold))), gold, old, new)


def test_targeted_fp_correction_passes():
    result = score([P,D,O,M], [P,P,O,M], [P,D,O,M])
    assert result["meets_all_requirements_on_this_split"]


def test_an_old_correct_row_is_protected_even_when_aggregate_class_scores_improve():
    result = score([P,D,D,D,O,M], [P,P,P,D,O,M], [P,D,D,P,O,M])
    assert result["checks"]["higher_prohibition_f1"]
    assert result["checks"]["other_precision_recall_f1_preserved"]
    assert not result["meets_all_requirements_on_this_split"]


def test_unrelated_swap_between_two_old_wrong_labels_is_protected():
    result = score([P,D,D,O,M], [P,P,O,O,M], [P,D,M,O,M])
    assert not result["checks"]["only_prohibition_related_corrections"]


def test_equal_predictions_do_not_claim_improvement():
    assert not score([P,D], [P,D], [P,D])["meets_all_requirements_on_this_split"]


def test_previous_paid_authorization_cannot_be_reused():
    with pytest.raises(ValueError, match="fresh authorization"):
        run.authorize(run.parent.read(run.parent.AUTH), "new-preflight")


@pytest.mark.skipif(not run.parent.PLAN.exists(), reason="local frozen corpus and request plan required")
def test_frozen_candidate_only_appends_two_training_sentences(monkeypatch):
    load = run.data.load_split
    train = {r.sample_id: r for r in load("train")}

    def train_only(split):
        assert split == "train"
        return load(split)

    monkeypatch.setattr(run.data, "load_split", train_only)
    parent_system = (run.parent.prepared.LOCAL / "composed_system_prompt.txt").read_text(encoding="utf-8").rstrip("\n")
    pairs, bodies, requests, system, record = run.build()
    examples = run.parent.read(run.MANIFEST)["examples"]
    expected = "\n".join(f'{e["position"]}. "{train[e["sample_id"]].text}" -> {train[e["sample_id"]].label}' for e in examples)
    assert system == parent_system + "\n" + expected
    assert len(pairs) == len(bodies) == len(requests) == 426
    assert all(b["messages"][0]["content"] == system for b in bodies.values())
    assert record == run.parent.read(run.FREEZE)
