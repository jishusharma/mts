# F4 PRE-REG: 8h look-alikes of the operator setup (BB squeeze-break on volume, RSI under SMA, StochRSI, CVD proxy), BTCUSDT spot

Frozen 2026-10-31 BEFORE any outcome was computed (no run of run_f4.py exists at this commit). Card fractal-state-analog-8h-f4;
operator screenshot 477f9045b120. Every parameter is OURS unless marked SOURCED. Nothing is tuned after the run.

## Data (SOURCED: card)
- Binance spot BTCUSDT 1h klines (public, data.binance.vision monthly files) 2017-08..2025-06, kept outside the repo; rows with open time >= 2025-07-01 are dropped at load, HOLDOUT never loaded. (The 1m DEV store F:/MTS is absent on this host; 1h gives the same taker-buy column 9 and more cycles than F3: 2017-08..2025-06 instead of 2022-01..2025-06.)
- 8h bars = UTC 00/08/16 buckets of 8 consecutive 1h bars, complete buckets only. Missing hours make a bucket absent. A signal at bar s is valid only if bars s-130..s are consecutive and the next 9 bars (trade path) are consecutive.
- Decision at the CLOSE of signal bar s; every feature at s uses bars <= s only (indicators are causal; volume z uses bars s-20..s-1); entry = open of the first 1h bar after s.

## Features on 8h closes
BB(20, 2.0, population std): mid, upper, lower, bandwidth bw = (upper-lower)/mid, %b = (c-lower)/(upper-lower). RSI14 (Wilder, ewm alpha 1/14); RSI gap = RSI - SMA14(RSI); StochRSI k = SMA3 of (RSI - min14 RSI)/(max14 - min14) (0..1). Volume z = (v[s] - mean(v[s-20..s-1])) / std(same, ddof 0). CVD proxy: delta = 2*taker_buy_base - volume (kline col 9); cvd slope = sum(delta[s-7..s]) / sum(volume[s-7..s]) (net taker share over the last 8 bars, in [-1,1]). bw percentile = fraction of bw[s-90..s-1] <= bw[s-1] (pre-break squeeze rank).

## Events
- (a) RULE: rank of bw[s-1] among bw[s-90..s-1] <= 0.30; bars s-6..s-1 all closed inside their own bands (lower <= c <= upper); c[s] < lower[s]; volume z[s] >= 2.
- (b) ANALOG: query = every valid bar with %b[s] < 0 (close below the lower band). Library = valid bars e' with %b[e'] < 0 and e' <= s-9 (outcome at 9 bars fully known), expanding, stride 1; at least 200 library bars else no query. Vector = 24-bar z-scored log-close path c[s-23..s] (each dim weighted sqrt(7/24), so shape is half the squared distance) + 7 scalars (%b, bw pct, RSI14, RSI gap, StochRSI k, volume z, cvd slope) each standardised with the library's own mean/std and weight 1. k = 20 nearest by Euclidean distance, greedy with spacing >= 3 bars between chosen. Direction per horizon h: mean of the 20 neighbours' own fee-net R for "continuation short" and for "fade long" (below); trade the larger mean if > 0, else no trade. The screenshot window itself (2026) is outside DEV, so excluded by construction.
- Non-overlap: per event set and horizon, an event is skipped if its entry is before the exit bar (s+h) of the previous taken trade.

## Trades (SOURCED: card)
Entry E = open of the first 1h bar after s. Horizons h = 3, 6, 9 bars (24/48/72 h). Continuation short: stop = high[s] (1R = high[s]-E, must be > 0), target E - 2R. Fade long (mirror): stop = low[s] (1R = E-low[s] > 0), target E + 2R. Path walked on 1h bars from entry to bar s+h; if stop and target are both inside one 1h bar, the stop counts first; no stop slippage; time exit at the close of bar s+h. Costs: taker on both legs, fee = fees.BINANCE_TAKER x (E + exit price); net R = gross R - fee/1R. Also report net % of E.

## Controls
- B1 (card baseline): random 8h bars with matched realised vol: vol = std of the last 30 8h log returns at s (bars <= s); quintile edges from all valid bars; each real event is replaced by a random valid bar of the same vol quintile, same trade type (and, for ANALOG, random direction with the observed long share). 2,000 draws, seed 41. p = (1 + #draws with mean >= real mean)/(1 + 2000), one-sided.
- B2 (descriptive, no verdict): the same but drawn only from bars with %b < 0 (same state gate, random bar).
- Block bootstrap: events resampled in calendar-month blocks, 2,000 resamples, seed 41, 95 % percentile CI of mean net R. Halves A/B = first/second half of the events in time.
- Holm over the 9 tests {RULE cont, RULE fade, ANALOG} x {3, 6, 9} against B1, alpha 0.05.
- Power: harness.power_n(sd of net R per trade, 0.10 R) reported per set; n below it is descriptive + forward log (d-flexible-min-n-per-case).

## Splits (descriptive, all at h = 6, time order, entry date's row of phase_tag/tags.csv)
1. Phase cells: cowen_side|sma200_side; wsma10_phase; dd_bin; cycle_year (cycle_year listed only, no test). Family-wise: harness.shift_null_test (1,000 shifts) per labelling per event set; a cell with n < 10 is shown but excluded from flags.
2. Layer states, available only from 2022-01 (DEV store of those layers): RSI-DIV-MTF fired = any event in p1b_rsi_feenet/events_feenet.csv with entry time in the 3 bars (24 h) before the signal bar close, y/n; Hurst regime = rolling 1h DFA H (f2/dfa.py, window 480, from these same 1h bars, value at the last hour of bar s): <0.45 / 0.45-0.55 / >0.55. Analyst-level proximity: no point-in-time DEV list exists, NOT RUN.

## Verdict rule per (set, horizon), frozen
- NOT_DECIDABLE: n < 30.
- PASS: mean net R > 0, Holm-adjusted p vs B1 < 0.05, bootstrap CI lower bound > 0, mean > 0 in both halves.
- FAIL: decidable and CI upper bound < 0.
- Otherwise INCONCLUSIVE. An honest negative is valid; no rule, gate or layer is added.

## Trials (rows in layer_lab/TRIALS.md)
F4-1..3 RULE cont h3/6/9; F4-4..6 RULE fade h3/6/9; F4-7..9 ANALOG h3/6/9; F4-10 phase splits; F4-11 layer splits. One k, one L, one set of thresholds: no variant tried.

## Tests (run_f4 tests, written before the module)
Features at s unchanged when later bars are altered; CVD proxy by hand on 3 bars; trade simulator by hand (stop-first, target, time exit, fee); RULE detector on a hand-built squeeze; planted-edge p-value detects a +0.3 R shift and not the null.
