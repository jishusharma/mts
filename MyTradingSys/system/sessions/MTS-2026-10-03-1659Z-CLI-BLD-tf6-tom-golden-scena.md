# MTS-2026-10-03-1659Z-CLI-BLD-tf6-tom-golden-scena
surface: App (Claude Win App, Code mode; python, git and the gate ran from the App, no CLI fallback needed) | model: claude-sonnet-5-5 | role: BLD | branch: fast-track
started: 2026-10-03 16:59Z | status: closed | commits: the commit history --grep "MTS-Session: MTS-2026-10-03-1659Z-CLI-BLD-tf6-tom-golden-scena"
handoff: none. Test-only; no execution/ file touched, no process stopped, no HALT/plan/order touched. The 6 gaps below go to the supervisor / CC_TASK_LIST.

## T0 PASS
- Row: runtime/BUILD_PIPELINE.md:47 (1.8 TF6, QUEUED, blocker 1.6 = TF4 LANDED at :45). Spec: research/_archive/loose_2026-10/TOM_FABIO_REVIEW_2026-10-03.md:89 (failing scenarios listed, not fixed).
- Code under test: execution/auto_trader.py parse_tom_alert :121-139, runner_split :142-161, tom_signal :174-220 (limit entry :210-212, time exit :215-219, breakeven flag :213-214). Live config execution/auto_trader_config.json:9-18 (tom.size_usd 10).
- Sources: extracts/v2/tom/4MoNjEQ2Dd8_v2.md decision rows (line 23+N); research/fast_track_2026-09-27/ANGLE_TRADE_CATALOG.md rows 3, 13, 37 and Q-quotes of EXEC_PROVENANCE_AUDIT.md.
- MyTradingSys/tests/test_tom_golden.py did not exist before this session (the prompt's READ FIRST lists it).

## T1 PASS
New MyTradingSys/tests/test_tom_golden.py (14 scenarios; hand-derived numbers in comments, none read from code). Target = live auto_trader.py; MTS_TOM_GOLDEN_TARGET = path of a staged copy (its sibling config, + ".new").
Known gaps skip with the failure text (@known_gap); MTS_TOM_GOLDEN_STRICT=1 makes them fail.

## T2 PASS - results (2026-10-03, JIS desktop)
| id | scenario (source) | live | auto_trader.py.new |
|---|---|---|---|
| g01-g08 | 4Mo long stop/target; 12-tick stop kept; AVIS 630/730/230; limit at zone; poor RRR 0.8 refused; wrong-side stop refused; re-entry; no TARGET no plan | PASS | PASS |
| g09 | 4Mo row 2 entry before proof: verdict WAIT_PROOF refused (E10-1, by design) | GAP | GAP |
| g10 | 4Mo rows 22, 47 partial + runner at configured size: size 10 -> single target (E3) | GAP | PASS (size 20) |
| g11 | 4Mo row 23, Q13/Q14 stop stays structural after leg 1: plan carries --breakeven-after-first-target (E7) | GAP | GAP |
| g12 | time exit independent of zone name: 5m zone 40 min, 4h zone 1920 min (E2) | GAP | PASS |
| g13 | Q22 size follows the stop: size 10 at 0.2 % and at 2.0 % (E3) | GAP | GAP |
| g14 | Q05/Q07 resting limit on the venue price scale: no apply_venue_price (E1a) | GAP | PASS |
Live: 8 passed, 6 known gaps (strict run: 6 failed). Staged: 11 passed, 3 gaps (strict).
Fail-before (7 mutants of a copy of tom_signal, each caught): limit->market g04; ordering check off g06; sides swapped g01-g04, g07, g10-g13; stop floor 0.2 g02; net_rr floor off g05; alert no not kept g07; TARGET optional g08.
Not translatable by a card (no test): 4Mo rows 15, 20-21, 27, 30-31, 35, 45, 48-49 (module docstring).

## T3 PASS
python scripts/dev/run_all_tests.py --quick: ALL TESTS PASSED (step 4 pytest covers MyTradingSys/tests; Maven + backtest skipped by --quick). Build-Check not run: no code, config or script changed.

## T4 PASS
BUILD_PIPELINE.md row 1.8 LANDED with receipt; 03_FILE_INDEX rows (test + this record). Commit "TF6: ..." stages the 3 paths I wrote that are still uncommitted (pipeline row, file index, this record). test_tom_golden.py is already in HEAD: another session's commit 91c2d0a ("rule: read the blocker cell ...") swept it in while I was working; HEAD content equals the file on disk (the change listing HEAD empty).

## T5 MISSED (deviations)
- "Failing scenarios" are known-gap skips, not red tests: the new file sits in gated step 4, so a red test would block every commit. STRICT env gives the red list.
- g09 expectation (an order on WAIT_PROOF) follows 4Mo row 2 literally; EXEC_PROVENANCE_AUDIT H4 point 1 keeps the proof-first chain. It is listed as a gap, as H4 point 4 asks.
- g11, g13 expectations come from Q13/Q14/Q22 reading, not an explicit Tom rule; verdict NO-SOURCE on the code side stays.
- Fixtures are normalised units (no Tom BTC trade has a date); translation fidelity only, no edge claim.
- Engine layer (Java SetupCandidatesBuilder zone/stop/target pick) not tested; only the card -> plan step is.
- Working tree had unrelated edits (DSA_SESSION_PROMPT.md, LESSONS_LEARNED.md, orderflow_live files): not mine, not staged.
- No Maven, no backtest step (--quick). One-claim spot check: the gate output "Step 4: Pytest tests: PASS" read from the log, not the worker summary.
- Stage discipline: my test file reached history inside an unrelated commit (91c2d0a) that I did not make; not rewritten (no rebase/reset).
