# V2 extract 0jM5Y31YJak (Fabio Valentini)

Session: V2 extraction worker, method EXTRACTION_METHOD_V2.md. Read in 4 chunks of about 2,000 characters (body 7,453 chars). One summary-style recap of a competition session: one trading day, three trades (the first with positions 1-3), all short, all winners; the video is one winning session.

## 3.1 Header
```
video_id: 0jM5Y31YJak
trader: Fabio Valentini (the transcript: "the market told me Fabio")
title: not in the header (header holds only "# Video ID: 0jM5Y31YJak" and the source file name fabervaale_0jM5Y31YJak_raw.txt)
instrument_stated: NASDAQ ("I just capitalize on the market collapsing on NASDAQ"); contract not stated
instrument_inferred: none
tick_size: unknown
session / time of day: before the session start "almost uh 12 uh central central European time"; "I closed the session around four"; day "30 of December" (hedged, "if I'm not wrong"), final days of a trading competition
translation_warning: no flag in the header; ASR-like artifacts are visible (for example "quarterly world cup of robins" [?], "deep trades model" for the big trades indicator)
body_chars: 7453
n_decision_rows: 48
n_trades: 3
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition ("as long as") |
|---|---|---|---|---|---|---|---|---|
| 1 | 5 | CONTEXT | - | before session start | clock | "it was almost uh 12 uh central central European time" | time of day | none stated |
| 2 | 5 | CONTEXT | - | balance | price action | "we had some kind of balance here" | prior/today profile (balance) | none stated |
| 3 | 7 | CONTEXT | - | no direction | price action | "We didn't had a a clear direction here." | price action | none stated |
| 4 | 11 | REJECT | - | price-only reading | price action | "you you just think that you need to wait" | price action vs volume | "volume was telling us something different"; rejects waiting on price alone |
| 5 | 17 | LESSON | - | - | volume | "there is a big difference between watching only price and adding volume to your narratives" | volume | none stated |
| 6 | 20 | CONTEXT | - | fair value in the middle | profile | "if we plot a profile for the current situation we can just see balance" | today's profile | none stated |
| 7 | 28 | PROOF (BEFORE) | short | - | cumulative volume delta vs price | "the market is clearly building pressure down" | delta (cumulative volume delta) | "this is only the first milestone for my trading model" (needs the second confirmation) |
| 8 | 34 | CONTEXT | short | - | cumulative volume delta | "we were distributing and we were ready to explode short" | delta (cumulative volume delta) | "this is not enough" |
| 9 | 42 | PROOF (BEFORE) | short | this candle | big trades indicator; price | "follow up on volume and confirmation from price was exactly this candle" | [new source] big trades indicator (proprietary); delta; price candle (TF not stated) | balance condition until then |
| 10 | 43 | PROOF (BEFORE) | short | - | big trades; price | "the market told me Fabio we are going down the volume pressure is down" | [new source] big trades indicator; price action follow-through | none stated |
| 11 | 45 | ENTRY | short | this candle | - | "So I have the first position here" | big trades; delta; price follow-through | none stated; order type unknown (market/limit/stop not stated) |
| 12 | 46 | LESSON | - | - | - | "my way of trading is keeping draw down really low" | - | none stated |
| 13 | 47 | LESSON | - | - | - | "building uh the profit for the day and then risking again the profit" | - | none stated |
| 14 | 50 | PROOF (AT entry candle) | short | - | distribution then breakdown | "This is the first confirmation that we are in a condition of out of balance." | today's profile; price action | "We we were in distribution for all the session. Now we are starting to go down." |
| 15 | 53 | CONTEXT | - | - | - | "this was 30 of December" | - | "if I'm not wrong" (date hedged) |
| 16 | 55 | PROOF (AFTER) | short | - | price | "the market exploded in my direction" | price action | none stated |
| 17 | 55 | STOP_MOVE | short | break even | - | "I put my stop loss to break even" | price action; delta/big trades | after the market "exploded in my direction" |
| 18 | 56 | STOP_SET | short | no stop stated | - | "The first stop loss was here." | - | no stop stated (chart pointer only; may refer to the break-even stop) |
| 19 | 58 | EXIT | short | "around here" (no price) | - | "the first position was closed around here" | - | none stated; reason not stated |
| 20 | 59 | LESSON | short | - | - | "almost 1 to three even more 1:5 risk-to-reward ratio" | - | stated realised R:R of the first position |
| 21 | 60 | LESSON | short | - | big trades/sellers | "another confirmation that the sellers are pushing the price down" | aggressive sellers (big trades) | after this confirmation: stop to break even |
| 22 | 62 | LESSON | short | - | - | "close the first trade and open a second one" | - | option stated: "I can consider"; condition = the confirmation in the previous row |
| 23 | 63 | ADD | short | - | trend | "continue to add to my position in direction of the trend" | - | option stated, after the confirmation of sellers pushing price down; not tied to a price |
| 24 | 65 | ADD | short | "this was the second position" (no price) | - | "This was the second position." | - | none stated; add or separate new position not stated |
| 25 | 66 | ADD | short | "third position" (no price) | - | "This was the third position." | - | none stated; add or separate new position not stated |
| 26 | 66 | EXIT | short | "here" (no price) | big trades | "I closed all these trades here in the second accumulation phase" | big trades | reason: big trades no longer pushing price down |
| 27 | 67 | PROOF (reason given after the exit statement) | short | second accumulation phase | big trades | "the big trades are not pushing anymore the price down" | big trades; delta | none stated |
| 28 | 68 | CONTEXT | short | second accumulation phase | big trades | "We are in a redistribution phase." | big trades | none stated |
| 29 | 70 | REJECT | - | accumulation vs distribution | price action | "guess if we are in a accumulation or distribution only using price action" | price action | reason: "this is something that is not really convenient" |
| 30 | 72 | LESSON | short | - | - | "I took some profit and I use half of this profit to risk again" | - | half of the realised profit is risked again |
| 31 | 73 | PROOF (BEFORE) | short | - | price | "You see again the the price action breaking down." | price action | none stated |
| 32 | 74 | PROOF (BEFORE) | short | - | big trades | "You see again big trades in the direction of the trend" | big trades | none stated |
| 33 | 75 | CONTEXT | short | - | auction market theory | "we know that this is a sell model day" | [new source] auction market theory day-type read | none stated |
| 34 | 76 | ENTRY | short | no price | - | "and we continue to sell" | big trades; price action | none stated; order type unknown |
| 35 | 76 | EXIT | short | no price | - | "this was another huge takeprofit" | - | none stated; level not stated; exit type unknown |
| 36 | 77 | LESSON | short | - | - | "I use part of the profit in this position" | - | part of the open profit funds the size of this position |
| 37 | 78 | STOP_MOVE | short | not stated | - | "five different position that were trailed as the market was moving" | - | trailing as price moved; levels and reasons not stated; summary |
| 38 | 80 | CONTEXT | - | - | clock | "I closed the session around four" | time of day | none stated |
| 39 | 80 | ENTRY | short | no price | market breaking down | "Another position that I took was this position" | big trades; footprint | none stated; order type unknown; side from later rows |
| 40 | 82 | PROOF (timing vs entry not stated) | short | - | big trades; price | "I see that the big trades is holding that the price is trying to retrace" | big trades; price action | none stated |
| 41 | 89 | PROOF (timing vs entry not stated) | short | this exact candle | delta profile footprint; cumulative volume delta; volume spread analysis | "the result of the price for a pressure in by delta was almost zero" | footprint; delta; [new source] volume spread analysis; absorption | none stated |
| 42 | 90 | PROOF (timing vs entry not stated) | short | - | absorption | "this is a confirmation that the buyers are punching a wall" | absorption; delta | none stated |
| 43 | 91 | LESSON | short | - | - | "I want to be short in this position" | - | none stated |
| 44 | 91 | ADD | short | no price | - | "So this was again a short position again a short position" | - | none stated; two further short positions, whether adds or new not stated |
| 45 | 94 | STOP_MOVE | short | risk to zero (level not stated) | big traders | "put the risk to zero to put your position to zero" | big trades / aggressive sellers; low of the day | "as soon as the market approach the all-time low for the day you see big traders sell continuing to push down" |
| 46 | 95 | EXIT | short | low of the day | - | "I took profit for this position at this level" | - | none stated; manual take-profit, no level number |
| 47 | 96 | CONTEXT | short | low of the day | - | "That was the low of the day" | - | none stated |
| 48 | 97 | REJECT | short | - | - | "I didn't continue to load my position during the evening" | - | reason: "I was sitting at a huge profit for the day" |

## 3.3 Trade blocks
```
TRADE 1 - short - rows 11-28
state (day/week): "balance", "We didn't had a a clear direction here", then "out of balance"; "super directional session"; "we were in distribution for all the session"; later "a sell model day" (row 33)
location: no price level named; he enters "on this candle" where volume follow-up and price confirmed (row 9) ; level type: unknown
leading signal: cumulative volume delta showing pressure down while price was in balance (rows 7-8)
trigger: volume follow-up plus price confirmation on one candle (rows 9-10) ; entered BEFORE or AFTER proof: after (his stated reason is the volume pressure and the price follow-through on that candle; exact order inside the candle not stated)
entry order type: unknown ; placed before the touch: unknown
initial stop: no stop stated (row 18 is a chart pointer only) ; distance: not stated ; % of price: unknown
target: not stated ; distance: not stated ; stated R:R: "almost 1 to three even more 1:5" realised on the first position (row 20)
management: STOP_MOVE row 17 (to break even, after the market "exploded in my direction"); option stated rows 22-23 (close and reopen with the profit, or add in the direction of the trend); ADD rows 24,25 (second and third position, add or separate not stated); first position closed row 19
exit: "I closed all these trades here in the second accumulation phase" because "the big trades are not pushing anymore the price down" (rows 26-28, reason spoken right after the exit statement) ; exit type: manual
rejects: row 4 reading the day from price alone / waiting; row 29 guessing accumulation or distribution from price action only (reason: not convenient)
information sources: time of day, today's profile, delta (cumulative volume delta), [new source] big trades indicator, price action follow-through, aggressive sellers
outcome: first position "almost 1 to three even more 1:5" risk-to-reward; the group was closed with profit (amount not stated)
horizon: from the break of balance after "12" CET until the second accumulation phase (no minutes stated)
mirror stated?: no - do not assume

