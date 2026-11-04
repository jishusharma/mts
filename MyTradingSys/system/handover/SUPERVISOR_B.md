# Supervisor B handover | written 2026-11-04T05:08Z by JIS-NUC | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)

## Goal
Login B on JIS-NUC: mode NORMAL, 5 h 13% (reset 2026-11-04T17:20Z), week 68%; the operator set this login's weekly stop at 75%.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: A@JIS-LAPTOP | `python scripts/dev/sync.py where --all` | read at 2026-11-04T05:08Z
- Last picks: none | `python scripts/dev/tasks.py dispatch` | read at 2026-11-04T05:08Z
- Open claims from JIS-NUC: none | `python scripts/dev/sync.py where --all` | read at 2026-11-04T05:08Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-B-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login B --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Still working at 13:45Z 11-04. DSA chat rebooted 13:40Z in its Chrome tab, hands-free on, no click needed, working the Tom ledger row; each wake read its panel and the bridge age, send the boot text again if it is quiet. Codex lane works from the NUC with no sign-in step; start ticks with the MTS-Wake-codextick task (20 min gap). lc-validation dropped, levels void.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
