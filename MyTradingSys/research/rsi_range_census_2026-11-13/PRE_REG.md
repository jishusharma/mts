# PRE_REG: RSI range census (descriptive, no trade rule)

Operator order 2026-11-13 ~15:40Z: how far RSI goes on each timeframe, what is rare vs sometimes hit, and what the hourly RSI does given the daily RSI.

## Context
Regime: none, because descriptive census
Phase: none, because descriptive census
Session: none, because descriptive census
Entry: none, because descriptive census

Regime mix: all regimes pooled (2020-2026 Bybit linear, BTC also daily/weekly back to 2013 from the repo csv); no regime filter applied.

## Method (fixed before any output is read)
- RSI = Wilder 14 on closes via `MyTradingSys/backtest/layers/rsi/rsi_core.py::rsi_core` (SOURCED: TradingView default). First 150 bars of each series dropped (seed warm-up, OURS).
- Data: Bybit v5 public linear 5m klines BTC/ETH/SOL; 15m/1h/4h/1d built from 5m on UTC boundaries, 1w from days on Monday-UTC boundaries (OURS). Only closed bars.
- Bands (OURS, operator words): rarely hit = below own 1st pct; sometimes hit = 1st-5th pct; common = above 5th.
- Episode = run of consecutive closed bars below a threshold; counted by start year.
- Conditional (section 2): condition = RSI of last CLOSED higher-timeframe bar; outcome = lowest lower-timeframe RSI inside the next higher-timeframe bar.
- Forward (section 3): first bar of a run with RSI <= X; entry = close of that bar; forward return gross of fees at +1/4/12/24/72 bars; max further drop = min low of next 24 bars vs entry, in % and in 1h ATR14 multiples.
- No pass rule (descriptive). Cells with n < 30 flagged. Overlapping forward windows: n counts episodes, not independent samples.
- Splits not used (no rule is tested); full history pooled.
