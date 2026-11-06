# PRE_REG: copy-paste pitchforks vs random parallels, BTC 4H DEV (frozen 2026-11-05, before any count was run)

Card `pitchfork-operator-charts-prep` (U5 in eagle_eyes_picture_2026-10-28/CARD_SPECS.md). Operator 10-30: he drew one fork years
ago and still pastes copies of it (same slope, same width) onto later price, and finds price respects the copies. Question: does
price react at a copied fork's lines more often than at a random line with the same slope? Descriptive DEV count only; no trade,
no fee-net claim, no survivor. The operator's own shots are not on disk yet (classification step pending); this run uses
machine-drawn source forks so the count exists before his shots arrive.

## Context

- Regime: none gated; regime mix of the DEV window reported in RESULT (research_kit.regime_tag, weekly tags)
- Phase: none (no phase gate; all pivots)
- Session: none (4H bars, all sessions)
- Entry: none (descriptive reaction count, no entry)

## Parameters

| Parameter | Value | Label |
|---|---|---|
| Data | `btc_4h_2020_2026.csv` in this folder (BTCUSDT 4H) | in-repo |
| Window | PRE_DEV + DEV (splits.py): bars 2020-01-01 .. 2024-06-30; the loader drops rows at/after splits.DEV_END before any computation. VALIDATION (2024-07-01..) and HOLDOUT (2025-07-01..) untouched | SOURCED splits.py; PRE_DEV use OURS (pasted forks need years of history) |
| Pivots | `find_pivots_zigzag(lookback=4, min_change_pct=0.03)` (scanner defaults) | OURS (in-repo defaults) |
| Source fork | every consecutive alternating pivot triplet, Standard Andrews, log scale | Andrews SOURCED; log scale OURS (multi-year paste) |
| Copy | `copy_fork`: whole fork translated so P0 sits on each of the next 3 pivots of P0's type after P2 | translation SOURCED operator 10-30; "next 3" OURS |
| Look window | bars anchor+lookback+1 .. +60 (copy usable once its anchor pivot is confirmed) | OURS (60 = max_eval_bars) |
| Copy lines | ML, UML, LML of each copy | SOURCED Andrews |
| Control | per copy, 10 parallels: same slope, ML shifted by u x channel width, u ~ U(-1.5, 1.5), seed 20261105; no exclusion zone (overlap dilutes toward zero, conservative) | OURS |
| Touch | first bar in the look window with low <= line <= high; approach side = side of the prior close; one touch per line | OURS |
| Reaction | within 6 bars from the touch (touch bar included), price goes 1.5 % away on the approach side before any close 1.5 % through the line | OURS |
| Statistic | reaction rate given touch, copy vs control; difference in points; two-proportion z; n = touches, plus source forks | OURS |
| Read rule (DEV) | "copies attract" iff diff >= +5 points and z >= 2; else "no difference shown" | OURS |
| Secondary rows | same count in linear scale; the source fork's own lines (unpasted) for reference | OURS |

## Not done here

Holdout run (only after the operator's shots are classified and the definition is checked against how he pastes); fee-net; any
live wiring.

## Run decisions (OURS, 2026-11-05, logged after freezing; no parameter changed)

- Card tag was STALE on a CARD_SPECS.md edit that touched only rows U1-U3, not this card's section: refreshed and built.
- No operator pitchfork shots on disk (where_is, git ls-files, F:/MTS): classification left to a follow-up card; machine forks used.
- Test placed in `backtest/layers/pitchfork/test_pitchfork_copy.py` (own file) rather than test_pitchfork_detector.py.
- Reaction base rate is high (~75 % for every line kind) at 1.5 % / 6 bars on 4H: the test separates lines poorly; a tighter R is a new pre-reg, not a retune here.
