MATCH: 64 | DIFF: 0 | NOT_IN_DATA: 0

# Independent Gemini Blind Read: `btc_cycles_2026-11/cycles.py` vs `cycles.md` and `cycles.csv` (`gemini-blind-read-cycles-py-1108`)

- **Card**: `gemini-blind-read-cycles-py-1108`
- **Reader / Provenance**: Gemini (`gemini-3.8-flash-low` worker on throwaway worktree branch `gemini-q/gemini-blind-read-cycles-py-1108`).
- **Scope In Read**:
  - `MyTradingSys/research/btc_cycles_2026-11/cycles.py` (lines 1-117, SOURCED/OURS)
  - `MyTradingSys/research/btc_cycles_2026-11/cycles.md` (lines 1-16, SOURCED)
  - `MyTradingSys/research/btc_cycles_2026-11/cycles.csv` (lines 1-6, SOURCED)
  - `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv` (lines 1-5926, SOURCED)
- **Scope Out Respected**: No source files edited; no live-tree edit, no push or sync ship, no `.secrets` or `.env` read.

---

## 1. Methodology & Algorithm Verification

1. **Protocol & Halvings Definition**:
   - Protocol block height halvings: Block 210,000 (`2012-11-28`), Block 420,000 (`2016-07-09`), Block 630,000 (`2020-05-11`), Block 840,000 (`2024-04-20`) (SOURCED `cycles.py:18`, Bitcoin consensus history).
   - Estimated next halving: Block 1,050,000 at ~10 min/block from Block 840,000 (`2024-04-20`) gives `2028-04-15` (OURS estimate, `cycles.py:20`).
2. **Cycle Boundaries & Extrema Logic (`cycles.py:52-74`)**:
   - `Cycle 0`: Pre-halving bubble. Peak defined as max high in `2011-01-01 .. 2011-12-31` (`2011-06-11` at `33.8`); bottom defined as min low from peak date to `2012-06-30` (`2011-11-22` at `2.3`).
   - `Cycles 1..4`: For each halving date `h`, peak defined as max high in `h .. min(h + 730 days, today)`; bottom defined as min low in `peak_date .. min(peak_date + 500 days, today)`.
   - Metrics computed:
     - `halving_to_peak_d = (peak_date - halving).days`
     - `peak_to_bottom_d = (bottom_date - peak_date).days`
     - `drawdown_pct = round((bottom / peak - 1) * 100, 1)`
     - `prev_bottom_to_peak_d = (peak_date - prev_bottom_date).days`
     - `prev_bottom_to_peak_x = round(peak / prev_bottom, 1)`
     - `bottom_to_bottom_d = (bottom_date - prev_bottom_date).days`
     - `bottom_is_final = bottom_date < today - 60 days`
     - `bottom_to_next_halving_d = (next_halving - bottom_date).days`
3. **Independent Re-computation**:
   - Every cell of `cycles.csv` and `cycles.md` was independently recomputed from raw daily rows in `btc_daily.csv` (5,925 trading days from `2010-08-18` to `2026-11-06`).
   - All 5 cycles and all summary calculations reproduce bit-for-bit with zero discrepancies.

---

## 2. Table Item Audit (cycles.md vs Independent Derivation)

### Table 1: BTC Cycles Main Table (`cycles.md:3-9`)

