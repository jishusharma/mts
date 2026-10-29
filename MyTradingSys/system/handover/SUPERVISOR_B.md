# Supervisor B handover | written 2026-10-28T18:14Z by JIS-NUC | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)
Successor task: MTS-SuccWake-B fireAt 2026-10-28T18:14Z (4b2)

## Goal
Login B on JIS-NUC: mode NORMAL, 5 h 56.0% (reset 2026-10-28T19:40Z), week 48.0% of cap 95.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: A@JIS-LAPTOP | `python scripts/dev/sync.py where --all` | read at 2026-10-28T18:14Z
- Last picks: layer-relations-concepts-us-open | `python scripts/dev/tasks.py dispatch` | read at 2026-10-28T18:14Z
- Open claims from JIS-NUC: funding-carry-with-real-spot-basis-margi | `python scripts/dev/sync.py where --all` | read at 2026-10-28T18:14Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-B-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login B --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Restart wake MTSLogonWake live; cold launch_app and the B14 successor chain fix (12d90245b) still unproven until the next real reboot, check F:/MTS/succ_wake/logon_wake.log; logins A and C need logon_wake.py install. Shipped+verified today: logon wake 4d, wiring audit bcfd46cfc, Opus fixes B1/B2/B3/B5/B6/B10, ship returns at push (f6c7c446b), ship --result + bg_watch until (223bb7c01), gate reuse (26fe674ec), stop-guard merge-base (d5946cee2), LC1 fair-control 0/12 KEEP (10dca8a07), live-layer relabel + T10 12 rows (eac7837a0), pre-US PRE_REG (04112bfe2), liquidation event log (a0704527f, needs MANUAL DEPLOY to record data). Open: bug-supervisor-handoff-duplicates card still raw (needs review stamp then done); cards layer-relations-concepts-us-open duplicated by login C flow_layers_concepts (skip); T0 tests in test_gemini_queue ok on NUC git 2.24 after fix; re-land multi_tf_bias study needs a costs.csv inventory row (author C); gap_frequency needs lookahead allowlist rows. ISSUES_REGISTER.md lists B1-B21 and I1-I9. Stalled bg tasks of other sessions: a8d649e9ded724c8c a4b4f1f06774c79f1 a09497793807739fc bhung0001. 5h burn about 19 pts/h, spawn one worker per wake.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
