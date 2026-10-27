# JIS-NUC worktree triage, 2026-10-21 (card wt-triage-nuc)

Rule: relevant unshipped work goes to origin/fast-track; stale or superseded trees are removed after their patches and untracked files were copied to `Dumps/wt_salvage_2026-10-21/<tree>/` on the NUC (gitignored). A branch is deleted only if it is an ancestor of origin/fast-track; otherwise it is kept (ref only, no tree).
All task cards / STATUS.md / LAYERS.md / artifact html / relay_runs changes in the stale trees were older generated snapshots of files trunk has since rewritten: DECISION (OURS) drop.

## Shipped (KEEP-SHIP)
| tree | verdict | evidence |
|---|---|---|
| F:/MTS/mts-candle-research (nuc/codex-candle-research) | SHIPPED f0f5dd47 + follow-ups | frozen corrected candle-close study (0/2016 cells), 4 TRIALS rows, INDEX row, done card; stale staged edits to wiring_registry/FORMULAS/layer_index/test_study.py NOT ported (trunk newer); in salvage patch |
| mts-dsa-jis-nuc-1019-1429 | SHIPPED f0f5dd47 | T04 `_make_log.py` helper |
| trunk-red fix (not a tree) | SHIPPED 19b4ae1d | 2 runbooks reworded (`git switch --detach`), 3 ladder.py lookahead rows baselined "pre-existing, unreviewed", trial-ledger test count made dynamic, ledger rebuilt (7075 rows) |

## Deleted (tree removed; branch deleted if ancestor)
| tree | verdict | reason |
|---|---|---|
| pensive-poincare-5e8cb0 | DELETE | only runtime_data; gate_timing.jsonl saved to salvage |
| mts-dsa-jis-nuc-1016-0629 | DELETE tree, branch kept | older T01 incarnation; trunk has T01 as 3a9b389a (t01_* scripts) |
| mts-dsa-jis-nuc-1019-0713 | DELETE tree, branch kept | T01_PROGRESS resume marker of a closed task; patch in salvage |
| mts-dsa-jis-nuc-1018-1516, -1019-0712 | DELETE | generated STATUS.md only |
| mts-jis-nuc-audit-72h-alignment | DELETE | stale task cards / doctor report / ROLES edits; trunk newer (eagle_eyes etc.); patch in salvage |
| b162-habib-intake-2, fable-run4-setups, ru1-dispatch-json-2, ru2-desk-sweep-2, supervisor-b-20261020-2 | DELETE | generated LAYERS.md only |
| g2-rescope | DELETE | card rescope superseded (card dropped on trunk bf5dba20) |
| nuc-tandem-1018 | DELETE | scripts identical to trunk; card closed on trunk |
| s1015-031508 | DELETE | regenerated sha line of proof pack |
| super-nuc-1017b | DELETE | stale relay NEXT_SESSION/relay_runs state |
| mts-jis-nuc-audit-revalidation | DELETE | generated html + runtime_data/_mirror copy (not committable) |
| mts-jis-nuc-krown-layer-v0-detectors | DELETE | krown files byte-identical on trunk |
| mts-jis-nuc-wavetrend-eom | DELETE | generated html only |
| gq/live-loop-timeouts-b191, malkan-prereg-dwm-equities, review-imbalance-analysts-report-and-imp | DELETE | ancestors / stale generated files (Lab_Guy 2026-10-21: ancestors of trunk) |
| gq/trim-builder-cwd-and-prelaunch-worktree, trim-claudemd-re-read-guard | DELETE tree, branch kept | Lab_Guy: shipped (trunk 4217c8da, df229206); cherry shows '-' |
| gq/tom-ledger-add-the-losing-first-attempts | DELETE tree, branch kept | on trunk as fa7f26b8 |
| gq/backfill-t087-session-level-split-and-ve | DELETE tree, branch kept | on trunk as e52a9ffc |
| gq/indicator-values-multi-model-audit | DELETE tree, branch kept | trunk already holds indicator_audit_2026-10-14 (bb/rsi/stochrsi packets, scripts); this is the older packet_NN variant |
| gq/live-orderflow-state-line-1m-5m-15m-pric | DELETE tree, branch kept | Lab_Guy: rejected for now, needs a builder rebase on market_guide.py (commit 5afb3079 on branch) |

## SKIPPED (not touched)
| tree | reason |
|---|---|
| BinanceDataFeed (main) | holds other sessions' uncommitted files |
| mts-dsa, mts-relay, mts-refiner, mts-push | lane trees |
| F:/MTS/mts-gemini (jis-nuc/gemini-pitchfork-layer) | active right now (file mtimes 0 min, 5 commits unshipped) |
| mts-jis-nuc-wt-maint-job | another session's work, 2 fresh unshipped commits |
| F:/MTS/mts-codex (nuc/codex-holdout), F:/codex_home/..., F:/MTS/mts-codex-lab | Codex trees |
| ~45 clean trees (`ok`, nothing unshipped) | left for `sync.py tidy` / their owners; hold no work |
