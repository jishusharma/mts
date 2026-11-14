# RESULT: bear-trap reclaim LONG (prior day / week low), 1h Bybit, 20 coins, downtrend filter vs control (2026-11-14)

Regime mix: 52.3 % of the 14300 sweep-reclaim events (PDL+PWL, per target-1R record) fire in the downtrend filter (coin close < falling SMA20, or BTC 3 red weeks) against 48.0 % of all hourly bars; by year share of events in the filter: 2020 27 %, 2021 43 %, 2022 62 %, 2023 48 %, 2024 45 %, 2025 54 %, 2026 59 %. Flush OI known for 14268 events, 4123 of them with OI down >= 1 %.

**VERDICT: FAIL on all 24 rows. No long bear-trap reclaim edge fee-net, with or without the downtrend filter or the OI flush.** Every VALIDATION mean R is negative (-0.04 to -0.15 R); no row passes the CI, placebo or BH gates; averaged over rows the downtrend filter lifts VAL mean R by only ~+0.01 to +0.02 versus control (-0.115 vs -0.135 none-OI; -0.073 vs -0.085 flush) and the OI flush by ~+0.04 versus no-flush; DEV downtrend mean is ~0.00 R. Gross edge is about zero; the 12 bp cost (~0.08 R) makes it negative.

Rules, split, costs, placebo, gates exactly as frozen in PRE_REG.md (committed before any outcome; nothing tuned). Fee-net: 12 bp round trip (taker 5 bp x2 from fees.py + 2 bp slippage), no funding. 15m not used (see PRE_REG), ties = stop. Data: Bybit v5 linear 1h, 20 coins (first bars 2020-03 BTC .. 2021-12 UNI), OI 1h from 2020-07. CI = 95 % bootstrap; day-cluster = UTC entry date. Placebo = random entry, same coin/hour/hold/R-width/cost (downtrend rows: flagged bars only), VALIDATION period, 2000 draws.

