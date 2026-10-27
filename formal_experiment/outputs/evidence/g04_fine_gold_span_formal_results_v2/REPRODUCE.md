# Frozen formal Part 2 (Stage 2) results — original Gold spans (v2)

Capsule id: `g04_fine_gold_span_formal_results_v2`

This capsule freezes the recomputed Stage 2 paper numbers under evaluation-view contract v2 (`fine_gold_span`): the reference side is the **original annotated Gold spans**, with **no** per-field envelope merge, and the match rule is the unchanged non-one-to-one character-overlap rule.

It is a metric-implementation fix plus a recomputation of already saved experiments. No LLM was called, no prediction was regenerated, no Gold, prompt, or Part 3 code was modified.

## Table I — Semantic extraction (recomputed)

| Element | Sun et al. | LLM-SE |
|---|---:|---:|
| Modality (Macro-F1) | 0.713 | 0.769 |
| Actor | 0.804 | 0.722 |
| Action | 0.855 | 0.880 |
| Condition | 0.705 | 0.786 |
| Constraint | 0.491 | 0.548 |
| Exception | 0.815 | 0.696 |
| Overall (Micro-F1) | 0.678 | 0.729 |

Unrounded overall: Sun 0.677824, LLM-SE 0.729437 (lead +5.16 pp).

## Table II — E/S/J prompt ablation (recomputed)

| E | S | J | Micro-F1 |
|---|---|---|---:|
| - | - | - | 0.6532 |
| - | - | + | 0.6389 |
| - | + | - | 0.7155 |
| - | + | + | 0.7212 |
| + | - | - | 0.7373 |
| + | - | + | 0.7342 |
| + | + | - | 0.7335 |
| + | + | + | 0.7280 |

## Inputs (frozen)

- Gold: `data/gold/stage2/estg150_formal_gold_v1.json` sha256 `c31a514a6b58b640ed020c380c0b7bed136dc9574b2c98c98dedec1ecdb57100`
- Sun et al. (rules-only): `data/predictions/b0_formal_arm_v1/predictions.json` sha256 `fa94991d246db9876b55d6a473644a4a1b93404bc35d3e314d3dba4768d9278d`
- LLM-SE (Ours): `data/predictions/direct_llm_formal_arm_v1/predictions.json` sha256 `bbadb6834572e58fb8321204b3bc975c887d23d9ae60bd804bf91137bb46072b`
- cell 000: `outputs/development/v6_factorial_ablation_v1/000/repeat-01/canonical_predictions.jsonl` sha256 `83e56603ab72f16e8c7d9677d388b63bbdeb0abef6ecc4dd88fc66bc4bdd8164`
- cell 001: `outputs/development/v6_factorial_ablation_v1/001/repeat-01/canonical_predictions.jsonl` sha256 `081da6f4f3ca4980903ac250d7320fe56777e0a07e0394dee4ccf50f026a2a73`
- cell 010: `outputs/development/v6_factorial_ablation_v1/010/repeat-01/canonical_predictions.jsonl` sha256 `602031ec551900bee12e02c9833cc00602a544c357b7a77a38f098064e0d2f43`
- cell 011: `outputs/development/d1_prompt_factorial_ablation_v2/D-no-semantic-examples-0813/repeat-01/canonical_predictions.jsonl` sha256 `ba642d6a8377720b71a9d2c4a5ae3a4b7417c9783bfa7c8efd4aa2aa1a77d121`
- cell 100: `outputs/development/v6_factorial_ablation_v1/100/repeat-01/canonical_predictions.jsonl` sha256 `d7bc985f395576260af7972107290cb467fa9a2ee4aebb03416c7381251288a7`
- cell 101: `outputs/development/d1_prompt_factorial_ablation_v2/D-no-semantic-guidance-0813/repeat-01/canonical_predictions.jsonl` sha256 `a32e60c7982765f1ab453eddde45c37ae82f474ae8f8173d2e81ab36e798bd6e`
- cell 110: `outputs/development/d1_prompt_factorial_ablation_v2/D-no-explicit-json-contract-0813/repeat-01/canonical_predictions.jsonl` sha256 `a240a11a2bba3a0e6196d36dd62ea6a036b83ba4be476efaac0723a44ccef5ed`
- cell 111: `outputs/development/barrientos_ablation_suite_v2/D-full-0813/repeat-01/canonical_predictions.jsonl` sha256 `2dc036c3c72f54e194ad9882aac5b78f2fd0e0a7f9fbdf44dc73baa31ce23195`

## Reproduction

```bash
python scripts/build_stage2_table1_paper_final_v1.py
python scripts/run_v6_factorial_ablation_v1.py --report-only
python scripts/build_stage2_fine_gold_span_freeze_v1.py
```

Historical coarse numbers remain reproducible through:

```bash
python scripts/build_stage2_table1_paper_final_v1.py --evaluation-view coarse_sentence_level
python scripts/run_v6_factorial_ablation_v1.py --report-only --evaluation-view coarse_sentence_level
```

## Rules

- view: `fine_gold_span`
- match rule: `independent_same_field_any_nonempty_character_span_intersection`
- coordinates: zero-based character offsets into approved_text_en, half-open [start,end)
- assignment: none (independent overlap coverage, not one-to-one)
- Overall = micro pooling over actor/action/condition/constraint/exception
- Modality = four-class label macro-F1, reported separately

## Acceptance

- 24/24 checks reproduce the independent audit reference.
