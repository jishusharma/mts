# MTS-2026-10-02-2055Z-CLI-SUP-r2-promote
surface: CLI
host: JIS-NB
account: A
model: claude-sonnet-5-5
role: SUP
branch: fast-track
branch_alias: none
predecessor: MTS-2026-10-02-1710Z-CLI-SUP-prompt-shape
lanes: none (no subagents)
started: 2026-10-02 20:55Z
ended: 2026-10-02 21:30Z
status: closed
handoff: operator rebuilds Java and restarts the loop wrapper / auto_trader (not done here)

## T0 Operator ruling (verbatim, 2026-10-03 IST)
"Let Claude judge this based on the realistic trades that we must place based on historical testing. This logic applies to all similar stuff! Use defaults when you have to - All permissions granted! Do not be afraid to experiment in order to fine tune trades to maximize profitability and reliability."

Also from the operator (2026-10-03 01:58 IST): "yes go ahead, fix runner and promote R2".

## Scope
T1 runner min-distance in the target pick (Java + Python mirror + config), T2 tests, T3 promote the staged R2 files in
the order of the R2 record (MTS-2026-10-03-CLI-BLD-r2-runner-exit.md, promotion checklist). No stop/kill of Java,
auto_trader or the loop wrapper.

## T1 Runner min-distance: value and reasoning
Rule: runner = the next node whose distance from the TARGET is at least `runner_min_distance_pct` (percent of the
target price); none qualifies -> runner_target = 0 (single-target plan, the old behaviour).
Config: `MyTradingSys/system/runner_min_distance.json`, key `runner_min_distance_pct`. Tag NO-SOURCE (no trader quote
sets it; operator Ruling T0 delegates the value to this session's judgement on realistic trades).

Evidence (historical snapshots `runtime_data/snapshots/BTCUSDT_2026-10-0*.json`, 873 files, 1057 candidates with a
target, 243 with a runner_target under the old "any strictly farther node" rule):
- Runner gap |runner - target| / target: 10th, 25th, 50th, 75th percentile are ALL 0.087 %; 90th is 1.89 %.
  86 % of runners sat 0.087 % beyond the target (about 0.45 R, 3.6 % of the target distance); the other 14 % were >= 0.5 %.
- Median target distance from the zone is 0.49 % of price. A 0.087 % runner leg adds almost nothing, yet leg 2 gives
  back the whole target profit if the breakeven stop (moved after leg 1) is hit first.
- Friction per round trip is 12 bps (taker 10 bps + slip 2 bps, FORMULAS.md section on fees).
Decision: 0.25 (%). It is about 2x the 12 bps round-trip friction, so a runner leg that is reached pays for itself
after costs, and it is half the median target distance, so a runner is a real extension of the trade. On the data above
any value in 0.10 .. 0.50 gives the same split (the 0.087 % pairs are rejected, the >= 0.5 % runners kept), so 0.25 is
the middle of the flat region and not a tuned point. Re-fit after the first batch of live runner trades.

## Log
T1 PASS. Java (in place): RunnerMinDistance.java (reader, NaN on bad file), SetupCandidatesBuilder.pickTarget 6-arg (5-arg
overload keeps min 0). Python (in place, critical): runtime/runner_min_distance.py + math_object_builder.pick_target(.., runner_min_pct=0.0).
Four-step proof on math_object_builder.py: before 985fb4818c66a8df, after d1876da614182319 (sha256 prefixes); diff = the import,
the load + fail-closed NaN, the 6th parameter, one condition in the runner loop (nothing else). Config: system/runner_min_distance.json 0.25.
T2 PASS. test_r2_runner_exit.py 18 -> 29 tests (+11: 7 pick cases incl. skip-to-next, skip-to-none, short side, NaN, target unchanged;
4 file/loader cases). Pre-change code (old builder, no reader): 11 of 11 new tests fail/error (9 behavioural: TypeError on the 6th
argument / wrong runner; 2 loader tests fail because the module did not exist). Staged run of r2_runner_exit + r2_breakeven_move +
auto_trader + plan_compiler: 146 pass. Java RunnerMinDistanceTest 8 pass (+ HvnTarget 10 pass). run_all_tests --quick: ALL TESTS PASSED.
T3 PASS. Promoted by rename with `.pre_r2` backups (untracked, gitignored); sha256 prefix live_before == backup, after == staged for all 8:
 (a) trade_plan_validator.py e8cae05e->3866a4df, new_plan.py 383efb58->706fa76c, position_manager.py 60262aaa->7447fa0e. 59f7785 082a733 7e1b4b1
     No position_manager process was running (no trade open). run_all_tests --quick PASS, Build-Check PASS.
 (b) auto_trader.py 0caef3f2->ed639a3c, trade_plan_schema.json 5e2f31cb->5413d2aa, test_auto_trader.py e5cf48d7->753413a9,
     test_plan_compiler.py 84cfefbc->524e8f7e. 35f8a8c d225c80 fba6fcd e8214e4. Gate PASS, Build-Check PASS.
 (c) scripts/core/start-trading-day.ps1 four-step proof: before 67a42a7e3e43249a66ac788094f8fbde9e16b8e66cb5555c24c095dcf09b4e45,
     rename .new -> live, after 1679e96eb50dc509bd1e45b2ada6a185b51cce60caf4e614bab790a3e21dd5eb (= staged), diff = exactly the 4 added
     lines (RUNNER_TARGET emit, only when math.runner_target > 0). PowerShell parser: 0 errors. Gate PASS, Build-Check PASS.
Build-Check also compiled Java (mvn compile) three times and `mvn test` ran 3 test classes: target/classes now holds the min-distance build.
Not done (operator side, by instruction): Java rebuild/restart of the apparatus, auto_trader restart (running pids still hold the old
auto_trader.py in memory, so no RUNNER_TARGET parsing / two-leg plans until it restarts), loop wrapper restart. Until both restart the
old behaviour stands. Restart order from the R2 record: new_plan/validator/manager already live; restart auto_trader, then the wrapper.
