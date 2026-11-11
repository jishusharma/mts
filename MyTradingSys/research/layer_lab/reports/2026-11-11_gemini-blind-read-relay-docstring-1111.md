Counts: MATCH: 7, DIFF: 0, NOT_IN_DATA: 0

# Gemini Blind Read of `scripts/sched/relay.py` Against Its Docstring

- **Card ID**: `gemini-blind-read-relay-docstring-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Scope In Read**:
  - `scripts/sched/relay.py` (read)
  - `MyTradingSys/tests/test_relay.py` (read)
  - `MyTradingSys/tests/test_relay_tick.py` (read)
  - `MyTradingSys/tests/test_relay_queue.py` (read)
  - `MyTradingSys/tests/test_relay_prompts.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-relay-docstring-1111.md` (new)
- **Scope Out**: No edit to source files; no live-tree edit, no deploy, no `.secrets` or `.env` read; read-only audit.
- **Commit Audit**: Commit `c0354cca92cf` (11 `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)` edits in `scripts/sched/relay.py` lines 227, 228, 236, 251, 259, 382, 385, 414, 568, 769, 865) changed no runtime logic or behaviour; all 79 tests across the 4 relay test suites pass without regression (`79 passed in 60.21s`).

---

## Verification Table

| Clause ID | Clause Description | Docstring Citation | Code Implementation (`scripts/sched/relay.py`) | Test Coverage (`MyTradingSys/tests/`) | Status | Audit Findings & File:Line Quotations |
|---|---|---|---|---|---|---|
| C1 | Header forms go and stop with depth and id | `scripts/sched/relay.py:8` | `scripts/sched/relay.py:65,201-206` | `MyTradingSys/tests/test_relay.py:65-73,100,110-115` | MATCH | SOURCED: Docstring at `scripts/sched/relay.py:8` specifies `<!-- relay: go depth=3 id=a1b2c3d4 --> or <!-- relay: stop reason=<text> depth=3 id=a1b2c3d4 -->`. Regex `HDR` defined at `scripts/sched/relay.py:65` (`r"<!-- relay: (go|stop)(?: reason=([^>]*?))? depth=(\d+) id=([0-9a-f]+) -->"`). Implementation in `cmd_handoff` at `scripts/sched/relay.py:201-206` constructs `<!-- relay: %s%s depth=%d id=%s -->`. Tested in `MyTradingSys/tests/test_relay.py:65-73` (go with depth/id), line 100 (stop with reason/depth/id), lines 110-115 (depth increment & reset). |
| C2 | Kick is IDLE on a stop flag | `scripts/sched/relay.py:9` | `scripts/sched/relay.py:280-282` | `MyTradingSys/tests/test_relay.py:105-106` | MATCH | SOURCED: Docstring at `scripts/sched/relay.py:9` specifies ``kick` stays IDLE on: stop flag`. Implementation at `scripts/sched/relay.py:280-282` (`flag = home() / "mts-relay-stop"; if flag.exists(): return idle("operator stop flag")`). Tested in `MyTradingSys/tests/test_relay.py:105-106` (`run(self.home, "stop", "weekly budget"); self.assertIn("stop flag", self.kick().stdout)`). |
| C3 | IDLE on no header or a stop header | `scripts/sched/relay.py:9` | `scripts/sched/relay.py:283-288` | `MyTradingSys/tests/test_relay.py:98-103`, `MyTradingSys/tests/test_relay_tick.py:90,147` | MATCH | SOURCED: Docstring at `scripts/sched/relay.py:9` specifies `IDLE on: ... / no header / header says stop`. Implementation at `scripts/sched/relay.py:283-288` (`if h is None: return idle("no relay header in handoff") ... if state != "go": return idle("handoff says stop: " + (reason or "no reason"))`). Tested in `MyTradingSys/tests/test_relay.py:98-103` (`self.assertIn("no relay header", self.kick().stdout)` and `self.assertIn("queue empty", r.stdout)`), and `MyTradingSys/tests/test_relay_tick.py:90,147`. |
| C4 | IDLE when no task this host can run | `scripts/sched/relay.py:9` | `scripts/sched/relay.py:303-311` | `MyTradingSys/tests/test_relay.py:303-316,368-372,381-385` | MATCH | SOURCED: Docstring at `scripts/sched/relay.py:9` specifies `IDLE on: ... / no task this host can run`. Implementation at `scripts/sched/relay.py:303-311` checks `lint_file` (`HOST_ERR`: `idle("no unblocked task for host ...")`, `NONE_ERR`: `idle("no unblocked open task in handoff ...")`), and checks lane-only work (`idle("no Claude-runnable task: open work is on lane CODEX ... / DSA ...")`). Tested in `MyTradingSys/tests/test_relay.py:315,370` (`IDLE no unblocked task for host JIS-NUC`) and line 383 (`IDLE no unblocked open task`). |
| C5 | IDLE when a launch is younger than ACTIVE_MIN | `scripts/sched/relay.py:9,52` | `scripts/sched/relay.py:312-316` | `MyTradingSys/tests/test_relay.py:51-53,88-90`, `MyTradingSys/tests/test_relay_tick.py:109` | MATCH | SOURCED: Docstring at `scripts/sched/relay.py:9` specifies `IDLE on: ... / a launch younger than ACTIVE_MIN`. Implementation at `scripts/sched/relay.py:52` defines `ACTIVE_MIN = 45`. Lines 312-316 check `prev = read_lock() ... if age < timedelta(minutes=ACTIVE_MIN): return idle("a launch %d min ago, chain is moving" % (age.total_seconds() // 60))`. Tested in `MyTradingSys/tests/test_relay.py:51-53` and lines 88-90 (`self.assertIn("chain is moving", moving.stdout)`), and `MyTradingSys/tests/test_relay_tick.py:109`. |
| C6 | IDLE for the same handoff id under STALE_H | `scripts/sched/relay.py:9-10,53` | `scripts/sched/relay.py:317-318` | `MyTradingSys/tests/test_relay.py:91-95` | MATCH | SOURCED: Docstring at `scripts/sched/relay.py:9-10` specifies `IDLE on: ... / the SAME handoff id launched under STALE_H ago (a session is on it)`. Implementation at `scripts/sched/relay.py:53` defines `STALE_H = 1`. Lines 317-318 check `if prev.get("id") == hid and age < timedelta(hours=STALE_H): return idle("handoff %s launched %d min ago, session still on it" % (hid, age.total_seconds() // 60))`. Tested in `MyTradingSys/tests/test_relay.py:91-95` (`self.assertIn("session still on it", working.stdout)`, and retry succeeds at 70 min > STALE_H). |
| C7 | IDLE when another host wrote the handoff under --peer-quiet-min | `scripts/sched/relay.py:10,25-27` | `scripts/sched/relay.py:289-293` | `MyTradingSys/tests/test_relay.py:255-275` | MATCH | SOURCED: Docstring at `scripts/sched/relay.py:10` specifies `IDLE on: ... / another host wrote the handoff under --peer-quiet-min ago`. Implementation at `scripts/sched/relay.py:289-293` checks `who, when = handoff_owner(a, hid); if who != "unknown" and not hosts.same_host(who, host()) and when is not None and now() - when < timedelta(minutes=a.peer_quiet_min): return idle("peer %s wrote handoff %s %d min ago (< %d): its chain is moving, this host stays out" ...)`. Tested in `MyTradingSys/tests/test_relay.py:255-275` (verifying peer handoff quiet window, same-host bypass, and expired window). |

---

## Handoff & Unlock Behaviour Verification

- **Docstring**: Lines 4-5 and 11, 19 state:
  - `The ending session ships its work, calls handoff (stamps NEXT_SESSION.md with a relay header), ships that, and runs unlock so the next tick starts the next handoff at once.`
  - `The lock is keyed by handoff id and freed by unlock, not by a clock alone.`
  - `python scripts/sched/relay.py unlock: free the launch lock (last action of a KICK session, not after --stop)`
- **Implementation**:
  - `cmd_handoff` (`scripts/sched/relay.py:171-210`): Stamps `HDR` with new `uuid.uuid4().hex[:8]` id and increments depth, writes to `NEXT_SESSION.md`, appends to `relay_runs.jsonl`.
  - `cmd_kick` (`scripts/sched/relay.py:319-322`): Writes lock file `mts-relay-lock.json` containing `{"utc": now().strftime(TS), "id": hid, "depth": depth}`.
  - `cmd_unlock` (`scripts/sched/relay.py:213-220`): Unlinks `mts-relay-lock.json` (`lock.unlink(missing_ok=True)`), freeing the launch lock immediately.
- **Test Coverage**:
  - `MyTradingSys/tests/test_relay.py:45-64` (`test_unlock_lets_the_next_handoff_start_at_once`) verifies that after `unlock`, the next handoff starts at once without waiting for clock expiry, and that unlocking when no lock is present exits 0.

---

## Commit `c0354cca92cf` Creationflags Verification

- 11 unattended subprocess calls in `scripts/sched/relay.py` were updated to pass `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)`:
  - Lines 227, 228 (`header_from_git`: `git fetch`, `git show`)
  - Line 236 (`text_from_git`: `git show`)
  - Lines 251, 259 (`handoff_owner`: `git show`, `git log`)
  - Lines 382, 385 (`lane_rows`: `git grep`, `git show`)
  - Line 414 (`codex_look`: `python codex_run.py status`)
  - Line 568 (`_sh`: helper running arbitrary subprocess arguments)
  - Line 769 (`prompt_drift`: `git show`)
  - Line 865 (`cmd_tick`: `git show`)
- **Impact Analysis**:
  - `getattr(subprocess, "CREATE_NO_WINDOW", 0)` evaluates to `0x08000000` on Windows and `0` on non-Windows platforms.
  - It suppresses console window creation for background scheduled tasks on Windows without altering process arguments, stdin/stdout/stderr capture, return codes, timeouts, or environment variables.
  - Behavioral invariance confirmed: all 79 unit tests in `test_relay.py`, `test_relay_tick.py`, `test_relay_queue.py`, and `test_relay_prompts.py` pass cleanly.

---

## Summary of Findings

- SOURCED: Total clauses audited = 7
- **MATCH**: 7
- **DIFF**: 0
- **NOT_IN_DATA**: 0
- The implementation of `scripts/sched/relay.py` matches all 7 docstring clauses, handoff and unlock semantics are fully validated, and the 11 `CREATE_NO_WINDOW` edits introduced zero behavioral drift.
