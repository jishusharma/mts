# DEV boundary fix - bigtrade event table (2026-10-17)

## What was wrong
Repo split (MyTradingSys/system/OPERATOR_DECISIONS.md:878): DEV 2022-01-01..2024-06-30, VALIDATION 2024-07-01..2025-06-30, HOLDOUT after.
`event_table.py:17` had `DEV_END_MS = 1735689600000` (2025-01-01) and REPORT.md said DEV ended 2024-12-31. Fire rows and the 20 forward excursion bars therefore read 2024-07..2024-12 = VALIDATION. Origin: `fires_kline.py:87` SPLITS names TRAIN as 2022-01-01..2025-01-01 (a separate, older bigtrade split; the table filtered on it).

## Fix
- `DEV_END_MS = 1719792000000` (2024-07-01 00:00 UTC, exclusive; checked with python datetime). Fires at/after it are dropped and excursion bars are clipped before it.
- New test `test_dev_end_is_2024_07_01_and_no_fire_or_bar_at_or_after_it` (already in EXTRA / wiring_registry via the existing test file). Run against the old `git show b6c4cef1:...event_table.py` copy: 1 failed (assert DEV_END_MS == 1719792000000), 4 passed; against the fix: 5 passed.
- Same constant bug fixed in `oi_delta_event_table/event_table.py:8` (was 1735689600000).

## Counts (regenerated, 5 s CPU, F:/MTS/data/bigtrade)
| | old (to 2025-01-01) | new (to 2024-07-01) |
|---|---|---|
| rows | 153,685 | 128,078 |
| OK | 6,748 | 5,685 |
| NOT_IN_DATA | 146,937 | 122,393 |
| 15m OK / missing | 5,400 / 13,046 | 4,540 / 10,969 |
| 1h OK / missing | 1,348 / 2,804 | 1,145 / 2,339 |
| 1m, 5m OK | 0 | 0 |
Max `t_fire_ms` in the new CSV < 1719792000000. No outcome analysis was run.

## Other boundaries (not fixed, listed)
- `MyTradingSys/backtest/bigtrade/fires_kline.py:87` SPLITS TRAIN to 2025-01-01, VALIDATE 2025-01-01..2025-07-01 (+ test_fires_kline.py:434-435): bigtrade's own split disagrees with the repo split, so every bigtrade "TRAIN" artifact (fires CSVs, labels) includes 2024-07..12. Not clear-cut to change (re-labels data on F:); needs an audit card.
- `research/tom_btc_2026-10-13/chart_lab.py:21` DEV 2024-12-01..2025-03-31 and `levels_confluence_2026-10-14` (DEV 2024-12..2025-03, already noted in imbalance_qriptal filter RESULT.md:110 and LAB_BLOCKED): inside VALIDATION by design of those studies; flagged elsewhere, left as is.
- All other DEV_END hits (candle_patterns, context_factors*, volume_2026-10-09, wlow_bounce, krown, imbalance filter, volume_event_table) already use 2024-07-01.

## Contaminated items
`CONTAMINATED (DEV read VALIDATION 2024-07..12)`: the old bigtrade_event_table (REPORT.md, event_table.csv, reports/2026-10-16_gptb-bigtrade-event-table.md, INDEX.md row, task card gptb-bigtrade-event-table result). No VERDICTS.csv row, Research Map entry or other consumer was found referencing it (grep of bigtrade_event_table / event_table.csv / card id). The oi_delta table had the same constant but its inputs are absent, so it produced no rows. The VALIDATION window 2024-07..12 has been seen for the bigtrade fire layers via the old table and cannot be a clean check for them; logged in layer_lab/TRIALS.md.
