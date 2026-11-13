AGREE

Blind re-derivation of `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13` from `PRE_REG.md`, `cells.csv`, `summary.json`, and `MyTradingSys/backtest/fees.py`, compared against `REPORT.md`.

## 1. Frozen Pass/Fail Rule (`PRE_REG.md`)

- **BH family / cells** (`MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/PRE_REG.md:33` SOURCED: `"Cells: 3 TF x 4 exits = 12 cells (the BH family)."`): `TF in {4h, 8h, 12h}` x `exit in {1R, 2R, 3R, time}`.
- **Decision split** (`MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/PRE_REG.md:39` SOURCED: `"VALIDATION 2024-07-01..2025-06-30... The verdict is read on VALIDATION."`).
- **Cell PASS criteria** (`MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/PRE_REG.md:46` SOURCED: `"VALIDATION n >= 30, VALIDATION mean fee-net R > 0, bootstrap 95% CI lower bound > 0, P1 placebo p <= 0.05, BH-10% significant, and the VALIDATION split not ONE-REGIME."`):
  1. `n_VAL >= 30` (and 95% CI computed only at `n >= 30`, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/PRE_REG.md:42`)
  2. `mean_r_VAL > 0`
  3. `lo_VAL > 0`
  4. `p1_p_VAL <= 0.05`
  5. `BH-10%` significant across the 12 `VAL` p-values (`MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/PRE_REG.md:45`)
  6. `VAL` not `ONE-REGIME` (no regime > `0.85` share of days, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/PRE_REG.md:14`)
- **Overall verdict** (`MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/PRE_REG.md:47` SOURCED: `"Overall verdict: PASS if any cell is PASS; FAIL if none and at least one cell has VALIDATION n >= 30; UNDERPOWERED if every cell has n < 30."`).
- **Round-trip cost** (`MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/PRE_REG.md:36` SOURCED: `"Round trip = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13"`).

## 2. Independent Recomputation (`cells.csv`, `summary.json`, `fees.py`)

Raw kline cache `runtime_data/edge4-rsi-4h-le12-1113` is **not present** on this machine (`Test-Path runtime_data/edge4-rsi-4h-le12-1113` -> `False`), so raw bar-by-bar simulation is `UNVERIFIABLE` here. All cell-level arithmetic, pooled `ALL` aggregations, `BH-10%`, and verdict logic are recomputed below from `cells.csv` and `summary.json`:

- **Cost formula** (OURS arithmetic on SOURCED constants from `MyTradingSys/backtest/fees.py`):
  `2 * 0.0005 + 0.0002 = 0.0012` (matches `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/summary.json:3` `"cost_rt": 0.0012000000000000001`).
- **Pooled `ALL` formula** (OURS):
  `n_ALL = n_DEV + n_VAL + n_RECENT`; `mean_r_ALL = (n_DEV * mean_r_DEV + n_VAL * mean_r_VAL + n_RECENT * mean_r_RECENT) / n_ALL`.
  Recomputed for all 12 cells from `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/cells.csv:2-49`; max `|recomputed - cells.csv| = 5.55e-17` (exact float match):
  - `4h`: `n_ALL = 19 + 12 + 4 = 35`; `mean_r_ALL = 0.165676` (`1R`), `0.245242` (`2R`), `0.235270` (`3R`), `0.096914` (`time`).
  - `8h`: `n_ALL = 12 + 0 + 6 = 18`; `mean_r_ALL = -0.152391` (`1R`), `-0.023780` (`2R`), `0.142887` (`3R`), `-0.046886` (`time`).
  - `12h`: `n_ALL = 3 + 1 + 3 = 7`; `mean_r_ALL = 0.028039` (`1R`), `0.016801` (`2R`), `0.016801` (`3R`), `0.016801` (`time`).
- **BH-10% over 12 `VAL` p-values** (OURS formula: sort `p_i` ascending for `i = 1..12`, find largest `k` with `p_(k) <= 0.10 * k / 12`):
  - `k=1`: `4h 1R` `p = 3.34e-70 <= 0.008333` (`True`)
  - `k=2`: `4h 2R` `p = 9.01e-09 <= 0.016667` (`True`)
  - `k=3`: `4h time` `p = 2.53e-06 <= 0.025000` (`True`)
  - `k=4`: `4h 3R` `p = 6.04e-06 <= 0.033333` (`True`)
  - `k=5..12`: `8h` (`p = 1.0`) and `12h` (`p = 1.0`) `> 0.10 * k / 12` (`False`)
  - Result: 4 `4h` cells are BH-10% significant (`True`), 8 others are `False` (`MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/cells.csv:3-47`).
