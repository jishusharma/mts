# EXTRACTION METHOD V2 - trader transcripts to decision logs and trade blocks

Version 2, 2026-09-30. It replaces rule-row extraction ("in-vivo codes + tiered rules") for trade-bearing transcripts.
Evidence for the change: TOM_LINE_BY_LINE_4MoNjEQ2Dd8.md (sections B4-B6) and MISSING_PIECES_2026-09-30.md (section 3).
Audience: DSA web model, Qwen, Haiku. One worker reads ONE transcript and writes ONE file. Everything you need is in this file.

## 1. Why V2
Old extractions produced 40+ codes and 20+ rules per video, each with one quote. The system could not rebuild a single trade
from them. This is what was lost:
- The ORDER of events. Tom enters AT the location first and reads the proof AFTER entry. The engine waits for proof first.
- The "as long as <level> holds" conditions. Each one is the stop rule and the hold rule.
- What the trader REJECTED and why (not scalping, not adding in a low-volume area, not moving the stop early).
- Management as a sequence: partials, stop moves, adds, exit reason.
- Role of a level. A big order that is later a stop reference was filed as a "target projection".
- Open profit vs planned target. "161 on the clock" was read as a target.
- Position tags. 5 of 7 checked tags were wrong, and nobody ran the checker.
- Instrument. It was guessed and written as fact.
- Taxonomy forcing. A return-to-value long was filed as "trend continuation" with a trend the trader never mentioned.
V2 records what the trader looks at, decides and does, in order, per trade. Rules are derived later, by someone else.

## 2. Inputs and set-up
1. Transcript: `raw_transcripts_canonical/<VIDEO_ID>_raw.txt`. The text after the `# ---` header line is the body.
2. Work in chunks of about 2,000 characters, in order, from the first character to the last. Do not skip. Do not summarise
   ahead.
3. For every chunk note its position: pos% = (character offset of the chunk start) / (body length) x 100, rounded to a
   whole number. If the transcript has `[m:ss]` markers, also record the time.
4. Keep a scratch list while reading: every price, level, time, size, side, and the words "stop", "target", "take profit",
   "close out", "add", "buy", "sell", "long", "short", "as long as", "I'm out", "I don't", "wait".

## 3. Output file
Path: `extracts/v2/<trader>/<VIDEO_ID>_v2.md` (or the path your task names). The file is LF-only ASCII. Sections are
written in this order:

### 3.1 Header (fill every line; write `unknown` instead of guessing)
```
video_id: <id>
trader: <name>
title: <from header line>
instrument_stated: <exact words, or "not stated">
instrument_inferred: <guess + reason, or "none">   (never copy the guess into other fields)
tick_size: <stated, or "unknown">
session / time of day: <stated words, or "unknown">
translation_warning: <yes/no; yes if the transcript says it was translated or auto-captioned>
body_chars: <number>
n_decision_rows: <number>
n_trades: <number>
```

### 3.2 Decision log (one row per decision point, in transcript order)
A decision point is any moment where the trader chooses, or says he would choose, one of the types below.
```
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition ("as long as") |
```
Allowed `type` values (use exactly these):
- CONTEXT: reads the day or week story (profile, open location, trend, balance).
- LOCATION: names the area where he wants to trade.
- ENTRY: in, or order placed. Say which: market, limit, stop order, or unknown.
- STOP_SET: initial stop.
- TARGET_SET: initial target.
- PROOF: a confirmation seen. Mark BEFORE or AFTER entry.
- HOLD: decides to stay in, with its condition.
- REJECT: decides NOT to do something, with the reason.
- ADD: adds size.
- PARTIAL: takes part off.
- STOP_MOVE: moves the stop, with the new level and the reason.
- EXIT: flat, with the reason.
- LESSON: a general statement; not a trade action.
- ERROR: the trader says he made a mistake.

Row rules:
1. One row per decision. If one sentence has two decisions (stop and target), write two rows.
2. `decision` holds 3 to 15 words copied from the transcript. The full quote goes in section 3.5.
3. `condition` holds every "as long as ...", "if it drops below ...", "we need a close above ..." tied to that decision.
   Write `none stated` if there is none. Do not leave it blank.
4. `info used`: list only the sources named in or right around the passage (see the list in section 5, item 7).
5. Unclear words: copy them and add `[?]`. Do not repair them.

