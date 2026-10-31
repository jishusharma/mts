# PRE_REG: Krown free setups, DEV check (card krown-free-setups-dev-check)

Written and frozen BEFORE any run or outcome read. The script `silver_cross_dev.py` refuses to run unless the last line of this file is `FROZEN_UTC: ...`, and writes this file's sha256 into its result CSV. Operator decisions 90-92 (stream A/B funnel). Template: backtest/PRE_REG_TEMPLATE.md.

## 1. Triage of KROWN_FREE_SETUPS.md (rule: entry + exit quotable with a verified quote, and BTC 1m on this machine can test it)

The app was unreachable (KROWN_APP_PROBE.md), so only the YouTube-caption rows count.

| Setup | Verdict | Reason / missing part |
|---|---|---|
| Silver Cross 1-month (bXug2l6qICc 00:03:08) | TESTABLE | entry = the cross (quote 00:00:44), exit = "one month out" (quote 00:03:08), claim "83 % of the time it is green" |
| Silver Cross 1-year (bXug2l6qICc 00:02:40) | NOT_TESTABLE on DEV | exit 1 year after a cross; every DEV-window cross exits after 2024-06-30, i.e. in VALIDATION/HOLDOUT, which this card may not read |
| Free AI Bot (OR3Q2Vf1lrM) | NOT_TESTABLE | "Range deviation indicator prints a blue/red signal" is a proprietary indicator; no formula in the file (NOT_IN_DATA). The stop (2x ATR14) and the bar timing are quotable, the entry and exit state are not computable. The file's "3x chandelier" has no quote |
| 10-Day Reconnect + Stoch > 80 (ro6tMlqbbBI) | NOT_TESTABLE | "reconnect with the 5 EMA" has no rule (touch? close back above? gap size?); stochastic lengths/smoothing NOT_IN_DATA; stop NOT_IN_DATA; about 80 ten-day bars in DEV |
| 10-Day Reconnect alone, 2-Day Bounce (zay_owGmjo0, LMRNBdMiQ2g) | NOT_TESTABLE | same undefined "reconnect" / "test of the 55 EMA"; hold = "10 days out" with no entry bar rule |
| 5/21, 13/34 corrective, 2-Day Corrective (dLq5Jyir3Iw, zay_owGmjo0) | NOT_TESTABLE | trigger direction and "corrective" condition not defined, stop NOT_IN_DATA, target "generally/minimum" 55 or 89 EMA with no time bound, claimed hit-rate NOT_IN_DATA (nothing to compare) |

Template items 0a-0g: 0a/0b see section 6; 0c record: Krown gives no dated trade list, only "since 2018" aggregates, so this is a hypothesis, never a core; 0d data: BTC 1m holds every input (close prices); 0g: not the operator's own idea; the encoding below is Krown's quote plus OURS gaps, labelled.

## 2. Event and outcome (one setup, one cell)

| Item | Value | Label |
|---|---|---|
| Market / bars | BTCUSDT klines 1m, F:/MTS/data/tom_raw/klines, resampled to complete UTC daily bars (1440 minutes) | OURS (his chart TF is "multi-day/daily") |
| Silver cross | daily EMA(21) crosses above EMA(55): diff(t-1) <= 0 and diff(t) > 0 on the daily close (diff = EMA21 - EMA55) | EMA lengths 21 and 55 SOURCED (bXug2l6qICc 00:00:44); alpha 2/(n+1), seeded with the first DEV daily close, OURS |
| Entry | open of the daily bar after the cross-day close (no same-bar fill) | OURS (look-ahead safe reading of "at cross") |
| Exit | open of the daily bar 30 calendar days after the entry bar | "one month" SOURCED (00:03:08); 30 days OURS |
| Stop | none (he gives none) | SOURCED absence |
| Outcome | net return = exit_open/entry_open - 1 - fee RT; hit = net return > 0 ("green") | fee SOURCED fees.py; "green" read as net > 0 is OURS (his is probably gross, so net is stricter) |
| Mean R | net return / risk unit; risk unit = 2 x ATR(14 daily, EMA alpha 1/14) / entry open; no stop applied, scale only | OURS; no stop exists so R is a scaling, not a risked R. The primary number is mean net return % |
| Costs | fee = 2 x fees.BINANCE_TAKER (0.10 % round trip, all-taker), imported from backtest/fees.py, never an own constant | SOURCED |
| Claim | 83 % green at 1 month, median +7.4 % since 2018 (bXug2l6qICc 00:03:08 and the shortlist); n of his sample NOT_IN_DATA | SOURCED quote |
| DEV window | events with cross day >= 2022-04-01 and exit open <= 2024-06-30. Daily bars before 2022-04-01 (from 2022-01-01, still DEV) are EMA warm-up only | SOURCED (card) |
| Data read | klines files 2022-01 .. 2024-06 only; the loader refuses any bar at or after 2024-07-01. No VALIDATION/HOLDOUT read | SOURCED |

## 3. Inference

Day-block bootstrap, 10000 resamples, seed 20261031 (OURS): crosses whose entry days are within 30 days of the previous one are chained into one block (their holds overlap); blocks are resampled with replacement; CI = 2.5/97.5 percentiles of the resampled mean net return and hit-rate. Reported: mean net return %, hit-rate, mean R, n events, n blocks.

## 4. Look-ahead checks

(a) Causality shift: for every event, recomputing the signal on data truncated at the cross day gives the event; truncated one bar earlier it does not. (b) Future perturbation: changing every bar after day d leaves events up to d unchanged. (c) `MyTradingSys/tests/test_lookahead_lint.py` must pass; an allowlist row only after review. Tests are written before the code and fail first (hand-worked expected values).

## 5. Trial count and Holm

New cells for this card: 1 (Silver cross, 1-month hold). Rows go to this folder's TRIAL_REGISTRY.csv (read by scripts/dev/trial_ledger.py). Holm family for this card m = 1; the result is pre-declared INCONCLUSIVE (section 7), so no repo-wide m is applied. No redesign after seeing outcomes; zero redesigns allowed (0f kill).

## 6. Cost and gross (0a, 0b, 6)

A no-stop 30-day hold: the 0.10 % fee is about 1/70 of the 7.4 % median move he claims, so the fee share is tiny and 0a/0b pass on cost. With no stop, no stop-width rule applies.

## 7. Power and verdict declared in advance (0e, 10)

Expected N is the count of daily 21/55 up-crosses in 2022-04..2024-05: single digits (a count-only pass on event dates is part of the run; outcomes are not read separately). N is far below 100 and below any usable power, so the verdict is declared now: **INCONCLUSIVE whatever the numbers are (underpowered; not "no edge", not "edge")**. DEV_CHECK.md reports the numbers against his claim as description only. His 100 % / 1-year claim cannot be checked on DEV.

## 8. Exits, fills, null, strata (items 7, 8, 9, 12)

Fill = next-bar open, no limit logic. Exit management: his is "hold"; ours is a fixed 30-day open exit (mismatch stated). Null: an all-days baseline (every DEV day entered at the open, held 30 days, same fee) is reported next to the setup as context only. Regime/session strata are not run, n is too small (stated).

## 9. Not allowed

No parameter changes after the run; no EMA length, horizon or hit definition changes; no extra setups added. Windows other than DEV stay unread.

FROZEN_UTC: 2026-10-31T01:05:00Z
