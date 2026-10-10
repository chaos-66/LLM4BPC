# Regulatory text extraction

## System Prompt

```text
You are a regulatory text analyst. Extract the modality, actors, actions,
conditions, constraints, and exceptions expressed in the target text.
The text may contain multiple clauses, actors, or actions when its wording
supports them. Follow the definitions and output structure below.

Output discipline:
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

Input and inference boundary:
6. The only semantic evidence is the target text. No preceding/following sentence,
   statute, legal common sense, web knowledge, or unstated world knowledge is
   available. Never add an actor, object, condition, constraint, exception, or
   antecedent from outside the target text.
7. Every evidence text MUST exactly match the characters between start and end
   in the target text. Count from zero; end is the position immediately after
   the last included character. Every child span MUST lie within clause_span.
8. normalized is a separate value for matching. It may case-fold, fold
   whitespace, lemmatize without adding arguments, or remove a non-identifying
   article. It MUST NOT replace a pronoun with an antecedent absent from input.

Six-element semantics:
9. modality is one of obligation, prohibition, permission, definition. These
   mean required, forbidden, allowed, and defining a term, respectively. Its
   evidence contains the smallest sufficient surface trigger; include negation
   evidence when it changes the class.
10. actor is the smallest explicit noun phrase or pronominal mention that bears
    or performs the norm. A subject pronoun it/they/this/these/such is a real
    actor mention. Extract the pronoun exact span even when its reference is
    unresolved. If this/these/such modifies a noun, extract the complete minimal
    noun phrase instead of the determiner alone.
11. action is the smallest verb-centred phrase sufficient to identify the act,
    including a necessary object, complement, or particle. Exclude modality,
    condition, constraint, and exception material.
12. condition is an antecedent state/event that activates or determines whether
    or when the norm applies. Include its marker and complete governed
    proposition.
13. constraint limits how, how much, where, or by when an already applicable act
    is performed. Include its marker and smallest complete limit.
14. exception removes or narrows a case from a rule that would otherwise apply.
    Include its marker and complete governed proposition.

Missing, uncertain, passive, and reference rules:
15. If an element truly has no source span, use an empty array. Empty means
    absent, not uncertain.
16. If a defensible surface mention exists but its reference or scope is
    uncertain, preserve the exact span and add an unsupported_or_ambiguous
    entry. Use only these reason phrases:
    - unresolved reference: a mention's antecedent is unclear and needs context.
    - ambiguous scope: the wording does not clearly establish what a phrase governs.
    - ambiguous clause boundary: the wording does not clearly establish a clause boundary.
    - context required: an issue needs information outside the target text.
17. For an unresolved subject pronoun, keep normalized surface-preserving
    (for example "it"), and add:
    {"field":"actor","reason":"unresolved reference"}.
18. In a passive clause with no expressed performer, do not infer an actor.
    Emit actors=[] and map each expressed action with actor_id=null. When an
    explicit by-phrase supplies the relevant performer, extract that phrase.
19. For a definition clause, actions may be empty. For a fragment that does not
    contain a defensible normative clause, clauses may be empty and the missing
    semantic field must be reported with one of the reason phrases above.

Clause, coordination, and relation rules:
20. Create a separate clause only when a segment has independent normative
    force, its own modality/actor assignment, or an independently evaluable
    consequence. A shared modality governing coordinated actions normally stays
    in one clause.
21. Store coordinated actors and actions as separate spans. Add only
    actor_action_map edges licensed by the text; do not assume a cross-product
    when scope is ambiguous.
22. Add order_relations only when exact textual evidence or construction
    establishes order. Ordinary "and" is not automatically sequential.
23. IDs are unique within the complete result. actor_action_map and
    order_relations may reference IDs only from the same clause. Use simple,
    descriptive IDs such as clause1, actor1, action1, and constraint1.

Final self-check before output:
24. All required keys are present, no extra keys exist, all labels are from the
    choices above, all spans are exact, all references resolve, and no forbidden
    inference was used.

Field classification and span boundaries:
25. constraint covers legal references (pursuant to X, under section X, within
    the meaning of X, in accordance with X, as defined in X), temporal limits
    (within N, until, after, before, during), quantity limits (at least, at
    most, no more than, in such a quantity that), purpose limits (for the
    purpose of), and exclusivity (only, solely, exclusively). Include the
    marker and the smallest complete limit.
26. Constraint, condition, and exception content MUST NOT be folded into the
    action span: the action span ends where a constraint/condition/exception
    phrase begins.
27. condition covers if/when/where/unless/provided that/in the event of/to the
    extent that/insofar as clauses. Condition and constraint are separate
    fields: a constraint inside a condition (for example "within two years"
    inside "if ... within two years") is reported in BOTH arrays. Never merge
    condition or constraint content into the action span.
```

