# gptb-bb-top-reversal-event-table

**1,577 DEV events; 1,577 complete 16-bar outcomes; own tests: 4 passed.** Card marked done by `python scripts/dev/tasks.py done gptb-bb-top-reversal-event-table --result "1577 DEV events; 4 tests pass; MyTradingSys/research/layer_lab/reports/2026-10-17_gptb-bb-top-reversal-event-table.md"`.

## Work and evidence

- Added `MyTradingSys/research/layer_lab/bb_top_reversal_event_table/event_table.py`: causal BB(20,2) green-bar test, next-red close below green open, next-bar-open entry, short forward MFE/MAE for 16 bars. R is OURS: red high minus entry. Incomplete forward data is `NOT_IN_DATA` (module constants, detector and outcome handling).
- Wrote tests first. Before implementation, pytest failed at collection because the module did not exist. Final command `python -m pytest MyTradingSys/research/layer_lab/bb_top_reversal_event_table/test_event_table.py -q -p no:cacheprovider` -> **4 passed**. The four cases verify hand-computed band/R, red close above green open, green high below band, and that post-red bars do not feed setup flags (`test_event_table.py`).
- DEV input: `F:/MTS/data/bigtrade/cache/perp/klines_15m.npz`, restricted by the loader to timestamps `[1640995200000, 1719792000000)` (2022-01-01 through 2024-06-30; `event_table.py`). This yielded 87,552 bars. Run command: `python MyTradingSys/research/layer_lab/bb_top_reversal_event_table/event_table.py --output MyTradingSys/research/layer_lab/bb_top_reversal_event_table/events_dev.csv` -> `bars=87552 events=1577 labeled=1577 not_in_data=0`. Mean gross MFE 2.7692R and MAE 3.0843R. Temporary CSV removed after aggregate counts; trial row is in `MyTradingSys/research/layer_lab/TRIALS.md`.
- Registered the test in `scripts/dev/run_extra_tests.py` EXTRA and the new tool in `MyTradingSys/system/wiring_registry.json`. `py_compile` passed; registry JSON parsed successfully. The companion build summary is `MyTradingSys/research/layer_lab/bb_top_reversal_event_table/REPORT.md`.

## Scope

DEV only. VALIDATION/HOLDOUT were not read. No live path, shared engine, trading rule, or tuning was changed. This is gross descriptive excursion data, not an edge claim.

## Evidence references

| Severity | Evidence | Finding |
|---|---|---|
| LOW | MATCH ? `MyTradingSys/backtest/layers/alerts/live_bb_top_reversal.py:11-14, 50-64`; implemented at `MyTradingSys/research/layer_lab/bb_top_reversal_event_table/event_table.py:46-68` | The detector uses the green candle's upper band, then a consecutive red candle below the green open. Research implementation follows the requested simplified detector without touching the live source. |
| LOW | MATCH ? `event_table.py:69-95`; hand calculation asserted in `test_event_table.py:24-37` | Entry and 16-bar short MFE/MAE use the requested OURS R definition. |
| LOW | MATCH ? `event_table.py:99-111`; run command and output above | Input is filtered to DEV timestamps before OHLC rows are built; observed 87,552 bars and 1,577 complete events. |
| LOW | MATCH ? `scripts/dev/run_extra_tests.py:32`; `MyTradingSys/system/wiring_registry.json:843`; `MyTradingSys/research/layer_lab/TRIALS.md:3` | Test/tool are gated and the DEV run is logged. |
