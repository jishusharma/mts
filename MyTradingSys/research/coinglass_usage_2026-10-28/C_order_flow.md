# Group C: Order flow (CoinGlass usage research, 2026-10-28)

Reader: Sonnet agent for Eagle_Eyes. Plan: PLAN.md. All links opened 2026-10-28. Tiers: T1 paper, T2 exchange/vendor docs, T3 practitioner. A T3 usage idea is a hypothesis to try, not evidence. No backtests, no numbers from memory. "Seen via search snippet" = the page itself was not fetched or was blocked.

## Sources

| ID | Tier | Source | Link | Opened |
|---|---|---|---|---|
| S1 | T2 | CoinGlass Learn: What is Cumulative Volume Delta (CVD)? | https://www.coinglass.com/learn/what-is-cumulative-volume-delta-cvd | 2026-10-28 |
| S2 | T2 | CoinGlass Learn: What is Orderbook Liquidity? | https://www.coinglass.com/learn/orderbook-liquidity-legend-en | 2026-10-28 |
| S3 | T2 | CoinGlass Learn: What is Footprint Charts? | https://www.coinglass.com/learn/footprint-chart-en | 2026-10-28 |
| S4 | T2 | CoinGlass Large Order / Large Trade page | https://www.coinglass.com/large-orderbook-statistics | 2026-10-28 |
| S5 | T2 | CoinGlass API docs, Whale Index endpoint | https://docs.coinglass.com/reference/whale-index | 2026-10-28 |
| S6 | T2 | CoinGlass API Complete Guide (taker endpoints listed) | https://www.coinglass.com/learn/CoinGlass-API-Full-Guide-en | 2026-10-28 |
| S7 | T2 | CryptoQuant docs, Taker Buy Sell Volume/Ratio (other vendor, not CoinGlass; seen via search snippet) | https://docs.cryptoquant.com/data-guide/market/taker-buy-sell-volume-ratio | 2026-10-28 |
| S8 | T2 | Glassnode Futures Volume Delta (other vendor; search snippet) | https://studio.glassnode.com/charts/derivatives.FuturesVd | 2026-10-28 |
| S9 | T1 | Cont, Kukanov, Stoikov, The Price Impact of Order Book Events, J. Financial Econometrics 12(1) 2014 | https://arxiv.org/abs/1011.6402 | 2026-10-28 |
| S10 | T1 | Silantyev, Order flow analysis of cryptocurrency markets, Digital Finance 1(1) 2019 (BitMEX XBTUSD) | https://ideas.repec.org/a/spr/digfin/v1y2019i1d10.1007_s42521-019-00007-w.html | 2026-10-28 |
| S11 | T1 | Alexander, Heck, Kaeck, Riordan, Order Flow Impact and Price Formation in Centralized Crypto Exchanges, SSRN 2024 (abstract via search summary only) | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4867599 | 2026-10-28 |
| S12 | T3 | Charles Univ. thesis, Bitcoin limit order book on Binance (search summary only; thesis, so weaker than a journal paper) | https://dspace.cuni.cz/bitstream/handle/20.500.11956/185017/130372787.pdf | 2026-10-28 |
| S13 | T3 | bgeometrics Bitcoin CVD page (search snippet only) | https://charts.bgeometrics.com/orderflow.html | 2026-10-28 |
| S14 | T3 | TradingView open-source BTC Spot vs Perpetual CVD Divergence (snippet only) | https://in.tradingview.com/script/OnreHN3j-BTC-Spot-vs-Perpetual-CVD-Divergence | 2026-10-28 |
| S15 | T3 | LuxAlgo Footprint Concepts (snippet only) | https://www.luxalgo.com/library/concept/footprint-concepts.md | 2026-10-28 |
| S16 | T3 | Quantower, Reading Stacked Imbalance on the Footprint Chart (snippet only) | https://www.quantower.com/blog/imbalance-footprint-chart-and-rithmic-plugin | 2026-10-28 |
| S17 | T3 | CoinGlass X post, Whale Index "worth your study" (fetch blocked, HTTP 402; text via search snippet only) | https://x.com/coinglass_com/status/1933334280371122351 | 2026-10-28 |
| S18 | T3 | CoinGlass X post, whale orders and large trades example commentary (snippet only) | https://x.com/coinglass_com/status/2016045330547323199 | 2026-10-28 |
| S19 | T3 | CoinGlass YouTube: How to Read WHALE ORDERS and LARGE TRADES (title only, not watched; per memory notes, YouTube needs captions + verify) | https://www.youtube.com/watch?v=q8gp5kTcgK4 | 2026-10-28 |

