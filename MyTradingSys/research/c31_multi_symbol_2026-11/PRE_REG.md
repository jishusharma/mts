# PRE_REG: C31 daily upper-BB-edge short in a 50-day downtrend, pooled over USD-M symbols (frozen before any pooled number)

Job `c31-multi-sym-m2-1105`. Source: `eagle_eyes_picture_2026-10-28/C31_HALVES.md` (BTCUSDT, rule A, edge + trend down) was
UNDERPOWERED: n=15, +1.02 R fee-net, 14 of 15 in 2022-23. This study reruns the identical frozen rule on every USD-M futures symbol
with 1m klines under F:/MTS/data/tom_raw (BTCUSDT, ETHUSDT: the only two present; max 6) and pools them. No retuning.

## Parameters (all copied from c31_halves.py rule A; nothing new is tuned)

| Parameter | Value | Label |
|---|---|---|
| Bands | Bollinger(20, 2) on daily closes (population sd) | SOURCED (operator teaching 11-03) |
| Edge | a daily close above the upper band in one of the 3 candles before the entry candle | OURS (C31 card) |
| Trend | prior daily close under its 50-day SMA = down (only down is traded) | OURS (C31 card) |
| Entry | first 1m bar of the entry candle trading under the prior daily close; fill at the prior close | OURS (C31 card) |
| Stop | prior candle high | SOURCED (operator teaching 11-03) |
| Target | BB middle of the prior candle | SOURCED (operator teaching 11-03) |
| Hold | 20 daily candles, path on 1m, exit at last 1m close | OURS |
| Cost | net R = gross R - 2 x fees.BINANCE_TAKER x 1.2 / stop distance (taker both sides + 2 bps slip RT, FORMULAS section 13) | SOURCED fees.py; slip OURS |
| Data | USD-M futures 1m, F:/MTS/data/tom_raw/klines (BTC) and klines_eth (ETH); daily candles = UTC days | OURS |
| Window | DEV only: bars in [2022-01-01, 2024-07-01); the loader raises on any bar at or after 2024-07-01 | SOURCED backtest/splits.py |

## Reproduction row
BTCUSDT runs first. The shipped C31 2022-23 half (the DEV-comparable part; the shipped total n=15 includes 1 trade in 2025 H1,
which lies outside DEV) is n=14, +1.09 R fee-net. The BTC futures DEV row must give n=14 (+/- 1 for a spot vs futures print) or the run
stops before ETH is read.

## Verdict rule (decided before any number)
Pooled trades (BTC + ETH, edge + trend down), per-trade fee-net R. Power gate = `scripts/dev/prereg_gate.py --n <pooled n> --sd <pooled
sd> --cost <mean cost R> --m auto --new-cells 1`.
- POWERED + EDGE: the gate exits 0 AND pooled mean fee-net R > 0 with one-sided t >= 1.645.
- POWERED + NO EDGE: the gate exits 0 and the t-test fails.
- UNDERPOWERED: the gate exits 1. No edge claim then, whatever the mean.
Per-symbol rows are descriptive only.

## Context
Regime: 50-day SMA downtrend (prior close under SMA50) is the gate, copied from C31; the RESULT reports the DEV regime mix per symbol (bull = close above a rising SMA50, bear = under a falling SMA50, else range; OURS).
Phase: upper-band walk ending (a close above BB(20,2) within the last 3 days), the C31 edge condition.
Session: none, because the trade is daily and enters on the first 1m print under the prior close, any UTC hour.
Entry: market short at the prior daily close on the first 1m bar trading under it; stop prior high, target BB middle, 20-day hold.

FROZEN_UTC: 2026-11-05T09:00:00Z
