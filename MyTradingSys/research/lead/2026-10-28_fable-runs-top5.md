# Fable runs: top 5, ready to paste (Lead thinker, login C, 2026-10-28)

Each run is ONE session, ONE paste, no messages in between. Model Fable 5.1, effort high. Each prompt carries its own usage guard,
its inputs (files that exist on trunk today), its output file and its stop rule. Run them in rank order; the top 3 are the ones to run first.
Rule used to rank: Fable is only worth its quota where the job is judgement over many documents (verdict, design, adversarial review),
never recount or build (those go to Sonnet).
Status of the inputs, checked 2026-10-28: gross-effect screen = INCONCLUSIVE (T n=40, MDE 0.365 % vs 0.14 % cost; power gate needs 2,427 days, DEV has ~912);
backtest-vs-live audit t09 = backtests do not describe live for 5 layer families; ETH 1m data = 0 files; G3 blind marking dropped for live validation;
one reset-radar and one live-validation card filed today. No layer has a fee-net out-of-sample pass yet (STATUS.md).

| Rank | Run | Question it settles | Output file | Est. turns |
|---|---|---|---|---|
| 1 | EDGE-OR-STOP verdict | Is there any path left to a fee-net edge, and which single experiment decides it? | `research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md` | 30 |
| 2 | MAKE-IT-ANSWERABLE pre-registration | How do we get a test with enough power without burning sealed data? | `.../R2_POWER_PREREG.md` | 30 |
| 3 | LIVE-PATH red team | What would lose money or fail open the day a layer goes live? | `.../R3_LIVE_REDTEAM.md` | 35 |
| 4 | OVERHEAD CUT list | What can we stop doing (67 % non-research commits, 33 % overhead, lost quota)? | `.../R4_OVERHEAD_CUTS.md` | 25 |
| 5 | LIVE-VALIDATION protocol review | Does "one operator verdict per category, look-alikes inherit" hold up statistically? | `.../R5_VALIDATION_PROTOCOL.md` | 25 |

Common header for every prompt (already inside each one): boot per CLAUDE.md steps 1-2 (`sync.py start`, STATUS.md), `get_usage` first and last
into `research/fable_runs_2026-10-28/USAGE.md` (UTC, all meters, source get_usage), stop and ship if weekly all-models rises 4 points.
Never read VALIDATION or HOLDOUT data, never run mainnet, never read `.secrets/`. Expected numbers come from `backtest/layers/FORMULAS.md`, not from code.
Operator-facing reply: bold result line, max 8 lines.

---

## R1. EDGE-OR-STOP verdict (rank 1)

```
MTS Fable session R1. Boot per CLAUDE.md steps 1-2. Usage guard: get_usage first and last into research/fable_runs_2026-10-28/USAGE.md; stop and ship if weekly all-models rises 4 points.
Do not read VALIDATION/HOLDOUT; do not run backtests; this is a reading and reasoning run.

QUESTION: After everything run so far, is there a credible path to a fee-net, out-of-sample edge on BTC, and what is the single cheapest experiment that would confirm or kill it?

READ (primary files, not summaries; re-derive one number per item you rely on from FORMULAS.md or the raw result file):
- research/gross_effect_screen_2026-10-15/ (PRE_REG and the INCONCLUSIVE result), research/fable_major_run/CARD_2026-10-20.md (power: 2,427 days needed vs ~912)
- research/layer_lab/TRIALS.md (count of tries: how many comparisons have been made on DEV)
- research/audits_2026-10-26/FABLE_FULL_AUDIT.md, research/layer_lab/reports/*t06*, *t07*, *t09* (cost/fill realism, stale verdicts, live parity)
- research/sim_desk/results/*.json and research/sim_desk/ROADMAP.md (what the simulator found: levels -0.12 R filled, RSI ~0 R)
- MyTradingSys/research/STATUS.md gate board; backtest/layers/FORMULAS.md section on fees.

DELIVERABLE research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md (max 3 pages):
1. One-line verdict per candidate family (Tom, Fabio, Malkan, Krown, levels, RSI/WaveTrend, funding carry): ALIVE / DEAD / UNTESTABLE-AS-BUILT, each with the file:line that decides it.
2. The multiple-comparisons bill: tries so far (from TRIALS.md), and the t-stat a new result needs to survive them (state the formula and the source; mark OURS where chosen).
3. What a fee-net edge must look like given 0.14 % round trip + 0.02 % slippage: minimum gross effect per trade, minimum trades, minimum days.
4. Ranked list of the 3 experiments with the highest information per unit of quota, each with cost (turns, data needed), the pass rule fixed in advance, and what we stop doing if it fails.
5. A STOP list: work that cannot change the verdict and should be paused (do not delete anything).
Label every number SOURCED (file:line) or OURS. Ship with `sync.py ship`, Result: the verdict table. Reply in 6 lines max.

EXPECTED OUTPUT: the md file above; verdict table with 7 rows; a 3-row ranked experiment list; USAGE.md with before/after.
```

