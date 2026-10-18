# COUNTS: DEV decision events per context-factor value (count-only, no outcome column anywhere)

Input: `grid_context.csv` (VEC build at every 1h close of DEV, both sides; 43776 rows = 21888 grid points x 2 sides).
Decision event = grid row with `at_level` True (nearest side-aware level within K_ZONE = 0.5 x ATR14(4h)). Episode = event with
`first_touch` True (the level had no earlier 1h touch since it became available, lookback 720 h). Rows at the same level on
consecutive hours are correlated: the n_needed check should be read against episodes, the per-value tables use events.

| side | events 2022 | 2023 | 2024H1 | all | episodes 2022 | 2023 | 2024H1 | all | grid rows |
|---|---|---|---|---|---|---|---|---|---|
| long | 8297 | 8182 | 4209 | 20688 | 885 | 910 | 369 | 2164 | 21888 |
| short | 8322 | 8178 | 4187 | 20687 | 884 | 936 | 498 | 2318 | 21888 |

## 0. n needed (research_kit.power_check: MDE = 2.8 x sd / sqrt(n); proceed iff MDE + cost <= plausible effect)

| model | sd per trade | cost | plausible effect | n needed | label |
|---|---|---|---|---|---|
| R units (PRE_REG outcome: stop ladder, target 1.5 R) | <= 1.25 R (bound for a -1/+1.5 outcome) | median ladder cost over events, all-taker 0.14 %: 0.105 R | 0.15 R | **5943** | sd bound: arithmetic; cost: events table below; plausible: OURS |
| R units, maker entry 0.09 % | same | 0.067 R | 0.15 R | 1789 | same |
| % units, h = 240 min | 1.97 % (FABLE_RUNS_AUDIT.md:73) | 0.14 % | 0.28 % (2 x cost, wlow_bounce RESULT.md rule) | 1553 | SOURCED sd, OURS plausible |
| % units, h = 60 min | 0.93 % (FABLE_RUNS_AUDIT.md:73) | 0.14 % | 0.28 % | 346 | same |

Flag rule: a bucket with fewer than **5943** events (the R model, all-taker) is marked `<n` in every table below. A factor whose
every value is flagged on one side cannot get a verdict on that side (PRE_REG section 4: INCONCLUSIVE by count, before any outcome).

## F1. Side-aware levels

**nearest level source (events)**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| prior_d_hl | 375 | 235 | 100 | 354 | 227 | 95 | 710 <n | 676 <n |
| prior_w_hl | 25 | 15 | 13 | 19 | 40 | 19 | 53 <n | 78 <n |
| fabio_vp_day | 1415 | 1633 | 639 | 1357 | 1608 | 592 | 3687 <n | 3557 <n |
| tom_vp_week | 309 | 451 | 115 | 310 | 333 | 117 | 875 <n | 760 <n |
| krown_zone | 3667 | 3253 | 1906 | 3737 | 3387 | 1862 | 8826 | 8986 |
| malkan_bb_d | 153 | 235 | 129 | 204 | 212 | 149 | 517 <n | 565 <n |
| vwap_session | 1392 | 1572 | 564 | 1335 | 1495 | 542 | 3528 <n | 3372 <n |
| vwap_week | 258 | 291 | 151 | 210 | 289 | 132 | 700 <n | 631 <n |
| round_1k | 703 | 497 | 592 | 796 | 587 | 679 | 1792 <n | 2062 <n |

**nearest level source (episodes = first touch)**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| prior_d_hl | 109 | 67 | 23 | 91 | 66 | 26 | 199 <n | 183 <n |
| prior_w_hl | 1 | 0 | 0 | 1 | 2 | 0 | 1 <n | 3 <n |
| fabio_vp_day | 358 | 471 | 149 | 374 | 437 | 237 | 978 <n | 1048 <n |
| tom_vp_week | 25 | 20 | 17 | 22 | 23 | 13 | 62 <n | 58 <n |
| krown_zone | 133 | 84 | 46 | 132 | 100 | 57 | 263 <n | 289 <n |
| malkan_bb_d | 27 | 63 | 35 | 59 | 83 | 34 | 125 <n | 176 <n |
| vwap_session | 204 | 197 | 86 | 185 | 202 | 92 | 487 <n | 479 <n |
| round_1k | 28 | 8 | 13 | 20 | 23 | 39 | 49 <n | 82 <n |

**level age at the decision (hours since the level became available)**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| 24-168h | 1410 | 1594 | 598 | 1502 | 1610 | 550 | 3602 <n | 3662 <n |
| <24h | 3597 | 3915 | 1567 | 3522 | 3782 | 1516 | 9079 | 8820 |
| >168h | 3290 | 2673 | 2044 | 3298 | 2786 | 2121 | 8007 | 8205 |

**earlier 1h touches of the level (0 = first touch)**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| 0 | 885 | 910 | 369 | 884 | 936 | 498 | 2164 <n | 2318 <n |
| 1 | 639 | 574 | 269 | 601 | 663 | 259 | 1482 <n | 1523 <n |
| 2 | 576 | 601 | 276 | 580 | 606 | 252 | 1453 <n | 1438 <n |
| 3+ | 6197 | 6097 | 3295 | 6257 | 5973 | 3178 | 15589 | 15408 |

**approach speed over the last 4 closed 1h bars**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| away | 4189 | 4193 | 2182 | 4230 | 4128 | 2041 | 10564 | 10399 |
| fast | 414 | 341 | 221 | 371 | 383 | 204 | 976 <n | 958 <n |
| slow | 3694 | 3648 | 1806 | 3721 | 3667 | 1942 | 9148 | 9330 |

**liquidity sweep: a wick through the level in the last 6 closed 1h bars with the close back on the right side**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| False | 790 | 745 | 324 | 789 | 945 | 506 | 1859 <n | 2240 <n |
| True | 7507 | 7437 | 3885 | 7533 | 7233 | 3681 | 18829 | 18447 |

## F2. Confluence

**distinct layers within 0.5 x ATR (K_ZONE, OURS)**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| 1 | 1512 | 1548 | 636 | 1544 | 1598 | 669 | 3696 <n | 3811 <n |
| 2 | 2563 | 2677 | 1101 | 2751 | 2647 | 1159 | 6341 | 6557 |
| 3 | 2536 | 2304 | 1216 | 2275 | 2335 | 1235 | 6056 | 5845 <n |
| 4+ | 1686 | 1653 | 1256 | 1752 | 1598 | 1124 | 4595 <n | 4474 <n |

