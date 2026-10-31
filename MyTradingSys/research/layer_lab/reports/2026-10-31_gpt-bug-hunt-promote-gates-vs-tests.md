# GPT promotion gate bug hunt

**FIX-FIRST — 1 LOW defect found; details and reproducing input are in [promote_gates_bug_hunt.md](../test_hunt_2026-10-31/promote_gates_bug_hunt.md).**

Checked `MyTradingSys/backtest/layers/promotion/promote.py:53-300`, its gate tests `MyTradingSys/backtest/layers/promotion/test_promote.py:90-229`, and `MyTradingSys/system/PROMOTION_PIPELINE.md`. Arithmetic was inspected with a read-only Python command. No data or backtest verdict was used. The existing unittest module was not run because its fixture launches Git subprocesses, prohibited by the task instruction.

Finding: `promote.py:293-296` accepts any nonempty `validation_reads[].at`, including `"not-a-date"` and `"2026-99-99"`, although the manifest contract at `promote.py:20` specifies an ISO date. The proposed regression at `MyTradingSys/research/layer_lab/test_hunt_2026-10-31/proposed_test_promote.py` expects REJECT and is expected to fail on current code; it was not run. PASS-ONLY probes cover one-variant Holm z and MDE integer cutoff arithmetic.

Observed boundaries: Holm z is 1.959964/2.393980/3.227218 for 1/3/40 variants; sample OOS `{net_r: .12, ci_low: .09, ci_high: .15, n_trades: 250}`, 3 variants gives an MDE floor of 170.1542. The existing tests reach Holm and MDE rejection but miss equality boundaries and the explicit 30-trade floor equality. An untested-branch inventory is in the findings file.

Task card: `python scripts/dev/tasks.py done gpt-bug-hunt-promote-gates-vs-tests --result "1 low finding; MyTradingSys/research/layer_lab/reports/2026-10-31_gpt-bug-hunt-promote-gates-vs-tests.md"` returned `done`.

Follow-up cards created: none.

Noticed: none.
