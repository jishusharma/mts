# Krown RULES_DRAFT (pilot, 2026-10-16) - his own words, tagged

Scope: pilot of 6 transcripts that are NOT in the TA 101 corpus (that corpus is already ledgered: `../krown_ta101_2026-10-13/KROWN_RULES.csv`, 120 rules).
This file adds the **daily-video method**: event-study "setups", targets as median-return arithmetic, probability statements, invalidation levels.
Videos: V0gjxlaW2Qk (2026-10-06), wvu0onib6WU (2026-10-13), BvxLX8FL3bg (2026-10-14), SOaAP9vBgM4 and 7CFrrRm5hLw (shorts, 2026-10-07), dzH7m9cQeZA (2026-09-27).
Not mined for rules: qwjU2jI2D-0 (accumulation theory, execution/slippage education, no numbers), 0F-WBBd5M3s (2024 Meta Signals NFT interview/promo).
Every quote is machine-checked by `scripts/dev/verify_extract_quotes.py` (replaced the deleted check_quotes.py) against the transcripts (auto-captions; case and punctuation normalised, timestamps are the caption line where the quote starts).
Tags: **SOURCED** = his words, **OURS** = our reading. Nothing here is an MTS rule; no edge is claimed. Captions carry stutter ("the the"), so quotes are cut at clean spans.

## A. How he states odds (the probability framing)

**A1. A setup = a trigger, a count, a hit-rate, a median return at fixed horizons.** SOURCED. He quotes (n, % green at +1, +2, +3 months, median %), never a stop or size.
> "this has happened 19 times in Bitcoin's history"
Source: wvu0onib6WU @00:00:49
> "79% of the time Bitcoin is green from that signal confirmed"
Source: wvu0onib6WU @00:01:08
> "the probability of it being green goes up significantly from 79 to 89%"
Source: wvu0onib6WU @00:03:37
> "95% of the time, you're going to be green during that time"
Source: wvu0onib6WU @00:04:03
OURS: construct = event (first bar where condition becomes true after a reset), outcome = sign and size of return at +21/+42/+63 calendar days. P(green) and median are both reported.

**A2. He reports two medians, all history and since 2018.** SOURCED. He concedes the pre-2018 returns can be called unrealistic, yet says he would "prefer the previous ones": he reports both and flags the gap; he does not drop the old sample.
> "median of returns for the totality of results going back all the way to 2011"
Source: wvu0onib6WU @00:01:41
> "if we just looked at the results pertaining to 2018 and beyond so I would say that would be you know, more modern results"
Source: wvu0onib6WU @00:01:50
> "the median return there is 14 and 1/2%"
Source: wvu0onib6WU @00:02:08
> "I just want to show you how people can kind of fool you with data."
Source: SOaAP9vBgM4 @00:00:10
> "I would prefer the previous ones, personally"
Source: V0gjxlaW2Qk @00:08:08
OURS: the study must report pre-2018 and post-2018 separately; our DEV/VALIDATION/HOLDOUT split replaces his choice of window.

**A3. The median is used as a target-price generator, with a band.** SOURCED.
> "about 14 and 1/2% to the upside puts Bitcoin where"
Source: wvu0onib6WU @00:02:31
> "I would make kind of a range of probability between now and sort of uh earlyish to mid-November"
Source: wvu0onib6WU @00:02:44
> "Again, these are median returns."
Source: V0gjxlaW2Qk @00:04:39
OURS: target = signal-bar close x (1 + median). Test: realised-return distribution vs his stated median (coverage of the 25th to 75th percentile).

**A4. Probability is never 1.** SOURCED.
> "if something has a 70% probability to work out, there's still a 30% probability that it does not"
Source: BvxLX8FL3bg @00:03:05
> "Not because it's guaranteed, but because it's more likely to happen and over time we will be more right than wrong."
Source: wvu0onib6WU @00:04:18

**A5. Independent setups stack.** SOURCED (logic), OURS (no combination rule given: he counts, no weights).
> "completely different indicators, completely different, you know, methodology"
Source: wvu0onib6WU @00:06:50
> "this is another setup amongst many"
Source: V0gjxlaW2Qk @00:04:40
OURS: confluence = number of independent setups pointing the same way inside the same window; test as an ordinal score, not a sum of his percentages.

