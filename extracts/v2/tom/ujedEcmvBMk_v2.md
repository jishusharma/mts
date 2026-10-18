# V2 extract ujedEcmvBMk

Method: EXTRACTION_METHOD_V2.md (decision rows, anchors machine-checked). Read in full from the first to the last character (body about 9,900 characters, read as one pass because the file is small; the raw file carries two identical header blocks, the body starts after the second `# ---`). Live-session review video: one short idea that is stopped out, then a short re-entry. Instrument is DAX futures. The trade result in money or points is never stated.

## 3.1 Header
```
video_id: ujedEcmvBMk
trader: Tom Vorwald (Tom Vorwald EN channel; transcript is first person: "how I traded DAX futures this morning")
title: This is the BEST DAX Trading Strategy! (LIVE Trade)
instrument_stated: DAX futures ("how I traded DAX futures this morning")
instrument_inferred: none
tick_size: unknown
session / time of day: "this morning"; pre-market highs and "main trading hours" mentioned; no clock times
translation_warning: yes (auto-captioned, cleaned: "An FDA's live session", "UX sentiment", "[?]" words left as in the raw file)
body_chars: 9932
n_decision_rows: 40
n_trades: 2
```
Trade result: two short trades on one day. Trade 1 is stopped out after a partial; trade 2 is a re-entry short that is scaled out in parts. No money, point or R figures are stated.

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 | LESSON | - | - | - | "sometimes it's important to be dynamic" | none (not a chart item) | none stated |
| 2 | 13 | LOCATION | short | "typical pre-market highs" (taken out) | pre-market highs, V reversal before | "We had taken out these highs here" | swing high, time of day (pre-market) | none stated |
| 3 | 12 | ENTRY | short | the taken-out pre-market highs area | chart | "what you see here is my short entry into the DAX" ; order type unknown (already shown in the chart, set-up shown afterwards) | weekly profile, VPOC, single prints | none stated |
| 4 | 17 | CONTEXT | short | weekly profile | weekly profile (market profiling) | "that prompted me to stick with the short side for now" | weekly profile | "for now" |
| 5 | 18 | CONTEXT | short | V POC | volume point of control, negative balance just below it | "first establishing a negative balance just below it" | VAH/VAL/POC | none stated |
| 6 | 20 | CONTEXT | short | single print area | single prints | "aggressive hands also decided to push the market down here" | single prints, delta / aggressive sellers | none stated |
| 7 | 21 | CONTEXT | short | 18,258 (role: caution level, above the entry) | price range 18,258 | "there it can then get uncomfortable if the market goes above it" | swing high | "if the market goes above it" |
| 8 | 24 | STOP_SET | short | above the level touched pre-market ("aggressive seller") ; exact stop price not stated | where the stop was touched pre-market and almost reached in main trading hours | "That's how I always determine a logical stop loss for myself." | delta / aggressive sellers, time of day | "If it goes above that, it can get uncomfortable" |
| 9 | 27 | STOP_MOVE | short | 257 (written "257", after the 18,258 range is mentioned) | market done up there | "I placed the stop at 257" ; moved after the session had got going (after row 8) | swing high | "I assumed the market was done up there and had fixed everything" |
| 10 | 30 | TARGET_SET | short | intraday price gap in main trading hours (level not stated) | intraday gap, ran through "extremely strongly and quickly" | "which I defined as an intermediate target for myself" | single prints / gap [new source: intraday price gap] | none stated |
| 11 | 31 | CONTEXT | short | market opening far below yesterday's range | prior-day profile | "very, very deep below the current price range of yesterday's profile" | prior-day profile | none stated |
| 12 | 34 | CONTEXT | short | stop level up above (role: stop reference) | the position start and the stop | "My stop loss was up here after the market had initially cleared everything out" | swing high | none stated |
| 13 | 36 | LESSON | short | price gaps | gap | "those are always nice areas that I like to define as targets" | intraday price gap [new source] | none stated |
| 14 | 41 | LESSON | short | price range ahead of the market | today's profile, volume | "Whenever the last volumes before such a price range are not traded, caution is advised" | today's profile, HVN/LVN or volume step | none stated |
| 15 | 42 | PARTIAL | short | the price range reached on the way down (level not stated) | price range picked up, volume not traded before it | "which prompted me to first reduce my position" | today's profile, HVN/LVN or volume step | "what you have, you have" |
| 16 | 48 | HOLD | short | UX sentiment moved "from here back over here" (no numbers) | UX sentiment (positioning of derivative investors) | "which prompted me to keep my short position for now" | other market: "UX sentiment" [?] | "for now" ; many went long, derivative investors "almost always wrongly positioned" |
| 17 | 51 | EXIT | short | the stop-loss level he had drawn in (price not stated) | price shot through | "the market then shot past my stop-loss level" ; exit type stop | none stated | none stated |
| 18 | 52 | PROOF (BEFORE) | short | up above the re-entry area | selling pressure | "there was really aggressive selling up here" | delta / aggressive sellers | none stated |
| 19 | 54 | PROOF (BEFORE) | short | back into the price range, then below it | price range | "we went back into the price range and then we actually went below this price range" | profile / acceptance area | none stated |
| 20 | 56 | LOCATION | short | "this wonderful and carefully defined range that I had previously set up" (level not stated) | predefined range | "within this wonderful and carefully defined range" | profile (prior defined range) | none stated |
| 21 | 57 | ENTRY | short | the predefined range | chart | "let's go short again because the conditions seemed right" ; order type unknown | delta / aggressive sellers, price range | none stated |
| 22 | 59 | PARTIAL | short | low volume (predefined price range, level not stated) | low volume area | "at the low volume I took out a position again" | HVN/LVN or volume step | none stated |
| 23 | 61 | TARGET_SET | short | predefined: "where I actually wanted to go, but we weren't there yet" (level not stated) | predefined target area | "I had predefined to say that's where I actually wanted to go" | HVN/LVN or volume step | none stated |
| 24 | 63 | PARTIAL | short | "hit the mark" (level not stated) | price reached the mark | "it hitting the mark means closing out another position here" | HVN/LVN or volume step | none stated |
| 25 | 64 | HOLD | short | rest of the position, towards "my take profit" (level not stated here) | take profit | "Let the rest run" | none stated | "let's see if this thing still hits my take profit" |
| 26 | 65 | CONTEXT | short | whole market | trend | "The trend is short" | market trend | "The entire market is currently trending downwards" |
| 27 | 67 | CONTEXT | short | up above | repeated failure to hold highs | "it hasn't made a decision up here to really go long sustainably" | swing high | "Otherwise, I would never have made this re-entry" |
| 28 | 70 | LESSON | - | UX sentiment | derivative investors' positioning | "derivative investors are usually wrong" | other market: "UX sentiment" [?] | very strong long positioning means the market is more likely to go down; the negative-side sentence is cut off [?] |
| 29 | 75 | CONTEXT | short | sentiment at zero | UX sentiment at zero | "there'll probably be a bit of short-term lethargy" | other market: "UX sentiment" [?] | "once the extreme situation has changed" momentum builds again |
| 30 | 80 | LESSON | short | pullback in nowhere ranges | room to the downside | "momentum trading ideas actually make sense" | none stated | "when you have plenty of room to the downside, otherwise you'll keep getting hit" |
| 31 | 82 | LESSON | short | swing trade | levels | "it's nothing more than a trade from one level to the next that I've simply predefined" | none stated | none stated |
| 32 | 84 | TARGET_SET | short | 411 range | where the orders were placed | "I plan my exit here in the 411 range" | order book / big orders | none stated |
| 33 | 84 | EXIT | short | 411 range | order levels | "plan my exit here in the 411 range" ; actual fill price and result not stated [?] | order book / big orders | exit type target (implied) |
| 34 | 85 | REJECT | short | 411 range | levels with opposite reaction | "important to stick to it" (do not deviate from the predefined exit) | order book / big orders | "They're always price ranges where I assume the market might initially do the opposite of what I'm planning" |
| 35 | 86 | CONTEXT | short | 411 range | other participants at the same level | "many people do that" | order book / big orders | "Otherwise, it would have broken through directly" |
| 36 | 88 | LESSON | short | take profit | break-through case | "Then I would have very likely chosen a much lower take profit" | none stated | only if the market had broken through directly |
| 37 | 89 | LESSON | - | predefined price ranges | profit levels | "always important to simply use predefined price ranges where you take your profits" | none stated | none stated |
| 38 | 93 | LESSON | - | - | swing trades | "really important to be patient when you have swing trades" | none stated | none stated |
| 39 | 95 | LESSON | - | balanced market phases | back-and-forth trading | "trade back and forth with your positions in such balanced market phases" | market phase (balance) | none stated |
| 40 | 97 | CONTEXT | - | day direction | context | "The direction you want to take for the day must be predefined" | weekly / today's profile | "that can change if the context breaks" |

