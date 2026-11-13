# RESULT: ONE layer at a time on the RSI-extreme + confirm-candle long (edge4-rsi-confirm-layers-1113)

**Verdict: FAIL.** 0 of 56 pre-registered layer tests PASS on VALIDATION (6 UNDERPOWERED, 50 FAIL); pairs: none passed. No edge claim.
Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %): DEV 2020-2023 bull 51 % / bear 40 % / range 10 %; VALIDATION 2024-01..2026-11-05 bull 56 % / bear 30 % / range 15 % (to 2025-06 bull 74 % / bear 7 %; from 2025-07 bull 36 % / bear 54 %).
Rule: 1h / 4h RSI(14) <= 20 first touch (re-arm >30), next bar green and closing above signal close = long at that close, stop = signal-bar low, exits +1R / +2R (72 h cap), 20 Bybit USDT perps from listing, fees 2 x BINANCE_TAKER (10 bp RT, taker both legs, no slippage, no funding), week-block bootstrap 2000, random-subset placebo 1000, BH 10 % over 56. Splits: DEV <= 2023-12-31, VALIDATION from 2024-01-01 (entry time). Trades with < 168 h of forward data excluded (last 7 days). Trades: 1h 975 (DEV 460 / VAL 515), 4h 265 (DEV 119 / VAL 146).
Coverage: open interest starts 2020-08-11 (1h) / 2020-09-04 (4h) (Bybit 1h OI; 972 of 975 1h and 265 of 265 4h trades have a 24 h OI change); funding on all trades (Bybit 8 h history); daily ADX on 964 / 975. Layers use only data closed at or before the signal bar's close.

## Unfiltered base (the bar every layer has to beat)

| base | n DEV / VAL | win% VAL | mean R DEV | mean R VAL | CI 95% VAL |
|---|---|---|---|---|---|
| 1h +1R | 460 / 515 | 47% | -0.216 | -0.169 | [-0.33, -0.00] |
| 1h +2R | 460 / 515 | 38% | -0.213 | -0.095 | [-0.30, +0.12] |
| 4h +1R | 119 / 146 | 60% | -0.017 | +0.093 | [-0.14, +0.33] |
| 4h +2R | 119 / 146 | 52% | -0.265 | +0.220 | [-0.11, +0.57] |

The bare rule is negative fee-net on 1h in both periods; 4h VALIDATION is positive but not distinguishable from zero (CI includes 0) and negative in DEV.

## All 56 layer tests (VALIDATION decides; DEV shown for stability; placebo p = share of same-size random subsets of the base with mean >= the layer's)

