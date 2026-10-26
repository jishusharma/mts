# Pizzino layer SPEC (pz-2), 2026-10-27

Turns `method_extraction.md` (call it ME) into testable rules for pz-3 (indicators) and pz-4 (backtest). No trading verdict: fee-net out-of-sample numbers decide (CLAUDE.md Hard rules). Style follows `MyTradingSys/backtest/layers/FORMULAS.md`: one definition, its source, variants, a hand-worked example. All expected numbers below are computed by hand from the bars printed in each example, never from code.

Labels (CLAUDE.md "Numbers"): **SOURCED** = the trader's words, quote and `ME:line` (the line of the `> "..."` quote in `MyTradingSys/research/pizzino_layer_2026-10-27/method_extraction.md`). **OURS** = our judgement; chosen on DEV, checked once on VALIDATION, holdout read once, every variant listed in the trial ledger (section 9). Never call an OURS value the trader's.

## 0. Conventions

- Bars are closed OHLC bars of one time frame. Index `i = 0..n-1`. A rule at bar `i` uses bars `0..i` only (no look-ahead). Entries fill at the open of bar `i+1`.
- `PH(d)` / `PL(d)`: confirmed pivot high / low of swing degree `d` (section 1). Latest = `PH(d)[-1]`, one before = `PH(d)[-2]`.
- Two features are kept apart and never merged under one name (ME differences table, ME:271): `bar_count` (Jason, section 3) and `swing_state[1..3]` (Michael, section 2).

## 1. Pivot detection (swing degree n)

**Definition.** A degree-n pivot high at bar `i` needs `high[i] > high[j]` for every `j` in `i-n..i-1` and `i+1..i+n` (strict both sides). Pivot low mirrors with `low[i] < low[j]`. It is **confirmed** at the close of bar `i+n` (not before). Pivots are then made **alternating**: two highs in a row keep the higher one, two lows in a row keep the lower one.

- Input: OHLC arrays, `n`. Output: list of `(index, price, confirmed_at)`.
- SOURCED: pivots/swing tops and bottoms exist as the named levels the traders use (ME:184 "pivot point at around $83,000", ME:154 "midpoint of the major prior run", ME:161 "swing bottom ... $75,500"). NOT_IN_DATA: the formula (ME:292). So the fractal rule, its strictness and its alternation are OURS.
- Ambiguity A1: what "1-bar / 2-bar / 3-bar" means as a swing size. Default (OURS): degree `d` uses `n = d`, i.e. n = 1, 2, 3 on the 1-day chart (literal reading of "one-day one-bar, two-bar, three-bar", ME:22, ME:29). Variants in section 9.

**Worked example 1 (n = 2).** Bars (H, L):

| i | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H | 10 | 12 | 14 | 13 | 12 | 11 | 12 | 14 | 16 | 15 | 14 |
| L | 8 | 9 | 11 | 10 | 9 | 7 | 8 | 10 | 12 | 11 | 10 |
| C | 9 | 11 | 13 | 11 | 10 | 8 | 11 | 13 | 15 | 12 | 13 |

- Bar 2: H = 14 is greater than 10, 12 (left) and 13, 12 (right) -> PH, confirmed at the close of bar 4.
- Bar 5: L = 7 is below 10, 9 (left) and 8, 10 (right) -> PL, confirmed at bar 7.
- Bar 8: H = 16 is above 12, 14 (left) and 15, 14 (right) -> PH, confirmed at bar 10.
- No other bar passes: bar 3 (13 < 14), bar 7 (14 < 16), bar 4 low 9 (above 7), bars 0, 1 (too few left bars), bars 9, 10 (too few right bars).
- Expected: `[(2, 14, 4), (5, 7, 7), (8, 16, 10)]`, already alternating H, L, H. For n = 1 the same three pivots result (bar 5 L = 7 < 9 and < 8; bar 8 H = 16 > 14 and > 15; bar 2 H = 14 > 12 and > 13).

## 2. Nested trend states, swing_state[1..3] (Michael)

