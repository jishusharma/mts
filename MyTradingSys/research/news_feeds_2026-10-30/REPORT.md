# News for MTS: what to watch, where from, how fast (2026-10-30)

Operator ask (2026-10-30, voice): "what is missing from the dashboard is also news ... yesterday we saw the market
sell-off, and there was some Binance hack of $6 billion. So we never could catch it, not early, not late ... do a
proper research on this, especially for Bitcoin ... What are the things that we can scan every day? Keep scanning,
keep polling ... What are the feeds for this? What are the plugins for this ... how MTS can also be prepared."

Observation only. Nothing here gates or sizes a trade; news is context on the dashboard.

## 1. How many times this was asked

| Date | Where | What was asked | What happened |
|---|---|---|---|
| 2026-09-28 | items/T054 (verbatim) | "regular news that affect BTC", news sentiment, US pre-market | Filed OPEN. Plan step 4 = free RSS + CPI/FOMC/NFP calendar + event study. Never built |
| 2026-10-04 | T054 STATE | (session note) 08:30 ET volume peak = "macro-release hint for step 4 (news), untested" | Never tested |
| 2026-10-16 | context_factors_2026-10-16/CONTEXT_FACTORS_SPEC.md:157 | (session decision) | News DROPPED: "no DEV data, no timestamps" |
| 2026-10-30 | this ask | news module, global events, feeds, plugins | This report |

Two operator asks in 33 days, both unbuilt. The blocker each time was "no timestamped news data". That blocker is now
gone: section 4 shows a free, timestamped, scored feed reachable from this machine.

## 2. What happened on 2026-10-29 (the event we missed)

All times UTC. Price = Deribit BTC-PERPETUAL 5m bars (fetched this session). On-chain = cryptoticker.io timeline
citing Etherscan. Headlines = Tree News archive (`news.treeofalpha.com/api/news`, `time` field, fetched this session).

| UTC | Layer | Event | BTC (Deribit 5m) |
|---|---|---|---|
| 20:20 | on-chain | "Binance 14" hot wallet (0x28C6...1d60) delegated via EIP-7702 to an outside contract | 80,302 close |
| 20:24 | on-chain | ~167,464 ETH + 63 tokens leave in one transaction | 80,332 close |
| 20:30-20:35 | price | first leg: low 79,801 then 79,731; volume 208 / 265 vs ~40-70 the bars before | 79,830 close |
| **20:39:00** | **headline** | **Tree News: "POTENTIAL BINANCE HACK ONGOING - ONCHAIN" (importance 7.4)** | 79,830 (20:35 close) |
| 20:39:07 | headline | Aggr News: "BINANCE SEES UNEXPLAINED OUTFLOWS TO FRESHLY CREATED ADDRESSES, FUNDED BY TORNADO" (5.6) | |
| 20:41:17 | headline | Tree News: "TreeAI flagged a possible theft from Binance Hot Wallets ... over 60 tokens" (7.8) | |
| 20:40-20:45 | price | **main leg: low 78,727 then 78,199; volume 727 (about 10x the 20:20 bar)** | 78,901 close |
| 20:55:54 | headline | PeckShield: "unexpected large outflows from @binance hot wallets" (4.0) | |
| 21:05:25 | headline | The Block: "BREAKING: Binance hot wallets appear to have transferred billions" (7.6) | |
| 21:12:51 | RSS | CoinDesk article "Potential multi-billion Binance hack" (7.9) | 79,121 (21:10 close) |
| 21:15:23 | official | CZ on X: "It does look like a hack on Binance" | bounce to 79,717 high |
| 21:24:39 | RSS | Cointelegraph article | |
| 21:36:30 | RSS | Decrypt: "Binance Drained of $5.5 Billion" | |
| 00:00 (10-30) | price | night low 77,771 (CoinMarketCap, per cryptoticker) | |
| 02:30 (10-30) | official | Binance: total impact ~$6.3 billion | |

