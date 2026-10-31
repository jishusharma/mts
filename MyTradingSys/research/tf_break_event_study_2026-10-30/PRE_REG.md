# PRE_REG: per-timeframe break event study (T058, ledger P0-45) re-land

Written for the re-land of the run reverted in 5700b1a39 / d133b4493 (first version eca12f3b6). Every parameter below is OURS (no trader source); none was tuned. Fees are SOURCED (MyTradingSys/backtest/fees.py: Binance taker 0.05% per side, regime A all-taker; regime D maker both legs as sensitivity). No slippage is modelled.

verdicts.py check "per-timeframe break event study sweep hold" -> no prior row matches (need 4 of break, event, hold, per, sweep, timef). Safe to pre-register.

| item | value | label |
|---|---|---|
| Data | BTCUSDT 1m archive, monthly files 2022-01..2025-06 only, symbol-filtered, deduped by timestamp; HOLDOUT 2025-07+ files are never opened | OURS |
| DEV / VAL | DEV 2022-01-01..2024-06-30, VAL 2024-07-01..2025-06-30 (event bar time decides the split) | OURS |
| Timeframes | W, 1D, 4h, 1h, 15m, UTC epoch buckets, complete buckets only | OURS |
| Swing | fractal L bars each side: W2, 1D3, 4h3, 1h5, 15m5; confirmed at the close of bar k+L, usable from the next bar; latest live swing per side | OURS |
| Break | first bar whose range pierces the level consumes it; close beyond by 0.1 x ATR14(SMA) = break, else W1 (wick sweep) | OURS |
| Class | R if any close is back inside within N bars (W2, 1D3, 4h6, 1h6, 15m8), else H | OURS |
| Entry / exit | open of the bar after the class is known; exit after 4 bars (headline) or 24 | OURS |
| Trades | H: follow the break; R: fade the break; W1: fade the pierce | OURS |
| Control C1 | pseudo-level = random non-swing bar's low/high in the last M bars (W26, 1D60, 4h90, 1h96, 15m96) | OURS |
| CI | week-block bootstrap 1000 draws, 95 % | OURS |
| Verdict rule per arm and split | n < 100: INCONCLUSIVE; else CI upper bound < 0: FAIL; CI lower bound > 0: PASS; else INCONCLUSIVE | OURS |

Differences from the reverted run: the sign of continuation and taker flow is now + = in the break direction (the reverted code multiplied by -side, which flipped it); VAL ends 2025-06 (was 2025-08); costs come from fees.py (was a 12 bp constant with 2 bp OURS slippage); swing confirmation is built from past-shifted series so the look-ahead lint has no hits; events.csv is written to F:/MTS/runs, not the repo. The event definitions and parameters are unchanged from the reverted run, whose class counts the new run reproduces.