| layer split (TF, exit) | n DEV / VAL | win% VAL | mean R VAL | mean R DEV | CI 95% VAL | vs base | placebo p | verdict |
|---|---|---|---|---|---|---|---|---|
| dADX<20, 1h +1R | 124 / 146 | 47% | -0.185 | -0.181 | [-0.40, +0.04] | -0.015 | 0.604 | FAIL |
| dADX20-25, 1h +1R | 99 / 105 | 45% | -0.190 | -0.229 | [-0.47, +0.05] | -0.021 | 0.617 | FAIL |
| dADX>25, 1h +1R | 226 / 264 | 48% | -0.153 | -0.214 | [-0.39, +0.07] | +0.017 | 0.328 | FAIL |
| dDI-down, 1h +1R | 300 / 403 | 47% | -0.181 | -0.166 | [-0.38, +0.01] | -0.012 | 0.690 | FAIL |
| 4hADX>=40, 1h +1R | 75 / 100 | 54% | -0.005 | -0.034 | [-0.36, +0.38] | +0.165 | 0.026 | FAIL |
| OI-unwind, 1h +1R | 229 / 180 | 61% | +0.117 | -0.222 | [-0.10, +0.32] | +0.287 | 0.001 | FAIL |
| VolCap, 1h +1R | 318 / 366 | 46% | -0.164 | -0.237 | [-0.37, +0.04] | +0.006 | 0.409 | FAIL |
| BTC>200MA, 1h +1R | 206 / 273 | 47% | -0.175 | -0.115 | [-0.41, +0.04] | -0.005 | 0.547 | FAIL |
| BTC/ETH, 1h +1R | 69 / 60 | 40% | -0.322 | -0.220 | [-0.62, -0.02] | -0.152 | 0.883 | FAIL |
| Asia, 1h +1R | 151 / 157 | 50% | -0.134 | -0.109 | [-0.41, +0.12] | +0.035 | 0.286 | FAIL |
| US, 1h +1R | 192 / 216 | 52% | -0.037 | -0.171 | [-0.30, +0.19] | +0.133 | 0.003 | FAIL |
| FundNeg, 1h +1R | 79 / 220 | 51% | -0.098 | -0.305 | [-0.31, +0.12] | +0.072 | 0.081 | FAIL |
| Deep, 1h +1R | 5 / 1 | 100% | +0.118 | +0.228 | [+0.12, +0.12] | +0.288 | - | UNDERPOWERED |
| SmallR, 1h +1R | 154 / 229 | 47% | -0.245 | -0.263 | [-0.44, -0.05] | -0.076 | 0.939 | FAIL |
| dADX<20, 1h +2R | 124 / 146 | 39% | -0.097 | -0.130 | [-0.34, +0.18] | -0.002 | 0.514 | FAIL |
| dADX20-25, 1h +2R | 99 / 105 | 35% | -0.147 | -0.212 | [-0.50, +0.20] | -0.052 | 0.658 | FAIL |
| dADX>25, 1h +2R | 226 / 264 | 38% | -0.073 | -0.252 | [-0.37, +0.22] | +0.022 | 0.365 | FAIL |
| dDI-down, 1h +2R | 300 / 403 | 37% | -0.112 | -0.134 | [-0.36, +0.15] | -0.017 | 0.704 | FAIL |
| 4hADX>=40, 1h +2R | 75 / 100 | 45% | +0.053 | +0.113 | [-0.29, +0.49] | +0.148 | 0.103 | FAIL |
| OI-unwind, 1h +2R | 229 / 180 | 53% | +0.244 | -0.335 | [-0.01, +0.48] | +0.339 | 0.001 | FAIL |
| VolCap, 1h +2R | 318 / 366 | 39% | -0.081 | -0.264 | [-0.35, +0.21] | +0.014 | 0.406 | FAIL |
| BTC>200MA, 1h +2R | 206 / 273 | 39% | -0.098 | -0.132 | [-0.34, +0.16] | -0.003 | 0.520 | FAIL |
| BTC/ETH, 1h +2R | 69 / 60 | 30% | -0.280 | -0.306 | [-0.69, +0.16] | -0.185 | 0.882 | FAIL |
| Asia, 1h +2R | 151 / 157 | 38% | -0.129 | -0.155 | [-0.57, +0.35] | -0.034 | 0.670 | FAIL |
| US, 1h +2R | 192 / 216 | 45% | +0.094 | -0.102 | [-0.21, +0.38] | +0.189 | 0.001 | FAIL |
| FundNeg, 1h +2R | 79 / 220 | 39% | -0.020 | -0.195 | [-0.31, +0.28] | +0.075 | 0.136 | FAIL |
| Deep, 1h +2R | 5 / 1 | 100% | +0.118 | +0.028 | [+0.12, +0.12] | +0.213 | - | UNDERPOWERED |
| SmallR, 1h +2R | 154 / 229 | 33% | -0.206 | -0.195 | [-0.47, +0.05] | -0.111 | 0.949 | FAIL |
| dADX<20, 4h +1R | 29 / 35 | 63% | -0.013 | -0.349 | [-0.44, +0.38] | -0.106 | 0.804 | FAIL |
| dADX20-25, 4h +1R | 23 / 30 | 73% | +0.307 | -0.085 | [+0.01, +0.57] | +0.214 | 0.075 | FAIL |
| dADX>25, 4h +1R | 66 / 81 | 54% | +0.060 | +0.137 | [-0.17, +0.30] | -0.033 | 0.692 | FAIL |
| dDI-down, 4h +1R | 108 / 138 | 59% | +0.074 | -0.024 | [-0.19, +0.32] | -0.020 | 0.870 | FAIL |
| 4hADX>=40, 4h +1R | 47 / 57 | 47% | -0.060 | +0.266 | [-0.32, +0.26] | -0.153 | 0.949 | FAIL |
| OI-unwind, 4h +1R | 59 / 65 | 65% | +0.080 | +0.042 | [-0.20, +0.36] | -0.013 | 0.567 | FAIL |
| VolCap, 4h +1R | 72 / 118 | 58% | +0.054 | -0.094 | [-0.21, +0.33] | -0.039 | 0.897 | FAIL |
| BTC>200MA, 4h +1R | 39 / 85 | 58% | -0.018 | -0.323 | [-0.34, +0.22] | -0.112 | 0.966 | FAIL |
| BTC/ETH, 4h +1R | 10 / 15 | 53% | +0.024 | -0.039 | [-0.47, +0.50] | -0.069 | 0.642 | UNDERPOWERED |
| Asia, 4h +1R | 34 / 49 | 76% | +0.267 | +0.209 | [-0.33, +0.69] | +0.173 | 0.052 | FAIL |
| US, 4h +1R | 59 / 57 | 51% | -0.069 | +0.010 | [-0.39, +0.29] | -0.163 | 0.965 | FAIL |
| FundNeg, 4h +1R | 46 / 85 | 62% | +0.066 | -0.006 | [-0.23, +0.37] | -0.028 | 0.683 | FAIL |
| Deep, 4h +1R | 1 / 0 | - | - | -1.178 | [-, -] | - | - | UNDERPOWERED |
| SmallR, 4h +1R | 40 / 45 | 58% | +0.037 | -0.165 | [-0.37, +0.35] | -0.057 | 0.711 | FAIL |
| dADX<20, 4h +2R | 29 / 35 | 60% | +0.232 | -0.633 | [-0.34, +0.92] | +0.012 | 0.487 | FAIL |
| dADX20-25, 4h +2R | 23 / 30 | 73% | +0.648 | -0.183 | [+0.17, +1.10] | +0.429 | 0.012 | FAIL |
| dADX>25, 4h +2R | 66 / 81 | 41% | +0.056 | -0.119 | [-0.25, +0.41] | -0.164 | 0.968 | FAIL |
| dDI-down, 4h +2R | 108 / 138 | 51% | +0.170 | -0.271 | [-0.16, +0.54] | -0.050 | 0.982 | FAIL |
| 4hADX>=40, 4h +2R | 47 / 57 | 42% | +0.132 | +0.044 | [-0.25, +0.62] | -0.088 | 0.746 | FAIL |
| OI-unwind, 4h +2R | 59 / 65 | 52% | -0.002 | -0.232 | [-0.36, +0.34] | -0.221 | 0.975 | FAIL |
| VolCap, 4h +2R | 72 / 118 | 50% | +0.117 | -0.355 | [-0.27, +0.48] | -0.103 | 0.982 | FAIL |
| BTC>200MA, 4h +2R | 39 / 85 | 48% | -0.004 | -0.418 | [-0.37, +0.37] | -0.223 | 0.996 | FAIL |
| BTC/ETH, 4h +2R | 10 / 15 | 53% | +0.306 | -0.317 | [-0.34, +0.90] | +0.086 | 0.364 | UNDERPOWERED |
| Asia, 4h +2R | 34 / 49 | 67% | +0.418 | -0.374 | [-0.51, +1.10] | +0.198 | 0.087 | FAIL |
| US, 4h +2R | 59 / 57 | 44% | -0.036 | -0.138 | [-0.48, +0.42] | -0.256 | 0.987 | FAIL |
| FundNeg, 4h +2R | 46 / 85 | 56% | +0.176 | -0.103 | [-0.16, +0.55] | -0.044 | 0.665 | FAIL |
| Deep, 4h +2R | 1 / 0 | - | - | -1.178 | [-, -] | - | - | UNDERPOWERED |
| SmallR, 4h +2R | 40 / 45 | 49% | +0.312 | -0.140 | [-0.29, +0.81] | +0.092 | 0.283 | FAIL |

