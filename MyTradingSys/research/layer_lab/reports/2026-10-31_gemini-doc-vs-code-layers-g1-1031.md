# Layer Lab Report: Audit of LAYERS.md Rows vs Code for fabio, kurisko, pizzino, session, session_levels

**Task ID:** `gemini-doc-vs-code-layers-g1-1031`  
**Lane:** CODEX  
**Reviewer:** Gemini 3.8 Flash (independent code-vs-doc audit)  
**Date:** 2026-10-31 (UTC 2026-10-31)  
**Registry Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  
**Deliverable File:** `MyTradingSys/research/gemini_burn_2026-10-31/LAYERS_VS_CODE_G1.md`  

---

## 1. Scope & Objective

Audit every stated parameter, window, formula, and rule documented across:
- `MyTradingSys/system/LAYERS.md`
- Related research notes (`FABIO_RULEBOOK.md`, `FABIO_TRADE_MODEL.md`, `KURISKO_SPEC.md`, `pizzino_layer_2026-10-27/SPEC.md`, `t087_session_levels_2026-10-09/RESULT.md`, `FORMULAS.md`)

against the actual implementation code under:
- `MyTradingSys/backtest/layers/fabio/`
- `MyTradingSys/backtest/layers/kurisko/`
- `MyTradingSys/backtest/layers/pizzino/`
- `MyTradingSys/backtest/layers/session/`
- `MyTradingSys/backtest/layers/session_levels/`

---

## 2. Key Audit Findings & Match Counts

1. **Target Layers Audited:** 5 families / layers (`fabio`, `kurisko`, `pizzino`, `session`, `session_levels`).
2. **Parameters & Mathematical Rules Verified:** 62 discrete items.
   - Exact Matches: 60 / 62 (SOURCED: see table in `LAYERS_VS_CODE_G1.md:14-43`).
   - Contradictions / Doc Discrepancies: 2 / 62 (SOURCED: `session_levels.py:24` vs `fabio_of_model.py:126`, and `fabio_of_model.py:10` docstring vs `fabio_of_model.py:123-128`).
3. **Identified Discrepancies:**
   - **Session Levels clock anchor (Fixed UTC vs DST):** In `session_levels.py:24` and `RESULT.md:3`, EU session is defined as 08:00-14:00 and US Open is fixed at 14:00 UTC (`US_OPEN_MIN = 840`, `session_levels.py:31`). This is an un-synced NO-SOURCE placeholder that ignores Ruling B102 DST transitions (London 07:00/08:00 UTC, NY 13:30/14:30 UTC), conflicting with `fabio_of_model.py:123-128` and `session_momentum.py:34-46`.
   - **Fabio OF Model docstring vs code:** In `fabio_of_model.py:10`, the docstring states static UTC windows (London 08:00-13:30, NY 13:30-21:00), but lines 123-128 implement `session_bounds(date)` with dynamic DST (`us_dst(date)`, `uk_bst(date)`).
4. **Subsystem Agreement:**
   - **Fabio:** Exact match across CVD absorption, escalation, volume profile FVG (70% VA, lowest-volume price bin), and Deribit taker fee update (5 bps/side).
   - **Kurisko Quad Rotation:** Exact match across all four stochastic bands `[(9,3), (14,3), (40,4), (60,10)]`, oversold/overbought thresholds (20/80), D = SMA_d(raw %K) line formula, and fast-line turn rule.
   - **Pizzino:** Exact match separating Jason bar count from Michael nested swings; exact match on degree lookbacks `(1, 2, 3)`, state values (+1/-1/0), confluence range (-3..+3), 50% line midpoint, and break-retest logic (`N=2`, `tol=0.5%`, `R=20`).
   - **Session Momentum:** Exact match on first-30m window predicting rest of session with DST-aware anchors.
   - **Session Levels:** Exact match on previous day high/low touch and 60-minute fail window evaluation.

---

## 3. Deliverables Status

- Full comparison table generated: [LAYERS_VS_CODE_G1.md](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g1-1031/MyTradingSys/research/gemini_burn_2026-10-31/LAYERS_VS_CODE_G1.md)
- Report generated: [2026-10-31_gemini-doc-vs-code-layers-g1-1031.md](file:///F:/MTS/gq/gemini-doc-vs-code-layers-g1-1031/MyTradingSys/research/layer_lab/reports/2026-10-31_gemini-doc-vs-code-layers-g1-1031.md)
- Zero engine or layer code modified (pure research audit).

Noticed: `session_levels.py` retains a fixed 14:00 UTC US open placeholder, whereas `session_momentum.py` and `fabio_of_model.py` dynamically apply Ruling B102 DST day gates.
