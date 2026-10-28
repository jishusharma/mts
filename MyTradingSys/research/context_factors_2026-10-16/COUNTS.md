# COUNTS: DEV decision events per factor value (counts only, no outcome read)

Built by `counts.py` from the vectorised frames (`run_dev.py vec`), DEV decision hours 2022-04-01 .. 2024-06-30 (bar open < 2024-07-01). No forward return, win/loss or exit exists in any file of this folder.

## Ledger

| step | long | short |
|---|---|---|
| DEV decision hours | 19729 | 19729 |
| at a same-side level (nearest within 1.0 x ATR14 1h) | 17802 | 17851 |
| after the 4 h same-side cooldown | 3814 | 3817 |
| with a valid ladder stop (stop_tf != none): **tradeable ledger** | **2817** | **2781** |
| distinct UTC days in the tradeable ledger | 769 | 754 |

## Power: n needed for a decisive test (research_kit)

- Outcome unit R (the PRE_REG trade: ladder stop, fixed 2 R target, all-taker cost). Per-trade sd = 1.5 R (OURS: a 1 R stop / 2 R target trade at the break-even hit rate 1/3 has sd 3 x sqrt(2/9) = 1.41 R; rounded up).
- Cross-check with FABLE_RUNS_AUDIT 1.5: per-trade sd 1.97 % at a 4 h hold. Divided by the median ladder stop (1.73 %) that is 1.14 R per trade, below 1.5 R, so 1.5 R is the conservative choice.
- Cost in R: median of the tradeable ledger = 0.14 % / stop % = **0.081 R** (all-taker); maker-in 0.09 % gives 0.052 R.
- Plausible effect of one context filter = 0.2 R (OURS: about a quarter of the best SOURCED whole-setup expectancy, +0.75 R gross, CATALOGUE T-3 quoted in FABLE_RUNS_AUDIT 3.2).
- `research_kit.power_check`: MDE = 2.8 x sd / sqrt(n) must satisfy MDE + cost <= 0.2 R  =>  **n_needed = 1242 independent units** per bucket and side. Units are UTC days (day-clustered SE), so a bucket is flagged LOW when its distinct-day count is below n_needed. The matched-baseline difference adds about sqrt(1 + 1/K) = 1.025 to the SE at K = 20 controls; ignored here (within rounding).

- Check: power_check(n=1242, sd=1.5, plausible=0.2, cost=0.081) -> mde 0.119 R, needed 0.200 R, proceed=True.

## Per factor value (tradeable ledger)

n = events, d = distinct UTC days; per-year columns are events. LOW = d < n_needed.

