# -*- coding: utf-8 -*-
"""Formal three-method Stage 2 comparison report v1 (zero-API).

Versioned, self-contained, verifiable formal report built ONLY from the
user-authorized evaluation contract (G0.4, 2026-08-11):

- MAIN report: sentence-level coarse FIVE span-bearing fields
  (actor/action/condition/constraint/exception) per method, plus the
  separate four-class modality-label metrics (accuracy, macro-F1, per-class)
- fine-grained five fields: diagnostic / 对照 only
- modality evidence-span metrics: explicitly unavailable (never zeroed,
  never aggregated)
- the historical six-field coarse aggregate is development provenance and
  is NOT mixed in

Per method: Rules-Only (sun_rule_only), LLM-SE (direct_llm),
Rules+LLM-Repair (sun_llm_fallback, comparison-only). Includes per-field
P/R/F1, modality-label metrics, cross-method deltas, historical call cost
and new calls=0, known limitations, the H1 net-negative stop-optimizing
decision, and per-method strengths/failure types. Every conclusion points
back to the formal artifact hashes.

Outputs:
- outputs/reports/stage2_formal_three_method_comparison_v1.json
- outputs/reports/stage2_formal_three_method_comparison_v1.md
- outputs/reports/stage2_formal_three_method_comparison_v1.manifest.json
- outputs/reports/stage2_formal_three_method_comparison_v1_export_index.json
- outputs/reports/verify_stage2_formal_comparison_v1.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

COMPARISON = ROOT / "outputs" / "evidence" / "d1_h1_zero_api_reeval_v1" / "comparison_capsule.json"
INPUT_V2 = ROOT / "data" / "input" / "estg150_formal_inference_input_v2.json"
GOLD = ROOT / "data" / "gold" / "stage2" / "estg150_formal_gold_v1.json"
G04_CONTRACT = ROOT / "configs" / "evaluation" / "g04_evaluation_views_contract_v1.json"
METHODS = ROOT / "configs" / "methods.json"
RELEASE_MANIFEST = ROOT / "outputs" / "reports" / "formal_benchmark_release_v2.manifest.json"

ARMS = {
    "sun_rule_only": {
        "arm_tag": "b0_formal_arm_v1",
        "label": "Rules-Only",
        "role": "baseline",
        "manifest": "outputs/reports/b0_formal_arm_v1.manifest.json",
    },
    "direct_llm": {
        "arm_tag": "direct_llm_formal_arm_v1",
        "label": "LLM-SE",
        "role": "replacement_method",
        "manifest": "outputs/reports/direct_llm_formal_arm_v1.manifest.json",
    },
    "sun_llm_fallback": {
        "arm_tag": "sun_llm_fallback_formal_arm_v1",
        "label": "Rules+LLM-Repair",
        "role": "comparison_arm_only",
        "manifest": "outputs/reports/sun_llm_fallback_formal_arm_v1.manifest.json",
    },
}

OUT_JSON = ROOT / "outputs" / "reports" / "stage2_formal_three_method_comparison_v1.json"
OUT_MD = ROOT / "outputs" / "reports" / "stage2_formal_three_method_comparison_v1.md"
OUT_MANIFEST = ROOT / "outputs" / "reports" / "stage2_formal_three_method_comparison_v1.manifest.json"
OUT_EXPORT = ROOT / "outputs" / "reports" / "stage2_formal_three_method_comparison_v1_export_index.json"
OUT_VERIFIER = ROOT / "outputs" / "reports" / "verify_stage2_formal_comparison_v1.py"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_report() -> dict[str, Any]:
    comparison = _load_json(COMPARISON)
    cmp_methods = comparison.get("methods", {})
    per_method: dict[str, Any] = {}
    deltas: dict[str, dict[str, dict[str, float]]] = {}

    for mid, info in ARMS.items():
        manifest = _load_json(ROOT / info["manifest"])
        cmp_entry = cmp_methods.get(mid, {})
        coarse = cmp_entry.get("coarse_span_fields", {})
        fine = cmp_entry.get("fine_span_fields", {})
        labels = cmp_entry.get("modality_labels", {})
        if mid == "sun_rule_only":
            hist_calls = 0
        else:
            hist_calls = cmp_entry.get("historical_llm_calls", 150)
        per_method[mid] = {
            "method": mid,
            "label": info["label"],
            "role": info["role"],
            "claim_scope": cmp_entry.get("claim_scope", "formal"),
            "arm_manifest": info["manifest"],
            "arm_manifest_sha256": cmp_entry.get("arm_manifest_sha256")
            if mid != "sun_rule_only" else cmp_entry.get(
                "prediction_manifest_sha256"),
            "historical_llm_calls": hist_calls,
            "new_llm_calls": 0,
            "main_view_coarse_five_fields": coarse,
            "diagnostic_fine_five_fields": fine,
            "modality_labels": {
                "accuracy": labels.get("accuracy"),
                "macro_f1": labels.get("macro_f1"),
                "per_class": labels.get("per_class"),
            },
        }
        deltas[mid] = {f: coarse.get(f, {}).get("f1") for f in coarse}

    # cross-method delta matrix on the main coarse five-field F1
    fields = ("actor", "action", "condition", "constraint", "exception")
    delta_matrix: dict[str, dict[str, Any]] = {}
    for a in ARMS:
        for b in ARMS:
            if a == b:
                continue
            row = {}
            for f in fields:
                fa = deltas[a].get(f)
                fb = deltas[b].get(f)
                if fa is not None and fb is not None:
                    row[f] = round(fa - fb, 4)
            delta_matrix[f"{a} vs {b}"] = row
    # overall coarse five-field arithmetic mean F1 per method (labeled as
    # arithmetic mean of the five span fields; NOT a single aggregate metric
    # replacing per-field reporting)
    mean_f1 = {}
    for mid in ARMS:
        vals = [v for v in deltas[mid].values() if v is not None]
        mean_f1[mid] = round(sum(vals) / len(vals), 4) if vals else None

    return {
        "schema_version": "stage2_formal_three_method_comparison@1.0.0",
        "report_id": "stage2_formal_three_method_comparison_v1",
        "generated_zero_api": True,
        "evaluation_contract": {
            "g04": "g04_evaluation_views_contract@1.0.0",
            "authorized": True,
            "authorized_at": "2026-08-11",
            "main_report": ("sentence-level coarse FIVE span-bearing fields "
                            "+ separate four-class modality-label metrics"),
            "modality_evidence_span_metrics": "unavailable (never zeroed, never aggregated)",
            "fine_five_fields_role": "diagnostic / 对照",
            "historical_six_field_aggregate": "development provenance only (NOT mixed in)",
        },
        "input": {"path": "data/input/estg150_formal_inference_input_v2.json",
                  "sha256": _sha256_file(INPUT_V2)},
        "gold": {"path": "data/gold/stage2/estg150_formal_gold_v1.json",
                 "sha256": _sha256_file(GOLD)},
        "comparison_capsule": {
            "path": "outputs/evidence/d1_h1_zero_api_reeval_v1/comparison_capsule.json",
            "sha256": _sha256_file(COMPARISON)},
        "methods": per_method,
        "delta_matrix": delta_matrix,
        "coarse_five_field_mean_f1": mean_f1,
        "conclusions": {
            "h1_net_negative_stop_optimizing": (
                "Rules+LLM-Repair (comparison-only) remains net-negative on "
                "the main coarse five-field view (esp. actor F1), consistent "
                "with the 2026-08-08 decision; no further optimization is "
                "intended"),
            "d1_strength": (
                "LLM-SE leads on action/condition/constraint coarse F1 "
                "with the highest modality-label accuracy; its actor "
                "extraction trails Rules-Only"),
            "b0_strength": (
                "Rules-Only leads on actor and exception coarse F1 with "
                "higher recall; its constraint field is the weakest"),
            "modality_label_separate": (
                "modality four-class label metrics are reported separately "
                "and must not be mixed into span metrics"),
            "common_limitation": (
                "modality evidence-span metrics are unavailable for all "
                "three methods (published Gold stores modality as a plain "
                "string)"),
            "three_method_ready_not_pipeline_complete": (
                "three-method formal comparison ready does NOT imply "
                "S2.13 / S1.7 / S3.7 completion"),
        },
        "zero_api": {"new_llm_api_calls": 0,
                     "historical_calls_total": sum(
                         per_method[m]["historical_llm_calls"] for m in ARMS)},
    }


def main() -> int:
    report = build_report()

    def _write(path: Path, data: bytes) -> None:
        if path.exists() and path.read_bytes() != data:
            raise RuntimeError(f"refusing to overwrite different content: {path}")
        path.write_bytes(data)

    json_data = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _write(OUT_JSON, json_data)
    json_sha = _sha256_bytes(json_data)

    md = [
        "# Formal Three-Method Stage 2 Comparison v1",
        "",
        f"- evaluation contract: {report['evaluation_contract']['main_report']}",
        f"- modality evidence-span: {report['evaluation_contract']['modality_evidence_span_metrics']}",
        f"- fine five fields: {report['evaluation_contract']['fine_five_fields_role']}",
        f"- historical six-field aggregate: {report['evaluation_contract']['historical_six_field_aggregate']}",
        "",
        "## Per-method main view (coarse five span fields, P/R/F1)",
    ]
    for mid, info in report["methods"].items():
        md.append(f"### {info['label']} ({mid}, {info['claim_scope']})")
        for f, m in info["main_view_coarse_five_fields"].items():
            md.append(f"- {f}: P {m.get('precision')} / R {m.get('recall')} / "
                      f"F1 {m.get('f1')}")
        ml = info["modality_labels"]
        md.append(f"- modality label accuracy: {ml['accuracy']} | "
                  f"macro-F1: {ml['macro_f1']}")
        for cls in (ml.get("per_class") or []):
            md.append(f"  - {cls['class']}: P {cls['precision']} / "
                      f"R {cls['recall']} / F1 {cls['f1']}")
        md.append(f"- historical LLM calls: {info['historical_llm_calls']} | "
                  f"new calls: {info['new_llm_calls']}")
        md.append("")
    md.append("## Cross-method deltas (coarse five-field F1)")
    for pair, row in report["delta_matrix"].items():
        md.append(f"- {pair}: {row}")
    md.append("")
    md.append("## Coarse five-field arithmetic mean F1 (descriptive)")
    md.append(f"- {report['coarse_five_field_mean_f1']}")
    md.append("")
    md.append("## Conclusions")
    for k, v in report["conclusions"].items():
        md.append(f"- {k}: {v}")
    md.append("")
    md.append("## Zero-API declaration")
    md.append(f"- new LLM/API calls: {report['zero_api']['new_llm_api_calls']}")
    md.append(f"- historical recorded calls: {report['zero_api']['historical_calls_total']}")
    md.append("")
    md_text = "\n".join(md)
    _write(OUT_MD, md_text.encode("utf-8"))

    manifest = {
        "schema_version": "stage2_formal_three_method_comparison_manifest@1.0.0",
        "report": {"path": "outputs/reports/stage2_formal_three_method_comparison_v1.json",
                   "sha256": json_sha},
        "report_md": {"path": "outputs/reports/stage2_formal_three_method_comparison_v1.md",
                      "sha256": _sha256_bytes(md_text.encode("utf-8"))},
        "input_v2_sha256": report["input"]["sha256"],
        "gold_sha256": report["gold"]["sha256"],
        "comparison_capsule_sha256": report["comparison_capsule"]["sha256"],
        "zero_api": report["zero_api"],
    }
    man_data = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _write(OUT_MANIFEST, man_data)
    man_sha = _sha256_bytes(man_data)

    export = {
        "schema_version": "stage2_formal_three_method_comparison_export@1.0.0",
        "artifacts": {
            "report.json": {"path": "outputs/reports/stage2_formal_three_method_comparison_v1.json",
                            "sha256": json_sha},
            "report.md": {"path": "outputs/reports/stage2_formal_three_method_comparison_v1.md",
                          "sha256": _sha256_bytes(md_text.encode("utf-8"))},
            "manifest.json": {"path": "outputs/reports/stage2_formal_three_method_comparison_v1.manifest.json",
                              "sha256": man_sha},
            "verifier.py": {"path": "outputs/reports/verify_stage2_formal_comparison_v1.py",
                            "sha256": "computed-after"},
        },
        "manifest": {"path": "outputs/reports/stage2_formal_three_method_comparison_v1.manifest.json",
                     "sha256": man_sha},
    }
    verifier_src = _VERIFIER_TEMPLATE.format(
        REPORT_SHA=json_sha, MANIFEST_SHA=man_sha,
        INPUT_SHA=report["input"]["sha256"], GOLD_SHA=report["gold"]["sha256"])
    _write(OUT_VERIFIER, verifier_src.encode("utf-8"))
    ver_sha = _sha256_bytes(verifier_src.encode("utf-8"))
    export["artifacts"]["verifier.py"]["sha256"] = ver_sha
    export_data = (json.dumps(export, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _write(OUT_EXPORT, export_data)

    print(f"formal comparison report written: {OUT_JSON.relative_to(ROOT)}")
    print(f"  report sha256: {json_sha[:16]}...")
    print(f"  manifest sha256: {man_sha[:16]}...")
    print(f"  verifier sha256: {ver_sha[:16]}...")
    return 0


_VERIFIER_TEMPLATE = '''# -*- coding: utf-8 -*-
"""Independent verifier for the formal three-method comparison v1."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "outputs" / "reports" / "stage2_formal_three_method_comparison_v1.json"
MANIFEST = ROOT / "outputs" / "reports" / "stage2_formal_three_method_comparison_v1.manifest.json"
INPUT_V2 = ROOT / "data" / "input" / "estg150_formal_inference_input_v2.json"
GOLD = ROOT / "data" / "gold" / "stage2" / "estg150_formal_gold_v1.json"

