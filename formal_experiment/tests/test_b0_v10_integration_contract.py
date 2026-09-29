"""B0-R0-C1 B0-v10 integration contract regression test.

This test pins down the B0-R0 dependency-closure claim:

  * The b0_v10 package, sun_style/lexicon_v2_runtime, estg150_b0_development_v10,
    PROFILE_V10A, BRIDGE_REL, and the v10 development runner script can all be
    imported and their declared contract paths exist on disk.
  * The v10 runner's --help path works without starting CoreNLP, loading a
    checkpoint, or reading Layer E.
  * The audit keeps `b0_paper_faithful_components_present` as a PASS and
    `sun_stage2_baseline_not_paper_faithful` as a BLOCKER, regardless of
    whether components are detected in code. B0-R0 cannot lift the method-
    conformance blocker; only B0-R2 may set
    `method_conformance_status='verified_method_level_independent_reconstruction'`.

It is a pure offline / static contract test: it MUST NOT touch the 441MB
checkpoint, must NOT read data/gold, must NOT read data/development/human_review,
must NOT call any LLM/API, and must NOT require any network.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMAL = ROOT  # formal_experiment/
WORKSPACE = ROOT.parent  # workspace root
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _formal_path(*parts: str) -> Path:
    """Resolve a repo-relative path under formal_experiment/."""
    return FORMAL.joinpath(*parts)


# ---------------------------------------------------------------------------
# 1. Imports.
# ---------------------------------------------------------------------------


def test_actor_action_module_imports() -> None:
    from bpc_hybrid.b0_v10 import actor_action  # noqa: F401

    assert hasattr(actor_action, "extract_actors_actions_edges")
    assert hasattr(actor_action, "filter_actor_span")


def test_v10_runner_module_imports() -> None:
    from bpc_hybrid import estg150_b0_development_v10  # noqa: F401

    assert hasattr(estg150_b0_development_v10, "run_b0_batch_v10")
    assert hasattr(estg150_b0_development_v10, "build_canonical_record_v10")
    assert hasattr(estg150_b0_development_v10, "run_corenlp_batch_v10")
    assert hasattr(estg150_b0_development_v10, "BRIDGE_REL")
    assert hasattr(estg150_b0_development_v10, "EXTRACTION_ORDER")
    assert hasattr(estg150_b0_development_v10, "METHOD_ID")
    assert hasattr(estg150_b0_development_v10, "METHOD_VARIANT")


def test_v10_profile_constants() -> None:
    from bpc_hybrid.b0_v10.profile import PROFILE_V10A

    assert PROFILE_V10A.profile_id == "v10-A_scope_tregex_recall_recovery"
    assert PROFILE_V10A.s26_config_rel == "configs/models/sun_b0_s26_candidate_B_v1.json"
    assert (
        PROFILE_V10A.tregex_registry_rel
        == "resources/corenlp/sun_phrase_patterns_v3_enhanced.json"
    )
    assert PROFILE_V10A.tsurgeon_enabled is False


# ---------------------------------------------------------------------------
# 2. Versioned path existence.
# ---------------------------------------------------------------------------


def _workspace_path(*parts: str) -> Path:
    """Resolve a path that lives in formal_experiment/ (the audit, the
    config root, the runner script and the versioned contract files)."""
    return FORMAL.joinpath(*parts)


def test_profiled_paths_exist() -> None:
    from bpc_hybrid.b0_v10.profile import PROFILE_V10A
    from bpc_hybrid.estg150_b0_development_v10 import BRIDGE_REL

    s26 = _workspace_path(PROFILE_V10A.s26_config_rel)
    tregex = _workspace_path(PROFILE_V10A.tregex_registry_rel)
    bridge = _workspace_path(BRIDGE_REL)
    runtime = _workspace_path("configs/sun_corenlp_runtime.json")
    for p in (s26, tregex, bridge, runtime):
        assert p.is_file(), f"missing versioned B0-v10 path: {p}"


def test_v10_runner_script_exists() -> None:
    runner = _workspace_path("scripts/run_estg150_b0_enhanced_v10_development.py")
    assert runner.is_file()
    text = runner.read_text(encoding="utf-8")
    assert "DEFAULT_CONFIG" in text
    assert "estg150_b0_enhanced_s27_v10a.json" in text


def test_v10_default_config_exists_and_is_well_formed() -> None:
    cfg_path = _workspace_path("configs/models/estg150_b0_enhanced_s27_v10a.json")
    assert cfg_path.is_file()
    doc = json.loads(cfg_path.read_text(encoding="utf-8"))
    assert doc.get("schema_version") == "estg150_b0_enhanced_development@1.0.0"
    assert doc.get("task_id") == "S2.7-B0-ENHANCED-DEV"
    assert doc.get("claim_scope") == "development"
    assert doc.get("method", {}).get("method_id") in {"b0_enhanced_v10a", "b0_enhanced_v10"}
    assert doc.get("safety", {}).get("llm_api_called") is False
    assert doc.get("safety", {}).get("network_allowed") is False


# ---------------------------------------------------------------------------
# 3. Configs load through the runtime contract.
# ---------------------------------------------------------------------------


def test_s26_candidate_b_loads_via_load_s26_config() -> None:
    from bpc_hybrid.sun_style.sun_b0 import load_s26_config

    cfg = load_s26_config(
        _workspace_path("configs/models/sun_b0_s26_candidate_B_v1.json")
    )
    assert cfg["task_id"] == "S2.6"
    assert cfg["method_id"] == "sun_rule_only"
    extractor = cfg["phrase_extractor"]
    assert tuple(extractor["extraction_order"]) == (
        "modality",
        "condition",
        "constraint",
        "exception",
        "action",
        "actor",
    )
    assert extractor["inference_language"] == "en"
    assert cfg["classifier"]["inference_language"] == "de"
    safety = cfg["safety"]
    for locked in (
        "gold_read_or_modified",
        "llm_api_called",
        "network_allowed",
        "test_split_read_or_evaluated",
        "row_level_real_data_predictions_persisted",
    ):
        assert safety.get(locked) is False, f"S2.6 safety boundary relaxed: {locked}"
    assert safety.get("no_overwrite") is True


def test_corenlp_runtime_contract_loads_offline() -> None:
    """The CoreNLP runtime contract is a JSON document. It must load without
    starting any Java process or opening a network connection. External 482MB
    CoreNLP zip is NOT vendored in formal_experiment; that is documented as an
    external runtime prerequisite (vendored_in_formal_experiment=false)."""
    cfg_path = _workspace_path("configs/sun_corenlp_runtime.json")
    doc = json.loads(cfg_path.read_text(encoding="utf-8"))
    assert doc.get("schema_version") == "sun_corenlp_runtime_contract@1.0.0"
    runtime = doc["runtime"]
    assert runtime["corenlp_version"] == "4.5.10"
    assert runtime["home_environment_variable"] == "CORENLP_HOME"
    official = doc.get("official_distribution", {})
    assert official.get("vendored_in_formal_experiment") is False
    assert official.get("future_storage_policy") == (
        "external_local_runtime_only_not_committed"
    )


def test_tregex_pattern_registry_loads_offline() -> None:
    reg_path = _workspace_path("resources/corenlp/sun_phrase_patterns_v3_enhanced.json")
    assert reg_path.is_file()
    doc = json.loads(reg_path.read_text(encoding="utf-8"))
    assert doc.get("schema_version") == "sun_tregex_rule_registry@1.0.0"
    assert doc.get("language") == "en"
    # Pattern registry must declare its parser + parent lineage.
    parser = doc.get("parser", {})
    assert parser.get("name") == "Stanford CoreNLP"
    assert parser.get("tree_representation") == "constituency_parse"


# ---------------------------------------------------------------------------
# 4. v10 development runner --help must succeed without touching Gold,
#    Layer E, the 441MB checkpoint, or any network.
# ---------------------------------------------------------------------------


def test_v10_runner_help_succeeds_offline() -> None:
    runner = _workspace_path("scripts/run_estg150_b0_enhanced_v10_development.py")
    completed = subprocess.run(
        [sys.executable, str(runner), "--help"],
        cwd=WORKSPACE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout
    assert "Run EStG-150 B0 enhanced development evaluation" in completed.stdout
    # The help output must declare --runtime-home as required, which is
    # exactly what prevents any accidental execution.
    assert "--runtime-home" in completed.stdout


# ---------------------------------------------------------------------------
# 5. Audit semantics: components present is a PASS; method conformance was a
#    BLOCKER until the user-authorized B0-R2 gate flip (2026-08-04), which
#    clears the blocker by design (MASTER_PIPELINE 8.6 B0-R2 row).
# ---------------------------------------------------------------------------


def _codes(audit: dict, level: str) -> set[str]:
    return {item["code"] for item in audit["findings"][level]}


def test_audit_components_pass_and_method_conformance_blocker_cleared() -> None:
    from formal_experiment.audit import collect_project_audit

    audit = collect_project_audit()
    passes = _codes(audit, "passes")
    blockers = _codes(audit, "blockers")
    assert "b0_paper_faithful_components_present" in passes
    assert "sun_stage2_baseline_not_paper_faithful" not in blockers


def test_methods_json_sun_rule_only_verified_after_user_authorization() -> None:
    doc = json.loads(
        _workspace_path("configs/methods.json").read_text(encoding="utf-8")
    )
    methods = {m["id"]: m for m in doc["methods"]}
    sun_rule = methods.get("sun_rule_only")
    assert sun_rule is not None
    assert (
        sun_rule.get("method_conformance_status")
        == "verified_method_level_independent_reconstruction"
    )


def test_audit_blocker_message_cites_b0_r2_gate() -> None:
    from formal_experiment.audit import collect_project_audit

    audit = collect_project_audit()
    # After the user-authorized B0-R2 gate flip the blocker is cleared; the
    # methods.json note still cites the gate vocabulary for auditability.
    doc = json.loads(
        _workspace_path("configs/methods.json").read_text(encoding="utf-8")
    )
    sun_rule = {m["id"]: m for m in doc["methods"]}["sun_rule_only"]
    msg = sun_rule.get("notes", "")
    assert "method_conformance_status" in msg
    assert "B0-R2" in msg
    assert "verified_method_level_independent_reconstruction" in msg


# ---------------------------------------------------------------------------
# 6. Negative test: simulate the B0-R2 unlock by patching the in-memory
#    config and confirm the blocker is suppressed ONLY under the exact status
#    value. This proves the audit cannot be silenced by accident.
# ---------------------------------------------------------------------------


def test_blocker_is_lifted_only_under_exact_verified_status(tmp_path: Path) -> None:
    import formal_experiment.audit as audit_mod
    from formal_experiment.audit import collect_project_audit

    # Reload the audit so it picks up the patched config.
    real_load = audit_mod._load_json

    def _patched(path):
        result = real_load(path)
        if str(path).endswith("methods.json"):
            for m in result.get("methods", []):
                if m.get("id") == "sun_rule_only":
                    m["method_conformance_status"] = (
                        "verified_method_level_independent_reconstruction"
                    )
        return result

    audit_mod._load_json = _patched
    try:
        audit = collect_project_audit()
    finally:
        audit_mod._load_json = real_load
    blockers = _codes(audit, "blockers")
    # With the exact verified status, the method-conformance blocker is gone.
    assert "sun_stage2_baseline_not_paper_faithful" not in blockers
    # And the static component-presence PASS is still reported.
    passes = _codes(audit, "passes")
    assert "b0_paper_faithful_components_present" in passes


# ---------------------------------------------------------------------------
# 7. Negative test: arbitrary status strings do NOT lift the blocker.
# ---------------------------------------------------------------------------


def test_blocker_remains_for_arbitrary_status_strings() -> None:
    import formal_experiment.audit as audit_mod
    from formal_experiment.audit import collect_project_audit

    real_load = audit_mod._load_json

    def _patched(path):
        result = real_load(path)
        if str(path).endswith("methods.json"):
            for m in result.get("methods", []):
                if m.get("id") == "sun_rule_only":
                    m["method_conformance_status"] = "i_promise_it_works"
        return result

    audit_mod._load_json = _patched
    try:
        audit = collect_project_audit()
    finally:
        audit_mod._load_json = real_load
    blockers = _codes(audit, "blockers")
    assert "sun_stage2_baseline_not_paper_faithful" in blockers


# ---------------------------------------------------------------------------
# 8. B0-R1-A-C3 (2026-08-03): narrow .gitattributes line-ending pin and
#    manifest artifact integrity gate. These pin the contract so the
#    B0-R1-A~C3 development run's raw working-tree bytes match its
#    declared manifest hashes regardless of Windows CRLF checkout.
# ---------------------------------------------------------------------------


def test_gitattributes_pins_c3_output_to_text_eol_lf() -> None:
    attrs_path = _workspace_path(".gitattributes")
    assert attrs_path.is_file()
    text = attrs_path.read_text(encoding="utf-8")
    expected_rule = (
        "outputs/development/"
        "s27_estg150_b0_enhanced_v10a_r1a_c3_hist56d_v1/*.json text eol=lf"
    )
    assert expected_rule in text, (
        "C3 development output rule is missing or different from the narrow "
        f"pin: {expected_rule!r}"
    )


def test_gitattributes_has_no_broad_json_or_outputs_rule() -> None:
    text = _workspace_path(".gitattributes").read_text(encoding="utf-8")
    # The fix must not introduce broad rules that would renormalize
    # unrelated JSONs or the whole outputs tree. The 2026-07-31 Sun
    # modality rule is allowed; the new C3 rule is allowed; nothing else.
    # Only check the active rule lines, not the comments (which may
    # name the banned patterns as a warning).
    rules = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    # Each forbidden token must NOT appear as the leading path-glob of
    # any rule. We split on whitespace and check the first token only,
    # so the C3 rule's full path does not match ``outputs/development/*``
    # because its first token is a deeper path component.
    forbidden_path_globs = {
        "*.json",
        "outputs/**",
        "outputs/development",
        "outputs/development/",
        "outputs/development/*.json",
    }
    for rule in rules:
        head = rule.split()[0]
        assert head not in forbidden_path_globs, (
            f"broad/banned line-ending path-glob present: {head!r} in rule {rule!r}"
        )
    forbidden_attrs = {"text=auto", "text -auto"}
    for rule in rules:
        for token in rule.split()[1:]:
            assert token not in forbidden_attrs, (
                f"banned attribute token present: {token!r} in rule {rule!r}"
            )


def test_c3_manifest_four_artifacts_hash_match() -> None:
    """All four B0-R1-A-C3 artifacts (excluding manifest.json itself) must
    hash-match the manifest's declared raw SHA-256 in the current
    working tree. The C3 manifest does not bind its own SHA into
    ``artifacts`` (it is the source of truth for the other four)."""
    import hashlib

    manifest_path = _workspace_path(
        "outputs/development/"
        "s27_estg150_b0_enhanced_v10a_r1a_c3_hist56d_v1/manifest.json"
    )
    assert manifest_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = manifest.get("artifacts")
    assert isinstance(artifacts, dict) and artifacts, "artifacts must be non-empty object"
    expected_keys = {
        "attempts",
        "evaluation_all150",
        "evaluation_independent82",
        "sun_table8_any_overlap_diagnostic",
    }
    assert set(artifacts.keys()) >= expected_keys, (
        f"manifest missing C3 artifacts: missing={sorted(expected_keys - set(artifacts.keys()))}"
    )
    for key in sorted(expected_keys):
        entry = artifacts[key]
        rel = entry["path"]
        declared = entry["sha256"]
        full = manifest_path.parent / rel
        assert full.is_file(), f"missing C3 artifact: {full}"
        actual = hashlib.sha256(full.read_bytes()).hexdigest()
        assert actual == declared, (
            f"C3 raw SHA mismatch for {rel}: declared={declared} actual={actual}"
        )


def test_c3_manifest_development_status_unchanged() -> None:
    """The C3 manifest must still be flagged as development-only with
    formal_gold_published=False and a non-formal status. The fix must
    not silently promote the run to formal."""
    manifest = json.loads(
        (
            _workspace_path(
                "outputs/development/"
                "s27_estg150_b0_enhanced_v10a_r1a_c3_hist56d_v1/manifest.json"
            )
        ).read_text(encoding="utf-8")
    )
    assert manifest.get("claim_scope") == "development"
    assert manifest.get("is_formal_performance_result") is False
    assert manifest.get("safety", {}).get("formal_predictions_or_results_written") is False
    assert manifest.get("safety", {}).get("gold_read_only") is True
    assert manifest.get("safety", {}).get("llm_api_called") is False
    routes = manifest.get("route_boundaries", {})
    assert routes.get("formal_performance_result") is False
    assert routes.get("formal_gold_published") is False
    assert manifest.get("status") == "succeeded_development_not_formal"
