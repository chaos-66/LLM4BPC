# LLM-SE Actor Exploratory Branch Study

Status: CLOSED  
Evidence level: DEVELOPMENT / EXPLORATORY  
Paper role: NOT PRIMARY RESULTS  
Further experiments: NOT PLANNED IN THIS BRANCH

Archive date: 2026-09-26  
Repository baseline HEAD at archive time: `3789ebb9f68fe1c9ae008f5c864eda7aad8a71bf`

This note records a completed Stage 2 Actor-related exploratory branch. It is an
archival record only: no API calls, no new experiments, no Prompt changes, no
Gold changes, no evaluator changes, and no formal-result changes were made while
producing this note.

## 1. Purpose

The branch was created only to understand:

- LLM-SE Actor field error sources;
- post-processing effects on Actor spans;
- Prompt sensitivity of Actor output behavior.

The branch is a development-only exploratory branch study. It is not the final
experimental result, does not replace the formal LLM-SE method, is not a
paper mainline method, and is not used to update formal Stage 2 main results.

## 2. Scope

Recorded completed artifacts:

- `d_span_grounding_repair_v1` span-grounding / post-processing repair study;
- `d1_actor_semantic_error_audit_v1` read-only Actor semantic error audit;
- `d1_actor_refinement_v1` four-arm Actor Prompt sensitivity development
  screening.

No Stage 2 or Stage 3 work outside these completed artifacts is recorded here.

## 3. Span Grounding Investigation

Artifact: `d_span_grounding_repair_v1`.

Research question recorded by the completed study:

> Whether repeated exact occurrences caused already-emitted Actor/spans to be
> unnecessarily deleted during canonicalization.

Changed factor:

- legacy canonicalizer;
- vs `repair_v1`.

Recorded `repair_v1` properties:

- repeated exact occurrence recovery;
- nearest original offset;
- one-to-one minimum-cost assignment;
- tie fail-safe;
- structured resolution provenance;
- Gold-blind;
- does not modify model semantic text or field assignment.

Recorded overall results:

| arm | P | R | F1 |
| --- | --- | --- | --- |
| OLD | 0.8203 | 0.7289 | 0.7719 |
| NEW | 0.8172 | 0.7479 | 0.7810 |

Recorded Actor results:

| arm | Pred | matched pred | matched Gold | P | R | F1 | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OLD | 82 | 45 | 44 | 0.5488 | 0.9167 | 0.6865 | 37 | 4 |
| NEW | 86 | 46 | 45 | 0.5349 | 0.9375 | 0.6811 | 40 | 3 |

Recorded interpretation:

- Actor Recall improved;
- Actor F1 did not improve;
- recovered spans included not only TP but also model-emitted pronoun FP.

Core recorded conclusion:

> Span grounding caused a small technical information loss, but it is not the
> main explanation for the LLM-SE Actor performance gap.

`repair_v1` was later promoted to the default canonicalizer in the repository
state. The engineering repair may remain, but the Actor-F1 analysis around it
is part of this exploratory branch.

## 4. Actor Semantic Error Audit

Artifact: `d1_actor_semantic_error_audit_v1`.

Recorded Actor metrics under `repair_v1`:

- Gold Actor = 48
- Pred = 86
- FP = 40
- FN = 3
- matched predictions = 46
- matched Gold = 45
- P = 0.5348837209
- R = 0.9375
- F1 = 0.6811451135

The three FN cases were:

- `estg_000206`
- `estg_000417`
- `estg_000776`

All three were classified as:

- `FN-B_EMBEDDED_IN_CONDITION`

Recorded interpretation:

> The Gold actor mention was already present inside the model-emitted
> condition span, but was not independently projected into `actors`. These FN
> cases are therefore closer to a field-projection gap than to a complete
> failure to see the actor mention.

Recorded FP structure:

- pronoun / demonstrative: 9
- non-role grammatical subject: 28
- legal/normative role but Gold-unannotated: 3

Recorded core observation:

> The current LLM-SE Actor Precision problem is mainly
> grammatical-subject over-extraction, and part of it is related to the
> unresolved pronoun actor policy.

## 5. Prompt Sensitivity Screening

Artifact: `d1_actor_refinement_v1`.

Completed development screening:

- B0 = unchanged fresh baseline
- R = Actor Role Eligibility
- P = Unresolved Pronoun Policy
- C = Condition Actor Projection

Scale:

- 4 arms x 150 samples = 600 sample runs.

Recorded status:

> exploratory development screening only.

This branch record does not call it a final experiment, formal experiment,
final Prompt selection, or confirmed improvement.

Recorded prompt integrity:

