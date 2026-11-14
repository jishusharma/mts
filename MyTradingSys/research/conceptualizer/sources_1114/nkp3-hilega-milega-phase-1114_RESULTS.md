# nkp3-hilega-milega-phase-1114: NK4 Hilega Milega + Bollinger breakout/fakeout, phase-specific, MTS brains

**VERDICT: FAIL. 0 of 12 DEV-chosen cells pass on VAL (2024+, fee-net at 12 bp); 3 of 12 have net R > 0 and none has a day-cluster CI low above 0. The phase-appropriate direction beat the opposite direction by more than 2 se in 4 of 34 VAL rule x phase rows (9 of 35 on DEV). Zero DEV cells for HM15, HM1h and FO1h.**

Plain reading: inside the 6 BTC phases, with 8 context layers choosing the trades, no cell chosen on 2019-2023 data survived 2024-26 fee-net. The best VAL cell by net R is BO4h ACCUM-RANGE / C1_rsi4h = >=60 / long: n 384, net R +0.324, day-cluster CI low -0.322, placebo p 0.14, BH q 1.00; it is not a PASS (CI spans 0, ex-best-5 -0.334).

Code commit before any outcome: `b39244cb6` (PRE_REG + study + tests). Frozen cells commit: `d23599900` (cells_frozen.json, dev_cells.csv, dev_step_a.csv). VAL was run once afterwards (`run.py val`). Method: `MTS_BRAINS_SPEC_1114.md`; all parameters OURS except where PRE_REG says SOURCED.

Regime mix: days per phase and signals per phase are in the tables below (DEV 2019-2023, VAL 2024-2026). CAPITULATION is under 5% of DEV days (UNDERPOWERED, no kept cell).

## Context
Operator order 2026-11-13: NK tests must be phase specific and apply the MTS brains. Earlier NK1-NK6 used one ADX phase and no context and failed (gross about 0). This study labels every UTC day from BTC with the 6-phase cycle/structure clock (causal, closes through the prior day), reads 8 context layers at the signal bar close, picks at most 3 cells per rule on DEV, freezes them in git, then tests them on VAL once. Rules: NK4 Hilega Milega flips on 15m / 1h / 4h (RSI9, EMA3 vs WMA21, formula OURS) and Bollinger(20,2) breakout and fakeout fade on 1h / 4h (OURS; NK-R11 was 15m only). HTF: 4h RSI and %B and 1D WaveTrend are context layers, HM also runs on 4h. Prices are Binance spot, 20 coins, funding not charged (spot).

## Regime mix
| Phase | DEV days | DEV % | VAL days | VAL % | mean halving age (days) | note |
|---|---|---|---|---|---|---|
| CAPITULATION | 52 | 2.8% | 6 | 0.6% | 709 | UNDERPOWERED (<5% of DEV days, no kept cell) |
| MARKDOWN | 434 | 23.8% | 198 | 18.9% | 768 |  |
| RELIEF | 155 | 8.5% | 34 | 3.2% | 808 |  |
| ACCUM-RANGE | 333 | 18.2% | 156 | 14.9% | 757 |  |
| MARKUP | 605 | 33.1% | 321 | 30.6% | 579 |  |
| DISTRIBUTION | 247 | 13.5% | 333 | 31.8% | 519 |  |

Signals per phase (DEV / VAL):

| Rule | CAPITULATION | MARKDOWN | RELIEF | ACCUM-RANGE | MARKUP | DISTRIBUTION |
|---|---|---|---|---|---|---|
| HM15 DEV / VAL | 21382 / 2692 | 184113 / 89422 | 60784 / 15147 | 136404 / 70413 | 252055 / 149260 | 104104 / 154990 |
| HM1h DEV / VAL | 5341 / 685 | 46173 / 21837 | 15491 / 3700 | 34302 / 17546 | 63442 / 37061 | 25699 / 37850 |
| HM4h DEV / VAL | 1228 / 118 | 11052 / 5375 | 3759 / 955 | 8252 / 4283 | 15286 / 8861 | 6360 / 8830 |
| BO1h DEV / VAL | 1242 / 126 | 11563 / 5328 | 3852 / 945 | 8421 / 4439 | 15843 / 9382 | 6294 / 9755 |
| BO4h DEV / VAL | 235 / 5 | 2766 / 1348 | 1052 / 259 | 2225 / 1116 | 3994 / 2356 | 1474 / 2417 |
| FO1h DEV / VAL | 1250 / 111 | 11537 / 5353 | 3841 / 965 | 8397 / 4457 | 15846 / 9387 | 6335 / 9717 |
| FO4h DEV / VAL | 268 / 21 | 2772 / 1357 | 1021 / 247 | 2162 / 1084 | 3947 / 2327 | 1582 / 2467 |

