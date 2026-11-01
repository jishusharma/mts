# Audit: FORMULAS.md s26 Cowen band vs phase_tag.py (2026-11-02)

Verdict: **SAME** (3 hand values, plus shift check). Report only; no code edited.

## Formulas
| Formula | FORMULAS.md | Code (research/fractals_2026-10-31/phase_tag/phase_tag.py) |
|---|---|---|
| Weekly close = Sunday bar, Monday present (index >= 6) | s26 | :93-95 |
| SMA20w = mean of last 20 weekly closes | s26 | :96 |
| EMA21w: seed = SMA of first 21, then e += (2/22)(W-e) | s26 | :98-105 |
| Carry forward from last Sunday | s26 | :108-113 |
| Side: above if close>max, below if close<min, else inside | s26 | :115-117 |
| Weekly SMA10 phase: close vs SMA10, slope vs prior week | s26 | :97, :106, :118-119 |
| Tag at row t = features at t-1 | s26 | :123-129 |

## Toy series
A 10-bar daily series holds only one completed week, so the 20/21-week windows cannot be exercised. DECISION (OURS): module constants set to SMA 2, EMA 3, SMA10-phase 2 (phase_tag.py:42) and a 28-bar series from Monday 2023-01-02, closes 10 everywhere except bar6=10, bar13=14, bar20=12, bar24=14, bar27=18. Weekly closes W = 10,14,12,18 (bars 6,13,20,27). The 450-bar default-window worked example in s26 is a hand-only derivation in the doc (not re-run here).

Hand: SMA2 at bar 20 = (14+12)/2 = 13; EMA3 seed (k=2) = (10+14+12)/3 = 12, alpha 0.5, so EMA at bar 20 = 12; at bar 27: 12+0.5*(18-12) = 15, SMA2 = (12+18)/2 = 15.

| Output | Hand | Code | Result |
|---|---|---|---|
| bar 20: sma/ema, side (close 12, not >13, not <12) | 13 / 12, inside | 13 / 12, inside | SAME |
| bar 24: carried 13 / 12, close 14 > 13 | above | above | SAME |
| bar 20: SMA10-phase: close 12 < 13, slope 13 vs prev 12 | below_up | below_up | SAME |
| bar 27: sma 15 / ema 15, close 18, phase | above, above_up | above, above_up | SAME |
| compute_tags row 21 = features of bar 20 | 13/12 inside below_up | same | SAME |

Boundary note: close == lower band gives "inside" (strict <), matches doc.
