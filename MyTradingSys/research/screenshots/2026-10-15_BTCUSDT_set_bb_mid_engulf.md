# 2026-10-15 BTCUSDT screenshots, set bb_mid_engulf (29b79af8ff8f, 587ee73bd78c)

Shots: 29b79af8ff8f 587ee73bd78c
Operator words: see `MyTradingSys/research/setup_catalog_2026-10-15/sources/OPERATOR_2026-10-15_bb_mid_engulf.md` (relayed paraphrase, label OPERATOR). Draft row: `drafts/MAL-BB-MID-ENGULF.md`. Checks: `setup_catalog_2026-10-15/evidence/bb_mid_engulf_checks_output.txt`.
Clocks: CoinGlass tv page = UTC
Pre-read (VVP-002 F.1): pass: OHLC header, BB/RSI/SMA/OI/CVD/net-delta legends, the marked horizontal line 80654.5, forming-bar countdown timers
Operator marks: white horizontal line at 80654.5 across the 13:35-13:50 candles (the open of the last green bar before the red engulf)
Set timeframes present: 5m (both shots)   missing: higher timeframes (the operator says to check them; context only, from our 1h/4h recompute)

## Carried context
Prior: none

## 29b79af8ff8f 5m CoinGlass
- Window: about 10:45 .. 13:52 UTC, forming bar 13:50 (open 80342.3), countdown 02:19 so the shot is at about 13:52:41Z
- Panels and indicators: price + BB(20,2), OI, CVD, net delta, RSI14 + SMA14, StochRSI, volume

## 587ee73bd78c 5m CoinGlass
- Window: about 11:00 .. 13:54 UTC, forming bar 13:50 (open 80342.3), countdown 00:55 so the shot is at about 13:54:05Z
- Panels and indicators: same as above

| Id | Check | Chart claim | Data check and evidence |
|---|---|---|---|
| C-01 | MATCH | shot 1 legend: BB 80058.5 / 80615.8 / 81173.2, RSI 34.56, SMA 38.14 on the forming bar close 80083.6 | our 1m klines aggregated to 5m with that close: 80058.5 / 80615.8 / 81173.2, RSI 34.56, SMA 38.14 (exact) |
| C-02 | MATCH | shot 2 legend: BB 80015.7 / 80607.7 / 81199.7, RSI 31.86, SMA 37.94 on close 79920.3 | recomputed: 80015.7 / 80607.7 / 81199.7, RSI 31.86, SMA 37.94 (exact) |
| C-03 | MATCH | marked line 80654.5 | open of the 13:40 green 5m bar 80654.4 (and the 13:35 bar close 80654.5) |
| C-04 | MATCH | red 5m bar closes below the previous green bar's open | 13:45 bar O80680.0 C80342.4 against 13:40 green open 80654.4: 312.0 pts below (bar closed 13:50:00) |
| C-05 | MATCH | second break to 79,831 | 1m 13:53 low 79831.4 (the 13:50 5m bar final low 79818.0) |
| C-06 | MISMATCH | swept low "80,050" | no closed 5m bar has that low: 13:30 5m low 80027.0 (1m 13:31), forming-bar low at shot 1 80053.7; the number is read by eye |
| C-07 | MISMATCH | registered capture times 13:48Z (shot 1) and 13:54Z (shot 2) | countdown timers put shot 1 at about 13:52:41Z (forming 5m low 80053.7 = our 1m 13:52 low); shot 2 at about 13:54:05Z |
| C-08 | NOT_IN_DATA | CVD -11.14K then -11.938K; OI 94.14K then 94.174K | CVD anchor unknown; increments since the 13:50 open: chart -267 and -1065, ours -280 and -1260; OI: recorder is sparse (13:35 93106, 13:55 94010 BTC), fapi 5m history ends 13:40 |

## Outcomes
| Claim id | Outcome | Item |
|---|---|---|
| C-06 | noaction | note:operator's 80,050 is by eye; draft records the nearest lows 80027.0 and 80053.7 |
| C-07 | noaction | note:registered times are loose, draft uses the timer-derived 13:52:41Z and 13:54:05Z |