Sanity windows (listed in the spec, not tuned):

| Window | share labelled as expected | note |
|---|---|---|
| CAPITULATION 2020-03-12..2020-03-15 | 75% | ok ({'CAPITULATION': (3), 'DISTRIBUTION': (1)}) |
| CAPITULATION 2022-06-13..2022-06-18 | 83% | ok ({'CAPITULATION': (5), 'MARKDOWN': (1)}) |
| MARKDOWN 2022-01-01..2022-10-31 | 51% | borderline (51-59%), recorded not retuned ({'MARKDOWN': (154), 'RELIEF': (55), 'ACCUM-RANGE': (47), 'DISTRIBUTION': (26), 'CAPITULATION': (22)}) |
| MARKDOWN 2025-11-01..2026-02-28 | 68% | ok ({'MARKDOWN': (81), 'ACCUM-RANGE': (26), 'DISTRIBUTION': (9), 'CAPITULATION': (3), 'RELIEF': (1)}) |
| MARKUP 2020-11-01..2021-03-31 | 100% | ok ({'MARKUP': (151)}) |
| MARKUP 2023-10-01..2024-03-31 | 68% | ok ({'MARKUP': (124), 'ACCUM-RANGE': (53), 'DISTRIBUTION': (6)}) |

## Step A: per-phase table, DEV 2019-2023 (every phase separate, phase-appropriate direction first)
Right dir = direction the phase allows (CAPITULATION/RELIEF/MARKUP long, MARKDOWN/DISTRIBUTION short, ACCUM-RANGE both, shown as the signal-weighted blend with the long/short split in the last column). cost R = 12 bp x entry / stop distance. Rows with right minus opposite above +2 se: 9 of 35.

