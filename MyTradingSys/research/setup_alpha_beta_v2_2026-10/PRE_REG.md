# PRE-REGISTRATION: Setup Alpha / Setup Beta v2 (B163 re-run, frozen before any outcome)

Card ask-p0-65-setup-alpha-beta-backtest, 2026-10-30. One-run study: design, definitions and gates below are frozen before the first run and not changed after the first outcome. Label NO-SOURCE (chatbot handoff, no trader transcript). Every parameter is OURS.

Why v2: v1 (../setup_alpha_beta_2026-10-10/) had no DEV/VAL split, counted Beta per bar (n = 708,240) not per sweep event, and `mark_levels` in beta_sweep.py used `bars[i+1]` (next bar) to define swing points, a look-ahead. v1 numbers are void; v1 files stay as history.

## 1. Data and windows
- BTCUSDT 1m klines, Binance USDT-M. Dedupe by open_time (tom_raw 2025-09 has overlapping monthly + daily files; no 2025-09 file is read here anyway). Daily (UTC) and 15m bars are built from 1m, closed buckets only; a 15m bucket with fewer than 15 1m bars is dropped. Not raw_1d (T01-F2: a different snapshot).
- Sources: 2020-01..2021-12 `Dumps/backtest/raw_1m_2019/klines` (indicator warm-up only), 2022-01.. `F:/MTS/data/tom_raw/klines`. Funding: `Dumps/backtest/raw/fundingRate`.
- DEV 2022-01-01..2024-06-30, VALIDATION 2024-07-01..2025-06-30 (sim_desk/ROADMAP.md 2.1). HOLDOUT 2025-07-01+ is sealed: the loader refuses any month >= 2025-07 and cuts every row at 2025-07-01. backtest/splits.py is not on origin/fast-track yet, so the dates are hard-coded with a comment.
- Fees: backtest/fees.py BINANCE_TAKER 0.0005 per side on every leg (entry, target, stop, timeout, SMA exit). No slippage modelled (stated limit). Funding: every settled rate between entry and exit; a long pays a positive rate, a short receives it.

## 2. Alpha (daily SMA200 long-flat), the one rule, no tuning
- At each daily close t: long if close_t > SMA200(close)_t, else flat. The position is held over day t+1 (close_t to close_t+1). No look-ahead: the signal uses bars <= t only.
- Indicator history before 2022-01-01 is used for warm-up only (pre-DEV, legal). A position held at a split end is closed at the split's last close (fee charged) so no later data is needed.
- Baseline: buy-and-hold of the same window (one entry fee, one exit fee at the window end, funding paid).
- Per trade: net return after 2 x fee and funding; R = net return / (2 x ATR14_entry-day / entry close) (the handoff's 2 x ATR stop distance as the risk unit). Reported: n entries, win rate, mean R, CAGR, Sharpe (daily, sqrt 365), max drawdown, time in market, for Alpha and buy-and-hold per split.
- Verdict rule (frozen): Alpha PASS iff in BOTH DEV and VAL its net Sharpe is above buy-and-hold's AND its max drawdown is below buy-and-hold's. Else FAIL. n entries is expected under 30 per split, so PASS is descriptive only: INCONCLUSIVE as an edge claim, never a live layer.

## 3. Beta (15m sweep + taker-buy CVD absorption), one entry per sweep event
- Level: previous UTC day high (PDH) and low (PDL) only (equal highs/lows and swing levels dropped: v1's swing code was the look-ahead; DECISION OURS).
- Event, evaluated on a CLOSED 15m bar i: short if high_i > PDH and close_i < PDH and close_i-1 <= PDH; long mirrored on PDL. At most one event per (day, level): the first bar that qualifies.
- CVD proxy: delta_bar = 2 x taker_buy_volume - volume; CVD = cumulative sum. Absorption (the `cvd` arms): price makes a new 8-bar extreme (short: high_i > max high of bars i-8..i-1) while CVD at close_i is not above max CVD close of bars i-8..i-1 (long mirrored). Plain arms: no CVD test.
- Session filter arms: event bar opens 07:00-20:59 UTC. Arms: S1 session+CVD (PRIMARY), S0 session plain, A1 all hours+CVD, A0 all hours plain.
- Entry: market at the OPEN of bar i+1 (taker). Stop: wick extreme of bar i plus 0.1 beyond. Event skipped if the entry is at or past the stop. Target 1.5 R. Time stop 90 min (6 bars) from the entry bar open, exit at the close of its last 1m bar. Management walks 1m bars; stop wins if stop and target sit in the same 1m bar. No partial exit. Events whose 90 min window is not fully inside loaded data are dropped and counted.
- R_net = (side x (exit - entry)/entry - 2 x fee - side x funding_sum) / (|entry - stop|/entry). Reported per arm and split: n events, n trades, win rate (R_net > 0), mean R_net, SE, t, median round-trip fee in R.
- Verdict rule (frozen) on the PRIMARY arm S1 only: PASS iff DEV n >= 100, DEV mean R_net > 0 with t >= 2, AND VAL n >= 30 with VAL mean R_net > 0. DEV n < 100 or VAL n < 30 (and no sign flip) = INCONCLUSIVE. Otherwise FAIL. The S0 vs S1 gap (does CVD add anything over a plain sweep) is reported, not a verdict. 3 further arms are read as sensitivity; m = 4 arms for any Holm talk, and no arm other than S1 can PASS.
- FAIL means stop: the PDH/PDL one-entry-per-sweep + kline-CVD proxy + 1.5R/90min bracket under taker fees on BTCUSDT 2022-2025; it says nothing about true aggTrades CVD, 5m structure-shift entries, other levels, or maker entries.

## 4. Power and kill (items 0a, 0e, 0f of the template)
- 0a: the stop is the sweep wick, often well under 0.40 %, so taker fees can exceed 0.25 R; reported (median fee in R), not skipped.
- 0e: power is stated from the DEV n of the result; below n 100 the answer is INCONCLUSIVE in advance.
- 0f: one run, no redesign. FAIL ends the NO-SOURCE Alpha/Beta setups; only a trader source can reopen them.

## Verdict arms
| arm | split | rule |
|---|---|---|
| Alpha vs buy-and-hold | DEV and VAL | Sharpe and max drawdown better in both |
| Beta S1 | DEV and VAL | see section 3 |
