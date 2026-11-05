# Plan: spend the Claude API credit before it expires (operator 2026-11-04: "Use Claude Platform credits also! Plan for it as it is going to expire")

Credit: $100 promotional on platform.claude.com ("jis's Individual Org"), granted 2026-10-22, expires 2026-11-17 UTC. Spent to
2026-11-02: about $1 (api_batch runs, COST_FIGURES.md). Balance left: about $99 over 13 days = about $7.50 a day. No payment method
is on file, so a run that answers was paid by the credit; the console billing page is the only balance read (operator-only).

## What the credit can run (measured 2026-11-04 on JIS-NB)
| Lane | How | Measured | Use for |
|---|---|---|---|
| Headless builder | `claude -p` with `ANTHROPIC_API_KEY` from the key file, `--settings '{"disableAllHooks":true}'`, `--permission-mode bypassPermissions`, `--max-budget-usd <n>`, own worktree, output to `F:/MTS/api_runs/<card>/` | probe: Haiku answered, $0.004, 32.8k cached input | SONNET-lane build/research cards with a clear done_when |
| Batch (half price) | `scripts/dev/api_batch.py submit jobs.jsonl --max-usd <n>` | 6 Haiku reads about $0.30 (11-02) | blind re-reads, quote checks, recounts, label passes |
| One hard question | `api_batch.py` single job on Opus/Fable, `--max-tokens 32000` | Fable run-5 rerun about $0.69 to $1.38 | design reviews with no tool use |

Hooks note: the repo's `$CLAUDE_PROJECT_DIR` hooks do not resolve under a nested headless run (they look for `C:\scripts\dev\...`),
so `disableAllHooks` is required; the Builder prompt carries the CLAUDE.md rules it would otherwise get from hooks. The key never
appears in a prompt, argument, log, signal or commit (`export ANTHROPIC_API_KEY="$(tr -d '\r\n ' < F:/ClaudePlaform/key.txt)"`).

## Allocation (OURS, by card value, not by headroom)
| Day(s) | Job | Lane | Cap | Why it is worth the credit |
|---|---|---|---|---|
| 11-04 | rumers-testable-rules-dev-backtest (5 frozen rules, DEV fee-net, DEV_CHECK.md + VERDICTS rows) | headless Sonnet | $15 | operator asked today; S3 funnel gets 5 new tested rules; extraction done, never run |
| 11-05 | 4 Gemini blind-read cards (prob_table, trendlines, us_open_oos, wavetrend) as Haiku batch jobs | batch | $2 | they sit in the CODEX lane with no reader; recounts are batch-shaped |
| 11-05 | haiku-refresh-stale-ready-cards-1104 | headless Haiku | $3 | 19 ready cards carry STALE markers; mechanical |
| 11-06 | research-pass-needs-rerun-gate guard + research-lint-warn-not-revert | headless Sonnet | $10 | week-plan move 2 prerequisite (PASS rule guard) |
| 11-06 | s2-uptime-heartbeat-jis-nb (test-first) | headless Sonnet | $10 | week-plan move 3, S2 M4 |
| 11-07 | s4-cbp-module-e2e | headless Sonnet | $10 | week-plan S4, builder lane, no operator input |
| 11-08 | setup-review-with-operator pages (one page per catalogued Tom/Fabio setup) | headless Sonnet | $8 | prep for the operator's review sitting, read-only inputs |
| 11-09..16 | second pass on whatever the week leaves: rsi-deep-prereg + engine, sim-continuous-strip, test-sync-py flake | headless Sonnet | $30 | S3 next-in-line and sim page |
| reserve | - | - | $11 | reruns of a failed job (one retry each, never a loop) |

Rules: one headless job at a time per machine; every job gets `--max-budget-usd`; a job that fails twice is a card note, not a third
run; results ship through `sync.py ship` like any Builder; the launcher records the job's cost from the result JSON in
the Spent ledger below the same day (COST_FIGURES.md is the fee-figure note, not a ledger). Cards that need the operator (fable-run7, c26-phase2) or the live tree never go here.

