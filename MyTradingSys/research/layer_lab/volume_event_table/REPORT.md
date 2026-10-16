# Volume event table -- blocked on DEV input

Requested 1h/4h DEV relative-volume event table is implemented in `event_table.py`. It uses prior N same-hour-of-week observations, excludes the current bar, labels unavailable baselines or incomplete forward windows `NOT_IN_DATA`, and reports signed forward return/MFE/MAE in R. R is based on the spike candle's high-low range and body direction.

No permitted DEV klines were found (`Dumps/backtest` is absent), so empirical rows generated: **0**. No holdout was read and no data trial was run.

Test-first regression: bearish excursion test failed before its fix (expected MFE 1.5R, observed 0.0R). Final own test command: `python -m pytest MyTradingSys/research/layer_lab/volume_event_table/test_event_table.py -q -p no:cacheprovider` -> **5 passed**. `py_compile` passed; wiring registry JSON parsed successfully. The test is registered in `scripts/dev/run_extra_tests.py:27`; the module is registered in `wiring_registry.json:827-830`.

**Verdict: BLOCKED** -- required DEV klines are missing, preventing empirical row counts and outcomes.
