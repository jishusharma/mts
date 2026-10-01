# V2 extract 4MoNjEQ2Dd8 (round 2, method audit 5.1a)

Session: MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio. Method: MyTradingSys/research/fast_track_2026-09-27/EXTRACTION_METHOD_V2.md. Read in 12 chunks of about 2,000
characters, first to last character, without opening any existing extract of this video first (V1 comparison done afterwards, see EXTRACTION_ROUND2_2026-10-01.md).

## 3.1 Header
```
video_id: 4MoNjEQ2Dd8
trader: Tom (corpus mapping; the transcript does not name him)
title: $2,350 in 40 Minutes: How the World Champion ACTUALLY ... (header line of the raw file)
instrument_stated: not stated (he names the NASDAQ and the S&P as markets he watches)
instrument_inferred: DAX future, a guess: levels 25,600-25,644 sit near the DAX level in his other videos (24,220 in WSCIURybK3U) and the intro says euro; the NASDAQ and S&P are named as OTHER markets watched (rows 10, 32). Never copied below.
tick_size: unknown
session / time of day: "1845" (time zone not stated), "5-minute close", "15-minute close", "lunch break is coming up"
translation_warning: yes ("I translated this video with AI")
body_chars: 22120
n_decision_rows: 52
n_trades: 1
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition ("as long as") |
|---|---|---|---|---|---|---|---|---|
| 1 | 3 | LOCATION | long | "wonderful price area" | price area | "price area where I'm looking for a long entry" | prior-day profile (row 5) | none stated |
| 2 | 3 | ENTRY | long | same area | - | "that's why I'm now" [?] (sentence cut); order type unknown | - | none stated |
| 3 | 3 | STOP_SET | long | below the last low | last low | "The stop loss goes below the last low here" | swing high/low | none stated |
| 4 | 3 | TARGET_SET | long | above the highs ("ledge") | ledge | "my take-profit is set above the highs" [F2] | equal highs ("ledge") | none stated |
| 5 | 4 | CONTEXT | long | yesterday's profile | tail, value, PC [?] | "buying tail ... moved back into value, saw rejection at the PC" | prior-day profile, tail, POC | none stated |
| 6 | 5 | TARGET_SET | long | value high, "around 644" | value high, ledge | "reach the price area of the value high" | VAH, equal highs | none stated; R:R "very large", no number |
| 7 | 8 | PROOF (AFTER) | long | bottom | absorption | "the market was absorbed at the bottom" | absorption | "will it hold this level or break down through it" |
| 8 | 10 | PROOF (AFTER) | long | down here | aggressive buying | "aggressive buying keeps happening down here" | delta / aggressive buyers | none stated |
| 9 | 12 | CONTEXT | long | today's POC; volume above and below, empty space between | today's profile | "as long as we hold these volumes here ... the market can shoot upwards" | today's profile, HVN/LVN | "as long as we hold these volumes here" |
| 10 | 14 | CONTEXT | long | PC | S&P | "constantly holding its ground ... buying tails" | other market (S&P), tail | none stated |
| 11 | 16 | ADD | long | at the breakout (planned) | market speed | "I'll add to the position again at the breakout" | market speed | "If we continue to move steadily up and carefully maintain the current speed" |
| 12 | 17 | STOP_SET | long | below the business zone | - | "Stop loss as mentioned below the bid below the business zone" [?] | order book [?] | none stated; "risk ratio and four. So 4:1" [?] |
| 13 | 20 | CONTEXT | long | absorption volume of the initial long | absorption | "we first covered our initial long trade down here" ["covered"?] | absorption | "as soon as we move past this point" a "very very aggressive long trade" follows |
| 14 | 22 | CONTEXT | long | 25,600 | big order | "There's a big order at 25,600" | order book / big orders | "if it breaks through here soon" |
| 15 | 24 | REJECT | long | 25,600 | seller absorbing, speed | "But I don't want to scalp." [F1] | order book, absorption | "I want the momentum to happen above here" |
| 16 | 26 | PARTIAL | long | value high about 25,640 (planned) | VAH | "I might be willing to sell the first position" | VAH | "if we move up to the value high around 25,640" |
| 17 | 28 | CONTEXT | long | "the long side is still to be favored" | volume at the top | "the long side is still to be favored" | today's profile | "as long as we stay above here"; "mindful of what happens if the market drops below that level" |
| 18 | 33 | CONTEXT | long | low volume area | profile | "intraday swing traders, breakout traders who are waiting for the explosion" | HVN/LVN | none stated |
| 19 | 36 | CONTEXT | long | - | open P&L | "100 ticks risk. We've got 161 on the clock." (open profit, not a target; risk 100 ticks stated) | - | none stated |
| 20 | 38 | HOLD | long | closing price above the high | bar close (TF not stated) | "we absolutely need to get a closing price now. then I'll keep the position" | bar close | "Otherwise, I'd just close out one contract right away" |
| 21 | 41 | HOLD | long | above the high | speed, big order | "now we need to hold above this level" | order book | "Otherwise, it's better to close out a" [cut] |
| 22 | 44 | PARTIAL | long | top | rotation | "let's close out a position. We're happy with that." | order book, rotation | stop left "down here" because "too much rotation up there" |
| 23 | 45 | HOLD | long | stop stays | rotation | "We'll leave the stop loss down here" | order book | none stated |
| 24 | 46 | CONTEXT | long | - | - | "pocketed the first $1,200 or so" (outcome of row 22) | - | none stated |
| 25 | 47 | HOLD | long | price range above / low volume area | trading volume | "As long as we stay above this price range ... the whole thing is fine for us" | today's profile | "if the market lingers a bit in the low volume area here and then picks up action again" |
| 26 | 49 | CONTEXT | long | 620 and 600 | big orders | "large orders sitting down here ... exactly 620 and 600" | order book | "as long as this level holds"; "if it drops below that, then it's game over" |
| 27 | 50 | STOP_MOVE | long | below the 600/620 area; the new level is not stated in words [?] | big orders, liquidity | "We now adjust our stop" | big orders, today's value | "if it goes below that it's simply over"; reason: probability high that the market takes out the accumulated liquidity first |
| 28 | 53 | CONTEXT | long | today's value area | profile | "back within today's value area" | today's profile | "as long as we're above it the market is ... a bit out of control" |
| 29 | 56 | LESSON | - | - | - | "You can't control the market. You can only react to the circumstances that arise." | - | none stated |
| 30 | 56 | STOP_MOVE | long | a range where "I simply expect the opposite of my long position" | - | "I moved the stop loss to a price range where I simply expect the opposite of my long position" | - | "before that, it doesn't make sense to move the stop-loss" |
| 31 | 56 | REJECT | long | - | - | "it doesn't make sense to move the stop-loss" before such a range exists [F3] | - | stop moves only to a range where the opposite is expected |
| 32 | 58 | CONTEXT | long | swing high "at 82" | swing high, S&P, NASDAQ | "probability is simply high that it will take out this swing high" | swing high, other market (S&P, NASDAQ) | "as long as we stay above here" |
| 33 | 60 | CONTEXT | long | - | - | "we've already taken profits twice now" (summary; only one explicit PARTIAL before pos 60, see flags) | - | "we won't lose anything here anymore even if the market stops us out" |
| 34 | 66 | HOLD | long | last buying area / up here | liquidity, delta | "As long as that holds, it's not critical." | HVN/LVN, delta | "if we go down here now, then it's over" |
| 35 | 68 | REJECT | long | - | - | "I deliberately didn't do it this time so as not to" [cut] (scalpers would have bought here) | - | reason cut [?] |
| 36 | 70 | ADD | long | - | S&P holding its step | "I'm definitely buying yet another significant position" | other market (S&P), volume step | none stated; order type unknown; reason cut ("far too much inherent") [?] |
| 37 | 71 | ADD | long | - | - | "buying our last position now and just saying all or nothing" | - | "Either it breaks out upwards now or it turns around and it's over" |
| 38 | 73 | CONTEXT | long | 600 area; "fair prices" above | liquidity | "the market broke through liquidity nicely on the downside and now wants to move back up" | order book | none stated |
| 39 | 74 | HOLD | long | stop | - | "Our stop-loss is really tight which means we have absolutely no stress." | - | none stated |
| 40 | 76 | PARTIAL | long | the S&P step (planned) | S&P | "I'd be ready to close out one of the very short-term positions again" | other market (S&P), volume step | "if the S&P doesn't make it past the step now" |
| 41 | 78 | CONTEXT | long | "660" [?] / 620 | steps | "It would be nice if we could get above 660 now." [?] ("Close it right away" unclear) | volume step | none stated |
| 42 | 80 | PARTIAL | long | 620 (planned) | 5-minute close | "we'll take a few ticks off" | bar close (5m) | "we're almost at 620 ... whatever happens above that is all bonus" |
| 43 | 83 | ERROR | long | - | - | "I placed an order too early because I expected the breakout to happen" | - | "it was all within a price range where the probability was very high" |
| 43b | 84 | CONTEXT | long | 620 | market speed | "if we push above it, then the sky's is the limit" (added after the condition count, see EXTRACTION_ROUND2) | market speed | "as long as we're below it, it's just going to keep consolidating back and forth" |
| 44 | 85 | CONTEXT | long | 15-minute close; "1845" | bar close, time | "now it's 1845 and unfortunately we still don't have any higher closing prices" | bar close (15m), time of day | "as long as it doesn't do that, there's a high risk" [cut] |
| 45 | 91 | STOP_MOVE | long | 603 | 5-minute volume by price | "we don't want to go below 603 anymore" | volume by price (5m) | "if it drops below that, things will break down" |
| 46 | 93 | PROOF (AFTER) | long | "118 contracts at 25." [cut] | big order, speed | "The speed is picking up. Look at what's being bought here. And now comes the breakout." | order book, market speed | none stated |
| 47 | 95 | PARTIAL | long | top | - | "Let's take out another position." | market speed | none stated |
| 48 | 95 | STOP_MOVE | long | "below the last trades price area 16" [level shorthand] | volume by price | "I'm moving my stop loss up now below the last trades price area 16." | volume by price | reason: "keep it really simple now" and "Last attempt" |
| 49 | 97 | EXIT | long | top | speed | "That's why I'm out now, I think." | market speed ("Speed Off") | "Speed Off ... being sold off again"; exit type manual |
| 50 | 98 | LESSON | long | - | - | "it was a good decision for now to put the stop there" (outcome "$2,360") | - | none stated |
| 51 | 99 | CONTEXT | - | - | time of day | "lunch break is coming up, so I'm ending the session" | time of day | none stated |

## 3.3 Trade blocks
```
TRADE 1 - long - rows 1-50
state (day/week): "The market opened lower, then crashed down, came back in, formed acceptance, then made a nice pull back to the business zone"
location: "business zone" / "wonderful price area" ; level type: acceptance area (his words); also yesterday's buying tail and rejection at the PC
leading signal: buying tail after the open, move back into value, rejection at the PC
trigger: at the location ; entered BEFORE or AFTER proof: before (absorption and aggressive buying read after, rows 7-8)
entry order type: unknown ; placed before the touch: unknown
initial stop: "below the last low" / "below the business zone" ; distance: 100 ticks (stated at pos 36) ; % of price: unknown (tick size not stated, price level not tied to the stop)
target: "above the highs" (ledge), value high about 25,640-644 ; distance: not stated ; stated R:R: "4:1" [?] (pos 17) ; open profit "161 on the clock" at pos 36 (not a target)
management: PARTIAL rows 22, 47 (explicit) and planned 16, 40, 42 ; STOP_MOVE rows 27, 30, 45, 48 ; ADD rows 36, 37 (planned 11)
exit: speed faded at the top ("Speed Off") ; exit type manual
rejects: scalping at the first resistance (row 15) ; buying like a scalper (row 35) ; moving the stop before an "opposite" range exists (row 31)
information sources: prior-day profile, today's profile, VAH, POC, tail, equal highs, volume step, HVN/LVN, order book / big orders, delta / aggressive buyers, absorption, market speed, other market (S&P, NASDAQ), bar close 5m and 15m, time of day, swing high/low
outcome: "$1,200 or so" for the first batch; "$2,360" at the end; intro says "€2,350 in 40 minutes" (currency differs)
horizon: "40 minutes" (title and intro)
mirror stated?: no - do not assume
```

## 3.4 Rejections and conditions
- Row 15: no scalping at the first resistance; wait for momentum above ("I want the momentum to happen above here").
- Row 31: no stop move before a range exists where the opposite of the long is expected.
- Row 35: did not buy like a scalper at that point (reason cut).
- Conditions: rows 7, 9, 17, 20, 21, 25, 26, 28, 32, 34, 40, 42, 44, 45 each carry an "as long as / if below / need a close" test; rows 20 and 21 make a PARTIAL the fallback if the close or the hold fails.
- Row 26 and 34: "if it drops below that ... it's game over / then we should definitely exit": the exit rule below the 600/620 area, stated before the stop move at row 27.

## 3.5 Verbatim anchors
> "Here we have a wonderful price area where I'm looking for a long entry and that's why I'm now"
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "The stop loss goes below the last low here"
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "my take-profit is set above the highs"
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "we should definitely reach the price area of the value high up here"
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "I'll add to the position again at the breakout"
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "Stop loss as mentioned below the bid below the business zone"
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "But I don't want to scalp."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "I might be willing to sell the first position"
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "let's close out a position. We're happy with that."
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE**

> "We now adjust our stop"
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE**

> "I moved the stop loss to a price range where I simply expect the opposite of my long position."
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE**

> "And before that, it doesn't make sense to move the stop-loss."
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE**

> "Again, I deliberately didn't do it this time so as not to"
**Source GPS: 4MoNjEQ2Dd8 | END**

> "I'm definitely buying yet another significant position"
**Source GPS: 4MoNjEQ2Dd8 | END**

> "Here we're buying our last position now and just saying all or nothing."
**Source GPS: 4MoNjEQ2Dd8 | END**

> "I'd be ready to close out one of the very short-term positions again"
**Source GPS: 4MoNjEQ2Dd8 | END**

> "then we'll take a few ticks off. That's a sensible move right now."
**Source GPS: 4MoNjEQ2Dd8 | END**

> "That means we don't want to go below 603 anymore."
**Source GPS: 4MoNjEQ2Dd8 | END**

> "Let's take out another position."
**Source GPS: 4MoNjEQ2Dd8 | END**

> "I'm moving my stop loss up now below the last trades price area 16."
**Source GPS: 4MoNjEQ2Dd8 | END**

> "That's why I'm out now, I think."
**Source GPS: 4MoNjEQ2Dd8 | END**

## 3.6 Ambiguity flags
- Row 13: "covered our initial long trade" - probably "opened" (translation).
- Row 5: "PC" is read as POC; the transcript writes "PC".
- Row 12: "below the bid below the business zone"; "from chance risk ratio and four. So 4:1 from the winning line" is garbled; the 4:1 is not tied to entry, stop and target prices.
- Rows 14, 26, 41, 45, 48: price levels are given as 25,600, 620, 600, 660, 603 and "16"; the thousands part is dropped after the first mention; "660" at row 41 may be 640 or 620.
- Row 33: "taken profits twice" while only one explicit PARTIAL (row 22) precedes it; the second is not located in the text.
- Row 19: "161 on the clock" has no unit; it is read as open profit in ticks next to "100 ticks risk".
- Row 24 and the outcome: "$1,200", "$2,360" and the intro "€2,350" use different currencies.
- Row 49: "Speed Off" is a spoken label, not a defined indicator.

## 3.7 Falsification flags (5.3)
Method (5.3): each rule claim below was searched against all 102 transcripts in raw_transcripts_canonical for a contradicting passage (patterns: stop placement, target, scalp, trailing and moving stops, short at the top, risk percent, draw down, re-entry, hit rate, adding); a hit counts only if it is in a Tom-set transcript and speaks to the same variable. Starred ids in the corpus search are the Tom set (57 ids).
Claims searched (8): C1 stop below the last low (row 3); C2 target above the highs (row 4); C3 no scalping at the first resistance (row 15); C4 add at the breakout (row 11); C5 keep only on a close above the high (rows 20-21); C6 partial on rotation (row 22); C7 no stop move before an "opposite" range (rows 30-31); C8 stop to the last 5-minute volume (row 45).
Result: 3 flagged (C2, C3, C7), 5 with no contradiction found (C1, C4, C5, C6, C8).
- [F1] row 15, tension: the reject is for this trade; Tom teaches scalping: "if you're a scalper, for example, you can brilliantly search for short trades here in these price ranges" [T/43JaKHRvxHk:19@5866]. Not a contradiction of the row; it contradicts any reading of row 15 as "Tom rejects scalping".
- [F2] row 4, tension: target = above the highs (a "ledge") here; elsewhere "the profit target should be where the last largest volumes occurred" [T/tS6ZEiHj8gQ:19@6115] and "the next high volume price and that is your target" [T/qLnQan0KGmQ:19@7547]. Two target definitions (liquidity ledge vs volume node).
- [F3] row 31, tension (trade-dependent): moving or trailing the stop varies: he trails "to the high" early in kXhIAug0Gh8 [T/kXhIAug0Gh8:19@3349], declines to trail in another trade ("In this case, I don't do that") [T/k0zm5NYn0IQ:19@7033], and moves the stop up after adding [T/n7ZSkjb7JXs:19@4807].
- C1 and C8 kin: "my stop loss belongs below the last liquidity" [T/3o1VVsfBmmU:19@6014] and "my stop loss is now set exactly above the last volume levels" [T/k0zm5NYn0IQ:19@16227] support, not contradict.
## 7 self-check
1 ENTRY rows: 1 (row 2); trade blocks: 1. 2 All trade-block fields filled ("unknown" where not stated). 3 Last row pos% 99 (>= 95).
4 Checker line: last line of this file. 5 Forbidden mapping words (whole-word grep for the four labels the method names) do not occur outside this self-check.

PASS: 0 problem(s)
