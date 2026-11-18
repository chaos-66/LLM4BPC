#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""课内实验三：分类学习与模型比较（完整、按顺序执行的代码材料）。

研究问题：理化检测完成、人工感官评分未知时，筛选可能获得 quality >= 7 的红葡萄酒。
来源：Cortez et al. (2009), UCI Wine Quality, DOI: 10.24432/C56S3T。
许可：CC BY 4.0；仅下载官方红葡萄酒表，不使用个人或企业识别信息。

Python 3.12；本次运行依赖的完整版本见生成的 results.json / manifest.json。
建议在独立环境安装：
  python -m pip install numpy==2.3.5 pandas==3.0.1 scipy==1.18.1 \
    scikit-learn==1.7.2 matplotlib==3.10.7 xgboost==3.1.1
运行（默认自动下载 89 KB 的官方数据包）：
  python classification_lab3.py --output lab3_results
离线运行（同一官方 CSV，不是其他网站的改版）：
  python classification_lab3.py --data winequality-red.csv --output lab3_results
输出：数据检查、划分索引、原始概率、模型指标、误分类样本、图表和来源清单。
为防止覆盖既有结果，--output 必须指向尚不存在的目录。

设计固定：去重；分层约 60/20/20；seed=42；三个模型的参数事先固定；
验证集按 FP + 3*FN 选择阈值和模型（教学情景假设，并非真实货币成本）；
最终保留训练子集拟合的模型，不合并验证集重训，不用测试集调参。
AI 用途：代码、排错及解释辅助。代码内断言属于自动核验，不能冒充学生人工复核。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import sys
import time
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen
import zipfile

# 限制线程，便于复现，也避免占用共享工作区全部资源。
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".matplotlib_cache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score,
                             confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from xgboost import XGBClassifier

SEED = 42
SOURCE_URL = "https://archive.ics.uci.edu/static/public/186/wine+quality.zip"
SOURCE_PAGE = "https://archive.ics.uci.edu/dataset/186/wine+quality"
DATA_SHA256 = "4a402cf041b025d4566d954c3b9ba8635a3a8a01e039005d97d6a710278cf05e"
FEATURES = ["fixed acidity", "volatile acidity", "citric acid", "residual sugar",
            "chlorides", "free sulfur dioxide", "total sulfur dioxide", "density",
            "pH", "sulphates", "alcohol"]
MODEL_NAMES = ["Majority baseline", "Logistic regression", "Random forest", "XGBoost"]
FP_COST, FN_COST = 1, 3


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, (np.ndarray, pd.Index)):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def write_json(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                               default=json_default, allow_nan=False) + "\n",
                    encoding="utf-8")


def evaluate(y_true, probability, threshold=0.5):
    """正类固定为 1；混淆矩阵行是真实值、列是预测值，顺序均为 [0, 1]。"""
    actual = np.asarray(y_true, dtype=int)
    predicted = (np.asarray(probability) >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(actual, predicted, labels=[0, 1]).ravel()
    assert int(tn + fp + fn + tp) == len(actual)
    # 独立手算四项指标，与 sklearn 逐项比对，避免混淆 Precision 和 Recall。
    manual = [(tp + tn) / len(actual), tp / (tp + fp) if tp + fp else 0.0,
              tp / (tp + fn) if tp + fn else 0.0,
              2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0]
    library = [accuracy_score(actual, predicted),
               precision_score(actual, predicted, zero_division=0),
               recall_score(actual, predicted, zero_division=0),
               f1_score(actual, predicted, zero_division=0)]
    assert np.allclose(manual, library, atol=1e-12)
    return dict(zip(["accuracy", "precision", "recall", "f1"], map(float, library)),
                threshold=float(threshold), tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp),
                predicted_positive=int(predicted.sum()), n=len(actual),
                cost=int(FP_COST * fp + FN_COST * fn),
                average_precision=float(average_precision_score(actual, probability)),
                roc_auc=float(roc_auc_score(actual, probability)))


def class_summary(y):
    return {"n": len(y), "negative": int((y == 0).sum()),
            "positive": int((y == 1).sum()), "positive_rate": float(y.mean())}