TRADE 2 - short - rows 30-36
state (day/week): "again ... the price action breaking down", "a sell model day" (auction market theory)
location: no price level named ; level type: unknown
leading signal: price action breaking down again and big trades in the direction of the trend (rows 31-32)
trigger: "we continue to sell" (row 34) ; entered BEFORE or AFTER proof: after (the two "you see again" rows are read first)
entry order type: unknown ; placed before the touch: unknown
initial stop: no stop stated ; distance: not stated ; %% of price: unknown
target: not stated ; distance: not stated ; stated R:R: unknown
management: size funded by profit: "I use half of this profit to risk again" (row 30), "I use part of the profit in this position" (row 36); stop trailing in summary only, row 37 ("five different position that were trailed")
exit: "this was another huge takeprofit" (row 35) ; exit type: unknown (take profit, no level or reason beyond that); whether it is one trade or part of the position group is not stated
rejects: none in this trade
information sources: price action, big trades, auction market theory day-type read
outcome: "huge takeprofit" (no figure)
horizon: until the session close "around four" (row 38)
mirror stated?: no - do not assume

TRADE 3 - short - rows 39-48
state (day/week): "the market is breaking down"; "another model that I use"
location: no price level named ; level type: unknown (the stop-to-zero happens near "the all-time low for the day")
leading signal: big trades holding while price tries to retrace (row 40)
trigger: delta pressure with almost zero price result, "the buyers are punching a wall" (rows 41-42) ; entered BEFORE or AFTER proof: unknown (the position is named first, the footprint zoom explains it afterwards)
entry order type: unknown ; placed before the touch: unknown
initial stop: no stop stated ; distance: not stated ; %% of price: unknown
target: not stated ; distance: not stated ; stated R:R: unknown
management: ADD row 44 ("again a short position again a short position"); STOP_MOVE row 45 (risk to zero when big traders keep selling as price approaches the low of the day)
exit: "I took profit for this position at this level. That was the low of the day" (row 46) ; exit type: manual
rejects: row 48 no more loading during the evening (reason: already sitting at a huge profit for the day)
information sources: big trades, footprint (delta profile), cumulative volume delta, [new source] volume spread analysis, absorption
outcome: "my most profitable session on the World Trading Cup" (day figure not stated; competition result "total performance of 350% over 9 months")
horizon: not stated
mirror stated?: no - do not assume
```

## 3.4 Rejections and conditions
- Row 4: waiting on price alone ("you just think that you need to wait"); volume told something different.
- Row 29: guessing accumulation or distribution "only using price action"; "not really convenient".
- Row 48: no more loading during the evening because the day was already at a huge profit.
- Row 17: stop to break even after the market exploded in his direction; row 21: the rule "when the market is giving me another confirmation that the sellers are pushing the price down".
- Row 26: exit all when the big trades no longer push price down (redistribution).
- Row 45: risk to zero when big traders keep selling as price approaches the low of the day.
- Row 7: first milestone only ("this is not enough"): the cumulative volume delta needs a second confirmation (big trades) before the position.

## 3.5 Verbatim anchors
> "it was almost uh 12 uh central central European time"
**Source GPS: 0jM5Y31YJak | BEGIN**

> "we had some kind of balance here"
**Source GPS: 0jM5Y31YJak | BEGIN**

> "We didn't had a a clear direction here."
**Source GPS: 0jM5Y31YJak | BEGIN**

> "you you just think that you need to wait"
**Source GPS: 0jM5Y31YJak | BEGIN**

> "there is a big difference between watching only price and adding volume to your narratives"
**Source GPS: 0jM5Y31YJak | BEGIN**

> "if we plot a profile for the current situation we can just see balance"
**Source GPS: 0jM5Y31YJak | BEGIN**

> "the market is clearly building pressure down"
**Source GPS: 0jM5Y31YJak | BEGIN**

> "we were distributing and we were ready to explode short"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "follow up on volume and confirmation from price was exactly this candle"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "the market told me Fabio we are going down the volume pressure is down"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "So I have the first position here"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "my way of trading is keeping draw down really low"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "building uh the profit for the day and then risking again the profit"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "This is the first confirmation that we are in a condition of out of balance."
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "this was 30 of December"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "the market exploded in my direction"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "I put my stop loss to break even"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "The first stop loss was here."
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "the first position was closed around here"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "almost 1 to three even more 1:5 risk-to-reward ratio"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "another confirmation that the sellers are pushing the price down"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "close the first trade and open a second one"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "continue to add to my position in direction of the trend"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "This was the second position."
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "This was the third position."
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "I closed all these trades here in the second accumulation phase"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "the big trades are not pushing anymore the price down"
**Source GPS: 0jM5Y31YJak | END**

> "We are in a redistribution phase."
**Source GPS: 0jM5Y31YJak | END**

> "guess if we are in a accumulation or distribution only using price action"
**Source GPS: 0jM5Y31YJak | END**

> "I took some profit and I use half of this profit to risk again"
**Source GPS: 0jM5Y31YJak | END**

> "You see again the the price action breaking down."
**Source GPS: 0jM5Y31YJak | END**

> "You see again big trades in the direction of the trend"
**Source GPS: 0jM5Y31YJak | END**

> "we know that this is a sell model day"
**Source GPS: 0jM5Y31YJak | END**

> "and we continue to sell"
**Source GPS: 0jM5Y31YJak | END**

> "this was another huge takeprofit"
**Source GPS: 0jM5Y31YJak | END**

> "I use part of the profit in this position"
**Source GPS: 0jM5Y31YJak | END**

> "five different position that were trailed as the market was moving"
**Source GPS: 0jM5Y31YJak | END**

> "I closed the session around four"
**Source GPS: 0jM5Y31YJak | END**

> "Another position that I took was this position"
**Source GPS: 0jM5Y31YJak | END**

> "I see that the big trades is holding that the price is trying to retrace"
**Source GPS: 0jM5Y31YJak | END**

> "the result of the price for a pressure in by delta was almost zero"
**Source GPS: 0jM5Y31YJak | END**

> "this is a confirmation that the buyers are punching a wall"
**Source GPS: 0jM5Y31YJak | END**

> "I want to be short in this position"
**Source GPS: 0jM5Y31YJak | END**

> "So this was again a short position again a short position"
**Source GPS: 0jM5Y31YJak | END**

> "put the risk to zero to put your position to zero"
**Source GPS: 0jM5Y31YJak | END**

> "I took profit for this position at this level"
**Source GPS: 0jM5Y31YJak | END**

> "That was the low of the day"
**Source GPS: 0jM5Y31YJak | END**

> "I didn't continue to load my position during the evening"
**Source GPS: 0jM5Y31YJak | END**

> "as soon as the market approach the all-time low for the day you see big traders sell continuing to push down"
**Source GPS: 0jM5Y31YJak | END**

> "I was sitting at a huge profit for the day"
**Source GPS: 0jM5Y31YJak | END**

> "This is only the first milestone for my trading model"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "this is something that is not really convenient"
**Source GPS: 0jM5Y31YJak | END**

> "my most profitable session on the World Trading Cup"
**Source GPS: 0jM5Y31YJak | END**

> "I can consider to close the first trade"
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "a total performance of 350% over 9 months"
**Source GPS: 0jM5Y31YJak | BEGIN**

## 3.6 Ambiguity flags
- Row 18: "The first stop loss was here" has no price or distance and follows the break-even move (row 17); it may mean the break-even stop, not an initial stop. Initial stop: no stop stated for any trade.
- Row 19: "went to break even immediately" and "closed around here" with a realised 1:3 to 1:5: whether the first position was closed at a target, by the break-even stop, or manually is not stated.
- Rows 24-25: "second position", "third position": add to the same position or separate new positions not stated; row 26 says all these trades were closed together, row 19 says the first was closed earlier.
- Row 37: "five different position that were trailed": the count of five does not match the three positions named (rows 11-25) plus the re-entry; trailing levels are not stated.
- Row 30: "I took some profit and I use half of this profit to risk again" does not say whether this is a partial, the close of rows 24-26, or a fresh sizing rule; no PARTIAL row is recorded.
- Rows 9, 40: "big trades" (ASR variant "deep trades model") is a proprietary indicator; his statement "where the big players are pushing the price" is the only description.
- Row 26: "the second accumulation phase" and "redistribution phase" are used for the same moment, as spoken.
- Row 45: "all-time low for the day" is spoken as "all-time low" (likely the lowest price of the day, not an all-time record).
- Row 15: date "30 of December" is hedged by him; year and contract not stated.
- No ERROR rows: he admits no mistakes in this video.

## 7 self-check
1 ENTRY rows: 3; trade blocks: 3 (each starts at an ENTRY row). 2 All fields filled (unknown where not stated). 3 Last row pos% 97. 4 Checker line below.

PASS: 0 problem(s)
