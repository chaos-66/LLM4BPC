# -*- coding: utf-8 -*-
"""Winter et al. (2020) Stage 3 baseline: regulation paragraph parsing.

Transcribed from the read-only Winter prototype
(``references/winter_2020_model_check/model_check/lib/classes/``
``Paragraph.py``, ``Sentence.py``, ``Clause.py``, ``Flow.py`` and
``Document_Collection.py``): a regulation text is split into sentences by
spaCy; sentences containing a signal word (``shall``/``must``/``should``/
``may``) are constraints; each sentence is split into clauses by dependency
subtrees (ROOT / verb-conj / verb-prep); with ``only_constraints=True`` the
paragraph obligations are the clauses of constraint sentences; sequential
order relations (flows) are detected from sequence markers ("After", "then",
...). Clause lemmatization drops stopwords/punct/numbers, mirroring the
prototype.
"""

from __future__ import annotations

from typing import Any

SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
COMP = ["compound", "amod", "conj"]
OBJECTS = ["dobj", "dative", "attr", "oprd", "pobj"]
VERB_MOD = ["aux", "acomp", "xcomp"]


class WinterClause:
    """One obligation clause: lemmatized string + (prototype-compatible)
    subject/verb/object/rest accessors."""

    def __init__(self, clause_id: str, nlp, stopwords: set[str], clause_tokens: list[Any]):
        self._id = clause_id
        self.nlp = nlp
        self.stopwords = stopwords
        self.clause = clause_tokens
        self.subject = None
        self.verb = None
        self.object = None
        self.rest = None
        self.lemmatized = _lemmatize_tokens(clause_tokens, stopwords)


class WinterFlow:
    """Sequential order relation between two clauses (condition -> consequence)."""

    def __init__(self, flow_id: str, condition: Any, consequence: Any, stopwords: set[str]):
        self._id = flow_id
        self.condition = condition
        self.consequence = consequence
        self.stopwords = stopwords

    def lemmatize_condition(self) -> str:
        return _lemmatize_parts(self.condition, self.stopwords)

    def lemmatize_consequence(self) -> str:
        return _lemmatize_parts(self.consequence, self.stopwords)


class WinterParagraph:
    """One regulation article: obligations (clauses of constraint sentences)
    and flows (sequential order relations)."""

    def __init__(self, paragraph_id: str, sentences: list[Any],
                 sequencemarkers: set[str], only_constraints: bool):
        self.paragraphID = paragraph_id
        self.sentences = sentences
        self.sequencemarkers = sequencemarkers
        self.only_constraints = only_constraints
        self.obligations = self.calculate_obligations(only_constraints)
        self.flows = self.calculate_flows()

    def calculate_obligations(self, only_constraints: bool) -> list[Any]:
        result = []
        for sentence in self.sentences:
            if only_constraints and sentence.constraint is False:
                continue
            for clause in sentence.clauses:
                result.append(clause)
            if not result:
                result.append(sentence)
        return result

    def calculate_flows(self) -> list[Any] | None:
        if len(self.obligations) == 1:
            return None
        result = []
        for idx, obligation in enumerate(self.obligations):
            if _exists_flow_intra(obligation, self.sequencemarkers):
                condition, consequence = _extract_intra_flow(obligation)
                result.append(WinterFlow(obligation._id, condition, consequence, obligation.stopwords))
            elif _exists_flow(obligation, self.sequencemarkers):
                result.append(WinterFlow(obligation._id, obligation, self.obligations[idx], obligation.stopwords))
        return result


class WinterSentence:
    """One sentence: constraint flag + dependency-subtree clauses."""

    def __init__(self, paragraph_id: str, sentence_id: str, nlp, stopwords: set[str],
                 constraint: bool, doc: Any):
        self.paragraphID = paragraph_id
        self._id = sentence_id
        self.nlp = nlp
        self.stopwords = stopwords
        self.constraint = constraint
        self.original = doc
        self.clauses = self.calculate_clauses()

    def calculate_clauses(self) -> list[WinterClause]:
        root = None
        for word in self.original:
            if word.dep_ == "ROOT":
                root = word
                break
        if root is None:
            return [WinterClause(self._id + "0", self.nlp, self.stopwords, list(self.original))]
        trees = _subtrees(root)
        curr = []
        clauses = []
        for t in reversed(trees):
            head = t[0]
            subtree = t[1]
            if (head.dep_ == "ROOT"
                    or (head.dep_ == "conj" and head.pos_ == "VERB")
                    or (head.dep_ == "prep" and _contains_verb(subtree))):
                clause_tokens = [i for i in subtree if i not in curr]
                clauses.append(WinterClause(self._id + str(len(clauses)), self.nlp, self.stopwords, clause_tokens))
                curr.extend(subtree)
        # prototype sort_clauses: single-token clauses sort first (key 1),
        # otherwise by first token position; stable sort preserves order.
        clauses.sort(key=lambda c: 1 if len(c.clause) == 1 else c.clause[0].i)
        previous_subj = None
        for clause in clauses:
            for token in clause.clause:
                if token.dep_ in SUBJECTS and token.head.pos_ == "VERB" and token.pos_ != "PRON":
                    previous_subj = [t for t in token.subtree
                                     if ((t.dep_ in COMP and t in token.lefts) or t == token)]
            clause.subject = previous_subj
        return clauses


def parse_regulation_paragraph(paragraph_id: str, text: str, nlp, stopwords: set[str],
                               signalwords: set[str], sequencemarkers: set[str],
                               only_constraints: bool = True) -> WinterParagraph:
    """Mirror Document_Collection.get_paragraphs for a single article."""
    doc = nlp(text)
    sentences = []
    for idx, sentence in enumerate(doc.sents):
        flag = any(w.text in signalwords for w in sentence)
        sentences.append(
            WinterSentence(paragraph_id, paragraph_id + str(idx), nlp, stopwords, flag, sentence)
        )
    return WinterParagraph(paragraph_id, sentences, sequencemarkers, only_constraints)


def _lemmatize_tokens(tokens: list[Any], stopwords: set[str]) -> str:
    result = []
    for word in tokens:
        if word.lemma_ == "-PRON-":
            result.append(word.text)
        else:
            if word.is_punct or word.like_num or word.is_space or word.text in stopwords:
                continue
            result.append(word.lemma_)
    return " ".join(result)


def _lemmatize_parts(part: Any, stopwords: set[str]) -> str:
    if hasattr(part, "clause"):
        return _lemmatize_tokens(part.clause, stopwords)
    return _lemmatize_tokens(list(part), stopwords)


def _subtrees(node: Any) -> list[tuple[Any, list[Any]]]:
    if not node.children:
        return []
    result = [(node, list(node.subtree))]
    for child in node.children:
        result.extend(_subtrees(child))
    return result


def _contains_verb(tokens: list[Any]) -> bool:
    return any(w.pos_ == "VERB" for w in tokens)


def _exists_flow_intra(obligation: Any, sequencemarkers: set[str]) -> bool:
    for x in obligation.clause:
        if x.text in sequencemarkers and x.i == 0 and x.text == "After":
            return True
    return False


def _extract_intra_flow(obligation: Any) -> tuple[list[Any], list[Any]]:
    condition = list(obligation.clause[0].subtree)
    indices = {t.i for t in condition}
    consequence = [t for t in obligation.clause if t.i not in indices]
    return (condition, consequence)


def _exists_flow(obligation: Any, sequencemarkers: set[str]) -> bool:
    for x in obligation.clause:
        if x.text in sequencemarkers and x.i != 0:
            return True
    return False
