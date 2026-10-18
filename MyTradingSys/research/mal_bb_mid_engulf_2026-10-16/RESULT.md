FAIL

# RESULT: MAL-BB-MID-ENGULF, midline bounce + bearish engulf + second break, DEV screen (primary cell 1 min extra delay, h=60, cost 0.14 % round trip)

**Screen, ran before G3 marks by operator decision 2026-10-16.** DEV-only exploration (bars before 2024-07-01); VALIDATION and HOLDOUT were not read. Rules frozen in PRE_REG.md (committed before this file). SOURCED = the operator's words in the draft (close below the previous green bar's open, second break lower); every threshold, entry, horizon and cost is OURS, written in PRE_REG.md before the run (the operator states no entry or stop).

Study word = FAIL (PASS if any verdict arm passes; FAIL only if every arm is FAIL; otherwise INCONCLUSIVE). Verdict arms: A1 FAIL; A2 FAIL.

## Verdict arms (mean G % of notional after funding, SHORT; SE day-clustered)

| arm | n | mean G % (after funding) | SE (day-cl.) | net of 0.14 % | t_net | n_ctrl | mean_ctrl | DIFF vs ctrl % | t_DIFF | MDD (% clip) | MDE 80 % (2.8 SE) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1: engulf (a) close, SHORT, h=60 | 1179 | 0.0124 | 0.0212 | -0.1276 | -6.02 | 2486 | 0.0013 | 0.0111 | 0.61 | 151.98 | 0.0593 | FAIL |
| A2: second break close, SHORT, h=60 | 807 | 0.0143 | 0.0257 | -0.1257 | -4.89 | 372 | 0.0358 | -0.0216 | -0.54 | 103.10 | 0.0720 | FAIL |

Controls: A1 = bounce-state bars (falling, wick touch of the mid, HTF on) with NO engulf (a), same 60-minute cooldown, same SHORT h=60. A2 = the engulf events whose next bar did NOT trade below the engulf low, entered at the same bar close. Buy-and-hold DEV max drawdown 67.80 % of price. PASS needs n >= 200, mean >= 0.14 %, t_net >= 2, DIFF >= +0.05 % with t >= 2, MDD <= BH MDD.

## Secondary cells (no verdict; cannot rescue a FAIL)

| arm | n | mean G % (after funding) | SE (day-cl.) | net of 0.14 % | t_net | n_ctrl | mean_ctrl | DIFF vs ctrl % | t_DIFF | MDD (% clip) | MDE 80 % (2.8 SE) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 h=30 | 1179 | 0.0013 | 0.0132 | -0.1387 | -10.47 | 2486 | -0.0000 | 0.0013 | 0.09 | 164.00 | 0.0371 | secondary |
| A2 h=30 | 807 | 0.0091 | 0.0185 | -0.1309 | -7.07 | 372 | 0.0009 | 0.0082 | 0.29 | 106.39 | 0.0518 | secondary |
| A1 h=120 | 1179 | 0.0146 | 0.0293 | -0.1254 | -4.27 | 2486 | 0.0077 | 0.0069 | 0.29 | 151.70 | 0.0822 | secondary |
| A2 h=120 | 807 | 0.0270 | 0.0345 | -0.1130 | -3.27 | 372 | 0.0152 | 0.0118 | 0.22 | 96.47 | 0.0967 | secondary |
| A1 h=240 | 1179 | -0.0158 | 0.0421 | -0.1558 | -3.70 | 2486 | -0.0005 | -0.0153 | -0.55 | 193.03 | 0.1178 | secondary |
| A2 h=240 | 807 | 0.0167 | 0.0505 | -0.1233 | -2.44 | 372 | -0.0993 | 0.1160 | 1.58 | 116.92 | 0.1414 | secondary |
| E3 midline retest close h=60 | 979 | 0.0382 | 0.0229 | -0.1018 | -4.45 | 0 | nan | nan | nan | 104.12 | 0.0641 | secondary |

## Variant grid (entry at the engulf close, SHORT h=60, no control; every cell is a trial)

