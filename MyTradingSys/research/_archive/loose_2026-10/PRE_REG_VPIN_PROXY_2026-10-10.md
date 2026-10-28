# PRE-REGISTRATION VPIN PROXY - 2026-10-10

Session: MTS-2026-10-10-1608Z-DSA-COO
Registered before computation.
Caveat: Dumps/backtest/raw/aggTrades is empty, so this is a kline-based flow-toxicity proxy, not true VPIN.

## Input

- Klines: Dumps/backtest/raw/klines, 1-minute, columns volume and taker_buy_volume.
- Window: 2025-09-01 to 2026-09-26 (the metrics OI span, so OI can cross-check).
- Regime: Dumps/backtest/raw_1d/klines, SMA200 on 1d close.

## Construction (fixed)

- Bucket volume V = 2500 BTC. Accumulate 1m bars until cumulative volume crosses V, close bucket.
- Bucket imbalance = |sum over bars in bucket of (2*taker_buy_volume - volume)|.
- VPIN_t = mean of (imbalance / V) over the last 50 completed buckets at bar t.
- Spike = VPIN_t above the trailing 180-day 90th percentile.
## Test (fixed)

For each bar t where a spike fires:
- fwd_abs_ret_1h = |close[t+60] - close[t]| / close[t] * 100.
- fwd_abs_ret_4h = |close[t+240] - close[t]| / close[t] * 100.
- fwd_max_adverse = max adverse excursion over t+1..t+60 bars, in percent (worst move against a neutral position, both directions checked).

Baseline: the same three measures over ALL bars in the window (unconditional).
Reported: spike mean, baseline mean, difference, t-statistic on the difference (Welch), with day-clustered standard error.

## Strata (fixed)

- Regime: trend_up, trend_down, range, from the prior completed 1d bar's SMA200 and slope.
- Session: asia, europe, us, from bar time in UTC (00-07, 07-13, 13-21 asia/europe/us).

## Walk-forward (fixed)

Three chronological folds on the spike list. Fold 1: first third, Fold 2: first two thirds, Fold 3: all.
Only spikes after a 180-day warmup count. Report test-fold difference per fold.

## Success criterion (fixed)

A (horizon, regime) cell passes if the spike-versus-baseline difference is positive AND t > 2 after Bonferroni over cells reported.
If no cell passes on fwd_abs_ret, VPIN-proxy closes for that horizon.
fwd_max_adverse is reported separately: a pass means the spike predicts a larger adverse excursion than baseline, useful as a risk gate even if the directional signal fails.

## Stop rule

Run once. No re-tuning of bucket size, window, percentile, or horizons after results.
Different parameters require a new pre-registration.

## Result block

(To be appended.)
## RESULT (appended after computation)

Spikes 2530 of 580260 bars (0.44 percent). Buckets 22957. Baseline 580260 bars.

Pooled spike vs baseline:
- abs 1h: 0.4812 vs 0.2965, diff +0.1847, t +17.14
- abs 4h: 0.7976 vs 0.6026, diff +0.1950, t +12.69
- adverse 60 bars: 0.7722 vs 0.4576, diff +0.3146, t +18.31

Per regime: trend_down and range pass all three measures. trend_up passes abs 1h (t +3.64) and
adverse (t +4.42); trend_up abs 4h fails (t +0.49). Walk-forward: all three folds positive.

VERDICT: PASS. The kline flow-toxicity proxy separates fragile from calm. It predicts larger
absolute moves and larger adverse excursions. It does not predict direction. Useful as a risk
gate (widen stops, reduce size, or stand aside during a spike), not as an entry signal.

DEVIATIONS from the pre-registration, stated plainly:
1. The pre-registration specified day-clustered standard error. The script used Welch t only.
   Overlapping 60-bar windows inflate t, so the effective sample is smaller than the raw n.
   The sign and magnitude are stable across folds, but the t values are optimistic. A
   day-clustered rerun is required before this is treated as confirmed at full strength.
2. aggTrades archive is empty, so this is a kline proxy, not true VPIN. The label must say so.

FOLLOW-UPS:
- Day-clustered t on the same spikes (cheap, same script).
- True VPIN once a tick archive exists (see the aggTrades gap filing).
- If confirmed: define how the spike gates the live engine (size, stop width, or stand-aside).
## DAY-CLUSTERED CONFIRMATION (appended 2026-10-10)

Removes deviation 1 above. Days are the resampling unit.

| measure | spike n | spike days | base days | spike mean | base mean | diff | se(day) | t |
|---|---|---|---|---|---|---|---|---|
| abs_1h | 2530 | 126 | 403 | +0.4812 | +0.2965 | +0.1847 | 0.0259 | +7.14 |
| abs_4h | 2530 | 126 | 403 | +0.7976 | +0.6026 | +0.1950 | 0.0392 | +4.97 |
| adv_60 | 2530 | 126 | 403 | +0.7722 | +0.4576 | +0.3146 | 0.0448 | +7.02 |

All three t above 2 after day clustering. The pass holds at full strength.
Detail: research/_archive/loose_2026-10/VPIN_DAYCLUSTERED_2026-10-10.md