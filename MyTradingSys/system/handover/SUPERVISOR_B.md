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
2. Still working at 17:00Z 11-04; operator: eco mode, week stop 75%, send review and fix work to the Claude Platform credit (`api_job.py launch`, Haiku for read checks, Sonnet for small fixes, one job at a time). DSA is STOPPED: bridge 0.7.26 is installed in F:/AIBridge, but the operator must reload the extension, refresh the tab and tick Hands-free (the permission system refuses it from a session). After that, tell DSA its last three read results never posted, ask it to re-read smaller pieces, and read the Hands-free box directly each wake. Codex starts with the MTS-Wake-codextick task (20 min gap); before a tick after a codex_run.py fix, fast-forward F:/MTS/mts-codex-lab, since a tick keeps the old code in memory. Gemini: `gemini_queue.py run <card>:medium`, then a capped Haiku job spot-checks and ships the branch. At 21:00Z 11-04: Codex results ship again (89482fbfe); Malkan window card is corrected and ready for Codex; if Codex shows BLOCKED or a merge clash, read F:/MTS/nuc_wake/tick.log. Week 73%: stop at 75%, docs only.
3. `python scripts/dev/tasks.py dispatch`; start the next picks.

## Traps
- One ship at a time; EXTRA registration forces the ~20 min gate.
- This machine's account file reads as login A while the app is B; set env MTS_LOGIN=B for supervisor.py and mts_signal.py (raw card login-detection-reads-the-wrong-account-).
- A ship through red CI needs `sync.py ship --fix-ci`; without it the tool refuses after printing "pure revert", and nothing is pushed.

## Open
- Claims above: finish, hand over in the card, or release.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
