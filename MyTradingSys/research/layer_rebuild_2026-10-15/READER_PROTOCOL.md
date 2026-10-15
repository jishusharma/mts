# READER PROTOCOL for G3 blind marks (v1, 2026-10-16)

Purpose: the one page both readers (operator = reader 1, Claude = reader 2) use so that a disagreement in G3 is a disagreement about the chart, not about what "balance" means.
Source: CATALOGUE_AUDIT.md (fable_audit_2026-10-16) section 4.3 gap list and plan correction P3. Decisions applied: D1 (00:00 UTC anchor), D3 (merges/splits allowed), D4 (markable rows and Krown/Malkan first).
Labels: SOURCED = the trader's words (quote + where). OURS = a definition we chose so a row can be marked. **Every OURS item below is a definition, not a tuned number: it was fixed before any outcome was seen, is the same for every row and window, and is never varied during G3.** Changing any item = new protocol version and all marks restart. Tuned numbers (stops, targets, horizons, fees) stay out until G5.

## 1. Definitions (all causal: computed from bars closed at the window's right edge, never after)
| term | definition | label |
|---|---|---|
| BTC session | the UTC day, 00:00 to 24:00; session VWAP and session profile restart at 00:00 UTC. "Prior session" = the previous UTC day. | OURS (D1; same as the gross-effect PRE_REG) |
| close-based | every range, edge and shape below uses closing prices, not wicks. | OURS (plan: "by closing prices") |
| balance | N consecutive closes inside a range whose width (max close - min close) is at most W % of the last close. Edges = highest and lowest close of the run. Per timeframe (TF): 5m N=36 W=1.0; 30m N=12 W=1.5; 1d N=20 W=8; 1w N=8 W=15. | OURS (Tom: "balance" has no rule in his words) |
| value area (VA) | 70 % of volume around the volume POC, 10 USD footprint bins (the `fp` field), contiguous bins grown from the POC, ties lower (same as `chart_lab._value_area`). "Old value area" = VA of the prior session. | OURS |
| P / b / D by closes | histogram of the session's closes in 20 equal bins from lowest to highest close (at least 24 closes, else "undefined"). POC bin in the top third of the range = P, bottom third = b, middle third = D. | OURS (Tom's letters, no rule in his words) |
| thin top | the top quarter of the session's close range holds at most 10 % of the session's closes (mirror: thin bottom). | OURS |
| big trade | one aggTrades print at or above the prior-30-day 99.9th percentile of print size (`thr999` in `orderflow_1m`, flags `b999_*`). No notional match with NQ is claimed; the rank rule is OURS. | anchor SOURCED: Fabio "What was the minimum contract? Always the same. It's 30 contracts. If you are in London, I use 20." (DyS79Eb92Ug captions on F:, t 1634-1641, audit 3.3 F-2; not gate-checked until P2) and slide "30 to 40 on NQ" (FL:50). BTC equivalent OURS |
| healthy trend (up) | his test is whether the volumes shifted: SOURCED "check whether the volumes have really shifted upwards" (YkclL6xgu-s END) and "Not with quick spikes but with real acceptance" (qLnQan0KGmQ END). OURS test: the volume POC of the three consecutive 4h blocks ending at the last closed bar rises twice in a row (each by at least one 10 USD bin) and the last close is above session VWAP. Down = mirror. | test SOURCED, numbers OURS |
| VWAP pullback | the bar's low (up trend) trades at or below session VWAP and the bar closes above it; mirror for down. | OURS |
| outside P / break-in | P above the old VA = at least 4 consecutive closes above the old VAH, then a close back inside the old VA (mirror for b below VAL). The break-in bar is that first close back inside. | OURS (closing-price counting rule "taught elsewhere", audit 4.3) |
| clear space to the left | no close in the last 5 sessions (240 bars of 30m) inside the 0.5 % band beyond the broken edge. | OURS |
| absorption | at one price (within 0.05 %), a bar trades with aggressive delta against the level's holders but closes on the holder's side of the level, repeated at least 3 times in 60 bars (bars at least 3 apart). The resting wall is not visible; mark the absorption, never the wall. | OURS (audit 4.3 FAB-5) |
| zone (Krown) | a price band from a wick extreme to the nearest close that turned price at least twice; level tested more than three times = mature. | SOURCED shape (KR-S1, KROWN_SETUP_CATALOG); counts OURS |
| BBWP | percentile rank of the 20-day Bollinger Band width (2 sd) within the previous 252 daily bars, in %; compression = below 30, "back above 50" = release. Lines at 30, 50 are drawn. | SOURCED idea ("below about 25-35", "above the 50th", KR-S8), exact numbers OURS |
| RSI | Wilder RSI(14) on closes of the row's TF. Malkan's levels 40 and 60 are drawn. Monthly RSI = last completed calendar month (no partial month). Divergence pivots: highest (lowest) close of the last 20 bars versus the highest (lowest) close in bars 5..60 back; RSI lower (higher) there. | levels SOURCED (Malkan 40/60), 14 and windows OURS |

