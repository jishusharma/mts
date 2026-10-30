# Parameter Labels Audit: session_levels

Audit of numeric parameter defaults in `MyTradingSys/backtest/layers/session_levels/`.

## Parameters

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `ASIA_END_MIN` | `MyTradingSys/backtest/layers/session_levels/session_levels.py:29` | `480` | `OPERATOR-HYPOTHESIS` | 08:00 UTC (480 min). Docstring: `Parameters, ALL NO-SOURCE (placeholders fixed before the run, not tuned): sessions in UTC (Asia 00:00-08:00, EU 08:00-14:00)` |
| `US_OPEN_MIN` | `MyTradingSys/backtest/layers/session_levels/session_levels.py:30` | `840` | `OPERATOR-HYPOTHESIS` | 14:00 UTC (840 min). Docstring: `US open 14:00 UTC... Tom's only related words (Of_wlv3xaZo:7, QClPWDJ-BrU:7) name no clock, threshold or probability` |
| `FAIL_WINDOW_MIN` | `MyTradingSys/backtest/layers/session_levels/session_levels.py:31` | `60` | `OURS` | Fixed 60-minute window for close-back failure detection; NO-SOURCE engineering choice |
| `MIN_PREV_BARS` | `MyTradingSys/backtest/layers/session_levels/session_levels.py:32` | `1400` | `OURS` | Minimum 1m bars required to qualify previous day as complete (out of 1440 possible) |
| `FEE` | `MyTradingSys/backtest/layers/session_levels/session_levels.py:33` | `0.0005` | `SOURCED` | Deribit exchange contract taker fee rate: inline comment `# fees.py DERIBIT_TAKER per side` |
| `MIN_EVENTS` | `MyTradingSys/backtest/layers/session_levels/run_session_levels.py:19` | `300` | `OPERATOR-HYPOTHESIS` | T087 specification: docstring `fewer than MIN_EVENTS (300) events in a cell = 'insufficient n'` |
| `T_MIN` | `MyTradingSys/backtest/layers/session_levels/run_session_levels.py:20` | `2.0` | `OURS` | Fixed statistical t-ratio threshold for edge candidacy |
| `MIN_MS` | `MyTradingSys/backtest/layers/session_levels/session_levels.py:27` | `60000` | `SOURCED` | Standard millisecond constant for 1 minute |
| `DAY_MS` | `MyTradingSys/backtest/layers/session_levels/session_levels.py:28` | `86400000` | `SOURCED` | Standard millisecond constant for 1 day |