| Rule | Phase | Right dir | n | days | gross R | cost R | net R (12bp) | opposite net R | right minus opp (se) |
|---|---|---|---|---|---|---|---|---|---|
| HM15 | CAPITULATION | long | 10756 | 52 | +0.018 | +0.070 | -0.052 | -0.058 | +0.006 (0.034) |
| HM15 | MARKDOWN | short | 91593 | 434 | -0.000 | +0.153 | -0.153 | -0.157 | +0.004 (0.012) |
| HM15 | RELIEF | long | 30340 | 155 | +0.020 | +0.134 | -0.114 | -0.142 | +0.028 (0.018) |
| HM15 | ACCUM-RANGE | both | 136404 | 333 | -0.006 | +0.176 | -0.182 |  | long -0.189 / short -0.175 |
| HM15 | MARKUP | long | 125366 | 605 | +0.002 | +0.132 | -0.130 | -0.150 | +0.020 (0.009) |
| HM15 | DISTRIBUTION | short | 52020 | 247 | -0.006 | +0.139 | -0.145 | -0.145 | -0.000 (0.015) |
| HM1h | CAPITULATION | long | 2776 | 52 | +0.005 | +0.032 | -0.027 | -0.019 | -0.007 (0.056) |
| HM1h | MARKDOWN | short | 22610 | 432 | +0.003 | +0.079 | -0.076 | -0.096 | +0.020 (0.021) |
| HM1h | RELIEF | long | 7311 | 155 | +0.036 | +0.065 | -0.029 | -0.104 | +0.075 (0.035) |
| HM1h | ACCUM-RANGE | both | 34302 | 333 | -0.019 | +0.097 | -0.116 |  | long -0.118 / short -0.113 |
| HM1h | MARKUP | long | 31480 | 605 | +0.003 | +0.065 | -0.062 | -0.100 | +0.038 (0.017) |
| HM1h | DISTRIBUTION | short | 12519 | 247 | +0.034 | +0.070 | -0.035 | -0.065 | +0.030 (0.032) |
| HM4h | CAPITULATION | long | 802 | 50 | +0.001 | +0.014 | -0.013 | -0.012 | -0.001 (0.117) |
| HM4h | MARKDOWN | short | 5397 | 406 | +0.037 | +0.035 | +0.002 | -0.039 | +0.041 (0.040) |
| HM4h | RELIEF | long | 1696 | 145 | +0.093 | +0.032 | +0.061 | -0.107 | +0.169 (0.063) |
| HM4h | ACCUM-RANGE | both | 8252 | 324 | +0.011 | +0.046 | -0.035 |  | long -0.069 / short -0.001 |
| HM4h | MARKUP | long | 7332 | 592 | +0.075 | +0.031 | +0.044 | -0.065 | +0.109 (0.031) |
| HM4h | DISTRIBUTION | short | 3075 | 239 | +0.017 | +0.031 | -0.014 | -0.026 | +0.012 (0.055) |
| BO1h | CAPITULATION | long | 604 | 48 | +0.031 | +0.034 | -0.002 | -0.316 | +0.314 (0.351) |
| BO1h | MARKDOWN | short | 6164 | 385 | +0.057 | +0.077 | -0.020 | -0.112 | +0.093 (0.105) |
| BO1h | RELIEF | long | 2060 | 152 | +0.278 | +0.065 | +0.214 | -0.187 | +0.401 (0.167) |
| BO1h | ACCUM-RANGE | both | 8421 | 319 | +0.078 | +0.096 | -0.018 |  | long -0.048 / short +0.009 |
| BO1h | MARKUP | long | 8506 | 589 | +0.150 | +0.067 | +0.084 | -0.133 | +0.217 (0.078) |
| BO1h | DISTRIBUTION | short | 3196 | 221 | +0.111 | +0.066 | +0.046 | +0.008 | +0.037 (0.173) |
| BO4h | CAPITULATION | long | 111 | 24 | -0.308 | +0.018 | -0.325 | -0.349 | +0.024 (0.396) |
| BO4h | MARKDOWN | short | 1586 | 215 | +0.144 | +0.034 | +0.110 | -0.192 | +0.302 (0.175) |
| BO4h | RELIEF | long | 700 | 125 | +0.231 | +0.032 | +0.199 | +0.019 | +0.180 (0.242) |
| BO4h | ACCUM-RANGE | both | 2225 | 238 | +0.398 | +0.044 | +0.354 |  | long +0.327 / short +0.379 |
| BO4h | MARKUP | long | 2384 | 469 | +0.214 | +0.032 | +0.182 | -0.354 | +0.537 (0.106) |
| BO4h | DISTRIBUTION | short | 731 | 108 | -0.018 | +0.031 | -0.049 | +0.119 | -0.169 (0.241) |
| FO1h | CAPITULATION | long | 649 | 43 | +0.068 | +0.028 | +0.040 | -0.041 | +0.082 (0.181) |
| FO1h | MARKDOWN | short | 5352 | 409 | -0.013 | +0.076 | -0.089 | -0.144 | +0.054 (0.053) |
| FO1h | RELIEF | long | 1755 | 135 | +0.029 | +0.060 | -0.032 | -0.173 | +0.141 (0.079) |
| FO1h | ACCUM-RANGE | both | 8397 | 319 | -0.015 | +0.093 | -0.108 |  | long -0.160 / short -0.049 |
| FO1h | MARKUP | long | 7336 | 537 | -0.028 | +0.060 | -0.089 | -0.147 | +0.059 (0.036) |
| FO1h | DISTRIBUTION | short | 3088 | 232 | +0.013 | +0.070 | -0.056 | -0.004 | -0.052 (0.062) |
| FO4h | CAPITULATION | long | 165 | 19 | +0.175 | +0.011 | +0.164 | +0.083 | +0.081 (0.257) |
| FO4h | MARKDOWN | short | 1110 | 254 | +0.046 | +0.036 | +0.009 | -0.111 | +0.121 (0.091) |
| FO4h | RELIEF | long | 263 | 50 | -0.043 | +0.029 | -0.072 | -0.166 | +0.094 (0.167) |
| FO4h | ACCUM-RANGE | both | 2162 | 223 | -0.132 | +0.043 | -0.175 |  | long -0.188 / short -0.161 |
| FO4h | MARKUP | long | 1528 | 255 | +0.140 | +0.027 | +0.113 | -0.118 | +0.232 (0.064) |
| FO4h | DISTRIBUTION | short | 756 | 157 | +0.129 | +0.034 | +0.095 | -0.032 | +0.127 (0.120) |

## Step A on VAL 2024-2026 (control table, computed after the freeze; unconditional rules, no context)
Rows with right minus opposite above +2 se: 4 of 34.

