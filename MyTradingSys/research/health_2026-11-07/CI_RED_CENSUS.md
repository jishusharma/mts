# CI red census: last 30 red fast-track runs (read 2026-11-08 by login B, GitHub API + job logs; counts are OURS)

Card ci-red-ship-gate-parity-1107. Each row is one red CI run: failed step(s), failing test file(s), files in that commit.

| run | commit | failed steps | failing tests | files in the commit |
|---|---|---|---|---|
| 42410763666 | e5b96b6e9 | Step 3xt.2 | test_boot_audit.py | extra_tests.tsv |
| 42410615860 | f21bea28d | Step 3xt.1 | test_boot_audit.py | test_artifact.py, sim-desk-test-artifact-node-timeout-flake.json |
| 42410541271 | 65ba72338 | Step 3xt.1 | test_boot_audit.py | boot-audit-fix-reports-nothing-to-fix-wh.json, boot_audit.py, test_boot_audit.py |
| 42398801939 | 008a94ffa | Step 4.2, Step 4.5 | test_aibridge_version_bump.py | lab-safe-file-repo-data-gate.json, lab-shared-keeps-weight.json |
| 42397989771 | 6336fa4c9 | Step 4.5, Step 4.2 | test_aibridge_version_bump.py | - |
| 42392305178 | a8fd1e1ce | Step 4.10, Step 4.8, Step 3gd, Step 4.2, Step 4.5, Step 4.3 | test_aibridge_selftest_concurrent.py, test_aibridge_version_bump.py, test_gate_discovery_b150.py | - |
| 42390705600 | acb6eff3a | Step 3gd, Step 4.2, Step 4.3, Step 4.8, Step 4.5 | test_aibridge_version_bump.py, test_gate_discovery_b150.py | - |
| 42386246475 | e4c810b58 | Step 3xt.2 | test_trunk_lag.py | FORMULAS.md |
| 42385712450 | ea97191dc | Step 3xt.2 | test_trunk_lag.py | - |
| 42384774318 | 357fc59f3 | Step 4.7 | test_aibridge_argon.py | - |
| 42383732434 | 24bbfe772 | Step 3pc | - | 2026-11-07_adx-di-census.md, 2026-11-07_gpt-rederive-adx-di-census-1107.md, gpt-rederive-adx-di-census-1107.json |
| 42383637884 | c768a69c9 | Step 3pc | - | BLIND_READ_MS_WT_VOLMATCH_ETH.md, 2026-11-07_gemini-blind-read-ms-wt-volmatch-eth.md, 2026-11-07_h3-ny-open-10sym.md, 2026-11-07_wicks-census.md +3 |
| 42383330865 | ec33bf719 | Step 3pc | - | - |
| 42383294725 | 33ecd1df9 | Step 3pc, Step 4.1, Step 4.12, Step 4.6 | test_aibridge_install_fresh.py, test_aibridge_version_bump.py | 2026-11-07_cryptocred-s3-pooled.md, 2026-11-07_michael-lines.md, gpt-rederive-cryptocred-s3-pooled-1107.json, gpt-rederive-michael-lines-1107.json |
| 42383169455 | 42ad5bfde | Step 3pc, Step 4.1, Step 4.6, Step 4.12 | test_aibridge_install_fresh.py, test_aibridge_version_bump.py | BLIND_READ_MS_LEVEL_ETH.md, 2026-11-07_gemini-blind-read-adx-di-census.md, 2026-11-07_gemini-blind-read-ms-level-eth.md, 2026-11-07_gpt-rederive-value-area-acceptance-1107.md +4 |
| 42383023255 | b26778646 | Step 3pc, Step 4.1, Step 4.6, Step 4.12 | test_aibridge_install_fresh.py, test_aibridge_version_bump.py | 2026-11-07_gemini-blind-read-cc-s3-10sym.md, 2026-11-07_gemini-blind-read-ms-bb-retest-eth.md, 2026-11-07_gemini-blind-read-reclaim-close-stop.md, 2026-11-07_gemini-blind-read-tom-v2-gross-first.md +10 |
| 42382636135 | 4dbfa9ddf | Step 4.12, Step 3pc, Step 4.1, Step 4.6 | test_aibridge_install_fresh.py, test_aibridge_version_bump.py | - |
| 42382308120 | 7f0693d20 | Step 4.1, Step 4.6, Step 4.12 | test_aibridge_install_fresh.py, test_aibridge_version_bump.py | - |
| 42382255625 | 038c14d2b | Step 4.1, Step 4.12, Step 4.6 | test_aibridge_install_fresh.py, test_aibridge_version_bump.py | LAYERS.md |
| 42380697294 | c7d729e31 | Step 3xt.8 | test_spec_us_open.py | - |
| 42375957285 | 13ebd4455 | Step 3w, Step 3x | - | lookahead_allowlist.tsv |
| 42310104094 | 75405e45c | Step 4.8 | test_aibridge_chain.py | - |
| 42307003634 | 740530341 | Step 4.8, Step 3xt.5 | test_aibridge_chain.py, test_spec_us_open.py | - |
| 42287960167 | 17e4c6cc8 | Step 4e | test_no_own_costs.py | LADDER_PROPOSAL.md, habib_watch.py, test_habib_concept_book.py, habib_watch.py.json |
| 42287020840 | ad4619326 | Step 4e | test_no_own_costs.py | costs.csv, calls_score.py |
| 42284452148 | 591a9b2ba | Step 3cx | - | - |
| 42280822698 | 9a4622bec | Step 4.7, Step 3xt.3, Step 3xt.10, Step 3gd, Step 4.2 | test_gate_discovery_b150.py, test_rescore.py | RESCORE.md, rescore.py, rescore_fabio.py, test_rescore.py +3 |
| 42280238386 | 4f39906df | Step 3w, Step 3x | - | ma-strip-live-aid.json |
| 42279851289 | 7f38fa2c1 | Step 3w, Step 3x, Step 3tk | - | extra_tests.tsv |
| 42279263182 | 3af24f379 | Step 3tk | - | - |

