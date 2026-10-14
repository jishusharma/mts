# LC1 levels hold — DEV result

**KEEP: prior_day_high, prior_day_low, prior_day_poc, naked_poc, 4h_fractal_low, 4h_fractal_high, round_1000, prior_week_high. DROP: prior_day_vah, prior_day_val, daily_open, prior_week_low. L2 reached: 83.8%.** Each KEEP family has a positive lower 95% day-bootstrap CI bound. L2 candidates are restricted to KEEP families.

Implemented the causal level set and touch/random-line/pair measurement in `MyTradingSys/research/levels_confluence_2026-10-14/levels.py` and `levels_hold.py`; added synthetic coverage in `test_levels.py`. The full family table, pair count, and reproduction command are in [levels_hold.md](../../levels_confluence_2026-10-14/levels_hold.md).

## Evidence

- Data: `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-YYYY-MM.csv`; loader `MyTradingSys/backtest/bt/bt_data.py:10-48`. Loaded 188,640 bars, 2024-11-21 00:00 through 2025-03-31 23:59 UTC; measured DEV 2024-12-01 through 2025-03-31.
- Formula source: `MyTradingSys/backtest/layers/FORMULAS.md:414-428` (10 USD-bin profile and 70% value area).
- Verification: `python -m pytest MyTradingSys/research/levels_confluence_2026-10-14/test_levels.py -q` — **3 passed** (pytest cache warning only).
- Analysis: 12 families, 1,504 first-touch events; 1,279 L1→KEEP-family-L2 pairs, of which 1,072 reached L2 (83.8%); 917/1,072 (85.5%) revisited L1 after reaching L2. All detail is tabulated in the linked study report.

## Findings

| Severity | File:line | Finding | Evidence |
|---|---|---|---|
| LOW | `levels_hold.py` (`analyze`) | L2 results are descriptive: the KEEP label is based on the pooled DEV touch sample and is not validation evidence. | The study is restricted to DEV; validation and holdout were not read. |

No follow-up card created.
