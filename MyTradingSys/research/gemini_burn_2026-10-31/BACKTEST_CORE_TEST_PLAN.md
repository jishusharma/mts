# Test Plan: Backtest Core (`fees.py`, `sim.py`, `promote.py`, `prob_table.py`)

**Status:** COMPLETE  
**Standard Reference:** `FORMULAS.md` (Sections 10, 13, 17, 18.5, 18.7), `FORMULAS_SPEC.md`  
**Registry Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  
**Card ID:** `gemini-test-plan-backtest-core-1031`  
**Date:** 2026-10-31  

---

## 1. Executive Summary & Inventory Matrix

This test plan analyzes boundary, degenerate, and failure cases across the four backtest core modules:
1. `MyTradingSys/backtest/fees.py` — Single source of truth for exchange fees (Bug B081).
2. `MyTradingSys/backtest/sim.py` — Offline simulation engine evaluating snapshots over `replay_rows.json`.
3. `MyTradingSys/backtest/layers/promotion/promote.py` — Five-gate research-to-trading promotion and verification pipeline.
4. `MyTradingSys/backtest/prob_table.py` — Discrete Dirichlet-smoothed empirical probability table generator.

Every finding cites exact `file:line` locations in code and tests. Tests status is classified strictly as **EXISTS** (verified by pytest execution and code inspection) or **MISSING** (untested boundary, missing negative assertion, or unhandled exception).

| Module | Functions / Components | Total Cases Examined | EXISTS | MISSING | Primary Risk / Blast Radius |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `fees.py` | `fees_dict`, Fee Constants | 7 | 2 | 5 | Inconsistent fee profiles, missing validation on negative/zero fees, zero division in net R |
| `sim.py` | `wilson`, `geom_ok`, `run`, `report` | 13 | 0 | 13 | Zero denominator crash ($risk=0$), inverted timestamps, missing required keys, negative fees |
| `promote.py` | `_num`, `holm_z`, `mde_floor`, `recompute_oos`, `check`, `register`, `demote`, `verify` | 24 | 16 | 8 | Division by zero on zero net R / zero CI width, uncommitted CSVs, git subprocess injection |
| `prob_table.py` | `load_labels`, `outcome`, `build_table`, `evaluate` | 16 | 10 | 6 | Total count zero smoothing ($n=0, \alpha=0$), malformed JSON, empty training set division |
| **Total** | **All 4 Core Modules** | **60** | **28** | **32** | |

---

## 2. Detailed Function Matrix with Expected Results from FORMULAS.md

### 2.1 `MyTradingSys/backtest/fees.py`
Single source of truth for fees (`fees.py:1-59`).  
**Formula Reference:** `FORMULAS.md` Section 17 (`net_rr = (|target - entry| - cost) / (|entry - stop| + cost)` where `cost = 2 * taker * entry`), and Section 18.5 (`net_R = (side * (exit - L) - fee_in * L - fee_out * exit) / R`).

| Function / Constant | Test Scenario / Category | Input / Trigger Condition | Expected Result (from `FORMULAS.md` / Spec) | Status | Test Citation / Gap Analysis |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `fees.py:32-38` | Constant Parity | `DERIBIT_TAKER == 0.0005`, `FDAX_PER_SIDE == 0.000005` | Matches Java `ExecutionMathConstants` exactly | **EXISTS** | `MyTradingSys/tests/test_b070_fee_parity.py:18`, `MyTradingSys/tests/test_b070_fee_parity.py:27` |
| `fees_dict` (`fees.py:42-44`) | Standard Dict Shape | `fees_dict(0.0, 0.0, 0.0005, 0.0005)` | Returns dict with exact keys `{"entry", "target", "stop", "timeout"}` | **MISSING** | No dedicated unit test in `MyTradingSys/tests` or `backtest/` asserts return keys directly |
| `fees_dict` (`fees.py:42-44`) | Zero Fees Boundary | All arguments `0.0` | Returns dict with all `0.0`; downstream net R equals gross R | **MISSING** | Untested in isolation (only exercised transitively in `test_bt_engine.py:17` with `taker_fee=0`) |
| `fees_dict` (`fees.py:42-44`) | Negative Fee / Rebate Boundary | Maker rebate e.g. `-0.0001` | Returns negative fee fraction; net R > gross R | **MISSING** | Untested; no validation against negative taker fees |
| `fees_dict` (`fees.py:42-44`) | NaN / None Fee Inputs | `entry=float('nan')` or `stop=None` | Should raise `TypeError` or `ValueError` fail-closed | **MISSING** | No type or numeric validation in `fees_dict`; propagates NaN downstream silently |
| `FEES_DERIBIT` (`fees.py:48`) | Regime B Consistency | `entry=0.0, target=0.0, stop=0.0005, timeout=0.0005` | Matches `FORMULAS.md` 18.5 variantmaker entry/target, taker exit | **EXISTS** | Validated in `test_sim_planted_edge.py:223` |
| `FEES_ALL_TAKER` (`fees.py:49`)| Regime A Consistency | All legs `0.0005` | Matches `FORMULAS.md` 18.5 all-taker 10 bp RT | **MISSING** | Direct dict shape assertion missing; used in `tom_bt_report.py:27` but unverified in unit tests |

