# RSI layer, timeframe layer, layer backtesting - design (Opus supervisor, 2026-09-28)

Source directive: PROJECT_VISION.md "USER DIRECTIVE (verbatim, 2026-09-28)". This file records the
decisions; the operator's words live only there.

## D1. Timeframe layer (shared; serves every layer, core included)

- Decision: yes, one separate layer. `MyTradingSys/backtest/layers/timeframe/` (backtest side first;
  the live side reuses the same module later). It is a bar provider only. It never computes signals.
- Input: 1m OHLCV bars (the base). Output: bars for any timeframe in the registry, closed bars only.
- Registry (config, not code): 1m 2m 3m 5m 10m 15m 30m 1h 2h 4h 6h 8h 12h 1d 2d 3d 5d 1w 1M.
  Adding a timeframe is a one-line config change.
- Anchoring (UTC): minute/hour frames align to the Unix epoch (a 3m bar opens at minutes divisible by 3
  since 1970-01-01 00:00). 1d opens 00:00 UTC. 2d/3d/5d: epoch-day index mod N (configurable anchor
  date so it can be matched to TradingView/Binance later). 1w opens Monday 00:00 UTC. 1M = calendar month.
- Partial bars: a bar is emitted only when its window has closed. Missing 1m bars inside a window are
  reported (gap count on the bar), never silently filled.
- Event: `bar_closed(tf, bar)`. Downstream layers subscribe per timeframe. This is what makes
  "an alert per timeframe whenever it changes" possible.
- Correctness gate (T0): resampled 1d from 1m must equal Binance's native 1d archive bars exactly
  (open, high, low, close, volume) over the overlap. Same for 1h vs native 1h if fetched.
- Core (Tom) is NOT changed by this. Core may adopt the provider later as a separate decision.

## D2. RSI layer, layered inside

All under `MyTradingSys/backtest/layers/rsi/`. Every number comes from a params file (D4).

| Sub-layer | Purpose | Defaults |
|---|---|---|
| `rsi_core` | Wilder RSI on close. The ONLY RSI any other MTS consumer uses. | length 14; standard readings 70 / 50 / 30 |
| `rsi_ma` | Smoothing line on the RSI, as shipped with the standard indicator. Types SMA, EMA, RMA(SMMA), WMA. | SMA 14 |
| `rsi_events` | Generic level and line interactions with a tolerance band: support, rejection, cross. Works on any level (70/50/30, 40/60) or on the rsi_ma line. | tolerance from params |
| `malkan_40_60` | MalkanView system: regime (bull holds above ~40 and reaches 60+, bear stays below ~60 and reaches 40-) and trade setups for any timeframe. | 40 / 60 live ONLY here |

- Isolation rule (operator): the 40/60 numbers are private to `malkan_40_60`. No other module imports
  them. A unit test asserts that `rsi_core` and `rsi_ma` default params contain no 40 or 60 level.
- `rsi_ma` support: RSI pulls back to its MA line (within tolerance) and closes back on the trend side
  -> `ma_support` / `ma_rejection`. Separate feature, switchable, per timeframe.
- Event schema (all sub-layers): `{layer, sub, tf, t_close, event, level_name, level_value,
  tolerance_used, penetration, rsi, rsi_ma, params_id}`. An alert is a change in the event stream for
  one timeframe.
- Existing `bt/bt_rsi.py.new`: reuse its `rsi_wilder` in `rsi_core` (after tests); its `rsi_regime`
  becomes the starting point for `malkan_40_60`. It is not promoted into `bt/`.

## D3. Tolerance ("slippage") study - how far from 40/60 still counts

- Parameters swept: tolerance 0 to 5 RSI points in 0.5 steps, above and below the level separately
  (a support at 60 may hold at 58; a rejection at 40 may turn at 41-42).
- Measured per timeframe x level x event type: event count, forward return after N bars
  (N = 1, 3, 5, 10, 20), hit rate vs a no-event baseline, max adverse move.
- Chosen tolerance: best out-of-sample on walk-forward splits, then the existing PBO check
  (`bt/ref_pbo`). A tolerance that only wins in-sample is rejected.
- Edge cases, each with a hand-computed test: exact touch; touch within band and close back (support);
  close through the band (failure, not support); RSI jumps across the band inside one bar; double and
  triple touches; several bars inside the band; RSI flat on the level; warm-up bars (no RSI yet);
  first bar after a data gap; close-based vs intrabar (high/low) RSI (report both, decide on data).

## D4. Fine-tuning built in (testnet phase)

- Every threshold lives in `layers/<layer>/params/<name>.json` with `params_id`, `source`
  (operator | MalkanView | CryptoCred | backtest run id), `date` and `note`. Code has no magic numbers.
- A tuning change = a new params file, never an edit of an old one. Every backtest run and every
  testnet event records the params_id it used, so any two settings can be compared.
- Operator and trusted-professional inputs go in as params files with `source` naming who, and are
  backtested before going live on testnet.

## D5. Where backtests run

- Data is on the desktop (JIS-NB): 1d BTCUSDT 2020-01..2025-08 in `Dumps/backtest/raw_1d/klines`,
  1m from 2025-09 onward in `Dumps/backtest/raw/klines`. The NUC holds no data and no repo (T049 rule).
- Now: Qwen (NUC) writes all backtest code from specs; Sonnet writes the tests from the test plans;
  the desktop runs backtests as background jobs under `Dumps/backtest/runs/<run_id>/` with a manifest
  (git hash, params_id, data file hashes, command, start/end, row counts) and a progress log.
- Next (T049 extension, "RUN" job type): the NUC runs parameter sweeps from committed code plus a
  packed data slice, returns results + manifest; the desktop re-runs 1 in 5 and the result hashes must
  match. Precondition: Python on the NUC (operator check). Built only if desktop sweeps exceed ~30 min.

## D6. Data needed

- DONE 2026-09-28 (operator approved): 1m BTCUSDT 2022-01..2025-08 in `Dumps/backtest/raw_1m_2022/klines`
  (44 monthly files, 210 MB; row counts exact, e.g. 2024-02 = 41,760 = 29 x 1440). With
  `Dumps/backtest/raw/klines` (2025-09 onward) that is continuous 1m from 2022-01 to now.

## D7. Build order (NUC task ids)

| id | module | tests from |
|---|---|---|
| 070 | timeframe/tf_resample.py + registry config | TF test plan (Sonnet) |
| 071 | rsi/rsi_core.py + rsi/rsi_ma.py | RSI test plan |
| 072 | rsi/rsi_events.py (tolerance band, all edge cases in D3) | RSI test plan |
| 073 | rsi/malkan_40_60.py (regime + setups) | RSI test plan + Malkan extracts |
| 074 | layers/runner.py: events -> forward-return stats per tf x params, run manifest | runner test plan |
| 075 | cryptocred adapter: cc_setups trades -> bt_engine | CC TEST_PLAN + runner plan |

Probability layer: `prob_table.py.new` (Qwen 033) is reviewed and backtested by the same runner.
