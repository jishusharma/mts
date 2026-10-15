# V2 extract G0CiJcuXCRs (session 2026-10-15)

Method: EXTRACTION_METHOD_V2.md (decision rows, anchors machine-checked).
Read in full, in chunks of about 2,000 characters, first to last character (body 8412 characters after the second header block). Lecture video on order book scalping: big orders, market speed, volume profile. No trade is taken and no stop, target or entry price is stated.

## 3.1 Header
```
video_id: G0CiJcuXCRs
trader: Tom Vorwald (transcript says "I am Thomas Forwald", spelling as in the auto-captions)
title: The ONLY Scalping-Video you will EVER need
instrument_stated: not stated as a traded instrument (he shows "the S&P order book" and speaks of "the ES"; he names gold, the DAX future and the Euro Stoxx only as markets for learning)
instrument_inferred: ES (E-mini S&P future) for the demo order book, because of "S&P order book" and "in the ES"; not copied into any other field
tick_size: unknown
session / time of day: unknown ("pre-market" is named once, row 28)
translation_warning: yes (auto-captioned, non-native English, garbled words such as "order book scalp" and "this sessions"; the file has a doubled header block)
body_chars: 8412
n_decision_rows: 33
n_trades: 0
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition |
|---|---|---|---|---|---|---|---|---|
| 1 | 11 | CONTEXT | - | big orders in the S&P book | order book | "these prepared big orders were played by major market participants" | order book / big orders | none stated |
| 2 | 13 | CONTEXT | - | upward move | order book | "The market is currently striving upwards." | order book / big orders | none stated |
| 3 | 15 | LESSON | - | - | speed | "I need market speed." (next to big orders = liquidity) | market speed, order book / big orders | none stated |
| 4 | 16 | LESSON | - | - | interaction | "I need to see interaction that plays in my direction." | market speed | none stated |
| 5 | 17 | LESSON | - | big order | speed plus big order | both together tell him whether the big order gets filled or "front running is being played and the whole thing reverses" | market speed, order book / big orders | needs both big order and speed seen together |
| 6 | 20 | LESSON | - | - | order sizes | "first learn which order sizes associated with the product" | order book / big orders | none stated |
| 7 | 21 | LESSON | - | - | key figures | "I must be able to scale the exact key figures 100%" | order book / big orders | none stated |
| 8 | 21 | LESSON | - | LVN / HVN | volume profile | "low volume nodes or high volume nodes" as past liquidity or little liquidity | HVN/LVN or "volume step" | none stated |
| 9 | 26 | CONTEXT | - | today's intraday volume profile | intraday volume profile | "take a quick look at how liquidity has been played so far today" | today's profile | none stated |
| 10 | 32 | LOCATION | - | low volume spots on the profile | intraday volume profile | "I can very clearly and easily locate areas of low volume." | today's profile, HVN/LVN or "volume step" | none stated |
| 11 | 33 | LOCATION | - | where volume increases | profile | "noticing when the volume increases significantly" | HVN/LVN or "volume step" | none stated |
| 12 | 35 | CONTEXT | - | high volume areas | profile | "I know the market was in balance." | today's profile, HVN/LVN | none stated |
| 13 | 37 | CONTEXT | - | high volume areas | profile | larger positions over a longer time = "an assumption of equilibrium" (he did not see it) | today's profile | admits "I didn't actually see it" |
| 14 | 38 | CONTEXT | - | low volume areas | profile | "the market had little desire to stay for a long time" = "Rejection." | today's profile, HVN/LVN | none stated |
| 15 | 41 | LESSON | - | big order in the book | order book | "If the market now just ticks along comfortably here in the book" with small numbers: "Nothing." | order book | hypothetical scenario A |
| 16 | 44 | LOCATION | - | low volume level (expected to go through again) | profile, order book | price reaches a low volume level "where I actually assume it will go through again" | HVN/LVN or "volume step" | hypothetical scenario A, price ticking down |
| 17 | 45 | PROOF (AFTER) | - | below the low volume level | speed | "it goes below that and does nothing and stops and starts going up again" | market speed | price goes below the low volume level and stalls |
| 18 | 46 | HOLD | - | back to high volume | outcome of scenario A | "it will run back to the high volume" | HVN/LVN, market speed | stall at the low volume level, then price turns up |
| 19 | 47 | LESSON | - | - | scenario A | "lethargic back and forth scalping, which any of us can easily do" | market speed | none stated |
| 20 | 49 | PROOF (AFTER) | - | low volume area | speed | "reaches the low volume area and has a constantly high speed" | market speed, HVN/LVN | scenario B, price going down |
| 21 | 50 | LESSON | - | - | participants | "Large market participants are ready to interact." | market speed | scenario B, "a bit more selling pressure than buying pressure" |
| 22 | 55 | PROOF (AFTER) | - | big order / liquidity | speed | "Here I need to see the market slowing down." | market speed | if it slows, "the possibility that it goes up to the big order, to the liquidity" |
| 23 | 57 | HOLD | - | continues through the level | speed | "it will continue to run" | market speed | "if the market goes to such a level and continues to interact" |
| 24 | 58 | LESSON | - | level the market zipped through earlier | speed | "If it gets there and is lethargic again and had no interest, then it goes back to the interest." | market speed, prior profile | lethargic at a level where it earlier showed no interest |
| 25 | 62 | LESSON | - | - | speed | "it's about market speed at the corresponding price ranges" | market speed | none stated |
| 26 | 64 | LESSON | - | ES order sizes | order sizes | "which key figures are actually large in the ES and which are small" | order book / big orders | none stated |
| 27 | 66 | LESSON | - | - | speed | "Can you really define what is fast and what is slow?" | market speed | none stated |
| 28 | 68 | REJECT | - | - | speed | rejects judging speed by feel: "Oh, my gut tells me something is fast right now." | market speed | speed must "correlate" with liquidity (high or low) present at that price |
| 29 | 74 | CONTEXT | - | high past liquidity vs low volume node | profile | "Am I in price ranges of high past liquidity, meaning acceptance, or am I in price ranges of low volume nodes?" | HVN/LVN or "volume step" | none stated |
| 30 | 76 | LESSON | - | low volume node | profile | "the market might stall and pull back" even at a low volume node | HVN/LVN, market speed | none stated |
| 31 | 83 | PROOF (AFTER) | - | pre-market big orders | order book | "one big order, second big order, third big order. They've all been eaten up." | order book / big orders, time of day | pre-market; he calls it "easy money for breakfast"; no entry or price stated |
| 32 | 89 | REJECT | - | DAX future | order book | does not recommend the DAX for order book scalping, "extremely thin uh liquidity" | order book, other market (DAX) | none stated |
| 33 | 96 | LESSON | - | - | claim | "very high hit rates" for "short-term trading" done this way | - | no number or sample stated |

## 3.3 Trade blocks
No trade is taken or shown. The video describes how to read big orders, speed and volume profile in two hypothetical scenarios (A: price goes below a low volume level and stalls, so it returns to high volume; B: price goes into a low volume area with constant high speed, so it keeps running). Row 31 is a pre-market remark about big orders that "have all been eaten up", with no entry, stop or target. n_trades: 0.

Stops, targets and entries stated in words: none.

## 3.4 Rejections and conditions
- Row 28 (REJECT): judging "fast" or "slow" from a gut feeling; speed has to be read together with the liquidity present at that price.
- Row 32 (REJECT): the DAX future for order book scalping, reason "extremely thin uh liquidity".
- Row 5 condition: the big order is only meaningful when market speed is seen together with it.
- Row 13 condition: equilibrium at the high volume areas is "an assumption" because he did not see it trade.
- Row 17 / 18 condition: price goes below the low volume level, does nothing, stalls and turns up, then it runs back to the high volume.
- Row 22 condition: if the market slows at the low volume area, it may go up to the big order, to the liquidity.
- Row 23 condition: if the market keeps interacting at that level, it continues to run.
- Row 24 condition: lethargic again at a level where it earlier had no interest, then it goes back to the interest.
- Row 28 condition: speed and liquidity must correlate.

## 3.5 Verbatim anchors
> "We can clearly see that these prepared big orders were played by major market participants."
**Source GPS: G0CiJcuXCRs | BEGIN**

> "I need market speed."
**Source GPS: G0CiJcuXCRs | BEGIN**

> "I need to see interaction that plays in my direction."
**Source GPS: G0CiJcuXCRs | BEGIN**

> "or if front running is being played and the whole thing reverses."
**Source GPS: G0CiJcuXCRs | BEGIN**

> "I can very clearly and easily locate areas of low volume."
**Source GPS: G0CiJcuXCRs | BEGIN**

> "Here and here, I know the market was in balance."
**Source GPS: G0CiJcuXCRs | MIDDLE**

> "That's an assumption because I didn't actually see it."
**Source GPS: G0CiJcuXCRs | MIDDLE**

> "If the market now just ticks along comfortably here in the book"
**Source GPS: G0CiJcuXCRs | MIDDLE**

> "it goes below that and does nothing and stops and starts going up again"
**Source GPS: G0CiJcuXCRs | MIDDLE**

> "it will run back to the high volume."
**Source GPS: G0CiJcuXCRs | MIDDLE**

> "reaches the low volume area and has a constantly high speed."
**Source GPS: G0CiJcuXCRs | MIDDLE**

> "Here I need to see the market slowing down."
**Source GPS: G0CiJcuXCRs | MIDDLE**

> "But if the market goes to such a level and continues to interact, well, what does it do then?"
**Source GPS: G0CiJcuXCRs | MIDDLE**

> "it will continue to run."
**Source GPS: G0CiJcuXCRs | MIDDLE**

> "If it gets there and is lethargic again and had no interest, then it goes back to the interest."
**Source GPS: G0CiJcuXCRs | MIDDLE**

> "Not just, Oh, my gut tells me something is fast right now."
**Source GPS: G0CiJcuXCRs | END**

> "Am I in price ranges of high past liquidity, meaning acceptance, or am I in price ranges of low volume nodes?"
**Source GPS: G0CiJcuXCRs | END**

> "one big order, second big order, third big order. They've all been eaten up."
**Source GPS: G0CiJcuXCRs | END**

> "which I absolutely don't recommend for order book scalping due to the extremely thin uh liquidity"
**Source GPS: G0CiJcuXCRs | END**

## 3.6 Ambiguity flags
- Row 5: "front running is being played" is his phrase for a big order that is not filled and the move reverses; meaning not defined further.
- Row 13: "equilibrium" is an assumption he flags himself; no price is stated.
- Row 16 / 17 / 20: "low volume level" and "price range" are not given as prices; "Here" and "here" refer to a chart or book on screen the transcript does not show.
- Row 21: "keeping the downtrend stable" is said in scenario B; no trend is stated for the day.
- Row 24: "goes back to the interest" is unclear (back to a high interest level or back to the big order).
- Row 28: "Not just, ..." sentence is cut; the closing words "when it tells you that it also sees that both correlate" are garbled.
- Row 33: "very high hit rates" has no number; the intro claim "trading World Cup champions" is promotional.
- Row 1 / 2: "the S&P order book" vs "the ES"; the instrument is not stated as the one traded.
- The transcript ends mid-sentence ("and I'll").

## 3.8 Self-check
- ENTRY rows: 0; trade blocks: 0 (no trade in the video).
- Last decision row pos% is 96 (row 33), the closing lines have no decision.
- Terms checked: none of the forbidden labels is used.

PASS: 0 problem(s)