Read of the timeline (measured, one event):
- On-chain was first (20:24). The scored headline feed was 15 min later (20:39), but **before the main leg** (20:40-20:45, about -1,100 to -1,600 pts from the 20:35 close).
- Mainstream RSS (CoinDesk 21:12, Cointelegraph 21:24) arrived **after the low of the first hour**. An RSS-only news module would have been late, as the operator said.
- The official word (CZ 21:15) came 51 min after the drain, during the bounce.
- Our own feeds also moved: the 20:40 bar had about 10x normal volume, and Bybit/Deribit liquidations (wired 2026-10-29) would have shown the long flush. Press reported $607M of $628M liquidated in the first hour were longs (cryptoticker citing CoinGlass via PANews).

Context, not cause: the same day had a US stock sell-off (Bloomberg, CNBC: "as stock selloff also weighs"), the FOMC
on 10-28 and US GDP / Core PCE on 10-29 12:30 UTC (ForexFactory calendar, fetched this session).

## 3. What the literature says about news and BTC

| Event type | Finding | Source | Strength |
|---|---|---|---|
| Exchange hacks | BTC return about -1.4 % to -1.5 % on attack days (2012-2021) | Lee and Milunovich, Applied Economics Letters 32(12) 2025; related working paper | one author group, daily data |
| Exchange hacks | Bigger theft, bigger drop; recovery does not scale with size | Hu 2020 (FIU digital commons, 30 hacks) | small sample |
| Exchange hacks | Effect sits in the upper tail of volatility | Lyocsa et al. (quoted in quantpedia "What drives volatility of Bitcoin") | quantile regression |
| Exchange hacks | 44 breaches 2017-2025: no significant BTC price effect; markets more resilient | arXiv 2602.07046 | recent, contradicts the above |
| FOMC / CPI | Volatility spike lasts minutes to hours; matters for day traders, not longer horizons | Arcane Research via FXStreet (2022); KSE thesis 2025 (tables not read) | practitioner |

Take: the evidence is mixed on direction but consistent that big unscheduled events raise short-term volatility.
That supports news as a **volatility and context flag**, not as a direction signal. Any direction claim needs our own
event study (section 6, N5).

## 4. Feeds, tested from this machine (2026-10-30 ~08:00 UTC)

| Feed | What | Reached? | Cost | Speed (measured or sourced) |
|---|---|---|---|---|
| Tree News REST `news.treeofalpha.com/api/news?limit=N` | 1,000+ sources and 2,000+ X accounts, each item has `time`, `source`, `title`, `importance` (0-10), `suggestions` (coins) | **yes, 200**, CORS `*` (the dashboard can read it directly) | free; paid tiers remove delay | free REST items seen about 14.5 s after their `time` (3 samples, 5 s poll); hack headline 15 min after on-chain |
| Tree News websocket `wss://news.treeofalpha.com/ws` | same, pushed | not tested | free with delay; Sprout/Sapling paid ($500 / $2,500 a month per a Jan-2025 reseller page, unverified) | lowest |
| Tree News Telegram `t.me/TreeNewsFeed` | same headlines | (phone) | free | phone push |
| Ethereum public RPC `ethereum-rpc.publicnode.com` | live balance of exchange hot wallets | **yes** (latest only; history 403) | free, no key | 12 s blocks; would have seen the 20:24 drain |
| ForexFactory calendar `nfs.faireconomy.media/ff_calendar_thisweek.json` | this week's macro events with impact High/Medium/Low | **yes** (97 events; 429 when hit twice in a minute) | free | scheduled, known days ahead |
| The Block / Cointelegraph / Decrypt RSS | articles | **yes, 200** | free | 30-60 min late on 10-29 |
| CoinDesk RSS | articles | 308 redirect | free | 48 min late on 10-29 |
| alternative.me Fear and Greed | daily sentiment index | **yes** | free | daily |
| mempool.space | BTC fees / mempool | **yes** | free | live |
| CryptoPanic API | aggregator with votes | 404 without key | free key (5 req/s per its page) | not measured |
| Whale Alert API | large transfers incl. exchange flows | not tested | $29.95 a month Alerts plan, websocket, 7-day trial | not measured |
| GDELT, Polymarket, Binance announcements CMS | world news, event odds, listings | **blocked here** (timeout) | free | - |
| X API | the raw source of most headlines | not tested | pay-per-use, about $0.005 per post read (2026 guides, conflicting) | lowest, costly |

