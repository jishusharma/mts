# COUNTS: DEV decision events per factor value (counts only, no outcome read)

Built by `counts.py` from the vectorised frames (`run_dev.py vec`), DEV decision hours 2022-04-01 .. 2024-06-30 (bar open < 2024-07-01). No forward return, win/loss or exit exists in any file of this folder.

## Ledger

| step | long | short |
|---|---|---|
| DEV decision hours | 19729 | 19729 |
| at a same-side level (nearest within 1.0 x ATR14 1h) | 16834 | 16707 |
| after the 4 h same-side cooldown | 3713 | 3702 |
| with a valid ladder stop (stop_tf != none): **tradeable ledger** | **3018** | **3005** |
| distinct UTC days in the tradeable ledger | 800 | 796 |

## Power: n needed for a decisive test (research_kit)

- Outcome unit R (the PRE_REG trade: ladder stop, fixed 2 R target, all-taker cost). Per-trade sd = 1.5 R (OURS: a 1 R stop / 2 R target trade at the break-even hit rate 1/3 has sd 3 x sqrt(2/9) = 1.41 R; rounded up).
- Cross-check with FABLE_RUNS_AUDIT 1.5: per-trade sd 1.97 % at a 4 h hold. Divided by the median ladder stop (1.64 %) that is 1.20 R per trade, below 1.5 R, so 1.5 R is the conservative choice.
- Cost in R: median of the tradeable ledger = 0.14 % / stop % = **0.085 R** (all-taker); maker-in 0.09 % gives 0.055 R.
- Plausible effect of one context filter = 0.2 R (OURS: about a quarter of the best SOURCED whole-setup expectancy, +0.75 R gross, CATALOGUE T-3 quoted in FABLE_RUNS_AUDIT 3.2).
- `research_kit.power_check`: MDE = 2.8 x sd / sqrt(n) must satisfy MDE + cost <= 0.2 R  =>  **n_needed = 1338 independent units** per bucket and side. Units are UTC days (day-clustered SE), so a bucket is flagged LOW when its distinct-day count is below n_needed. The matched-baseline difference adds about sqrt(1 + 1/K) = 1.025 to the SE at K = 20 controls; ignored here (within rounding).

- Check: power_check(n=1338, sd=1.5, plausible=0.2, cost=0.085) -> mde 0.115 R, needed 0.200 R, proceed=True.

## Per factor value (tradeable ledger)

n = events, d = distinct UTC days; per-year columns are events. LOW = d < n_needed.

