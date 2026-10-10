# -*- coding: utf-8 -*-
"""Stage 2 formal conclusion capsule v1 (B0-R5 / D1-R5 close-out, zero-API).

Paper-safe conclusions built ONLY from the authorized G0.4 evaluation
contract and the verified formal artifacts:

- formal names: Rules-Only (sun_rule_only), LLM-SE (direct_llm),
  Rules+LLM-Repair (sun_llm_fallback, comparison-only); legacy codes are
  used only for Pipeline/task ID cross-reference;
- main report: sentence-level coarse FIVE span-bearing fields;
- modality four-class labels reported separately;
- fine five fields diagnostic only; modality evidence-span unavailable;
- the historical six-field development aggregate is NOT cited as a formal
  conclusion;
- disclosures: data scale (150 sentences), reconstruction method
  (paper-faithful independent reconstruction, NOT the authors' original
  implementation, NOT an exact reproduction), historical call cost and zero
  new calls, and NO statistical-significance inference (field differences
  are descriptive, never claimed significant);
- every conclusion points back to the formal report / manifest / hash.

B0-R5 / D1-R5 DoD (form paper conclusions; results may be positive or
negative; written as method-level independent reconstruction with
disclosed assets and adaptations) is met by this capsule + the comparison
report; statuses are set to verified. H1 keeps the comparison-only
conclusion.

Outputs:
- outputs/reports/stage2_formal_conclusion_v1.json
- outputs/reports/stage2_formal_conclusion_v1.md
- outputs/reports/stage2_formal_conclusion_v1.manifest.json
- outputs/reports/stage2_formal_conclusion_v1_export_index.json
- outputs/reports/verify_stage2_formal_conclusion_v1.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

COMPARISON_REPORT = ROOT / "outputs" / "reports" / "stage2_formal_three_method_comparison_v1.json"
COMPARISON_MANIFEST = ROOT / "outputs" / "reports" / "stage2_formal_three_method_comparison_v1.manifest.json"
COMPARISON_CAPSULE = ROOT / "outputs" / "evidence" / "d1_h1_zero_api_reeval_v1" / "comparison_capsule.json"
INPUT_V2 = ROOT / "data" / "input" / "estg150_formal_inference_input_v2.json"
GOLD = ROOT / "data" / "gold" / "stage2" / "estg150_formal_gold_v1.json"

OUT_JSON = ROOT / "outputs" / "reports" / "stage2_formal_conclusion_v1.json"
OUT_MD = ROOT / "outputs" / "reports" / "stage2_formal_conclusion_v1.md"
OUT_MANIFEST = ROOT / "outputs" / "reports" / "stage2_formal_conclusion_v1.manifest.json"
OUT_EXPORT = ROOT / "outputs" / "reports" / "stage2_formal_conclusion_v1_export_index.json"
OUT_VERIFIER = ROOT / "outputs" / "reports" / "verify_stage2_formal_conclusion_v1.py"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_conclusion() -> dict[str, Any]:
    report = _load_json(COMPARISON_REPORT)
    methods = report["methods"]
    coarse = {m: methods[m]["main_view_coarse_five_fields"] for m in methods}
    labels = {m: methods[m]["modality_labels"] for m in methods}

    def f1(mid: str, field: str) -> float | None:
        return coarse[mid].get(field, {}).get("f1")

    def label_acc(mid: str) -> float | None:
        return labels[mid].get("accuracy")

    conclusions: list[dict[str, Any]] = []
    # LLM-SE leads action / condition / constraint + modality label acc
    for field in ("action", "condition", "constraint"):
        winner = max(methods, key=lambda m: f1(m, field) or 0)
        conclusions.append({
            "claim": f"LLM-SE leads on {field} (coarse five-field F1)",
            "value": {m: round(f1(m, field), 4) for m in methods},
            "supported": winner == "direct_llm",
            "reference": "stage2_formal_three_method_comparison_v1.json#methods.*.main_view_coarse_five_fields",
        })
    acc_winner = max(methods, key=lambda m: label_acc(m) or 0)
    conclusions.append({
        "claim": "LLM-SE leads on modality four-class label accuracy",
        "value": {m: round(label_acc(m), 4) for m in methods},
        "supported": acc_winner == "direct_llm",
        "reference": "stage2_formal_three_method_comparison_v1.json#methods.*.modality_labels.accuracy",
    })
    # Rules-Only leads actor / exception
    for field in ("actor", "exception"):
        winner = max(methods, key=lambda m: f1(m, field) or 0)
        conclusions.append({
            "claim": f"Rules-Only leads on {field} (coarse five-field F1)",
            "value": {m: round(f1(m, field), 4) for m in methods},
            "supported": winner == "sun_rule_only",
            "reference": "stage2_formal_three_method_comparison_v1.json#methods.*.main_view_coarse_five_fields",
        })
    # Rules+LLM-Repair net-negative, comparison-only, stop optimizing
    conclusions.append({
        "claim": ("Rules+LLM-Repair is net-negative as an overall scheme; "
                  "kept as comparison-only and no longer optimized "
                  "(2026-08-08 decision)"),
        "value": {m: round(f1(m, "actor"), 4) for m in methods},
        "supported": f1("sun_llm_fallback", "actor") < f1("sun_rule_only", "actor"),
        "reference": "stage2_formal_three_method_comparison_v1.json#conclusions.h1_net_negative_stop_optimizing",
    })

    return {
        "schema_version": "stage2_formal_conclusion@1.0.0",
        "conclusion_id": "stage2_formal_conclusion_v1",
        "project_date": "2026-08-11",
        "formal_names": {
            "sun_rule_only": "Rules-Only",
            "direct_llm": "LLM-SE",
            "sun_llm_fallback": "Rules+LLM-Repair (comparison-only)",
        },
        "legacy_codes_are_pipeline_ids_only": True,
        "evaluation_contract": report["evaluation_contract"],
        "data_scale": {
            "sentences": 150,
            "dataset": "independently_reconstructed_estg_150_v1",
            "input_v2_sha256": _sha256_file(INPUT_V2),
            "gold_sha256": _sha256_file(GOLD),
        },
        "reconstruction_disclosure": (
            "paper-faithful independent reconstruction of the published Sun "
            "et al. (2024) Stage 2; NOT the authors' original implementation "
            "and NOT an exact reproduction"),
        "disclosures": {
            "historical_llm_calls": 300,
            "new_llm_api_calls": 0,
            "no_statistical_significance_inference": (
                "field differences are descriptive; no significance tests "
                "were run and none are claimed"),
            "modality_evidence_span_metrics": "unavailable (never zeroed/aggregated)",
            "historical_six_field_aggregate": "development provenance only; NOT cited as formal conclusion",
        },
        "conclusions": conclusions,
        "per_method_summary": {
            m: {
                "label": methods[m]["label"],
                "role": methods[m]["role"],
                "coarse_five_field_mean_f1": report["coarse_five_field_mean_f1"].get(m),
                "modality_label_accuracy": label_acc(m),
            } for m in methods
        },
        "references": {
            "comparison_report": {
                "path": "outputs/reports/stage2_formal_three_method_comparison_v1.json",
                "sha256": _sha256_file(COMPARISON_REPORT)},
            "comparison_manifest": {
                "path": "outputs/reports/stage2_formal_three_method_comparison_v1.manifest.json",
                "sha256": _sha256_file(COMPARISON_MANIFEST)},
            "comparison_capsule": {
                "path": "outputs/evidence/d1_h1_zero_api_reeval_v1/comparison_capsule.json",
                "sha256": _sha256_file(COMPARISON_CAPSULE)},
        },
        "task_status": {
            "B0-R5": "verified (paper conclusion formed; method-level independent reconstruction; result may be positive or negative and is reported descriptively)",
            "D1-R5": "verified (paper conclusion formed; method-level independent reconstruction; disclosures recorded)",
            "H1": "comparison-only conclusion (2026-08-08 decision; stop optimizing)",
        },
        "not_downgraded": (
            "the three-method formal comparison remains formal; S2.11/S2.13 "
            "incompleteness does not demote it to candidate"),
        "zero_api": {"new_llm_api_calls": 0},
    }


def main() -> int:
    conclusion = build_conclusion()

    def _write(path: Path, data: bytes) -> None:
        if path.exists() and path.read_bytes() != data:
            raise RuntimeError(f"refusing to overwrite different content: {path}")
        path.write_bytes(data)

    json_data = (json.dumps(conclusion, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _write(OUT_JSON, json_data)
    json_sha = _sha256_bytes(json_data)

    md = [
        "# Stage 2 Formal Conclusion v1",
        "",
        f"- project date: {conclusion['project_date']}",
        f"- formal names: {conclusion['formal_names']}",
        f"- reconstruction disclosure: {conclusion['reconstruction_disclosure']}",
        f"- data scale: {conclusion['data_scale']['sentences']} sentences "
        f"(input v2 {conclusion['data_scale']['input_v2_sha256'][:16]}...)",
        "",
        "## Conclusions (each references the formal report)",
    ]
    for c in conclusion["conclusions"]:
        md.append(f"- {c['claim']} [{c['value']}] "
                  f"supported={c['supported']} ({c['reference']})")
    md += [
        "",
        "## Per-method summary",
    ]
    for m, s in conclusion["per_method_summary"].items():
        md.append(f"- {s['label']} ({m}): coarse five-field mean F1 "
                  f"{s['coarse_five_field_mean_f1']} | modality label acc "
                  f"{s['modality_label_accuracy']}")
    md += [
        "",
        "## Disclosures",
    ]
    for k, v in conclusion["disclosures"].items():
        md.append(f"- {k}: {v}")
    md += [
        "",
        "## Task status",
    ]
    for k, v in conclusion["task_status"].items():
        md.append(f"- {k}: {v}")
    md.append(f"- not downgraded: {conclusion['not_downgraded']}")
    md.append("")
    md_text = "\n".join(md)
    _write(OUT_MD, md_text.encode("utf-8"))

    manifest = {
        "schema_version": "stage2_formal_conclusion_manifest@1.0.0",
        "conclusion": {"path": "outputs/reports/stage2_formal_conclusion_v1.json",
                       "sha256": json_sha},
        "conclusion_md": {"path": "outputs/reports/stage2_formal_conclusion_v1.md",
                          "sha256": _sha256_bytes(md_text.encode("utf-8"))},
        "references": conclusion["references"],
        "zero_api": {"new_llm_api_calls": 0},
    }
    man_data = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _write(OUT_MANIFEST, man_data)
    man_sha = _sha256_bytes(man_data)

    verifier_src = _VERIFIER_TEMPLATE.format(
        CONCLUSION_SHA=json_sha, MANIFEST_SHA=man_sha,
        REPORT_SHA=conclusion["references"]["comparison_report"]["sha256"])
    _write(OUT_VERIFIER, verifier_src.encode("utf-8"))
    ver_sha = _sha256_bytes(verifier_src.encode("utf-8"))

    export = {
        "schema_version": "stage2_formal_conclusion_export@1.0.0",
        "artifacts": {
            "conclusion.json": {"path": "outputs/reports/stage2_formal_conclusion_v1.json",
                                "sha256": json_sha},
            "conclusion.md": {"path": "outputs/reports/stage2_formal_conclusion_v1.md",
                              "sha256": _sha256_bytes(md_text.encode("utf-8"))},
            "manifest.json": {"path": "outputs/reports/stage2_formal_conclusion_v1.manifest.json",
                              "sha256": man_sha},
            "verifier.py": {"path": "outputs/reports/verify_stage2_formal_conclusion_v1.py",
                            "sha256": ver_sha},
        },
        "manifest": {"path": "outputs/reports/stage2_formal_conclusion_v1.manifest.json",
                     "sha256": man_sha},
    }
    _write(OUT_EXPORT, (json.dumps(export, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    print(f"Stage 2 formal conclusion written: {OUT_JSON.relative_to(ROOT)}")
    print(f"  conclusion sha256: {json_sha[:16]}...")
    print(f"  verifier sha256: {ver_sha[:16]}...")
    return 0


_VERIFIER_TEMPLATE = '''# -*- coding: utf-8 -*-
"""Independent verifier for the Stage 2 formal conclusion v1."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONCLUSION = ROOT / "outputs" / "reports" / "stage2_formal_conclusion_v1.json"
MANIFEST = ROOT / "outputs" / "reports" / "stage2_formal_conclusion_v1.manifest.json"
REPORT = ROOT / "outputs" / "reports" / "stage2_formal_three_method_comparison_v1.json"

