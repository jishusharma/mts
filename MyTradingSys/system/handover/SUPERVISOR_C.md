# Supervisor C handover | written 2026-11-03T16:55Z by JIS-DESKTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)

## Goal
Login C on JIS-DESKTOP: mode NORMAL, 5 h 27.0% (reset 2026-11-03T18:40Z), week 98.0% of cap 99.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: A@JIS-LAPTOP, B@JIS-NUC | `python scripts/dev/sync.py where --all` | read at 2026-11-03T16:55Z
- Last picks: fabio-v3-model-b-managed-is-rerun | `python scripts/dev/tasks.py dispatch` | read at 2026-11-03T16:55Z
- Open claims from JIS-DESKTOP: none | `python scripts/dev/sync.py where --all` | read at 2026-11-03T16:55Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-C-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login C --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Weekly 98% (stop 97%) until 20:00Z reset: no workers. After reset: refine 9 raw cards (Session_Planner), then fabio-v3-model-b-managed-is-rerun; release dead JIS-NB claims (q-8df7bd); republish stale mts_home/sim_desk/mts_layer_map; AIBridge 0.7.24 installed on JIS-NB (verify 29/29), operator to reload ext + remove stale 0.7.11 copy.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
