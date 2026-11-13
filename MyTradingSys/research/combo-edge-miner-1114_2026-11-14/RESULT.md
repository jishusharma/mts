**VERDICT: FAIL. None of the 10 DEV-selected combinations passes the VAL gates at 12 bp (210,684 trials tried; best VAL mean net R 1.788 on n=79); 0 of 84 pre-registered thinker cells pass.**

**Descriptive, post-run (not a gate): the DEV-significant cells are one family, long trend / momentum continuation in the early-cycle UP phase (UP_E), and its SIGN replicates on VAL: 86% of the 649 DEV-CI>0 cells with VAL n >= 30 have VAL mean net R > 0 and 85% beat same-phase random entries (median VAL excess +0.47 R); shorts do not replicate. It fails the strict gates on tail dependence and the BH step, and BTC and ETH are in MIX_L today, so it is not active.**

# combo-edge-miner-1114: exhaustive 2/3-way layer combinations x phase x direction x 3 exits

## Context

Regime: BTC structure UP / MIX / DOWN (close vs SMA200d and its 20-day slope), 20 coins, 4h and 1d bars; entry day label from prior closes only.
Phase: cycle clock (halving, early under 540 days / late) x structure = 6 labels, every cell conditioned on exactly one label.
Session: none, because holds are days to weeks.
Entry: next bar open after the onset bar, taker, 12 bp round trip plus actual funding, stop max(2.5 ATR, 2%), exits 3R / ATR trail / structure break.

Regime mix: DEV (2020-2023, 27,704 coin-days) bull 51.4% / range 21.1% / bear 27.5%; VAL (2024-2026-11, 20,960 coin-days) bull 58.1% / range 15.2% / bear 26.7% (bull = UP, range = MIX, bear = DOWN; shares of coin-days with a valid label).
Six-label shares (DEV | VAL, 1d frame): UP_E 28.0% | 39.1%, UP_L 23.4% | 19.0%, MIX_E 8.2% | 11.1%, MIX_L 12.9% | 4.1%, DOWN_E 0.9% | 1.3%, DOWN_L 26.7% | 25.4%.

## Trials and deflation (DEV, selection only)

- Cells enumerated (combo x direction x phase x exit x timeframe): **210,600**; plus 84 named thinker trials = **210,684 total trials**.
- Cells with n >= 100 non-overlapping DEV trades: 10,262; of those, mean net R > 0 at 12 bp: 5,560; day-cluster CI lower bound > 0: 694.
- Benjamini-Hochberg over m = 210,684: **29 cells rejected at q < 0.05**. Best DEV cluster t = 5.34.
- Max-of-N placebo (40 rounds of random same-phase entries in every qualifying cell): the null maximum t has mean 6.71, 95th percentile 7.25, max 7.69. A DEV cell is distinguishable from the best-of-everything noise only when its t is above that range.

## Top 10 chosen on DEV (rank = day-cluster CI lower bound at 12 bp), confirmed untouched on VAL

Net R columns are mean per trade after fees, slippage and funding. fee R = round-trip cost divided by the stop distance. DEV excess = DEV mean minus the mean of random same-phase entries with the same exit. Placebo p = share of 1,000 random same-phase VAL draws (same n, same exit) with mean at least the cell's.