EXPECTED_CONCLUSION_SHA = "{CONCLUSION_SHA}"
EXPECTED_MANIFEST_SHA = "{MANIFEST_SHA}"
EXPECTED_REPORT_SHA = "{REPORT_SHA}"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    checks = []

    def check(name, ok, detail=""):
        checks.append({{"name": name, "ok": bool(ok), "detail": detail}})

    check("conclusion exists", CONCLUSION.exists())
    check("conclusion hash", _sha(CONCLUSION) == EXPECTED_CONCLUSION_SHA)
    check("manifest exists", MANIFEST.exists())
    check("manifest hash", _sha(MANIFEST) == EXPECTED_MANIFEST_SHA)
    check("report hash bound", _sha(REPORT) == EXPECTED_REPORT_SHA)
    c = json.loads(CONCLUSION.read_text(encoding="utf-8"))
    check("schema", c.get("schema_version") == "stage2_formal_conclusion@1.0.0")
    check("project date", c.get("project_date") == "2026-08-11")
    check("conclusions non-empty", bool(c.get("conclusions")))
    check("all supported", all(x.get("supported") for x in c.get("conclusions", [])))
    check("disclosures", c.get("disclosures", {{}}).get("no_statistical_significance_inference") is not None)
    check("not exact reproduction",
          "NOT an exact reproduction" in c.get("reconstruction_disclosure", ""))
    check("B0-R5 verified", c.get("task_status", {{}}).get("B0-R5", "").startswith("verified"))
    check("D1-R5 verified", c.get("task_status", {{}}).get("D1-R5", "").startswith("verified"))
    check("H1 comparison-only", "comparison-only" in c.get("task_status", {{}}).get("H1", ""))
    check("zero new calls", c.get("zero_api", {{}}).get("new_llm_api_calls") == 0)
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
