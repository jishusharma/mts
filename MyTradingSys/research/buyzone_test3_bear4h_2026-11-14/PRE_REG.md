# PRE_REG: Test 3, bear-phase 4H bearish-divergence short, replication on 22 coins with funding (frozen before any outcome is computed)

Source brief: `buy_zone_1114/NEXT5_TESTS.md` Test 3 and its Shared rules. Task from login C ask q-d8cd77. Nothing here is an edge until a fee-net out-of-sample result passes. Only data availability (symbol listing, funding endpoint reachability) was looked at when this file was written; no signal, entry, exit or return has been computed. The BTC "+1.03 R, n=28" number is from `BUY_ZONE_MAP.md` and is NOT reproduced or tuned against here. Every parameter is OURS unless marked SOURCED.

## Context
Regime: the ex-ante post-peak-bear flag BEAR below (daily, previous day only) is the regime gate. Shorts are claimed only when it is true.
Phase: reported with the Test 1 daily phase labels (UP, BASE, RANGE, DOWN, POSTPEAK_BEAR; definitions in `buyzone_test1_ladder_2026-11-14/PRE_REG.md`, re-implemented here) plus the claim flag BEAR. Signals with BEAR false are the control, split by the Test 1 label (expected no edge).
Session: not applicable, 24/7 4H bars (UTC).
Entry: short at the next 4H open after the confirming close (SOURCED, NEXT5 Test 3).
Regime mix: reported in REPORT.md as the share of coin-days with BEAR true per split, and the share of each Test 1 phase per split, pooled over the universe. Regime mix in BEAR: reported; UP: reported; BASE: reported; RANGE: reported; DOWN: reported; POSTPEAK_BEAR: reported. A split whose claim events are more than 85% from one calendar year is flagged ONE-YEAR and cannot carry a PASS alone.

## Data (OURS)
| Item | Choice |
|---|---|
| Price | Binance spot klines, public `data-api.binance.vision`, no key: 1d (existing host cache) and 4h (fetched now). Binance futures not used (unreachable from the study machine, per brief caveat) |
| Funding | Bybit linear perpetual funding history (public `api.bybit.com/v5/market/funding/history`), SYMBOLUSDT, used as the funding proxy for the Binance spot price path. Source is Bybit, not Binance, and is stated in the report |
| Cache | host cache outside the repo (`F:/MTS/data_cache` absent): `$MTS_DATA_CACHE` or `C:/Users/e-ngineers/MTS_data_cache/{binance_spot_1d,binance_spot_4h,bybit_funding}`. Never committed; repo is public |
| Universe | 22 coins fixed now (same as Test 1): BTC, ETH, BNB, XRP, ADA, DOGE, SOL, LTC, LINK, TRX, DOT, AVAX, ATOM, ETC, XLM, BCH, NEO, UNI, NEAR, FIL, ALGO, VET (all `*USDT`). No coin added or dropped after outcomes. The brief says 20 coins; the Test 1 universe is BTC, ETH plus those 20 (DECISION, OURS: same universe as Test 1) |
| Bars | UTC; the last (possibly partial) bar of each series is dropped. 4H warm-up: first 100 4H bars of each coin give no event and no placebo draw. Daily phase needs 350+ daily bars (no phase = no event) |
| Funding coverage | A trade whose entry precedes the first Bybit funding record of that coin, or a coin with no Bybit history, gets funding 0 on the with-funding row and is counted and listed ("no funding coverage"). The no-funding row is unaffected. No trade is dropped for it |

## Phase flag BEAR (OURS, from closed daily bars through the day BEFORE the entry day)
SMA50w = 350-day SMA of closes. BEAR on day t is true iff both hold at bar t:
1. Close[t] < SMA50w[t];
2. NOT base reclaim, where base reclaim = (a) the Test 1 BASE condition (not UP, DD >= 0.40 and higher-low: `min Low[t-59..t] >= min Low[t-179..t-60]`, DD = 1 - Close / max High over 365 bars) OR (b) the UP condition (Close > SMA200 and SMA200[t] > SMA200[t-30]).
For a 4H entry bar e with open time on UTC day D the flag is read at daily bar D-1 (previous day only, stale up to 24 h, conservative).

