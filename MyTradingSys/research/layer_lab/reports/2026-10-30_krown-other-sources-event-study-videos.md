# Krown Other Sources Event-Study Videos & Call Ledger Report

- **Task:** `krown-other-sources-event-study-videos`
- **Session:** Gemini (Antigravity, JIS-NUC)
- **Date:** 2026-10-30

## 1. Summary of Transcripts & V2 Extractions

Captions for all 4 videos were fetched and verified:
1. `OggsnATGbOg` (2026-09-25): *Bitcoin's Dip Has a Landing Zone: $80,214. Then the Bounce* (CBP item; 4,587 words).
2. `V0gjxlaW2Qk` (2026-10-06): *Bitcoin's Overbought Signal: 12 of 13 Times, +26% Within 4 Weeks* (3,206 words).
3. `sCLLZKY_r8g` (2026-10-07): *Bitcoin's Weekly Just Went Overbought. 12 of 13 Times, +26%* (137 words).
4. `ZNvLh3JyOco` (2026-10-08): *Bitcoin's Overbought Weekly, Modern Cases Only: +17.7%* (111 words).

Each transcript was extracted into `MyTradingSys/research/krown_ta101_2026-10-13/extracts/` using the V2 extraction method (Header, Decision Log, Trade Blocks, Verbatim Quotes with Source GPS).

## 2. Quote Gate Verification

Ran `python scripts/dev/verify_extract_quotes.py` on all 4 extracts:
- `extract_OggsnATGbOg.md`: 3/3 quotes PASS (0 problems)
- `extract_V0gjxlaW2Qk.md`: 3/3 quotes PASS (0 problems)
- `extract_sCLLZKY_r8g.md`: 2/2 quotes PASS (0 problems)
- `extract_ZNvLh3JyOco.md`: 2/2 quotes PASS (0 problems)
- **Total:** 10/10 verbatim quotes match canonical raw transcripts and position tags.

## 3. Call Ledger (`CALL_LEDGER.csv`)

Built `MyTradingSys/research/krown_ta101_2026-10-13/CALL_LEDGER.csv` satisfying PRE_REG_KROWN Item 2:
- 7 prospectively timestamped calls across the 4 videos.
- Includes `date_utc`, `video_id`, `instrument`, `side`, `trigger`, `target`, `hit_rate_stated`, `split` (design / check split by date <= 2026-10-06 vs > 2026-10-06), and `outcome_stated`.

## 4. Verdict

**SOUND / COMPLETE**
