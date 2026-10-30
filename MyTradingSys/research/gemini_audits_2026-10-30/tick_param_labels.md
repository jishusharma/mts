# Parameter Labels Audit: tick

Audit of numeric parameter defaults across `MyTradingSys/backtest/layers/tick/`.

## Parameters

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `timeframes` | `MyTradingSys/backtest/layers/tick/tick_extremes.py:214` | `(1, 2, 3, 5, 10, 15)` | `OURS` | T040 decision "s6": tick/delta aggregation timeframes in minutes |
| `top_n` | `MyTradingSys/backtest/layers/tick/tick_extremes.py:149, 214` | `20` | `OURS` | Extreme ranking table depth; internal engineering cutoff |
| `factor` (gap tier multiplier) | `MyTradingSys/backtest/layers/tick/tick_extremes.py:108` | `1.5` | `OURS` | Gap distribution outlier factor: `gaps[i] > factor * median_gap` |
| `session_tag Asian` | `MyTradingSys/backtest/layers/tick/tick_extremes.py:87` | `0..480` | `OURS` | 00:00 to 08:00 UTC session definition |
| `session_tag European` | `MyTradingSys/backtest/layers/tick/tick_extremes.py:89` | `480..780` | `OURS` | 08:00 to 13:00 UTC disjoint European session window |
| `session_tag Overlap` | `MyTradingSys/backtest/layers/tick/tick_extremes.py:91` | `780..990` | `OURS` | 13:00 to 16:30 UTC EU/US overlap window |
| `session_tag American` | `MyTradingSys/backtest/layers/tick/tick_extremes.py:93` | `990..1260` | `OURS` | 16:30 to 21:00 UTC American session window |
| `in_funding_window window_min` | `MyTradingSys/backtest/layers/tick/tick_extremes.py:98` | `30` | `OURS` | Window around funding reset (minutes) |
| `funding resets` | `MyTradingSys/backtest/layers/tick/tick_extremes.py:101` | `[0, 480, 960]` | `SOURCED` | Binance perpetual contract 8-hour funding reset schedule (00:00, 08:00, 16:00 UTC) |
| `cooldown_ms` | `MyTradingSys/backtest/layers/tick/tick_flagger.py:142` | `1800000` | `OURS` | 30 minutes (1,800,000 ms) flag emission cooldown |
| `oi resample base period` | `MyTradingSys/backtest/layers/tick/tick_oi_extremes.py:16` | `5` | `SOURCED` | Binance exchange 5-minute native open interest data interval |
| `oi timeframes` | `MyTradingSys/backtest/layers/tick/tick_oi_extremes.py:156` | `(5, 10, 15)` | `OURS` | Multiples of 5 minutes for OI extreme evaluation |
| `oi top_n` | `MyTradingSys/backtest/layers/tick/tick_oi_extremes.py:156` | `20` | `OURS` | Open interest extreme ranking depth |
| `oi factor` | `MyTradingSys/backtest/layers/tick/tick_oi_extremes.py:90` | `1.5` | `OURS` | Gap tier multiplier for OI deltas |
| `oi window_min` | `MyTradingSys/backtest/layers/tick/tick_oi_extremes.py:80` | `30` | `OURS` | Window around funding reset for OI deltas |
| `orderflow threshold days` | `MyTradingSys/backtest/layers/tick/build_tiers.py:72` | `30` | `OURS` | Minimum days threshold (`thr_days >= 30`) for orderflow aggregation |
