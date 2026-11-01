# Supervisor B handover | written 2026-11-01T05:34Z by JIS-NUC | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at last boot)

## Goal
Login B on JIS-NUC: mode NORMAL, 5 h 4.0% (reset 2026-11-01T10:29Z), week 96.0% of cap 99.
Stop at 5 h >= 80%, week >= cap, CI red, no ready cards, the TRANSIT at time, or a 3 h wave.

## Truth
- Peers live at write: A@JIS-LAPTOP, C@JIS-DESKTOP | `python scripts/dev/sync.py where --all` | read at 2026-11-01T05:34Z
- Last picks: tom-v2-gross-first-dev-ext | `python scripts/dev/tasks.py dispatch` | read at 2026-11-01T05:34Z
- Open claims from JIS-NUC: none | `python scripts/dev/sync.py where --all` | read at 2026-11-01T05:34Z

## Ruled out
- none recorded by the tool; add what was tried and closed (`handover --from <file>`).

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-B-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login B --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0`.
2. Weekly 96% cap reached 2026-11-01; no Claude spawns until reset 17:00Z. Gemini Rumers cards running (gemini_rumers.log), codex tick running. Next: confirm trunk CI green after d6b0814f, re-ship Lab_Guy gemini-burn-c (jis-nuc/gemini-burn-c-2), NUC user must reload AIBridge 0.7.9 and F5.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
