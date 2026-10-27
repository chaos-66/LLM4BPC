# Table 1 — Part 2 regulatory information extraction (EStG-150)

Evaluation view: **original Gold spans (fine_gold_span, formal main view)**

Report id: `stage2_table1_paper_final_v2` · zero new LLM calls · regenerated from frozen Gold + frozen arm predictions.

## Main table

| Method | Modality (macro-F1) | Actor | Action | Condition | Constraint | Exception | **Overall (pooled 5)** |
|---|---|---|---|---|---|---|---|
| Sun et al. (rules-only) | 0.713 | **0.804** | 0.855 | 0.705 | 0.491 | **0.815** | 0.678 |
| Ours (LLM-SE) | **0.769** | 0.722 | **0.880** | **0.786** | **0.548** | 0.696 | **0.729** |

## Overall metric (pooled five span-bearing fields)

| Method | Precision | Recall | F1 | n (Gold spans) | n (extracted) |
|---|---|---|---|---|---|
| Sun et al. (rules-only) | 0.6435 | 0.7160 | 0.6778 | 824 | 892 |
| Ours (LLM-SE) | 0.8424 | 0.6432 | 0.7294 | 824 | 590 |

Δ Overall (pooled F1, Ours − rules-only): **+5.16 pp**

## Per-field deltas (Ours − rules-only, percentage points)

| Field | Rules-only F1 | Ours F1 | Δ (pp) | Higher |
|---|---|---|---|---|
| Actor | 0.804 | 0.722 | -8.17 | rules-only |
| Action | 0.855 | 0.880 | +2.46 | Ours |
| Condition | 0.705 | 0.786 | +8.09 | Ours |
| Constraint | 0.491 | 0.548 | +5.68 | Ours |
| Exception | 0.815 | 0.696 | -11.92 | rules-only |

## Modality label classification (reported separately)

| Method | Accuracy | Macro-F1 | Unlabeled predictions |
|---|---|---|---|
| Sun et al. (rules-only) | 0.7400 | 0.7128 | 0 |
| Ours (LLM-SE) | 0.8333 | 0.7695 | 1 |

## Table note (must be carried into the paper)

Modality is a four-class **label** macro-F1 over {obligation, permission, prohibition, definition}. The other five columns are span F1 under the fixed Sun literal-overlap contract. **Overall is the pooled (micro) F1 over the five span-bearing fields only.** Modality evidence spans are not recoverable from the published decision-only Gold, so they are excluded from the overall score and never zeroed.

## Provenance

- Gold: `data/gold/stage2/estg150_formal_gold_v1.json` (sha256 `c31a514a6b58b640ed020c380c0b7bed136dc9574b2c98c98dedec1ecdb57100`)
- Sun et al. (rules-only): `data/predictions/b0_formal_arm_v1/predictions.json` (sha256 `fa94991d246db9876b55d6a473644a4a1b93404bc35d3e314d3dba4768d9278d`)
- Ours (LLM-SE): `data/predictions/direct_llm_formal_arm_v1/predictions.json` (sha256 `bbadb6834572e58fb8321204b3bc975c887d23d9ae60bd804bf91137bb46072b`)
- New LLM calls: 0
