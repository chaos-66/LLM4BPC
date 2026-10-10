# -*- coding: utf-8 -*-
"""Build the paper Table 2 capsule: Stage 2 prompt-design ablation.

Zero-API, read-only over frozen artifacts.  Re-scores the ALREADY-EXECUTED
prompt ablation arms (450 real calls, DeepSeek-V4-Pro-0813, 2026-08-29/30)
under the SAME evaluation contract and the SAME overall metric family as the
paper's Table 1, so the two tables are directly comparable.

Why this script exists
----------------------
The historical report ``d1_prompt_factorial_results_v1.json`` scores the arms
with a pooled SIX-field metric that folds in modality evidence spans.  Table 1
reports the contract-aligned POOLED FIVE-span-field metric.  Comparing the two
directly would be a metric-definition error.  This script recomputes every arm
from the persisted canonical predictions using
``bpc_hybrid.sep_c3_modular_evaluation.evaluate_coarse`` (the frozen coarse
five-field main view) and reports:

- ``coarse_five_field_micro`` -- THE overall metric (identical family to the
  Table 1 "Overall (pooled 5)" column);
- ``coarse_five_field_mean_f1`` -- per-field-F1 arithmetic mean, as a
  secondary/complementary view;
- per-field F1, modality-label metrics, and per-sample matched counts so a
  PAIRED per-sample comparison is possible.

Reads ONLY:
- ``data/gold/stage2/estg150_formal_gold_v1.json``
- the four arms' ``canonical_predictions.jsonl`` under ``outputs/development``

Writes ONE report pair under ``outputs/reports/``:
- ``stage2_table2_prompt_ablation_paper_final_v1.json``
- ``stage2_table2_prompt_ablation_paper_final_v1.md``

CAVEAT recorded in the report: the per-arm artifacts under
``outputs/development/`` are git-ignored, so this re-score is reproducible on
this machine but not from a fresh clone.  The original aggregate report
``d1_prompt_factorial_results_v1.json`` IS tracked and pins the six-field
numbers plus every arm's prompt/response hash.

Usage:
    python scripts/build_stage2_table2_prompt_ablation_v1.py
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

from bpc_hybrid.formal_stage2_evaluation import SPAN_FIELDS  # noqa: E402
from bpc_hybrid.g04_coarse_view import build_coarse_view  # noqa: E402
from bpc_hybrid.sep_c3_modular_evaluation import (  # noqa: E402
    attempt_rows,
    evaluate_coarse,
)
from bpc_hybrid.stage2_sun_literal_overlap import (  # noqa: E402
    evaluate_sun_literal_overlap,
)

FORMAL_GOLD = ROOT / "data" / "gold" / "stage2" / "estg150_formal_gold_v1.json"
DEV = ROOT / "outputs" / "development"

#: (arm id, display name, module removed, canonical predictions path, prompt sha)
ARMS: tuple[dict[str, Any], ...] = (
    {
        "arm_id": "D-full-0813",
        "display_name": "Full (all modules)",
        "removed": "-",
        "predictions": (DEV / "barrientos_ablation_suite_v2" / "D-full-0813"
                        / "repeat-01" / "canonical_predictions.jsonl"),
        "raw_responses": (DEV / "barrientos_ablation_suite_v2" / "D-full-0813"
                          / "repeat-01" / "raw_responses.jsonl"),
        "prompt_name": "direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md",
        "prompt_sha256": ("3aa64877cd4c4dae9f13cb40d102c3c9b04cc9bee5d478"
                          "c34ad04621c0ede895"),
    },
    {
        "arm_id": "D-no-semantic-examples-0813",
        "display_name": "Full - Examples (E)",
        "removed": "semantic examples (E)",
        "predictions": (DEV / "d1_prompt_factorial_ablation_v2"
                        / "D-no-semantic-examples-0813" / "repeat-01"
                        / "canonical_predictions.jsonl"),
        "raw_responses": (DEV / "d1_prompt_factorial_ablation_v2"
                          / "D-no-semantic-examples-0813" / "repeat-01"
                          / "raw_responses.jsonl"),
        "prompt_name": "direct_llm_no_semantic_examples_prompt_v2.md",
        "prompt_sha256": ("261d7b23e015c9faa3bcb75ad49c440dfdd96c00567fb498"
                          "edeed939f364f072"),
    },
    {
        "arm_id": "D-no-semantic-guidance-0813",
        "display_name": "Full - Guidance (S)",
        "removed": "semantic interpretation guidance (S)",
        "predictions": (DEV / "d1_prompt_factorial_ablation_v2"
                        / "D-no-semantic-guidance-0813" / "repeat-01"
                        / "canonical_predictions.jsonl"),
        "raw_responses": (DEV / "d1_prompt_factorial_ablation_v2"
                          / "D-no-semantic-guidance-0813" / "repeat-01"
                          / "raw_responses.jsonl"),
        "prompt_name": "direct_llm_no_semantic_guidance_prompt_v2.md",
        "prompt_sha256": ("fa5e9f0043809428b8034a08cb58ff0e98a7e5b69c5be99f"
                          "88286724217f0aa3"),
    },
    {
        "arm_id": "D-no-explicit-json-contract-0813",
        "display_name": "Full - JSON discipline (J)",
        "removed": "explicit JSON output contract (J)",
        "predictions": (DEV / "d1_prompt_factorial_ablation_v2"
                        / "D-no-explicit-json-contract-0813" / "repeat-01"
                        / "canonical_predictions.jsonl"),
        "raw_responses": (DEV / "d1_prompt_factorial_ablation_v2"
                          / "D-no-explicit-json-contract-0813" / "repeat-01"
                          / "raw_responses.jsonl"),
        "prompt_name": "direct_llm_no_explicit_json_contract_prompt_v2.md",
        "prompt_sha256": ("0b7b93ad30e3d72f20fb809b48fdda694a2242233f203234"
                          "a3f5d8dc91ab5da7"),
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


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _per_sample_f1(coarse_gold: list[dict[str, Any]],
                   attempts: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Per-sample pooled five-field F1 AND per-sample per-field F1.

    The frozen evaluator emits aggregate counters only, so each sample is
    scored as a single-record population.  Membership is a single shared
    sample_id, so the evaluator's membership check still passes.

    Returns ``{sample_id: {"pooled": f1, "<field>": f1, ...}}``.
    """
    gold_by_id = {r["sample_id"]: r for r in coarse_gold}
    out: dict[str, dict[str, float]] = {}
    for attempt in attempts:
        sid = attempt["sample_id"]
        report = evaluate_sun_literal_overlap(
            [gold_by_id[sid]], [attempt],
            dataset_id="independently_reconstructed_estg_150_v1",
            method_id="per_sample")
        counts = {f: report["per_field"][f] for f in SPAN_FIELDS}
        extracted = sum(c["extracted"] for c in counts.values())
        ground_truth = sum(c["ground_truth"] for c in counts.values())
        matched_predictions = sum(c["matched_predictions"] for c in counts.values())
        matched_ground_truth = sum(c["matched_ground_truth"] for c in counts.values())
        precision = matched_predictions / extracted if extracted else 0.0
        recall = matched_ground_truth / ground_truth if ground_truth else 0.0
        row = {f: float(counts[f]["f1"]) for f in SPAN_FIELDS}
        row["pooled"] = (2.0 * precision * recall / (precision + recall)
                         if (precision + recall) else 0.0)
        out[sid] = row
    return out


