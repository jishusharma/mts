# MTS-2026-10-03-1620Z-CLI-BLD-tf5-tom-exec
surface: App (Claude Win App, Code mode; no CLI fallback needed: python, PowerShell Build-Check and git all ran from the App) | host: JIS-NB | account: none | model: claude-opus-5-5 | role: BLD | branch: fast-track | branch_alias: none
predecessor: MTS-2026-10-03-1444Z-CLI-BLD-tf4-execution-proven | lanes: none (no subagents, no workers)
started: 2026-10-03 16:20Z (ID time; first clock read 16:46Z) | ended: 2026-10-03 16:55Z | status: closed | commits: the commit history --grep "MTS-Session: MTS-2026-10-03-1620Z-CLI-BLD-tf5-tom-exec"
handoff: supervisor via SUPERVISOR_LOG.md (CLAIM line of this session) and CC_TASK_LIST_2026-10-03.md row 1.1: promote the 3 TF5 .new files, re-gate, restart auto_trader. Claim on execution/ held until that promote.

## Scope
Task A: TF5 (BUILD_PIPELINE row 1.7) = EXEC_PROVENANCE_AUDIT.md H5 items 1-3, staged as .new in MyTradingSys/execution/ only.
Task B: research/_archive/loose_2026-10/CC_TASK_LIST_2026-10-03.md (read-only). Task C: research/CL_PROMPT_TEMPLATE_REVIEW_2026-10-03.md (read-only).
No live file edited in place, no process stopped or restarted, no HALT/AUTO_PAUSE/plan/order touched, no promote.

## T0 PASS
- Read: STATUS.md, SURFACE_POLICY.md, EXEC_PROVENANCE_AUDIT.md (all 304 lines), OPERATOR_RULINGS_2026-10-02.md (Ruling 3 still pending, :40), auto_trader.py (all), auto_trader_config.json, executor.py :120-128, :400-460, :530-564, deribit_orders.py :438-439, plan_compiler.py :40-105, :255-280, start-trading-day.ps1 :165, :284-325, position_manager.py :399, test_auto_trader.py, test_r2_runner_exit.py, run_staged_tests.py, run_all_tests.py step 1, BUILD_PIPELINE.md, BUGS.md.
- Live values before TF5: CFG:10 tom.size_usd 10; AT:57 max_hold_minutes None, max_hold_bars 8 (zone-TF scaled, AT:134-136, :217-219); AT:336 executor run without --max-entry-seconds (EX:125 = 600); card PRICE (PS1:292 = snap.current_price, PS1:165) not parsed (AT:108).

## T1 PASS - staged files (sha256 prefix)
| file | live (unchanged) | staged .new | backup |
|---|---|---|---|
| execution/auto_trader.py | ed639a3c0eb3 | e4e0d788dfcf (673 lines) | auto_trader.py.pre_tf5 |
| execution/auto_trader_config.json | 26a6be4b60ea | 31026cd6cf35 | auto_trader_config.json.pre_tf5 |
| execution/test_auto_trader.py | 753413a9e033 | 331c097083a4 (761 lines) | test_auto_trader.py.pre_tf5 |
- E1a: CARD_FIELD reads PRICE; apply_venue_price() sets --price = card ENTRY + (Deribit mark - card PRICE), mark via deribit_mark() = DO.get_ticker (public, no auth); called in cycle() only after HALT/AUTO_PAUSE/busy checks, right before place(). No card PRICE, ticker exception, NaN/inf/<=0/non-number mark -> signal_rejected, nothing placed. Stop/target stay % of the card levels. trade_attempt logs card_entry, card_price, deribit_mark, basis, venue_entry.
- E1b: tom.max_entry_seconds (default 600 = EX:125, unchanged) -> sig executor_args -> appended to the executor --go call only; a non-positive or non-int value rejects the signal.
- E3: CFG tom.size_usd 10 -> 20 (Ruling 2). runner_split floors each leg to 10 USD like PC round_size and refuses when either leg < 10 or the legs do not sum to the size (size 30 at 50/50 -> "legs 10+10 do not sum to size 30").
- E2: tom.max_hold_minutes 120 in DEFAULT_CONFIG and CFG; zone_tf parse and the bar x zone-TF rule removed from the Tom path; None = no time exit. Layer path (AT.new:332-333) unchanged (audit E2-F KEEP).
- Values: 600 s and 120 min are the values the live path already used (EX:125; the old 15m fallback). NO-SOURCE, flagged MEASURE (Ruling 3 pending).

