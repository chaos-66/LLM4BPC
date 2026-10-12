# -*- coding: utf-8 -*-
"""Sun et al. (2024) Stage 3: process-model view built from the canonical
Process Record (Definition 4's ``action(Am union Em)``, business objects
``bs_obj(Am union Em)``, actors, and control-flow reachability ``Fm``).

The canonical Process Record comes from ``src/bpc_hybrid/stage1_process.py``
(parser contract ``configs/stage1_structural_s11_s14.json``). The frozen
GDPR7 files carry empty lane names but non-empty pool names; actor elements
are pool names plus any non-empty lane names. Business objects are extracted
deterministically from activity labels via spaCy dependency parsing (dobj /
pobj of the root verb); labels without an extractable object contribute no
business object (recorded, never invented).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bpc_hybrid.stage1_process import load_stage1_contract, parse_bpmn_file


class SunProcessModel:
    def __init__(self, process_id: str, record: dict[str, Any], nlp):
        self.process_id = process_id
        self.record = record
        self.nlp = nlp
        self.actions: list[dict[str, str]] = []
        for act in record.get("activities", []):
            self.actions.append({"id": act["id"], "name": act["name"], "kind": "activity"})
        for ev in record.get("events", []):
            self.actions.append({"id": ev["id"], "name": ev.get("name", ""), "kind": "event"})
        # actors: pool names + non-empty lane names
        self.actors: list[str] = []
        for pool in record.get("pools", []):
            name = (pool.get("name") or "").strip()
            if name:
                self.actors.append(name)
        for lane in record.get("lanes", []):
            name = (lane.get("name") or "").strip()
            if name:
                self.actors.append(name)
        self.actor_sources: dict[str, str] = {}
        for pool in record.get("pools", []):
            name = (pool.get("name") or "").strip()
            if name:
                self.actor_sources[name] = "pool"
        for lane in record.get("lanes", []):
            name = (lane.get("name") or "").strip()
            if name:
                self.actor_sources[name] = "lane"
        # Definition 6 needs f_m: retain ownership, not just a bag of names.
        # A pool belongs to its process; a lane belongs only to its flow nodes.
        self.action_actor_names: dict[str, list[str]] = {}
        for action in self.actions:
            owners = [p["name"].strip() for p in record.get("pools", [])
                      if (p.get("name") or "").strip()
                      and p.get("process_ref") == record.get("process_id")]
            owners += [lane["name"].strip() for lane in record.get("lanes", [])
                       if (lane.get("name") or "").strip()
                       and action["id"] in lane.get("flow_node_refs", [])]
            self.action_actor_names[action["id"]] = list(dict.fromkeys(owners))
        # business objects from activity labels (dobj/pobj of root verb)
        self.business_objects: list[dict[str, str]] = []
        for act in record.get("activities", []):
            name = act["name"]
            obj = _extract_business_object(name, nlp)
            if obj:
                self.business_objects.append({"activity_id": act["id"], "object": obj})
        # reachability Fm from control_flow.reachable_pairs
        self.reachable: dict[str, set[str]] = {}
        for pair in record.get("control_flow", {}).get("reachable_pairs", []):
            src = pair["source_ref"]
            tgt = pair["target_ref"]
            self.reachable.setdefault(src, set()).add(tgt)
        # activity id -> name lookup for evidence
        self.id_to_name = {a["id"]: a["name"] for a in self.actions}

    def is_reachable(self, source_id: str, target_id: str) -> bool:
        return target_id in self.reachable.get(source_id, set())


def _extract_business_object(label: str, nlp) -> str | None:
    """Deterministic dobj/pobj extraction from an activity label; None when
    the label has no extractable object (recorded, never invented)."""
    doc = nlp(label)
    root = None
    for token in doc:
        if token.dep_ == "ROOT":
            root = token
            break
    if root is None:
        return None
    for token in root.subtree:
        if token.dep_ in ("dobj", "pobj", "attr", "oprd"):
            parts = [t.text for t in token.subtree]
            text = " ".join(parts).strip()
            if text:
                return text
    return None


def build_sun_models(bpmn_dir: Path, structural_contract: Path, nlp) -> dict[str, SunProcessModel]:
    contract = load_stage1_contract(structural_contract)
    models: dict[str, SunProcessModel] = {}
    for bpmn in sorted(bpmn_dir.glob("*.bpmn")):
        record = parse_bpmn_file(bpmn, contract=contract)
        models[bpmn.stem] = SunProcessModel(bpmn.stem, record, nlp)
    return models
