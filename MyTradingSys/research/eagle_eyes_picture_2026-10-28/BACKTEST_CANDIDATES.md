# Backtest candidates seen live (BTCUSDT, 2026-10-28)

Author: Eagle_Eyes (observer). Operator rule (10-28 about 22:40Z): at every price move, watch how the indicators behave around it and log anything worth a backtest. These are things SEEN once in a live session, written as testable definitions. No edge claim, no trade advice. Thresholds are OURS and must be fixed before the data is looked at. Shots are in the local shot store (not in the repo).

| # | Trigger (price) | Indicators read | What to measure | Seen at | Data needed | Status |
|---|---|---|---|---|---|---|
| C1 | Lower low on 1m or 5m at or under the lower BB | RSI, StochRSI, WT higher low; CVD and net delta higher low; OI direction | Forward move at 15, 30, 60 min, split by how many layers agree | 12:35 to 13:40Z (5m, OI up, RSI and CVD higher lows); 20:30 to 20:47Z (RSI mild, CVD did not agree) | Binance 1m klines, CoinGlass OI, CVD (taker delta) | idea |
| C2 | Burst bar near a band | Case A: OI up with negative delta and CVD. Case B: OI up with all positive. Case C: positive burst with OI down | Counts and forward move per case | A 20:46Z, B 20:56Z, C 20:00Z | same as C1 | card `flow-state-pairs-on-1m-oi-up-negative-de` |
| C3 | Price rides between upper and mid band for N bars | BB, RSI above 50, volume | Time to first close under the mid, then forward move | 17:00 to 20:00Z (5m) | 5m klines | idea |
| C4 | Lower highs on WT peaks while price is flat | WT peaks (+48, +40, +26), RSI peaks | Forward move after the third lower peak | 21:15, 22:00, 22:31Z (Bitstamp 1m), then a drop at 23:01Z | Bitstamp or Binance 1m | idea; E2 Krown S8 4h was INCONCLUSIVE |
| C5 | WT at or under about -55 then a cross up | WT, price low | Forward move 30 and 60 min | 20:47Z (WT -58, cross up, then about +370) | 1m klines | idea |
| C6 | Price spikes through a drawn heatmap cluster, then is rejected | Heatmap band, OI on the spike bar | Move after the touch; whether OI fell | 81,45x to 81,51x band, 20:00Z spike to 81,759 | Heatmap history: not stored (NOT_IN_DATA) | needs a recorder or saved shots |
| C7 | Top-trader ratio steps | Accounts and positions ratio, price, OI | Lead and lag at 15m to 2h | accounts 2.093 (15:01Z) to 2.017 (22:36Z) | Ratio history: Binance keeps 30 days only | concept only |

Open gaps behind every row: CVD, net delta and net longs/shorts anchors and units (NOT_IN_DATA); 15m footprint delta mismatch (card `legend-footprint-bar-delta-differs-betwe`). One session, one day: none of this is evidence.
