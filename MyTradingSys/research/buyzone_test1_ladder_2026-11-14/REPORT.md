# REPORT: Test 1, causal confirmation ladder, long side

Rules frozen in `PRE_REG.md` (committed before any outcome). Data: Binance spot daily, host cache, not committed. Code: `ladder.py`, `run_test1.py`, tests `test_ladder.py`. Nothing here is a trade instruction.

## Coverage and regime mix (share of coin-days per phase per split, post warm-up)

| coin | bars | first day |
|---|---|---|
| BTC | 3375 | 2017-08-17 |
| ETH | 3375 | 2017-08-17 |
| BNB | 3294 | 2017-11-06 |
| XRP | 3115 | 2018-05-04 |
| ADA | 3132 | 2018-04-17 |
| DOGE | 2688 | 2019-07-05 |
| SOL | 2285 | 2020-08-11 |
| LTC | 3257 | 2017-12-13 |
| LINK | 2858 | 2019-01-16 |
| TRX | 3077 | 2018-06-11 |
| DOT | 2278 | 2020-08-18 |
| AVAX | 2243 | 2020-09-22 |
| ATOM | 2755 | 2019-04-29 |
| ETC | 3076 | 2018-06-12 |
| XLM | 3088 | 2018-05-31 |
| BCH | 2542 | 2019-11-28 |
| NEO | 3280 | 2017-11-20 |
| UNI | 2248 | 2020-09-17 |
| NEAR | 2221 | 2020-10-14 |
| FIL | 2220 | 2020-10-15 |
| ALGO | 2701 | 2019-06-22 |
| VET | 3033 | 2018-07-25 |

| split | UP | BASE | RANGE | DOWN | POSTPEAK_BEAR |
|---|---|---|---|---|---|
| DEV | 34.5% | 17.6% | 8.0% | 7.4% | 32.4% |
| VAL | 32.4% | 12.2% | 12.4% | 9.4% | 33.6% |

## Candidate A HL_BREAK (PRIMARY)

Events kept after lockout: 563; dropped for entry <= stop: 0; with a phase label: 563.

### Pooled by phase group and split (mean R fee-net; placebo = 2000 same-coin same-phase same-stop draws)

