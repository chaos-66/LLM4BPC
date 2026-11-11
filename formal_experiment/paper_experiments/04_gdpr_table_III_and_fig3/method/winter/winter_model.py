# -*- coding: utf-8 -*-
"""Winter et al. (2020) Stage 3 baseline: BPMN model parsing.

Method transcribed from the read-only Winter prototype
(``references/winter_2020_model_check/model_check/lib/classes/Process.py``
and ``main.py``): a process model's obligation list is the set of start
events, end events, tasks and intermediate events of a BPMN ``process``
element; labels are lemmatized with spaCy minus stopwords; control flow is
the sequence-flow transitive closure.

One documented deviation: the prototype's ``is_reachable_from`` returns
``targetid in reachability[targetid]`` (always True, deterministic bug that
makes out-of-order detection vacuous); this re-implementation returns
``targetid in reachability[sourceid]``. See config ``known_prototype_deviation``.

No code from ``references/`` is imported; this is an independent transcription.
"""

from __future__ import annotations

import re
import xml.dom.minidom as minidom
from typing import Any

GATEWAYS = [
    "parallelGateway", "exclusiveGateway", "complexGateway",
    "eventBasedGateway", "inclusiveGateway",
]
EVENTS = ["intermediateCatchEvent", "intermediateThrowEvent", "boundaryEvent"]


REACHABILITY_CORRECTED = "corrected_reachability"
REACHABILITY_PROTOTYPE_LITERAL = "prototype_literal"
REACHABILITY_MODES = (REACHABILITY_CORRECTED, REACHABILITY_PROTOTYPE_LITERAL)


class WinterModel:
    """One BPMN file as the Winter prototype sees it (all ``process``
    elements flattened per file, mirroring ``BPMN(f, processes)``)."""

    def __init__(self, model_id: str, processes: list["WinterProcess"]):
        self._id = model_id
        self.processes = processes
        self.obligations: dict[str, list[Any]] = {}
        self.lemmatized_obligations: dict[str, list[list[str]]] = {}
        for proc in processes:
            key = proc.participant
            self.obligations.setdefault(key, []).extend(proc.obligation_list)
            self.lemmatized_obligations.setdefault(key, []).extend(
                proc.obligation_list_labels_lemmatized
            )


class WinterProcess:
    """One ``<process>`` element: obligation elements, labels, lemmatized
    labels, directly-follows relation and reachability."""

    def __init__(
        self,
        process_id: str,
        participant: str,
        start_events: list[Any],
        end_events: list[Any],
        tasks: list[Any],
        gateways: dict[str, list[Any]],
        events: dict[str, list[Any]],
        flows: list[Any],
        nlp,
        stopwords: set[str],
        reachability_mode: str = REACHABILITY_CORRECTED,
    ):
        if reachability_mode not in REACHABILITY_MODES:
            raise ValueError(f"unknown reachability mode: {reachability_mode}")
        self._id = process_id
        self.participant = participant
        self.start_events = start_events
        self.end_events = end_events
        self.tasks = tasks
        self.gateways = gateways
        self.events = events
        self.flows = flows
        self.nlp = nlp
        self.stopwords = stopwords
        self.reachability_mode = reachability_mode

        self.start_event_labels = _labels(start_events)
        self.end_event_labels = _labels(end_events)
        self.task_labels = _labels(tasks)
        self.event_labels: dict[str, list[str]] = {
            k: _labels(v) for k, v in events.items()
        }
        self.gateway_labels: dict[str, list[str]] = {
            k: _labels(v) for k, v in gateways.items()
        }

        self.directly_follows = _compute_directly_follows(flows)
        self.reachability = _compute_reachability(self.directly_follows)
        self.obligation_list = (
            list(start_events) + list(end_events) + list(tasks)
        )
        for ev in events.values():
            self.obligation_list.extend(ev)
        self.obligation_list_labels = (
            self.start_event_labels + self.end_event_labels + self.task_labels
        )
        for ev_labels in self.event_labels.values():
            self.obligation_list_labels.extend(ev_labels)
        self.obligation_list_labels_lemmatized = [
            _lemmatize_label(label, nlp, stopwords)
            for label in self.obligation_list_labels
        ]

    def is_reachable_from(self, sourceid: str, targetid: str) -> bool:
        """Two explicit modes:

        - ``corrected_reachability``: is ``targetid`` reachable from
          ``sourceid`` in the sequence-flow transitive closure (fixes the
          prototype's deterministic always-True bug);
        - ``prototype_literal``: replicates the Winter prototype's exact
          expression ``targetid in reachability[targetid]`` (always True),
          kept as a zero-cost sensitivity mode so the bug's effect on the
          out-of-order baseline is measurable.
        """
        if self.reachability_mode == REACHABILITY_PROTOTYPE_LITERAL:
            return targetid in self.reachability.get(targetid, set())
        return targetid in self.reachability.get(sourceid, set())


def _labels(elements: list[Any]) -> list[str]:
    result = []
    for element in elements:
        label = element.getAttribute("name")
        if re.search(r".+", label):
            result.append(label)
    return result


def _lemmatize_label(label: str, nlp, stopwords: set[str]) -> list[str]:
    result = []
    words = nlp(label)
    for w in words:
        if w.lemma_ == "-PRON-":
            result.append(w.text)
        else:
            if w.is_punct or w.like_num or w.is_space or w.text in stopwords:
                continue
            result.append(w.lemma_)
    return result


def _compute_directly_follows(flows: list[Any]) -> dict[str, list[str]]:
    directly_follows: dict[str, list[str]] = {}
    for flow in flows:
        sourceid = flow.getAttribute("sourceRef")
        targetid = flow.getAttribute("targetRef")
        directly_follows.setdefault(sourceid, []).append(targetid)
    return directly_follows


def _compute_reachability(directly_follows: dict[str, list[str]]) -> dict[str, set[str]]:
    nodes: set[str] = set()
    for key, targets in directly_follows.items():
        nodes.add(key)
        nodes.update(targets)
    reachability: dict[str, set[str]] = {}
    for node in nodes:
        stack = [node]
        reachable: set[str] = {node}
        while stack:
            current = stack.pop()
            for follower in directly_follows.get(current, []):
                if follower not in reachable:
                    reachable.add(follower)
                    stack.append(follower)
        reachability[node] = reachable
    return reachability


def parse_bpmn_file_winter(path, nlp, stopwords: set[str],
                           reachability_mode: str = REACHABILITY_CORRECTED) -> WinterModel:
    """Parse one BPMN file the Winter way (``minidom``; every ``process``
    element becomes a WinterProcess; gateway/event tags as in the prototype)."""
    doc = minidom.parse(str(path))
    processes_dom = doc.getElementsByTagName("process")
    processes = []
    for p in processes_dom:
        _id = p.getAttribute("id")
        participant = p.getAttribute("name")
        start_events = p.getElementsByTagName("startEvent")
        end_events = p.getElementsByTagName("endEvent")
        tasks = p.getElementsByTagName("task")
        flows = p.getElementsByTagName("sequenceFlow")
        gateways = {g: p.getElementsByTagName(g) for g in GATEWAYS}
        events = {e: p.getElementsByTagName(e) for e in EVENTS}
        processes.append(
            WinterProcess(
                _id, participant, start_events, end_events, tasks,
                gateways, events, flows, nlp, stopwords,
                reachability_mode=reachability_mode,
            )
        )
    return WinterModel(path.stem, processes)