| factor | value | long n | long d | short n | short d | 2022 (Apr-Dec) | 2023 | 2024H1 | flag |
|---|---|---|---|---|---|---|---|---|---|
| f1_near_layer | bb4h | 173 | 140 | 165 | 133 | 110 | 162 | 66 | LOW |
| f1_near_layer | krown | 106 | 84 | 124 | 103 | 92 | 83 | 55 | LOW |
| f1_near_layer | pd_va | 884 | 510 | 856 | 492 | 614 | 793 | 333 | LOW |
| f1_near_layer | prior_dw | 281 | 210 | 268 | 202 | 227 | 207 | 115 | LOW |
| f1_near_layer | pw_va | 209 | 136 | 211 | 155 | 143 | 219 | 58 | LOW |
| f1_near_layer | round | 398 | 282 | 429 | 301 | 234 | 248 | 345 | LOW |
| f1_near_layer | vwap | 967 | 573 | 952 | 548 | 637 | 899 | 383 | LOW |
| f2_conf_obj | 1 | 1303 | 633 | 1293 | 653 | 916 | 1157 | 523 | LOW |
| f2_conf_obj | 2 | 1199 | 624 | 1208 | 626 | 800 | 1065 | 542 | LOW |
| f2_conf_obj | 3+ | 516 | 340 | 504 | 336 | 341 | 389 | 290 | LOW |
| f2_touch_cat | dynamic | 1140 | 621 | 1117 | 587 | 747 | 1061 | 449 | LOW |
| f2_touch_cat | first | 199 | 176 | 165 | 151 | 145 | 151 | 68 | LOW |
| f2_touch_cat | retest | 1467 | 693 | 1495 | 679 | 1002 | 1200 | 760 | LOW |
| f2_touch_cat | untested | 212 | 188 | 228 | 189 | 163 | 199 | 78 | LOW |
| f3_armed | False | 1409 | 475 | 1295 | 457 | 918 | 1182 | 604 | LOW |
| f3_armed | True | 1609 | 516 | 1710 | 517 | 1139 | 1429 | 751 | LOW |
| f3_stop_tf | 12h | 401 | 236 | 397 | 225 | 282 | 327 | 189 | LOW |
| f3_stop_tf | 8h | 235 | 178 | 213 | 164 | 162 | 172 | 114 | LOW |
| f3_stop_tf | D | 2382 | 700 | 2395 | 704 | 1613 | 2112 | 1052 | LOW |
| f4_D_align | against | 373 | 103 | 407 | 112 | 295 | 333 | 152 | LOW |
| f4_D_align | none | 2193 | 583 | 2170 | 577 | 1395 | 1922 | 1046 | LOW |
| f4_D_align | with | 452 | 114 | 428 | 107 | 367 | 356 | 157 | LOW |
| f4_12h_align | against | 397 | 194 | 383 | 200 | 278 | 330 | 172 | LOW |
| f4_12h_align | none | 2166 | 717 | 2176 | 709 | 1457 | 1909 | 976 | LOW |
| f4_12h_align | with | 455 | 216 | 446 | 202 | 322 | 372 | 207 | LOW |
| f4_8h_align | against | 407 | 257 | 420 | 261 | 278 | 373 | 176 | LOW |
| f4_8h_align | none | 2108 | 749 | 2100 | 742 | 1440 | 1799 | 969 | LOW |
| f4_8h_align | with | 503 | 296 | 485 | 291 | 339 | 439 | 210 | LOW |
| f4_4h_align | against | 450 | 368 | 443 | 364 | 303 | 399 | 191 | LOW |
| f4_4h_align | none | 2069 | 761 | 2057 | 764 | 1431 | 1764 | 931 | LOW |
| f4_4h_align | with | 499 | 391 | 505 | 400 | 323 | 448 | 233 | LOW |
| f5_1h | break_lower | 51 | 50 | 118 | 112 | 60 | 83 | 26 | LOW |
| f5_1h | break_upper | 139 | 131 | 46 | 45 | 57 | 84 | 44 | LOW |
| f5_1h | inside | 2611 | 797 | 2594 | 783 | 1783 | 2252 | 1170 | LOW |
| f5_1h | reenter_lower | 62 | 59 | 123 | 113 | 70 | 74 | 41 | LOW |
| f5_1h | reenter_upper | 116 | 110 | 60 | 58 | 55 | 73 | 48 | LOW |
| f5_1h | walk_lower | 8 | 8 | 52 | 52 | 23 | 24 | 13 | LOW |
| f5_1h | walk_upper | 31 | 31 | 12 | 12 | 9 | 21 | 13 | LOW |
| f5_4h | break_lower | 65 | 55 | 129 | 100 | 71 | 83 | 40 | LOW |
| f5_4h | break_upper | 98 | 76 | 40 | 36 | 39 | 73 | 26 | LOW |
| f5_4h | inside | 2573 | 761 | 2534 | 753 | 1750 | 2199 | 1158 | LOW |
| f5_4h | reenter_lower | 99 | 94 | 110 | 102 | 76 | 80 | 53 | LOW |
| f5_4h | reenter_upper | 89 | 86 | 86 | 84 | 47 | 91 | 37 | LOW |
| f5_4h | walk_lower | 46 | 35 | 58 | 47 | 46 | 40 | 18 | LOW |
| f5_4h | walk_upper | 48 | 39 | 48 | 43 | 28 | 45 | 23 | LOW |
| f5_veto | False | 2987 | 799 | 2953 | 794 | 2030 | 2576 | 1334 | LOW |
| f5_veto | True | 31 | 31 | 52 | 52 | 27 | 35 | 21 | LOW |
| f5_conf | False | 2956 | 800 | 2945 | 795 | 2012 | 2566 | 1323 | LOW |
| f5_conf | True | 62 | 59 | 60 | 58 | 45 | 45 | 32 | LOW |
| f6_phaseA | accumulation | 280 | 74 | 278 | 75 | 115 | 281 | 162 | LOW |
| f6_phaseA | distribution | 326 | 89 | 321 | 88 | 148 | 300 | 199 | LOW |
| f6_phaseA | markdown | 1016 | 269 | 1026 | 270 | 1573 | 422 | 47 | LOW |
| f6_phaseA | markup | 1396 | 368 | 1380 | 363 | 221 | 1608 | 947 | LOW |
| f6_phaseB | accumulation | 350 | 95 | 330 | 94 | 470 | 210 | 0 | LOW |
| f6_phaseB | balance | 399 | 111 | 403 | 112 | 189 | 384 | 229 | LOW |
| f6_phaseB | distribution | 364 | 97 | 366 | 96 | 15 | 366 | 349 | LOW |
| f6_phaseB | markdown | 799 | 209 | 815 | 210 | 1119 | 266 | 229 | LOW |
| f6_phaseB | markup | 1106 | 288 | 1091 | 284 | 264 | 1385 | 548 | LOW |
| f6_intraday | balance | 2405 | 752 | 2391 | 759 | 1617 | 2102 | 1077 | LOW |
| f6_intraday | trend_down | 239 | 146 | 370 | 213 | 270 | 220 | 119 | LOW |
| f6_intraday | trend_up | 374 | 227 | 244 | 162 | 170 | 289 | 159 | LOW |
| f7_volreg | high | 925 | 400 | 933 | 393 | 521 | 907 | 430 | LOW |
| f7_volreg | low | 1130 | 437 | 1072 | 438 | 957 | 781 | 464 | LOW |
| f7_volreg | mid | 961 | 500 | 998 | 496 | 575 | 923 | 461 | LOW |
| f7_volreg | na | 2 | 1 | 2 | 1 | 4 | 0 | 0 | LOW |
| f7_squeeze | normal | 2368 | 673 | 2321 | 663 | 1529 | 2078 | 1082 | LOW |
| f7_squeeze | squeeze | 650 | 247 | 684 | 243 | 528 | 533 | 273 | LOW |
| f7_session | asia | 1008 | 678 | 1005 | 667 | 686 | 859 | 468 | LOW |
| f7_session | late | 375 | 361 | 365 | 353 | 250 | 325 | 165 | LOW |
| f7_session | london | 650 | 650 | 634 | 634 | 443 | 560 | 281 | LOW |
| f7_session | ny | 985 | 700 | 1001 | 693 | 678 | 867 | 441 | LOW |
| f7_weekend | weekday | 2125 | 593 | 2182 | 599 | 1464 | 1888 | 955 | LOW |
| f7_weekend | weekend | 893 | 248 | 823 | 234 | 593 | 723 | 400 | LOW |
| f7_approach | away | 1679 | 755 | 1686 | 757 | 1135 | 1463 | 767 | LOW |
| f7_approach | fast | 104 | 99 | 80 | 79 | 72 | 67 | 45 | LOW |
| f7_approach | slow | 1235 | 676 | 1239 | 655 | 850 | 1081 | 543 | LOW |
| f7_sweep | False | 1867 | 764 | 1913 | 768 | 1264 | 1672 | 844 | LOW |
| f7_sweep | True | 1151 | 624 | 1092 | 605 | 793 | 939 | 511 | LOW |
| f7_htf_align | 0 | 962 | 317 | 968 | 321 | 623 | 856 | 451 | LOW |
| f7_htf_align | 1 | 988 | 394 | 1004 | 396 | 759 | 837 | 396 | LOW |
| f7_htf_align | 2 | 1068 | 333 | 1033 | 330 | 675 | 918 | 508 | LOW |
| f7_funding | base | 1100 | 379 | 1092 | 379 | 534 | 1036 | 622 | LOW |
| f7_funding | high | 280 | 91 | 288 | 90 | 0 | 179 | 389 | LOW |
| f7_funding | low | 1258 | 466 | 1265 | 465 | 1080 | 1139 | 304 | LOW |
| f7_funding | neg | 380 | 184 | 360 | 176 | 443 | 257 | 40 | LOW |

