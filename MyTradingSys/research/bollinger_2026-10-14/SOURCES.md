# Bollinger Bands: band walk ("dance"), setups and BTC settings (sources, 2026-10-14)

Tiers: T1 = peer-reviewed or primary author; T2 = practitioner with reproducible backtest (data, period, fees stated); T3 = blog/opinion/no data; REJECT = unverifiable, blocked with no readable abstract, or marketing. Numbers carry their source number [n] from the Sources list. "Link loaded" is stated per source at the bottom.

## Answer in short

- "Bollinger Band dance" is not a term any source used. The real term is "walking the bands" (band walk): in a strong trend price keeps closing on or beyond one outer band, and pullbacks stop near the middle line [1][6].
- Bollinger himself says a touch of a band is only a "tag", not a signal. A close outside the band usually means the trend continues, not that it reverses [1][2].
- No source gives a numeric "close enough to the band" rule. The only tolerance language is %b (0 = lower band, 1 = upper band, 0.5 = middle). LuxAlgo says readings pinned near 1 quantify a walk but does not say what counts as pinned; "3 or more closes within a handful of bars" is a practitioner habit with no data [6][7]. Any cushion (for example %b >= 0.95) would be our own choice.
- Bollinger's parameter advice: 20/2 is a starting point; longer averages need a bigger multiplier (about 2.1 at 50) and shorter ones a smaller one (about 1.9 at 10) [1]. This keeps band width comparable; it is not a claimed edge.
- Nobody we found has a backtested "best" Bollinger setting for Bitcoin. The 24/7 argument (use 30 instead of 20 because crypto has 30 days a month) is one 2016 chart post with no backtest [10]. Day et al. report that a 60-day average beat a 20-day one on BTC futures, but only the abstract was readable and costs were not visible [3].
- Evidence on profit is thin and regime-dependent. Index tests net of costs show no edge over buy-and-hold [4]; the famous stock edge faded after the rule became popular [5]; crypto grids show big gains in bull windows and losses in bear windows [8]; a Bollinger-in-Keltner squeeze test on SPY found no useful breakout signal [9].
- Winning-percentage is a poor guide: in one crypto grid 14 of 78 runs won 65% or more of trades and still lost money [8].
- For our repo this means: treat every tolerance, length and multiplier as OURS, fix the grid before looking, test on a held-out period, and report trade counts and fees. The candidate list is in section 5.

## 1. Band walk / dance and the "close enough" tolerance

What it is
- Bollinger's rule 7: in strong trends price can ride the upper band up or the lower band down for long stretches [1]. StockCharts' write-up says the 20-day average often acts as support during an uptrend walk, so dips toward it are the buy zone [2].
- LuxAlgo defines a walk as a sustained run of closes on or beyond one outer band, with pullbacks holding near the midline and the opposite band bending away. Its end signal: price stops reaching the band and closes back near the middle [6].
- "Dance" and "dancing on the band": a search for these phrases returned nothing as a defined term. Treat it as the operator's word for band walk.

How traders use it
- Continuation, not fading: stay with the trend, buy pullbacks to the midline, do not short strength [1][6]. Bollinger rule 8: a close outside the band signals continuation first; many volatility-breakout systems rely on it [1].
- Confirmation: a TradingView script says Bollinger recommends Intraday Intensity and/or Accumulation Distribution to confirm continuation or reversal during walks. That is second-hand, not checked against the book [7].

Tolerance for "close to the band" (what exists and what does not)
- No source states a numeric tolerance. LuxAlgo's concept page says it sets none and points only to %b near 1 or near 0 [6]. The TradingView "Walking The Bands" script offers two modes (consecutive tags, or closes outside the bands) and gives no tolerance, bar count or %b threshold in its description [7].
- Exact-tag definitions: LuxAlgo's tag-reversion page uses close at or beyond the band, equal to %b <= 0 or %b >= 1, and mentions a variant using the high or low instead of the close, with no cushion [11].
- Bar count: LuxAlgo: no canonical number; "three or more within a handful of bars" is common [6]. Source has no backtest.
- Statistical reason a cushion is needed: Bollinger says about 88-89% of price sits inside default bands [2], and rule 14 says about 90% rather than 95% because prices are not normal [1]. So a strict close-outside is roughly a 10-12% per-bar event by his own estimate, but it is a clustered event in trends (that is the walk).
- Our reading (OURS, not from a source): a cushion expressed in %b units (distance as a fraction of band width) scales with volatility, unlike a percent-of-price cushion. See section 5.

## 2. Setups and combinations