**distinct layers within 1.0 x ATR (K_ZONE_ALT, counted only)**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| 1 | 329 | 352 | 111 | 268 | 452 | 134 | 792 <n | 854 <n |
| 2 | 1016 | 1126 | 414 | 1159 | 1065 | 423 | 2556 <n | 2647 <n |
| 3 | 1963 | 2042 | 832 | 1996 | 1975 | 881 | 4837 <n | 4852 <n |
| 4+ | 4989 | 4662 | 2852 | 4899 | 4686 | 2749 | 12503 | 12334 |

**ledger size (all levels on the map, both roles)**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| 12+ | 8297 | 8182 | 4209 | 8322 | 8178 | 4187 | 20688 | 20687 |

## F3. Operator's daily-candle stop ladder

Stop = prior completed daily low (long) / high (short); if wider than W = 2.5 % (OURS) the prior 12h, then the prior 8h candle;
every rung wider than W -> the tightest valid rung. Widths and counts only.

**rung chosen**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| 1d | 4493 | 5735 | 2330 | 4427 | 5636 | 2502 | 12558 | 12565 |
| 12h | 1815 | 1261 | 949 | 1886 | 1349 | 790 | 4025 <n | 4025 <n |
| 8h | 1584 | 961 | 760 | 1671 | 856 | 698 | 3305 <n | 3225 <n |
| none | 405 | 225 | 170 | 338 | 337 | 197 | 800 <n | 872 <n |

**operator condition (close rule): price has moved past the prior daily open**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| False | 4442 | 3979 | 1964 | 3760 | 4098 | 2200 | 10385 | 10058 |
| True | 3855 | 4203 | 2245 | 4562 | 4080 | 1987 | 10303 | 10629 |

**operator condition (touch rule, counted only): the partial day's high/low moved past the prior open**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| False | 2657 | 2140 | 1297 | 2244 | 2510 | 1257 | 6094 | 6011 |
| True | 5640 | 6042 | 2912 | 6078 | 5668 | 2930 | 14594 | 14676 |

**stop narrower than the cost floor 0.56 % (cost > 0.25 R)**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| False | 7093 | 6706 | 3664 | 7086 | 6654 | 3456 | 17463 | 17196 |
| True | 1204 | 1476 | 545 | 1236 | 1524 | 731 | 3225 <n | 3491 <n |

**stop width distribution (% of price) and cost in R per rung, over events (both sides, all years)**

| rung | n | stop p10 | p25 | p50 | p75 | p90 | cost R taker p50 (0.14 %/stop) | cost R maker-in p50 (0.09 %/stop) |
|---|---|---|---|---|---|---|---|---|
| 1d (all events where valid) | 37369 | 0.49 | 0.95 | 1.79 | 3.32 | 5.38 | 0.078 | 0.050 |
| 12h (all events where valid) | 36645 | 0.32 | 0.65 | 1.26 | 2.32 | 3.92 | 0.111 | 0.072 |
| 8h (all events where valid) | 37118 | 0.25 | 0.50 | 0.97 | 1.77 | 3.04 | 0.144 | 0.092 |
| chosen = 1d | 25123 | 0.37 | 0.71 | 1.20 | 1.81 | 2.29 | 0.116 | 0.075 |
| chosen = 12h | 8050 | 0.40 | 0.83 | 1.56 | 2.28 | 3.20 | 0.090 | 0.058 |
| chosen = 8h | 6530 | 0.43 | 0.94 | 1.98 | 3.11 | 4.66 | 0.071 | 0.045 |

## F4. Candle patterns on the last COMPLETED candle