**Definition.** For each degree `d` in {1, 2, 3}, state at bar `i` (all pivots confirmed by `i`, `c` = close[i]):

- `up (+1)` if `PH[-1] > PH[-2]` and `PL[-1] > PL[-2]` and `c > PL[-1]` (higher high, higher low, close above the last swing low);
- `down (-1)` if `PH[-1] < PH[-2]` and `PL[-1] < PL[-2]` and `c < PH[-1]`;
- otherwise `neutral (0)`. Fewer than two pivots of either kind: neutral.

Derived: `conf = state1 + state2 + state3` (range -3..+3). `conf = +3` or `-3` is **confluence**; anything else is mixed. **Break level** of an `up` state is `PL[-1]` (close below it makes the state neutral); of a `down` state `PH[-1]`. **Lead flag** `lead_up(i)`: state1 became `up` within the last `L` bars while state2 and state3 are not yet `up`.

- Input: pivot lists per degree, close. Output: `state[1..3]`, `conf`, `break_level[1..3]`, `lead_up/lead_down`.
- SOURCED: three states up / down / neutral per nested time frame, 1-bar low-term, 3-bar high-term (ME:36 "up on the one-day one-bar ... down on the mid-term ... neutral on the high-term"); confluence when all agree (ME:22 "confluence across multiple time frames just showing the strong downward bias", ME:29); mixed = no confluence (ME:57); 1-bar turns first and is a precursor (ME:43 "always a precursor", ME:50); the trend flips at a stated price (ME:66 "break of our one-day, one-bar trend, which will happen above around $61,200").
- OURS: the pivot-sequence formula for the state (Gann Swing Pro is proprietary, ME:289), the neutral rule, the close condition, the break level, `conf` as a plain sum, `L`.

**Worked example 2 (states).** Pivots given directly:

| degree | PH[-2] | PH[-1] | PL[-2] | PL[-1] |
|---|---|---|---|---|
| 1 | 12 | 14 | 8 | 10 |
| 2 | 14 | 16 | 7 | 10 |
| 3 | 20 | 16 | 5 | 10 |

- Close = 13. Degree 1: 14 > 12, 10 > 8, 13 > 10 -> up (+1). Degree 2: 16 > 14, 10 > 7, 13 > 10 -> up (+1). Degree 3: PH 16 < 20 (lower high) but PL 10 > 5 (higher low) -> neutral (0). `conf = 1 + 1 + 0 = +2`, mixed, not confluence. Break levels: degree 1 and 2 = 10.
- Close = 9.5. Degree 1: 9.5 > 10 false -> not up; down needs lower high (14 < 12 false) -> neutral. Degree 2: same, neutral. Degree 3 neutral. `conf = 0`.
- Down case, degree 1 pivots PH 14, 12 and PL 9, 7, close 11.5: 12 < 14, 7 < 9, 11.5 < 12 -> down (-1). With close 12.5: 12.5 < 12 false -> neutral (the break above `PH[-1] = 12` flips it, the "61,200" behaviour).

## 3. Bar count from a turning point (Jason)

**Definition.** Let `T` be the latest **significant** confirmed pivot (type decides direction). Starting with the bar after `T`, a bar `k` extends an up-count if `high[k] > high[k-1]` and `low[k] > low[k-1]` (higher high and higher low); a down-count mirrors (lower high, lower low) after a pivot high. `bar_count` = number of consecutive extending bars since `T`; it stops (value kept) at the first bar that does not extend. `three_bar = true` from the bar where `bar_count` reaches 3 (up or down, sign gives direction).

- Significant pivot (OURS): the pivot's price is the lowest low (for a low) / highest high (for a high) of the previous `W` bars before the pivot bar.
- Input: OHLC, pivot list (degree 3 default), `W`. Output: `bar_count` (signed), `three_bar`, `bars_since_T`.
- SOURCED: "three bars up from the low", "higher high, higher low" (ME:82, ME:96); "three in a row from a significant turning point" (ME:82); significant "generally means all-time high, but not always" (ME:89); used on 3-day and weekly bars as well as daily (ME:96, ME:110); small versions are "relatively unconvincing" (ME:103). NOT_IN_DATA: bar-size threshold for "small", any 1-bar or 2-bar count (ME:290).
- OURS: strict (non-inside) HH+HL test, count stops at first break, `W`, degree of `T`, no size filter by default.

