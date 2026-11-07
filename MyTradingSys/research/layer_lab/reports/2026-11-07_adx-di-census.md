MATCH: 815 | DIFF: 9 | NOT_IN_DATA: 1

# Independent Re-derivation of `adx_di_2026-11/CENSUS.md` Numbers (`gpt-rederive-adx-di-census-1107`)

- **Card**: `gpt-rederive-adx-di-census-1107`
- **Worker**: `gemini-4-argon-medium` on throwaway git worktree (`F:/MTS/gq/gpt-rederive-adx-di-census-1107`)
- **Scope In Read**:
  - `MyTradingSys/research/adx_di_2026-11/CENSUS.md` (`:1-291`, `SOURCED` target report)
  - `MyTradingSys/research/adx_di_2026-11/SPEC.md` (`:1-33`, `SOURCED` study specification) and `TV_CROSSCHECK.md` (`:1-33`)
  - `MyTradingSys/backtest/layers/FORMULAS.md` (`:152-162` Section 8 `tf_resample` 2d bucket math; `:684-691` Section 30 Wilder ADX/DI `n=14` formula)
  - `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv` (`3,597` rows from `2017-01-01` to `2026-11-06`, cited at `CENSUS.md:3` and `SPEC.md:25`)
- **Scope Out Respected**: Did not read or run `MyTradingSys/research/adx_di_2026-11/census.py` or `MyTradingSys/backtest/layers/adx/adx.py`; no source files edited; no live-tree, `.secrets`, or `.env` touched.
- **Parameter Provenance (`SOURCED` vs `OURS`)**: Per `CENSUS.md:3` (`"Context layer, no orders, no edge claim; every threshold is OURS (CCU, Steve 2026-11-05, names none)"`, `SOURCED`) and `SPEC.md:3-5`, Wilder's ADX/DI recursive equations in `FORMULAS.md:689` are `SOURCED` (J. Welles Wilder 1978 / TradingView DMI 14/14), while `n=14`, epoch-even 2d bucketing, `slope5 = ADX[i] - ADX[i-5]`, ADX buckets (`<20`, `20-40`, `>40`), forward swing window (`30` 2d bars), whipsaw horizons (`k=1,2,3`), cascade windows (`20` days look-back / `5` 2d bars = `10` days look-ahead), and split dates (`DEV`, `VALIDATION`, `RECENT`) are `OURS`.

## Summary of Discrepancies (`DIFF`: 9, `NOT_IN_DATA`: 1)

1. **Table (c) Median Lead Formatting Bug (`DIFF` x 3 — `CENSUS.md:192,193,194`)**:
   - In `CENSUS.md:192-194`, the column `median lead (days)` prints `400.0%` (`DEV`), `850.0%` (`VALIDATION`), and `1300.0%` (`RECENT`).
   - Recomputing the median of the per-cross lead days listed in `CENSUS.md:200-287` gives exactly **`4.0` days** (`DEV`, `n=52`), **`8.5` days** (`VALIDATION`, `n=12`), and **`13.0` days** (`RECENT`, `n=15`). The report generator formatted raw day counts with Python's percentage format specifier (`:.1%`), multiplying by 100 and appending `%`.
2. **Table (b) `RECENT` `n_ws` / `whipsaw<=3` Boundary (`DIFF` x 6 — `CENSUS.md:63,75,79`)**:
   - `CENSUS.md:3` states: `"Whipsaw = opposite cross within k bars; cells need k bars after (n_ws)."`
   - Cross `2026-11-03` (`CENSUS.md:183`, `green`, `ADX=24.6`, `slope5=-7.5`) has only `nfwd = 1` bar after it (`2026-11-05`), not `k = 3` bars. Because `2026-11-05` (`CENSUS.md:184`) is an immediate opposite (`red`) cross at `k = 1`, `CENSUS.md:183` marks `whip1 = yes, whip2 = yes, whip3 = yes` and includes `2026-11-03` in `n_ws` for `RECENT` (`all, 20-40, falling`: `n_ws=10, whipsaw<=3=60.0%`; `green, 20-40, falling`: `n_ws=5, whipsaw<=3=80.0%`; `all, all, all`: `n_ws=16, whipsaw<=3=50.0%`).
   - Under the strict `nfwd >= 3` rule from `CENSUS.md:3` (`"cells need k bars after (n_ws)"`), `2026-11-03` (`nfwd=1`) is excluded from `k=3` whipsaw denominators, giving `n_ws=9` (`5/9 = 55.6%`), `n_ws=4` (`3/4 = 75.0%`), and `n_ws=15` (`7/15 = 46.7%`). Both the strict `nfwd >= 3` value and the realized-early-whipsaw value are shown in the audit table below.
3. **1h / 4h Cascade (`NOT_IN_DATA` x 1 — `CENSUS.md:5,188`)**:
   - `CENSUS.md:5` notes `"1h / 4h not run: no 1h/4h BTC kline file covering 2020-2026 is on this machine"`; recorded as `NOT_IN_DATA`.

## Complete Number-by-Number Audit Table (`825` items)

