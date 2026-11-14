# Extract: Andrea Cimi, "I Got Funded 150.000$ with This Strategy" (`kYX05qESJMs`)

- **Video ID:** `kYX05qESJMs`
- **Speaker:** Andrea Cimi (DeepCharts co-founder, Fabio Valentini's partner); personal prop-firm challenge diary on ES futures (stop run, iceberg, CVD divergence)
- **Market in the video:** CME ES futures, London session and New York open, DeepCharts footprint and order-book heat map; no crypto. Concepts transfer, contract counts and session clocks do not (volume thresholds must be rescaled to BTC).
- **Source:** `raw_transcripts_canonical/kYX05qESJMs_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Overall data status:** all trade results are shown as screenshots he narrates, the caption carries only his words; every win rate and profit factor below is a speaker claim, no data shown to us. The stop-run filters were fitted on the same hand-collected sample they were measured on (in-sample).

## Rules

### S1. Stop run (book sweep) fade, entry, stop, target (SOURCED)

Rule: phase = exhaustion at the end of an impulse, price sweeps above a prior high (or below a prior low) where stop orders sit. Order flow shows market orders clearing the book (book sweeping), then a short gap with little liquidity so the path of least resistance is back. Entry: on the close of the signal candle (volume spike versus the previous candle, large delta). Stop: slightly beyond the candle extreme. Target: the beginning of the stop run. It is a very short-term trade, not a session reversal. Computable from aggTrades/klines (volume spike, delta, sweep of a prior high/low): yes, except the order-book gap which needs depth data (partly).

> "And when price is reaching that level, there's going to be, as always, sell limits above here." [0:01:39]
**Source GPS: kYX05qESJMs | BEGIN**

> "So, the path of least resistance is this one. So, it's a very short-term trade. I'm not trying to look for a session reversal." [0:02:36]
**Source GPS: kYX05qESJMs | BEGIN**

> "I don't wait for a breakout and a test and go down for the whole session. That's not the point of the stop run." [0:02:57]
**Source GPS: kYX05qESJMs | BEGIN**

> "So, I want to see an increase in volume, a really high delta. Likely, this number should be at least 1/3 of this one. So, I want to have at least 1/3 clear aggression." [0:05:02]
**Source GPS: kYX05qESJMs | BEGIN**

> "And then I simply buy when this candle closes. My stop loss is slightly below here, and my target is the beginning of the stop run." [0:05:13]
**Source GPS: kYX05qESJMs | BEGIN**

### S2. Stop run filters: session, size, sweep of an important level, exhaustion only (SOURCED)

Rule: only London-session low-liquidity conditions (in New York there are absorptions, a different pattern); only an anomalous volume spike (his fitted threshold 1,300 ES contracts in the signal candle, which is ours to rescale for BTC); only before 7:00 a.m. New York time; best when the sweep takes out a very important high or low; never at the beginning of an impulse, only an exhaustion phase. Win rates after filters are in S3.

> "The stop runs I've traded only happen in the ES in the London session. It's a low liquidity pattern that specifically happens during the London session when there's low liquidity." [0:01:23]
**Source GPS: kYX05qESJMs | BEGIN**

> "And during these phases in the New York session, there's no stop run. There's actually absorptions, which are very different patterns that requires a very different trading style." [0:01:14]
**Source GPS: kYX05qESJMs | BEGIN**

> "So, I started putting a filter of all of the stop runs above 1,300 contracts." [0:07:10]
**Source GPS: kYX05qESJMs | BEGIN**

> "I also I I tried to just put a filter on, maybe let's take them before 7:00 a.m. New York time." [0:07:30]
**Source GPS: kYX05qESJMs | BEGIN**

> "because normally I don't trade beginning of impulses. I only trade an exhaustion phase." [0:10:13]
**Source GPS: kYX05qESJMs | MIDDLE**

> "I should have waited for the stop run that actually swept the high." [0:09:17]
**Source GPS: kYX05qESJMs | MIDDLE**

### S3. Stop run backtest numbers (SOURCED, speaker claim, no data shown, in-sample)

Rule: no rule, numbers only. Sample: about 349 trades collected by hand over roughly a year, three different take-profit types tried. Volume filter lifted win rate from 48-53 percent (depending on target) to 53-55 percent; adding the time filter improved it further (no number); stop runs that swept very important highs or lows reached 80 percent (sample size of that subset NOT stated); final fitted version 66 percent. All numbers are in-sample after fitting, so expect decay (OURS).

> "I gathered a huge amount of data, around 349 trades as a sample. We did this manually." [0:06:37]
**Source GPS: kYX05qESJMs | BEGIN**

> "Now, I started having a 53% win rate to 55% win rate." [0:07:20]
**Source GPS: kYX05qESJMs | BEGIN**

> "At the stop runs that specifically swept some very important highs or lows. And the results of these were absolutely phenomenal, 80% win rate." [0:07:48]
**Source GPS: kYX05qESJMs | BEGIN**

> "So, from this fitting phase, I had the final optimized version of the strategy that led me to this profit and loss, a win rate of 66%, which is decent." [0:07:55]
**Source GPS: kYX05qESJMs | BEGIN**

### S4. Iceberg fade on a single tick (SOURCED)

Rule: phase = low-liquidity London session. Trigger: price pushes into one price tick and order flow shows buyers absorbed on that single tick while someone keeps reloading (iceberg). Entry: sell one tick under the iceberg; scalp a couple of ticks, may repeat every bounce, take one to three trades then stop. Stop: one tick above the iceberg. Target: a couple of ticks (exact count NOT stated); a runner toward VWAP is mentioned in examples. Filter: size must be an anomaly for the session (2 to 3,000 contracts on one tick versus 200 to 300 contracts in an average London 1-minute candle); it does not work in the New York session where it gets run through. Expected end: momentum ignition through the level, hence the stop. A favourite variant: break a level, then trade the iceberg on the test. Evidence: "observed so many times", no backtest, speaker claim, no data shown. Computable: volume absorbed at one price tick is computable from aggTrades (yes); proof of reloading needs order-book data (partly).

> "And I want to see from order flow on this area buyers getting absorbed on a single tick. That means that in the book, there is someone who is constantly reloading and reloading and reloading contracts." [0:03:14]
**Source GPS: kYX05qESJMs | BEGIN**

> "I basically sell one tick under the iceberg and cover myself with a stop loss one tick above. And that's it, very simple strategy." [0:03:41]
**Source GPS: kYX05qESJMs | BEGIN**

> "So, if I see them from order flow, I'm going to sell to earn a couple ticks, front run this huge trader, maybe a couple times every time it bounces." [0:03:25]
**Source GPS: kYX05qESJMs | BEGIN**

> "a good iceberg could have, I don't know, two to 3,000 contracts on a single tick, and that is an anomaly in the London session." [0:03:58]
**Source GPS: kYX05qESJMs | BEGIN**

> "But in the New York session, icebergs like these are completely ran through like like a hot blade through butter." [0:04:16]
**Source GPS: kYX05qESJMs | BEGIN**

> "So, with this one, I've observed it so many times that I did not need a thorough backtest" [0:03:47]
**Source GPS: kYX05qESJMs | BEGIN**

> "So, my goal here is to take one, two, maybe three trades" [0:06:23]
**Source GPS: kYX05qESJMs | BEGIN**

### S5. CVD divergence plus absorption then initiative, session open (SOURCED)

Rule: phase = start of the New York session (the speaker also uses this elsewhere). Setup: price pushes to a new extreme but CVD/delta does not follow (not enough participation on that leg) and volume piles at the extreme of the candle (absorption), then wait for an initiative candle with high delta (example 7,000 contracts) and enter. Location filter: first or second standard deviation band of VWAP. Target: the other side of VWAP. Stop: beyond the last liquidation level or imbalance cluster, trailed below the previous low as the trade works. Win rate for this setup alone NOT stated (only in the pooled stats of S7). Computable from aggTrades (CVD, delta per bar, VWAP bands): yes.

> "This is the order flow divergence where I basically waited for an absorption phase at the bottoms where you can see a lot of volume being traded at the bottoms of the candle and then a phase of initiative and that's where I open my trade" [0:12:02]
**Source GPS: kYX05qESJMs | MIDDLE**

> "So, this is a CVD divergence where I can see that on this leg of price there was not enough participation, not enough delta compared to this one over here." [0:12:25]
**Source GPS: kYX05qESJMs | MIDDLE**

> "Normally here I wait for a clear initiative, so a candle with a high delta and there you have it." [0:12:38]
**Source GPS: kYX05qESJMs | MIDDLE**

> "We're also on the second standard deviation of the VWAP, which is normally where a lot of institutional trading goes on." [0:12:49]
**Source GPS: kYX05qESJMs | MIDDLE**

> "I set my take profit on the other side of the VWAP." [0:25:59]
**Source GPS: kYX05qESJMs | END**

> "This was my last liquidation level. This is an imbalance cluster. I said if this is going to be broken, I'd like to get out of this trade" [0:18:52]
**Source GPS: kYX05qESJMs | MIDDLE**

### S6. Trade management: scale out, break-even, runner to VWAP (SOURCED)

Rule: take most of the position off at the first target, move the stop to break even, optionally leave a small runner aiming at VWAP. Contract split NOT stated.

> "taking most of the profit out and maybe leaving some for the VWAP if you're feeling generous" [0:14:30]
**Source GPS: kYX05qESJMs | MIDDLE**

> "I moved my stop loss to break even as I often do" [0:16:20]
**Source GPS: kYX05qESJMs | MIDDLE**

### S7. Forward-test results and risk per trade (SOURCED, speaker claim, no data shown)

Rule: risk about 0.20 percent of the account per trade (prop-firm drawdown limits). First prop account after about 11 trading days: about 2,000 dollars profit, profit factor about 1.2, win rate 52 percent, slightly positive average R. Pooled over three accounts and more than 100 trades: profit factor 2.2, win rate about 50 percent, max drawdown 2.15 percent, gain 10 percent. Internal inconsistency: the spoken totals (34,000 wins, 50,000 losses) do not give profit factor 2.2 or a positive gain, so treat the pooled numbers as unreliable until the trade list is seen. Costs are material (he mentions about 95 dollars commission per trade on one broker). Setup split of these results NOT given.

> "So, I decided to only risk on average 0.20% of the account. Super conservative risk." [0:08:10]
**Source GPS: kYX05qESJMs | BEGIN**

> "It's probably a 1.2 profit factor with a 52% win rate and a slightly positive average risk to reward." [0:19:20]
**Source GPS: kYX05qESJMs | MIDDLE**

> "The total wins amounted to $34,000, $50,000 of losses for a profit factor of 2.2 with a positive risk to reward with around a 50% win rate, an average risk of 0.20%, a maximum drawdown of 2.15% and a gain of 10%." [0:27:57]
**Source GPS: kYX05qESJMs | END**

> "So over more than a hundred trades, I proved that my edge was profitable" [0:28:17]
**Source GPS: kYX05qESJMs | END**

### S8. Mistakes he names (what NOT to do) (SOURCED)

Rule: do not open a stop-run trade early (before the high is actually swept); do not trade a directional breakout with rising volume as if it were an exhaustion stop run; do not take the London-session iceberg or stop-run patterns in the New York session.

> "So, my mistake was I kind of opened it too early." [0:09:14]
**Source GPS: kYX05qESJMs | MIDDLE**

> "I did not have a stop run on top because stop run is supposed to be an exhaustion move, but I opened simply an increasing volume due to a directional breakout." [0:10:31]
**Source GPS: kYX05qESJMs | MIDDLE**

> "it looks like this is New York session and this is not a trade I supposed to be taking during the New York session." [0:11:34]
**Source GPS: kYX05qESJMs | MIDDLE**
