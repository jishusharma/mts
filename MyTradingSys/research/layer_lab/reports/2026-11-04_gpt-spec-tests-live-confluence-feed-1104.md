# GPT spec tests: live confluence feed

Changed file: `MyTradingSys/tests/test_live_confluence_feed.py` (5 tests). Feeder implementation remained unchanged.

## What was checked

- `MyTradingSys/backtest/layers/alerts/live_confluence_feed.py:48-49,65,81-110`: primary 12 / maximum 18 windows, classification, close inputs, and Malkan/Krown event mapping.
- `MyTradingSys/backtest/layers/rsi/rsi_divergence.py`: strict local close pivots and inclusive A/B bar count; `krown_hidden_divergence.py`: distinct hidden divergence definition.
- Added deterministic tests with fixed RSI values so expected divergence directions, pivot spacing, and code mapping are independent of RSI calculation details.
- The 12/18 window values are tested as current **OURS** parameters, per card note (Hindi concepts: 18 NOT_IN_DATA). The test expects 12 = STRONG, 18 = OK, >18 = WEAK and not emitted.

## Findings

| Severity | Evidence | Finding | Status / action |
|---|---|---|---|
| LOW | `test_live_confluence_feed.py:30-43`; `live_confluence_feed.py:48-49` | 12-bar and 18-bar primary Malkan windows are checked with expected STRONG/OK labels. | MATCH; locked by tests as OURS. |
| LOW | `test_live_confluence_feed.py:45-51`; `live_confluence_feed.py:65` | A 20-bar pair is not emitted by the primary Malkan window and the class helper returns WEAK. | MATCH; >18 is WEAK, not a signal. |
| LOW | `test_live_confluence_feed.py:54-65`; `rsi_divergence.py:_pivots` | Changing wick lows while holding closes fixed does not change Malkan primary events. | MATCH; pivots use close values. |
| LOW | `test_live_confluence_feed.py:68-81`; `live_confluence_feed.py:100-110` | Krown hidden bullish wiring emits `K-HBULL`, sourced to KROWN-CONFLUENCE, close basis, collection-only, without a side. | MATCH. |

## Verification

- `python -m pytest MyTradingSys/tests/test_live_confluence_feed.py -q` - **5 passed**. Pytest emitted a cache-path warning (`WinError 183`); test process exited successfully.
- Mutation check: temporarily changed `WINDOW_MAX` from 18 to 17. The 18-bar parametrized test failed (1 failed, 4 passed). Restored `WINDOW_MAX = 18`; final suite passed.
- No market data was read; tests use synthetic bar fixtures.
- No follow-up cards created.