| Setup | Rule as stated | Claimed edge | Evidence tier | Source |
|---|---|---|---|---|
| Band-touch reversal (fade) | Long when close <= lower band (%b <= 0), short when close >= upper (%b >= 1); target middle band; needs confirmation (close back inside, rejection candle, oscillator turning); skip tags while BandWidth is expanding out of a tight base | "Tag alone is not a signal"; edge depends on regime and filters; no win rate given | T3 for the rule; Bollinger's own caution T1 | [11][1] |
| Fade, tested on BTC futures | Buy when price falls below lower band, sell when it penetrates the upper band, round-trip, 20-day average | Average holding-period return above 20% (20-day), above 50% (60-day average); sample period and costs not visible in the abstract | T1 (peer reviewed, abstract only; full text paywalled) | [3] |
| Fade, tested on an index | Bollinger-band rules, costs included | Net of transaction costs the bands did not beat buy-and-hold; contrarian version did better than trend-following version | T1 (abstract only; sample not visible) | [4] |
| W-bottom / M-top | W-bottom: reaction low, bounce to middle band, second lower low that holds above the lower band, then strong move that breaks resistance. M-top mirrors it: new high fails to reach the upper band, confirmed by a support break or indicator signal | "Pattern recognition", probabilistic; no stats given | T3 (StockCharts write-up of Bollinger's method); the rule list names M tops/W bottoms in rule 5 (T1) | [2][1] |
| W-bottom with %b | Price makes lower low while %b makes higher low | Flags fading pressure; "needs confirmation" | T3 | LuxAlgo %b page (search result only, not fetched; same idea in [2] as indicator divergence) |
| Squeeze breakout | Very low BandWidth, then price breaks out of the band; BandWidth is "best known" for spotting the squeeze (no threshold on Bollinger's rules page) | Qualitative: "excels in crypto" with no data | T3 (Mudrex); T1 for the concept only | [1][12] |
| Squeeze test, Bollinger inside Keltner | Bands (20, 2 SD) inside Keltner channel (20, 1.5 x average range); breakout = 3-day return from last squeeze day | Test found no help: 126 breakouts, correlation with next 18-day trend -0.11 (R2 0.01); SPY daily 1993-2010; gross of costs; author warns of data-snooping if rules are tweaked | T2 (data and period stated; no costs) | [9] |
| Band-walk continuation / breakout | Buy a close above the upper band, exit below the lower band (S&P 500, 1960 to Apr 2026) | CAGR 5.7% ex dividends, 58 trades, invested about 64% of time, max drawdown 30%; costs not mentioned; band length not visible (paywalled) | T3 (rule only partly visible) | [13] |
| Close back inside after a close outside | Tag then a close back inside the band before entering toward the middle | Described as a confirmation option; no stats | T3, no backtest found | [11] |
| RSI divergence at band | Price makes higher high at upper band while RSI makes lower high | Early warning only | T3; no published backtest found for the combination | search only (see note) |
| Candle pattern at band (for example red candle closing below the prior green candle's open or low at the upper band) | "Rejection candle at the extreme" listed as one confirmation option | None stated; no source for the specific "closes below prior open/low" rule | T3 (generic mention) | [11] |
| Volume / CVD | Bollinger's named volume tools are Intraday Intensity and Accumulation Distribution (second-hand); Bollinger rules 3-4 say combine indicators that measure different things | CVD with bands is a community-script idea; the LuxAlgo version estimates delta from OHLC, not from trades | T3 | [7][1] |
| Regime dependence | Band reversion on 20-period, k 2.0/2.5 across bear (2022), sideways (Apr-Oct 2023), bull (Oct 2023-Mar 2024) | Average returns bull +16.3%, sideways -2.2%, bear -40.6% over all strategies/timeframes; BTC daily k=2 in 2022: 6 trades, 33% win, -38.9% | T2 (data and windows stated; fee rate not given; some cells have 2-6 trades) | [8] |
| Edge decay | Bollinger-band profits in stocks before vs after the rule became popular | Reported as profitable before popularity, not after (from the SSRN title and search summary; abstract page not loaded) | T1 but not verified here | [5] |

Note on missing items: no fetched source tests RSI divergence + candle + band on BTC, or any CVD-confirmed tag. Searches returned only indicator scripts without results.

## 3. Settings for BTC / 24/7 markets

| Setting | Claim | Backtest? sample/period/fees | Tier | Source |
|---|---|---|---|---|
| 20 / 2 | Default starting point, to be adjusted for market | No BTC test by Bollinger | T1 (guidance) | [1] |
| 10 / 1.9 and 50 / 2.1 | Scale the multiplier with the length so containment stays similar | No backtest; rule of thumb | T1 (guidance) | [1][2] |
| 20-day vs 60-day average (BTC futures, 2 SD style) | 60-day beat 20-day: holding-period return above 50% vs above 20% | Yes in the paper; sample dates, fee model and trade count not visible in abstract; full text paywalled | T1 (abstract only) | [3] |
| 30 instead of 20 for Bitcoin | 20 trading days is about one month in stocks, BTC trades 30 days a month | No; chart observation on BTCUSD Bitfinex daily, post dated 2016-07-22 | T3 | [10] |
| 20 / 2.0 vs 20 / 2.5 | 2.5 is "stricter, fewer entries" | Yes, BTC/ETH Binance spot 15m-1d, three windows 2022-2024, fees "built in" but rate not stated; text does not isolate k=2.5 vs 2.0 | T2 | [8] |
| 20-21 for swing, 20-50 at 2-2.5 for position, 10-14 at 1.5-2 for intraday, 2.5 for volatile assets | Starting-point advice | None. Page says settings are "proven" but cites no data | T3 | [12] |
| 5-minute BTC/USDT squeeze-gated mean reversion | Unoptimized version was weak because of trading frequency, fee drag and false breakouts; filters (BandWidth, volatility, cooldown) helped | Report summary gives no length, multiplier, dates, fees or numbers | T3 | [14] |
| Technical rules in crypto generally (about 15,000 rules, five classes, two Bitcoin markets + three coins) | Breakeven costs well above typical crypto costs; but no predictability for Bitcoin in the out-of-sample period | Yes, with data-snooping controls; page does not name Bollinger rules or sample dates | T1 | [15] |

24/7 scaling argument
- Arithmetic (OURS): a 6.5 h session is 390 minutes; a 24 h day is 1,440 minutes, ratio about 3.7. If a stock-tuned window of 20 intraday bars is meant to span a fixed fraction of a trading day, the same fraction of a BTC day needs about 20 x 3.7 = 74 bars. On daily bars the ratio is 7/5 = 1.4 (calendar days vs weekdays), giving 28, which is near the 30 in [10]. Whether lookbacks should follow clock time or bar count is unproven.
- Nothing we fetched backtests this scaling. The only source for the idea on Bollinger Bands is [10] (opinion). Bollinger rule 21 says bands work on any bar interval as long as bars contain enough activity [1]; he does not say to scale by hours.
- Gap: no source gives a backtested BTC length/multiplier grid with fees and a held-out period. Say so in any brief.

## 4. Bollinger's own rules (22 rules page, bollingerbands.com) [1]

- Rule 6: touching a band is a tag, not a signal; it calls for study, not a trade. StockCharts phrases the same point as tag versus signal [2].
- Rule 7: in strong trends price can walk the upper or lower band. Rule 8: a close outside the band is first a continuation sign; many breakout systems are built on it.
- Rule 1: price near the upper band is relatively high, near the lower band relatively low. Rules 3-4: pair the bands with indicators of momentum, volume, sentiment, open interest or related markets, and choose indicators that measure different things.
- Rule 5: use the bands to clarify M tops, W bottoms and momentum shifts.
- Rules 9-11: 20/2 is a start; middle band should reflect the intermediate trend and not be tuned for crossovers; longer average gets a larger multiplier (2.1 at 50), shorter gets smaller (1.9 at 10).
- Rule 12-13: simple average is the standard (matches the standard-deviation math); exponential versions smooth sudden width jumps.
- Rule 14: prices are not normal; about 90% sits inside default bands.
- Rules 15-17: %b = where price sits in the band (adapted from stochastics): good for divergences, patterns and coding systems; applying 50-period-or-longer bands to another indicator removes fixed thresholds.
- Rules 18-19: BandWidth = band width relative to the middle band (four times the coefficient of variation at defaults); best known for the Squeeze, also useful for spotting trend changes. The page gives no squeeze threshold.
- Rules 20-22: works on most markets and any timeframe; bands are not continuous advice, they locate setups where odds may favor you.
- Not in the primary text we could read: the book "Bollinger on Bollinger Bands" itself was not accessed; the squeeze lookback is not stated on the rules page.

## 5. What we should pre-register and test

Principles: one grid fixed before any result is seen; DEV / VALIDATION / holdout split, each variant in the trial ledger; fees from the repo fee model; report trade counts per cell; compare against buy-and-hold and a random-entry baseline of equal exposure; split results by regime (trend/range) because [8][9] show strong regime dependence. Every number below is OURS unless marked.

| Item | Definition | Source label |
|---|---|---|
| Bands | SMA of close, population SD of close, length L, multiplier k | FORMULA per [11]; population SD per LuxAlgo default |
| Base setting | L=20, k=2.0 | from source [1] |
| Scaled-by-Bollinger settings | L=10,k=1.9; L=50,k=2.1 | from source [1] |
| 24/7 candidates | L=30 (daily bars); L=74 (intraday bars, 20 x 24/6.5) with k=2.0 | 30 from [10] (opinion); 74 OURS |
| Wider multiplier arm | L=20,k=2.5 | k=2.5 from [8][12]; no backtest isolates it |
| Tag (strict) | close >= upper (%b >= 1) / close <= lower (%b <= 0) | from source [11] |
| Tag (cushion) | %b >= 1 - eps with eps in {0.05, 0.10}; mirror at the lower band. Also a high/low-based version: high >= upper - eps x (upper-lower) | OURS (no source gives a tolerance) |
| Band walk | at least 3 closes with %b >= 1 - eps within 5 bars, and no close below the SMA between them; walk ends on first close below the SMA (long case) | "3 within a handful of bars" and midline-hold from [6] (T3, no data); eps, 5-bar window OURS |
| Walk continuation test | after walk start, enter next bar open, exit on close below SMA; measure fee-net return, hold time, trade count | OURS |
| Fade (reversion) | after a tag, enter when the next close is back inside the band (%b < 1 - eps), target SMA, stop at tag extreme | structure from [11]; target/stop OURS |
| Fade filter | skip when BandWidth rose in each of last 3 bars from a trailing low | from [11] (concept); 3-bar rule OURS |
| Squeeze | BandWidth <= its 10th percentile over the trailing 180 bars; trade the first close outside the band | percentile and window OURS; concept [1]; Keltner version: BB inside Keltner(20, 1.5) as in [9] |
| W-bottom / M-top | per StockCharts four steps: reaction low below lower band, bounce above SMA, second lower low with %b > first low's %b and > 0, entry on close above the intervening swing high | steps from [2]; %b comparison from LuxAlgo %b page (search only); swing definition OURS |
| Confirmations (separate arms, never stacked in the first pass) | RSI(14) divergence; candle rule (red close below prior green open); trade-level CVD, not OHLC-estimated | no source backtests these; all OURS |
| Controls | each setup with no confirmation; random entries with same count; buy-and-hold | OURS |
| Costs | repo fee model per side plus a slippage stress at 2x fees | OURS; paper [15] finds breakeven costs are high, so test at 2x |
| Decision rule | an arm advances only if fee-net result holds on VALIDATION and in both trend and range regimes, with at least 100 trades per arm | threshold OURS |

Questions this answers for the operator: is "close enough" worth a cushion (compare eps 0, 0.05, 0.10 on identical trades); does walk-continuation beat fade in trends and the reverse in ranges; does 30 beat 20 on BTC daily or is the difference noise.

## Sources

Tier T1 (5)
1. T1. John Bollinger, "Bollinger Band Rules" (22 rules), bollingerbands.com. https://www.bollingerbands.com/bollinger-band-rules . Supports parameters, tags, band walk, %b, BandWidth, scaling of multiplier. Quote: "tags, not signals" is the page's own wording for touches.
3. T1. Day, Cheng, Huang, Ni, "The profitability of Bollinger Bands trading bitcoin futures", Applied Economics Letters 30(11), 1437-1443 (2023). https://ideas.repec.org/a/taf/apeclt/v30y2023i11p1437-1443.html . Abstract only: AHPR above 20% with 20-day, above 50% with 60-day average. Publisher page (tandfonline) not fetched.
4. T1. Lento, Gradojevic, Wright, "Investment information content in Bollinger Bands?", Applied Financial Economics Letters 3(4), 263-267 (2007). https://ideas.repec.org/a/taf/raflxx/v3y2007i4p263-267.html . Abstract only: no excess return over buy-and-hold net of costs; contrarian better.
5. T1 (not verified). Fang, Jacobsen, Qin, "Popularity versus Profitability: Evidence from Bollinger Bands". https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2484322 . Link returned 403; the title and a search summary only. Supports: stock profits reported to fade after the rule became popular.
15. T1. Hudson and Urquhart, "Technical trading and cryptocurrencies", Annals of Operations Research 297, 191-220 (2021). https://ideas.repec.org/a/spr/annopr/v297y2021i1d10.1007_s10479-019-03357-1.html . About 15,000 rules, five classes, crypto; no Bitcoin predictability out-of-sample; Bollinger not named in the abstract.

Tier T2 (2)
8. T2. Coinquant, "Building a Mean-Reversion Strategy in Cryptocurrency Markets: Evidence from 78 Backtests". https://www.coinquant.ai/blog/building-a-mean-reversion-strategy-in-cryptocurrency-markets-evidence-from-78-backtests . Binance BTC/ETH spot, 3 regime windows 2022-2024, 20-period, k 2.0/2.5, net of costs but rate not stated, grid count does not reconcile (72 vs 78). Trade counts small on daily.
9. T2. CXO Advisory, "Testing a Complex Breakout Indicator" (LeCompte, 2010-01-14). https://cxoadvisory.com/?p=4461 . SPY 1993-2010 Bollinger-inside-Keltner squeeze; no support for breakout signal; costs not mentioned.

Tier T3 (9)
2. T3. StockCharts ChartSchool, "Bollinger Bands". https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/bollinger-bands . Four-step W-bottom, M-top, 88-89% inside bands, 10/1.9 and 50/2.1, band walk description. Third-party summary of Bollinger's method.
6. T3. LuxAlgo library, "Band Walk". https://www.luxalgo.com/library/concept/band-walk/ . Definition, no numeric tolerance, no data.
7. T3. TradingView script "Walking The Bands". https://www.tradingview.com/script/lvtoUx9T-Walking-The-Bands . Two walk modes; second-hand note on Intraday Intensity/Accumulation Distribution. Search results also supplied the %b-divergence W-bottom wording from LuxAlgo's %b page (not separately fetched).
10. T3. IAmSatoshi, "Changes to Default BBands for bitcoin", TradingView, 2016-07-22. https://my.tradingview.com/chart/BTCUSD/yQanb3wG-Changes-to-Default-BBands-for-bitcoin . Period 30 for BTC because 24/7; chart observation, no backtest.
11. T3. LuxAlgo library, "Bollinger Band Tag Reversion". https://www.luxalgo.com/library/concept/bollinger-band-tag-reversion/ . Exact tag rule (%b <= 0 / >= 1), confirmation options, population SD; no backtest.
12. T3. Mudrex Learn, "Bollinger Bands Explained: Formula, Best Settings & Strategy". https://mudrex.com/learn/bollinger-bands-in-crypto-trading/ . Settings table and setup descriptions with no data.
13. T3. Quantified Strategies, "Bollinger Band Breakout Strategy" (Substack). https://quantifiedstrategies.substack.com/p/bollinger-band-breakout-strategy . S&P 500 1960-2026: 58 trades, CAGR 5.7%, 64% invested, 30% drawdown; rules paywalled; no costs.
14. T3. Gate Research, "Bollinger Bands in Crypto Markets, Effectiveness Analysis and Mean Reversion Strategy Backtest". https://www.gate.com/announcements/article/50944 . BTC/USDT 5m; announcement summary without parameters or numbers; exchange-published.
16. T3. CoinDesk, "Bitcoin tests Bollinger Bands breakout as creator flips bullish on BTC" (2026-05-07). https://www.coindesk.com/markets/2026/05/07/bitcoin-tests-bollinger-bands-breakout-as-creator-flips-bullish-on-btc . News only: BTC daily close above standard 20/2 upper band; Bollinger's model settings not disclosed.

REJECT (3)
17. REJECT. Arda, "Bollinger Bands under Varying Market Regimes: breakout and mean-reversion in BTC/USDT", SSRN. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5775962 . Appeared in a search result (July 2017-March 2022 BTC/USDT, regime-dependent); page returned 403 and a second search could not corroborate it. Lead only: obtain the PDF manually before use.
18. REJECT. Quantified Strategies, "Bitcoin Bollinger Bands Trading Strategy". https://www.quantifiedstrategies.com/bitcoin-bollinger-bands-trading-strategy-performance-backtest/ . Blocked by bot check; a search snippet claimed 49.7% CAGR 2015-2026 but it cannot be read here and is commercial. Not used.
19. REJECT. TradingView "Multi-Band Comparison Strategy (CRYPTO)". https://www.tradingview.com/script/bq0ELG1b-Multi-Band-Comparison-Strategy-CRYPTO/ . Loaded, but not a Bollinger-settings test (own quantile bands), single one-year BTC run with 25.5% win rate, author's promotional claims. Not used.

Link-load log: loaded = 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19; not loaded (403 or bot check) = 5, 17, 18. Numbered items 3/4/15 were read via IDEAS/RePEc abstract pages (publisher and SSRN pages were not readable).
