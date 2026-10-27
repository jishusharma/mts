# One-shot successor wake (4b2) — design for review (2026-10-27, Lead/admin, JIS-NUC login B)

One line per section. Corrections go here; the task card (`tasks.py brief one-shot-successor-wake-task-4b2-no-human`) ref's this file.

## Problem
- Two regimes. **Alive session** on another host: already solved — `mts_signal.py` ping/broadcast lands on its next prompt; zero human.
- **Dead/hung session** (ENDED, finished, or parked on a prompt) while the app is open (or closed): nothing reaches it — a signal needs a live turn to inject into. The only policy-allowed boot of a new session is the 4b2 one-time task (SCHEDULING_POLICY.md §4b2), and even that only helps if the ENDED session *recorded* it. C's 2026-10-27 ENDED handover recorded no task-id → JIS-NB is parked, only a human click starts it. That click is exactly what rolling sessions must not need.
- Stuck sessions (hung on a question / permission click): no revival is in scope. The fix is a fresh successor; the stuck one stays as-is.

## Solution: one script, one line
On the machine that needs waking (C on JIS-NB, A on the laptop — the task registers where it runs, by design, no cross-host remote gate):

```
python scripts/dev/successor_wake.py --login C            # fires now
python scripts/dev/successor_wake.py --login C --at 2026-10-27T20:05Z   # fires at 4b2 fireAt
```

What `successor_wake.py` does (all local, no network, no new deps; pattern = `nuc_wake.py` minus the SSH gate):
1. Write the successor prompt (default = the handover successor line `You are Supervisor. Login <L>. Continue from MyTradingSys/system/handover/SUPERVISOR_<L>.md` + "never ask, take the defaults"; `--prompt-file` overrides).
2. Register a **one-time** task `MTS-SuccWake-<login>` (existing → `-Force`, i.e. idempotent):
   - principal: Interactive, current user (no password needed — same trick as `nuc_wake.py` / `SCHEDULING_POLICY §4c`).
   - action: `conhost --headless` → `claude -p --model claude-sonnet-5-5` in the MTS checkout with that prompt, then **self-unregister** in the same command line (`Unregister-ScheduledTask MTS-SuccWake-<login>`). Self-unregister *is* the 4b2 rule "must be unregistered after it fires".
   - log to `F:/MTS/succ_wake/<login>/out.log` so a human can verify without reading the app.
3. Append one line to `handover/SUPERVISOR_<L>.md`: `Successor task: MTS-SuccWake-C fireAt <iso> (4b2)` — the 4b2 rule "the creating session records the task id in its hand-over".
4. Print one confirmation line.

Flags: `--at` (future only, fail closed on past), `--model` (default sonnet — cost rule), `--prompt-file`, `--cwd` (default: the checkout it runs from; fail closed if not an MTS checkout), `--dry` (print the PowerShell, run nothing).

## Auto wiring (the rolling guarantee)
`supervisor.py handover` (`supervisor.py:1518`, ENDED heartbeat at `:1547`): after writing the handover and sending `mode=ENDED`, call `successor_wake.py` register for the same login. `--no-wake` stays as the manual opt-out. ENDED then always self-boots the next link: task → successor supervisor → its ENDED → next task. Human input only on exceptions (no CLI login on that machine, checkout missing — both visible in `who`'s missing heartbeat and the out.log).

## Budget-aware fireAt (operator d-47, 2026-10-27: "depending of the session usage limits runs has to continue. keep distributing load.")
- At handover, read the pacer (`supervisor.py` slot bands): slots ≥ 1 → fireAt = now; STOP (5h ≥ 80 / weekly at cap) → fireAt = next 5-hour or weekly reset (the `reset=` value already on the BUDGET heartbeat lines).
- The successor boots inside a window where the pacer has room, so ready cards drain as each reset opens; per-station pacing (the existing pacer) keeps load distributed across A/B/C — the chain adds no re-balancer, it just keeps each station's loop alive across limits.

## "Something exists but is not wired" — what we reuse (operator 2026-10-27)
All three pieces exist; only the connector is missing:
1. **The chain mechanism**: 4b2 one-time task proven end-to-end on 2026-10-26 (`chain_test_proof.txt`, commit `ce8194ba2`: task fired, session shipped, task deleted).
2. **The registration pattern**: `nuc_wake.py` (Interactive-principal one-shot task, self-unregister, `conhost --headless`, `--dry` golden output).
3. **The hook point**: `supervisor.py handover` / ENDED heartbeat (`supervisor.py:1518` / `:1547`) where the successor registration goes.
Missing: `successor_wake.py` + that one wiring hunk. Nothing new is invented.

## 4b2 rule "the successor never creates another task" — interpretation (OURS, pinned here)
The *task's action* registers nothing: one prompt, one session, one self-unregister. The supervisor session it boots **may** register the next link at its own ENDED — that is exactly what the 2026-10-26 chain test proved (`chain_test_proof.txt`, commit `ce8194ba2`: task `chain-test-2` fired, the run shipped, the task was deleted after). If the operator reads the rule as "no chain, ever", the auto-wiring above is off by default (`--no-wake` default) and the manual one-liner stays the tool.

## What it does NOT do
- No cron, no repeat trigger, no standing task (SCHEDULING_POLICY §4: "It must be unregistered after it fires").
- No revival of hung/finished app sessions; no mts_signal changes; no cross-host registration (NUC cannot wake NB — NB's own ENDED path covers NB).
- No effect on the budget pacer: the successor is the supervisor itself; pacing still governs its spawns.

## Test plan (new test must fail on the pre-change code at least once)
`test_successor_wake.py`:
- `--dry` golden: PS text has exactly one `FireAt`, no `Trigger` repeat/cron flag, model named in the prompt, self-unregister present.
- handover file gets exactly one `Successor task:` line; a second run updates, does not duplicate.
- `--at` in the past → refused.
- register idempotent (existing task → `-Force`).
- `supervisor.py handover --no-wake`: no task (stub the register call); default path registers.

## Size
~150–250 lines incl. tests: one new file (`successor_wake.py`), one test file, one wiring hunk in `supervisor.py` + its flag. No live path, no deploy gate: `sync.py ship` smoke gate only.

## Open question for the operator
Resolved 2026-10-27 (d-47, VERBATIM below): runs must be chained, nothing manual by default; manual intervention stays possible/compatible (`--no-wake`, `Unregister-ScheduledTask MTS-SuccWake-<login>`); fireAt is budget-aware per the pacer.
> "runs must be chained - nothing manual but manual interventions possible/compatible -> makes sense? So depending of the session usage limits runs has to continue. keep distributing load. Something exists on this but perhaps is not woired and connetted." (operator, 2026-10-27)