## Per-indicator tables

### 1. CVD

| Question | Answer |
|---|---|
| 1 What it is | Sum of each bar's Delta (buy volume minus sell volume), plotted under price. Page does not give source exchange, update period or units. Delta can be shown for 1w, 1d, 4h, 1h, 15m. Green line = buys exceed sells, red = reverse (S1). Source exchange/units: NOT_IN_DATA. Glassnode defines futures volume delta as aggressive-buy minus aggressive-sell volume in the chosen window (S8, other vendor). |
| 2 Practitioner use | Vendor: gauge overall trend; check whether a top or bottom is confirmed; if price makes a new high or low and CVD does not follow, "may" signal reversal (S1, T2). Rising CVD with flat or falling price read as absorption (S13, T3). |
| 3 Papers | Trade-flow imbalance explains contemporaneous price change better than aggregate order flow imbalance on BitMEX XBTUSD (S10). Cont et al. show the relation is contemporaneous (explains moves in the same interval) in US stocks (S9). Predictive power of CVD divergence: No validated evidence found. |
| 4 Combined with | S1 compares only with price. S13/S14 pair spot CVD with perp CVD; a commercial script recommends VWAP, higher-timeframe structure, OI, funding (S14 snippet, T3). |
| 5 Try on live 1m/5m | Plot CVD under price; mark price new-high/CVD-not-confirming events; note what price did over next N bars. Working = divergence marks a stall more often than a coin flip as observed by eye; not working = price continues. Observation only. Note S1 timeframes list starts at 15m; 1m/5m use not documented by CoinGlass (NOT_IN_DATA). |

### 2. Taker Buy/Sell (ratio and volume)

| Question | Answer |
|---|---|
| 1 What it is | CoinGlass API lists futures and spot taker buy/sell volume history and aggregated spot taker stats; calls it "useful for sentiment analysis and trend reversal signals"; no definition, no intervals stated (S6). Taker = side that hits resting orders (S7, other vendor). CoinGlass formula, units, whether ratio is buy/sell or buy share: NOT_IN_DATA. CryptoQuant defines ratio = taker buy volume / taker sell volume, above 1 = buyers more aggressive (S7). A third-party CoinGlass wrapper uses a 0.5-centered buy ratio (glama.ai, unconfirmed, not cited as source). |
| 2 Practitioner use | Vendor line only: sentiment and reversal signals (S6). Above 1 vs below 1 as pressure side (S7); CryptoQuant itself cautions that above 1 does not necessarily mean price rises (S7 snippet). Perp taker-buy ratio minus spot taker-buy ratio read as "leverage-driven move" and squeeze precursor (S13, T3). |
| 3 Papers | Closest: signed trade flow imbalance explains same-interval price change (S10). Predictive use of taker ratio: No validated evidence found. |
| 4 Combined with | Spot vs perp comparison (S13, S14). |
| 5 Try live | Watch taker ratio on 1m/5m next to price; mark extremes and see if price follows or fades. Also try perp-minus-spot spread. Check CoinGlass tooltip for which formula the chart uses first. |

### 3. Active Buy/Sell Volume and Trades

