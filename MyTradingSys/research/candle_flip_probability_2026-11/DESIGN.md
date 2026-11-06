# Candle-close-colour probability ("flip engine") - design note

Operator ask 2026-11-06 (voice): a flipping engine that watches every timeframe and tells, graphically, how likely the open candle is to close its current colour, used in the live-aid strip.

## What it is (and is not)
- Context layer (a bias number per timeframe), never a TAKE/SKIP signal. See `MyTradingSys/system/OPERATOR_DECISIONS.md` (CBP = context).
- Generalises the ledger sequencing scenarios (`eagle_eyes_picture_2026-10-28/scenario_ledger.csv` S005: lows-first after a down day, 73/103) from the daily to every timeframe.
- The live-aid strip (`tools/live_aid/tf_strip.js`) already shows colour, flip age, time left and CVD per timeframe; this study adds the probability behind the colour.

## Timeframes (20)
1w, 5d, 3d, 2d, 1d, 12h, 8h, 7h, 6h, 4h, 3h, 2h, 1h, 30m, 15m, 10m, 5m, 3m, 2m, 1m.
Odd sizes (5d, 3d, 2d, 7h, 10m, 3m, 2m) need a fixed anchor: bars start at 2024-01-01T00:00Z and tile forward (OURS). 1w anchors Monday 00:00Z, the exchange convention.

## Colour, two definitions (two columns, both reported)
- open-colour: close vs the bar's open (what the chart paints).
- prior-close colour: close vs the previous bar's close (the operator's "less than last week's close").

## The null that must be beaten
Inside an open bar, with displacement d = (price - open) in units of the bar's ATR-scaled sd and fraction of time left t, a random walk gives
P(close on the other side of open) = Phi(-d / sqrt(t)) (Brownian bridge). Early in the bar every candle flips back; late flips carry the information. Raw flip counts therefore look predictive without any edge. The study reports realised minus null, never raw rates.

## Pre-registered cells (max 12, Holm within the study)
HTF colour (1d red/green, 1w red/green) x session (Asia, EU, US) x BB position (inside, at band) is 2x2x3x2 = 24: cut to 12 by pooling 1d and 1w into "HTF aligned / HTF split". Written in PRE_REG.md with `## Context` before any count (step 3pc).

## Scoring
- Brier score of the null per timeframe, then of the conditioned model; a cell counts only if it lowers Brier out of sample (2024 fit, 2025-2026 score).
- Output function: P_close_colour(tf, d_atr, t_left, ctx) -> [0,1], a spec test, and a per-row gauge in tf_strip.js (colour intensity, no new words).

## Review
Haiku credit job through api_job.py (cap 3 USD) reviews PRE_REG.md and RESULT.md; the review is attached as REVIEW.md before ship.

## Risks
- Cell count: this is the kind of study the repo-wide Holm m (card power-gate-holm-m-decision-1106) blocks; the study keeps its own m = 12.
- Anchor choice changes every odd-size bar; the PRE_REG freezes it.
- A probability that only restates time-left is maths, not edge; the Brier-vs-null test is the guard.
