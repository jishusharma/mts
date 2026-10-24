# T05 Placebo nulls: what does chance alone produce here? (card dsa-audit-05-placebo-nulls)

Seeds: placebo and bootstrap SEED = 20261016 (per arm: numpy default_rng([SEED, arm ordinal])); LC1 SEED = 20261016. DEV only (bars before 2024-07-01).

## 1. Summary
- Checked: for every arm of the gross screen, mal_bb, opr_bb_mtf_center, opr_weekly_low_round_sweep, opr_preopen_tops and the 126 candle_close arms, 1,000 placebo sets matched on weekday, 15-minute slot and cooldown, scored by the study's own return function (every real mean and SE below reproduces the published number), plus overlap, week-block bootstrap, best-of-N bars, half-year signs and a fair LC1 control.
- Found: no tested arm's gross mean beats chance once the number of arms tried is counted (arms above their study's best-of-N bar: {'screen': 0, 'mal_bb': 0, 'opr_bb': 0, 'wlow': 0, 'preopen': 0, 'candle': 0}); the published day-clustered SE is not too small (placebo SD / SE above 1.2 in 30 of 137 arms); the LC1 control is not fair (about half of its lines are the real level, and untouched lines count as non-holds), and with a touched-only control 0 of 12 families stay KEEP (published 8; lost: 4h_fractal_high, 4h_fractal_low, naked_poc, prior_day_high, prior_day_low, prior_day_poc, prior_week_high, round_1000; newly passing: none).
- Changes: the FAIL / INCONCLUSIVE screen verdicts stand; the LC1 KEEP list must be re-stated on the fair control before any layer uses it.

## 2. Scope
| Study | Window | Method | Result |
|---|---|---|---|
| Gross screen T/notF/C, d=1 h=60 | DEV 2022-01..2024-06 | S.build_ledger events, placebo + overlap + bootstrap | out/placebo_screen.csv |
| mal_bb A1, A2 x h 30/60/120/240 | DEV | study.py sets(), same | out/placebo_mal_bb.csv |
| opr_bb AU, AD x h 60/120/240 | DEV | same | out/placebo_opr_bb.csv |
| wlow RL, AS x h 30/60/120 | DEV | same | out/placebo_wlow.csv |
| preopen H1, H2 x h 60/180/390 | DEV | same | out/placebo_preopen.csv |
| candle_close 126 arms (tf x family x signature), h=60 | DEV | events.csv.gz, cooldown = one event per side and UTC day | out/placebo_candle.csv |
| LC1 12 families | standard DEV decisions 2022-04-01..2024-06-30 | fair touched-only random lines | out/lc1_fair.csv |

Reproduction check: every real arm mean, n and SE equals the published trials.csv / ledger value (columns mean G vs pub mean); the gross-screen control mean -0.0081 and n 1439 match RESULT.md. Placebo test: t05_core.py draws 1,000 sets per arm; test_placebo_nulls.py::test_placebo_sets_are_matched_and_seeded passes (it failed before t05_core.py existed).

Method notes. Statistic: mean side-signed gross % after the study's own funding charge (net = gross - 0.14). Empirical p = (1 + number of placebo means >= the real mean) / 1001 (one-sided). SD ratio = SD of the 1,000 placebo means / the study's published day-clustered SE (above 1.2 = published SE too small). Overlap: share of events whose hold [entry, entry+h] overlaps another event's hold; n_eff = number of connected hold groups. Boot t_net = (mean - 0.14) / SD of 2,000 week-block bootstrap means. need t_gross (pass rule) = 2 + 0.14/SE, the gross t at which t_net reaches 2. Placebo events are redrawn while a same-side pair violates the cooldown; conflict = share left unresolved (0 means none).

