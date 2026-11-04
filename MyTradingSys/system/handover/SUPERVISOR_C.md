# Supervisor C handover | written 2026-11-04T08:39Z by JIS-DESKTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)

## Goal
Login C on JIS-DESKTOP: mode NORMAL, 5 h 49.0% (reset 2026-11-04T09:50Z), week 21.0% of cap 85.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: none | `python scripts/dev/sync.py where --all` | read at 2026-11-04T08:39Z
- Last picks: c26-phase2-freeze-regime-ladder | `python scripts/dev/tasks.py dispatch` | read at 2026-11-04T08:39Z
- Open claims from JIS-DESKTOP: none | `python scripts/dev/sync.py where --all` | read at 2026-11-04T08:39Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-C-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login C --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. retired: PLAN_24H_2026-11-04 L1 Sonnet owns login C; Wave 2 c26-phase2 carried into L2
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