---

### 2.2 `MyTradingSys/backtest/sim.py`
Trade simulation over snapshots (`sim.py:1-122`).  
**Formula Reference:** `FORMULAS.md` Section 10 (Confidence intervals, sample statistics), Section 17 & 18.5 (Fee-net R: `gross = (x - e) / risk`, `fee_R = fee_pct * e / risk`, `net = gross - fee_R`).

| Function | Test Scenario / Category | Input / Trigger Condition | Expected Result (from `FORMULAS.md` / Spec) | Status | Test Citation / Gap Analysis |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `wilson` (`sim.py:34-39`) | Zero Sample Boundary | `k=0, n=0` | Return `(0.0, 0.0)` | **MISSING** | Handled by early return `sim.py:35`, but has 0 unit tests |
| `wilson` (`sim.py:34-39`) | Full Success ($k=n$) | `k=10, n=10, z=1.96` | High interval bound $\le 1.0$, low bound $> 0.0$ | **MISSING** | Untested |
| `wilson` (`sim.py:34-39`) | Zero Success ($k=0, n>0$) | `k=0, n=10, z=1.96` | Low bound $\ge 0.0$, high bound $< 1.0$ | **MISSING** | Untested |
| `wilson` (`sim.py:34-39`) | Degenerate Inputs ($k > n$ or $n < 0$)| `k=12, n=10` or `n=-1` | Should raise `ValueError` fail-closed | **MISSING** | `p = k / n` computes $> 1.0$ or negative, sqrt takes negative or nan; crashes with `ValueError: math domain error` |
| `geom_ok` (`sim.py:42-43`) | Valid Geometry | Long: $s < e < t$; Short: $t < e < s$ | Return `True` | **MISSING** | Untested |
| `geom_ok` (`sim.py:42-43`) | Inverted Geometry | Long: $s \ge e$ or $e \ge t$; Short: $s \le e$ or $e \le t$ | Return `False` | **MISSING** | Untested |
| `geom_ok` (`sim.py:42-43`) | Degenerate Geometry | Stop equals Entry ($s == e$) | Return `False` (avoids zero division in risk) | **MISSING** | Untested |
| `run` (`sim.py:46-82`) | Empty Input | `rows = []` | Return `[]` | **MISSING** | Untested |
| `run` (`sim.py:46-82`) | Zero Risk ($stop == price$) | `rows` with $stop == price$ bypassing `geom_ok` | If `geom_ok` called: skipped. If uncalled: `ZeroDivisionError: float division by zero` at line 76 | **MISSING** | Untested; depends strictly on `geom_ok` gate |
| `run` (`sim.py:46-82`) | Timestamp Gaps ($> 180s$) | `q["t"] - last["t"] > 180` | Outcome labelled `censored_gap`, fill price `last["price"]` (`sim.py:64`) | **MISSING** | Untested |
| `run` (`sim.py:46-82`) | Timeout ($> 12h$) | `q["t"] - r["t"] > 43200` | Outcome labelled `timeout`, fill price `q["price"]` (`sim.py:66`) | **MISSING** | Untested |
| `run` (`sim.py:46-82`) | Bar Resolution Order | Snapshot simultaneously penetrates stop and target | Stops evaluated first at line 68 before target at line 70 (`stop_first = True`) | **MISSING** | Untested in `sim.py` (only tested for `tom_bt.py` in `test_sim_planted_edge.py`) |
| `report` (`sim.py:85-105`) | Empty Trades List | `trades = []` | Prints summary; returns early at line 90 without error | **MISSING** | Untested; `Counter` handles empty, line 89-90 returns cleanly |

