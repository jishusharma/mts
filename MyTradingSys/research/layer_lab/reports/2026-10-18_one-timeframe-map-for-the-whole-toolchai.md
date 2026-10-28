# One timeframe map for the whole toolchain: report

Card `one-timeframe-map-for-the-whole-toolchai` (build).
Layer: `live_engine` (`MyTradingSys/system/LAYERS.md:192-209`).

## Goal & Architecture (Lesson G)
Unify timeframe maps so that `capture.TF_MINUTES` is the canonical source of truth for the whole toolchain:
- Canonical source: `MyTradingSys/observation/capture.py:33` `TF_MINUTES` (SOURCED: `capture.py:33-34`)
  Keys: `1m`, `3m`, `4m`, `5m`, `15m`, `30m`, `1h`, `2h`, `3h`, `4h`, `6h`, `7h`, `8h`, `12h`, `1d`, `1w` (count: 16).
- Derived set: `scripts/dev/chart_verify.py:19` `TFS = set(capture.TF_MINUTES)`
  Previously hardcoded without `4m`, `3h`, `7h`, `1w` (SOURCED: `git diff 311b710b6c31 scripts/dev/chart_verify.py:17`).
- Derived alert subset: `scripts/dev/alert_rate_check.py:25` `TF_MIN = {k: capture.TF_MINUTES[k] for k in ("1m", "3m", "5m", "15m", "1h", "4h", "1d")}`
  Previously hardcoded literal dict (SOURCED: `git diff 311b710b6c31 scripts/dev/alert_rate_check.py:23`).

## Test Verification
1. Created `scripts/dev/test_tf_map.py`:
   - `test_chart_verify_tfs_equals_capture_tf_minutes`: tests `chart_verify.TFS == set(capture.TF_MINUTES)`
   - `test_alert_rate_check_keys_in_capture_tf_minutes`: tests every key in `alert_rate_check.TF_MIN` is in `capture.TF_MINUTES` with matching minute value.
2. Verified failure on pre-change code:
   Command: `python -m unittest scripts/dev/test_tf_map.py`
   Output: `AssertionError: Items in the second set but not the first: '7h', '3h', '4m', '1w'` (FAIL).
3. Verified pass on post-change code:
   Command: `python -m unittest scripts/dev/test_tf_map.py scripts/dev/test_chart_verify.py scripts/dev/test_alert_rate_check.py scripts/dev/test_shot.py`
   Output: `Ran 45 tests in 1.731s - OK`.
4. Verified no remaining literal TF dicts in those files:
   `git grep -n "TF_MIN" MyTradingSys/observation/capture.py scripts/dev/chart_verify.py scripts/dev/alert_rate_check.py` confirms only canonical `TF_MINUTES` in `capture.py`, derived `TFS` in `chart_verify.py`, and derived `TF_MIN` in `alert_rate_check.py`.
