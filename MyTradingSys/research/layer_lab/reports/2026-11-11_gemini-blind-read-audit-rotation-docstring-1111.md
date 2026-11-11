Counts: MATCH: 6, DIFF: 0, NOT_IN_DATA: 0

# Gemini Blind Read of `scripts/worker/audit_rotation.py` Against Its Docstring and Test Suite

- **Card ID**: `gemini-blind-read-audit-rotation-docstring-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Scope In Read**:
  - `scripts/worker/audit_rotation.py` (read)
  - `scripts/worker/test_audit_rotation.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-audit-rotation-docstring-1111.md` (new)
- **Scope Out**: No edit to source files; no live-tree edit, no deploy, no `.secrets` or `.env` read; read-only audit.
- **Commit Audit**: Commit `c0354cca92cf` updated `scripts/worker/audit_rotation.py:101` in `pack_one()` to add `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)` on the unattended `subprocess.run` invocation of `queue_tool.py pack`. All 21 tests in `scripts/worker/test_audit_rotation.py` pass cleanly (`21 passed in 0.17s`).

---

## Verification Table (Docstring Clauses)

The module docstring in `scripts/worker/audit_rotation.py:2-7` reads:
```python
"""T056 Qwen-audit rotation script, backfill half.

Packs least-recently-audited targets from audit_targets.json as NUC queue tasks,
but only when the queue is currently idle (zero waiting tasks). The --t0 flag
delegates to audit_t0_checks.py module (built separately, T056 spec 095).
"""
```

| Clause ID | Clause Statement / Description | Docstring Citation | Code Implementation (`scripts/worker/audit_rotation.py`) | Test Coverage (`scripts/worker/test_audit_rotation.py`) | Status | Audit Findings & File:Line Quotations |
|---|---|---|---|---|---|---|
| C1 | Purpose: T056 Qwen-audit rotation script, backfill half | `scripts/worker/audit_rotation.py:2` | `scripts/worker/audit_rotation.py:78,108-121,134` | `scripts/worker/test_audit_rotation.py:1-4,166-200` | MATCH | SOURCED: Docstring at `scripts/worker/audit_rotation.py:2` states `T056 Qwen-audit rotation script, backfill half.` Implementation at `scripts/worker/audit_rotation.py:78` specifies `MODEL: qwen3-coder:30b`, `cmd_backfill()` at lines 108-121, and `--backfill` CLI flag at line 134. Test suite module docstring at `scripts/worker/test_audit_rotation.py:1-4` cites `094-audit-rotation-backfill.md (T056)`, and tests `test_cmd_backfill_*` at lines 166-200 verify backfill behavior. |
| C2 | Packs least-recently-audited targets from `audit_targets.json` | `scripts/worker/audit_rotation.py:4` | `scripts/worker/audit_rotation.py:18,44-52,56-63,113` | `scripts/worker/test_audit_rotation.py:26-54,58-80` | MATCH | SOURCED: Docstring at `scripts/worker/audit_rotation.py:4` states `Packs least-recently-audited targets from audit_targets.json`. Registry path defined at `scripts/worker/audit_rotation.py:18` (`REGISTRY_PATH = REPO / "scripts" / "worker" / "audit_targets.json"`). `load_registry()` and `save_registry()` at lines 44-52 handle I/O. `targets_due()` at lines 56-63 sorts targets where `last_audited is None` returns `(0, 0)` first, else `(1, la)` ascending. Tested in `scripts/worker/test_audit_rotation.py:26-54` (registry load/save roundtrip, atomic save) and lines 58-80 (`test_targets_due_never_audited_sorts_first`, `test_targets_due_does_not_mutate_registry`, `test_targets_due_n_larger_than_list_returns_all`). |
| C3 | Targets are packed as NUC queue tasks | `scripts/worker/audit_rotation.py:4` | `scripts/worker/audit_rotation.py:19-21,75-106` | `scripts/worker/test_audit_rotation.py:102-163` | MATCH | SOURCED: Docstring at `scripts/worker/audit_rotation.py:4` states `Packs ... as NUC queue tasks`. Constants at `scripts/worker/audit_rotation.py:19-21` point to `Dumps/workers/NUC-QUEUE` and `SPECS_DIR = QUEUE / "specs"`. `build_spec_text()` at lines 75-78 formats the task spec. `pack_one()` at lines 94-106 writes the spec file to `SPECS_DIR` and invokes `queue_tool.py pack <path>`. Tested in `scripts/worker/test_audit_rotation.py:102-117` (`test_build_spec_text_*`) and lines 136-163 (`test_pack_one_writes_spec_file`, `test_pack_one_false_on_nonzero_returncode`). |
| C4 | Packs only when the queue is currently idle (zero waiting tasks) | `scripts/worker/audit_rotation.py:5` | `scripts/worker/audit_rotation.py:65-73,109-112` | `scripts/worker/test_audit_rotation.py:84-98,167-178` | MATCH | SOURCED: Docstring at `scripts/worker/audit_rotation.py:5` states `but only when the queue is currently idle (zero waiting tasks)`. `queue_waiting_count()` at `scripts/worker/audit_rotation.py:65-73` counts `*.task.json` in `incoming` and `claimed` dirs. `cmd_backfill()` at lines 109-112 checks `waiting = queue_waiting_count(); if waiting > 0: print(...); return 0`. Tested in `scripts/worker/test_audit_rotation.py:84-98` (missing dirs return 0; counts incoming and claimed) and lines 167-178 (`test_cmd_backfill_skips_when_waiting`). |
| C5 | The `--t0` flag is supported | `scripts/worker/audit_rotation.py:5` | `scripts/worker/audit_rotation.py:123,135,144-145` | `scripts/worker/test_audit_rotation.py:203-216` | MATCH | SOURCED: Docstring at `scripts/worker/audit_rotation.py:5` specifies `The --t0 flag`. CLI parser at `scripts/worker/audit_rotation.py:135` adds `p.add_argument("--t0", action="store_true")`, and lines 144-145 invoke `cmd_t0(reg)` when `--t0` is passed. Tested in `scripts/worker/test_audit_rotation.py:203-216` verifying delegation to `audit_t0_checks.run_t0_checks()`. |
| C6 | `--t0` delegates to `audit_t0_checks.py` module (built separately, T056 spec 095) | `scripts/worker/audit_rotation.py:5-6` | `scripts/worker/audit_rotation.py:123-130` | `scripts/worker/test_audit_rotation.py:203-216` | MATCH | SOURCED: Docstring at `scripts/worker/audit_rotation.py:5-6` states `delegates to audit_t0_checks.py module (built separately, T056 spec 095)`. `cmd_t0()` at `scripts/worker/audit_rotation.py:123-130` imports `audit_t0_checks` and calls `audit_t0_checks.run_t0_checks()`, returning 1 if the module is missing (`"T0 checks: audit_t0_checks.py not present yet (see 095)"`). Tested in `scripts/worker/test_audit_rotation.py:203-207` (`test_cmd_t0_returns_1_when_sibling_module_missing`) and lines 209-216 (`test_cmd_t0_delegates_to_run_t0_checks`). |

---

## Detailed Rotation Order Audit

- **Sort Order**:
  - `scripts/worker/audit_rotation.py:56-63` defines `targets_due(reg: dict, n: int) -> list`.
  - Sort key function `sort_key(target)`:
    - If `target.get("last_audited") is None`: returns `(0, 0)`.
    - Else: returns `(1, la)` where `la` is the ISO timestamp string.
  - Slices the sorted list to `[:n]`, where `BACKFILL_BATCH = 6` (`scripts/worker/audit_rotation.py:22,113`).
- **Audit Findings**:
  - Unaudited targets (`last_audited` is `None`) always sort first.
  - Among audited targets, older ISO timestamps sort earlier (least-recently audited first).
  - Matches docstring claim "Packs least-recently-audited targets".
  - Tested in `scripts/worker/test_audit_rotation.py:58-66` (`test_targets_due_never_audited_sorts_first`).

---

## Detailed Records & State Audit

- **What It Records**:
  - Upon successful pack (`success = pack_one(target)` returns `True`):
    - Sets `target["last_audited"] = utc_now_stamp()` (`scripts/worker/audit_rotation.py:116`).
    - Timestamp format generated by `utc_now_stamp()`: `%Y-%m-%dT%H:%M:%SZ` (`scripts/worker/audit_rotation.py:54`).
    - Prints `AUDITED {target['id']}` (`scripts/worker/audit_rotation.py:117`).
    - Persists registry atomically via temporary file `.{name}.tmp` and `os.replace` (`scripts/worker/audit_rotation.py:47-51`).
  - Upon failed pack (`pack_one(target)` returns `False`):
    - Prints `FAILED  {target['id']}` (`scripts/worker/audit_rotation.py:119`).
    - Does NOT mutate `target["last_audited"]` (`scripts/worker/test_audit_rotation.py:192-199`).
  - Spec File Output:
    - Writes Markdown task specification to `Dumps/workers/NUC-QUEUE/specs/{id}-audit-{slug}.md` (`scripts/worker/audit_rotation.py:80-100`).
    - Spec ID starts at 900 or increments past existing `9*-audit-*.md` (`scripts/worker/audit_rotation.py:81-92`).
    - Spec body includes `TASK: Audit ({template}) -- {hint}`, `SCOPE: {paths}`, `OUTPUT`, `OUTPUT_TOKENS: 1536`, `MODEL: qwen3-coder:30b`, `NOTE: {note}`, and `REPLY_FORMAT` (`scripts/worker/audit_rotation.py:75-78`).

---

## Exit Codes Audit

- `scripts/worker/audit_rotation.py:132-146` (`main(argv=None) -> int`):
  - Exit code `2`: When neither `--backfill` nor `--t0` is provided (`scripts/worker/audit_rotation.py:137-139`; verified by `test_main_no_flags_returns_2` in `scripts/worker/test_audit_rotation.py:220-223`).
  - Exit code `0`: When `--backfill` runs successfully (whether queue was idle or skipped due to waiting tasks) (`scripts/worker/audit_rotation.py:112,121,143,146`; verified by `test_cmd_backfill_skips_when_waiting`, `test_cmd_backfill_packs_due_targets_and_updates_last_audited`, and `test_main_backfill_flag_invokes_cmd_backfill`).
  - Exit code `1`: When `--t0` is passed but `audit_t0_checks.py` cannot be imported (`scripts/worker/audit_rotation.py:127-129`; verified by `test_cmd_t0_returns_1_when_sibling_module_missing`).
  - Exit code `<rc>`: When `--t0` is passed and `audit_t0_checks` is present, returns the integer return code from `audit_t0_checks.run_t0_checks()` (`scripts/worker/audit_rotation.py:130,145,146`; verified by `test_cmd_t0_delegates_to_run_t0_checks`).

---

## Creationflags Edit Audit

- **Commit**: `c0354cca92cf` ("no-window flag on 35 unattended subprocess calls outside scripts/dev (q-5aeda0)")
- **File & Line**: `scripts/worker/audit_rotation.py:101`
- **Diff**:
  ```diff
  -    result = subprocess.run([sys.executable, str(QUEUE_TOOL), "pack", str(path)], capture_output=True, text=True)
  +    result = subprocess.run([sys.executable, str(QUEUE_TOOL), "pack", str(path)], capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
  ```
- **Audit Assessment**:
  - Safe cross-platform implementation: `getattr(subprocess, "CREATE_NO_WINDOW", 0)` evaluates to `0x08000000` on Windows and fallback `0` on non-Windows platforms where `CREATE_NO_WINDOW` is not defined.
  - Prevents console popup flashing when running unattended subprocess calls on Windows.
  - Does not alter command arguments, stdout/stderr capture, returncode handling, or control flow.
  - Test suite passes with 0 regressions.
