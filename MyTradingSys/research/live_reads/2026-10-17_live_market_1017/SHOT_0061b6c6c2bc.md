# 2026-10-18 BTCUSDT 5m: same day as the 15m pivot read, one timeframe down
<!-- Process: methodology/screenshot_intake.md. Claim rows `| id | MATCH or MISMATCH or NOT_IN_DATA | claim | evidence |`. No trade advice; testnet only; no marks (G3 gated). Tag: NOTE. -->

Shots: 0061b6c6c2bc (5m)
Operator words: none (sent right after the question "this is only one time frame ... check how our idea works in different time frames").
Clocks: CoinGlass TradingView = UTC. Header O 81139.5 H 81150.0 L 81139.5 C 81147.6 = 17:55 bar, countdown 02:40 -> ~17:57:20Z.
Timeframes present: 5m (with the 15m shot 163af24365f3 from 40 min earlier: 2 TFs of the same day).
Data: Binance fapi 1m 10-17 21:00 -> 10-18 17:59Z rebuilt to 5m; openInterestHist 5m from 10-18 00:00; fetched 17:59Z; mirror@2026-10-18 17:56Z.

## Carried context
Prior: MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SHOT_163af24365f3.md
Watch line "reclaim 81,500 with OI falling, or acceptance under 80,987.6": BROKEN on the low side by 31.7 pts only (15:40 low 80,955.9), no acceptance (closed back above 81,000 within minutes, weekly VAL 80,868 untouched). No reclaim of 81,500 (high since 15:00 81,221.5). Net: neither outcome; a flat base.

## Claims
| id | class | claim | evidence |
|---|---|---|---|
| 0061b6c6c2bc-1 | MATCH | 5m header O 81139.5 H 81150.0 L 81139.5 = 17:55 bar | fapi 17:55 O 81139.5 H 81150.0 L 81139.5 at 17:59 |
| 0061b6c6c2bc-2 | MATCH | VWAP 81569.4 | 5m-bar hlc3 VWAP from 00:00Z = 81,567.7 (15m chart showed its own value; per-TF VWAP as in SET_ffb3dd828daa) |
| 0061b6c6c2bc-3 | MATCH | OI 93.583K | openInterestHist 17:55 93,586.6 |
| 0061b6c6c2bc-4 | MATCH | OI steps up at ~07:20 and ~09:00 with price flat / breaking out | 07:15-07:30 OI +415, delta +374; 08:55-09:10 OI +309, delta +889, price 81,706 -> 81,979 |
| 0061b6c6c2bc-5 | MATCH | 13:15 OI cliff with price and CVD falling together (largest move of the day) | 13:10-13:55 price 81,912 -> 81,475, delta -1,879, OI -1,762 (94,691 -> 92,929; OI max 94,705 at 13:05) = long liquidation |
| 0061b6c6c2bc-6 | MATCH | OI rebuilt off its 14:00 low while price kept falling | 13:55-15:00 price 81,475 -> 81,060, delta -1,697, OI +817 (low 92,916 at 14:00) = new shorts into the fall |
| 0061b6c6c2bc-7 | MATCH | 15:00-18:00 flat base: price, OI, CVD and Net Delta all flat | price 80,956-81,222, OI 93,746 -> 93,587 (-158), delta +140 over 3 h; volume per hour 4,555 / 4,929 / 1,966 (fading) |
| 0061b6c6c2bc-8 | MATCH | CVD fall 13:00-15:00 ~5.5K -> ~2.0K | taker delta 13:10-15:00 = -3,576 (levels not compared: CoinGlass anchor differs) |
| 0061b6c6c2bc-9 | NOT_IN_DATA | Net Delta 2.306K; session volume profile on the left with two red lines (~81,520 and ~81,090) | CoinGlass Net Delta and session-VP blocks are in no file (recurring) |

## Reading: what the second TF adds
- Same events, sharper on 5m. The 07:15 15m turn is one 5m bar (07:20); the 13:15 unwind is a 45-min cliff. 5m shows WHEN a phase starts to the bar; 15m shows whether it lasted. That is the per-TF test in card oi-pivot-reversal-probability-by-tf: the same candidate rule must be scored on each TF, and the 5m candidate counts only if it survives to the 15m close.
- Mirror image of the morning. Morning: OI trough at flat price, then OI built with positive delta (new longs), released up. Now: OI built during the fall (new shorts, +817), then 3 h of flat price with flat OI and fading volume. The morning pattern needed OI rising at flat price; this one has OI flat at flat price, so it is not the same signal yet. The shorts are holding, not covering (OI -158 only).
- Context: Sunday evening, price at the bottom of the 10-18 range and just above weekly VAL 80,868, inside the 11-day balance. The day's taker delta is back to about zero (+750 since 00:00): the morning buying has been sold back.

## Live system (mirror@2026-10-18 17:56Z)
HALT + HALT_DAILY_LOSS raised; last decision 17:16:16Z `skipped_halt` (turn_of_candle 1m). No trade.

## Watch next
Which way the base resolves: OI falling while price rises (the 13:55-15:00 shorts cover, as at 10-16 17:30 and 10-17 21:45) or OI rising while price breaks 80,955.9 (acceptance below, toward weekly VAL 80,868).
