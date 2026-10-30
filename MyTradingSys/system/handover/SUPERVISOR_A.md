# Supervisor A handover | written 2026-10-30T08:33Z by JIS-LAPTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)
Successor task: MTS-SuccWake-A fireAt 2026-10-30T08:33Z (4b2)

## Goal
Login A on JIS-LAPTOP: mode NORMAL, 5 h 3.0% (reset 2026-10-30T07:59Z), week 96.0% of cap 99.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: none | `python scripts/dev/sync.py where --all` | read at 2026-10-30T08:33Z
- Last picks: bb-state-regime-tf-map | `python scripts/dev/tasks.py dispatch` | read at 2026-10-30T08:33Z
- Open claims from JIS-LAPTOP: none | `python scripts/dev/sync.py where --all` | read at 2026-10-30T08:33Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-A-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login A --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. weekly ~99% used; resets 09:00Z. Opus pizzino-layer-dashboard running (worktree mts-desktop-f7iu69n-pizzino-layer-dashboard-2). Open: C to run bb_state_study.py (f41aaa6e); where-is-index-redo raw card; JIS-NB cleanup card; ready cards for post-reset.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
