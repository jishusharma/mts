# PRE_REG: 1d ADX(14) through 25 (Rule A) and Raschke Holy Grail (Rule B), 5 symbols, fee-net (frozen before any outcome is computed)

Card adx-1d-through25-1113. Origin: `adx_di_2026-11/HOW_TO_USE_ADX_1113.md` section 7 (BTC 1d through-25 long n=34, thin, one asset, no fees, no split). Code and report in this folder. Nothing below is tuned; no outcome of any rule has been computed when this file is committed (only first-kline dates were fetched, to pick symbols).

## Context
Regime: none as an entry gate, because the ADX level IS the trend-regime gate under test. The window's bull/bear mix is reported (close above/below own 200-day SMA, share of bars per split, pooled over symbols), see Regime mix below.
Phase: none, because no cycle-phase gate is part of either rule (Rule A/B are pure ADX/DI/average rules).
Session: not applicable, daily bars (UTC day).
Entry: Rule A next daily open after the signal close; Rule B stop-buy at the pullback bar's high/low (rules below).
Regime mix: reported in REPORT.md as bull/bear share of bars per split (200d SMA definition above), BTC pre-2020-03-25 bars excluded from nothing (they are in DEV warm-up/DEV); a split whose mix is >85% one regime is flagged "ONE-REGIME" and cannot carry a PASS alone.

## Data (OURS)
| Item | Choice |
|---|---|
| Symbols | BTC, ETH, SOL (named by the card) plus the two of {BNB, XRP, ADA, DOGE, LINK, LTC, AVAX} with the earliest first Bybit daily kline, chosen from first-kline dates only before any outcome: LINKUSDT and LTCUSDT (both 2020-10-21) |
| Source | Bybit v5 linear daily klines (`fetch_klines.py`, Binance does not answer here). Files under `MyTradingSys/market_data/klines/` (git-ignored). Fetch command: `python fetch_klines.py BTCUSDT ETHUSDT SOLUSDT LINKUSDT LTCUSDT` |
| BTC back-fill | `btc_cycles_2026-11/btc_daily.csv` (Binance) for days before 2020-03-25, with open := prior close (the csv has no open); flagged OURS. All other symbols Bybit only |
| Bars | UTC days. The partial current day (2026-11-13) is dropped; last closed bar is 2026-11-12 |
| Warm-up | the first 100 bars of each symbol never produce an event |
| Indicators | ADX/+DI/-DI period 14, Wilder RMA smoothing, definitions of FORMULAS.md section 30.1 re-implemented in the run script (NOT imported from `adx.py`); EMA/SMA per section 4 |

## Splits (SOURCED, `adx_di_2026-11/CENSUS.md`; split by the date of the SIGNAL bar for Rule A and of the ENTRY bar for Rule B)
DEV 2020-01-01..2024-06-30; VALIDATION 2024-07-01..2025-06-30; RECENT 2025-07-01..last closed bar (CENSUS ended 2026-11-07; extended to the data end, OURS). Events whose exit bar is not in the data yet are dropped.

## Rule A (OURS; threshold 25 and period 14 are the Wilder rule-of-thumb levels)
- Signal at the close of day i: `ADX[i-1] <= 25 < ADX[i]`. Long if `+DI[i] > -DI[i]`, short if `-DI[i] > +DI[i]`; equal = no signal.
- Entry at the open of day i+1. Exit at the close of day i+h, h in {3, 6, 12} only (so the hold is h days). Gross = side * (C[i+h]/O[i+1] - 1); net = gross - 0.0010 (10 bps round trip).
- PRIMARY test = h = 6 (middle, fixed now), both sides pooled. h = 3 and h = 12 are robustness: a PASS also needs mean excess > 0 (point estimate) at both.

## Rule B (SOURCED Raschke Holy Grail, `adx_di_2026-11/MASTERS_1113.md` section 4: ADX(14) above 30 and rising, pullback to the 20-period average, buy above the high of the bar that touches it, mirror for shorts; sources give no exit and conflict on SMA vs EMA). Exact mechanical version; every item not in the SOURCED sentence is OURS:
| Step | Rule | Label |
|---|---|---|
| Filter on touch bar t | `ADX[t] > 30` and `ADX[t] > ADX[t-1]` (rising = one bar) | SOURCED level 30; "rising" = 1 bar OURS |
| Direction | long if `+DI[t] > -DI[t]` else short (the source uses ADX only, direction undefined) | OURS |
| Average | EMA(20) of close (sources conflict SMA/EMA) | OURS |
| Touch bar t (long) | `Low[t] <= EMA20[t]` and `Close[t-1] > EMA20[t-1]` (first touch from above). Short: `High[t] >= EMA20[t]` and `Close[t-1] < EMA20[t-1]` | OURS |
| Trigger | the first day k in t+1..t+3 with `High[k] > High[t]` (long) / `Low[k] < Low[t]` (short); later = setup expires | break = SOURCED; 3-day window OURS |
| Fill | long at `max(Open[k], High[t])`; short at `min(Open[k], Low[t])` (stop-buy gap fill at the open) | OURS |
| Stop | `Low[t]` (long) / `High[t]` (short), checked from the entry bar onwards, filled at the stop (or the open if it gapped through); if stop and target are both inside one bar, the stop is taken | OURS (source stop unknown) |
| Target | prior swing extreme = highest High (long) / lowest Low (short) of the 20 bars before t (t excluded). If that level is not beyond the fill, there is no target (time exit only) and the trade is flagged | SOURCED idea "prior swing", 20 bars OURS |
| Time exit | close of day k+12 | OURS (12 days from the card) |
| Positions | one at a time per symbol; setups arising while a trade is open are skipped | OURS |
| Fee | 0.0010 round trip | OURS |

## Baselines (OURS)
- Rule A: for the same symbol, split, side and h, the mean over EVERY day j in that split (after warm-up, exit in data) of `side * (C[j+h]/O[j+1] - 1) - 0.0010`. Shorts use the negative of the long gross, same fee.
- Rule B: each trade has a realised hold of d = exit day - entry day (>= 0). Its baseline is the mean over every day j of that symbol and split of `side * (C[j+d]/C[j] - 1) - 0.0010`. Excess per trade = trade net - its baseline.

## Statistics and verdict
- Event excess = event net - cell baseline. Windows overlap and symbols are correlated, so NO independence is assumed: CI = cluster bootstrap over calendar months (all events of every symbol and side in a month are one block), 10,000 resamples, seed 1113, percentile 95% CI of the pooled mean excess. Overlapping events are NOT removed (block bootstrap, not non-overlapping events).
- Per rule, the verdict is read on the VALIDATION pooled row (all five symbols, both sides, the primary hold for A; the single exit for B):
  - UNDERPOWERED if VALIDATION n < 30.
  - PASS if n >= 30, 95% CI lower bound of mean fee-net excess > 0, the h = 3 and h = 12 point excess > 0 (Rule A only), the split is not ONE-REGIME, AND RECENT does not contradict (contradict = RECENT pooled mean excess < 0 with n >= 10, or CI upper bound < 0 with any n >= 5).
  - FAIL otherwise.
- DEV and RECENT rows, per symbol x split x side cells and win rate are descriptive; per-symbol/per-side cells with n < 30 are marked UNDERPOWERED and never carry a verdict.
- Reproduction check (not a verdict): the same through-25 long definition on the BTC csv alone at close-to-close must give n within 34 +- 4 for the whole history, else the run is flagged as not matching the source study.
- A "current state" line per symbol (last closed bar) is reported; no forecast, no sizing.
