# -*- coding: utf-8 -*-
"""Sun et al. (2024) Stage 3: Gold-blind development Rule Record adapter.

Extracts a minimal Sun-compatible Rule Record (actions, actors, order
relations) from the frozen ``rule_text`` of the S3.2/S3.3 blank pack using
deterministic spaCy dependency parsing plus the shared external signalword
lexicon. It is a **development adapter**: the full Stage 2 Rules-Only method
(BERT-TextCNN + CoreNLP/Tregex/Tsurgeon + public marker lexicon) is not run
here (external CoreNLP runtime unavailable), so this adapter's output must
never be presented as formal B0 output.

Forbidden inputs (never read): decision_relevant, decision_violation_type,
candidate_relevant, candidate_violation_type, candidate_evidence,
candidate_location.
"""

from __future__ import annotations

import re
from typing import Any

SIGNALWORDS = {"shall", "must", "should", "may"}
SEQUENCE_MARKERS = {"after", "then", "afterward", "afterwards", "subsequently",
                    "based on this", "thus"}


def _obligation_sentences(doc) -> list[Any]:
    result = []
    for sent in doc.sents:
        words = [w.text.lower() for w in sent]
        if any(w in SIGNALWORDS for w in words):
            result.append(sent)
    return result


def _extract_actor(sent) -> str | None:
    for token in sent:
        if token.dep_ in ("nsubj", "nsubjpass", "agent", "expl") and token.pos_ != "PRON":
            parts = [t.text for t in token.subtree]
            text = " ".join(parts).strip()
            if text:
                return text
    return None


def _extract_action(sent) -> str | None:
    """Action = root verb plus its core object/complement subtrees
    (dobj/pobj/attr/oprd/acomp/xcomp). This mirrors the Sun rule-record
    action concept (the verb phrase that must be executed) without taking
    the whole sentence subtree, which would dilute similarity."""
    root = None
    for token in sent:
        if token.dep_ == "ROOT":
            root = token
            break
    if root is None:
        return None
    parts = [root.text]
    for child in root.children:
        if child.dep_ in ("dobj", "pobj", "attr", "oprd", "acomp", "xcomp", "advmod"):
            parts.extend(t.text for t in child.subtree)
    text = " ".join(parts).strip()
    return text or None


def _extract_order_relations(sentences: list[Any]) -> list[tuple[str, str]]:
    """Order relations from sequence markers within a sentence and across
    adjacent obligation sentences (the rule text's sequential constraints)."""
    relations: list[tuple[str, str]] = []
    texts = [" ".join(t.text for t in s) for s in sentences]
    for idx, sent in enumerate(sentences):
        lower = sent.text.lower()
        for marker in sorted(SEQUENCE_MARKERS, key=len, reverse=True):
            if marker in lower:
                # intra-sentence: parts split by the marker
                parts = re.split(rf"\b{re.escape(marker)}\b", sent.text, flags=re.IGNORECASE)
                if len(parts) >= 2 and texts[idx]:
                    relations.append((parts[0].strip(), parts[1].strip()))
                break
    # cross-sentence adjacency: sentence i's action precedes sentence i+1's
    for i in range(len(texts) - 1):
        if texts[i] and texts[i + 1]:
            relations.append((texts[i], texts[i + 1]))
    return relations


def extract_rule_record(rule_id: str, rule_text: str, nlp,
                        signalwords: set[str] | None = None) -> dict[str, Any]:
    """Gold-blind Rule Record extraction from rule text. Returns a dict with
    actions/actors/order_relations and provenance; reads no Gold fields."""
    sig = signalwords or SIGNALWORDS
    doc = nlp(rule_text)
    sentences = []
    for sent in doc.sents:
        words = [w.text.lower() for w in sent]
        if any(w in sig for w in words):
            sentences.append(sent)
    actions = []
    actors = []
    actor_action_pairs = []
    for sent in sentences:
        action = _extract_action(sent)
        actor = _extract_actor(sent)
        if action:
            actions.append(action)
        if actor:
            actors.append(actor)
        if actor and action:
            actor_action_pairs.append({"actor": actor, "action": action})
    order_relations = _extract_order_relations(sentences)
    return {
        "rule_id": rule_id,
        "schema_version": "sun_rule_record_development@1.0.0",
        "modality": "obligation" if actions else None,
        "actions": actions,
        "actors": actors,
        "actor_action_pairs": actor_action_pairs,
        "order_relations": order_relations,
        "provenance": {
            "adapter": "development Sun Rule Record adapter (spaCy dependency parsing + signalword lexicon)",
            "differences_from_full_stage2_rules_only": [
                "full Stage 2 Rules-Only (BERT-TextCNN + CoreNLP/Tregex/Tsurgeon + public marker lexicon) not run: external CoreNLP runtime unavailable",
                "no B0 predictions used; output is development-only and must not be presented as formal B0",
            ],
            "gold_fields_read": False,
        },
    }
