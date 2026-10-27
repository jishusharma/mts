# GPT formula re-derivation: sections 2–5

Verdict: SOUND

## Checked

- `MyTradingSys/backtest/layers/FORMULAS.md:59-119` definitions and worked examples for RMA, SMA, seeded EMA, and WMA.
- Hand calculation on `x = [1,2,3,4,5,6,7,8,9,10,11,12]`, length 3. Values below are aligned at indices 0–11; the first two are `None` because a complete 3-value window is not yet available.
- Compared the independent sequences with `MyTradingSys/backtest/layers/rsi/rsi_ma.py` using:
  `python -c` (import `rsi_ma`; evaluate each type on `list(range(1,13))`, length 3).

## Independent derivation and comparison

RMA seed at index 2 is `(1+2+3)/3 = 2`; alpha is `1/3`; thereafter each value is previous plus one third of the difference to the new input. SMA is each trailing 3-value sum divided by 3. EMA seed is 2 and alpha is `2/(3+1)=1/2`; each next result is the midpoint of the previous result and new input. WMA uses weights `[1,2,3]` and denominator 6 on every trailing window.

| Type | Hand-derived outputs (indices 2–11) | Implementation maximum absolute difference |
|---|---|---:|
| RMA | 2, 2.6666666667, 3.4444444444, 4.2962962963, 5.1975308642, 6.1316872428, 7.0877914952, 8.0585276635, 9.0390184423, 10.0260122949 | 0 |
| SMA | 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 | 0 |
| EMA | 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 | 0 |
| WMA | 2.3333333333, 3.3333333333, 4.3333333333, 5.3333333333, 6.3333333333, 7.3333333333, 8.3333333333, 9.3333333333, 10.3333333333, 11.3333333333 | 0 |

The implementation output matched each independently computed value (maximum difference 0.0 for all four types, below 1e-9). For this arithmetic input, EMA after the seed equals the trailing SMA; the comparison still confirms the specified seed and recurrence on this series.

## Findings

No findings. Sections 2–5's seed, alpha, window, and weight rules agree with the independent calculations and implementation output. No code or spec changed.
