# MATCH: 82, DIFF: 0, NOT_IN_DATA: 328

## Independent GPT Re-derivation: Wicks Census 15m (`CENSUS_15m_2026-10-03_11-07.md`)

- **Card**: `gpt-rederive-wicks-census-1107`
- **Audited source file**: `MyTradingSys/research/wicks_2026-11/CENSUS_15m_2026-10-03_11-07.md` (110 lines, 14 breakdown tables, 49 data rows, 2 event callouts)
- **Folder inventory**: `MyTradingSys/research/wicks_2026-11/` (`CENSUS_15m_2026-10-03_11-07.md`, `CENSUS_5m_2026-10-03_11-07.md`, `WICKS_NOTE_2026-11-07.md`, `wick_census.py`)
- **Formula reference**: `MyTradingSys/backtest/layers/FORMULAS.md`
- **Audit date**: 2026-11-07 UTC

## Executive Summary

1. **Data Availability Assessment**:
   - `wick_census.py:13` specifies loading 5 weeks of 15m klines from `btc_15m_5w.json` (`rows = json.load(open('btc_15m_5w.json'))`).
   - No JSON kline files (`btc_15m_5w.json`) or raw trade/event CSV files were checked into `MyTradingSys/research/wicks_2026-11/` or elsewhere in the repo.
   - Consequently, all raw market-data-dependent figures (total bar count `3411`, empirical event counts `n`, empirical `sweeps`, `target first` hit counts, `stop first` hit counts, `open` counts, `median wick %`, `median rel vol`, and individual Friday bar quotes) cannot be re-derived from permitted repository data and are classified as **NOT_IN_DATA** (total: 328 numbers).
2. **Formula Specification Assessment**:
   - `MyTradingSys/backtest/layers/FORMULAS.md` currently covers RSI, SMMA/RMA, SMA, Bollinger Bands, VP return-to-value, and engulfing patterns, but does not define the wick census rules.
   - Per `WICKS_NOTE_2026-11-07.md:91` (Plan item W1), formal definition of wicks in FORMULAS.md is future scheduled work.
3. **Internal Mathematical and Arithmetic Verification**:
   - **Target-first percentages**: All 49 table rows report a target-first percentage `round(target_first / n * 100)%`. Every single row's percentage independently reproduces exactly (**MATCH**, 49/49).
   - **Row sum conservation**: In all 49 rows, the conservation identity `target_first + stop_first + open == n` holds identically with zero discrepancies (**0 DIFF**).
   - **V-sweep identity**: In all 17 multi-bar V-sweep rows, `sweeps == n` holds identically by definition (**MATCH**, 17/17).
   - **Sweep vs Not partition identity**: In all 4 sweep partition rows, `sweeps == 0` for `False` and `sweeps == n` for `True` (**MATCH**, 4/4).
   - **Headline and marginal totals**: Headline sums `66 lower + 66 upper = 132 single-bar wicks` (**MATCH**) and `62 lower V-sweeps + 69 upper V-sweeps = 131 multi-bar V-sweeps` (**MATCH**) reproduce exactly from the underlying table partition sums.
   - **Parameters**: Timeframe `15m` (15), holding period `H=16`, and target `R=1` match the stated study specification (**MATCH**, 3/3).
   - Total **MATCH**: 82 numbers. Total **DIFF**: 0 numbers. Total **NOT_IN_DATA**: 328 numbers.

## Table Partition Marginal Sums Verification

| Category | Partition Dimension | Sum of `n` | Sum of `sweeps` | Sum of `target first` | Sum of `stop first` | Sum of `open` | Verification Status |
|---|---|---|---|---|---|---|---|
| LOW single-bar wicks | Week (6 rows) | OURS (66) | OURS (29) | OURS (25) | OURS (33) | OURS (8) | MATCH (Marginal sum equals headline 66) |
| LOW single-bar wicks | Session (4 rows) | OURS (66) | OURS (29) | OURS (25) | OURS (33) | OURS (8) | MATCH (Matches week partition exactly) |
| LOW single-bar wicks | Knife context (1 row) | OURS (66) | OURS (29) | OURS (25) | OURS (33) | OURS (8) | MATCH (Matches week partition exactly) |
| LOW single-bar wicks | Sweep vs not (2 rows) | OURS (66) | OURS (29) | OURS (25) | OURS (33) | OURS (8) | MATCH (Matches week partition exactly) |
| LOW V-sweeps (multi-bar) | Week (5 rows) | OURS (62) | OURS (62) | OURS (31) | OURS (24) | OURS (7) | MATCH (Marginal sum equals 62) |
| LOW V-sweeps (multi-bar) | Knife context (2 rows) | OURS (62) | OURS (62) | OURS (31) | OURS (24) | OURS (7) | MATCH (Matches week partition exactly) |
| LOW V-sweeps (multi-bar) | Session (4 rows) | OURS (62) | OURS (62) | OURS (31) | OURS (24) | OURS (7) | MATCH (Matches week partition exactly) |
| UP single-bar wicks | Week (6 rows) | OURS (66) | OURS (24) | OURS (31) | OURS (33) | OURS (2) | MATCH (Marginal sum equals headline 66) |
| UP single-bar wicks | Session (4 rows) | OURS (66) | OURS (24) | OURS (31) | OURS (33) | OURS (2) | MATCH (Matches week partition exactly) |
| UP single-bar wicks | Knife context (2 rows) | OURS (66) | OURS (24) | OURS (31) | OURS (33) | OURS (2) | MATCH (Matches week partition exactly) |
| UP single-bar wicks | Sweep vs not (2 rows) | OURS (66) | OURS (24) | OURS (31) | OURS (33) | OURS (2) | MATCH (Matches week partition exactly) |
| UP V-sweeps (multi-bar) | Week (6 rows) | OURS (69) | OURS (69) | OURS (29) | OURS (35) | OURS (5) | MATCH (Marginal sum equals 69) |
| UP V-sweeps (multi-bar) | Knife context (1 row) | OURS (69) | OURS (69) | OURS (29) | OURS (35) | OURS (5) | MATCH (Matches week partition exactly) |
| UP V-sweeps (multi-bar) | Session (4 rows) | OURS (69) | OURS (69) | OURS (29) | OURS (35) | OURS (5) | MATCH (Matches week partition exactly) |

## Complete Numeric Inventory and Re-derivation Table

