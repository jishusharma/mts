# V1 DEV RESULTS - BTC volume event study (run V1-2026-10-09, DEV 2020-01-01 .. 2024-06-30)

Definitions and decision rule: PRE_REG_VOLUME_2026-10-09.md (frozen in commit ec18096 before any outcome). Net = sign*fwd - 14 bps - sign*funding in (entry, exit]. Excess = sign*(mean fwd | event - mean fwd | all bars), BTC drift cancels. p_adj = White Reality-Check max-T over all 216 trials of the timeframe (both orientations). Triage PASS needs n >= min, net mean > 0 with block-bootstrap CI lower bound > 0, p_adj < 0.10, excess > 0.

## 1d: 1472 bars in range, 216 trials (96 live, 120 INSUFFICIENT-N), **0 pass triage**

Analytic minimum detectable excess (80 pct power, one-sided .05) per event size n at each horizon: h=3: n=50 -> 195 bp, n=200 -> 98 bp, n=1000 -> 44 bp; h=10: n=50 -> 373 bp, n=200 -> 187 bp, n=1000 -> 83 bp; h=20: n=50 -> 550 bp, n=200 -> 275 bp, n=1000 -> 123 bp
(sd of the h-bar forward return: h=3: 555 bp, h=10: 1062 bp, h=20: 1565 bp)

### 1d: continuation-oriented excess return per event and horizon (cell: n, continuation excess bp with its RC p_adj, and the RC p_adj of the reversal orientation)

