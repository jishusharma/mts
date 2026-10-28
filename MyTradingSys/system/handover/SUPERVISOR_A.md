# Supervisor A handover | written 2026-10-28T16:00Z by JIS-LAPTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)
Successor task: MTS-SuccWake-A fireAt 2026-10-28T16:52Z (4b2)

## Goal
Login A on JIS-LAPTOP: mode STOP, 5 h 87.0% (reset 2026-10-28T16:50Z), week 75.0% of cap 95.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: B@JIS-NUC, C@JIS-DESKTOP | `python scripts/dev/sync.py where --all` | read at 2026-10-28T16:00Z
- Last picks: none | `python scripts/dev/tasks.py dispatch` | read at 2026-10-28T16:00Z
- Open claims from JIS-LAPTOP: none | `python scripts/dev/sync.py where --all` | read at 2026-10-28T16:00Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-A-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login A --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Stalled Opus worker (a785107ddf929d913, 70m>45m cap, empty worktree) TaskStop'd; root cause fixed+shipped: supervisor.md step3 now calls watchcheck (96d2531c). Logged conflict bug-conflict-2bac1f8186 (exhaust-order vs TRANSIT-NOW-at-87%). Next: get_usage+plan after 5h reset (16:50Z), resume exhaust from BATCH 1 (main-checkout-stale-hooks-2026-10-24, bug-conflict-ad30df5c4d, re-state-lc1-keep-list-on-the-touched-on) if room, else continue dispatch.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
