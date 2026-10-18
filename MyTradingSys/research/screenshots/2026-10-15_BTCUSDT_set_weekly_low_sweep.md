# 2026-10-15 BTCUSDT screenshots, set weekly_low_sweep (4e8ef8d3f2e5, 3016b2621f9d)

Shots: 4e8ef8d3f2e5 3016b2621f9d
Operator words: see `MyTradingSys/research/setup_catalog_2026-10-15/sources/OPERATOR_2026-10-15_weekly_low_round_sweep.md` (relayed paraphrase, label OPERATOR). Draft row: `drafts/OPR-WEEKLY-LOW-ROUND-SWEEP.md`. Checks: `setup_catalog_2026-10-15/evidence/weekly_low_sweep_checks_output.txt`.
Clocks: CoinGlass tv page = UTC
Pre-read (VVP-002 F.1): pass for 4e8ef8d3f2e5: OHLC header, BB/RSI/OI/CVD/net-delta legends, four marked horizontal levels, countdown timer. 3016b2621f9d: not a chart (Claude desktop "New session" screen), nothing to pre-read
Operator marks: white horizontal lines at 81146.6, 80743.5, 80027.0 and 79732.3
Set timeframes present: 1m (4e8ef8d3f2e5 only)   missing: others (context only)

## Carried context
Prior: none

## 4e8ef8d3f2e5 1m CoinGlass
- Window: about 10:55 .. 14:09 UTC, forming bar 14:08 (open 80685.2), countdown 00:06 so the shot is at about 14:08:54Z
- Panels and indicators: price + BB(20,2), OI, CVD, net delta, RSI14 + SMA14 with 40/60, StochRSI, volume

## 3016b2621f9d (not a chart)
- Shows the Claude desktop "New session" screen, no market data; classified as a follow-up chart (81,293 / OI 93.28K / net delta +488 / RSI 77) by the relay, so those numbers are checked against our klines instead

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C-01 | MATCH | marked line 81146.6 (pre-open top) | 1m high 81146.6 at 12:25Z |
| C-02 | MATCH | marked line 79732.3 (sweep low) | 1m low 79732.3 at 13:55Z (also the 1w and 1d candle low) |
| C-03 | MATCH | marked line 80027.0 | 1m low 80027.0 at 13:31Z |
| C-04 | MATCH | marked line 80743.5 | 1m high 80743.5 at 13:45Z |
| C-05 | MATCH | forming 1m bar O80685.2 L80679.4, RSI 67.52, OI 94.077K | 1m 14:08 O80685.3 L80679.4 (bar closed C80823.0, RSI 68.1 at close); OI recorder 93939 at 14:07, chart about 140 higher |
| C-06 | MISMATCH | relay: prior-week low 80,393 | Binance 1w candle 10-05..10-11 low 80344.8 (1m 10-08 17:26); 80393 is only where price first closed below it on 13:11 |
| C-07 | MISMATCH | 3016b2621f9d classified as a chart of the 81,293 follow-up | the image is the Claude desktop "New session" screen; no market data |
| C-08 | MISMATCH | relay: top 81,146.6 broken at 14:11 with net delta +488 | first 1m high above it 14:10 (81390.5, close 81242.6); taker delta 14:10 +1026, 14:11 -51; the Net Delta panel is a different quantity |
| C-09 | NOT_IN_DATA | relay: OI fell to 93.28K at 14:11 (shorts covering) | recorder has no row after 14:07 (93939); fapi 5m OI history ends 13:40 |

## Outcomes
| Claim id | Outcome | Item |
|---|---|---|
| C-06 | noaction | note:draft uses the 1w candle low 80344.8 and records the relay value 80393 as not reproduced |
| C-07 | noaction | note:the image has no market data; the follow-up numbers were checked against our klines instead |
| C-08 | noaction | note:draft records the timeline from our 1m bars (break 14:10, delta +1026 then -51) |