| # | Item / Cell | `cycles.md` Line | Stated Value | Recomputed from `btc_daily.csv` | Verdict |
|---:|---|---|---|---|---|
| 1 | Table header date | `cycles.md:1` | `2026-11-06` | `2026-11-06` (`max(btc_daily.csv['date'])`) | MATCH |
| 2 | Table header close | `cycles.md:1` | `75,772` | `75,771.76` -> `75,772` (`btc_daily.csv:5926`) | MATCH |
| 3 | Cycle 0 halving | `cycles.md:5` | `""` (empty) | `""` (Cycle 0 is pre-halving) | MATCH |
| 4 | Cycle 0 peak date | `cycles.md:5` | `2011-06-11` | `2011-06-11` (high `33.8`) | MATCH |
| 5 | Cycle 0 peak | `cycles.md:5` | `34` | `33.8` -> `34` | MATCH |
| 6 | Cycle 0 halving to peak (d) | `cycles.md:5` | `""` (empty) | `""` | MATCH |
| 7 | Cycle 0 bottom date | `cycles.md:5` | `2011-11-22` | `2011-11-22` (low `2.3`) | MATCH |
| 8 | Cycle 0 bottom | `cycles.md:5` | `2` | `2.3` -> `2` | MATCH |
| 9 | Cycle 0 peak to bottom (d) | `cycles.md:5` | `164` | `164` (`(2011-11-22 - 2011-06-11).days`) | MATCH |
| 10 | Cycle 0 drawdown % | `cycles.md:5` | `-93.2` | `-93.2` (`round((2.3 / 33.8 - 1) * 100, 1)`) | MATCH |
| 11 | Cycle 0 prev bottom to peak | `cycles.md:5` | ` d, x` | `""` | MATCH |
| 12 | Cycle 1 halving | `cycles.md:6` | `2012-11-28` | `2012-11-28` (Block 210,000) | MATCH |
| 13 | Cycle 1 peak date | `cycles.md:6` | `2013-12-05` | `2013-12-05` (high `1136.9`) | MATCH |
| 14 | Cycle 1 peak | `cycles.md:6` | `1,137` | `1136.9` -> `1,137` | MATCH |
| 15 | Cycle 1 halving to peak (d) | `cycles.md:6` | `372` | `372` (`(2013-12-05 - 2012-11-28).days`) | MATCH |
| 16 | Cycle 1 bottom date | `cycles.md:6` | `2015-01-15` | `2015-01-15` (low `172.0`) | MATCH |
| 17 | Cycle 1 bottom | `cycles.md:6` | `172` | `172.0` -> `172` | MATCH |
| 18 | Cycle 1 peak to bottom (d) | `cycles.md:6` | `406` | `406` (`(2015-01-15 - 2013-12-05).days`) | MATCH |
| 19 | Cycle 1 drawdown % | `cycles.md:6` | `-84.9` | `-84.9` (`round((172.0 / 1136.9 - 1) * 100, 1)`) | MATCH |
| 20 | Cycle 1 prev bottom to peak (d) | `cycles.md:6` | `744 d` | `744` (`(2013-12-05 - 2011-11-22).days`) | MATCH |
| 21 | Cycle 1 prev bottom to peak (x) | `cycles.md:6` | `494.3x` | `494.3` (`round(1136.9 / 2.3, 1)`) | MATCH |
| 22 | Cycle 2 halving | `cycles.md:7` | `2016-07-09` | `2016-07-09` (Block 420,000) | MATCH |
| 23 | Cycle 2 peak date | `cycles.md:7` | `2017-12-17` | `2017-12-17` (high `19798.68`) | MATCH |
| 24 | Cycle 2 peak | `cycles.md:7` | `19,799` | `19798.68` -> `19,799` | MATCH |
| 25 | Cycle 2 halving to peak (d) | `cycles.md:7` | `526` | `526` (`(2017-12-17 - 2016-07-09).days`) | MATCH |
| 26 | Cycle 2 bottom date | `cycles.md:7` | `2018-12-15` | `2018-12-15` (low `3156.26`) | MATCH |
| 27 | Cycle 2 bottom | `cycles.md:7` | `3,156` | `3156.26` -> `3,156` | MATCH |
| 28 | Cycle 2 peak to bottom (d) | `cycles.md:7` | `363` | `363` (`(2018-12-15 - 2017-12-17).days`) | MATCH |
| 29 | Cycle 2 drawdown % | `cycles.md:7` | `-84.1` | `-84.1` (`round((3156.26 / 19798.68 - 1) * 100, 1)`) | MATCH |
| 30 | Cycle 2 prev bottom to peak (d) | `cycles.md:7` | `1067 d` | `1067` (`(2017-12-17 - 2015-01-15).days`) | MATCH |
| 31 | Cycle 2 prev bottom to peak (x) | `cycles.md:7` | `115.1x` | `115.1` (`round(19798.68 / 172.0, 1)`) | MATCH |
| 32 | Cycle 3 halving | `cycles.md:8` | `2020-05-11` | `2020-05-11` (Block 630,000) | MATCH |
| 33 | Cycle 3 peak date | `cycles.md:8` | `2021-11-10` | `2021-11-10` (high `69000.0`) | MATCH |
| 34 | Cycle 3 peak | `cycles.md:8` | `69,000` | `69000.0` -> `69,000` | MATCH |
| 35 | Cycle 3 halving to peak (d) | `cycles.md:8` | `548` | `548` (`(2021-11-10 - 2020-05-11).days`) | MATCH |
| 36 | Cycle 3 bottom date | `cycles.md:8` | `2022-11-21` | `2022-11-21` (low `15476.0`) | MATCH |
| 37 | Cycle 3 bottom | `cycles.md:8` | `15,476` | `15476.0` -> `15,476` | MATCH |
| 38 | Cycle 3 peak to bottom (d) | `cycles.md:8` | `376` | `376` (`(2022-11-21 - 2021-11-10).days`) | MATCH |
| 39 | Cycle 3 drawdown % | `cycles.md:8` | `-77.6` | `-77.6` (`round((15476.0 / 69000.0 - 1) * 100, 1)`) | MATCH |
| 40 | Cycle 3 prev bottom to peak (d) | `cycles.md:8` | `1061 d` | `1061` (`(2021-11-10 - 2018-12-15).days`) | MATCH |
| 41 | Cycle 3 prev bottom to peak (x) | `cycles.md:8` | `21.9x` | `21.9` (`round(69000.0 / 3156.26, 1)`) | MATCH |
| 42 | Cycle 4 halving | `cycles.md:9` | `2024-04-20` | `2024-04-20` (Block 840,000) | MATCH |
| 43 | Cycle 4 peak date | `cycles.md:9` | `2025-10-06` | `2025-10-06` (high `126199.63`) | MATCH |
| 44 | Cycle 4 peak | `cycles.md:9` | `126,200` | `126199.63` -> `126,200` | MATCH |
| 45 | Cycle 4 halving to peak (d) | `cycles.md:9` | `534` | `534` (`(2025-10-06 - 2024-04-20).days`) | MATCH |
| 46 | Cycle 4 bottom date | `cycles.md:9` | `2026-07-01` | `2026-07-01` (low `57800.19`) | MATCH |
| 47 | Cycle 4 bottom | `cycles.md:9` | `57,800` | `57800.19` -> `57,800` | MATCH |
| 48 | Cycle 4 peak to bottom (d) | `cycles.md:9` | `268` | `268` (`(2026-07-01 - 2025-10-06).days`) | MATCH |
| 49 | Cycle 4 drawdown % | `cycles.md:9` | `-54.2` | `-54.2` (`round((57800.19 / 126199.63 - 1) * 100, 1)`) | MATCH |
| 50 | Cycle 4 prev bottom to peak (d) | `cycles.md:9` | `1050 d` | `1050` (`(2025-10-06 - 2022-11-21).days`) | MATCH |
| 51 | Cycle 4 prev bottom to peak (x) | `cycles.md:9` | `8.2x` | `8.2` (`round(126199.63 / 15476.0, 1)`) | MATCH |

