# Supervisor B handover | written 2026-10-29T21:42Z by JIS-NUC | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)
Successor task: MTS-SuccWake-B fireAt 2026-10-29T21:42Z (4b2)

## Goal
Login B on JIS-NUC: mode NORMAL, 5 h 50.0% (reset 2026-10-29T21:59Z), week 57.0% of cap 95.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: none | `python scripts/dev/sync.py where --all` | read at 2026-10-29T21:42Z
- Last picks: layer-relations-concepts-us-open | `python scripts/dev/tasks.py dispatch` | read at 2026-10-29T21:42Z
- Open claims from JIS-NUC: none | `python scripts/dev/sync.py where --all` | read at 2026-10-29T21:42Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-B-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login B --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Wake 21:41Z: CI green after my revert ca25ae86f; B22 names rule + B23 fix (efc374bdf by C) on trunk; GPT lab lane up (lane_state c9cf84d4a), 2 GPT runs shipped 811f9870 after untracking .labflow-mutation-scratch. Open: Lenovo has not acked liquidation deploy b-d564be (LIQ_DEPLOY.md, operator ok 2026-10-30); rename card rename-devices-desktop-lenovo-nuc and bug-supervisor-stale-setup-one-step ready (SONNET); analyst-ingest-roman-x parked (needs real call posts); gpt-prereg-gate-boundary-tests claimed by another NUC session. Names: Desktop, Lenovo, NUC only. Start workers from tasks.py dispatch, skip layer-relations-concepts-us-open (C did it).
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
