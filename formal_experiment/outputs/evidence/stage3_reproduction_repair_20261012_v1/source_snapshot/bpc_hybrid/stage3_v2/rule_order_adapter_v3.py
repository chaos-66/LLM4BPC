# -*- coding: utf-8 -*-
"""Shared, Gold-blind RuleRecord U_r adapter v3.

This module is a documented project adaptation for Sun Definition 7.  Sun
requires a rule order relation ``U_r subset A_r x A_r`` but the public paper
does not prescribe an automatic extraction algorithm.  The adapter below is
shared by Sun and Ours.  It consumes only source regulation text, the method's
already-extracted Stage-2 actions, general syntactic information, and the
shared semantic matcher.  It never reads Gold, reference labels, mutation
metadata, target BPMN nodes, expected order pairs, or method predictions.

The adapter is deliberately conservative:

* native Stage-2 order relations always win;
* only existing Stage-2 action spans can become endpoints;
* every endpoint must have a syntactic predicate link to the temporal clause;
* a nominal phrase is never promoted to a new action;
* the best endpoint pair must be unambiguously better than the alternative;
* if no unique pair exists, no relation is emitted.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import OrderedDict
from typing import Any, Mapping, Sequence

from .action_order_projection_v2 import (
    EXTENDED_ORDER_TYPE,
    MAIN_ORDER_TYPE,
    NATIVE_PRECEDENCE,
    Stage2ActionElement,
    UNSUPPORTED_ORDER_TYPE,
    normalize_native_order_relations,
)

SCHEMA_VERSION = "stage3_v2_rule_order_adapter@3.0.0"

# Marker name, relation orientation for inline clauses, regex.
# ``left_before_right`` means the action on the left of the marker precedes
# the action on the right.  Fronted clauses are handled separately below.
MARKER_SPECS: tuple[tuple[str, str, str], ...] = (
    ("prior to", "left_before_right", r"\bprior\s+to\b"),
    ("in advance of", "left_before_right", r"\bin\s+advance\s+of\b"),
    ("before", "left_before_right", r"\bbefore\b"),
    ("preceding", "left_before_right", r"\bpreceding\b"),
    ("after", "right_before_left", r"\bafter\b"),
    ("following", "right_before_left", r"\bfollowing\b"),
    ("subsequent to", "right_before_left", r"\bsubsequent\s+to\b"),
)

_STOP_LEMMAS = {
    "be", "have", "do", "the", "a", "an", "of", "to", "and", "or", "that",
    "this", "with", "for", "by", "on", "in", "as", "it", "its", "their",
    "shall", "may", "only", "other", "further", "any", "all", "from", "at",
    "where", "which", "who", "when", "if", "than", "such", "not", "no", "is",
    "are", "was", "were", "will", "would", "can", "could", "should", "must",
    "pursuant", "article",
}

_FIRST_TOKEN_REJECT = {
    "with", "and", "or", "that", "which", "who", "where", "when", "if", "as",
    "by", "in", "on", "for", "to", "of", "from", "under", "without",
}


def _sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class RuleOrderAdapterError(RuntimeError):
    """Raised when adapter inputs violate the shared contract."""


class SharedRuleOrderAdapterV3:
    """Extract Type-A action-action precedence edges from source text.

    Parameters
    ----------
    matcher:
        Shared semantic matcher exposing ``similarity(a, b) -> float``.
    min_binding_score:
        Minimum combined clause-binding score required for an edge.
    max_fronted_span:
        Maximum number of characters between a fronted marker and its comma.
    """

    schema_version = SCHEMA_VERSION
    marker_specs = MARKER_SPECS

    def __init__(self, matcher: Any, *, min_binding_score: float = 1.15,
                 max_fronted_span: int = 120):
        self.matcher = matcher
        self.min_binding_score = float(min_binding_score)
        self.max_fronted_span = int(max_fronted_span)
        self._marker_patterns = [
            (name, orientation, re.compile(pattern, flags=re.IGNORECASE))
            for name, orientation, pattern in self.marker_specs
        ]

    # ------------------------------------------------------------------ public
    def project(self,
                source_text: str,
                record: Mapping[str, Any] | None = None,
                *,
                nlp: Any,
                rule_id: str = "",
                action_elements: Sequence[Stage2ActionElement | Mapping[str, Any]] | None = None,
                native_relations: Sequence[Mapping[str, Any]] | None = None,
                ) -> dict[str, Any]:
        if not isinstance(source_text, str):
            raise RuleOrderAdapterError("source_text must be a string")
        if nlp is None:
            raise RuleOrderAdapterError("nlp is required")

        actions = self._coerce_actions(action_elements or [])
        action_lookup = {action.action_id: action.text for action in actions}
        native = (
            list(native_relations)
            if native_relations is not None
            else normalize_native_order_relations(record, action_lookup)
        )

        base: dict[str, Any] = {
            "schema_version": self.schema_version,
            "rule_id": str(rule_id),
            "source_text_sha256": _sha256_text(source_text),
            "action_count": len(actions),
            "native_relation_count": len(native),
            "native_precedence": NATIVE_PRECEDENCE,
            "endpoint_policy": "existing_stage2_action_only",
            "nominal_endpoint_policy": "forbidden",
            "algorithm": "shared_rule_order_adapter_v3",
            "actions": [action.to_dict() for action in actions],
            "marker_set": [name for name, _, _ in self.marker_specs],
            "markers": [],
            "edges": [],
            "edge_pairs": [],
            "status": None,
            "status_reason": None,
        }

        if native:
            edges = self._native_edges(native, rule_id)
            base["edges"] = edges
            base["edge_pairs"] = [[e["before_text"], e["after_text"]] for e in edges]
            base["status"] = "native_preserved"
            base["status_reason"] = "native_order_relations_non_empty"
            return base

        marker_audits: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str, str]] = set()

        for marker_name, orientation, pattern in self._marker_patterns:
            for match in pattern.finditer(source_text):
                marker_start, marker_end = match.span()
                if self._is_false_following(source_text, marker_name, marker_start, marker_end):
                    marker_audits.append({
                        "marker": marker_name,
                        "marker_span": [marker_start, marker_end],
                        "orientation": orientation,
                        "status": "false_temporal_marker",
                        "status_reason": "following_used_as_adjectival_determiner",
                        "selected_left_action": None,
                        "selected_right_action": None,
                        "pattern_type": None,
                        "clause_left": None,
                        "clause_right": None,
                        "edges_generated": 0,
                    })
                    continue

                pattern_type, left_clause, right_clause = self._clause_context(
                    source_text, marker_start, marker_end, nlp
                )
                audit: dict[str, Any] = {
                    "marker": marker_name,
                    "marker_span": [marker_start, marker_end],
                    "orientation": orientation,
                    "pattern_type": pattern_type,
                    "clause_left": left_clause,
                    "clause_right": right_clause,
                    "selected_left_action": None,
                    "selected_right_action": None,
                    "candidate_left_actions": [],
                    "candidate_right_actions": [],
                    "edges_generated": 0,
                    "status": None,
                    "status_reason": None,
                }
                if not left_clause or not right_clause:
                    audit["status"] = "no_edge"
                    audit["status_reason"] = "empty_clause_context"
                    marker_audits.append(audit)
                    continue

                left_candidates = self._bind_side(actions, left_clause, nlp)
                right_candidates = self._bind_side(actions, right_clause, nlp)
                audit["candidate_left_actions"] = [
                    {"action_id": a.action_id, "text": a.text, "score": round(score, 4), "matched_predicate": verb}
                    for score, a, verb in left_candidates
                ]
                audit["candidate_right_actions"] = [
                    {"action_id": a.action_id, "text": a.text, "score": round(score, 4), "matched_predicate": verb}
                    for score, a, verb in right_candidates
                ]
                if not left_candidates or not right_candidates:
                    audit["status"] = "no_edge"
                    audit["status_reason"] = "no_action_candidate_for_one_side"
                    marker_audits.append(audit)
                    continue

                pair = self._select_pair(
                    left_candidates, right_candidates,
                    source_text=source_text,
                    marker_name=marker_name,
                    orientation=orientation,
                    pattern_type=pattern_type,
                )
                if pair is None:
                    audit["status"] = "no_edge"
                    audit["status_reason"] = "ambiguous_or_below_threshold_endpoint_pair"
                    marker_audits.append(audit)
                    continue

                score, left_action, right_action, before, after, before_text, after_text = pair
                audit["selected_left_action"] = {
                    "action_id": left_action.action_id,
                    "text": left_action.text,
                    "endpoint_surface": before_text,
                }
                audit["selected_right_action"] = {
                    "action_id": right_action.action_id,
                    "text": right_action.text,
                    "endpoint_surface": after_text,
                }
                audit["pair_score"] = round(score, 4)
                dedupe_key = (before.action_id, after.action_id, marker_name, orientation)
                if dedupe_key in seen:
                    audit["status"] = "duplicate_edge_skipped"
                    marker_audits.append(audit)
                    continue
                seen.add(dedupe_key)
                edge = {
                    "edge_id": f"{rule_id}:order:{len(edges) + 1}",
                    "before_action_id": before.action_id,
                    "after_action_id": after.action_id,
                    "before_text": before.text,
                    "after_text": after.text,
                    "before_action_text": before.text,
                    "after_action_text": after.text,
                    "before_endpoint_surface": before_text,
                    "after_endpoint_surface": after_text,
                    "before_span": [before.start, before.end],
                    "after_span": [after.start, after.end],
                    "marker": marker_name,
                    "marker_span": [marker_start, marker_end],
                    "orientation": orientation,
                    "source": "shared_rule_order_adapter_v3",
                    "endpoint_policy": "existing_stage2_action_predicate_surface",
                    "pattern_type": pattern_type,
                    "binding_score": round(score, 4),
                    "endpoint_surface_policy": "matched_clause_predicate_from_existing_action",
                }
                edges.append(edge)
                audit["edges_generated"] = 1
                audit["status"] = "edge_generated"
                marker_audits.append(audit)

        base["markers"] = marker_audits
        base["edges"] = edges
        base["edge_pairs"] = [[e["before_text"], e["after_text"]] for e in edges]
        if not marker_audits:
            base["status"] = "no_marker_found"
            base["status_reason"] = "marker_set_absent"
        elif not edges:
            base["status"] = "no_edge"
            base["status_reason"] = "no_marker_bound_a_unique_existing_action_pair"
        else:
            base["status"] = "projected"
            base["status_reason"] = "at_least_one_marker_bound_existing_action_pair"
        return base

    # --------------------------------------------------------------- internals
    @staticmethod
    def _coerce_actions(action_elements: Sequence[Stage2ActionElement | Mapping[str, Any]]
                        ) -> list[Stage2ActionElement]:
        actions: list[Stage2ActionElement] = []
        for item in action_elements:
            if isinstance(item, Stage2ActionElement):
                actions.append(item)
                continue
            if not isinstance(item, Mapping):
                continue
            start = item.get("start")
            end = item.get("end")
            if not isinstance(start, int) or not isinstance(end, int):
                continue
            actions.append(Stage2ActionElement(
                action_id=str(item.get("action_id") or item.get("id") or ""),
                text=str(item.get("text") or ""),
                start=int(start),
                end=int(end),
                clause_id=str(item.get("clause_id") or ""),
            ))
        unique: "OrderedDict[tuple[str, int, int, str], Stage2ActionElement]" = OrderedDict()
        for action in actions:
            unique[(action.action_id, action.start, action.end, action.text)] = action
        return sorted(unique.values(), key=lambda a: (a.start, a.end, a.action_id))

    @staticmethod
    def _native_edges(native: Sequence[Mapping[str, Any]], rule_id: str) -> list[dict[str, Any]]:
        edges: list[dict[str, Any]] = []
        for entry in native:
            edges.append({
                "edge_id": f"{rule_id}:native:{len(edges) + 1}",
                "before_action_id": entry.get("before_action_id"),
                "after_action_id": entry.get("after_action_id"),
                "before_text": entry.get("before_text"),
                "after_text": entry.get("after_text"),
                "marker": None,
                "marker_span": None,
                "orientation": "native_stage2",
                "source": "native_stage2_order_relation",
                "endpoint_policy": "native_stage2_action_reference",
                "pattern_type": "native",
                "binding_score": None,
            })
        return edges

    @staticmethod
    def _is_false_following(source_text: str, marker_name: str, start: int, end: int) -> bool:
        if marker_name != "following":
            return False
        tail = source_text[start:end + 30].casefold()
        return bool(re.search(r"\bfollowing\s+(information|grounds|purposes|condition|conditions)\b", tail))

    def _clause_context(self, source_text: str, marker_start: int, marker_end: int, nlp: Any
                        ) -> tuple[str, str, str]:
        """Return ``(pattern_type, left_clause, right_clause)``.

        ``inline`` means the marker occurs between the two clauses.
        ``fronted`` means the marker begins a fronted temporal adjunct, e.g.
        ``before approving X, submit Y``.  In that case ``left_clause`` is the
        marker's object clause and ``right_clause`` is the main clause after
        the comma.
        """
        before = source_text[:marker_start].rstrip()
        fronted_candidate = (not before) or before[-1] in ",;:"
        if fronted_candidate:
            after = source_text[marker_end:]
            comma_after = after.find(",")
            if 0 <= comma_after <= self.max_fronted_span:
                object_clause = after[:comma_after].strip(" ,;:")
                rest = after[comma_after + 1:]
                main_clause = self._first_clause(rest)
                if (object_clause and main_clause
                        and self._main_verb(object_clause, nlp)
                        and self._main_verb(main_clause, nlp)):
                    return "fronted", object_clause, main_clause

        left_start = self._previous_boundary(source_text, marker_start)
        right_end = self._next_boundary(source_text, marker_end)
        left_clause = source_text[left_start:marker_start].strip(" ,;:")
        right_clause = source_text[marker_end:right_end].strip(" ,;:")
        return "inline", left_clause, right_clause

    @staticmethod
    def _previous_boundary(text: str, pos: int) -> int:
        index = max(
            text.rfind(",", 0, pos),
            text.rfind(";", 0, pos),
            text.rfind(":", 0, pos),
            text.rfind(".", 0, pos),
        )
        return index + 1 if index != -1 else 0

    @staticmethod
    def _next_boundary(text: str, pos: int) -> int:
        candidates = [
            index for index in (
                text.find(",", pos),
                text.find(";", pos),
                text.find(":", pos),
                text.find(".", pos),
            ) if index != -1
        ]
        return min(candidates) if candidates else len(text)

    @staticmethod
    def _first_clause(text: str) -> str:
        end = SharedRuleOrderAdapterV3._next_boundary(text, 0)
        return text[:end].strip(" ,;:")

    # ------------------------------------------------------------ morphology
    @staticmethod
    def _gerund_roots(token_text: str) -> set[str]:
        low = token_text.casefold()
        if low.endswith("ing") and len(low) > 5:
            stem = low[:-3]
            roots = {stem}
            if stem.endswith(("v", "d", "m")):
                roots.add(stem + "e")
            return roots
        return set()

    @classmethod
    def _roots_for_token(cls, token: Any) -> set[str]:
        roots: set[str] = set()
        if not token.is_alpha:
            return roots
        lemma = token.lemma_.casefold()
        if lemma not in _STOP_LEMMAS:
            roots.add(lemma)
        roots |= cls._gerund_roots(token.text)
        return roots

    @classmethod
    def _verb_roots(cls, text: str, nlp: Any) -> set[str]:
        roots: set[str] = set()
        for token in nlp(text):
            if not token.is_alpha:
                continue
            lemma = token.lemma_.casefold()
            if lemma in _STOP_LEMMAS:
                continue
            if token.pos_ in ("VERB", "AUX") or token.tag_ == "VBG":
                roots |= cls._roots_for_token(token)
            elif token.pos_ == "NOUN" and token.text.casefold().endswith("ing"):
                roots |= cls._roots_for_token(token)
        return roots

    @classmethod
    def _main_verb(cls, text: str, nlp: Any = None) -> str | None:
        if nlp is None:  # pragma: no cover - public callers pass nlp
            return None
        doc = nlp(text)
        # 1. Prefer the syntactic root if it is a lexical verb.
        for token in doc:
            if token.head is token and token.pos_ == "VERB":
                lemma = token.lemma_.casefold()
                if lemma not in _STOP_LEMMAS:
                    return lemma
        # 2. Otherwise use the first non-auxiliary lexical verb.
        for token in doc:
            if token.pos_ == "VERB" and token.lemma_.casefold() not in _STOP_LEMMAS:
                return token.lemma_.casefold()
        # 3. Deverbal gerund / gerund-like noun.
        for token in doc:
            if token.tag_ == "VBG" or (token.pos_ == "NOUN" and token.text.casefold().endswith("ing")):
                roots = cls._roots_for_token(token)
                if roots:
                    return sorted(roots)[0]
        return None

    @staticmethod
    def _action_is_fragment(text: str, nlp: Any) -> bool:
        tokens = [token for token in nlp(text) if token.is_alpha]
        if not tokens:
            return True
        return tokens[0].text.casefold() in _FIRST_TOKEN_REJECT

    @classmethod
    def _endpoint_surface(cls, main_verb: str, action_text: str, clause_text: str,
                          nlp: Any) -> str:
        """Return a compact predicate+object surface bound to the action.

        The surface is derived from the existing Stage-2 action span or, when
        the action is a bare verb, from the source clause that syntactically
        realises its object.  It never introduces a new action or a Gold label.
        """
        for text in (action_text, clause_text):
            doc = nlp(text)
            token = None
            for candidate in doc:
                if not candidate.is_alpha:
                    continue
                roots = cls._roots_for_token(candidate)
                if main_verb in roots:
                    token = candidate
                    break
            if token is None:
                continue
            parts: list[str] = [main_verb]
            object_phrases: list[str] = []
            for child in token.children:
                if child.dep_ in ("dobj", "pobj", "attr", "oprd", "dative"):
                    phrase = " ".join(t.text for t in child.subtree if not t.is_punct)
                    if phrase:
                        object_phrases.append(phrase)
            if not object_phrases:
                for chunk in doc.noun_chunks:
                    if token.i < chunk.start <= token.i + 8:
                        object_phrases.append(chunk.text)
                        break
            for phrase in object_phrases:
                if phrase.casefold() not in main_verb.casefold():
                    parts.append(phrase)
            if len(parts) > 1:
                return " ".join(parts[:8]).casefold()
        return main_verb

    def _bind_action(self, action: Stage2ActionElement, clause: str, nlp: Any
                     ) -> tuple[float, str | None]:
        if self._action_is_fragment(action.text, nlp):
            return 0.0, None
        main_verb = self._main_verb(clause, nlp)
        if not main_verb:
            return 0.0, None
        action_verbs = self._verb_roots(action.text, nlp)
        if main_verb not in action_verbs:
            return 0.0, None
        similarity = float(self.matcher.similarity(action.text, clause))
        shared = 1
        score = 1.0 + 0.6 * similarity + 0.3 * shared
        endpoint_surface = self._endpoint_surface(main_verb, action.text, clause, nlp)
        return score, endpoint_surface

    def _bind_side(self, actions: Sequence[Stage2ActionElement], clause: str, nlp: Any
                   ) -> list[tuple[float, Stage2ActionElement, str]]:
        candidates: list[tuple[float, Stage2ActionElement, str]] = []
        for action in actions:
            score, main_verb = self._bind_action(action, clause, nlp)
            if score > 0.0 and main_verb is not None:
                candidates.append((score, action, main_verb))
        candidates.sort(key=lambda item: (-item[0], item[1].start, item[1].end, item[1].action_id))
        return candidates

    def _select_pair(self,
                     left_candidates: Sequence[tuple[float, Stage2ActionElement, str]],
                     right_candidates: Sequence[tuple[float, Stage2ActionElement, str]],
                     *,
                     source_text: str,
                     marker_name: str,
                     orientation: str,
                     pattern_type: str,
                     ) -> tuple[float, Stage2ActionElement, Stage2ActionElement,
                                Stage2ActionElement, Stage2ActionElement, str, str] | None:
        scored: list[tuple[float, Stage2ActionElement, Stage2ActionElement,
                            Stage2ActionElement, Stage2ActionElement, str, str]] = []
        for left_score, left_action, left_verb in left_candidates:
            for right_score, right_action, right_verb in right_candidates:
                if left_action.action_id == right_action.action_id:
                    continue
                score = left_score + right_score
                if pattern_type == "inline":
                    if orientation == "left_before_right":
                        before, after = left_action, right_action
                        before_text, after_text = left_verb, right_verb
                    else:
                        before, after = right_action, left_action
                        before_text, after_text = right_verb, left_verb
                else:
                    # fronted marker: left_clause is the marker's object
                    # clause, right_clause is the main clause.
                    if marker_name in ("before", "prior to", "in advance of", "preceding"):
                        before, after = right_action, left_action
                        before_text, after_text = right_verb, left_verb
                    else:
                        before, after = left_action, right_action
                        before_text, after_text = left_verb, right_verb
                scored.append((score, left_action, right_action, before, after,
                               before_text, after_text))
        if not scored:
            return None
        scored.sort(key=lambda item: (-item[0], item[3].start, item[4].start))
        best = scored[0]
        if best[0] < self.min_binding_score:
            return None
        # Require a clear margin over the best alternative pair.  This makes
        # ambiguous endpoint binding produce ``no edge`` instead of guessing.
        if len(scored) > 1:
            alternative = scored[1]
            if abs(best[0] - alternative[0]) < 0.05:
                return None
        return best

__all__ = [
    "SCHEMA_VERSION",
    "MARKER_SPECS",
    "RuleOrderAdapterError",
    "SharedRuleOrderAdapterV3",
]
