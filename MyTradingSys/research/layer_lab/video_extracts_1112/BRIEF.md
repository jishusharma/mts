# Brief: Gemini video extraction (cards gemini-extract-*-1112)

Why: YouTube caption fetch is locked until 2026-11-13T02:53Z (HTTP 429, never evaded). Operator wants these videos extracted anyway.

Rules (every card):
1. `python scripts/dev/fetch_captions_timed.py --analyst <Tom|LongShort> --status` (no network). NOT blocked: fetch the one video once (max 1); any 429 = stop, log, go to step 2. A fetched file raw_transcripts_canonical/<id>_raw.txt is the REAL transcript: quote only from it.
2. Blocked or no captions: use Gemini's own video access (agy) and write `<out>/gemini_transcript_<id>.txt`, header `# Source: GEMINI-WATCH, not YouTube captions, UNVERIFIED`, lines `[mm:ss] words`. Verbatim speech only; unintelligible = `[unclear]`, never a guess. Gemini watching a video invents lines, so a quote that is not a verbatim line of that file is dropped.
3. `<out>/EXTRACT.md`, format of research/tom_swing_2026-11-09/extract_M7ompiwv5co.md: each quote `> "verbatim line"` then `**Source GPS: <id> | BEGIN|MIDDLE|END**`, `[mm:ss]`, label SOURCED. Rules/levels the speaker states go in a table, each row citing a quote.
4. verify_extract_quotes.py needs raw_transcripts_canonical/<id>_raw.txt: if absent, copy the Gemini transcript there (git-ignored). Run `python scripts/dev/verify_extract_quotes.py <out>/EXTRACT.md` until exit 0 (fix the quote, never the checker).
5. EXTRACT.md line 1 names the transcript used. If Gemini-watch: add `RE-CHECK against real captions after 2026-11-13T02:54Z` (not yet independent).
6. Cannot do it: write `<out>/NOT_IN_DATA.md` with the blocker. Commit on gemini-q branch; a Claude session reviews and ships.
Never: proxy, VPN, cookies, --fallback, edits to fetch_captions*.py or verify_extract_quotes.py, .secrets/.env, live tree.