## Pairs (operator-named factors; events, long / short)

### f2_conf_obj x f6_phaseA

| f2_conf_obj | f6_phaseA | long | short | flag |
|---|---|---|---|---|
| 1 | accumulation | 119 | 102 | LOW |
| 1 | distribution | 160 | 147 | LOW |
| 1 | markdown | 434 | 464 | LOW |
| 1 | markup | 590 | 580 | LOW |
| 2 | accumulation | 110 | 117 | LOW |
| 2 | distribution | 131 | 128 | LOW |
| 2 | markdown | 410 | 405 | LOW |
| 2 | markup | 548 | 558 | LOW |
| 3+ | accumulation | 51 | 59 | LOW |
| 3+ | distribution | 35 | 46 | LOW |
| 3+ | markdown | 172 | 157 | LOW |
| 3+ | markup | 258 | 242 | LOW |

### f3_armed x f4_D_align

| f3_armed | f4_D_align | long | short | flag |
|---|---|---|---|---|
| False | against | 272 | 277 | LOW |
| False | none | 1008 | 947 | LOW |
| False | with | 129 | 71 | LOW |
| True | against | 101 | 130 | LOW |
| True | none | 1185 | 1223 | LOW |
| True | with | 323 | 357 | LOW |

### f5_1h x f6_phaseA