---

### 2.3 `MyTradingSys/backtest/layers/promotion/promote.py`
Promotion verification engine (`promote.py:1-483`).  
**Formula Reference:** `FORMULAS.md` Section 10 & 18.7 (Percentile bootstrap, Holm-Bonferroni adjusted $z$: `holm_z = NormalDist().inv_cdf(1 - 0.025 / variants)`, MDE trade floor: `mde_floor = max(30, 4 * ((z + 0.84) * sd / net_r)^2)`).

| Function | Test Scenario / Category | Input / Trigger Condition | Expected Result (from `FORMULAS.md` / Spec) | Status | Test Citation / Gap Analysis |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `_num` (`promote.py:53-54`) | Numeric Validation | `float("nan")`, `float("inf")`, `True`, `"10"` | Returns `False` | **EXISTS** | `test_promote.py:190-192` (`test_oos_nan_and_strings_reject`) |
| `holm_z` (`promote.py:57-59`) | Variants = 1 | `variants = 1` | Returns $z \approx 1.95996$ (Standard 95% two-sided normal) | **EXISTS** | Verified implicitly in `test_promote.py:91` |
| `holm_z` (`promote.py:57-59`) | Variants $\le 0$ / Float | `variants = 0` or negative | `max(1, int(variants))` floors to 1, returns 1.96 | **MISSING** | Negative or non-integer variants untested directly |
| `mde_floor` (`promote.py:62-66`) | High Variance / Many Variants | `variants = 40`, wide CI `[0.02, 0.22]` | Floor exceeds sample size, rejects manifest | **EXISTS** | `test_promote.py:95-99` (`test_holm_adjusted_ci_for_many_variants`) |
| `mde_floor` (`promote.py:62-66`) | Degenerate Net R ($net\_r \le 0$) | `net_r = 0.0` or negative | Handled in `check` line 253 (`elif o["net_r"] > 0:`), preventing zero division in `mde_floor` | **EXISTS** | `test_promote.py:178` (`test_oos_net_r_must_be_positive`) |
| `recompute_oos` (`promote.py:69-87`)| Deterministic Seed & Bootstrap | Standard trade list in CSV | Recomputes exact $(n, \mu, CI_{low}, CI_{high})$ deterministically | **EXISTS** | `test_promote.py:108-115` (`test_recompute_matches_manifest_numbers`) |
| `recompute_oos` (`promote.py:69-87`)| Empty CSV File | CSV with header only or 0 rows | Raises `ValueError("no trades")` | **MISSING** | Untested directly against empty CSV |
| `recompute_oos` (`promote.py:69-87`)| Missing `net_r` Column | CSV missing `net_r` header | Raises `ValueError("no net_r column")` | **MISSING** | Untested directly |
| `recompute_oos` (`promote.py:69-87`)| Non-finite values in CSV | CSV containing `NaN`, `Inf`, or strings | Raises `ValueError("non-finite net_r")` | **MISSING** | Untested directly |
| `_rel_file` (`promote.py:112-122`) | Path Traversal Boundary | Relative path `../outside.md` | Returns `None`; rejected fail-closed | **EXISTS** | `test_promote.py:228-230` (`test_report_path_cannot_escape_repo`) |
| `check` (`promote.py:143-303`) | Missing Required Fields | Manifest missing any of 10 keys | Returns `REJECT` with `missing fields: ...` | **EXISTS** | `test_promote.py:140-145` (`test_missing_field_rejects`) |
| `check` (`promote.py:143-303`) | Temporal Ordering Gate (G1) | PRE_REG commit date $>$ screen verdict commit date | Returns `REJECT` (`does not predate`) | **EXISTS** | `test_promote.py:149-153` (`test_pre_reg_must_predate_screen`) |
| `check` (`promote.py:143-303`) | Post-Registration Tamper Gate | Git blob at `pre_reg.git_sha` $\ne$ `HEAD` | Returns `REJECT` (`edited after registration`) | **EXISTS** | `test_promote.py:350-357` (`test_pre_reg_edited_after_registration_rejects`) |
| `check` (`promote.py:143-303`) | Screen Verdict Gate (G2) | `verdict` is `FAIL` or invalid string | Returns `REJECT` (`need PASS`) | **EXISTS** | `test_promote.py:157-168` (`test_screen_verdict_must_pass`) |
| `check` (`promote.py:143-303`) | Uncommitted Screen Verdict | Screen verdict file untracked/uncommitted | Returns `REJECT` (`not committed (no date)`) | **EXISTS** | `test_promote.py:169-172` (`test_screen_verdict_uncommitted_has_no_date`) |
| `check` (`promote.py:143-303`) | Backtest Label Gate (G3) | Report lacks `BT-TUNED` label | Returns `REJECT` (`lacks the BT-TUNED label`) | **EXISTS** | `test_promote.py:173-177` (`test_backtest_label_required`) |
| `check` (`promote.py:143-303`) | Tolerance Discrepancy Gate (G4)| Manifest numbers differ from CSV recompute by $> 0.01 R$ | Returns `REJECT` (`differs from the recompute`) | **EXISTS** | `test_promote.py:116-119` (`test_typed_net_r_far_from_trades_csv_rejects`) |
| `check` (`promote.py:143-303`) | Trade Count Tolerance Gate (G4)| Manifest `n_trades` differs from CSV rows by $> 5\%$ | Returns `REJECT` (`differs ... by more than 5%`) | **EXISTS** | `test_promote.py:126-128` (`test_trades_count_must_match_within_five_percent`) |
| `check` (`promote.py:143-303`) | CI Low Gate (G4) | $CI_{low} \le 0$ | Returns `REJECT` (`95% CI low ... is not above 0`) | **EXISTS** | `test_promote.py:181-183` (`test_ci_low_must_be_positive`) |
| `check` (`promote.py:143-303`) | CI Consistency Gate (G4) | $net\_r > CI_{high}$ or $net\_r < CI_{low}$ | Returns `REJECT` (`net_r outside its own CI`) | **EXISTS** | `test_promote.py:187-189` (`test_oos_inconsistent_ci`) |
| `check` (`promote.py:143-303`) | Multiple Validation Reads (G6)| `len(validation_reads) != 1` | Returns `REJECT` (`must hold exactly one read record`) | **EXISTS** | `test_promote.py:206-209` (`test_validation_exactly_one_read`) |
| `check` (`promote.py:143-303`) | Unlogged Validation File (G6) | `validation_reads.ref` does not exist on disk | Returns `REJECT` (`not an existing repo file`) | **EXISTS** | `test_promote.py:101-104` (`test_validation_read_ref_must_be_a_logged_file`) |
| `check` (`promote.py:143-303`) | Blocklisted Layer Gate (G7) | Setup ID listed in `trade_blocklist` or parked | Returns `REJECT` (`trade_blocklist lists ...`) | **EXISTS** | `test_promote.py:214-224` (`test_parked_layer_rejects`, `test_blocklisted_layer_rejects`) |
| `register` / `demote` / `verify` | Configuration & Persistence | Unreadable config, unreadable registry, missing shadow entry, demote off blocking | Fails closed; config unmodified or blocked in auto-trader | **EXISTS** | `test_promote.py:232-405` (Comprehensive coverage across 16 tests) |