| # | tf | dir | phase | exit | combination | DEV n | DEV net R [CI] | DEV gross | fee R | DEV excess | BH q | max-N p | VAL n | VAL net R @12 | VAL CI | VAL @6 | ex-best-5 | placebo p | VAL BH q | PASS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1d | L | UP_E | RIDE | ADX_DI+VOLX | 118 | 2.429 [1.212, 3.646] | 2.663 | 0.007 | 1.004 | 0.128 | 1.000 | 96 | 1.582 | [-0.030, 3.628] | 1.587 | -0.174 | 0.008 | 0.062 | fail |
| 2 | 1d | L | UP_E | RIDE | RSI_MOM+ADX_DI+VOLX | 103 | 2.399 [1.186, 3.612] | 2.666 | 0.007 | 0.974 | 0.132 | 1.000 | 87 | 1.636 | [-0.086, 3.631] | 1.641 | -0.175 | 0.013 | 0.062 | fail |
| 3 | 1d | L | UP_E | RIDE | ADX_DI+TREND_MA+VOLX | 110 | 2.186 [1.163, 3.208] | 2.405 | 0.007 | 0.761 | 0.062 | 1.000 | 78 | 1.603 | [-0.066, 3.724] | 1.607 | -0.249 | 0.016 | 0.062 | fail |
| 4 | 4h | L | UP_E | RIDE | ADX_DI+VOLX | 276 | 4.377 [1.108, 7.645] | 4.730 | 0.017 | 2.117 | 1.000 | 1.000 | 357 | 0.887 | [-0.351, 2.928] | 0.899 | -0.373 | 0.164 | 0.218 | fail |
| 5 | 4h | L | UP_E | RIDE | RSI_MOM+VOLX | 299 | 4.212 [1.081, 7.343] | 4.564 | 0.019 | 1.951 | 1.000 | 1.000 | 345 | 0.908 | [-0.369, 3.003] | 0.920 | -0.432 | 0.169 | 0.231 | fail |
| 6 | 1d | L | UP_E | RIDE | RSI_MOM+VOLX | 122 | 2.296 [1.071, 3.522] | 2.552 | 0.007 | 0.872 | 0.222 | 1.000 | 104 | 1.175 | [-0.014, 2.713] | 1.180 | -0.108 | 0.038 | 0.062 | fail |
| 7 | 1d | L | UP_E | RIDE | RSI_MOM+TREND_MA+VOLX | 114 | 2.233 [1.066, 3.399] | 2.472 | 0.007 | 0.808 | 0.196 | 1.000 | 80 | 1.625 | [0.185, 3.461] | 1.630 | -0.008 | 0.023 | 0.062 | fail |
| 8 | 1d | L | UP_E | RIDE | BRK5+ADX_DI+VOLX | 100 | 2.177 [1.041, 3.313] | 2.433 | 0.007 | 0.752 | 0.196 | 1.000 | 79 | 1.788 | [0.044, 3.935] | 1.793 | -0.155 | 0.013 | 0.062 | fail |
| 9 | 4h | L | UP_E | RIDE | BRK5+RSI_MOM+ADX_DI | 285 | 4.167 [1.029, 7.306] | 4.518 | 0.019 | 1.907 | 1.000 | 1.000 | 366 | 1.025 | [-0.372, 3.157] | 1.038 | -0.431 | 0.107 | 0.156 | fail |
| 10 | 1d | L | UP_E | RIDE | BRK5+VOLX | 123 | 2.419 [1.011, 3.827] | 2.663 | 0.007 | 0.994 | 0.477 | 1.000 | 117 | 1.211 | [-0.234, 3.023] | 1.216 | -0.339 | 0.036 | 0.141 | fail |

Top 3 by VAL mean net R at 12 bp (among the 10):

| tf | dir | phase | exit | combination | VAL n | VAL net R @12 | VAL CI | placebo p | PASS |
|---|---|---|---|---|---|---|---|---|---|
| 1d | L | UP_E | RIDE | BRK5+ADX_DI+VOLX | 79 | 1.788 | [0.044, 3.935] | 0.013 | fail |
| 1d | L | UP_E | RIDE | RSI_MOM+ADX_DI+VOLX | 87 | 1.636 | [-0.086, 3.631] | 0.013 | fail |
| 1d | L | UP_E | RIDE | RSI_MOM+TREND_MA+VOLX | 80 | 1.625 | [0.185, 3.461] | 0.023 | fail |

## Pre-registered thinker combinations (bank-feature analogs, not selected from DEV)

BH family = 84 cells on VAL. 44 of 84 have VAL n < 30 and 38 have DEV n < 30: UNDERPOWERED, not 'no edge' (same-bar AND of 3-4 layers inside one phase set is rare). T6 cohort divergence: NOT_IN_DATA (top-trader position ratio not in the cache).

