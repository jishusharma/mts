# NK StockTalk layer: review harness (6 reviewers)

Run after the NK extracts land in `flash/<id>/EXTRACT.md` and `argon/<id>/EXTRACT.md` (5 ids, captions unlock 11-13).

## Steps (coordinator)
1. `python MyTradingSys/research/nk_stocktalk_1113/review/harness.py check`: every quote against its Hindi caption
   `raw_transcripts_canonical/<id>_raw.txt`. Exit 0 required before step 3. This replaces `verify_extract_quotes.py`
   for Hindi, because that tool's `norm()` drops every Devanagari word.
2. `... harness.py fill`: writes `CHECKLIST.md` with one section per concept. Each section holds the page's claim and
   params from `concepts.json` (copied from the Conceptualizer `nk-stocktalk` layer), plus each model's Hindi quote and
   its English TRANSLATION line.
3. Start 6 reviewers in parallel. Each reads `CHECKLIST.md`, both EXTRACT.md files per id and the caption files,
   and only those. No YouTube, no web. Each writes `review/<lens>.md`.
4. Merge the findings into the Conceptualizer layer: quotes, params (SOURCED value or NOT_SEEN), rule, and status. Then ship.

## Lenses
| # | Lens | Model | Asks |
|---|---|---|---|
| 1 | quote-vs-caption | Haiku | Is each Hindi quote word for word in the caption, near its [mm:ss]? Script or romanisation changed? |
| 2 | numbers-conditions | Haiku | Is each number and condition (length, timeframe, level, cross) in the caption? Is a NOT_SEEN filled with a guess? |
| 3 | contradiction | Haiku | Do flash and argon disagree, or does an extract disagree with the page claim? Mark each AGREED, SINGLE or CONFLICT. |
| 4 | translation | Sonnet | Does the English say what the Hindi says? Trading terms right (e.g. "मिलेगा"), nothing added or softened? |
| 5 | definition-accuracy | Sonnet | Is the concept defined as he defines it (Hilega Milega parts, what SRP means, his BB use), or as textbook or Gemini prior? |
| 6 | missing-cases | Sonnet | What rule does the caption state that no extract or page row holds (exits, filters, no-trade cases, timeframe)? |

## Reviewer output (`review/<lens>.md`)
One table, one row per finding:
`| concept id | model/line | verdict PASS/FAIL/UNSURE | caption [mm:ss] + 1 short Hindi span | fix (<=12 words) |`
End with a line `Lens <n>: <pass>/<total> PASS`. No trade advice and no sizes. Never put a number in the Fix column
unless it appears in the caption.

## Rules the reviewers keep
- A Hindi quote counts as verified only against the Hindi caption file, never against a translation.
- He states a number = SOURCED. He does not state it = NOT_SEEN. Gemini's earlier RSI 9 / EMA 3 / WMA 21 counts as a guess
  until the caption shows it.
- BTC mappings stay OURS (gap = session open; options = Deribit testnet).