## 3. Findings
| ID | Sev | Status | Evidence | Numbers affected | Fix | Card |
|---|---|---|---|---|---|---|
| T05-F1 | S3 | CONFIRMED | scripts/T05/t05_merge.py -> out/summary.json; common.py:192-230, screen.py:220-250 (any-arm PASS, no correction) | No arm reaches its study's best-of-N bar: {'screen': 0, 'mal_bb': 0, 'opr_bb': 0, 'wlow': 0, 'preopen': 0, 'candle': 0}. Best-of-N bars (t_gross, 95%): screen N=90: 3.45 (single arm 1.55), mal_bb N=39: 2.74 (single arm 1.52), opr_bb N=6: 2.43 (single arm 1.58), wlow N=12: 2.49 (single arm 1.61), preopen N=26: 2.90 (single arm 1.67), candle N=126: 3.35 (single arm 1.66). The study pass rule demands more than either bar once the 0.14 % cost is added, so no verdict flips; the risk is a future arm with a smaller cost gap | Add a Holm/best-of-N bar next to the any-arm headline in common.verdict_arm / headline() | none (S3) |
| T05-F2 | S3 | CONFIRMED | out/placebo_*.csv column sd_ratio | Placebo SD / published SE: screen median 0.67, max 0.75, arms >1.2: 0, mal_bb median 0.79, max 0.81, arms >1.2: 0, opr_bb median 0.99, max 1.25, arms >1.2: 1, wlow median 0.64, max 0.69, arms >1.2: 0, preopen median 0.87, max 0.89, arms >1.2: 0, candle median 1.10, max 1.62, arms >1.2: 29. The day-clustered SE is conservative (ratio < 1) for the five G5 studies except opr_bb AD h=60/120 (1.30/1.25). For candle_close the same day-cluster formula is too small in 29 of 126 arms (up to 1.62), where 60-minute holds from the 1m/2m/3m timeframes overlap inside a day; the candle study itself publishes win/lift CIs, not this SE, so no published number changes | For arms with several overlapping holds per day use the week-block bootstrap, not the day cluster | none |
| T05-F3 | S3 | CONFIRMED | out/placebo_*.csv columns overlap_share, n_eff | Primary arms have cooldown = hold, so overlap is 0 (screen 3 %); secondary horizons longer than the cooldown overlap (mal_bb A1 h=240 59 %, h=120 30 %; preopen H2 h=390 8 %); the week-block bootstrap t is within about 0.4 of the published t on the primary arms. Lead L7 (390-minute holds, 60-minute cooldown) is real only for the secondary preopen/mal_bb horizons and does not change a verdict | Report n_eff next to n for any arm whose hold exceeds its cooldown | none |
| T05-F4 | S3 | CONFIRMED | Table wlow, arms RL h=30/60/120 | Placebo p = 0.017 / 0.063 / 0.005 on gross means +0.033 / +0.032 / +0.094 % against a placebo mean of about -0.004 %: the closest any arm comes to a pre-cost signal, but t_gross 1.92 at h=120 is under the best-of-12 bar (2.49), and the 0.14 % cost keeps t_net negative (-3.0 at h=60, -0.9 at h=120), so FAIL stands. The published control (non-reclaims) is itself a long-after-the-break sample (ctrl +0.084 % at h=120), so DIFF vs control (t 0.12) understates the placebo excess | Use a time-matched placebo as a second control in the verdict | none (S3) |
| T05-F5 | S1 | CONFIRMED | scripts/T05/t05_lc1.py -> out/lc1_fair.csv, levels_hold.py:78-93 | LC1 control unfair as in lead L8. Fair rerun: 0 of 12 KEEP vs published 8; lost 4h_fractal_high, 4h_fractal_low, naked_poc, prior_day_high, prior_day_low, prior_day_poc, prior_week_high, round_1000; gained none (table in section 5) | Re-state the LC1 KEEP list with the touched-only distance-matched control | raw card (see section 8) |
| T05-F6 | S3 | CONFIRMED | out/placebo_candle.csv | candle_close: 3 of 126 arms have empirical p < 0.05 (chance: 6.3); 0 beat the best-of-126 bar; half-year sign is the same in all periods for 5 of 122 arms with 4+ half-years of n >= 100 | None | none |

## 4. Per-arm tables (empirical p, SD ratio, placebo mean, overlap, n_eff, bootstrap t, best-of-N bar, half-year signs)
## Gross screen (session-extreme fade, 2026-10-15)

Trials counted N = 90. Single-arm placebo bar (95th pct of placebo t_gross, pooled over the 3 arms below) = 1.55; best-of-90 bar (95th pct of the max of 90 placebo arms, independence assumed) = 3.45. The study's own pass rule needs t_gross >= 2 + 0.14/SE per arm.

| arm | n | mean G % | pub mean | SE | placebo mean | pub control | p (mean) | p (t) | SD ratio | t_gross | need t_gross (pass rule) | overlap share | n_eff | boot t_net | conflict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T (flow-confirmed) d=1 h=60 | 40 | -0.0568 | - | 0.1304 | -0.0050 | - | 0.706 | 0.638 | 0.75 | -0.44 | 3.07 | 0.00 | 40 | -1.48 | 0.000 |
| notF d=1 h=60 | 1399 | -0.0067 | - | 0.0253 | -0.0018 | - | 0.630 | 0.577 | 0.67 | -0.27 | 7.53 | 0.03 | 1381 | -6.69 | 0.000 |
| C (all encounters) d=1 h=60 | 1439 | -0.0081 | - | 0.0245 | -0.0019 | - | 0.654 | 0.597 | 0.66 | -0.33 | 7.70 | 0.03 | 1419 | -6.90 | 0.000 |

