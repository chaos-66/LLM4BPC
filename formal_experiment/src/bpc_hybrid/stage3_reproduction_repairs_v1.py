"""Versioned Part 3 repairs; no benchmark labels or target mutations are inputs.

Sun VP candidates come from an actual post-Tsurgeon constituency tree. Removed
tokens remain explicit gaps, represented as separate original source segments.
Ownership uses dependencies between existing NP/VP candidates, never Gold.
The historical modality/scope results are retained, so this is a repair study,
not certification of a complete final-paper Sun reproduction.
"""
from __future__ import annotations

import copy
import re


DOMAIN_ROLES = frozenset({"data subject", "certification body", "supervisory authority",
                          "data protection officer", "representative", "third party"})
EXECUTOR_DEPS = frozenset({"nsubj", "nsubj:pass", "obl:agent", "nmod:agent"})


def source_segments(text, tokens, indexes):
    """Never turn a discontinuous match into a false continuous source span."""
    indexes = sorted(set(indexes))
    groups = []
    for index in indexes:
        if not 0 <= index < len(tokens):
            raise ValueError("candidate token outside sentence")
        if not groups or index != groups[-1][-1] + 1:
            groups.append([index])
        else:
            groups[-1].append(index)
    segments = []
    for group in groups:
        start = int(tokens[group[0]]["characterOffsetBegin"])
        end = int(tokens[group[-1]]["characterOffsetEnd"])
        if not 0 <= start < end <= len(text):
            raise ValueError("source offsets out of range")
        segments.append({"start": start, "end": end, "text": text[start:end]})
    return segments


def accept_role(tokens, indexes, head, surfaces):
    """Require the lexical NP head, or a complete multiword role containing it."""
    if head not in indexes:
        return False
    head_lemma = str(tokens[head].get("lemma") or tokens[head]["word"]).casefold()
    if head_lemma in surfaces:
        return True
    phrase = " ".join(str(tokens[i].get("lemma") or tokens[i]["word"]).casefold()
                      for i in sorted(indexes))
    words = phrase.split()
    head_pos = sorted(indexes).index(head)
    for role in surfaces | DOMAIN_ROLES:
        parts = role.split()
        for start in range(len(words) - len(parts) + 1):
            if words[start:start + len(parts)] == parts and start <= head_pos < start + len(parts):
                return True
    return False


def mask_tokens(sentence, clause):
    start, end = clause["span"]["start"], clause["span"]["end"]
    scopes = [s for field in ("conditions", "constraints", "exceptions")
              for s in clause.get(field, [])]
    masks = []
    for i, token in enumerate(sentence["tokens"]):
        a, b = token["characterOffsetBegin"], token["characterOffsetEnd"]
        if (b <= start or a >= end or token.get("pos") == "MD"
                or any(a < s["end"] and b > s["start"] for s in scopes)):
            masks.append(i)
    return masks


