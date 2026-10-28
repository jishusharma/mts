# Cross-check brief: E2 (Krown S8 4h) vs the simulator desk Krown study (card krown-s8-e2-desk-crosscheck)

Operator go 2026-10-28 ("Yes, run it", OPERATOR_DECISIONS.md d-krown-s8-e2-desk-crosscheck-go). Mechanics proof only: E2 stays INCONCLUSIVE whatever this finds. No change to e2_run.py numbers, PRE_REG.md, RESULT.md, the Krown detector code or its params.

## Two code paths
| | E2 `e2_run.py` (this folder) | desk `sim_desk/studies/krown.py` + `_bars.collect` |
|---|---|---|
| detector | `backtest/layers/krown/krown_events.setup_s8` | the same function |
| bars | 4h OHLC klines, `F:/MTS/data/fable_run6_klines/` | 1m bars (desk cache on JIS-DESKTOP) resampled to 4h for signals; trades replayed on 1m |
| entry | market at the next 4h open, taker 0.05 % + 0.02 % slip | market at the first 1m bar after the signal bar closes, same fees |
| stop | far side of the last 10 bars incl. the signal bar, floor 0.56 % of the fill | same 10 bars, no floor |
| target | 2R from the fill, maker 0.02 % | 2 x risk from the signal close, maker |
| time stop | 100 bars | 100 bars |
| busy rule | one position per symbol | one position (`busy_until`) |
| same-bar stop and target | stop wins | 1m order decides |
| warm-up | bars from 2020 | 1m bars from 2022-01 (`_bars.WARMUP_FROM`): early-2022 signals may differ |
| window edge | filtered by signal-bar time | filtered by entry time (`ref[1]`): one signal at 2022-04-01 may differ |
| entry bar | target may hit on the entry 4h bar; stop fills at the stop level | target off on the first 1m bar only; stop fills at the open on a gap |
| slippage | applied to the price | added to the taker fee rate on notional (`collect`): small R drift even on matched trades |

(Rows 5-8 from the Lab_Guy review 2026-10-28; every one is a known difference the cause list in CROSSCHECK.md may cite.)

## Slice
BTCUSDT only, S8, 4h, signals 2022-04-01..2024-06-30 (the desk window), target_r 2.0, desk fee defaults. Nothing at or after 2024-07-01 may be loaded by either path (assert).

## What to compare
1. Signal bars: E2 set vs desk set, count common; any difference listed with the bar and the reason (should be 100 % common: same function, same OHLC after resample).
2. Trades joined on (entry bar open time, side): matched count and %.
3. Net R per matched trade: mean and max |E2 - desk|; every trade with |diff| > 0.05 R listed with its cause: floor, target-from-close, 1m-vs-4h fill, same-bar rule, warm-up, window edge, entry-bar rule, slippage model.
4. Exit kind agreement (stop / target / time).

## Output: `CROSSCHECK.md` (this folder)
Tables for 1-4, a parameters table (SOURCED / OURS), and one bold line: **MECHANICS AGREE** (every mismatch explained by the known differences above) or **MECHANICS DISAGREE: <reason>**. Plus one `sim_desk/results/krown-s8-e2-desk-crosscheck.json` row (kind audit, `parity` field with entries_match / exits_match) so the simulator page lists it; percent and R only, no prices.

## Tests, fail-first (`test_crosscheck_desk.py`)
1. The diff function flags a planted trade whose net R differs by 0.2 R and whose exit kind differs; an identical list passes.
2. The signal-set comparison on two hand-made bar series (one with an extra signal) reports the extra bar.
3. Both loaders refuse bars >= 2024-07-01.
All three fail before `crosscheck_desk.py` exists.

## If the desk 1m cache is missing months
Write `BLOCKED.md` here with the exact missing months and stop; do not fetch 1m data in this card.
