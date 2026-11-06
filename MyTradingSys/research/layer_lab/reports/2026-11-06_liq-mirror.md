# liq_mirror.py spec test (gpt-spec-tests-liq-mirror-1106)

- Test: MyTradingSys/research/liq_mirror_2026-11/test_liq_mirror_spec.py, written from the liq_mirror.py module docstring (contract), 11 tests.
- Trunk: `python -m pytest MyTradingSys/research/liq_mirror_2026-11/test_liq_mirror_spec.py -q` -> 11 passed.
- Mutation (copy in %TEMP%, source untouched): liq_mirror.py:96 `if mv <= -move_pct:` -> `if mv <= move_pct:`. Result: 1 failed, 10 passed; failing test `test_move_below_threshold_is_unresolved` (a +0.4% move was wrongly counted as a reversal).
- Constants (3 events, 5 min gap, 60 min hold, 0.5%) are OURS per docstring line 4 (`DECISION (OURS)`); the test pins them.
- No contract/code mismatch found.
- Note: pytest `tmp_path` fails here (PermissionError on Temp/pytest-of-E-ngineers), so tests use tempfile.TemporaryDirectory.