| event | dir | h=3 | h=10 | h=20 |
|---|---|---|---|---|
| SP2_UP | +1 | n=51, cont +17 bp (p 1.00) / rev p 1.00 | n=51, cont +250 bp (p 0.99) / rev p 1.00 | n=51, cont +505 bp (p 0.63) / rev p 1.00 |
| SP2_DN | -1 | n=57, cont +16 bp (p 1.00) / rev p 1.00 | n=57, cont -47 bp (p 1.00) / rev p 1.00 | n=57, cont +104 bp (p 1.00) / rev p 1.00 |
| SP3_UP | +1 | n=14 INSUFF | n=14 INSUFF | n=14 INSUFF |
| SP3_DN | -1 | n=18 INSUFF | n=18 INSUFF | n=18 INSUFF |
| BCLX | +1 | n=5 INSUFF | n=5 INSUFF | n=5 INSUFF |
| SCLX | -1 | n=6 INSUFF | n=6 INSUFF | n=6 INSUFF |
| BAWAY_UP | +1 | n=15 INSUFF | n=15 INSUFF | n=15 INSUFF |
| BAWAY_DN | -1 | n=8 INSUFF | n=8 INSUFF | n=8 INSUFF |
| ABS_LOW | -1 | n=7 INSUFF | n=7 INSUFF | n=7 INSUFF |
| ABS_HIGH | +1 | n=0 INSUFF | n=0 INSUFF | n=0 INSUFF |
| NODEM_HIGH | +1 | n=26 INSUFF | n=26 INSUFF | n=26 INSUFF |
| NOSUP_LOW | -1 | n=3 INSUFF | n=3 INSUFF | n=3 INSUFF |
| DBUY | +1 | n=54, cont -55 bp (p 1.00) / rev p 1.00 | n=54, cont -30 bp (p 1.00) / rev p 1.00 | n=54, cont -8 bp (p 1.00) / rev p 1.00 |
| DSELL | -1 | n=32, cont +84 bp (p 1.00) / rev p 1.00 | n=32, cont +275 bp (p 0.79) / rev p 1.00 | n=32, cont +154 bp (p 1.00) / rev p 1.00 |
| CVDDIV_BEAR | +1 | n=157, cont +119 bp (p 0.63) / rev p 1.00 | n=157, cont +186 bp (p 1.00) / rev p 1.00 | n=157, cont +229 bp (p 1.00) / rev p 1.00 |
| CVDDIV_BULL | -1 | n=34, cont -130 bp (p 1.00) / rev p 1.00 | n=34, cont -45 bp (p 1.00) / rev p 1.00 | n=34, cont +181 bp (p 1.00) / rev p 1.00 |
| OBVDIV_BEAR | +1 | n=84, cont +76 bp (p 1.00) / rev p 1.00 | n=84, cont +117 bp (p 1.00) / rev p 1.00 | n=84, cont +24 bp (p 1.00) / rev p 1.00 |
| OBVDIV_BULL | -1 | n=39, cont -22 bp (p 1.00) / rev p 1.00 | n=39, cont +74 bp (p 1.00) / rev p 1.00 | n=39, cont +299 bp (p 1.00) / rev p 1.00 |
| BBSQ_UP_V | +1 | n=18 INSUFF | n=18 INSUFF | n=18 INSUFF |
| BBSQ_UP_N | +1 | n=57, cont +40 bp (p 1.00) / rev p 1.00 | n=57, cont -72 bp (p 1.00) / rev p 1.00 | n=57, cont -351 bp (p 1.00) / rev p 1.00 |
| BBSQ_DN_V | -1 | n=21 INSUFF | n=21 INSUFF | n=21 INSUFF |
| BBSQ_DN_N | -1 | n=37, cont -45 bp (p 1.00) / rev p 1.00 | n=37, cont -194 bp (p 1.00) / rev p 1.00 | n=37, cont +155 bp (p 1.00) / rev p 1.00 |
| BBALL_UP | +1 | n=181, cont +83 bp (p 0.96) / rev p 1.00 | n=181, cont +211 bp (p 0.87) / rev p 1.00 | n=181, cont +297 bp (p 0.96) / rev p 1.00 |
| BBALL_DN | -1 | n=99, cont +23 bp (p 1.00) / rev p 1.00 | n=99, cont -43 bp (p 1.00) / rev p 1.00 | n=99, cont +131 bp (p 1.00) / rev p 1.00 |
| DON_UP_V | +1 | n=43, cont +140 bp (p 0.87) / rev p 1.00 | n=43, cont +300 bp (p 0.42) / rev p 1.00 | n=43, cont +546 bp (p 0.37) / rev p 1.00 |
| DON_UP_N | +1 | n=55, cont +185 bp (p 0.91) / rev p 1.00 | n=55, cont +200 bp (p 1.00) / rev p 1.00 | n=55, cont +308 bp (p 1.00) / rev p 1.00 |
| DON_DN_V | -1 | n=21 INSUFF | n=21 INSUFF | n=21 INSUFF |
| DON_DN_N | -1 | n=19 INSUFF | n=19 INSUFF | n=19 INSUFF |
| DRY_UP | +1 | n=4 INSUFF | n=4 INSUFF | n=4 INSUFF |
| DRY_DN | -1 | n=2 INSUFF | n=2 INSUFF | n=2 INSUFF |
| R60U_V | +1 | n=12 INSUFF | n=12 INSUFF | n=12 INSUFF |
| R60U_N | +1 | n=56, cont -4 bp (p 1.00) / rev p 1.00 | n=56, cont -18 bp (p 1.00) / rev p 1.00 | n=56, cont -70 bp (p 1.00) / rev p 1.00 |
| R40D_V | -1 | n=8 INSUFF | n=8 INSUFF | n=8 INSUFF |
| R40D_N | -1 | n=42, cont -53 bp (p 1.00) / rev p 1.00 | n=42, cont +59 bp (p 1.00) / rev p 1.00 | n=42, cont +281 bp (p 1.00) / rev p 1.00 |
| R40RECL_V | +1 | n=11 INSUFF | n=11 INSUFF | n=11 INSUFF |
| R60REJ_V | -1 | n=16 INSUFF | n=16 INSUFF | n=16 INSUFF |

### 1d: 12 best trials by RC p_adj