---

## R2. MAKE-IT-ANSWERABLE pre-registration (rank 2)

```
MTS Fable session R2. Boot per CLAUDE.md steps 1-2. Usage guard as in R1. DEV window only for any number you compute; VALIDATION and HOLDOUT stay sealed.

QUESTION: The gross-effect test is unanswerable on DEV (need ~2,427 days, have ~912). Design the cheapest way to make a test answerable without leaking sealed data or inflating false positives.

READ: research/fable_major_run/CARD_2026-10-20.md, research/gross_effect_screen_2026-10-15/PRE_REG.md, research/sim_desk/ROADMAP.md section 2 (why data is small), research/sim_desk/studies/_bars.py (SYMBOL_PARAM, ROOT), layer_lab/TRIALS.md, ANNOUNCEMENTS.md A-20261018-2.

DELIVERABLE research/fable_runs_2026-10-28/R2_POWER_PREREG.md, a pre-registration a Sonnet session can run mechanically:
1. Options table: (a) ETH/SOL 1m for the same DEV months, pooled with BTC, (b) BTC before 2022, (c) coarser horizons, (d) event definitions with more events, (e) one sealed-window read. For each: events gained, MDE at 80 % power vs 0.14 % cost, dependence between assets (state how you correct for correlated events), data cost, what the operator must approve (a sealed-window or lock change goes to him as a one-line ask, everything else takes the conservative default).
2. Chosen design with the exact rule: universe, event definition, cooldown, delay after bar close, horizons, effect measure, pass/fail threshold, multiple-comparison correction. Fixed before any data is looked at.
3. Leakage checklist (timestamps at or after the sealed cut refused, as in sim_desk cache validation) and the traps list (gap-stop booking, fills never reached).
4. One task card per step, lane SONNET, with a test that fails on the old code. File them via tasks.py new/fill; run `tasks.py check` and revert any other card it rewrites.
Label SOURCED or OURS. Ship; Result: chosen design + MDE number. Reply in 6 lines.

EXPECTED OUTPUT: the pre-reg md, options table with MDE per option, 3-5 READY cards, USAGE.md.
```

---

## R3. LIVE-PATH red team (rank 3)

```
MTS Fable session R3, adversarial review. Boot per CLAUDE.md steps 1-2. Usage guard as in R1. Testnet only (Deribit test); do not touch the live tree, HALT files or processes; do not read .secrets/ or .env. Read-only: you may write tests in a temp copy and report, not change production code.

QUESTION: If a layer went live tomorrow on testnet, what would lose money, double-trade, or fail open? Find the failures a Sonnet builder missed.

READ: the live path (execution/, runtime/, live_runner and its tests), research/layer_lab/reports/*t09* (backtest vs live parity: 5 families not matching), t06 (cost/fill realism), MOVED_RULES.md (live-path rules: restart/reset state, non-trade balance moves, API errors, fail closed), system/DEPLOY_RUNBOOK.md.
Method: for each rule in MOVED_RULES.md find the code that enforces it and the test that proves it; try to break it (restart mid-position, deposit/withdrawal moves, API 5xx/timeouts, duplicate fills, clock skew, partial fills, stop gap). Prefer writing a failing test over arguing.

DELIVERABLE research/fable_runs_2026-10-28/R3_LIVE_REDTEAM.md:
1. Findings table: id, severity (BLOCKS-LIVE / FIX-SOON / NOTE), file:line, scenario (inputs -> wrong behaviour), failing test name or why none, proposed fix in one line.
2. Rule coverage matrix: each MOVED_RULES rule vs code vs test (COVERED / PARTIAL / NONE).
3. One go/no-go line for testnet live, with the BLOCKS-LIVE list that must be empty first.
4. One card per BLOCKS-LIVE finding (lane SONNET, test fails on old code).
Ship; Result: count by severity. Reply in 6 lines.

EXPECTED OUTPUT: the md; findings table; coverage matrix; cards; USAGE.md.
```

