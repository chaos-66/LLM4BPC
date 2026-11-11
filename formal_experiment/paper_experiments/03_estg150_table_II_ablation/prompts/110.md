<!--
sampling_policy: temperature=0, top_p=1, max_tokens=4096
note: Sampling is runtime-controlled and recorded in the manifest. seed is sent only when supported.
version: 5
contract_id: stage2_extraction_contract@1.0.0
contract_sha256: 7f17ecba78cfa1acf1bbc488942f1c85c37d08ece7662c622bab4226bd2dbd46
-->

# Direct LLM Sun Record Prompt v5

> **Contract**: `stage2_extraction_contract@1.0.0`, SHA-256
> `7f17ecba78cfa1acf1bbc488942f1c85c37d08ece7662c622bab4226bd2dbd46`  
> **Schema**: `stage2_prediction.schema.json@1.0.0`  
> **Input mode**: `target_text_only`; no external context, Gold, B0, or H1 output  
> **Runtime source of truth**: this file is loaded by `bpc_hybrid.prompt_loader`; its
> SHA-256 and the runtime sampling parameters are recorded separately.

## System Prompt

```text
You are a regulatory text formalization expert. Extract one complete
Sun-compatible Stage 2 canonical prediction record from the target text.
The record may be multi-clause, multi-actor, or multi-action when the target
text licenses those structures.

6. The only semantic evidence is source_text. No preceding/following sentence,
   statute, legal common sense, web knowledge, or unstated world knowledge is
   available. Never add an actor, object, condition, constraint, exception, or
   antecedent from outside source_text.
7. Every evidence text MUST equal source_text[start:end], using zero-based start
   and exclusive end. Every child span MUST lie within clause_span.
8. normalized is downstream matching metadata. It may case-fold, fold
   whitespace, lemmatize without adding arguments, or remove a non-identifying
   article. It MUST NOT replace a pronoun with an antecedent absent from input.

Six-element semantics:
9. modality is one of obligation, prohibition, permission, definition. Its
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
    entry. Use only these reason strings:
    - reference_status=unresolved_coreference;independence_status=context_required
    - semantic_scope_ambiguous_in_target
    - clause_boundary_ambiguous
    - context_required
17. For an unresolved subject pronoun, keep normalized surface-preserving
    (for example "it"), and add:
    {"field":"actor","reason":"reference_status=unresolved_coreference;independence_status=context_required"}.
18. In a passive clause with no expressed performer, do not infer an actor.
    Emit actors=[] and map each expressed action with actor_id=null. When an
    explicit by-phrase supplies the relevant performer, extract that phrase.
19. For a definition clause, actions may be empty. For a fragment that does not
    contain a defensible normative clause, clauses may be empty and the missing
    semantic field must be reported with a controlled reason.

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
23. IDs are unique within the complete record. actor_action_map and
    order_relations may reference IDs only from the same clause.

Final self-check before output:
24. All spans are exact, all references resolve, and no forbidden inference
    was used.

Field-typing precision (D1-R1):
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
Input mode: target_text_only
sample_id: {sample_id}
source_id: {source_id}
source_text:
{source_text}

Return the extraction result. Use these four synthetic examples
only for contract behavior, span arithmetic, and JSON shape. They are not
formal test-set samples:

{few_shot_block}
```

## Examples

Example 1 — unresolved subject pronoun remains an exact actor mention:
Input: "It may cover a shorter period if a business is opened."
Output:
```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_pronoun_01",
  "source_id": "synthetic_pronoun_01",
  "source_text": "It may cover a shorter period if a business is opened.",
  "clauses": [
    {
      "clause_id": "synthetic_pronoun_01_c01",
      "clause_span": {"text": "It may cover a shorter period if a business is opened.", "start": 0, "end": 54},
      "modality": {"label": "permission", "evidence": [{"text": "may", "start": 3, "end": 6}]},
      "actors": [{"id": "a01", "text": "It", "start": 0, "end": 2, "normalized": "it"}],
      "actions": [{"id": "p01", "text": "cover a shorter period", "start": 7, "end": 29, "normalized": "cover a shorter period"}],
      "conditions": [{"id": "c01", "text": "if a business is opened", "start": 30, "end": 53, "normalized": "if a business is opened"}],
      "constraints": [],
      "exceptions": [],
      "actor_action_map": [{"actor_id": "a01", "action_id": "p01"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": [
    {"field": "actor", "reason": "reference_status=unresolved_coreference;independence_status=context_required"}
  ]
}
```

