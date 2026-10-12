# -*- coding: utf-8 -*-
"""Shared full-rule-base Stage 3 checker for Table 3 v3.

The checker is intentionally dumb about benchmarks: it receives one current
Process Model, the complete method-specific Rule Base, and the frozen Sun
scorer. It ranks every rule by Definition 4, keeps rules with
``matching_score > tau``, and then applies Definitions 5-7 to those associated
rules. It never receives a target rule id, target activity, mutation type,
pair role, or Gold label.
"""

from __future__ import annotations

from typing import Any, Mapping

TYPES = ("missing_action", "incorrect_actor", "out_of_order")


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return str(value)


def normalize_sun_signal(check_type: str,
                         raw: Mapping[str, Any] | None) -> dict[str, Any]:
    """Turn a raw SunScorer result into an explicit three-state signal."""
    raw = dict(raw or {})
    details = _jsonable(raw.get("details") or [])
    if check_type == "missing_action":
        denominator = int(raw.get("denominator") or 0)
        score = raw.get("score")
        if denominator <= 0 or not details:
            return {
                "status": "unknown",
                "raw_score": score,
                "denominator": denominator,
                "observable": False,
                "reason": "no_rule_actions",
                "evidence": {"details": details},
            }
        return {
            "status": "violated" if float(score or 0.0) > 0.0 else "satisfied",
            "raw_score": score,
            "denominator": denominator,
            "observable": True,
            "reason": None,
            "evidence": {"details": details},
        }
    if check_type == "incorrect_actor":
        observable = bool(raw.get("observable", raw.get("score") is not None))
        score = raw.get("score")
        if not observable or score is None:
            return {
                "status": "unknown",
                "raw_score": score,
                "denominator": int(raw.get("denominator") or 0),
                "observable": False,
                "reason": raw.get("reason") or "unobservable_actor_relation",
                "evidence": _jsonable({
                    "details": raw.get("details") or [],
                    "unmapped_rule_actors": raw.get("unmapped_rule_actors") or [],
                }),
            }
        return {
            "status": "violated" if float(score) > 0.0 else "satisfied",
            "raw_score": score,
            "denominator": int(raw.get("denominator") or 0),
            "observable": True,
            "reason": None,
            "evidence": _jsonable({
                "details": raw.get("details") or [],
                "process_actor_candidates": raw.get("process_actor_candidates") or [],
                "matched_process_action_ids": raw.get("matched_process_action_ids") or [],
            }),
        }
    if check_type == "out_of_order":
        denominator = int(raw.get("denominator") or 0)
        score = raw.get("score")
        if denominator <= 0 or score is None:
            return {
                "status": "unknown",
                "raw_score": score,
                "denominator": denominator,
                "observable": False,
                "reason": raw.get("reason") or "no_rule_order_endpoints",
                "evidence": {"details": details},
            }
        return {
            "status": "violated" if float(score or 0.0) > 0.0 else "satisfied",
            "raw_score": score,
            "denominator": denominator,
            "observable": True,
            "reason": None,
            "evidence": {"details": details},
        }
    raise ValueError(f"unknown check type: {check_type}")


def violated_types(signals: Mapping[str, Mapping[str, Any]]) -> list[str]:
    return [t for t in TYPES
            if (signals.get(t) or {}).get("status") == "violated"]


