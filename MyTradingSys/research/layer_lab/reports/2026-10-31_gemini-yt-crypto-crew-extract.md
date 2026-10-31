# Task Report: gemini-yt-crypto-crew-extract

- Task ID: `gemini-yt-crypto-crew-extract`
- Lane / Weight: CODEX / ROUTINE
- Date: 2026-10-31
- Operator / Model: JIS-NUC / Gemini Flash

## 1. Scope & Objective

Extract stated BTC and alt entry rules, levels, price action structures, and technical indicators read with timed verbatim quotes from the latest 8 videos of Crypto Crew University (@CryptoCrewUniversity).
Output destination: `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md`.

## 2. Caption Fetching & Video Processing Summary

Command executed:
```bash
python scripts/dev/fetch_captions_timed.py --analyst CCU --channel "@CryptoCrewUniversity" --latest 8 --out MyTradingSys/research/yt_feed_2026-10-31/transcripts_crypto-crew
```

The 8 latest videos processed from @CryptoCrewUniversity:
1. `-Tu4DJsnOQs`: "BREAKING: BITCOIN GOLDEN CROSS QUICKLY APPROACHES" (2026-10-07) - Captioned [SOURCED: `MyTradingSys/research/yt_feed_2026-10-31/transcripts_crypto-crew/-Tu4DJsnOQs_timed.txt:1-5`]
2. `4WpAJxcyUzk`: "BREAKING: LARGEST BULL FLAG BREAKOUT IN HISTORY" (2026-10-19) - Captioned [SOURCED: `MyTradingSys/research/yt_feed_2026-10-31/transcripts_crypto-crew/4WpAJxcyUzk_timed.txt:1-5`]
3. `FlDFTA4s7XE`: "WARNING: WATCH THIS B4 NOVEMBER" (2026-10-21) - Captioned [SOURCED: `MyTradingSys/research/yt_feed_2026-10-31/transcripts_crypto-crew/FlDFTA4s7XE_timed.txt:1-5`]
4. `OGAIlXwmV1Q`: "BREAKING: WAVE TREND WARNING SIGNS" (2026-10-15) - Captioned [SOURCED: `MyTradingSys/research/yt_feed_2026-10-31/transcripts_crypto-crew/OGAIlXwmV1Q_timed.txt:1-5`]
5. `kZ5q1K3KzqI`: "WARNING: THEY’RE LYING TO YOU — HERE’S THE TRUTH" (2026-10-13) - Captioned [SOURCED: `MyTradingSys/research/yt_feed_2026-10-31/transcripts_crypto-crew/kZ5q1K3KzqI_timed.txt:1-5`]
6. `iwMbayybIVg`: "WARNING: HISTORY IS REPEATING" (2026-10-01) - Captioned [SOURCED: `MyTradingSys/research/yt_feed_2026-10-31/transcripts_crypto-crew/iwMbayybIVg_timed.txt:1-5`]
7. `RxyY3WAntg4`: "SOMETHING DOESN’T SMELL RIGHT" (2026-09-25) - Captioned [SOURCED: `MyTradingSys/research/yt_feed_2026-10-31/transcripts_crypto-crew/RxyY3WAntg4_timed.txt:1-5`]
8. `tp78FKX8pMc`: "HALVING LIES? — WILL MATH BE PROVEN WRONG" (2026-10-28) - Captioned [SOURCED: `MyTradingSys/research/yt_feed_2026-10-31/transcripts_crypto-crew/tp78FKX8pMc_timed.txt:1-5`]

Counts:
- Videos read: 8 [OURS]
- Captioned: 8 [OURS]
- UNVERIFIED: 0 [OURS]

## 3. Findings & Rules Extracted

Primary deliverable: `MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md`.
Extracted items: 32 total entries in the summary table.
- Verbatim quoted items verified against canonical transcripts: 24 [OURS]
- Explicit `NOT_IN_DATA` items (specifically altcoin standalone entry indicator rules, which Steve / CCU explicitly notes co-move with BTC / market liquidity rather than presenting standalone indicator rules): 8 [OURS]

Key Technical Indicators & Rules Analyzed:
- 2-Day 50 MA / 200 MA Golden Cross and Death Cross [SOURCED: `CCU_RULES_2026-10-31.md:51-63`]
- 2-Day 200 MA Reclaim and Support Holding [SOURCED: `CCU_RULES_2026-10-31.md:63`]
- Bull Flag Geometric Rules (parallel boundary lines, retracement depth <= 50% pole length) [SOURCED: `CCU_RULES_2026-10-31.md:71`]
- RSI Extreme Overbought Boundary (White line at 83.87) and 27-Year Cycle Periodicity [SOURCED: `CCU_RULES_2026-10-31.md:75-79`]
- 2-Month Stochastic RSI Momentum (>80 bull market top zone; cross downs marking cycle peaks; <20 cycle bottom zone) [SOURCED: `CCU_RULES_2026-10-31.md:87-95`]
- 12-Day Wave Trend Indicator (Green zone extreme oversold buy signal; Red zone cycle top exit signal) [SOURCED: `CCU_RULES_2026-10-31.md:103-111`]
- 2-Day 21 SMA Breakout & Retest Entry Rule (former resistance flipped to support) [SOURCED: `CCU_RULES_2026-10-31.md:131-135`]
- 3-Rule Sequential Bull Market Confirmation (Higher High, Higher Low on Stoch RSI cross down holding >$57k, second Higher High on Stoch RSI cross up) [SOURCED: `CCU_RULES_2026-10-31.md:139-147`]
- Monthly Stochastic RSI Bear Market Pocket (<16 white line) and ~65 Swing High Resistance Level [SOURCED: `CCU_RULES_2026-10-31.md:155-159`]
- Halving Phase 2 Cycle Framework and Phase 1 Consolidation [SOURCED: `CCU_RULES_2026-10-31.md:167-171`]

## 4. Verification Gate

Verification test:
```bash
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md
```
Output:
```
PASS: 0 problem(s)
```
Exit code: 0 [SOURCED: `verify_extract_quotes.py exit 0`].
All 24 verbatim quotes match raw canonical transcript text and positional third GPS tags (`BEGIN`, `MIDDLE`, `END`).
