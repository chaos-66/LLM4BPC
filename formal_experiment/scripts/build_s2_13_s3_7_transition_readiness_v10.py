# -*- coding: utf-8 -*-
"""S2.13 -> S3.7 transition readiness v10 (successor of v9).

v9 recorded the Gold-Rule-Record and Oracle-isolation state while S2.12 still
contained the cancelled Rules+LLM-Repair arm and two API arms.  The current
scope has only Rules-Only and LLM-SE, and the existing successor
``s2_12_two_method_contract_v1`` is the authority for whether the two-method
S2.12 evidence chain is complete.  v10 binds that contract and derives S2.12 /
S2.13 state from it; it never requires, reads, or waits for the cancelled
repair arm.  v9 and all older capsules remain byte-exact.

The builder reuses v9's verified helpers for Gold Rule Records / Oracle /
batch readiness rather than re-implementing those governance checks.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/reports"
REPORT = OUT / "s2_13_s3_7_transition_readiness_v10.json"
MARKDOWN = OUT / "s2_13_s3_7_transition_readiness_v10.md"
MANIFEST = OUT / "s2_13_s3_7_transition_readiness_v10.manifest.json"
EXPORT = OUT / "s2_13_s3_7_transition_readiness_v10_export_index.json"
SCHEMA = ROOT / "configs/schemas/s2_13_s3_7_transition_readiness_v10.schema.json"
V9_BUILDER_PATH = ROOT / "scripts/build_s2_13_s3_7_transition_readiness_v9.py"

TWO_METHOD_CONTRACT = ROOT / "outputs/reports/s2_12_two_method_contract_v1.json"
TWO_METHOD_MANIFEST = ROOT / "outputs/reports/s2_12_two_method_contract_v1.manifest.json"
TWO_METHOD_BUILDER = ROOT / "scripts/build_s2_12_two_method_contract_v1.py"
S2_12_ACTIVE_SCOPE = ROOT / "configs/s2_12_active_method_scope_v1.json"
S2_12_ACTIVE_PREFLIGHT = ROOT / "configs/s2_12_active_preflight_v2.json"
S2_12_ACTIVE_REPORT = ROOT / "outputs/reports/s2_12_active_preflight_v2.json"
S2_12_INPUT = ROOT / "data/input/s2_12_complex_corpus_formal_input_v1.json"
RULES_ONLY_EVAL = ROOT / "data/results/s2_12_sun_rule_only_v1/evaluation.json"
RULES_ONLY_PRED = ROOT / "data/predictions/s2_12_sun_rule_only_v1/predictions.json"
RULES_ONLY_RUN_MANIFEST = ROOT / "data/predictions/s2_12_sun_rule_only_v1/manifest.json"
DIRECT_EVAL = ROOT / "data/results/s2_12_direct_llm_v1/evaluation.json"
DIRECT_PRED = ROOT / "data/predictions/s2_12_direct_llm_v1/predictions.json"
DIRECT_RUN_MANIFEST = ROOT / "data/predictions/s2_12_direct_llm_v1/manifest.json"

V9_ASSETS = (
    "configs/schemas/s2_13_s3_7_transition_readiness_v9.schema.json",
    "scripts/build_s2_13_s3_7_transition_readiness_v9.py",
    "scripts/verify_s2_13_s3_7_transition_readiness_v9.py",
    "tests/test_s2_13_s3_7_transition_readiness_v9.py",
    "outputs/reports/s2_13_s3_7_transition_readiness_v9.json",
    "outputs/reports/s2_13_s3_7_transition_readiness_v9.md",
    "outputs/reports/s2_13_s3_7_transition_readiness_v9.manifest.json",
    "outputs/reports/s2_13_s3_7_transition_readiness_v9_export_index.json",
)

_V9_CACHE: Any = None


class TransitionFail(ValueError):
    """Fail-closed transition builder error."""


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _binding(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    if not path.is_file():
        raise TransitionFail(f"missing binding: {rel}")
    return {"path": rel, "sha256": _sha(path), "byte_size": path.stat().st_size}


def _load_v9():
    global _V9_CACHE
    if _V9_CACHE is None:
        spec = importlib.util.spec_from_file_location(
            "s2_13_transition_readiness_v9_for_v10", V9_BUILDER_PATH)
        if spec is None or spec.loader is None:
            raise TransitionFail("cannot load v9 builder helper")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        _V9_CACHE = module
    return _V9_CACHE


def historical_asset_ledger() -> dict[str, Any]:
    """v1-v8 from the v9 helper plus v9 assets bound byte-exact.

    Historical verifiers are not re-executed: they fail closed on legitimate
    later state changes.  v10 records their bytes and lifecycle state instead.
    """
    v9 = _load_v9()
    ledger = v9.historical_asset_ledger()
    v9_assets: dict[str, Any] = {}
    for rel in V9_ASSETS:
        path = ROOT / rel
        v9_assets[rel] = (
            {"sha256": _sha(path), "byte_size": path.stat().st_size}
            if path.is_file() else None
        )
    assets = dict(ledger.get("assets") or {})
    assets["v9"] = v9_assets
    ledger["assets"] = assets
    ledger["historical_verifiers_executed"] = False
    ledger["policy"] = (
        "superseded capsules stay byte-exact; their verifiers are not "
        "re-executed because they fail closed on legitimate later state changes"
    )
    return ledger


def _verified_gold_rule_records() -> dict[str, Any]:
    return _load_v9()._verified_gold_rule_records()


def _oracle_isolation_run() -> dict[str, Any]:
    return _load_v9()._oracle_isolation_run()


def _llm_batches() -> dict[str, Any]:
    return _load_v9()._llm_batches()


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise TransitionFail(f"missing {label}: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TransitionFail(f"{label} root is not an object")
    return value


def _two_method_state() -> dict[str, Any]:
    contract = _load_json(TWO_METHOD_CONTRACT, "two-method contract")
    manifest = _load_json(TWO_METHOD_MANIFEST, "two-method manifest")
    if manifest.get("report", {}).get("path") != \
            TWO_METHOD_CONTRACT.relative_to(ROOT).as_posix():
        raise TransitionFail("two-method manifest report path drift")
    if manifest["report"].get("sha256") != _sha(TWO_METHOD_CONTRACT):
        raise TransitionFail("two-method manifest report hash drift")
    if manifest["report"].get("byte_size") != TWO_METHOD_CONTRACT.stat().st_size:
        raise TransitionFail("two-method manifest report size drift")
    if contract.get("active_methods") != ["sun_rule_only", "direct_llm"]:
        raise TransitionFail("two-method active scope drift")
    cancelled = contract.get("cancelled_methods") or {}
    if "sun_llm_fallback" not in cancelled:
        raise TransitionFail("cancelled repair arm missing from two-method contract")
    comparison = contract.get("comparison") or {}
    if comparison.get("fallback_results_or_ledger_required") is not False:
        raise TransitionFail("two-method comparison still depends on repair results")
    if comparison.get("three_method_requirement_removed") is not True:
        raise TransitionFail("three-method requirement was not removed")
    evidence = comparison.get("evidence") or {}
    rules_evidence = evidence.get("sun_rule_only") or {}
    direct_evidence = evidence.get("direct_llm") or {}
    comparison_complete = comparison.get("complete") is True
    evidence_complete = all(
        e.get(key) is True for e in (rules_evidence, direct_evidence)
        for key in ("verified", "input_binding_ok", "all_36_rows", "metrics_valid")
    )
    if comparison_complete != evidence_complete:
        raise TransitionFail(
            "two-method complete flag disagrees with verified evidence fields")
    if contract.get("freeze", {}).get("s2_12_complete") is not comparison_complete:
        raise TransitionFail("two-method S2.12 freeze flag drift")
    return {
        "contract": contract,
        "manifest": manifest,
        "comparison_complete": comparison_complete,
        "rules_evidence": rules_evidence,
        "direct_evidence": direct_evidence,
        "remaining_calls": contract["call_plan"]["remaining_calls"],
    }


def build_report(history: Mapping[str, Any]) -> dict[str, Any]:
    state = _two_method_state()
    contract = state["contract"]
    complete = state["comparison_complete"]
    rules_evidence = state["rules_evidence"]
    direct_evidence = state["direct_evidence"]
    gold = _verified_gold_rule_records()
    oracle = _oracle_isolation_run()
    batches = _llm_batches()
    v9 = _load_v9()
    readiness = _load_json(v9.READINESS, "S2.12 readiness v4")
    if readiness.get("status") != \
            "partial_zero_api_arm_complete_api_arms_pending_authorization":
        raise TransitionFail("S2.12 readiness v4 status drift")
    s2_13_status = (
        "ready_for_separate_freeze_checkpoint"
        if complete else "blocked_only_on_two_method_contract"
    )
    pipeline_state = {
        "S1.7": "frozen",
        "S2.11": "verified_frozen",
        "S2.12": ("complete_two_method_evidence"
                  if complete else
                  "partial_two_method_contract_pending_direct_llm"),
        "S2.13": s2_13_status,
        "S3.4_S3.6": "development_only",
        "S3.7": "gold_rule_records_published_oracle_isolation_run_"
                "formal_main_table_not_authorized",
    }
    blockers = [] if complete else list(contract["comparison"].get("blockers") or [])
    if complete:
        blockers = ["separate S2.13 freeze checkpoint not yet executed"]
    report = {
        "schema_version": "s2_13_s3_7_transition_readiness@10.0.0",
        "report_id": "s2_13_s3_7_transition_readiness_v10",
        "supersedes": [
            {**_binding(rel),
             "reason": ("v10 supersedes v9 by replacing its three-method/API-arm "
                        "S2.12 state with the current verified two-method contract; "
                        "v9 assets stay byte-exact")}
            for rel in V9_ASSETS
        ],
        "pipeline_state": pipeline_state,
        "s2_11": {
            "status": "verified_frozen",
            "adjudicated": 36,
            "unresolved": 0,
            "reviewer": "hyc",
            "formal_gold": readiness["s2_11"]["formal_gold"],
            "formal_gold_payload_sha256": readiness["s2_11"]["formal_gold_payload_sha256"],
            "confirmation_event": readiness["s2_11"]["confirmation_event"],
            "provenance": ("deepseek_offline_proposal_v3 + user batch confirmation by "
                           "hyc; not independent-from-scratch expert annotation"),
        },
        "s2_12": {
            "status": "complete_two_method_evidence" if complete else "partial",
            "active_methods": ["sun_rule_only", "direct_llm"],
            "cancelled_methods": ["sun_llm_fallback"],
            "two_method_contract": _binding(
                TWO_METHOD_CONTRACT.relative_to(ROOT).as_posix()),
            "two_method_contract_manifest": _binding(
                TWO_METHOD_MANIFEST.relative_to(ROOT).as_posix()),
            "comparison_complete": complete,
            "completion_evidence": {
                "sun_rule_only": {
                    "verified": rules_evidence.get("verified") is True,
                    "input_binding_ok": rules_evidence.get("input_binding_ok") is True,
                    "all_36_rows": rules_evidence.get("all_36_rows") is True,
                    "metrics_valid": rules_evidence.get("metrics_valid") is True,
                },
                "direct_llm": {
                    "verified": direct_evidence.get("verified") is True,
                    "input_binding_ok": direct_evidence.get("input_binding_ok") is True,
                    "all_36_rows": direct_evidence.get("all_36_rows") is True,
                    "metrics_valid": direct_evidence.get("metrics_valid") is True,
                },
            },
            "cancelled_repair_arm": {
                "status": "cancelled_not_an_experimental_condition",
                "calls_removed": contract["cancelled_methods"]["sun_llm_fallback"]["cancelled_calls"],
                "required_for_completion": False,
            },
            "remaining_calls": state["remaining_calls"],
            "post_result_tuning_performed": False,
            "readiness_v4": _binding(v9.READINESS.relative_to(ROOT).as_posix()),
            "gold_blind_input": _binding("data/input/s2_12_complex_corpus_formal_input_v1.json"),
            "sun_rule_only": {
                "status": ("verified_complete"
                           if rules_evidence.get("verified") is True else "not_verified"),
                "evaluation": _binding(
                    RULES_ONLY_EVAL.relative_to(ROOT).as_posix()),
                "actual_cost_usd": 0.0,
            },
            "direct_llm": {
                "status": ("verified_complete"
                           if direct_evidence.get("verified") is True else "pending_evidence"),
                "evaluation": (_binding(DIRECT_EVAL.relative_to(ROOT).as_posix())
                               if DIRECT_EVAL.is_file() else None),
                "remaining_calls": state["remaining_calls"]["s2_12_direct"],
            },
            "offline_batch_readiness": {
                "historical_report": batches.get("report"),
                "historical_real_calls_remaining": batches.get("real_calls_remaining"),
                "historical_scope_superseded": True,
                "current_remaining_calls": state["remaining_calls"],
                "current_remaining_total": state["remaining_calls"]["total"],
                "note": ("the historical offline-readiness report described the "
                         "superseded 137-call three-arm scope; the current "
                         "two-method contract owns the remaining-call count"),
            },
            "three_method_comparison_complete": False,
            "historical_three_method_capsules_retained": True,
        },
        "s2_13": {
            "status": s2_13_status,
            "blockers": blockers,
            "note": (
                "Two-method S2.12 evidence is complete; S2.13 is eligible for a "
                "separate freeze checkpoint, which this builder does not execute."
                if complete else
                "S2.13 is blocked only on the current two-method S2.12 evidence "
                "chain. The cancelled Rules+LLM-Repair arm is not a dependency."
            ),
        },
        "stage3": {
            "S3.4": "development_only",
            "S3.5": "development_only",
            "S3.6": "development_only",
            "S3.7": {
                "status": ("gold_rule_records_published_and_oracle_isolation_run; "
                           "formal main table NOT started or authorized"),
                "authorized": False,
                "gold_rule_records_present": True,
                "oracle_isolation_started": oracle.get("started", False),
                "blockers": (["S2.13 freeze checkpoint"]
                             + ["formal promotion of S3.4-S3.6"]
                             + ["user authorization for the formal Oracle main table"]
                             if not complete else
                             ["formal promotion of S3.4-S3.6",
                              "user authorization for the formal Oracle main table"]),
            },
        },
        "gold_rule_records": gold,
        "oracle_isolation_run": oracle,
        "historical_transition_verifiers": history,
        "authorization": readiness["authorization"],
        "safety": {
            "new_llm_api_calls": 0,
            "new_network_calls": 0,
            "gold_rule_records_created": False,
            "oracle_started": False,
            "cancelled_repair_arm_used": False,
            "historical_transition_assets_modified": False,
            "project_audit_md_modified": False,
        },
    }
    return report


def _render_md(report: Mapping[str, Any]) -> bytes:
    gold = report["gold_rule_records"]
    counts = gold["counts"]
    oracle = report["oracle_isolation_run"]
    three = oracle.get("original_three_types", {}) if oracle.get("started") else {}
    s2 = report["s2_12"]
    lines = [
        "# S2.13 -> S3.7 Transition Readiness v10",
        "",
        "- S2.11: **verified / frozen**, 36/36 adjudicated; formal Gold published.",
        f"- S2.12: **{s2['status']}**; active methods Rules-Only / LLM-SE; "
        "`sun_llm_fallback` is cancelled and not an experimental condition.",
        f"- S2.13: **{report['s2_13']['status']}**; not auto-marked complete.",
        "- S3.4-S3.6: **development-only**.",
        f"- S3.7: **Gold Rule Records published** ({counts['rules']} rules / "
        f"{counts['sentences']} sentences / {counts['items']} items; independent "
        f"verifier verified); **Oracle isolation run** on the frozen development "
        "evaluation surface; **formal main table not started or authorized**.",
        "",
        "## Two-method evidence",
        "",
        f"- comparison complete: **{s2['comparison_complete']}**",
        f"- Rules-Only evidence: {s2['completion_evidence']['sun_rule_only']}",
        f"- LLM-SE evidence: {s2['completion_evidence']['direct_llm']}",
        f"- remaining calls: {s2['remaining_calls']}",
        f"- S2.13 blockers: {report['s2_13']['blockers']}",
        "",
        "## Oracle isolation (frozen development evaluation surface)",
        "",
        "| rule source | macro-F1 | exact | detected | unobservable |",
        "|---|---:|---:|---:|---:|",
    ]
    for arm in ("oracle", "oracle_obligation_only", "reference"):
        if arm not in three:
            continue
        ev = three[arm]
        lines.append(f"| {arm} | {ev['macro_f1']:.4f} | "
                     f"{ev['exact_type_accuracy']:.4f} | {ev['detected']} | "
                     f"{ev['unobservable']} |")
    lines += [
        "",
        "No post-result method, rule, prompt, threshold, or Gold adjustment was "
        "made. The cancelled repair arm is never consulted.",
        "",
        "Historical verifier lifecycle: v1-v9 stay byte-exact; v9's three-method / "
        "API-arm S2.12 state is superseded by the two-method contract bound here.",
        "",
    ]
    return ("\n".join(lines)).encode("utf-8")


def build_artifacts(history: Mapping[str, Any]) -> dict[Path, bytes]:
    report = build_report(history)
    report_bytes = _json_bytes(report)
    md_bytes = _render_md(report)
    required_bindings = (
        *V9_ASSETS,
        "scripts/build_s2_12_two_method_contract_v1.py",
        "configs/s2_12_active_method_scope_v1.json",
        "configs/s2_12_active_preflight_v2.json",
        "outputs/reports/s2_12_active_preflight_v2.json",
        "data/input/s2_12_complex_corpus_formal_input_v1.json",
        "data/results/s2_12_sun_rule_only_v1/evaluation.json",
        "data/predictions/s2_12_sun_rule_only_v1/predictions.json",
        "data/predictions/s2_12_sun_rule_only_v1/manifest.json",
    )
    bindings = {rel: _sha(ROOT / rel) for rel in required_bindings}
    for rel, path in (
        (TWO_METHOD_CONTRACT.relative_to(ROOT).as_posix(), TWO_METHOD_CONTRACT),
        (TWO_METHOD_MANIFEST.relative_to(ROOT).as_posix(), TWO_METHOD_MANIFEST),
        (DIRECT_EVAL.relative_to(ROOT).as_posix(), DIRECT_EVAL),
        (DIRECT_PRED.relative_to(ROOT).as_posix(), DIRECT_PRED),
        (DIRECT_RUN_MANIFEST.relative_to(ROOT).as_posix(), DIRECT_RUN_MANIFEST),
    ):
        if path.is_file():
            bindings[rel] = _sha(path)
    manifest = {
        "schema_version": "s2_13_s3_7_transition_readiness_manifest@10.0.0",
        "manifest_id": "s2_13_s3_7_transition_readiness_v10.manifest",
        "artifacts": {
            "report_json": {"path": REPORT.relative_to(ROOT).as_posix(),
                            "sha256": hashlib.sha256(report_bytes).hexdigest(),
                            "byte_size": len(report_bytes)},
            "report_md": {"path": MARKDOWN.relative_to(ROOT).as_posix(),
                          "sha256": hashlib.sha256(md_bytes).hexdigest(),
                          "byte_size": len(md_bytes)},
        },
        "bindings": bindings,
        "implementation": {
            "builder": _binding("scripts/build_s2_13_s3_7_transition_readiness_v10.py"),
            "verifier": _binding("scripts/verify_s2_13_s3_7_transition_readiness_v10.py"),
            "schema": _binding("configs/schemas/s2_13_s3_7_transition_readiness_v10.schema.json"),
        },
        "zero_api": {"new_llm_api_calls": 0, "new_network_calls": 0},
    }
    manifest_bytes = _json_bytes(manifest)
    export = {
        "schema_version": "s2_13_s3_7_transition_readiness_export_index@10.0.0",
        "files": {
            REPORT.relative_to(ROOT).as_posix(): {
                "sha256": hashlib.sha256(report_bytes).hexdigest(),
                "byte_size": len(report_bytes)},
            MARKDOWN.relative_to(ROOT).as_posix(): {
                "sha256": hashlib.sha256(md_bytes).hexdigest(),
                "byte_size": len(md_bytes)},
            MANIFEST.relative_to(ROOT).as_posix(): {
                "sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                "byte_size": len(manifest_bytes)},
        },
    }
    return {REPORT: report_bytes, MARKDOWN: md_bytes, MANIFEST: manifest_bytes,
            EXPORT: _json_bytes(export)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--publish", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        history = historical_asset_ledger()
        artifacts = build_artifacts(history)
        if args.publish:
            existing = [path for path in artifacts if path.exists()]
            if existing:
                raise TransitionFail(f"refusing to overwrite v10 outputs: {existing}")
            OUT.mkdir(parents=True, exist_ok=True)
            staged: list[tuple[Path, Path]] = []
            for target, payload in artifacts.items():
                with tempfile.NamedTemporaryFile(dir=OUT, delete=False) as stream:
                    stage = Path(stream.name)
                    stream.write(payload)
                staged.append((stage, target))
            try:
                for stage, target in staged:
                    stage.replace(target)
            except Exception:
                for stage, _target in staged:
                    stage.unlink(missing_ok=True)
                raise
        else:
            for path, expected in artifacts.items():
                if not path.is_file() or path.read_bytes() != expected:
                    raise TransitionFail(f"v10 replay differs: {path}")
        report = json.loads(artifacts[REPORT].decode("utf-8"))
        print("S2.13 -> S3.7 transition readiness v10 VERIFIED "
              f"(S2.12 two-method complete={report['s2_12']['comparison_complete']}; "
              f"S2.13={report['s2_13']['status']}; zero API)")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Transition readiness v10 refused: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
