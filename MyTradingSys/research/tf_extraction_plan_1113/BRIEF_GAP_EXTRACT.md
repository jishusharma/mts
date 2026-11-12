# Brief: gap-driven Tom/Fabio extraction (cards tf-x*, tf-g*, tf-r*)

Why: 12 coded versions failed; reviews say we coded our numbers, not their method. These cards do NOT summarise videos. They answer fixed questions (PLAN.md section 1, ids Q1..Q14) from the trader's own words, or say NOT_SEEN.

## Extractor rules (Sonnet on held transcripts; Gemini `gemini_queue.py run <card>:low` after caption unlock)
1. Read `MyTradingSys/research/tf_extraction_plan_1113/PLAN.md` section 1 for your card's questions, and `ANSWERS_FROM_DISK.md` for what is already settled (do not redo; add only new evidence or a contradiction).
2. Source = the full `raw_transcripts_canonical/<id>_raw.txt` of each id on the card. Read it whole (Tom files are one long line; Fabio files have [m:ss]). Never "watch the video", never quote from memory or from an old extract. Gemini: only use the real caption file; if absent write NOT_IN_DATA.md naming the blocker.
3. Output the file named in your card's done_when: Sonnet/Haiku cards `MyTradingSys/research/tf_extraction_plan_1113/out/<card-id>/`, Gemini (CODEX) cards `MyTradingSys/research/layer_lab/tf_extract_1113/<card-id>/` (a CODEX run may only write under layer_lab). Per question one block:
   - `### Q<n> <question>`
   - `**Verdict: ANSWER | PARTIAL | NOT_SEEN | CONTRADICTION**` then 1-3 plain sentences. A number the trader states = SOURCED (say which words). A number he does not state = NOT_SEEN (never fill it in).
   - each supporting quote as `> "verbatim words"` then `**Source GPS: <id> | BEGIN|MIDDLE|END**` (thirds of the transcript body) then `[m:ss]` for Fabio files.
   - Different speakers on one channel (Serge Hoffmann, Patrick Nill) and contested ids (9IliXww64uM) are labelled GUEST / CONTESTED, never merged into Tom/Fabio.
4. End with a table `parameter | trader's value | SOURCED or NOT_SEEN | id`. No OURS numbers in it.
5. Gate: `python scripts/dev/verify_extract_quotes.py <ANSWERS.md>` exit 0 with at least 1 quote. Fix the quote, never the checker. Drop what you cannot verify.
6. Commit on your own branch; a Claude session reviews and ships.
Never: proxy, VPN, cookies, edits to fetch_captions*.py or verify_extract_quotes.py, `.secrets`, `.env`, live tree, Chrome.

## Reviewer rules (Haiku, a different model from the extractor)
1. Run the gate on every ANSWERS.md of the wave; exit 0 and at least 1 quote or the card fails.
2. For each Verdict ANSWER or PARTIAL, open the transcript and check that the quote really supports the sentence (not just that the words exist). Check 5 blocks per file, or all if fewer.
3. For each NOT_SEEN: grep the card's transcripts for two keywords from the question; if a hit contradicts NOT_SEEN, list it.
4. Write `<out dir>/REVIEW.md`: table `block | quote supports claim Y/N | note`; and verdict PASS/FIX with the exact lines to fix. Do not edit the extractor's file.
