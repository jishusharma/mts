**T11 breadth washout long: FAIL (primary cell, 1d, VAL episodes 17); BTC > SMA200d row: UNDERPOWERED**

Regime mix: DEV events 21: BULL 10% BASE 33% BEAR 57%, BTC above SMA200d 33%; VAL events 19: BULL 58% BASE 5% BEAR 37%, BTC above SMA200d 32%

Research, not advice. Fee 12 bp (fees.py) + real funding, stop max(2.5 ATR14, 8%), exit close of day 10. Unit = episode (events within 14 days merged). R = return / stop distance. Survivorship: longs biased UP.

| cell | split | events | episodes | legs | gross R | net R | fee R | net % | CI95 episode | CI95 event | CI95 week | DEV/VAL n pooled |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| primary | DEV | 21 | 18 | 780 | +0.0540 | +0.0481 | +0.0055 | +3.30 | [-0.2307, +0.3349] | [-0.2417, +0.2706] | [-0.2484, +0.3213] | |
| primary | VAL | 19 | 17 | 760 | -0.0167 | -0.0160 | +0.0062 | +0.46 | [-0.2989, +0.2555] | [-0.2789, +0.2240] | [-0.3056, +0.1613] | |
| BTC>SMA200d | DEV | 7 | 7 | 256 | -0.0090 | -0.0223 | +0.0067 | +2.26 | [-0.5649, +0.4999] | [-0.5649, +0.4999] | [-0.6363, +0.5266] | |
| BTC>SMA200d | VAL | 6 | 6 | 271 | -0.0935 | -0.0993 | +0.0053 | +0.43 | [-0.4725, +0.2271] | [-0.4725, +0.2271] | [-0.4541, +0.2432] | |

Pooled DEV+VAL is a power row only: 35 episodes, 40 events.

### Bars, primary (verdict FAIL)

| bar | met |
|---|---|
| 1_power_ge8_val_episodes | PASS |
| 2_val_mean_gt0_and_episode_ci_low_gt0 | not met |
| 3_dev_mean_gt0 | PASS |
| 4_placebo_primary_window | PASS |
| 4g_placebo_primary_global_reported | not met |
| 5_ex_best2_gt0_and_loeo_all_gt0 | not met |
| 6_vs_basket_per_day | not met |
| 7_ex_luna_ftt_and_top3_coin_gt0 | not met |
| 8_loyo_all_gt0 | not met |
| dose_response_monotone | not met |
| strata_prediction_holds | not met |

Kill criteria: a_val_mean_le0_with_ge8_eps=True, b_loeo_flips_sign_with_lt12_eps=False, c_placebo_excess_le_p975=False

| placebo (VAL) | legs | real | draw mean | p97.5 | excess | p | fallbacks (global/state) | skipped |
|---|---|---|---|---|---|---|---|---|
| VAL_pri_window | 760 | -0.0160 | -0.1566 | -0.1115 | +0.1406 | 0.001 | 43/3 | 0 |
| VAL_pri_global | 760 | -0.0160 | -0.0777 | -0.0106 | +0.0617 | 0.036 | 0/3 | 0 |
| VAL_sec_window | 760 | -0.0160 | -0.1927 | -0.1393 | +0.1767 | 0.001 | 0/0 | 0 |
| VAL_sec_global | 760 | -0.0160 | -0.0683 | +0.0099 | +0.0523 | 0.075 | 0/0 | 0 |
| DEV_pri_window | 780 | +0.0481 | +0.0415 | +0.0781 | +0.0066 | 0.364 | 138/7 | 0 |
| DEV_pri_global | 780 | +0.0481 | +0.0733 | +0.1271 | -0.0251 | 0.831 | 0/7 | 0 |

Robustness (VAL): ex-best-2 episodes -0.1396 (dropped [20, 33]); leave-one-event-out min -0.1004 max +0.0426 flips 5; ex-LUNA/FTT -0.0199; ex-ENDED -0.0176; top-3 coin removal ['LUNA'] -> -0.0192; ['LUNA', 'ZEC'] -> -0.0221; ['LUNA', 'ZEC', 'COMP'] -> -0.0253; per-day net -0.00861 vs basket +0.00245.

Leave-one-year-out (VAL): without 2024: +0.0477 (13 eps); without 2025: -0.1431 (10 eps); without 2026: +0.0243 (11 eps)

