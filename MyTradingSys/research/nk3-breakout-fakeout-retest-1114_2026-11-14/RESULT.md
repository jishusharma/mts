**VERDICT: FAIL. None of the 16 phase-fit rows passes (no row has mean net R > 0 at 12 bp on VALIDATION); NK's breakout-retest and fakeout-fade rules, mapped objectively to a 20-bar box on 20 Binance spot coins, lose roughly the fee and a bit more.**

Nearest row: 1h type B (fakeout fade) X1, no filter: mean net R -0.034 (n 2448), CI lows -0.088 / -0.110, placebo p 0.000 (it beats random entries, which sit at -0.129), but still below zero after 12 bp. At the maker 6 bp sensitivity row it is +0.030R (n 2448); that row is not PASS-bearing and has no CI or placebo computed, so it is a lead, not a result.

## Context
Phase from the prior daily close: UP = ADX14(1d)>=20, +DI>-DI, MA20 slope(5d)>0; DOWN mirror; else RANGE. Primary rows trade the phase-fit direction only (A: long in UP, short in DOWN, none in RANGE; B: both ways in RANGE, long in UP, short in DOWN). Mismatched direction = control rows.

Regime mix: share of coin-bars by phase (identical on 15m and 1h within rounding).

| split | UP | DOWN | RANGE |
|---|---|---|---|
| DEV | 31% | 31% | 38% |
| VAL | 25% | 35% | 40% |

## Phase-fit rows, 12 bp taker, VALIDATION (from 2024-01-01); DEV = to 2023-12-31

`ex5` = mean net R without the 5 best days. `fee R` = mean fee as a fraction of R (min stop 0.5% / 0.6 ATR in force). BH family = these 16 rows; none survives.

| tf | type | exit | filter | n DEV | DEV mean R | n VAL | win % | mean net R | fee R | CI low trade | CI low day | placebo p | ex5 | BH | PASS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 15m | A | X1 | none | 15147 | -0.220 | 9423 | 33.7 | -0.228 | 0.21 | -0.255 | -0.269 | 0.917 | -0.242 | N | FAIL |
| 15m | A | X1 | blast | 5893 | -0.248 | 3586 | 33.8 | -0.226 | 0.21 | -0.270 | -0.287 | 0.803 | -0.247 | N | FAIL |
| 15m | B | X1 | none | 15634 | -0.129 | 10691 | 37.0 | -0.160 | 0.20 | -0.185 | -0.195 | 0.000 | -0.171 | N | FAIL |
| 15m | B | X1 | blast | 5007 | -0.122 | 3416 | 37.2 | -0.149 | 0.19 | -0.194 | -0.206 | 0.047 | -0.170 | N | FAIL |
| 15m | A | X2 | none | 15497 | -0.168 | 9781 | 28.8 | -0.209 | 0.21 | -0.240 | -0.251 | 0.260 | -0.238 | N | FAIL |
| 15m | A | X2 | blast | 5963 | -0.185 | 3645 | 28.0 | -0.239 | 0.21 | -0.278 | -0.292 | 0.883 | -0.267 | N | FAIL |
| 15m | B | X2 | none | 15982 | -0.178 | 11048 | 25.7 | -0.205 | 0.20 | -0.219 | -0.225 | 0.670 | -0.217 | N | FAIL |
| 15m | B | X2 | blast | 5035 | -0.177 | 3454 | 26.2 | -0.193 | 0.19 | -0.219 | -0.224 | 0.333 | -0.209 | N | FAIL |
| 1h | A | X1 | none | 3497 | -0.097 | 2261 | 34.5 | -0.132 | 0.15 | -0.188 | -0.213 | 0.210 | -0.177 | N | FAIL |
| 1h | A | X1 | blast | 1475 | -0.066 | 893 | 35.2 | -0.127 | 0.15 | -0.218 | -0.235 | 0.287 | -0.184 | N | FAIL |
| 1h | B | X1 | none | 3283 | -0.012 | 2448 | 38.4 | -0.034 | 0.13 | -0.088 | -0.110 | 0.000 | -0.066 | N | FAIL |
| 1h | B | X1 | blast | 1075 | 0.002 | 828 | 37.7 | -0.048 | 0.12 | -0.138 | -0.170 | 0.037 | -0.123 | N | FAIL |
| 1h | A | X2 | none | 3517 | -0.048 | 2260 | 32.7 | -0.157 | 0.15 | -0.211 | -0.229 | 0.587 | -0.198 | N | FAIL |
| 1h | A | X2 | blast | 1480 | -0.039 | 894 | 32.8 | -0.129 | 0.15 | -0.220 | -0.235 | 0.287 | -0.196 | N | FAIL |
| 1h | B | X2 | none | 3310 | -0.054 | 2474 | 31.2 | -0.100 | 0.13 | -0.140 | -0.160 | 0.107 | -0.145 | N | FAIL |
| 1h | B | X2 | blast | 1081 | -0.121 | 831 | 31.6 | -0.046 | 0.12 | -0.125 | -0.171 | 0.047 | -0.166 | N | FAIL |

