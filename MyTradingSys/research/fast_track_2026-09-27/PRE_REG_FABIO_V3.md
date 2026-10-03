# PRE-REGISTRATION FABIO V3 - L3 historical backtest (2026-10-03)

Session: MTS-2026-10-03-1759Z-CLI-BLD-tf8-fabio-v3-histori. Row: BUILD_PIPELINE.md 1.10 (TF8). Spec: FABIO_V3_SPEC.md v3.1 sections 7.2, 8
(this file fixes only what the spec leaves open; where the spec decides, the spec wins). Written and committed BEFORE the runner exists or runs.
Code under test: backtest/layers/fabio/v3 at the commit that carries this file (any change to v3/*.py or backtest/fees.py after it voids this block).

## The four required fields
- Metric: mean DAY net R (day R = risk_u * net_r of the day's first-leg trade, 0 if no trade) per model, NY window, fees from backtest/fees.py via v3/costs.py
  (maker 0.0, taker 0.0005), slippage 2 bps per taker leg for selection and the primary figure; 0 and 5 bps reported.
- Threshold: OOS mean day net R > 0 with week-block bootstrap 95% CI lower bound > 0 (2000 draws, seed 12345); DSR >= 0.95 with N = 139; PBO <= 0.2 (CSCV S 16).
- Stop rule: one run per (model, config hash). Selection is IS-only; the OOS block is read once per model after selection is frozen in the output file.
  Stop and report INSUFFICIENT-N if OOS day count is below n = ((1.96+0.8416)*SD_IS/0.2)^2. No re-run to change a cell, seed, split, slippage or threshold;
  a bug-fix re-run is a new trial row. The holdout 2026-06-26..2026-09-28 is NOT read in this task (spec 8: once, after freeze, by a later task).
- N for DSR: 139 declared cells (spec 7.2: stage 1 = 6, A = 48, B = 24, C = 16, D = 24, variants = 20, B trail = 1). Cells declared but not executed here
  (stage 1 event study 6; variants s7 off, S8(d) off, add_mode day = 12 cells: no engine config key) still count in N. Stage 3 (+12) is not run and not counted.

## Design
- Data: F:/MTS/data/orderflow_1m via orderflow_bars.load_days, 2024-12-02..2026-09-28. Days with thr_days == 0 and windows with > 5 missing minutes excluded
  (spec 1). NY window per day_gates.ny_open_utc (DST-aware, US_CLOSED), 390 bars, one engine.run per (day, cell, model) with models=(model,).
- Split (spec 8): IS 2024-12-02..2025-12-31; OOS 2026-01-01..2026-06-25. Walk-forward = frozen IS selection then single OOS pass (the spec's walk-forward form).
- Grid (spec 7.2, main grid mgmt "event", k_bal 0.8, z_hi 2.5 unless listed; engine required keys all set explicitly):
  A: N{60,120,240} x p{0.05,0.10} x f{0.003,0.005} x entry{rest,confirm} x g{off,0.8} = 48 (m_c = 15 passed, unused by A).
  B: N x z_hi{2.0,3.0} x f x entry = 24 (p 0.10, g off, target_mode edge). C: m_c{5,15} x f x entry x g = 16 (N 120, p 0.10 passed, unused).
  D: N x p x f x entry = 24 (g off). Variants on each model's IS-chosen cell: mgmt dist with be_k 1.0 and 2.0 (8 cells); B target_mode trail (1 cell).
- Selection: per model, the IS-best cell by mean day net R at 2 bps (ties: first in grid order). Primary report = the chosen cell's OOS figures.
- Statistics: bt_stats.dsr / psr (Sharpe per day, N 139, var_sr = variance of the per-day Sharpe across the executed cells), pbo_cscv on the per-model IS+OOS day-R
  matrix of the main-grid cells; week-block bootstrap on OOS day R.
- Decision (fixed now): PASS-L3 needs every Threshold item AND the spec 8 items not run here; since null permutation, stop-first/funding-2x stress, the regime rule
  and the holdout are NOT run in this task, the best possible outcome is "L3-PARTIAL-PASS" (all executed thresholds met) or "L3-FAIL" (any executed threshold missed).
  Per spec 8 a fail on BTC does not mean the extraction was wrong (TOM_FABIO_REVIEW s2 limit b).

## Declared engine limits (reported with the result, not tuned)
- engine.run returns the FIRST LEG only; adds are not executed (v3 README). Model B IN_TRADE and model A confirm IN_TRADE are reported without management
  (engine._manage returns None): such days count as 0 R and are tallied as "unmanaged". Tier S4 is fixed "99" (no prior_vols), a spec S4 fallback.
- Day gate g = 0.8 uses prior_ranges built from the prior 20 valid weekday NY windows of the same elapsed range (spec 6); fewer than 20 prior -> fail closed (engine).
- Funding is not in the bars and is not charged (spec 5.3 own line; stress not run).

## Result block
Appended after the run by the same session, below this line. Nothing has been run at the time of this commit.

Result block (appended 2026-10-04, session MTS-2026-10-03-1759Z-CLI-BLD-tf8-fabio-v3-histori): NO RESULT. The OOS pass hung (B099) and was killed; no OOS figure, DSR, PBO or CI exists. The IS grid completed and the IS-best cells were frozen in selection.json before any OOS window ran (A N60/p0.05/f0.003/rest/g0.8, B N60/z2/f0.003/rest, C m5/f0.005/rest/g0.8, D N240/p0.05/f0.003/rest). Verdict: not evaluated. A re-run after the B099 fix is a new trial row; the registered cells, split and thresholds above are unchanged.
