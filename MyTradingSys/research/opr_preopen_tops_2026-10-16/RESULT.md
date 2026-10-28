INCONCLUSIVE

# RESULT: OPR-PREOPEN-TOPS, break speed vs session outcome, DEV screen (primary cell d=1 min delay, h=60, cost 0.14 % round trip)

**Screen, ran before G3 marks by operator decision 2026-10-16.** DEV-only exploration (bars before 2024-07-01); VALIDATION and HOLDOUT were not read. Rules frozen in PRE_REG.md (committed before this file). Labels: SOURCED = the operator's words in the draft; every threshold, entry, horizon and cost choice below is OURS, written in PRE_REG.md before the run (the operator's reads state no entry or stop).

Study word = INCONCLUSIVE (rule: PASS if any verdict arm passes; FAIL only if every arm is FAIL; otherwise INCONCLUSIVE). Verdict arms: H1 INCONCLUSIVE; H2 INCONCLUSIVE.

## Verdict arms (mean G in % of notional after 1 bp-per-settlement funding; SE day-clustered; control = the other S1 groups, same side and horizon)

| arm | n | mean G % (after funding) | SE (day-cl.) | net of 0.14 % | t_net | n_ctrl | mean_ctrl | DIFF vs ctrl % | t_DIFF | MDD (% clip) | MDE 80 % (2.8 SE) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H1: S1 quick, SHORT at the break close, h=60 | 105 | -0.0111 | 0.0929 | -0.1511 | -1.63 | 203 | -0.0768 | 0.0657 | 0.57 | 17.34 | 0.2601 | INCONCLUSIVE |
| H2: S1 slow, LONG at the break close, h=60 | 104 | 0.0373 | 0.0814 | -0.1027 | -1.26 | 204 | 0.0566 | -0.0193 | -0.18 | 15.11 | 0.2280 | INCONCLUSIVE |

Buy-and-hold DEV max drawdown 67.80 % (of price). PASS needs n >= 200, mean >= 0.14 %, t_net >= 2, DIFF >= +0.05 % with t >= 2, MDD <= BH MDD. MDE at 80 % power = 2.8 x SE (column above).

## Secondary cells (all computed cells printed; no verdict, cannot rescue a FAIL)

