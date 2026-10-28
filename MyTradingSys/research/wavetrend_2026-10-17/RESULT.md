# WaveTrend DEV atlas: RESULT (card wavetrend-dev-atlas, run 2026-10-17)

Verdict: **INCONCLUSIVE** - 0 of 9 frozen cells pass the gross DEV screen. FAIL/INCONCLUSIVE: stop; this atlas adopts no rule and the cells are not tuned or re-cut; any strategy needs its own PRE_REG with Binance-venue costs, VALIDATION once, HOLDOUT sealed.

Status: EXPLORATORY BEHAVIOUR TABLE on DEV (2022-01-01..2024-06-30), one run, gross (no fees, no funding). Cells, outcomes, arms and Holm m = 9 exactly as `PRE_REG.md` s5-s6 (committed `cd663831` / `7e75c720`, before `atlas.py`). `atlas.py` raises on any cell not in `PRE_REG.md`. VALIDATION reads: 0. HOLDOUT reads: 0 (the loader refuses bars >= 2024-07-01).

Reproduce: `python atlas.py --out atlas_out` then `python make_result.py` (seed 20261017, 200 draws). Tests: `python -m pytest test_atlas.py`.

## Primary arms (Verdict arms)

Primary outcome: signed gross return open(t+1) -> close(t+12) in the implied direction (reversal toward the centre for A1/A2/C1, direction of the cross for B1, continuation for B2). Means are in percent (SE = day-clustered). Verdict per cell: PASS only if Holm (m = 9) rejects vs the random clock with a positive difference AND the conjunction beats WT-alone and context-alone (|z| > 1.96); otherwise FAIL (no gross edge on DEV), never a strategy verdict.

| arm | n | mean % | SE % | verdict |
|---|---|---|---|---|
| W01 5m A1_L53 trend:trend_with | 3893 | -0.0143 | 0.0108 | FAIL |
| W02 5m A1_L53 htf:htf_mid | 4196 | -0.0078 | 0.0096 | FAIL |
| W03 5m A2_L53 trend:trend_with | 3509 | -0.0043 | 0.0110 | FAIL |
| W04 15m A2_L53 trend:trend_with | 1154 | -0.0209 | 0.0325 | FAIL |
| W05 15m B2 htf:htf_mid | 788 | -0.0578 | 0.0329 | FAIL |
| W06 15m B2 trend:trend_with | 538 | -0.0422 | 0.0402 | FAIL |
| W07 1h C1 trend:trend_with | 298 | -0.0295 | 0.1457 | FAIL |
| W08 1h C1 htf:htf_mid | 271 | 0.0897 | 0.1228 | FAIL |
| W09 1h B1 htf:htf_mid | 947 | 0.0241 | 0.0418 | FAIL |

## Every cell, every arm (primary outcome, bps; hit = share of signed 12-bar returns > 0 with Wilson 95 % CI)

