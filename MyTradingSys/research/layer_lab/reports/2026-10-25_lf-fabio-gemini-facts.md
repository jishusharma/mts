# Layer Fact Sheet Report: fabio family (`lf-fabio-gemini-facts`)

**Date:** 2026-10-25 (UTC) [SOURCED: system clock UTC]  
**Card:** `lf-fabio-gemini-facts` [CODEX, size S, prio 2]  
**Worker:** Gemini Flash (Antigravity worktree `gemini-q/lf-fabio-gemini-facts`)  
**Artifact:** `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/fabio.md`  

---

## 1. Execution Summary

Per task card instructions and `ANTIGRAVITY_LAPTOP.md` item C:
1. Ran `python scripts/dev/lab_query.py layers` and queried all 5 layers belonging to family `fabio`:
   - `fabio_cvd_absorption`
   - `fabio_escalation`
   - `fabio_volume_fvg`
   - `fabio_v3`
   - `fabio_of`
2. Queried active rulings using `python scripts/dev/lab_query.py rulings fabio`:
   - Checked rulings B179, B167, B137, B127, B123, B103, B102, B095, B090.
3. Examined all spec, ledger, rulebook, and backtest report files:
   - `MyTradingSys/system/LAYERS.md:44-72`
   - `MyTradingSys/system/layer_index.json`
   - `MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md`
   - `MyTradingSys/research/fast_track_2026-09-27/FABIO_RULEBOOK.md`
   - `MyTradingSys/research/fast_track_2026-09-27/FABIO_TRADE_MODEL.md`
   - `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md`
   - `MyTradingSys/research/P2_FABIO_V3_HOLDOUT_STATUS.md`
   - `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md`
   - `MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md`
   - `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-fabio-ledger-frames.md`
   - `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md`
   - `MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py`
   - `MyTradingSys/backtest/layers/fabio/fabio_escalation.py`
   - `MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py`
   - `MyTradingSys/backtest/layers/fabio/fabio_of_model.py`
4. Created fact sheet `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/fabio.md` covering all 5 layers across all 5 requested sections:
   - ORIGIN (quoted source)
   - PARAMETERS (labeled SOURCED or OURS)
   - BACKTESTS (path, fee-net, IS/OOS, n trades/days)
   - KNOWN BUGS / RULINGS
   - CONFLUENCE
   - Plus general family rulings and ledger frame audit findings.
   - Strictly zero verdicts on keeping, dropping, demoting, or parking any layer.
   - Every fact carries a concrete repo `file:line` citation or `NOT_IN_DATA`.

---

## 2. Key Facts Count

- **Layers covered:** 5 (`fabio_cvd_absorption`, `fabio_escalation`, `fabio_volume_fvg`, `fabio_v3`, `fabio_of`)
- **Facts documented:** 85+ individual sourced facts across the 5 sections and family summary.
