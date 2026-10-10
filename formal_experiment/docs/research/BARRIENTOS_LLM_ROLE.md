# Barrientos 2026 LLM Role

This document locks the role of the Barrientos et al. (2026) paper in this
experiment.

## Terminology

When this project says "the LLM paper", it means:

Barrientos, Winter, and Rinderle-Ma (2026), "Impact analysis of regulatory
requirement changes on business process compliance".

This is different from Winter et al. (2020), which is the textual compliance
assessment baseline compared by Sun.

## Main Rule

Sun is the main methodological backbone.

Barrientos 2026 is a **direct engineering-method reference** for LLM structured
output, schema validation, controlled vocabularies, traceability, and
evaluation discipline. Its discussion of normalization is an improvement
motivation, not evidence that it implements this project's post-processing.
It is not the project's task/schema backbone and must
not replace Sun's rule-record representation, Sun's Stage 2 extraction targets,
or Sun's Stage 3 checking goal.

Source-fidelity rule (verified against the paper on 2026-08-20): keep the paper's
automated RC4PC evaluation separate from the artifact's expert-annotation
protocol. The paper evaluates 36 requirements and repeats the complete approach
five times; the artifact's 20 requirements x 2 versions x 2 experts = 80 records
are annotations, not 20 x 20 LLM stability runs.

## What We Borrow From Barrientos

Allowed Barrientos-inspired ideas:

- LLM-based formalization from natural-language requirements into structured
  output.
- Detailed extraction instructions in the prompt.
- Strict JSON schema.
- Controlled vocabulary for allowed labels.
- Validation of every LLM output against the schema.
- Motivation to reduce inconsistent representations; the paper's evaluation
  in Section 6.2 reports that its outputs required no additional normalization
  or manual post-processing.
- Traceability of what the LLM added or repaired.
- Future optional ideas for compliance deviation explanations and
  over-compliance analysis.

### Concrete post-processing belongs to this project

The canonical validator, relay-format adapter, exact-text coordinate repair,
repeated-occurrence assignment, local filtering, and dangling-reference cleanup
are project implementations for the Sun-compatible rule-record interface.
Do not attribute that complete pipeline or the name "Canonical Validation" to
Barrientos. Sections 5 and 6.2 of the original paper distinguish implemented
JSON-schema validation from normalization discussed as a further need.

For each project step, explain the observed error or predefined format rule,
the resulting interface problem, why the operation was chosen, its evidence,
and its limits. D1-R1 nested-output diagnostics motivated format adaptation;
earlier project coordinate forensics motivated unique exact-text repair; later
retrospective error attribution motivated repeated-occurrence recovery.
Schema and cross-field checks are predefined integrity requirements and must
not be presented as if every check arose from a separately measured error.
The later development repair does not explain or replace the frozen Table 1
results. The motivation and evidence mapping is in `paper/THESIS_DRAFT.md`
Section 4.2.2; historical runs and their results remain unchanged.

## Exact Schema Mapping

Barrientos/RC4PC does not directly extract Sun's six phrase concepts. Its
formalization contains a Boolean `precondition`, a list of `norms` with
`modality` and `action`, and `temporal_validity`. Each action is assigned to a
control-flow, data, resource, or time dimension and a controlled compliance
pattern.

### Critical: Modality Class Count Difference (verified 2026-07-12)

| Aspect | Barrientos (RC4PC) | Sun et al. (2024) / Our D1 |
|---|---|---|
| Modality classes | **3** | **4** |
| Enum | `obligation`, `permission`, `prohibition` | `obligation`, `prohibition`, `permission`, `definition` |
| `definition` class | ❌ absent | ✅ required (e.g., "X means...", "X refers to...") |

**Implication**: D1/H1 prompts MUST use the 4-class Sun enum, NOT the
3-class Barrientos enum. Direct copy-paste of Barrientos prompt loses the
`definition` class and breaks Sun-compatible narrative. Full audit in
`docs/research/BARRIENTOS_BORROWING_AUDIT_2026-07-12.md`.

The only allowed adaptation is explicit rather than implicit:

| Sun concept | Closest RC4PC construct | Required extension |
|---|---|---|
| modality | `norms[].modality` | source evidence span |
| actor | resource action / `resources` | separate participant from physical resource |
| action | `activities` | preserve the original verb phrase span |
| condition | `precondition` | preserve marker, scope, and source span |
| constraint | pattern plus data/time arguments | preserve the limiting source span |
| exception | no first-class equivalent | add an explicit exception field |

Consequently, the thesis must not state that Barrientos already provides a
method for extracting Sun's six elements. It provides prompting, schema
validation, and stability methodology that can be adapted to a Sun-compatible
output, plus a motivation for further normalization. Concrete normalization
and coordinate-repair operations must be attributed to this project's code.

## What We Do Not Borrow

Not allowed:

- Replacing Sun's semantic concepts with the Barrientos/RC4PC schema.
- Turning the thesis into a regulatory requirement change-impact study.
- Making atomic change operations the main Stage 2 target.
- Using compliance deviation explanations as the primary evaluation objective.
- Calling the main method "Barrientos method".

## Formal Experiment Meaning

The formal method remains:

1. Run Sun or Sun-reconstructed Stage 2 extraction first.
2. If the rule extractor fails, misses required fields, has low confidence, or
   cannot be converted into a Stage 3 record, call the LLM.
3. The LLM output must be validated and normalized.
4. The final record must remain Sun-compatible.

The comparison variants are:

- `sun_rule_only`
- `sun_llm_fallback`
- `direct_llm`

The `sun_llm_fallback` and `direct_llm` variants may use
Barrientos-inspired prompting and validation discipline, but they must output
Sun-compatible fields.

## Legacy Naming Warning

Some old project files use names such as `sun_plus_winter` or
`winter_formalizer`. Those names are historical and misleading.

For formal reporting, treat them as legacy structured-LLM prototypes only. They
must be renamed, replaced, or clearly documented before final metrics are
reported.
