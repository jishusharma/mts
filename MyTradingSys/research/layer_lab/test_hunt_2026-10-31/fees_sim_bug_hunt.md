# Fees and simulator bug hunt — 2026-10-31

Verdict: FIX-FIRST — reproducible invalid-fee acceptance and NaN price handling; funding coverage is absent from this simulator API.

## Scope and method

Read `MyTradingSys/backtest/fees.py` (1-59), `sim.py` (34-87), `test_no_own_costs.py`, `test_sim_planted_edge.py`, and `MyTradingSys/backtest/layers/FORMULAS.md` sections 11 and 13. Synthetic in-memory rows only; no market data read. Command: inline Python importing `sim` and `fees` and calling `sim.run` / `fees.fees_dict`. No source changes and no tests executed. Fee numbers independently use profile B (`entry=maker=0`, taker=0.0005) from fees.py 19-23, 31-49. Funding arithmetic uses FORMULAS.md 13.

## Findings

| Severity | File:line | Finding and reproducing input | Expected (independent) vs actual | Proposed fix |
|---|---|---|---|---|
| MED | `MyTradingSys/backtest/fees.py:42-44` | `fees.fees_dict(-1, float('nan'), 0, 2)` | Expected reject: fee fractions must be finite and nonnegative. Actual `{'entry': -1, 'target': nan, 'stop': 0, 'timeout': 2}`. This allows invalid profile values to propagate silently. | Validate all four rates as finite, nonnegative fractions; reject invalid values with `ValueError`. |
| HIGH | `MyTradingSys/backtest/sim.py:62-64` | rows `[{'t':0,'ts':'x','verdict':'SETUP_FORMING','stop':99,'target':102,'price':nan,'dir':'long','setup':'s'}, {'t':60,'ts':'y','verdict':'x','stop':None,'target':None,'price':102,'dir':'long','setup':'s'}]`; `run(rows,'A','observed',.0005,0)` | Expected: reject non-finite entry price, since risk, gross and fee math are undefined. Actual `[]` (setup silently skipped because NaN makes both sides of geometric comparison false). | Validate finite entry/stop/target and report malformed input; do not silently treat as no signal. |
| HIGH | `MyTradingSys/backtest/sim.py:68-77` | valid long entry 100/stop 99/target 102 at t=0; path rows at t=60 price=NaN and t=120 price=102; call as above. | Expected reject the invalid path value (or mark trade invalid); it cannot establish a reliable continuous sampled path. Actual target trade: gross 2.0, fee_R 0.05, net 1.95. NaN was silently ignored because comparisons are false, then later target was accepted. | Validate every timestamp and price before simulation or return an explicit invalid-data outcome that is excluded from resolved results. |
| MED | `MyTradingSys/backtest/sim.py:82-85` | same 100→102 target trade, but `taker=-0.001, maker=0` | Expected invalid fee input rejected. If mechanically applying the stated two-leg fee arithmetic: fee fraction = -0.001; fee_R = -0.001*100/1 = -0.1; net = 2 - (-0.1) = 2.1. Actual returns fee_R -0.1 and net 2.1 as if a rebate were a valid fee regime. | Validate finite nonnegative taker/maker rates at `run` boundary too (direct callers can bypass `fees_dict`). |
| MED | `MyTradingSys/backtest/sim.py:48-87`; `FORMULAS.md:350-361` | Funding-sign case specified by formula: long 100→101, t_in=0, funding records `(8h,.0001),(16h,.0003)`, exit 16h. `run` accepts no funding records or entry/exit funding timestamps. | FORMULAS.md 13 independently gives gross=.01, fee_rt=.0010, slip_rt=.0002, funding charge=.0004, net=.0084. Simulator cannot calculate this contract; it has no funding input and its per-trade result contains no funding term (and does not model `slip_rt`). This is a documented scope gap, not an incorrect sign calculation in code. | Either add explicit funding/slippage inputs for studies governed by section 13, with interval `(t_in,t_out]` and `side_sign` convention, or clearly keep this tool out of that formula's scope. |

## Checked edge classes

- Zero size: not applicable to `fees_dict` or `sim.run`; neither accepts position size. No zero-size claim made.
- Negative risk / zero risk: `geom_ok` rejects equal or incorrectly ordered prices; no observed division-by-zero for finite input. Negative position size is likewise not an argument.
- Fee regime boundary: zero-fee target returned gross 2.0, net 2.0, fee_R 0.0; expected under regime C. Profile-B baseline returned gross 2.0, fee_R .05, net 1.95; independently `.0005*100/1=.05`, matching.
- Rounding: these functions return unrounded floats. The inspected formula sections specify directional price/amount rounding for order construction, not rounding an R-valued research result. No standalone rounding defect established here.
- Short funding sign: FORMULAS.md 13 says short receives positive rates; formula example independently gives net `.01-.0012+.0004=.0092`. `sim.run` has no funding pathway to test that sign.

## Proposed regression tests

`proposed_test_fees_sim.py` contains assertions for the reproductions and intended validation contracts above. These are proposed failing tests for current code, not run in this audit.
