# What Tom/Fabio say about order flow: what transfers to BTC, what does not

One page. Sources: the 10 verified extracts in `MyTradingSys/research/orderflow_extracts_1112/` (Tom Vorwald EN channel, Fabio/Serge guests; ledger analyst "unknown", see STATUS.md). Quotes are verbatim and pass `scripts/dev/verify_extract_quotes.py`. Operator decision 2026-11-12: take the order-flow IDEA only; BTC runs on its own clocks and flows. Test links point to `MyTradingSys/research/btc_orderflow_map_1112/PREREG.md` (frozen; nothing here changes it).

## Limits (OURS)
- Clocks: cash open, closing auction, settlement, first-5-minutes are index/stock-session clocks. BTC trades 24/7; its own clocks are funding 00/08/16Z and session tags (PREREG "Clocks").
- Instruments: their numbers (contract sizes, tick counts, "10x size") are index-futures figures. None is a BTC parameter.
- Data: footprint and delta rebuild from Binance aggTrades/klines; resting-order (L2 book) history is not in the public archive, so book-reading rules are NOT_IN_DATA.

## Transfers (idea only)

### T1. Absorption: heavy aggression that does not move price = a big passive side (SOURCED)
> "It means that there is a very large buyer here who is absorbing everything that's being sold. So, it's an absorption, a catching of all the sale orders."
**Source GPS: y67l86cSqb8 | MIDDLE**

BTC test: PREREG A2 (|delta5| in the top 2 % with the 5m bar moving < 0.1 %), trade against delta.

### T2. Extremes are per market, never a fixed number (SOURCED)
> "know which volume sizes are typical for each instrument."
**Source GPS: YkclL6xgu-s | END**

BTC test: PREREG uses trailing percentiles (A1 99.9th print size, A2 98th delta), not their numbers.

### T3. Flow only matters at a level (SOURCED)
> "Because if I also have a strong technical level here, then I know there was an exhaustion here, which means an extremum."
**Source GPS: y67l86cSqb8 | MIDDLE**

Not in PREREG (events fire anywhere). Next card: condition A2 on a prior-day high/low or value-area edge, as a new pre-registered family.

### T4. Forced seller: a big order chasing price is someone in trouble; do not fade it until it ends (SOURCED)
> "But in most cases like this, it's usually because someone has gotten into trouble and now needs to exit the market."
**Source GPS: DVZVE9rXGtU | MIDDLE**

> "there's just no point in going against it. You just have to wait until you can see that it's over."
**Source GPS: DVZVE9rXGtU | MIDDLE**

BTC proxy: large aggressor prints (PREREG A1, traded WITH the sign) and funding extremes (A3, against the payers). Liquidation history: no public feed (NOT_IN_DATA).

### T5. Trapped side must cover (SOURCED)
> "the probability that other market participants also have to flip their positions, or give up their short positions in that case, and thus have to buy is sometimes the best option."
**Source GPS: viT_VzF5Fsw | BEGIN**

BTC proxy: A3 funding extreme (crowded payers). Open interest drop after a run is a later OURS idea, untested.

### T6. Acceptance beats delta (SOURCED)
> "even though there was more of a selling surplus, the market accordingly accepted higher and higher prices. And when higher prices are accepted, what does that mean?"
**Source GPS: viT_VzF5Fsw | MIDDLE**

Same mechanism as T1 seen from the other side; covered by A2's sign rule.

### T7. Unfinished auction: size at a high/low means price comes back (SOURCED)
> "When there are high volumes at the tops or lows, the auctions are very often not yet finished, not yet completed."
**Source GPS: oa8kxSLLkAo | BEGIN**

Not in PREREG. Buildable from aggTrades (bid and ask volume in the top/bottom price bucket of a 15m or daily bar). Candidate card, new family.

### T8. Never trade a delta divergence alone (SOURCED)
> "Never combine such a divergence based solely on cumulative data divergence. You can always confirm it, for example, with footprints or the order book."
**Source GPS: rFPCtOcfUMI | END**

Agrees with our own result: price-vs-CVD divergence alone, 0 of 12 arms (orderflow_views_2026-10-14, cited in PREREG "Not repeated").

## Does not transfer (SOURCED, with the reason)

### N1. Closing-auction block orders: a cash-session clock; BTC has no closing auction (SOURCED)
> "you'll bring the remaining shares to the market during the closing auction because it's precisely in the closing auctions that you often find trading partners who want to buy or sell in large blocks."
**Source GPS: YkclL6xgu-s | MIDDLE**

### N2. Index trackers buying by weight: an index-product mechanic (SOURCED)
> "similar orders of similar size keep coming into the market because those guys don't put in a lot of effort. They just have to position it on the market."
**Source GPS: DVZVE9rXGtU | BEGIN**

### N3. Front running a resting order: works in crypto per the speaker, but needs L2 book history we do not hold (SOURCED)
> "in let's say in the crypto markets it still works very well, for example front running."
**Source GPS: 4P5WAxyPCis | BEGIN**

### N4. "70 % balance / 30 % trend" and "heavy money needs time": a stock/index figure, not measured on BTC by us (SOURCED)
> "the big heavy money needs time to position itself in the markets."
**Source GPS: VxN5IxTwpbE | MIDDLE**

## Net (OURS)
- Three of the eight transferable ideas are already in the frozen BTC map (A1, A2, A3). Two are not and are new families: T3 (flow at a level) and T7 (unfinished auction). They go in as new pre-registered cards after the map's RESULT, never as edits to its PREREG.
- Every number in their videos stays theirs; on BTC the threshold is a trailing percentile.
