# gptb-dev-split-guard

**Changed files + test output:** Added `MyTradingSys/research/layer_lab/dev_split_guard/event_table.py` with `dev_only(rows, t_key)` and `assert_dev(rows, t_key)`. The guard keeps UTC open times from 2022-01-01T00:00:00Z through 2024-06-30T23:59:59.999Z, accepts epoch milliseconds and ISO-8601 timestamps, returns the number of rows excluded by `dev_only`, and raises `ValueError` for missing/invalid timestamps or any timestamp outside DEV. The effective interval is `[1640995200000, 1719792000000)`.

**Red/green evidence:** First test run, before implementation:

```
python -m pytest MyTradingSys/research/layer_lab/dev_split_guard/test_event_table.py -q -p no:cacheprovider
ERROR collecting ...
FileNotFoundError: ...dev_split_guard/event_table.py
1 error in 0.24s
```

After implementation:

```
python -m pytest MyTradingSys/research/layer_lab/dev_split_guard/test_event_table.py -q -p no:cacheprovider
....                                                                     [100%]
4 passed in 0.07s
```

**Counts/data:** 4 test cases; 4 passed. Fixture rows exercised: 3 split boundary rows, 2 same-time rows encoded as ISO and milliseconds, 1 missing timestamp, and 2 start-boundary rows. No market data was necessary or read; no trial/backtest was run. Missing input status: NOT_IN_DATA is not applicable because this utility consumes caller-provided rows and the task required no dataset.

**Registry/gate:** `scripts/dev/run_extra_tests.py` EXTRA contains the new test; `MyTradingSys/system/wiring_registry.json` registers the new non-test module as TOOL. Details are in `MyTradingSys/research/layer_lab/dev_split_guard/REPORT.md`.