### 3.3 Trade blocks (one per trade; a trade runs from first ENTRY to final EXIT on one idea)
```
TRADE <n> - <side> - rows <first #>-<last #>
state (day/week): <his words>
location: <his words> ; level type: <VAH/VAL/POC/tail/acceptance area/swing/order/other/unknown>
leading signal: <what made him look>
trigger: <what made him act> ; entered BEFORE or AFTER proof: <before/after/unknown>
entry order type: <market/limit/stop/unknown> ; placed before the touch: <yes/no/unknown>
initial stop: <rule in his words> ; distance: <ticks or points as stated> ; % of price: <only if the price and the distance
  are both stated; show the arithmetic> ; else unknown
target: <rule in his words> ; distance: <as stated> ; stated R:R: <as stated or unknown>
management: <ordered list: PARTIAL / STOP_MOVE / ADD with row numbers>
exit: <reason in his words> ; exit type: <target / stop / manual / time / unknown>
rejects: <each REJECT row, with its reason>
information sources: <from section 5, item 7>
outcome: <money or ticks as stated; R only if the risk is stated>
horizon: <his words, or minutes if stated>
mirror stated?: <yes + quote row #, or "no - do not assume">
```

### 3.4 Rejections and conditions (collect them again here, one line each)
Every REJECT row and every "as long as" condition, with its row number. These become stop rules and filters later.

### 3.5 Verbatim anchors (machine-checked; exact format)
```
line 1:  > "<exact words from the transcript>"
line 2:  **Source GPS: <VIDEO_ID> | BEGIN**
```
(Write the two lines without the "line 1:" / "line 2:" labels; the real example below shows the result.)
- The GPS line comes directly after the quote line.
- BEGIN = first third of the body, MIDDLE = second third, END = last third (by character position).
- Copy the words exactly. Case and punctuation are ignored by the checker; words are not.
- Do not join two passages in one quote, and do not use "..." inside an anchor quote. Split it into two anchors instead.
- One anchor for every ENTRY, STOP_SET, TARGET_SET, STOP_MOVE, PARTIAL, ADD, EXIT and REJECT row.
- HTML entities stay as they are in the file (for example `S&amp;P`). Better: pick a quote without them.
- Only anchor lines may start with `> "`. The checker reads every such line.

### 3.6 Ambiguity flags
List the words that may be mistranslated or that contradict the action. Example: "covered" used where he means "opened".
Give the row number. Do not resolve them.

## 4. Longs vs shorts - symmetry rules
1. Every ENTRY row has `side`. Never leave it blank, and never infer it from the title.
2. Extract longs as fully as shorts. If the video has both, both get trade blocks.
3. Do NOT write the mirrored rule unless the trader states it. Write `mirror stated?: no - do not assume`. Later work mirrors,
   not you.
4. Record which side of the level the entry is on. "Stop below the last low" means the long's stop is under structure. "Sell
   limit below the last volume step" is the short's entry. Keep his direction words exactly.
5. If the trader rejects one side ("the long side is still to be favored"), record that as CONTEXT with the side.
6. Never map his trade to our labels (CT, TC, BO, scalp, trend_healthy). Describe it in his words. The mapping is done later,
   against the code.

## 5. Checklist - things previous extractions missed (tick every box before you submit)
1. [ ] The ENTRY row exists and says BEFORE or AFTER proof.
2. [ ] Each STOP_SET and STOP_MOVE has a level, his reason, and the TIME ORDER (row number).
3. [ ] Each PARTIAL is a separate row. Also count partials he mentions only in summary ("taken profits twice").
4. [ ] Each ADD is a row with its condition (breakout, a step holding, speed) and each REJECTED add is a REJECT row.
5. [ ] Every "as long as", "if it drops below", "we need a closing price" is in the `condition` column.
6. [ ] Each level has a ROLE per row: location, stop reference, target, add trigger, caution. A level can change role later
       (a sell order becomes support). Write each role on its own row. Do not merge them.
7. [ ] `info used` only from this list: prior-day profile, today's profile, weekly profile, VAH/VAL/POC, tail, single prints,
       HVN/LVN or "volume step", VWAP, swing high/low, equal highs/lows ("ledge"), order book / big orders, delta /
       aggressive buyers or sellers, absorption, footprint, market speed, bar close (give the TF), other market (name it), time of
       day, news. Anything else: write it out and flag it `[new source]`.
