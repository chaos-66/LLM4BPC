# -*- coding: utf-8 -*-
"""Shared Sun/Ours surface normalization for role comparison.

Approved scope (2026-09-26):
- Unicode casefold;
- collapse whitespace;
- remove a leading English article (the/a/an).

No synonym dictionary, no Gold-derived mapping, and no method-specific
favouritism.  In particular, ``controller`` and ``processor`` remain distinct.
"""

from __future__ import annotations

import re

_LEADING_ARTICLE = re.compile(r"^(the|a|an)\s+", re.IGNORECASE)


def normalize_role_surface(value: str) -> str:
    """Return the approved role surface form used by shared comparison."""
    text = " ".join(str(value or "").casefold().split())
    if not text:
        return ""
    while True:
        stripped = _LEADING_ARTICLE.sub("", text, count=1)
        if stripped == text:
            break
        text = stripped.strip()
    return text


def role_surfaces_equal(left: str, right: str) -> bool:
    """Exact equality after approved normalization only."""
    return normalize_role_surface(left) == normalize_role_surface(right)