| arm | n | mean G % (after funding) | SE (day-cl.) | net of 0.14 % | t_net | n_ctrl | mean_ctrl | DIFF vs ctrl % | t_DIFF | MDD (% clip) | MDE 80 % (2.8 SE) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 quick SHORT h=60 | 105 | -0.0111 | 0.0929 | -0.1511 | -1.63 | 203 | -0.0768 | 0.0657 | 0.57 | 17.34 | 0.2601 | secondary |
| S1 slow LONG h=60 | 104 | 0.0373 | 0.0814 | -0.1027 | -1.26 | 204 | 0.0566 | -0.0193 | -0.18 | 15.11 | 0.2280 | secondary |
| S1 quick SHORT h=180 | 105 | 0.0126 | 0.1643 | -0.1274 | -0.78 | 203 | -0.0590 | 0.0716 | 0.38 | 22.22 | 0.4600 | secondary |
| S1 slow LONG h=180 | 104 | 0.0714 | 0.1254 | -0.0686 | -0.55 | 204 | -0.0050 | 0.0765 | 0.45 | 12.63 | 0.3510 | secondary |
| S1 quick SHORT h=390 | 105 | -0.0646 | 0.2427 | -0.2046 | -0.84 | 203 | -0.2178 | 0.1532 | 0.58 | 32.35 | 0.6797 | secondary |
| S1 slow LONG h=390 | 104 | 0.2913 | 0.1985 | 0.1513 | 0.76 | 204 | 0.0748 | 0.2164 | 0.86 | 12.54 | 0.5557 | secondary |
| S2 quick SHORT h=60 | 103 | -0.0834 | 0.1135 | -0.2234 | -1.97 | 205 | -0.0399 | -0.0435 | -0.34 | 26.45 | 0.3179 | secondary |
| S2 slow LONG h=60 | 103 | -0.0257 | 0.0773 | -0.1657 | -2.14 | 205 | 0.0882 | -0.1139 | -1.08 | 20.73 | 0.2165 | secondary |
| S2 quick SHORT h=180 | 103 | -0.1176 | 0.1560 | -0.2576 | -1.65 | 205 | 0.0071 | -0.1247 | -0.66 | 37.65 | 0.4367 | secondary |
| S2 slow LONG h=180 | 103 | -0.1923 | 0.1335 | -0.3323 | -2.49 | 205 | 0.1279 | -0.3201 | -1.92 | 42.98 | 0.3738 | secondary |
| S2 quick SHORT h=390 | 103 | -0.3804 | 0.1889 | -0.5204 | -2.75 | 205 | -0.0576 | -0.3227 | -1.23 | 63.45 | 0.5290 | secondary |
| S2 slow LONG h=390 | 103 | 0.0025 | 0.2280 | -0.1375 | -0.60 | 205 | 0.2210 | -0.2184 | -0.86 | 37.51 | 0.6383 | secondary |
| S3 quick SHORT h=60 | 122 | -0.0633 | 0.0887 | -0.2033 | -2.29 | 186 | -0.0486 | -0.0146 | -0.13 | 25.68 | 0.2484 | secondary |
| S3 slow LONG h=60 | 112 | -0.0090 | 0.0719 | -0.1490 | -2.07 | 196 | 0.0838 | -0.0928 | -0.89 | 18.89 | 0.2014 | secondary |
| S3 quick SHORT h=180 | 122 | -0.0125 | 0.1493 | -0.1525 | -1.02 | 186 | -0.0491 | 0.0366 | 0.20 | 20.26 | 0.4179 | secondary |
| S3 slow LONG h=180 | 112 | -0.0192 | 0.1267 | -0.1592 | -1.26 | 196 | 0.0436 | -0.0628 | -0.38 | 26.74 | 0.3547 | secondary |
| S3 quick SHORT h=390 | 122 | 0.0573 | 0.2088 | -0.0827 | -0.40 | 186 | -0.3117 | 0.3690 | 1.47 | 22.95 | 0.5847 | secondary |
| S3 slow LONG h=390 | 112 | 0.2673 | 0.2400 | 0.1273 | 0.53 | 196 | 0.0797 | 0.1876 | 0.70 | 17.74 | 0.6720 | secondary |
| S1 median split quick SHORT h=60 | 158 | -0.0338 | 0.0797 | -0.1738 | -2.18 | 150 | -0.0762 | 0.0424 | 0.40 | 28.80 | 0.2231 | secondary |
| S1 median split slow LONG h=60 | 150 | 0.0705 | 0.0723 | -0.0695 | -0.96 | 158 | 0.0307 | 0.0398 | 0.38 | 16.00 | 0.2024 | secondary |
| S1 median split quick SHORT h=180 | 158 | -0.0058 | 0.1355 | -0.1458 | -1.08 | 150 | -0.0650 | 0.0593 | 0.34 | 33.39 | 0.3793 | secondary |
| S1 median split slow LONG h=180 | 150 | 0.0577 | 0.1145 | -0.0823 | -0.72 | 158 | -0.0142 | 0.0719 | 0.41 | 21.91 | 0.3206 | secondary |
| S1 median split quick SHORT h=390 | 158 | -0.1859 | 0.2034 | -0.3259 | -1.60 | 150 | -0.1442 | -0.0416 | -0.16 | 68.00 | 0.5696 | secondary |
| S1 median split slow LONG h=390 | 150 | 0.1290 | 0.1728 | -0.0110 | -0.06 | 158 | 0.1659 | -0.0368 | -0.15 | 28.20 | 0.4840 | secondary |

## Mean G by group, side and horizon (S1/S2/S3 tertiles; S2 quick = top tertile, S3 slow = top dwell tertile)

