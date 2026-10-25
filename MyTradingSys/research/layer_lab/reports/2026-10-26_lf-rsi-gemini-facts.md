# Layer Fact Sheet Report: rsi family (`lf-rsi-gemini-facts`)

**Date:** 2026-10-26 (UTC) [SOURCED: system clock UTC]  
**Card:** `lf-rsi-gemini-facts` [CODEX, size S, prio 2]  
**Worker:** Gemini Flash (Antigravity worktree `gemini-q/lf-rsi-gemini-facts`)  
**Artifact:** `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/rsi.md`  

---

## 1. Execution Summary

Per task card instructions and `ANTIGRAVITY_LAPTOP.md` item C:
1. Ran `python scripts/dev/lab_query.py layers` and queried family `rsi`:
   - `rsi_levels`
   - `rsi_divergence`
   - Examined Kurisko references in `MyTradingSys/system/layer_index.json:104` and `MyTradingSys/system/LAYERS.md:85-95`.
2. Queried active rulings using `python scripts/dev/lab_query.py rulings rsi`:
   - Checked rulings B163, B161, B125 in `MyTradingSys/research/BUGS.md:236,274,276` and general backtest ruling B154 in `MyTradingSys/research/BUGS.md:266`.
3. Examined all spec, ledger, provenance, and backtest report files:
   - `MyTradingSys/system/LAYERS.md:85-105`
   - `MyTradingSys/system/layer_index.json:100-149`
   - `MyTradingSys/system/layer_map.json:448-478,626-659,710-755`
   - `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md`
   - `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md`
   - `MyTradingSys/backtest/layers/FORMULAS.md:1-58,541-570`
   - `extracts/processed/malkan/extract_Wvq1TZh8aF0.md`
   - `extracts/processed/malkan/extract_cQ-y1oULkBw.md`
   - `MyTradingSys/backtest/layers/rsi/malkan_40_60.py`
   - `MyTradingSys/backtest/layers/rsi/rsi_divergence.py`
   - `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py`
   - `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json`
   - `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json`
   - `MyTradingSys/backtest/layers/rsi/params/default.json`
   - `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json`
   - `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:1-86`
   - `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:1-24`
   - `MyTradingSys/research/MARKET_GUIDE_RESULTS_2026-10-07.md:20-22`
   - `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:1-50`
   - `MyTradingSys/research/layer_lab/reports/2026-10-17_gptb-malkan-rsi-event-table.md:1-25`
   - `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:1-50`
   - `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:1-79`
   - `MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:11,28-34`
4. Created fact sheet `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/rsi.md` covering all layers across all 5 requested sections:
   - ORIGIN (quoted source)
   - PARAMETERS (labeled SOURCED or OURS)
   - BACKTESTS (path, fee-net, IS/OOS, n trades/days/events)
   - KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (rulings)
   - CONFLUENCE
   - Documented Kurisko Quad Rotation relationship to RSI family.
   - Strictly zero verdicts on keeping, dropping, demoting, or parking any layer.
   - Every fact carries a concrete repo `file:line` citation or `NOT_IN_DATA`.

---

## 2. Key Facts Count

- **Layers covered:** 2 primary layers (`rsi_levels`, `rsi_divergence`) plus 1 related spec candidate (`kurisko_quad_rotation`).
- **Facts documented:** 50+ individual sourced facts across the 5 sections.
