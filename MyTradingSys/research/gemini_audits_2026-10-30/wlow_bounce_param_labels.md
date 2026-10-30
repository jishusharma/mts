# Parameter Labels Audit: wlow_bounce

Audit of numeric parameter defaults in `MyTradingSys/backtest/layers/wlow_bounce/`.

## Parameters

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `bb_n` | `MyTradingSys/backtest/layers/wlow_bounce/detector.py:14` | `20` | `SOURCED` | Operator chart settings (Bollinger band 20, 2); `research/wlow_bounce_bbrsi60_2026-10-16/PRE_REG.md` s2 |
| `bb_k` | `MyTradingSys/backtest/layers/wlow_bounce/detector.py:14` | `2.0` | `SOURCED` | Operator chart settings (Bollinger band 20, 2); `research/wlow_bounce_bbrsi60_2026-10-16/PRE_REG.md` s2 |
| `rsi_n` | `MyTradingSys/backtest/layers/wlow_bounce/detector.py:15` | `14` | `SOURCED` | Operator chart settings (standard Wilder 14 RSI); `PRE_REG.md` s2 |
| `rsi_hi` | `MyTradingSys/backtest/layers/wlow_bounce/detector.py:16` | `60.0` | `SOURCED` | Operator explicit quote 2026-10-16: "just under the RSI 60 line"; `PRE_REG.md` s2 |
| `rsi_lo` | `MyTradingSys/backtest/layers/wlow_bounce/detector.py:17` | `52.0` | `OURS` | Judgement: chart showed 56-58, floor set 4 points below; `PRE_REG.md` s2 |
| `slope_max` | `MyTradingSys/backtest/layers/wlow_bounce/detector.py:18` | `3.0` | `OURS` | Discretization of operator "flat RSI": $|\Delta\text{RSI}| \le 3.0$ points over hold window; `PRE_REG.md` s2 |
| `band_x` | `MyTradingSys/backtest/layers/wlow_bounce/detector.py:19` | `0.005` | `OURS` | Discretization of operator "near the upper edge": $\text{close} \ge \text{upper} \times (1 - 0.5\%)$; `PRE_REG.md` s2 |
| `K` (hold window) | `MyTradingSys/backtest/layers/wlow_bounce/detector.py:20` | `4` | `OURS` | Discretization: chart showed 5-6 candles, 4 chosen to capture more events; `PRE_REG.md` s2 |
| `B` (bounce window) | `MyTradingSys/backtest/layers/wlow_bounce/detector.py:21` | `6` | `OURS` | Discretization: chart showed 2-3 candle bounce, 6 chosen as conservative upper bound; `PRE_REG.md` s2 |
| `HMAX` (max episode length) | `MyTradingSys/backtest/layers/wlow_bounce/detector.py:22` | `24` | `OURS` | Max 24 bars from break to trigger; `PRE_REG.md` s2 |
| `COOLDOWN` | `MyTradingSys/backtest/layers/wlow_bounce/detector.py:23` | `24` | `OURS` | Minimum 24 bars between consecutive episode starts; `PRE_REG.md` s2 |
| `week_mode hours` | `MyTradingSys/backtest/layers/wlow_bounce/detector.py:57, 63` | `168` | `SOURCED` | Total hourly bars in one complete 7-day week ($7 \times 24 = 168$) |
| `active_bars` | `MyTradingSys/backtest/layers/wlow_bounce/detector.py:111` | `6` | `OURS` | Active state recency horizon in closed 1h bars |
| `HOUR_MS` | `MyTradingSys/backtest/layers/wlow_bounce/detector.py:12` | `3600000` | `SOURCED` | Exact milliseconds per hour |
