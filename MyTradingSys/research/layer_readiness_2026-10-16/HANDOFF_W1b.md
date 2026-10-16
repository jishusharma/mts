# HANDOFF W1b (bb_top_reversal, candle_close) - for W3 wiring. Both are SAMPLING (no edge claim), size OURS 20/2.
1. Modules: `MyTradingSys.backtest.layers.alerts.live_bb_top_reversal.bb_top_reversal_layer` (15m) and `...live_candle_close.candle_close_layer` (1m). Tests beside them (17 pass).
2. cli tuples (live_runner_cli.py, like toc line 392): `("bb_top_reversal", "bb_top_reversal", "15m", lbt.bb_top_reversal_layer)`, `("candle_close", "candle_close", "1m", lcc.candle_close_layer)`.
3. Registry keys: `layer:bb_top_reversal:bb_top_reversal:15m`, `layer:candle_close:candle_close:1m`.
4. size_overrides proposal: both 20 (fixed) / 2 (OURS); events carry "sampling": true.
5. bb_top: short only (card defines no mirror), E2, BB 20/2 pop-stdev, touch cushion 0.05*bandwidth (all OURS in docstring).
6. candle_close: 1m in; arms = study top per side by gross, n>=100: short 3m/week/strong_break, long 15m/day/reclaim (0/126 passed screen).
7. candle_close needs 1440 (day) / 10080 (week) 1m bars of history in the fetch window; shorter -> no events (week arm needs 7d+; long arm needs >1d). W3: check the runner's 1m lookback.
8. Event "t" for candle_close = open of the last 1m bar of the signal candle; event names embed edge+level (dedup-safe).
9. TF/family maps to grep: alert_rate_check TF_MIN/family classifier, auto_trader TF_SECONDS/account routing, test_live_toc_tfs, test_live_runner_wiring.
10. New tests are auto-gated (B150 discovery); no changes to live_layers/cli/config/registry.
