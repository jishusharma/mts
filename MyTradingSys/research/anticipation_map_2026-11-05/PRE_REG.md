# PRE_REG: anticipation map base rates (price x OI x taker delta, 60 min)

Card: anticipation-map-from-current-layer-stat (Eagle_Eyes 10-30 operator ask). Descriptive, fee-free; no entries, no edge claim, so no costs and no fees.py import.

## Question
For each price x OI state over the last 60 min, how often is each reading (taker delta BUY = aggressive side lifting, SELL = passive side absorbing) the one in the data, and what followed in the next 60 min?

## Data and window
- BTCUSDT USD-M futures 1m klines (F:/MTS/data/tom_raw/klines) + Binance metrics 5m sum_open_interest (F:/MTS/data/binance_metrics): SOURCED.
- DEV only: 2022-01-01 to 2024-06-30; the loader drops every bar at or after 2024-07-01. VALIDATION/HOLDOUT not read.
- ETH: not run (no ETH metrics OI files on disk); BTC futures only.

## Definitions (all OURS, fixed before the run)
- Event = each UTC hour close t with complete 1m bars over [t-60, t+60) and OI at t-60, t, t+60.
- Price state = sign of close change over the window; OI state = sign of OI change; |change| < 0.1 % = FLAT, dropped.
- Delta = sum over the 60 bars of (2 x taker buy volume - volume); BUY if > 0 else SELL.
- Follow-up (next 60 min): price continues (same sign), move undone (close back past the window's start price), OI keeps its sign.
- Regime tag: trailing 30-day close return > +10 % bull, < -10 % bear, else range.
- Third reading per state ("other venues lead") = UNMEASURED: no other-venue OI history on disk.

## Context
Regime: none, because this is a descriptive base-rate table for every regime; the regime mix is reported, not gated.
Phase: none, because the price x OI x delta state itself is the reading; no trend-phase filter.
Session: none, because events are every UTC hour; no session gate.
Entry: none, because there is no entry: fee-free descriptive follow-up only.

## What the result will say
RESULT.md: Regime mix: line, then the table of 8 cells (n, share of the state, continue, undone, OI keeps sign).
FROZEN_UTC: 2026-11-05T00:58:28Z
