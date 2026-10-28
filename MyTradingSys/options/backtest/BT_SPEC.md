# OPTIONS BACKTEST SPEC v1 (2026-10-09). Source of truth for builder AND test writer. Python 3.14, stdlib + numpy only (no pandas/scipy).
Independent module: imports nothing from execution/, layers/, live files. Files LF. Package dir: MyTradingSys/options/backtest/ (flat modules, import by name with sys.path insert of own dir).

## Data (read-only; produced by collector, see ../collector/README.md)
- ../data/hist/trades/YYYY-MM-DD.jsonl.gz  option trades: timestamp(ms), instrument_name, direction ('buy'|'sell' = TAKER side), price (BTC), amount (contracts = BTC), iv (%), index_price (USD), mark_price (BTC); optional block_trade_id, combo_id, liquidation.
- ../data/hist/delivery_prices.csv (ts_ms,date,delivery_price) | dvol_1d.csv/dvol_1h.csv (ts_ms,open,high,low,close) | perp_1h.csv (ts_ms,open,high,low,close,...) | funding.csv (ts_ms,interest_8h,interest_1h,...).
- Ignore *.tmp shards. Missing days are allowed (report coverage), never interpolated.

## Conventions
- Options are INVERSE: price quoted in BTC; 1 contract = 1 BTC notional. USD value of option = price_btc * index. Expiry = 08:00 UTC of the date in the name (e.g. BTC-9OCT26-86000-P; day may be 1 or 2 digits; month 3 letters). Settlement S = delivery_prices.csv value for that date.
- Payoff per contract in BTC at settlement: call max(0,S-K)/S ; put max(0,K-S)/S.
- Black-76 with r=0 and F=index (no futures data; documented approximation). price_usd = F*N(d1)-K*N(d2) (call), K*N(-d2)-F*N(-d1) (put); d1=(ln(F/K)+0.5 s^2 T)/(s sqrt T), s = iv/100, T in years (365d). price_btc = price_usd/F. delta (USD-space, call) = N(d1); put = N(d1)-1. Use |delta| for strike targeting.
- Fees per contract, per leg: trade fee = min(0.0003, 0.125*price_btc) BTC [0.0004 if ts < 2020-08-24 UTC]. Delivery fee: only when the option finishes ITM AND the expiry weekday is Friday (treated as the non-daily weekly/monthly/quarterly): min(0.00015, 0.125*payoff_btc). Expiries on Mon-Thu, Sat, Sun are treated as daily => no delivery fee. Perp (hedge) taker fee 0.05% of notional per fill; maker not assumed.
- Trades flagged block_trade_id / combo_id / liquidation are EXCLUDED from the panel (off-market risk).

## panel.py
class Panel(trades_dir): lazy per-day load with small LRU cache of days; per-instrument time-sorted arrays.
- last_obs(instrument, ts_ms, lookback_ms) -> dict(price, iv, index, ts) or None : latest filtered trade with ts<=ts_ms within lookback.
- live_instruments(ts_ms, lookback_ms) -> set of names that traded in (ts_ms-lookback_ms, ts_ms].
- first_fill(instrument, side, ts_ms, window_ms, size) -> dict(price, ts, index) or None. side 'sell' means WE sell => requires a taker 'sell' print (hit bid) at ts>=ts_ms within window; side 'buy' needs a taker 'buy' print. Liquidity rule: cumulative same-direction amount in the window from ts_ms up to and including the fill trade must reach `size` (default 1.0) else no fill (fill price = price of the print that completes the size; report it, no averaging). This builds the real spread/slippage in; no assumed haircut. A swept optional extra slippage parameter `slip_pct` (fraction of price, adverse) defaults 0.
- No lookahead: instrument SELECTION may use only obs with ts<=decision time; fills use only ts>=decision time.

## selection
pick_by_delta(panel, ts, expiry_ms, is_call, target_abs_delta, lookback_ms=6h) -> instrument or None: among live instruments with that expiry and type, compute |delta| from last_obs (iv, index, strike, T to expiry) at ts; choose nearest to target; reject if |delta-target| > max_dev (default 0.10). pick_by_strike_pct for puts at K ~ pct*index.
pick_expiry(ts, min_dte_days, ...) : nearest listed expiry (from instruments seen) with DTE >= tenor, tolerance in days given; deterministic.

## strategies.py (each returns list of trade dicts: entry_ts, exit_ts(=expiry), legs[{name,side,entry_px,fee_entry,payoff_btc,fee_delivery}], pnl_btc (per 1 BTC notional, sum of premium received/paid, payoffs, fees), spot_entry, spot_exit; plus list of skipped decisions with reason: no_instrument|no_fill)
 R1 weekend_strangle(panel, dow_entry=4 (Fri), hour=16, expiry='next_sunday_0800', delta in grid, ...): sell put+call at target |delta|, hold to expiry. Also variants dow_entry in {3,4,6}, hour in {8,12,16}.
 R2 covered_call(delta, tenor_days): at each expiry-roll time sell 1 call, hold to expiry, immediately roll next decision time = expiry (08:00 UTC)+1h fills. Optional filter: DVOL daily close (known at decision, previous day) > mean of previous 90 daily closes.
 R4 cash_secured_put(delta, tenor_days): same as R2 with puts.
 R3 delta_hedged_short_straddle(tenor_days, hedge_rule in {'hourly','band0.02'}): sell ATM-ish straddle (call+put nearest |delta| 0.5/ nearest strike to index), hedge with BTC-PERPETUAL hourly: delta tracked from last-observed iv of each leg (carry forward, fallback entry iv) on perp_1h closes; hedge PnL in USD converted to BTC at index; perp fee 0.05% per hedge fill; funding paid/received hourly from funding.csv interest_1h on position notional. Reports gamma/theta proxy NOT required; report total pnl_btc split: options, hedge, funding, fees.
 R7 protective_put_overlay(strike_pct in {0.95,0.90,0.85}, tenor in {30,90}) and collar (sell call whose premium ~ matches put premium, nearest strike): account = 1 BTC + options; reports USD equity vs HODL; carry cost %/yr, max drawdown, ES5 (mean of worst 5% daily USD returns) comparison.
 S7 control long_straddle(tenor in {7,30}).
 All stochastic-free; deterministic given data. Grids: report EVERY cell (no cherry-picking).

## stats.py
- summarize(trades): n, n_skipped_by_reason, win_rate, mean/median/worst/best pnl_btc, total pnl_btc, t-stat of mean, stationary-bootstrap 95% CI of mean (block len 5, 2000 resamples, seeded).
- equity_btc(trades): sequential cumulative BTC (1 BTC start); max_drawdown_pct; Sharpe on weekly aggregated pnl; vs HODL: for USD view, equity_usd_t=(1+cum pnl_btc)*spot_t at trade exits vs spot_t.
- split by period: IS = start..2024-08-31, OOS1 = 2024-09-01..2025-04-30 (post-source), OOS2 = 2025-05-01..end; and by calendar year.
- pbo_cscv(matrix[config x period], n_slices=8) -> probability of backtest overfitting (Bailey et al. CSCV). 

## run_grid.py CLI
python run_grid.py --strategy R1|R2|R3|R4|R7|S7|all --start 2021-01-01 --end 2026-10-08 --out ../research/results/ . Writes one CSV per strategy (all grid cells x periods) + a coverage report (days with shard vs calendar days, fill rate). Prints only counts parsed from the written files.
