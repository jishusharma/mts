# NK deep pass brief (flash_deep)

Read ONLY `raw_transcripts_canonical/<id>_raw.txt` (Hindi caption). No web, no YouTube, no background knowledge.
Write `MyTradingSys/research/nk_stocktalk_1113/flash_deep/<id>/EXTRACT.md`, same shape as `flash/<id>/EXTRACT.md`.

For the video, list EVERY parameter and rule he states, each with its own block:
`> "exact Hindi caption line"` then `**Source GPS: <id> | BEGIN|MIDDLE|END**`, `- [mm:ss]`, `- **TRANSLATION:** English`.
Cover: indicator settings (RSI zone and levels, lengths, averages), timeframes, entry, exit, stop, targets, filters, what he says it is NOT, no-trade cases, hedge/expiry rules, anything on crypto.
Minimum 6 distinct quotes, or write `NOT_STATED: <what>` per missing item. A number counts only if it sits inside a quoted line; otherwise NOT_SEEN.
Quotes are copied exactly, Devanagari as in the file, one caption line each (no stitching, no romanising).
After writing run `verify_extract_quotes.py` on your file, then `python MyTradingSys/research/nk_stocktalk_1113/review/harness.py check` with PYTHONUTF8=1, until both exit 0.
