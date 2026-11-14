FAIL

Blind re-derivation of `MyTradingSys/research/buyzone_test3_bear4h_2026-11-14` from `MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/PRE_REG.md` and `MyTradingSys/backtest/layers/FORMULAS.md` using `MyTradingSys/research/layer_lab/gemini_1114d/rederive-buyzone-test3-bear4h/recompute.py`.

While the overall verdict (`KILL`) and total post-lockout trade count (`1238`) match, the primary claim sample size (`n`), headline mean R, bootstrap CI, and placebo percentile all MISMATCH because `MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/bear4h.py:31` delegates daily phase classification to `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/ladder.py:53-54`, which computes a 60-bar `lo_prior` window (`min Low[t-179..t-120]`) instead of the 120-bar window (`min Low[t-179..t-60]`) specified in `MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/PRE_REG.md:25`.

## Claim Table

| claim | recomputed | stated | file:line | status |
|---|---|---|---|---|
| Primary verdict (BEAR VAL 12 bp) | KILL (OURS, `recompute.py`) | "VERDICT: KILL" (SOURCED) | MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/REPORT.md:185 | MATCH |
| BEAR VAL n | 144 (OURS, `recompute.py`) | "VAL n=211" (SOURCED) | MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/REPORT.md:185 | MISMATCH |
| BEAR VAL mean R12 (no funding) | +0.0088 (OURS, `recompute.py`) | "VAL meanR12=0.090" (SOURCED) | MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/REPORT.md:185 | MISMATCH |
| BEAR VAL mean R12 (with funding) | +0.0112 (OURS, `recompute.py`) | "VAL meanR12=0.092" (SOURCED) | MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/REPORT.md:185 | MISMATCH |
| BEAR VAL 95% CI 12 bp (nf / f) | [-0.1462, +0.1733] / [-0.1433, +0.1744] (OURS) | "CI[-0.069, 0.271]" / "CI[-0.067, 0.274]" (SOURCED) | MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/REPORT.md:185 | MISMATCH |
| BEAR VAL placebo pct 12 bp (nf / f) | 57.35% / 57.8% (OURS, `recompute.py`) | "placebo pct=89.3" / "placebo pct=89.7" (SOURCED) | MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/REPORT.md:185 | MISMATCH |
| BEAR DEV n | 218 (OURS, `recompute.py`) | "DEV n=287" (SOURCED) | MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/REPORT.md:185 | MISMATCH |
| BEAR DEV mean R12 (nf / f) | +0.0959 / +0.0995 (OURS, `recompute.py`) | "DEV meanR12=0.107" / "DEV meanR12=0.111" (SOURCED) | MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/REPORT.md:185 | MISMATCH |
| BEAR RECENT n and mean R12 (nf / f) | n=75, +0.1625 / +0.1648 (OURS) | "| BEAR | RECENT | 127 | 47% | 0.238 | 0.240 |" (SOURCED) | MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/REPORT.md:49 | MISMATCH |
| Total events kept after lockout | 1238 (OURS, `recompute.py`) | "Events kept after lockout: 1238" (SOURCED) | MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/REPORT.md:39 | MATCH |
| Dropped for entry >= stop0 | 0 (OURS, `recompute.py`) | "dropped for entry >= stop: 0" (SOURCED) | MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/REPORT.md:39 | MATCH |
| BTC-only BEAR VAL (n, R12 nf / f) | n=6, +0.5900 / +0.5979 (OURS) | "| VAL | 6 | 50% | 0.590 | 0.598 |" (SOURCED) | MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/REPORT.md:181 | MATCH |

## Root Cause of Mismatches

1. `MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/PRE_REG.md:25` defines `BASE` higher-low as "`min Low[t-59..t] >= min Low[t-179..t-60]`" (SOURCED).
2. `MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/bear4h.py:31` calls `lab = L1.phases(h, l, c)` (SOURCED).
3. In `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/ladder.py:53-54`, `lo_recent = s(l).rolling(60).min().values` and `lo_prior = s(lo_recent).shift(120).values` (SOURCED). Shifting a 60-bar rolling minimum by 120 bars yields `min Low[t-179..t-120]` (a 60-bar window) instead of `min Low[t-179..t-60]` (a 120-bar window).
4. Consequently, `BASE` is under-triggered (`5626` coin-days in DEV in `MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/summary.json:6` vs `8857` OURS) and `BEAR` is over-triggered (`13085` coin-days in DEV in `MyTradingSys/research/buyzone_test3_bear4h_2026-11-14/summary.json:4` vs `10044` OURS). Substituting the 60-bar `min Low[t-179..t-120]` window into `recompute.py` reproduces the stated `BEAR` counts (`287` DEV, `211` VAL) exactly.
