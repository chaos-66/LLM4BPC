# -*- coding: utf-8 -*-
"""Freeze the formal Stage 2 results under the contract-v2 main view.

Zero-API, read-only over frozen artifacts.  Re-scores the ALREADY-FROZEN
predictions with the formal main evaluator (``fine_gold_span``: ORIGINAL Gold
spans, no envelope merge) and writes a self-describing, immutable-style result
capsule:

    outputs/evidence/g04_fine_gold_span_formal_results_v2/
        manifest.json     -- inputs, hashes, code/config versions, rules,
                             every recomputed number (full precision), the
                             paper display value and the reproduction commands
        results.json      -- the paper-facing numbers of Table I and Table II
        REPRODUCE.md      -- human-readable reproduction recipe

The script does NOT:

- call any LLM/API,
- write to Gold, predictions, prompts, or any historical result,
- overwrite an existing capsule (it refuses unless ``--overwrite`` is given).

Usage:
    python scripts/build_stage2_fine_gold_span_freeze_v1.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bpc_hybrid.formal_stage2_evaluation import (  # noqa: E402
    SPAN_FIELDS,
    predictions_to_evaluator,
)
from bpc_hybrid.sep_c3_modular_evaluation import attempt_rows  # noqa: E402
from bpc_hybrid.sep_c3_primary_evaluation import (  # noqa: E402
    CONTRACT_ID,
    CONTRACT_PATH,
    COORDINATE_CONVENTION,
    LEGACY_COARSE_VIEW_ID,
    MATCH_RULE,
    PRIMARY_VIEW_ID,
    evaluate_primary_view,
)
from bpc_hybrid.stage2_sun_literal_overlap import SCHEMA_VERSION as EVAL_SCHEMA  # noqa: E402

CAPSULE_ID = "g04_fine_gold_span_formal_results_v2"
CAPSULE_DIR = ROOT / "outputs" / "evidence" / CAPSULE_ID
FORMAL_GOLD = ROOT / "data" / "gold" / "stage2" / "estg150_formal_gold_v1.json"
TABLE1_REPORT = (ROOT / "outputs" / "reports"
                 / "stage2_table1_paper_final_v2.json")
TABLE2_REPORT = (ROOT / "outputs" / "reports"
                 / "stage2_table2_prompt_ablation_paper_final_v3.json")
DATASET_ID = "independently_reconstructed_estg_150_v1"

TABLE1_ARMS = (
    ("sun_rule_only", "Sun et al. (rules-only)", "b0_formal_arm_v1"),
    ("direct_llm", "LLM-SE (Ours)", "direct_llm_formal_arm_v1"),
)
HISTORICAL_TABLE1 = (ROOT / "outputs" / "reports"
                     / "stage2_table1_paper_final_v1.json")
HISTORICAL_TABLE2 = (ROOT / "outputs" / "reports"
                     / "stage2_table2_prompt_ablation_paper_final_v2.json")

#: Independent offline re-computation recorded by the 2026-10 audit.  The
#: freeze is accepted only if the recomputation reproduces these values; the
#: values are NEVER copied into a result field.
AUDIT_REFERENCE = {
    "table1": {
        "sun_rule_only": {"modality_macro_f1": 0.713, "actor": 0.804,
                          "action": 0.855, "condition": 0.705,
                          "constraint": 0.491, "exception": 0.815,
                          "overall_micro_f1": 0.678},
        "direct_llm": {"modality_macro_f1": 0.769, "actor": 0.722,
                       "action": 0.880, "condition": 0.786,
                       "constraint": 0.548, "exception": 0.696,
                       "overall_micro_f1": 0.729},
        "overall_unrounded": {"sun_rule_only": 0.6778, "direct_llm": 0.7294},
    },
    "table2": {
        "000": 0.6532, "001": 0.6389, "010": 0.7155, "011": 0.7212,
        "100": 0.7373, "101": 0.7342, "110": 0.7335, "111": 0.7280,
    },
    "tolerance": 0.00005,
}

CODE_FILES = (
    "src/bpc_hybrid/sep_c3_primary_evaluation.py",
    "src/bpc_hybrid/formal_stage2_evaluation.py",
    "src/bpc_hybrid/stage2_sun_literal_overlap.py",
    "src/bpc_hybrid/sep_c3_modular_evaluation.py",
    "src/bpc_hybrid/g04_coarse_view.py",
    "scripts/build_stage2_table1_paper_final_v1.py",
    "scripts/run_v6_factorial_ablation_v1.py",
)
CONFIG_FILES = (
    CONTRACT_PATH,
    "configs/evaluation/g04_evaluation_views_contract_v1.json",
    "prompts/sun_compat/ablation_v2_factorial/manifest.json",
)


class FreezeError(RuntimeError):
    """A frozen-input or reproducibility precondition failed."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _git(*args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=ROOT, text=True,
                               encoding="utf-8", stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else "unavailable"


