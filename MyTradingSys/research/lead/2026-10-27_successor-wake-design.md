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
`supervisor.py handover` (`supervisor.py:1518`, ENDED heartbeat at `:1547`): after writing the handover and sending `mode=ENDED`, unless `--no-wake` is passed, call `successor_wake.py` register for the same login, `--at now`. ENDED then always self-boots the next link: task → successor supervisor → its ENDED → next task. Human input only on exceptions (no CLI login on that machine, checkout missing — both visible in `who`'s missing heartbeat and the out.log).

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
Chain-vs-one-shot (the "4b2 rule" bullet above): default auto-wake every ENDED, or manual one-liner only? Everything else is settled; answer with "chain" or "manual" and the card's `--done-when` adjusts.