| Rule | Phase | Right dir | n | days | gross R | cost R | net R (12bp) | opposite net R | right minus opp (se) |
|---|---|---|---|---|---|---|---|---|---|
| HM15 | CAPITULATION | long | 1342 | 6 | +0.100 | +0.112 | -0.012 | -0.171 | +0.159 (0.091) |
| HM15 | MARKDOWN | short | 44618 | 197 | -0.010 | +0.165 | -0.175 | -0.174 | -0.001 (0.016) |
| HM15 | RELIEF | long | 7551 | 34 | -0.003 | +0.204 | -0.207 | -0.218 | +0.011 (0.033) |
| HM15 | ACCUM-RANGE | both | 70413 | 156 | -0.011 | +0.194 | -0.205 |  | long -0.210 / short -0.199 |
| HM15 | MARKUP | long | 75015 | 321 | -0.002 | +0.149 | -0.151 | -0.159 | +0.007 (0.012) |
| HM15 | DISTRIBUTION | short | 77438 | 333 | +0.005 | +0.166 | -0.160 | -0.179 | +0.018 (0.013) |
| HM1h | CAPITULATION | long | 388 | 6 | +0.026 | +0.052 | -0.026 | -0.215 | +0.189 (0.134) |
| HM1h | MARKDOWN | short | 10612 | 197 | +0.004 | +0.085 | -0.082 | -0.072 | -0.010 (0.032) |
| HM1h | RELIEF | long | 1752 | 34 | +0.019 | +0.125 | -0.106 | -0.137 | +0.031 (0.065) |
| HM1h | ACCUM-RANGE | both | 17546 | 156 | +0.002 | +0.110 | -0.108 |  | long -0.113 / short -0.103 |
| HM1h | MARKUP | long | 18179 | 321 | +0.001 | +0.080 | -0.078 | -0.088 | +0.010 (0.024) |
| HM1h | DISTRIBUTION | short | 19019 | 331 | +0.021 | +0.087 | -0.066 | -0.093 | +0.027 (0.025) |
| HM4h | CAPITULATION | long | 110 | 6 | +0.149 | +0.021 | +0.128 | -0.448 | +0.576 (0.158) |
| HM4h | MARKDOWN | short | 2563 | 195 | -0.017 | +0.040 | -0.057 | -0.037 | -0.020 (0.059) |
| HM4h | RELIEF | long | 436 | 34 | -0.009 | +0.061 | -0.070 | -0.139 | +0.069 (0.125) |
| HM4h | ACCUM-RANGE | both | 4283 | 154 | +0.025 | +0.053 | -0.029 |  | long -0.020 / short -0.038 |
| HM4h | MARKUP | long | 4253 | 304 | +0.071 | +0.038 | +0.032 | -0.025 | +0.057 (0.050) |
| HM4h | DISTRIBUTION | short | 4463 | 315 | +0.059 | +0.041 | +0.018 | -0.006 | +0.024 (0.049) |
| BO1h | CAPITULATION | long | 85 | 6 | -0.068 | +0.058 | -0.126 | -0.853 | +0.727 (0.106) |
| BO1h | MARKDOWN | short | 2684 | 188 | -0.057 | +0.084 | -0.141 | -0.097 | -0.044 (0.163) |
| BO1h | RELIEF | long | 551 | 33 | -0.096 | +0.122 | -0.217 | -0.149 | -0.068 (0.275) |
| BO1h | ACCUM-RANGE | both | 4439 | 152 | +0.097 | +0.109 | -0.012 |  | long +0.066 / short -0.079 |
| BO1h | MARKUP | long | 4654 | 304 | +0.141 | +0.082 | +0.059 | -0.136 | +0.195 (0.108) |
| BO1h | DISTRIBUTION | short | 5209 | 312 | +0.147 | +0.085 | +0.062 | -0.028 | +0.090 (0.117) |
| BO4h | CAPITULATION | long | 5 | 1 | -0.057 | +0.022 | -0.080 |  |  |
| BO4h | MARKDOWN | short | 737 | 116 | -0.398 | +0.037 | -0.436 | -0.060 | -0.375 (0.165) |
| BO4h | RELIEF | long | 184 | 28 | -0.088 | +0.060 | -0.148 | -0.267 | +0.119 (0.224) |
| BO4h | ACCUM-RANGE | both | 1116 | 111 | +0.229 | +0.054 | +0.176 |  | long +0.399 / short -0.015 |
| BO4h | MARKUP | long | 1266 | 238 | +0.191 | +0.039 | +0.152 | -0.012 | +0.164 (0.199) |
| BO4h | DISTRIBUTION | short | 1321 | 176 | +0.205 | +0.037 | +0.168 | +0.131 | +0.037 (0.194) |
| FO1h | CAPITULATION | long | 41 | 3 | +0.632 | +0.053 | +0.579 | -0.057 | +0.636 (0.255) |
| FO1h | MARKDOWN | short | 2631 | 186 | +0.090 | +0.087 | +0.003 | -0.009 | +0.012 (0.078) |
| FO1h | RELIEF | long | 382 | 34 | -0.035 | +0.113 | -0.148 | -0.120 | -0.027 (0.136) |
| FO1h | ACCUM-RANGE | both | 4457 | 152 | -0.016 | +0.105 | -0.121 |  | long -0.111 / short -0.132 |
| FO1h | MARKUP | long | 4711 | 289 | -0.026 | +0.073 | -0.099 | -0.133 | +0.034 (0.050) |
| FO1h | DISTRIBUTION | short | 4541 | 303 | -0.007 | +0.088 | -0.096 | -0.160 | +0.064 (0.056) |
| FO4h | CAPITULATION | long | 19 | 1 | +1.340 | +0.019 | +1.321 | +0.429 | +0.892 (0.000) |
| FO4h | MARKDOWN | short | 569 | 119 | +0.069 | +0.041 | +0.028 | +0.061 | -0.033 (0.126) |
| FO4h | RELIEF | long | 60 | 17 | +0.012 | +0.063 | -0.050 | -0.114 | +0.064 (0.176) |
| FO4h | ACCUM-RANGE | both | 1084 | 107 | +0.111 | +0.053 | +0.059 |  | long +0.028 / short +0.099 |
| FO4h | MARKUP | long | 984 | 149 | -0.076 | +0.035 | -0.111 | -0.071 | -0.040 (0.094) |
| FO4h | DISTRIBUTION | short | 1102 | 195 | -0.052 | +0.045 | -0.097 | -0.093 | -0.004 (0.103) |

