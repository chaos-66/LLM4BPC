"""Build the versioned five-way comparison report from locked local runs.

All metrics are recomputed here from the saved per-sample predictions and
the dataset labels with the shared evaluator, so no arm can report a
different metric definition.  The report keeps aggregate numbers only;
raw German sentences and per-sample predictions stay in the ignored run
directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bpc_hybrid.modality_benchmark import data as data_mod  # noqa: E402
from bpc_hybrid.modality_benchmark.metrics import (  # noqa: E402
    LABELS,
    label_distribution,
    evaluate,
)

DEFAULT_RUN_ID = "s28_sun_modality_five_way_v1"
RUN_ROOT = ROOT / "outputs/development"
REPORT_DIR = ROOT / "outputs/reports"

DISPLAY = {
    "cfkw": "CFKW",
    "cfrnn": "CFRNN (BiLSTM)",
    "cfcnn": "CFCNN (CNN)",
    "sun": "Sun (BERT-TextCNN)",
    "llm_se": "LLM-SE",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git(*args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=ROOT.parent, capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def read_predictions(path: Path) -> dict[str, str | None]:
    rows: dict[str, str | None] = {}
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if not raw.strip():
                continue
            row = json.loads(raw)
            rows[row["sample_id"]] = row.get("predicted")
    return rows


def llm_predictions(path: Path) -> tuple[dict[str, str | None], dict[str, Any]]:
    predictions: dict[str, str | None] = {}
    cost = 0.0
    calls = 0
    statuses: dict[str, int] = {}
    models: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if not raw.strip():
                continue
            row = json.loads(raw)
            predictions[row["sample_id"]] = row.get("label")
            cost += float(row.get("cost_cny") or 0.0)
            calls += 1
            statuses[row["parse_status"]] = statuses.get(row["parse_status"], 0) + 1
            if row.get("returned_model"):
                models.add(row["returned_model"])
    return predictions, {
        "calls": calls,
        "cost_cny": round(cost, 6),
        "parse_status_counts": statuses,
        "returned_models": sorted(models),
    }


def arm_metrics(gold: Sequence[str], predictions: dict[str, str | None], order: Sequence[str]) -> tuple[dict[str, Any], list[int]]:
    missing = [sid for sid in order if sid not in predictions]
    pred = [predictions.get(sid) for sid in order]
    metrics = evaluate(gold, pred)
    return metrics, missing


def fmt(value: float) -> str:
    return f"{value:.4f}"


def build_markdown(report: dict[str, Any]) -> str:
    methods = report["methods"]
    lines = [
        "# Sun modality 五方法对比（独立补充实验）",
        "",
        f"- suite: `{report['suite_id']}`",
        f"- 生成时间（UTC）: `{report['generated_at']}`",
        f"- 数据: `{report['dataset']['dataset_dir']}`，固定划分 1985/420/426，seed 20260715，"
        f"测试集 {report['population']['rows']} 条全部进入统计",
        f"- 主指标: 四分类 Macro-F1；同一评价器 `{report['evaluator']}`",
        f"- EStG-150 主表（S2.10）未被替换，本表为独立补充",
        "",
        "## 主表（测试集 426 条）",
        "",
        "| 方法 | Accuracy | Macro-P | Macro-R | Macro-F1 | 失败数 | 失败率 | 运行时间(s) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key in ["cfkw", "cfrnn", "cfcnn", "sun", "llm_se"]:
        arm = methods.get(key)
        if not arm:
            continue
        m = arm["metrics"]
        runtime = m.get("runtime_seconds")
        train = m.get("training_seconds") or 0.0
        total_runtime = (runtime or 0.0) + train
        lines.append(
            f"| {DISPLAY[key]} | {fmt(m['accuracy'])} | {fmt(m['macro_precision'])} | "
            f"{fmt(m['macro_recall'])} | {fmt(m['macro_f1'])} | {m['failures']} | "
            f"{fmt(m['failure_rate'])} | {total_runtime:.2f} |"
        )
    lines += ["", "## 分类别 F1（support 为测试集真值条数）", "",
              "| 方法 | definition (177) | obligation (195) | permission (39) | prohibition (15) |",
              "|---|---:|---:|---:|---:|"]
    for key in ["cfkw", "cfrnn", "cfcnn", "sun", "llm_se"]:
        arm = methods.get(key)
        if not arm:
            continue
        pc = arm["metrics"]["per_class"]
        lines.append(
            f"| {DISPLAY[key]} | {fmt(pc['definition']['f1'])} | {fmt(pc['obligation']['f1'])} | "
            f"{fmt(pc['permission']['f1'])} | {fmt(pc['prohibition']['f1'])} |"
        )
    lines += ["", "## 与 Sun 的差值（Macro-F1 百分点，正数表示更高）", "",
              "| 方法 | Δ Macro-F1 (pp) | Δ Accuracy (pp) |", "|---|---:|---:|"]
    for key, delta in report["deltas_vs_sun"].items():
        lines.append(
            f"| {DISPLAY.get(key, key)} | {delta['delta_macro_f1_pp']:+.4f} | "
            f"{delta['delta_accuracy_pp']:+.4f} |"
        )
    budget = report.get("llm_budget") or {}
    if budget:
        lines += [
            "",
            "## LLM-SE 真实调用与费用",
            "",
            f"- 调用次数: {budget['calls']}（计划 {budget['planned_calls']}，无重试）",
            f"- 实际费用: ¥{budget['cost_cny']:.4f}（上限 ¥{budget['cap_cny']:.2f}）",
            f"- 返回模型: {', '.join(budget['returned_models']) or 'n/a'}",
            f"- 解析状态分布: {json.dumps(budget['parse_status_counts'], ensure_ascii=False)}",
            f"- 价格窗口: {budget['price_window_at_start']} → {budget['price_window_at_end']}",
        ]
    lines += ["", "## 实现与原论文的差异（必读）", ""]
    for item in report["differences"]:
        lines.append(f"- {item}")
    lines += ["", "## 局限", ""]
    for item in report["limitations"]:
        lines.append(f"- {item}")
    lines += ["", "## 复现命令", "", "```bash"]
    lines += report["reproduction"]["commands"]
    lines += ["```", ""]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    run_dir = RUN_ROOT / args.run_id
    inventory = data_mod.verify_splits()
    test = data_mod.load_split("test")
    gold = [row.label for row in test]
    order = [row.sample_id for row in test]

    methods: dict[str, Any] = {}
    missing_report: dict[str, list[str]] = {}

    # local arms
    for key in ["cfkw", "cfrnn", "cfcnn", "sun"]:
        arm_path = run_dir / key / f"{key}.json"
        pred_path = run_dir / key / "local_only/test_predictions.jsonl"
        if not arm_path.exists():
            continue
        arm = json.loads(arm_path.read_text(encoding="utf-8"))
        predictions = read_predictions(pred_path)
        metrics, missing = arm_metrics(gold, predictions, order)
        declared = arm.get("test_metrics") or {}
        if declared.get("runtime_seconds") is not None:
            metrics["runtime_seconds"] = declared["runtime_seconds"]
        if arm.get("training_seconds") is not None:
            metrics["training_seconds"] = arm["training_seconds"]
        methods[key] = {
            "display_name": DISPLAY[key],
            "metrics": metrics,
            "declared_metrics": declared,
            "config": arm.get("config") or arm.get("classifier") or {},
            "provenance": {
                k: v
                for k, v in arm.items()
                if k in {
                    "checkpoint",
                    "classifier_config",
                    "run_manifest",
                    "selected_candidate",
                    "dev_candidate_scores",
                    "dev_metrics",
                    "reused_weights",
                    "retrained_here",
                    "implementation_difference",
                    "training_seed",
                    "trained_on_split",
                    "best_epoch",
                    "epochs_completed",
                    "training_seconds",
                }
            },
        }
        if missing:
            missing_report[key] = missing

    # llm arm
    llm_summary_path = run_dir / "llm_se/llm_se_run.json"
    llm_resp_path = run_dir / "llm_se/llm_se_responses.jsonl"
    llm_budget = None
    if llm_resp_path.exists():
        predictions, budget = llm_predictions(llm_resp_path)
        metrics, missing = arm_metrics(gold, predictions, order)
        summary = (
            json.loads(llm_summary_path.read_text(encoding="utf-8"))
            if llm_summary_path.exists()
            else {}
        )
        methods["llm_se"] = {
            "display_name": DISPLAY["llm_se"],
            "metrics": metrics,
            "provenance": {
                "prompt_sha256": summary.get("prompt_sha256"),
                "model_accepted": summary.get("model_accepted"),
                "status": summary.get("status"),
                "input_language": "de",
            },
        }
        llm_budget = {
            "calls": budget["calls"],
            "planned_calls": inventory["test"]["rows"],
            "cost_cny": budget["cost_cny"],
            "cap_cny": summary.get("cap_cny", 20.0),
            "returned_models": budget["returned_models"],
            "parse_status_counts": budget["parse_status_counts"],
            "price_window_at_start": summary.get("first_price_window", "off_peak"),
            "price_window_at_end": summary.get("final_price_window"),
        }
        if missing:
            missing_report["llm_se"] = missing

    if "sun" not in methods:
        raise SystemExit("the Sun arm must exist before building the comparison report")

    deltas = {}
    base = methods["sun"]["metrics"]
    for key, arm in methods.items():
        if key == "sun":
            continue
        deltas[key] = {
            "delta_macro_f1_pp": round((arm["metrics"]["macro_f1"] - base["macro_f1"]) * 100, 4),
            "delta_accuracy_pp": round((arm["metrics"]["accuracy"] - base["accuracy"]) * 100, 4),
        }

    report = {
        "schema_version": "sun_modality_five_way_report@1.0.0",
        "suite_id": "SUN-MODALITY-5WAY-001",
        "generated_at": now(),
        "scope": (
            "independent supplement to S2.4/EXP-S2A; does not replace the "
            "frozen EStG-150 S2.10 comparison and contains no paper-reported "
            "Sun value"
        ),
        "git": {
            "commit": git("rev-parse", "HEAD"),
            "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "worktree_dirty": bool(git("status", "--porcelain")),
        },
        "dataset": data_mod.dataset_binding(),
        "population": {
            "rows": len(test),
            "label_distribution": label_distribution(gold),
            "sample_id_order_sha256": hashlib.sha256(
                "\n".join(order).encode("utf-8")
            ).hexdigest(),
        },
        "evaluator": "src/bpc_hybrid/modality_benchmark/metrics.py::evaluate",
        "methods": methods,
        "deltas_vs_sun": deltas,
        "llm_budget": llm_budget,
        "missing_predictions": missing_report,
        "differences": [
            "CFKW, CFRNN and CFCNN are independent reimplementations from the paper description; no author code, lexicon, embedding table or hyperparameters were available, and they are never referred to as the authors' original systems.",
            "CFKW rule priority order and fallback class were selected on the dev split from four pre-declared candidates; the selected configuration is recorded with the arm.",
            "Sun is the project's own BERT-TextCNN reconstruction (Legal-BERT base uncased) trained on the same train split; paper-reported scores are not used anywhere in this table.",
            "The bound Sun checkpoint (candidate B) uses inverse-sqrt class-frequency weighted cross-entropy, while the S2.4 base config declares unweighted cross-entropy; the checkpoint is the one the project binds for the Sun baseline.",
            "LLM-SE reuses the frozen EStG-150 prompt, schema and sampling policy (temperature 0, top_p 1, max_tokens 4096, thinking disabled, no retry) with deepseek-v4-pro (DeepSeek-V4-Pro-0813).",
            "The frozen LLM-SE prompt was authored for the English EStG-150 text and here receives German sentences, because every arm must see the same German original. This language mismatch is a real deviation and is reported, not corrected.",
            "No modality-only prompt is used; such a prompt would have to be reported separately as 'LLM modality-only' and is not part of this table.",
        ],
        "limitations": [
            "The 426-row test split is a project-reconstructed deterministic split (seed 20260715), not Sun's original split.",
            "The same test split was already used by the S2.4 candidate evaluation (2026-07-22) and the S2.7 alignment check (2026-08-08); it is therefore not pristine for the Sun arm, and all arms are single-seed without repeated runs.",
            "The official modality data license remains unknown_pending_confirmation; raw sentences, vectors and row-level predictions stay local and are not redistributed.",
            "Only one seed and one run per arm are reported; no significance test or confidence interval is claimed.",
        ],
        "reproduction": {
            "commands": [
                "cd formal_experiment",
                "python scripts/run_sun_modality_five_way_v1.py --methods cfkw,cfcnn,cfrnn,sun",
                "python scripts/run_sun_modality_llm_se_v1.py --preflight",
                "python scripts/run_sun_modality_llm_se_v1.py --execute   # off-peak window",
                "python scripts/build_sun_modality_five_way_report_v1.py",
            ]
        },
        "safety": {
            "gold_modified": False,
            "estg150_results_modified": False,
            "paper_values_inserted": False,
            "failed_samples_dropped": False,
            "third_party_text_committed": False,
        },
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORT_DIR / "sun_modality_five_way_v1.json"
    md_path = REPORT_DIR / "sun_modality_five_way_v1.md"
    for path in (json_path, md_path):
        if path.exists() and not args.force:
            raise SystemExit(f"refusing to overwrite {path}")
    with json_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    md_path.write_text(build_markdown(report), encoding="utf-8", newline="\n")
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    for key, arm in methods.items():
        m = arm["metrics"]
        print(
            f"{key:7s} macro_f1={m['macro_f1']:.6f} acc={m['accuracy']:.6f} "
            f"failures={m['failures']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
