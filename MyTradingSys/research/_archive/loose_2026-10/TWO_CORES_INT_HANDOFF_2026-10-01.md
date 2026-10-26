# TWO CORES INTEGRATION: HANDOFF (budget stop, 2026-10-01 19:40Z)
Session MTS-2026-10-01-1916Z-CLD-BLD-two-cores-int. Branch alias claude/quirky-knuth-y2u3ij. Task: CLOUD_PROMPT_TWO_CORES_INTEGRATION_2026-10-02.md.
Operator message: "3 $s left - save tasks - commits". Everything on disk was committed and pushed; nothing below is gated unless it says so.

## State per wave
| Wave | State | Evidence | Checkpoint |
|---|---|---|---|
| 3 consensus writer + RSI observation | DONE, parent-verified | overlay run 71 tests OK (69 new + 2 boundary); rsi_ma_events has no live producer (only rsi/run_rsi_backtest.py:50); boundary rule test_layer_boundaries.py:81-101 confirmed | febe8e5 (checkpoint 3) |
| 1 readiness fix pass | PARTIAL, NOT reviewed | staged .new on disk (below); the subagent had not reported; docs TWO_CORES_FIX_PASS_2026-10-02.md and MTS_LAUNCHER_SPEC_2026-10-02.md did NOT exist at 19:36Z; no fail-first run seen by the parent; gate not run | none (WIP aa8933a) |
| 2 Fabio v3 core | PARTIAL, NOT reviewed | v3/ signals, fill, manage, costs, day_gates staged; MISSING models.py, engine.py, __init__.py, tests/, README.md | none (WIP aa8933a) |
| 4 switchability spec | DONE, parent spot-checked (173 lines; boot-only config read AT:546-548, source string AT:208-209, disabled_layers exact-name AT:211, LRC:259-261, TLB:54/92 all match) | spec file is on the branch as committed; 21 open items, decisions D1-D6 for the supervisor (D1: propose cores.fabio default false until a registered backtest) | checkpoint 4 (this commit) |

Wave 1 staged (all unreviewed): runtime/math_object_builder.py.new, tests/test_book_imbalance_nodata.py.new, scripts/dev/alert_rate_check.py.new (+test), execution/auto_trader.py.new (+test), runtime/test_quad_classify.py.new, runtime/test_regime_classifier.py.new, tests/java/MarketDataSnapshotTest.java.new. UNEXPECTED, not in the brief: tests/test_proof_direction.py.new and research/core_readiness_2026-09-27/harness/proof_direction_cases.py.new (the brief said existing tests stay unchanged): diff them against the originals and justify or drop.

## Remaining tasks (in order)
1. Review W1: diff each .new vs original (smallest change?), re-run fail-first (overlay the TEST only -> must FAIL; test + fix -> PASS), write TWO_CORES_FIX_PASS_2026-10-02.md (with the failing run) and MTS_LAUNCHER_SPEC_2026-10-02.md (root mts.ps1, NOT scripts/mts.ps1; that path does not exist). Gate: `python scripts/dev/run_all_tests.py --quick` on the tree (baseline: all PASS except Step 3c, which fails because gitignored execution/plans, journal, halt_history are absent in the clone) AND the same inside an overlay of the W1 files. Commit checkpoint 1.
2. Finish W2: models.py, engine.py, __init__.py, tests/ (one per module), README.md. Acceptance: pending_test_fabio_v3.py runs against v3 with only its import line changed (T01-T64); a signal-level test that fails on a broken copy. Engine rules: grid params (NS-grid) are REQUIRED config, no defaults (no cell is selected; TRIAL_REGISTRY.csv absent, FABIO_V3_SPEC.md:234); verdicts are an engine convention mirroring spec state names. Gate on tree + overlay. Commit checkpoint 2.
3. (W4 done; optional: spot-check the remaining sections.) Add to SUPERVISOR_LOG a layers/alerts/ ownership claim before any step-3 live_runner work (the W4 spec notes none exists).
4. Deliverables: update sessions/<ID>.md (14 fields; commits list), CLOUD_INBOX.md (a note addressed to this session = the 19:00 QUEUE line; remove it only when W1 is accepted), 03_FILE_INDEX.md (one row per new file + refresh the # SIZE header), SUPERVISOR_INBOX.md (one entry: session ID, files staged, migration order). `git add -f` every .new (`*.new` is gitignored, .gitignore:4).
5. Print the Step 5 desktop runbook verbatim and the four-line verify block.

## Findings to carry into the report
- Fabio core cannot trade live as compiled: needs footprint/big-trade columns (orderflow_bars COLUMNS), but live_runner_cli.py:23-53 maps klines t,o,h,l,c,v,tbv only. Runbook steps 7-9 (wire, route, armed) also conflict with FABIO_V3_SPEC.md:249-268 (backtest first): supervisor decision.
- execution/ may not import MyTradingSys.backtest.layers (test_layer_boundaries.py:81-101): auto_trader cannot call consensus/writer directly; hook owner unknown. snapshot_id has no owner (absent in math_object_builder.py).
- The RSI block holds the last rsi_events alert per tf (stale between events); 1m, 3m, 4h, 1d have no source.
- MyTradingSys/runtime/test_*.py is not collected by run_all_tests.py (pytest collects MyTradingSys/tests only; Step 5b collects backtest/layers): gate decision needed for the W1 item-4 tests.
- auto_trader TF_SECONDS is at :48, not :47; the launcher is /mts.ps1 (repo root).

## Resume helper
`MTS_REPO=<repo> python MyTradingSys/research/two_cores_int_handoff_2026-10-01/stage_overlay.py <DEST> [--prefix path ...]` copies the repo (no .git) to DEST and applies every X.new over X there; run tests inside DEST. Nothing in the repo is written.
