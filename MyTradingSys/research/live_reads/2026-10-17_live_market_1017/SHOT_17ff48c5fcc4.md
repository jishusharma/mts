# 2026-10-19 BTCUSDT 1m 14:02Z: the flat-CVD rising-lows structure breaks, 82,092.1 lost
Prior: MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SHOT_8dc32fc2ff4e.md
Shots: 17ff48c5fcc4 (CoinGlass 1m, UTC; header O 81920.2 H 81920.2 L 81835.0 = 14:02 bar, countdown 00:17 => ~14:02:43Z). Operator words: none (drawings: rising line under 13:41-13:52 lows, flat CVD arrow). Mirror: mirror@2026-10-19 14:01Z. Data: Binance fapi 1m, openInterestHist 5m.
| id | class | claim | evidence |
|---|---|---|---|
| 17ff4-1 | MATCH | Header = 14:02 bar | 14:02 O 81920.2 H 81920.2 L 81835.0 (data close 81,879.8 later in bar) |
| 17ff4-2 | MATCH | Rising-lows line broken, CVD arrow flat until it breaks | lows 82,115.7 (13:53), 82,110.0 (13:55), 82,110.1 (13:58) then 13:59 low 82,010.0; 13:50-13:58 delta sums +16, then -216 (13:59), -595 (14:00), -25, -104 |
| 17ff4-3 | MATCH | The flush lost 82,092.1 on volume | 13:59 volume 479 BTC (6x the 82-bar average), 14:00 volume 969 BTC (largest 1m bar of the session), trades 8,093 and 9,052 vs ~3,000 |
| 17ff4-4 | MATCH | OI jumps on the flush | CoinGlass last candle 94.764K from ~94.36K; Binance 5m OI 94,343 at 14:00, 14:05 not yet published: price down + OI up + delta negative = new shorts |
| 17ff4-5 | MATCH | RSI 25.45 below its SMA 36.40 | 1m RSI14 14:02 = 25.1 |
| 17ff4-6 | NOT_IN_DATA | CVD -875.0, Net Delta -490.9, VWAP 82,466.1, BB, Stoch RSI | CoinGlass aggregated, not reproduced |
Reading: 13:51-13:58 was a quiet drift on ~0 delta; 13:59-14:02 flushed -275 pts (82,110 -> 81,835). Live: HALT + HALT_DAILY_LOSS raised; mirror shows only rsi-5m short skips (13:41, 13:56, right side), a long skip 13:50 (wrong side), Tom longs rejected WAIT_TRIGGER (13:43) / WAIT_PROOF (13:49), no signal at the break. Watch: 81,758 prior-day VAH, 81,600 (10-17 POC), 81,500 reclaim zone; a bounce into 82,092 on low delta = failed retest. HALT unchanged.
