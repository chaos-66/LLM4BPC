# Table 2 - v6 prompt-family 2^3 E/S/J factorial ablation

- status: **complete**
- evaluation view: **fine_gold_span** (original Gold spans, formal main view; no envelope merge)
- primary metric: `five_field_micro_f1`
- Gold: `data/gold/stage2/estg150_formal_gold_v1.json`
- prompt family: `v6_chunk_direct_assembly`

| E S J | Modality macro-F1 | Actor | Action | Condition | Constraint | Exception | Overall pooled (micro) F1 | Mean-of-5 F1 | Delta overall vs 111 | Failed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 0 0 | 0.8338 | 0.4579 | 0.8018 | 0.8046 | 0.4024 | 0.6316 | 0.6532 | 0.6197 | -0.0748 | 0 |
| 0 0 1 | 0.8096 | 0.4428 | 0.7809 | 0.8139 | 0.3616 | 0.7000 | 0.6389 | 0.6199 | -0.0891 | 0 |
| 0 1 0 | 0.8006 | 0.5443 | 0.8451 | 0.8014 | 0.6019 | 0.6000 | 0.7155 | 0.6785 | -0.0125 | 0 |
| 0 1 1 | 0.7627 | 0.5548 | 0.8566 | 0.8074 | 0.5937 | 0.6667 | 0.7212 | 0.6958 | -0.0068 | 0 |
| 1 0 0 | 0.7370 | 0.7739 | 0.8465 | 0.7823 | 0.5924 | 0.6364 | 0.7373 | 0.7263 | +0.0093 | 0 |
| 1 0 1 | 0.7083 | 0.7328 | 0.8086 | 0.7990 | 0.6153 | 0.7423 | 0.7342 | 0.7396 | +0.0062 | 0 |
| 1 1 0 | 0.7520 | 0.6705 | 0.8837 | 0.7750 | 0.6007 | 0.7500 | 0.7335 | 0.7360 | +0.0055 | 0 |
| 1 1 1 | 0.7537 | 0.6865 | 0.8603 | 0.7843 | 0.5971 | 0.6364 | 0.7280 | 0.7129 | +0.0000 | 0 |

## Overall metric detail

| E S J | Precision | Recall | F1 | Gold spans | Extracted | Source |
|---|---:|---:|---:|---:|---:|---|
| 0 0 0 | 0.6929 | 0.6177 | 0.6532 | 824 | 736 | v6_factorial_new_calls |
| 0 0 1 | 0.6776 | 0.6044 | 0.6389 | 824 | 729 | v6_factorial_new_calls |
| 0 1 0 | 0.7288 | 0.7027 | 0.7155 | 824 | 767 | v6_factorial_new_calls |
| 0 1 1 | 0.7328 | 0.7100 | 0.7212 | 824 | 771 | historical_same_release |
| 1 0 0 | 0.8057 | 0.6796 | 0.7373 | 824 | 669 | v6_factorial_new_calls |
| 1 0 1 | 0.7870 | 0.6881 | 0.7342 | 824 | 690 | historical_same_release |
| 1 1 0 | 0.7715 | 0.6990 | 0.7335 | 824 | 722 | historical_same_release |
| 1 1 1 | 0.7698 | 0.6905 | 0.7280 | 824 | 708 | historical_same_release |

## Main effects (overall pooled micro-F1 scale)

```json
{
  "E_main_effect": 0.05104990682625676,
  "J_main_effect": -0.004273765300478072,
  "S_main_effect": 0.03364473583172578,
  "three_way_ESJ": -0.022340420403119343,
  "two_way_EJ": 1.1074860567061862e-05,
  "two_way_ES": -0.07733613113594473,
  "two_way_SJ": 0.008786082111083782
}
```

## Provenance

- prompt manifest: `prompts/sun_compat/ablation_v2_factorial/manifest.json`
- Gold sha256: `c31a514a6b58b640ed020c380c0b7bed136dc9574b2c98c98dedec1ecdb57100`
- historical 111/110/101/011: reused predictions from the same DeepSeek-V4-Pro-0813 release window.
- new 000/001/010/100: 600 calls in this batch.
- no Gold or benchmark mutation; evaluator fixed.
- no new LLM call was made for this re-score.
