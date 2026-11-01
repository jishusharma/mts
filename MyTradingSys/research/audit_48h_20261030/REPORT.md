# MTS 48-hour functionality audit — Cloud review handoff

**Status: implemented fixes; independent Cloud review and verification required before trunk merge.**

## Scope and method

The fixed window is 2026-10-27 22:43:13 UTC to 2026-10-29 22:43:13 UTC (28 October 04:13:13 to 30 October 04:13:13 IST). Audited tip: `f73ff791c905d725a01755d29256d039e0850b5a`; baseline: `afe15027f0dbffab0f7eb8f6a41868428285011c`. Work branch: `jis-nuc/codex-48h-value-audit`.

The complete git inventory contains **711 non-merge commits**, touching 6,833 distinct paths during the window. Intermediate restore/revert churn inflates that number. The net baseline-to-tip change is **1,085 paths, including 201 code/UI/workflow files**. `inventory.json`, `inventory.txt`, and `net_changes.tsv` preserve both views. `CODE_COVERAGE.csv` distinguishes manual inspection from inventory/gate coverage. This is a risk-prioritized audit of the committed change inventory; it does not claim every research sentence or every intermediate version was independently re-derived. Foreign uncommitted work and unpublished branches were preserved and were not treated as audited.

Priority was execution and data integrity, sealed-window boundaries, human validation correctness, ingestion and scorecard functionality, then basic UI and repository checks. Claims were acquired before edits; foreign claims and worktrees were left alone. All edits are in an isolated worktree. The five-hour allowance is a maximum; work was stopped and resumed as described below.

## Confirmed bugs and fixes

| ID | Priority | Confirmed failure | Resulting behavior |
|---|---|---|---|
| A48-01 | P1 | CBP malformed stored rows and envelopes crash queries | Malformed rows are skipped; valid peer rows remain available. |
| A48-02 | P1 | Simulator test-card route bypasses saved-run DEV boundary | Desk result cards reject outside-DEV, absent, invalid and reversed windows; corrupt catalogue is empty. |
| A48-03 | P1 | Live validation accepts infinite inputs and crashes on malformed state or disk failure | Reject nonfinite values; validate state shape; failed durable receipt returns PENDING; doubt-write failure stays DOUBT. |
| A48-04 | P1 | An older VALID case hides a newer operator rejection | Newest matching reviewed case wins; non-VALID verdict appears explicitly in notification. |
| A48-05 | P1 | Liquidation log shutdown silently abandons accepted events | Drain accepted events up to five seconds; reject post-shutdown log accepts; count queued abandonment. |
| A48-06 | P2 | Analyst scorecard disagrees with CBP tradability | Use canonical any-complete-call predicate; whitespace and em dash placeholders are incomplete. |
| A48-07 | P3 | Generated catalogue has corrupt punctuation in 25 rows | Repair known UTF-8/cp1251 punctuation round trips; rebuild artifact; numeric leaves unchanged. |

Every row has a task card in `MyTradingSys/system/tasks/` and remains pending Cloud review; no VERIFIED stamp or independent approval is fabricated. The live-validation disk-write regression is grouped under A48-03. `BUG_LOG.csv` is the machine-readable log.

## Proof and verification

All reproduction inputs are synthetic. `proof/*-red.txt` records original failures; the matching green logs record repaired behavior. Counts below overlap and must not be added together.

- CBP query/scorecard/scheduler: 51 tests passed at the initial fix. Final scorecard/CBP suite: 63 passed and 2 subtests passed.
- Live validation: final targeted run 16 tests and 15 subtests passed. Existing restart/reset, non-trade balance-event rejection, API send failure and retry tests are included.
- Simulator saved-run, HTTP integration, sealed cache and backfill suite: 40 passed, 2 skipped because the local idea cache is absent, 8 subtests passed. Artifact/backfill check after punctuation repair: 17 passed and 9 subtests passed.
- Java liquidation recorder: 10 offline tests passed, including restart/reset, non-trade/malformed messages, write errors, overflow, shutdown drain and repeated shutdown. Surefire result is attached.
- Read-only browser smoke: the real desk loaded 189/189 tests; the Audits filter showed 35/189; opening a result card showed its title, verdict, provenance and evidence. No study or market-data fetch was started. Own temporary server/tab were closed.
- Catalogue inspection: 189 result files (164 source-extracted, 23 hand/export, 2 run); no missing source-file pointers. The punctuation repair changed 29 string fields across the catalogue, affecting 25 rows; no numeric leaves changed. See `unicode_repair.json`.
- Syntax compile: all surviving net-changed Python files compiled. Whitespace check: `git diff --check`.
- Full offline gate and independent reviewer outcomes are recorded in `VERIFICATION.md` after completion. An early exploratory gate saw missing mutation-probe metadata on this audit's new cards. Those cards were corrected; the 103-test task suite subsequently passed. The initial failure is not attributed to trunk.

