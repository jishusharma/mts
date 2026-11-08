# Supervisor A handover | written 2026-11-08T13:03Z by JIS-LAPTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)

## Goal
Login A on JIS-LAPTOP: mode NORMAL, 5 h 30.0% (reset 2026-11-08T13:50Z), week 35.0% of cap 95.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: none | `python scripts/dev/sync.py where --all` | read at 2026-11-08T13:03Z
- Last picks: none | `python scripts/dev/tasks.py dispatch` | read at 2026-11-08T13:03Z
- Open claims from JIS-LAPTOP: none | `python scripts/dev/sync.py where --all` | read at 2026-11-08T13:03Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-A-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login A --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Builder a7428cb6 (cbp-events-reland-1108) was in its full ship gate (58/72 at 12:40Z, fix ba578bc76 for test_headline_links_event node parity); verify it landed on trunk with Result:, CI green, else revert immediately. Then: Lab_Guy stamps for ~10 raw/IMPORTANT cards (labguy-gpt-card-no-model-identity-1104, route-g7-slippage-into-cost-model, supervisor-py-plan-tasks-py-next-dispatc, 3 gate cards); DSA desks blocked: DeepSeek account suspended to 2026-11-11 10:22Z (do not re-kick); signals b-1aa316 b-36973f b-fc3654 b-b7dabe acked told, blocked on others; GitHub setup-uv 504 flakes: gh run rerun --failed, not a revert; republish mts_layer_map and mts_home (login C)
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
