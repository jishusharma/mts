# Mutation-kill audit: pizzino_indicators.py (card gpt-mutation-pizzino-indicators-1031)

Date 2026-11-01 (UTC). Scope: `MyTradingSys/backtest/layers/pizzino/pizzino_indicators.py` (182 lines), `test_pizzino_indicators.py` (32 tests), `MyTradingSys/backtest/layers/FORMULAS.md`, and the source they cite, `MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md` (sections 1-6) -> `method_extraction.md` (ME). No code and no spec changed. No backtest is involved, so the 12 items of `PRE_REG_TEMPLATE.md` do not apply (N/A).

**Verdict: SOUND.** The code matches the SPEC rule text in all six sections, and there are no HIGH findings. The old suite killed 7 of 24 hand mutants. The new `test_pizzino_spec.py` (16 tests) kills the other 17, so the two suites together kill 24/24. Every new test fails on exactly one mutant and passes on the original.

## Method

- Mutants are one-token text replacements in a scratch copy of the source. They are exec'd in memory into the module object, so the real file is never written. Runner: `scratch/mutate.py` (session scratch dir), started from the repo root. The 24 mutated sources are kept next to it in `scratch/mutants/MNN.py`.
- Expected values in the new tests come by hand from the SPEC rule text (each test cites `SPEC.md:line`). None was copied from the code. The bars are made up (OURS). `X = 100, tol = 0.25` is chosen so that the band edges 125 and 75 are exact floats.
- Checked: `python -m unittest MyTradingSys.backtest.layers.pizzino.test_pizzino_indicators MyTradingSys.backtest.layers.pizzino.test_pizzino_spec` -> `Ran 48 tests ... OK`.

## Mutation table (runner output, 2026-11-01)

| id | line | mutation | old suite | new suite (killing test) |
|---|---|---|---|---|
| M01 | :22 | `high[i] > high[j]` -> `>=` | KILLED test_strict_both_sides | survived |
| M02 | :24 | `low[i] < low[j]` -> `<=` | **SURVIVED** | test_equal_lows_are_not_strict_pivot_lows |
| M03 | :33 | keep higher high -> keep lower | KILLED test_two_highs_keep_higher | survived |
| M04 | :33 | keep lower low -> keep higher | **SURVIVED** | test_two_lows_keep_lower |
| M05 | :62 | down `close < ph[-1]` -> `<=` | **SURVIVED** | test_down_close_equal_to_last_ph_is_neutral |
| M06 | :60 | up `close > pl[-1]` -> `>=` | **SURVIVED** | test_up_close_equal_to_last_pl_is_neutral |
| M07 | :75 | `for sign in (1, -1)` -> `(1,)` (no lead_down) | **SURVIVED** | test_lead_down_mirror |
| M08 | :81 | `i - j < L` -> `<=` | **SURVIVED** | test_lead_window_last_L_bars |
| M09 | :81 | `j > 0` -> `j >= 0` | **SURVIVED** | test_no_observed_turn_no_lead |
| M10 | :90 | window `idx - W` -> `idx - W + 1` | **SURVIVED** | test_significance_window_is_W_bars |
| M11 | :107 | down count `low[k] < low[k-1]` -> `<=` | **SURVIVED** | test_down_count_needs_strict_lower_low |
| M12 | :131 | hold_above `low <= mid` -> `<` | **SURVIVED** | test_hold_above_touch_at_mid |
| M13 | :132 | hold_below `high >= mid` -> `>` | **SURVIVED** | test_hold_below_touch_at_mid |
| M14 | :136 | drop `and prev_close < mid` | **SURVIVED** | test_reject_needs_previous_close_below |
| M15 | :150 | drop `and not beyond(closes[i - N])` | **SURVIVED** | test_break_needs_a_close_below_first |
| M16 | :156 | window `c + R + 1` -> `c + R` | **SURVIVED** | test_retest_on_the_Rth_bar_counts |
| M17 | :157 | up touch `<=` -> `<` | **SURVIVED** | test_up_retest_touch_at_band_edge |
| M18 | :157 | down touch `>=` -> `>` | **SURVIVED** | test_down_retest_touch_at_band_edge |
| M19 | :118 | mid `/ 2` -> `/ 3` | KILLED test_example4a, 4b | survived |
| M20 | :179 | `risk <= 0` -> `< 0` | KILLED test_bad_stop_not_taken | survived |
| M21 | :182 | `rr >= rr_min` -> `>` | KILLED test_short_mirror | survived |
| M22 | :177 | short target `max` -> `min` | KILLED test_short_mirror | survived |
| M23 | :23 | `confirmed_at = i + n` -> `i` | KILLED test_causal_view, example1 x2 | survived |
| M24 | :106 | up count `low[k] > low[k-1]` -> `>=` | KILLED test_failure_case | survived |