Half-year mean gross % (n), arms with n >= 100:

| arm | 2022H1 | 2022H2 | 2023H1 | 2023H2 | 2024H1 | signs |
|---|---|---|---|---|---|---|
| notF d=1 h=60 | +0.009 (300) | +0.100 (259) | -0.062 (263) | -0.045 (289) | -0.031 (288) | 2+/3- |
| C (all encounters) d=1 h=60 | +0.002 (312) | +0.098 (263) | -0.065 (271) | -0.043 (294) | -0.027 (299) | 2+/3- |

## MAL BB mid engulf

Trials counted N = 39. Single-arm placebo bar (95th pct of placebo t_gross, pooled over the 2 arms below) = 1.52; best-of-39 bar (95th pct of the max of 39 placebo arms, independence assumed) = 2.74. The study's own pass rule needs t_gross >= 2 + 0.14/SE per arm.

| arm | n | mean G % | pub mean | SE | placebo mean | pub control | p (mean) | p (t) | SD ratio | t_gross | need t_gross (pass rule) | overlap share | n_eff | boot t_net | conflict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 h=30 | 1179 | 0.0013 | 0.0013 | 0.0132 | -0.0008 | -0.0000 | 0.428 | 0.435 | 0.92 | 0.10 | 12.57 | 0.00 | 1179 | -9.22 | 0.000 |
| A1 h=60 | 1179 | 0.0124 | 0.0124 | 0.0212 | -0.0019 | 0.0013 | 0.179 | 0.231 | 0.76 | 0.59 | 8.61 | 0.00 | 1179 | -5.74 | 0.000 |
| A1 h=120 | 1179 | 0.0146 | 0.0146 | 0.0293 | -0.0063 | 0.0077 | 0.178 | 0.210 | 0.80 | 0.50 | 6.77 | 0.30 | 995 | -4.13 | 0.000 |
| A1 h=240 | 1179 | -0.0158 | -0.0158 | 0.0421 | -0.0127 | -0.0005 | 0.521 | 0.498 | 0.75 | -0.38 | 5.33 | 0.59 | 754 | -3.64 | 0.000 |
| A2 h=30 | 807 | 0.0091 | 0.0091 | 0.0185 | 0.0001 | 0.0009 | 0.256 | 0.292 | 0.76 | 0.49 | 9.57 | 0.00 | 807 | -6.66 | 0.000 |
| A2 h=60 | 807 | 0.0143 | 0.0143 | 0.0257 | -0.0009 | 0.0358 | 0.238 | 0.289 | 0.81 | 0.55 | 7.44 | 0.00 | 807 | -4.45 | 0.000 |
| A2 h=120 | 807 | 0.0270 | 0.0270 | 0.0345 | -0.0073 | 0.0152 | 0.121 | 0.151 | 0.84 | 0.78 | 6.06 | 0.21 | 718 | -2.80 | 0.000 |
| A2 h=240 | 807 | 0.0167 | 0.0167 | 0.0505 | -0.0133 | -0.0993 | 0.203 | 0.226 | 0.79 | 0.33 | 4.77 | 0.43 | 603 | -2.47 | 0.000 |

Half-year mean gross % (n), arms with n >= 100:

| arm | 2022H1 | 2022H2 | 2023H1 | 2023H2 | 2024H1 | signs |
|---|---|---|---|---|---|---|
| A1 h=30 | +0.023 (297) | -0.020 (273) | -0.006 (209) | -0.023 (189) | +0.028 (211) | 2+/3- |
| A1 h=60 | +0.039 (297) | +0.006 (273) | +0.006 (209) | -0.048 (189) | +0.043 (211) | 4+/1- |
| A1 h=120 | +0.079 (297) | +0.007 (273) | +0.028 (209) | -0.019 (189) | -0.050 (211) | 3+/2- |
| A1 h=240 | +0.049 (297) | +0.026 (273) | +0.018 (209) | -0.099 (189) | -0.121 (211) | 3+/2- |
| A2 h=30 | +0.054 (216) | -0.028 (181) | -0.005 (135) | -0.020 (132) | +0.028 (143) | 2+/3- |
| A2 h=60 | +0.060 (216) | -0.005 (181) | +0.016 (135) | -0.031 (132) | +0.010 (143) | 3+/2- |
| A2 h=120 | +0.118 (216) | -0.003 (181) | +0.041 (135) | -0.004 (132) | -0.057 (143) | 2+/3- |
| A2 h=240 | +0.149 (216) | +0.078 (181) | -0.003 (135) | -0.105 (132) | -0.129 (143) | 2+/3- |

