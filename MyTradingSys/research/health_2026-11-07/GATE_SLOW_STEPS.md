# Gate slow steps: per-file seconds for 3sig, 3xt, 4f

Measured 2026-11-11 on JIS-NUC (12 logical CPUs) in a clean worktree at trunk d97098d0f. Measure only: no gate or test code changed.
Method: 3sig and 4f = `pytest --durations=0 --durations-min=0.5` on the exact targets of the gate step (4f via `pytest_cmd(PYTEST_LAYER_PATHS)`); 3xt = `run_extra_tests.py` at the gate default of 4 jobs, per-file "in Ns" lines. Runs were sequential, 2 samples per step. Machine load (CPU %, sampled at start of each run): 3sig 4 % and 0 %; 4f 8 % and 2 %; 3xt 7 % and 8 %. Only this session's runs were active, so the numbers are close to idle.

## Table (seconds; the two samples are shown as s1 / s2)

| step | file | seconds | n samples | load note |
|---|---|---|---|---|
| 3sig | scripts/dev/test_mts_signal.py (63 tests; step = this one file) | 85.6 / 84.5 (pytest wall 88 / 87) | 2 | idle, 4 % / 0 % |
| 4f | scripts/dev/test_wt_maint.py | 47.2 / 42.1 | 2 | idle, 8 % / 2 % |
| 4f | scripts/dev/test_route_audit.py | 4.5 / 4.5 | 2 | same |
| 4f | scripts/dev/test_outcome_labeler_incremental.py | 4.3 / 4.0 | 2 | same |
| 4f | all other files (425 tests, step wall 68 / 62) | under 1 each | 2 | same |
| 3xt | scripts/dev/test_planted_error_trial.py | 68.5 / 61.4 | 2 | 4 jobs at once, 7 % / 8 % at start |
| 3xt | research/context_factors_2026-10-16/test_context_asof.py | 59.7 / 52.5 | 2 | same |
| 3xt | tools/live_aid/test_live_aid.py | 46.2 / 45.3 | 2 | same |
| 3xt | tools/live_aid/test_live_aid_replay.py | 44.5 / 42.3 | 2 | same |
| 3xt | research/context_factors_pit_2026-10-16/test_context_asof.py | 38.3 / 35.0 | 2 | same |
| 3xt | scripts/dev/test_lab_query.py | 27.9 / 25.8 | 2 | same |
| 3xt | all 397 files, summed per-file seconds | 981 / 896 (about 245 s wall at 4 jobs) | 2 | same |

History, `runtime_data/gate_timing.jsonl` (full-mode rows, last 10): 3sig median 136 s (125 to 145, n 9), 4f median 114 s (69 to 122, n 10), 3xt median 878 s (860 to 1041, n 6; that is the step's logged seconds, which looks like the per-file sum rather than 4-job wall). Today's idle run of 3sig (85 s) and 4f (65 s) is well under the logged medians, so the logged gate numbers carry load from parallel steps; the per-file ranking is the stable part. 3xt per-file seconds are not in the jsonl (only the step total), so the per-file column above is from this run.

## Proposal per step (each names the invariant it must keep)

- 3sig: test_mts_signal.py is one file whose 63 tests each spawn a fresh hook subprocess and git hub (1.4 to 6 s each); split it into two files (ask tests vs signal tests) so two shards run them side by side, or mark the 10 slowest (over 3 s) CI-only. Invariant: the broadcast/ask/told/ack behaviour tests keep running on every ship that touches mts_signal.py.
- 3xt: 397 files, 6 files make up about 270 s of the sum; cap each at one fast smoke test locally and leave the full run to CI, or give test_planted_error_trial and both test_context_asof files their own shard. Invariant: the file list check test_gate_discovery_b150 still sees every file, and a changed file always runs (gate_select D6).
- 4f: one file is 80 % of the step; test_wt_maint.py (28 tests, each builds a git repo and worktree) can be split in two files, or its fixture repo built once per class. Invariant: 4f stays in the local ship gate (test_a_ship_leaves_the_slow_coordination_steps_to_ci) and the worktree-safety tests (never remove an unshipped tree) keep running.

## After (2026-11-11, JIS-NUC, idle, 2 samples each)

| step | before (s) | after (s) | change |
|---|---|---|---|
| 4f (pytest_cmd(PYTEST_LAYER_PATHS) wall) | 68 / 62 | 50.2 / 50.3 | test_wt_maint.py 47 / 42 -> 30.4 / 30.4 |
| 3sig (exec_unittest_shards, 2 shards) | 85.6 / 84.5 | 51.7 / 52.7 | about 33 s saved |

- 4f (ship 4f10aa79b): test_wt_maint.py builds the bare origin + primary clone once per run (module template) and copies it per test, then `git remote set-url origin` to the copy's own origin. All 30 tests and every assertion unchanged; each test still gets its own fresh repo. No split: 4f is one pytest process, so a second file would not run in parallel.
- 3sig: no file split needed. The gate already has `exec_unittest_shards` (used by 3dk, 3k, 3ds, 3bk); step 3sig now calls it with 2 shards (round-robin of the same 63 test ids, union = every test once; gate_jobs() == 1 keeps one process). test_mts_signal.py untouched.
- Not changed: SHARD_EST_WIN / STEP_EST for 3sig (test_ci_split pins them); CI partition estimates are therefore a little high.
