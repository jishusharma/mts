# Supervisor C handover | written 2026-11-06T22:22Z by JIS-DESKTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)

## Goal
Login C on JIS-DESKTOP: mode NORMAL, 5 h 0.0% (reset 2026-11-07T03:20Z), week 58.0% of cap 85.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: none | `python scripts/dev/sync.py where --all` | read at 2026-11-06T22:22Z
- Last picks: fabio-v3-model-b-managed-is-rerun | `python scripts/dev/tasks.py dispatch` | read at 2026-11-06T22:22Z
- Open claims from JIS-DESKTOP: none | `python scripts/dev/sync.py where --all` | read at 2026-11-06T22:22Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-C-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login C --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. N2 done 22:20Z. Shipped: cycle-bottom rule window gap + live line (5b90b2eed), fee/stop re-score (78423a49, no setup net positive, Next END), ledger P4 scored (b0c019f9). Open: S005 scores 11-07 end, S008 11-16. Next window N3: first pick card prob-base-rates-registry-1106 is the Lead's (do not hand out); fabio-v3-model-b-managed-is-rerun is a desk run-and-report card (post to desk, not a Builder); republish stale pages mts_layer_map and sim_desk (edit access check first); P1-P3 US prep phases per d-us-session-prep-1106 (09:00Z, 13:15Z, 14:45Z, P4 21:15Z). Credit left about 12.88 USD, job 3 skipped unless a card fits. Trunk CI green at last check; a revert of a commit touching extra_tests.tsv leaves a dead entry.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
