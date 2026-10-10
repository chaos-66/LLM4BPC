# -*- coding: utf-8 -*-
"""Build the paper Table 1 capsule: Stage 2 EStG-150 extraction comparison.

Zero-API, read-only over frozen artifacts.  Reads ONLY:

- the published formal Stage 2 Gold
  ``data/gold/stage2/estg150_formal_gold_v1.json``
- the two frozen formal arms' prediction envelopes
  ``data/predictions/b0_formal_arm_v1/predictions.json``      (Sun rules-only)
  ``data/predictions/direct_llm_formal_arm_v1/predictions.json`` (LLM-SE)

and the frozen evaluator (``formal_stage2_evaluation`` +
``stage2_sun_literal_overlap`` + the G0.4 coarse transform).

Writes ONE report pair under ``outputs/reports/``:

- ``stage2_table1_paper_final_v1.json``
- ``stage2_table1_paper_final_v1.md``

Contract notes (G0.4 evaluation-views contract, user-authorized 2026-08-11):

- the reported OVERALL score is ``pooled_five_span_fields``: a micro/pooled
  P/R/F1 over the five span-bearing fields
  (actor/action/condition/constraint/exception);
- modality is reported as a four-class LABEL macro-F1, never as a span and
  never folded into the overall score (modality evidence spans are not
  recoverable from the published decision-only Gold).

Usage:
    python scripts/build_stage2_table1_paper_final_v1.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bpc_hybrid.formal_stage2_evaluation import (  # noqa: E402
    SPAN_FIELDS,
    evaluate_modality_labels,
    evaluate_span_metrics,
    published_gold_to_evaluator,
    predictions_to_evaluator,
)
from bpc_hybrid.g04_coarse_view import build_coarse_view  # noqa: E402

FORMAL_GOLD = ROOT / "data" / "gold" / "stage2" / "estg150_formal_gold_v1.json"
DATASET_ID = "independently_reconstructed_estg_150_v1"

#: Display order and paper-facing names of the two formal arms.  The method
#: ids are the frozen ids used by the formal capsules; the display names are
#: what the paper prints.
ARMS = (
    {
        "method_id": "sun_rule_only",
        "display_name": "Sun et al. (rules-only)",
        "arm": "b0_formal_arm_v1",
    },
    {
        "method_id": "direct_llm",
        "display_name": "Ours (LLM-SE)",
        "arm": "direct_llm_formal_arm_v1",
    },
)

FIELD_LABELS = {
    "actor": "Actor",
    "action": "Action",
    "condition": "Condition",
    "constraint": "Constraint",
    "exception": "Exception",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def collect() -> dict[str, Any]:
    gold_doc = _load_json(FORMAL_GOLD)
    coarse_gold = build_coarse_view(gold_doc)
    fine_gold = published_gold_to_evaluator(gold_doc)

    arms: dict[str, Any] = {}
    for spec in ARMS:
        pred_path = (ROOT / "data" / "predictions" / spec["arm"]
                     / "predictions.json")
        attempts = predictions_to_evaluator(
            _load_json(pred_path)["records"])
        coarse = evaluate_span_metrics(
            coarse_gold, attempts, dataset_id=DATASET_ID,
            method_id=spec["method_id"], view="coarse_sentence_level")
        labels = evaluate_modality_labels(fine_gold, attempts)
        arms[spec["method_id"]] = {
            "display_name": spec["display_name"],
            "arm_directory": spec["arm"],
            "predictions_path": str(pred_path.relative_to(ROOT)).replace("\\", "/"),
            "predictions_sha256": _sha256(pred_path),
            "overall_pooled_five_span_fields": coarse["pooled_five_span_fields"],
            "span_fields": coarse["span_fields"],
            "modality_labels": {
                "accuracy": labels["accuracy"],
                "macro_f1": labels["macro_f1"],
                "classes": labels["classes"],
                "per_class": labels["per_class"],
                "records": labels["records"],
                "unlabeled_predictions": labels["unlabeled_predictions"],
            },
            "view": coarse["view"],
            "pooled_metric_id": coarse["pooled_metric_id"],
        }

    # ---- deltas in percentage points (LLM-SE minus rules-only) ----
    base_id, ours_id = ARMS[0]["method_id"], ARMS[1]["method_id"]
    base, ours = arms[base_id], arms[ours_id]
    field_deltas = {
        field: {
            "baseline_f1": base["span_fields"][field]["f1"],
            "ours_f1": ours["span_fields"][field]["f1"],
            "delta_f1": ours["span_fields"][field]["f1"]
            - base["span_fields"][field]["f1"],
            "delta_f1_pp": 100.0 * (ours["span_fields"][field]["f1"]
                                    - base["span_fields"][field]["f1"]),
            "winner": ("ours" if ours["span_fields"][field]["f1"]
                       > base["span_fields"][field]["f1"]
                       else "baseline" if ours["span_fields"][field]["f1"]
                       < base["span_fields"][field]["f1"] else "tie"),
        }
        for field in SPAN_FIELDS
    }
    pooled_base = base["overall_pooled_five_span_fields"]
    pooled_ours = ours["overall_pooled_five_span_fields"]
    pooled_delta_pp = 100.0 * (pooled_ours["f1"] - pooled_base["f1"])

    return {
        "schema_version": "stage2_table1_paper_final@1.0.0",
        "report_id": "stage2_table1_paper_final_v1",
        "dataset_id": DATASET_ID,
        "sample_count": len(coarse_gold),
        "view": "coarse_sentence_level",
        "evaluation_contract": {
            "contract": "g04_evaluation_views_contract@1.0.0",
            "overall_metric_id": "pooled_five_span_fields",
            "overall_aggregation": "micro_pooled_over_five_span_bearing_fields",
            "overall_fields": list(SPAN_FIELDS),
            "modality_policy": (
                "four-class label macro-F1 reported separately; modality "
                "evidence spans are unavailable in the published "
                "decision-only Gold and are never aggregated into the overall "
                "score"),
            "match_rule": (
                "independent same-field any-nonempty-character-span "
                "intersection (Sun literal-overlap contract)"),
        },
        "source_artifacts": {
            "gold_path": str(FORMAL_GOLD.relative_to(ROOT)).replace("\\", "/"),
            "gold_sha256": _sha256(FORMAL_GOLD),
            "evaluator": "bpc_hybrid.formal_stage2_evaluation + "
                         "bpc_hybrid.stage2_sun_literal_overlap + "
                         "bpc_hybrid.g04_coarse_view",
            "llm_calls_performed": 0,
        },
        "arms": arms,
        "field_deltas_ours_minus_baseline": field_deltas,
        "overall_pooled_delta_pp": pooled_delta_pp,
        "fields_won_by_ours": sum(
            1 for v in field_deltas.values() if v["winner"] == "ours"),
        "fields_won_by_baseline": sum(
            1 for v in field_deltas.values() if v["winner"] == "baseline"),
    }


def render_markdown(report: dict[str, Any]) -> str:
    base_id, ours_id = ARMS[0]["method_id"], ARMS[1]["method_id"]
    base, ours = report["arms"][base_id], report["arms"][ours_id]
    lines: list[str] = []
    lines.append("# Table 1 — Stage 2 regulatory information extraction "
                 "(EStG-150, coarse sentence view)")
    lines.append("")
    lines.append("Report id: `stage2_table1_paper_final_v1` · zero new LLM calls "
                 "· regenerated from frozen Gold + frozen arm predictions.")
    lines.append("")
    lines.append("## Main table")
    lines.append("")
    header = ("| Method | Modality (macro-F1) | "
              + " | ".join(FIELD_LABELS[f] for f in SPAN_FIELDS)
              + " | **Overall (pooled 5)** |")
    sep = "|---" * (len(SPAN_FIELDS) + 3) + "|"
    lines.append(header)
    lines.append(sep)
    for method_id in (base_id, ours_id):
        arm = report["arms"][method_id]
        other_id = ours_id if method_id == base_id else base_id
        other = report["arms"][other_id]
        cells = []
        for field in SPAN_FIELDS:
            mine = arm["span_fields"][field]["f1"]
            text = f"{mine:.3f}"
            if mine > other["span_fields"][field]["f1"]:
                text = f"**{text}**"
            cells.append(text)
        mod = arm["modality_labels"]["macro_f1"]
        mod_text = f"{mod:.3f}"
        if mod > other["modality_labels"]["macro_f1"]:
            mod_text = f"**{mod_text}**"
        pooled = arm["overall_pooled_five_span_fields"]["f1"]
        pooled_text = f"{pooled:.3f}"
        if pooled > other["overall_pooled_five_span_fields"]["f1"]:
            pooled_text = f"**{pooled_text}**"
        lines.append(f"| {arm['display_name']} | {mod_text} | "
                     + " | ".join(cells) + f" | {pooled_text} |")
    lines.append("")
    lines.append("## Overall metric (pooled five span-bearing fields)")
    lines.append("")
    lines.append("| Method | Precision | Recall | F1 | n (Gold spans) | "
                 "n (extracted) |")
    lines.append("|---|---|---|---|---|---|")
    for method_id in (base_id, ours_id):
        arm = report["arms"][method_id]
        p = arm["overall_pooled_five_span_fields"]
        lines.append(f"| {arm['display_name']} | {p['precision']:.4f} | "
                     f"{p['recall']:.4f} | {p['f1']:.4f} | "
                     f"{p['ground_truth']} | {p['extracted']} |")
    lines.append("")
    lines.append(f"Δ Overall (pooled F1, Ours − rules-only): "
                 f"**{report['overall_pooled_delta_pp']:+.2f} pp**")
    lines.append("")
    lines.append("## Per-field deltas (Ours − rules-only, percentage points)")
    lines.append("")
    lines.append("| Field | Rules-only F1 | Ours F1 | Δ (pp) | Higher |")
    lines.append("|---|---|---|---|---|")
    winner_names = {"ours": "Ours", "baseline": "rules-only", "tie": "tie"}
    for field in SPAN_FIELDS:
        d = report["field_deltas_ours_minus_baseline"][field]
        lines.append(f"| {FIELD_LABELS[field]} | {d['baseline_f1']:.3f} | "
                     f"{d['ours_f1']:.3f} | {d['delta_f1_pp']:+.2f} | "
                     f"{winner_names[d['winner']]} |")
    lines.append("")
    lines.append("## Modality label classification (reported separately)")
    lines.append("")
    lines.append("| Method | Accuracy | Macro-F1 | Unlabeled predictions |")
    lines.append("|---|---|---|---|")
    for method_id in (base_id, ours_id):
        arm = report["arms"][method_id]
        m = arm["modality_labels"]
        lines.append(f"| {arm['display_name']} | {m['accuracy']:.4f} | "
                     f"{m['macro_f1']:.4f} | {m['unlabeled_predictions']} |")
    lines.append("")
    lines.append("## Table note (must be carried into the paper)")
    lines.append("")
    lines.append("Modality is a four-class **label** macro-F1 over "
                 "{obligation, permission, prohibition, definition}. The other "
                 "five columns are span F1 under the fixed Sun literal-overlap "
                 "contract. **Overall is the pooled (micro) F1 over the five "
                 "span-bearing fields only.** Modality evidence spans are not "
                 "recoverable from the published decision-only Gold, so they "
                 "are excluded from the overall score and never zeroed.")
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
    lines.append(f"- Gold: `{report['source_artifacts']['gold_path']}` "
                 f"(sha256 `{report['source_artifacts']['gold_sha256']}`)")
    for method_id in (base_id, ours_id):
        arm = report["arms"][method_id]
        lines.append(f"- {arm['display_name']}: `{arm['predictions_path']}` "
                     f"(sha256 `{arm['predictions_sha256']}`)")
    lines.append(f"- New LLM calls: {report['source_artifacts']['llm_calls_performed']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default=str(ROOT / "outputs" / "reports"))
    args = parser.parse_args()

    report = collect()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "stage2_table1_paper_final_v1.json"
    md_path = out_dir / "stage2_table1_paper_final_v1.md"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    print()
    # Windows consoles in this repo may use a legacy code page; never let a
    # non-ASCII glyph turn a successful build into a non-zero exit.
    try:
        print(render_markdown(report))
    except UnicodeEncodeError:
        sys.stdout.buffer.write(
            render_markdown(report).encode("utf-8", errors="replace"))
        sys.stdout.buffer.write(b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
