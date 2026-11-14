# PRE_REG: Test 1, causal confirmation ladder, long side (frozen before any outcome is computed)

Source brief: `buy_zone_1114/NEXT5_TESTS.md` Test 1 and its Shared rules. Task from login C ask q-d8cd77. Nothing here is an edge until a fee-net out-of-sample result passes. Only data availability (first-kline dates, bar counts) was looked at when this file was written; no entry, exit or return of any rule has been computed. Every parameter is OURS unless marked SOURCED.

## Context
Regime: none as a separate gate; the phase below (daily, previous day only) is the regime gate.
Phase: UP, BASE, RANGE, DOWN, POSTPEAK_BEAR (definitions below), computed from closed daily bars through the day BEFORE the entry day. Long trades are claimed only in UP and BASE; the other three phases are reported as the control (expected no edge).
Session: not applicable, daily bars (UTC day).
Entry: next daily open after the confirming close (SOURCED, NEXT5_TESTS Test 1).
Regime mix: reported in REPORT.md per phase (share of coin-days per phase per split, pooled over the universe) and per phase the event count per split; a split whose pooled long-phase events are more than 85% from one calendar year is flagged ONE-YEAR and cannot carry a PASS alone. Regime mix in UP: reported; BASE: reported; RANGE: reported; DOWN: reported; POSTPEAK_BEAR: reported.

## Data (OURS)
| Item | Choice |
|---|---|
| Source | Binance spot daily klines (public `data-api.binance.vision`, no key). Binance futures not used. Bybit funding is NOT needed: spot long, no funding cost line (the brief says "where needed"; not needed) |
| Cache | host cache dir outside the repo (`F:/MTS/data_cache` does not exist on this host; used `$MTS_DATA_CACHE`, default `C:/Users/e-ngineers/MTS_data_cache/binance_spot_1d`). Never committed; repo is public |
| Universe | BTCUSDT, ETHUSDT plus 20 liquid coins fixed now: BNB, XRP, ADA, DOGE, SOL, LTC, LINK, TRX, DOT, AVAX, ATOM, ETC, XLM, BCH, NEO, UNI, NEAR, FIL, ALGO, VET (all `*USDT`). A coin with fewer than 500 daily bars is reported but its bars still enter; no coin is added or dropped after outcomes |
| Bars | UTC days; the partial current day is dropped. Warm-up: first 400 bars of each coin produce no event and no placebo draw (SMA350 and ATR need history) |

## Candidates
PRIMARY (carries the verdict): A. HL_BREAK. SECONDARY (reported, descriptive, one extra test counted in the multiplicity note): B. BULL_DIV.

Swing low (causal): bar i is a swing low if `Low[i] < Low[i-3..i-1]` and `Low[i] < Low[i+1..i+3]` (k = 3, OURS). It is KNOWN only at the close of bar i+3; nothing earlier uses it.

A. HL_BREAK: second swing low L2 (index j) and the swing low before it L1 (index p) with `Low[j] > Low[p]` and `10 <= j-p <= 60` (OURS). H = max High over bars p..j. Signal at the first bar c in j+3..j+33 (setup expires 30 bars after L2 is known, OURS) with `Close[c] > H`, provided no bar in j+1..c has `Low <= Low[j]` (second low not violated) and no earlier bar in j+3..c-1 closed above H. A close above H on bars j+1..j+2 (before L2 is known) does not count and does not use up the setup; the first qualifying close is at c >= j+3.
B. BULL_DIV: same as A but with `Low[j] < Low[p]` (lower price low) AND `RSI14[j] > RSI14[p]` (higher RSI at the second low), RSI Wilder smoothing, 14, closed bars. In B the second-low-not-violated test is `Low > Low[j]` after j as in A. WaveTrend is not used (OURS: RSI only).

