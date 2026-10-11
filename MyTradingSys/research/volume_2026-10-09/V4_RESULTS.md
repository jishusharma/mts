# V4 RESULTS - pooled volume-confirmation premium (VCP)

Registered in PRE_REG_ADDENDUM_B_2026-10-09.md (commit f69f01c) before any V4 outcome. VCP = pooled mean oriented gross forward return of volume-CONFIRMED breakout/cross events (RVadj >= 1.5) minus UNCONFIRMED (< 1.5) over six pairs (BB-squeeze up/down, Donchian-20 up/down, RSI(14) cross 60 up / 40 down). H1: VCP > 0. Primary 4h h=18, secondary 1d h=10, Bonferroni alpha 0.025 each.

## 4h (h = 18)

- DEV (descriptive prior, NOT a test, hypothesis was chosen on it): VCP +88 bp [+15, +155], confirmed n=1275 mean +60 bp (net of 14 bp: +46), unconfirmed n=1224 mean -27 bp, one-sided p=0.008, pairs positive 5/6
- **VALIDATION (the test)**: VCP -13 bp [-109, +81], confirmed n=286 mean -22 bp (net of 14 bp: -36), unconfirmed n=286 mean -9 bp, one-sided p=0.597, pairs positive 3/6
- VALIDATION verdict: **NOT SUPPORTED** (support needs one-sided p < 0.025 and VCP > 0)

Per-pair difference (confirmed minus unconfirmed, bp, oriented gross), DEV then VALIDATION:

| pair | DEV nV / nN | DEV diff | VALID nV / nN | VALID diff |
|---|---|---|---|---|
| BBSQ_UP_V | 201 / 314 | +100 | 35 / 61 | +20 |
| BBSQ_DN_V | 204 / 267 | -39 | 31 / 50 | -248 |
| DON_UP_V | 314 / 153 | +120 | 82 / 41 | +88 |
| DON_DN_V | 244 / 70 | +140 | 66 / 22 | -68 |
| R60U_V | 153 / 230 | +94 | 35 / 62 | +130 |
| R40D_V | 159 / 190 | +138 | 37 / 50 | -81 |

EXPLORATORY session split of the pooled difference (bp; CI; not evidence): DEV: A 00-08 nV=406 nN=349 +106 [-1, +212]; B 08-16 nV=404 nN=451 +69 [-53, +192]; C 16-24 nV=465 nN=424 +84 [-15, +185]

VALIDATION: A 00-08 nV=94 nN=62 +45 [-106, +210]; B 08-16 nV=71 nN=127 -30 [-217, +144]; C 16-24 nV=121 nN=97 -15 [-166, +131]

- HOLDOUT: sealed (VALIDATION did not support the hypothesis).

## 1d (h = 10)

- DEV (descriptive prior, NOT a test, hypothesis was chosen on it): VCP +314 bp [+12, +627], confirmed n=123 mean +324 bp (net of 14 bp: +310), unconfirmed n=270 mean +10 bp, one-sided p=0.026, pairs positive 6/6
- **VALIDATION (the test)**: VCP +123 bp [-425, +526], confirmed n=34 mean +168 bp (net of 14 bp: +154), unconfirmed n=57 mean +45 bp, one-sided p=0.339, pairs positive 3/6
- VALIDATION verdict: **NOT SUPPORTED** (support needs one-sided p < 0.025 and VCP > 0)

Per-pair difference (confirmed minus unconfirmed, bp, oriented gross), DEV then VALIDATION:

| pair | DEV nV / nN | DEV diff | VALID nV / nN | VALID diff |
|---|---|---|---|---|
| BBSQ_UP_V | 18 / 57 | +361 | 5 / 13 | +508 |
| BBSQ_DN_V | 21 / 40 | +382 | 7 / 5 | -128 |
| DON_UP_V | 43 / 55 | +100 | 10 / 18 | +351 |
| DON_DN_V | 21 / 19 | +946 | 7 / 2 | -295 |
| R60U_V | 12 / 56 | +178 | 1 / 15 | +1969 |
| R40D_V | 8 / 43 | +310 | 4 / 4 | -9 |

- HOLDOUT: sealed (VALIDATION did not support the hypothesis).

## Descriptive appendix (B2): events too rare for the registered test - DEV, oriented gross forward return, NO inference, NO pass/fail

| event | tf | n | h index 1 | h index 2 | h index 3 |
|---|---|---|---|---|---|
| BCLX (dir +1) | 4h | 82 | h=6: +57 bp [-25, +134] (all bars +12) | h=18: +141 bp [+12, +259] (all bars +36) | h=42: +211 bp [-42, +430] (all bars +83) |
| SCLX (dir -1) | 4h | 67 | h=6: -77 bp [-188, +44] (all bars -12) | h=18: +16 bp [-203, +261] (all bars -36) | h=42: -45 bp [-361, +287] (all bars -83) |
| ABS_LOW (dir -1) | 4h | 41 | h=6: +127 bp [-13, +247] (all bars -12) | h=18: +269 bp [-72, +566] (all bars -36) | h=42: -43 bp [-485, +393] (all bars -83) |
| ABS_HIGH (dir +1) | 4h | 36 | h=6: +39 bp [-65, +131] (all bars +12) | h=18: +238 bp [-50, +444] (all bars +36) | h=42: +462 bp [+139, +812] (all bars +83) |
| NODEM_HIGH (dir +1) | 4h | 55 | h=6: +3 bp [-89, +87] (all bars +12) | h=18: -126 bp [-370, +84] (all bars +36) | h=42: -123 bp [-594, +344] (all bars +83) |
| NOSUP_LOW (dir -1) | 4h | 23 | h=6: +70 bp [-82, +247] (all bars -12) | h=18: +160 bp [-91, +388] (all bars -36) | h=42: +1 bp [-494, +676] (all bars -83) |
| DON_DN_N (dir -1) | 4h | 70 | h=6: -90 bp [-174, -18] (all bars -12) | h=18: -91 bp [-243, +53] (all bars -36) | h=42: -227 bp [-443, +14] (all bars -83) |
| DRY_UP (dir +1) | 4h | 36 | h=6: +25 bp [-80, +124] (all bars +12) | h=18: +74 bp [-62, +230] (all bars +36) | h=42: +159 bp [-83, +423] (all bars +83) |
| DRY_DN (dir -1) | 4h | 34 | h=6: +10 bp [-91, +96] (all bars -12) | h=18: -104 bp [-215, +6] (all bars -36) | h=42: -112 bp [-336, +111] (all bars -83) |
| R40RECL_V (dir +1) | 4h | 98 | h=6: -50 bp [-176, +47] (all bars +12) | h=18: +9 bp [-119, +144] (all bars +36) | h=42: +131 bp [-65, +350] (all bars +83) |
| NODEM_HIGH (dir +1) | 1d | 26 | h=3: +113 bp [-287, +502] (all bars +40) | h=10: +346 bp [-330, +971] (all bars +131) | h=20: +287 bp [-471, +977] (all bars +259) |
| BBSQ_DN_V (dir -1) | 1d | 21 | h=3: +295 bp [-211, +639] (all bars -40) | h=10: +137 bp [-623, +527] (all bars -131) | h=20: +401 bp [-408, +916] (all bars -259) |
| DON_DN_V (dir -1) | 1d | 21 | h=3: +77 bp [-328, +386] (all bars -40) | h=10: +254 bp [-154, +643] (all bars -131) | h=20: +297 bp [-413, +909] (all bars -259) |

