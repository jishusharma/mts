# Extract: Andrea Cimi, "EXPOSING How Banks Hide their Trades" (`JR50FQIQN2A`)

- **Video ID:** `JR50FQIQN2A`
- **Speaker:** Andrea Cimi (DeepCharts co-founder; Deep Dome liquidity heat map with MBO iceberg tracker, CME Nasdaq/S&P futures replay)
- **Market in the video:** CME index futures; needs Level 2 market-by-order (MBO) data with order IDs, which Binance aggTrades/klines do not contain. Order-flow definitions transfer, iceberg detection does not (only crude proxies, OURS).
- **Source:** `raw_transcripts_canonical/JR50FQIQN2A_raw.txt` (caption via public transcript site, copied from F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Trade taken (replay demo, one trade):** long in an accumulation area on the session high-volume node with a test of the low-volume node; risk 5,000 sized from the stop; second add on the low-volume node test (not filled), add after a 1,000-contract iceberg; stop below the highest volume node; break even later; sell about half at deloading; exit at another big iceberg. No prices or R multiple are stated.

## Rules

### J1. Aggressive vs passive liquidity (SOURCED)

Rule: market takers (aggressive, shown as bubbles / executed trades) and market makers (passive resting orders) are the two sides of liquidity; footprint, profile and delta need only executed trades (Level 1), the heat map needs full depth. From aggTrades the aggressor side is computable (taker flag), resting liquidity is not.

> "So, you have one side of the liquidity, which is called aggressive, one side that's called passive. These are so-called market takers, these are the market makers." [0:03:08]
**Source GPS: JR50FQIQN2A | BEGIN**

> "for volume profiles, for footprint charts, for delta, and all this kind of stuff, level one is technically good enough." [0:16:00]
**Source GPS: JR50FQIQN2A | MIDDLE**

### J2. Meta-order slicing means bullish order flow persists (SOURCED)

Rule: large participants split a huge order into many small ones, so aggressive flow in one direction tends to be followed by more of the same (flow autocorrelation). No threshold or horizon is stated; testable as autocorrelation of signed aggTrades volume per time bucket (OURS design).

> "this is likely a small part of a huge meta order that they're planning to put in the market, right? And so, typically bullish order flow will lead to more bullish order flow, okay?" [0:11:13]
**Source GPS: JR50FQIQN2A | MIDDLE**

### J3. Price is attracted to large resting liquidity (SOURCED)

Rule: a large resting order (example 465 contracts, then a 795-contract single order) pulls price toward it; price runs up fast and eats the level. Needs order-book depth history, not available in aggTrades or klines (partly testable only if we record Binance depth snapshots, OURS).

> "market will be attracted by these areas and they will push price down and they will push price down and eat all of that liquidity." [0:11:47]
**Source GPS: JR50FQIQN2A | MIDDLE**

> "And as you can see, the the first thing that happened right after is that price pumps up incredibly fast and goes and eat that level of liquidity." [0:12:58]
**Source GPS: JR50FQIQN2A | MIDDLE**

### J4. Iceberg = many small prints with one order ID, refilled at the same level (SOURCED)

Rule: an iceberg shows a small visible size that is replenished every time it is hit; the proof is that all the small orders share the same order ID (MBO feed). A level-2 MBP feed cannot tell one big order from many small ones. Binance aggTrades has no order ID and no passive-side identity, so detection is NOT possible; a proxy would be many aggressive fills at one price with price not moving (OURS, unvalidated).

> "even though they look like multiple small orders, they all have the same order ID. So, thanks to MBO data feeds, we can see that these small orders of eight contracts have the same order ID, so they're likely part of one big order." [0:18:06]
**Source GPS: JR50FQIQN2A | MIDDLE**

> "every time one of these bubble pops up and eats that liquidity, a new fresh liquidity is presented." [0:13:49]
**Source GPS: JR50FQIQN2A | MIDDLE**

### J5. Filter to big icebergs only (SOURCED parameter, speaker's example)

Rule: keep only icebergs above a size filter (example 150 contracts) to remove small institutional orders; the filtered ones mark session extremes more often. The 150 is an example, not a tested threshold (OURS: untested; BTC scale unknown).

> "we can go on indicators, iceberg, and filter out only big icebergs. Let's say above 150 contracts." [0:21:26]
**Source GPS: JR50FQIQN2A | END**

### J6. Iceberg absorption marks highs and lows, but not every time (SOURCED)

Rule: a large participant absorbing the opposite side's aggression builds a wall and price reverses from that level (sell iceberg at the session high, buy iceberg at the low, 160 or 1,000 contracts in the examples); it does not plot the extreme every time (a buyer who keeps buying all the way down does not), so context filters are needed. No hit rate stated.

> "where these huge market participants absorb all of the market pressure of buyers, they build this wall of liquidity that buyers can't pierce through, price melts." [0:22:21]
**Source GPS: JR50FQIQN2A | END**

> "of course, they're not going to plot the high every single time." [0:23:18]
**Source GPS: JR50FQIQN2A | END**

### J7. Context for icebergs: value area edges, opening range, important highs, extended hours (SOURCED)

Rule: take icebergs only where they matter: at value area high/low or profile edges, in an opening range breakout context, right above an important high, and preferably in London or pre-market (extended hours) sessions; he advises to backtest it. Value area parameters NOT stated.

> "you might just want to take a look at things that happen only at the value area highs or at the edges of the profile and then you know it's right where I want to see it" [0:23:41]
**Source GPS: JR50FQIQN2A | END**

> "When this happens in the London session or in the, let's say, extended trading hours, that's where it has the most power." [0:25:39]
**Source GPS: JR50FQIQN2A | END**

> "So, I strongly advise you to do this to see if they happen, for example, at some specific areas of the volume profiles" [0:24:51]
**Source GPS: JR50FQIQN2A | END**

### J8. Replay trade: buy with the iceberg buyers above the high-volume node, risk-based sizing (SOURCED)

Rule: long in an accumulation area on the session high-volume node (value area low just below), with the stop below the low-volume node and below the whole high-volume node; size comes from a fixed money risk (5,000) chosen before placing the stop, a second add is planned on a test of the low-volume node; after a 1,000-contract iceberg in his direction he adds; stop to break even once buyers keep absorbing. Target NOT stated as a price.

> "So, for example, I want to risk in this position $5,000, let's say." [0:26:55]
**Source GPS: JR50FQIQN2A | END**

> "I can buy the exact quantity when I place my stop loss, for example, below this low volume node." [0:27:07]
**Source GPS: JR50FQIQN2A | END**

> "So, let's cover ourselves below the highest volume node here and look at that." [0:27:41]
**Source GPS: JR50FQIQN2A | END**

### J9. Scale out when the iceberg buyers deload, finish at the next big iceberg (SOURCED)

Rule: when sellers appear to deload (the hidden buyers stop adding) he halves the exposure with a market sell, keeps the remainder, and plans to take the final profit when another big iceberg appears; he notes he was early and could have reloaded.

> "So, we're going to half halving our exposure so we can sell market" [0:28:35]
**Source GPS: JR50FQIQN2A | END**

> "the other ones we can, you know, take the final profit when we see another big iceberg if there's any." [0:28:42]
**Source GPS: JR50FQIQN2A | END**
