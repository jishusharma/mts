# V2 extract tS6ZEiHj8gQ (round 2, 5.2: third by risk/stop/target/size frequency)

Session: MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio. Method: EXTRACTION_METHOD_V2.md. Read in 6 chunks of about 2,000 characters.
Frequency 11.1 per 1,000 words (rank 3 of the Tom-set transcripts, after WSCIURybK3U and kXhIAug0Gh8).

## 3.1 Header
```
video_id: tS6ZEiHj8gQ
trader: Tom (corpus mapping; the transcript says "I'm Thomas Forgald. I'm the champions maker" - ASR of his name)
title: Trading World Champion Explains: The PERFECT Short ... (header line of the raw file)
instrument_stated: Avis Budget Group stock (Nasdaq); he also mentions Volkswagen "back then" and crude oil "which then went to minus"
instrument_inferred: none
tick_size: unknown (prices in dollars)
session / time of day: "8:40" (the peak of the move; time zone not stated), "1-hour time frame"
translation_warning: no flag in the text (non-native English, auto-captioned)
body_chars: 10785
n_decision_rows: 28
n_trades: 2 (an "old days" example: first short stopped out, then a re-entry that "worked")
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition ("as long as") |
|---|---|---|---|---|---|---|---|---|
| 1 | 5 | CONTEXT | - | Avis, short squeeze | story | "The first thing we always need is what is the story behind it?" (hedge funds hold shares, high short interest) | news | none stated |
| 2 | 15 | CONTEXT | - | - | squeeze mechanics | short sellers forced to buy: "Panic broke out. Then margin call started happening." | news | none stated |
| 3 | 19 | REJECT | short | the peak at 8:40 | - | "it really does not make much sense to just short somewhere around here" [F4] | [new source] story/exhaustion | "wait until the market falls back below certain key price levels" |
| 4 | 21 | CONTEXT | short | previous candle close | bar close | "we can use the closing price of the previous candle as a benchmark" | bar close (TF not stated) | "quite often, by that time, it is already far too late in the move" |
| 5 | 37 | CONTEXT | - | - | volume | "The first thing I'm always interested in is what do the volumes look like?" | volume by price / HVN/LVN [?] | none stated |
| 6 | 39 | CONTEXT | - | 1-hour chart | volume trend | "a 1-hour chart is completely sufficient"; "total volumes are increasing at a steady rate" | [new source] volume trend | none stated |
| 7 | 41 | REJECT | short | early entry | - | an early short: "That's always possible. But, the probability of getting stopped out is then high" | volume | none stated |
| 8 | 44 | LOCATION | short | huge volume bar, then consolidation | volume, consolidation | "a market has risen sharply with absolutely exponential volumes, and suddenly there's a period of consolidation" | volume, profile (consolidation) | none stated |
| 9 | 48 | ENTRY | short | "640" (stated as "if you entered the market at 640") | - | "There was an opportunity here to enter my first short." ; order type unknown ; BEFORE or AFTER proof: after the consolidation | profile (consolidation) | none stated |
| 10 | 51 | STOP_SET | short | above the level; 730 | - | "you have to place your risk above this level" [F5] ; "a stop loss at 730. That's $90" | swing high [?] | none stated |
| 11 | 55 | TARGET_SET | short | where the last largest volumes occurred ($250) | volume by price | "the profit target should be where the last largest volumes occurred" [F2] | HVN/LVN (largest volume node) | reason: "that is where the market had its stable and fair market price valuation before the story began its rapid and explosive move" |
| 12 | 57 | CONTEXT | short | 640 to 250 | R:R | "9 18 27 36 up to greater than four" (profit range $390 against $90 risk) | - | none stated |
| 13 | 56 | EXIT | short | - | - | "As we can see, it unfortunately didn't work out as expected." ; exit type stop (implied by "if you had hit the stop loss here") | - | none stated |
| 14 | 59 | CONTEXT | short | - | - | "we can enter another trade" | - | none stated |
| 15 | 61 | LOCATION | short | the stop-out area, on a smaller time frame | profile (balance zone) | "build a corresponding balance zone right here in this area where you unfortunately got stopped out" | profile (balance zone) | none stated |
| 16 | 64 | PROOF (BEFORE) | short | above the level again | volume | "when the market went above this level again, the trading volumes were already not as extreme anymore" | volume | none stated |
| 17 | 73 | PROOF (BEFORE) | short | - | B profile | "this here is a wonderful B profile" | today's profile (B shape) | none stated |
| 18 | 76 | ENTRY | short | - | - | "makes sense to enter into this trade again" ; order type unknown ; entered AFTER proof (rows 16-17) | profile, volume | "Here, I have a risk that is suddenly significantly and substantially reduced" |
| 19 | 77 | STOP_SET | short | - | - | "If I have a risk of $40, $35, I can relax." (stop distance per share; the stop level is not stated) | - | none stated |
| 20 | 78 | TARGET_SET | short | $250 | - | "I always have to stick to my price target, my price target of $250" | - | none stated |
| 21 | 80 | LESSON | short | position size | size | "I always determine my position size in direct accordance with my stop-loss level." | - | "I can take many more shares than in the previous idea with, for example, $90" |
| 22 | 83 | LESSON | short | - | size | with the first stop, "almost three times as many" shares would have lost much more | - | none stated |
| 23 | 85 | REJECT | short | shorting at the tops | - | "it's always good to wait" because "your risk to the upside is theoretically unlimited" | - | none stated |
| 24 | 87 | CONTEXT | short | next day | gap | "another gap down on the following day" after the "initial maximum squeeze" and "a trend reversal" | time of day (overnight gap) | none stated |
| 25 | 88 | LESSON | short | - | - | "the idea, unfortunately, didn't work out. Second idea, that one worked." | - | none stated |
| 26 | 93 | PROOF (summary) | short | - | - | three pieces of information before the second trade: the overnight gap, the volume "no longer as high, but still exponentially much greater", "a B structure" | volume, today's profile (B shape), time of day | none stated |
| 27 | 95 | LESSON | - | - | - | "sometimes it's better not to short right at the tops, even if it looks like you should" | - | none stated |
| 28 | 96 | LESSON | - | - | - | "you can try both times. And if you have smart risk management, it works out great as well." | - | none stated |

## 3.3 Trade blocks
```
TRADE 1 - short - rows 8-13
state (day/week): short squeeze in a stock after a sharp, sudden rise; volumes "exponential", then a consolidation
location: after the huge-volume bar, in the consolidation ; level type: other (volume peak and consolidation)
leading signal: huge volume then consolidation
trigger: consolidation after the exponential volume ; entered BEFORE or AFTER proof: after
entry order type: unknown ; placed before the touch: unknown
initial stop: "above this level" ; distance: $90 (entry 640, stop 730 as an "if you entered" example) ; % of price: 90/640 = 14.1 percent (both stated; arithmetic mine)
target: "where the last largest volumes occurred", $250 ; distance: $390 ; stated R:R: "greater than four" (390/90 = 4.33, arithmetic mine)
management: none ; exit: stop hit ("didn't work out as expected") ; exit type stop
rejects: shorting at the peak (row 3), shorting early (row 7)
information sources: news (squeeze story), volume, 1-hour chart, bar close of the previous candle, profile (consolidation)
outcome: loss of the stop distance ($90 per share as stated for the stop); no total
horizon: unknown
mirror stated?: no - do not assume
TRADE 2 - short - rows 14-26 (re-entry)
state: after the stop-out, the market above the level again with "trading volumes ... not as extreme anymore", an overnight gap, "a B structure"
location: balance zone built where he was stopped out ; level type: balance zone
leading signal: lower volume on the new push above the level
trigger: B profile ; entered BEFORE or AFTER proof: after
entry order type: unknown ; placed before the touch: unknown
initial stop: not stated as a level ; distance: "$40, $35" ; % of price: unknown (no entry price stated)
target: same $250 ; stated R:R: not stated
management: size set from the stop distance: "a significantly larger position size" ; exit: "Second idea, that one worked" ; exit type unknown
rejects: shorting at the tops without such a setup (rows 23, 27)
information sources: volume, profile (balance zone, B shape), time of day (overnight gap)
outcome: "that one worked" (no figure)
mirror stated?: no - do not assume
```

## 3.4 Rejections and conditions
- Row 3 and 27: no short at the peak; wait for a fall back below key levels or for a setup.
- Row 7: no early short because the stop-out probability is high.
- Row 23: always good to wait when shorting because the upside risk is unlimited.
- Row 10 condition: the stop sits above a level; row 11: the target is the last largest-volume area; row 21: size comes from the stop distance.

## 3.5 Verbatim anchors
> "it really does not make much sense to just short somewhere around here"
**Source GPS: tS6ZEiHj8gQ | MIDDLE**

> "But, the probability of getting stopped out is then high."
**Source GPS: tS6ZEiHj8gQ | MIDDLE**

> "There was an opportunity here to enter my first short."
**Source GPS: tS6ZEiHj8gQ | MIDDLE**

> "you have to place your risk above this level"
**Source GPS: tS6ZEiHj8gQ | MIDDLE**

> "the profit target should be where the last largest volumes occurred"
**Source GPS: tS6ZEiHj8gQ | MIDDLE**

> "As we can see, it unfortunately didn't work out as expected."
**Source GPS: tS6ZEiHj8gQ | MIDDLE**

> "makes sense to enter into this trade again"
**Source GPS: tS6ZEiHj8gQ | END**

> "If I have a risk of $40, $35, I can relax."
**Source GPS: tS6ZEiHj8gQ | END**

> "my price target of $250"
**Source GPS: tS6ZEiHj8gQ | END**

> "That's why it's always good to wait."
**Source GPS: tS6ZEiHj8gQ | END**

## 3.6 Ambiguity flags
- Row 9-10: "if you entered the market at 640, you had a stop loss at 730" is stated with "you", as a worked example; whether these were his fills is not said. In the sister video WSCIURybK3U the same stock uses entry 630, stop 730, exit 230.
- Row 13: the exit is implied by "if you had hit the stop loss here"; no words say "I was stopped out" for the first trade except "got stopped out" at row 15.
- Row 19: "$40, $35" is the stop distance in dollars per share; the level is not given.
- Row 26: the three "pieces of information" are listed at the very end and are a summary of rows 16-17 and 24.

## 3.7 Falsification flags (5.3)
Method (5.3): each rule claim below was searched against all 102 transcripts in raw_transcripts_canonical for a contradicting passage (patterns: stop placement, target, scalp, trailing and moving stops, short at the top, risk percent, draw down, re-entry, hit rate, adding); a hit counts only if it is in a Tom-set transcript and speaks to the same variable.
Claims searched (6): C1 no short at the peak (row 3); C2 stop above a level (row 10); C3 target at the last largest volumes (row 11); C4 position size from the stop distance (row 21); C5 re-entry on a B profile after lower volume (rows 16-18); C6 an early short has a high stop-out probability (row 7).
Result: 3 flagged (C1, C2, C3), 3 with no contradiction found (C4, C5, C6).
- [F4] row 3, partial contradiction: "If you want to go short at the top, you have to pay dynamic attention to it." [T/rFPCtOcfUMI:13@10093]. Reconcilable (shorting the top needs proof), but the two sentences differ in tone.
- [F5] row 10, direct contradiction on the variable "stop of a short": "It doesn't belong above the high. Why is that?" [T/yRvMW6lgN1o:19@6182]; also "my stop loss is now set exactly above the last volume levels" [T/k0zm5NYn0IQ:19@16227]. Row 10 says "above this level" without naming the level, so the contradiction is with the reading "above the high".
- [F2] row 11, tension with the "above the highs" ledge target [T/4MoNjEQ2Dd8:19@810]: liquidity ledge vs largest-volume node. Supported by "if it accepts new prices, then it looks for the next high volume price and that is your target" [T/qLnQan0KGmQ:19@7547].
- C4: no opposing statement found; sizing from the stop is repeated in WSCIURybK3U and hQ8sOq67x5o ("how much risk per trade I can even take").
## 7 self-check
1 ENTRY rows: 2 (rows 9, 18); trade blocks: 2. 2 Fields filled. 3 Last row pos% 96. 4 Checker line below.

PASS: 0 problem(s)