- `unexpected_diff_count = 0`;
- B0 is a byte-for-byte copy of the frozen full Prompt;
- each non-baseline arm changes only its pre-specified one-factor semantic
  intervention.

### 5.1 B0

Actor:

- P = 0.4891
- R = 0.9375
- F1 = 0.6429

Recorded context: B0 was the fresh unchanged baseline run in the same
development screening period.

### 5.2 R

Changed direction:

> Tighten Actor eligibility, emphasizing that grammatical subjecthood alone is
> not sufficient for Actor status; an Actor is the explicit participant that
> performs or bears an action or state relevant to the rule.

Actor:

- F1 = 0.7132
- delta vs B0 = +0.0703

Recorded observations:

- non-role grammatical-subject FP decreased;
- no obvious harmful TP removal was observed;
- other-field changes were small;
- overall development F1 rose slightly.

Recorded conclusion:

> In this single development screening, R showed a relatively clean Actor
> Precision improvement trend.

Must also be recorded:

> No subsequent replication; not used as a formal Prompt; not a final
> conclusion.

### 5.3 P

Changed direction:

> When an unresolved pronoun cannot be resolved explicitly within the current
> `source_text`, do not force it to be emitted as an Actor.

Actor:

- F1 = 0.7458
- delta vs B0 = +0.1029

Recorded observations:

- Actor Precision improved markedly;
- the original single pronoun TP was lost;
- obvious non-pronoun behavioral spillover appeared;
- constraint F1 dropped noticeably.

Recorded conclusion:

> In this single development screening, P raised Actor F1 substantially, but
> also produced clear behavioral spillover on non-pronoun Actor predictions and
> other fields; it therefore cannot be treated as a clean single-factor
> improvement.

No further judgment is recorded.

### 5.4 C

Changed direction:

> Explicit actor-eligible participants inside a condition are also projected
> independently into `actors`.

Actor:

- F1 = 0.6182
- delta vs B0 = -0.0246

Condition-contained newly projected Actor:

- TP = 1
- FP = 4
- projection precision = 0.20

Recorded conclusion:

> The current C formulation introduced more FP than benefit in this development
> screening and did not show an improvement effect.

No further optimization is recorded.

## 6. Main Observations

1. Repeated-span grounding caused a small technical information loss, but is
   not the main explanation for the Actor gap.
2. The remaining Actor FN cases in the current development run mainly appeared
   as actor mentions already inside a condition but not independently projected
   into `actors`.
3. Actor FP was largely from non-role grammatical subjects, with additional
   unresolved pronoun FP.
4. The R/P/C screening showed that Actor behavior is sensitive to Prompt
   definition.
5. R showed the relatively clean behavior in that single screening.
6. P raised Actor F1 more, but had obvious spillover.
7. The current C formulation did not show effective improvement.
8. These observations do not constitute a final Prompt choice or formal
   performance conclusion.

## 7. Research Boundaries

- Formal Stage 2 main results were not replaced.
- LLM-SE still uses its original locked results.
- The formal Prompt was not replaced.
- Formal predictions were not replaced.
- The formal Stage 2 comparison was not replaced.
- These Actor branch experiments did not change paper main results.
- Development fine-grained Actor F1 must not be merged directly with formal
  coarse-grained Actor F1; the evaluation views are different.
- No new overall-method conclusion is recorded.
- The following statements are not supported and are not recorded as
  conclusions: R is the final best Prompt; P is better than R; the Actor problem
  is solved; LLM-SE now beats Rules-Only on Actor.

## 8. Relationship to Formal Stage 2 Results

Recorded relation only:

> This branch helps understand LLM-SE Actor error sources and Prompt
> sensitivity.

These experiments are retained as development-only exploratory evidence and
are not used as the primary Stage 2 results.

Their numbers must not be placed into the paper main result table, and the paper
must not be edited to strengthen these results.

## 9. Branch Closure

Actor exploratory branch = CLOSED.

No further work was performed under this archive task.

No R replication, P replication, C refinement, combined Prompt, new ablation,
new formal evaluation, API call, Prompt modification, Gold modification,
evaluator modification, promotion, or paper main-table modification was done.

## 10. Evidence / Artifact Index

All paths below are repository-relative and were read from the repository at
archive time. SHA-256 values are of the current files.

### Span grounding / post-processing repair

- `formal_experiment/outputs/reports/d_span_grounding_repair_v1.json`
  - SHA-256: `350f2fb1853302f36ee696559bec3787d911fa6fdc74820f2f97b22adc313f64`
- `formal_experiment/outputs/reports/d_span_grounding_repair_v1.md`
  - SHA-256: `e08a28330b92b580229a08f888b06c15fd789c5b608aeb2eca48dd62e9d17f2a`