## 2. Timeframe per row (one TF per row for all of G3)
| row | TF | bars shown | panels (only these) |
|---|---|---|---|
| TOM-4 | 15m | 288 | candles, session VWAP, prior-session VA lines, 4h-block VPOC ticks, volume |
| TOM-6 | 30m | 240 | candles, session VWAP, 5-session composite volume profile, volume, per-bar delta |
| TOM-12 | 30m | 240 | candles, old VAH/VAL/POC lines, session close profile, volume |
| TOM-15 | 30m | 240 | candles, balance edges, volume |
| FAB-1 | 5m | 288 | candles, session close profile, CVD (daily reset) and per-bar delta, big-trade ticks |
| FAB-4 | 5m | 288 | candles, prior-session VAH/VAL/POC, per-bar delta, big-trade ticks |
| FAB-5 | 5m | 288 | candles, per-bar delta, footprint top-3 price bins by volume, big-trade ticks |
| KR-S1 | 1d | 180 | candles, volume with 30-day average |
| KR-S8 | 1d | 180 | candles, BBWP with 30/50 lines |
| MAL-2/5 | 1w | 60 | weekly candles, weekly RSI(14) with 40/60, monthly RSI(14) with 40/60 |
| MAL-16/17 | 1d | 180 | candles, daily RSI(14) with 40/60 |
MAL-5 is MAL-2's order mechanic (order on the high, stop below the lowest): same visible event, so one mark "MAL-2/5". MAL-16 (bearish) and MAL-17 (bullish) regular divergence share windows and a 3-way mark (SHORT / LONG / NONE). Rows not in this list (TOM-1a, TOM-2, TOM-3, TOM-7 to 11, 13, 14, 16, FAB-2, 3, 6 to 8) join G3 later (D4); TOM-1a and TOM-2 use this protocol's session and balance.

## 3. How to mark a window
1. The chart ends at the last closed bar (offset 0). Dates are hidden; the price axis is % from the last close. You see no bar after the edge.
2. TAKE = the row's setup, as the catalogue says you would see it, has triggered on the last closed bar or up to 3 bars before it. Otherwise SKIP. No "maybe": a doubt is a SKIP with a note.
3. If TAKE: write the trigger bar as an offset (0 = last bar), the concepts you saw from the fixed list (BAL, P, B, D, THIN_TOP, BIG_TRADE, HEALTHY_TREND, VWAP_PULLBACK, OUTSIDE_P, BREAK_IN, EDGE_CANDLE, CVD_PRESSURE, ABSORB, ZONE_TURN, PROOF_CANDLE, BBWP_LOW, RSI_SUPPORT_60, RSI_DIV), your stop and target as % from the last close (his rule if he states one, else where the trade is wrong / the next structure: marked, not optimised).
4. Readers never see each other's marks, the answer key, the outcome after the edge, or the date. Reader 2 sees only this page, the row's catalogue text and the PNG.
