# US open plan, Friday 2026-11-13 (us_open_trader, TESTNET, dry run today)

Frozen 13:10Z, before the 14:30Z cash open. BTC 69,207 (Binance spot, public data). Mode today: DRY RUN
(paper, scored after 16:30Z from public 1m candles). No order is placed today: see "Why dry run".
Not a forecast and not a measured edge: testnet-forward calibration (never counts toward the bar).

## Levels

| side | price | what | source |
|---|---|---|---|
| above | 69,571 | Europe session high | Live Aid `daily_playbook.py` (OURS windows) |
| above | 69,846 | typical US swing up (+0.93 % median) | Live Aid scenario S026 (OURS) |
| above | 70,000 | analyst cluster, 5 calls; Habib's invalidation | SOURCED `analyst_levels.py` (Michael 11-09..12, Qriptal 11-10) |
| above | 71,113 / 71,250 | prior-day low / value-area low | Live Aid `key_levels`, `value_area` |
| now | 69,207 | last hour 69,106 - 69,509 | Binance 1m |
| below | 69,000 | "next support about 69K" | SOURCED Benjamin 11-11 |
| below | 68,516 | Europe session low | Live Aid |
| below | 68,000 - 68,100 | 200-week average; Krown median-loss level | SOURCED Krown 11-10, Jala 11-09/10 |
| below | 67,568 | Asia low (today's low) | Live Aid |

Volatility: ATR(14) 15m = 239, 1h = 602. First 2 h after the open, last 8 weekdays: range median about 1,150
(693 to 4,040). Asia range today 5.84 % (95th percentile). PPI is due 13:30Z.

## Orders (one position at a time, BTC-PERPETUAL, 5,000 USD = 100 USD margin at 50x)

| id | side | trigger | entry | hard stop | target | risk | reward | why this level |
|---|---|---|---|---|---|---|---|---|
| A | long | trades above Europe high | 69,620 | 69,370 (-250) | 69,980 (+360) | 18 USD | 26 USD | break of 69,571; out before 70,000 |
| B | short | trades below Europe low | 68,490 | 68,740 (+250) | 68,120 (-370) | 18 USD | 27 USD | break of 68,516; out before 68,100 |
| C | short | touch from below | 69,980 | 70,230 (+250) | 69,480 (-500) | 18 USD | 36 USD | fade the 70,000 cluster |
| D | long | touch from above | 68,120 | 67,870 (-250) | 68,620 (+500) | 18 USD | 36 USD | fade the 200-week area |

Stop 250 = about 1 ATR(15m) = 0.36 % of price: inside Habib's observed 0.08 - 1.43 % and about 5 times
closer than the 50x liquidation distance (about 2 %, 1,380). Loss at the stop = 18 % of margin.

## Rules

| # | rule | label |
|---|---|---|
| 1 | Armed 13:35Z (5 min after PPI) to 16:30Z (2 h after the open); nothing new after 16:30Z | OURS |
| 2 | One position at a time; at most 3 entries in the session | OURS (cotrade "one at a time") |
| 3 | Which side survives: when A or B fills, the other breakout stays armed only as a reversal after a stop-out; after a target hit both breakouts are cancelled | OURS |
| 4 | Fades C and D arm only after the breakout on that side is closed (A's target sits just under C's entry) | OURS |
| 5 | Hard server-side stop on every fill, never widened | SOURCED Habib C11 "hard structure stop" (`habib_concept_book_2026-11/HABIB_CONCEPT_BOOK.md:38`) |
| 6 | At +250 (1R) move the stop to entry | SOURCED Habib C11 "break-even after TP1" (same file) |
| 7 | Size from risk, leverage follows stop width | SOURCED Habib (`HABIB_CONCEPT_BOOK.md:101,162`); 18 USD risk is OURS |
| 8 | Time stop: flat at 16:30Z at market | OURS |
| 9 | Levels are read on Binance spot; the order goes on Deribit testnet at the same distances | OURS |

What history says (so nobody reads an edge into this): a touch of the day high or low in the first 2 h still
holds 60 min later 40 - 55 % of the time (`us_open_levels_2026-10-30/RESULT.md`); the first 3 minutes do not
give the direction (`us_open_first3m_2026-11-11/RESULT.md`); the 28-day Live Aid replay passed only "fade at
Europe high" (60 %, n 30, underpowered). Tom levels: no Tom rule names a clock or a level for this window
(`session_levels.py` header: "Tom's only related words name no clock, threshold or probability"), so none is used.

## Why dry run today

`cotrade.py place` refuses a resting entry ("a later fill would have no stop") and allows one order at a time,
so both-side resting brackets cannot go through it as it stands. The module will watch the price and send a
market entry through `cotrade.place_order` at the trigger, which gets its stop at once. That watcher needs
tests and a safety review before it places anything. Both A and B passed `cotrade.py place --dry-run`
(amount, stop side, loss cap) at 13:09Z.

## Scoring

After 16:30Z `us_open_trader score` replays these four orders over the 1m candles (a bar that touches stop and
target counts as the stop) and writes entry, exit, R, level and confluence per trade to the ignored path
`runtime_data/us_open_trader/` for the Live Aid learner. The summary (no account data) is added below.
