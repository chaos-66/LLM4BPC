"""Prospective constituent-bound scope repair, independent of benchmark labels.

Prefix markers are restricted to an actual SBAR/PP/NP/ADVP constituent.
The legacy regex fallback may cross a main clause, so it is not reused here.
Temporal NP attachments introduced by `with` remain available to the action;
this explicit disambiguation is a reconstruction choice, not an author rule.
"""
from __future__ import annotations

import copy
import re


def constituents(parse, token_count):
    pieces = re.findall(r"\(|\)|[^\s()]+", parse)
    position = leaf_index = 0
    nodes = []

    def consume():
        nonlocal position, leaf_index
        if pieces[position] != "(":
            raise ValueError("invalid Penn tree")
        position += 1
        label = pieces[position]
        position += 1
        begin = leaf_index
        children = []
        while pieces[position] != ")":
            if pieces[position] == "(":
                children.append(consume())
            else:
                leaf_index += 1
                position += 1
        position += 1
        node = {"label": label, "begin": begin, "end": leaf_index, "children": children}
        nodes.append(node)
        return node

    consume()
    if position != len(pieces) or leaf_index != token_count:
        raise ValueError("Penn tree/token alignment drift")
    return nodes


def scope_indexes(sentence, markers):
    tokens = sentence["tokens"]
    nodes = constituents(sentence["parse"], len(tokens))
    found = {f: [] for f in ("conditions", "constraints", "exceptions")}
    legal_nodes = {"conditions": {"SBAR", "PP", "ADVP"},
                   "constraints": {"PP", "NP", "ADVP", "ADJP", "SBAR"},
                   "exceptions": {"SBAR", "PP", "NP", "ADVP"}}
    temporal = {"before", "after", "prior to", "within", "until", "during",
                "between", "throughout", "no later than", "no earlier than"}
    for field in found:
        for node in nodes:
            if node["label"] not in legal_nodes[field]:
                continue
            indexes = list(range(node["begin"], node["end"]))
            words = [str(tokens[i]["word"]).casefold() for i in indexes]
            prefixes = [m for m in markers[field] if words[:len(m.split())] == m.split()]
            if not prefixes:
                continue
            marker = max(prefixes, key=lambda m: len(m.split()))
            # A temporal target can have a parser-attached action complement.
            # Preserve such `with` complements; do not delete obligation content.
            if field == "constraints" and marker in temporal:
                boundaries = [n["begin"] for n in nodes if n["label"] == "PP"
                              and node["begin"] < n["begin"] < node["end"]
                              and n["end"] <= node["end"]
                              and str(tokens[n["begin"]]["word"]).casefold() == "with"]
                if boundaries:
                    indexes = [i for i in indexes if i < min(boundaries)]
                    while indexes and tokens[indexes[-1]]["pos"] in {"CC", ","}:
                        indexes.pop()
            if indexes and indexes not in found[field]:
                found[field].append(indexes)
    return found


def replace_scopes(clause, sentence, text, markers):
    from bpc_hybrid.stage3_reproduction_repairs_v1 import source_segments
    out = copy.deepcopy(clause)
    scopes = scope_indexes(sentence, markers)
    span = clause.get("clause_span") or clause["span"]
    for field, matches in scopes.items():
        out[field] = []
        for indexes in matches:
            segments = source_segments(text, sentence["tokens"], indexes)
            a, b = segments[0]["start"], segments[-1]["end"]
            if span["start"] <= a < b <= span["end"]:
                out[field].append({"start": a, "end": b, "text": text[a:b],
                                   "route": "constituent_prefix_scope_v2"})
    out["scope_repair_audit"] = {"legacy_scopes_reused": False,
                                 "scope_reference_states_used": False}
    return out
