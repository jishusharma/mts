# Group D: Context and confluence (2026-10-28)

Reader: Group D subagent. Scope per PLAN.md: Funding, Predicted Funding, Basis, Coinbase Premium, CME OI, Fear and Greed, confluence, squeezes.
All links opened 2026-10-28 unless marked SEARCH-ONLY (seen only as a search-result summary, page body not read). Tiers: T1 paper, T2 exchange/vendor doc or disclosed study, T3 practitioner. A T3 usage idea is a hypothesis to try, not evidence. Numbers below appear only where a fetched page stated them; sources are named inline.

## Source list

| ID | Tier | Source | Opened | Read how |
|---|---|---|---|---|
| S1 | T2 | Deribit support, Funding Specifications https://support.deribit.com/hc/en-us/articles/31424939178397-Funding-Specifications | 10-28 | SEARCH-ONLY (fetch 403) |
| S2 | T2 | Deribit support, Inverse Perpetual https://support.deribit.com/hc/en-us/articles/31424954847133-Inverse-Perpetual | 10-28 | SEARCH-ONLY |
| S3 | T2 | Binance Academy, What Are Funding Rates https://academy.binance.com/en/articles/what-are-funding-rates-in-crypto-markets | 10-28 | SEARCH-ONLY (fetch failed) |
| S4 | T2 | Binance FAQ, Intro to Futures Funding Rates https://www.binance.com/en/support/faq/introduction-to-binance-futures-funding-rates-360033525031 | 10-28 | SEARCH-ONLY (fetch failed) |
| S5 | T2 | CoinGlass funding page https://www.coinglass.com/FundingRate | 10-28 | fetched; dashboard only, no definitions |
| S6 | T2 | CoinGlass intro https://www.coinglass.com/learn/coinglass-intro-en | 10-28 | fetched |
| S7 | T2 | CoinGlass Fear and Greed page https://www.coinglass.com/pro/i/FearGreedIndex | 10-28 | fetched; title only, no methodology |
| S8 | T2 | CryptoQuant data guide, Coinbase Premium https://docs.cryptoquant.com/data-guide/fund-premium/coinbase-premium | 10-28 | fetched |
| S9 | T1 | He, Manela, Ross, von Wachter, Fundamentals of Perpetual Futures, arXiv 2212.06888 https://arxiv.org/abs/2212.06888 | 10-28 | abstract only |
| S10 | T1 | Ackerer, Hugonnier, Jermann, Perpetual Futures Pricing, arXiv 2310.11771 (NBER w32936) https://arxiv.org/abs/2310.11771 | 10-28 | abstract only |
| S11 | T3 | Maverick Quant, Perpetual Futures (2025-03-12) https://maverickquant.substack.com/p/perpetual-futures | 10-28 | fetched |
| S12 | T3 | The Block, CME BTC futures activity (2026-04-09) https://www.theblock.co/post/396722/cme-bitcoin-futures-activity-slumps-to-14-month-low-as-basis-trade-unwind-drains-institutional-demand | 10-28 | fetched |
| S13 | T3 | CoinGecko, Crypto Fear and Greed Index https://www.coingecko.com/learn/crypto-fear-and-greed-index | 10-28 | fetched (describes the Alternative.me-style index, not CoinGlass's) |
| S14 | T3 | investinglive, shorts squeezed (2026-09-22) https://investinglive.com/education/crypto-open-interest-jumped-as-650m-of-shorts-were-squeezed-where-the-data-comes-from/ | 10-28 | fetched |
| S15 | T3 | BIT Knowledge Hub, Short squeeze (2026-08-25) https://www.bit.com/knowledge-hub/short-squeeze | 10-28 | fetched |
| S16 | T3 | Axel Adler Jr, OI and funding quadrants (2026-02-25) https://axeladlerjr.com/bitcoin-open-interest-funding-rate/ | 10-28 | fetched |
| S17 | T3 | TradingView script, Liquidity Trap Squeeze Detector https://www.tradingview.com/script/Q4X2DK2s-Advanced-Liquidity-Trap-Squeeze-Detector-MazzaropiYoussef | 10-28 | SEARCH-ONLY |
| S18 | T3 | TradingView script, Coinbase Premium Index Any Symbol https://www.tradingview.com/script/NXnLGGdF-Coinbase-Premium-Index-Any-Symbol/ | 10-28 | SEARCH-ONLY |
| S19 | T3 | MEXC news on funding thresholds https://www.mexc.com/news/339995 | 10-28 | SEARCH-ONLY |
| S20 | T3 | Benzinga/Glassnode, institutional BTC strategies (2024-10) https://www.benzinga.com/markets/cryptocurrency/24/10/41524936/institutional-bitcoin-investors-have-their-own-trading-strategies-heres-one | 10-28 | SEARCH-ONLY |

