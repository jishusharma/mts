# 2026-10-17 BTCUSDT 15m (operator read request: first RSI 60 cross, Malkan RSI rules)
<!-- Process: methodology/screenshot_intake.md. Claim rows `| id | MATCH or MISMATCH or NOT_IN_DATA | claim | evidence |`. No trade advice; testnet only; no marks (G3 blind-marks rule). -->

Shots: b3ab9b71a265 (15m)
Operator words: b3ab9b71a265 "15m: yesterday's 17:30 spike, price in a range since; RSI 14 is poking the 60 line for the first time on the 07:30 candle; asks what the market is doing, a bias, and whether Malkan's RSI rules (support at 60) are understood and usable in layers and analysis."
Clocks: CoinGlass TradingView page = UTC. Last bar opens 07:30Z (x-axis 06:00 / 09:00 ticks).
Pre-read (VVP-002 F.1): pass (timeframe 15m, OHLC header, BB 20 2, RSI 14 SMA 14, right-edge price). Only 15m present; no 1h/4h/1D, so the higher-timeframe RSI filter of Malkan cannot be read from this shot.

## Carried context
Prior: none

## Claims
| id | class | claim | evidence |
|---|---|---|---|
| b3ab9b71a265-1 | MATCH | RSI 14 on the forming 07:30 bar is 61.43 (SMA 14 52.56), first time at/above 60 since the 10-16 spike | Wilder RSI from public Binance 15m spot klines: 07:30 bar 60.88 forming at fetch (spot, later minute); last close >=60 before it was the 10-16 11:45Z bar |
| b3ab9b71a265-2 | MATCH | The 15m bar is a break above the upper Bollinger band (header BB 81554.2 mid, 81668.5 upper, 81439.9 lower); bar O 81614.1 H 81733.0 C 81674.4 | same klines: BB(20,2) upper 81,711 vs close 81,710 at fetch; shot is perp, klines are spot (about 40 offset), so pixel numbers are the shot's own |
| b3ab9b71a265-3 | MATCH | Price has ranged since the 10-16 17:30 bar (low ~80,8xx to ~81,8xx), compressed bands overnight | 1h klines 10-16 17Z L 80,809 (vol 1.65K BTC); 10-17 02Z-07Z 1h ranges 81,416-81,654 |
| b3ab9b71a265-4 | NOT_IN_DATA | OI 93.96K flat, CVD -5.74K, Net Delta +5.24K, StochRSI 100/96.79 (overbought), volume SMA9 59.8M | panel values from the shot; no engine snapshot at the shot minute (shot.py engine not run) |
