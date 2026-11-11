Counts: MATCH: 8, DIFF: 0, NOT_IN_DATA: 0

# Gemini Blind Read of `scripts/dev/run_extra_tests.py` Against Its Docstring

- **Card ID**: `gemini-blind-read-run-extra-tests-docstring-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Scope In**:
  - `scripts/dev/run_extra_tests.py` (read)
  - `scripts/dev/test_run_extra_tests.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-run-extra-tests-docstring-1111.md` (new)
- **Scope Out**: no edit to source files; no live-tree edit, no deploy, no `.secrets` or `.env` read; read-only audit

## Target Docstring

From `scripts/dev/run_extra_tests.py:2-8`:
```python
"""run_extra_tests.py - run the tracked test files that live outside the dirs the main gate collects (B150).

Each slow file (SLOW_FIRST) runs in its own pytest process; the fast files of a directory share one (run_group; a red group is re-run per file). Each process runs with the file's directory as cwd (the way each was written to run), so same-named
helper modules in different dirs cannot collide. Files run MTS_GATE_JOBS at a time (default min(4, cpu count); 1 = one after
the other), each with its own --basetemp, and print their line when they finish. Exit 1 if any file fails. The list is checked by
MyTradingSys/tests/test_gate_discovery_b150.py: a new tracked test file must be gated, listed here, or skipped with a reason.
"""
```

## Verification Table (8 Clauses)

| Clause # | Docstring Statement | File:Line | Code Implementation Reference | Test Verification Reference | Status |
|---|---|---|---|---|---|
| 1 | Run tracked test files outside main gate dirs (B150) | `scripts/dev/run_extra_tests.py:2` | SOURCED `scripts/dev/run_extra_tests.py:23-28` (`load_extra`), `scripts/dev/run_extra_tests.py:32-41` (`discovered`), `scripts/dev/run_extra_tests.py:43-44` (`all_tests`) | SOURCED `scripts/dev/test_run_extra_tests.py:30-36` (`test_extra_is_loaded_from_the_tsv_data_file`), `scripts/dev/test_run_extra_tests.py:38-50` (`test_study_folder_tests_are_discovered_without_an_entry`) | MATCH |
| 2 | Slow files (SLOW_FIRST) run in their own pytest process | `scripts/dev/run_extra_tests.py:4` | SOURCED `scripts/dev/run_extra_tests.py:63-70` (`SLOW_FIRST`), `scripts/dev/run_extra_tests.py:139-141` (`if rel in SLOW_FIRST or shares_state(rel): units.append(("one", rel))`) | SOURCED `scripts/dev/test_run_extra_tests.py:103-109` (`test_slowest_first_keeps_every_file_once_and_leads_with_the_slow_ones`), `scripts/dev/test_run_extra_tests.py:111-113` (`test_every_slow_first_file_is_a_registered_extra_test`), `scripts/dev/test_run_extra_tests.py:127-138` (`test_plan_units_groups_fast_files_per_dir_and_keeps_slow_ones_single`) | MATCH |
| 3 | Fast files of a directory share one process (run_group; red group re-run per file) | `scripts/dev/run_extra_tests.py:4` | SOURCED `scripts/dev/run_extra_tests.py:142-148` (`plan_units` grouping by dir up to `group_max`), `scripts/dev/run_extra_tests.py:154-171` (`run_group` falls back to `run_one` on red / undecidable) | SOURCED `scripts/dev/test_run_extra_tests.py:140-149` (`test_run_group_green_files_run_in_one_process`), `scripts/dev/test_run_extra_tests.py:151-157` (`test_run_group_reports_the_failing_file_by_name_and_keeps_the_others_green`), `scripts/dev/test_run_extra_tests.py:159-165` (`test_run_group_a_file_with_no_tests_fails_like_alone`), `scripts/dev/test_run_extra_tests.py:167-173` (`test_run_group_timeout_falls_back_to_per_file_with_the_same_ceiling`) | MATCH |
| 4 | Each process runs with the file's directory as cwd | `scripts/dev/run_extra_tests.py:4-5` | SOURCED `scripts/dev/run_extra_tests.py:100` (`cwd=p.parent` in `run_one`), SOURCED `scripts/dev/run_extra_tests.py:163` (`cwd=paths[0].parent` in `run_group`) | SOURCED `scripts/dev/test_run_extra_tests.py:71-83` (`test_child_env_lets_a_test_in_a_subfolder_import_a_repo_root_package`) | MATCH |
| 5 | Files run MTS_GATE_JOBS at a time (default min(4, cpu count) or capped formula) | `scripts/dev/run_extra_tests.py:5-6` | SOURCED `scripts/dev/run_extra_tests.py:47` (`JOBS_MAX = 8`), `scripts/dev/run_extra_tests.py:50-58` (`jobs(cpu)` reads `os.environ.get("MTS_GATE_JOBS")`, fallback `min(JOBS_MAX, max(min(4, cpu), cpu // 2))`), `scripts/dev/run_extra_tests.py:202-203` (`ThreadPoolExecutor(max_workers=max(1, n_jobs))`) | SOURCED `scripts/dev/test_run_extra_tests.py:115-120` (`test_default_jobs_never_below_the_old_four_and_capped`) | MATCH |
| 6 | Each process runs with its own --basetemp | `scripts/dev/run_extra_tests.py:6` | SOURCED `scripts/dev/run_extra_tests.py:99` (`f"--basetemp={basetemp}"` in `run_one`), SOURCED `scripts/dev/run_extra_tests.py:162` (`f"--basetemp={basetemp}"` in `run_group`), SOURCED `scripts/dev/run_extra_tests.py:177-180,193,195,199` | SOURCED `scripts/dev/test_run_extra_tests.py:81,98,147,171` (all pass dedicated `tmp_path / "bt"` basetemp) | MATCH |
| 7 | Print their line when they finish | `scripts/dev/run_extra_tests.py:6` | SOURCED `scripts/dev/run_extra_tests.py:184-187` (`def report(rel, ok, tail): with lock: print(f"{'ok  ' if ok else 'FAIL'} {rel}: {tail}", flush=True)`) | SOURCED `scripts/dev/run_extra_tests.py:184-187` (flushed real-time stdout per file under lock) | MATCH |
| 8 | Exit 1 if any file fails (and checked by B150 gate discovery) | `scripts/dev/run_extra_tests.py:6-7` | SOURCED `scripts/dev/run_extra_tests.py:204` (`return [f"{rel}: missing" ... if not done[rel][0]]`), SOURCED `scripts/dev/run_extra_tests.py:231-233` (`print(... "FAIL " + ", ".join(bad) if bad else "PASS"); return 1 if bad else 0`) | SOURCED `scripts/dev/test_run_extra_tests.py:151-157` (`test_run_group_reports_the_failing_file_by_name_and_keeps_the_others_green`), `scripts/dev/test_run_extra_tests.py:159-165` (`test_run_group_a_file_with_no_tests_fails_like_alone`) | MATCH |

## Detailed Clause Breakdown

### 1. Tracked Test Files Outside Main Gate Dirs (B150)
- **Docstring Statement**: SOURCED `scripts/dev/run_extra_tests.py:2`
  > `"run_extra_tests.py - run the tracked test files that live outside the dirs the main gate collects (B150)."`
- **Implementation**: SOURCED `scripts/dev/run_extra_tests.py:23-28` reads `extra_tests.tsv` via `load_extra()`. SOURCED `scripts/dev/run_extra_tests.py:32-41` discovers untracked test files under `MyTradingSys/research/` via git `ls-files` excluding those in `run_all_tests.py`. SOURCED `scripts/dev/run_extra_tests.py:43-44` combines them: `all_tests() = EXTRA + discovered()`.
- **Test Reference**: SOURCED `scripts/dev/test_run_extra_tests.py:30-36` validates `test_extra_is_loaded_from_the_tsv_data_file`. SOURCED `scripts/dev/test_run_extra_tests.py:38-50` validates `test_study_folder_tests_are_discovered_without_an_entry`.
- **Verdict**: MATCH.

### 2. Slow Files (SLOW_FIRST) Run in Their Own Pytest Process
- **Docstring Statement**: SOURCED `scripts/dev/run_extra_tests.py:4`
  > `"Each slow file (SLOW_FIRST) runs in its own pytest process;"`
- **Implementation**: SOURCED `scripts/dev/run_extra_tests.py:63-70` defines table `SLOW_FIRST`. SOURCED `scripts/dev/run_extra_tests.py:139-141` in `plan_units()` separates any file where `rel in SLOW_FIRST or shares_state(rel)` directly into `units.append(("one", rel))`. SOURCED `scripts/dev/run_extra_tests.py:199` runs each `"one"` unit with `one(unit[1], tmp / str(i))`.
- **Test Reference**: SOURCED `scripts/dev/test_run_extra_tests.py:103-109` verifies `test_slowest_first_keeps_every_file_once_and_leads_with_the_slow_ones`. SOURCED `scripts/dev/test_run_extra_tests.py:111-113` verifies `test_every_slow_first_file_is_a_registered_extra_test`. SOURCED `scripts/dev/test_run_extra_tests.py:127-138` asserts `units[0] == ("one", slow)` in `test_plan_units_groups_fast_files_per_dir_and_keeps_slow_ones_single`.
- **Verdict**: MATCH.

### 3. Fast Files of a Directory Share One Process (run_group; Red Group Re-run Per File)
- **Docstring Statement**: SOURCED `scripts/dev/run_extra_tests.py:4`
  > `"the fast files of a directory share one (run_group; a red group is re-run per file)."`
- **Implementation**: SOURCED `scripts/dev/run_extra_tests.py:142-148` gathers files by directory into chunks up to `group_max` (`GROUP_MAX = 12`). In `scripts/dev/run_extra_tests.py:154-171`, `run_group()` runs all files of a directory in one invocation; if return code is non-zero, stdout empty, test results missing from `-rA`, or if a timeout expires, it re-runs each file individually via `run_one()`. SOURCED `scripts/dev/run_extra_tests.py:192-195` catches unexpected exceptions from `many(unit[2], ...)` and falls back closed to `one()`.
- **Test Reference**: SOURCED `scripts/dev/test_run_extra_tests.py:140-149` (`test_run_group_green_files_run_in_one_process`), SOURCED `scripts/dev/test_run_extra_tests.py:151-157` (`test_run_group_reports_the_failing_file_by_name_and_keeps_the_others_green`), SOURCED `scripts/dev/test_run_extra_tests.py:159-165` (`test_run_group_a_file_with_no_tests_fails_like_alone`), SOURCED `scripts/dev/test_run_extra_tests.py:167-173` (`test_run_group_timeout_falls_back_to_per_file_with_the_same_ceiling`), and SOURCED `scripts/dev/test_run_extra_tests.py:175-182` (`test_a_crashing_group_runner_falls_back_to_the_per_file_run`).
- **Verdict**: MATCH.

### 4. Process Working Directory (cwd) Set to File's Directory
- **Docstring Statement**: SOURCED `scripts/dev/run_extra_tests.py:4-5`
  > `"Each process runs with the file's directory as cwd (the way each was written to run), so same-named helper modules in different dirs cannot collide."`
- **Implementation**: SOURCED `scripts/dev/run_extra_tests.py:100` executes `subprocess.run(..., cwd=p.parent)` in `run_one()`. SOURCED `scripts/dev/run_extra_tests.py:163` executes `subprocess.run(..., cwd=paths[0].parent)` in `run_group()`. SOURCED `scripts/dev/run_extra_tests.py:78-83` (`child_env()`) appends the repo root to `PYTHONPATH` so top-level imports remain functional while cwd is the subfolder.
- **Test Reference**: SOURCED `scripts/dev/test_run_extra_tests.py:71-83` (`test_child_env_lets_a_test_in_a_subfolder_import_a_repo_root_package`) verifies execution from subfolder cwd importing both local files and repo root.
- **Verdict**: MATCH.

### 5. Concurrent Execution (MTS_GATE_JOBS, Default / Capping Formula)
- **Docstring Statement**: SOURCED `scripts/dev/run_extra_tests.py:5-6`
  > `"Files run MTS_GATE_JOBS at a time (default min(4, cpu count); 1 = one after the other),"`
- **Implementation**: SOURCED `scripts/dev/run_extra_tests.py:47,50-58` sets `JOBS_MAX = 8` and checks `os.environ.get("MTS_GATE_JOBS")`. When unset, it computes `min(JOBS_MAX, max(min(4, cpu), cpu // 2))`, preserving the old `min(4, cpu)` baseline on 4-8 CPU hosts and scaling up to 8 on larger machines. SOURCED `scripts/dev/run_extra_tests.py:202-203` enforces worker concurrency using `ThreadPoolExecutor(max_workers=max(1, n_jobs))`.
- **Test Reference**: SOURCED `scripts/dev/test_run_extra_tests.py:115-120` (`test_default_jobs_never_below_the_old_four_and_capped`) tests `rx.jobs(c)` across 1, 2, 4, 8, 12, 32 CPUs and explicit `MTS_GATE_JOBS` override.
- **Verdict**: MATCH.

### 6. Dedicated Isolated --basetemp Per Process / File
- **Docstring Statement**: SOURCED `scripts/dev/run_extra_tests.py:6`
  > `"each with its own --basetemp,"`
- **Implementation**: SOURCED `scripts/dev/run_extra_tests.py:99` passes `f"--basetemp={basetemp}"` to pytest in `run_one()`. SOURCED `scripts/dev/run_extra_tests.py:162` passes `f"--basetemp={basetemp}"` in `run_group()`. SOURCED `scripts/dev/run_extra_tests.py:180,193,195,199,226` creates dedicated subpaths per task unit `tmp / str(i)` and `tmp / f"{i}_{j}"`.
- **Test Reference**: SOURCED `scripts/dev/test_run_extra_tests.py:81,98,147,171` invokes `run_one` and `run_group` with isolated temporary directory basetemp paths.
- **Verdict**: MATCH.

### 7. Output Result Line on Completion
- **Docstring Statement**: SOURCED `scripts/dev/run_extra_tests.py:6`
  > `"and print their line when they finish."`
- **Implementation**: SOURCED `scripts/dev/run_extra_tests.py:184-187,196-199` calls `report(rel, ok, tail)` inside `ThreadPoolExecutor.map(work, ...)` with a thread lock: `print(f"{'ok  ' if ok else 'FAIL'} {rel}: {tail}", flush=True)`. Each file's summary line is printed as soon as its execution completes.
- **Test Reference**: Verified directly via implementation in `scripts/dev/run_extra_tests.py:184-187`.
- **Verdict**: MATCH.

### 8. Exit Code 1 on Failure and Test Registration Discipline
- **Docstring Statement**: SOURCED `scripts/dev/run_extra_tests.py:6-7`
  > `"Exit 1 if any file fails. The list is checked by MyTradingSys/tests/test_gate_discovery_b150.py: a new tracked test file must be gated, listed here, or skipped with a reason."`
- **Implementation**: SOURCED `scripts/dev/run_extra_tests.py:204` returns bad files list `bad`. SOURCED `scripts/dev/run_extra_tests.py:231-233` in `main()` prints `FAIL` or `PASS` and returns `1 if bad else 0`.
- **Test Reference**: SOURCED `scripts/dev/test_run_extra_tests.py:151-157` (`test_run_group_reports_the_failing_file_by_name_and_keeps_the_others_green`) and SOURCED `scripts/dev/test_run_extra_tests.py:159-165` (`test_run_group_a_file_with_no_tests_fails_like_alone`).
- **Verdict**: MATCH.