def build_models():
    # 所有填补器只在 fit(X_train) 内学习；LR 的缩放器也只在训练子集拟合。
    def pipe(model, scale=False):
        steps = [("imputer", SimpleImputer(strategy="median"))]
        if scale:
            steps.append(("scaler", StandardScaler()))
        return Pipeline(steps + [("model", model)])
    return {
        MODEL_NAMES[0]: pipe(DummyClassifier(strategy="most_frequent")),
        MODEL_NAMES[1]: pipe(LogisticRegression(C=1.0, solver="lbfgs", max_iter=2000,
                                                random_state=SEED), scale=True),
        MODEL_NAMES[2]: pipe(RandomForestClassifier(n_estimators=300, max_depth=8,
                              min_samples_leaf=3, max_features="sqrt", bootstrap=True,
                              random_state=SEED, n_jobs=1)),
        MODEL_NAMES[3]: pipe(XGBClassifier(n_estimators=200, max_depth=3,
                              learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                              min_child_weight=3, reg_lambda=2, objective="binary:logistic",
                              eval_metric="logloss", tree_method="hist", device="cpu",
                              random_state=SEED, n_jobs=1)),
    }


def make_figures(out, results, threshold_rows, importance):
    """英文图标签避免跨平台中文字体依赖；报告以中文解释每一幅图。"""
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.dpi": 130,
                         "savefig.dpi": 200, "font.family": "DejaVu Sans"})
    palette = ["#8795a5", "#247c92", "#d49a35", "#564d88"]
    fig, axes = plt.subplots(2, 2, figsize=(8.4, 6.2))
    for ax, name in zip(axes.flat, MODEL_NAMES):
        m = results["models"][name]["test_default"]
        matrix = np.array([[m["tn"], m["fp"]], [m["fn"], m["tp"]]])
        ax.imshow(matrix, cmap="Blues", vmin=0, vmax=max(matrix.max(), 1))
        for i in range(2):
            for j in range(2):
                tag = [["TN", "FP"], ["FN", "TP"]][i][j]
                ax.text(j, i, f"{tag} = {matrix[i,j]}", ha="center", va="center",
                        color="white" if matrix[i,j] > matrix.max() * .55 else "#17283a")
        ax.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["0: ordinary", "1: high"],
               yticklabels=["0: ordinary", "1: high"], xlabel="Predicted label",
               ylabel="True label", title=name + " (t=0.50)")
    fig.tight_layout()
    fig.savefig(out / "confusion_matrices.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.4, 3.5))
    measures = ["accuracy", "precision", "recall", "f1"]
    x = np.arange(len(measures))
    for j, name in enumerate(MODEL_NAMES):
        vals = [results["models"][name]["test_default"][k] for k in measures]
        ax.bar(x + (j - 1.5) * .19, vals, .18, label=name, color=palette[j])
    ax.set(xticks=x, xticklabels=["Accuracy", "Precision", "Recall", "F1"],
           ylim=(0, 1.02), ylabel="Test score")
    ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(.5, 1.28), frameon=False)
    fig.tight_layout()
    fig.savefig(out / "model_comparison.png")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.4))
    lr_rows = pd.DataFrame([r for r in threshold_rows if r["model"] == MODEL_NAMES[1]])
    for key, color in zip(["precision", "recall", "f1"], palette[1:]):
        axes[0].plot(lr_rows.threshold, lr_rows[key], label=key.title(), color=color)
    axes[0].legend(frameon=False)
    axes[0].set(xlabel="Threshold (validation only)", ylabel="Score", ylim=(0, 1.05))
    axes[1].plot(lr_rows.threshold, lr_rows.cost, color="#247c92", marker="o", ms=3)
    chosen = results["models"][MODEL_NAMES[1]]["selected_threshold"]
    axes[1].axvline(chosen, color="#d49a35", linestyle="--", label=f"Chosen t={chosen:.2f}")
    axes[1].set(xlabel="Threshold (validation only)", ylabel="FP + 3 FN")
    axes[1].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out / "threshold_validation.png")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8))
    coef = results["lr_coefficients"]
    idx = np.argsort([abs(c["coefficient"]) for c in coef])[-6:]
    axes[0].barh([coef[i]["feature"] for i in idx], [coef[i]["coefficient"] for i in idx],
                 color=["#247c92" if coef[i]["coefficient"] >= 0 else "#d49a35" for i in idx])
    axes[0].axvline(0, color="#8795a5", lw=.8)
    axes[0].set(xlabel="Coefficient per training SD", title="Logistic regression")
    imp = sorted(importance, key=lambda x: x["mean"])[-6:]
    axes[1].barh([x["feature"] for x in imp], [x["mean"] for x in imp],
                xerr=[x["std"] for x in imp], color="#564d88", capsize=2)
    axes[1].set(xlabel="Validation AP decrease", title=results["selected_model"] + " (validation)")
    fig.tight_layout()
    fig.savefig(out / "interpretation.png")
    plt.close(fig)