## T2 PASS
- Staged suite (run_staged_tests.py, .new over live): test_auto_trader + test_r2_runner_exit + test_fabio_slot 126/126 OK.
- Pre-change run (test_auto_trader.py.new against the live auto_trader.py): 91 tests, 6 failures + 49 errors. Every TF5 behaviour test fails or errors; CycleTest/RecoverTest error in setUp on the missing deribit_mark (pre-change has no mark read).
- Live-path coverage: API errors (OSError, KeyError, ValueError, RuntimeError, NaN, 0, negative, None, junk, inf -> refused, price untouched); fail closed and no late retry (the refused alert is consumed); restart (main() with the staged config: size 20, 50/50 split, 120 min, --max-entry-seconds 600; second restart does not replay); reset (state file missing -> current alert marked seen, no trade); non-trade balance move (mark read never authenticates or reads the account); HALT and busy slot read no mark.

## T3 PASS
- python scripts/dev/run_all_tests.py --quick: ALL TESTS PASSED (step 1 runs execution tests through run_staged_tests.py, so the .new code was gated).
- scripts\Build-Check.ps1: STATUS: PASS.
- verify_extract_quotes.py on both reports: PASS, 0 problems (they carry no trader quotes). No promote.

## T4 PASS
- BUILD_PIPELINE row 1.7 LANDED with receipt; 03_FILE_INDEX rows for the 2 reports and this record; SUPERVISOR_LOG claim; commit on fast-track, prefix "TF5: ".

## T5 MISSED (deviations)
1. Row 1.7 marked LANDED as the prompt asks while the code is staged, not promoted; GATED would match the pipeline's status words. Promote = CC_TASK_LIST row 1.1 (supervisor).
2. E1a basis = mark at placement minus card PRICE at the card TIME (up to 300 s apart): price drift since the alert moves the limit with the basis. Implemented as specified; the one-instant fix is CC_TASK_LIST row 3.1.
3. The mark is read in cycle() just before place(), not inside place(): keeps tom_signal() offline-testable and skips the read on HALT/busy. Same cycle, same second as the order.
4. No cap on the basis size: any cap would be a NO-SOURCE number; only non-finite or non-positive marks are refused.
5. max_entry_seconds and max_hold_minutes kept at 600 / 120 (live-path values) because Ruling 3 is pending; MEASURE plan is CC_TASK_LIST row 4.2.
6. DEFAULT_CONFIG tom.size_usd stays 200 (only CFG:10 changes, per H5 item 2); found that a missing config file silently runs on these defaults (CC_TASK_LIST row 2.1).
7. TF5 tests were added to test_auto_trader.py.new (the gate's existing module) instead of a new test file, so scripts/dev/run_all_tests.py needed no edit.
8. Four new tests also pass on pre-change code (regression guards): size 20 split, size 10 too small, layer signals not venue-priced, staged config values (the last one fails on the live config: size 10). The reset-state test fails pre-change only through setUp.
9. Build-Check rewrote MyTradingSys/runtime/BUILD_REPORT.md and session_log.json (B091); not staged in this commit.
10. Session record written at close, not at boot; the SUPERVISOR_LOG claim was written before the first staged edit.
11. Task C token figures are chars/4 estimates (no tokenizer installed).
12. The row-1.7 Next cell cited Ruling 1 for size 20; the receipt names Ruling 2 (as the audit and this prompt say).
13. The second Build-Check (after the T4 doc edits) FAILED once: this record named a git command (doc rule test_integrity test_2); reworded, third run STATUS: PASS.
