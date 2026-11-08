# Supervisor A handover | written 2026-11-06T19:54Z by JIS-LAPTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)

## Goal
Login A on JIS-LAPTOP: mode NORMAL, 5 h 11.0% (reset 2026-11-06T22:10Z), week 8.0% of cap 95.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: C@JIS-DESKTOP | `python scripts/dev/sync.py where --all` | read at 2026-11-06T19:54Z
- Last picks: fee-stop-rescore-fabio-habib-1106 | `python scripts/dev/tasks.py dispatch` | read at 2026-11-06T19:54Z
- Open claims from JIS-LAPTOP: none | `python scripts/dev/sync.py where --all` | read at 2026-11-06T19:54Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-A-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login A --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Operator shut desktop-f7iu69n down 11-07 for a restart. FIRST after boot: python scripts/dev/boot_audit.py (expect no MTS-Supervisor; MTS-Wrapper Disabled, remove it elevated: Unregister-ScheduledTask MTS-Wrapper) and note boot time vs before. Primary checkout stash 'pre-pull 2026-11-07' holds old local edits (24 scripts + 4 docs), do not drop. J9 = login C's call. Then normal plan loop, eco pace.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
