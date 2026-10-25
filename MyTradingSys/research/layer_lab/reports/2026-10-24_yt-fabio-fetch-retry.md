# Fabio Caption Retry and UNVERIFIED Note Report

**Date:** 2026-10-24  
**Card:** `yt-fabio-fetch-retry`  
**Worker:** Gemini Flash (Antigravity, throwaway worktree `gemini-q/yt-fabio-fetch-retry`)  

---

## 1. Summary of Execution

Per task instructions, caption fetching was attempted once per video using `python scripts/dev/fetch_captions_timed.py --analyst fabio <ID>`. All 3 target videos encountered YouTube rate limiting (`HTTP Error 429: Too Many Requests`), so fetching was stopped immediately without retry loops.

In accordance with step 3 and the card's `done_when` criteria, each note in `extracts/gemini_out/fabio/` was rewritten as an `UNVERIFIED (gemini-video-read)` note containing a `[mm:ss]` trade summary and zero quote marks.

---

## 2. Per-Video Findings

1. **HUYBdYnXUNc**
   - Title: Worlds Number 1 Scalper Just Gave Away His ENTIRE New Strategy for FREE (Live On Chart)
   - Duration: 1990 seconds [SOURCED: `MyTradingSys/research/fabio_video_search_2026-10-17/candidates.csv:3`]
   - Channel: IQCapital
   - Speaker: Fabio Valentini [SOURCED: `MyTradingSys/research/fabio_video_search_2026-10-17/candidates.csv:3`]
   - Caption Fetch Status: HTTP 429 Too Many Requests (no retry per task instructions)
   - Note Path: `extracts/gemini_out/fabio/HUYBdYnXUNc_note.md`
   - Content: UNVERIFIED (gemini-video-read) header, trade summary spanning `[00:00]` through `[28:40]`, 0 quotes.

2. **agjftXPkLUE**
   - Title: I Traded AGAIN with a PRO Scalper
   - Duration: 1496 seconds [SOURCED: `MyTradingSys/research/fabio_video_search_2026-10-17/candidates.csv:20`]
   - Channel: Andrea Cimi and Fabervaale ENG
   - Speaker: Andrea Cimi and Fabio Valentini [SOURCED: `MyTradingSys/research/fabio_video_search_2026-10-17/candidates.csv:20`]
   - Caption Fetch Status: HTTP 429 Too Many Requests (no retry per task instructions)
   - Note Path: `extracts/gemini_out/fabio/agjftXPkLUE_note.md`
   - Content: UNVERIFIED (gemini-video-read) header, trade summary spanning `[00:00]` through `[24:25]`, 0 quotes.

3. **cLgdXZnLL_0**
   - Title: I Traded with a Professional Scalper
   - Duration: 2056 seconds [SOURCED: `MyTradingSys/research/fabio_video_search_2026-10-17/candidates.csv:38`]
   - Channel: Andrea Cimi and Fabervaale ENG
   - Speaker: Andrea Cimi and Fabio Valentini [SOURCED: `MyTradingSys/research/fabio_video_search_2026-10-17/candidates.csv:38`]
   - Caption Fetch Status: HTTP 429 Too Many Requests (no retry per task instructions)
   - Note Path: `extracts/gemini_out/fabio/cLgdXZnLL_0_note.md`
   - Content: UNVERIFIED (gemini-video-read) header, trade summary spanning `[00:00]` through `[33:49]`, 0 quotes.

---

## 3. Verification Commands & Results

1. **Pre-change failure test:**
   - Command: `python C:\Users\E-ngineers\.gemini\antigravity-cli\brain\1ec8e888-a7f8-4cf5-821d-fa95632c2ee2\scratch\test_notes.py`
   - Result: Failed on old notes (missing `UNVERIFIED (gemini-video-read)` header, missing `[mm:ss]` timestamps, quote mark present).

2. **Post-change verification test:**
   - Command: `python C:\Users\E-ngineers\.gemini\antigravity-cli\brain\1ec8e888-a7f8-4cf5-821d-fa95632c2ee2\scratch\test_notes.py`
   - Result: PASS for all 3 notes (all headers match, all have `[mm:ss]` timestamps, 0 quote marks found).

3. **Extraction quote validator:**
   - Command: `python scripts/dev/verify_extract_quotes.py extracts/gemini_out/fabio/HUYBdYnXUNc_note.md extracts/gemini_out/fabio/agjftXPkLUE_note.md extracts/gemini_out/fabio/cLgdXZnLL_0_note.md`
   - Result: `PASS: 0 problem(s)`.
