# P1b PRE-REG: fee-net exit for RSI-DIV-MTF, DEV per-event R list, then the P1 phase split

Frozen 2026-10-31 BEFORE any outcome (exit, R, fee-net mean) was read. This commit contains no events_feenet.csv and no result.
Parent: `p1_split/PRE_REG.md` + `p1_split/RESULT.md` (BLOCKED for lack of this list).

## 1. Signal (unchanged)
- Events = exactly the 643 rows of `research/layer_lab/rsi_divergence_event_table/event_table.py` `run()`: BTCUSDT perp, 1h and 4h
  (4h built from complete UTC 4h buckets of the 1h bars), detector `backtest/layers/rsi/rsi_divergence.py`, interval 3-10 bars
  (SOURCED, MTF RESULT.md / Malkan), RSI delta 0, bullish = long, bearish = short. No parameter of the signal is touched.
- Data: `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz`, bars opening before 2024-07-01 00:00 UTC only (DEV 2022-01..2024-06). Nothing 2025-07+ is read (the loader cuts at DEV_END_MS before use).
- Rows with status NOT_IN_DATA (no complete 24-bar window inside DEV; 3 expected) are dropped and counted, not imputed.

## 2. Entry and exit (frozen; every number below is OURS unless marked SOURCED)
- Entry = open of the bar after the detector event bar (SOURCED: event_table.py, causal one-bar delay). Entry price = that open.
- R unit = ATR14 at the entry bar (as event_table.py: 1h from the cache `atr`, 4h Wilder ATR14 recomputed). Same R as the MFE/MAE table.
- Bracket (event_table.py gives only the 24-bar horizon and the ATR14 unit, no stop or target; the two multiples are therefore OURS and fixed here, not tuned):
  stop = entry -/+ 1.0 R, target = entry +/- 2.0 R, time exit = close of the 24th bar (horizon 24 bars including the entry bar, from event_table.py HORIZON).
- Bars scanned from the entry bar onward, in order, one bar at a time. The entry bar counts (the bracket is live from the open).
- Same-bar touch of both stop and target: the STOP is taken (conservative, OURS). Gap through the stop (bar open beyond the stop): fill at that open (OURS, conservative). Target fills at the target price.
- No bar after the exit bar is read.
- gross R = side * (exit - entry) / R.

## 3. Fees (no new constants)
- `MyTradingSys/backtest/fees.py` `BINANCE_TAKER` (0.0005 per side; the data is Binance USDT-M perp), imported, not copied. Regime A style, all-taker: entry, target, stop and time exit each pay one taker side. Round trip = exactly two sides, each applied once.
- fee in R = BINANCE_TAKER * (entry price + exit price) / R. net R = gross R - fee in R.
- Slippage and funding are NOT modelled (stated limit; the verdict says "taker fee only"). A maker-entry variant is NOT run (would be a second trial).

## 4. Outputs
- `events_feenet.csv`: one row per kept event: time (entry bar open, UTC ISO), timeframe, side, entry, exit, exit_reason (stop/target/time), R gross, R net, date (UTC day of entry), r_unit.
- `build_feenet.py` (builder), `test_build_feenet.py`, `RESULT.md`.
- Rerun `p1_split/p1_split.py` (`join_events` + `analyse`) per tag (cowen_side, sma200_side, wsma10_phase) on events with columns date, r = net R, exactly per `p1_split/PRE_REG.md` section 1 (n>=30 report, n>=200 decide, block bootstrap CI, shift test, placebo, years, episodes). Pooled 1h+4h are one event list (the 4h events overlap 1h ones in time; stated dependence; the block bootstrap is on calendar-day blocks so it absorbs it).
- Also reported (no verdict): pooled net mean R, pooled gross mean R, stop/target/time shares, by timeframe.
- One TRIALS.md row per (RSI-DIV-MTF x tag) cell family, plus one for the pooled exit rule itself.

## 5. Tests (fail-first)
1. Hand-built bars: long target hit, long stop hit, short mirror, time exit at bar 24 close, same-bar both -> stop, gap through stop fills at open.
2. Fee applied exactly once per side: with a zero-move trade, net = -(2 * BINANCE_TAKER * price / R) to the formula; doubling fee-count would fail.
3. No look past exit: changing every bar after the exit bar leaves the row identical.
4. DEV only: a bar at/after 2024-07-01 changes nothing.

## 6. Honest-negative rule
A negative or null pooled net mean is a valid result and is shipped as such. No change of stop/target/horizon/fees after reading. Any variant = a new PRE_REG and a new TRIALS row.
