# V2 extract WSCIURybK3U (round 2, 5.2: first by risk/stop/target/size frequency)

Session: MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio. Method: EXTRACTION_METHOD_V2.md. Read in 7 chunks of about 2,000 characters.
Frequency 16.2 per 1,000 words (rank 1 of the Tom-set transcripts). The video is a risk-management lecture: no trade is taken; plans are illustrations.

## 3.1 Header
```
video_id: WSCIURybK3U
trader: Tom (corpus mapping; the transcript says "I'm Thomas Forgert. I'm the champions maker" - ASR of his name)
title: Trading World Champion Reveals: The #1 Reason Tra... (header line of the raw file)
instrument_stated: Avis short squeeze (stock), DAX future, S&P future, FDXM / FDXS (DAX mini and smallest DAX contract)
instrument_inferred: none
tick_size: unknown (DAX "5 euros per tick" for FDXM is stated at pos 63)
session / time of day: unknown ("the DAX future, which many like to trade in the mornings")
translation_warning: no flag in the text (non-native English)
body_chars: 12681
n_decision_rows: 24
n_trades: 0 (2 illustrations)
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition ("as long as") |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 | LESSON | - | - | - | "90% of traders loses 90% of their money in 90 days. Why? Because they have no clear risk management." | - | none stated |
| 2 | 8 | REJECT | short | "short here, short here, short here" | - | "there are many who go short here, short here, short here. And I used to do that, too" | - | none stated |
| 3 | 9 | LESSON | - | - | - | "The first and most important insight is always wait for a real setup so that you have reference values." | - | none stated |
| 4 | 16 | LESSON | - | - | - | "you need a stop loss, and you need a predefined target where you end your trade" | - | none stated |
| 5 | 18 | STOP_SET (illustration) | short | 730 | - | "our stop loss is at 730, my entry at 630, and my profit taking at 230" | - | none stated |
| 6 | 19 | ENTRY (illustration) | short | 630 | - | entry 630 (illustration; order type unknown) | - | none stated |
| 7 | 19 | TARGET_SET (illustration) | short | 230 | - | profit taking at 230; "I have a risk-reward ratio of four" (stated) | - | none stated |
| 8 | 20 | LESSON | - | - | size | 1% risk of 100,000 euros: "I can short 12 shares if I take a 1% risk"; at 5% risk "58 shares" [as transcribed] | [new source] position-size table | none stated |
| 9 | 21 | LESSON | - | - | hit rate | counter-trading strategy, win rate 30%; "need a win rate of 20% to theoretically make money" at R:R four | - | none stated |
| 10 | 33 | LESSON | - | - | size | simulation, 5% risk, 100 trades: maximum draw down 43.7% and 46.8%; "about an 85% return just to get back to zero" | [new source] equity curve simulator | none stated |
| 11 | 40 | LESSON | - | - | - | "you should never allow more than a 20% drawdown of your trading capital" (a 20% loss needs a 25% gain) | - | none stated |
| 12 | 47 | LESSON | - | - | size | "1% risk per trade is often too much": 20 consecutive losses are "over 20%" | - | none stated |
| 13 | 52 | STOP_SET (illustration) | short | above the last supposed high | swing high | "I set my stop loss above the last supposed high" (DAX future short idea) [F5] | swing high/low | "Whether that makes sense or not is another matter. That's what I'm predefining." |
| 14 | 53 | TARGET_SET (illustration) | short | exit "down here" | - | stop 24,220, exit 24,120 (entry not stated) | - | none stated |
| 15 | 55 | REJECT | - | profit taking | - | "many fail because they take profits as soon as there's a tiny twitch" | - | none stated |
| 16 | 58 | LESSON | - | DAX | size | with 100,000 euros and a stop of 35 ticks "you're not even allowed to trade the DAX future ... your loss would be greater than 0.5%" | [new source] position-size table | none stated |
| 17 | 59 | LESSON | - | - | size | 0.5% risk per trade comes from the strategy's key figures: more risk would give "a possible drawdown in sequence of more than 20%" | - | none stated |
| 18 | 62 | LESSON | - | DAX | size | 1% = 1,000 euros against a one-contract stop of 875 euros; use FDXM (5 euros per tick) or FDXS (28 units) "but only if the corresponding fees are right" | [new source] fee table | none stated |
| 19 | 68 | LESSON | - | - | - | cost-of-living calculator: 4,000 euros, 18 trading days, 28% tax: "12.0 on average" points per day to build wealth | [new source] calculator | none stated |
| 20 | 77 | LESSON | - | - | - | "very few people are even in a position to truly know ... what position size they are actually allowed to take" | - | none stated |
| 21 | 80 | REJECT | - | early exit | - | "they very often exit their trades much too early" (average R:R of 1:1 "is often the reality") | - | none stated |
| 22 | 83 | LESSON | - | - | size | hit rate 60%, 1:1, 4 trades a day, 800 trades a year, 0.5% risk: low draw downs "from a real win probability of 60% and the fact that you really always stick to your corresponding stop losses" | [new source] equity curve simulator | none stated |
| 23 | 91 | LESSON | - | - | size | "two contracts or one contract in the S&P future because you are only allowed to take 0.5% or even less risk per trade" | - | none stated |
| 24 | 96 | LESSON | - | - | - | "Great opportunities are not always the best trades unless your risk is huge." | - | none stated |

## 3.3 Trade blocks
No trade was taken. Illustrations:
```
ILLUSTRATION 1 - short - rows 5-7 (Avis short squeeze, dollars): entry 630, stop 730, exit 230; stated R:R four; arithmetic (mine): risk 100, reward 400, 4.0. 1% risk = 12 shares, 5% = 58 shares [as transcribed]. mirror stated?: no - do not assume
ILLUSTRATION 2 - short - rows 13-14 (DAX future): stop above the last supposed high at 24,220, exit 24,120; entry not stated; stop distance "35 ticks"; at 100,000 euros a 35-tick stop breaks the 0.5% limit. mirror stated?: no - do not assume
```

## 3.4 Rejections and conditions
- Row 2: no shorting "here, here, here" on a sense that price is too expensive; wait for a real setup (row 3).
- Row 15 and 21: no taking profit at "a tiny twitch"; no early exits that cut the planned R:R to 1:1.
- Rows 11, 12, 17: the per-trade risk is capped by the 20% maximum draw down, which gives 0.5% for his strategy.

## 3.5 Verbatim anchors
> "there are many who go short here, short here, short here. And I used to do that, too"
**Source GPS: WSCIURybK3U | BEGIN**

> "our stop loss is at 730, my entry at 630, and my profit taking at 230"
**Source GPS: WSCIURybK3U | BEGIN**

> "Entry 630, stop loss 730, exit 230, the currency is US dollars."
**Source GPS: WSCIURybK3U | BEGIN**

> "It tells me I have a risk-reward ratio of four."
**Source GPS: WSCIURybK3U | BEGIN**

> "And here I set my stop loss above the last supposed high."
**Source GPS: WSCIURybK3U | MIDDLE**

> "This is where many fail because they take profits as soon as there's a tiny twitch."
**Source GPS: WSCIURybK3U | MIDDLE**

> "they very often exit their trades much too early"
**Source GPS: WSCIURybK3U | END**

## 3.6 Ambiguity flags
- Rows 5-7: prices 630/730/230 are given in US dollars for a stock; the side is "short" from "I can short 12 shares" at row 8.
- Row 8: "58 shares" at 5% risk is out of proportion to 12 shares at 1% (a factor of 4.8, not 5) as transcribed; not corrected.
- Rows 13-14: the DAX entry is not stated; "35 ticks" and the 24,220 / 24,120 levels do not fix an entry price.
- Row 19: "12.0" is spoken as "a result of 12.0 on average"; the unit (points per day) is clear only from the next sentence.

## 3.7 Falsification flags (5.3)
Method (5.3): each rule claim below was searched against all 102 transcripts in raw_transcripts_canonical for a contradicting passage (patterns: stop placement, target, scalp, trailing and moving stops, short at the top, risk percent, draw down, re-entry, hit rate, adding); a hit counts only if it is in a Tom-set transcript and speaks to the same variable.
Claims searched (6): C1 a stop and a predefined target are required (row 4); C2 wait for a real setup (row 3); C3 0.5% risk per trade follows from the draw-down cap (row 17); C4 never allow more than a 20% draw down (row 11); C5 do not take profits at a tiny twitch (row 15); C6 stop above the last supposed high (row 13).
Result: 1 flagged (C6), 5 with no contradiction found (C1-C5).
- [F5] row 13, direct contradiction with "It doesn't belong above the high." [T/yRvMW6lgN1o:19@6182]. The row is an illustration he introduces with "Whether that makes sense or not is another matter", so it is a naive stop, not his rule.
- C4 is supported: "you must never have a strategy that has a drawdown of more than 20%" [T/hQ8sOq67x5o:7@3516].
## 7 self-check
1 ENTRY rows: 1 (illustration); trade blocks: 0, 2 illustrations. 2 Fields filled. 3 Last row pos% 96. 4 Checker line below.

PASS: 0 problem(s)