**Worked example 3 (count).** Pivot low `T` at bar 0 with H = 10, L = 8 (all lows in the prior `W` bars are >= 8, so significant). Following bars (H, L): bar 1 (11, 9), bar 2 (12, 10), bar 3 (13, 10.5), bar 4 (12.5, 11).

- Bar 1: 11 > 10 and 9 > 8 -> count 1. Bar 2: 12 > 11 and 10 > 9 -> count 2. Bar 3: 13 > 12 and 10.5 > 10 -> count 3, `three_bar = true` at the close of bar 3.
- Bar 4: 12.5 > 13 false -> stop, `bar_count` stays 3 (signal stays fired).
- Failure case: if bar 2 were (12, 9): 9 > 9 false -> `bar_count = 1`, no signal.
- Not significant: if a bar 20 bars earlier had low 7.5 and `W = 50`, `T` (low 8) is not the lowest low -> no count started.

## 4. The 50% line

**Definition.** Take the latest confirmed degree-`dm` pivots `PH[-1]` and `PL[-1]` (after alternation they bound the last completed leg). `mid = (PH[-1] + PL[-1]) / 2`. `half = strong` if `close > mid`, `weak` if `close < mid` (equal: previous value). Bar events at bar `i`:

- `hold_above`: `low <= mid` and `close > mid`; `hold_below`: `high >= mid` and `close < mid` (rejection from underneath);
- `reject_from_below` = `hold_below` while the previous close was below `mid`.

- Input: pivots, OHLC. Output: `mid`, `half`, `hold_above`, `hold_below`, `reject_from_below`.
- SOURCED: midpoint of the prior major run, peak to low (ME:154, ME:133 "Top, bottom, halfway through"); above = strong half, below = weak half (ME:126); rejection off the 50% then a bounce to test it again (ME:147); "held above 50%" = strength (ME:110); change of trend beneath the 50% is the lead for weakness, the swing bottom is the second trigger (ME:161, ME:168); a retest from below that fails is resistance (ME:175).
- OURS: which pivots define "the major run" (`dm = 3` default, section 9), strictness of the touch tests.

**Worked example 4.** (a) From example 1 (n = 2), the last leg is PL 7 -> PH 16: `mid = (16 + 7) / 2 = 11.5`; bar 10 close 13 > 11.5 -> `half = strong`. (b) Illustrative BTC leg top 100,000, bottom 84,000: `mid = (100,000 + 84,000) / 2 = 92,000` (the figure Jason names, ME:133). Bar H 92,500, L 90,000, C 91,000 with previous close 90,500: `high >= mid` and `close < mid` -> `hold_below` and `reject_from_below`. Bar H 93,000, L 91,500, C 92,800: `low <= mid` and `close > mid` -> `hold_above`.

## 5. Level break and retest

**Definition.** A **level** `X` is a pivot price or `mid`. An **up-break** of `X` is confirmed at the bar where `N` consecutive closes are above `X` (the first of them closed above after being below). A **retest** after a confirmed up-break is the first later bar, within `R` bars, with `low <= X * (1 + tol)`. Outcome at that bar: `hold` if `close > X`, `fail` if `close < X`. Down-break and retest mirror (`high >= X * (1 - tol)`, `hold` if `close < X`).

- Input: level `X`, closes/highs/lows. Output: `break_confirmed_at`, `retest_bar`, `outcome`.
- SOURCED: close-beyond confirmation: "higher time frame closes above those pivot points" (ME:73), "consecutive closes above that level and only just a short-term retest" (ME:235); hold = continuation (ME:235); after a breakdown, a retest of the 50 from underneath is weak (ME:214); moving-average breakout then retest pattern (ME:228); retest of support after a break down (ME:242). NOT_IN_DATA: `N`, `tol`, `R` (ME:291).
- OURS: `N = 2`, `tol = 0.5%`, `R = 20` bars, touch-by-wick rule, the hold/fail test on the close.

