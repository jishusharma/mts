# Group B: Positioning (reader: Sonnet, 2026-10-28)

Tiers: T1 paper, T2 exchange docs / disclosed studies, T3 practitioner. A T3 usage idea is a hypothesis to try, never evidence.
All sources opened 2026-10-28. Honesty note: direct WebFetch of developers.binance.com failed (no output); the Binance definitions below come from web-search excerpts of those pages and are marked "via search excerpt". Re-open the pages to confirm exact wording before relying on it. CoinGlass's own indicator definitions (Legend/TradingView) were NOT found; CoinGlass-specific items are NOT_IN_DATA unless stated.

## Sources

| ID | Tier | Link | Opened | What it is |
|---|---|---|---|---|
| S1 | T2 | https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Top-Long-Short-Account-Ratio | 2026-10-28 (via search excerpt) | Binance top-trader L/S ratio (Accounts) |
| S2 | T2 | https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Top-Trader-Long-Short-Ratio | 2026-10-28 (via search excerpt) | Binance top-trader L/S ratio (Positions) |
| S3 | T2 | https://developers.binance.com/docs/zh-CN/derivatives/coin-margined-futures/market-data/Long-Short-Ratio | 2026-10-28 (via search excerpt, Chinese COIN-M page) | Binance global long/short account ratio endpoint |
| S4 | T3 | https://coinalyze.net/api3/long-short-ratio/ | 2026-10-28 (search excerpt) | Aggregator quoting Binance's global definition |
| S5 | T3 | https://docs.amberdata.io/data-dictionary/market/longshort-ratio | 2026-10-28 (search excerpt) | Data vendor: three L/S variants |
| S6 | T3 | https://www.coinglass.com/de/learn/guide-rookies-en | 2026-10-28 (fetched) | CoinGlass Guide for Rookies (vendor page) |
| S7 | T3 | https://www.luxalgo.com/library/concept/long-short-account-ratio/ | 2026-10-28 (fetched) | Practitioner concept page, no sourced studies |
| S8 | T3 | https://www.sharpe.ai/futures/ripple/long-short-ratio | 2026-10-28 (search excerpt) | Retail vs top-trader divergence idea |
| S9 | T3 | https://mudrex.com/learn/what-is-bitcoin-long-short-ratio/ | 2026-10-28 (search excerpt) | Says top-trader ratio more reliable (assertion, unsourced) |
| S10 | T3 | https://www.tradingview.com/scripts/netlongs/ (script: it.tradingview.com/script/trDi6evG-Net-Positions-Net-Longs-Net-Shorts-By-Leviathan/) | 2026-10-28 (search excerpt) | Third-party Net Longs/Net Shorts script; NOT confirmed to be CoinGlass's method |
| S11 | T3 | https://docs.coinglass.com/v4.0-zh/reference/hyperliquid-long-short-account-ratio-history | 2026-10-28 (search excerpt, Chinese) | CoinGlass API: Hyperliquid account long/short ratio history |
| S12 | T3 | https://forklog.com/en/bitcoin-whales-on-hyperliquid-reach-record-long-positions/ | 2026-10-28 (search listing only) | News reports citing CoinGlass whale long/short; methodology not stated |
| S13 | T1 | https://causalclaims.trfetzer.com/paper/w16712.html (Hong and Yogo, NBER w16712) | 2026-10-28 (fetched) | Open interest predicts returns, commodity futures mainly |
| S14 | T3 | https://www.theblock.co/post/380213/btc-perp-accounts-turn-heavily-long-as-binance-long-short-ratio-surges-to-3-87 | 2026-10-28 (search excerpt) | News: Binance top-20% metric counts each account equally |

## Per indicator

### Open Interest (OI) and OI Delta
| Q | Answer |
|---|---|
| 1 Definition | CoinGlass: "OI represents the total value of active, unsettled contracts in the market at any given moment"; "OI Change tracks the fluctuation of this value over specific periods, such as 1 or 24 hours" (S6, T3 vendor). Binance has an open-interest-statistics endpoint; its fields/periods were not verified (fetch failed). CoinGlass "OI Delta" indicator definition and update period: NOT_IN_DATA. |
| 2 Practitioner use | CoinGlass: rising price + rising OI = "healthy, strong trend driven by new long positions"; rising price + falling OI = weakness, short covering or false breakout (S6). Timeframe: 1h/24h change. Also as a 4-way price/OI-change table (S10, see Net Longs). |
| 3 Papers | Hong and Yogo (S13, T1): open interest movements predict returns in commodity futures, weaker in currency/bond/stock; this is commodities, not BTC perps. BTC/crypto perp OI predicting returns: No validated evidence found. |
| 4 Combined with | Price (S6), funding, ratio and liquidation clusters (S7). |
| 5 Live watch | On 1m/5m: OI change over the last N bars vs price direction. Working = the stated 4-way reading matches the next move more often than a coin flip, judged by us live; not a test. |