| event | h | orient | n | gross bp | net bp [95% CI] | win | excess bp | t | p_raw | p_adj | q_BH | MDE bp | triage |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DON_UP_V | 20 | cont | 43 | +805 | +663 [+186, +1125] | 65% | +546 | 2.44 | 0.014 | 0.371 | 1.00 | 593 | FAIL |
| DON_UP_V | 10 | cont | 43 | +431 | +346 [+64, +574] | 74% | +300 | 2.37 | 0.014 | 0.424 | 1.00 | 403 | FAIL |
| SP2_UP | 20 | cont | 51 | +763 | +667 [+113, +1185] | 67% | +505 | 2.11 | 0.018 | 0.627 | 1.00 | 545 | FAIL |
| CVDDIV_BEAR | 3 | cont | 157 | +159 | +115 [-5, +235] | 54% | +119 | 2.10 | 0.019 | 0.627 | 1.00 | 110 | FAIL |
| DSELL | 10 | cont | 32 | +144 | +174 [-54, +459] | 56% | +275 | 1.89 | 0.032 | 0.792 | 1.00 | 467 | FAIL |
| BBALL_UP | 10 | cont | 181 | +342 | +261 [-65, +533] | 64% | +211 | 1.79 | 0.033 | 0.865 | 1.00 | 196 | FAIL |
| DON_UP_V | 3 | cont | 43 | +179 | +139 [-25, +291] | 60% | +140 | 1.78 | 0.044 | 0.868 | 1.00 | 211 | FAIL |
| DON_UP_N | 3 | cont | 55 | +225 | +185 [-49, +408] | 60% | +185 | 1.67 | 0.042 | 0.912 | 1.00 | 186 | FAIL |
| BBALL_UP | 3 | cont | 181 | +123 | +86 [-49, +203] | 55% | +83 | 1.52 | 0.068 | 0.964 | 1.00 | 103 | FAIL |
| BBALL_UP | 20 | cont | 181 | +556 | +418 [-131, +862] | 60% | +297 | 1.51 | 0.060 | 0.964 | 1.00 | 289 | FAIL |
| SP2_UP | 10 | cont | 51 | +381 | +327 [-131, +716] | 63% | +250 | 1.37 | 0.084 | 0.989 | 1.00 | 370 | FAIL |
| CVDDIV_BEAR | 10 | cont | 157 | +317 | +215 [-136, +546] | 57% | +186 | 1.27 | 0.100 | 0.996 | 1.00 | 211 | FAIL |

### 1d: registered contrasts at h=10 (does volume add information? time hypotheses)

| id | what | nA | nB | mean A bp | mean B bp | diff bp | 95% CI bp | p | q_BH (C-family) | q (TH-family) | CI excludes 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | squeeze up-break: vol-confirmed minus not | 18 | 57 | +420 | +59 | +361 | [-266, +947] | 0.225 | 0.360 | - | no |
| C2 | squeeze down-break (short oriented) | 21 | 37 | +137 | -325 | +462 | [-214, +1180] | 0.185 | 0.360 | - | no |
| C3 | Donchian up: vol-confirmed minus not | 43 | 55 | +431 | +331 | +100 | [-346, +580] | 0.660 | 0.660 | - | no |
| C4 | Donchian down (short oriented) | 21 | 19 | +254 | -692 | +946 | [+66, +2003] | 0.055 | 0.220 | - | yes |
| C5 | RSI up-cross 60: vol minus not | 12 | 56 | +291 | +113 | +178 | [-412, +785] | 0.507 | 0.641 | - | no |
| C6 | RSI down-cross 40 (short oriented) | 8 | 42 | +256 | -72 | +329 | [-612, +1806] | 0.561 | 0.641 | - | no |
| C7 | SP3 defined with RVadj minus defined with plain RV (overlapping sets; signed cont return) | 32 | 20 | +54 | +491 | -436 | [-848, -1] | 0.045 | 0.220 | - | yes |
| C8/TH2 | SP3 weekend minus weekday (signed cont return) | 17 | 15 | -134 | +267 | -400 | [-891, +236] | 0.144 | 0.360 | 0.144 | no |

## 4h: 9665 bars in range, 216 trials (156 live, 60 INSUFFICIENT-N), **1 pass triage**

Analytic minimum detectable excess (80 pct power, one-sided .05) per event size n at each horizon: h=6: n=50 -> 122 bp, n=200 -> 61 bp, n=1000 -> 27 bp; h=18: n=50 -> 208 bp, n=200 -> 104 bp, n=1000 -> 46 bp; h=42: n=50 -> 327 bp, n=200 -> 164 bp, n=1000 -> 73 bp
(sd of the h-bar forward return: h=6: 346 bp, h=18: 591 bp, h=42: 930 bp)

### 4h: continuation-oriented excess return per event and horizon (cell: n, continuation excess bp with its RC p_adj, and the RC p_adj of the reversal orientation)