| Cell | TF | Event | Context | Arm | N | Days | Ev/day | Mean bps | SE bps | Hit (CI) | Mean H4 | Mean H48 | MFE med | MAE med | Resp med |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| W01 | 5m | A1_L53 | trend:trend_with | conjunction | 3893 | 910 | 4.28 | -1.43 | 1.08 | 58.4% (56.9-60.0) | -0.49 | -3.46 | 28.8 | -29.8 | 4.0 |
| W01 | 5m | A1_L53 | trend:trend_with | WT alone | 5114 | 912 | 5.61 | -1.07 | 0.93 | 58.2% (56.8-59.5) | -0.67 | -2.07 | 27.5 | -27.9 | 4.0 |
| W01 | 5m | A1_L53 | trend:trend_with | context alone | 3893 | - | - | -0.10 | 0.91 | 52.9% | -0.09 | -0.30 | 23.4 | -23.7 | - |
| W01 | 5m | A1_L53 | trend:trend_with | random clock | 3893 | - | - | -0.11 | 0.95 | 49.9% | -0.11 | -0.05 | 22.7 | -22.8 | - |
| W02 | 5m | A1_L53 | htf:htf_mid | conjunction | 4196 | 908 | 4.62 | -0.78 | 0.96 | 58.3% (56.8-59.8) | -0.70 | -0.63 | 26.0 | -25.5 | 4.0 |
| W02 | 5m | A1_L53 | htf:htf_mid | WT alone | 5114 | 912 | 5.61 | -1.07 | 0.93 | 58.2% (56.8-59.5) | -0.67 | -2.07 | 27.5 | -27.9 | 4.0 |
| W02 | 5m | A1_L53 | htf:htf_mid | context alone | 4196 | - | - | 0.01 | 0.80 | 50.1% | -0.00 | -0.01 | 21.9 | -21.9 | - |
| W02 | 5m | A1_L53 | htf:htf_mid | random clock | 4196 | - | - | -0.18 | 0.88 | 49.9% | -0.03 | -0.13 | 22.5 | -22.6 | - |
| W03 | 5m | A2_L53 | trend:trend_with | conjunction | 3509 | 904 | 3.88 | -0.43 | 1.10 | 57.1% (55.5-58.8) | -1.36 | -2.99 | 26.6 | -27.0 | 1.0 |
| W03 | 5m | A2_L53 | trend:trend_with | WT alone | 4229 | 908 | 4.66 | -0.15 | 0.98 | 56.5% (55.0-58.0) | -0.93 | -1.88 | 25.9 | -25.9 | 1.0 |
| W03 | 5m | A2_L53 | trend:trend_with | context alone | 3509 | - | - | 0.03 | 1.03 | 53.0% | -0.05 | -0.09 | 23.6 | -23.8 | - |
| W03 | 5m | A2_L53 | trend:trend_with | random clock | 3509 | - | - | 0.03 | 0.94 | 49.9% | 0.10 | -0.04 | 23.6 | -23.5 | - |
| W04 | 15m | A2_L53 | trend:trend_with | conjunction | 1154 | 716 | 1.61 | -2.09 | 3.25 | 56.9% (54.1-59.8) | -0.51 | -4.73 | 49.7 | -50.9 | 1.0 |
| W04 | 15m | A2_L53 | trend:trend_with | WT alone | 1369 | 788 | 1.74 | -2.02 | 2.92 | 57.1% (54.5-59.7) | 0.08 | -6.76 | 48.7 | -47.9 | 1.0 |
| W04 | 15m | A2_L53 | trend:trend_with | context alone | 1154 | - | - | -0.29 | 2.93 | 52.6% | -0.12 | -2.47 | 42.6 | -42.8 | - |
| W04 | 15m | A2_L53 | trend:trend_with | random clock | 1154 | - | - | 0.08 | 3.00 | 49.9% | 0.07 | 0.54 | 43.6 | -43.2 | - |
| W05 | 15m | B2 | htf:htf_mid | conjunction | 788 | 511 | 1.54 | -5.78 | 3.29 | 42.1% (38.7-45.6) | -4.60 | 0.48 | 35.1 | -44.9 | 4.0 |
| W05 | 15m | B2 | htf:htf_mid | WT alone | 873 | 556 | 1.57 | -4.55 | 3.08 | 42.7% (39.5-46.0) | -3.35 | 2.19 | 34.9 | -45.1 | 4.0 |
| W05 | 15m | B2 | htf:htf_mid | context alone | 788 | - | - | 0.01 | 3.32 | 50.2% | -0.01 | 0.26 | 40.3 | -39.9 | - |
| W05 | 15m | B2 | htf:htf_mid | random clock | 788 | - | - | 0.17 | 3.36 | 50.1% | 0.18 | -0.28 | 41.4 | -41.3 | - |
| W06 | 15m | B2 | trend:trend_with | conjunction | 538 | 390 | 1.38 | -4.22 | 4.02 | 43.9% (39.7-48.1) | -3.80 | 4.20 | 34.2 | -45.7 | 4.0 |
| W06 | 15m | B2 | trend:trend_with | WT alone | 873 | 556 | 1.57 | -4.55 | 3.08 | 42.7% (39.5-46.0) | -3.35 | 2.19 | 34.9 | -45.1 | 4.0 |
| W06 | 15m | B2 | trend:trend_with | context alone | 538 | - | - | 0.49 | 4.36 | 47.1% | 0.45 | 1.58 | 42.1 | -42.2 | - |
| W06 | 15m | B2 | trend:trend_with | random clock | 538 | - | - | 0.30 | 3.91 | 50.1% | 0.15 | 0.58 | 41.3 | -41.1 | - |
| W07 | 1h | C1 | trend:trend_with | conjunction | 298 | 251 | 1.19 | -2.95 | 14.57 | 57.4% (51.7-62.9) | 6.83 | -45.59 | 112.8 | -91.4 | 3.0 |
| W07 | 1h | C1 | trend:trend_with | WT alone | 392 | 331 | 1.18 | -6.09 | 12.51 | 55.4% (50.4-60.2) | 4.73 | -52.25 | 105.9 | -89.1 | 3.0 |
| W07 | 1h | C1 | trend:trend_with | context alone | 298 | - | - | -1.63 | 12.00 | 51.4% | -0.81 | -9.18 | 91.6 | -93.9 | - |
| W07 | 1h | C1 | trend:trend_with | random clock | 298 | - | - | -0.07 | 11.73 | 50.3% | -0.21 | -0.87 | 95.2 | -94.7 | - |
| W08 | 1h | C1 | htf:htf_mid | conjunction | 271 | 239 | 1.13 | 8.97 | 12.28 | 56.1% (50.1-61.9) | 3.18 | -34.41 | 99.3 | -79.5 | 3.0 |
| W08 | 1h | C1 | htf:htf_mid | WT alone | 392 | 331 | 1.18 | -6.09 | 12.51 | 55.4% (50.4-60.2) | 4.73 | -52.25 | 105.9 | -89.1 | 3.0 |
| W08 | 1h | C1 | htf:htf_mid | context alone | 271 | - | - | -1.00 | 11.36 | 49.8% | -0.05 | -1.82 | 86.1 | -86.7 | - |
| W08 | 1h | C1 | htf:htf_mid | random clock | 271 | - | - | -1.38 | 11.68 | 49.9% | -0.87 | -1.40 | 91.9 | -91.9 | - |
| W09 | 1h | B1 | htf:htf_mid | conjunction | 947 | 562 | 1.69 | 2.41 | 4.18 | 48.0% (44.9-51.2) | 2.47 | 1.09 | 92.0 | -81.9 | 6.0 |
| W09 | 1h | B1 | htf:htf_mid | WT alone | 1116 | 659 | 1.69 | -1.77 | 4.13 | 46.7% (43.8-49.6) | 0.43 | -5.08 | 96.2 | -87.8 | 6.0 |
| W09 | 1h | B1 | htf:htf_mid | context alone | 947 | - | - | -0.90 | 6.14 | 49.7% | -0.29 | -0.88 | 87.8 | -88.6 | - |
| W09 | 1h | B1 | htf:htf_mid | random clock | 947 | - | - | -0.79 | 6.65 | 50.0% | -0.47 | -0.57 | 89.5 | -90.1 | - |

