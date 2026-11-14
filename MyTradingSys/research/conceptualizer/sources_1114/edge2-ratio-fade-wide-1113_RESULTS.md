# Account-ratio fade, 1d signal, 20 NEW Bybit perps (wave 2), 2026-11-13

**Verdict: FAIL.** 0 of 2 cells pass. VALIDATION both-sides fee-net mean is -16.8 bp (7d) and +0.1 bp (3d); neither CI excludes zero. Wave-1 DEV/RECENT positive did not replicate on new coins in RECENT (-13 bp at 7d). PRE_REG sha 44b703ef6 (committed before outcomes); rule/thresholds unchanged from wave 1. Raw: results.csv, output.txt in the worktree folder MyTradingSys/research/edge2_ratio_fade_wide_1113.

Coins (20, rank filter explained in PRE_REG, survivor bias stated): ZEC NEAR 1000PEPE SUI UNI XMR AAVE WLD INJ XLM ONDO ARB TAO BCH TIA HBAR ICP QNT STRK APT. Fees = BINANCE_TAKER x2 + funding while held; week-cluster bootstrap 4000; placebo = same coin, same month, same side, random 00:00Z day, 200 draws.

## Both sides pooled (bp per trade, fee-net)
| Hold | Split | n | mean | CI95 | placebo mean / p95 | beats p95 |
|---|---|---|---|---|---|---|
| 7d | DEV | 632 | +134.5 | -14..+273 | +18 / +97 | yes |
| 7d | VALIDATION | 419 | -16.8 | -315..+287 | -139 / -1 | no |
| 7d | RECENT | 532 | -13.4 | -193..+161 | +1 / +124 | no |
| 3d | DEV | 991 | +38.7 | -36..+112 | +9 / +54 | no |
| 3d | VALIDATION | 670 | +0.1 | -146..+152 | -72 / -6 | yes (but CI includes 0, p 0.5) |
| 3d | RECENT | 864 | +25.1 | -60..+109 | +8 / +70 | no |
BH 10% over the 2 VALIDATION p-values selects nothing (p about 0.5).

## Sides (7d hold, VALIDATION / RECENT; n 237/283 long, 182/249 short)
Long-only: +212.5 (CI -124..+598) / +67.0. Short-only: -315.5 (CI -901..+282) / -104.7. The short leg is the loser in VALIDATION and RECENT; the long leg (fade a crowded-short ratio) is positive in every split but its placebo (long drift) is nearly as large: 7d long VALIDATION +212 vs placebo +79 (p95 +253), RECENT +67 vs +124. 3d long: VALIDATION +66, RECENT +90 (CI -20..+219), pooled VAL+RECENT +79 (n 835, CI -23..+182) vs placebo +37 (p95 +110). Not a pass; the one thing leaning positive.

## Per-year, both sides, 7d hold (bp): 2021 +225 (n 34), 2022 +86, 2023 +60, 2024 +64, 2025 +102, 2026 -98 (n 333)
3d hold: 2021 -3, 2022 +53, 2023 +12, 2024 +15, 2025 +37, 2026 +15. So the VALIDATION-year weakness is not a single weak year: 2024H2-2025H1 straddles 2024 (+64) and 2025 (+102), both positive across the calendar-year cut; the loss appears only when VALIDATION is cut by its own boundaries, and 2026 is the first negative calendar year. All yearly CIs include zero. Regime mix (share of 3-day windows up): DEV 0.476, VALIDATION 0.480, RECENT 0.451.

## Reading
Pooled over both waves the ratio fade is near zero both sides with the short leg negative and long leg positive; the earlier 10-coin DEV result of +196 bp is not a stable edge. Best next test, if any: long-only ratio-fade (buy when the account buy-ratio is in its bottom 5%) 3d hold, pre-registered as one cell on both waves pooled with a long-drift-matched placebo; expected size about +70 bp per trade vs +40 placebo, which is inside the CI.
