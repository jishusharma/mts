# P0-C identity table: live registry key -> detector / side / entry / exit / cost / config

Source: `MyTradingSys/backtest/layers/alerts/live_runner_cli.py` build_registry (lines ~246-310) and
`alerts/live_layers.py`. Cost and exit are NOT per layer: detectors emit only {t, side, event}; sizing, stop and
fees belong to `execution/auto_trader.py` (RT_TAKER_FEE_FRAC 0.0010 = worst-case round trip, line 197).
Per-layer exit rules: NOT IN DATA at the detector (a trade plan is built downstream); do not infer one.

| key (layer/sub/tf) | detector | side | entry | config (params_id) | status |
|---|---|---|---|---|---|
| rsi/rsi_events/1h,15m,5m | live_layers.rsi_level_layer -> rsi_events | only on `failure`: resolved below -> short, above -> long; support/rejection/cross no side | resolving bar close | level 40, tol 0.5, RSI14 (rsi_40_tol0.5_L1_2026-09-29) | LIVE; tol 0.5 is an in-sample grid pick = NO-SOURCE |
| fabio/cvd_absorption/1h,15m | cvd_absorption_events | detector's own | event bar | fabio_cvd_default_2026-09-29 | LIVE |
| fabio/escalation/1h,15m | escalation_layer | e["side"] | event bar | escalation_defaults_2026-09-29 | LIVE |
| fabio/volume_fvg/1h,15m | volume_fvg_layer (20 bins) | close at start vs mid: above -> short, else long | touch bar | volume_fvg_defaults_2026-09-29 | LIVE |
| fabio/v3_grid/1m | make_fabio_v3_layer | per grid cell; SHADOW cells collection-only | per cell | FABIO_V3_PARAMS_ID | LIVE |
| session/session_momentum/15m | session_momentum_layer | e["side"] | bar e["i"] | session_momentum_defaults_2026-09-29 | LIVE |
| positioning/funding_cvd_fade/1h | make_funding_layer | fade crowded side (bear CVD div + funding pct >= 0.95 -> short) | bar e["i"] | funding_cvd_fade_defaults_2026-09-29 | LIVE |
| rsi/malkan_bull/1h | malkan_setup_bull (MLK-S1) | long | candle after support bounce | module defaults: tol 2.0, regime lookback 20, RSI14 | LIVE; research label MalkanView |
| rsi/malkan_bear/1h | malkan_setup_bear (MLK-S2) | short | candle after rejection at 60 | same defaults | LIVE |
| cryptocred/sr_flip, fib_pullback, failed_msb /1h,15m | setup1/2/3 via _cc_layer | setup's own | entry_t, carries entry_price + stop | module defaults | LIVE; only CC keys carrying a source stop |
| turn_of_candle/turn_of_candle/1m | turn_of_candle_events(lead 1) | sign of minute-0 taker imbalance of same quarter; 0/missing -> none | minute 14 close | C3, `sampling: True` | LIVE, no-edge, fill collection only |

## ER-02 / ER-03 tolerance resolution
- 0.5 = LIVE (RSI level 40, `live_layers.RSI_TOL`; default.json is test-only).
- 2.0 = RESEARCH label (MalkanView, `malkan_*` module default). NOTE the malkan_bull/bear keys also run live with 2.0,
  so two tolerances for the 40 level do coexist live under different keys (rsi_events vs malkan_*): different
  experiments, never share a label or pool their rows.
