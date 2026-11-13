VERDICT: NO EDGE - 0 of 1088 testable DEV cells (9 rules x 6 phases x 8 context layers x 3 buckets) had a day-clustered lower 90% bound of net R above 0 at 12 bp, so 0 cells were kept and 0 went to VAL (best DEV score -0.044 R, in CAPITULATION which holds only 2.8% of DEV days; best eligible-phase score -0.071 R). Only CAPITULATION-long is positive in both splits, on 52 DEV days and 6 VAL days: UNDERPOWERED, not a pass

Study nkp4-nk-plus-mts-confluence-1114: the five NK layers combined with MTS context (OI unwind/build, funding extreme, 24h taker-delta divergence, 4h RSI, daily WaveTrend, 4h Bollinger %B, volatility, session) inside six causal BTC phases; NK + MTS agreement counted in the phase direction (rules X1-X3). Method = MTS_BRAINS_SPEC_1114. PRE_REG.md and all study code committed before any outcome (sha bda9e074c); DEV stage ran on signals <= 2023-12-31 only (inputs truncated), cells_frozen.json (empty) committed before the VAL stage. 20 Binance spot USDT coins, 15m. Trade: next open, stop max(1 ATR, 0.5%), target 2R, 24-bar exit, 12 bp round trip taker (6 bp maker row with fill model is only run on kept cells, so none).

## Context
Phase = one label per UTC day from BTC closes through the prior day: CAPITULATION (long only), MARKDOWN (short), RELIEF (long), ACCUM-RANGE (long at lower third / short at upper third of the 40d range), MARKUP (long), DISTRIBUTION (short). Cycle state BEAR/BULL/BASE from drawdown, SMA200, 200-week SMA. Every table below is per phase, in the phase-appropriate direction; there is no pooled-phase headline. Cost R = fee as a fraction of the stop distance (12 bp x entry / stop); net R = gross R - cost R.

Regime mix: BTC days DEV (2019-2023, 1826 days): CAPITULATION 3% / MARKDOWN 24% / RELIEF 8% / ACCUM-RANGE 18% / MARKUP 33% / DISTRIBUTION 14%. VAL (2024-01-01 to 2026-11-13, 1048 days): CAPITULATION 1% / MARKDOWN 19% / RELIEF 3% / ACCUM-RANGE 15% / MARKUP 31% / DISTRIBUTION 32%.
Signals per phase (all rules, both directions), DEV: CAPITULATION 50232, MARKDOWN 375783, RELIEF 128630, ACCUM-RANGE 258767, MARKUP 529043, DISTRIBUTION 215822. VAL: CAPITULATION 6347, MARKDOWN 198540, RELIEF 30387, ACCUM-RANGE 141835, MARKUP 325784, DISTRIBUTION 327922.
Sanity windows (labels, not tuned): CAPITULATION 2020-03-12..15 reads 75% CAPITULATION, 2022-06-13..18 83%; MARKDOWN 2022-01..10 51%, 2025-11..2026-02 68%; MARKUP 2020-11..2021-03 100%, 2023-10..2024-03 68%. CAPITULATION is 2.8% of DEV days (52 days), below the 5% floor, so it cannot supply a kept cell (UNDERPOWERED, not "fail"); it has only 6 VAL days.

## Step A: does the phase-appropriate direction beat the opposite one? (DEV, net of 12 bp)
diff = net R(appropriate) - net R(opposite), day-clustered; se by day-cluster bootstrap. Rows of the confluence rules X1-X3 are the "NK + MTS" test; N1-N5 and NN are the NK-only rules for comparison.