| arm | n | mean G % (after funding) | SE (day-cl.) | net of 0.14 % | t_net | n_ctrl | mean_ctrl | DIFF vs ctrl % | t_DIFF | MDD (% clip) | MDE 80 % (2.8 SE) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| engulf a, HTF on, x=0.0 | 1179 | 0.0124 | 0.0212 | -0.1276 | -6.02 | 0 | nan | nan | nan | 151.98 | 0.0593 | secondary |
| engulf a, HTF on, x=0.05 | 1348 | -0.0010 | 0.0185 | -0.1410 | -7.63 | 0 | nan | nan | nan | 191.60 | 0.0517 | secondary |
| engulf a, HTF on, x=0.1 | 1553 | -0.0009 | 0.0173 | -0.1409 | -8.14 | 0 | nan | nan | nan | 221.82 | 0.0485 | secondary |
| engulf a, HTF off, x=0.0 | 2793 | 0.0106 | 0.0114 | -0.1294 | -11.31 | 0 | nan | nan | nan | 362.66 | 0.0320 | secondary |
| engulf a, HTF off, x=0.05 | 3222 | 0.0008 | 0.0099 | -0.1392 | -14.06 | 0 | nan | nan | nan | 449.00 | 0.0277 | secondary |
| engulf a, HTF off, x=0.1 | 3717 | 0.0014 | 0.0093 | -0.1386 | -14.90 | 0 | nan | nan | nan | 518.72 | 0.0260 | secondary |
| engulf b, HTF on, x=0.0 | 926 | 0.0190 | 0.0255 | -0.1210 | -4.74 | 0 | nan | nan | nan | 115.84 | 0.0715 | secondary |
| engulf b, HTF on, x=0.05 | 1071 | 0.0160 | 0.0236 | -0.1240 | -5.26 | 0 | nan | nan | nan | 135.24 | 0.0660 | secondary |
| engulf b, HTF on, x=0.1 | 1249 | 0.0080 | 0.0207 | -0.1320 | -6.38 | 0 | nan | nan | nan | 166.76 | 0.0579 | secondary |
| engulf b, HTF off, x=0.0 | 2236 | 0.0072 | 0.0130 | -0.1328 | -10.19 | 0 | nan | nan | nan | 299.83 | 0.0365 | secondary |
| engulf b, HTF off, x=0.05 | 2599 | 0.0039 | 0.0118 | -0.1361 | -11.49 | 0 | nan | nan | nan | 356.21 | 0.0332 | secondary |
| engulf b, HTF off, x=0.1 | 3015 | 0.0026 | 0.0109 | -0.1374 | -12.65 | 0 | nan | nan | nan | 417.97 | 0.0304 | secondary |
| engulf c1, HTF on, x=0.0 | 1179 | 0.0124 | 0.0212 | -0.1276 | -6.02 | 0 | nan | nan | nan | 151.98 | 0.0593 | secondary |
| engulf c1, HTF on, x=0.05 | 1348 | -0.0010 | 0.0185 | -0.1410 | -7.63 | 0 | nan | nan | nan | 191.60 | 0.0517 | secondary |
| engulf c1, HTF on, x=0.1 | 1553 | -0.0009 | 0.0173 | -0.1409 | -8.14 | 0 | nan | nan | nan | 221.82 | 0.0485 | secondary |
| engulf c1, HTF off, x=0.0 | 2793 | 0.0106 | 0.0114 | -0.1294 | -11.31 | 0 | nan | nan | nan | 362.66 | 0.0320 | secondary |
| engulf c1, HTF off, x=0.05 | 3222 | 0.0008 | 0.0099 | -0.1392 | -14.06 | 0 | nan | nan | nan | 449.00 | 0.0277 | secondary |
| engulf c1, HTF off, x=0.1 | 3717 | 0.0014 | 0.0093 | -0.1386 | -14.90 | 0 | nan | nan | nan | 518.72 | 0.0260 | secondary |
| engulf c1.5, HTF on, x=0.0 | 973 | 0.0198 | 0.0229 | -0.1202 | -5.25 | 0 | nan | nan | nan | 118.48 | 0.0641 | secondary |
| engulf c1.5, HTF on, x=0.05 | 1120 | 0.0043 | 0.0200 | -0.1357 | -6.79 | 0 | nan | nan | nan | 153.58 | 0.0560 | secondary |
| engulf c1.5, HTF on, x=0.1 | 1302 | 0.0054 | 0.0185 | -0.1346 | -7.25 | 0 | nan | nan | nan | 178.09 | 0.0519 | secondary |
| engulf c1.5, HTF off, x=0.0 | 2314 | 0.0052 | 0.0124 | -0.1348 | -10.91 | 0 | nan | nan | nan | 313.67 | 0.0346 | secondary |
| engulf c1.5, HTF off, x=0.05 | 2672 | -0.0003 | 0.0112 | -0.1403 | -12.58 | 0 | nan | nan | nan | 375.87 | 0.0312 | secondary |
| engulf c1.5, HTF off, x=0.1 | 3122 | 0.0015 | 0.0104 | -0.1385 | -13.28 | 0 | nan | nan | nan | 436.42 | 0.0292 | secondary |
| engulf c2, HTF on, x=0.0 | 831 | 0.0076 | 0.0247 | -0.1324 | -5.36 | 0 | nan | nan | nan | 111.97 | 0.0692 | secondary |
| engulf c2, HTF on, x=0.05 | 958 | -0.0035 | 0.0215 | -0.1435 | -6.69 | 0 | nan | nan | nan | 138.99 | 0.0601 | secondary |
| engulf c2, HTF on, x=0.1 | 1120 | 0.0052 | 0.0196 | -0.1348 | -6.87 | 0 | nan | nan | nan | 155.21 | 0.0550 | secondary |
| engulf c2, HTF off, x=0.0 | 1961 | 0.0044 | 0.0133 | -0.1356 | -10.21 | 0 | nan | nan | nan | 269.71 | 0.0372 | secondary |
| engulf c2, HTF off, x=0.05 | 2278 | 0.0019 | 0.0121 | -0.1381 | -11.44 | 0 | nan | nan | nan | 316.13 | 0.0338 | secondary |
| engulf c2, HTF off, x=0.1 | 2670 | 0.0071 | 0.0112 | -0.1329 | -11.90 | 0 | nan | nan | nan | 359.35 | 0.0313 | secondary |

