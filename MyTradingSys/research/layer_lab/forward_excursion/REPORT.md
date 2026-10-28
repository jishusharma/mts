# Forward excursion helper

**Result:** 5 tests passed; the helper measures MFE/MAE in R from the entry bar close over subsequent bars, records first 1R touch with same-bar stop priority, and flags a horizon cut short by available data.

## Built

- `event_table.py:4-51` exposes the pure `forward_excursion(bars, i_entry, side, r_price, horizon)` function. It consumes caller-provided OHLC lists only; no data rows were loaded (synthetic test fixture: 6 bars per direction).
- `test_event_table.py:22-51` checks hand-computed long and mirrored short excursions (2.0R MFE, 0.5R MAE), same-bar ambiguity, horizon truncation, and invalid R size.
- Registered in `scripts/dev/run_extra_tests.py:29` EXTRA and `system/wiring_registry.json:834` as a research TOOL.

## Test evidence

Red first: `python -m pytest MyTradingSys/research/layer_lab/forward_excursion/test_event_table.py -q` failed during collection because `event_table.py` was absent (`FileNotFoundError`).

Green: `python -m pytest MyTradingSys/research/layer_lab/forward_excursion/test_event_table.py -q -p no:cacheprovider` -> `5 passed in 0.07s`.

No market data or trial rows were used.
