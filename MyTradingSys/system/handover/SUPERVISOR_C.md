# Supervisor C notes: Pilot 2 (6 workers, 4 h, rotation on). FULL REWRITE at ROTATE (sys clock ~19:55Z)

Window: stop starting work 22:20Z, hard stop 22:50Z (drain, ship notes, `git cherry` 0, stop report). Login C JIS-NB. I am the Supervisor (role file MyTradingSys/system/roles/supervisor.md; first reply banner `ROLE LOADED: Supervisor v3 ...`).
Doctor session: local_bf48e37d-ceba-4d0e-94fe-330458b891ac (SendMessage). Reports due: 20:00Z, 21:30Z, stop; plus at once on CI red / blocker / gate>30min. One line per card: state, sha, turns. At stop also: workers peak, max gate wait, reverts, get_usage at end.
Plan doc: MyTradingSys/research/mts_doctor/PILOT_super_session_2026-10-24.md. Pilot 2 change vs 1b: up to 6 workers, rotation (clear+rebuild on `ROTATE` -> reply `ROTATE-READY`).
Rules in force: workers = background Agents (model sonnet, haiku for mechanical), isolation worktree, commit only their paths, never ship, never edit run_extra_tests.py/run_all_tests.py, 40-turn cap. I ship from the worker's worktree: `cd <wt> && (time python scripts/dev/sync.py ship --release <wtname> [--again]) > $TEMP/ship_X.log 2>&1` run_in_background; ONE ship at a time; verify `git -C <wt> cherry origin/fast-track HEAD | wc -l` = 0. sync.py limits 10 min between ships per tree (use --again for a separate change, or wait). Red trunk: git revert within 10 min. Every turn ends with a live wake (background ship/worker). Never: deploy, main checkout, .mts_live, HALT, trades, .secrets, mainnet. The Stop hook nags about unshipped notes commits: ship notes (`python scripts/dev/sync.py ship --release supervisor-C-2026-10-25`) whenever no other ship is in flight and >10 min since the last one from this tree. Git merge by Bash from this worktree is denied; use `git show origin/fast-track:<path>` to read trunk.

## Cards: state and shas (worktrees under C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\.claude\worktrees\)
SHIPPED + verified (cherry 0):
- t02-f1-review-allowlist-chunk-4: card-done only (work already shipped c68e93ced300), 4 turns, 50b93be91
- tasks-py-check-rewrites-other-cards-mark: 753075e76, 6 turns, gate 2m33s
- cbp-add-channel-latest-n-to-fetch-captio: 18bd7fec4 (CBP repo d20ae76 in F:/CryptoScrapper; ~24 ignored inbox files left on disk), 12 turns, 43s
- context-conditioned-session-flow-states: 80777df8a (card-done only; verdict INCONCLUSIVE, 604 DEV rows, 2/84 cells powered), 5 turns, 56s
- dsa-audit-07-stale-verdicts (T07): eb293abb5 + lint-fix commit, ~55 turns (over cap), gate 3m23s; 8/10 reruns reproduce; mfe_exit DEV rerun read VALIDATION bars by accident (values withheld; card mfe-exit-dev-only-rerun-not-reproducible); card NOT done (stamp + hold)
- dsa-audit-06-cost-fill-realism (T06): 0d738711f, ~36 turns, gate 2m40s; 201 cost rows, 57/70 files bypass fees.py, funding changes no verdict (max +0.018pp); card NOT done
- dsa-audit-09-live-parity (T09): 446f6c503 + array_split lint fix, ~40 turns, gate 35s; findings S1x3 (volume_fvg mirror side 0/24 agree; RSI uncovered events; unbacktested 1%/2%/8-bar bracket); card NOT done; Doctor made raw cards T09-F1..F4 (live-path, leave alone); F5 is now a ready card
- argon-fix-defects-and-re-land: ad987950b (+EXTRA registration of scripts/dev/test_argon_blind_read.py, 5e280d203), ~20 turns, gate ~20 min (registration forced a bigger gate)

