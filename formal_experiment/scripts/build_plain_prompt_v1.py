"""Build the readable prompt from frozen v6, without editing historical files.

Offline only. Builds the model-facing prompt, never a prediction or metric.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "prompts/sun_compat/direct_llm_sun_record_prompt_v6_d1r1_2026_08_05.md"
TARGET = ROOT / "prompts/sun_compat/plain_v1/direct_llm_plain_record_prompt_v1.md"

REASONS = {
    "reference_status=unresolved_coreference;independence_status=context_required": "unresolved reference",
    "semantic_scope_ambiguous_in_target": "ambiguous scope",
    "clause_boundary_ambiguous": "ambiguous clause boundary",
    "context_required": "context required",
}

OUTPUT_RULES = """Output discipline:
1. Return ONLY one valid JSON object. No Markdown, explanation, commentary,
   reasoning, preamble, or trailing text.
2. Use exactly two top-level keys: clauses and unsupported_or_ambiguous.
   clauses is the list of extracted normative clauses.
   unsupported_or_ambiguous is the list of fields you cannot fully determine.
3. Each clause has these keys: clause_id, clause_span, modality, actors,
   actions, conditions, constraints, exceptions, actor_action_map,
   order_relations. clause_id identifies the clause. clause_span records its
   original text and character positions. modality contains label and evidence.
   actors, actions, conditions, constraints, and exceptions are arrays of spans.
4. clause_span and each evidence span have text, start, and end. Each element
   span also has id and normalized. id identifies that element. normalized is
   a simplified wording for matching, subject to the rules below.
   Each actor_action_map entry has actor_id and action_id: it states who
   performs which action. Each order_relations entry has before_action_id,
   after_action_id, and evidence: it states which action precedes which other
   action and gives the original wording that establishes the order.
5. Each unsupported_or_ambiguous entry has field and reason. field names the
   affected element or relation: modality, actor, action, condition, constraint,
   exception, actor_action_map, or order_relations. Use the readable reasons
   described below. Use an empty list when there is no unresolved issue.

"""


def render() -> str:
    base = SOURCE.read_text(encoding="utf-8")
    system = re.search(r"## System Prompt\s*```text\n(.*?)\n```", base, re.S).group(1)
    system = (
        "You are a regulatory text analyst. Extract the modality, actors, actions,\n"
        "conditions, constraints, and exceptions expressed in the target text.\n"
        "The text may contain multiple clauses, actors, or actions when its wording\n"
        "supports them. Follow the definitions and output structure below.\n\n"
        + OUTPUT_RULES
        + system[system.index("Input and inference boundary:"):]
    )
    system = system.replace("source_text", "the target text")
    system = system.replace(
        "Every evidence text MUST equal the target text[start:end], using zero-based start\n"
        "   and exclusive end.",
        "Every evidence text MUST exactly match the characters between start and end\n"
        "   in the target text. Count from zero; end is the position immediately after\n"
        "   the last included character.",
    )
    system = system.replace("normalized is downstream matching metadata.", "normalized is a separate value for matching.")
    system = system.replace(
        "definition. Its\n   evidence",
        "definition. These\n   mean required, forbidden, allowed, and defining a term, respectively. Its\n   evidence",
    )
    system = system.replace("Use only these reason strings:", "Use only these reason phrases:")
    for old, new in REASONS.items():
        system = system.replace(old, new)
    explanations = {
        "unresolved reference": "a mention's antecedent is unclear and needs context.",
        "ambiguous scope": "the wording does not clearly establish what a phrase governs.",
        "ambiguous clause boundary": "the wording does not clearly establish a clause boundary.",
        "context required": "an issue needs information outside the target text.",
    }
    for name, explanation in explanations.items():
        system = system.replace("    - " + name + "\n", "    - " + name + ": " + explanation + "\n")
    system = system.replace("must be reported with a controlled reason.", "must be reported with one of the reason phrases above.")
    system = system.replace("IDs are unique within the complete record.", "IDs are unique within the complete result.")
    system = system.replace(
        "may reference IDs only from the same clause.",
        "may reference IDs only from the same clause. Use simple,\n"
        "    descriptive IDs such as clause1, actor1, action1, and constraint1.",
    )
    system = system.replace("fixed enums", "choices above")
    system = system.replace("Field-typing precision (D1-R1):", "Field classification and span boundaries:")
    user = (
        "Target text:\n{source_text}\n\n"
        "Return the extracted clauses and any unresolved issues as one JSON object.\n"
        "These six synthetic examples demonstrate the extraction rules, character\n"
        "positions, and JSON structure. Their sentences illustrate the task; they are\n"
        "not additional evidence for the target text.\n\n{few_shot_block}"
    )
    examples = base[base.index("## Examples"):base.index("## Notes")]
    blocks = re.findall(r"(Example \d+[^\n]*\nInput:[^\n]*\nOutput:\n)```json\n(.*?)\n```", examples, re.S)
    if len(blocks) != 6:
        raise ValueError("expected all six original examples")
    parts = []
    for heading, raw in blocks:
        old = json.loads(raw)
        id_map = {}
        fields = {"actors": "actor", "actions": "action", "conditions": "condition", "constraints": "constraint", "exceptions": "exception"}
        for n, clause in enumerate(old["clauses"], 1):
            clause["clause_id"] = f"clause{n}"
            for field, prefix in fields.items():
                for span in clause[field]:
                    previous = span["id"]
                    span["id"] = prefix + str(int(re.search(r"\d+$", previous).group(0)))
                    id_map[previous] = span["id"]
        for clause in old["clauses"]:
            for edge in clause["actor_action_map"]:
                if edge["actor_id"] is not None:
                    edge["actor_id"] = id_map[edge["actor_id"]]
                edge["action_id"] = id_map[edge["action_id"]]
            for edge in clause["order_relations"]:
                for key in ("before_action_id", "after_action_id"):
                    edge[key] = id_map[edge[key]]
        for issue in old["unsupported_or_ambiguous"]:
            issue["reason"] = REASONS[issue["reason"]]
        cleaned = {key: old[key] for key in ("clauses", "unsupported_or_ambiguous")}
        parts.append(heading + "```json\n" + json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n```")
    text = (
        "# Regulatory text extraction\n\n## System Prompt\n\n```text\n"
        + system + "\n```\n\n## User Prompt Template\n\n```text\n"
        + user + "\n```\n\n## Examples\n\n" + "\n\n".join(parts) + "\n"
    )
    if re.search(r"[0-9a-f]{64}|@[0-9]|D1-R1|schema_version|schema_source|schema_valid|cross_field_valid|synthetic_", text):
        raise ValueError("internal metadata remains in the plain prompt")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = render()
    if args.check:
        if not TARGET.is_file() or TARGET.read_text(encoding="utf-8") != text:
            print("Plain prompt differs from the offline builder.")
            return 1
    else:
        if TARGET.exists():
            raise FileExistsError("refusing to overwrite an existing prompt")
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(text, encoding="utf-8", newline="\n")
    print("Plain prompt: six examples, readable instructions, no internal metadata.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
