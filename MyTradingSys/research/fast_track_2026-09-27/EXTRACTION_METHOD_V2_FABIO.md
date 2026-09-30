# EXTRACTION METHOD V2 - FABIO APPENDIX (for DSA web model / Haiku; merge into EXTRACTION_METHOD_V2.md)

Purpose: extract ONE Fabio Valentini transcript as trades and decisions in order, not as one-line rules. Built from the
line-by-line reading FABIO_LINE_BY_LINE_fZlNGWvd2Ko.md. Fabio is a separate layer, never a Tom filter.
Input: `raw_transcripts_canonical/<id>_raw.txt`. Output: `extracts/processed/fabio_valentini/<id>/extract_<id>.md.new`.

## 1. Steps
1. **Triage (write it at the top).** Type = WALKTHROUGH (his own position, live or replay), LECTURE (concepts with
   hypothetical "you can enter here" examples) or MINDSET. For LECTURE/MINDSET do only section 2 rows marked "teaching" and
   the checklist; do not invent trade blocks. State the instrument only if the transcript names it.
2. **Read the whole file in fixed ranges** (e.g. 60 lines at a time) from line 1 to the last line. No skimming, no search-only
   reading. Write the range you read before its rows, so a checker can see nothing was skipped.
3. **Decision rows** (section 2) for every passage where he looks at something or acts. Teaching asides get one row, type teaching.
4. **Trade blocks** (section 3): one per position, built only from the rows.
5. **Day block** (section 4).
6. **Ambiguities** list: anything with two readings stays open; say both readings.
7. **Gate:** `python scripts/dev/verify_extract_quotes.py <file>` must PASS (quote format in section 6).

## 2. Decision row (one per passage, in transcript order)
| field | how to fill |
|---|---|
| id | D01, D02 ... |
| lines / time | `L58-61 [2:19-2:29]` from the file |
| side in trade | FLAT / LONG / SHORT at that moment (write it every row) |
| looking at | the object: consolidation, level, big trades, aggression, absorption, candle body/wick, wall, day P&L, day type, session |
| who | which side acts and what happens to it: `sellers: effort, no result (absorbed)` / `buyers: effort, result (control)` / `both: no result` |
| decision | one of WAIT, ENTER, ADD/RELOAD, REDUCE RISK, STOP TO ZERO, TRAIL/RATCHET, PARTIAL, EXIT, SKIP/REJECT, STOP SESSION, TEACHING |
| trigger | the event that caused the decision, in his words |
| verbatim | the shortest exact quote that carries the decision (quote block, section 6) |
| numbers | only numbers he says ($, R:R, contracts, times). Never compute new ones |

## 3. Trade block (one per position)
| field | content |
|---|---|
| state | day type and session phase before entry (chop, balance, directional); what happened earlier in the day |
| location | the level or area (consolidation, absorption level, pivot, wall) |
| pressure relation | which side pressed first and was absorbed; does the entry go WITH that pressure or AGAINST it (failed auction) |
| trigger | the entry event |
| side | LONG / SHORT |
| stop rule + width | where the stop is (behind which level) and width in points/ticks/$ if said; else UNKNOWN |
| target rule | fixed level, day extreme, none (managed) |
| management | ordered list of every stop move / add / reduce, each with its trigger event and line range |
| exit | reason in his words and line |
| rejected | what he says he did not do or would not do, and why (includes "I could have held") |
| information | every source he names: big trades, aggression, absorption, footprint, CVD, profile, heat map, day P&L |
| budget | where the risk comes from (day's profit, fixed $, prop rule) |

## 4. Day block
P&L path with spoken numbers and lines (before session, after each trade, "worst case" statements); the floor or stop rule;
trades per side; whether he stops after a target, after recovery, or at break even.

## 5. Fabio vocabulary (map words, do not paraphrase them away)
| his words | meaning to record |
|---|---|
| "absorbed", "effort but no result", "punch to the wall" | that side aggressed and price did not move: record WHICH side |
| "took control", "aggression", "solid aggression" | that side aggressed and price moved (effort with result) |
| "failed auction (of the seller)" | the named side pushed and failed; the trade goes the other way |
| "big trades" | large prints; note side and where (body/wick, at a level) |
| "cover behind / below this level/low", "protection level" | STOP placement. Never a target |
| "stop loss to zero", "risk free" | stop at entry (BE) |
| "worst case scenario, I close $X" | stop ratchet expressed as day P&L locked |
| "loading", "scaling in", "reload" | adds; record whether still at risk and where (price vs first entry) if said |
| "new pivot" | the next level that takes over if the current one fails |
| "wall" | passive liquidity (heat map / L2), not order flow |
| "consolidation", "no result from buyers ... no result from sellers" | balance; inside a trade it is a management point, not an exit by itself |
| "potential acceleration level" | balance edge where a break should run |

## 6. Quote format (gate)
```
> "exact words from the transcript"   (one quote per block)
**Source GPS: <VIDEO_ID> | BEGIN|MIDDLE|END** (L<a>-L<b>, [m:ss]-[m:ss])
```
Words must match the transcript (punctuation and case ignored). BEGIN/MIDDLE/END = which third of the text the quote is in.

## 7. Checklist: what past Fabio extractions missed (check each; answer yes/no in the output)
1. Losing trades and the loss side of the day recorded (fZlNGWvd2Ko extract dropped two failed shorts).
2. Side on every row; side flips within a session recorded.
3. For each entry: which side was absorbed BEFORE the entry, and whether the entry is with or against that pressure.
4. Every stop move has its trigger event (opposite side absorbed? own side control? own side failed?), not "trail in profit".
5. "Cover", "protection level" filed as STOP, not target (FR-87 was filed as target).
6. Adds: at risk or after BE? funded by what (day profit vs trade profit)?
7. Reductions of risk that are not exits ("lower my risk") kept as REDUCE, not merged into "exit when big trades stop".
8. In-trade consolidations: hold or exit, and why.
9. Exit reason in his words, plus what he says he gave up (counterfactual) and the day type he cites.
10. Day budget: prior-session P&L, day floor, "worst case" day figures.
11. R data kept (e.g. "$980 to make potential $25,000"); never dismissed as "just numbers".
12. Nothing merged across videos at extraction time; one row never cites two events.
13. Conditionals kept whole ("if this level failed, this one become the new pivot"), not cut to their verb.
14. Ambiguous sentences listed with both readings, not resolved.

## 8. Worked example (fZlNGWvd2Ko, L97-L116)
Rows:
| id | lines | side | looking at | who | decision | trigger |
|---|---|---|---|---|---|---|
| D18 | L97-106 [3:49-4:11] | LONG | consolidation in the trade, buyers wall | sellers absorbed; buyers no result | WAIT (plan: risk free or tight stop if it breaks down) | a breakdown "will probably revisit this level here" |
| D20 | L110-116 [4:20-4:36] | LONG | sell acceleration, aggressive buyers | sellers: effort, stopped (absorbed) | STOP TO ZERO | "the sellers got stopped again in the movement" |

> "Now my position is stop loss to zero. Why? Because we already saw that the sellers got stopped again in the movement"
**Source GPS: fZlNGWvd2Ko | MIDDLE** (L112-115, [4:27]-[4:33])

Wrong (old extract style): "R6: Trail stop in profit after breakout" and "R7: Cover behind the new low (target)". Right: the
stop moves to zero because the OPPOSITE side's push was absorbed; the consolidation is a hold with a conditional stop; "covered
below this low" is the stop under the pullback low of a long.
