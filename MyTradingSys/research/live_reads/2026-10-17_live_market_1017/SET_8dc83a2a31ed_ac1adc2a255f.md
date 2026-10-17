# 2026-10-17 BTCUSDT 15m + 5m set (operator live paste, ~10:00Z: the 09:59 flush)
<!-- Process: methodology/screenshot_intake.md. Claim rows `| id | MATCH or MISMATCH or NOT_IN_DATA | claim | evidence |`. No trade advice; testnet only; no marks (G3 blind-marks rule: draw rebuild not checked as shipped). -->

Shots: 8dc83a2a31ed (15m), ac1adc2a255f (5m)
Operator words: none sent with the paste (no text with the images). Meaning taken from the pair: a live look at the moment, 15m for position/flow panels, 5m for BB + RSI.
Clocks: CoinGlass TradingView page = UTC. 5m shot: last bar opens 10:00Z, countdown 03:58 -> captured ~10:01:02Z (shell clock 10:01:44Z at fetch). 15m shot: x-axis ticks 6px per bar, last bar opens 09:45Z, countdown 00:19 -> captured ~09:59:41Z, i.e. 19 s before the 09:45 bar closed, about 80 s before the 5m shot.
Pre-read (VVP-002 F.1): pass (both OHLC headers, right-edge prices, countdowns). Timeframes present: 5m, 15m. Missing: 1m, 1h, 4h, 1D. 15m shot has no BB or RSI panel; 5m shot has no Net Longs/Shorts panels.
Data: Binance fapi 1m klines (perp, public, closed bars plus the forming minute) fetched 10:01:44Z; mirror@2026-10-17 10:01Z (live_mirror pull). shot.py engine NOT run (no scratch raw dir built); VWAP/VP numbers below come from the live snapshot at 10:01:14Z and from my own 1m recompute.

## Carried context
Prior: MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SHOT_b3ab9b71a265.md

Prior read b3ab9b71a265 (15m, 07:30 bar): RSI poking 60 for the first time, bar through the upper BB, high 81,733, OI 93.96K. Falsify lines of that read: none written.
Since then (same files): that 07:30-07:45 high 81,733.0 is still the day high (fapi); price ground sideways-up on thin 5m volume to 81,707.8 (09:53), then fell in the last minute of the 15m bar. OI 93.96K -> 94.08-94.15K (+120 to +190 BTC).