| # | Line (`CENSUS.md`) | Section | Metric / Cell (`OURS` unless noted) | Cited Value (`SOURCED` from `CENSUS.md`) | Recomputed Value (Independent) | Status | Basis & Formula Reference |
|---:|---|---|---|---|---|---|---|
| 1 | `CENSUS.md:3` | Header prose | Daily bars count (2017-01-01..2026-11-06) | `3597` | `3597` | `MATCH` | `btc_daily.csv` rows >= 2017-01-01 (`SOURCED` data count) |
| 2 | `CENSUS.md:3` | Header prose | Closed 2d bars count (epoch-even 2d buckets) | `1799` | `1799` | `MATCH` | `FORMULAS.md:153-161` s8 2d `bucket_end <= last_bar_close` (`OURS`) |
| 3 | `CENSUS.md:3` | Header prose | Wilder ADX/DI period n | `14` | `14` | `MATCH` | `FORMULAS.md:687,689` s30.1 `n=14` (`OURS`) |
| 4 | `CENSUS.md:3` | Header prose | Forward swing window (2d bars after cross) | `30` | `30` | `MATCH` | `SPEC.md:14` / `CENSUS.md:3` 30 2d bars (`OURS`) |
| 5 | `CENSUS.md:5` | Header prose | 1h / 4h cascade numbers (table c) | `not run` | `NOT_IN_DATA` | `NOT_IN_DATA` | No 2020-2026 1h/4h BTC klines on machine (`CENSUS.md:5`, `OURS`) |
| 6 | `CENSUS.md:9` | (b) DEV header | DEV total crosses | `56` | `56` | `MATCH` | `btc_daily.csv` + `FORMULAS.md:689` (2020-01-01..2024-06-30, `OURS`) |
| 7 | `CENSUS.md:9` | (b) DEV header | DEV red crosses | `28` | `28` | `MATCH` | DI- over DI+ count in DEV (`OURS`) |
| 8 | `CENSUS.md:9` | (b) DEV header | DEV green crosses | `28` | `28` | `MATCH` | DI+ over DI- count in DEV (`OURS`) |
| 9 | `CENSUS.md:13` | (b) DEV | DEV (all, <20, falling) n | `22` | `22` | `MATCH` | Bucket count (`OURS`) |
| 10 | `CENSUS.md:13` | (b) DEV | DEV (all, <20, falling) n_ws | `22` | `22` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 11 | `CENSUS.md:13` | (b) DEV | DEV (all, <20, falling) whipsaw<=3 | `31.8%` | `31.8%` | `MATCH` | 7/22 opposite cross within 3 bars (`OURS`) |
| 12 | `CENSUS.md:13` | (b) DEV | DEV (all, <20, falling) n_dp | `22` | `22` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 13 | `CENSUS.md:13` | (b) DEV | DEV (all, <20, falling) median depth | `20.6%` | `20.6%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 14 | `CENSUS.md:13` | (b) DEV | DEV (all, <20, falling) median bars to extreme | `18.5` | `18.5` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 15 | `CENSUS.md:14` | (b) DEV | DEV (all, <20, rising) n | `1` | `1` | `MATCH` | Bucket count (`OURS`) |
| 16 | `CENSUS.md:14` | (b) DEV | DEV (all, <20, rising) n_ws | `1` | `1` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 17 | `CENSUS.md:14` | (b) DEV | DEV (all, <20, rising) whipsaw<=3 | `0.0%` | `0.0%` | `MATCH` | 0/1 opposite cross within 3 bars (`OURS`) |
| 18 | `CENSUS.md:14` | (b) DEV | DEV (all, <20, rising) n_dp | `1` | `1` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 19 | `CENSUS.md:14` | (b) DEV | DEV (all, <20, rising) median depth | `2.8%` | `2.8%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 20 | `CENSUS.md:14` | (b) DEV | DEV (all, <20, rising) median bars to extreme | `6.0` | `6.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 21 | `CENSUS.md:15` | (b) DEV | DEV (all, 20-40, falling) n | `28` | `28` | `MATCH` | Bucket count (`OURS`) |
| 22 | `CENSUS.md:15` | (b) DEV | DEV (all, 20-40, falling) n_ws | `28` | `28` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 23 | `CENSUS.md:15` | (b) DEV | DEV (all, 20-40, falling) whipsaw<=3 | `35.7%` | `35.7%` | `MATCH` | 10/28 opposite cross within 3 bars (`OURS`) |
| 24 | `CENSUS.md:15` | (b) DEV | DEV (all, 20-40, falling) n_dp | `28` | `28` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 25 | `CENSUS.md:15` | (b) DEV | DEV (all, 20-40, falling) median depth | `12.1%` | `12.1%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 26 | `CENSUS.md:15` | (b) DEV | DEV (all, 20-40, falling) median bars to extreme | `8.5` | `8.5` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 27 | `CENSUS.md:16` | (b) DEV | DEV (all, 20-40, rising) n | `4` | `4` | `MATCH` | Bucket count (`OURS`) |
| 28 | `CENSUS.md:16` | (b) DEV | DEV (all, 20-40, rising) n_ws | `4` | `4` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 29 | `CENSUS.md:16` | (b) DEV | DEV (all, 20-40, rising) whipsaw<=3 | `25.0%` | `25.0%` | `MATCH` | 1/4 opposite cross within 3 bars (`OURS`) |
| 30 | `CENSUS.md:16` | (b) DEV | DEV (all, 20-40, rising) n_dp | `4` | `4` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 31 | `CENSUS.md:16` | (b) DEV | DEV (all, 20-40, rising) median depth | `17.6%` | `17.6%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 32 | `CENSUS.md:16` | (b) DEV | DEV (all, 20-40, rising) median bars to extreme | `16.0` | `16.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 33 | `CENSUS.md:17` | (b) DEV | DEV (all, >40, falling) n | `1` | `1` | `MATCH` | Bucket count (`OURS`) |
| 34 | `CENSUS.md:17` | (b) DEV | DEV (all, >40, falling) n_ws | `1` | `1` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 35 | `CENSUS.md:17` | (b) DEV | DEV (all, >40, falling) whipsaw<=3 | `0.0%` | `0.0%` | `MATCH` | 0/1 opposite cross within 3 bars (`OURS`) |
| 36 | `CENSUS.md:17` | (b) DEV | DEV (all, >40, falling) n_dp | `1` | `1` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 37 | `CENSUS.md:17` | (b) DEV | DEV (all, >40, falling) median depth | `32.2%` | `32.2%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 38 | `CENSUS.md:17` | (b) DEV | DEV (all, >40, falling) median bars to extreme | `20.0` | `20.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 39 | `CENSUS.md:18` | (b) DEV | DEV (all, >40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 40 | `CENSUS.md:18` | (b) DEV | DEV (all, >40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 41 | `CENSUS.md:18` | (b) DEV | DEV (all, >40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 42 | `CENSUS.md:19` | (b) DEV | DEV (red, <20, falling) n | `9` | `9` | `MATCH` | Bucket count (`OURS`) |
| 43 | `CENSUS.md:19` | (b) DEV | DEV (red, <20, falling) n_ws | `9` | `9` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 44 | `CENSUS.md:19` | (b) DEV | DEV (red, <20, falling) whipsaw<=3 | `33.3%` | `33.3%` | `MATCH` | 3/9 opposite cross within 3 bars (`OURS`) |
| 45 | `CENSUS.md:19` | (b) DEV | DEV (red, <20, falling) n_dp | `9` | `9` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 46 | `CENSUS.md:19` | (b) DEV | DEV (red, <20, falling) median depth | `-7.5%` | `-7.5%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 47 | `CENSUS.md:19` | (b) DEV | DEV (red, <20, falling) median bars to extreme | `7.0` | `7.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 48 | `CENSUS.md:20` | (b) DEV | DEV (red, <20, rising) n | `1` | `1` | `MATCH` | Bucket count (`OURS`) |
| 49 | `CENSUS.md:20` | (b) DEV | DEV (red, <20, rising) n_ws | `1` | `1` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 50 | `CENSUS.md:20` | (b) DEV | DEV (red, <20, rising) whipsaw<=3 | `0.0%` | `0.0%` | `MATCH` | 0/1 opposite cross within 3 bars (`OURS`) |
| 51 | `CENSUS.md:20` | (b) DEV | DEV (red, <20, rising) n_dp | `1` | `1` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 52 | `CENSUS.md:20` | (b) DEV | DEV (red, <20, rising) median depth | `-2.8%` | `-2.8%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 53 | `CENSUS.md:20` | (b) DEV | DEV (red, <20, rising) median bars to extreme | `6.0` | `6.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 54 | `CENSUS.md:21` | (b) DEV | DEV (red, 20-40, falling) n | `17` | `17` | `MATCH` | Bucket count (`OURS`) |
| 55 | `CENSUS.md:21` | (b) DEV | DEV (red, 20-40, falling) n_ws | `17` | `17` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 56 | `CENSUS.md:21` | (b) DEV | DEV (red, 20-40, falling) whipsaw<=3 | `17.6%` | `17.6%` | `MATCH` | 3/17 opposite cross within 3 bars (`OURS`) |
| 57 | `CENSUS.md:21` | (b) DEV | DEV (red, 20-40, falling) n_dp | `17` | `17` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 58 | `CENSUS.md:21` | (b) DEV | DEV (red, 20-40, falling) median depth | `-13.9%` | `-13.9%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 59 | `CENSUS.md:21` | (b) DEV | DEV (red, 20-40, falling) median bars to extreme | `5.0` | `5.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 60 | `CENSUS.md:22` | (b) DEV | DEV (red, 20-40, rising) n | `1` | `1` | `MATCH` | Bucket count (`OURS`) |
| 61 | `CENSUS.md:22` | (b) DEV | DEV (red, 20-40, rising) n_ws | `1` | `1` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 62 | `CENSUS.md:22` | (b) DEV | DEV (red, 20-40, rising) whipsaw<=3 | `0.0%` | `0.0%` | `MATCH` | 0/1 opposite cross within 3 bars (`OURS`) |
| 63 | `CENSUS.md:22` | (b) DEV | DEV (red, 20-40, rising) n_dp | `1` | `1` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 64 | `CENSUS.md:22` | (b) DEV | DEV (red, 20-40, rising) median depth | `-4.4%` | `-4.4%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 65 | `CENSUS.md:22` | (b) DEV | DEV (red, 20-40, rising) median bars to extreme | `12.0` | `12.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 66 | `CENSUS.md:23` | (b) DEV | DEV (red, >40, falling) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 67 | `CENSUS.md:23` | (b) DEV | DEV (red, >40, falling) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 68 | `CENSUS.md:23` | (b) DEV | DEV (red, >40, falling) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 69 | `CENSUS.md:24` | (b) DEV | DEV (red, >40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 70 | `CENSUS.md:24` | (b) DEV | DEV (red, >40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 71 | `CENSUS.md:24` | (b) DEV | DEV (red, >40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 72 | `CENSUS.md:25` | (b) DEV | DEV (green, <20, falling) n | `13` | `13` | `MATCH` | Bucket count (`OURS`) |
| 73 | `CENSUS.md:25` | (b) DEV | DEV (green, <20, falling) n_ws | `13` | `13` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 74 | `CENSUS.md:25` | (b) DEV | DEV (green, <20, falling) whipsaw<=3 | `30.8%` | `30.8%` | `MATCH` | 4/13 opposite cross within 3 bars (`OURS`) |
| 75 | `CENSUS.md:25` | (b) DEV | DEV (green, <20, falling) n_dp | `13` | `13` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 76 | `CENSUS.md:25` | (b) DEV | DEV (green, <20, falling) median depth | `31.0%` | `31.0%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 77 | `CENSUS.md:25` | (b) DEV | DEV (green, <20, falling) median bars to extreme | `20.0` | `20.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 78 | `CENSUS.md:26` | (b) DEV | DEV (green, <20, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 79 | `CENSUS.md:26` | (b) DEV | DEV (green, <20, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 80 | `CENSUS.md:26` | (b) DEV | DEV (green, <20, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 81 | `CENSUS.md:27` | (b) DEV | DEV (green, 20-40, falling) n | `11` | `11` | `MATCH` | Bucket count (`OURS`) |
| 82 | `CENSUS.md:27` | (b) DEV | DEV (green, 20-40, falling) n_ws | `11` | `11` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 83 | `CENSUS.md:27` | (b) DEV | DEV (green, 20-40, falling) whipsaw<=3 | `63.6%` | `63.6%` | `MATCH` | 7/11 opposite cross within 3 bars (`OURS`) |
| 84 | `CENSUS.md:27` | (b) DEV | DEV (green, 20-40, falling) n_dp | `11` | `11` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 85 | `CENSUS.md:27` | (b) DEV | DEV (green, 20-40, falling) median depth | `10.4%` | `10.4%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 86 | `CENSUS.md:27` | (b) DEV | DEV (green, 20-40, falling) median bars to extreme | `20.0` | `20.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 87 | `CENSUS.md:28` | (b) DEV | DEV (green, 20-40, rising) n | `3` | `3` | `MATCH` | Bucket count (`OURS`) |
| 88 | `CENSUS.md:28` | (b) DEV | DEV (green, 20-40, rising) n_ws | `3` | `3` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 89 | `CENSUS.md:28` | (b) DEV | DEV (green, 20-40, rising) whipsaw<=3 | `33.3%` | `33.3%` | `MATCH` | 1/3 opposite cross within 3 bars (`OURS`) |
| 90 | `CENSUS.md:28` | (b) DEV | DEV (green, 20-40, rising) n_dp | `3` | `3` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 91 | `CENSUS.md:28` | (b) DEV | DEV (green, 20-40, rising) median depth | `29.2%` | `29.2%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 92 | `CENSUS.md:28` | (b) DEV | DEV (green, 20-40, rising) median bars to extreme | `20.0` | `20.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 93 | `CENSUS.md:29` | (b) DEV | DEV (green, >40, falling) n | `1` | `1` | `MATCH` | Bucket count (`OURS`) |
| 94 | `CENSUS.md:29` | (b) DEV | DEV (green, >40, falling) n_ws | `1` | `1` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 95 | `CENSUS.md:29` | (b) DEV | DEV (green, >40, falling) whipsaw<=3 | `0.0%` | `0.0%` | `MATCH` | 0/1 opposite cross within 3 bars (`OURS`) |
| 96 | `CENSUS.md:29` | (b) DEV | DEV (green, >40, falling) n_dp | `1` | `1` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 97 | `CENSUS.md:29` | (b) DEV | DEV (green, >40, falling) median depth | `32.2%` | `32.2%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 98 | `CENSUS.md:29` | (b) DEV | DEV (green, >40, falling) median bars to extreme | `20.0` | `20.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 99 | `CENSUS.md:30` | (b) DEV | DEV (green, >40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 100 | `CENSUS.md:30` | (b) DEV | DEV (green, >40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 101 | `CENSUS.md:30` | (b) DEV | DEV (green, >40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 102 | `CENSUS.md:31` | (b) DEV | DEV (all, all, all) n | `56` | `56` | `MATCH` | Bucket count (`OURS`) |
| 103 | `CENSUS.md:31` | (b) DEV | DEV (all, all, all) n_ws | `56` | `56` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 104 | `CENSUS.md:31` | (b) DEV | DEV (all, all, all) whipsaw<=3 | `32.1%` | `32.1%` | `MATCH` | 18/56 opposite cross within 3 bars (`OURS`) |
| 105 | `CENSUS.md:31` | (b) DEV | DEV (all, all, all) n_dp | `56` | `56` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 106 | `CENSUS.md:31` | (b) DEV | DEV (all, all, all) median depth | `14.8%` | `14.8%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 107 | `CENSUS.md:31` | (b) DEV | DEV (all, all, all) median bars to extreme | `16.0` | `16.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 108 | `CENSUS.md:33` | (b) VALIDATION header | VALIDATION total crosses | `15` | `15` | `MATCH` | `btc_daily.csv` + `FORMULAS.md:689` (2024-07-01..2025-06-30, `OURS`) |
| 109 | `CENSUS.md:33` | (b) VALIDATION header | VALIDATION red crosses | `7` | `7` | `MATCH` | DI- over DI+ count in VALIDATION (`OURS`) |
| 110 | `CENSUS.md:33` | (b) VALIDATION header | VALIDATION green crosses | `8` | `8` | `MATCH` | DI+ over DI- count in VALIDATION (`OURS`) |
| 111 | `CENSUS.md:37` | (b) VALIDATION | VALIDATION (all, <20, falling) n | `7` | `7` | `MATCH` | Bucket count (`OURS`) |
| 112 | `CENSUS.md:37` | (b) VALIDATION | VALIDATION (all, <20, falling) n_ws | `7` | `7` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 113 | `CENSUS.md:37` | (b) VALIDATION | VALIDATION (all, <20, falling) whipsaw<=3 | `14.3%` | `14.3%` | `MATCH` | 1/7 opposite cross within 3 bars (`OURS`) |
| 114 | `CENSUS.md:37` | (b) VALIDATION | VALIDATION (all, <20, falling) n_dp | `7` | `7` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 115 | `CENSUS.md:37` | (b) VALIDATION | VALIDATION (all, <20, falling) median depth | `17.3%` | `17.3%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 116 | `CENSUS.md:37` | (b) VALIDATION | VALIDATION (all, <20, falling) median bars to extreme | `5.0` | `5.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 117 | `CENSUS.md:38` | (b) VALIDATION | VALIDATION (all, <20, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 118 | `CENSUS.md:38` | (b) VALIDATION | VALIDATION (all, <20, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 119 | `CENSUS.md:38` | (b) VALIDATION | VALIDATION (all, <20, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 120 | `CENSUS.md:39` | (b) VALIDATION | VALIDATION (all, 20-40, falling) n | `8` | `8` | `MATCH` | Bucket count (`OURS`) |
| 121 | `CENSUS.md:39` | (b) VALIDATION | VALIDATION (all, 20-40, falling) n_ws | `8` | `8` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 122 | `CENSUS.md:39` | (b) VALIDATION | VALIDATION (all, 20-40, falling) whipsaw<=3 | `75.0%` | `75.0%` | `MATCH` | 6/8 opposite cross within 3 bars (`OURS`) |
| 123 | `CENSUS.md:39` | (b) VALIDATION | VALIDATION (all, 20-40, falling) n_dp | `8` | `8` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 124 | `CENSUS.md:39` | (b) VALIDATION | VALIDATION (all, 20-40, falling) median depth | `16.3%` | `16.3%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 125 | `CENSUS.md:39` | (b) VALIDATION | VALIDATION (all, 20-40, falling) median bars to extreme | `12.0` | `12.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 126 | `CENSUS.md:40` | (b) VALIDATION | VALIDATION (all, 20-40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 127 | `CENSUS.md:40` | (b) VALIDATION | VALIDATION (all, 20-40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 128 | `CENSUS.md:40` | (b) VALIDATION | VALIDATION (all, 20-40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 129 | `CENSUS.md:41` | (b) VALIDATION | VALIDATION (all, >40, falling) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 130 | `CENSUS.md:41` | (b) VALIDATION | VALIDATION (all, >40, falling) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 131 | `CENSUS.md:41` | (b) VALIDATION | VALIDATION (all, >40, falling) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 132 | `CENSUS.md:42` | (b) VALIDATION | VALIDATION (all, >40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 133 | `CENSUS.md:42` | (b) VALIDATION | VALIDATION (all, >40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 134 | `CENSUS.md:42` | (b) VALIDATION | VALIDATION (all, >40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 135 | `CENSUS.md:43` | (b) VALIDATION | VALIDATION (red, <20, falling) n | `3` | `3` | `MATCH` | Bucket count (`OURS`) |
| 136 | `CENSUS.md:43` | (b) VALIDATION | VALIDATION (red, <20, falling) n_ws | `3` | `3` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 137 | `CENSUS.md:43` | (b) VALIDATION | VALIDATION (red, <20, falling) whipsaw<=3 | `0.0%` | `0.0%` | `MATCH` | 0/3 opposite cross within 3 bars (`OURS`) |
| 138 | `CENSUS.md:43` | (b) VALIDATION | VALIDATION (red, <20, falling) n_dp | `3` | `3` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 139 | `CENSUS.md:43` | (b) VALIDATION | VALIDATION (red, <20, falling) median depth | `-21.6%` | `-21.6%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 140 | `CENSUS.md:43` | (b) VALIDATION | VALIDATION (red, <20, falling) median bars to extreme | `5.0` | `5.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 141 | `CENSUS.md:44` | (b) VALIDATION | VALIDATION (red, <20, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 142 | `CENSUS.md:44` | (b) VALIDATION | VALIDATION (red, <20, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 143 | `CENSUS.md:44` | (b) VALIDATION | VALIDATION (red, <20, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 144 | `CENSUS.md:45` | (b) VALIDATION | VALIDATION (red, 20-40, falling) n | `4` | `4` | `MATCH` | Bucket count (`OURS`) |
| 145 | `CENSUS.md:45` | (b) VALIDATION | VALIDATION (red, 20-40, falling) n_ws | `4` | `4` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 146 | `CENSUS.md:45` | (b) VALIDATION | VALIDATION (red, 20-40, falling) whipsaw<=3 | `100.0%` | `100.0%` | `MATCH` | 4/4 opposite cross within 3 bars (`OURS`) |
| 147 | `CENSUS.md:45` | (b) VALIDATION | VALIDATION (red, 20-40, falling) n_dp | `4` | `4` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 148 | `CENSUS.md:45` | (b) VALIDATION | VALIDATION (red, 20-40, falling) median depth | `-16.3%` | `-16.3%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 149 | `CENSUS.md:45` | (b) VALIDATION | VALIDATION (red, 20-40, falling) median bars to extreme | `17.5` | `17.5` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 150 | `CENSUS.md:46` | (b) VALIDATION | VALIDATION (red, 20-40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 151 | `CENSUS.md:46` | (b) VALIDATION | VALIDATION (red, 20-40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 152 | `CENSUS.md:46` | (b) VALIDATION | VALIDATION (red, 20-40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 153 | `CENSUS.md:47` | (b) VALIDATION | VALIDATION (red, >40, falling) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 154 | `CENSUS.md:47` | (b) VALIDATION | VALIDATION (red, >40, falling) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 155 | `CENSUS.md:47` | (b) VALIDATION | VALIDATION (red, >40, falling) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 156 | `CENSUS.md:48` | (b) VALIDATION | VALIDATION (red, >40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 157 | `CENSUS.md:48` | (b) VALIDATION | VALIDATION (red, >40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 158 | `CENSUS.md:48` | (b) VALIDATION | VALIDATION (red, >40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 159 | `CENSUS.md:49` | (b) VALIDATION | VALIDATION (green, <20, falling) n | `4` | `4` | `MATCH` | Bucket count (`OURS`) |
| 160 | `CENSUS.md:49` | (b) VALIDATION | VALIDATION (green, <20, falling) n_ws | `4` | `4` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 161 | `CENSUS.md:49` | (b) VALIDATION | VALIDATION (green, <20, falling) whipsaw<=3 | `25.0%` | `25.0%` | `MATCH` | 1/4 opposite cross within 3 bars (`OURS`) |
| 162 | `CENSUS.md:49` | (b) VALIDATION | VALIDATION (green, <20, falling) n_dp | `4` | `4` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 163 | `CENSUS.md:49` | (b) VALIDATION | VALIDATION (green, <20, falling) median depth | `13.2%` | `13.2%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 164 | `CENSUS.md:49` | (b) VALIDATION | VALIDATION (green, <20, falling) median bars to extreme | `14.5` | `14.5` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 165 | `CENSUS.md:50` | (b) VALIDATION | VALIDATION (green, <20, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 166 | `CENSUS.md:50` | (b) VALIDATION | VALIDATION (green, <20, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 167 | `CENSUS.md:50` | (b) VALIDATION | VALIDATION (green, <20, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 168 | `CENSUS.md:51` | (b) VALIDATION | VALIDATION (green, 20-40, falling) n | `4` | `4` | `MATCH` | Bucket count (`OURS`) |
| 169 | `CENSUS.md:51` | (b) VALIDATION | VALIDATION (green, 20-40, falling) n_ws | `4` | `4` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 170 | `CENSUS.md:51` | (b) VALIDATION | VALIDATION (green, 20-40, falling) whipsaw<=3 | `50.0%` | `50.0%` | `MATCH` | 2/4 opposite cross within 3 bars (`OURS`) |
| 171 | `CENSUS.md:51` | (b) VALIDATION | VALIDATION (green, 20-40, falling) n_dp | `4` | `4` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 172 | `CENSUS.md:51` | (b) VALIDATION | VALIDATION (green, 20-40, falling) median depth | `15.6%` | `15.6%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 173 | `CENSUS.md:51` | (b) VALIDATION | VALIDATION (green, 20-40, falling) median bars to extreme | `12.0` | `12.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 174 | `CENSUS.md:52` | (b) VALIDATION | VALIDATION (green, 20-40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 175 | `CENSUS.md:52` | (b) VALIDATION | VALIDATION (green, 20-40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 176 | `CENSUS.md:52` | (b) VALIDATION | VALIDATION (green, 20-40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 177 | `CENSUS.md:53` | (b) VALIDATION | VALIDATION (green, >40, falling) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 178 | `CENSUS.md:53` | (b) VALIDATION | VALIDATION (green, >40, falling) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 179 | `CENSUS.md:53` | (b) VALIDATION | VALIDATION (green, >40, falling) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 180 | `CENSUS.md:54` | (b) VALIDATION | VALIDATION (green, >40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 181 | `CENSUS.md:54` | (b) VALIDATION | VALIDATION (green, >40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 182 | `CENSUS.md:54` | (b) VALIDATION | VALIDATION (green, >40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 183 | `CENSUS.md:55` | (b) VALIDATION | VALIDATION (all, all, all) n | `15` | `15` | `MATCH` | Bucket count (`OURS`) |
| 184 | `CENSUS.md:55` | (b) VALIDATION | VALIDATION (all, all, all) n_ws | `15` | `15` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 185 | `CENSUS.md:55` | (b) VALIDATION | VALIDATION (all, all, all) whipsaw<=3 | `46.7%` | `46.7%` | `MATCH` | 7/15 opposite cross within 3 bars (`OURS`) |
| 186 | `CENSUS.md:55` | (b) VALIDATION | VALIDATION (all, all, all) n_dp | `15` | `15` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 187 | `CENSUS.md:55` | (b) VALIDATION | VALIDATION (all, all, all) median depth | `17.3%` | `17.3%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 188 | `CENSUS.md:55` | (b) VALIDATION | VALIDATION (all, all, all) median bars to extreme | `9.0` | `9.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 189 | `CENSUS.md:57` | (b) RECENT header | RECENT total crosses | `17` | `17` | `MATCH` | `btc_daily.csv` + `FORMULAS.md:689` (2025-07-01..2026-11-07, `OURS`) |
| 190 | `CENSUS.md:57` | (b) RECENT header | RECENT red crosses | `9` | `9` | `MATCH` | DI- over DI+ count in RECENT (`OURS`) |
| 191 | `CENSUS.md:57` | (b) RECENT header | RECENT green crosses | `8` | `8` | `MATCH` | DI+ over DI- count in RECENT (`OURS`) |
| 192 | `CENSUS.md:61` | (b) RECENT | RECENT (all, <20, falling) n | `5` | `5` | `MATCH` | Bucket count (`OURS`) |
| 193 | `CENSUS.md:61` | (b) RECENT | RECENT (all, <20, falling) n_ws | `5` | `5` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 194 | `CENSUS.md:61` | (b) RECENT | RECENT (all, <20, falling) whipsaw<=3 | `40.0%` | `40.0%` | `MATCH` | 2/5 opposite cross within 3 bars (`OURS`) |
| 195 | `CENSUS.md:61` | (b) RECENT | RECENT (all, <20, falling) n_dp | `5` | `5` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 196 | `CENSUS.md:61` | (b) RECENT | RECENT (all, <20, falling) median depth | `13.4%` | `13.4%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 197 | `CENSUS.md:61` | (b) RECENT | RECENT (all, <20, falling) median bars to extreme | `17.0` | `17.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 198 | `CENSUS.md:62` | (b) RECENT | RECENT (all, <20, rising) n | `1` | `1` | `MATCH` | Bucket count (`OURS`) |
| 199 | `CENSUS.md:62` | (b) RECENT | RECENT (all, <20, rising) n_ws | `1` | `1` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 200 | `CENSUS.md:62` | (b) RECENT | RECENT (all, <20, rising) whipsaw<=3 | `0.0%` | `0.0%` | `MATCH` | 0/1 opposite cross within 3 bars (`OURS`) |
| 201 | `CENSUS.md:62` | (b) RECENT | RECENT (all, <20, rising) n_dp | `1` | `1` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 202 | `CENSUS.md:62` | (b) RECENT | RECENT (all, <20, rising) median depth | `28.5%` | `28.5%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 203 | `CENSUS.md:62` | (b) RECENT | RECENT (all, <20, rising) median bars to extreme | `21.0` | `21.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 204 | `CENSUS.md:63` | (b) RECENT | RECENT (all, 20-40, falling) n | `11` | `11` | `MATCH` | Bucket count (`OURS`) |
| 205 | `CENSUS.md:63` | (b) RECENT | RECENT (all, 20-40, falling) n_ws | `10` | `9 (strict nfwd>=3; 10 if 2026-11-03 whip1=yes included)` | `DIFF` | `CENSUS.md:3` requires k=3 bars after, but 2026-11-03 (nfwd=1, whip1=yes) was counted in n_ws (`OURS`) |
| 206 | `CENSUS.md:63` | (b) RECENT | RECENT (all, 20-40, falling) whipsaw<=3 | `60.0%` | `55.6% (strict 5/9; 60.0% if 2026-11-03 included)` | `DIFF` | Propagated from 2026-11-03 (nfwd=1) counted in n_ws (`OURS`) |
| 207 | `CENSUS.md:63` | (b) RECENT | RECENT (all, 20-40, falling) n_dp | `8` | `8` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 208 | `CENSUS.md:63` | (b) RECENT | RECENT (all, 20-40, falling) median depth | `14.3%` | `14.3%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 209 | `CENSUS.md:63` | (b) RECENT | RECENT (all, 20-40, falling) median bars to extreme | `11.5` | `11.5` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 210 | `CENSUS.md:64` | (b) RECENT | RECENT (all, 20-40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 211 | `CENSUS.md:64` | (b) RECENT | RECENT (all, 20-40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 212 | `CENSUS.md:64` | (b) RECENT | RECENT (all, 20-40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 213 | `CENSUS.md:65` | (b) RECENT | RECENT (all, >40, falling) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 214 | `CENSUS.md:65` | (b) RECENT | RECENT (all, >40, falling) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 215 | `CENSUS.md:65` | (b) RECENT | RECENT (all, >40, falling) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 216 | `CENSUS.md:66` | (b) RECENT | RECENT (all, >40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 217 | `CENSUS.md:66` | (b) RECENT | RECENT (all, >40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 218 | `CENSUS.md:66` | (b) RECENT | RECENT (all, >40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 219 | `CENSUS.md:67` | (b) RECENT | RECENT (red, <20, falling) n | `2` | `2` | `MATCH` | Bucket count (`OURS`) |
| 220 | `CENSUS.md:67` | (b) RECENT | RECENT (red, <20, falling) n_ws | `2` | `2` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 221 | `CENSUS.md:67` | (b) RECENT | RECENT (red, <20, falling) whipsaw<=3 | `100.0%` | `100.0%` | `MATCH` | 2/2 opposite cross within 3 bars (`OURS`) |
| 222 | `CENSUS.md:67` | (b) RECENT | RECENT (red, <20, falling) n_dp | `2` | `2` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 223 | `CENSUS.md:67` | (b) RECENT | RECENT (red, <20, falling) median depth | `-18.6%` | `-18.6%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 224 | `CENSUS.md:67` | (b) RECENT | RECENT (red, <20, falling) median bars to extreme | `25.5` | `25.5` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 225 | `CENSUS.md:68` | (b) RECENT | RECENT (red, <20, rising) n | `1` | `1` | `MATCH` | Bucket count (`OURS`) |
| 226 | `CENSUS.md:68` | (b) RECENT | RECENT (red, <20, rising) n_ws | `1` | `1` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 227 | `CENSUS.md:68` | (b) RECENT | RECENT (red, <20, rising) whipsaw<=3 | `0.0%` | `0.0%` | `MATCH` | 0/1 opposite cross within 3 bars (`OURS`) |
| 228 | `CENSUS.md:68` | (b) RECENT | RECENT (red, <20, rising) n_dp | `1` | `1` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 229 | `CENSUS.md:68` | (b) RECENT | RECENT (red, <20, rising) median depth | `-28.5%` | `-28.5%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 230 | `CENSUS.md:68` | (b) RECENT | RECENT (red, <20, rising) median bars to extreme | `21.0` | `21.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 231 | `CENSUS.md:69` | (b) RECENT | RECENT (red, 20-40, falling) n | `6` | `6` | `MATCH` | Bucket count (`OURS`) |
| 232 | `CENSUS.md:69` | (b) RECENT | RECENT (red, 20-40, falling) n_ws | `5` | `5` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 233 | `CENSUS.md:69` | (b) RECENT | RECENT (red, 20-40, falling) whipsaw<=3 | `40.0%` | `40.0%` | `MATCH` | 2/5 opposite cross within 3 bars (`OURS`) |
| 234 | `CENSUS.md:69` | (b) RECENT | RECENT (red, 20-40, falling) n_dp | `4` | `4` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 235 | `CENSUS.md:69` | (b) RECENT | RECENT (red, 20-40, falling) median depth | `-28.6%` | `-28.6%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 236 | `CENSUS.md:69` | (b) RECENT | RECENT (red, 20-40, falling) median bars to extreme | `12.0` | `12.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 237 | `CENSUS.md:70` | (b) RECENT | RECENT (red, 20-40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 238 | `CENSUS.md:70` | (b) RECENT | RECENT (red, 20-40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 239 | `CENSUS.md:70` | (b) RECENT | RECENT (red, 20-40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 240 | `CENSUS.md:71` | (b) RECENT | RECENT (red, >40, falling) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 241 | `CENSUS.md:71` | (b) RECENT | RECENT (red, >40, falling) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 242 | `CENSUS.md:71` | (b) RECENT | RECENT (red, >40, falling) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 243 | `CENSUS.md:72` | (b) RECENT | RECENT (red, >40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 244 | `CENSUS.md:72` | (b) RECENT | RECENT (red, >40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 245 | `CENSUS.md:72` | (b) RECENT | RECENT (red, >40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 246 | `CENSUS.md:73` | (b) RECENT | RECENT (green, <20, falling) n | `3` | `3` | `MATCH` | Bucket count (`OURS`) |
| 247 | `CENSUS.md:73` | (b) RECENT | RECENT (green, <20, falling) n_ws | `3` | `3` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 248 | `CENSUS.md:73` | (b) RECENT | RECENT (green, <20, falling) whipsaw<=3 | `0.0%` | `0.0%` | `MATCH` | 0/3 opposite cross within 3 bars (`OURS`) |
| 249 | `CENSUS.md:73` | (b) RECENT | RECENT (green, <20, falling) n_dp | `3` | `3` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 250 | `CENSUS.md:73` | (b) RECENT | RECENT (green, <20, falling) median depth | `13.4%` | `13.4%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 251 | `CENSUS.md:73` | (b) RECENT | RECENT (green, <20, falling) median bars to extreme | `17.0` | `17.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 252 | `CENSUS.md:74` | (b) RECENT | RECENT (green, <20, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 253 | `CENSUS.md:74` | (b) RECENT | RECENT (green, <20, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 254 | `CENSUS.md:74` | (b) RECENT | RECENT (green, <20, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 255 | `CENSUS.md:75` | (b) RECENT | RECENT (green, 20-40, falling) n | `5` | `5` | `MATCH` | Bucket count (`OURS`) |
| 256 | `CENSUS.md:75` | (b) RECENT | RECENT (green, 20-40, falling) n_ws | `5` | `4 (strict nfwd>=3; 5 if 2026-11-03 whip1=yes included)` | `DIFF` | `CENSUS.md:3` requires k=3 bars after, but 2026-11-03 (nfwd=1, whip1=yes) was counted in n_ws (`OURS`) |
| 257 | `CENSUS.md:75` | (b) RECENT | RECENT (green, 20-40, falling) whipsaw<=3 | `80.0%` | `75.0% (strict 3/4; 80.0% if 2026-11-03 included)` | `DIFF` | Propagated from 2026-11-03 (nfwd=1) counted in n_ws (`OURS`) |
| 258 | `CENSUS.md:75` | (b) RECENT | RECENT (green, 20-40, falling) n_dp | `4` | `4` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 259 | `CENSUS.md:75` | (b) RECENT | RECENT (green, 20-40, falling) median depth | `8.3%` | `8.3%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 260 | `CENSUS.md:75` | (b) RECENT | RECENT (green, 20-40, falling) median bars to extreme | `9.0` | `9.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 261 | `CENSUS.md:76` | (b) RECENT | RECENT (green, 20-40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 262 | `CENSUS.md:76` | (b) RECENT | RECENT (green, 20-40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 263 | `CENSUS.md:76` | (b) RECENT | RECENT (green, 20-40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 264 | `CENSUS.md:77` | (b) RECENT | RECENT (green, >40, falling) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 265 | `CENSUS.md:77` | (b) RECENT | RECENT (green, >40, falling) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 266 | `CENSUS.md:77` | (b) RECENT | RECENT (green, >40, falling) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 267 | `CENSUS.md:78` | (b) RECENT | RECENT (green, >40, rising) n | `0` | `0` | `MATCH` | Bucket count (`OURS`) |
| 268 | `CENSUS.md:78` | (b) RECENT | RECENT (green, >40, rising) n_ws | `0` | `0` | `MATCH` | Cells with >=3 bars after (`OURS`) |
| 269 | `CENSUS.md:78` | (b) RECENT | RECENT (green, >40, rising) n_dp | `0` | `0` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 270 | `CENSUS.md:79` | (b) RECENT | RECENT (all, all, all) n | `17` | `17` | `MATCH` | Bucket count (`OURS`) |
| 271 | `CENSUS.md:79` | (b) RECENT | RECENT (all, all, all) n_ws | `16` | `15 (strict nfwd>=3; 16 if 2026-11-03 whip1=yes included)` | `DIFF` | `CENSUS.md:3` requires k=3 bars after, but 2026-11-03 (nfwd=1, whip1=yes) was counted in n_ws (`OURS`) |
| 272 | `CENSUS.md:79` | (b) RECENT | RECENT (all, all, all) whipsaw<=3 | `50.0%` | `46.7% (strict 7/15; 50.0% if 2026-11-03 included)` | `DIFF` | Propagated from 2026-11-03 (nfwd=1) counted in n_ws (`OURS`) |
| 273 | `CENSUS.md:79` | (b) RECENT | RECENT (all, all, all) n_dp | `14` | `14` | `MATCH` | Cells with nfwd==30 (`OURS`) |
| 274 | `CENSUS.md:79` | (b) RECENT | RECENT (all, all, all) median depth | `15.0%` | `15.0%` | `MATCH` | Median depth over n_dp (`OURS`) |
| 275 | `CENSUS.md:79` | (b) RECENT | RECENT (all, all, all) median bars to extreme | `16.0` | `16.0` | `MATCH` | Median bars to extreme over n_dp (`OURS`) |
| 276 | `CENSUS.md:81` | CCU check | DEV+VALIDATION red crosses n (full 30-bar window) | `35` | `35` | `MATCH` | 28 DEV red + 7 VALIDATION red = 35 (`OURS`) |
| 277 | `CENSUS.md:85` | CCU check | Red crosses bars 1-3 n | `13` | `13` | `MATCH` | Count of red crosses with bars_to_low in 1..3 (`OURS`) |
| 278 | `CENSUS.md:85` | CCU check | Red crosses bars 1-3 share | `37.1%` | `37.1%` | `MATCH` | 13 / 35 (`OURS`) |
| 279 | `CENSUS.md:85` | CCU check | Red crosses bars 1-3 median depth | `-3.6%` | `-3.6%` | `MATCH` | Median depth in 1..3 bucket (`OURS`) |
| 280 | `CENSUS.md:86` | CCU check | Red crosses bars 4-7 n | `7` | `7` | `MATCH` | Count of red crosses with bars_to_low in 4..7 (`OURS`) |
| 281 | `CENSUS.md:86` | CCU check | Red crosses bars 4-7 share | `20.0%` | `20.0%` | `MATCH` | 7 / 35 (`OURS`) |
| 282 | `CENSUS.md:86` | CCU check | Red crosses bars 4-7 median depth | `-7.3%` | `-7.3%` | `MATCH` | Median depth in 4..7 bucket (`OURS`) |
| 283 | `CENSUS.md:87` | CCU check | Red crosses bars 8-12 n | `3` | `3` | `MATCH` | Count of red crosses with bars_to_low in 8..12 (`OURS`) |
| 284 | `CENSUS.md:87` | CCU check | Red crosses bars 8-12 share | `8.6%` | `8.6%` | `MATCH` | 3 / 35 (`OURS`) |
| 285 | `CENSUS.md:87` | CCU check | Red crosses bars 8-12 median depth | `-13.9%` | `-13.9%` | `MATCH` | Median depth in 8..12 bucket (`OURS`) |
| 286 | `CENSUS.md:88` | CCU check | Red crosses bars 13-20 n | `5` | `5` | `MATCH` | Count of red crosses with bars_to_low in 13..20 (`OURS`) |
| 287 | `CENSUS.md:88` | CCU check | Red crosses bars 13-20 share | `14.3%` | `14.3%` | `MATCH` | 5 / 35 (`OURS`) |
| 288 | `CENSUS.md:88` | CCU check | Red crosses bars 13-20 median depth | `-21.6%` | `-21.6%` | `MATCH` | Median depth in 13..20 bucket (`OURS`) |
| 289 | `CENSUS.md:89` | CCU check | Red crosses bars 21-30 n | `7` | `7` | `MATCH` | Count of red crosses with bars_to_low in 21..30 (`OURS`) |
| 290 | `CENSUS.md:89` | CCU check | Red crosses bars 21-30 share | `20.0%` | `20.0%` | `MATCH` | 7 / 35 (`OURS`) |
| 291 | `CENSUS.md:89` | CCU check | Red crosses bars 21-30 median depth | `-22.9%` | `-22.9%` | `MATCH` | Median depth in 21..30 bucket (`OURS`) |
| 292 | `CENSUS.md:97` | (a) 2d cross | 2020-01-05 (green) ADX | `17.1` | `17.1` | `MATCH` | ADX14 at 2020-01-05 = 17.1465 (`OURS`) |
| 293 | `CENSUS.md:97` | (a) 2d cross | 2020-01-05 (green) slope5 | `-3.8` | `-3.8` | `MATCH` | ADX[i]-ADX[i-5] = -3.7971 (`OURS`) |
| 294 | `CENSUS.md:97` | (a) 2d cross | 2020-01-05 (green) bars to extreme | `19` | `19` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 295 | `CENSUS.md:97` | (a) 2d cross | 2020-01-05 (green) depth | `35.3%` | `35.3%` | `MATCH` | extreme / close - 1 = 35.3442% (`OURS`) |
| 296 | `CENSUS.md:97` | (a) 2d cross | 2020-01-05 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 297 | `CENSUS.md:98` | (a) 2d cross | 2020-02-26 (red) ADX | `30.8` | `30.8` | `MATCH` | ADX14 at 2020-02-26 = 30.8308 (`OURS`) |
| 298 | `CENSUS.md:98` | (a) 2d cross | 2020-02-26 (red) slope5 | `-3.6` | `-3.6` | `MATCH` | ADX[i]-ADX[i-5] = -3.5596 (`OURS`) |
| 299 | `CENSUS.md:98` | (a) 2d cross | 2020-02-26 (red) bars to extreme | `8` | `8` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 300 | `CENSUS.md:98` | (a) 2d cross | 2020-02-26 (red) depth | `-57.1%` | `-57.1%` | `MATCH` | extreme / close - 1 = -57.1343% (`OURS`) |
| 301 | `CENSUS.md:98` | (a) 2d cross | 2020-02-26 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 302 | `CENSUS.md:99` | (a) 2d cross | 2020-03-05 (green) ADX | `24.3` | `24.3` | `MATCH` | ADX14 at 2020-03-05 = 24.2797 (`OURS`) |
| 303 | `CENSUS.md:99` | (a) 2d cross | 2020-03-05 (green) slope5 | `-8.5` | `-8.5` | `MATCH` | ADX[i]-ADX[i-5] = -8.5477 (`OURS`) |
| 304 | `CENSUS.md:99` | (a) 2d cross | 2020-03-05 (green) bars to extreme | `28` | `28` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 305 | `CENSUS.md:99` | (a) 2d cross | 2020-03-05 (green) depth | `3.6%` | `3.6%` | `MATCH` | extreme / close - 1 = 3.5931% (`OURS`) |
| 306 | `CENSUS.md:99` | (a) 2d cross | 2020-03-05 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 307 | `CENSUS.md:100` | (a) 2d cross | 2020-03-07 (red) ADX | `23.9` | `23.9` | `MATCH` | ADX14 at 2020-03-07 = 23.8723 (`OURS`) |
| 308 | `CENSUS.md:100` | (a) 2d cross | 2020-03-07 (red) slope5 | `-7.0` | `-7.0` | `MATCH` | ADX[i]-ADX[i-5] = -6.9585 (`OURS`) |
| 309 | `CENSUS.md:100` | (a) 2d cross | 2020-03-07 (red) bars to extreme | `3` | `3` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 310 | `CENSUS.md:100` | (a) 2d cross | 2020-03-07 (red) depth | `-52.9%` | `-52.9%` | `MATCH` | extreme / close - 1 = -52.9194% (`OURS`) |
| 311 | `CENSUS.md:100` | (a) 2d cross | 2020-03-07 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 312 | `CENSUS.md:101` | (a) 2d cross | 2020-04-22 (green) ADX | `19.7` | `19.7` | `MATCH` | ADX14 at 2020-04-22 = 19.6516 (`OURS`) |
| 313 | `CENSUS.md:101` | (a) 2d cross | 2020-04-22 (green) slope5 | `-4.9` | `-4.9` | `MATCH` | ADX[i]-ADX[i-5] = -4.9071 (`OURS`) |
| 314 | `CENSUS.md:101` | (a) 2d cross | 2020-04-22 (green) bars to extreme | `20` | `20` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 315 | `CENSUS.md:101` | (a) 2d cross | 2020-04-22 (green) depth | `38.7%` | `38.7%` | `MATCH` | extreme / close - 1 = 38.7257% (`OURS`) |
| 316 | `CENSUS.md:101` | (a) 2d cross | 2020-04-22 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 317 | `CENSUS.md:102` | (a) 2d cross | 2020-05-24 (red) ADX | `17.3` | `17.3` | `MATCH` | ADX14 at 2020-05-24 = 17.2767 (`OURS`) |
| 318 | `CENSUS.md:102` | (a) 2d cross | 2020-05-24 (red) slope5 | `-4.1` | `-4.1` | `MATCH` | ADX[i]-ADX[i-5] = -4.0975 (`OURS`) |
| 319 | `CENSUS.md:102` | (a) 2d cross | 2020-05-24 (red) bars to extreme | `1` | `1` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 320 | `CENSUS.md:102` | (a) 2d cross | 2020-05-24 (red) depth | `-2.3%` | `-2.3%` | `MATCH` | extreme / close - 1 = -2.2510% (`OURS`) |
| 321 | `CENSUS.md:102` | (a) 2d cross | 2020-05-24 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 322 | `CENSUS.md:103` | (a) 2d cross | 2020-05-28 (green) ADX | `15.5` | `15.5` | `MATCH` | ADX14 at 2020-05-28 = 15.5493 (`OURS`) |
| 323 | `CENSUS.md:103` | (a) 2d cross | 2020-05-28 (green) slope5 | `-5.3` | `-5.3` | `MATCH` | ADX[i]-ADX[i-5] = -5.2644 (`OURS`) |
| 324 | `CENSUS.md:103` | (a) 2d cross | 2020-05-28 (green) bars to extreme | `30` | `30` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 325 | `CENSUS.md:103` | (a) 2d cross | 2020-05-28 (green) depth | `20.9%` | `20.9%` | `MATCH` | extreme / close - 1 = 20.8738% (`OURS`) |
| 326 | `CENSUS.md:103` | (a) 2d cross | 2020-05-28 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 327 | `CENSUS.md:104` | (a) 2d cross | 2020-06-15 (red) ADX | `14.3` | `14.3` | `MATCH` | ADX14 at 2020-06-15 = 14.2868 (`OURS`) |
| 328 | `CENSUS.md:104` | (a) 2d cross | 2020-06-15 (red) slope5 | `-2.0` | `-2.0` | `MATCH` | ADX[i]-ADX[i-5] = -1.9655 (`OURS`) |
| 329 | `CENSUS.md:104` | (a) 2d cross | 2020-06-15 (red) bars to extreme | `6` | `6` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 330 | `CENSUS.md:104` | (a) 2d cross | 2020-06-15 (red) depth | `-7.3%` | `-7.3%` | `MATCH` | extreme / close - 1 = -7.2708% (`OURS`) |
| 331 | `CENSUS.md:104` | (a) 2d cross | 2020-06-15 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 332 | `CENSUS.md:105` | (a) 2d cross | 2020-06-21 (green) ADX | `12.4` | `12.4` | `MATCH` | ADX14 at 2020-06-21 = 12.3724 (`OURS`) |
| 333 | `CENSUS.md:105` | (a) 2d cross | 2020-06-21 (green) slope5 | `-3.4` | `-3.4` | `MATCH` | ADX[i]-ADX[i-5] = -3.4401 (`OURS`) |
| 334 | `CENSUS.md:105` | (a) 2d cross | 2020-06-21 (green) bars to extreme | `28` | `28` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 335 | `CENSUS.md:105` | (a) 2d cross | 2020-06-21 (green) depth | `28.7%` | `28.7%` | `MATCH` | extreme / close - 1 = 28.7260% (`OURS`) |
| 336 | `CENSUS.md:105` | (a) 2d cross | 2020-06-21 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 337 | `CENSUS.md:106` | (a) 2d cross | 2020-06-25 (red) ADX | `11.1` | `11.1` | `MATCH` | ADX14 at 2020-06-25 = 11.1127 (`OURS`) |
| 338 | `CENSUS.md:106` | (a) 2d cross | 2020-06-25 (red) slope5 | `-3.2` | `-3.2` | `MATCH` | ADX[i]-ADX[i-5] = -3.1741 (`OURS`) |
| 339 | `CENSUS.md:106` | (a) 2d cross | 2020-06-25 (red) bars to extreme | `1` | `1` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 340 | `CENSUS.md:106` | (a) 2d cross | 2020-06-25 (red) depth | `-3.6%` | `-3.6%` | `MATCH` | extreme / close - 1 = -3.5931% (`OURS`) |
| 341 | `CENSUS.md:106` | (a) 2d cross | 2020-06-25 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 342 | `CENSUS.md:107` | (a) 2d cross | 2020-07-07 (green) ADX | `9.4` | `9.4` | `MATCH` | ADX14 at 2020-07-07 = 9.3852 (`OURS`) |
| 343 | `CENSUS.md:107` | (a) 2d cross | 2020-07-07 (green) slope5 | `-1.6` | `-1.6` | `MATCH` | ADX[i]-ADX[i-5] = -1.5574 (`OURS`) |
| 344 | `CENSUS.md:107` | (a) 2d cross | 2020-07-07 (green) bars to extreme | `20` | `20` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 345 | `CENSUS.md:107` | (a) 2d cross | 2020-07-07 (green) depth | `32.1%` | `32.1%` | `MATCH` | extreme / close - 1 = 32.1314% (`OURS`) |
| 346 | `CENSUS.md:107` | (a) 2d cross | 2020-07-07 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 347 | `CENSUS.md:108` | (a) 2d cross | 2020-07-09 (red) ADX | `8.8` | `8.8` | `MATCH` | ADX14 at 2020-07-09 = 8.8303 (`OURS`) |
| 348 | `CENSUS.md:108` | (a) 2d cross | 2020-07-09 (red) slope5 | `-1.8` | `-1.8` | `MATCH` | ADX[i]-ADX[i-5] = -1.8440 (`OURS`) |
| 349 | `CENSUS.md:108` | (a) 2d cross | 2020-07-09 (red) bars to extreme | `3` | `3` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 350 | `CENSUS.md:108` | (a) 2d cross | 2020-07-09 (red) depth | `-2.6%` | `-2.6%` | `MATCH` | extreme / close - 1 = -2.5956% (`OURS`) |
| 351 | `CENSUS.md:108` | (a) 2d cross | 2020-07-09 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 352 | `CENSUS.md:109` | (a) 2d cross | 2020-07-21 (green) ADX | `7.9` | `7.9` | `MATCH` | ADX14 at 2020-07-21 = 7.9133 (`OURS`) |
| 353 | `CENSUS.md:109` | (a) 2d cross | 2020-07-21 (green) slope5 | `-0.4` | `-0.4` | `MATCH` | ADX[i]-ADX[i-5] = -0.4017 (`OURS`) |
| 354 | `CENSUS.md:109` | (a) 2d cross | 2020-07-21 (green) bars to extreme | `13` | `13` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 355 | `CENSUS.md:109` | (a) 2d cross | 2020-07-21 (green) depth | `31.0%` | `31.0%` | `MATCH` | extreme / close - 1 = 30.9917% (`OURS`) |
| 356 | `CENSUS.md:109` | (a) 2d cross | 2020-07-21 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 357 | `CENSUS.md:110` | (a) 2d cross | 2020-09-03 (red) ADX | `26.1` | `26.1` | `MATCH` | ADX14 at 2020-09-03 = 26.1003 (`OURS`) |
| 358 | `CENSUS.md:110` | (a) 2d cross | 2020-09-03 (red) slope5 | `-2.8` | `-2.8` | `MATCH` | ADX[i]-ADX[i-5] = -2.8059 (`OURS`) |
| 359 | `CENSUS.md:110` | (a) 2d cross | 2020-09-03 (red) bars to extreme | `1` | `1` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 360 | `CENSUS.md:110` | (a) 2d cross | 2020-09-03 (red) depth | `-5.9%` | `-5.9%` | `MATCH` | extreme / close - 1 = -5.9471% (`OURS`) |
| 361 | `CENSUS.md:110` | (a) 2d cross | 2020-09-03 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 362 | `CENSUS.md:111` | (a) 2d cross | 2020-09-19 (green) ADX | `20.8` | `20.8` | `MATCH` | ADX14 at 2020-09-19 = 20.8328 (`OURS`) |
| 363 | `CENSUS.md:111` | (a) 2d cross | 2020-09-19 (green) slope5 | `-5.5` | `-5.5` | `MATCH` | ADX[i]-ADX[i-5] = -5.4990 (`OURS`) |
| 364 | `CENSUS.md:111` | (a) 2d cross | 2020-09-19 (green) bars to extreme | `30` | `30` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 365 | `CENSUS.md:111` | (a) 2d cross | 2020-09-19 (green) depth | `69.2%` | `69.2%` | `MATCH` | extreme / close - 1 = 69.1983% (`OURS`) |
| 366 | `CENSUS.md:111` | (a) 2d cross | 2020-09-19 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 367 | `CENSUS.md:112` | (a) 2d cross | 2020-09-21 (red) ADX | `20.2` | `20.2` | `MATCH` | ADX14 at 2020-09-21 = 20.1580 (`OURS`) |
| 368 | `CENSUS.md:112` | (a) 2d cross | 2020-09-21 (red) slope5 | `-6.2` | `-6.2` | `MATCH` | ADX[i]-ADX[i-5] = -6.1547 (`OURS`) |
| 369 | `CENSUS.md:112` | (a) 2d cross | 2020-09-21 (red) bars to extreme | `1` | `1` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 370 | `CENSUS.md:112` | (a) 2d cross | 2020-09-21 (red) depth | `-3.7%` | `-3.7%` | `MATCH` | extreme / close - 1 = -3.7303% (`OURS`) |
| 371 | `CENSUS.md:112` | (a) 2d cross | 2020-09-21 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 372 | `CENSUS.md:113` | (a) 2d cross | 2020-10-09 (green) ADX | `16.9` | `16.9` | `MATCH` | ADX14 at 2020-10-09 = 16.9213 (`OURS`) |
| 373 | `CENSUS.md:113` | (a) 2d cross | 2020-10-09 (green) slope5 | `-1.2` | `-1.2` | `MATCH` | ADX[i]-ADX[i-5] = -1.2401 (`OURS`) |
| 374 | `CENSUS.md:113` | (a) 2d cross | 2020-10-09 (green) bars to extreme | `26` | `26` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 375 | `CENSUS.md:113` | (a) 2d cross | 2020-10-09 (green) depth | `76.1%` | `76.1%` | `MATCH` | extreme / close - 1 = 76.1057% (`OURS`) |
| 376 | `CENSUS.md:113` | (a) 2d cross | 2020-10-09 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 377 | `CENSUS.md:114` | (a) 2d cross | 2021-04-17 (red) ADX | `27.6` | `27.6` | `MATCH` | ADX14 at 2021-04-17 = 27.5728 (`OURS`) |
| 378 | `CENSUS.md:114` | (a) 2d cross | 2021-04-17 (red) slope5 | `-2.1` | `-2.1` | `MATCH` | ADX[i]-ADX[i-5] = -2.0735 (`OURS`) |
| 379 | `CENSUS.md:114` | (a) 2d cross | 2021-04-17 (red) bars to extreme | `16` | `16` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 380 | `CENSUS.md:114` | (a) 2d cross | 2021-04-17 (red) depth | `-46.6%` | `-46.6%` | `MATCH` | extreme / close - 1 = -46.5717% (`OURS`) |
| 381 | `CENSUS.md:114` | (a) 2d cross | 2021-04-17 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 382 | `CENSUS.md:115` | (a) 2d cross | 2021-07-28 (green) ADX | `41.1` | `41.1` | `MATCH` | ADX14 at 2021-07-28 = 41.0666 (`OURS`) |
| 383 | `CENSUS.md:115` | (a) 2d cross | 2021-07-28 (green) slope5 | `-7.2` | `-7.2` | `MATCH` | ADX[i]-ADX[i-5] = -7.2304 (`OURS`) |
| 384 | `CENSUS.md:115` | (a) 2d cross | 2021-07-28 (green) bars to extreme | `20` | `20` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 385 | `CENSUS.md:115` | (a) 2d cross | 2021-07-28 (green) depth | `32.2%` | `32.2%` | `MATCH` | extreme / close - 1 = 32.2455% (`OURS`) |
| 386 | `CENSUS.md:115` | (a) 2d cross | 2021-07-28 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 387 | `CENSUS.md:116` | (a) 2d cross | 2021-09-06 (red) ADX | `30.5` | `30.5` | `MATCH` | ADX14 at 2021-09-06 = 30.5052 (`OURS`) |
| 388 | `CENSUS.md:116` | (a) 2d cross | 2021-09-06 (red) slope5 | `-1.9` | `-1.9` | `MATCH` | ADX[i]-ADX[i-5] = -1.8534 (`OURS`) |
| 389 | `CENSUS.md:116` | (a) 2d cross | 2021-09-06 (red) bars to extreme | `7` | `7` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 390 | `CENSUS.md:116` | (a) 2d cross | 2021-09-06 (red) depth | `-15.5%` | `-15.5%` | `MATCH` | extreme / close - 1 = -15.4997% (`OURS`) |
| 391 | `CENSUS.md:116` | (a) 2d cross | 2021-09-06 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 392 | `CENSUS.md:117` | (a) 2d cross | 2021-09-16 (green) ADX | `22.3` | `22.3` | `MATCH` | ADX14 at 2021-09-16 = 22.2738 (`OURS`) |
| 393 | `CENSUS.md:117` | (a) 2d cross | 2021-09-16 (green) slope5 | `-8.2` | `-8.2` | `MATCH` | ADX[i]-ADX[i-5] = -8.2314 (`OURS`) |
| 394 | `CENSUS.md:117` | (a) 2d cross | 2021-09-16 (green) bars to extreme | `27` | `27` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 395 | `CENSUS.md:117` | (a) 2d cross | 2021-09-16 (green) depth | `45.9%` | `45.9%` | `MATCH` | extreme / close - 1 = 45.8774% (`OURS`) |
| 396 | `CENSUS.md:117` | (a) 2d cross | 2021-09-16 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 397 | `CENSUS.md:118` | (a) 2d cross | 2021-09-20 (red) ADX | `21.6` | `21.6` | `MATCH` | ADX14 at 2021-09-20 = 21.5868 (`OURS`) |
| 398 | `CENSUS.md:118` | (a) 2d cross | 2021-09-20 (red) slope5 | `-5.4` | `-5.4` | `MATCH` | ADX[i]-ADX[i-5] = -5.4360 (`OURS`) |
| 399 | `CENSUS.md:118` | (a) 2d cross | 2021-09-20 (red) bars to extreme | `1` | `1` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 400 | `CENSUS.md:118` | (a) 2d cross | 2021-09-20 (red) depth | `-0.4%` | `-0.4%` | `MATCH` | extreme / close - 1 = -0.4149% (`OURS`) |
| 401 | `CENSUS.md:118` | (a) 2d cross | 2021-09-20 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 402 | `CENSUS.md:119` | (a) 2d cross | 2021-09-30 (green) ADX | `22.5` | `22.5` | `MATCH` | ADX14 at 2021-09-30 = 22.4915 (`OURS`) |
| 403 | `CENSUS.md:119` | (a) 2d cross | 2021-09-30 (green) slope5 | `0.9` | `0.9` | `MATCH` | ADX[i]-ADX[i-5] = 0.9046 (`OURS`) |
| 404 | `CENSUS.md:119` | (a) 2d cross | 2021-09-30 (green) bars to extreme | `20` | `20` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 405 | `CENSUS.md:119` | (a) 2d cross | 2021-09-30 (green) depth | `43.3%` | `43.3%` | `MATCH` | extreme / close - 1 = 43.3272% (`OURS`) |
| 406 | `CENSUS.md:119` | (a) 2d cross | 2021-09-30 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 407 | `CENSUS.md:120` | (a) 2d cross | 2021-11-25 (red) ADX | `27.6` | `27.6` | `MATCH` | ADX14 at 2021-11-25 = 27.5895 (`OURS`) |
| 408 | `CENSUS.md:120` | (a) 2d cross | 2021-11-25 (red) slope5 | `-10.2` | `-10.2` | `MATCH` | ADX[i]-ADX[i-5] = -10.1715 (`OURS`) |
| 409 | `CENSUS.md:120` | (a) 2d cross | 2021-11-25 (red) bars to extreme | `30` | `30` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 410 | `CENSUS.md:120` | (a) 2d cross | 2021-11-25 (red) depth | `-38.7%` | `-38.7%` | `MATCH` | extreme / close - 1 = -38.7320% (`OURS`) |
| 411 | `CENSUS.md:120` | (a) 2d cross | 2021-11-25 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 412 | `CENSUS.md:121` | (a) 2d cross | 2021-11-29 (green) ADX | `24.4` | `24.4` | `MATCH` | ADX14 at 2021-11-29 = 24.4409 (`OURS`) |
| 413 | `CENSUS.md:121` | (a) 2d cross | 2021-11-29 (green) slope5 | `-8.9` | `-8.9` | `MATCH` | ADX[i]-ADX[i-5] = -8.8746 (`OURS`) |
| 414 | `CENSUS.md:121` | (a) 2d cross | 2021-11-29 (green) bars to extreme | `1` | `1` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 415 | `CENSUS.md:121` | (a) 2d cross | 2021-11-29 (green) depth | `3.7%` | `3.7%` | `MATCH` | extreme / close - 1 = 3.6927% (`OURS`) |
| 416 | `CENSUS.md:121` | (a) 2d cross | 2021-11-29 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 417 | `CENSUS.md:122` | (a) 2d cross | 2021-12-03 (red) ADX | `24.3` | `24.3` | `MATCH` | ADX14 at 2021-12-03 = 24.3393 (`OURS`) |
| 418 | `CENSUS.md:122` | (a) 2d cross | 2021-12-03 (red) slope5 | `-4.9` | `-4.9` | `MATCH` | ADX[i]-ADX[i-5] = -4.8695 (`OURS`) |
| 419 | `CENSUS.md:122` | (a) 2d cross | 2021-12-03 (red) bars to extreme | `26` | `26` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 420 | `CENSUS.md:122` | (a) 2d cross | 2021-12-03 (red) depth | `-33.0%` | `-33.0%` | `MATCH` | extreme / close - 1 = -33.0305% (`OURS`) |
| 421 | `CENSUS.md:122` | (a) 2d cross | 2021-12-03 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 422 | `CENSUS.md:123` | (a) 2d cross | 2022-02-15 (green) ADX | `30.7` | `30.7` | `MATCH` | ADX14 at 2022-02-15 = 30.6822 (`OURS`) |
| 423 | `CENSUS.md:123` | (a) 2d cross | 2022-02-15 (green) slope5 | `-11.5` | `-11.5` | `MATCH` | ADX[i]-ADX[i-5] = -11.4723 (`OURS`) |
| 424 | `CENSUS.md:123` | (a) 2d cross | 2022-02-15 (green) bars to extreme | `20` | `20` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 425 | `CENSUS.md:123` | (a) 2d cross | 2022-02-15 (green) depth | `9.8%` | `9.8%` | `MATCH` | extreme / close - 1 = 9.8380% (`OURS`) |
| 426 | `CENSUS.md:123` | (a) 2d cross | 2022-02-15 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 427 | `CENSUS.md:124` | (a) 2d cross | 2022-02-17 (red) ADX | `29.5` | `29.5` | `MATCH` | ADX14 at 2022-02-17 = 29.4566 (`OURS`) |
| 428 | `CENSUS.md:124` | (a) 2d cross | 2022-02-17 (red) slope5 | `-9.9` | `-9.9` | `MATCH` | ADX[i]-ADX[i-5] = -9.9086 (`OURS`) |
| 429 | `CENSUS.md:124` | (a) 2d cross | 2022-02-17 (red) bars to extreme | `3` | `3` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 430 | `CENSUS.md:124` | (a) 2d cross | 2022-02-17 (red) depth | `-14.1%` | `-14.1%` | `MATCH` | extreme / close - 1 = -14.1394% (`OURS`) |
| 431 | `CENSUS.md:124` | (a) 2d cross | 2022-02-17 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 432 | `CENSUS.md:125` | (a) 2d cross | 2022-03-17 (green) ADX | `19.0` | `19.0` | `MATCH` | ADX14 at 2022-03-17 = 18.9962 (`OURS`) |
| 433 | `CENSUS.md:125` | (a) 2d cross | 2022-03-17 (green) slope5 | `-5.8` | `-5.8` | `MATCH` | ADX[i]-ADX[i-5] = -5.7878 (`OURS`) |
| 434 | `CENSUS.md:125` | (a) 2d cross | 2022-03-17 (green) bars to extreme | `5` | `5` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 435 | `CENSUS.md:125` | (a) 2d cross | 2022-03-17 (green) depth | `15.4%` | `15.4%` | `MATCH` | extreme / close - 1 = 15.4040% (`OURS`) |
| 436 | `CENSUS.md:125` | (a) 2d cross | 2022-03-17 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 437 | `CENSUS.md:126` | (a) 2d cross | 2022-04-06 (red) ADX | `15.7` | `15.7` | `MATCH` | ADX14 at 2022-04-06 = 15.7319 (`OURS`) |
| 438 | `CENSUS.md:126` | (a) 2d cross | 2022-04-06 (red) slope5 | `-1.3` | `-1.3` | `MATCH` | ADX[i]-ADX[i-5] = -1.2808 (`OURS`) |
| 439 | `CENSUS.md:126` | (a) 2d cross | 2022-04-06 (red) bars to extreme | `18` | `18` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 440 | `CENSUS.md:126` | (a) 2d cross | 2022-04-06 (red) depth | `-38.5%` | `-38.5%` | `MATCH` | extreme / close - 1 = -38.5418% (`OURS`) |
| 441 | `CENSUS.md:126` | (a) 2d cross | 2022-04-06 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 442 | `CENSUS.md:127` | (a) 2d cross | 2022-08-10 (green) ADX | `21.3` | `21.3` | `MATCH` | ADX14 at 2022-08-10 = 21.2634 (`OURS`) |
| 443 | `CENSUS.md:127` | (a) 2d cross | 2022-08-10 (green) slope5 | `-6.8` | `-6.8` | `MATCH` | ADX[i]-ADX[i-5] = -6.7607 (`OURS`) |
| 444 | `CENSUS.md:127` | (a) 2d cross | 2022-08-10 (green) bars to extreme | `2` | `2` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 445 | `CENSUS.md:127` | (a) 2d cross | 2022-08-10 (green) depth | `5.3%` | `5.3%` | `MATCH` | extreme / close - 1 = 5.3351% (`OURS`) |
| 446 | `CENSUS.md:127` | (a) 2d cross | 2022-08-10 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 447 | `CENSUS.md:128` | (a) 2d cross | 2022-08-18 (red) ADX | `18.4` | `18.4` | `MATCH` | ADX14 at 2022-08-18 = 18.4258 (`OURS`) |
| 448 | `CENSUS.md:128` | (a) 2d cross | 2022-08-18 (red) slope5 | `-4.0` | `-4.0` | `MATCH` | ADX[i]-ADX[i-5] = -3.9623 (`OURS`) |
| 449 | `CENSUS.md:128` | (a) 2d cross | 2022-08-18 (red) bars to extreme | `17` | `17` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 450 | `CENSUS.md:128` | (a) 2d cross | 2022-08-18 (red) depth | `-13.0%` | `-13.0%` | `MATCH` | extreme / close - 1 = -12.9997% (`OURS`) |
| 451 | `CENSUS.md:128` | (a) 2d cross | 2022-08-18 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 452 | `CENSUS.md:129` | (a) 2d cross | 2022-09-11 (green) ADX | `21.4` | `21.4` | `MATCH` | ADX14 at 2022-09-11 = 21.3776 (`OURS`) |
| 453 | `CENSUS.md:129` | (a) 2d cross | 2022-09-11 (green) slope5 | `-0.0` | `-0.0` | `MATCH` | ADX[i]-ADX[i-5] = -0.0401 (`OURS`) |
| 454 | `CENSUS.md:129` | (a) 2d cross | 2022-09-11 (green) bars to extreme | `1` | `1` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 455 | `CENSUS.md:129` | (a) 2d cross | 2022-09-11 (green) depth | `1.8%` | `1.8%` | `MATCH` | extreme / close - 1 = 1.8006% (`OURS`) |
| 456 | `CENSUS.md:129` | (a) 2d cross | 2022-09-11 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 457 | `CENSUS.md:130` | (a) 2d cross | 2022-09-13 (red) ADX | `20.8` | `20.8` | `MATCH` | ADX14 at 2022-09-13 = 20.8044 (`OURS`) |
| 458 | `CENSUS.md:130` | (a) 2d cross | 2022-09-13 (red) slope5 | `-1.2` | `-1.2` | `MATCH` | ADX[i]-ADX[i-5] = -1.1592 (`OURS`) |
| 459 | `CENSUS.md:130` | (a) 2d cross | 2022-09-13 (red) bars to extreme | `28` | `28` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 460 | `CENSUS.md:130` | (a) 2d cross | 2022-09-13 (red) depth | `-22.9%` | `-22.9%` | `MATCH` | extreme / close - 1 = -22.9336% (`OURS`) |
| 461 | `CENSUS.md:130` | (a) 2d cross | 2022-09-13 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 462 | `CENSUS.md:131` | (a) 2d cross | 2022-10-03 (green) ADX | `17.2` | `17.2` | `MATCH` | ADX14 at 2022-10-03 = 17.1767 (`OURS`) |
| 463 | `CENSUS.md:131` | (a) 2d cross | 2022-10-03 (green) slope5 | `-3.5` | `-3.5` | `MATCH` | ADX[i]-ADX[i-5] = -3.5394 (`OURS`) |
| 464 | `CENSUS.md:131` | (a) 2d cross | 2022-10-03 (green) bars to extreme | `16` | `16` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 465 | `CENSUS.md:131` | (a) 2d cross | 2022-10-03 (green) depth | `5.6%` | `5.6%` | `MATCH` | extreme / close - 1 = 5.6192% (`OURS`) |
| 466 | `CENSUS.md:131` | (a) 2d cross | 2022-10-03 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 467 | `CENSUS.md:132` | (a) 2d cross | 2022-10-07 (red) ADX | `15.3` | `15.3` | `MATCH` | ADX14 at 2022-10-07 = 15.2997 (`OURS`) |
| 468 | `CENSUS.md:132` | (a) 2d cross | 2022-10-07 (red) slope5 | `-4.5` | `-4.5` | `MATCH` | ADX[i]-ADX[i-5] = -4.4801 (`OURS`) |
| 469 | `CENSUS.md:132` | (a) 2d cross | 2022-10-07 (red) bars to extreme | `22` | `22` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 470 | `CENSUS.md:132` | (a) 2d cross | 2022-10-07 (red) depth | `-20.3%` | `-20.3%` | `MATCH` | extreme / close - 1 = -20.3006% (`OURS`) |
| 471 | `CENSUS.md:132` | (a) 2d cross | 2022-10-07 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 472 | `CENSUS.md:133` | (a) 2d cross | 2022-10-13 (green) ADX | `13.2` | `13.2` | `MATCH` | ADX14 at 2022-10-13 = 13.1925 (`OURS`) |
| 473 | `CENSUS.md:133` | (a) 2d cross | 2022-10-13 (green) slope5 | `-4.0` | `-4.0` | `MATCH` | ADX[i]-ADX[i-5] = -3.9842 (`OURS`) |
| 474 | `CENSUS.md:133` | (a) 2d cross | 2022-10-13 (green) bars to extreme | `11` | `11` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 475 | `CENSUS.md:133` | (a) 2d cross | 2022-10-13 (green) depth | `12.0%` | `12.0%` | `MATCH` | extreme / close - 1 = 12.0130% (`OURS`) |
| 476 | `CENSUS.md:133` | (a) 2d cross | 2022-10-13 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 477 | `CENSUS.md:134` | (a) 2d cross | 2022-11-08 (red) ADX | `18.2` | `18.2` | `MATCH` | ADX14 at 2022-11-08 = 18.2336 (`OURS`) |
| 478 | `CENSUS.md:134` | (a) 2d cross | 2022-11-08 (red) slope5 | `3.9` | `3.9` | `MATCH` | ADX[i]-ADX[i-5] = 3.9238 (`OURS`) |
| 479 | `CENSUS.md:134` | (a) 2d cross | 2022-11-08 (red) bars to extreme | `6` | `6` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 480 | `CENSUS.md:134` | (a) 2d cross | 2022-11-08 (red) depth | `-2.8%` | `-2.8%` | `MATCH` | extreme / close - 1 = -2.8061% (`OURS`) |
| 481 | `CENSUS.md:134` | (a) 2d cross | 2022-11-08 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 482 | `CENSUS.md:135` | (a) 2d cross | 2022-12-14 (green) ADX | `25.3` | `25.3` | `MATCH` | ADX14 at 2022-12-14 = 25.3252 (`OURS`) |
| 483 | `CENSUS.md:135` | (a) 2d cross | 2022-12-14 (green) slope5 | `-4.7` | `-4.7` | `MATCH` | ADX[i]-ADX[i-5] = -4.7130 (`OURS`) |
| 484 | `CENSUS.md:135` | (a) 2d cross | 2022-12-14 (green) bars to extreme | `25` | `25` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 485 | `CENSUS.md:135` | (a) 2d cross | 2022-12-14 (green) depth | `39.7%` | `39.7%` | `MATCH` | extreme / close - 1 = 39.7472% (`OURS`) |
| 486 | `CENSUS.md:135` | (a) 2d cross | 2022-12-14 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 487 | `CENSUS.md:136` | (a) 2d cross | 2022-12-16 (red) ADX | `24.3` | `24.3` | `MATCH` | ADX14 at 2022-12-16 = 24.3292 (`OURS`) |
| 488 | `CENSUS.md:136` | (a) 2d cross | 2022-12-16 (red) slope5 | `-5.5` | `-5.5` | `MATCH` | ADX[i]-ADX[i-5] = -5.5086 (`OURS`) |
| 489 | `CENSUS.md:136` | (a) 2d cross | 2022-12-16 (red) bars to extreme | `1` | `1` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 490 | `CENSUS.md:136` | (a) 2d cross | 2022-12-16 (red) depth | `-3.1%` | `-3.1%` | `MATCH` | extreme / close - 1 = -3.1009% (`OURS`) |
| 491 | `CENSUS.md:136` | (a) 2d cross | 2022-12-16 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 492 | `CENSUS.md:137` | (a) 2d cross | 2023-01-09 (green) ADX | `16.6` | `16.6` | `MATCH` | ADX14 at 2023-01-09 = 16.5831 (`OURS`) |
| 493 | `CENSUS.md:137` | (a) 2d cross | 2023-01-09 (green) slope5 | `-3.8` | `-3.8` | `MATCH` | ADX[i]-ADX[i-5] = -3.7629 (`OURS`) |
| 494 | `CENSUS.md:137` | (a) 2d cross | 2023-01-09 (green) bars to extreme | `19` | `19` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 495 | `CENSUS.md:137` | (a) 2d cross | 2023-01-09 (green) depth | `44.8%` | `44.8%` | `MATCH` | extreme / close - 1 = 44.7766% (`OURS`) |
| 496 | `CENSUS.md:137` | (a) 2d cross | 2023-01-09 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 497 | `CENSUS.md:138` | (a) 2d cross | 2023-03-08 (red) ADX | `34.8` | `34.8` | `MATCH` | ADX14 at 2023-03-08 = 34.7620 (`OURS`) |
| 498 | `CENSUS.md:138` | (a) 2d cross | 2023-03-08 (red) slope5 | `-9.4` | `-9.4` | `MATCH` | ADX[i]-ADX[i-5] = -9.3659 (`OURS`) |
| 499 | `CENSUS.md:138` | (a) 2d cross | 2023-03-08 (red) bars to extreme | `1` | `1` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 500 | `CENSUS.md:138` | (a) 2d cross | 2023-03-08 (red) depth | `-4.0%` | `-4.0%` | `MATCH` | extreme / close - 1 = -3.9933% (`OURS`) |
| 501 | `CENSUS.md:138` | (a) 2d cross | 2023-03-08 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 502 | `CENSUS.md:139` | (a) 2d cross | 2023-03-12 (green) ADX | `33.0` | `33.0` | `MATCH` | ADX14 at 2023-03-12 = 33.0078 (`OURS`) |
| 503 | `CENSUS.md:139` | (a) 2d cross | 2023-03-12 (green) slope5 | `-7.5` | `-7.5` | `MATCH` | ADX[i]-ADX[i-5] = -7.4903 (`OURS`) |
| 504 | `CENSUS.md:139` | (a) 2d cross | 2023-03-12 (green) bars to extreme | `16` | `16` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 505 | `CENSUS.md:139` | (a) 2d cross | 2023-03-12 (green) depth | `28.6%` | `28.6%` | `MATCH` | extreme / close - 1 = 28.5588% (`OURS`) |
| 506 | `CENSUS.md:139` | (a) 2d cross | 2023-03-12 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 507 | `CENSUS.md:140` | (a) 2d cross | 2023-05-07 (red) ADX | `22.9` | `22.9` | `MATCH` | ADX14 at 2023-05-07 = 22.9048 (`OURS`) |
| 508 | `CENSUS.md:140` | (a) 2d cross | 2023-05-07 (red) slope5 | `-6.3` | `-6.3` | `MATCH` | ADX[i]-ADX[i-5] = -6.3343 (`OURS`) |
| 509 | `CENSUS.md:140` | (a) 2d cross | 2023-05-07 (red) bars to extreme | `19` | `19` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 510 | `CENSUS.md:140` | (a) 2d cross | 2023-05-07 (red) depth | `-10.4%` | `-10.4%` | `MATCH` | extreme / close - 1 = -10.3683% (`OURS`) |
| 511 | `CENSUS.md:140` | (a) 2d cross | 2023-05-07 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 512 | `CENSUS.md:141` | (a) 2d cross | 2023-05-27 (green) ADX | `17.7` | `17.7` | `MATCH` | ADX14 at 2023-05-27 = 17.6731 (`OURS`) |
| 513 | `CENSUS.md:141` | (a) 2d cross | 2023-05-27 (green) slope5 | `-2.2` | `-2.2` | `MATCH` | ADX[i]-ADX[i-5] = -2.1671 (`OURS`) |
| 514 | `CENSUS.md:141` | (a) 2d cross | 2023-05-27 (green) bars to extreme | `23` | `23` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 515 | `CENSUS.md:141` | (a) 2d cross | 2023-05-27 (green) depth | `13.3%` | `13.3%` | `MATCH` | extreme / close - 1 = 13.3234% (`OURS`) |
| 516 | `CENSUS.md:141` | (a) 2d cross | 2023-05-27 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 517 | `CENSUS.md:142` | (a) 2d cross | 2023-05-31 (red) ADX | `16.1` | `16.1` | `MATCH` | ADX14 at 2023-05-31 = 16.0925 (`OURS`) |
| 518 | `CENSUS.md:142` | (a) 2d cross | 2023-05-31 (red) slope5 | `-2.9` | `-2.9` | `MATCH` | ADX[i]-ADX[i-5] = -2.8616 (`OURS`) |
| 519 | `CENSUS.md:142` | (a) 2d cross | 2023-05-31 (red) bars to extreme | `7` | `7` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 520 | `CENSUS.md:142` | (a) 2d cross | 2023-05-31 (red) depth | `-7.5%` | `-7.5%` | `MATCH` | extreme / close - 1 = -7.5246% (`OURS`) |
| 521 | `CENSUS.md:142` | (a) 2d cross | 2023-05-31 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 522 | `CENSUS.md:143` | (a) 2d cross | 2023-06-20 (green) ADX | `21.5` | `21.5` | `MATCH` | ADX14 at 2023-06-20 = 21.4548 (`OURS`) |
| 523 | `CENSUS.md:143` | (a) 2d cross | 2023-06-20 (green) slope5 | `3.0` | `3.0` | `MATCH` | ADX[i]-ADX[i-5] = 3.0391 (`OURS`) |
| 524 | `CENSUS.md:143` | (a) 2d cross | 2023-06-20 (green) bars to extreme | `11` | `11` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 525 | `CENSUS.md:143` | (a) 2d cross | 2023-06-20 (green) depth | `6.0%` | `6.0%` | `MATCH` | extreme / close - 1 = 6.0356% (`OURS`) |
| 526 | `CENSUS.md:143` | (a) 2d cross | 2023-06-20 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 527 | `CENSUS.md:144` | (a) 2d cross | 2023-08-17 (red) ADX | `21.8` | `21.8` | `MATCH` | ADX14 at 2023-08-17 = 21.8100 (`OURS`) |
| 528 | `CENSUS.md:144` | (a) 2d cross | 2023-08-17 (red) slope5 | `2.9` | `2.9` | `MATCH` | ADX[i]-ADX[i-5] = 2.8551 (`OURS`) |
| 529 | `CENSUS.md:144` | (a) 2d cross | 2023-08-17 (red) bars to extreme | `12` | `12` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 530 | `CENSUS.md:144` | (a) 2d cross | 2023-08-17 (red) depth | `-4.4%` | `-4.4%` | `MATCH` | extreme / close - 1 = -4.4254% (`OURS`) |
| 531 | `CENSUS.md:144` | (a) 2d cross | 2023-08-17 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 532 | `CENSUS.md:145` | (a) 2d cross | 2023-08-29 (green) ADX | `24.2` | `24.2` | `MATCH` | ADX14 at 2023-08-29 = 24.2380 (`OURS`) |
| 533 | `CENSUS.md:145` | (a) 2d cross | 2023-08-29 (green) slope5 | `1.2` | `1.2` | `MATCH` | ADX[i]-ADX[i-5] = 1.1918 (`OURS`) |
| 534 | `CENSUS.md:145` | (a) 2d cross | 2023-08-29 (green) bars to extreme | `28` | `28` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 535 | `CENSUS.md:145` | (a) 2d cross | 2023-08-29 (green) depth | `29.2%` | `29.2%` | `MATCH` | extreme / close - 1 = 29.2308% (`OURS`) |
| 536 | `CENSUS.md:145` | (a) 2d cross | 2023-08-29 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 537 | `CENSUS.md:146` | (a) 2d cross | 2023-08-31 (red) ADX | `23.0` | `23.0` | `MATCH` | ADX14 at 2023-08-31 = 23.0304 (`OURS`) |
| 538 | `CENSUS.md:146` | (a) 2d cross | 2023-08-31 (red) slope5 | `-1.5` | `-1.5` | `MATCH` | ADX[i]-ADX[i-5] = -1.4726 (`OURS`) |
| 539 | `CENSUS.md:146` | (a) 2d cross | 2023-08-31 (red) bars to extreme | `5` | `5` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 540 | `CENSUS.md:146` | (a) 2d cross | 2023-08-31 (red) depth | `-3.5%` | `-3.5%` | `MATCH` | extreme / close - 1 = -3.5034% (`OURS`) |
| 541 | `CENSUS.md:146` | (a) 2d cross | 2023-08-31 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 542 | `CENSUS.md:147` | (a) 2d cross | 2023-09-18 (green) ADX | `15.0` | `15.0` | `MATCH` | ADX14 at 2023-09-18 = 14.9552 (`OURS`) |
| 543 | `CENSUS.md:147` | (a) 2d cross | 2023-09-18 (green) slope5 | `-3.8` | `-3.8` | `MATCH` | ADX[i]-ADX[i-5] = -3.7973 (`OURS`) |
| 544 | `CENSUS.md:147` | (a) 2d cross | 2023-09-18 (green) bars to extreme | `29` | `29` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 545 | `CENSUS.md:147` | (a) 2d cross | 2023-09-18 (green) depth | `39.6%` | `39.6%` | `MATCH` | extreme / close - 1 = 39.5797% (`OURS`) |
| 546 | `CENSUS.md:147` | (a) 2d cross | 2023-09-18 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 547 | `CENSUS.md:148` | (a) 2d cross | 2024-01-22 (red) ADX | `28.6` | `28.6` | `MATCH` | ADX14 at 2024-01-22 = 28.5756 (`OURS`) |
| 548 | `CENSUS.md:148` | (a) 2d cross | 2024-01-22 (red) slope5 | `-6.6` | `-6.6` | `MATCH` | ADX[i]-ADX[i-5] = -6.5757 (`OURS`) |
| 549 | `CENSUS.md:148` | (a) 2d cross | 2024-01-22 (red) bars to extreme | `1` | `1` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 550 | `CENSUS.md:148` | (a) 2d cross | 2024-01-22 (red) depth | `-1.0%` | `-1.0%` | `MATCH` | extreme / close - 1 = -1.0362% (`OURS`) |
| 551 | `CENSUS.md:148` | (a) 2d cross | 2024-01-22 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 552 | `CENSUS.md:149` | (a) 2d cross | 2024-01-28 (green) ADX | `24.3` | `24.3` | `MATCH` | ADX14 at 2024-01-28 = 24.2585 (`OURS`) |
| 553 | `CENSUS.md:149` | (a) 2d cross | 2024-01-28 (green) slope5 | `-7.2` | `-7.2` | `MATCH` | ADX[i]-ADX[i-5] = -7.2028 (`OURS`) |
| 554 | `CENSUS.md:149` | (a) 2d cross | 2024-01-28 (green) bars to extreme | `23` | `23` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 555 | `CENSUS.md:149` | (a) 2d cross | 2024-01-28 (green) depth | `70.4%` | `70.4%` | `MATCH` | extreme / close - 1 = 70.3751% (`OURS`) |
| 556 | `CENSUS.md:149` | (a) 2d cross | 2024-01-28 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 557 | `CENSUS.md:150` | (a) 2d cross | 2024-04-13 (red) ADX | `35.9` | `35.9` | `MATCH` | ADX14 at 2024-04-13 = 35.9186 (`OURS`) |
| 558 | `CENSUS.md:150` | (a) 2d cross | 2024-04-13 (red) slope5 | `-8.8` | `-8.8` | `MATCH` | ADX[i]-ADX[i-5] = -8.7716 (`OURS`) |
| 559 | `CENSUS.md:150` | (a) 2d cross | 2024-04-13 (red) bars to extreme | `9` | `9` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 560 | `CENSUS.md:150` | (a) 2d cross | 2024-04-13 (red) depth | `-13.9%` | `-13.9%` | `MATCH` | extreme / close - 1 = -13.8726% (`OURS`) |
| 561 | `CENSUS.md:150` | (a) 2d cross | 2024-04-13 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 562 | `CENSUS.md:151` | (a) 2d cross | 2024-05-15 (green) ADX | `20.5` | `20.5` | `MATCH` | ADX14 at 2024-05-15 = 20.5379 (`OURS`) |
| 563 | `CENSUS.md:151` | (a) 2d cross | 2024-05-15 (green) slope5 | `-3.3` | `-3.3` | `MATCH` | ADX[i]-ADX[i-5] = -3.3394 (`OURS`) |
| 564 | `CENSUS.md:151` | (a) 2d cross | 2024-05-15 (green) bars to extreme | `11` | `11` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 565 | `CENSUS.md:151` | (a) 2d cross | 2024-05-15 (green) depth | `10.4%` | `10.4%` | `MATCH` | extreme / close - 1 = 10.3653% (`OURS`) |
| 566 | `CENSUS.md:151` | (a) 2d cross | 2024-05-15 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 567 | `CENSUS.md:152` | (a) 2d cross | 2024-06-14 (red) ADX | `16.4` | `16.4` | `MATCH` | ADX14 at 2024-06-14 = 16.4155 (`OURS`) |
| 568 | `CENSUS.md:152` | (a) 2d cross | 2024-06-14 (red) slope5 | `-2.2` | `-2.2` | `MATCH` | ADX[i]-ADX[i-5] = -2.2030 (`OURS`) |
| 569 | `CENSUS.md:152` | (a) 2d cross | 2024-06-14 (red) bars to extreme | `26` | `26` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 570 | `CENSUS.md:152` | (a) 2d cross | 2024-06-14 (red) depth | `-26.0%` | `-26.0%` | `MATCH` | extreme / close - 1 = -26.0134% (`OURS`) |
| 571 | `CENSUS.md:152` | (a) 2d cross | 2024-06-14 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 572 | `CENSUS.md:153` | (a) 2d cross | 2024-07-20 (green) ADX | `22.7` | `22.7` | `MATCH` | ADX14 at 2024-07-20 = 22.6941 (`OURS`) |
| 573 | `CENSUS.md:153` | (a) 2d cross | 2024-07-20 (green) slope5 | `-4.7` | `-4.7` | `MATCH` | ADX[i]-ADX[i-5] = -4.7212 (`OURS`) |
| 574 | `CENSUS.md:153` | (a) 2d cross | 2024-07-20 (green) bars to extreme | `4` | `4` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 575 | `CENSUS.md:153` | (a) 2d cross | 2024-07-20 (green) depth | `2.8%` | `2.8%` | `MATCH` | extreme / close - 1 = 2.8088% (`OURS`) |
| 576 | `CENSUS.md:153` | (a) 2d cross | 2024-07-20 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 577 | `CENSUS.md:154` | (a) 2d cross | 2024-07-24 (red) ADX | `20.3` | `20.3` | `MATCH` | ADX14 at 2024-07-24 = 20.2510 (`OURS`) |
| 578 | `CENSUS.md:154` | (a) 2d cross | 2024-07-24 (red) slope5 | `-7.2` | `-7.2` | `MATCH` | ADX[i]-ADX[i-5] = -7.2052 (`OURS`) |
| 579 | `CENSUS.md:154` | (a) 2d cross | 2024-07-24 (red) bars to extreme | `6` | `6` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 580 | `CENSUS.md:154` | (a) 2d cross | 2024-07-24 (red) depth | `-25.5%` | `-25.5%` | `MATCH` | extreme / close - 1 = -25.5319% (`OURS`) |
| 581 | `CENSUS.md:154` | (a) 2d cross | 2024-07-24 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 582 | `CENSUS.md:155` | (a) 2d cross | 2024-07-26 (green) ADX | `19.1` | `19.1` | `MATCH` | ADX14 at 2024-07-26 = 19.1043 (`OURS`) |
| 583 | `CENSUS.md:155` | (a) 2d cross | 2024-07-26 (green) slope5 | `-6.8` | `-6.8` | `MATCH` | ADX[i]-ADX[i-5] = -6.8391 (`OURS`) |
| 584 | `CENSUS.md:155` | (a) 2d cross | 2024-07-26 (green) bars to extreme | `1` | `1` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 585 | `CENSUS.md:155` | (a) 2d cross | 2024-07-26 (green) depth | `3.2%` | `3.2%` | `MATCH` | extreme / close - 1 = 3.2159% (`OURS`) |
| 586 | `CENSUS.md:155` | (a) 2d cross | 2024-07-26 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 587 | `CENSUS.md:156` | (a) 2d cross | 2024-07-30 (red) ADX | `17.1` | `17.1` | `MATCH` | ADX14 at 2024-07-30 = 17.1205 (`OURS`) |
| 588 | `CENSUS.md:156` | (a) 2d cross | 2024-07-30 (red) slope5 | `-5.6` | `-5.6` | `MATCH` | ADX[i]-ADX[i-5] = -5.5735 (`OURS`) |
| 589 | `CENSUS.md:156` | (a) 2d cross | 2024-07-30 (red) bars to extreme | `3` | `3` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 590 | `CENSUS.md:156` | (a) 2d cross | 2024-07-30 (red) depth | `-24.2%` | `-24.2%` | `MATCH` | extreme / close - 1 = -24.1815% (`OURS`) |
| 591 | `CENSUS.md:156` | (a) 2d cross | 2024-07-30 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 592 | `CENSUS.md:157` | (a) 2d cross | 2024-09-26 (green) ADX | `20.3` | `20.3` | `MATCH` | ADX14 at 2024-09-26 = 20.3024 (`OURS`) |
| 593 | `CENSUS.md:157` | (a) 2d cross | 2024-09-26 (green) slope5 | `-6.2` | `-6.2` | `MATCH` | ADX[i]-ADX[i-5] = -6.2069 (`OURS`) |
| 594 | `CENSUS.md:157` | (a) 2d cross | 2024-09-26 (green) bars to extreme | `28` | `28` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 595 | `CENSUS.md:157` | (a) 2d cross | 2024-09-26 (green) depth | `51.4%` | `51.4%` | `MATCH` | extreme / close - 1 = 51.4187% (`OURS`) |
| 596 | `CENSUS.md:157` | (a) 2d cross | 2024-09-26 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 597 | `CENSUS.md:158` | (a) 2d cross | 2024-09-30 (red) ADX | `19.3` | `19.3` | `MATCH` | ADX14 at 2024-09-30 = 19.2955 (`OURS`) |
| 598 | `CENSUS.md:158` | (a) 2d cross | 2024-09-30 (red) slope5 | `-4.9` | `-4.9` | `MATCH` | ADX[i]-ADX[i-5] = -4.8545 (`OURS`) |
| 599 | `CENSUS.md:158` | (a) 2d cross | 2024-09-30 (red) bars to extreme | `5` | `5` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 600 | `CENSUS.md:158` | (a) 2d cross | 2024-09-30 (red) depth | `-3.1%` | `-3.1%` | `MATCH` | extreme / close - 1 = -3.0586% (`OURS`) |
| 601 | `CENSUS.md:158` | (a) 2d cross | 2024-09-30 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 602 | `CENSUS.md:159` | (a) 2d cross | 2024-10-14 (green) ADX | `18.1` | `18.1` | `MATCH` | ADX14 at 2024-10-14 = 18.0526 (`OURS`) |
| 603 | `CENSUS.md:159` | (a) 2d cross | 2024-10-14 (green) slope5 | `-1.6` | `-1.6` | `MATCH` | ADX[i]-ADX[i-5] = -1.6150 (`OURS`) |
| 604 | `CENSUS.md:159` | (a) 2d cross | 2024-10-14 (green) bars to extreme | `26` | `26` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 605 | `CENSUS.md:159` | (a) 2d cross | 2024-10-14 (green) depth | `55.2%` | `55.2%` | `MATCH` | extreme / close - 1 = 55.1835% (`OURS`) |
| 606 | `CENSUS.md:159` | (a) 2d cross | 2024-10-14 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 607 | `CENSUS.md:160` | (a) 2d cross | 2024-12-27 (red) ADX | `31.1` | `31.1` | `MATCH` | ADX14 at 2024-12-27 = 31.0543 (`OURS`) |
| 608 | `CENSUS.md:160` | (a) 2d cross | 2024-12-27 (red) slope5 | `-11.3` | `-11.3` | `MATCH` | ADX[i]-ADX[i-5] = -11.3496 (`OURS`) |
| 609 | `CENSUS.md:160` | (a) 2d cross | 2024-12-27 (red) bars to extreme | `30` | `30` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 610 | `CENSUS.md:160` | (a) 2d cross | 2024-12-27 (red) depth | `-13.7%` | `-13.7%` | `MATCH` | extreme / close - 1 = -13.6873% (`OURS`) |
| 611 | `CENSUS.md:160` | (a) 2d cross | 2024-12-27 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 612 | `CENSUS.md:161` | (a) 2d cross | 2025-01-02 (green) ADX | `25.9` | `25.9` | `MATCH` | ADX14 at 2025-01-02 = 25.9361 (`OURS`) |
| 613 | `CENSUS.md:161` | (a) 2d cross | 2025-01-02 (green) slope5 | `-9.6` | `-9.6` | `MATCH` | ADX[i]-ADX[i-5] = -9.6233 (`OURS`) |
| 614 | `CENSUS.md:161` | (a) 2d cross | 2025-01-02 (green) bars to extreme | `9` | `9` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 615 | `CENSUS.md:161` | (a) 2d cross | 2025-01-02 (green) depth | `11.6%` | `11.6%` | `MATCH` | extreme / close - 1 = 11.6261% (`OURS`) |
| 616 | `CENSUS.md:161` | (a) 2d cross | 2025-01-02 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 617 | `CENSUS.md:162` | (a) 2d cross | 2025-01-12 (red) ADX | `20.0` | `20.0` | `MATCH` | ADX14 at 2025-01-12 = 20.0088 (`OURS`) |
| 618 | `CENSUS.md:162` | (a) 2d cross | 2025-01-12 (red) slope5 | `-5.9` | `-5.9` | `MATCH` | ADX[i]-ADX[i-5] = -5.9273 (`OURS`) |
| 619 | `CENSUS.md:162` | (a) 2d cross | 2025-01-12 (red) bars to extreme | `29` | `29` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 620 | `CENSUS.md:162` | (a) 2d cross | 2025-01-12 (red) depth | `-19.0%` | `-19.0%` | `MATCH` | extreme / close - 1 = -18.9664% (`OURS`) |
| 621 | `CENSUS.md:162` | (a) 2d cross | 2025-01-12 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 622 | `CENSUS.md:163` | (a) 2d cross | 2025-01-14 (green) ADX | `19.0` | `19.0` | `MATCH` | ADX14 at 2025-01-14 = 19.0278 (`OURS`) |
| 623 | `CENSUS.md:163` | (a) 2d cross | 2025-01-14 (green) slope5 | `-5.5` | `-5.5` | `MATCH` | ADX[i]-ADX[i-5] = -5.5013 (`OURS`) |
| 624 | `CENSUS.md:163` | (a) 2d cross | 2025-01-14 (green) bars to extreme | `3` | `3` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 625 | `CENSUS.md:163` | (a) 2d cross | 2025-01-14 (green) depth | `9.0%` | `9.0%` | `MATCH` | extreme / close - 1 = 9.0457% (`OURS`) |
| 626 | `CENSUS.md:163` | (a) 2d cross | 2025-01-14 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 627 | `CENSUS.md:164` | (a) 2d cross | 2025-02-01 (red) ADX | `18.0` | `18.0` | `MATCH` | ADX14 at 2025-02-01 = 18.0315 (`OURS`) |
| 628 | `CENSUS.md:164` | (a) 2d cross | 2025-02-01 (red) slope5 | `-2.4` | `-2.4` | `MATCH` | ADX[i]-ADX[i-5] = -2.4254 (`OURS`) |
| 629 | `CENSUS.md:164` | (a) 2d cross | 2025-02-01 (red) bars to extreme | `19` | `19` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 630 | `CENSUS.md:164` | (a) 2d cross | 2025-02-01 (red) depth | `-21.6%` | `-21.6%` | `MATCH` | extreme / close - 1 = -21.5911% (`OURS`) |
| 631 | `CENSUS.md:164` | (a) 2d cross | 2025-02-01 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 632 | `CENSUS.md:165` | (a) 2d cross | 2025-04-22 (green) ADX | `21.5` | `21.5` | `MATCH` | ADX14 at 2025-04-22 = 21.5200 (`OURS`) |
| 633 | `CENSUS.md:165` | (a) 2d cross | 2025-04-22 (green) slope5 | `-3.0` | `-3.0` | `MATCH` | ADX[i]-ADX[i-5] = -3.0047 (`OURS`) |
| 634 | `CENSUS.md:165` | (a) 2d cross | 2025-04-22 (green) bars to extreme | `15` | `15` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 635 | `CENSUS.md:165` | (a) 2d cross | 2025-04-22 (green) depth | `19.5%` | `19.5%` | `MATCH` | extreme / close - 1 = 19.5204% (`OURS`) |
| 636 | `CENSUS.md:165` | (a) 2d cross | 2025-04-22 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 637 | `CENSUS.md:166` | (a) 2d cross | 2025-06-21 (red) ADX | `21.3` | `21.3` | `MATCH` | ADX14 at 2025-06-21 = 21.2724 (`OURS`) |
| 638 | `CENSUS.md:166` | (a) 2d cross | 2025-06-21 (red) slope5 | `-4.6` | `-4.6` | `MATCH` | ADX[i]-ADX[i-5] = -4.6360 (`OURS`) |
| 639 | `CENSUS.md:166` | (a) 2d cross | 2025-06-21 (red) bars to extreme | `1` | `1` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 640 | `CENSUS.md:166` | (a) 2d cross | 2025-06-21 (red) depth | `-1.3%` | `-1.3%` | `MATCH` | extreme / close - 1 = -1.3376% (`OURS`) |
| 641 | `CENSUS.md:166` | (a) 2d cross | 2025-06-21 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 642 | `CENSUS.md:167` | (a) 2d cross | 2025-06-23 (green) ADX | `19.8` | `19.8` | `MATCH` | ADX14 at 2025-06-23 = 19.7889 (`OURS`) |
| 643 | `CENSUS.md:167` | (a) 2d cross | 2025-06-23 (green) slope5 | `-4.9` | `-4.9` | `MATCH` | ADX[i]-ADX[i-5] = -4.8664 (`OURS`) |
| 644 | `CENSUS.md:167` | (a) 2d cross | 2025-06-23 (green) bars to extreme | `26` | `26` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 645 | `CENSUS.md:167` | (a) 2d cross | 2025-06-23 (green) depth | `17.3%` | `17.3%` | `MATCH` | extreme / close - 1 = 17.3364% (`OURS`) |
| 646 | `CENSUS.md:167` | (a) 2d cross | 2025-06-23 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 647 | `CENSUS.md:168` | (a) 2d cross | 2025-08-26 (red) ADX | `17.7` | `17.7` | `MATCH` | ADX14 at 2025-08-26 = 17.6910 (`OURS`) |
| 648 | `CENSUS.md:168` | (a) 2d cross | 2025-08-26 (red) slope5 | `-6.1` | `-6.1` | `MATCH` | ADX[i]-ADX[i-5] = -6.0520 (`OURS`) |
| 649 | `CENSUS.md:168` | (a) 2d cross | 2025-08-26 (red) bars to extreme | `22` | `22` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 650 | `CENSUS.md:168` | (a) 2d cross | 2025-08-26 (red) depth | `-8.3%` | `-8.3%` | `MATCH` | extreme / close - 1 = -8.3245% (`OURS`) |
| 651 | `CENSUS.md:168` | (a) 2d cross | 2025-08-26 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 652 | `CENSUS.md:169` | (a) 2d cross | 2025-09-01 (green) ADX | `15.3` | `15.3` | `MATCH` | ADX14 at 2025-09-01 = 15.2520 (`OURS`) |
| 653 | `CENSUS.md:169` | (a) 2d cross | 2025-09-01 (green) slope5 | `-5.1` | `-5.1` | `MATCH` | ADX[i]-ADX[i-5] = -5.0657 (`OURS`) |
| 654 | `CENSUS.md:169` | (a) 2d cross | 2025-09-01 (green) bars to extreme | `17` | `17` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 655 | `CENSUS.md:169` | (a) 2d cross | 2025-09-01 (green) depth | `13.4%` | `13.4%` | `MATCH` | extreme / close - 1 = 13.4481% (`OURS`) |
| 656 | `CENSUS.md:169` | (a) 2d cross | 2025-09-01 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 657 | `CENSUS.md:170` | (a) 2d cross | 2025-09-23 (red) ADX | `15.6` | `15.6` | `MATCH` | ADX14 at 2025-09-23 = 15.6412 (`OURS`) |
| 658 | `CENSUS.md:170` | (a) 2d cross | 2025-09-23 (red) slope5 | `-0.5` | `-0.5` | `MATCH` | ADX[i]-ADX[i-5] = -0.5073 (`OURS`) |
| 659 | `CENSUS.md:170` | (a) 2d cross | 2025-09-23 (red) bars to extreme | `29` | `29` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 660 | `CENSUS.md:170` | (a) 2d cross | 2025-09-23 (red) depth | `-28.9%` | `-28.9%` | `MATCH` | extreme / close - 1 = -28.8658% (`OURS`) |
| 661 | `CENSUS.md:170` | (a) 2d cross | 2025-09-23 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 662 | `CENSUS.md:171` | (a) 2d cross | 2025-09-29 (green) ADX | `14.3` | `14.3` | `MATCH` | ADX14 at 2025-09-29 = 14.2591 (`OURS`) |
| 663 | `CENSUS.md:171` | (a) 2d cross | 2025-09-29 (green) slope5 | `-3.6` | `-3.6` | `MATCH` | ADX[i]-ADX[i-5] = -3.5507 (`OURS`) |
| 664 | `CENSUS.md:171` | (a) 2d cross | 2025-09-29 (green) bars to extreme | `3` | `3` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 665 | `CENSUS.md:171` | (a) 2d cross | 2025-09-29 (green) depth | `10.7%` | `10.7%` | `MATCH` | extreme / close - 1 = 10.6539% (`OURS`) |
| 666 | `CENSUS.md:171` | (a) 2d cross | 2025-09-29 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 667 | `CENSUS.md:172` | (a) 2d cross | 2025-10-09 (red) ADX | `19.8` | `19.8` | `MATCH` | ADX14 at 2025-10-09 = 19.8128 (`OURS`) |
| 668 | `CENSUS.md:172` | (a) 2d cross | 2025-10-09 (red) slope5 | `5.6` | `5.6` | `MATCH` | ADX[i]-ADX[i-5] = 5.5537 (`OURS`) |
| 669 | `CENSUS.md:172` | (a) 2d cross | 2025-10-09 (red) bars to extreme | `21` | `21` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 670 | `CENSUS.md:172` | (a) 2d cross | 2025-10-09 (red) depth | `-28.5%` | `-28.5%` | `MATCH` | extreme / close - 1 = -28.5299% (`OURS`) |
| 671 | `CENSUS.md:172` | (a) 2d cross | 2025-10-09 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 672 | `CENSUS.md:173` | (a) 2d cross | 2026-01-05 (green) ADX | `29.5` | `29.5` | `MATCH` | ADX14 at 2026-01-05 = 29.5327 (`OURS`) |
| 673 | `CENSUS.md:173` | (a) 2d cross | 2026-01-05 (green) slope5 | `-6.7` | `-6.7` | `MATCH` | ADX[i]-ADX[i-5] = -6.7039 (`OURS`) |
| 674 | `CENSUS.md:173` | (a) 2d cross | 2026-01-05 (green) bars to extreme | `4` | `4` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 675 | `CENSUS.md:173` | (a) 2d cross | 2026-01-05 (green) depth | `4.5%` | `4.5%` | `MATCH` | extreme / close - 1 = 4.4551% (`OURS`) |
| 676 | `CENSUS.md:173` | (a) 2d cross | 2026-01-05 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 677 | `CENSUS.md:174` | (a) 2d cross | 2026-01-07 (red) ADX | `27.7` | `27.7` | `MATCH` | ADX14 at 2026-01-07 = 27.7281 (`OURS`) |
| 678 | `CENSUS.md:174` | (a) 2d cross | 2026-01-07 (red) slope5 | `-7.6` | `-7.6` | `MATCH` | ADX[i]-ADX[i-5] = -7.6115 (`OURS`) |
| 679 | `CENSUS.md:174` | (a) 2d cross | 2026-01-07 (red) bars to extreme | `15` | `15` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 680 | `CENSUS.md:174` | (a) 2d cross | 2026-01-07 (red) depth | `-34.1%` | `-34.1%` | `MATCH` | extreme / close - 1 = -34.1383% (`OURS`) |
| 681 | `CENSUS.md:174` | (a) 2d cross | 2026-01-07 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 682 | `CENSUS.md:175` | (a) 2d cross | 2026-01-13 (green) ADX | `24.1` | `24.1` | `MATCH` | ADX14 at 2026-01-13 = 24.1014 (`OURS`) |
| 683 | `CENSUS.md:175` | (a) 2d cross | 2026-01-13 (green) slope5 | `-7.3` | `-7.3` | `MATCH` | ADX[i]-ADX[i-5] = -7.3345 (`OURS`) |
| 684 | `CENSUS.md:175` | (a) 2d cross | 2026-01-13 (green) bars to extreme | `1` | `1` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 685 | `CENSUS.md:175` | (a) 2d cross | 2026-01-13 (green) depth | `0.2%` | `0.2%` | `MATCH` | extreme / close - 1 = 0.2492% (`OURS`) |
| 686 | `CENSUS.md:175` | (a) 2d cross | 2026-01-13 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 687 | `CENSUS.md:176` | (a) 2d cross | 2026-01-19 (red) ADX | `22.4` | `22.4` | `MATCH` | ADX14 at 2026-01-19 = 22.3882 (`OURS`) |
| 688 | `CENSUS.md:176` | (a) 2d cross | 2026-01-19 (red) slope5 | `-3.7` | `-3.7` | `MATCH` | ADX[i]-ADX[i-5] = -3.6642 (`OURS`) |
| 689 | `CENSUS.md:176` | (a) 2d cross | 2026-01-19 (red) bars to extreme | `9` | `9` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 690 | `CENSUS.md:176` | (a) 2d cross | 2026-01-19 (red) depth | `-32.1%` | `-32.1%` | `MATCH` | extreme / close - 1 = -32.1479% (`OURS`) |
| 691 | `CENSUS.md:176` | (a) 2d cross | 2026-01-19 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 692 | `CENSUS.md:177` | (a) 2d cross | 2026-03-16 (green) ADX | `33.9` | `33.9` | `MATCH` | ADX14 at 2026-03-16 = 33.8987 (`OURS`) |
| 693 | `CENSUS.md:177` | (a) 2d cross | 2026-03-16 (green) slope5 | `-9.1` | `-9.1` | `MATCH` | ADX[i]-ADX[i-5] = -9.1259 (`OURS`) |
| 694 | `CENSUS.md:177` | (a) 2d cross | 2026-03-16 (green) bars to extreme | `25` | `25` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 695 | `CENSUS.md:177` | (a) 2d cross | 2026-03-16 (green) depth | `12.1%` | `12.1%` | `MATCH` | extreme / close - 1 = 12.0968% (`OURS`) |
| 696 | `CENSUS.md:177` | (a) 2d cross | 2026-03-16 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 697 | `CENSUS.md:178` | (a) 2d cross | 2026-03-18 (red) ADX | `32.3` | `32.3` | `MATCH` | ADX14 at 2026-03-18 = 32.2933 (`OURS`) |
| 698 | `CENSUS.md:178` | (a) 2d cross | 2026-03-18 (red) slope5 | `-9.8` | `-9.8` | `MATCH` | ADX[i]-ADX[i-5] = -9.8480 (`OURS`) |
| 699 | `CENSUS.md:178` | (a) 2d cross | 2026-03-18 (red) bars to extreme | `5` | `5` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 700 | `CENSUS.md:178` | (a) 2d cross | 2026-03-18 (red) depth | `-7.0%` | `-7.0%` | `MATCH` | extreme / close - 1 = -7.0499% (`OURS`) |
| 701 | `CENSUS.md:178` | (a) 2d cross | 2026-03-18 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 702 | `CENSUS.md:179` | (a) 2d cross | 2026-04-07 (green) ADX | `23.7` | `23.7` | `MATCH` | ADX14 at 2026-04-07 = 23.6708 (`OURS`) |
| 703 | `CENSUS.md:179` | (a) 2d cross | 2026-04-07 (green) slope5 | `-4.9` | `-4.9` | `MATCH` | ADX[i]-ADX[i-5] = -4.8993 (`OURS`) |
| 704 | `CENSUS.md:179` | (a) 2d cross | 2026-04-07 (green) bars to extreme | `14` | `14` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 705 | `CENSUS.md:179` | (a) 2d cross | 2026-04-07 (green) depth | `16.6%` | `16.6%` | `MATCH` | extreme / close - 1 = 16.5753% (`OURS`) |
| 706 | `CENSUS.md:179` | (a) 2d cross | 2026-04-07 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 707 | `CENSUS.md:180` | (a) 2d cross | 2026-05-23 (red) ADX | `22.3` | `22.3` | `MATCH` | ADX14 at 2026-05-23 = 22.2838 (`OURS`) |
| 708 | `CENSUS.md:180` | (a) 2d cross | 2026-05-23 (red) slope5 | `-6.4` | `-6.4` | `MATCH` | ADX[i]-ADX[i-5] = -6.4205 (`OURS`) |
| 709 | `CENSUS.md:180` | (a) 2d cross | 2026-05-23 (red) bars to extreme | `19` | `19` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 710 | `CENSUS.md:180` | (a) 2d cross | 2026-05-23 (red) depth | `-25.0%` | `-25.0%` | `MATCH` | extreme / close - 1 = -24.9981% (`OURS`) |
| 711 | `CENSUS.md:180` | (a) 2d cross | 2026-05-23 (red) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 712 | `CENSUS.md:181` | (a) 2d cross | 2026-08-17 (green) ADX | `18.6` | `18.6` | `MATCH` | ADX14 at 2026-08-17 = 18.5995 (`OURS`) |
| 713 | `CENSUS.md:181` | (a) 2d cross | 2026-08-17 (green) slope5 | `-4.1` | `-4.1` | `MATCH` | ADX[i]-ADX[i-5] = -4.1130 (`OURS`) |
| 714 | `CENSUS.md:181` | (a) 2d cross | 2026-08-17 (green) bars to extreme | `17` | `17` | `MATCH` | 30-bar forward extreme index offset (`OURS`) |
| 715 | `CENSUS.md:181` | (a) 2d cross | 2026-08-17 (green) depth | `35.0%` | `35.0%` | `MATCH` | extreme / close - 1 = 35.0253% (`OURS`) |
| 716 | `CENSUS.md:181` | (a) 2d cross | 2026-08-17 (green) nfwd | `30` | `30` | `MATCH` | min(30, bars_after) (`OURS`) |
| 717 | `CENSUS.md:182` | (a) 2d cross | 2026-10-28 (red) ADX | `28.3` | `28.3` | `MATCH` | ADX14 at 2026-10-28 = 28.3165 (`OURS`) |
| 718 | `CENSUS.md:182` | (a) 2d cross | 2026-10-28 (red) slope5 | `-8.6` | `-8.6` | `MATCH` | ADX[i]-ADX[i-5] = -8.6329 (`OURS`) |
| 719 | `CENSUS.md:182` | (a) 2d cross | 2026-10-28 (red) nfwd | `4` | `4` | `MATCH` | min(30, bars_after) (`OURS`) |
| 720 | `CENSUS.md:183` | (a) 2d cross | 2026-11-03 (green) ADX | `24.6` | `24.6` | `MATCH` | ADX14 at 2026-11-03 = 24.5762 (`OURS`) |
| 721 | `CENSUS.md:183` | (a) 2d cross | 2026-11-03 (green) slope5 | `-7.5` | `-7.5` | `MATCH` | ADX[i]-ADX[i-5] = -7.4877 (`OURS`) |
| 722 | `CENSUS.md:183` | (a) 2d cross | 2026-11-03 (green) nfwd | `1` | `1` | `MATCH` | min(30, bars_after) (`OURS`) |
| 723 | `CENSUS.md:184` | (a) 2d cross | 2026-11-05 (red) ADX | `23.0` | `23.0` | `MATCH` | ADX14 at 2026-11-05 = 22.9895 (`OURS`) |
| 724 | `CENSUS.md:184` | (a) 2d cross | 2026-11-05 (red) slope5 | `-7.2` | `-7.2` | `MATCH` | ADX[i]-ADX[i-5] = -7.1908 (`OURS`) |
| 725 | `CENSUS.md:184` | (a) 2d cross | 2026-11-05 (red) nfwd | `0` | `0` | `MATCH` | min(30, bars_after) (`OURS`) |
| 726 | `CENSUS.md:186` | (a) footer | Total 2d crosses from 2020-01-01 (n) | `88` | `88` | `MATCH` | 56 DEV + 15 VAL + 17 RECENT = 88 (`OURS`) |
| 727 | `CENSUS.md:192` | (c) summary | DEV 2d crosses | `56` | `56` | `MATCH` | Total 2d crosses in DEV (`OURS`) |
| 728 | `CENSUS.md:192` | (c) summary | DEV with same-dir 1d cross in prev 20d | `52` | `52` | `MATCH` | Count with lead in 0..20 days (`OURS`) |
| 729 | `CENSUS.md:192` | (c) summary | DEV cascade share | `92.9%` | `92.9%` | `MATCH` | 52 / 56 (`OURS`) |
| 730 | `CENSUS.md:192` | (c) summary | DEV median lead (days) | `400.0%` | `4.0 days` | `DIFF` | Median of 52 lead days is 4.0 days; `CENSUS.md:192` formatted days with `:.1%` (`400.0%`, `OURS`) |
| 731 | `CENSUS.md:193` | (c) summary | VALIDATION 2d crosses | `15` | `15` | `MATCH` | Total 2d crosses in VALIDATION (`OURS`) |
| 732 | `CENSUS.md:193` | (c) summary | VALIDATION with same-dir 1d cross in prev 20d | `12` | `12` | `MATCH` | Count with lead in 0..20 days (`OURS`) |
| 733 | `CENSUS.md:193` | (c) summary | VALIDATION cascade share | `80.0%` | `80.0%` | `MATCH` | 12 / 15 (`OURS`) |
| 734 | `CENSUS.md:193` | (c) summary | VALIDATION median lead (days) | `850.0%` | `8.5 days` | `DIFF` | Median of 12 lead days is 8.5 days; `CENSUS.md:193` formatted days with `:.1%` (`850.0%`, `OURS`) |
| 735 | `CENSUS.md:194` | (c) summary | RECENT 2d crosses | `17` | `17` | `MATCH` | Total 2d crosses in RECENT (`OURS`) |
| 736 | `CENSUS.md:194` | (c) summary | RECENT with same-dir 1d cross in prev 20d | `15` | `15` | `MATCH` | Count with lead in 0..20 days (`OURS`) |
| 737 | `CENSUS.md:194` | (c) summary | RECENT cascade share | `88.2%` | `88.2%` | `MATCH` | 15 / 17 (`OURS`) |
| 738 | `CENSUS.md:194` | (c) summary | RECENT median lead (days) | `1300.0%` | `13.0 days` | `DIFF` | Median of 15 lead days is 13.0 days; `CENSUS.md:194` formatted days with `:.1%` (`1300.0%`, `OURS`) |
| 739 | `CENSUS.md:200` | (c) lead days | 2020-01-05 (green) lead days | `15.0` | `15.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 740 | `CENSUS.md:201` | (c) lead days | 2020-02-26 (red) lead days | `10.0` | `10.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 741 | `CENSUS.md:202` | (c) lead days | 2020-03-05 (green) lead days | `17.0` | `17.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 742 | `CENSUS.md:203` | (c) lead days | 2020-03-07 (red) lead days | `20.0` | `20.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 743 | `CENSUS.md:204` | (c) lead days | 2020-04-22 (green) lead days | `17.0` | `17.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 744 | `CENSUS.md:205` | (c) lead days | 2020-05-24 (red) lead days | `1.0` | `1.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 745 | `CENSUS.md:206` | (c) lead days | 2020-05-28 (green) lead days | `2.0` | `2.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 746 | `CENSUS.md:207` | (c) lead days | 2020-06-15 (red) lead days | `2.0` | `2.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 747 | `CENSUS.md:208` | (c) lead days | 2020-06-21 (green) lead days | `0.0` | `0.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 748 | `CENSUS.md:209` | (c) lead days | 2020-06-25 (red) lead days | `12.0` | `12.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 749 | `CENSUS.md:210` | (c) lead days | 2020-07-07 (green) lead days | `16.0` | `16.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 750 | `CENSUS.md:211` | (c) lead days | 2020-07-09 (red) lead days | `16.0` | `16.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 751 | `CENSUS.md:212` | (c) lead days | 2020-07-21 (green) lead days | `1.0` | `1.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 752 | `CENSUS.md:213` | (c) lead days | 2020-09-03 (red) lead days | `10.0` | `10.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 753 | `CENSUS.md:214` | (c) lead days | 2020-09-19 (green) lead days | `4.0` | `4.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 754 | `CENSUS.md:215` | (c) lead days | 2020-09-21 (red) lead days | `20.0` | `20.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 755 | `CENSUS.md:216` | (c) lead days | 2020-10-09 (green) lead days | `2.0` | `2.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 756 | `CENSUS.md:217` | (c) lead days | 2021-04-17 (red) lead days | `0.0` | `0.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 757 | `CENSUS.md:218` | (c) lead days | 2021-07-28 (green) lead days | `5.0` | `5.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 758 | `CENSUS.md:219` | (c) lead days | 2021-09-06 (red) lead days | `0.0` | `0.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 759 | `CENSUS.md:221` | (c) lead days | 2021-09-20 (red) lead days | `14.0` | `14.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 760 | `CENSUS.md:222` | (c) lead days | 2021-09-30 (green) lead days | `0.0` | `0.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 761 | `CENSUS.md:223` | (c) lead days | 2021-11-25 (red) lead days | `10.0` | `10.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 762 | `CENSUS.md:225` | (c) lead days | 2021-12-03 (red) lead days | `18.0` | `18.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 763 | `CENSUS.md:226` | (c) lead days | 2022-02-15 (green) lead days | `11.0` | `11.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 764 | `CENSUS.md:227` | (c) lead days | 2022-02-17 (red) lead days | `1.0` | `1.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 765 | `CENSUS.md:228` | (c) lead days | 2022-03-17 (green) lead days | `17.0` | `17.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 766 | `CENSUS.md:229` | (c) lead days | 2022-04-06 (red) lead days | `1.0` | `1.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 767 | `CENSUS.md:230` | (c) lead days | 2022-08-10 (green) lead days | `15.0` | `15.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 768 | `CENSUS.md:231` | (c) lead days | 2022-08-18 (red) lead days | `0.0` | `0.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 769 | `CENSUS.md:232` | (c) lead days | 2022-09-11 (green) lead days | `3.0` | `3.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 770 | `CENSUS.md:233` | (c) lead days | 2022-09-13 (red) lead days | `1.0` | `1.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 771 | `CENSUS.md:234` | (c) lead days | 2022-10-03 (green) lead days | `1.0` | `1.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 772 | `CENSUS.md:236` | (c) lead days | 2022-10-13 (green) lead days | `11.0` | `11.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 773 | `CENSUS.md:237` | (c) lead days | 2022-11-08 (red) lead days | `1.0` | `1.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 774 | `CENSUS.md:238` | (c) lead days | 2022-12-14 (green) lead days | `2.0` | `2.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 775 | `CENSUS.md:239` | (c) lead days | 2022-12-16 (red) lead days | `1.0` | `1.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 776 | `CENSUS.md:240` | (c) lead days | 2023-01-09 (green) lead days | `4.0` | `4.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 777 | `CENSUS.md:241` | (c) lead days | 2023-03-08 (red) lead days | `6.0` | `6.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 778 | `CENSUS.md:242` | (c) lead days | 2023-03-12 (green) lead days | `8.0` | `8.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 779 | `CENSUS.md:243` | (c) lead days | 2023-05-07 (red) lead days | `17.0` | `17.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 780 | `CENSUS.md:244` | (c) lead days | 2023-05-27 (green) lead days | `0.0` | `0.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 781 | `CENSUS.md:245` | (c) lead days | 2023-05-31 (red) lead days | `1.0` | `1.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 782 | `CENSUS.md:246` | (c) lead days | 2023-06-20 (green) lead days | `1.0` | `1.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 783 | `CENSUS.md:247` | (c) lead days | 2023-08-17 (red) lead days | `17.0` | `17.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 784 | `CENSUS.md:248` | (c) lead days | 2023-08-29 (green) lead days | `1.0` | `1.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 785 | `CENSUS.md:249` | (c) lead days | 2023-08-31 (red) lead days | `16.0` | `16.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 786 | `CENSUS.md:250` | (c) lead days | 2023-09-18 (green) lead days | `1.0` | `1.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 787 | `CENSUS.md:251` | (c) lead days | 2024-01-22 (red) lead days | `20.0` | `20.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 788 | `CENSUS.md:253` | (c) lead days | 2024-04-13 (red) lead days | `13.0` | `13.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 789 | `CENSUS.md:254` | (c) lead days | 2024-05-15 (green) lead days | `1.0` | `1.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 790 | `CENSUS.md:255` | (c) lead days | 2024-06-14 (red) lead days | `4.0` | `4.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 791 | `CENSUS.md:256` | (c) lead days | 2024-07-20 (green) lead days | `6.0` | `6.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 792 | `CENSUS.md:258` | (c) lead days | 2024-07-26 (green) lead days | `12.0` | `12.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 793 | `CENSUS.md:260` | (c) lead days | 2024-09-26 (green) lead days | `10.0` | `10.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 794 | `CENSUS.md:261` | (c) lead days | 2024-09-30 (red) lead days | `0.0` | `0.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 795 | `CENSUS.md:262` | (c) lead days | 2024-10-14 (green) lead days | `8.0` | `8.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 796 | `CENSUS.md:263` | (c) lead days | 2024-12-27 (red) lead days | `8.0` | `8.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 797 | `CENSUS.md:265` | (c) lead days | 2025-01-12 (red) lead days | `5.0` | `5.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 798 | `CENSUS.md:266` | (c) lead days | 2025-01-14 (green) lead days | `9.0` | `9.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 799 | `CENSUS.md:267` | (c) lead days | 2025-02-01 (red) lead days | `7.0` | `7.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 800 | `CENSUS.md:268` | (c) lead days | 2025-04-22 (green) lead days | `11.0` | `11.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 801 | `CENSUS.md:269` | (c) lead days | 2025-06-21 (red) lead days | `18.0` | `18.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 802 | `CENSUS.md:270` | (c) lead days | 2025-06-23 (green) lead days | `15.0` | `15.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 803 | `CENSUS.md:271` | (c) lead days | 2025-08-26 (red) lead days | `8.0` | `8.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 804 | `CENSUS.md:272` | (c) lead days | 2025-09-01 (green) lead days | `11.0` | `11.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 805 | `CENSUS.md:273` | (c) lead days | 2025-09-23 (red) lead days | `2.0` | `2.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 806 | `CENSUS.md:274` | (c) lead days | 2025-09-29 (green) lead days | `1.0` | `1.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 807 | `CENSUS.md:275` | (c) lead days | 2025-10-09 (red) lead days | `18.0` | `18.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 808 | `CENSUS.md:276` | (c) lead days | 2026-01-05 (green) lead days | `8.0` | `8.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 809 | `CENSUS.md:278` | (c) lead days | 2026-01-13 (green) lead days | `16.0` | `16.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 810 | `CENSUS.md:279` | (c) lead days | 2026-01-19 (red) lead days | `0.0` | `0.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 811 | `CENSUS.md:280` | (c) lead days | 2026-03-16 (green) lead days | `13.0` | `13.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 812 | `CENSUS.md:281` | (c) lead days | 2026-03-18 (red) lead days | `13.0` | `13.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 813 | `CENSUS.md:282` | (c) lead days | 2026-04-07 (green) lead days | `16.0` | `16.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 814 | `CENSUS.md:283` | (c) lead days | 2026-05-23 (red) lead days | `6.0` | `6.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 815 | `CENSUS.md:285` | (c) lead days | 2026-10-28 (red) lead days | `16.0` | `16.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 816 | `CENSUS.md:286` | (c) lead days | 2026-11-03 (green) lead days | `16.0` | `16.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 817 | `CENSUS.md:287` | (c) lead days | 2026-11-05 (red) lead days | `17.0` | `17.0` | `MATCH` | close_ed(2d) - close_ed(first 1d in prev 20d) (`OURS`) |
| 818 | `CENSUS.md:289` | (c) 1d->2d follow | Window length in 2d bars / days | `5 / 10` | `5 / 10` | `MATCH` | `SPEC.md:19` 5 2d bars = 10 days (`OURS`) |
| 819 | `CENSUS.md:289` | (c) 1d->2d follow | 1d crosses followed by same-dir 2d cross within 10d | `74` | `74` | `MATCH` | Count of 1d crosses with 2d cross in 0..10d (`OURS`) |
| 820 | `CENSUS.md:289` | (c) 1d->2d follow | Total 1d crosses from 2020-01-01 | `165` | `165` | `MATCH` | 83 red + 82 green = 165 (`OURS`) |
| 821 | `CENSUS.md:289` | (c) 1d->2d follow | Share of 1d crosses followed within 10d | `44.8%` | `44.8%` | `MATCH` | 74 / 165 = 44.848% (`OURS`) |
| 822 | `CENSUS.md:289` | (c) 1d->2d follow | Red 1d crosses followed within 10d | `41` | `41` | `MATCH` | 41 of 83 red 1d crosses (`OURS`) |
| 823 | `CENSUS.md:289` | (c) 1d->2d follow | Total red 1d crosses from 2020-01-01 | `83` | `83` | `MATCH` | Red 1d crosses count (`OURS`) |
| 824 | `CENSUS.md:289` | (c) 1d->2d follow | Green 1d crosses followed within 10d | `33` | `33` | `MATCH` | 33 of 82 green 1d crosses (`OURS`) |
| 825 | `CENSUS.md:289` | (c) 1d->2d follow | Total green 1d crosses from 2020-01-01 | `82` | `82` | `MATCH` | Green 1d crosses count (`OURS`) |
