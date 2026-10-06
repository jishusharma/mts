# V2 extract kXhIAug0Gh8 (round 2, 5.2: top by risk/stop/target/size frequency)

Session: MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio. Method: EXTRACTION_METHOD_V2.md. Read in 5 chunks of about 2,000 characters.
Selection: second of the Tom-set transcripts ranked by (risk+stop+target+size) per 1,000 words, 13.6 per 1,000 words (WSCIURybK3U first at 16.2).

## 3.1 Header
```
video_id: kXhIAug0Gh8
trader: Tom (corpus mapping; the transcript says "I'm Don Polwad. I'm the champions maker" - ASR of his name)
title: World Champion LIVE Trading: Exact strategy for t... (header line of the raw file)
instrument_stated: S and P (trade 1), Nasdaq (trade 2), crude oil (trades 3 and 4)
instrument_inferred: none
tick_size: unknown ("two ticks" mentioned in trade 3)
session / time of day: unknown ("day two ... the market opening")
translation_warning: yes (non-native English)
body_chars: 8790
n_decision_rows: 34
n_trades: 4 (one of them a re-entry)
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition ("as long as") |
|---|---|---|---|---|---|---|---|---|
| 1 | 5 | LESSON | - | stop loss | - | "What is much more important than knowing exactly where my trade is going to go? ... the stop loss" | - | none stated |
| 2 | 8 | LESSON | - | - | - | "letting the trades that are running continue to run, that is a great art" | - | none stated |
| 3 | 17 | CONTEXT | - | previous day (S&P) | prior-day profile | "a nice buying tail ... A nice selling tail ... huge volume ... the equilibrium zone" | prior-day profile, tail | none stated |
| 4 | 20 | CONTEXT | - | market opening | open location | "the market opening. Very very very very very far away from the previous day" | prior-day profile, time of day | none stated |
| 5 | 24 | LOCATION | short [inferred: "ran down ... take profit down here"] | value high / buying tail of the prior day | prior-day profile | "I immediately see ah, here was value high. Ah, here was a buying tail" | prior-day profile, VAH, tail | "I assume that a reaction will occur here" |
| 6 | 27 | PROOF (BEFORE) | short | up here | rejection, selling overhang | "the market simply had rejection up here ... an absolute selling overhang" | delta / aggressive sellers [?] ("dynamically recognize") | none stated |
| 7 | 27 | ENTRY | short [inferred] | here | - | "And so I opened my position here." order type unknown | - | none stated |
| 8 | 28 | TARGET_SET | short | value ("where the fair prices are") | prior-day profile | "if we go over this again, there's a high probability we'll run to value" | prior-day profile | "if we go over this again" |
| 9 | 30 | CONTEXT | short | - | speed of the open | "when something is very fast, there's usually no big foundation in between" | time of day, speed | "if there's still a support here ... the market could work through that again" |
| 10 | 33 | CONTEXT | short | - | risk vs plan | "the risk is very manageable and my plan profit run is very very large" | - | none stated |
| 11 | 36 | HOLD | short | - | stop nearly hit | "It also almost stopped me out." | - | none stated |
| 12 | 37 | STOP_MOVE | short | to the high | - | "I decided to also trail the stop loss to the high." [F3] | swing high | none stated; effect: raises the theoretical R:R |
| 13 | 39 | ERROR | short | - | - | "That wasn't the actual risk. The actual risk was a bit higher" (always consult the math of the first trade) | - | none stated |
| 14 | 42 | PROOF (AFTER) | short | up here | volume | "the volumes kept getting lower and lower ... the people up here weren't blasting in like crazy anymore" | volume | none stated |
| 15 | 44 | HOLD | short | - | - | "here I waited patiently" | - | none stated |
| 16 | 45 | CONTEXT | short | - | R:R | "Here the trades risk reward ratio was already at a greater than one" | - | none stated |
| 17 | 47 | LESSON | - | - | hit rate | "for such counter trades, it's usually below 50% and that's why I need long winning streaks" | - | none stated |
| 18 | 48 | EXIT | short | down here | - | "The market then really ran down fortunately giving me my nice take profit down here" ; stated R:R "around four to one" ; exit type target | - | none stated |
| 19 | 50 | CONTEXT | - | Nasdaq | balance | "The market had also made its balance here, played exactly the same game as before." | profile (balance), other market [S&P game] | none stated |
| 20 | 52 | ENTRY | [not stated; "same game"] | here | - | "placed another limit order here in case it picked me up again and it did" ; limit | - | "in case it picked me up again" |
| 21 | 53 | CONTEXT | - | - | R:R | "I had a risk reward ratio of eight here." (stated) | - | none stated |
| 22 | 56 | CONTEXT | long [inferred from "I actually wanted to buy"] | crude oil open and equilibrium | prior-day profile | "Up here was the open ... And down here was the equilibrium again." | prior-day profile, time of day | "the market had opened far above the previous day ... an absolute sign of strength" |
| 23 | 59 | CONTEXT | long | - | fundamentals | "a lot of problems in the Middle East" | news | none stated |
| 24 | 60 | ENTRY | long | "either here or here" | balance zone | "I actually wanted to buy there, either here or here. And that's what I did" ; order type unknown | balance zone, reaction | "a reaction occurred there and another reaction occurred" |
| 25 | 62 | STOP_SET | long | "the level 9246" | - | "I also set my stop loss relatively tight." | profile levels (value area, prior-day POC 9220-9250) | none stated |
| 26 | 69 | ERROR | long | stop price range | - | "I definitely placed my stop loss in a price range that was not smart at the time." | prior-day profile (value area 9220-9250) | none stated |
| 27 | 72 | EXIT | long | - | - | "the market then took me out" ; exit type stop ; "two ticks lower than where my stop loss had been set" [?] | - | none stated |
| 28 | 74 | LESSON | long | - | - | "did the market play a game that was just different from what I had planned? ... no" (stop placement was the mistake) | - | none stated |
| 29 | 75 | ENTRY | long (re-entry) | - | buyer stability | "So I then started a re-entry." ; order type unknown | delta / aggressive buyers [?] | "the market was incredibly stable and started moving in my favor again" |
| 30 | 76 | STOP_SET | long | below the last swing low | swing low | "I then placed my stop loss below the last swing low again." | swing high/low | none stated |
| 31 | 81 | EXIT | long | - | - | "I chose the first exit quite well here." ; exit type unknown ; "the market went much higher" | - | none stated |
| 32 | 88 | LESSON | long | - | - | "the courage to make re-entries immediately when the market does it at the right spot" | - | "when you see that the buyers are actually there" |
| 33 | 92 | REJECT | - | re-entry | - | "is it just a case of me jumping back in because I feel like I have to be part of it again?" (a question he poses as a test) | - | re-enter only with "real proof from dynamic buyers" |
| 34 | 94 | LESSON | - | - | - | "you definitely need to know your key figures" | - | none stated |

## 3.3 Trade blocks
```
TRADE 1 - short [inferred] - rows 5-18 (S and P)
state (day/week): day 2 opens "very very very very far away from the previous day"; previous day: buying tail, selling tail, huge volume, equilibrium zone
location: value high and a buying tail of the prior day ; level type: VAH / tail
leading signal: prior-day profile levels
trigger: rejection and an absolute selling overhang ; entered BEFORE or AFTER proof: after (proof row 6, entry row 7; further proof row 14, falling volume)
entry order type: unknown ; placed before the touch: unknown
initial stop: not stated ; distance: not stated ; % of price: unknown
target: "run to value" / "take profit down here" ; distance: not stated ; stated R:R: "greater than one" then "around four to one"
management: STOP_MOVE row 12 (trailed to the high; actual risk "a bit higher")
exit: take profit hit ; exit type target
rejects: none stated
information sources: prior-day profile, VAH, tail, volume, time of day, speed
outcome: win; no money figure
horizon: unknown
mirror stated?: no - do not assume
TRADE 2 - [side not stated] - rows 19-21 (Nasdaq)
state: balance, "exactly the same game as before"
location: "here" (no level named) ; level type: unknown
leading signal: balance
trigger: limit order placed in case price "picked me up again" ; entered BEFORE or AFTER proof: unknown ; entry order type: limit ; placed before the touch: yes ("in case")
initial stop: not stated ; target: not stated ; stated R:R: "eight"
management: none stated ; exit: not stated ; outcome: "I took that one too" (taken as a win; amount not stated)
mirror stated?: no - do not assume
TRADE 3 - long [inferred] - rows 22-28 (crude oil)
state: opened "far above the previous day", read as strength ; Middle East news
location: balance zone ("either here or here") ; level type: balance zone / value area and prior-day POC 9220-9250
trigger: "a reaction occurred there and another reaction occurred" ; entered BEFORE or AFTER proof: after (two reactions seen)
entry order type: unknown ; placed before the touch: unknown
initial stop: "relatively tight", level 9246 mentioned ; distance: not stated ; % of price: unknown
target: not stated ; stated R:R: not stated
management: none ; exit: stopped out ; exit type stop (two ticks beyond the stop level [?])
rejects: none ; admitted error: stop placed in a price range "that was not smart" (row 26)
outcome: loss; no money figure
mirror stated?: no - do not assume
TRADE 4 - long (re-entry of trade 3) - rows 29-33
state: after the stop-out "the market was incredibly stable and started moving in my favor again"
trigger: buyer stability ; entered AFTER proof (stability seen after the stop-out)
initial stop: "below the last swing low" ; target: not stated
exit: "I chose the first exit quite well here" ; exit type unknown ; later the market "went much higher" ("huge risk reward ratio" in hindsight)
rejects: re-entering only to "be part of it again" (row 33)
mirror stated?: no - do not assume
```

## 3.4 Rejections and conditions
- Row 33: re-entry needs proof from dynamic buyers; wanting to be part of the move is not a reason.
- Row 12 and row 13: trailing the stop raises the theoretical R:R but "the actual risk" is the first trade's math.
- Row 26: the stop belongs where the profile shows structure (value area 9220-9250), not "relatively tight" below it.

## 3.5 Verbatim anchors
> "And so I opened my position here."
**Source GPS: kXhIAug0Gh8 | BEGIN**

> "if we go over this again, there's a high probability we'll run to value"
**Source GPS: kXhIAug0Gh8 | BEGIN**

> "I decided to also trail the stop loss to the high."
**Source GPS: kXhIAug0Gh8 | MIDDLE**

> "The market then really ran down fortunately giving me my nice take profit down here"
**Source GPS: kXhIAug0Gh8 | MIDDLE**

> "placed another limit order here in case it picked me up again and it did"
**Source GPS: kXhIAug0Gh8 | MIDDLE**

> "I actually wanted to buy there, either here or here. And that's what I did"
**Source GPS: kXhIAug0Gh8 | MIDDLE**

> "I also set my stop loss relatively tight."
**Source GPS: kXhIAug0Gh8 | END**

> "I definitely placed my stop loss in a price range that was not smart at the time."
**Source GPS: kXhIAug0Gh8 | END**

> "The market then took me out."
**Source GPS: kXhIAug0Gh8 | END**

> "So I then started a re-entry."
**Source GPS: kXhIAug0Gh8 | END**

> "I then placed my stop loss below the last swing low again."
**Source GPS: kXhIAug0Gh8 | END**

> "I chose the first exit quite well here."
**Source GPS: kXhIAug0Gh8 | END**

> "is it just a case of me jumping back in because I feel like I have to be part of it again?"
**Source GPS: kXhIAug0Gh8 | END**

## 3.6 Ambiguity flags
- Row 5, 18: side of trade 1 is never named; "ran down" and "take profit down here" are the only evidence.
- Row 20: "in case it picked me up again" - read as a second limit order to re-enter at the same area; the side is not stated.
- Row 25: "the level 9246" is a profile level near the stop; whether 9246 is the stop price is not stated.
- Row 27: "two ticks lower than where my stop loss had been set" - unclear whether the market traded two ticks beyond the stop or the fill was two ticks worse.
- Row 6: "dynamically recognize" is not tied to a named indicator.

## 3.7 Falsification flags (5.3)
Method (5.3): each rule claim below was searched against all 102 transcripts in raw_transcripts_canonical for a contradicting passage (patterns: stop placement, target, scalp, trailing and moving stops, short at the top, risk percent, draw down, re-entry, hit rate, adding); a hit counts only if it is in a Tom-set transcript and speaks to the same variable. Starred ids in the corpus search are the Tom set (57 ids).
Claims searched (5): C1 stop at structure, not "relatively tight" below it (rows 25-26); C2 trail the stop to the high (row 12); C3 re-entry only with proof from dynamic buyers (rows 29, 33); C4 counter trades win less than half the time (row 17); C5 a reaction is expected at the prior-day value high and buying tail (row 5).
Result: 1 flagged (C2), 4 with no contradiction found (C1, C3, C4, C5).
- [F3] row 12, tension (trade-dependent): "In this case, I don't do that" about trailing [T/k0zm5NYn0IQ:19@7033]; 4MoNjEQ2Dd8 says moving the stop before an "opposite" range exists "doesn't make sense" [T/4MoNjEQ2Dd8:19@12857]; moves the stop up after adding [T/n7ZSkjb7JXs:19@4807].
- C3 is supported: "Otherwise, I would never have made this re-entry." [T/ujedEcmvBMk:13@6670] (after aggressive selling was seen); "And it was worth it to make a re-entry here." [T/k0zm5NYn0IQ:19@17276].
## 7 self-check
1 ENTRY rows: 4 (rows 7, 20, 24, 29); trade blocks: 4. 2 Fields filled. 3 Last row pos% 94 (the last 6 percent is sign-off). 4 Checker line below.

PASS: 0 problem(s)