| factor | value | long n | long d | short n | short d | 2022 (Apr-Dec) | 2023 | 2024H1 | flag |
|---|---|---|---|---|---|---|---|---|---|
| f1_near_layer | bb4h | 151 | 128 | 163 | 138 | 115 | 136 | 63 | LOW |
| f1_near_layer | krown | 95 | 81 | 100 | 84 | 76 | 69 | 50 | LOW |
| f1_near_layer | pd_va | 817 | 478 | 805 | 498 | 571 | 727 | 324 | LOW |
| f1_near_layer | prior_dw | 214 | 168 | 193 | 146 | 158 | 162 | 87 | LOW |
| f1_near_layer | pw_va | 192 | 130 | 176 | 138 | 124 | 192 | 52 | LOW |
| f1_near_layer | round | 333 | 243 | 336 | 237 | 189 | 201 | 279 | LOW |
| f1_near_layer | session | 253 | 208 | 283 | 220 | 175 | 255 | 106 | LOW |
| f1_near_layer | vwap | 762 | 477 | 725 | 448 | 487 | 698 | 302 | LOW |
| f2_conf_obj | 1 | 1072 | 571 | 1053 | 576 | 741 | 965 | 419 | LOW |
| f2_conf_obj | 2 | 1184 | 614 | 1178 | 609 | 773 | 1040 | 549 | LOW |
| f2_conf_obj | 3+ | 561 | 366 | 550 | 366 | 381 | 435 | 295 | LOW |
| f2_touch_cat | dynamic | 1166 | 605 | 1171 | 593 | 777 | 1089 | 471 | LOW |
| f2_touch_cat | first | 232 | 199 | 194 | 172 | 165 | 177 | 84 | LOW |
| f2_touch_cat | retest | 1253 | 612 | 1286 | 619 | 844 | 1035 | 660 | LOW |
| f2_touch_cat | untested | 166 | 165 | 130 | 130 | 109 | 139 | 48 | LOW |
| f3_armed | False | 1210 | 417 | 1106 | 398 | 767 | 1021 | 528 | LOW |
| f3_armed | True | 1607 | 524 | 1675 | 510 | 1128 | 1419 | 735 | LOW |
| f3_stop_tf | 12h | 255 | 139 | 251 | 125 | 177 | 214 | 115 | LOW |
| f3_stop_tf | 8h | 130 | 95 | 103 | 70 | 76 | 94 | 63 | LOW |
| f3_stop_tf | D | 2432 | 698 | 2427 | 707 | 1642 | 2132 | 1085 | LOW |
| f4_D_align | against | 404 | 115 | 447 | 129 | 282 | 399 | 170 | LOW |
| f4_D_align | none | 1844 | 507 | 1831 | 497 | 1212 | 1573 | 890 | LOW |
| f4_D_align | with | 569 | 147 | 503 | 128 | 401 | 468 | 203 | LOW |
| f4_12h_align | against | 435 | 210 | 428 | 212 | 306 | 356 | 201 | LOW |
| f4_12h_align | none | 1822 | 634 | 1814 | 628 | 1199 | 1635 | 802 | LOW |
| f4_12h_align | with | 560 | 259 | 539 | 242 | 390 | 449 | 260 | LOW |
| f4_8h_align | against | 426 | 264 | 445 | 273 | 279 | 394 | 198 | LOW |
| f4_8h_align | none | 1824 | 699 | 1817 | 683 | 1251 | 1562 | 828 | LOW |
| f4_8h_align | with | 567 | 325 | 519 | 319 | 365 | 484 | 237 | LOW |
| f4_4h_align | against | 477 | 384 | 498 | 389 | 325 | 426 | 224 | LOW |
| f4_4h_align | none | 1785 | 710 | 1740 | 690 | 1203 | 1515 | 807 | LOW |
| f4_4h_align | with | 555 | 429 | 543 | 424 | 367 | 499 | 232 | LOW |
| f5_1h | break_lower | 45 | 44 | 122 | 114 | 56 | 80 | 31 | LOW |
| f5_1h | break_upper | 136 | 126 | 38 | 38 | 49 | 78 | 47 | LOW |
| f5_1h | inside | 2439 | 754 | 2388 | 735 | 1651 | 2087 | 1089 | LOW |
| f5_1h | reenter_lower | 43 | 43 | 137 | 125 | 66 | 78 | 36 | LOW |
| f5_1h | reenter_upper | 112 | 107 | 37 | 36 | 40 | 71 | 38 | LOW |
| f5_1h | walk_lower | 8 | 8 | 48 | 48 | 24 | 20 | 12 | LOW |
| f5_1h | walk_upper | 34 | 34 | 11 | 11 | 9 | 26 | 10 | LOW |
| f5_4h | break_lower | 35 | 31 | 136 | 108 | 59 | 80 | 32 | LOW |
| f5_4h | break_upper | 103 | 79 | 20 | 18 | 32 | 70 | 21 | LOW |
| f5_4h | inside | 2446 | 727 | 2377 | 715 | 1638 | 2075 | 1110 | LOW |
| f5_4h | reenter_lower | 66 | 66 | 109 | 100 | 68 | 66 | 41 | LOW |
| f5_4h | reenter_upper | 86 | 83 | 57 | 56 | 40 | 75 | 28 | LOW |
| f5_4h | walk_lower | 24 | 19 | 59 | 48 | 37 | 32 | 14 | LOW |
| f5_4h | walk_upper | 57 | 46 | 23 | 20 | 21 | 42 | 17 | LOW |
| f5_veto | False | 2783 | 768 | 2733 | 752 | 1867 | 2404 | 1245 | LOW |
| f5_veto | True | 34 | 34 | 48 | 48 | 28 | 36 | 18 | LOW |
| f5_conf | False | 2774 | 768 | 2744 | 751 | 1866 | 2410 | 1242 | LOW |
| f5_conf | True | 43 | 43 | 37 | 36 | 29 | 30 | 21 | LOW |
| f6_phaseA | accumulation | 267 | 73 | 256 | 69 | 111 | 263 | 149 | LOW |
| f6_phaseA | distribution | 301 | 87 | 299 | 83 | 131 | 285 | 184 | LOW |
| f6_phaseA | markdown | 933 | 256 | 955 | 259 | 1440 | 398 | 50 | LOW |
| f6_phaseA | markup | 1316 | 353 | 1271 | 343 | 213 | 1494 | 880 | LOW |
| f6_phaseB | accumulation | 325 | 91 | 307 | 89 | 431 | 201 | 0 | LOW |
| f6_phaseB | balance | 380 | 106 | 376 | 105 | 186 | 350 | 220 | LOW |
| f6_phaseB | distribution | 363 | 94 | 334 | 92 | 12 | 351 | 334 | LOW |
| f6_phaseB | markdown | 731 | 198 | 767 | 201 | 1031 | 251 | 216 | LOW |
| f6_phaseB | markup | 1018 | 280 | 997 | 267 | 235 | 1287 | 493 | LOW |
| f6_intraday | balance | 2260 | 721 | 2242 | 723 | 1520 | 1960 | 1022 | LOW |
| f6_intraday | trend_down | 173 | 113 | 366 | 212 | 234 | 211 | 94 | LOW |
| f6_intraday | trend_up | 384 | 240 | 173 | 115 | 141 | 269 | 147 | LOW |
| f7_volreg | high | 842 | 365 | 842 | 370 | 470 | 824 | 390 | LOW |
| f7_volreg | low | 1078 | 421 | 1005 | 408 | 887 | 742 | 454 | LOW |
| f7_volreg | mid | 896 | 457 | 932 | 467 | 535 | 874 | 419 | LOW |
| f7_volreg | na | 1 | 1 | 2 | 1 | 3 | 0 | 0 | LOW |
| f7_squeeze | normal | 2218 | 642 | 2137 | 623 | 1411 | 1942 | 1002 | LOW |
| f7_squeeze | squeeze | 599 | 233 | 644 | 232 | 484 | 498 | 261 | LOW |
| f7_session | asia | 1016 | 683 | 989 | 664 | 675 | 855 | 475 | LOW |
| f7_session | late | 334 | 329 | 332 | 326 | 226 | 293 | 147 | LOW |
| f7_session | london | 595 | 595 | 590 | 590 | 399 | 525 | 261 | LOW |
| f7_session | ny | 872 | 611 | 870 | 602 | 595 | 767 | 380 | LOW |
| f7_weekend | weekday | 1951 | 571 | 2024 | 568 | 1328 | 1759 | 888 | LOW |
| f7_weekend | weekend | 866 | 242 | 757 | 218 | 567 | 681 | 375 | LOW |
| f7_approach | away | 1570 | 702 | 1553 | 694 | 1033 | 1390 | 700 | LOW |
| f7_approach | fast | 81 | 78 | 76 | 73 | 56 | 53 | 48 | LOW |
| f7_approach | slow | 1166 | 642 | 1152 | 623 | 806 | 997 | 515 | LOW |
| f7_sweep | False | 1787 | 721 | 1772 | 713 | 1195 | 1586 | 778 | LOW |
| f7_sweep | True | 1030 | 584 | 1009 | 574 | 700 | 854 | 485 | LOW |
| f7_htf_align | 0 | 853 | 288 | 842 | 292 | 532 | 761 | 402 | LOW |
| f7_htf_align | 1 | 905 | 363 | 913 | 355 | 694 | 766 | 358 | LOW |
| f7_htf_align | 2 | 1059 | 333 | 1026 | 323 | 669 | 913 | 503 | LOW |
| f7_funding | base | 1035 | 354 | 995 | 354 | 488 | 943 | 599 | LOW |
| f7_funding | high | 257 | 89 | 263 | 80 | 0 | 170 | 350 | LOW |
| f7_funding | low | 1163 | 433 | 1176 | 435 | 984 | 1074 | 281 | LOW |
| f7_funding | neg | 362 | 173 | 347 | 166 | 423 | 253 | 33 | LOW |

