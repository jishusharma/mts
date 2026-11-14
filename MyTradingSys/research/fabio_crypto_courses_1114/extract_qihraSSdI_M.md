# Extract: Andrea Cimi, "How to ACTUALLY use Volume Profiles" (`qihraSSdI_M`)

- **Video ID:** `qihraSSdI_M`
- **Speaker:** Andrea Cimi (DeepCharts co-founder, Fabio Valentini's partner)
- **Market in the video:** CME index futures (S&P / ES, 5-minute chart, cash session plus London/Asia sessions); no crypto. Concepts transfer, session clocks do not.
- **Source:** `raw_transcripts_canonical/qihraSSdI_M_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### V1. HVN and LVN meaning (SOURCED)

Rule: volume per price level over a window defines high volume nodes (peaks, price spent time, two-sided trade) and low volume nodes (valleys, one side pushing hard, directional sprints with few retracements). Computable from aggTrades binned by price. No entry, stop or target here.

> "these levels where there's a lot of volume specifically in a few levels of price we call these high volume nodes or HVN." [0:02:03]
**Source GPS: qihraSSdI_M | BEGIN**

> "So low volume node are let's say the more directional sprints of the markets." [0:03:20]
**Source GPS: qihraSSdI_M | BEGIN**

### V2. Value area is the first standard deviation, about 70 percent of volume (SOURCED)

Rule: the profile band plotted is the first standard deviation, rounded to 70 percent of the session volume. Trade outside it is a statistical anomaly that can revert to the mean. Window = a session (OURS for BTC: UTC day or a chosen session, untested).

> "So what we typically plot inside of a volume profile distribution is the first standard deviation only." [0:07:09]
**Source GPS: qihraSSdI_M | BEGIN**

> "This is where 70% of the volume was traded throughout that session." [0:07:20]
**Source GPS: qihraSSdI_M | BEGIN**

> "So, anything that happens outside is to be considered an anomaly that could revert back to the mean." [0:07:34]
**Source GPS: qihraSSdI_M | BEGIN**

### V3. Fade outside the value area, failed auction (SOURCED)

Rule: phase = balance (price inside a volume range). Setup = range-bound reversal: sell above / buy below the first standard deviation edge, especially a breakout that fails (failed auction). Entry trigger: price re-enters after a failed break (exact bar rule NOT stated). Stop: beyond the failed-break extreme ("below here" for a long). Target: other side of the distribution, or the conservative option POC / highest volume node. Win rate claim: "very decent win rate" with "typically a high risk-to-reward ratio": speaker claim, no data shown. Computable from aggTrades/klines (value area, POC, break and re-entry): yes.

> "we basically sell the tops and buy the bottoms whenever we go outside of the first volume standard deviation" [0:07:50]
**Source GPS: qihraSSdI_M | BEGIN**

> "when we see a breakout that fails, we call this a failed auction." [0:08:32]
**Source GPS: qihraSSdI_M | MIDDLE**

> "We might, for example, want to buy here with a stop-loss below here, targeting either the other side as a take-profit, or if you want to be more conservative, targeting the point of control or the highest volume node inside of the distribution as a take-profit." [0:08:34]
**Source GPS: qihraSSdI_M | MIDDLE**

> "And these are all trading setups that can have a very decent win rate with typically a high risk-to-reward ratio." [0:08:49]
**Source GPS: qihraSSdI_M | MIDDLE**

### V4. Volume-defined trend and breakout-test entry (SOURCED)

Rule: phase = trend. A trend exists when a new volume distribution forms above the previous one and the biggest chunk of volume trades above the previous biggest chunk (not just highs and lows). Entry: buy early for higher R, or wait for a strong breakout that spends time outside the old range and enter on the test. Stop: under the main high volume node. Target: NOT stated. Win rate: "very high win rate, high risk-to-reward": speaker claim, no data shown.

> "Whenever you see a new distribution of price happening above the previous one and a big chunk of volume being traded at higher prices than the previous biggest chunk of volume. That's when you can qualify that we're in an actual trend." [0:09:03]
**Source GPS: qihraSSdI_M | MIDDLE**

> "or wait for a very strong breakout that spends some time outside, enter on the test, stop-loss under the main high volume node, and that's also a very high win rate, high risk-to-reward type of setup." [0:09:49]
**Source GPS: qihraSSdI_M | MIDDLE**

### V5. Use real traded volume, not tick volume (SOURCED)

Rule: tick-count volume profiles are a proxy and can place the POC several points off the real one. Binance aggTrades quantity is real traded volume, so this transfers directly. Data-quality rule, no trade logic.

> "They're based on something called tick volume, which is a very rough approximation of actual trading volume." [0:10:39]
**Source GPS: qihraSSdI_M | MIDDLE**

> "here the point of control is at 69.87 so several points below." [0:12:26]
**Source GPS: qihraSSdI_M | MIDDLE**

### V6. Delta profile: net aggression per price level (SOURCED)

Rule: split each price level volume into buying and selling pressure; delta per level = buying minus selling. Big one-sided clusters mark where one side repeatedly took control; those levels (extended as zones) are reused as support or resistance from the previous session. Computable from aggTrades with the buyer-maker flag: yes. Entry/stop/target NOT stated for this use.

> "Delta tells you the total buying pressure minus the total selling pressure. So you have the net level of pressure at each level of price." [0:14:15]
**Source GPS: qihraSSdI_M | MIDDLE**

> "you can also clearly see from the previous session where was the area with most selling." [0:15:06]
**Source GPS: qihraSSdI_M | MIDDLE**

### V7. Use the cash-session profile, not the whole 24h session (SOURCED)

Rule: split the profile by session and keep the regular trading hours profile because that is where most volume trades; its value areas respond best for price-action and breakout ideas. For BTC (24/7 market) the equivalent session split is OURS and untested.

> "You might want to have only the volume profile for the so-called cash session, the regular trading hours, because that's where most money is traded anyways." [0:16:40]
**Source GPS: qihraSSdI_M | END**

> "And you'll see that those are the areas that responds best for price action ideas, for breakout ideas." [0:16:58]
**Source GPS: qihraSSdI_M | END**

### V8. Three uses: bias, support/resistance, trigger (SOURCED)

Rule: (1) bias: trend is up if the volume distribution (money) moves up; (2) support/resistance: in an uptrend, buy near the lower part of the previous session distribution after price fails below it, in trend direction, target the other side of the value area; (3) trigger: a short-term volume shift inside the signal candle (volume migrating away from the failed breakout level, plus an engulfing candle) confirms the higher-timeframe idea. Trigger example is a fade back to the mean: stop above the failed high, target the mean ("all the way until here", exact level NOT stated).

> "So we know the trend is up if we see volume going up, if we see the money going up." [0:17:48]
**Source GPS: qihraSSdI_M | END**

> "We want to see price failing below and then entering our trade together with a trend and maybe target the other side of the value area." [0:18:13]
**Source GPS: qihraSSdI_M | END**

> "we not only have an engulfing type of pattern where you have one candle being bigger than the previous one, but we can also have an extra confirmation with volume" [0:20:34]
**Source GPS: qihraSSdI_M | END**

> "That's our trigger with a stop above here and trading all the way until here." [0:21:10]
**Source GPS: qihraSSdI_M | END**

### V9. Opening-range breakout in the value area (SOURCED)

Rule: phase = after a failed auction back to the mean. Entry: buy when price breaks out of the opening range again and starts to spend time outside; stop "right below here" (the range, exact level NOT stated); target: the session, 1:3 risk-to-reward. Win rate: "really, really high": speaker claim, no data shown. Session clock is index-futures cash open (OURS for BTC: untested).

> "when we break out of the opening range, we can buy this market with a very conservative stop-loss right below here and basically take this entire session for a 1:3 risk-to-reward ratio with a really, really high win rate." [0:21:56]
**Source GPS: qihraSSdI_M | END**

### V10. Prefer the node distribution over the single POC (SOURCED, what NOT to do)

Rule: do not enter on the point of control as a singular level; neighbouring levels can have nearly the same volume, so the exact POC can be random. Use the high volume node (an area) instead.

> "I would not look at the point of control as a singular level because that can be random at times." [0:22:34]
**Source GPS: qihraSSdI_M | END**

> "It's more important to find a high volume node than the actual precise point of control" [0:23:01]
**Source GPS: qihraSSdI_M | END**

### V11. Caveat the speaker states about his own examples (SOURCED)

Rule: all examples are hand-picked past charts; no sample size, win rate count or R statistics are shown anywhere in the video. Every win rate and R figure above is a speaker claim, no data shown.

> "yes in hindsight everyone's good to cherry pick a couple example and I totally get that." [0:23:19]
**Source GPS: qihraSSdI_M | END**
