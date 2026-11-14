# RESULT: where to sell the RSI-extreme + confirm-candle long (edge4-rsi-confirm-exits-1113)

**Verdict: FAIL. 0 of 48 pre-registered exit rules pass (16 per set; headline set S1 = 1h RSI<=20, 20 coins, 0 of 16, no exit has a positive fee-net VALIDATION mean).** No edge claim. The best S1 exit loses about 0.08R per trade net; the 4h set (S3) is gross-positive for most exits but no CI clears zero.

Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %): DEV (2020-01-01..2023-12-31) bull 51 % / bear 40 % / range 10 %; VALIDATION (2024-01-01..now) bull 56 % / bear 30 % / range 15 %.

Setup: Bybit v5 public linear 1h/1D, 20 coins since listing, entries as in edge3 (first touch, re-arm > 30, confirm = next bar green and closing above the signal close, entry = confirm close, stop = signal-bar low). Costs: 2 x fees.BINANCE_TAKER (5.00 bp/side, a little above the 4 bp in the brief) + fees.SLIPPAGE_RT_S13 (2 bp round trip) = 12 bp of entry price per round trip, divided by the stop distance to get R. Closed bars, stop before target in a bar, trades need a full 168 h forward window. Placebo: 30 draws of a random same-coin same-week bar with the same stop distance and exit rule (RSI/MA exits: bars below SMA20 with RSI<=40). n per split (all / DEV / VALIDATION): S1 982/482/500, S2 253/137/116, S3 268/124/144.

## Part 1: the path after entry (descriptive, all dates pooled, R = entry - signal low)

| set | n | stopped within 72 h | stop hit in bar 1 | reach +0.5R before stop | +1R | +2R | +0.5R then stopped (before +1R) | median bars to peak |
|---|---|---|---|---|---|---|---|---|
| S1 1h RSI<=20 (primary) | 982 | 73% | 17% | 58% | 41% | 25% | 14% | 6 |
| S2 1h RSI<=15 | 253 | 65% | 16% | 53% | 36% | 21% | 9% | 10 |
| S3 4h RSI<=20 | 268 | 49% | 7% | 60% | 40% | 21% | 8% | 16 |

Median raw MFE / MAE in R after k hourly bars (max high / min low from entry, stop ignored):

| set | 1b | 2b | 4b | 8b | 12b | 24b | 48b |
|---|---|---|---|---|---|---|---|
| S1 MFE | 0.37 | 0.49 | 0.64 | 0.84 | 1.02 | 1.43 | 1.94 |
| S1 MAE | 0.32 | 0.48 | 0.65 | 0.92 | 1.12 | 1.81 | 2.39 |
| S2 MFE | 0.27 | 0.42 | 0.55 | 0.69 | 0.78 | 1.12 | 1.40 |
| S2 MAE | 0.25 | 0.34 | 0.48 | 0.58 | 0.72 | 1.08 | 1.51 |
| S3 MFE | 0.15 | 0.20 | 0.30 | 0.49 | 0.65 | 0.92 | 1.07 |
| S3 MAE | 0.14 | 0.19 | 0.23 | 0.31 | 0.35 | 0.56 | 0.81 |

Reading: the price spends the first hours going both ways by about the same size (MFE ~ MAE), then the downside grows faster than the upside; the median peak (before the stop) is about 6 bars for S1. 1 in 7 S1 trades first gets +0.5R and then is stopped out.

## Part 2 S1: S1 1h RSI<=20 (primary), VALIDATION from 2024-01-01 (500 trades on 168 signal days)

