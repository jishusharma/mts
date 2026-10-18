# Gap G1 Pre-Reg Power (verdicts.py check)

Verdict: BUILD COMPLETE — `verdicts.py check` prints MDE80, net mean, trades-for-80%-power, and LOW-POWER flag; 13 tests pass in `scripts/dev/test_verdicts.py`; `VERDICTS.csv` byte-identical.

## What was checked or run

- Red-first test added to `scripts/dev/test_verdicts.py:107-134`. Ran `python scripts/dev/test_verdicts.py`: failed with `AttributeError: module 'verdicts' has no attribute 'power_line'` (3 errors out of 13 tests).
- Implemented `power_line(row)` in `scripts/dev/verdicts.py:331-366` and called it in `cmd_check` (`scripts/dev/verdicts.py:390-392`).
- Green test run: `python scripts/dev/test_verdicts.py` -> 13 tests passed.
- Command check: `python scripts/dev/verdicts.py check "imbalance qriptal"` printed `power: MDE80=0.02521 net=-0.1467 trades_for_80_power=97` and `power: MDE80=0.02886 net=-0.1629 trades_for_80_power=85`.
- Verified `MyTradingSys/research/VERDICTS.csv` is unchanged and byte-identical (`git diff MyTradingSys/research/VERDICTS.csv` produces zero diff).

## Numbers and Sources

- `2.8016`: SOURCED (`MyTradingSys/research/backtest_gap_review_2026-10-13/REPORT.md:211-212`, `trades for 80 % = ((1.96 + 0.8416) * sd / mean)^2`; two-sided alpha=0.05 $z=1.96$, 80% power $z=0.8416$).
- Test row: `n=400`, `se_pct=0.10`, `gross=0.20`, `cost=0.05`:
  - `net = 0.20 - 0.05 = 0.15`: SOURCED (`MyTradingSys/system/tasks/gap-g1-prereg-power.json:50`).
  - `MDE80 = 2.8016 * 0.10 = 0.28016`: SOURCED (`MyTradingSys/system/tasks/gap-g1-prereg-power.json:50`).
  - `|net mean| = 0.15 < 0.28016` -> `LOW-POWER`: SOURCED (`MyTradingSys/system/tasks/gap-g1-prereg-power.json:50`).
  - `trades for 80% power = 400 * (0.28016 / 0.15)^2 = 1395`: SOURCED (`MyTradingSys/system/tasks/gap-g1-prereg-power.json:50`).
- Adequate-power test case: `gross=0.40`, `cost=0.05`, `net=0.35 >= 0.28016`, no `LOW-POWER`, trades for 80% = `round(400 * (0.28016 / 0.35)^2) = 256`: OURS.

## Findings

| Severity | Location | Finding | Evidence |
|---|---|---|---|
| INFO | `scripts/dev/verdicts.py:331-366` | Helper `power_line` cleanly ignores non-numeric and UNPARSED rows while displaying MDE80 and trades-for-80%-power when parameters are present. | `python scripts/dev/test_verdicts.py` 13 passed; `scripts/dev/verdicts.py check "imbalance qriptal"` |