| event | dir | h=6 | h=18 | h=42 |
|---|---|---|---|---|
| SP2_UP | +1 | n=585, cont +24 bp (p 1.00) / rev p 1.00 | n=585, cont +25 bp (p 1.00) / rev p 1.00 | n=585, cont +120 bp (p 0.83) / rev p 1.00 |
| SP2_DN | -1 | n=624, cont -0 bp (p 1.00) / rev p 1.00 | n=624, cont +13 bp (p 1.00) / rev p 1.00 | n=624, cont -28 bp (p 1.00) / rev p 1.00 |
| SP3_UP | +1 | n=219, cont +41 bp (p 1.00) / rev p 1.00 | n=219, cont +40 bp (p 1.00) / rev p 1.00 | n=219, cont +247 bp (p 0.37) / rev p 1.00 |
| SP3_DN | -1 | n=239, cont -5 bp (p 1.00) / rev p 1.00 | n=239, cont +19 bp (p 1.00) / rev p 1.00 | n=239, cont +13 bp (p 1.00) / rev p 1.00 |
| BCLX | +1 | n=82 INSUFF | n=82 INSUFF | n=82 INSUFF |
| SCLX | -1 | n=67 INSUFF | n=67 INSUFF | n=67 INSUFF |
| BAWAY_UP | +1 | n=181, cont +51 bp (p 0.99) / rev p 1.00 | n=181, cont +67 bp (p 1.00) / rev p 1.00 | n=181, cont +192 bp (p 0.58) / rev p 1.00 |
| BAWAY_DN | -1 | n=145, cont +39 bp (p 1.00) / rev p 1.00 | n=145, cont +104 bp (p 1.00) / rev p 1.00 | n=145, cont +134 bp (p 1.00) / rev p 1.00 |
| ABS_LOW | -1 | n=41 INSUFF | n=41 INSUFF | n=41 INSUFF |
| ABS_HIGH | +1 | n=36 INSUFF | n=36 INSUFF | n=36 INSUFF |
| NODEM_HIGH | +1 | n=55 INSUFF | n=55 INSUFF | n=55 INSUFF |
| NOSUP_LOW | -1 | n=23 INSUFF | n=23 INSUFF | n=23 INSUFF |
| DBUY | +1 | n=284, cont +8 bp (p 1.00) / rev p 1.00 | n=284, cont +14 bp (p 1.00) / rev p 1.00 | n=284, cont +54 bp (p 1.00) / rev p 1.00 |
| DSELL | -1 | n=254, cont +12 bp (p 1.00) / rev p 1.00 | n=254, cont +46 bp (p 1.00) / rev p 1.00 | n=254, cont +44 bp (p 1.00) / rev p 1.00 |
| CVDDIV_BEAR | +1 | n=555, cont -18 bp (p 1.00) / rev p 1.00 | n=555, cont -1 bp (p 1.00) / rev p 1.00 | n=555, cont -19 bp (p 1.00) / rev p 1.00 |
| CVDDIV_BULL | -1 | n=215, cont -70 bp (p 1.00) / rev p 0.98 | n=215, cont -86 bp (p 1.00) / rev p 1.00 | n=215, cont -125 bp (p 1.00) / rev p 1.00 |
| OBVDIV_BEAR | +1 | n=379, cont +17 bp (p 1.00) / rev p 1.00 | n=379, cont +19 bp (p 1.00) / rev p 1.00 | n=379, cont +43 bp (p 1.00) / rev p 1.00 |
| OBVDIV_BULL | -1 | n=254, cont +8 bp (p 1.00) / rev p 1.00 | n=254, cont +25 bp (p 1.00) / rev p 1.00 | n=254, cont +40 bp (p 1.00) / rev p 1.00 |
| BBSQ_UP_V | +1 | n=201, cont +57 bp (p 0.98) / rev p 1.00 | n=201, cont +71 bp (p 1.00) / rev p 1.00 | n=201, cont +49 bp (p 1.00) / rev p 1.00 |
| BBSQ_UP_N | +1 | n=314, cont -28 bp (p 1.00) / rev p 1.00 | n=314, cont -29 bp (p 1.00) / rev p 1.00 | n=314, cont -135 bp (p 1.00) / rev p 1.00 |
| BBSQ_DN_V | -1 | n=198, cont -13 bp (p 1.00) / rev p 1.00 | n=198, cont -17 bp (p 1.00) / rev p 1.00 | n=198, cont -53 bp (p 1.00) / rev p 1.00 |
| BBSQ_DN_N | -1 | n=266, cont -5 bp (p 1.00) / rev p 1.00 | n=266, cont +26 bp (p 1.00) / rev p 1.00 | n=266, cont -16 bp (p 1.00) / rev p 1.00 |
| BBALL_UP | +1 | n=1027, cont +16 bp (p 1.00) / rev p 1.00 | n=1027, cont +40 bp (p 1.00) / rev p 1.00 | n=1027, cont +55 bp (p 1.00) / rev p 1.00 |
| BBALL_DN | -1 | n=838, cont +21 bp (p 1.00) / rev p 1.00 | n=838, cont +65 bp (p 1.00) / rev p 1.00 | n=838, cont +97 bp (p 1.00) / rev p 1.00 |
| DON_UP_V | +1 | n=314, cont +70 bp (p 0.19) / rev p 1.00 | n=314, cont +90 bp (p 0.75) / rev p 1.00 | n=314, cont +164 bp (p 0.42) / rev p 1.00 |
| DON_UP_N | +1 | n=153, cont -10 bp (p 1.00) / rev p 1.00 | n=153, cont -30 bp (p 1.00) / rev p 1.00 | n=153, cont -63 bp (p 1.00) / rev p 1.00 |
| DON_DN_V | -1 | n=239, cont +31 bp (p 1.00) / rev p 1.00 | n=239, cont +84 bp (p 1.00) / rev p 1.00 | n=239, cont +110 bp (p 1.00) / rev p 1.00 |
| DON_DN_N | -1 | n=70 INSUFF | n=70 INSUFF | n=70 INSUFF |
| DRY_UP | +1 | n=36 INSUFF | n=36 INSUFF | n=36 INSUFF |
| DRY_DN | -1 | n=34 INSUFF | n=34 INSUFF | n=34 INSUFF |
| R60U_V | +1 | n=153, cont +37 bp (p 1.00) / rev p 1.00 | n=153, cont +46 bp (p 1.00) / rev p 1.00 | n=153, cont -2 bp (p 1.00) / rev p 1.00 |
| R60U_N | +1 | n=230, cont -19 bp (p 1.00) / rev p 1.00 | n=230, cont -48 bp (p 1.00) / rev p 1.00 | n=230, cont -25 bp (p 1.00) / rev p 1.00 |
| R40D_V | -1 | n=158, cont +66 bp (p 0.74) / rev p 1.00 | n=158, cont +42 bp (p 1.00) / rev p 1.00 | n=158, cont +24 bp (p 1.00) / rev p 1.00 |
| R40D_N | -1 | n=189, cont -74 bp (p 1.00) / rev p 0.08 | n=189, cont -94 bp (p 1.00) / rev p 0.83 | n=189, cont -12 bp (p 1.00) / rev p 1.00 |
| R40RECL_V | +1 | n=98 INSUFF | n=98 INSUFF | n=98 INSUFF |
| R60REJ_V | -1 | n=119, cont -46 bp (p 1.00) / rev p 0.99 | n=119, cont -40 bp (p 1.00) / rev p 1.00 | n=119, cont -12 bp (p 1.00) / rev p 1.00 |

