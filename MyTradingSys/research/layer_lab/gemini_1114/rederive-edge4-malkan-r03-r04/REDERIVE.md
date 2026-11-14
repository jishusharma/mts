AGREE

# Blind Re-derivation: edge4-malkan-r03-r04-2026-11-13

## 1. Frozen Pass/Fail Rule (from PRE_REG.md before reading REPORT.md)

From `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/PRE_REG.md`:
- **Decision cells** (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/PRE_REG.md:27`, OURS/SOURCED): 8 cells = 2 sides (`R03` short, `R04` long) x 2 lookbacks (`12`, `18` bars) x 2 timeframes (`1h`, `4h`).
- **Verdict split** (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/PRE_REG.md:37`, OURS): `VALIDATION` (`2024-07-01..2025-06-30` by entry bar time).
- **Round-trip cost** (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/PRE_REG.md:34`, OURS): `2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13` from `MyTradingSys/backtest/fees.py`. Using `BINANCE_TAKER = 0.0005` (`MyTradingSys/backtest/fees.py:36`, SOURCED) and `SLIPPAGE_RT_S13 = 0.0002` (`MyTradingSys/backtest/fees.py:62`, OURS), `cost_rt = 2 * 0.0005 + 0.0002 = 0.0012`.
- **Cell PASS criteria** (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/PRE_REG.md:41`, OURS): all 6 must hold in `VALIDATION`:
  1. `n >= 30`
  2. `mean fee-net R > 0`
  3. 95% cluster-bootstrap CI lower bound `> 0` (cluster = UTC day of entry, 2000 draws, seed `20261114`; `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/PRE_REG.md:38`)
  4. `placebo_p <= 0.05` (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/PRE_REG.md:39`)
  5. `BH-10%` significant over the 8 `VALIDATION` p-values (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/PRE_REG.md:40`): sort `p_(1) <= ... <= p_(8)`, reject `1..k` for largest `k` with `p_(k) <= (k / 8) * 0.10`
  6. Split not `ONE-REGIME` (`max(regime_share) <= 0.85`; `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/PRE_REG.md:12`)
- **ROBUST** (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/PRE_REG.md:41`, OURS): `PASS` and `RECENT` `n >= 30` with `RECENT` `mean net R > 0`.
- **Overall verdict** (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/PRE_REG.md:42`, OURS): `PASS` if any cell `PASS`; `FAIL` if none `PASS` and at least one cell has `n >= 30`; `UNDERPOWERED` if every cell has `n < 30`.

## 2. Independent Arithmetic from summary.json

Note on data availability: `runtime_data/edge4-malkan-r03-r04-1113/` (Bybit kline cache, git-ignored per `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/PRE_REG.md:31`) is not present on this machine, so raw trade-by-trade R re-simulation from klines is `UNVERIFIABLE` locally. All cell counts, mean net R, CIs, p-values, BH-10%, regime shares, and verdicts below are recomputed directly from `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json` and `MyTradingSys/backtest/fees.py`.