Unconditional VAL rows per rule (all phases pooled, for reference only, not a headline):

| Rule | VAL signals | gross R | net R (12bp) |
|---|---|---|---|
| HM15 | 481924 | -0.007 | -0.172 |
| HM1h | 118679 | +0.002 | -0.086 |
| HM4h | 28422 | +0.028 | -0.014 |
| BO1h | 29975 | +0.053 | -0.036 |
| BO4h | 7501 | +0.087 | +0.045 |
| FO1h | 29990 | -0.015 | -0.100 |
| FO4h | 7503 | -0.000 | -0.041 |

## DEV-chosen cells on VAL (Step C, run once)
Kept per rule on DEV: HM15 0, HM1h 0, HM4h 3, BO1h 3, BO4h 3, FO1h 0, FO4h 3 (12 cells from 876 eligible cells across 7 rules). Cells that passed VAL: 0 of 12. fee/R = 12 bp x entry / stop distance. C4 (OI) and C5 (funding) were not NO-DATA for any rule (DEV signals with a reading exceed 150).

| Rule | Cell (phase / layer = bucket / dir) | DEV n | DEV net | DEV lo90 | VAL n | days | win% (break-even) | gross R | fee/R | net R | day CI 95% | ex-best-5 | placebo p | BH q | 6bp maker net (fill) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HM4h | RELIEF / C7_rvratio = <0.7 / long | 354 | +0.236 | +0.075 | 115 | 17 | 18% (38%) | -0.193 | +0.070 | -0.263 | [-0.495, -0.002] | -0.451 | 0.99 | 1.00 | -0.227 (97%) | UNDERPOWERED |
| HM4h | ACCUM-RANGE / C3_pctb4h = <0.10 / short | 835 | +0.154 | +0.042 | 475 | 100 | 31% (38%) | -0.040 | +0.048 | -0.088 | [-0.209, +0.039] | -0.194 | 0.12 | 1.00 | -0.102 (96%) | FAIL |
| HM4h | MARKUP / C8_session = EU / long | 2408 | +0.109 | +0.034 | 1513 | 261 | 31% (34%) | +0.010 | +0.040 | -0.029 | [-0.124, +0.070] | -0.095 | 0.21 | 1.00 | -0.029 (98%) | FAIL |
| BO1h | RELIEF / C7_rvratio = <0.7 / long | 427 | +0.544 | +0.135 | 142 | 20 | 15% (36%) | -0.440 | +0.149 | -0.589 | [-0.917, -0.107] | -0.857 | 1.00 | 1.00 | -0.640 (89%) | UNDERPOWERED |
| BO1h | RELIEF / C1_rsi4h = mid / long | 926 | +0.391 | +0.086 | 305 | 31 | 29% (34%) | -0.021 | +0.131 | -0.152 | [-0.624, +0.344] | -0.667 | 0.97 | 1.00 | -0.130 (93%) | FAIL |
| BO1h | MARKUP / C5_fund = >0.03% / long | 2542 | +0.203 | +0.062 | 480 | 50 | 30% (25%) | +0.227 | +0.061 | +0.166 | [-0.266, +0.647] | -0.331 | 0.00 | 1.00 | +0.165 (98%) | FAIL |
| BO4h | ACCUM-RANGE / C1_rsi4h = >=60 / long | 855 | +0.416 | +0.152 | 384 | 105 | 27% (20%) | +0.383 | +0.060 | +0.324 | [-0.322, +1.160] | -0.334 | 0.14 | 1.00 | +0.305 (97%) | FAIL |
| BO4h | ACCUM-RANGE / C7_rvratio = <0.7 / short | 345 | +0.769 | +0.148 | 141 | 44 | 25% (49%) | -0.352 | +0.058 | -0.410 | [-0.617, -0.168] | -0.621 | 1.00 | 1.00 | -0.413 (97%) | UNDERPOWERED |
| BO4h | ACCUM-RANGE / C6_takerdiv = agree / short | 995 | +0.421 | +0.135 | 501 | 88 | 31% (32%) | +0.020 | +0.049 | -0.029 | [-0.417, +0.444] | -0.437 | 0.83 | 1.00 | -0.035 (96%) | FAIL |
| FO4h | MARKUP / C6_takerdiv = bull-div / long | 216 | +0.227 | +0.094 | 150 | 80 | 54% (57%) | -0.019 | +0.033 | -0.052 | [-0.247, +0.151] | -0.198 | 0.80 | 1.00 | -0.040 (99%) | FAIL |
| FO4h | MARKUP / C7_rvratio = >1.3 / long | 263 | +0.198 | +0.065 | 159 | 43 | 61% (56%) | +0.109 | +0.024 | +0.085 | [-0.170, +0.293] | -0.213 | 0.58 | 1.00 | +0.087 (99%) | FAIL |
| FO4h | MARKUP / C3_pctb4h = <0.10 / long | 842 | +0.167 | +0.051 | 584 | 113 | 44% (53%) | -0.134 | +0.034 | -0.168 | [-0.350, +0.024] | -0.294 | 0.53 | 1.00 | -0.152 (100%) | FAIL |

