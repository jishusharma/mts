# PREREG: trend following on 4h / daily (written before any result was computed)

Data: daily = pattern_book_2026-11/data/BTCUSDT_1d.csv (spot, 2017-08-17..2026-11-06, 3369 bars).
4h = perp_1h.csv (options/data/hist, 2018-08..2026) aggregated to 4h bars (00/04/08/12/16/20 UTC). The 7y spot 1h set
was NOT found on disk (only 2000-bar 1h files); the perp 1h file is the longest intraday history. Other symbols: none
of size on disk (BTC only).

Three rules, parameters fixed, no tuning, no sweep, one run:
1. Daily Donchian 20/10. SOURCED: Donchian channel / Turtle System 1 (Dennis, Eckhardt; Faith, "Way of the Turtle")
   entry 20, exit 10. Long: close > highest high of previous 20 bars. Short: close < lowest low of previous 20.
   Exit long: close < lowest low of previous 10 bars; exit short: close > highest high of previous 10.
2. 4h Donchian 55/20. SOURCED: Turtle System 2 (55 entry / 20 exit), same definitions, 4h bars.
3. Time-series momentum, lookback 28 days, weekly rebalance. SOURCED: Moskowitz, Ooi, Pedersen 2012 "Time series
   momentum" (sign of past return, periodic rebalance); 28d and weekly are the stated horizon here (OURS in
   the exact value). Every 7th daily bar: long if close/close[-28]-1 > 0 else short. A run of equal-sign weeks = one trade.

Execution: signal on bar close, fill at next bar open. One position at a time per rule. No leverage (1x notional).
Fee 10 bp round trip per trade deducted from the trade return. Stop-R: for rules 1-2 the initial exit-channel level at
entry is the stop, R = (entry - stop)/entry; rule 3 has no stop (R not reported).
Split: first 60 % of bars = DEV, 30-day gap discarded, remainder = VALIDATION. Each segment is run on its own (own
warm-up, open trade closed at segment end at last close). Rows: ALL, long-only, short-only.
Placebo: same number of trades per row, same direction, holding times resampled from the actual trades, entry time
uniform at random inside the segment, 200 draws, seed 1; percentile = share of draws with mean net return below actual.
Buy-and-hold: close-to-close over the same segment span. t-stat = mean/(sd/sqrt(n)) of net return per trade.
Pass bar (stated now): VALIDATION mean net > 0, t >= 2, placebo percentile >= 95, and DEV same sign. Anything else is FAIL
or INCONCLUSIVE. FAIL is a result.
