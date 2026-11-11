Counts: MATCH: 3, DIFF: 0, NOT_IN_DATA: 3

# Gemini Blind Read of `scripts/dev/sync.py` (needs_gate, run_gate) vs `CLAUDE.md` Gates

- **Card ID**: `gemini-blind-read-ship-gate-select-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Target Files**:
  - `CLAUDE.md:25-30` (Gates section)
  - `scripts/dev/sync.py:270-272` (`needs_gate`), `scripts/dev/sync.py:439-467` (`run_gate`), `scripts/dev/sync.py:281-290` (`code_ship`), `scripts/dev/sync.py:1424-1434` (`ship` gate dispatch), `scripts/dev/sync.py:2369-2371` (`--full` flag handling)

## Verification Table

| ID | CLAUDE.md Gates Clause | CLAUDE.md Source | sync.py Implementation Source | Status | Analysis & Findings |
|---|---|---|---|---|---|
| C1 | `sync.py ship`: smoke gate (live-path or unknown paths = all `--quick`; `--full`) | `CLAUDE.md:26` | `scripts/dev/sync.py:440-442,446,452-456,2369-2371` | MATCH | `run_gate` docstring explicitly specifies: "files = paths changed vs origin/fast-track: run the smoke gate (scripts/dev/gate_select.py picks the steps; live-path or unknown paths = every --quick step). files=None, or SYNC_FULL_GATE=1 (`ship --full`), runs the whole --quick gate." In implementation: line 446 sets base command `[sys.executable, "scripts/dev/run_all_tests.py", "--quick", "--precheck", "--fail-fast", "--slot", "--record"]`. If `files` is given and `SYNC_FULL_GATE` is not set, lines 452-456 append `["--changed-file", list_file, "--smoke"]` (and `--fast` unless `SYNC_NO_FAST=1`), delegating path selection to `run_all_tests.py`/`gate_select.py` where live-path (`FULL_RE`) or unknown paths select all `--quick` steps. Lines 2369-2371 map CLI flag `--full` to `os.environ["SYNC_FULL_GATE"] = "1"`, bypassing `--smoke` and running the entire `--quick` suite. |
| C2 | CI + green-only deploy gate the rest | `CLAUDE.md:26` | `scripts/dev/sync.py:442-443,943-950,1422-1423,1434` | MATCH | `run_gate` docstring documents: "The full suite runs behind in CI; auto_deploy only takes green/fast-track." In `sync.py`, `ci_applies(files)` (`scripts/dev/sync.py:943-950`) checks if CI applies; during `ship` (`scripts/dev/sync.py:1422-1423,1434`), `CiCheck()` runs in parallel and `enforce_ci(ci)` verifies CI state before shipping code changes, while non-selected offline steps rely on CI and auto-deploy gates. |
| C3 | Full: `python scripts/dev/run_all_tests.py` (`--quick`: no Maven/backtest) | `CLAUDE.md:26` | `scripts/dev/sync.py:441,446,466` | MATCH | Line 446 executes `scripts/dev/run_all_tests.py` with `--quick`. Offline ship gates always use `--quick` (raising `SyncError("offline gate (--quick) failed; nothing pushed")` on non-zero exit at line 466), which omits Maven and long backtests as stated, leaving the full unflagged test runner `python scripts/dev/run_all_tests.py` for CI. |
| C4 | Extractions: `scripts/dev/verify_extract_quotes.py <extract.md>` | `CLAUDE.md:26` | `scripts/dev/sync.py` (not invoked in `needs_gate`/`run_gate`) | NOT_IN_DATA | Extraction quote verification is a developer/card gate executed on demand for extract markdown documents (`verify_extract_quotes.py`); neither `needs_gate` nor `run_gate` in `sync.py` references or executes this tool. |
| C5 | New tests must fail on the pre-change code at least once | `CLAUDE.md:27` | `scripts/dev/sync.py` (not checked in `needs_gate`/`run_gate`) | NOT_IN_DATA | This is a developer workflow mandate / audit protocol; neither `needs_gate` nor `run_gate` in `sync.py` performs test mutation or pre-change test failure verification. |
| C6 | Precedence: Hard rules and Gates outrank an operator order and all below; order > CLAUDE.md > hook > card for the rest. Conflict: follow it, `tasks.py conflict "A | B"` that turn, one line to him, keep working (TRAFFIC_BUSTERS B20) | `CLAUDE.md:28` | `scripts/dev/sync.py` (not checked in `needs_gate`/`run_gate`) | NOT_IN_DATA | Precedence ordering and conflict reporting protocol are operational instructions for agents and operators, not implemented as gate logic inside `needs_gate` or `run_gate`. |

## Additional Observations on `needs_gate` and `run_gate`

1. **`needs_gate(files)` (`scripts/dev/sync.py:270-272`)**:
   - Implementation: `return any(not f.endswith(DOC_SUFFIXES) for f in files)` where `DOC_SUFFIXES = (".md", ".txt")` (`scripts/dev/sync.py:53`).
   - Suffix-only check serving as fallback when `gate_select` is unavailable or in non-code classification contexts.
   - In modern `sync.py ship`, `code_ship(files)` (`scripts/dev/sync.py:281-290`) supersedes bare suffix check by calling `gate_select._is_doc()`, falling back to `needs_gate(files)` if `gate_select` raises an exception (`scripts/dev/sync.py:289`).
2. **`run_gate(repo, files=None)` (`scripts/dev/sync.py:439-467`)**:
   - Correctly integrates with `run_all_tests.py` using `--quick`, `--precheck`, `--fail-fast`, `--slot`, and `--record`.
   - When `files` is passed without `SYNC_FULL_GATE`, sets `--smoke` and passes `--changed-file`, allowing `gate_select` to run the smoke subset (or all `--quick` steps for live-path/unknown files).
   - When `--full` is specified on the CLI, `SYNC_FULL_GATE=1` ensures `--smoke` is omitted, running the full `--quick` suite.