def run(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone(timedelta(hours=8))).isoformat()
    if args.data:
        raw_bytes = args.data.read_bytes()
        acquisition = "local_csv_sha256_verified"
    else:
        with urlopen(SOURCE_URL, timeout=60) as response:
            archive = response.read()
        raw_bytes = zipfile.ZipFile(io.BytesIO(archive)).read("winequality-red.csv")
        acquisition = "downloaded_from_uci"
    if sha256(raw_bytes) != DATA_SHA256:
        raise ValueError("官方 CSV SHA-256 不符；停止运行，不静默替换数据。")
    (out / "winequality-red.csv").write_bytes(raw_bytes)
    raw = pd.read_csv(io.BytesIO(raw_bytes), sep=";")
    assert list(raw.columns) == FEATURES + ["quality"]
    assert raw.shape == (1599, 12)
    assert np.isfinite(raw.to_numpy()).all()
    assert raw.quality.between(0, 10).all()
    assert (raw[FEATURES] >= 0).all().all()
    assert raw.pH.between(0, 14).all()
    assert (raw["free sulfur dioxide"] <= raw["total sulfur dioxide"]).all()

    # 先基于原始 12 列去掉完全相同记录；索引只作追溯，绝不作为特征。
    duplicates = int(raw.duplicated().sum())
    clean = raw.drop_duplicates().copy()
    clean.index = clean.index + 1  # 原 CSV 数据行编号（不含表头）。
    clean.index.name = "source_row_id"
    X, y = clean[FEATURES].copy(), (clean.quality >= 7).astype(int)
    assert len(clean) >= 1000 and len(FEATURES) >= 4
    feature_duplicates = int(X.duplicated().sum())
    # 如未来数据出现同特征、不同评分行，必须采用分组划分，而不是静默跨集合。
    if feature_duplicates:
        raise ValueError("去重后仍有相同特征组合，需先设计分层分组划分。")

    # 外层开发/测试 80/20；开发集内部训练/验证 75/25，即总样本约 60/20/20。
    development_ids, test_ids = train_test_split(X.index.to_numpy(), test_size=.20,
                                                  stratify=y, random_state=SEED)
    train_ids, validation_ids = train_test_split(development_ids, test_size=.25,
                                                  stratify=y.loc[development_ids],
                                                  random_state=SEED)
    split_ids = {"train": train_ids, "validation": validation_ids, "test": test_ids}
    assert not set(train_ids) & set(validation_ids)
    assert not set(train_ids) & set(test_ids)
    assert not set(validation_ids) & set(test_ids)
    assert set(np.concatenate(list(split_ids.values()))) == set(X.index)
    for a, b in [("train", "validation"), ("train", "test"), ("validation", "test")]:
        assert not set(map(tuple, X.loc[split_ids[a]].to_numpy())) & set(map(tuple, X.loc[split_ids[b]].to_numpy()))
    write_json(out / "split_indices.json", split_ids)

    # IQR 仅作异常观察，不删去少数类或极端样本；界限只由训练子集确定。
    train_X = X.loc[train_ids]
    q1, q3 = train_X.quantile(.25), train_X.quantile(.75)
    lower, upper = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    feature_audit = []
    for column in FEATURES:
        feature_audit.append({"feature": column, "min": float(X[column].min()),
            "max": float(X[column].max()), "missing": int(raw[column].isna().sum()),
            "missing_rate": float(raw[column].isna().mean()),
            "iqr_low_train": float(lower[column]), "iqr_high_train": float(upper[column]),
            "iqr_flagged_clean": int(((X[column] < lower[column]) | (X[column] > upper[column])).sum())})
    audit = {"raw_shape": list(raw.shape), "clean_shape": list(clean.shape),
             "missing_total": int(raw.isna().sum().sum()), "duplicate_removed": duplicates,
             "feature_duplicates_after_cleaning": feature_duplicates,
             "raw_classes": class_summary((raw.quality >= 7).astype(int)),
             "clean_classes": class_summary(y), "quality_counts": clean.quality.value_counts().sort_index().to_dict(),
             "features": feature_audit, "invalid_domain_count": 0,
             "split": {k: class_summary(y.loc[v]) for k, v in split_ids.items()}}
    write_json(out / "data_audit.json", audit)
    pd.DataFrame(feature_audit).to_csv(out / "feature_audit.csv", index=False)

    models = build_models()
    results = {"seed": SEED, "fp_cost": FP_COST, "fn_cost": FN_COST, "models": {}, "data": audit}
    threshold_rows, validation_probabilities, train_probabilities = [], {}, {}
    validation_candidates = []
    for order, (name, model) in enumerate(models.items()):
        start = time.perf_counter()
        model.fit(X.loc[train_ids], y.loc[train_ids])
        fit_seconds = time.perf_counter() - start
        assert list(model.named_steps["model"].classes_) == [0, 1]
        assert np.allclose(model.named_steps["imputer"].statistics_, train_X.median())
        train_probabilities[name] = model.predict_proba(X.loc[train_ids])[:, 1]
        validation_probabilities[name] = model.predict_proba(X.loc[validation_ids])[:, 1]
        vm = evaluate(y.loc[validation_ids], validation_probabilities[name])
        selected_threshold = .5
        if order > 0:
            rows = []
            for threshold in np.round(np.arange(.05, 1.0, .05), 2):
                row = dict(model=name, **evaluate(y.loc[validation_ids], validation_probabilities[name], threshold))
                rows.append(row)
                threshold_rows.append(row)
            # 先最小化业务假设成本，依次以 F1、Precision、较高阈值打破平局。
            best = min(rows, key=lambda r: (r["cost"], -r["f1"], -r["precision"], -r["threshold"]))
            selected_threshold = best["threshold"]
            vm_selected = evaluate(y.loc[validation_ids], validation_probabilities[name], selected_threshold)
        else:
            vm_selected = vm
        # 同成本/指标时优先简单模型；多数类基线也有资格成为最终选择。
        validation_candidates.append((vm_selected["cost"], -vm_selected["f1"],
                                      -vm_selected["precision"], order, name))
        results["models"][name] = {"fit_seconds": fit_seconds, "selected_threshold": selected_threshold,
                "train_default": evaluate(y.loc[train_ids], train_probabilities[name]),
                "validation_default": vm, "validation_selected": vm_selected}
    selected_model = min(validation_candidates)[-1]
    results["selected_model"] = selected_model
    results["selection_rule"] = "Validation min(FP+3*FN), then max F1, max precision, simpler model"
    scaler = models[MODEL_NAMES[1]].named_steps["scaler"]
    assert int(scaler.n_samples_seen_) == len(train_ids)
    assert np.allclose(scaler.mean_, train_X.mean())
    coefficients = models[MODEL_NAMES[1]].named_steps["model"].coef_[0]
    results["lr_coefficients"] = [{"feature": f, "coefficient": float(b), "odds_ratio_per_sd": float(np.exp(b))}
                                   for f, b in zip(FEATURES, coefficients)]
    results["lr_intercept"] = float(models[MODEL_NAMES[1]].named_steps["model"].intercept_[0])

    # 解释也只用验证集；不由测试集重要性反向选择特征。
    importance_result = permutation_importance(models[selected_model], X.loc[validation_ids],
                    y.loc[validation_ids], scoring="average_precision", n_repeats=10,
                    random_state=SEED, n_jobs=1)
    importance = [{"feature": f, "mean": float(m), "std": float(s)} for f, m, s in
                  zip(FEATURES, importance_result.importances_mean, importance_result.importances_std)]
    results["selected_model_validation_importance"] = importance

    # 直到模型/阈值固定后才进入测试评价；不依据此后观察重新训练或选择。
    predictions, metric_rows = [], []
    for name, model in models.items():
        start = time.perf_counter()
        test_probability = model.predict_proba(X.loc[test_ids])[:, 1]
        predict_seconds = time.perf_counter() - start
        assert np.isfinite(test_probability).all() and ((test_probability >= 0) & (test_probability <= 1)).all()
        selected_threshold = results["models"][name]["selected_threshold"]
        results["models"][name].update({"test_default": evaluate(y.loc[test_ids], test_probability),
              "test_selected": evaluate(y.loc[test_ids], test_probability, selected_threshold),
              "predict_seconds_test_batch": predict_seconds})
        for split, ids, probs in [("train", train_ids, train_probabilities[name]),
                                  ("validation", validation_ids, validation_probabilities[name]),
                                  ("test", test_ids, test_probability)]:
            for rid, p in zip(ids, probs):
                predictions.append({"source_row_id": int(rid), "split": split, "model": name,
                    "quality": int(clean.loc[rid, "quality"]), "actual": int(y.loc[rid]),
                    "probability": float(p), "prediction_default": int(p >= .5),
                    "selected_threshold": selected_threshold, "prediction_selected": int(p >= selected_threshold)})
        for stage in ["train_default", "validation_default", "validation_selected", "test_default", "test_selected"]:
            metric_rows.append(dict(model=name, evaluation=stage, **results["models"][name][stage]))
    pd.DataFrame(metric_rows).to_csv(out / "metrics.csv", index=False)
    pd.DataFrame(threshold_rows).to_csv(out / "validation_thresholds.csv", index=False)
    prediction_df = pd.DataFrame(predictions)
    prediction_df.to_csv(out / "predictions.csv", index=False)

    # 确定性选择 3 个 FP 和 3 个 FN，避免只挑有利于结论的错误。
    selected_test = prediction_df[(prediction_df.model == selected_model) & (prediction_df.split == "test")].copy()
    selected_test["error"] = np.where(selected_test.actual == 0, "FP", "FN")
    errors = selected_test[selected_test.actual != selected_test.prediction_selected]
    chosen_errors = pd.concat([errors[errors.error == kind].sort_values("source_row_id").head(3)
                               for kind in ["FP", "FN"]])
    chosen_errors = chosen_errors.merge(X.reset_index(), on="source_row_id", validate="one_to_one")
    chosen_errors.to_csv(out / "error_examples.csv", index=False)
    results["error_examples"] = chosen_errors.to_dict("records")
    results["environment"] = {"python": platform.python_version(), "platform": platform.platform(),
        "processor": platform.processor(), "cpu_count": os.cpu_count(), "model_threads": 1,
        "packages": {p: importlib.metadata.version(p) for p in
                     ["numpy", "pandas", "scipy", "scikit-learn", "matplotlib", "xgboost", "threadpoolctl", "joblib"]}}
    results["verification"] = {"disjoint_indices": True, "no_cross_split_duplicate_features": True,
        "train_only_imputer_and_scaler": True, "manual_metrics_equal_sklearn": True,
        "positive_class_order_verified": True, "no_test_selection": True,
        "known_source_hash_verified": True, "human_review_performed_by_script": False}
    make_figures(out, results, threshold_rows, importance)
    write_json(out / "results.json", results)
    manifest = {"run_id": "coursework-lab3-red-wine-seed42", "scope": "standalone_coursework_not_LLM4BPC_pipeline",
        "started_at": started, "finished_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "data_source": SOURCE_PAGE, "download_url": SOURCE_URL, "source_file": "winequality-red.csv",
        "source_doi": "10.24432/C56S3T", "license": "CC BY 4.0", "acquisition": acquisition,
        "data_sha256": DATA_SHA256, "code_sha256": sha256(Path(__file__).read_bytes()),
        "command": sys.argv, "seed": SEED, "gold_changed": False, "llm_api_calls": 0,
        "environment": results["environment"], "model_parameters": {
            # XGBoost 的 missing 默认值是 NaN；以字符串记载，保持 JSON 严格有效。
            name: {key: ("NaN" if isinstance(value, float) and np.isnan(value) else value)
                   for key, value in model.named_steps["model"].get_params().items()}
            for name, model in models.items()},
        "files": {p.name: sha256(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()}}
    write_json(out / "manifest.json", manifest)
    print(pd.DataFrame([dict(model=name, **results["models"][name]["test_default"]) for name in MODEL_NAMES])
          [["model", "accuracy", "precision", "recall", "f1", "tn", "fp", "fn", "tp"]].to_string(index=False))
    print("Validation-selected model:", selected_model)
    print("Results:", out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", type=Path, help="可选：已下载的官方 winequality-red.csv")
    parser.add_argument("--output", type=Path, default=Path("lab3_results"), help="新建输出目录（不得已存在）")
    with threadpool_limits(limits=1):
        run(parser.parse_args())