| phase | rule | approp. dir | n app | days | gross R | cost R (12bp) | net R | n opp | opp net R | diff | se |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CAPITULATION | N1_firsthour | long | 1307 | 47 | 0.003 | 0.111 | -0.108 | 1244 | -0.271 | 0.164 | 0.134 |
| CAPITULATION | N2_pivots | long | 2492 | 52 | 0.009 | 0.103 | -0.095 | 2510 | -0.132 | 0.038 | 0.100 |
| CAPITULATION | N3_breakretest | long | 2381 | 52 | -0.000 | 0.102 | -0.102 | 2367 | -0.114 | 0.012 | 0.094 |
| CAPITULATION | N4_hilega | long | 6287 | 52 | 0.051 | 0.102 | -0.051 | 6269 | -0.106 | 0.054 | 0.094 |
| CAPITULATION | N5_rsi3070 | long | 956 | 49 | 0.081 | 0.082 | -0.001 | 851 | -0.172 | 0.171 | 0.143 |
| CAPITULATION | NN_nkcount2 | long | 4477 | 52 | 0.025 | 0.101 | -0.075 | 4496 | -0.141 | 0.065 | 0.085 |
| CAPITULATION | X1_nk+mts>=1 | long | 5168 | 52 | 0.047 | 0.098 | -0.051 | 2884 | -0.135 | 0.083 | 0.093 |
| CAPITULATION | X2_nk+mts>=2 | long | 3635 | 52 | 0.051 | 0.092 | -0.041 | 777 | -0.083 | 0.042 | 0.119 |
| CAPITULATION | X3_nk+mts>=3 | long | 1882 | 46 | 0.137 | 0.084 | 0.052 | 249 | 0.033 | 0.019 | 0.153 |
| MARKDOWN | N1_firsthour | short | 10259 | 428 | 0.037 | 0.194 | -0.157 | 11050 | -0.147 | -0.010 | 0.044 |
| MARKDOWN | N2_pivots | short | 20054 | 433 | 0.015 | 0.188 | -0.173 | 20093 | -0.205 | 0.033 | 0.035 |
| MARKDOWN | N3_breakretest | short | 19307 | 434 | 0.013 | 0.189 | -0.176 | 19177 | -0.205 | 0.029 | 0.034 |
| MARKDOWN | N4_hilega | short | 48396 | 434 | 0.012 | 0.185 | -0.173 | 48056 | -0.200 | 0.027 | 0.031 |
| MARKDOWN | N5_rsi3070 | short | 7247 | 425 | -0.025 | 0.180 | -0.205 | 7971 | -0.192 | -0.013 | 0.051 |
| MARKDOWN | NN_nkcount2 | short | 35023 | 434 | 0.007 | 0.187 | -0.180 | 35333 | -0.192 | 0.012 | 0.032 |
| MARKDOWN | X1_nk+mts>=1 | short | 24722 | 432 | 0.016 | 0.186 | -0.170 | 32092 | -0.180 | 0.010 | 0.034 |
| MARKDOWN | X2_nk+mts>=2 | short | 8669 | 400 | 0.011 | 0.176 | -0.166 | 17747 | -0.165 | -0.000 | 0.039 |
| MARKDOWN | X3_nk+mts>=3 | short | 3172 | 289 | 0.014 | 0.168 | -0.154 | 7415 | -0.167 | 0.014 | 0.051 |
| RELIEF | N1_firsthour | long | 3471 | 151 | 0.077 | 0.182 | -0.105 | 3769 | -0.148 | 0.044 | 0.067 |
| RELIEF | N2_pivots | long | 7155 | 153 | 0.012 | 0.178 | -0.166 | 7063 | -0.218 | 0.052 | 0.055 |
| RELIEF | N3_breakretest | long | 6788 | 154 | -0.008 | 0.179 | -0.187 | 6609 | -0.196 | 0.008 | 0.048 |
| RELIEF | N4_hilega | long | 16594 | 154 | 0.002 | 0.176 | -0.174 | 17033 | -0.200 | 0.026 | 0.048 |
| RELIEF | N5_rsi3070 | long | 2269 | 139 | 0.015 | 0.159 | -0.144 | 2875 | -0.208 | 0.064 | 0.083 |
| RELIEF | NN_nkcount2 | long | 12100 | 154 | -0.003 | 0.177 | -0.179 | 12381 | -0.201 | 0.021 | 0.049 |
| RELIEF | X1_nk+mts>=1 | long | 6536 | 151 | 0.005 | 0.177 | -0.172 | 11504 | -0.161 | -0.010 | 0.052 |
| RELIEF | X2_nk+mts>=2 | long | 2172 | 111 | -0.051 | 0.170 | -0.221 | 6704 | -0.147 | -0.074 | 0.072 |
| RELIEF | X3_nk+mts>=3 | long | 605 | 54 | -0.198 | 0.165 | -0.362 | 3002 | -0.123 | -0.240 | 0.110 |
| ACCUM-RANGE | N1_firsthour | geometry | 7611 | 328 | -0.063 | 0.209 | -0.272 | 7175 | -0.187 | -0.085 | 0.045 |
| ACCUM-RANGE | N2_pivots | geometry | 14393 | 333 | -0.058 | 0.205 | -0.263 | 14389 | -0.170 | -0.092 | 0.038 |
| ACCUM-RANGE | N3_breakretest | geometry | 13652 | 333 | -0.082 | 0.206 | -0.288 | 13707 | -0.164 | -0.124 | 0.037 |
| ACCUM-RANGE | N4_hilega | geometry | 32220 | 333 | -0.046 | 0.200 | -0.247 | 32572 | -0.153 | -0.094 | 0.035 |
| ACCUM-RANGE | N5_rsi3070 | geometry | 5564 | 320 | -0.083 | 0.188 | -0.271 | 4724 | -0.148 | -0.123 | 0.054 |
| ACCUM-RANGE | NN_nkcount2 | geometry | 24187 | 333 | -0.061 | 0.202 | -0.263 | 24064 | -0.160 | -0.103 | 0.033 |
| ACCUM-RANGE | X1_nk+mts>=1 | geometry | 18873 | 333 | -0.062 | 0.199 | -0.261 | 17888 | -0.126 | -0.135 | 0.038 |
| ACCUM-RANGE | X2_nk+mts>=2 | geometry | 9264 | 311 | -0.063 | 0.193 | -0.257 | 7217 | -0.137 | -0.120 | 0.042 |
| ACCUM-RANGE | X3_nk+mts>=3 | geometry | 3260 | 241 | -0.120 | 0.188 | -0.308 | 2767 | -0.169 | -0.139 | 0.055 |
| MARKUP | N1_firsthour | long | 14593 | 592 | -0.032 | 0.173 | -0.205 | 14546 | -0.214 | 0.009 | 0.034 |
| MARKUP | N2_pivots | long | 29573 | 605 | -0.026 | 0.169 | -0.195 | 29116 | -0.192 | -0.004 | 0.026 |
| MARKUP | N3_breakretest | long | 27897 | 605 | -0.035 | 0.171 | -0.206 | 27577 | -0.178 | -0.029 | 0.027 |
| MARKUP | N4_hilega | long | 67475 | 605 | -0.012 | 0.166 | -0.178 | 69617 | -0.163 | -0.015 | 0.024 |
| MARKUP | N5_rsi3070 | long | 9258 | 571 | 0.005 | 0.149 | -0.144 | 10977 | -0.192 | 0.048 | 0.035 |
| MARKUP | NN_nkcount2 | long | 49654 | 605 | -0.022 | 0.167 | -0.189 | 50990 | -0.181 | -0.009 | 0.025 |
| MARKUP | X1_nk+mts>=1 | long | 25605 | 603 | 0.015 | 0.168 | -0.153 | 48230 | -0.142 | -0.011 | 0.028 |
| MARKUP | X2_nk+mts>=2 | long | 9265 | 475 | 0.035 | 0.156 | -0.121 | 27891 | -0.118 | -0.003 | 0.033 |
| MARKUP | X3_nk+mts>=3 | long | 2467 | 277 | 0.043 | 0.160 | -0.117 | 14312 | -0.107 | -0.010 | 0.048 |
| DISTRIBUTION | N1_firsthour | short | 6263 | 244 | -0.036 | 0.176 | -0.212 | 5990 | -0.228 | 0.017 | 0.053 |
| DISTRIBUTION | N2_pivots | short | 11595 | 248 | -0.030 | 0.172 | -0.202 | 11683 | -0.223 | 0.021 | 0.044 |
| DISTRIBUTION | N3_breakretest | short | 11435 | 248 | 0.016 | 0.175 | -0.159 | 11287 | -0.239 | 0.080 | 0.043 |
| DISTRIBUTION | N4_hilega | short | 28374 | 248 | -0.008 | 0.171 | -0.179 | 27676 | -0.190 | 0.011 | 0.039 |
| DISTRIBUTION | N5_rsi3070 | short | 4047 | 241 | -0.035 | 0.167 | -0.202 | 4289 | -0.192 | -0.010 | 0.066 |
| DISTRIBUTION | NN_nkcount2 | short | 20627 | 248 | -0.023 | 0.173 | -0.196 | 20474 | -0.216 | 0.020 | 0.040 |
| DISTRIBUTION | X1_nk+mts>=1 | short | 14854 | 245 | 0.023 | 0.170 | -0.147 | 16532 | -0.210 | 0.063 | 0.044 |
| DISTRIBUTION | X2_nk+mts>=2 | short | 6029 | 221 | 0.063 | 0.162 | -0.099 | 8647 | -0.172 | 0.072 | 0.051 |
| DISTRIBUTION | X3_nk+mts>=3 | short | 2525 | 174 | 0.059 | 0.156 | -0.097 | 3495 | -0.129 | 0.032 | 0.066 |

