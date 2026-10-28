# Supervisor A handover | written 2026-10-28T10:59Z by JIS-LAPTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)
Successor task: MTS-SuccWake-A fireAt 2026-10-28T10:59Z (4b2)

## Goal
Login A on JIS-LAPTOP: mode CRUCIAL-ONLY, 5 h 63.0% (reset 2026-10-28T11:19Z), week 64.0% of cap 95.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, or a 3 h wave.

## Truth
- Peers live at write: B@JIS-NUC, C@JIS-DESKTOP | `python scripts/dev/sync.py where --all` | read at 2026-10-28T10:59Z
- Last picks: trendline-count-only-v2 | `python scripts/dev/tasks.py dispatch` | read at 2026-10-28T10:59Z
- Open claims from JIS-LAPTOP: none | `python scripts/dev/sync.py where --all` | read at 2026-10-28T10:59Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-A-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login A --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Usage gate blocked all spawns this wake (5h 63% > elapsed 11%+10); trendline-count-only-v2 (CRUCIAL, host DESKTOP-F7IU69N/JIS-NB) broadcast to C (b-9ba2b0); Session_Planner refine-9-raw and desk.py assign still pending once gate clears; DSA/DSA-NB/DSA-NUC still held.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
