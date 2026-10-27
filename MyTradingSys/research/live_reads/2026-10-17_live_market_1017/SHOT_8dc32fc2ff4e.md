# 2026-10-19 BTCUSDT 1m 13:53Z: operator's rising-lows line and flat CVD arrow
Prior: MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SHOT_dc0f695a740d.md
Shots: 8dc32fc2ff4e (CoinGlass 1m, UTC; header O 82189.9 H 82189.9 L 82186.3 = 13:53 bar, countdown 00:59 => ~13:53:01Z). Operator words: none (drawings: rising line under the lows 13:40-13:50, flat arrow on CVD). Data: Binance fapi 1m, openInterestHist 5m.
| id | class | claim | evidence |
|---|---|---|---|
| 8dc32-1 | MATCH | Header = 13:53 bar open | 13:53 O 82189.9 H 82189.9 (price 82,163 at the 13:53 close of data) |
| 8dc32-2 | MATCH | Lows 13:39-13:50 rise; line then broken | lows 82,138.4 (13:39), 82,180 (13:42), 82,240.5 (13:43), 82,201.7 (13:46), 82,308.7 (13:48), 82,234.7 (13:50), then 82,147.3 (13:51) under the line |
| 8dc32-3 | MATCH | CVD flat across the bounce | Binance taker delta 13:39-13:53 sums -26 BTC (CoinGlass CVD -190 on its aggregate); bounce high 82,426.5 (13:48) gave the whole move back |
| 8dc32-4 | MATCH | OI 94.362K flat-to-up | 5m OI 94,361 (13:40) -> 94,389 (13:50); up 494 vs 13:20 (93,895) while price fell ~600 from the open |
| 8dc32-5 | MATCH | RSI 38.67 under 40, SMA 40.81 | 1m RSI 37.5-39.6 at 13:51-13:53 |
| 8dc32-6 | NOT_IN_DATA | Net Delta -53.057, VWAP 82,496.8, BB 82,396.4/82,266.6/82,136.8, the drawn line | CoinGlass series/drawing |
Reading: the 288-pt bounce (82,138 -> 82,426.5) had no net buying (delta ~0), OI not falling (no short covering, no new longs): low-conviction, and the rising-lows line broke at 13:51 (delta -44). Price 82,163 sits 71 above the 82,092.1 line with BB lower 82,137. OI +494 since 13:20 on a falling price = shorts added. HALT unchanged. Prior watch (82,092.1 / close over 82,369 with OI flat or falling): 82,369-82,426 was reached at 13:48 with OI flat and no delta, then failed.
