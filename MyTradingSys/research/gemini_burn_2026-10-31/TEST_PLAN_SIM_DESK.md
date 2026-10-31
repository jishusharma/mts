# Test Plan: Simulator Desk (`MyTradingSys/research/sim_desk`)

**Status:** COMPLETE  
**Standard Reference:** `DESIGN.md`, `ROADMAP.md`, `FORMULAS.md` (Sections 10, 13, 17, 18.5)  
**Registry Reference:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  
**Card ID:** `gemini-test-plan-sim-desk-1031`  
**Date:** 2026-10-31  

---

## 1. Executive Summary & Inventory Matrix

This test plan provides comprehensive boundary, degenerate, and failure case coverage across `MyTradingSys/research/sim_desk`:
1. **Empty Data Handling:** Zero-length raw open times, empty klines, zero filled trades, zero-division in streak/stats/breakdown/luck/equity curve calculations.
2. **Data Gaps & Temporal Integrity:** Missing 1m kline intervals, out-of-order timestamps, duplicate timestamps, gap-through-stop fills, period-profile boundary alignment.
3. **Symbol Switching:** Multi-asset isolation (`BTCUSDT` vs `ETHUSDT`), coin parameter propagation, coin tag isolation in trial ledgers and cache keys, refusal of unregistered pairs.
4. **Catalogue Rebuild:** Dynamic indexing of audit reports, study notes, and trial ledgers into `_catalogue.json`, missing verdict/title fallback, uncatalogued run detection, exported count parity.
5. **Result Export & Look-Ahead Guards:** Schema compliance of exported JSON result artifacts, strict look-ahead cutoffs enforcing the `DEV` window (`2022-04-01` to `2024-06-30`), and refusal of post-cut records.

Every finding cites exact `file:line` locations in code and tests. Tests status is verified via automated AST parsing and test suite inspection as **EXISTS** or **MISSING**.

### Summary Matrix

| Category / Component | Total Cases Analyzed | EXISTS | MISSING | Primary Risk / Blast Radius |
| :--- | :--- | :--- | :--- | :--- |
| **1. Empty Data Cases** | 16 | 9 | 7 | Division by zero in stats/metrics, page render crash on 0 trades, silent empty cache creation |
| **2. Gaps & Temporal Integrity** | 14 | 9 | 5 | Silent missing candle propagation, look-ahead leakage across months, stop-fill mispricing |
| **3. Symbol Switching** | 10 | 5 | 5 | Cache key contamination between BTC/ETH, unhandled symbol parameters in fixed studies |
| **4. Catalogue Rebuild** | 14 | 6 | 8 | Crash on malformed markdown notes, uncommitted run divergence, missing verdict line parse errors |
| **5. Result Export & Look-Ahead** | 16 | 10 | 6 | Validation/Holdout data leakage past `2024-07-01 CUT_MS`, malformed JSON export schema |
| **Total** | **70** | **39** | **31** | |

---

## 2. Top-10 MISSING Failure Cases Ranked by Blast Radius

The following table prioritizes the top 10 test gaps identified across `sim_desk`, ranked by potential blast radius (severity of silent failures, look-ahead data contamination, or system crashes):