| def | group | side | h | n | mean G % | SE | net of 0.14 % |
|---|---|---|---|---|---|---|---|
| S1 | quick | SHORT | 60 | 105 | -0.0111 | 0.0929 | -0.1511 |
| S1 | quick | SHORT | 180 | 105 | 0.0126 | 0.1643 | -0.1274 |
| S1 | quick | SHORT | 390 | 105 | -0.0646 | 0.2427 | -0.2046 |
| S1 | quick | LONG | 60 | 105 | 0.0100 | 0.0929 | -0.1300 |
| S1 | quick | LONG | 180 | 105 | -0.0326 | 0.1643 | -0.1726 |
| S1 | quick | LONG | 390 | 105 | 0.0446 | 0.2427 | -0.0954 |
| S1 | mid | SHORT | 60 | 99 | -0.1149 | 0.1062 | -0.2549 |
| S1 | mid | SHORT | 180 | 99 | -0.0425 | 0.1600 | -0.1825 |
| S1 | mid | SHORT | 390 | 99 | -0.1253 | 0.2176 | -0.2653 |
| S1 | mid | LONG | 60 | 99 | 0.1061 | 0.1063 | -0.0339 |
| S1 | mid | LONG | 180 | 99 | 0.0242 | 0.1600 | -0.1158 |
| S1 | mid | LONG | 390 | 99 | 0.1069 | 0.2176 | -0.0331 |
| S1 | slow | SHORT | 60 | 104 | -0.0406 | 0.0815 | -0.1806 |
| S1 | slow | SHORT | 180 | 104 | -0.0747 | 0.1254 | -0.2147 |
| S1 | slow | SHORT | 390 | 104 | -0.3059 | 0.1985 | -0.4459 |
| S1 | slow | LONG | 60 | 104 | 0.0373 | 0.0814 | -0.1027 |
| S1 | slow | LONG | 180 | 104 | 0.0714 | 0.1254 | -0.0686 |
| S1 | slow | LONG | 390 | 104 | 0.2913 | 0.1985 | 0.1513 |
| S2 | quick | SHORT | 60 | 103 | -0.0834 | 0.1135 | -0.2234 |
| S2 | quick | SHORT | 180 | 103 | -0.1176 | 0.1560 | -0.2576 |
| S2 | quick | SHORT | 390 | 103 | -0.3804 | 0.1889 | -0.5204 |
| S2 | quick | LONG | 60 | 103 | 0.0781 | 0.1136 | -0.0619 |
| S2 | quick | LONG | 180 | 103 | 0.1052 | 0.1559 | -0.0348 |
| S2 | quick | LONG | 390 | 103 | 0.3625 | 0.1889 | 0.2225 |
| S2 | mid | SHORT | 60 | 102 | -0.1020 | 0.0887 | -0.2420 |
| S2 | mid | SHORT | 180 | 102 | -0.1648 | 0.1594 | -0.3048 |
| S2 | mid | SHORT | 390 | 102 | -0.0956 | 0.2531 | -0.2356 |
| S2 | mid | LONG | 60 | 102 | 0.0983 | 0.0888 | -0.0417 |
| S2 | mid | LONG | 180 | 102 | 0.1507 | 0.1595 | 0.0107 |
| S2 | mid | LONG | 390 | 102 | 0.0780 | 0.2532 | -0.0620 |
| S2 | slow | SHORT | 60 | 103 | 0.0216 | 0.0775 | -0.1184 |
| S2 | slow | SHORT | 180 | 103 | 0.1773 | 0.1336 | 0.0373 |
| S2 | slow | SHORT | 390 | 103 | -0.0200 | 0.2279 | -0.1600 |
| S2 | slow | LONG | 60 | 103 | -0.0257 | 0.0773 | -0.1657 |
| S2 | slow | LONG | 180 | 103 | -0.1923 | 0.1335 | -0.3323 |
| S2 | slow | LONG | 390 | 103 | 0.0025 | 0.2280 | -0.1375 |
| S3 | quick | SHORT | 60 | 122 | -0.0633 | 0.0887 | -0.2033 |
| S3 | quick | SHORT | 180 | 122 | -0.0125 | 0.1493 | -0.1525 |
| S3 | quick | SHORT | 390 | 122 | 0.0573 | 0.2088 | -0.0827 |
| S3 | quick | LONG | 60 | 122 | 0.0590 | 0.0888 | -0.0810 |
| S3 | quick | LONG | 180 | 122 | -0.0030 | 0.1492 | -0.1430 |
| S3 | quick | LONG | 390 | 122 | -0.0756 | 0.2088 | -0.2156 |
| S3 | mid | SHORT | 60 | 74 | -0.1280 | 0.1364 | -0.2680 |
| S3 | mid | SHORT | 180 | 74 | -0.1346 | 0.1863 | -0.2746 |
| S3 | mid | SHORT | 390 | 74 | -0.3536 | 0.2157 | -0.4936 |
| S3 | mid | LONG | 60 | 74 | 0.1248 | 0.1362 | -0.0152 |
| S3 | mid | LONG | 180 | 74 | 0.1206 | 0.1863 | -0.0194 |
| S3 | mid | LONG | 390 | 74 | 0.3358 | 0.2156 | 0.1958 |
| S3 | slow | SHORT | 60 | 112 | 0.0038 | 0.0720 | -0.1362 |
| S3 | slow | SHORT | 180 | 112 | 0.0074 | 0.1266 | -0.1326 |
| S3 | slow | SHORT | 390 | 112 | -0.2841 | 0.2399 | -0.4241 |
| S3 | slow | LONG | 60 | 112 | -0.0090 | 0.0719 | -0.1490 |
| S3 | slow | LONG | 180 | 112 | -0.0192 | 0.1267 | -0.1592 |
| S3 | slow | LONG | 390 | 112 | 0.2673 | 0.2400 | 0.1273 |

