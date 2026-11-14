# Extract: deepcharts, "The Ultimate Guide to Orderflow Delta" (`uk2-7T1BW34`)

- **Video ID:** `uk2-7T1BW34`
- **Speaker:** Andrea Cimi on the deepcharts channel (published 2026-04-27; product pitches for the Deep Dom launch skipped)
- **Market in the video:** CME index futures (S&P 500 e-mini) on 1-minute footprint, CVD candles, delta profile and a big-delta filter; no crypto. Concepts transfer, session clocks and contract sizes do not.
- **Source:** `raw_transcripts_canonical/uk2-7T1BW34_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Note:** bar-level delta, delta percent, the 10 percent initiative bar, absorption divergence and exhaustion divergence are already in `extract_Ni6quY00dcw.md` (C1 to C4); this file adds only what is new (per-level delta, distribution of delta inside the bar, balanced band, delta by price, session reset, zigzag detector, big-delta filter). No stop or target is stated anywhere in this video.

## Rules

### U1. Delta per price level (SOURCED)

Rule: at one price level, total volume = aggressive buyers plus aggressive sellers, delta = aggressive buyers minus aggressive sellers (his example: 43 buyers, 71 sellers, volume 114, delta minus 28). Same sign as `Ni6quY00dcw` C1, now per level. Computable from aggTrades with price bins (bin size OURS).

> "aggressive buyers plus aggressive sellers gives total volume. Aggressive buyers minus aggressive sellers gives us the delta." [0:03:28]
**Source GPS: uk2-7T1BW34 | BEGIN**

> "a negative delta means that in that level there was more aggressive sellers than aggressive buyers" [0:03:37]
**Source GPS: uk2-7T1BW34 | BEGIN**

### U2. Delta clogged at one level = absorption; spread across the bar = initiative (SOURCED)

Rule: inside one bar, look at where per-level delta sits. Strong delta stuck at a single level (for example at the high of an up bar) means that aggressor was absorbed by passive orders on the other side and price reverses; strong delta spread across the body of a rising bar means buyers are in control (initiative). Strong delta alone is effort, not direction. Level thresholds ("dark colour") NOT stated; OURS: per-level delta share of bar volume.

> "if you see some delta, some very dark color all stuck at one single level, typically means that there was a very aggressive seller that was absorbed by a passive buyer." [0:05:27]
**Source GPS: uk2-7T1BW34 | BEGIN**

> "when we see delta clogged at one place, it typically means absorption. If we see it well distributed throughout a candlestick, it means that that participant is in control." [0:05:58]
**Source GPS: uk2-7T1BW34 | BEGIN**

> "strong delta doesn't mean a lot of directionality. It means a lot of effort in general." [0:05:50]
**Source GPS: uk2-7T1BW34 | BEGIN**

### U3. Delta percent: above 10 is initiative, 2 to 7 is balanced (SOURCED)

Rule: delta percent of a bar = how much one side is more aggressive than the other, as a percent of volume (formula in `Ni6quY00dcw` C1). Above 10 percent in absolute value = initiative auction (same threshold as `Ni6quY00dcw` C2); readings like 2, 4 and 7 percent = balanced auction. Between 7 and 10 not stated. Example bars in the video: minus 36 percent, 15 percent, 19 percent.

> "anything above 10% is typically considered an initiative type of auction. Anything below, so let's say for example, 2% delta, 4% delta, 7% delta. This all typically means that the auction is pretty much balanced." [0:08:30]
**Source GPS: uk2-7T1BW34 | MIDDLE**

### U4. CVD is rebuilt from per-bar delta and starts at zero each session (SOURCED)

Rule: cumulative volume delta as candles: each bar opens at the previous bar's close and closes at previous close plus the bar's delta; the series starts from zero at the new session start. Session start for BTC (for example 00:00 UTC) is OURS, untested. Caution: the worked example in the video steps the CVD by delta percent numbers (15, minus 4, minus 12) while an earlier line uses contracts (1.1k); use cumulative contracts (OURS reading, matches C1).

> "So this is exactly when the new session started. And as you can see we start exactly from zero." [0:09:09]
**Source GPS: uk2-7T1BW34 | MIDDLE**

> "every candle plots on a candlestick basis this data over here. And it creates what we call the cumulative volume delta, where it basically shows how the delta went through the entire session." [0:09:53]
**Source GPS: uk2-7T1BW34 | MIDDLE**

### U5. Short-term delta divergence: lower price high, higher delta high (SOURCED)

Rule: price makes a lower high while delta (CVD) makes a higher high: effort with no result on that leg, absorbed, reversal likely (mirror at lows). Same pattern as `Ni6quY00dcw` C3/C4; here stated with the reliability caveat. Swing definition, lookback, entry, stop, target NOT stated (OURS to define).

> "So, when you see price plotting a high and failing to plot another high, just like here, so this, but at the same time delta drifting higher, so you see price plotting a lower high and delta plotting a higher high, it typically means that on this leg of price over here, this effort didn't have any result and it's likely to be absorbed." [0:11:08]
**Source GPS: uk2-7T1BW34 | MIDDLE**

> "It doesn't happen, of course, at every single reversal, but you're going to see it happen very, very often." [0:11:33]
**Source GPS: uk2-7T1BW34 | MIDDLE**

### U6. Divergence detector: zigzag swings, used as confluence (SOURCED)

Rule: the platform marks divergences between delta (or volume and delta) and price on zigzag highs and lows; it clusters near important highs and lows and is a "great confluence" for reversals when used in the right areas, not a standalone trigger. Zigzag deviation and delta definition NOT stated.

> "This is basically going to use volume and Delta or Delta and use a zigzag mode, so the highs and the lows, to basically plot when there's a divergence in Delta." [0:13:44]
**Source GPS: uk2-7T1BW34 | END**

> "So, it's a great confluence when used in the right areas and situation to look for reversals." [0:14:01]
**Source GPS: uk2-7T1BW34 | END**

### U7. Delta profile: delta by price over a range (SOURCED)

Rule: over a chosen range (swing low to high), sum delta per price level (a delta profile next to the volume profile). A price zone with a lot of buying delta at a swing high that price then leaves is absorbed buying (and mirror for selling at a low). Zone thresholds NOT stated. Computable from aggTrades.

> "but this one is Delta by price." [0:14:45]
**Source GPS: uk2-7T1BW34 | END**

> "So, for example, I can see that there was a lot of buying effort here that got completely absorbed and price run back right after." [0:14:48]
**Source GPS: uk2-7T1BW34 | END**

### U8. Big-delta filter on aggregate trades: breakout continues, lows sit at peak sell delta (SOURCED)

Rule: filter bars by delta built from large aggregate trades only (the example ranges are 10, 20, 30 and up to 100 contracts, ES-specific; BTC size cut-offs are OURS, untested). During a breakout, many strongest-delta bars mean the breakout likely continues; main lows come where the highest sell-side delta appears. Entry, stop, target NOT stated.

> "I can select a range of 10 contracts for the first range, 20 contracts all the way down to 30 contracts or even, let's say, 100." [0:17:12]
**Source GPS: uk2-7T1BW34 | END**

> "if during a breakout, you see there's a lot of these light blue colors, it's likely that that breakout will continue." [0:18:24]
**Source GPS: uk2-7T1BW34 | END**

> "the times where there was the highest delta on the sell side is exactly where we plotted the main lows" [0:18:49]
**Source GPS: uk2-7T1BW34 | END**