| group | split | n | win % | mean R 12bp | mean R 6bp | 95% CI (12bp) | placebo pct (12bp) |
|---|---|---|---|---|---|---|---|
| UP+BASE (claim) | DEV | 195 | 44% | 0.208 | 0.211 | [0.04, 0.38] | 82.7% (band -0.006..0.304; 6bp pct 82.7%) |
| UP+BASE (claim) | VAL | 97 | 38% | 0.037 | 0.041 | [-0.15, 0.21] | 80.8% (band -0.190..0.162; 6bp pct 80.8%) |
| UP+BASE (claim) | RECENT | 20 | 45% | 0.118 | 0.124 | [-0.14, 0.25] | 80.5% (band -0.300..0.329; 6bp pct 80.5%) |
| UP+BASE (claim) | ALL | 292 | 42% | 0.151 | 0.155 | [0.02, 0.28] | 88.8% (band -0.044..0.208; 6bp pct 88.8%) |
| UP | DEV | 163 | 47% | 0.242 | 0.245 | [0.06, 0.42] | 87.0% (band -0.025..0.335; 6bp pct 87.0%) |
| UP | VAL | 90 | 39% | 0.051 | 0.056 | [-0.14, 0.23] | 83.8% (band -0.193..0.218; 6bp pct 83.8%) |
| UP | RECENT | 16 | 44% | 0.123 | 0.130 | [-0.23, 0.30] | 84.9% (band -0.373..0.320; 6bp pct 84.8%) |
| UP | ALL | 253 | 44% | 0.174 | 0.177 | [0.03, 0.32] | 91.6% (band -0.057..0.225; 6bp pct 91.6%) |
| BASE | DEV | 32 | 28% | 0.038 | 0.041 | [-0.22, 0.39] | 31.1% (band -0.159..0.473; 6bp pct 31.1%) |
| BASE | VAL | 7 | 29% | -0.153 | -0.150 | [-0.51, 0.05] | 35.2% (band -0.460..0.425; 6bp pct 35.2%) |
| BASE | RECENT | 4 | 50% | 0.097 | 0.101 | [0.04, 0.16] | 43.9% (band -0.462..0.817; 6bp pct 43.9%) |
| BASE | ALL | 39 | 28% | 0.004 | 0.007 | [-0.21, 0.28] | 35.4% (band -0.181..0.368; 6bp pct 35.4%) |
| RANGE | DEV | 39 | 38% | 0.132 | 0.135 | [-0.14, 0.37] | 44.9% (band -0.085..0.409; 6bp pct 44.9%) |
| RANGE | VAL | 40 | 35% | 0.065 | 0.069 | [-0.13, 0.20] | 53.0% (band -0.170..0.338; 6bp pct 53.0%) |
| RANGE | RECENT | 13 | 38% | 0.063 | 0.069 | [-0.30, 0.46] | 63.1% (band -0.353..0.483; 6bp pct 63.1%) |
| RANGE | ALL | 79 | 37% | 0.098 | 0.101 | [-0.06, 0.23] | 52.8% (band -0.077..0.278; 6bp pct 52.8%) |
| DOWN | DEV | 22 | 41% | 0.061 | 0.064 | [-0.19, 0.40] | 57.6% (band -0.201..0.326; 6bp pct 57.6%) |
| DOWN | VAL | 25 | 28% | -0.144 | -0.140 | [-0.31, -0.08] | 9.2% (band -0.208..0.446; 6bp pct 9.2%) |
| DOWN | RECENT | 4 | 25% | -0.254 | -0.247 | [-0.46, -0.13] | 20.5% (band -0.481..0.306; 6bp pct 20.5%) |
| DOWN | ALL | 47 | 34% | -0.048 | -0.045 | [-0.18, 0.13] | 21.0% (band -0.162..0.315; 6bp pct 21.0%) |
| POSTPEAK_BEAR | DEV | 98 | 34% | 0.016 | 0.019 | [-0.17, 0.28] | 48.2% (band -0.119..0.174; 6bp pct 48.2%) |
| POSTPEAK_BEAR | VAL | 47 | 43% | 0.072 | 0.076 | [-0.16, 0.29] | 66.8% (band -0.168..0.266; 6bp pct 66.8%) |
| POSTPEAK_BEAR | RECENT | 38 | 39% | 0.057 | 0.061 | [-0.20, 0.30] | 66.3% (band -0.208..0.258; 6bp pct 66.3%) |
| POSTPEAK_BEAR | ALL | 145 | 37% | 0.034 | 0.038 | [-0.12, 0.22] | 53.2% (band -0.088..0.167; 6bp pct 53.2%) |

### Per coin, UP+BASE (n<30 per cell is UNDERPOWERED; no verdict from a coin)

