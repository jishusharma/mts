# Group A: Liquidation layers, how they are used (2026-10-28)

Reader: Group A. Plan: PLAN.md. No backtest; T3 usage ideas are hypotheses to try live, not evidence. All sources opened 2026-10-28. Several pages were read through WebFetch/WebSearch summaries, not raw HTML; quoted text is as returned.

Tiers: T1 = papers (arXiv preprints, not peer reviewed unless stated); T2 = exchange docs, vendor docs, disclosed vendor statements; T3 = practitioner/blog.

## Sources

| ID | Tier | Source | Opened |
|---|---|---|---|
| S1 | T2 | CoinGlass on X, Models 1 vs 2 statement: https://x.com/coinglass_com/status/1833073677015126058 | 2026-10-28 |
| S2 | T2 | CoinGlass API, Pair Liquidation Heatmap Model2: https://docs.coinglass.com/reference/liquidation-heatmap-model2 | 2026-10-28 |
| S3 | T2 | CoinGlass API, Coin Liquidation Heatmap Model3: https://docs.coinglass.com/reference/liquidation-aggregated-heatmap-model3 | 2026-10-28 |
| S4 | T2 | CoinGlass API, Coin Liquidation Heatmap Model1: https://docs.coinglass.com/reference/liquidation-aggregate-heatmap (search summary only, not fetched) | 2026-10-28 |
| S5 | T2 | CoinGlass API, Coin Liquidation Map: https://docs.coinglass.com/reference/liquidation-aggregated-map (search summary only) | 2026-10-28 |
| S6 | T2 | CoinGlass Hyperliquid Liquidation Map page: https://www.coinglass.com/hyperliquid-liquidation-map | 2026-10-28 |
| S7 | T2 | CoinGlass Liquidation Data page: https://www.coinglass.com/LiquidationData | 2026-10-28 |
| S8 | T2 | CoinGlass on X, Hyperliquid map posts: https://x.com/coinglass_com/status/1977681633898909879 and https://x.com/coinglass_com/status/1987815598945091663 (search snippets only) | 2026-10-28 |
| S9 | T2 | Hyperliquid docs, Liquidations: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations | 2026-10-28 |
| S10 | T2 | Binance USD-M docs, Liquidation Order Streams: https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Liquidation-Order-Streams and All-Market variant .../All-Market-Liquidation-Order-Streams (fetch failed; content from search summary of the docs) | 2026-10-28 |
| S11 | T3 | SimpleMarkets, "CoinGlass Liquidation Heatmap & Data, Explained": https://simplemarkets.io/blog/post/coinglass-liquidation | 2026-10-28 |
| S12 | T3 | Kyledoops Substack, 2025-02-26 (promotes a paid group): https://kyledoops.substack.com/p/harnessing-liquidation-zones-magnet | 2026-10-28 |
| S13 | T3 | Bittime, "How to Read the Coinglass Heatmap" (intro only seen): https://www.bittime.com/en/blog/tag/rsi | 2026-10-28 |
| S14 | T3 | TradingView script description, OI drop + volume spike capitulation heuristic (closed source, CME BTC): https://in.tradingview.com/script/4Ww1ZJ40 | 2026-10-28 |
| S15 | T1 | Garcia Seuma, "Where does the criticality live?", arXiv:2607.27070, 2026-07-29: https://arxiv.org/abs/2607.27070 | 2026-10-28 |
| S16 | T1 | Sepper, "Slippage-at-Risk", arXiv:2603.09164, 2026-03-10: https://arxiv.org/abs/2603.09164 (abstract only) | 2026-10-28 |
| S17 | T1 | Donnelly, Lin, Lorig, "Optimal Liquidation of Perpetual Contracts", arXiv:2601.10812: https://arxiv.org/pdf/2601.10812 (search summary only; about execution of one's own position, not cascades) | 2026-10-28 |
| S18 | T1 | "Two-Regime Liquidity Recovery After a Perpetual Futures Liquidation Cascade", J. FinTech and Digital Assets: https://journals.lincoln.ac.nz/index.php/JFDA/article/view/1395 (search summary only; not fetched) | 2026-10-28 |
| S19 | T3 | FTI Consulting, "The Crypto Crash of October 2025": https://www.fticonsulting.com/en/canada/insights/articles/crypto-crash-october-2025-leverage-met-liquidity (search summary; consultancy, figures unverified) | 2026-10-28 |

