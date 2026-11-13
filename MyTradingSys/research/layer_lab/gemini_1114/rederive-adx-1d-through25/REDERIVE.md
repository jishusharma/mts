AGREE

Blind re-derivation of `MyTradingSys/research/adx_1d_through25_2026-11-13` from `MyTradingSys/research/adx_1d_through25_2026-11-13/PRE_REG.md` and `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json`, compared against `MyTradingSys/research/adx_1d_through25_2026-11-13/REPORT.md`. Note: raw Bybit 1d klines (`MyTradingSys/market_data/klines/`, git-ignored per `MyTradingSys/research/adx_1d_through25_2026-11-13/PRE_REG.md:16`) are not present on this machine, so bar-level OHLCV recomputation is `UNVERIFIABLE`; all verdict and summary arithmetic from `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json` and `MyTradingSys/research/adx_1d_through25_2026-11-13/REPORT.md` internal cell sums `MATCH`.

## 1. Frozen Pass/Fail Rule (`PRE_REG.md` only)

- **Decision cell**: VALIDATION split (`2024-07-01..2025-06-30`, SOURCED `"VALIDATION 2024-07-01..2025-06-30"` at `MyTradingSys/research/adx_1d_through25_2026-11-13/PRE_REG.md:23`), pooled across all 5 symbols (`BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `LINKUSDT`, `LTCUSDT`) and both sides; primary hold `h = 6` for Rule A, single exit rule for Rule B (`MyTradingSys/research/adx_1d_through25_2026-11-13/PRE_REG.md:28`, `MyTradingSys/research/adx_1d_through25_2026-11-13/PRE_REG.md:51`).
- **Cost**: `0.0010` (10 bps round trip) subtracted from gross return (`net = gross - 0.0010`, SOURCED `"net = gross - 0.0010 (10 bps round trip)"` at `MyTradingSys/research/adx_1d_through25_2026-11-13/PRE_REG.md:27`, `"Fee | 0.0010 round trip"` at `MyTradingSys/research/adx_1d_through25_2026-11-13/PRE_REG.md:43`; matches `fees.BINANCE_TAKER * 2 = 0.0005 * 2 = 0.0010` at `MyTradingSys/research/adx_1d_through25_2026-11-13/run_1113.py:21` and `MyTradingSys/backtest/fees.py:36`).
- **Verdict rules** (`MyTradingSys/research/adx_1d_through25_2026-11-13/PRE_REG.md:51-54`):
  - `UNDERPOWERED` if VALIDATION `n < 30`.
  - `PASS` iff ALL hold: (1) `n >= 30`, (2) 95% cluster-bootstrap CI lower bound `lo > 0`, (3) Rule A only: `h = 3` and `h = 12` point mean excess `> 0`, (4) VALIDATION not `ONE-REGIME` (`<= 85%` in one 200d-SMA regime), (5) `RECENT` does not contradict (`RECENT` mean excess `< 0` with `n >= 10`, or CI `hi < 0` with `n >= 5`).
  - `FAIL` otherwise.

## 2. Independent Arithmetic from `summary.json` & Cell Sums

From `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json`:
- **Rule A VALIDATION `h = 6` (primary)**: `n = 30` (`MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:12`), `net = -0.01961473209907453` (`-1.96%`, `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:13`), `ex = -0.017053434817843435` (`-1.71%`, `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:14`), `lo = -0.05797078317932973` (`-5.80%` / `-5.8%`, `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:15`), `hi = 0.018928227930279793` (`+1.89%` / `+1.9%`, `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:16`), `win = 0.4666666666666667` (`47%`, `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:17`).
  - Weighted-mean cross-check across the 10 VALIDATION symbol-side cells (`MyTradingSys/research/adx_1d_through25_2026-11-13/REPORT.md:16-25`, OURS arithmetic):
    - `n = 2+3+2+2+4+7+2+3+2+3 = 30`
    - `net = (2*10.43 + 3*(-4.74) + 2*(-5.38) + 2*5.74 + 4*0.50 + 7*(-7.24) + 2*0.79 + 3*(-2.17) + 2*(-4.29) + 3*(-1.35)) / 30 = -58.84 / 30 = -1.96%`
    - `ex = (2*9.37 + 3*(-3.47) + 2*(-5.33) + 2*5.89 + 4*(-0.05) + 7*(-6.49) + 2*0.19 + 3*(-1.37) + 2*(-5.05) + 3*(-0.38)) / 30 = -51.17 / 30 = -1.71%`
- **Rule A VALIDATION `h = 3` and `h = 12`**:
  - `h = 3`: `n = 30`, `net = -2.41%`, `ex = -2.23%` (`-0.022341919763065526`), CI `[-3.9%, -0.3%]`, `win = 33%` (`MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:4-9`).
  - `h = 12`: `n = 30`, `net = -0.59%`, `ex = -0.17%` (`-0.001653910117090655`), CI `[-7.7%, +6.0%]`, `win = 47%` (`MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:20-25`).
- **Rule A PASS/FAIL call**: `n = 30 >= 30` (powered), but `lo = -5.80%` is not `> 0`, and `h = 3` (`-2.23%`) and `h = 12` (`-0.17%`) excess are not both `> 0` -> **`FAIL`**.
- **Rule B VALIDATION**: `verdict_B = "UNDERPOWERED (VALIDATION n=0 < 30)"` (`MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:29`), `n = 0 < 30` -> **`UNDERPOWERED`**.
- **Reproduction check**: `repro = 33` (`MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:30`), within `34 +- 4` (`[30, 38]`, `MyTradingSys/research/adx_1d_through25_2026-11-13/PRE_REG.md:56`) -> **`OK`**.

## 3. Claim Comparison vs `REPORT.md`

| Claim | Claimed (`REPORT.md`) | Recomputed | Status | Source (`file:line`) |
|---|---|---|---|---|
| Rule A headline verdict | `FAIL: VALIDATION excess CI lower bound -5.80% not > 0; h=3/h=12 excess not both > 0` | `FAIL` (`n=30 >= 30`, `lo=-5.80% <= 0`, `h=3 ex=-2.23% <= 0`, `h=12 ex=-0.17% <= 0`) | MATCH | `MyTradingSys/research/adx_1d_through25_2026-11-13/REPORT.md:10`, `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:6`, `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:14-15`, `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:22`, `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:28`, `MyTradingSys/research/adx_1d_through25_2026-11-13/PRE_REG.md:53-54` |
| Rule A VALIDATION `h=6` pooled `n`, `net`, `ex`, CI, `win` | `n=30 net -1.96% ex -1.71% [-5.8%,+1.9%] win 47%` | `n=30`, `net=-1.96%`, `ex=-1.71%`, `[-5.8%,+1.9%]`, `win=47%` (from `summary.json`; cell sum `n=30`, `net=-1.96%`, `ex=-1.71%`) | MATCH | `MyTradingSys/research/adx_1d_through25_2026-11-13/REPORT.md:10`, `MyTradingSys/research/adx_1d_through25_2026-11-13/REPORT.md:28`, `MyTradingSys/research/adx_1d_through25_2026-11-13/REPORT.md:34`, `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:12-17` |
| Rule A VALIDATION `h=3` and `h=12` robustness | `h=3`: `n=30 net -2.41% ex -2.23% [-3.9%,-0.3%] win 33%`; `h=12`: `n=30 net -0.59% ex -0.17% [-7.7%,+6.0%] win 47%` | `h=3`: `n=30 net=-2.41% ex=-2.23% [-3.9%,-0.3%] win=33%`; `h=12`: `n=30 net=-0.59% ex=-0.17% [-7.7%,+6.0%] win=47%` | MATCH | `MyTradingSys/research/adx_1d_through25_2026-11-13/REPORT.md:33`, `MyTradingSys/research/adx_1d_through25_2026-11-13/REPORT.md:35`, `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:4-9`, `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:20-25` |
| Rule B headline verdict | `UNDERPOWERED (VALIDATION n=0 < 30)` | `UNDERPOWERED` (`n=0 < 30`) | MATCH | `MyTradingSys/research/adx_1d_through25_2026-11-13/REPORT.md:11`, `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:29`, `MyTradingSys/research/adx_1d_through25_2026-11-13/PRE_REG.md:52` |
| BTC 2017+ through-25 long reproduction check | `33 (source study 34 +-4): OK` | `33` in `[30, 38]` -> `OK` | MATCH | `MyTradingSys/research/adx_1d_through25_2026-11-13/REPORT.md:5`, `MyTradingSys/research/adx_1d_through25_2026-11-13/summary.json:30`, `MyTradingSys/research/adx_1d_through25_2026-11-13/PRE_REG.md:56` |
| Raw-kline bar-level event counts, DEV/RECENT cells, and 200d-SMA regime mix | e.g., Rule A DEV `n=124`, RECENT `n=42`; Regime mix `DEV 49%/51%`, `VALIDATION 43%/57%`, `RECENT 38%/62%` | Raw Bybit 1d klines (`MyTradingSys/market_data/klines/`) are git-ignored and absent on this machine | UNVERIFIABLE | `MyTradingSys/research/adx_1d_through25_2026-11-13/REPORT.md:3`, `MyTradingSys/research/adx_1d_through25_2026-11-13/REPORT.md:28`, `MyTradingSys/research/adx_1d_through25_2026-11-13/PRE_REG.md:16` |
