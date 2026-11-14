# PRE_REG: what do large trades say about price, per phase (large-trade-evidence-1114)

Written and committed with the code BEFORE the first outcome run (2026-11-14). Operator order 2026-11-13 ~21:25Z: "Wrt volume, we need evidence using large trade data we gathered".
Descriptive study plus three pre-registered tests. No orders, no account data, public market data only. Every parameter below is OURS (no source behind it) unless marked SOURCED.

## Context
Regime mix: the PUBLIC sample covers 2022-01-01 .. 2026-11-13 (bear 2022, recovery and halving run 2023-24, 2025 top and rollover, 2026 downtrend). The OUR sample covers 2024-12-02 .. 2026-10-22 only; its phase mix is printed in RESULT.md. The question is asked inside a 7-week downtrend low, so the DOWN phase and the deep-drawdown buckets are the cells that matter; the other phases are controls.

## Data (rows are labelled OUR or PUBLIC everywhere)
- OUR = `F:/MTS/data/orderflow_1m/*.csv.gz` (Binance USD-M BTCUSDT aggTrades rolled to 1m by `orderflow_bars.py`, 2024-12-02 .. 2026-09-28) plus `runtime/orderflow_live/*.csv` (the live writer, 2026-09-29 .. 2026-10-22, with a gap). Large-trade fields: `b99_*` (prints at or above the causal 30-day 99th percentile of print size, about 2.5 BTC) and `b999_*` (99.9th percentile, about 8 BTC, near 0.8 M USD). The live-writer files after 10-22 sit on the laptop, not reachable from this machine (live mirror refused), so OUR data stops 2026-10-22.
- PUBLIC = `data.binance.vision` USD-M BTCUSDT aggTrades zips, kept on D: (2022-01 .. 2024-05 were already ours on D:; 2024-06 .. 2026-10 monthly and 2026-11-01 .. 11-13 daily downloaded for this study, checksums verified), reduced by `reduce_public.py` into 1m bars with, per print (= one aggTrade row, aggressor from `is_buyer_maker`), USD notional >= 250k / 500k / 1M / 5M: buy USD, sell USD, counts. The $1M and $5M columns are the operator's thresholds.
- Prices: the 1m bars' own OHLC (perp). Phase: spot daily BTCUSDT candles (`data_cache/btc_anatomy/BTCUSDT_1d.csv`, 2017-08 .. 2026-11-13).
- Raw trade rows are never committed; only code, this file, RESULT.md and aggregated tables.

## Definitions
- **Large-trade delta** `LD_T(W, t)` = sum over the trailing window W ending at decision time t of (buy USD - sell USD) of prints >= T. T in {1M, 5M} (PUBLIC), {b999, b99} converted to USD at the minute close (OUR). W in {15m, 1h, 4h}.
- **Decision times**: every full UTC hour, at the close of the hour. Signals use bars closed at t only.
- **Standardised delta** `z = LD / std(prior 720 hourly LD values of the same series)` (causal, needs >= 480 prior values).
- **Forward return** `R_H` = close(t+H)/close(t) - 1, H in {1h, 4h, 24h}.
- **Phase of UTC day D** from daily candles through D-1 only: Wilder ADX14/DI (`backtest/layers/adx/adx.py`, FORMULAS.md section 30). UP = ADX >= 20 and DI+ > DI- and SMA20(close) rising; DOWN = ADX >= 20 and DI- > DI+ and SMA20 falling; else RANGE.
- **Drawdown bucket** from the prior close: dd = 1 - close / (all-time daily high to date): B0 < 10 %, B1 10-25 %, B2 25-40 %, B3 >= 40 %.
- **Eras**: A = decisions before 2024-12-02 (before our own recording), B = 2024-12-02 onward.
- **Cluster** for all bootstrap statistics: UTC day for H <= 4h, 3-day block for H = 24h. 20,000 draws, seed 1114, 95 % CI.
- **Holm**: step-down within each test's primary family at alpha = 0.05.

