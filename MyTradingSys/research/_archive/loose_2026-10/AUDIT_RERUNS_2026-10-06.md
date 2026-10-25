# AUDIT RERUNS 2026-10-06 (state at credit stop)

Audit page: https://claude.ai/artifact/VYrWZbBj5LU1NR9rpesZNY (section "reruns").
PR #12 merged (stop floor removed, book_imbalance null, MSB fix, Deribit fees, trade_blocklist); live since auto_trader restart 2026-10-06 15:41:23Z.

## Results
| Rerun | Where | Result | Status |
|---|---|---|---|
| T055 C1 funding_cvd_fade (funding 2020+) | PC research worktree, commit 4c74cd7 | FAIL (unchanged) | done |
| T055 C2 session_momentum (DST ny anchor) | PC research worktree, commit 4c74cd7 | FAIL (unchanged) | done |
| Testnet pre-fix note (before 15:41:23Z; OI tainted 09-24..B136 restart) | PC research worktree, commit 2aa75cc | recorded | done |
| CryptoCred setups (run_cc_setups.py, 1h, net of fees) | PC research worktree, commit b3dbe74 | setup1 maker_entry PASS, setup2 maker_entry PASS, all_taker FAIL, setup3 FAIL | **UNVERIFIED: fill bias** |
| Tom core BT (archive snapshots on current Java) | PC, not finished | - | open |

CryptoCred PASS is invalid until rerun: bt_engine.simulate_trade fills at entry_price at entry_t, and setups 1/2 enter at the broken level / fib zone, so the runner books a limit fill at the level after the HTF retest bar has closed. Signature: setup1 hit rate 0.84 with a 1.5R target. The maker-vs-taker gap is about 0.9R because stops are only ~0.1% wide, so the fee per R is huge.

## Next steps (in order)
1. DONE in code (commit after cd916b7 on this branch; rerun still needed). CryptoCred limit-fill fix in run_cc_setups.py: a resting limit at the level, placed at the close of the MSB confirm bar and filled on the first 1m bar after placement that touches it; no fill before expiry = no trade. Add a failing-first test. Then rerun on the PC (research worktree, below-normal priority) and replace the b3dbe74 numbers.
2. Tom core: in the PC research worktree merge origin/claude/project-thread-7gvyfy (needs 3fdf8cb), build, run TomSnapshotGen into F:\MTS\data\tom_snapshots_2026-10-06 (README_REPLAY.md), then tom_bt_run.py rows/report into a fresh dir, and write TOM_CORE_BT_RERUN_2026-10-06.md.
3. Decide on the remaining NO-SOURCE items from the audit: ExtraSetupBuilder 1m stop, layer brackets (auto_trader.py stop 1% / target 2%), CryptoCred 0.1% stop and 1.5R target, exhaustion proxy (SCB 2x/240), proof bands 3/5.
4. Push the PC research branch commits (4c74cd7, 2aa75cc, b3dbe74) when the operator allows.

## UPDATE 2026-10-07 (MTS-2026-10-07-1002Z-APP-BLD-research-closeout)
| Rerun | Result | File |
|---|---|---|
| CryptoCred setups, limit-fill model | setup1 FAIL, setup2 FAIL, setup3 FAIL (both fee variants). The b3dbe74 PASS was the fill bias; UNVERIFIED mark removed | research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md |
| T055 C1 / C2, full funding | C1 FAIL (OOS net -0.0453%), C2 FAIL (OOS +0.0177%, Sharpe 0.0084). The 10-06 reruns used ~12 months of funding, not the 80 files, and are superseded; full funding crashed run_t055 until bars were clipped to funding coverage (fixed, tested) | research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md |
| Tom core BT, current Java | no edge, live rule 0 signals (was 17), net R -2.91 sensitivity (fee ~2.76 R per trade after the stop floor removal) | research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md |
| Step 3 NO-SOURCE items | all five stay flagged by operator ruling 2026-10-07: B116 (closed earlier), B117, B118, B142, B143, B144 | items/ |
| Step 4 push of research commits | not done; research branch is local at 7aa01cd | - |