### 4h: 12 best trials by RC p_adj

| event | h | orient | n | gross bp | net bp [95% CI] | win | excess bp | t | p_raw | p_adj | q_BH | MDE bp | triage |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R40D_N | 6 | rev | 189 | +86 | +70 [+24, +121] | 62% | +74 | 3.17 | 0.004 | 0.081 | 0.29 | 63 | PASS |
| DON_UP_V | 6 | cont | 314 | +82 | +61 [+9, +110] | 52% | +70 | 2.89 | 0.002 | 0.191 | 0.29 | 49 | FAIL |
| SP3_UP | 42 | cont | 219 | +330 | +288 [+62, +476] | 61% | +247 | 2.61 | 0.004 | 0.368 | 0.29 | 156 | FAIL |
| DON_UP_V | 42 | cont | 314 | +247 | +193 [+24, +341] | 55% | +164 | 2.54 | 0.010 | 0.421 | 0.54 | 131 | FAIL |
| BAWAY_UP | 42 | cont | 181 | +275 | +222 [+23, +392] | 56% | +192 | 2.35 | 0.013 | 0.577 | 0.56 | 172 | FAIL |
| R40D_V | 6 | cont | 158 | +54 | +43 [-20, +115] | 47% | +66 | 2.14 | 0.029 | 0.738 | 0.70 | 68 | FAIL |
| DON_UP_V | 18 | cont | 314 | +126 | +93 [+3, +179] | 58% | +90 | 2.13 | 0.018 | 0.754 | 0.65 | 83 | FAIL |
| R40D_N | 18 | rev | 189 | +130 | +108 [+13, +212] | 60% | +94 | 2.02 | 0.026 | 0.828 | 0.70 | 107 | FAIL |
| SP2_UP | 42 | cont | 585 | +203 | +161 [-9, +326] | 57% | +120 | 2.01 | 0.027 | 0.832 | 0.70 | 96 | FAIL |
| CVDDIV_BULL | 6 | rev | 215 | +83 | +68 [-14, +156] | 59% | +70 | 1.67 | 0.054 | 0.977 | 0.98 | 59 | FAIL |
| BBSQ_UP_V | 6 | cont | 201 | +70 | +49 [-22, +123] | 51% | +57 | 1.66 | 0.056 | 0.979 | 0.98 | 61 | FAIL |
| BAWAY_UP | 6 | cont | 181 | +63 | +42 [-25, +104] | 49% | +51 | 1.61 | 0.059 | 0.988 | 0.98 | 64 | FAIL |