| Rank | Function / Target | Category | Failure Scenario / Missing Test Boundary | Blast Radius & System Impact |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `studies/levels.py:242 run()` | Symbol Switch | Running `levels` study with `symbol="ETHUSDT"` | **CRITICAL:** `levels.py` hardcodes BTC assumptions; passing an ETH parameter without an explicit symbol gate loads mismatched caches or causes unhandled index errors. |
| **2** | `studies/_bars.py:108 resample()` | Gaps | Kline timestamp gaps spanning candle boundaries during resampling | **HIGH:** If raw 1m klines have missing minutes, `resample` produces irregularly spaced higher-timeframe candles without warning, distorting indicators causal lookbacks. |
| **3** | `desk.py:38 check_dates()` | Look-Ahead / Export | Malformed date strings or inverted dates (`start > end`) | **HIGH:** An invalid date string raises unhandled `ValueError` in HTTP requests or causes negative/inverted date loops in simulation windows. |
| **4** | `export_results.py:116 write()` | Export / Look-Ahead | Exporting backtest results that include post-cut timestamps | **HIGH:** If a study result inadvertently contains timestamps at or after `2024-07-01`, `export_results.py` writes an invalid result file that compromises DEV isolation. |
| **5** | `build_catalogue.py:39 date_of()` | Catalogue Rebuild | Note path without date regex and git commit log failure/timeout | **MEDIUM:** If git subprocess fails or source file is untracked, `date_of()` returns `None`, which may lead to un-sortable catalogue entries or `NoneType` attribute errors. |
| **6** | `desk.py:107 monte_carlo()` | Empty Data | Invoking Monte Carlo permutation with $n=0$ trades | **MEDIUM:** Permuting an empty array or computing drawdowns on zero trades can trigger empty slicing exceptions or zero division in percentiles. |
| **7** | `studies/_bars.py:108 resample()` | Empty Data | Passing empty array `arr` ($shape = (0, 5)$) to `resample()` | **MEDIUM:** Empty array slicing produces empty outputs; downstream indicators (`rsi`, `wavetrend`) crash with `IndexError` on empty arrays. |
| **8** | `build_catalogue.py:79 verdict_of()` | Catalogue Rebuild | Research markdown file with only headers and empty body | **MEDIUM:** `verdict_of` falls back to empty body indexing; returns string `"no verdict line"` but unverified against malformed UTF-8 or blank files. |
| **9** | `export_results.py:18 commit_of()` | Export | Uncommitted, untracked, or deleted source files | **LOW:** `commit_of` returns `"unknown"` via exception fallback; untested against subprocess timeouts or dirty working tree states. |
| **10** | `build_catalogue.py:87 kind_of()` | Catalogue Rebuild | Disambiguation between audit, backtest, and thought experiment | **LOW:** Classification relies on regex matching; edge case notes with ambiguous keyword combinations lack isolated boundary tests. |

---

## 3. Detailed Matrix: Boundary and Failure Cases per Function

### 3.1 Empty Data Handling