## Placebo, report only (A1 side and hour taken 7 days earlier and later)

n = 2335, mean G -0.0033 %, SE 0.0128.

## Frequencies: share of trades with G > 0 (price lower after the entry) at h=60, Wilson 95 % CI

| set | P(G > 0) |
|---|---|
| A1 | 523/1179 = 44.4% [41.5, 47.2] |
| A2 | 369/807 = 45.7% [42.3, 49.2] |
| control (no engulf) | 1147/2486 = 46.1% [44.2, 48.1] |

## MFE / MAE in ATR(14, 5m) from the entry open (A1, medians)

| bars (5m) | n | median MFE | median MAE |
|---|---|---|---|
| 6 | 1179 | 0.98 | 1.05 |
| 12 | 1179 | 1.47 | 1.57 |
| 24 | 1179 | 2.11 | 2.14 |

## Flow / expansion 2 x 2 on A1 (mean G %, SE day-clustered)

| engulf-bar delta | BB width | n | mean G % | SE |
|---|---|---|---|---|
| engulf-bar taker delta < 0 | BB width expanding | 239 | -0.0566 | 0.0516 |
| engulf-bar taker delta < 0 | BB width not expanding | 872 | 0.0189 | 0.0231 |
| engulf-bar taker delta >= 0 | BB width expanding | 15 | 0.3835 | 0.2731 |
| engulf-bar taker delta >= 0 | BB width not expanding | 53 | 0.1117 | 0.1082 |

## Data and decisions

OI/CVD level: OI NOT_IN_DATA on DEV; CVD level not used (windowed delta only). Funding: flat 1 bp per settlement crossed. A PASS here is a gross-effect finding on the Binance tape only.

## Count section (no return or outcome column was computed)

1m bars missing on the DEV tape: 0 of 1313280. 5m bars 262656 (0 incomplete). Bars in a falling state 69174; falling + wick touch of the 5m BB mid in the last 3 bars (x = 0) 26367; + HTF filter on (1h and 4h RSI14 < 50, close below the 1h BB mid) 10673.
Ledger sizes after the 60-minute cooldown, bounce x = 0, HTF on: engulf (a) **n = 1179**, (b) 926, (c) r=1 1179, r=1.5 973, r=2 831; control (bounce state, no engulf (a)) n = 2486.
Second break (next 5m bar trades below the engulf low): arm A2 n = 807; its control (engulf without the second break) n = 372.
OI: NOT_IN_DATA on DEV (metrics archive starts 2025-09-01). Funding: raw_fund archive absent -> flat 1 bp per settlement crossed.
