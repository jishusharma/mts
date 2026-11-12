# Brief: V2 extracts from transcripts already on disk (cards gemini-tom-*-1113, gemini-fabio-shorts-extract-1113)

1. Transcripts are tracked at raw_transcripts_canonical/<id>_raw.txt. Make NO caption fetch and NO YouTube request.
2. Format: copy an existing V2 file (extracts/v2/tom/Ld1dhjGdTCA_v2.md, extracts/v2/fabio/*_v2.md). Each quote is `> "verbatim line"` then `**Source GPS: <id> | BEGIN|MIDDLE|END**`, `[mm:ss]`, label SOURCED.
3. The position tag must match where the quote sits in the transcript (first, middle, last third).
4. Line 1 names the transcript and the speaker (guests are not Tom).
5. Run `python scripts/dev/verify_extract_quotes.py <file>` until exit 0 with at least 1 quote. Fix the quote or the tag, never the checker. Unverifiable quotes are dropped.
6. Commit on your gemini-q branch in small batches. Never: proxy, VPN, cookies, edits to fetch_captions*.py or verify_extract_quotes.py, .secrets/.env, live tree.