MFE/MAE are medians over bar extremes (upper bounds), 12 bars, implied direction. Response time = bars until wt1 re-crosses wt2 or reaches 0 against the event side, censored at 12. Random clock: 200 draws matched on TF, UTC hour slot and vol tercile, each draw taking the event's own implied direction. Context alone: same bin, bars with no event of that type, hour slot matched, 200 draws with the bar's own side. SE of the two control arms = SD of the 200 draw means. Median episode depth (max side x wt1, outcome only) for A cells: W01 61.9, W02 61.7, W03 63.2, W04 63.7.

## Tests, Holm and honest MDE

| Cell | conj - random clock (bps) | SE | z | p | Holm adj p (m=9) | vs WT alone (diff, z) | vs context alone (diff, z) | Event-days found / PRE_REG | Realised MDE bps (Holm 9, 80 %) | PRE_REG MDE bps (SD x rc SD) | Passes gross DEV |
|---|---|---|---|---|---|---|---|---|---|---|---|
| W01 | -1.32 | 1.44 | -0.91 | 0.362 | 1.000 | -0.36, -0.25 | -1.33, -0.94 | 910 / 910 | 5.22 | 7.09 | no |
| W02 | -0.60 | 1.30 | -0.46 | 0.645 | 1.000 | 0.29, 0.22 | -0.79, -0.63 | 908 / 908 | 4.71 | 7.03 | no |
| W03 | -0.47 | 1.44 | -0.32 | 0.747 | 1.000 | -0.28, -0.19 | -0.47, -0.31 | 904 / 904 | 5.21 | 7.24 | no |
| W04 | -2.17 | 4.42 | -0.49 | 0.623 | 1.000 | -0.07, -0.02 | -1.81, -0.41 | 716 / 716 | 15.98 | 13.91 | no |
| W05 | -5.95 | 4.70 | -1.27 | 0.206 | 1.000 | -1.23, -0.27 | -5.78, -1.24 | 511 / 511 | 16.98 | 16.07 | no |
| W06 | -4.51 | 5.60 | -0.81 | 0.421 | 1.000 | 0.34, 0.07 | -4.71, -0.79 | 390 / 390 | 20.25 | 18.17 | no |
| W07 | -2.88 | 18.70 | -0.15 | 0.878 | 1.000 | 3.14, 0.16 | -1.32, -0.07 | 251 / 251 | 67.60 | 47.32 | no |
| W08 | 10.34 | 16.95 | 0.61 | 0.542 | 1.000 | 15.05, 0.86 | 9.97, 0.60 | 239 / 239 | 61.27 | 47.51 | no |
| W09 | 3.19 | 7.86 | 0.41 | 0.684 | 1.000 | 4.18, 0.71 | 3.31, 0.44 | 562 / 562 | 28.41 | 30.37 | no |