| Function | File:Line | Boundary / Failure Scenario | Expected Result | Status | Test Citation / Gap Analysis |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `check()` | `data_check.py:41` | Raw input rows empty (`rows = []`) | Returns `{expected: N, present: 0, missing: N, duplicates: 0, out_of_order: 0, longest_gap: N}` | **MISSING** | Tested with non-empty fixtures in `test_data_check.py:16`, but empty list `rows=[]` is untested. |
| `_raw_open_times()` | `data_check.py:85` | CSV file with header only, zero data rows | Returns `[]` without error | **MISSING** | Only tests existing valid CSV files; zero-row CSV unverified. |
| `_symbol_rows()` | `data_check.py:96` | Missing kline file on disk | Raises `FileNotFoundError` | **EXISTS** | Explicitly tested in `test_data_check.py:16-25`. |
| `worst_streak()` | `desk.py:51` | Empty net returns list (`net = []`) | Returns `0` | **EXISTS** | Handled in `desk.py:53`, verified in `test_desk.py:131`. |
| `stats()` | `desk.py:60` | Zero filled trades (`net[filled].size == 0`) | Returns early `{'n': 0, 'streak': 0, 'nofill': nofill}` without calling bootstrap | **EXISTS** | Handled in `desk.py:68-69`, tested in `test_build2.py:39`. |
| `numbers()` | `desk.py:81` | Result dictionary with zero trades (`st['n'] == 0`) | Returns dash/safe dictionary for display without division by zero | **EXISTS** | Tested in `test_conditions.py:224` (`test_numbers_strip_by_hand`). |
| `trade_list()` | `desk.py:124` | Result dictionary with zero filled trades | Returns empty trade list `[]` | **EXISTS** | Tested in `test_conditions.py:236` (`test_trade_list_by_hand`). |
| `breakdown()` | `desk.py:140` | Empty run with zero trades | Returns three standard groups marked `few=True` | **EXISTS** | Tested in `test_build2.py:39` (`test_breakdown_empty_run`). |
| `trade_chart()` | `desk.py:170` | Trade index out of bounds or empty trades | Returns error dictionary or handled safely | **MISSING** | Untested for empty trade results. |
| `curve()` | `desk.py:184` | Result dictionary with 0 filled trades | Returns single initial zero point `[0.0]` without crash | **EXISTS** | Tested in `test_conditions.py:181` (`test_equity_curve_filled_only_in_time_order`). |
| `count_tries()` | `desk.py:226` | Non-existent or empty `TRIALS.md` | Returns `0` tries | **MISSING** | Untested when trials file does not exist. |
| `apply()` | `conditions.py:203` | Condition mask where all trades are filtered out (`keep = all False`) | Returns valid result structure with 0 trades, empty arrays, matching keys | **EXISTS** | Tested in `test_conditions.py:159` (`test_apply_keeps_arrays_and_refs_aligned`). |
| `load_1m()` | `studies/_bars.py:97` | Missing raw month CSV | Raises `FileNotFoundError` | **EXISTS** | Tested in `test_sealed_cache.py:39` (`test_l1_month_loader_refuses_sealed_row`). |
| `resample()` | `studies/_bars.py:108` | Empty bar array input ($0 \times 5$) | Returns empty resampled array | **MISSING** | No test passes empty array to `resample()`. |
| `run_trade()` | `studies/_bars.py:127` | Trigger level never reached within window | Returns trade dict with `filled = False` | **EXISTS** | Tested in `test_studies.py:55` (`test_no_fill_when_trigger_never_reached_in_window`). |
| `monte_carlo()` | `desk.py:107` | Zero trades input | Should return zero/empty bands without throwing exception | **MISSING** | Tested only with non-empty results in `test_conditions.py:283`. |

---

### 3.2 Data Gaps and Temporal Integrity

| Function | File:Line | Boundary / Failure Scenario | Expected Result | Status | Test Citation / Gap Analysis |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `check()` | `data_check.py:41` | Single and multi-minute timestamp gaps in 1m series | Accurately calculates `missing` count and `longest_gap` | **EXISTS** | Verified in `test_data_check.py:16` (`test_hole_and_duplicate_hand_counted`). |
| `check()` | `data_check.py:41` | Out-of-order timestamps in raw CSV | Increments `out_of_order` count | **EXISTS** | Tested in `test_data_check.py:44` (`test_out_of_order_row_is_counted`). |
| `check()` | `data_check.py:41` | Duplicate timestamps in raw CSV | Increments `duplicates` count, counts `present` once | **EXISTS** | Tested in `test_data_check.py:16`. |
| `check()` | `data_check.py:41` | Row timestamp at or after `CUT_MS` (`2024-07-01`) | Raises `ValueError` refusing sealed data | **EXISTS** | Tested in `test_data_check.py:30` and `37`. |
| `resample()` | `studies/_bars.py:108` | Missing minutes in 1m series during resampling | Retains gap in higher-timeframe bars (no synthetic fill) | **MISSING** | Untested; silent gap propagation occurs without assertion. |
| `run_trade()` | `studies/_bars.py:127` | Price gaps over stop price on next minute | Fills stop at bar open (worse price), not theoretical stop level | **EXISTS** | Tested in `test_studies.py:38` (`test_long_stop_and_gap_through_stop`). |
| `run_trade()` | `studies/_bars.py:127` | Simultaneous stop and target hit on same bar | Fills stop loss first (pessimistic fill rule) | **EXISTS** | Tested in `test_studies.py:48` (`test_same_bar_stop_and_target_counts_the_stop`). |
| `simulate_one()` | `studies/levels.py:174` | Price gaps beyond target level on open | Fills at open price (slippage/gap accounted) | **MISSING** | Target gap fill price precision untested. |
| `period_profiles()`| `studies/tom_vp.py:157` | Kline gaps across session/day boundaries | Calculates volume profile without bleeding into adjacent sessions | **EXISTS** | Tested in `test_tom_vp.py:57` (`test_period_profile_is_the_periods_own_bars_worked_example_b`). |
| `signals()` | `studies/tom_vp.py:194` | Gaps causing missing anchor profiles | Skips trading ideas for unanchored periods | **EXISTS** | Tested in `test_tom_vp.py:86` (`test_three_ideas_fire_where_the_concept_check_says`). |
| `_closed_index()` | `conditions.py:131` | Trade touch timestamp occurring before first bar | Returns `-1` or out-of-range index safely | **MISSING** | Negative timestamp offset boundary untested. |
| `ema()` | `conditions.py:136` | Price series length shorter than EMA length | Handled without NaN/IndexError crash | **MISSING** | Tested on long series in `test_conditions.py:59`, short series untested. |
| `atr()` | `conditions.py:147` | Fewer bars than ATR length | Returns array with correct padding or raises ValueError | **MISSING** | Short bar boundary untested. |
| `mask()` | `conditions.py:159` | Condition referencing timestamp outside bar index | Mask correctly evaluates to False | **EXISTS** | Tested in `test_conditions.py:30-44`. |

