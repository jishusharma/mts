# PRE_REG: Tom's return-to-value on the prior NY CASH-SESSION value area (BTC, ETH, SOL, 1m)

Written 2026-11-13 before any outcome was computed. Slug edge4-ny-session-value-1113.

## Hypothesis
Tom's claim is about the prior CASH SESSION value area, not a 24h profile. Gap hunt G01/G02: every earlier BTC value-area test
(vp_return_to_value, census_session_ladder, FACTS B2 57.2% vs 70%) used a 24h UTC day or Monday week, which Tom calls
"inherently quite meaningless". `auction_context.prior_ny_session_profile` is the coded fix and nothing calls it. This study calls it.
H1 (count): when today's session opens outside the prior session's 70% value area and price re-enters value and holds
for two 30-minute closes, price reaches the opposite value edge before session end in about 70-80% of cases, higher in balanced days.
H2 (trade): that setup, traded with a session-extreme stop and the opposite edge as target, has positive fee-net mean R on VALIDATION.

## Quotes (SOURCED) - Tom; transcript ids from the gap report sonnet_conditions.md
- Cash session only: Of_wlv3xaZo "You can't say, 'I only trade the cash session.' But then refer to 24-hour profiles. Why? That's inherently quite meaningless."
  and "if you only trade during cash hours, please only refer to the cash session."
- Skip first 30 min: Of_wlv3xaZo "stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is".
- 70% and its failure clause: VumVuGnCcFM "markets always tend to return to the Vpo to regain balance. And that happens about 70% a little over 70% of the time.
  But heaven help us if that's not the case." and "when a market becomes strongly trending, please stop trying to get back".
- Open range: Fj4FDZQxw0I "Open range ... If it's very large, it likely won't hold. If it's very small, it likely will."
- Balance only for counter trades: VxN5IxTwpbE "the strategy of countertrend trading is what really works" in balance; 4VXpUjhKG2U "Breakout trading only works when a market is out of balance."

## Data
Binance SPOT 1m klines (public archive data.binance.vision, monthly zips) BTCUSDT, ETHUSDT 2020-01.., SOLUSDT 2020-09.. to 2026-10.
Coverage and gaps are printed in RESULT.md. Spot volume (base asset) is the profile weight. Microsecond stamps (2025+) are converted.
Closed bars only: signals use 30m closes = the close of the last 1m bar of the 30m block; fills at that close.

## Exact rule
Session: NY cash session 09:30-16:00 America/New_York on weekdays = 13:30-20:00 UTC in US daylight time, 14:30-21:00 UTC in winter. DST rule: the code's
`auction_context._us_dst` (2nd Sunday March to 1st Sunday November, US 2005 rule), used via `ny_session_window`. US exchange holidays NOT modelled (weekday = session day);
sessions with < 90% of the expected 1m bars are skipped (current or prior).
Prior session = the previous weekday's session (Monday uses Friday). Profile = `prior_ny_session_profile` on that session's 1m bars
(HLC3 into price bins, 70% value area expanding to the larger neighbour; VAL/VAH/POC). Bin = 5 bp of the prior session mean close (OURS).
Open outside: first 1m open of today's session > VAH or < VAL (strict).
30m blocks are aligned to the session start (block 0 = first 30 min). Setup: the first pair of CONSECUTIVE 30m closes both inside [VAL, VAH]
with the first block of the pair >= block 1 when skip_first30 = yes, >= block 0 when skip_first30 = no. Entry = close of the second block of the pair.
One trade per symbol-session. Direction: opened above VAH -> SHORT, target VAL; opened below VAL -> LONG, target VAH.
Stop = session extreme so far (running high for short, low for long, from session open to entry) beyond by a 1 bp buffer. Target = the opposite value edge.
Time exit = last 1m close of the session. Stop-first when a 1m bar touches both. A trade is skipped when stop distance < 10 bp of entry (OURS, degenerate R guard).
Net R = (signed move/entry - round-trip cost) / (stop distance/entry). Round-trip cost = 2 x (fees.BINANCE_TAKER + slippage), slippage = BINANCE_TAKER/5
(1 bp, OURS, same assumption as the bigtrade costs: 5 bp taker + 1 bp slip per leg, 12 bp round trip). The task text said "4 bps/side"; the repo's frozen taker is 5 bp, so
this run is 2 bp per side MORE conservative than the order.

## Cells (12, fixed)
regime {all, balanced, trending} x skip_first30 {yes, no} x side {long, short}. Pooled over the 3 symbols; per-symbol numbers are descriptive only, not cells.
Balanced day (known before entry): prior session range inside the range of the session before it (inside day: its high <= and low >= those), OR today's opening range
(first 30 min high-low) < the median of the same quantity over the prior 20 sessions. Trending = not balanced. (Thresholds: inside rule and 20-day median are OURS;
balance-vs-trend as the splitter is SOURCED, Tom VumVuGnCcFM/VxN5IxTwpbE.)

## Count (reported first)
Per cell and split: n setups, and reach-other-edge % = share of setups where any 1m bar after entry until session end touches the target edge (stop ignored: Tom's plain count),
plus the same share before the stop is hit. His claim: 70-80%.

## Splits and pass rule
DEV = sessions to 2023-12-31. VALIDATION = 2024-01-01 to the end of data (includes 2025-07 onward; no separate RECENT cell). Pass per cell, all required:
VALIDATION n >= 30; fee-net mean R > 0; 95% bootstrap CI lower bound > 0 (resample whole session-dates, 5000 draws, so coins on one day stay together);
beats placebo (real mean above the 95th percentile of 500 placebo means; placebo = for each trade, a random 1m entry between the earliest possible entry minute of that variant and the session end,
restricted to bars whose close is inside the value area, same side, same target, stop = running extreme at that moment, same costs); Benjamini-Hochberg at 10% over the 12 cells'
one-sided bootstrap p-values (p = share of bootstrap means <= 0). Primary metric: mean net R per trade.

## Parameter labels
| param | value | label |
|---|---|---|
| value area share | 70% | SOURCED (VumVuGnCcFM / TOM-277) |
| profile window | prior NY cash session | SOURCED (Of_wlv3xaZo) |
| skip first 30 min | cell variable | SOURCED (Of_wlv3xaZo) |
| two 30m closes inside as hold | 2 x 30m | OURS (accept80 convention, FACTS B3) |
| target = opposite edge, entry toward it | | SOURCED in kind (return to value, VumVuGnCcFM); exact edge OURS |
| stop at session extreme + 1 bp | | OURS |
| profile bin 5 bp | | OURS |
| min stop 10 bp | | OURS |
| balanced rule (inside day OR opening range < 20-day median) | | OURS (concept SOURCED) |
| costs 5 bp taker + 1 bp slip per side | | OURS (repo fees.py) |

## Context
Regime: balanced vs trending day is a cell dimension (rule above), not a bull/bear filter; RESULT.md also reports the bull/bear/range mix of each window (BTC close vs 200-day SMA, band 5%) as `Regime mix:`.
Phase: balance (inside day or small opening range) vs trend, both run and compared; Tom says the 70% holds only in balance.
Session: prior NY cash session value area, weekdays only, 13:30-20:00 UTC (14:30-21:00 UTC winter); first 30 min skipped or not (cell variable).
Entry: second consecutive 30m close back inside the prior session value area, toward the opposite edge; stop at the session extreme; target opposite edge; exit at session end.
