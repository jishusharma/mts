# Order book heatmaps, trade bubbles and liquidation heatmaps: how analysts say traders read them (2025-2026)

Reader: Sonnet agent for Lab_Guy, 2026-11-01, web only. Date opened for every source: 2026-11-01. Tiers: T1 paper, T2
exchange or vendor doc, T3 practitioner or journalist. Quotes marked "as fetched" came through a page summariser and are
not verified verbatim; "snippet only" means the page was not opened. Re-open before quoting elsewhere.

## Sources

| ID | Tier | Title | URL | Status |
|---|---|---|---|---|
| S1 | T2 | CoinGlass Learn: How to use Liquidity Heatmap | https://www.coinglass.com/learn/liquidity-heatmap-en | opened; no pub date |
| S2 | T2 | CoinGlass Learn: How to use Liquidation Heatmaps to assist trading | https://www.coinglass.com/ja/learn/how-to-use-liqmap-to-assist-trading-en | opened; no pub date |
| S3 | T2 | Bookmap: Heatmap in trading, complete guide to market depth visualization | https://blog.bookmap.com/blog/heatmap-in-trading-the-complete-guide-to-market-depth-visualization | opened; undated |
| S4 | T2 | Bookmap: How price reacts around fake liquidity, bait walls and phantom size | https://bookmap.com/blog/how-price-reacts-around-fake-liquidity-bait-walls-and-phantom-size | opened; 2025-10-07; ES futures example |
| S5 | T2 | Hyblock Academy: Liquidation Heatmap | https://academy.hyblockcapital.com/tools/liquidation-levels-1 | opened; undated |
| S6 | T2 | TheKingfisher glossary: Spoofing | https://thekingfisher.io/glossary/spoofing | opened; 2024-04-20 |
| S7 | T3 | Cointelegraph Research: Crypto market spoofing, identifying fake orders | https://cointelegraph.com/research/crypto-market-spoofing-identifying-fake-orders-and-their-impact | opened; 2024-04-03 |
| S8 | T3 | Cointelegraph (Pechman): Crypto crashed six months ago... | https://cointelegraph.com/markets/crypto-crashed-six-months-ago-have-markets-improved-or-are-bears-still-in-charge | opened; 2026-04-11; CoinAnk data |
| S9 | T3 | Digital Today: Bitcoin order book depth halves in six months | https://www.digitaltoday.co.kr/en/view/47346/bitcoin-order-book-depth-halves-in-six-months-crypto-market-liquidity-worsens | opened; 2026-04-12 |
| S10 | T3 | CryptoSlate: Something broke for crypto in October... | https://cryptoslate.com/crypto-traders-say-something-broke-after-in-october-the-data-says-the-market-really-did-change/ | opened; 2025-12-23; secondary summary of Kaiko and Coin Metrics |
| S11 | T2? | "How $3.21B vanished in 60 seconds" (blog.amberdata.io URL redirecting to kaiko.com) | https://www.kaiko.com/resources/how-3-21b-vanished-in-60-seconds-october-2025-crypto-crash-explained-through-7-charts | opened; page dated 28/07/2025, before the event; provenance unreliable |
| S12 | T2 | Kaiko Research: When October Surprise Meets Crypto Liquidity Drought | https://research.kaiko.com/insights/when-october-surprise-meets-crypto-liquidity-drought | snippet only (paywalled; 2025-10-13) |
| S13 | T3 | Cointelegraph: Bitcoin liquidity zones swept, OI uptick hints at recovery (Hyblock CEO quoted) | https://cointelegraph.com/news/bitcoin-liquidity-zones-swept-but-uptick-in-open-interest-hints-at-btc-recovery | opened; 2025-08-19 |
| S14 | T3 | CryptoSlate: Risky Bitcoin positions hunted, "liquidation treadmill" | https://cryptoslate.com/?p=515794 | opened; 2026-01-24 |
| S15 | T3 | ForkLog: Bitcoin traders highlight potential order book manipulations (Keith Alan, Material Indicators) | https://forklog.com/en/bitcoin-traders-highlight-potential-order-book-manipulations/ | opened; 2025-08-20 |
| S16 | T3 | Cointelegraph: Bitcoin pundits "spoof city" (trader Skew) | https://cointelegraph.com/markets/bitcoin-pundits-spoof-city-btc-price-gains-77k | opened; 2024-11-09 |
| S17 | T1 | Tuccella and Nadler, GRU-based spoofing detection (Kraken ETH/USD), arXiv 2110.03687 | https://arxiv.org/pdf/2110.03687 | snippet only |
| S18 | T1 | Hasbrouck and Saar (2009), via a search snippet of a later options paper | none opened | snippet only (equities) |
| S19 | T3 | Elliptic corpus spoofing pages (crypto perps); provenance unclear | https://www.elliptic.co/corpus/gen-3103/spoofing-finance/spoofing-detection-signals-in-crypto-perpetual-futures-and-derivatives-markets.html | snippet only (404) |
| S20 | T3 | Search summary: Material Indicators / FireCharts commentary Aug 2025 to early 2026 | multiple | snippet only |
| S21 | T3 | Search summaries: Binance post-mortem (2026-01-31), BitMEX Q4 report, Benzinga on Kaiko "voluntary liquidity gap" | multiple | snippet only |
| S22 | T3 | Vendor order-flow blogs on absorption and CVD | multiple | snippet only |
| S23 | T3 | Blofin Academy: Liquidation heatmaps and order flow | https://blofin.com/en/academy/education/trading/liquidation-heatmaps-order-flow | 403; snippet only |
| S24 | T3 | CryptoSlate (p=511978) citing Kaiko Binance 1 % depth; iTiger "one year after 10/10" | https://cryptoslate.com/?p=511978 | snippet only |
| S25 | T3 | NexusFi forum threads on Bookmap spoofing and icebergs | https://nexusfi.com/a/platforms/order-flow-heatmap-visualization | snippet only |

