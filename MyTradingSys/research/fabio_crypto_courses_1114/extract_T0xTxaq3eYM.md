# Extract: Andrea Cimi, "Orderflow Explained Stupid Simple" (`T0xTxaq3eYM`)

- **Video ID:** `T0xTxaq3eYM`
- **Speaker:** Andrea Cimi (DeepCharts co-founder); 9-minute explainer with a turkey-market metaphor and a short heat-map clip, published 2026-05-06
- **Market in the video:** CME futures heat map (DeepDOM, level 6800 mentioned on an index future); Bitcoin appears only as an analogy ("let's say this is the market of Bitcoin") and is not a statement that the tools support crypto. Mostly concept, little rule; ends in a DeepDOM sales pitch (skipped).
- **Source:** `raw_transcripts_canonical/T0xTxaq3eYM_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Not repeated here:** iceberg and absorption mechanics are in `extract_WPAP7JaVzF4.md` (I1 to I4) and `extract_2Mm_1wS40m0.md` (M6); this video adds the definitions and the liquidity-seeking idea only. No entry, stop or target rule is stated anywhere in this video (NOT stated).

## Rules

### E1. Aggressive = market takers, passive = market makers (SOURCED)

Rule: a trade is aggressive when the taker hits the resting order; the resting side is passive. Computable on BTC: yes (Binance aggTrades `isBuyerMaker` flag gives aggressor side). Same split as delta in `extract_Ni6quY00dcw.md` C1.

> "You have hungry buyers and sellers, also known as aggressive. We call these kids the market takers because they take the meat." [0:02:55]
**Source GPS: T0xTxaq3eYM | BEGIN**

> "And here you have passive liquidity or passive buyers and sellers, also known as market makers because they make the meat and provide it to the market." [0:03:06]
**Source GPS: T0xTxaq3eYM | MIDDLE**

### E2. Price moves with the count of hungry buyers versus sellers; a wick marks where the last liquidity was consumed (SOURCED)

Rule: the direction of price follows which aggressor side is larger at the time; after a burst of buying, one hungry seller drops price immediately and leaves a wick at the last consumed level. Computable: yes (delta per bar versus bar direction; wick versus last big-volume level). No threshold, entry, stop or target stated.

> "So price in financial markets moves up and down based on how many hungry sellers and hungry buyers are in the market at a certain point in time." [0:01:53]
**Source GPS: T0xTxaq3eYM | BEGIN**

> "And as soon as he takes that meat, price immediately drops and leaves a wick where it used to be, where the last piece of meat was eaten." [0:01:31]
**Source GPS: T0xTxaq3eYM | BEGIN**

### E3. Liquidity seeking: price gravitates to the big resting level, then reverses once the aggressors are full (SOURCED)

Rule: price tends to move toward the nearest large pool of resting orders; once the aggressors have eaten the liquidity on the way, the other side is likely to take control and move price toward the opposite pool; when price reaches a huge fresh wall of opposite liquidity, expect a reversal. Needs the order book (not in aggTrades): partly computable on BTC only through a proxy such as the prior high-volume node or a depth-snapshot feed (OURS, untested). Entry, stop and target: NOT stated; the heat-map clip uses the next liquidity level as the target.

> "whenever there's a big level with a lot of meat, price will tend to gravitate towards that level because big market participants are going to have way easier time to make business there." [0:04:23]
**Source GPS: T0xTxaq3eYM | MIDDLE**

> "So, if all of these customers are full and have eaten all of this liquidity, it's likely that buyers now will step in and move price up instead when there's sell meat." [0:02:23]
**Source GPS: T0xTxaq3eYM | BEGIN**

> "A huge level of sell liquidity just happened. And it's likely that buyers will get full by the time they get there. And that we'll see some form of reversal from price." [0:07:09]
**Source GPS: T0xTxaq3eYM | END**

### E4. Large orders are sliced into small pieces to fit the book (SOURCED)

Rule: a big participant (his analogy: a large fund buying Bitcoin) splits the order into smaller and smaller pieces so it fits what is available, which is why large flow shows up as many small prints rather than one print. Computable on BTC: partly (a sustained run of same-side small aggTrades at one price band is the footprint of slicing; no threshold stated, OURS to define).

> "they will fraction their buy hunger into multiple buy orders. And they will fraction their orders in smaller and smaller pieces so they can fit whatever is the meat available in the book." [0:03:41]
**Source GPS: T0xTxaq3eYM | MIDDLE**

### E5. Price action alone is late; executed-trade bubbles do not show resting liquidity (SOURCED, limitation)

Rule: price is only the end result of liquidity seeking, so a trader who reacts to the price chart is late; and footprint or big-trade bubbles show only trades already done, not where the resting orders were. For us this is a data limit: Binance aggTrades and klines show only executed trades (no resting orders), so any rule that needs where the resting liquidity sat (E3, iceberg detection from reloads) cannot be computed from them. A book feed is needed.

> "But price is only the end result of liquidity seeking. So, if you're only looking at price action, you're kind of always late to the party." [0:04:55]
**Source GPS: T0xTxaq3eYM | MIDDLE**

> "But these bubbles still only show you trades that just happened. Meat that was just eaten. They don't tell you where the meat actually was." [0:05:19]
**Source GPS: T0xTxaq3eYM | MIDDLE**

### E6. Heat-map use: time the entry and choose the target at the liquidity level (SOURCED, speaker claim)

Rule: he uses the liquidity heat map both to time entries (an attempt from sellers absorbed at a level, 3.7 thousand contracts shown in the clip) and to choose the target (a strong level, 6800 in the clip); resting orders at such levels are often pulled before they trade. No stop or exact entry stated; no performance numbers shown. Not computable from aggTrades (needs book heat map).

> "So, we had an attempt from sellers. They got absorbed here. You see 3.7 thousand contracts." [0:08:03]
**Source GPS: T0xTxaq3eYM | END**

> "Oh, we have a very strong level at 6800 that we're likely going to be taking. These orders typically don't get filled and they get removed constantly and they typically anticipate breakdown." [0:08:11]
**Source GPS: T0xTxaq3eYM | END**

> "And that's exactly how I used a liquidity heat map to not only time my trades, but to find the best targets where price could go towards." [0:08:22]
**Source GPS: T0xTxaq3eYM | END**

## Not computable (needs CME depth or MBO)

| Item | Why |
|---|---|
| Heat-map liquidity levels and "fresh liquidity" joining the book | needs book snapshots or MBO; Binance aggTrades and klines show executed trades only |
| Deep Trades bubbles | proprietary view; a size filter on aggTrades approximates it (see `extract_agjftXPkLUE.md` A14) |