**pattern on the last closed 4h candle**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| bear_engulf | 457 | 470 | 244 | 483 | 500 | 244 | 1171 <n | 1227 <n |
| bear_engulf|bear_pin | 11 | 29 | 4 | 11 | 31 | 4 | 44 <n | 46 <n |
| bear_engulf|bear_pin|inside | 4 | 4 | 0 | 4 | 4 | 0 | 8 <n | 8 <n |
| bear_engulf|bull_pin | 16 | 35 | 20 | 16 | 36 | 20 | 71 <n | 72 <n |
| bear_engulf|bull_pin|inside | 4 | 4 | 0 | 4 | 4 | 0 | 8 <n | 8 <n |
| bear_engulf|bull_pin|outside | 4 | 4 | 0 | 4 | 4 | 0 | 8 <n | 8 <n |
| bear_engulf|inside | 87 | 155 | 24 | 98 | 164 | 24 | 266 <n | 286 <n |
| bear_engulf|outside | 155 | 197 | 108 | 161 | 206 | 107 | 460 <n | 474 <n |
| bear_pin | 299 | 334 | 171 | 296 | 332 | 168 | 804 <n | 796 <n |
| bear_pin|bull_engulf | 24 | 50 | 4 | 24 | 47 | 4 | 78 <n | 75 <n |
| bear_pin|bull_engulf|inside | 4 | 0 | 4 | 4 | 0 | 4 | 8 <n | 8 <n |
| bear_pin|bull_engulf|outside | 0 | 4 | 4 | 0 | 4 | 4 | 8 <n | 8 <n |
| bear_pin|inside | 153 | 121 | 39 | 157 | 121 | 39 | 313 <n | 317 <n |
| bear_pin|inside|three_down | 11 | 5 | 31 | 9 | 8 | 31 | 47 <n | 48 <n |
| bear_pin|inside|three_up | 16 | 20 | 4 | 15 | 19 | 4 | 40 <n | 38 <n |
| bear_pin|outside | 59 | 47 | 9 | 60 | 47 | 12 | 115 <n | 119 <n |
| bear_pin|outside|three_down | 9 | 4 | 4 | 11 | 8 | 4 | 17 <n | 23 <n |
| bear_pin|outside|three_up | 0 | 4 | 4 | 0 | 4 | 4 | 8 <n | 8 <n |
| bear_pin|three_down | 24 | 16 | 12 | 24 | 16 | 12 | 52 <n | 52 <n |
| bear_pin|three_up | 72 | 114 | 41 | 72 | 112 | 40 | 227 <n | 224 <n |
| bull_engulf | 450 | 379 | 268 | 447 | 378 | 267 | 1097 <n | 1092 <n |
| bull_engulf|bull_pin | 12 | 23 | 7 | 13 | 23 | 8 | 42 <n | 44 <n |
| bull_engulf|bull_pin|inside | 12 | 0 | 4 | 12 | 0 | 4 | 16 <n | 16 <n |
| bull_engulf|bull_pin|outside | 0 | 16 | 3 | 0 | 16 | 4 | 19 <n | 20 <n |
| bull_engulf|inside | 103 | 113 | 50 | 94 | 109 | 52 | 266 <n | 255 <n |
| bull_engulf|outside | 157 | 167 | 72 | 153 | 157 | 68 | 396 <n | 378 <n |
| bull_pin | 430 | 442 | 181 | 436 | 420 | 185 | 1053 <n | 1041 <n |
| bull_pin|inside | 129 | 138 | 87 | 127 | 129 | 87 | 354 <n | 343 <n |
| bull_pin|inside|three_down | 15 | 16 | 9 | 16 | 16 | 12 | 40 <n | 44 <n |
| bull_pin|inside|three_up | 16 | 15 | 8 | 15 | 14 | 8 | 39 <n | 37 <n |
| bull_pin|outside | 52 | 41 | 16 | 52 | 42 | 16 | 109 <n | 110 <n |
| bull_pin|outside|three_down | 4 | 8 | 0 | 3 | 8 | 0 | 12 <n | 11 <n |
| bull_pin|outside|three_up | 12 | 4 | 7 | 12 | 4 | 7 | 23 <n | 23 <n |
| bull_pin|three_down | 73 | 85 | 20 | 71 | 89 | 20 | 178 <n | 180 <n |
| bull_pin|three_up | 28 | 20 | 16 | 28 | 19 | 20 | 64 <n | 67 <n |
| inside | 1107 | 1224 | 503 | 1121 | 1222 | 503 | 2834 <n | 2846 <n |
| inside|three_down | 102 | 101 | 47 | 105 | 106 | 46 | 250 <n | 257 <n |
| inside|three_up | 95 | 125 | 44 | 85 | 125 | 41 | 264 <n | 251 <n |
| none | 2498 | 2382 | 1331 | 2484 | 2376 | 1320 | 6211 | 6180 |
| outside | 363 | 397 | 143 | 368 | 384 | 146 | 903 <n | 898 <n |
| outside|three_down | 65 | 23 | 34 | 65 | 22 | 35 | 122 <n | 122 <n |
| outside|three_up | 42 | 45 | 40 | 42 | 45 | 32 | 127 <n | 119 <n |
| three_down | 582 | 315 | 221 | 600 | 341 | 226 | 1118 <n | 1167 <n |
| three_up | 541 | 486 | 371 | 520 | 466 | 355 | 1398 <n | 1341 <n |

**pattern on the last closed 8h candle**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| bear_engulf | 500 | 365 | 173 | 504 | 361 | 179 | 1038 <n | 1044 <n |
| bear_engulf|bear_pin | 0 | 16 | 16 | 0 | 16 | 15 | 32 <n | 31 <n |
| bear_engulf|bear_pin|inside | 0 | 8 | 0 | 0 | 8 | 0 | 8 <n | 8 <n |
| bear_engulf|bear_pin|outside | 0 | 6 | 0 | 0 | 8 | 0 | 6 <n | 8 <n |
| bear_engulf|bull_pin | 40 | 55 | 8 | 39 | 53 | 8 | 103 <n | 100 <n |
| bear_engulf|bull_pin|inside | 8 | 0 | 0 | 8 | 0 | 0 | 8 <n | 8 <n |
| bear_engulf|bull_pin|outside | 8 | 0 | 0 | 8 | 0 | 0 | 8 <n | 8 <n |
| bear_engulf|inside | 102 | 113 | 36 | 103 | 114 | 39 | 251 <n | 256 <n |
| bear_engulf|outside | 144 | 258 | 144 | 155 | 256 | 143 | 546 <n | 554 <n |
| bear_pin | 280 | 401 | 177 | 283 | 414 | 174 | 858 <n | 871 <n |
| bear_pin|bull_engulf | 15 | 16 | 16 | 15 | 15 | 16 | 47 <n | 46 <n |
| bear_pin|bull_engulf|inside | 8 | 0 | 0 | 8 | 0 | 0 | 8 <n | 8 <n |
| bear_pin|bull_engulf|outside | 0 | 8 | 7 | 0 | 8 | 8 | 15 <n | 16 <n |
| bear_pin|inside | 56 | 151 | 45 | 56 | 155 | 48 | 252 <n | 259 <n |
| bear_pin|inside|three_down | 8 | 8 | 8 | 8 | 8 | 8 | 24 <n | 24 <n |
| bear_pin|inside|three_up | 16 | 22 | 0 | 16 | 23 | 0 | 38 <n | 39 <n |
| bear_pin|outside | 48 | 22 | 8 | 48 | 21 | 8 | 78 <n | 77 <n |
| bear_pin|outside|three_down | 16 | 16 | 8 | 16 | 16 | 8 | 40 <n | 40 <n |
| bear_pin|outside|three_up | 24 | 8 | 8 | 24 | 8 | 8 | 40 <n | 40 <n |
| bear_pin|three_down | 32 | 16 | 24 | 32 | 16 | 24 | 72 <n | 72 <n |
| bear_pin|three_up | 34 | 31 | 61 | 34 | 27 | 64 | 126 <n | 125 <n |
| bull_engulf | 495 | 431 | 249 | 482 | 400 | 241 | 1175 <n | 1123 <n |
| bull_engulf|bull_pin | 16 | 24 | 0 | 16 | 24 | 0 | 40 <n | 40 <n |
| bull_engulf|bull_pin|outside | 8 | 16 | 8 | 8 | 13 | 8 | 32 <n | 29 <n |
| bull_engulf|inside | 128 | 104 | 40 | 128 | 100 | 39 | 272 <n | 267 <n |
| bull_engulf|outside | 160 | 173 | 37 | 156 | 174 | 37 | 370 <n | 367 <n |
| bull_pin | 366 | 390 | 160 | 370 | 387 | 167 | 916 <n | 924 <n |
| bull_pin|inside | 162 | 205 | 66 | 160 | 200 | 71 | 433 <n | 431 <n |
| bull_pin|inside|three_down | 24 | 24 | 15 | 21 | 24 | 16 | 63 <n | 61 <n |
| bull_pin|inside|three_up | 23 | 37 | 16 | 24 | 28 | 14 | 76 <n | 66 <n |
| bull_pin|outside | 61 | 32 | 16 | 64 | 32 | 16 | 109 <n | 112 <n |
| bull_pin|outside|three_up | 8 | 3 | 8 | 8 | 0 | 8 | 19 <n | 16 <n |
| bull_pin|three_down | 108 | 118 | 32 | 106 | 119 | 32 | 258 <n | 257 <n |
| bull_pin|three_up | 27 | 22 | 23 | 29 | 21 | 24 | 72 <n | 74 <n |
| inside | 1172 | 1132 | 410 | 1184 | 1140 | 412 | 2714 <n | 2736 <n |
| inside|three_down | 99 | 125 | 16 | 107 | 132 | 16 | 240 <n | 255 <n |
| inside|three_up | 92 | 186 | 80 | 87 | 166 | 73 | 358 <n | 326 <n |
| none | 2400 | 2263 | 1493 | 2407 | 2285 | 1476 | 6156 | 6168 |
| outside | 288 | 373 | 168 | 290 | 386 | 159 | 829 <n | 835 <n |
| outside|three_down | 79 | 99 | 30 | 87 | 107 | 32 | 208 <n | 226 <n |
| outside|three_up | 45 | 62 | 32 | 48 | 65 | 32 | 139 <n | 145 <n |
| three_down | 709 | 350 | 184 | 724 | 393 | 189 | 1243 <n | 1306 <n |
| three_up | 488 | 493 | 387 | 459 | 455 | 375 | 1368 <n | 1289 <n |