## OPR BB MTF centre

Trials counted N = 6. Single-arm placebo bar (95th pct of placebo t_gross, pooled over the 2 arms below) = 1.58; best-of-6 bar (95th pct of the max of 6 placebo arms, independence assumed) = 2.43. The study's own pass rule needs t_gross >= 2 + 0.14/SE per arm.

| arm | n | mean G % | pub mean | SE | placebo mean | pub control | p (mean) | p (t) | SD ratio | t_gross | need t_gross (pass rule) | overlap share | n_eff | boot t_net | conflict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AU h=60 | 194 | 0.0121 | 0.0121 | 0.0598 | 0.0026 | 0.0034 | 0.395 | 0.436 | 0.69 | 0.20 | 4.34 | 0.00 | 194 | -2.03 | 0.000 |
| AU h=120 | 194 | 0.0196 | 0.0196 | 0.0824 | 0.0102 | 0.0162 | 0.450 | 0.473 | 0.73 | 0.24 | 3.70 | 0.00 | 194 | -1.43 | 0.000 |
| AU h=240 | 194 | -0.0112 | -0.0112 | 0.1094 | 0.0108 | 0.0207 | 0.591 | 0.577 | 0.77 | -0.10 | 3.28 | 0.00 | 194 | -1.22 | 0.000 |
| AD h=60 | 282 | -0.0098 | -0.0098 | 0.0266 | 0.0081 | -0.0314 | 0.711 | 0.735 | 1.30 | -0.37 | 7.27 | 0.00 | 282 | -5.37 | 0.000 |
| AD h=120 | 282 | 0.0322 | 0.0322 | 0.0397 | -0.0041 | -0.0387 | 0.240 | 0.193 | 1.25 | 0.81 | 5.52 | 0.00 | 282 | -2.69 | 0.000 |
| AD h=240 | 282 | 0.0243 | 0.0243 | 0.0644 | -0.0096 | -0.0433 | 0.305 | 0.297 | 1.09 | 0.38 | 4.17 | 0.00 | 282 | -1.95 | 0.000 |

Half-year mean gross % (n), arms with n >= 100:

| arm | 2022H1 | 2022H2 | 2023H1 | 2023H2 | 2024H1 | signs |
|---|---|---|---|---|---|---|
| AU h=60 | -0.099 (39) | -0.004 (55) | -0.012 (33) | +0.136 (32) | +0.071 (35) | 2+/3- |
| AU h=120 | +0.019 (39) | -0.109 (55) | +0.022 (33) | +0.139 (32) | +0.111 (35) | 4+/1- |
| AU h=240 | -0.212 (39) | -0.025 (55) | -0.049 (33) | +0.181 (32) | +0.095 (35) | 2+/3- |
| AD h=60 | -0.149 (58) | +0.123 (50) | -0.009 (60) | +0.023 (58) | -0.018 (56) | 2+/3- |
| AD h=120 | -0.050 (58) | +0.118 (50) | -0.004 (60) | +0.102 (58) | +0.006 (56) | 3+/2- |
| AD h=240 | -0.277 (58) | +0.197 (50) | +0.048 (60) | +0.100 (58) | +0.079 (56) | 4+/1- |

## Weekly-low round sweep

Trials counted N = 12. Single-arm placebo bar (95th pct of placebo t_gross, pooled over the 2 arms below) = 1.61; best-of-12 bar (95th pct of the max of 12 placebo arms, independence assumed) = 2.49. The study's own pass rule needs t_gross >= 2 + 0.14/SE per arm.

