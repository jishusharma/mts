# Sim Desk Test Plan Findings & Report

**Date:** 2026-10-31  
**Card ID:** `gemini-test-plan-sim-desk-1031`  
**Test Plan Document:** [`MyTradingSys/research/gemini_burn_2026-10-31/TEST_PLAN_SIM_DESK.md`](file:///F:/MTS/gq/gemini-test-plan-sim-desk-1031/MyTradingSys/research/gemini_burn_2026-10-31/TEST_PLAN_SIM_DESK.md)  
**Total Cases Analyzed:** 70  
- **EXISTS:** 39  
- **MISSING:** 31  

## 1. Summary of Verification

The test plan evaluates the 5 core operational domains of `MyTradingSys/research/sim_desk`:
1. **Empty Data Handling:** 16 cases evaluated (9 EXISTS, 7 MISSING). Verifies zero-length raw klines, zero filled trades, and edge-case behavior in streak, stats, breakdown, luck line, and equity curve functions.
2. **Data Gaps & Temporal Integrity:** 14 cases evaluated (9 EXISTS, 5 MISSING). Verifies single/multi-minute gaps, out-of-order timestamps, duplicate timestamps, and gap-through-stop fills.
3. **Symbol Switching:** 10 cases evaluated (5 EXISTS, 5 MISSING). Verifies `BTCUSDT` vs `ETHUSDT` data loading, parameter validation, coin tag isolation, and lack of ETH testing in fixed studies (`levels.py`, `krown.py`, `pitchfork.py`).
4. **Catalogue Rebuild:** 14 cases evaluated (6 EXISTS, 8 MISSING). Verifies dynamic indexing of study notes into `_catalogue.json`, missing verdict/title fallbacks, and exported count parity.
5. **Result Export & Look-Ahead Guards:** 16 cases evaluated (10 EXISTS, 6 MISSING). Verifies JSON schema compliance, path-traversal prevention, and strict enforcement of the `DEV` window (`2022-04-01` to `2024-06-30`, `CUT_MS = 2024-07-01`).

## 2. Top-10 MISSING Failure Cases Ranked by Blast Radius

| Rank | Target | Category | Description | Blast Radius |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `studies/levels.py:242 run()` | Symbol Switch | Running `levels` study with `symbol="ETHUSDT"` | CRITICAL: No symbol gate; hardcoded BTC assumptions lead to mismatched caches or unhandled errors. |
| 2 | `studies/_bars.py:108 resample()` | Gaps | Missing 1m minutes in raw kline arrays during resampling | HIGH: Irregularly spaced bars produced silently without synthetic fill or warning. |
| 3 | `desk.py:38 check_dates()` | Look-Ahead | Malformed date strings or inverted dates (`start > end`) | HIGH: Lacks unit test asserting exception raised on invalid format or inverted range. |
| 4 | `export_results.py:116 write()` | Export | Result file containing post-cut timestamps | HIGH: Risk of exporting non-DEV data into committed results. |
| 5 | `build_catalogue.py:39 date_of()` | Catalogue Rebuild | Git log failure or missing path date | MEDIUM: Returns `None` fallback unverified against sort routines. |
| 6 | `desk.py:107 monte_carlo()` | Empty Data | Permutation test with zero filled trades | MEDIUM: Untested against empty trade lists. |
| 7 | `studies/_bars.py:108 resample()` | Empty Data | Empty bar array input | MEDIUM: Slicing empty array untested. |
| 8 | `build_catalogue.py:79 verdict_of()`| Catalogue Rebuild | Empty note body without verdict line | MEDIUM: Fallback text untested on malformed notes. |
| 9 | `export_results.py:18 commit_of()` | Export | Untracked/uncommitted git files | LOW: Fallback to `"unknown"` untested. |
| 10 | `build_catalogue.py:87 kind_of()` | Catalogue Rebuild | Disambiguation of audit vs backtest | LOW: Regex classification boundaries untested in isolation. |

## 3. Verification Command
- Test suite execution: `python -m pytest MyTradingSys/research/sim_desk --basetemp=<tmp_dir> -q`
- Result: 169 passed, 11 skipped in 17.13s (clean).
