# Supervisor C notes: Pilot 2 (6 workers, 4 h, rotation on). Rewritten every wake.

Window: start ~18:50Z 2026-10-24, stop starting 22:20Z, hard stop 22:50Z. Login C JIS-NB. Doctor session: local_bf48e37d-ceba-4d0e-94fe-330458b891ac (reports 20:00Z, 21:30Z, stop; at once on CI red / blocker / gate>30 min).
Plan doc: MyTradingSys/research/mts_doctor/PILOT_super_session_2026-10-24.md. Rule: one ship at a time (I ship from the worker's worktree after `git cherry` of previous is empty); workers commit only, never ship, never touch run_extra_tests.py / run_all_tests.py (registrations batched by me in one ship).
ROTATE protocol: on ROTATE from Doctor: no new workers, let running finish, rewrite this file, stop watchers, reply `ROTATE-READY`. Rebuild from this file + card board + git cherry + list_sessions {"linked": true}.

## Frozen card list (2026-10-24 18:50Z, from tasks.py dispatch; shipped already: T04, sim-dashboard-v1, habib-holdout, mid-turn-image)
RUN (6): dsa-audit-05-placebo-nulls (scripts/T05/, T05_*.md) | dsa-audit-06-cost-fill-realism (T06) | dsa-audit-07-stale-verdicts (T07) | dsa-audit-09-live-parity (T09) | t02-f1-review-allowlist-chunk-4 (lookahead_allowlist.tsv, T02/f1_rows.py, T02_F1_chunks.tsv, lookahead_lint.py) | tasks-py-check-rewrites-other-cards-mark (scripts/dev/tasks.py + test_tasks*)
SPARE (2): cbp-add-channel-latest-n-to-fetch-captio (fetch_captions_timed.py, test, .gitignore) | context-conditioned-session-flow-states (new dir research/session_flow_context_2026-10-18/; B-SHARED, needs review)
Excluded: hook-reminder (new hook, freeze spirit), analyst-ingest-roman-x (stale per Doctor), rv05-h2 / bt-engine-wire (deps/critical), JIS-NB machine cards, lab/YT/Gemini/AWS cards.
Disjoint check: T05/T06/T07/T09 = new files in separate dirs; t02 = lint/allowlist files; tasks.py alone. Central files: none held.

## State (rewritten 18:55Z)
Workers running (Sonnet Agents, own worktrees, started ~18:53Z; they commit only, I ship):
- aeff7478879c89c20 dsa-audit-05-placebo-nulls
- a98795da9ab134b19 dsa-audit-06-cost-fill-realism
- a1089c4267107ce94 dsa-audit-07-stale-verdicts
- a401dace18fdc5813 dsa-audit-09-live-parity
- a0e64b1f86498d923 t02-f1-review-allowlist-chunk-4: DONE 19:0xZ, card was already reviewed (c68e93ced300), 4 turns, card-done commit 50b93be91 shipped
- ae4cea31ac539a0b2 context-conditioned-session-flow-states (spare 2, started ~19:05Z, worktree: find via sync.py where --all)
- a948ff46879f9b963 cbp-add-channel-latest-n-to-fetch-captio (spare 1, started ~19:00Z)
- a8783e71ee944c683 tasks-py-check-rewrites-other-cards-mark: DONE, 6 turns, commit 753075e76, worktree agent-a8783e71ee944c683; SHIP IN PROGRESS ~19:05Z (log $TEMP/ship_tasks.log, bg task b8zk6p3r9); verify git cherry empty
Worktrees: in each worker's final report (find via `sync.py where --all`).
Central-file holders: none. Ship queue: empty. T07 SHIPPED (13 files, 3m23s, after I fixed one lint fwd-index false positive in t07_docdrift.py), T06 SHIPPED (10 files, 2m40s). Both cherry 0 at 19:11Z. Cards 06/07 not marked done (review stamp + A-20261018-5 hold).
Shipped+verified earlier: t02 card-done, tasks.py fix, cbp, flow-states, notes.
Registration batch (one ship at end; forces full gate, only if time): run_extra_tests.py EXTRA += T07/test_rerun_diff.py, T06/test_cost_inventory.py, session_flow_context_2026-10-18/test_build_rows.py (+T05, T09 tests).
Cards needing a review stamp/clear of A-20261018-5 hold to mark done: dsa-audit-06, -07 (and likely 05, 09): report to Doctor.
T09 SHIPPED 19:20Z (7 files, 35s, after lint fix in exit_analysis.py), cherry 0. T09 follow-ups for Doctor/board: raw cards for F4,F5; desk row for F1-F3 (live-path: volume_fvg mirror side 0/24, RSI uncovered events, unbacktested 1%/2%/8-bar bracket) - not created yet.
Running (19:21Z): T05 aeff7478879c89c20; extra cards added to use slots: argon-fix-defects-and-re-land a0724398b018e0ac4 (sonnet), yt-fabio-fetch-retry a8391044ff8788666 (haiku). 3 of 6 running. Gate times so far: 2m33, 43s, 56s, 3m23, 2m40; max gate wait 0; reverts 0; CI green.
Decisions (OURS): ships serialised by me from worker worktrees; test registration batched into one ship at end.
Usage 18:48Z: 5h 13% (reset 21:10Z), week 34%.
Next action: wait for worker completions (notifications), then ship one at a time; Doctor report 20:00Z.
Last Doctor contact: none yet. Reverts 0. Peak workers 6. Max gate wait 0.

## Update 19:30Z
T05 done (wt agent-aeff7478879c89c20, commit c7f5eefb8, 41 turns; card not closed: stamp+A-20261018-5 hold; lint pre-checked 0 new). S1: touched-only distance-matched random-line control makes all 12 LC1 families DROP (8 published KEEPs don't survive); raw card cmd in T05 report section 8, not created.
Ship IN PROGRESS: argon-fix ad987950b + EXTRA registration of scripts/dev/test_argon_blind_read.py (wt agent-a0724398b018e0ac4, bg bzy6c6trg, log $TEMP/ship_argon.log; full-ish gate, 62 steps). Queue next: T05, then yt-fabio-fetch-retry (a8391044ff8788666 haiku, still fetching captions in bg).
Shipped so far (7+notes): t02, tasks.py, cbp, flow-states, T07, T06, T09. Argon pending.
Pending report items for Doctor: cards 05/06/07/09 need Lab_Guy REVIEWED stamp / A-20261018-5 hold cleared to close; T09 live-path follow-ups; T05 S1 raw card.

## Update 19:52Z
Argon SHIPPED 19:47Z (~20 min gate incl. EXTRA registration of test_argon_blind_read.py; cherry 0). yt-fabio-fetch-retry: 0/3 (HTTP 429 all videos), no commit, card left open (its worktree has an uncommitted wrong 'done' on the card json: discard, do not ship). T05 SHIPPING (bg bam9ocivm, log $TEMP/ship_t05.log).
Doctor 19:48Z asked to fill slots. Ready queue is nearly empty of eligible cards (rest: JIS-NB/CODEX/DSA lanes, review-stamp-needing, new-hook, stale-flagged, declutter). Started bt-engine-wire-real-funding-rsi-cc-rerun (sonnet, 19:52Z). gap-g7-stop-slippage deferred (shares bt_data.py with it). No sim-v2 backfill cards seen on board.
For score: test_lease.py exceeds the 240 s gate limit when CPU is at 100% (sim-v2 lost 2 ships); Fabio fetch 429 on all 3 videos.

## Update ~19:58Z
bt-engine-wire DONE (wt agent-a578ee348d9a30577, commits c0c5b7ea0 reapply + 9be3f415e lint fix; 8 turns); NOT yet shipped: queue = T05 (in flight, bg bam9ocivm) -> bt-engine-wire. Card not marked done.
Doctor-supplied cards started (sonnet, own worktrees): lint-lookahead-false-positive-chunked-slices ab98e197a6a0059b8; gate-test-lease-timeout-under-load af05c70c26fd93566; t09-f5-funding-cvd-fade-backtest-at-1h ac8b2b68eddeaee06 (told not to touch bt_data.py). 3 workers running.
T09-F1..F4 raw live-path cards: leave alone. Report at 20:00Z due.