**pattern on the last closed 12h candle**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| bear_engulf | 473 | 337 | 285 | 489 | 341 | 291 | 1095 <n | 1121 <n |
| bear_engulf|bear_pin | 12 | 36 | 0 | 12 | 36 | 0 | 48 <n | 48 <n |
| bear_engulf|bear_pin|outside | 12 | 0 | 0 | 12 | 0 | 0 | 12 <n | 12 <n |
| bear_engulf|bull_pin | 60 | 21 | 12 | 60 | 20 | 12 | 93 <n | 92 <n |
| bear_engulf|bull_pin|inside | 0 | 12 | 0 | 0 | 12 | 0 | 12 <n | 12 <n |
| bear_engulf|bull_pin|outside | 0 | 12 | 0 | 0 | 12 | 0 | 12 <n | 12 <n |
| bear_engulf|inside | 106 | 138 | 35 | 106 | 142 | 36 | 279 <n | 284 <n |
| bear_engulf|outside | 198 | 166 | 72 | 212 | 163 | 71 | 436 <n | 446 <n |
| bear_pin | 318 | 244 | 162 | 318 | 250 | 161 | 724 <n | 729 <n |
| bear_pin|bull_engulf | 0 | 47 | 0 | 0 | 47 | 0 | 47 <n | 47 <n |
| bear_pin|inside | 114 | 158 | 12 | 120 | 158 | 12 | 284 <n | 290 <n |
| bear_pin|inside|three_down | 12 | 12 | 11 | 12 | 12 | 12 | 35 <n | 36 <n |
| bear_pin|inside|three_up | 0 | 12 | 0 | 0 | 12 | 0 | 12 <n | 12 <n |
| bear_pin|outside | 48 | 33 | 0 | 48 | 33 | 0 | 81 <n | 81 <n |
| bear_pin|outside|three_down | 0 | 0 | 12 | 0 | 0 | 12 | 12 <n | 12 <n |
| bear_pin|three_down | 24 | 24 | 12 | 24 | 24 | 12 | 60 <n | 60 <n |
| bear_pin|three_up | 70 | 36 | 12 | 69 | 36 | 12 | 118 <n | 117 <n |
| bull_engulf | 493 | 434 | 318 | 461 | 445 | 316 | 1245 <n | 1222 <n |
| bull_engulf|bull_pin | 24 | 0 | 10 | 24 | 0 | 12 | 34 <n | 36 <n |
| bull_engulf|bull_pin|inside | 12 | 0 | 0 | 12 | 0 | 0 | 12 <n | 12 <n |
| bull_engulf|inside | 130 | 118 | 59 | 131 | 112 | 58 | 307 <n | 301 <n |
| bull_engulf|outside | 117 | 211 | 51 | 117 | 202 | 48 | 379 <n | 367 <n |
| bull_pin | 359 | 283 | 178 | 352 | 277 | 171 | 820 <n | 800 <n |
| bull_pin|inside | 121 | 145 | 95 | 126 | 149 | 95 | 361 <n | 370 <n |
| bull_pin|inside|three_down | 23 | 32 | 0 | 24 | 35 | 0 | 55 <n | 59 <n |
| bull_pin|inside|three_up | 24 | 39 | 24 | 23 | 40 | 24 | 87 <n | 87 <n |
| bull_pin|outside | 45 | 60 | 48 | 48 | 59 | 48 | 153 <n | 155 <n |
| bull_pin|outside|three_up | 24 | 23 | 24 | 24 | 24 | 24 | 71 <n | 72 <n |
| bull_pin|three_down | 81 | 104 | 36 | 82 | 107 | 36 | 221 <n | 225 <n |
| bull_pin|three_up | 60 | 21 | 0 | 60 | 24 | 0 | 81 <n | 84 <n |
| inside | 1058 | 1313 | 602 | 1057 | 1290 | 600 | 2973 <n | 2947 <n |
| inside|three_down | 144 | 123 | 48 | 143 | 124 | 48 | 315 <n | 315 <n |
| inside|three_up | 80 | 116 | 56 | 77 | 103 | 55 | 252 <n | 235 <n |
| none | 2188 | 2258 | 1305 | 2169 | 2267 | 1300 | 5751 <n | 5736 <n |
| outside | 500 | 539 | 265 | 511 | 536 | 259 | 1304 <n | 1306 <n |
| outside|three_down | 82 | 100 | 12 | 81 | 113 | 12 | 194 <n | 206 <n |
| outside|three_up | 89 | 68 | 46 | 86 | 65 | 48 | 203 <n | 199 <n |
| three_down | 690 | 455 | 178 | 735 | 474 | 189 | 1323 <n | 1398 <n |
| three_up | 506 | 452 | 229 | 497 | 434 | 213 | 1187 <n | 1144 <n |

