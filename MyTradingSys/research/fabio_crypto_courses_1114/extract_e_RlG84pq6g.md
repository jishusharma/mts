# Extract: Andrea Cimi, "The Only Trading STRATEGY you'll EVER need" (`e_RlG84pq6g`)

- **Video ID:** `e_RlG84pq6g`
- **Speaker:** Andrea Cimi (DeepCharts co-founder, Fabio Valentini's partner); the "PBD method" (P, B and D shapes of volume distribution)
- **Market in the video:** CME index futures and stocks (daily, 5-minute and 1-minute charts, DeepCharts footprint); no crypto. Concepts transfer, session clocks (cash open, 15-minute opening range) do not.
- **Source:** `raw_transcripts_canonical/e_RlG84pq6g_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Overall data status:** no win-rate count, sample size or R statistic is shown anywhere; every "high win rate" below is a speaker claim, no data shown. The walk-through examples are in hindsight and the speaker says so.

## Rules

### E1. Market phases and the range definition (SOURCED)

Rule: price alternates between balance (a range, fair value, lots of volume, a distribution) and imbalance (one side pushing, low volume). A P or B shape is "impulse, pullback, small move again", i.e. a range after an impulse; D is a plain consolidation with no trend. Before a real imbalance there is usually a failed auction. Computable from klines plus aggTrades (range = value area of a window): partly (range detection is OURS: no exact algorithm given).

> "whenever you see that there's, let's say, big move up, a move down, small move up again, well, that's pretty much your range, and that's when you know this is your P." [0:24:55]
**Source GPS: e_RlG84pq6g | MIDDLE**

> "So, typically, before you see a clear situation of imbalance, you always have some form of failed auction, very, very often" [0:08:29]
**Source GPS: e_RlG84pq6g | BEGIN**

### E2. Value area = about 70 percent of volume; outside is an anomaly (SOURCED)

Rule: the range is a volume area holding at least 70 percent of the volume; price outside it is a statistical anomaly expected to return inside. Speaker's "edge" claim is that more of the next trading happens inside the 70 percent area than outside (speaker claim, no data shown; note it is close to a tautology, so the test must be the trade P and L, not the share of volume).

> "if you consider this to be a volume area where at least 70% of the volume is traded, statistically speaking, anything that happens outside of this area is considerable a statistical anomaly." [0:12:58]
**Source GPS: e_RlG84pq6g | BEGIN**

> "And this is a very high win rate setup because you have both the statistical anomaly that we're outside of the standard deviation" [0:25:45]
**Source GPS: e_RlG84pq6g | MIDDLE**

### E3. Setup 1, break-in (failed auction in trend direction) (SOURCED)

Rule: phase = P (uptrend range) or mirrored B (downtrend range). Wait for price to break out of the range against the trend and then back in. Entry: after a candle closes back inside the range, wait for a test, enter in trend direction. Target: the other side of the range. Stop: below the point of control, or more conservative below the entire area (long example; NOT stated whether the extreme of the failed break is used instead). Win rate: highest of the setups ("highest win rate, possibly"), speaker claim, no data shown. Computable (range, break, close-back-inside, test): yes.

> "That's an option, but the option with the highest win rate, possibly, and the highest risk to reward ratio is" [0:12:51]
**Source GPS: e_RlG84pq6g | BEGIN**

> "So, this is why the P, the first P setup is you wait for price to break out of a range and then to break back in. This is what Tom calls the break-in setup." [0:13:29]
**Source GPS: e_RlG84pq6g | BEGIN**

> "So, what you can do here is wait for a candle to close inside of the range, wait for a test, and buy to go to the other side." [0:13:57]
**Source GPS: e_RlG84pq6g | MIDDLE**

> "Ideally, your stop loss in this situation could be below the point of control, or if you want to be more conservative, you can put it below the entire area." [0:28:15]
**Source GPS: e_RlG84pq6g | MIDDLE**

### E4. Setup 2, breakout continuation with test (SOURCED)

Rule: phase = trend range. Entry: a candle breaks out of the range in trend direction with strength and initiative; do not take it if the breakout immediately drops back inside (that is the failed auction of E3). Filter: wait for a couple of candles to stay outside, or require the breakout candle to carry a lot of volume and initiative (checked with order flow). Then enter on the test. Stop: below the point of control. Target: 1:3 to 1:4 R quoted for the intraday example (also 1:1 used for the daily walk-through). Win rate: "very high", speaker claim, no data shown.

> "And whenever we see a candle breaking outside with strength and initiative, another idea is to trade the breakout." [0:14:33]
**Source GPS: e_RlG84pq6g | MIDDLE**

> "But not when the breakout, for example, immediately drops back inside, because that could be easily the same concept of failed auction" [0:14:40]
**Source GPS: e_RlG84pq6g | MIDDLE**

> "So, we want to maybe take some extra caution here and wait for maybe a couple of candles to stay outside and then join the party." [0:14:48]
**Source GPS: e_RlG84pq6g | MIDDLE**

> "Or we want this candle here to have like a lot of volume and a lot of initiative, which is something we can verify with order flow, as we'll see later." [0:14:54]
**Source GPS: e_RlG84pq6g | MIDDLE**

> "So, you either buy here, stop loss below the point of control, and up for a 1:3, 1:4 with a very high win rate." [0:34:27]
**Source GPS: e_RlG84pq6g | END**

### E5. Setup 3, counter-trend failed auction (reversal) (SOURCED)

Rule: in an uptrend range, if the upside breakout shows little buying (buyers weak, move exhausted) and then a big strong red candle closes back inside, short to the other side of the range. Lower win rate than E3 because it fades the trend (speaker claim, no data shown). Stop NOT stated explicitly for this setup (walk-through says a stop "above here" for conservative stops).

> "You see buyers getting a little weak, exhausting the movement, and then you see a big, strong, red candle that drops back inside." [0:15:20]
**Source GPS: e_RlG84pq6g | MIDDLE**

> "Maybe not as much as this type of failed auction, because again, we're going against the current trend, but this is still a valid short auction idea." [0:15:36]
**Source GPS: e_RlG84pq6g | MIDDLE**

### E6. Setup 4, trend reversal through the range (SOURCED)

Rule: a P forms, the breakout happens with a lot of volume, but instead of going up price breaks below the range with initiative; short it back to the beginning of the impulse. Described as the most reversal type of setup; stop NOT stated; win rate NOT stated.

> "more sellers take control of the auction and break below here with a lot of initiative and vengeance. And so, you want to short this all the way to the beginning of the impulse." [0:15:56]
**Source GPS: e_RlG84pq6g | MIDDLE**

### E7. B setups mirror the P setups; D setups in a consolidation (SOURCED)

Rule: B = the same four setups reversed after a downtrend impulse. D (no trend, consolidation): short every failed auction above, long every failed auction below, trade a breakout only with strength, volume and initiative. Simply buying or selling the bounce at the range edge is called the weaker option because levels get "dirty".

> "The B setups are basically the same, but opposite, right?" [0:16:08]
**Source GPS: e_RlG84pq6g | MIDDLE**

> "the first idea is to short every upwards failed auction and long every lower failed auction, and trade the breakouts only and only if there's strength volume initiative" [0:20:01]
**Source GPS: e_RlG84pq6g | MIDDLE**

> "I'm not saying it's not right, but a lot of the time they will get these levels dirty." [0:17:22]
**Source GPS: e_RlG84pq6g | MIDDLE**

### E8. Volume confirmation on break-in (SOURCED)

Rule: on the breakout side of a failed auction some buying pushes price out, then volume dries up; on the way back inside the range volume should rise. For a reversal setup: strength on the way out, weakness on the continuation, strength again on the way back. With this extra confirmation the speaker calls it a "very high win rate" trade (speaker claim, no data shown). Exact volume threshold NOT stated (OURS: e.g. compare bar volume to prior bars, untested). Computable from klines volume: yes.

> "You're going to see volume decreasing, decreasing, and on the way down, on the way back inside of the range on the P, you want to see volume increasing instead." [0:22:42]
**Source GPS: e_RlG84pq6g | MIDDLE**

> "And if you have these type of extra confirmation, then you're up to taking a very high win rate type of trade." [0:24:19]
**Source GPS: e_RlG84pq6g | MIDDLE**

### E9. Timeframe stack: daily for bias, 5-minute and 1-minute for entries (SOURCED)

Rule: build the bias on the daily chart (value area and trend of the volume ranges), take entries on the 5-minute or 1-minute chart in the bias direction. The speaker combines a D with a P on the daily chart as confirmation.

> "You can use it in the daily timeframe to spot long-term trading ideas or bias or to build actually your bias, or you can use them in the lower timeframe to look for your entries, such as in the 5-minute timeframe and the 1-minute timeframe." [0:19:34]
**Source GPS: e_RlG84pq6g | MIDDLE**

### E10. Walk-through results (hindsight, no counts) (SOURCED)

Rule: the daily chart examples use a 1:1 risk-to-reward "to be really, really pessimistic" with large stops, and the speaker states the outcome qualitatively; no list of trades, win count or sample size is given, and the speaker concedes hindsight. Treat as speaker claim, no data shown. The counter-trend break-back-inside entries are described as losers in part of the walk-through ("probably a stop loss").

> "And let's even say we have just a one-to-one risk-to-reward ratio to be really, really pessimistic about the performance of this approach with very large stop losses and stuff like that." [0:27:52]
**Source GPS: e_RlG84pq6g | MIDDLE**

> "So, for example, in this type of environment, we would have had a lot of profitable trades and very few losses. And we're just considering a 1:1 risk-to-reward ratio." [0:30:33]
**Source GPS: e_RlG84pq6g | END**

> "with the benefit of hindsight, everyone can be able just to tell, 'Hey, this is what happened, so I'm right.'" [0:35:25]
**Source GPS: e_RlG84pq6g | END**

### E11. Live example, long breakout of a two-day range (SOURCED)

Rule: after failed auctions at the range edge and a return to value, buy the break above the two-day range once the breakout candle closes with strong delta and a big trade on the breakout ("big trade" = footprint bubble; size threshold NOT stated). Target: the other side of the value area (highs). Stop: just back inside where aggressive sellers drop price back fast; exact level NOT stated. Optional: manage dynamically if sellers show strong conviction with rising volume.

> "So, breakout with a big trade means we're probably going to keep going up, and this is our setup for the day." [0:37:03]
**Source GPS: e_RlG84pq6g | END**

> "If we close this candle like this, we close this candle like this with a strong delta, and yes, we're ready. This is a qualified buy setup." [0:37:09]
**Source GPS: e_RlG84pq6g | END**

> "If they're too fast to drop back down, this is not a good sign, of course, but this would be a stop loss I'm I'm happy to take." [0:37:17]
**Source GPS: e_RlG84pq6g | END**

### E12. Live example, 15-minute opening-range short (SOURCED)

Rule: after a breakout that dropped back inside with volume, and buyers absorbed at the top near the previous value area, sell the break of the first 15-minute opening range (and of the B range and previous value area). Stop: slightly above the range. Target: at least the lower end of the value area. Entry refinement: sell momentum, or the more conservative option, sell on the imbalance if it fills (order-flow imbalance fill; exact definition NOT stated). Risk: the speaker mentions splitting daily risk over two trades (wording is garbled in the caption; risk per trade NOT reliably stated). Session clock is index-futures (OURS for BTC: untested).

> "We have the first 15-minute opening range, we sell the breakout, okay?" [0:40:23]
**Source GPS: e_RlG84pq6g | END**

> "We can place our stop loss slightly above here and ideally have a target at least on the lower end of this value area." [0:40:10]
**Source GPS: e_RlG84pq6g | END**

> "you either sell momentum here or, which is more conservative but better, is you sell on the imbalance if if it fills." [0:40:53]
**Source GPS: e_RlG84pq6g | END**
