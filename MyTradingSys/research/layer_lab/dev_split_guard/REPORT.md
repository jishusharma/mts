# DEV split guard

**Build result:** `event_table.py` provides `dev_only(rows, t_key)` and `assert_dev(rows, t_key)` as pure functions. The accepted UTC window is 2022-01-01T00:00:00Z inclusive through 2024-06-30T23:59:59.999Z (implemented as a half-open range ending 2024-07-01T00:00:00Z). Epoch milliseconds and ISO-8601 strings are supported. Missing or malformed timestamps raise `ValueError`.

**Counts:** 4 focused tests; 4 passed. The tests use 3 boundary/split rows, 2 equivalent-format rows, 1 missing-timestamp row, and 2 start-boundary rows. No market data was needed or read; no backtest/trial was run.

**Test output:**

```
python -m pytest MyTradingSys/research/layer_lab/dev_split_guard/test_event_table.py -q -p no:cacheprovider
....                                                                     [100%]
4 passed in 0.07s
```

**Wiring:** the test is listed in `scripts/dev/run_extra_tests.py` EXTRA; `event_table.py` is registered as a TOOL in `MyTradingSys/system/wiring_registry.json`.
