# Gap G4 through_ticks flag - 2026-10-15

BLOCKED - required flag-off golden comparison against a BTC fixture cannot be completed: the checkout has no frozen `tom_bt` BTC 1-minute fixture with a recorded expected output. The available `MyTradingSys/data/klines/BTCUSDT_5m.json` is 5-minute sample data and is not a `tom_bt` golden fixture. The card was restored to `ready`; it was not left marked done.

## What changed and was checked

- `MyTradingSys/backtest/tom_bt.py:175-215`: `sim_limit_trade` now accepts trailing `through_ticks=0.0`; long entry/target thresholds apply `entry - through_ticks` / `target + through_ticks`; short entry/target thresholds apply `entry + through_ticks` / `target - through_ticks`, matching the price-offset convention in `bt/bt_ladder.py`. Zero retains the prior comparisons.
- `MyTradingSys/backtest/test_tom_bt.py:34-56`: added red-first tests for exact entry touch vs one-unit trade-through, one-unit target trade-through, and default golden output. The test was run against the old signature first and failed with `TypeError: sim_limit_trade() got an unexpected keyword argument 'through_ticks'`.
- `python -m pytest MyTradingSys/backtest/test_tom_bt.py -q` - **24 passed**. Pytest emitted a cache path warning (`WinError 183`) for the existing `.pytest_cache`; tests passed.
- The default golden assertion covers the existing synthetic unit-test bars and exact result dict (`target`, gross/net R, fees, indexes, held bars, ambiguity). It is not a BTC fixture comparison.
- Fixture inventory command: `Get-ChildItem MyTradingSys -Recurse -File | Where-Object { $_.FullName -match 'fixture|golden' -or $_.Name -match 'BTC.*csv|btc.*csv' }`; results include unrelated golden fixtures, but no frozen `tom_bt` BTC 1m fixture/output. `MyTradingSys/data/klines/BTCUSDT_5m.json` is present, but lacks a 1m `tom_bt` golden expectation.

## Finding

| Severity | Location | Finding | Evidence | Next step |
|---|---|---|---|---|
| MED | `MyTradingSys/system/tasks/gap-g4-through-ticks-flag.json` (`done_when`) | Required BTC fixture golden equality is unverified because that fixture and its frozen expected output are absent. | `done_when` in the task JSON; fixture inventory command above. | Provide a frozen, non-holdout BTC 1m fixture and expected `sim_limit_trade` output, then run the flag-off parity check. |

No BTC backtest, holdout read, tuning, live-tree change, DAX harness edit, git operation, or sync claim/ship/release command was run. No follow-up card was created.