## Controls and maker sensitivity (VALIDATION, no-filter rows; n, mean net R)

| tf | type | exit | fit 12bp | fit 6bp (maker) | control 12bp | control 6bp |
|---|---|---|---|---|---|---|
| 15m | A | X1 | 9423 / -0.228 | 9423 / -0.121 | 9168 / -0.218 | 9168 / -0.111 |
| 15m | A | X2 | 9781 / -0.209 | 9781 / -0.102 | 9465 / -0.209 | 9465 / -0.101 |
| 15m | B | X1 | 10691 / -0.160 | 10691 / -0.062 | 4627 / -0.177 | 4627 / -0.083 |
| 15m | B | X2 | 11048 / -0.205 | 11048 / -0.107 | 4703 / -0.191 | 4703 / -0.097 |
| 1h | A | X1 | 2261 / -0.132 | 2261 / -0.058 | 2206 / -0.194 | 2206 / -0.118 |
| 1h | A | X2 | 2260 / -0.157 | 2260 / -0.084 | 2231 / -0.104 | 2231 / -0.028 |
| 1h | B | X1 | 2448 / -0.034 | 2448 / 0.030 | 1115 / -0.176 | 1115 / -0.118 |
| 1h | B | X2 | 2474 / -0.100 | 2474 / -0.037 | 1119 / -0.110 | 1119 / -0.052 |

Controls (wrong direction for the phase) are also negative, so the phase gate neither rescues nor explains the result: the mapped rules carry no directional edge; the only visible structure is that fakeout fades lose less than random entries (placebo p ~0 on type B no-filter rows).

## BTC today (descriptive, no advice)

- Last closed 1h bar 2026-11-13T19:00:00.000 UTC, close 69060. Phase label (from prior daily close): DOWN.
- 20-bar 1h box: high 71514, low 67568; width 6.3 ATR (above the 4.0 ATR cap, so the study's box filter would not arm a signal now). Close is inside the box, mid-to-lower half; last three 1h closes 68944, 68989, 69060.
- A fakeout fade or retest setup in this study would need a close beyond 71.5k or below 67.6k first.

## Parameters
| param | value | label |
|---|---|---|
| BB length 20 / box length 20 | 20 | SOURCED (#1) for BB length; box mapping OURS |
| fakeout = breakout high not taken out next bar; close back inside | rule | SOURCED (#10, #13) |
| retest is best | type A | SOURCED (#9); zone = box edge OURS |
| stop = breakout candle extreme / prior candle trail (X2) | | SOURCED (#5-#7), mapping OURS |
| BB std-dev 2.0, blast thresholds, width 1.5-4 ATR, K=10, 2R, 24/48 bars, min stop, phase definition | | OURS (NOT_STATED by NK) |

## Method notes and limits
- Same-bar stop/target resolves to stop; type A limit fills assume a touch below the edge fills (optimistic); no slippage on stops beyond the 12 bp round trip. Both biases favour the strategy, and it still fails.
- DEV/VAL split by signal bar date; 20 coins pooled; one position per coin per row; 15m n is inflated by cross-coin correlation, which is why day-cluster CIs are reported.
- Data cache F:\MTS\data_cacheinance_spot (shared with another worker; key `ts`). Tests: test_study.py, 4 pass; causality test fails under STUDY_BUG=1 and 2.
