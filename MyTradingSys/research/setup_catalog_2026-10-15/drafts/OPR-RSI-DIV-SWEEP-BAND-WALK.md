# DRAFT catalogue rows OPR-RSI-DIV-SWEEP, OPR-BB-UPPER-WALK, OPR-RSI-DIV-LOWER-TF: RSI regular bullish divergence at the weekly-pivot sweep, the 5m upper-band walk after the reclaim, and the same divergence on 1m/2m/3m (2026-10-15)

Status: DRAFT in its own file; `SETUP_CATALOG.md` is NOT edited. G0-G2 draft only: no backtest, no G3. Order flow is described, not advised. Not a trade call. Every parameter is OPERATOR (his words) or OURS (grid value or our rule, decided on DEV, never called his). Operator text (word for word): `../sources/OPERATOR_2026-10-15_rsi_div_band_walk.md`. Shot extract: `MyTradingSys/research/screenshots/2026-10-15_BTCUSDT_set_rsi_div_band_walk.md` (shot 8fc58204ee18, chart, BTCUSDT 5m CoinGlass TV Binance, about 15:24Z, clock UTC). Checks: `../evidence/rsi_divergence_mtf_checks.py` + `_output.txt` (our Binance 1m klines; 2m/3m/5m resampled). Siblings: `MAL-BB-RSI-4060.md` (BB with RSI 40/60, flow layering), `OPR-WEEKLY-LOW-ROUND-SWEEP.md` (the same sweep and reclaim, read through the lines), `OPR-PREOPEN-TOPS.md`.

Divergence terms follow Malkan's glossary (regular vs hidden; no new names): `MyTradingSys/research/setup_catalog_2026-10-15/malkan/MALKAN_DIVERGENCE_GLOSSARY.md` (built by the malkan-divergence session; on fast-track as commit 33893a09, checked 2026-10-15; the section headings 2.1, 2.3, 2.4 and 4 were confirmed in the fast-track copy). The glossary sections used: 2.1 (regular divergence, always contra-trend, close to close), 2.3 (regular bullish divergence: price lower low, RSI higher low, a buy signal inside a down trend), 2.4 (bar count 3 to 10 powerful, near RSI 40 strongest for bullish), 4 (his "bullish divergence" = regular bullish divergence = price lower low, RSI higher low). The sweep shape on the shot, a price lower low with an RSI higher low, is a REGULAR bullish divergence in that glossary; it is NOT a hidden (reverse, PRD/NRD) divergence, which would need a price higher low with an RSI lower low.

### OPR-RSI-DIV-SWEEP (row a) RSI regular bullish divergence at a sweep below the weekly pivot / lower band is the long trigger
1. **Name / trader.** Operator (OPERATOR): "look at the RSI divergence - that was the sinal to buy as well". Malkan term: regular bullish divergence (glossary 2.3; context inside a down trend, SOURCED for Malkan, only as a definition; his intraday use is NOT in the glossary, section 5).
2. **What you see.** Marked lines on the shot (all verified as exact 1m extremes): 79732.3 sweep low (1m low 13:55Z, also the day low), 80027.0 (1m low 13:31Z), 80743.5 (1m high 13:45Z), 81146.6 (1m high 11:40 and 12:25Z). At the sweep the 5m close pivots are P1 = bar 13:25 close 80192.6 (the 13:30 close) with RSI14 29.1 and P2 = bar 13:50 close 79842.4 with RSI14 30.7: price lower low, RSI higher low by 1.6 points (our Wilder RSI, adjacent close pivots, k = 2). The price wick (79732.3) is in the 13:55 bar, which closed 80164.5. The lower band at the sweep is 79916 on the chart (our 5m legend, current bar, 79918.0 on the closed-1m legend; 79916.4 with the chart's tick); the 13:50 close 79842.4 is below the then-lower band (79993.0, bar 13:50) and the 13:55 bar closed back above it (lower band 79947.9). The relay says "about 13:45Z" for the sweep: the 1m low is at 13:55Z (13:45 is the 80743.5 HIGH), so the relay time is about 10 minutes early.
   - After the divergence (5m): RSI14 crossed above 40 on the 13:55 bar (close 14:00Z, RSI 40.3), the first 5m close above 80743.5 was the 14:05 bar (14:10Z, 80950.0), RSI crossed above 60 and the first 5m close above 81146.6 were the 14:15 bar (14:20Z, 81270.0, RSI 61.7).
   - Order flow (our klines, taker delta = 2 x taker_buy - volume, BTC per 5m; CVD from 13:00Z, anchor ours): the 13:50 bar (the P2 bar) taker delta -1321 on volume 5423 (heavy sell flow into the low), then +113, +269, +923 (14:05), +372, +420 through 14:15; CVD from 13:00 from -2764 at the 13:50 close to -668 at the 14:15 close. The chart's CVD (about -10K to -5.2K), OI (92K to 93.8K) and Net Delta (+3.7K) are CoinGlass quantities: not reproduced (OI recorder has no 14:00-15:25 rows checked here, taker delta of the forming bar is -52 BTC against the chart's +3.718K).