**Worked example 5.** `X = 63,000` (Michael's pivot, ME:66; the bars are illustrative), `N = 2`, `tol = 0.5%`. Band edge `63,000 * 1.005 = 63,315`.

- Closes 62,800, 63,400 (1st above), 63,800 (2nd above) -> up-break confirmed at the third bar.
- Later bar L 63,200, C 63,900: 63,200 <= 63,315 -> retest; 63,900 > 63,000 -> `hold`.
- A later bar with L 63,200, C 62,900 would be `fail`. A bar with L 63,500 would not touch (63,500 > 63,315).

## 6. Entry, stop, target (defaults, all OURS except where marked)

**Long setup (mirror for short), evaluated at the close of bar `i`:**

1. Level `X` = latest `PH(1)` or `mid` that was up-broken and confirmed (section 5), and a retest at bar `i` has outcome `hold`.
2. `conf >= +2` (section 2) and `half = strong` (section 4).
3. Optional filter (variant, off by default): `three_bar` up within the last `B` bars.
4. Entry: open of bar `i+1`. **Stop** = `PL(1)[-1]` (the last degree-1 swing low). **Target** = nearest confirmed `PH` above the entry price; if none, `entry + 2 * (entry - stop)`. Skip if `reward / risk < RRmin`. **Time stop**: exit at the open after `TS` bars. **Invalidation exit**: close below the stop level (change of trend beneath the pivot).

- SOURCED: the next pivot point as the target (ME:66 "look up to that next pivot point where price is likely going to rally to next ... 63,000"); the swing bottom as breakdown trigger and invalidation = "change in trend beneath $88" (ME:161, ME:205). NOT_IN_DATA: position size, stop distance, order recipe (ME:292).
- OURS: every other number (the whole combination, `conf >= +2`, `RRmin = 1.0`, `TS = 20`, `B = 5`, the 2R fallback target, stop at `PL(1)[-1]`). Fee and slippage are applied in pz-4, not here.

**Worked example 6 (numbers continue example 5).** Retest bar closes 63,900; entry at next open 63,950. Degree-1 `PL[-1] = 62,500`, nearest `PH` above = 66,000.

- Risk = 63,950 - 62,500 = 1,450. Reward = 66,000 - 63,950 = 2,050. `RR = 2,050 / 1,450 = 1.4138` >= 1.0 -> take.
- Without a `PH` above: target = 63,950 + 2 * 1,450 = 66,850.
- If the nearest `PH` were 64,500: reward = 550, `RR = 550 / 1,450 = 0.3793` < 1.0 -> skip.

## 7. Time frame

Default (OURS): daily bars; states use degree 1..3 on the daily chart; the break confirmation of a higher time frame uses weekly closes as an optional filter (variant). SOURCED use of daily, 3-day and weekly bars: ME:96, ME:110; "1-day 1-bar" naming: ME:36; weekly closes: ME:73. Crypto trades 24/7, so the day boundary is 00:00 UTC (OURS).

## 8. Parameter table

| ID | Parameter | Default | Label | Source or ledger id |
|---|---|---|---|---|
| P01 | State set up / down / neutral | 3 states | SOURCED | ME:36 |
| P02 | Number of nested degrees | 3 | SOURCED | ME:22, ME:36 |
| P03 | Confluence = all agree | `abs(conf) = 3` | SOURCED | ME:22, ME:29 |
| P04 | 1-bar leads the others | lead flag exists | SOURCED | ME:43, ME:50 |
| P05 | Bar-count length for the signal | 3 | SOURCED | ME:82 |
| P06 | Count direction test | HH+HL up, LH+LL down | SOURCED | ME:82, ME:96 |
| P07 | Turning point must be significant | yes | SOURCED | ME:82, ME:89 |
| P08 | Bar sizes allowed for the count | D, 3D, W | SOURCED | ME:96, ME:110 |
| P09 | 50% = midpoint of prior major run | (H+L)/2 | SOURCED | ME:154, ME:133 |
| P10 | Above 50% strong, below weak | close vs mid | SOURCED | ME:126 |
| P11 | Pivot as breakout/breakdown level; close-beyond confirms | yes | SOURCED | ME:73, ME:184 |
| P12 | Retest after break is read: hold = continuation, fail = reversal | yes | SOURCED | ME:214, ME:235 |
| P13 | Target = next pivot | nearest PH/PL | SOURCED | ME:66 |
| P14 | Invalidation = change of trend beneath pivot/swing bottom | stop at PL(1) | SOURCED | ME:161, ME:205 |
| P15 | Swing-degree size n per degree | 1, 2, 3 | OURS | V-n |
| P16 | Fractal strictness | strict both sides | OURS | V-frac |
| P17 | Alternation of pivots | keep extreme | OURS | fixed (no variant) |
| P18 | State formula (HH/HL + close vs last swing) | section 2 | OURS | V-state |
| P19 | Lead window `L` | 5 bars | OURS | V-L |
| P20 | Significance window `W` | 50 bars | OURS | V-W |
| P21 | Degree of `T` for the count | 3 | OURS | V-T |
| P22 | Major-run degree `dm` for the 50% line | 3 | OURS | V-dm |
| P23 | Break confirmation `N` consecutive closes | 2 | OURS | V-N |
| P24 | Retest tolerance `tol` | 0.5% | OURS | V-tol |
| P25 | Retest window `R` | 20 bars | OURS | V-R |
| P26 | Entry needs `conf >=` | +2 (short -2) | OURS | V-conf |
| P27 | Minimum reward/risk `RRmin` | 1.0 | OURS | V-RR |
| P28 | Fallback target | entry + 2R | OURS | V-tgt |
| P29 | Time stop `TS` | 20 bars | OURS | V-TS |
| P30 | Count filter `B` (off by default) | off, 5 | OURS | V-B |
| P31 | Day boundary | 00:00 UTC | OURS | fixed |
| P32 | Base time frame | D | OURS | V-tf |

Count: 14 SOURCED (P01-P14), 18 OURS (P15-P32); 16 of the OURS carry a ledger id, 2 are fixed conventions.

## 9. Trial-ledger variants (OURS only)

Protocol per variant: tune on DEV, one VALIDATION check, holdout read once, each row logged in the trial ledger before it is run; fee-net out-of-sample results decide.

| Id | Variants (first = default) |
|---|---|
| V-n | (1,2,3); (2,5,13); (3,8,21); nested time frames D/3D/W with n = 1 |
| V-frac | strict both sides; strict left, non-strict right |
| V-state | section 2; add "inside-bar ignored"; pivot-sequence only (no close condition) |
| V-L | 5; 3; 10 |
| V-W | 50; 20; 100; all-time (whole history) |
| V-T | degree 3; degree 2; degree 1 |
| V-dm | 3; 2; the larger of the last two legs |
| V-N | 2; 1; 3 |
| V-tol | 0.5%; 0.25%; 1.0% |
| V-R | 20; 10; 40 |
| V-conf | +2; +3 (confluence only); +1 |
| V-RR | 1.0; 1.5; 2.0 |
| V-tgt | 2R; 3R; no target (invalidation exit only) |
| V-TS | 20; 10; 40 |
| V-B | off; bar-count signal required; required and `\|conf\| = 3` |
| V-tf | D; 3D; W (weekly-close filter on/off) |

## 10. Ambiguities left (default taken, to be tested)

1. What Gann Swing Pro's 1/2/3-bar swing degrees are (bar sizes, algorithm): NOT_IN_DATA. Default: fractal of n = 1, 2, 3.
2. Whether Jason's "three bars" and Michael's "3-bar" are related: not stated. They stay two features; pz-4 may test them together as a confluence.
3. Which turning points are "significant": window `W` is ours.
4. Retest tolerance and the number of closes: ours.
5. Entry, stop and size: only the target (next pivot) and the invalidation idea are sourced.
6. Both are macro analysts on equities, gold, oil and BTC; every example here uses made-up bars, so nothing is yet shown on BTC data (pz-4).
