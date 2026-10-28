# Supervisor C handover | written 2026-10-27T23:59Z by JIS-DESKTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)
Successor task: MTS-SuccWake-C fireAt 2026-10-27T23:59Z (4b2)

## Goal
Login C on JIS-DESKTOP: mode NORMAL, 5 h 8.0% (reset 2026-10-28T03:10Z), week 4.0% of cap 85.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, or a 3 h wave.

## Truth
- Peers live at write: A@JIS-LAPTOP | `python scripts/dev/sync.py where --all` | read at 2026-10-27T23:59Z
- Last picks: main-checkout-stale-hooks-2026-10-24 | `python scripts/dev/tasks.py dispatch` | read at 2026-10-27T23:59Z
- Open claims from JIS-DESKTOP: ship-root-cause | `python scripts/dev/sync.py where --all` | read at 2026-10-27T23:59Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-C-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login C --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Verify Opus audit ac11f7eb0a30ecbd7 ship (process audit + sleeping-threads note) via git cherry; health-checks card all-health-checks-run-and-triage on NUC (confirm queued, Gemini low); Argon id for gemini_queue.py; login A live (13pct 5h); plan fixed 16da534e (26s); raw-aged cards need refine; Session_Planner run; operator: arm DeepSeek hands-free
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
