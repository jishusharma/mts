# OPTIONS BACKTEST - API (written by the builder; BT_SPEC.md is the source of truth, this file only fixes what the spec left open)

Import style: flat modules, `sys.path.insert(0, <options/backtest>)`, then `import bs`, `from panel import Panel`, ...
Units: timestamps are int ms UTC; prices BTC unless named `_usd`; `iv` / `iv_pct` is percent (e.g. 45.0); `T` in years (365 d).
`is_call` is bool. Instrument names look like `BTC-9OCT26-86000-P`. Dates are `'YYYY-MM-DD'` strings.

## bs.py
- `MS_PER_YEAR = 365*86400*1000`
- `norm_cdf(x)`
- `years_to_expiry(ts_ms, expiry_ms) -> float`  (>= 0)
- `price_usd(F, K, T, iv_pct, is_call) -> float`   (aliases: `bs_price_usd`, `black76_price_usd`)
- `price_btc(F, K, T, iv_pct, is_call) -> float`   = price_usd / F (aliases: `bs_price_btc`, `black76_price_btc`)
- `delta(F, K, T, iv_pct, is_call) -> float`       call N(d1), put N(d1)-1 (aliases: `bs_delta`, `black76_delta`)
- `payoff_btc(is_call, K, S) -> float`             max(0,S-K)/S or max(0,K-S)/S
- degenerate inputs (T<=0 or iv<=0): price = intrinsic, delta = 1/0 (0.5 at F==K) for call, call-1 for put.

## instruments.py
- `parse_instrument(name) -> Instrument | None` ; `Instrument(name, underlying, expiry_ms, expiry_date, strike, is_call, expiry_weekday)` (namedtuple; weekday 0=Mon..6=Sun, UTC). Expiry = 08:00 UTC of the coded date.
- `ymd_to_ms(date_str) -> int` (00:00 UTC) ; `ms_to_ymd(ms) -> str` ; `weekday_of_ms(ms) -> int`
- `load_delivery_prices(path) -> {date_str: float}` (missing file -> {})
- `payoff_btc` re-exported from bs.

## fees.py
- `trade_fee_btc(price_btc, ts_ms=None) -> float`   min(0.0003, 0.125*price) ; cap 0.0004 if ts_ms < 2020-08-24 UTC
- `delivery_fee_btc(payoff_btc, expiry_ms=None, *, weekday=None) -> float`   0 unless payoff>0 and expiry weekday == Friday(4); then min(0.00015, 0.125*payoff)
- `perp_fee_usd(notional_usd) -> float`  0.0005*|notional| ; `perp_fee_btc(notional_usd, price_usd) -> float`
- constants: `TRADE_FEE_CAP_BTC, TRADE_FEE_PREMIUM_FRAC, OLD_TRADE_FEE_CAP_BTC, OLD_FEE_CUTOFF_MS, DELIVERY_FEE_CAP_BTC, PERP_TAKER_RATE`

## panel.py
- `Panel(trades_dir, hist_dir=None, cache_days=16, cache_dir=None)`  hist_dir defaults to parent of trades_dir (delivery_prices.csv, dvol_1d.csv, perp_1h.csv, funding.csv are read lazily from it; a missing CSV gives empty data, never an error at construction). `cache_dir` (optional) enables an on-disk parsed-day cache (npz, keyed by source file size+mtime and the directory path).
- Filter at parse: trades with truthy `block_trade_id` / `combo_id` / `liquidation` are dropped; also dropped: non-positive/NaN price, amount or index_price, unknown direction, unparseable instrument name, timestamp outside the shard's UTC day. Missing/None iv is kept with iv=NaN (selection skips those).
- `last_obs(instrument, ts_ms, lookback_ms) -> {'price','iv','index','ts'} | None`  latest kept trade with `ts_ms - lookback_ms < ts <= ts_ms` (lower bound EXCLUSIVE, same as live_instruments). Exactly these four keys.
- `live_instruments(ts_ms, lookback_ms) -> set[str]`  names with a kept trade in `(ts_ms-lookback_ms, ts_ms]`.
- `first_fill(instrument, side, ts_ms, window_ms, size=1.0, slip_pct=0.0) -> {'price','ts','index'} | None`  side = OUR side; needs taker prints of the same word ('sell' prints to sell) with `ts_ms <= ts <= ts_ms+window_ms` (both ends inclusive); cumulative same-direction amount from ts_ms up to and including the fill print must reach size (1e-9 tolerance); price = completing print's price, adverse-adjusted by slip_pct (sell: *(1-slip), buy: *(1+slip)). Exactly these three keys.
- extras: `chain_obs(ts_ms, expiry_ms, lookback_ms) -> {name: obs}` (memoised, treat as read-only) ; `live_expiries(ts_ms, lookback_ms) -> sorted list[int]` ; `index_at(ts_ms, lookback_ms) -> float|None` (latest index of any kept trade) ; `obs_range(instrument, t0_ms, t1_ms) -> dict of numpy arrays ts/price/iv/index/amount/dir` (inclusive; dir +1 buy/-1 sell) ; `available_dates() -> list[str]` ; `date_range() -> (first, last)|(None,None)` ; `has_day(date)` ; `coverage(start, end) -> {calendar_days, days_with_shard, missing}` ; properties `delivery_prices` (dict date->float), `dvol_daily` ({'ts','close'}), `perp_1h` ({'ts','close'}, ts = bar open), `funding` ({'ts','interest_1h'}) ; `settlement_price(date) -> float|None`.

