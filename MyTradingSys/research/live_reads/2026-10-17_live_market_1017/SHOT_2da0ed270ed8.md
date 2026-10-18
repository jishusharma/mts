# 2026-10-18 BTCUSDT 6h shot (operator: "start recording/observing", resume the live log)
<!-- Process: methodology/screenshot_intake.md. Claim rows `| id | MATCH or MISMATCH or NOT_IN_DATA | claim | evidence |`. No trade advice; testnet only; no marks (G3 gated). Tag: LAB-VERIFY (see end). -->

Shots: 2da0ed270ed8 (6h)
Operator words: "Start recording/observing - retrieve our last discussion when we were doing screenshots ... be prepared to move our context, data, information, changes to the correct channels."
Clocks: CoinGlass TradingView page = UTC. Last bar = 10-18 12:00Z 6h bar, countdown 03:06:15 -> captured ~14:53:45Z (shell 14:55:09Z at fetch).
Pre-read (VVP-002 F.1): pass (OHLC header, right-edge price, countdown). Timeframes present: 6h only = SINGLE-TF, so this read is context, not a setup read. Panels: price + VWAP, OI candles, CVD candles, Net Delta. No BB, RSI or volume panel.
Data: Binance fapi 6h klines (1000 bars, from 02-10), 1m klines (last 1000), futures/data/openInterestHist 6h (30-day limit: from 09-18 18:00Z), fetched 14:55Z; mirror@2026-10-18 14:51Z. shot.py engine NOT run (SINGLE-TF context; engine state cited from the live snapshot 14:51Z).

## Carried context
Prior: MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SET_8dc83a2a31ed_ac1adc2a255f.md

Prior read (10-17 ~10:00Z): 09:59 flush to 81,550 under 5m lower BB and day VWAP 81,574.9, under weekly VAL 81,603.5; watch was "5m closes under VWAP, 12:00Z sellers or reclaim of weekly VAL". Falsify lines: none written.
Since then (fapi 6h): 10-17 12:00 bar went to 81,149.8 (delta -628); 18:00 bar flushed to 80,751.0 and closed 81,455.9; 10-18 00:00 and 06:00 bars rose to 82,268.7 (deltas +1,798, +2,697); 12:00 bar gave it all back, 82,100.3 -> 80,987.6 (delta -3,840). Net: weekly VAL not reclaimed and held as a ceiling on 10-17; the 10-18 push above it failed.