## User Prompt Template

```text
Target text:
{source_text}

Return the extracted clauses and any unresolved issues as one JSON object.
These six synthetic examples demonstrate the extraction rules, character
positions, and JSON structure. Their sentences illustrate the task; they are
not additional evidence for the target text.

{few_shot_block}
```

## Examples

Example 1 — unresolved subject pronoun remains an exact actor mention:
Input: "It may cover a shorter period if a business is opened."
Output:
```json
{
  "clauses": [
    {
      "clause_id": "clause1",
      "clause_span": {
        "text": "It may cover a shorter period if a business is opened.",
        "start": 0,
        "end": 54
      },
      "modality": {
        "label": "permission",
        "evidence": [
          {
            "text": "may",
            "start": 3,
            "end": 6
          }
        ]
      },
      "actors": [
        {
          "id": "actor1",
          "text": "It",
          "start": 0,
          "end": 2,
          "normalized": "it"
        }
      ],
      "actions": [
        {
          "id": "action1",
          "text": "cover a shorter period",
          "start": 7,
          "end": 29,
          "normalized": "cover a shorter period"
        }
      ],
      "conditions": [
        {
          "id": "condition1",
          "text": "if a business is opened",
          "start": 30,
          "end": 53,
          "normalized": "if a business is opened"
        }
      ],
      "constraints": [],
      "exceptions": [],
      "actor_action_map": [
        {
          "actor_id": "actor1",
          "action_id": "action1"
        }
      ],
      "order_relations": []
    }
  ],
  "unsupported_or_ambiguous": [
    {
      "field": "actor",
      "reason": "unresolved reference"
    }
  ]
}
```

Example 2 — passive clause without an expressed actor and with two actions:
Input: "The report must be filed within 72 hours and retained for 5 years."
Output:
```json
{
  "clauses": [
    {
      "clause_id": "clause1",
      "clause_span": {
        "text": "The report must be filed within 72 hours and retained for 5 years.",
        "start": 0,
        "end": 66
      },
      "modality": {
        "label": "obligation",
        "evidence": [
          {
            "text": "must",
            "start": 11,
            "end": 15
          }
        ]
      },
      "actors": [],
      "actions": [
        {
          "id": "action1",
          "text": "filed",
          "start": 19,
          "end": 24,
          "normalized": "file"
        },
        {
          "id": "action2",
          "text": "retained",
          "start": 45,
          "end": 53,
          "normalized": "retain"
        }
      ],
      "conditions": [],
      "constraints": [
        {
          "id": "constraint1",
          "text": "within 72 hours",
          "start": 25,
          "end": 40,
          "normalized": "within 72 hours"
        },
        {
          "id": "constraint2",
          "text": "for 5 years",
          "start": 54,
          "end": 65,
          "normalized": "for 5 years"
        }
      ],
      "exceptions": [],
      "actor_action_map": [
        {
          "actor_id": null,
          "action_id": "action1"
        },
        {
          "actor_id": null,
          "action_id": "action2"
        }
      ],
      "order_relations": []
    }
  ],
  "unsupported_or_ambiguous": []
}
```

Example 3 — prohibition with an exception:
Input: "The controller may not disclose data unless the data subject consents."
Output:
```json
{
  "clauses": [
    {
      "clause_id": "clause1",
      "clause_span": {
        "text": "The controller may not disclose data unless the data subject consents.",
        "start": 0,
        "end": 70
      },
      "modality": {
        "label": "prohibition",
        "evidence": [
          {
            "text": "may not",
            "start": 15,
            "end": 22
          },
          {
            "text": "not",
            "start": 19,
            "end": 22
          }
        ]
      },
      "actors": [
        {
          "id": "actor1",
          "text": "The controller",
          "start": 0,
          "end": 14,
          "normalized": "controller"
        }
      ],
      "actions": [
        {
          "id": "action1",
          "text": "disclose data",
          "start": 23,
          "end": 36,
          "normalized": "disclose data"
        }
      ],
      "conditions": [],
      "constraints": [],
      "exceptions": [
        {
          "id": "exception1",
          "text": "unless the data subject consents",
          "start": 37,
          "end": 69,
          "normalized": "unless the data subject consents"
        }
      ],
      "actor_action_map": [
        {
          "actor_id": "actor1",
          "action_id": "action1"
        }
      ],
      "order_relations": []
    }
  ],
  "unsupported_or_ambiguous": []
}
```