Dose-response VAL: 15-30: 12 ev -0.0041; 30-50: 3 ev -0.2229; >=50: 4 ev +0.1002 (testable True, monotone False). Pooled: 15-30: 25 ev -0.0022; 30-50: 8 ev -0.1023; >=50: 7 ev +0.1253 (monotone False).

Strata prediction: VAL above -0.0993 (6 ev), below +0.0214 (13 ev), holds False; DEV above -0.0223 (7), below +0.0341 (14); pooled above -0.0578, below +0.0280.

| by BTC smoothed state | split | key | legs | events | episodes | mean event net R | mean leg net R |
|---|---|---|---|---|---|---|---|
| | DEV | BASE | 255 | 7 | 7 | +0.0641 | +0.0143 |
| | DEV | BEAR | 456 | 12 | 9 | +0.0248 | +0.0860 |
| | DEV | BULL | 69 | 2 | 2 | -0.2123 | -0.2176 |
| | VAL | BASE | 40 | 1 | 1 | -0.4294 | -0.4294 |
| | VAL | BEAR | 221 | 7 | 6 | -0.0098 | -0.1828 |
| | VAL | BULL | 499 | 11 | 11 | +0.0164 | +0.0343 |

| by BTC vs SMA200d | split | key | legs | events | episodes | mean event net R | mean leg net R |
|---|---|---|---|---|---|---|---|
| | DEV | above | 256 | 7 | 7 | -0.0223 | -0.0698 |
| | DEV | below | 524 | 14 | 11 | +0.0341 | +0.0873 |
| | VAL | above | 271 | 6 | 6 | -0.0993 | -0.0686 |
| | VAL | below | 489 | 13 | 11 | +0.0214 | -0.0448 |

| by year | split | key | legs | events | episodes | mean event net R | mean leg net R |
|---|---|---|---|---|---|---|---|
| | DEV | 2019 | 42 | 3 | 1 | -0.2544 | -0.2629 |
| | DEV | 2020 | 73 | 3 | 3 | +0.4403 | +0.3971 |
| | DEV | 2021 | 163 | 4 | 4 | +0.2823 | +0.3442 |
| | DEV | 2022 | 273 | 6 | 5 | -0.1717 | -0.1687 |
| | DEV | 2023 | 229 | 5 | 5 | -0.0670 | -0.0005 |
| | VAL | 2024 | 191 | 4 | 4 | -0.2231 | -0.1539 |
| | VAL | 2025 | 380 | 9 | 7 | +0.1238 | +0.1331 |
| | VAL | 2026 | 189 | 6 | 6 | -0.0898 | -0.3263 |

### Bars, BTC>SMA200d row (verdict UNDERPOWERED)

| bar | met |
|---|---|
| 1_power_ge8_val_episodes | not met |
| 2_val_mean_gt0_and_episode_ci_low_gt0 | not met |
| 3_dev_mean_gt0 | not met |
| 4_placebo_primary_window | not met |
| 4g_placebo_primary_global_reported | not met |
| 5_ex_best2_gt0_and_loeo_all_gt0 | not met |
| 6_vs_basket_per_day | not met |
| 7_ex_luna_ftt_and_top3_coin_gt0 | not met |
| 8_loyo_all_gt0 | not met |
| dose_response_monotone | PASS |
| strata_prediction_holds | not met |

Kill criteria: a_val_mean_le0_with_ge8_eps=False, b_loeo_flips_sign_with_lt12_eps=False, c_placebo_excess_le_p975=False

| placebo (VAL) | legs | real | draw mean | p97.5 | excess | p | fallbacks (global/state) | skipped |
|---|---|---|---|---|---|---|---|---|
| VAL_pri_window | 271 | -0.0993 | -0.0517 | +0.0214 | -0.0476 | 0.935 | 15/3 | 0 |
| VAL_pri_global | 271 | -0.0993 | -0.0805 | +0.0028 | -0.0189 | 0.656 | 0/3 | 0 |
| VAL_sec_window | 271 | -0.0993 | -0.1681 | -0.0801 | +0.0687 | 0.049 | 0/0 | 0 |
| VAL_sec_global | 271 | -0.0993 | -0.0530 | +0.0545 | -0.0463 | 0.822 | 0/0 | 0 |
| DEV_pri_window | 256 | -0.0223 | -0.0194 | +0.0463 | -0.0029 | 0.530 | 63/6 | 0 |
| DEV_pri_global | 256 | -0.0223 | +0.0999 | +0.2089 | -0.1222 | 0.989 | 0/6 | 0 |

