# Supervisor B handover | written 2026-10-29T21:59Z by JIS-NUC | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)
Successor task: MTS-SuccWake-B fireAt 2026-10-29T22:00Z (4b2)

## Goal
Login B on JIS-NUC: mode NORMAL, 5 h 50.0% (reset 2026-10-29T21:59Z), week 57.0% of cap 95.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: A@JIS-LAPTOP | `python scripts/dev/sync.py where --all` | read at 2026-10-29T21:59Z
- Last picks: legend-footprint-bar-delta-differs-betwe | `python scripts/dev/tasks.py dispatch` | read at 2026-10-29T21:59Z
- Open claims from JIS-NUC: none | `python scripts/dev/sync.py where --all` | read at 2026-10-29T21:59Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-B-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login B --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. No get_usage on this profile; budget hand-recorded 5h 50 week 57 (stale at 21:59Z reset). Set MTS_LOGIN=B on every call (app email maps to A). Spawn legend-footprint-bar-delta-differs-betwe (MTS_Doctor) if plan still says so; answer A on LIQ_DEPLOY.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