## Counts per step (a run can fail several)

| step | runs |
|---|---|
| Step 3pc | 7 |
| Step 4.1 | 6 |
| Step 4.12 | 6 |
| Step 4.6 | 6 |
| Step 4.2 | 5 |
| Step 4.5 | 4 |
| Step 4.8 | 4 |
| Step 3xt.2 | 3 |
| Step 3gd | 3 |
| Step 3w | 3 |

## Counts per failing test file

| test | runs |
|---|---|
| MyTradingSys/tests/test_aibridge_version_bump.py | 10 |
| MyTradingSys/tests/test_aibridge_install_fresh.py | 6 |
| scripts/dev/test_boot_audit.py | 3 |
| MyTradingSys/tests/test_gate_discovery_b150.py | 3 |
| scripts/dev/test_trunk_lag.py | 2 |
| MyTradingSys/tools/live_aid/test_spec_us_open.py | 2 |
| MyTradingSys/tests/test_aibridge_chain.py | 2 |
| MyTradingSys/backtest/test_no_own_costs.py | 2 |

## Reading

* Top 3 classes: (1) AIBridge tests (`test_aibridge_version_bump`, `test_aibridge_install_fresh`, `test_aibridge_chain`) in the pytest shards, 16+ runs; (2) step 3pc PRE_REG context lint, 7 runs; (3) step 3xt extra tests (`test_boot_audit`, `test_trunk_lag`, `test_spec_us_open`), 8 runs.
* (1) is mostly one red state that stayed red across many runs (consecutive runs share the failing test), and the smoke gate already selects the bridge shards for any bridge file (checked with gate_select.select on scripts/aibridge/*, RELEASES.json, aibridge_install.py): not a selection gap.
* (2) had one real selection gap: the lint also reads `DEV_CHECK*.md` next to a PRE_REG, but a docs-only ship of such a file ran no 3pc. Fixed in this card (DOC_MUST).
* (3) three of these were the ubuntu runner disagreeing with Windows (`sys.platform` early return in boot_audit, trunk_lag): the gate selected the step and it passed on Windows. That is platform parity, which gate_select cannot fix; tests must pass on ubuntu.
