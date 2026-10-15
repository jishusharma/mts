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

**Claude spot-check: MATCH** (2026-10-15, Claude session lab-unstall). Recomputed `prior_day_high` and `prior_day_low` from raw public Binance USD-M BTCUSDT 1m klines (data.binance.vision futures/um monthly files 2024-11..2025-03, 217,440 bars), written from the levels_hold.md method text without importing the lab code (level = prior UTC day high/low, first bar of the day whose low-high range contains it, width = max(0.40% of 00:00 open, 0.10% of level), BREAK first/same-bar, HOLD, else NEITHER). `prior_day_high`: 57 touches, 32 HOLD (56.1%), 24 BREAK, 1 NEITHER = the report's 57 and 56.1%. `prior_day_low`: 60 touches, 38 HOLD (63.3%) = the report's 60 and 63.3%. Not rechecked: the random-line controls, the bootstrap CIs, the other ten families, the L1-L2 pairs.

No follow-up card created.
