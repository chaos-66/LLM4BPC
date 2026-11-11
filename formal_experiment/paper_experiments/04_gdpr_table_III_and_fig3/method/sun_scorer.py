# -*- coding: utf-8 -*-
"""Sun et al. (2024) Stage 3: matching score and the three violation scores
(paper section 4.3 Definitions 4-7). Method-level independent reconstruction;
thresholds (tau/gamma/theta) live in the versioned config, never tuned on
this project's Gold.
"""

from __future__ import annotations

from typing import Any

from bpc_hybrid.role_surface import normalize_role_surface


class SunScorer:
    def __init__(self, sim, tau: float, gamma: float, theta: float, nlp=None):
        self.sim = sim
        self.tau = tau
        self.gamma = gamma
        self.theta = theta
        self.nlp = nlp
        self._lemma_cache: dict[str, str] = {}

    def _lemma(self, text: str) -> str:
        """Lemmatized text for similarity comparisons, aligned with the
        Winter baseline (same spaCy backend, controlled comparison)."""
        if self.nlp is None:
            return text
        cached = self._lemma_cache.get(text)
        if cached is None:
            cached = " ".join(
                w.lemma_ if w.lemma_ != "-PRON-" else w.text
                for w in self.nlp(text)
                if not w.is_punct and not w.is_space
            )
            self._lemma_cache[text] = cached
        return cached

    # ------------------------------------------------------------- Definition 4
    def matching_score(self, rule_actions: list[str], rule_actors: list[str],
                       model: Any) -> dict[str, Any]:
        """matching(r,m,tau) = max( fraction of Dr,m with sim>tau,
        fraction of Or,m with sim>tau )."""
        d_count = len(rule_actions)
        o_count = len(rule_actors)
        d_over = 0
        d_best: list[tuple[str, str, float]] = []
        for ra in rule_actions:
            best, best_score = self._best_action_match(ra, model)
            d_best.append((ra, best, best_score))
            if best is not None and best_score > self.tau:
                d_over += 1
        o_over = 0
        o_best: list[tuple[str, str, float, str]] = []
        for ra in rule_actors:
            best, best_score, kind = self._best_actor_match(ra, model)
            o_best.append((ra, best, best_score, kind))
            if best is not None and best_score > self.tau:
                o_over += 1
        d_ratio = (d_over / d_count) if d_count else 0.0
        o_ratio = (o_over / o_count) if o_count else 0.0
        score = max(d_ratio, o_ratio) if (d_count or o_count) else 0.0
        return {
            "matching_score": score,
            "action_ratio": d_ratio,
            "actor_object_ratio": o_ratio,
            "action_map": d_best,
            "actor_object_map": o_best,
        }

    def _best_action_match(self, rule_action: str, model: Any):
        best_score = 0.0
        best_name = None
        rule_lemma = self._lemma(rule_action)
        for act in model.actions:
            if not act["name"]:
                continue
            score = self.sim.text_pair(rule_lemma, self._lemma(act["name"]))
            if score > best_score:
                best_score = score
                best_name = act["name"]
        return best_name, best_score

    def _best_actor_match(self, rule_actor: str, model: Any):
        best_score = 0.0
        best_name = None
        best_kind = None
        rule_lemma = self._lemma(rule_actor)
        rule_surface = normalize_role_surface(rule_actor)
        # Approved shared surface normalization is checked first for BOTH
        # methods.  It is exact after casefold/whitespace/leading-article
        # stripping only; controller and processor remain distinct.
        for actor in model.actors:
            if normalize_role_surface(actor) == rule_surface:
                return actor, 1.0, model.actor_sources.get(actor, "actor")
        for bo in model.business_objects:
            if normalize_role_surface(bo["object"]) == rule_surface:
                return bo["object"], 1.0, "business_object"
        # actors first (pool/lane names), then business objects
        for actor in model.actors:
            score = self.sim.text_pair(rule_lemma, self._lemma(actor))
            if score > best_score:
                best_score = score
                best_name = actor
                best_kind = model.actor_sources.get(actor, "actor")
        for bo in model.business_objects:
            score = self.sim.text_pair(rule_lemma, self._lemma(bo["object"]))
            if score > best_score:
                best_score = score
                best_name = bo["object"]
                best_kind = "business_object"
        return best_name, best_score, best_kind

    # ------------------------------------------------------------ Definition 5
    def missing_action(self, rule_actions: list[str], model: Any) -> dict[str, Any]:
        """action violation = |{(ar,am) in Dr,m | sim(ar,am)<gamma}| / |Ar|"""
        denominator = len(rule_actions)
        missing = 0
        details = []
        for ra in rule_actions:
            best, best_score = self._best_action_match(ra, model)
            is_missing = best is None or best_score < self.gamma
            if is_missing:
                missing += 1
            details.append({
                "rule_action": ra,
                "best_model_action": best,
                "similarity": round(best_score, 4),
                "missing": is_missing,
            })
        score = (missing / denominator) if denominator else 0.0
        return {
            "score": score,
            "missing": missing,
            "denominator": denominator,
            "details": details,
        }

    # ------------------------------------------------------------ Definition 6
    def incorrect_actor(self, rule_actions: list[str], rule_actors: list[str],
                        model: Any, actor_action_pairs=None) -> dict[str, Any]:
        """Definition 6: keep the paper's existential/min comparison.

        R uses f_r (explicit actor-action pairs); C uses f_m (process
        ownership and activity-bound business objects). No process-wide
        fallback is permitted. A single actor and action are unambiguous;
        multi-action records must provide their actual associations.
        """
        def unavailable(reason, denominator=0):
            return {"score": None, "denominator": denominator,
                    "observable": False, "reason": reason, "details": [],
                    "actor_scope_policy": "sun_def6_action_bound_v2"}

        if not rule_actors:
            return unavailable("empty_rule_actor_denominator")
        if not model.actors and not model.business_objects:
            return unavailable("no_actor_labels")
        pairs = actor_action_pairs
        if pairs is None and len(rule_actors) == len(rule_actions) == 1:
            pairs = [{"actor": rule_actors[0], "action": rule_actions[0]}]
        if not pairs:
            return unavailable("missing_rule_actor_action_map")
        valid = [p for p in pairs if p.get("actor") in rule_actors
                 and p.get("action") in rule_actions]
        unmapped = sorted(set(rule_actors) - {p["actor"] for p in valid})
        if unmapped:
            result = unavailable("incomplete_rule_actor_action_map")
            result["unmapped_rule_actors"] = unmapped
            return result
        r_set = []
        matched_rule_actions = []
        for pair in valid:
            _, score = self._best_action_match(pair["action"], model)
            if score > self.gamma:
                r_set.append(pair["actor"])
                matched_rule_actions.append(pair["action"])
        r_set = list(dict.fromkeys(r_set))
        if not r_set:
            return unavailable("action_mapping_below_gamma")
        # C is the union specified by Sun, filtered by the corresponding
        # actions; do not replace the existential quantifier with max(sim).
        c_set = []
        matched_ids = []
        for action in model.actions:
            if not action.get("name"):
                continue
            if any(self.sim.text_pair(self._lemma(ra), self._lemma(action["name"]))
                   > self.gamma for ra in matched_rule_actions):
                matched_ids.append(action["id"])
                c_set.extend(model.action_actor_names.get(action["id"], []))
                c_set.extend(bo["object"] for bo in model.business_objects
                             if bo["activity_id"] == action["id"])
        c_set = list(dict.fromkeys(c_set))
        if not c_set:
            return unavailable("no_matching_process_actor", len(r_set))
        details = []
        for actor in r_set:
            actor_surface = normalize_role_surface(actor)
            minimum = min(
                1.0 if normalize_role_surface(c) == actor_surface
                else self.sim.text_pair(self._lemma(actor), self._lemma(c))
                for c in c_set
            )
            details.append({"rule_actor": actor,
                            "min_process_actor_similarity": round(minimum, 4),
                            "exists_low_similarity": minimum < self.theta,
                            "violated": minimum < self.theta})
        violations = sum(d["violated"] for d in details)
        return {"score": violations / len(r_set), "violations": violations,
                "denominator": len(r_set), "observable": True, "reason": None,
                "details": details, "process_actor_candidates": c_set,
                "matched_process_action_ids": matched_ids,
                "actor_scope_policy": "sun_def6_action_bound_v2"}

    # ------------------------------------------------------------ Definition 7
    def out_of_order(self, rule_order_relations: list[tuple[str, str]],
                     rule_actions: list[str], model: Any) -> dict[str, Any]:
        """order violation = (|Ur,m,gamma| - satisfied) / |Ur,m,gamma| with
        Ur,m,gamma = order constraints whose both endpoints map with sim>gamma,
        satisfied = forward reachable and not backward reachable."""
        denominator = 0
        satisfied = 0
        details = []
        for before_text, after_text in rule_order_relations:
            before_map = self._best_action_match(before_text, model)
            after_map = self._best_action_match(after_text, model)
            before_name, before_score = before_map
            after_name, after_score = after_map
            if before_name is None or after_name is None:
                details.append({
                    "constraint": (before_text, after_text),
                    "mapped": False,
                    "reason": "endpoint without a process action match",
                })
                continue
            if before_score <= self.gamma or after_score <= self.gamma:
                details.append({
                    "constraint": (before_text, after_text),
                    "mapped": False,
                    "reason": "endpoint similarity below gamma",
                })
                continue
            denominator += 1
            before_id = self._action_id_by_name(model, before_name)
            after_id = self._action_id_by_name(model, after_name)
            forward = model.is_reachable(before_id, after_id) if before_id and after_id else False
            backward = model.is_reachable(after_id, before_id) if before_id and after_id else False
            ok = forward and not backward
            if ok:
                satisfied += 1
            details.append({
                "constraint": (before_text, after_text),
                "mapped": True,
                "before_activity": before_name,
                "after_activity": after_name,
                "forward_reachable": forward,
                "backward_reachable": backward,
                "satisfied": ok,
            })
        score = ((denominator - satisfied) / denominator) if denominator else 0.0
        return {
            "score": score,
            "denominator": denominator,
            "satisfied": satisfied,
            "violations": denominator - satisfied,
            "details": details,
        }

    def _action_id_by_name(self, model: Any, name: str) -> str | None:
        for act in model.actions:
            if act["name"] == name:
                return act["id"]
        return None
