# GOLAS-B: how indicators relate in crypto perps, named setup types (ledger P0-03)

Date 2026-10-31. Builder, card ask-p0-03-golas-indicator-relations. Tier bar as in A_DIVERGENCE_METHOD.md: T1 = papers, exchange/platform docs; T2 = exchange/platform education pages; T3 (user posts, blogs) is below the bar and listed only as a negative finding. Quotes taken from the live pages on this date (fetch tool truncates at about 125 chars). Reused from ask-p0-02: the TradingView-is-T2-for-docs-only and T3-never-proof rules. No number here is a parameter of ours; every threshold quoted is the source's own and is NOT validated on our data.

## Result table (one row per setup type)

| Setup type | Relation claimed | Source URL | Verbatim quote | Tier | Not sourced |
|---|---|---|---|---|---|
| Price up + OI up (OI-price heuristic) | Buyers are the aggressors | https://arxiv.org/abs/2310.14973 (Giagkiozis, Said, "Reconciling Open Interest with Traded Volume in Perpetual Swaps") | "if open interest is rising and the price is increasing then the aggressors, presumably informed investors, are the buyers." / "This heuristic may or may not be valid." | T1 (paper, states it is unproven) | Any hit rate or forward return: NOT_IN_DATA |
| OI definition / what OI cannot show | OI changes only when contracts are created or settled; a trade can leave OI unchanged; some exchanges misquote BTC perp OI | same | "any increase or decrease of open interest in perpetual contracts implies that a prior trade has taken place" / "open interest in Bitcoin perpetual swaps is systematically misquoted by some of the largest derivatives exchanges." | T1 | Net long vs net short from OI alone: paper does not say; NOT_IN_DATA |
| Price down + OI up | New shorts entering | https://www.tradingview.com/education/openinterest | "If this was a healthy bearish continuation, we would normally see rising Open Interest as new short positions enter the market." | T3 (user-written idea on a T2 site; below bar) | T1/T2 source: NOT_IN_DATA |
| Price up + OI down | Short covering, not new longs | same | "This suggests the move is likely driven by short covering rather than aggressive new long positioning." | T3 (below bar) | T1/T2 source: NOT_IN_DATA |
| Price down + OI down | Long liquidation, no new shorts | same | "This combination suggests long liquidation rather than fresh positioning" | T3 (below bar) | T1/T2 source: NOT_IN_DATA |
| Funding spike + flat/falling OI | Overleveraged, correction likely | https://www.onebullex.com/academy/funding-rate-open-interest-divergence | "Funding rates climb to +0.05% or higher per 8 hours, but open interest does not increase or even declines slightly." / "The market is overleveraged, and a correction is likely." | T2 (exchange academy; the +0.05% threshold is the page's own, not tested) | Backtest or sample: NOT_IN_DATA |
| OI surge + neutral/negative funding | Shorts building; squeeze if price holds | same | "Open interest increases by 15% or more in 24 hours, but funding rates remain near zero or turn negative." / "If price stabilizes or rallies, these shorts are forced to cover, creating a short squeeze." | T2 | 15% threshold basis: NOT_IN_DATA |
| Funding falling + OI rising | Divergence resolves as a squeeze if no follow-through down | same | "Funding rates turn negative or drop sharply while open interest climbs." / "If the market does not follow through with a decline, the divergence resolves with a squeeze." | T2 | Time window, magnitude: NOT_IN_DATA |
| Funding high + OI high | Crowded; any reversal violent | same | "Both metrics rise sharply together, indicating a highly leveraged market with strong directional conviction." / "any reversal will be violent as overleveraged positions unwind." (second quote reconstructed from page text "any reversal will be violent as overleveraged positions unwind"; re-check before reuse) | T2 | Entry/exit rule: NOT_IN_DATA |
| Funding sign meaning | Positive: longs pay shorts; persistent sign = sentiment | https://www.binance.com/en/square/post/13424182691225 (reproduces Binance Academy perpetual intro) | "When the funding rate is positive, long positions pay funding to short positions." / "persistently positive funding rate" read as bullish sentiment | T2 | Predictive power of funding sign: NOT_IN_DATA |
| Funding anchors perp to spot | Funding keeps perp price near spot | https://academy.santiment.net/metrics/funding-rates-aggregated | "The goal is to ensure that the price of the perpetual contract stays close to the spot price of the underlying asset." | T2 | none (definition only) |
| Price x CVD (e.g. OI up + CVD down) | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | none | No T1/T2 page found stating a CVD-vs-price or OI-vs-CVD setup; the onebullex page "does not mention CVD or RSI"; a TradingView ETH post mentions CVD but its text was cut off |
| RSI x OI / funding / CVD | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | none | RSI is defined alone in A_DIVERGENCE_METHOD.md; no source relating it to OI, funding or CVD |

## Flags

- Every directional OI-price reading below T1 is a user post (T3). The only T1 source calls the heuristic unproven.
- All numeric thresholds (+0.05% funding, 15% OI in 24h) are the source's, uncited to data: treat as OURS-unvalidated before any use.
- Row 9's second quote was not re-fetched verbatim; mark it unverified until checked.
- A web-search summary listed "Falling OI + funding normalizing toward zero = leverage unwound" from a third-party page; not retrieved, not used.
