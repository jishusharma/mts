# gpt-mutation-tests-sim-desk-conditions — 2026-11-01 (UTC)

**Result: 19 tests from the spec in `MyTradingSys/research/sim_desk/test_conditions_spec.py`, all passing on the current code. 3 of 3 hand mutations are killed.**

Command: `python -m pytest MyTradingSys/research/sim_desk/test_conditions_spec.py -q` -> `19 passed in 0.94s`.

## 1. Conditions and their written rules (the spec used)

| Function / condition | Written rule (SOURCED) | Tests |
|---|---|---|
| `side` | "side both \| long \| short" conditions.py:11 | `test_side_filter` |
| hour window | "UTC hour window [from, to), wraps midnight when from > to; both empty = any hour" conditions.py:12 | `test_hour_window_half_open`, `_wraps_midnight`, `test_hour_to_24_means_end_of_day` |
| `ema_rel` | "off \| above \| below : last closed close vs EMA(ema_len) of ema_tf-minute bars" conditions.py:13 | `test_ema_trend_above_below_and_causal`, `test_ema_above_is_strict`, `test_ema_needs_closed_history` |
| ATR band | "percentile band 0..100 of ATR(atr_len) on atr_tf-minute bars, among the last atr_win bars" conditions.py:14 | `test_atr_percentile_band` |
| `days` | "weekdays allowed, e.g. "mon,tue" or "0,1" (Monday=0, UTC); empty = any" conditions.py:15 | `test_days_filter_utc_calendar`, `test_normalize_all_seven_days_is_any` |
| `layer_b` | "only when study layer_b ... also fired within the last layer_b_bars bars of layer_b_tf minutes before this trade's touch time" conditions.py:16-17 | `test_layer_b_within_n_bars_before_touch` |
| causal | "Features use the last bar closed before the trade's touch time (causal)" DESIGN.md:43; conditions.py:4-5 | `test_ema_trend_above_below_and_causal`, `test_closed_index` |
| `normalize` | "Validated canonical form holding only the ACTIVE conditions (an empty dict = no condition). ValueError on bad input." conditions.py:79 | `test_normalize_*` |
| `label` | "e.g. 'long, UTC 8-16, close above EMA50 of 60m bars'. Empty if none." conditions.py:114 | `test_label_matches_docstring_example` |
| `_closed_index` | "Index of the last bar whose close time (open + tf) is <= touch_t; -1 if none." conditions.py:132 | `test_closed_index` |
| `ema` | "Standard EMA, alpha 2/(length+1), seeded with the first close." conditions.py:137 | `test_ema_formula_by_hand` |
| `atr` | "Simple mean of the last `length` true ranges; NaN until enough bars." conditions.py:148 | `test_atr_simple_mean_nan_until_enough` |
| `apply` | "Subset a study result dict ... all_days stays whole" conditions.py:204 | `test_apply_subsets_trades_keeps_day_universe` |
| combined | conditions filter together (DESIGN.md:43 "filters a study's trades") | `test_conditions_combine_with_and` |

## 2. Expected values worked out by hand (OURS, not taken from the code)

- EMA, length 3: alpha = 2/4 = 0.5. Closes 1,2,3,0 give 1, 1.5, 2.25, 1.125.
- ATR, length 2, on bars (h,l,c) (11,9,10), (12,10,11), (11,7,8), (14,13,13). True ranges are 2, 2, 4, 6, so ATR is NaN, 2, 3, 5. ATR(5) on 4 bars is all NaN.
- Closed index on 5-minute bars opening at 0, 5 and 10 minutes. Touches at 5m-1ms, 5m, 10m-1ms, 10m and 99m give -1, 0, 0, 1, 2.
- Hour window [8,16): 07:59 out, 08:00 in, 15:59 in, 16:00 out. Wrap [22,2): 21:59 out, 22:00/23:30/00:30/01:59 in, 02:00 out. [20,24): 19:59 out, 20:00 and 23:59 in.
- Weekdays come from `datetime.weekday()`: 2026-01-05 Mon, 2026-01-04 Sun, 2026-01-10 Sat, 2026-01-11 Sun.
- EMA trend: rising closes 100..129 put the close above the lagging EMA; a following close of 50 puts it below. A touch inside that last bar must still see 129 (causal). Flat closes put the close equal to the EMA, which is not "above".
- ATR band: ranges that widen every bar put the current ATR at the top of its window (percentile 100). So 90-100 keeps the trade, 0-50 drops it, and [100,100] keeps it. With only 2 bars closed, ATR14 does not exist yet, so the trade is dropped.
- Layer B, 4 x 60m look-back from 12:00: a fire at 11:00 or 08:01 is in. A fire at 07:59, a fire at 12:01 (after the touch) and no fire at all are out.

## 3. Hand mutations (scratch copy in a temp dir; loaded through `MTS_COND_PATH`; conditions.py left as it was)

| # | Mutation (conditions.py line) | Result | Test that failed |
|---|---|---|---|
| M1 | `:170` `(h < t)` -> `(h <= t)` (hour window end included) | **KILLED** (1 failed, 18 passed) | `test_hour_window_half_open` |
| M2 | `:180` `bars[jj, 4] > e[jj]` -> `>=` (EMA "above") | **KILLED** (1 failed, 18 passed) | `test_ema_above_is_strict` |
| M3 | `:199` `keep &= hi > lo` -> `hi >= lo` (layer B with no fire passes) | **KILLED** (1 failed, 18 passed) | `test_layer_b_within_n_bars_before_touch` |

At first M2 **survived**: the first 18 tests never had a close exactly equal to its EMA. I added `test_ema_above_is_strict` (flat series) and M2 is now killed. These tests are new and cover code that already exists. The "fail on old code first" check is therefore met by the mutants: each of M1-M3 fails these tests.

Script used (scratch, not committed). For each mutation it replaces one exact string in a temp copy and runs pytest with `MTS_COND_PATH=<copy>`. At the end it asserts that the original file is unchanged ("original conditions.py untouched" was printed).

## Findings

- F1: the `label` docstring example says `'long, UTC 8-16, ...'` (conditions.py:114), but the code writes `'long only'` (conditions.py:117). The docs and code differ, but only in wording. The test checks `startswith('long')` and does not lock in either form.
- F2: the docstring does not say how a close **equal** to the EMA counts for `below`. The code treats it as below (`~above`, conditions.py:181). I left this untested on purpose because the spec is silent.
- F3: the docstring does not say whether the layer B window edges are inclusive (a fire exactly `span` before the touch, or at the touch). Only clear inside and outside cases are tested.
- F4: the sign convention long=+1 / short=-1 for `side` is not written in conditions.py:11 or DESIGN.md:43. The test uses it as an OURS assumption.
