# Supervisor B handover | written 2026-10-30T01:06Z by JIS-NUC | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)
Successor task: MTS-SuccWake-B fireAt 2026-10-30T01:07Z (4b2)

## Goal
Login B on JIS-NUC: mode NORMAL, 5 h 50.0% (reset 2026-10-30T02:59Z), week 57.0% of cap 95.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: A@JIS-NUC, C@JIS-DESKTOP | `python scripts/dev/sync.py where --all` | read at 2026-10-30T01:06Z
- Last picks: spikefade-prior-day-high-proxy-cap | `python scripts/dev/tasks.py dispatch` | read at 2026-10-30T01:06Z
- Open claims from JIS-NUC: funding-carry-with-real-spot-basis-margi | `python scripts/dev/sync.py where --all` | read at 2026-10-30T01:06Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-B-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login B --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. No get_usage on this profile: set MTS_LOGIN=B, record usage by hand (usage_reminder.py record, elapsed from 5h window start). Shipped simdesk-declutter-top (b39ea8c1) and planner refine (3da2c45a3). Next: spikefade-prior-day-high-proxy-cap Builder + 1 raw card; file Noticed: sim_desk tests missing from extra_tests.tsv, tasks.py check NOT READY wording. station_disk_report.py reverted again at 01:06Z, recheck.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
