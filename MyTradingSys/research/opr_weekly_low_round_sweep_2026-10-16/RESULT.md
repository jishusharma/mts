FAIL

# RESULT: OPR-WEEKLY-LOW-ROUND-SWEEP, weekly low / round-1000 break, reclaim vs acceptance, DEV screen (primary cell 1 min extra delay, h=60, cost 0.14 % round trip)

**Screen, ran before G3 marks by operator decision 2026-10-16.** DEV-only exploration (bars before 2024-07-01); VALIDATION and HOLDOUT were not read. Rules frozen in PRE_REG.md (committed before this file). SOURCED = the operator's words in the draft (weekly low and round numbers taken together; reclaim, acceptance, range); every threshold, entry, horizon and cost is OURS, written in PRE_REG.md before the run (the operator states no entry or stop). Related evidence (a different question, HOLD not sweep-and-reclaim): `research/levels_confluence_2026-10-14/levels_hold.md` (round_1000 KEEP n=322; prior_week_low DROP at n=20).

Study word = FAIL (PASS if any verdict arm passes; FAIL only if every arm is FAIL; otherwise INCONCLUSIVE). Verdict arms: RL FAIL; AS FAIL.

## Verdict arms (pooled ledger, p = 0.1 %; mean G % of notional after funding; SE day-clustered)

| arm | n | mean G % (after funding) | SE (day-cl.) | net of 0.14 % | t_net | n_ctrl | mean_ctrl | DIFF vs ctrl % | t_DIFF | MDD (% clip) | MDE 80 % (2.8 SE) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RL: reclaim within 5 min, LONG at the reclaim close, h=60 | 685 | 0.0317 | 0.0335 | -0.1083 | -3.23 | 375 | -0.0004 | 0.0321 | 0.48 | 75.62 | 0.0939 | FAIL |
| AS: first three closes below, SHORT at the third close, h=60 | 525 | -0.0389 | 0.0462 | -0.1789 | -3.87 | 535 | -0.0268 | -0.0120 | -0.19 | 93.90 | 0.1292 | FAIL |

Controls (same elapsed time, no signal): RL = first breaks with NO close above the level in the first six 1m bars (indices 0-5), LONG at the close of bar index 5. AS = first breaks whose first three closes are NOT all below, SHORT at the close of bar index 2. Buy-and-hold DEV max drawdown 67.80 % of price. PASS needs n >= 200, mean >= 0.14 %, t_net >= 2, DIFF >= +0.05 % with t >= 2, MDD <= BH MDD.

## Secondary cells (no verdict)

| arm | n | mean G % (after funding) | SE (day-cl.) | net of 0.14 % | t_net | n_ctrl | mean_ctrl | DIFF vs ctrl % | t_DIFF | MDD (% clip) | MDE 80 % (2.8 SE) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RL h=30 | 685 | 0.0326 | 0.0272 | -0.1074 | -3.96 | 375 | 0.0297 | 0.0029 | 0.06 | 74.06 | 0.0760 | secondary |
| AS h=30 | 525 | -0.0606 | 0.0339 | -0.2006 | -5.92 | 535 | -0.0111 | -0.0495 | -1.03 | 105.31 | 0.0949 | secondary |
| RL h=120 | 685 | 0.0942 | 0.0491 | -0.0458 | -0.93 | 375 | 0.0837 | 0.0104 | 0.12 | 42.34 | 0.1375 | secondary |
| AS h=120 | 525 | -0.1415 | 0.0543 | -0.2815 | -5.18 | 535 | -0.0427 | -0.0988 | -1.21 | 148.34 | 0.1521 | secondary |
| RL round only h=60 | 634 | 0.0252 | 0.0343 | -0.1148 | -3.35 | 343 | -0.0182 | 0.0434 | 0.63 | 74.21 | 0.0960 | secondary |
| AS round only h=60 | 482 | -0.0249 | 0.0469 | -0.1649 | -3.51 | 495 | -0.0203 | -0.0047 | -0.07 | 79.50 | 0.1314 | secondary |
| RL weekly only h=60 | 51 | 0.1125 | 0.1405 | -0.0275 | -0.20 | 32 | 0.1909 | -0.0784 | -0.39 | 8.44 | 0.3933 | secondary |
| AS weekly only h=60 | 43 | -0.1950 | 0.1789 | -0.3350 | -1.87 | 40 | -0.1081 | -0.0869 | -0.37 | 14.40 | 0.5010 | secondary |
| RL stacked 0.25 % h=60 | 9 | 0.4455 | 0.3224 | 0.3055 | 0.95 | 4 | -1.4511 | 1.8965 | 1.63 | 1.07 | 0.9028 | secondary |
| AS stacked 0.25 % h=60 | 5 | 0.4611 | 1.5860 | 0.3211 | 0.20 | 8 | -0.1413 | 0.6025 | 0.36 | 4.57 | 4.4408 | secondary |

