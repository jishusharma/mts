# RSI divergence event table

Built a research-only BTCUSDT event table using the read-only divergence detector. The sourced interval is 3 to 10 bars (MTF result, `research/rsi_divergence_mtf_2026-10-09/RESULT.md`); RSI delta threshold is zero, so RSI must be strictly higher/lower as specified by the detector. The table measures both bullish and bearish events. Entry is the open one bar after the detector's causal event index. `R` is ATR14 at entry (provided 1h ATR from the cache; Wilder ATR14 recalculated from aggregated 4h OHLC). MFE/MAE use the next 24 bars including the entry bar. Incomplete windows remain as `NOT_IN_DATA` with blank excursion fields.

## Run

Command: `python -c "from MyTradingSys.research.layer_lab.rsi_divergence_event_table.event_table import run; from collections import Counter; rows=run(); print(len(rows),Counter((x['timeframe'],x['status']) for x in rows))"`

Input: `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz`; bars opening before 2024-07-01 00:00 UTC only. The 4h bars use complete UTC buckets starting at 00/04/08/12/16/20 UTC. Validation and holdout bars were not read.

Result: 643 events total: 502 1h `OK`, 2 1h `NOT_IN_DATA`, 138 4h `OK`, and 1 4h `NOT_IN_DATA`. All rows are retained. The three unavailable outcomes lack a complete 24-bar forward window at the DEV boundary.

## Tests

Fail-first: initial test collection failed because `event_table.py` did not exist. Final command: `python -m pytest MyTradingSys/research/layer_lab/rsi_divergence_event_table/test_event_table.py -q` → 4 passed. The synthetic bullish fixture checks pivots `(2, 6)`, next-bar-open entry, hand-calculated MFE/MAE, horizon isolation, empty input, and incomplete-window handling.