## Launch recipe (this machine or JIS-NUC, both hold the key file)
```
python scripts/dev/sync.py start <slug>                      # prints WORKTREE
export ANTHROPIC_API_KEY="$(tr -d '\r\n ' < /f/ClaudePlaform/key.txt)"
env -u CLAUDE_CODE_OAUTH_TOKEN -u CLAUDECODE claude -p "$(cat prompt.txt)" --model claude-sonnet-5-5 \
  --permission-mode bypassPermissions --settings '{"disableAllHooks":true}' --max-budget-usd 15 --max-turns 200 \
  --output-format stream-json --verbose < /dev/null > F:/MTS/api_runs/<card>/out.jsonl 2> F:/MTS/api_runs/<card>/err.txt
```
Run it from the worktree, in the background; the last line of out.jsonl is the result record (cost, turns, final text).

## Spent (from the result record of each run)
| Date | Job | Model | Cost USD | Turns | Outcome |
|---|---|---|---|---|---|
| 2026-11-04 | rumers-testable-rules-dev-backtest | Sonnet 5.5 | 1.26 | 49 | shipped 561df2f0; 0 of 5 rules pass DEV; cap was 15 |
| 2026-11-04 | haiku-refresh-stale-ready-cards-1104 (pulled forward from 11-05) | Haiku 5.5 | 0.04 | 24 | shipped 6c92942e; stale 22 -> 4 (the 4 left are tasks-dir churn); card not closed (done_when needs 0); cap was 3 |
| 2026-11-04 | haiku-review-1 (8 coordinator-stamped cards, tasks.py check + scope read) | Haiku 5.5 | 0.03 | 23 | 6 ACCEPT, 2 HOLD (krown-hidden-divergence-confluence-feed scope file missing; s1-signal-v1-schema-seam-test already on trunk 29d7c85a4); job could not write stamps (prompt named `tag --line`, which only annotates `--add`), Lead wrote them from the verdict table; cap was 2 |
| 2026-11-04 | haiku-review-2 (4 re-run cards, stamps written into the note by the job) | Haiku 5.5 | 0.02 | 12 | shipped feb0ad85f; 2 ACCEPT (wavetrend-c30-retest-rsi-session, bb-range-to-range-by-session), 2 HOLD (bb-range-retest-level-arm scope folder not yet created; rsi-divergence-chart-draws-used-pivots raw, empty fields); flagged a SOURCED label with no transcript line (Tom session claim) for relabel; cap was 2 |
| 2026-11-04 | haiku-stale-review-1104 (9 unstamped STALE ready cards, tasks.py check + scope read, stamps written by the job) | Haiku 5.5 | 0.03 | 18 | 4 ACCEPT (mts-home-rebuild-1103, sim-continuous-strip, sim-desk-tom-fabio-studies, test-sync-py-step-3k-4); 5 HOLD; 9 cards stamped in note; cap was 3 |
| 2026-11-04 | probe-launcher-1104 | Haiku 5.5 | 0.01 | 1 | launcher end-to-end probe: PROBE OK (detached run, stdin prompt, result record parsed); cap was 0.05 |
| 2026-11-04 | haiku-review-ready-sonnet-1104 | Haiku 5.5 | 0.25 | 35 | 24 cards stamped 15 ACCEPT/4 HOLD/5 DROP, shipped df2f8e5a; J3,J4 skipped (cards shipped 5ea4d7457e19, d286be4a1447); cap was 2.0 |
| 2026-11-04 | ship-train-design-1104 | Opus 5.5 | 1.29 | 25 | DESIGN.md shipped cf765e87; 56 red runs: 38 real 18 flaky; cap was 6.0 |
| 2026-11-04 | research-lint-warn-not-revert | Opus 5.5 | 1.79 | 43 | lint warn-not-revert analysis shipped; 9 of 20 reverts docs/data-only; cap was 6.0 |
| 2026-11-04 | setup-review-with-operator | Opus 5.5 | 0.57 | 7 | nothing to build; card refreshed READY, 0/22 setups have operator verdict (needs Eagle_Eyes sitting); cap was 8.0 |
| 2026-11-04 | longdev-bb-range | Sonnet 5.5 | 0.41 | 15 | see result record; cap was 6.0 |
| 2026-11-04 | gem-review-wavetrend-1104 | Haiku 5.5 | 0.04 | 17 | shipped 3515fd34a; 5 of 5 numbers agree with Gemini's MATCH; cap was 1.0 |
| 2026-11-04 | c31-daily-short-upper-bb | Sonnet 5.5 | 0.51 | 27 | see result record; cap was 4.0 |
| 2026-11-04 | cbp-alt-coverage | Sonnet 5.5 | 0.38 | 19 | done, ship blocked by red CI; needs re-ship after trunk green; cap was 4.0 |
| 2026-11-04 | mts-home-rebuild-1103 | Opus 5.5 | 0.65 | 9 | wasted: card STOP valid, already superseded; no build; cap was 8.0 |
| 2026-11-04 | wt30-div-blind-recount-haiku-1104 | Haiku 5.5 | 0.01 | 4 | not built: card stale (scope changed 9a7a43033); cap was 2.0 |
| 2026-11-04 | gem-review-three-1104 | Haiku 5.5 | 0.42 | 37 | shipped 5bf57ce75; RSI and BB reads MATCH with 4 of 5 (1 slip at the 4th decimal each, cards open), Fabio MATCH 5 of 5; cap was 2.0 |
| 2026-11-04 | sim-news-concept-tabs-1104 | Sonnet 5.5 | 0.42 | 16 | built, ship refused (CI red); needs re-ship when trunk green; cap was 4.0 |
| 2026-11-04 | route-tag-closeout-1104 | Opus 5.5 | 5.50 | 18 | shipped ee29e31e, reverted for red CI; reland job running; cap was 10.0 |
| 2026-11-04 | gem-review-three-b-1104 | Haiku 5.5 | 0.37 | 59 | shipped abcce966e; 15 of 15 numbers agree across BB retest, BB range-to-range, sim C30 banner; cap was 2.0 |
| 2026-11-04 | route-tag-reland-1104 | Sonnet 5.5 | 0.49 | 32 | shipped 6e07fe14; trunk CI red after it (wiring steps 3w/3x), Super notified; cap was 6.0 |
| 2026-11-04 | labguy-context-filter-two-class-labels-1104 | Haiku 5.5 | 0.02 | 13 | done; ship status unverified; cap was 1.0 |
| 2026-11-04 | route-tag-reland3-1104 | Sonnet 5.5 | 0.20 | 10 | done; trunk CI queued at finish; cap was 8.0 |
| 2026-11-04 | labguy-context-filter-two-class-labels-1104 | Haiku 5.5 | 0.03 | 5 | second run of the same card; quick gate still running at finish; cap was 1.0 |
| 2026-11-04 | gem-review-spec-1104 | Haiku 5.5 | 0.06 | 22 | shipped f908b25e6; 10 of 10 findings confirmed, 6 raw cards; cap was 1.5 |
| 2026-11-04 | codex-spec-tests-scope-1104 | Sonnet 5.5 | 0.36 | 13 | shipped c72495e3b; spec-test audit cards may write the test files they name; 4 new tests; cap was 4.0 |
| 2026-11-04 | codex-audit-no-pass-1104 | Sonnet 5.5 | 0.35 | 16 | shipped 9d10d1a7b; audit and run results starting PASS close as SOUND; cap was 3.0 |
| 2026-11-04 | gem-review-chain-1104 | Haiku 5.5 | 0.03 | 16 | shipped 847811b78; 3 cards closed, 16 spot-checks agree, 1 raw card; cap was 2.0 |
| 2026-11-04 | codex-spec-tests-tsv-1104 | Sonnet 5.5 | 0.29 | 17 | shipped 792a88a37; spec-test cards may add their own test line to extra_tests.tsv; cap was 3.0 |
| 2026-11-04 | sim-desk-tom-fabio-studies | Opus 5.5 | 4.20 | 75 | shipped per-trade replay files (DEV window); cap was 6.0 |
| 2026-11-04 | salvage-unshipped-branches-nuc-1103 | Sonnet 5.5 | 0.39 | 12 | shipped DECISIONS.md: 1 SHIP, 6 DROP; cap was 3.0 |
| 2026-11-04 | sim-malkan-close-div-trade-chart-1104 | Opus 5.5 | 1.70 | 45 | shipped per-trade Malkan close-divergence chart on sim page; cap was 3.0 |
| 2026-11-04 | haiku-review-3b-1104 | Haiku 5.5 | 0.02 | 11 | stamped 3 cards: pz-4 ACCEPT, wavetrend-c1-v2 DROP (twin shipped), level-approach ACCEPT; cap was 2.0 |
| 2026-11-04 | liquidations-mirror | Sonnet 5.5 | 0.54 | 22 | shipped liq_mirror.py (runtime liq_events mirror to F:/MTS); cap was 4.0 |
| 2026-11-04 | c31-reland-1104 | Sonnet 5.5 | 0.61 | 23 | J8 re-land shipped 07e1e7a17: costs from fees.py, allowlist rows for 3 fwd-index hits; C31 UNDERPOWERED n=15; cap was 4.0 |
| 2026-11-04 | malkan-card-fix-1104 | Sonnet 5.5 | 0.59 | 20 | shipped 240a2e618; 8 of 8 findings confirmed, card fixed and stamped; cap was 2.0 |
| 2026-11-04 | codex-next-line-b-1104 | Sonnet 5.5 | 0.17 | 9 | not shipped; fixture fixed, next gate failure reported; cap was 2.0 |
| 2026-11-04 | codex-next-line-1104 | Sonnet 5.5 | 0.40 | 18 | not shipped; commit line written, gate failed on the route audit fixture; cap was 3.0 |
| 2026-11-04 | codex-next-line-c-1104 | Sonnet 5.5 | 0.11 | 5 | shipped 89482fbfe; Codex commits carry a Next line; cap was 2.0 |
| 2026-11-04 | level-approach-study-daily-last-lower-hi | Sonnet 5.5 | 0.80 | 1 | shipped C15 level approach study + lookahead allowlist rows (33470c3ec, 6e04f85d8); cap was 5.0 |
| 2026-11-04 | wt-extreme-cross-1104 | Opus 5.5 | 2.25 | 2 | shipped WT extreme-cross bounce study f72763f16 + Gemini feeder card; cap was 8.0 |
| 2026-11-04 | wall-ledger-1104 | Opus 5.5 | 1.11 | 22 | shipped offline wall ledger (15 tests, 4 mutants killed); cap was 6.0 |
| 2026-11-04 | worktree-gone-1104 | Opus 5.5 | 0.34 | 8 | done; see trunk for the ship; cap was 6.0 |
| 2026-11-04 | bisect-eject-1104 | Opus 5.5 | 0.42 | 10 | no code: depends on train.yml (ship-train card 3 not buildable yet); cap was 6.0 |
| 2026-11-04 | wt-spec-fixes-1104 | Sonnet 5.5 | 0.34 | 14 | 4 WT SPEC cards fixed in SPEC.md (m=14, k=3 OURS), shipped; cap was 5.0 |
| 2026-11-04 | eth-data-gap-1104 | Sonnet 5.5 | 0.36 | 22 | ETHUSDT 1m 2022-01..2026-09: 57 months, 0 missing bars; cap was 3.0 |
| 2026-11-04 | run-v3-l3-test-1104 | Sonnet 5.5 | 0.23 | 9 | added full-path test test_days_limit_full_path_produces_oos; 14 tests pass; cap was 3.0 |
| 2026-11-04 | testnet-fast-lane-1104 | Sonnet 5.5 | 0.32 | 15 | shipped design note eeec191e (testnet signal fast lane); cap was 3.0 |
| 2026-11-04 | haiku-review-ships-1104 | Haiku 5.5 | 0.03 | 17 | recount of 4 result files: 2 MATCH, 1 DIFF (sim_desk 341 vs 337 known), 1 NOT CHECKABLE; ac5b28b2; cap was 2.0 |
| 2026-11-04 | route-wiring-1104 | Opus 5.5 | 0.51 | 14 | filed 43 raw wire cards (32 Krown, 11 Malkan) from the wiring audit; cap was 6.0 |
| 2026-11-04 | haiku-review-4-1104 | Haiku 5.5 | 0.03 | 11 | stamped 5 cards (see table); cap was 2.0 |
| 2026-11-04 | malkan-window-land-1104 | Sonnet 5.5 | 0.34 | 16 | shipped 856f44e3; 12/18 window has no Malkan source, 4 of 4 thresholds confirmed; cap was 2.0 |
| 2026-11-04 | ms-bb-eth-1104 | Opus 5.5 | 3.51 | 84 | BB range retest pooled BTC+ETH: still INCONCLUSIVE; cap was 7.0 |
| 2026-11-04 | ms-wt-volmatch-1104 | Opus 5.5 | 2.41 | 52 | WT extreme cross vs ATR-matched baseline on BTC+ETH: VOLATILITY-ONLY; cap was 7.0 |
| 2026-11-04 | ms-level-eth-1104 | Opus 5.5 | 2.49 | 56 | C15 level approach replicated on ETH: narrow agreement; cap was 7.0 |
| 2026-11-05 | extra-tests-root-path-1105 | Sonnet 5.5 | 0.28 | 8 | Test runner gives children the repo root; Codex lab results land again; cap was 1.5 |
| 2026-11-04 | wire-krown-a-1104 | Sonnet 5.5 | 0.66 | 18 | 5 Krown wire cards (see trunk); cap was 4.0 |
| 2026-11-04 | wire-krown-b-1104 | Sonnet 5.5 | 0.49 | 16 | 4 Krown wire cards built; ship pending in gate; cap was 4.0 |
| 2026-11-05 | haiku-review-refined-1105 | Haiku 5.5 | 0.04 | 32 | stamped 7 refined cards: 1 ACCEPT, 6 HOLD; cap was 2.0 |
| 2026-11-05 | anticipation-map-1105 | Opus 5.5 | 2.61 | 56 | see trunk for the anticipation map ship; cap was 7.0 |
| 2026-11-05 | level-approach-prep-1105 | Opus 5.5 | 2.21 | 46 | built; ship in gate at job end (verify on trunk); cap was 7.0 |
| 2026-11-05 | critical-test-w2-1105 | Opus 5.5 | 2.73 | 67 | critical test wave 2: rows 6 FINDING, 7 FINDING, 8 UN(measured); see trunk; cap was 7.0 |
| 2026-11-05 | haiku-review-refined-1105b | Haiku 5.5 | 0.12 | 19 | stamped 18 cards: 9 ACCEPT, 7 HOLD, 2 DROP; cap was 2.0 |
| 2026-11-05 | pitchfork-fixes-1105 | Opus 5.5 | 1.55 | 35 | 6 pitchfork desk/python fixes shipped (702d...); cap was 6.0 |
| 2026-11-05 | spikefade-wave1-1105 | Sonnet 5.5 | 1.47 | 45 | 3 spikefade/wave1 cards shipped as one change 8eda7d8a; cap was 4.0 |
| 2026-11-05 | oi-toptrader-1105 | Opus 5.5 | 1.03 | 22 | OI top-trader fetch script; fetch was still running at job end (verify on trunk); cap was 6.0 |
| 2026-11-05 | session-handoff-audit-1105 | Opus 5.5 | 0.90 | 24 | shipped da963242 (session/handoff ship-speed audit); cap was 5.0 |
| 2026-11-05 | 4b3-successor-wake-1105 | Opus 5.5 | 0.44 | 11 | no build: card already done on trunk, closed; cap was 6.0 |
| 2026-11-05 | haiku-review-refined-1105c | Haiku 5.5 | 0.22 | 25 | stamped 20 cards: 5 ACCEPT, 9 HOLD, 6 DROP; cap was 2.0 |
| 2026-11-05 | ci-auto-revert-1105 | Opus 5.5 | 1.05 | 30 | shipped scripts/dev/ci_revert.py (finds the commit that turned CI red and proposes the revert); cap was 6.0 |
| 2026-11-05 | gate-fix-6-1105 | Opus 5.5 | 1.20 | 39 | promotion gate min trade count from effect size (gate-fix-6); ship verified separately; cap was 6.0 |
| 2026-11-05 | ship-signal-1105 | Sonnet 5.5 | 0.68 | 36 | ship signal done only on completed ship; 15 min repeat window (848838d1); cap was 3.0 |
| 2026-11-05 | successor-wake-1105b | Sonnet 5.5 | 0.34 | 8 | already on trunk, nothing new; cap was 3.0 |