| coin | split | n | win % | mean R 12bp | mean R 6bp |
|---|---|---|---|---|---|
| BTC | DEV | 15 (under) | 27% | 0.064 | 0.068 |
| BTC | VAL | 8 (under) | 50% | 0.527 | 0.534 |
| BTC | RECENT | 2 (under) | 50% | -0.085 | -0.072 |
| BTC | ALL | 23 (under) | 35% | 0.225 | 0.230 |
| ETH | DEV | 19 (under) | 58% | 0.327 | 0.331 |
| ETH | VAL | 5 (under) | 60% | 0.034 | 0.038 |
| ETH | RECENT | 1 (under) | 100% | 0.095 | 0.100 |
| ETH | ALL | 24 (under) | 58% | 0.266 | 0.270 |
| BNB | DEV | 18 (under) | 44% | 0.136 | 0.139 |
| BNB | VAL | 9 (under) | 67% | 0.409 | 0.414 |
| BNB | RECENT | 3 (under) | 67% | 0.592 | 0.598 |
| BNB | ALL | 27 (under) | 52% | 0.227 | 0.231 |
| XRP | DEV | 4 (under) | 50% | 0.310 | 0.313 |
| XRP | VAL | 1 (under) | 100% | 1.048 | 1.051 |
| XRP | ALL | 5 (under) | 60% | 0.458 | 0.461 |
| ADA | DEV | 12 (under) | 58% | 0.540 | 0.543 |
| ADA | VAL | 3 (under) | 67% | 0.188 | 0.191 |
| ADA | ALL | 15 (under) | 60% | 0.470 | 0.472 |
| DOGE | DEV | 11 (under) | 55% | 0.210 | 0.212 |
| DOGE | VAL | 4 (under) | 0% | -0.361 | -0.358 |
| DOGE | ALL | 15 (under) | 40% | 0.058 | 0.060 |
| SOL | DEV | 4 (under) | 25% | 0.304 | 0.306 |
| SOL | VAL | 3 (under) | 67% | 0.154 | 0.157 |
| SOL | RECENT | 1 (under) | 100% | 0.404 | 0.408 |
| SOL | ALL | 7 (under) | 43% | 0.239 | 0.242 |
| LTC | DEV | 13 (under) | 46% | 0.175 | 0.178 |
| LTC | ALL | 13 (under) | 46% | 0.175 | 0.178 |
| LINK | DEV | 13 (under) | 46% | 0.043 | 0.045 |
| LINK | VAL | 3 (under) | 0% | -0.269 | -0.267 |
| LINK | RECENT | 1 (under) | 0% | -0.345 | -0.343 |
| LINK | ALL | 16 (under) | 38% | -0.016 | -0.013 |
| TRX | DEV | 11 (under) | 73% | 0.318 | 0.322 |
| TRX | VAL | 15 (under) | 27% | -0.200 | -0.191 |
| TRX | RECENT | 4 (under) | 0% | -0.296 | -0.285 |
| TRX | ALL | 26 (under) | 46% | 0.019 | 0.026 |
| DOT | DEV | 3 (under) | 0% | -0.170 | -0.167 |
| DOT | VAL | 3 (under) | 33% | -0.061 | -0.058 |
| DOT | ALL | 6 (under) | 17% | -0.116 | -0.113 |
| AVAX | DEV | 4 (under) | 75% | 0.277 | 0.279 |
| AVAX | VAL | 4 (under) | 25% | -0.234 | -0.231 |
| AVAX | RECENT | 1 (under) | 100% | 0.344 | 0.347 |
| AVAX | ALL | 8 (under) | 50% | 0.022 | 0.024 |
| ATOM | DEV | 10 (under) | 30% | -0.213 | -0.211 |
| ATOM | VAL | 4 (under) | 0% | -0.263 | -0.259 |
| ATOM | RECENT | 1 (under) | 0% | -0.092 | -0.086 |
| ATOM | ALL | 14 (under) | 21% | -0.227 | -0.225 |
| ETC | DEV | 8 (under) | 75% | 0.924 | 0.926 |
| ETC | VAL | 5 (under) | 20% | -0.218 | -0.215 |
| ETC | ALL | 13 (under) | 54% | 0.485 | 0.487 |
| XLM | DEV | 6 (under) | 50% | 0.152 | 0.154 |
| XLM | VAL | 3 (under) | 0% | -0.341 | -0.339 |
| XLM | RECENT | 1 (under) | 0% | -0.314 | -0.312 |
| XLM | ALL | 9 (under) | 33% | -0.012 | -0.010 |
| BCH | DEV | 7 (under) | 14% | 0.158 | 0.161 |
| BCH | VAL | 5 (under) | 40% | 0.400 | 0.403 |
| BCH | RECENT | 1 (under) | 0% | -0.368 | -0.365 |
| BCH | ALL | 12 (under) | 25% | 0.259 | 0.262 |
| NEO | DEV | 9 (under) | 33% | 0.359 | 0.361 |
| NEO | VAL | 4 (under) | 25% | -0.221 | -0.218 |
| NEO | ALL | 13 (under) | 31% | 0.180 | 0.183 |
| UNI | DEV | 2 (under) | 0% | -0.427 | -0.423 |
| UNI | VAL | 5 (under) | 80% | 0.342 | 0.344 |
| UNI | RECENT | 1 (under) | 100% | 0.599 | 0.601 |
| UNI | ALL | 7 (under) | 57% | 0.122 | 0.125 |
| NEAR | DEV | 2 (under) | 50% | 0.222 | 0.223 |
| NEAR | VAL | 4 (under) | 50% | 0.337 | 0.339 |
| NEAR | RECENT | 3 (under) | 67% | 0.538 | 0.540 |
| NEAR | ALL | 6 (under) | 50% | 0.298 | 0.301 |
| FIL | DEV | 3 (under) | 33% | 0.169 | 0.172 |
| FIL | VAL | 3 (under) | 33% | -0.107 | -0.105 |
| FIL | ALL | 6 (under) | 33% | 0.031 | 0.034 |
| ALGO | DEV | 9 (under) | 22% | 0.122 | 0.124 |
| ALGO | VAL | 5 (under) | 40% | -0.094 | -0.091 |
| ALGO | ALL | 14 (under) | 29% | 0.045 | 0.047 |
| VET | DEV | 12 (under) | 33% | 0.093 | 0.096 |
| VET | VAL | 1 (under) | 0% | -0.446 | -0.444 |
| VET | ALL | 13 (under) | 31% | 0.052 | 0.054 |

