# Opus run design, 2026-10-28 (Lead, Opus, login C): top 3

Operator ask 2026-10-28: "design the next best Opus runs", "include self-healing mechanisms for AI health / mechanisms / hooks".
Opus is used where the work is judgement plus careful code that a Sonnet worker gets wrong (hooks, gates, statistics review); recount and plain build stay on Sonnet (CLAUDE.md "Cost and routing").
Start text for all three: `system/handover/OPUS_RUNS.md`; the operator types `Run OPUS_RUNS.md O1` (or O2, O3) in a new Code session on Opus.

## State the ranking is built on (checked on disk 2026-10-28)
- Edge path: R1 says only a 4h+ powered rule is left; R6 (Fable, card `fable-run6-powered-prereg`) started on jis-nb today, no output on trunk yet. `prereg_gate.py --m auto` ledger fix is still an open card (`fable-run2-regate-fixes-1to8`, refined), so R6's m may be computed by the unfixed gate.
- AI health: `mts_doctor.py` only reports ("Reports only; nothing was edited", REPORT_2026-10-27.md Part 1); it has no apply mode. The 2026-10-27 report shows 6 WARNs that recur: 58 stale claims (limit 5), CI red 18-27 min to green (limit 10), main checkout 243 behind (today 1706, diverged, so `git pull --ff-only` fails and broadcast b-4c2dfe can never be acked here), 8+ broadcasts nobody can ack, 5 cards waiting on the operator, dead refs. Hooks: 18 registered (SessionStart 6, UserPromptSubmit 5, PostToolUse 3, PreToolUse 2, Stop 2); they load from the main checkout, which is stale (memory hooks-come-from-main-checkout). Queue: many READY cards carry `[STALE:scope changed]` flags.
- Overhead: STATUS gate board, commits 24 h = 217, research 24 %, "other 72 % OVER 30 % CAP"; no gate moved in 24 h.
- Live path: R3 F-GAP-1 (BLOCKS-LIVE) already has a Sonnet card with a failing test (`fable-r3-stop-gap-early-return`); not an Opus job.

## Ranking

| Rank | Run | What it settles for the operator | Cost (OURS) | Verdict |
|---|---|---|---|---|
| O2 | **Independent review of R6 pre-reg** | The one clean VALIDATION read is spent only on a test whose m, power and sealed-cut rules are right | ~25 turns, 30-45 min | **RUN first, the moment R6 ships, before any E2 run** (R6 read below: power margin hangs on m) |
| O1 | **Self-healing loop for AI health and hooks** | Health problems fix themselves within the safe class instead of piling up as WARN lines nobody acts on | ~40 turns, 60-90 min | **RUN now, in parallel with O2** (operator asked; every other run pays this tax; touches no research files) |
| O3 | **Overhead cut: 72 % non-research commits** | Quota goes to research; a ranked stop-doing list with the number each cut saves | ~25 turns, 30-45 min | **RUN after O1** (O1 removes part of the churn; measure after) |
| - | R5 live-validation protocol review | Detector checks; R1: not profit validation | ~25 turns | later |
| - | fable-run5 grandfather decision | Fable lane, operator-run | - | not Opus |
| - | F-T09-2 live bracket backtest | Sonnet card, formula is fixed | - | not Opus |