def _paired_bootstrap(a: dict[str, dict[str, float]],
                      b: dict[str, dict[str, float]], *,
                      key: str = "pooled",
                      resamples: int = 10000, seed: int = 20260921,
                      confidence: float = 0.95) -> dict[str, Any]:
    """Percentile bootstrap CI for mean(a[key] - b[key]) over paired ids."""
    import random

    ids = sorted(set(a) & set(b))
    diffs = [a[sid][key] - b[sid][key] for sid in ids]
    n = len(diffs)
    if not n:
        return {"n": 0, "mean_delta": None, "ci_low": None, "ci_high": None,
                "excludes_zero": None}
    rng = random.Random(seed)
    means = []
    for _ in range(resamples):
        means.append(sum(diffs[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    lo_idx = int((1.0 - confidence) / 2.0 * resamples)
    hi_idx = min(resamples - 1, int((1.0 + confidence) / 2.0 * resamples))
    return {
        "n": n,
        "mean_delta": sum(diffs) / n,
        "ci_low": means[lo_idx],
        "ci_high": means[hi_idx],
        "excludes_zero": (means[lo_idx] > 0.0) or (means[hi_idx] < 0.0),
        "resamples": resamples,
        "seed": seed,
        "confidence": confidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default=str(ROOT / "outputs" / "reports"))
    args = parser.parse_args()

    gold_doc = json.loads(FORMAL_GOLD.read_text(encoding="utf-8"))
    coarse_gold = build_coarse_view(gold_doc)
    gold_ids = {r["sample_id"] for r in coarse_gold}

    missing = [a["arm_id"] for a in ARMS if not a["predictions"].is_file()]
    if missing:
        raise SystemExit(
            "arm artifacts unavailable: " + ", ".join(missing)
            + "\nThese live under the git-ignored outputs/development/ tree.")

    results: dict[str, Any] = {}
    per_sample: dict[str, dict[str, float]] = {}
    for spec in ARMS:
        rows = _read_jsonl(spec["predictions"])
        attempts = attempt_rows(rows)
        ids = {a["sample_id"] for a in attempts}
        if ids != gold_ids:
            raise SystemExit(
                f"{spec['arm_id']}: sample_id set differs from Gold "
                f"(missing={sorted(gold_ids - ids)[:5]}, "
                f"extra={sorted(ids - gold_ids)[:5]})")
        evaluation = evaluate_coarse(gold_doc, attempts,
                                     method_id=spec["arm_id"])
        per_sample[spec["arm_id"]] = _per_sample_f1(coarse_gold, attempts)
        results[spec["arm_id"]] = {
            "display_name": spec["display_name"],
            "removed_module": spec["removed"],
            "prompt_name": spec["prompt_name"],
            "predictions_path": str(
                spec["predictions"].relative_to(ROOT)).replace("\\", "/"),
            "predictions_sha256": _sha256(spec["predictions"]),
            "raw_responses_path": str(
                spec["raw_responses"].relative_to(ROOT)).replace("\\", "/"),
            "raw_responses_sha256": (
                _sha256(spec["raw_responses"])
                if spec["raw_responses"].is_file() else None),
            "overall_pooled_five_span_fields":
                evaluation["coarse_five_field_micro"],
            "coarse_five_field_mean_f1": evaluation["coarse_five_field_mean_f1"],
            "span_fields": evaluation["five_fields"],
            "modality_labels": {
                "accuracy": evaluation["modality_labels"]["accuracy"],
                "macro_f1": evaluation["modality_labels"]["macro_f1"],
                "unlabeled_predictions":
                    evaluation["modality_labels"]["unlabeled_predictions"],
            },
            "denominator": evaluation["denominator"],
            "failed_count": evaluation["failed_count"],
        }

    base_id = ARMS[0]["arm_id"]
    base = results[base_id]
    deltas = {}
    for spec in ARMS:
        arm = results[spec["arm_id"]]
        paired = _paired_bootstrap(per_sample[spec["arm_id"]],
                                   per_sample[base_id])
        deltas[spec["arm_id"]] = {
            "delta_overall_f1": (
                arm["overall_pooled_five_span_fields"]["f1"]
                - base["overall_pooled_five_span_fields"]["f1"]),
            "delta_overall_f1_pp": 100.0 * (
                arm["overall_pooled_five_span_fields"]["f1"]
                - base["overall_pooled_five_span_fields"]["f1"]),
            "delta_mean_f1_pp": 100.0 * (
                arm["coarse_five_field_mean_f1"]
                - base["coarse_five_field_mean_f1"]),
            "per_field_delta_f1_pp": {
                field: 100.0 * (arm["span_fields"][field]["f1"]
                                - base["span_fields"][field]["f1"])
                for field in SPAN_FIELDS
            },
            "paired_per_sample_f1_delta": paired,
            "paired_per_field_delta": {
                field: _paired_bootstrap(per_sample[spec["arm_id"]],
                                         per_sample[base_id], key=field)
                for field in SPAN_FIELDS
            },
        }

    report = {
        "schema_version": "stage2_table2_prompt_ablation_paper_final@1.0.0",
        "report_id": "stage2_table2_prompt_ablation_paper_final_v1",
        "dataset_id": "independently_reconstructed_estg_150_v1",
        "sample_count": len(coarse_gold),
        "view": "coarse_sentence_level",
        "prompt_family": {
            "base_prompt": ("prompts/sun_compat/"
                            "direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md"),
            "base_prompt_sha256": ARMS[0]["prompt_sha256"],
            "note": ("all four arms are derived from the SAME monolithic v6 "
                     "prompt that produced the frozen LLM-SE formal arm "
                     "reported in Table 1"),
        },
        "evaluation_contract": {
            "contract": "g04_evaluation_views_contract@1.0.0",
            "overall_metric_id": "coarse_five_field_micro_f1",
            "overall_aggregation": "micro_pooled_over_five_span_bearing_fields",
            "overall_fields": list(SPAN_FIELDS),
            "modality_policy": ("separate four-class label metrics; modality "
                                "evidence spans never aggregated"),
            "metric_family_matches_table1": True,
        },
        "execution_provenance": {
            "real_llm_calls": 450,
            "model_release": "DeepSeek-V4-Pro-0813",
            "sampling": "temperature=0, top_p=1, retry=0",
            "n_per_arm": 150,
            "original_aggregate_report": (
                "outputs/reports/d1_prompt_factorial_results_v1.json"),
            "new_llm_calls_for_this_report": 0,
        },
        "reproducibility_caveat": (
            "per-arm predictions live under the git-ignored "
            "outputs/development/ tree, so this re-score is reproducible on "
            "this machine but not from a fresh clone; the tracked aggregate "
            "report pins the six-field numbers and every arm hash"),
        "arms": results,
        "deltas_vs_full": deltas,
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "stage2_table2_prompt_ablation_paper_final_v1.json"
    md_path = out_dir / "stage2_table2_prompt_ablation_paper_final_v1.md"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")

    # ---- markdown ----
    lines: list[str] = []
    lines.append("# Table 2 - Stage 2 prompt-design ablation (EStG-150, "
                 "coarse sentence view)")
    lines.append("")
    lines.append("Report id: `stage2_table2_prompt_ablation_paper_final_v1` - "
                 "re-scored from the existing 450 real calls, **0 new LLM "
                 "calls** - same metric family as Table 1.")
    lines.append("")
    lines.append("## Main table")
    lines.append("")
    lines.append("| Prompt arm | Module removed | Modality (macro-F1) | "
                 + " | ".join(FIELD_LABELS[f] for f in SPAN_FIELDS)
                 + " | Overall (pooled 5) | d Overall vs Full (pp) |")
    lines.append("|---" * (len(SPAN_FIELDS) + 4) + "|")
    for spec in ARMS:
        arm = results[spec["arm_id"]]
        d = deltas[spec["arm_id"]]
        cells = [f"{arm['span_fields'][f]['f1']:.3f}" for f in SPAN_FIELDS]
        lines.append(
            f"| {arm['display_name']} | {arm['removed_module']} | "
            f"{arm['modality_labels']['macro_f1']:.3f} | "
            + " | ".join(cells)
            + f" | {arm['overall_pooled_five_span_fields']['f1']:.4f} | "
            f"{d['delta_overall_f1_pp']:+.2f} |")
    lines.append("")
    lines.append("## Overall metric detail (pooled five span-bearing fields)")
    lines.append("")
    lines.append("| Prompt arm | Precision | Recall | F1 | Gold spans | "
                 "Extracted | Mean-of-5 F1 | Valid outputs |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for spec in ARMS:
        arm = results[spec["arm_id"]]
        p = arm["overall_pooled_five_span_fields"]
        lines.append(
            f"| {arm['display_name']} | {p['precision']:.4f} | "
            f"{p['recall']:.4f} | {p['f1']:.4f} | {p['ground_truth']} | "
            f"{p['extracted']} | {arm['coarse_five_field_mean_f1']:.4f} | "
            f"{arm['denominator'] - arm['failed_count']}/{arm['denominator']} |")
    lines.append("")
    lines.append("## Per-field delta vs Full (percentage points)")
    lines.append("")
    lines.append("| Prompt arm | " + " | ".join(FIELD_LABELS[f]
                                               for f in SPAN_FIELDS) + " |")
    lines.append("|---" * (len(SPAN_FIELDS) + 1) + "|")
    for spec in ARMS:
        d = deltas[spec["arm_id"]]
        lines.append(f"| {results[spec['arm_id']]['display_name']} | "
                     + " | ".join(
                         f"{d['per_field_delta_f1_pp'][f]:+.2f}"
                         for f in SPAN_FIELDS) + " |")
    lines.append("")
    lines.append("## Paired per-sample comparison vs Full (10,000 resamples)")
    lines.append("")
    lines.append("| Prompt arm | n | mean delta F1 (pp) | 95% CI (pp) | "
                 "CI excludes 0 |")
    lines.append("|---|---|---|---|---|")
    for spec in ARMS:
        d = deltas[spec["arm_id"]]
        p = d["paired_per_sample_f1_delta"]
        if p["n"]:
            lines.append(
                f"| {results[spec['arm_id']]['display_name']} | {p['n']} | "
                f"{100.0 * p['mean_delta']:+.3f} | "
                f"[{100.0 * p['ci_low']:+.3f}, {100.0 * p['ci_high']:+.3f}] | "
                f"{'yes' if p['excludes_zero'] else 'no'} |")
    lines.append("")
    lines.append("## Paired per-field deltas vs Full (pp, 95% CI, 10,000 "
                 "resamples)")
    lines.append("")
    lines.append("| Prompt arm | Field | mean delta (pp) | 95% CI (pp) | "
                 "CI excludes 0 |")
    lines.append("|---|---|---|---|---|")
    for spec in ARMS:
        if spec["arm_id"] == base_id:
            continue
        d = deltas[spec["arm_id"]]
        for field in SPAN_FIELDS:
            p = d["paired_per_field_delta"][field]
            lines.append(
                f"| {results[spec['arm_id']]['display_name']} | "
                f"{FIELD_LABELS[field]} | {100.0 * p['mean_delta']:+.3f} | "
                f"[{100.0 * p['ci_low']:+.3f}, {100.0 * p['ci_high']:+.3f}] | "
                f"{'yes' if p['excludes_zero'] else 'no'} |")
    lines.append("")
    lines.append("## Reading (what the ablation actually supports)")
    lines.append("")
    lines.append("**The pooled overall F1 does not separate any arm from Full**: "
                 "all three deletion deltas have 95% CIs that contain zero. "
                 "The honest conclusion is therefore NOT 'every module lowers "
                 "overall F1 when removed'.")
    lines.append("")
    lines.append("The per-field paired test does separate some field-level "
                 "effects, and they are **mixed in sign**, so they do not "
                 "support a simple 'each module is necessary' claim either:")
    lines.append("")
    lines.append("- **Examples (E)**: removing E *raises* Condition F1 "
                 "(significant); Action/Constraint move the other way without "
                 "a CI excluding zero. E therefore has a field-specific "
                 "trade-off, not a uniform positive contribution.")
    lines.append("- **Guidance (S)**: no field effect is statistically "
                 "separable from noise at this sample size. S is not "
                 "established as contributing on this metric.")
    lines.append("- **JSON discipline (J)**: removing J *raises* Action F1 "
                 "(significant) while Condition moves down; all four arms "
                 "already produce valid JSON and a valid canonical schema at "
                 "150/150. J is therefore the BASE OUTPUT CONTRACT (an "
                 "interface/validity guarantee), NOT an accuracy-improving "
                 "module.")
    lines.append("")
    lines.append("### Structural limits of this ablation (state these in the "
                 "paper)")
    lines.append("")
    lines.append("1. **E and S carry overlapping information.** The examples "
                 "already illustrate the guidance rules, so a leave-one-out "
                 "arm measures the *residual* after the other carrier is "
                 "removed, not the module's standalone contribution. This is "
                 "the recorded reason the modular single-factor ablation was "
                 "superseded by the full 2^3 design.")
    lines.append("2. **Power.** The coarse view has only 459 Gold spans over "
                 "150 samples, so small overall effects are not separable from "
                 "sampling noise at one repeat per arm.")
    lines.append("3. **One repeat per arm.** Per-cell repeats were designed "
                 "but never authorized, so no variance estimate across "
                 "re-executions exists.")
    lines.append("")
    lines.append("The paired per-sample CI remains the appropriate evidence "
                 "here: it uses the SAME 150 samples for every arm, so it does "
                 "not depend on the across-arm execution order.")
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
    lines.append(f"- Gold: `data/gold/stage2/estg150_formal_gold_v1.json`")
    lines.append(f"- Real LLM calls behind these arms: "
                 f"{report['execution_provenance']['real_llm_calls']} "
                 f"({report['execution_provenance']['model_release']})")
    lines.append(f"- New LLM calls for this report: 0")
    for spec in ARMS:
        arm = results[spec["arm_id"]]
        lines.append(f"- {arm['display_name']}: prompt `{arm['prompt_name']}`, "
                     f"predictions sha256 `{arm['predictions_sha256'][:16]}...`")
    lines.append("")
    lines.append(f"**Reproducibility caveat:** {report['reproducibility_caveat']}.")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    print()
    try:
        print("\n".join(lines))
    except UnicodeEncodeError:
        sys.stdout.buffer.write("\n".join(lines).encode("utf-8",
                                                        errors="replace"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