VAL long-phase events by year: {'2024': 59, '2025': 28, '2026': 10}; largest-year share 61% -> not one-year
VAL long-phase events by coin: {'TRX': 15, 'BNB': 9, 'BTC': 8, 'ETH': 5, 'ETC': 5, 'BCH': 5, 'UNI': 5, 'ALGO': 5, 'DOGE': 4, 'AVAX': 4, 'ATOM': 4, 'NEO': 4, 'NEAR': 4, 'ADA': 3, 'SOL': 3, 'LINK': 3, 'DOT': 3, 'XLM': 3, 'FIL': 3, 'XRP': 1, 'VET': 1}

**VERDICT A: KILL: VAL n=97 meanR12=0.037 CI[-0.148, 0.213] placebo pct=80.8 (97.5th=0.162) DEV n=195 meanR12=0.208**

## Candidate B BULL_DIV (SECONDARY)

Events kept after lockout: 57; dropped for entry <= stop: 0; with a phase label: 57.

### Pooled by phase group and split (mean R fee-net; placebo = 2000 same-coin same-phase same-stop draws)

| group | split | n | win % | mean R 12bp | mean R 6bp | 95% CI (12bp) | placebo pct (12bp) |
|---|---|---|---|---|---|---|---|
| UP+BASE (claim) | DEV | 7 | 57% | 0.092 | 0.095 | [-0.28, 0.53] | 61.8% (band -0.366..1.332; 6bp pct 61.8%) |
| UP+BASE (claim) | VAL | 9 | 33% | -0.100 | -0.098 | [-0.31, 0.09] | 52.0% (band -0.311..0.192; 6bp pct 52.0%) |
| UP+BASE (claim) | RECENT | 3 | 33% | -0.184 | -0.181 | [-0.57, 0.32] | 21.8% (band -0.350..0.437; 6bp pct 21.8%) |
| UP+BASE (claim) | ALL | 16 | 44% | -0.016 | -0.013 | [-0.22, 0.22] | 56.1% (band -0.256..0.446; 6bp pct 56.1%) |
| UP | DEV | 4 | 75% | 0.068 | 0.070 | [-0.26, 0.29] | 57.6% (band -0.491..2.262; 6bp pct 57.6%) |
| UP | VAL | 6 | 33% | -0.078 | -0.076 | [-0.31, 0.12] | 64.3% (band -0.373..0.247; 6bp pct 64.3%) |
| UP | RECENT | 1 | 0% | -0.307 | -0.305 | [-0.31, -0.31] | 13.2% (band -0.414..0.316; 6bp pct 13.2%) |
| UP | ALL | 10 | 50% | -0.019 | -0.017 | [-0.18, 0.16] | 59.4% (band -0.334..0.591; 6bp pct 59.4%) |
| BASE | DEV | 3 | 33% | 0.125 | 0.127 | [-0.63, 1.19] | 71.0% (band -0.493..0.787; 6bp pct 71.0%) |
| BASE | VAL | 3 | 33% | -0.144 | -0.142 | [-0.57, 0.32] | 38.2% (band -0.389..0.466; 6bp pct 38.2%) |
| BASE | RECENT | 2 | 50% | -0.122 | -0.120 | [-0.57, 0.32] | 35.8% (band nan..nan; 6bp pct 35.7%) |
| BASE | ALL | 6 | 33% | -0.010 | -0.007 | [-0.45, 0.52] | 53.5% (band -0.342..0.462; 6bp pct 53.5%) |
| RANGE | DEV | 0 | | | | |  |
| RANGE | VAL | 1 | 100% | 0.477 | 0.483 | [0.48, 0.48] | 68.7% (band nan..nan; 6bp pct 68.7%) |
| RANGE | RECENT | 1 | 100% | 0.477 | 0.483 | [0.48, 0.48] | 67.5% (band nan..nan; 6bp pct 67.5%) |
| RANGE | ALL | 1 | 100% | 0.477 | 0.483 | [0.48, 0.48] | 71.7% (band nan..nan; 6bp pct 71.7%) |
| DOWN | DEV | 4 | 50% | 0.069 | 0.071 | [-0.06, 0.15] | 59.2% (band -0.380..0.660; 6bp pct 59.2%) |
| DOWN | VAL | 3 | 33% | -0.173 | -0.171 | [-0.32, -0.10] | 16.3% (band -0.280..0.671; 6bp pct 16.3%) |
| DOWN | RECENT | 0 | | | | |  |
| DOWN | ALL | 7 | 43% | -0.035 | -0.033 | [-0.19, 0.09] | 44.3% (band -0.265..0.368; 6bp pct 44.3%) |
| POSTPEAK_BEAR | DEV | 21 | 33% | 0.068 | 0.071 | [-0.17, 0.36] | 66.3% (band -0.265..0.373; 6bp pct 66.3%) |
| POSTPEAK_BEAR | VAL | 12 | 42% | -0.059 | -0.056 | [-0.22, 0.08] | 46.9% (band -0.301..0.345; 6bp pct 46.9%) |
| POSTPEAK_BEAR | RECENT | 7 | 57% | -0.037 | -0.033 | [-0.30, 0.16] | 64.2% (band -0.463..0.478; 6bp pct 64.2%) |
| POSTPEAK_BEAR | ALL | 33 | 36% | 0.022 | 0.024 | [-0.14, 0.22] | 53.8% (band -0.193..0.294; 6bp pct 53.8%) |