## 3.3 Trade blocks
```
TRADE 1 - short - rows 3-17
state (day/week): weekly profile from market profiling, V POC with negative balance just below it, single print area; "I identified ... short side for now"; market opened "very, very deep below" yesterday's range
location: "typical pre-market highs" taken out (after a V reversal) ; level type: swing (pre-market highs) with VPOC / single prints context
leading signal: weekly profile with VPOC and single prints ("aggressive hands")
trigger: at the pre-market highs; set-up shown afterwards ; entered BEFORE or AFTER proof: unknown (no proof is named for this entry)
entry order type: unknown ; placed before the touch: unknown
initial stop: above the level touched pre-market by the aggressive seller ("That's how I always determine a logical stop loss") ; distance: not stated ; % of price: unknown (distance not stated) ; the only number near the stop is 18,258 as the "uncomfortable" level above
target: intermediate target at an intraday price gap in main trading hours ; distance: not stated ; stated R:R: unknown
management: STOP_MOVE row 9 (stop to 257, "market was done up there") ; PARTIAL row 15 ("reduce my position", price range ahead where the last volumes are not traded) ; HOLD row 16 (UX sentiment)
exit: stopped out, "shot past my stop-loss level that I had drawn in here" ; exit type: stop
rejects: none in this trade (no REJECT row in rows 3-17)
information sources: weekly profile, VAH/VAL/POC, single prints, prior-day profile, swing high, delta / aggressive sellers, HVN/LVN or volume step, other market ("UX sentiment" [?]), time of day (pre-market), intraday price gap [new source]
outcome: partial taken, remainder stopped out ; no money, points or R stated
horizon: pre-market into main trading hours, "a few hours of back and forth"
mirror stated?: no - do not assume
```
```
TRADE 2 - short - rows 21-34 (pre-entry rows 18-20)
state (day/week): "The trend is short. The entire market is currently trending downwards" ; market "hasn't made a decision up here to really go long sustainably"
location: "this wonderful and carefully defined range that I had previously set up" ; level type: acceptance area (predefined range; level price not stated)
leading signal: "really aggressive selling up here" and price going back into the range and then below it
trigger: price below the range after the aggressive selling ; entered BEFORE or AFTER proof: after (rows 18 and 19 come first)
entry order type: unknown ; placed before the touch: unknown
initial stop: not stated for the re-entry ; distance: not stated ; % of price: unknown
target: predefined low volume area ("where I actually wanted to go") and "my take profit" (level not stated), plus the 411 range exit ("where the orders were ultimately placed") ; distance: not stated ; stated R:R: unknown
management: PARTIAL row 22 (at the low volume) ; PARTIAL row 24 ("closing out another position here") ; HOLD row 25 ("Let the rest run")
exit: plan to exit in the 411 range where orders were placed; the final fill is not narrated [?] ; exit type: target (implied)
rejects: row 34 (sticking to the predefined exit; he does not deviate because the level draws an opposite reaction) ; rows 27 (no re-entry without the market failing to go long)
information sources: delta / aggressive sellers, profile / acceptance area, HVN/LVN or volume step, market trend, swing high, order book / big orders (411 range), other market ("UX sentiment" [?])
outcome: not stated (no money, ticks or R)
horizon: "It took quite a while"; "drifted around here for ages, then did another pullback"
mirror stated?: no - do not assume
```

