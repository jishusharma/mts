# MTS testnet watch list (BTCUSDT, patterns active now)

Phase-first (d-phase-first-method-1106): these patterns are valid in the current market phase; each goes to testnet when its trigger fires and runs until it fails. No backtest was run for this list. Built by `detect_patterns.py` on closed bars: 1h to 2026-11-06 18:00Z, 4h to 11-06 12:00Z, 1d to 11-05, 1w to 10-26 (the forming bar of each is excluded). Price at the time: about 75,800. Drawings: `charts/`, numbers below are the detector's (OURS) and wait for the operator's eye check. Base rates are Bulkowski, US stocks, bull market (PATTERN_BOOK.md s1); they are the starting belief, not a BTC result. "Stop by plan" = just beyond the pattern's invalidation point; the stop distance times the leverage must stay well under 100 % of margin, so the leverage cap is written next to every rule. No fixed 0.15 % floor anywhere.

## The map in one line
Every 4h/1h structure sits between two lines: **75,400 (floor)** and **80,900 (ceiling)**. A close outside either one is the trigger for four of the five rows below. The weekly and daily patterns disagree on direction (weekly bullish, daily bearish), so the range break decides which one gets tested first.

## Decision rows

| # | Pattern, timeframe | State now | Trigger (close) | Target (full height) | Invalidation | Published base rate (Bulkowski, bull mkt) | Testnet rule (cotrade.py place; size `--amount` is the operator's) |
|---|---|---|---|---|---|---|---|
| 1 | **Rectangle** 4h (also 1h x6), 4 touches, since 10-29 | forming, price 0.5 % above the floor | up: close > 80,932; down: close < 75,398 | up 86,440; down 69,886 (height 5,508) | up-trade: back below 75,398 (7 % below the trigger); down-trade: back above 80,990 | Rectangle: up-break fails 15 %, avg +48-51 %, meets 78-79 %; down-break fails 24-34 %, avg -13 to -16 %, meets 54-55 %; throwback 64-66 % | **Long:** `place --side buy --type market --stop 75300` after a 4h close > 80,932. **Short:** `place --side sell --type market --stop 80990` after a 4h close < 75,398. Both stops are about 7 % away: **leverage cap 5x** |
| 2 | **Channel down** 4h (10-15 to 11-04), 5 touches | forming; same levels as row 1 | up: close > 80,674 (upper line); down: close < 75,231 | up 87,477; down 68,428 (height 6,802) | the opposite line | NOT FOUND: Bulkowski has no channel statistics; his only rule is "close outside adversely = exit" | No separate order: it confirms row 1. A break below 75,231 is the stronger short (target 68,428) |
| 3 | **Head and shoulders top** 1d (head 87,396 on 09-21), confirmed 10-24 | neckline (about 83,400 today) already broken; price 8 % below it; likely in its pullback window (68 % pullback rate) | already confirmed; add on a daily close < 75,398 (new low after the pullback) | 69,824 (full head-to-neckline height); Bulkowski scales the height by the 51 % hit rate: 81,309 (neckline at the break) - 0.51 x 11,485 = about 75,450, **where price already is**: most of the typical reach is used, the full 69,824 needs a continuation | head 87,396; **stop by plan above the right shoulder 84,898** (12 % away) | fails 19 %, avg -16 % (breakout to ultimate low), pullback 68 %, meets target 51 %; busted H&S tops rise 35 % on average | **Short:** same order as row 1 short, stop `84900` (12 %: **leverage cap 3x**), or the tighter 80,990 at 5x, which accepts a pattern that is not fully invalidated. Target zone 69,800-69,900 is shared with row 1: two patterns agree |
| 4 | **Double bottom** 1w (60,000 on 02-06 / 57,800 on 07-01), neckline 82,850, confirmed in Sep | price 8.5 % below the neckline: the throwback went through it (the 35 % branch: after a throwback reaches the breakout price, 35 % keep falling below the pattern) | long: daily close > 82,850 (neckline reclaimed) | 107,900 full height (25,050); Bulkowski scales by 69.8 %, so about 100,300 | **stop by plan below 57,800** (24 % away); Bible break: weekly close < 60,000 | fails 13.2 %, avg +43 %, throwback 66.5 %, meets 69.8 % (DERIVED from the four Adam/Eve variants) | **Long:** `place --side buy --type market --stop 57700` after a daily close > 82,850. **Leverage cap 2x** at that stop |
| 5 | **Falling wedge** 4h (10-15 to 11-04) | broke up on 11-04 at 79,901, price now 5 % under it: a failed break in progress | no long. Watch a 4h close < 75,635 (wedge floor): that is the bust | if it busts: bearish, rows 1 and 3 targets | 79,901 reclaimed | falling wedge up-break fails 26 %, meets 62 %; 31 % of up-breaks bust (BustPerformance) | none: information for rows 1 and 3 |
| 6 | **Descending triangle** 4h (10-29 to 11-04) | broke UP on 11-04 against its bearish bias, price back inside | none (a bust: 28 % of up-breaks) | 82,439 if it resumes | 75,714 | up-break fails 22 %, meets 64 %; down-break fails 23 %, meets 50 % | none: information |

## Trendlines active now (strip rule: last 3 same-side swing pivots within 0.2 % of one line; slope = log %/bar; distance = price vs line)

| TF | Support | Resistance |
|---|---|---|
| 1h | 3 touches, 74,709, -0.080 %/bar, price 1.4 % above | 3 touches, 79,922, -0.031 %/bar, price 5.4 % below |
| 4h | 3 touches, 75,084, -0.042 %/bar, price 1.0 % above | 3 touches, 83,569, +0.041 %/bar, price 10.2 % below |
| 1d | none (no live line) | 3 touches, 81,009, -0.169 %/bar, price 6.5 % below |
| 1w | none | 2 touches only, 101,337, price 29 % below (weak) |

The 1d resistance (81,009) and the 1h/4h ceiling (80,922-80,932) are the same level: a 1d close above about 81,000 would break the daily down-trend line and the 4h rectangle together.

## How a row leaves the list
- Trigger fires: place the testnet order by the row's rule; the row becomes "running".
- Invalidation printed in the row is hit by a close: the pattern failed; close the trade and note the failure (a failed pattern is data: busted patterns move further the other way in Bulkowski's study, Busted.html).
- Target reached or the pattern expires (3x its width without a break): remove.

## Caveats the operator should hold
- The detector sees a swing only after it has been confirmed by a retrace, so the newest turn is always one swing late.
- Row 3 and row 4 are opposite calls; run neither as a standing position until the row 1 break shows which side the market picks.
- Bulkowski's averages run from the breakout to the ultimate high or low, so they are best-case reach, not expected return; the "meets target" column is the honest expectation.
- BTC's own test of candle patterns found nothing after costs (PATTERN_BOOK.md s2); this list uses chart-pattern geometry, whose BTC base rates are not yet measured: the testnet run is the measurement.
