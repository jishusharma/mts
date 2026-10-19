# 2026-10-19 BTCUSDT 1m: the 13:34 high-volume bar and the 13:37 big-delta bar after the US open
<!-- Process: methodology/screenshot_intake.md. No trade advice; testnet only; circles and verticals are the operator's. Tag: NOTE (research candidates routed as a card, nothing run here as proof). -->

Prior: MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SHOT_45668ed864d7.md
Shots: f34fe84a244a (CoinGlass tv 1m, UTC). Last bar 13:40, countdown 00:31 => captured ~13:40:29Z (the 13:53 label is the cursor, not the clock). Verticals by pixel = 13:34 and 13:37 (label). Mirror: mirror@2026-10-19 13:41Z.
Operator words: first vertical = big volume, hammer inside the Bollinger band, OI up while CVD and Net Delta fall; RSI rejected at 40 and under its MA (two circles); second vertical = Net Delta jumps up but volume small compared with the red candle; "pass it on for more research and validations".
Data: Binance fapi 1m klines 12:00-13:42Z (taker delta = 2*takerBuyBase - volume), openInterestHist 5m, RSI14 Wilder on 1m closes.

## Claims
| id | class | claim | evidence |
|---|---|---|---|
| f34fe-1 | MATCH | Header O 82212.0 H 82240.8 L 82160.2 C 82240.7 = forming 13:40 bar | 13:40 O 82212.0 L 82160.2, final H 82250.0 C 82230.3 (bar still open at capture) |
| f34fe-2 | MATCH | Line 1 (13:34) has the largest volume | 495 BTC, 2.4x the 13:30 open bar (206) and the largest 1m bar of the window; delta -202; range 82,342.8-82,420.5, close 82,394.5 (lower wick 52); inside the BB (lower 82,178) |
| f34fe-3 | MATCH | OI up while CVD and Net Delta fall at line 1 | 5m OI 93,967 (13:30) -> 94,061 (13:35) -> 94,361 (13:40) = +394 in 10 min while delta 13:30-13:35 -251 and price 82,481 -> 82,312 |
| f34fe-4 | MATCH | RSI rejected at 40 twice, under its SMA | RSI14(1m) 41.4 (13:30), 39.1 (13:33), 37.6 (13:37), each followed by lower lows 29.2 (13:32), 30.1 (13:35), 27.2 (13:38) |
| f34fe-5 | MATCH | Line 2 (13:37): big positive Net Delta, volume smaller than the red bar | 13:37 delta +209 on volume 312 (67% one-sided) vs 13:34 -202 on 495 (41% one-sided); price only +55 (82,299 -> 82,354), high 82,369.1 |
| f34fe-6 | MATCH | Then it is pushed back | 13:38: delta -183, volume 334, price -166 to 82,188.0 (low of the move), 13:39-13:41 delta ~0, 82,138-82,250 |
| f34fe-7 | NOT_IN_DATA | CoinGlass CVD 101.8 / Net Delta -122.7 values; BB 82,423.3/82,668.5/82,178.1; VWAP 82,505.6 | aggregated series, not reproduced in this read |

## What the two bars convey (my eye read, OURS; a candidate, not a result)
- 13:34: the heaviest selling bar of the morning (delta -202, 495 BTC) moved price only 26 points: sellers were absorbed at 82,343-82,420 (hammer wick), yet OI rose, so the sellers were opening shorts, not closing longs. Absorption was short-lived: 13:35 delta -110 broke 82,292 and the move continued; i.e. the absorbed bid did not hold.
- 13:37: buying burst (+209) on fewer contracts gained 55 points and stopped at 82,369 under VWAP/BB mid, then reversed (-183 next minute). Delta per unit price was 3.8/pt up vs 1.1/pt down on the next bar: the up push met resting offers, the down push did not meet bids. Reads as a thin-liquidity squeeze inside a downtrend (OI +300 over 13:35-13:40 = fresh shorts through the fall), not a reversal.
- Your volume point: the 13:37 delta looked big because it was 67% one-sided, not because volume was big; one-sidedness without volume leaves no follow-through here.
- Prediction scoring (my 13:28 note): US open 13:30 -> 13:40 = 82,455 -> 82,230 (-225, 10-min delta -326, range 82,138-82,481). The "down" branch triggered (82,420 and 82,330 lost, 82,092.1 line not reached: low 82,138.4); the up lean (60-70%) did not. Base rate said down 30-40% of days; this was one of them.
- Live: HALT + HALT_DAILY_LOSS raised; mirror shows no non-turn-of-candle layer event since 13:25 and Tom's last row is the stale 12:02 WATCH long (entry 82,339.6, stop 82,168.9, target 82,758.8): price is through that entry and 70 pts above its stop. Fabio null.

## Research candidates (card one-minute-absorption-and-thin-delta-bars, raw; feeds oi-pivot-reversal-probability-by-tf)
1. Absorption bar = 1m volume rank in the top decile of the last 60 bars, |delta|/vol >= 0.35, price move < 0.15 x ATR: forward 5/15-bar return and whether the wick low/high is revisited; split by OI up/down on the next 5m.
2. Thin push = |delta|/vol >= 0.6 on below-median volume: does the next bar reverse? Compare with the base rate; report hit, miss, timeout.
3. Context columns: session (US open first 10 min), BB position, RSI vs 40 and SMA, VWAP side. Thresholds are OURS (DEV only, one VALIDATION check). Two bars today are an anecdote, not a sample.

## Watch
82,092.1 line (no touch yet; low 82,138.4) and VWAP 82,5xx above: a 1m bar with big positive delta that closes above 82,369 with OI flat or falling would be the first real buying; otherwise another sweep toward 82,092 with OI still rising = shorts still being added.
