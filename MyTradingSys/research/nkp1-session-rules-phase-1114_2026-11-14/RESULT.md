# RESULT nkp1-session-rules-phase-1114

**VERDICT: FAIL: 0 of 3 DEV-kept cells pass VAL (net R>0, CI low>0, ex-best-5>0, placebo p<0.05, BH q<0.10, n>=150).**

Rules: NK1 first-hour low break + VWAP (UTC and NY sessions, E3 session-end exit) and NK5 session open 15/10/5 (NY-asia, UTC-4h), 20 original coins each, taker 12 bp + funding, 6 bp maker row. Phase = BTC 6-phase label (causal, d-1 closes), 8 context layers, cells chosen on DEV (<=2023-12-31), frozen in git (code commit `5edae3170`), run once on VAL (>=2024-01-01).

## Context

Regime mix: share of BTC days per phase (VAL is a single regime, 2024-26):

| phase | DEV | VAL |
|---|---|---|
| MARKUP | 0.341 | 0.309 |
| DISTRIBUTION | 0.19 | 0.314 |
| MARKDOWN | 0.186 | 0.19 |
| ACCUM-RANGE | 0.172 | 0.13 |
| RELIEF | 0.076 | 0.052 |
| CAPITULATION | 0.035 | 0.006 |

Cycle state M: DEV {'BASE': 0.503, 'BEAR': 0.376, 'BULL': 0.121}, VAL {'BULL': 0.537, 'BEAR': 0.321, 'BASE': 0.142}. Days: DEV 4684, VAL 1049. ONE-REGIME flag: none (no phase >85% in either split)

Trades (signals) by phase, all dates:

| phase | NK1-UTC | NK1-NY | NK5-NYasia | NK5-UTC4h |
|---|---|---|---|---|
| MARKUP | 10991 | 12690 | 1869 | 1826 |
| DISTRIBUTION | 7455 | 7833 | 1362 | 1160 |
| MARKDOWN | 7367 | 7458 | 1401 | 1108 |
| ACCUM-RANGE | 5001 | 5434 | 1103 | 711 |
| RELIEF | 2516 | 2897 | 514 | 469 |
| CAPITULATION | 627 | 774 | 67 | 119 |

Sanity windows (not tuned; spec s1):

| window | expected | share_expected | mix |
|---|---|---|---|
| CAP 2020-03-12..15 | CAPITULATION | 0.75 | {'CAPITULATION': 0.75, 'DISTRIBUTION': 0.25} |
| CAP 2022-06-13..18 | CAPITULATION | 0.833 | {'CAPITULATION': 0.833, 'MARKDOWN': 0.167} |
| MARKDOWN 2022-01..10 | MARKDOWN | 0.507 | {'MARKDOWN': 0.507, 'RELIEF': 0.211, 'DISTRIBUTION': 0.115, 'ACCUM-RANGE': 0.095, 'CAPITULATION': 0.072} |
| MARKDOWN 2025-11..2026-02 | MARKDOWN | 0.675 | {'MARKDOWN': 0.675, 'ACCUM-RANGE': 0.192, 'DISTRIBUTION': 0.075, 'RELIEF': 0.033, 'CAPITULATION': 0.025} |
| MARKUP 2020-11..2021-03 | MARKUP | 1.0 | {'MARKUP': 1.0} |
| MARKUP 2023-10..2024-03 | MARKUP | 0.678 | {'MARKUP': 0.678, 'ACCUM-RANGE': 0.268, 'DISTRIBUTION': 0.033, 'RELIEF': 0.022} |

Median halving age (days) per phase (reported, not used): {'ACCUM-RANGE': 859.0, 'CAPITULATION': 734.0, 'DISTRIBUTION': 475.0, 'MARKDOWN': 744.0, 'MARKUP': 405.0, 'RELIEF': 750.0}

## Step A: per-phase table (no pooled headline)

net R at 12 bp + funding; gross R and cost R are per R (stop distance); app = phase-appropriate direction, opp = opposite (control); diff = app minus opp with day-cluster SE.

### DEV