- **PASS / Verdict call** (OURS):
  - Max `n_VAL` across all 12 cells is `12` (`4h` cells, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/cells.csv:3-15`), while `8h` has `n_VAL = 0` and `12h` has `n_VAL = 1`.
  - Every cell has `n_VAL < 30`, so `0` cells have a 95% CI computed in `VAL` and `0` of `12` cells PASS (`MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/PRE_REG.md:46`).
  - Regime shares in `VAL` (`MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/summary.json:941-945`) are `[0.6164, 0.1096, 0.2740]` (max `0.6164 <= 0.85`, not `ONE-REGIME`).
  - By `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/PRE_REG.md:47`, since every cell has `n_VAL < 30`, the overall verdict is **UNDERPOWERED**.

## 3. Claim Comparison vs `REPORT.md`

| Claim | Claimed (`REPORT.md`) | Recomputed | Status | Source (`file:line`) |
|---|---|---|---|---|
| Overall verdict | `UNDERPOWERED`, `0 of 12 cells PASS` | `UNDERPOWERED`, `0/12 PASS` (max `n_VAL = 12 < 30`) | MATCH | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/REPORT.md:3`, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/summary.json:2`, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/summary.json:6`, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/PRE_REG.md:47` |
| Largest-n VALIDATION cell (`4h 3R`) | `n=12`, `mean 0.814 R`, `CI [n/a, n/a]`, `P1 p=0.029`, `BH=True` | `n=12`, `mean_r=0.813520`, `CI=nan`, `p1_p=0.028971`, `BH=True` | MATCH | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/REPORT.md:3`, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/REPORT.md:35`, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/cells.csv:11` |
| Round-trip cost | `0.0012` (`2 x BINANCE_TAKER + SLIPPAGE_RT_S13`) | `2 * 0.0005 + 0.0002 = 0.0012` | MATCH | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/REPORT.md:7`, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/summary.json:3`, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/PRE_REG.md:36` |
| VAL regime mix | `bull 62% / bear 11% / range 27%` | `0.6164 / 0.1096 / 0.2740` (not `ONE-REGIME`) | MATCH | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/REPORT.md:5`, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/summary.json:941-945` |
| Pooled `4h 2R` (`ALL`) | `n=35`, `mean net R = 0.245`, `CI [-0.298, 0.667]`, `win 60.0%` | `n=19+12+4=35`, `mean_r=0.245242`, `win=0.6000` (CI from `cells.csv`) | MATCH | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/REPORT.md:13`, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/cells.csv:6-9` |
| Pooled `8h 1R` (`ALL`) | `n=18`, `mean net R = -0.152`, `win 44.4%` | `n=12+0+6=18`, `mean_r=-0.152391`, `win=0.4444` | MATCH | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/REPORT.md:16`, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/cells.csv:18-21` |
| Pooled `12h 1R` (`ALL`) | `n=7`, `mean net R = 0.028`, `win 71.4%` | `n=3+1+3=7`, `mean_r=0.028039`, `win=0.7143` | MATCH | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/REPORT.md:20`, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/cells.csv:34-37` |
| BH-10% significance (`VAL`) | `yes` for all 4 `4h` cells; `no` for all 8 `8h`/`12h` cells | `True` for `4h {1R,2R,3R,time}`; `False` for `8h`/`12h` | MATCH | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/REPORT.md:29-62`, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/cells.csv:3-47` |
| Signals per coin sums (`4h/8h/12h`) | `4h=39`, `8h=18`, `12h=7` (sum of coin rows) | `4h=39`, `8h=18`, `12h=7` | MATCH | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/REPORT.md:84-103`, `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/summary.json:873-934` |
| BTC alone (`4h/8h/12h` mean net R) | `4h: n=8 (0.398.. -0.229)`; `8h: n=3 (-1.128)`; `12h: n=2 (-1.067)` | Not in `cells.csv`/`summary.json`; `runtime_data/edge4-rsi-4h-le12-1113/` absent | UNVERIFIABLE | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/REPORT.md:65-79` |
