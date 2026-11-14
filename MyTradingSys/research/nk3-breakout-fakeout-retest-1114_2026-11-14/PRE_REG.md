# PRE_REG: NK breakout retest / fakeout fade (video wrEEf8o9n9E), 2026-11-14

Written before any outcome was computed. Labels: SOURCED = NK said it (EXTRACT wrEEf8o9n9E, quote #); OURS = our choice.

## Context
Regime: UP / DOWN / RANGE per day, from data known at the prior daily close (OURS, operator order 11-14).
Phase: UP = ADX14(1d) >= 20 and +DI > -DI and MA20(1d) slope (MA20[d-1] - MA20[d-6]) > 0; DOWN = ADX14 >= 20, -DI > +DI, slope < 0; else RANGE. Wilder smoothing.
Session: none (24h).
Entry: see Rules.

Regime mix: reported in RESULT.md per split (share of coin-days per phase, and trades per phase per row). Primary rows trade only the phase-fit direction; the mismatched direction is a control row, never a pass row.

## Data
Binance spot USDT, 15m klines, 20 coins (BTC ETH BNB XRP ADA SOL DOGE LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO), 2019-01 to latest closed bar; 1h built from 15m on UTC boundaries; daily from complete UTC days. Cache F:\MTS\data_cache\binance_spot. DEV: signal bar <= 2023-12-31. VALIDATION: >= 2024-01-01. Gates are on VALIDATION only.

## Rules (all parameters fixed here)
- Range box (OURS; length 20 = NK's BB length, SOURCED #1): H/L = max high / min low of the 20 bars before bar B. Width filter OURS: 1.5 <= (H-L)/ATR14[B-1] <= 4.0 (ATR Wilder, signal tf).
- Breakout bar B: close > H (up break) or close < L (down break). Breakout candle = B.
- Fakeout test (SOURCED #10, #13): up break is a fakeout when bar B+1 high <= B high AND B+1 close <= H (back inside); mirror for down. Else if B+1 takes out B's high/low, it is a true breakout.
- Type A, true-breakout retest (SOURCED #9 "retest trading is best trading"; retest zone = broken box edge, OURS; NK's MA/AVWAP retest not used): after confirmation, within K=10 bars (OURS) starting B+2, first bar whose low < H (long) / high > L (short) fills a limit at the edge (min(H, open) long). Stop = breakout candle low (long) / high (short) (SOURCED #5/#7 prior-candle-extreme stop, mapped by us). Primary: long in UP, short in DOWN. RANGE: no type A.
- Type B, fakeout fade: entry at close of B+1, opposite to the break; stop = breakout candle extreme (OURS). Primary: RANGE both ways; UP long only (fading down-break fakeouts); DOWN short only.
- Control rows: mismatched direction (A: short in UP / long in DOWN; B: short in UP / long in DOWN). Not in BH family, no PASS.
- Minimum stop (OURS, from today's lesson): stop distance = max(natural, 0.6 x ATR14[B-1], 0.5% of entry). Fee as a fraction of R is reported.
- Exits: X1 (OURS): target 2R, stop, time exit at close of bar +24; X2 (SOURCED #6 trail with previous candle low/high): stop trails to previous bar's extreme from the 2nd bar after entry, never loosened, time exit at +48 bars. Same-bar stop and target = stop. Stop checked on the fill bar for type A. Gap through stop fills at open.
- One position per coin per row (next signal must be after the previous exit).
- Optional Bollinger blast filter (OURS; std-dev 2.0 NOT_STATED by NK): BB(20,2) bandwidth at B-1 in lowest 25% of its prior 100 bars and BW[B] >= 1.15 x BW[B-1].
- Costs: taker 12 bp round trip is primary; maker-entry 6 bp is a pre-registered sensitivity row (same trades), not PASS-bearing.

## Rows
Phase-fit family (BH family, 16 rows) = type {A,B} x tf {15m,1h} x exit {X1,X2} x filter {none, blast}, at 12 bp. Controls and maker rows reported separately.

## PASS gates (VALIDATION, phase-fit row, 12 bp)
n >= 100; mean net R > 0; bootstrap 95% CI lower > 0 per trade (10000 resamples) and per UTC-day cluster (resample days); beats matched random entries, p < 0.05 (placebo: same coin, phase, direction, same stop% and exit rule, random bar in VALIDATION, 300 draws, p = share of draws with mean >= observed); survives Benjamini-Hochberg q=0.05 over the 16-row family (p = day-cluster bootstrap one-sided p); mean net R > 0 after removing the 5 best days.
Verdict is PASS only if some row passes all gates; else FAIL, with the nearest row named.

## Tests
test_study.py: causality (truncated vs full series give identical phases and signals); fails under env STUDY_BUG=1 (phase uses same-day close) and STUDY_BUG=2 (fakeout test peeks B+2).