## 3.4 Rejections and conditions
- Row 34 (REJECT): do not deviate from the predefined exit in the 411 range ("it's important to stick to it"); the reason is that these levels are where the market "might initially do the opposite".
- Row 36 condition: a much lower take profit only if the market had broken through the 411 range directly.
- Row 27 condition: no re-entry short unless the market had shown it had not decided to go long sustainably up there.
- Row 7 condition: caution above 18,258 ("get uncomfortable if the market goes above it").
- Row 8 condition: if price goes above the level where the aggressive seller is, it gets uncomfortable (this is the stop rule).
- Row 9 condition: the 257 stop is only tied to "the market was done up there".
- Row 14 condition: caution when the last volumes before a price range are not traded (leads to the partial in row 15).
- Row 16 condition: hold the short "for now" because the derivative investors went long (contrarian, row 28).
- Row 25 condition: "let's see if this thing still hits my take profit".
- Row 30 condition: momentum ideas only "when you have plenty of room to the downside".
- Row 40 condition: the day direction changes only "if the context breaks".

## 3.5 Verbatim anchors
> "first of all, what you see here is my short entry into the DAX."
**Source GPS: ujedEcmvBMk | BEGIN**

> "typical pre-market highs"
**Source GPS: ujedEcmvBMk | BEGIN**

> "We had taken out these highs here."
**Source GPS: ujedEcmvBMk | BEGIN**

> "that prompted me to stick with the short side for now"
**Source GPS: ujedEcmvBMk | BEGIN**

> "had led to the market first establishing a negative balance just below it as a result."
**Source GPS: ujedEcmvBMk | BEGIN**

> "aggressive hands also decided to push the market down here."
**Source GPS: ujedEcmvBMk | BEGIN**

> "let's also note the price range 18,258."
**Source GPS: ujedEcmvBMk | BEGIN**

> "there it can then get uncomfortable if the market goes above it."
**Source GPS: ujedEcmvBMk | BEGIN**

