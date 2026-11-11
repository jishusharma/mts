Counts: MATCH: 8, DIFF: 0, NOT_IN_DATA: 0

# Gemini Blind Read of `scripts/sched/check_live_health.py` Against Its Docstring and Tests

- **Card ID**: `gemini-blind-read-check-live-health-docstring-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Scope In Read**:
  - `scripts/sched/check_live_health.py` (read)
  - `MyTradingSys/tests/test_check_live_health.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-check-live-health-docstring-1111.md` (new)
- **Scope Out**: Read-only audit; no source file edits; no live-tree edit; no deploy; no `.secrets` or `.env` read.

---

## Verification Table

| Clause ID | Docstring Clause Description | Implementation in `scripts/sched/check_live_health.py` | Test Verification in `MyTradingSys/tests/test_check_live_health.py` | Status | File:Line Citations & Detailed Audit Findings |
|---|---|---|---|---|---|
| C1 | Read-only contract: Read-only on the live system (never starts, stops or edits a process or a live file) | `scripts/sched/check_live_health.py:3,54-87,90-106,110-133` | `MyTradingSys/tests/test_check_live_health.py:1,46-50` | MATCH | **Docstring (`scripts/sched/check_live_health.py:3`)**: `"Read-only on the live system (never starts, stops or edits a process or a live file)."`<br>**Implementation (`scripts/sched/check_live_health.py:3,54-87,90-106,110-133`)**: The script inspects processes via Win32_Process queries or fixture json (`list_procs`), inspects file mtimes via `p.stat().st_mtime` (`file_problems`), and never modifies live processes or monitored live output files. The only files written are local debounce alert state / popup JSON in `runtime_data/live_health_alert.json` and `runtime/sched/live_health_state.json` when `--alert` is triggered.<br>**Test (`MyTradingSys/tests/test_check_live_health.py:1,46-50`)**: Tests execute against mock temp directory fixtures and json proc fixtures without modifying any live tree or launching background processes. |
| C2 | Detector contract: Output line 1 `live_health <OK\|WARN\|RED> <reason>`, line 2 `HASH ...`, exit code 0/1/2 | `scripts/sched/check_live_health.py:4,30,119,129,131,132,136` | `MyTradingSys/tests/test_check_live_health.py:46-50,52-56,60-65,106,113` | MATCH | **Docstring (`scripts/sched/check_live_health.py:4`)**: `"Detector contract (_common): line 1 \`live_health <OK\|WARN\|RED> <reason>\`, line 2 \`HASH ...\`, exit 0/1/2."`<br>**Implementation (`scripts/sched/check_live_health.py:4,30,119,129,131,132,136`)**: Line 30 imports `emit, run` from `_common`. `_common.py:12,20-23` defines `EXIT = {"OK": 0, "WARN": 1, "RED": 2}` and emits line 1 `live_health <status> <reason>` and line 2 `HASH <sha256>`. In `check_live_health.py:119,129,131,132`, statuses `WARN` (exit 1), `RED` (exit 2), and `OK` (exit 0) are emitted accordingly.<br>**Test (`MyTradingSys/tests/test_check_live_health.py:46-50,52-56,60-65,106,113`)**: Helper `check()` verifies exit code and stdout line 1. Tests verify `code == 0` for OK, `code == 1` for WARN, and `code == 2` for RED. |
| C3 | Stale files check: 5 monitored file types with age limits (snapshots 300s, state_code 300s, orderflow day csv 300s, oi_1m.csv 300s, htf_context jsonl 15000s); newest mtime older than limit -> RED | `scripts/sched/check_live_health.py:6-10,32-38,63-73,120,123-129` | `MyTradingSys/tests/test_check_live_health.py:11-17,58-66,68-73,75-82` | MATCH | **Docstring (`scripts/sched/check_live_health.py:6-10`)**: `"Stale files (newest matching file's mtime older than the limit -> RED): snapshots, state_code 300 s ... orderflow day csv 300 s ... oi_1m.csv 300 s ... htf_context jsonl 15000 s ..."`<br>**Implementation (`scripts/sched/check_live_health.py:32-38,63-73,120,123-129`)**: Lines 32-38 configure `FILES` matching all 5 paths/globs and limits: snapshots (300s), state_code (300s), orderflow (300s), oi_1m (300s), htf_context (15000s). Lines 63-73 (`file_problems`) compute `age = now - max(p.stat().st_mtime for p in found)` and mark as bad if missing or `age > limit`. Lines 123-129 emit `RED`.<br>**Test (`MyTradingSys/tests/test_check_live_health.py:11-17,58-66,68-73,75-82`)**: `test_each_file_goes_red_just_past_its_limit`, `test_missing_file_is_red`, and `test_every_generated_input_absent_is_red_never_ok` verify each file goes RED on stale age or missing file. |
| C4 | Processes check (drop condition): Command-line regex for 7 processes; none alive -> RED | `scripts/sched/check_live_health.py:11-13,39-47,76-87,121-129` | `MyTradingSys/tests/test_check_live_health.py:18-26,92-97` | MATCH | **Docstring (`scripts/sched/check_live_health.py:11-13`)**: `"Processes (command-line regex; none alive -> RED, more than one top-level copy -> WARN): java statemachine loop, loop-supervisor.ps1, and the supervisor's $Aux list (auto_trader, live_runner_cli, orderflow_live, daily_loss_monitor), plus htf_context_live --loop."`<br>**Implementation (`scripts/sched/check_live_health.py:39-47,76-87,121-129`)**: Lines 39-47 configure `PROCS` regexes for `loop_java`, `loop_supervisor`, `auto_trader`, `live_runner_cli`, `orderflow_live`, `daily_loss_monitor`, and `htf_context_live`. Lines 76-87 (`proc_problems`) find top-level processes (`p["ppid"] not in pids`). If `not top`, records `f"{name}: process not running"` in `bad`, resulting in exit code 2 `RED`.<br>**Test (`MyTradingSys/tests/test_check_live_health.py:18-26,92-97`)**: `test_each_dropped_process_is_red` tests omitting each of the 7 processes in turn and asserts exit code 2 and `"process not running"` in line. |
| C5 | Processes check (duplicate condition): More than one top-level copy alive -> WARN (launcher shim + child count once) | `scripts/sched/check_live_health.py:11-13,76-87,121,130-131` | `MyTradingSys/tests/test_check_live_health.py:99-107` | MATCH | **Docstring (`scripts/sched/check_live_health.py:11-13`)**: `"...more than one top-level copy -> WARN ..."`<br>**Implementation (`scripts/sched/check_live_health.py:76-87,121,130-131`)**: Lines 81-82 deduplicate parent-child pairs (`top = [p for p in hits if p.get("ppid") not in pids]`). If `len(top) > 1`, records warning in `warn`. Line 131 emits `WARN` (exit 1) with message `f"{len(top)} copies running"`.<br>**Test (`MyTradingSys/tests/test_check_live_health.py:99-107`)**: `test_launcher_shim_and_child_count_once_but_two_copies_warn` verifies that child + parent counts once (OK), but two top-level copies produce `code == 1` and `WARN`. |
| C6 | Stop flag handling: `runtime_data/loop_stop.flag` present -> WARN "loop stopped by flag" (intended stop is not an outage) | `scripts/sched/check_live_health.py:14,118-119` | `MyTradingSys/tests/test_check_live_health.py:109-113` | MATCH | **Docstring (`scripts/sched/check_live_health.py:14`)**: `"runtime_data/loop_stop.flag present -> WARN \"loop stopped by flag\" (an intended stop is not an outage)."`<br>**Implementation (`scripts/sched/check_live_health.py:118-119`)**: Lines 118-119 check `if (root / "runtime_data" / "loop_stop.flag").exists(): return emit("live_health", "WARN", "loop stopped by flag (runtime_data/loop_stop.flag)", ["stop_flag"])`. Short-circuits health checks, returning exit 1 without RED failure.<br>**Test (`MyTradingSys/tests/test_check_live_health.py:109-113`)**: `test_stop_flag_is_warn_not_red` creates `loop_stop.flag` with empty proc list and stale age; asserts `code == 1` and `"stopped by flag" in line`. |
| C7 | Desktop alert & debounce: `--alert`: on RED, show desktop popup (`scripts/core/show-alert.ps1`) when failing set changed or 60 min passed; debounce state in `MyTradingSys/runtime/sched/live_health_state.json` | `scripts/sched/check_live_health.py:16-17,48,90-106,126-128` | `MyTradingSys/tests/test_check_live_health.py:1` | MATCH | **Docstring (`scripts/sched/check_live_health.py:16-17`)**: `"--alert: on RED, show the desktop popup (scripts/core/show-alert.ps1) when the failing set changed or 60 min passed since the last popup for the same set. Debounce state: MyTradingSys/runtime/sched/live_health_state.json."`<br>**Implementation (`scripts/sched/check_live_health.py:48,90-106,126-128`)**: Line 48 sets `REPOPUP_SEC = 3600` (60 min). Lines 90-106 (`popup`) check debounce state file against hash `h` and elapsed time. If hash matches and age < 3600s, returns `False` (debounced). Otherwise writes `live_health_alert.json`, launches `launch-alert.vbs` pointing to `show-alert.ps1`, and records new hash and timestamp to state path.<br>**Test (`MyTradingSys/tests/test_check_live_health.py:1`)**: Tests run without `--alert` fixture to prevent invasive GUI popups during automated test runs as noted in file docstring line 1. |
| C8 | Unattended execution flag: `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)` on PowerShell subprocess call preserves behavior without flashing console windows | `scripts/sched/check_live_health.py:57-58` | `MyTradingSys/tests/test_check_live_health.py:52-56` | MATCH | **Docstring (`scripts/sched/check_live_health.py:18`)**: `"Usage: python scripts/sched/check_live_health.py [--root LIVE_TREE] [--alert] [--procs-json F] [--now EPOCH]"`<br>**Implementation (`scripts/sched/check_live_health.py:57-58`)**: Line 58 passes `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)` to `subprocess.run(["powershell", ...])`. On Windows, `CREATE_NO_WINDOW = 0x08000000` prevents spawning console window popups during background scheduler executions; on non-Windows platforms `getattr` defaults to 0. It alters no process arguments, timeouts, output parsing, or exit codes.<br>**Test (`MyTradingSys/tests/test_check_live_health.py:52-56`)**: Subprocess execution and fixture handling pass 100% of the 8 test cases. |

---

## Detailed Audit of the `creationflags` Edit

1. **Commit Audit**:
   - Commit `c0354cca92cf` (2026-11-11) introduced `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)` to `scripts/sched/check_live_health.py:58`.
   - Prior code:
     ```python
     out = subprocess.run(["powershell", "-NoProfile", "-Command", PS_LIST], capture_output=True, text=True,
                          timeout=60, check=True).stdout
     ```
   - Current code:
     ```python
     out = subprocess.run(["powershell", "-NoProfile", "-Command", PS_LIST], capture_output=True, text=True,
                          timeout=60, check=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout
     ```
2. **Behavioral Invariance**:
   - `capture_output=True`, `text=True`, `timeout=60`, `check=True` and stdout capture remain identical.
   - The output string `out` is parsed identically with `json.loads(out or "[]")`.
   - `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)` only instructs the Windows process creation subsystem (`CreateProcessW`) to omit creating a console window (`CREATE_NO_WINDOW`). No process input/output or operational semantics are modified.
   - All 8 unit tests in `MyTradingSys/tests/test_check_live_health.py` pass cleanly.

---

## Summary of Findings

- Total clauses audited: 8
- **MATCH**: 8
- **DIFF**: 0
- **NOT_IN_DATA**: 0
- The implementation in `scripts/sched/check_live_health.py` and test suite `MyTradingSys/tests/test_check_live_health.py` fully match all docstring clauses. The `creationflags` edit changed no functional behavior.