| exit | n VAL | net>0 % | mean R gross | mean R net | CI trade (95%) | CI day-cluster | placebo mean (p) | DEV net | verdict |
|---|---|---|---|---|---|---|---|---|---|
| time2 | 500 | 41% | -0.088 | -0.217 | [-0.35, -0.07] | [-0.25, +0.02] | -0.161 (1.000) | -0.109 | FAIL |
| time4 | 500 | 42% | -0.092 | -0.221 | [-0.40, -0.05] | [-0.29, +0.03] | -0.181 (0.806) | -0.200 | FAIL |
| time8 | 500 | 40% | -0.003 | -0.132 | [-0.40, +0.16] | [-0.35, +0.16] | -0.209 (0.161) | -0.154 | FAIL |
| tgt0.5R | 500 | 59% | -0.091 | -0.220 | [-0.33, -0.11] | [-0.32, -0.11] | -0.302 (0.032) | -0.169 | FAIL |
| tgt0.75R | 500 | 53% | -0.068 | -0.197 | [-0.34, -0.06] | [-0.34, -0.09] | -0.325 (0.032) | -0.200 | FAIL |
| rsi30 | 500 | 48% | -0.088 | -0.217 | [-0.38, -0.05] | [-0.28, +0.01] | -0.186 (0.839) | -0.115 | FAIL |
| rsi40 | 500 | 42% | -0.022 | -0.151 | [-0.39, +0.10] | [-0.31, +0.17] | -0.226 (0.129) | -0.189 | FAIL |
| rsi50 | 500 | 34% | +0.046 | -0.083 | [-0.38, +0.24] | [-0.38, +0.17] | -0.261 (0.065) | -0.166 | FAIL |
| ma20touch | 500 | 39% | -0.008 | -0.137 | [-0.40, +0.13] | [-0.36, +0.07] | -0.261 (0.032) | -0.195 | FAIL |
| ma20close | 500 | 37% | +0.023 | -0.106 | [-0.39, +0.20] | [-0.35, +0.15] | -0.205 (0.065) | -0.217 | FAIL |
| be_tgt2 | 500 | 24% | -0.003 | -0.132 | [-0.29, +0.05] | [-0.27, +0.02] | -0.311 (0.032) | -0.205 | FAIL |
| trail | 500 | 38% | -0.100 | -0.229 | [-0.39, -0.06] | [-0.29, +0.11] | -0.265 (0.355) | -0.219 | FAIL |
| half_trail | 500 | 47% | -0.106 | -0.235 | [-0.36, -0.10] | [-0.30, -0.03] | -0.297 (0.161) | -0.197 | FAIL |
| confstop_1R | 500 | 49% | -0.023 | -0.161 | [-0.31, -0.01] | [-0.33, -0.06] | -0.333 (0.032) | -0.151 | FAIL |
| confstop_2R | 500 | 35% | +0.005 | -0.132 | [-0.36, +0.10] | [-0.35, +0.01] | -0.397 (0.032) | -0.123 | FAIL |
| base_1R | 500 | 47% | -0.074 | -0.203 | [-0.36, -0.03] | [-0.34, -0.05] | -0.350 (0.032) | -0.228 | FAIL |

## Part 2 S2: S2 1h RSI<=15, VALIDATION from 2024-01-01 (116 trades on 52 signal days)

| exit | n VAL | net>0 % | mean R gross | mean R net | CI trade (95%) | CI day-cluster | placebo mean (p) | DEV net | verdict |
|---|---|---|---|---|---|---|---|---|---|
| time2 | 116 | 51% | +0.005 | -0.113 | [-0.37, +0.12] | [-0.45, +0.03] | -0.149 (0.355) | -0.031 | FAIL |
| time4 | 116 | 48% | +0.060 | -0.059 | [-0.41, +0.27] | [-0.58, +0.02] | -0.188 (0.097) | -0.063 | FAIL |
| time8 | 116 | 46% | +0.156 | +0.038 | [-0.44, +0.54] | [-0.61, +0.18] | -0.225 (0.032) | +0.135 | FAIL |
| tgt0.5R | 116 | 59% | -0.116 | -0.234 | [-0.46, -0.05] | [-0.52, -0.08] | -0.332 (0.097) | -0.181 | FAIL |
| tgt0.75R | 116 | 53% | -0.097 | -0.215 | [-0.44, +0.01] | [-0.46, -0.02] | -0.350 (0.129) | -0.173 | FAIL |
| rsi30 | 116 | 49% | -0.033 | -0.151 | [-0.49, +0.18] | [-0.59, -0.03] | -0.190 (0.290) | +0.002 | FAIL |
| rsi40 | 116 | 42% | +0.070 | -0.048 | [-0.52, +0.43] | [-0.62, +0.13] | -0.292 (0.065) | +0.001 | FAIL |
| rsi50 | 116 | 39% | +0.154 | +0.036 | [-0.51, +0.64] | [-0.61, +0.29] | -0.315 (0.065) | +0.092 | FAIL |
| ma20touch | 116 | 48% | +0.192 | +0.074 | [-0.42, +0.59] | [-0.58, +0.19] | -0.281 (0.032) | -0.055 | FAIL |
| ma20close | 116 | 45% | +0.122 | +0.004 | [-0.51, +0.51] | [-0.63, +0.15] | -0.284 (0.065) | -0.079 | FAIL |
| be_tgt2 | 116 | 31% | +0.003 | -0.115 | [-0.39, +0.14] | [-0.42, +0.12] | -0.328 (0.032) | -0.199 | FAIL |
| trail | 116 | 40% | -0.035 | -0.153 | [-0.44, +0.14] | [-0.50, +0.07] | -0.347 (0.097) | -0.140 | FAIL |
| half_trail | 116 | 48% | -0.098 | -0.216 | [-0.46, +0.01] | [-0.50, -0.03] | -0.368 (0.065) | -0.167 | FAIL |
| confstop_1R | 116 | 55% | +0.097 | -0.006 | [-0.25, +0.20] | [-0.28, +0.18] | -0.334 (0.032) | -0.226 | FAIL |
| confstop_2R | 116 | 44% | +0.234 | +0.131 | [-0.23, +0.47] | [-0.26, +0.38] | -0.398 (0.032) | -0.316 | FAIL |
| base_1R | 116 | 51% | -0.043 | -0.161 | [-0.41, +0.09] | [-0.44, +0.07] | -0.367 (0.032) | -0.209 | FAIL |

