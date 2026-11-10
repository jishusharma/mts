MATCH: 10 | DIFF: 0 | NOT_IN_DATA: 0

# Gemini Blind Read Report: `census_1109.py` vs Module Docstring Rules

- **Card**: `gemini-blind-read-census-1109-py`
- **Date**: 2026-11-10 UTC
- **Reader**: Gemini (`gemini-3.8-flash-low`, blind read worker, JIS-NUC)
- **Target File**: `MyTradingSys/research/sim_desk/census_1109.py`
- **Scope In Read**:
  - `MyTradingSys/research/sim_desk/census_1109.py` (lines 1-10 docstring rules and lines 11-219 implementation)
  - `MyTradingSys/research/sim_desk/results/_census_1109.json` (output artifact checked for compliance)
- **Scope Out Respected**: No source code modified; no live-tree edit; no `.secrets` or `.env` read; no network re-fetch; no trades/orders.

---

## 1. Specification Clauses Extracted from Docstring (`census_1109.py:1-10`)

The module docstring defines the following explicit rules:
1. **Rule 1 (Outputs & Scope)**: "11-09 census rows for the simulator page: one row per tested study with a colour verdict chip, n, mean net R and a one-line why, read from the studies' own RESULT / cells / events / READING files. Writes results/_census_1109.json (the page's '11-09 census' tab)." (`census_1109.py:1-2`)
2. **Rule 2 (No new backtest)**: "Rules (card sim-desk-edge-hunt-census-1109): no new backtest" (`census_1109.py:4`)
3. **Rule 3 (No number outside RESULT / study files)**: "and no number that is not already in a RESULT file" [qualified by line 2: 'read from the studies' own RESULT / cells / events / READING files'] (`census_1109.py:2,4`)
4. **Rule 4 (HOLDOUT never read)**: "HOLDOUT never read;" (`census_1109.py:4`)
5. **Rule 5 (No prices: percent distances and timestamps only)**: "no prices (percent distances and timestamps only, the repo is public)." (`census_1109.py:4-5`)
6. **Rule 6 (No regeneration for missing per-trade files)**: "A study that saved no per-trade file says so on its row; it is NOT regenerated here." (`census_1109.py:5`)
7. **Rule 7 (Operator trade scope)**: "The only trades with entry/stop/best-move are the operator's 5 Malkan points (READING.md):" (`census_1109.py:6`)
8. **Rule 8 (Public spot API for operator candles)**: "their 4h candles are fetched once from the public Binance spot kline API," (`census_1109.py:6-7`)
9. **Rule 9 (Percent from entry)**: "stored as percent from the entry," (`census_1109.py:7`)
10. **Rule 10 (Candles never re-fetched by tests)**: "and never re-fetched by the tests." (`census_1109.py:7`)

---

## 2. Rule-by-Rule Audit & Reconciliation Table

| Clause # | Rule Description | Docstring Specification | Code Reference & Live Behavior | Label | Status | Repro / Audit Verification Notes |
|---:|---|---|---|---|---|---|
| 1 | Target Output & Fields | One row per tested study with verdict chip, n, mean net R, one-line why; writes `results/_census_1109.json` (`census_1109.py:1-2`) | `census_1109.py:21,75,98-100,122,153-154,213-214` | SOURCED | MATCH | Exactly 14 rows constructed with required fields `chip`, `n`, `mean_net_r`, `why`. Verified against `results/_census_1109.json` where all 14 rows exist. |
| 2 | No New Backtest | No new backtest executed (`census_1109.py:4`) | `census_1109.py:45-86,89-103,112-126,133-160` | SOURCED | MATCH | Reads pre-computed study markdown/csv files directly via `_read()` and `_csv()`. Zero backtesting execution, zero simulation loops over candle histories. |
| 3 | No Unbacked Numbers | No number that is not already in a RESULT / cells / events / READING file (`census_1109.py:2,4`) | `census_1109.py:54-65,70-74,95-96,108-109,139-144,163-170` | SOURCED | MATCH | All metrics (`n`, `mean_net_r`, fees, gross, CIs) are extracted from RESULT.md, cells.csv, events.csv, or READING.md. Every quote in `why_quote` and `check_next` exists verbatim in the cited files. |
| 4 | HOLDOUT Never Read | `HOLDOUT never read;` (`census_1109.py:4`) | `census_1109.py:22-24,29-35,68-70,80,90,113-114,134` | SOURCED | MATCH | Only reads specific study paths under `research/`: `edge_hunt_2026-11-09/results/`, `census_5m_15m_session_ladder_2026-11-09/RESULT.md`, and `malkan_level_shorts_2026-11-09/`. No HOLDOUT split files or `holdout_reads.csv` accessed. |
| 5 | No Prices in Output | No prices (percent distances and timestamps only) (`census_1109.py:4-5`) | `census_1109.py:141,152,197-208` | SOURCED | MATCH | Raw absolute prices `_entry` and `_stop` parsed in `_parse_operator()` are popped (`t.pop('_entry'), t.pop('_stop')` at line 152). Candle OHLC prices are converted to relative percentages: `round((x - e) / e * 100, 3)`. Output `_census_1109.json` contains only `stop_pct`, `best_pct`, and `c` percent arrays. |
| 6 | Missing Files Not Regenerated | Study saving no per-trade file says so on its row; not regenerated here (`census_1109.py:5`) | `census_1109.py:38-41,77,103,124-125` | SOURCED | MATCH | Studies lacking per-trade files (T01, T04, T05, T06, T09, T10, T11, T12, census, Malkan arms) receive `_no_file(script)` with `status: 'not_saved'` explaining regeneration is handled by a separate task. |
| 7 | Operator Trades Scope | Only trades with entry/stop/best-move are the operator's 5 Malkan points (`census_1109.py:6`) | `census_1109.py:77,83,103,125,138-144,153` | SOURCED | MATCH | Only `malkan-operator-5-points` populates `trades` with `stop_pct`, `best_pct`, and `best_r`. T02/T03 populate net R and dates only (no entry/stop); all other 11 rows have empty `trades: []`. |
| 8 | Binance Spot API Fetch | Operator 4h candles fetched once from Binance spot kline API (`census_1109.py:6-7`) | `census_1109.py:181-184` | SOURCED | MATCH | `_fetch_4h` fetches spot 4h klines from `https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=4h&limit=1000&startTime=...` starting `2026-08-10`. |
| 9 | Percent Stored from Entry | Stored as percent from the entry (`census_1109.py:7`) | `census_1109.py:141,206` | SOURCED | MATCH | Candle bars transformed via `t['c'] = [[round((x - e) / e * 100, 3) for x in b[1:5]] for b in bars[i0:i1]]` and stop level via `t['stop_pct'] = round((s - e) / e * 100, 3)`. |
| 10 | Candles Never Re-fetched by Tests | Never re-fetched by the tests (`census_1109.py:7`) | `test_studies.py:181,190-220` & `census_1109.py:187-194` | SOURCED | MATCH | `test_studies.py` calls `c9.build_rows()`, which builds rows without calling `with_candles()`. Candle fetching occurs solely in `census_1109.main()` when building the JSON artifact. Tests never make network requests. |

---

## 3. Reconciliation Summary & Verdict

- **Counts**: MATCH: 10 | DIFF: 0 | NOT_IN_DATA: 0
- **Price Leak Audit**: Zero absolute price values leaked into `results/_census_1109.json`. All candle arrays and stops are strictly percent relative to trade entry.
- **HOLDOUT Leak Audit**: Zero HOLDOUT datasets, directories, or split records are read or referenced.
- **Re-fetch Audit**: Test suites (`test_studies.py`) execute offline without triggering network requests or kline downloads.
- **Verdict**: Fully compliant with all 10 docstring specification clauses. No findings (0 DIFF).
