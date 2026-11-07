# Critical path 2026-11-08 (refine-batch-1108, Lead C credit batch, scoping only)

Built from origin/fast-track at f4e938467: PLAN_8H_2026-11-08, OPERATOR_DECISIONS (last 40), D7_ROADMAP (research/v1_plan_2026-10-20), ROADMAP_BOARD_2026-11-04,
BIBLE headings. STATUS.md is generated 2026-11-04 (4 days old): not used as a source. Protected news chain set by the operator is items 1-7 in his order.

## SUPERSEDED RULES (tested against every card before it was touched)
1. Phase-first testnet-forward replaces long backtest gates (d-phase-first-method-1106); mainnet still needs the fee-net out-of-sample record (testnet supplies it).
2. The 0.15 % minimum stop and the Habib candle-extreme stop are retired; a stop follows the trade (d-stops-follow-trade-1106).
3. Funding carry is dropped; direction is cycle-bottom longs plus session scalps/day/swing from Tom and Fabio levels (d-carry-dropped-leverage-direction-1106).
4. Argon direction: count over the window, fix the Java VA bug, then testnet-forward; no fixed core, no long backtest gate (d-argon-tom-fabio-review-1108).
5. Machinery growth is frozen: no new layers, sources, lanes, pages, rule docs or tools (D7 frozen list; week-plan move 5).
6. S0 closed unmet and S0 parking ended (d-s0-exit-waived-1103); S1 signed 11-04; D7 Now = S2, S3, S4 in parallel; S4 module e2e is done.
7. Layer ideas are not discarded before the simulator review (layer-review-after-simulator stays blocked); context layers are judged by distribution shift (11-03 order).
8. Credit path = api_job --engine api only (raw Messages API); claude -p, Agent SDK and cloud sessions are not credit paths (d-api-credit-raw-api-engine-1107).
9. Fable-named work runs on claude-fable-5-1 (added e5b96b6e9, card done); Opus 5.5 is the fallback.
10. No GPT/Codex credit (d-no-gpt-codex-credit-1106); the Codex lane returns 401 and is stalled.
11. News is research first: no weight, flash or bias rule is final until NEWS_DESIGN.md (d-news-research-first-reviews-synthesis-1108).
12. News is context for a hand decision, never a gate or an order; public repo, no account data.
13. A promoted config (D7 S5 entry) is no precondition for testnet trades of phase-first setups; a PASS claim still needs a VERDICTS row, causal replay, independent re-run.
14. Testnet only, never touch the live tree, HALT or orders; live-path and JIS-NB cards are owned by their lane.
15. Login A owns java-va, census, auction-plan, signal-broadcast (not refined here); Login C only monitors.

## The path (order they must run)
Precondition done: api-job-add-fable-model-1108 (e5b96b6e9). Item numbers 1-7 are the operator order; the brief said "1-6" but names seven cards.
1. news-headline-panel-tree-rest-1108 (protected). why now: d-news-is-live-aid-critical-1108. forces: producer of every headline the later layers read. State: news_feed.js + test shipped a65df6891, card still open (page wiring unverified).
   defect catch: test_news_feed.py fails pre-change (module missing); importance>=7 SOURCED (Tree), poll 15 s OURS.
2. news-effect-event-catalogue-1108 (protected). why now: d-news-research-first-reviews-synthesis-1108. forces: data before any review or weight.
   defect catch: weak (check_catalogue.py exists only after the build, no fail-first named); gaps listed, classes under 8 events reported unknown.