| arm | n | mean G % | pub mean | SE | placebo mean | pub control | p (mean) | p (t) | SD ratio | t_gross | need t_gross (pass rule) | overlap share | n_eff | boot t_net | conflict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RL h=30 | 685 | 0.0326 | 0.0326 | 0.0272 | -0.0041 | 0.0297 | 0.017 | 0.069 | 0.61 | 1.20 | 7.16 | 0.00 | 685 | -3.97 | 0.000 |
| RL h=60 | 685 | 0.0317 | 0.0317 | 0.0335 | -0.0044 | -0.0004 | 0.063 | 0.126 | 0.69 | 0.95 | 6.18 | 0.01 | 683 | -3.03 | 0.000 |
| RL h=120 | 685 | 0.0942 | 0.0942 | 0.0491 | -0.0031 | 0.0837 | 0.005 | 0.024 | 0.70 | 1.92 | 4.85 | 0.13 | 635 | -0.92 | 0.000 |
| AS h=30 | 525 | -0.0606 | -0.0606 | 0.0339 | 0.0022 | -0.0111 | 1.000 | 0.970 | 0.57 | -1.79 | 6.13 | 0.00 | 525 | -7.36 | 0.000 |
| AS h=60 | 525 | -0.0389 | -0.0389 | 0.0462 | 0.0020 | -0.0268 | 0.933 | 0.839 | 0.60 | -0.84 | 5.03 | 0.00 | 525 | -4.20 | 0.000 |
| AS h=120 | 525 | -0.1415 | -0.1415 | 0.0543 | 0.0001 | -0.0427 | 1.000 | 0.999 | 0.68 | -2.60 | 4.58 | 0.06 | 508 | -5.92 | 0.000 |

Half-year mean gross % (n), arms with n >= 100:

| arm | 2022H1 | 2022H2 | 2023H1 | 2023H2 | 2024H1 | signs |
|---|---|---|---|---|---|---|
| RL h=30 | +0.036 (229) | -0.040 (93) | +0.043 (105) | +0.065 (73) | +0.046 (185) | 4+/1- |
| RL h=60 | +0.121 (229) | -0.034 (93) | +0.044 (105) | +0.021 (73) | -0.049 (185) | 3+/2- |
| RL h=120 | +0.147 (229) | -0.015 (93) | +0.099 (105) | +0.038 (73) | +0.103 (185) | 4+/1- |
| AS h=30 | -0.081 (180) | +0.018 (70) | -0.017 (71) | -0.007 (49) | -0.109 (155) | 1+/4- |
| AS h=60 | -0.116 (180) | +0.134 (70) | -0.028 (71) | -0.055 (49) | -0.027 (155) | 1+/4- |
| AS h=120 | -0.146 (180) | +0.080 (70) | -0.234 (71) | -0.121 (49) | -0.200 (155) | 1+/4- |

## Pre-open tops

Trials counted N = 26. Single-arm placebo bar (95th pct of placebo t_gross, pooled over the 2 arms below) = 1.67; best-of-26 bar (95th pct of the max of 26 placebo arms, independence assumed) = 2.90. The study's own pass rule needs t_gross >= 2 + 0.14/SE per arm.

| arm | n | mean G % | pub mean | SE | placebo mean | pub control | p (mean) | p (t) | SD ratio | t_gross | need t_gross (pass rule) | overlap share | n_eff | boot t_net | conflict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 h=60 | 105 | -0.0111 | -0.0111 | 0.0929 | 0.0057 | -0.0768 | 0.587 | 0.578 | 0.85 | -0.12 | 3.51 | 0.00 | 105 | -1.71 | 0.000 |
| H1 h=180 | 105 | 0.0126 | 0.0126 | 0.1643 | 0.0408 | -0.0590 | 0.575 | 0.577 | 0.79 | 0.08 | 2.85 | 0.00 | 105 | -0.85 | 0.000 |
| H1 h=390 | 105 | -0.0646 | -0.0646 | 0.2427 | 0.0058 | -0.2178 | 0.628 | 0.611 | 0.80 | -0.27 | 2.58 | 0.00 | 105 | -0.87 | 0.000 |
| H2 h=60 | 104 | 0.0373 | 0.0373 | 0.0814 | -0.0020 | 0.0566 | 0.289 | 0.311 | 0.89 | 0.46 | 3.72 | 0.00 | 104 | -1.21 | 0.000 |
| H2 h=180 | 104 | 0.0714 | 0.0714 | 0.1254 | 0.0095 | -0.0050 | 0.297 | 0.306 | 0.95 | 0.57 | 3.12 | 0.08 | 100 | -0.61 | 0.000 |
| H2 h=390 | 104 | 0.2913 | 0.2913 | 0.1985 | 0.0842 | 0.0748 | 0.101 | 0.160 | 0.81 | 1.47 | 2.71 | 0.08 | 100 | 0.89 | 0.000 |

Half-year mean gross % (n), arms with n >= 100:

