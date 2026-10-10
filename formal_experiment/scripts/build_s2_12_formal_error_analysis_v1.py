# -*- coding: utf-8 -*-
"""S2.12 formal descriptive error analysis v1 (zero-API, retrospective).

Based ONLY on the three formal arm evaluation results (same error taxonomy,
same denominator, same input set): per-field ground_truth / extracted /
matched / misclassified / missed counts from the main coarse five-field view
plus the separate modality-label metrics. Shows cross-method error
complementarity and common failures descriptively.

IMPORTANT: the stratification/analysis was formed AFTER seeing the results,
so this is explicitly marked retrospective/exploratory -- NOT preregistered.
The S2.12 full DoD remains blocked on S2.11 (complex legal corpus + G0.5);
this document is the EStG-150-internal descriptive part only.

Outputs:
- outputs/reports/s2_12_formal_descriptive_error_analysis_v1.json
- outputs/reports/s2_12_formal_descriptive_error_analysis_v1.md
- outputs/reports/s2_12_formal_descriptive_error_analysis_v1.manifest.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

ARMS = {
    "sun_rule_only": ("b0_formal_arm_v1", "Rules-Only"),
    "direct_llm": ("direct_llm_formal_arm_v1", "LLM-SE"),
    "sun_llm_fallback": ("sun_llm_fallback_formal_arm_v1", "Rules+LLM-Repair"),
}
FIELDS = ("actor", "action", "condition", "constraint", "exception")

OUT_JSON = ROOT / "outputs" / "reports" / "s2_12_formal_descriptive_error_analysis_v1.json"
OUT_MD = ROOT / "outputs" / "reports" / "s2_12_formal_descriptive_error_analysis_v1.md"
OUT_MANIFEST = ROOT / "outputs" / "reports" / "s2_12_formal_descriptive_error_analysis_v1.manifest.json"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_analysis() -> dict[str, Any]:
    per_method: dict[str, Any] = {}
    for mid, (tag, label) in ARMS.items():
        coarse = _load_json(ROOT / "data" / "results" / tag / "evaluation_coarse.json")
        labels = _load_json(ROOT / "data" / "results" / tag / "modality_labels.json")
        fields = {}
        for f in FIELDS:
            v = coarse.get("span_fields", {}).get(f, {})
            gt = v.get("ground_truth")
            ext = v.get("extracted")
            prec = v.get("precision")
            rec = v.get("recall")
            # the per-field report carries P/R/F1 + counts; matched/missed/
            # misclassified are DERIVED approximations for descriptive use
            matched = round(rec * gt) if (rec is not None and gt is not None) else None
            missed = round((1 - rec) * gt) if (rec is not None and gt is not None) else None
            misclass = round((1 - prec) * ext) if (prec is not None and ext is not None) else None
            fields[f] = {
                "ground_truth": gt,
                "extracted": ext,
                "precision": prec,
                "recall": rec,
                "f1": v.get("f1"),
                "matched_approx": matched,
                "missed_approx": missed,
                "misclassified_approx": misclass,
            }
        per_method[mid] = {
            "label": label, "arm": tag, "fields": fields,
            "modality_labels": {
                "accuracy": labels.get("accuracy"),
                "macro_f1": labels.get("macro_f1"),
            },
        }

    # complementarity: for each field, who misses the most / least
    # (approximate counts derived from recall; descriptive only)
    complementarity: dict[str, Any] = {}
    for f in FIELDS:
        missed = {mid: per_method[mid]["fields"][f].get("missed_approx")
                  for mid in ARMS}
        misclass = {mid: per_method[mid]["fields"][f].get(
            "misclassified_approx") for mid in ARMS}

        def _min_key(d):
            return min((k for k, v in d.items() if v is not None), key=d.get)

        def _max_key(d):
            return max((k for k, v in d.items() if v is not None), key=d.get)

        complementarity[f] = {
            "missed_approx": missed,
            "misclassified_approx": misclass,
            "lowest_missed": _min_key(missed),
            "highest_missed": _max_key(missed),
        }
    # weakest field per method by recall
    weakest = {mid: min(FIELDS, key=lambda f: (
        per_method[mid]["fields"][f].get("recall") or 0))
        for mid in ARMS}
    return {
        "schema_version": "s2_12_formal_descriptive_error_analysis@1.0.0",
        "retrospective": True,
        "preregistered": False,
        "note": ("stratification/analysis formed AFTER seeing the results; "
                 "explicitly retrospective/exploratory, NOT preregistered; "
                 "S2.12 full DoD remains blocked on S2.11 (complex legal "
                 "corpus + G0.5)"),
        "methodology": {
            "error_taxonomy": "per-field ground_truth/extracted/matched/misclassified/missed (Sun literal-overlap contract)",
            "denominator": "same formal input v2 (150 records) and same published Gold views for all methods",
            "input_set": "estg150_formal_inference_input_v2.json (150)",
            "view": "coarse five span fields (main) + separate modality labels",
            "modality_evidence_span": "unavailable (never zeroed/aggregated)",
        },
        "per_method": per_method,
        "complementarity": complementarity,
        "weakest_field_per_method": weakest,
        "observations": [
            "constraint is the weakest field for Rules-Only (lowest recall) and among the weakest for the other methods",
            "LLM-SE has the highest recall on action/condition/constraint; Rules-Only has the highest recall on actor (approx missed counts derived from recall)",
            "Rules+LLM-Repair consistently underperforms its own Rules-Only base on actor (net-negative), matching the 2026-08-08 stop-optimizing decision",
            "all three methods share the modality evidence-span limitation (structural, from the published Gold)",
            "misclassified vs missed trade-off differs per method per field (see complementarity)",
        ],
        "dependency": {
            "full_doD_blocked_on": "S2.11 (complex legal corpus freeze + G0.5 complexity rules frozen before results) + Barrientos adapter",
            "this_document": "EStG-150-internal formal descriptive part only",
        },
        "zero_api": {"new_llm_api_calls": 0},
    }


def main() -> int:
    analysis = build_analysis()

    def _write(path: Path, data: bytes) -> None:
        if path.exists() and path.read_bytes() != data:
            raise RuntimeError(f"refusing to overwrite different content: {path}")
        path.write_bytes(data)

    json_data = (json.dumps(analysis, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _write(OUT_JSON, json_data)
    json_sha = _sha256_bytes(json_data)

    md = [
        "# S2.12 Formal Descriptive Error Analysis v1 (retrospective/exploratory)",
        "",
        f"- retrospective: {analysis['retrospective']} | preregistered: {analysis['preregistered']}",
        f"- note: {analysis['note']}",
        "",
        "## Methodology",
    ]
    for k, v in analysis["methodology"].items():
        md.append(f"- {k}: {v}")
    md.append("")
    for mid, info in analysis["per_method"].items():
        md.append(f"### {info['label']} ({mid})")
        for f, m in info["fields"].items():
            md.append(f"- {f}: gt={m['ground_truth']} ext={m['extracted']} "
                      f"matched_ap={m['matched_approx']} "
                      f"misclass_ap={m['misclassified_approx']} "
                      f"missed_ap={m['missed_approx']}")
        md.append(f"- modality label acc: {info['modality_labels']['accuracy']}")
        md.append("")
    md.append("## Complementarity")
    for f, info in analysis["complementarity"].items():
        md.append(f"- {f}: missed_ap {info['missed_approx']} | "
                  f"lowest {info['lowest_missed']} | "
                  f"highest {info['highest_missed']}")
    md.append("")
    md.append("## Weakest field per method")
    md.append(f"- {analysis['weakest_field_per_method']}")
    md.append("")
    md.append("## Observations")
    for o in analysis["observations"]:
        md.append(f"- {o}")
    md.append("")
    md.append("## Dependency")
    md.append(f"- {analysis['dependency']['full_doD_blocked_on']}")
    md.append("")
    md_text = "\n".join(md)
    _write(OUT_MD, md_text.encode("utf-8"))

    manifest = {
        "schema_version": "s2_12_formal_descriptive_error_analysis_manifest@1.0.0",
        "analysis": {"path": "outputs/reports/s2_12_formal_descriptive_error_analysis_v1.json",
                     "sha256": json_sha},
        "analysis_md": {"path": "outputs/reports/s2_12_formal_descriptive_error_analysis_v1.md",
                        "sha256": _sha256_bytes(md_text.encode("utf-8"))},
        "zero_api": {"new_llm_api_calls": 0},
    }
    man_data = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _write(OUT_MANIFEST, man_data)
    print(f"S2.12 descriptive error analysis written: {OUT_JSON.relative_to(ROOT)}")
    print(f"  analysis sha256: {json_sha[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
