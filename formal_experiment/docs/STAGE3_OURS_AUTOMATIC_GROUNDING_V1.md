> **Superseded on 2026-09-23.** This v1 automatic-grounding path used the
> paired CONTROL BPMN as reference and a structural control-vs-current detector;
> it is not the Table 3 v2 Ours arm. Its F1=1.0 is retracted. The repaired
> controlled comparison uses `run_stage3_table3_v2.py`, current BPMN only, and
> the same frozen Sun Stage-3 scorer for Sun and Ours. See
> `outputs/reports/stage3_table3_v2_rootcause_notes.md` and
> `docs/MASTER_PIPELINE.md` Section "Table 3 v2 controlled repair".

﻿# Stage 3 Ours automatic grounding and detector v1

## Boundary

`Ours` means the gold-blind chain:

1. LLM-SE Rule Record (plus the frozen Stage-2 sentence spans needed to
   recover the record's character offsets);
2. the benchmark's gold-blind inference view
   (`stage3_paired_benchmark_inference_view_v1.json`);
3. a reference/control BPMN Process Record for automatic grounding;
4. persisted grounding predictions;
5. a structural detector that checks each item BPMN against those predictions.

It never reads the benchmark `grounding` block, `target_activity_id`,
expected lane, `order_pair`, `gold_violation_type`, `target_violation_type`,
the mutation manifest, or the binding reference. Binding reference and
benchmark answers are read only by evaluators after the grounding and detector
predictions have been persisted.

## Automatic grounding

For each benchmark pair, the runner:

- extracts actions, actors and any order relations from the LLM-SE Rule
  Record;
- uses the pair's control BPMN as the reference Process Record;
- ranks BPMN activities against every rule action with
  `s3_semantic_grounding_v1.ground_action`, using spaCy vector similarity plus
  deterministic lexical coverage;
- keeps both a forced top-1 activity and a candidate set;
- records structural lane ownership for every candidate activity;
- grounds actor text against lane/pool names and records the item's
  activity-to-lane map;
- maps any available rule order relation to grounded activity endpoints.

The candidate set is intentionally retained rather than forced to one ID: the
single forced mapping is below the lexical gap, while the candidate set covers
the reference activity needed for structural checking. Both quantities are
reported separately.

## Detector

For every benchmark item the detector parses only that item's BPMN and:

- `missing_action` if a grounded candidate activity from the reference process
  is absent in the item;
- `incorrect_actor` if a grounded candidate activity is present but its lane
  owner differs from the reference lane;
- `out_of_order` only if the Rule Record supplied a usable order relation and
  the item inverts it;
- otherwise `compliant`.

Process-only order mutations are not interpreted as rule-side order
requirements. The formal benchmark eligibility audit therefore marks all ten
`out_of_order` pairs `ineligible_no_rule_order`; their row is `N/A`, not 0.

## Reproduce

```powershell
python scripts/run_stage3_full_repair_v1.py
```

Individual artifacts:

- `data/development/stage3_synth/stage3_binding_audit_v1.json`
- `data/development/stage3_synth/stage3_binding_reference_v1.json`
- `data/development/stage3_synth/stage3_paired_benchmark_eligibility_v1.json`
- `outputs/development/stage3_ours_v1/automatic_grounding_predictions_v1.json`
- `outputs/development/stage3_ours_v1/predictions.jsonl`
- `outputs/reports/stage3_automatic_grounding_evaluation_v1.json`
- `outputs/reports/stage3_ours_v1_evaluation.json`
- `outputs/reports/stage3_table3_v1.json`
- `outputs/reports/stage3_binding_final_human_approval_packet_v1.md`

## Claim boundary

- The Oracle / Grounded Upper Bound row uses supplied human bindings and is not
  Ours.
- Full three-type formal Table 3 still requires human approval of the 19
  unresolved pairs, especially the rule-side order ineligibility judgments.
- `out_of_order` must not be reported as a zero-F1 method conclusion while no
  eligible rule-side order relation exists.
