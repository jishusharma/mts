# FIX-FIRST

## What was checked

- `MyTradingSys/backtest/layers/FORMULAS.md` (the file has no Pizzino entry; its opening scope at lines 3–8 lists RSI, timeframe, CryptoCred, runner and metrics).
- `MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py:18-182` (all implemented calculations).
- `MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md:13-120` (the layer's actual formula definitions and worked examples).
- Command: Python loaded `pizzino_indicators.py` directly and evaluated the 10-bar series below.

Toy input (bar indices 0–9):

| i | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| H | 10 | 12 | 14 | 13 | 12 | 11 | 12 | 14 | 16 | 15 |
| L | 8 | 9 | 11 | 10 | 9 | 7 | 8 | 10 | 12 | 11 |
| C | 9 | 11 | 13 | 11 | 10 | 8 | 11 | 13 | 15 | 12 |

## Findings

| Severity | Formula / source | FORMULAS.md | Code and evidence | Independent hand result | Code result | Status |
|---|---|---|---|---|---|---|
| HIGH | Strict degree-1 fractal pivots, alternated; SPEC `:15`, worked example `:21-33` | NOT_IN_DATA: no Pizzino formula in FORMULAS.md (scope at `:3-8`) | `pizzino_indicators.py:18-43`; output `[(2,14,3,H),(5,7,6,L),(8,16,9,H)]` | Bar 2 high 14 exceeds neighbors 10/12 and 13/12, confirmed 3; bar 5 low 7 is below 12/11 and 12/8, confirmed 6; bar 8 high 16 exceeds 12/14 and 15, confirmed 9. Sequence alternates H/L/H. | Same three pivots, same confirmation indices. | SAME vs SPEC; NOT_IN_DATA in FORMULAS.md |
| HIGH | Consecutive HH+HL count after low; SPEC `:63-75` | NOT_IN_DATA: no Pizzino formula in FORMULAS.md (`:3-8`) | `pizzino_indicators.py:96-113`; called with `t=5, kind='L'`; output `[0,1,2,3,3]` | Start at bar 5. Bar 6: HH and HL => 1; bar 7 => 2; bar 8 => 3; bar 9 high 15 is below 16, so extension stops and count stays 3. | `[0,1,2,3,3]` | SAME vs SPEC; NOT_IN_DATA in FORMULAS.md |
| HIGH | 50% midpoint and half state; SPEC `:79-88` | NOT_IN_DATA: no Pizzino formula in FORMULAS.md (`:3-8`) | `pizzino_indicators.py:117-127`; `mid_line(16,7)`, then `half_state(C[9], mid, 'weak')`; output `11.5`, `strong` | Midpoint `(16+7)/2=11.5`; bar 9 close 12 > 11.5, therefore strong. | `11.5`, `strong` | SAME vs SPEC; NOT_IN_DATA in FORMULAS.md |

## Coverage / verdict

The implementation also defines nested swing state and confluence (`pizzino_indicators.py:52-69`), lead flag (`:72-83`), significance and count (`:87-113`), half-line events (`:130-138`), break/retest (`:141-162`), and trade risk/reward (`:165-182`). Their matching definitions are in `SPEC.md:35-47`, `:63-68`, `:79-86`, `:90-96`, and `:104-120`. None is documented in `FORMULAS.md`; its stated purpose/scope at lines 3–8 does not include Pizzino. The three sampled calculations match the Pizzino SPEC by hand, but the requested canonical FORMULAS.md definitions are absent.

**Verdict: FIX-FIRST** — add the Pizzino formulas (or explicitly extend the canonical formula source) before treating `FORMULAS.md` as covering this layer. No code was changed.