| combination | tf | exit | dir | phases | DEV n | DEV net R | VAL n | VAL net R @12 | VAL CI | placebo p | PASS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 flush-reset long | 1d | T3R | L | UP_E,UP_L,MIX_E,MIX_L | 0 | - | 0 | - | - | - | fail |
| T1 flush-reset long | 1d | TRAIL | L | UP_E,UP_L,MIX_E,MIX_L | 0 | - | 0 | - | - | - | fail |
| T1 flush-reset long | 1d | RIDE | L | UP_E,UP_L,MIX_E,MIX_L | 0 | - | 0 | - | - | - | fail |
| T1 flush-reset long | 4h | T3R | L | UP_E,UP_L,MIX_E,MIX_L | 1 | - | 14 | -0.169 | [-1.017, 0.688] | 0.507 | fail |
| T1 flush-reset long | 4h | TRAIL | L | UP_E,UP_L,MIX_E,MIX_L | 1 | - | 14 | -0.296 | [-0.736, 0.122] | 0.712 | fail |
| T1 flush-reset long | 4h | RIDE | L | UP_E,UP_L,MIX_E,MIX_L | 1 | - | 14 | -0.384 | [-0.687, -0.072] | 0.629 | fail |
| T2 trapped-longs short | 1d | T3R | S | DOWN_E,DOWN_L | 4 | - | 9 | 0.426 | [-0.502, 1.515] | 0.193 | fail |
| T2 trapped-longs short | 1d | TRAIL | S | DOWN_E,DOWN_L | 4 | - | 9 | 0.153 | [-0.724, 1.156] | 0.361 | fail |
| T2 trapped-longs short | 1d | RIDE | S | DOWN_E,DOWN_L | 4 | - | 9 | 0.236 | [-0.633, 1.410] | 0.214 | fail |
| T2 trapped-longs short | 4h | T3R | S | DOWN_E,DOWN_L | 4 | - | 9 | -0.050 | [-1.015, 0.966] | 0.446 | fail |
| T2 trapped-longs short | 4h | TRAIL | S | DOWN_E,DOWN_L | 4 | - | 9 | -0.074 | [-0.832, 0.689] | 0.523 | fail |
| T2 trapped-longs short | 4h | RIDE | S | DOWN_E,DOWN_L | 4 | - | 9 | -0.348 | [-0.921, 0.263] | 0.692 | fail |
| T2b trapped-longs short + no spot absorb | 1d | T3R | S | DOWN_E,DOWN_L | 2 | - | 3 | - | - | - | fail |
| T2b trapped-longs short + no spot absorb | 1d | TRAIL | S | DOWN_E,DOWN_L | 2 | - | 3 | - | - | - | fail |
| T2b trapped-longs short + no spot absorb | 1d | RIDE | S | DOWN_E,DOWN_L | 2 | - | 3 | - | - | - | fail |
| T2b trapped-longs short + no spot absorb | 4h | T3R | S | DOWN_E,DOWN_L | 2 | - | 3 | - | - | - | fail |
| T2b trapped-longs short + no spot absorb | 4h | TRAIL | S | DOWN_E,DOWN_L | 2 | - | 3 | - | - | - | fail |
| T2b trapped-longs short + no spot absorb | 4h | RIDE | S | DOWN_E,DOWN_L | 2 | - | 3 | - | - | - | fail |
| T3 trapped-shorts squeeze long | 1d | T3R | L | UP_E,UP_L,MIX_E,MIX_L | 3 | - | 5 | 0.792 | [-0.812, 2.396] | 0.099 | fail |
| T3 trapped-shorts squeeze long | 1d | TRAIL | L | UP_E,UP_L,MIX_E,MIX_L | 3 | - | 5 | 5.646 | [-0.974, 18.036] | 0.032 | fail |
| T3 trapped-shorts squeeze long | 1d | RIDE | L | UP_E,UP_L,MIX_E,MIX_L | 3 | - | 5 | 6.216 | [-0.809, 18.490] | 0.024 | fail |
| T3 trapped-shorts squeeze long | 4h | T3R | L | UP_E,UP_L,MIX_E,MIX_L | 50 | 0.399 | 76 | 0.220 | [-0.185, 0.692] | 0.053 | fail |
| T3 trapped-shorts squeeze long | 4h | TRAIL | L | UP_E,UP_L,MIX_E,MIX_L | 48 | -0.017 | 76 | 0.280 | [-0.273, 0.937] | 0.156 | fail |
| T3 trapped-shorts squeeze long | 4h | RIDE | L | UP_E,UP_L,MIX_E,MIX_L | 45 | 2.675 | 72 | 2.420 | [0.217, 5.887] | 0.047 | fail |
| T4 squeeze-exhaustion short | 1d | T3R | S | DOWN_E,DOWN_L | 12 | -0.369 | 5 | 0.289 | [-0.407, 1.215] | 0.313 | fail |
| T4 squeeze-exhaustion short | 1d | TRAIL | S | DOWN_E,DOWN_L | 12 | -0.332 | 5 | 0.166 | [-0.765, 1.333] | 0.365 | fail |
| T4 squeeze-exhaustion short | 1d | RIDE | S | DOWN_E,DOWN_L | 12 | 0.028 | 7 | 0.425 | [-0.440, 2.508] | 0.144 | fail |
| T4 squeeze-exhaustion short | 4h | T3R | S | DOWN_E,DOWN_L | 16 | -0.253 | 13 | 0.110 | [-1.018, 1.425] | 0.369 | fail |
| T4 squeeze-exhaustion short | 4h | TRAIL | S | DOWN_E,DOWN_L | 16 | -0.043 | 13 | 0.147 | [-0.756, 1.268] | 0.361 | fail |
| T4 squeeze-exhaustion short | 4h | RIDE | S | DOWN_E,DOWN_L | 16 | 0.003 | 13 | -0.167 | [-0.680, 0.497] | 0.607 | fail |
| T5 spot-led ignition long | 1d | T3R | L | UP_E,UP_L,MIX_E,MIX_L | 20 | 0.752 | 9 | 2.964 | [2.958, 2.969] | 0.001 | fail |
| T5 spot-led ignition long | 1d | TRAIL | L | UP_E,UP_L,MIX_E,MIX_L | 18 | 1.359 | 9 | 2.266 | [1.191, 3.610] | 0.058 | fail |
| T5 spot-led ignition long | 1d | RIDE | L | UP_E,UP_L,MIX_E,MIX_L | 19 | 1.528 | 9 | 2.856 | [0.764, 5.470] | 0.049 | fail |
| T5 spot-led ignition long | 4h | T3R | L | UP_E,UP_L,MIX_E,MIX_L | 34 | 0.192 | 17 | 1.878 | [-0.633, 2.960] | 0.001 | fail |
| T5 spot-led ignition long | 4h | TRAIL | L | UP_E,UP_L,MIX_E,MIX_L | 34 | 0.165 | 13 | 1.728 | [-0.238, 2.756] | 0.019 | fail |
| T5 spot-led ignition long | 4h | RIDE | L | UP_E,UP_L,MIX_E,MIX_L | 31 | 1.038 | 13 | 3.166 | [-0.944, 5.093] | 0.046 | fail |
| T7 bear rip-sell short | 1d | T3R | S | DOWN_E,DOWN_L | 8 | -0.419 | 9 | 0.532 | [0.025, 1.104] | 0.132 | fail |
| T7 bear rip-sell short | 1d | TRAIL | S | DOWN_E,DOWN_L | 8 | -0.518 | 9 | 0.427 | [-0.097, 0.934] | 0.189 | fail |
| T7 bear rip-sell short | 1d | RIDE | S | DOWN_E,DOWN_L | 8 | -0.042 | 9 | -0.182 | [-0.431, 0.148] | 0.642 | fail |
| T7 bear rip-sell short | 4h | T3R | S | DOWN_E,DOWN_L | 38 | -0.285 | 31 | -0.585 | [-0.958, -0.134] | 0.982 | fail |
| T7 bear rip-sell short | 4h | TRAIL | S | DOWN_E,DOWN_L | 39 | -0.051 | 31 | -0.418 | [-0.718, -0.127] | 0.960 | fail |
| T7 bear rip-sell short | 4h | RIDE | S | DOWN_E,DOWN_L | 38 | -0.218 | 31 | -0.459 | [-0.872, 0.241] | 0.947 | fail |
| T8 broken-low continuation short | 1d | T3R | S | DOWN_E,DOWN_L | 11 | 0.076 | 6 | 0.842 | [-1.002, 2.388] | 0.060 | fail |
| T8 broken-low continuation short | 1d | TRAIL | S | DOWN_E,DOWN_L | 11 | 0.347 | 6 | 0.329 | [-1.002, 1.390] | 0.284 | fail |
| T8 broken-low continuation short | 1d | RIDE | S | DOWN_E,DOWN_L | 11 | 0.208 | 6 | 0.382 | [-0.901, 1.389] | 0.181 | fail |
| T8 broken-low continuation short | 4h | T3R | S | DOWN_E,DOWN_L | 30 | -0.170 | 22 | 0.744 | [-0.070, 1.595] | 0.008 | fail |
| T8 broken-low continuation short | 4h | TRAIL | S | DOWN_E,DOWN_L | 28 | 0.023 | 21 | 0.546 | [-0.409, 1.699] | 0.074 | fail |
| T8 broken-low continuation short | 4h | RIDE | S | DOWN_E,DOWN_L | 28 | 0.143 | 19 | 0.754 | [-0.381, 2.013] | 0.081 | fail |
| T9 200w failed breakdown long | 1d | T3R | L | MIX_E,MIX_L,DOWN_E,DOWN_L | 41 | 0.771 | 27 | 0.042 | [-0.680, 0.569] | 0.613 | fail |
| T9 200w failed breakdown long | 1d | TRAIL | L | MIX_E,MIX_L,DOWN_E,DOWN_L | 40 | 1.153 | 27 | 0.049 | [-0.637, 0.671] | 0.785 | fail |
| T9 200w failed breakdown long | 1d | RIDE | L | MIX_E,MIX_L,DOWN_E,DOWN_L | 46 | 0.844 | 32 | 0.158 | [-0.295, 0.649] | 0.489 | fail |
| T9 200w failed breakdown long | 4h | T3R | L | MIX_E,MIX_L,DOWN_E,DOWN_L | 173 | 0.883 | 49 | -0.264 | [-0.751, 0.146] | 0.907 | fail |
| T9 200w failed breakdown long | 4h | TRAIL | L | MIX_E,MIX_L,DOWN_E,DOWN_L | 173 | 0.690 | 57 | -0.003 | [-0.475, 0.427] | 0.580 | fail |
| T9 200w failed breakdown long | 4h | RIDE | L | MIX_E,MIX_L,DOWN_E,DOWN_L | 196 | 0.689 | 67 | 0.192 | [-0.380, 1.322] | 0.394 | fail |
| T10 washout band-reclaim trend long | 1d | T3R | L | UP_E,UP_L,MIX_E | 279 | 0.548 | 187 | 0.189 | [-0.101, 0.509] | 0.030 | fail |
| T10 washout band-reclaim trend long | 1d | TRAIL | L | UP_E,UP_L,MIX_E | 241 | 1.139 | 172 | 0.880 | [-0.048, 2.154] | 0.039 | fail |
| T10 washout band-reclaim trend long | 1d | RIDE | L | UP_E,UP_L,MIX_E | 246 | 1.211 | 181 | 0.756 | [-0.051, 1.939] | 0.061 | fail |
| T10 washout band-reclaim trend long | 4h | T3R | L | UP_E,UP_L,MIX_E | 742 | 0.258 | 542 | 0.105 | [-0.153, 0.361] | 0.004 | fail |
| T10 washout band-reclaim trend long | 4h | TRAIL | L | UP_E,UP_L,MIX_E | 808 | 0.300 | 575 | 0.292 | [-0.031, 0.707] | 0.063 | fail |
| T10 washout band-reclaim trend long | 4h | RIDE | L | UP_E,UP_L,MIX_E | 472 | 2.417 | 375 | 0.882 | [0.100, 1.843] | 0.110 | fail |
| T11 sweep-reclaim discount long | 1d | T3R | L | all | 474 | 0.036 | 359 | 0.028 | [-0.155, 0.243] | 0.451 | fail |
| T11 sweep-reclaim discount long | 1d | TRAIL | L | all | 402 | 0.049 | 313 | 0.294 | [-0.095, 0.753] | 0.476 | fail |
| T11 sweep-reclaim discount long | 1d | RIDE | L | all | 639 | -0.023 | 504 | 0.083 | [-0.118, 0.321] | 0.831 | fail |
| T11 sweep-reclaim discount long | 4h | T3R | L | all | 927 | 0.000 | 770 | -0.035 | [-0.238, 0.188] | 0.249 | fail |
| T11 sweep-reclaim discount long | 4h | TRAIL | L | all | 1122 | 0.010 | 939 | 0.108 | [-0.095, 0.337] | 0.289 | fail |
| T11 sweep-reclaim discount long | 4h | RIDE | L | all | 1196 | 0.036 | 998 | 0.127 | [-0.136, 0.428] | 0.801 | fail |
| T11b sweep-reclaim discount + OI flush long | 1d | T3R | L | all | 146 | -0.126 | 122 | 0.099 | [-0.191, 0.410] | 0.265 | fail |
| T11b sweep-reclaim discount + OI flush long | 1d | TRAIL | L | all | 138 | -0.118 | 118 | 1.090 | [0.127, 2.467] | 0.037 | fail |
| T11b sweep-reclaim discount + OI flush long | 1d | RIDE | L | all | 163 | -0.040 | 138 | 0.529 | [-0.070, 1.473] | 0.137 | fail |
| T11b sweep-reclaim discount + OI flush long | 4h | T3R | L | all | 176 | -0.295 | 141 | -0.285 | [-0.547, 0.006] | 0.932 | fail |
| T11b sweep-reclaim discount + OI flush long | 4h | TRAIL | L | all | 182 | -0.255 | 143 | -0.203 | [-0.431, 0.046] | 0.940 | fail |
| T11b sweep-reclaim discount + OI flush long | 4h | RIDE | L | all | 196 | -0.204 | 150 | 0.063 | [-0.364, 0.589] | 0.597 | fail |
| T12 flag long (squeeze, ADX, break) | 1d | T3R | L | UP_E,UP_L | 98 | -0.280 | 53 | 0.244 | [-0.244, 0.713] | 0.067 | fail |
| T12 flag long (squeeze, ADX, break) | 1d | TRAIL | L | UP_E,UP_L | 93 | 0.234 | 52 | 0.355 | [-0.340, 1.435] | 0.259 | fail |
| T12 flag long (squeeze, ADX, break) | 1d | RIDE | L | UP_E,UP_L | 96 | 0.183 | 52 | 0.179 | [-0.288, 0.696] | 0.315 | fail |
| T12 flag long (squeeze, ADX, break) | 4h | T3R | L | UP_E,UP_L | 123 | 0.166 | 85 | 0.090 | [-0.429, 0.737] | 0.077 | fail |
| T12 flag long (squeeze, ADX, break) | 4h | TRAIL | L | UP_E,UP_L | 123 | 0.356 | 83 | 0.404 | [-0.132, 1.059] | 0.096 | fail |
| T12 flag long (squeeze, ADX, break) | 4h | RIDE | L | UP_E,UP_L | 116 | 0.785 | 80 | 0.513 | [-0.296, 1.437] | 0.311 | fail |
| T12 flag short (squeeze, ADX, break) | 1d | T3R | S | DOWN_E,DOWN_L | 65 | 0.510 | 63 | -0.149 | [-0.514, 0.363] | 0.904 | fail |
| T12 flag short (squeeze, ADX, break) | 1d | TRAIL | S | DOWN_E,DOWN_L | 58 | 0.583 | 52 | -0.090 | [-0.408, 0.233] | 0.707 | fail |
| T12 flag short (squeeze, ADX, break) | 1d | RIDE | S | DOWN_E,DOWN_L | 63 | 0.437 | 54 | -0.072 | [-0.389, 0.323] | 0.611 | fail |
| T12 flag short (squeeze, ADX, break) | 4h | T3R | S | DOWN_E,DOWN_L | 129 | -0.034 | 103 | -0.144 | [-0.498, 0.313] | 0.688 | fail |
| T12 flag short (squeeze, ADX, break) | 4h | TRAIL | S | DOWN_E,DOWN_L | 140 | -0.123 | 104 | -0.038 | [-0.388, 0.452] | 0.653 | fail |
| T12 flag short (squeeze, ADX, break) | 4h | RIDE | S | DOWN_E,DOWN_L | 115 | 0.456 | 97 | -0.077 | [-0.571, 0.691] | 0.725 | fail |

