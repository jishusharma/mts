# Extract: deepcharts, "The Best Trading Indicator Ever? Full Guide Orderflow" (`gtg1Lt7jG2Y`)

- **Video ID:** `gtg1Lt7jG2Y`
- **Speaker:** Andrea Cimi on the deepcharts channel (Deep Trades = "big trades" bubble indicator, the tool Fabio Valentini uses; marketing and discount pitch skipped)
- **Market in the video:** CME index futures (ES, Nasdaq) on candle charts with big-trade bubbles built from aggregate trades; no crypto. Concepts transfer, contract sizes and session clocks do not.
- **Source:** `raw_transcripts_canonical/gtg1Lt7jG2Y_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Note:** no stop, target or numeric big-trade size is stated anywhere (the size threshold is picked by an automatic low/medium/strong filter from the last sessions, or by hand). All rules are discretionary reads of a bubble relative to wick, body and the next candle.

## Rules

### G1. Big trade = one aggregate trade with large volume; threshold is relative (SOURCED)

Rule: a big trade is a single aggregated trade (tape rows merged), not a count of raw prints, because big participants slice orders into ones. Use aggregate trades as input data. Threshold: NOT stated as a number; the platform derives it from the last few sessions (strong / medium / low filter), and he says to be more selective when volume is high and looser when volume is low. Computable: Binance aggTrades are already aggregated per price-time; threshold = OURS (for example a rolling percentile of trade size, untested).

> "What a big trade actually is is exactly a single trade that had a lot of volume inside." [0:03:39]
**Source GPS: gtg1Lt7jG2Y | BEGIN**

> "instead of using as input data volume, I can use aggregate trade." [0:03:21]
**Source GPS: gtg1Lt7jG2Y | BEGIN**

> "deep chart itself will calculate for you which one is likely the best range based on the last few sessions worth of data" [0:11:56]
**Source GPS: gtg1Lt7jG2Y | END**

### G2. Big trade absorbed in a wick at the extreme = reversal (SOURCED)

Rule: a big aggressive buy (sell) trade whose bubble sits inside the top (bottom) wick of the candle, i.e. price rejected it, is a reversal signal against the aggressor ("punch to the wall": effort with no follow-through). Big trades tend to occur at the start or end of important moves. No quantitative threshold; stop and target NOT stated.

> "When this happens at the top inside of the top wick, for example, this is a very good bearish signal." [0:03:56]
**Source GPS: gtg1Lt7jG2Y | BEGIN**

> "This is also what we call a punch to the wall. A big effort from buyer that finds a huge walls of sellers and then sellers taking control." [0:06:04]
**Source GPS: gtg1Lt7jG2Y | MIDDLE**

> "you're going to see that all of these big trades either happen at the beginning or at the end of very important movements" [0:04:27]
**Source GPS: gtg1Lt7jG2Y | BEGIN**

### G3. Big trade in the body, move continues = that side is in control (SOURCED)

Rule: a big trade bubble inside the body of a candle (not in a wick, not at the end of the move), with the candle continuing the move, means the big participant on that side controls the auction (a big green bubble in a big green candle: buyers dominate and price likely keeps rising for a short while or the session). A big trade in a trending move is likely one slice of a larger meta order. Duration claim ("short while or the entire session") is vague; stop and target NOT stated.

> "when you see a bubble that is inside of a movement, not at the end of a movement, not inside of the wicks, but in the bodies of the candle and the candle continuing that move, it means that this big seller is actually in control." [0:04:04]
**Source GPS: gtg1Lt7jG2Y | BEGIN**

> "When you see a big green bubble in a big green candle, it means that buyers are dominating the auction." [0:05:37]
**Source GPS: gtg1Lt7jG2Y | MIDDLE**

### G4. Opposite-side big trade inside a trend candle = absorption in continuation (SOURCED)

Rule: a big seller inside the body of a bullish candle, where price keeps going up anyway, means the selling effort was absorbed and the bullish state is likely to continue (mirror for a big buyer in a bearish candle, called absorption for continuation). Same logic as effort versus result. Stop and target NOT stated.

> "If you see a seller inside of the body of a bullish candle, it means there was an big effort from sellers that got absorbed because then price kept going higher even though there was a big effort from seller." [0:05:13]
**Source GPS: gtg1Lt7jG2Y | BEGIN**

> "that's likely to keep the auction in a bullish state" [0:05:31]
**Source GPS: gtg1Lt7jG2Y | MIDDLE**

### G5. The next candle decides: follow-through (SOURCED)

Rule: after an absorbed big trade, read the following candle: if it closes beyond the level with more aggression from the same side, that side is in control because its effort has follow-through in price; if not, the effort is absorbed. He calls this "a very crucial data point". Exact close condition and aggression threshold NOT stated.

> "What is the following candle doing? This is a very crucial data point." [0:09:49]
**Source GPS: gtg1Lt7jG2Y | MIDDLE**

> "the following candle closes below this with more aggressive seller and closes again. So sellers are clearly in control of this auction because all of this effort is having a follow through in price." [0:09:56]
**Source GPS: gtg1Lt7jG2Y | MIDDLE**

### G6. Big seller absorbed on a bottom wick at value area low = long (SOURCED)

Rule: a big seller bubble on a bottom wick (sellers absorbed by passive buyers) at a value area low or demand zone, followed by aggressive buying, means buyers are taking control. Value area comes from a cash-session volume profile (percentage NOT stated). Entry, stop, target NOT stated.

> "This is a seller on a bottom wick, which means that sellers got absorbed and these passive buyers really absorbed all of this pressure and exactly then at the value area low, that's exactly where they start responding." [0:09:15]
**Source GPS: gtg1Lt7jG2Y | MIDDLE**

> "he likely has found a wall of passive buyers that absorbed all of this pressure and instead started buying aggressively" [0:07:42]
**Source GPS: gtg1Lt7jG2Y | MIDDLE**

### G7. Zone drawn after the biggest big trades (SOURCED)

Rule: keep only the biggest big trades and extend a zone from each; price later retests the zone, where entries or exits can be evaluated. He admits it "doesn't happen very often". Zone width, hold time and trade parameters NOT stated.

> "you can enable the zone, apply the zone and you can maybe select the biggest only and this is going to give you a area right after the big trade has happened where you can for example evaluate your entries or your exits" [0:10:44]
**Source GPS: gtg1Lt7jG2Y | MIDDLE**

> "It doesn't happen very often, but it's a feature that I think is very cool and and shows you what's the main area of dominance." [0:11:11]
**Source GPS: gtg1Lt7jG2Y | END**