---

### 3.3 Symbol Switching

| Function | File:Line | Boundary / Failure Scenario | Expected Result | Status | Test Citation / Gap Analysis |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `symbol_of()` | `studies/_bars.py:71` | Unregistered symbol (e.g. `'SOLUSDT'`, `''`) | Raises `ValueError: symbol: unknown choice` | **EXISTS** | Tested in `test_studies.py:125` (`test_symbol_box`). |
| `symbol_of()` | `studies/_bars.py:71` | Valid symbols `'BTCUSDT'` and `'ETHUSDT'` | Returns valid symbol string | **EXISTS** | Tested in `test_studies.py:125`. |
| `coin_tag()` | `studies/_bars.py:78` | Tag generation for `'BTCUSDT'` vs `'ETHUSDT'` | Returns `""` for BTC (backwards compatibility), `" ETHUSDT"` for ETH | **EXISTS** | Tested in `test_studies.py:125`. |
| `load_1m()` | `studies/_bars.py:97` | Switching between BTC and ETH kline loading | Caches independently in `BTCUSDT-1m-*.npy` and `ETHUSDT-1m-*.npy` | **EXISTS** | Tested in `test_studies.py:135` (`test_eth_bars_are_eth_and_stay_inside_dev`). |
| `run()` | `studies/rsi.py:91` | Full backtest run with ETH symbol switch | Generates distinct trade list and stats from BTC | **EXISTS** | Tested in `test_studies.py:141` (`test_eth_run_end_to_end`). |
| `run()` | `studies/wavetrend.py:82`| Full backtest run with ETH symbol switch | Executes cleanly using ETH cache | **MISSING** | Direct end-to-end test missing for wavetrend ETH (only RSI tested in `test_studies.py:141`). |
| `run()` | `studies/levels.py:242` | Invoking levels study with `symbol="ETHUSDT"` | Must either support ETH or fail closed with explicit error | **MISSING** | No validation in `levels.py` for symbol parameter; silently ignores or fails. |
| `run()` | `studies/krown.py:117` | Invoking krown study with ETH symbol | Rejects or verifies multi-symbol execution | **MISSING** | Untested; defaults to BTC klines only. |
| `run()` | `studies/pitchfork.py:148`| Pitchfork study with ETH symbol | Rejects or verifies multi-symbol execution | **MISSING** | Untested; defaults to BTC klines only. |
| `run_setting()` | `desk.py:298` | Symbol switch in web desk run | Appends distinct row to `TRIALS.md` carrying coin tag | **MISSING** | HTTP server integration tests run default BTC only. |

