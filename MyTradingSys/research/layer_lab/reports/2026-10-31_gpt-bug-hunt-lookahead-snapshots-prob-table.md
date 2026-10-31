FINDING: one split-boundary look-ahead risk (prob_table.py:184-187); detailed reproducer and checks: MyTradingSys/research/layer_lab/test_hunt_2026-10-31/lookahead_snapshots_prob_table.md

## What was checked

Read `MyTradingSys/backtest/snapshots.py:18-42`, `MyTradingSys/backtest/prob_table.py:7-197`, `MyTradingSys/backtest/test_prob_table.py`, and `MyTradingSys/backtest/test_prob_table_edge.py`. The CLI's chronological 70/30 split can include a training forward-return window extending past the first test timestamp when observations are closer together than the outcome horizon. Five-row reproducing input and proposed fix are in the hunt file.

Snapshot parsing with explicit UTC timestamps and snapshot sorting showed no future-value use. Probability-table feature lookup uses the current supplied record; the finding is exclusively overlapping future label windows across the chronological split. No market rows were needed; these modules consume snapshot JSON and precomputed labels, not candle arrays. No tests were added or run (report-only scope).

## Findings

| Severity | File:line | Result |
|---|---|---|
| MED | `MyTradingSys/backtest/prob_table.py:184-187` | MISMATCH — the split is by start timestamp only and does not purge training forward-return windows that reach into the test interval. See five-row reproducer in `test_hunt_2026-10-31/lookahead_snapshots_prob_table.md`. |
| — | `MyTradingSys/backtest/snapshots.py:18-42` | MATCH — explicit UTC parsing and ordering did not reveal look-ahead. |
| — | `MyTradingSys/backtest/prob_table.py:32-93,103-157` | MATCH — per-record target and feature processing did not access another/future record; overlap risk arises from CLI split described above. |

Follow-up cards created: none.

Noticed: purge training labels whose forward horizon reaches the test boundary.
