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
| 2026-11-04 | c31-daily-short-upper-bb | Sonnet 5.5 | 0.51 | 27 | see result record; cap was 4.0 |
| 2026-11-04 | cbp-alt-coverage | Sonnet 5.5 | 0.38 | 19 | done, ship blocked by red CI; needs re-ship after trunk green; cap was 4.0 |
| 2026-11-04 | mts-home-rebuild-1103 | Opus 5.5 | 0.65 | 9 | wasted: card STOP valid, already superseded; no build; cap was 8.0 |
| 2026-11-04 | route-tag-closeout-1104 | Opus 5.5 | 4.63 | 3 | shipped ee29e31e (CI verdict pending); cap was 10.0 |
| 2026-11-04 | wt30-div-blind-recount-haiku-1104 | Haiku 5.5 | 0.01 | 4 | not built: card stale (scope changed 9a7a43033); cap was 2.0 |
