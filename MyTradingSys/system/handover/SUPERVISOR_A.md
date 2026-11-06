# Supervisor A handover | written 2026-11-06T08:40Z by JIS-LAPTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)

## Goal
Login A on JIS-LAPTOP: mode SPEND, 5 h 40.0% (reset 2026-11-06T12:10Z), week 89.0% of cap 99.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: B@JIS-NUC, C@JIS-DESKTOP | `python scripts/dev/sync.py where --all` | read at 2026-11-06T08:40Z
- Last picks: voice-start-supervisor-a-handover | `python scripts/dev/tasks.py dispatch` | read at 2026-11-06T08:40Z
- Open claims from JIS-LAPTOP: none | `python scripts/dev/sync.py where --all` | read at 2026-11-06T08:40Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-A-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login A --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Weekly reset 09:00Z: next A Supervisor boots normally. Refine sync-py-start-tidy-gateway-only-reads-cl (stale-claims retire risk) and sync-py-ship-tasks-py-done-route-tag-tra (Next: trap filed junk cards fix/none). 3 blind-read cards need F: raw data (export-trades, level-approach-prep, research-anticipati): desktop/NUC only.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
