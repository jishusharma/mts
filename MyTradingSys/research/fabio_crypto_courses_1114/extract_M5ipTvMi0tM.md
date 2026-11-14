# Extract: Deep Charts, "Orderflow will be 10x simpler with THIS strategy" (`M5ipTvMi0tM`)

- **Video ID:** `M5ipTvMi0tM`
- **Speaker:** DeepCharts presenter (not named in the caption; teaches Fabio Valentini's "IVB" model, an initial-balance / opening-range volatility breakout)
- **Market in the video:** CME Nasdaq futures (NQ), 30-minute opening range from the US cash open, 5-minute chart with a 1-minute chart for triggers; no crypto. Concepts transfer, session clocks and contract-size filters do not.
- **Source:** `raw_transcripts_canonical/M5ipTvMi0tM_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Not repeated here (same as finished extracts):** opening range with big-trade stop = `extract_KObUowoFiK0.md` K9; 10 percent delta initiative threshold = `extract_Ni6quY00dcw.md` C2 and `extract_uk2-7T1BW34.md` U3; imbalance cluster as a zone to trade on retest = K3 in `extract_KObUowoFiK0.md`; the 1:2 target in the sister video `extract_A5J4e5jbgVI.md`.
- **Caveat:** the video promises "real historical performance numbers behind it", but the only numbers shown are results from academic papers the speaker cites, not DeepCharts data (see V8).

## Rules

### V1. Opening range length: 15 or 30 minutes, 30 preferred (SOURCED)

Rule: the range is built from the first N minutes of the cash session: 15, 30, 45 or 60 minutes are all allowed; 15 and 30 are his favourites; he calls 30 "the best one statistically" (speaker claim, no data shown). Range = top and bottom of the opening period; the IVB indicator also plots the 50 percent middle line. For BTC there is no cash open: the session anchor is OURS and untested.

> "We can get the 15-minutes range or the 30-minutes range. You can also try it with the 45, with the 60-minutes, whatever you want. These is are my favorites and the best one statistically is the 30-minutes." [0:03:26]
**Source GPS: M5ipTvMi0tM | BEGIN**

> "You are going to get your top of the range and the bottom of the range and you're going to wait for a breakout either of the top or of the bottom." [0:03:51]
**Source GPS: M5ipTvMi0tM | BEGIN**

> "So, with this strategy, you are deleting all that noise of the beginning of the session and you are getting only the important part." [0:11:58]
**Source GPS: M5ipTvMi0tM | END**

### V2. Breakout validation: body closes outside the range, then initiative (SOURCED)

Rule: a breakout counts only if the candle BODY closes above (below) the range; a wick outside with a close back inside is not valid. Then validate initiative with at least one of: a strong candle, higher volume than the previous candle, delta above 10 percent, a big trade (filter of 60 contracts on NQ; BTC size OURS), or many footprint imbalances. Combination needed (how many of them): NOT stated.

> "To validate this initiative, you want, first of all, the body of the candle closing above the range or below the range." [0:04:15]
**Source GPS: M5ipTvMi0tM | BEGIN**

> "So seeing that this candle has more volume that the previous one and more than a 10% of delta, for example." [0:04:39]
**Source GPS: M5ipTvMi0tM | MIDDLE**

> "And you can validate the initiative maybe with normal volume or with a big trade or even with the footprint seeing a lot of imbalances, seeing a lot of delta." [0:04:28]
**Source GPS: M5ipTvMi0tM | BEGIN**

> "I like to put the 60 filter on them and let's wait for a breakout." [0:07:31]
**Source GPS: M5ipTvMi0tM | MIDDLE**

### V3. Three ways to enter the validated breakout, with stop and target (SOURCED)

Rule: (a) market entry on the closed 5-minute breakout candle, stop below that candle, target 1:1 or 1:2; (b) stop below the whole range, target 1:1; (c) wait for a retest of the IVB level / big-trade zone / imbalance cluster, enter on an order-flow trigger, stop below the test, target 1:1, 1:2 or the protection level. Stop is a candle low or range low (no tick buffer stated). Win rate / expectancy per option: NOT stated.

> "The first option is when you see your breakout with a 5-minute candle, you can enter market putting maybe your stop below the candle searching for a 1:1 or a 1:2." [0:04:53]
**Source GPS: M5ipTvMi0tM | MIDDLE**

> "The other thing that you can do is put your stop loss below all the range, maybe here, yes, searching for a 1:1." [0:05:02]
**Source GPS: M5ipTvMi0tM | MIDDLE**

> "wait for a test in the zone of the IVB or in the zone of the big trade or uh imbalance cluster and wait here for an order flow trigger to again engage the market" [0:05:12]
**Source GPS: M5ipTvMi0tM | MIDDLE**

> "with the stop below the test searching for a 1:1, a 1:2 or the protection level." [0:05:22]
**Source GPS: M5ipTvMi0tM | MIDDLE**

### V4. Order-flow trigger and scaling on the retest (SOURCED)

Rule: on the 1-minute chart, buyers stepping in and leaving a first rejection candle at the zone = trigger for the first contract, stop below the candle that made the breakout. A second smaller position is added on a later retest of the imbalance zone when buyers step in again, with the same stop below the breakout candle. Zone = footprint cluster where sellers were absorbed by big buyers at the breakout. Timeframe pairing: 5-minute for the breakout, 1-minute for the trigger. Position sizes: NOT stated ("one contract", "little contract").

> "In this case, we can also open our 1-minute time frame to see the triggers in a more precise way." [0:09:00]
**Source GPS: M5ipTvMi0tM | MIDDLE**

> "We are seeing a lot of buyers trying to step in and leaving this first rejection candle. So, maybe we can start loading here our first contract with the stop below the candle that made the breakout." [0:09:14]
**Source GPS: M5ipTvMi0tM | MIDDLE**

> "We can also wait for a test to this zone. We come back to the zone and we are seeing again some buyers stepping in." [0:09:56]
**Source GPS: M5ipTvMi0tM | END**

> "So, we can maybe engage with another little contract, putting again the stop loss below the candle that made the breakout." [0:10:04]
**Source GPS: M5ipTvMi0tM | END**

### V5. Exit management: protection level, partial, break-even, trail (SOURCED)

Rule: at the protection level take one contract off, move the stop to break-even, hold the rest toward the extended average. He does NOT usually hold for the extended average ("I've only seen the extended average a few times"); he enters with a small stop and aims at the protection level. A second example: when the protection level is hit, close or trail the stop below the big buyers (result 1:2). Target = stats from the indicator, not a fixed R multiple.

> "So, maybe here I will take one contract out and going to get out of the other one in the extended average." [0:10:16]
**Source GPS: M5ipTvMi0tM | END**

> "We are reaching the protection level. Now, I can put my stop to break even." [0:10:23]
**Source GPS: M5ipTvMi0tM | END**

> "I don't normally search for the extended average. I enter with little stop loss till the protection level, finding my zone and my trigger in a smaller time frame." [0:10:44]
**Source GPS: M5ipTvMi0tM | END**

> "To be clear and honest, I've only seen the extended average a few times." [0:11:04]
**Source GPS: M5ipTvMi0tM | END**

> "If I see this and I'm in the trade, I probably close the trade there or trail my stop loss below all these big buyers, getting a 1 to 2." [0:13:02]
**Source GPS: M5ipTvMi0tM | END**

### V6. Protection level and extended average: indicator outputs, formula NOT stated (SOURCED)

Rule: after the breakout the indicator prints the bias (direction of the breakout), a protection level, an extended average and an extended average plus standard deviation, and a "single breakout percentage of session" (share of sessions with only one breakout). The video never gives how they are computed; the sister video describes the exit average as "the average exit for this asset" (`extract_A5J4e5jbgVI.md` A3). For BTC these would have to be re-derived from our own breakout excursions (OURS, untested). Values: NOT stated.

> "And also we are start seeing here our protection level, our extended average, and our extended average with standard deviation." [0:07:57]
**Source GPS: M5ipTvMi0tM | MIDDLE**

> "And it says you also the single breakout percentage of session. So, what is the percentage of sessions that is making only one breakout?" [0:07:46]
**Source GPS: M5ipTvMi0tM | MIDDLE**

### V7. When NOT to enter at market: no volume increase, no delta, no big trade (SOURCED)

Rule: skip the market entry when the breakout candle shows no increasing volume, little delta and no big trade; some traders do trade the plain breakout, he does not recommend it. A breakout candle that returns inside the range is "not a trigger" and a pile of big trades with "no acceptance" does not count. Good example: 12 percent delta with two big trades in a big candle and no volume increase was accepted (so volume increase is not strictly required), entry at market, target "1 to 2.5" at the protection level.

> "In this case, we don't have an increasing volume, we don't have much delta, and we don't have either a huge big trade on the candle. So, maybe is not the best thing to do entering here market" [0:08:13]
**Source GPS: M5ipTvMi0tM | MIDDLE**

> "The candle went back again, so this is not a trigger. Again, sellers absorbed on the bottom and again a ton of big trades, but with no acceptance." [0:12:16]
**Source GPS: M5ipTvMi0tM | END**

> "Here we have our trigger. Two big trades in a big candle. We don't have increasing volume, but we have a 12% of delta, so it's good. I can enter market here." [0:12:30]
**Source GPS: M5ipTvMi0tM | END**

> "Searching for a 1 to 2.5 till the protection level." [0:12:43]
**Source GPS: M5ipTvMi0tM | END**

### V8. Volume filter claim from academic papers (SOURCED, speaker claim, no data shown)

Rule: speaker cites a peer-reviewed ORB paper (returns above zero, win rate better than random) and a study of 7,000 US stocks where a volume filter lifted returns from 3.2 percent to 41.6 percent a year. The video shows no data of its own; the numbers are the speaker's recollection of third-party papers. Our test: ORB with and without a volume/delta filter on BTC, OURS. No stop/target.

> "Without a volume filter, the strategy made 3.2% a year." [0:02:40]
**Source GPS: M5ipTvMi0tM | BEGIN**

> "they test opening range breakouts and found returns clearly above zero with a win rate better than random." [0:02:22]
**Source GPS: M5ipTvMi0tM | BEGIN**