def _attempts(path: Path) -> list[dict[str, Any]]:
    """Prediction file -> evaluator attempt envelopes.

    Supports both frozen shapes: ``predictions.json`` (``{"records": [...]}``
    envelopes with request_status) and ``canonical_predictions.jsonl`` (one
    canonical row per line, converted by ``attempt_rows``).
    """
    if path.suffix == ".jsonl":
        rows = [json.loads(line) for line in
                path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return attempt_rows(rows)
    return predictions_to_evaluator(_read_json(path)["records"])


def _score(gold_doc: Mapping[str, Any], pred_path: Path, *,
           method_id: str) -> dict[str, Any]:
    out = evaluate_primary_view(gold_doc, _attempts(pred_path),
                                dataset_id=DATASET_ID, method_id=method_id)
    span = out["span"]
    return {
        "predictions_path": _rel(pred_path),
        "predictions_sha256": _sha256(pred_path),
        "overall_micro": span["pooled_five_span_fields"],
        "per_field": {
            field: span["span_fields"][field] for field in SPAN_FIELDS},
        "modality_label_macro_f1": out["modality_labels"]["macro_f1"],
        "modality_label_accuracy": out["modality_labels"]["accuracy"],
    }


def _round(value: Any, digits: int) -> Any:
    return None if value is None else round(float(value), digits)


def _gold_span_count(gold_doc: Mapping[str, Any]) -> int:
    """Number of reference spans under the formal main view."""
    return sum(
        sum(len(clause.get(plural) or [])
            for clause in record.get("clauses") or [])
        for record in gold_doc["records"]
        for plural in ("actors", "actions", "conditions", "constraints",
                       "exceptions"))


def _coarse_span_count(gold_doc: Mapping[str, Any]) -> int:
    """Number of reference spans under the superseded coarse envelope view."""
    from bpc_hybrid.g04_coarse_view import build_coarse_view
    return sum(
        sum(len(clause.get(plural) or [])
            for clause in record.get("clauses") or [])
        for record in build_coarse_view(dict(gold_doc))
        for plural in ("actors", "actions", "conditions", "constraints",
                       "exceptions"))


def collect() -> dict[str, Any]:
    gold_doc = _read_json(FORMAL_GOLD)
    gold_sha = _sha256(FORMAL_GOLD)

    # ---- Table I: Sun vs LLM-SE, recomputed from the frozen arms ----------
    table1: dict[str, Any] = {}
    for method_id, display, arm in TABLE1_ARMS:
        pred = ROOT / "data" / "predictions" / arm / "predictions.json"
        row = _score(gold_doc, pred, method_id=method_id)
        row.update({
            "display_name": display,
            "arm_directory": arm,
            "paper_display": {
                "modality_macro_f1": _round(row["modality_label_macro_f1"], 3),
                "overall_micro_f1": _round(row["overall_micro"]["f1"], 3),
                **{f: _round(row["per_field"][f]["f1"], 3)
                   for f in SPAN_FIELDS},
            },
        })
        table1[method_id] = row
    lead_pp = 100.0 * (table1["direct_llm"]["overall_micro"]["f1"]
                       - table1["sun_rule_only"]["overall_micro"]["f1"])

    # ---- Table II: the eight E/S/J cells --------------------------------
    table2_report = _read_json(TABLE2_REPORT)
    table2: dict[str, Any] = {}
    for arm in sorted(table2_report["arms"]):
        entry = table2_report["arms"][arm]
        if entry.get("overall_micro_f1") is None:
            raise FreezeError(f"arm {arm} is not evaluated in {TABLE2_REPORT}")
        pred = ROOT / entry["path"]
        if _sha256(pred) != entry["sha256"]:
            raise FreezeError(f"frozen predictions changed: {entry['path']}")
        row = _score(gold_doc, pred, method_id=f"direct_llm_v6_chunk_{arm}")
        if abs(row["overall_micro"]["f1"] - entry["overall_micro_f1"]) > 1e-12:
            raise FreezeError(
                f"arm {arm}: capsule report and recomputation disagree")
        row.update({
            "factors": {k: arm[i] == "1" for i, k in enumerate("ESJ")},
            "source": entry.get("source"),
            "prompt_sha256": entry.get("prompt_sha256"),
            "paper_display_micro_f1": _round(row["overall_micro"]["f1"], 4),
        })
        table2[arm] = row

    # ---- verification against the independent 2026-10 audit -------------
    tol = AUDIT_REFERENCE["tolerance"]
    checks: list[dict[str, Any]] = []
    for method_id, row in table1.items():
        ref = AUDIT_REFERENCE["table1"][method_id]
        pairs = [("overall_micro_f1", row["overall_micro"]["f1"],
                  ref["overall_micro_f1"]),
                 ("modality_macro_f1", row["modality_label_macro_f1"],
                  ref["modality_macro_f1"])]
        pairs += [(f, row["per_field"][f]["f1"], ref[f]) for f in SPAN_FIELDS]
        for name, got, want in pairs:
            checks.append({
                "scope": f"table1.{method_id}.{name}",
                "recomputed": got, "audit_reference": want,
                "matches": abs(round(got, 3) - want) <= tol,
            })
        want_unrounded = AUDIT_REFERENCE["table1"]["overall_unrounded"][method_id]
        checks.append({
            "scope": f"table1.{method_id}.overall_unrounded",
            "recomputed": row["overall_micro"]["f1"],
            "audit_reference": want_unrounded,
            "matches": abs(row["overall_micro"]["f1"] - want_unrounded) <= 5e-5,
        })
    for arm, ref in AUDIT_REFERENCE["table2"].items():
        got = table2[arm]["overall_micro"]["f1"]
        checks.append({
            "scope": f"table2.{arm}.overall_micro_f1",
            "recomputed": got, "audit_reference": ref,
            "matches": abs(round(got, 4) - ref) <= tol,
        })
    failed = [c for c in checks if not c["matches"]]
    if failed:
        raise FreezeError(
            "recomputation does not reproduce the audit reference: "
            + json.dumps(failed[:5], ensure_ascii=False))

    # ---- Table I / Table II consistency (same view, same rule) ----------
    definition = {
        "view": PRIMARY_VIEW_ID,
        "reference_side": "original annotated Gold spans (no envelope merge)",
        "prediction_side": "original validated prediction spans (unmerged)",
        "match_rule": MATCH_RULE,
        "coordinate_convention": COORDINATE_CONVENTION,
        "evaluator_schema": EVAL_SCHEMA,
        "overall_metric_id": "pooled_five_span_fields",
        "overall_aggregation": "micro over the evaluator's own counters",
        "fields": list(SPAN_FIELDS),
        "modality": "four-class label macro-F1, separate, never pooled",
        "table1_and_table2_share_definition": True,
        "note": ("Table I scores the two frozen formal arms; Table II scores "
                 "the eight frozen E/S/J cells of a DIFFERENT saved run. They "
                 "share the metric definition, not the predictions."),
    }

    return {
        "schema_version": "g04_fine_gold_span_formal_results@2.0.0",
        "capsule_id": CAPSULE_ID,
        "phase": "Part 2 (Stage 2) formal semantic-extraction evaluation",
        "nature": ("metric-implementation fix + recomputation of already "
                   "saved experiments; NOT a new experiment, NOT a retraining, "
                   "NOT a new LLM run"),
        "evaluation_contract": {
            "contract_id": CONTRACT_ID,
            "contract_path": CONTRACT_PATH,
            "contract_sha256": _sha256(ROOT / CONTRACT_PATH),
            "supersedes_for_main_report": (
                "configs/evaluation/g04_evaluation_views_contract_v1.json"),
            "historical_coarse_view_retained": LEGACY_COARSE_VIEW_ID,
        },
        "git": {
            "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
            "base_commit": _git("rev-parse", "HEAD"),
            "base_commit_subject": _git("log", "-1", "--pretty=%s"),
            "worktree_dirty_at_freeze": bool(_git("status", "--porcelain")),
        },
        "defect_fixed": {
            "description": (
                "The superseded main view merged every semantic field of a "
                "sentence into one envelope [min(start), max(end)) on the Gold "
                "side only, so a prediction between two annotated spans earned "
                "credit without overlapping any annotated span."),
            "reference_spans_original_gold": _gold_span_count(gold_doc),
            "reference_spans_superseded_coarse": _coarse_span_count(gold_doc),
            "fix": "evaluate the original Gold spans; keep the match rule",
        },
        "definition": definition,
        "inputs": {
            "gold": {"path": _rel(FORMAL_GOLD), "sha256": gold_sha,
                     "records": len(gold_doc["records"])},
            "table1_predictions": {
                m: {"path": table1[m]["predictions_path"],
                    "sha256": table1[m]["predictions_sha256"]}
                for m in table1},
            "table2_predictions": {
                arm: {"path": row["predictions_path"],
                      "sha256": row["predictions_sha256"],
                      "source": row.get("source")}
                for arm, row in table2.items()},
            "prompt_manifest": {
                "path": "prompts/sun_compat/ablation_v2_factorial/manifest.json",
                "sha256": _sha256(
                    ROOT / "prompts" / "sun_compat"
                    / "ablation_v2_factorial" / "manifest.json"),
            },
        },
        "code_version": {
            f: _sha256(ROOT / f) for f in CODE_FILES},
        "config_version": {
            f: _sha256(ROOT / f) for f in CONFIG_FILES},
        "table1_semantic_extraction": table1,
        "table1_overall_lead_pp": lead_pp,
        "table2_prompt_ablation": table2,
        "rounding": {
            "stored": "full precision; paper_display* fields carry the "
                      "rounded paper value",
            "table1": "3 decimals (F1 and macro-F1)",
            "table2": "4 decimals (Micro-F1)",
        },
        "verification": {
            "audit_reference_source": (
                "independent 2026-10 offline re-computation (audit), used as "
                "an acceptance reference only, never copied into results"),
            "checks_total": len(checks),
            "checks_passed": len(checks) - len(failed),
            "checks_failed": len(failed),
            "all_match": not failed,
        },
        "preserved_history": {
            "table1_coarse": {"path": _rel(HISTORICAL_TABLE1),
                              "sha256": _sha256(HISTORICAL_TABLE1)},
            "table2_coarse": {"path": _rel(HISTORICAL_TABLE2),
                              "sha256": _sha256(HISTORICAL_TABLE2)},
            "coarse_view_evidence": "outputs/evidence/g04_formal_coarse_view_v1",
            "note": ("historical coarse capsules and their generating "
                     "configurations are untouched; the coarse view remains "
                     "readable and reproducible"),
        },
        "reproduction": {
            "table1": ("python scripts/build_stage2_table1_paper_final_v1.py"),
            "table2": ("python scripts/run_v6_factorial_ablation_v1.py "
                       "--report-only"),
            "capsule": ("python scripts/build_stage2_fine_gold_span_freeze_v1.py"),
            "historical_coarse_table1": (
                "python scripts/build_stage2_table1_paper_final_v1.py "
                "--evaluation-view coarse_sentence_level"),
            "historical_coarse_table2": (
                "python scripts/run_v6_factorial_ablation_v1.py "
                "--report-only --evaluation-view coarse_sentence_level"),
            "llm_calls": 0,
            "network_calls": 0,
        },
        "safety": {
            "llm_api_called": False,
            "gold_modified": False,
            "predictions_modified": False,
            "prompts_modified": False,
            "stage3_touched": False,
            "paper_latex_modified": False,
            "historical_results_overwritten": False,
        },
    }


def build_reproduce_md(manifest: Mapping[str, Any]) -> str:
    t1 = manifest["table1_semantic_extraction"]
    t2 = manifest["table2_prompt_ablation"]
    lines = [
        "# Frozen formal Part 2 (Stage 2) results — original Gold spans (v2)",
        "",
        f"Capsule id: `{CAPSULE_ID}`",
        "",
        "This capsule freezes the recomputed Stage 2 paper numbers under "
        "evaluation-view contract v2 (`fine_gold_span`): the reference side "
        "is the **original annotated Gold spans**, with **no** per-field "
        "envelope merge, and the match rule is the unchanged non-one-to-one "
        "character-overlap rule.",
        "",
        "It is a metric-implementation fix plus a recomputation of already "
        "saved experiments. No LLM was called, no prediction was "
        "regenerated, no Gold, prompt, or Part 3 code was modified.",
        "",
        "## Table I — Semantic extraction (recomputed)",
        "",
        "| Element | Sun et al. | LLM-SE |",
        "|---|---:|---:|",
        f"| Modality (Macro-F1) | {t1['sun_rule_only']['paper_display']['modality_macro_f1']:.3f} "
        f"| {t1['direct_llm']['paper_display']['modality_macro_f1']:.3f} |",
    ]
    for field, label in (("actor", "Actor"), ("action", "Action"),
                         ("condition", "Condition"),
                         ("constraint", "Constraint"),
                         ("exception", "Exception")):
        lines.append(
            f"| {label} | {t1['sun_rule_only']['paper_display'][field]:.3f} "
            f"| {t1['direct_llm']['paper_display'][field]:.3f} |")
    lines += [
        f"| Overall (Micro-F1) | "
        f"{t1['sun_rule_only']['paper_display']['overall_micro_f1']:.3f} "
        f"| {t1['direct_llm']['paper_display']['overall_micro_f1']:.3f} |",
        "",
        f"Unrounded overall: Sun "
        f"{t1['sun_rule_only']['overall_micro']['f1']:.6f}, LLM-SE "
        f"{t1['direct_llm']['overall_micro']['f1']:.6f} "
        f"(lead +{manifest['table1_overall_lead_pp']:.2f} pp).",
        "",
        "## Table II — E/S/J prompt ablation (recomputed)",
        "",
        "| E | S | J | Micro-F1 |",
        "|---|---|---|---:|",
    ]
    for arm in sorted(t2):
        f = t2[arm]["factors"]
        lines.append(
            f"| {'+' if f['E'] else '-'} | {'+' if f['S'] else '-'} | "
            f"{'+' if f['J'] else '-'} | "
            f"{t2[arm]['paper_display_micro_f1']:.4f} |")
    lines += [
        "",
        "## Inputs (frozen)",
        "",
        f"- Gold: `{manifest['inputs']['gold']['path']}` "
        f"sha256 `{manifest['inputs']['gold']['sha256']}`",
    ]
    for method_id, row in t1.items():
        lines.append(f"- {row['display_name']}: `{row['predictions_path']}` "
                     f"sha256 `{row['predictions_sha256']}`")
    for arm, row in t2.items():
        lines.append(f"- cell {arm}: `{row['predictions_path']}` "
                     f"sha256 `{row['predictions_sha256']}`")
    lines += [
        "",
        "## Reproduction",
        "",
        "```bash",
        manifest["reproduction"]["table1"],
        manifest["reproduction"]["table2"],
        manifest["reproduction"]["capsule"],
        "```",
        "",
        "Historical coarse numbers remain reproducible through:",
        "",
        "```bash",
        manifest["reproduction"]["historical_coarse_table1"],
        manifest["reproduction"]["historical_coarse_table2"],
        "```",
        "",
        "## Rules",
        "",
        f"- view: `{manifest['definition']['view']}`",
        f"- match rule: `{manifest['definition']['match_rule']}`",
        f"- coordinates: {manifest['definition']['coordinate_convention']}",
        "- assignment: none (independent overlap coverage, not one-to-one)",
        "- Overall = micro pooling over actor/action/condition/constraint/"
        "exception",
        "- Modality = four-class label macro-F1, reported separately",
        "",
        "## Acceptance",
        "",
        f"- {manifest['verification']['checks_passed']}/"
        f"{manifest['verification']['checks_total']} checks reproduce the "
        "independent audit reference.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    manifest_path = CAPSULE_DIR / "manifest.json"
    if manifest_path.exists() and not args.overwrite:
        raise SystemExit(
            f"{_rel(manifest_path)} already exists; pass --overwrite to "
            "regenerate the capsule")

    manifest = collect()
    CAPSULE_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        "capsule_id": CAPSULE_ID,
        "view": PRIMARY_VIEW_ID,
        "table1": {
            m: {"display_name": r["display_name"], **r["paper_display"],
                "overall_micro_f1_unrounded": r["overall_micro"]["f1"]}
            for m, r in manifest["table1_semantic_extraction"].items()},
        "table1_overall_lead_pp": manifest["table1_overall_lead_pp"],
        "table2": {
            arm: {"factors": r["factors"],
                  "micro_f1": r["paper_display_micro_f1"],
                  "micro_f1_unrounded": r["overall_micro"]["f1"]}
            for arm, r in manifest["table2_prompt_ablation"].items()},
    }
    (CAPSULE_DIR / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    (CAPSULE_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2,
                   sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    (CAPSULE_DIR / "REPRODUCE.md").write_text(
        build_reproduce_md(manifest), encoding="utf-8", newline="\n")

    print(f"wrote {_rel(CAPSULE_DIR / 'manifest.json')}")
    print(f"wrote {_rel(CAPSULE_DIR / 'results.json')}")
    print(f"wrote {_rel(CAPSULE_DIR / 'REPRODUCE.md')}")
    t1 = manifest["table1_semantic_extraction"]
    print(f"Table I  Sun {t1['sun_rule_only']['overall_micro']['f1']:.4f}  "
          f"LLM-SE {t1['direct_llm']['overall_micro']['f1']:.4f}  "
          f"lead {manifest['table1_overall_lead_pp']:+.2f} pp")
    print("Table II " + " ".join(
        f"{arm}={row['overall_micro']['f1']:.4f}"
        for arm, row in sorted(manifest["table2_prompt_ablation"].items())))
    print(f"audit reference: {manifest['verification']['checks_passed']}/"
          f"{manifest['verification']['checks_total']} checks match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