## P(A), P(B), P(C) by family, penetration p, reclaim window k, acceptance m (draft grid; event window 60 min; Wilson 95 % CI; cells with n < 10 are not read)

| set | n | P(A reclaim) | P(B acceptance) | P(C neither) |
|---|---|---|---|---|
| round, p=0.0 %, k=3, m=3 | 1636 | 335/1636 = 20.5% [18.6, 22.5] | 1208/1636 = 73.8% [71.7, 75.9] | 93/1636 = 5.7% [4.7, 6.9] |
| round, p=0.0 %, k=5, m=3 | 1636 | 336/1636 = 20.5% [18.7, 22.6] | 1208/1636 = 73.8% [71.7, 75.9] | 92/1636 = 5.6% [4.6, 6.8] |
| round, p=0.0 %, k=10, m=3 | 1636 | 336/1636 = 20.5% [18.7, 22.6] | 1208/1636 = 73.8% [71.7, 75.9] | 92/1636 = 5.6% [4.6, 6.8] |
| round, p=0.0 %, k=15, m=3 | 1636 | 336/1636 = 20.5% [18.7, 22.6] | 1208/1636 = 73.8% [71.7, 75.9] | 92/1636 = 5.6% [4.6, 6.8] |
| round, p=0.0 %, k=5, m=5 | 1636 | 372/1636 = 22.7% [20.8, 24.8] | 1085/1636 = 66.3% [64.0, 68.6] | 179/1636 = 10.9% [9.5, 12.5] |
| round, p=0.1 %, k=3, m=3 | 1006 | 171/1006 = 17.0% [14.8, 19.4] | 791/1006 = 78.6% [76.0, 81.1] | 44/1006 = 4.4% [3.3, 5.8] |
| round, p=0.1 %, k=5, m=3 | 1006 | 171/1006 = 17.0% [14.8, 19.4] | 791/1006 = 78.6% [76.0, 81.1] | 44/1006 = 4.4% [3.3, 5.8] |
| round, p=0.1 %, k=10, m=3 | 1006 | 171/1006 = 17.0% [14.8, 19.4] | 791/1006 = 78.6% [76.0, 81.1] | 44/1006 = 4.4% [3.3, 5.8] |
| round, p=0.1 %, k=15, m=3 | 1006 | 171/1006 = 17.0% [14.8, 19.4] | 791/1006 = 78.6% [76.0, 81.1] | 44/1006 = 4.4% [3.3, 5.8] |
| round, p=0.1 %, k=5, m=5 | 1006 | 210/1006 = 20.9% [18.5, 23.5] | 708/1006 = 70.4% [67.5, 73.1] | 88/1006 = 8.7% [7.2, 10.7] |
| round, p=0.2 %, k=3, m=3 | 543 | 90/543 = 16.6% [13.7, 19.9] | 433/543 = 79.7% [76.2, 82.9] | 20/543 = 3.7% [2.4, 5.6] |
| round, p=0.2 %, k=5, m=3 | 543 | 90/543 = 16.6% [13.7, 19.9] | 433/543 = 79.7% [76.2, 82.9] | 20/543 = 3.7% [2.4, 5.6] |
| round, p=0.2 %, k=10, m=3 | 543 | 90/543 = 16.6% [13.7, 19.9] | 433/543 = 79.7% [76.2, 82.9] | 20/543 = 3.7% [2.4, 5.6] |
| round, p=0.2 %, k=15, m=3 | 543 | 90/543 = 16.6% [13.7, 19.9] | 433/543 = 79.7% [76.2, 82.9] | 20/543 = 3.7% [2.4, 5.6] |
| round, p=0.2 %, k=5, m=5 | 543 | 105/543 = 19.3% [16.2, 22.9] | 394/543 = 72.6% [68.7, 76.1] | 44/543 = 8.1% [6.1, 10.7] |
| round, p=0.3 %, k=3, m=3 | 332 | 55/332 = 16.6% [13.0, 20.9] | 264/332 = 79.5% [74.9, 83.5] | 13/332 = 3.9% [2.3, 6.6] |
| round, p=0.3 %, k=5, m=3 | 332 | 55/332 = 16.6% [13.0, 20.9] | 264/332 = 79.5% [74.9, 83.5] | 13/332 = 3.9% [2.3, 6.6] |
| round, p=0.3 %, k=10, m=3 | 332 | 55/332 = 16.6% [13.0, 20.9] | 264/332 = 79.5% [74.9, 83.5] | 13/332 = 3.9% [2.3, 6.6] |
| round, p=0.3 %, k=15, m=3 | 332 | 55/332 = 16.6% [13.0, 20.9] | 264/332 = 79.5% [74.9, 83.5] | 13/332 = 3.9% [2.3, 6.6] |
| round, p=0.3 %, k=5, m=5 | 332 | 64/332 = 19.3% [15.4, 23.9] | 244/332 = 73.5% [68.5, 78.0] | 24/332 = 7.2% [4.9, 10.5] |
| weekly, p=0.0 %, k=3, m=3 | 189 | 59/189 = 31.2% [25.0, 38.1] | 118/189 = 62.4% [55.3, 69.0] | 12/189 = 6.3% [3.7, 10.8] |
| weekly, p=0.0 %, k=5, m=3 | 189 | 59/189 = 31.2% [25.0, 38.1] | 118/189 = 62.4% [55.3, 69.0] | 12/189 = 6.3% [3.7, 10.8] |
| weekly, p=0.0 %, k=10, m=3 | 189 | 59/189 = 31.2% [25.0, 38.1] | 118/189 = 62.4% [55.3, 69.0] | 12/189 = 6.3% [3.7, 10.8] |
| weekly, p=0.0 %, k=15, m=3 | 189 | 59/189 = 31.2% [25.0, 38.1] | 118/189 = 62.4% [55.3, 69.0] | 12/189 = 6.3% [3.7, 10.8] |
| weekly, p=0.0 %, k=5, m=5 | 189 | 62/189 = 32.8% [26.5, 39.8] | 109/189 = 57.7% [50.5, 64.5] | 18/189 = 9.5% [6.1, 14.6] |
| weekly, p=0.1 %, k=3, m=3 | 103 | 24/103 = 23.3% [16.2, 32.3] | 76/103 = 73.8% [64.5, 81.3] | 3/103 = 2.9% [1.0, 8.2] |
| weekly, p=0.1 %, k=5, m=3 | 103 | 24/103 = 23.3% [16.2, 32.3] | 76/103 = 73.8% [64.5, 81.3] | 3/103 = 2.9% [1.0, 8.2] |
| weekly, p=0.1 %, k=10, m=3 | 103 | 24/103 = 23.3% [16.2, 32.3] | 76/103 = 73.8% [64.5, 81.3] | 3/103 = 2.9% [1.0, 8.2] |
| weekly, p=0.1 %, k=15, m=3 | 103 | 24/103 = 23.3% [16.2, 32.3] | 76/103 = 73.8% [64.5, 81.3] | 3/103 = 2.9% [1.0, 8.2] |
| weekly, p=0.1 %, k=5, m=5 | 103 | 28/103 = 27.2% [19.5, 36.5] | 71/103 = 68.9% [59.4, 77.1] | 4/103 = 3.9% [1.5, 9.6] |
| weekly, p=0.2 %, k=3, m=3 | 70 | 12/70 = 17.1% [10.1, 27.6] | 56/70 = 80.0% [69.2, 87.7] | 2/70 = 2.9% [0.8, 9.8] |
| weekly, p=0.2 %, k=5, m=3 | 70 | 12/70 = 17.1% [10.1, 27.6] | 56/70 = 80.0% [69.2, 87.7] | 2/70 = 2.9% [0.8, 9.8] |
| weekly, p=0.2 %, k=10, m=3 | 70 | 12/70 = 17.1% [10.1, 27.6] | 56/70 = 80.0% [69.2, 87.7] | 2/70 = 2.9% [0.8, 9.8] |
| weekly, p=0.2 %, k=15, m=3 | 70 | 12/70 = 17.1% [10.1, 27.6] | 56/70 = 80.0% [69.2, 87.7] | 2/70 = 2.9% [0.8, 9.8] |
| weekly, p=0.2 %, k=5, m=5 | 70 | 15/70 = 21.4% [13.4, 32.4] | 52/70 = 74.3% [63.0, 83.1] | 3/70 = 4.3% [1.5, 11.9] |
| weekly, p=0.3 %, k=3, m=3 | 56 | 10/56 = 17.9% [10.0, 29.8] | 44/56 = 78.6% [66.2, 87.3] | 2/56 = 3.6% [1.0, 12.1] |
| weekly, p=0.3 %, k=5, m=3 | 56 | 10/56 = 17.9% [10.0, 29.8] | 44/56 = 78.6% [66.2, 87.3] | 2/56 = 3.6% [1.0, 12.1] |
| weekly, p=0.3 %, k=10, m=3 | 56 | 10/56 = 17.9% [10.0, 29.8] | 44/56 = 78.6% [66.2, 87.3] | 2/56 = 3.6% [1.0, 12.1] |
| weekly, p=0.3 %, k=15, m=3 | 56 | 10/56 = 17.9% [10.0, 29.8] | 44/56 = 78.6% [66.2, 87.3] | 2/56 = 3.6% [1.0, 12.1] |
| weekly, p=0.3 %, k=5, m=5 | 56 | 14/56 = 25.0% [15.5, 37.7] | 39/56 = 69.6% [56.7, 80.1] | 3/56 = 5.4% [1.8, 14.6] |

