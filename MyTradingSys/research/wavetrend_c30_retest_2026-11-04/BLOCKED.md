# prereg_gate.py output, 2026-11-04 (before any return; n = distinct event-days of the "with-trend" pooled cell, signal entry, m = 24, cost 0.14, unit %)

| TF (best conf cell) | n days | sd (%) | MDE + cost | max plausible | n needed | gate |
|---|---|---|---|---|---|---|
| 15m | 214 (optimistic bound) | 0.9 | 0.381 | 0.30 | 486 | BLOCK |
| 30m | 125 | 1.3 | 0.596 | 0.30 | 1013 | BLOCK |
| 1h | 71 | 1.9 | 1.023 | 0.30 | 2165 | BLOCK |
| 15m, single cell (m = 1) | 214 | 0.9 | 0.312 | 0.30 | 248 | BLOCK |

sd values are OURS (typical BTC 12-bar return sd in %, not a study outcome); gate units are R, this study has no stop so % is used (stated).
Counts used are the optimistic unconfluenced "with" bound (counts.csv); every confluence cell (rsi, div) has fewer days, session cells far fewer.
Reading: the design cannot detect a plausible effect after cost on DEV. The DEV table is descriptive; verdict ceiling INCONCLUSIVE (underpowered).