IN FLIGHT: dsa-audit-05-placebo-nulls (T05): wt agent-aeff7478879c89c20, commit c7f5eefb8, ~41 turns. SHIP RUNNING since ~19:48 (bg task bam9ocivm, log $TEMP/ship_t05.log). Verify cherry 0 in that wt. S1: touched-only distance-matched random-line control makes all 12 LC1 families DROP (8 published KEEPs don't survive); S3 SE too small in 29/126 candle_close arms; raw card for S1 not created (cmd in T05 report sec 8); card NOT done (stamp+hold).

DONE, NOT SHIPPED (queue after T05): bt-engine-wire-real-funding-rsi-cc-rerun: wt agent-a578ee348d9a30577, commits c0c5b7ea0 (reapply of the trunk-reverted 'load real funding') + 9be3f415e (lint-clean fwd_bars at run_rsi_backtest.py:111), 8 turns; RSI funding effect <=0.0147pp no sign change; CC setup3 -0.006pp. No new test files. Card not marked done.

RUNNING workers (Sonnet Agents, started ~19:56): lint-lookahead-false-positive-chunked-slices id ab98e197a6a0059b8; gate-test-lease-timeout-under-load id af05c70c26fd93566; t09-f5-funding-cvd-fade-backtest-at-1h id ac8b2b68eddeaee06 (told not to touch bt_data.py). Find worktrees via `python scripts/dev/sync.py where --all` (agent-<id> names) or their final reports.

NO COMMIT: yt-fabio-fetch-retry (a8391044ff8788666 haiku): 0/3 videos, HTTP 429 all; card left open; its wt agent-a8391044ff8788666 has an uncommitted wrong 'done' in the card json: do not ship.

Not eligible / skipped: hook-reminder (new hook), analyst-ingest-roman-x (stale), rv05-h2 and gap-g7 (need review stamp; gap-g7 shares bt_data.py), declutter, JIS-NB/CODEX/DSA-lane cards, cpu-audit (Doctor role), docker-vs-windows (heavy).

Registration batch NOT yet done (study-folder tests are only flagged, not failing): EXTRA += T05/test_placebo_nulls.py, T06/test_cost_inventory.py, T07/test_rerun_diff.py, T09/test_layer_signal_parity.py, session_flow_context_2026-10-18/test_build_rows.py (all under MyTradingSys/research/...). One ship at the end only if time (forces a big gate; the T09 test needs committed out/parity_result.json).

## Ship queue (in order)
1 T05 (running) -> 2 bt-engine-wire (wt agent-a578ee348d9a30577) -> 3+ new workers' commits as each finishes (lint-chunked, lease-timeout, t09-f5) -> final notes ship.
Unshipped notes commits in my worktree: ~4 (SUPERVISOR_C.md updates).

## Score notes for the Doctor
- test_lease.py exceeds the 240 s gate limit at 100% CPU (sim-v2 lost 2 ships): card gate-test-lease-timeout-under-load running.
- Fabio fetch HTTP 429 on all 3 videos (card left open).
- CryptoScrapper breach: the cbp worker edited and committed the CBP repo outside this repo (F:/CryptoScrapper cbp_v2 d20ae76, git rm of cbp_v2/inbox). The card scope named it, but note it.
- Lint false positives: fwd-index rule flagged a text-window slice (T07 t07_docdrift.py:34) and a chunk slice (T09 exit_analysis.py:25); each cost a failed ship (~3 min). Card lint-lookahead-false-positive-chunked-slices running.
- Cards with work already on trunk when started (t02-f1, flow-states, cbp): worker only marked done; stale card supply.
- A test in scripts/dev not in EXTRA fails gate discovery (Argon); study-folder tests are only flagged.
- Review stamp / hold A-20261018-5 blocks `tasks.py done` for T05/06/07/09 (not faked).
- Gate times: 2m33, 43s, 56s, 3m23, 2m40, 35s, ~20m (Argon with registration). Max gate wait 0. Reverts by me: 0. Peak workers: 6 (first ~20 min), then 1-3. CI green on every run seen. Worker turns 4-55; T07 55, T05 41, T09 40 over the 40 cap.
- Usage at start 18:48Z: 5h 13% (reset 21:10Z), week 34%. Take get_usage again at the 21:30Z report and at stop.

## Report status
20:00Z report: NOT SENT yet (watcher bg b8k5a05br fires at 20:00Z sys clock; if lost in a clear, send manually). Content = Cards + Score notes above, one line per card.
Last Doctor contact: ROTATE message (~19:55Z). Doctor asked: start no new workers; reply ROTATE-READY only when all workers/ships finished and recorded.

## Next action after rebuild
1. Rebuild: read this file, `python scripts/dev/sync.py where --all`, list_sessions {"linked": true}, `git cherry` per worktree, gh run list.
2. Verify T05 shipped (cherry 0); ship bt-engine-wire; ship finished new workers one at a time; ship notes.
3. Send 20:00Z report if not sent; 21:30Z; stop report by 22:50Z. No new workers after 22:20Z. Keep a live background wake every turn.

## Update 20:02Z (supersedes queue above)
lint-lookahead-false-positive-chunked-slices DONE: wt agent-ab98e197a6a0059b8, commit 14f1703b9 (lookahead_lint.py + MyTradingSys/tests/test_lookahead_lint.py), 17 turns.
gate-test-lease-timeout-under-load DONE (partly: 117s -> 80s, target 30s missed): wt agent-af05c70c26fd93566, commit 11850c8c7, 22 turns.
t09-f5 worker (ac8b2b68eddeaee06) waiting on its backtest run (interim notice), will report again.
SHIP CHAIN running as Monitor task bdxkro7il (script $TEMP/chain.sh): waits for T05 cherry 0, then ships sequentially bt-engine-wire (agent-a578ee348d9a30577), lint (agent-ab98e197a6a0059b8), lease (agent-af05c70c26fd93566); prints CHAIN lines per ship, stops on first failure. After chain: ship t09-f5 when its worker finishes, then notes, then reply ROTATE-READY. 20:00Z report SENT (queued to Doctor).
Operator rule 2026-10-25 via Doctor: ALL YouTube work goes to Gemini (lane CODEX, gemini_queue.py on JIS-NUC); no Claude worker for YouTube. Doctor rewrites yt-fabio-fetch-retry.