| variant | phase | n_app | days_app | gross_R | cost_R | net_R_app | n_opp | net_R_opp | diff | diff_se |
|---|---|---|---|---|---|---|---|---|---|---|
| NK1-UTC | CAPITULATION | 273 | 38 | 0.846 | 0.124 | 0.721 | 270 | 0.130 | 0.591 | 1.039 |
| NK1-UTC | MARKDOWN | 2148 | 341 | 0.181 | 0.198 | -0.017 | 2154 | -0.298 | 0.281 | 0.171 |
| NK1-UTC | RELIEF | 873 | 148 | 0.003 | 0.190 | -0.187 | 871 | -0.072 | -0.115 | 0.253 |
| NK1-UTC | ACCUM-RANGE | 1502 | 238 | -0.082 | 0.222 | -0.305 | 1505 | -0.116 | -0.189 | 0.179 |
| NK1-UTC | MARKUP | 3260 | 509 | 0.385 | 0.201 | 0.183 | 3022 | 0.029 | 0.154 | 0.153 |
| NK1-UTC | DISTRIBUTION | 1296 | 209 | 0.131 | 0.180 | -0.048 | 1281 | -0.242 | 0.194 | 0.231 |
| NK1-NY | CAPITULATION | 426 | 41 | -0.190 | 0.115 | -0.305 | 255 | 0.081 | -0.386 | 0.490 |
| NK1-NY | MARKDOWN | 2452 | 343 | 0.060 | 0.202 | -0.141 | 2605 | -0.092 | -0.049 | 0.153 |
| NK1-NY | RELIEF | 1111 | 140 | 0.210 | 0.198 | 0.013 | 1028 | -0.236 | 0.248 | 0.207 |
| NK1-NY | ACCUM-RANGE | 1956 | 255 | 0.017 | 0.222 | -0.205 | 1672 | -0.028 | -0.177 | 0.177 |
| NK1-NY | MARKUP | 4280 | 550 | 0.071 | 0.210 | -0.139 | 3861 | -0.201 | 0.062 | 0.121 |
| NK1-NY | DISTRIBUTION | 1672 | 223 | 0.097 | 0.192 | -0.095 | 1626 | -0.024 | -0.071 | 0.210 |
| NK5-NYasia | CAPITULATION | 18 | 5 | -1.000 | 0.081 | -1.081 | 27 | -0.510 | -0.571 | 0.227 |
| NK5-NYasia | MARKDOWN | 395 | 129 | -0.314 | 0.167 | -0.482 | 524 | -0.168 | -0.314 | 0.298 |
| NK5-NYasia | RELIEF | 194 | 35 | -0.309 | 0.140 | -0.449 | 195 | -0.063 | -0.386 | 0.574 |
| NK5-NYasia | ACCUM-RANGE | 427 | 99 | 0.032 | 0.182 | -0.150 | 311 | -0.293 | 0.143 | 0.263 |
| NK5-NYasia | MARKUP | 581 | 150 | -0.053 | 0.146 | -0.199 | 609 | -0.345 | 0.146 | 0.195 |
| NK5-NYasia | DISTRIBUTION | 297 | 94 | 0.124 | 0.147 | -0.023 | 302 | -0.346 | 0.322 | 0.377 |
| NK5-UTC4h | CAPITULATION | 62 | 5 | 0.431 | 0.050 | 0.380 | 52 | -0.167 | 0.548 | 0.500 |
| NK5-UTC4h | MARKDOWN | 399 | 128 | 0.070 | 0.176 | -0.107 | 368 | -0.207 | 0.101 | 0.225 |
| NK5-UTC4h | RELIEF | 122 | 27 | 0.804 | 0.158 | 0.646 | 230 | -0.346 | 0.992 | 0.433 |
| NK5-UTC4h | ACCUM-RANGE | 250 | 72 | 0.078 | 0.185 | -0.107 | 207 | -0.181 | 0.074 | 0.276 |
| NK5-UTC4h | MARKUP | 377 | 103 | -0.155 | 0.150 | -0.305 | 697 | -0.262 | -0.043 | 0.195 |
| NK5-UTC4h | DISTRIBUTION | 184 | 75 | 0.006 | 0.147 | -0.141 | 190 | -0.410 | 0.268 | 0.247 |

