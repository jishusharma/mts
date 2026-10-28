# Opus runs O1-O3 (start text)

Operator start line, typed into a new Code session on Opus 5.5, effort high (one run per session):

    Run OPUS_RUNS.md O2

(or O1, O3). Design and ranking: `MyTradingSys/research/opus_run_design_2026-10-28/DESIGN.md`. Order: O2 the moment R6 is on trunk (before any E2 run); O1 now, in parallel; O3 after O1 ships.

Common to every run: boot per CLAUDE.md steps 1-2 (`python scripts/dev/sync.py start <card id>`, STATUS.md). `get_usage` first and last, one line each in the commit body. Stop and ship at 5 h window 85 %, login weekly cap (C 85 %), the run's turn cap, or context 60 %. Testnet only, no live tree, no deploy, no process kill, never read `.secrets/` or `.env`, no schedulers. No questions to the operator: conservative default, log `DECISION (OURS)`. Ship with `python scripts/dev/sync.py ship --release <card id>`, commit body `Result: ...`, then `sync.py where` clean and `tasks.py done <card id>`. Reply: bold result line, max 6 lines.

## O1 Self-healing loop (card `opus-o1-self-heal-loop`, 40 turns)
QUESTION: which recurring doctor and hook findings can fix themselves safely, and fix the top 3 now.
DO: read DESIGN.md section O1 and its inputs. Write `research/self_heal_2026-10-28/HEAL_MAP.md`: one row per `mts_doctor.py` check and per hook in `.claude/settings.json` (symptom, last count from `research/mts_doctor/REPORT_2026-10-27.md`, class HEAL / CARD / OPERATOR, action, trigger, test). HEAL only when idempotent, reversible, and it touches no git history, live tree, runtime data or others' uncommitted files. Add `mts_doctor.py --heal` that runs HEAL rows only; build 3 heals (default: release stale claims whose branch `git cherry` shows shipped; expire broadcasts no host can ack, with the reason; main checkout behind/diverged prints one exact recovery command and which hook copy is in use), each with a test that fails on today's code. Bigger fixes: one SONNET card each (twins first). Result: WARN count before -> after.

## O2 Independent review of R6 (card `opus-o2-r6-review`, 35 turns; blocked until R6 is on trunk)
QUESTION: is R6's frozen Krown S8 4h pre-reg right enough to spend the one VALIDATION read on?
If `research/fable_run6_powered_prereg/PRE_REG.md` and `COUNTS.csv` are not on origin/fast-track, stop and reply "R6 not shipped". DO: read `research/opus_run_design_2026-10-28/R6_LIVE_READ.md` and DESIGN.md section O2. Recount events and UTC days with your own script `research/fable_run6_powered_prereg/recount_o2.py` (+ `test_recount_o2.py`: its sealed-cut assert fails on a planted 2024-07-01 bar) from the same cached klines `F:/MTS/data/fable_run6_klines/` on JIS-NB (the desktop; the cache holds months >= 2024-07: drop every bar >= 2024-07-01 at load, before any computation), not R6's `counts_only.py`; no outcome column, no bar >= 2024-07-01. Settle the two must-answer checks: (1) which m the test must pay (42 for a fresh pre-reg per R1 `research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md:31`, 65 as R6 used, 281 per `research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md:29`, 3,018 cells; with sources) and re-run `prereg_gate.py` with it; (2) an outcome-free bound on entry days after the busy rule and 100-bar time stop, and whether the gate must use it. Write `research/fable_run6_powered_prereg/REVIEW_O2.md`: ACCEPT or REJECT + must-fixes. ACCEPT: put `REVIEWED: Opus_O2 <YYYY-MM-DD> ACCEPT` (date as second token, `tasks.py` stamp grammar) on its own line in the note of `krown-s8-4h-e2-dev-run`. REJECT: set that card back to refined with the must-fix list. Result: verdict + m used + n available/needed.

## O3 Overhead cut (card `opus-o3-overhead-cut`, 35 turns; after O1 ships)
QUESTION: what stops so non-research commits fall under the 30 % cap (72 % on STATUS today)?
DO: read DESIGN.md section O3. Count 7 days of `origin/fast-track` commits by kind with a script (parse, then count; never from truncated output). Write `research/overhead_cut_2026-10-28/CUTS.md` (cut, commits/day now, saved, risk, applied). Apply the 3 cheapest cuts; never remove a safety gate or live-path check. Result: research share before -> after (projected).
