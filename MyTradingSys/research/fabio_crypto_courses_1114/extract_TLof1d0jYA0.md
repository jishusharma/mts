# Extract: Andrea Cimi, "The trading Indicator Closest to a Cheatcode [MBO Icebergs]" (`TLof1d0jYA0`)

- **Video ID:** `TLof1d0jYA0`
- **Speaker:** Andrea Cimi (host, deepcharts channel, live session in the DeepDOM launch week, 43 minutes with chat Q&A), published 2026-05-14
- **Market in the video:** CME ES, NQ and GC (gold) on the DeepDOM heat map with MBO (market-by-order) data; no crypto traded. Crypto statements are collected in the last section. Skipped: the boot-camp, price, data-feed and platform Q&A (marketing).
- **Source:** `raw_transcripts_canonical/TLof1d0jYA0_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Not repeated here:** iceberg fade and iceberg break trades are `extract_WPAP7JaVzF4.md` I1 to I4; single-level iceberg absorption is `extract_2Mm_1wS40m0.md` M6 and S4 in `extract_kYX05qESJMs.md`. New here: the MBO definition, the high/low filter value (150 contracts on ES), reloads, fresh liquidity walls, pulled orders and the data requirement. No entry, stop or target rule is stated for icebergs (NOT stated); one demo trade is risk-sized in dollars with a stop placed first.

## Rules

### T1. What an iceberg is, and why only MBO data shows it (SOURCED)

Rule: an iceberg is a hidden large order that is shown to the book in tiny repeated pieces; a big executed print at a level where the visible book showed only a few dozen contracts reveals it. Only market-by-order data (order IDs) proves it is one order; the example is 166 contracts executed from one order ID, reloaded 2 contracts at a time, where only about 30 to 38 contracts were displayed. Binance aggTrades have no order IDs: the only proxy is executed volume at one price far above any displayed depth, which needs a depth feed (partly computable, OURS, untested; no threshold stated).

> "How is it possible that there is 166 over here? Well, that's what we call an iceberg." [0:15:34]
**Source GPS: TLof1d0jYA0 | MIDDLE**

> "there was a order with the same order ID, so the same big guy, that put 166 contracts one by one. In this case, two by two." [0:16:17]
**Source GPS: TLof1d0jYA0 | MIDDLE**

> "A big bubble appears, but there's no liquidity level." [0:15:07]
**Source GPS: TLof1d0jYA0 | MIDDLE**

### T2. Biggest icebergs mark highs and lows; filter at 150 contracts (SOURCED)

Rule: the largest icebergs appear at the tops and bottoms (absorption, then price reverses); filtering to icebergs of at least 150 contracts on ES removes noise and leaves only the ones that plot swing highs and lows. The 150 threshold is the speaker's own for ES, no study shown (OURS: scale to BTC volume and test). Computable on BTC from aggTrades: partly (large same-price executed volume at swing extremes; the order-ID reload count needs MBO). Entry, stop, target: NOT stated.

> "We had this huge absorption and then boom. And at the tops and the bottoms is where you see the biggest icebergs." [0:18:38]
**Source GPS: TLof1d0jYA0 | MIDDLE**

> "you can filter them and say hey, I want to see only those up above 150 contracts." [0:19:42]
**Source GPS: TLof1d0jYA0 | MIDDLE**

> "now you can see only the big ones that basically plot highs and lows inside of the marketplace." [0:20:00]
**Source GPS: TLof1d0jYA0 | MIDDLE**

### T3. Reload: a broken level is immediately re-offered (SOURCED)

Rule: a reload is a liquidity level that gets traded through and is immediately refilled by new passive orders close by; it can then be cancelled or held. Needs book data (not aggTrades). No entry or stop stated.

> "This is what we call a reload, right? This is basically a level that gets broken and immediately aggressive buyers putting uh or let's say passive buyers putting a very close order." [0:10:25]
**Source GPS: TLof1d0jYA0 | BEGIN**

### T4. Aggressors eat several liquidity levels, then a huge fresh wall appears and price reverses (SOURCED)

Rule: after sellers consume several buy-liquidity levels on the way down, a very large fresh wall of passive buy liquidity (thousands of contracts) marks likely exhaustion: eat all the liquidity, then reverse. Example: a move up of 58 ES points after the wall; after a big fall the sellers are "not hungry anymore" and buyers show up. Needs the book for the wall (no aggTrades equivalent); the exhaustion part (a steep fall, volume dying, absorption) is partly computable. Entry, stop, target: NOT stated.

> "Now we have a huge wall of meat. They might not be that hungry anymore. And also, there's more meat joining the party at once. We call this a reload. This is called fresh liquidity." [0:22:34]
**Source GPS: TLof1d0jYA0 | MIDDLE**

> "Is it clear for now? Eat all the liquidity and reverse. Well, from here the liquidity is so much there's they're even scared of getting there." [0:23:19]
**Source GPS: TLof1d0jYA0 | MIDDLE**

> "we had this move up for a total of 58 points. Okay? So, they provided more liquidity, build a huge wall, and then buyers take control." [0:23:43]
**Source GPS: TLof1d0jYA0 | MIDDLE**

> "So, if there's a big fall in price, they ate they're they're not hungry anymore. Buyers start start to show their teeth." [0:24:33]
**Source GPS: TLof1d0jYA0 | MIDDLE**

### T5. Liquidity is a magnet and the target; price rejects an area, then returns to hunt it (SOURCED)

Rule: resting-liquidity areas act as targets and as rejection points: price rejects an area moving up and later returns to hunt it down. Core claim: big participants need big counterparties, so price seeks liquidity. Needs book data; on aggTrades the nearest proxy is the high-volume node of the profile (partly, OURS, untested). Same idea as `extract_agjftXPkLUE.md` A6 for targets at the point of control.

> "The biggest concept you need to know is that price seeks liquidity. Because market big market participants need big counterparts. Hence, there is a structural behavior of liquidity seeking." [0:37:13]
**Source GPS: TLof1d0jYA0 | END**

> "Liquidity acts as a magnet, and we keep moving lower. So, all of these liquidity areas are typically used as targets and rejections." [0:24:51]
**Source GPS: TLof1d0jYA0 | MIDDLE**

> "You're going to see price moving up, rejecting these areas, and then hunting them down once more." [0:25:03]
**Source GPS: TLof1d0jYA0 | MIDDLE**

### T6. Pulled (deleted) liquidity and spoofing (SOURCED)

Rule: large orders that appear and are then deleted either end up filled through iceberg orders or are spoofing (placing huge orders near price and deleting them); he says spoofing no longer happens much in very liquid markets. Not computable from aggTrades (needs book changes). No trade rule stated.

> "So, these two were placed in the market and then deleted. Where do they end up? Either they buy or they place it with these icebergs." [0:26:19]
**Source GPS: TLof1d0jYA0 | MIDDLE**

> "So, basically spoofing is the opposite of an iceberg. They place orders very close, huge huge orders, and then they delete them." [0:34:40]
**Source GPS: TLof1d0jYA0 | END**

> "it's likely you're likely not going to see it uh because it doesn't happen anymore in very high liquid markets." [0:34:32]
**Source GPS: TLof1d0jYA0 | END**

### T7. Bubbles are footprint numbers; data tier is MBO or MBP, not level two or three (SOURCED)

Rule: a bubble on the DeepDOM chart is the same thing as a number in a footprint cell (executed volume at a price), so per-level footprint rules apply (computable on BTC from aggTrades: yes). For the book side he says think in MBO (order IDs) or MBP (price levels) only; Binance's depth stream is a price-level (MBP-type) feed, with no order IDs, so iceberg detection by ID is not possible there.

> "These are your footprints. Like a bubble is like a number in the footprint. It's exactly the same thing." [0:31:54]
**Source GPS: TLof1d0jYA0 | END**

> "don't think about level in terms of level two or level three. Just think in terms of MBO or MBP." [0:36:19]
**Source GPS: TLof1d0jYA0 | END**

### T8. Demo trade: stop placed first, risk in money, target at the liquidity level (SOURCED)

Rule: size is derived from a fixed money risk and the stop (risk 100, 500 or 5,000 dollars; "risk" sets the quantity), the stop is entered first, and the target is the liquidity level where the trade is aimed. Stop distance, grade and exact entry trigger: NOT stated (demo of the order panel on a replayed sim trade). Computable: sizing yes; the liquidity target needs the book.

> "I'm going to place a stop loss based on money $500 or $5,000. And on quantity, I'm going to put risk." [0:32:35]
**Source GPS: TLof1d0jYA0 | END**

> "I'm going to buy and nothing will happen until I place my stop first." [0:32:44]
**Source GPS: TLof1d0jYA0 | END**

> "And you can also see we open it here, target at the liquidity, boom, super easy." [0:37:49]
**Source GPS: TLof1d0jYA0 | END**

### T9. Daily VWAP as the institutional reference (SOURCED)

Rule: the daily VWAP (caption says "view app"), optionally with standard-deviation bands, is plotted as the institutional reference point beside the heat map. No trigger or stop stated. Computable on BTC: yes (VWAP with deviation bands from klines or aggTrades; daily anchor = UTC day, OURS).

> "Yeah. We got the view app here. Which is, you know, a very clear institutional reference point." [0:29:24]
**Source GPS: TLof1d0jYA0 | END**

## Not computable (needs CME MBO)

| Item | Why |
|---|---|
| Order IDs, iceberg reload size (the "two by two" parenthesis), pulled orders | MBO only; Binance has no order-level data |
| Heat-map liquidity walls and reloads | needs book snapshots; DeepDOM has no BTC feed (see below) |
| Contrast and colour filters, templates by Fabio and Carmine | platform settings, no rule |

## Crypto statements

Video published 2026-05-14 (DeepDOM launch week, Andrea Cimi). No crypto trading is shown; the statements below are all the video says about crypto or non-CME markets.

### K1. No aggregated crypto data in DeepDOM yet (SOURCED, 00:26:53)

Rule: not a trading rule. At 2026-05-14 DeepDOM (the MBO heat map) has no aggregated crypto data; so no DeepCharts or DeepDOM evidence about icebergs or heat maps exists for Bitcoin yet.

> "Does Deep Dom have crypto? Um it doesn't have aggregated crypto data yet." [0:26:53]
**Source GPS: TLof1d0jYA0 | MIDDLE**

### K2. Crypto planned in the next few months (SOURCED, 00:39:46)

Rule: not a trading rule. In answer to a question about aggregated Bitcoin data, the team says it is working on it and expects to add cryptos in the next few months (no firm date; caption is garbled around the question).

> "When Deep Dome will get aggregated data from Bitcoins from I We're working on it, guys. Next few months, inshallah, we're going to have um We're going to have cryptos as well." [0:39:46]
**Source GPS: TLof1d0jYA0 | END**

### K3. Iceberg and MBO analysis requires a centralized market (SOURCED, 00:26:38)

Rule: not a trading rule. A chat comment he confirms ("absolutely correct"): the approach needs a centralized market and FX is not one. Implication for BTC (OURS): a single exchange feed such as Binance is centralized for its own book but is one of many venues, which is likely why DeepDOM wants "aggregated" crypto data.

> "You need a centralized market. Some markets like FX are not. That's absolutely correct." [0:26:38]
**Source GPS: TLof1d0jYA0 | MIDDLE**