## Topic 1: Reading rules

| Claim | Source | Quote or paraphrase |
|---|---|---|
| Resting-order clusters presented as likely support or resistance | S1 | "often become real support or resistance zones" (as fetched) |
| Orders on the heatmap can be cancelled or modified | S1 | "participants may cancel or modify orders" (as fetched) |
| Resting liquidity as a barrier: offers resistance, bids support | S3 | "stacked offers above the price can act as resistance" (as fetched) |
| Absorption: a level hit repeatedly that holds | S3 | "repeatedly hit but still holds, that can suggest absorption" (as fetched) |
| Absorption: size refills at the level while hit (iceberg-like) | S4 | paraphrase: new size keeps refilling at the same price, real defence |
| Pulled liquidity makes the level less reliable | S3 | "If liquidity pulls before price arrives, the level may be less reliable" (as fetched) |
| Bait wall: looks like support or resistance, disappears as price nears | S4 | "disappear when the price gets close" (as fetched) |
| Breakout trap: wall pulled after a breakout, then snap-back | S4 | paraphrase |
| Real vs fake: real walls get traded into; fake ones show no prints | S4 | paraphrase: if price reaches the level and "no dots appear", it was phantom |
| Heatmap alone does not time entries | S3 | "It doesn't tell you when to buy or sell." (as fetched) |
| Trade what executes, not what is displayed | S6 | "Trade based on what's trading, not what's displayed." |
| Visible-but-never-traded orders are probably spoofed | S6 | "If the orders are visible but never trade, they're likely spoofed." |
| Depth as primary tool is a listed mistake | S6 | "Visible order book depth is mostly noise." |
| Liquidation heatmap bright zones as magnets | S2 | "market prices tend to gravitate towards these areas" (as fetched) |
| Market seeks forced-flow pools when books are thin | S14 | "the market tends to seek those pools when order books thin" (as fetched) |
| Liquidation heatmap values are relative intensity, not dollars | S2, S5 | S5: "essential to read it as a relative number" (as fetched) |
| Liquidity sweep then reversal: swept downside liquidity became support, shorts trapped | S13 | "that liquidity was swept", "shorts are currently trapped" (as fetched) |
| Bubble size = market-order volume; green = more market buys | S3 | "The bubbles shown indicate the volume of market orders." (as fetched) |
| Imbalance pane meaning: not defined by any source opened | - | gap; CoinGlass FAQ (FIELD_GUIDE.md) defines its own pane |

## Topic 2: Caveats

| Claim | Source | Quote or paraphrase |
|---|---|---|
| CoinGlass learn page names no exchanges for its heatmap | S1 | paraphrase (the product FAQ does: FIELD_GUIDE.md section 2) |
| Signals "not infallible" | S1 | as fetched |
| Liquidation heatmap shows more than will liquidate | S2 | "actual liquidation amounts that occur may be lower than the levels shown" (as fetched) |
| Map shows levels opening, not closing | S5 | "predicts where liquidation levels are opening but not closing" (as fetched) |
| Liquidation maps are model estimates from OI and leverage tiers | S5 | "calculates the liquidation levels based on market data and different leverage amounts" (as fetched) |
| Hypothesis generator, not a forecast | S14 | "not prophecies"; "a hypothesis to test, not a conclusion to embrace" (as fetched) |
| A cancellation rate alone does not prove spoofing | S19 | paraphrase, snippet only |
| Spoofing frequency needs level-3 data and cross-platform linkage | S7 | "would likely require correlating users across platforms" (as fetched) |
| Detectors can miss the final order sent without cancellation | S17 | paraphrase, snippet only |
| Spoof and iceberg detection need order-by-order data | S25 | paraphrase, forum, snippet only |
| Size near the market cannot be fully fake (risk of execution) | S25 | paraphrase, forum, snippet only |
| Material Indicators labels walls "spoofy" but hedges; intent cannot be proven | S15, S20 | "Too soon to make any assumptions" (as fetched) |

## Topic 3: Quantitative claims

