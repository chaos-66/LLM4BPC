"""Offline integrity and readiness audit for the formal experiment capsule.

Wave 1.1 \u00a78 additions:
- canonical Stage 2 prediction schema existence + loadability check
- D1/H1 prompt file existence + canonical-schema reference check
- prompt loader actually being used by the runners (no hardcoded
  SYSTEM_PROMPT in runner scripts)
- prompt few-shot fixtures passing the canonical validator
- formal-runner readiness gate: when route / methods are blocked,
  the formal runner must refuse to write to formal artifact dirs
- B0 still has no BERT-TextCNN / CoreNLP / Tregex \u2014 keep blocker
- event log report uses the actual JSONL record count, never a
  fabricated event_id
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from formal_experiment.paths import (
    CANONICAL_REVIEW_FILE,
    CANONICAL_REVIEW_SCHEMA,
    ESTG_150_MEMBERSHIP_HASHES,
    EXPERIMENT_CONTRACT,
    FORMAL_PREDICTIONS_DIR,
    FORMAL_REPORTS_DIR,
    FORMAL_RESULTS_DIR,
    FROZEN_GOLD_DIR,
    FROZEN_INPUT_DIR,
    HUMAN_CORRECTION_FILE,
    HUMAN_REVIEW_PACK,
    HUMAN_REVIEW_SCHEMA,
    METHODS_CONFIG,
    REPO_ROOT,
    SUN_ORIGINAL_REFERENCE_DIR,
    WINTER_2020_REFERENCE_DIR,
)
from formal_experiment.status import collect_status, formal_final_gate_conditions


REQUIRED_DOCS = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "MANIFEST.md",
    REPO_ROOT / "docs/MASTER_PIPELINE.md",
    REPO_ROOT / "docs/INDEX.md",
    REPO_ROOT / "docs/AGENT_RUNBOOK.md",
    REPO_ROOT / "docs/DIRECTORY_GUIDE.md",
    REPO_ROOT / "docs/FILE_CATALOG.md",
    REPO_ROOT / "docs/PROJECT_AUDIT.md",
    REPO_ROOT / "docs/AI_CHANGE_PROTOCOL.md",
    REPO_ROOT / "docs/ROUTE_LOCK.md",
    REPO_ROOT / "docs/HUMAN_GOLD_GUIDE.md",
    REPO_ROOT / "docs/EXPERIMENT_LOG.md",
    REPO_ROOT / "docs/EXPERIMENT_EVENTS.jsonl",
    REPO_ROOT / "_retired/README.md",
    REPO_ROOT / "_retired/MANIFEST.md",
    REPO_ROOT / "paper/README.md",
    REPO_ROOT / "paper/THESIS_DRAFT.md",
    REPO_ROOT / "paper/CLAIM_EVIDENCE_MATRIX.md",
    REPO_ROOT / "docs/ESTG150_DATA_MAP.md",
    REPO_ROOT / "data" / "development" / "human_review" / "ESTG150_REVIEW_WORKFLOW_V1.md",
    EXPERIMENT_CONTRACT,
    HUMAN_REVIEW_SCHEMA,
    CANONICAL_REVIEW_SCHEMA,
    REPO_ROOT / "configs" / "schemas" / "stage2_prediction.schema.json",
    REPO_ROOT / "src" / "bpc_hybrid" / "stage2_canonical.py",
    REPO_ROOT / "src" / "bpc_hybrid" / "prompt_loader.py",
    REPO_ROOT / "src" / "formal_experiment" / "sun_modality_gate.py",
    REPO_ROOT / "src" / "bpc_hybrid" / "sun_style" / "public_marker_lexicon.py",
    REPO_ROOT / "scripts" / "build_public_marker_lexicon.py",
    REPO_ROOT / "resources" / "lexicon" / "public_marker_sources_en_v1.json",
    REPO_ROOT / "resources" / "lexicon" / "public_marker_lexicon_en_v1.manifest.json",
    REPO_ROOT / "prompts" / "sun_compat" / "direct_llm_sun_record_prompt.md",
    REPO_ROOT / "prompts" / "sun_compat" / "rule_first_llm_fallback_prompt.md",
    CANONICAL_REVIEW_FILE,
    HUMAN_CORRECTION_FILE,
    ESTG_150_MEMBERSHIP_HASHES,
    REPO_ROOT / "scripts" / "validate_canonical_review.py",
    REPO_ROOT / "scripts" / "validate_human_correction.py",
    REPO_ROOT / "scripts" / "estg150_review_tool.py",
    REPO_ROOT / "scripts" / "build_estg150_review_layers.py",
    REPO_ROOT / "data" / "development" / "human_review" / "estg_150_translation_en_v1.jsonl",
    REPO_ROOT / "data" / "development" / "human_review" / "estg_150_llm_six_element_candidates_v1.jsonl",
    REPO_ROOT / "data" / "development" / "human_review" / "estg_150_review_aids_zh_v1.jsonl",
)


@dataclass
class JsonlReport:
    path: Path
    exists: bool = False
    total_lines: int = 0
    valid_json: int = 0
    invalid_json: int = 0
    invalid_lines: list[int] = field(default_factory=list)
    duplicate_ids: list[str] = field(default_factory=list)
    ids: set[str] = field(default_factory=set)
    records: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": _relative(self.path), "exists": self.exists,
            "total_lines": self.total_lines, "valid_json": self.valid_json,
            "invalid_json": self.invalid_json, "invalid_lines": self.invalid_lines,
            "unique_ids": len(self.ids), "duplicate_ids": self.duplicate_ids,
        }


def _relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def inspect_jsonl(path: Path) -> JsonlReport:
    report = JsonlReport(path=path, exists=path.exists())
    if not path.exists():
        return report
    duplicates: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            report.total_lines += 1
            try:
                row = json.loads(raw)
            except json.JSONDecodeError:
                report.invalid_json += 1
                report.invalid_lines.append(line_number)
                continue
            if not isinstance(row, dict):
                report.invalid_json += 1
                report.invalid_lines.append(line_number)
                continue
            report.valid_json += 1
            report.records.append(row)
            sample_id = row.get("sample_id")
            if isinstance(sample_id, str) and sample_id:
                if sample_id in report.ids:
                    duplicates.add(sample_id)
                report.ids.add(sample_id)
    report.duplicate_ids = sorted(duplicates)
    return report


def _add(findings: dict[str, list[dict[str, str]]], level: str, code: str, message: str) -> None:
    findings[level].append({"code": code, "message": message})


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _formal_capsule_methods() -> set[str]:
    """Method arms with published formal capsules (predictions+results).

    Coverage is derived from per-arm manifests under outputs/reports
    (pattern <arm>_v*.manifest.json carrying method_id); a single file in
    data/predictions is NOT treated as the complete three-method capsule.
    """
    methods: set[str] = set()
    pred_dir = FORMAL_PREDICTIONS_DIR
    if not pred_dir.exists():
        return methods
    for arm_dir in pred_dir.iterdir():
        if not arm_dir.is_dir():
            continue
        for manifest_candidate in (FORMAL_REPORTS_DIR / f"{arm_dir.name}.manifest.json",):
            if manifest_candidate.exists():
                manifest = _load_json(manifest_candidate)
                mid = manifest.get("method_id")
                if isinstance(mid, str) and mid:
                    methods.add(mid)
    return methods


def _load_release_verifier() -> Any | None:
    """Load the independent release verifier script as a module (no package
    import cycle: the verifier lives under scripts/ and imports nothing from
    formal_experiment)."""
    try:
        import importlib.util
        path = REPO_ROOT / "scripts" / "verify_formal_benchmark_release_v2.py"
        spec = importlib.util.spec_from_file_location(
            "formal_benchmark_release_verifier", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:  # pragma: no cover - defensive
        return None


def _load_adjudication_verifier() -> Any | None:
    """Load the incremental S1.5 human-adjudication verifier (script module)."""
    try:
        import importlib.util
        path = REPO_ROOT / "scripts" / "verify_stage1_human_adjudication.py"
        spec = importlib.util.spec_from_file_location(
            "stage1_human_adjudication_verifier", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:  # pragma: no cover - defensive
        return None


def _load_gold_verifier() -> Any | None:
    """Load the Stage 1 Process Gold publication verifier (script module)."""
    try:
        import importlib.util
        path = REPO_ROOT / "scripts" / "verify_stage1_process_gold.py"
        spec = importlib.util.spec_from_file_location(
            "stage1_process_gold_verifier", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:  # pragma: no cover - defensive
        return None


def _load_formal_evaluation_verifier() -> Any | None:
    """Load the S1.6 formal evaluation capsule verifier (script module)."""
    try:
        import importlib.util
        path = REPO_ROOT / "scripts" / "verify_stage1_formal_evaluation.py"
        spec = importlib.util.spec_from_file_location(
            "stage1_formal_evaluation_verifier", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:  # pragma: no cover - defensive
        return None


def _load_p2_verifier() -> Any | None:
    """Load the S1.3 P2 lock verifier (script module)."""
    try:
        import importlib.util
        path = REPO_ROOT / "scripts" / "verify_stage1_p2.py"
        spec = importlib.util.spec_from_file_location(
            "stage1_p2_verifier", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:  # pragma: no cover - defensive
        return None


def _load_prediction_verifier() -> Any | None:
    """Load the S1.6 formal predictions verifier (script module)."""
    try:
        import importlib.util
        path = REPO_ROOT / "scripts" / "verify_stage1_predictions.py"
        spec = importlib.util.spec_from_file_location(
            "stage1_predictions_verifier", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:  # pragma: no cover - defensive
        return None


def _load_verifier_script(name: str, filename: str) -> Any | None:
    """Load an independent verifier script module by filename."""
    try:
        import importlib.util
        path = REPO_ROOT / "scripts" / filename
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:  # pragma: no cover - defensive
        return None


def _valid_event_log(path: Path) -> tuple[int, list[int]]:
    report = inspect_jsonl(path)
    return report.valid_json, report.invalid_lines


# ---------------------------------------------------------------------------
# Manifest artifact integrity gate (B0-R1-A-C3, 2026-08-03).
#
# Verifies that a development-only Stage-2 manifest's declared artifact
# entries (relative `path` + 64-bit sha256) still match the actual
# working-tree raw bytes of those artifacts. This is a pure read-only
# helper:
#
#   * manifest must be a JSON object;
#   * `artifacts` must be a JSON object;
#   * every entry must have a relative `path` (no absolute, no `..`,
#     no path that escapes the manifest's parent directory);
#   * every entry must declare a 64-character lowercase hex sha256;
#   * the file at the resolved path must exist, be a regular file, and
#     its raw bytes must hash to the declared sha256.
#
# The helper is single-purpose and unit-testable. It does NOT read
# `.env`, Gold, Layer E, or Layer B/C/D, and it never writes anything.
# It returns a structured list of `{code, message, artifact}` errors
# rather than printing file contents.
# ---------------------------------------------------------------------------

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_PASS_CODE = "b0_r1a_c3_development_artifacts_verified"
_FAIL_CODE = "b0_r1a_c3_development_artifact_integrity_failed"


@dataclass
class ManifestArtifactError:
    code: str
    artifact: str
    message: str

    def to_finding(self) -> dict[str, str]:
        return {"code": self.code, "artifact": self.artifact, "message": self.message}


def _resolve_artifact_path(manifest_path: Path, declared: str) -> Path:
    """Resolve a declared relative artifact path against the manifest's
    parent directory and refuse anything that escapes it.
    """

    candidate = (manifest_path.parent / declared).resolve()
    base = manifest_path.parent.resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError(
            f"artifact path {declared!r} resolves outside manifest directory {base}"
        ) from exc
    return candidate


def verify_manifest_artifact_integrity(manifest_path: Path) -> list[ManifestArtifactError]:
    """Return a (possibly empty) list of integrity errors for a manifest.

    The helper never raises on integrity problems; it converts each
    problem into a structured ``ManifestArtifactError`` so the audit
    caller can decide how to surface it. Real exceptions are only
    raised for programmer errors (e.g. ``manifest_path`` is not a
    Path).
    """

    errors: list[ManifestArtifactError] = []
    if not manifest_path.is_file():
        return [
            ManifestArtifactError(
                code=_FAIL_CODE,
                artifact=str(manifest_path),
                message=f"manifest not found or not a regular file: {manifest_path}",
            )
        ]

    try:
        raw = manifest_path.read_bytes()
    except OSError as exc:
        return [
            ManifestArtifactError(
                code=_FAIL_CODE,
                artifact=str(manifest_path),
                message=f"manifest could not be read: {exc!r}",
            )
        ]

    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [
            ManifestArtifactError(
                code=_FAIL_CODE,
                artifact=str(manifest_path),
                message=f"manifest is not valid UTF-8 JSON: {exc!r}",
            )
        ]

    if not isinstance(doc, dict):
        return [
            ManifestArtifactError(
                code=_FAIL_CODE,
                artifact=str(manifest_path),
                message="manifest must be a JSON object at the top level",
            )
        ]

    artifacts = doc.get("artifacts")
    if not isinstance(artifacts, dict):
        return [
            ManifestArtifactError(
                code=_FAIL_CODE,
                artifact=str(manifest_path),
                message="manifest.artifacts must be a JSON object",
            )
        ]

    for key, entry in artifacts.items():
        artifact_label = f"{manifest_path.name}#artifacts.{key}"
        if not isinstance(entry, dict):
            errors.append(
                ManifestArtifactError(
                    code=_FAIL_CODE,
                    artifact=artifact_label,
                    message="artifact entry must be a JSON object",
                )
            )
            continue
        rel_path = entry.get("path")
        declared_sha = entry.get("sha256")
        if not isinstance(rel_path, str) or not rel_path:
            errors.append(
                ManifestArtifactError(
                    code=_FAIL_CODE,
                    artifact=artifact_label,
                    message="artifact entry must declare a non-empty string `path`",
                )
            )
            continue
        if Path(rel_path).is_absolute():
            errors.append(
                ManifestArtifactError(
                    code=_FAIL_CODE,
                    artifact=artifact_label,
                    message=f"artifact path must be relative (got absolute {rel_path!r})",
                )
            )
            continue
        try:
            resolved = _resolve_artifact_path(manifest_path, rel_path)
        except ValueError as exc:
            errors.append(
                ManifestArtifactError(
                    code=_FAIL_CODE,
                    artifact=artifact_label,
                    message=str(exc),
                )
            )
            continue
        if not isinstance(declared_sha, str) or not _SHA256_RE.match(declared_sha):
            errors.append(
                ManifestArtifactError(
                    code=_FAIL_CODE,
                    artifact=artifact_label,
                    message=(
                        "artifact sha256 must be a 64-character lowercase hex string; "
                        f"got {declared_sha!r}"
                    ),
                )
            )
            continue
        if not resolved.exists() or not resolved.is_file():
            errors.append(
                ManifestArtifactError(
                    code=_FAIL_CODE,
                    artifact=artifact_label,
                    message=f"artifact file missing: {resolved}",
                )
            )
            continue
        try:
            data = resolved.read_bytes()
        except OSError as exc:
            errors.append(
                ManifestArtifactError(
                    code=_FAIL_CODE,
                    artifact=artifact_label,
                    message=f"artifact could not be read: {exc!r}",
                )
            )
            continue
        actual_sha = hashlib.sha256(data).hexdigest()
        if actual_sha != declared_sha:
            errors.append(
                ManifestArtifactError(
                    code=_FAIL_CODE,
                    artifact=artifact_label,
                    message=(
                        f"sha256 mismatch for {rel_path}: declared={declared_sha} "
                        f"actual={actual_sha} (file bytes={len(data)})"
                    ),
                )
            )
            continue
    return errors


def _git_check(args: list[str]) -> bool | None:
    completed = subprocess.run(
        ["git", *args], cwd=REPO_ROOT.parent, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, check=False,
    )
    if completed.returncode == 0:
        return True
    if completed.returncode == 1:
        return False
    return None


def _meaningful_count(path: Path) -> int:
    """Count real files recursively (subdirectories like data/gold/stage2/ must
    count their contents)."""
    if not path.exists():
        return 0
    return sum(
        1 for item in path.rglob("*")
        if item.is_file() and item.name != ".gitkeep"
    )


def _review_structure_errors(report: JsonlReport) -> list[str]:
    errors: list[str] = []
    required = {"schema_version", "sample_id", "source", "text_review", "clauses", "annotation_review", "do_not_auto_score"}
    for index, row in enumerate(report.records, 1):
        missing = required - set(row)
        if missing:
            errors.append(f"row {index}: missing {sorted(missing)}")
            continue
        if row.get("schema_version") != "1.0.0" or row.get("do_not_auto_score") is not True:
            errors.append(f"row {index}: contract markers invalid")
        source = row.get("source")
        if not isinstance(source, dict) or not source.get("source_text_de_ocr") or not source.get("candidate_text_en"):
            errors.append(f"row {index}: source text missing")
        if not isinstance(row.get("clauses"), list):
            errors.append(f"row {index}: clauses must be an array")
    return errors


def collect_project_audit() -> dict[str, Any]:
    status = collect_status()
    findings: dict[str, list[dict[str, str]]] = {"errors": [], "blockers": [], "warnings": [], "passes": []}

    missing_docs = [_relative(path) for path in REQUIRED_DOCS if not path.exists()]
    if missing_docs:
        _add(findings, "errors", "missing_canonical_docs", f"Missing: {missing_docs}")
    else:
        _add(findings, "passes", "canonical_docs_present", "Agent contract, route, review guide, schemas, and audit documents are present.")

    event_count, invalid_events = _valid_event_log(REPO_ROOT / "docs/EXPERIMENT_EVENTS.jsonl")
    if not event_count or invalid_events:
        _add(findings, "errors", "audit_event_log_invalid", f"valid={event_count}, invalid lines={invalid_events}")
    else:
        _add(findings, "passes", "audit_event_log_valid", f"Append-only event log contains {event_count} valid event(s).")

    contract = _load_json(EXPERIMENT_CONTRACT)
    route = contract.get("route", {})
    dataset = contract.get("stage2_dataset", {})
    route_is_safe = (
        route.get("exact_reproduction") is False
        and route.get("methodological_source_of_truth")
        and route.get("claim")
    )
    if not route_is_safe:
        _add(findings, "errors", "route_contract_invalid", "Reconstruction route is missing its source of truth or overclaims exact reproduction.")
    elif route.get("status") == "locked":
        _add(findings, "passes", "reconstruction_route_locked", "Final-version Sun 2024 reconstruction route is locked with an explicit non-exact claim boundary.")
    else:
        _add(findings, "blockers", "final_version_route_alignment_pending", "Route v2 is intentionally reopened until the final published method and assets are reconciled.")

    phrase_dataset = dataset.get("phrase_dataset", {})
    sun_modality_gate = status.get("sun_modality_gate", {})
    if dataset.get("status") == "locked_for_human_review" and phrase_dataset.get("target_size") == 150:
        _add(findings, "passes", "stage2_dataset_route_locked", "Official-data-aligned Stage 2 route is locked for human review.")
    elif dataset.get("status") == "reopened_modality_verified_pending_phrase_gold_freeze_and_route_relock" and phrase_dataset.get("target_size") == 150:
        _add(
            findings,
            "blockers",
            "stage2_dataset_route_relock_pending",
            "Sun modality development data are verified, but the top-level Stage 2 data route is not re-locked; the independently reconstructed phrase Gold is not frozen and its separate human-review/publication gates remain incomplete.",
        )
    else:
        _add(findings, "errors", "stage2_dataset_contract_invalid", "Stage 2 dataset route has an unrecognized status or target size.")

    if sun_modality_gate.get("ready") is True:
        _add(
            findings,
            "passes",
            "sun_modality_dataset_verified",
            "Sun modality development dataset verified: source=2833, analysis=2831, train/dev/test=1985/420/426, quarantine=2; license remains unknown_pending_confirmation and redistribution is forbidden.",
        )
    else:
        gate_blockers = sun_modality_gate.get("blockers", [])
        _add(
            findings,
            "errors",
            "sun_modality_dataset_gate_failed",
            "Sun modality development data gate failed closed: "
            f"{gate_blockers[:8]}",
        )

    public_marker_gate = status.get("public_marker_gate", {})
    if public_marker_gate.get("ready") is True:
        counts = public_marker_gate.get("category_counts", {})
        _add(
            findings,
            "passes",
            "public_marker_lexicon_verified",
            "S2.3 public marker lexicon verified offline: "
            f"language=en, counts={counts}, extensions=0; development-only, "
            "no training/evaluation and not activated for S2.4+.",
        )
    else:
        _add(
            findings,
            "errors",
            "public_marker_lexicon_gate_failed",
            "S2.3 public marker lexicon gate failed closed: "
            f"{public_marker_gate.get('blockers', [])[:8]}",
        )

    # Stage 1 gates (S1.1-S1.6 + S3.1 GDPR7 membership). Restored from
    # the 56d2b03 checkpoint and re-bound 2026-08-08; findings are
    # converted from the status layer exactly as in the checkpoint.
    stage1_gate = status.get("stage1_structural_gate", {})
    if stage1_gate.get("ready") is True:
        _add(
            findings,
            "passes",
            "stage1_structural_process_record_verified",
            "S1.1/S1.2/S1.4 verified the canonical Process Record v1 schema, "
            "deterministic BPMN activity/event/gateway/flow/lane/pool parsing, direct "
            "and transitive control flow, activity order, branch/parallel classification, "
            "cycle detection, and unreachable-node accounting on two synthetic BPMN "
            "fixtures. No label semantics, human Gold, formal BPMN, network, LLM, or "
            "performance evaluation was used.",
        )
    else:
        _add(
            findings,
            "blockers",
            "stage1_structural_process_record_not_verified",
            "S1.1/S1.2/S1.4 structural Process Record gate failed closed: "
            f"{stage1_gate.get('errors', [])[:6]}",
        )

    stage1_label_gate = status.get("stage1_label_semantics_gate", {})
    if stage1_label_gate.get("ready") is True:
        _add(
            findings,
            "passes",
            "stage1_label_semantics_p0_p1_verified",
            "S1.3 verified two deterministic label baselines on synthetic BPMN: "
            "P0 preserves raw activity/lane labels without actor/action/object inference; "
            "P1 uses one unambiguous lane label as the actor surface and a fixed first-token/"
            "remainder split for action/business-object surfaces. Empty, punctuation-only, "
            "single-token, no-lane, and ambiguous-lane cases fail or report explicitly. No "
            "lemmatizer, tagger, learned model, human Gold, formal BPMN, network, LLM, or "
            "performance evaluation was used.",
        )
    else:
        _add(
            findings,
            "blockers",
            "stage1_label_semantics_p0_p1_not_verified",
            "S1.3 P0/P1 label-semantics gate failed closed: "
            f"{stage1_label_gate.get('errors', [])[:6]}",
        )

    stage1_annotation_gate = status.get("stage1_annotation_gate", {})
    if stage1_annotation_gate.get("protocol_ready") is True:
        _add(
            findings,
            "passes",
            "stage1_annotation_protocol_verified",
            "S1.5 verified a blank human-annotation schema, exact BPMN/Process-Record "
            "source binding, activity label/lane context, three-field review states, "
            "and fail-closed freeze summaries on one synthetic process with 6 activities "
            "and 18 unresolved label fields. No candidate value was copied into Gold; "
            "formal membership is reported by the separate GDPR7 gate.",
        )
    else:
        _add(
            findings,
            "blockers",
            "stage1_annotation_protocol_not_verified",
            "S1.5 annotation protocol failed closed: "
            f"{stage1_annotation_gate.get('errors', [])[:6]}",
        )

    stage1_membership_gate = status.get("stage1_membership_gate", {})
    if stage1_membership_gate.get("membership_ready") is True:
        summary = stage1_membership_gate.get("annotation_summary", {})
        _add(
            findings,
            "passes",
            "stage1_formal_bpmn_membership_locked",
            "S1.5/S3.1 locked seven byte-exact Winter-provenance GDPR BPMN files as "
            "the shared all-seven extension membership. All seven parsed into unique "
            "dataset-level Process Records; the formal annotation input has "
            f"{summary.get('records', 0)} records and {summary.get('label_fields', 0)} "
            "blank label fields. This is not Sun's unidentified original four-model set, "
            "and no human Gold or performance result was created.",
        )
    else:
        _add(
            findings,
            "blockers",
            "stage1_formal_bpmn_membership_not_promoted",
            "S1.5/S3.1 formal GDPR7 membership gate failed closed: "
            f"{stage1_membership_gate.get('errors', [])[:6]}",
        )

    stage1_evaluator_gate = status.get("stage1_evaluator_gate", {})
    if stage1_evaluator_gate.get("evaluator_ready") is True:
        _add(
            findings,
            "passes",
            "stage1_evaluator_contract_verified",
            "S1.6 verified exact method/process membership, eight structural set "
            "components, actor/action/business-object exact-value P/R/F1, triple "
            "accuracy, coverage, and terminal/invalid denominators on one synthetic "
            "reference. The constants are not human Gold or formal performance; formal "
            "scope remains refused until S1.5 membership and Gold are ready.",
        )
    else:
        _add(
            findings,
            "blockers",
            "stage1_evaluator_contract_not_verified",
            "S1.6 evaluator contract failed closed: "
            f"{stage1_evaluator_gate.get('errors', [])[:6]}",
        )

    supplement = contract.get("official_supplement", {})
    stage3_archive = supplement.get("stage3_input_archive", {})
    if (
        supplement.get("landing_page") == "https://archive.org/details/input-2"
        and stage3_archive.get("effective_file_count") == 57
        and stage3_archive.get("local_hash_result")
    ):
        _add(findings, "passes", "official_sun_supplement_identified", "Sun's official Archive.org supplement is recorded; all 57 Stage 3 input files were hash-matched to the mentor/Winter copies.")
    else:
        _add(findings, "errors", "official_sun_supplement_missing", "Official Sun dataset provenance or the verified Stage 3 input match is missing.")

    if WINTER_2020_REFERENCE_DIR.exists() and not (REPO_ROOT.parent / "references/sun_program").exists():
        _add(findings, "passes", "winter_reference_correctly_named", "The Winter 2020 reference is separated from the Sun 2024 reconstruction.")
    else:
        _add(findings, "errors", "reference_identity_ambiguous", "Winter/Sun reference directory naming is ambiguous.")
    if not SUN_ORIGINAL_REFERENCE_DIR.exists():
        _add(findings, "warnings", "sun_original_code_unavailable", "Sun 2024 original code is unavailable; exact-reproduction claims remain forbidden.")

    review = inspect_jsonl(HUMAN_REVIEW_PACK)
    review_errors = _review_structure_errors(review)
    if review.invalid_json or review.duplicate_ids or review_errors or review.valid_json != 150 or len(review.ids) != 150:
        _add(findings, "errors", "human_review_pack_invalid", f"records={review.valid_json}, unique={len(review.ids)}, first_errors={review_errors[:3]}")
    else:
        _add(findings, "passes", "human_review_pack_structurally_valid", "Legacy blank review pack has 150 unique records, full source/translation context, and no auto-filled Gold.")
        if dataset.get("status") != "locked_for_human_review":
            _add(findings, "warnings", "legacy_review_pack_not_formal",
                 "Legacy review pack is retired as editing surface (kept as provenance). "
                 "Active editing surface is "
                 "data/development/human_review/estg_150_human_correction_v1.json "
                 "(v2 LLM-assisted workflow). The v1 canonical_review_v1.json is "
                 "itself retired as workflow draft and not edited any more.")

    # Canonical review file (v1 workflow, retired as editing surface
    # but still kept as provenance). v2 human_correction file is the
    # active editing surface; we report both.
    canonical = status["human_review"]
    if not CANONICAL_REVIEW_FILE.exists():
        _add(findings, "errors", "canonical_review_file_missing",
             f"Canonical review file missing: {CANONICAL_REVIEW_FILE}")
    else:
        if canonical.get("format_valid"):
            _add(findings, "passes", "canonical_review_format_valid",
                 f"Canonical review (v1, retired as editing surface, kept as provenance): "
                 f"150 records, IDs unique, raw_de hashes match, schema_version pinned; "
                 f"text_approved={canonical.get('text_approved')}/150, "
                 f"annotation_reviewed={canonical.get('annotation_reviewed')}/150, "
                 f"freeze_ready={canonical.get('freeze_ready')}.")
        else:
            _add(findings, "errors", "canonical_review_format_invalid",
                 f"Canonical review file is not format-valid: "
                 f"records={canonical.get('records')}, "
                 f"unique_ids={canonical.get('unique_ids')}.")

    # v2 human_correction file is the ACTIVE editing surface.
    human_correction = status.get("human_correction_v2") or {}
    if not HUMAN_CORRECTION_FILE.exists():
        _add(findings, "errors", "human_correction_v2_missing",
             f"v2 human_correction file missing: {HUMAN_CORRECTION_FILE}")
    else:
        if human_correction.get("format_valid"):
            # The "six element" display now shows BOTH per-field and
            # per-record counters so the denominator 150 (records) is
            # never confused with 900 (6 fields * 150 records).
            n_ft = human_correction.get("n_field_decisions_total", 0)
            n_fu = human_correction.get("n_field_decisions_unreviewed", 0)
            n_fr = human_correction.get("n_field_decisions_resolved", 0)
            n_inc = human_correction.get("n_records_incomplete", 0)
            n_ok = human_correction.get("n_records_fully_decided", 0)
            _add(findings, "passes", "human_correction_v2_format_valid",
                 f"Human_correction (v2, LLM-assisted editing surface): "
                 f"{human_correction.get('records')} records; "
                 f"approved_text_en={human_correction.get('n_approved_en')}/150, "
                 f"translation_unreviewed={human_correction.get('n_translation_unreviewed')}/150, "
                 f"six_element_decisions_unreviewed={n_fu}/{n_ft} (6 fields x 150 records), "
                 f"six_element_decisions_resolved={n_fr}/{n_ft}, "
                 f"six_element_records_incomplete={n_inc}/150, "
                 f"six_element_records_fully_decided={n_ok}/150, "
                 f"reviewed={human_correction.get('n_reviewed', 0)}/150, "
                 f"adjudicated={human_correction.get('n_adjudicated', 0)}/150, "
                 f"review_ready={human_correction.get('review_ready')}, "
                 f"freeze_ready={human_correction.get('freeze_ready')}.")
        else:
            _add(findings, "errors", "human_correction_v2_format_invalid",
                 f"Human_correction v2 file is not format-valid: "
                 f"records={human_correction.get('records')}, "
                 f"errors={human_correction.get('format_error_messages', human_correction.get('format_errors', []))[:3]}.")

    # Layer D (Chinese aid) — read the active path from the
    # configuration file. The v1 file remains the
    # all-null placeholder provenance and is NEVER overwritten
    # by the audit. The audit decides which warning/pass to emit
    # based on `configs/estg150_layer_d.json` `active_path`:
    #
    #   * active_path == placeholder_path (v1): emit the
    #     `review_aids_zh_not_generated` warning (existing
    #     behavior). v1 is all null; the user has not yet
    #     authorized a real LLM run.
    #   * active_path == filled_path (v2): verify v2 is
    #     complete (150/150 non-null text_zh and
    #     back_translation_en, model non-empty, prompt_sha256
    #     non-empty, every record traceable to a run_id). If
    #     complete, emit a `review_aids_zh_v2_active` pass and
    #     suppress the warning. If incomplete, emit a
    #     `review_aids_zh_v2_incomplete` error (this is the
    #     switch-to-v2 rule from configs/estg150_layer_d.json).
    #   * active_path == something else: emit an
    #     `review_aids_zh_active_path_unknown` error.
    layer_d_config_path = REPO_ROOT / "configs" / "estg150_layer_d.json"
    if layer_d_config_path.exists():
        try:
            ld_cfg = json.loads(layer_d_config_path.read_text(encoding="utf-8"))
            active_rel = ld_cfg.get("active_path", "")
            placeholder_rel = ld_cfg.get("placeholder_path", "")
            filled_rel = ld_cfg.get("filled_path", "")
            active_path = (REPO_ROOT / active_rel).resolve() if active_rel else None
            placeholder_path = (REPO_ROOT / placeholder_rel).resolve() if placeholder_rel else None
            filled_path = (REPO_ROOT / filled_rel).resolve() if filled_rel else None
            if active_path is None or not active_path.exists():
                _add(findings, "errors", "review_aids_zh_active_path_missing",
                     f"Layer D config declares active_path={active_rel!r} but the file does not exist.")
            elif active_path == placeholder_path:
                # Existing behavior: all null, user has not yet authorized.
                if active_path.exists():
                    try:
                        all_null = True
                        n = 0
                        with active_path.open("r", encoding="utf-8") as f:
                            for line in f:
                                if not line.strip():
                                    continue
                                n += 1
                                r = json.loads(line)
                                if r.get("text_zh") is not None or r.get("back_translation_en") is not None:
                                    all_null = False
                                    break
                        if all_null and n == 150:
                            _add(findings, "warnings", "review_aids_zh_not_generated",
                                 "Layer D (Chinese aid) is not_generated for all 150 records: "
                                 "text_zh=null, back_translation_en=null, model=null, "
                                 "prompt_sha256=null, aid_source=pending_authorized_llm_call. "
                                 "Chinese-aided review workflow is NOT available until the "
                                 "user authorizes a real LLM call (see "
                                 "docs/LLM_BUDGET_PROPOSAL_2026-07-12.md for the design draft). "
                                 "Until then, the review tool shows a placeholder banner and "
                                 "never fabricates Chinese / back-translation content. "
                                 "The 150 sample_ids are the SAME as Layer E's; v2 will not be a "
                                 "second 150.")
                    except (OSError, json.JSONDecodeError):
                        pass
            elif active_path == filled_path:
                # v2 is active; check completeness
                try:
                    n_text_zh_ok = 0
                    n_back_ok = 0
                    n_model_ok = 0
                    n_prompt_ok = 0
                    n_run_id_ok = 0
                    n = 0
                    with active_path.open("r", encoding="utf-8") as f:
                        for line in f:
                            if not line.strip():
                                continue
                            n += 1
                            r = json.loads(line)
                            if isinstance(r.get("text_zh"), str) and r["text_zh"].strip():
                                n_text_zh_ok += 1
                            if isinstance(r.get("back_translation_en"), str) and r["back_translation_en"].strip():
                                n_back_ok += 1
                            if r.get("model"):
                                n_model_ok += 1
                            if r.get("prompt_sha256"):
                                n_prompt_ok += 1
                            if r.get("run_id"):
                                n_run_id_ok += 1
                    if n == 150 and n_text_zh_ok == 150 and n_back_ok == 150 and \
                       n_model_ok == 150 and n_prompt_ok == 150 and n_run_id_ok == 150:
                        _add(findings, "passes", "review_aids_zh_v2_active",
                             f"Layer D v2 (filled Chinese aid) is ACTIVE and complete: "
                             f"text_zh={n_text_zh_ok}/150, back_translation_en={n_back_ok}/150, "
                             f"model={n_model_ok}/150, prompt_sha256={n_prompt_ok}/150, "
                             f"run_id={n_run_id_ok}/150. v2 lives on the SAME 150 sample_ids "
                             f"as Layer E; the v1 placeholder provenance is preserved.")
                    else:
                        _add(findings, "errors", "review_aids_zh_v2_incomplete",
                             f"Layer D config declares active_path=v2 but the v2 file is "
                             f"INCOMPLETE: records={n}/150, text_zh={n_text_zh_ok}/150, "
                             f"back_translation_en={n_back_ok}/150, model={n_model_ok}/150, "
                             f"prompt_sha256={n_prompt_ok}/150, run_id={n_run_id_ok}/150. "
                             f"The switch-to-v2 rule in configs/estg150_layer_d.json requires "
                             f"150/150 on every field. Re-run scripts/validate_layer_d_v2.py "
                             f"and re-authorize the run before switching back to v1.")
                except (OSError, json.JSONDecodeError) as e:
                    _add(findings, "errors", "review_aids_zh_v2_unreadable",
                         f"Layer D v2 active file {active_path} could not be read: {e!r}")
            else:
                _add(findings, "errors", "review_aids_zh_active_path_unknown",
                     f"Layer D config active_path={active_rel!r} is neither the v1 placeholder "
                     f"nor the v2 filled path. The audit refuses to guess. Fix "
                     f"configs/estg150_layer_d.json.")
        except (OSError, json.JSONDecodeError) as e:
            _add(findings, "errors", "review_aids_zh_config_unreadable",
                 f"configs/estg150_layer_d.json could not be read: {e!r}")
    else:
        # No config file: fall back to the original v1-only check.
        zh_aid_path = REPO_ROOT / "data" / "development" / "human_review" / "estg_150_review_aids_zh_v1.jsonl"
        if zh_aid_path.exists():
            try:
                with zh_aid_path.open("r", encoding="utf-8") as f:
                    all_null = True
                    n = 0
                    for line in f:
                        if not line.strip():
                            continue
                        n += 1
                        r = json.loads(line)
                        if r.get("text_zh") is not None or r.get("back_translation_en") is not None:
                            all_null = False
                            break
                if all_null and n == 150:
                    _add(findings, "warnings", "review_aids_zh_not_generated",
                         "Layer D (Chinese aid) is not_generated for all 150 records (v1 placeholder check).")
            except (OSError, json.JSONDecodeError):
                pass

    if HUMAN_REVIEW_SCHEMA.exists() and contract.get("human_review_gate", {}).get("span_review_required") is True and contract.get("human_review_gate", {}).get("multi_clause_required") is True:
        _add(findings, "passes", "span_multiclause_contract_locked", "Span-aware, multi-clause annotation and actor/action/order contracts are locked.")
    else:
        _add(findings, "errors", "span_multiclause_contract_missing", "Human Gold span/multi-clause contract is incomplete.")

    # ------------------------------------------------------------------
    # Four orthogonal readiness gates (split 2026-07-13; 4-gate
    # alignment 2026-07-13 Event 22):
    #
    #   1. human_review_input_ready
    #       True as soon as the data sources, schemas, tool, v2
    #       file, and AUTHORITATIVE CONTRACT GATE STATUS are in
    #       place. Independent of the user's review progress. The
    #       user can start the human review NOW.
    #
    #   2. human_review_freeze_ready
    #       True only after every record has been adjudicated. This
    #       is the precondition for declaring formal Gold.
    #
    #   3. formal_gold_publication_ready
    #       True only when human_review_freeze_ready AND
    #       route.status=="locked" AND dataset locked AND stage3
    #       locked AND formal_gold_publication_gate.status is not
    #       blocked. Conservative: any missing or non-locked field
    #       keeps it false.
    #
    #   4. final_experiment_ready
    #       True only when formal_gold_publication_ready AND
    #       methods not blocked AND frozen input/gold present.
    #
    # The previously misleading `formal_human_review_paused`
    # blocker is replaced by these four explicit gates so the
    # audit never emits the contradictory "user can edit NOW" /
    # "don't start human review" pair.
    # ------------------------------------------------------------------
    human_review_input_ready = bool(status.get("human_review_input_ready"))
    human_review_freeze_ready = bool(status.get("human_review_freeze_ready"))
    formal_gold_publication_ready = bool(status.get("formal_gold_publication_ready"))
    final_experiment_ready = bool(status.get("final_experiment_ready"))
    # The authoritative contract gate must agree with the computed
    # boolean. If the contract says input is NOT ready but our
    # computation says it is (or vice versa), surface as a finding.
    gate_status = status.get("human_review_gate_status")
    contract_authorizes = bool(status.get("human_review_gate_contract_authorizes_input_start"))
    if contract_authorizes and not human_review_input_ready:
        _add(findings, "errors", "human_review_input_status_mismatch",
             f"Contract says input is ready (status={gate_status!r}) but the "
             f"input preconditions are not all satisfied. Check schema, tool, "
             f"v2 human_correction file, and membership cross-check.")
    if (not contract_authorizes) and human_review_input_ready:
        _add(findings, "errors", "human_review_input_status_mismatch",
             f"Contract says input is NOT ready (status={gate_status!r}) but "
             f"the preconditions are all satisfied. Update the contract's "
             f"human_review_gate.status to one of the allowed values.")
    if human_review_input_ready:
        _add(findings, "passes", "human_review_input_ready",
             "EStG-150 single-dataset input is ready to start human review: "
             "authoritative contract.human_review_gate.status in allowed "
             "values; 150 unique sample_ids locked; v1 canonical review "
             "(provenance) and v2 human_correction (active editing surface) "
             "are format-valid; membership_payload_sha256 matches; schema + "
             "review tool + validator are in place. The 150 records are the "
             "project-self-sampled EStG-150 dataset (NOT Sun's original 150, "
             "NOT an exact reproduction). The user can begin editing "
             "data/development/human_review/estg_150_human_correction_v1.json NOW.")
    else:
        # Distinguish "contract says paused" from "preconditions missing".
        if not contract_authorizes:
            _add(findings, "blockers", "human_review_input_not_ready",
                 f"Contract.human_review_gate.status={gate_status!r} is NOT in "
                 f"the allowed input values "
                 f"{status.get('human_review_gate_allowed', [])!r}. "
                 f"Update the contract to a status that authorizes the user "
                 f"to begin editing the v2 human_correction file.")
        else:
            _add(findings, "blockers", "human_review_input_not_ready",
                 f"EStG-150 input preconditions are not all satisfied "
                 f"(membership_ok={status.get('membership_ok')!s}, "
                 f"reason={status.get('membership_reason')!r}). Check the "
                 f"canonical review file, v2 human_correction file, "
                 f"human_review schema, and review tool presence.")
    if not human_review_freeze_ready:
        n_rev = human_correction.get("n_reviewed", 0)
        n_adj = human_correction.get("n_adjudicated", 0)
        _add(findings, "blockers", "annotation_freeze_pending",
             f"Annotation freeze is pending: v2 human_correction progress "
             f"reviewed={n_rev}/150, adjudicated={n_adj}/150, "
             f"review_ready={human_correction.get('review_ready')}, "
             f"freeze_ready={human_correction.get('freeze_ready')}. "
             f"This blocker does NOT prevent the user from starting or "
             f"continuing the human review; it only blocks declaring "
             f"annotation frozen.")
    else:
        _add(findings, "passes", "annotation_freeze_ready",
             f"All 150 records adjudicated; v2 human_correction freeze_ready=True. "
             f"Annotation is frozen. Note: this is a NECESSARY but NOT "
             f"SUFFICIENT condition for formal_gold_publication_ready — "
             f"the route, data, stage3, and freeze_policy gates must also "
             f"be re-locked before formal Gold can be published.")
    # The formal_gold_publication_paused blocker must be present as
    # long as formal_gold_publication_ready is false. The blocker
    # message must NOT promise that formal Gold can be declared when
    # only annotation is frozen. Event 23 also requires that the
    # formal_gold_publication_gate.status be matched against the
    # contract's allowed_publication_statuses WHITELIST (exact match),
    # not the older "not blocked and not unknown" heuristic.
    if not formal_gold_publication_ready:
        n_rev = human_correction.get("n_reviewed", 0)
        n_adj = human_correction.get("n_adjudicated", 0)
        missing = []
        if not human_review_freeze_ready:
            missing.append(
                f"human_review_freeze_ready=False (adjudicated {n_adj}/150, "
                f"reviewed {n_rev}/150)"
            )
        route_status = (contract.get("route") or {}).get("status", "?")
        if route_status != "locked":
            missing.append(f"route.status={route_status!r} (must be 'locked')")
        dataset_status = (contract.get("stage2_dataset") or {}).get("status", "?")
        if dataset_status != "locked_for_human_review":
            missing.append(
                f"stage2_dataset.status={dataset_status!r} "
                f"(must be 'locked_for_human_review')"
            )
        stage3_status = (contract.get("stage3") or {}).get("status", "?")
        if stage3_status != "locked":
            missing.append(
                f"stage3.status={stage3_status!r} (must be 'locked')"
            )
        fgg_status = status.get("formal_gold_publication_gate_status", "?")
        fgg_allowed = status.get("formal_gold_publication_gate_allowed", [])
        if not status.get("formal_gold_publication_gate_match", False):
            missing.append(
                f"formal_gold_publication_gate.status={fgg_status!r} "
                f"is NOT in the contract's allowed_publication_statuses "
                f"whitelist {list(fgg_allowed)!r}. An exact match is "
                f"required; any pending/unknown/misspelled/blocked "
                f"value keeps the publication gate false."
            )
        _add(findings, "blockers", "formal_gold_publication_paused",
             "Formal Gold publication is paused. Missing preconditions: " +
             "; ".join(missing) +
             ". Even when annotation is frozen, the route / data / stage3 / "
             "freeze_policy / exact publication status whitelist must each "
             "individually be re-locked before formal Gold can be declared. "
             "The user can still continue the human review; this blocker "
             "only prevents publishing formal Gold.")
    else:
        _add(findings, "passes", "formal_gold_publication_ready",
             "All formal Gold publication preconditions are satisfied: "
             "human_review_freeze_ready=True, route.status=locked, "
             "stage2_dataset.status=locked_for_human_review, stage3.status=locked, "
             "formal_gold_publication_gate.status is an exact match against the "
             "contract's allowed_publication_statuses whitelist. "
             "Formal Gold can be declared as 'LLM-assisted, human-adjudicated Gold'.")
    if not final_experiment_ready:
        if not formal_gold_publication_ready:
            _add(findings, "blockers", "final_experiment_not_ready",
                 "Final experiment is not ready: formal_gold_publication_ready=False. "
                 "Stage 3 / three-method end-to-end cannot run until formal Gold "
                 "is declared.")
        else:
            n_methods_blocked = len(status.get("method_blockers") or [])
            frozen = (status.get("frozen_artifacts") or {})
            _add(findings, "blockers", "final_experiment_not_ready",
                 f"Final experiment is not ready even though formal Gold is "
                 f"publishable: {n_methods_blocked} method(s) blocked, "
                 f"frozen input={frozen.get('input', 0)} files, "
                 f"frozen gold={frozen.get('gold', 0)} files.")

    methods = _load_json(METHODS_CONFIG).get("methods", [])
    expected = {"sun_rule_only", "sun_llm_fallback", "direct_llm"}
    ids = {item.get("id") for item in methods if isinstance(item, dict)}
    if ids != expected:
        _add(findings, "errors", "method_set_mismatch", f"Configured methods: {sorted(str(x) for x in ids)}")
    else:
        _add(findings, "passes", "method_set_defined", "Legacy IDs define the non-LLM Sun baseline, Sun+LLM fallback, and direct-LLM replacement roles.")
    nonready = {str(item.get("id")): str(item.get("formal_status")) for item in methods if item.get("formal_status") != "ready"}
    if nonready:
        _add(findings, "blockers", "formal_methods_not_ready", f"Method gates: {nonready}")
    else:
        # Final-readiness hardening (user-authorized 2026-08-11, hardened
        # 2026-08-11): with all three methods ready, the audit EXECUTES the
        # full fail-closed verification -- three arm capsules verified
        # structurally and by hash from disk, the three independent
        # verifiers actually run, the comparison capsule re-derived, and the
        # G0.4 contract authorization checked. methods_unexpectedly_ready
        # fires ONLY when those conditions are not REALLY satisfied; in the
        # authorized, fully satisfied state it must NOT fire.
        from bpc_hybrid.formal_arm_verification import verify_all_with_verifiers
        gate = verify_all_with_verifiers()
        if gate["verified"]:
            _add(findings, "passes", "final_gate_conditions_met",
                 "All three method gates are ready AND the fail-closed "
                 "final-gate conditions are really satisfied (three formal "
                 "capsules verified from disk incl. executed independent "
                 "verifiers, hash-consistent shared comparison capsule "
                 "re-derived, user-authorized G0.4 contract).")
        else:
            _add(findings, "errors", "methods_unexpectedly_ready",
                 "methods.json has all 3 methods ready but the fail-closed "
                 "final-gate conditions are NOT met: " + "; ".join(gate["reasons"]))

    rule = (REPO_ROOT / "scripts/run_sun_rule_only.py").read_text(encoding="utf-8")
    hybrid = (REPO_ROOT / "scripts/run_sun_llm_fallback.py").read_text(encoding="utf-8")
    rule_has_legacy_front_end = "SemanticExtractor()" in rule
    hybrid_reuses_persisted_b0 = (
        "--b0-predictions" in hybrid
        and "load_b0_predictions" in hybrid
        and "SemanticExtractor()" not in hybrid
    )
    if rule_has_legacy_front_end and hybrid_reuses_persisted_b0:
        _add(
            findings,
            "passes",
            "h1_explicit_b0_artifact_binding",
            "The development H1 runner consumes a persisted B0 artifact and does not recreate the rule front end internally.",
        )
    elif "SemanticExtractor()" in rule and "SemanticExtractor()" in hybrid:
        _add(findings, "warnings", "legacy_shared_front_end_only", "Current development M1/M2 share one heuristic front end, but it is not the final published Sun Stage 2 baseline.")
    else:
        _add(findings, "errors", "rule_front_end_mismatch", "H1 does not demonstrably reuse either the persisted B0 artifact or the same legacy rule front end.")
    # NOTE: the actual `sun_stage2_baseline_not_paper_faithful` blocker is
    # emitted later as a precise code-level check (see below), not here.
    # Keeping only one canonical message avoids duplicate blocker rows.
    if not (REPO_ROOT / "scripts/run_direct_llm.py").exists():
        _add(findings, "blockers", "direct_llm_runner_missing", "Dedicated guarded direct-LLM runner is not implemented yet.")

    # D1 prompt root-level entry-point scripts: a separate blocker from
    # the formal-capsule tracking. They violate the "all active code
    # under formal_experiment/" contract; tracked here so it shows up
    # alongside the other blockers but does not affect the formal
    # methods' readiness.
    # Resolve against the actual workspace so directory renames and
    # linked worktrees do not require hardcoded checkout paths.
    workspace_root = REPO_ROOT.parent
    d1_root_scripts = [
        workspace_root / "build_d1_prompt.py",
        workspace_root / "build_few_shot.py",
        workspace_root / "verify_d1_few_shot.py",
    ]
    present_root_scripts = [p for p in d1_root_scripts if p.exists()]
    if present_root_scripts:
        rels = [str(p.relative_to(workspace_root)) for p in present_root_scripts]
        _add(
            findings, "blockers", "d1_root_scripts_outside_formal_capsule",
            "D1 prompt entry-point scripts violate the formal-capsule contract "
            "(all active code must live under formal_experiment/). They are "
            "tracked here as a SEPARATE blocker; the EStG-150 LLM-assisted "
            "human-correction workflow does not depend on them and they are "
            "not moved or deleted in this task: " + ", ".join(rels),
        )

    frozen_counts = {
        "input": _meaningful_count(FROZEN_INPUT_DIR), "gold": _meaningful_count(FROZEN_GOLD_DIR),
        "predictions": _meaningful_count(FORMAL_PREDICTIONS_DIR), "results": _meaningful_count(FORMAL_RESULTS_DIR),
        "reports": _meaningful_count(FORMAL_REPORTS_DIR),
    }
    # The frozen capsule check distinguishes the GOLD capsule (frozen input +
    # Gold artifacts, which IS frozen since the 2026-08-10 formal Gold
    # publication) from the FINAL EXPERIMENT capsule (predictions/results,
    # which are expected to not exist yet). predictions/results == 0 must
    # never be misread as "the final capsule is frozen".
    gold_capsule_frozen = bool(frozen_counts["input"]) and bool(frozen_counts["gold"])
    if gold_capsule_frozen:
        _add(findings, "passes", "formal_gold_capsule_frozen",
             "Gold capsule frozen: frozen input and Gold artifacts exist under data/input and data/gold.")
    else:
        _add(findings, "blockers", "formal_capsule_not_frozen",
             f"Gold capsule NOT frozen (frozen input and/or Gold artifacts missing): {frozen_counts}")
    # Method-coverage check for the predictions/results capsule: one file in
    # data/predictions must never be misread as the complete three-method
    # final capsule. Coverage is derived from the per-arm manifests under
    # outputs/reports (each arm manifest carries method_id).
    capsule_methods = _formal_capsule_methods()
    all_methods = {"sun_rule_only", "sun_llm_fallback", "direct_llm"}
    if not frozen_counts["predictions"] or not frozen_counts["results"]:
        _add(findings, "warnings", "formal_predictions_results_capsule_not_produced",
             "Formal predictions/results capsule is not produced yet (expected at this stage). "
             "This is NOT the final experiment capsule being frozen.")
    elif capsule_methods != all_methods:
        _add(findings, "warnings", "formal_predictions_results_capsule_partial",
             f"Formal predictions/results capsule is PARTIAL: published method arms "
             f"{sorted(capsule_methods)} of the three-method set "
             f"{sorted(all_methods)}; this is NOT the complete three-method final capsule.")
    else:
        _add(findings, "passes", "formal_predictions_results_capsule_complete",
             "Formal predictions/results capsule covers all three methods.")

    # ------------------------------------------------------------------
    # Formal benchmark release v2: independent verifier gate.
    # The verifier re-reads every published artifact from disk (hashes,
    # sizes, counts, schema, membership, text provenance, decisions vs
    # frozen sources, forbidden fields, modality exclusion, implementation
    # hashes). A directory-with-files check is NOT a publication check.
    verifier = _load_release_verifier()
    if verifier is None:
        _add(findings, "errors", "formal_benchmark_release_invalid",
             "Formal benchmark release verifier module could not be loaded.")
    else:
        try:
            release_result = verifier.verify_release()
            if release_result.get("verified"):
                _add(findings, "passes", "formal_benchmark_release_verified",
                     "Formal benchmark release v2 verified by independent verifier "
                     "(artifacts, schema, membership, text provenance, decisions, "
                     "forbidden fields, modality exclusion, implementation hashes).")
            else:
                failed_checks = [c["name"] for c in release_result.get("checks", []) if not c["ok"]]
                _add(findings, "errors", "formal_benchmark_release_invalid",
                     f"Formal benchmark release v2 verification FAILED: {failed_checks}")
        except Exception as exc:  # pragma: no cover - defensive
            _add(findings, "errors", "formal_benchmark_release_invalid",
                 f"Formal benchmark release verifier raised: {exc}")
    if contract.get("stage3", {}).get("status") != "locked":
        _add(findings, "blockers", "stage3_benchmark_not_locked", "Formal BPMN set, matching configuration, and violation Gold still require a later lock.")

    # ------------------------------------------------------------------
    # S1.5 review-surface input-readiness (user-authorized 2026-08-11).
    # The authorization record must exist with all checks green; the
    # correction file must stay all-unreviewed with freeze_ready=False
    # (the tool must never infer/prefill). This is input-ready only; Gold
    # freeze remains blocked until the user adjudicates 7/7 + 135/135.
    # State evolution (2026-08-11): once verified human adjudications
    # exist, the audit switches to stage1_human_adjudication_in_progress,
    # which additionally requires every correction-vs-blank difference to be
    # backed by a versioned decision asset and the incremental adjudication
    # verifier to pass. State evolution (2026-08-13, Batch 7/7): when the
    # correction reports 7/7 adjudicated + 135/135 resolved (freeze_ready
    # true) and the verifier passes while gold_freeze_authorized stays
    # false, the audit reports stage1_human_adjudication_complete_freeze_pending
    # ("142/142 resolved" is a freeze-READY fact, NOT a freeze authorization
    # and NOT published Gold). State evolution (2026-08-13, user freeze
    # authorization): with gold_freeze_authorized=true AND the published
    # Stage 1 Process Gold independently verified, the audit reports
    # stage1_process_gold_published; this is published Gold, but S1.6
    # formal evaluation / S1.7 / S3.7 are NOT auto-advanced.
    s15_auth = _load_json(REPO_ROOT / "outputs" / "reports"
                          / "s1_5_review_surface_authorization_v1.manifest.json")
    s15_checks = s15_auth.get("checks", {})
    freeze_authorized = s15_auth.get("authorization_scope", {}).get(
        "gold_freeze_authorized") is True
    auth_ok = (s15_auth.get("authorized_by_user") is True
               and all(s15_checks.values())
               and (s15_auth.get("authorization_scope", {}).get(
                   "gold_freeze_authorized") is False
                    or freeze_authorized))
    adjudication_dir = (REPO_ROOT / "outputs" / "development" / "human_review"
                        / "stage1_adjudications")
    has_adjudications = adjudication_dir.exists() and any(
        d.is_dir() for d in adjudication_dir.iterdir())
    adjudication_ok = False
    if has_adjudications:
        try:
            verifier = _load_adjudication_verifier()
            if verifier is not None:
                adjudication_ok = verifier.verify()["verified"] is True
        except Exception:  # pragma: no cover - defensive
            adjudication_ok = False
    # 7/7 + 135/135 (derived from the on-disk correction summary, the same
    # source the adjudication verifier validates; freeze_ready true)
    s15_correction = _load_json(
        REPO_ROOT / "data" / "development" / "human_review"
        / "stage1_gdpr7_human_correction_v1.json")
    s15_summary = s15_correction.get("review_summary", {})
    adjudication_complete = (
        s15_summary.get("adjudicated_records") == 7
        and s15_summary.get("resolved_label_fields") == 135
        and s15_summary.get("freeze_ready") is True)
    # published Stage 1 Process Gold: independently verified artifact
    gold_verified = False
    if freeze_authorized:
        try:
            gold_verifier = _load_gold_verifier()
            if gold_verifier is not None:
                gold_verified = gold_verifier.verify()["verified"] is True
        except Exception:  # pragma: no cover - defensive
            gold_verified = False
    if has_adjudications and adjudication_ok and auth_ok \
            and adjudication_complete and freeze_authorized and gold_verified:
        _add(findings, "passes", "stage1_process_gold_published",
             "Formal Stage 1 Process Gold FROZEN and PUBLISHED "
             "(data/gold/stage1/process_records/stage1_process_gold_v1.json): "
             "7/7 records, 135/135 label fields, 7/7 structure decisions, "
             "142/142 human decisions, 0 unresolved; every published record "
             "equals the adjudicated correction record (no added/inferred/"
             "rewritten decision); source/candidate/correction/seven-batch "
             "chain hashes preserved; seven-batch chain verifier passes; "
             "user-authorized 2026-08-13 (gold_freeze_authorized=true). "
             "S1.7 / S3.7 are NOT auto-advanced.")

    # ------------------------------------------------------------------
    # S1.3 P2 + S1.6 one-shot formal evaluation (2026-08-13): the audit
    # ACTUALLY RUNS the independent P2 lock verifier, the prediction
    # verifier and the formal evaluation capsule verifier (recomputed from
    # disk, not file-presence checks).
    p2_verified = False
    predictions_verified = False
    evaluation_verified = False
    try:
        p2_verifier = _load_p2_verifier()
        if p2_verifier is not None:
            p2_verified = p2_verifier.verify()["verified"] is True
    except Exception:  # pragma: no cover - defensive
        p2_verified = False
    try:
        pred_verifier = _load_prediction_verifier()
        if pred_verifier is not None:
            predictions_verified = pred_verifier.verify()["verified"] is True
    except Exception:  # pragma: no cover - defensive
        predictions_verified = False
    try:
        eval_verifier = _load_formal_evaluation_verifier()
        if eval_verifier is not None:
            evaluation_verified = eval_verifier.verify()["verified"] is True
    except Exception:  # pragma: no cover - defensive
        evaluation_verified = False
    if p2_verified and predictions_verified and evaluation_verified:
        _add(findings, "passes", "stage1_formal_evaluation_verified",
             "S1.6 fixed-GDPR-7 formal descriptive component evaluation "
             "VERIFIED (2026-08-13): P2 Sun/Leopold-style reconstruction "
             "locked and byte-unchanged; P0/P1/P2 formal predictions "
             "re-verified from whitelisted inputs (no Gold leakage at "
             "runtime); evaluation capsule re-run from disk matches the "
             "stored report; zero LLM/API; P2 not tuned after evaluation. "
             "Claim boundary (2026-08-13 correction): the reconstruction is "
             "post-Gold and target-aware (three fixture labels overlapped "
             "the GDPR-7 target); NOT strict test-blind; NOT held-out "
             "generalization evidence; candidate-assisted Gold; structure "
             "1.0 is not external generalization evidence; no significance "
             "inference; no hard comparison with Sun absolute scores.")
    elif (p2_verified and not predictions_verified) or (
            predictions_verified and not evaluation_verified):
        _add(findings, "errors", "stage1_formal_evaluation_invalid",
             "S1.3/S1.6 formal assets exist but an independent verifier "
             "FAILED (predictions or evaluation capsule tampered).")

    # ------------------------------------------------------------------
    # 2026-08-13 correction gate: target-overlap audit + claim correction +
    # formal v2 assets + S1.7 v2 readiness. All verifiers ACTUALLY run.
    overlap_verified = False
    v2_verified = False
    v2p_verified = False
    try:
        ov_verifier = _load_verifier_script("s1_overlap_audit_verifier",
                                            "verify_s1_p2_target_overlap_audit.py")
        if ov_verifier is not None:
            overlap_verified = ov_verifier.verify()["verified"] is True
    except Exception:  # pragma: no cover - defensive
        overlap_verified = False
    try:
        v2_verifier = _load_verifier_script("s1_v2_verifier",
                                            "verify_stage1_formal_evaluation_v2.py")
        if v2_verifier is not None:
            v2_verified = v2_verifier.verify()["verified"] is True
    except Exception:  # pragma: no cover - defensive
        v2_verified = False
    try:
        v2p_verifier = _load_verifier_script("s1_v2p_verifier",
                                             "verify_s1_7_freezer_dry_run_v2.py")
        if v2p_verifier is not None:
            v2p_verified = v2p_verifier.verify()["verified"] is True
    except Exception:  # pragma: no cover - defensive
        v2p_verified = False
    if overlap_verified and v2_verified and v2p_verified:
        _add(findings, "passes", "stage1_claim_correction_verified",
             "S1 claim/formal-path correction VERIFIED (2026-08-13): "
             "target-overlap audit (historical 3 overlaps documented, "
             "current fixtures zero-overlap) + target-aware claim "
             "correction v2 (strict_test_blind=false, "
             "held_out_generalization_claim_allowed=false, "
             "runtime_gold_read=false, post_evaluation_tuning=false) + "
             "formal v2 assets (data/predictions + data/results + v2 report, "
             "numbers byte-locked) + S1.7 readiness v2 (v1 superseded, "
             "freeze NOT applied).")
    elif (overlap_verified or v2_verified or v2p_verified):
        _add(findings, "errors", "stage1_claim_correction_invalid",
             "S1 correction assets exist but an independent verifier "
             "FAILED (overlap audit / v2 assets / S1.7 v2 tampered, or a "
             "claim was reverted to test-blind / a formal path points back "
             "to development / verb count is not 200).")

    elif has_adjudications and adjudication_ok and auth_ok \
            and adjudication_complete:
        _add(findings, "passes",
             "stage1_human_adjudication_complete_freeze_pending",
             "S1.5 human adjudication COMPLETE: 7/7 records, 135/135 label "
             "fields, 7/7 structure decisions, 142/142 human decisions "
             "resolved, 0 unresolved (every correction-vs-blank difference "
             "backed by a versioned user-decision asset; incremental "
             "adjudication verifier passes). Formal Process Gold freeze is "
             "NOT yet authorized (gold_freeze_authorized=false); this is a "
             "freeze-READY fact, not published Gold.")
    elif has_adjudications and adjudication_ok and auth_ok:
        _add(findings, "passes", "stage1_human_adjudication_in_progress",
             "S1.5 human adjudication is in progress (user-authorized "
             "review surface; every correction-vs-blank difference backed by "
             "a versioned user-decision asset; incremental adjudication "
             "verifier passes; freeze remains blocked).")
    elif has_adjudications and not adjudication_ok:
        _add(findings, "errors", "stage1_human_adjudication_invalid",
             "S1.5 adjudication assets exist but the incremental "
             "adjudication verifier FAILED (tampered field/hash/summary or "
             "unevidenced correction change).")
    elif auth_ok:
        _add(findings, "passes", "stage1_review_surface_input_ready",
             "S1.5 review surface is input-ready (user-authorized 2026-08-11; "
             "all-seven GDPR-7 membership, all-unreviewed correction file, "
             "review tool + bilingual guide; tool never infers/prefills; "
             "Gold freeze remains blocked).")
    else:
        _add(findings, "errors", "stage1_review_surface_not_ready",
             "S1.5 review-surface authorization missing or its preconditions "
             "failed (correction file must stay all-unreviewed, freeze_ready "
             "must be False).")

    # ------------------------------------------------------------------
    # S1.7 freeze authorization (2026-08-13, user-authorized): the
    # authorization manifest must verify (byte-locks, sentences, safety,
    # exclusions) and the readiness packet must still be dry-run. The
    # freeze does NOT auto-advance S1.6/S3.7. (Placed after the S1.5
    # state machine so the if/elif chain above stays intact.)
    freeze_verified = False
    try:
        fa_verifier = _load_verifier_script("s1_freeze_auth_verifier",
                                            "verify_s1_7_freezer_authorization.py")
        if fa_verifier is not None:
            freeze_verified = fa_verifier.verify()["verified"] is True
    except Exception:  # pragma: no cover - defensive
        freeze_verified = False
    if freeze_verified:
        _add(findings, "passes", "stage1_s7_freeze_authorized",
             "S1.7 formal freeze AUTHORIZED and APPLIED (2026-08-13, "
             "user-authorized): the existing non-tuned P2 method (locked "
             "config/implementation/offline runtime), the existing locked "
             "P0/P1/P2 predictions, the ORIGINAL metrics, the Stage 1 "
             "Process Gold and the verified evaluation capsule are frozen; "
             "no P2 modification, no selective recomputation, zero LLM/API; "
             "target-aware disclosure holds (post-Gold development, "
             "strict_test_blind=false, fixed-GDPR7 descriptive "
             "evaluation). The formal Stage 3 Oracle is NOT authorized and "
             "advances only through its own gates.")
    else:
        _add(findings, "errors", "stage1_s7_freeze_authorization_invalid",
             "S1.7 freeze authorization manifest missing or FAILED "
             "(tampered sentences/bindings/safety/exclusions, or the "
             "readiness packet was mutated).")
    tracked = _git_check(["ls-files", "--error-unmatch", "formal_experiment/AGENTS.md"])
    if tracked is False:
        _add(findings, "blockers", "formal_capsule_not_versioned", "Create an intentional Git checkpoint before freezing input and Gold.")
    elif tracked is None:
        _add(findings, "warnings", "git_tracking_unavailable", "Git tracking state could not be verified.")
    else:
        _add(findings, "passes", "formal_capsule_versioned", "Formal control capsule is tracked by Git.")

    ignored = _git_check(["check-ignore", "-q", "formal_experiment/outputs/reports/audit-probe.md"])
    if ignored is True:
        _add(findings, "errors", "formal_reports_gitignored", "Formal reports are ignored by Git.")
    else:
        _add(findings, "passes", "formal_reports_versionable", "Formal reports can be versioned.")

    # ------------------------------------------------------------------
    # B0-R1-A-C3 (2026-08-03): manifest artifact integrity gate.
    #
    # We register one specific development-only Stage-2 manifest that
    # the project audit must verify by raw SHA-256. The gate never
    # scans the entire ``outputs/development/`` history; older runs
    # remain provenance and are not retroactively bound. Adding a new
    # registered run requires an explicit correction event.
    #
    # ``REPO_ROOT`` already points at ``formal_experiment/``, so the
    # registered path is the project-relative path MINUS that prefix.
    # ------------------------------------------------------------------
    _C3_MANIFEST_REL = (
        "outputs/development/"
        "s27_estg150_b0_enhanced_v10a_r1a_c3_hist56d_v1/manifest.json"
    )
    c3_manifest = REPO_ROOT / _C3_MANIFEST_REL
    c3_errors = verify_manifest_artifact_integrity(c3_manifest)
    if c3_errors:
        for err in c3_errors:
            _add(
                findings,
                "errors",
                err.code,
                f"{err.artifact}: {err.message}",
            )
    else:
        _add(
            findings,
            "passes",
            _PASS_CODE,
            "Registered C3 development manifest's four artifacts (b0_attempts.json + "
            "three evaluation JSONs) all hash-match the declared raw SHA-256 against the "
            "current working tree.",
        )

    # ------------------------------------------------------------------
    # Wave 1.1 \u00a78: canonical schema / prompt loader / runner integration
    # ------------------------------------------------------------------

    canonical_schema_path = REPO_ROOT / "configs" / "schemas" / "stage2_prediction.schema.json"
    if not canonical_schema_path.exists():
        _add(findings, "errors", "canonical_schema_missing",
             "configs/schemas/stage2_prediction.schema.json is required (Wave 1.1 \u00a78).")
    else:
        try:
            schema_doc = json.loads(canonical_schema_path.read_text(encoding="utf-8"))
            if schema_doc.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0":
                _add(findings, "errors", "canonical_schema_version_mismatch",
                     "Canonical schema_version must be exactly 1.0.0.")
            else:
                _add(findings, "passes", "canonical_schema_loaded",
                     "Canonical Stage 2 prediction schema v1.0.0 is present and loadable.")
        except json.JSONDecodeError as exc:
            _add(findings, "errors", "canonical_schema_unparseable",
                 f"Canonical schema is not valid JSON: {exc}")

    # Prompt file existence and schema reference
    d1_prompt_path = REPO_ROOT / "prompts" / "sun_compat" / "direct_llm_sun_record_prompt.md"
    h1_prompt_path = REPO_ROOT / "prompts" / "sun_compat" / "rule_first_llm_fallback_prompt.md"
    prompt_files_ok = True
    for path in (d1_prompt_path, h1_prompt_path):
        if not path.exists():
            _add(findings, "errors", "prompt_file_missing", f"Prompt file missing: {path}")
            prompt_files_ok = False
    if prompt_files_ok:
        d1_text = d1_prompt_path.read_text(encoding="utf-8").lower()
        h1_text = h1_prompt_path.read_text(encoding="utf-8").lower()
        d1_refs = "stage2_prediction.schema.json@1.0.0" in d1_text
        h1_refs = "stage2_prediction.schema.json@1.0.0" in h1_text
        if d1_refs and h1_refs:
            _add(findings, "passes", "prompts_reference_canonical_schema",
                 "D1 and H1 prompt files reference the canonical schema.")
        else:
            _add(findings, "errors", "prompts_must_reference_canonical_schema",
                 f"D1 refs={d1_refs}; H1 refs={h1_refs}; both must cite stage2_prediction.schema.json@1.0.0.")

    # Prompt loader is being used (no hardcoded SYSTEM_PROMPT in runners)
    for runner_name, runner_path in (
        ("run_direct_llm", REPO_ROOT / "scripts" / "run_direct_llm.py"),
        ("run_sun_llm_fallback", REPO_ROOT / "scripts" / "run_sun_llm_fallback.py"),
    ):
        if not runner_path.exists():
            continue
        text = runner_path.read_text(encoding="utf-8")
        if "from bpc_hybrid.prompt_loader import" not in text:
            _add(findings, "errors", "runner_hardcodes_prompt",
                 f"{runner_name} does not import bpc_hybrid.prompt_loader (Wave 1.1 \u00a78).")
        elif 'SYSTEM_PROMPT = """' in text:
            _add(findings, "errors", "runner_hardcodes_system_prompt",
                 f"{runner_name} has a hardcoded SYSTEM_PROMPT triple-quoted string.")
        else:
            _add(findings, "passes", f"{runner_name}_uses_prompt_loader",
                 f"{runner_name} uses the prompt loader (no hardcoded SYSTEM_PROMPT).")

    # Few-shot fixtures must validate against canonical schema
    if d1_prompt_path.exists():
        try:
            sys_mod = __import__("sys")
            project_root_str = str(REPO_ROOT)
            if project_root_str not in sys_mod.path:
                sys_mod.path.insert(0, project_root_str)
            from bpc_hybrid.prompt_loader import load_prompt
            from bpc_hybrid.stage2_canonical import validate_canonical
            d1_prompt = load_prompt("direct_llm_sun_record_prompt")
            few_shot_failures: list[str] = []
            for ex in d1_prompt.few_shot_examples:
                rep = validate_canonical(ex["output"])
                if not (rep.schema_valid and rep.cross_field_valid):
                    few_shot_failures.append(ex["description"][:60])
            if few_shot_failures:
                _add(findings, "errors", "few_shot_fixtures_fail_validation",
                     f"D1 few-shot fixtures fail canonical validation: {few_shot_failures}")
            else:
                _add(findings, "passes", "few_shot_fixtures_validate",
                     f"All {len(d1_prompt.few_shot_examples)} D1 few-shot fixtures pass canonical validation.")
        except Exception as exc:  # pragma: no cover - defensive
            _add(findings, "errors", "few_shot_check_crashed",
                 f"Could not verify few-shot fixtures: {exc}")

    # B0 component presence is now separated from method-conformance.
    #   A. component presence: code under src/bpc_hybrid/sun_style (and
    #      other B0 modules) actually references BertTextCNN, CoreNLP
    #      and Tregex/Tsurgeon. This is a *static* check that the
    #      paper-faithful components exist in the code base. It does
    #      NOT imply that the B0 method-level reconstruction has
    #      completed B0-R2 (component-vs-method conformance cross-
    #      walk, BERT-TextCNN training on the frozen split, Tregex
    #      patterns, end-to-end run on ESTG-150 frozen IDs).
    #   B. method conformance: the formal Sun Stage 2 baseline is the
    #      complete method, not a heuristic. The audit MUST keep
    #      `sun_stage2_baseline_not_paper_faithful` as a blocker
    #      until configs/methods.json explicitly states
    #      `method_conformance_status == "verified_method_level_independent_reconstruction"`.
    #      B0-R0 (component integration) and B0-R1 (deterministic
    #      defect repair) do NOT satisfy that gate; only B0-R2 (or
    #      later) may.
    # Stricter check on (A): require import statements or class
    # definitions, not bare word matches (which can be triggered by
    # docstring edits).
    b0_has_textcnn = False
    b0_has_corenlp = False
    b0_has_tregex = False
    sun_style = REPO_ROOT / "src" / "bpc_hybrid" / "sun_style"
    if sun_style.exists():
        for path in sun_style.rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for line in text.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if not b0_has_textcnn and (
                    "class BertTextCNN" in stripped
                    or "BertTextCNN(" in stripped
                    or "import textcnn" in stripped.lower()
                    or "from .textcnn" in stripped.lower()
                ):
                    b0_has_textcnn = True
                if not b0_has_corenlp and (
                    "import corenlp" in stripped.lower()
                    or "from corenlp" in stripped.lower()
                    or "from stanfordnlp" in stripped.lower()
                    or "StanfordCoreNLP" in stripped
                ):
                    b0_has_corenlp = True
                if not b0_has_tregex and (
                    "import tregex" in stripped.lower()
                    or "from tregex" in stripped.lower()
                    or "TregexPattern" in stripped
                    or "Tsurgeon" in stripped
                ):
                    b0_has_tregex = True
    if b0_has_textcnn and b0_has_corenlp and b0_has_tregex:
        _add(findings, "passes", "b0_paper_faithful_components_present",
             "B0 paper-faithful components (TextCNN + CoreNLP + Tregex) are present in code. "
             "This is a static source-presence check, NOT a B0-R2 method-conformance approval.")
    else:
        missing = [
            n for n, p in (
                ("TextCNN", b0_has_textcnn),
                ("CoreNLP", b0_has_corenlp),
                ("Tregex/Tsurgeon", b0_has_tregex),
            ) if not p
        ]
        _add(findings, "blockers", "sun_stage2_baseline_not_paper_faithful",
             f"Formal baseline must be rebuilt with: {', '.join(missing)}; "
             f"current implementation is heuristic only. (Component presence is the only check the "
             f"static source scan can do; method-level conformance must still be verified through B0-R2.)")

    # (B) Method-level conformance gate. Only when
    # `sun_rule_only.method_conformance_status` is exactly
    # `verified_method_level_independent_reconstruction` may the
    # `sun_stage2_baseline_not_paper_faithful` blocker be lifted. B0-R0
    # explicitly does NOT set this status; it remains
    # `blocked_until_b0_r2` until the B0-R2 component-vs-method cross-
    # walk is complete. This decouples component-source-presence from
    # method-conformance so that one pass cannot silently cancel the
    # other.
    methods_cfg = _load_json(METHODS_CONFIG).get("methods", [])
    sun_rule_only = next(
        (m for m in methods_cfg if isinstance(m, dict) and m.get("id") == "sun_rule_only"),
        None,
    )
    method_conformance_status = (
        str(sun_rule_only.get("method_conformance_status", ""))
        if isinstance(sun_rule_only, dict)
        else ""
    )
    if method_conformance_status != "verified_method_level_independent_reconstruction":
        _add(
            findings,
            "blockers",
            "sun_stage2_baseline_not_paper_faithful",
            "B0 method-level conformance is not yet verified: "
            f"configs/methods.json sun_rule_only.method_conformance_status="
            f"{method_conformance_status!r} (required exact value: "
            f"'verified_method_level_independent_reconstruction'). "
            "B0-R0 integrates source components; B0-R1 repairs deterministic "
            "defects; B0-R2 must complete the component-vs-method cross-walk "
            "and ESTG-150 frozen-split run before this gate can be lifted.",
        )

    # Dynamic final-readiness wording (2026-08-15 regression fix): the
    # previous hardcoded tails claimed "final_experiment_ready remains
    # false" and "Formal predictions/results capsule is NOT produced yet"
    # even after the 2026-08-11 user-authorized final gate really opened.
    # Derive the wording from the same state the audit itself reports so
    # the warning and the claim boundary can never contradict the printed
    # gate values again.
    capsule_complete = any(
        item.get("code") == "formal_predictions_results_capsule_complete"
        for item in findings.get("passes", []))
    final_gate_now = bool(
        status.get("ready_for_final_metrics")
        and not findings["errors"]
        and not findings["blockers"])
    if final_gate_now:
        final_gate_wording = (
            "final_experiment_ready=True, which means ONLY that the "
            "Stage 2 three-method formal evaluation / final-metric "
            "machine gates are ready (three verified formal capsules, "
            "hash-consistent shared comparison capsule, user-authorized "
            "G0.4 contract); it does NOT mean S2.13, S3.7, or the full "
            "MASTER_PIPELINE is complete.")
    else:
        final_gate_wording = (
            "final_experiment_ready remains false: Stage 2 three-method "
            "formal capsules, shared comparison consistency, authorized "
            "G0.4 contract, frozen input/Gold, or integrity conditions are "
            "not ready. This still says nothing about S2.13/S3.7/"
            "full-pipeline completion.")
    capsule_wording = (
        "the formal predictions/results capsule covers all three methods"
        if capsule_complete
        else "the formal predictions/results capsule is NOT produced yet")

    _add(
        findings,
        "warnings",
        "estg_reconstruction_development_only",
        "Boundary reminder (NOT a gate on the active 150): "
        "(1) The OLD review pack / OCR-derived / marker-enriched / LLM-translated "
        "EStG-150 reconstruction is DEVELOPMENT-ONLY provenance and lives under "
        "data/development/ ; it is NOT the active editing surface. "
        "(2) The 150 sample_ids in the ACTIVE editing file "
        "data/development/human_review/estg_150_human_correction_v1.json "
        "(Layer E) are PERMANENTLY LOCKED to the membership payload "
        "sha256=8573e105d2bc167c6aa0a92c16f79a3aaf725baadfea86f0b5d2b1ea68b1e0d7 "
        "and the sorted legacy_record_ids in "
        "data/development/estg/estg_150_membership_hashes.json ; they CANNOT be "
        "re-sampled, re-seeded, or swapped with the legacy reconstruction. "
        "(3) After the user finishes 150/150 adjudication, this 150 becomes the "
        "project's INDEPENDENTLY RECONSTRUCTED EStG-150 BENCHMARK "
        "(independently_reconstructed_estg_150_v1), named "
        "'LLM-assisted, human-adjudicated Gold' ; it is NOT Sun's original 150 "
        "and is NOT an exact reproduction of any external dataset. "
        "(4) The official Sun Archive.org supplement (Decision_Logic_data.zip, "
        "input 2.zip) is reserved for METHOD, MODALITY DATA, and BASELINE "
        "ALIGNMENT use only ; it MAY NOT be used to replace any of the 150 "
        "active sample_ids. "
        "(5) Re-sampling, creating a parallel old/new 150, or migrating any "
        "user-entered human_correction result between two different 150s is "
        "FORBIDDEN. "
        "(6) The four orthogonal gates (human_review_input_ready / "
        "human_review_freeze_ready / formal_gold_publication_ready / "
        "final_experiment_ready) are unchanged by this reminder. Current "
        "state: input/freeze/Gold-publication gates true (150/150 "
        "adjudicated, formal Gold published, executable input v2 verified); "
        + capsule_wording + "; " + final_gate_wording,
    )

    integrity_pass = not findings["errors"]
    # Four orthogonal gates. The flag `--require-human-review-ready`
    # in audit_project.py checks `human_review_ready` (the INPUT
    # gate, kept as a backward-compatible alias of
    # human_review_input_ready). `final_experiment_ready` is the
    # all-clear gate and requires formal_gold_publication_ready
    # plus frozen input/gold and method readiness.
    human_review_input_ready = bool(
        status.get("human_review_input_ready") and integrity_pass
    )
    human_review_freeze_ready = bool(
        status.get("human_review_freeze_ready") and integrity_pass
    )
    formal_gold_publication_ready = bool(
        status.get("formal_gold_publication_ready") and integrity_pass
    )
    final_ready = bool(
        status.get("ready_for_final_metrics")
        and integrity_pass
        and not findings["blockers"]
    )
    # Backward-compatible alias (DEPRECATED). Field name kept so the
    # --require-human-review-ready flag still works. New code that
    # needs "ready to publish Gold" must use
    # formal_gold_publication_ready or final_experiment_ready.
    human_review_ready = human_review_input_ready
    return {
        "audit_version": "3.6",
        "integrity_pass": integrity_pass,
        # Backward-compatible field: semantics = "input is ready to
        # start the human review". True at 0/150 once the data,
        # schema, tool, v2 file, and authoritative contract gate
        # status are all in place.
        "human_review_ready": human_review_ready,
        "human_review_ready_semantics": (
            "DEPRECATED alias. Equals human_review_input_ready. Current "
            "state: 150/150 adjudicated (annotation frozen), formal Gold "
            "published, executable input v2 verified. New code that needs "
            "'ready to publish Gold' must use human_review_freeze_ready, "
            "formal_gold_publication_ready, or final_experiment_ready."
        ),
        # Four orthogonal gates:
        "human_review_input_ready": human_review_input_ready,
        "human_review_freeze_ready": human_review_freeze_ready,
        "formal_gold_publication_ready": formal_gold_publication_ready,
        "final_experiment_ready": final_ready,
        "sun_modality_development_data_verified": bool(
            status.get("sun_modality_development_data_verified")
        ),
        "sun_modality_source_population": status.get(
            "sun_modality_source_population"
        ),
        "sun_modality_analysis_population": status.get(
            "sun_modality_analysis_population"
        ),
        "sun_modality_quarantined_records": status.get(
            "sun_modality_quarantined_records"
        ),
        "sun_modality_train_size": status.get("sun_modality_train_size"),
        "sun_modality_dev_size": status.get("sun_modality_dev_size"),
        "sun_modality_test_size": status.get("sun_modality_test_size"),
        "sun_modality_license_status": status.get(
            "sun_modality_license_status"
        ),
        "sun_modality_formal_use_ready": bool(
            status.get("sun_modality_formal_use_ready")
        ),
        "public_marker_lexicon_verified": bool(
            status.get("public_marker_lexicon_verified")
        ),
        "public_marker_lexicon_language": status.get(
            "public_marker_gate", {}
        ).get("language"),
        "public_marker_lexicon_combined_payload_sha256": status.get(
            "public_marker_gate", {}
        ).get("combined_payload_sha256"),
        "claim_boundary": (
            "Route is locked (sun_2024_final_version_stage2_reconstruction, "
            "method-level independent reconstruction, not an exact reproduction). "
            "The EStG-150 dataset is the project-self-sampled 150 (NOT Sun's original 150). "
            "150/150 Layer E records are adjudicated (annotation frozen); formal Gold "
            "artifacts are published and the executable Gold-blind input v2 is verified. "
            + capsule_wording + "; " + final_gate_wording
        ),
        "findings": findings,
        "formal_status": status,
        "datasets": {"estg150_human_review_pack": review.to_dict()},
        "formal_capsule_counts": frozen_counts,
    }