DEV to VAL shrinkage per kept cell:

| Rule | Cell | DEV net | VAL net | shrinkage |
|---|---|---|---|---|
| HM4h | RELIEF / C7_rvratio = <0.7 | +0.236 | -0.263 | -0.499 |
| HM4h | ACCUM-RANGE / C3_pctb4h = <0.10 | +0.154 | -0.088 | -0.241 |
| HM4h | MARKUP / C8_session = EU | +0.109 | -0.029 | -0.138 |
| BO1h | RELIEF / C7_rvratio = <0.7 | +0.544 | -0.589 | -1.133 |
| BO1h | RELIEF / C1_rsi4h = mid | +0.391 | -0.152 | -0.543 |
| BO1h | MARKUP / C5_fund = >0.03% | +0.203 | +0.166 | -0.036 |
| BO4h | ACCUM-RANGE / C1_rsi4h = >=60 | +0.416 | +0.324 | -0.092 |
| BO4h | ACCUM-RANGE / C7_rvratio = <0.7 | +0.769 | -0.410 | -1.179 |
| BO4h | ACCUM-RANGE / C6_takerdiv = agree | +0.421 | -0.029 | -0.450 |
| FO4h | MARKUP / C6_takerdiv = bull-div | +0.227 | -0.052 | -0.279 |
| FO4h | MARKUP / C7_rvratio = >1.3 | +0.198 | +0.085 | -0.114 |
| FO4h | MARKUP / C3_pctb4h = <0.10 | +0.167 | -0.168 | -0.335 |

Controls on VAL (same cell, opposite direction; same bucket in the other phases; unconditional):

