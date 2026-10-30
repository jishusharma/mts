# Lab Report: Pizzino Spec vs Method Blind Check (2026-10-31)

**Task**: `gemini-pizzino-spec-vs-method-blind-check`  
**Card Title**: `[GEMINI] Pizzino blind check: every SPEC.md rule (1/2/3-bar, 50% level, pivot, retest) re-found in method_jason.md or method_michael.md quotes, and pizzino_indicators.py constants vs SPEC (file:line)`  
**Producer**: Claude (`SPEC.md`, `method_jason.md`, `method_michael.md`, `pizzino_indicators.py`)  
**Reviewer**: Google Gemini (Antigravity worker)  
**Deliverable**: [GEMINI_BLIND_CHECK_2026-10-31.md](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/research/pizzino_layer_2026-10-27/GEMINI_BLIND_CHECK_2026-10-31.md)

---

## 1. Summary of Findings

Counts: SPEC Rules FOUND: 14, NOT_IN_DATA: 18, DIFF: 0 | Module Constants SAME: 12, DIFF: 0

1. **SPEC.md vs Method Files (`method_jason.md` and `method_michael.md`)**:
   - Out of 32 parameters and rules in `SPEC.md` section 8:
     - **FOUND (14)**: All 14 `SOURCED` rules (P01–P14) were verified with exact quotes and line numbers in `method_jason.md` and `method_michael.md`.
     - **NOT_IN_DATA (18)**: All 18 `OURS` parameters (P15–P32) represent our system design choices (swing sizes, strictness, lookback windows, retest tolerances, trade management). They are not provided in trader transcripts and are properly tagged as `NOT_IN_DATA` / `OURS` in `SPEC.md`.
     - **DIFF (0)**: Zero discrepancies found between what `SPEC.md` claimed was sourced and what the method files state.

2. **`pizzino_indicators.py` Constants vs `SPEC.md`**:
   - Out of 12 distinct functional constants, thresholds, and default parameters checked across `pizzino_indicators.py`:
     - **SAME (12)**: All 12 constants and logic definitions match `SPEC.md` specifications exactly.
       - Confirmation delay `i + n` ([pizzino_indicators.py:23,25](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py#L23-L25) vs [SPEC.md:15](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md#L15))
       - Pivot alternation ([pizzino_indicators.py:33-35](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py#L33-L35) vs [SPEC.md:15,146](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md#L15))
       - Swing state minimum history ([pizzino_indicators.py:58-59](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py#L58-L59) vs [SPEC.md:41](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md#L41))
       - Swing state formulas ([pizzino_indicators.py:60-64](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py#L60-L64) vs [SPEC.md:39-43,147](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md#L39-L43))
       - Confluence sum ([pizzino_indicators.py:69](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py#L69) vs [SPEC.md:43,132](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md#L43))
       - Lead turn window `L` ([pizzino_indicators.py:81](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py#L81) vs [SPEC.md:43,148](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md#L43))
       - Significance window `W` ([pizzino_indicators.py:90](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py#L90) vs [SPEC.md:65,149](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md#L65))
       - 50% midpoint formula ([pizzino_indicators.py:118](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py#L118) vs [SPEC.md:79,138](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md#L79))
       - Break confirmation `N=2` ([pizzino_indicators.py:141](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py#L141) vs [SPEC.md:96,152](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md#L96))
       - Retest tolerance `tol=0.005` ([pizzino_indicators.py:141](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py#L141) vs [SPEC.md:96,153](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md#L96))
       - Retest window `R=20` ([pizzino_indicators.py:141](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py#L141) vs [SPEC.md:96,154](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md#L96))
       - Reward/risk `rr_min=1.0` & fallback target `fallback_r=2.0` ([pizzino_indicators.py:166](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py#L166) vs [SPEC.md:111,114,156,157](file:///F:/MTS/gq/gemini-pizzino-spec-vs-method-blind-check/MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md#L111))
     - **DIFF (0)**: Zero discrepancies.

---

## 2. Command Checks

Line count check of `pizzino_indicators.py`:
- Command: `python -c "import ast,sys;print(len(open('MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py').read().splitlines()))"`
- Output: `182` lines

Noticed: `SPEC.md` faithfully distinguishes between Jason's consecutive bar-count signal (`bar_count`) and Michael's mechanical trend indicator states (`swing_state[1..3]`), referencing the appropriate brother's quotes for each concept.