Claude connectors for chat use (from the MCP registry, none connected yet): CoinGecko (`get-crypto-news`),
CoinMarketCap (`get_crypto_latest_news`), MT Newswires (real-time financial news), CoinDesk (market data), FMP
(includes an economic calendar). These help a chat session read the news on request; they are not a 24/7 poller.

## 5. What to scan, and how often

Two kinds of news. Scheduled news is known in advance and goes on a calendar. Unscheduled news (hacks, ETF or SEC
surprises, exchange halts, wars) has to be polled.

| Kind | Examples | Feed | Poll | Dashboard shows |
|---|---|---|---|---|
| Scheduled macro | FOMC, CPI, NFP, PCE, GDP, BOJ/ECB | ForexFactory JSON | once a day + on page load | "next High event in 3h 20m: US CPI" strip |
| Scheduled crypto | options expiry (Deribit Friday 08:00 UTC), ETF flow print (Farside, US evening) | Deribit instruments; Farside page | daily | countdown, flows number |
| Unscheduled, scored | hacks, halts, ETF/SEC, big-player moves | Tree News REST | every 10-15 s while the page is open | headline list, high-score items marked, burst count |
| Unscheduled, on-chain | exchange hot-wallet drains, big stablecoin mints/freezes | public ETH RPC (balances of named wallets) | every block (12 s) to 60 s | "Binance 14 ETH -X % in 5 min" line |
| Market's own reaction | volume spike, liquidation flush, funding jump | already wired (Deribit, Bybit) | live | already on the page |

Noise check on the Tree archive (2,420 items, 10-26 to 10-30, measured):

| Day | Items | importance >= 7 | >= 7.5 | >= 8 |
|---|---|---|---|---|
| 10-26 | 471 | 5 | 1 | 0 |
| 10-27 | 492 | 7 | 0 | 0 |
| 10-28 | 492 | 9 | 1 | 0 |
| 10-29 (hack) | 724 | 42 | 25 | 7 |
| 10-30 (to 08:00) | 241 | 75 | 52 | 25 |

A normal day has 5-9 items at 7 or more; the hack day had 42. So "count of importance >= 7 in the last hour" is a
quiet line on normal days and a loud one on event days. One week of data only; the threshold is OURS.

## 6. MTS wiring plan

| Id | What | Parameters | Effort | Order |
|---|---|---|---|---|
| N1 | Headline panel in live_aid: Tree REST every 15 s, last 12 headlines (time, source, score, title), score >= 7 marked, BTC/macro words marked | poll 15 s OURS; mark at importance >= 7 OURS (5-9 a day measured); `importance` SOURCED (Tree) | small, page only | 1 |
| N2 | "News pulse" glance tile: high-score count last 60 min vs the 7-day normal; glance shows QUIET / BUSY / EVENT | 60 min window OURS; EVENT at >= 3 high-score items in 60 min OURS (normal day under 1 an hour) | small | 1 |
| N3 | Macro calendar strip: next High-impact USD event, countdown, last 3 results (actual vs forecast) | `impact` SOURCED (ForexFactory) | small; JSON needs a CORS check or a local copy | 2 |
| N4 | Exchange hot-wallet watch: ETH balance of named Binance/Bybit/OKX/Coinbase hot wallets via public RPC; line lights when one drops >= 20 % in 10 min | wallet list SOURCED (Etherscan labels); 20 % / 10 min OURS | medium; needs a vetted wallet list | 3 |
| N5 | News log + event study: keep every headline seen (time, score, source) in a local file outside the repo while the page or a manually started logger runs; after 4+ weeks test "EVENT pulse" vs next-hour BTC range | fee-free observation study; OOS split | medium | 4 |
| N6 | Words that matter (class tags): hack/exploit/drain, halt/suspend withdrawals, ETF/SEC, Fed/CPI, war/sanction, delist | word list OURS | small, inside N1 | 1 |