### VAL

| variant | phase | n_app | days_app | gross_R | cost_R | net_R_app | n_opp | net_R_opp | diff | diff_se |
|---|---|---|---|---|---|---|---|---|---|---|
| NK1-UTC | CAPITULATION | 63 | 5 | 0.426 | 0.161 | 0.265 | 21 | -1.006 | 1.272 | 0.878 |
| NK1-UTC | MARKDOWN | 1493 | 186 | -0.281 | 0.222 | -0.503 | 1572 | -0.208 | -0.295 | 0.176 |
| NK1-UTC | RELIEF | 452 | 53 | 0.028 | 0.234 | -0.206 | 320 | -0.367 | 0.162 | 0.271 |
| NK1-UTC | ACCUM-RANGE | 1009 | 128 | -0.118 | 0.230 | -0.347 | 985 | -0.171 | -0.176 | 0.190 |
| NK1-UTC | MARKUP | 2333 | 295 | -0.033 | 0.213 | -0.247 | 2376 | -0.250 | 0.004 | 0.161 |
| NK1-UTC | DISTRIBUTION | 2536 | 311 | 0.125 | 0.221 | -0.096 | 2342 | -0.330 | 0.234 | 0.155 |
| NK1-NY | CAPITULATION | 64 | 5 | 2.667 | 0.148 | 2.519 | 29 | 0.676 | 1.843 | 1.562 |
| NK1-NY | MARKDOWN | 1173 | 153 | 0.072 | 0.204 | -0.132 | 1228 | -0.255 | 0.123 | 0.187 |
| NK1-NY | RELIEF | 367 | 46 | -0.295 | 0.224 | -0.519 | 391 | -0.343 | -0.176 | 0.208 |
| NK1-NY | ACCUM-RANGE | 970 | 126 | 0.024 | 0.223 | -0.198 | 836 | 0.269 | -0.467 | 0.291 |
| NK1-NY | MARKUP | 2357 | 279 | -0.077 | 0.197 | -0.274 | 2192 | -0.242 | -0.033 | 0.147 |
| NK1-NY | DISTRIBUTION | 2256 | 279 | 0.388 | 0.202 | 0.186 | 2279 | -0.072 | 0.258 | 0.250 |
| NK5-NYasia | CAPITULATION | 14 | 1 | 0.811 | 0.121 | 0.690 | 8 | -0.585 | 1.275 | n/a |
| NK5-NYasia | MARKDOWN | 229 | 72 | 0.919 | 0.171 | 0.749 | 253 | 0.267 | 0.482 | 0.586 |
| NK5-NYasia | RELIEF | 56 | 18 | 0.434 | 0.213 | 0.221 | 69 | -0.071 | 0.292 | 0.588 |
| NK5-NYasia | ACCUM-RANGE | 241 | 59 | -0.058 | 0.198 | -0.256 | 124 | 0.124 | -0.381 | 0.526 |
| NK5-NYasia | MARKUP | 376 | 78 | 0.300 | 0.154 | 0.146 | 303 | -0.289 | 0.435 | 0.322 |
| NK5-NYasia | DISTRIBUTION | 362 | 126 | 0.318 | 0.175 | 0.143 | 401 | -0.325 | 0.468 | 0.368 |
| NK5-UTC4h | CAPITULATION | 0 | 0 | n/a | n/a | n/a | 5 | -0.619 | n/a | n/a |
| NK5-UTC4h | MARKDOWN | 151 | 64 | -0.143 | 0.184 | -0.327 | 190 | 0.108 | -0.434 | 0.322 |
| NK5-UTC4h | RELIEF | 33 | 13 | 0.848 | 0.224 | 0.624 | 84 | -0.459 | 1.082 | 0.632 |
| NK5-UTC4h | ACCUM-RANGE | 111 | 38 | -0.170 | 0.206 | -0.376 | 143 | -0.593 | 0.217 | 0.277 |
| NK5-UTC4h | MARKUP | 276 | 74 | -0.007 | 0.166 | -0.173 | 476 | -0.324 | 0.151 | 0.213 |
| NK5-UTC4h | DISTRIBUTION | 393 | 117 | -0.121 | 0.181 | -0.302 | 393 | -0.295 | -0.007 | 0.202 |