**pattern on the last closed 1d candle**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| bear_engulf | 681 | 503 | 180 | 686 | 522 | 184 | 1364 <n | 1392 <n |
| bear_engulf|bear_pin|outside | 24 | 0 | 0 | 24 | 0 | 0 | 24 <n | 24 <n |
| bear_engulf|bull_pin|outside | 0 | 24 | 0 | 0 | 24 | 0 | 24 <n | 24 <n |
| bear_engulf|inside | 24 | 24 | 64 | 24 | 24 | 66 | 112 <n | 114 <n |
| bear_engulf|outside | 189 | 91 | 64 | 185 | 90 | 68 | 344 <n | 343 <n |
| bear_pin | 304 | 246 | 117 | 306 | 242 | 113 | 667 <n | 661 <n |
| bear_pin|bull_engulf | 0 | 23 | 0 | 0 | 22 | 0 | 23 <n | 22 <n |
| bear_pin|bull_engulf|outside | 0 | 48 | 0 | 0 | 44 | 0 | 48 <n | 44 <n |
| bear_pin|inside | 64 | 119 | 47 | 63 | 114 | 45 | 230 <n | 222 <n |
| bear_pin|inside|three_down | 62 | 24 | 0 | 64 | 24 | 0 | 86 <n | 88 <n |
| bear_pin|inside|three_up | 0 | 24 | 0 | 0 | 24 | 0 | 24 <n | 24 <n |
| bear_pin|outside | 48 | 0 | 0 | 47 | 0 | 0 | 48 <n | 47 <n |
| bear_pin|outside|three_down | 22 | 0 | 22 | 20 | 0 | 22 | 44 <n | 42 <n |
| bear_pin|three_down | 19 | 0 | 0 | 24 | 0 | 0 | 19 <n | 24 <n |
| bear_pin|three_up | 72 | 46 | 24 | 71 | 48 | 24 | 142 <n | 143 <n |
| bull_engulf | 457 | 493 | 229 | 428 | 479 | 230 | 1179 <n | 1137 <n |
| bull_engulf|bull_pin | 72 | 22 | 0 | 71 | 21 | 0 | 94 <n | 92 <n |
| bull_engulf|inside | 93 | 114 | 24 | 96 | 101 | 24 | 231 <n | 221 <n |
| bull_engulf|outside | 167 | 204 | 80 | 165 | 214 | 85 | 451 <n | 464 <n |
| bull_pin | 422 | 202 | 155 | 425 | 201 | 165 | 779 <n | 791 <n |
| bull_pin|inside | 142 | 129 | 48 | 143 | 135 | 48 | 319 <n | 326 <n |
| bull_pin|inside|three_down | 0 | 24 | 0 | 0 | 24 | 0 | 24 <n | 24 <n |
| bull_pin|inside|three_up | 0 | 21 | 0 | 0 | 24 | 0 | 21 <n | 24 <n |
| bull_pin|outside | 72 | 63 | 48 | 71 | 66 | 48 | 183 <n | 185 <n |
| bull_pin|outside|three_down | 0 | 19 | 0 | 0 | 22 | 0 | 19 <n | 22 <n |
| bull_pin|outside|three_up | 0 | 21 | 0 | 0 | 21 | 0 | 21 <n | 21 <n |
| bull_pin|three_down | 47 | 96 | 0 | 48 | 96 | 0 | 143 <n | 144 <n |
| inside | 941 | 1554 | 641 | 934 | 1545 | 629 | 3136 <n | 3108 <n |
| inside|three_down | 113 | 171 | 48 | 120 | 184 | 44 | 332 <n | 348 <n |
| inside|three_up | 86 | 162 | 94 | 88 | 158 | 85 | 342 <n | 331 <n |
| none | 2490 | 2232 | 1487 | 2480 | 2247 | 1488 | 6209 | 6215 |
| outside | 293 | 417 | 166 | 299 | 397 | 166 | 876 <n | 862 <n |
| outside|three_down | 71 | 137 | 0 | 72 | 139 | 0 | 208 <n | 211 <n |
| outside|three_up | 24 | 0 | 41 | 24 | 0 | 35 | 65 <n | 59 <n |
| three_down | 886 | 433 | 165 | 945 | 437 | 168 | 1484 <n | 1550 <n |
| three_up | 412 | 496 | 465 | 399 | 489 | 450 | 1373 <n | 1338 <n |

## F5. Bollinger state (20, 2, closed bars; band walk = 3+ closes beyond the band while the bandwidth expands)

**4h Bollinger state**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| break_down | 238 | 201 | 130 | 258 | 217 | 129 | 569 <n | 604 <n |
| break_up | 192 | 218 | 89 | 179 | 204 | 87 | 499 <n | 470 <n |
| inside | 6760 | 6725 | 3480 | 6782 | 6703 | 3463 | 16965 | 16948 |
| na | 26 | 0 | 0 | 31 | 0 | 0 | 26 <n | 31 <n |
| outside_down | 154 | 121 | 64 | 159 | 126 | 67 | 339 <n | 352 <n |
| outside_up | 104 | 141 | 67 | 92 | 126 | 63 | 312 <n | 281 <n |
| reenter_from_lower | 254 | 214 | 132 | 268 | 227 | 136 | 600 <n | 631 <n |
| reenter_from_upper | 194 | 247 | 87 | 192 | 242 | 94 | 528 <n | 528 <n |
| walk_down | 208 | 116 | 64 | 215 | 147 | 64 | 388 <n | 426 <n |
| walk_up | 167 | 199 | 96 | 146 | 186 | 84 | 462 <n | 416 <n |

