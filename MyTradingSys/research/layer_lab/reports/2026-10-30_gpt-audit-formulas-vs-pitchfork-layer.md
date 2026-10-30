# Pitchfork formula audit

Verdict: FIX-FIRST — FORMULAS.md has generic straight-line/log-line equations, but does not define the pitchfork midpoint, tine offsets, variant shifts, or channel rules implemented by `pitchfork_detector.py`. The three geometric outputs below agree with code; formula-to-source completeness is NOT_IN_DATA for the pitchfork-specific construction.

## Checked

- `MyTradingSys/backtest/layers/FORMULAS.md:492-514` (section 19, trend-line contract formulas).
- `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:66-161,232-272,300-` (variant geometry, median/tine values, log wrapper, pivot and scan functions).
- Toy execution: `python -c "from MyTradingSys.backtest.layers.pitchfork.pitchfork_detector import *; p0=PitchforkPivot(0,100,False); p1=PitchforkPivot(4,140,True); p2=PitchforkPivot(8,120,False); f=PitchforkChannel(p0,p1,p2); print(f.slope, f.get_ml(9), f.get_uml(9), f.get_lml(9), f.get_upper_warning_line(9), f.get_lower_quarter_line(9))"` -> `5.0 145.0 165.0 125.0 185.0 135.0`.
- No market data used; synthetic 10-bar example only. The channel is instantiated from explicit pivots, so zigzag pivot selection is outside these three value checks.

## Formula inventory and comparison

Toy 10-bar OHLC series (index: O,H,L,C): 0:(100,102,98,100), 1:(105,110,102,108), 2:(115,120,110,118), 3:(125,130,120,128), 4:(135,140,132,138), 5:(130,132,125,127), 6:(122,128,115,120), 7:(118,124,110,115), 8:(115,122,110,120), 9:(121,125,118,123). Use explicit anchors P0=(0,100), P1=(4,140), P2=(8,120), STANDARD variant; query t=9.

For hand calculation, apply the code's documented-in-comments construction: midpoint M=((4+8)/2,(140+120)/2)=(6,130); slope=(130-100)/(6-0)=5. At t=9, ML=100+5*(9-0)=145. ML at P1 time 4 is 120, so P1 tine offset=140-120=+20. ML at P2 time 8 is 140, so P2 tine offset=120-140=-20. Thus UML=165 and LML=125 at t=9. FORMULAS.md 19.2's line equation is the shared linear-line form; it does not state the midpoint-and-parallel-tines construction.

| Severity | Formula / evidence | FORMULAS.md | Code lines | Hand value vs code | Result; issue / proposed fix |
|---|---|---|---|---|---|
| MED | Pitchfork median line from anchor P0 to midpoint of P1/P2 | 19.2 `L(t) = pa + (pb-pa)*(t-ia)/(ib-ia)` at 499-500 supplies only a generic line; midpoint rule is NOT_IN_DATA | `pitchfork_detector.py:81-91,131-133` | M=(6,130); slope=5; ML(9)=145 vs 145.0 | NOT_IN_DATA for formula coverage; numeric implementation agrees with hand. Add explicit pitchfork midpoint definition to FORMULAS.md. |
| MED | Upper tine: parallel to ML through P1; offset | No pitchfork tine formula in section 19; NOT_IN_DATA | `pitchfork_detector.py:93-118,135-137` | ML(4)=120; P1 offset +20; UML(9)=165 vs 165.0 | NOT_IN_DATA for formula coverage; numeric implementation agrees with hand. Document offset and upper/lower ordering. |
| MED | Lower tine: parallel to ML through P2; offset | No pitchfork tine formula in section 19; NOT_IN_DATA | `pitchfork_detector.py:93-121,139-141` | ML(8)=140; P2 offset -20; LML(9)=125 vs 125.0 | NOT_IN_DATA for formula coverage; numeric implementation agrees with hand. Document offset and variant conventions. |
| LOW | Schiff / Modified Schiff effective P0 | No such definition in section 19; NOT_IN_DATA | `pitchfork_detector.py:66-79` | Standard variant used in this toy; not exercised | NOT_IN_DATA; add separate explicit formulas if these variants are intended to be audited. |
| LOW | Log-scale transform (log prices, linear geometry, exponentiate levels) | 19.2 includes a log line through two anchors (499-500), but no three-anchor log-pitchfork rule; NOT_IN_DATA | `pitchfork_detector.py:232-272` | Not exercised in this toy | NOT_IN_DATA; document whether log-pitchfork geometry means log-transform all three anchors and channel offsets. |
| LOW | Pivot detector, reach/breach/Hagopian and warning/quartile outputs | Section 19 defines separate strict trend-line pivots, contact rules, and arm rules (496-514); it does not cover pitchfork zigzag, reach/Hagopian, or warning/quartile logic | `pitchfork_detector.py:143-229,300-` | Not part of three requested geometric values | NOT_IN_DATA; these are layer behaviors without corresponding pitchfork definitions in the cited formula section. |

## Conclusion

The three requested outputs are SAME against an independent hand calculation of the code's stated geometry. The audit is FIX-FIRST on traceability: FORMULAS.md section 19 is for ordinary anchored trend lines and is not a complete formula source for this pitchfork layer. No code changes made.

Follow-up cards created: none.
