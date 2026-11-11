MATCH: 8, DIFF: 0, NOT_IN_DATA: 0

# Gemini Blind Read of `scripts/sched/tick.py` Against Its Docstring and Creationflags Edit

- **Card ID**: `gemini-blind-read-tick-docstring-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Scope In Read**:
  - `scripts/sched/tick.py` (read)
  - `MyTradingSys/tests/test_autogo.py` (read; tick tests finding `tick.py`)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-tick-docstring-1111.md` (new)
- **Scope Out**: No edit to source files; no live-tree edit, no deploy, no `.secrets` or `.env` read; read-only audit.

---

## Clause Verification Table

| # | Clause from Docstring / Goal | Code Reference in `scripts/sched/tick.py` | Classification | Audit Details & Citations (file:line) |
|---|---|---|---|---|
| 1 | Detector order: "run every detector in order" (`scripts/sched/tick.py:1`) | `scripts/sched/tick.py:31-40`, `scripts/sched/tick.py:96-116` | MATCH | **Docstring (`scripts/sched/tick.py:1`)**: SOURCED: `"Tier 0 clock (SCHEDULER_PLAN s2/s5): run every detector in order, debounce by state hash, write a tick report."`<br>**Implementation (`scripts/sched/tick.py:31-40,96-116`)**: SOURCED: `CHECKS` is an ordered list of 8 detectors: `snapshot_age` (L32), `live_health` (L33), `canary` (L34), `autogo` (L35), `sessions` (L36), `bug_age` (L37), `paste_size` (L38), `new_aging` (L39). In `main()`, `for name, argv, kind in CHECKS:` (L96) iterates sequentially through each detector in that exact order, executing `run_check(name, argv)` (L99) and collecting results into `rows` (L116). |
| 2 | Debounce by state hash: "debounce by state hash" (`scripts/sched/tick.py:1,4-7`) | `scripts/sched/tick.py:4-7`, `scripts/sched/tick.py:19`, `scripts/sched/tick.py:65-67`, `scripts/sched/tick.py:93-94`, `scripts/sched/tick.py:104-115` | MATCH | **Docstring (`scripts/sched/tick.py:1,4-7`)**: SOURCED: `"debounce by state hash"` (L1), `"Debounce state: MyTradingSys/runtime/sched/tick_state.json"` (L4), `"event_seen {hash: last_fired_utc} event check fires only if hash unseen within 24 h"` (L5), `"digest_included [hash] hashes in the last completed digest ... a digest item is new if its hash is not in that list"` (L6-7).<br>**Implementation (`scripts/sched/tick.py:65-67,93-94,104-115`)**: SOURCED: Uses `state_hash` from `_common.py` (L19, L67) or parser from stdout (L65). Filters expired event hashes with `DEBOUNCE = timedelta(hours=24)` (L25, L93-94). For event checks, if `h in state["event_seen"]`, action is `"debounced(24h)"` (L105); otherwise fires event and records hash (L107-108). For digest checks, if `h in state["digest_included"]`, marks `"digest(already included)"` (L112), else adds to pending digest as `"digest(new)"` (L114-115). |
| 3 | 24 h event_seen debounce window: "event check fires only if hash unseen within 24 h" (`scripts/sched/tick.py:5`) | `scripts/sched/tick.py:25`, `scripts/sched/tick.py:93-94`, `scripts/sched/tick.py:104-109` | MATCH | **Docstring (`scripts/sched/tick.py:5`)**: SOURCED: `"event_seen    {hash: last_fired_utc}   event check fires only if hash unseen within 24 h"`.<br>**Implementation (`scripts/sched/tick.py:25,93-94,104-109`)**: SOURCED: `DEBOUNCE = timedelta(hours=24)` (L25). In `main()`, pruning retains hashes seen within 24 hours: `state["event_seen"] = {h: t for h, t in state["event_seen"].items() if now - datetime.fromisoformat(t) < DEBOUNCE}` (L93-94). When an event check produces code 2, if `h in state["event_seen"]`, it is debounced (`"debounced(24h)"`, L105); else it fires Haiku event and records `state["event_seen"][h] = now.isoformat()` (L108). |
| 4 | Worst exit code: "Exit code = worst exit of the checks run (0 OK, 1 WARN, 2 RED)" (`scripts/sched/tick.py:3`) | `scripts/sched/tick.py:3`, `scripts/sched/tick.py:68`, `scripts/sched/tick.py:95`, `scripts/sched/tick.py:100`, `scripts/sched/tick.py:132`, `scripts/sched/tick.py:136` | MATCH | **Docstring (`scripts/sched/tick.py:3`)**: SOURCED: `"No Claude calls here. Exit code = worst exit of the checks run (0 OK, 1 WARN, 2 RED)."`.<br>**Implementation (`scripts/sched/tick.py:68,95,100,132,136`)**: SOURCED: `run_check` normalizes returncode: `code = p.returncode if p.returncode in (0, 1, 2) else 2` (L68) and maps timeout to 2 (L62). `main()` initializes `worst = 0` (L95), updates `worst = max(worst, code)` per check (L100), outputs worst exit to report header (L124) and summary stdout (L131), returns `worst` (L132), and exits with `sys.exit(main())` (L136). |
| 5 | Tick report path: "Output: MyTradingSys/research/sched_reports/tick_<utc>.md" (`scripts/sched/tick.py:8`) | `scripts/sched/tick.py:24`, `scripts/sched/tick.py:26`, `scripts/sched/tick.py:122-128` | MATCH | **Docstring (`scripts/sched/tick.py:8`)**: SOURCED: `"Output: MyTradingSys/research/sched_reports/tick_<utc>.md (ends with a "## Pick" section from pick_task.py) ; also prints a one-line summary."`.<br>**Implementation (`scripts/sched/tick.py:24,26,122-128`)**: SOURCED: `REPORT_DIR = REPO / "MyTradingSys" / "research" / "sched_reports"` (L24), `TS_FMT = "%Y%m%dT%H%M%SZ"` (L26), `REPORT_DIR.mkdir(parents=True, exist_ok=True)` (L122), `out = REPORT_DIR / f"tick_{now.strftime(TS_FMT)}.md"` (L123), `out.write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")` (L128). Also prints summary `print(f"TICK worst={worst} fires={len(fires)} digest_new={len(digest)} report={out.name}")` (L131). |
| 6 | Pick section: "(ends with a "## Pick" section from pick_task.py)" (`scripts/sched/tick.py:8`) | `scripts/sched/tick.py:72-81`, `scripts/sched/tick.py:129-130` | MATCH | **Docstring (`scripts/sched/tick.py:8`)**: SOURCED: `"(ends with a "## Pick" section from pick_task.py)"`.<br>**Implementation (`scripts/sched/tick.py:72-81,129-130`)**: SOURCED: `run_pick()` runs `[PY, "scripts/sched/pick_task.py"]` (L74) and returns first line of stdout or error message (L76, L78, L80, L81). Appends to report file: `with open(out, "a", encoding="utf-8", newline="\n") as f: f.write("\n## Pick\n\n" + run_pick() + "\n")` (L129-130). |
| 7 | CLI Usage and options: "Usage (repo root): python scripts/sched/tick.py [--now ISO] [--only name,name]" (`scripts/sched/tick.py:9`) | `scripts/sched/tick.py:85-90`, `scripts/sched/tick.py:97-98` | MATCH | **Docstring (`scripts/sched/tick.py:9`)**: SOURCED: `"Usage (repo root): python scripts/sched/tick.py [--now ISO] [--only name,name]"`.<br>**Implementation (`scripts/sched/tick.py:85-90,97-98`)**: SOURCED: Uses `argparse.ArgumentParser()` (L85), defines `--now` (L86) parsed to UTC datetime (L89), and `--only` (L87) parsed to set of check names (L90). Loops over checks and skips unselected: `if only and name not in only: continue` (L97-98). |
| 8 | Creationflags edit: `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)` changed no behaviour (`scripts/sched/tick.py:60,74`) | `scripts/sched/tick.py:60`, `scripts/sched/tick.py:74`, commit `c0354cca92cf` | MATCH | **Goal Requirement**: SOURCED: `"and that the creationflags edit changed no behaviour"`.<br>**Implementation & Analysis (`scripts/sched/tick.py:60,74`)**: SOURCED: In commit `c0354cca92cf`, `run_check()` (L60) and `run_pick()` (L74) added `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)`. On Windows, `subprocess.CREATE_NO_WINDOW == 0x08000000`, which suppresses console window creation without affecting process arguments, streams, environment, working directory, exit code, or stdout/stderr capture (`capture_output=True, text=True`). On non-Windows platforms, `getattr(..., 0)` safely falls back to `0` (no flag). All returncode handling, timeout handling, and string processing remain identical. |

