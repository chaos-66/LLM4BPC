"""CFKW: German keyword-rule sentence classifier (independent reimplementation).

Sun et al. (2024) compared a keyword classifier (``CFKW``) with a BiLSTM
(``CFRNN``), a CNN (``CFCNN``) and their BERT variant.  No author code or
author lexicon is available, so this is an **independent reimplementation
from the paper's method description**, not the authors' original system.

Fixed design (pre-registered before any test evaluation):

* Tokenisation: lowercase letter runs (the corpus itself is lowercase and
  punctuation-stripped).
* Cues are ordered token n-grams, matched as contiguous token
  subsequences anywhere in the sentence.
* Rule priority is a total order over the four classes.  The highest
  priority class with at least one matching cue wins; the matched cue and
  its tier are recorded for traceability.
* If no cue of any class matches, a declared fallback class is used.
  The fallback is a rule, not a guess: it is the majority class of the
  training split.
* Priority order and fallback were selected on the **dev** split only,
  from a small pre-declared candidate list; the test split is evaluated
  once with the frozen selection.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from .metrics import LABELS

_TOKEN_RE = re.compile(r"[a-zäöüß]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


# Cue inventory, grouped by the semantic class it votes for.  Every cue is
# a token n-gram; multiword cues keep their word order.
CUES: dict[str, tuple[tuple[str, ...], ...]] = {
    "prohibition": (
        ("nicht", "zulässig"),
        ("nicht", "gestattet"),
        ("nicht", "erlaubt"),
        ("nicht", "statthaft"),
        ("unzulässig",),
        ("untersagt",),
        ("verboten",),
        ("keinesfalls",),
        ("darf", "nicht"),
        ("dürfen", "nicht"),
        ("hat", "zu", "unterbleiben"),
        ("haben", "zu", "unterbleiben"),
        ("ist", "zu", "unterlassen"),
        ("sind", "zu", "unterlassen"),
        ("zu", "unterbleiben"),
        ("nicht", "vorzunehmen"),
        ("nicht", "anzuwenden"),
        ("nicht", "anzusetzen"),
        ("nicht", "abzugsfähig"),
    ),
    "permission": (
        ("kann",),
        ("können",),
        ("darf",),
        ("dürfen",),
        ("berechtigt",),
        ("ermächtigt",),
        ("gestattet",),
        ("steht", "frei"),
        ("nach", "wahl"),
        ("wahlweise",),
        ("optional",),
        ("auf", "antrag"),
    ),
    "obligation": (
        ("muss",),
        ("müssen",),
        ("soll",),
        ("sollen",),
        ("ist", "zu"),
        ("sind", "zu"),
        ("hat", "zu"),
        ("haben", "zu"),
        ("verpflichtet",),
        ("erforderlich",),
        ("anzuwenden",),
        ("einzubehalten",),
    ),
    "definition": (
        ("bezeichnet",),
        ("gelten", "als"),
        ("gilt", "als"),
        ("im", "sinne"),
        ("bedeutet",),
        ("versteht", "man"),
        ("umfasst",),
        ("liegen", "vor"),
        ("gehören", "zu"),
        ("gehört", "zu"),
        ("zählt",),
        ("sind", "anzusehen"),
        ("ist", "anzusehen"),
        ("ist", "zu", "verstehen"),
        ("ist", "ein"),
        ("ist", "eine"),
        ("sind", "ein"),
        ("sind", "eine"),
        ("ist", "der"),
        ("ist", "die"),
        ("ist", "das"),
        ("sind", "die"),
        ("sind", "der"),
        ("ist", "nicht"),
        ("sind", "nicht"),
        ("ist", "auch"),
        ("ist", "im"),
    ),
}

# Permission modals whose negation within a short window turns the clause
# into a prohibition ("darf ... nicht", "dürfen sich nicht vermindern").
PERMISSION_MODALS: tuple[str, ...] = ("darf", "dürfen", "kann", "können", "mag")
NEGATORS: tuple[str, ...] = ("nicht", "kein", "keine", "keinen", "keinesfalls", "niemals")
NEGATION_WINDOW = 4

# Pre-declared candidate configurations; the dev split selects one.
CANDIDATES: dict[str, dict[str, object]] = {
    "priority_prohibition_permission_obligation_definition_fallback_obligation": {
        "priority": ["prohibition", "permission", "obligation", "definition"],
        "fallback": "obligation",
    },
    "priority_prohibition_obligation_permission_definition_fallback_obligation": {
        "priority": ["prohibition", "obligation", "permission", "definition"],
        "fallback": "obligation",
    },
    "priority_prohibition_permission_obligation_definition_fallback_definition": {
        "priority": ["prohibition", "permission", "obligation", "definition"],
        "fallback": "definition",
    },
    "priority_prohibition_obligation_permission_definition_fallback_definition": {
        "priority": ["prohibition", "obligation", "permission", "definition"],
        "fallback": "definition",
    },
}


@dataclass(frozen=True)
class KeywordDecision:
    label: str
    tier: str | None
    cue: tuple[str, ...] | None
    matched_tier: bool


def _contains(tokens: Sequence[str], cue: Sequence[str]) -> bool:
    n = len(cue)
    if n == 0 or n > len(tokens):
        return False
    first = cue[0]
    for i in range(len(tokens) - n + 1):
        if tokens[i] != first:
            continue
        if tuple(tokens[i : i + n]) == tuple(cue):
            return True
    return False


def _negated_permission(tokens: Sequence[str]) -> tuple[str, ...] | None:
    """Return the matched modal cue when a permission modal is negated nearby."""
    for index, token in enumerate(tokens):
        if token not in PERMISSION_MODALS:
            continue
        window = tokens[index + 1 : index + 1 + NEGATION_WINDOW]
        for negator in NEGATORS:
            if negator in window:
                return (token, negator)
    return None


class KeywordClassifier:
    """Deterministic ordered keyword classifier with an explicit fallback."""

    def __init__(self, priority: Sequence[str], fallback: str) -> None:
        if list(sorted(priority)) != sorted(LABELS):
            raise ValueError("priority must be a total order over the four labels")
        if fallback not in LABELS:
            raise ValueError("unknown fallback label")
        self.priority = list(priority)
        self.fallback = fallback

    @classmethod
    def from_candidate(cls, name: str) -> "KeywordClassifier":
        spec = CANDIDATES[name]
        return cls(priority=spec["priority"], fallback=spec["fallback"])  # type: ignore[arg-type]

    def decide(self, text: str) -> KeywordDecision:
        tokens = tokenize(text)
        for tier in self.priority:
            if tier == "prohibition":
                negated = _negated_permission(tokens)
                if negated is not None:
                    return KeywordDecision(
                        label="prohibition",
                        tier="prohibition",
                        cue=negated,
                        matched_tier=True,
                    )
            for cue in CUES[tier]:
                if _contains(tokens, cue):
                    return KeywordDecision(
                        label=tier, tier=tier, cue=cue, matched_tier=True
                    )
        return KeywordDecision(
            label=self.fallback, tier=None, cue=None, matched_tier=False
        )

    def predict(self, texts: Iterable[str]) -> list[str]:
        return [self.decide(text).label for text in texts]

    def describe(self) -> Mapping[str, object]:
        return {
            "method": "cfkw_independent_keyword_rule_reimplementation",
            "tokenizer": "lowercase_letter_runs",
            "priority": self.priority,
            "fallback": self.fallback,
            "cue_counts": {label: len(cues) for label, cues in CUES.items()},
            "cues": {label: [" ".join(cue) for cue in cues] for label, cues in CUES.items()},
            "not_author_original": (
                "No author code or author lexicon was available; cues and "
                "priority were written from the paper's method description and "
                "selected on the dev split."
            ),
        }


def select_on_dev(
    dev_rows: Sequence[Mapping[str, str]]
) -> tuple[str, dict[str, dict[str, float]]]:
    """Select priority/fallback by dev macro-F1 (deterministic tie-break)."""
    from .metrics import evaluate

    gold = [row["label"] for row in dev_rows]
    scores: dict[str, dict[str, float]] = {}
    best_name = None
    best_key = None
    for name in CANDIDATES:
        classifier = KeywordClassifier.from_candidate(name)
        pred = classifier.predict([row["text"] for row in dev_rows])
        metrics = evaluate(gold, pred)
        scores[name] = {
            "macro_f1": metrics["macro_f1"],
            "accuracy": metrics["accuracy"],
        }
        key = (metrics["macro_f1"], metrics["accuracy"], -list(CANDIDATES).index(name))
        if best_key is None or key > best_key:
            best_key = key
            best_name = name
    assert best_name is not None
    return best_name, scores
