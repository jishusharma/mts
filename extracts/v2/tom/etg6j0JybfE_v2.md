# V2 extract etg6j0JybfE (session 2026-10-09, jisnb/extract-2026-10-09)

Method: EXTRACTION_METHOD_V2.md (decision rows, anchors machine-checked) + playbook Part J tiers on the derived rules (section 3.7).
Read in full (one pass, 10,477 characters). One hypothetical swing-trade walk-through on the DAX (no real trade, no price numbers).

## 3.1 Header
```
video_id: etg6j0JybfE
trader: Tom Vorwald (channel "Tom Vorwald EN" per YouTube oEmbed; first person, "my personal swing trading strategy")
title: The Ultimate Swing Trading Strategy 2026 (For Beginners)
instrument_stated: DAX ("Let's just take the DAX in this case"); stocks and commodities are named as other places to use the idea
instrument_inferred: none
tick_size: unknown (no price is stated)
session / time of day: unknown; time frame of the chart is not stated; holding period stated as days
translation_warning: yes (auto-captioned, non-native English)
body_chars: 10477
n_decision_rows: 20
n_trades: 1 (hypothetical, long, ends without outcome)
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition |
|---|---|---|---|---|---|---|---|---|
| 1 | 7 | CONTEXT | - | - | holding period | "holding periods of three, four, at most seven or eight days" | time of day / horizon | "where there's current momentum or where it's expected that momentum could arise" |
| 2 | 13 | REJECT | - | - | quarterly reports | screen for "figures being released like quarterly reports" before the trade | news | stocks only ("if you're doing this with stocks") |
| 3 | 26 | CONTEXT | - | - | market phase | phases "reflation, recovery, overheat, or even stagflation" from a growth and inflation "duality" ("four quadrant model") | news (growth, inflation data) | "always fundamentally depends on which particular product they currently prefer" |
| 4 | 37 | CONTEXT | - | - | liquidity | is the idea "being played by the market technically and in terms of liquidity?" ("capital flow index") | volume, other index | none stated |
| 5 | 47 | LOCATION | long | DAX "right up here, very, very high" | chart | "the whole thing looks really strong and stable" | swing high (chart) | none stated |
| 6 | 50 | PROOF (before entry) | long | the high area | volume | "liquidity is decreasing, but it's starting to increase again in this area" | volume | none stated |
| 7 | 52 | PROOF (before entry) | long | - | volume | "is liquidity currently entering the market? Yes, liquidity is going in." | volume | none stated |
| 8 | 55 | PROOF (before entry) | long | corrections | swing sizes | last corrections "relatively small, or rather, they're getting smaller and smaller" | swing high/low | none stated |
| 9 | 57 | CONTEXT | long | up moves | swing sizes | looks at the up moves "to get a feel for how strongly the market is playing right now" | swing high/low | none stated |
| 10 | 60 | PROOF (before entry) | long | last few highs | highs | "there was a reaction at every single high point" except one area | swing high | none stated |
| 11 | 63 | REJECT | long | now (at the high) | - | "I would actually be much better off if I just wait and see here." | swing high | "I need to observe if the market eventually gives me a clear reaction" ; reason: "to be on the right side of the risk-reward ratio" |
| 12 | 69 | REJECT | long | - | - | not entering from fear of missing a trade: "I'll have the patience now" | - | "the overall movement hasn't actually come down just yet" |
| 13 | 71 | ENTRY (illustration; order type unknown; after the market "runs to here") | long | the price he marks after the wait | - | "technically, I have the idea to buy now." | chart | "I should now take a moment to check my idea once more" |
| 14 | 73 | PROOF (after the price point, before the order) | long | - | macro data | "are the data points, specifically the inflation data" and growth data "still holding steady" | news | "within that critical range where stock markets are truly supported" |
| 15 | 81 | TARGET_SET | long | measured from the entry point upwards | distances of earlier moves | "these distances here are my minimum profit target" | swing high/low distances | "I calculate them from here" |
| 16 | 85 | STOP_SET | long | a level below entry | past corrections | "this is the absolute maximum it has gone down in the past" ; "this level right here is now my defined risk" | swing low (largest past correction) | none stated |
| 17 | 91 | CONTEXT | long | - | R:R | "my profit is about twice as large as my risk" | - | "check, uh all the evidence provided that my idea can now be implemented" |
| 18 | 98 | LESSON | - | - | - | "Does this align with the idea of the major market participants?" (to be checked "again and again") | - | none stated |
| 19 | 96 | LESSON | - | - | key figures | "you absolutely must determine the key figures for yourself, so that you don't take any unnecessary risk" | - | none stated |
| 20 | 93 | LESSON | - | stocks in sectors | - | "Try doing the whole thing with stocks" in "the corresponding sectors" | - | none stated |

## 3.3 Trade blocks
```
TRADE 1 (hypothetical, no outcome) - long - rows 5-17
state (day/week): macro phase check first (rows 3-4); DAX "right up here, very, very high", "really strong and stable"
location: the high area; level type: swing high ; he does NOT buy at the high (row 11)
leading signal: volume liquidity turning up after a decrease (rows 6-7); corrections shrinking (row 8); reaction at every earlier high (row 10)
trigger: "the market eventually gives me a clear reaction that in turn truly confirms and supports my original idea" (row 11) ; entered BEFORE or AFTER proof: after (proof first, then "the idea to buy now")
entry order type: unknown ; placed before the touch: unknown
initial stop: at the level that equals "the absolute maximum it has gone down in the past" ; distance: unknown (no price or points stated) ; % of price: unknown
target: "minimum profit target" = "these distances" measured upward from the entry ; distance: unknown ; stated R:R: "about twice as large as my risk"
management: none stated
exit: none stated ; exit type: unknown
rejects: entering at the high before a clear reaction (row 11); entering from fear of missing the trade (row 12); trading stocks into quarterly reports (row 2)
information sources: volume, swing high/low, news (growth and inflation data), other market (capital flow index named, not shown)
outcome: none (hypothetical)
horizon: "three, four, at most seven or eight days"
mirror stated?: no - do not assume
```

## 3.4 Rejections and conditions
- Row 2 (REJECT): do not hold through stock "quarterly reports" without screening; stocks only.
- Row 11 (REJECT): no long at the highs without "a clear reaction that in turn truly confirms and supports my original idea". Reason given: the risk-reward ratio.
- Row 12 (REJECT): no entry out of fear of missing a trade.
- Row 14 condition: growth and inflation data must still be "within that critical range where stock markets are truly supported" before the order.
- Row 17 condition: the 2:1 comparison is checked together with "all the evidence".

## 3.5 Verbatim anchors
> "In swing trading, we want to locate trades with holding periods of three, four, at most seven or eight days where there's current momentum or where it's expected that momentum could arise."
**Source GPS: etg6j0JybfE | BEGIN**

> "You absolutely have to screen for that beforehand."
**Source GPS: etg6j0JybfE | BEGIN**

> "Let's just take the DAX in this case"
**Source GPS: etg6j0JybfE | MIDDLE**

> "I can already see that liquidity is decreasing, but it's starting to increase again in this area."
**Source GPS: etg6j0JybfE | MIDDLE**

> "So, the first question is, is liquidity currently entering the market? Yes, liquidity is going in."
**Source GPS: etg6j0JybfE | MIDDLE**

> "I can see right away from the intervals, yeah, they're relatively small, or rather, they're getting smaller and smaller."
**Source GPS: etg6j0JybfE | MIDDLE**

> "with the exception of this specific area here, there was a reaction at every single high point."
**Source GPS: etg6j0JybfE | MIDDLE**

> "I would actually be much better off if I just wait and see here."
**Source GPS: etg6j0JybfE | MIDDLE**

> "I need to observe if the market eventually gives me a clear reaction that in turn truly confirms and supports my original idea."
**Source GPS: etg6j0JybfE | MIDDLE**

> "And that is so crucially important just to be on the right side of the risk-reward ratio."
**Source GPS: etg6j0JybfE | MIDDLE**

> "I'll have the patience now and wait until a recovery phase has arrived."
**Source GPS: etg6j0JybfE | END**

> "technically, I have the idea to buy now."
**Source GPS: etg6j0JybfE | END**

> "Are the data points, specifically the inflation data, and is the economic growth data still holding steady within that critical range where stock markets are truly supported?"
**Source GPS: etg6j0JybfE | END**

> "I need a profit target upwards that I can determine."
**Source GPS: etg6j0JybfE | END**

> "I can then say, these distances here are my minimum profit target that I want to expect for myself."
**Source GPS: etg6j0JybfE | END**

> "this is the absolute maximum it has gone down in the past."
**Source GPS: etg6j0JybfE | END**

> "this level right here is now my defined risk. That's where I put my stop loss."
**Source GPS: etg6j0JybfE | END**

> "And then I already see my profit is about twice as large as my risk."
**Source GPS: etg6j0JybfE | END**

## 3.6 Ambiguity flags
- Row 12 / row 13: "wait until a recovery phase has arrived" mixes the macro word "recovery" (row 3) with a price recovery. The sentence after it ("the market does exactly that and runs to here") is a chart move he points at with "here"; the price move is not described in words. Two readings: (a) macro phase, (b) price recovery. Not resolved.
- Row 15: "these distances here" are shown on the screen; the words before are "the up moves" (row 9) and "the intervals" (row 8). Which swing distances (last up move, average, largest) is not stated.
- Row 16: "the absolute maximum it has gone down in the past": the lookback window is not stated.
- Row 5: "right up here, very, very high" is a screen location; no price or percentage of range is given.
- Row 10: "a reaction at every single high point" does not say reaction size or how many highs.

## 3.7 Candidate rules, with provenance and the Naked BTC chart test
Tier = playbook Part J. Location tag = [T/id:file line@char offset in the raw file].

R-etg6-1 | T5-like instruction in his own words ("You absolutely have to screen for that beforehand", stocks only) | Check scheduled company numbers (quarterly reports) before a stock swing trade.
- Source: [T/etg6j0JybfE:7@1360]
- Naked BTC chart test: not chart-observable. BTC has no quarterly reports: not applicable to BTC. Event risk equivalent (funding times, macro releases) is NO-SOURCE here.

R-etg6-2 | T1 (example) | Buy side needs "liquidity seems to be entering the market": volume low, then rising again in the area, before the trade.
- Source: [T/etg6j0JybfE:7@5269] ; [T/etg6j0JybfE:7@5448]
- Naked BTC chart test: a volume histogram under the price (the rule names volume): volume bars shrink over a stretch near the highs, then bar height rises again. Measurable on a bare BTC chart with its volume pane. NO-SOURCE for how long the decrease must last, how much the increase must be, and the timeframe.

R-etg6-3 | T1 (example) | Healthy trend context for a long: the last corrections "getting smaller and smaller".
- Source: [T/etg6j0JybfE:7@5940]
- Naked BTC chart test: pure price. On a bare BTC chart each successive down swing (high to following low) is smaller than the one before. Strict-decrease test is implementable; the number of swings is NO-SOURCE (he says "the last down moves", count unstated).

R-etg6-4 | T2/T4 (self-check and recommendation) | Do not buy at the high right away. Wait for "a clear reaction that in turn truly confirms and supports my original idea", for the sake of the risk-reward ratio.
- Source: [T/etg6j0JybfE:7@6723] ; [T/etg6j0JybfE:7@6658] ; [T/etg6j0JybfE:7@6891]
- Naked BTC chart test: a bare BTC chart shows price reaching the prior swing high and either rejecting it (candle that turns back below the high) or not. What "clear reaction" means is not defined in this video: NO-SOURCE. Do not invent a candle pattern.

R-etg6-5 | T1 (example, he did it on the chart) | Stop for a long = entry minus "the absolute maximum it has gone down in the past" (the largest past correction), "That's where I put my stop loss."
- Source: [T/etg6j0JybfE:7@8973] ; [T/etg6j0JybfE:7@9068]
- Naked BTC chart test: on a bare BTC chart measure the largest down swing in the lookback window and put the stop that far below the entry. The lookback window is NO-SOURCE; it is the one free parameter.

R-etg6-6 | T1 (example) | Target for a long = at least the distances of the earlier up moves ("minimum profit target"), measured up from the entry; check that profit is "about twice as large as my risk".
- Source: [T/etg6j0JybfE:7@8777] ; [T/etg6j0JybfE:7@9549]
- Naked BTC chart test: on a bare BTC chart measure the prior up swings and project the same distance above the entry. Which up swing is NO-SOURCE. The 2:1 is his picture's outcome ("I already see"), not a stated minimum: T3 one calculation, never a minimum-R:R-2 rule (Part J lists this exact error).

R-etg6-7 | T1 | Horizon: swing trades are held "three, four, at most seven or eight days".
- Source: [T/etg6j0JybfE:7@863]
- Naked BTC chart test: a duration on a bare BTC chart (3 to 8 daily candles, or the equivalent on the traded timeframe). Only the days are sourced.

Not a rule: the growth / inflation four-quadrant macro process (rows 3, 14) is not chart-observable and has no BTC mapping in this video. "Capital flow index" is named, not defined: NO-SOURCE.

Rules with parameters and no source: none added by the extractor. The free parameters listed above are marked NO-SOURCE; do not tune them.
Not found in this video: any numeric stop or target, any timeframe for the chart, any entry order type, any partial or trailing management.

## 3.8 Self-check
- Last decision row pos% is above 95.
- No mirror (short) rule is written; he does not state one.
- Gate result is pasted at the end of the file after the run.