| row (level target filter OI) | trades DEV/VAL | win rate VAL | mean R VAL | CI per-trade | CI day-cluster | placebo p | w/o best 5 days | verdict |
|---|---|---|---|---|---|---|---|---|
| PDL 1R downtrend none | 3007 / 3384 | 49.3 % | -0.111 | [-0.145, -0.078] | [-0.178, -0.044] | 0.757 | -0.138 | FAIL |
| PDL 1R downtrend flush | 915 / 584 | 48.8 % | -0.093 | [-0.172, -0.012] | [-0.208, +0.015] | 0.644 | -0.156 | FAIL |
| PDL 1R control none | 5957 / 6625 | 48.5 % | -0.129 | [-0.152, -0.104] | [-0.176, -0.081] | 0.987 | -0.144 | FAIL |
| PDL 1R control flush | 2134 / 1387 | 49.0 % | -0.094 | [-0.145, -0.045] | [-0.167, -0.019] | 0.776 | -0.131 | FAIL |
| PDL 2R downtrend none | 3007 / 3384 | 37.6 % | -0.111 | [-0.152, -0.067] | [-0.193, -0.021] | 0.685 | -0.151 | FAIL |
| PDL 2R downtrend flush | 915 / 584 | 39.2 % | -0.075 | [-0.172, +0.025] | [-0.205, +0.068] | 0.511 | -0.158 | FAIL |
| PDL 2R control none | 5957 / 6625 | 36.0 % | -0.137 | [-0.167, -0.107] | [-0.200, -0.071] | 0.983 | -0.162 | FAIL |
| PDL 2R control flush | 2134 / 1387 | 38.6 % | -0.074 | [-0.141, -0.009] | [-0.171, +0.023] | 0.592 | -0.120 | FAIL |
| PDL PDH downtrend none | 2993 / 3371 | 34.6 % | -0.138 | [-0.189, -0.089] | [-0.241, -0.039] | 0.879 | -0.188 | FAIL |
| PDL PDH downtrend flush | 910 / 583 | 39.1 % | -0.036 | [-0.159, +0.084] | [-0.192, +0.119] | 0.286 | -0.136 | FAIL |
| PDL PDH control none | 5928 / 6600 | 33.1 % | -0.143 | [-0.179, -0.105] | [-0.217, -0.064] | 0.980 | -0.177 | FAIL |
| PDL PDH control flush | 2122 / 1382 | 37.4 % | -0.071 | [-0.144, +0.006] | [-0.178, +0.030] | 0.584 | -0.121 | FAIL |
| PWL 1R downtrend none | 504 / 590 | 47.1 % | -0.146 | [-0.222, -0.073] | [-0.255, -0.038] | 0.911 | -0.196 | FAIL |
| PWL 1R downtrend flush | 210 / 134 | 50.7 % | -0.076 | [-0.233, +0.088] | [-0.251, +0.094] | 0.562 | -0.178 | FAIL |
| PWL 1R control none | 774 / 944 | 46.7 % | -0.151 | [-0.211, -0.092] | [-0.240, -0.065] | 0.967 | -0.188 | FAIL |
| PWL 1R control flush | 358 / 244 | 50.0 % | -0.073 | [-0.188, +0.045] | [-0.211, +0.061] | 0.568 | -0.143 | FAIL |
| PWL 2R downtrend none | 504 / 590 | 39.5 % | -0.103 | [-0.204, +0.003] | [-0.236, +0.028] | 0.662 | -0.185 | FAIL |
| PWL 2R downtrend flush | 210 / 134 | 44.0 % | -0.065 | [-0.259, +0.132] | [-0.269, +0.137] | 0.495 | -0.170 | FAIL |
| PWL 2R control none | 774 / 944 | 37.7 % | -0.132 | [-0.208, -0.053] | [-0.246, -0.019] | 0.874 | -0.192 | FAIL |
| PWL 2R control flush | 358 / 244 | 41.8 % | -0.079 | [-0.221, +0.067] | [-0.236, +0.086] | 0.608 | -0.160 | FAIL |
| PWL PDH downtrend none | 503 / 589 | 38.0 % | -0.082 | [-0.194, +0.024] | [-0.256, +0.102] | 0.520 | -0.204 | FAIL |
| PWL PDH downtrend flush | 209 / 134 | 43.3 % | -0.092 | [-0.290, +0.130] | [-0.303, +0.117] | 0.581 | -0.231 | FAIL |
| PWL PDH control none | 773 / 943 | 36.1 % | -0.121 | [-0.213, -0.025] | [-0.259, +0.022] | 0.793 | -0.202 | FAIL |
| PWL PDH control flush | 357 / 244 | 39.8 % | -0.120 | [-0.269, +0.029] | [-0.294, +0.063] | 0.731 | -0.225 | FAIL |

DEV (descriptive) mean R per row is in results_table.csv (mean_dev, win_dev); all rows are also reported there with n DEV.

## Tests
`python test_study.py`: 7 tests pass (entry at next bar open, 0.1 % sweep, 6-bar reclaim window, stop-first tie/gap, cost in R, trend flag uses only completed days, BTC 3-red-week flag). With the deliberately wrong version `ENTRY_OFFSET = 0` (entry at the reclaim bar, one-bar look-ahead) the entry test FAILS (checked, reverted).

## Caveats
- Hourly bars only: intrabar order of stop vs target unknown, ties resolved to the stop (pessimistic); stops fill at the stop price (no extra slippage).
- Trades overlap across coins on the same days (crypto beta); day-cluster CI is the conservative view.
- Events are one per level per period (first sweep only); events whose 24 h window is cut by data end are dropped.
- Flush rows use OI snapshots at the sweep-bar and reclaim-bar starts (timestamp semantics assumed to be snapshot at that time; reclaim bar itself excluded).
- A FAIL here is for these exact rules; shorts, 15m, maker entries, other levels, regime-conditional exits are untested.