### Per coin, UP+BASE (n<30 per cell is UNDERPOWERED; no verdict from a coin)

| coin | split | n | win % | mean R 12bp | mean R 6bp |
|---|---|---|---|---|---|
| BTC | DEV | 1 (under) | 0% | -0.188 | -0.184 |
| BTC | ALL | 1 (under) | 0% | -0.188 | -0.184 |
| BNB | DEV | 1 (under) | 100% | 0.305 | 0.307 |
| BNB | ALL | 1 (under) | 100% | 0.305 | 0.307 |
| DOGE | DEV | 1 (under) | 100% | 0.126 | 0.129 |
| DOGE | ALL | 1 (under) | 100% | 0.126 | 0.129 |
| SOL | VAL | 1 (under) | 100% | 0.309 | 0.311 |
| SOL | ALL | 1 (under) | 100% | 0.309 | 0.311 |
| LINK | DEV | 1 (under) | 100% | 0.278 | 0.280 |
| LINK | ALL | 1 (under) | 100% | 0.278 | 0.280 |
| DOT | VAL | 1 (under) | 0% | -0.384 | -0.381 |
| DOT | ALL | 1 (under) | 0% | -0.384 | -0.381 |
| AVAX | VAL | 2 (under) | 50% | 0.007 | 0.009 |
| AVAX | RECENT | 1 (under) | 100% | 0.324 | 0.326 |
| AVAX | ALL | 2 (under) | 50% | 0.007 | 0.009 |
| BCH | DEV | 1 (under) | 0% | -0.438 | -0.435 |
| BCH | VAL | 2 (under) | 0% | -0.185 | -0.184 |
| BCH | RECENT | 1 (under) | 0% | -0.307 | -0.305 |
| BCH | ALL | 3 (under) | 0% | -0.270 | -0.268 |
| UNI | DEV | 1 (under) | 0% | -0.627 | -0.625 |
| UNI | VAL | 1 (under) | 100% | 0.290 | 0.292 |
| UNI | ALL | 2 (under) | 50% | -0.169 | -0.166 |
| ALGO | VAL | 2 (under) | 0% | -0.378 | -0.376 |
| ALGO | RECENT | 1 (under) | 0% | -0.568 | -0.566 |
| ALGO | ALL | 2 (under) | 0% | -0.378 | -0.376 |
| VET | DEV | 1 (under) | 100% | 1.189 | 1.190 |
| VET | ALL | 1 (under) | 100% | 1.189 | 1.190 |