Reading: phase-appropriate net R is negative in 53 of 54 DEV rows; the one positive row is CAPITULATION X3 (+0.052 R). The largest diff/se ratio is 1.9 (CAPITULATION X3; DISTRIBUTION N3 also 1.9), below 2. The phase direction does not beat the opposite direction in a way that survives noise and pays the fee, so Step B is labelled exploratory per the spec (it was still run, as the spec requires).

CAPITULATION long, the only phase with a consistent sign (DEV vs VAL, 12 bp, per rule):

| rule | DEV n | DEV days | DEV gross R | DEV net R | VAL n | VAL days | VAL gross R | VAL net R | VAL day CI low |
|---|---|---|---|---|---|---|---|---|---|
| N1_firsthour | 1307 | 47 | 0.003 | -0.108 | 127 | 4 | 0.344 | 0.158 | -0.234 |
| N2_pivots | 2492 | 52 | 0.009 | -0.095 | 256 | 6 | 0.161 | 0.006 | -0.431 |
| N3_breakretest | 2381 | 52 | -0.000 | -0.102 | 310 | 6 | 0.162 | 0.004 | -0.324 |
| N4_hilega | 6287 | 52 | 0.051 | -0.051 | 782 | 6 | 0.165 | 0.007 | -0.324 |
| N5_rsi3070 | 956 | 49 | 0.081 | -0.001 | 85 | 5 | 0.271 | 0.143 | -0.532 |
| NN_nkcount2 | 4477 | 52 | 0.025 | -0.075 | 517 | 6 | 0.214 | 0.059 | -0.243 |
| X1_nk+mts>=1 | 5168 | 52 | 0.047 | -0.051 | 650 | 6 | 0.269 | 0.112 | -0.227 |
| X2_nk+mts>=2 | 3635 | 52 | 0.051 | -0.041 | 508 | 6 | 0.325 | 0.171 | -0.236 |
| X3_nk+mts>=3 | 1882 | 46 | 0.137 | 0.052 | 306 | 6 | 0.490 | 0.347 | -0.202 |

