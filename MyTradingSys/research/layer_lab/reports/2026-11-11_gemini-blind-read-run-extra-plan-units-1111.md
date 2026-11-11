Counts: MATCH: 5, DIFF: 0, NOT_IN_DATA: 0

# Gemini Blind Read of `scripts/dev/run_extra_tests.py` (plan_units, shares_state, run_group)

- **Card ID**: `gemini-blind-read-run-extra-plan-units-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Target Files**:
  - `scripts/dev/run_extra_tests.py` (`shares_state`: lines 121-130; `plan_units`: lines 133-148; `run_group`: lines 154-171; `run_files`: lines 174-204)
  - `scripts/dev/test_run_extra_tests.py` (test coverage mapping)

## Verification Table (5 Clauses)

| Clause # | Clause Description | Implementation Quote & File:Line | Status | Covering Test in `test_run_extra_tests.py` | Analysis & Verification |
|---|---|---|---|---|---|
| 1 | Grouped per directory | `scripts/dev/run_extra_tests.py:142-147`: `by_dir.setdefault(str(Path(rel).parent), []).append(rel)` and `units.append(("group", d, chunk) if len(chunk) > 1 else ("one", chunk[0]))` | MATCH | `test_plan_units_groups_fast_files_per_dir_and_keeps_slow_ones_single` (`scripts/dev/test_run_extra_tests.py:127-138`) | Fast files sharing a parent directory are partitioned by directory and grouped into chunks of at most `group_max` (`GROUP_MAX = 12`). Single-item groups degrade cleanly to `("one", rel)`. Tested explicitly in `test_plan_units_groups_fast_files_per_dir_and_keeps_slow_ones_single`. |
| 2 | Slow stays single | `scripts/dev/run_extra_tests.py:139-141`: `for rel in slowest_first(rels): if rel in SLOW_FIRST or shares_state(rel): units.append(("one", rel))` | MATCH | `test_plan_units_groups_fast_files_per_dir_and_keeps_slow_ones_single` (`scripts/dev/test_run_extra_tests.py:127-138`) | `SLOW_FIRST` files bypass `by_dir` grouping and are directly added as `("one", rel)`. `slowest_first` ensures they lead in execution order. Verified by assertion `units[0] == ("one", slow)` in `test_plan_units_groups_fast_files_per_dir_and_keeps_slow_ones_single`. |
| 3 | Shared-state writer never grouped | `scripts/dev/run_extra_tests.py:121,124-130,140-141`: `_SHARED_STATE = re.compile(r"sys\.modules\s*\[[^\]]*\]\s*=|os\.chdir\s*\(|os\.environ\s*\[[^\]]*\]\s*=|os\.environ\.(?:update|setdefault|pop)\s*\(|os\.putenv\s*\(|os\.unsetenv\s*\(|sys\.modules\.(?:update|setdefault|pop)\s*\(")` and `if rel in SLOW_FIRST or shares_state(rel): units.append(("one", rel))` | MATCH | `test_files_writing_shared_interpreter_state_stay_single` (`scripts/dev/test_run_extra_tests.py:184-196`) | `shares_state` checks for mutations to `sys.modules`, `os.environ`, and `os.chdir`. Files matching regex return `True` and are appended as single units `("one", rel)` rather than grouped into `by_dir`. Verified by `test_files_writing_shared_interpreter_state_stay_single` checking `test_cd.py`, `test_mod.py`, and `test_env.py` stay single. |
| 4 | Unreadable = single | `scripts/dev/run_extra_tests.py:129-130`: `except OSError: return True` | MATCH | `test_files_writing_shared_interpreter_state_stay_single` (`scripts/dev/test_run_extra_tests.py:196`) | If opening/reading a test file fails with `OSError`, `shares_state` fails closed and returns `True`, preventing it from grouping and causing `plan_units` to keep it as `("one", rel)`. Covered by assertion `assert rx.shares_state("d/missing.py")` in `test_files_writing_shared_interpreter_state_stay_single`. |
| 5 | Red group re-run per file | `scripts/dev/run_extra_tests.py:166,171`: `if r.returncode == 0 and (r.stdout or "").strip() and all(p.name in seen for p in paths): ... return {rel: (True, ...)} ... return {rel: run_one(rel, Path(basetemp) / f"f{i}", timeout) for i, rel in enumerate(rels)}` | MATCH | `test_run_group_reports_the_failing_file_by_name_and_keeps_the_others_green` (`scripts/dev/test_run_extra_tests.py:151-157`) | In `run_group`, unless the merged group returns exit code 0, non-empty stdout, and all files collected reported tests, it falls back to re-running every file individually via `run_one`. Tested directly by `test_run_group_reports_the_failing_file_by_name_and_keeps_the_others_green` (as well as `test_run_group_a_file_with_no_tests_fails_like_alone` and `test_run_group_timeout_falls_back_to_per_file_with_the_same_ceiling`). |

## Detailed Clause Breakdown

### Clause 1: Grouped per directory
- **Card Goal**: "fast extra test files merge per directory into one pytest process"
- **Code Quote** (`scripts/dev/run_extra_tests.py:142-147`):
  ```python
          else:
              by_dir.setdefault(str(Path(rel).parent), []).append(rel)
      for d, files in by_dir.items():
          for i in range(0, len(files), group_max):
              chunk = files[i:i + group_max]
              units.append(("group", d, chunk) if len(chunk) > 1 else ("one", chunk[0]))
  ```
- **Test Quote** (`scripts/dev/test_run_extra_tests.py:133-136`):
  ```python
      units = rx.plan_units(rels, group_max=2)
      assert units[0] == ("one", slow)
      assert ("group", "a", ["a/test_1.py", "a/test_2.py"]) in units
      assert ("one", "a/test_4.py") in units and ("one", "b/test_3.py") in units
  ```
- **Finding**: **MATCH** (Covered by `test_plan_units_groups_fast_files_per_dir_and_keeps_slow_ones_single`)

---

### Clause 2: Slow stays single
- **Card Goal**: "slow files stay single"
- **Code Quote** (`scripts/dev/run_extra_tests.py:139-141`):
  ```python
      for rel in slowest_first(rels):
          if rel in SLOW_FIRST or shares_state(rel):
              units.append(("one", rel))
  ```
- **Test Quote** (`scripts/dev/test_run_extra_tests.py:130-135`):
  ```python
      slow = "scripts/dev/test_planted_error_trial.py"
      rels = ["a/test_1.py", slow, "a/test_2.py", "b/test_3.py", "a/test_4.py"]
      units = rx.plan_units(rels, group_max=2)
      assert units[0] == ("one", slow)
  ```
- **Finding**: **MATCH** (Covered by `test_plan_units_groups_fast_files_per_dir_and_keeps_slow_ones_single`)

---

### Clause 3: Shared-state writer never grouped
- **Card Goal**: "a file that writes sys.modules, chdir or os.environ never groups"
- **Code Quote** (`scripts/dev/run_extra_tests.py:121, 127-128, 140-141`):
  ```python
  _SHARED_STATE = re.compile(r"sys\.modules\s*\[[^\]]*\]\s*=|os\.chdir\s*\(|os\.environ\s*\[[^\]]*\]\s*=|os\.environ\.(?:update|setdefault|pop)\s*\(|os\.putenv\s*\(|os\.unsetenv\s*\(|sys\.modules\.(?:update|setdefault|pop)\s*\(")

  def shares_state(rel):
      try:
          return bool(_SHARED_STATE.search((REPO / rel).read_text(encoding="utf-8", errors="replace")))
  ...
          if rel in SLOW_FIRST or shares_state(rel):
              units.append(("one", rel))
  ```
- **Test Quote** (`scripts/dev/test_run_extra_tests.py:186-195`):
  ```python
      bodies = {"d/test_clean1.py": ok, "d/test_clean2.py": ok,
                "d/test_cd.py": "import os" + NL + "def test_x(): os.chdir('.')",
                "d/test_mod.py": "import sys" + NL + "sys.modules['m'] = object()" + NL + ok,
                "d/test_env.py": "import os" + NL + "os.environ['A'] = '1'" + NL + ok}
      ...
      assert ("group", "d", ["d/test_clean1.py", "d/test_clean2.py"]) in units
      assert {u[1] for u in units if u[0] == "one"} == {"d/test_cd.py", "d/test_mod.py", "d/test_env.py"}
  ```
- **Finding**: **MATCH** (Covered by `test_files_writing_shared_interpreter_state_stay_single`)

---

### Clause 4: Unreadable = single
- **Card Goal**: "an unreadable file is single"
- **Code Quote** (`scripts/dev/run_extra_tests.py:129-130`):
  ```python
      except OSError:
          return True
  ```
- **Test Quote** (`scripts/dev/test_run_extra_tests.py:196`):
  ```python
      assert rx.shares_state("d/missing.py")
  ```
- **Finding**: **MATCH** (Covered by `test_files_writing_shared_interpreter_state_stay_single`)

---

### Clause 5: Red group re-run per file
- **Card Goal**: "a red group is re-run per file"
- **Code Quote** (`scripts/dev/run_extra_tests.py:166-171`):
  ```python
              if r.returncode == 0 and (r.stdout or "").strip() and all(p.name in seen for p in paths):   # a file with no test (exit 5 alone) must not hide in a green group
                  tail = (r.stdout.strip().splitlines() or [""])[-1]
                  return {rel: (True, f"{tail} (grouped x{len(rels)})") for rel in rels}
          except subprocess.TimeoutExpired:
              pass
      return {rel: run_one(rel, Path(basetemp) / f"f{i}", timeout) for i, rel in enumerate(rels)}
  ```
- **Test Quote** (`scripts/dev/test_run_extra_tests.py:151-157`):
  ```python
  def test_run_group_reports_the_failing_file_by_name_and_keeps_the_others_green(tmp_path, monkeypatch):
      monkeypatch.setattr(rx, "REPO", tmp_path)
      _mk(tmp_path, "d/test_good.py", "def test_a():\n    pass")
      _mk(tmp_path, "d/test_bad.py", "def test_b():\n    assert 0")
      bad = rx.run_files(["d/test_good.py", "d/test_bad.py"], 2, tmp=str(tmp_path / "bt"), many=rx.run_group)
      assert bad == ["d/test_bad.py"]
  ```
- **Finding**: **MATCH** (Covered by `test_run_group_reports_the_failing_file_by_name_and_keeps_the_others_green`)
