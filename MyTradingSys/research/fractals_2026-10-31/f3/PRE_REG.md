# F3 PRE-REG: phase-matched nearest-neighbour analog forecast, 1h BTC, vs random-walk surrogate and block-shuffled-outcome libraries

Frozen 2026-10-31 BEFORE any outcome was computed (no run of run_f3.py exists at this commit). Spec: SYNTHESIS.md s3/s4 row F3/s7,
VALIDATION.md 3e/4a/4d/5b, R1 rank 4. Every parameter is OURS unless marked SOURCED. Nothing is tuned after the run.

## Design (frozen)
| item | value | label |
|---|---|---|
| Data | BTCUSDT 1m monthly files F:/MTS/data/tom_raw/klines, 2022-01-01..2025-06-30; files after 2025-06 never opened (reuse tf_break `load`/`bars`); complete 1h buckets only; windows or outcomes spanning a missing hour are invalid | SOURCED (SYNTHESIS F3 row) |
| Query | at 1h bar e (decision at the CLOSE of e): the last L = 48 log returns r[e-47..e], z-normalised (minus mean, over std); std = 0 invalid | SOURCED (R1 rank 4: 48-bar path) / OURS (z-norm) |
| Outcome | H = 24: log(close[e+24] / close[e]); entry at close of e, exit at close of e+24 | SOURCED (R1: 24-bar outcome) |
| Library | all windows ending at e' with e' + H <= e (ended at least 24 bars before the query; its own outcome is fully known at e and never overlaps the query outcome (e, e+24]); expanding, stride 1 | SOURCED (R1 expanding library, no overlap) |
| Neighbours | k = 10 nearest by Euclidean distance on z-paths, chosen greedily with a minimum spacing of 48 bars between chosen windows (no two neighbours share a bar) | OURS |
| Forecast | sign of the mean outcome of the k neighbours; trade only if >= 70 % of the neighbours (>= 7 of 10) share that sign | OURS |
| Trade | 1 unit long/short at close of e, exit close of e+24; all-taker both legs, round trip = 2 x `fees.BINANCE_TAKER` (0.10 %); no slippage | SOURCED (fees.py) |
| Queries | non-overlapping: e = e_first + 24 j. e_first = first bar with 2,000 library windows (warm-up ~ 83 days, fixed) | OURS |
| Splits | the answered queries (a forecast = a query with >= k spaced neighbours, before the agreement filter) cut in two equal halves by time: A and B. Needs >= 500 forecasts per split for the unfiltered variant | SOURCED (SYNTHESIS gate) / OURS (halves) |
| Variants | UNFILT: library not filtered. PHASE: library restricted to windows whose end date has the same (cowen_side, sma200_side) pair as the query end date, pair read from phase_tag/tags.csv row of that UTC date (row t is built from bars closed <= t-1) | OURS |
| Control RW | library built on a surrogate random walk: iid N(0,1) x sigma_loc, sigma_loc = std of real returns of the trailing 168 bars (shifted one bar, so no look-ahead; matched volatility), one surrogate series per draw, the library windows AND their outcomes come from the surrogate; queries stay real; same phase tags by timestamp. 300 draws, seed 31 | OURS |
| Control SHUF | real windows, outcomes block-permuted (blocks of 168 bars, random block order) over the valid outcomes, so path-outcome pairing is broken but outcome marginal and autocorrelation inside blocks are kept. 300 draws, seed 31 | OURS |
| Statistic | mean net return per trade in % (and hit rate; R = net % / (trailing-168 std of 1h returns x sqrt(24) x 100), the vol-normalised R, OURS) | OURS |
| p-values | one-sided: (1 + #controls with mean net >= real mean net) / (1 + 300), per variant x control = 4 tests, Holm at 0.05 | OURS |
| CI | week-block bootstrap (entry week), 2,000 resamples, 95 % percentile, seed 31, on the real per-trade net; control 95 % interval = 2.5..97.5 percentile of the control means | OURS |
| Horizons | H = 24 only: Holm over horizons has one member. No other horizon is run | OURS |
| Power | harness.power_n(sd of net % per trade, 0.10 %) reported | SOURCED (harness.py) |

## Verdict rule (frozen), per variant
- NOT_DECIDABLE: pooled trades < 200, or forecasts < 500 in a split.
- PASS: all of: pooled mean net % > 0; Holm-adjusted p < 0.05 against BOTH controls; mean net % > 0 in both splits A and B.
- FAIL: decidable and the week-block bootstrap 95 % CI upper bound of the real mean net % < 0.
- Otherwise INCONCLUSIVE.
- Phase-filtered vs unfiltered: descriptive difference of pooled mean net % with a week-block bootstrap CI, no verdict of its own.
- An honest negative is a valid result. No rule, gate or layer is added by this study.

## Trials (rows in research/layer_lab/TRIALS.md)
F3-1 UNFILT vs RW; F3-2 UNFILT vs SHUF; F3-3 PHASE vs RW; F3-4 PHASE vs SHUF; F3-5 PHASE minus UNFILT (descriptive). One k, one agreement fraction, one horizon, one L: no variant was tried.