## selection.py
- `pick_by_delta(panel, ts, expiry_ms, is_call, target_abs_delta, lookback_ms=6h, max_dev=0.10) -> name | None`  delta from the instrument's own last_obs (obs iv, obs index, T = (expiry-ts)/year). Candidates need iv>0. Nearest |delta| to target; ties -> lower strike, then name. None if the best deviation > max_dev.
- `pick_by_strike_pct(panel, ts, expiry_ms, pct, is_call=False, lookback_ms=6h, max_dev=0.05) -> name | None`  reference = `panel.index_at(ts, lookback_ms)`; picks min |K/ref - pct|; None if > max_dev.
- `pick_expiry(ts, min_dte_days, instruments=None, tol_days=3.0, panel=None, lookback_ms=3 days) -> expiry_ms | None`  candidates: expiries of `instruments` (names / Instrument / int expiry_ms) or, if None, `panel.live_expiries(ts, lookback_ms)`. Picks smallest DTE >= min_dte_days (DTE=(expiry-ts)/86400000); None if none or DTE > min_dte_days + tol_days (tol_days=None disables the upper limit).
- `pick_straddle(panel, ts, expiry_ms, lookback_ms=6h) -> (call_name, put_name) | None`  same strike with both legs live, nearest to the latest chain index.
- `pick_by_premium(panel, ts, expiry_ms, is_call, target_premium_btc, min_strike=None, lookback_ms=6h) -> name | None`  nearest last-obs premium (collar call).

## strategies.py   (every strategy returns `(trades, skipped)`)
Trade dict: `strategy, decision_ts, entry_ts (latest leg fill), exit_ts (=expiry), legs[], pnl_btc, spot_entry (index of latest fill), spot_exit (settlement), fees_btc`. Leg dict: `name, side ('sell'|'buy' = OUR side), entry_px, fee_entry, payoff_btc, fee_delivery` (+ extras `fill_ts, strike, is_call, entry_iv, entry_index`). pnl per leg = sign*(entry_px - payoff_btc) - fee_entry - fee_delivery, sign=+1 sell / -1 buy.
Skipped dict: `ts` (decision), `date`, `reason`, `strategy`, `detail`. reason in `no_instrument | no_fill` (spec) plus `filter` (DVOL filter), `no_settlement` (no delivery price for the expiry date), `no_hedge_data` (R3, no perp bars). A package (strangle/straddle/collar) is all-or-nothing: any leg without a fill skips the whole decision (`no_fill`).
- `weekend_strangle(panel, dow_entry=4, hour=16, expiry='next_sunday_0800', delta=0.15, *, start=None, end=None, fill_window_ms=2h, size=1.0, slip_pct=0.0, max_dev=0.10, lookback_ms=6h)`  expiry spec `next_<mon..sun>_0800` = first such weekday 08:00 UTC strictly after the entry time.
- `covered_call(panel, delta=0.20, tenor_days=7, *, dvol_filter=False, tol_days=None, start=None, end=None, ...)` ; `cash_secured_put(...)` same args
- `delta_hedged_short_straddle(panel, tenor_days=7, hedge_rule='hourly', *, ...)` hedge_rule 'hourly' | 'band<x>' (e.g. 'band0.02')
- `protective_put_overlay(panel, strike_pct=0.90, tenor_days=30, *, collar=False, ...)` ; `collar(panel, strike_pct=0.90, tenor_days=30, ...)` = overlay with collar=True ; `overlay_equity_series(panel, trades, start=None, end=None)`
- `long_straddle(panel, tenor_days=7, *, ...)`  (S7)
- helpers: `next_expiry_ms(ts_ms, spec)`, `dvol_filter_ok(panel, ts_ms, n=90)`, `default_tol_days(tenor)`.

## stats.py
- `summarize(trades, skipped=None, *, block_len=5, n_boot=2000, seed=12345) -> dict` keys `n, n_skipped, n_skipped_by_reason, win_rate, mean_pnl_btc, median_pnl_btc, worst_pnl_btc, best_pnl_btc, total_pnl_btc, t_stat, boot_ci_lo, boot_ci_hi` (+ short aliases `mean, median, worst, best, total`).
- `equity_btc(trades) -> dict` (see docstring) ; `max_drawdown_pct(equity) -> float` (positive %)
- `period_of(ts_ms)`, `split_by_period(trades, key='entry_ts')`, `split_by_year(trades, key='entry_ts')` ; `PERIODS`
- `pbo_cscv(matrix, n_slices=8) -> float`
- `es_mean_worst(returns, frac=0.05)`, `overlay_metrics(...)`

## run_grid.py
`python run_grid.py --strategy R1|R2|R3|R4|R7|S7|all --start YYYY-MM-DD --end YYYY-MM-DD --out DIR [--grid small|full] [--write-trades]`
(details and deviations: see the "Ambiguities / deviations" section appended below once the build is finished.)
