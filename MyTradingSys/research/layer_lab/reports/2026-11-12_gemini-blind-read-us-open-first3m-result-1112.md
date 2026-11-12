COUNTS: MATCH=8 DIFF=0 NOT_IN_DATA=0

# Blind read: us_open_first3m_2026-11-11/RESULT.md (internal consistency only)

Source: `MyTradingSys/research/us_open_first3m_2026-11-11/RESULT.md` (only file read). Checks are arithmetic and cross-row consistency against the stated universe (line 3: 1006 opens); no raw data was re-run.

| # | file:line | cited | check | verdict |
|---|---|---|---|---|
| 1 | RESULT.md:9 | first 1 min up 463, down 541 | 463+541 = 1004 (2 flat of 1006); matches the 1004 denominator on line 12 | MATCH |
| 2 | RESULT.md:10 | first 3 min up 477, down 529 | 477+529 = 1006 = line 3 universe | MATCH |
| 3 | RESULT.md:12 | 645 / 1004 (64.2%) | 645/1004 = 64.24% | MATCH |
| 4 | RESULT.md:13 | 498 / 1006 (49.5%) | 498/1006 = 49.50% | MATCH |
| 5 | RESULT.md:15 | big (>= 0.20%) 125 / 251 (49.8%) | 125/251 = 49.80%; 251/1006 = 24.9%, consistent with p75 0.20% on line 10 | MATCH |
| 6 | RESULT.md:16 | 113 / 251 (45.0%) | 113/251 = 45.02%; same n as line 15 | MATCH |
| 7 | RESULT.md:18 | last 60: 22 / 60 (36.7%) | 22/60 = 36.67% | MATCH |
| 8 | RESULT.md:22 | n 202: first 3 up 89 / down 113; next 57 up 100 / down 102 | 89+113 = 202; 100+102 = 202 | MATCH |

Not in the 8, spot-checked also consistent: line 14 474/1006 = 47.12%, line 17 29/60 = 48.33%, line 19 470/1006 = 46.72%, line 20 486/1006 = 48.31%, line 21 508/1006 = 50.50%, line 23 109+93 = 90+112 = 202.

## Verdict check (RESULT.md:25)
- "size, not direction": all direction rows (lines 13-21) sit 45-51% except line 18 (36.7%, n 60, small sample); line 12 (64.2%) is minute-1 vs its own containing window, not a forecast. Consistent.
- "about double the volume": line 11 median 2.10x. Consistent.
- "taker share does not separate": lines 22-23 splits 89/113 vs 109/93 (first 3) and 100/102 vs 90/112 (next 57), all within ~44-56%. Consistent.

Note: line 18 (36.7%) is the one outlier and is not called out in the Read; with n = 60 it is within noise, but a reader could mistake it for a contrarian edge.
