# Report: Analyst Call Back-Catalogue Extract (2026-11-12)

- **Card ID:** `analyst-call-backcatalogue-extract-1112`
- **Lane:** CODEX / Gemini (`gemini-3.8-flash-low`)
- **Date:** 2026-11-12 UTC
- **Worktree:** `F:\MTS\gq\analyst-call-backcatalogue-extract-1112` (`gemini-q/analyst-call-backcatalogue-extract-1112`)

## 1. Objective & Scope

Per card goal:
> "Extract the back-catalogue of analyst calls (level, direction, date; losers included) from captions into research/analyst_call_slot_2026-11-11/calls.jsonl format, on the Gemini lane"

Card steps:
1. "Pick the analysts and videos from MyTradingSys/research/analyst_call_slot_2026-11-11/ (read its README first); captions only, never invented"
2. "Write EXTRACT.md rows (video id, date, level, direction, verbatim quote); no outcomes read before extraction"
3. "Run verify_extract_quotes.py until exit 0; unverifiable quotes dropped; commit on your branch"

## 2. Investigation & Findings

1. **Analyst Selection & README Inspection:**
   - In [PREREG.md](file:///F:/MTS/gq/analyst-call-backcatalogue-extract-1112/MyTradingSys/research/analyst_call_slot_2026-11-11/PREREG.md#L1-L24), the analyst-call slot defines the call schema (level/zone, side, t_logged, expires) and was seeded with the Habib 72.5k long (`HABIB-2026-11-10-L72.5`) from CBP store `rows.json`.
   - The card notes that the back-catalogue of analyst calls with a level, a direction, and a date (losers included) comes from Habib's YouTube channel (`@qriptal`).

2. **Transcript Verification Barrier:**
   - [verify_extract_quotes.py](file:///F:/MTS/gq/analyst-call-backcatalogue-extract-1112/scripts/dev/verify_extract_quotes.py#L43-L59) strictly requires transcripts to be in `raw_transcripts_canonical/<VIDEO_ID>_raw.txt`.
   - The 15 canonical raw Habib transcripts (`c9qf7QJroAE`, `14PZEEbHSaM`, `YuTkhoJ3n-0`, `2XOJcddS61E`, `5dTABLiktmg`, `yHFg7oVN3ts`, `PrHoIQ-YWX0`, `te5DetlT3XU`, `0tiz6_pSBuw`, `fBg2-RXPOAk`, `a4Um_W3Nfss`, `Jt5QElvvzPw`, `brg09NkHi6A`, `cuhsL6RENvw`, `vU7_4Gq9c5Y`) and the recent 8 videos (`K1UJr76yy94`, `hymqmEfCGrw`, etc.) were previously extracted on `JIS-NB` / other machines and do **not** exist in `raw_transcripts_canonical/` on this host ([STATUS.md:11](file:///F:/MTS/gq/analyst-call-backcatalogue-extract-1112/MyTradingSys/research/analyst_video_status_1112/STATUS.md#L11)).
   - Attempting to verify any quote for these videos via `python scripts/dev/verify_extract_quotes.py` returns `NO-TRANSCRIPT <VID>` (fail code 1).
   - Staged raw files in `extracts/_staged_2026-09-27/raw/qriptal_*_raw.txt` are not checked by `verify_extract_quotes.py` (which only looks at `raw_transcripts_canonical/` and cbp `inbox/`).

3. **YouTube Caption Lockout:**
   - Running `python scripts/dev/fetch_captions_timed.py --status` reports:
     `BLOCKED until 2026-11-13T13:58:11+00:00 (host JIS-NUC, ip 49.37.73.158); lockout level 3 of 3 (6/24/72 h, OURS)`.
   - Under global and workspace strict policies, we cannot bypass or evade the caption lockout or fetch captions from YouTube.

4. **Zero Fabrication Policy:**
   - Under strict rule "NO ASSUMPTIONS, NO FABRICATIONS", unverified quotes cannot be fabricated or marked as verified.
   - Step 3 explicitly mandates: `Run verify_extract_quotes.py until exit 0; unverifiable quotes dropped`. Because no canonical transcript exists on this host to verify back-catalogue quotes for Habib/Qriptal, no rows can pass `verify_extract_quotes.py`.

## 3. Blocker Statement

The task cannot be completed until the canonical transcripts for the analyst videos (`raw_transcripts_canonical/<VIDEO_ID>_raw.txt`) are synced to this host from `JIS-NB` or the YouTube caption fetcher lockout expires after `2026-11-13T13:58:11Z`.
