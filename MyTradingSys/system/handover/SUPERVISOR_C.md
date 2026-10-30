# Supervisor C handover | written 2026-10-30T02:17Z by JIS-DESKTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)
Successor task: MTS-SuccWake-C fireAt 2026-10-30T02:18Z (4b2)

## Goal
Login C on JIS-DESKTOP: mode NORMAL, 5 h 22.0% (reset 2026-10-30T02:40Z), week 28.0% of cap 85.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: A@JIS-NUC, B@JIS-NUC | `python scripts/dev/sync.py where --all` | read at 2026-10-30T02:17Z
- Last picks: main-checkout-stale-hooks-2026-10-24 | `python scripts/dev/tasks.py dispatch` | read at 2026-10-30T02:17Z
- Open claims from JIS-DESKTOP: ship-root-cause | `python scripts/dev/sync.py where --all` | read at 2026-10-30T02:17Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-C-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login C --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. 02:20Z TRANSIT. Open: Fable R5 shipped (GRANDFATHER_DECISION 7f02769e; config edit is a CRITICAL card); R7 on O2 hold; reply protocol e8e7e8cd shipped; station_disk_report removed from trunk, needs Linux-safe re-land; successor wake fix e1e0dba8 unproven (proof fire card); b-230ce8 told (GPT/Gemini on NUC); DeepSeek DSA row 39h; A reset conflict.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