### Net Longs / Net Shorts
| Q | Answer |
|---|---|
| 1 Definition | CoinGlass definition NOT_IN_DATA. Closest found, a third-party TradingView script (S10, T3): each bar classified by OI change and price change (OI up + price up = longs opening; OI down + price down = longs closing; OI up + price down = shorts opening; OI down + price up = shorts closing); Net Longs/Net Shorts are running sums of OI Delta per class; Net Delta = Net Longs minus Net Shorts; ratio = NL/NS. Author notes true net notional of longs and shorts is always equal, so this is inferred flow, not a count. Unconfirmed that CoinGlass uses this method. |
| 2 Practitioner use | Only the script's own description; no usage rule found beyond reading flow of opening/closing. |
| 3 Papers | No validated evidence found. |
| 4 Combined with | OI + price (by construction). |
| 5 Live watch | Plot the inferred opening/closing classes next to price on 1m; watch whether "shorts opening" into a rise precedes squeezes. Hypothesis only. |

### Top Trader Long/Short Ratio (Accounts) and (Positions)
| Q | Answer |
|---|---|
| 1 Definition | Binance (S1, T2, via excerpt): Accounts = proportion of net long and net short accounts to total accounts of the top 20% users with highest margin balance; each account counted once; endpoint /futures/data/topLongShortAccountRatio; periods 5m to 1d; only latest 30 days available. Positions (S2) = proportion of net long and net short positions to total open positions of the top 20% users by margin balance (size-weighted). Amberdata (S5, T3) describes the same split: accounts counts each account once regardless of size; positions is dollar-weighted. Whether CoinGlass shows Binance only or other venues: NOT_IN_DATA. |
| 2 Practitioner use | Two camps, both T3, neither sourced. (a) Follow big book: when retail head-count and top-trader/size-weighted measures disagree, side with the larger book (S7); top-trader ratio called more reliable (S9, assertion). (b) Divergence retail vs top: fade retail when top traders are flat/short and retail heavily long (S8). Judge extremes against own trailing history, not fixed thresholds (S7). Timeframe: not specified. |
| 3 Papers | No validated evidence found. |
| 4 Combined with | Funding (stretched funding same side as crowd raises trust), OI build, liquidation clusters, price structure near support (S7). |
| 5 Live watch | Record Accounts vs Positions each 5m; flag divergence from the global ratio; note which side price moves toward over the next 30-60 min. Binance only gives 30 days of history, so we must log it ourselves. |

### Long/Short Ratio and Aggregated L/S Ratio
| Q | Answer |
|---|---|
| 1 Definition | Binance global (S3 via excerpt, S4 T3 quoting Binance): proportion of net long and net short accounts to total accounts with positions, each account counted once; endpoint globalLongShortAccountRatio, 30-day limit; sample response has longAccount, shortAccount, longShortRatio. Account-count based, so a high ratio means many small longs, not more capital (S8, T3). CoinGlass "Aggregated" L/S: which exchanges, how weighted: NOT_IN_DATA. S6 says only that selecting a coin shows long/short ratios; no interpretation given. |
| 2 Practitioner use | Contrarian at extremes: crowded long = long-flush risk, crowded short = squeeze risk; extremes can persist through trends ("wall of disbelief"); venue baselines differ, retail ratios long-skewed, cross-venue comparison unreliable (S7). |
| 3 Papers | No validated evidence found. S7 itself cites no studies. |
| 4 Combined with | Funding, OI, liquidation clusters, price compression, event risk (S7). |
| 5 Live watch | Ratio percentile vs its own trailing history; extreme + rising OI + stretched funding = the crowd setup to watch. |

### Hyperliquid Long/Short Trader Ratio
| Q | Answer |
|---|---|
| 1 Definition | CoinGlass API (S11, T3, Chinese, via excerpt): per-interval counts of accounts long and short, each side's percentage, and a long-short account ratio; sample numbers appear consistent with long% / short% (our arithmetic on a sample, not a stated formula). A separate "whale position" long/short ratio is quoted in news citing CoinGlass (S12); whale threshold not stated. Which of these the dashboard indicator uses: NOT_IN_DATA. |
| 2 Practitioner use | Only news reports of whale ratio values; no usage rule found. Hyperliquid positions are on-chain and public (our general knowledge; not sourced here). |
| 3 Papers | No validated evidence found. |
| 4 Combined with | Not found. |
| 5 Live watch | Compare Hyperliquid account ratio with Binance global ratio; note divergences. Hypothesis only. |

## Try today (max 5, hypotheses not evidence)
1. Price vs OI change 4-way read on 5m (S6, S10); log whether the label matches next 30 min.
2. Binance Top-Trader Positions vs Accounts vs global: flag divergence, log both sides' next move (S7, S8 conflict: follow big book vs fade retail; log which one wins, do not pick in advance).
3. Global ratio at own-history extreme plus rising OI plus stretched funding = crowd setup (S7); note flush/squeeze outcome.
4. Log Binance ratios ourselves from the API (30-day limit, S1/S3) to build history.
5. Hyperliquid vs Binance ratio divergence, observation only.

## Gaps
- Binance doc fetch failed: reconfirm S1 to S3 wording and the OI-statistics definition.
- CoinGlass's own definitions for OI Delta, Net Longs/Shorts, Aggregated L/S, Hyperliquid ratio: NOT_IN_DATA.
- No paper found on crypto-perp OI or L/S ratio predicting returns: No validated evidence found.
