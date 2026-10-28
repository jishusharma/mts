# DRAFT KRW-RANGE-BB-MAP: Krown's range concept (SOURCED) and whether BB(20,2) bands or the mid match his range edges or midpoint (OURS)

Status: DRAFT in its own file; `SETUP_CATALOG.md` is NOT edited. Built from the Krown extracts in `MyTradingSys/research/krown_ta101_2026-10-13/extracts/` (`extract_6aA-P4Gvhrc.md` "Why the Boring Part of the Chart Makes the Most Money (Range Trading)", published 2026-10-10; `extract_qEfES84jwwo.md` support and resistance; `extract_INOCBmqQupc.md` RSI). The `KROWN_SETUP_CATALOG` of the krown-g2 session had NOT landed on fast-track when this was written; the consolidated rules KR-R01..KR-R08 in `KROWN_CONSOLIDATED.md:120-127` and the layer spec S3/S4 (`KROWN_LAYER_SPEC.md:59-60`) already hold the same range material and agree with what is quoted here. Quotes are checked by `verify_extract_quotes.py` against the Krown transcripts. Labels: SOURCED (Krown's words, quote + extract file:line), OURS (our reading, mapping or variant, decided on DEV, never called Krown's), NOT FOUND (asked for, not in his words). Krown extracts are tier T3 (ideas and definitions, no sample).

## 1. How Krown defines a range (SOURCED)

R1 Definition. Two zones with price stuck between them. `extract_6aA-P4Gvhrc.md:18`:

> "A range is simply just two zones with a market stuck between them."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:02:40**

R2 High and low are zones, not lines, drawn "wick to close" with at least two reactions. `extract_6aA-P4Gvhrc.md:20` (zones come from his support/resistance episode) and `extract_qEfES84jwwo.md:65`:

> "Wick to close, episode four, again, that's where all that information was."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:02:36**

> "That's where the price turned at least twice. One is an event twice as a memory."
**Source GPS: qEfES84jwwo | BEGIN | t=00:07:24**

R3 Who owns the edges, and the ping-pong. `extract_6aA-P4Gvhrc.md:47` and `:45`:

> "Buyers own the low, sellers own the high."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:02:05**

> "price ping pongs between the two camps, that's all a range is, an unsettled argument effectively."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:04:41**

R4 Midpoint. He names the middle only to rule it out. `extract_6aA-P4Gvhrc.md:72`:

> "The middle, that's your no man's land. No memory, no zone, no edge."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:06:08**

R5 Deviations (price poking beyond an edge). He uses the word "fake out" and not "deviation" for price. `extract_6aA-P4Gvhrc.md:180` and `:182`:

> "The quick poke below the floor that snaps back inside the range is signature fake out."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:17:43**

> "Only act on the close back inside with proof."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:18:04**

R6 Resolution is a close beyond the boundary, and the height projects the first leg. `extract_6aA-P4Gvhrc.md:148` and `:213`:

> "until you should get the range resolution with the closure above or below the range boundaries, you don't have confirmation of that."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:16:46**

> "read the height of the range often projects the first leg of the move."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:21:51**

## 2. How BTC forms a range (SOURCED, no numbers)

- The tell is flat tangled moving averages and shrinking volume (`extract_6aA-P4Gvhrc.md:36`, quote below). He gives no threshold; the only number is an observed "like 50% of the average" volume right before a weekly breakout, which he says is not a rule (`:130`, `:279`).

> "The tell, flat tangled averages plus shrinking volume."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:04:04**

- Ranges last as long as the timeframe allows. `extract_6aA-P4Gvhrc.md:56` (BTC example; stairs: a range, then a step, `:242`):

> "We've seen ranges in Bitcoin even go on for six, seven, eight months."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:05:06**

- A range after a trend: winners take profit, losers regroup, new buyers argue with old sellers (`:43`, stated mechanics, no quote needed). The previous range high becomes the next range low (`:139`).
- Inside a range the bias comes from the structure of the swings: same lows with lower highs favours the sellers, same highs with higher lows favours the buyers (`:153-158`). Not from a band or a midpoint.
- The range width, the number of touches and the length of a "longer and tighter" consolidation: NOT STATED (`extract_6aA-P4Gvhrc.md:277-285`, Gaps). His S/R episode gives "at least twice" for a zone (qEfES84jwwo line above).

## 3. When does he expect both edges to be hit?

- He expects bounces from both edges while the range lasts, and tells the viewer to play both sides. `extract_6aA-P4Gvhrc.md:65`, `:81`, and the support/resistance episode `extract_qEfES84jwwo.md:136`:

