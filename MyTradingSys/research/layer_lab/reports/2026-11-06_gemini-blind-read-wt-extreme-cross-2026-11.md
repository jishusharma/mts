# Blind Read: gemini-blind-read-wt-extreme-cross-2026-11

Reader: Gemini (independent blind read worker), 2026-11-06.
Target study: `MyTradingSys/research/wt_extreme_cross_2026-11/RESULT.md` (registry).
Data source: `MyTradingSys/research/wt_extreme_cross_2026-11/dev_cells.csv` (135 cells).
Audit detail: `MyTradingSys/research/gemini_audits_2026-11-05/BLIND_READ_WT_EXTREME_CROSS.md`.
Verification command: `python -c "import pathlib; p=pathlib.Path('MyTradingSys/research/gemini_audits_2026-11-05/BLIND_READ_WT_EXTREME_CROSS.md'); assert p.exists() and 'VERDICT' in p.read_text()"`

## Headline Verification (dev_cells.csv vs RESULT.md:39-47)
Every cell was loaded and recomputed from `dev_cells.csv` prior to reading `RESULT.md`.

- **1m buy -50 (card)**:
  - SOURCED `RESULT.md:39`: `15936 | 912 | 0.161 / 0.104 | 32 | 0.148 | +0.013 (3.7) | -0.141 (-58.6) | 0.20`
  - OURS `dev_cells.csv:2`: n=15936, days=912, mfe=0.161040/0.103707, pts=32.4, base=0.148157, excess=+0.012883 (t=3.67), net=-0.141446 (t=-58.63), hit=0.195971 -> MATCH.
- **1m buy -60 (bible60)**:
  - SOURCED `RESULT.md:40`: `7310 | 910 | 0.187 / 0.122 | 38 | 0.148 | +0.039 (8.2) | -0.140 (-35.6) | 0.22`
  - OURS `dev_cells.csv:32`: n=7310, days=910, mfe=0.187248/0.122013, pts=37.6, base=0.148157, excess=+0.039091 (t=8.21), net=-0.139909 (t=-35.57), hit=0.224350 -> MATCH.
- **1m sell +40 (card)**:
  - SOURCED `RESULT.md:41`: `26580 | 912 | 0.145 / 0.094 | 29 | 0.149 | -0.005 (-1.7) | -0.141 (-79.7) | 0.18`
  - OURS `dev_cells.csv:17`: n=26580, days=912, mfe=0.144752/0.093666, pts=29.0, base=0.149345, excess=-0.004593 (t=-1.73), net=-0.140850 (t=-79.69), hit=0.175282 -> MATCH.
- **5m buy -50 (card)**:
  - SOURCED `RESULT.md:42`: `2938 | 832 | 0.387 / 0.248 | 79 | 0.348 | +0.038 (2.8) | -0.134 (-12.6) | 0.36`
  - OURS `dev_cells.csv:47`: n=2938, days=832, mfe=0.386557/0.248300, pts=78.7, base=0.348263, excess=+0.038294 (t=2.83), net=-0.133884 (t=-12.65), hit=0.363513 -> MATCH.
- **5m buy -60 (bible60)**:
  - SOURCED `RESULT.md:43`: `1400 | 654 | 0.436 / 0.291 | 93 | 0.348 | +0.087 (4.3) | -0.128 (-7.2) | 0.40`
  - OURS `dev_cells.csv:77`: n=1400, days=654, mfe=0.435612/0.290514, pts=92.7, base=0.348263, excess=+0.087349 (t=4.30), net=-0.127860 (t=-7.21), hit=0.402143 -> MATCH.
- **5m sell +40 (card)**:
  - SOURCED `RESULT.md:44`: `5130 | 904 | 0.340 / 0.219 | 69 | 0.352 | -0.012 (-1.6) | -0.140 (-18.2) | 0.33`
  - OURS `dev_cells.csv:62`: n=5130, days=904, mfe=0.339532/0.218716, pts=69.2, base=0.351843, excess=-0.012311 (t=-1.55), net=-0.140014 (t=-18.25), hit=0.327290 -> MATCH.
- **15m buy -50 (card)**:
  - SOURCED `RESULT.md:45`: `922 | 499 | 0.688 / 0.459 | 136 | 0.626 | +0.062 (1.9) | -0.128 (-3.8) | 0.46`
  - OURS `dev_cells.csv:92`: n=922, days=499, mfe=0.687555/0.459296, pts=135.9, base=0.625672, excess=+0.061883 (t=1.86), net=-0.127785 (t=-3.83), hit=0.464208 -> MATCH.
- **15m buy -60 (bible60)**:
  - SOURCED `RESULT.md:46`: `462 | 307 | 0.797 / 0.520 | 164 | 0.626 | +0.171 (3.3) | -0.089 (-1.7) | 0.49`
  - OURS `dev_cells.csv:122`: n=462, days=307, mfe=0.797172/0.520397, pts=164.5, base=0.625672, excess=+0.171499 (t=3.29), net=-0.088846 (t=-1.75), hit=0.489177 -> MATCH.
- **15m sell +40 (card)**:
  - SOURCED `RESULT.md:47`: `1636 | 693 | 0.630 / 0.433 | 143 | 0.632 | -0.001 (-0.1) | -0.152 (-6.3) | 0.42`
  - OURS `dev_cells.csv:107`: n=1636, days=693, mfe=0.630391/0.432739, pts=142.55, base=0.631804, excess=-0.001414 (t=-0.07), net=-0.151981 (t=-6.28), hit=0.421760 -> MATCH.

## Split Rows & Notes
- Split rows in `RESULT.md:53-63` (11 rows, 66 values) were verified against `dev_cells.csv`; all 66 values match.
- Finding on `RESULT.md:65` ("The only positive net cell in the 135..."):
  - SOURCED `RESULT.md:65`: `15m buy -60, same_range day (ex-post tag), n 309, net +0.043 % (t 0.7)` matches OURS `dev_cells.csv:123` (n=309, net_mean=+0.043046%, t=0.697).
  - Scope nuance: This is the only positive cell among the 45 marginal cells where `htf == 'all'`. In the full 135-cell dataset with `htf` slices, 4 cells have `net_mean > 0`, but none are statistically significant (all $|t| < 1.4$) and none represent a tradable edge.

## Verdict
All 99 headline table numbers, 66 split table numbers, and stated prose numbers match `dev_cells.csv` exactly.

VERDICT: MATCH
