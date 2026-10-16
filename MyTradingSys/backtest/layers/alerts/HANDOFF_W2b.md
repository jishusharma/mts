# HANDOFF W2b - bigtrade_fires (row 13): NOT a wiring, it is a BUILD. No adapter shipped.
Step (1) result: `backtest/bigtrade/fires_kline.py:106 kline_registry` is NOT a pure causal fn(bars) for a bigtrade layer.
- It imports `live_runner_cli.build_default_registry` and returns the EXISTING live layers' registry (minus B2_KEYS): it is a
  replay harness that re-runs layers already live (turn_of_candle, rsi, malkan, fabio, cc_*, session), not a detector of its own.
- "FIRES-B1 parity PASS" = those live layers replayed on 1m klines match live output; it validates the harness, not a bigtrade signal.
- `bigmoves.py` (the "bigtrade" ground truth) is hindsight by design (ATR zigzag legs, forward MFE/MAE labels): look-ahead, unusable live.
- "volume_candles_ma" appears in no .py under MyTradingSys; no source-sourced causal detector exists to wrap.
Therefore no params can be taken "from the backtest that produced FIRES-B1" (they belong to other layers, already wired).
DECISION (OURS): reclassify row 13 as build per LAYER_READINESS rule ("not a pure fn(bars) -> build"); W3 wires nothing for it.
Needed to build: a transcript-sourced volume-candle/MA detector spec (provenance rule), then adapter + tests. Size if built: OURS 20/2.
