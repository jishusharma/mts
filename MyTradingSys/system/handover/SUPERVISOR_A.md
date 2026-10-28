# Supervisor A handover | written 2026-10-28T16:19Z by JIS-LAPTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)
Successor task: MTS-SuccWake-A fireAt 2026-10-28T16:51Z (4b2)

## Goal
Login A on JIS-LAPTOP: mode STOP, 5 h 88.0% (reset 2026-10-28T16:49Z), week 75.0% of cap 95.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: B@JIS-NUC, C@JIS-DESKTOP | `python scripts/dev/sync.py where --all` | read at 2026-10-28T16:19Z
- Last picks: none | `python scripts/dev/tasks.py dispatch` | read at 2026-10-28T16:19Z
- Open claims from JIS-LAPTOP: none | `python scripts/dev/sync.py where --all` | read at 2026-10-28T16:19Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-A-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login A --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. get_usage+plan after reset; resume exhaust-a-opus-wave1 (check it's still alive via sync.py where --all) or BATCH 1 dispatch
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
