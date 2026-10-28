# 2026-10-15 BTCUSDT screenshots, set rsi_div_band_walk (8fc58204ee18)

Shots: 8fc58204ee18
Operator words: see `MyTradingSys/research/setup_catalog_2026-10-15/sources/OPERATOR_2026-10-15_rsi_div_band_walk.md` (word for word, label OPERATOR). Draft rows: `drafts/OPR-RSI-DIV-SWEEP-BAND-WALK.md`. Checks: `setup_catalog_2026-10-15/evidence/rsi_divergence_mtf_checks_output.txt`.
Clocks: CoinGlass tv page = UTC
Pre-read (VVP-002 F.1): pass: OHLC header (O82269.9 H82319.2 L82124.0 C82319.2), BB 20 2 legend (81355.6 / 82794.9 / 79916.4), RSI 14 SMA 14 legend (75.32 / 67.56), OI, CVD and Net Delta legends, five white horizontal levels with price labels (81146.6, 80743.5, 80027.0, 79732.3 and the BB mid/upper tags), two yellow lines (price and RSI), countdown timer 00:48
Operator marks: white horizontal lines at 81146.6, 80743.5, 80027.0 and 79732.3; yellow line on price from about 13:30 to the low bar and yellow line on RSI over the same two lows
Set timeframes present: 5m   missing: 1m, 2m, 3m (the operator asks whether they show the divergence; checked from klines)

## Carried context
Prior: none

## 8fc58204ee18 5m CoinGlass
- Window: about 06:30 .. 15:24 UTC, forming bar 15:20 (open 82269.9), countdown 00:48 so the shot is at about 15:24:12Z
- Panels and indicators: price + BB(20,2), VWAP (hidden), OI candles, CVD candles, Net Delta, RSI14 + SMA14 with 40/60 lines, StochRSI, volume

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C-01 | MATCH | marked lines 79732.3, 80027.0, 80743.5, 81146.6 | 1m low 13:55Z, 1m low 13:31Z, 1m high 13:45Z, 1m high 12:25Z (also 11:40Z) |
| C-02 | MATCH | header O82269.9 H82319.2 L82124.0 C82319.2 | 5m bar 15:20 O82269.9 L82124.0; H/C are the live tick (our 1m closed through 15:23: H82307.6 C82284.0) |
| C-03 | MATCH | BB 20 2: 81355.6 / 82794.9 / 79916.4; RSI 75.32, SMA 67.56 | exact once the last close is set to 82319.2: BB 79916.4 / 81355.6 / 82794.9, RSI 75.32, SMA 67.56 |
| C-04 | MATCH | yellow lines: price lower low with RSI higher low at the sweep | 5m close pivots: 13:25 bar close 80192.6 RSI 29.1, 13:50 bar close 79842.4 RSI 30.7; 1m/2m/3m same two points also lower low, RSI higher low |
| C-05 | MATCH | RSI crossed 40 and later 60 | 5m RSI 40.3 at the 13:55 bar (14:00Z); 61.7 at the 14:15 bar (14:20Z) |
| C-06 | MATCH | price reclaimed 80743.5 and 81146.6 | first 5m close above: 14:05 bar (80950.0), 14:15 bar (81270.0) |
| C-07 | MISMATCH | relay: swept to 79,732.3 at about 13:45Z | the 1m low 79732.3 is at 13:55Z; 13:45Z is the 80743.5 high |
| C-08 | MISMATCH | relay: from about 14:20Z the walk of the upper band | 5m closes %b >= 0.8 from the 14:05 bar (16 bars to 15:20), high >= upper from 14:10 |
| C-09 | MISMATCH | Net Delta panel +3.7K | our taker delta of the forming 5m bar is -52 to -111 BTC; the CoinGlass Net Delta is a different quantity or unit |
| C-10 | NOT_IN_DATA | CVD about -10K to -5.2K, OI 92K to 93.8K | CoinGlass CVD anchor unknown; our CVD from 13:00 is -2764 at 13:50 and +2126 at 15:20 (anchor ours); OI recorder not checked for 13:00-15:25 |

## Outcomes
| Claim id | Outcome | Item |
|---|---|---|
| C-07 | noaction | note:draft records the sweep low at 13:55Z from our 1m bars |
| C-08 | noaction | note:draft records the walk from our 5m table (starts 14:05 at %b >= 0.8) |
| C-09 | noaction | note:order flow is described from our klines; the CoinGlass panel is listed as not reproduced |
| C-10 | noaction | note:CVD/OI of the chart not reproduced; our CVD anchored 13:00Z shown instead |
