# Task Report: gemini-malkan-top12-rsi-rules-extract

- Task ID: `gemini-malkan-top12-rsi-rules-extract`
- Lane / Weight: CODEX / ROUTINE
- Date: 2026-10-31
- Operator / Model: JIS-NUC / Gemini Flash

## 1. Scope & Objective

Extract Malkan RSI 40-60 rules, timeframes, momentum reads, entries, and invalidations with timed verbatim quotes from the 12 top-ranked videos on channel `@malkansview` (identified via `MyTradingSys/research/malkan_extract_2026-10-15/CHANNEL_LIST.md`).

## 2. Video Priority List & Processing Summary

From `MyTradingSys/research/malkan_extract_2026-10-15/CHANNEL_LIST.md:14-44`, the top 12 ranked videos were targeted:
1. `v8pCR_bA0_0` (RSI - 5 Star Set Up #1) - English (Fetched, rules extracted)
2. `kVIvcn7T44o` (RSI Powerful Strategy) - Hindi audio / auto-captions (Fetched, NOT_IN_DATA per non-English transcript policy)
3. `-2uZSqKKrFQ` (RSI 40-60 Strategy Explained, Grandfather-Father-Son Trading System) - Hindi audio / auto-captions (Fetched, NOT_IN_DATA per non-English transcript policy)
4. `2HcJ3NeZmEQ` (RSI 5 Star Set Up #1 Sell Setup) - English (Fetched, rules extracted)
5. `5Aoyw_sG_88` (RSI - Set up 1 - Targets) - English (Fetched, rules extracted)
6. `kL7_ybtI_Fc` (RSI - 5 -) - Transcripts disabled on YouTube; replaced by next priority bench video `hGPqIpWRUMQ` (Pullback Trading Using Unconventional RSI Part 1) - English (Fetched, rules extracted)
7. `cQ-y1oULkBw` (Divergence Trading Strategy) - English translation transcript (Fetched, rules extracted)
8. `GbXnw_tNMtw` (Reverse Divergence - Positive & Negative Divergence!) - English (Fetched, rules extracted)
9. `TrZQ4Xat_sQ` (RSI Divergence Trade) - Hindi audio / auto-captions (Fetched, NOT_IN_DATA per non-English transcript policy)
10. `TO3pLafk7Us` (RSI Divergence Class A/B/C) - Hindi audio / auto-captions (Fetched, NOT_IN_DATA per non-English transcript policy)
11. `sPu2SnAFEIY` (5. RSI Ki Ye Strategy Koi Nahi Batayega) - Hindi audio / auto-captions (Fetched, NOT_IN_DATA per non-English transcript policy)
12. `fgN6QBFY3Ss` (11. Bollinger Bands Ka Father-Son Strategy) - Hindi audio / auto-captions (Fetched, NOT_IN_DATA per non-English transcript policy)

Total videos read: 12.
All 12 timed transcripts saved under `MyTradingSys/research/malkan_rsi_2026-10-31/transcripts/`.

## 3. Findings & Rules Extracted

Primary deliverable: `MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md`.
Contains:
- Table mapping 27 rules / rows across all 12 videos.
- 21 verbatim extracted rules with GPS thirds tags across the 6 English transcripts.
- 6 rows explicitly marked `NOT_IN_DATA` for the Hindi-only transcripts where verbatim English quotes cannot be fabricated.
- First line: `Videos read: 12 (6 English transcripts with extracted rules, 6 Hindi transcripts with NOT_IN_DATA per non-English transcript policy).`

## 4. Verification Gate

Executed:
```bash
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md
```
Result: `PASS: 0 problem(s)` (Exit code 0).
Every verbatim quote matches canonical transcript text and exact positional third (`BEGIN`, `MIDDLE`, `END`).
