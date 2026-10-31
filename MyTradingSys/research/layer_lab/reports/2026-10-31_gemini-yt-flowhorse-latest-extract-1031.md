# Task Report: gemini-yt-flowhorse-latest-extract-1031

- Task ID: `gemini-yt-flowhorse-latest-extract-1031`
- Lane / Weight: CODEX / ROUTINE
- Date: 2026-10-31 (UTC: 2026-10-31)
- Operator / Model: JIS-NUC / Gemini Flash

## 1. Scope & Objective

From the latest 8 videos of @TheFlowHorse (FlowHorse), extract stated BTC levels, order flow reads, and trade setups as a table with video ID, timestamp, and verbatim caption quote, or `NOT_IN_DATA`. Verify with `scripts/dev/verify_extract_quotes.py`.

## 2. Caption Ingestion Summary

Channel handle: `@TheFlowHorse` (uploader: `Ryan Rossi | Horse`).
Captions fetched using:
```bash
python scripts/dev/fetch_captions_timed.py --analyst FlowHorse --channel "@TheFlowHorse" --latest 8 --out MyTradingSys/research/gemini_burn_2026-10-31/transcripts_flowhorse-latest
```

Targeted latest 8 videos:
1. `KDh8txtcTeU` ("Liquid Tutorial: One Wallet for Stocks, Perps & Prediction Markets", 2026-10-28) - auto captions OK (2,079 words, en) [file: `raw_transcripts_canonical/KDh8txtcTeU_raw.txt`]
2. `N2iZdLOUE0Y` ("AI Debt Bomb - Did CoreWeave Just Crack the AI Trade?", 2026-10-17) - auto captions OK (4,250 words, en) [file: `raw_transcripts_canonical/N2iZdLOUE0Y_raw.txt`]
3. `T5TVsWhgqpE` ("Market Update FOMC Week | Stream Recap", 2026-09-13) - auto captions OK (3,306 words, en) [file: `raw_transcripts_canonical/T5TVsWhgqpE_raw.txt`]
4. `yJUYafb6vTk` ("Market Update | Stream Recap", 2026-09-09) - auto captions OK (4,060 words, en) [file: `raw_transcripts_canonical/yJUYafb6vTk_raw.txt`]
5. `B82RNrNjxZM` ("Weekend Market Update | Stream Recap", 2026-08-30) - auto captions OK (3,837 words, en) [file: `raw_transcripts_canonical/B82RNrNjxZM_raw.txt`]
6. `4jeFdS7RUcU` ("3 THINGS YOU NEED TO STAY IN THE TREND", 2026-08-23) - auto captions OK (2,762 words, en) [file: `raw_transcripts_canonical/4jeFdS7RUcU_raw.txt`]
7. `zMM9QgxfEFI` ("The Bitcoin Setup Changed - Market Overview and Analysis", 2026-08-19) - auto captions OK (2,762 words, en) [file: `raw_transcripts_canonical/zMM9QgxfEFI_raw.txt`]
8. `fl5cZac72rM` ("Your Stops Are Wrong", 2026-08-14) - auto captions OK (2,822 words, en) [file: `raw_transcripts_canonical/fl5cZac72rM_raw.txt`]

Totals [OURS]:
- Videos read: 8
- Captioned: 8
- UNVERIFIED: 0

## 3. Extracted Items & Verification

Primary deliverable: `MyTradingSys/research/gemini_burn_2026-10-31/FLOWHORSE_LATEST.md`.
Verification gate:
```bash
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/gemini_burn_2026-10-31/FLOWHORSE_LATEST.md
```
Result [OURS]:
- `PASS: 0 problem(s)` across 23 verbatim quotes / GPS tags verified against `raw_transcripts_canonical/`.

### Summary of Extracted Key Findings:
1. **Stated BTC Price Levels & Execution Trigger Zones:**
   - **`zMM9QgxfEFI` (2026-08-19):** Breakout above value area high overlap through $65,500 targets low 70s [SOURCED: `zMM9QgxfEFI` L310-L312]. Retest / dip buying at 50-yard line in the 66.5k-67k region [SOURCED: `zMM9QgxfEFI` L319-L321]. Gap invalidation boundary at 65.5k-66k [SOURCED: `zMM9QgxfEFI` L340-L343]. Upside target mid-70s / 72 [SOURCED: `zMM9QgxfEFI` L350-L352].
   - **`B82RNrNjxZM` (2026-08-30):** Dip buyer in the 76s and below; avoid aggressive chasing towards 80-81 [SOURCED: `B82RNrNjxZM` L322-L324]. Reclaim of 83 high triggers momentum longs [SOURCED: `B82RNrNjxZM` L327-L329]. Expansion target into mid/high 80s and 90k [SOURCED: `B82RNrNjxZM` L310-L312].
   - **`N2iZdLOUE0Y` (2026-10-17):** Invalidation/involvement zones: deep stab into the 70s or cleanly back above 84k [SOURCED: `N2iZdLOUE0Y` L430-L432]. Decisive momentum flip on reclaim of yearly open through 87.6k ($87,600) [SOURCED: `N2iZdLOUE0Y` L435-L438].
   - **`T5TVsWhgqpE` (2026-09-13):** Testing lower before higher; 90k rip requires reclaim of 83 [SOURCED: `T5TVsWhgqpE` L160-L163]. Downside rotation trading into gap [SOURCED: `T5TVsWhgqpE` L448-L450].
2. **Order Flow & Tape Reads:**
   - **`zMM9QgxfEFI`:** Tape absorption of Saylor / large entity selling ~7,000 BTC with price holding structure [SOURCED: `zMM9QgxfEFI` L188-L191].
   - **`N2iZdLOUE0Y`:** Reflexive flow dynamics from corporate holding strategies and forced flows out of index exclusions (e.g. MSCI) [SOURCED: `N2iZdLOUE0Y` L461-L463].
   - **`T5TVsWhgqpE`:** IBIT flows dropping off; upside confirmation requires IBIT spot aggression at NY open and widening CME basis [SOURCED: `T5TVsWhgqpE` L452-L457].
   - **`fl5cZac72rM`:** Liquidity sweeps beyond obvious swing highs/lows where retail stops cluster [SOURCED: `fl5cZac72rM` L65-L68].
3. **Trade Setups & Volatility Rules:**
   - **`yJUYafb6vTk` (2026-09-09):** Cleanest contextual risk-reward short defined against range high resistance with hard peel-off above high [SOURCED: `yJUYafb6vTk` L175-L180]. Flaggy consolidation setup on BTC and ETH [SOURCED: `yJUYafb6vTk` L395-L398].
   - **`4jeFdS7RUcU` (2026-08-23):** Initial RSI overbought reading indicates strong trend rather than reflexive fade [SOURCED: `4jeFdS7RUcU` L58-L62]. Trend entry on reclaim of 200-day MA and weekly 20 EMA [SOURCED: `4jeFdS7RUcU` L310-L314]. Setting stop distance according to ATR rather than swing low tick [SOURCED: `4jeFdS7RUcU` L410-L415].
   - **`fl5cZac72rM` (2026-08-14):** 30-minute BTC ATR is 218 points; placing stops tighter than 200 points guarantees noise-based stop-outs [SOURCED: `fl5cZac72rM` L330-L335].