Gross R in CAPITULATION long is positive in DEV (up to +0.14 R) and larger in VAL (+0.16 to +0.49 R), but VAL contains 6 CAPITULATION days, so the day-cluster interval is wide and the phase is under the 5% DEV-day floor. It is a lead for a later, separate pre-registration with more symbols or history, not a result of this study.

## Step B: DEV cell selection
Cells testable (n >= 150 signals and >= 40 days): 1088 of 1296. Cells with lower 90% bound > 0: 0 (eligible phases: 0). Kept: 0. Ten best DEV cells by score, none kept:

| rule | phase | layer | bucket | n | days | gross R | cost R | net R | lo90 (score) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| X3_nk+mts>=3 | CAPITULATION | C8_sess | ASIA | 839 | 46 | 0.253 | 0.083 | 0.170 | -0.044 | under 5% of DEV days |
| X3_nk+mts>=3 | CAPITULATION | C5_fund3 | NEG<0 | 1523 | 40 | 0.150 | 0.079 | 0.071 | -0.044 | under 5% of DEV days |
| N4_hilega | CAPITULATION | C5_fund3 | NEG<0 | 2781 | 43 | 0.128 | 0.089 | 0.040 | -0.070 | under 5% of DEV days |
| N1_firsthour | DISTRIBUTION | C1_rsi4h | HIGH>=60 | 1077 | 136 | 0.186 | 0.169 | 0.017 | -0.071 | eligible |
| X3_nk+mts>=3 | CAPITULATION | C2_wt1d | OS<=-53 | 1492 | 44 | 0.102 | 0.088 | 0.014 | -0.071 | under 5% of DEV days |
| X1_nk+mts>=1 | CAPITULATION | C5_fund3 | NEG<0 | 2700 | 43 | 0.096 | 0.088 | 0.008 | -0.085 | under 5% of DEV days |
| X2_nk+mts>=2 | CAPITULATION | C5_fund3 | NEG<0 | 2456 | 43 | 0.089 | 0.088 | 0.002 | -0.093 | under 5% of DEV days |
| X2_nk+mts>=2 | CAPITULATION | C6_td24 | AGREE | 2257 | 48 | 0.094 | 0.085 | 0.009 | -0.097 | under 5% of DEV days |
| N2_pivots | CAPITULATION | C6_td24 | BULL-DIV | 384 | 48 | 0.152 | 0.112 | 0.040 | -0.098 | under 5% of DEV days |
| X3_nk+mts>=3 | MARKDOWN | C2_wt1d | OB>=53 | 316 | 64 | 0.212 | 0.162 | 0.051 | -0.104 | eligible |