**1d Bollinger state**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| break_down | 147 | 108 | 144 | 150 | 113 | 144 | 399 <n | 407 <n |
| break_up | 209 | 289 | 216 | 176 | 244 | 216 | 714 <n | 636 <n |
| inside | 6592 | 6746 | 3298 | 6611 | 6763 | 3270 | 16636 | 16644 |
| na | 450 | 0 | 0 | 469 | 0 | 0 | 450 <n | 469 <n |
| outside_down | 90 | 65 | 24 | 96 | 69 | 24 | 179 <n | 189 <n |
| outside_up | 163 | 116 | 47 | 158 | 114 | 45 | 326 <n | 317 <n |
| reenter_from_lower | 183 | 133 | 144 | 181 | 140 | 144 | 460 <n | 465 <n |
| reenter_from_upper | 234 | 279 | 226 | 236 | 308 | 237 | 739 <n | 781 <n |
| walk_down | 206 | 63 | 0 | 221 | 62 | 0 | 269 <n | 283 <n |
| walk_up | 23 | 383 | 110 | 24 | 365 | 107 | 516 <n | 496 <n |

**long confidence: 4h re-entry from below the lower band (long side only)**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| False | 8043 | 7968 | 4077 | 8322 | 8178 | 4187 | 20088 | 20687 |
| True | 254 | 214 | 132 | 0 | 0 | 0 | 600 <n | 0 <n |

**short veto: 4h band walk down in progress (short side only)**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| False | 8297 | 8182 | 4209 | 8107 | 8031 | 4123 | 20688 | 20261 |
| True | 0 | 0 | 0 | 215 | 147 | 64 | 0 <n | 426 <n |

**short veto (alt, counted only): %b <= 0 on the last closed 4h bar**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| False | 8297 | 8182 | 4209 | 7690 | 7688 | 3927 | 20688 | 19305 |
| True | 0 | 0 | 0 | 632 | 490 | 260 | 0 <n | 1382 <n |

**4h bandwidth squeeze (<= 10th trailing percentile over 180 closed 4h bars)**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| False | 7288 | 7073 | 3730 | 7291 | 7069 | 3711 | 18091 | 18071 |
| True | 1009 | 1109 | 479 | 1031 | 1109 | 476 | 2597 <n | 2616 <n |

## F6. Bitcoin phase

**phase A: daily fractal pivots (HH&HL markup, LH&LL markdown, else distribution/accumulation by the last trend)**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| accumulation | 1071 | 1700 | 617 | 1070 | 1718 | 620 | 3388 <n | 3408 <n |
| distribution | 1559 | 1319 | 1537 | 1564 | 1316 | 1519 | 4415 <n | 4399 <n |
| markdown | 2333 | 2015 | 491 | 2323 | 1990 | 496 | 4839 <n | 4809 <n |
| markup | 2793 | 3148 | 1564 | 2809 | 3154 | 1552 | 7505 | 7515 |
| na | 541 | 0 | 0 | 556 | 0 | 0 | 541 <n | 556 <n |

**phase B (counted only): 30-day return +/- 7.5 % markup/markdown, else distribution above SMA50 / accumulation below**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| accumulation | 2023 | 1772 | 757 | 2021 | 1795 | 760 | 4552 <n | 4576 <n |
| distribution | 658 | 1571 | 1021 | 650 | 1515 | 1019 | 3250 <n | 3184 <n |
| markdown | 3438 | 858 | 693 | 3466 | 894 | 688 | 4989 <n | 5048 <n |
| markup | 1096 | 3981 | 1738 | 1091 | 3974 | 1720 | 6815 | 6785 |
| na | 1082 | 0 | 0 | 1094 | 0 | 0 | 1082 <n | 1094 <n |

**intraday: 24h range <= 1.5 x ATR14(4h) = balance, else trend by the 24h close change**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| balance | 1032 | 1220 | 589 | 1031 | 1219 | 587 | 2841 <n | 2837 <n |
| trend_down | 3763 | 3287 | 1710 | 3898 | 3418 | 1733 | 8760 | 9049 |
| trend_up | 3502 | 3675 | 1910 | 3393 | 3541 | 1867 | 9087 | 8801 |

**intraday (alt, counted only): last 12 1h closes inside the prior 12 bars' range = balance**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| balance | 3123 | 3659 | 1623 | 3127 | 3657 | 1628 | 8405 | 8412 |
| trend_down | 2729 | 2088 | 1181 | 2850 | 2179 | 1198 | 5998 | 6227 |
| trend_up | 2445 | 2435 | 1405 | 2345 | 2342 | 1361 | 6285 | 6048 |

phase A == phase B on events: long: 7646 agree / 11960 disagree, short: 7651 agree / 11942 disagree

## F7. Own additions

**volatility regime: ATR14(4h) tercile over the trailing 180 closed 4h bars**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| low | 3523 | 2610 | 1599 | 3560 | 2601 | 1589 | 7732 | 7750 |
| mid | 2161 | 2634 | 1092 | 2144 | 2669 | 1079 | 5887 <n | 5892 <n |
| high | 1953 | 2938 | 1518 | 1946 | 2908 | 1519 | 6409 | 6373 |
| na | 660 | 0 | 0 | 672 | 0 | 0 | 660 <n | 672 <n |

**session (UTC: asia 00-08, london 08-13, ny 13-21, late 21-24)**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| asia | 2793 | 2781 | 1429 | 2811 | 2801 | 1413 | 7003 | 7025 |
| late | 1030 | 1009 | 523 | 1033 | 996 | 524 | 2562 <n | 2553 <n |
| london | 1736 | 1712 | 864 | 1736 | 1715 | 866 | 4312 <n | 4317 <n |
| ny | 2738 | 2680 | 1393 | 2742 | 2666 | 1384 | 6811 | 6792 |

**weekend (Saturday/Sunday UTC)**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| False | 5934 | 5799 | 2982 | 5933 | 5779 | 2979 | 14715 | 14691 |
| True | 2363 | 2383 | 1227 | 2389 | 2399 | 1208 | 5973 | 5996 |

**HTF alignment: weekly close above (long) / below (short) the close 4 weeks earlier**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| False | 5593 | 2833 | 1465 | 3473 | 5309 | 2736 | 9891 | 11518 |
| True | 2704 | 5349 | 2744 | 4849 | 2869 | 1451 | 10797 | 9169 |

