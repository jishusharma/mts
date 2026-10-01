# V2 extract UrZ4vpHJ97g (round 2, method audit 5.1b: not extracted before)

Session: MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio. Method: EXTRACTION_METHOD_V2.md (MyTradingSys/research/fast_track_2026-09-27/). Read in 11 chunks of about 2,000 characters.
This video is a money-management lecture, not a trading session: no trade is taken. Illustrations (hypothetical plans) are logged with the row types the method offers and marked "(illustration)".

## 3.1 Header
```
video_id: UrZ4vpHJ97g
trader: Tom (named in the text: "Tom says that you can earn much much more", "Tom, tell us more about this")
title: World Champion reveals: The PERFECT risk-reward ratio (RRR) ... (header line of the raw file)
instrument_stated: DAX future (illustrations), S&P (one illustration)
instrument_inferred: none
tick_size: unknown (a "40 ticks" stop is used with the DAX; tick value not stated)
session / time of day: unknown
translation_warning: yes (non-native English, auto-captioned)
body_chars: 20103
n_decision_rows: 27
n_trades: 0 (3 illustrations)
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition ("as long as") |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | LESSON | - | - | - | "the real and easy mathematic from trading ... risk of reward of hit rates" | - | none stated |
| 2 | 9 | LESSON | - | - | - | money management has "three basic elements": hit rate, riskreward ratio, capital size | - | none stated |
| 3 | 5 | REJECT | - | risk per trade | - | "think they can always enter the market with 1% risk per trade or even more. No, that's absolutely wrong." | [new source] strategy key figures | none stated |
| 4 | 10 | REJECT | - | target | - | "They haven't defined a target in advance at all." | - | none stated |
| 5 | 12 | STOP_SET | long (example) | below the low | swing low | "The next step is the stop loss, which I always place below the low." | swing high/low | "A stop loss belongs where I would expect the opposite of what I'm aiming for" |
| 6 | 13 | TARGET_SET (illustration) | long | target and stop "set at 19460" [?] | - | "So our target and our stop loss are simply set at 19460." [?] R:R of the sample "3.5" | - | none stated |
| 7 | 14 | LESSON | - | - | size | "How many units am I allowed to trade?" with "a risk up here of 1%" | [new source] position-size table | none stated |
| 8 | 19 | LESSON | - | DAX | size | "a risk of 3% per trade ... three DAX future contracts" (illustration) | [new source] sizing table | none stated |
| 9 | 20 | LESSON | - | DAX | size | "0.5% per trade and ... a stop-loss of 40 ticks, I can't even trade a DAX future anymore"; use a smaller product | [new source] sizing table | none stated |
| 10 | 29 | LESSON | - | - | - | a 20% loss needs 25% to recover; a 35% draw down needs "between 42% and 66%", "a solid 50%" | - | none stated |
| 11 | 33 | LESSON | - | - | - | "You should assign a maximum draw down of 20% to your entire trading business." | - | none stated |
| 12 | 40 | LESSON | - | hit rate | - | hit rate 35% "not unusual if you're doing intraday swing trading" | - | none stated |
| 13 | 41 | REJECT | - | target | - | never delete the predefined target [F6] | - | "unless in the meantime you've used other mathematical approaches" |
| 14 | 44 | LESSON | - | - | size | 35% hit rate, "3.5 to1", 1% risk, 100 trades, 20 runs: draw downs 17.3%, 20.3%, 26% -> above 20% | [new source] equity curve simulator | none stated |
| 15 | 52 | LESSON | - | - | size | 0.8% still over 20%; "that's how I arrived at the figure of 0.5%" | [new source] equity curve simulator | none stated |
| 16 | 55 | LESSON | - | - | - | high hit rates need modest R:R; low hit rates need "really high" R:R | - | none stated |
| 17 | 56 | ENTRY (illustration) | short [?] | DAX | - | "This is where I enter for example 20 points in the DAX stop loss 20 points lower." (a short stop would be higher: [?]) | - | none stated |
| 18 | 57 | STOP_SET (illustration) | - | S&P | - | "$6 up and $4 stop-loss"; "typical momentum trades ... hit rate between 65 and 70%" | - | none stated |
| 19 | 58 | TARGET_SET (illustration) | short | 100 points lower | - | "a 100 point profit distance and a 20 point loss distance which gives a riskreward ratio of five" | - | "with a hit rate of 20% I would mathematically make money" |
| 20 | 61 | LESSON | - | - | - | "many trader colleagues who have hit rates around 50% with riskreward ratios of 2 or three" | - | none stated |
| 21 | 63 | LESSON | - | - | - | "Typical breakout trading riskreward ratio of 1.1" with a 70% hit rate, 200 trades, 1% risk, draw down 10 to 11% | [new source] equity curve simulator | none stated |
| 22 | 68 | LESSON | - | - | size | swing trading: "0.7% per trade with a maximum draw down of 12.9%"; "never more than 20%"; "2.5 to 1" | [new source] equity curve simulator | none stated |
| 23 | 72 | LESSON | - | - | size | the 3.5 to 1 sample with 0.7% risk: largest draw down 14%; "you can lose up to 15 trades in a row" | [new source] equity curve simulator | none stated |
| 24 | 79 | LESSON | - | - | - | intraday swing hit rate "truly around 38 to 42%", draw down about 12%, 500 trades vs 200 for breakout | - | none stated |
| 25 | 82 | LESSON | - | - | - | cost-of-living calculator (5 points per point value, 18 trading days): "12 full points of profit every single day" to break even | [new source] calculator | none stated |
| 26 | 90 | LESSON | - | - | - | "to actually build wealth, you need to earn an average of 20 points per day" | [new source] calculator | none stated |
| 27 | 94 | LESSON | - | - | - | "determine an expected value per trade" and "never having a draw down of more than 20%" | - | none stated |

## 3.3 Trade blocks
No trade was taken, so there is no first ENTRY to final EXIT. Illustrations (plans, not trades):
```
ILLUSTRATION A - long - rows 5-6 : stop "below the low"; target and stop "at 19460" [?]; stated R:R 3.5; hit rate 35%; 1% then 0.5-0.7% risk. mirror stated?: n/a
ILLUSTRATION B - short [?] - rows 17-19 : DAX, enter, stop 20 points, target 100 points, stated R:R five, breakeven hit rate 20%. mirror stated?: no - do not assume
ILLUSTRATION C - momentum - row 18 : S&P "$6 up and $4 stop-loss", hit rate 65-70%, typical breakout R:R 1.1 (row 21). mirror stated?: no - do not assume
```

## 3.4 Rejections and conditions
- Row 3: no fixed 1% (or more) risk per trade; the per-trade risk comes from the strategy's key figures and a 20% draw down limit (rows 11, 14, 15).
- Row 4: no entry without a target defined in advance. Row 13: never delete the predefined target, except when other mathematical approaches replace it.
- Row 5 condition: the stop belongs "where I would expect the opposite of what I'm aiming for".

## 3.5 Verbatim anchors
> "think they can always enter the market with 1% risk per trade or even more. No, that's absolutely wrong."
**Source GPS: UrZ4vpHJ97g | BEGIN**

> "They haven't defined a target in advance at all."
**Source GPS: UrZ4vpHJ97g | BEGIN**

> "The next step is the stop loss, which I always place below the low."
**Source GPS: UrZ4vpHJ97g | BEGIN**

> "So our target and our stop loss are simply set at 19460."
**Source GPS: UrZ4vpHJ97g | BEGIN**

> "which is why you must never ever delete this predefined target unless in the meantime you've used other mathematical approaches for yourself"
**Source GPS: UrZ4vpHJ97g | MIDDLE**

> "This is where I enter for example 20 points in the DAX stop loss 20 points lower."
**Source GPS: UrZ4vpHJ97g | MIDDLE**

> "$6 up and $4 stop-loss"
**Source GPS: UrZ4vpHJ97g | MIDDLE**

> "a 100 point profit distance and a 20 point loss distance which gives a riskreward ratio of five"
**Source GPS: UrZ4vpHJ97g | MIDDLE**

## 3.6 Ambiguity flags
- Row 6: "I need a set takerit" and "set at 19460" for both target and stop are garbled; target and stop prices are not separately stated.
- Row 17: "stop loss 20 points lower" next to "a quick short breakout" contradicts a short stop above entry; side and stop direction are unresolved.
- Rows 10, 25, 26: "between 42% and 66%" and the points-per-day figures come from tools shown on screen; the transcript gives the results, not the inputs (account size, tax, fees partly "fictitious").
- Row 17-19: the "20 points" figures are illustrations; instrument tick size is not stated, so no percent-of-price is computed.

## 3.7 Falsification flags (5.3)
Method (5.3): each rule claim below was searched against all 102 transcripts in raw_transcripts_canonical for a contradicting passage (patterns: stop placement, target, scalp, trailing and moving stops, short at the top, risk percent, draw down, re-entry, hit rate, adding); a hit counts only if it is in a Tom-set transcript and speaks to the same variable.
Claims searched (6): C1 stop below the low (row 5); C2 never delete the predefined target (row 13); C3 no fixed 1% risk per trade (row 3); C4 maximum 20% draw down (row 11); C5 risk per trade is set per strategy, 0.5% and 0.7% (rows 15, 22); C6 define the target in advance (row 4).
Result: 1 flagged (C2), 5 with no contradiction found (C1, C3, C4, C5, C6).
- [F6] row 13, tension: he asks whether to keep or move predefined targets as an open, measurable question: "If you have predefined profit  targets via a limit order, do you stick to them or do you move them?" [T/UOBgXV20yCM:7@177]; and he leaves a trade without trailing "In this case" but trails in others [T/k0zm5NYn0IQ:19@7033]. The exception clause in row 13 ("unless ... other mathematical approaches") already covers part of this.
- C4 supported by [T/hQ8sOq67x5o:7@3516] and row 11 of WSCIURybK3U_v2.md.
## 7 self-check
1 ENTRY rows: 1 (illustration); trade blocks: 0, 3 illustrations (no trade was taken). 2 Fields filled. 3 Last row pos% 94 (the closing 5 percent is sign-off text). 4 Checker line below.

PASS: 0 problem(s)