### 4h: registered contrasts at h=18 (does volume add information? time hypotheses)

| id | what | nA | nB | mean A bp | mean B bp | diff bp | 95% CI bp | p | q_BH (C-family) | q (TH-family) | CI excludes 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | squeeze up-break: vol-confirmed minus not | 201 | 314 | +107 | +7 | +100 | [-14, +220] | 0.090 | 0.190 | - | no |
| C2 | squeeze down-break (short oriented) | 198 | 266 | -53 | -10 | -43 | [-147, +59] | 0.405 | 0.405 | - | no |
| C3 | Donchian up: vol-confirmed minus not | 314 | 153 | +126 | +6 | +120 | [-15, +266] | 0.090 | 0.190 | - | no |
| C4 | Donchian down (short oriented) | 239 | 70 | +48 | -91 | +139 | [-37, +297] | 0.105 | 0.190 | - | no |
| C5 | RSI up-cross 60: vol minus not | 153 | 230 | +83 | -12 | +94 | [-26, +216] | 0.119 | 0.190 | - | no |
| C6 | RSI down-cross 40 (short oriented) | 158 | 189 | +6 | -130 | +136 | [+5, +272] | 0.041 | 0.190 | - | yes |
| C7 | SP3 defined with RVadj minus defined with plain RV (overlapping sets; signed cont return) | 458 | 599 | +28 | +52 | -24 | [-68, +18] | 0.287 | 0.328 | - | no |
| C8/TH2 | SP3 weekend minus weekday (signed cont return) | 50 | 408 | -114 | +45 | -159 | [-376, +112] | 0.210 | 0.280 | 0.315 | no |
| TH1 | SP3 session C (16-24 UTC) minus A (00-08 UTC) | 188 | 145 | -40 | +138 | -178 | [-344, -20] | 0.027 | - | 0.081 | yes |
| TH3 | BBSQ_*_V session B (08-16) minus A (00-08) | 109 | 143 | +14 | +12 | +2 | [-128, +122] | 0.982 | - | 0.982 | no |

## Placebo calibration (volume and taker-buy columns circularly shifted by a multiple of 42 bars, lag >= 504; family-wise RC pass = any trial with p_adj < 0.10)

- 1d: 20 placebo runs, family-wise pass rate 0.05 (expected <= 0.10; miscalibrated if > 0.20) -> **CALIBRATED**. Events that triggered: {'DON_UP_N': 1}
- 4h: 20 placebo runs, family-wise pass rate 0.15 (expected <= 0.10; miscalibrated if > 0.20) -> **CALIBRATED**. Events that triggered: {'ABS_HIGH': 1, 'R40D_N': 1, 'SP2_DN': 1}

## Candidates frozen for VALIDATION (triage PASS on DEV)

| event | tf | h | orient | n | net bp [CI] | excess bp | p_adj |
|---|---|---|---|---|---|---|---|
| R40D_N | 4h | 6 | rev | 189 | +70 [+24, +121] | +74 | 0.081 |

T2 decay (R40D_N 4h rev): mean signed fwd bp by bar after entry: 1:+12, 6:+86, 12:+119, 18:+130, 24:+131, 30:+119, 36:+113, 42:+95
T3 EXPLORATORY strata (R40D_N 4h rev, h=6, excess bp vs all bars): session A 00-08 n=50 +18; session B 08-16 n=77 +69; session C 16-24 n=62 +125; weekend n=54 +128; weekday n=135 +52; bull (prev close > SMA200) n=87 +74; bear (prev close < SMA200) n=77 +80

