# V2 extract 8CWKfoSJu3c (Fabio, NASDAQ short, one-trade session commentary)

Method: EXTRACTION_METHOD_V2.md. Read in 5 chunks of about 2,000 characters (offsets 0, 2000, 4000, 6000, 8000), start to end. The video is a replay commentary of one managed short: the entry happened before the clip starts, so the entry row has no price and no stop level; only money amounts are given for risk and locked profit. The whole video is one winning trade (a trailed short that ended at +23,000 on the position; session +50,000).

## 3.1 Header
```
video_id: 8CWKfoSJu3c
trader: Fabio (Fabio Valentini, day trader; corpus label)
title: unknown (the raw file has no '# ---' header line; text starts at [0:00])
instrument_stated: NASDAQ ("I scalp the NASDAQ during the New York session"; "the short that I took on NASDAQ"); 10 contracts
instrument_inferred: none
tick_size: unknown
session / time of day: "New York session"; month "December" ("the best session of the month of December")
translation_warning: yes (auto-captioned, [m:ss] markers; many ASR slips, see 3.6)
body_chars: 9852
n_decision_rows: 53
n_trades: 1 (entered before the clip; managed and exited inside the clip)
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition ("as long as") |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 | HOLD | short | - | aggressive buyers | "if these buyers aggressive buyers take back control I want to be out of the market" (intro teaser, said again at row 48) | delta / aggressive buyers | aggressive buyers take back control -> he wants to be out |
| 2 | 3 | CONTEXT | - | NASDAQ | session | "I scalp the NASDAQ during the New York session"; closed the session at "$50,000 profit" | time of day | none stated |
| 3 | 13 | CONTEXT | short | - | day story | "after building $27,500 in profit on the first trades of the day" | - | none stated |
| 4 | 13 | ENTRY (short; order type unknown; price not stated; before the clip) | short | not stated | the short | "the short that I took on NASDAQ" | - | none stated |
| 5 | 15 | CONTEXT | short | - | risk vs reward in money | "we are risking a small amount of profit, only 3,150" to make "an additional 23,000 of profit" (open expectation, not a target row) | - | none stated |
| 6 | 17 | PROOF (before/after entry unknown) | short | - | buyers absorbed | "the path of least resistance of the buyers getting completely absorbed" | absorption | none stated |
| 7 | 18 | PROOF (before/after entry unknown) | short | marked level | "punch to the wall" ; sellers' effort | "the rewarded effort of the sellers" | big orders / absorption ; "punch to the wall" [new source] | none stated |
| 8 | 20 | CONTEXT | short | "high in the curve" | position in the "curve" | "We are really high in the curve" ; "complete control on the auction of the sellers" | "the curve" [new source] | none stated |
| 9 | 22 | REJECT | short | add | exposure | no extra contract: "is not the best idea when you are already loaded with 10 contracts" | market speed | price too aggressive, could only add "in discount" ; already 10 contracts ; "low in the curve" |
| 10 | 24 | STOP_MOVE | short | "stop to zero" [?] | risk | "I will lower my risk to be above the eye or a stop to zero" [?] | big sellers in control | sellers controlling the auction ; before any new lows |
| 11 | 25 | HOLD | short | - | buyers | "run this train on the way down" ; trail "when I see that buyers might take back control" | delta / aggressive buyers | trail aggressively when buyers might take back control |
| 12 | 27 | LOCATION | short | 25,650 | level of control | "a clean level on the 25,650 of control of the sellers" ; they "are tapping back into it" | big orders | role: sellers' control level |
| 13 | 29 | LOCATION | short | "25,7630" [?] | aggressive sell order | "It's controlled by the sellers" ; "another punch to the wall" | big orders / aggressive sellers | role: possible stop-in-profit reference (see row 14) |
| 14 | 30 | STOP_MOVE (conditional) | short | that level (25,7630 [?]) | break of the low | "this could be a level where we cover ourself" | big orders | "if the market decide to break again the low" |
| 15 | 31 | LESSON | short | - | floating profit | "an aggressive trailing stop that I take when we have already a nice floating profit" | - | nice floating profit already exists |
| 16 | 33 | CONTEXT | short | - | open profit | floating "$8,000 in profit on top of the 27,000 already for the day" (open profit, not target) ; "it could be an idea to be aggressive" | - | none stated |
| 17 | 36 | TARGET_SET | short | "low of the curve" ; "27,600" [?] | low of the curve | "Final target is 27,600 for 1 to 19 risk-to-reward" ; earlier "like 1 to 16 1 to 19 on the final target" | swing low (the low) | "We see if they break the low" |
| 18 | 37 | LESSON | - | - | volatility | "This is not common. You need volatility to do these kind of trades." | market speed | volatility is needed |
| 19 | 38 | LESSON | - | - | consolidation | "you can decide to take profit more often than I do when we are in a consolidation phase" (alternative he does not use here) | - | consolidation phase |
| 20 | 40 | STOP_MOVE | short | locks "$2,550" profit (level not stated) | buyers reloading | "I put my stop loss in profit for $2,550" | - | "waiting to cover myself" |
| 21 | 41 | CONTEXT | short | 25,630 | buyers | "the buyers are trying to reload their position and reach the 25,630" | delta / aggressive buyers | none stated |
| 22 | 44 | PROOF (AFTER) | short | the level | sellers back | "the sellers taking back control. They are absorbing all the buy orders and the momentum is kicking back in" | absorption, delta, market speed | none stated |
| 23 | 46 | PROOF (AFTER) | short | the level | buyers' fight | "There was no fight of the buyers to break this level." ; candles "getting wider" [new source] ; "Zero doubt here." | absorption, candle width [new source] | none stated |
| 24 | 49 | HOLD | short | - | the curve | "we are going to explode and collapse on the same direction of the auction" | "the curve" [new source], market speed | "now we are still high in the curve" |
| 25 | 50 | CONTEXT | short | - | open profit | floating "$10,000 in profit for the session", "almost half of the profit that we expect from this trade" (open profit, not target) | - | none stated |
| 26 | 52 | LESSON | - | - | day P&L | if "in loss for the day, for example, let's say minus 5,000, it will be smart to take profit" (not his case) | - | day P&L negative |
| 27 | 55 | REJECT | short | profit taking | day cushion | "Doesn't make sense to be super conservative on the profit taking" | market speed | $27,000 banked plus about $12,000 floating ; market "sharp and directional" |
| 28 | 57 | LOCATION | short | 25,63 | retest | "this is where we can expect the sellers to take back control" | delta / aggressive sellers | none stated |
| 29 | 59 | LESSON | - | - | order flow | "I always explain every single move why it's happening and who is controlling price" ; "I use orderflow" | order book / big orders, delta | none stated |
| 30 | 60 | PROOF (AFTER) | short | 25,584.3 | level break | "They are breaking the level 25,584.3 taking back control" ; "super aggressive on the down move" | delta / aggressive sellers | none stated |
| 31 | 62 | LOCATION | short | 25,584 | value area low of the session | "reaching the value area low of the session" ; "cluster ... of absorbed sellers and control of the buyers" ; "They are going to reload 25,584. That is the level that I marked." | today's profile VAL, absorption, footprint | role: caution (buyers reload) |
| 32 | 64 | HOLD | short | 25,584 | sellers | "sellers taking back control again, taking back control again" | delta / aggressive sellers | none stated |
| 33 | 65 | PROOF (AFTER) | short | - | struggle | "they are starting to struggle on the way down because you have absorption of the sell aggressive orders here" (caution) | absorption, delta | none stated |
| 34 | 68 | LOCATION | short | 25,570 ; "yellow level" | level of the squeeze | "if the market managed to break this low at 25,570 ... you can expect volatility on the way down" ; reach "the yellow level that I marked" | swing low, market speed | role: break of 25,570 expected to speed price to the yellow level (price not stated) |
| 35 | 70 | HOLD | short | 25,584 ("white level") | reload level | "They are reloading from the white level that I marked 25,584. And now you can expect control back of the sellers." | delta / aggressive sellers | none stated |
| 36 | 72 | CONTEXT | short | - | size | "I was still in the market with the full 10 contracts for 176 and 500,000 profit" [?] | - | none stated |
| 37 | 73 | STOP_MOVE | short | locks "$9,600" profit (level not stated) | worst case | "Now I put my stop loss to stopping profit for $9,600" ; "worst case scenario, we close 36 $37,000" [?] | - | none stated |
| 38 | 75 | PROOF (AFTER) | short | the level | absorption | "a little bit of absorption on the level but still the buyers are not holding the movement" | absorption, delta | buyers not holding the movement |
| 39 | 77 | LOCATION | short | 25,550 | psychological level | "it's the 25,550 this is also a psychological level" ; "low in the curve" ; "the last point of absorption" ; squeeze level "where the catalyst will happen" | absorption, psychological level [new source], "the curve" [new source] | role: where the catalyst is expected |
| 40 | 80 | STOP_MOVE | short | locks "$20,000" profit (level not stated) | squeeze level | "I cover myself for $20,000 in profit on the single position" | absorption | at the squeeze level 25,550, "last point of absorption" |
| 41 | 81 | CONTEXT | short | stop placement | big orders | "I was not sure where to put it because I don't see participation of the aggressive traders big orders from the buy side and sell side" | order book / big orders, delta | none stated |
| 42 | 83 | PROOF (AFTER) | short | bottom | absorbed seller | "I have an aggressive traders on the sell side on the bottom that got absorbed" ("the first clue") | big orders, absorption | none stated |
| 43 | 84 | STOP_MOVE (conditional) | short | "above the last point of break" | recovery then break | "I'm waiting for him to be recovered and break on the way down to cover myself" | big orders, absorption | the absorbed aggressive seller must "be recovered and break on the way down" |
| 44 | 86 | LOCATION | short | "2534" [?] | level marked | "sellers trying to load back again to load momentum on the way up mark the level 2534" [?] | big orders | none stated |
| 45 | 87 | STOP_MOVE | short | locks "21,000" profit (level not stated) | level break | "they break I put myself 21,000 in profit" | big orders | after the break of the level |
| 46 | 87 | HOLD | short | last point of aggression | failed test | "They try to test. They fail on the way up." | delta / aggressive buyers | "still closed in the last point of aggression of the sellers" |
| 47 | 89 | PROOF (AFTER) | short | - | aggressive buyers | "take control back of the sellers with aggressive buyers" | delta / aggressive buyers | none stated |
| 48 | 90 | STOP_MOVE | short | locks "23,000" profit (level not stated) | aggressive buyers | "So I close my stop loss in profit for 23,000" | delta / aggressive buyers | "if these buyers, aggressive buyers take back control, I want to be out of the market" |
| 49 | 91 | EXIT | short | - | session end | "And this is how the session finished." (exit price not stated; trade result "23,000" per rows 5, 48) | delta / aggressive buyers | exit type not stated (stop in profit implied by rows 48 and 1) |
| 50 | 93 | LESSON | - | - | skew | "the incredible skew between the maximum draw down on the single position and profit" | - | none stated |
| 51 | 94 | LESSON | - | - | trailing | "this is what you can do when the market is really directional. If you know how to trail your stop-loss" | - | market really directional |
| 52 | 97 | STOP_SET | short | money only | initial stop | "we started with a small stop-loss for 3,500" (stated at the end, in hindsight) | - | none stated |
| 53 | 98 | CONTEXT | short | - | result | "then we completed the session with a 10x risk-to-reward multiplier" | - | none stated |

## 3.3 Trade blocks
```
TRADE 1 - short - rows 4-49
state (day/week): "the best session of the month of December"; "the first trades of the day" built "$27,500 in profit"; New York session
location: entry price not stated; levels named during the hold: 25,650 / 25,7630 [?] (sellers' control), 25,63 (retest), 25,584.3 and 25,584 (value area low of the session, absorbed-seller cluster), 25,570 (squeeze low), 25,550 (psychological, last point of absorption) ; level type: other (order levels, value area low of the session)
leading signal: "the path of least resistance of the buyers getting completely absorbed" ; "punch to the wall"
trigger: unknown (entry is before the clip) ; entered BEFORE or AFTER proof: unknown
entry order type: unknown ; placed before the touch: unknown
initial stop: "we started with a small stop-loss for 3,500" (money, row 52) ; "only 3,150" at risk when the clip starts (row 5) ; distance: no price distance stated ; % of price: unknown
target: "the low of the curve", "Final target is 27,600 for 1 to 19 risk-to-reward" [?] ; distance: not stated ; stated R:R: "1 to 16 1 to 19" (rows 17) ; final "10x risk-to-reward multiplier" (row 53)
management: STOP_MOVE rows 10 (stop to zero [?]), 14 (conditional), 20 ($2,550 locked), 37 ($9,600), 40 ($20,000), 43 (conditional), 45 (21,000), 48 (23,000) ; PARTIAL none ; ADD none (REJECT row 9: no extra contract, already 10)
exit: "this is how the session finished" ; stop in profit at 23,000 implied ("I want to be out of the market" if aggressive buyers take back control) ; exit type: unknown (stop in profit, not confirmed)
rejects: row 9 adding a contract (price too aggressive, only "in discount", already 10 contracts, low in the curve) ; row 27 being "super conservative" on profit taking (large day cushion, directional market)
information sources: absorption, delta / aggressive buyers and sellers, big orders ("aggressive sell order", "punch to the wall" [new source]), today's profile value area low, footprint cluster, market speed, swing low, "the curve" [new source], psychological level [new source], candle width [new source]
outcome: "23,000" profit on the position (stop in profit) ; session "$50,000"; day had "27,000" before this trade ; 10 contracts
horizon: "scalp" (his word, row 2); minutes not stated ; the commentary runs about 9 minutes of captions
mirror stated?: no - do not assume
```

## 3.4 Rejections and conditions
- Row 9: no extra contract low in the curve with 10 contracts on; the price was too aggressive and only "discount" fills were possible.
- Row 27: not conservative on profit taking when $27,000 is banked and the market is sharp and directional.
- Row 1 / 11 / 48: aggressive buyers taking back control -> out of the market; trail aggressively when buyers might take back control.
- Row 14: conditional stop in profit if the market breaks the low again.
- Row 17: target depends on a break of the low.
- Row 43: stop above the last point of break once the absorbed seller is recovered and breaks down.
- Row 24: expects the collapse while still high in the curve.
- Rows 19, 26: taking profit more often in consolidation, or when the day is negative, are alternatives he states for others; not his action in this trade.

## 3.5 Verbatim anchors
> "because if these buyers aggressive buyers take back control I want to be out of the market"
**Source GPS: 8CWKfoSJu3c | BEGIN**

> "the short that I took on NASDAQ"
**Source GPS: 8CWKfoSJu3c | BEGIN**

> "is not the best idea when you are already loaded with 10 contracts here to raise the exposure low in the curve"
**Source GPS: 8CWKfoSJu3c | BEGIN**

> "I will lower my risk to be above the eye or a stop to zero"
**Source GPS: 8CWKfoSJu3c | BEGIN**

> "trailing aggressively my stop loss when I see that buyers might take back control"
**Source GPS: 8CWKfoSJu3c | BEGIN**

> "this could be a level where we cover ourself"
**Source GPS: 8CWKfoSJu3c | BEGIN**

> "Final target is 27,600 for 1 to 19 risk-to-reward"
**Source GPS: 8CWKfoSJu3c | MIDDLE**

> "I put my stop loss in profit for $2,550"
**Source GPS: 8CWKfoSJu3c | MIDDLE**

> "Doesn't make sense to be super conservative on the profit taking"
**Source GPS: 8CWKfoSJu3c | MIDDLE**

> "I put my stop loss to stopping profit for $9,600"
**Source GPS: 8CWKfoSJu3c | END**

> "I cover myself for $20,000 in profit on the single position"
**Source GPS: 8CWKfoSJu3c | END**

> "I'm waiting for him to be recovered and break on the way down to cover myself above the last point of break"
**Source GPS: 8CWKfoSJu3c | END**

> "they break I put myself 21,000 in profit"
**Source GPS: 8CWKfoSJu3c | END**

> "So I close my stop loss in profit for 23,000"
**Source GPS: 8CWKfoSJu3c | END**

> "And this is how the session finished."
**Source GPS: 8CWKfoSJu3c | END**

> "we started with a small stop-loss for 3,500"
**Source GPS: 8CWKfoSJu3c | END**

## 3.6 Ambiguity flags
- Row 4, 49: the entry is before the clip; "the short that I took" gives no price, order type or time. The exit row is only "this is how the session finished"; the exit may be a stop in profit or a manual close; not resolved.
- Rows 10, 14, 20, 40, 43, 48: "cover myself" / "cover ourself" / "close my stop loss in profit" appear to mean placing a stop in profit, but "cover" could also mean closing; the stop levels are given only as money locked ($2,550, $9,600, $20,000, 21,000, 23,000), never as prices.
- Row 10: "above the eye or a stop to zero" is garbled [?]; read as lowering risk to breakeven but not resolved.
- Row 13: "25,7630" [?] and row 12 "25,650" and row 21 "25,630": likely one level near 25,63x; as transcribed.
- Row 17: "27,600" as the "Final target" sits near profit-in-dollars magnitudes ($27,000 day profit), not near NASDAQ index prices (25,5xx); unclear whether price or money.
- Row 36: "for 176 and 500,000 profit" [?] garbled; "36 $37,000" in row 37 [?].
- Row 44: "level 2534" [?] missing digits.
- Rows 5, 52: risk "only 3,150" at the start of the clip versus "stop-loss for 3,500" at the start of the trade; as stated.
- Row 5: "risking a small amount of profit" - risk is expressed against open profit; as stated.
- Row 43: "him" and "he" refer to the absorbed aggressive seller (assumed); "recovered" is not defined.
- Row 8, 24, 39: "the curve" is not defined in the clip.
- Row 1 / 47: the opening lines include other speakers ("Yeah", "You you coded the algorithm"); the same sentence "if these buyers aggressive buyers take back control I want to be out of the market" is said at the start and at row 48.

## 7 self-check
1 ENTRY rows: 1; trade blocks: 1 (starts at row 4). 2 All trade-block fields filled (unknown where not stated). 3 Last row pos% 98. 4 No ADD, no PARTIAL: none stated in the clip (REJECT row 9 for the add). 5 Checker line below.

PASS: 0 problem(s)
