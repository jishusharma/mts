# Supervisor C handover | written 2026-10-27T21:58Z by JIS-DESKTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)
Successor task: MTS-SuccWake-C fireAt 2026-10-27T22:12Z (4b2)

## Goal
Login C on JIS-DESKTOP: mode NORMAL, 5 h 23.0% (reset 2026-10-27T22:10Z), week 3.0% of cap 85.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, or a 3 h wave.

## Truth
- Peers live at write: A@JIS-LAPTOP | `python scripts/dev/sync.py where --all` | read at 2026-10-27T21:58Z
- Last picks: fable-run2-regate-b-verdicts-and-ledger-rows | `python scripts/dev/tasks.py dispatch` | read at 2026-10-27T21:58Z
- Open claims from JIS-DESKTOP: ship-root-cause | `python scripts/dev/sync.py where --all` | read at 2026-10-27T21:58Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-C-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login C --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Verify Builder a99b550dc2fdaf705 (test_dsa .gateway_owner) shipped, then re-ship malkan-prd-nrd-align; Gemini claims fail on NUC (push rejected x6, see F:/MTS/gq/*.log); wake GPT lane (nuc_lab.py tick) after ~01:00Z; check B wake F:/MTS/nuc_wake/default/out.log; run Session_Planner
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