## Test 1: net large-trade delta vs forward return
Cells: T in {1M, 5M} x W in {15m, 1h, 4h} x H in {1h, 4h, 24h} x group in {all, UP, DOWN, RANGE, B0, B1, B2, B3, DOWN&(B2 or B3)}; the last group is the current-like cell (downtrend and 25 %+ below the high) and is exploratory. Per cell: Spearman rank IC of z vs R_H (cluster bootstrap), quintile means of R_H (bp) by z, top-minus-bottom spread (cluster CI).
**Primary family (6 cells)**: T = 1M, group in {UP, DOWN, RANGE}, and (W=1h, H=4h) and (W=4h, H=24h). A primary cell PASSES only if: Holm-adjusted p < 0.05 AND the IC has the same sign in era A and era B AND at least 60 clusters in each era. Everything else is exploratory; the report states how many exploratory cells show a 95 % CI away from zero against the 5 % expected by chance.

## Test 2: absorption at 24-hour extremes
Hourly bars. A **low event** = the hour's low is below the lowest low of the previous 24 hourly bars. **Absorption at a low** = low event AND hour return < 0 AND z(1h, T=1M) >= +1 (large buyers net absorbed while price fell). Contrast group = all other low events. Outcome from the hour close: first touch within 24 h of close +1 ATR vs close -1 ATR (hourly ATR14, plain SMA of true range, FORMULAS.md section 12; both in one 15m bar or neither = "none"), plus R_4h and R_24h. Mirror: **absorption at a high** = new 24h high AND hour return > 0 AND z <= -1; outcome mirrored (-1 ATR first = reversal).
**Primary family (6 cells)**: {low, high} x {UP, DOWN, RANGE}, statistic = P(reversal-side first-touch) for absorption minus the same for the contrast group, cluster CI/p. PASS rule as Test 1 (Holm over the 6, same sign in eras A and B, >= 60 clusters each era). Secondary: -1 ATR-first (continuation) and the three drawdown buckets, labelled exploratory.

## Test 3: delta-divergence trade trigger (fee-net)
Windows of 12 hourly bars: A = latest 12 hours, B = the 12 before. **Bull divergence at hour k**: min low of A < min low of B, the low of A made in its latest 3 hours, AND LD_1M over A > LD_1M over B. **Bear** mirrors (max high, LD lower). Entry at the open of the 15m bar after the hourly close; long on bull, short on bear. Stop = max(0.6 x ATR14(1h), 0.5 %) from entry, checked on 15m high/low, filled at the stop, no slippage; exit at the stop or at 24 h (96 x 15m buckets) at the close. Round-trip fee 12 bp deducted. One position per side at a time. **Placebo**: 5,000 draws of the same number of entries from random hourly bars of the same phase and side, same stop and exit rules; p = share of draws whose mean net return is at least the trigger's. Reported per trade set: n, win %, mean net bp, mean R (net return / stop %), cluster CI of the mean (UTC day).
**Primary family (6 cells)**: {long, short} x {UP, DOWN, RANGE} on T = 1M. A cell PASSES if mean net > 0 AND placebo p < 0.05 Holm-adjusted over the 6 AND the mean net is > 0 in both eras AND n >= 60 per phase overall. Also reported, exploratory: T = 5M, all phases pooled, drawdown buckets.

## OUR-data replication
Test 1 primary cells and Test 3 long/short (all phases and per phase) are rerun on OUR rows (b999 as T and b99 as the lower tier) over 2024-12-02 .. 2026-10-22 and labelled "OUR". OUR b999 is a quantity-based causal threshold (about 0.8 M USD), PUBLIC 1M is a fixed USD threshold, so they are close but not identical; the hourly correlation of the two net-delta series on the overlap is reported as a data check.

## Verdict rule
- "EVIDENCE": at least one primary cell of a test passes its full rule in PUBLIC data and the same-direction sign holds in the OUR replication.
- "NO EVIDENCE": no primary cell passes.
- Anything else is "DESCRIPTIVE ONLY" and the table says what leans and how underpowered it is.
The current-low section (7-week downtrend, 2026-11-13) is descriptive: today's large-trade delta against its own history for the same phase/drawdown bucket; no advice, no forecast.

## Honest limits stated in advance
- 4.8 years, BTC only; the DOWN phase with deep drawdown has few independent episodes (a handful of selloffs), so day-clusters overstate independence across consecutive days.
- aggTrade rows are exchange-aggregated (same aggressor, price, millisecond); one large order can be several rows, a row can be several orders.
- One venue (Binance USD-M). Bybit trades (the Live Aid collector) are only 24 h deep and not used.
