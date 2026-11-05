# PRE_REG: level-approach prep base rates (U1 absorption, U2 OI tell, U3 wick count)

Card: level-approach-prep (Eagle_Eyes 10-30 operator ask; spec research/eagle_eyes_picture_2026-10-28/CARD_SPECS.md#level-approach-prep, UNKNOWNS U1-U3). Descriptive, fee-free; no entries, no edge claim, so no costs and no fees.py import.

## Question
- U1: at a prior-day high/low approach, does absorption (aggressive delta toward the level, no extension) reverse more often than a distance-matched non-absorption approach?
- U2: among absorption approaches, does OI rising during the push (shorts opening into buying / longs into selling) reverse more often than OI flat or falling?
- U3: does the number of timeframes (1m/2m/3m/5m) showing a wick rejection in the 15 min before the first touch change the hold rate?
- U4 (5m vs 1m confirm close) is NOT run here; it stays an open ledger row.

## Data and window
- BTCUSDT USD-M futures 1m klines (F:/MTS/data/tom_raw/klines) + Binance metrics 5m sum_open_interest (F:/MTS/data/binance_metrics): SOURCED.
- DEV only: 2022-01-01 to 2024-06-30; the loader drops every bar at or after 2024-07-01. VALIDATION/HOLDOUT not read.
- ETH: not run (no ETHUSDT 1m klines and no ETH metrics on disk); BTC futures only.

## Definitions (all OURS, fixed before the run)
- Levels: prior UTC-day high (PDH) and low (PDL) from the 1m bars of the previous day. One approach per level per day.
- Approach (U1/U2): the first 1m bar t of the day whose high comes within 0.3 % of PDH (low within 0.3 % of PDL); skipped when the day opened inside that zone.
- Push = bars t-2..t. Delta share = sum(2 x taker buy - volume) / sum(volume), signed toward the level (+ = pushing into it).
- Extension = best price in the push direction over bars t+1..t+3 vs close of t. Absorption = delta share >= +0.3 and extension under 0.1 %.
- Outcome from close of t+3 over the next 60 bars: break = a 1m close more than 0.1 % beyond the level; reversal = price 0.5 % back from that close before any break close.
- Distance match: close of t vs level in buckets beyond / 0-0.1 / 0.1-0.2 / 0.2 % +; non-absorption reversal rate reweighted to the absorption bucket mix.
- OI tell (U2): OI at the 5m stamp at or before t+4 min vs the stamp 5 min before t-2 min; UP / DOWN beyond 0.1 %, else FLAT.
- Touch (U3): the first 1m bar u whose high reaches PDH (low reaches PDL), day opened outside the 0.3 % zone. Wick rejection on a TF = a closed bar fully inside [u-15 min, u) with its extreme within 0.3 % of the level and the wick toward the level >= 50 % of its range. Count = number of TFs (0-4) with at least one. Hold = no 1m close more than 0.1 % beyond the level over u..u+59.
- Regime tag: trailing 30-day close return > +10 % bull, < -10 % bear, else range.

## Context
Regime: none, because this is a descriptive base-rate table for every regime; the regime mix is reported, not gated.
Phase: none, because the approach to a prior-day level is itself the condition; no trend-phase filter.
Session: none, because approaches happen at any UTC hour; no session gate.
Entry: none, because there is no entry: fee-free descriptive follow-up only (U4 confirm rule not run).

## What the result will say
RESULT.md: Regime mix: line, then U1 (absorption vs matched non-absorption reversal rate, n), U2 (reversal by OI sign, n), U3 (hold rate by TF count, n).
FROZEN_UTC: 2026-11-05T01:27:38Z
