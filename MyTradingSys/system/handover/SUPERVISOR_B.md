# Supervisor B handover | written 2026-10-28T13:04Z by JIS-NUC | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)
Successor task: MTS-SuccWake-B fireAt 2026-10-28T13:04Z (4b2)

## Goal
Login B on JIS-NUC: mode NORMAL, 5 h 48.0% (reset 2026-10-28T14:40Z), week 35.0% of cap 95.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, or a 3 h wave.

## Truth
- Peers live at write: C@JIS-DESKTOP | `python scripts/dev/sync.py where --all` | read at 2026-10-28T13:04Z
- Last picks: none | `python scripts/dev/tasks.py dispatch` | read at 2026-10-28T13:04Z
- Open claims from JIS-NUC: funding-carry-with-real-spot-basis-margi | `python scripts/dev/sync.py where --all` | read at 2026-10-28T13:04Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-B-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login B --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Restart wake MTSLogonWake live (launch_app proven only at next cold boot; check F:/MTS/succ_wake/logon_wake.log); logins A and C need 'logon_wake.py install --login X' from their own primary clone; Builder agent on cbp-query-symbol-btcusdt-returns-zero in flight (verify note, is-ancestor, green); wiring audit bcfd46cfc verified, Haiku recheck + diff review still owed; Session_Planner 0b57bdf20 has no Result line; apply-dedupe-audit-findings still raw; stalled bg tasks a7d41f374b06f4e89 b1lx1m5ta b5hx9ksb7 belong to other sessions; headless Supervisor B (MTS-SuccWake-B) may still run, the successor should check and not duplicate; 5h burn 14/h so spawn one worker per wake
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