---

## R4. OVERHEAD CUT list (rank 4)

```
MTS Fable session R4. Boot per CLAUDE.md steps 1-2. Usage guard as in R1. Operator style: lean; propose REMOVALS, never new gates or schedulers.

QUESTION: Last 72 h on trunk: 1,085 commits, 67 % non-research, 33 % overhead (merge/claim/release), 45+ stale claims, 3 CI reds that took 10-240 min to fix, ~20 % of a weekly quota lost to an unnoticed reset. What can we stop doing, and what single mechanism prevents the lost quota?

READ: scripts/dev/health_audit.py output, research/mts_doctor/REPORT_2026-10-27.md, system/EXHAUST_PHASE.md, research/lead/2026-10-27_successor-wake-design.md, card weekly-reset-radar-48h-exhaust, system/TRAFFIC_BUSTERS.md, git log of the last 72 h (bucket with a script; do not read commits one by one).

DELIVERABLE research/fable_runs_2026-10-28/R4_OVERHEAD_CUTS.md:
1. Time/commit budget table by activity (research, build, claims, merges, CI repair, docs, roles), from a script you ship alongside.
2. Top 10 removals ranked by (commits or quota saved) / risk, each: what to stop, how it was added (commit), evidence it does not carry weight, rollback.
3. Whether the reset-radar + successor-wake design closes the lost-quota gap; list what it misses (hung sessions, app closed, login switch) and the smallest addition.
4. Which doctor warnings are noise (state the test), which are real.
No new gates, no schedulers. Ship; Result: top-3 removals with saved-commit estimate. Reply in 6 lines.

EXPECTED OUTPUT: the md, the bucketing script, ranked removal table, USAGE.md.
```

---

## R5. LIVE-VALIDATION protocol review (rank 5)

```
MTS Fable session R5. Boot per CLAUDE.md steps 1-2. Usage guard as in R1. No live-path changes.

QUESTION: The operator replaced G3 blind marking with live validation: one confirm/correct per unique signal category, look-alikes inherit "matches validated case #n", differences go to a DOUBTS list. Is that sound, and what must the category key and inherit rule be so the validation means something?

READ: card live-validation-store-signal-chart-hook, d-live-validation in OPERATOR_DECISIONS.md, research/malkan_extract_2026-10-15/ (Malkan's own definitions of regular/hidden divergence, quotes), research/malkan_div_flags_2026-10-28/ if on trunk (else say so), READER_PROTOCOL.md and the g3_marks files (what blind marking was meant to protect against).

DELIVERABLE research/fable_runs_2026-10-28/R5_VALIDATION_PROTOCOL.md:
1. What blind marking protected against (bias, leakage) and which of those the new flow still covers or loses.
2. The category key and inherit rule, written so a machine can apply it: fields, tolerances (OURS, with reason), what counts as "differs" (route to DOUBTS), how a correction changes earlier inherited cases.
3. Sample-size honesty: how many validated cases per category before the layer's accuracy can be claimed, and why one confirm is a reading check, not an edge test (validation of the detector is not validation of profit; profit still needs the fee-net out-of-sample pass).
4. Edge cases: signal on a forming bar, repainting, two signals one bar, timeframe boundary, operator unavailable (default = pending, never auto-confirm).
5. Edits to the card (list as a diff in the md); do not edit the card yourself.
Ship; Result: the key + inherit rule. Reply in 6 lines.

EXPECTED OUTPUT: the md with key/inherit rule, edge-case table, card edit list, USAGE.md.
```