## Part 2 S3: S3 4h RSI<=20, VALIDATION from 2024-01-01 (144 trades on 38 signal days)

| exit | n VAL | net>0 % | mean R gross | mean R net | CI trade (95%) | CI day-cluster | placebo mean (p) | DEV net | verdict |
|---|---|---|---|---|---|---|---|---|---|
| time2 | 144 | 45% | +0.117 | +0.061 | [-0.19, +0.28] | [-0.38, +0.09] | -0.067 (0.032) | -0.084 | FAIL |
| time4 | 144 | 47% | +0.055 | -0.002 | [-0.26, +0.21] | [-0.43, +0.04] | -0.128 (0.065) | -0.076 | FAIL |
| time8 | 144 | 68% | +0.253 | +0.196 | [-0.07, +0.40] | [-0.30, +0.20] | -0.145 (0.032) | -0.063 | FAIL |
| tgt0.5R | 144 | 70% | +0.072 | +0.015 | [-0.20, +0.22] | [-0.32, +0.13] | -0.298 (0.032) | -0.058 | FAIL |
| tgt0.75R | 144 | 67% | +0.122 | +0.065 | [-0.18, +0.28] | [-0.36, +0.19] | -0.322 (0.032) | -0.076 | FAIL |
| rsi30 | 144 | 53% | +0.040 | -0.017 | [-0.19, +0.14] | [-0.38, +0.04] | -0.136 (0.032) | +0.013 | FAIL |
| rsi40 | 144 | 62% | +0.060 | +0.003 | [-0.23, +0.21] | [-0.32, +0.16] | -0.236 (0.032) | -0.128 | FAIL |
| rsi50 | 144 | 65% | +0.197 | +0.141 | [-0.15, +0.43] | [-0.27, +0.39] | -0.300 (0.032) | -0.172 | FAIL |
| ma20touch | 144 | 65% | +0.116 | +0.059 | [-0.17, +0.25] | [-0.40, +0.12] | -0.242 (0.032) | -0.154 | FAIL |
| ma20close | 144 | 70% | +0.163 | +0.106 | [-0.14, +0.32] | [-0.37, +0.21] | -0.264 (0.032) | -0.148 | FAIL |
| be_tgt2 | 144 | 31% | +0.111 | +0.054 | [-0.20, +0.29] | [-0.29, +0.28] | -0.308 (0.032) | -0.160 | FAIL |
| trail | 144 | 58% | +0.037 | -0.020 | [-0.24, +0.18] | [-0.36, +0.14] | -0.297 (0.032) | -0.075 | FAIL |
| half_trail | 144 | 62% | +0.031 | -0.026 | [-0.24, +0.17] | [-0.33, +0.13] | -0.304 (0.032) | -0.068 | FAIL |
| confstop_1R | 144 | 60% | +0.198 | +0.154 | [-0.16, +0.43] | [-0.42, +0.09] | -0.297 (0.032) | -0.006 | FAIL |
| confstop_2R | 144 | 54% | +0.309 | +0.264 | [-0.12, +0.66] | [-0.30, +0.44] | -0.352 (0.032) | -0.125 | FAIL |
| base_1R | 144 | 61% | +0.134 | +0.077 | [-0.17, +0.31] | [-0.36, +0.24] | -0.344 (0.032) | -0.051 | FAIL |

Notes: gross = no costs; net = fees + slippage. Median net R sits near -1.0 for the late/wide exits (most trades are stopped, a minority win big); medians and %-return means are in results.json. The placebo mean is lower than the real mean for almost every exit, so the signal is better than a random entry with the same stop, but the improvement is not enough to cover cost per stop distance. Placebo p has a floor of 1/31 = 0.032 (30 draws). BH is applied inside each set over its 16 p-values (one-sided trade-level bootstrap); none is significant.

## Limits
No funding; 1h bars cannot order stop vs target inside a bar (stop first = pessimistic for tight targets); exits tested on one VALIDATION stretch (2024+, bull 56 %); coins overlap in time (day view and week blocks reduce, not remove, the dependence); tiny stop distances inflate cost in R and are not filtered (the operator rule has none); S3 has few signal days.

Files: PRE_REG.md (committed before outcomes), fetch.py, rsi_grid_lib.py (edge3 lib), exits_lib.py, study.py, test_exits.py, results.json, trades_S1.csv.
