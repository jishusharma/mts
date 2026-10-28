# tom-v2-btc-min-stop-width — 2026-10-18

**Result:** Minimum stop width gate implemented in `scripts/dev/tom_noise_units.py` and `MyTradingSys/backtest/tom_bt.py`. Off by default (`min_width=None` preserves bit-identical output). `test_worked_example` and `test_off_by_default_identity` pass.

## Sourced vs Ours Parameter Classification

- **0.88**: SOURCED (TOM_LAYER_V2_SPEC.md:313; his 20-point stop, k0zm5NYn0IQ:22-24).
- **0.25 R**: SOURCED (PROJECT_VISION.md:234: "Stops are wide enough that fees cost under 0.25 R").
- **20-day lookback**: OURS (TOM_LAYER_V2_SPEC.md:315).
- **10-day and 40-day lookbacks**: OURS (TOM_LAYER_V2_SPEC.md:315).
- **Worked example parameters**: SOURCED (TOM_LAYER_V2_SPEC.md:333-335: entry 100000, N5 0.14%, W_noise 123.20, taker W_fee 400.00, W_min 400.00, stop 100399 dropped, 100400 kept at 0.25 R, FEES_DERIBIT W_fee 200.00).
- **Formula 12 example bars**: SOURCED (FORMULAS.md:337-339: highs=[10,11,12,11], lows=[9,9,10,9], closes=[9.5,10.5,11.5,10], TRs=[2, 2, 2.5], median TR fraction 2 / 10.5 = 0.190476).

## Work Done

1. `scripts/dev/tom_noise_units.py`:
   - Added `min_stop_width(entry, n5, fees)` returning `max(0.88 * n5, fee_rt / 0.25) * entry`.
   - Added `n5(bars, asof=None, days=20)` computing median true range of completed 5-minute bars over trailing UTC days as a fraction of close, reusing `true_ranges` and `aggregate`.
2. `MyTradingSys/backtest/tom_bt.py`:
   - Imported `min_stop_width` from `tom_noise_units`.
   - Added `min_width=None` argument to `run_variant`. When provided as a callable `asof_ms -> n5`, any signal with stop distance `< min_stop_width` is dropped with `filled=False, reason="stop_below_min_width"`. `min_width=None` leaves existing output completely unchanged.
3. `MyTradingSys/tests/test_tom_min_stop_width.py`:
   - Added `test_worked_example` and `test_off_by_default_identity`.
   - Failed first on the old codebase: `AttributeError: module 'tom_noise_units' has no attribute 'min_stop_width'` and `TypeError: run_variant() got an unexpected keyword argument 'min_width'`.

## Lookback 10, 20, 40 Floors as of 2026-06-25

Computed with `tom_noise_units.load` on `F:/MTS/data/tom_raw/klines` as of 2026-06-25 (OURS calculation; nothing chosen):
- **Lookback 10 UTC days (2026-06-16..2026-06-25, 2,880 5m bars)**:
  `N5 = 0.13746%` (`0.001375`), `W_noise = 0.12097%`, `W_fee_taker = 0.40%` -> `W_min_taker = 0.40%`; `W_fee_deribit = 0.20%` -> `W_min_deribit = 0.20%`.
- **Lookback 20 UTC days (2026-06-06..2026-06-25, 5,760 5m bars)**:
  `N5 = 0.15029%` (`0.001503`), `W_noise = 0.13226%`, `W_fee_taker = 0.40%` -> `W_min_taker = 0.40%`; `W_fee_deribit = 0.20%` -> `W_min_deribit = 0.20%`.
- **Lookback 40 UTC days (2026-05-17..2026-06-25, 11,520 5m bars)**:
  `N5 = 0.13640%` (`0.001364`), `W_noise = 0.12004%`, `W_fee_taker = 0.40%` -> `W_min_taker = 0.40%`; `W_fee_deribit = 0.20%` -> `W_min_deribit = 0.20%`.

In all lookbacks, taker fees (0.10% RT) set a fee floor of 0.40% that dominates `W_noise` (~0.12-0.13%), while Deribit maker/taker fees (0.05% RT) set a fee floor of 0.20% that also dominates `W_noise`.

## Verification Commands and Output

- `python -m pytest MyTradingSys/tests/test_tom_min_stop_width.py -q`: `2 passed in 0.10s`.
- `python -m pytest MyTradingSys/tests/test_tom_noise_units.py -q`: `2 passed in 0.11s`.
- `python -m pytest MyTradingSys/tests -k "tom" -q`: `31 passed, 5 skipped, 626 deselected in 1.73s`.
- No BTC backtest was run. No live tree or holdout data (2026-06-26 onwards) was touched.