| arm | 2022H1 | 2022H2 | 2023H1 | 2023H2 | 2024H1 | signs |
|---|---|---|---|---|---|---|
| H1 h=60 | +0.129 (20) | +0.024 (21) | +0.152 (20) | -0.128 (23) | -0.206 (21) | 3+/2- |
| H1 h=180 | +0.006 (20) | +0.271 (21) | +0.165 (20) | -0.240 (23) | -0.108 (21) | 3+/2- |
| H1 h=390 | -0.152 (20) | -0.072 (21) | +0.029 (20) | -0.356 (23) | +0.256 (21) | 2+/3- |
| H2 h=60 | +0.070 (17) | +0.171 (20) | +0.096 (26) | -0.079 (21) | -0.079 (20) | 3+/2- |
| H2 h=180 | +0.045 (17) | -0.233 (20) | +0.465 (26) | +0.034 (21) | -0.073 (20) | 3+/2- |
| H2 h=390 | +0.075 (17) | +0.030 (20) | +0.927 (26) | +0.151 (21) | +0.058 (20) | same sign |

## Candle close (126 arms)

Trials counted N = 126. Single-arm placebo bar (95th pct of placebo t_gross, pooled over the 126 arms below) = 1.66; best-of-126 bar (95th pct of the max of 126 placebo arms, independence assumed) = 3.35. The study's own pass rule needs t_gross >= 2 + 0.14/SE per arm.

Arms with empirical p < 0.05: 3 of 126 (chance alone gives 6.3); arms above the best-of-126 bar: 0. Placebo SD / published SE: median 1.10, max 1.62, arms above 1.2: 29. Lowest-p 12 arms shown.

| arm | n | mean G % | pub mean | SE | placebo mean | pub control | p (mean) | p (t) | SD ratio | t_gross | need t_gross (pass rule) | overlap share | n_eff | boot t_net | conflict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tf15 day reclaim | 431 | 0.0687 | 0.0687 | 0.0258 | -0.0033 | - | 0.005 | 0.004 | 1.05 | 2.66 | 7.42 | 0.29 | 368 | -2.94 | 0.000 |
| tf2 day reclaim | 760 | 0.0387 | 0.0387 | 0.0168 | -0.0025 | - | 0.030 | 0.009 | 1.26 | 2.30 | 10.34 | 0.49 | 573 | -5.97 | 0.000 |
| tf15 week reclaim | 144 | 0.0932 | 0.0932 | 0.0447 | 0.0024 | - | 0.039 | 0.030 | 1.11 | 2.09 | 5.13 | 0.26 | 124 | -1.08 | 0.000 |
| tf3 week strong_break | 339 | 0.0541 | 0.0541 | 0.0309 | -0.0002 | - | 0.056 | 0.045 | 1.10 | 1.75 | 6.52 | 0.52 | 251 | -2.41 | 0.000 |
| tf30 week retest | 204 | 0.0661 | 0.0661 | 0.0418 | -0.0000 | - | 0.057 | 0.056 | 1.04 | 1.58 | 5.35 | 0.00 | 204 | -1.59 | 0.000 |
| tf15 4h retest | 1528 | 0.0214 | 0.0214 | 0.0137 | -0.0004 | - | 0.059 | 0.061 | 0.98 | 1.56 | 12.20 | 0.07 | 1471 | -9.28 | 0.014 |
| tf5 4h retest | 1672 | 0.0201 | 0.0201 | 0.0140 | 0.0001 | - | 0.068 | 0.084 | 0.92 | 1.43 | 12.00 | 0.19 | 1513 | -7.77 | 0.031 |
| tf15 4h rejection | 1621 | 0.0190 | 0.0190 | 0.0123 | -0.0009 | - | 0.068 | 0.058 | 1.08 | 1.54 | 13.39 | 0.16 | 1491 | -10.54 | 0.024 |
| tf1 week reclaim | 333 | 0.0446 | 0.0446 | 0.0284 | -0.0007 | - | 0.088 | 0.066 | 1.15 | 1.57 | 6.93 | 0.53 | 245 | -3.46 | 0.000 |
| tf60 week rejection | 175 | 0.0595 | 0.0595 | 0.0343 | -0.0014 | - | 0.094 | 0.037 | 1.33 | 1.73 | 6.08 | 0.00 | 175 | -2.40 | 0.000 |
| tf1 day break | 1170 | 0.0210 | 0.0210 | 0.0147 | -0.0007 | - | 0.095 | 0.069 | 1.18 | 1.43 | 11.52 | 0.82 | 690 | -6.69 | 0.003 |
| tf60 week retest | 140 | 0.0660 | 0.0660 | 0.0395 | -0.0083 | - | 0.096 | 0.042 | 1.39 | 1.67 | 5.55 | 0.00 | 140 | -1.95 | 0.000 |

