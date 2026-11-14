Regime mix: VALIDATION 150 weeks: bull 84 (56%) | bear 46 (31%) | range 20 (13%) | n/a 0 (0%) (BTC weekly close vs 200d SMA +-5 %)

Verdict: FAIL / no edge. 0 of 24 cells PASS (VALIDATION fee-net mean R > 0, day-clustered CI lower > 0, n >= 30, placebo p <= 0.05, BH 10 %).

Regime mix DEV: 197 weeks: bull 89 (45%) | bear 66 (34%) | range 14 (7%) | n/a 28 (14%) | RECENT: 71 weeks: bull 26 (37%) | bear 39 (55%) | range 6 (8%) | n/a 0 (0%)
Costs: 2 x BINANCE_TAKER + SLIPPAGE_RT_S13 = 12.00 bp round trip, charged on entry, converted to R. Data end 2026-11-13 18:00 UTC. 20 Bybit USDT perps, 1h; 4h folded.

| cell | n DEV | n VAL | mean R VAL | CI (day-cluster) | CI (per-trade) | placebo (mean, p) | BH | verdict |
|---|---|---|---|---|---|---|---|---|
| R03_1h_W12_1R | 5226 | 6181 | -0.246 | [-0.284, -0.207] | [-0.272, -0.221] | -0.304, 0.000 | no | FAIL |
| R03_1h_W12_2R | 5226 | 6181 | -0.221 | [-0.274, -0.165] | [-0.254, -0.187] | -0.289, 0.000 | no | FAIL |
| R03_1h_W12_T12 | 5226 | 6181 | -0.216 | [-0.299, -0.123] | [-0.268, -0.163] | -0.314, 0.000 | no | FAIL |
| R03_1h_W18_1R | 5247 | 6200 | -0.247 | [-0.286, -0.212] | [-0.272, -0.221] | -0.304, 0.000 | no | FAIL |
| R03_1h_W18_2R | 5247 | 6200 | -0.221 | [-0.275, -0.168] | [-0.254, -0.186] | -0.288, 0.000 | no | FAIL |
| R03_1h_W18_T12 | 5247 | 6200 | -0.217 | [-0.305, -0.128] | [-0.269, -0.162] | -0.314, 0.000 | no | FAIL |
| R04_1h_W12_1R | 5247 | 6319 | -0.223 | [-0.265, -0.180] | [-0.247, -0.197] | -0.299, 0.000 | no | FAIL |
| R04_1h_W12_2R | 5247 | 6319 | -0.245 | [-0.302, -0.184] | [-0.277, -0.214] | -0.308, 0.000 | no | FAIL |
| R04_1h_W12_T12 | 5247 | 6319 | -0.223 | [-0.312, -0.128] | [-0.273, -0.174] | -0.314, 0.000 | no | FAIL |
| R04_1h_W18_1R | 5264 | 6336 | -0.222 | [-0.261, -0.179] | [-0.245, -0.198] | -0.302, 0.000 | no | FAIL |
| R04_1h_W18_2R | 5264 | 6336 | -0.243 | [-0.298, -0.184] | [-0.276, -0.213] | -0.309, 0.000 | no | FAIL |
| R04_1h_W18_T12 | 5264 | 6336 | -0.221 | [-0.306, -0.130] | [-0.269, -0.173] | -0.318, 0.000 | no | FAIL |
| R03_4h_W12_1R | 1289 | 1364 | -0.054 | [-0.122, +0.017] | [-0.105, -0.004] | -0.244, 0.000 | no | FAIL |
| R03_4h_W12_2R | 1289 | 1364 | -0.003 | [-0.096, +0.098] | [-0.073, +0.068] | -0.297, 0.000 | no | FAIL |
| R03_4h_W12_T12 | 1289 | 1364 | +0.030 | [-0.125, +0.210] | [-0.087, +0.156] | -0.403, 0.000 | no | FAIL |
| R03_4h_W18_1R | 1292 | 1364 | -0.054 | [-0.122, +0.017] | [-0.105, -0.004] | -0.247, 0.000 | no | FAIL |
| R03_4h_W18_2R | 1292 | 1364 | -0.003 | [-0.096, +0.098] | [-0.073, +0.068] | -0.298, 0.000 | no | FAIL |
| R03_4h_W18_T12 | 1292 | 1364 | +0.030 | [-0.125, +0.210] | [-0.087, +0.156] | -0.407, 0.000 | no | FAIL |
| R04_4h_W12_1R | 1280 | 1577 | -0.124 | [-0.202, -0.047] | [-0.169, -0.076] | -0.269, 0.000 | no | FAIL |
| R04_4h_W12_2R | 1280 | 1577 | -0.090 | [-0.195, +0.024] | [-0.150, -0.026] | -0.316, 0.000 | no | FAIL |
| R04_4h_W12_T12 | 1280 | 1577 | -0.099 | [-0.251, +0.058] | [-0.193, -0.004] | -0.352, 0.000 | no | FAIL |
| R04_4h_W18_1R | 1284 | 1579 | -0.124 | [-0.203, -0.047] | [-0.171, -0.077] | -0.271, 0.000 | no | FAIL |
| R04_4h_W18_2R | 1284 | 1579 | -0.089 | [-0.193, +0.025] | [-0.153, -0.026] | -0.310, 0.000 | no | FAIL |
| R04_4h_W18_T12 | 1284 | 1579 | -0.101 | [-0.252, +0.056] | [-0.188, -0.011] | -0.352, 0.000 | no | FAIL |