| Item ID | Line:Col | Metric / Entity Description | Quoted Source Value | Recomputed Value | Status | Derivation Notes & Evidence |
|---|---|---|---|---|---|---|
| 1 | 1:1 | Timeframe (minutes) | SOURCED ("15m", CENSUS_15m_2026-10-03_11-07.md:1) | OURS (15) | **MATCH** | Timeframe parameter in document header |
| 2 | 1:2 | Total 15m bars count | SOURCED ("3411 bars", CENSUS_15m_2026-10-03_11-07.md:1) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Raw kline JSON btc_15m_5w.json absent from folder/repo |
| 3 | 1:3 | Total single-bar long wicks | SOURCED ("132 single-bar long wicks", CENSUS_15m_2026-10-03_11-07.md:1) | OURS (132) | **MATCH** | Arithmetic identity: 66 lower + 66 upper = 132 |
| 4 | 1:4 | Lower single-bar wicks count | SOURCED ("66 lower", CENSUS_15m_2026-10-03_11-07.md:1) | OURS (66) | **MATCH** | Sum of lower week counts: 2+17+16+14+9+8 = 66 |
| 5 | 1:5 | Upper single-bar wicks count | SOURCED ("66 upper", CENSUS_15m_2026-10-03_11-07.md:1) | OURS (66) | **MATCH** | Sum of upper week counts: 7+10+14+12+12+11 = 66 |
| 6 | 1:6 | Total multi-bar V-sweeps | SOURCED ("131 multi-bar V-sweeps", CENSUS_15m_2026-10-03_11-07.md:1) | OURS (131) | **MATCH** | Arithmetic identity: 62 lower V-sweeps + 69 upper V-sweeps = 131 |
| 7 | 1:7 | Holding period H (bars) | SOURCED ("H=16 bars", CENSUS_15m_2026-10-03_11-07.md:1) | OURS (16) | **MATCH** | Holding horizon parameter H=16 |
| 8 | 1:8 | Target R multiple | SOURCED ("target R=1", CENSUS_15m_2026-10-03_11-07.md:1) | OURS (1) | **MATCH** | Risk-reward parameter R=1 |
| 9 | 6:1 | LOW single-bar wicks by week [2026-09-28] n | SOURCED ("2", CENSUS_15m_2026-10-03_11-07.md:6) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 1+1+0=2; raw klines absent |
| 10 | 6:2 | LOW single-bar wicks by week [2026-09-28] sweeps | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:6) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 11 | 6:3 | LOW single-bar wicks by week [2026-09-28] target first count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:6) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 12 | 6:4 | LOW single-bar wicks by week [2026-09-28] target first % | SOURCED ("50%", CENSUS_15m_2026-10-03_11-07.md:6) | OURS (50%) | **MATCH** | Arithmetic formula round(1/2*100)% = 50% |
| 13 | 6:5 | LOW single-bar wicks by week [2026-09-28] stop first count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:6) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 14 | 6:6 | LOW single-bar wicks by week [2026-09-28] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:6) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 15 | 6:7 | LOW single-bar wicks by week [2026-09-28] median wick % | SOURCED ("0.12", CENSUS_15m_2026-10-03_11-07.md:6) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 16 | 6:8 | LOW single-bar wicks by week [2026-09-28] median rel vol | SOURCED ("2.8", CENSUS_15m_2026-10-03_11-07.md:6) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 17 | 7:1 | LOW single-bar wicks by week [2026-10-05] n | SOURCED ("17", CENSUS_15m_2026-10-03_11-07.md:7) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 4+11+2=17; raw klines absent |
| 18 | 7:2 | LOW single-bar wicks by week [2026-10-05] sweeps | SOURCED ("10", CENSUS_15m_2026-10-03_11-07.md:7) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 19 | 7:3 | LOW single-bar wicks by week [2026-10-05] target first count | SOURCED ("4", CENSUS_15m_2026-10-03_11-07.md:7) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 20 | 7:4 | LOW single-bar wicks by week [2026-10-05] target first % | SOURCED ("24%", CENSUS_15m_2026-10-03_11-07.md:7) | OURS (24%) | **MATCH** | Arithmetic formula round(4/17*100)% = 24% |
| 21 | 7:5 | LOW single-bar wicks by week [2026-10-05] stop first count | SOURCED ("11", CENSUS_15m_2026-10-03_11-07.md:7) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 22 | 7:6 | LOW single-bar wicks by week [2026-10-05] open count | SOURCED ("2", CENSUS_15m_2026-10-03_11-07.md:7) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 23 | 7:7 | LOW single-bar wicks by week [2026-10-05] median wick % | SOURCED ("0.23", CENSUS_15m_2026-10-03_11-07.md:7) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 24 | 7:8 | LOW single-bar wicks by week [2026-10-05] median rel vol | SOURCED ("3.3", CENSUS_15m_2026-10-03_11-07.md:7) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 25 | 8:1 | LOW single-bar wicks by week [2026-10-12] n | SOURCED ("16", CENSUS_15m_2026-10-03_11-07.md:8) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 9+7+0=16; raw klines absent |
| 26 | 8:2 | LOW single-bar wicks by week [2026-10-12] sweeps | SOURCED ("9", CENSUS_15m_2026-10-03_11-07.md:8) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 27 | 8:3 | LOW single-bar wicks by week [2026-10-12] target first count | SOURCED ("9", CENSUS_15m_2026-10-03_11-07.md:8) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 28 | 8:4 | LOW single-bar wicks by week [2026-10-12] target first % | SOURCED ("56%", CENSUS_15m_2026-10-03_11-07.md:8) | OURS (56%) | **MATCH** | Arithmetic formula round(9/16*100)% = 56% |
| 29 | 8:5 | LOW single-bar wicks by week [2026-10-12] stop first count | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:8) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 30 | 8:6 | LOW single-bar wicks by week [2026-10-12] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:8) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 31 | 8:7 | LOW single-bar wicks by week [2026-10-12] median wick % | SOURCED ("0.23", CENSUS_15m_2026-10-03_11-07.md:8) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 32 | 8:8 | LOW single-bar wicks by week [2026-10-12] median rel vol | SOURCED ("3.8", CENSUS_15m_2026-10-03_11-07.md:8) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 33 | 9:1 | LOW single-bar wicks by week [2026-10-19] n | SOURCED ("14", CENSUS_15m_2026-10-03_11-07.md:9) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 6+6+2=14; raw klines absent |
| 34 | 9:2 | LOW single-bar wicks by week [2026-10-19] sweeps | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:9) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 35 | 9:3 | LOW single-bar wicks by week [2026-10-19] target first count | SOURCED ("6", CENSUS_15m_2026-10-03_11-07.md:9) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 36 | 9:4 | LOW single-bar wicks by week [2026-10-19] target first % | SOURCED ("43%", CENSUS_15m_2026-10-03_11-07.md:9) | OURS (43%) | **MATCH** | Arithmetic formula round(6/14*100)% = 43% |
| 37 | 9:5 | LOW single-bar wicks by week [2026-10-19] stop first count | SOURCED ("6", CENSUS_15m_2026-10-03_11-07.md:9) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 38 | 9:6 | LOW single-bar wicks by week [2026-10-19] open count | SOURCED ("2", CENSUS_15m_2026-10-03_11-07.md:9) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 39 | 9:7 | LOW single-bar wicks by week [2026-10-19] median wick % | SOURCED ("0.31", CENSUS_15m_2026-10-03_11-07.md:9) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 40 | 9:8 | LOW single-bar wicks by week [2026-10-19] median rel vol | SOURCED ("5.7", CENSUS_15m_2026-10-03_11-07.md:9) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 41 | 10:1 | LOW single-bar wicks by week [2026-10-26] n | SOURCED ("9", CENSUS_15m_2026-10-03_11-07.md:10) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 4+3+2=9; raw klines absent |
| 42 | 10:2 | LOW single-bar wicks by week [2026-10-26] sweeps | SOURCED ("4", CENSUS_15m_2026-10-03_11-07.md:10) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 43 | 10:3 | LOW single-bar wicks by week [2026-10-26] target first count | SOURCED ("4", CENSUS_15m_2026-10-03_11-07.md:10) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 44 | 10:4 | LOW single-bar wicks by week [2026-10-26] target first % | SOURCED ("44%", CENSUS_15m_2026-10-03_11-07.md:10) | OURS (44%) | **MATCH** | Arithmetic formula round(4/9*100)% = 44% |
| 45 | 10:5 | LOW single-bar wicks by week [2026-10-26] stop first count | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:10) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 46 | 10:6 | LOW single-bar wicks by week [2026-10-26] open count | SOURCED ("2", CENSUS_15m_2026-10-03_11-07.md:10) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 47 | 10:7 | LOW single-bar wicks by week [2026-10-26] median wick % | SOURCED ("0.35", CENSUS_15m_2026-10-03_11-07.md:10) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 48 | 10:8 | LOW single-bar wicks by week [2026-10-26] median rel vol | SOURCED ("3.4", CENSUS_15m_2026-10-03_11-07.md:10) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 49 | 11:1 | LOW single-bar wicks by week [2026-11-02] n | SOURCED ("8", CENSUS_15m_2026-10-03_11-07.md:11) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 1+5+2=8; raw klines absent |
| 50 | 11:2 | LOW single-bar wicks by week [2026-11-02] sweeps | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:11) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 51 | 11:3 | LOW single-bar wicks by week [2026-11-02] target first count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:11) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 52 | 11:4 | LOW single-bar wicks by week [2026-11-02] target first % | SOURCED ("12%", CENSUS_15m_2026-10-03_11-07.md:11) | OURS (12%) | **MATCH** | Arithmetic formula round(1/8*100)% = 12% |
| 53 | 11:5 | LOW single-bar wicks by week [2026-11-02] stop first count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:11) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 54 | 11:6 | LOW single-bar wicks by week [2026-11-02] open count | SOURCED ("2", CENSUS_15m_2026-10-03_11-07.md:11) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 55 | 11:7 | LOW single-bar wicks by week [2026-11-02] median wick % | SOURCED ("0.28", CENSUS_15m_2026-10-03_11-07.md:11) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 56 | 11:8 | LOW single-bar wicks by week [2026-11-02] median rel vol | SOURCED ("2.9", CENSUS_15m_2026-10-03_11-07.md:11) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 57 | 16:1 | LOW single-bar wicks by session [ASIA] n | SOURCED ("18", CENSUS_15m_2026-10-03_11-07.md:16) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 7+10+1=18; raw klines absent |
| 58 | 16:2 | LOW single-bar wicks by session [ASIA] sweeps | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:16) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 59 | 16:3 | LOW single-bar wicks by session [ASIA] target first count | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:16) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 60 | 16:4 | LOW single-bar wicks by session [ASIA] target first % | SOURCED ("39%", CENSUS_15m_2026-10-03_11-07.md:16) | OURS (39%) | **MATCH** | Arithmetic formula round(7/18*100)% = 39% |
| 61 | 16:5 | LOW single-bar wicks by session [ASIA] stop first count | SOURCED ("10", CENSUS_15m_2026-10-03_11-07.md:16) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 62 | 16:6 | LOW single-bar wicks by session [ASIA] open count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:16) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 63 | 16:7 | LOW single-bar wicks by session [ASIA] median wick % | SOURCED ("0.24", CENSUS_15m_2026-10-03_11-07.md:16) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 64 | 16:8 | LOW single-bar wicks by session [ASIA] median rel vol | SOURCED ("3.4", CENSUS_15m_2026-10-03_11-07.md:16) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 65 | 17:1 | LOW single-bar wicks by session [EU] n | SOURCED ("10", CENSUS_15m_2026-10-03_11-07.md:17) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 4+6+0=10; raw klines absent |
| 66 | 17:2 | LOW single-bar wicks by session [EU] sweeps | SOURCED ("6", CENSUS_15m_2026-10-03_11-07.md:17) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 67 | 17:3 | LOW single-bar wicks by session [EU] target first count | SOURCED ("4", CENSUS_15m_2026-10-03_11-07.md:17) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 68 | 17:4 | LOW single-bar wicks by session [EU] target first % | SOURCED ("40%", CENSUS_15m_2026-10-03_11-07.md:17) | OURS (40%) | **MATCH** | Arithmetic formula round(4/10*100)% = 40% |
| 69 | 17:5 | LOW single-bar wicks by session [EU] stop first count | SOURCED ("6", CENSUS_15m_2026-10-03_11-07.md:17) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 70 | 17:6 | LOW single-bar wicks by session [EU] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:17) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 71 | 17:7 | LOW single-bar wicks by session [EU] median wick % | SOURCED ("0.25", CENSUS_15m_2026-10-03_11-07.md:17) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 72 | 17:8 | LOW single-bar wicks by session [EU] median rel vol | SOURCED ("4.0", CENSUS_15m_2026-10-03_11-07.md:17) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 73 | 18:1 | LOW single-bar wicks by session [LATE] n | SOURCED ("9", CENSUS_15m_2026-10-03_11-07.md:18) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 3+5+1=9; raw klines absent |
| 74 | 18:2 | LOW single-bar wicks by session [LATE] sweeps | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:18) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 75 | 18:3 | LOW single-bar wicks by session [LATE] target first count | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:18) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 76 | 18:4 | LOW single-bar wicks by session [LATE] target first % | SOURCED ("33%", CENSUS_15m_2026-10-03_11-07.md:18) | OURS (33%) | **MATCH** | Arithmetic formula round(3/9*100)% = 33% |
| 77 | 18:5 | LOW single-bar wicks by session [LATE] stop first count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:18) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 78 | 18:6 | LOW single-bar wicks by session [LATE] open count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:18) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 79 | 18:7 | LOW single-bar wicks by session [LATE] median wick % | SOURCED ("0.18", CENSUS_15m_2026-10-03_11-07.md:18) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 80 | 18:8 | LOW single-bar wicks by session [LATE] median rel vol | SOURCED ("2.5", CENSUS_15m_2026-10-03_11-07.md:18) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 81 | 19:1 | LOW single-bar wicks by session [US] n | SOURCED ("29", CENSUS_15m_2026-10-03_11-07.md:19) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 11+12+6=29; raw klines absent |
| 82 | 19:2 | LOW single-bar wicks by session [US] sweeps | SOURCED ("13", CENSUS_15m_2026-10-03_11-07.md:19) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 83 | 19:3 | LOW single-bar wicks by session [US] target first count | SOURCED ("11", CENSUS_15m_2026-10-03_11-07.md:19) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 84 | 19:4 | LOW single-bar wicks by session [US] target first % | SOURCED ("38%", CENSUS_15m_2026-10-03_11-07.md:19) | OURS (38%) | **MATCH** | Arithmetic formula round(11/29*100)% = 38% |
| 85 | 19:5 | LOW single-bar wicks by session [US] stop first count | SOURCED ("12", CENSUS_15m_2026-10-03_11-07.md:19) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 86 | 19:6 | LOW single-bar wicks by session [US] open count | SOURCED ("6", CENSUS_15m_2026-10-03_11-07.md:19) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 87 | 19:7 | LOW single-bar wicks by session [US] median wick % | SOURCED ("0.28", CENSUS_15m_2026-10-03_11-07.md:19) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 88 | 19:8 | LOW single-bar wicks by session [US] median rel vol | SOURCED ("3.5", CENSUS_15m_2026-10-03_11-07.md:19) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 89 | 24:1 | LOW single-bar wicks: knife context [False] n | SOURCED ("66", CENSUS_15m_2026-10-03_11-07.md:24) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 25+33+8=66; raw klines absent |
| 90 | 24:2 | LOW single-bar wicks: knife context [False] sweeps | SOURCED ("29", CENSUS_15m_2026-10-03_11-07.md:24) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 91 | 24:3 | LOW single-bar wicks: knife context [False] target first count | SOURCED ("25", CENSUS_15m_2026-10-03_11-07.md:24) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 92 | 24:4 | LOW single-bar wicks: knife context [False] target first % | SOURCED ("38%", CENSUS_15m_2026-10-03_11-07.md:24) | OURS (38%) | **MATCH** | Arithmetic formula round(25/66*100)% = 38% |
| 93 | 24:5 | LOW single-bar wicks: knife context [False] stop first count | SOURCED ("33", CENSUS_15m_2026-10-03_11-07.md:24) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 94 | 24:6 | LOW single-bar wicks: knife context [False] open count | SOURCED ("8", CENSUS_15m_2026-10-03_11-07.md:24) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 95 | 24:7 | LOW single-bar wicks: knife context [False] median wick % | SOURCED ("0.27", CENSUS_15m_2026-10-03_11-07.md:24) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 96 | 24:8 | LOW single-bar wicks: knife context [False] median rel vol | SOURCED ("3.4", CENSUS_15m_2026-10-03_11-07.md:24) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 97 | 29:1 | LOW single-bar wicks: sweep vs not [False] n | SOURCED ("37", CENSUS_15m_2026-10-03_11-07.md:29) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 12+22+3=37; raw klines absent |
| 98 | 29:2 | LOW single-bar wicks: sweep vs not [False] sweeps | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:29) | OURS (0) | **MATCH** | Sweep condition False definition requires sweeps == 0 |
| 99 | 29:3 | LOW single-bar wicks: sweep vs not [False] target first count | SOURCED ("12", CENSUS_15m_2026-10-03_11-07.md:29) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 100 | 29:4 | LOW single-bar wicks: sweep vs not [False] target first % | SOURCED ("32%", CENSUS_15m_2026-10-03_11-07.md:29) | OURS (32%) | **MATCH** | Arithmetic formula round(12/37*100)% = 32% |
| 101 | 29:5 | LOW single-bar wicks: sweep vs not [False] stop first count | SOURCED ("22", CENSUS_15m_2026-10-03_11-07.md:29) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 102 | 29:6 | LOW single-bar wicks: sweep vs not [False] open count | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:29) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 103 | 29:7 | LOW single-bar wicks: sweep vs not [False] median wick % | SOURCED ("0.24", CENSUS_15m_2026-10-03_11-07.md:29) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 104 | 29:8 | LOW single-bar wicks: sweep vs not [False] median rel vol | SOURCED ("3.1", CENSUS_15m_2026-10-03_11-07.md:29) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 105 | 30:1 | LOW single-bar wicks: sweep vs not [True] n | SOURCED ("29", CENSUS_15m_2026-10-03_11-07.md:30) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 13+11+5=29; raw klines absent |
| 106 | 30:2 | LOW single-bar wicks: sweep vs not [True] sweeps | SOURCED ("29", CENSUS_15m_2026-10-03_11-07.md:30) | OURS (29) | **MATCH** | Sweep condition True definition requires sweeps == 29 |
| 107 | 30:3 | LOW single-bar wicks: sweep vs not [True] target first count | SOURCED ("13", CENSUS_15m_2026-10-03_11-07.md:30) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 108 | 30:4 | LOW single-bar wicks: sweep vs not [True] target first % | SOURCED ("45%", CENSUS_15m_2026-10-03_11-07.md:30) | OURS (45%) | **MATCH** | Arithmetic formula round(13/29*100)% = 45% |
| 109 | 30:5 | LOW single-bar wicks: sweep vs not [True] stop first count | SOURCED ("11", CENSUS_15m_2026-10-03_11-07.md:30) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 110 | 30:6 | LOW single-bar wicks: sweep vs not [True] open count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:30) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 111 | 30:7 | LOW single-bar wicks: sweep vs not [True] median wick % | SOURCED ("0.38", CENSUS_15m_2026-10-03_11-07.md:30) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 112 | 30:8 | LOW single-bar wicks: sweep vs not [True] median rel vol | SOURCED ("4.3", CENSUS_15m_2026-10-03_11-07.md:30) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 113 | 35:1 | LOW V-sweeps (multi-bar) by week [2026-10-05] n | SOURCED ("9", CENSUS_15m_2026-10-03_11-07.md:35) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 5+4+0=9; raw klines absent |
| 114 | 35:2 | LOW V-sweeps (multi-bar) by week [2026-10-05] sweeps | SOURCED ("9", CENSUS_15m_2026-10-03_11-07.md:35) | OURS (9) | **MATCH** | V-sweep definition requires sweeps == n (9) |
| 115 | 35:3 | LOW V-sweeps (multi-bar) by week [2026-10-05] target first count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:35) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 116 | 35:4 | LOW V-sweeps (multi-bar) by week [2026-10-05] target first % | SOURCED ("56%", CENSUS_15m_2026-10-03_11-07.md:35) | OURS (56%) | **MATCH** | Arithmetic formula round(5/9*100)% = 56% |
| 117 | 35:5 | LOW V-sweeps (multi-bar) by week [2026-10-05] stop first count | SOURCED ("4", CENSUS_15m_2026-10-03_11-07.md:35) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 118 | 35:6 | LOW V-sweeps (multi-bar) by week [2026-10-05] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:35) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 119 | 35:7 | LOW V-sweeps (multi-bar) by week [2026-10-05] median wick % | SOURCED ("0.28", CENSUS_15m_2026-10-03_11-07.md:35) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 120 | 35:8 | LOW V-sweeps (multi-bar) by week [2026-10-05] median rel vol | SOURCED ("3.0", CENSUS_15m_2026-10-03_11-07.md:35) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 121 | 36:1 | LOW V-sweeps (multi-bar) by week [2026-10-12] n | SOURCED ("19", CENSUS_15m_2026-10-03_11-07.md:36) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 7+9+3=19; raw klines absent |
| 122 | 36:2 | LOW V-sweeps (multi-bar) by week [2026-10-12] sweeps | SOURCED ("19", CENSUS_15m_2026-10-03_11-07.md:36) | OURS (19) | **MATCH** | V-sweep definition requires sweeps == n (19) |
| 123 | 36:3 | LOW V-sweeps (multi-bar) by week [2026-10-12] target first count | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:36) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 124 | 36:4 | LOW V-sweeps (multi-bar) by week [2026-10-12] target first % | SOURCED ("37%", CENSUS_15m_2026-10-03_11-07.md:36) | OURS (37%) | **MATCH** | Arithmetic formula round(7/19*100)% = 37% |
| 125 | 36:5 | LOW V-sweeps (multi-bar) by week [2026-10-12] stop first count | SOURCED ("9", CENSUS_15m_2026-10-03_11-07.md:36) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 126 | 36:6 | LOW V-sweeps (multi-bar) by week [2026-10-12] open count | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:36) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 127 | 36:7 | LOW V-sweeps (multi-bar) by week [2026-10-12] median wick % | SOURCED ("0.33", CENSUS_15m_2026-10-03_11-07.md:36) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 128 | 36:8 | LOW V-sweeps (multi-bar) by week [2026-10-12] median rel vol | SOURCED ("3.3", CENSUS_15m_2026-10-03_11-07.md:36) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 129 | 37:1 | LOW V-sweeps (multi-bar) by week [2026-10-19] n | SOURCED ("15", CENSUS_15m_2026-10-03_11-07.md:37) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 8+6+1=15; raw klines absent |
| 130 | 37:2 | LOW V-sweeps (multi-bar) by week [2026-10-19] sweeps | SOURCED ("15", CENSUS_15m_2026-10-03_11-07.md:37) | OURS (15) | **MATCH** | V-sweep definition requires sweeps == n (15) |
| 131 | 37:3 | LOW V-sweeps (multi-bar) by week [2026-10-19] target first count | SOURCED ("8", CENSUS_15m_2026-10-03_11-07.md:37) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 132 | 37:4 | LOW V-sweeps (multi-bar) by week [2026-10-19] target first % | SOURCED ("53%", CENSUS_15m_2026-10-03_11-07.md:37) | OURS (53%) | **MATCH** | Arithmetic formula round(8/15*100)% = 53% |
| 133 | 37:5 | LOW V-sweeps (multi-bar) by week [2026-10-19] stop first count | SOURCED ("6", CENSUS_15m_2026-10-03_11-07.md:37) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 134 | 37:6 | LOW V-sweeps (multi-bar) by week [2026-10-19] open count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:37) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 135 | 37:7 | LOW V-sweeps (multi-bar) by week [2026-10-19] median wick % | SOURCED ("0.28", CENSUS_15m_2026-10-03_11-07.md:37) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 136 | 37:8 | LOW V-sweeps (multi-bar) by week [2026-10-19] median rel vol | SOURCED ("2.5", CENSUS_15m_2026-10-03_11-07.md:37) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 137 | 38:1 | LOW V-sweeps (multi-bar) by week [2026-10-26] n | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:38) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 5+2+0=7; raw klines absent |
| 138 | 38:2 | LOW V-sweeps (multi-bar) by week [2026-10-26] sweeps | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:38) | OURS (7) | **MATCH** | V-sweep definition requires sweeps == n (7) |
| 139 | 38:3 | LOW V-sweeps (multi-bar) by week [2026-10-26] target first count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:38) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 140 | 38:4 | LOW V-sweeps (multi-bar) by week [2026-10-26] target first % | SOURCED ("71%", CENSUS_15m_2026-10-03_11-07.md:38) | OURS (71%) | **MATCH** | Arithmetic formula round(5/7*100)% = 71% |
| 141 | 38:5 | LOW V-sweeps (multi-bar) by week [2026-10-26] stop first count | SOURCED ("2", CENSUS_15m_2026-10-03_11-07.md:38) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 142 | 38:6 | LOW V-sweeps (multi-bar) by week [2026-10-26] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:38) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 143 | 38:7 | LOW V-sweeps (multi-bar) by week [2026-10-26] median wick % | SOURCED ("0.24", CENSUS_15m_2026-10-03_11-07.md:38) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 144 | 38:8 | LOW V-sweeps (multi-bar) by week [2026-10-26] median rel vol | SOURCED ("4.2", CENSUS_15m_2026-10-03_11-07.md:38) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 145 | 39:1 | LOW V-sweeps (multi-bar) by week [2026-11-02] n | SOURCED ("12", CENSUS_15m_2026-10-03_11-07.md:39) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 6+3+3=12; raw klines absent |
| 146 | 39:2 | LOW V-sweeps (multi-bar) by week [2026-11-02] sweeps | SOURCED ("12", CENSUS_15m_2026-10-03_11-07.md:39) | OURS (12) | **MATCH** | V-sweep definition requires sweeps == n (12) |
| 147 | 39:3 | LOW V-sweeps (multi-bar) by week [2026-11-02] target first count | SOURCED ("6", CENSUS_15m_2026-10-03_11-07.md:39) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 148 | 39:4 | LOW V-sweeps (multi-bar) by week [2026-11-02] target first % | SOURCED ("50%", CENSUS_15m_2026-10-03_11-07.md:39) | OURS (50%) | **MATCH** | Arithmetic formula round(6/12*100)% = 50% |
| 149 | 39:5 | LOW V-sweeps (multi-bar) by week [2026-11-02] stop first count | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:39) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 150 | 39:6 | LOW V-sweeps (multi-bar) by week [2026-11-02] open count | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:39) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 151 | 39:7 | LOW V-sweeps (multi-bar) by week [2026-11-02] median wick % | SOURCED ("0.48", CENSUS_15m_2026-10-03_11-07.md:39) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 152 | 39:8 | LOW V-sweeps (multi-bar) by week [2026-11-02] median rel vol | SOURCED ("2.8", CENSUS_15m_2026-10-03_11-07.md:39) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 153 | 44:1 | LOW V-sweeps: knife context [False] n | SOURCED ("61", CENSUS_15m_2026-10-03_11-07.md:44) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 31+24+6=61; raw klines absent |
| 154 | 44:2 | LOW V-sweeps: knife context [False] sweeps | SOURCED ("61", CENSUS_15m_2026-10-03_11-07.md:44) | OURS (61) | **MATCH** | V-sweep definition requires sweeps == n (61) |
| 155 | 44:3 | LOW V-sweeps: knife context [False] target first count | SOURCED ("31", CENSUS_15m_2026-10-03_11-07.md:44) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 156 | 44:4 | LOW V-sweeps: knife context [False] target first % | SOURCED ("51%", CENSUS_15m_2026-10-03_11-07.md:44) | OURS (51%) | **MATCH** | Arithmetic formula round(31/61*100)% = 51% |
| 157 | 44:5 | LOW V-sweeps: knife context [False] stop first count | SOURCED ("24", CENSUS_15m_2026-10-03_11-07.md:44) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 158 | 44:6 | LOW V-sweeps: knife context [False] open count | SOURCED ("6", CENSUS_15m_2026-10-03_11-07.md:44) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 159 | 44:7 | LOW V-sweeps: knife context [False] median wick % | SOURCED ("0.30", CENSUS_15m_2026-10-03_11-07.md:44) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 160 | 44:8 | LOW V-sweeps: knife context [False] median rel vol | SOURCED ("2.9", CENSUS_15m_2026-10-03_11-07.md:44) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 161 | 45:1 | LOW V-sweeps: knife context [True] n | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:45) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 0+0+1=1; raw klines absent |
| 162 | 45:2 | LOW V-sweeps: knife context [True] sweeps | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:45) | OURS (1) | **MATCH** | V-sweep definition requires sweeps == n (1) |
| 163 | 45:3 | LOW V-sweeps: knife context [True] target first count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:45) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 164 | 45:4 | LOW V-sweeps: knife context [True] target first % | SOURCED ("0%", CENSUS_15m_2026-10-03_11-07.md:45) | OURS (0%) | **MATCH** | Arithmetic formula round(0/1*100)% = 0% |
| 165 | 45:5 | LOW V-sweeps: knife context [True] stop first count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:45) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 166 | 45:6 | LOW V-sweeps: knife context [True] open count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:45) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 167 | 45:7 | LOW V-sweeps: knife context [True] median wick % | SOURCED ("1.04", CENSUS_15m_2026-10-03_11-07.md:45) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 168 | 45:8 | LOW V-sweeps: knife context [True] median rel vol | SOURCED ("19.6", CENSUS_15m_2026-10-03_11-07.md:45) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 169 | 50:1 | LOW V-sweeps by session [ASIA] n | SOURCED ("19", CENSUS_15m_2026-10-03_11-07.md:50) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 13+4+2=19; raw klines absent |
| 170 | 50:2 | LOW V-sweeps by session [ASIA] sweeps | SOURCED ("19", CENSUS_15m_2026-10-03_11-07.md:50) | OURS (19) | **MATCH** | V-sweep definition requires sweeps == n (19) |
| 171 | 50:3 | LOW V-sweeps by session [ASIA] target first count | SOURCED ("13", CENSUS_15m_2026-10-03_11-07.md:50) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 172 | 50:4 | LOW V-sweeps by session [ASIA] target first % | SOURCED ("68%", CENSUS_15m_2026-10-03_11-07.md:50) | OURS (68%) | **MATCH** | Arithmetic formula round(13/19*100)% = 68% |
| 173 | 50:5 | LOW V-sweeps by session [ASIA] stop first count | SOURCED ("4", CENSUS_15m_2026-10-03_11-07.md:50) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 174 | 50:6 | LOW V-sweeps by session [ASIA] open count | SOURCED ("2", CENSUS_15m_2026-10-03_11-07.md:50) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 175 | 50:7 | LOW V-sweeps by session [ASIA] median wick % | SOURCED ("0.32", CENSUS_15m_2026-10-03_11-07.md:50) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 176 | 50:8 | LOW V-sweeps by session [ASIA] median rel vol | SOURCED ("2.6", CENSUS_15m_2026-10-03_11-07.md:50) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 177 | 51:1 | LOW V-sweeps by session [EU] n | SOURCED ("16", CENSUS_15m_2026-10-03_11-07.md:51) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 7+9+0=16; raw klines absent |
| 178 | 51:2 | LOW V-sweeps by session [EU] sweeps | SOURCED ("16", CENSUS_15m_2026-10-03_11-07.md:51) | OURS (16) | **MATCH** | V-sweep definition requires sweeps == n (16) |
| 179 | 51:3 | LOW V-sweeps by session [EU] target first count | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:51) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 180 | 51:4 | LOW V-sweeps by session [EU] target first % | SOURCED ("44%", CENSUS_15m_2026-10-03_11-07.md:51) | OURS (44%) | **MATCH** | Arithmetic formula round(7/16*100)% = 44% |
| 181 | 51:5 | LOW V-sweeps by session [EU] stop first count | SOURCED ("9", CENSUS_15m_2026-10-03_11-07.md:51) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 182 | 51:6 | LOW V-sweeps by session [EU] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:51) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 183 | 51:7 | LOW V-sweeps by session [EU] median wick % | SOURCED ("0.26", CENSUS_15m_2026-10-03_11-07.md:51) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 184 | 51:8 | LOW V-sweeps by session [EU] median rel vol | SOURCED ("2.4", CENSUS_15m_2026-10-03_11-07.md:51) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 185 | 52:1 | LOW V-sweeps by session [LATE] n | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:52) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 3+3+1=7; raw klines absent |
| 186 | 52:2 | LOW V-sweeps by session [LATE] sweeps | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:52) | OURS (7) | **MATCH** | V-sweep definition requires sweeps == n (7) |
| 187 | 52:3 | LOW V-sweeps by session [LATE] target first count | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:52) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 188 | 52:4 | LOW V-sweeps by session [LATE] target first % | SOURCED ("43%", CENSUS_15m_2026-10-03_11-07.md:52) | OURS (43%) | **MATCH** | Arithmetic formula round(3/7*100)% = 43% |
| 189 | 52:5 | LOW V-sweeps by session [LATE] stop first count | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:52) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 190 | 52:6 | LOW V-sweeps by session [LATE] open count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:52) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 191 | 52:7 | LOW V-sweeps by session [LATE] median wick % | SOURCED ("0.30", CENSUS_15m_2026-10-03_11-07.md:52) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 192 | 52:8 | LOW V-sweeps by session [LATE] median rel vol | SOURCED ("8.0", CENSUS_15m_2026-10-03_11-07.md:52) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 193 | 53:1 | LOW V-sweeps by session [US] n | SOURCED ("20", CENSUS_15m_2026-10-03_11-07.md:53) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 8+8+4=20; raw klines absent |
| 194 | 53:2 | LOW V-sweeps by session [US] sweeps | SOURCED ("20", CENSUS_15m_2026-10-03_11-07.md:53) | OURS (20) | **MATCH** | V-sweep definition requires sweeps == n (20) |
| 195 | 53:3 | LOW V-sweeps by session [US] target first count | SOURCED ("8", CENSUS_15m_2026-10-03_11-07.md:53) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 196 | 53:4 | LOW V-sweeps by session [US] target first % | SOURCED ("40%", CENSUS_15m_2026-10-03_11-07.md:53) | OURS (40%) | **MATCH** | Arithmetic formula round(8/20*100)% = 40% |
| 197 | 53:5 | LOW V-sweeps by session [US] stop first count | SOURCED ("8", CENSUS_15m_2026-10-03_11-07.md:53) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 198 | 53:6 | LOW V-sweeps by session [US] open count | SOURCED ("4", CENSUS_15m_2026-10-03_11-07.md:53) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 199 | 53:7 | LOW V-sweeps by session [US] median wick % | SOURCED ("0.40", CENSUS_15m_2026-10-03_11-07.md:53) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 200 | 53:8 | LOW V-sweeps by session [US] median rel vol | SOURCED ("5.8", CENSUS_15m_2026-10-03_11-07.md:53) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 201 | 58:1 | UP single-bar wicks by week [2026-09-28] n | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:58) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 2+5+0=7; raw klines absent |
| 202 | 58:2 | UP single-bar wicks by week [2026-09-28] sweeps | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:58) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 203 | 58:3 | UP single-bar wicks by week [2026-09-28] target first count | SOURCED ("2", CENSUS_15m_2026-10-03_11-07.md:58) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 204 | 58:4 | UP single-bar wicks by week [2026-09-28] target first % | SOURCED ("29%", CENSUS_15m_2026-10-03_11-07.md:58) | OURS (29%) | **MATCH** | Arithmetic formula round(2/7*100)% = 29% |
| 205 | 58:5 | UP single-bar wicks by week [2026-09-28] stop first count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:58) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 206 | 58:6 | UP single-bar wicks by week [2026-09-28] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:58) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 207 | 58:7 | UP single-bar wicks by week [2026-09-28] median wick % | SOURCED ("0.11", CENSUS_15m_2026-10-03_11-07.md:58) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 208 | 58:8 | UP single-bar wicks by week [2026-09-28] median rel vol | SOURCED ("3.9", CENSUS_15m_2026-10-03_11-07.md:58) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 209 | 59:1 | UP single-bar wicks by week [2026-10-05] n | SOURCED ("10", CENSUS_15m_2026-10-03_11-07.md:59) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 3+6+1=10; raw klines absent |
| 210 | 59:2 | UP single-bar wicks by week [2026-10-05] sweeps | SOURCED ("4", CENSUS_15m_2026-10-03_11-07.md:59) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 211 | 59:3 | UP single-bar wicks by week [2026-10-05] target first count | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:59) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 212 | 59:4 | UP single-bar wicks by week [2026-10-05] target first % | SOURCED ("30%", CENSUS_15m_2026-10-03_11-07.md:59) | OURS (30%) | **MATCH** | Arithmetic formula round(3/10*100)% = 30% |
| 213 | 59:5 | UP single-bar wicks by week [2026-10-05] stop first count | SOURCED ("6", CENSUS_15m_2026-10-03_11-07.md:59) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 214 | 59:6 | UP single-bar wicks by week [2026-10-05] open count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:59) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 215 | 59:7 | UP single-bar wicks by week [2026-10-05] median wick % | SOURCED ("0.21", CENSUS_15m_2026-10-03_11-07.md:59) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 216 | 59:8 | UP single-bar wicks by week [2026-10-05] median rel vol | SOURCED ("2.2", CENSUS_15m_2026-10-03_11-07.md:59) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 217 | 60:1 | UP single-bar wicks by week [2026-10-12] n | SOURCED ("14", CENSUS_15m_2026-10-03_11-07.md:60) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 7+7+0=14; raw klines absent |
| 218 | 60:2 | UP single-bar wicks by week [2026-10-12] sweeps | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:60) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 219 | 60:3 | UP single-bar wicks by week [2026-10-12] target first count | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:60) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 220 | 60:4 | UP single-bar wicks by week [2026-10-12] target first % | SOURCED ("50%", CENSUS_15m_2026-10-03_11-07.md:60) | OURS (50%) | **MATCH** | Arithmetic formula round(7/14*100)% = 50% |
| 221 | 60:5 | UP single-bar wicks by week [2026-10-12] stop first count | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:60) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 222 | 60:6 | UP single-bar wicks by week [2026-10-12] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:60) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 223 | 60:7 | UP single-bar wicks by week [2026-10-12] median wick % | SOURCED ("0.22", CENSUS_15m_2026-10-03_11-07.md:60) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 224 | 60:8 | UP single-bar wicks by week [2026-10-12] median rel vol | SOURCED ("3.0", CENSUS_15m_2026-10-03_11-07.md:60) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 225 | 61:1 | UP single-bar wicks by week [2026-10-19] n | SOURCED ("12", CENSUS_15m_2026-10-03_11-07.md:61) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 6+5+1=12; raw klines absent |
| 226 | 61:2 | UP single-bar wicks by week [2026-10-19] sweeps | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:61) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 227 | 61:3 | UP single-bar wicks by week [2026-10-19] target first count | SOURCED ("6", CENSUS_15m_2026-10-03_11-07.md:61) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 228 | 61:4 | UP single-bar wicks by week [2026-10-19] target first % | SOURCED ("50%", CENSUS_15m_2026-10-03_11-07.md:61) | OURS (50%) | **MATCH** | Arithmetic formula round(6/12*100)% = 50% |
| 229 | 61:5 | UP single-bar wicks by week [2026-10-19] stop first count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:61) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 230 | 61:6 | UP single-bar wicks by week [2026-10-19] open count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:61) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 231 | 61:7 | UP single-bar wicks by week [2026-10-19] median wick % | SOURCED ("0.26", CENSUS_15m_2026-10-03_11-07.md:61) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 232 | 61:8 | UP single-bar wicks by week [2026-10-19] median rel vol | SOURCED ("2.6", CENSUS_15m_2026-10-03_11-07.md:61) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 233 | 62:1 | UP single-bar wicks by week [2026-10-26] n | SOURCED ("12", CENSUS_15m_2026-10-03_11-07.md:62) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 7+5+0=12; raw klines absent |
| 234 | 62:2 | UP single-bar wicks by week [2026-10-26] sweeps | SOURCED ("4", CENSUS_15m_2026-10-03_11-07.md:62) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 235 | 62:3 | UP single-bar wicks by week [2026-10-26] target first count | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:62) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 236 | 62:4 | UP single-bar wicks by week [2026-10-26] target first % | SOURCED ("58%", CENSUS_15m_2026-10-03_11-07.md:62) | OURS (58%) | **MATCH** | Arithmetic formula round(7/12*100)% = 58% |
| 237 | 62:5 | UP single-bar wicks by week [2026-10-26] stop first count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:62) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 238 | 62:6 | UP single-bar wicks by week [2026-10-26] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:62) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 239 | 62:7 | UP single-bar wicks by week [2026-10-26] median wick % | SOURCED ("0.36", CENSUS_15m_2026-10-03_11-07.md:62) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 240 | 62:8 | UP single-bar wicks by week [2026-10-26] median rel vol | SOURCED ("4.3", CENSUS_15m_2026-10-03_11-07.md:62) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 241 | 63:1 | UP single-bar wicks by week [2026-11-02] n | SOURCED ("11", CENSUS_15m_2026-10-03_11-07.md:63) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 6+5+0=11; raw klines absent |
| 242 | 63:2 | UP single-bar wicks by week [2026-11-02] sweeps | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:63) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 243 | 63:3 | UP single-bar wicks by week [2026-11-02] target first count | SOURCED ("6", CENSUS_15m_2026-10-03_11-07.md:63) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 244 | 63:4 | UP single-bar wicks by week [2026-11-02] target first % | SOURCED ("55%", CENSUS_15m_2026-10-03_11-07.md:63) | OURS (55%) | **MATCH** | Arithmetic formula round(6/11*100)% = 55% |
| 245 | 63:5 | UP single-bar wicks by week [2026-11-02] stop first count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:63) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 246 | 63:6 | UP single-bar wicks by week [2026-11-02] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:63) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 247 | 63:7 | UP single-bar wicks by week [2026-11-02] median wick % | SOURCED ("0.30", CENSUS_15m_2026-10-03_11-07.md:63) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 248 | 63:8 | UP single-bar wicks by week [2026-11-02] median rel vol | SOURCED ("3.7", CENSUS_15m_2026-10-03_11-07.md:63) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 249 | 68:1 | UP single-bar wicks by session [ASIA] n | SOURCED ("22", CENSUS_15m_2026-10-03_11-07.md:68) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 8+14+0=22; raw klines absent |
| 250 | 68:2 | UP single-bar wicks by session [ASIA] sweeps | SOURCED ("11", CENSUS_15m_2026-10-03_11-07.md:68) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 251 | 68:3 | UP single-bar wicks by session [ASIA] target first count | SOURCED ("8", CENSUS_15m_2026-10-03_11-07.md:68) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 252 | 68:4 | UP single-bar wicks by session [ASIA] target first % | SOURCED ("36%", CENSUS_15m_2026-10-03_11-07.md:68) | OURS (36%) | **MATCH** | Arithmetic formula round(8/22*100)% = 36% |
| 253 | 68:5 | UP single-bar wicks by session [ASIA] stop first count | SOURCED ("14", CENSUS_15m_2026-10-03_11-07.md:68) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 254 | 68:6 | UP single-bar wicks by session [ASIA] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:68) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 255 | 68:7 | UP single-bar wicks by session [ASIA] median wick % | SOURCED ("0.21", CENSUS_15m_2026-10-03_11-07.md:68) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 256 | 68:8 | UP single-bar wicks by session [ASIA] median rel vol | SOURCED ("2.8", CENSUS_15m_2026-10-03_11-07.md:68) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 257 | 69:1 | UP single-bar wicks by session [EU] n | SOURCED ("10", CENSUS_15m_2026-10-03_11-07.md:69) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 4+5+1=10; raw klines absent |
| 258 | 69:2 | UP single-bar wicks by session [EU] sweeps | SOURCED ("4", CENSUS_15m_2026-10-03_11-07.md:69) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 259 | 69:3 | UP single-bar wicks by session [EU] target first count | SOURCED ("4", CENSUS_15m_2026-10-03_11-07.md:69) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 260 | 69:4 | UP single-bar wicks by session [EU] target first % | SOURCED ("40%", CENSUS_15m_2026-10-03_11-07.md:69) | OURS (40%) | **MATCH** | Arithmetic formula round(4/10*100)% = 40% |
| 261 | 69:5 | UP single-bar wicks by session [EU] stop first count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:69) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 262 | 69:6 | UP single-bar wicks by session [EU] open count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:69) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 263 | 69:7 | UP single-bar wicks by session [EU] median wick % | SOURCED ("0.23", CENSUS_15m_2026-10-03_11-07.md:69) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 264 | 69:8 | UP single-bar wicks by session [EU] median rel vol | SOURCED ("2.4", CENSUS_15m_2026-10-03_11-07.md:69) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 265 | 70:1 | UP single-bar wicks by session [LATE] n | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:70) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 5+2+0=7; raw klines absent |
| 266 | 70:2 | UP single-bar wicks by session [LATE] sweeps | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:70) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 267 | 70:3 | UP single-bar wicks by session [LATE] target first count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:70) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 268 | 70:4 | UP single-bar wicks by session [LATE] target first % | SOURCED ("71%", CENSUS_15m_2026-10-03_11-07.md:70) | OURS (71%) | **MATCH** | Arithmetic formula round(5/7*100)% = 71% |
| 269 | 70:5 | UP single-bar wicks by session [LATE] stop first count | SOURCED ("2", CENSUS_15m_2026-10-03_11-07.md:70) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 270 | 70:6 | UP single-bar wicks by session [LATE] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:70) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 271 | 70:7 | UP single-bar wicks by session [LATE] median wick % | SOURCED ("0.42", CENSUS_15m_2026-10-03_11-07.md:70) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 272 | 70:8 | UP single-bar wicks by session [LATE] median rel vol | SOURCED ("8.3", CENSUS_15m_2026-10-03_11-07.md:70) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 273 | 71:1 | UP single-bar wicks by session [US] n | SOURCED ("27", CENSUS_15m_2026-10-03_11-07.md:71) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 14+12+1=27; raw klines absent |
| 274 | 71:2 | UP single-bar wicks by session [US] sweeps | SOURCED ("8", CENSUS_15m_2026-10-03_11-07.md:71) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 275 | 71:3 | UP single-bar wicks by session [US] target first count | SOURCED ("14", CENSUS_15m_2026-10-03_11-07.md:71) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 276 | 71:4 | UP single-bar wicks by session [US] target first % | SOURCED ("52%", CENSUS_15m_2026-10-03_11-07.md:71) | OURS (52%) | **MATCH** | Arithmetic formula round(14/27*100)% = 52% |
| 277 | 71:5 | UP single-bar wicks by session [US] stop first count | SOURCED ("12", CENSUS_15m_2026-10-03_11-07.md:71) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 278 | 71:6 | UP single-bar wicks by session [US] open count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:71) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 279 | 71:7 | UP single-bar wicks by session [US] median wick % | SOURCED ("0.27", CENSUS_15m_2026-10-03_11-07.md:71) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 280 | 71:8 | UP single-bar wicks by session [US] median rel vol | SOURCED ("3.4", CENSUS_15m_2026-10-03_11-07.md:71) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 281 | 76:1 | UP single-bar wicks: knife context [False] n | SOURCED ("65", CENSUS_15m_2026-10-03_11-07.md:76) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 31+32+2=65; raw klines absent |
| 282 | 76:2 | UP single-bar wicks: knife context [False] sweeps | SOURCED ("24", CENSUS_15m_2026-10-03_11-07.md:76) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 283 | 76:3 | UP single-bar wicks: knife context [False] target first count | SOURCED ("31", CENSUS_15m_2026-10-03_11-07.md:76) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 284 | 76:4 | UP single-bar wicks: knife context [False] target first % | SOURCED ("48%", CENSUS_15m_2026-10-03_11-07.md:76) | OURS (48%) | **MATCH** | Arithmetic formula round(31/65*100)% = 48% |
| 285 | 76:5 | UP single-bar wicks: knife context [False] stop first count | SOURCED ("32", CENSUS_15m_2026-10-03_11-07.md:76) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 286 | 76:6 | UP single-bar wicks: knife context [False] open count | SOURCED ("2", CENSUS_15m_2026-10-03_11-07.md:76) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 287 | 76:7 | UP single-bar wicks: knife context [False] median wick % | SOURCED ("0.26", CENSUS_15m_2026-10-03_11-07.md:76) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 288 | 76:8 | UP single-bar wicks: knife context [False] median rel vol | SOURCED ("3.0", CENSUS_15m_2026-10-03_11-07.md:76) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 289 | 77:1 | UP single-bar wicks: knife context [True] n | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:77) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 0+1+0=1; raw klines absent |
| 290 | 77:2 | UP single-bar wicks: knife context [True] sweeps | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:77) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical sweep count; raw klines absent |
| 291 | 77:3 | UP single-bar wicks: knife context [True] target first count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:77) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 292 | 77:4 | UP single-bar wicks: knife context [True] target first % | SOURCED ("0%", CENSUS_15m_2026-10-03_11-07.md:77) | OURS (0%) | **MATCH** | Arithmetic formula round(0/1*100)% = 0% |
| 293 | 77:5 | UP single-bar wicks: knife context [True] stop first count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:77) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 294 | 77:6 | UP single-bar wicks: knife context [True] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:77) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 295 | 77:7 | UP single-bar wicks: knife context [True] median wick % | SOURCED ("0.48", CENSUS_15m_2026-10-03_11-07.md:77) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 296 | 77:8 | UP single-bar wicks: knife context [True] median rel vol | SOURCED ("5.6", CENSUS_15m_2026-10-03_11-07.md:77) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 297 | 82:1 | UP single-bar wicks: sweep vs not [False] n | SOURCED ("42", CENSUS_15m_2026-10-03_11-07.md:82) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 20+21+1=42; raw klines absent |
| 298 | 82:2 | UP single-bar wicks: sweep vs not [False] sweeps | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:82) | OURS (0) | **MATCH** | Sweep condition False definition requires sweeps == 0 |
| 299 | 82:3 | UP single-bar wicks: sweep vs not [False] target first count | SOURCED ("20", CENSUS_15m_2026-10-03_11-07.md:82) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 300 | 82:4 | UP single-bar wicks: sweep vs not [False] target first % | SOURCED ("48%", CENSUS_15m_2026-10-03_11-07.md:82) | OURS (48%) | **MATCH** | Arithmetic formula round(20/42*100)% = 48% |
| 301 | 82:5 | UP single-bar wicks: sweep vs not [False] stop first count | SOURCED ("21", CENSUS_15m_2026-10-03_11-07.md:82) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 302 | 82:6 | UP single-bar wicks: sweep vs not [False] open count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:82) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 303 | 82:7 | UP single-bar wicks: sweep vs not [False] median wick % | SOURCED ("0.22", CENSUS_15m_2026-10-03_11-07.md:82) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 304 | 82:8 | UP single-bar wicks: sweep vs not [False] median rel vol | SOURCED ("2.6", CENSUS_15m_2026-10-03_11-07.md:82) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 305 | 83:1 | UP single-bar wicks: sweep vs not [True] n | SOURCED ("24", CENSUS_15m_2026-10-03_11-07.md:83) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 11+12+1=24; raw klines absent |
| 306 | 83:2 | UP single-bar wicks: sweep vs not [True] sweeps | SOURCED ("24", CENSUS_15m_2026-10-03_11-07.md:83) | OURS (24) | **MATCH** | Sweep condition True definition requires sweeps == 24 |
| 307 | 83:3 | UP single-bar wicks: sweep vs not [True] target first count | SOURCED ("11", CENSUS_15m_2026-10-03_11-07.md:83) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 308 | 83:4 | UP single-bar wicks: sweep vs not [True] target first % | SOURCED ("46%", CENSUS_15m_2026-10-03_11-07.md:83) | OURS (46%) | **MATCH** | Arithmetic formula round(11/24*100)% = 46% |
| 309 | 83:5 | UP single-bar wicks: sweep vs not [True] stop first count | SOURCED ("12", CENSUS_15m_2026-10-03_11-07.md:83) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 310 | 83:6 | UP single-bar wicks: sweep vs not [True] open count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:83) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 311 | 83:7 | UP single-bar wicks: sweep vs not [True] median wick % | SOURCED ("0.28", CENSUS_15m_2026-10-03_11-07.md:83) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 312 | 83:8 | UP single-bar wicks: sweep vs not [True] median rel vol | SOURCED ("4.0", CENSUS_15m_2026-10-03_11-07.md:83) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 313 | 88:1 | UP V-sweeps (multi-bar) by week [2026-09-28] n | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:88) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 1+2+0=3; raw klines absent |
| 314 | 88:2 | UP V-sweeps (multi-bar) by week [2026-09-28] sweeps | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:88) | OURS (3) | **MATCH** | V-sweep definition requires sweeps == n (3) |
| 315 | 88:3 | UP V-sweeps (multi-bar) by week [2026-09-28] target first count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:88) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 316 | 88:4 | UP V-sweeps (multi-bar) by week [2026-09-28] target first % | SOURCED ("33%", CENSUS_15m_2026-10-03_11-07.md:88) | OURS (33%) | **MATCH** | Arithmetic formula round(1/3*100)% = 33% |
| 317 | 88:5 | UP V-sweeps (multi-bar) by week [2026-09-28] stop first count | SOURCED ("2", CENSUS_15m_2026-10-03_11-07.md:88) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 318 | 88:6 | UP V-sweeps (multi-bar) by week [2026-09-28] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:88) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 319 | 88:7 | UP V-sweeps (multi-bar) by week [2026-09-28] median wick % | SOURCED ("0.20", CENSUS_15m_2026-10-03_11-07.md:88) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 320 | 88:8 | UP V-sweeps (multi-bar) by week [2026-09-28] median rel vol | SOURCED ("4.7", CENSUS_15m_2026-10-03_11-07.md:88) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 321 | 89:1 | UP V-sweeps (multi-bar) by week [2026-10-05] n | SOURCED ("14", CENSUS_15m_2026-10-03_11-07.md:89) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 7+5+2=14; raw klines absent |
| 322 | 89:2 | UP V-sweeps (multi-bar) by week [2026-10-05] sweeps | SOURCED ("14", CENSUS_15m_2026-10-03_11-07.md:89) | OURS (14) | **MATCH** | V-sweep definition requires sweeps == n (14) |
| 323 | 89:3 | UP V-sweeps (multi-bar) by week [2026-10-05] target first count | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:89) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 324 | 89:4 | UP V-sweeps (multi-bar) by week [2026-10-05] target first % | SOURCED ("50%", CENSUS_15m_2026-10-03_11-07.md:89) | OURS (50%) | **MATCH** | Arithmetic formula round(7/14*100)% = 50% |
| 325 | 89:5 | UP V-sweeps (multi-bar) by week [2026-10-05] stop first count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:89) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 326 | 89:6 | UP V-sweeps (multi-bar) by week [2026-10-05] open count | SOURCED ("2", CENSUS_15m_2026-10-03_11-07.md:89) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 327 | 89:7 | UP V-sweeps (multi-bar) by week [2026-10-05] median wick % | SOURCED ("0.20", CENSUS_15m_2026-10-03_11-07.md:89) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 328 | 89:8 | UP V-sweeps (multi-bar) by week [2026-10-05] median rel vol | SOURCED ("1.3", CENSUS_15m_2026-10-03_11-07.md:89) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 329 | 90:1 | UP V-sweeps (multi-bar) by week [2026-10-12] n | SOURCED ("14", CENSUS_15m_2026-10-03_11-07.md:90) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 6+8+0=14; raw klines absent |
| 330 | 90:2 | UP V-sweeps (multi-bar) by week [2026-10-12] sweeps | SOURCED ("14", CENSUS_15m_2026-10-03_11-07.md:90) | OURS (14) | **MATCH** | V-sweep definition requires sweeps == n (14) |
| 331 | 90:3 | UP V-sweeps (multi-bar) by week [2026-10-12] target first count | SOURCED ("6", CENSUS_15m_2026-10-03_11-07.md:90) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 332 | 90:4 | UP V-sweeps (multi-bar) by week [2026-10-12] target first % | SOURCED ("43%", CENSUS_15m_2026-10-03_11-07.md:90) | OURS (43%) | **MATCH** | Arithmetic formula round(6/14*100)% = 43% |
| 333 | 90:5 | UP V-sweeps (multi-bar) by week [2026-10-12] stop first count | SOURCED ("8", CENSUS_15m_2026-10-03_11-07.md:90) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 334 | 90:6 | UP V-sweeps (multi-bar) by week [2026-10-12] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:90) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 335 | 90:7 | UP V-sweeps (multi-bar) by week [2026-10-12] median wick % | SOURCED ("0.28", CENSUS_15m_2026-10-03_11-07.md:90) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 336 | 90:8 | UP V-sweeps (multi-bar) by week [2026-10-12] median rel vol | SOURCED ("2.4", CENSUS_15m_2026-10-03_11-07.md:90) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 337 | 91:1 | UP V-sweeps (multi-bar) by week [2026-10-19] n | SOURCED ("10", CENSUS_15m_2026-10-03_11-07.md:91) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 2+8+0=10; raw klines absent |
| 338 | 91:2 | UP V-sweeps (multi-bar) by week [2026-10-19] sweeps | SOURCED ("10", CENSUS_15m_2026-10-03_11-07.md:91) | OURS (10) | **MATCH** | V-sweep definition requires sweeps == n (10) |
| 339 | 91:3 | UP V-sweeps (multi-bar) by week [2026-10-19] target first count | SOURCED ("2", CENSUS_15m_2026-10-03_11-07.md:91) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 340 | 91:4 | UP V-sweeps (multi-bar) by week [2026-10-19] target first % | SOURCED ("20%", CENSUS_15m_2026-10-03_11-07.md:91) | OURS (20%) | **MATCH** | Arithmetic formula round(2/10*100)% = 20% |
| 341 | 91:5 | UP V-sweeps (multi-bar) by week [2026-10-19] stop first count | SOURCED ("8", CENSUS_15m_2026-10-03_11-07.md:91) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 342 | 91:6 | UP V-sweeps (multi-bar) by week [2026-10-19] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:91) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 343 | 91:7 | UP V-sweeps (multi-bar) by week [2026-10-19] median wick % | SOURCED ("0.20", CENSUS_15m_2026-10-03_11-07.md:91) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 344 | 91:8 | UP V-sweeps (multi-bar) by week [2026-10-19] median rel vol | SOURCED ("3.0", CENSUS_15m_2026-10-03_11-07.md:91) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 345 | 92:1 | UP V-sweeps (multi-bar) by week [2026-10-26] n | SOURCED ("16", CENSUS_15m_2026-10-03_11-07.md:92) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 8+7+1=16; raw klines absent |
| 346 | 92:2 | UP V-sweeps (multi-bar) by week [2026-10-26] sweeps | SOURCED ("16", CENSUS_15m_2026-10-03_11-07.md:92) | OURS (16) | **MATCH** | V-sweep definition requires sweeps == n (16) |
| 347 | 92:3 | UP V-sweeps (multi-bar) by week [2026-10-26] target first count | SOURCED ("8", CENSUS_15m_2026-10-03_11-07.md:92) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 348 | 92:4 | UP V-sweeps (multi-bar) by week [2026-10-26] target first % | SOURCED ("50%", CENSUS_15m_2026-10-03_11-07.md:92) | OURS (50%) | **MATCH** | Arithmetic formula round(8/16*100)% = 50% |
| 349 | 92:5 | UP V-sweeps (multi-bar) by week [2026-10-26] stop first count | SOURCED ("7", CENSUS_15m_2026-10-03_11-07.md:92) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 350 | 92:6 | UP V-sweeps (multi-bar) by week [2026-10-26] open count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:92) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 351 | 92:7 | UP V-sweeps (multi-bar) by week [2026-10-26] median wick % | SOURCED ("0.30", CENSUS_15m_2026-10-03_11-07.md:92) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 352 | 92:8 | UP V-sweeps (multi-bar) by week [2026-10-26] median rel vol | SOURCED ("3.7", CENSUS_15m_2026-10-03_11-07.md:92) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 353 | 93:1 | UP V-sweeps (multi-bar) by week [2026-11-02] n | SOURCED ("12", CENSUS_15m_2026-10-03_11-07.md:93) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 5+5+2=12; raw klines absent |
| 354 | 93:2 | UP V-sweeps (multi-bar) by week [2026-11-02] sweeps | SOURCED ("12", CENSUS_15m_2026-10-03_11-07.md:93) | OURS (12) | **MATCH** | V-sweep definition requires sweeps == n (12) |
| 355 | 93:3 | UP V-sweeps (multi-bar) by week [2026-11-02] target first count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:93) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 356 | 93:4 | UP V-sweeps (multi-bar) by week [2026-11-02] target first % | SOURCED ("42%", CENSUS_15m_2026-10-03_11-07.md:93) | OURS (42%) | **MATCH** | Arithmetic formula round(5/12*100)% = 42% |
| 357 | 93:5 | UP V-sweeps (multi-bar) by week [2026-11-02] stop first count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:93) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 358 | 93:6 | UP V-sweeps (multi-bar) by week [2026-11-02] open count | SOURCED ("2", CENSUS_15m_2026-10-03_11-07.md:93) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 359 | 93:7 | UP V-sweeps (multi-bar) by week [2026-11-02] median wick % | SOURCED ("0.23", CENSUS_15m_2026-10-03_11-07.md:93) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 360 | 93:8 | UP V-sweeps (multi-bar) by week [2026-11-02] median rel vol | SOURCED ("1.5", CENSUS_15m_2026-10-03_11-07.md:93) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 361 | 98:1 | UP V-sweeps: knife context [False] n | SOURCED ("69", CENSUS_15m_2026-10-03_11-07.md:98) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 29+35+5=69; raw klines absent |
| 362 | 98:2 | UP V-sweeps: knife context [False] sweeps | SOURCED ("69", CENSUS_15m_2026-10-03_11-07.md:98) | OURS (69) | **MATCH** | V-sweep definition requires sweeps == n (69) |
| 363 | 98:3 | UP V-sweeps: knife context [False] target first count | SOURCED ("29", CENSUS_15m_2026-10-03_11-07.md:98) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 364 | 98:4 | UP V-sweeps: knife context [False] target first % | SOURCED ("42%", CENSUS_15m_2026-10-03_11-07.md:98) | OURS (42%) | **MATCH** | Arithmetic formula round(29/69*100)% = 42% |
| 365 | 98:5 | UP V-sweeps: knife context [False] stop first count | SOURCED ("35", CENSUS_15m_2026-10-03_11-07.md:98) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 366 | 98:6 | UP V-sweeps: knife context [False] open count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:98) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 367 | 98:7 | UP V-sweeps: knife context [False] median wick % | SOURCED ("0.23", CENSUS_15m_2026-10-03_11-07.md:98) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 368 | 98:8 | UP V-sweeps: knife context [False] median rel vol | SOURCED ("2.5", CENSUS_15m_2026-10-03_11-07.md:98) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 369 | 103:1 | UP V-sweeps by session [ASIA] n | SOURCED ("25", CENSUS_15m_2026-10-03_11-07.md:103) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 9+15+1=25; raw klines absent |
| 370 | 103:2 | UP V-sweeps by session [ASIA] sweeps | SOURCED ("25", CENSUS_15m_2026-10-03_11-07.md:103) | OURS (25) | **MATCH** | V-sweep definition requires sweeps == n (25) |
| 371 | 103:3 | UP V-sweeps by session [ASIA] target first count | SOURCED ("9", CENSUS_15m_2026-10-03_11-07.md:103) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 372 | 103:4 | UP V-sweeps by session [ASIA] target first % | SOURCED ("36%", CENSUS_15m_2026-10-03_11-07.md:103) | OURS (36%) | **MATCH** | Arithmetic formula round(9/25*100)% = 36% |
| 373 | 103:5 | UP V-sweeps by session [ASIA] stop first count | SOURCED ("15", CENSUS_15m_2026-10-03_11-07.md:103) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 374 | 103:6 | UP V-sweeps by session [ASIA] open count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:103) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 375 | 103:7 | UP V-sweeps by session [ASIA] median wick % | SOURCED ("0.26", CENSUS_15m_2026-10-03_11-07.md:103) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 376 | 103:8 | UP V-sweeps by session [ASIA] median rel vol | SOURCED ("2.2", CENSUS_15m_2026-10-03_11-07.md:103) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 377 | 104:1 | UP V-sweeps by session [EU] n | SOURCED ("18", CENSUS_15m_2026-10-03_11-07.md:104) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 9+9+0=18; raw klines absent |
| 378 | 104:2 | UP V-sweeps by session [EU] sweeps | SOURCED ("18", CENSUS_15m_2026-10-03_11-07.md:104) | OURS (18) | **MATCH** | V-sweep definition requires sweeps == n (18) |
| 379 | 104:3 | UP V-sweeps by session [EU] target first count | SOURCED ("9", CENSUS_15m_2026-10-03_11-07.md:104) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 380 | 104:4 | UP V-sweeps by session [EU] target first % | SOURCED ("50%", CENSUS_15m_2026-10-03_11-07.md:104) | OURS (50%) | **MATCH** | Arithmetic formula round(9/18*100)% = 50% |
| 381 | 104:5 | UP V-sweeps by session [EU] stop first count | SOURCED ("9", CENSUS_15m_2026-10-03_11-07.md:104) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 382 | 104:6 | UP V-sweeps by session [EU] open count | SOURCED ("0", CENSUS_15m_2026-10-03_11-07.md:104) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 383 | 104:7 | UP V-sweeps by session [EU] median wick % | SOURCED ("0.22", CENSUS_15m_2026-10-03_11-07.md:104) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 384 | 104:8 | UP V-sweeps by session [EU] median rel vol | SOURCED ("2.4", CENSUS_15m_2026-10-03_11-07.md:104) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 385 | 105:1 | UP V-sweeps by session [LATE] n | SOURCED ("10", CENSUS_15m_2026-10-03_11-07.md:105) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 3+6+1=10; raw klines absent |
| 386 | 105:2 | UP V-sweeps by session [LATE] sweeps | SOURCED ("10", CENSUS_15m_2026-10-03_11-07.md:105) | OURS (10) | **MATCH** | V-sweep definition requires sweeps == n (10) |
| 387 | 105:3 | UP V-sweeps by session [LATE] target first count | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:105) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 388 | 105:4 | UP V-sweeps by session [LATE] target first % | SOURCED ("30%", CENSUS_15m_2026-10-03_11-07.md:105) | OURS (30%) | **MATCH** | Arithmetic formula round(3/10*100)% = 30% |
| 389 | 105:5 | UP V-sweeps by session [LATE] stop first count | SOURCED ("6", CENSUS_15m_2026-10-03_11-07.md:105) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 390 | 105:6 | UP V-sweeps by session [LATE] open count | SOURCED ("1", CENSUS_15m_2026-10-03_11-07.md:105) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 391 | 105:7 | UP V-sweeps by session [LATE] median wick % | SOURCED ("0.19", CENSUS_15m_2026-10-03_11-07.md:105) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 392 | 105:8 | UP V-sweeps by session [LATE] median rel vol | SOURCED ("1.4", CENSUS_15m_2026-10-03_11-07.md:105) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 393 | 106:1 | UP V-sweeps by session [US] n | SOURCED ("16", CENSUS_15m_2026-10-03_11-07.md:106) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical event count; verified row sum identity 8+5+3=16; raw klines absent |
| 394 | 106:2 | UP V-sweeps by session [US] sweeps | SOURCED ("16", CENSUS_15m_2026-10-03_11-07.md:106) | OURS (16) | **MATCH** | V-sweep definition requires sweeps == n (16) |
| 395 | 106:3 | UP V-sweeps by session [US] target first count | SOURCED ("8", CENSUS_15m_2026-10-03_11-07.md:106) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical target-first hit count; raw klines absent |
| 396 | 106:4 | UP V-sweeps by session [US] target first % | SOURCED ("50%", CENSUS_15m_2026-10-03_11-07.md:106) | OURS (50%) | **MATCH** | Arithmetic formula round(8/16*100)% = 50% |
| 397 | 106:5 | UP V-sweeps by session [US] stop first count | SOURCED ("5", CENSUS_15m_2026-10-03_11-07.md:106) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical stop-first hit count; raw klines absent |
| 398 | 106:6 | UP V-sweeps by session [US] open count | SOURCED ("3", CENSUS_15m_2026-10-03_11-07.md:106) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Empirical open/unresolved count; raw klines absent |
| 399 | 106:7 | UP V-sweeps by session [US] median wick % | SOURCED ("0.29", CENSUS_15m_2026-10-03_11-07.md:106) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median wick %; raw bar series absent |
| 400 | 106:8 | UP V-sweeps by session [US] median rel vol | SOURCED ("4.0", CENSUS_15m_2026-10-03_11-07.md:106) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Distribution median relative volume; raw bar series absent |
| 401 | 109:1 | Fri 15:00 LOW 1bar low | SOURCED ("74810", CENSUS_15m_2026-10-03_11-07.md:109) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Individual bar price quote; raw klines absent |
| 402 | 109:2 | Fri 15:00 LOW 1bar high | SOURCED ("75820", CENSUS_15m_2026-10-03_11-07.md:109) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Individual bar price quote; raw klines absent |
| 403 | 109:3 | Fri 15:00 LOW 1bar close | SOURCED ("75809", CENSUS_15m_2026-10-03_11-07.md:109) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Individual bar price quote; raw klines absent |
| 404 | 109:4 | Fri 15:00 LOW 1bar wick % | SOURCED ("0.93%", CENSUS_15m_2026-10-03_11-07.md:109) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Individual bar calculated wick %; open price and raw klines absent |
| 405 | 109:5 | Fri 15:00 LOW 1bar relvol | SOURCED ("12.0", CENSUS_15m_2026-10-03_11-07.md:109) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Individual bar relative volume; baseline volume distribution absent |
| 406 | 110:1 | Fri 15:30 LOW 1bar low | SOURCED ("75250", CENSUS_15m_2026-10-03_11-07.md:110) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Individual bar price quote; raw klines absent |
| 407 | 110:2 | Fri 15:30 LOW 1bar high | SOURCED ("75720", CENSUS_15m_2026-10-03_11-07.md:110) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Individual bar price quote; raw klines absent |
| 408 | 110:3 | Fri 15:30 LOW 1bar close | SOURCED ("75696", CENSUS_15m_2026-10-03_11-07.md:110) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Individual bar price quote; raw klines absent |
| 409 | 110:4 | Fri 15:30 LOW 1bar wick % | SOURCED ("0.48%", CENSUS_15m_2026-10-03_11-07.md:110) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Individual bar calculated wick %; open price and raw klines absent |
| 410 | 110:5 | Fri 15:30 LOW 1bar relvol | SOURCED ("2.6", CENSUS_15m_2026-10-03_11-07.md:110) | OURS (NOT_IN_DATA) | **NOT_IN_DATA** | Individual bar relative volume; baseline volume distribution absent |

## Verdict and Follow-up

- **Mathematical Integrity**: PASS. All internal formulas, percentage roundings, partition marginal sums, and cross-table identities hold with zero discrepancies (0 DIFF).
- **Data Completeness**: INCOMPLETE (328 NOT_IN_DATA). The empirical census figures cannot be independently recomputed from scratch because `btc_15m_5w.json` was not committed to `MyTradingSys/research/wicks_2026-11/` or the repo.
- **Remediation**: If an independent re-derivation from raw market data is required by the operator, commit `btc_15m_5w.json` or the per-event detection CSV into `MyTradingSys/research/wicks_2026-11/` and formalize the wick detection thresholds in `FORMULAS.md` (Plan W1).
