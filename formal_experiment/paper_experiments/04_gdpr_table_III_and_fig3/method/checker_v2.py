# -*- coding: utf-8 -*-
"""Shared Stage-3-v2 checker wrapper around the frozen Sun Definitions 5-7.

The wrapper changes only the semantic-similarity implementation and the
order-relation adapter.  It does not alter Definition 5, 6, or 7 formulas.
"""

from __future__ import annotations

from typing import Any, Mapping

from bpc_hybrid.stage3_sun_style_checker import normalize_sun_signal
from bpc_hybrid.sun_stage3.sun_scorer import SunScorer

TYPES = ("missing_action", "incorrect_actor", "out_of_order")
SCHEMA_VERSION = "stage3_v2_checker@1.0.0"


class SharedStage3CheckerV2:
    """One checker instance used for both Sun and Ours."""

    def __init__(self, matcher: Any, nlp: Any, *, tau: float, gamma: float, theta: float):
        self.matcher = matcher
        self.nlp = nlp
        self.tau = float(tau)
        self.gamma = float(gamma)
        self.theta = float(theta)
        # One SunScorer implementation is shared; only its ``sim`` differs from
        # the frozen v1 run.  The shared nlp is also used for lemmatisation.
        self.scorer = SunScorer(self.matcher, self.tau, self.gamma, self.theta, nlp=self.nlp)

    def set_thresholds(self, *, gamma: float, theta: float) -> None:
        """Update thresholds in place so the lemma/similarity caches persist."""
        self.gamma = float(gamma)
        self.theta = float(theta)
        self.scorer.gamma = float(gamma)
        self.scorer.theta = float(theta)

    def check_rule_record(self, record: Mapping[str, Any], model: Any) -> dict[str, Any]:
        actions = list(record.get("actions") or [])
        actors = list(record.get("actors") or [])
        pairs = list(record.get("actor_action_pairs") or [])
        order_relations = list(record.get("order_relations") or [])
        raw_missing = self.scorer.missing_action(actions, model)
        raw_actor = self.scorer.incorrect_actor(actions, actors, model, pairs)
        raw_order = self.scorer.out_of_order(order_relations, actions, model)
        return {
            "schema_version": SCHEMA_VERSION,
            "tau": self.tau,
            "gamma": self.gamma,
            "theta": self.theta,
            "missing_action": normalize_sun_signal("missing_action", raw_missing),
            "incorrect_actor": normalize_sun_signal("incorrect_actor", raw_actor),
            "out_of_order": normalize_sun_signal("out_of_order", raw_order),
            "raw": {
                "missing_action": raw_missing,
                "incorrect_actor": raw_actor,
                "out_of_order": raw_order,
            },
        }

    def check_rule_records(self, records_by_rule: Mapping[str, Mapping[str, Any]], model: Any
                           ) -> dict[str, Any]:
        return {
            str(rule_id): self.check_rule_record(record, model)
            for rule_id, record in sorted(records_by_rule.items(), key=lambda item: str(item[0]))
        }


__all__ = [
    "SCHEMA_VERSION",
    "TYPES",
    "SharedStage3CheckerV2",
]