## Placebo, report only (same side and hour taken 7 days earlier and later)

| arm | lags | n | mean G % | SE |
|---|---|---|---|---|
| H1: S1 quick, SHORT at the break close, h=60 | -7 d, +7 d | 208 | 0.0403 | 0.0583 |
| H2: S1 slow, LONG at the break close, h=60 | -7 d, +7 d | 207 | -0.0926 | 0.0474 |

## Frequencies with Wilson 95 % CI (draft outcomes; cells with n < 10 are not read)

| def | group | n | close < break close at +1 h | at +3 h | at +6.5 h | 15m upper BB(20,2) tagged within 6.5 h | next higher top exceeded within 6.5 h |
|---|---|---|---|---|---|---|---|
| S1 | quick | 105 | 60/105 = 57.1% [47.6, 66.2] | 64/105 = 61.0% [51.4, 69.7] | 64/105 = 61.0% [51.4, 69.7] | 97/105 = 92.4% [85.7, 96.1] | 63/79 = 79.7% [69.6, 87.1] |
| S1 | mid | 99 | 50/99 = 50.5% [40.8, 60.1] | 54/99 = 54.5% [44.8, 64.0] | 54/99 = 54.5% [44.8, 64.0] | 95/99 = 96.0% [90.1, 98.4] | 52/61 = 85.2% [74.3, 92.0] |
| S1 | slow | 104 | 53/104 = 51.0% [41.5, 60.4] | 61/104 = 58.7% [49.0, 67.6] | 55/104 = 52.9% [43.4, 62.2] | 99/104 = 95.2% [89.2, 97.9] | 51/62 = 82.3% [71.0, 89.8] |
| S2 | quick | 103 | 55/103 = 53.4% [43.8, 62.7] | 60/103 = 58.3% [48.6, 67.3] | 53/103 = 51.5% [41.9, 60.9] | 96/103 = 93.2% [86.6, 96.7] | 59/68 = 86.8% [76.7, 92.9] |
| S2 | mid | 102 | 49/102 = 48.0% [38.6, 57.6] | 55/102 = 53.9% [44.3, 63.3] | 60/102 = 58.8% [49.1, 67.9] | 97/102 = 95.1% [89.0, 97.9] | 52/61 = 85.2% [74.3, 92.0] |
| S2 | slow | 103 | 59/103 = 57.3% [47.6, 66.4] | 64/103 = 62.1% [52.5, 70.9] | 60/103 = 58.3% [48.6, 67.3] | 98/103 = 95.1% [89.1, 97.9] | 55/73 = 75.3% [64.4, 83.8] |
| S3 | quick | 122 | 68/122 = 55.7% [46.9, 64.2] | 72/122 = 59.0% [50.1, 67.3] | 76/122 = 62.3% [53.4, 70.4] | 116/122 = 95.1% [89.7, 97.7] | 66/82 = 80.5% [70.6, 87.6] |
| S3 | mid | 74 | 37/74 = 50.0% [38.9, 61.1] | 43/74 = 58.1% [46.7, 68.7] | 39/74 = 52.7% [41.5, 63.7] | 69/74 = 93.2% [85.1, 97.1] | 39/46 = 84.8% [71.8, 92.4] |
| S3 | slow | 112 | 58/112 = 51.8% [42.6, 60.8] | 64/112 = 57.1% [47.9, 65.9] | 58/112 = 51.8% [42.6, 60.8] | 106/112 = 94.6% [88.8, 97.5] | 61/74 = 82.4% [72.2, 89.4] |

