# Test Gap Report: trade_plan_validator

- **Card**: `testgap-trade-plan-validator-gemini3-1114`
- **Target**: `MyTradingSys/execution/trade_plan_validator.py`
- **Lab deliverable**: `MyTradingSys/research/layer_lab/gemini_1114c/testgap-trade-plan-validator/test_trade_plan_validator.py`

## 1. Existing Coverage Search
Command: `git grep -n "trade_plan_validator" -- MyTradingSys/execution/test_*.py MyTradingSys/execution/testnet/test_*.py scripts/`
- No test file named for `trade_plan_validator` exists.
- Indirect imports/references found:
  - `MyTradingSys/execution/test_r2_runner_exit.py:34`: `import trade_plan_validator as tpv`
  - `MyTradingSys/execution/testnet/test_suite_static.py:36`: `import trade_plan_validator as tpv  # noqa: E402`
  - `MyTradingSys/execution/test_auto_trader_sizes.py:48`: comment `# above trade_plan_validator ceiling`
  - `scripts/worker/audit_targets.json:900`: `"MyTradingSys/execution/trade_plan_validator.py"`

## 2. Pure Functions & Hand-Computed Expectations
From `MyTradingSys/execution/trade_plan_validator.py`:
- `_require(cond, msg)` (`MyTradingSys/execution/trade_plan_validator.py:51-53`): raises `ValidationError(msg)` if `not cond`.
- `_parse_iso8601(s, field_name)` (`MyTradingSys/execution/trade_plan_validator.py:56-61`): normalizes `"Z"` to `"+00:00"` and returns `datetime`; raises `ValidationError` on invalid input.
- `validate(plan: dict) -> tuple` (`MyTradingSys/execution/trade_plan_validator.py:64-73`): calls `_validate_structure(plan)` and `_validate_caps(plan)`; returns `(True, "OK")` or `(False, str(e))`.
- `_validate_structure(plan: dict)` (`MyTradingSys/execution/trade_plan_validator.py:76-105`): checks 9 required fields, `ALLOWED_INSTRUMENTS = {"BTC-PERPETUAL"}` (`:39`), `ALLOWED_SIDES = {"LONG", "SHORT"}` (`:40`), `end > start` (`:91`), `base_unit > 0` (`:94`), entry, stop, optional targets, and `breakeven_after_first_target` (`len(targets) >= 2` at `:103`).
- `_validate_entry(entry: dict)` (`MyTradingSys/execution/trade_plan_validator.py:107-136`): validates `type` in `{"market", "limit", "ladder"}` (`:41`), `limit` positive `price`, `ladder` `0 < low < high`, `1 <= rungs <= 10` (`MAX_LADDER_RUNGS = 10` at `:38`), `len(size_multipliers) == rungs`.
- `_validate_stop(stop: dict)` (`MyTradingSys/execution/trade_plan_validator.py:139-152`): validates `type` in `{"fixed_percent", "trailing_percent", "breakeven_after_fills"}` (`:42`), `0 < percent_below_entry <= 50` (`:147`), `min_fills_for_breakeven >= 1` (`:152`).
- `_validate_targets(targets: list)` (`MyTradingSys/execution/trade_plan_validator.py:155-166`): validates `0 < amount_percent <= 100`, `pnl_target_percent > 0`, and `total_pct <= 100.0001` (`:166`).
- `_validate_caps(plan: dict)` (`MyTradingSys/execution/trade_plan_validator.py:169-210`): validates `0 < max_notional_usd <= 10000` (`MAX_NOTIONAL_CEILING = 10000` at `:35`), `-500 <= max_loss_usd < 0` (`MAX_LOSS_FLOOR = -500` at `:36`), `1 <= max_concurrent_orders <= 10` (`MAX_CONCURRENT_ORDERS_CEILING = 10` at `:37`), `order_count <= max_orders` (`:194`), and `total_units <= max_notional * 1.5` (`:207`).

## 3. Test & Scratch Mutation Results
- `python -m pytest MyTradingSys/research/layer_lab/gemini_1114c/testgap-trade-plan-validator/test_trade_plan_validator.py -v`: `5 passed in 0.16s` (OURS).
- Broken scratch copy mutation: changed `MyTradingSys/execution/trade_plan_validator.py:166` from `_require(total_pct <= 100.0001,` to `_require(total_pct <= 200.0,` in scratch copy; re-running pytest produced `1 failed, 4 passed in 0.35s` with `test_validate_targets_sum_exceeds_100` failing (`AssertionError: assert True is False`).
