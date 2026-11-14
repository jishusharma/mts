Big sellers dominate the last 24 h before every low and big buyers only show up AT the low and in the 24 h after it (5 of 6 lows), so large-trade flow confirms a low after the fact and does not call it in advance; today's selling looks like the pre-low blocks, not like a finished flush.

Descriptive study, no trading rule, nothing pre-registered. n = 6 lows, so read the tables as pictures, not statistics. Data: Binance spot + USDM futures aggTrades and Bybit USDT-perp trade dumps, 9 days around each low (low day -4 to +4) plus 2026-10-24 to 2026-11-12; Coinbase BTC-USD vs Binance BTCUSDT hourly closes. Hourly aggregates are in `F:\MTS\data_cache\bigtrades\` (about 1 MB). Scripts: `fetch_hourly.py`, `fetch_premium.py`, `fetch_rest_spot.py`, `analyze.py`, `leadlag.py`, `today_spot.py`; full tables in `analysis_out.md`, `leadlag_out.txt`, `today_spot_out.txt`.

## (a) What published work says (understanding, not validation)

Honest note: the search returned analytics-firm commentary and news write-ups of it, not primary reports. I could not open Glassnode / CryptoQuant / Kaiko originals. Numbers below are as reported by the linked pages.

| Source | What they measured | What they found | Weak point |
|---|---|---|---|
| [CryptoQuant via Cointelegraph, Sep 2022](https://cointelegraph.com/markets/bitcoin-whales-send-btc-to-futures-exchanges-in-classic-bottom-signal) | 30-day average of coin transfers from spot exchanges to derivatives exchanges | Spikes "typically" near local bottoms; story: whales fund long futures | No threshold, no outcome table in the article |
| [CryptoQuant via Whale Alert, Dec 2025](https://whale-alert.io/stories/9375c43e251f/On-chain-whale-accumulation-was-exchange-internal-consolidation-true-whales-and-mid-size-holders-net-sold-in-December-coinciding-with-a-price-drop) | Cohort balances (whales >1,000 BTC, mid 100-1,000) after removing exchange-internal moves | A big "accumulation" signal was exchange cold-wallet housekeeping; filtered whales were net sellers while price fell 94.3k to 84.6k | Secondary report |
| [Glassnode Accumulation Trend Score via NewsBTC/DigitalMoneyBox, Jan 2026](https://digitalmoneybox.com/news/bitcoin/bitcoin-bottoming-phase-was-driven-by-large-entities-glassnode-data-shows) | Balance changes weighted by wallet size, by cohort | Nov-Dec bottoming phase: 10,000+ BTC wallets near max accumulation, small wallets sold; mega whales went neutral by mid-December | Wallet reshuffles blur it; no exact dates |
| [Santiment + Material Indicators via Cointelegraph, 28 Dec 2022](https://cointelegraph.com/markets/bitcoin-price-bottom-not-in-data-says-as-whale-orders-hit-2-year-low) | Count of on-chain transfers >= $1M; Binance BTC/USD order-book bids | Whale activity at 2-year low = "bottom not in" (it was in, 15.5k was 5 weeks earlier) | Shows these signals can read bearish after the low |
| [Kaiko via Kitco, Jul 2022](https://www.kitco.com/news/article/2022-07-27/crypto-bankruptcy-proceedings-slow-massive-selloffs-triggered-bear-market) and [CoinDesk Jan 2022](https://www.Coindesk.Com/business/2022/01/03/bitcoin-whales-were-active-on-coinbase-amidst-a-quiet-holiday-week/) | Second-by-second buy vs sell for trades > 5 BTC; exchange market share | Called the June 2022 17k low a likely floor; large Coinbase buying clusters were seen without moving Coinbase's share | Not a low study |
| [CryptoQuant Coinbase Premium via Cointelegraph, Jul 2026](https://cointelegraph.com/markets/bitcoin-whales-sent-btc-price-to-64k-as-coinbase-premium-broke-key-level-cryptoquant) | Coinbase minus Binance BTC/USDT price, 14-day SMA | Reclaiming the SMA14 from negative gave a bounce (58k to 64k); lasting change needs premium above zero; it had been negative since 6 May 2026 ([report](https://www.mexc.com/news/1187967)) | Single episode |

What I take from it, in plain words: everyone defines "whale" differently (on-chain wallets vs exchange prints vs transfers); on-chain "whale buying" is often exchange plumbing; the same reading is bullish to one analyst and bearish to another; and the signals are usually stated at the moment of the move, after the fact. That matches what my own numbers show.

## Context

Regime mix of the 6 lows (known at the time: drawdown from the all-time high to that day, close vs 200-day SMA):

| Low (UTC hour) | Price | Drawdown from ATH | Close vs 200d SMA | Drop from 7-week high | Phase |
|---|---|---|---|---|---|
| 2022-06-18 20:00 | 17,622 | -74% | -52% | -56% | post-peak bear |
| 2022-11-21 21:00 | 15,476 | -78% | -29% | -28% | post-peak bear (late; the FTX flush was 9-10 Nov, this is the slow retest low) |
| 2024-08-05 06:00 | 49,000 | -34% | -12% | -30% | bull correction (yen unwind) |
| 2025-04-07 07:00 | 74,508 | -32% | -9% | -25% | bull correction (tariff shock) |
| 2026-02-06 00:00 | 60,000 | -52% | -31% | -39% | post-peak bear |
| 2026-07-01 01:00 | 57,800 | -54% | -20% | -30% | post-peak bear (lowest low in the data) |

Mix: 4 post-peak bear, 2 bull corrections, 0 base. "Base" is not represented, so nothing here says what large flow looks like in a long sideways base. The 2026-07-01 low is not in your list; I added it because it is the lowest price in the data and the retest question is relative to it.

## (b) Own measurement

Method: for each hour, summed buy and sell volume (by taker side) of single aggTrade prints at or above $1M, $5M and 50 BTC. Fixed-dollar thresholds mean more BTC in 2022 (a $1M print is 58 BTC at 17k, 14 BTC at 70k), so the 50 BTC version is the like-for-like one. Flow is shown as net buying (buy minus sell) in bp of all volume in the block; buy share is buy / (buy + sell) of large prints. Blocks are relative to the low hour. Binance spot + futures combined.

Net large buying, trades >= 50 BTC, bp of all volume (negative = large sellers dominate):

| Low | -96..-48h | -48..-24h | -24..0h | 0..+24h | +24..+48h | +48..+96h |
|---|---|---|---|---|---|---|
| 2022-06-18 | +9 | -6 | -66 | +60 | +30 | +20 |
| 2022-11-21 | +1 | -8 | -39 | -11 | +52 | +10 |
| 2024-08-05 | -85 | +2 | -36 | +14 | +96 | +39 |
| 2025-04-07 | +14 | -29 | -28 | +11 | -24 | -2 |
| 2026-02-06 | -1 | -58 | -46 | +32 | +70 | +43 |
| 2026-07-01 | +17 | -1 | -203 | +272 | -164 | +97 |

Buy share of >= $1M volume, %:

| Low | -96..-48h | -48..-24h | -24..0h | 0..+24h | +24..+48h | +48..+96h |
|---|---|---|---|---|---|---|
| 2022-06-18 | 52.2 | 48.9 | 40.9 | 61.6 | 57.7 | 54.5 |
| 2022-11-21 | 50.0 | 47.1 | 36.2 | 44.1 | 66.4 | 50.6 |
| 2024-08-05 | 39.9 | 47.8 | 42.9 | 51.9 | 63.2 | 58.7 |
| 2025-04-07 | 49.7 | 45.2 | 42.5 | 51.8 | 46.5 | 48.9 |
| 2026-02-06 | 47.5 | 41.0 | 44.4 | 54.8 | 52.6 | 56.3 |
| 2026-07-01 | 50.4 | 46.2 | 31.0 | 66.3 | 40.7 | 59.8 |

Did large buyers step in before, at or after the low?

| Question | Answer (6 lows) |
|---|---|
| Before the low (-24..0h): buy share below 50%? | 6 of 6 (31% to 44%). Large sellers lead into every low. |
| Before, -96..-48h: any early large buying? | No pattern: net flow -85 to +17 bp, mixed sign. |
| At/just after the low (0..+24h): buy share above 50%? | 5 of 6 (52% to 66%); the exception is 2022-11 (44%), a quiet drift low. |
| Second day after (+24..+48h): buyers still dominant? | 4 of 6; 2025-04 and 2026-07 flipped back to sellers. |
| Share of >= $5M prints (Binance, buy/sell count) in -24..0h vs 0..+24h | 2022-06 1/3 then 7/1; 2024 18/31 then 30/25; 2025 41/52 then 60/48; 2026-02 53/85 then 82/62; 2026-07 6/19 then 39/10. Sellers outnumber before, buyers equal or outnumber after. |

Large flow follows price rather than leading it. Over 67 non-overlapping days in these windows: correlation of 24 h large net flow with the PRIOR 24 h return is +0.45 (>= $1M) / +0.31 (>= 50 BTC); with the NEXT 24 h return it is +0.05 / +0.08. Days in the bottom fifth of flow went up the next day 64% / 57% of the time vs 46% for all days, n = 14, and the windows are built around lows so this is selection-biased: do not read it as an edge.

Big prints are a thin slice. Share of all volume in single prints at or above $1M: Binance spot 0.50%, Binance futures 6.6%, Bybit 1.2%; at or above $5M: 0.04% / 1.6% / 0.11%. This is the numeric version of "big trades are not sufficient on Binance": algos and icebergs slice large orders into small prints, so a print-size filter sees only a few percent of the flow, mostly in futures. Coinbase has no free historical trade archive, so for Coinbase I could only use price (premium), not large-trade flow.

Coinbase minus Binance premium (bp of price, hourly close; includes the USDT/USD basis, so read the change, not the level):

| Low | -48..-24h | -24..0h | At low hour | 0..+24h | +48..+96h |
|---|---|---|---|---|---|
| 2022-06-18 | -13.4 | -14.8 | -16.9 | -14.3 | -10.5 |
| 2022-11-21 | -12.2 | -16.4 | -10.7 | -12.5 | -7.9 |
| 2024-08-05 | -6.6 | -4.5 | +0.7 | +3.8 | +3.4 |
| 2025-04-07 | -3.5 | -6.0 | -11.5 | -4.8 | -5.2 |
| 2026-02-06 | -17.3 | -20.5 | -17.2 | -9.8 | -7.4 |
| 2026-07-01 | -16.6 | -17.5 | -17.3 | -13.0 | -10.3 |

The premium is at its most negative around the low in 5 of 6 (2024-08 is the exception) and is less negative over the next 1 to 4 days in all 6, barely so in 2025-04.

## BTC now (descriptive, no advice)

| Item | State |
|---|---|
| Price | Low of the move 67,568 at 2026-11-13 05:45 UTC (5-6% above the 2026-07-01 low of 57,800; 200-week SMA about 68,000 per your read); last 15m close in data 68,942 |
| Large flow, Binance spot + futures, 24 h to 2026-11-12 end (the last published dump day) | Net -87 bp at >= $1M (14th percentile of all history hours in the windows; the 6 lows' median in the 24 h before the low is -81 bp); buy share 42.6% (pre-low blocks above were 31% to 44%). At >= 50 BTC: 24 h -15 bp vs the lows' median -47 (all 6 lows were more negative); 72 h +16 vs lows' median -36. So large-print selling is milder than at any of the six lows at that size. |
| Drop day 2026-11-13 (spot only, pulled by REST because the daily dump is not published yet; futures and Bybit not available) | 24 h taker imbalance to the low hour -611 bp of volume, versus the 6 lows -131 to -1,044 (4 of 6 lows were more extreme); 24 h spot volume $2.0B vs $1.3B to $8.1B at the lows (5 of 6 lows had more); 7M of >= $1M spot sells and zero buys all day |
| Coinbase premium | About -10 to -11 bp on 13 Nov (hour of the low -11.4), vs about -17 at 3 of the 6 lows and -11 at two; it was -23 on 30 Oct and has improved while price made lower lows |
| 3-week picture | Daily net >= $1M flow flips sign constantly (-146 to +98 bp), 17 of 20 days under 55% buy share, no day with a clear large-buyer takeover. |

Reading it against the six lows: today looks like the pre-low blocks (sellers dominate large prints, premium negative but less than at deep lows), and not like the first 24 h after a low (buy share above 52%, premium recovering fast). The 11-13 spot flush was lower-volume and less one-sided than most past lows. Neither a retest nor a double bottom is confirmed or ruled out by this; the measured signature of a low in these 6 events is "sellers dominate, then buy share crosses 50% within 24 h and premium rises".

## Untested leads for the edge hunt (not rules, no outcomes looked at)

1. After-low confirmation: buy share of >= 50 BTC volume above 52% over 24 h after a drop of 25%+ from the 7-week high, premium rising over the same 24 h. Cost: it triggers about 1 day after the low.
2. Futures-versus-spot split of large flow (futures carries almost all of it): do the 2 bull-correction lows differ from the 4 bear lows?
3. 11-13 gap: rerun after the dumps publish (command below) and check whether futures show the large buying spot did not.
4. Needs more lows (n = 6 is too few): add 2018 and 2020 from repo csvs for price/premium proxies only; large-print data does not exist for that period in the cache.

Rerun for the missing days: `python fetch_hourly.py` (skips existing files; day 2026-11-13 fut/bybit/spot dumps 404 on 2026-11-14), then `python analyze.py` after setting the date range end to 2026-11-13.

## Limits

- n = 6; 2022-11 low was quiet so $5M counts there are near zero (price 16k).
- Taker side comes from the aggressor flag; Binance aggTrades merge fills of one order at one price, Bybit rows are single fills (hence fewer large prints there).
- Premium uses USDT as the Binance leg.
- Windows are 9 days around each low, so the "before" blocks are mechanically sell-heavy because price was falling into the low; the finding is only that large prints join the selling and then flip, not that the flip is predictive.
- Last published dump day is 2026-11-12; 11-13 is spot-only.