## Claims
| id | class | claim | evidence |
|---|---|---|---|
| 2da0ed270ed8-1 | MATCH | 6h header O 82038.5 H 82100.3 L 80987.6 C 81041.7 (-996.9, -1.22%) is the 10-18 12:00Z bar at ~14:53:45Z | fapi 6h 12:00 O 82038.5 H 82100.3 L 80987.6; 1m 14:53 O 81079.1 L 81041.6 C 81049.8, so 81041.7 is an intrabar price in that minute; 82038.5 - 81041.7 = 996.8 |
| 2da0ed270ed8-2 | MATCH | VWAP 81654.7 | the chart's VWAP is built from the chart's own 6h bars: hlc3 x volume of the 00:00, 06:00 and forming 12:00 bars (volume 19,828 at 14:55) = 81,653.6. A 1m-hlc3 day VWAP gives 81,680.8 and the engine's vwap.price is 81,676.03 (current_market_state.md). The ~26-point gap is bar granularity on a 6h chart, not a pipeline defect; on 5m/15m shots the two agree (prior read) |
| 2da0ed270ed8-3 | MATCH | OI candle O 94.8K H 94.864K L 92.891K C 93.7K | openInterestHist 12:00Z 94,808.5; mirror oi_1m.csv since 12:00Z: min 92,890.8 at 13:58:56Z (exact), max 94,849.2 at 12:09:57Z (chart 15 higher: finer sampling), 14:50:57Z 93,674.9 |
| 2da0ed270ed8-4 | MATCH | CVD candle step -8.407K -> -12.245K (-3,838) on the forming bar | Binance taker delta of the 12:00 6h bar at 14:55 = -3,840.0. Third most negative 6h delta of the last 40 bars (10-15 00:00 -5,751; 10-12 12:00 -4,727). Levels not compared |
| 2da0ed270ed8-5 | NOT_IN_DATA | Net Delta 9.685K -> 8.579K (-1,106) | no file holds the CoinGlass Net Delta series; recurring NOT_IN_DATA (screenshot_intake.md section 7) |
| 2da0ed270ed8-6 | MATCH | CVD falls from ~65K (late Aug) to -12.2K while price rose: sellers by taker flow, price held | sum of Binance 6h taker deltas: since 08-23 -80.5K (price 77,084.5 -> 81,069.6); since 09-21 -38.5K (81,144 -> 81,070); since 10-08 -14.4K (83,281.9 -> 81,069.6). Chart step ~-77K since late Aug by pixel (error ~3K) |
| 2da0ed270ed8-7 | MATCH | Price structure: Aug 15-19 base ~62.7-65K, rally to ~80K by Aug 21, Sep 21 spike to ~87.4K, 84-87K range to Oct 7, drop Oct 8, balance since | fapi 6h: 08-15..08-19 low 62,681.1 high 65,057.9; 09-21 00:00 low 80,819.4 -> 18:00 high 87,385.1; 10-08..now high 84,340.2 (10-12 06:00) low 79,732.3 (10-15 12:00) |
| 2da0ed270ed8-8 | MATCH | OI step down ~110K -> ~96K around Sep 23-24 | openInterestHist 6h: 09-23 12:00 106,267.5 -> 09-23 18:00 99,277.7 -> 09-24 18:00 95,653.0; 09-21/22 at 108-110.5K |
| 2da0ed270ed8-9 | MATCH | Engine state at the shot: weekly VP poc 81,661.01 / vah 83,194.48 / val 80,868.01 (rolled from last week's 83,422 poc), daily poc 81,695.71 / val 81,498.04, price under daily VAL; 4h VA 81,067.79-81,644.19; state S 4 bearish / 0 bullish | mirror current_market_state.md (14:51:09Z, last_price 81,079.2) + state_code.json (14:51:11Z; cvd_slope, price_vs_vwap, net_delta_1m, last_3_delta bearish) |
| 2da0ed270ed8-10 | MATCH | VWAP bands: price at the engine's -2s band | engine VWAP band_-2s 81,064.36, band_-1s 81,370.19; shot price 81,041.7 |

## Operator chart checklist (every line answered; 6h only)
| # | Item | Answer |
|---|---|---|
| 1 | Liquidity rays | absent (no operator rays; NOT_IN_DATA until T066). File levels: weekly VAL 80,868.0, 10-17 low 80,751.0, 10-15 low 79,732.3 |
| 2 | Spike bar | present: 10-18 12:00 bar, range 1,112.7, delta -3,840 (3rd largest negative in 10 days); OI fell 1.9K into 13:58 then rebuilt +0.8K as price kept falling |
| 3 | Bollinger dance | panel missing (no BB on this shot) |
| 4 | RSI divergence | panel missing |
| 5 | RSI 40/60 | panel missing |
| 6 | OI vs price | 12:00-13:58: price down, OI down 1.9K = longs closing; 13:58-14:51: price still down, OI up 0.78K = new positions into the fall (checklist convention). Engine quad at 13:58: long_liquidation (alert #449) |
| 7 | Ladder channel | absent at 6h |
| 8 | Bottom before spike | n/a now; Aug 15-19 base (62.7-65K) before the Aug 20-21 run is the chart's example |
| 9 | Confluence count | on the 12:00 bar: spike delta (2), OI new positions into fall (6), price at engine -2s band (claim 10) = 3 families; no momentum panel to add |
| 10 | Multi-TF band propagation | cannot be read: 6h only |
| 11 | Pop into upper BB | panel missing; the 06:00 bar high 82,268.7 = engine +2s band 82,287.7 minus 19, then reversed |
| 12 | Spike down is not a stop | measured: 2 h 53 min into the bar, delta -3,840, OI rebuilding; no opposite behaviour yet |
| 13 | Context before signal | Sunday (weekend true), US cash open per alert #449; weekly profile rolled to a lower POC (83,422 -> 81,661) |
| 14 | Higher-horizon | 2-month view: Aug rally, Sep 21 spike, 84-87K range, Oct 8 drop, balance 79.7-84.3K since; taker flow net negative throughout (claim 6) |

## Live system at the shot (mirror@2026-10-18 14:51Z)
- HALT + HALT_DAILY_LOSS still raised. Auto-trader restarted 10-18 06:43:48Z with both brakes; since 10-17 10:05Z every layer fire is `skipped_halt` (turn_of_candle 1m 113, rsi 5m 26, cryptocred, fabio, levels, session, bb_top_reversal). No trade opened.
- Tom: 19 rejections since the prior read; last tom#446 short 12:05:56Z and tom#448 long 13:55:57Z, both `verdict WAIT_PROOF`. Alert #449 13:58:08Z NO_TRADE "no candidates", state TWOPEAK/below_val -> TWOPEAK/in_va at 81,514.4.

## Tag: LAB-VERIFY
The engine labels the state `trend_healthy` while the 6h shows an 11-day balance (79.7-84.3K) and a full rotation today (82.1K -> 81.0K). Cause: mts_math.py:354-355 sets `trend_healthy` whenever price is `above_vah`/`below_val` of the daily VA (OURS rule), regardless of the higher-timeframe balance. Sent to the Lab via desk (DSA); this session does not verify it.

## Watch next
Whether the 12:00 6h bar closes under weekly VAL 80,868 (acceptance below, a new state) or wicks back into the 81.5-81.7K daily VA; HALT keeps every fire skipped regardless.