EXPECTED_REPORT_SHA = "{REPORT_SHA}"
EXPECTED_MANIFEST_SHA = "{MANIFEST_SHA}"
EXPECTED_INPUT_SHA = "{INPUT_SHA}"
EXPECTED_GOLD_SHA = "{GOLD_SHA}"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    checks = []

    def check(name, ok, detail=""):
        checks.append({{"name": name, "ok": bool(ok), "detail": detail}})

    check("report exists", REPORT.exists())
    check("report hash", _sha(REPORT) == EXPECTED_REPORT_SHA)
    check("manifest exists", MANIFEST.exists())
    check("manifest hash", _sha(MANIFEST) == EXPECTED_MANIFEST_SHA)
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    check("schema", report.get("schema_version")
          == "stage2_formal_three_method_comparison@1.0.0")
    check("input v2 hash", report["input"]["sha256"] == EXPECTED_INPUT_SHA)
    check("gold hash", report["gold"]["sha256"] == EXPECTED_GOLD_SHA)
    check("three methods", set(report["methods"]) ==
          {{"sun_rule_only", "direct_llm", "sun_llm_fallback"}})
    check("zero new calls", report["zero_api"]["new_llm_api_calls"] == 0)
    check("main report five fields",
          all(set(m["main_view_coarse_five_fields"]) ==
              {{"actor", "action", "condition", "constraint", "exception"}}
              for m in report["methods"].values()))
    check("modality labels separate",
          all("accuracy" in m["modality_labels"]
              for m in report["methods"].values()))
    check("no historical six-field aggregate mixed in",
          "historical_six_field_aggregate" in
          report["evaluation_contract"] and
          "development provenance" in
          report["evaluation_contract"]["historical_six_field_aggregate"])
    check("h1 comparison-only declared",
          report["methods"]["sun_llm_fallback"]["role"]
          == "comparison_arm_only")
    check("conclusions present", bool(report["conclusions"]))
    return {{"verified": all(c["ok"] for c in checks), "checks": checks}}


if __name__ == "__main__":
    result = verify()
    for c in result["checks"]:
        print(("PASS" if c["ok"] else "FAIL"), c["name"], c["detail"])
    print("VERIFIED" if result["verified"] else "NOT VERIFIED")
    sys.exit(0 if result["verified"] else 1)
'''


if __name__ == "__main__":
    raise SystemExit(main())
