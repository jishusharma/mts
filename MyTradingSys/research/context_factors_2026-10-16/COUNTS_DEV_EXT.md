# COUNTS_DEV_EXT: DEV + DEV_EXT per-factor event counts (counts only, no outcome read)

Built by `count_ext.py` (frames: `context_asof.context_frame`, unedited; ledger rule of `counts.py`). Segments: DEV_EXT = bar open 2020-01-01 .. 2021-12-31 (decisions from 2020-04-01), DEV = 2022-01-01 .. 2024-06-30 (decisions from 2022-01-01 now, because DEV_EXT supplies the warm-up). VALIDATION and HOLDOUT are never loaded (`dev_ext.assert_dev_stage`).

- Decision days: 1553 total, of which 641 in DEV_EXT. Tradeable ledger: long 5516, short 5258.
- Median cost in R of the tradeable ledger: 0.069 R.
- n_needed (distinct UTC days per bucket and side, plausible 0.2 R, sd 1.5 R): **1031** at m = 1; **2151** at Holm m = 37 (PRE_REG s.4: 1,242 and 2,064 on DEV only).
- Factors with at least one POWERED value at m = 37: **none**.
- Factors with at least one POWERED value at m = 1 only: f2_conf_obj, f2_touch_cat, f3_armed, f3_stop_tf, f4_12h_align, f4_8h_align, f4_4h_align, f5_1h, f5_4h, f5_veto, f5_conf, f6_intraday, f7_squeeze, f7_session, f7_weekend, f7_approach, f7_sweep.

