# Supervisor A handover | written 2026-11-03T20:17Z by JIS-LAPTOP | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)

## Goal
Login A on JIS-LAPTOP: mode NORMAL, 5 h 48.0% (reset 2026-11-03T20:40Z), week 80.0% of cap 95.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: B@JIS-NUC | `python scripts/dev/sync.py where --all` | read at 2026-11-03T20:17Z
- Last picks: none | `python scripts/dev/tasks.py dispatch` | read at 2026-11-03T20:17Z
- Open claims from JIS-LAPTOP: none | `python scripts/dev/sync.py where --all` | read at 2026-11-03T20:17Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-A-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login A --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. OPERATOR 11-03 ~20:10Z: A PAUSED (week 80%, cap 85%, reset 11-06 09:00Z); B and C take the work. A only runs the 4 Argon cards after the quota reset ~22:20Z (gemini-blind-read-volume-candles-facts-1103, gemini-mutation-rerun-research-kit-1103, gemini-blind-read-eagle-c36-wt-confluence-1103, gemini-rerun-cbp-scorecard-spec-tests-1103), reviews docs-only and ships. No Lenovo blockers on trunk. Open for operator: ff primary checkout + search_index_scope.ps1 UAC; DeepSeek DSA-NB; Lead pipeline mode.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
