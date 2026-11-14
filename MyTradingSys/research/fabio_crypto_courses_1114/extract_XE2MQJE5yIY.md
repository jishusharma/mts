# Extract: Andrea Cimi, "Making 13.000$ in 4h Trading during the War" (`XE2MQJE5yIY`)

- **Video ID:** `XE2MQJE5yIY`
- **Speaker:** Andrea Cimi (live S&P 500 futures scalping on DeepCharts footprint, "same strategy of Fabio Valentini", April 2026, news-driven choppy session)
- **Market in the video:** CME S&P 500 futures (ES), footprint with big-trade bubbles, IVB (opening-range based daily bias tool), options gamma levels; no crypto. Contract counts and levels (6640, 6690, 6781) are ES points, not transferable.
- **Source:** `raw_transcripts_canonical/XE2MQJE5yIY_raw.txt` (caption via public transcript site, timed copy on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Trades taken (OURS summary):** about a dozen scalps, shorts and longs, 2 to 3 contracts, repeated stop-outs then reversals, stated results 4.2k, 6k, 7k, 10k, 12k, 13k on the day. The captions give price levels for a few stops only (6690 reverse stop, 6640 protection level, target 6700 flat, 6780s high); no per-trade stop/target table is stated and no risk-per-trade figure is stated.

## Rules

### E1. Daily directional bias from opening range, trade the bias side with more tolerance (SOURCED)

Rule: the daily bias comes from an opening-range breakout (here short, because the opening range broke out several times) confirmed by the IVB signal; with the bias he accepts more stop-outs on that side. IVB is a DeepCharts tool, formula NOT stated (OURS: unknown, approximated by opening range only).

> "So, I overall have a daily short bias because of the opening range that has broken out multiple times." [0:01:54]
**Source GPS: XE2MQJE5yIY | BEGIN**

> "Like on shorts, I'm a little more confident because the overall bias is short and the IVB is giving us a sell signal." [0:04:23]
**Source GPS: XE2MQJE5yIY | BEGIN**

> "So I'm willing to take a little more losses on the on on here because we have we have, you know, more stats on our side." [0:04:33]
**Source GPS: XE2MQJE5yIY | MIDDLE**

### E2. Mean-reversion entry at an options level (implied move edge) (SOURCED)

Rule: mean-reversion trades are taken at the implied-move low next to a cluster of long-gamma exposure (put wall); stop trailed as soon as momentum starts. Needs options market-maker gamma and implied move data (not in Binance aggTrades or klines; Deribit options would be a separate source). Stop/target NOT stated.

> "Currently trying one more mean reversion setup right on the implied move low close to the cluster of long gamma exposure and I'm going to trail the stop as soon as possible as soon as the momentum kicks." [0:03:07]
**Source GPS: XE2MQJE5yIY | BEGIN**

### E3. Trigger: aggressive buyers on top as a big bubble, sellers absorbing, invalidation at that level (SOURCED)

Rule: after entering a mean-reversion short, the confirming picture is aggressive buyers at the top shown as a big bubble that sellers absorb; the absorbed level is the invalidation point and the trade exits at break even if price breaks it; while the auction keeps moving in favour the stop is trailed. Bubble size is not given here.

> "Get aggressive buyers on the top. We got a big bubble right here where I would expect it. You got sellers absorbing. I mean, this is my invalidation point." [0:03:17]
**Source GPS: XE2MQJE5yIY | BEGIN**

> "So, if it breaks it, I'm out at break even." [0:03:26]
**Source GPS: XE2MQJE5yIY | BEGIN**

### E4. Trail the stop beyond the last candle or the big trade (SOURCED)

Rule: once momentum shows, the stop is trailed just beyond the low (for longs) or high (for shorts) of the last candle or wick, or beyond the big trade (large single print) that the move started from; he also says to leave some room when participation below is low.

> "We can now trail the stop below this candlestick, below the big trade." [0:00:26]
**Source GPS: XE2MQJE5yIY | BEGIN**

> "Okay, we can trail the stop below the last wick." [0:08:40]
**Source GPS: XE2MQJE5yIY | MIDDLE**

> "Actually, the big trade is okay as as a trail." [0:13:34]
**Source GPS: XE2MQJE5yIY | END**

### E5. Reverse when the rejection fails: stop beyond the aggression (SOURCED)

Rule: if the candle does not reject, he flips direction; the stop for the reverse sits just beyond the aggression that triggered it. If the absorbed side wick is taken out he is out. Candle timeframe for rejection not stated.

> "If this candle doesn't reject, I'm ready to reverse." [0:05:32]
**Source GPS: XE2MQJE5yIY | MIDDLE**

> "Reverse, stop at 6690, below the aggression." [0:05:02]
**Source GPS: XE2MQJE5yIY | MIDDLE**

> "we got aggressive buyers absorbed and sellers taking control. If they take this wick out, I'm officially out." [0:08:47]
**Source GPS: XE2MQJE5yIY | MIDDLE**

### E6. Entry with a very tight stop, wait for aggression to build, do not trust a 5-minute candle (SOURCED)

Rule: long entries use a very tight stop below the signal candle and require buyers to get more aggressive; if stopped, he loads again once and otherwise waits for deeper confirmation. He says he does not trust a 5-minute candle (lower-timeframe footprint preferred). Stop size in ticks NOT stated.

> "I don't trust a 5-minute candle." [0:07:52]
**Source GPS: XE2MQJE5yIY | MIDDLE**

> "I'm going to start the first position here. Very tight stop like before. Selling stop below this candle. I want to see buyers getting more aggressive." [0:08:03]
**Source GPS: XE2MQJE5yIY | MIDDLE**

> "Loading one more. Last one here, otherwise I'm going to wait for a deeper confirmation." [0:08:21]
**Source GPS: XE2MQJE5yIY | MIDDLE**

### E7. Scale in with small size and add on convincing inertia; break even early (SOURCED)

Rule: start with two contracts and a tight stop, add one more contract only if selling inertia is convincing; stop goes to break even or slightly better as soon as possible; position building is repeated through the session.

> "Going to engage with two contracts. My stop is very tight and I eventually add more, maybe add one contract more if I see some convincing selling inertia." [0:09:34]
**Source GPS: XE2MQJE5yIY | MIDDLE**

> "We can already place our stop to break even, maybe a slightly less than break even." [0:09:47]
**Source GPS: XE2MQJE5yIY | MIDDLE**

### E8. Absorbed volume at a level, then who keeps pushing wins (SOURCED)

Rule: large contract counts absorbed at one level (about 1,100 at a single price, 2,300 and still buying) are read as absorption; if the absorbed side keeps pushing and price follows through, it is an auction in that direction and he holds; if the aggressor is absorbed and the other side takes control, he exits and prepares the reverse. A "momentum ignition" is when absorbed buyers are broken and price runs on.

> "1.1 thousand contracts all absorbed at one single level." [0:12:48]
**Source GPS: XE2MQJE5yIY | END**

> "These absorbed buyers are going to be probably broken right now. There you go. This is not over." [0:09:04]
**Source GPS: XE2MQJE5yIY | MIDDLE**

> "2.3 thousand contracts absorbed and still buying." [0:14:07]
**Source GPS: XE2MQJE5yIY | END**

### E9. Wait for a clear winner, otherwise flat or reverse (SOURCED)

Rule: in the first long of a sequence, a candle closing above a stated level (6781) and a clear upside winner are required; without a clear winner he flattens and may reverse.

> "I want to see a clear winner on the upside. Otherwise, I'm I'm I'm going to flat and maybe reverse." [0:06:27]
**Source GPS: XE2MQJE5yIY | MIDDLE**

> "I want to see this candle close like this really bad. And ideally close above 6781." [0:05:52]
**Source GPS: XE2MQJE5yIY | MIDDLE**

### E10. Low participation below means a candle that eats back is not a threat (SOURCED)

Rule: a candle that fully retraces the prior candle is not a threat to the position if the volume below the current price is low (low participation); stop is placed leaving room because of that thin area.

> "I don't feel the threat even though this candle completely ate back this candle, it's not a threat because participation right below here is very low." [0:16:02]
**Source GPS: XE2MQJE5yIY | END**

### E11. Big aggression prints as break-even and target triggers; targets are structure highs/lows (SOURCED)

Rule: aggression measured in contracts (3,000 and 4,700 contracts quoted as strong) is used to justify going to break even or holding; targets are the session range edge or high ("target to 67 flat", "6780s and take this high"), exits are manual. Contract thresholds are index-futures size, BTC scale OURS.

> "3,000 contracts worth of aggression. Yes, sir. Break even already." [0:10:28]
**Source GPS: XE2MQJE5yIY | MIDDLE**

> "I want to be patient enough to let trades run until 6780s and take this high once more" [0:13:03]
**Source GPS: XE2MQJE5yIY | END**

### E12. News-driven choppy day: do not rely on news, stop for the day (SOURCED, what NOT to do)

Rule: in a news-driven range without a breakout he adapts side and size and finally stops: relying on news to arrive "is not a strategy". Daily profit target or loss limit NOT stated.

> "This was all news driven so either I'm relying on a news to come out of nowhere. That's not a strategy, bro." [0:17:06]
**Source GPS: XE2MQJE5yIY | END**

> "They're just trapping traders that don't adapt." [0:15:49]
**Source GPS: XE2MQJE5yIY | END**