## Beta every cell is up against: all-days random entries (12 bp, mean net R, no signal)

| tf | dir | exit | DEV n | DEV mean | VAL n | VAL mean |
|---|---|---|---|---|---|---|
| 4h | L | T3R | 166,233 | 0.078 | 125,426 | -0.077 |
| 4h | L | TRAIL | 166,233 | 0.158 | 125,439 | 0.067 |
| 4h | L | RIDE | 166,233 | 0.773 | 125,567 | 0.300 |
| 4h | S | T3R | 166,233 | -0.018 | 124,578 | 0.069 |
| 4h | S | TRAIL | 166,233 | -0.041 | 124,682 | -0.005 |
| 4h | S | RIDE | 166,233 | -0.028 | 122,444 | -0.073 |
| 1d | L | T3R | 27,664 | 0.201 | 20,715 | 0.020 |
| 1d | L | TRAIL | 27,664 | 0.501 | 20,709 | 0.307 |
| 1d | L | RIDE | 27,664 | 0.459 | 20,850 | 0.221 |
| 1d | S | T3R | 27,664 | -0.060 | 20,377 | 0.021 |
| 1d | S | TRAIL | 27,664 | -0.117 | 19,949 | -0.052 |
| 1d | S | RIDE | 27,664 | -0.065 | 20,164 | -0.082 |