Honest MDE: the realised MDE uses the root-sum-square of the day-clustered SE of the conjunction and the draw SE of the matched random clock (the PRE_REG figure assumes independent unit-variance days, so it is the optimistic bound). Events with an outcome equal the PRE_REG counts except where a signal sits within 12 bars of the series end: W04 1154 with an outcome vs 1155 frozen. Event and event-day counts re-derived before any outcome match PRE_REG for all cells: True.

## Per-cell statement

FAIL here means "does not pass the gross DEV screen", not "no effect": a cell whose realised MDE exceeds any plausible gross effect (W04-W08 at 14-68 bps against a 12-bar mean move of a few bps) is an underpowered null, read as INCONCLUSIVE for that cell.

- **W01** (5m A1_L53 trend:trend_with): conj -1.43 bps vs random clock -0.11 (diff -1.32, z -0.91, Holm adj p 1.000): does NOT pass gross DEV. Realised MDE 5.22 bps: a true effect smaller than this was not detectable here.
- **W02** (5m A1_L53 htf:htf_mid): conj -0.78 bps vs random clock -0.18 (diff -0.60, z -0.46, Holm adj p 1.000): does NOT pass gross DEV. Realised MDE 4.71 bps: a true effect smaller than this was not detectable here.
- **W03** (5m A2_L53 trend:trend_with): conj -0.43 bps vs random clock 0.03 (diff -0.47, z -0.32, Holm adj p 1.000): does NOT pass gross DEV. Realised MDE 5.21 bps: a true effect smaller than this was not detectable here.
- **W04** (15m A2_L53 trend:trend_with): conj -2.09 bps vs random clock 0.08 (diff -2.17, z -0.49, Holm adj p 1.000): does NOT pass gross DEV. Realised MDE 15.98 bps: a true effect smaller than this was not detectable here.
- **W05** (15m B2 htf:htf_mid): conj -5.78 bps vs random clock 0.17 (diff -5.95, z -1.27, Holm adj p 1.000): does NOT pass gross DEV. Realised MDE 16.98 bps: a true effect smaller than this was not detectable here.
- **W06** (15m B2 trend:trend_with): conj -4.22 bps vs random clock 0.30 (diff -4.51, z -0.81, Holm adj p 1.000): does NOT pass gross DEV. Realised MDE 20.25 bps: a true effect smaller than this was not detectable here.
- **W07** (1h C1 trend:trend_with): conj -2.95 bps vs random clock -0.07 (diff -2.88, z -0.15, Holm adj p 1.000): does NOT pass gross DEV. Realised MDE 67.60 bps: a true effect smaller than this was not detectable here.
- **W08** (1h C1 htf:htf_mid): conj 8.97 bps vs random clock -1.38 (diff 10.34, z 0.61, Holm adj p 1.000): does NOT pass gross DEV. Realised MDE 61.27 bps: a true effect smaller than this was not detectable here.
- **W09** (1h B1 htf:htf_mid): conj 2.41 bps vs random clock -0.79 (diff 3.19, z 0.41, Holm adj p 1.000): does NOT pass gross DEV. Realised MDE 28.41 bps: a true effect smaller than this was not detectable here.