In the five phases that can supply cells, no cell's lower bound is above -0.07 R (best: N1 first-hour x DISTRIBUTION x 4h RSI HIGH, net +0.017 R, gross 0.186 R, cost 0.169 R). CAPITULATION cells reach net +0.17 R on 40 to 50 days but their lower bounds stay below 0 and the phase is under the 5% floor.

C4/C5 data limits (futures OI from 2020-09 for BTC, 2021-12 for most others; funding from 2020-01 or listing; spot 1h taker data from 2019 or listing): signals with OI / funding available, per rule (phase-appropriate signals on DEV):

| rule | C4_signals | C5_signals | all_signals |
|---|---|---|---|
| N1_firsthour | 21526 | 36934 | 43504 |
| N2_pivots | 40574 | 72599 | 85262 |
| N3_breakretest | 38869 | 69494 | 81460 |
| N4_hilega | 93591 | 169298 | 199346 |
| N5_rsi3070 | 14608 | 25025 | 29341 |
| NN_nkcount2 | 69305 | 124320 | 146068 |
| X1_nk+mts>=1 | 55096 | 83492 | 95758 |
| X2_nk+mts>=2 | 23083 | 34505 | 39034 |
| X3_nk+mts>=3 | 9469 | 12693 | 13911 |

First available date per coin (OI first date is when the Binance archive starts, not a gap): see `val_results.json` key aux_first. Example: BTC OI 2020-09-01, ETH OI 2021-12-01, FIL OI 2021-12-01, BTC funding 2020-01-01. No cell was marked NO-DATA for a whole rule (every rule has more than 150 DEV signals with OI and funding).

## Step C: DEV-chosen cells on VAL (run once, kept cells only)
No kept cells, so no VAL cell, no placebo, no BH, no maker row. DEV cells passed VAL: 0 of 0 (nothing to shrink). Fee/R reference at 12 bp: cost R per rule is 0.08 to 0.11 R in DEV CAPITULATION and 0.15 to 0.23 R in the other phases (VAL Step A table), against gross R between -0.12 and +0.09 R outside CAPITULATION.

Descriptive only, not selected: the six best VAL Step A rows by net R in the phase-appropriate direction (VAL has 9 of 54 positive rows, all in CAPITULATION, 6 days):

| rule | phase | dir | n | days | gross R | cost R | net R | day CI low (95%) |
|---|---|---|---|---|---|---|---|---|
| X3_nk+mts>=3 | CAPITULATION | long | 306 | 6 | 0.490 | 0.143 | 0.347 | -0.202 |
| X2_nk+mts>=2 | CAPITULATION | long | 508 | 6 | 0.325 | 0.154 | 0.171 | -0.236 |
| N1_firsthour | CAPITULATION | long | 127 | 4 | 0.344 | 0.186 | 0.158 | -0.234 |
| N5_rsi3070 | CAPITULATION | long | 85 | 5 | 0.271 | 0.128 | 0.143 | -0.532 |
| X1_nk+mts>=1 | CAPITULATION | long | 650 | 6 | 0.269 | 0.158 | 0.112 | -0.227 |
| NN_nkcount2 | CAPITULATION | long | 517 | 6 | 0.214 | 0.155 | 0.059 | -0.243 |