## Active now (descriptive, last closed bar, no advice)

Whether each top-10 combination's conditions are true at the last closed bar of BTC and ETH, and the phase label for the current day. `in phase` = the label equals the cell's phase.

| # | combination | tf | BTC state | BTC phase | ETH state | ETH phase |
|---|---|---|---|---|---|---|
| 1 | ADX_DI+VOLX (L, UP_E, RIDE) | 1d | false | MIX_L | false | MIX_L |
| 2 | RSI_MOM+ADX_DI+VOLX (L, UP_E, RIDE) | 1d | false | MIX_L | false | MIX_L |
| 3 | ADX_DI+TREND_MA+VOLX (L, UP_E, RIDE) | 1d | false | MIX_L | false | MIX_L |
| 4 | ADX_DI+VOLX (L, UP_E, RIDE) | 4h | false | MIX_L | false | MIX_L |
| 5 | RSI_MOM+VOLX (L, UP_E, RIDE) | 4h | false | MIX_L | false | MIX_L |
| 6 | RSI_MOM+VOLX (L, UP_E, RIDE) | 1d | false | MIX_L | false | MIX_L |
| 7 | RSI_MOM+TREND_MA+VOLX (L, UP_E, RIDE) | 1d | false | MIX_L | false | MIX_L |
| 8 | BRK5+ADX_DI+VOLX (L, UP_E, RIDE) | 1d | false | MIX_L | false | MIX_L |
| 9 | BRK5+RSI_MOM+ADX_DI (L, UP_E, RIDE) | 4h | false | MIX_L | false | MIX_L |
| 10 | BRK5+VOLX (L, UP_E, RIDE) | 1d | false | MIX_L | false | MIX_L |