## Flow split (taker delta over the break bar and the 3 bars before; CVD level not used)

| arm | split | n | mean G % | SE |
|---|---|---|---|---|
| H1: S1 quick | delta4 > 0 | 104 | -0.0012 | 0.0933 |
| H1: S1 quick | delta4 <= 0 | 1 | -1.0413 | 0.0000 |
| H2: S1 slow | delta4 > 0 | 101 | 0.0397 | 0.0839 |
| H2: S1 slow | delta4 <= 0 | 3 | -0.0451 | 0.7495 |

## MFE / MAE in ATR(14, 1h) from the entry open (medians; side of the arm)

| arm | h | n | median MFE | median MAE |
|---|---|---|---|---|
| H1: S1 quick | 60 | 105 | 0.76 | 0.74 |
| H1: S1 quick | 180 | 105 | 1.27 | 0.98 |
| H1: S1 quick | 390 | 105 | 1.66 | 1.14 |
| H2: S1 slow | 60 | 104 | 0.69 | 0.56 |
| H2: S1 slow | 180 | 104 | 1.04 | 1.03 |
| H2: S1 slow | 390 | 104 | 1.19 | 1.20 |

## Data and decisions

OI: NOT_IN_DATA on DEV. Funding: flat 1 bp per 00/08/16 UTC settlement crossed (raw_fund archive absent). Participation: not computed (research clip, no fill claim).
A PASS here is a gross-effect finding on the Binance tape only; no entry, stop or rule is adopted.

## Count section (no return or outcome column was computed)

1m bars missing on the DEV tape: 0 of 1313280. Weekdays 650, dropped for a missing open/ATR bar 0, weekdays with >= 1 qualifying top 530.
Qualifying tops 1110; tops broken inside the 390-minute session 514; break events before the 60-minute cooldown 409; events after the cooldown (the ledger) **n = 308**.
S1 tertile cut points (minutes from the open): 33.0 / 114.0. Arm sizes by S1: quick 105, mid 99, slow 104 (verdict arms H1 = quick, H2 = slow; each needs n >= 200).
S2 quick (top tertile) 103, S2 slow 103; S3 quick 122, S3 slow 112 (secondary, no verdict).
OI: NOT_IN_DATA on DEV (metrics archive starts 2025-09-01). Funding: raw_fund archive absent -> flat 1 bp per settlement crossed.
