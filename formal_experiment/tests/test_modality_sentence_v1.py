"""Focused offline interface tests; synthetic fixtures, no performance claim."""
import copy
import json
import sys
from pathlib import Path

import pytest

from bpc_hybrid.modality_benchmark import data, llm_se, sentence as candidate

ROOT = Path(__file__).resolve().parents[1]


def example(index=0):
    return copy.deepcopy(candidate.read_json(candidate.PROMPT_DIR / "format_examples.json")[index])


def parse(obj, **kwargs):
    record = obj["rule_record"]
    return candidate.parse_response(json.dumps(obj), request_id=record["sample_id"],
                                    source_text=record["source_text"], **kwargs)


def test_all_synthetic_envelopes_reuse_canonical_validation():
    for obj in candidate.read_json(candidate.PROMPT_DIR / "format_examples.json"):
        before = copy.deepcopy(obj)
        result = parse(obj)
        assert result["status"] == "ok"
        assert result["rule_record_validation"] == {
            "schema_valid": True, "cross_field_valid": True, "errors": []}
        assert obj == before


def test_explicit_decision_does_not_relabel_or_reorder_clauses():
    obj = example(3)  # definition then obligation; synthetic sentence label obligation
    before = copy.deepcopy(obj["rule_record"]["clauses"])
    result = parse(obj)
    assert result["label"] == "obligation"
    assert result["first_clause_label"] == "definition"
    assert result["rule_record"]["clauses"] == before
    obj["sentence_modality"]["label"] = "definition"
    assert parse(obj)["label"] == "definition"  # no O>P>M>D rule or fallback


def test_null_is_not_repaired_from_clause_label():
    obj = example()
    obj["sentence_modality"] = {"label": None, "evidence": [], "uncertainty": ["incomplete_input"]}
    result = parse(obj)
    assert result["label"] is None and result["status"] == "null_label"
    assert result["first_clause_label"] == "permission"
    obj["sentence_modality"]["uncertainty"] = []
    assert parse(obj)["status"] == "invalid_sentence_modality"


def test_empty_rule_record_can_have_a_valid_null_sentence():
    obj = example()
    obj["rule_record"]["clauses"] = []
    obj["sentence_modality"] = {"label": None, "evidence": [], "uncertainty": ["incomplete_input"]}
    result = parse(obj)
    assert result["status"] == "null_label"
    assert result["first_clause_label"] is None
    assert result["rule_record_validation"]["cross_field_valid"]


@pytest.mark.parametrize("bad", ["unknown", [], True, 2])
def test_invalid_sentence_labels_do_not_fall_back(bad):
    obj = example()
    obj["sentence_modality"]["label"] = bad
    result = parse(obj)
    assert result["label"] is None
    assert result["first_clause_label"] == "permission"


@pytest.mark.parametrize("field,value", [("text", "invented"), ("start", -1),
                                        ("start", True), ("end", 9999)])
def test_sentence_evidence_must_match_input(field, value):
    obj = example()
    obj["sentence_modality"]["evidence"][0][field] = value
    assert parse(obj)["status"] == "invalid_sentence_modality"


@pytest.mark.parametrize("flags", [["invented"], ["incomplete_input"] * 2, [[]], "incomplete_input"])
def test_unknown_or_duplicate_flags_fail_closed(flags):
    obj = example()
    obj["sentence_modality"]["uncertainty"] = flags
    assert parse(obj)["label"] is None


def test_canonical_span_validation_is_independent_and_authoritative():
    obj = example()
    obj["rule_record"]["clauses"][0]["actions"][0]["text"] = "not an input span"
    result = parse(obj)
    assert result["label"] == "permission"
    assert not result["rule_record_validation"]["cross_field_valid"]
    assert result["rule_record"]["validation"] == result["rule_record_validation"]
    assert result["first_clause_label"] == "permission"


@pytest.mark.parametrize("content", ["not json", "{}", '[]', '{"schema_version": NaN}',
                                     '{"schema_version":1,"schema_version":2}'])
def test_parse_failures(content):
    result = candidate.parse_response(content, request_id="s", source_text="Synthetic.")
    assert result["label"] is None and result["first_clause_label"] is None


