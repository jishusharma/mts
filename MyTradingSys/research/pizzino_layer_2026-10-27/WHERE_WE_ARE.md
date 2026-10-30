# Pizzino layer: where we are (2026-10-30)

Jason Pizzino and Michael Pizzino (two analysts, one family channel set; never merged with Michael van de Poppe). Sources: `method_extraction.md` (ME, quotes with video id and timestamp), `method_jason.md`, `method_michael.md`; rules: `SPEC.md`; code: `MyTradingSys/backtest/layers/pizzino/`. Read the files, not this note, for the exact rule text.

## What "1-bar / 2-bar / 3-bar" means in the sources

There are two different things with "bar" in the name. They stay apart (SPEC section 0).

| Thing | Who | What the source says | Quote (ME line, video, time) |
|---|---|---|---|
| 1-bar / 2-bar / 3-bar **trend states** | Michael | "one-day one-bar, two-bar, and three-bar time frames, which is basically just different measurements of time to let us know what the trends are doing"; each is up / down / neutral; all three agree = confluence | ME:22, a0sy0EW_nSA 2026-06-29 [00:02:40]; ME:29, 8TvLQ87KrfU 2026-08-26 [00:02:40] |
| (same) | Michael | the tool is **Gann Swing Pro**; 1-bar = low-term, then mid-term, 3-bar = high-term | ME:29; ME:36, 326kGNFr8tM 2026-10-20 [00:08:01] |
| (same) | Michael | 1-bar and 2-bar turning first "is always a precursor" for the next one | ME:43, ZYrKqu8TxHo 2026-08-20 [00:01:27] |
| (same) | Michael | the 1-bar trend flips at a stated price ("break ... above around $61,200"); target = next pivot | ME:66, a0sy0EW_nSA [00:03:11] |
| **Three bars up from the low** (bar count) | Jason | three bars in a row of higher high + higher low from a significant turning point (usually an all-time high/low, not always); used on daily, 3-day and weekly bars | ME:82, CY7-W_b7UAU 2026-09-08 [00:05:19]; ME:89, GaHjNt91mPU 2026-10-23 [00:06:32]; ME:96, CY7-W_b7UAU [00:08:01] |
| **50% line** | both | midpoint of the prior major run, top to bottom ("Top, bottom, halfway through ... $92,000"); above = strong half, below = weak half; a retest of the 50 from underneath that fails = weak | ME:126, RCq5pfzA4oo 2026-09-17 [00:05:50]; ME:133, Hlot1KhrlMs 2026-09-22 [00:17:50]; ME:154, Pg8Z7BezFeo 2026-10-01 [00:07:47]; ME:161, 8TvLQ87KrfU [00:02:55] |
| Break and retest | both | consecutive closes beyond a level, then a short retest; hold = continuation | ME:235, FPaXP3LE6c8 2026-10-07 [00:08:23]; ME:214 |

Time frames named in the sources: daily ("one-day"), 3-day and weekly. **4h and anything lower is never mentioned** (NOT_IN_DATA).

## SOURCED, OURS, unknown

- SOURCED (14, SPEC P01-P14): three nested states, three degrees, confluence = all agree, 1-bar leads, 3-bar count length, HH+HL test, significant turning point, D/3D/W bars, 50% = (top + bottom) / 2, strong/weak half, close-beyond confirms a break, retest read, target = next pivot, invalidation = change of trend beneath the swing bottom.
- OURS (18, SPEC P15-P32): the pivot formula (strict fractal, degree d uses n = d), alternation, the state formula, lead window L = 5, significance window W = 50, count anchored on degree-3 pivots, 50% leg = last degree-3 PH/PL, N = 2 closes, tol 0.5%, R = 20 bars, entry/stop/target numbers, 00:00 UTC day.
- Unknown (NOT_IN_DATA, ME:289-292): Gann Swing Pro's real swing algorithm and bar sizes (proprietary; our n = 1/2/3 fractal is a stand-in, ambiguity A1), whether Jason's three bars equals Michael's 3-bar, retest tolerance, position size and stop distance.

## Lower time frames (all OURS)

The traders never apply the method below the daily chart. Our rule, written before any data was looked at, is in `MyTradingSys/backtest/layers/pizzino/pizzino_levels.py` (`LTF_RULE`): the same pivot, state, count, 50% and retest maths run unchanged on 4h, 1h, 15m, 5m and 1m bars (lower bars folded from 1m on UTC boundaries), and each lower frame is read **nested under its parent**: 4h under 1d, the rest under 4h. "Aligned" = the frame's state sum has the same sign as the parent's half (strong = +1, weak = -1). Whether lower frames add anything is a pz-4 question, not a claim.

## Done

| Card | What | Where |
|---|---|---|
| pz-1a/1b/1c | method extraction, Jason, Michael, merge | `method_*.md` |
| pz-2 | SPEC: rules, hand-worked examples, 16 trial-ledger variants | `SPEC.md` |
| pz-3 | indicator functions + tests | `layers/pizzino/pizzino_indicators.py` |
| this card | level export (any time frame, JSON) and the live aid overlay | `layers/pizzino/pizzino_levels.py`, `tools/live_aid` |

## Remaining

1. pz-4-backtest: BTC daily first, DEV/VALIDATION only until the trial ledger is complete, fee-net; holdout read once. No verdict before that.
2. pz-5-confluence-and-live: confluence with the other layers; the CBP feed (their daily videos) gives the traders' own stated levels and states; compare them to what our code computes on the same day (that is the only check that our 1/2/3-bar stand-in matches Gann Swing Pro).
3. Open audits already queued: `gemini-param-labels-pizzino`, `gpt-audit-formulas-vs-pizzino-layer`.