### Section 2: Cycle 4 Now Analysis Statements (`cycles.md:11-16`)

| # | Statement / Metric | `cycles.md` Line | Stated Value | Recomputed from `btc_daily.csv` | Verdict |
|---:|---|---|---|---|---|
| 52 | Cycle 4 peak & level | `cycles.md:12` | `peak 2025-10-06 at 126,200` | `2025-10-06` at `126,200` | MATCH |
| 53 | Days since cycle 4 peak | `cycles.md:12` | `396 days since the peak` | `396` (`(2026-11-06 - 2025-10-06).days`) | MATCH |
| 54 | Distance of latest close from peak | `cycles.md:12` | `close 75,772 = -40.0 %` | `round((75771.76 / 126199.63 - 1) * 100, 1) = -40.0%` | MATCH |
| 55 | Lowest low since peak | `cycles.md:12` | `lowest since the peak 57,800 on 2026-07-01 (-54.2 %)` | `57,800` on `2026-07-01` (`-54.2%`) | MATCH |
| 56 | Cycles 1-3 peak to bottom array | `cycles.md:13` | `[406, 363, 376] days` | `[406, 363, 376]` | MATCH |
| 57 | Clock-implied window start | `cycles.md:13` | `2026-10-04` | `2025-10-06 + 363 days = 2026-10-04` | MATCH |
| 58 | Clock-implied window end | `cycles.md:13` | `2026-11-16` | `2025-10-06 + 406 days = 2026-11-16` | MATCH |
| 59 | Bottom to next halving (cycles 0-3) | `cycles.md:14` | `[372, 541, 513, 516] days` | `[372, 541, 513, 516]` | MATCH |
| 60 | Days from 2026-07-01 to est halving | `cycles.md:14` | `654 days` | `(2028-04-15 - 2026-07-01).days = 654` | MATCH |
| 61 | Cycles 1-3 drawdowns array | `cycles.md:15` | `[-84.9, -84.1, -77.6] %` | `[-84.9, -84.1, -77.6]` | MATCH |
| 62 | Depth equivalent 1 (-84.9%) | `cycles.md:15` | `19,056` | `round(126199.63 * (1 - 0.849)) = 19,056` | MATCH |
| 63 | Depth equivalent 2 (-84.1%) | `cycles.md:15` | `20,066` | `round(126199.63 * (1 - 0.841)) = 20,066` | MATCH |
| 64 | Depth equivalent 3 (-77.6%) | `cycles.md:15` | `28,269` | `round(126199.63 * (1 - 0.776)) = 28,269` | MATCH |

---

## 3. Findings & Summary

- **Reproducibility**: `cycles.py` deterministically produces `cycles.md` and `cycles.csv` from `btc_daily.csv`. Zero rows or metrics were hand-edited.
- **Data Integrity**: All historical halving dates, peak dates, bottom dates, durations, multiples, and projections in `cycles.md` directly follow the market data in `btc_daily.csv` without exception.
- **Totals**: 64 items checked; 64 MATCH, 0 DIFF, 0 NOT_IN_DATA.