Half-year mean gross % (n), arms with n >= 100:

| arm | 2022H1 | 2022H2 | 2023H1 | 2023H2 | 2024H1 | signs |
|---|---|---|---|---|---|---|
| tf15 day reclaim | +0.202 (78) | +0.097 (109) | -0.040 (88) | +0.057 (77) | +0.031 (79) | 4+/1- |
| tf2 day reclaim | +0.034 (150) | +0.091 (169) | +0.013 (150) | +0.036 (135) | +0.014 (156) | same sign |
| tf15 week reclaim | +0.109 (20) | +0.236 (24) | +0.114 (28) | +0.002 (28) | +0.053 (44) | same sign |
| tf3 week strong_break | +0.011 (59) | +0.128 (61) | +0.081 (48) | +0.108 (63) | -0.007 (108) | 4+/1- |
| tf30 week retest | +0.128 (33) | +0.014 (36) | +0.172 (32) | -0.082 (44) | +0.117 (59) | 4+/1- |
| tf15 4h retest | +0.059 (247) | +0.002 (319) | +0.040 (320) | -0.031 (327) | +0.047 (315) | 4+/1- |
| tf5 4h retest | +0.114 (285) | +0.009 (346) | -0.001 (344) | +0.012 (349) | -0.017 (348) | 3+/2- |
| tf15 4h rejection | +0.047 (269) | +0.010 (335) | +0.027 (337) | -0.029 (348) | +0.048 (332) | 4+/1- |
| tf1 week reclaim | -0.016 (65) | +0.008 (61) | +0.048 (55) | +0.054 (53) | +0.100 (99) | 4+/1- |
| tf60 week rejection | +0.133 (24) | -0.034 (30) | +0.216 (30) | -0.031 (40) | +0.059 (51) | 3+/2- |
| tf1 day break | +0.051 (217) | +0.021 (262) | +0.021 (230) | -0.017 (213) | +0.028 (248) | 4+/1- |
| tf60 week retest | +0.121 (18) | -0.067 (24) | +0.193 (25) | -0.027 (34) | +0.122 (39) | 3+/2- |


## 5. LC1 fair null (lead L8)
Fair control: for every candidate level of a family, 20 random lines whose distance from the midnight open is drawn from that family's own distances in the same calendar month, sign random, counted only when touched, hold rate = holds / touches. Same HOLD rule, stop width and 2,000-draw day bootstrap as levels_hold.py. The published run was reproduced on the same bars first (out/lc1_orig_reproduction.csv, matches the Q79 table in levels_hold.md: True).
Last column: share of the published-style control lines that equal the real level (sign agrees) / that are never touched.

| family | real touches | real HOLD | published random | published diff pp | published | fair control HOLD | fair diff pp | fair 95% CI pp | fair verdict | pub-ctl = real level / untouched |
|---|---|---|---|---|---|---|---|---|---|---|
| 4h_fractal_high | 1984 | 46.3% | 36.4% | +9.9 | KEEP | 49.8% | -3.5 | [-5.9, -1.0] | DROP | 50% / 71% |
| 4h_fractal_low | 1963 | 44.9% | 34.9% | +10.0 | KEEP | 50.0% | -5.1 | [-7.3, -2.6] | DROP | 50% / 71% |
| daily_open | 822 | 49.3% | 48.0% | +1.3 | DROP | 49.4% | -0.1 | [-3.1, +2.8] | DROP | 77% / 0% |
| naked_poc | 732 | 53.1% | 41.4% | +11.7 | KEEP | 50.6% | +2.6 | [-0.8, +6.1] | DROP | 51% / 65% |
| prior_day_high | 380 | 37.6% | 30.9% | +6.7 | KEEP | 49.5% | -11.9 | [-16.5, -7.1] | DROP | 51% / 53% |
| prior_day_low | 345 | 40.9% | 33.3% | +7.6 | KEEP | 49.7% | -8.8 | [-14.1, -3.7] | DROP | 50% / 57% |
| prior_day_poc | 583 | 52.7% | 43.9% | +8.7 | KEEP | 51.1% | +1.6 | [-2.3, +5.5] | DROP | 50% / 32% |
| prior_day_vah | 537 | 48.2% | 42.5% | +5.8 | KEEP | 50.7% | -2.4 | [-6.6, +1.8] | DROP | 50% / 35% |
| prior_day_val | 539 | 52.3% | 43.5% | +8.8 | KEEP | 50.9% | +1.4 | [-2.8, +5.4] | DROP | 49% / 37% |
| prior_week_high | 150 | 44.7% | 34.1% | +10.5 | KEEP | 50.1% | -5.4 | [-13.5, +2.6] | DROP | 50% / 82% |
| prior_week_low | 124 | 43.5% | 34.2% | +9.4 | KEEP | 48.2% | -4.6 | [-13.1, +3.7] | DROP | 49% / 85% |
| round_1000 | 831 | 45.0% | 35.9% | +9.1 | KEEP | 50.3% | -5.3 | [-8.3, -1.8] | DROP | 50% / 59% |