8. [ ] Open profit is not the target. Record "X on the clock" as open profit, not as a target.
9. [ ] Stated numbers are copied exactly (ticks, points, money, R:R). Nothing is computed unless both inputs are stated.
10. [ ] Instrument is `not stated` unless he names it. Other markets he watches are recorded as information sources.
11. [ ] Time-of-day and bar-close cues are rows (for example "5-minute close", "15-minute close", "1845", "lunch break").
12. [ ] Admitted errors are ERROR rows.
13. [ ] Anchor quotes pass: `python3 scripts/dev/verify_extract_quotes.py <your file>` prints PASS. Fix every MISSING or
        POSITION line before you submit.
14. [ ] Losing trades get the same detail as winners. If the whole video is one winning trade, say so in the header.
15. [ ] No rule tiers, no in-vivo code tables, no cross-references to other videos, no "gaps" essays. They are not asked for.

## 6. Worked example (4MoNjEQ2Dd8, first rows and the trade block, shortened)
Header excerpt:
```
instrument_stated: not stated (he names the NASDAQ and the S&P as markets he watches)
tick_size: unknown
translation_warning: yes ("I translated this video with AI")
```
Decision log excerpt:

| # | pos% | type | side | price/level | what he looks at | decision | info used | condition |
|---|---|---|---|---|---|---|---|---|
| 1 | 3 | LOCATION | long | "wonderful price area" | price area | "looking for a long entry" | prior-day profile | none stated |
| 2 | 3 | ENTRY | long | same | - | "that's why I'm now" [?] (sentence cut) ; order type unknown | - | none stated |
| 3 | 3 | STOP_SET | long | last low | last low | "The stop loss goes below the last low" | swing low | none stated |
| 4 | 3 | TARGET_SET | long | above highs | ledge | "take-profit is set above the highs" | equal highs ("ledge") | none stated |
| 5 | 4 | CONTEXT | long | yesterday's profile | tail, value, POC | "moved back into value, saw rejection at the PC" | prior-day profile, tail, POC | none stated |
| 6 | 9 | PROOF (AFTER) | long | bottom | absorption | "the market was absorbed at the bottom" | absorption | "will it hold this level or break down" |
| 7 | 26 | REJECT | long | 25,600 | seller absorbed | "But I don't want to scalp." | order book, absorption | hold for momentum above |
| 8 | 44 | PARTIAL | long | top | rotation | "let's close out a position" | rotation, orders | stop left "down here" |
| 9 | 51 | STOP_MOVE | long | 600-620 | order levels | "We now adjust our stop" | big orders, today's value | below = "game over" |
| 10 | 92 | STOP_MOVE | long | 603 | 5m volume | "we don't want to go below 603 anymore" | 5m volume by price | below 603 = "break down" |
| 11 | 98 | EXIT | long | top | speed | "That's why I'm out now" | market speed | none stated |

Anchor example:

> "I moved the stop loss to a price range where I simply expect the opposite of my long position. And before that, it doesn't make sense to move the stop-loss."
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE**

Trade block excerpt:
```
TRADE 1 - long - rows 1-40
state: opened lower, buying tail, back into value, rejection at the PC, pullback
location: "business zone" ; level type: acceptance area
trigger: at location ; entered BEFORE proof: before (absorption read afterwards)
initial stop: "below the last low" / "below the business zone" ; distance: 100 ticks (stated at pos 36) ; % of price: unknown
  (tick size not stated)
target: "above the highs" (ledge), value high ~640-644 ; stated R:R: 4:1
management: PARTIAL rows 22,27,32,38 ; STOP_MOVE rows 24,37,39 ; ADD rows 29,30
exit: speed faded at the top ("Speed Off") ; exit type: manual
rejects: scalping the first resistance ; adding inside the low volume area ; moving the stop before an "opposite" level exists
mirror stated?: no - do not assume
```

## 7. Self-check before submit (a weaker model must do all of these)
1. Count the rows with type ENTRY and the trade blocks. Every trade block starts at an ENTRY row.
2. Every trade block has all fields filled (`unknown` is allowed; blank is not).
3. The last row's pos% is at least 95. If not, you stopped reading early: continue.
4. Run the quote checker and paste its last line (`PASS: 0 problem(s)`) at the end of your file.
5. Grep your file for `CT`, `TC`, `trend_healthy`, `tier`. They must not appear (rule 4.6).

## Fabio additions (pending)
