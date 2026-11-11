Counts: MATCH: 8, DIFF: 0, NOT_IN_DATA: 0

# Gemini Blind Read of `scripts/worker/queue_tool.py` Against Its Docstring and Tests

- **Card ID**: `gemini-blind-read-queue-tool-docstring-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Scope In Read**:
  - `scripts/worker/queue_tool.py` (read)
  - `scripts/worker/test_dsa_worker.py` (read; contains `TestQueueTool` suite testing `queue_tool.py`)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-queue-tool-docstring-1111.md` (new)
- **Scope Out**: No edit to source files; no live-tree edit, no deploy, no `.secrets` or `.env` read; read-only audit.
- **Commit Audit**: Commit `c0354cca92cf` updated `scripts/worker/queue_tool.py:677,706` in `verify_one()` to add `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)` on the unattended `subprocess.run` invocations of `py_compile` and `unittest`. All 37 tests in `scripts/worker/test_dsa_worker.py` (including all 11 `TestQueueTool` tests) pass cleanly (`37 passed in 0.61s`).

---

## Verification Table (Docstring Clauses)

The module docstring in `scripts/worker/queue_tool.py:2-36` defines the coordinator-side queue tool contract:

| Clause ID | Clause Description | Docstring Citation (`scripts/worker/queue_tool.py`) | Code Implementation (`scripts/worker/queue_tool.py`) | Test Coverage (`scripts/worker/test_dsa_worker.py`) | Status | Audit Findings & File:Line Quotations |
|---|---|---|---|---|---|---|
| C1 | Purpose: NUC worker queue tool, coordinator side; self-contained task packaging with real file contents, no repo access needed for worker | `scripts/worker/queue_tool.py:2-7` | `scripts/worker/queue_tool.py:50-52,82-96,365-382,383-401` | `scripts/worker/test_dsa_worker.py:416-419,432-444` | MATCH | SOURCED: Docstring at `scripts/worker/queue_tool.py:2-7` states: `"The coordinator packs every task into a self-contained package: the task text plus the real content of every file in its scope. The NUC worker needs no access to the repository. Replies are checked mechanically before anyone reads them in full."`<br>Code implementation: `WORKER_RULES` (`scripts/worker/queue_tool.py:82-96`) instructs model that SOURCE blocks are its only source of truth. `build_package()` (`scripts/worker/queue_tool.py:365-382,383-401`) packages prompt with inlined file contents (`<<<SOURCE ...>>>`) and metadata. Tested in `scripts/worker/test_dsa_worker.py:416-419,432-444` verifying package generation with scoped content. |
| C2 | Subcommand `pack`: build task packages from spec files into `incoming/`; `--lane dsa` writes to `incoming_dsa/` | `scripts/worker/queue_tool.py:10-11` | `scripts/worker/queue_tool.py:298-401,404-425,798-802` | `scripts/worker/test_dsa_worker.py:432-444,445-450` | MATCH | SOURCED: Docstring at `scripts/worker/queue_tool.py:10-11` states: `"pack SPEC [SPEC ...]  Build task packages from spec files into incoming/. --lane dsa writes them to incoming_dsa/ (browser worker lane)."`<br>Code implementation: `cmd_pack()` (`scripts/worker/queue_tool.py:404-425`) and parser (`scripts/worker/queue_tool.py:798-802`). Reads spec files from `specs/` or current dir, checks duplicate package IDs across lanes (`scripts/worker/queue_tool.py:311-314`), routes to `incoming_dsa/` if `lane == "dsa"` else `incoming/` (`scripts/worker/queue_tool.py:417-419`). Exit code 0 on all success, 1 on any `Refused` error (`scripts/worker/queue_tool.py:425`). Tested in `scripts/worker/test_dsa_worker.py:432-450` (`test_pack_default_lane_goes_to_incoming_only`, `test_pack_dsa_lane_goes_to_incoming_dsa_only`, `test_duplicate_id_refused_across_lanes`). |
| C3 | Subcommand `status`: one-screen summary of queue and worker heartbeat | `scripts/worker/queue_tool.py:12` | `scripts/worker/queue_tool.py:449-514,806-807` | `scripts/worker/test_dsa_worker.py:451-520` | MATCH | SOURCED: Docstring at `scripts/worker/queue_tool.py:12` states: `"status  One-screen summary of the queue and the worker heartbeat."`<br>Code implementation: `cmd_status()` (`scripts/worker/queue_tool.py:487-514`) reads `heartbeat.json` via `read_heartbeat()` (`scripts/worker/queue_tool.py:452-459`, fresh threshold 180s); prints worker status or retired notice (`scripts/worker/queue_tool.py:491-496`); prints queue counts for waiting, running, replies, unverified (`scripts/worker/queue_tool.py:499-506`); invokes `print_dsa_status()` (`scripts/worker/queue_tool.py:465-485`) reporting `DSA-WORKER` lane status and heartbeats; prints recent verdicts (`scripts/worker/queue_tool.py:508-512`); exits 0 (`scripts/worker/queue_tool.py:513`). Tested in `scripts/worker/test_dsa_worker.py:451-520` (6 status tests covering dormant, active, aged heartbeats). |
| C4 | Subcommand `verify`: mechanical checks on finished replies; no ID verifies every reply without a verdict; explicit ID re-runs and overwrites verdict | `scripts/worker/queue_tool.py:13-15` | `scripts/worker/queue_tool.py:556-755,757-775,808-810` | `scripts/worker/QUEUE_TOOL_CHANGES.md:34-35,49-70` | MATCH | SOURCED: Docstring at `scripts/worker/queue_tool.py:13-15` states: `"verify [ID ...]  Mechanical checks on finished replies. No ID: every reply that has no verdict yet. An explicit ID always re-runs the checks and overwrites that id's verdict."`<br>Code implementation: `cmd_verify()` (`scripts/worker/queue_tool.py:757-775`) collects IDs without existing `.verdict.txt` when `args.ids` is empty (`scripts/worker/queue_tool.py:761-768`). Explicit ID verifies regardless of existing file and calls `write_atomic(done / f"{task_id}.verdict.txt", ...)` (`scripts/worker/queue_tool.py:753`). Exit codes: 0 for PASS, 1 for REVIEW, 2 for FAIL (`scripts/worker/queue_tool.py:773-774`). Verified in `scripts/worker/QUEUE_TOOL_CHANGES.md:34-35,49-70`. |
| C5 | Subcommand `lint`: check only that SCOPE/CREATE lines are bare paths | `scripts/worker/queue_tool.py:16` | `scripts/worker/queue_tool.py:181-192,428-444,803-805` | `scripts/worker/QUEUE_TOOL_CHANGES.md:28-33,72-76` | MATCH | SOURCED: Docstring at `scripts/worker/queue_tool.py:16` states: `"lint SPEC [SPEC ...]  Check only that SCOPE/CREATE lines are bare paths."`<br>Code implementation: `check_bare_path_line()` (`scripts/worker/queue_tool.py:181-192`) checks entries for spaces or parentheses; `parse_spec()` invokes it for `SCOPE` and `CREATE` headers (`scripts/worker/queue_tool.py:207,211`). `cmd_lint()` (`scripts/worker/queue_tool.py:428-444`) runs `parse_spec()` without packing or resolving paths on disk; exits 0 if all OK, 1 if any refused (`scripts/worker/queue_tool.py:444`). Documented and tested in `scripts/worker/QUEUE_TOOL_CHANGES.md:28-33,72-76`. |
| C6 | Subcommand `deploy`: copy worker scripts into `deploy/` for unattended installation | `scripts/worker/queue_tool.py:17-18` | `scripts/worker/queue_tool.py:53,779-793,811-812` | `scripts/worker/queue_tool.py:53,782-792` | MATCH | SOURCED: Docstring at `scripts/worker/queue_tool.py:17-18` states: `"deploy  Copy the worker scripts into deploy/. The NUC launcher installs a changed worker by itself within a minute."`<br>Code implementation: `DEPLOY_FILES = ("nuc-worker.ps1", "nuc-launcher.ps1", "setup-nuc.ps1")` (`scripts/worker/queue_tool.py:53`). `cmd_deploy()` (`scripts/worker/queue_tool.py:779-793`) copies each script from `scripts/worker/` to `Dumps/workers/NUC-QUEUE/deploy/` atomically; exits 0 on success, 1 on missing script (`scripts/worker/queue_tool.py:786,792`). |
| C7 | Spec file format & header schema: `TASK`, `SCOPE`, `OUTPUT`, `MODEL`, `OUTPUT_TOKENS`, `THINK`, `EXPECT`, `CREATE`, `OVERRIDE-CRITICAL` | `scripts/worker/queue_tool.py:20-32` | `scripts/worker/queue_tool.py:194-220,302-339,383-401` | `scripts/worker/test_dsa_worker.py:417-418`, `scripts/worker/QUEUE_TOOL_CHANGES.md:6-19` | MATCH | SOURCED: Docstring at `scripts/worker/queue_tool.py:20-32` documents header keys: `TASK`, `SCOPE`, `OUTPUT`, `MODEL` (default `qwen3-coder:30b`), `OUTPUT_TOKENS` (default `4096`), `THINK` (true/false), `EXPECT` (repeatable acceptance check), `CREATE` (repeatable bare path for new allowed files), `OVERRIDE-CRITICAL` (`approved-by-operator`).<br>Code implementation: `parse_spec()` (`scripts/worker/queue_tool.py:194-220`) parses headers and task body. `build_package()` (`scripts/worker/queue_tool.py:302-339,383-401`) validates critical paths, applies defaults, and structures the task JSON package. |
| C8 | Atomic write guarantee and formatting: UTF-8 without BOM, LF endings, write to temp name first and atomic replace | `scripts/worker/queue_tool.py:34-35` | `scripts/worker/queue_tool.py:140-145,419,650,663,753,789-790` | `scripts/worker/test_dsa_worker.py:435,442` | MATCH | SOURCED: Docstring at `scripts/worker/queue_tool.py:34-35` states: `"Every file this tool writes is UTF-8 without BOM, LF line endings, written to a temporary name first and then renamed, so a reader never sees half a file."`<br>Code implementation: `write_atomic()` (`scripts/worker/queue_tool.py:140-145`) writes to `.{name}.tmp` with `encoding="utf-8", newline="\n"` and uses `os.replace(tmp, path)`. Used in `cmd_pack` (`scripts/worker/queue_tool.py:419`), proposals and diffs (`scripts/worker/queue_tool.py:650,663`), verdicts (`scripts/worker/queue_tool.py:753`), and `cmd_deploy` (`scripts/worker/queue_tool.py:789-790`). |

