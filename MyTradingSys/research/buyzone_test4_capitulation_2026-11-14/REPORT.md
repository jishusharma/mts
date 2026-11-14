# REPORT: Test 4, capitulation signature at lows (2026-11-13)

**Verdict: KILL: VAL h=7 12 bp mean R -0.077, CI [-0.234, 0.096], placebo any-day percentile 20.7, lows-like percentile 50.5, n = 221; DEV mean R 0.125 (n 127).**

Rules frozen in `PRE_REG.md` (committed before this run). Data: Binance spot daily + Bybit funding and 1d OI (public), host cache outside the repo. Rules are OURS unless marked SOURCED in the PRE_REG. Not a trade instruction.

Regime mix: signature events (7-day set) DEV 127 / VAL 221; UP 88, BASE 59, RANGE 36, DOWN 29, POSTPEAK_BEAR 136, NOPHASE 0 (per-split table below); no split flagged ONE-YEAR.

## Coverage
| Coin | OI first stamp | daily bars | last closed bar |
|---|---|---|---|
| BTC | 2020-08-05 | 3375 | 2026-11-12 |
| ETH | 2020-10-22 | 3375 | 2026-11-12 |
| BNB | 2021-06-30 | 3294 | 2026-11-12 |
| XRP | 2021-05-14 | 3115 | 2026-11-12 |
| ADA | 2021-03-19 | 3132 | 2026-11-12 |
| DOGE | 2021-06-03 | 2688 | 2026-11-12 |
| SOL | 2021-06-30 | 2285 | 2026-11-12 |
| LTC | 2020-10-22 | 3257 | 2026-11-12 |
| LINK | 2020-10-22 | 2858 | 2026-11-12 |
| TRX | 2021-08-18 | 3077 | 2026-11-12 |
| DOT | 2021-03-19 | 2278 | 2026-11-12 |
| AVAX | 2021-09-16 | 2243 | 2026-11-12 |
| ATOM | 2021-10-12 | 2755 | 2026-11-12 |
| ETC | 2021-06-30 | 3076 | 2026-11-12 |
| XLM | 2021-08-18 | 3088 | 2026-11-12 |
| BCH | 2020-12-15 | 2542 | 2026-11-12 |
| NEO | 2022-01-31 | 3280 | 2026-11-12 |
| UNI | 2021-03-19 | 2248 | 2026-11-12 |
| NEAR | 2021-10-12 | 2221 | 2026-11-12 |
| FIL | 2021-06-30 | 2220 | 2026-11-12 |
| ALGO | 2021-09-24 | 2701 | 2026-11-12 |
| VET | 2021-10-26 | 3033 | 2026-11-12 |

## Step 1a: lows (ex-post labelled, descriptive)
Lows population = k=10 swing lows after a >=25% fall from the 120-day high with funding and OI available: **1279 lows, 86 meet the full signature** (gate for Step 2 is >= 6).

All coins pooled:

| Group | n | med 1d | med 3d | med 7d | mean 7d | lower-low share <=26w (n eligible) | censored |
|---|---|---|---|---|---|---|---|
| ALL | 1279 | 2.4% | 4.7% | 7.1% | 9.1% | 81.1% (1183) | 96 |
| SIG (F+O+B) | 86 | 1.5% | 4.7% | 7.0% | 8.9% | 73.1% (78) | 8 |
| NOT-SIG | 1193 | 2.4% | 4.7% | 7.2% | 9.1% | 81.6% (1105) | 88 |
| F only-flag (funding<0) | 546 | 2.2% | 4.7% | 7.1% | 8.9% | 76.8% (487) | 59 |
| O (OI unwind) | 374 | 2.8% | 5.0% | 7.1% | 8.5% | 82.2% (348) | 26 |
| B (failed breakdown) | 864 | 2.2% | 5.1% | 7.8% | 10.3% | 81.0% (800) | 64 |
| F+O | 143 | 1.9% | 4.7% | 6.7% | 7.9% | 73.1% (130) | 13 |
| F+B | 347 | 1.9% | 5.2% | 7.7% | 10.3% | 78.1% (311) | 36 |
| O+B | 240 | 2.3% | 5.3% | 7.3% | 9.4% | 83.0% (224) | 16 |

BTC alone:

