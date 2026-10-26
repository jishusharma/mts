# P4 CORRECTED - quarter-hour opening imbalance: RESULT (2026-10-08)

**Verdict: NO REPLICATION at 4h, 8h and 12h.** Supersedes `P4_QUARTER_HOUR_IMBALANCE_20261006_FINAL.md` (invalid: 4 opens/day,
long-only returns, entry at the open of the bar whose imbalance it used). Pre-registration: `PRE_REG_P4_CORRECTED_2026-10-06.md`.
Reproduce: `python MyTradingSys/research/loose_code/p4_corrected.py` (about 15 s, data `F:/MTS/data/orderflow_1m`, numpy only).

## Result
The signed gross edge is about zero at every window (+0.43, +0.10, -0.24 bp against a 10 bp round-trip fee). The gross sign
is not stable across years at any window. The net CI sits wholly below zero because of fee drag.

```
bars 959021  2024-12-02 00:00 .. 2026-09-28 23:59
## 4h: n=63918  gross mean +0.43 bp  net mean -9.57 bp  net CI95 [-10.35, -8.74]
   2024: gross mean +3.85 bp  n=2880
   2025: gross mean +0.60 bp  n=35038
   2026: gross mean -0.17 bp  n=26000
   sign stable across years: False   CI above zero: False   placebo net -9.94 bp CI [-10.63, -9.27]
   VERDICT 4h: NO REPLICATION
## 8h: n=63902  gross mean +0.10 bp  net mean -9.90 bp  net CI95 [-10.96, -8.87]
   2024: gross mean +3.57 bp  n=2880
   2025: gross mean -0.25 bp  n=35038
   2026: gross mean +0.18 bp  n=25984
   sign stable across years: False   CI above zero: False   placebo net -10.89 bp CI [-11.99, -9.80]
   VERDICT 8h: NO REPLICATION
## 12h: n=63886  gross mean -0.24 bp  net mean -10.24 bp  net CI95 [-11.63, -8.90]
   2024: gross mean +3.48 bp  n=2880
   2025: gross mean +0.11 bp  n=35038
   2026: gross mean -1.11 bp  n=25968
   sign stable across years: False   CI above zero: False   placebo net -9.00 bp CI [-10.42, -7.59]
   VERDICT 12h: NO REPLICATION
```

## What was wrong with the first run (so the 8h "PASS" is void)
1. Opens were 4 per day, not 96.
2. Returns were never signed by the imbalance, so it measured long-only drift minus fee.
3. Entry used the open of the same 1m bar whose imbalance was the signal (look-ahead); now entry is that bar's close.
4. Decision rule "CI excludes zero" also passes a strategy that reliably loses the fee. Implemented as lower bound > 0.
   The new test `test_p4_corrected.py::test_no_edge_gross_near_zero_and_no_pass` failed on that rule before the fix.

## Interpretation choices (pre-reg silent; fixed before the first run, nothing tuned)
Signal = sign of the open bar's (buy-sell)/(buy+sell); entry = close of that bar; exit = close W minutes later; day-block bootstrap
(seed 12345, 2000 draws); placebo = imbalance signs shuffled across opens. Full list in the script docstring.

## Limits
2024 is December only (n=2880) and 2026 runs to 28 Sep. One venue/instrument (BTCUSDT futures). Windows overlap heavily
(96 opens/day against 4-12 h holds): the day-block bootstrap absorbs this approximately, not exactly. None of it changes the
verdict, since the gross mean is itself about zero.

## Disposition
P4 is closed: no live use, nothing to wire. Do not re-test with other windows or thresholds (that would be tuning).
