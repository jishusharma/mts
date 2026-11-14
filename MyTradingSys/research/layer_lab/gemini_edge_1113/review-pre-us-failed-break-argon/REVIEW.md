VERDICT: UNVERIFIABLE (ledger-derived metrics MATCH; raw-data metrics and regeneration UNVERIFIABLE without `F:/MTS/data/tom_raw`)

# Blind Review: `MyTradingSys/research/pre_us_failed_break_10sym_2026-11`

## 1. Headline Numbers Recount

Recounted from `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/ledger.csv` and `per_symbol.csv` against `RESULT.md` and `analysis.json`. `F:/MTS/data/tom_raw` is not present on this machine, so raw-data-dependent metrics (`bh_mdd_pct`, `regime_mix`, and regenerating `ledger.csv` from 1m klines) cannot be independently verified.

| Claim | Claimed Value | Recounted Value | Status | Source |
|---|---|---|---|---|
| Pooled `n` | 1393 | 1393 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:12`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:2`, `ledger.csv` |
| Mean net bps of K | -2.47 | -2.467156 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:12`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:3`, `ledger.csv` |
| SE (day-clustered) | 4.39 | 4.391812 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:12`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:4`, `ledger.csv` |
| `t` (day-clustered) | -0.56 | -0.561763 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:12`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:5`, `ledger.csv` |
| 95% CI | -11.08 .. +6.14 | [-11.0751, 6.1408] | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:12`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:9-12`, `ledger.csv` |
| SE plain / t plain | 3.21 / -0.77 | 3.214786 / -0.767440 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:12`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:6-7`, `ledger.csv` |
| Measured `sd` | 119.99 | 119.985186 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:12`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:8`, `ledger.csv` |
| Time-cap days / sum | 1270 / -16,400 bps | 1270 / -16399.80 bps | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:19`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:18-19`, `ledger.csv` |
| Target days / sum | 123 / +12,963 bps | 123 / +12963.05 bps | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:19`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:16-17`, `ledger.csv` |
| MDD of cumulative net (% of K) | 97.9 | 97.9307 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:20`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:20`, `ledger.csv` |
| BTC buy-and-hold MDD (%) | 66.9 | — | UNVERIFIABLE | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:20`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:21` (`F:/MTS/data/tom_raw` missing) |
| Regime mix (130 weeks) | bull 25 (19%), bear 0 (0%), range 105 (81%) | — | UNVERIFIABLE | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:7`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:28` (`F:/MTS/data/tom_raw` missing) |
| Win rate / mean winner / mean loser | 60.7% / +45.96 / -77.36 | 0.607322 / +45.9584 / -77.3631 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:21`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:13-15`, `ledger.csv` |
| MAE % of K (p50/p90/p99/max) | 0.21 / 1.87 / 6.22 / 22.25 | 0.2063 / 1.8680 / 6.2187 / 22.2491 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:22`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:22-27`, `ledger.csv` |
| Tranches filled 1/2/3/4 | 553 / 310 / 190 / 340 | 553 / 310 / 190 / 340 | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:23`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/analysis.json:30-35`, `ledger.csv` |
| Per-symbol `n`, `mean`, `sd`, `win`, `timecap`, `sum_bps` (10 symbols) | See `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:28-37` | All 10 symbols match to 2 d.p. | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:28-37`, `per_symbol.csv`, `ledger.csv` |
| By year (`2022`/`2023`/`2024` n & mean) | 552 (+3.64) / 573 (-8.29) / 268 (-2.59) | 552 (+3.64) / 573 (-8.29) / 268 (-2.59) | MATCH | `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/RESULT.md:39`, `ledger.csv` |

## 2. Look-Ahead Hunt

No look-ahead bias found in `run_10sym.py` or `analyze.py`:
- **Hourly ATR (`atr_at`, `atr_b`)**: `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:123-126` and `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:166-167` use `atr[k]` only when `m % 60 == 59` (hour `k` closed) and `atr[k - 1]` otherwise. Entry is at `e = t + 1` (`MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:197-199`).
- **PDH (`self.h[d - 1].max()`)**: `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:170` uses previous UTC day `d - 1`.
- **ASH (`ash`)**: `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:171-178` uses `pre[ms - 1]` (highs strictly before break bar `b`) with `first[ms - 1] <= ms - 60`.
- **Swing High / Low (`swing_hi`, `swing_lo`)**: `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:106-111` requires `H[k] > H[k-1]` and `H[k] > H[k+1]`; `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:130, 136` sets `kmax = (m + 1) // 60 + d * 24 - 2`, ensuring 2h confirmation before use.
- **Support (`support(d, t)`)**: `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:184-192` uses `d - 1` low, `self.l[d][:t + 1].min()` (up to signal bar `t`, before entry `e = t + 1`), and `swing_lo(d, t)`.
- **Simulation (`simulate(d, t)`)**: `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:197-217` enters at `o[t + 1]`, steps `j` from `e + 1` to `W1 - 1`, and exits at `o[W1]` on time-cap.

## 3. Fee & Slippage Hunt

No fee or slippage errors found in `run_10sym.py`:
- **Fee model**: `FEE_LEG = fees.FEES_ALL_TAKER["entry"]` (`MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:34`, SOURCED `fees.py` regime A all-taker, 5 bps/leg) + `ADVERSE_PX = 2 / 1e4` (`MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:35`, OURS 2 bps slippage/leg) = `LEG_COST` 7 bps/leg, 14 bps round-trip (`MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:36`).
- **Round-trip & side**: `rt_drag = 2 * LEG_COST * TRANCHE * len(fills)` (`MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:219`) applies 2 legs (entry + exit) per filled tranche (`TRANCHE = 0.25`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:38`), subtracted from `gross` (`net = gross - rt_drag - fund`, `MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:221`).
- **Funding**: `SETTLE_DRAG = 1 / 1e4` (`MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:37`, OURS flat 1 bp) applied once to `fund_w` held across `j == 480` (08:00 UTC) when `e < 480 and exit_j >= 480` (`MyTradingSys/research/pre_us_failed_break_10sym_2026-11/run_10sym.py:206-207, 220`).