## P(A), P(B), P(C) at the primary cell (p = 0.1 %, k = 5, m = 3), unconditional and by condition

| set | n | P(A reclaim) | P(B acceptance) | P(C neither) |
|---|---|---|---|---|
| all pooled events (unconditional) | 1060 | 182/1060 = 17.2% [15.0, 19.6] | 832/1060 = 78.5% [75.9, 80.9] | 46/1060 = 4.3% [3.3, 5.7] |
| round-1000 events | 977 | 163/977 = 16.7% [14.5, 19.2] | 771/977 = 78.9% [76.2, 81.4] | 43/977 = 4.4% [3.3, 5.9] |
| prior-week-low events | 83 | 19/83 = 22.9% [15.2, 33.0] | 61/83 = 73.5% [63.1, 81.8] | 3/83 = 3.6% [1.2, 10.1] |
| stacked within 0.10 % | 3 | 1/3 = 33.3% [6.1, 79.2] (n<10, not read) | 2/3 = 66.7% [20.8, 93.9] (n<10, not read) | 0/3 = 0.0% [0.0, 56.2] (n<10, not read) |
| single level (not stacked within 0.10 %) | 1057 | 181/1057 = 17.1% [15.0, 19.5] | 830/1057 = 78.5% [75.9, 80.9] | 46/1057 = 4.4% [3.3, 5.8] |
| stacked within 0.25 % | 13 | 2/13 = 15.4% [4.3, 42.2] | 11/13 = 84.6% [57.8, 95.7] | 0/13 = 0.0% [0.0, 22.8] |
| single level (not stacked within 0.25 %) | 1047 | 180/1047 = 17.2% [15.0, 19.6] | 821/1047 = 78.4% [75.8, 80.8] | 46/1047 = 4.4% [3.3, 5.8] |
| stacked within 0.50 % | 44 | 9/44 = 20.5% [11.2, 34.5] | 34/44 = 77.3% [63.0, 87.2] | 1/44 = 2.3% [0.4, 11.8] |
| single level (not stacked within 0.50 %) | 1016 | 173/1016 = 17.0% [14.8, 19.5] | 798/1016 = 78.5% [75.9, 81.0] | 45/1016 = 4.4% [3.3, 5.9] |
| US-open window (0-60 min after 09:30 NY, weekdays) | 77 | 9/77 = 11.7% [6.3, 20.7] | 65/77 = 84.4% [74.7, 90.9] | 3/77 = 3.9% [1.3, 10.8] |
| not: US-open window | 983 | 173/983 = 17.6% [15.3, 20.1] | 767/983 = 78.0% [75.3, 80.5] | 43/983 = 4.4% [3.3, 5.8] |
| HTF stretch (1h and 4h RSI14 < 35, close below the 4h lower BB) | 108 | 24/108 = 22.2% [15.4, 30.9] | 79/108 = 73.1% [64.1, 80.6] | 5/108 = 4.6% [2.0, 10.4] |
| not: HTF stretch | 952 | 158/952 = 16.6% [14.4, 19.1] | 753/952 = 79.1% [76.4, 81.6] | 41/952 = 4.3% [3.2, 5.8] |
| CVD flip (5-bar delta before < 0 and after > 0; uses 5 bars after the break, descriptive only) | 116 | 51/116 = 44.0% [35.3, 53.0] | 56/116 = 48.3% [39.4, 57.3] | 9/116 = 7.8% [4.1, 14.1] |
| not: CVD flip | 944 | 131/944 = 13.9% [11.8, 16.2] | 776/944 = 82.2% [79.6, 84.5] | 37/944 = 3.9% [2.9, 5.4] |
| break-bar taker delta > 0 | 12 | 3/12 = 25.0% [8.9, 53.2] | 8/12 = 66.7% [39.1, 86.2] | 1/12 = 8.3% [1.5, 35.4] |
| not: break-bar taker delta > 0 | 1048 | 179/1048 = 17.1% [14.9, 19.5] | 824/1048 = 78.6% [76.0, 81.0] | 45/1048 = 4.3% [3.2, 5.7] |