## Pairs (operator-named factors; events, long / short)

### f2_conf_obj x f6_phaseA

| f2_conf_obj | f6_phaseA | long | short | flag |
|---|---|---|---|---|
| 1 | accumulation | 101 | 79 | LOW |
| 1 | distribution | 132 | 128 | LOW |
| 1 | markdown | 342 | 397 | LOW |
| 1 | markup | 497 | 449 | LOW |
| 2 | accumulation | 118 | 125 | LOW |
| 2 | distribution | 136 | 121 | LOW |
| 2 | markdown | 393 | 383 | LOW |
| 2 | markup | 537 | 549 | LOW |
| 3+ | accumulation | 48 | 52 | LOW |
| 3+ | distribution | 33 | 50 | LOW |
| 3+ | markdown | 198 | 175 | LOW |
| 3+ | markup | 282 | 273 | LOW |

### f3_armed x f4_D_align

| f3_armed | f4_D_align | long | short | flag |
|---|---|---|---|---|
| False | against | 299 | 312 | LOW |
| False | none | 782 | 718 | LOW |
| False | with | 129 | 76 | LOW |
| True | against | 105 | 135 | LOW |
| True | none | 1062 | 1113 | LOW |
| True | with | 440 | 427 | LOW |

### f5_1h x f6_phaseA

