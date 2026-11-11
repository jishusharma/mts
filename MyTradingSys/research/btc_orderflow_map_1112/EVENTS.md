# EVENTS: BTC order-flow map A2/A3 on DEV 2022-02-01 .. 2024-05-31 (card btc-of-map-events-1112)

Frozen PREREG.md. Net = signed forward return minus 0.10 % round trip (fees.py Binance taker). Placebo = 1,000 draws seed 1112, same hour histogram / long-short count / 60-min de-clustering; band = mean net 1st..99th pct. n floor 180. VALIDATION NOT OPENED. A1 NOT_RUN (no aggTrades).

| Event | Horizon | n | mean net % | sd | t | share positive | placebo 1-99 % | session mix | Regime mix |
|---|---|---|---|---|---|---|---|---|---|
| A2 absorption | 15m | 170 INSUFFICIENT_N | -0.059 | 0.591 | -1.30 | 38.8 % | n/a | Asia 35 Europe 48 US 72 Late 15 | n/a 6 range 103 bear 10 bull 51 |
| A2 absorption | 60m | 170 INSUFFICIENT_N | -0.034 | 0.895 | -0.49 | 47.6 % | n/a | Asia 35 Europe 48 US 72 Late 15 | n/a 6 range 103 bear 10 bull 51 |
| A3 funding extreme | 15m | 819 | -0.090 | 0.321 | -8.04 | 32.2 % | -0.123..-0.075 | Asia 275 Europe 274 US 270 Late 0 | n/a 65 range 344 bear 127 bull 283 |
| A3 funding extreme | 60m | 819 | -0.075 | 0.562 | -3.82 | 37.2 % | -0.138..-0.045 | Asia 275 Europe 274 US 270 Late 0 | n/a 65 range 344 bear 127 bull 283 |

Marks (PREREG rule): A2 15m/60m INSUFFICIENT_N (n 170 < 180, floor not loosened; no verdict). A3 15m/60m: none (DEV mean net negative; gross = net + 0.10 = +0.010 % / +0.025 %, "gross only"; A3 15m also sits below the placebo band, i.e. worse than hour-matched random entries). No PASS/LEAD possible, VALIDATION not opened.