VAL Step A per phase and rule (same layout as DEV):

| phase | rule | approp. dir | n app | days | gross R | cost R (12bp) | net R | n opp | opp net R | diff | se |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CAPITULATION | N1_firsthour | long | 127 | 4 | 0.344 | 0.186 | 0.158 | 251 | -0.330 | 0.488 | 0.410 |
| CAPITULATION | N2_pivots | long | 256 | 6 | 0.161 | 0.154 | 0.006 | 233 | -0.210 | 0.216 | 0.288 |
| CAPITULATION | N3_breakretest | long | 310 | 6 | 0.162 | 0.158 | 0.004 | 298 | -0.553 | 0.557 | 0.252 |
| CAPITULATION | N4_hilega | long | 782 | 6 | 0.165 | 0.158 | 0.007 | 734 | -0.367 | 0.374 | 0.295 |
| CAPITULATION | N5_rsi3070 | long | 85 | 5 | 0.271 | 0.128 | 0.143 | 158 | -0.214 | 0.357 | 0.614 |
| CAPITULATION | NN_nkcount2 | long | 517 | 6 | 0.214 | 0.155 | 0.059 | 557 | -0.393 | 0.452 | 0.291 |
| CAPITULATION | X1_nk+mts>=1 | long | 650 | 6 | 0.269 | 0.158 | 0.112 | 469 | -0.346 | 0.458 | 0.243 |
| CAPITULATION | X2_nk+mts>=2 | long | 508 | 6 | 0.325 | 0.154 | 0.171 | 88 | -0.234 | 0.405 | 0.264 |
| CAPITULATION | X3_nk+mts>=3 | long | 306 | 6 | 0.490 | 0.143 | 0.347 | 18 | -0.448 | 0.795 | 0.261 |
| MARKDOWN | N1_firsthour | short | 6176 | 197 | 0.095 | 0.205 | -0.110 | 5835 | -0.262 | 0.152 | 0.064 |
| MARKDOWN | N2_pivots | short | 10698 | 198 | 0.011 | 0.202 | -0.191 | 10764 | -0.240 | 0.048 | 0.045 |
| MARKDOWN | N3_breakretest | short | 10214 | 198 | 0.020 | 0.205 | -0.185 | 10144 | -0.229 | 0.044 | 0.045 |
| MARKDOWN | N4_hilega | short | 24357 | 198 | 0.011 | 0.201 | -0.191 | 24462 | -0.222 | 0.031 | 0.041 |
| MARKDOWN | N5_rsi3070 | short | 3687 | 196 | 0.045 | 0.199 | -0.154 | 3960 | -0.175 | 0.021 | 0.073 |
| MARKDOWN | NN_nkcount2 | short | 18220 | 198 | 0.030 | 0.202 | -0.172 | 18360 | -0.226 | 0.054 | 0.040 |
| MARKDOWN | X1_nk+mts>=1 | short | 12636 | 198 | 0.023 | 0.200 | -0.178 | 17851 | -0.214 | 0.037 | 0.044 |
| MARKDOWN | X2_nk+mts>=2 | short | 3977 | 189 | 0.061 | 0.195 | -0.134 | 10618 | -0.200 | 0.066 | 0.060 |
| MARKDOWN | X3_nk+mts>=3 | short | 1571 | 139 | 0.060 | 0.186 | -0.126 | 5010 | -0.187 | 0.061 | 0.078 |
| RELIEF | N1_firsthour | long | 974 | 34 | -0.036 | 0.230 | -0.265 | 871 | -0.239 | -0.027 | 0.135 |
| RELIEF | N2_pivots | long | 1736 | 34 | 0.049 | 0.228 | -0.179 | 1746 | -0.297 | 0.117 | 0.133 |
| RELIEF | N3_breakretest | long | 1593 | 34 | -0.014 | 0.229 | -0.243 | 1618 | -0.331 | 0.088 | 0.115 |
| RELIEF | N4_hilega | long | 3707 | 34 | 0.006 | 0.226 | -0.220 | 3783 | -0.273 | 0.053 | 0.106 |
| RELIEF | N5_rsi3070 | long | 600 | 34 | -0.038 | 0.225 | -0.264 | 689 | -0.149 | -0.115 | 0.123 |
| RELIEF | NN_nkcount2 | long | 2799 | 34 | 0.007 | 0.227 | -0.221 | 2931 | -0.287 | 0.067 | 0.106 |
| RELIEF | X1_nk+mts>=1 | long | 2053 | 34 | -0.029 | 0.226 | -0.255 | 2343 | -0.235 | -0.019 | 0.095 |
| RELIEF | X2_nk+mts>=2 | long | 836 | 34 | 0.009 | 0.228 | -0.219 | 1229 | -0.148 | -0.071 | 0.114 |
| RELIEF | X3_nk+mts>=3 | long | 286 | 28 | -0.068 | 0.230 | -0.299 | 593 | -0.152 | -0.147 | 0.142 |
| ACCUM-RANGE | N1_firsthour | geometry | 4471 | 154 | -0.011 | 0.223 | -0.234 | 4562 | -0.185 | -0.049 | 0.058 |
| ACCUM-RANGE | N2_pivots | geometry | 7800 | 156 | -0.047 | 0.219 | -0.266 | 7759 | -0.194 | -0.072 | 0.052 |
| ACCUM-RANGE | N3_breakretest | geometry | 7509 | 156 | -0.024 | 0.221 | -0.245 | 7534 | -0.195 | -0.051 | 0.050 |
| ACCUM-RANGE | N4_hilega | geometry | 17165 | 156 | -0.057 | 0.218 | -0.274 | 17328 | -0.200 | -0.074 | 0.047 |
| ACCUM-RANGE | N5_rsi3070 | geometry | 3174 | 155 | -0.015 | 0.213 | -0.227 | 2709 | -0.274 | 0.047 | 0.065 |
| ACCUM-RANGE | NN_nkcount2 | geometry | 13246 | 156 | -0.049 | 0.218 | -0.267 | 13230 | -0.198 | -0.069 | 0.049 |
| ACCUM-RANGE | X1_nk+mts>=1 | geometry | 10818 | 156 | -0.044 | 0.218 | -0.262 | 8877 | -0.192 | -0.070 | 0.052 |
| ACCUM-RANGE | X2_nk+mts>=2 | geometry | 5875 | 156 | -0.016 | 0.217 | -0.233 | 3114 | -0.217 | -0.017 | 0.062 |
| ACCUM-RANGE | X3_nk+mts>=3 | geometry | 2541 | 141 | 0.067 | 0.216 | -0.149 | 1354 | -0.220 | 0.071 | 0.076 |
| MARKUP | N1_firsthour | long | 9911 | 318 | 0.020 | 0.189 | -0.169 | 9452 | -0.157 | -0.011 | 0.047 |
| MARKUP | N2_pivots | long | 17543 | 321 | -0.031 | 0.186 | -0.218 | 17327 | -0.159 | -0.059 | 0.038 |
| MARKUP | N3_breakretest | long | 17356 | 321 | -0.014 | 0.190 | -0.204 | 17007 | -0.147 | -0.057 | 0.039 |
| MARKUP | N4_hilega | long | 40107 | 321 | -0.015 | 0.185 | -0.199 | 41542 | -0.165 | -0.035 | 0.036 |
| MARKUP | N5_rsi3070 | long | 6077 | 301 | -0.078 | 0.175 | -0.253 | 6310 | -0.157 | -0.096 | 0.056 |
| MARKUP | NN_nkcount2 | long | 30603 | 321 | -0.019 | 0.186 | -0.205 | 30778 | -0.160 | -0.045 | 0.035 |
| MARKUP | X1_nk+mts>=1 | long | 20409 | 321 | -0.016 | 0.184 | -0.200 | 26691 | -0.162 | -0.038 | 0.038 |
| MARKUP | X2_nk+mts>=2 | long | 9131 | 306 | -0.029 | 0.180 | -0.209 | 14590 | -0.186 | -0.023 | 0.042 |
| MARKUP | X3_nk+mts>=3 | long | 3286 | 208 | -0.023 | 0.171 | -0.194 | 7664 | -0.184 | -0.010 | 0.054 |
| DISTRIBUTION | N1_firsthour | short | 9866 | 327 | 0.029 | 0.207 | -0.178 | 9362 | -0.215 | 0.037 | 0.050 |
| DISTRIBUTION | N2_pivots | short | 17236 | 333 | 0.063 | 0.202 | -0.139 | 17209 | -0.236 | 0.097 | 0.042 |
| DISTRIBUTION | N3_breakretest | short | 17537 | 333 | 0.039 | 0.204 | -0.165 | 17578 | -0.239 | 0.075 | 0.039 |
| DISTRIBUTION | N4_hilega | short | 41205 | 333 | 0.054 | 0.200 | -0.146 | 40891 | -0.247 | 0.101 | 0.035 |
| DISTRIBUTION | N5_rsi3070 | short | 6294 | 317 | -0.058 | 0.200 | -0.258 | 7129 | -0.207 | -0.051 | 0.055 |
| DISTRIBUTION | NN_nkcount2 | short | 30833 | 333 | 0.045 | 0.202 | -0.157 | 30903 | -0.245 | 0.088 | 0.036 |
| DISTRIBUTION | X1_nk+mts>=1 | short | 22390 | 333 | 0.040 | 0.202 | -0.162 | 25409 | -0.240 | 0.078 | 0.038 |
| DISTRIBUTION | X2_nk+mts>=2 | short | 8941 | 312 | -0.004 | 0.203 | -0.206 | 14434 | -0.244 | 0.037 | 0.042 |
| DISTRIBUTION | X3_nk+mts>=3 | short | 4034 | 246 | 0.002 | 0.197 | -0.195 | 6671 | -0.221 | 0.027 | 0.051 |