## DEV-chosen cells on VAL (kept cells only, run once)

| variant | phase | layer | bucket | dev_n | DEV_net_R | n | days | VAL_net_R | day_CI_low | day_CI_high | gross_R | fee_funding_R | ex_best5 | placebo_p | bh_q | VAL-DEV | maker6bp_net_R | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NK1-UTC | MARKUP | C3 | %B<0.10 | 279 | 0.892 | 232 | 63 | -0.174 | -0.819 | 0.480 | 0.011 | 0.185 | -0.896 | 0.000 | 0.964 | -1.066 | -0.104 | FAIL |
| NK1-UTC | MARKUP | C1 | 4hRSI<=40 | 365 | 0.796 | 364 | 88 | -0.290 | -0.694 | 0.158 | -0.091 | 0.199 | -0.740 | 0.089 | 0.964 | -1.086 | -0.165 | FAIL |
| NK1-UTC | MARKUP | C6 | bull-div | 337 | 0.558 | 253 | 137 | -0.308 | -0.615 | 0.025 | -0.089 | 0.219 | -0.605 | 0.221 | 0.964 | -0.866 | -0.152 | FAIL |

Control rows on VAL (opposite direction in the same cell; same bucket in the other 5 phases; the unconditional rule; placebo mean):

| variant | phase | layer | bucket | ctl_opp_n | ctl_opp_net | ctl_otherph_n | ctl_otherph_net | ctl_uncond_n | ctl_uncond_net | placebo_mean |
|---|---|---|---|---|---|---|---|---|---|---|
| NK1-UTC | MARKUP | C3 | %B<0.10 | 251 | -0.480 | 908 | -0.351 | 7886 | -0.253 | -0.509 |
| NK1-UTC | MARKUP | C1 | 4hRSI<=40 | 344 | -0.138 | 1488 | -0.262 | 7886 | -0.253 | -0.422 |
| NK1-UTC | MARKUP | C6 | bull-div | 276 | -0.215 | 734 | -0.436 | 7886 | -0.253 | -0.403 |

DEV-kept cells that pass VAL: 0 of 3. Mean DEV-to-VAL shrinkage (VAL net R minus DEV net R): -1.006.

## Layer coverage (signals with data per layer)

| variant | layer | dev_with_data | val_with_data | signals |
|---|---|---|---|---|
| NK1-UTC | C1 | 18455 | 15502 | 33957 |
| NK1-UTC | C2 | 16725 | 15502 | 33957 |
| NK1-UTC | C3 | 18455 | 15502 | 33957 |
| NK1-UTC | C4 | 9717 | 15502 | 33957 |
| NK1-UTC | C5 | 15793 | 15363 | 33957 |
| NK1-UTC | C6 | 18455 | 15386 | 33957 |
| NK1-UTC | C7 | 18248 | 15502 | 33957 |
| NK1-UTC | C8 | 18455 | 15502 | 33957 |
| NK1-NY | C1 | 22923 | 14142 | 37086 |
| NK1-NY | C2 | 20513 | 14142 | 37086 |
| NK1-NY | C3 | 22923 | 14142 | 37086 |
| NK1-NY | C4 | 10315 | 14142 | 37086 |
| NK1-NY | C5 | 19147 | 14003 | 37086 |
| NK1-NY | C6 | 22944 | 14041 | 37086 |
| NK1-NY | C7 | 22604 | 14142 | 37086 |
| NK1-NY | C8 | 22944 | 14142 | 37086 |
| NK5-NYasia | C1 | 3880 | 2436 | 6316 |
| NK5-NYasia | C2 | 3542 | 2436 | 6316 |
| NK5-NYasia | C3 | 3880 | 2436 | 6316 |
| NK5-NYasia | C4 | 2037 | 2436 | 6316 |
| NK5-NYasia | C5 | 3269 | 2412 | 6316 |
| NK5-NYasia | C6 | 3880 | 2429 | 6316 |
| NK5-NYasia | C7 | 3822 | 2436 | 6316 |
| NK5-NYasia | C8 | 3880 | 2436 | 6316 |
| NK5-UTC4h | C1 | 3138 | 2255 | 5393 |
| NK5-UTC4h | C2 | 2822 | 2255 | 5393 |
| NK5-UTC4h | C3 | 3138 | 2255 | 5393 |
| NK5-UTC4h | C4 | 1686 | 2255 | 5393 |
| NK5-UTC4h | C5 | 2652 | 2219 | 5393 |
| NK5-UTC4h | C6 | 3138 | 2221 | 5393 |
| NK5-UTC4h | C7 | 3099 | 2255 | 5393 |
| NK5-UTC4h | C8 | 3138 | 2255 | 5393 |