Rules: no scheduled tasks (SCHEDULING_POLICY.md). Polling runs only while the dashboard page is open or a logger
is started by hand. The news log is market data, not account data, but it stays outside the repo (size). Observation
only: the panel says what is happening, never what to do.

## 7. What the operator can use today, without code

| Tool | Why | Cost |
|---|---|---|
| Tree News site (news.treeofalpha.com) or Telegram @TreeNewsFeed | the feed that had the hack at 20:39, before the main leg | free |
| Lookonchain / PeckShield / ZachXBT on X | on-chain sleuths, often first on hacks (Lookonchain and PeckShield appear in the Tree archive above) | free |
| ForexFactory calendar | every scheduled macro event, with impact | free |
| CoinGlass liquidations page | shows the flush as it happens | free |
| Claude connectors: CoinGecko or CoinMarketCap news | ask a chat "what moved BTC in the last hour" | free account |

## Sources

- Deribit public API `get_tradingview_chart_data` BTC-PERPETUAL 5m, 2026-10-29 20:00-22:00 UTC (fetched 2026-10-30)
- Tree News archive `https://news.treeofalpha.com/api/news?limit=3000` (fetched 2026-10-30 ~08:00 UTC; 2,420 items)
- Tree News docs https://docs.treeofalpha.com/websockets
- Timeline: https://cryptoticker.io/en/crypto-crash-binance-hack-timeline-liquidations/
- https://fortune.com/2026/10/30/what-we-know-about-binance-hack-biggest-crypto-heist/
- https://www.coindesk.com/markets/2026/10/30/usd6-billion-binance-hack-sends-bitcoin-ether-tumbling-standard-chartered-sees-more-losses-ahead
- https://www.bloomberg.com/news/articles/2026-10-30/bitcoin-drops-on-binance-hack-as-stock-selloff-also-weighs
- https://www.cnbc.com/2026/10/30/bitcoin-ether-price-binance-security-scare-rattles-crypto-markets.html
- https://www.theblock.co/news/markets/2026-10-29-bitcoin-slides-below-77000-binance-hack-432183
- https://news.bitcoin.com/market-updates/binance-hack-sparks-1-5b-liquidation-bloodbath-across-crypto/
- ForexFactory JSON https://nfs.faireconomy.media/ff_calendar_thisweek.json (fetched 2026-10-30)
- Hack studies: https://econpapers.repec.org/RePEc:taf:apeclt:v:32:y:2025:i:12:p:1741-1745 ;
  https://digitalcommons.fiu.edu/srhreports/cybersecurity/cybersecurity/59 ; https://arxiv.org/html/2602.07046 ;
  https://quantpedia.com/what-drives-volatility-of-bitcoin/
- FOMC/CPI: https://kse.ua/wp-content/uploads/2026/05/illia-nazaruk_268722_assignsubmission_file_nazaruk_final_thesis.pdf ;
  https://www.fxstreet.com/cryptocurrencies/news/bitcoin-price-all-eyes-on-fomc-negative-inflation-could-slash-hopes-for-crypto-202209201630
- CryptoPanic API https://cryptopanic.com/developers/api/about ; Whale Alert https://developer.whale-alert.io/pricing.html
- Tree pricing (reseller page, unverified) https://web-5gv.pages.dev/resources/tree-of-alpha
- X API pricing https://www.wearefounders.uk/the-x-api-price-hike-a-blow-to-indie-hackers/
- Farside ETF flows https://farside.co.uk/?p=997