The card's minimum of 5 mutants is met with 24. The old suite killed 7 and missed 17. The pattern is clear: the old suite tests the SPEC worked examples, which test the "up" side and interior values. It never tests an equality boundary or the "down" mirror of a rule it has already tested on the up side.

## Findings

| sev | file:line | what is wrong | evidence | proposed fix |
|---|---|---|---|---|
| MED | `test_pizzino_indicators.py` (whole file) | 17/24 one-token mutants survive. Equality boundaries and down mirrors are untested. | Mutation table above (runner output). | **Done in this commit**: `test_pizzino_spec.py`, 16 tests, 17/17 killed. |
| MED | `FORMULAS.md` (no section) | FORMULAS.md has no Pizzino section, so the CLAUDE.md rule "expected numbers come from FORMULAS.md" cannot be met for this layer. SPEC.md is the only formula source. | `Select-String FORMULAS.md -Pattern pizzino` -> 0 hits. Headers run s1-s29, none Pizzino. | Add a FORMULAS.md section that points to SPEC.md sections 1-6 (a spec change, so out of scope here). |
| LOW | `SPEC.md:43` vs `pizzino_indicators.py:81` | The SPEC says "within the last L bars" but does not define the boundary. The code counts a turn only if the turn bar is in `i-L+1..i`. | Code `i - j < L`. Pinned by test_lead_window_last_L_bars (reading labelled OURS). | One sentence in SPEC s2: the turn bar must be in `i-L+1..i`. |
| LOW | `SPEC.md:92` vs `:156` | The SPEC says "within R bars" but does not define the boundary. The code includes bar `c + R`. | `range(c + 1, c + R + 1)`. Pinned by test_retest_on_the_Rth_bar_counts (OURS). | State in SPEC s5 that bar `c + R` is included. |
| LOW | `SPEC.md:92` vs `:160` | The SPEC gives `hold` for close > X and `fail` for close < X, but says nothing about close == X. The code returns `fail` there. | `"hold" if beyond(closes[j]) else "fail"`. | Decide and state it in the SPEC (`fail` is the conservative choice). |
| LOW | `:149-152` vs `SPEC.md:108` | `break_retest` returns only the first break and its first retest. SPEC s6 wants the *latest* broken level with a hold retest at bar i. A pz-4 caller must slice `closes` to see a later break. | `break` after the first confirmed index. | Document the slicing in the docstring, or add a `start` argument (code change, a later card). |
| LOW | `SPEC.md:66` vs `:96-113` | The SPEC lists `three_bar` and `bars_since_T` as outputs. The module has no function for them; they exist only as the docstring formula `abs(count) >= 3`. | Docstring `:100`. | Leave to pz-4, or add a two-line helper with a test. |
| LOW | `:92`, `:90` | `is_significant` counts a tie with an earlier low as significant (`<=`). With `idx < W` it uses a shorter window. SPEC s3 ("the lowest low", `SPEC.md:65`) says nothing about ties or the early-history case. | `all(series[idx] <= x ...)`, `max(0, idx - W)`. | State both conventions in SPEC s3. |
| LOW | `:22-25` | On an outside bar that is both a pivot high and a pivot low, H is appended before L, which decides what alternation keeps. The SPEC does not say. | Order of the two `if` blocks. | State the convention in SPEC s1. |

## Source checks (SOURCED parameters cited by the code docstring `:8-10`)

The quotes below were read at the cited lines of `method_extraction.md`. All of them match SPEC section 8:

- P05/P06, 3 bars, HH+HL: ME:82 "Three bars up from the low", ME:96 "higher high, higher low".
- P07, significant turning point: ME:89 "significant generally means all-time high, but not always".
- P09, 50% line: ME:133 "Top, bottom, halfway through that gives you $92,000" (SPEC example 4b uses 92,000).
- P13, next-pivot target: ME:66.
- P11, closes beyond the level: ME:73, ME:235.
- The pivot formula, the state formula, N, tol, R and W are NOT_IN_DATA in the transcript (ME:289-292). The SPEC and the code docstring correctly label them OURS.

All other numbers in the new tests are OURS (made-up bars and the parameter values listed in each test docstring).

No HIGH findings, so no follow-up cards (card step 5).