| Rule | Cell | opposite dir, same cell (n, net) | same bucket, other phases | unconditional same phase+dir | unconditional rule+dir |
|---|---|---|---|---|---|
| HM4h | RELIEF / C7_rvratio = <0.7 / long | 160, -0.163 | 2671, +0.026 | 436, -0.070 | 14191, -0.004 |
| HM4h | ACCUM-RANGE / C3_pctb4h = <0.10 / short | n<2 | 2549, +0.022 | 2070, -0.038 | 14231, -0.024 |
| HM4h | MARKUP / C8_session = EU / long | 1538, -0.042 | 3160, -0.018 | 4253, +0.032 | 14191, -0.004 |
| BO1h | RELIEF / C7_rvratio = <0.7 / long | 123, +0.015 | 2812, +0.126 | 551, -0.217 | 14551, -0.007 |
| BO1h | RELIEF / C1_rsi4h = mid / long | 297, -0.155 | 8575, -0.038 | 551, -0.217 | 14551, -0.007 |
| BO1h | MARKUP / C5_fund = >0.03% / long | 476, -0.314 | 12, +1.301 | 4654, +0.059 | 14551, -0.007 |
| BO4h | ACCUM-RANGE / C1_rsi4h = >=60 / long | n<2 | 2578, +0.135 | 514, +0.399 | 3676, +0.130 |
| BO4h | ACCUM-RANGE / C7_rvratio = <0.7 / short | 166, +0.836 | 612, +0.057 | 602, -0.015 | 3825, -0.037 |
| BO4h | ACCUM-RANGE / C6_takerdiv = agree / short | 368, +0.535 | 2769, -0.051 | 602, -0.015 | 3825, -0.037 |
| FO4h | MARKUP / C6_takerdiv = bull-div / long | 13, -0.029 | 471, -0.038 | 984, -0.111 | 3825, -0.039 |
| FO4h | MARKUP / C7_rvratio = >1.3 / long | 279, -0.066 | 262, +0.268 | 984, -0.111 | 3825, -0.039 |
| FO4h | MARKUP / C3_pctb4h = <0.10 / long | 2, +0.032 | 1711, +0.012 | 984, -0.111 | 3825, -0.039 |

PASS rule: net R > 0, day-cluster CI low > 0, ex-best-5 > 0, placebo p < 0.05, BH q < 0.10 (family = 12 kept cells), n >= 150. UNDERPOWERED = n < 150 on VAL. Placebo p is a one-sided test of the real mean against 1000 hour-matched random entries in the same cell; a small p only means "beats random", random entries lose about the fee.

## Useful trades now (descriptive only, no advice)
Today's phase label (day 2026-11-13, provisional, built from closes through 2026-11-12) is MARKDOWN; the same BTC label applies to BTC and ETH. Last 10 days:

| Day | Label | Cycle state | BTC close (prior day) | SMA50 | SMA200 | W200 |
|---|---|---|---|---|---|---|
| 2026-11-04 | ACCUM-RANGE | BASE | 77454 | 81967 | 73207 | 67475 |
| 2026-11-05 | ACCUM-RANGE | BASE | 80504 | 82064 | 73231 | 67521 |
| 2026-11-06 | DISTRIBUTION | BASE | 76088 | 82061 | 73243 | 67563 |
| 2026-11-07 | DISTRIBUTION | BASE | 75844 | 82050 | 73243 | 67605 |
| 2026-11-08 | DISTRIBUTION | BASE | 75868 | 81950 | 73240 | 67647 |
| 2026-11-09 | DISTRIBUTION | BASE | 74851 | 81822 | 73224 | 67688 |
| 2026-11-10 | DISTRIBUTION | BASE | 75368 | 81705 | 73209 | 67730 |
| 2026-11-11 | DISTRIBUTION | BASE | 73796 | 81449 | 73191 | 67770 |
| 2026-11-12 | DISTRIBUTION | BASE | 74015 | 81205 | 73173 | 67810 |
| 2026-11-13 | MARKDOWN | BEAR | 71460 | 80946 | 73137 | 67848 |