## Replication diagnostic (post-run, descriptive, NOT pre-registered, NOT used for selection)

All 10,262 DEV cells with n >= 100 were also evaluated on VAL (mean net R at 12 bp, no bootstrap); 8,963 have VAL n >= 30. Cells overlap heavily (same trades under different layer sets), so these shares are not independent trials; they say whether the DEV ranking carried information, not how many independent edges exist.

| DEV subset | cells | VAL mean > 0 | VAL beats same-phase random | median VAL mean | median VAL excess | median DEV mean |
|---|---|---|---|---|---|---|
| all cells | 8963 | 54.0% | 50.5% | 0.028 | 0.004 | 0.028 |
| DEV CI lower bound > 0 | 649 | 86.3% | 84.7% | 0.470 | 0.470 | 0.645 |
| DEV BH q < 0.05 | 29 | 100.0% | 100.0% | 0.225 | 0.358 | 0.527 |
| CI>0, dir = short | 44 | 72.7% | 61.4% | 0.158 | 0.107 | 0.439 |
| CI>0, dir = long | 605 | 87.3% | 86.4% | 0.522 | 0.496 | 0.665 |
| CI>0, exit = RIDE | 200 | 87.5% | 80.5% | 1.122 | 0.874 | 1.904 |
| CI>0, exit = T3R | 253 | 79.1% | 85.4% | 0.215 | 0.319 | 0.489 |
| CI>0, exit = TRAIL | 196 | 94.4% | 88.3% | 0.709 | 0.582 | 0.628 |
| CI>0, phase = UP_E | 562 | 91.1% | 89.9% | 0.584 | 0.534 | 0.686 |
| CI>0, phase = UP_L | 36 | 66.7% | 58.3% | 0.105 | 0.091 | 0.432 |
| CI>0, phase = MIX_E | 1 | 100.0% | 0.0% | 0.165 | -0.074 | 0.328 |
| CI>0, phase = MIX_L | 2 | 100.0% | 100.0% | 0.130 | 0.104 | 0.405 |
| CI>0, phase = DOWN_L | 48 | 43.8% | 45.8% | -0.044 | -0.082 | 0.521 |
| CI>0, tf = 1d | 257 | 93.0% | 92.2% | 0.789 | 0.760 | 0.876 |
| CI>0, tf = 4h | 392 | 81.9% | 79.8% | 0.316 | 0.312 | 0.554 |

