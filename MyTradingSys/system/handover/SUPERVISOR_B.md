# Supervisor B handover | written 2026-11-04T05:08Z by JIS-NUC | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)

## Goal
Login B on JIS-NUC: mode NORMAL, 5 h 13.0% (reset 2026-11-03T23:30Z), week 61.0% of cap 95.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: A@JIS-LAPTOP | `python scripts/dev/sync.py where --all` | read at 2026-11-04T05:08Z
- Last picks: none | `python scripts/dev/tasks.py dispatch` | read at 2026-11-04T05:08Z
- Open claims from JIS-NUC: none | `python scripts/dev/sync.py where --all` | read at 2026-11-04T05:08Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-B-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login B --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Weekly hit 65% cap at 2026-11-04. DSA chat (own Chrome tab) runs Tom ledger card rv-dsa-ledger-mechanical, hands-free at #33 26/200, CI green. C Malkan Hindi ask still open (6 video ids). Left for C.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