PASS needs all of: n >= 30, mean > 0, CI lower > 0, beats base, placebo p <= 0.05, BH 10 %. BH column in cells.csv. The two layers with Deep n = 0..5 ('UNDERPOWERED') carry p ~ 0 by construction and take BH ranks; excluding them does not change any verdict.

## Closest calls (VALIDATION mean > 0 and CI lower > 0)

| layer split (TF, exit) | n DEV / VAL | win% VAL | mean R VAL | mean R DEV | CI 95% VAL | vs base | placebo p | verdict |
|---|---|---|---|---|---|---|---|---|
| dADX20-25, 4h +1R | 23 / 30 | 73% | +0.307 | -0.085 | [+0.01, +0.57] | +0.214 | 0.075 | FAIL |
| dADX20-25, 4h +2R | 23 / 30 | 73% | +0.648 | -0.183 | [+0.17, +1.10] | +0.429 | 0.012 | FAIL |

FAIL reason for each: BH 10 % over 56 not met (smallest real p is 0.006, BH needs <= 0.0054 at rank 3), and DEV mean is negative for the same split, so the sign does not hold across periods.

## Stage 2: pairs (only layers that passed the DEV screen: n >= 30, mean > 0, above DEV base)

DEV-screen layers per base: {"1h/1R": [], "1h/2R": ["4hADX>=40"], "4h/1R": ["dADX>25", "4hADX>=40", "OI-unwind", "Asia", "US"], "4h/2R": ["4hADX>=40"]}

