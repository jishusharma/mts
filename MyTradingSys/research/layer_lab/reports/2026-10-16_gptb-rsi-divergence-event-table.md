# 640 complete RSI divergence DEV event rows

Verdict: 640 complete rows (643 events; 3 `NOT_IN_DATA`).

| Severity | File:line | Finding and evidence | Proposed fix |
|---|---|---|---|
| LOW | `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:3-4` | MATCH — sourced divergence spacing is 3–10 bars. | None. |
| LOW | `MyTradingSys/research/layer_lab/rsi_divergence_event_table/event_table.py:15,76` | MATCH — cache input is DEV filtered; entry is the open after the causal event index. | None. |
| LOW | `MyTradingSys/research/layer_lab/rsi_divergence_event_table/event_table.py:89` | MATCH — 3 events lack the full forward window and retain `NOT_IN_DATA` with blank excursions. | None. |
| LOW | `MyTradingSys/research/layer_lab/rsi_divergence_event_table/test_event_table.py:21-51` | MATCH — `python -m pytest MyTradingSys/research/layer_lab/rsi_divergence_event_table/test_event_table.py -q`: 4 passed. | None. |

Checked: read-only detector `MyTradingSys/backtest/layers/rsi/rsi_divergence.py`; sourced result `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md`; DEV cache `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz` (2022-01-01 through 2024-06-30 bars only). See the study report for command and row counts.

The full method, source, data cutoff, counts, and fail-first evidence are in `MyTradingSys/research/layer_lab/rsi_divergence_event_table/REPORT.md`.
