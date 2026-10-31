# Layer Lab Report: Bob Loukas (@bobloukas3493) Cycle Timing Rules Extraction

**Date (UTC)**: 2026-10-30  
**Card**: `gemini-yt-bob-loukas-extract`  
**Command Run**:
```powershell
python scripts/dev/fetch_captions_timed.py --analyst Loukas --channel "@bobloukas3493" --latest 8 --out MyTradingSys/research/yt_feed_2026-10-31/transcripts_bob-loukas
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md
```

## Summary of Results

- **Videos read**: 8 [SOURCED: `fetch_captions_timed.py` output; 8 of 8 downloaded]
- **Captioned**: 8 [SOURCED: all 8 transcripts contain captions and headers in `MyTradingSys/research/yt_feed_2026-10-31/transcripts_bob-loukas/`]
- **UNVERIFIED**: 0 [SOURCED: no videos failed captions or timed extraction]
- **Items found**: 8 [OURS: I-01, I-02, I-03, I-05, I-06, I-07, I-09, I-10]
- **NOT_IN_DATA count**: 2 [OURS: I-04 (60-day / daily cycle rules), I-08 (explicit 'right translation' term)]
- **Verbatim quotes verified**: 18 [SOURCED: `scripts/dev/verify_extract_quotes.py` exited with code 0, PASS: 0 problem(s)]

## Findings and Rules Extracted

1. **4-Year Cycle Length**:
   - 48 months (low to low) / 4 years; average 47-48 months.
   - Sourced quote: [ctJSV8aTDSk:24:58](file:///F:/MTS/gq/gemini-yt-bob-loukas-extract/MyTradingSys/research/yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md#L27)
   - Sourced quote: [DU0nwsY-8WY:02:26](file:///F:/MTS/gq/gemini-yt-bob-loukas-extract/MyTradingSys/research/yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md#L54)

2. **Weekly Cycle Length**:
   - Typically 26 weeks from low to low, or ~6-month period.
   - Sourced quote: [wzve_n4gBY4:02:48](file:///F:/MTS/gq/gemini-yt-bob-loukas-extract/MyTradingSys/research/yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md#L34)
   - Sourced quote: [DU0nwsY-8WY:08:00](file:///F:/MTS/gq/gemini-yt-bob-loukas-extract/MyTradingSys/research/yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md#L57)

3. **Weekly Cycle Advance Phase**:
   - New weekly cycle advances higher for 10 to 15 or 10 to 18 weeks into a 4-year cycle peak.
   - Sourced quote: [wzve_n4gBY4:03:13](file:///F:/MTS/gq/gemini-yt-bob-loukas-extract/MyTradingSys/research/yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md#L37)

4. **Timing Band / Window**:
   - Majority of cycle lows fall within a 10% to 15% deviation of cycle length (e.g., month 43 to month 51 on a 48-month cycle).
   - Sourced quote: [ctJSV8aTDSk:16:57](file:///F:/MTS/gq/gemini-yt-bob-loukas-extract/MyTradingSys/research/yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md#L24)
   - Sourced quote: [FYxQXT8J7ek:08:30](file:///F:/MTS/gq/gemini-yt-bob-loukas-extract/MyTradingSys/research/yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md#L47)
   - Sourced quote: [aKbB7gV67M4:00:54](file:///F:/MTS/gq/gemini-yt-bob-loukas-extract/MyTradingSys/research/yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md#L90)

5. **Cycle Translation**:
   - Left translation: Early peak in 15 to 18 months ushering in a larger bear market.
   - Sourced quote: [DU0nwsY-8WY:22:35](file:///F:/MTS/gq/gemini-yt-bob-loukas-extract/MyTradingSys/research/yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md#L60)
   - Sourced quote: [BU6j1p-bNUY:06:14](file:///F:/MTS/gq/gemini-yt-bob-loukas-extract/MyTradingSys/research/yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md#L67)
   - Right translation: NOT_IN_DATA. Standard bull market cycles are referenced as 33 to 35 months to a high or 3 years up / 1 year down, but the specific term 'right translation' was not uttered in the 8 transcripts.

6. **Daily / 60-Day Cycles**:
   - NOT_IN_DATA. Neither '60-day cycle' nor 'daily cycle' appears in any of the 8 latest transcripts examined.

7. **Timing Window vs Price Low**:
   - A cycle low comes with a timing band / window, not just a price low; price declines often go deep into the timing window before a cycle low is confirmed.
   - Sourced quote: [VWsFf5rQoqE:20:32](file:///F:/MTS/gq/gemini-yt-bob-loukas-extract/MyTradingSys/research/yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md#L83)
   - Sourced quote: [VWsFf5rQoqE:10:06](file:///F:/MTS/gq/gemini-yt-bob-loukas-extract/MyTradingSys/research/yt_feed_2026-10-31/LOUKAS_CYCLE_2026-10-31.md#L80)