## Areas checked beyond the fixed files

Execution routing: the Pitchfork setup rejection in `auto_trader.py` was inspected. No execution formula was changed. Recent FT2/kill-switch and settlement/parity reports were reconciled with their existing cards. RSI regular/reverse divergence separation, causal pivot stamping, levels-confluence collection-only status, and the Sharpe/PSR/DSR/CSCV boundary change were inspected against their local definitions; broad layer/execution tests provide additional regression coverage. No new profitability or strategy-promotion verdict is asserted.

The 189-card catalogue was checked for reachability and source pointers; that check does not validate every extracted statistic. Source-extracted values remain clearly labelled copied, not rerun. Live-aid, statistics, Java, development-safeguard and research checks are covered by the full gate where wired. Actual exchanges, live feed parity and deployment remain outside the offline proof.

## Existing open dependencies and limits

- `cbp-ingestion`: activation still depends on a data host/config. Its prior card is DONE but carries UNCHECKED trust; a passing dry run does not prove scheduled ingestion is active. No scheduler was registered here.
- `wire-binanceliquidationaccumulator-into-`: separate live-host wiring/deployment work remains on its existing JIS-NB card. Recorder tests do not prove the production JVM constructs it.
- `wave1-settlement-pnl-identity-gap` / `settlement-capture-testnet-second-log`: competing settlement interpretations require a second capture. The daily-loss formula was not changed or declared correct on one capture.
- Live/archive feed parity and private-data tests require their owning host. Existing requests were preserved rather than duplicated.
- Shutdown draining is bounded to five seconds (OURS operational limit); forced process termination and a permanently stalled disk cannot guarantee persistence. Overflow/abandoned queue counters expose loss. A send followed by a failed durable receipt returns PENDING and can be retried; exactly-once external delivery is not claimed.
- GitHub CLI and in-app browser are signed out. No PR or hosted CI run is claimed. The review branch, local proof bundle and repository handoff are the delivery route; Cloud must open a draft PR and run Linux/Windows CI before merge.

## Cloud checklist before merge

1. Fetch the review branch; inspect each fix commit and `BUG_LOG.csv`. Reproduce fail-first cases against the audited tip (or use the attached patch/tests); then run the repaired suites. Check numeric catalogue fields remain unchanged.
2. Independently inspect Java shutdown concurrency/bounded waiting, validation correction precedence and failure paths, CBP schema rejection, scorecard counts, and the test-card DEV guard. Pay special attention to the at-least-once notification limitation above.
3. Reconcile intervening trunk commits and all existing claims. Open a **draft** PR into `fast-track`; keep auto-merge off. Run the complete Linux and Windows CI matrix, record independent review evidence and only then permit merge. No live restart/deploy is part of this audit.

The user's explicit pre-merge review requirement takes precedence over the normal `sync.py ship` route, which pushes straight to trunk. This delivery therefore uses a review branch and a separate repository review signal, without shipping audit code to `fast-track`.


## Resume reconciliation — 1 November 2026

The session stopped at its usage limit after approximately 18 minutes of active work on 30 October. The original five-hour allowance was not exhausted in active time; no claim of five uninterrupted hours is made. On resumption, the eight audit fix commits and pending report/catalogue changes were found intact. Gate shards 1/12 and 2/12 both had ALL TESTS PASSED; the remaining shards were not yet run. Unsharded attempts ended before a summary, so they are not counted as successful full gates.

Current trunk was fetched before resuming. It independently added a non-object CBP-store guard and implemented a different liquidation shutdown drain. These overlap A48-01 and A48-05 and must be reconciled by Cloud; the audit branch must not replace current trunk files wholesale. The other three compared fix targets (live_validation.py, runs_view.py, and analysts/run_scorecard.py) have no intervening change relative to the audited tip at this reconciliation. Generated catalogue/artifact files must also be regenerated from current trunk rather than replaced wholesale with this historical 189-card snapshot. The saved audit window remains fixed; this is not a new 48-hour audit of 1 November.

Delivery remains review-only, as the original operator asked for Cloud review before trunk merge. The final branch receipt records the fetched trunk SHA and all gate outcomes. Existing CODEX task-scope repairs in another session are outside this audit's edits.


The resumed shard 9 initially failed only `test_broadcast_warns_on_unacked_and_expired_told_for_a_seen_host`: its fixed 25 October clock fell outside the real seven-day broadcast retention window. Current trunk already fixed this in `39e9eb030b2c2d85d55c9fd6b98124615764d88e`. That exact test-only change was cherry-picked with provenance as `a19ce28e3`; no duplicate implementation or production change was made. The focused test failed before and passed after the backport. The initial shard failure and final rerun are retained in the proof bundle.
