# Report: gemini-edge-blind-edge-xsec-momentum-1114

- Task: `gemini-edge-blind-edge-xsec-momentum-1114`
- Date: 2026-11-13 (UTC)
- Review file: `MyTradingSys/research/layer_lab/gemini_edge_1114/blind-edge-xsec-momentum/REVIEW.md`

## Summary of Findings

1. **Verdict**: **SOUND**
   - The reported conclusion "Verdict: UNDERPOWERED, no pass." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:3`) is fully supported by the tables and text.
   - What would change it: an expanded dataset with adequate statistical power where the validation confidence interval lower bound excludes zero and survives Benjamini-Hochberg multiple testing correction.

2. **Table Consistency and Arithmetic**:
   - 21 rows across 7 cells and 3 splits (`DEV` 159 wks, `VALIDATION` 53 wks, `RECENT` 70 wks; total 282 wks: `159 + 53 + 70 = 282`, OURS; recomputed from `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:9,15,16,17`).
   - Regime breakdown sums match exactly: DEV 35 bull + 30 bear + 94 range = 159; VALIDATION 14 bull + 5 bear + 34 range = 53; RECENT 8 bull + 12 bear + 50 range = 70 (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:7`, OURS).
   - Net return identity `net mean = gross - fee + funding` recomputed for all 21 rows matches reported net mean within +/-0.01% (attributable to 2 decimal places rounding, OURS).
   - In VALIDATION, all 7 cells have 95% CIs spanning roughly -2% to +3% a week (widths 2.33% to 5.63%, OURS), and minimum p-value is 0.420 (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:3,16`).

3. **Risks Exposed in the Text**:
   - Look-ahead / execution: "Limits: universe is a survivor list; weekly open prices from daily bars (not tradable fills); ~50-70 weeks per out-of-sample split." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:55`).
   - Fee / slippage: 0 bp slippage modeled; "Costs: fees.BINANCE_TAKER (5 bp) per side on drifted-weight turnover; Bybit funding history, long pays positive rate, short receives. Columns are weekly means." (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:11`). Fees (5-16 bp) are small relative to weekly volatility (200-500 bp), so statistical noise dominates.
   - Placebo validity: Long-short placebo 95th percentile in VALIDATION is +1.24% (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:42`), exceeding the best empirical factor (+0.39%, p=0.420).
   - Clustering / independence: Crypto cross-sectional market correlation and temporal autocorrelation; addressed with 4-week block bootstrap (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:13`), which yields wide CIs. Validation also suffers from severe regime imbalance (only 5 bear weeks out of 53, `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:7`).
   - Multiple testing / survivorship: Survivor list excludes delisted perps (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:9`); factor sign flips across regimes without BH significance (`MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-xsec-momentum_RESULTS.md:50`).

4. **Verification**:
   - Quote verification tool `scripts/dev/verify_extract_quotes.py` run on `REVIEW.md`: PASS with 0 errors (24 quotes verified verbatim against `edge-xsec-momentum_RESULTS.md`).
   - Quote verification tool `scripts/dev/verify_extract_quotes.py` run on this report: PASS with 0 errors.
