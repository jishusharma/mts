# Layer Fact Sheet Report: session_timing family (`lf-session_timing-gemini-facts`)

**Date:** 2026-10-28 (UTC) [SOURCED: system clock UTC]  
**Card:** `lf-session_timing-gemini-facts` [CODEX, size S, prio 2]  
**Worker:** Google Gemini (Antigravity worktree `mts-desktop-f7iu69n-lf-session_timing-gemini-facts`)  
**Artifact:** [`MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/session_timing.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-lf-session_timing-gemini-facts/MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/session_timing.md)  

---

## 1. Execution Summary

Per task card instructions and `MyTradingSys/system/ANTIGRAVITY_LAPTOP.md:27-34` item C:
1. Ran `python scripts/dev/lab_query.py layers session_timing`:
   - `session_momentum` (Intraday session momentum, status: FAIL, closed)
   - `turn_of_candle` (Turn-of-candle + quarter-hour opening order imbalance, status: no edge, closed)
   - `session_levels` (Failed first break of prior-day high/low T087, status: no edge)
2. Queried active rulings using `python scripts/dev/lab_query.py rulings session_timing` and examined `MyTradingSys/research/BUGS.md:212,283`:
   - Checked ruling B102 (offline session models anchor NY/London at fixed UTC minutes with no DST; replaced by `day_gates` DST rules).
   - Checked ruling B187 (PIT price-level study blocked by power gate on available DEV data).
3. Examined all spec, ledger, provenance, and backtest report files:
   - `MyTradingSys/system/LAYERS.md:148-165`
   - `MyTradingSys/system/layer_index.json:416-439`
   - `MyTradingSys/system/layer_map.json:1005-1045`
   - `MyTradingSys/backtest/layers/FORMULAS.md:345-397`
   - `MyTradingSys/backtest/layers/session/session_momentum.py:1-90`
   - `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:1-85`
   - `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:131-157`
   - `MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:1-43`
   - `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c2.md:1-40`
   - `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:1-31`
   - `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:68-114`
   - `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:1-43`
   - `MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:1-68`
   - `MyTradingSys/research/eur_low_us_sweep_followups_2026-10-18/RESULT.md:1-34`
   - `MyTradingSys/research/levels_sizing_2026-10-14/REPORT.md:1-48`
   - `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:123-145`
   - `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:31,37,64,70`
   - `MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:14,33`
   - `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8,31-32`
4. Created fact sheet [`MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/session_timing.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-lf-session_timing-gemini-facts/MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/session_timing.md) covering all 3 layers across all 5 requested sections:
   - ORIGIN (quoted source)
   - PARAMETERS (labeled SOURCED or OURS)
   - BACKTESTS (path, fee-net, IS/OOS, n trades/days/events)
   - KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (rulings)
   - CONFLUENCE
   - Strictly zero verdicts on keeping, dropping, demoting, or parking any layer.
   - Every fact carries a concrete repo `file:line` citation or `NOT_IN_DATA`.

---

## 2. Key Facts Count

- **Layers covered:** 3 layers (`session_momentum`, `turn_of_candle`, `session_levels`).
- **Facts documented:** 111 bullet fact items across the 5 standard sections, every line carrying a `file:line` citation or `NOT_IN_DATA`.
