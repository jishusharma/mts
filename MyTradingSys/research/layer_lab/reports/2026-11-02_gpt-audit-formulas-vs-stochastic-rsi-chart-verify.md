# Audit: FORMULAS.md s23 Stochastic RSI vs scripts/dev/chart_verify.py (2026-11-02)

Verdict: **SAME** (all formulas, all 3 hand values). Report only; no code edited.

## Formulas
| Formula | FORMULAS.md | Code |
|---|---|---|
| RSI = Wilder RSI(rsi_len) (s1) | s23 line 562 | chart_verify.py:24-25 (delegates to rsi_core) |
| raw = 100*(r-min)/(max-min) over last stoch_len RSI values, all must exist | s23 | chart_verify.py:52-56 |
| max==min -> raw 0 (OURS) | s23 | chart_verify.py:56 |
| K = SMA(raw,k_len); D = SMA(K,d_len), None if any input None | s23 | chart_verify.py:28-34, 57-58 |
| Defaults 14,14,3,3 | s23 | chart_verify.py:48 |

## Toy series (10 bars), rsi_len 2, stoch_len 3, k_len 2, d_len 2
closes = [10,11,10,12,11,13,12,12,14,13]. Hand (Wilder, seed = SMA of first 2 changes, then (prev+x)/2):
RSI[2]=50, [3]=83.3333, [4]=50, [5]=80.76923, [6]=50, [7]=50, [8]=87.64706 (ag 1.1640625, al 0.1640625), [9]=50.
raw[4]=0, raw[5]=92.30769, raw[6]=0, raw[7]=0, raw[8]=100, raw[9]=0.

| Value | Hand | Code | Result |
|---|---|---|---|
| K[5] = (0+92.30769)/2 | 46.15385 | 46.15384615 | SAME |
| K[8] = (0+100)/2 | 50 | 50.0 | SAME |
| D[7] = (K6+K7)/2 = (46.15385+0)/2 | 23.07692 | 23.07692308 | SAME |
Also SAME: K[6]=46.15385, K[7]=0, K[9]=50, D[6]=46.15385, D[8]=25, D[9]=50, RSI[8]=87.64706.

Command: python with `chart_verify.stochrsi(c,2,3,2,2)` on the series above (temp script, not committed).

## Notes
- First-K index rule (s23: rsi_len+stoch_len-1+k_len-1 = 2+3-1+2-1 = 5) matches the code: first K at index 5.
- RSI maths itself (rsi_core) was taken as given from s1; only its output on this series was checked (matches).
- DECISION (OURS): short windows used so a 10-bar series is enough; defaults 14/14/3/3 are the same code path.
