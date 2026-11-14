# Test Gap Report: `MyTradingSys/backtest/layers/promotion/registry.py`

## 1. Existing Coverage Check
- Command: `git ls-files "*test_registry*"` returned `MyTradingSys/backtest/layers/promotion/test_registry_gate.py` and `scripts/dev/test_registry_consistency.py`; no `test_registry.py` exists.
- `MyTradingSys/backtest/layers/promotion/test_registry_gate.py:1` covers `apply_promotion_gate`, `load_registry`, `poll_once` wiring, and `auto_trader` rejection (`16 passed in 0.18s` via `python -m pytest MyTradingSys/backtest/layers/promotion/test_registry_gate.py`).
- Direct unit tests for `decision_for_source`, `grandfather_error`, `size_entry`, `entry_for_source`, `alert_source`, and `make_collection_only` were missing from a dedicated `test_registry.py`.

## 2. Pure Functions & Hand-Computed Expectations
- `alert_source(alert)` (`MyTradingSys/backtest/layers/promotion/registry.py:47-49`): formats `"layer:%s:%s:%s"` from `layer`, `sub`, `tf`; empty `{}` yields `"layer:None:None:None"`.
- `entry_for_source(source, entries)` (`MyTradingSys/backtest/layers/promotion/registry.py:52-55`): returns longest-prefix match via `max(hits, key=lambda e: len(e["setup_id"])) if hits else None`; empty `entries=[]` yields `None`.
- `grandfather_error(grandfather)` (`MyTradingSys/backtest/layers/promotion/registry.py:58-77`): returns `None` for `{}` or valid `{prefix: {reason, review_by}}`; returns `"pre_pipeline_sources is not an object"` for non-dict or `"pre_pipeline_sources[%s]: review_by is not a date"` for invalid calendar dates.
- `decision_for_source(source, entries, grandfather)` (`MyTradingSys/backtest/layers/promotion/registry.py:80-91`): returns `'registry_error'` if `entries is None`, `grandfather_error(grandfather) is not None`, or `source` is not `str`; otherwise `'shadow'` / `'trade'` from registry entry, or `'trade'` / `'unregistered'` from `grandfather`.
- `size_entry(v, ceiling=10000)` (`MyTradingSys/backtest/layers/promotion/registry.py:94-104`): `ceiling=10000` (OURS, `MyTradingSys/backtest/layers/promotion/registry.py:94`), contract lot multiple `10` (SOURCED: `"a multiple of 10 (Deribit contract)"` in `MyTradingSys/backtest/layers/promotion/registry.py:96`). Rejects `bool`, non-multiples of `10`, values `> ceiling`, `loss <= 0`, and `float("inf")` with `ValueError`.
- `make_collection_only(alert, why)` (`MyTradingSys/backtest/layers/promotion/registry.py:107-115`): returns a new dict with `"collection_only"` set to `True`, `"promotion_note"` set to `why`, and `"side"` moved to `"shadow_side"` for `"long"`/`"short"`, without mutating input `alert`.

## 3. Lab Tests & Mutation Check
- Created `MyTradingSys/research/layer_lab/gemini_1114c/testgap-registry/test_registry.py` with 5 tests covering normal, empty, and malformed cases via `sys.path.insert`.
- `python -m pytest MyTradingSys/research/layer_lab/gemini_1114c/testgap-registry/test_registry.py`: `5 passed`.
- Scratch mutation: copied `registry.py` to scratch dir and mutated `MyTradingSys/backtest/layers/promotion/registry.py:55` from `max` to `min`. Rerunning `test_registry.py` against the scratch copy failed `test_normal_decision_and_longest_prefix` (`1 failed, 4 passed`).
