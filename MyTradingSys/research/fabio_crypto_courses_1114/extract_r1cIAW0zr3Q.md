# Extract: Andrea Cimi, "Stop Drawing Liquidity Lines... Use THIS Instead" (`r1cIAW0zr3Q`)

- **Video ID:** `r1cIAW0zr3Q`
- **Speaker:** Andrea Cimi (DeepCharts co-founder, free course EP "Complete Orderflow Trading Course", playlist PLBVwIU37953qr7DBLMJVXqcaVrJAaQy3D)
- **Market in the video:** CME S&P 500 futures, order-book heatmap (resting limit orders over time) plus aggressive-order bubbles; no crypto.
- **Source:** `raw_transcripts_canonical/r1cIAW0zr3Q_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Verdict:** every rule in this video reads resting limit orders in the order book heatmap. We have no order-book history (only aggTrades/klines), so nothing here is computable. One table row below; at most 2 quoted rules. No entry, stop or target number is stated in the video; all examples are chart narration.

## Rules

### H1. Heatmap book-liquidity statements (SOURCED, not computable)

| Statement | Needs | Computable from Binance aggTrades/klines | Entry / stop / target |
|---|---|---|---|
| Thick resting limit-order zones are less likely to be passed and more likely to turn price; zones act as a magnet and also as a deterrent; price travels "liquidity to liquidity" | order-book depth history (resting limit orders over time, spoofed or cancelled orders seen live) | no (needs book history) | NOT stated |

Rule: the thicker an area of resting liquidity on the heatmap, the lower the chance price goes straight through and the higher the chance of a reversal around it. Not computable (needs book history); our proxy would be traded-volume nodes (OURS, untested, not what he describes).

> "the thicker these areas of liquidity the lesser the chance that the price will just go through them but the higher the chance that price will reverse around these points" [0:03:37]
**Source GPS: r1cIAW0zr3Q | BEGIN**

> "these areas of liquidity usually work as a magnet for the market so Market will be attracted to these areas" [0:10:27]
**Source GPS: r1cIAW0zr3Q | MIDDLE**

Other statements in the video (spoofing visible as orders following price, order flipping, stop runs seen as vertical sweeps, market-maker cloud filtered by contrast, S&P order-book average of 50 contracts per level for market-impact maths, Wyckoff and ICT power-of-three comparisons) are narration of the heatmap or background with no numeric rule: no testable rule beyond H1.