## Useful trades now (descriptive only, no advice)
Today's phase label (BTC, applied to BTC and ETH) from the last 10 days; the 2026-11-14 row is provisional because it uses the incomplete 2026-11-13 daily candle (data to 2026-11-13 20:15 UTC):

| date | label | cycle | provisional |
|---|---|---|---|
| 2026-11-05 | ACCUM-RANGE | BASE | False |
| 2026-11-06 | DISTRIBUTION | BASE | False |
| 2026-11-07 | DISTRIBUTION | BASE | False |
| 2026-11-08 | DISTRIBUTION | BASE | False |
| 2026-11-09 | DISTRIBUTION | BASE | False |
| 2026-11-10 | DISTRIBUTION | BASE | False |
| 2026-11-11 | DISTRIBUTION | BASE | False |
| 2026-11-12 | DISTRIBUTION | BASE | False |
| 2026-11-13 | MARKDOWN | BEAR | False |
| 2026-11-14 | MARKDOWN | BEAR | True |

Current context buckets on the last closed 15m bar:

| coin | last closed 15m bar (UTC) | phase | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 2026-11-13 20:15 | MARKDOWN | LOW<=40 | OS<=-53 | MID | NO-DATA | NORMAL | AGREE | NORMAL | US |
| ETH | 2026-11-13 20:15 | MARKDOWN | LOW<=40 | OS<=-53 | MID | NO-DATA | NEG<0 | AGREE | NORMAL | US |