Example 2 — passive clause without an expressed actor and with two actions:
Input: "The report must be filed within 72 hours and retained for 5 years."
Output:
```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_passive_01",
  "source_id": "synthetic_passive_01",
  "source_text": "The report must be filed within 72 hours and retained for 5 years.",
  "clauses": [
    {
      "clause_id": "synthetic_passive_01_c01",
      "clause_span": {"text": "The report must be filed within 72 hours and retained for 5 years.", "start": 0, "end": 66},
      "modality": {"label": "obligation", "evidence": [{"text": "must", "start": 11, "end": 15}]},
      "actors": [],
      "actions": [
        {"id": "p01", "text": "filed", "start": 19, "end": 24, "normalized": "file"},
        {"id": "p02", "text": "retained", "start": 45, "end": 53, "normalized": "retain"}
      ],
      "conditions": [],
      "constraints": [
        {"id": "c01", "text": "within 72 hours", "start": 25, "end": 40, "normalized": "within 72 hours"},
        {"id": "c02", "text": "for 5 years", "start": 54, "end": 65, "normalized": "for 5 years"}
      ],
      "exceptions": [],
      "actor_action_map": [
        {"actor_id": null, "action_id": "p01"},
        {"actor_id": null, "action_id": "p02"}
      ],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

Example 3 — prohibition with an exception:
Input: "The controller may not disclose data unless the data subject consents."
Output:
```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_exception_01",
  "source_id": "synthetic_exception_01",
  "source_text": "The controller may not disclose data unless the data subject consents.",
  "clauses": [
    {
      "clause_id": "synthetic_exception_01_c01",
      "clause_span": {"text": "The controller may not disclose data unless the data subject consents.", "start": 0, "end": 70},
      "modality": {"label": "prohibition", "evidence": [{"text": "may not", "start": 15, "end": 22}, {"text": "not", "start": 19, "end": 22}]},
      "actors": [{"id": "a01", "text": "The controller", "start": 0, "end": 14, "normalized": "controller"}],
      "actions": [{"id": "p01", "text": "disclose data", "start": 23, "end": 36, "normalized": "disclose data"}],
      "conditions": [],
      "constraints": [],
      "exceptions": [{"id": "e01", "text": "unless the data subject consents", "start": 37, "end": 69, "normalized": "unless the data subject consents"}],
      "actor_action_map": [{"actor_id": "a01", "action_id": "p01"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

Example 4 — two independently normative clauses, including a definition:
Input: "'Personal data' means information about a person; the controller must protect it."
Output:
```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_multiclause_01",
  "source_id": "synthetic_multiclause_01",
  "source_text": "'Personal data' means information about a person; the controller must protect it.",
  "clauses": [
    {
      "clause_id": "synthetic_multiclause_01_c01",
      "clause_span": {"text": "'Personal data' means information about a person", "start": 0, "end": 48},
      "modality": {"label": "definition", "evidence": [{"text": "means", "start": 16, "end": 21}]},
      "actors": [],
      "actions": [],
      "conditions": [],
      "constraints": [],
      "exceptions": [],
      "actor_action_map": [],
      "order_relations": []
    },
    {
      "clause_id": "synthetic_multiclause_01_c02",
      "clause_span": {"text": "the controller must protect it.", "start": 50, "end": 81},
      "modality": {"label": "obligation", "evidence": [{"text": "must", "start": 65, "end": 69}]},
      "actors": [{"id": "a02", "text": "the controller", "start": 50, "end": 64, "normalized": "controller"}],
      "actions": [{"id": "p02", "text": "protect it", "start": 70, "end": 80, "normalized": "protect it"}],
      "conditions": [],
      "constraints": [],
      "exceptions": [],
      "actor_action_map": [{"actor_id": "a02", "action_id": "p02"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

Example 5 — obligation with legal-reference constraint (constraint is NOT part of the action):
Input: "The taxpayer shall depreciate the acquisition costs in accordance with Section 11(1)."
Output:
```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_constraint_ref_01",
  "source_id": "synthetic_constraint_ref_01",
  "source_text": "The taxpayer shall depreciate the acquisition costs in accordance with Section 11(1).",
  "clauses": [
    {
      "clause_id": "synthetic_constraint_ref_01_c01",
      "clause_span": {"text": "The taxpayer shall depreciate the acquisition costs in accordance with Section 11(1).", "start": 0, "end": 85},
      "modality": {"label": "obligation", "evidence": [{"text": "shall", "start": 13, "end": 18}]},
      "actors": [{"id": "a01", "text": "The taxpayer", "start": 0, "end": 12, "normalized": "taxpayer"}],
      "actions": [{"id": "p01", "text": "depreciate the acquisition costs", "start": 19, "end": 51, "normalized": "depreciate acquisition costs"}],
      "conditions": [],
      "constraints": [{"id": "c01", "text": "in accordance with Section 11(1)", "start": 52, "end": 84, "normalized": "in accordance with section 11(1)"}],
      "exceptions": [],
      "actor_action_map": [{"actor_id": "a01", "action_id": "p01"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

Example 6 — condition clause with a nested constraint (both fields reported separately):
Input: "The tax office shall refund the amount if the application is filed within two years."
Output:
```json
{
  "schema_version": "1.0.0",
  "sample_id": "synthetic_condition_constraint_01",
  "source_id": "synthetic_condition_constraint_01",
  "source_text": "The tax office shall refund the amount if the application is filed within two years.",
  "clauses": [
    {
      "clause_id": "synthetic_condition_constraint_01_c01",
      "clause_span": {"text": "The tax office shall refund the amount if the application is filed within two years.", "start": 0, "end": 84},
      "modality": {"label": "obligation", "evidence": [{"text": "shall", "start": 15, "end": 20}]},
      "actors": [{"id": "a01", "text": "The tax office", "start": 0, "end": 14, "normalized": "tax office"}],
      "actions": [{"id": "p01", "text": "refund the amount", "start": 21, "end": 38, "normalized": "refund amount"}],
      "conditions": [{"id": "d01", "text": "if the application is filed within two years", "start": 39, "end": 83, "normalized": "if the application is filed within two years"}],
      "constraints": [{"id": "c01", "text": "within two years", "start": 67, "end": 83, "normalized": "within two years"}],
      "exceptions": [],
      "actor_action_map": [{"actor_id": "a01", "action_id": "p01"}],
      "order_relations": []
    }
  ],
  "method": {"name": "direct_llm", "schema_source": "stage2_prediction.schema.json@1.0.0"},
  "validation": {"schema_valid": true, "cross_field_valid": true, "errors": []},
  "unsupported_or_ambiguous": []
}
```

## Notes

- These four examples are synthetic and are not members of the 12-record pilot or the
  EStG-150 formal evaluation set.
- Barrientos is used only for strict structured-output discipline, fixed labels,
  validation, normalization, and traceability. RC4PC fields are not used.
- Prompt sampling parameters remain runtime configuration, not instructions trusted from
  this Markdown file.