Coins without a futures funding file: none. First available context date per coin and layer is in summary.json (`ctx_first_avail`).

## Useful trades now (descriptive only, no advice)

Today's label (2026-11-14, from BTC closes through the previous day): **MARKDOWN** (cycle state BEAR, BTC 40d range position 0.07, RSI14d 25.5, drawdown from ATH -44.7%). Allowed direction in this phase: short.
Cell filter state per kept cell (BTC: context read at 2026-11-13 21:05 UTC, ETH: context read at 2026-11-13 21:05 UTC; the 5m cache ends before today, so layer buckets are stale by that age). ACTIVE = today's phase and the layer bucket both match; the NK signal itself must also fire for a trade to exist.

| variant | cell | symbol | phase_matches_today | bucket_now | context_matches | ACTIVE |
|---|---|---|---|---|---|---|
| NK1-UTC | MARKUP x C3=%B<0.10 | BTC | False | %B mid | False | False |
| NK1-UTC | MARKUP x C3=%B<0.10 | ETH | False | %B mid | False | False |
| NK1-UTC | MARKUP x C1=4hRSI<=40 | BTC | False | 4hRSI<=40 | True | False |
| NK1-UTC | MARKUP x C1=4hRSI<=40 | ETH | False | 4hRSI<=40 | True | False |
| NK1-UTC | MARKUP x C6=bull-div | BTC | False | NO-DATA | False | False |
| NK1-UTC | MARKUP x C6=bull-div | ETH | False | NO-DATA | False | False |

## Notes and limits

- Phase is BTC-only, so effective n is days; 4 cycles only. VAL = one regime.
- The shared phase table `F:\MTS\data_cache\mts_brains\phase_daily.csv` was built by another worker (git 5b21ebe34); this study uses its own committed `phases.py` and spot-verified it against the shared table: 97.2% label agreement over 2012-2026 (all differences are ACCUM-RANGE edges), cycle state 100%, last 30 days 100%.
- All layer cutoffs except RSI 40/60 and WT +-53 are OURS. HM, the session mapping and C8 (constant per variant) are OURS.
- Step A VAL rows that look positive (for example NK5-NYasia MARKDOWN short, NK1-NY DISTRIBUTION short, NK5-NYasia MARKUP/DISTRIBUTION) were NOT chosen on DEV; their DEV net R was negative. Reading them as edge would be selecting on VAL, so they are descriptive only. Where the appropriate-minus-opposite difference is under ~1.5 SE it is noise.
- C2 (WaveTrend) values exist only after the 200-bar warm-up; the first-available date in summary.json is the first bar, not the first valid value. C4 (OI) starts 2021-12 for all coins (Binance published metrics from then), so C4 cells have no 2019-2021 DEV data. C6 had no data at the 'now' read (stale cache).
- Coins: NK1 uses its original 20, NK5 its original 20 (union 23 incl. EOS, DASH, IOTA; EOS ends 2025-05, so NK5 EOS has no VAL rows; EOS/DASH/IOTA have no NK1 pool).
- E1/E2 exits of NK1 and three NK5 rows were dropped to keep cells at 144 per variant.
