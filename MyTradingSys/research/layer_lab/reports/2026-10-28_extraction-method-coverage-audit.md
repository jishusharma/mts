# Layer Lab Report: extraction-method-coverage-audit

**Card**: `extraction-method-coverage-audit`  
**Kind**: audit  
**Date**: 2026-10-28  
**Operator Goal**: Group videos by type (English talk, Hinglish/Hindi, chart-walk, live stream) and by method; count thin, garbled, and never-read videos; produce the re-extraction list with the cheapest viable method per video.  

---

## 1. Summary of Deliverables

1. **`MyTradingSys/research/extraction_ledger_2026-10/COVERAGE_AUDIT.md`**:
   - Comprehensive audit of all 303 extraction ledger rows across 230 unique YouTube videos.
   - Coverage matrix: Video Type × Extraction Method breaking down Sound, Thin, Garbled/FAIL Quotes, and Never-Read categories.
   - Spot-reading evidence with file:line citations across major groups.
   - Cost analysis and recommended re-extraction protocols.

2. **`MyTradingSys/research/extraction_ledger_2026-10/REEXTRACT_LIST.csv`**:
   - 183 unique videos prioritized for extraction or re-extraction.
   - Schema: `video_id,why,method,est_cost`.
   - 100% verified: every single video ID exists in `EXTRACTION_LEDGER.csv`.

---

## 2. Coverage Matrix Summary

| Video Type | Extraction Method | Total Rows | Sound (>=3 quotes) | Thin (1-2 quotes) | Garbled / FAIL Quotes | Never-Read (No Extract) |
|---|---|---|---|---|---|---|
| English talk | `captions` | 164 | 55 | 9 | 24 | 76 |
| English talk | `gemini` | 11 | 6 | 0 | 5 | 0 |
| Hinglish/Hindi | `captions` | 22 | 19 | 2 | 0 | 1 |
| Hinglish/Hindi | `hindi_asr` | 56 | 0 | 0 | 1 | 55 |
| chart-walk | `captions` | 44 | 36 | 6 | 0 | 2 |
| chart-walk | `gemini` | 5 | 0 | 4 | 1 | 0 |
| live stream | `captions` | 1 | 0 | 0 | 1 | 0 |
| **TOTAL** | **-** | **303** | **116** | **21** | **32** | **134** |

---

## 3. Re-Extraction Strategy

- **`never-read` (134 videos)**:
  - 55 Hindi/Malkan videos routed to local `hindi_asr` / `whisper` ($0.00).
  - 76 English talk videos routed to free YouTube `captions` ($0.00) or `gemini-flash` ($0.005).
  - 2 chart-walks routed to `gemini-flash` ($0.010).
  - 1 live stream routed to `gemini-flash` ($0.015).
- **`garbled` / `fail-quotes` (31 videos)**:
  - Repaired via `gemini-flash` structured re-extraction against full canonical transcripts ($0.005).
- **`thin` (18 videos)**:
  - Upgraded via `gemini-flash` ($0.005 - $0.010) to expand rule coverage.

Total estimated campaign cost: **~$0.65 - $0.85 USD**.

---

## 4. Verification Check

- Every `video_id` in `REEXTRACT_LIST.csv` verified against `EXTRACTION_LEDGER.csv`: **183/183 PASS**.
- `tasks.py check extraction-method-coverage-audit` passes.