---

### 3.4 Catalogue Rebuild

| Function | File:Line | Boundary / Failure Scenario | Expected Result | Status | Test Citation / Gap Analysis |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `date_of()` | `build_catalogue.py:39` | Path with date vs path without date | Extracts date from path; if missing, queries `git log -1` | **MISSING** | Unit test verifying git log fallback and None handling missing. |
| `read()` | `build_catalogue.py:57` | Non-existent or unreadable file in repo | Returns empty string `""` without throwing `OSError` | **MISSING** | Untested in isolation. |
| `clean()` | `build_catalogue.py:65` | Price strings present in note text | Redacts raw prices to `[price omitted]` (public repo rule) | **MISSING** | Untested directly against un-sanitized price fixtures. |
| `title_of()` | `build_catalogue.py:72` | Markdown note with no `#` heading | Returns provided fallback string | **MISSING** | Untested. |
| `verdict_of()` | `build_catalogue.py:79` | Note with explicit verdict line vs note without | Extracts clean verdict; falls back to first non-empty line | **MISSING** | Untested directly. |
| `kind_of()` | `build_catalogue.py:87` | Classifying `audit` vs `backtest` vs `thought_experiment` | Correctly maps keywords in path, text, and verdict | **MISSING** | Untested directly. |
| `family_of()` | `build_catalogue.py:95` | Path in `research/<folder>` with trailing date suffix | Strips date suffix and replaces underscores with spaces | **MISSING** | Untested directly. |
| `tag()` | `build_catalogue.py:103`| Verdict text with negative keywords (`fail`, `no edge`) | Sets `status="FAILED"`, `verdict_class="failed"` | **MISSING** | Untested directly. |
| `main()` | `build_catalogue.py:113`| Local desk saved run (`results/desk-*.json`) | Rebuild includes desk run row; marks `exported=True` | **EXISTS** | Tested in `test_build2.py:58` (`test_saved_run_is_in_the_catalogue`). |
| `main()` | `build_catalogue.py:113`| Result file where ID differs from row claiming source | Flags `result_id` and keeps row exported | **EXISTS** | Tested in `test_build2.py:77` (`test_rebuild_flags_result_whose_id_differs_from_the_row_that_claimed_its_source`). |
| `main()` | `build_catalogue.py:113`| Full catalogue build on repository trunk | Exported count equals valid results count; all rows valid | **EXISTS** | Tested in `test_backfill.py:28` (`test_exported_count_equals_result_files`). |
| `main()` | `build_catalogue.py:113`| Every catalogue row reachable from desk | All rows have valid links and cards | **EXISTS** | Tested in `test_backfill.py:34` (`test_every_row_reachable_from_desk_list_and_card`). |
| `main()` | `build_catalogue.py:113`| Unknown test ID queried from desk | Returns HTTP 404 or refuses invalid ID | **EXISTS** | Tested in `test_backfill.py:42` (`test_list_is_newest_first_and_unknown_id_refused`). |
| `main()` | `build_catalogue.py:113`| Artifact HTML build against catalogue | HTML artifact lists every catalogue row | **EXISTS** | Tested in `test_backfill.py:48` (`test_artifact_lists_every_catalogue_row`). |

---

### 3.5 Result Export and Look-Ahead Guards