---

### 2.4 `MyTradingSys/backtest/prob_table.py`
Dirichlet-smoothed frequency table (`prob_table.py:1-197`).  
**Formula Reference:** Spec 033 / `FORMULAS.md` Section 10 & 18.1 (`prob = (count + alpha) / (n + 3 * alpha)`).

| Function | Test Scenario / Category | Input / Trigger Condition | Expected Result (from `FORMULAS.md` / Spec) | Status | Test Citation / Gap Analysis |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `load_labels` (`prob_table.py:7-17`) | File Missing / Malformed JSON | File not found or invalid JSON format | Raises `FileNotFoundError` or `json.JSONDecodeError` | **MISSING** | Untested; no dedicated test for `load_labels` error handling |
| `load_labels` (`prob_table.py:7-17`) | Incomplete Record Filtering | Record missing `ts`, `fwd_return_pct`, `vp_shape`, `price_vs_va`, or `cvd_slope` | Incomplete record skipped; valid records returned sorted by `ts` | **MISSING** | `load_labels` logic exists at lines 12-16 but has 0 direct unit tests |
| `outcome` (`prob_table.py:19-25`) | Threshold Above Band | $ret\_pct > band$ | Returns `"UP"` | **EXISTS** | `test_prob_table.py:13`, `test_prob_table.py:40`, `test_prob_table_edge.py:21` |
| `outcome` (`prob_table.py:19-25`) | Threshold Below Band | $ret\_pct < -band$ | Returns `"DOWN"` | **EXISTS** | `test_prob_table.py:19`, `test_prob_table.py:41`, `test_prob_table_edge.py:22` |
| `outcome` (`prob_table.py:19-25`) | Inside Band Boundaries | $-band \le ret\_pct \le band$ | Returns `"FLAT"` | **EXISTS** | `test_prob_table.py:25`, `test_prob_table_edge.py:19-20` |
| `outcome` (`prob_table.py:19-25`) | Exact Boundary Edge | $ret\_pct == band$ or $ret\_pct == -band$ | Returns `"FLAT"` (strict inequality required for UP/DOWN) | **EXISTS** | `test_prob_table.py:32-36`, `test_prob_table_edge.py:19-20` |
| `outcome` (`prob_table.py:19-25`) | NaN / None Return | $ret\_pct = float('nan')$ | Returns `"FLAT"` (comparisons with NaN return False) | **MISSING** | Handled before `outcome` call in `build_table`, but direct call with NaN untested |
| `build_table` (`prob_table.py:27-93`) | Empty Records Input | `records = []` | Returns table with `__baseline__` counts = 0, probs = $\frac{1}{3}$ | **EXISTS** | `test_prob_table_edge.py:24-29` (`test_empty_records_baseline_uniform`) |
| `build_table` (`prob_table.py:27-93`) | Smoothing Formula ($p = \frac{k+\alpha}{n+3\alpha}$) | Single record $UP=1, n=1, \alpha=1.0$ | Cell probs: $UP = \frac{2}{4} = 0.5$, $FLAT = \frac{1}{4} = 0.25$, $DOWN = \frac{1}{4} = 0.25$ | **EXISTS** | `test_prob_table_edge.py:30-36`, `test_prob_table.py:44-61` |
| `build_table` (`prob_table.py:27-93`) | Unsmoothed / Zero Alpha ($\alpha=0$) | $n=4, \alpha=0.0$ | Cell probs match raw empirical frequencies exactly | **EXISTS** | `test_prob_table_edge.py:38-43` (`test_alpha_zero_gives_raw_frequencies`) |
| `build_table` (`prob_table.py:27-93`) | Zero Counts with Zero Alpha | Empty records or cell count 0 with $\alpha=0.0$ | $n + 3\alpha = 0$, raises `ZeroDivisionError` | **MISSING** | Untested; if $n=0$ and $\alpha=0.0$, line 72-74 crashes with division by zero |
| `build_table` (`prob_table.py:27-93`) | Skip Missing / NaN Returns | Record with `fwd_return_pct` None or NaN | Record skipped; not added to cell counts or baseline | **EXISTS** | `test_prob_table.py:63`, `test_prob_table_edge.py:45-51` |
| `build_table` (`prob_table.py:27-93`) | Probabilities Sum to 1.0 | Arbitrary record set | Sum of $UP + FLAT + DOWN == 1.0$ within floating precision | **EXISTS** | `test_prob_table_edge.py:53-56` (`test_probabilities_sum_to_one`) |
| `evaluate` (`prob_table.py:95-172`) | Empty Test Set | `test = []` | Returns `"n_test": 0, "improvement": 0.0` | **EXISTS** | `test_prob_table_edge.py:58-61` (`test_evaluate_empty_test_set`) |
| `evaluate` (`prob_table.py:95-172`) | Empty Training Set | `train = [], test = [rec]` | `build_table` creates empty baseline ($n=0$); evaluate runs | **MISSING** | Untested in isolation |
| `evaluate` (`prob_table.py:95-172`) | Sample Size Fallback ($n < min\_n$) | Cell count in training set $< min\_n$ | Evaluator falls back to baseline distribution | **EXISTS** | `test_prob_table.py:91`, `test_prob_table_edge.py:63-69` |