Survivors on the fair control: . Published KEEP: 4h_fractal_high, 4h_fractal_low, naked_poc, prior_day_high, prior_day_low, prior_day_poc, prior_week_high, round_1000. Lost: 4h_fractal_high, 4h_fractal_low, naked_poc, prior_day_high, prior_day_low, prior_day_poc, prior_week_high, round_1000.

## 6. Leads
| Lead | Status | Evidence |
|---|---|---|
| L7 | CONFIRMED as a risk, CLEARED as a verdict flip | F1 (no correction in headline(); no arm beats best-of-N), F3 (overlap only where hold > cooldown) |
| L8 | CONFIRMED | F5: control lines are the real level in about half the draws and untouched lines are non-holds; fair control changes the KEEP list as shown |

## 7. Not checked
- BLOCKED: LC1 on the footprint window 2024-12-02..2025-03-31 (the brief asks for it): that window lies inside VALIDATION and this run may not read VALIDATION returns; standard DEV was used instead, so no exposure row was written.
- candle_close placebo uses the 1m tape returns h=60 with no delay and no funding (the study's own forward() definition), not the footprint or the 0.14 % cost; arms with fewer than 100 events have no half-year row.
- Best-of-N assumes the N trials are independent draws from the pooled placebo t; nested variants are correlated, so the bar is conservative (too high).

## 8. Decisions taken
- DECISION (OURS): placebo events are drawn uniformly from all DEV 1m bars with the same UTC weekday and 15-minute slot (UTC, so the NY-open arms are matched on UTC clock, not on the NY clock); the cooldown rule of the study (60 or 120 minutes, same side) is enforced by redrawing conflicting events; candle_close uses one event per side and UTC day (its dedupe rule) with at most 12 redraw rounds (unresolved share printed in the conflict column).
- DECISION (OURS): empirical p is one-sided upper tail on the side-signed mean gross; t for the best-of-N null is gross mean / clustered SE.
- DECISION (OURS): trial counts N: trials.csv rows per study (mal_bb 39, opr_bb 6, wlow 12, preopen 26), candle_close 126 (TRIAL_REGISTRY), gross screen 90 (3 arms x 5 delays x 6 horizons).
- DECISION (OURS): effective n = number of connected hold groups (events whose holds touch are one group).
- DECISION (OURS) D1: LC1 rerun on standard DEV, not the footprint window (VALIDATION rule); fair control = 20 lines per candidate level, distances from the same family and calendar month, both signs, touched only.
- DECISION (OURS): the raw card for F5 is NOT created from this worktree (tasks.py new writes outside the card scope); the Supervisor files it: `python scripts/dev/tasks.py new "Re-state LC1 KEEP list on the touched-only fair control" --lane SONNET --prio 2 --ref MyTradingSys/research/dsa_backtest_audit_2026-10-16/T05_placebo_nulls.md`.

## 9. Bridge log
Not applicable: run directly by a worktree builder session (no AIBridge). Worked best: one study per process in parallel chunks, each writing its own CSV. Failed and recovered: candle_close redraw loop (64 s per arm) fixed by redrawing only conflicting rows and capping rounds. Rule for the next chat: profile the first arm before launching 126.

## 10. Handover
1. Top fix: re-state the LC1 KEEP list (F5) in MyTradingSys/research/levels_confluence_2026-10-14/levels_hold.py using a touched-only, distance-matched control.
2. Test that proves it: the control draws never equal the real level and untouched lines are excluded from the denominator (scripts/T05/t05_lc1.py is the reference).
3. Risk: any layer that consumed the 8 KEEP families as priors.
4. Registration lines needed (central files, not edited here): scripts/dev/run_extra_tests.py -> MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T05/test_placebo_nulls.py.
5. Rerun after the fix: python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T05/t05_lc1.py then build_report.py.
