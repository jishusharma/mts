# Moving-average layer: concepts (2026-11-07)

Operator ask (2026-11-06 18:14Z, voice): MTS must know moving averages the way Krown and the guru canon use them, per timeframe, like the candle-flip strip. Method: phase first, no backtest gate (d-phase-first-method-1106). This is a DISPLAY layer: it reports state, it gates nothing and places nothing. Evidence status for MA rules on BTC is in `research/btc_ma_2026-10-03/Q_ALL_ma_findings.md` (only the ~1-week price-to-MA ratio has OOS support; crossovers and cycle lines are folklore at our bar, n <= 4 cycles). Labels: SOURCED = quote and file or URL; OURS = our choice.

## (a) What Krown does with moving averages (SOURCED from our extracts only)

Rule ids are in `research/krown_ta101_2026-10-13/KROWN_CONSOLIDATED.md` section M (lines 98-114); quotes are in `extracts/extract_-NXzJs5JRks.md` (NXz) and `extracts/extract_vjzy_KxJ_y8.md` (vjzy).

| Topic | What he does | Source |
|---|---|---|
| Starter set | 21 EMA + 55 EMA (short and medium trend, "turn with the market") + 200 simple ("more stubborn"), on any timeframe, higher timeframe = more powerful. His live stack: ribbon 5, 21, 55, 377 EMA plus 200 simple. | KR-M01; NXz-09 "We're going to be using a 21 and a 55 EMA. And then we're going to use a 200 simple moving average" |
| 200 SMA | The line to have on the chart at all times: price "almost always will have a reaction any time it comes into contact with the 200 simple moving average on almost any time frame for the first time in a long time". In an uptrend with price above the 200, corrections to it are "at least a good bounce area for a scalp". | KR-M03; NXz-08, NXz-25 |
| 200 SMA vs 200 EMA | He says both carry value ("one would be a 200 EMA or 200 SMA. Both of these I find significant amounts of value in") and makes NO choice between them; his stack uses the SMA. Reading: SMA = the stubborn slow line (equal weights, turns late); EMA reacts faster and is "faked out faster", his favourite family (KR-M08). So we show both and label the gap between them, we do not pick a winner. | vjzy-20 (t=00:11:55); KR-M01 note; KR-M08 |
| 21 and 55 EMA | In uptrends dynamic support: "buy between the two lines"; "the distance between the 21 and the green 55 EMA, that is a zone of interest"; a rising 55 EMA is "a support zone walking uphill". | KR-M05; NXz-13, NXz-14 |
| 21 vs 55 cross ("Silver Cross") | Short and medium trend turning; strongest with the 200 SMA: below the 200 plus a down-cross preceded the big drops, a cross plus a reclaim of the 200 was the reversal; fails in chop. He says (claim, T3) the daily cross is right "more than 80 %, less than 95 %". | KR-M02; NXz-11; KR-F08 |
| 50/200 golden and death cross | 50 SMA above 200 SMA = long-term upside, not short-term; a death cross while the 200's slope is still up is ignored, with the 200 sloping down it starts the long downtrend: "looking to sell any rally towards that 200 simple". | KR-M07; NXz-20 |
| Pair rule | Lower-period average above higher-period average = that trend probably up: 5/21 short term, 21/55, 200/377 very long term. | KR-M09 |
| Slope | Slope of an average = strength: near vertical = strong trend emerging; flat or flattening = chop, do not trend trade. No angle given. | KR-M11 |
| 5 EMA leash (distance) | Price "sprints so hard that the entire candle floats above" a very short average: the low does not touch the 5 EMA = disconnect. It reconnects: "even when it disconnects, it goes sideways until it reconnects"; three closes without touching means you are late. His own count (claim, T3, not verified): 5,284 daily candles, 476 disconnects, median 1 close, 82 % reconnect within 2, longest 7. | KR-M06; NXz-17..19; KR-F08 |
| Distance as "how far it can come down" | He has no distance-in-percent or in-ATR rule for the 21, 55 or 200. The only sourced distance concept is the leash (candle fully off the 5 EMA) and "first touch after a long time away" for the 200. Percent and ATR distances in this layer are OURS and serve the operator's question; we do not claim they are Krown's. | extract search 2026-11-07: no distance threshold in NXz or vjzy |
| Weekly | Weekly 55 EMA: above = generally bullish, below = bearish; a reclaim given up within about two closes is a bull trap (KR-M10). Weekly 200 SMA "is basically four years of price in one line"; BTC lows 2015, 2018, 2020, 2022 called by it, 2022 traded below it briefly; his 26-year, 80-touch back-test is a claim only. | KR-M04, KR-M10; NXz-16 |
| Timeframes | Highest timeframe with 200+ periods first (min 200, ideal 500); importance ladder 1w > 1d > 12h > 6h > 4h > 1h > 30m > 5m; below 4h is noise and the daily is "where to live" (our conflict C8: our scalps live on 1m to 15m, so the lower rows are context for them, not Krown's home). | KR-T01, KR-T02; conflict C8 |
| Role | Averages are filters, not entry signals: "going long or short at every cross will not work"; they keep you with the trend and validate trades. A range break needs a close beyond the edge with the averages confirming. | KR-M12, KR-M13 |

Not extracted anywhere: what he does with the monthly chart's averages; the 200 EMA on a specific timeframe; any percent distance rule. The layer says so instead of inventing them.

## (b) What the widely taught practice says (web, opened 2026-11-07; vendor and blog level unless marked)

| Practice | Statement | Source | Our evidence status |
|---|---|---|---|
| 20 MA pullback buys in an uptrend, low timeframes | Buy a dip to a rising 20 EMA inside an established uptrend; entry on the close back off the average, not the first touch; 9 and 20 EMA pullbacks on 5-minute charts; trend on 15m/5m, entry on 1m/2m; 50 EMA as trend check, stop under the last swing low. Rules vary (9/20 vs 20/50). | [newtraderu two-legged pullback](https://www.newtraderu.com/2022/03/18/two-legged-pullback/); [therighttrader EMA pullback](https://therighttrader.com/learn/trading-strategies/ema-pullback-strategy); [protraderdashboard pullback day trading](https://protraderdashboard.pages.dev/blog/pullback-day-trading); [kotakneo EMA pullback swing](https://www.kotakneo.com/stockshaala/swing-trading-strategies/ema-pullback-swing-strategy/) | folklore; blogs, no costs. Intraday MA rules are fee-limited (Q_ALL F7) |
| Golden / death cross | Golden = 50-day SMA crosses above the 200-day SMA; death = below. "A moving-average crossover does not predict future direction but shows trends"; the death cross "is not a reliable indicator of future market declines". | [Wikipedia, Moving average crossover](https://en.wikipedia.org/wiki/Moving_average_crossover) | folklore (12 events in our data, Q_ALL) |
| Weekly bull-market support band | The 20-week SMA and 21-week EMA together form a dynamic support zone; a weekly close below both is a warning; under the band it is read as resistance. | [TradingView Bull Market Support Band script](https://www.tradingview.com/script/Bxg5DSp5-Ricco-Bull-Market-Support-Band); [rosetta.to Bitcoin Bull Market Support Band](https://rosetta.to/u/intothecryptoverse/bitcoin-bull-market-support-band-2025-06-30) | anecdote, n <= 4 cycles |
| 200-week MA as the cycle floor | Acted as a floor at prior cycle bottoms; one analysis counts 56 of 642 weekly closes below it and calls the 50-week the usual bear-market ceiling. Promotional "never breached" claims are false for closes (2022). | [Galaxy research: 50W ceiling, 200W floor](https://www.galaxy.com/insights/research/bitcoin-50-week-moving-average-bear-market-ceiling-200-week-floor-analysis); [bit.com 200 WMA](https://www.bit.com/knowledge-hub/200-wma) | anecdote, n <= 4; same claim Krown makes (KR-M04) |
| Mayer multiple | Price / 200-day MA (Trace Mayer). Popular levels 2.4 (stretched, likely bubble) and 0.8 (oversold); derived from BTC history, "approximate" elsewhere; some argue peaks are shrinking. | [Glassnode Mayer multiple](https://studio.glassnode.com/charts/mayer-multiple); [TradingView Mayer multiple scripts](https://it.tradingview.com/scripts/mayer_multiple) | folklore levels; the ratio is a pure distance gauge (see Q_ALL F1/F3: price-to-MA ratios are the only OOS-supported construct, at a ~1-week horizon) |
| Monthly 20 MA | A 20-month SMA nearly divides bull from bear phases on BTC since 2011 (one 2023 analysis; whipsaw in March 2020); CryptoQuant cites the 20-month SMA at 87,165 (Oct 2026) and BTC losing it in Dec 2025. | [NewsBTC 2023](https://www.newsbtc.com/news/bitcoin-poised-for-potential-major-buy-signal-in-july/); [Cointelegraph / CryptoQuant](https://cointelegraph.com/news/bitcoin-seeks-20-month-trend-line-reclaim-before-new-record-highs-cryptoquant) | anecdote, one analysis |
| EMA vs SMA lag | SMA = unweighted mean of the last k points, hard window; EMA = exponentially decaying weights that never reach zero, so recent bars count more and it turns earlier. Standard smoothing alpha = 2/(N+1) (textbook; the Wikipedia page does not state it). | [Wikipedia, Moving average](https://en.wikipedia.org/wiki/Moving_average) | maths, SOURCED; seed choice OURS |
| Academic | Only the short-horizon (~1 week) log price-to-MA ratio survives snooping control and OOS on BTC (T1, sample to Mar 2022); classic crossovers do not. | `btc_ma_2026-10-03/Q_ALL_ma_findings.md` F1, F2, F9 | reason the layer is display-only |

Fetch note: investopedia.com was blocked from this machine, so golden cross and EMA definitions come from Wikipedia.

## (c) MA state per timeframe (the definition `ma_state.py` and `ma_strip.js` implement)

Timeframes: 5m, 15m, 1h, 4h, 1d, 1w, 1M (the last bar of each is the forming bar, as in the timeframe strip). Klines: Binance spot BTCUSDT from data-api.binance.vision, 1000 bars each. An average with fewer bars than its length is null (shown as a dash), never a guess; the monthly 200s are null (about 100 months of history).

Averages (price series = closes, forming bar included):

| Name | Definition | Label |
|---|---|---|
| sma20 | mean of last 20 closes | length 20: SOURCED as the weekly band leg and monthly 20 (web, section b); on low timeframes the textbook 20 MA |
| ema21 | EMA length 21, alpha 2/(N+1), seeded with the mean of the first 21 closes | 21: SOURCED (Krown KR-M01); alpha: SOURCED maths; seed: OURS |
| ema55 | same, length 55 | SOURCED (KR-M01) |
| sma50 | mean of last 50 closes | SOURCED (golden/death cross, KR-M07) |
| sma200 | mean of last 200 closes | SOURCED (KR-M01, KR-M03) |
| ema200 | EMA length 200 | SOURCED (vjzy-20, "200 EMA or 200 SMA") |

Per average, per timeframe:

| Field | Definition | Label |
|---|---|---|
| side | price above / below the average (equal = null) | SOURCED idea (KR-M10) |
| distPct | 100 x (price - avg) / avg | OURS (answers "how far from the average"); on 1d for sma200 it equals 100 x (Mayer multiple - 1) |
| distAtr | (price - avg) / ATR14 of that timeframe; ATR14 = mean true range of the 14 closed bars before the forming bar (same as tf_strip.js atr14) | OURS |
| ratio | price / avg (Mayer multiple when avg = sma200 on 1d) | SOURCED formula (Trace Mayer, web); 2.4 / 0.8 shown as popular levels only, folklore |
| slope | sign of avg(now) - avg(5 bars ago): up if change > +0.5 ATR14, down if < -0.5 ATR14, else flat | SOURCED idea (KR-M11 flat = chop); 5 bars and 0.5 ATR are OURS |

Row-level fields:

| Field | Definition | Label |
|---|---|---|
| cross2155 | state up if ema21 > ema55, down if below, null on a tie; barsSince = bars since the last change of state (null if none in the window) | SOURCED (KR-M02, KR-M09) |
| cross50200 | same for sma50 vs sma200: golden (up) / death (down) | SOURCED (KR-M07) |
| pullback | up when in an uptrend (ema21 > ema55 and ema55 slope up) the forming bar's low is at or below ema21 + 0.25 ATR14 and its close is at or above ema55; down is the mirror (downtrend, high at or above ema21 - 0.25 ATR14, close at or below ema55); else null. This is "price pulled back to the 20/21 in a trend", the 20 MA pullback of section (b) with Krown's 21/55 zone as the floor | structure SOURCED (KR-M05 buy between the 21 and 55; web 20 EMA pullback); 0.25 ATR touch tolerance OURS |
| band | price vs the 20-week-style band between sma20 and ema21: above / inside / below (null if either missing) | SOURCED idea (web bull market support band); applied to every timeframe: OURS |

Not in this version: the 5 EMA leash and the 377 EMA (Krown, sourced, KR-M06 and KR-M09) are noted for the next step; no producer without a consumer.

Reading rules (display, not signals): a flag says what the average relationship is now. It does not say buy or sell; Krown himself calls averages filters (KR-M12) and our own evidence review finds no validated MA entry rule.
