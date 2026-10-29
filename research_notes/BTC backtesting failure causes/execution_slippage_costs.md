# Transaction Costs, Slippage and Execution-Modeling Errors as Causes of Backtest-to-Live Divergence (crypto/BTC emphasis)

Research date: 2026-10-30. Source type and approximate date are given for each major claim. In the cited findings, "[peer-reviewed]" means a peer-reviewed journal, "[WP]" a working paper, "[vendor]" an exchange or data-vendor research note, "[aggregator]" a data aggregator snapshot, and "[secondary]" news or blog coverage of someone else's data.

## Q1. What do backtests typically get wrong about transaction costs (fixed fees vs. actual maker/taker, funding on perps, borrow on shorts)?

### Takeaway
Naive backtests usually apply one flat per-trade fee, or none, and leave out the costs that build up while a position is held. On BTC perpetuals the biggest of these is funding. It has averaged roughly 10% a year or more for longs over long stretches, swings from strongly positive to negative, and is paid every 8 hours. A single flat fee also hides the maker/taker difference: on Binance USD-M futures, the retail taker fee is 2.5x the maker fee. On the evidence, transaction costs only ever reduce strategy returns, high-turnover strategies are the ones they wipe out, and the losses come mostly from the short legs and the small or illiquid names.

### Cited Findings
**Fee structure (crypto)**
- Binance's official futures fee FAQ uses 0.02% maker / 0.05% taker as its worked example of a "regular user's" (VIP 0) rate. Futures VIP tiers need 5x the spot volume, paying fees in BNB gives a 10% discount, and Binance warns that fees are subject to change. — [Binance Futures Fee Structure FAQ (exchange doc, current page)](https://www.binance.com/support/faq/360033544231)
- So a strategy that crosses the spread both ways pays about 0.10% per round trip in fees alone at VIP 0 (2 x 0.05%), against 0.04% if both legs fill as maker. That is a 2.5x difference before any slippage. (Arithmetic from the FAQ figures above.) — [Binance FAQ](https://www.binance.com/support/faq/360033544231)
- An academic perp study (He, Manela, Ross & von Wachter, arXiv 2212.06888, v5 2024) models Binance fee tiers explicitly and uses **maker** fees on the grounds that "institutions typically trade maker orders". Its tiers run from "No fee" (negotiated market makers) through VIP 8 and VIP 5 to "High" (VIP 1 retail). — [He et al., "Fundamentals of Perpetual Futures" [WP, rev. 2024]](https://arxiv.org/html/2212.06888v5)
  - Caution: the round-trip futures fees in that table as extracted (0.0018% to 0.0144%) are far below Binance's published VIP 0 maker rate of 0.02% per side. The report writer should check the table before quoting those fee figures.

**Funding cost on perpetuals**
- **Average:** BIS Working Paper 1087 "Crypto carry" (Schmeling, Schrimpf, Todorov; first version April 2023, revised Oct 2025) finds the futures-minus-spot carry on BTC/ETH "averaging above 10% annually". It also says carry "can become very large": up to 60% p.a. in the 2023 abstract, and "exceeding 40%" in the revised abstract. Which figure appears in which version is unconfirmed. — [BIS WP 1087 page](https://www.bis.org/publ/work1087.htm); [EconPapers listing](https://econpapers.repec.org/RePEc:bis:biswps:1087)
- **Risk:** The same paper says arbitrageurs who harvest carry face "spikes in margins and liquidations amid drawdowns". A backtest that books carry as a smooth return understates this tail risk. — [BIS WP 1087](https://www.bis.org/publ/work1087.htm)
- **Baseline rate:** The 0.01%-per-8h baseline is built into most exchanges' funding formula as a fixed interest-rate component; it is not a measured average. Annualized it is 0.01% x 3 x 365 = 10.95% a year, and Coin Metrics annualizes funding by simple multiplication (no compounding). — [Coin Metrics docs: market funding rates (vendor doc)](https://docs.coinmetrics.io/market-data/market-data-overview/market-funding-rates); [Athenum blog (practitioner)](https://athenum.mataroa.blog/blog/annualized-funding-rate-how-to-read-perpetual-funding-as-a-carry/)
- **Regime swings (aggregator snapshots):** BTC funding moves sharply between regimes. One DeFi Rate snapshot in late September 2026 showed a 6-exchange simple average of about -0.7% annualized (Kraken -12.8%, Coinbase Intl +4.4%), while 24 Oct 2026 showed +16.0%. These are single-date, unweighted readings. — [DeFi Rate snapshot 2026-09-25](https://defirate.com/perp/snapshot/2026-09-25T1925/); [DeFi Rate snapshot 2026-10-24](https://defirate.com/perps/snapshot/2026-10-24T0041/)
- **He et al. on BTC perps:**
  - Over 2020-01 to 2024-03 on Binance, funding payments make up 5.06 percentage points of a 13.70% gross annual return on a perp-spot convergence strategy. The rest (8.64) comes from price convergence. — [He et al. [WP, 2024]](https://arxiv.org/html/2212.06888v5)
  - Perp prices deviate from no-arbitrage values far more than in traditional currency markets. The deviations move together across coins and have shrunk over time. — [He et al. arXiv abstract](https://arxiv.org/abs/2212.06888)

**Borrow cost on spot shorts**
- Since March 2023, Binance Margin borrow rates change **hourly**. Under the old rule a full hour of interest was charged as soon as funds were borrowed. Binance announced prorated first-hour interest from 2026-04-30. Binance keeps only 30 days of rate history in the UI and 6 months via the API, so a long backtest needs separately archived rate data (Coinglass has a multi-exchange chart). — [Binance dynamic interest-rate FAQ (exchange doc)](https://www.binance.com/support/faq/360030157812); [Coinlive news on proration change (secondary, 2026)](https://www.coinlive.com/news-flash/1097502); [Coinglass margin fee chart (aggregator)](https://www.coinglass.com/MarginFee)

**General (TradFi) evidence that costs decide which anomalies survive**
- **Novy-Marx & Velikov (RFS 2016), 23 anomalies:**
  - Transaction costs reduce profitability in every case.
  - Strategies with monthly turnover under about 50% mostly keep significant net spreads when designed to limit costs. Few higher-turnover strategies do.
  - A buy/hold spread (stricter rules for entering a position than for keeping it) is the most effective way to cut costs.
  - Their cost measure (Hasbrouck effective spread) leaves out price impact, so it represents a small trader.
  — [Novy-Marx & Velikov PDF](https://mysimon.rochester.edu/novy-marx/research/ToAatTC.pdf); [NBER w20721](https://nber.org/papers/w20721); [Alpha Architect summary (practitioner blog, 2017)](https://alphaarchitect.com/2017/05/trading-costs-destroy-factor-investing/)
- **Frazzini, Israel & Moskowitz ("Trading Costs", AQR/Chicago; 2012 draft, later 2017-18 version):** About $1 trillion of AQR live trades (later $1.7 trillion, 21 markets, 1998-2016) show real costs are less than a tenth of earlier academic estimates, for a large institution trading patiently. Short-term reversal is the most cost-constrained anomaly. The counterpoint is that cost estimates depend on who is trading: cost-aware institutional execution differs from naive market orders. — [Alpha Architect summary](https://alphaarchitect.com/the-best-research-paper-ever-written-on-trading-costs/); [Swedroe, ETF.com (secondary)](https://www.etf.com/sections/index-investor-corner/swedroe-trading-cost-truths)

**Crypto anomalies after costs**
- **Fieberg, Liedtke & Zaremba ("Cryptocurrency anomalies and economic constraints", International Review of Financial Analysis 2024):**
  - The size and volume anomalies come mostly from micro-cap coins "of negligible economic importance".
  - Momentum survives in larger coins but "incurs substantial trading costs" and gets its alpha mostly from **short** positions, where borrow and funding costs bite and which naive backtests short for free.
  - Abnormal returns cluster in bull markets and fade over time.
  — [ICM repository record](https://open.icm.edu.pl/handle/123456789/25544) (abstract via search snippet; full text returned 403)
- **Caporale et al. ("Price Overreactions in the Cryptocurrency Market", Brunel WP ~2018; BTC, LTC, XRP, DASH):** Overreactions are statistically real, but neither the contrarian nor the inertia strategy beats random outcomes, "possibly because of transaction costs". — [Brunel WP PDF](https://www.brunel.ac.uk/economics-finance-and-accounting/research/pdf/1801-Jan-GMC-Price-Overreactions-In-The-Cryptocurrency-Market.pdf)

### Inferences
- For a directional BTC-perp strategy that holds long positions for days to weeks, funding at a typical ~10% a year (about 0.03% a day) can match or exceed the fee drag. A backtest run on spot OHLCV, or on perp prices without the funding series, will overstate long-biased returns and understate short-biased ones, in a way that depends on the regime. In crowded long regimes (funding 15-60% a year) a long-only perp backtest without funding could be badly wrong.
- A flat "0.1% per trade" assumption is roughly right for VIP 0 taker round trips. It is wrong for strategies that assume limit-order (maker) fills, which also carry fill risk (see Q2), and for strategies that pay taker fees on both entry and stop-loss exits.
- The pattern seen in TradFi (high turnover, short legs and small caps are killed by costs) probably applies even more strongly in crypto. The Fieberg et al. result locates crypto momentum alpha in the cost-heavy short legs.

### Gaps
- No peer-reviewed long-run average of BTC perp funding per exchange (e.g. Binance BTCUSDT 2019-2026) was found. The BIS "above 10%" figure is futures-spot carry across instruments, not perp funding specifically.
- Binance's current live VIP fee table could not be retrieved; only the FAQ example (0.02%/0.05%) is confirmed.
- No source quantified how often spot-margin borrow for altcoins becomes unavailable (borrow-pool exhaustion) during short squeezes.
- Deribit fee and funding specifics were not researched within the tool budget.

## Q2. What are slippage and market impact, and how do naive fills (close/mid price) overstate performance versus realistic fill models (book walking, partial fills, signal-to-execution latency)?

### Takeaway
The best crypto-specific evidence is a live experiment (Albers, Cucuringu, Howison & Shestopaloff, *Quantitative Finance* 2025). It placed millions of real orders on Binance and Bybit and found a systematic trader disadvantage against the last book snapshot. Profitable orders fill worse than expected and unprofitable ones fill as expected, which is adverse selection. Marketable limit orders also often fail to fill. Filling at close or mid is therefore biased toward the strategy, not merely noisy.

### Cited Findings
- **Albers et al. (*Quantitative Finance* 25(6):919-947, 2025, DOI 10.1080/14697688.2025.2515933), millions of live market and marketable-limit orders on Bybit and Binance:**
  - Fills differ from what the latest limit-order-book snapshot predicts, because the book keeps updating during exchange, trader-side and network delays.
  - The gaps are "strongly correlated with" volatility, latency and book liquidity.
  - The disadvantage to the trader is consistent and comes from an "adverse selection effect for taker orders": profitable orders tend to fill worse than expected, while unprofitable ones often meet their expected outcomes.
  - For marketable limit orders there is a "substantial chance" of not filling immediately.
  - The authors propose simple models of fill-failure probability and fill-price deterioration "to make backtests more accurate".
  — [IDEAS/RePEc abstract](https://ideas.repec.org/a/taf/quantf/v25y2025i6p919-947.html); [Oxford ORA record](https://ora.ox.ac.uk/objects/uuid:cdab1de2-7576-42e2-abae-ab12371eba76)
- Kaiko measures slippage by simulating a fixed-size market order (e.g. a $50k or $100k sell) walking the live book, and measures depth as resting limit orders within X% (0.1%-10%) of mid. A strategy's real cost depends on its order size relative to that depth. — [Kaiko: understanding CEX liquidity data (vendor)](https://www.kaiko.com/resources/understanding-centralized-exchange-liquidity-data); [Kaiko 2022 chartbook](https://marketing.kaiko.com/hubfs/Kaiko_Weekly_Cryptocurrency_Chartbook_07_06_2022.pdf); [Kaiko API docs: compare slippage](https://docs.kaiko.com/getting-started/kaiko-examples/compare-price-slippage-between-exchanges)
- Practitioner guidance commonly models execution delay by shifting the signal one bar (fill at the next bar's open, not the signal bar's close) and warns against assuming a limit order filled just because price touched its level. — [Vibe-Trading execution-model skill (practitioner code)](https://tessl.io/registry/skills/github/HKUDS/Vibe-Trading/execution-model)
- An unverified vendor blog claims realistic slippage and liquidity modeling cuts backtested returns by 0.5-3% a year. There is no methodology behind it, so treat it as anecdotal. — [LuxAlgo blog (vendor marketing)](https://luxalgo.com/blog/backtesting-limitations-slippage-and-liquidity-explained)

**How much costs shrink a BTC strategy in the He et al. perp study**
- **Gross to retail-tier fees, Binance BTC 2020-2024 (He et al.):**
  - Sharpe falls from 3.53 to 1.80 (about -49%) and annual return from 13.70% to 6.38% (about -53%).
  - The time the strategy can stay active falls from 100% to 20%, and the average holding period rises from 19 to 135 hours, because only the larger deviations still clear the cost hurdle.
  - The only costs modeled are **maker fees**, with no slippage or fill-failure modeling. The cost-adjusted figures are therefore still an upper bound for a retail taker.
  — [He et al. [WP, 2024]](https://arxiv.org/html/2212.06888v5)

### Inferences
- Combining Albers et al. with He et al.: even published academic cost adjustments (fees only, maker assumed) probably overstate what a retail or small algorithmic trader on Binance can achieve. Taker execution adds both the fee difference and adverse-selection slippage. Maker execution adds non-fill risk, and the trades most likely to go unfilled are the winners (price moves away).
- Close-price fills on bar data hide two biases. (a) The close is not an executable price, because you cross half the spread or more. (b) A signal computed on bar t's close cannot be filled at that same close. Both biases favor the strategy.

### Gaps
- The numeric slippage figures from Albers et al. (e.g. bps deterioration per volatility or latency bucket) could not be extracted. The PDF text was not machine-readable in this environment. The report writer should cite the qualitative findings only.
- No source quantified partial-fill rates for passive limit orders on Binance BTC perps.

## Q3. How do missing order-book depth and liquidity models make backtests on thin altcoins or low-liquidity hours look better than live?

### Takeaway
BTC on major venues is extremely liquid in normal conditions, with spreads often under 1 bp. Depth, however, is time-varying, venue-specific and fragile: it collapses in stress, varies by hour and weekday, and is far thinner on altcoins. Reported volume, a common backtest liquidity filter, is heavily inflated by wash trading on unregulated venues. Backtests that assume constant or volume-proportional liquidity therefore overstate what can be executed exactly when signals fire, which is in volatile, thin moments.

### Cited Findings
**Normal-condition liquidity**
- BTCUSD is more liquid than US equities, with bid-ask spreads "often below 1 basis point". Liquidity is driven by the same exchange's past liquidity, crypto-wide liquidity and volatility, and on-chain transfer fees. — [Brauneis, Mestel, Riordan, Theissen, "Bitcoin unchained", J. Empirical Finance 2022 [peer-reviewed]](https://econpapers.repec.org/RePEc:eee:empfin:v:69:y:2022:i:c:p:106-122)
- For estimating crypto liquidity from low-frequency data, the Corwin-Schultz and Abdi-Ranaldo spread estimators track time variation best, and Kyle-Obizhaeva and Amihud capture levels best. The benchmarks are order books for BTC and ETH on Bitfinex, Bitstamp and Coinbase Pro. This is relevant if a backtest has only OHLCV data. — [Brauneis et al., J. Banking & Finance 2021 [peer-reviewed]](https://madoc.bib.uni-mannheim.de/62108/); [Alpha Architect summary](https://alphaarchitect.com/how-to-measure-the-liquidity-of-cryptocurrency/)

**Depth collapse in stress**
- October 2023, during the false BlackRock ETF-approval report: Binance BTC 0.1% ask depth fell from about 100 BTC to 1.2 BTC (Kaiko data). Kraken and Coinbase held up better, and some traders reportedly saw slippage up to 20%. — [CoinDesk on Kaiko data (secondary, Oct 2023)](https://hotfix.coindesk.com/markets/2023/10/17/bitcoin-liquidity-on-binance-plummeted-during-the-etf-rumor-induced-market-rollercoaster-kaiko)
- 5 August 2024 sell-off: BTC-USD slippage on major US exchanges "tripled within hours". KuCoin BTC-EUR slippage exceeded 5%, and USDT/USDC pairs on BitMEX and Binance US rose by more than 3 bp. — [Kaiko "Moving markets" (vendor research, 29 Aug 2024)](https://www.kaiko.com/resources/moving-markets-liquidity-and-large-sell-orders)
- Aggregate BTC 2% depth was reported near $540M in Feb 2024, against more than $800M before the FTX collapse (Nov 2022). Market-wide depth regimes shift by hundreds of millions of dollars over months. — [FXStreet on Kaiko data (secondary, Feb 2024)](https://fxstreet.com/cryptocurrencies/news/bitcoin-order-books-are-most-liquid-since-october-as-market-depth-nears-540m-202402201148)

**Time-of-day and weekday effects**
- Coinbase hourly BTC slippage for a $100k sell rises around 15:00 and 20:00 UTC (the start and end of US market hours). Kraken's peaks around 14:00 UTC and is lowest around 23:00 UTC. — [Kaiko (vendor, Aug 2024)](https://www.kaiko.com/resources/moving-markets-liquidity-and-large-sell-orders)
- The weekend share of BTC volume fell from 24% (2018) to about 13% (early 2024), and Coinbase weekend spreads have widened since Q2 2023. — [Decrypt on Kaiko (secondary, 2024)](https://decrypt.co/219288/bitcoin-crypto-weekend-trading-liquidity-kaiko); [The Block (secondary, 2024)](https://www.theblock.co/post/279353/bitcoin-weekend-trading)
- These sources conflict. A later Kaiko analysis reported by Bitcoin.com found 1% depth lowest on Tuesdays and Wednesdays and highest on Fridays in 2025, unlike 2024 when weekends were shallowest. — [Bitcoin.com on Kaiko (secondary, 2025)](https://news.bitcoin.com/report-sundays-see-bitcoin-trading-spike-linked-to-institutional-market-hours)

**Altcoins and fake volume**
- Even the most widely traded altcoins show "significantly higher slippage than BTC on nearly all exchanges" (qualitative; no numbers given). — [Kaiko (vendor, Aug 2024)](https://www.kaiko.com/resources/moving-markets-liquidity-and-large-sell-orders)
- FTT's liquidity was far below what its market cap suggested and stayed more than 50% below pre-collapse levels (10% depth band). — [Kaiko CEX liquidity marketing page (vendor)](https://marketing.kaiko.com/cex-liquidity-data)
- **Cong, Li, Tang & Yang ("Crypto Wash Trading", Management Science 2023; NBER w30783), 29 exchanges, 2020 data:**
  - Wash trading averages more than 70% of reported volume on unregulated exchanges, up to 80% on some.
  - That is over $4.5T in spot and $1.5T in derivatives in Q1 2020 alone.
  - Regulated exchanges look statistically like traditional markets.
  — [NBER w30783](https://nber.org/papers/w30783); [Management Science](https://pubsonline.informs.org/doi/10.1287/mnsc.2021.02709)
- Micro-cap coins produce the size and volume "anomalies" but are "of negligible economic importance". — [Fieberg et al., IRFA 2024](https://open.icm.edu.pl/handle/123456789/25544)

### Inferences
- A backtest that uses volume (e.g. "participate at 1% of bar volume") as its liquidity proxy will overstate capacity on venues and coins with wash trading. Book depth is the safer proxy.
- Fills that assume normal liquidity are most wrong at the moments strategies trade most, such as breakouts, liquidation cascades and news. Depth can fall about 99% within minutes (Binance Oct 2023: 100 BTC to 1.2 BTC).
- Small-cap altcoin backtests carry wider spreads, thinner books and inflated volume all at once. This is consistent with academic findings that their anomalies don't survive costs.

### Gaps
- No primary dataset with numeric altcoin 1%/2% depth or slippage relative to BTC was found.
- Hour-by-hour Binance BTC-perp depth figures were not found, only Coinbase and Kraken spot patterns.

## Q4. What are latency arbitrage and execution delay, and why is assuming zero delay wrong?

### Takeaway
In live trading, time passes between the market event, signal computation, order transmission and the exchange's matching. During that window, books move in a direction that is correlated with the trade's profitability (adverse selection), not randomly. Across fragmented crypto venues, faster participants arbitrage stale quotes, so a slow strategy's quotes or market orders systematically get the worse side.

### Cited Findings
- Albers et al. (2025) tie the gap between expected and realized fills to "exchange delays, trader-side delays, or communication delays". The gap correlates with latency and volatility and hurts taker orders through adverse selection. This is direct live-trading evidence on Binance and Bybit. — [IDEAS/RePEc abstract](https://ideas.repec.org/a/taf/quantf/v25y2025i6p919-947.html)
- **Makarov & Schoar ("Trading and Arbitrage in Cryptocurrency Markets", J. Financial Economics 2020; 34 exchanges in 19 countries):**
  - Large, recurring BTC price gaps across exchanges last hours to weeks.
  - Gaps are much wider between countries (capital controls) than within them.
  - Gaps widen when BTC rises sharply.
  - Estimated arbitrage profits exceeded $1B over Dec 2017 to Feb 2018.
  - Fragmentation means "the price" in a single-venue backtest is not the price available everywhere. Cross-venue signals built on one venue's data can rest on gaps that were not tradable because of transfer frictions.
  — [JFE listing](https://econpapers.repec.org/RePEc:eee:jfinec:v:135:y:2020:i:2:p:293-319); [Harvard Law Forum summary (2019)](https://corpgov.law.harvard.edu/2019/09/21/trading-and-arbitrage-in-cryptocurrency-markets); [LSE Research Online](https://researchonline.lse.ac.uk/id/eprint/118909)
- Glassnode runs a public real-time latency monitor for centralized crypto exchange infrastructure, which shows that exchange-side latency varies and is measurable. — [Glassnode Latency Monitor (vendor tool)](https://latency.glassnode.com/cex/about)
- Practitioners recommend logging signal time, intended price and fill price in live or paper trading to measure the backtest-live gap directly. — [Reddit snapshot (practitioner forum, 2026; low authority)](https://reddit.sentinel-team.org/posts/1tnl249/snapshots/2026-05-27T16%3A55%3A25.196064Z)

### Inferences
- Zero-latency backtests are worst for short-horizon signals (minutes or less) and for signals that fire on fast moves, because the price drift during the delay runs in the signal's own direction. That is the essence of adverse selection.
- For bar-based strategies (hourly or daily), the main latency error is look-ahead from same-bar fills, not milliseconds. A one-bar shift is the minimum correction.

### Gaps
- No study quantifying return decay as a function of signal-to-order delay (e.g. bp lost per 100 ms or per bar) for BTC was found.
- "Latency arbitrage" against slow crypto traders (stale-quote sniping, as in the Budish et al. equity literature) was not found quantified for crypto venues.

## Q5. Are there studies quantifying how much backtested returns shrink after realistic costs, ideally crypto-specific?

### Takeaway
The firmest crypto-specific figure found is He et al. (2024). Adding retail-tier Binance maker fees alone roughly halves a BTC perp-spot strategy's Sharpe (3.53 to 1.80) and return (13.7% to 6.4%). That is before slippage, which Albers et al. show to be systematically adverse. Equity evidence agrees on direction (costs always hurt; turnover above about 50% a month rarely survives) but disagrees on size depending on who executes (academic spread-based estimates vs. AQR's patient institutional execution).

### Cited Findings
- **Crypto, He et al.:** Binance BTC 2020-2024 strategy goes from gross Sharpe 3.53 / 13.70% to 2.20 / 8.40% at VIP 8 fees, 2.16 / 7.93% at VIP 5, and 1.80 / 6.38% at VIP 1. Active time falls from 100% to 20%. — [He et al. [WP, 2024]](https://arxiv.org/html/2212.06888v5)
- **Crypto, Fieberg et al.:** Crypto anomalies are largely micro-cap driven or cost-heavy, and fade over time. — [Fieberg, Liedtke, Zaremba, IRFA 2024](https://open.icm.edu.pl/handle/123456789/25544)
- **Crypto, Caporale et al.:** Overreaction strategies are not profitable versus random, possibly because of transaction costs. — [Brunel WP ~2018](https://www.brunel.ac.uk/economics-finance-and-accounting/research/pdf/1801-Jan-GMC-Price-Overreactions-In-The-Cryptocurrency-Market.pdf)
- **Crypto, BIS:** Carry above 10% a year on average, but exploiting it carries margin-spike and liquidation risk. — [BIS WP 1087](https://www.bis.org/publ/work1087.htm)
- **Equities, Novy-Marx & Velikov:** Across 23 anomalies, costs always reduce profitability, and few strategies with monthly turnover above 50% stay significant net of costs. — [Novy-Marx & Velikov RFS 2016](https://mysimon.rochester.edu/novy-marx/research/ToAatTC.pdf)
- **Equities, Frazzini et al.:** Real institutional costs are under a tenth of earlier academic estimates, and short-term reversal is the most cost-constrained anomaly. — [Alpha Architect summary](https://alphaarchitect.com/the-best-research-paper-ever-written-on-trading-costs/)
- **Vendor claim:** A 0.5-3% annual return reduction from slippage and liquidity modeling, unverified. — [LuxAlgo (vendor blog)](https://luxalgo.com/blog/backtesting-limitations-slippage-and-liquidity-explained)

### Inferences
- A reasonable synthesis for BTC: high-turnover intraday strategies can lose most or all of their gross edge to fees, slippage and adverse selection. The cost hurdle per round trip at retail taker (about 10 bp in fees plus spread and impact) is large compared with typical intraday BTC edges. Lower-turnover strategies that hold positions mostly lose edge to funding (perps) or borrow (spot shorts).
- A backtest modeling only fees, with maker fills assumed, should be treated as an upper bound.

### Gaps
- No crypto study was found that reports the ratio of backtested to live returns for a real deployed strategy or fund.
- Hummingbot, Hudson & Thames, Deribit Insights and Binance Research write-ups on backtest-vs-live slippage were not reached within the tool budget, so their potential contributions are unverified.
