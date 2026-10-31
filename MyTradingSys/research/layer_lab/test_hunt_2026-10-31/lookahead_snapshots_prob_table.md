# Look-ahead hunt: snapshots and probability table

Verdict: FINDING — the CLI's 70/30 split can put a training forward-return window across the first test timestamp when labels are closer together than the selected horizon. No future-bar read was found in snapshot loading or feature lookup itself.

## Scope and method

Read `MyTradingSys/backtest/snapshots.py` (lines 18–42), `MyTradingSys/backtest/prob_table.py` (lines 7–197), `MyTradingSys/backtest/test_prob_table.py`, and `MyTradingSys/backtest/test_prob_table_edge.py`. Checked timestamp parsing, snapshot ordering, label sorting, table training, test scoring, and CLI split. Existing `test_prob_tables.py` under `research/rsi_deep_buy_2026-10-19` is a separate research consumer and was not used as a test for this module. No test was added or run: this is a report-only hunt.

The modules do not accept candle arrays. `snapshots.py` reads JSON snapshots; `prob_table.py` reads precomputed outcomes. Therefore no bar-array perturbation applies directly. The reproducible synthetic five-row sequence below models 15-minute label timestamps with a 60-minute forward label; it isolates the split/window-boundary defect without reading any post-2024-07-01 market rows. No market-data source was needed for this boundary proof.

## Finding

| Severity | File:line | Finding | Evidence | Proposed fix |
|---|---|---|---|---|
| MED | `MyTradingSys/backtest/prob_table.py:184-187` | Chronological split assigns records by their label start timestamp only. With 15-minute observations and `--horizon 60m`, the last training label's outcome window includes prices at/after the first test timestamp. Its outcome can therefore use test-period prices when fitting the training probability table. | Reproducer below: with five 15-minute rows, `split_idx=3`; row 2 at 00:30 remains training while its 60-minute outcome endpoint is 01:30, after test begins at 00:45. | Purge training records whose forward-label end (`ts + selected horizon`) is at or beyond the first test timestamp; derive the horizon duration explicitly for each supported label key. Alternatively add a gap of at least the maximum label horizon before test. |

### Five-row reproducing input

Assume `ts` is the 15-minute candle open and `fwd_return_pct["60m"]` is computed from that row's close to the close four bars later. Values are illustrative and hand-constructed; no market outcomes are claimed.

| Sorted row | `ts` (UTC) | close | `fwd_return_pct["60m"]` uses close at | Split assignment |
|---:|---|---:|---|---|
| 0 | 2024-06-30 00:00 | 100 | 01:00 | train |
| 1 | 2024-06-30 00:15 | 101 | 01:15 | train |
| 2 | 2024-06-30 00:30 | 102 | 01:30 | train **(leaks into test interval)** |
| 3 | 2024-06-30 00:45 | 103 | 01:45 | test begins |
| 4 | 2024-06-30 01:00 | 104 | 02:00 | test |

Reproduction: sort these five records as `load_labels()` does; `int(5 * 0.7) == 3`, so rows 0–2 train and rows 3–4 test. Row 2's 60-minute forward target reaches 01:30, after the test interval starts at 00:45. Thus the training table at `build_table(train, ...)` incorporates future prices from the test interval. This issue concerns label-window overlap; it is not a feature-at-time-t lookup of a future candle.

## Other checks

- `snapshots.py:18-20`: explicit `Z` timestamps become `+00:00` and parse to absolute epoch seconds. Truncating fractional seconds to microseconds discards precision but not future data. **NO LEAK FOUND** for explicit UTC timestamps.
- `snapshots.py:28-41`: glob/load/sort uses each snapshot's own timestamp; no next snapshot value is copied into an earlier record. **NO LEAK FOUND** in inspected logic.
- `prob_table.py:32-93`: each record contributes only its supplied horizon return to counts. This is the intended target for a supervised outcome table; no additional `t+1` bar access occurs here.
- `prob_table.py:103-157`: evaluation trains from the supplied `train` list and scores supplied `test` records; feature values are read from the same test record. However the CLI split does not purge overlapping training labels, as detailed above.
- Timezone/session boundaries: the CLI sorts `ts` lexicographically. This is chronological only if timestamps have a consistent, sortable representation (for example uniform ISO-8601 UTC). Mixed offsets or mixed formats can misorder rows. No fixture or label file for this consumer was present in the inspected scope to establish that such mixed values occur, so this remains a conditional risk, not a finding. `parse_ts()` accepts naive timestamps as local time; the data contract says `timestamp_utc`, and explicit UTC strings are handled correctly. No boundary defect demonstrated.
- Existing tests cover probability arithmetic, missing values and split sizes, but the chronological-split test asserts counts only; it does not assert non-overlap of forward-label windows.

## Artifacts and commands

- `MyTradingSys/research/layer_lab/test_hunt_2026-10-31/lookahead_snapshots_prob_table.md` — this hunt and reproduction.
- `MyTradingSys/research/layer_lab/reports/2026-10-31_gpt-bug-hunt-lookahead-snapshots-prob-table.md` — delivery report.
- Inputs inspected: target source and tests listed above. No external market rows read; no command-based test executed.

Follow-up cards created: none.
Noticed: CLI evaluation split needs forward-label horizon purging to prevent train outcomes crossing into the test interval.

