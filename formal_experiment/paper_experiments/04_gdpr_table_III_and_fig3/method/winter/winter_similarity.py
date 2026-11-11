# -*- coding: utf-8 -*-
"""Winter et al. (2020) Stage 3 baseline: spaCy similarity helpers.

Transcribed from the read-only Winter prototype
(``references/winter_2020_model_check/model_check/lib/classes/SimilarityComputer.py``):
three similarity functions (text-obligation to model obligation, task to
clause, and paragraph-level) all use spaCy ``.similarity()`` on lemmatized
text and return 0.0 when either side has no vector. The prototype's JSON
cache is replaced by an in-process memo dict (deterministic, no files).
"""

from __future__ import annotations

from typing import Any


class WinterSimilarity:
    def __init__(self, nlp):
        self.nlp = nlp
        self._parse_cache: dict[str, Any] = {}
        self._sim_cache: dict[tuple[str, str], float] = {}

    def _parse(self, text: str) -> Any:
        doc = self._parse_cache.get(text)
        if doc is None:
            doc = self.nlp(text)
            self._parse_cache[text] = doc
        return doc

    def _similarity(self, left: str, right: str) -> float:
        key = (left, right)
        if key in self._sim_cache:
            return self._sim_cache[key]
        left_doc = self._parse(left)
        right_doc = self._parse(right)
        if not left_doc.has_vector or not right_doc.has_vector:
            value = 0.0
        else:
            value = float(left_doc.similarity(right_doc))
        self._sim_cache[key] = value
        return value

    def text_model_obligation(self, text_obligation: str, model_obligation: list[str]) -> float:
        """spacy_similarity_text_model_obligation: lemmatized clause vs
        lemmatized model obligation."""
        return self._similarity(text_obligation, " ".join(model_obligation))

    def task_clause(self, task: list[str], clause: Any) -> float:
        """spacy_similarity_task_clause: lemmatized task vs clause
        (resource-cost path uses the raw clause object)."""
        return self._similarity(" ".join(task), clause.lemmatized)

    def text_pair(self, left: str, right: str) -> float:
        """Direct text-pair similarity used by flow checks."""
        return self._similarity(left, right)
