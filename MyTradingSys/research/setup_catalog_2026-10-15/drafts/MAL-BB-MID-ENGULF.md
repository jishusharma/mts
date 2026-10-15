# DRAFT catalogue row MAL-BB-MID-ENGULF: falling market, bounce to the BB midline, bearish engulf, second break (2026-10-15)

Status: DRAFT in its own file (sibling of `MAL-BB-RSI-4060.md`, which reads better with rows A-C unchanged); `SETUP_CATALOG.md` is NOT edited. G0-G2 draft only: nothing here has passed G3, no backtest was run.
Source of the idea: the operator's live 5m teaching, `../sources/OPERATOR_2026-10-15_bb_mid_engulf.md` (a relayed paraphrase, see its header). Data checks: `../evidence/bb_mid_engulf_checks.py` + `../evidence/bb_mid_engulf_checks_output.txt` (our own Binance 1m klines aggregated to 5m/15m/1h/4h). Shots: `29b79af8ff8f` (about 13:52:41Z), `587ee73bd78c` (about 13:54:05Z), BTCUSDT 5m CoinGlass, UTC.
Labels as in the sibling draft: SOURCED (Malkan) = his words in a transcript we hold; OPERATOR = the operator's own reading; OURS = a threshold or reading of ours (variant for G5, decided on DEV, never called the operator's or Malkan's).

### MAL-BB-MID-ENGULF Midline rejection confirmed by a bearish engulf, then a second break
1. **Name / trader.** Operator reading (OPERATOR); it adds a price-action confirmation to the sibling rows A-C. Malkan's part: his sell setup names "a bearish engulfing" at the sell signals, with no rule for it (Q8 below). Nothing from Tom or Fabio: `SETUP_CATALOG.md` has no row with an engulf.
2. **What you see.**
   - Market state (OPERATOR, M1): falling, under selling pressure. Our data: BB mid sloping down on 5m (80742.8 at 13:25, 80659.6 at 13:45, 80603.8 at 13:50 close), price below its 5m mid from 13:25.
   - Bounce to the midline (OPERATOR, M1): 5m 13:40 green bar O80654.4 H80719.4 C80680.0 (closed 5.6 pts below the mid 80685.6; high 33.8 above it); 5m 13:45 bar H80743.5 against mid 80659.6 (wick 83.9 above). The operator's marked line 80654.5 is the 13:40 green bar's open (80654.4) and also the 13:35 bar's close; the 80615 he quotes is the midline value on the chart at the shot (13:52:41), not at the bounce.
   - First confirmation (OPERATOR, M2): red 5m bar 13:45, O80680.0 C80342.4, closes 312.0 pts below the previous green bar's open (80654.4); its open equals the previous close, i.e. a full classic engulf too; body 337.6 against 25.6 (ratio 13.2). The bar closed at 13:50:00.
   - Second confirmation (OPERATOR, M3): the 13:50 bar breaks lower again: low 79831.4 at shot 2 (final low 79818.0, close 79842.4), below the 13:45 low (80273.7) and below the swept low. His "80,050" is not a closed-bar low in our data: the 13:30 5m bar low is 80027.0 (the 1m 13:31 low, 23 pts away) and the low of the forming bar at shot 1 was 80053.7; so "swept low" = the 13:31 wick, number read by eye.
   - Context (OURS, relay): RSI 31.86 below its SMA 37.94 and below 40; our recompute with the image's forming close substituted equals both legends exactly (shot 1 RSI 34.56 / SMA 38.14, BB 80058.5 / 80615.8 / 81173.2; shot 2 RSI 31.86 / SMA 37.94); with our last closed 1m close instead, shot 2 is 31.80 / 37.94. OI 94.14K -> 94.174K flat at its high on the chart.
