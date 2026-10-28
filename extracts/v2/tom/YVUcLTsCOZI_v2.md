# V2 extract YVUcLTsCOZI (session 2026-10-15)

Method: EXTRACTION_METHOD_V2.md (decision rows, anchors machine-checked). Read in full from first to last character in chunks of about 2,000 characters.
Lecture video: order-book basics (large orders, market orders, volume profile, liquidity, slippage, stop loss as market order, market speed, absorption). No chart walk-through with a trade; entries and stops are hypothetical and carry no numbers. n_trades: 0.

## 3.1 Header
```
video_id: YVUcLTsCOZI
trader: Tom Vorwald (self-introduction as "Thomas Forwald" in the transcript; auto-caption spelling; first person, "I'll share my screen with you")
title: Maximum win rate: The ONLY Scalping-Video you'll EVER need!
instrument_stated: not stated for any trade (markets named on the desk: "Zen" [?], Bund future, crude oil, Russell 2000, Nasdaq, S&P, FDAX, Euro stocks, gold)
instrument_inferred: none ("Zen" is probably ZN, the 10-year note, because he later says "Let's go into the ZN here"; kept out of every other field)
tick_size: unknown
session / time of day: unknown (only "at this time of day" for the Nasdaq, no clock time)
translation_warning: yes (auto-captioned, non-native English; the raw file has the header block twice and mojibake in the title)
body_chars: 12910
n_decision_rows: 34
n_trades: 0
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition |
|---|---|---|---|---|---|---|---|---|
| 1 | 5 | LESSON | - | - | knowledge gap | "Mostly of the people are not big enough in their knowledge to understand the real way of scalping." | none (not a chart item) | none stated |
| 2 | 21 | CONTEXT | - | S&P | book imbalance | "Here, there are larger orders positioned on the buy side than on the sell side." | order book / big orders | none stated |
| 3 | 23 | LESSON | - | order book, S&P | large vs small orders | "First clue. Where are the large orders? Where are the small orders?" | order book / big orders | none stated |
| 4 | 28 | LESSON | - | - | imbalance reading | "there is a likelihood that the market will want to move in that direction." | order book / big orders | "when there is an imbalance in the market between the buy and sell sides" |
| 5 | 32 | LESSON | - | - | what moves the book | "market orders are the orders that actually make the order book move." | delta / aggressive buyers or sellers | none stated |
| 6 | 39 | CONTEXT | - | crude oil, VPOC | volume profile, large orders | "below the VPOC, below the price level where the market is in balance." | today's profile, VAH/VAL/POC, order book / big orders | none stated |
| 7 | 41 | CONTEXT | - | crude oil, below VPOC | large orders below, few above | "it's a first indication for me that the market is currently moving away from equilibrium." | order book / big orders, VAH/VAL/POC | none stated |
| 8 | 42 | REJECT | counter-trade (side unstated) | back to equilibrium | market moving away from equilibrium | "I won't quickly take a counter trade to get back to equilibrium." | order book / big orders, VAH/VAL/POC | market "currently moving away from equilibrium" (row 7) |
| 9 | 44 | CONTEXT | - | crude oil, value area | price inside value area | "as long as the market is within the value area, there's a good chance that it will continue to move within it" | VAH/VAL/POC | as long as the market is within the value area |
| 10 | 45 | CONTEXT | down (lean, no trade) | crude oil, down side | where there is "a lot to gain" | "the probability is higher that the market will move downwards because there's a lot to gain down here." | order book / big orders, VAH/VAL/POC | none stated |
| 11 | 51 | REJECT | - | gold | empty book, "no liquidity" | "Is that good for us? No, because with that we can't route our orders cleanly." | order book / big orders | no liquidity on bid or ask side |
| 12 | 51 | LESSON | - | gold | slippage risk | "if the market makes a quick move, we are very likely to experience slippage on both sides." | order book / big orders, market speed | thin book plus quick move |
| 13 | 54 | LESSON | - | - | liquidity check | "That means you always have to check whether there is liquidity in the books." | order book / big orders | none stated |
| 14 | 54 | LESSON (hypothetical ENTRY, long, market, 5 contracts) | long | - | next best price not available | "Cuz just imagine you buy at market now, five contracts." | order book / big orders | no seller at the next price |
| 15 | 59 | CONTEXT | - | ZN | book depth | "Contracts are visible both on the bid and ask side" | order book / big orders | none stated |
| 16 | 60 | CONTEXT | - | ZN | execution quality for small traders | "we'll never have a situation where we don't get a good execution there." | order book / big orders | thousands of contracts on both sides |
| 17 | 61 | CONTEXT | - | Nasdaq | book depth at this time of day | "But if we take a look at the Nasdaq at this time of day, we can already see, wow, there's much much less in the book here." | order book / big orders, time of day | thin book at this time of day |
| 18 | 63 | LESSON (hypothetical ENTRY, long, order type unknown) | long | Russell, "right here and now" | where a stop would sit | "Just imagine for a moment that you decide to buy into the market right here and now." | order book / big orders | none stated |
| 19 | 64 | LESSON (hypothetical STOP_SET, long) | long | Russell, "here" (no number) | stop below, drop = sell | "And now you set your stop loss here." | order book / big orders | none stated |
| 20 | 65 | LESSON | - | - | stop type | "a stop loss is always a market order." | order book / big orders | none stated |
| 21 | 67 | CONTEXT | long | Russell | orders in the book near the stop | "the risk of significant slippage of a large erratic execution of your stop loss is not that high." | order book / big orders | orders visible in the book near the stop |
| 22 | 69 | LESSON (hypothetical STOP_SET, long, 10 contracts) | long | other market, "here" (no number) | stop with 10 contracts, thin book | "you place your stop loss here, and you have perhaps 10 contracts" | order book / big orders | book is thin |
| 23 | 71 | LESSON | long | other market | fill price of the stop | "You will be stopped out with your contracts at this price at the earliest, because it becomes a market order." | order book / big orders | if you are next in line in the book; algos may be ahead |
| 24 | 73 | LESSON | - | - | stop planning | "stop losses are only reasonably plannable for you if you know that the market is also sufficiently large and liquid." | order book / big orders | market sufficiently large and liquid |
| 25 | 74 | LESSON | - | - | instrument key figures | "So, the very first thing we need to know is what are the key figures for the respective instruments." | order book / big orders (averages per instrument) | none stated |
| 26 | 80 | LESSON | - | - | market speed | "is the speed, the so-called speed, high or low?" | market speed | none stated |
| 27 | 81 | CONTEXT | - | - | slow market | "the market is currently routing an order every two or three seconds, then there just isn't much going on." | market speed | order every two or three seconds |
| 28 | 82 | LESSON | - | - | speed acceleration | "suddenly the speed between the bid and the ask begins to accelerate, then the market starts to rotate in a different direction." | market speed | speed between bid and ask accelerates |
| 29 | 87 | LESSON | - | - | speed takes off | "then you know it's just about to accelerate in one direction or the other." | market speed | speed suddenly takes off |
| 30 | 88 | LESSON | - | - | direction tools | "You can look for big orders. You can look for absorption." | order book / big orders, absorption | none stated |
| 31 | 89 | PROOF (n/a, no trade) | - | - | absorption definition | "orders keep getting hit over and over, but the market doesn't move any further." | absorption, market speed, delta / aggressive buyers or sellers | then speed shifts the other way |
| 32 | 90 | LESSON | - | - | absorption then speed shift | "Yes, then you have exactly the opposite of a breakout." | absorption, market speed | "Now it moves just a little further, and suddenly the market speed shifts in the other direction" |
| 33 | 95 | REJECT | - | dangerous markets | which markets and times to avoid | "so that you don't trade in markets at times that are unfavorable" | order book / big orders, time of day | none stated |
| 34 | 97 | LESSON | - | - | future content | "over the next weeks and months, we'll be publishing and showing you some of them with live trades in combination with exactly these methods." | - | none stated |

## 3.3 Trade blocks
No trade is taken or shown, so there is no trade block. Rows 14, 18, 19 and 22 are hypothetical illustrations (a market buy of five contracts, a buy "right here and now" with a stop "here", a stop with "10 contracts") with no price, distance or target. They are typed LESSON, not ENTRY or STOP_SET, so that n_trades stays 0. No target is stated anywhere. mirror stated?: no - do not assume.

Stops, targets and entries stated in words (all hypothetical, none with a number):
- Entry (row 14): "you buy at market now, five contracts" (long, market order, hypothetical).
- Entry (row 18): "you decide to buy into the market right here and now" (Russell, long, hypothetical).
- Stop (row 19): "you set your stop loss here" (no level; "if the market drops below here and you sell, that's where your stop loss would be").
- Stop (row 22): "you place your stop loss here, and you have perhaps 10 contracts" (no level).
- Target: none stated.

## 3.4 Rejections and conditions
- Row 8 (REJECT): no quick counter trade back to equilibrium while the market is moving away from it (large orders on one side, price below the VPOC).
- Row 11 (REJECT): a market with no liquidity on either side is "not good for us" because orders cannot be routed cleanly (slippage).
- Row 33 (REJECT): do not trade in dangerous markets or at unfavorable times.
- Row 4 condition: an imbalance between buy and sell sides makes a move in that direction likely.
- Row 9 condition: as long as the market is within the value area it will probably keep moving within it.
- Row 23 condition: the stop fills "at this price at the earliest" because it becomes a market order.
- Row 24 condition: stop losses are only reasonably plannable if the market is sufficiently large and liquid.
- Row 28 condition: an order every two or three seconds means little is going on; accelerating speed between bid and ask means something is about to happen.

## 3.5 Verbatim anchors
> "Mostly of the people are not big enough in their knowledge to understand the real way of scalping."
**Source GPS: YVUcLTsCOZI | BEGIN**

> "Here, there are larger orders positioned on the buy side than on the sell side."
**Source GPS: YVUcLTsCOZI | BEGIN**

> "First clue. Where are the large orders? Where are the small orders?"
**Source GPS: YVUcLTsCOZI | BEGIN**

> "there is a likelihood that the market will want to move in that direction."
**Source GPS: YVUcLTsCOZI | BEGIN**

> "market orders are the orders that actually make the order book move."
**Source GPS: YVUcLTsCOZI | BEGIN**

> "below the VPOC, below the price level where the market is in balance."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "it's a first indication for me that the market is currently moving away from equilibrium."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "I won't quickly take a counter trade to get back to equilibrium."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "as long as the market is within the value area, there's a good chance that it will continue to move within it"
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "the probability is higher that the market will move downwards because there's a lot to gain down here."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "Is that good for us? No, because with that we can't route our orders cleanly."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "if the market makes a quick move, we are very likely to experience slippage on both sides."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "That means you always have to check whether there is liquidity in the books."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "Cuz just imagine you buy at market now, five contracts."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "Contracts are visible both on the bid and ask side"
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "we'll never have a situation where we don't get a good execution there."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "But if we take a look at the Nasdaq at this time of day, we can already see, wow, there's much much less in the book here."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "Just imagine for a moment that you decide to buy into the market right here and now."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "And now you set your stop loss here."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "a stop loss is always a market order."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "the risk of significant slippage of a large erratic execution of your stop loss is not that high."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "you place your stop loss here, and you have perhaps 10 contracts"
**Source GPS: YVUcLTsCOZI | END**

> "You will be stopped out with your contracts at this price at the earliest, because it becomes a market order."
**Source GPS: YVUcLTsCOZI | END**

> "stop losses are only reasonably plannable for you if you know that the market is also sufficiently large and liquid."
**Source GPS: YVUcLTsCOZI | END**

> "So, the very first thing we need to know is what are the key figures for the respective instruments."
**Source GPS: YVUcLTsCOZI | END**

> "is the speed, the so-called speed, high or low?"
**Source GPS: YVUcLTsCOZI | END**

> "the market is currently routing an order every two or three seconds, then there just isn't much going on."
**Source GPS: YVUcLTsCOZI | END**

> "suddenly the speed between the bid and the ask begins to accelerate, then the market starts to rotate in a different direction."
**Source GPS: YVUcLTsCOZI | END**

> "then you know it's just about to accelerate in one direction or the other."
**Source GPS: YVUcLTsCOZI | END**

> "You can look for big orders. You can look for absorption."
**Source GPS: YVUcLTsCOZI | END**

> "orders keep getting hit over and over, but the market doesn't move any further."
**Source GPS: YVUcLTsCOZI | END**

> "Yes, then you have exactly the opposite of a breakout."
**Source GPS: YVUcLTsCOZI | END**

> "so that you don't trade in markets at times that are unfavorable"
**Source GPS: YVUcLTsCOZI | END**

> "over the next weeks and months, we'll be publishing and showing you some of them with live trades in combination with exactly these methods."
**Source GPS: YVUcLTsCOZI | END**

> "Here you can see the limit buy orders currently in the book, and here you see the limit sell orders."
**Source GPS: YVUcLTsCOZI | BEGIN**

> "Now, let's make a reference to the large orders and take a look at where they are."
**Source GPS: YVUcLTsCOZI | MIDDLE**

> "This means if the market drops below here and you sell, that's where your stop loss would be."
**Source GPS: YVUcLTsCOZI | MIDDLE**

## 3.6 Ambiguity flags
- Header and rows: "Thomas Forwald" and "Zen" are caption spellings; Tom Vorwald and ZN are not confirmed by the transcript.
- Row 1 and title: "big hit rate" and "Maximum win rate" are promised; no win rate or number is ever given.
- Row 10: "there's a lot to gain down here" is not defined (no price, target or distance).
- Row 11: "Is that good for us? No" follows the sentence "If a market participant buys now, will he cause these jumps here?"; the exact meaning of "jumps" is unclear.
- Rows 14, 18, 19, 22: "here" refers to an on-screen position that the transcript does not describe; no level can be written.
- Row 32: "exactly the opposite of a breakout" has no stated direction or trade action.
- Row 2: "S&P" appears in the raw file as "S&amp;P"; the anchors avoid it.

## 3.7 Self-check
- Last decision row pos% is at least 95 (row 34). ENTRY rows: 0; trade blocks: 0 (consistent). Extra anchors cover the stops and entries stated in words.

PASS: 0 problem(s)