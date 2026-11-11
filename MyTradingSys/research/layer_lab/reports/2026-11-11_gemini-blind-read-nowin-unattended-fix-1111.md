COUNTS: MATCH=36 DIFF=2 NOT_IN_DATA=0

# Scan Report: Subprocess Calls in `scripts/sched`, `scripts/worker`, `MyTradingSys/execution`, and `MyTradingSys/runtime` Outside `scripts/dev` (Post-`c0354cca9`)

- **Task**: `gemini-blind-read-nowin-unattended-fix-1111`
- **Date**: 2026-11-11 UTC
- **Auditor**: Gemini 3.8 Flash (Low)
- **Scope In**:
  - `scripts/sched/*.py` (16 files)
  - `scripts/worker/*.py` (non-test files: 6 files; test files: 4 files)
  - `MyTradingSys/execution/*.py` (non-test files: 25 files; test files: 46 files)
  - `MyTradingSys/runtime/*.py` (non-test files: 14 files; test files: 1 file)
  - `scripts/dev/nowin_scan.py` (the rule; read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-nowin-unattended-fix-1111.md` (new)
- **Scope Out**: No edit to the source files; no live-tree edit, no deploy, no `.secrets` or `.env` read; read-only audit.

---

## Executive Summary

An independent audit of all non-test Python files across the 4 specified directories outside `scripts/dev` was conducted following commit `c0354cca9` ("no-window flag on 35 unattended subprocess calls outside scripts/dev (q-5aeda0)"):
- Total non-test files scanned in scope: 61 files
  - `scripts/sched/*.py`: 16 files
  - `scripts/worker/*.py` (excluding `test_*.py`): 6 files
  - `MyTradingSys/execution/*.py` (excluding `test_*.py`): 25 files
  - `MyTradingSys/runtime/*.py` (excluding `test_*.py`): 14 files
- Total subprocess call sites identified: 38 calls
  - **MATCH**: 36 calls
    - 35 captured subprocess calls pass `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)` (all patched in `c0354cca9`).
    - 1 uncaptured subprocess call inherits the console on purpose: `scripts/sched/go.py:117` (`subprocess.call(cmd, cwd=ROOT)`), which is the interactive CLI entry point launching Claude whose stdout/stderr the operator reads on the active terminal.
  - **DIFF**: 2 calls
    - Unattended background subprocess calls that lack `creationflags` and do not intend to display console windows to the user:
      1. `scripts/sched/autogo.py:149` (`subprocess.Popen([sys.executable, str(HERE / "go.py"), "--id", rid, "--headless"], cwd=ROOT)`): Spawns `go.py --headless` as an unattended background child from `autogo.py`. Because `creationflags` is omitted, Windows spawns a flashing console window on invocation.
      2. `scripts/sched/check_live_health.py:102` (`subprocess.Popen(["wscript.exe", str(root / "scripts" / "core" / "launch-alert.vbs"), str(root / "scripts" / "core" / "show-alert.ps1"), str(alert)])`): Spawns `wscript.exe` to launch a desktop toast alert script without `creationflags`.
  - **NOT_IN_DATA**: 0

---

## Calls Lacking `creationflags` (DIFF and Console-Inheriting MATCH)

| # | Call Site (`file:line`) | Call Name | Captured | Call Quote | Status | Purpose / Console Intent |
|---|---|---|---|---|---|---|
| 1 | `scripts/sched/autogo.py:149` | `Popen` | `No` | `child = subprocess.Popen([sys.executable, str(HERE / "go.py"), "--id", rid, "--headless"], cwd=ROOT)` | `DIFF` | Unattended background scheduler daemon spawning headless `go.py`. Lacks `creationflags`; opens a flashing console window. |
| 2 | `scripts/sched/check_live_health.py:102` | `Popen` | `No` | `subprocess.Popen(["wscript.exe", str(root / "scripts" / "core" / "launch-alert.vbs"), str(root / "scripts" / "core" / "show-alert.ps1"), str(alert)])` | `DIFF` | Unattended health monitor spawning `wscript.exe` for alert notification. Lacks `creationflags`. |
| 3 | `scripts/sched/go.py:117` | `call` | `No` | `return subprocess.call(cmd, cwd=ROOT)` | `MATCH` | Interactive CLI launcher running Claude session attached to active operator terminal. Inherits console on purpose. |

---

## All Subprocess Calls in Scope (38 Sites)

| # | Call Site (`file:line`) | Call Name | Captured | Has `creationflags` | Status | Quoted Call |
|---|---|---|---|---|---|---|
| 1 | `MyTradingSys/execution/auto_trader.py:685` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 2 | `MyTradingSys/execution/auto_trader.py:767` | `Popen` | `Yes` | `Yes` | `MATCH` | `return subprocess.Popen([sys.executable, str(HERE / "position_manager.py"), plan_id], cwd=REPO, stdout=mlog, stderr=subprocess.STDOUT, env=penv, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 3 | `MyTradingSys/execution/auto_trader.py:897` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Process \| Select-Object ProcessId,CommandLine \| ConvertTo-Json -Compress"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 4 | `MyTradingSys/execution/mutation_check_auto_trader_failclosed.py:70` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run([sys.executable, str(d / f"{T}.py"), test], capture_output=True, text=True, env=env, cwd=str(d), creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 5 | `MyTradingSys/runtime/update_market_state.py:39` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run([sys.executable, str(LEVELS_SCRIPT), "--json"], capture_output=True, text=True, timeout=timeout, encoding="utf-8", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 6 | `scripts/sched/autogo.py:67` | `run` | `Yes` | `Yes` | `MATCH` | `out = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/NH"], capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout` |
| 7 | `scripts/sched/autogo.py:97` | `run` | `Yes` | `Yes` | `MATCH` | `p = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=100, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 8 | `scripts/sched/autogo.py:149` | `Popen` | `No` | `No` | `DIFF` | `child = subprocess.Popen([sys.executable, str(HERE / "go.py"), "--id", rid, "--headless"], cwd=ROOT)` |
| 9 | `scripts/sched/check_live_health.py:57` | `run` | `Yes` | `Yes` | `MATCH` | `out = subprocess.run(["powershell", "-NoProfile", "-Command", PS_LIST], capture_output=True, text=True, timeout=60, check=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout` |
| 10 | `scripts/sched/check_live_health.py:102` | `Popen` | `No` | `No` | `DIFF` | `subprocess.Popen(["wscript.exe", str(root / "scripts" / "core" / "launch-alert.vbs"), str(root / "scripts" / "core" / "show-alert.ps1"), str(alert)])` |
| 11 | `scripts/sched/dispatch_gate.py:57` | `run` | `Yes` | `Yes` | `MATCH` | `subprocess.run(["git", "-C", str(root), "fetch", "-q", "origin", "fast-track"], capture_output=True, timeout=120, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 12 | `scripts/sched/dispatch_gate.py:59` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run(["git", "-C", str(root), "show", "origin/fast-track:scripts/sched/%s.py" % name], capture_output=True, timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 13 | `scripts/sched/dispatch_gate.py:97` | `run` | `Yes` | `Yes` | `MATCH` | `w = subprocess.run([sys.executable, str(relay), "watchdog"], capture_output=True, text=True, encoding="utf-8", timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 14 | `scripts/sched/dispatch_gate.py:100` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run([sys.executable, str(relay), "tick", "--root", a.root, "--peer-quiet-min", a.peer_quiet_min, "--hourly-min", HOURLY_MIN, "--gate"], capture_output=True, text=True, encoding="utf-8", timeout=300, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 15 | `scripts/sched/dispatch_gate.py:112` | `run` | `Yes` | `Yes` | `MATCH` | `p = subprocess.run(launcher_argv(a.launcher), input=REFINE_PREAMBLE + hourly, capture_output=True, text=True, encoding="utf-8", timeout=3600, cwd=a.root, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 16 | `scripts/sched/dispatch_gate.py:124` | `run` | `Yes` | `Yes` | `MATCH` | `p = subprocess.run(launcher_argv(a.launcher), input=PREAMBLE + r.stdout, capture_output=True, text=True, encoding="utf-8", timeout=3600, cwd=a.root, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 17 | `scripts/sched/dispatch_gate.py:128` | `run` | `Yes` | `Yes` | `MATCH` | `subprocess.run([sys.executable, str(relay), "unlock"], capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 18 | `scripts/sched/dispatch_gate.py:131` | `run` | `Yes` | `Yes` | `MATCH` | `subprocess.run([sys.executable, str(relay), "unlock"], capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 19 | `scripts/sched/go.py:117` | `call` | `No` | `No` | `MATCH` | `return subprocess.call(cmd, cwd=ROOT)` |
| 20 | `scripts/sched/pick_task.py:115` | `run` | `Yes` | `Yes` | `MATCH` | `p = subprocess.run(["git", "log", "-n", "1", "--format=%h", "-i", "-E", "--grep=^" + rid + ":"], cwd=ROOT, capture_output=True, text=True, timeout=30, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 21 | `scripts/sched/relay.py:227` | `run` | `Yes` | `Yes` | `MATCH` | `subprocess.run(["git", "fetch", "-q", "origin", ref.split("/", 1)[-1]], capture_output=True, timeout=120, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 22 | `scripts/sched/relay.py:228` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run(["git", "show", spec], capture_output=True, text=True, encoding="utf-8", timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 23 | `scripts/sched/relay.py:236` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run(["git", "show", spec], capture_output=True, text=True, encoding="utf-8", timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 24 | `scripts/sched/relay.py:251` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run(["git", "show", "%s:%s/%s" % (ref, path.rsplit("/", 1)[0], RUNS_NAME)], capture_output=True, text=True, encoding="utf-8", timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 25 | `scripts/sched/relay.py:259` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run(["git", "log", "-1", "--format=%ct", ref, "--", path], capture_output=True, text=True, timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 26 | `scripts/sched/relay.py:381` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run(["git", "-C", str(root), "grep", "-l", '"relay_key"', ref, "--", DESK_DIR, CARD_DIR], capture_output=True, text=True, encoding="utf-8", timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 27 | `scripts/sched/relay.py:385` | `run` | `Yes` | `Yes` | `MATCH` | `s = subprocess.run(["git", "-C", str(root), "show", "%s:%s" % (ref, n)], capture_output=True, text=True, encoding="utf-8", timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 28 | `scripts/sched/relay.py:414` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run([sys.executable, str(script), "status"], capture_output=True, text=True, encoding="utf-8", timeout=30, cwd=str(root), creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 29 | `scripts/sched/relay.py:568` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 30 | `scripts/sched/relay.py:769` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run(["git", "-C", str(root), "show", PROMPT_REF], capture_output=True, text=True, encoding="utf-8", timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 31 | `scripts/sched/relay.py:865` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run(["git", "-C", str(root), "show", SESSION_REF], capture_output=True, text=True, encoding="utf-8", timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 32 | `scripts/sched/run_worker.py:223` | `run` | `Yes` | `Yes` | `MATCH` | `p = subprocess.run([claude, "--help"], capture_output=True, text=True, timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 33 | `scripts/sched/run_worker.py:248` | `Popen` | `Yes` | `Yes` | `MATCH` | `proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=REPO, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 34 | `scripts/sched/tick.py:60` | `run` | `Yes` | `Yes` | `MATCH` | `p = subprocess.run(argv, cwd=REPO, capture_output=True, text=True, timeout=120, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 35 | `scripts/sched/tick.py:74` | `run` | `Yes` | `Yes` | `MATCH` | `p = subprocess.run([PY, "scripts/sched/pick_task.py"], cwd=REPO, capture_output=True, text=True, timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 36 | `scripts/worker/audit_rotation.py:101` | `run` | `Yes` | `Yes` | `MATCH` | `result = subprocess.run([sys.executable, str(QUEUE_TOOL), "pack", str(path)], capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))` |
| 37 | `scripts/worker/queue_tool.py:674` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run( [sys.executable, "-m", "py_compile", str(tmp_py)], capture_output=True, text=True, timeout=30, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), )` |
| 38 | `scripts/worker/queue_tool.py:703` | `run` | `Yes` | `Yes` | `MATCH` | `r = subprocess.run( [sys.executable, "-m", "unittest", stem], cwd=str(tdp), capture_output=True, text=True, timeout=120, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), )` |
