# Parameter Labels Audit: wavetrend

Audit of numeric parameter defaults in `MyTradingSys/backtest/layers/wavetrend/`.

## Parameters

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `N1` (channel length) | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `10` | `SOURCED` | LazyBear's WaveTrend Oscillator (TradingView scripts 2KE8wTuF / jFQn4jYZ, Crosses:14-21); `FORMULAS.md` s20 |
| `N2` (average length) | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `21` | `SOURCED` | LazyBear's WaveTrend Oscillator (Crosses:14-21); `FORMULAS.md` s20 |
| `SMA_N` (signal line length) | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `4` | `SOURCED` | LazyBear's WaveTrend Oscillator (Crosses:14-21); `FORMULAS.md` s20 |
| `K` (multiplier constant) | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:16` | `0.015` | `SOURCED` | Lambert's Commodity Channel Index (CCI) constant adopted in LazyBear's formula (Crosses:14-21); `FORMULAS.md` s20 |
| `OB1` (extreme overbought/oversold) | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:17` | `60.0` | `SOURCED` | LazyBear's WaveTrend second overbought level `ob2 = 60.0`, `os2 = -60.0` (Crosses:9-12); `FORMULAS.md` s20 |
| `OB2` (outer overbought/oversold) | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:17` | `53.0` | `SOURCED` | LazyBear's WaveTrend first overbought level `ob1 = 53.0`, `os1 = -53.0` (Crosses:9-12); `FORMULAS.md` s20 |
| `WARMUP` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:18` | `200` | `OURS` | EMA stabilization warm-up suppression mask: `research/wavetrend_2026-10-17/PARITY_CONTRACT.md` s3 |
| `D_TOL` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:19` | `1e-9` | `OURS` | Flat window zero-deviation tolerance: inline comment `# OURS: d <= D_TOL*|ap| counts as a flat window` |
| `typical price divisor` | `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:92` | `3.0` | `SOURCED` | Standard typical price calculation $\frac{H + L + C}{3}$; `FORMULAS.md` s20 |