## O1 Self-healing loop (AI health, mechanisms, hooks)
**Goal:** every recurring doctor/hook finding gets one of three classes, and the SAFE class heals itself with a test: HEAL (machine fixes it, idempotent, reversible, never touches live tree, runtime data, others' uncommitted files or git history), CARD (files or refreshes one card, no duplicate), OPERATOR (only money, mainnet, going private, deleting data, live tree).
**Inputs:** `scripts/dev/mts_doctor.py`, `research/mts_doctor/REPORT_2026-10-27.md`, `.claude/settings.json` hooks and their scripts (`trunk_lag.py`, `ci_watch.py`, `c_drive_guard.py`, `mts_signal.py`, `role_loader.py`, `stop_guard.py`, `preship.py`, `usage_reminder.py`, `bg_watch.py`, `health_audit.py`, `lane_health.py`), `system/MTS_DOCTOR.md`, `TRAFFIC_BUSTERS.md`, `SCHEDULING_POLICY.md` (no schedulers: heals run from hooks or `sync.py`, never a timer), cards `broadcast-hygiene-stale-and-b4c2dfe`, `bug-long-background-processes-dead-ends`, `coordinator-sits-idle-during-long-backgr`, `bug-session-handoff-ship-speed-audit`.
**Output:** `research/self_heal_2026-10-28/HEAL_MAP.md` (one row per check: symptom, class, heal action, trigger hook, test) and code: `mts_doctor.py --heal` running only HEAL rows, each with a test that fails on today's code. Build the top 3 HEAL rows in this run (OURS default: stale claims whose branch is shipped get released; broadcasts to hosts that cannot ack expire with a reason; main checkout diverged/behind reports one exact recovery command and the hook source in use). Cheap hook fixes in the same run; anything bigger becomes a SONNET card.
**Stop:** 5 h window 85 %, weekly login cap (C 85 %), 40 tool turns (card cap), context 60 %, or any heal needing git history change, process kill, or the live tree: make it CARD/OPERATOR and stop that row.
**Waste if:** it adds a new gate or doc page instead of removing a WARN (operator style: lean, no paperwork gates); a heal that is not idempotent; a timer/scheduler.
**Done when:** HEAL_MAP.md on trunk; `mts_doctor.py --heal` exists; 3 tests that failed before now pass; next doctor run shows STALE-CLAIMS and BROADCAST counts lower than 2026-10-27 (58 and 8); commit body `Result:` = WARN count before -> after.

## O2 Independent review of the R6 pre-reg (blocked on R6)
**Goal:** a Lab_Guy-grade independent re-derivation of R6's counts, m, n_needed and pass rule before any Sonnet session runs E2, so the single VALIDATION read is not wasted.
**Inputs:** `research/fable_run6_powered_prereg/{PRE_REG.md,COUNTS.csv,counts_only.py}` (from R6), R1 sections 2-4, `backtest/PRE_REG_TEMPLATE.md`, `research/pit_levels_2026-10-16/PRE_REG_V2.md:36`, `backtest/power_mde.py`, FORMULAS.md fees, `fable_audit_2026-10-18/REGATE_AUDIT.md:73-83`.
**Two must-answer checks from the live read of R6 (`R6_LIVE_READ.md`):** (1) m: R6 used m = 56 + 9 = 65 (z 3.364, n_needed 439); R1's bill for DEV-mined results is m = 281 (z 3.748, n_needed 523, `research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md:29`), and the cell count is 3,018 (n_needed about 660 > 539 available). Also weigh R1's own rule for a fresh pre-registered test (m <= 42, z 3.241, `research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md:31`). Decide which m a pre-registered sibling of an already-read Krown S5 row must pay, with the source. (2) Power counted on signal days (539), pass rule counts entry days after the one-position-per-symbol busy rule with a 100-bar time stop; the busy rule removes days, so a gate PASS on signals may be INCONCLUSIVE on entries. Bound the entry-day count without outcomes (worst case: every trade runs its 100-bar time stop) and say whether the pre-reg must re-gate on that bound.
**Output:** `research/fable_run6_powered_prereg/REVIEW_O2.md`: ACCEPT or REJECT with must-fix list; one recount of event totals with an own script (independent, not R6's); check that m came from the ledger-aware gate (REGATE fix 1) and that every bar >= 2024-07-01 is refused. On ACCEPT, the `REVIEWED:` line on the E2 card.
**Stop:** any outcome column or sealed bar would be read: stop. 35 turns.
**Waste if:** it re-argues R1, or reruns R6's own script as its check.
**Done when:** REVIEW_O2.md on trunk; recount matches COUNTS.csv rows or each mismatch named; verdict line; E2 card stamped or set back to refined.

## O3 Overhead cut
**Goal:** a ranked stop-doing list that brings non-research commits under the 30 % cap, each row with commits/day saved measured from git log, and the 3 cheapest cuts applied in the run.
**Inputs:** `git log --since=7.days origin/fast-track` grouped by path/prefix (count, then parse), STATUS gate board, `TRAFFIC_BUSTERS.md`, `PARALLEL.md`, R4 brief in `lead/2026-10-28_fable-runs-top5.md`, dedupe audit `research/*dedupe*`, O1 HEAL_MAP.md.
**Output:** `research/overhead_cut_2026-10-28/CUTS.md` (cut, commits/day now, saved, risk, applied yes/no) + the 3 applied cuts with tests where code changes.
**Stop:** 35 turns; never removes a safety gate or a live-path check.
**Waste if:** it proposes cuts without a measured count, or cuts research commits.
**Done when:** CUTS.md on trunk; research share recomputed with the same script before and after; `Result:` = non-research share now and projected.

DECISION (OURS): O1 builds its top 3 heals itself instead of handing all to Sonnet, because hook code that misfires blocks every session and the operator asked for working mechanisms, not another report.
DECISION (OURS): O2 is filed blocked on R6 output, not started now; reviewing before R6 ships has nothing to review.
DECISION (OURS): O3 runs after O1, so its before/after count is not mixed with O1's changes.
