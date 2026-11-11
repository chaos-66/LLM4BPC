# -*- coding: utf-8 -*-
"""Winter et al. (2020) Stage 3 baseline: Pair (fitness / cost) computation.

Transcribed from the read-only Winter prototype
(``references/winter_2020_model_check/model_check/lib/classes/Pair.py``):

- mapping: each paragraph obligation clause -> model obligation with maximal
  spaCy similarity (per model resource);
- fitness = mean of mapping similarities above gamma (0 if none);
- cost_obligation = fraction of clauses whose best mapping similarity is
  below gamma            -> missing-action violations;
- cost_resource = fraction of clauses whose matched task is similar (> gamma)
  but whose mentioned resource is not the model participant (spaCy similarity
  < delta and no exact textual match) -> incorrect-actor violations;
- cost_so = fraction of paragraph flows whose condition matches and whose
  obligation task is reachable from the compared task but not vice versa
  -> out-of-order violations (bug-fixed reachability, see config);
- cost = w_o*cost_obligation + w_r*cost_resource + w_so*cost_so (weights 1/3).

The prototype's resource set is the set of process participants; on the
frozen GDPR7 BPMN the participant attribute is empty, so resource cost is
vacuous there (disclosed limitation, not a threshold added by us).
"""

from __future__ import annotations

import re
from typing import Any


class WinterPair:
    def __init__(self, nlp, sim: Any, model: Any, paragraph: Any,
                 resource_set: set[str], gamma: float, delta: float):
        self.nlp = nlp
        self.sim = sim
        self.model = model
        self.paragraph = paragraph
        self.resource_set = resource_set
        self.gamma = gamma
        self.delta = delta
        self.mapping = self.calculate_mapping()
        self.fitness = self.fitness_score()
        self.cost_obligation = self.cost_obligation_score(gamma)
        self.cost_resource = self.cost_resource_score(gamma, delta)
        self.cost_so = self.cost_so_score(gamma)
        self.cost = self.cost_score(1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)

    # ------------------------------------------------------------------ mapping
    def calculate_mapping(self) -> list[dict[str, Any]]:
        model_obligations = self.model.obligations
        model_obligations_lemmatized = self.model.lemmatized_obligations
        mapping = []
        for para_obligation in self.paragraph.obligations:
            max_element, max_lemmatized, resource, score, proc = (
                self._max_text_obligation_to_model(
                    para_obligation, model_obligations, model_obligations_lemmatized
                )
            )
            mapping.append({
                "paragraph_obligation": para_obligation,
                "paragraph_obligation_lemmatized": para_obligation.lemmatized,
                "model_obligation": max_element,
                "model_obligation_lemmatized": max_lemmatized,
                "model_resource": resource,
                "sim_score": score,
                "process": proc,
            })
        return mapping

    def _max_text_obligation_to_model(self, text_obligation, model_obligations,
                                      model_obligations_lemmatized):
        max_score = 0.0
        max_element = None
        max_element_lemmatized = None
        resource = None
        proc = None
        for key in model_obligations_lemmatized:
            resource_obligations = model_obligations_lemmatized[key]
            for idx, model_obligation in enumerate(resource_obligations):
                if max_element is None:
                    max_element = model_obligations[key][idx]
                    max_element_lemmatized = model_obligation
                    proc = model_obligations[key]
                    resource = key
                sim_score = self.sim.text_model_obligation(
                    text_obligation.lemmatized, model_obligation
                )
                if sim_score > max_score:
                    max_score = sim_score
                    max_element = model_obligations[key][idx]
                    max_element_lemmatized = model_obligation
                    proc = model_obligations[key]
                    resource = key
        return (max_element, max_element_lemmatized, resource, max_score, proc)

    # ------------------------------------------------------------------ fitness
    def fitness_score(self) -> float:
        sum_scores = 0.0
        sum_all = 0
        for mapping in self.mapping:
            if mapping["sim_score"] > self.gamma:
                sum_scores += mapping["sim_score"]
                sum_all += 1
        if sum_all == 0:
            return 0.0
        return float(sum_scores) / sum_all

    # ------------------------------------------------------------------- costs
    def cost_score(self, w_obligation: float, w_resource: float, w_so: float) -> float:
        return (w_obligation * self.cost_obligation
                + w_resource * self.cost_resource
                + w_so * self.cost_so)

    def cost_obligation_score(self, gamma: float) -> float:
        count_violations = 0
        count_all = 0
        for mapping in self.mapping:
            count_all += 1
            if mapping["sim_score"] < gamma:
                count_violations += 1
        if count_all == 0:
            return 0.0
        return float(count_violations) / count_all

    def cost_resource_score(self, gamma: float, gamma_resource: float) -> float:
        if not self.resource_set:
            return 0.0
        count_violations = 0
        count_all = 0
        for mapping in self.mapping:
            count_all += 1
            if self.check_resource_violation(mapping, gamma, gamma_resource):
                count_violations += 1
        if count_all == 0:
            return 0.0
        return float(count_violations) / count_all

    def check_resource_violation(self, mapping, gamma: float, gamma_resource: float) -> bool:
        task_sim = self.sim.task_clause(mapping["model_obligation_lemmatized"],
                                        mapping["paragraph_obligation"])
        if task_sim > gamma:
            for a in self.resource_set:
                if (a.lower() in mapping["paragraph_obligation_lemmatized"]
                        and self.nlp(a.lower()).similarity(
                            self.nlp(mapping["model_resource"].lower())
                        ) < gamma_resource
                        and mapping["model_resource"].lower()
                        not in mapping["paragraph_obligation_lemmatized"]):
                    return True
        return False

    def cost_so_score(self, gamma: float) -> float:
        paragraph_flows = self.paragraph.flows
        if paragraph_flows is None:
            return 0.0
        count_violations = 0
        count_all = 0
        for para_flow in paragraph_flows:
            count_all += 1
            for m in self.mapping:
                if para_flow._id == m["paragraph_obligation"]._id:
                    process_object = None
                    for x in self.model.processes:
                        if x.participant == m["model_resource"]:
                            process_object = x
                    if process_object is not None and self.check_flow_violation(
                            para_flow, m, process_object, gamma):
                        count_violations += 1
        if count_all == 0:
            return 0.0
        return float(count_violations) / count_all

    def check_flow_violation(self, para_flow, mapping, process_object, gamma: float) -> bool:
        condition_sim = self.sim.text_pair(
            para_flow.lemmatize_condition(),
            " ".join(mapping["model_obligation_lemmatized"]),
        )
        if condition_sim > gamma:
            regexp = re.compile(r".+")
            obligation_id = mapping["model_obligation"].getAttribute("id")
            for compare in mapping["process"]:
                c = compare.getAttribute("name")
                if not regexp.search(c):
                    continue
                compare_id = compare.getAttribute("id")
                if (self.sim.text_pair(
                        c, para_flow.lemmatize_consequence()) > gamma
                        and c != " ".join(mapping["model_obligation_lemmatized"])
                        and process_object.is_reachable_from(obligation_id, compare_id)
                        and not process_object.is_reachable_from(compare_id, obligation_id)):
                    return True
            return False
        return True
