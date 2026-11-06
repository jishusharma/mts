# PRE_REG: Malkan regular-divergence window arms, fee-net, DEV (frozen 2026-11-06, before any return was computed)

Card `compare-malkan-divergence-windows-fee-ne`. Source of arms: `research/malkan_hindi_2026-11-04/WINDOW_RECONCILE_1104.md`
(3-10 SOURCED, `extract_Wvq1TZh8aF0.md:131,133`; the operator's 12 / 13-18 / over 18 split has no source, so it is OURS).
The default window (params `malkan_divergence_default.json`, 3-10) stays unchanged whatever this study says.
Code `study.py`, tests `test_study.py` (4 tests, written first and failing before study.py existed).

## Arms (swing-to-swing bars, inclusive of both swings, regular divergence, close-to-close, strict-close pivots, RSI 14, any RSI difference)

| Arm | Bars | Label |
|---|---|---|
| S3_10 | 3..10 | SOURCED Malkan |
| B11_12 | 11..12 | OURS (the operator's "12" band; 11 added so no bar count falls in a gap) |
| C13_18 | 13..18 | OURS (operator's "13-18 OK") |
| D19_50 | 19..50 | OURS (operator's "over 18"; cap 50 = the longest span Malkan names, `TrZQ4Xat_sQ_raw.txt:8`) |

DECISION (OURS): bands tile the line so the arms are disjoint and an event belongs to exactly one arm.

## Parameters

| Parameter | Value | Label |
|---|---|---|
| Data | BTCUSDT + ETHUSDT 1m, `F:/MTS/data/tom_raw/klines`, `klines_eth`, monthly files 2022-01..2024-06 only; resampled to full UTC buckets 1h and 4h | OURS; window SOURCED `backtest/splits.py` |
| Window | DEV [2022-01-01, 2024-07-01). Loader refuses an end past DEV end and never opens a later month file. VALIDATION / HOLDOUT never loaded | SOURCED splits.py |
| Timeframes | 1h, 4h | OURS (task spec) |
| Sides | bullish = long, bearish = short; both read, no regime gate | OURS |
| Entry | close of the event bar (bar after swing B) | OURS (as 2026-10-09 / 11-04 runs) |
| Exit | close 10 bars after the entry bar | OURS, NO-SOURCE (carried) |
| Cost | 0.14 % round trip: `research_kit.TAKER_RT_PCT` (taker in+out incl. slippage); `fees.py` BINANCE_TAKER 0.0005 x 2 = 0.10 % is the fee part, the study asserts 0.14 >= 0.10 | SOURCED research_kit / fees.py |
| Statistics | net = gross - cost; cluster = symbol x UTC day of entry; CI = mean +- 1.96 SE (`research_kit.cluster_mean_se`) | SOURCED research_kit |
| Family | 4 arms x 2 TF x 2 sides = 16 cells; Holm with m = 16 (`research_kit.holm`); BTC and ETH pooled inside a cell | OURS |
| Contrast | each OURS arm minus S3_10, same TF and side (`research_kit.cluster_diff`), descriptive | OURS |
| Survivor | n >= 30, >= 20 distinct clusters-days, net mean > 0, Holm p < 0.05 | OURS |
| No drift control | all arms in one cell group share the same bars, so drift is common; a positive net is not an edge claim | OURS |

## Power gate (`scripts/dev/prereg_gate.py --m auto --new-cells 16`, run BEFORE any return; counts from `study.py --pass count`, `counts.csv`)

Event counts (days = clusters): S3_10: 1h bearish 550 / 405 days, 1h bullish 517 / 399, 4h bearish 132 / 128, 4h bullish 129 / 125.
All other arms: 0-2 events in a cell (B11_12 2, C13_18 2, D19_50 0 in total). Consecutive strict-close swing pairs almost never sit
more than 10 bars apart, so the OURS windows cannot be tested by this detector. This is a count, not a return.
Gate inputs: sd = unconditional 10-bar return sd in %, measured on all bars of the DEV window (BTC/ETH 1h 1.8 / 2.3, 4h 3.65 / 4.55; used 2.0 and 4.0); cost 0.14; max plausible gross 0.30; m auto = 236.

| TF | n days | sd % | m | MDE + cost | n needed | gate |
|---|---|---|---|---|---|---|
| 1h | 405 | 2.0 | 236 | 0.592 | 3227 | BLOCK |
| 4h | 128 | 4.0 | 236 | 1.747 | 12907 | BLOCK |

Consequence, fixed now: the DEV table is DESCRIPTIVE. A FAIL cannot be issued from a cell that cannot detect a plausible effect, so the
verdict ceiling is INCONCLUSIVE (underpowered). A PASS needs an S3_10 survivor, and still would not move the default (VALIDATION read is a separate card).
Verdict rule: INCONCLUSIVE when the gate blocks (it does); FAIL only if the gate passed and no cell survives; PASS only on a survivor plus an independent re-run.

## What the result will say

RESULT.md: per-arm n, fee-net mean, CI, Holm p, the `Regime mix:` line, the verdict, and the empty-window finding.

## Context
Regime: not a filter here; the window regime mix is reported as context (research_kit.regime_tag, as the 11-04 study).
Phase: none, left to a later re-run.
Session: none, left to a later re-run.
Entry: signal-bar close only; retest entry not tested here (OURS).
