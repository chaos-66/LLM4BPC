"""Offline statistical supplement for SUN-MODALITY-BOUNDARY-001.

Computes, from already-saved artifacts only (zero API calls, zero network,
never loads a .env file, never touches Gold or frozen results):

1. exact two-sided McNemar tests on paired per-sample correctness
   (frozen v6 vs boundary branch; boundary branch vs Sun);
2. nonparametric percentile bootstrap 95% CIs (B=10,000, fixed seed,
   paired resampling, full-denominator semantics identical to the frozen
   evaluator) for per-class F1 / macro-F1 of both LLM arms and for the
   paired deltas (boundary minus v6);
3. quantification of the applicability-scope clause absorption side
   effect via transparent German markers, reported as counts and
   sample ids only -- license-restricted German sentences are never
   copied into versioned outputs.

The script fails closed on any input drift (split hash, historical
artifact hash, journal hash, or disagreement with the parent report).
"""
from __future__ import annotations

import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bpc_hybrid.modality_benchmark import boundary, data
from bpc_hybrid.modality_benchmark.metrics import LABELS, evaluate

PARENT_REPORT = ROOT / "outputs/reports/sun_modality_boundary_v1.json"
JOURNAL = ROOT / "outputs/development/sun_modality_boundary_v1/local_only/events.jsonl"
STATS = ROOT / "outputs/reports/sun_modality_boundary_stats_v1"
B = 10_000
SEED = 20261031
SCOPE_MARKERS = (
    "anzuwenden",
    "anwendbar",
    "anwendbarkeit",
    "gilt nur",
    "gilt entsprechend",
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def prf(tp: int, fp: int, fn: int) -> float:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0


def mcnemar_exact_two_sided(b: int, c: int) -> float:
    """Exact binomial McNemar: 2 * P(X <= min(b, c)), X ~ Bin(b + c, 0.5)."""
    n = b + c
    if n == 0:
        return 1.0
    m = min(b, c)
    tail = sum(math.comb(n, k) for k in range(m + 1)) / (2 ** n)
    return min(1.0, 2.0 * tail)


def percentile_ci(values: list[float]) -> list[float]:
    ordered = sorted(values)
    lo = ordered[int(round(0.025 * (len(ordered) - 1)))]
    hi = ordered[int(round(0.975 * (len(ordered) - 1)))]
    return [lo, hi]


def marker_hits(text: str) -> list[str]:
    return [m for m in SCOPE_MARKERS if m in text]


def main() -> None:
    parent = json.loads(PARENT_REPORT.read_text(encoding="utf-8"))
    contract = parent["contract"]

    # Fail-closed input bindings.
    if data.sha256_file(data.EXPECTED["test"]["path"]) != data.EXPECTED["test"]["sha256"]:
        raise SystemExit("test split hash mismatch")
    for key in ("historical_llm", "historical_sun"):
        spec = contract[key]
        if boundary.digest((ROOT / spec["path"]).read_bytes()) != spec["sha256"]:
            raise SystemExit("historical evidence drift: " + key)
    journal_sha = boundary.digest(JOURNAL.read_bytes())
    if parent.get("journal_sha256") not in (None, journal_sha):
        raise SystemExit("journal drift vs parent report")

    rows = data.load_split("test")
    order = [r.sample_id for r in rows]
    gold = [r.label for r in rows]
    texts = {r.sample_id: r.text for r in rows}

    old = {x["sample_id"]: x.get("label") for x in read_jsonl(ROOT / contract["historical_llm"]["path"])}
    sun = {x["sample_id"]: x.get("predicted") for x in read_jsonl(ROOT / contract["historical_sun"]["path"])}
    events = boundary.read_events(JOURNAL)
    finished = {x["sample_id"]: x for x in events if x["kind"] == "finished"}
    new = {sid: x.get("label") for sid, x in finished.items()}
    if len(finished) != len(order):
        raise SystemExit(f"journal covers {len(finished)} of {len(order)} samples")

    old_p = [old.get(sid) for sid in order]
    new_p = [new.get(sid) for sid in order]
    sun_p = [sun.get(sid) for sid in order]

    # Self-check: recomputation must reproduce the frozen parent report.
    m_old, m_new = evaluate(gold, old_p), evaluate(gold, new_p)
    for got, want, name in (
        (m_old, parent["metrics"]["baseline"], "baseline"),
        (m_new, parent["metrics"]["boundary"], "boundary"),
    ):
        if abs(got["macro_f1"] - want["macro_f1"]) > 1e-9 or abs(got["accuracy"] - want["accuracy"]) > 1e-9:
            raise SystemExit(f"recomputed {name} disagrees with parent report")

    # ------------------------------------------------------------------
    # 1. McNemar exact tests on paired correctness.
    # ------------------------------------------------------------------
    def paired_counts(pred_a: list[str | None], pred_b: list[str | None]) -> tuple[int, int]:
        only_a = only_b = 0
        for g, a, b in zip(gold, pred_a, pred_b):
            ca, cb = a == g, b == g
            if ca and not cb:
                only_a += 1
            elif cb and not ca:
                only_b += 1
        return only_a, only_b

    only_old, only_new = paired_counts(old_p, new_p)
    only_new_vs_sun, only_sun = paired_counts(new_p, sun_p)
    mcnemar = {
        "v6_vs_boundary": {
            "only_v6_correct": only_old,
            "only_boundary_correct": only_new,
            "p_exact_two_sided": mcnemar_exact_two_sided(only_old, only_new),
        },
        "boundary_vs_sun": {
            "only_boundary_correct": only_new_vs_sun,
            "only_sun_correct": only_sun,
            "p_exact_two_sided": mcnemar_exact_two_sided(only_new_vs_sun, only_sun),
        },
    }

    # ------------------------------------------------------------------
    # 2. Paired percentile bootstrap for per-class F1 / macro-F1 / deltas.
    # ------------------------------------------------------------------
    li = {label: i for i, label in enumerate(LABELS)}
    gi = [li[g] for g in gold]
    oi = [-1 if p is None else li[p] for p in old_p]
    ni = [-1 if p is None else li[p] for p in new_p]
    n = len(gold)
    rng = random.Random(SEED)

    old_f1: list[list[float]] = [[] for _ in LABELS]
    new_f1: list[list[float]] = [[] for _ in LABELS]
    delta_f1: list[list[float]] = [[] for _ in LABELS]
    old_macro: list[float] = []
    new_macro: list[float] = []
    delta_macro: list[float] = []

    for _ in range(B):
        idx = rng.choices(range(n), k=n)
        tpo = [0] * 4; fpo = [0] * 4; fno = [0] * 4
        tpn = [0] * 4; fpn = [0] * 4; fnn = [0] * 4
        for i in idx:
            g = gi[i]
            o = oi[i]
            if o == g:
                tpo[g] += 1
            elif o < 0:
                fno[g] += 1
            else:
                fpo[o] += 1; fno[g] += 1
            w = ni[i]
            if w == g:
                tpn[g] += 1
            elif w < 0:
                fnn[g] += 1
            else:
                fpn[w] += 1; fnn[g] += 1
        mo = mn = 0.0
        for c in range(4):
            fo = prf(tpo[c], fpo[c], fno[c])
            fw = prf(tpn[c], fpn[c], fnn[c])
            old_f1[c].append(fo)
            new_f1[c].append(fw)
            delta_f1[c].append(fw - fo)
            mo += fo
            mn += fw
        old_macro.append(mo / 4.0)
        new_macro.append(mn / 4.0)
        delta_macro.append((mn - mo) / 4.0)

    def arm_block(metrics: dict[str, Any], samples: list[list[float]], macro: list[float]) -> dict[str, Any]:
        block: dict[str, Any] = {}
        for c, label in enumerate(LABELS):
            block[label] = {
                "f1": metrics["per_class"][label]["f1"],
                "ci95": percentile_ci(samples[c]),
                "support": metrics["per_class"][label]["support"],
            }
        block["macro_f1"] = {"f1": metrics["macro_f1"], "ci95": percentile_ci(macro)}
        return block

    bootstrap = {
        "B": B,
        "seed": SEED,
        "method": "percentile bootstrap; paired resampling of the 426 test samples with replacement; "
                  "no-prediction stays in the denominator and never becomes a false positive "
                  "(identical to the frozen evaluator semantics)",
        "v6": arm_block(m_old, old_f1, old_macro),
        "boundary": arm_block(m_new, new_f1, new_macro),
        "delta_boundary_minus_v6": {},
    }
    for c, label in enumerate(LABELS):
        point = m_new["per_class"][label]["f1"] - m_old["per_class"][label]["f1"]
        bootstrap["delta_boundary_minus_v6"][label] = {"delta": point, "ci95": percentile_ci(delta_f1[c])}
    bootstrap["delta_boundary_minus_v6"]["macro_f1"] = {
        "delta": m_new["macro_f1"] - m_old["macro_f1"],
        "ci95": percentile_ci(delta_macro),
    }

    # ------------------------------------------------------------------
    # 3. Scope-clause absorption side effect (counts and ids only).
    # ------------------------------------------------------------------
    regressions = []
    for sid, g, a, b in zip(order, gold, old_p, new_p):
        if a == g and b != g:
            regressions.append({
                "sample_id": sid, "gold": g, "v6": a, "boundary": b,
                "scope_markers": marker_hits(texts[sid]),
            })
    new_def_fps = [
        {"sample_id": sid, "gold": g, "boundary": b, "scope_markers": marker_hits(texts[sid])}
        for sid, g, b in zip(order, gold, new_p) if g != "definition" and b == "definition"
    ]
    old_def_fps = [
        sid for sid, g, b in zip(order, gold, old_p) if g != "definition" and b == "definition"
    ]
    index_of = {sid: i for i, sid in enumerate(order)}
    scope_population = [sid for sid in order if marker_hits(texts[sid])]
    scope_gold: dict[str, int] = {label: 0 for label in LABELS}
    for sid in scope_population:
        scope_gold[gold[index_of[sid]]] += 1
    scope_new_correct = sum(1 for sid in scope_population if new.get(sid) == gold[index_of[sid]])
    scope_old_correct = sum(1 for sid in scope_population if old_p[index_of[sid]] == gold[index_of[sid]])
    def_fn_to_obligation = [
        sid for sid, g, b in zip(order, gold, new_p) if g == "definition" and b == "obligation"
    ]
    def_fn_to_obligation_markers = sum(1 for sid in def_fn_to_obligation if marker_hits(texts[sid]))

    side_effect = {
        "markers": list(SCOPE_MARKERS),
        "regressions_total": len(regressions),
        "regressions_to_definition": sum(1 for r in regressions if r["boundary"] == "definition"),
        "regressions_with_scope_marker": sum(1 for r in regressions if r["scope_markers"]),
        "regressions_detail": regressions,
        "boundary_definition_fp": len(new_def_fps),
        "boundary_definition_fp_with_scope_marker": sum(1 for x in new_def_fps if x["scope_markers"]),
        "boundary_definition_fp_detail": new_def_fps,
        "v6_definition_fp": len(old_def_fps),
        "scope_marker_population": len(scope_population),
        "scope_marker_gold_distribution": scope_gold,
        "scope_marker_subset_correct": {"v6": scope_old_correct, "boundary": scope_new_correct,
                                        "n": len(scope_population)},
        "definition_fn_to_obligation_boundary": len(def_fn_to_obligation),
        "definition_fn_to_obligation_with_scope_marker": def_fn_to_obligation_markers,
    }

    result = {
        "suite_id": contract["suite_id"],
        "supplement": "offline statistics v1 (McNemar + paired bootstrap + scope side effect)",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "claim_scope": parent["claim_scope"],
        "inputs": {
            "test_split_sha256": data.EXPECTED["test"]["sha256"],
            "historical_llm_sha256": contract["historical_llm"]["sha256"],
            "historical_sun_sha256": contract["historical_sun"]["sha256"],
            "journal_sha256": journal_sha,
            "parent_report_preflight_sha256": parent["preflight_sha256"],
        },
        "consistency_check": {
            "recomputed_v6_macro_f1": m_old["macro_f1"],
            "recomputed_boundary_macro_f1": m_new["macro_f1"],
            "matches_parent_report": True,
        },
        "mcnemar": mcnemar,
        "bootstrap": bootstrap,
        "side_effect_scope_clauses": side_effect,
        "limitations": [
            "统计量描述本次单次运行在固定 426 测试集上的抽样波动，不覆盖提示词设计层面的随机性。",
            "提示词为看过测试错误后设计，所有差值是上界估计，不是盲测确认。",
            "bootstrap 为百分位法、非分层；小类别（prohibition n=15）的区间宽度本身即说明单次差异不可作为稳健结论。",
            "McNemar 与 bootstrap 互不替代：前者检验配对正确性翻转，后者给出 F1 尺度的不确定度。",
            "德语原文不进入版本化产物；副作用分析只含 sample_id、标签与标记命中计数。",
        ],
    }

    STATS.parent.mkdir(parents=True, exist_ok=True)
    with STATS.with_suffix(".json").open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")

    d = bootstrap["delta_boundary_minus_v6"]
    lines = ["# sun_modality_boundary_v1 统计补强（纯离线，零 API）", "",
             f"- 输入：已保存预测（历史 v6 / 边界分支 / Sun）+ 哈希校验测试集；重算点估计与主报告逐位一致。",
             f"- bootstrap：B={B}，seed={SEED}，配对重采样，全分母口径（无预测计失败、不产生误报）。", "",
             "## McNemar 精确检验（双侧）",
             "| 对照 | 仅A对 | 仅B对 | p 值 |", "|---|---:|---:|---:|"]
    mnv = mcnemar["v6_vs_boundary"]
    mns = mcnemar["boundary_vs_sun"]
    lines.append(f"| v6 vs 边界分支 | {mnv['only_v6_correct']} | {mnv['only_boundary_correct']} | "
                 f"{mnv['p_exact_two_sided']:.3e} |")
    lines.append(f"| 边界分支 vs Sun | {mns['only_boundary_correct']} | {mns['only_sun_correct']} | "
                 f"{mns['p_exact_two_sided']:.3e} |")
    lines += ["", "## Bootstrap 95% CI",
              "| 类别 | 原v6 F1 [CI] | 边界分支 F1 [CI] | ΔF1 [CI] |",
              "|---|---|---|---|"]
    for label in LABELS:
        v6b = bootstrap["v6"][label]
        nb = bootstrap["boundary"][label]
        dl = d[label]
        lines.append(
            f"| {label} (n={v6b['support']}) | {v6b['f1']:.4f} [{v6b['ci95'][0]:.4f}, {v6b['ci95'][1]:.4f}] "
            f"| {nb['f1']:.4f} [{nb['ci95'][0]:.4f}, {nb['ci95'][1]:.4f}] "
            f"| {dl['delta']:+.4f} [{dl['ci95'][0]:+.4f}, {dl['ci95'][1]:+.4f}] |")
    v6m, nm, dm = bootstrap["v6"]["macro_f1"], bootstrap["boundary"]["macro_f1"], d["macro_f1"]
    lines.append(
        f"| **macro-F1** | {v6m['f1']:.4f} [{v6m['ci95'][0]:.4f}, {v6m['ci95'][1]:.4f}] "
        f"| {nm['f1']:.4f} [{nm['ci95'][0]:.4f}, {nm['ci95'][1]:.4f}] "
        f"| {dm['delta']:+.4f} [{dm['ci95'][0]:+.4f}, {dm['ci95'][1]:+.4f}] |")
    lines += ["", "## 适用范围条款吸收副作用（标记："
              + " / ".join(SCOPE_MARKERS) + "）",
              f"- 回归 {side_effect['regressions_total']} 条：判为 definition {side_effect['regressions_to_definition']} 条，"
              f"其中含范围标记 {side_effect['regressions_with_scope_marker']} 条。",
              f"- 边界分支 definition 误报 {side_effect['boundary_definition_fp']} 条，"
              f"含范围标记 {side_effect['boundary_definition_fp_with_scope_marker']} 条"
              f"（原v6 definition 误报 {side_effect['v6_definition_fp']} 条）。",
              f"- 全测试集含范围标记样本 {side_effect['scope_marker_population']} 条，gold 分布 "
              + "、".join(f"{k}={v}" for k, v in side_effect["scope_marker_gold_distribution"].items())
              + f"；该子集正确数 v6 {side_effect['scope_marker_subset_correct']['v6']}"
              f" vs 边界分支 {side_effect['scope_marker_subset_correct']['boundary']}。",
              f"- 对照：边界分支仍把 {side_effect['definition_fn_to_obligation_boundary']} 条 gold=definition "
              f"判为 obligation，其中含范围标记 {side_effect['definition_fn_to_obligation_with_scope_marker']} 条"
              "（残余漏抽不是同类机制）。", ""]
    lines += ["- " + note for note in result["limitations"]]
    with STATS.with_suffix(".md").open("x", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    print(json.dumps({"report": str(STATS), "mcnemar_p_v6_vs_boundary": mcnemar["v6_vs_boundary"]["p_exact_two_sided"],
                      "macro_f1_delta_ci95": d["macro_f1"]["ci95"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
