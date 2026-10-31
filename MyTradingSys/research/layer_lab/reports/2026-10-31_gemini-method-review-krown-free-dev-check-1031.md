# Layer Lab Report: Method Review of Krown Free Setups DEV Check (Commit abf939506)

**Task ID:** `gemini-method-review-krown-free-dev-check-1031`  
**Lane:** CODEX  
**Reviewer:** Gemini 3.8 Flash (independent cross-vendor method review)  
**Date:** 2026-10-31 (UTC)  
**Target Commit:** `abf939506231b994cad22803ac521e395ee24af3`  
**Deliverable File:** `MyTradingSys/research/gemini_burn_2026-10-31/METHOD_REVIEW_KROWN_FREE_DEV_CHECK.md`  
**Registry Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`

---

## 1. Scope & Objective

Conduct a rigorous cross-vendor method review of the Krown free setups DEV check implementation committed in `abf939506`. Evaluate:
- Look-ahead risks
- Selection effects
- Missing costs
- Sample size ($n$) and statistical power
- Claims that outrun data
- Limitations and unchecked components

---

## 2. Key Audit Findings

1. **Look-Ahead Risk: NO ISSUE FOUND**
   - The signal calculation is strictly causal (`silver_cross_dev.py:61-68`), depending only on data up to the cross-day close.
   - Entry occurs at `open[t+1]` (`silver_cross_dev.py:77`), eliminating same-bar execution bias.
   - The two allowlist additions (`lookahead_allowlist.tsv:333-334`) are isolated to the unconditional all-days baseline forward-return computation (`silver_cross_dev.py:116-117`).
2. **Selection Effects: ISSUE IDENTIFIED**
   - 5 of 6 setup families were filtered out as `NOT_TESTABLE` due to missing formal definitions in YouTube captions (`PRE_REG.md:9-24`, `DEV_CHECK.md:13-17`).
   - Testing only the Silver Cross creates a survivorship/selection bias towards mathematically trivial moving-average crosses that do not represent Krown's broader discretionary strategy suite.
3. **Missing Costs: MINOR ISSUE**
   - Exchange taker fees ($0.10\%$ round trip) are sourced from `fees.py:BINANCE_TAKER` (`silver_cross_dev.py:18`).
   - Bid-ask spread and execution slippage are omitted ($0.00\%$). While average trade return (+7.87%) dwarfs fee costs, boundary trades near zero (-0.41% and -0.59% net) are sensitive to slippage.
4. **Sample Size ($n$) and Power: MAJOR ISSUE (Properly Handled)**
   - Sample size is severely underpowered ($n = 6$ events, 5 independent bootstrap blocks, `RESULT.csv:3-4`).
   - The 95% bootstrap confidence interval for hit rate is $[0.0\%, 87.5\%]$ (`RESULT.csv:10-11`), spanning almost the entire range.
   - Pre-registration properly declared the verdict `INCONCLUSIVE` ahead of the run (`PRE_REG.md:58-61`).
5. **Claims vs Data: NO FABRICATION / CLAIMS CONSERVATIVE**
   - The author strictly refrained from claiming Krown's 83% claim was refuted, explicitly stating that 83% falls inside the 95% confidence interval (`DEV_CHECK.md:47-48`).
6. **Unchecked Elements:**
   - 2018 to early 2022 pre-DEV history could not be verified due to DEV data boundary constraints (`PRE_REG.md:23-24`).
   - Undefined indicators ("Range Deviation", 5 EMA reconnect criteria) remain uncheckable without proprietary software.

---

## 3. Deliverables Status

- Full review document: [METHOD_REVIEW_KROWN_FREE_DEV_CHECK.md](file:///F:/MTS/gq/gemini-method-review-krown-free-dev-check-1031/MyTradingSys/research/gemini_burn_2026-10-31/METHOD_REVIEW_KROWN_FREE_DEV_CHECK.md)
- Report file: [2026-10-31_gemini-method-review-krown-free-dev-check-1031.md](file:///F:/MTS/gq/gemini-method-review-krown-free-dev-check-1031/MyTradingSys/research/layer_lab/reports/2026-10-31_gemini-method-review-krown-free-dev-check-1031.md)
- Zero engine or layer code modified.

Noticed: The pre-registration gate pattern requiring sha256 of frozen PRE_REG.md inside RESULT.csv effectively prevents post-hoc parameter tweaking and preserves auditability.
