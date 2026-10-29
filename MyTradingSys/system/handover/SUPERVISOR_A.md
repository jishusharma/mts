# Supervisor A handover | written 2026-10-29T17:30Z by JIS-LAPTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)
Successor task: MTS-SuccWake-A fireAt 2026-10-29T17:31Z (4b2)

## Goal
Login A on JIS-LAPTOP: mode SPEND, 5 h 39.0% (reset 2026-10-29T21:20Z), week 83.0% of cap 99.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: B@JIS-NUC, C@JIS-DESKTOP | `python scripts/dev/sync.py where --all` | read at 2026-10-29T17:30Z
- Last picks: bug-stale-role-history-blocks-lease | `python scripts/dev/tasks.py dispatch` | read at 2026-10-29T17:30Z
- Open claims from JIS-LAPTOP: none | `python scripts/dev/sync.py where --all` | read at 2026-10-29T17:30Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-A-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login A --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. CI RED (TOM-CTX-DIV) hit and was reverted by B mid-wake; context hit TRANSIT at 255K. Backlog drained: wiring audit, gemini race test (no-op, already done), pitchfork arm-check (verdict NO), 8 raw Noticed cards filed. B/C coordinating on their own ready-4 sets; week budget still 83% used, 15h to reset -- keep draining via tasks.py dispatch, same D5 chain, no scheduler.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
