# Mutation-kill audit of trendline_core.py (card gpt-mutation-trendline-core-1031)

Method (OURS): 20 hand-written single-point mutants applied to an in-memory copy of `trendline_core.py` (harness `scratch/mut.py`, not committed); each run against `test_trendline_core.py` (35 tests, original green) and then `test_trendline_core_spec.py`. Expected values in the new tests are from FORMULAS.md s12 (worked ATR example, lines 331-346), s19.5 (strict penetration L6, line 508) and the definition (c-l)/(h-l); not from the code.

## Result of existing tests (35 tests): 13 killed, 5 survived, 1 equivalent, 1 invalid mutant

| Sev | file:line | Survivor | Why it survived | Fix (done in test_trendline_core_spec.py) |
|---|---|---|---|---|
| MED | trendline_core.py:45 | M2d TR without `abs(l - prev close)` arm | fixtures have no gaps (TR=10 always) | `test_atr_section12_worked_example_uses_gap_term` (2.5 / 2.1667, FORMULAS s12) |
| MED | trendline_core.py:230 | M3c support penetration `<` -> `<=` | no test sits exactly on L - 0.10*ATR_b | `test_penetration_support_boundary...` (FORMULAS 19.5: passes iff low >= L - tol) |
| MED | trendline_core.py:232 | M3d resistance `>` -> `>=` | same, resistance side never at boundary | `test_penetration_resistance_boundary...` |
| LOW | trendline_core.py:64 | M4a close_loc inverted (h-c)/r | `close_loc` field of `broken` event never asserted | `test_close_location_is_close_minus_low_over_range` (0.4 / 1 / 0) |
| LOW | trendline_core.py:64 | M4b close_loc divides by h | same | same test |
| equivalent | trendline_core.py:225 | M3e anchor loop excludes `ib` | at ib the line equals the pivot price (low or close), so no wick/close can be beyond it: no observable difference | none needed |
| equivalent | trendline_core.py:149 | M5b (my mutation was a no-op) | invalid mutant, not a gap | none |

Killed by the existing suite: line_price (M1a, M1b, M1c), atr window/divisor/warmup (M2a, M2b, M2c), PEN_TOL and sign (M3a, M3b), poke tol (M3f), pivot confirm index, right/left window, warmup (M5a, M5c, M5d, M5e). Counts: 20 mutants - 1 invalid (M5b) - 1 equivalent (M3e) = 18 valid, 5 survived (the table's MED/LOW rows), 13 killed.

After the spec file: all 5 survivors killed (M2d, M3c, M3d, M4a, M4b), each test fails on its mutant and passes on the original (`python scratch/mut.py ...test_trendline_core_spec`).

No HIGH findings; no code or spec changes. No source unreachable (NOT_IN_DATA: none). No backtest involved (PRE_REG not applicable).

VERDICT: SOUND