def test_wrong_identity_and_failed_request_are_not_scored():
    obj = example()
    result = candidate.parse_response(json.dumps(obj), request_id="different", source_text=obj["rule_record"]["source_text"])
    assert result["status"] == "source_binding_mismatch"
    assert result["first_clause_label"] is None
    assert parse(obj, request_ok=False)["label"] is None


def test_all_426_remain_in_denominator_including_missing_failed_and_null():
    obj = example()
    rows, responses, ids, old = [], {}, {}, {}
    for i in range(426):
        sid = f"synthetic_{i}"
        rows.append(data.Example(sid, obj["rule_record"]["source_text"], "permission"))
        ids[sid] = sid
        old[sid] = "permission"
        response = copy.deepcopy(obj)
        response["rule_record"].update(sample_id=sid, source_id=sid)
        responses[sid] = {"raw_content": json.dumps(response), "request_ok": True}
    responses.pop("synthetic_0")
    responses["synthetic_1"]["request_ok"] = False
    responses["synthetic_2"]["raw_content"] = "broken JSON"
    null_obj = json.loads(responses["synthetic_3"]["raw_content"])
    null_obj["sentence_modality"] = {"label": None, "evidence": [], "uncertainty": ["incomplete_input"]}
    responses["synthetic_3"]["raw_content"] = json.dumps(null_obj)
    report = candidate.evaluate_responses(rows, responses, ids, old)
    assert report["primary"]["n"] == 426
    assert report["primary"]["failures"] == 4
    assert report["primary"]["accuracy"] == 422 / 426
    assert report["primary"]["per_class"]["permission"]["fn"] == 4
    assert report["same_response_first_clause_diagnostic"]["failures"] == 3
    assert report["primary_vs_historical"] == {"corrected": 0, "regressed": 4}
    assert len(report["sentence_vs_first_clause_differences"]) == 1
    with pytest.raises(ValueError, match="membership"):
        candidate.evaluate_responses(rows, dict(responses, unknown={}), ids, old)
    with pytest.raises(ValueError, match="membership"):
        candidate.evaluate_responses(rows[:1], {}, {rows[0].sample_id: "s"}, {rows[0].sample_id: "permission"})


def test_request_sampling_and_target_identity_only():
    body = candidate.request_body("input_000001", "Synthetic target.", system="New system.", examples=[example()])
    parent = llm_se.request_body("local", "Synthetic target.")
    assert {k: v for k, v in body.items() if k != "messages"} == {k: v for k, v in parent.items() if k != "messages"}
    assert "sun_modality_" not in json.dumps(body)
    assert "Synthetic target." in body["messages"][1]["content"]


def test_prompt_assets_replace_conflicting_output_instructions():
    system = (candidate.PROMPT_DIR / "system_prompt.md").read_text(encoding="utf-8")
    guide = (candidate.PROMPT_DIR / "modality_guidance.md").read_text(encoding="utf-8")
    assert "Use exactly these top-level keys and no others" not in system
    assert "rule_record" in system and candidate.VERSION in system
    assert "Do not impose a universal priority" in guide
    assert "Never copy the sentence label to all clauses" in guide


def test_train_manifest_has_exact_four_replacements_and_keeps_protective_examples():
    manifest = candidate.read_json(candidate.PROMPT_DIR / "selection_manifest.json")
    rows = manifest["examples"]
    assert len(rows) == 22
    assert {r["parent_position"] for r in rows if r["replacement_of"]} == {4, 7, 15, 17}
    assert all(r["label"] == "definition" for r in rows if r["replacement_of"])
    old = candidate.read_json(ROOT / "prompts/sun_compat/modality_fewshot_v1/selection_manifest.json")["selections"]
    protected = {r["sample_id"] for r in old if r["label"] != "definition"}
    assert protected <= {r["sample_id"] for r in rows}


def test_offline_preparation_has_no_execute_mode():
    sys.path.insert(0, str(ROOT / "scripts"))
    import prepare_sun_modality_sentence_v1 as prep
    policy = candidate.read_json(prep.CONTRACT)
    assert policy["execute_authorized"] is False
    assert policy["planned_requests"] == 426 and policy["retries"] == 0
    with pytest.raises(ValueError, match="authorization"):
        prep.assert_offline_policy(dict(policy, execute_authorized=True))
