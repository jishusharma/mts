# Task Report: gemini-yt-cowen-extract

- **Task ID:** `gemini-yt-cowen-extract`
- **Lane / Weight:** CODEX / ROUTINE
- **Date:** 2026-10-31 UTC
- **Worker / Model:** JIS-NUC / Gemini Flash
- **Registry:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`

## 1. Scope & Objective

Ingest the latest 8 videos from Benjamin Cowen (@benjaminjcowen) on YouTube, capture timed captions, and extract his stated Bitcoin price levels, Bull Market Support Band (20-week SMA / 21-week EMA) ranges, cycle positioning calls, and quantitative risk metrics.

## 2. Ingestion & Captions Summary

Executed timed caption download:
```powershell
python scripts/dev/fetch_captions_timed.py --analyst Cowen --channel "@benjaminjcowen" --latest 8 --out MyTradingSys/research/yt_feed_2026-10-31/transcripts_cowen
```
All 8 latest videos were read and captioned (with fallback to canonical transcript storage in `raw_transcripts_canonical/` where HTTP 429 rate limit errors occurred):
1. `bekghgecip8` ("Bitcoin: The Q4 Dump is Here") - 2026-10-30 - 4539 words - Captioned
2. `21mBnslOLd0` ("Bitcoin: Post-FOMC") - 2026-10-29 - 3632 words - Captioned
3. `4oHSuPTr8H0` ("Gold: Dubious Speculation") - 2026-10-27 - 2955 words - Captioned
4. `bWdXPK3Hlok` ("Bitcoin: Bears Regaining Control") - 2026-10-25 - 5524 words - Captioned
5. `eN6dpreDIk4` ("Bitcoin: A Precarious Position") - 2026-10-24 - 3536 words - Captioned
6. `KZ1Jro92t48` ("Bitcoin Bull Market Support Band") - 2026-10-22 - 1902 words - Captioned
7. `oYPawyUxnnE` ("Bitcoin Hovers Above $83k") - 2026-10-21 - 985 words - Captioned
8. `WAMu9tSOyyY` ("What will the Federal Reserve Do Next?") - 2026-10-19 - 2034 words - Captioned

Total videos read: 8. Captioned: 8. UNVERIFIED: 0.

## 3. Extracted Deliverable & Key Findings

Deliverable file created:
- [`COWEN_LEVELS_2026-10-31.md`](file:///F:/MTS/gq/gemini-yt-cowen-extract/MyTradingSys/research/yt_feed_2026-10-31/COWEN_LEVELS_2026-10-31.md)

### Key Metrics & Levels Sourced:
1. **Line in the Sand ($83k):**
   - Cowen explicitly defines $83,000 as the line in the sand separating the bull regime from a confirmed fakeout (`oYPawyUxnnE` at `[00:00:26]`: *"One of the sort of the line in the sand that we talked about is 83K as the line that the the bulls need to defend"*).
   - Once a second weekly close below 83k occurs, the upside fakeout is confirmed (`21mBnslOLd0` at `[00:05:20]`: *"first one was you get your second weekly close by Bitcoin below 83K, which happened. So, therefore, fake out confirmed"*).
2. **Bull Market Support Band (20-week SMA & 21-week EMA):**
   - The Bitcoin Bull Market Support Band currently spans $72,000 to $76,000 (`bWdXPK3Hlok` at `[00:06:02]`: *"the bull market support band for Bitcoin currently ranges from around 76k to about 72. So, 72 to 76k"*).
   - A daily close below the 50-day moving average (around 81.7k) is the primary early warning sign that the 21-week EMA is in play (`KZ1Jro92t48` at `[00:08:22]`: *"A close below the 50-day would be your first sign that the 21-week EMA is in is in play"*).
3. **Cycle Positioning & Midterms:**
   - Cowen repeatedly notes that Bitcoin's prior major cycle bottoms have consistently occurred after US midterms (`21mBnslOLd0` at `[00:16:45]`: *"all of Bitcoin's prior major drops that marked market cycle bottoms have always occurred after the midterms"*).
   - Expected path: potential bounce off the bull market support band into midterms, followed by the final cycle low post-midterms (`bekghgecip8` at `[00:14:16]`: *"and then after the midterms you get the final drop, right? And and then that ends up being sort of the four-year cycle low"*).
4. **Specific ITC Risk Metric Bands:**
   - Mentions macro risk ratio 0.8 in conjunction with oil targets (`bWdXPK3Hlok` at `[00:23:16]`), but numerical ITC logarithmic regression risk levels (0.0 to 1.0) were not stated on screen across this 8-video batch; categorized strictly as `NOT_IN_DATA`.
   - `WAMu9tSOyyY` focuses on Federal Reserve interest rate policy, with crypto price levels categorized as `NOT_IN_DATA`.

## 4. Verification Gate

Ran verification command:
```powershell
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/yt_feed_2026-10-31/COWEN_LEVELS_2026-10-31.md
```
Result: `PASS: 0 problem(s)` (Exit code 0).
Every verbatim quote matches canonical transcript text and exact positional thirds (`BEGIN`, `MIDDLE`, `END`).

Noticed: Benjamin Cowen consistently operates with conditional structural levels (specifically the 50-day moving average and 20-week/21-week Bull Market Support Band) rather than static price targets, with the $83k level functioning as his binary macro regime threshold.