| Group | n | med 1d | med 3d | med 7d | mean 7d | lower-low share <=26w (n eligible) | censored |
|---|---|---|---|---|---|---|---|
| ALL | 37 | 2.2% | 2.8% | 4.6% | 6.4% | 68.6% (35) | 2 |
| SIG (F+O+B) | 0 | n/a | n/a | n/a | n/a | n/a (0) | 0 |
| NOT-SIG | 37 | 2.2% | 2.8% | 4.6% | 6.4% | 68.6% (35) | 2 |
| F only-flag (funding<0) | 10 | 1.8% | 4.5% | 5.7% | 7.5% | 66.7% (9) | 1 |
| O (OI unwind) | 6 | 3.3% | 6.8% | 4.5% | 5.8% | 66.7% (6) | 0 |
| B (failed breakdown) | 25 | 2.6% | 2.5% | 4.8% | 7.1% | 66.7% (24) | 1 |
| F+O | 3 | 3.7% | 7.9% | 4.6% | 6.3% | 33.3% (3) | 0 |
| F+B | 5 | 2.3% | 3.2% | 10.8% | 10.9% | 80.0% (5) | 0 |
| O+B | 2 | 6.3% | 5.9% | 7.6% | 7.6% | 100.0% (2) | 0 |

Lower-low share SIG 73.1% (n 78) vs NOT-SIG 81.6% (n 1105); Fisher exact p = n/a. Forward returns are from Close[L], where L is the ex-post low (not tradable; anatomy only). Partial-flag groups overlap.

## Step 1b: causal signature events (all days, lockout 10 bars)
Events kept at hold 1 / 3 / 7: 350 / 349 / 348 (dropped entry<=stop: {1: 0, 3: 0, 7: 0}). Year spread of the 7-day set: {2020: 1, 2021: 14, 2022: 71, 2023: 41, 2024: 36, 2025: 101, 2026: 84}.

Unstopped forward return from Open[s+1] to Close[s+h] (7-day kept set; descriptive):

| h | n | median | mean | win % net 12 bp | median net 12 bp |
|---|---|---|---|---|---|
| 1d | 348 | 0.0% | 0.0% | 48.3% | -0.1% |
| 3d | 348 | -0.1% | 0.1% | 48.0% | -0.2% |
| 7d | 348 | -0.8% | -0.5% | 45.4% | -0.9% |

Regime mix (events per phase, 7-day set):

| Split | n | UP | BASE | RANGE | DOWN | POSTPEAK_BEAR | NOPHASE | ONE-YEAR |
|---|---|---|---|---|---|---|---|---|
| DEV | 127 | 23 | 26 | 13 | 14 | 51 | 0 | no |
| VAL | 221 | 65 | 33 | 23 | 15 | 85 | 0 | no |
| ALL | 348 | 88 | 59 | 36 | 29 | 136 | 0 | no |

Today's state (reading only, never a sample): BTC last closed day 2026-11-12: funding mean 0.00006 (positive), OI 0.6% over 7d, OI at the 97.0th percentile of the prior 365 days.

## Step 2: fee-net trades of the causal signature (long, stop = failed-breakdown low - max(0.6 ATR, 0.5%))
Columns: n, win % at 12 bp, mean R 12 bp, mean R 6 bp, block-bootstrap 95% CI (12 bp), placebo percentile and band (12 bp; any day in the same phase / lows-like days in the same phase). Placebo 2000 draws, seed 1114. The placebo pool is restricted to days from the coin's first OI stamp + 7 days, where the signature can exist.

### hold 1 day (descriptive)
| Split | n | win | R 12bp | R 6bp | CI 12bp | placebo any-day | placebo lows-like |
|---|---|---|---|---|---|---|---|
| DEV | 127 | 44.1% | -0.033 | -0.027 | [-0.088, 0.019] | 28.6% (band -0.085..0.071) | 27.4% (band -0.085..0.083) |
| VAL | 223 | 50.2% | -0.000 | 0.007 | [-0.064, 0.065] | 72.0% (band -0.084..0.049) | 82.7% (band -0.092..0.035) |
| RECENT | 130 | 46.2% | -0.020 | -0.011 | [-0.111, 0.072] | 64.3% (band -0.114..0.054) | 72.0% (band -0.123..0.044) |
| ALL | 350 | 48.0% | -0.012 | -0.005 | [-0.057, 0.033] | 54.9% (band -0.063..0.044) | 62.9% (band -0.070..0.035) |