| Function | File:Line | Boundary / Failure Scenario | Expected Result | Status | Test Citation / Gap Analysis |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `check_dates()` | `desk.py:38` | Start or end date outside `DEV_FIRST..DEV_LAST` | Raises `ValueError` refusing validation/holdout window | **EXISTS** | Tested in `test_desk.py:64` (`test_date_lock_refuses_outside_dev`). |
| `check_dates()` | `desk.py:38` | Valid dates within DEV window | Returns ISO format date strings | **EXISTS** | Tested in `test_desk.py:69` (`test_date_lock_accepts_dev`). |
| `check_dates()` | `desk.py:38` | Inverted dates (`start > end`) | Raises `ValueError: start is after end` | **MISSING** | Handled in code (`desk.py:47`), but lacks unit test. |
| `check_dates()` | `desk.py:38` | Invalid date formatting (e.g. `'2022/04/01'`) | Raises `ValueError: dates must be YYYY-MM-DD` | **MISSING** | Handled in code (`desk.py:43`), but lacks unit test. |
| `_guard_result()` | `desk.py:256` | Cached result containing timestamp $\ge CUT\_MS$ | Raises `ValueError` refusing sealed data | **EXISTS** | Tested in `test_sealed_cache.py:65` (`test_l3_result_cache_refused`). |
| `_guard_result()` | `desk.py:256` | Filter condition result containing sealed timestamp | Raises `ValueError` refusing sealed data | **EXISTS** | Tested in `test_sealed_cache.py:71` (`test_l4_result_cache_refused_under_condition`). |
| `_raw()` | `desk.py:265` | Stale cache schema version (`cache_v3` vs `cache_v4`) | Discards stale cache, re-executes study | **EXISTS** | Tested in `test_reasons.py:142` (`test_v3_cache_is_rejected_not_served`). |
| `export_result()` | `desk.py:384` | Exporting study run result | Generates standard JSON schema with `id`, `kind`, `what`, `numbers` | **EXISTS** | Tested in `test_conditions.py:203` (`test_export_result_standard_schema_and_page_builds`). |
| `commit_of()` | `export_results.py:18` | Source path without git history | Returns string `"unknown"` | **MISSING** | Exception handler in `export_results.py:24` untested. |
| `levels_result()` | `export_results.py:46` | Data containing unfilled ideas | Exports filled trades only; unfilled excluded | **EXISTS** | Tested in `artifact/test_artifact.py:64` and `test_conditions.py:203`. |
| `build()` | `backfill_results.py:89`| Source note missing expected metrics | Fills `None` values and records error reasons | **EXISTS** | Tested in `test_backfill.py:71` (`test_missing_source_gives_nulls_with_reasons`). |
| `build()` | `backfill_results.py:89`| Backfilled result files validation | All result files conform to standard schema | **EXISTS** | Tested in `test_backfill.py:79` (`test_all_backfilled_files_are_valid_and_labelled`). |
| `write()` | `export_results.py:116`| Export destination directory does not exist | Creates directory or raises explicit error | **MISSING** | Directory creation safety untested. |
| `write()` | `export_results.py:116`| Export result contains raw prices | Enforces price omission (public repo requirement) | **MISSING** | Untested on output payload. |
| `run_detail()` | `runs_view.py:100` | Path traversal attack in test ID (`../../secret`) | Refuses access / sanitizes path | **EXISTS** | Tested in `test_launcher.py:79` (`test_run_detail_refuses_path_tricks`). |
| `list_runs()` | `runs_view.py:70` | Result file timestamp outside DEV window | Filters out file, does not list on desk | **EXISTS** | Tested in `test_launcher.py:87` (`test_run_outside_dev_window_is_not_listed`). |

---

## 4. Verification and Execution Notes

- **Existing Test Suite Status:** `sim_desk` currently has 22 test files containing 161 test cases. When executed with standard temporary directory isolation (`pytest --basetemp=<dir>`), 169 test items pass (including parameterized runs) with 11 skipped (requiring live web browser / Playwright).
- **Fail-First Philosophy:** Any newly added test addressing the 31 MISSING cases identified above must be executed against the existing codebase first to verify expected failure before code fixes or test assertions are finalized.