def rebuild_clause(clause, text, sentence, candidates, surfaces):
    """Use maximal VP matches; retain every independent, nonnested VP."""
    out = copy.deepcopy(clause)
    tokens = sentence["tokens"]
    deps = sentence.get("basicDependencies") or []
    vps = [frozenset(c["indexes"]) for c in candidates if c["field"] == "action"]
    vps = [v for v in set(vps) if any(str(tokens[i].get("pos", "")).startswith("VB") for i in v)]
    vps = sorted((v for v in vps if not any(v < other for other in vps)), key=lambda x: min(x))
    nps = [frozenset(c["indexes"]) for c in candidates if c["field"] == "actor"]
    actions, actors, edges = [], [], []
    actor_lookup = {}
    cid = clause["clause_id"]
    for vp in vps:
        # Use surviving CoreNLP dependency head only for ownership attachment.
        heads = [i for i in vp if str(tokens[i].get("pos", "")).startswith("VB")
                 and not any(d["dependent"] - 1 == i and d["governor"] - 1 in vp
                             and str(d["dep"]) not in {"aux", "aux:pass"} for d in deps)]
        if not heads:
            heads = [min(i for i in vp if str(tokens[i].get("pos", "")).startswith("VB"))]
        kept = [i for i in vp if tokens[i].get("pos") not in {".", ",", ":", "``", "''"}]
        segments = source_segments(text, tokens, kept)
        if not segments:
            continue
        aid = f"{cid}.repair.action.{len(actions)+1}"
        action = {"id": aid, "start": segments[0]["start"], "end": segments[-1]["end"],
                  "text": text[segments[0]["start"]:segments[-1]["end"]],
                  "segments": segments, "semantic_text": " ".join(s["text"] for s in segments),
                  "route": "post_tsurgeon_tregex_vp"}
        actions.append(action)
        for dep in deps:
            if dep["governor"] - 1 not in heads or dep["dep"] not in EXECUTOR_DEPS:
                continue
            head = dep["dependent"] - 1
            possible = [np for np in nps if head in np and accept_role(tokens, sorted(np), head, surfaces)]
            if not possible:
                continue
            np = min(possible, key=lambda x: (len(x), min(x)))
            key = tuple(sorted(np))
            if key not in actor_lookup:
                segs = source_segments(text, tokens, key)
                actor_id = f"{cid}.repair.actor.{len(actors)+1}"
                actors.append({"id": actor_id, "start": segs[0]["start"], "end": segs[-1]["end"],
                               "text": text[segs[0]["start"]:segs[-1]["end"]], "segments": segs})
                actor_lookup[key] = actor_id
            edges.append({"actor_id": actor_lookup[key], "action_id": aid})
    out.update(actions=actions, actors=actors, actor_action_map=edges)
    out["repair_audit"] = {"algorithm": "post_tsurgeon_vp_np_v1", "action_count": len(actions),
                           "actor_count": len(actors), "modality_scope_reused": True}
    return out


def span_text(span, source):
    segments = span.get("segments") or [span]
    previous = -1
    texts = []
    for seg in segments:
        a, b = seg["start"], seg["end"]
        if not 0 <= a < b <= len(source) or a < previous:
            raise ValueError("invalid or unordered source segments")
        if "text" in seg and source[a:b] != seg["text"]:
            raise ValueError("source segment text drift")
        texts.append(source[a:b])
        previous = b
    return " ".join(texts)


def convert_segmented(record, source, rule_id, nlp, adapter):
    """Same lossless converter for repaired Sun and unchanged LLM-SE records."""
    actions, actors, pairs, elements = [], [], [], []
    for clause in record.get("clauses", []):
        if clause.get("modality", {}).get("label") != "obligation":
            continue
        aa, ar = {}, {}
        for field, target, lookup in (("actions", actions, aa), ("actors", actors, ar)):
            for span in clause.get(field, []):
                surface = span_text(span, source)
                lookup[span["id"]] = surface
                target.append(surface)
                if field == "actions":
                    elements.append({"action_id": span["id"], "text": surface,
                                     "start": span["start"], "end": span["end"],
                                     "clause_id": clause["clause_id"]})
        for edge in clause.get("actor_action_map", []):
            if edge.get("actor_id") in ar and edge.get("action_id") in aa:
                pairs.append({"actor": ar[edge["actor_id"]], "action": aa[edge["action_id"]]})
    from bpc_hybrid.stage3_v2.action_order_projection_v2 import normalize_native_order_relations
    native = normalize_native_order_relations(record, {e["action_id"]:e["text"] for e in elements})
    order = adapter.project(source, record, nlp=nlp, rule_id=rule_id,
                            action_elements=elements, native_relations=native)
    return {"rule_id":rule_id, "actions":actions, "actors":actors, "actor_action_pairs":pairs,
            "order_relations":[[e["before_text"],e["after_text"]] for e in order.get("edges", [])],
            "failed":False, "failure_reasons":[],
            "conversion_audit":{"schema_version":"source_segment_converter@1.0.0", "order_projection":order}}


def align_winter_model(model):
    """Filter nodes and labels together, retaining correct control-flow IDs."""
    changed = 0
    for process in model.processes:
        nodes = process.obligation_list
        kept = [n for n in nodes if re.search(r".+", n.getAttribute("name"))]
        if len(kept) != len(process.obligation_list_labels_lemmatized):
            raise ValueError("Winter labels do not correspond to named nodes")
        changed += len(nodes) - len(kept)
        process.obligation_list = kept
    model.obligations = {}
    model.lemmatized_obligations = {}
    for process in model.processes:
        key = process.participant
        model.obligations.setdefault(key, []).extend(process.obligation_list)
        model.lemmatized_obligations.setdefault(key, []).extend(process.obligation_list_labels_lemmatized)
    return changed