**last settled funding rate: neg / low (<= 0.01 %) / high**

| value | long 2022 | long 2023 | long 2024H1 | short 2022 | short 2023 | short 2024H1 | long all | short all |
|---|---|---|---|---|---|---|---|---|
| neg | 1865 | 831 | 108 | 1860 | 799 | 110 | 2804 <n | 2769 <n |
| low | 6432 | 6830 | 2920 | 6462 | 6840 | 2916 | 16182 | 16218 |
| high | 0 | 521 | 1181 | 0 | 539 | 1161 | 1702 <n | 1700 <n |

## Pairs of the strongest factors (chosen by the operator's emphasis, not by outcome)

**confluence x 4h Bollinger state, long** (rows = n_layers, columns = bb_4h_state; all three years)

| n_layers \ bb_4h_state | break_down | break_up | inside | na | outside_down | outside_up | reenter_from_lower | reenter_from_upper | walk_down | walk_up |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 236 <n | 175 <n | 2416 <n | 11 <n | 152 <n | 105 <n | 117 <n | 140 <n | 174 <n | 170 <n |
| 2 | 188 <n | 188 <n | 5056 <n | 7 <n | 111 <n | 119 <n | 206 <n | 181 <n | 123 <n | 162 <n |
| 3+ | 145 <n | 136 <n | 9493 | 8 <n | 76 <n | 88 <n | 277 <n | 207 <n | 91 <n | 130 <n |

**confluence x 4h Bollinger state, short** (rows = n_layers, columns = bb_4h_state; all three years)

| n_layers \ bb_4h_state | break_down | break_up | inside | na | outside_down | outside_up | reenter_from_lower | reenter_from_upper | walk_down | walk_up |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 175 <n | 229 <n | 2541 <n | 10 <n | 98 <n | 141 <n | 108 <n | 156 <n | 164 <n | 189 <n |
| 2 | 200 <n | 153 <n | 5275 <n | 14 <n | 128 <n | 89 <n | 248 <n | 154 <n | 145 <n | 151 <n |
| 3+ | 229 <n | 88 <n | 9132 | 7 <n | 126 <n | 51 <n | 275 <n | 218 <n | 117 <n | 76 <n |

**phase A x ladder rung, long** (rows = phase_a, columns = ladder_rung; all three years)

| phase_a \ ladder_rung | 12h | 1d | 8h | none |
|---|---|---|---|---|
| accumulation | 593 <n | 2258 <n | 449 <n | 88 <n |
| distribution | 941 <n | 2612 <n | 676 <n | 186 <n |
| markdown | 928 <n | 2867 <n | 866 <n | 178 <n |
| markup | 1429 <n | 4549 <n | 1201 <n | 326 <n |
| na | 134 <n | 272 <n | 113 <n | 22 <n |

**phase A x ladder rung, short** (rows = phase_a, columns = ladder_rung; all three years)

| phase_a \ ladder_rung | 12h | 1d | 8h | none |
|---|---|---|---|---|
| accumulation | 653 <n | 2144 <n | 436 <n | 175 <n |
| distribution | 910 <n | 2618 <n | 708 <n | 163 <n |
| markdown | 886 <n | 2964 <n | 745 <n | 214 <n |
| markup | 1422 <n | 4573 <n | 1214 <n | 306 <n |
| na | 154 <n | 266 <n | 122 <n | 14 <n |

**4h candle pattern x confluence, long** (rows = pat_4h, columns = n_layers; all three years)

| pat_4h \ n_layers | 1 | 2 | 3+ |
|---|---|---|---|
| bear_engulf | 258 <n | 375 <n | 538 <n |
| bear_engulf|bear_pin | 9 <n | 12 <n | 23 <n |
| bear_engulf|bear_pin|inside | 4 <n | 1 <n | 3 <n |
| bear_engulf|bull_pin | 17 <n | 18 <n | 36 <n |
| bear_engulf|bull_pin|inside | 7 <n | 1 <n | 0 <n |
| bear_engulf|bull_pin|outside | 1 <n | 2 <n | 5 <n |
| bear_engulf|inside | 51 <n | 103 <n | 112 <n |
| bear_engulf|outside | 82 <n | 166 <n | 212 <n |
| bear_pin | 122 <n | 214 <n | 468 <n |
| bear_pin|bull_engulf | 8 <n | 25 <n | 45 <n |
| bear_pin|bull_engulf|inside | 3 <n | 4 <n | 1 <n |
| bear_pin|bull_engulf|outside | 3 <n | 3 <n | 2 <n |
| bear_pin|inside | 46 <n | 116 <n | 151 <n |
| bear_pin|inside|three_down | 13 <n | 16 <n | 18 <n |
| bear_pin|inside|three_up | 10 <n | 14 <n | 16 <n |
| bear_pin|outside | 13 <n | 40 <n | 62 <n |
| bear_pin|outside|three_down | 1 <n | 3 <n | 13 <n |
| bear_pin|outside|three_up | 1 <n | 1 <n | 6 <n |
| bear_pin|three_down | 10 <n | 19 <n | 23 <n |
| bear_pin|three_up | 34 <n | 77 <n | 116 <n |
| bull_engulf | 140 <n | 291 <n | 666 <n |
| bull_engulf|bull_pin | 12 <n | 14 <n | 16 <n |
| bull_engulf|bull_pin|inside | 1 <n | 7 <n | 8 <n |
| bull_engulf|bull_pin|outside | 3 <n | 1 <n | 15 <n |
| bull_engulf|inside | 41 <n | 74 <n | 151 <n |
| bull_engulf|outside | 66 <n | 102 <n | 228 <n |
| bull_pin | 159 <n | 301 <n | 593 <n |
| bull_pin|inside | 47 <n | 109 <n | 198 <n |
| bull_pin|inside|three_down | 9 <n | 10 <n | 21 <n |
| bull_pin|inside|three_up | 5 <n | 11 <n | 23 <n |
| bull_pin|outside | 5 <n | 36 <n | 68 <n |
| bull_pin|outside|three_down | 4 <n | 4 <n | 4 <n |
| bull_pin|outside|three_up | 1 <n | 8 <n | 14 <n |
| bull_pin|three_down | 40 <n | 40 <n | 98 <n |
| bull_pin|three_up | 4 <n | 16 <n | 44 <n |
| inside | 416 <n | 846 <n | 1572 <n |
| inside|three_down | 61 <n | 70 <n | 119 <n |
| inside|three_up | 42 <n | 77 <n | 145 <n |
| none | 1067 <n | 1904 <n | 3240 <n |
| outside | 164 <n | 309 <n | 430 <n |
| outside|three_down | 35 <n | 52 <n | 35 <n |
| outside|three_up | 21 <n | 38 <n | 68 <n |
| three_down | 369 <n | 361 <n | 388 <n |
| three_up | 291 <n | 450 <n | 657 <n |

