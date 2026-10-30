# Parameter Labels Audit: trendlines

Audit of numeric parameter defaults in `MyTradingSys/backtest/layers/trendlines/`.

## Parameters

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `ATR_LEN` | `MyTradingSys/backtest/layers/trendlines/trendline_core.py:27` | `14` | `SOURCED` | Standard Wilder ATR length 14; `FORMULAS.md` s12 |
| `VOL_LEN` | `MyTradingSys/backtest/layers/trendlines/trendline_core.py:28` | `20` | `OURS` | Contract E4 volume baseline lookback window |
| `PEN_TOL` | `MyTradingSys/backtest/layers/trendlines/trendline_core.py:29` | `0.10` | `OURS` | Contract L6 / E7 penetration tolerance ($0.10 \times \text{ATR}_b$) |
| `TOUCH_TOL` | `MyTradingSys/backtest/layers/trendlines/trendline_core.py:30` | `0.25` | `OURS` | Contract E5, L7, E3, B6 touch tolerance ($0.25 \times \text{ATR}_b$) |
| `RESET_DIST` | `MyTradingSys/backtest/layers/trendlines/trendline_core.py:31` | `1.0` | `OURS` | Contract E6 episode reset distance ($1.0 \times \text{ATR}_b$) |
| `RETEST_WINDOW` | `MyTradingSys/backtest/layers/trendlines/trendline_core.py:32` | `20` | `OURS` | Contract B6 retest bar evaluation window |
| `k` | `MyTradingSys/backtest/layers/trendlines/trendline_core.py:77` | `3` | `OURS` | Contract P1 fractal half-width ($2k+1 = 7$ bar pivot window) |
| `max_age` | `MyTradingSys/backtest/layers/trendlines/trendline_core.py:77` | `500` | `OURS` | Contract maximum bar age before line retirement |
| `min_spacing` | `MyTradingSys/backtest/layers/trendlines/trendline_core.py:78` | `10` | `OURS` | Contract minimum bar spacing between anchors $A$ and $B$ |
| `max_spacing` | `MyTradingSys/backtest/layers/trendlines/trendline_core.py:78` | `200` | `OURS` | Contract maximum bar spacing between anchors $A$ and $B$ |
| `volume surge ratio` | `MyTradingSys/backtest/layers/trendlines/trendline_core.py:241` | `2.0` | `OURS` | Contract E4 anchor volume surge threshold ($2.0 \times \text{mean}$) |