Penetration at the first break bar: median 0.196 %; maximum penetration inside the window: median 0.619 %. Share of C events that stay within 0.3 x ATR(14, 1h) of the level: 0 of 46.

## After A / after B (medians in ATR(14, 1h) from the entry open after the reclaim / acceptance close)

| event | h (min) | n | median MFE | median MAE |
|---|---|---|---|---|
| after A (reclaim close, LONG) | 30 | 182 | 0.52 | 0.19 |
| after B (acceptance close, SHORT) | 30 | 831 | 0.40 | 0.41 |
| after A (reclaim close, LONG) | 60 | 182 | 0.71 | 0.27 |
| after B (acceptance close, SHORT) | 60 | 831 | 0.52 | 0.55 |
| after A (reclaim close, LONG) | 120 | 182 | 0.87 | 0.44 |
| after B (acceptance close, SHORT) | 120 | 831 | 0.67 | 0.74 |

After A: prior 12 h high exceeded within 120 minutes of the reclaim close: 8/182 = 4.4% [2.2, 8.4]. After B: next round-1000 level below reached within 120 minutes of the acceptance close: 123/832 = 14.8% [12.5, 17.4]. Pre-open tops and OI were not used (pre-open top logic belongs to the sibling screen; OI NOT_IN_DATA on DEV).

