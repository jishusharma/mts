# PRE-REGISTRATION OI DIVERGENCE - 2026-10-10

Session: MTS-2026-10-10-1608Z-DSA-COO
Registered: 2026-10-10 (before computation)
Supersedes: the three informal OI tests run 2026-10-10 (state table, event study, walk-forward).
Reason for redo: no pre-registration, snapshot OI quantized to 0.01, no cost model, no regime strata.

## Data

- OI: Dumps/backtest/raw/metrics BTCUSDT-metrics-*.csv, 5-minute cadence, column sum_open_interest.
  Window: 2025-09-01 to 2026-09-26 (last metrics file). 391 files.
- Price: Dumps/backtest/raw/klines 1-minute, resampled to 15-minute closed bars. Same window.
- Funding: Dumps/backtest/raw/fundingRate, columns calc_time, funding_interval_hours, last_funding_rate.
- Regime: Dumps/backtest/raw_1d/klines 1-day bars, 2020-01 to present.

## Signal (fixed, not tuned)

Bar: 15 minutes. At each closed bar t:
- price_pct = (close[t] - close[t-4]) / close[t-4] * 100 (1-hour price change, 4 bars).
- oi_pct = (oi[t] - oi[t-4]) / oi[t-4] * 100 (1-hour OI change, nearest 5m record at or before bar time).
- taker_ratio = taker_buy_volume / volume on bar t (from klines, column taker_buy_volume).

Signal SHORT: price_pct > 0.25 AND oi_pct < 0 AND taker_ratio < 0.5.
Signal LONG: price_pct < -0.25 AND oi_pct > 0 AND taker_ratio > 0.5.
Horizons: 4, 8, 16 bars (1h, 2h, 4h).

## Costs (from the repo, no tuning)

- Fee: 0.0010 round trip. Source backtest/fees.py BINANCE_TAKER 0.0005 per side.
- Slippage: 0.0002 round trip. Source FORMULAS.md section 13 slip_rt.
- Funding: net_return formula in backtest/layers/positioning/trade_costs.py, fail-closed if
  the hold window is outside the loaded funding span. Long pays positive rate.
- Net = gross - fee - slip - funding. All reported returns are net.

## Regime strata (fixed)

Each 15m bar inherits the day regime from the prior completed 1d bar:
- trend_up if 1d close > SMA200(1d) and SMA200 slope over 20 days > 0.
- trend_down if 1d close < SMA200(1d) and slope < 0.
- range otherwise.
Results reported per regime, not only aggregate.

## Walk-forward (fixed)

Three chronological folds on the event list. Fold 1: first third train, second third test.
Fold 2: first two thirds train, last third test. Embargo: 1 day (96 bars) dropped at each boundary.
A signal is a candidate only if the test-fold sign matches the train-fold sign in at least 2 of 3 folds.

## Success criterion (fixed)

A (signal, horizon, regime) cell passes if:
- test-fold mean net return > 0, and
- t-statistic > 2 after Bonferroni correction across the full family of cells tested.
Bonferroni divisor: number of cells reported (counted and printed).
If no cell passes, the verdict is NO REPLICATION and OI divergence is closed.

## Stop rule

Run the window once. No re-tuning of thresholds, horizons, or symbols after seeing results.
If a later session wants a different threshold, it files a new pre-registration.

## Result block

(To be appended after computation.)
## RESULT (appended 2026-10-10, after computation)

Events: 2350. Cells: 24. Bonferroni divisor: 24.

Pooled net-of-cost, all events:
- long 4 bars: -0.1468% (t -8.40); long 8: -0.1387% (t -5.68); long 16: -0.1441% (t -4.31)
- short 4 bars: -0.1380% (t -9.24); short 8: -0.1429% (t -7.39); short 16: -0.1315% (t -4.89)

Per-regime and walk-forward: same negative sign in every cell. No positive cell.
The magnitude matches the cost floor (fee 0.10% plus slippage 0.02% RT = 0.12%, plus funding),
so the gross signal is at or below zero and cost turns it into a steady loss.
Test-fold signs match train-fold signs (negative in both).

VERDICT: NO REPLICATION. OI divergence has no net edge on the 2025-09 to 2026-09 window
at 15-minute bars with Binance taker fees, 2 bps slippage and funding. The result is
pre-registered, cost-aware, regime-stratified and walk-forward. OI divergence is closed
as a candidate layer.

Not closed by this: B171 (the snapshot's quantized OI field) stands on its own. The
full-precision OI series is now proven readable; whether any other layer uses it is a
separate question for Claude per B171.