SOUND

## Scope and method

Audited `MyTradingSys/backtest/layers/FORMULAS.md` §21 and `MyTradingSys/backtest/layers/krown/krown_core.py`. The implementation functions were invoked directly on the same 10-bar toy arrays below using:

`python -` (inline script importing `krown_core`; calls `vol_ratio(v,3)`, `engulfing(h,l,1)`, and `rsi(c,2)`)

Toy closes: `[10,11,10,11,10,11,10,11,10,11]`; highs: `[10.5,11.5,10.5,11.5,10.5,11.5,10.5,11.5,10.5,11.5]`; lows: `[9.5,9,9.5,9.5,9.5,9.5,9.5,9.5,9.5,9.5]`; volumes: `[100,120,80,200,90,110,130,70,160,100]`. Each output is at the stated bar index. RSI uses period 2 and volume ratio uses n=3 to make the definitions hand-checkable on ten bars.

## Formula inventory and findings

| Severity | Formula and definition evidence | Krown implementation evidence | Hand calculation vs code | Result / proposed fix |
|---|---|---|---|---|
| LOW | **KR-V01/V02 volume ratio, OURS baseline** — FORMULAS.md:538: “ratio = V / mean of the n=20 PRIOR volumes (the current bar is excluded…)”. | `krown_core.py:84-90`: `vol_ratio`; line 88 averages `v[t-n:t]`, line 89 divides current volume by that mean. | At t=3, prior volumes 100,120,80 average to 100; V=200; hand ratio = 200/100 = **2.0**. Code `vol_ratio(v,3)[3]` = **2.0**. | **MATCH**. None. |
| LOW | **KR-C06 strict engulfing, SOURCED** — FORMULAS.md:540: “low < prior low AND close > prior HIGH” for bullish. | `krown_core.py:142-150`; line 146 requires `l[i] < l[i-1]` and `c[i] > h[i-1]`, returning `bull`. | At t=1, prior low=9.5 and prior high=10.5; current low=9 and close=11. Both strict inequalities hold; hand = **bull**. Code `engulfing(h,l,c,1)` = **bull**. | **MATCH**. None. |
| LOW | **KR-S02 Wilder RSI, period OURS** — FORMULAS.md:548: initial gain/loss are simple means of first period changes, then each is `(avg*(period-1)+x)/period`. | `krown_core.py:289-310`; lines 297-298 SMA seed, lines 305-309 recursive Wilder updates, line 303 RSI transform. | For the alternating +1/−1 close changes, period-2 seed at t=2 is avg gain=0.5 and avg loss=0.5, RSI=50. Thereafter Wilder recursion yields t=3: 75; t=4: 37.5; t=5: 68.75; t=6: 34.375; t=7: 67.1875; t=8: 33.59375; t=9: **66.796875**. Code `rsi(c,2)[9]` = **66.796875**. | **MATCH**. None. |

All three audited formulas are used by Krown code. The checked outputs are SAME; no DIFFERENT or NOT_IN_DATA rows.

## Follow-up cards

None.
