# Report: gemini-edge-blind-edge4-rsi-confirm-layers-1114

- Task: `gemini-edge-blind-edge4-rsi-confirm-layers-1114`
- Date: 2026-11-13 (UTC)
- Review file: `MyTradingSys/research/layer_lab/gemini_edge_1114/blind-edge4-rsi-confirm-layers/REVIEW.md`

## Summary of Findings

1. **Verdict**: **SOUND** (The reported study verdict of **FAIL** is completely supported by the empirical data and pre-registered protocol).
2. **Table Consistency**:
   - 56 pre-registered layer tests evaluated on VALIDATION (OURS; recomputed from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:21-78`).
   - Breakdown: 50 FAIL, 6 UNDERPOWERED (OURS; recomputed from table rows).
   - Recomputation of `vs base` relative difference against base VALIDATION mean R matches all 56 rows and 3 pair rows within rounding (+/- 0.001) (OURS).
   - Benjamini-Hochberg 10% FDR correction verified: `dADX20-25, 4h +2R` with placebo `p=0.012` is rank 5 across the 56 tests; required BH threshold is `(5 / 56) * 0.10 = 0.0089` (OURS), so it fails multiple-testing control.
3. **Risks Exposed Directly by Text**:
   - Look-ahead: "the OI/funding timestamp alignment uses the last record at or before signal close." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:121`).
   - Fee / slippage: "fees 2 x BINANCE_TAKER (10 bp RT, taker both legs, no slippage, no funding)" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:5`). Omits slippage and funding charges.
   - Placebo validity: "The two layers with Deep n = 0..5 ('UNDERPOWERED') carry p ~ 0 by construction and take BH ranks; excluding them does not change any verdict." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:80`).
   - Clustering: "trades across the 20 coins overlap in time (week blocks cover part)" (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:121`). Cross-sectional coin correlation during market-wide drops inflates effective sample size.
4. **Verification**:
   - Quote verification tool `scripts/dev/verify_extract_quotes.py` executed on `REVIEW.md` and passed with 0 errors (18 quotes verified verbatim).