| f5_1h | f6_phaseA | long | short | flag |
|---|---|---|---|---|
| break_lower | accumulation | 5 | 14 | LOW |
| break_lower | distribution | 2 | 8 | LOW |
| break_lower | markdown | 17 | 39 | LOW |
| break_lower | markup | 27 | 57 | LOW |
| break_upper | accumulation | 18 | 1 | LOW |
| break_upper | distribution | 20 | 5 | LOW |
| break_upper | markdown | 38 | 18 | LOW |
| break_upper | markup | 63 | 22 | LOW |
| inside | accumulation | 236 | 232 | LOW |
| inside | distribution | 284 | 290 | LOW |
| inside | markdown | 892 | 883 | LOW |
| inside | markup | 1199 | 1189 | LOW |
| reenter_lower | accumulation | 5 | 14 | LOW |
| reenter_lower | distribution | 4 | 8 | LOW |
| reenter_lower | markdown | 21 | 42 | LOW |
| reenter_lower | markup | 32 | 59 | LOW |
| reenter_upper | accumulation | 11 | 11 | LOW |
| reenter_upper | distribution | 13 | 6 | LOW |
| reenter_upper | markdown | 36 | 20 | LOW |
| reenter_upper | markup | 56 | 23 | LOW |
| walk_lower | accumulation | 1 | 4 | LOW |
| walk_lower | distribution | 0 | 3 | LOW |
| walk_lower | markdown | 3 | 20 | LOW |
| walk_lower | markup | 4 | 25 | LOW |
| walk_upper | accumulation | 4 | 2 | LOW |
| walk_upper | distribution | 3 | 1 | LOW |
| walk_upper | markdown | 9 | 4 | LOW |
| walk_upper | markup | 15 | 5 | LOW |

### f4_D_align x f5_1h

| f4_D_align | f5_1h | long | short | flag |
|---|---|---|---|---|
| against | break_lower | 4 | 10 | LOW |
| against | break_upper | 20 | 4 | LOW |
| against | inside | 332 | 373 | LOW |
| against | reenter_lower | 4 | 14 | LOW |
| against | reenter_upper | 9 | 4 | LOW |
| against | walk_lower | 1 | 2 | LOW |
| against | walk_upper | 3 | 0 | LOW |
| none | break_lower | 40 | 97 | LOW |
| none | break_upper | 104 | 34 | LOW |
| none | inside | 1884 | 1849 | LOW |
| none | reenter_lower | 47 | 96 | LOW |
| none | reenter_upper | 87 | 48 | LOW |
| none | walk_lower | 7 | 38 | LOW |
| none | walk_upper | 24 | 8 | LOW |
| with | break_lower | 7 | 11 | LOW |
| with | break_upper | 15 | 8 | LOW |
| with | inside | 395 | 372 | LOW |
| with | reenter_lower | 11 | 13 | LOW |
| with | reenter_upper | 20 | 8 | LOW |
| with | walk_lower | 0 | 12 | LOW |
| with | walk_upper | 4 | 4 | LOW |

## Stop ladder (F3): widths and cost in R per timeframe (tradeable ledger; widths only)

| side | stop tf | n | stop % p10 | p50 | p90 | cost R p10 | p50 | p90 |
|---|---|---|---|---|---|---|---|---|
| long | D | 2382 | 0.78 | 1.65 | 3.56 | 0.039 | 0.085 | 0.179 |
| long | 12h | 401 | 0.78 | 1.69 | 3.82 | 0.037 | 0.083 | 0.179 |
| long | 8h | 235 | 0.66 | 1.27 | 2.97 | 0.047 | 0.111 | 0.212 |
| short | D | 2395 | 0.79 | 1.69 | 3.72 | 0.038 | 0.083 | 0.177 |
| short | 12h | 397 | 0.68 | 1.63 | 4.00 | 0.035 | 0.086 | 0.206 |
| short | 8h | 213 | 0.67 | 1.27 | 3.57 | 0.039 | 0.110 | 0.208 |

Ladder outcome on the cooled-down ledger before the stop filter (why events have no stop):

| side | D | 12h | 8h | none | of none: some width > W_max | all valid widths < W_min |
|---|---|---|---|---|---|---|
| long | 2382 | 401 | 235 | 695 | 203 | 492 |
| short | 2395 | 397 | 213 | 697 | 153 | 544 |
