# CoinGlass layers: usage synthesis (2026-10-28)

Author: Eagle_Eyes, from reader files A to D (same folder). Usage ideas only: no backtest, no edge claim, no trade advice.
Evidence level: papers (T1) cover same-interval flow-to-price association and perpetual pricing only. For heatmap clusters, OI, L/S ratios, funding, basis and premium as short-term signals the readers found "No validated evidence found". Everything below is T3 practitioner usage to TRY live and watch.
Several sources were read through search summaries only; the reader files flag them. Re-open before quoting.

## 1. Ideas that repeat across sources (hypotheses)

| Idea | Groups | Plain form |
|---|---|---|
| Price and OI move together or apart (4-way read) | A, B, D | Price down with OI up means new positions; price down with OI down means closing. Matches candidate concept 1 in `flow_layers_concepts_2026-10-28` |
| Liquidation bursts: did OI fall or rise afterwards | A, D | OI falls after a burst means leverage was flushed; OI rises means it was replaced |
| Heatmap clusters as magnets or reaction zones | A | Price tends to go to the nearest dense cluster; act just short of it, not on it |
| Crowd extreme: ratio at its own extreme + rising OI + stretched funding | B, D | Positioning crowded one way; squeeze or flush is the story told |
| Flow against price: new price extreme without CVD following | C | Divergence of CVD from price |
| Agreement between big flow and resting orders | C | Large-trade net flow and orderbook net agree = more reliable (one source) |
| Perp vs spot taker ratio | C, D | Perp-led flow next to OI and funding as a squeeze watch |

## 2. Where sources disagree (log both, pick neither)

- Top-trader ratios: follow the big book versus fade retail (group B).
- Sign of funding before a short squeeze (group D).

## 3. Layers that pair up (confluence candidates, operator idea)

| Pair or trio | Why the sources put them together |
|---|---|
| Heatmap level + OI + CVD | what OI and CVD do in the bars after price reaches a cluster |
| Liquidation burst + OI change + volume | flush or replace |
| Top-trader ratio + global ratio + OI + funding | crowd and big-book divergence |
| Perp-spot taker spread + OI + funding | squeeze watch |

## 4. NOT_IN_DATA (fill from Legend tooltips in Chrome before trusting)

Whale Index 1 to 4 formula; Net Delta definition; Active Buy/Sell Volume and Trades; CoinGlass taker formula and units; Model 3 and Hyperliquid map method; aggregated liquidation definition; CoinGlass definitions of OI Delta, Net Longs/Shorts, Aggregated L/S, Hyperliquid ratio, Funding, Basis, Coinbase Premium, CME OI, Fear and Greed. The CoinGlass docs also call the heatmap value both "leverage" and "USD amount".

## 5. Facts that change how we log

- Binance keeps only 30 days of top-trader and global ratio history: MTS must log the series itself to have history.
- Binance's liquidation stream pushes the latest liquidation per symbol per second: event counts are a lower bound.
- Binance funding interval is not always 8 hours: read it per contract.

## 6. Live-watch list for the dashboard (try today, observation only)

1. Price vs OI 4-way label on 5m; note whether the label held over the next 30 minutes.
2. Each time price reaches the nearest heatmap cluster: OI and CVD in the next few bars.
3. Each liquidation burst: OI up or down within 15 to 30 minutes.
4. Top-trader positions vs accounts vs global ratio: flag divergence, log which side moved next.
5. CVD vs price at new extremes on 5m.
6. Funding and predicted funding at settlement times (daily context only: CME OI, Fear and Greed).