3. **Entry, stop, target, management.** NOT STATED ("signal to buy"). Nothing is filled in. Illustration only: none.
4. **Context.** Down move 12:30-13:55Z, then the weekly-low sweep (`OPR-WEEKLY-LOW-ROUND-SWEEP.md`): the weekly low (1w candle low 80344.8) broke 13:22-13:26Z, 80K broke 13:53Z, the day low 79732.3 at 13:55Z. The divergence points sit inside that break.
5. **BTC visibility: YES.** Bars, RSI14 (Wilder), BB from 1m klines; taker delta and CVD from `taker_buy_volume`.
6. **Evidence.** 1 instance, 2026-10-15 (the same day as every sibling row; not independent). No ledger trade.
7. **Gaps.** Which pivots (swing lows, closes), how far apart in bars, the RSI level, whether the lower band or a marked line is the sweep reference, the confirmation (a bullish candle, a line reclaim): NOT STATED. Malkan's glossary gives bar counts (3 to 10) and a strongest level (RSI near 40) for the DAILY/weekly use; they are not the operator's and are used here only as grid values.

### OPR-BB-UPPER-WALK (row b) A 5m upper-band walk after a pivot reclaim is a continuation; the walk ends when closes return inside toward the mid
1. **Name / trader.** Operator (OPERATOR): "the band dance in BB 5 mins coming out of a break of weekly pivots". "Ends when closes return inside toward the mid" is the relay's reading, labelled OURS here, not the operator's words. BB(20,2) 5m (OPERATOR: "BB 5 mins"; 20 and 2 are the chart legend).
2. **What you see.** After the reclaim of 80743.5 (14:10Z) and 81146.6 (14:20Z), 5m closes sit near the upper band. Our table (`evidence` section E, %b = (close - lower) / (upper - lower)): %b >= 0.8 on every closed 5m bar from 14:05 to 15:20 (16 bars, still running at the last closed bar); %b >= 0.9 in two runs, 14:10-14:20 and 14:35-15:05; the bar high touched or crossed the upper band at 14:10, 14:15, 14:20, 14:25 and 14:45. The mid rose 24 points per 3 bars at 14:15 and 258-282 points per 3 bars at 15:10-15:20; BB mid 80528 at 14:05 to 81355 at the shot. At the shot: price 82319.2 (chart tick), upper 82794.9, mid 81355.6, lower 79916.4, RSI14 75.32 and SMA14 67.56: all five legend numbers reproduce EXACTLY from our klines once the last close is set to the chart's tick (our closed-1m legend alone gives upper 82791.4 and RSI 75.07).
   - The operator says the walk started "from about 14:20Z" (the relay); our 5m table has %b >= 0.8 from 14:05 and the first bar high above the upper band at 14:10. The 14:20 start is NOT matched; the walk bars begin earlier in our data.
   - Order flow (ours): 14:05 +923 BTC, 14:10 +372 (volume 5367), 14:15 +420, then 14:20 -118 and 14:25 -107 on thin volume (1123, 661), then 14:45 +1353, 15:05 +53, 15:20 -52. CVD from 13:00 turned positive in the 14:45 bar (+853). OI and the CoinGlass Net Delta/CVD of the chart: not reproduced.
3. **Entry, stop, target, management.** NOT STATED. Nothing filled in.
4. **Context.** Follows OPR-RSI-DIV-SWEEP and the reclaim; same single day.
5. **BTC visibility: YES.**
6. **Evidence.** 1 instance (14:05-15:20Z and still running at the time of writing), 2026-10-15. No ledger trade. The end of the walk is unobserved.
7. **Gaps.** "Dance": NOT STATED beyond closes hugging the band. Hug threshold, minimum bars, and what "return toward the mid" means: NOT STATED.