> "You can play both sides and you probably should play both sides."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:06:42**

> "Trade the edges or don't trade at all. Flat is again a position."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:07:07**

> "You can play on both sides, by the way. In fact, almost always, you will see something like this."
**Source GPS: qEfES84jwwo | MIDDLE | t=00:14:51**

- NOT FOUND: any statement that price WILL touch the opposite edge after an edge touch, in how many bars, with what frequency, or that a touch at one edge predicts a touch at the other. He says only "ping pongs" (R3) and that the range ends when one side runs out of ammunition (`extract_6aA-P4Gvhrc.md:43`). The opposite edge is a target in our layer spec (`KROWN_LAYER_SPEC.md:59` S3 "opposite edge") and that is OURS, not his words.
- NOT FOUND: a midpoint computation, a 50 % line, an equilibrium, or a deviation size in price terms.
- The word "deviate" appears only for RSI: an RSI of 10 in a downtrend is "a bit exaggerated" and likely to snap back, and RSI back above 60 holding means "something else is emerging" (`extract_INOCBmqQupc.md:232`); he calls 40 to 60 his own view of an RSI range (`:244`), the textbook band being 30 to 70:

> "My personal experience and and opinion would be more like 40 to 60."
**Source GPS: INOCBmqQupc | MIDDLE | t=00:10:31**

## 4. Does a Bollinger Band or its mid match his range? (OURS, untested)

None of the following is Krown's. His only Bollinger-type statement is that he prefers BBWP (the Bollinger Band Width Percentile) to bands for volatility and gives no band settings (`extract_kcMnnQr1VFg.md:87-92`, `:719`; compression is a squeeze, expansion the opposite, `:147`, `:238`).

| Krown element | candidate BB reading | status |
|---|---|---|
| floor and ceiling (horizontal zones, wick to close, >= 2 reactions) | lower and upper band | OURS candidate. The bands are a moving volatility envelope, the zones are fixed price areas. They can coincide only while the mid is flat. In a trend the bands slope and the swing zones do not |
| the middle ("no man's land", no edge) | BB mid (SMA20) | OURS candidate. CONFLICT to test: Krown says the middle has no edge; the operator's row `OPR-BB-MTF-CENTER` treats the 1h and 30m mid as the decision line. Both go to G5; neither is called right |
| a fake-out, i.e. a poke beyond the edge that closes back inside | wick outside the band with a close back inside (or the reverse, a close outside the band = continuation by Bollinger rule 8 in `bollinger_2026-10-14/SOURCES.md`) | OURS candidate. Bollinger-side and Krown-side readings point opposite ways for a close outside; see test M3 |
| range height projects the first leg | band width (4 SD) as the height | OURS candidate, weak: a band width is not the height of a swing range |
| coil (range on declining volume, tightening) | BB squeeze (low band width percentile) | OURS candidate; his own measure is BBWP |
| RSI 40 to 60 as a ranging band | the operator's 40/60 reading (`MAL-BB-RSI-4060.md`) | The numbers coincide; the claims differ (Krown: RSI oscillating inside 40-60 means a range, operator: 40/60 as a trend filter in a BB reading). OURS observation only |

Tests (OURS, DEV only, descriptive tables on 1h and 4h BTC, not a trading rule; they are outcome 5 of the G5 card `opr-bb-mtf-center-g5`):

- M1 range detector (OURS): a window of n bars (grid 24, 48, 96 on 1h) whose high and low zones each have >= 2 touches within x % (grid 0.25, 0.5 %) of the extreme and no close beyond them. Report n ranges.
- M2 band against edges: in those ranges, share of bars where the upper band is within y % of the range high and the lower band within y % of the range low (grid y = 0.25, 0.5, 1.0 %); share of bars where the BB mid is within y % of the range midpoint. Control: the same statistics on random windows of the same length that fail the range test.
- M3 pokes: for pokes beyond a range edge that close back inside within k bars (k = 1, 2, 3), frequency of reaching the opposite edge within H bars against the frequency after a close outside the BB band; n and Wilson 95 % CI, cells below n = 10 not read.
- M4 midpoint: touches of the range midpoint (or the BB mid inside a range) followed by the next close side; is the midpoint a coin flip (Krown) or a decision line (operator)? Report next-1/2/3 close side with n and Wilson CI.

Every range parameter above (n, x, y, k, H) is OURS. Krown's extracts are T3: no sample, so no test result may be described as confirming or refuting him, only as how our data behaves when his definitions are made mechanical.