---

## Detailed Audit of Commands, Reads/Writes, Exit Codes, and Creationflags

### 1. Commands Offered
- `pack SPEC [SPEC ...] [--lane {default,dsa}]`:
  - **Reads**: Spec file (`Path`), repo files named in `SCOPE:` header (`scripts/worker/queue_tool.py:222-283,286-295`), existing tasks in `incoming`, `claimed`, `done`, `incoming_dsa`, `claimed_dsa` to detect ID collisions (`scripts/worker/queue_tool.py:311-314`).
  - **Writes**: `Dumps/workers/NUC-QUEUE/incoming/<task_id>.task.json` (or `incoming_dsa/<task_id>.task.json` if `--lane dsa`) via `write_atomic()` (`scripts/worker/queue_tool.py:417-419`).
  - **Exit Codes**: Returns `0` if all specs packed successfully; `1` if any spec failed/refused (`scripts/worker/queue_tool.py:425`).
- `lint SPEC [SPEC ...]`:
  - **Reads**: Spec file (`Path`) (`scripts/worker/queue_tool.py:439`).
  - **Writes**: None (read-only validation).
  - **Exit Codes**: Returns `0` if all specs pass bare path checks; `1` if any contains prose or invalid headers (`scripts/worker/queue_tool.py:444`).