3. news-effect-review-opus-1108 (protected). why now: same decision. forces: reads the catalogue (2). defect catch: check_review.py is a structure check; 10 events re-checked is the real catch.
4. news-effect-review-market-lens-1108 (protected). why now: same decision. forces: blind to 3, reads 2; model Fable 5.1 now supported. defect catch: as 3.
5. news-design-synthesis-1108 (protected). why now: same decision. forces: needs 2, 3, 4 on trunk. defect catch: done_when makes it name a fail-first test for every rule it hands the builds.
6. news-weight-bias-flash-1108 (protected, blocked). why now: d-news-weight-bias-events-1108. forces: needs 5 and 8. defect catch: test_news_weight.py, 6 fixtures written first; every number commented SOURCED or OURS.
7. cbp-events-to-watch-wire-1108 (protected, blocked). why now: d-news-weight-bias-events-1108. forces: needs 5. defect catch: test_events_wire.py, 3-event fixture, fails pre-change.
8. gemini-blind-read-of-mytradingsys-tools- (refined now). why now: no initial defects in the panel (1) before 6 builds on it. forces: runs on the Gemini lane in parallel with 2-5; must be green before 6 starts.
   defect catch: report recomputes the importance>=7 count and the 12 newest ids from sample_tree_news.json; every DIFF names file:line.
9. java-va-state-asymmetry-fix-1108 (login A, raw). why now: d-argon-tom-fabio-review-1108 (root cause 4, pure bug). forces: bug fix before the census and the plan that read Java output.
   defect catch: card note names a Maven test (price above VAH keeps ct_short; below VAL puts short in dirs) that must fail pre-change; smoke gate --full.
10. auction-context-event-census-1108 (login A, raw). why now: d-argon-tom-fabio-review-1108 + d-phase-first-method-1106. forces: counts before the plan (13). defect catch: PRE_REG Context + Regime mix lint; thresholds labelled SOURCED/OURS; fee-net R.
11. fable-r3-stop-gap-early-return (SONNET, ready, added by the 11-08 second pass). why now: D7 S2 exit (restart drill) and every unattended testnet trade: on a restart with a filled entry and no journaled stop the manager halts with the position naked (R3 F-GAP-1, BLOCKS-LIVE). forces: a bug fix before the restart drill (12) that relies on it. Checked on origin/fast-track: position_manager.py:340-342 still raises ManagerHalted and scratch_r3/test_stop_gap_r3.py is still unmoved, so not built and not superseded.
   defect catch: MyTradingSys/execution/test_stop_gap_offline.py (moved from scratch_r3) must FAIL on the current code with the F-GAP-1 assertion before the fix; offline suite stays green; no formula in this card.
12. s2-halt-restart-drills (JIS-NB, refined, live path; operator runs the drills). why now: D7 S2 exit (HALT drill + restart drill, EXPECT before RESULT). forces: before an unattended testnet run (13) is trusted, after the stop-gap fix (11); depends state-code backfill (done).
   defect catch: test_drill_check.py: wrong value, missing key, unreadable RESULT, RESULT older than EXPECT each exit 1; numbers read from executor.py preflight lines 205-236.
13. auction-plan-testnet-forward-1108 (login A, raw). why now: d-phase-first-method-1106 (a pattern visible now goes to testnet). forces: needs 9 and 10 (restart safety 11, 12 first). defect catch: not yet testable (card raw, no done_when); the card note requires one scenario_ledger row per audit claim, so refinement must name a fail-first test.
14. ci-red-ship-gate-parity-1107 (refined now, ready). why now: trunk red 26.7 % (SHIP_HEALTH item 2), every ship above passes this gate. forces: independent lane (credit/A), position follows the operator credit order.
   defect catch: 3 new test_gate_select.py cases, one per top red class, each must fail on the old gate_select.py; counts from gh run view, top-3 cut-off labelled OURS.
15. cycle-bottom-long-testnet-trade-1106 (JIS-NB, raw, operator-called only). why now: direction 1 of d-carry-dropped-leverage-direction-1106; rule and flag are done (cycle-bottom-long-testnet-rule-1106).
   forces: waits for the flag line ENTRY OK. BLOCKED on a missing refinement: done_when empty, lane JIS-NB (skipped by order); a JIS-NB refiner must give it a done_when naming the logged trade and flag state.

## Blocked on a missing refinement
Items 9, 10, 13 (login A owns them, still raw) and 15 (JIS-NB lane). Items 6 and 7 wait for 5 by design.