| factor | value | long n | long d | (DEV / EXT) | short n | short d | (DEV / EXT) | m=1 | m=37 |
|---|---|---|---|---|---|---|---|---|---|
| f1_near_layer | bb4h | 288 | 230 | 136 / 94 | 282 | 243 | 152 / 91 | low | low |
| f1_near_layer | krown | 194 | 163 | 91 / 72 | 181 | 156 | 94 / 62 | low | low |
| f1_near_layer | pd_va | 1552 | 917 | 532 / 385 | 1480 | 921 | 548 / 373 | low | low |
| f1_near_layer | prior_dw | 454 | 347 | 186 / 161 | 382 | 295 | 173 / 122 | low | low |
| f1_near_layer | pw_va | 356 | 256 | 142 / 114 | 330 | 249 | 145 / 104 | low | low |
| f1_near_layer | round | 801 | 548 | 287 / 261 | 807 | 530 | 288 / 242 | low | low |
| f1_near_layer | session | 477 | 394 | 231 / 163 | 532 | 411 | 248 / 163 | low | low |
| f1_near_layer | vwap | 1394 | 899 | 531 / 368 | 1264 | 811 | 501 / 310 | low | low |
| f2_conf_obj | 1 | 1996 | 1091 | 634 / 457 | 1874 | 1050 | 636 / 414 | POWERED | low |
| f2_conf_obj | 2 | 2328 | 1195 | 686 / 509 | 2232 | 1142 | 680 / 462 | POWERED | low |
| f2_conf_obj | 3+ | 1192 | 744 | 406 / 338 | 1152 | 726 | 413 / 313 | low | low |
| f2_touch_cat | dynamic | 2159 | 1145 | 672 / 473 | 2078 | 1100 | 663 / 437 | POWERED | low |
| f2_touch_cat | first | 456 | 392 | 223 / 169 | 370 | 324 | 192 / 132 | low | low |
| f2_touch_cat | retest | 2595 | 1235 | 687 / 548 | 2538 | 1189 | 695 / 494 | POWERED | low |
| f2_touch_cat | untested | 306 | 305 | 189 / 116 | 272 | 272 | 146 / 126 | low | low |
| f3_armed | False | 2215 | 788 | 468 / 320 | 2165 | 799 | 446 / 353 | low | low |
| f3_armed | True | 3301 | 1031 | 582 / 449 | 3093 | 949 | 569 / 380 | POWERED | low |
| f3_stop_tf | 12h | 634 | 310 | 158 / 152 | 470 | 239 | 142 / 97 | low | low |
| f3_stop_tf | 8h | 254 | 181 | 107 / 74 | 177 | 122 | 78 / 44 | low | low |
| f3_stop_tf | D | 4628 | 1340 | 779 / 561 | 4611 | 1348 | 787 / 561 | POWERED | low |
| f4_D_align | against | 787 | 227 | 128 / 99 | 900 | 263 | 143 / 120 | low | low |
| f4_D_align | none | 3559 | 958 | 566 / 392 | 3410 | 933 | 557 / 376 | low | low |
| f4_D_align | with | 1170 | 296 | 162 / 134 | 948 | 241 | 141 / 100 | low | low |
| f4_12h_align | against | 812 | 397 | 236 / 161 | 872 | 427 | 246 / 181 | low | low |
| f4_12h_align | none | 3558 | 1228 | 708 / 520 | 3400 | 1180 | 698 / 482 | POWERED | low |
| f4_12h_align | with | 1146 | 524 | 294 / 230 | 986 | 455 | 272 / 183 | low | low |
| f4_8h_align | against | 857 | 518 | 295 / 223 | 900 | 549 | 308 / 241 | low | low |
| f4_8h_align | none | 3502 | 1325 | 779 / 546 | 3374 | 1277 | 762 / 515 | POWERED | low |
| f4_8h_align | with | 1157 | 666 | 366 / 300 | 984 | 593 | 354 / 239 | low | low |
| f4_4h_align | against | 931 | 748 | 430 / 318 | 956 | 748 | 430 / 318 | low | low |
| f4_4h_align | none | 3446 | 1387 | 794 / 593 | 3273 | 1317 | 774 / 543 | POWERED | low |
| f4_4h_align | with | 1139 | 857 | 477 / 380 | 1029 | 808 | 472 / 336 | low | low |
| f5_1h | break_lower | 113 | 109 | 49 / 60 | 252 | 239 | 129 / 110 | low | low |
| f5_1h | break_upper | 251 | 238 | 136 / 102 | 80 | 77 | 42 / 35 | low | low |
| f5_1h | inside | 4770 | 1455 | 839 / 616 | 4516 | 1410 | 821 / 589 | POWERED | low |
| f5_1h | reenter_lower | 84 | 82 | 45 / 37 | 231 | 211 | 132 / 79 | low | low |
| f5_1h | reenter_upper | 219 | 208 | 124 / 84 | 77 | 75 | 44 / 31 | low | low |
| f5_1h | walk_lower | 17 | 17 | 11 / 6 | 87 | 86 | 55 / 31 | low | low |
| f5_1h | walk_upper | 62 | 62 | 36 / 26 | 15 | 15 | 11 / 4 | low | low |
| f5_4h | break_lower | 68 | 60 | 37 / 23 | 239 | 187 | 119 / 68 | low | low |
| f5_4h | break_upper | 225 | 172 | 89 / 83 | 43 | 38 | 20 / 18 | low | low |
| f5_4h | inside | 4752 | 1411 | 810 / 601 | 4552 | 1373 | 800 / 573 | POWERED | low |
| f5_4h | reenter_lower | 120 | 119 | 74 / 45 | 195 | 182 | 109 / 73 | low | low |
| f5_4h | reenter_upper | 200 | 191 | 96 / 95 | 107 | 106 | 64 / 42 | low | low |
| f5_4h | walk_lower | 37 | 29 | 23 / 6 | 71 | 58 | 51 / 7 | low | low |
| f5_4h | walk_upper | 114 | 90 | 52 / 38 | 51 | 44 | 23 / 21 | low | low |
| f5_veto | False | 5454 | 1479 | 854 / 625 | 5171 | 1434 | 839 / 595 | POWERED | low |
| f5_veto | True | 62 | 62 | 36 / 26 | 87 | 86 | 55 / 31 | low | low |
| f5_conf | False | 5432 | 1480 | 855 / 625 | 5181 | 1433 | 837 / 596 | POWERED | low |
| f5_conf | True | 84 | 82 | 45 / 37 | 77 | 75 | 44 / 31 | low | low |
| f6_phaseA | accumulation | 570 | 154 | 73 / 81 | 529 | 145 | 69 / 76 | low | low |
| f6_phaseA | distribution | 484 | 133 | 94 / 39 | 455 | 128 | 89 / 39 | low | low |
| f6_phaseA | markdown | 1580 | 429 | 332 / 97 | 1630 | 434 | 337 / 97 | low | low |
| f6_phaseA | markup | 2882 | 765 | 357 / 408 | 2644 | 730 | 346 / 384 | low | low |
| f6_phaseB | accumulation | 477 | 130 | 115 / 15 | 468 | 130 | 115 / 15 | low | low |
| f6_phaseB | balance | 573 | 160 | 118 / 42 | 559 | 157 | 116 / 41 | low | low |
| f6_phaseB | distribution | 768 | 197 | 94 / 103 | 683 | 190 | 92 / 98 | low | low |
| f6_phaseB | markdown | 1371 | 367 | 236 / 131 | 1405 | 368 | 240 / 128 | low | low |
| f6_phaseB | markup | 2327 | 627 | 293 / 334 | 2143 | 592 | 278 / 314 | low | low |
| f6_intraday | balance | 4417 | 1394 | 798 / 596 | 4272 | 1365 | 803 / 562 | POWERED | low |
| f6_intraday | trend_down | 289 | 191 | 122 / 69 | 647 | 375 | 234 / 141 | low | low |
| f6_intraday | trend_up | 810 | 481 | 263 / 218 | 339 | 230 | 128 / 102 | low | low |
| f7_volreg | high | 1663 | 681 | 411 / 270 | 1672 | 690 | 417 / 273 | low | low |
| f7_volreg | low | 2085 | 786 | 472 / 314 | 1896 | 748 | 455 / 293 | low | low |
| f7_volreg | mid | 1768 | 848 | 516 / 332 | 1690 | 832 | 517 / 315 | low | low |
| f7_squeeze | normal | 4273 | 1227 | 712 / 515 | 4006 | 1172 | 691 / 481 | POWERED | low |
| f7_squeeze | squeeze | 1243 | 465 | 261 / 204 | 1252 | 460 | 259 / 201 | low | low |
| f7_session | asia | 1992 | 1332 | 759 / 573 | 1876 | 1264 | 739 / 525 | POWERED | low |
| f7_session | late | 663 | 650 | 369 / 281 | 621 | 612 | 363 / 249 | low | low |
| f7_session | london | 1164 | 1164 | 665 / 499 | 1116 | 1116 | 662 / 454 | POWERED | low |
| f7_session | ny | 1697 | 1177 | 681 / 496 | 1645 | 1114 | 671 / 443 | POWERED | low |
| f7_weekend | weekday | 3843 | 1098 | 637 / 461 | 3794 | 1077 | 632 / 445 | POWERED | low |
| f7_weekend | weekend | 1673 | 462 | 271 / 191 | 1464 | 427 | 247 / 180 | low | low |
| f7_approach | away | 3056 | 1367 | 784 / 583 | 2888 | 1309 | 776 / 533 | POWERED | low |
| f7_approach | fast | 168 | 162 | 90 / 72 | 162 | 154 | 87 / 67 | low | low |
| f7_approach | slow | 2292 | 1233 | 715 / 518 | 2208 | 1191 | 699 / 492 | POWERED | low |
| f7_sweep | False | 3457 | 1390 | 803 / 587 | 3328 | 1340 | 796 / 544 | POWERED | low |
| f7_sweep | True | 2059 | 1148 | 651 / 497 | 1930 | 1089 | 639 / 450 | POWERED | low |
| f7_htf_align | 0 | 1500 | 502 | 328 / 174 | 1738 | 609 | 314 / 295 | low | low |
| f7_htf_align | 1 | 1750 | 677 | 401 / 276 | 1685 | 660 | 395 / 265 | low | low |
| f7_htf_align | 2 | 2266 | 688 | 360 / 328 | 1835 | 557 | 369 / 188 | low | low |
| f7_funding | base | 2328 | 777 | 406 / 371 | 2218 | 769 | 406 / 363 | low | low |
| f7_funding | high | 1048 | 341 | 89 / 252 | 965 | 309 | 80 / 229 | low | low |
| f7_funding | low | 1459 | 588 | 484 / 104 | 1450 | 577 | 484 / 93 | low | low |
| f7_funding | neg | 681 | 318 | 212 / 106 | 625 | 292 | 199 / 93 | low | low |
