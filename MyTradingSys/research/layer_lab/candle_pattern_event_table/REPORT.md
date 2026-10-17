# Candle pattern DEV event table

Run: `python MyTradingSys/research/layer_lab/candle_pattern_event_table/event_table.py` (2026-10-17); input `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz`, masked to bar opens from 2022-01-01 through 2024-06-30 before OHLC dictionaries were constructed. Horizon: 20 bars. R is the signal bar high-low range (OURS).

| Timeframe | Pattern | Rows | OK | NOT_IN_DATA | Mean MFE_R | Mean MAE_R |
|---|---|---:|---:|---:|---:|---:|
| 1h | engulfing | 4,136 | 4,132 | 4 | 3.2149 | 3.1198 |
| 1h | pin_bar | 1,309 | 1,307 | 2 | 3.4251 | 3.5232 |
| 1h | inside_bar | 4,367 | 4,364 | 3 | 4.2599 | 4.1567 |
| 1h | doji | 2,407 | 2,404 | 3 | 3.9801 | 3.9939 |
| 4h | engulfing | 1,054 | 1,050 | 4 | 3.3039 | 3.3198 |
| 4h | pin_bar | 267 | 266 | 1 | 3.6067 | 3.4960 |
| 4h | inside_bar | 1,258 | 1,255 | 3 | 5.0282 | 4.5243 |
| 4h | doji | 729 | 727 | 2 | 4.3458 | 3.6304 |
| **Total** |  | **15,527** | **15,505** | **22** |  |  |

Definitions: engulfing `PRE_REG_CANDLE_PILOT.md:41-42`; pin-bar wick shape `:45-48`; inside-bar `:56`; doji `:56`. Events are detected on closed bars; event timestamp is the bar close and the forward path starts at the next bar (`event_table.py:63-94`). The 4h builder skips incomplete aligned buckets (`event_table.py:43-57`). Forward gaps and truncated 20-bar windows produce `NOT_IN_DATA`, with null MFE/MAE. Directionless inside-bar and doji detections use side `+1` solely as the event table's orientation convention; their directional MFE/MAE is not a directional-pattern claim (`event_table.py:109-115`).

Test command: `python -m pytest MyTradingSys/research/layer_lab/candle_pattern_event_table/test_patterns.py -q -p no:cacheprovider --basetemp=MyTradingSys/research/layer_lab/candle_pattern_event_table/.pytest_tmp` — **9 passed**. Red-first: the added loader test failed during collection against the old implementation because `load_dev_bars` was absent. `python scripts/dev/lookahead_lint.py --new`: zero new FAIL hits; three pre-existing/new WARNs elsewhere remain.

**Delivery blocked:** while attempting to add the event table entry to `MyTradingSys/system/wiring_registry.json`, the write command truncated that file to zero bytes. The workspace contains no other copy, and this unattended sandbox is explicitly barred from running git (including recovery from repository history). Do not ship or mark the card done until the existing registry is restored and the required entry is added. No CSV was written.