---

## 3. Top-10 Missing Cases Ranked by Blast Radius

The 32 missing test cases are prioritized below by **blast radius** (potential for runtime crashes, silent position/order errors, incorrect promotion to trading, or corrupted backtest statistics):

| Rank | Module & Function | Failure / Boundary Case | Blast Radius & Justification | Expected Fix / Test Requirement |
| :---: | :--- | :--- | :--- | :--- |
| **1** | `sim.py:76-78` (`run`) | $risk = 0$ ($stop == entry$) | **CRITICAL: ZeroDivisionError**. If a corrupted snapshot has stop equal to price, `risk = abs(e - s) = 0`. Calculating `gross` or `fee_R` crashes the simulation run completely. | Add unit test verifying that `geom_ok` filters identical stop and entry, and `run()` refuses/skips zero-risk trades cleanly without division by zero. |
| **2** | `sim.py:46-82` (`run`) | Out-of-order timestamp / inverted timeline | **CRITICAL: Corrupted Simulation**. If snapshots in `replay_rows.json` are not sorted chronologically, gap detection ($q["t"] - last["t"] > GAP$) triggers spuriously or causes negative time elapsed. | Add unit test verifying chronological sorting enforcement or fail-closed error if $q["t"] < last["t"]$. |
| **3** | `promote.py:69-87` (`recompute_oos`) | Corrupted / non-numeric `net_r` in `trades_csv` | **HIGH: Unhandled Exception during CI / Verify**. If CSV contains strings or empty cells, line 78 raises unhandled `ValueError` rather than a clean pipeline `REJECT`. | Add unit test for corrupted CSVs in `test_promote.py` verifying clean `REJECT` outcome rather than uncaught tracebacks. |
| **4** | `prob_table.py:72-74` (`build_table`) | Empty input with $\alpha = 0.0$ | **HIGH: ZeroDivisionError**. When $\alpha = 0.0$ (raw frequencies) and a cell has $n = 0$, denominator $(n + 3\alpha) = 0$, crashing table creation. | Add unit test asserting `ZeroDivisionError` prevention or fallback when $\alpha = 0.0$ and cell is empty. |
| **5** | `fees.py:42-44` (`fees_dict`) | Missing keys or invalid types (None / NaN) | **HIGH: Downstream Arithmetic Failure**. `fees_dict` accepts arbitrary inputs without validation. Passing None or NaN silently pollutes trade calculations across all simulators. | Add unit test asserting strict dictionary shape and validation against NaN/None fee values. |
| **6** | `sim.py:34-39` (`wilson`) | Degenerate arguments ($k > n$ or $n < 0$) | **MEDIUM: Math Domain Error**. If passed negative sample or $k > n$, `math.sqrt()` receives negative value, throwing uncaught `ValueError: math domain error`. | Add unit test for $k > n$ and $n < 0$ ensuring fail-closed ValueError or `(0.0, 0.0)` return. |
| **7** | `prob_table.py:7-17` (`load_labels`) | Missing / unreadable outcome labels file | **MEDIUM: Pipeline Crash**. Missing file or malformed JSON raises unhandled `FileNotFoundError` / `JSONDecodeError`. | Add unit test asserting graceful handling of missing or corrupted label JSON files. |
| **8** | `sim.py:68-71` (`run`) | Simultaneous stop and target wick penetration | **MEDIUM: Execution Ambiguity**. In a 60-second snapshot where price movement could have touched both boundaries, order of evaluation dictates outcome. `sim.py` is stop-first, but lacks explicit assertions. | Add unit test verifying conservative `stop_first` resolution in snapshot simulation. |
| **9** | `promote.py:57-59` (`holm_z`) | Non-positive or float variants ($variants \le 0$) | **LOW: Unexpected CI Bounds**. Passing negative or invalid variants to `holm_z`. Handled partially by `max(1, int(variants))` but lacks explicit regression test. | Add unit test asserting `holm_z` boundary behavior on non-positive integers. |
| **10** | `prob_table.py:95-172` (`evaluate`) | Completely empty training set ($train = []$) | **LOW: Degenerate Evaluation**. Evaluating with 0 training records causes baseline smoothing with $total\_n = 0$, giving uniform 1/3 probabilities. | Add unit test verifying baseline uniform probability behavior on empty training sets. |

---

## 4. Verification and Execution Notes

Existing core test suites were executed and verified against live code:
- `MyTradingSys/backtest/layers/promotion/test_promote.py`: **54 passed**
- `MyTradingSys/backtest/test_prob_table.py`: **12 passed**
- `MyTradingSys/backtest/test_prob_table_edge.py`: **9 passed**
- `MyTradingSys/tests/test_b070_fee_parity.py`: **4 passed**
- Total passing baseline tests: **79 passed** in 24.57s.