## Claims
| id | class | claim | evidence |
|---|---|---|---|
| 8dc83a2a31ed-1 | MATCH | 15m header O 81636.6 H 81707.8 L 81626.4 C 81651.7 is the 09:45 bar caught 19 s before close | fapi 1m: 09:45 open 81636.6, 09:53 high 81707.8, 09:48 low 81626.4; 09:59 minute open 81671.0 then low 81550.0 and close 81573.7, so 81651.7 is an intrabar price before the last-19-second drop. 15m bar closed C 81573.7, L 81550.0 |
| 8dc83a2a31ed-2 | MATCH | 15m OI 94.081K at the shot | oi_1m.csv (mirror): 09:58:52Z 94,080.2, 09:59:59Z 94,131.7 (fapi openInterest sampled each minute) |
| 8dc83a2a31ed-3 | MATCH | 15m agg CVD step is up (-12.818K -> -12.722K, +96 coins) while price fell at the end | direction only: Binance taker delta 09:45-09:58 = +46.8 BTC, then -158.3 BTC in 09:59. Chart panel is aggregated futures (all exchanges), so the size differs; step sign over 09:45-09:59:41 agrees. Levels not compared (anchored at first loaded bar) |
| 8dc83a2a31ed-4 | NOT_IN_DATA | Net Longs 3.22K, Net Longs(New) -911.9, Net Shorts -874.3, Net Shorts(New) 5.592K and their 10-16 17:45 step-down (Net Shorts 1.9K -> ~0) | no file holds CoinGlass net long/short series; recurring NOT_IN_DATA (screenshot_intake.md section 7) |
| 8dc83a2a31ed-5 | MATCH | 15m: the 10-16 17:30 bar is the spike bar (large green bar, OI down at it, agg CVD step -) | fapi: 5m 17:30 O 80871.3 H 82092.1 L 80860 C 81395.7, volume 8,279 BTC (1,051 in the bar before); chart bar around x=1400 is the 17:30/17:45 area. Pixel read, +-1 bar |
| ac1adc2a255f-1 | MATCH | 5m header O 81573.7 H 81584.8 L 81533.0 C 81543.9 (-29.9) for the 10:00 bar | fapi: 10:00-10:01 O 81573.7 H 81584.8 L 81533.0; 1m close 81543.8 at 10:00 minute end, 81537.9 at 10:01:44 (later) |
| ac1adc2a255f-2 | MATCH | BB 20 2: mid 81653.1, upper 81730.9, lower 81575.2 | recompute BB(20,2) of 5m closes incl. forming bar: mid 81652.8 / upper 81732.3 / lower 81573.2 at the later minute (close 81537.9 vs 81543.9 on the shot); within 2 of the shot |
| ac1adc2a255f-3 | MATCH | RSI 14 = 35.18, RSI MA 51.40 | Wilder RSI on the same closes: 34.6 at the later minute (close 6 pts lower); 0.6 apart, consistent |
| ac1adc2a255f-4 | MATCH | 5m CVD step on the forming bar 2.927K -> 2.881K (-46) | Binance taker delta of the 10:00 5m bar at 10:01:44 = -45.6 BTC (2 minutes in) |
| ac1adc2a255f-5 | MATCH | 5m OI 94.149K | oi_1m.csv 10:00:56Z 94,152.1 |
| ac1adc2a255f-6 | NOT_IN_DATA | 5m Net Delta 2.496K and CVD 2.881K as levels | levels anchored at the chart's first loaded bar; steps only (claims 3, 4) |
| ac1adc2a255f-7 | MATCH | The big green 5m bar at ~17:30 (volume spike to the 9.34M-axis top) is 10-16 17:30Z | fapi 5m 17:30 volume 8,279 BTC vs 658-1,666 around it |
| ac1adc2a255f-8 | MATCH | Price lost the 5m lower BB at the 09:59 drop; last 5m closes under the middle band since 09:59 | fapi 1m 09:59 low 81550.0 < lower band 81575.2; BB lower 81575.2 sits on day VWAP 81574.9 (live snapshot VWAP 81574.89, my recompute 81574.9) |
| ac1adc2a255f-9 | MATCH | The live RSI layer saw the 40 cross: rsi_events 5m short, RSI 37.75, t_close 09:55 bar | mirror runtime/alerts/5m.jsonl (down cross level 40, rsi 37.747, t_close 1792230900000 = 09:55Z bar, confirmed at its close ~10:00); auto_trades.jsonl 10:00:31Z `skipped_halt` rsi:rsi_events:cross:5m side short, brakes HALT + HALT_DAILY_LOSS |
| ac1adc2a255f-10 | MATCH | Engine state at the shot minute: weekly VAL 81,603.48 lost (price 81,543.8 under), daily POC 81,568.35 just above, daily VAL 81,484.76 below; state S (3 bearish / 0 bullish) at 10:01:14Z | mirror current_market_state.md + state_code.json (signals net_delta_1m, last_3_delta, volume_ratio bearish; cvd_slope and price_vs_vwap neutral; weekend true) |

