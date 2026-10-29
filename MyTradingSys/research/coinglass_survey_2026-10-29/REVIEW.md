# CoinGlass review for the live observer

**Verdict.** CoinGlass is worth using for four things: 1m net delta / aggregated CVD / net longs-shorts (Supercharts), Legend Large Trades bubbles, the liquidation heatmap/map plus 1h/4h liquidation totals, and the Coinbase premium. All free to view. Everything else is daily or slow context. There is no free API; the cheapest feed is $29/mo (personal use, 30 requests/min, 80+ endpoints). On the 10-28/29 move, three pages showed the sell at 81,800 and the flush toward 79,800 (Legend bubbles, 1m delta/CVD, liquidation totals).

Caveat: one anonymous snapshot (about 02:30 UTC). Liquidation heatmap values are modelled, not realised.

## What exists vs what matters
| Data | Where | Granularity | Matters for observer | Matters for severity rating |
|---|---|---|---|---|
| Net delta, agg CVD, net longs/shorts | /tv | 1m | Yes, top | Yes (same-bar collapse = high) |
| Large trades, footprint | Legend | 1m+ | Yes | Partly (size scale about $4M max seen) |
| Liquidation heatmap / map | /pro/futures/Liquidation* | live model | Yes (stop clusters) | Partly (pre-event, not realised) |
| Liquidation totals 1h/4h/24h | /liquidations | live | Yes | Yes (size vs 24h average) |
| Coinbase premium | /pro/i/coinbase-... | 1m-1d | Yes | Yes (US flow tag) |
| OI by exchange, 1h/4h change | /open-interest/BTC | live | Yes | Yes (de-risk vs new positions) |
| Orderbook liquidity delta | /pro/depth-delta | 15m | Some | Weak |
| Long/short accounts and top trader | /LongShortRatio | 30m-4h | Some (divergence) | Weak |
| Funding rates | /FundingRate | 8h | Context | Weak |
| Options, max pain | /pro/options | daily | Expiry days only | No |
| Trading sessions | /TimeZoneDistribution | daily | No | Maybe (Asia/EU/US weighting) |
| ETF flows, CME COT | /pro/i, /pro/cme | daily | No | Macro tag |
| Cycle indicators (AHR999, rainbow, peak checklist, many more) | /pro/i | daily | No | No |
| Altcoin heatmaps | /pro/heatmap | live | No | No |

## Redundant with what MTS already has
These need a check against our own feeds before any adoption (not verified here, NOT_SEEN in repo): Binance funding, OI, taker buy/sell, long/short ratios and liquidation stream are available from the exchange APIs directly, so CoinGlass adds value only where it aggregates across exchanges (aggregated CVD/delta, cross-exchange OI, aggregated liquidations, Coinbase premium).

## Missing from CoinGlass (not seen)
- No free raw tick / trade stream, no per-minute realised liquidation history (daily only on the history page), no free API or export.
- Large-trade threshold and Whale Index definitions not documented on the page.
- Footprint cells and Legend Liquidity Heatmap not inspected, so L2 depth heat is unconfirmed.
- No explicit timestamped alert feed seen on free pages (Alerts link exists, NOT_SEEN).
- Time zones differ across tools (Legend uses the browser zone, Supercharts appears UTC); needs pinning before any cross-reading.

## Candidates to decide
| # | Candidate | Cost | Note |
|---|---|---|---|
| 1 | Observer tab pack: Supercharts layout + Legend Large Trades + liquidation heatmap + Coinbase premium, opened by the operator | free, manual | fastest win; screenshot-based reading only |
| 2 | Add liquidation 1h/4h long-short totals and Coinbase premium to the severity rating as tags | free, manual until a feed exists | needs a numeric threshold from our own events (OURS) |
| 3 | Test one month of the Hobbyist API ($29/mo) for aggregated CVD, liquidations, OI by exchange | $29/mo | confirm endpoint coverage and latency before paying |
| 4 | Do not adopt cycle indicators, options, ETF, altcoin heatmaps for the live observer | none | not intraday |
| 5 | Open follow-ups: inspect Footprint and Liquidity Heatmap in Legend; read Whale Index definitions; check Alerts | free | NOT_SEEN items above |