## PARKED (not on the critical path)
Each carries the note line `PARKED 2026-11-08: <reason>`. Reasons in one line:
- Ship train machinery (frozen; item 13 is the ship-gate lever): ship-train-bisect-eject-signal, ship-train-cutover, ship-train-flake-floor, ship-train-runner, ship-train-shadow-week, gate-slow-steps-3xt-3sig-4f-1107, ship-record-gate-failure-step-1107, test-sync-py-step-3k-4-failed-once-on-wi.
- GPT/Codex lane (no credit, 401 stall): gpt-rederive-fabio-cvd-1108, gpt-rederive-pre-us-failed-break-10sym-1108, gpt-rederive-v-recovery-low-sweep-1108, gpt-rederive-wt-extreme-cross-1108, gpt-spec-tests-squeeze-1108, gpt-spec-tests-vfi-1108, labguy-gpt-card-no-model-identity-1104.
- Context-engine reviews (follow the path): gemini-blind-read-of-squeeze-py-bb-dev-q, gemini-blind-read-of-vfi-py-vfi-engine-f.
- Long-history DEV studies and cost-model inputs (rule 1): flip-engine-follow-up-session-adjusted-s, malkan-window-comparison-needs-a-wider-p, power-gate-holm-m-decision-1106, route-g7-slippage-into-cost-model, fabio-v3-funding-r-never-called.
- Live Aid display (serialise after 7, same build_artifact.py): live-aid-balance-acceptance-1105, live-aid-trendlines-liquidations-1106, live-aid-card-show-the-habib-daily-watch.
- CBP ingestion and parsers: cbp-daily-firing-gap, cbp-sync-fails-and-discord-reader-stopped-1104, fix-analyst-levels-py-parse-defects-anal, fix-malkan-div-trade-charts-py-display-d.
- DSA bridge and sessions tooling: dsa-seed-full-task-list-1107, dsa-block-stdout-utf8-1107, dsa-multi-chat-driver-1107, dsa-py-edit-refuses-json-state-anchor-js, role-loader-bare-login-a-injects-supervisor-1107, aibridge-desk-no-inject-after-075.
- Pages and MTS Home: mts-home-rebuild-1103, hub-waiting-list-stale-decisions-1106, republish-mts-home-and-mts-layers-stale-, pages-follow-builds-gaps-1107.
- Tooling and housekeeping: broadcast-hygiene-stale-and-b4c2dfe, gateway-prompt-card-must-exist, haiku-accept-review-stamps-must-check-fo, laptop-wake-path-from-desktop, main-folder-staged-blocks-ff, tasks-py-twins-crashes-on-cards-whose-sc, test-aibridge-chain-hidden-tab-test-test, weekly-plan-per-login-wired-into-supervi, desk-py-auto-ship-fails-on-dirty-live-tr, host-health-kill-tree-orphan-1107, mts-signal-py-acks-view-misses-ack-prese, sync-py-start-tidy-gateway-only-reads-cl, tasks-py-done-requires-next-and-rejects-.
- Operator review of the old setup catalogue: setup-review-with-operator.
Second pass 11-08 (same job, run on the tree already holding the first ship): added item 11; parked notes on aibridge-seed-bad-origin-1107, analyst-ingest-roman-x, gpt-spec-tests-cycle-ma-clock-1108, gpt-spec-tests-cycles-1108, indicator-map-1107, labguy-codex-host-401-lane-stalled-1104, studies-write-into-base-rates-registry, tvfav-usage-adx-1107.
Default PARKED (not on the path, not touched, no note added, owner lane decides): every other raw/refined/ready/blocked card not named above, e.g. JIS-NB and DSA lane cards, the Gemini blind reads loaded by PLAN_8H (run on the NUC lane, no credit), the OPUS/blocked research chains (tom-btc-*, rsi-deep-*, fable-run4/5). UNSURE: fable-run7-forward-test (is its 72-month forward-power design superseded by d-phase-first-method-1106?).
Closed in this batch: vfi-engine-1107 (6d39f63f4), wt30-div-blind-recount-haiku-1104 (990e9b8b8), pitchfork-operator-charts-prep (1dff1abde), session-planner-md-duty-0-code-red-lane- (1c2a874ec), route-cryptocred-s3-power-unblock (4be92a523, 5392a26aa); dropped test-ship-train-py-fails-on-git-2-24-hos (3c7102081), haiku-refine-argon-cards-1108.