### OPR-RSI-DIV-LOWER-TF (row c) The same divergence may already show on 1m, 2m and 3m
1. **Name / trader.** Operator (OPERATOR): "there could be 1 min, 2 min and 3 min divergance already possible". A could, not a claim that it did.
2. **What you see.** Verified on our klines for the same two points (the bar closing at 13:30Z against the lowest close bar closing 13:45-13:56Z; evidence section F; RSI14 Wilder on each timeframe's own closes):

| TF | A (close at 13:30Z) | B (lowest close, sweep) | price | RSI (A, B) | RSI gap |
|---|---|---|---|---|---|
| 1m | 13:29 close 80192.6 | 13:54 close 79842.4 | lower low | 28.0, 28.9 | +0.9 |
| 2m | 13:28 close 80192.6 | 13:52 close 79916.0 | lower low | 29.1, 31.5 | +2.4 |
| 3m | 13:27 close 80192.6 | 13:51 close 79916.0 | lower low | 29.0, 33.6 | +4.6 |
| 5m | 13:25 close 80192.6 | 13:50 close 79842.4 | lower low | 29.1, 30.7 | +1.6 |

   So all four timeframes show a price lower low with a higher RSI low across the same two moments: yes, the divergence is visible on 1m, 2m and 3m too, with 3m the widest RSI gap.
   - When each is KNOWN. Signal time = close of the bar that is k bars after the second pivot (adjacent close pivot lows, B <= 10 bars apart, k = 2). Signals: 5m at 14:05Z (close of bar 14:00, price 80484.1; with k = 3, 14:10Z at 80950.0); 3m at 14:00Z (price 80164.5; k = 3: 14:03Z at 80382.5); 2m at 14:00Z (price 80164.5) only with the wider grid (k = 3, B = 30; 12 bars apart); 1m: no divergence between these two points under the adjacent-pivot rule (the 1m has intermediate close pivots), only a small one at 13:57 -> 14:00 (P1 close 80114.1 RSI 43.3, P2 80109.8 RSI 43.6, k = 2; signal 14:03Z at 80382.5), which is ABOVE the sweep and a 0.3-point RSI difference. In clock terms the 2m/3m (k = 2) signals are 5 minutes before the 5m one and 320 points lower in price.
   - Both readings are shown because the result depends on the rule: "same two points" gives divergence on all four timeframes, "adjacent pivots" gives 2m (wide grid), 3m and 5m but not 1m. The operator's "could be already possible" is true for 3m and 2m under the stated rule, and for 1m only under the "same two points" reading.
3. **Entry, stop, target, management.** NOT STATED.
4. **Context.** As row (a).
5. **BTC visibility: YES.**
6. **Evidence.** 1 instance.
7. **Gaps.** What "already possible" requires (the pivot rule, the bar count, the timeframe in which the signal is acted on): NOT STATED.

## Parameter table (every parameter labelled)

| parameter | value or definition | label |
|---|---|---|
| BB | 20 closes, 2 population SD on 5m | OPERATOR (BB 5 mins, 20 2 on the legend), OURS (population SD as reproduced) |
| RSI | 14, Wilder RMA on each timeframe's own closes, seeded over the 15-day history; SMA14 of the RSI | OPERATOR (RSI on the chart), OURS (Wilder, SMA14 as in the legend) |
| price pivot low | a close that is the minimum over k bars each side and itself, k = 2, 3 | OURS |
| regular bullish divergence | two adjacent close pivot lows, close(P2) < close(P1) and RSI(P2) > RSI(P1), at most B bars apart, B = 10 (glossary 2.4, W) and 30 | SHAPE: OPERATOR ("RSI divergence"), Malkan glossary 2.3 for the name; B and k: OURS |
| signal time | close of the bar k after P2 | OURS |
| RSI reference level | RSI at P2 below 40 (here 30.7) | OURS (Malkan W "near 40" is a daily/weekly statement, not the operator's) |
| sweep reference | the lower band or a marked line (79916/80027) | NOT STATED (OPERATOR gives the marked lines on the chart) |
| pivot-reclaim | first 5m close above 80743.5, then 81146.6 | OPERATOR (the marked lines, called weekly pivots) |
| band walk bar | closed 5m close with %b >= x, x = 0.7, 0.8, 0.9 | OURS |
| walk | at least 3 consecutive walk bars | OURS |
| walk end | first closed 5m bar with %b < 0.8, or < 0.5 (the mid) | OURS (the relay's reading "closes return inside toward the mid") |
| lower timeframes | 1m, 2m, 3m | OPERATOR (named) ; resample alignment OURS (epoch minutes) |

## Outcomes to measure (G5 sketch, DEV only, fee-net, NOT run, no card)

1. Divergence events (regular bullish, close pivots, k and B as above) on 1m, 2m, 3m, 5m with a sweep condition (the P2 low below the previous 12 h low, or below the lower band): next 15/30/60 min return, MFE and MAE in ATR units, n and Wilson CI; cells below n = 10 not read.
2. First signal timeframe: for events seen on 2m/3m before 5m, the clock gap and the price gap.
3. Band walk: after a 5m close above an earlier swing high, the distribution of walk length for x = 0.7, 0.8, 0.9 and the next bars after the end rule (mid return), against walks in a flat mid.
4. Fee-net R with METHOD.md fees (taker 5 bp + 1 bp slippage per fill) only if the frequencies show something.
5. Order flow as covariate: taker-delta sign and CVD slope at the signal bar, OI direction; described only.

No card is filed for this teaching: the study overlaps the BB/RSI and weekly-low cards (`opr-weekly-low-round-sweep-g5`, the MAL-BB-RSI-4060 divergence variants) and the operator gave no trade; it is a draft for the coordinator to card if wanted.