| Claim | Source | Note |
|---|---|---|
| 248,796 orders submitted and cancelled during the LUNA/USD flash crash (2022-05-11) | S7 (citing ACM doi 10.1145/3604237.3626871) | one event, one pair |
| 124 uniform-sized orders placed and cancelled within one hour, same crash | S7 | same |
| A bid ladder of about $37M vanished between 39,000 and 40,000 | S7 | anecdote |
| About one third of limit orders cancelled within 2 s (2004 equities, INET) | S18 | equities, 2004, context only |
| No crypto source gives "x % of walls over $y are cancelled before touch" | - | gap |
| No numeric wall-size-to-depth threshold anywhere | S3, S4 | gap |
| Aggregate BTC spot +/-1 % depth about 180-260M (Sep 2025), about 150M (mid-Nov 2025), "seldom exceeds $130 million" (Apr 2026) | S8, S9 | CoinAnk figures |
| Depth below 60M for about 10 days in Feb 2026 | S8, S9 | "plunged below $60 million for nearly 10 days" (as fetched) |

## Topic 4: Use with CVD, footprint, OI

| Claim | Source | Quote or paraphrase |
|---|---|---|
| Delta-based signals show whether a level is accepted or rejected | S3 | "delta-based signals" help confirm "accepting or rejecting a level" (as fetched) |
| Volume dots show whether a wall is actually traded | S4 | paraphrase |
| Absorption = high executed volume while price stalls; spoof = resting order that vanishes before filling | S22 | paraphrase, snippet only, no thresholds |
| Executed flow and liquidation flow over displayed orders | S6 | paraphrase (vendor position) |
| Liquidation heatmap with depth and OI | S2 | "combining the heatmap with other market analysis tools" (as fetched) |
| Liquidation heatmap as confluence | S5 | "along with other indicators that may be used as confluence" (as fetched) |
| Liquidity heatmap with other indicators | S1 | "should always be used in conjunction with other technical indicators" (as fetched) |
| Sweep plus OI: new OI at a swept level marks trapped positions | S13 | one case, Hyblock CEO |
| Sweep trap: price hits a liquidation zone, CVD spikes, price stalls | S23 family | snippet only |

## Topic 5: Order book depth and the 2025-10-10 cascade

| Claim | Source | Note |
|---|---|---|
| Kaiko: near-mid depth almost empty on several venues; meaningful bids 4 % and 10 % from mid (Binance, Crypto.com, Kraken) | S10 (secondary) | not verified against Kaiko (S12 paywalled) |
| Coin Metrics: Binance BTCUSDT depth within +/-2 % thinned sharply | S10 (secondary) | no dollar figures |
| Top-of-book depth stayed "well below early October levels" afterwards | S10 | unattributed |
| Kaiko: "voluntary liquidity gap", collective risk tightening | S21 | snippet only |
| Kaiko: Binance 1 % depth above 600M at the Oct 2025 high, below 400M later | S24 | snippet only |
| Market makers throttled quotes; BitMEX: books thinnest since 2022 in Q4 | S21 | snippet only |
| Binance post-mortem: market makers' risk controls pulled liquidity; 75 % of liquidations before index deviation | S21 | snippet only, interested party |
| CoinAnk aggregate +/-1 % depth down about 50 % since Sep 2025 | S8, S9 | "plummeted by 50% since September 2025" (as fetched) |
| Counter-view: BTC book deeper than before the crash (iTiger and another analysis) | S24 family | snippet only; methodology differs, unresolved |
| S11 page: spreads up to 26.43 bps at 21:31 UTC vs 0.02 bps at day start; one venue's visible liquidity 103.64M to about 0.17M; imbalance +0.0566 to -0.2196 | S11 | provenance doubtful; do not cite until confirmed |

## Topic 6: Named practitioners

| Claim | Source | Quote or paraphrase |
|---|---|---|
| Keith Alan (Material Indicators), Aug 2025: "Spoofy the Whale" and "Notorious B.I.D." patterns around bids at 105,000 | S15 | "FireCharts is showing some behavior in the $BTC order book" (as fetched) |
| Material Indicators late 2025 to early 2026: buy wall near 88,000 flagged as likely to spoof; 50M ask wall before expiry; 50M order near 83k pulled | S20 | snippet only |
| Trader Skew: "Spoof city again today"; "Asks walking price down & bids causing price to bounce" | S16 | 2024-11-09 |
| Hyblock CEO Shubh Varma: thin weekend markets more vulnerable to liquidity grabs | S13 | paraphrase |
| Kingfisher pushes its trade-flow and liquidation-map tools over displayed depth | S6 | vendor position |
| Bookmap: iceberg = hidden size revealed by repeated absorption | S3, S4 | paraphrase |

## Reliability notes

- Vendor material (S1-S6) is marketing-grade guidance with no measured hit rates.
- No source gives backtested or fee-net results for any wall, sweep or liquidation-map rule.
- S7's cancellation numbers come from one LUNA crash.
- S11 should not be cited for numbers until confirmed with Kaiko or Amberdata.

Noticed: no Glassnode, CryptoQuant or Velo material on walls or heatmaps found; Kaiko's primary Oct 10 note paywalled;
no crypto cancel-before-touch rate by wall size; no wall-size-to-depth threshold; no primary X posts opened; no
independent test of heatmap or liquidation-map predictiveness in the sources; Blofin 403, Elliptic 404.
