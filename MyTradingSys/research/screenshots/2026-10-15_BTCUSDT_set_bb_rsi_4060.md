# 2026-10-15 BTCUSDT screenshots, set bb-rsi-4060 teaching example

Shots: 9317fd8402ed, 672453a288eb
Operator words: see `MyTradingSys/research/setup_catalog_2026-10-15/sources/OPERATOR_2026-10-15_bb_rsi_4060.md` (verbatim, label OPERATOR). Draft setup rows: `MyTradingSys/research/setup_catalog_2026-10-15/drafts/MAL-BB-RSI-4060.md`.
Clocks: CoinGlass tv page = UTC (axis labels 12:39, 12:51, 13:15 in UTC)
Pre-read (VVP-002 F.1): pass: cursor/OHLC header, BB/RSI legends, OI/CVD/net-delta legends visible in both shots
Operator marks: blue verticals at 12:39, 12:51, 13:15 (both shots); circles on price/RSI at each vertical and on the RSI at the 40 line (13:00-13:20); read from the x axis, +-1 bar
Set timeframes present: 1m (two shots 5 minutes apart)   missing: 5m, 15m, 1h (context only, not a multi-timeframe read)

## Carried context
Prior: none

## 9317fd8402ed 1m CoinGlass
- Window: about 11:25 .. 13:23 UTC, last bar 13:23 forming (open 80348.1)
- Panels and indicators: price + BB(20,2), OI (candles), CVD (candles), net delta, RSI14 + SMA14 with 40/60 lines, StochRSI, volume

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| A-01 | MATCH | BB legend 80458.0 / 80592.2 / 80323.7 (mid / up / lo) on the forming 13:23 bar | recomputed with the shot's close 80388.0: 80457.7 / 80592.8 / 80322.5 (evidence/bb_rsi_4060_indicators_output.txt) |
| A-02 | MATCH | RSI 39.05, SMA 37.98 on the forming bar | recomputed 39.27 / 38.00 from our 1m klines (within 0.22) |
| A-03 | MATCH | open interest 92.506K at the last bar | recorder oi_1m.csv 13:22:02 = 92500.4 BTC |
| A-04 | MATCH | RSI at vertical 12:39 reaches about 58-60 and turns down; price in the upper half of the BB | closed bar RSI 57.30, %B 0.74, next closes RSI 55.6, 53.5, 48.9 |
| A-05 | MATCH | vertical 12:51: price at the BB centre line, RSI at its blue SMA | bar high 80886.7 over mid 80843.7, close 80851.3; RSI 48.94 vs SMA 48.69 |
| A-06 | MATCH | vertical 13:15: wick to the centre line, RSI on the 40 line | high 80535.9 vs mid 80525.7; RSI 40.81, then 38.0 |
| A-07 | NOT_IN_DATA | CVD legend -1.79K absolute level | our taker-delta sum reproduces the per-bar signs but the chart's CVD start is unknown (ours from 11:30 gives -947 at 13:23) |

## 672453a288eb 1m CoinGlass
- Window: about 11:35 .. 13:28 UTC, last bar 13:28 forming (open 80267.7, shot 56 s into the bar)
- Panels and indicators: same as above

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| B-01 | MATCH | BB legend 80402.8 / 80552.9 / 80252.6 | recomputed with close 80234.1: 80402.3 / 80553.0 / 80251.7 |
| B-02 | MATCH | RSI 29.95, SMA 37.46 | recomputed 30.24 / 37.55 (within 0.29) |
| B-03 | MATCH | price closes below the lower band for several bars from about 13:27 | closes 13:27-13:30 have %B -0.06, -0.04, -0.07, -0.10 |
| B-04 | MATCH | OI rises at the end (92.838K to 93.015K in the last bar) while price falls | fapi 5m OI 13:25 92547 -> 13:30 93122 (+575 BTC) |
| B-05 | MATCH | net delta bar plunges at the break (legend -378.968, forming) | closed 13:28 bar taker delta -516.2, 13:27 -515.3 (the shot is mid-bar) |
| B-06 | NOT_IN_DATA | CVD legend -3.178K absolute level | anchor unknown; ours from 11:30 gives -2156 at 13:28 |
| B-07 | MATCH | operator: "US session is starting, so price has just started to break" | the break starts 13:26-13:27Z, four minutes before the 13:30Z US cash open; the claim holds as a rough timing, not to the minute |

## Outcomes
| Claim id | Outcome | Item |
|---|---|---|
| A-07 | feature | note:bb-rsi-40-60 setup draft |
| B-06 | feature | note:bb-rsi-40-60 setup draft |
