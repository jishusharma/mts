# 2026-10-02 BTCUSDT screenshots, set oct02-coinglass (4 charts, read 2026-10-09 under Control Room decision D07)
<!-- Process: methodology/screenshot_intake.md. Read late (7 days after landing) on the operator's D07 "yes, close them out". -->

Shots: e86a0aadb83b, 0218083e8fd8, 97e7395bbd34, 05881d61f6b1
Operator words: "Can u apply the latest Fabio and Tom's consolidated set of rules - directly on this 1 day chart! Look at the complete picture ... what is happening in the current context of the Market?" (1d and 4h, 2026-10-02 ~18:23Z); "updates, what is exactly happening now" (the two 15m charts, ~20:17Z).
Clocks: CoinGlass TradingView pages = UTC (BTCUSDT Binance perp). The right edge is the paste time: 18:22-18:24Z for 4h/1d, 20:16-20:17Z for 15m (countdown 13:08 and 12:36 to the 20:30 close).
Pre-read (VVP-002 F.1): pass for OHLC header, timeframe, price axis; fail for operator marks (no operator drawing, only the page's own VWAP, VP and POC rays).
Operator marks: none drawn. Page overlays: VWAP 85,763.4 (15m), fixed-range volume profile with a red POC ray near 86.4-86.5K (15m), per-session profile boxes with red POC rays (4h, 1d).
Set timeframes present: 15m x2, 4h, 1d   missing: 1h, 5m, 3m (a read of context, not a full set)

## 1d (e86a0aadb83b) and 4h (0218083e8fd8)
- Window: 1d from 2026-08-15 to Oct 2; 4h from Sep 20 to Oct 2. Panels: price, OI, CVD, net delta.

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| A-01 | MATCH | 1d header O84,829.6 H87,249.6 L84,444.4 at 18:24Z | Dumps/backtest/raw/klines/BTCUSDT-1m-2026-10-02.csv up to 18:24Z: open 84,829.60, high 87,249.60, low 84,444.40 |
| A-02 | MATCH | 4h header C84,585.4 L84,444.4 at 18:22Z | same file up to 18:22Z: close 84,585.30, low 84,444.40 (0.1 USD from the chart's last tick) |
| A-03 | MATCH | 1d OI last 95.279K at 18:20Z; the fall from about 112K (09-21/22 highs) to the mid-90Ks | runtime/oi_live/oi_5m_30d.csv (Binance sumOpenInterest, BTC): 18:20Z 95,277.3 (0.002 % from the chart); 09-22 00:00Z 109,189, 09-24 00:00Z 98,503, 10-02 20:15Z 95,694. The 112K is a wick high of the CoinGlass aggregate, not in this file

## 15m (97e7395bbd34, 05881d61f6b1)
- Window: 2026-10-02 ~00:30Z to 20:17Z. 05881d adds OI delta, aggregated CVD, net longs/shorts panels.

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| B-01 | MATCH | 15m close 84,328.1 (97e7), 84,320.4 (05881d) at 20:16-20:17Z | klines 1m 2026-10-02 20:16Z close 84,328.00 |
| B-02 | MATCH | VWAP label 85,763.4 | hlc3 VWAP from 00:00Z to 20:16Z over the 1m klines = 85,759.9 (close-based 85,761.4); the 3.5 USD gap is the page's own price source. Anchored at 00:00Z, not 13:30Z (the 13:30Z anchor gives 85,307.8), which is the F-BT-12 anchor question |
| B-03 | MATCH | Red POC ray of the fixed-range profile at about 86.45K (pixel read +-40) | orderflow_live/2026-10-02.csv trade-level $10 profile 03:00-20:16Z: top nodes 86,300 (2,172) and 86,500 (2,034, 6 % less); the page's coarser bins pick the 86.5K node. Note F-BT-09: the MTS snapshot would not have shown this POC (Java weights not normalised) |
| B-04 | MATCH | Flush to about 84.0K after the 13:30Z top near 87.2K | klines: day high 87,249.60 at 12:31Z, low 83,841.90 at 18:47Z; the chart's low is read at about 84.0K (axis pixel read, 160 USD of slack) |
| B-05 | MATCH | OI +1K bar at 03:30-04:00Z and a run of negative OI-delta bars at 14:45-15:15Z; OI close 95.731K at 20:17Z | oi_5m_30d.csv: 03:30Z 98,222 -> 04:00Z 98,624 (+402 in 30 min, rise); 14:30Z 98,530 -> 15:15Z 97,045 (-1,485, fall); 20:15Z 95,694 (0.04 % from the chart). Magnitudes are CoinGlass aggregate, so only sign and order are claimed

## Across timeframes (set)
| Level or event | 3m | 5m | 15m | 1h | 4h | Agree? |
|---|---|---|---|---|---|---|
| High 87,249.6 (12:31Z) | - | - | seen | - | seen | yes |
| Close ~84.3-84.6K | - | - | 84,328 | - | 84,585 | yes (two times, 2 h apart) |

## Outcomes
| Claim id | Outcome | Item |
|---|---|---|
| A-03, B-05 | none | OI series on disk agrees with the chart (5m file, not the hourly-stepped snapshot field of F-BT-10) |
| B-02 | existing finding confirmed | F-BT-12 (VWAP anchor): the chart anchors at 00:00Z |
| B-03 | existing finding confirmed | F-BT-09 (fixed Java volume profile in 39520d4) |
