# Stage 3 Binding Gold annotation format (v1)

The supplied-binding **oracle diagnostic** consumes three inputs:

1. **LLM-SE Rule Record**:
   `data/predictions/gdpr7_direct_llm_v1/predictions.json`
2. **Binding Gold** (human-filled): an explicitly supplied `--binding-gold` path.
3. **BPMN**: control/variant paths already embedded in each binding item.

Agents must never infer human decision fields. This document defines the
oracle input format. Both validator and runner require an explicit input.
These human bindings are reference answers; an automatic predictor must not
receive them, the expected lane, target activity ID or declared order pair.
The Rule Record input below is used for ID diagnostics, not for predicting
bindings. This runner cannot establish end-to-end Ours performance.

The 30-item candidate review is complete. Its retained result is
`data/development/stage3_synth/stage3_binding_human_decisions_v1.json`
(`human_review_complete`, `is_gold=false`). It uses the review-decision schema,
not the detector's binding schema below. The old template and temporary review
tool are archived and must not be auto-selected for another batch. Completing
review does not supply missing rule order endpoints or publish Binding Gold.

## Item fields

Each of the 30 pair items contains immutable process/rule context and the
following human decision fields:

| Field | Required for | Meaning |
|---|---|---|
| `decision_action_id` | all types | Rule-side action (from `immutable_context.rule_side.actions`) that the target BPMN activity discharges. |
| `decision_actor_id` | incorrect_actor | Rule-side actor (from `immutable_context.rule_side.actors`) that legitimately performs the action. |
| `decision_expected_lane` | incorrect_actor | Lane name or lane id in the **control** BPMN that legitimately owns the target activity. |
| `decision_order_before_action_id` | out_of_order | Rule-side action that must precede the second endpoint. |
| `decision_order_after_action_id` | out_of_order | Rule-side action that must follow the first endpoint. Both order fields must be set together. |
| `decision_note` | optional | Free-text rationale. |
| `review_state` | all items | `unreviewed`, `reviewed`, or `adjudicated`. |

## Validation

```powershell
python scripts/validate_binding_gold_v1.py \
  --binding-gold <explicit-binding-file.json>

# strict gate; exits non-zero until every item is filled/reviewed
python scripts/validate_binding_gold_v1.py --binding-gold <explicit-binding-file.json> --require-ready
```

The validator checks BPMN existence and sha256, action/actor id existence,
target activity existence, lane existence, order-pair format, and review state.
It never generates or modifies Gold.

## Running the supplied-binding oracle diagnostic

The oracle fails closed until the supplied binding file is ready. This is not automatic Ours:

```powershell
python scripts/run_stage3_binding_oracle_v1.py \
  --binding-gold <filled-binding-gold.json>
```

It writes `outputs/development/stage3_binding_oracle_v1/predictions.jsonl` and
`outputs/reports/stage3_binding_oracle_v1.{json,md}`.

## Evaluation

The runner invokes the evaluator pipeline automatically.  To re-score an
existing prediction file:

```powershell
python scripts/evaluate_stage3_binding_oracle_v1.py \
  --benchmark data/development/stage3_synth/stage3_paired_benchmark_v1.json \
  --predictions outputs/development/stage3_binding_oracle_v1/predictions.jsonl
```

Reported metrics: per-type precision/recall/F1, Macro-F1, Micro-F1, and
compliant specificity.