Stop at entry: `Low[j] - max(0.6 x ATR14[c], 0.005 x Low[j])` (NEXT5 Shared rule, SOURCED). ATR14 Wilder, closed bars. Risk fraction r = (entry - stop) / entry, entry = Open[c+1]. An event with entry <= stop is dropped (counted).
Exit (SOURCED, Test 1): first of (a) trailing stop, (b) 30 days. Trailing level at bar t = `max(initial stop, max High[e..t-1] - 2 x ATR14[t-1])` using only bars before t (e = entry bar); if `Low[t] <= level`, exit at `min(Open[t], level)`. (b) Exit at Close[e+29]. If the exit bar is not in the data yet the event is dropped. On the entry bar itself only the initial stop is checked.
Return: `gross = exit/entry - 1`; net12 = gross - 0.0012; net6 = gross - 0.0006 (round trip). R = net / r. Reported mean R is per trade at 12 bp (main) and 6 bp (sensitivity).

## Phase (OURS, from the daily bar of the previous day only; evaluated at bar e-1 for entry bar e)
With SMA200 and SMA350 (= 50 weeks) of closes, DD = 1 - Close / (max High over the last 365 bars), and higher-low = `min Low[t-59..t] >= min Low[t-179..t-60]`. A day gets the first that matches:
1. UP: Close > SMA200 and SMA200[t] > SMA200[t-30].
2. BASE: not UP, DD >= 0.40 and higher-low true.
3. POSTPEAK_BEAR: not UP, not BASE, Close < SMA350, SMA350[t] < SMA350[t-30] and DD >= 0.40.
4. DOWN: not 1-3, Close < SMA200 and SMA200[t] < SMA200[t-30].
5. RANGE: everything else.

## Events and lockout
Events per coin in signal order. A signal is dropped if its signal bar is < 10 bars after the previous KEPT signal bar of the same coin, or its entry bar is on or before the previous kept trade's exit bar (no overlap). Long phases for the claim: phase in {UP, BASE} (looked up at e-1).

## Splits
DEV: entry date <= 2023-12-31. VAL: entry date >= 2024-01-01 (to the last closed bar). RECENT: entry date >= 2025-07-01, a subset of VAL, reported separately, never used to choose anything.

## Placebo (>= 1000 draws)
For every group x split cell, 2000 draws (seed 1114): each event is replaced by an entry at the open of a uniformly random eligible day of the SAME coin, SAME split, with phase at e-1 equal to the event's phase, past warm-up and with the exit in the data. Same stop distance (r of that event), same exit rule (trail 2 x ATR14 from entry, max 30 days) and same fee. Per draw the mean R is computed; the placebo band is the 2.5th to 97.5th percentile of the 2000 draw means, and the percentile of the actual mean within the draws is reported. "Beats the placebo band" = actual mean R above the 97.5th percentile. No lockout is applied to placebo draws (stated).

## Bootstrap
Block bootstrap of the pooled per-trade R: blocks are 30-calendar-day windows of ENTRY date (block = hold length, SOURCED Shared rule), all coins in a window form one block; 10000 resamples of blocks with replacement, seed 1114, percentile 95% CI of mean R.

## Verdict (SOURCED, Shared rules; applied to PRIMARY A, pooled UP+BASE, VAL, 12 bp R)
- UNDERPOWERED (do not claim) if VAL pooled n < 30.
- PASS only if VAL mean R (12 bp) > 0 AND bootstrap CI low > 0 AND actual mean R > placebo 97.5th percentile AND DEV mean R (12 bp) > 0 (sign agrees).
- Otherwise KILL, stated with the VAL mean R, CI, placebo percentile and n.
- The 6 bp row, RECENT, per coin, the DOWN/POSTPEAK_BEAR/RANGE control and secondary B are descriptive and cannot change the A verdict. B gets its own PASS/KILL line by the same rule but is labelled secondary (two tests run, multiplicity noted; a B-only PASS needs independent replication before any use).
- Per-coin rows with n < 30 are marked underpowered.

## Output
`REPORT.md`, `summary.json`: table per coin and pooled with n, win %, mean R 12 bp, mean R 6 bp, CI, placebo percentile, DEV/VAL/RECENT columns. Data files never committed.
