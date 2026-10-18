# Volume event table -- DEV result (1h and 4h)

Source: `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz`, DEV slice (bar open < 2024-07-01, mask applied to the arrays before any bar dict is built; nothing on/after 2024-07-01 read). 4h is built from four consecutive 1h bars at 00/04/08/12/16/20 UTC, complete buckets only.

Params (all OURS): relative volume = volume / median of the same hour-of-week volume over the prior 8 weeks, current bar excluded; spike >= 2.0x; forward window 6 bars from the next bar open; R = spike bar high-low, direction = spike body. Gross, no fees, no rules.

Command: `python MyTradingSys/research/layer_lab/volume_event_table/event_table.py --timeframe 1h` (and `4h`); no CSV written.

| TF | bars (DEV) | rows OK | rows NOT_IN_DATA | spikes | spikes labelled | spikes NOT_IN_DATA | mean MFE (R) | mean MAE (R) |
|---|---|---|---|---|---|---|---|---|
| 1h | 21,888 | 20,540 | 1,348 | 3,392 | 3,388 | 4 | 1.036 | 0.933 |
| 4h | 5,472 | 5,134 | 338 | 645 | 643 | 2 | 1.076 | 0.913 |

NOT_IN_DATA rows are the first 8 weeks (no full baseline: 1,344 1h / 336 4h) plus gaps; spikes NOT_IN_DATA are incomplete forward windows or zero-range bars. Mean MFE slightly above MAE is an event-enumeration fact, not an edge claim (gross, in-bar excursions, no entry rule, no fees).

Tests: `python -m pytest MyTradingSys/research/layer_lab/volume_event_table/test_event_table.py -q -p no:cacheprovider` -> 11 passed (original 5 plus 6 new; the 5 loader/summary tests failed first with missing `load_dev_npz`/`summarize`). `lookahead_lint.py --new`: 0 new hits in this module.

Verdict: DEV table produced; no rule, no tuning, VALIDATION/HOLDOUT unread.
