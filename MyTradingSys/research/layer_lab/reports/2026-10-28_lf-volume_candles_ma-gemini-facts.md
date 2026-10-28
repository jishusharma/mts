# Layer Fact Sheet Report: volume_candles_ma family (`lf-volume_candles_ma-gemini-facts`)

**Date:** 2026-10-28 (UTC) [SOURCED: system clock UTC]  
**Card:** `lf-volume_candles_ma-gemini-facts` [CODEX, size S, prio 2]  
**Worker:** Google Gemini (Antigravity worktree `mts-desktop-f7iu69n-lf-volume_candles_ma-gemini-facts`)  
**Artifact:** [`MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/volume_candles_ma.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-lf-volume_candles_ma-gemini-facts/MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/volume_candles_ma.md)  

---

## 1. Execution Summary

Per task card instructions and `MyTradingSys/system/ANTIGRAVITY_LAPTOP.md:27-34` item C:
1. Ran `python scripts/dev/lab_query.py layers volume_candles_ma`:
   - `volume` (Volume intensity / exhaustion / time-of-day V0-V4, status: no validated edge; HOLDOUT sealed)
   - `candle_patterns` (Classical candle patterns: 18 patterns x h 1,3,5; 1d and 1h, status: pilot run)
   - `ma_daily` (Daily long-flat MA setups: SMA200, EMA, RSI2, ADX, Supertrend, status: NO-SOURCE [chatbot handoff numbers])
   - `bigtrade_fires` (Layer fires x exit policies, status: fires + exit policies run, HOLDOUT unread)
2. Queried active rulings using `python scripts/dev/lab_query.py rulings volume_candles_ma` and examined `MyTradingSys/research/BUGS.md:270`:
   - Checked ruling B163 (operator pasted a 'Setup Alpha / Setup Beta' BTC perp handoff; chatbot output ungrounded in trader literature).
3. Examined all spec, ledger, provenance, and backtest report files:
   - `MyTradingSys/system/LAYERS.md:169-195`
   - `MyTradingSys/system/layer_index.json:150-205`
   - `MyTradingSys/system/layer_map.json:970-1045`
   - `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:1-50`
   - `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:1-42`
   - `MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md:1-38`
   - `MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md:1-30`
   - `MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md:1-35`
   - `MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:1-35`
   - `MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:1-35`
   - `MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:1-50`
   - `MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md:1-40`
   - `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:1-45`
   - `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:1-55`
   - `MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:1-48`
   - `MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:1-50`
   - `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:1-85`
   - `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:1-147`
   - `MyTradingSys/research/bigtrade_2026-10-09/CAPTURE_MATRIX_SPOT.md:1-60`
   - `MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:15,30`
   - `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8,33`
4. Created fact sheet [`MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/volume_candles_ma.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-lf-volume_candles_ma-gemini-facts/MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/volume_candles_ma.md) covering all 4 layers across all 5 requested sections:
   - ORIGIN (quoted source)
   - PARAMETERS (labeled SOURCED or OURS)
   - BACKTESTS (path, fee-net, IS/OOS, n trades/days/events)
   - KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (rulings)
   - CONFLUENCE
   - Strictly zero verdicts on keeping, dropping, demoting, or parking any layer.
   - Every fact carries a concrete repo `file:line` citation or `NOT_IN_DATA`.

---

## 2. Key Facts Count

- **Layers covered:** 4 layers (`volume`, `candle_patterns`, `ma_daily`, `bigtrade_fires`).
- **Facts documented:** 110 bullet fact items across the 5 standard sections, every line carrying a `file:line` citation or `NOT_IN_DATA`.