## Placebo, report only (arm side and hour taken 7 days earlier and later)

| arm | lags | n | mean G % | SE |
|---|---|---|---|---|
| RL | -7 d, +7 d | 1357 | 0.0364 | 0.0209 |
| AS | -7 d, +7 d | 1037 | 0.0079 | 0.0228 |

## Data and decisions

Funding flat 1 bp per settlement crossed. The draft's range outcome C is reported as 'neither A nor B'; the extra ATR-band condition is the share printed above. A PASS would be a gross-effect finding on the Binance tape only.

## Count section (no return and no A/B/C or other outcome column was computed)

1m bars missing on the DEV tape: 0 of 1313280. Prior-week low available on 903 of 912 days.
First-break events after the 60-minute cooldown (all of the previous 60 closes at/above the level, then a 1m low at least p below it):

| penetration p | round-1000 events | prior-week-low events | pooled ledger | pooled events stacked within 0.1 % / 0.25 % / 0.5 % |
|---|---|---|---|---|
| 0.0 % | 1636 | 189 | 1748 | 0.001: 10  0.0025: 23  0.005: 80 |
| 0.1 % | 1006 | 103 | 1060 | 0.001: 3  0.0025: 13  0.005: 44 |
| 0.2 % | 543 | 70 | 581 | 0.001: 1  0.0025: 8  0.005: 25 |
| 0.3 % | 332 | 56 | 365 | 0.001: 1  0.0025: 7  0.005: 20 |

Primary p = 0.1 %: pooled ledger **n = 1060** (round 1006, weekly 103). Arm sizes (reclaim within 5 minutes; first three closes below) depend on the 1m closes after the break and are printed with the outcome run, not here.
OI: NOT_IN_DATA on DEV (metrics archive starts 2025-09-01). Funding: raw_fund archive absent -> flat 1 bp per settlement crossed.
