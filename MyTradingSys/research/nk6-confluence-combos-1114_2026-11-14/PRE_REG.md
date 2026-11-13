# PRE_REG: NK confluence combos (nk6-confluence-combos-1114), written BEFORE any outcome is computed

Source of rules: NK (@NKStockTalk) extracts in research/nk_stocktalk_1113/flash_deep (JLcDdrHkB5M first-hour low break + Hilega Milega; 3EpXq8JC4jU standard pivot, RSI 30 re-cross + close above pivot, "buy when close above R1", stop on closing basis; wrEEf8o9n9E breakout / retest / fakeout). Label: SOURCED = NK said it, OURS = our choice.

## Data
Binance spot USDT 15m, 20 coins (BTC ETH BNB XRP ADA DOGE SOL LTC TRX LINK DOT AVAX ATOM ETC XLM BCH UNI NEAR FIL ALGO), from 2019 where listed, to 2026-11-13 20:30Z. Cache F:\MTS\data_cache\binance_spot. DEV: signal date <= 2023-12-31. VALIDATION: >= 2024-01-01.

## Context (operator order: context first)
Daily phase for UTC day D from daily bars closed on D-1 only: UP = ADX(14,Wilder) >= 20 and +DI > -DI and SMA20(close) rising over 5 days; DOWN = ADX>=20 and -DI > +DI and SMA20 falling; else RANGE (ADX 20 OURS, operator-ordered; SMA20/5-day slope OURS).
Primary rows: longs in UP, shorts in DOWN, both directions in RANGE (fade = take whichever layers fire). Control rows (not in BH, not a PASS path): shorts in UP, longs in DOWN.
`## Context` and `Regime mix:` reported in RESULT.md (share of bars, trades per phase, DEV vs VAL).

## Layers (15m bar i, UTC day session, all computed from bars <= i)
Long / short booleans. Event layers (1,2,3,5) are "active" for 4 bars after the event (K=4, OURS); layer 4 is a state at bar i.
1. First-hour break and reclaim (first hour = UTC 00:00-01:00, OURS; NK uses first 10 min of the Indian session): from 01:00. Long: close crosses back above first-hour low (prev close <= FHlow < close). Short: close crosses back below first-hour high.
2. Standard pivots from previous UTC day (SOURCED: standard pivot, P/R1/S1; levels subset OURS): long = close crosses above P, S1 or R1, or (low<=S1 and close>S1) rejection; short mirror with (high>=R1 and close<R1).
3. Breakout retest / fakeout (concept SOURCED, numbers OURS): level U = max high of bars i-26..i-7, D = min low same window. Breakout = close beyond U (D). Long = within 6 bars after an up-breakout, low <= U*1.001 and close > U (retest holds), OR within 6 bars after a down-break, close back above D (fakeout). Short mirror.
4. Hilega Milega (periods OURS: RSI(9), EMA(3) of RSI, WMA(21) of RSI; NK states: red under green = buy, red above = sell): long = RSI9 > EMA3 > WMA21; short = RSI9 < EMA3 < WMA21.
5. 15m RSI(14) extreme (SOURCED 30/70 re-cross): long = RSI14 prev < 30 and now >= 30; short = prev > 70 and now <= 70.
Context layer: phase (above) and session VWAP (UTC-day reset, typical price): VWAP-aligned = long if close > VWAP, short if close < VWAP.

## Combinations (full list, 33 combos; "A&B" = both layers active in the trade direction, others unconstrained)
Singles: L1, L2, L3, L4, L5 (5). Pairs: all 10 (L1&L2 ... L4&L5). Triples: all 10. Count buckets: exactly 1, exactly 2, exactly 3, 4 or more layers agree (4). VWAP variants: the same 4 count buckets AND VWAP-aligned (4). Total 5+10+10+4+4 = 33.
Trade fires on the onset bar (combo true now, false on previous bar), per coin per direction, no overlapping trades (next signal only after prior exit).

## Trade management (OURS)
Entry next bar open. Stop distance S = max(1.0 x ATR(14,15m), 0.5% of entry) (minimum stop pre-registered: >= 0.6 x ATR and >= 0.5%). Target 2R, time exit after 24 bars at close. Stop touched intrabar; stop and target in same bar = stop. Fee: 12 bp round trip taker (primary), plus one maker row at 6 bp (assumes fill; no fill-risk model, flagged optimistic). Net R = gross R - fee_bp*1e-4*entry/S. Fee as fraction of R reported per row.

## Gates for PASS (on VALIDATION, primary phase-matched rows, 12 bp)
n >= 100; mean net R > 0; bootstrap 95% CI lower > 0 per trade (2000 resamples) AND per UTC-day cluster (2000 resamples of days); placebo p < 0.05 (1000 draws: same coin, same direction, same count of trades, random VAL bars where that direction is phase-eligible, same management); BH q < 0.05 over the family of 33 combos x {12 bp, 6 bp} = 66 rows using the one-sided day-cluster bootstrap p (all rows count, including n<100); mean net R > 0 after removing the best 5 UTC days. A combo passes only if all gates hold at 12 bp. The 6 bp row is informational unless the 12 bp row passes.
Bundle: a PASS needs the combination to hold on its own, not the best of many (BH handles that).
Tests: test_study.py has a causality test (features at bars < T unchanged when data after T is removed) that fails under STUDY_BUG=1 (phase labelled with same-day close) and passes on the real code.
