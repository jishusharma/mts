# Extract: Fabio Valentini, "This Changes How You Trade Forever - Fabio Valentini" (`TjEYZH4u7d0`)

- **Video ID:** `TjEYZH4u7d0`
- **Speaker:** Fabio Valentini (Fabervaale), interviewed by Andrea Cimi on World Class Edge (81 min). Mostly career, prop-firm and expectation talk; only the passages below are trading rules.
- **Market in the video:** CME index futures (NQ/ES) and US equities, plus Nifty/KOSPI mentions; no crypto. The IVB (his name for the volume-confirmed opening-range breakout, caption writes "IBB"/"IVB"/"orb") is an opening-range idea tied to the US cash open; the clock does not transfer, the pattern may.
- **Source:** `raw_transcripts_canonical/TjEYZH4u7d0_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote. Every number he reports is a speaker claim, no data shown, unless stated otherwise.

## Rules

### T1. IVB: why the opening range works and which hours matter (SOURCED)

Rule: US index volume arrives at known times; the two highest-volatility hours are known in advance (he says 8 sessions out of 10). The opening-range top and bottom are passive liquidity walls. Parameters: opening-range length, the two hours and the "8 out of 10" are speaker claims, no data shown. Duplicate check: IVB appears in extract_XE2MQJE5yIY.md only as a bias label, not these definitions.

> "US indices are predictable on where the volume will arrive during the day. You know when the volume will arrive and you know the 2 hours where the maximum volatility will be there, okay? Eight session out of 10." [0:47:03]
**Source GPS: TjEYZH4u7d0 | MIDDLE**

> "you take the top range and the bottom of range of the battle, okay? So you know that there was a liquidity passive passive liquidity wall on the top and on the bottom." [0:47:29]
**Source GPS: TjEYZH4u7d0 | MIDDLE**

### T2. IVB entry: break of one side of the range, direction continues (SOURCED)

Rule: trade in the direction of the first side that breaks the opening range, with options levels (put/call wall) as an extra check where available. Entry bar, stop and target: NOT stated in this video (see T3 for the stop idea). He warns the break often fails.

> "Once one side breaks, okay, the probability that the day will continue in that direction is really high. What's the problem of this? That a lot of times it does fake breakout." [0:47:47]
**Source GPS: TjEYZH4u7d0 | MIDDLE**

### T3. Fake-breakout filter: strong delta bar, one big aggressor, stop below the aggression (SOURCED)

Rule: take the range breakout only when the breakout bar has strong delta; stronger still when MBO (market-by-order) shows one big participant pushing, not many small ones. Stop goes below that aggression, which gives an asymmetric risk to reward. Delta-bar threshold and stop distance in ticks: NOT stated (OURS/unknown). BTC aggTrades have no order IDs, so the "one big player" test is only approximated by a single large aggTrade or a burst of same-side prints (OURS).

> "during the years I find out that the best filter is using a strong delta bar when you have a breakout." [0:48:01]
**Source GPS: TjEYZH4u7d0 | MIDDLE**

> "Even better if you have aggressive buyers there, market participants with MBO that you can see that there's one market participant, not many, okay? So one big player betting in directional there." [0:48:06]
**Source GPS: TjEYZH4u7d0 | MIDDLE**

> "And then you can cover yourself below this aggression and take really asymmetric risk to return." [0:48:20]
**Source GPS: TjEYZH4u7d0 | MIDDLE**

### T4. ORB confirmed by volume (big trades or participation) (SOURCED)

Rule: the plain opening-range breakout is upgraded by watching volume interaction (big trades or participation), not only direction. Speaker claim, no data shown: tested over 10 years and traded live for longer, still works, with some bad quarters.

> "the orb supported by volume. It becomes the IBB. So, you don't only watch the direction, you watch the interaction of the volume using big trades or using participation. This is one of the most consistent I tested on the last 10 years" [0:10:05]
**Source GPS: TjEYZH4u7d0 | BEGIN**

### T5. IVB is a bias, order flow is the trigger (SOURCED)

Rule: IVB alone is not the system; it sets the day's bias and the footprint/order-flow event times the entry. He says timing with order flow lets him double or triple the risk to reward with the same bias and raises the profit factor (speaker claim, no data shown, no numbers). Entry trigger detail, stop and target: NOT stated here.

> "I don't use the IVB as a standalone system. I use the IVB as a bias system because it's really consistent and then I use order flow to time better the market." [0:14:08]
**Source GPS: TjEYZH4u7d0 | BEGIN**

### T6. Regime filter: weak volatility expansion means fake IVB breakouts (SOURCED)

Rule: when a volatility-regime model (GARCH) says the environment is bad for volatility expansion, expect IVB fake breakouts; filtering on it raised win rate by about 7 percent (speaker claim, no data shown, his quant partner's study). The GARCH setup itself is NOT given. For BTC an own realised-volatility or GARCH filter is OURS and untested. Separately he says the IVB works worse on S&P than Nasdaq.

> "when the GARCH environment it's bad for volatility expansion, a lot of times you can see from the IVB fake breakout. It's not a holy grail, but also boosting your win rate by 7%." [0:24:31]
**Source GPS: TjEYZH4u7d0 | BEGIN**

> "What I find on S&P working worse than Nasdaq still there is the IVB. And this is structural." [0:13:57]
**Source GPS: TjEYZH4u7d0 | BEGIN**

### T7. Prefer the directional instrument (SOURCED)

Rule: the breakout system works better on the more directional index (Nasdaq) than on the slower, more liquid one (ES); equity line on ES "not so smooth" (speaker claim, no data shown). For BTC the analogue is instrument choice by trendiness (OURS).

> "Nasdaq it's an asset that it's really good on this because it's more directional than ES. ES is more slow and liquid, okay?" [0:48:26]
**Source GPS: TjEYZH4u7d0 | MIDDLE**

### T8. Tool choice for bias vs timing (SOURCED)

Rule: bias from the cash-session volume profile; candlesticks only together with volume; footprint delta over footprint bid/ask; big trades over liquidity heat map. Nothing about entry or stop here.

> "cash session volume profile for bias." [1:18:46]
**Source GPS: TjEYZH4u7d0 | END**

> "Candlesticks only with volume." [1:18:52]
**Source GPS: TjEYZH4u7d0 | END**

### T9. Earnings-surprise gap: buy the resting orders in the gap, stop below (SOURCED, equities only)

Rule: after a large earnings surprise, big players get heavy slippage if they execute at once, so resting orders build inside the gap; the entry is a test of that area with a stop below it, to capture the following drift. Speaker claims, no data shown: about 20 executions on one stock, very high win rate; gap size three to four times smaller than the 60-day drift; with 50 percent win rate that is about 1 to 2. Not testable on BTC (no earnings).

> "it creates a huge amount of resting orders in that gap. And this is your window of opportunity for that test with a stop loss below to take the drift, okay?" [0:12:40]
**Source GPS: TjEYZH4u7d0 | BEGIN**

### T10. Risk: oversizing signal, no martingale, stop when the strategy is off (SOURCED, what NOT to do)

Rule: if you feel fear or excitement on a trade you are oversizing; one day's result should not matter to you. Do not double risk after losses (martingale); a losing streak means the strategy does not fit the current market, so stop. Numeric risk per trade: NOT stated.

> "Like the single day of stop loss, of profit, should not be able to change to change your life in any single way." [0:08:42]
**Source GPS: TjEYZH4u7d0 | BEGIN**

> "if you double the risk with martingale or stuff like this that beginners do, you end up the day with a huge loss." [0:06:39]
**Source GPS: TjEYZH4u7d0 | BEGIN**

> "The market is telling you, look, your strategy is not performing at the moment, okay? Because maybe you have a trend following strategy, the market is compressed, you should stop." [0:06:23]
**Source GPS: TjEYZH4u7d0 | BEGIN**

### T11. Validate on trigger probability before execution (SOURCED)

Rule: three validation layers: bias system, option flow, and the order-flow trigger (he tests trigger probability inside DeepCharts); discretion only in position management and environment. Only execute what is validated. Numbers: none.

> "I know what the order flow gives me as an edge on a trigger because we can test now on deep chart the trigger probability. So, I have three lines of validation and then I put my discretionarity in position management in environment." [0:34:44]
**Source GPS: TjEYZH4u7d0 | MIDDLE**

> "Only execute what you already validated." [1:20:47]
**Source GPS: TjEYZH4u7d0 | END**
