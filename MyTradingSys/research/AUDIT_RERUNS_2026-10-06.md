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
1. CryptoCred limit-fill fix in run_cc_setups.py: a resting limit at the level, placed at the close of the MSB confirm bar and filled on the first 1m bar after placement that touches it; no fill before expiry = no trade. Add a failing-first test. Then rerun on the PC (research worktree, below-normal priority) and replace the b3dbe74 numbers.
2. Tom core: in the PC research worktree merge origin/claude/project-thread-7gvyfy (needs 3fdf8cb), build, run TomSnapshotGen into F:\MTS\data\tom_snapshots_2026-10-06 (README_REPLAY.md), then tom_bt_run.py rows/report into a fresh dir, and write TOM_CORE_BT_RERUN_2026-10-06.md.
3. Decide on the remaining NO-SOURCE items from the audit: ExtraSetupBuilder 1m stop, layer brackets (auto_trader.py stop 1% / target 2%), CryptoCred 0.1% stop and 1.5R target, exhaustion proxy (SCB 2x/240), proof bands 3/5.
4. Push the PC research branch commits (4c74cd7, 2aa75cc, b3dbe74) when the operator allows.