## Controls beside the A cells (never cells, never in Holm; unconditioned, same primary outcome, reversal direction)

| TF | Control | N | Days | Mean bps | SE | Random clock bps | diff z | Hit % |
|---|---|---|---|---|---|---|---|---|
| 5m | A3_L53 | 6373 | 911 | 0.70 | 0.82 | -0.14 | 0.75 | 56.5 |
| 5m | A1_L60 | 3353 | 899 | 0.34 | 1.22 | -0.20 | 0.34 | 59.5 |
| 5m | A3_L60 | 3854 | 899 | 2.23 | 1.14 | -0.01 | 1.51 | 57.8 |
| 15m | A3_L53 | 2033 | 829 | -2.15 | 2.90 | -0.13 | -0.55 | 55.7 |
| 15m | A1_L60 | 1122 | 705 | -4.25 | 3.87 | -0.52 | -0.77 | 57.7 |
| 15m | A3_L60 | 1268 | 686 | -2.71 | 3.63 | -0.11 | -0.54 | 55.2 |
| 1h | A3_L53 | 533 | 412 | -13.75 | 11.04 | -0.14 | -0.99 | 50.5 |
| 1h | A1_L60 | 291 | 261 | -24.51 | 14.49 | 0.59 | -1.38 | 46.0 |
| 1h | A3_L60 | 340 | 269 | -33.13 | 15.09 | -0.70 | -1.74 | 45.0 |

## Descriptive rows outside Holm (4h unconditioned, flagged underpowered; C2 on 5m/15m, no cell)

| TF | Event | N | Days | Mean bps | SE | Random clock bps | diff z |
|---|---|---|---|---|---|---|---|
| 4h | A1_L53 | 102 | 102 | -6.48 | 41.90 | 1.80 | -0.14 |
| 4h | A2_L53 | 85 | 85 | -2.57 | 49.90 | -1.33 | -0.02 |
| 4h | B1 | 244 | 204 | 19.77 | 21.69 | -0.32 | 0.58 |
| 4h | B2 | 56 | 56 | 5.14 | 44.83 | -7.99 | 0.18 |
| 4h | C1 | 103 | 101 | -13.20 | 42.06 | -1.86 | -0.20 |
| 4h | C2 | 22 | 21 | -106.62 | 95.35 | -6.92 | -0.75 |
| 5m | C2 | 1207 | 646 | 1.56 | 1.87 | -0.08 | 0.65 |
| 15m | C2 | 402 | 306 | 1.25 | 6.62 | -0.27 | 0.18 |

## Checks

- Observation module vs `wt_parity_ref.py` on DEV bars (max abs difference, wt1 / wt2): 5m: 0.0e+00 / 1.4e-14 over 262456 bars (valid module 262456 = ref 262456); 15m: 0.0e+00 / 1.4e-14 over 87352 bars (valid module 87352 = ref 87352); 1h: 0.0e+00 / 1.4e-14 over 21688 bars (valid module 21688 = ref 21688); 4h: 0.0e+00 / 1.4e-14 over 5272 bars (valid module 5272 = ref 5272). The PRE_REG counts are therefore unchanged by the module.
- Trial ids: WT-A01..WT-A09 = W01..W09, one primary test each (PRE_REG s7). The L=60 and A3 controls and the descriptive rows are not trials.

## Known weaknesses

1. Draw-based controls: the random-clock SE reflects control resampling noise (200 draws), not independent days of the control; the conjunction SE is day-clustered. The difference z treats the arms as independent (the conjunction is a subset of WT-alone, so the WT-alone contrast is conservative).
2. 5m and 15m cells rest on strongly autocorrelated events within a day; the day cluster is the unit.
3. Bin edges, k, c, R_out, G were chosen on DEV counts (PRE_REG s8); VALIDATION is the only independent check and was not opened.
4. The implied direction is a measurement convention, not a rule. A null on the implied direction says nothing about the opposite sign; the signed table above shows which sign each cell leaned.
