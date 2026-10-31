# RESULT: per-timeframe break event study (T058 re-land, ledger P0-45)

PRE_REG.md written before the numbers were summarised; parameters unchanged from the reverted run (eca12f3b6), nothing tuned. Data BTCUSDT 1m 2022-01-01..2025-06-30 (1,838,880 rows); HOLDOUT 2025-07+ never loaded. Costs from backtest/fees.py, regime A (all-taker, round trip 0.10 %), regime D (maker both legs, 0.04 %) in output.md; no slippage. Tables: output.md (study.py then analyze.py; events.csv lives in F:/MTS/runs/tf_break_event_study/, not in the repo).

Answer: no class earns a fee-net edge at any timeframe. At 15m every trade (follow a hold, fade a reclaim, fade a wick sweep) is negative in DEV and VAL with a CI that excludes zero (FAIL). At 1h and 4h the means are around zero and the CIs span zero (INCONCLUSIVE). W and 1D have too few events (W 6 H / 1 R / 10 W1 over 3.5 years; 1D 31 H / 20 R / 71 W1) to say anything.

## Verdict arms

Fee-net mean % per trade at h4, regime A (0.10 % round trip), SE from the week-block CI.

| arm | n | mean % | SE % | verdict |
|---|---|---|---|---|
| 4h follow H DEV | 110 | -0.033 | 0.247 | INCONCLUSIVE |
| 4h follow H VAL | 38 | 0.414 | 0.384 | INCONCLUSIVE |
| 4h fade R DEV | 111 | -0.417 | 0.233 | INCONCLUSIVE |
| 4h fade R VAL | 48 | -0.634 | 0.403 | INCONCLUSIVE |
| 4h fade W1 DEV | 304 | -0.105 | 0.114 | INCONCLUSIVE |
| 4h fade W1 VAL | 126 | -0.151 | 0.171 | INCONCLUSIVE |
| 1h follow H DEV | 266 | 0.003 | 0.084 | INCONCLUSIVE |
| 1h follow H VAL | 98 | -0.002 | 0.139 | INCONCLUSIVE |
| 1h fade R DEV | 308 | -0.076 | 0.082 | INCONCLUSIVE |
| 1h fade R VAL | 131 | -0.172 | 0.103 | INCONCLUSIVE |
| 1h fade W1 DEV | 804 | -0.064 | 0.042 | INCONCLUSIVE |
| 1h fade W1 VAL | 283 | -0.053 | 0.084 | INCONCLUSIVE |
| 15m follow H DEV | 790 | -0.097 | 0.020 | FAIL |
| 15m follow H VAL | 323 | -0.124 | 0.027 | FAIL |
| 15m fade R DEV | 1393 | -0.069 | 0.017 | FAIL |
| 15m fade R VAL | 594 | -0.095 | 0.019 | FAIL |
| 15m fade W1 DEV | 3055 | -0.122 | 0.011 | FAIL |
| 15m fade W1 VAL | 1146 | -0.103 | 0.017 | FAIL |

FAIL means stop: following a held close-break, fading a reclaimed break or fading a wick sweep of a fractal swing at 15m on BTCUSDT 2022-2025 with taker fees, entry at the next open and a 4-bar hold; it says nothing about other exits, maker entries, order-flow or OI conditioning, other swing definitions, or the weekly and daily frames. INCONCLUSIVE at 1h and 4h: the CIs span zero.

## Findings

| # | Finding | Evidence |
|---|---|---|
| 1 | Most pierces are wick sweeps: W1 is about 55-60 % of events at 4h, 1h and 15m; hold share among close-breaks falls with shorter TF: 4h 50 % / 44 % (DEV / VAL), 1h 46 % / 43 %, 15m 36 % / 35 % | T1, T2 |
| 2 | Hold share of real swing levels is close to that of random pseudo-levels (15m 36.2 % vs 34.6 % DEV, 35.2 % vs 33.3 % VAL; 4h 49.8 % vs 50.9 %); at 1h real is 3-7 points higher (46.3 vs 40.0, 42.8 vs 35.5) | T2 |
| 3 | State at the break bar: RSI drops 8-12 points from pre to at in both H and R; taker flow with the break is positive and about equal (15m 0.18 H vs 0.18 R); volume spike is bigger for H (1h 3.85x vs 3.03x). After: RSI recovers for R (15m 36.8 to 47.2) and stays low for H (34.1 to 36.4); taker flow after turns against the break for R (-0.025) and stays near zero for H. That is a consequence of the class, not a predictor | T3 |
| 4 | Break distance in ATR separates H from R and keeps its direction in VAL (15m: 23.5 / 48.9 % DEV, 24.5 / 50.3 % VAL below / above the DEV median; 4h 36.9 / 62.7 DEV, 25.6 / 62.8 VAL). Partly mechanical (a deeper close is further from reclaiming); not corrected for multiple testing | T4 |
| 5 | Gross continuation in the break direction is within about 0.1 % at 15m and 1h for every class (T5); the fee-net losses at 15m are the 0.10 % round trip. With maker both legs (0.04 %, regime D) 15m is still negative or near zero, 1h and 4h stay inside their CIs | T0, T5 |
| 6 | 1D and 4h point estimates with n < 50 (1D W1 DEV +0.60 %, 4h H VAL +0.41 %) have CIs spanning zero and flip sign between DEV and VAL; not results | T0 |

## Not done

OI delta, funding, tick tiers (no local data 2022-2025); DSR, time-shuffle control C2, rolling-channel baseline C3, parameter sensitivity grid (L, N, buffer 0 and 0.25); slippage. The reverted run's headline for the follow-H and fade-R trades had the continuation sign flipped; this run's signs are checked by test_study.py.

## Caveats

Bar-level evaluation (no 1m intrabar ordering), so a pierce and a close back inside in the same bar is W1 by construction. Events overlap in time; week-block bootstrap CIs. A late DEV event's forward bars can run into VAL. Complete-bucket bars only, so a missing 1m minute drops the bar. Taker-flow ratio uses taker_buy_volume from the archive.