---

## Verification with Test Suite

- **Tick Test Discovery**:
  - Grepping `tick.py` in test folders revealed `MyTradingSys/tests/test_autogo.py:138-140` (`test_9_tick_runs_autogo_check`), which explicitly verifies `scripts/sched/tick.py` CHECKS definition:
    - SOURCED (`MyTradingSys/tests/test_autogo.py:139-140`): `assert '("autogo", [PY, "scripts/sched/autogo.py", "--tick"], "event")' in src`.
  - Executed `pytest MyTradingSys/tests/test_autogo.py`:
    - SOURCED: 9 passed in 1.88s (100% pass).
  - Executed import verification `python -c "import scripts.sched.tick; print('Import OK')"`:
    - SOURCED: Exit code 0, prints `Import OK`.

---

## Summary of Findings

- Total clauses audited: 8 (SOURCED: 8 rows in table above)
- **MATCH**: 8 (SOURCED: 8 clauses verified against `scripts/sched/tick.py` lines 1-136, test suite, and commit `c0354cca92cf`)
- **DIFF**: 0 (OURS: 0 discrepancies)
- **NOT_IN_DATA**: 0 (OURS: 0 unverified clauses)
- Line 1 count: `MATCH: 8, DIFF: 0, NOT_IN_DATA: 0`.