## Signal (OURS, pivot-based, closed bars only)
Swing high on the 4H series: bar i with `High[i] > High[i-3..i-1]` and `High[i] > High[i+1..i+3]` (k = 3). KNOWN only at the close of bar i+3; that is the confirming close.
Bearish divergence: consecutive swing highs p < j (j known at its confirming close c = j+3) with `6 <= j-p <= 60` bars, `High[j] > High[p]` (higher price high), `RSI14[j] < RSI14[p]` (lower RSI at the second high; Wilder 14 on closes; RSI only, WaveTrend NOT used, DECISION OURS), AND outside the upper Bollinger band: `High[j] > SMA20(Close)[j] + 2 x stdev20(Close)[j]` (population stdev, closed bars through j). Signal bar = c = j+3, one signal per pivot j. Entry bar e = c+1 at Open[e].
Stop (SOURCED, Shared rule): `stop0 = High[j] + max(0.6 x ATR14[c], 0.005 x High[j])` (ATR14 Wilder on 4H, closed bars at c). Risk fraction r = (stop0 - entry) / entry. An event with entry >= stop0 is dropped and counted.
Exit (SOURCED, Test 3): first of (a) trailing stop 2 x ATR, (b) 7 days = 42 4H bars. Short trailing level at bar t (t > e) = `min(stop0, min Low[e..t-1] + 2 x ATR14[t-1])`; if `High[t] >= level`, exit at `max(Open[t], level)`. On the entry bar only stop0 is checked: if `High[e] >= stop0` exit at `max(Open[e], stop0)`. (b) exit at Close[e+41]. If neither occurs before the data end the event is dropped.
Lockout (SOURCED, 10 days): a signal is dropped if its entry bar is within 60 4H bars of the previous KEPT entry bar of the same coin, or on or before the previous kept trade's exit bar.

## Returns and funding
gross = (entry - exit) / entry (short). Fee 12 bp round trip (main row) and 6 bp (sensitivity), subtracted in return units. Funding: Bybit settlements are assigned to the 4H bar that contains their timestamp. A short held from entry bar e to exit bar x receives the sum of settlement rates in bars e+1..x (a settlement at the entry bar's own open is not counted; one in the exit bar is counted). A positive rate is income to the short, a negative rate is a cost. Funding return = that sum (notional approximated as entry notional, OURS). R = (gross - fee + funding) / r on the with-funding row; R = (gross - fee) / r on the no-funding row. Four reported mean-R columns: {12 bp, 6 bp} x {with funding, without funding}.

## Splits
DEV: entry date <= 2023-12-31. VAL: entry date >= 2024-01-01 (last closed bar). RECENT: entry date >= 2025-07-01, a subset of VAL, reported separately, never used to pick anything.

## Placebo (>= 1000 draws)
For every group x split cell, 2000 draws (seed 1114): each event is replaced by a short entry at the open of a uniformly random eligible 4H bar of the SAME coin, SAME split, with the daily BEAR flag (or Test 1 phase for control groups, read at D-1) equal to the event's, past warm-up, with the exit inside the data. Same stop distance r, same exit rule (2 x ATR trail from entry, max 42 bars), same fee, and (with-funding row) that draw's own funding over its own hold. Per draw the mean R is computed; the placebo band is the 2.5th to 97.5th percentile of the 2000 draw means; the percentile of the actual mean within the draws is reported. "Beats the placebo band" = actual mean R above the 97.5th percentile. Computed separately for the with- and without-funding row. No lockout on placebo draws (stated).

## Bootstrap
Block bootstrap of pooled per-trade R: blocks are 7-calendar-day windows of ENTRY date (block = hold length, SOURCED Shared rule), all coins in a window form one block; 10000 resamples of blocks with replacement, seed 1114, percentile 95% CI of mean R.

## Verdict (SOURCED, Shared rules; PRIMARY = pooled, BEAR true, 22 coins, VAL, 12 bp)
- UNDERPOWERED (do not claim) if VAL pooled n < 30.
- PASS only if, on BOTH the without-funding and the with-funding 12 bp rows (DECISION OURS, conservative: the brief asks for both rows and does not say which one carries): VAL mean R > 0 AND bootstrap CI low > 0 AND actual mean R > placebo 97.5th percentile AND DEV mean R > 0 (sign agrees).
- Otherwise KILL, stated with the VAL mean R, CI, placebo percentile and n (both rows).
- Descriptive only, cannot change the verdict: 6 bp rows, RECENT, per coin (n < 30 marked underpowered), BTC-only row (replication check of the prior +1.03 R, n=28), result with the top-contributing coin removed, the BEAR-false control by Test 1 phase.
- One primary test, no parameter chosen after outcomes; nothing re-run with changed rules. If the run shows a bug, the fix is stated in the report with both numbers.

## Output
`REPORT.md` and `summary.json` in this folder: table per coin and pooled with n, win %, mean R (four columns), CI, placebo percentile, DEV/VAL/RECENT columns. Data files never committed.
