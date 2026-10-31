# Report: Krown beyond TA 101 EMA Setups

- **Task:** `gemini-krown-setups-beyond-ta101`
- **Session:** Gemini Flash (Antigravity JIS-NUC)
- **Date:** 2026-10-30 (UTC)
- **Artifact:** `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LIVE_SETUPS_2026-10-31.md`
- **Source Transcripts:** `MyTradingSys/research/krown_ta101_2026-10-13/transcripts_live_2026-10-31/`

---

## 1. Corpus Analysis & Exclusion Check

From the channel `@ECKrown`, the newest 14 videos were fetched via:
`python scripts/dev/fetch_captions_timed.py --analyst Krown --channel "@ECKrown" --latest 14 --out MyTradingSys/research/krown_ta101_2026-10-13/transcripts_live_2026-10-31`
- 12 transcripts were successfully downloaded.
- 2 videos (`ftK2BqggabQ`, `YAF6fCuVWaI`) belong to the TA 101 playlist recorded in [MANIFEST.csv](file:///F:/MTS/gq/gemini-krown-setups-beyond-ta101/MyTradingSys/research/krown_ta101_2026-10-13/MANIFEST.csv) and are excluded from this beyond-TA101 corpus.
- This leaves the latest 10 non-TA101 videos:
  1. `dLq5Jyir3Iw` (2026-10-27)
  2. `zay_owGmjo0` (2026-10-27)
  3. `M_p2k4uvRKc` (2026-10-26)
  4. `OR3Q2Vf1lrM` (2026-10-25)
  5. `8cC9Jpc8D5c` (2026-10-22)
  6. `LMRNBdMiQ2g` (2026-10-22)
  7. `bXug2l6qICc` (2026-10-20)
  8. `ro6tMlqbbBI` (2026-10-20)
  9. `P3rDSh187TE` (2026-10-17)
  10. `TDQwVve6G3Y` (2026-10-15)

## 2. Findings: EMA-based BTC Setups

Across the 10 videos, 12 EMA setup instances / rules were identified, categorized into three core setups:
1. **5/21 EMA Corrective Setup (Daily / 2-Day):**
   - **Structure:** Red 5 EMA crosses underneath yellow 21 EMA.
   - **Trigger:** Candle closure crossing 5 EMA below 21 EMA.
   - **Target / Expectation:** Minimum corrective move down to the green 55 EMA.
   - **Invalidation:** Candle closure back above yellow 21 EMA prior to reaching 55 EMA.
   - **Citations:** SOURCED [TDQwVve6G3Y](file:///F:/MTS/gq/gemini-krown-setups-beyond-ta101/raw_transcripts_canonical/TDQwVve6G3Y_raw.txt) t=00:00:30, [dLq5Jyir3Iw](file:///F:/MTS/gq/gemini-krown-setups-beyond-ta101/raw_transcripts_canonical/dLq5Jyir3Iw_raw.txt) t=00:09:09, [zay_owGmjo0](file:///F:/MTS/gq/gemini-krown-setups-beyond-ta101/raw_transcripts_canonical/zay_owGmjo0_raw.txt) t=00:04:47 & t=00:19:12.

2. **13/34 EMA Corrective Setup (Community-introduced variant):**
   - **Structure:** Cyan 13 EMA crosses underneath yellow 34 EMA.
   - **Trigger:** Cross confirmation on candle close.
   - **Target / Expectation:** Minimum corrective target down to the blue 89 EMA.
   - **Invalidation:** Candle closure back above 34 EMA.
   - **Citations:** SOURCED [dLq5Jyir3Iw](file:///F:/MTS/gq/gemini-krown-setups-beyond-ta101/raw_transcripts_canonical/dLq5Jyir3Iw_raw.txt) t=00:09:26.

3. **5-Day 21/55 EMA Silver Cross:**
   - **Structure:** Yellow 21 EMA crossing above green 55 EMA on the 5-day timeframe.
   - **Trigger:** 5-day closure confirming 21 EMA above 55 EMA (requires price closure above Caretaker reverse price, e.g. 79,200 or 83,611 depending on calculation period).
   - **Target / Expectation:** 83% of the time green one month forward with bullish momentum continuation.
   - **Invalidation:** Candle closure back below 55 EMA.
   - **Citations:** SOURCED [dLq5Jyir3Iw](file:///F:/MTS/gq/gemini-krown-setups-beyond-ta101/raw_transcripts_canonical/dLq5Jyir3Iw_raw.txt) t=00:06:21, [bXug2l6qICc](file:///F:/MTS/gq/gemini-krown-setups-beyond-ta101/raw_transcripts_canonical/bXug2l6qICc_raw.txt) t=00:00:44, [8cC9Jpc8D5c](file:///F:/MTS/gq/gemini-krown-setups-beyond-ta101/raw_transcripts_canonical/8cC9Jpc8D5c_raw.txt) t=00:02:40.

4. **10-Day 5 EMA Disconnect / Reconnect Setup:**
   - **Structure:** Disconnect where neither candle high nor low touches red 5 EMA, followed by a subsequent 10-day period testing/reconnecting with 5 EMA and holding above it.
   - **Trigger:** 10-day closure resting upon or above red 5 EMA.
   - **Target / Expectation:** 62% to 83% probability of green closure / higher high over next 10-day period (median return ~5% to ~22%).
   - **Invalidation:** 10-day candle closure below red 5 EMA.
   - **Citations:** SOURCED [TDQwVve6G3Y](file:///F:/MTS/gq/gemini-krown-setups-beyond-ta101/raw_transcripts_canonical/TDQwVve6G3Y_raw.txt) t=00:04:01, [bXug2l6qICc](file:///F:/MTS/gq/gemini-krown-setups-beyond-ta101/raw_transcripts_canonical/bXug2l6qICc_raw.txt) t=00:05:38, [ro6tMlqbbBI](file:///F:/MTS/gq/gemini-krown-setups-beyond-ta101/raw_transcripts_canonical/ro6tMlqbbBI_raw.txt) t=00:03:51, [LMRNBdMiQ2g](file:///F:/MTS/gq/gemini-krown-setups-beyond-ta101/raw_transcripts_canonical/LMRNBdMiQ2g_raw.txt) t=00:12:57.

## 3. Verification Gate

Executed:
`python scripts/dev/verify_extract_quotes.py MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LIVE_SETUPS_2026-10-31.md`
- Total quotes verified: 12
- Result: `PASS: 0 problem(s)` (Exit code 0).
