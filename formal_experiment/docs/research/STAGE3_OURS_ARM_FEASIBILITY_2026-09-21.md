# Stage 3 "Ours" arm feasibility: what the evidence now requires (2026-09-21)

**Status:** read-only analysis. Zero LLM/API calls. Zero writes to Gold, panels,
predictions or results.

**Question:** can a three-type Stage 3 detector be built that derives its
rule-to-process bindings from the **published Stage 2 Rule Record**, so the
paper can report an "Ours" row on the paired benchmark?

**Corrected interpretation (2026-09-23): reference annotation and automatic
prediction are separate requirements.** Completing human bindings alone
cannot produce an end-to-end Ours result. Existing automatic matchers are
present; their integration and evaluation must keep reference bindings out of
inference. The observations below remain historical development evidence.

---

## 1. The benchmark carries no rule-action → activity annotation

`synthetic_controlled_error_extension_v1.json` gives each variant exactly these
fields:

```
variant_id, process_id, rule_id, mutation_type, expected_violation,
source_bpmn(+sha), variant_bpmn(+sha), target_activity_id,
mutation_config, validation_checks, generator_sha256
```

There is **no field naming the rule-side action that `target_activity_id`
realizes**, and both the rule text and the activity names are several spans
long, so the correspondence is not recoverable by construction. A detector
cannot prove "this BPMN activity discharges that rule action" — it can only
guess, and guessing is precisely the similarity path that fails (§3).

## 2. The Gold Rule Records hold actor-action links but no order relations

Read directly from the published Gold
(`data/gold/stage3/gdpr7_gold_rule_records_v1.json`, 9 rules / 74 sentences):

| Quantity | Value |
|---|---|
| clauses | 92 |
| clauses carrying actions | 70 (75 action spans) |
| clauses with a non-empty `actor_action_map` | **38** (38 links) |
| clauses with a non-empty `order_relations` | **0** (0 links) |

So `actor_action_map` exists for a minority of clauses, and
`order_relations` exists for none.

## 3. Lexical grounding is the thing that fails — measured

On the 60-item paired benchmark, with each arm's own frozen rule:

| Arm | Macro-F1 | Specificity | Exact type | Unobservable |
|---|---:|---:|---:|---:|
| `sun_reconstruction` | 0.3175 | 0.3333 | 12/30 | 16 |
| `winter_wrapper` | 0.2222 | 0.6000 | 10/30 | 0 |
| grounded reference (declared bindings) | 1.0000 | 1.0000 | 30/30 | 0 |

`out_of_order` F1 is **0.0 for both predecessors**. The declared-binding
reference receives additional answer information, so this comparison cannot
isolate algorithm quality or prove that a new grounding method is superior.

## 4. The project's own formal pipeline already records this blocker

`outputs/reports/gdpr_3type_linkage_v1_direct_llm.md` (the real, promoted
LLM-SE Stage 2 arm, 74 records), states verbatim:

- "order relations absent in capsule for rules: all nine ... (Definition-7
  input unavailable by contract; **never fabricated**)"
- "unobservable = 11 (by reason: `action_mapping_below_gamma`: 8,
  `stage2_empty_envelope`: 1, `incomplete_rule_actor_action_map`: 2)"
- `out_of_order` precision/recall/F1 = 0.0000

This is not a hypothesis about the new benchmark. It is what the **actual
LLM-SE Stage 2 output** did on the original three-type evaluation: eight of
eleven incorrect-actor items were unobservable because the rule action could
not be mapped to a process action above gamma, and every item had no order
relation to check.

## 5. What this means

Automatic prediction and reference annotation have different owners:

- The predictor receives a Stage 2 Rule Record, a BPMN model and frozen method
  settings. It must predict action/activity and actor/executor mappings itself.
- The evaluator may use independently adjudicated bindings as reference
  answers. Accepted nulls must not be silently converted into positive matches.
- A supplied-binding checker uses human mappings and declared activity/order
  IDs. It is an oracle diagnostic, not an end-to-end Ours arm. Merely consuming
  a LLM-SE file for ID diagnostics does not change that classification.

The earlier claim that only human annotation remained was too strong.
Automatic matching already exists in `sun_stage3/sun_scorer.py` and
`s3_action_matching_v3.py`; further integration and controlled evaluation are
distinct from producing reference labels. AI-generated predictions are allowed
as predictions, but must never be relabelled as human Gold.

## 5b. The mechanism itself works — measured (added 2026-09-21, round 5)

To make sure the conclusion above is not dodging solvable work, the detector
mechanism was tested directly
(`scripts/diagnose_stage3_binding_selfcheck_v1.py`, read-only):

| Check | Result |
|---|---|
| `out_of_order` pairs whose **control** is forward-ordered only | **10/10** |
| `out_of_order` pairs whose **variant** is the inversion | **10/10** |
| order relations available from the **Gold** Rule Records | **0** (0 of 92 clauses) |
| order relations available from the **real LLM-SE capsule** | **0** (0 of 78 clauses) |

The control/variant inversion establishes a **process-structure difference**.
It does not establish that a regulation requires that order. Missing rule-side
relations in the two saved capsules also do not prove that the legal text
contains, or omits, a particular relation: source evidence must be checked.

The user completed 30/30 candidate reviews. The active result is
`data/development/stage3_synth/stage3_binding_human_decisions_v1.json`,
with 5 null actions, 8 null actors and 10 process-only orders. The null action
and actor occurrences cover 7 distinct rule/activity contexts. This is not
Binding Gold; review completion remains valid and does not need to be undone.
The old review batch stays archived. The source inventory and role questions
are in `outputs/reports/stage3_binding_reference_assessment_v1.md`.

## 6. Evaluation paths

| Path | Required inputs and separation | Permitted interpretation |
|---|---|---|
| Automatic grounding evaluation | Predictor uses only predicted Rule Records and process inputs; evaluator separately holds adjudicated bindings, including supported no-match/unknown cases. | Measured grounding accuracy and coverage within the declared development/test scope; no superiority assumed. |
| End-to-end compliance evaluation | The same automatic predictions feed fixed formulas; reference bindings, mutation targets and expected lanes/orders are unavailable during inference. Legal order checks require source-supported rule relations. | Actual measured compliance results under comparable inputs; completion of annotation alone is insufficient. |
| Supplied-binding oracle diagnostic | Human mappings and declared process IDs are deliberately supplied to the checker. | Diagnostic performance with privileged inputs; never label this as end-to-end Ours. |

A complete reference dataset can include justified no-match or not-applicable
decisions. It does not require every BPMN task to have a legal action span, or
every synthetic order inversion to have a corresponding legal ordering rule.
The deterministic work in this correction does not modify frozen methods,
publish Gold, resume cancelled LLM fallback, or run new experiments.

## 7. Reproduction

```powershell
cd formal_experiment
python -W ignore scripts/build_stage3_paired_benchmark_v1.py       # 60-item benchmark
python -W ignore scripts/run_stage3_grounded_checker_v1.py          # upper bound
python -W ignore scripts/run_stage3_predecessors_paired_v1.py       # predecessor sanity run
python -W ignore scripts/diagnose_stage3_mutation_detectability_v1.py  # 30/30 structural
```

All read-only over frozen artifacts; no LLM/API; no network.