| f5_1h | f6_phaseA | long | short | flag |
|---|---|---|---|---|
| break_lower | accumulation | 4 | 12 | LOW |
| break_lower | distribution | 1 | 11 | LOW |
| break_lower | markdown | 18 | 41 | LOW |
| break_lower | markup | 22 | 58 | LOW |
| break_upper | accumulation | 19 | 4 | LOW |
| break_upper | distribution | 19 | 1 | LOW |
| break_upper | markdown | 40 | 9 | LOW |
| break_upper | markup | 58 | 24 | LOW |
| inside | accumulation | 225 | 216 | LOW |
| inside | distribution | 265 | 263 | LOW |
| inside | markdown | 813 | 826 | LOW |
| inside | markup | 1136 | 1083 | LOW |
| reenter_lower | accumulation | 4 | 16 | LOW |
| reenter_lower | distribution | 1 | 16 | LOW |
| reenter_lower | markdown | 14 | 42 | LOW |
| reenter_lower | markup | 24 | 63 | LOW |
| reenter_upper | accumulation | 8 | 5 | LOW |
| reenter_upper | distribution | 12 | 5 | LOW |
| reenter_upper | markdown | 35 | 9 | LOW |
| reenter_upper | markup | 57 | 18 | LOW |
| walk_lower | accumulation | 2 | 3 | LOW |
| walk_lower | distribution | 0 | 2 | LOW |
| walk_lower | markdown | 2 | 23 | LOW |
| walk_lower | markup | 4 | 20 | LOW |
| walk_upper | accumulation | 5 | 0 | LOW |
| walk_upper | distribution | 3 | 1 | LOW |
| walk_upper | markdown | 11 | 5 | LOW |
| walk_upper | markup | 15 | 5 | LOW |

### f4_D_align x f5_1h

| f4_D_align | f5_1h | long | short | flag |
|---|---|---|---|---|
| against | break_lower | 1 | 18 | LOW |
| against | break_upper | 28 | 2 | LOW |
| against | inside | 352 | 395 | LOW |
| against | reenter_lower | 2 | 23 | LOW |
| against | reenter_upper | 17 | 5 | LOW |
| against | walk_lower | 0 | 4 | LOW |
| against | walk_upper | 4 | 0 | LOW |
| none | break_lower | 31 | 88 | LOW |
| none | break_upper | 83 | 31 | LOW |
| none | inside | 1598 | 1560 | LOW |
| none | reenter_lower | 29 | 95 | LOW |
| none | reenter_upper | 74 | 21 | LOW |
| none | walk_lower | 6 | 32 | LOW |
| none | walk_upper | 23 | 4 | LOW |
| with | break_lower | 13 | 16 | LOW |
| with | break_upper | 25 | 5 | LOW |
| with | inside | 489 | 433 | LOW |
| with | reenter_lower | 12 | 19 | LOW |
| with | reenter_upper | 21 | 11 | LOW |
| with | walk_lower | 2 | 12 | LOW |
| with | walk_upper | 7 | 7 | LOW |

## Stop ladder (F3): widths and cost in R per timeframe (tradeable ledger; widths only)

| side | stop tf | n | stop % p10 | p50 | p90 | cost R p10 | p50 | p90 |
|---|---|---|---|---|---|---|---|---|
| long | D | 2432 | 0.78 | 1.66 | 3.57 | 0.039 | 0.085 | 0.180 |
| long | 12h | 255 | 0.98 | 2.06 | 3.96 | 0.035 | 0.068 | 0.143 |
| long | 8h | 130 | 0.99 | 2.20 | 3.79 | 0.037 | 0.064 | 0.141 |
| short | D | 2427 | 0.79 | 1.69 | 3.75 | 0.037 | 0.083 | 0.178 |
| short | 12h | 251 | 0.78 | 2.10 | 4.51 | 0.031 | 0.067 | 0.180 |
| short | 8h | 103 | 1.00 | 2.16 | 4.04 | 0.035 | 0.065 | 0.141 |

Ladder outcome on the cooled-down ledger before the stop filter (why events have no stop):

| side | D | 12h | 8h | none | of none: some width > W_max | all valid widths < W_min |
|---|---|---|---|---|---|---|
| long | 2432 | 255 | 130 | 997 | 214 | 535 |
| short | 2427 | 251 | 103 | 1036 | 170 | 619 |
