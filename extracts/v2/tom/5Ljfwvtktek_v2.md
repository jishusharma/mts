# V2 extract 5Ljfwvtktek (session 2026-10-09, jisnb/tom-extract-2026-10-09b)

Method: EXTRACTION_METHOD_V2.md (decision rows, anchors machine-checked) + playbook Part J tiers on the derived rules (section 3.7).
Read in full, one chunk. Show format: four contestants (Christian, Hines, Frank, Katherina) present strategies, Tom critiques each with hand sketches. No live trade. Only Tom's lines become rules; contestant lines are logged as CONTEXT, contestant and never sourced as Tom.

## 3.1 Header
```
video_id: 5Ljfwvtktek
trader: Tom Vorwald (channel "Tom Vorwald EN"; host and judge, "Four traders are competing against each other today for €1 million and a free spot in my mentorship")
title: I Build You a Profitable Trading Strategy in 10 Minutes | 1,000,000 Trader Battle Episode 4
instrument_stated: gold CFD (Christian), Nasdaq / S&P / gold / BTC / ETH (Hines), S&P and Nasdaq (Frank), EUR/USD and DAX (Katherina); Tom names 6E for EUR/USD
instrument_inferred: none
tick_size: unknown ("25 ticks" is a hypothetical stop distance)
session / time of day: S&P cash open 15:30 German time (Frank trades "1530 to,600, maybe until 1615"); 9-12 German time (Katherina)
translation_warning: yes (auto-captioned, non-native English; >> speaker marks; "riskreward" = risk-reward; "takerit" = take-profit; "P andB" unclear, see 3.6)
body_chars: 61061
n_decision_rows: 26
n_trades: 0
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition |
|---|---|---|---|---|---|---|---|---|
| 1 | 7 | LESSON | - | - | hit rate vs R:R | an 80% hit rate without the R:R "doesn't mean a thing to me" | own statistics | none stated |
| 2 | 11 | LESSON | - | - | R:R tracking | "You must track your riskreward ratios"; without them "you have no what's called expected value per trade" | own statistics | "when markets change their structure" |
| 3 | 14 | LESSON | - | - | losing streak | "What kind of consecutive stop- losses do I actually have to be able to expect? And that is the absolute alpha." | own statistics | none stated |
| 4 | 24 | CONTEXT | short | fair value gap | Hines's setup | "You have momentum alpha. The market shows you momentum via the corresponding fair value gap" | FVG, structure breaks | none stated |
| 5 | 24 | ENTRY (hypothetical) | short | retrace into the FVG | two structure breaks | wait "for a break of this structure", "another break which clearly indicates to you that the market is very weak", then "it runs up to the fair value gap and that is where you make your entry" | FVG, structure | two breaks first |
| 6 | 26 | LESSON | - | stop distance | size | stop "25 ticks away" -> calculate "exactly how many units you can afford"; "you define the number of units based on your stop-loss size firmly beforehand" | stop distance, money risk | none stated |
| 7 | 29 | LESSON | - | - | backtest without intervention | take profit "below the supposed last low", entry and stop as chosen, "check at least 200 trades": average R:R and hit rate | backtest | "if I hadn't intervened at all" |
| 8 | 30 | STOP_SET | - | invalidation level | stop placement | "a stop-loss order always belongs exactly where I would expect the complete opposite of my intended market movement to occur" | idea | none stated |
| 9 | 30 | REJECT | - | trailed stop | trailing | "stop trailing your stop- losses because that is just not the right way to manage your risk" | - | none stated |
| 10 | 32 | LESSON | - | - | setup quality | the FVG strategy is "functional because it always brings several aspects of proof with it before an entry is even planned" | FVG + breaks | none stated |
| 11 | 44 | LESSON | long | value area low of a balance profile | location in the balance | counter long against a downtrend: setup "better if it's lower" | balance profile | balance profile |
| 12 | 46 | REJECT | long | value area low inside a downtrend | location | against the trend "please only look in this area if you want to go long at all"; stops hit "in a price range where an aggressive downtrend prevails and the market isn't even in imbalance yet" | profile, trend | downtrend |
| 13 | 47 | STOP_SET | long | previous day low | stop level | below the previous day's low the market "most likely continues its downtrend. So, it's a much more logical level" | previous day range | counter long |
| 14 | 48 | LESSON | - | value area alerts | market selection | set signals on four markets: "You'll never have more than two markets giving you a signal at the same time" | alerts | none stated |
| 15 | 49 | LESSON | - | - | location | "where is a location where the market would absolutely have to turn to even do the opposite" | supply and demand | none stated |
| 16 | 52 | LESSON | - | - | process | analysis (trend and levels), "set signals", then "wait patiently for the entire setup process to finish completely" | alerts | none stated |
| 17 | 53 | ENTRY (hypothetical) | long | highest-volume price of the setup | footprint, CVD | finished auction at the low, "cumulative delta is rising", then wait for price back at "the highest volume" of the setup: "that's where you enter" | footprint, CVD, volume | price returns to the setup's highest volume |
| 18 | 55 | STOP_SET | long | below the setup low | stop | buy "just above the greatest equilibrium" with the stop below the setup's low: "a super clearly defined risk" | volume | none stated |
| 19 | 55 | TARGET_SET | long | POC, then value area high | targets | "first the point of control"; "in a sideways phase, I would definitely say it has to go up to the value high" | balance profile | counter-trend trade |
| 20 | 56 | LESSON | - | - | four points | include the trend "100%"; counter only "in price areas where an equilibrium was left and then finds acceptance again and not already at the equilibrium boundary"; "setups are welcome to come twice"; patience | profile, trend | against the trend |
| 21 | 85 | REJECT | - | trend line break | trend line | "please never take trend lines in isolation"; a break "quickly runs back" because "the market is running into a previous sideways range" | trend lines, prior range | none stated |
| 22 | 86 | ENTRY rule | short | below the broken range | acceptance | confirmation is liquidity shifting down, "forming acceptance of lower prices and then it makes sense to trade this trend continuation"; "A direct trend break is always fraught with very high risks" | volume | none stated |
| 23 | 88 | LESSON | - | candle bodies | zone drawing | zones from candle bodies: "the profile is often roughly in the middle of these bodies and the value areas are at the top and bottom" | candle bodies | H4 / daily zones |
| 24 | 92 | LESSON | - | resistance break | trade speed | "Trend continuation when a market goes into imbalance usually happens quickly"; "A counter trade in such a scenario if you see it coming here and it wants to turn usually takes a lot of time" | levels | imbalance = breaking a resistance level |
| 25 | 95 | LESSON | - | multi-time-frame levels | level quality | a wall hit on a large time frame gives "the probability is much higher than if you do that in a 1 minute chart" | multi-TF levels | none stated |
| 26 | 96 | LESSON | - | - | sample size | "at least 250 300 trades for each strategy to even recognize that I have a positive expected value" | own statistics | per strategy |

## 3.3 Trade blocks
No trade is taken. Rows 5 and 17 are hypothetical sketches (Hines's short into a fair value gap; Frank's long at a balance low), with stop and target only as drawn levels. n_trades: 0.

## 3.4 Rejections and conditions
- Row 9 (REJECT): trailing stops (Hines) is not risk management; the stop stays at the invalidation level.
- Row 12 (REJECT): a counter long at a value-area level inside an aggressive downtrend before the market reaches imbalance and returns to equilibrium.
- Row 21 (REJECT): trend-line breaks traded alone; the break often runs back into a prior sideways range.
- Row 20 condition: counter trades only where an equilibrium was left and price is accepted again, not at the equilibrium boundary; a second test ("come twice") raises the probability.
- Row 22 condition: continuation after a break only once acceptance of lower prices forms.

## 3.5 Verbatim anchors
> "So what's the risk-to-reward ratio underlying all of this? Otherwise, that hit rate doesn't mean a thing to me, right?"
**Source GPS: 5Ljfwvtktek | BEGIN**

> "Because when markets change their structure without tracking these metrics, you have no what's called expected value per trade."
**Source GPS: 5Ljfwvtktek | BEGIN**

> "What kind of consecutive stop- losses do I actually have to be able to expect? And that is the absolute alpha."
**Source GPS: 5Ljfwvtktek | BEGIN**

> "Now the next thing is you wait for a break of this structure right here."
**Source GPS: 5Ljfwvtktek | BEGIN**

> "So, and now it runs up to the fair value gap and that is where you make your entry."
**Source GPS: 5Ljfwvtktek | BEGIN**

> "Okay, that means you define the number of units based on your stop-loss size firmly beforehand."
**Source GPS: 5Ljfwvtktek | BEGIN**

> "Entry where you choose it, stop loss where you choose it, and then please check at least 200 trades."
**Source GPS: 5Ljfwvtktek | BEGIN**

> "a stop-loss order always belongs exactly where I would expect the complete opposite of my intended market movement to occur."
**Source GPS: 5Ljfwvtktek | BEGIN**

> "If you want to trade something like that against the trend, please only look in this area if you want to go long at all."
**Source GPS: 5Ljfwvtktek | MIDDLE**

> "is suddenly in a price range where the market goes below the previous day's low and most likely continues its downtrend. So, it's a much more logical level."
**Source GPS: 5Ljfwvtktek | MIDDLE**

> "You'll never have more than two markets giving you a signal at the same time."
**Source GPS: 5Ljfwvtktek | MIDDLE**

> "You see a finished auction down here. You see that the cumulative delta is rising down here."
**Source GPS: 5Ljfwvtktek | MIDDLE**

> "Next level first the point of control, please."
**Source GPS: 5Ljfwvtktek | MIDDLE**

> "For this trade in a sideways phase, I would definitely say it has to go up to the value high."
**Source GPS: 5Ljfwvtktek | MIDDLE**

> "If you want to enter markets against the trend, it makes sense to do that in price areas where an equilibrium was left and then finds acceptance again and not already at the equilibrium boundary"
**Source GPS: 5Ljfwvtktek | MIDDLE**

> "The third thing is setups are welcome to come twice."
**Source GPS: 5Ljfwvtktek | MIDDLE**

> "That's because the market is running into a previous sideways range. Therefore, please never take trend lines in isolation."
**Source GPS: 5Ljfwvtktek | END**

> "A direct trend break is always fraught with very high risks if you can't read it."
**Source GPS: 5Ljfwvtktek | END**

> "the profile is often roughly in the middle of these bodies and the value areas are at the top and bottom."
**Source GPS: 5Ljfwvtktek | END**

> "Trend continuation when a market goes into imbalance usually happens quickly."
**Source GPS: 5Ljfwvtktek | END**

> "And you must have at least 250 300 trades for each strategy to even recognize that I have a positive expected value."
**Source GPS: 5Ljfwvtktek | END**

## 3.6 Ambiguity flags
- Speakers: no names in the captions; Tom vs contestant is assigned from content. Row 4 opens with Tom restating Hines's setup in his own words, so the setup is Hines's and the reading is Tom's.
- Row 2: "if that is for example at 0.81, 81, you will never make money. If it's at 3.7, you'll be rich as a king" - an EV of 0.81R per trade would be positive; the number cannot be EV in R as stated. Not carried into any rule; flagged as unclear (possibly a profit factor or a caption error).
- Row 7: 200 trades here, row 26 "250 300" per strategy, Of_wlv3xaZo says well over 300: three sample numbers in three contexts.
- Row 11: the answer "It's probably better if it's lower" is Frank's; Tom confirms ("Exactly"). Logged as Tom's lesson with that caveat.
- Row 17-18: "highest volume" of the setup and "greatest equilibrium" are the same level as drawn; no width given. Stop "either down below here" is from the sketch.
- Row 22: "P andB concepts" is a caption fragment (possibly "P and b" profile shapes); not used.
- Row 24: imbalance is defined only by example ("breaking through one of your resistance levels").

## 3.7 Candidate rules, with provenance and the Naked BTC chart test
Tier = playbook Part J (T1 example, T2 self-check, T3 calculation, T4 recommendation, T5 command). Location tag = [T/id:file line@char offset in the raw file].

R-5Ljf-1 | T5 | The stop goes where the opposite of the trade idea would be proven; never trail it.
- Source: [T/5Ljfwvtktek:7@18834] ; [T/5Ljfwvtktek:7@18632]
- Naked BTC chart test: yes as a principle (the invalidation level is drawn on the chart); the level itself depends on the setup. No buffer given: NO-SOURCE.

R-5Ljf-2 | T5 | Size from the stop: units = money risk / stop distance, fixed before entry.
- Source: [T/5Ljfwvtktek:7@16367] ; [T/5Ljfwvtktek:7@16738]
- Naked BTC chart test: yes (stop distance is on the chart). 25 ticks and "100" risk are examples, not parameters.

R-5Ljf-3 | T1 (example) | Short continuation: impulsive move leaves a fair value gap, two breaks of structure show weakness, entry when price runs back up into the fair value gap, stop above the gap, target below the last low.
- Source: [T/5Ljfwvtktek:7@15046] ; [T/5Ljfwvtktek:7@15240] ; [T/5Ljfwvtktek:7@15543] ; [T/5Ljfwvtktek:7@18147]
- Naked BTC chart test: yes in shape (FVG = three-candle gap, swing breaks, last low all on a bare chart). Swing length, which FVG, and stop buffer: NO-SOURCE. Setup and stop "a bit above the gap" are Hines's; Tom calls it "functional" (row 10) and sets the backtest (row 7).

R-5Ljf-4 | T1 (example) | Counter-trend long in a downtrend only at the low of a balance (value area low) after price left the balance and is accepted back in it; the second test is better; stop below the previous day's low; targets POC first, then value area high.
- Source: [T/5Ljfwvtktek:7@34661] ; [T/5Ljfwvtktek:7@34948] ; [T/5Ljfwvtktek:7@29399] ; [T/5Ljfwvtktek:7@34210] ; [T/5Ljfwvtktek:7@34373]
- Naked BTC chart test: yes in part. VAL / POC / VAH and the previous day's low are computable from candle volume; left and accepted again has no time or close count: NO-SOURCE. The footprint confirmation (finished auction, rising CVD, row 17) is not on OHLCV; CVD needs trade-side data.

R-5Ljf-5 | T1 (example) | After the setup forms, enter when price returns to the setup's highest-volume price, stop below the setup's extreme.
- Source: [T/5Ljfwvtktek:7@33012] ; [T/5Ljfwvtktek:7@33914]
- Naked BTC chart test: yes. The highest-volume price inside the setup candles is computable from lower-time-frame volume; setup window: NO-SOURCE.

R-5Ljf-6 | T4 | Never trade a trend-line break alone; it often runs back into the prior sideways range. Trade continuation only when price is accepted beyond the broken level (liquidity shifts there).
- Source: [T/5Ljfwvtktek:7@52206] ; [T/5Ljfwvtktek:7@52787]
- Naked BTC chart test: partly. Prior range and its volume are computable; "acceptance" has no measure: NO-SOURCE.

R-5Ljf-7 | T1 (example) | Zones from candle bodies: the volume profile sits roughly mid-bodies, value area edges at the top and bottom of the bodies.
- Source: [T/5Ljfwvtktek:7@54392]
- Naked BTC chart test: yes, and testable: compare body-cluster midpoints with computed POC on BTC. Tom states it from "many analyses", no number.

R-5Ljf-8 | T4 | Statistics per strategy: track R:R, hit rate, EV per trade and the longest losing streak; at least 200 trades without intervention (row 7), 250-300 per strategy (row 26).
- Source: [T/5Ljfwvtktek:7@6940] ; [T/5Ljfwvtktek:7@8563] ; [T/5Ljfwvtktek:7@59011]
- Not chart-observable; backtest design rule.

Not a rule (contestant words): Christian's early exits and 1:2 to 1:5; Hines's stop at the end of the gap and trailing; Frank's 3:1 minimum and stop below the reversal candle (Tom: "That's totally stupid, right?" refers to the oversized stop); Katherina's three-touch trend lines, half-candle limit and EMA5 "flash".

Rules with parameters and no source: none in this file.

## 3.8 Self-check
- Last decision row pos% 96: row 26 is the last strategy item; after it Tom only announces who moves on.
- Terms CT / TC / trend_healthy / tier: tier appears only in section 3.7, as the playbook Part J tiers.
- Gate result is pasted at the end of the file after the run.

## Gate result (2026-10-09)
```
verify_extract_quotes.py: PASS: 0 problem(s) (21 anchors)
inline quoted fragments: all verbatim (extract_fix_gps.py)
```
