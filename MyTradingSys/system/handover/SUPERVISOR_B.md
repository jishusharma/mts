# Supervisor B handover | written 2026-10-28T12:51Z by JIS-NUC | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)
Successor task: MTS-SuccWake-B fireAt 2026-10-28T12:51Z (4b2)

## Goal
Login B on JIS-NUC: mode NORMAL, 5 h 22.0% (reset 2026-10-28T14:40Z), week 31.0% of cap 95.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, or a 3 h wave.

## Truth
- Peers live at write: C@JIS-DESKTOP | `python scripts/dev/sync.py where --all` | read at 2026-10-28T12:51Z
- Last picks: cryptocred-stop-sweep-conclusion-provenance | `python scripts/dev/tasks.py dispatch` | read at 2026-10-28T12:51Z
- Open claims from JIS-NUC: funding-carry-with-real-spot-basis-margi | `python scripts/dev/sync.py where --all` | read at 2026-10-28T12:51Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-B-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login B --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Builder a34675 on cbp-query-symbol-btcusdt-returns-zero was still running at transit (verify its sha); MTS_Doctor wiring audit and cryptocred-stop-sweep not spawned; this profile has no get_usage (budget by hand: 5h 22 pct, week 31 pct)
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