- `status`:
  - **Reads**: `Dumps/workers/NUC-QUEUE/heartbeat.json` and `heartbeat_dsa.json` (`scripts/worker/queue_tool.py:454-457,471,490`); directory file listings in `incoming`, `claimed`, `done`, `incoming_dsa`, `claimed_dsa` (`scripts/worker/queue_tool.py:468-469,499-502`); latest three `done/*.verdict.txt` files (`scripts/worker/queue_tool.py:508-510`).
  - **Writes**: None (console output only).
  - **Exit Codes**: Returns `0` (`scripts/worker/queue_tool.py:513`).
- `verify [ID ...]`:
  - **Reads**: `done/<id>.reply.json` (`scripts/worker/queue_tool.py:558-561`), package json `<id>.task.json` across queue dirs (`scripts/worker/queue_tool.py:522-527`), scope file hashes/content on disk (`scripts/worker/queue_tool.py:530-542,624-627`), existing target file contents (`scripts/worker/queue_tool.py:644`).
  - **Writes**: Proposal files `<target>.new` (or `done/<id>/<path>.new`) (`scripts/worker/queue_tool.py:646-650`), diff file `done/<id>.diff` (`scripts/worker/queue_tool.py:662-663`), verdict file `done/<id>.verdict.txt` (`scripts/worker/queue_tool.py:753`).
  - **Exit Codes**: Returns `0` if worst verdict is PASS, `1` if REVIEW, `2` if FAIL (`scripts/worker/queue_tool.py:773-774`).