CoinGlass learning-center pages for Funding, Basis, Coinbase Premium, CME OI, Fear and Greed: not found. /learn category pages listed no articles in the fetch; guessed URLs for Basis and Coinbase Premium returned 404.

## Funding

1. Definition (S1, S2, S3, S4, S11; S1-S4 search-only): periodic payment between longs and shorts on a perpetual, to keep its price near spot/index; positive means longs pay shorts, negative the reverse; the exchange is not the recipient (S3). Deribit: based on mark price vs Deribit index premium, accrued continuously and settled daily (S2). Binance: premium index plus an interest component, normally 8-hour interval, with some contracts moved to shorter intervals in 2025 (S3, search summary; verify per contract). S11 (older Binance method): premium sampled every 5 s, linearly averaged over 8 h, plus clamped term toward a 1 bp baseline, payments at three fixed UTC times. CoinGlass page itself gives no definition or update period: NOT_IN_DATA (S5). CoinGlass shows OI-weighted and volume-weighted BTC funding, accumulated funding, a funding arbitrage list and a heatmap (S5).
2. Practitioner use: positive funding = leveraged long demand, negative = crowded shorts (S14, S15). A neutral baseline near 0.01 percent with above read bullish and below read bearish is quoted as a rule of thumb, not a standard (S19, search-only). Rate often sits at the baseline, so it carries information mainly when it leaves the neutral band (S11, author's inference). Timeframe: not stated by most; S16 uses daily.
3. Papers: perpetual price is not guaranteed to converge to spot; deviations from no-arbitrage price are larger than in currency markets, co-move across coins and shrink over time (S9). Funding design determines anchoring (S10). Neither tests funding as a directional signal for intraday price. Directional predictive value of funding: No validated evidence found.
4. Combined with: OI (S16, S14, S15), liquidations (S14, S15), taker volume (S14), CME share of OI (S16 notes CME pays no funding, so aggregate funding may understate conviction).
5. Live watch: CoinGlass funding (OI-weighted BTC) next to OI and 1m/5m price. Working = extreme funding plus OI rise precedes liquidation cascade or sharp reversal more often than chance in what we see; not working = extremes with no follow-through. Observation only.

## Predicted Funding

1. Definition: CoinGlass lists a "Predicted" option with no explanation (S5): NOT_IN_DATA. Exchange side: the rate is built from a premium averaged over the interval (S11, S2), so a predicted value is the interval-to-date premium path; this is our reading, not a vendor statement.
2. Practitioner use: No usage source found. No validated evidence found.
3. Papers: none specific. No validated evidence found.
4. Confluence: none sourced.
5. Live watch: compare predicted vs the last settled rate near the funding time; whether price tends to move when they diverge is an open question, not a claim.

## Basis

1. Definition: CoinGlass basis page not found (404): NOT_IN_DATA. General: futures price vs spot; dated futures converge at expiry, perpetuals use funding instead (S11). For CME the annualised basis is compared to short-term Treasury yield (S12).
2. Practitioner use: the CME-spot ETF cash-and-carry trade buys spot ETF and shorts CME futures; "the key metric to watch is the CME basis rate relative to short-term Treasury yields"; when basis yield falls to risk-free plus capital cost the trade unwinds (S12). Basis as a directional intraday tool: No usage source found.
3. Papers: perpetual-spot deviation is the same object as perp basis; arbitrage after trading costs is claimed to be profitable in the sample (S9). No validated evidence found for intraday timing use.
4. Confluence: CME OI (S12, S20 search-only).
5. Live watch: perp basis vs funding vs price on 1m, as a stress gauge.

## Coinbase Premium

1. Definition: price difference between Coinbase BTCUSD and Binance BTCUSDT (S8). CoinGlass definition and update period: NOT_IN_DATA (page not found). Unit: S8 does not say; CryptoQuant elsewhere has a percentage Index and dollar Gap (search-only).
2. Practitioner use (S8, T2 vendor reading, interpretive): high or rising = possible Coinbase "whale" accumulation; low or falling = weak demand or selling. TradingView scripts say it is a short-term tool best combined with others (S18, search-only). Caveat from search results: stablecoin stress can distort it (search-only, no page read).
3. Papers: No validated evidence found.
4. Confluence: price trend, "whale" layers (S8 frames it as a whale proxy).
5. Live watch: premium sign flips against 5m price direction; note CoinGlass may use a different definition from CryptoQuant.

## CME OI

1. Definition: open contracts on CME BTC futures. CoinGlass page not read: NOT_IN_DATA. CME futures pay no funding (S16).
2. Practitioner use: proxy for institutional positioning, tracked together with basis (S12). Falling CME OI is read as basis-trade unwind (S12). Daily or slower; no intraday use found.
3. Papers: No validated evidence found.
4. Confluence: basis vs Treasury yield (S12); funding and aggregate OI (S16 caveat).
5. Live watch: low value on 1m/5m (daily scale); record as slow context only.

## Fear and Greed

1. Definition: CoinGlass page has no methodology in the fetch: NOT_IN_DATA (S7). A secondary source describes an Alternative.me-style index, 0 to 100, from volatility, momentum/volume, social media, dominance, Google Trends and a paused survey (S13); CoinGlass's weights are unknown and not assumed equal. Search-only note: providers differ and the index can sit in extremes for weeks or months.
2. Practitioner use: contrarian sentiment gauge, short and mid term, never alone (S13).
3. Papers: No validated evidence found.
4. Confluence: "other market metrics" (S13), unspecified.
5. Live watch: slow daily context only; unsuited to 1m/5m.

## How practitioners combine layers (confluence)

| Idea | Source | Tier |
|---|---|---|
| OI = how much leverage, funding = which way it leans; neither alone is enough | S16 | T3 |
| OI rising + funding positive = leverage building long; OI rising + funding negative = new shorts, rare; OI falling + funding positive = longs flushed; OI falling + funding negative = capitulation | S16 | T3 |
| Liquidations show forced flow, OI shows whether leverage was replaced, funding and taker volume show direction | S14 | T3 |
| Overlay OI and funding on the price chart; CoinGlass Legend adds liquidity heatmap, footprint and large trades | S6 | T2 |
| Squeeze detector = relative OI + funding sign + aggressive flow (search-only) | S17 | T3 |
| Order book and volume as confirmation for any squeeze signal (search-only) | S17 | T3 |

No source gives a tested combined rule. Quadrant frequencies and thresholds in S16 come from one blog's daily aggregate data (2019-2026) and are not validated; they apply to daily bars, not 1m/5m.

## Squeezes: how described and identified

- Short squeeze chain: forced short liquidations require buy-backs which can trigger more liquidations; "powerful but self-limiting" (S14).
- Setup: crowded shorts shown by negative funding, strengthened by rising OI; "necessary fuel, not a trigger" (S15). S16 flags OI rising with deeply negative funding for 2+ days as a setup and waits for funding to recover before acting.
- Execution evidence: short-liquidation total dominating the liquidation total, OI rising afterwards means new leverage replaced it (S14).
- Conflict: a TradingView script ties short squeeze to high OI plus POSITIVE funding plus aggressive buying (S17, search-only), the opposite funding sign to S15/S16. Sign convention and definition of "squeeze" differ between sources.
- Data caveat: Binance public liquidation feed shows only the latest order per contract each second, so totals are estimates (search summary, S14 context).
- Papers on squeeze identification: No validated evidence found.

## Try today (max 5, observation only)

1. Log BTC OI-weighted funding, OI change and price on 5m; tag quadrant per S16 logic and note what price did next.
2. Mark every large short-liquidation burst (Group A) and record whether OI rose or fell within the next 15 to 30 minutes (S14 test of "replaced leverage").
3. Watch funding at settlement times for predicted vs settled gap.
4. Track Coinbase premium sign vs 5m direction; first confirm CoinGlass's definition.
5. Treat CME OI and Fear and Greed as daily context labels, not triggers.

Noticed: Funding intervals are no longer always 8 h on Binance (S3 search summary), so any funding-time logic must read the per-contract interval.