- `formal_experiment/outputs/development/d_span_grounding_repair_v1/manifest.json`
  - SHA-256: `339d27ceab5f1ba59d5396f16d98332d7e6d9dd4bfc40cb4326effc88bfa582b`
- relevant commit: `6ee826484699532df1c39c60a359bc25f878989a`

### Actor semantic error audit

- `formal_experiment/outputs/reports/d1_actor_semantic_error_audit_v1.json`
  - SHA-256: `f70ea61ccdfb72d0343b10fa28ec4658a0ed10c60cfe9f16ec190508dbaa978a`
- `formal_experiment/outputs/reports/d1_actor_semantic_error_audit_v1.md`
  - SHA-256: `5ef1117726e4bfe2908e6e3b196f774a84de663daec92850a50c06b5fdc76d2b`
- relevant commit: `d8b77b6e99b6775093e95a5ca98f7b6e66a59371`

### Actor Prompt sensitivity screening

- `formal_experiment/outputs/reports/d1_actor_refinement_v1.json`
  - SHA-256: `79a9d21c99eaa58eee2eb0630854bdc166b0eae2a876b4d5f17c7b7eb3af44be`
- `formal_experiment/outputs/reports/d1_actor_refinement_v1.md`
  - SHA-256: `aef1379c333f49b2be47630f047b3fb4b4e77b58023cb1a8ecb39c0fe05d2d24`
- `formal_experiment/outputs/reports/d1_actor_refinement_v1.evidence_manifest.json`
  - SHA-256: `6445b8d80f19ce4a7b87fbcf9c4041b4cc7735089880490f8e69637662407a0b`
- `formal_experiment/outputs/development/d1_actor_refinement_v1/experiment_manifest.json`
  - SHA-256: `f00c03f490f53504db93e68615e0d5b7122f4dc05baa4c0538ba0e2e397a5ed0`
- `formal_experiment/outputs/development/d1_actor_refinement_v1/execution_summary.json`
  - SHA-256: `fc9fdfc6e072c2cd33835e203eaccce75bb22c9c00c57d7e2d876c063b02eee8`
- `formal_experiment/outputs/development/d1_actor_refinement_v1/execution_incident_001.json`
  - SHA-256: `3df32b9f4caa4ba926a6511212a695410ab0b300cc47774b90a705f313a875f9`
- `formal_experiment/prompts/sun_compat/actor_refinement_v1/manifest.json`
  - SHA-256: `fc5192efce14e83775b97f07320ae5737ca37a3ae6e5f126e3c83d25c6bab21d`
- `formal_experiment/prompts/sun_compat/actor_refinement_v1/prompt_diff_manifest.json`
  - SHA-256: `2499467d7612c7568ceaae03c834cb4fc273a0b16b0dac860c1a4e4b8cd21192`
- Prompt variants:
  - `formal_experiment/prompts/sun_compat/actor_refinement_v1/direct_llm_actor_baseline_v1.md`
    - SHA-256: `3aa64877cd4c4dae9f13cb40d102c3c9b04cc9bee5d478c34ad04621c0ede895`
  - `formal_experiment/prompts/sun_compat/actor_refinement_v1/direct_llm_actor_role_eligibility_v1.md`
    - SHA-256: `57d42002060ff2909855bdb0eda1ec3c9af76933b6ebd5805d002fa9fe7626dd`
  - `formal_experiment/prompts/sun_compat/actor_refinement_v1/direct_llm_actor_pronoun_policy_v1.md`
    - SHA-256: `4ec0756bae791fdb0f013f80c93deeb6cfa3b14a0b2656ee89b16f76653f539f`
  - `formal_experiment/prompts/sun_compat/actor_refinement_v1/direct_llm_actor_condition_projection_v1.md`
    - SHA-256: `aac408ad9d1940eeee899d223cb51544afdc9d04de331b907d9a485e2e19792d`
- Raw/derived per-sample evidence:
  - `formal_experiment/outputs/development/d1_actor_refinement_v1/<arm>/repeat-01/raw_responses.jsonl`
  - `formal_experiment/outputs/development/d1_actor_refinement_v1/<arm>/repeat-01/provenance.jsonl`
  - and remaining derived artifacts in the same run directories.
  - per-file SHA-256 and byte sizes are recorded in
    `formal_experiment/outputs/reports/d1_actor_refinement_v1.evidence_manifest.json`.
- relevant commit: `3789ebb9f68fe1c9ae008f5c864eda7aad8a71bf`

### Branch closure metadata

- Actor exploratory branch status: CLOSED.
- No further work performed.
