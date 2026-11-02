# PRE_REG tsfm-zero-shot-vs-analog (frozen before any forecast is run)

Question: does a zero-shot time-series foundation model, given only past BTC bars, produce calibrated quantiles and a fee-net long signal on 4h and 8h bars?

## Data and window
- BTCUSDT USD-M perp 1m klines (data.binance.vision, public, gitignored Dumps/), built into 4h and 8h UTC-aligned bars (complete bars only).
- Window: splits.py DEV 2022-01-01..2024-06-30 only; runner calls splits.assert_dev_only and refuses any bar >= 2024-07-01. VALIDATION/HOLDOUT never loaded. (SOURCED: splits.py)
- F3 (1h) / F4 (8h) ran 2017-2025; compared by their published verdicts on the overlap only (no re-run).

## Model (OURS unless noted)
- Chronos-Bolt-small (amazon/chronos-bolt-small, public weights, SOURCED: HF hub), CPU, torch 2.15, chronos-forecasting 2.3.2 pinned. TimesFM NOT run (DECISION OURS: extra install + weights; time-boxed).
- Input: log close, context 256 bars (OURS), horizon 1 bar (OURS), model's 9 quantile levels 0.1..0.9 (SOURCED: model output).
- Forecasts only at bars whose full 256-bar context lies inside DEV.

## Calibration (descriptive, no verdict)
- Mean pinball loss over the 9 levels on the 1-bar log-return forecast; naive baseline = zero-drift Gaussian with trailing-256 sd.
- 80 % interval coverage (q0.1..q0.9), target 0.80.

## Trade rule (OURS)
- At bar close t: LONG if median forecast log return > 0.0014 (the round-trip fee), else flat. Hold exactly one bar, exit at next bar close. No shorts, no stop.
- Cost: 14 bp round trip (fees.py both legs taker, 0.0014 log units) subtracted per trade. Net R = net log return / DEV sd of 1-bar log return of that bar size (constant, OURS).

## Metric, controls, verdict
- Metric: mean net log return per trade (percent) and mean net R, 95 % CI by week-block bootstrap (2000 resamples, seed 1, blocks = ISO week).
- Controls: (a) shuffled: permute the long/flat flags over all forecast bars 2000x, p = share of shuffles with mean net >= observed; (b) random direction: same trade count, random bars, long. Holm over m = 108 (verdicts.py count 106 + 2 new cells: 4h, 8h); alpha 0.05/m per cell.
- PASS: n >= 30 and bootstrap CI lower > 0 and shuffled p < 0.05/m. FAIL: CI upper < 0. Otherwise INCONCLUSIVE. FAIL means stop for this model, context, horizon and rule on 4h/8h BTC DEV; it says nothing about other models, shorts, or later data.
- Power: prereg_gate.py --n 1000 --sd 0.84 --cost 0.14 --m auto --new-cells 2 -> PASS (MDE 0.115 R; sd from f4/RESULT.md 0.84-1.74). If trades < 519 the result is labelled underpowered.
- One run. No re-tuning after seeing results.
