# FLOW result (forced flows), BTCUSDT USD-M perp, 1h bars 2020-01..2026-10. Frozen rules in PREREG.md. Script: flow_test.py, raw table: results.csv, log: out.txt.
Net = price move minus 10 bp round trip (fees only). Funding column = same minus funding paid/plus received. Placebo pct = share of 200 random same-count entries with a lower mean (95+ beats chance).
Funding history on disk starts 2020-01 (the archive's own start); OI on disk is 2022-01..2025-12; no liquidation history exists (event b is the drop+volume proxy).
Data note: funding timestamps carry up to 4 ms jitter; fixed by flooring to the hour (first run before the fix gave similar numbers).

## (a) Funding extreme, 3-day hold (eligible 2021-01+)
| split | side | n | win % | mean net % | t | placebo pct | mean net incl. funding % |
|---|---|---|---|---|---|---|---|
| DEV | long (bottom 5 %) | 55 | 63.6 | +1.328 | 1.75 | 94.5 | +1.328 |
| DEV | short (top 5 %) | 111 | 45.9 | -0.485 | -0.85 | 47.0 | -0.262 |
| DEV | both | 166 | 51.8 | +0.116 | 0.25 | - | +0.265 |
| VAL | long | 58 | 44.8 | -0.337 | -0.63 | 20.5 | -0.337 |
| VAL | short | 27 | 59.3 | -0.181 | -0.19 | 52.5 | -0.113 |
| VAL | both | 85 | 49.4 | -0.288 | -0.61 | - | -0.266 |

## (b) Cascade proxy (drop/spike >= 3 % on volume > 3x 30-day median), 24 h hold (eligible 2020-02+)
| split | side | n | win % | mean net % | t | placebo pct | mean net incl. funding % |
|---|---|---|---|---|---|---|---|
| DEV | long (drop) | 75 | 52.0 | +0.581 | 0.84 | 89.5 | +0.563 |
| DEV | short (spike) | 59 | 40.7 | -0.353 | -0.53 | 49.5 | -0.285 |
| DEV | both | 134 | 47.0 | +0.170 | 0.35 | - | +0.189 |
| VAL | long | 17 | 47.1 | +1.344 | 1.69 | 100.0 | +1.331 |
| VAL | short | 11 | 81.8 | +1.274 | 1.47 | 98.5 | +1.300 |
| VAL | both | 28 | 60.7 | +1.317 | 2.27 | - | +1.319 |

## (c) OI flush (OI -5 % in 4 h with price down), long 24 h (eligible 2022-01..2025-12)
| split | side | n | win % | mean net % | t | placebo pct | mean net incl. funding % |
|---|---|---|---|---|---|---|---|
| DEV | long | 75 | 54.7 | -0.106 | -0.26 | 39.0 | -0.124 |
| VAL | long | 18 | 55.6 | +0.669 | 1.11 | 90.5 | +0.651 |
(no short side defined for c)

## Reading (frozen verdict rule: positive in both splits, |t|>=2 in VALIDATION, placebo >=95 both, n>=30 each)
- (a) FAIL: the one DEV winner (funding bottom 5 % long, +1.33 %, placebo 94.5) flips to -0.34 % in VALIDATION (placebo 20.5); the short side loses in both splits.
- (b) INCONCLUSIVE, not a pass: VALIDATION is +1.3 % (t 2.27 both sides, placebo 98-100) but n is only 17 + 11, and DEV is t 0.35 with the short side negative (-0.35 %); the sign agrees for the long side only (+0.58 DEV, +1.34 VAL, both t < 2).
  Long-after-cascade is the only lead; its validation n is far below the n >= 30 bar, and the 24 h returns are fat-tailed (a few 2022-2024 rebounds can carry a mean this size).
- (c) INCONCLUSIVE/FAIL: DEV -0.11 % (t -0.26); VALIDATION +0.67 % with n 18, t 1.11. Events cluster (one flush day gives several entries; one-position rule only skips overlaps), so effective n is lower than shown.
- Fees 10 bp are small next to these 24 h/72 h moves (std per trade several %); every mean is within about 2 SE of zero, so nothing here separates from noise at these n. No forecast.