class SunStyleChecker:
    """Definition 4 matching followed by Definitions 5-7 on associated rules."""

    def __init__(self, scorer: Any, tau: float):
        self.scorer = scorer
        self.tau = float(tau)

    def check(self, model: Any,
              rule_records: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
        matching: list[dict[str, Any]] = []
        for rule_id, record in sorted(rule_records.items()):
            raw = self.scorer.matching_score(
                list(record.get("actions") or []),
                list(record.get("actors") or []),
                model,
            )
            matching.append({
                "rule_id": str(rule_id),
                "matching_score": float(raw.get("matching_score") or 0.0),
                "action_ratio": float(raw.get("action_ratio") or 0.0),
                "actor_object_ratio": float(raw.get("actor_object_ratio") or 0.0),
                "action_map": _jsonable(raw.get("action_map") or []),
                "actor_object_map": _jsonable(raw.get("actor_object_map") or []),
            })
        matching.sort(key=lambda row: (-row["matching_score"], row["rule_id"]))
        for rank, row in enumerate(matching, start=1):
            row["rank"] = rank
            row["relevant"] = row["matching_score"] > self.tau

        signals_by_rule: dict[str, dict[str, Any]] = {}
        violations: list[dict[str, Any]] = []
        for row in matching:
            if not row["relevant"]:
                continue
            rule_id = row["rule_id"]
            record = rule_records[rule_id]
            if record.get("failed"):
                signals = {
                    t: {
                        "status": "unknown",
                        "raw_score": None,
                        "denominator": 0,
                        "observable": False,
                        "reason": "stage2_rule_record_failed",
                        "evidence": {
                            "failure_reasons": record.get("failure_reasons") or []
                        },
                    }
                    for t in TYPES
                }
            else:
                raw_missing = self.scorer.missing_action(
                    list(record.get("actions") or []), model)
                raw_actor = self.scorer.incorrect_actor(
                    list(record.get("actions") or []),
                    list(record.get("actors") or []),
                    model,
                    list(record.get("actor_action_pairs") or []),
                )
                raw_order = self.scorer.out_of_order(
                    list(record.get("order_relations") or []),
                    list(record.get("actions") or []),
                    model,
                )
                signals = {
                    "missing_action": normalize_sun_signal(
                        "missing_action", raw_missing),
                    "incorrect_actor": normalize_sun_signal(
                        "incorrect_actor", raw_actor),
                    "out_of_order": normalize_sun_signal(
                        "out_of_order", raw_order),
                }
            signals_by_rule[rule_id] = signals
            for check_type in TYPES:
                signal = signals[check_type]
                if signal.get("status") != "violated":
                    continue
                violations.append({
                    "rule_id": rule_id,
                    "violation_type": check_type,
                    "raw_score": signal.get("raw_score"),
                    "denominator": signal.get("denominator"),
                    "observable": bool(signal.get("observable")),
                    "reason": signal.get("reason"),
                })

        return {
            "matching": matching,
            "signals_by_rule": signals_by_rule,
            "violations": violations,
            "violated_types": sorted({v["violation_type"] for v in violations}),
        }


def _winter_mapping_evidence(pair: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for mapping in pair.mapping:
        model_obligation = mapping.get("model_obligation_lemmatized")
        if isinstance(model_obligation, list):
            model_text = " ".join(str(x) for x in model_obligation)
        elif model_obligation is None:
            model_text = ""
        else:
            model_text = str(model_obligation)
        paragraph_obligation = mapping.get("paragraph_obligation")
        paragraph_text = getattr(paragraph_obligation, "lemmatized", "")
        rows.append({
            "paragraph_obligation_lemmatized": str(paragraph_text or ""),
            "model_obligation_lemmatized": model_text,
            "model_resource": mapping.get("model_resource"),
            "similarity": mapping.get("sim_score"),
        })
    return rows


def winter_signals(*, pair: Any, model: Any, paragraph: Any,
                   resource_set: set[str]) -> dict[str, dict[str, Any]]:
    """Convert a native Winter ``WinterPair`` into three-state signals.

    This is the same semantic conversion used by the repaired v2 diagnostic;
    it is duplicated here so the v3 main runner does not depend on the v2
    target-check module.
    """
    n_obligations = len(paragraph.obligations)
    n_model_obligations = sum(
        len(values) for values in (model.obligations or {}).values()
    )
    flow_count = 0 if not paragraph.flows else len(paragraph.flows)
    mapping_evidence = _winter_mapping_evidence(pair)
    costs = {
        "cost_obligation": float(pair.cost_obligation),
        "cost_resource": float(pair.cost_resource),
        "cost_so": float(pair.cost_so),
        "fitness": float(pair.fitness),
    }

    if n_obligations <= 0:
        missing = {
            "status": "unknown",
            "raw_score": None,
            "denominator": 0,
            "observable": False,
            "reason": "no_rule_obligations",
            "evidence": {"obligation_count": 0, "mapping": mapping_evidence},
        }
    else:
        missing = {
            "status": ("violated" if costs["cost_obligation"] > 0.0
                       else "satisfied"),
            "raw_score": costs["cost_obligation"],
            "denominator": n_obligations,
            "observable": True,
            "reason": None,
            "evidence": {
                "obligation_count": n_obligations,
                "model_obligation_count": n_model_obligations,
                "mapping": mapping_evidence,
            },
        }

    if n_obligations <= 0:
        actor = {
            "status": "unknown",
            "raw_score": None,
            "denominator": 0,
            "observable": False,
            "reason": "no_rule_obligations",
            "evidence": {"resource_set": sorted(resource_set), "mapping": []},
        }
    elif not resource_set:
        actor = {
            "status": "unknown",
            "raw_score": None,
            "denominator": 0,
            "observable": False,
            "reason": "no_process_resource_labels",
            "evidence": {"resource_set": [], "mapping": mapping_evidence},
        }
    elif not model.processes:
        actor = {
            "status": "unknown",
            "raw_score": None,
            "denominator": 0,
            "observable": False,
            "reason": "no_process_models",
            "evidence": {"resource_set": sorted(resource_set), "mapping": mapping_evidence},
        }
    else:
        actor = {
            "status": ("violated" if costs["cost_resource"] > 0.0
                       else "satisfied"),
            "raw_score": costs["cost_resource"],
            "denominator": n_obligations,
            "observable": True,
            "reason": None,
            "evidence": {
                "resource_set": sorted(resource_set),
                "mapping": mapping_evidence,
            },
        }

    if flow_count <= 0:
        order = {
            "status": "unknown",
            "raw_score": None,
            "denominator": 0,
            "observable": False,
            "reason": "no_rule_side_flow_relations",
            "evidence": {"flow_count": 0, "mapping": mapping_evidence},
        }
    else:
        order = {
            "status": ("violated" if costs["cost_so"] > 0.0
                       else "satisfied"),
            "raw_score": costs["cost_so"],
            "denominator": flow_count,
            "observable": True,
            "reason": None,
            "evidence": {"flow_count": flow_count, "mapping": mapping_evidence},
        }

    return {
        "missing_action": missing,
        "incorrect_actor": actor,
        "out_of_order": order,
    }


__all__ = [
    "TYPES",
    "SunStyleChecker",
    "normalize_sun_signal",
    "violated_types",
    "winter_signals",
]