3. **Entry, stop, target, management.** NOT STATED (the operator names two confirmations, not an entry). Nothing filled in. Illustration only, one instance and after the fact: entry at the open after the engulf closed (80342.3 at 13:50) moved 12.7 pts against and 610.0 pts in favour by the last closed 1m (13:55); entry after the second confirmation (79842.4 at 13:55) moved 313.2 against and 110.1 in favour (the 13:55 bar was still forming; round trip fees 12 bp = about 96 pts). The two entries differ by 500 pts and nothing says which the operator means: that is a G5 question.
4. **Context.** HTF momentum: "if they keep moving with the same momentum, lower-timeframe levels will be broken" (OPERATOR, M4); the number is NOT STATED. Our data at about 13:54: 15m RSI 31.64, 1h RSI 29.77, 4h RSI 31.22 (all below 50 and below 40), price below the 15m/1h/4h BB midline by 966 / 1345 / 2574 pts (OURS reading of "same momentum"). "The Bollinger Band can even expand" (OPERATOR, M4): the 5m BB width went from 1019 pts (13:25 close) to 1222 (13:50 close; 1186 at shot 2, forming) while price fell; a falling mid plus a widening band is the continuation picture in `bollinger_2026-10-14/SOURCES.md` s1 (rule 8: a close outside the band means continuation first), so the expansion supports the operator's M4 rather than contradicting M1.
5. **BTC visibility: YES.** Bars, BB, RSI, taker delta and HTF RSI from 1m klines (both legends reproduced exactly when the image's forming close is substituted: shot 2 BB 80015.7/80607.7/81199.7, RSI 31.86, SMA 37.94; screenshots extract C-01, C-02). CVD: increments since the 13:50 open are -280 (shot 1) and -1260 (shot 2) in our series against -267 and -1065 on the chart, so the sign and size match but the shot-2 figure is not reproduced (CoinGlass aggregates differently: sibling draft, section 1). OI: our 1m recorder is sparse (13:26 92579, 13:35 93106, 13:55 94010 BTC) and the fapi 5m history ends at 13:40 (93170, +48 over 13:30-13:40), so OI "flat at its high" is consistent with, not proven by, our data; CoinGlass level 94.17K is about 160 above the recorder's 94.01K at 13:55.
6. **Evidence.** 1 instance (13:40-13:55, 2026-10-15), the same hour and downtrend as the sibling rows A-C (not independent of them). No ledger trade.
7. **Gaps.** What a "bounce to the midline" is (touch, wick through, close within X of the mid): NOT STATED; here the bounce closed 5.6 below the mid. How big the engulf must be: NOT STATED (one instance, ratio 13.2; the previous candle was a 25.6-pt doji-like green bar, which makes the engulf trivially easy to satisfy). Entry and stop: NOT STATED. "Swept earlier" low: which low counts: NOT STATED. HTF "same momentum": NOT STATED. Whether the engulf is required or only an example: the operator says confirmations, not a rule; Malkan also says no rule (Q8).

## Parameter table (every parameter labelled)

| parameter | value or definition | label |
|---|---|---|
| market is falling under selling pressure | BB(20,2) mid on the signal timeframe lower than 10 bars ago (OURS slope test) and net delta over the last 6 bars negative (OURS) | OPERATOR (idea), OURS (test) |
| bounce reaches the midline | high of a 5m bar within the last 3 bars >= BB mid minus x% of band width (grid x = 0, 5, 10) | OPERATOR (idea), OURS (grid) |
| the marked line | the open of the last green bar before the engulf (80654.4; operator drew 80654.5) | OPERATOR |
| engulf, first confirmation | red bar whose close < the open of the previous green bar; previous bar green; DEV variants: (a) as stated, (b) also red open >= previous close, (c) body ratio >= r (grid 1, 1.5, 2) | OPERATOR (close < previous open), OURS (variants and r) |
| second confirmation | next 5m bar trades below the engulf bar's low (variant: below the swept low; variant: closes below the engulf low) | OPERATOR (breaks lower again), OURS (which of the three) |
| the swept low | lowest low of the last 12 5m bars before the bounce (operator's 80,050 is by eye) | OURS |
| HTF momentum filter | 1h RSI14 < 50 and 4h RSI14 < 50 and price below the 1h BB mid (relay default); variants: 15m/1h only, RSI < 40, no filter | OURS (relay default) |
| BB expansion | 5m BB width now > width 10 bars ago (reported, not required) | OPERATOR (mentioned), OURS (test) |
| flow context | OI change over 15 min (up / flat / down), CVD slope 15 min (down), net delta sign of the engulf bar | OURS |
| entry, stop, target | candidates only: entry at the open after the engulf closes or after the second confirmation; stop above the engulf high, above the BB mid, or k x ATR(14, 5m) (k = 1, 1.5, 2); exits: lower band, 1R/2R, time stop 6/12/24 bars | OURS |
| engulf size ratio default | chosen on DEV by the best fee-net separation at fixed n, one look on VALIDATION | OURS |

Malkan quote (checked by `verify_extract_quotes.py`):

Q8 (`extract_2HcJ3NeZmEQ.md:84`; primary, uploader Malkansview; a candlestick pattern shown at the sell signals, he gives no rule for it):

> "next sell signal where there is a small shooting star a bearish engulfing and all then then we get a strong downtrend"
**Source GPS: 2HcJ3NeZmEQ | MIDDLE**

Rule table for this row: operator rule M1 (midline bounce in a downtrend): NOT FOUND in Malkan, OPERATOR; M2 (bearish engulf as confirmation): Malkan names the pattern at sell signals (Q8) but no rule, so SOURCED (Malkan) only for "a bearish engulfing is seen at a sell signal"; M3 (second break): NOT FOUND, OPERATOR; M4 (HTF momentum): Malkan's multi-timeframe principle (Q4 in the sibling draft, `extract_cQ-y1oULkBw.md:248`) with no intraday numbers, OPERATOR; BB expansion: NOT FOUND, OPERATOR.

## Outcomes to measure (also on the G5 task card)

1. Per instance: continuation after the engulf and after the second break, in ATR(14, 5m) units: MAE and MFE to +6, +12, +24 bars, short measured separately from long.
2. Hit rates and mean fee-net R for the three candidate entries (engulf close, second-break close, retest of the midline) with the stops and exits above, per trial in the ledger.
3. Same location without the engulf (controls): bounce-to-mid bars with no engulf; random time shift within the same day.
4. Whether the HTF filter (relay default vs variants) changes the outcome: with and without it, 2 x 2 flow splits only (n small).
5. Whether the first-confirmation-only trade beats the second-confirmation trade fee-net (the two entries differ by about 500 pts here).
6. Every table prints n and a Wilson interval; a cell with n < 10 is not read. Holdout sealed; VALIDATION once after the DEV choice.
