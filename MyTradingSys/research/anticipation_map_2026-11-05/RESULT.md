# RESULT: anticipation map base rates (price x OI x taker delta, 60 min)

Regime mix: bull 29% / bear 20% / range 51% (21,855 hourly events, trailing 30-day return +-10 %, OURS)

Verdict: descriptive only, fee-free, no edge. In every price x OI state the taker delta agrees with price 86-90 % of the time; the
minority reading (delta against price) is 10-14 %. What follows in the next 60 min is near a coin flip in all 8 cells (price continues
42-49 %), but the minority reading has the move undone more often (26-30 % vs 14-19 %).

Data: Binance USD-M BTCUSDT 1m klines + Binance metrics 5m sum_open_interest, DEV 2022-01-01..2024-06-30 (loader drops bars at or after
2024-07-01). Command: `python MyTradingSys/research/anticipation_map_2026-11-05/study.py` (writes `MyTradingSys/tools/live_aid/anticipation_rates.js`).

| State price / OI / delta | Reading (live_aid label) | n | share of state | price continues next 60m | move undone next 60m | OI keeps its sign next 60m |
|---|---|---:|---:|---:|---:|---:|
| UP / UP / BUY | new aggressive longs | 3262 | 87% | 47% | 19% | 60% |
| UP / UP / SELL | shorts opening into the rally | 488 | 13% | 48% | 29% | 60% |
| UP / DOWN / BUY | short covering | 2644 | 86% | 45% | 14% | 51% |
| UP / DOWN / SELL | longs take profit into passive bids | 428 | 14% | 46% | 28% | 57% |
| DOWN / UP / SELL | new aggressive shorts | 2825 | 87% | 44% | 19% | 58% |
| DOWN / UP / BUY | longs opening into the drop | 411 | 13% | 49% | 30% | 58% |
| DOWN / DOWN / SELL | long liquidation | 2959 | 90% | 42% | 18% | 51% |
| DOWN / DOWN / BUY | shorts take profit into passive offers | 320 | 10% | 48% | 26% | 53% |
| any / any / - | another venue leads | - | UNMEASURED | UNMEASURED | UNMEASURED | UNMEASURED |

States (price and OI both beyond 0.1 %): UP/UP 3750, DOWN/DOWN 3279, DOWN/UP 3236, UP/DOWN 3072; the rest of the 21,855 events had a flat leg.

## Parameters
- SOURCED: Binance kline fields (close, volume, taker buy volume), Binance metrics sum_open_interest.
- OURS: 60-min window and follow-up, 0.1 % flat band, delta sign split, "move undone" = close back past the window's start price, regime band +-10 % over 30 days.

## Deviations from PRE_REG
- Post-freeze fix: metrics rows with sum_open_interest = 0 (feed gaps) are treated as missing; the first run stopped on a divide by zero. No outcome had been read.
- BTC reproduction row: none possible, no shipped price x OI x delta study to reproduce (`layer_lab/oi_delta_event_table` is BLOCKED, NOT_IN_DATA). Spot vs futures does not apply: OI exists only for the perp.
- ETH: not run, no ETH metrics files on disk.

## Where it shows
`live_aid.html` panel "Same data, other readings": the live state (Binance OI 60-min window + taker delta from the last 12 Binance 5m bars) lists 3 readings,
each with its share (n, MEASURED) or UNMEASURED, the deciding layer, a confirm and a kill. Test: `test_live_aid.py -k anticipation`.