Active kept cells for BTC/ETH: none, because there are no kept cells. Both coins currently sit in MARKDOWN (short phase) with 4h RSI at or below 40 and daily WaveTrend at or below -53 (oversold) - the exact exhaustion-against-the-phase state; DEV found no cell in MARKDOWN that pays fees (best MARKDOWN cell: X3 with daily WaveTrend OB, lower bound -0.10 R). C4 (OI) shows NO-DATA because the archive's daily files end before the last bar.

## Limits, stated
- BTC-only phase label on 20 coins: effective n is days. 4 cycles. CAPITULATION and ACCUM-RANGE are thin; VAL has 6 CAPITULATION days.
- OI and funding are USD-M perp series used as context for spot-priced trades; no funding cost charged on the spot trades.
- Parameters are OURS (phase thresholds, bucket cutoffs, MTS-agreement mapping, stop/target/hold); not tuned on DEV or VAL. Nothing was added after the DEV result.
- Zero kept cells is a valid pre-registered outcome; it supports "no NK or NK+MTS rule has fee-net edge on 15m crypto in any single-bucket phase cell", and does not show that other timeframes, exits or maker-only execution would fail.
- Files: PRE_REG.md, study.py, phases.py, stats.py, run.py, test_study.py, fetch.py, dev_cells.csv, dev_stepA.json, cells_frozen.json, val_results.json. Raw data in F:\MTS\data_cache\ (not in git).