- `deploy`:
  - **Reads**: `scripts/worker/{nuc-worker.ps1, nuc-launcher.ps1, setup-nuc.ps1}` (`scripts/worker/queue_tool.py:53,782-785`).
  - **Writes**: `Dumps/workers/NUC-QUEUE/deploy/{nuc-worker.ps1, nuc-launcher.ps1, setup-nuc.ps1}` atomically (`scripts/worker/queue_tool.py:787-790`).
  - **Exit Codes**: Returns `0` on success; `1` if any deploy source script is missing (`scripts/worker/queue_tool.py:786,792`).

### 2. Verification of `creationflags` Edit (Commit `c0354cca92cf`)
- Commit `c0354cca92cf` modified two `subprocess.run` calls inside `verify_one()` (`scripts/worker/queue_tool.py:677,706`):
  1. `py_compile` check:
     ```python
     r = subprocess.run(
         [sys.executable, "-m", "py_compile", str(tmp_py)],
         capture_output=True, text=True, timeout=30,
         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
     )
     ```
  2. `unittest` check:
     ```python
     r = subprocess.run(
         [sys.executable, "-m", "unittest", stem],
         cwd=str(tdp), capture_output=True, text=True, timeout=120,
         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
     )
     ```
- **Behavioural Analysis**:
  - `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)` suppresses console window creation on Windows when spawning background test/compile subprocesses during verification.
  - On non-Windows platforms, `getattr(subprocess, "CREATE_NO_WINDOW", 0)` evaluates to `0`, leaving behavior unmodified.
  - Standard streams, timeouts, return codes, and stdout/stderr capture remain identical.
  - All 37 existing tests in `scripts/worker/test_dsa_worker.py` (which includes `TestQueueTool`) continue to pass completely.
  - SOURCED finding: The `creationflags` edit changed zero functional logic, outputs, exit codes, or queue state handling.

---

## Summary of Findings

- Total clauses audited: 8 (SOURCED: 8 clauses in `scripts/worker/queue_tool.py:2-36`)
- **MATCH**: 8 (SOURCED: 8 rows verified against `scripts/worker/queue_tool.py` and `scripts/worker/test_dsa_worker.py`)
- **DIFF**: 0
- **NOT_IN_DATA**: 0