def print_human(audit: dict[str, Any]) -> None:
    print("Experiment integrity check (legacy command: audit_project.py)")
    print("=" * 40)
    print(f"Integrity pass: {audit['integrity_pass']}")
    print(
        "Sun modality development data verified: "
        f"{audit.get('sun_modality_development_data_verified')}"
    )
    print(
        "S2.3 public marker lexicon verified: "
        f"{audit.get('public_marker_lexicon_verified')}"
    )
    # Four orthogonal gates in the audit output so the four
    # readiness states are never confused.
    print(f"Human review input ready       : {audit.get('human_review_input_ready')}")
    print(f"Human review freeze ready      : {audit.get('human_review_freeze_ready')}")
    print(f"Formal Gold publication ready : {audit.get('formal_gold_publication_ready')}")
    print(f"Final experiment ready         : {audit.get('final_experiment_ready')}")
    release_verified = any(
        item["code"] == "formal_benchmark_release_verified"
        for item in audit["findings"]["passes"])
    print(f"Executable input v2 verified   : {release_verified}")
    print(f"(human_review_ready alias = {audit.get('human_review_ready')}; "
          f"{audit.get('human_review_ready_semantics', '')})")
    print()
    for level in ("errors", "blockers", "warnings", "passes"):
        print(f"{level.upper()} ({len(audit['findings'][level])}):")
        for item in audit["findings"][level]:
            print(f"  [{item['code']}] {item['message']}")
        if not audit["findings"][level]:
            print("  none")
        print()
    print(audit["claim_boundary"])
