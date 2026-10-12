# RV02 [HIGH] DAX backtest harness fixes H1-H8 (lab-dax-* cards)

Rules and output format: `MyTradingSys/system/revalidation/_COMMON.md` (read it first).
Prompt id: RV02. Report: `MyTradingSys/research/revalidation/RV02_<UTC date>.md`.

Scope in: MyTradingSys/backtest/tom_dax_bt.py, dax_engine.py, dax_data.py, fees.py, test_tom_dax_bt.py, test_dax_data.py,
MyTradingSys/research/layer_lab/reports/2026-10-11_lab-audit-tom-dax-bt.md and the eight 2026-10-12_lab-dax-*.md reports,
MyTradingSys/research/tom_transfer_2026-10-11/PRE_REG_DAX.md.
Scope out: running `report --read-holdout` (the holdout is read once, by the pre-registered card), editing, any real-data backtest.
Why risky: the same model family found the 14 defects, fixed 8 of them, and wrote the regression tests. A holdout leak burns the
only out-of-sample set for Tom on DAX.
Checks:
1. For each H1..H8: open the original finding, the fix diff (the follow-renames commit history with patches on the files), and the new test. Does the test fail
   on the pre-fix commit (use `git worktree add` in the scratchpad, never the main tree)? MATCH/MISMATCH per H.
2. The 6 MED findings of the audit that had no fix card: list status (fixed by side effect / still open / not reproducible).
3. Holdout isolation, end to end: trace every path from raw bars to a metric printed by `all` and `report` without
   `--read-holdout`; list each place a bar with timestamp >= holdout start can influence a development number (indicator warm-up,
   trade exit beyond boundary, null/placebo draws, stress, fee gate, session calendar).
4. Fee gate: recompute the net RR from FDAX_PER_SIDE in fees.py for the primary arm by hand; compare to the report's 1.247752.
5. Run the two test files; report pass counts (expected 62 + dax_data tests) and anything skipped.
Already known (confirm or refute): test_tom_dax_bt.py 62 passed on 2026-10-12 on JIS-NUC.