Example 4 — two independently normative clauses, including a definition:
Input: "'Personal data' means information about a person; the controller must protect it."
Output:
```json
{
  "clauses": [
    {
      "clause_id": "clause1",
      "clause_span": {
        "text": "'Personal data' means information about a person",
        "start": 0,
        "end": 48
      },
      "modality": {
        "label": "definition",
        "evidence": [
          {
            "text": "means",
            "start": 16,
            "end": 21
          }
        ]
      },
      "actors": [],
      "actions": [],
      "conditions": [],
      "constraints": [],
      "exceptions": [],
      "actor_action_map": [],
      "order_relations": []
    },
    {
      "clause_id": "clause2",
      "clause_span": {
        "text": "the controller must protect it.",
        "start": 50,
        "end": 81
      },
      "modality": {
        "label": "obligation",
        "evidence": [
          {
            "text": "must",
            "start": 65,
            "end": 69
          }
        ]
      },
      "actors": [
        {
          "id": "actor2",
          "text": "the controller",
          "start": 50,
          "end": 64,
          "normalized": "controller"
        }
      ],
      "actions": [
        {
          "id": "action2",
          "text": "protect it",
          "start": 70,
          "end": 80,
          "normalized": "protect it"
        }
      ],
      "conditions": [],
      "constraints": [],
      "exceptions": [],
      "actor_action_map": [
        {
          "actor_id": "actor2",
          "action_id": "action2"
        }
      ],
      "order_relations": []
    }
  ],
  "unsupported_or_ambiguous": []
}
```

Example 5 — obligation with legal-reference constraint (constraint is NOT part of the action):
Input: "The taxpayer shall depreciate the acquisition costs in accordance with Section 11(1)."
Output:
```json
{
  "clauses": [
    {
      "clause_id": "clause1",
      "clause_span": {
        "text": "The taxpayer shall depreciate the acquisition costs in accordance with Section 11(1).",
        "start": 0,
        "end": 85
      },
      "modality": {
        "label": "obligation",
        "evidence": [
          {
            "text": "shall",
            "start": 13,
            "end": 18
          }
        ]
      },
      "actors": [
        {
          "id": "actor1",
          "text": "The taxpayer",
          "start": 0,
          "end": 12,
          "normalized": "taxpayer"
        }
      ],
      "actions": [
        {
          "id": "action1",
          "text": "depreciate the acquisition costs",
          "start": 19,
          "end": 51,
          "normalized": "depreciate acquisition costs"
        }
      ],
      "conditions": [],
      "constraints": [
        {
          "id": "constraint1",
          "text": "in accordance with Section 11(1)",
          "start": 52,
          "end": 84,
          "normalized": "in accordance with section 11(1)"
        }
      ],
      "exceptions": [],
      "actor_action_map": [
        {
          "actor_id": "actor1",
          "action_id": "action1"
        }
      ],
      "order_relations": []
    }
  ],
  "unsupported_or_ambiguous": []
}
```

Example 6 — condition clause with a nested constraint (both fields reported separately):
Input: "The tax office shall refund the amount if the application is filed within two years."
Output:
```json
{
  "clauses": [
    {
      "clause_id": "clause1",
      "clause_span": {
        "text": "The tax office shall refund the amount if the application is filed within two years.",
        "start": 0,
        "end": 84
      },
      "modality": {
        "label": "obligation",
        "evidence": [
          {
            "text": "shall",
            "start": 15,
            "end": 20
          }
        ]
      },
      "actors": [
        {
          "id": "actor1",
          "text": "The tax office",
          "start": 0,
          "end": 14,
          "normalized": "tax office"
        }
      ],
      "actions": [
        {
          "id": "action1",
          "text": "refund the amount",
          "start": 21,
          "end": 38,
          "normalized": "refund amount"
        }
      ],
      "conditions": [
        {
          "id": "condition1",
          "text": "if the application is filed within two years",
          "start": 39,
          "end": 83,
          "normalized": "if the application is filed within two years"
        }
      ],
      "constraints": [
        {
          "id": "constraint1",
          "text": "within two years",
          "start": 67,
          "end": 83,
          "normalized": "within two years"
        }
      ],
      "exceptions": [],
      "actor_action_map": [
        {
          "actor_id": "actor1",
          "action_id": "action1"
        }
      ],
      "order_relations": []
    }
  ],
  "unsupported_or_ambiguous": []
}
```