Robustness (VAL): ex-best-2 episodes -0.3203 (dropped [7, 11]); leave-one-event-out min -0.2112 max +0.0579 flips 1; ex-LUNA/FTT -0.1001; ex-ENDED -0.1039; top-3 coin removal ['HBAR'] -> -0.1097; ['HBAR', 'COMP'] -> -0.1124; ['HBAR', 'COMP', 'FTT'] -> -0.1141; per-day net -0.00372 vs basket +0.00160.

Leave-one-year-out (VAL): without 2024: -0.0426 (4 eps); without 2025: -0.2851 (3 eps); without 2026: -0.0333 (5 eps)

Dose-response VAL: 15-30: 4 ev -0.3203; 30-50: 0 ev n/a; >=50: 2 ev +0.3425 (testable True, monotone True). Pooled: 15-30: 9 ev -0.1658; 30-50: 2 ev +0.0277; >=50: 2 ev +0.3425 (monotone True).

Strata prediction: VAL above -0.0993 (6 ev), below n/a (0 ev), holds False; DEV above -0.0223 (7), below n/a (0); pooled above -0.0578, below n/a.

| by BTC smoothed state | split | key | legs | events | episodes | mean event net R | mean leg net R |
|---|---|---|---|---|---|---|---|
| | DEV | BASE | 220 | 6 | 6 | +0.0295 | -0.0267 |
| | DEV | BULL | 36 | 1 | 1 | -0.3331 | -0.3331 |
| | VAL | BASE | 40 | 1 | 1 | -0.4294 | -0.4294 |
| | VAL | BULL | 231 | 5 | 5 | -0.0333 | -0.0061 |

| by BTC vs SMA200d | split | key | legs | events | episodes | mean event net R | mean leg net R |
|---|---|---|---|---|---|---|---|
| | DEV | above | 256 | 7 | 7 | -0.0223 | -0.0698 |
| | VAL | above | 271 | 6 | 6 | -0.0993 | -0.0686 |

| by year | split | key | legs | events | episodes | mean event net R | mean leg net R |
|---|---|---|---|---|---|---|---|
| | DEV | 2020 | 38 | 2 | 2 | +0.5245 | +0.5126 |
| | DEV | 2021 | 36 | 1 | 1 | -0.3331 | -0.3331 |
| | DEV | 2023 | 182 | 4 | 4 | -0.2180 | -0.1393 |
| | VAL | 2024 | 93 | 2 | 2 | -0.2129 | -0.1478 |
| | VAL | 2025 | 138 | 3 | 3 | +0.0864 | +0.0894 |
| | VAL | 2026 | 40 | 1 | 1 | -0.4294 | -0.4294 |

Holm over the two T11 cells (m=2): {'primary': 1.0, 'btc_above_sma200': 1.0}. Worst-case family adjustment (9 x p): {'primary': 1.0, 'btc_above_sma200': 1.0}.

Funding NOT_IN_DATA legs (funding 0): VAL 61, DEV 65. Exit reasons VAL: {'TIME': 600, 'STOP': 158, 'STOP-GAP': 0, 'ENDED-EXIT': 2}.

## Adversarial check

Flag: **MINOR**. Final verdict: **FAIL** (checker re-derived the same verdict).

- Order clean (aa41f4459 before e872739a7); no PRE_REG or code change after outcomes.
- Spec fidelity clean; no look-ahead. 6 VAL trades recomputed from raw klines match (4 to 1e-7; ALGO and BCH differ 0.0006 and 0.0014 R from funding-print timestamp jitter).
- Verdict FAIL re-derived: VAL net -0.016 R over 17 episodes, kill criterion a true; BTC > SMA200d row UNDERPOWERED (6 episodes).
- Disclosure gap: the loader keeps only the longest contiguous bar run per coin, so pre-gap FTT (1062 bars) and pre-collapse LUNA (631 bars) are excluded from RSI, alive counts and breadth. DEV is affected (the 2022-01-10 event is an artefact, 6 FTT/LUNA legs missing), VAL is not; verdict unchanged. The earlier sentence 'all 68 coins present, no data-driven deviation' is wrong.
- Funding prints are rounded to the second and a print just after the exit-day midnight counts, so independent recomputes can differ by about 1e-4 of price per leg.
- Placebo p 0.001 against the same-window draw comes from the placebo losing -0.157 R, not from the signal making money.
