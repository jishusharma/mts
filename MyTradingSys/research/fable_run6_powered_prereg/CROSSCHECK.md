# CROSSCHECK: E2 (4h OHLC) vs the simulator desk (1m replay), Krown S8 4h, BTCUSDT, signals 2022-04-01..2024-06-30 (run 2026-10-28)

**MECHANICS AGREE**

Mechanics proof only: the E2 verdict (INCONCLUSIVE, RESULT.md) is untouched; this says nothing about edge. Brief: CROSSCHECK_BRIEF.md. Code: `crosscheck_desk.py` (tests `test_crosscheck_desk.py`). Both paths use the repo's own S8 detector; E2 = `e2_run.py` functions (signals, stop_for, run_trade, FLOOR), desk = `sim_desk/studies/krown.py run()` via `_bars.collect`. Slice: target 2R, stop 10 bars, time stop 100 bars, desk fee defaults (0.02 % maker, 0.05 % taker, 0.02 % slip). No bar at or after 2024-07-01 was loaded by either path (asserted: last E2 4h bar opens 2024-06-30 20:00, desk 1m bars read 1,313,280, 4h resample 5,472 bars). R and percent only; no prices.

## 1. Signal bars

| item | value |
|---|---|
| E2 detector signals, whole history (2020-01..2024-06, warm-up included) | 277 |
| desk detector signals, whole history (1m-resampled 4h, 2022-01..2024-06) | 134 |
| E2 signals in the slice (signal bar open 2022-04-01..2024-06-30) | 122 |
| desk signals in the slice (same filter) | 122 |
| common | 122 of 122 (100.0 %) |
| E2 only / desk only | 0 / 0 |
| warm-up zone 2022-01-01..2022-03-31 (desk has bars, E2 has 2 more years): E2 / desk / common | 13 / 12 / 12 (E2 only 2022-01-07 00:00) |
| window edge: signal bars 2022-03-31 20:00 (desk would enter 2022-04-01 00:00, E2 would not) | 0 |
| 4h bars whose OHLC differs between the E2 kline file and the 1m resample (of 5,472 common) | 1 (2023-11-10 16:00) |

## 2. Trades joined on (entry bar open time, side)

| item | value |
|---|---|
| E2 trades (slice) | 71 (E2 skipped 51 signals as busy, 0 under the floor) |
| desk trades (slice) | 71 (never filled: 0) |
| matched | 70 (98.6 % of E2, 98.6 % of desk) |
| E2 only / desk only | 1 / 1 |

Unmatched trades, with cause:

| path | entry bar | side | exit kind | why the other path did not trade it | cause (known difference) |
|---|---|---|---|---|---|
| desk only | 2022-07-07 20:00 | long | stop | the other path was still in the trade entered 2022-07-04 12:00 (an exit-bar shift, below) | target-from-close + slippage model (cascade) |
| E2 only | 2022-07-10 16:00 | short | stop | the other path was still in the trade entered 2022-07-07 20:00 (itself unmatched: the cascade) | target-from-close + slippage model (cascade) |

The desk target is 2R of |signal close - stop|, E2's is 2R of |fill - stop| with the fill 0.02 % worse, so the E2 target sits a little further out (mean 0.018 R, max 0.052 R). In 3 trades that is the difference between the target touching in one 4h bar and in a later one; the desk then leaves the trade earlier. In the 2022-07 case that frees the desk for a signal E2 still skipped as busy, and the desk's extra trade then blocks the next E2 trade: one cascade, two unmatched trades. Removing the target-level difference (section 4, row 2) restores 71 of 71 matches.

## 3. Net R per matched trade (desk minus E2)

| item | value |
|---|---|
| mean abs diff | 0.00620 R |
| max abs diff | 0.01984 R |
| mean signed diff | -0.00575 R |
| trades with abs diff > 0.05 R | 0 (each would need a cause from the 8 differences; none to list) |

Five largest differences, all explained by the slippage model (E2 slips the fill price, the desk adds the slip to the fee rate; for target exits the shifted target adds a little more):

| entry bar | side | kind E2 / desk | net R E2 | net R desk | diff | cause |
|---|---|---|---|---|---|---|
| 2023-01-02 04:00 | long | target / target | +1.940 | +1.920 | -0.0198 | slippage model + target-from-close |
| 2023-08-07 16:00 | short | stop / stop | -1.093 | -1.111 | -0.0172 | slippage model |
| 2023-10-16 00:00 | long | target / target | +1.949 | +1.933 | -0.0155 | slippage model + target-from-close |
| 2023-01-09 00:00 | long | target / target | +1.947 | +1.932 | -0.0147 | slippage model + target-from-close |
| 2023-08-14 16:00 | long | stop / stop | -1.066 | -1.079 | -0.0121 | slippage model |

Exits that land in a different 4h bar (matched trades):