> "That means the aggressive seller is still there."
**Source GPS: ujedEcmvBMk | BEGIN**

> "If it goes above that, it can get uncomfortable."
**Source GPS: ujedEcmvBMk | BEGIN**

> "That's how I always determine a logical stop loss for myself."
**Source GPS: ujedEcmvBMk | BEGIN**

> "I placed the stop at 257 because I assumed the market was done up there and had fixed everything."
**Source GPS: ujedEcmvBMk | BEGIN**

> "which I defined as an intermediate target for myself."
**Source GPS: ujedEcmvBMk | BEGIN**

> "very, very deep below the current price range of yesterday's profile."
**Source GPS: ujedEcmvBMk | BEGIN**

> "My stop loss was up here after the market had initially cleared everything out."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "those are always nice areas that I like to define as targets."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "Whenever the last volumes before such a price range are not traded, caution is advised"
**Source GPS: ujedEcmvBMk | MIDDLE**

> "which prompted me to first reduce my position"
**Source GPS: ujedEcmvBMk | MIDDLE**

> "what you have, you have."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "I saw that an incredible number went long, which prompted me to keep my short position for now."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "the market then shot past my stop-loss level that I had drawn in here, flushing me out of the market."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "there was really aggressive selling up here."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "we went back into the price range and then we actually went below this price range"
**Source GPS: ujedEcmvBMk | MIDDLE**

> "within this wonderful and carefully defined range that I had previously set up, I would take action."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "let's go short again because the conditions seemed right."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "at the low volume I took out a position again because that was the price range."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "I had predefined to say that's where I actually wanted to go, but we weren't there yet."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "it hitting the mark means closing out another position here."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "Let the rest run."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "now let's see if this thing still hits my take profit."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "The trend is short."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "The entire market is currently trending downwards."
**Source GPS: ujedEcmvBMk | MIDDLE**

> "it hasn't made a decision up here to really go long sustainably."
**Source GPS: ujedEcmvBMk | END**

> "Otherwise, I would never have made this re-entry."
**Source GPS: ujedEcmvBMk | END**

> "derivative investors are usually wrong."
**Source GPS: ujedEcmvBMk | END**

> "there'll probably be a bit of short-term lethargy."
**Source GPS: ujedEcmvBMk | END**

> "Well, when you have plenty of room to the downside, otherwise you'll keep getting hit."
**Source GPS: ujedEcmvBMk | END**

> "it's nothing more than a trade from one level to the next that I've simply predefined"
**Source GPS: ujedEcmvBMk | END**

> "If I plan my exit here in the 411 range where the orders were ultimately placed"
**Source GPS: ujedEcmvBMk | END**

> "well, then it's important to stick to it"
**Source GPS: ujedEcmvBMk | END**

> "They're always price ranges where I assume the market might initially do the opposite of what I'm planning."
**Source GPS: ujedEcmvBMk | END**

> "And as you can see here, many people do that."
**Source GPS: ujedEcmvBMk | END**

> "Then I would have very likely chosen a much lower take profit for this swing trading idea."
**Source GPS: ujedEcmvBMk | END**

> "it's always important to simply use predefined price ranges where you take your profits"
**Source GPS: ujedEcmvBMk | END**

> "It's really important to be patient when you have swing trades."
**Source GPS: ujedEcmvBMk | END**

> "The direction you want to take for the day must be predefined and that can change if the context breaks."
**Source GPS: ujedEcmvBMk | END**

## 3.6 Ambiguity flags
- Opening intro: "I executed partial buys and partial sells" and later "a long swing trade" (row 30-31): only shorts are shown; "buys" and "long" are not tied to any long trade. Unresolved.
- Row 9: "257" is written without the "18," prefix; 18,258 is given as the uncomfortable level above. Whether the stop is 18,257 or something else is not stated.
- Row 16, 28, 29: "UX sentiment" is probably a mistranscription of an index sentiment measure; the transcript says only "UX". Copied as is.
- Row 28: "Then the market is more" ends mid-sentence in the raw file; the negative-sentiment outcome is not stated.
- Row 22 and 24: "at the low volume I took out a position" and "it hitting the mark means closing out another position" may describe one event or two. Recorded as two PARTIAL rows.
- Row 32-33: the 411 range is not tied explicitly to trade 1 or trade 2, and the exit fill itself is not narrated. Recorded under trade 2 as the surviving position.
- Row 17-18: "re-entry for myself down here" (row 18 area) comes before the "aggressive selling up here" clause in the same sentence; time order of ENTRY and proof taken from the later sentences (rows 18-21).
- Row 10: "huge intraday price gap" is not in the allowed info list; flagged as a new source.
- Row 8: "the aggressive seller" may be the same as the "single print area" actors in row 6; not resolved.

PASS: 0 problem(s)
