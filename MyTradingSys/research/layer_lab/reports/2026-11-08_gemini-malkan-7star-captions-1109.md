# Report: Malkan 7-Star Captions and Star Conditions (2026-11-08)

**Task:** `gemini-malkan-7star-captions-1109`  
**Command / Test:** `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/malkan_level_shorts_2026-11-09/SEVEN_STAR_CAPTIONS.md` (exits 0, PASS: 0 problem(s))

## 1. Executive Summary

- Primary source captions for Malkan 7-star setups and the 3X3 Swing Trading series post-Episode 8 were audited to answer the operator's question: *What are the missing 7-star conditions in reverse divergence?*
- Captions for `XFO49JlODxI` ("Spinning Top 7 Star Setup", 1608 words) were fetched and canonicalized to `raw_transcripts_canonical/XFO49JlODxI_raw.txt`.
- Video `bH0mXqSXV3Y` ("Banknifty 7 Star Signal") was confirmed **PRIVATE** on YouTube (`ERROR: [youtube] bH0mXqSXV3Y: Private video`).
- Episodes post-Episode 8 in the 3X3 series:
  - Episode 11 (`fgN6QBFY3Ss`, "Bollinger Bands Ka Father-Son Strategy", 5133 words) exists in repo (`raw_transcripts_canonical/fgN6QBFY3Ss_raw.txt`), inspected line-by-line; contains zero mentions of star grades.
  - Episodes 9 (`WBByyLBp8-c`), 10 (`TYB7GJODt-k`), and 12 (`p32qB7PjkVI`) are rate-limited with HTTP 429 (`fetch_captions.py` blocked).
- Discovered an additional primary source transcript in repo: `GbXnw_tNMtw` ("Reverse Divergence - Positive & Negative Divergence!", 4836 words) which directly addresses the 3-star, 5-star, and 7-star reverse divergence grading conditions.

## 2. Star Grade Findings & Verbatim Evidence

### Reverse Divergence (PRD / NRD) Star Grades
1. **3-Star Grade:**
   - **Conditions:** Basic reverse divergence present, but loose / minimal confluence; bar count marginal (e.g. >15-20 bars) or level criteria unconvincing (`GbXnw_tNMtw_raw.txt:357-366`).
   - **Performance:** Strike rate ~50% ("five of them will work five of them will not work" `XFO49JlODxI_raw.txt:8`; "it is loose, it will run on it, I do n't know" `A-CQiV_UFB4_raw.txt:296`). Risk/reward 1:3 (`XFO49JlODxI_raw.txt:8`).
2. **5-Star Grade:**
   - **Conditions:** Bar count between 5 and 50 bars (`GbXnw_tNMtw_raw.txt:460-461`); both swing lows above 60 for bullish PRD or both swing highs below 40 for bearish NRD (`GbXnw_tNMtw_raw.txt:461-465`).
   - **Performance:** Strike rate 60-70% ("seven of them will work three of them will not work" `XFO49JlODxI_raw.txt:8`; "chances of running will be 60-70" `A-CQiV_UFB4_raw.txt:295`). Risk/reward 1:5 to 1:7 (`XFO49JlODxI_raw.txt:8`).
3. **7-Star Grade:**
   - **Conditions (Multi-Timeframe RSI Divergence):** Monthly RSI above 60 + Daily RSI below 40 + Daily divergence visible (`Wvq1TZh8aF0_raw.txt:393-403`). Target doubled, stop unchanged.
   - **Conditions (Reverse Divergence Confluence):** Bar count between 5 and 50 bars + points above 60 / below 40 (`GbXnw_tNMtw_raw.txt:460-465`) + all additional proprietary conditions matched. In both `A-CQiV_UFB4` (lines 292-301) and `GbXnw_tNMtw` (lines 387-394, 458-459), Malkan explicitly withholds the advanced confluence parameters from public videos, citing they are reserved for the paid "Star Trader / 10X" programs.
   - **Performance:** Strike rate 80-90% ("nine of them will work one of them will not work" `XFO49JlODxI_raw.txt:8`; "chances of running become very high almost 80-90" `A-CQiV_UFB4_raw.txt:293`). Risk/reward 1:10, 1:20, 1:30 (`XFO49JlODxI_raw.txt:8`).

### Candlestick 7-Star Setup (`XFO49JlODxI`)
- **Structure:** Spinning top at a major top or bottom: small body (color red/green immaterial) + long upper and lower shadows + high volume (exhaustion/expansion volume) (`XFO49JlODxI_raw.txt:8`).
- **Entry & Risk:** Buy above high (stop below low) for long; sell below low (stop above high) for short. Target much higher than risk (1:10 to 1:30) (`XFO49JlODxI_raw.txt:8`).
- **Purity:** Standalone trade; when seen, "i will not look at any other thing no rsi no bollinger band no candles no other adx nothing just this and enter" (`XFO49JlODxI_raw.txt:8`).

## 3. Artifact Deliverable

- File: `MyTradingSys/research/malkan_level_shorts_2026-11-09/SEVEN_STAR_CAPTIONS.md`
- Gate test: `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/malkan_level_shorts_2026-11-09/SEVEN_STAR_CAPTIONS.md` -> **PASS: 0 problem(s)**.
