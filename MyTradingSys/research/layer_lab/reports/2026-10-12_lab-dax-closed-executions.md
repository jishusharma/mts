Changed `MyTradingSys/backtest/tom_dax_bt.py` and `MyTradingSys/backtest/test_tom_dax_bt.py`; H4 red: 8 failures, green: 39 tests OK.

# DAX H4: closed-market execution repair

Card: `lab-dax-closed-executions`. Date: 2026-10-12 UTC. Surface: COD. Result: DONE.

## What was checked

All paths are relative to `F:/MTS/mts-codex-lab`.

- Source finding: `MyTradingSys/research/layer_lab/reports/2026-10-11_lab-audit-tom-dax-bt.md:15-23` (file legend), `:59` (H4), `:109-118` (synthetic evidence).
- Referenced contract: `MyTradingSys/research/tom_transfer_2026-10-11/PRE_REG_DAX.md:9-16`, read only. Its original text remains intact.
- Old execution and scheduling: `MyTradingSys/backtest/tom_bt.py:175-249`, read only; mask contract at `:50-58`.
- Changed execution: `MyTradingSys/backtest/tom_dax_bt.py:210-277`; DAX null route at `:331`; DAX strategy/stress scheduling at `:568-591`.
- Coverage: existing daily-download contract at `MyTradingSys/backtest/tom_dax_bt.py:367-384`; new guard at `:387-398`, called before archive loading at `:607-622`.
- New synthetic tests: `MyTradingSys/backtest/test_tom_dax_bt.py:132-239`. Full test file executed.

Data range: synthetic three-minute fixtures with `real=[1,0,1]`, mirrored long/short; a 43-minute fixture for the unchanged 40-minute clock; temporary empty daily download artifacts dated 2026-01-01 through 2026-01-03. No real archive, snapshots, holdout, recall or BTC outcome run was performed. These unit checks are not empirical trials; TRIALS.md was not changed.

## Findings and resulting behavior

| Severity | File:line | Finding | Evidence and classification | Fix |
|---|---|---|---|---|
| HIGH | audit report:59; tom_bt.py:184-221 | Fill and holding loops ignored the real-bar mask. | MISMATCH before repair: the original simulator filled at index 1 and exited at index 1 with reason timeout. The eight long/short subcases failed before the fix. MATCH after repair: pending orders expire without filling on a filler, or fill at real index 2 if still eligible. | DAX-local simulator skips every filler for entry, ran-away checks and exits; elapsed clocks keep their original deadlines. |
| HIGH | tom_dax_bt.py:255-277; test_tom_dax_bt.py:159-177 | An expiry during closure must use an executable reopening price. | MATCH: entry 100, risk 1; reopening 100.4 produces +0.4R timeout at index 2, rather than +0.5R from its close. Reopening 97 produces -3R stop, mirrored for shorts. | At the first real open after expiry, execute a stop gap at open, a target gap at the resting limit, otherwise timeout at open. Later intrabar prices cannot alter this exit. A deadline on a real bar retains the existing close-price timeout. |
| HIGH | tom_dax_bt.py:331,568-591; test_tom_dax_bt.py:206-222 | Fixing only a standalone helper would leave strategy, stress or null runs exposed. | MATCH: synthetic strategy exits at index 42 for -3.5R including 0.5-point stop slippage; overlapping signals remain blocked through that exit. Synthetic null stops at index 42 for -3R. | Route DAX strategy/stress and DAX null executions through the local helper. Preserve one-position scheduling, geometry, fees and existing clocks. Shared engine files are unchanged. |
| MED | tom_dax_bt.py:387-398,617-622; test_tom_dax_bt.py:224-239 | A missing download is not evidence of a scheduled closure. | MATCH: missing 2026-01-02.bi5 raises SystemExit; completed empty daily files pass the existing download contract. An incomplete report request fails before the archive loader is called. | Require each daily raw artifact in the requested DAX interval before report simulation. Development-only requests cap this check at the last development date. |
| LOW | tom_dax_bt.py:217,277; test_tom_dax_bt.py:181-204 | Coverage may end before an expired position can reopen. | MATCH: no real reopening returns filled/open_at_end without inventing an exit. Deferred timeouts retain the same fee and adverse-slippage formulas. | Keep unresolved positions unresolved; do not use filler prices as substitutes. |

The coverage guard establishes the existing generator's daily download-artifact contract. It does not establish exchange-calendar parity, detect corruption inside a downloaded file, or prove that every intraday gap is scheduled. Those classifications are NOT_IN_DATA from the binary real mask alone (`tom_bt.py:56-58`). Every zero-mask minute remains non-executable regardless of its cause. This repair makes no claim that the broader harness is ready for a market outcome run.

## Red then green output

All test commands used `PYTHONPATH` equal to the work-tree root:

```powershell
$env:PYTHONPATH=(Get-Location).Path
python MyTradingSys/backtest/test_tom_dax_bt.py TestClosedExecutions -v
```

RESULT (2026-10-12, lab work tree), before the execution fix: the new test called a temporary local alias of the unchanged `T.sim_limit_trade`, so these failures exercised the actual old simulator:

```text
pending expires while closed: filled=True, fill_i=1 (expected no_fill)
pending survives closure: 1 != 2
timeout during closure: (0, 1, 'timeout') != (0, 2, 'timeout')
reopening gap through stop: (0, 1, 'timeout') != (0, 2, 'stop')
The same four failures occurred for long and short.
Ran 1 test in 0.004s
FAILED (failures=8)
```

The four additional execution test methods were also checked against the unchanged shared simulator by rebinding only the local helper in a separate Python process:

```powershell
python -B -c "import sys, unittest; sys.path.insert(0, 'MyTradingSys/backtest'); import test_tom_dax_bt as S; S.D.sim_limit_trade = S.T.sim_limit_trade; r = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(S.TestClosedExecutions)); sys.exit(not r.wasSuccessful())"
```

RESULT: `Ran 5 tests in 0.007s`, `FAILED (failures=15)`. This command preceded the sixth, download-coverage test. No shared source file was modified.

Coverage guard sensitivity check (separate process, guard replaced in memory by a no-op):

```powershell
python -B -c "import sys, unittest; sys.path.insert(0, 'MyTradingSys/backtest'); import test_tom_dax_bt as S; S.D.require_download_coverage = lambda *args: None; r = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromName('TestClosedExecutions.test_missing_download_is_rejected_before_archive_read', S)); sys.exit(not r.wasSuccessful())"
```

RESULT: `AssertionError: SystemExit not raised`, `Ran 1 test in 0.004s`, `FAILED (failures=1)`. This is a disabled-guard check, not a claim that the helper existed in the old source.

Final full-file command:

```powershell
python MyTradingSys/backtest/test_tom_dax_bt.py
```

RESULT (2026-10-12, lab work tree):

```text
.......................................
Ran 39 tests in 0.080s
OK
```

Delivery files: the two code files listed above, this report, and `MyTradingSys/system/tasks/lab-dax-closed-executions.json` via the required `tasks.py done` command. The historical audit report was read, not rewritten. The runner owns the quick shipping gate; it was not run here.

## Follow-up cards created

None. No parameters were tuned. The existing H4 source remains historical evidence, with this report documenting its execution repair and coverage limits.