**A6. Timing is a window, not a bar.** SOURCED.
> "it's the back half of October when I really expect things to try into the like to the upside"
Source: wvu0onib6WU @00:06:34

## B. Setups with a trigger definition

**B1. Stochastic above 80 for the first time after a long spell below.** SOURCED. Two separate studies: weekly (V0g: first time above 80 after 10 or more weeks below; 12 of the past 13 times) and 10-day timeframe (wvu: 19 prior cases, 79% green at one month).
> "weekly stochastic also to get above 80"
Source: V0gjxlaW2Qk @00:00:16
> "12 of the past 13 times"
Source: V0gjxlaW2Qk @00:00:28
> "stochastic momentum oscillator is about to get above the 80"
Source: wvu0onib6WU @00:00:46
Parameters NOT given: oscillator length and smoothing ("stochastic momentum oscillator" is a named indicator; settings unverified). OURS to choose on DEV.
His own undo condition for the 10-day signal:
> "for that signal to be undone"
Source: wvu0onib6WU @00:01:34
> "come down below about 81 or at least 80,000 bucks"
Source: wvu0onib6WU @00:01:30
OURS: "the signal depends on the close of the 10-day bar" is our reading; he gives only a price level, and in BvxLX8FL3bg admits he has no backward calculation for it.

**B2. Corrective setup: 5 EMA crosses below 21 EMA, minimum target the 55 EMA.** SOURCED. Hit-rate varies by timeframe (6h in the CBP video: 72% within 4 bars, see KROWN_FREE_VS_PAID s1d).
> "82% um you know, probability to test the 55 EMA within 10 days"
Source: wvu0onib6WU @00:08:40
> "it is a minimum corrective target, so you can see a wick below"
Source: BvxLX8FL3bg @00:05:09
> "the more and more that will naturally be pulled up"
Source: wvu0onib6WU @00:08:50
> "less than a 10% probability"
Source: wvu0onib6WU @00:09:25
OURS: target is the 55 EMA value at test time (moving), not the value at the cross. His unit is days on the daily chart, not bars of any timeframe. Tail: outliers take 30 to 40 days, "less than a 10% probability".
Follow-on: after the test, next day green 70%, 5 days 60%, returns "less than a percent":
> "the next day is very likely to be green 70"
Source: BvxLX8FL3bg @00:14:31

**B3. Golden cross dispersion path.** SOURCED. Realised path of the current cross is compared with the historical median path and the 25th to 75th percentile band; the leg up is expected around day 40.
> "day number 40 is typically where you see this leg up"
Source: wvu0onib6WU @00:06:21
> "especially as we get closer and closer to day number 40"
Source: BvxLX8FL3bg @00:13:55
> "you probably have some plus EV just by looking"
Source: BvxLX8FL3bg @00:14:01
OURS: construct = cumulative return path indexed by days since the cross; "underperformance vs median path then catch-up" is a testable second-order claim (his claim, no stated n).

**B4. 5-day EMA reconnect bounce.** SOURCED.
> "about 7 and 1/2% in the first days after"
Source: BvxLX8FL3bg @00:15:18
Definition of "reconnect" is not in the pilot (price touches the 5 EMA from away, on the 5-day or 10-day timeframe). OURS to define.

**B5. Death cross filter: slope of the 200 simple average.** SOURCED.
> "when the 200 simple slope is down"
Source: 7CFrrRm5hLw @00:00:18
> "you're probably looking to sell any rally towards that"
Source: 7CFrrRm5hLw @00:00:33
OURS: filter = sign of the 200 SMA slope over N bars (N not given).

**B6. Three green weeks / three green months.** SOURCED (stated in V0g: 13 prior monthly cases, 77% green at 1, 3 and 6 months).
> "there are 13 previous times"
Source: V0gjxlaW2Qk @00:06:52
> "77 % of the time, time, literally for all three of those timeframes"
Source: V0gjxlaW2Qk @00:06:58
> "the median returns there is is over 14 and a quarter percent"
Source: V0gjxlaW2Qk @00:07:25
77% of 13 cases is 10 cases (our arithmetic). All-history medians 14.25 / 60 / 44.7 % at 1, 3, 6 months; since 2018 about 8 % (OURS reading of his "plus 8%, plus 7%, plus 8.5%").

## C. Levels, supports, invalidation

