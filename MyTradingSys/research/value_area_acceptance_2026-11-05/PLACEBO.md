# PLACEBO: how much of the 77% acceptance claim is just same-day volatility?

Regime mix: NOT_IN_DATA (descriptive study, no regime spec frozen; 666 days 2024-12-02..2026-09-28 of Binance spot 1m, F:/MTS/data/orderflow_1m)

**Verdict: real Event A = 77% [72..81] (n = 300); random day, same segment and distance = 64% (95% of draws 60..69); the label adds 12.6 points over the placebo (>= 10: YES).**

Method: `placebo80.py` imports `accept80.py` (days, va, m30). Each real Event A (two consecutive 30m closes below the prior day's VAL) keeps its 30m segment index k and the distance d it needed below its own close; a placebo draw gives every event a random UTC day that is not an Event-A day and asks whether the rest-of-day low reaches close_k - d. 2000 draws of 300 events, seed 7. Descriptive: no fee, no trade rule, no return.

| variant | real hit rate | placebo mean | placebo 2.5% | placebo 97.5% | real - placebo |
|---|---|---|---|---|---|
| needed distance d = close_k - (VAL - w/2) | 77.0% | 64.4% | 60.0% | 68.7% | +12.6 pts |
| exact width d = w/2 from the close | 62.3% | 43.6% | 38.7% | 48.7% | +18.7 pts |

Excluded placebo days: the 300 distinct Event-A days; eligible days per segment = days with that 30m segment, minus those.
Context: this is a continuation-probability check on one label, not an edge: nothing here is traded, so no fee-net result exists. Test: `test_placebo80.py` (synthetic drift and flat series, seed determinism).
