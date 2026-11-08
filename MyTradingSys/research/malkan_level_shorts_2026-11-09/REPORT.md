# Malkan level short, BTC 4h, counted 2017-08 .. 2026-11

**No arm is a proven edge. The best arm uses Malkan's own sourced divergence window (3-10 bars, close to close): 126 trades, +0.11 R per trade after fees, positive in bull and bear and in 6 of 10 years. That is about 0.9 standard errors from zero, with 10 arms tried. The full 5-layer stack fires 37 times in 9 years (+0.14 R, about 0.6 SE). Worth a cheap testnet forward look; not worth money.**

Card `malkan-level-short-4h-count-1109`. Layer: `MyTradingSys/backtest/layers/rsi/malkan_level_short.py` (rules in its docstring). Runner: `count.py` writes `COUNT.json`. Data: Binance spot BTCUSDT 4h/1d/1w, closed bars only, from data-api.binance.vision, 20,208 4h bars. Every trade: short, stop at the highest high since the level tag +5 bps, target 2R, 60-bar time stop, stop wins a shared bar, 0.04 % taker fee each side. Regime = daily close above or below its 200-day SMA.

## Context

- Regime mix: 7y pooled, split bull/bear below. Phase: none (the current 75.4-80.9k range is too short for a count; that is what testnet is for). Session: none (4h). Entry: stop order under the prior bar's open within 3 bars.
- Level = OURS proxy: a confirmed 5/5 pivot high or low within 60 days, tagged from below (high within 0.5 %, close not more than 0.5 % above). The operator's lines are hand-drawn and cannot be counted.

## The five operator points

| Point | Base (level + trigger) | Full 5 layers | Dropped by |
|---|---|---|---|
| C1 08-28 | fires | no | HTF (daily/weekly never failed 60) |
| C2 09-04 | fires | no | WaveTrend (peak 38.8), HTF |
| V1 09-23 | fires | no | WaveTrend (crossed down more than 4 bars before the trigger), HTF |
| V2 10-06 | fires | no | WaveTrend, HTF |
| C3 10-22 | fires | **yes** | - |

This matches READING.md's own table, where only C3 shows all five layers. The test pins it (`test_malkan_level_short.py`).

## Count by arm (all years)

| Arm | n | hit 1R | win 2R | gross R | net R | bull net (n) | bear net (n) |
|---|---|---|---|---|---|---|---|
| base level + trigger | 529 | 0.48 | 0.30 | +0.01 | -0.03 | -0.07 (282) | +0.06 (217) |
| + structure (div or sweep) | 482 | 0.49 | 0.31 | +0.03 | -0.00 | | |
| + structure div 3-10 close (SOURCED window) | 126 | 0.49 | 0.37 | +0.15 | **+0.11** | +0.12 (70) | +0.14 (49) |
| + structure div 5-50 close | 254 | 0.50 | 0.32 | -0.00 | -0.04 | | |
| + structure div 5-50 wick | 273 | 0.48 | 0.31 | +0.02 | -0.02 | | |
| + structure sweep | 472 | 0.49 | 0.31 | +0.04 | +0.01 | | |
| + WaveTrend | 201 | 0.48 | 0.32 | +0.11 | +0.08 | +0.01 (117) | +0.31 (69) |
| + HTF 60 fail | 148 | 0.51 | 0.33 | +0.12 | +0.08 | +0.08 (67) | +0.11 (76) |
| FULL 5 layers | 37 | 0.49 | 0.35 | +0.17 | +0.14 | +0.20 (24) | -0.07 (11) |
| FULL, div 5-50 wick | 10 | 0.50 | 0.40 | +0.35 | +0.31 | | |

Rough standard error per trade at a 2R target is about 1.4 R, so SE = 1.4/sqrt(n): 0.12 R at n=126, 0.23 R at n=37. Nothing here clears 2 SE.

## Answers to the card's two questions

1. **Window: 3-10 bars beats swing to swing.** Widening to 5-50 bars (what the operator's 4h reads needed, 15-19 bars) doubles the count and takes the result to zero. Malkan's sourced short window is the only divergence arm with a positive sign.
2. **Close vs wick: no difference** at 5-50 bars (-0.04 vs -0.02 R).

## What it means

- The sweep (a lower high that runs a pivot high and closes back under it) is nearly always present at a level tag, so as written it filters nothing (482 of 529). Layer 2 only adds information through divergence.
- WaveTrend and HTF each lift the base by about +0.1 R, mostly in bear regimes. Stacking all five leaves 4 trades a year.
- The five hand-picked points all caught 1R+; the counted base catches 1R only 48 % of the time. The reads are a pattern, as READING.md said, not an edge.

## Next

- Testnet forward, context-only (phase-first): the `div 3-10 close` arm on BTC 4h in the current range, with a kill line of 30 trades at net R <= 0. Filed raw for JIS-NB as `malkan-level-short-testnet-forward-1109` (live path belongs to C's lane).
- Not done: the long side, and other symbols.
