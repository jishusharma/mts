# Report: gemini-concept-extract-tom-M7ompiwv5co-1112

- **Date:** 2026-11-12 (SOURCED: system date)
- **Task:** `gemini-concept-extract-tom-M7ompiwv5co-1112` (OURS)
- **Video ID:** `M7ompiwv5co` (The Easiest Way to Start Trading (Swing Trading for Beginners)) (SOURCED: card definition)
- **Status:** PASS (0 problem(s), 15/15 quotes verified against canonical auto-caption transcript `raw_transcripts_canonical/M7ompiwv5co_raw.txt`) (SOURCED: `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/tom_fabio_rebuild_2026-11-09/tom_M7ompiwv5co/EXTRACT.md`)

## Verification Summary
1. Pre-change failure test:
   - Command: `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/tom_fabio_rebuild_2026-11-09/tom_M7ompiwv5co/EXTRACT.md` (with intentionally altered quote)
   - Result: `MISSING  EXTRACT.md:6 'This is an intentionally altered fake quote to ensure failur' ; FAIL: 1 problem(s)` (exit code 1)
2. Final extract validation:
   - Command: `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/tom_fabio_rebuild_2026-11-09/tom_M7ompiwv5co/EXTRACT.md`
   - Output:
     ```
     OK       EXTRACT.md:38
     OK       EXTRACT.md:41
     OK       EXTRACT.md:44
     OK       EXTRACT.md:47
     OK       EXTRACT.md:50
     OK       EXTRACT.md:53
     OK       EXTRACT.md:56
     OK       EXTRACT.md:59
     OK       EXTRACT.md:62
     OK       EXTRACT.md:65
     OK       EXTRACT.md:68
     OK       EXTRACT.md:71
     OK       EXTRACT.md:74
     OK       EXTRACT.md:77
     OK       EXTRACT.md:80
     PASS: 0 problem(s)
     ```
   - Exit code: 0

## Deliverable File
- Extract: [EXTRACT.md](file:///F:/MTS/gq/gemini-concept-extract-tom-M7ompiwv5co-1112/MyTradingSys/research/tom_fabio_rebuild_2026-11-09/tom_M7ompiwv5co/EXTRACT.md#L1-L81) (OURS)