VAL long-phase events by year: {'2024': 5, '2025': 3, '2026': 1}; largest-year share 56% -> not one-year
VAL long-phase events by coin: {'AVAX': 2, 'BCH': 2, 'ALGO': 2, 'SOL': 1, 'DOT': 1, 'UNI': 1}

**VERDICT B: UNDERPOWERED (VAL n=9 < 30), no claim**
(Secondary: two tests run, multiplicity noted; a B-only PASS needs independent replication before any use.)

## Reading (hand-added after the run; the numbers above are generated)
- A (PRIMARY): KILL. VAL UP+BASE n=97, mean R 12bp +0.037, CI [-0.15, 0.21], placebo percentile 80.8 (band top 0.162). DEV is +0.208 (n=195, CI above 0, placebo 82.7) but never beat its placebo band either; the DEV-to-VAL drop is the usual shrink. Mean R is near flat in the 12bp-to-6bp step because the stop sits far below entry (median risk about 15-20%), so the fee is a small share of R.
- Control: DOWN VAL is negative (-0.144, CI [-0.31, -0.08]), as expected; RANGE and POSTPEAK_BEAR show no edge over placebo. The phase gate separates losers from non-losers but the entry adds nothing over same-phase random entries.
- B (SECONDARY): UNDERPOWERED, VAL n=9 (57 events total in 22 coins). No claim.
- Deviations (all OURS, logged as DECISION): `F:/MTS/data_cache` absent on this host, so Binance spot daily klines were fetched into `C:/Users/e-ngineers/MTS_data_cache/binance_spot_1d` (not committed). WaveTrend not used. Bybit funding not needed (spot long). RECENT (2025-07-01+) is a subset of VAL.
- Multiplicity: 2 candidates tested; A carries the verdict. Test file mutations (trailing level including the current bar; confirming close before the pivot is known) each fail a test.
