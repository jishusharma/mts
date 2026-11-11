COUNTS: MATCH=5 DIFF=0 NOT_IN_DATA=0

# Independent Gemini Blind Read: One-Gate-Pool-Per-Machine Slots (c637bfa4e)

- **Card**: `gemini-blind-read-gate-pool-slots-1111`
- **Date**: 2026-11-11 UTC
- **Reader**: Gemini (`gemini-3.8-flash-low`, JIS-NUC throwaway worktree `gemini-q/gemini-blind-read-gate-pool-slots-1111`)
- **Scope In (read-only)**:
  - `scripts/dev/sync.py` (`host_gate_slots_dir`, `gate_slot_factory`, `_log_wait` and callers; read)
  - `scripts/dev/run_all_tests.py` (`run_plan` slot argument, `gate_slot_factory`; read)
  - `scripts/dev/supervisor.py` (the slot use, `_gate_slots_raw`; read)
  - `MyTradingSys/system/GATE_SPEED.md` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-gate-pool-slots-1111.md` (this report)
- **Scope Out Respected**:
  - No edit to the source files; no live-tree edit, no deploy, no `.secrets` or `.env` read; read-only audit.
  - Zero push; no `sync.py ship`.
- **Target Clauses**:
  1. The slots dir is per machine, not per worktree
  2. One ship holds one slot for its whole gate
  3. A waiting ship appends to wait.log
  4. A slot held by a dead process is reclaimed
  5. GATE_SPEED.md describes the same behaviour

---

## 1. Clause Audit Table

| # | Clause / Claim Description | Status | Target Code & Doc References (`file:line` & Quote) | Audit Analysis & Verification Notes (SOURCED / OURS) |
|---|---|---|---|---|
| 1 | The slots dir is per machine, not per worktree | `MATCH` | `scripts/dev/sync.py:293` (`GATE_POOL = "gate-slots" # ARCH_REVIEW row 3: the ONE gate queue per machine`); `scripts/dev/sync.py:322-333` (`def host_gate_slots_dir(name=GATE_POOL, repo=None): ... base = Path(tempfile.gettempdir()) / "mts_gate_slots" ... d = base / name`); `scripts/dev/supervisor.py:242-244` (`def gate_slots_dir(repo: Path = REPO) -> Path: ... return sync.gate_slot(repo)._dir()`) | SOURCED (`scripts/dev/sync.py:322-333`, `scripts/dev/supervisor.py:242-244`): `host_gate_slots_dir` resolves to `Path(tempfile.gettempdir()) / "mts_gate_slots" / name` (defaulting to name `GATE_POOL = "gate-slots"`). Because it is rooted in system `tempfile.gettempdir()`, all git worktrees and clones across the entire host resolve to the exact same directory path on disk regardless of worktree path or repository checkout location. Overridable via `MTS_GATE_SLOTS_DIR` only for test isolation. |
| 2 | One ship holds one slot for its whole gate | `MATCH` | `scripts/dev/run_all_tests.py:791` (`with (slot() if slot and todo else contextlib.nullcontext()): # one slot for the whole ship; a precheck failure frees it at once`); `scripts/dev/run_all_tests.py:804` (`with (slot() if slot else contextlib.nullcontext()): run_steps(todo, jobs, fail_fast)`); `scripts/dev/run_all_tests.py:809-813` (`def gate_slot_factory(mode): ... return lambda: sync.gate_slot(REPO, slots=sync.GATE_SLOTS, name=sync.GATE_POOL, mode=mode)`); `scripts/dev/run_all_tests.py:1418` (`slot = gate_slot_factory("fast" if fast_applied else "full") # one pool for every mode (ARCH_REVIEW row 3)`) | SOURCED (`scripts/dev/run_all_tests.py:791,804,809-813,1418`): `main` instantiates a single slot context manager via `gate_slot_factory("fast" if fast_applied else "full")` and passes `slot` to `run_plan`. When `precheck` runs, `with (slot() if slot and todo else contextlib.nullcontext()):` encloses both the precheck steps and the main steps in a single context block, so a ship holds exactly one slot for the entire duration of precheck + main phase, releasing it on exit or failure. In non-precheck runs, `with (slot() if slot else contextlib.nullcontext()): run_steps(todo, jobs, fail_fast)` similarly holds the slot for the whole gate run. |
| 3 | A waiting ship appends to wait.log | `MATCH` | `scripts/dev/sync.py:354-373` (`def _log_wait(self, d): ... log = d.parent / "wait.log" ... row = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "host": socket.gethostname(), "repo": Path(str(self.repo)).name, "pid": os.getpid(), "mode": self.mode, "wait_s": round(self.wait_s, 2), "busy": self.busy_first} ... fd = os.open(str(log), os.O_CREAT \| os.O_APPEND \| os.O_WRONLY) ... os.write(fd, (json.dumps(row) + "\n").encode("utf-8"))`); `scripts/dev/sync.py:417` (`self.wait_s = time.monotonic() - start; self._log_wait(d)`) | SOURCED (`scripts/dev/sync.py:354-373,417`): In `gate_slot.__enter__`, upon acquiring a slot, `self.wait_s` is calculated and `self._log_wait(d)` is called. `_log_wait` constructs a JSON payload containing timestamp `ts`, `host`, `repo`, `pid`, `mode`, `wait_s`, and `busy`, opening `<slots base>/wait.log` (`d.parent / "wait.log"`) with `os.O_CREAT | os.O_APPEND | os.O_WRONLY` to append the record atomically. It also caps log size to `WAIT_LOG_KEEP = 200` lines, swallowing any exception so logging never breaks a gate. |
| 4 | A slot held by a dead process is reclaimed | `MATCH` | `scripts/dev/sync.py:387-399` (`raw = p.read_text().strip() ... owner = int(raw) if raw else (0 if time.time() - p.stat().st_mtime > 10 else None) ... if owner is not None and not self.alive(owner): print(f"gate slot {i}: owner PID {owner} is dead, reclaiming"); try: p.unlink() except OSError: pass continue`); `scripts/dev/supervisor.py:263-271` (`raw = p.read_text(encoding="utf-8").strip() ... owner = int(raw) if raw else (0 if time.time() - p.stat().st_mtime > 10 else None) ... elif owner > 0 and pid_alive(owner): busy += 1; pids.append(owner)`) | SOURCED (`scripts/dev/sync.py:387-399`, `scripts/dev/supervisor.py:263-271`): When attempting to acquire slot file `slot-i`, if the file already exists (`FileExistsError`), `sync.py` reads the PID of the owner. If `owner is not None and not self.alive(owner)`, it unlinks `slot-i` and loops to immediately re-attempt `os.open(..., O_CREAT | O_EXCL)`. Mid-write empty files (`owner = None`) are respected unless older than 10 s (`owner = 0`, reclaimed as dead). In `supervisor.py:269-270`, slots with non-alive PIDs are not counted as busy. |
| 5 | GATE_SPEED.md describes the same behaviour | `MATCH` | `MyTradingSys/system/GATE_SPEED.md:16-17` (`D1 ... inside the one gate slot (X3)`; `D2 ... run_all_tests takes the one gate slot once, around precheck + main (X3)`); `MyTradingSys/system/GATE_SPEED.md:56-60` (`X3 (ARCH_REVIEW row 3, 2026-11-11; reverses the 10-24 own-pool rule) ONE gate pool per machine, gate-slots (GATE_SLOTS=2): fast, full, precheck and deploy gates all take from it, once per ship (run_all_tests.gate_slot_factory), so at most 2 gates run at once, not 6 ... Every acquire appends one JSON line {ts,host,repo,pid,mode,wait_s,busy} to <tmp>/mts_gate_slots/wait.log ... An empty slot file is its creator mid-write (busy, not a dead owner 0) unless older than 10 s.`) | SOURCED (`MyTradingSys/system/GATE_SPEED.md:16-17,56-60`): `GATE_SPEED.md` under rows D1, D2 and section X3 explicitly specifies: (1) ONE gate pool per machine (`gate-slots`, `GATE_SLOTS=2`), (2) single slot held once per ship around precheck + main via `run_all_tests.gate_slot_factory`, (3) every acquire appending JSON `{ts,host,repo,pid,mode,wait_s,busy}` to `<tmp>/mts_gate_slots/wait.log` (last 200 lines), and (4) handling empty slot files mid-write vs older than 10 s dead reclamation. This matches the codebase implementation in `sync.py`, `run_all_tests.py`, and `supervisor.py` exactly. |

---

## 2. Summary & Audit Conclusions

- **Total Clauses Checked**: 5
- **Counts**: `MATCH: 5`, `DIFF: 0`, `NOT_IN_DATA: 0` (Sum: 5)
- **Result**: The machine-wide gate pool implementation introduced in `c637bfa4e` faithfully realizes all five specifications: host-wide scope via tempdir, unified single-slot lifetime per ship across precheck and main phases, structured JSON wait logging to `wait.log`, dead process slot recovery with mid-write safety, and exact synchronization with `GATE_SPEED.md`.