| Question | Answer |
|---|---|
| 1 What it is | NOT_IN_DATA. No CoinGlass page found defining "Active Buy/Sell Volume" or "Trades" (count). Likely the same aggressor-side idea as taker volume, but that is inference, not sourced. Glassnode's aggressive-buy/aggressive-sell wording is the nearest definition (S8, other vendor). |
| 2 Practitioner use | None found for the CoinGlass label. |
| 3 Papers | Same as taker: trade flow imbalance (S10). Trade count vs volume: No validated evidence found in this pass. |
| 4 Combined with | NOT_IN_DATA. |
| 5 Try live | Read the Legend tooltip on the live app to get the definition; until then treat as taker volume and trade count by side. |

### 4. Footprint

| Question | Answer |
|---|---|
| 1 What it is | Per-price-level seller-executed (Bid) and buyer-executed (Ask) volume inside each candle; Delta per level and per bar; POC = level with most volume (S3). Source exchange, bar timeframes, tick size: NOT_IN_DATA on the learn page. A CoinGlass footprint page exists (https://www.coinglass.com/footprint?symbol=APT, search result), built on taker buy/sell data per a search summary; signals shift with timeframe. |
| 2 Practitioner use | Absorption: heavy one-side volume that fails to move price (S3, S15). Exhaustion: new extreme on thin volume (S3, S15). Breakout: sustained buyer volume with positive Delta is real, weak volume or negative Delta may be false breakout (S3). Stacked imbalances: several consecutive levels one-sided; many traders start around 200-300% ratio and tune; on retest, price slicing through = momentum, stall = absorption (S15, S16, T3; one search summary, thresholds are a practitioner starting point only). |
| 3 Papers | No validated evidence found for footprint patterns (absorption, stacked imbalance). |
| 4 Combined with | Liquidity heatmap (executed vs resting orders), volume profile, chart patterns (S3). Several T3 guides say confirmation only, not standalone entry (search summary). |
| 5 Try live | On 5m footprint, mark POC, bars with negative delta at a new high, stacked imbalance zones, and what price does on first retest. |

### 5. Large Trades (and large orders)

| Question | Answer |
|---|---|
| 1 What it is | Large trades = executed market orders above a size threshold, shown as bubbles; green = taker buy, red = taker sell; overlapping bubbles show only the largest. Default threshold control shown as >= $1M; five wall size tiers scale per coin. Live updates. Sources: Binance perp and spot, OKX perp and spot, Coinbase spot. Large orders = resting limit orders (walls), may be cancelled, so not trades; fill/cancel history kept 3 months (S4). |
| 2 Practitioner use | Large-trade net flow pane = CVD of large trades only (taker buys minus sells summed). Net resting orders = new bid walls minus new ask walls. When both point the same way the page says signals are more reliable (S4). CoinGlass X commentary: whale buy orders "defending" a level with heavy sell liquidity above, read as a liquidity-driven range (S18, T3, vendor marketing). |
| 3 Papers | Alexander et al. report limit order activity (submissions, cancellations) dominates price discovery on Coinbase and Binance BTC, per abstract summary (S11); relevant to treating walls as information but also to spoofing/cancel risk. Walls or large trades predicting direction: No validated evidence found. |
| 4 Combined with | Net flow of trades with net resting orders (S4); liquidity heatmap (S3 for footprint). |
| 5 Try live | Log large-bubble clusters vs wall tests at a level; note whether walls get cancelled before price arrives (the fill/cancel history helps). |

### 6. Orderbook Liquidity (Delta, Ratio)

| Question | Answer |
|---|---|
| 1 What it is | Delta = bid depth minus ask depth within a price band (quantity or value; units unspecified). Page says major platforms use a percentage band around price, 1% "commonly" for Bitcoin. Ratio = (bid - ask) / (bid + ask), usually -1 to +1, dimensionless (S2). Which exchange(s) and update period for the CoinGlass chart: NOT_IN_DATA on this page. |
| 2 Practitioner use | Delta positive and rising in a rally = strong buying intent, trend may continue; sharp fall or negative at a high = buying exhausted (S2). Ratio: set thresholds for buy signal or sell warning (S2, no values given). |
| 3 Papers | Cont et al.: price change over short intervals is linear in order flow imbalance at best bid/ask, slope inversely related to depth (S9, US stocks). Silantyev: strong linear link over long enough intervals on BitMEX, differences attributed to thinner depth and lower update rate (S10). Charles Univ. thesis on Binance reports non-linear impact and coefficient falling with depth (S12, T3). These are same-interval associations; forecasting use of depth imbalance: No validated evidence found. |
| 4 Combined with | Liquidity heatmap (S2). Page itself says relying solely on depth is limiting and that the ratio hides absolute depth (a balanced ratio in a thin book is still thin). |
| 5 Try live | Watch ratio at 1% band on 1m next to price; mark sustained readings above/below zero and sharp flips; check separately whether walls vanish when price approaches. |

### 7. Whale Index 1 to 4

| Question | Answer |
|---|---|
| 1 What it is | Only one "Whale Index" found: futures endpoint `/api/futures/whale-index/history`, fields time and whale_index_value (can be negative), exchange param (Binance default, OKX), intervals 1m to 1w, updates every minute (S5). Formula, units, what is "whale": NOT_IN_DATA. "Whale Index 1, 2, 3, 4" as separate series: NOT_IN_DATA, no source found; the numbering may be a Legend/app label not in public docs. CoinGlass API guide mentions only "CGDI, CDRI (whale & depth indicators)" with no definition (S6). Do not assume it equals Hyperliquid whale position data (those are a different product, news reports only). |
| 2 Practitioner use | CoinGlass X: "really a good indicator and worth your study" (S17, snippet; fetch blocked). A June 2025 CoinGlass post (per search summary) said a negative Whale Index suggests nearing the bottom or on verge of rebound (T3, vendor marketing, unverified, link not captured). |
| 3 Papers | No validated evidence found. |
| 4 Combined with | NOT_IN_DATA. |
| 5 Try live | Only after reading the tooltip in Legend for the exact definition. Then plot beside price, mark negative extremes, record price after. |

### 8. Net Delta (asked in task)

Definition: NOT_IN_DATA as a CoinGlass term. Nearest documented: footprint Delta = buy volume minus sell volume per level/bar (S3), Glassnode volume delta (S8, other vendor), and the large-trade net flow pane (S4). Do not treat these as the same without checking the Legend tooltip.

## Cross-source themes (hypotheses, not evidence)

- Price-vs-flow divergence (CVD, footprint delta, depth delta) read as exhaustion or absorption: S1, S2, S3, S13.
- Executed flow (trades) confirmed by resting liquidity (walls, heatmap): S2, S3, S4.
- Spot vs perp flow comparison to separate leverage from real demand: S13, S14.
- Academic support is for same-interval association of signed flow and price change (S9, S10), not for forecasting; crypto order books are thinner with lower update rates (S10).

## Try today (max 5)

1. 5m chart: CVD vs price, log new-extreme-without-CVD events and the next 6 bars by eye.
2. Large-trade bubbles plus large-trade net flow vs net resting orders: mark agreement vs disagreement (S4 says agreement is more reliable).
3. Orderbook ratio (1% band) flips: note whether wall cancellations precede the flip.
4. Footprint 5m: negative-delta new highs and first retest of stacked-imbalance zones.
5. Perp-minus-spot taker ratio spread next to OI/funding (group B/D) as a squeeze watch.

Before any of these: read Legend tooltips to fill the NOT_IN_DATA items (Whale Index 1-4, Active Buy/Sell, Net Delta, taker formula).

## Gaps

- Whale Index 1-4, Active Buy/Sell Volume/Trades, Net Delta: undocumented in public pages found.
- S11, S12, S13-S16, S17, S18: summary or snippet only, not read in full; re-verify before quoting.
- No Binance/OKX docs read on taker-side flag definition; not searched.
