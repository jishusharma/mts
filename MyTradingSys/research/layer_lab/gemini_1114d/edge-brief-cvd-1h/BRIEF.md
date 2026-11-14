NO DATA

# Edge-Hunt Brief: CVD Layer on 1h Cache (`edge-brief-cvd-1h-gemini4-1114`)

## 1. Data-Coverage Audit (`MyTradingSys/data/klines/`)

- `MyTradingSys/data/klines/BTCUSDT_1h.json`: **100 rows**, **7 fields** per row (`open_time`, `close_time`, `open`, `high`, `low`, `close`, `volume`), UTC `2026-09-20T09:00:00+00:00` to `2026-09-24T12:59:59.999000+00:00` (~4.2 days), **0 taker-buy fields** (`taker_buy_volume` / `tbv` absent).
- `MyTradingSys/data/klines/BTCUSDT_15m.json`: **102 rows**, **7 fields** per row (`open_time`, `close_time`, `open`, `high`, `low`, `close`, `volume`), UTC `2026-09-23T11:15:00+00:00` to `2026-09-24T12:44:59.999000+00:00` (~1.06 days), **0 taker-buy fields**.
- `MyTradingSys/data/klines/BTCUSDT_5m.json`: **106 rows**, **7 fields** per row (`open_time`, `close_time`, `open`, `high`, `low`, `close`, `volume`), UTC `2026-09-24T03:55:00+00:00` to `2026-09-24T12:44:59.999000+00:00` (~8.8 hours), **0 taker-buy fields**.

### Why Verdict Is `NO DATA`
1. **Missing `taker_buy_volume` (`tbv`):** Canonical CVD is `delta = 2 * taker_buy_volume - volume` (`MyTradingSys/research/indicator_rulebooks/CVD.md:9`, `MyTradingSys/backtest/bt/bt_data.py:184`, `MyTradingSys/backtest/layers/FORMULAS.md:368`). None of the three cached kline files in `MyTradingSys/data/klines/` contain `taker_buy_volume` or any aggressive-volume field.
2. **OHLCV proxy rejected:** Estimating intrabar delta from price action is explicitly `NOT VERIFIED-TV` (`MyTradingSys/research/indicator_rulebooks/CVD.md:11`) and rated `anecdote (vendor approximation, unverified accuracy against tick-level data)` (`MyTradingSys/research/indicator_rulebooks/CVD.md:31`).
3. **Sample size too small:** 100 rows on 1h (~4.2 days), 102 rows on 15m (~1.06 days), and 106 rows on 5m (~8.8 hours) cannot support a DEV/VAL split or any pre-registered `n` floor (`n >= 50`–`100`).

---

## 2. SOURCED Rule Quotes & Fee-Net Definitions

- **Core CVD role** (`MyTradingSys/research/indicator_rulebooks/CVD.md:72`): "Read effort (CVD) against result (price) only at existing structural levels; never trade CVD divergence or delta crosses as an entry by itself."
- **Open test — structural-level sweep + CVD** (`MyTradingSys/research/indicator_rulebooks/CVD.md:78`): "Price sweeps level, CVD fails to confirm with lower low / higher high; 15m/1h horizon, fee-net 10 bps"
- **Fabio absorption** (`MyTradingSys/research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md:26`): "we have a lower low on the cumulative volume delta here while the market is still on the same level as before. This is what it's called it's called absorption."
- **Fabio green sell-delta candle** (`MyTradingSys/research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md:28`): "now they have a cvd cell candle but the candle is printing green so they are absorbing with passive liquidity all this attempt to go short"
- **Fabio CVD veto** (`MyTradingSys/research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md:32`): "the CVD as you can see is flipping lower. So, even if the main direction of the day is higher, they are getting aggressive on the downside."
- **Divergence formula** (`MyTradingSys/backtest/layers/FORMULAS.md:372-373`): "bearish if `c[i] > max(c[i-n..i-1])` and `cvd[i] < max(cvd[i-n..i-1])`; bullish if `c[i] < min(c[i-n..i-1])` and `cvd[i] > min(cvd[i-n..i-1])` (strict)."
- **Fee-net cost model** (`MyTradingSys/backtest/layers/FORMULAS.md:352-358`): Binance USDT-M perp taker fee `0.0010` (10 bps RT; `BINANCE_TAKER = 0.0005` per side per `MyTradingSys/backtest/layers/FORMULAS.md:410`) + `slip_rt = 0.0002` (2 bps RT) + funding `side_sign * sum(rate over records in (t_in, t_out])`, i.e. `net = gross - fee_rt - slip_rt - side_sign * sum(rate over records in (t_in, t_out])`.
- **Forward return / no-lookahead fill contract** (`MyTradingSys/backtest/layers/FORMULAS.md:135-136`, `MyTradingSys/backtest/layers/FORMULAS.md:652`): Signal is evaluated strictly at bar `i` close; taker entry executes at `open[i+1]`; forward return at horizon `h` uses `closes[i+1+h]` (never `i` intrabar); ATR uses plain SMA (`MyTradingSys/backtest/layers/FORMULAS.md:331`).

---

## 3. Pre-Registered Cells (Blocked on `tbv` Data; Ready Once Full 1h Binance Klines with `tbv` Are Cached)

