# Parameter Labels Audit: timeframe

Audit of numeric parameter defaults and timeframe specifications in `MyTradingSys/backtest/layers/timeframe/`.

## Parameters

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `1m` | `MyTradingSys/backtest/layers/timeframe/registry.json:7` | `60s` | `SOURCED` | Standard base candlestick period (60 seconds) |
| `2m` | `MyTradingSys/backtest/layers/timeframe/registry.json:8` | `120s` | `SOURCED` | Standard candlestick period (120 seconds) |
| `3m` | `MyTradingSys/backtest/layers/timeframe/registry.json:9` | `180s` | `SOURCED` | Standard candlestick period (180 seconds) |
| `4m` | `MyTradingSys/backtest/layers/timeframe/registry.json:10` | `240s` | `SOURCED` | Standard candlestick period (240 seconds) |
| `5m` | `MyTradingSys/backtest/layers/timeframe/registry.json:11` | `300s` | `SOURCED` | Standard candlestick period (300 seconds) |
| `10m` | `MyTradingSys/backtest/layers/timeframe/registry.json:12` | `600s` | `SOURCED` | Standard candlestick period (600 seconds) |
| `15m` | `MyTradingSys/backtest/layers/timeframe/registry.json:13` | `900s` | `SOURCED` | Standard candlestick period (900 seconds) |
| `30m` | `MyTradingSys/backtest/layers/timeframe/registry.json:14` | `1800s` | `SOURCED` | Standard candlestick period (1800 seconds) |
| `1h` | `MyTradingSys/backtest/layers/timeframe/registry.json:15` | `3600s` | `SOURCED` | Standard hourly candlestick period (3600 seconds) |
| `2h` | `MyTradingSys/backtest/layers/timeframe/registry.json:16` | `7200s` | `SOURCED` | Standard 2-hour candlestick period (7200 seconds) |
| `3h` | `MyTradingSys/backtest/layers/timeframe/registry.json:17` | `10800s` | `SOURCED` | Standard 3-hour candlestick period (10800 seconds) |
| `4h` | `MyTradingSys/backtest/layers/timeframe/registry.json:18` | `14400s` | `SOURCED` | Standard 4-hour candlestick period (14400 seconds) |
| `6h` | `MyTradingSys/backtest/layers/timeframe/registry.json:19` | `21600s` | `SOURCED` | Standard 6-hour candlestick period (21600 seconds) |
| `7h` (day_reset) | `MyTradingSys/backtest/layers/timeframe/registry.json:20` | `25200s` | `OPERATOR-HYPOTHESIS` | Flagged explicitly: `NO-SOURCE anchor (T090 2026-10-09: no source for 00:00 UTC on crypto... restarts at 00:00 UTC each day... 00/07/14/21 then a 3h stub)` |
| `7h_epoch` | `MyTradingSys/backtest/layers/timeframe/registry.json:21` | `25200s` | `OPERATOR-HYPOTHESIS` | Flagged explicitly: `NO-SOURCE anchor (T090: nobody cites epoch alignment for 7h): epoch-aligned, drifts 3h against the UTC day each day` |
| `8h` | `MyTradingSys/backtest/layers/timeframe/registry.json:22` | `28800s` | `SOURCED` | Standard 8-hour candlestick period (28800 seconds) matching exchange funding cycles |
| `12h` | `MyTradingSys/backtest/layers/timeframe/registry.json:23` | `43200s` | `SOURCED` | Standard 12-hour candlestick period (43200 seconds) |
| `1d` | `MyTradingSys/backtest/layers/timeframe/registry.json:24` | `1 day` | `SOURCED` | Standard UTC daily bar anchored to `1970-01-01` |
| `2d` | `MyTradingSys/backtest/layers/timeframe/registry.json:25` | `2 days` | `OURS` | Multi-day custom bar anchored to `1970-01-01` |
| `3d` | `MyTradingSys/backtest/layers/timeframe/registry.json:26` | `3 days` | `OURS` | Multi-day custom bar anchored to `1970-01-01` |
| `5d` | `MyTradingSys/backtest/layers/timeframe/registry.json:27` | `5 days` | `OURS` | Multi-day custom bar anchored to `1970-01-01` |
| `1w` | `MyTradingSys/backtest/layers/timeframe/registry.json:28` | `1 week` | `SOURCED` | ISO 8601 standard weekly bar opening Monday 00:00 UTC |
| `1M` | `MyTradingSys/backtest/layers/timeframe/registry.json:29` | `1 month` | `SOURCED` | Standard Gregorian calendar monthly bar opening on 1st of month 00:00 UTC |
| `epoch_day % 7 == 4` | `MyTradingSys/backtest/layers/timeframe/tf_resample.py:48` | `4` | `SOURCED` | 1970-01-01 was Thursday (day index 4 relative to Monday 0) |
| `expected week minutes` | `MyTradingSys/backtest/layers/timeframe/tf_resample.py:139` | `10080` | `SOURCED` | Exact minutes in a 7-day week ($7 \times 24 \times 60$) |
| `expected day minutes` | `MyTradingSys/backtest/layers/timeframe/tf_resample.py:137` | `1440` | `SOURCED` | Exact minutes in a 24-hour day ($24 \times 60$) |
| `compare_month tolerance` | `MyTradingSys/backtest/layers/timeframe/tf_realdata_gate.py:34` | `1e-6` | `OURS` | Relative numerical comparison tolerance for OHLCV verification |
