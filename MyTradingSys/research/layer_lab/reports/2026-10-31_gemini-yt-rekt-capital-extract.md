# Rekt Capital (@RektCapital) Latest 8 Videos Cycle & Range Levels Extraction

- **Task ID:** `gemini-yt-rekt-capital-extract`
- **Session:** Gemini (Antigravity, JIS-NUC)
- **Date:** 2026-10-31
- **File:** `MyTradingSys/research/yt_feed_2026-10-31/REKT_LEVELS_2026-10-31.md`

## 1. Caption Fetching & Data Summary
Captions fetched via `python scripts/dev/fetch_captions_timed.py --analyst Rekt --channel "@RektCapital" --latest 8 --out MyTradingSys/research/yt_feed_2026-10-31/transcripts_rekt-capital`:
- Videos read: 8
- Captioned: 8
- UNVERIFIED: 0
- NOT_IN_DATA count: 0

The 8 extracted videos are:
1. `MRBXsqgIGb8` (3,155 words): *Is Bitcoin Still In The Accumulation Phase?*
2. `ZAGbis1hfXw` (2,204 words): *3 Things That Will Change How You See the Bitcoin Bear Market*
3. `XMbLOHZRSFo` (1,463 words): *The Bitcoin Summer Game Plan - A Crucial Update*
4. `BFMztI2UDQ4` (1,620 words): *Bitcoin and Red August - My Perspective*
5. `P0v26DCPiZ4` (1,666 words): *Is Bitcoin On The Cusp Of A New Breakdown Phase?*
6. `s22yyxspRT0` (1,433 words): *The Bitcoin Bargain Framework*
7. `y1VZlQtjUwY` (1,261 words): *Where Is Bitcoin In the Cycle? EMA Crossover Analysis*
8. `C1kVrs-u0WM` (2,221 words): *Is The Bitcoin Summer Rally Ending?*

## 2. Verification Gate
Ran `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/yt_feed_2026-10-31/REKT_LEVELS_2026-10-31.md`:
- Total quotes verified: 16 (2 per video across all 8 videos)
- Verification result: PASS (0 problems, exit code 0)

Noticed: Rekt Capital consistently frames bear market rally peaks as retests of the 50-month EMA where former support is confirmed as new resistance, while highlighting the $60,000 region and $82,500 boundary as pivotal re-accumulation thresholds.