Kept cells vs now (BTC and ETH, last closed bar of the rule's timeframe):

| Rule | Kept cell | Coin | phase matches today | current bucket of the layer | bucket matches | VAL verdict |
|---|---|---|---|---|---|---|
| HM4h | RELIEF/C7_rvratio=<0.7/long | BTC | False | mid | False | UNDERPOWERED |
| HM4h | RELIEF/C7_rvratio=<0.7/long | ETH | False | mid | False | UNDERPOWERED |
| HM4h | ACCUM-RANGE/C3_pctb4h=<0.10/short | BTC | False | low | True | FAIL |
| HM4h | ACCUM-RANGE/C3_pctb4h=<0.10/short | ETH | False | mid | False | FAIL |
| HM4h | MARKUP/C8_session=EU/long | BTC | False | low | False | FAIL |
| HM4h | MARKUP/C8_session=EU/long | ETH | False | low | False | FAIL |
| BO1h | RELIEF/C7_rvratio=<0.7/long | BTC | False | mid | False | UNDERPOWERED |
| BO1h | RELIEF/C7_rvratio=<0.7/long | ETH | False | mid | False | UNDERPOWERED |
| BO1h | RELIEF/C1_rsi4h=mid/long | BTC | False | low | False | FAIL |
| BO1h | RELIEF/C1_rsi4h=mid/long | ETH | False | low | False | FAIL |
| BO1h | MARKUP/C5_fund=>0.03%/long | BTC | False | NA | False | FAIL |
| BO1h | MARKUP/C5_fund=>0.03%/long | ETH | False | NA | False | FAIL |
| BO4h | ACCUM-RANGE/C1_rsi4h=>=60/long | BTC | False | low | False | FAIL |
| BO4h | ACCUM-RANGE/C1_rsi4h=>=60/long | ETH | False | low | False | FAIL |
| BO4h | ACCUM-RANGE/C7_rvratio=<0.7/short | BTC | False | mid | False | UNDERPOWERED |
| BO4h | ACCUM-RANGE/C7_rvratio=<0.7/short | ETH | False | mid | False | UNDERPOWERED |
| BO4h | ACCUM-RANGE/C6_takerdiv=agree/short | BTC | False | mid | True | FAIL |
| BO4h | ACCUM-RANGE/C6_takerdiv=agree/short | ETH | False | mid | True | FAIL |
| FO4h | MARKUP/C6_takerdiv=bull-div/long | BTC | False | mid | False | FAIL |
| FO4h | MARKUP/C6_takerdiv=bull-div/long | ETH | False | mid | False | FAIL |
| FO4h | MARKUP/C7_rvratio=>1.3/long | BTC | False | mid | False | FAIL |
| FO4h | MARKUP/C7_rvratio=>1.3/long | ETH | False | mid | False | FAIL |
| FO4h | MARKUP/C3_pctb4h=<0.10/long | BTC | False | low | True | FAIL |
| FO4h | MARKUP/C3_pctb4h=<0.10/long | ETH | False | mid | False | FAIL |

Cells active right now (phase and bucket both match): 0. None of the 12 kept cells is active, and none passed VAL anyway.

## Data and provenance
- Spot 5m bars: `F:\MTS\data_cache\binance\<SYM>USDT_5m.npz` (sibling cache, 20 coins, last full day 2026-11-12). Parsed fetches written by this study: `F:\MTS\data_cache\binance_spot\nkp3-hilega-milega-phase-1114\<SYM>USDT_1h_taker.npz` (spot 1h klines incl. taker-buy base volume, C6), `F:\MTS\data_cache\binance\nkp3-hilega-milega-phase-1114\<SYM>USDT_oi_1h.npz` (C4) and `..._funding.npz` (C5), each with `.meta.json` (source, row count, sha256, key ts ms). Derived trades/universes: `F:\MTS\data_cache\mts_brains\nkp3\`.
- First available futures dates: BTC 2020-09-01; all other coins 2021-12-01 (EOS series ends early). Funding first settlement 2020-01 (BTC, ETH, BCH) up to 2020-10 (FIL), last file 2026-10 (monthly, so C5 is NA for the last ~13 days).
- Phase table: own copy `F:\MTS\data_cache\mts_brains\nkp3\phase_daily_nkp3.csv` (a sibling had already written the shared `phase_daily.csv` with another schema). Cross-check against the shared table: 99.93% of days since 2019-01-01 carry the same label (2 differing days of 2,874, MARKUP vs DISTRIBUTION and MARKUP vs RELIEF).
- WaveTrend parameters checked against `backtest/layers/wavetrend/wavetrend.py` (10/21, 0.015, +-53).
- Nothing over 5 MB is tracked (test enforces).

## Gates and tests
`test_study.py`: phase table equals an independent truncated recompute (fails under PHASE_LAG=0 and STUDY_BUG=1), each of the 8 context layers equals its truncated-prefix value and ignores overwritten future data (fails under STUDY_BUG=1), HM and Bollinger signals causal, hand-checked stop/gap/cost numbers (gap through stop fills at the open, 12 bp x 100 / 1 = 0.12 R), random-walk gross R shows no edge, file-size test, and a meta-test that runs the bug variants and requires them to fail.

## Weaknesses and flags
- The Hilega Milega formula is OURS and unverified against NK's chart. The Bollinger variants are OURS.
- BTC-only phase: effective n is days; cell CIs are day-clustered, so many cells have n in the hundreds but 20 to 100 days.
- Four cycles; CAPITULATION and RELIEF are thin. A VAL pass would only mean surviving 2024-26.
- 144 cells per rule with DEV-only selection: DEV lo90 scores are optimistic; shrinkage table above shows DEV net to VAL net.
- Spot prices, no funding charged; taker costs 12 bp round trip on notional; 6 bp maker row uses a next-bar-trade-through fill model.
- Disclosure: one wiring smoke run on BTC+ETH 4h (trade counts and gross means) preceded the PRE_REG commit; it did not change the design. The shared `phase_daily.csv` was not used (see above).
- No orders placed, no `.secrets` or `.env` read.