| Cell ID | Rule (SOURCED quote / formula) | TF | Entry / Stop / Target (OURS unless noted) | Fee-Net Horizon | `n` Floor (OURS) | Kill Criterion (OURS) | Cache Status |
|---|---|---|---|---|---|---|---|
| `CVD-1H-ABS-LONG` | Structural support sweep + CVD lower low (`MyTradingSys/research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md:26`, `MyTradingSys/research/indicator_rulebooks/CVD.md:78`): `low[i] <= PDL`, `close[i] >= PDL`, `cvd[i] < min(cvd[i-20..i-1])`, `close[i] >= min(close[i-20..i-1])` (OURS lookback `n=20` from `MyTradingSys/backtest/layers/FORMULAS.md:376`) | `1h` (OURS) | Entry: taker long at `open[i+1]` (no lookahead); Stop: `min(low[i], PDL) - 0.5 * ATR_14[i]` (SMA ATR, SOURCED `MyTradingSys/backtest/layers/FORMULAS.md:331`); Target: `1.5R` or timeout `h=12` | `h=12` bars (12h, OURS); net of `10 bps` RT taker + `2 bps` RT slip + funding (SOURCED `MyTradingSys/backtest/layers/FORMULAS.md:352-358`) | DEV `n >= 100`; VAL `n >= 50` | DEV fee-net mean R `<= 0` OR VAL fee-net Sharpe `< 0.3` OR VAL `n < 50` | **NO DATA** (`tbv` absent in `BTCUSDT_1h.json`, 100 rows) |
| `CVD-1H-ABS-SHORT` | Structural resistance sweep + bearish CVD divergence (`MyTradingSys/backtest/layers/FORMULAS.md:372-373`, `MyTradingSys/research/indicator_rulebooks/CVD.md:78`): `high[i] >= PDH`, `close[i] <= PDH`, `c[i] > max(c[i-20..i-1])` & `cvd[i] < max(cvd[i-20..i-1])` | `1h` (OURS) | Entry: taker short at `open[i+1]`; Stop: `max(high[i], PDH) + 0.5 * ATR_14[i]`; Target: `1.5R` or timeout `h=12` | `h=12` bars (12h, OURS); net of `10 bps` RT taker + `2 bps` RT slip + funding (SOURCED `MyTradingSys/backtest/layers/FORMULAS.md:352-358`) | DEV `n >= 100`; VAL `n >= 50` | DEV fee-net mean R `<= 0` OR VAL fee-net Sharpe `< 0.3` OR VAL `n < 50` | **NO DATA** (`tbv` absent in `BTCUSDT_1h.json`, 100 rows) |
| `CVD-1H-GREEN-ABS` | Candle-level sell-delta absorption at swing low (`MyTradingSys/research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md:28`, `MyTradingSys/research/indicator_rulebooks/CVD.md:81`): `delta[i] < 0` & `close[i] > open[i]` & `low[i] <= min(low[i-20..i-1])` inside completed `4h` uptrend gate `close_4h > SMA_20_4h` (OURS) | `1h` (OURS) | Entry: taker long at `open[i+1]`; Stop: `low[i] - 0.5 * ATR_14[i]`; Target: `1.5R` or timeout `h=8` | `h=8` bars (8h, OURS); net of `10 bps` RT taker + `2 bps` RT slip + funding (SOURCED `MyTradingSys/backtest/layers/FORMULAS.md:352-358`) | DEV `n >= 100`; VAL `n >= 50` | DEV fee-net mean R `<= 0` OR VAL fee-net Sharpe `< 0.3` OR VAL `n < 50` | **NO DATA** (`tbv` absent in `BTCUSDT_1h.json`, 100 rows) |
| `CVD-1H-VETO-LONG` | CVD flip-lower veto on pullback longs (`MyTradingSys/research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md:32`, `MyTradingSys/research/indicator_rulebooks/CVD.md:71`): baseline `close[i]` pullback to `SMA_20[i]` in uptrend; veto if `cvd[i] < cvd[i-1]` & `delta[i] < 0`; score `PASS - BLOCKED` | `1h` (OURS) | Entry: taker long at `open[i+1]`; Stop: `low[i] - 1.0 * ATR_14[i]`; Target: `1.5R` or timeout `h=12` | `h=12` bars (12h, OURS); net of `10 bps` RT taker + `2 bps` RT slip + funding (SOURCED `MyTradingSys/backtest/layers/FORMULAS.md:352-358`) | DEV `n >= 100` (`>= 40` vetoed); VAL `n >= 50` | `PASS - BLOCKED` fee-net mean R `<= 0` OR Welch `t < 1.5` | **NO DATA** (`tbv` absent in `BTCUSDT_1h.json`, 100 rows) |

### Parameter Provenance & DEV/VAL Split
- **SOURCED parameters:** CVD formula `delta = 2 * taker_buy_volume - volume` (`MyTradingSys/research/indicator_rulebooks/CVD.md:9`), divergence strict inequality (`MyTradingSys/backtest/layers/FORMULAS.md:372-373`), SMA ATR (`MyTradingSys/backtest/layers/FORMULAS.md:331`), taker fee `0.0010` RT + `0.0002` slip RT + funding (`MyTradingSys/backtest/layers/FORMULAS.md:352-358`).
- **OURS parameters:** Timeframe (`1h`), lookback `n = 20` (reused from `MyTradingSys/backtest/layers/FORMULAS.md:376` grid default), `0.5 * ATR_14` / `1.0 * ATR_14` stop buffers, `1.5R` target, `h = 8` / `12` bar timeouts, `n` floors (`100` DEV / `50` VAL), and kill thresholds.
- **DEV / VAL split (OURS):** Once full Binance USDT-M `1h` klines with `taker_buy_volume` are available, freeze `DEV` = earliest 70% chronological (or pre-`2025-07-01`) and `VAL` = remaining 30% up to `2026-09-01`, keeping post-`2026-09-01` `RECENT` / `HOLDOUT` sealed.
