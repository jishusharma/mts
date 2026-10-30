# C26 pre-registration: trading the held 15m retest (written 2026-10-31, before any P&L run)

Operator: "Yes, pre-register" (10-31). Source study: C26, `failed_retest_takeout.py` (base rates only; no P&L computed yet).
Every number below is OURS. Nothing here is changed after the run; a changed rule is a new id (C26c...).

## Honesty about the data
2022-01..now was already used for the C26 base rates, so a history run is a SEEN-PERIOD check, not a clean test.
The clean test is FORWARD: events from 2026-11-01 00:00Z on, scored by the same script, until n >= 30 per arm.

## Events (unchanged from C26)
Pivot = highest high (lowest low) of +-16 15m bars; pull-back >= 0.8%; first retest within 0.4% not exceeding it, pivot age <= 72h;
decision bar j = retest bar + 4 if the pivot is still not exceeded and the close is on the near side. Lows = exact mirror.

## Arm A: RIDE TO THE LEVEL
At a held high: long at the open of j+1 (held low: short). Exits, first hit wins, checked bar by bar:
- target: the pivot level (a high touching it fills at the level),
- stop: entry -0.8% (mirror +0.8%); if target and stop fall in the same bar, count the stop,
- time: close of bar j+96 (24h).

## Arm B: FADE THE SWEPT TAKE-OUT
After the take-out bar k of a C26 event (first bar beyond the pivot, within 72h of j): the first 15m close back on the near side
within bars k..k+4 = signal bar s. Short at the open of s+1 at a high (long at a low). Exits:
- stop: the most extreme high since k plus 0.05% (mirror for lows); same-bar tie = stop,
- target: entry -1.0% (mirror +1.0%),
- time: close of bar s+96 (24h).

## Costs and scoring
Fee = `BINANCE_TAKER * 2` from `backtest/fees.py` per trade; slippage and funding not modelled (stated, not hidden).
Per arm and side, per period (2022-01..2024-06, 2024-07..2026-10-31, forward): n, win %, mean net %, t-stat of the mean.

## Pass (all must hold, else the arm is a NO)
1. Seen-period check: mean net > 0 in BOTH periods, n >= 100 each, highs and lows pooled.
2. Forward: mean net > 0 with n >= 30 before any live use; one look at n = 30, no peeking rule changes.
3. A pass is still research: no order, no size, no live path without the operator and the normal gates.