| entry bar | side | kind | E2 exit bar | desk exit bar | cause |
|---|---|---|---|---|---|
| 2022-07-04 12:00 | long | target | 2022-07-08 00:00 | 2022-07-07 16:00 | target-from-close + slippage model |
| 2023-02-05 20:00 | short | target | 2023-02-10 20:00 | 2023-02-10 12:00 | target-from-close + slippage model |
| 2024-03-03 20:00 | long | target | 2024-03-04 12:00 | 2024-03-04 08:00 | target-from-close + slippage model |

## 4. One known difference removed at a time (counterfactual runs, nothing in the shared code edited)

| variant | matched | E2 only / desk only | kinds agree | mean abs diff R | max abs diff R | exit-bar shifts |
|---|---|---|---|---|---|---|
| base (as shipped) | 70 / 71 | 1 / 1 | 70 / 70 | 0.00620 | 0.01984 | 3 |
| desk target 2R from the E2 fill | 71 / 71 | 0 / 0 | 71 / 71 | 0.00829 | 0.03351 | 0 |
| slippage 0 in both paths | 71 / 71 | 0 / 0 | 71 / 71 | 0.00010 | 0.00155 | 0 |
| both removed | 71 / 71 | 0 / 0 | 71 / 71 | 0.00000 | 0.00000 | 0 |

With the target level and the slippage placement aligned the two paths agree to rounding (max abs diff 2.2e-16 R): every remaining difference is already counted in the two rows above, so no ninth difference is hiding in the trade mechanics. Row 3 also restores 71 of 71 on its own: the slippage placement moves E2's target level as well, so the cascade is jointly target-from-close and slippage model.

## 5. Exit kinds (matched trades; rows E2, columns desk)

| E2 / desk | stop | target | time |
|---|---|---|---|
| stop | 40 | 0 | 0 |
| target | 0 | 24 | 0 |
| time | 0 | 0 | 6 |

Kind agreement 70 of 70.

## 6. The eight known differences, and whether each bit

| difference | exposure in this slice | outcome |
|---|---|---|
| 1 floor 0.56 % (E2 only) | E2 skipped 0 signals under the floor; desk trades under it 0; narrowest stop 1.16 % | did not bite |
| 2 target from signal close (desk) vs from the fill (E2) | all 70 matched trades; target level differs by mean 0.018 R, max 0.052 R | bit: 3 exits land in an earlier desk bar; one cascade (section 2) |
| 3 1m vs 4h fill (stop gap fills) | 0 E2 stop exits on a gap open | did not bite |
| 4 same-bar stop and target (stop wins vs 1m order) | 0 trades with both levels inside the exit bar | did not bite |
| 5 warm-up (E2 bars from 2020, desk from 2022-01) | 13 E2 / 12 desk signals in 2022-01..03, 12 common | bit before the slice only: signal(s) before 2022-04-01 differ; none inside it, so no trade is affected (both paths start flat at 2022-04-01) |
| 6 window edge (signal-bar time vs entry time) | 0 signal bars straddle 2022-04-01 | did not bite |
| 7 entry-bar rule (target may hit on the entry 4h bar vs first 1m bar off) | 3 E2 trades exit on their entry bar, exit kind agrees on 3 | did not bite |
| 8 slippage model (price vs fee rate) | all 71 trades | explains the 0.0062 R mean gap (section 4) |

## 7. Parameters

| label | parameter | source |
|---|---|---|
| SOURCED | taker 0.05 %, maker 0.02 % (both paths) | MyTradingSys/backtest/fees.py:27-28 |
| SOURCED | detector S8: BBWP basis 7, lookback 100; break above the 50th percentile | krown_params.json bbwp_basis, bbwp_lookback, bbwp_confirm (KR-Q01, KR-Q02) |
| OURS | S8 squeeze level 30 (trader: 25-35) | krown_params.json bbwp_low; unchanged |
| OURS | slippage 0.02 % (E2: on the price; desk: added to the fee rate) | sim_desk/studies/_bars.py SLIP_DEFAULT |
| OURS | stop = far side of the last 10 bars; target 2R; time stop 100 bars | sim_desk/studies/krown.py; e2_run.py |
| OURS | E2 stop floor 0.56 % of the fill | e2_run.py FLOOR; desk has none |
| OURS | slice BTCUSDT, signals 2022-04-01..2024-06-30, nothing at or after 2024-07-01 | CROSSCHECK_BRIEF.md; desk DEV window |
| OURS | a net-R gap counts as a mismatch above 0.05 R | CROSSCHECK_BRIEF.md |

Data note: 1 4h bar (2023-11-10 16:00) has a different open in the 4h kline file than in the 1m cache resample; it is not a signal bar and lies in no E2 trade footprint (stop window, hold, exit bar), so it changed no result above.

**MECHANICS AGREE**
