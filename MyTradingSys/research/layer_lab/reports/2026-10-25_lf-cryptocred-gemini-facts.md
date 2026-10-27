# Layer Fact Sheet Report: cryptocred

- **Card ID**: `lf-cryptocred-gemini-facts` [SOURCED: `MyTradingSys/system/tasks/lf-cryptocred-gemini-facts.json:16`]
- **Date**: 2026-10-25 [SOURCED: system clock UTC]
- **Worker**: Gemini Flash (Antigravity worktree `gemini-q/lf-cryptocred-gemini-facts`)
- **Deliverable**: `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/cryptocred.md` [SOURCED: card scope in]

---

## 1. Commands Executed

- `python scripts/dev/lab_query.py layers` [SOURCED: card step 1]
  - Identified cryptocred row: id `cryptocred`, family `cryptocred`, status `adapter + stop sweep run`, module `backtest/layers/cryptocred/`.
- `python scripts/dev/lab_query.py rulings cryptocred` [SOURCED: card step 2]
  - Found rulings:
    - B143 (BLOCKED / MED): CryptoCred 0.1 percent stop buffer and 1.5R target are NO-SOURCE (`MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:1-8`).
    - B145 (CLOSED / LOW): classify_msb filter_range_noise is off in the live CryptoCred layer (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:1-8`).
    - B151 (CLOSED / MED): CryptoCred limit-fill backtest fills on touch and drops signals by a future event (`MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md:1-8`).
    - B154 (OPEN / MED): No regime-stratified and no session-stratified backtest verdict exists (`MyTradingSys/items/B154_regime_and_session_stratified_backtest.md:1-8`).

---

## 2. Summary of Findings

1. **Origin**:
   - Primary analyst is CryptoCred (`MyTradingSys/system/LAYERS.md:106`).
   - Covered setup clusters C07 (Retests), C08 (MSB Definition & Significance), C10 (Setup Types: S/R flip, Fib pullback, Failed MSB reversal) from `MyTradingSys/research/cross_trader_consolidated.md:255-440`.
   - All quotes verified directly against `cross_trader_consolidated.md` and `STOP_SOURCES.md`.

2. **Parameters**:
   - Categorized all parameters across `cc_structure.py`, `cc_retest.py`, `cc_setups.py`, and `run_cc_setups.py`.
   - Identified trader-sourced values: sequence violation (`require_prior_sequence=True`), fibonacci ratios (`fib_lo=0.618`, `fib_hi=0.786`), counter-trend target ratio (`target_r=2.0`).
   - Identified repo-invented choices (OURS / NO-SOURCE): fractal swing windows (left=2, right=2), use_body=True, range extreme filters (lookback=50, extreme_pct=0.25), retest tolerances (tolerance_pct=0.0015, invalidate_pct=0.005, expiry_bars=200, immediate_bars=5), and the 0.1% stop buffer and 1.5R target on setups 1 & 2.

3. **Backtests**:
   - Documented 7 distinct backtest/study runs with exact report paths, fee basis, split methodology, and trade counts:
     - Run 1: L1-D3 baseline (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:37-64`).
     - Run 2: CC setups touch-fill model (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:1-125`).
     - Run 3: CC setups trade-through by 1 tick rerun (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:144-245`).
     - Run 4: BigTrade exit policies backtest (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:21-56`).
     - Run 5: BigTrade fires parity check (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:16,24`).
     - Run 6: Stop placement and parameter sweep study (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:47-69`).
     - Run 7: Live range noise neutrality replay (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:29-34`).

4. **Known Bugs & Assumptions**:
   - Documented rulings B143, B145, B151, B154, and historical module indexing bug in `setup2_fib_pullback` fixed in `54ad393` (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:50-64`).

5. **Confluence**:
   - Documented trader's intended multi-timeframe and key-level confluence requirements vs repo's isolated single-timeframe implementation.
   - Cross-layer confirmations with Tom, Fabio, RSI recorded as NOT_IN_DATA.

---

## 3. Verification

- Every fact line in `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/cryptocred.md` carries an explicit `file:line` citation or `NOT_IN_DATA`.
- No verdict on keeping, dropping, demoting, or parking any layer was given.
