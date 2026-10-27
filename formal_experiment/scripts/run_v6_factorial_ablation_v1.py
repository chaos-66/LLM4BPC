# -*- coding: utf-8 -*-
"""Run the v6 prompt-family E/S/J 2^3 factorial ablation.

This runner is a thin adapter over the already-audited
``run_sep_c3_modular_ablation_v1`` call/parse/persist/evaluate stack.  It
replaces only the prompt side with the v6 chunk-assembly prompts under
``prompts/sun_compat/ablation_v2_factorial`` and evaluates all eight arms with
the same frozen EStG-150 Gold and the same five-field evaluator.

The historical four cells (111/110/101/011) are reused byte-identically from
the same model-release batch.  The four new cells (000/001/010/100) are the only
arms sent in this batch: 4 x 150 = 600 calls.

Evaluation view (``g04_evaluation_views_contract_v2``, user decision
2026-10-27)
--------------------------------------------------------------------------
``--evaluation-view fine_gold_span`` (DEFAULT, formal main view) scores the
frozen predictions against the ORIGINAL annotated Gold spans -- no per-field
envelope merge -- with the unchanged non-one-to-one overlap rule.  This is the
view Table I uses, so Table I and Table II stay directly comparable.

``--evaluation-view coarse_sentence_level`` reproduces the superseded
historical numbers into the historical output paths; it is diagnostic only.

Modes
-----
--offline-check : zero-network prompt/request/render/evaluator audit
--smoke         : 4 arms x 5 samples = 20 calls, same persistence tree
--execute       : 4 arms x 150 samples = 600 calls (resumes smoke rows first)
--report-only   : zero-API re-score of the persisted predictions

Real sends require ``--execute/--smoke --allow-llm``.  Use ``--project-env`` to
load the project ``.env`` through ``LLMConfig.from_env``; secrets are never
printed or written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for candidate in (SRC, SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import run_sep_c3_modular_ablation_v1 as core  # noqa: E402
from bpc_hybrid.prompt_loader import load_prompt  # noqa: E402
from bpc_hybrid.sep_c3_modular_evaluation import (  # noqa: E402
    evaluate_coarse as evaluate_coarse_legacy,
)
from bpc_hybrid.sep_c3_primary_evaluation import (  # noqa: E402
    CONTRACT_ID,
    CONTRACT_PATH,
    LEGACY_COARSE_VIEW_ID,
    PRIMARY_VIEW_ID,
    evaluate_primary_view,
)

NEW_ARMS = ("000", "001", "010", "100")
HISTORICAL_ARMS = ("111", "110", "101", "011")
ALL_ARMS = ("000", "001", "010", "011", "100", "101", "110", "111")
SAMPLES_PER_ARM = 150
PLANNED_CALLS = 600
CALL_CAP = 600
SMOKE_SAMPLES_PER_ARM = 5
SMOKE_PLANNED_CALLS = 20
SMOKE_CALL_CAP = 20

PROMPT_DIR = ROOT / "prompts" / "sun_compat" / "ablation_v2_factorial"
PROMPT_MANIFEST = PROMPT_DIR / "manifest.json"
ESTG_INPUT = ROOT / "data" / "input" / "estg150_formal_inference_input_v2.json"
FORMAL_GOLD = ROOT / "data" / "gold" / "stage2" / "estg150_formal_gold_v1.json"
BUDGET_PATH = ROOT / "configs" / "v6_factorial_ablation_budget_v1.json"
SMOKE_BUDGET_PATH = (
    ROOT / "configs" / "v6_factorial_ablation_budget_smoke_v1.json"
)
OUT_DIR = ROOT / "outputs" / "development" / "v6_factorial_ablation_v1"
OFFLINE_REPORT = (
    ROOT / "outputs" / "reports" / "v6_factorial_ablation_v1_offline_check.json"
)

#: Output capsules per evaluation view.  The formal (fine) view writes a NEW
#: v2/v3 capsule; the coarse view keeps writing the historical paths so the
#: pre-2026-10-27 artifacts stay reproducible and are never overwritten.
OUT_PATHS: dict[str, dict[str, Path]] = {
    PRIMARY_VIEW_ID: {
        "report_json": (ROOT / "outputs" / "reports"
                        / "v6_factorial_ablation_v2_fine_gold_span.json"),
        "report_md": (ROOT / "outputs" / "reports"
                      / "v6_factorial_ablation_v2_fine_gold_span.md"),
        "table2_json": (ROOT / "outputs" / "reports"
                        / "stage2_table2_prompt_ablation_paper_final_v3.json"),
        "table2_md": (ROOT / "outputs" / "reports"
                      / "stage2_table2_prompt_ablation_paper_final_v3.md"),
    },
    LEGACY_COARSE_VIEW_ID: {
        "report_json": ROOT / "outputs" / "reports" / "v6_factorial_ablation_v1.json",
        "report_md": ROOT / "outputs" / "reports" / "v6_factorial_ablation_v1.md",
        "table2_json": (ROOT / "outputs" / "reports"
                        / "stage2_table2_prompt_ablation_paper_final_v2.json"),
        "table2_md": (ROOT / "outputs" / "reports"
                      / "stage2_table2_prompt_ablation_paper_final_v2.md"),
    },
}


def out_paths(view: str) -> dict[str, Path]:
    if view not in OUT_PATHS:
        raise V6FactorialError(f"unknown evaluation view: {view}")
    return OUT_PATHS[view]


def evaluate_arm(gold_doc: dict[str, Any],
                 attempts: Sequence[Mapping[str, Any]], *,
                 method_id: str, view: str) -> dict[str, Any]:
    """Score one arm under the requested view (formal view by default)."""
    if view == PRIMARY_VIEW_ID:
        return evaluate_primary_view(gold_doc, attempts, method_id=method_id)
    if view == LEGACY_COARSE_VIEW_ID:
        return evaluate_coarse_legacy(gold_doc, attempts, method_id=method_id)
    raise V6FactorialError(f"unknown evaluation view: {view}")


def overall_micro(evaluation: Mapping[str, Any]) -> Mapping[str, Any]:
    """Overall micro P/R/F1 of either evaluation shape."""
    if "five_field_micro" in evaluation:
        return evaluation["five_field_micro"]
    return evaluation["coarse_five_field_micro"]


def mean_field_f1(evaluation: Mapping[str, Any]) -> float:
    if "five_field_mean_f1" in evaluation:
        return float(evaluation["five_field_mean_f1"])
    return float(evaluation["coarse_five_field_mean_f1"])


class V6FactorialError(RuntimeError):
    """The v6 factorial runner precondition failed."""


@dataclass(frozen=True)
class V6Prompt:
    combination: str
    flags: Mapping[str, bool]
    system_prompt: str
    user_prompt_template: str
    composition_sha256: str
    path: Path
    raw_text: str

    def render_user(self, sample_id: str, source_text: str) -> str:
        return self.user_prompt_template.format(
            sample_id=sample_id,
            source_id=sample_id,
            source_text=source_text,
            few_shot_block=_few_shot_block(self.raw_text),
        )


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _prompt_name(arm: str) -> str:
    if arm not in ALL_ARMS:
        raise V6FactorialError(f"unknown v6 factorial arm: {arm}")
    return f"ablation_v2_factorial/direct_llm_v6_{arm}"


def _few_shot_block(raw_text: str) -> str:
    start = raw_text.find("## Examples")
    end = raw_text.find("## Notes", start)
    if start < 0 or end < 0:
        return ""
    return raw_text[start:end].strip()


def _prompt(arm: str) -> V6Prompt:
    loaded = load_prompt(_prompt_name(arm))
    flags = {
        "E": arm[0] == "1",
        "S": arm[1] == "1",
        "J": arm[2] == "1",
    }
    composition_sha256 = _sha256_text(
        loaded.system_prompt + "\n<!--USER-->\n" + loaded.user_prompt_template
    )
    return V6Prompt(
        combination=arm,
        flags=flags,
        system_prompt=loaded.system_prompt,
        user_prompt_template=loaded.user_prompt_template,
        composition_sha256=composition_sha256,
        path=loaded.path,
        raw_text=loaded.raw_text,
    )


def _load_generated_prompt(arm: str):
    return load_prompt(_prompt_name(arm))


def _render_prompt(arm: str, sample_id: str, source_text: str
                   ) -> tuple[str, str]:
    loaded = _load_generated_prompt(arm)
    user = loaded.user_prompt_template.format(
        sample_id=sample_id,
        source_id=sample_id,
        source_text=source_text,
        few_shot_block=_few_shot_block(loaded.raw_text),
    )
    system = loaded.system_prompt
    if not system or not user:
        raise V6FactorialError(f"empty rendered prompt for arm {arm}")
    return system, user


# Bind the audited generic call stack to the v6 prompt family.
core.ALL_ARMS = ALL_ARMS
core._prompt = _prompt
core._load_generated_prompt = _load_generated_prompt
core.render_prompt = _render_prompt
# The generic core expects an input file whose row count equals the requested
# sample count.  This adapter always reads the frozen 150-row input and slices
# the requested smoke/full prefix, so a 5-sample smoke can share the same
# persistence tree with the full 150-sample run.
core.samples = lambda n=SAMPLES_PER_ARM: _samples(n)


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise V6FactorialError(f"expected JSON object: {path}")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _samples(first_n: int | None = None) -> list[dict[str, str]]:
    """Return the frozen EStG input rows in order (optionally first N)."""
    doc = _read_json(ESTG_INPUT)
    rows = doc.get("records")
    if not isinstance(rows, list) or len(rows) != SAMPLES_PER_ARM:
        raise V6FactorialError("EStG input must contain exactly 150 records")
    out = [
        {"sample_id": str(row["sample_id"]),
         "text": str(row["approved_text_en"])}
        for row in rows
    ]
    if len({r["sample_id"] for r in out}) != SAMPLES_PER_ARM:
        raise V6FactorialError("EStG sample ids must be unique")
    return out if first_n is None else out[: int(first_n)]


def _request_body(arm: str, sample_id: str, source_text: str) -> dict[str, Any]:
    system, user = _render_prompt(arm, sample_id, source_text)
    return {
        "model": core.MODEL_ALIAS,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": core.TEMPERATURE,
        "top_p": core.TOP_P,
        "max_tokens": core.MAX_TOKENS,
        "stream": False,
        "thinking": {"type": "disabled"},
    }


def _estimated_input_tokens(arms: Sequence[str], rows: Sequence[Mapping[str, str]]
                           ) -> dict[str, int]:
    out: dict[str, int] = {}
    for arm in arms:
        total = 0
        for row in rows:
            body = _request_body(arm, row["sample_id"], row["text"])
            raw = json.dumps(
                body, ensure_ascii=False, sort_keys=True).encode("utf-8")
            total += math.ceil(len(raw) / 3)
        out[arm] = total
    return out


def _prompt_checks(arm: str) -> list[str]:
    prompt = _prompt(arm)
    text = prompt.raw_text
    problems: list[str] = []
    e, s, j = (arm[0] == "1", arm[1] == "1", arm[2] == "1")
    if e:
        if "## Examples" not in text:
            problems.append("E=1 without examples")
        if "Structural output template" in text:
            problems.append("E=1 with structural template")
    else:
        if "Structural output template" not in text:
            problems.append("E=0 without structural template")
        if "## Examples" in text:
            problems.append("E=0 with examples")
    for marker in ("Six-element semantics:", "Field-typing precision (D1-R1):"):
        if s and marker not in text:
            problems.append(f"S=1 without {marker}")
        if not s and marker in text:
            problems.append(f"S=0 with {marker}")
    for marker in ("You MUST follow stage2_extraction", "Output discipline:"):
        if j and marker not in text:
            problems.append(f"J=1 without {marker}")
        if not j and marker in text:
            problems.append(f"J=0 with {marker}")
    if not prompt.system_prompt.strip() or not prompt.user_prompt_template.strip():
        problems.append("empty system or user prompt after loader parse")
    rendered = prompt.render_user("offline_sample", "A must act.")
    if "A must act." not in rendered:
        problems.append("user template render failed")
    if "source_text:" not in prompt.user_prompt_template:
        problems.append("user template missing source_text envelope")
    return problems


def offline_check() -> dict[str, Any]:
    manifest = _read_json(PROMPT_MANIFEST)
    input_rows = _samples()
    arm_rows: dict[str, Any] = {}
    total_input = 0
    for arm in ALL_ARMS:
        prompt = _prompt(arm)
        problems = _prompt_checks(arm)
        arm_input = _estimated_input_tokens((arm,), input_rows)[arm]
        total_input += arm_input
        arm_rows[arm] = {
            "factors": {"E": int(prompt.flags["E"]),
                        "S": int(prompt.flags["S"]),
                        "J": int(prompt.flags["J"])},
            "prompt_path": str(prompt.path.relative_to(ROOT)).replace(
                "\\", "/"),
            "prompt_sha256": _sha256_text(prompt.path.read_text(
                encoding="utf-8")),
            "system_sha256": _sha256_text(prompt.system_prompt),
            "user_sha256": _sha256_text(prompt.user_prompt_template),
            "composition_sha256": prompt.composition_sha256,
            "estimated_input_tokens_150": arm_input,
            "problems": problems,
        }
    expected_manifest = {
        arm: row["prompt_sha256"] for arm, row in arm_rows.items()
    }
    manifest_ok = all(
        manifest["arms"][arm]["prompt_sha256"] == expected_manifest[arm]
        for arm in ALL_ARMS
    )
    report = {
        "schema_version": "v6_factorial_ablation_offline_check@1.0.0",
        "status": "pass" if all(
            not row["problems"] for row in arm_rows.values()) and manifest_ok
        else "fail",
        "network_calls": 0,
        "prompt_manifest": str(PROMPT_MANIFEST.relative_to(ROOT)).replace(
            "\\", "/"),
        "prompt_manifest_sha256": hashlib.sha256(
            PROMPT_MANIFEST.read_bytes()).hexdigest(),
        "manifest_hashes_match": manifest_ok,
        "input_sha256": hashlib.sha256(ESTG_INPUT.read_bytes()).hexdigest(),
        "gold_sha256": hashlib.sha256(FORMAL_GOLD.read_bytes()).hexdigest(),
        "estimated_total_input_tokens_8_arms": total_input,
        "arms": arm_rows,
        "model": {
            "id": core.MODEL_ALIAS,
            "documented_release": core.MODEL_RELEASE,
            "temperature": core.TEMPERATURE,
            "top_p": core.TOP_P,
            "max_tokens": core.MAX_TOKENS,
            "retry": 0,
            "stream": False,
            "thinking": {"type": "disabled"},
        },
        "execution_plan": {
            "historical_reused": list(HISTORICAL_ARMS),
            "new_calls": list(NEW_ARMS),
            "samples_per_new_arm": SAMPLES_PER_ARM,
            "planned_new_calls": PLANNED_CALLS,
            "smoke_samples_per_arm": SMOKE_SAMPLES_PER_ARM,
            "smoke_calls": SMOKE_PLANNED_CALLS,
        },
    }
    _write_json(OFFLINE_REPORT, report)
    return report


def _historical_path(arm: str) -> Path:
    mapping = {
        "111": (
            ROOT / "outputs" / "development" / "barrientos_ablation_suite_v2"
            / "D-full-0813" / "repeat-01" / "canonical_predictions.jsonl"),
        "110": (
            ROOT / "outputs" / "development"
            / "d1_prompt_factorial_ablation_v2"
            / "D-no-explicit-json-contract-0813" / "repeat-01"
            / "canonical_predictions.jsonl"),
        "101": (
            ROOT / "outputs" / "development"
            / "d1_prompt_factorial_ablation_v2"
            / "D-no-semantic-guidance-0813" / "repeat-01"
            / "canonical_predictions.jsonl"),
        "011": (
            ROOT / "outputs" / "development"
            / "d1_prompt_factorial_ablation_v2"
            / "D-no-semantic-examples-0813" / "repeat-01"
            / "canonical_predictions.jsonl"),
    }
    return mapping[arm]


def _new_path(arm: str) -> Path:
    return OUT_DIR / arm / "repeat-01" / "canonical_predictions.jsonl"


def _attempt_rows_for(path: Path) -> list[dict[str, Any]]:
    rows = core._read_jsonl(path)
    if len(rows) != SAMPLES_PER_ARM:
        raise V6FactorialError(
            f"expected {SAMPLES_PER_ARM} canonical rows in {path}, "
            f"found {len(rows)}")
    return core.attempt_rows(rows)


def _evaluate_all(view: str = PRIMARY_VIEW_ID) -> dict[str, Any]:
    gold_doc = _read_json(FORMAL_GOLD)
    arms: dict[str, Any] = {}
    for arm in ALL_ARMS:
        path = _historical_path(arm) if arm in HISTORICAL_ARMS else _new_path(arm)
        if not path.is_file():
            arms[arm] = {
                "status": "missing_predictions",
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            }
            continue
        attempts = _attempt_rows_for(path)
        evaluation = evaluate_arm(
            gold_doc, attempts,
            method_id=f"direct_llm_v6_chunk_{arm}", view=view)
        arms[arm] = {
            "status": "evaluated",
            "source": ("historical_same_release" if arm in HISTORICAL_ARMS
                       else "v6_factorial_new_calls"),
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "evaluation": evaluation,
        }
    return arms


def _main_effects(arms: Mapping[str, Mapping[str, Any]]) -> dict[str, float]:
    means: dict[str, float] = {}
    for arm, row in arms.items():
        if row.get("status") != "evaluated":
            continue
        means[arm] = float(overall_micro(row["evaluation"])["f1"])
    out: dict[str, float] = {}
    for factor, index in (("E", 0), ("S", 1), ("J", 2)):
        on = [v for k, v in means.items() if k[index] == "1"]
        off = [v for k, v in means.items() if k[index] == "0"]
        if on and off:
            out[f"{factor}_main_effect"] = (
                sum(on) / len(on) - sum(off) / len(off))
    for name, idxs in (
            ("ES", (0, 1)), ("EJ", (0, 2)), ("SJ", (1, 2))):
        cells = {}
        for k, v in means.items():
            key = "".join(k[i] for i in idxs)
            cells.setdefault(key, []).append(v)
        if len(cells) == 4:
            out[f"two_way_{name}"] = (
                sum(cells["11"]) / len(cells["11"])
                - sum(cells["10"]) / len(cells["10"])
                - sum(cells["01"]) / len(cells["01"])
                + sum(cells["00"]) / len(cells["00"]))
    if len(means) == 8:
        out["three_way_ESJ"] = (
            means["111"] - means["110"] - means["101"] + means["100"]
            - means["011"] + means["010"] + means["001"] - means["000"])
    return out


def _build_report(execution: Mapping[str, Any] | None = None,
                  view: str = PRIMARY_VIEW_ID) -> dict[str, Any]:
    is_primary = view == PRIMARY_VIEW_ID
    paths = out_paths(view)
    arms = _evaluate_all(view)
    manifest = _read_json(PROMPT_MANIFEST)
    means = {
        arm: float(overall_micro(row["evaluation"])["f1"])
        for arm, row in arms.items() if row.get("status") == "evaluated"
    }
    baseline = means.get("111")
    table: dict[str, Any] = {}
    for arm in ALL_ARMS:
        row = arms[arm]
        factors = {"E": arm[0] == "1", "S": arm[1] == "1",
                   "J": arm[2] == "1"}
        if row.get("status") != "evaluated":
            table[arm] = {"factors": factors, **row}
            continue
        ev = row["evaluation"]
        micro = overall_micro(ev)
        mean_f1 = mean_field_f1(ev)
        entry: dict[str, Any] = {
            "factors": factors,
            "source": row["source"],
            "path": row["path"],
            "sha256": row["sha256"],
            "view": ev.get("view"),
            "prompt_sha256": manifest["arms"][arm]["prompt_sha256"],
            "overall_micro_f1": micro["f1"],
            "overall_micro_precision": micro["precision"],
            "overall_micro_recall": micro["recall"],
            "overall_ground_truth_spans": micro.get("ground_truth"),
            "overall_extracted_spans": micro.get("extracted"),
            "mean_field_f1": mean_f1,
            "modality_label_macro_f1":
                (ev.get("modality_labels") or {}).get("macro_f1"),
            "delta_vs_111": (
                None if baseline is None else round(micro["f1"] - baseline, 8)),
            "failed_count": ev.get("failed_count"),
            "per_field_f1": {
                k: v.get("f1")
                for k, v in (ev.get("five_fields")
                             or ev.get("per_field") or {}).items()
            },
        }
        if not is_primary:
            # historical key names, kept so pre-2026-10-27 consumers and the
            # historical coarse capsule stay readable
            entry.update({
                "coarse_five_field_micro_f1": micro["f1"],
                "coarse_five_field_micro_precision": micro["precision"],
                "coarse_five_field_micro_recall": micro["recall"],
                "coarse_five_field_mean_f1": mean_f1,
            })
        table[arm] = entry
    report = {
        "schema_version": ("v6_factorial_ablation_report@2.0.0" if is_primary
                           else "v6_factorial_ablation_report@1.0.0"),
        "suite_id": "V6-ESJ-FACTORIAL-001",
        "status": "complete" if len(means) == 8 else "incomplete",
        "prompt_family": "v6_chunk_direct_assembly",
        "view": view,
        "view_role": ("formal main report (original Gold spans)" if is_primary
                      else "historical/diagnostic only (superseded)"),
        "evaluation_contract": {
            "contract_id": CONTRACT_ID if is_primary else (
                "g04_evaluation_views_contract_v1"),
            "contract_path": CONTRACT_PATH,
            "reference_side": ("original annotated Gold spans, one reference "
                               "span per annotated span (no envelope merge)"
                               if is_primary else
                               "one [min(start), max(end)) envelope per field "
                               "per sentence"),
            "prediction_side": "original validated prediction spans (unmerged)",
            "match_rule": (
                "independent_same_field_any_nonempty_character_span_intersection"),
            "coordinate_convention": (
                "zero-based character offsets into approved_text_en, "
                "half-open [start,end)"),
            "assignment": "none_independent_overlap_coverage (not one-to-one)",
            "metric_family_matches_table1": True,
        },
        "prompt_manifest": str(PROMPT_MANIFEST.relative_to(ROOT)).replace(
            "\\", "/"),
        "prompt_manifest_sha256": hashlib.sha256(
            PROMPT_MANIFEST.read_bytes()).hexdigest(),
        "gold_path": str(FORMAL_GOLD.relative_to(ROOT)).replace("\\", "/"),
        "gold_sha256": hashlib.sha256(FORMAL_GOLD.read_bytes()).hexdigest(),
        "evaluator": ("bpc_hybrid.sep_c3_primary_evaluation."
                      "evaluate_primary_view (five_field_micro + modality "
                      "labels)" if is_primary
                      else "coarse_five_field + modality labels"),
        "primary_metric": ("five_field_micro_f1" if is_primary
                           else "coarse_five_field_micro_f1"),
        "primary_metric_definition": (
            "pooled five-span-field micro-F1; identical family to the "
            "paper's Table 1 Overall (Micro-F1) metric"),
        "secondary_metric": ("five_field_mean_f1" if is_primary
                             else "coarse_five_field_mean_f1"),
        "historical_reuse": {
            arm: {
                "prompt_sha256": manifest["arms"][arm]["prompt_sha256"],
                "historical_reference": manifest["arms"][arm].get(
                    "historical_reference"),
            }
            for arm in HISTORICAL_ARMS
        },
        "new_execution": {
            arm: {
                "prompt_sha256": manifest["arms"][arm]["prompt_sha256"],
                "path": str(_new_path(arm).relative_to(ROOT)).replace(
                    "\\", "/"),
            }
            for arm in NEW_ARMS
        },
        "main_effects": _main_effects(arms),
        "arms": table,
        "execution": execution,
        "notes": [
            "The historical four cells are evaluated from their existing "
            "same-release predictions; no new calls were made for them.",
            "The four new cells are the 600 authorized calls.",
            "The evaluator and Gold are identical for every cell.",
            "E/S/J are coded in that order.",
            (f"Evaluation view: {view} (formal main view, original Gold "
             "spans)." if is_primary else
             f"Evaluation view: {view} (historical; NOT the paper main "
             "report)."),
        ],
    }
    _write_json(paths["report_json"], report)
    _write_json(paths["table2_json"], report)
    view_line = (
        "- evaluation view: **fine_gold_span** (original Gold spans, formal "
        "main view; no envelope merge)" if is_primary else
        "- evaluation view: **coarse_sentence_level** (historical/diagnostic; "
        "superseded as the paper main report)")
    lines = [
        "# Table 2 - v6 prompt-family 2^3 E/S/J factorial ablation",
        "",
        f"- status: **{report['status']}**",
        view_line,
        f"- primary metric: `{report['primary_metric']}`",
        f"- Gold: `{report['gold_path']}`",
        f"- prompt family: `{report['prompt_family']}`",
        "",
        "| E S J | Modality macro-F1 | Actor | Action | Condition | "
        "Constraint | Exception | Overall pooled (micro) F1 | Mean-of-5 F1 | "
        "Delta overall vs 111 | Failed |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ALL_ARMS:
        row = table[arm]
        if row.get("overall_micro_f1") is None:
            lines.append(
                f"| {arm[0]} {arm[1]} {arm[2]} | | | | | | | | | | |")
            continue
        fields = row.get("per_field_f1") or {}
        def fmt(name):
            value = fields.get(name)
            return "" if value is None else f"{float(value):.4f}"
        lines.append(
            f"| {arm[0]} {arm[1]} {arm[2]} | "
            f"{row['modality_label_macro_f1']:.4f} | "
            f"{fmt('actor')} | {fmt('action')} | {fmt('condition')} | "
            f"{fmt('constraint')} | {fmt('exception')} | "
            f"{row['overall_micro_f1']:.4f} | "
            f"{row['mean_field_f1']:.4f} | "
            f"{row['delta_vs_111']:+.4f} | {row['failed_count']} |")
    lines += [
        "",
        "## Overall metric detail",
        "",
        "| E S J | Precision | Recall | F1 | Gold spans | Extracted | Source |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for arm in ALL_ARMS:
        row = table[arm]
        if row.get("overall_micro_f1") is None:
            continue
        lines.append(
            f"| {arm[0]} {arm[1]} {arm[2]} | "
            f"{row['overall_micro_precision']:.4f} | "
            f"{row['overall_micro_recall']:.4f} | "
            f"{row['overall_micro_f1']:.4f} | "
            f"{row['overall_ground_truth_spans']} | "
            f"{row['overall_extracted_spans']} | {row['source']} |")
    lines += [
        "",
        "## Main effects (overall pooled micro-F1 scale)",
        "",
        "```json",
        json.dumps(report["main_effects"], ensure_ascii=False, indent=2,
                   sort_keys=True),
        "```",
        "",
        "## Provenance",
        "",
        f"- prompt manifest: `{report['prompt_manifest']}`",
        f"- Gold sha256: `{report['gold_sha256']}`",
        "- historical 111/110/101/011: reused predictions from the same "
        "DeepSeek-V4-Pro-0813 release window.",
        "- new 000/001/010/100: 600 calls in this batch.",
        "- no Gold or benchmark mutation; evaluator fixed.",
        "- no new LLM call was made for this re-score.",
    ]
    paths["report_md"].write_text("\n".join(lines) + "\n", encoding="utf-8",
                                  newline="\n")
    paths["table2_md"].write_text("\n".join(lines) + "\n", encoding="utf-8",
                                  newline="\n")
    return report


def _result_writer(execution: Mapping[str, Any]) -> None:
    _build_report(execution, PRIMARY_VIEW_ID)


def run_offline() -> int:
    report = offline_check()
    print(json.dumps({
        "status": report["status"],
        "network_calls": report["network_calls"],
        "arms": {k: v["problems"] for k, v in report["arms"].items()},
        "estimated_total_input_tokens_8_arms":
            report["estimated_total_input_tokens_8_arms"],
    }, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


def _smoke_evaluate_coarse(gold_doc, attempts, method_id=None):
    """Minimal evaluator shim for the 5-sample smoke only.

    The frozen coarse evaluator requires the attempt membership to equal the
    full 150-record Gold set.  Smoke predictions are only 5 records, so the
    full evaluator cannot be called there.  Smoke verifies transport, JSON
    parsing, and canonicalization; the full 150-record run uses the real
    evaluator and overwrites these smoke metrics.
    """
    n = len(attempts)
    return {
        "primary_metric": "coarse_five_field_mean_f1",
        "coarse_five_field_mean_f1": 0.0,
        "coarse_five_field_micro": {"precision": 0.0, "recall": 0.0,
                                    "f1": 0.0},
        "modality_labels": {"macro_f1": 0.0},
        "failed_count": sum(
            1 for row in attempts if row.get("request_status") != "ok"),
        "smoke_only": True,
        "smoke_attempts": n,
        "note": "evaluator shim used only for the 5-sample smoke",
    }


def run_smoke(project_env: bool) -> int:
    real_evaluate = core.evaluate_coarse
    core.evaluate_coarse = _smoke_evaluate_coarse
    try:
        result = core.execute(
            project_env=project_env,
            arms=NEW_ARMS,
            out_dir=OUT_DIR,
            budget_path=SMOKE_BUDGET_PATH,
            planned_calls=SMOKE_PLANNED_CALLS,
            call_cap=SMOKE_CALL_CAP,
            samples_per_arm=SMOKE_SAMPLES_PER_ARM,
            result_writer=None,
        )
    finally:
        core.evaluate_coarse = real_evaluate
    print(json.dumps({
        "complete": result.get("complete"),
        "actual_calls": result.get("actual_calls"),
        "aborted": result.get("aborted"),
        "abort_reason": result.get("abort_reason"),
        "budget_gate": result.get("budget_gate"),
        "runs": result.get("runs"),
    }, ensure_ascii=False, indent=2))
    return 0 if result.get("complete") else 3


def run_full(project_env: bool, view: str = PRIMARY_VIEW_ID) -> int:
    paths = out_paths(view)
    # Any future execution must evaluate with the SAME view as the paper
    # tables, so bind the selected evaluator into the shared call stack.
    real_evaluator = core.evaluate_coarse
    core.evaluate_coarse = (
        lambda gold_doc, attempts, *, method_id:
        evaluate_arm(gold_doc, attempts, method_id=method_id, view=view))
    try:
        result = core.execute(
            project_env=project_env,
            arms=NEW_ARMS,
            out_dir=OUT_DIR,
            budget_path=BUDGET_PATH,
            planned_calls=PLANNED_CALLS,
            call_cap=CALL_CAP,
            samples_per_arm=SAMPLES_PER_ARM,
            result_writer=lambda execution: _build_report(execution, view),
        )
    finally:
        core.evaluate_coarse = real_evaluator
    print(json.dumps({
        "complete": result.get("complete"),
        "actual_calls": result.get("actual_calls"),
        "completed_samples": result.get("completed_samples"),
        "aborted": result.get("aborted"),
        "abort_reason": result.get("abort_reason"),
        "budget_gate": result.get("budget_gate"),
        "runtime_seconds": result.get("runtime_seconds"),
        "evaluation_view": view,
        "report": str(paths["report_json"].relative_to(ROOT)).replace(
            "\\", "/"),
    }, ensure_ascii=False, indent=2))
    return 0 if result.get("complete") else 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--offline-check", action="store_true")
    mode.add_argument("--report-only", action="store_true")
    mode.add_argument("--smoke", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--allow-llm", action="store_true")
    parser.add_argument("--project-env", action="store_true")
    parser.add_argument(
        "--evaluation-view", default=PRIMARY_VIEW_ID,
        choices=(PRIMARY_VIEW_ID, LEGACY_COARSE_VIEW_ID),
        help=("evaluation view; default = formal main view (original Gold "
              "spans). coarse_sentence_level reproduces the historical "
              "capsules."))
    args = parser.parse_args()
    view = args.evaluation_view
    paths = out_paths(view)
    if args.offline_check:
        return run_offline()
    if args.report_only:
        execution_path = OUT_DIR / "execution_summary.json"
        execution = _read_json(execution_path) if execution_path.is_file() else None
        report = _build_report(execution, view)
        print(json.dumps({
            "status": report["status"],
            "evaluation_view": report["view"],
            "primary_metric": report["primary_metric"],
            "main_effects": report["main_effects"],
            "report_json": str(paths["report_json"].relative_to(ROOT)).replace(
                "\\", "/"),
            "report_md": str(paths["report_md"].relative_to(ROOT)).replace(
                "\\", "/"),
            "table2_json": str(paths["table2_json"].relative_to(ROOT)).replace(
                "\\", "/"),
        }, ensure_ascii=False, indent=2))
        return 0 if report["status"] == "complete" else 1
    if not args.allow_llm:
        print("real sends require --allow-llm", file=sys.stderr)
        return 2
    if args.smoke:
        return run_smoke(args.project_env)
    return run_full(args.project_env, view)


if __name__ == "__main__":
    raise SystemExit(main())