DEV mean R and RECENT (>= 2025-07-01) are descriptive only (cells.csv). Best 3 by VALIDATION mean R: R03_4h_W12_T12 +0.030 (n 1364, cluster CI lower -0.125, placebo p 0.0); R03_4h_W18_T12 +0.030 (n 1364, cluster CI lower -0.125, placebo p 0.0); R03_4h_W12_2R -0.003 (n 1364, cluster CI lower -0.096, placebo p 0.0)

Not a deployable PASS even if a row says PASS: needs a causal replay test and an independent trade-loop re-run first (CLAUDE.md). Coverage: BTC from 2020-03-25, ETH from 2021-03-15, SOL from 2021-10-15, XRP from 2021-05-13, DOGE from 2021-06-02, BNB from 2021-06-29, ADA from 2021-03-18, LINK from 2020-10-21, LTC from 2020-10-21, AVAX from 2021-09-15, DOT from 2021-03-18, TRX from 2021-08-31, ATOM from 2021-10-11, NEAR from 2021-10-11, UNI from 2021-11-30, ETC from 2021-06-29, BCH from 2020-12-14, FIL from 2021-06-29, AAVE from 2021-05-13, XLM from 2021-08-31

Reading the table (added after the run): placebo p = share of 200 random same-coin same-week entries (same side, stop distance and exit rule) with mean R >= the real cell, so 0.000 means the divergence signal beats random entries. It does, in every cell, but random entries are themselves -0.24 to -0.41 R after the 12 bp cost, so beating them still leaves 22 of 24 cells below zero (the two exceptions, R03 4h T12, +0.030 R, are well inside the CI). Median stop distance is 0.9 % (1h) and 2.0 % (4h): at 12 bp round trip the cost alone is about 0.14 R (1h) and 0.06 R (4h) per trade. Pooling 20 coins (n about 6,200 per 1h cell in VALIDATION) removes the BTC-only power problem: the 1h result is a tight negative (CI upper bounds -0.12 to -0.18), not a noisy one. 4h R03 (short) is the only family near zero (CI spans zero, 4h bull-regime counter-trend shorts); DEV is also negative (-0.006 to -0.07) and RECENT (>= 2025-07) positive on R03 4h (n 605, +0.19 R at T12), a lead only, not a pass.
Code fix during the run: the first run set the placebo stop of shorts on the wrong side of entry (placebo for R03 was invalid, showing p 1.000); fixed with `placebo_stop` (+ test) and re-run; the real-trade numbers did not change. Only these 24 cells were run; none tuned.
Files: PRE_REG.md, mal_div_lib.py, study.py, test_mal_div.py (5 tests), fetch.py, cells.csv, summary.json. Data cache runtime_data/edge4-malkan-divergence-1113/ (ignored).