## 1. Liquidation Heatmap, Models 1 to 3 (CoinGlass)

| Q | Answer |
|---|---|
| 1 What is it | An estimate, not a ledger. S11: it "infers where liquidations might cluster from visible open interest and assumed leverage"; "a model, not a ledger of real orders." Price on Y, time on X, colour by intensity. Model 1: "only calculates high leverage, 10X, 25X, 50X, 100X", for short-term trading; Model 2: "calculates all leverage", usually long-term (S1, CoinGlass's own post). Model 2 API is per exchange+pair (e.g. Binance BTCUSDT), Model 3 API is aggregated per coin; both take a range (12h to 1y) and return a price grid of [x, y, value] plus candles; real time; Professional/Enterprise plans only (S2, S3). Unit of the value is ambiguous in the docs themselves: "liquidation leverage" vs "liquidation amount in USD" (S2, S3). Model 3 definition: NOT_IN_DATA (docs say only "calculated from market data and various leverage amounts"). Exact formula, update period of the UI, source exchanges: NOT_IN_DATA. |
| 2 Practitioner use | T3 S11: treat bright bands "as zones of elevated probability, not levels price is guaranteed to reach"; set alerts short of a cluster, not at it; place stops beyond a dense cluster or cut size. T3 S12: "Magnet Zones: Liquidation clusters pull prices like gravity"; clusters as support/resistance where "big players flip trends"; "the real number of liquidations is lower" than shown. S12 gives no fixed timeframe; S1 implies Model 1 for short-term, Model 2 for long-term. S12 warns the 12h heatmap lags. |
| 3 Papers | No validated evidence found that heatmap clusters attract price or predict cascades. S15 does not test heatmaps. S11 itself: liquidation data "shows where forced sellers and buyers exist, not whether price will actually reach them." |
| 4 Combined with | S11: funding rates, open interest, volume profile, technical levels ("High funding plus liquidation clusters can mean elevated squeeze risk"). S12: OI, net longs/shorts, CVD, because heatmaps miss limit orders, market orders and stop-losses; cross-check other vendors (CoinAnk, Kingfisher) since CoinGlass lags and misses exchanges. |
| 5 Watch on 1m/5m | Overlay Model 1 (short horizon) on the chart; note the nearest cluster above and below spot. Looks like working: price travels to the cluster and reaction shows in CVD/OI after touching. Looks like not working: price ignores nearby clusters, or touches and no OI drop follows. Record both, do not tally as proof. |

## 2. Hyperliquid Liquidation Map (CoinGlass)

| Q | Answer |
|---|---|
| 1 What is it | CoinGlass page titled "Hyperliquid Real-Time Liquidation Map"; the page text gives no method, source or refresh interval (S6). CoinGlass's own posts quote it as showing individual "super whale" positions with a specific liquidation price (S8, snippets). Hyperliquid positions are on-chain and public, so levels can be computed per wallet rather than inferred (S9 gives the formula and rules; whether CoinGlass uses it: NOT_IN_DATA). Hyperliquid rules that matter: liquidation at maintenance margin; mark price used (blend of external CEX prices and book state); positions above 100k USDC only 20% sent to the book per order with a 30-second cooldown; backstop to the Liquidator Vault below 2/3 of maintenance margin (S9). |
| 2 Practitioner use | CoinGlass itself uses it as a headline alert: "If Bitcoin breaks above [level], a super whale's short ... will be liquidated" (S8). No independent practitioner rules found beyond generic liquidation-map reading. |
| 3 Papers | No validated evidence found that a whale liquidation level moves price. Related T1: S18 and S16 study Hyperliquid order-book liquidity around the 2025-10-10 cascade (S16 claims predictive validity for its own book-based metric, abstract only, unverified here); S15 finds no cross-event regularity in early-warning signals. |
| 4 Combined with | Not stated by CoinGlass (S6, S8). Generic: see Model rows. |
| 5 Watch | Watch whether price approaches a listed whale liquidation price on the BTC chart, and whether Hyperliquid liquidations (not other exchanges) print near it. Not working: level breached with no liquidation event or no extra volume. |

## 3. Liquidation (events) (CoinGlass Liquidation Data and exchange feeds)

| Q | Answer |
|---|---|
| 1 What is it | CoinGlass page: live liquidation feed and totals over 1h, 4h, 12h, 24h, history 1d to All; exchange filter; source not named and figures "May be below the market total" (S7). Exchange source example: Binance USD-M stream pushes, per symbol, only the latest liquidation order within each 1000 ms window as a snapshot, nothing if none occurs, so intermediate liquidations are dropped (S10, via search summary, one fetch failed). Payload has symbol, side, order type, quantity, price, average price, status, trade time (S10). Implication to verify on our own feed: event counts and sizes from Binance are a lower bound. |
| 2 Practitioner use | T3 S14: a sharp OI drop plus a volume spike is read as positions closing fast (usually longs), a "capitulation" entry candidate; price drop with rising OI plus volume is read as new shorts confirming the downtrend. S12 notes the Liquidation tool totals cover the last 24 hours. No timeframe rule found. |
| 3 Papers | S15 (T1, preprint): seven BTC cascades 2022 to 2025; no variable behaves the same across all events; price shows critical slowing down in five of seven but not the two sudden news shocks; only cross-event regularity is a decline in taker order-flow variance, a population-level precursor not a reliable per-event alarm. Cascade onset prediction from liquidation prints: no validated evidence found. S19 (T3, consultancy): high leverage plus auto-deleveraging turned the 2025-10-10 sell-off into a spiral; depth fell sharply; figures unverified. S16 (T1 abstract): forced liquidations can exhaust book liquidity, so execution can be far from theoretical price. |
| 4 Combined with | S14: open interest and volume. S12: CVD and OI. |
| 5 Watch | On 1m/5m, mark bars where long-liquidation prints cluster, then see what the next few bars do with OI and CVD. Working: OI falls while price stops falling. Not working: price continues through with OI still rising. |

## 4. Aggregated Liquidations (CoinGlass)

| Q | Answer |
|---|---|
| 1 What is it | Liquidation totals summed across exchanges, by time bucket, long vs short. CoinGlass's own definition page for the "aggregated" chart: NOT_IN_DATA (S7 gives only windows 1h to 24h and history 1d to All). Official API endpoint for aggregated liquidation history with parameters: not confirmed (search found only the Coin Liquidation Map endpoint, S5, and a third-party wrapper that is not CoinGlass docs). Coverage caveat: exchanges CoinGlass does not cover, and the feed limits in section 3, make the total a floor (S7, S11). |
| 2 Practitioner use | S11 (T3): compare windows, "a quiet 1h reading next to a large 24h figure tells a different story than both spiking at once", separating normal churn from a real event. S14 as above. |
| 3 Papers | No validated evidence found that aggregated liquidation totals predict direction or reversals. |
| 4 Combined with | S11: funding, OI, volume profile, technical levels, cross-asset context (liquidations often move alongside risk assets such as tech stocks). |
| 5 Watch | Compare 1h vs 24h totals on the dashboard when a 5m bar is extreme; note whether spikes line up with turning points or with continuation. Record only. |

## Try today (max 5)

1. Overlay Model 1 heatmap on the BTC 1m/5m chart; log each time price reaches the nearest cluster and what OI/CVD do in the next few bars (S1, S11, S12). Hypothesis only.
2. Place alerts just short of the nearest major cluster, not on it (S11).
3. Tag liquidation spikes where OI drops and volume spikes versus OI rises and volume spikes, and watch continuation vs stall (S14).
4. Watch the Hyperliquid map's listed whale level when price is near it; note whether liquidations print there (S8, S9).
5. Check our own Binance forceOrder capture against the 1-per-second snapshot limit, so event counts are labelled a lower bound (S10).

## Gaps

- Model 3 definition, heatmap formula, Hyperliquid map method, aggregated liquidation definition: NOT_IN_DATA from vendor sources found.
- No peer-reviewed or preprint evidence found on heatmap magnet effect; practitioner "magnet" claims are T3 and unvalidated.
- S4, S5, S8, S10, S13, S17, S18, S19 were not read in full; confirm before quoting in SYNTHESIS.