**4h candle pattern x confluence, short** (rows = pat_4h, columns = n_layers; all three years)

| pat_4h \ n_layers | 1 | 2 | 3+ |
|---|---|---|---|
| bear_engulf | 153 <n | 343 <n | 731 <n |
| bear_engulf|bear_pin | 12 <n | 13 <n | 21 <n |
| bear_engulf|bear_pin|inside | 1 <n | 4 <n | 3 <n |
| bear_engulf|bull_pin | 8 <n | 25 <n | 39 <n |
| bear_engulf|bull_pin|inside | 1 <n | 0 <n | 7 <n |
| bear_engulf|bull_pin|outside | 2 <n | 3 <n | 3 <n |
| bear_engulf|inside | 30 <n | 83 <n | 173 <n |
| bear_engulf|outside | 42 <n | 143 <n | 289 <n |
| bear_pin | 122 <n | 240 <n | 434 <n |
| bear_pin|bull_engulf | 7 <n | 29 <n | 39 <n |
| bear_pin|bull_engulf|inside | 3 <n | 4 <n | 1 <n |
| bear_pin|bull_engulf|outside | 0 <n | 3 <n | 5 <n |
| bear_pin|inside | 44 <n | 95 <n | 178 <n |
| bear_pin|inside|three_down | 6 <n | 9 <n | 33 <n |
| bear_pin|inside|three_up | 10 <n | 15 <n | 13 <n |
| bear_pin|outside | 14 <n | 29 <n | 76 <n |
| bear_pin|outside|three_down | 0 <n | 9 <n | 14 <n |
| bear_pin|outside|three_up | 0 <n | 4 <n | 4 <n |
| bear_pin|three_down | 11 <n | 11 <n | 30 <n |
| bear_pin|three_up | 59 <n | 72 <n | 93 <n |
| bull_engulf | 236 <n | 386 <n | 470 <n |
| bull_engulf|bull_pin | 8 <n | 15 <n | 21 <n |
| bull_engulf|bull_pin|inside | 1 <n | 6 <n | 9 <n |
| bull_engulf|bull_pin|outside | 3 <n | 3 <n | 14 <n |
| bull_engulf|inside | 67 <n | 69 <n | 119 <n |
| bull_engulf|outside | 102 <n | 139 <n | 137 <n |
| bull_pin | 185 <n | 340 <n | 516 <n |
| bull_pin|inside | 53 <n | 117 <n | 173 <n |
| bull_pin|inside|three_down | 12 <n | 10 <n | 22 <n |
| bull_pin|inside|three_up | 14 <n | 7 <n | 16 <n |
| bull_pin|outside | 14 <n | 45 <n | 51 <n |
| bull_pin|outside|three_down | 1 <n | 1 <n | 9 <n |
| bull_pin|outside|three_up | 10 <n | 10 <n | 3 <n |
| bull_pin|three_down | 34 <n | 51 <n | 95 <n |
| bull_pin|three_up | 18 <n | 21 <n | 28 <n |
| inside | 495 <n | 890 <n | 1461 <n |
| inside|three_down | 53 <n | 68 <n | 136 <n |
| inside|three_up | 58 <n | 85 <n | 108 <n |
| none | 1028 <n | 1959 <n | 3193 <n |
| outside | 153 <n | 310 <n | 435 <n |
| outside|three_down | 22 <n | 40 <n | 60 <n |
| outside|three_up | 37 <n | 38 <n | 44 <n |
| three_down | 260 <n | 347 <n | 560 <n |
| three_up | 422 <n | 466 <n | 453 <n |

## Angle (e): two reasonable definitions, counts under both (trials.csv; T8 = PRIOR_RULE, counted by prior_rule_count.py)

| id | factor | primary | alternative | n primary (long/short) | n alt (long/short) | why the primary |
|---|---|---|---|---|---|---|
| T1 | F1 role rule | support iff last closed 1h close > level | last closed 4h close > level | 21888/21888 | 16293/16528 | the 1h close is the decision grid itself (no stale role up to 4 h); a 4h close flips later |
| T2 | F2 zone width | K_ZONE = 0.5 x ATR14(4h) | 1.0 x ATR14(4h) | 20688/20687 | 21610/21594 | half an ATR keeps 'at the level' tighter than one 4h bar's typical range |
| T3 | F3 operator condition | close rule: current close past the prior daily open | touch rule: the partial day's extreme past the prior open | 10303/10629 | 14594/14676 | the operator says 'has moved past the opening' at a decision; a close is the PIT reading a trader quotes |
| T4 | F3 width W | W = 2.5 % of price | W = 1.5 % | 12558/12565 | 9365/9392 | 2.5 % is about one DEV median daily range; 1.5 % pushes most days to the 12h/8h rungs |
| T5 | F5 short veto | band walk down in progress (3+ closes beyond, bandwidth expanding) | %b <= 0 on the last closed 4h bar | 0/426 | 0/1382 | the operator's 'dance' is the walk, not a single close outside |
| T6 | F6 phase | A: daily fractal pivots | B: 30-day return vs 7.5 % + SMA50 split | 7505/7515 | 6815/6785 | A is what a trader reads off swing highs/lows (markup = HH&HL); B is the repo's trend_tag reused |
| T7 | F6 intraday | 24h range <= 1.5 ATR = balance | last 12 1h closes inside the prior 12 bars' range | 2841/2837 | 8405/8412 | range-vs-ATR is one number a trader checks; the inside-range rule needs two windows |

T1 counts grid rows (not events) whose nearest source and layer count agree under both role rules; T2 counts rows within the zone.