### hold 3 days (descriptive)
| Split | n | win | R 12bp | R 6bp | CI 12bp | placebo any-day | placebo lows-like |
|---|---|---|---|---|---|---|---|
| DEV | 127 | 45.7% | 0.045 | 0.050 | [-0.096, 0.198] | 84.8% (band -0.131..0.104) | 85.2% (band -0.134..0.102) |
| VAL | 222 | 46.8% | -0.014 | -0.006 | [-0.128, 0.106] | 51.5% (band -0.117..0.102) | 73.2% (band -0.137..0.060) |
| RECENT | 129 | 40.3% | -0.107 | -0.098 | [-0.241, 0.042] | 28.4% (band -0.195..0.094) | 33.0% (band -0.210..0.064) |
| ALL | 349 | 46.4% | 0.008 | 0.014 | [-0.082, 0.101] | 74.2% (band -0.095..0.073) | 85.5% (band -0.112..0.044) |

### hold 7 days (PRIMARY)
| Split | n | win | R 12bp | R 6bp | CI 12bp | placebo any-day | placebo lows-like |
|---|---|---|---|---|---|---|---|
| DEV | 127 | 43.3% | 0.125 | 0.130 | [-0.131, 0.425] | 95.5% (band -0.181..0.150) | 95.4% (band -0.181..0.156) |
| VAL | 221 | 40.7% | -0.077 | -0.070 | [-0.234, 0.096] | 20.7% (band -0.160..0.167) | 50.5% (band -0.202..0.063) |
| RECENT | 128 | 38.3% | -0.182 | -0.173 | [-0.374, 0.045] | 20.2% (band -0.276..0.093) | 33.9% (band -0.313..0.049) |
| ALL | 348 | 41.7% | -0.004 | 0.003 | [-0.145, 0.148] | 56.1% (band -0.128..0.118) | 79.0% (band -0.150..0.066) |

### hold 7, per phase (descriptive, no placebo)
| Phase | split | n | win | R 12bp | R 6bp | CI |
|---|---|---|---|---|---|---|
| UP | DEV | 23 (underpowered) | 39.1% | 0.099 | 0.105 | [-0.343, 0.626] |
| UP | VAL | 65 | 41.5% | -0.068 | -0.061 | [-0.280, 0.198] |
| BASE | DEV | 26 (underpowered) | 30.8% | -0.164 | -0.158 | [-0.483, 0.254] |
| BASE | VAL | 33 | 42.4% | -0.106 | -0.100 | [-0.440, 0.243] |
| RANGE | DEV | 13 (underpowered) | 30.8% | 0.446 | 0.450 | [-0.322, 1.905] |
| RANGE | VAL | 23 (underpowered) | 43.5% | 0.024 | 0.034 | [-0.403, 0.416] |
| DOWN | DEV | 14 (underpowered) | 35.7% | 0.128 | 0.135 | [-0.378, 0.741] |
| DOWN | VAL | 15 (underpowered) | 46.7% | 0.059 | 0.069 | [-0.423, 0.489] |
| POSTPEAK_BEAR | DEV | 51 | 56.9% | 0.200 | 0.206 | [-0.174, 0.692] |
| POSTPEAK_BEAR | VAL | 85 | 37.6% | -0.125 | -0.117 | [-0.392, 0.193] |
| NOPHASE | DEV | 0 | | | | |
| NOPHASE | VAL | 0 | | | | |

### hold 7, per coin, all splits (descriptive)
| Coin | n | win | R 12bp |
|---|---|---|---|
| BTC | 5 | 20.0% | -0.637 |
| ETH | 10 | 40.0% | -0.200 |
| BNB | 27 | 48.1% | -0.075 |
| XRP | 22 | 27.3% | -0.204 |
| ADA | 25 | 40.0% | -0.157 |
| DOGE | 17 | 35.3% | -0.053 |
| SOL | 15 | 40.0% | -0.060 |
| LTC | 9 | 66.7% | -0.183 |
| LINK | 14 | 35.7% | -0.058 |
| TRX | 27 | 51.9% | 0.378 |
| DOT | 10 | 30.0% | -0.365 |
| AVAX | 21 | 42.9% | -0.079 |
| ATOM | 16 | 37.5% | -0.096 |
| ETC | 19 | 26.3% | 0.264 |
| XLM | 21 | 38.1% | -0.114 |
| BCH | 23 | 60.9% | 0.529 |
| NEO | 12 | 50.0% | 0.032 |
| UNI | 15 | 46.7% | 0.110 |
| NEAR | 13 | 30.8% | -0.323 |
| FIL | 8 | 25.0% | -0.583 |
| ALGO | 13 | 38.5% | -0.152 |
| VET | 6 | 83.3% | 1.546 |
