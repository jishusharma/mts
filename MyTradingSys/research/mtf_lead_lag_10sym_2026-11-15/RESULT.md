Regime mix: 150 weeks: bull 58 (39%) | bear 0 (0%) | range 92 (61%) | n/a 0 (0%)  (BTC, 2024-01-01..2026-11-14, research_kit.regime_tag; the tag never returns bear in this window, so the per-regime cut has bull and range only)

# Early-flip rules R1-R3 on 10 symbols, out of sample 2024+: NO EDGE (underpowered, INCONCLUSIVE ceiling)

**The early-flip rules still anticipate the daily flip (R3 hit 43.4 % vs 25.3 % base, +18 points), but none makes money fee-net on 10 symbols: R3 3-day net -0.025 %, n 4,393 (980 days), Holm-adjusted p 1.00. The BTC-only +0.17 % does not carry over; use it as context, not a trigger.**

Pre-registration `PRE_REG.md` (frozen in 54e9c99ca before any return), code `study.py` (rules reused unchanged from `mtf_lead_lag_2026-11-09/lead_lag.py`), tests `test_study.py` (3). Data: Binance spot 1h/4h/1d, 10 symbols, events 2024-01-01..2026-11-07. Cost = research_kit.TAKER_RT_PCT 0.14 % round trip. Power gate BLOCKs (POWER_GATE.md): a 3-day net effect below about 0.66 % is not detectable here.

## Context
Regime: pooled; BTC regime tag is a descriptive cut only. Phase: 4h+1h RSI both flipped to 60+/40-, R3 with daily RSI already on that side of 50. Session: none. Entry: confirming close, 3-day hold (1 d, 7 d descriptive), no stop.

## Verdict table (3-day fee-net, SE = larger of day-cluster and week-cluster, Holm m = 3)
| Rule | n (days) | hit | hit - base | gross 3d | net 3d | SE used | Holm p | net 2024-01..25-06 | net 2025-07..26-11 | EDGE |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 4h flip | 3,919 (939) | 38.6 % | +13.3 | +0.058 % | -0.083 % | 0.233 | 1.00 | +0.109 % | -0.289 % | no |
| R2 4h+1h | 5,996 (1,022) | 37.1 % | +11.8 | +0.068 % | -0.073 % | 0.244 | 1.00 | -0.003 % | -0.148 % | no |
| R3 R2 + 1d RSI side | 4,393 (980) | 43.4 % | +18.1 | +0.115 % | -0.025 % | 0.296 | 1.00 | -0.022 % | -0.028 % | no |
| Baseline (every 4h close, both sides) | 125,040 | 25.3 % | | 0.000 % | -0.140 % | | | | | |

No rule is positive in both halves, and none beats the baseline by 2 SE (R3 +0.115 % over baseline, SE 0.195). R3 per side: BULL +0.417 % net (n 1,947, p 0.18), BEAR -0.377 % (n 2,446, p 0.17): a long-only drift in a bull-leaning window, not a lead; neither survives clustering. 1-day and 7-day nets are also at or below zero (cells.csv).

## Lead time (descriptive, leads.csv)
The 4h RSI flip precedes the daily one in 95-97 % of daily flips on the three largest symbols (median 12-20 h, IQR 8-32/56 h; BTC 78 daily flips, 96 %, median 12 h, matches the parent's VAL 12 h). WaveTrend 4h leads 100 % at about 36 h.

## Comparison with the BTC study
Parent R3 VAL: hit 41.0 % vs 22.7 %, 3d net +0.17 % (1.2 SE). Here the hit lift holds (+18 points over 10 symbols) but the trade return does not: the anticipation is real, the fee-net trigger is not.

## Limits
Power gate BLOCK (above); survivor-biased majors; spot, no funding; 3-day holds overlap (week-cluster SE used); the regime tag has no bear weeks in 2024+, so no bear-regime read; reading 2024+ burns the holdout for this family (holdout_reads.csv).
