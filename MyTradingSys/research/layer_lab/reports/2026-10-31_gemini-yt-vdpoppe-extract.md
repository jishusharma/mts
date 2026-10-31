# Task Report: gemini-yt-vdpoppe-extract

- Task ID: `gemini-yt-vdpoppe-extract`
- Lane / Weight: CODEX / ROUTINE
- Date: 2026-10-31 (UTC: 2026-10-30)
- Operator / Model: JIS-NUC / Gemini Flash

## 1. Scope & Objective

Extract stated BTC levels, directional bias calls, and technical indicators read by Michaël van de Poppe (@michaelvdpoppe) from his latest 8 videos on YouTube, with timed quotes and exact Source GPS tags, into `MyTradingSys/research/yt_feed_2026-10-31/VDPOPPE_LEVELS_2026-10-31.md`.

## 2. Caption Ingestion Summary

Captions fetched using:
```bash
python scripts/dev/fetch_captions_timed.py --analyst vdPoppe --channel "@michaelvdpoppe" --latest 8 --out MyTradingSys/research/yt_feed_2026-10-31/transcripts_vdpoppe
```

Targeted latest 8 videos:
1. `4IDGi-O8SNg` (Why I Invest $25,000 in this Single Altcoin!, 2026-09-06) - auto captions OK (2690 words)
2. `Jn9hM3jwEik` (My Altcoin Portfolio Is Back In Profit!, 2026-10-18) - auto captions OK (2690 words)
3. `MY2rE9WUgzw` (I've Bought A New Altcoin For My Altcoin Portfolio!, 2026-09-20) - auto captions OK (2478 words)
4. `MiQePVTGCXQ` (The Ultimate Strategy How I trade Altcoins, 2026-10-11) - auto captions OK (3140 words)
5. `SfPE7sWygLE` (These Are My Top Altcoin Picks for October, 2026-10-04) - auto captions OK (2995 words)
6. `_QG1bt4iwQc` (My Altcoin Portfolio Has Doubled in 40 Days!, 2026-09-27) - auto captions OK (3251 words)
7. `fnRXA4AzEcI` (Altcoins Are About To Rally, I'm Holding These!, 2026-10-25) - auto captions OK (2662 words)
8. `zRIn-ZcFouk` (How I've Made $40,000 In One Month With Altcoins!, 2026-09-13) - auto captions OK (2292 words)

Totals:
- Videos read: 8
- Captioned: 8
- UNVERIFIED: 0

## 3. Extracted Items & Findings

Primary deliverable: `MyTradingSys/research/yt_feed_2026-10-31/VDPOPPE_LEVELS_2026-10-31.md`.
Contains:
- First line header: `Videos read: 8 (8 captioned, 0 UNVERIFIED).`
- Summary table: 29 items across all 8 videos covering BTC levels, directional bias, and technical indicators.
- Per-video verbatim extraction blocks with Source GPS tags (`BEGIN`, `MIDDLE`, `END` thirds).
- Verbatim quotes: 26 quotes verified against transcripts.
- `NOT_IN_DATA` items: 3 items explicitly recorded where the speaker did not cite specific numerical BTC levels (`zRIn-ZcFouk`) or technical indicators (`MY2rE9WUgzw`, `MiQePVTGCXQ`).

Key Stated Levels & Bias Calls:
- BTC 58k: Accumulation range base and bear market low level (`4IDGi-O8SNg:45`, `Jn9hM3jwEik:51`, `SfPE7sWygLE:34`, `fnRXA4AzEcI:145`).
- BTC 60k: Extreme downside tail correction scenario (`4IDGi-O8SNg:37`).
- BTC 70k - 75k: Primary correction support target zone (`4IDGi-O8SNg:74`, `Jn9hM3jwEik:189`, `MiQePVTGCXQ:343`, `_QG1bt4iwQc:64`).
- BTC 80k - 83k: Current consolidation support / floor level (`Jn9hM3jwEik:51`, `Jn9hM3jwEik:194`, `fnRXA4AzEcI:146`).
- BTC 88k: High of initial impulse wave (`fnRXA4AzEcI:145`).
- BTC 95k - 98k / 100k: Projected impulse continuation and range high (`Jn9hM3jwEik:197`, `SfPE7sWygLE:140`).
- Bias: Uniformly bullish / bull market confirmation (`4IDGi-O8SNg:27`, `Jn9hM3jwEik:181`, `MY2rE9WUgzw:168`, `SfPE7sWygLE:56`, `_QG1bt4iwQc:436`, `fnRXA4AzEcI:111`, `zRIn-ZcFouk:129`).
- Indicators Read: Bullish divergences on RSI and MACD across weekly/daily timeframes (`4IDGi-O8SNg:52`, `Jn9hM3jwEik:156`, `SfPE7sWygLE:95`, `fnRXA4AzEcI:321`), volume expansion (`zRIn-ZcFouk:149`).

## 4. Verification Gate

Command:
```bash
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/yt_feed_2026-10-31/VDPOPPE_LEVELS_2026-10-31.md
```
Result: `PASS: 0 problem(s)` (Exit code 0).
Every verbatim quote matches canonical transcript text and exact positional third (`BEGIN`, `MIDDLE`, `END`).
