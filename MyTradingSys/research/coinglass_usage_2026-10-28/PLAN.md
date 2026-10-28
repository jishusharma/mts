# CoinGlass layers: how are they used? Research plan (2026-10-28)

Author: Eagle_Eyes. Operator ask (2026-10-28): understand HOW each CoinGlass/Legend indicator is used, from articles, exchange and vendor docs and papers.
No backtest to prove anything; take the usage ideas, apply them live, see what works. Playbook Part I tiers apply (T1 papers, T2 exchange docs and disclosed studies, T3 practitioner); a T3 usage idea is a hypothesis to try, never evidence it works.

## Questions asked of every indicator

1. What exactly is it (definition, source exchange, update period, units)? Cite the vendor or exchange page. If not stated: NOT_IN_DATA.
2. How do practitioners say they use it (one-line rules, which timeframe)? Name the source and its tier.
3. What do papers or exchange research say about it? If nothing: "No validated evidence found".
4. Which other layers do the sources combine it with (the confluence idea)?
5. What would we look at on a live 1m or 5m chart to try it, and what would count as it working or not working today? (a thing to watch, not a test)

## Groups (one reader each)

| Group | Indicators |
|---|---|
| A Liquidation | Liquidation Heatmap (Models 1 to 3), Hyperliquid Liquidation Map, Liquidation (events), Aggregated Liquidations |
| B Positioning | Open Interest, OI Delta, Net Longs, Net Shorts, Top Trader L/S (Accounts, Positions), Long/Short Ratio, Aggregated L/S Ratio, Hyperliquid Long/Short Trader Ratio |
| C Order flow | CVD, Taker Buy/Sell, Active Buy/Sell Volume and Trades, Footprint, Large Trades, Orderbook Liquidity (Delta, Ratio), Whale Index 1 to 4 |
| D Context and confluence | Funding, Predicted Funding, Basis, Coinbase Premium, CME OI, Fear and Greed; how practitioners combine layers; squeeze write-ups |

## Output

One file per group in this folder (`A_liquidation.md` and so on): a table per indicator with the five answers, source links with the date opened, tier tags, and a closing "try today" list of at most 5 items. No numbers from memory; every claim needs a link.
Then one `SYNTHESIS.md` (Eagle_Eyes): which usage ideas repeat across sources, which layers pair up, and the live-watch list for the dashboard. No edge claims.
