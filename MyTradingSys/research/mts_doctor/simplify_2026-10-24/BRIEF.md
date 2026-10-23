# Brief: one simplification session (MTS_Doctor, 2026-10-24, operator ask)

Operator ask (2026-10-24): "Freeze new tooling, and collect the inventory (cost and catch of each hook, gate step and script;
bug origins for the last 2 weeks; which machinery the research uses) as the brief for one simplification session."
Freeze: ANNOUNCEMENTS.md A-20261024-1. Raw data: `inv_hooks_gate.md`, `inv_scripts_bugs.md`, `inv_research_needs.md` (this folder).

## 1. What the numbers say
- Work mix, 14 days: 3,675 real commits; 135 (3.7%) touch trading code. About 9 in 10 are coordination or docs.
- scripts/dev: 216 files, 52,949 lines. Trading code reaches 10 of them (cbp_run, verify_extract_quotes, fetch_captions_timed,
  live_mirror, shot, nowin, tom_noise_units, prereg_gate, verdicts, live_owner). The other 206 are machinery and its tests.
- Bugs, 14 days: 110 real fixes; 87 (79%) are in dev tooling, 13 (12%) in trading code. 42 of the 87 repair tooling that is
  under 14 days old. BUGS.md: 36 of 42 new rows are tooling. The machinery makes most of the bugs it then has to catch.
- Hooks: a tool call costs 0.64 s against a 0.5 s budget (3-4 Python processes per call).
- Gate: 66 steps. Two steps take a quarter of all gate time and catch nothing: 4h (358 slot-min, 13 of 13 fails are 240 s
  timeouts) and 3xt (269 slot-min, 7 of 11 fails are timeouts).

## 2. Why one ship took 14-22 minutes and failed late
- The smoke gate is meant to run only what a change touches, in under 2 minutes. It does not, because
  `gate_impact` always keeps "direct" tests (those that import a changed file) whatever the 30 s budget says, and its estimates
  are guesses (152 s estimated, about 10 min real). A change to supervisor.py pulls in test_soak_six_slots (135-164 s alone).
- A slow test hits the 240 s smoke cap, the step fails, so the session falls back to `--full` (66 steps, 16-22 min).
- A failed step means re-running the whole gate: no record of which steps already passed for the same code.
- A non-hermetic test on trunk (planted_error_trial read a lab file) turned every ship red for hours until 7facabce8.

Standard practice elsewhere (one repo, one CI): the local check runs only the tests of the changed code (seconds to 2 min);
the full suite runs once on CI after push, split into parallel shards; a red trunk is reverted, not patched forward;
a re-run repeats only the failed tests (pytest `--last-failed`, build caches). MTS already has CI with 15 shards and
green-only deploy, so the local `--full` gate duplicates CI.

## 3. Proposed cuts (session decides; each is one small ship that lowers line count)
Gate
1. Smoke obeys its budget: "direct" tests inside the budget, estimates from measured `gate_timing.jsonl` medians,
   any test at or above SLOW_FILE_S (30 s) runs in CI only. Card `gate-impact-direct-obeys-budget` (Builder).
   Card `soak-six-slots-smoke-cap` is the first instance.
2. Local `--full` only for the live path (gate_select FULL_RE, unchanged). Everything else: smoke locally, all 66 steps in CI.
3. Drop from the local gate (CI keeps them): 3k (281 min, 1 fail), 5b and 4f (127 min each, 0 fails), 4, 3dk, 3ad, 3bk.
4. Steps that test a hook go with the hook (3sg, 3sig: about 100 slot-min).
Hooks
5. Remove turn_meter, model_guard, offer_guard, prereq_guard: warn-only or false positives, no recorded catch, about 1,300 lines.
6. trunk_lag: fetch once per session, compare with the session's own tree (it reported "87 behind" for a tree equal to trunk, 2026-10-24).
   role_loader: drop the SubagentStart duplicate.
7. Keep: stop_guard, ci_watch, c_drive_guard, role_loader (shrink), preship until its catches are counted.
Scripts
8. 15 scripts have only a doc as caller; 5 of them have no test (deploy_untrack_backup, gq_after_reset, traffic_report,
   wait_pid, worker_cost_report). Delete or move to archive after an import-graph check.
9. Multi-device and multi-login machinery (relay, signals/budget/exhaust, nuc_wake, cloud_setup, lane_health: about 3k lines)
   only if the operator confirms one machine is the plan.
Process
10. Red trunk: revert within 10 minutes, then fix on a branch. Card `red-trunk-revert-10-min` (Session_Planner).
11. One editor per central file (run_all_tests, run_extra_tests, sync, tasks, supervisor.md); WIP limit 2 sessions.

## 4. Never cut (the "keep heavy" set)
Execution tests (56 files), Java tests (31) and Maven, steps 1/2/3/4e/5b/6 in CI, gate_select FULL_RE (live path = full gate,
unknown path = full), CI 15 shards + mark-green + green-only deploy (DEPLOY_RUNBOOK), live_owner + loop-supervisor tests,
backtest correctness checks (lookahead_lint, research_kit_lint, prereg_gate, trial_ledger, holdout split), wiring and discovery
checks (3x, 3gd, 3dl: 0.2-11 s each), doc contract 4d and card lint 3tl (cheap, real catches), CBP (cbp_run, verify_extract_quotes,
fetch_captions_timed).

## 5. How the session works
- One session, operator picks the model. Output 1: a deletion list (file, lines, who calls it, what replaces it), checked against
  the import graph. Output 2: removal ships, one group each, each with `Result: -<n> lines, gate <before> -> <after> s`.
- No big-bang rewrite; no new tools. Done when a non-live-path ship passes the local gate in under 2 minutes and the hook cost
  per tool call is under 0.5 s.

## Caveats
Gate timing covers 5 days (the log is new). Catches were not matched to fixing commits. Script groups are by file name, not
call graph. Bug causes are classified by commit subject.