Spearman rank correlation DEV mean vs VAL mean over all cells: 0.36 (partly shared drift). Cells with DEV CI low > 0 AND VAL mean > 0 AND VAL excess > 0: 529; they sit in long UP_E for all three exits and both timeframes, plus a handful of 4h cells (UP_L shorts, DOWN_L longs) that sit on thin counts.
Layers that appear most in DEV-CI>0 cells: VOLX 217, TREND_MA 199, RSI_MOM 194, ADX_DI 191, ABOVE_200 179, BRK5 171, BRK20 154, FUND_HI 104, NB_ABS 58, BB_SQZ 51 (VOLX, TREND_MA, RSI_MOM, ADX_DI, ABOVE_200, BRK5/BRK20 = trend continuation with participation). Flow layers (OI, funding, spot taker) rarely survive.
VAL same-phase random entries in UP_E earn +0.19 R (1d RIDE) and -0.10 R (1d T3R), so the family's VAL +0.4 to +1.2 R is an excess over drift, but two cycles (2020-21 and 2024-25) are two episodes.

## What this does and does not show

- Exhaustive over a fixed 26-layer bank with fixed thresholds; any layer, threshold or exit outside the bank (cost-basis VWAP of OI additions, weekly Cowen band, monthly low, top-trader ratio, options) was not searched.
- Trades run on SPOT prices with perp funding charged; the universe is a fixed list of 20 coins that still trade (survivorship). Entries before 2020-01-01 are not scored. The last 30-60 days are not scored (trades unresolved at the data end are dropped).
- Day-cluster errors treat each UTC day as one unit, pooling coins; coins move together, so independent episodes are fewer than the day count. VAL holds one regime sequence.
- BH tests each cell against ZERO (so it includes the drift of a bull market: 29 rejections, all long UP_E); the max-of-N placebo tests timing against random same-phase entries (null max t above the best DEV t, so no DEV cell stands out from the best of random timing once phase drift is removed at the t level).
- Deflation: BH over every enumerated cell and a max-of-N placebo in which each cell draws the same number of random same-phase entries (overlap rule not applied to the random draws; their variance is, if anything, overstated).
- Code frozen with PRE_REG (commit fae9d0840): miner.py, run.py, fetch.py, test_miner.py. After the run only these were added: make_result.py, diagnostics.py (post-run replication diagnostic), and a test comparing the simulator with an independent bar-by-bar reference (24 tests, all pass; the 2 causality tests fail under STUDY_BUG=1). results.json is the single run, no re-runs or parameter changes.
- Files: PRE_REG.md, fetch.py, miner.py, run.py, make_result.py, test_miner.py (causality test passes on the real code and fails under STUDY_BUG=1), results.json. Data: F:\MTS\data_cache\binance\combo-edge-miner-1114 (dev_cells.csv holds every DEV cell with n >= 100).
