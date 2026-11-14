# Supervisor A handover | written 2026-11-14T14:51Z by JIS-LAPTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)

## Goal
Login A on JIS-LAPTOP: mode NORMAL, 5 h 3.0% (reset 2026-11-14T15:00Z), week 26.0% of cap 95.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: none | `python scripts/dev/sync.py where --all` | read at 2026-11-14T14:51Z
- Last picks: tf-x1-fabio-orderflow-gaps-1113 | `python scripts/dev/tasks.py dispatch` | read at 2026-11-14T14:51Z
- Open claims from JIS-LAPTOP: none | `python scripts/dev/sync.py where --all` | read at 2026-11-14T14:51Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-A-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login A --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Trunk red at 6948173c (step 4e test_no_own_costs; author C must revert). Hold spawns until CI green. tf-x1 shipped 9237567b, card still ready on trunk (coordinator to mark done). Operator/coordinator: deploy b-f33439, disk_keep facts b-94ba93. Next Supervisor: plan --login A, act on lines.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