- `cost_rt = 2 * 0.0005 + 0.0002 = 0.0012` (`MyTradingSys/backtest/fees.py:36`, `MyTradingSys/backtest/fees.py:62`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:528`).
- `VALIDATION` `n` range: `min(n) = 379`, `max(n) = 1754`; all 8 cells have `n >= 30`.
- `VALIDATION` day regime shares (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:535-539`): `above = 0.616438`, `below = 0.109589`, `within = 0.273973`; `max = 0.616438 <= 0.85` -> not `ONE-REGIME`.
- `BH-10%` over the 8 `VALIDATION` p-values: smallest `p = 0.747626` (`R04 4h 12`), whereas rank-1 threshold is `(1 / 8) * 0.10 = 0.0125`. Since `0.747626 > 0.0125`, `0` cells pass `BH-10%`.
- Per-cell `VALIDATION` evaluation:
  - `R03 1h 12`: `n=1752 >= 30`, `mean_r=-0.332592 <= 0`, `lo=-0.416714 <= 0`, `placebo_p=0.953047 > 0.05`, `bh=False`, `one_regime=False` -> `FAIL` (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:28-49`)
  - `R03 1h 18`: `n=1754 >= 30`, `mean_r=-0.333837 <= 0`, `lo=-0.415230 <= 0`, `placebo_p=0.967033 > 0.05`, `bh=False`, `one_regime=False` -> `FAIL` (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:93-114`)
  - `R04 1h 12`: `n=1651 >= 30`, `mean_r=-0.319748 <= 0`, `lo=-0.404887 <= 0`, `placebo_p=0.687313 > 0.05`, `bh=False`, `one_regime=False` -> `FAIL` (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:158-179`)
  - `R04 1h 18`: `n=1652 >= 30`, `mean_r=-0.315438 <= 0`, `lo=-0.394767 <= 0`, `placebo_p=0.494505 > 0.05`, `bh=False`, `one_regime=False` -> `FAIL` (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:223-244`)
  - `R03 4h 12`: `n=379 >= 30`, `mean_r=-0.166634 <= 0`, `lo=-0.303965 <= 0`, `placebo_p=0.547453 > 0.05`, `bh=False`, `one_regime=False` -> `FAIL` (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:288-309`)
  - `R03 4h 18`: `n=379 >= 30`, `mean_r=-0.166634 <= 0`, `lo=-0.301376 <= 0`, `placebo_p=0.627373 > 0.05`, `bh=False`, `one_regime=False` -> `FAIL` (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:353-374`)
  - `R04 4h 12`: `n=383 >= 30`, `mean_r=-0.073965 <= 0`, `lo=-0.285401 <= 0`, `placebo_p=0.194805 > 0.05`, `bh=False`, `one_regime=False` -> `FAIL` (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:418-439`)
  - `R04 4h 18`: `n=382 >= 30`, `mean_r=-0.082968 <= 0`, `lo=-0.292985 <= 0`, `placebo_p=0.170829 > 0.05`, `bh=False`, `one_regime=False` -> `FAIL` (`MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:483-504`)
- Overall verdict: `0` of `8` cells `PASS`, at least one cell has `n >= 30` -> `FAIL`.

## 3. Claim Comparison vs REPORT.md

| Claim | Claimed (`REPORT.md`) | Recomputed | Status | Source (`file:line`) |
|---|---|---|---|---|
| Overall verdict | `FAIL`, `0 of 8 VALIDATION cells PASS` | `FAIL`, `0` of `8` `PASS` | MATCH | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/REPORT.md:3`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:4`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:527`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:549` |
| VALIDATION `n` range | `379..1754` | `379..1754` | MATCH | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/REPORT.md:3`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:28-504`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:546` |
| Round-trip cost | `0.0012` of entry | `2*0.0005 + 0.0002 = 0.0012` | MATCH | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/REPORT.md:3`, `MyTradingSys/backtest/fees.py:36`, `MyTradingSys/backtest/fees.py:62`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:528` |
| Day regime mix (DEV / VAL / REC) | `0.57/0.34/0.09`; `0.62/0.11/0.27`; `0.36/0.54/0.10` | `0.572/0.343/0.085`; `0.616/0.110/0.274`; `0.361/0.539/0.100` | MATCH | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/REPORT.md:5`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:529-545` |
| `R03 1h 12` VALIDATION | `n=1752`, `mean=-0.333`, `CI=[-0.417, -0.247]`, `plac_p=0.953`, `FAIL` | `n=1752`, `mean=-0.332592`, `CI=[-0.416714, -0.246846]`, `plac_p=0.953047`, `FAIL` | MATCH | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/REPORT.md:10`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:28-49` |
| `R03 1h 18` VALIDATION | `n=1754`, `mean=-0.334`, `CI=[-0.415, -0.241]`, `plac_p=0.967`, `FAIL` | `n=1754`, `mean=-0.333837`, `CI=[-0.415230, -0.240869]`, `plac_p=0.967033`, `FAIL` | MATCH | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/REPORT.md:11`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:93-114` |
| `R04 1h 12` VALIDATION | `n=1651`, `mean=-0.320`, `CI=[-0.405, -0.232]`, `plac_p=0.687`, `FAIL` | `n=1651`, `mean=-0.319748`, `CI=[-0.404887, -0.231661]`, `plac_p=0.687313`, `FAIL` | MATCH | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/REPORT.md:12`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:158-179` |
| `R04 1h 18` VALIDATION | `n=1652`, `mean=-0.315`, `CI=[-0.395, -0.236]`, `plac_p=0.495`, `FAIL` | `n=1652`, `mean=-0.315438`, `CI=[-0.394767, -0.235600]`, `plac_p=0.494505`, `FAIL` | MATCH | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/REPORT.md:13`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:223-244` |
| `R03 4h 12` VALIDATION | `n=379`, `mean=-0.167`, `CI=[-0.304, -0.017]`, `plac_p=0.547`, `FAIL` | `n=379`, `mean=-0.166634`, `CI=[-0.303965, -0.017174]`, `plac_p=0.547453`, `FAIL` | MATCH | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/REPORT.md:14`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:288-309` |
| `R03 4h 18` VALIDATION | `n=379`, `mean=-0.167`, `CI=[-0.301, -0.018]`, `plac_p=0.627`, `FAIL` | `n=379`, `mean=-0.166634`, `CI=[-0.301376, -0.018346]`, `plac_p=0.627373`, `FAIL` | MATCH | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/REPORT.md:15`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:353-374` |
| `R04 4h 12` VALIDATION | `n=383`, `mean=-0.074`, `CI=[-0.285, 0.149]`, `plac_p=0.195`, `FAIL` | `n=383`, `mean=-0.073965`, `CI=[-0.285401, 0.149039]`, `plac_p=0.194805`, `FAIL` | MATCH | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/REPORT.md:16`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:418-439` |
| `R04 4h 18` VALIDATION | `n=382`, `mean=-0.083`, `CI=[-0.293, 0.135]`, `plac_p=0.171`, `FAIL` | `n=382`, `mean=-0.082968`, `CI=[-0.292985, 0.134510]`, `plac_p=0.170829`, `FAIL` | MATCH | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/REPORT.md:17`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/summary.json:483-504` |
| Raw kline trade-level R | Generated from `runtime_data/edge4-malkan-r03-r04-1113/` | Cache not present on this machine | UNVERIFIABLE | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/PRE_REG.md:31`, `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/run_1113.py:1` |
