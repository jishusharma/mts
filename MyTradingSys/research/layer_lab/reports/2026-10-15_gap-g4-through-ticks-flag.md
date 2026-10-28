# Gap G4: through_ticks in Tom limit simulation — 2026-10-15

**Build result:** `through_ticks=0` preserves touch behavior; `through_ticks=1` requires one price unit of trade-through for entry and target checks. The pre-entry target-cancellation check now uses the same threshold.

## Work and evidence

- `MyTradingSys/backtest/tom_bt.py:175-193`: `sim_limit_trade` accepts `through_ticks=0.0`; entry and pre-entry “ran” target checks use the offset. `MyTradingSys/backtest/tom_bt.py:215`: the in-trade target trigger also uses the offset. `MyTradingSys/backtest/bt/bt_ladder.py:10,23` was read as reference and not changed.
- `MyTradingSys/tests/test_tom_through_ticks.py:21-65`: long/short touch and one-unit-through entry and target cases, pre-entry target cancellation, and default-versus-explicit-zero result equality.
- Red-first evidence: before the pre-entry target check was fixed, `python -m pytest MyTradingSys/tests/test_tom_through_ticks.py -q` failed in `test_target_touch_before_entry_only_cancels_after_trade_through_threshold`: with one tick offset it returned `ran`, expected `no_fill`.
- Verification: `python -m pytest MyTradingSys/backtest/test_tom_bt.py MyTradingSys/tests/test_tom_through_ticks.py -q` — **30 passed**. Also `python -m pytest MyTradingSys/tests/test_tom_through_ticks.py MyTradingSys/tests/test_tom_golden.py MyTradingSys/tests/test_tom_noise_units.py -q` — **19 passed, 3 skipped**. Pytest emitted a cache-path warning (`WinError 183`), with tests passing.
- Existing golden evidence is synthetic: `MyTradingSys/backtest/test_tom_bt.py` includes `test_default_through_ticks_preserves_golden_result`. No BTC 1-minute fixture or BTC-specific `sim_limit_trade` golden was identified in the inspected tests/data paths; this report does not claim a BTC fixture comparison. The new direct default/explicit-zero equality test verifies the default API result.

## Changed files

- `MyTradingSys/backtest/tom_bt.py` — apply the trade-through threshold when determining whether price ran before entry.
- `MyTradingSys/tests/test_tom_through_ticks.py` — add six focused behavior and output-parity tests.
- This report.

The `through_ticks` argument and entry/exit trigger offsets were already present at task inspection; this change completes consistent handling for pre-entry target cancellation. No holdout was read, tuning was not run, and defaults were not changed.
