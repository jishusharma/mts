# BLOCKED: none of the 8 counted Quad Rotation cells (1m, 5m) can be frozen (2026-10-18)

`prereg_gate.py` exited 1 for all 8 TF x arm x side candidates (m = 8, sd = 1 SD unit, cost = 14 bp / median stop bp in R).
Stochastic arm: stop width 6-7 bp (1m) and 18-23 bp (5m) against a 14 bp round trip, fee 2.1-2.3 R (1m), 0.60-0.79 R (5m): cost alone exceeds the 0.30 R ceiling. RSI arm: 3-18 event-days, MDE 0.84-2.06 SD.
Nothing is frozen; no outcome may be read for these cells. FAIL/INCONCLUSIVE: stop; this BLOCK (count-only, no outcome read) covers only Quad Rotation on BTCUSDT 1m and 5m with bands (9,3),(14,3),(40,4),(60,10) D-line, the pattern-low stop and a 14 bp taker round trip; 15m and 1h, a minimum-stop filter, a maker entry or a tick stop are untested and need their own PRE_REG and gate. See PRE_REG.md s4-s5 for the table.
