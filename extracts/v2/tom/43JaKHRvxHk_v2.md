# V2 extract 43JaKHRvxHk

Method: EXTRACTION_METHOD_V2.md (decision rows, anchors machine-checked). Read in full in 5 chunks of about 2,000 characters (offsets 0, 2000, 4000, 6000, 8000 of the 9,147-character body), first to last character. Lecture video on how to use the VWAP (counter trader, trend follower, scalper). No chart price, no entry, no exit, no trade is shown or taken.

## 3.1 Header
```
video_id: 43JaKHRvxHk
trader: Tom (the transcript is first person and does not name him)
title: 90% of Traders Use VWAP WRONG! (Here's How to Do It Right)
instrument_stated: not stated
instrument_inferred: none
tick_size: unknown
session / time of day: unknown (only "the open" / "the market open" is mentioned as a context cue, no clock time)
translation_warning: no (the transcript does not say it was translated); the wording reads as machine-translated or auto-captioned ("7 million stop losses", cut sentences), so treat odd phrases as [?]
body_chars: 9147
n_decision_rows: 35
n_trades: 0
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition |
|---|---|---|---|---|---|---|---|---|
| 1 | 10 | CONTEXT | - | VWAP | where price is relative to today's average | "volume weighted average price of today" | VWAP | none stated |
| 2 | 16 | LESSON | - | VWAP | daily reset | "recalculated for every single day" | VWAP | "starts again essentially at zero" |
| 3 | 20 | LOCATION | long | VWAP, after market ran back to it | market far above VWAP | "I have the opportunity to make a long trade" | VWAP | "whenever the market is far above the VWAP and it runs back to the VWAP"; "if the market is stably trending, we can use it" |
| 4 | 23 | CONTEXT | - | - | share of trending time | "only about 30% truly stably trending" | market phase | the other "70%" is not trending |
| 5 | 32 | REJECT | - | VWAP | counter trading every VWAP touch | "I'd have 7 million stop losses here" | VWAP, market phase | applies if VWAP is used "for counter trading" always, without context |
| 6 | 33 | LESSON | - | VWAP | trend as first filter | "the VWAP must be based on a trend" | market phase | "Only then can I see if I might enter my trade based on counter trades on this VWAP" |
| 7 | 36 | LESSON | - | VWAP | how institutions read it | "If the price is below it, they're initially more bearishly inclined." | VWAP | above VWAP: "more bullishly inclined" |
| 8 | 37 | LESSON | - | VWAP | context needed | "without context, you'll just keep getting punched in the nose" | VWAP | none stated |
| 9 | 40 | LOCATION | - (counter trader; side word not said) | "up here", above, trading toward the VWAP | liquidity running out | "wait until the market shows me no more liquidity" | order book / big orders [?] ("no more liquidity" not defined) | counter trader only |
| 10 | 41 | TARGET_SET | - (counter trader) | VWAP | VWAP as profit target | "I have the VWAP as a profit target, for example." | VWAP | "I also have to adjust my profit target dynamically" because the VWAP keeps moving up |
| 11 | 42 | LESSON | - | VWAP target | VWAP drifts | "adjust my profit target dynamically accordingly" | VWAP | "It keeps moving up with it" |
| 12 | 43 | LOCATION | long | VWAP pullback | long trend, VWAP pullback | "wait for a long trend and can wait until the VWAP gives me a pullback" | VWAP, market phase | trend follower |
| 13 | 45 | CONTEXT | - | "target areas" | earlier collapse | "Hasn't it hit some target areas before that caused the market to completely collapse now?" | unknown ("target areas" not defined) [?] | "I absolutely must be able to classify" |
| 14 | 47 | CONTEXT | - | the open | how the open forms | "how is the market opening formed? The open." | time of day (open) | none stated |
| 15 | 47 | CONTEXT | - | the open | trendy open | "if the open tells me the market is going to be very trendy today" | time of day (open), VWAP | "the VWAP, for example, that's running along" |
| 16 | 50 | LOCATION | - (with the trend; side word not said) | VWAP | trend continuation at VWAP | "I have the possibility to use a trend continuation sequence here" | VWAP, time of day (open) | the open "fits with the variant that it's trendy" |
| 17 | 52 | REJECT | - | - | other setup types on a trendy open | "definitely only look for a trend continuation setup here" | time of day (open) | applies when the open says trendy |
| 18 | 56 | LOCATION | - | "price ranges from the VWAP" | reaction zones | "define so-called price ranges from the VWAP where you expect a reaction" | VWAP | none stated |
| 19 | 59 | LOCATION | - | counter trader from above toward VWAP; trend continuing trader upwards | different locations | "a completely different location than the counter trader" | VWAP | none stated |
| 20 | 63 | CONTEXT | - | VWAP running sideways | balance | "the VWAP is basically running sideways here the whole time" | VWAP | "you can already see balance" |
| 21 | 64 | LOCATION | short | price ranges above the sideways VWAP ("in these price ranges") | scalper, balance | "you can brilliantly search for short trades here" | VWAP | VWAP sideways (balance) |
| 22 | 65 | LOCATION | long | "down" (sentence cut after "down") | scalper, balance | "you can search for long trades down" [?] | VWAP | VWAP sideways (balance) |
| 23 | 67 | TARGET_SET | - (scalper) | VWAP | trade taken only up to VWAP | "only ever take the trade up to the VWAP" | VWAP | "very modest profit targets" |
| 24 | 68 | STOP_SET | - (scalper) | not stated | where the trade is given up | "where do I give up on my trade?" (a question; no level or rule stated) | unknown | none stated |
| 25 | 71 | LESSON | - | - | risk-reward for scalpers | "It's very modest" | VWAP | "you can localize it depending on how the VWAP is currently structured" |
| 26 | 73 | REJECT | - | - | trend continuation in a sideways VWAP | "you mustn't trade a trend continuation" | VWAP | "in a sequence like this", VWAP sideways; instead "go for counter trades" |
| 27 | 75 | LESSON | - | - | filter for scalping model | "Only if the VWAP is currently oriented sideways" | VWAP, time of day (open) | "I can't assume a maximally brutal breakout now or a trend day from the market open" |
| 28 | 79 | LESSON | - | VWAP | summary 1: trend following | "we use the VWAP for trend continuation scenarios" | VWAP, time of day (open) | "the open variant is also suitable for a trend" |
| 29 | 83 | TARGET_SET | - (counter trader) | VWAP | steep VWAP, price running extremely high | "we can define the VWAP as a profit target" | VWAP | "if the VWAP is very steep" and "the price is running extremely high"; assumption "the market always likes to return to its equilibrium price" |
| 30 | 86 | CONTEXT | - | VWAP | caution on target | "this level will continue to shift upwards" | VWAP | "as long as the market has stability or achieves some short-term balance" |
| 31 | 87 | REJECT | - | - | predefined risk-reward ratio | "you don't have the opportunity here to establish a predefined risk-reward ratio" | VWAP | counter trader with VWAP target |
| 32 | 88 | LESSON | - | - | hit rate and minimum R:R decide the distance | "you have to know your hit rate" | own statistics | "I have to trade at least up to here, otherwise the whole thing makes no sense" (no number stated) |
| 33 | 93 | LOCATION | short and long | "at the top" / "at the bottom" | dynamic scalping | "keep looking for shorts at the top and keep looking for longs at the bottom" | VWAP, time of day (open) | VWAP "very sideways oriented" and the opening variant "more sideways weighted"; "until a reversal of the market environment eventually occurs" |
| 34 | 96 | CONTEXT | - (downward, his word) | VWAP going lower | VWAP and average price shifting down | "should the VWAP suddenly start to go lower and lower" | VWAP | none stated |
| 35 | 98 | LESSON | - | - | consequence of lower VWAP | "the probability increases that a trend continuation downwards will occur" | VWAP | "or even a breakout" |

## 3.3 Trade blocks
No trade is taken or shown. No ENTRY row exists; the video describes three ways of using the VWAP, not a trade. n_trades: 0. Because there is no trade, no stop level, target level or entry price is stated anywhere; the only stated levels are role descriptions:
- Counter trader: location above ("up here"), target = the VWAP (rows 9-10, 29), target moves with the VWAP (row 11).
- Trend follower: location = the VWAP pullback in a long trend after a trendy open (rows 12, 14-16).
- Scalper in a sideways VWAP: shorts in the upper ranges, longs in the lower ranges, target = the VWAP, "very modest" R:R, stop level not stated (rows 20-26, 33).
mirror stated?: no - do not assume

## 3.4 Rejections and conditions
- Row 5 (REJECT): always counter trading the VWAP gives "7 million stop losses"; condition: no context filter.
- Row 17 (REJECT): on a trendy open, "only look for a trend continuation setup".
- Row 26 (REJECT): in a sideways VWAP sequence, do not trade a trend continuation; go for counter trades.
- Row 31 (REJECT): with a moving VWAP target no predefined risk-reward ratio can be set well; use own hit rate and minimum usable R:R (row 32).
- Row 3 condition: market "stably trending", price far above the VWAP and running back to it.
- Row 6 condition: "the VWAP must be based on a trend" before counter trades on it are considered.
- Row 10 / 11 condition: the target is adjusted dynamically because the VWAP keeps moving up.
- Row 27 condition: scalping model only if the VWAP is oriented sideways and no "maximally brutal breakout" or "trend day from the market open" is expected.
- Row 29 condition: VWAP "very steep" and price "running extremely high".
- Row 30 condition: the VWAP level shifts up "as long as the market has stability or achieves some short-term balance".
- Row 33 condition: VWAP sideways and sideways-weighted open; ends "until a reversal of the market environment eventually occurs".

## 3.5 Verbatim anchors
> "The VWAP shows us nothing other than the volume weighted average price of today."
**Source GPS: 43JaKHRvxHk | BEGIN**

> "the VWAP is recalculated for every single day"
**Source GPS: 43JaKHRvxHk | BEGIN**

> "whenever the market is far above the VWAP and it runs back to the VWAP, then I have the opportunity to make a long trade"
**Source GPS: 43JaKHRvxHk | BEGIN**

> "markets are only about 30% truly stably trending"
**Source GPS: 43JaKHRvxHk | BEGIN**

> "then I'd have 7 million stop losses here"
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "the VWAP must be based on a trend"
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "If the price is below it, they're initially more bearishly inclined."
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "without context, you'll just keep getting punched in the nose"
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "I have to wait until the market shows me no more liquidity in some way, for example, up here"
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "And then I have the VWAP as a profit target, for example."
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "I also have to adjust my profit target dynamically accordingly"
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "I have to wait for a long trend and can wait until the VWAP gives me a pullback"
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "Hasn't it hit some target areas before that caused the market to completely collapse now?"
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "how is the market opening formed? The open."
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "if the open tells me the market is going to be very trendy today"
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "I have the possibility to use a trend continuation sequence here"
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "You should then definitely only look for a trend continuation setup here."
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "You can define so-called price ranges from the VWAP where you expect a reaction."
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "a completely different location than the counter trader who trades from above towards the VWAP and the trend continuing trader who trades upwards"
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "the VWAP is basically running sideways here the whole time"
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "you can already see balance"
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "you can brilliantly search for short trades here in these price ranges"
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "And you can search for long trades down"
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "if I were to only ever take the trade up to the VWAP, I can already see those are very modest profit targets"
**Source GPS: 43JaKHRvxHk | END**

> "where do I have to set my stop loss? So, where do I give up on my trade?"
**Source GPS: 43JaKHRvxHk | END**

> "It's very modest"
**Source GPS: 43JaKHRvxHk | END**

> "in a sequence like this, you mustn't trade a trend continuation. You absolutely have to go for counter trades."
**Source GPS: 43JaKHRvxHk | END**

> "Only if the VWAP is currently oriented sideways, and I can't assume a maximally brutal breakout now or a trend day from the market open, then I can use this whole model for myself."
**Source GPS: 43JaKHRvxHk | END**

> "Then we use the VWAP for trend continuation scenarios"
**Source GPS: 43JaKHRvxHk | END**

> "then we can define the VWAP as a profit target"
**Source GPS: 43JaKHRvxHk | END**

> "the market always likes to return to its equilibrium price"
**Source GPS: 43JaKHRvxHk | END**

> "this level will continue to shift upwards as long as the market has stability or achieves some short-term balance"
**Source GPS: 43JaKHRvxHk | END**

> "you don't have the opportunity here to establish a predefined risk-reward ratio very well"
**Source GPS: 43JaKHRvxHk | END**

> "you have to know your hit rate"
**Source GPS: 43JaKHRvxHk | END**

> "I have to trade at least up to here, otherwise the whole thing makes no sense"
**Source GPS: 43JaKHRvxHk | END**

> "you have the opportunity to keep looking for shorts at the top and keep looking for longs at the bottom until a reversal of the market environment eventually occurs"
**Source GPS: 43JaKHRvxHk | END**

> "should the VWAP suddenly start to go lower and lower"
**Source GPS: 43JaKHRvxHk | END**

> "then the probability increases that a trend continuation downwards will occur here again, or even a breakout"
**Source GPS: 43JaKHRvxHk | END**

> "those are exactly the possibilities that in my view are feasible with the VWAP"
**Source GPS: 43JaKHRvxHk | END**

## 3.6 Ambiguity flags
- Row 9: "no more liquidity in some way, for example, up here" - "liquidity" is not defined (order book, volume or tail); the chart location "up here" has no price.
- Row 13: "target areas" that "caused the market to completely collapse" - not defined; may be a mistranslation of reaction or level areas.
- Row 5: "7 million stop losses" is hyperbole, not a number.
- Row 22: sentence cut after "long trades down" (a pause or missing words in the caption).
- Row 24: the stop is only asked as a question ("where do I give up on my trade?"); no answer is given in the transcript.
- Row 27/33: "non-trend or something like that" (the open) is vague.
- Row 28: the summary sentence before "the open variant is also suitable for a trend" is cut ("if we" then a gap).
- The raw file carries three header blocks with different word counts (1746, 1715, 1695) before the body; the body_chars above counts only the text after the last header block.

## 3.7 Self-check
- ENTRY rows: 0; trade blocks: 0 (consistent; no trade in this lecture).
- Last decision row pos% is 98 (at least 95).
- Instrument not stated; no stop, target or entry price is stated in numbers anywhere; every stop/target statement is a rule in words (VWAP as target; stop level not given).
- Quote checker result is appended below.
PASS: 0 problem(s)