**C1. The trending higher low is the invalidation level, per timeframe.** SOURCED (explained in TA 101).
> "as long as you're above 62,000 bucks, which is that last trending higher low"
Source: wvu0onib6WU @00:07:28
> "Even below 75,000 bucks, you know, would take out a higher low, but not the most important higher low."
Source: wvu0onib6WU @00:07:44
> "that last trading higher low for the daily time frame is all the way at 75,000 bucks"
Source: BvxLX8FL3bg @00:05:15
OURS: THL pivots per timeframe are a mechanical swing construct (TA 101 KR-L10 already defines it); the ladder of levels (12h, daily, weekly) is the support map. Test: P(close below THL(tf)) vs forward drawdown.

**C2. Closing basis, not wicks.** SOURCED.
> "if you close below there"
Source: wvu0onib6WU @00:07:23
(In context: closes decide; wicks below are allowed: "you can see a wick below".)

**C3. Ribbon mid band as the swing line.** SOURCED. Proprietary TradingView indicator ("Revin Ribbons" in the captions, spelling uncertain); mid band about 85,000 at that time.
> "as long as the coins closing dailies above there"
Source: V0gjxlaW2Qk @00:12:07
> "I would be very much looking for a corrective move down at least between 83 to 84 thousand dollars"
Source: V0gjxlaW2Qk @00:12:21
OURS: not testable until the ribbon settings are known (paid indicator, not in pilot).

**C4. Quarterly 5 EMA as the cycle floor.** SOURCED.
> "you should probably be looking for low somewhere around that red 5 EMA"
Source: BvxLX8FL3bg @00:04:15

## D. What he refuses to trade (useful filters for us)

**D1. Macro prints.** SOURCED. CPI-conditional returns: 43% green, under half a percent; "not worth trading".
> "you're talking about things that have a 43% probability"
Source: BvxLX8FL3bg @00:08:40
> "Thus, it's not worth trading upon."
Source: BvxLX8FL3bg @00:08:48
> "the further and further away from a realistic edge you have"
Source: BvxLX8FL3bg @00:08:31

**D2. Prediction markets as a probability cross-check.** SOURCED (he trades small, "fun money").
> "I did very, very, very small dollar amounts"
Source: V0gjxlaW2Qk @00:01:31
OURS: free read of implied probabilities is an optional context input; no trading of it.

**D3. "Krown optimism index" (proprietary).** SOURCED: ranges -100 to +100; he says it is not a buy/sell signal.
> "I would argue at negative 25 pessimism, you have no edge"
Source: V0gjxlaW2Qk @00:08:50
> "it's not telling you to buy or sell"
Source: V0gjxlaW2Qk @00:08:56

## E. Stops and false breakouts (dzH7m9cQeZA, microstructure series)

**E1. Wait for confirmation to avoid sweeps.** SOURCED.
> "one easy rule is just wait for three"
Source: dzH7m9cQeZA @00:12:23
> "consecutive candles above"
Source: dzH7m9cQeZA @00:12:26
> "typically happens within one to three"
Source: dzH7m9cQeZA @00:12:18
OURS: breakout confirmed = 3 consecutive closes beyond the boundary; sweep = wick beyond with a close back inside within 1 to 3 bars. Test: fire rate and forward move for confirmed vs swept.

**E2. Stop placement: where the idea is wrong, not where the crowd parks.**
> "pull your stop where the idea is wrong, not where the crowd parks"
Source: dzH7m9cQeZA @00:18:45
> "go a few percent above that or below that"
Source: dzH7m9cQeZA @00:18:54
SOURCED: the principle and "a few percent" past the pile. OURS: "a few percent" is a vague range; we must choose a number on DEV. It is the only stop-distance language in the pilot. His "invalidation" elsewhere (C1) is a level, not a stop order.

## F. Not rules (recorded so nobody re-reads them as such)
- Daily DCA buys, Coinbase fee-discount referral, TradingView lifetime-indicator sale (code word and 20% off), Kalshi referral credit: sales, not method.
- "Do I think that it's highly probable? I don't know about that": his own Kalshi bets are sized as fun money; there is no sizing rule here.
- Sentiment of the pilot (bullish toward 90k to 100k by end of October 2026) is a call, not a rule: it becomes an out-of-sample observation (post 2026-09-30), see INVENTORY.md section 6.
