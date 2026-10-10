"""Fresh native Winter replay on the frozen paper-facing Stage 3 population.

Preparation snapshots an active worktree without changing it. Inference reads
only raw regulations and BPMNs, scores every case against every requirement,
and persists all outputs before the separate evaluation command reads labels.
No LLM, network, threshold selection, or Sun/Ours execution is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for directory in (ROOT / "src", ROOT / "scripts"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

RUN_ID = "stage3_winter_paper_rerun_20261010_v1"
BUNDLE = ROOT / "data/development" / RUN_ID
OUT = ROOT / "outputs/evidence" / RUN_ID
CONFIG = ROOT / "configs" / f"{RUN_ID}.json"
REPORT = ROOT / "outputs/reports" / RUN_ID
TYPES = ("missing_action", "incorrect_actor", "out_of_order")
METRICS_SOURCE = "src/bpc_hybrid/stage3_v2/evaluation_v2.py"
CODE = [
    "scripts/run_stage3_winter_paper_rerun_v1.py",
    "scripts/stage3_winter_paper_metrics_v1.py",
    "src/bpc_hybrid/stage3_sun_style_checker.py",
    "src/bpc_hybrid/winter_stage3/winter_clause.py",
    "src/bpc_hybrid/winter_stage3/winter_model.py",
    "src/bpc_hybrid/winter_stage3/winter_pair.py",
    "src/bpc_hybrid/winter_stage3/winter_similarity.py",
    "src/bpc_hybrid/winter_stage3/global_roles.py",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8", newline="\n")


def git_state(directory: Path) -> dict:
    def command(*args):
        return subprocess.check_output(["git", *args], cwd=directory, encoding="utf-8").strip()
    return {"commit": command("rev-parse", "HEAD"),
            "branch": command("branch", "--show-current"),
            "dirty_paths": command("status", "--porcelain=v1").splitlines()}


def verify_bindings(bindings: dict) -> None:
    for rel, expected in bindings.items():
        path = (ROOT / rel).resolve()
        if not path.is_relative_to(ROOT.resolve()) or sha(path) != expected:
            raise RuntimeError(f"binding mismatch: {rel}")


def validate_inference(view: dict, sources: dict) -> None:
    if view.get("gold_labels_present") is not False:
        raise RuntimeError("inference view must explicitly exclude labels")
    cases = set()
    for item in view["items"]:
        if set(item) != {"case_id", "bpmn_path", "process_id"}:
            raise RuntimeError("forbidden inference fields")
        if item["case_id"] in cases:
            raise RuntimeError("duplicate inference case")
        cases.add(item["case_id"])
    ids = set()
    for row in sources["rules"]:
        if set(row) != {"rule_id", "text", "text_sha256"} or row["rule_id"] in ids:
            raise RuntimeError("invalid raw regulation input")
        if hashlib.sha256(row["text"].encode("utf-8")).hexdigest() != row["text_sha256"]:
            raise RuntimeError("regulation text hash mismatch")
        ids.add(row["rule_id"])


def prepare(source: Path) -> dict:
    source = source.resolve()
    if BUNDLE.exists() or CONFIG.exists():
        raise RuntimeError("input snapshot already exists; use infer/evaluate, never overwrite")
    if source.name != "formal_experiment" or any(p in {"_retired", "archive", "references"} for p in source.parts):
        raise RuntimeError("source must be an active formal_experiment worktree")
    pool_path = source / "data/development/stage3_final_development_pool_v1.json"
    supplement_path = source / "data/development/stage3_final_order_supplement_v1/manifest.json"
    source_path = source / "data/development/stage3_table3_r5_benchmark_v2/source_requirements.json"
    scope_path = source / "outputs/reports/stage3_final_order_eligibility_v1.json"
    canonical_path = source / "outputs/reports/stage3_table3_provisional_final_v1.json"
    convergence_path = source / "outputs/reports/stage3_final_convergence_report_v1.json"
    old_manifest_path = source / "outputs/reports/stage3_table3_r5_winter_native_manifest_v1.json"
    old_signals_path = source / "outputs/evidence/stage3_table3_r5_formal_v1/signals_matrix.json"
    pool, supplement, canonical = read(pool_path), read(supplement_path), read(canonical_path)
    convergence_lf_sha = hashlib.sha256(convergence_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    if convergence_lf_sha != canonical["source_result_sha256"]:
        raise RuntimeError("canonical Table 3 source report hash mismatch")
    cases = [dict(c) for c in pool["cases"]] + [dict(c) for c in supplement["cases"]]
    if len(cases) != 115 or len({c["case_id"] for c in cases}) != 115:
        raise RuntimeError("paper population must be 113 original + 2 order supplement cases")
    by_id = {row["requirement_id"]: row for row in read(source_path)["requirements"]}
    rule_ids = sorted({c["requirement_id"] for c in cases})
    rules = []
    for rid in rule_ids:
        text = by_id[rid]["excerpt_text"]
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if any(c["source_text_sha256"] != digest for c in cases if c["requirement_id"] == rid):
            raise RuntimeError(f"case regulation text drift: {rid}")
        rules.append({"rule_id": rid, "text": text, "text_sha256": digest})
    code_equivalence = {}
    for rel in CODE[2:]:
        equal = (ROOT / rel).read_text(encoding="utf-8") == (source / rel).read_text(encoding="utf-8")
        code_equivalence[rel] = equal
        if not equal:
            raise RuntimeError(f"Winter implementation differs across worktrees: {rel}")
    if (ROOT / CODE[1]).read_text(encoding="utf-8") != (source / METRICS_SOURCE).read_text(encoding="utf-8"):
        raise RuntimeError("paper evaluator source copy differs beyond line endings")
    scope = {rid: row.get("order_type") or "" for rid, row in read(scope_path)["requirements"].items()}
    from stage3_winter_paper_metrics_v1 import evaluate_dev_method
    support = evaluate_dev_method("winter", cases, {}, scope)["overall"]
    if (support["scored_cells"], support["positive_support"], support["negative_support"]) != (201, 69, 132):
        raise RuntimeError("reference denominator differs from canonical Table 3")
    inputs = {}
    origins = {}
    items = []
    for c in cases:
        base = (source / "data/development/stage3_final_order_supplement_v1" if c["case_id"].startswith("case_devsupp_")
                else source / "data/development/stage3_table3_r5_benchmark_v2")
        original = base / c["bpmn_path"]
        dest = BUNDLE / "bpmn" / f"{c['case_id']}.bpmn"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(original.read_bytes())
        rel = dest.relative_to(ROOT).as_posix()
        inputs[rel] = sha(dest)
        origins[rel] = {"source_path": original.relative_to(source).as_posix(), "sha256": sha(original)}
        items.append({"case_id": c["case_id"], "bpmn_path": rel, "process_id": c["process_id"]})
    write(BUNDLE / "inference_view.json", {"gold_labels_present": False, "items": items})
    write(BUNDLE / "regulation_sources.json", {"rules": rules})
    write(BUNDLE / "evaluation_reference.json", {"cases": cases, "order_scope": scope,
                                                "is_formal_gold": False, "all_existing_cases_seen": True})
    for name, original in [("canonical_table3.json", canonical_path), ("convergence_report.json", convergence_path),
                           ("order_eligibility.json", scope_path), ("historical_winter_manifest.json", old_manifest_path)]:
        dest = BUNDLE / name
        dest.write_bytes(original.read_bytes())
        origins[dest.relative_to(ROOT).as_posix()] = {"source_path": original.relative_to(source).as_posix(), "sha256": sha(original)}
    old = read(old_signals_path)
    write(BUNDLE / "historical_winter_signals.json", {"signals": [s for s in old["signals"] if s["method"] == "winter"]})
    originals = [pool_path, supplement_path, source_path, scope_path, canonical_path, convergence_path,
                 old_manifest_path, old_signals_path, source / METRICS_SOURCE]
    write(BUNDLE / "provenance.json", {"source_formal_root": str(source), "source_git": git_state(source),
        "source_hashes": {p.relative_to(source).as_posix(): sha(p) for p in originals},
        "bpmn_origins": origins, "implementation_text_equivalence": code_equivalence,
        "convergence_report_raw_sha256": sha(convergence_path),
        "convergence_report_canonical_lf_sha256": convergence_lf_sha,
        "canonical_source_hash_match": "canonical LF only; raw snapshot bytes retained",
        "evaluator_source": METRICS_SOURCE, "base_cases": 113, "order_supplement_cases": 2,
        "note": "Canonical metadata says 113 base cases; source report counters include 2 additional order-only cases."})
    for name in ("inference_view.json", "regulation_sources.json"):
        p = BUNDLE / name
        inputs[p.relative_to(ROOT).as_posix()] = sha(p)
    inputs["configs/winter_stage3_development_v1.json"] = sha(ROOT / "configs/winter_stage3_development_v1.json")
    bundle_hashes = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(BUNDLE.rglob("*")) if p.is_file()}
    config = {"run_id": RUN_ID, "task_id": "S3-WINTER-PAPER-RERUN-V1", "scope": "development_only_same_paper_population",
        "user_authorization": "2026-10-10 用户要求确认来源并重新跑 Winter", "real_api_calls_cap": 0,
        "nlp_model": "en_core_web_sm", "gamma": 0.4, "delta": 0.8, "case_count": 115,
        "rule_count": len(rules), "scored_cells": 201, "positive_support": 69, "negative_support": 132,
        "inference_bindings": inputs, "evaluation_bindings": bundle_hashes,
        "code_bindings": {rel: sha(ROOT / rel) for rel in CODE},
        "inference_forbidden_files": ["evaluation_reference.json", "canonical_table3.json", "convergence_report.json",
                                      "historical_winter_signals.json"],
        "backend_boundary": "Sun/Ours reuse MPNet calibrated development results; Winter retains its independent native spaCy backend and fixed gamma/delta."}
    write(CONFIG, config)
    return {"status": "prepared", "cases": 115, "rules": len(rules), "scored_cells": 201}


class CachedNLP:
    """Memoize deterministic spaCy documents; do not change native scoring."""
    def __init__(self, nlp):
        self.nlp = nlp
        self.cache = {}

    def __call__(self, text):
        if text not in self.cache:
            self.cache[text] = self.nlp(text)
        return self.cache[text]


def infer() -> dict:
    if OUT.exists():
        raise RuntimeError("run directory already exists; cannot reuse or overwrite a partial run")
    cfg = read(CONFIG)
    verify_bindings(cfg["inference_bindings"])
    verify_bindings(cfg["code_bindings"])
    view, sources = read(BUNDLE / "inference_view.json"), read(BUNDLE / "regulation_sources.json")
    validate_inference(view, sources)
    import spacy
    from bpc_hybrid.winter_stage3.global_roles import collect_global_role_candidates
    from bpc_hybrid.winter_stage3.winter_clause import parse_regulation_paragraph
    from bpc_hybrid.winter_stage3.winter_model import REACHABILITY_CORRECTED, parse_bpmn_file_winter
    from bpc_hybrid.winter_stage3.winter_pair import WinterPair
    from bpc_hybrid.winter_stage3.winter_similarity import WinterSimilarity
    from bpc_hybrid.stage3_sun_style_checker import winter_signals
    started = time.perf_counter()
    nlp = CachedNLP(spacy.load(cfg["nlp_model"]))
    sim = WinterSimilarity(nlp)
    lexicon = ROOT.parent / "references/winter_2020_model_check/model_check/input/files"
    lexicon_hashes = {name: sha(lexicon / name) for name in ("stopwords.txt", "signalwords.txt", "sequencemarkers.txt")}
    stop, signalwords, seq = [set((lexicon / name).read_text(encoding="utf-8").splitlines())
                             for name in ("stopwords.txt", "signalwords.txt", "sequencemarkers.txt")]
    roles = collect_global_role_candidates(view, ROOT)
    resources = set(roles["roles"])
    paragraphs = {r["rule_id"]: parse_regulation_paragraph(r["rule_id"], r["text"], nlp, stop, signalwords, seq,
                                                           only_constraints=True) for r in sources["rules"]}
    OUT.mkdir(parents=True)
    rows = []
    for index, item in enumerate(sorted(view["items"], key=lambda r: r["case_id"]), 1):
        model = parse_bpmn_file_winter(ROOT / item["bpmn_path"], nlp, stop, reachability_mode=REACHABILITY_CORRECTED)
        for rid, paragraph in sorted(paragraphs.items()):
            pair = WinterPair(nlp, sim, model, paragraph, resources, cfg["gamma"], cfg["delta"])
            rows.append({"case_id": item["case_id"], "rule_id": rid, "fitness": float(pair.fitness),
                "cost": float(pair.cost), "cost_obligation": float(pair.cost_obligation),
                "cost_resource": float(pair.cost_resource), "cost_so": float(pair.cost_so),
                "signals": winter_signals(pair=pair, model=model, paragraph=paragraph, resource_set=resources)})
        if index % 20 == 0 or index == len(view["items"]):
            print(f"Winter cases completed: {index}/{len(view['items'])}", flush=True)
    expected = {(i["case_id"], r["rule_id"]) for i in view["items"] for r in sources["rules"]}
    validate_predictions(rows, expected)
    write(OUT / "predictions.json", {"records": rows, "gold_read_by_runner": False})
    write(OUT / "global_role_candidates.json", roles)
    manifest = {"run_id": RUN_ID, "status": "completed", "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git": git_state(ROOT), "command": "python formal_experiment/scripts/run_stage3_winter_paper_rerun_v1.py infer",
        "config_sha256": sha(CONFIG), "input_bindings": cfg["inference_bindings"], "code_bindings": cfg["code_bindings"],
        "cases": len(view["items"]), "rules": len(sources["rules"]), "pair_count": len(rows), "signals": len(rows) * 3,
        "case_ids": sorted(i["case_id"] for i in view["items"]), "rule_ids": sorted(paragraphs),
        "gamma": cfg["gamma"], "delta": cfg["delta"], "reachability_mode": REACHABILITY_CORRECTED,
        "nlp_model": cfg["nlp_model"], "spacy_version": spacy.__version__,
        "nlp_model_version": nlp.nlp.meta.get("version"), "lexicon_sha256": lexicon_hashes,
        "native_exception_count": 0, "cached_nlp_documents": len(nlp.cache),
        "elapsed_seconds": time.perf_counter() - started, "llm_api_calls": 0, "network_calls": 0,
        "gold_read_by_runner": False, "evaluation_reference_read_by_runner": False,
        "artifacts": {p.name: sha(p) for p in sorted(OUT.iterdir()) if p.is_file()}}
    write(OUT / "run_manifest.json", manifest)
    return {k: manifest[k] for k in ("status", "cases", "rules", "pair_count", "signals", "elapsed_seconds")}


def validate_predictions(rows: list, expected: set) -> None:
    actual = set()
    for row in rows:
        key = (row["case_id"], row["rule_id"])
        if key in actual or set(row["signals"]) != set(TYPES):
            raise RuntimeError("duplicate/incomplete Winter predictions")
        actual.add(key)
        if any(row["signals"][t].get("status") not in {"violated", "satisfied", "unknown"} for t in TYPES):
            raise RuntimeError("invalid Winter signal state")
    if actual != expected:
        raise RuntimeError(f"incomplete Winter population: missing={len(expected - actual)}, extra={len(actual - expected)}")


def evaluate() -> dict:
    cfg, manifest = read(CONFIG), read(OUT / "run_manifest.json")
    if manifest["status"] != "completed" or manifest["config_sha256"] != sha(CONFIG):
        raise RuntimeError("completed config-bound run required")
    for name, digest in manifest["artifacts"].items():
        if sha(OUT / name) != digest:
            raise RuntimeError(f"run output drift: {name}")
    verify_bindings(cfg["evaluation_bindings"])
    verify_bindings(cfg["code_bindings"])
    rows = read(OUT / "predictions.json")["records"]
    expected = {(cid, rid) for cid in manifest["case_ids"] for rid in manifest["rule_ids"]}
    validate_predictions(rows, expected)
    # Read evaluation labels only after persisted output and completeness checks.
    reference, canonical = read(BUNDLE / "evaluation_reference.json"), read(BUNDLE / "canonical_table3.json")
    from stage3_winter_paper_metrics_v1 import evaluate_dev_method
    lookup = {(r["case_id"], r["rule_id"]): r for r in rows}
    signals = {("winter", c["case_id"], t): lookup[(c["case_id"], c["requirement_id"])]["signals"][t]
               for c in reference["cases"] for t in TYPES}
    metrics = evaluate_dev_method("winter", reference["cases"], signals, reference["order_scope"])
    if (metrics["overall"]["scored_cells"], metrics["overall"]["positive_support"], metrics["overall"]["negative_support"]) != (201, 69, 132):
        raise RuntimeError("Winter comparison denominator drift")
    main_table = {"Sun-style Rules-Only": canonical["methods"]["Sun"],
                  "LLM-RE": canonical["methods"]["Ours"], "Winter baseline": metrics["overall"]}
    for method in ("Sun", "Ours"):
        m = canonical["methods"][method]
        counts = m["support"]
        if abs(m["f1"] - 2 * counts["TP"] / (2 * counts["TP"] + counts["FP"] + counts["FN"])) > 1e-12:
            raise RuntimeError("canonical F1 arithmetic mismatch")
    old = read(BUNDLE / "historical_winter_signals.json")["signals"]
    differences = []
    for s in old:
        fresh = lookup[(s["case_id"], s["rule_id"])]["signals"][s["check_type"]]
        for field in ("status", "raw_score", "denominator", "observable", "reason"):
            a, b = s.get(field), fresh.get(field)
            same = abs(a - b) <= 1e-12 if isinstance(a, (float, int)) and isinstance(b, (float, int)) else a == b
            if not same:
                differences.append({"case_id": s["case_id"], "rule_id": s["rule_id"], "type": s["check_type"],
                                    "field": field, "historical": a, "fresh": b})
    report = {"run_id": RUN_ID, "status": "completed_development_comparison", "formal_release_ready": False,
        "main_table": main_table, "winter_metrics": metrics, "scope": {"base_cases": 113, "order_supplement_cases": 2,
        "total_cases": 115, "requirements": 33, "scored_cells": 201, "positive_support": 69, "negative_support": 132},
        "historical_comparison": {"manifest_status": read(BUNDLE / "historical_winter_manifest.json")["status"],
                                  "signals_compared": len(old), "difference_count": len(differences), "differences": differences},
        "expected_ranking_supported": canonical["methods"]["Ours"]["f1"] > canonical["methods"]["Sun"]["f1"] > metrics["overall"]["f1"],
        "run_manifest_sha256": sha(OUT / "run_manifest.json"), "source_provenance_sha256": sha(BUNDLE / "provenance.json"),
        "validation_boundary": "Focused checks only. Existing Stage 1 correction integrity failure is unrelated and remains unmodified.",
        "limitations": ["Same constructed development benchmark as the frozen paper table; not unseen test or formal Oracle.",
                        "Sun/Ours numbers are reused from the hash-bound canonical source, not freshly rerun.",
                        cfg["backend_boundary"], "Applicable-pair checking; complete rule-selection/end-to-end performance is not claimed.",
                        "Order denominator has only 8 cells. Unknown positives remain FN; unknown negatives are not TN."],
        "real_llm_api_calls": 0, "network_calls": 0}
    write(REPORT.with_suffix(".json"), report)
    lines = ["# Stage 3：论文同口径 Winter 完整重跑", "", "状态：开发期对照完成；不是独立未见测试或正式发布。", "",
             "115 个案例（原始 113 + 顺序补充 2），33 条要求；每方法 201 个评分单元（69 正、132 负）。", "",
             "| 方法 | Precision | Recall | F1 |", "|---|---:|---:|---:|"]
    for label, m in main_table.items():
        lines.append(f"| {label} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1']:.4f} |")
    lines += ["", "Sun/LLM-RE 原数值复用固定来源，Winter 从头运行全部案例×全部要求；不按预期排序调参。", "",
              f"Winter TP/FP/FN/TN：{metrics['overall']['TP']}/{metrics['overall']['FP']}/{metrics['overall']['FN']}/{metrics['overall']['TN']}。",
              f"历史 Winter {len(old)} 个信号逐项比较，差异字段数 {len(differences)}。旧 manifest 声明 completed；无法据此判断用户另一次中断运行。", "",
              "| Winter 类型 | P | R | F1 | 评分单元 |", "|---|---:|---:|---:|---:|"]
    for t, m in metrics["per_type"].items():
        lines.append(f"| {t} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1']:.4f} | {m['scored_cells']} |")
    lines += ["", f"Winter coverage={metrics['overall']['coverage']:.4f}；unknown rate={metrics['overall']['unknown_rate']:.4f}。", "",
              "原论文表元数据标记 113 个基础案例；其来源收敛报告的计数包含另外 2 个顺序案例。本次保留原文件，明确总数 115。", "",
              "验证与限制：", "", *[f"- {x}" for x in report["limitations"]],
              "- 本工作区既有 Stage 1 correction 完整性错误仍存在；未修改用户文件，未运行全量测试。", ""]
    REPORT.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    REPORT.with_suffix(".csv").write_text("Method,Precision,Recall,F1\n" + "".join(
        f"{label},{m['precision']:.10f},{m['recall']:.10f},{m['f1']:.10f}\n" for label, m in main_table.items()), encoding="utf-8", newline="\n")
    REPORT.with_suffix(".tex").write_text("\\begin{table}[t]\n\\centering\n\\caption{Performance comparison of downstream compliance checking on the constructed development benchmark.}\n\\label{tab:stage3}\n\\begin{tabular}{lccc}\n\\hline\nMethod & Precision & Recall & F1 \\\\\n\\hline\n" + "".join(
        f"{label} & {m['precision']:.4f} & {m['recall']:.4f} & {m['f1']:.4f} \\\\\n" for label, m in main_table.items()) + "\\hline\n\\end{tabular}\n\\end{table}\n", encoding="utf-8", newline="\n")
    return {"main_table": {k: {field: v[field] for field in ("precision", "recall", "f1")} for k, v in main_table.items()},
            "historical_difference_count": len(differences), "expected_ranking_supported": report["expected_ranking_supported"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "infer", "evaluate"))
    parser.add_argument("--source-formal-root", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        if args.source_formal_root is None:
            parser.error("prepare requires --source-formal-root")
        result = prepare(args.source_formal_root)
    else:
        result = infer() if args.command == "infer" else evaluate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