| layer split (TF, exit) | n DEV / VAL | win% VAL | mean R VAL | mean R DEV | CI 95% VAL | vs base | placebo p | verdict |
|---|---|---|---|---|---|---|---|---|
| dADX>25 + 4hADX>=40, 4h +1R | 31 / 31 | 42% | -0.083 | +0.397 | [-0.40, +0.33] | -0.176 | 0.907 | FAIL |
| dADX>25 + OI-unwind, 4h +1R | 32 / 33 | 64% | +0.168 | +0.322 | [-0.12, +0.44] | +0.075 | 0.304 | FAIL |
| dADX>25 + US, 4h +1R | 34 / 30 | 47% | -0.076 | +0.162 | [-0.45, +0.50] | -0.170 | 0.885 | FAIL |

## Descriptive only (not tested; no verdict)

| subset | TF | n VAL | mean R +1R VAL | mean R +2R VAL | n DEV | mean R +2R DEV |
|---|---|---|---|---|---|---|
| Europe | 1h | 142 | -0.411 | -0.345 | 117 | -0.472 |
| Europe | 4h | 40 | +0.113 | +0.342 | 26 | -0.409 |
| RSI 10-15 | 1h | 21 | -0.371 | -0.293 | 43 | -0.226 |
| RSI 10-15 | 4h | 21 | +0.127 | +0.270 | 9 | +0.114 |
| RSI 15-20 | 1h | 493 | -0.162 | -0.087 | 412 | -0.215 |
| RSI 15-20 | 4h | 125 | +0.088 | +0.211 | 109 | -0.288 |
| RSI <=15 | 1h | 22 | -0.348 | -0.275 | 48 | -0.199 |
| RSI <=15 | 4h | 21 | +0.127 | +0.270 | 10 | -0.015 |

## Reading

- Nothing separates winners from losers robustly. The bare rule loses on 1h (-0.17 R at +1R after fees). Layers that look good on VALIDATION (OI-unwind and US session on 1h; daily ADX 20-25 on 4h) all had NEGATIVE DEV means, i.e. the sign flips between periods, which is what chance across 56 looks gives.
- Only 4hADX>=40 has the same sign in both periods on 1h (DEV -0.03/+0.11, VAL -0.01/+0.05 R at +1R/+2R), but its mean is ~0 and CI includes 0: it removes losses, it does not create an edge.
- Funding negative, volume capitulation, BTC above 200MA, BTC/ETH-vs-alt (BTC/ETH worse than alts), small stop and Asia do not help. 'Deep' (RSI <= 10) has 1 VALIDATION trade (5 DEV): the operator's example regime is too rare to test.
- Power: 1h VALIDATION n 60-400 per split, 4h 15-140; 4h results are mostly UNDERPOWERED-adjacent noise (CI width ~ 0.5-1.0 R).

Limits: no slippage, no funding charge, 10 bp RT fee (taker); trades across the 20 coins overlap in time (week blocks cover part); VALIDATION is mostly bull; ADX/DI per FORMULAS.md Wilder 14 (not TradingView-cross-checked here, HOW_TO_USE_ADX note applies); DEV screen thresholds are OURS; the OI/funding timestamp alignment uses the last record at or before signal close.

Best next test if anything: 4hADX>=40 + OI-unwind on 1h as a forward (testnet) paper log, since those are the only layers with a plausible mechanism and non-negative VALIDATION; do not promote on this evidence.
