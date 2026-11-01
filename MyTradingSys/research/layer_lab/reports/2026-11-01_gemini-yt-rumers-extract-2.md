# Task Report: gemini-yt-rumers-extract-2

- **Task ID:** `gemini-yt-rumers-extract-2` [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-extract-2.json:16`]
- **Lane / Weight:** CODEX / ROUTINE [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-extract-2.json:18,48`]
- **Date (UTC):** 2026-11-01
- **Worker / Model:** Gemini 3.8 Flash (Medium)
- **Registry / Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md` [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-extract-2.json:29`]

## 1. Scope & Objective

Extract stated trading rules with timed caption quotes for the second batch of 5 operator-picked videos from YouTube channel `@the.rumers` (Doug & Silvia). All 5 videos were successfully fetched into the canonical raw transcript store (`raw_transcripts_canonical/<vid>_raw.txt` and `_timed.txt`), enabling full verbatim caption verification with zero unverified placeholders:

Target videos [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-extract-2.json:10`]:
1. `T0H_jpQXdVI` — *"This 15-Minute Scalping Strategy Shouldn't Work... But It Makes Me $2,392/Day"* (Published: 2026-07-03, Duration: 1414s, 4399 words)
2. `pcYO-yzAtrQ` — *"If I Had to Make $500 by Tomorrow, I'd Use This Trading Strategy"* (Published: 2026-09-06, Duration: 1659s, 5417 words)
3. `hMURCHLnZVE` — *"The ONLY INDICATOR That Predicts Every Mega Move (Most Traders Use It Wrong)"* (Published: 2025-11-29, Duration: 1185s, 3382 words)
4. `xtN0U-j_4Jc` — *"The  One Line Indicator That Flat Out Delivers"* (Published: 2025-08-28, Duration: 1728s, 5506 words)
5. `l0j1irTKIUw` — *"The ONLY INDICATOR That Predicts Monster Moves (Most Traders Use It Wrong)"* (Published: 2026-02-14, Duration: 1580s, 5132 words)

## 2. Deliverables & Verification

1. **Extraction Deliverable:** `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md`
   - Total videos covered: `5` [SOURCED: `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md:8-13`]
   - Stated rules in table: `25` rows (`R01`-`R25`) [SOURCED: `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md:21-46`]
   - Verbatim caption quotes checked: `25` quotes across Section 2 [SOURCED: `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md:50-131`]
   - Testable shortlist: `4` mechanical setups (`T1` `15-Minute Pattern Scalp Reversal`, `T2` `4-Point Boundary Confluence Fade`, `T3` `Hourly RSI Liquidity Reversal`, `T4` `9 EMA 20% ATR Separation Reversion`) ready for pre-registration in downstream card `rumers-testable-rules-dev-backtest` [SOURCED: `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md:135-168`].

2. **Verification Suite:**
   - Ran `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_2.md`
   - Exit code: `0` (`PASS: 0 problem(s)`, 25/25 quotes verified against canonical transcripts with matching thirds: `BEGIN` (10), `MIDDLE` (7), `END` (8)).

## 3. Noticed

Noticed: YouTube throttles yt-dlp timedtext requests on this endpoint, but `scripts/dev/fetch_captions_timed.py`'s automatic fallback to `youtube_transcript_api` fetches the captions successfully without rate limits, ensuring 100% complete and verified quotes across all 10 operator-picked Rumers videos across both extraction batches.
