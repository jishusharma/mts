# Route-tag audit, 7 days of origin/fast-track (2026-10-28 .. 2026-11-04)

Operator 2026-11-04 (d-route-tag-every-session-1104): every session finishes with a note saying which pipeline the work goes to next.

## Counts (method below; `python scripts/dev/route_audit.py audit --days 7`, trunk at 7a057d919 + fetch of 2026-11-04)

| Class | Commits | Share of Result commits |
|---|---:|---:|
| Result commits (non-merge, body has `Result:`) | 2236 | 100% |
| Tool bookkeeping (claim/release/heartbeat, LAYERS regen, fold, desk, lane health, task closed, card-only, reverts) | 983 | 44% |
| Named where it goes next (a `Next:` line, a new card file in the commit, or routing words: tasks.py new, filed, follow-on, dead end, END:, BACKTEST_CANDIDATES, PRE_REG, shadow, hand-over, queued, companion/[GEMINI]/rederive card) | 265 | 12% |
| Picked up later (no route in the commit, but a card created after it names its output folder or file) | 315 | 14% |
| **Orphan output: a study/verdict/tool with no route and no later card** | **70** | **3%** |
| Other work with no route and no output file (docs, pages, config, fixes) | 603 | 27% |

Of the 1253 non-bookkeeping Result commits, 265 (21%) named their next step; 988 (79%) did not. 315 of those were rescued by a
later card, 70 study/tool outputs were never picked up, and 603 other commits stated no next step at all. Zero commits carried a
`Next:` line (the grammar did not exist).

## Method
- `git log origin/fast-track --no-merges --since=7d --name-status`, parsed per commit (no truncated output: counts come from the parser).
- Bookkeeping = `route_audit.EXEMPT_SUBJECT` (subjects written by sync.py, desk.py, context_gap.py, lane_health.py, tasks.py) or every
  file under `MyTradingSys/system/tasks/`, `claims/` or `LAYERS.md` (a card-only commit routes by itself).
- Output = a changed `research/*/(RESULT|REPORT|VERDICT|AUDIT|DEV_CHECK|FINDINGS)*.md` or a non-test `.py` under scripts/ or MyTradingSys/.
- Picked up = any card on trunk (open, done or archived) whose `created` is after the commit and whose JSON names the output file
  (generic names RESULT.md/REPORT.md/study.py/analyze.py skipped) or its `research/<folder>`. The card that ordered a study is created
  before it, so it does not count. Heuristic limits: routing words can be false positives ("queued" in another sense); a later card
  can name a folder for an unrelated reason. Both make the orphan count a floor, not a ceiling.

## 10 worst orphans (study/verdict/tool, nothing downstream) and the backfill card filed 2026-11-04
| sha | subject | next stage it should have named | card filed |
|---|---|---|---|
| 4fb3c2fb5 | rumers: DEV check of 5 frozen rules (0 PASS-DEV) | blind read, then END: no edge | route-rumers-dev-blind-read |
| 7501e2816 | cryptocred 4h/1d S3: power gate BLOCKS the DEV run | redesign to pass the power gate, or END | route-cryptocred-s3-power-unblock |
| 2877e1fed | G7: BTCUSDT stop-slippage proxy by volatility tercile | backtest cost model input | route-g7-slippage-into-cost-model |
| 7fcf21aa0 | multi-TF bias stack: DEV event study (no net edge) | blind read, then END: no edge | route-multi-tf-bias-blind-read |
| 108c58d8a | bb-state-regime-tf-map: blocked on data | run counts on the host holding tom_raw 1m | route-bb-state-map-run-counts |
| 20be1c6ec | H3 NY-open+180 new-low-holds (FAIL on n=6) | more symbols to reach n>=30, or END | route-h3-ny-open-more-symbols |
| 4a36c8a38 | T053 hedge variants (all worse than unhedged) | blind read, then END: no edge | route-t053-hedge-blind-read |
| ef9d10095 | wiring audit Malkan + Krown, 167 rules | one fix card per unwired rule | route-wiring-audit-fix-cards |
| d286be4a1 | cbp candidates() -> CANDIDATE_UNTESTED records | BACKTEST_CANDIDATES rows | route-cbp-candidates-to-backtest |
| dca8f6d49 | S2 M4 uptime heartbeat writer/reader | wire into the live runner (JIS-NB desk) | route-uptime-heartbeat-wire-live |

Not picked: the rsi_deep_buy commits (87a79ab32, 8849893da, 9f1aeacaa, ea442ac79) have open older cards (rsi-deep-crossvendor-review);
duplicate or reverted-then-relanded commits (9c43ee797, 0cc1b2000) and pre-feeder-rule tool .py files with no verdict.

## Earlier asks (the same requirement, rule-only, decayed)
- OPERATOR_DECISIONS.md "2026-11-03 - Everything in the pipeline": "get all discussed and planned items into pipeline".
- WORKERS.md rule 11 (`Noticed:` -> raw card) and ANNOUNCEMENTS A-20261104-1 (feeder rule: companion [GEMINI]/CODEX card per shipped study or .py).
- handoff_history/2026-10-12.md Q21: hand-over lines already ended `Next: ...` (a format; no script checked it).
- 11-04 scenario_ledger lesson: a rule in a doc decayed in 4 days with no script.

## What is enforced now
- `sync.py ship` refuses a ship whose non-bookkeeping commits carry no `Next: <card-id | stage | END: reason>` line, an unparseable tag,
  or a card id with no card file; fix in one line: `--next "<tag>"` (adds the line, or an empty `route tag` commit on a clean tree).
- `tasks.py done` requires `--next` (same grammar; `new:"<title>"` files the card raw and stores its id in the card's `next`).
- `route_audit.py check --days N` (Supervisor and coordinator boot) lists untagged Result commits since the gate went live, Next card
  ids with no file, and Next cards still open and untouched > 72 h; exit 1 when any.