## Operator chart checklist (operator_chart_checklist.md; every line answered)
| # | Item | Answer |
|---|---|---|
| 1 | Liquidity rays | absent: no operator rays on either shot (NOT_IN_DATA until T066). Level context from files: 10-16 flush low 80,809 (17Z), daily VAL 81,484.8 under price, weekly VAL 81,603.5 just lost |
| 2 | Spike bar | present, small: the 09:59 minute, taker delta -158 BTC, range 121 points (81671 -> 81550), OI +52 then +20 after it (oi_1m 09:58:52 -> 09:59:59 -> 10:00:56). No big volume bar (5m 09:55 volume 288 BTC vs ~100 before). Not the 10-16 17:30 type (8,279 BTC) |
| 3 | Bollinger dance | 5m present: rode the upper half 07:40-09:55 (upper 81,731; high 81,707.8 stayed 24 under it), 09:59 dropped through the middle (81,653) to below the lower (81,575). 15m: panel missing |
| 4 | RSI divergence | 5m: RSI highs at 07:40-09:40 sit at/near the 60 line while price made 81,707.8 at 09:53; no clean lower-high pattern readable by pixel (error ~2 RSI pts); not claimed |
| 5 | RSI 40/60 (Malkan) | 5m present: RSI touched 60 repeatedly (green line), MA 51.4, then lost 40 at the 09:55 bar close (live layer fired a short, HALT-skipped), now 35.18 under the red 40 line with its MA (51.4) above. 15m: panel missing |
| 6 | OI vs price | OI rose (94.08K -> 94.15K) as price fell 09:59-10:01: new positions into the fall (per checklist convention) |
| 7 | Ladder channel | present on 5m 08:00-09:55: equal small candles, shallow rise, ~100 BTC per 5m, low volume; ended by the 09:59 drop |
| 8 | Bottom before spike | not applicable now; yesterday's 17:30 spike came from the 80,780 low (5m 17:25 low 80,780, RSI under 30 in the 5m panel just before) |
| 9 | Confluence count | on the 09:59/10:00 5m bar: items 3 (lost lower BB), 5 (RSI under 40, MA above), 6 (OI up into fall) agree = 3 families at one bar; 2 weak. What price does next is the data for the probability layer (not measured here) |
| 10 | Multi-TF band propagation | cannot be read: only 5m (BB panel) and 15m (no BB panel) present; 1m/3m/10m missing |
| 11 | Pop into upper BB | absent as a pop: the 09:53 high 81,707.8 reached 81,730.9 upper minus 23 (15% of band width 157): "in the vicinity" by the OURS fraction guess, not a pass-through; market was not falling then |
| 12 | Spike down is not a stop | the 09:59 flush measured: CVD step -46 (5m), -158 (09:59 minute), OI +72, RSI 35, state S 3-0; sustained opposite behaviour not yet present (only 2 minutes since) |
| 13 | Context before signal | Saturday (state_code weekend true), asia/europe session, volume thin (5m 100 BTC), balance/in_va classification, before the 12:00 move window; sentiment not in data |
| 14 | Higher-horizon | 10-16: 11Z spike to 82,941, 17Z flush to 80,809, then recovery to 81.2-81.7k and a flat grind (prior read). Weekly POC 83,422 is 1.9k above, prior-day POC 82,297.9; price is under weekly VAL and prior-week POC 83,007.8 |

## Live system at the shot (mirror@2026-10-17 10:01Z)
- HALT and HALT_DAILY_LOSS both still raised; every layer fire is `skipped_halt`: turn_of_candle 1m long at 09:31, 09:45, 10:00:31 and rsi 5m short at 10:00:31 (bracket SAMPLING). No trade opened. Tom: tom#411 short rejected 09:30:10 (net_rr 0.5 < 1.25), tom#412 long rejected 09:52:31 (verdict WAIT_PROOF).
- Fabio 15m cvd_absorption bearish_absorption alert is the last in alerts/15m.jsonl (price 81,626.01, cvd 807.9 vs 693.4): not a fire row in auto_trades in this window.
- daily_loss_monitor: breached_today false; 18 accounts at day-start equity (flat).

## Watch next
Whether 5m closes hold under the lower BB and day VWAP (81,574.9) and whether the 12:00Z move window gets sellers or a reclaim of weekly VAL 81,603.5; the HALT flags keep every fire skipped regardless.
