# Supervisor C handover | written 2026-10-25T20:50Z by local_supervisor-C (pilot 2) | verify: python scripts/dev/supervisor.py handover --verify   (STALE 0 at write; not yet re-verified)
EXAMPLE: the pilot-2 notes (handover/SUPERVISOR_C.md, 82 lines, 8 appended updates) rewritten into the fixed form of CONTEXT_FILES_DESIGN.md section 3b. Facts are the pilot's; nothing here is current state.

## Goal
Pilot 2 (PILOT_super_session_2026-10-24.md): 6 Sonnet Agent workers on ready cards, login C JIS-NB, 18:48Z-22:50Z; stop at 5 h >= 80%, week >= 45%, CI red, no ready cards, or 22:50Z.
Report to the Doctor (local_bf48e37d-ceba-4d0e-94fe-330458b891ac) at 20:00Z, 21:30Z and stop: one line per card (state, sha, turns).

## Truth (claim | check | result at write)
- 13 cards shipped, cherry 0 each | `for wt in <agent-* trees>: git -C $wt cherry origin/fast-track HEAD | wc -l` | 0 for all 13
- T05 c7f5eefb8, bt-engine-wire c0c5b7ea0+9be3f415e, lint-chunked 14f1703b9, test_lease 11850c8c7, T09-F5 2bd5dcdf2 on trunk | `git merge-base --is-ancestor <sha> origin/fast-track` | exit 0 each
- T05/T06/T07/T09 cards still OPEN (work shipped, `tasks.py done` refused by stamp A-20261018-5) | `python scripts/dev/tasks.py brief <id>` STATE line | SHIPPED@<sha>, state active
- No worker running, no ship running | `list_sessions {"linked": true}`; `python scripts/dev/sync.py where --all` | 0 workers, 0 ships
- Ready cards for dispatch: 0 (only sim-dashboard-v1 = sim-v2's, JIS-NB/Doctor cards) | `python scripts/dev/tasks.py dispatch` | empty
- CI green on every run seen; reverts 0 | `python scripts/dev/ci_watch.py` | green
- Usage end: 5 h 42%, week 38% (cap 45%) | `get_usage` | 20:50Z reading
- yt-fabio-fetch-retry: no commit (HTTP 429 x3); its wt agent-a8391044ff8788666 holds a WRONG uncommitted 'done' in the card json | `git -C <wt> status --short` | 1 modified card file: do not ship

## Ruled out
- Claude workers for YouTube (429 on all 3; operator 2026-10-25: all YouTube goes to Gemini on the NUC, lane CODEX).
- Parallel ships (two gates at once pushed tests past the 240 s cap, lost 2 sim-v2 ships): one ship at a time.
- Registering study tests in EXTRA during a run (forces the ~20 min gate; Argon): batch it at the end or leave to a card.
- `clear_session` for rotation (refused 3x while a ship or wake was live): compact or end the wave.

## Next 3 steps
1. `python scripts/dev/sync.py start supervisor-C-<utc date>`; `get_usage`; `python scripts/dev/supervisor.py plan --login C --five <%> --five-reset <utc> --week <%> --week-reset <utc> --running 0` (prints this file and TRANSIT).
2. Review stamps for T05/T06/T07/T09 (Lab_Guy pass, TASK_REFINEMENT promotion gate), then `tasks.py done <id> --result "<sha>"` each; one docs-only ship.
3. EXTRA registration batch in ONE ship (T05/test_placebo_nulls.py, T06/test_cost_inventory.py, T07/test_rerun_diff.py, T09/test_layer_signal_parity.py, session_flow_context_2026-10-18/test_build_rows.py); T09 needs committed out/parity_result.json; expect the ~20 min gate.

## Traps
- Lint false positives on text-window / chunk slices cost a failed ship each (fixed by 14f1703b9; if a new one appears, card it, do not hand-edit the lint).
- A ship can wait behind a push race (T05: 28m59s, retry 2/5); do not kill it under 30 min.
- `sync.py` refuses a second ship from one tree within 10 min: `--again` only for a separate change.
- A Monitor/chain shell dies with a clear or compact: re-check every row by cherry count, never from memory.
- `git merge` by Bash is denied in this worktree: read trunk with `git show origin/fast-track:<path>`.
- The f5 script still writes results to the old sim_desk path (gate 3xt fails on the artifact schema): results go to dsa_backtest_audit/out/.

## Open
- Review stamps T05/T06/T07/T09 (owner: Lab_Guy pass; hold A-20261018-5).
- Raw card for T05 S1 (distance-matched random-line control drops all 12 LC1 families) not yet created: command in T05 report section 8.
- Doctor rewrites yt-fabio-fetch-retry for the Gemini lane.

## Missed last time
(machine-written by `context_gap.py fold` at the next ship; the pilot-2 coordinator read these before its first edit and no file named them:)
MyTradingSys/system/ANNOUNCEMENTS.md (ACTIVE), MyTradingSys/system/SUPER_SESSION.md (Boot facts), MyTradingSys/research/mts_doctor/PILOT_super_session_2026-10-24.md, `tasks.py dispatch --json`, MyTradingSys/system/handover/SUPERVISOR_C.md (previous)
