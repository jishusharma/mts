# REPORT: cross-sectional momentum / reversal, Bybit USDT perps, weekly (edge-xsec-momentum-1113)

**Verdict: UNDERPOWERED, no pass.** 0 of 7 cells pass; no cell has VALIDATION CI lower bound > 0 (all CIs span roughly +-2 to +-3 percent a week against means under 0.4 percent), none is BH-10% significant (smallest VALIDATION p 0.42). No factor earns a testnet-forward run on this evidence.

Rule, splits, pass rule: PRE_REG.md (committed 9f86723f1 before any outcome). Factor is SOURCED: academic literature, generic; every parameter is OURS. Nothing tuned.

Regime mix: weeks with a tested universe (>= 10 names), BTC Monday-to-Monday (bull / bear / range): DEV 35/30/94, VALIDATION 14/5/34, RECENT 8/12/50 (up >5%, down <-5%, else range). VALIDATION had only 5 bear weeks; RECENT has the most bear weeks.

Universe: top 20 by trailing 30-day mean turnover among 79 candidates (launchTime <= 2021-12-31), chosen per Monday from data before that date (universe_by_week.csv: 282 weeks 2021-06-14 .. 2026-11-02, 67 distinct names; 18 early weeks have 10-19 names). Candidate list excludes delisted perps (Bybit does not serve them): residual survivorship, which flatters long legs.

Costs: fees.BINANCE_TAKER (5 bp) per side on drifted-weight turnover; Bybit funding history, long pays positive rate, short receives. Columns are weekly means.

| Cell | Split | n | gross | fee | funding | net mean | 95% CI (4-wk block) | p (net<=0) |
|---|---|---|---|---|---|---|---|---|
| MOM-7 | DEV | 159 | -0.08% | 0.16% | +0.05% | -0.20% | [-1.22%, +0.81%] | 0.646 |
| MOM-7 | VALIDATION | 53 | 0.55% | 0.16% | -0.00% | +0.39% | [-2.13%, +3.43%] | 0.420 |
| MOM-7 | RECENT | 70 | 1.57% | 0.15% | -0.02% | +1.40% | [-0.49%, +3.23%] | 0.070 |
| MOM-14 | DEV | 159 | -0.08% | 0.12% | +0.07% | -0.13% | [-1.20%, +0.97%] | 0.593 |
| MOM-14 | VALIDATION | 53 | 0.41% | 0.12% | +0.02% | +0.31% | [-1.77%, +2.85%] | 0.423 |
| MOM-14 | RECENT | 70 | 0.86% | 0.12% | +0.00% | +0.75% | [-1.29%, +2.77%] | 0.234 |
| MOM-28 | DEV | 159 | 0.01% | 0.10% | +0.08% | -0.00% | [-1.68%, +1.53%] | 0.489 |
| MOM-28 | VALIDATION | 53 | 0.10% | 0.10% | +0.07% | +0.07% | [-2.11%, +2.63%] | 0.494 |
| MOM-28 | RECENT | 70 | -1.40% | 0.10% | +0.62% | -0.87% | [-2.85%, +1.24%] | 0.805 |
| REV-7 | DEV | 159 | 0.08% | 0.16% | -0.05% | -0.12% | [-1.12%, +0.88%] | 0.604 |
| REV-7 | VALIDATION | 53 | -0.55% | 0.16% | +0.00% | -0.71% | [-3.77%, +1.86%] | 0.674 |
| REV-7 | RECENT | 70 | -1.57% | 0.16% | +0.02% | -1.71% | [-3.55%, +0.18%] | 0.961 |
| LO-7 | DEV | 159 | -0.52% | 0.09% | +0.03% | -0.58% | [-1.29%, +0.14%] | 0.940 |
| LO-7 | VALIDATION | 53 | 0.18% | 0.08% | +0.04% | +0.14% | [-1.31%, +1.96%] | 0.474 |
| LO-7 | RECENT | 70 | 0.86% | 0.08% | +0.23% | +1.01% | [-0.27%, +2.34%] | 0.060 |
| LO-14 | DEV | 159 | -0.53% | 0.06% | +0.06% | -0.54% | [-1.28%, +0.20%] | 0.916 |
| LO-14 | VALIDATION | 53 | 0.08% | 0.06% | +0.03% | +0.05% | [-1.28%, +1.58%] | 0.497 |
| LO-14 | RECENT | 70 | 0.20% | 0.06% | +0.25% | +0.39% | [-0.91%, +1.76%] | 0.285 |
| LO-28 | DEV | 159 | -0.25% | 0.05% | +0.06% | -0.25% | [-1.22%, +0.66%] | 0.691 |
| LO-28 | VALIDATION | 53 | -0.11% | 0.05% | +0.07% | -0.09% | [-1.19%, +1.14%] | 0.568 |
| LO-28 | RECENT | 70 | -1.04% | 0.05% | +0.54% | -0.54% | [-1.88%, +0.90%] | 0.785 |

Placebo (random q-set per week, 200 draws, same fees and funding), weekly net mean, 5th / mean / 95th percentile:

| Type | Split | p5 | mean | p95 |
|---|---|---|---|---|
| long-short (MOM, REV) | DEV | -1.13% | -0.16% | +0.66% |
| long-short (MOM, REV) | VALIDATION | -1.60% | -0.16% | +1.24% |
| long-short (MOM, REV) | RECENT | -1.20% | -0.10% | +1.06% |
| long-only minus EW | DEV | -0.71% | -0.07% | +0.48% |
| long-only minus EW | VALIDATION | -0.94% | -0.09% | +0.75% |
| long-only minus EW | RECENT | -0.73% | -0.08% | +0.66% |

## Reading
- VALIDATION: best net cell MOM-7 +0.39% a week, CI [-2.13%, +3.43%], p 0.42, below the long-short placebo 95th percentile (+1.24%). Not a result.
- RECENT (reported, never used to select): MOM-7 +1.40% (p 0.07) and LO-7 +1.01% (p 0.06) lean positive, MOM-28 and REV-7 negative; the 7-day momentum sign flips from DEV (-0.20%) to RECENT. A one-regime lean at 70 weeks, not BH-corrected, not a pass.
- DEV (2021-06 on): momentum is flat to negative; 1-week reversal is not positive net (VALIDATION and RECENT clearly negative, i.e. winners kept winning).
- Fees are 0.05-0.16% a week of a 2-5% weekly standard deviation: the weekly horizon makes costs small and noise large, so the limit is statistical power (53 validation weeks), not cost.
- Funding: long-short nets near zero; long-only-minus-EW funding is a small positive in RECENT (+0.2 to +0.5%), a tilt toward shorting high-funding names, not a separate edge.

Limits: universe is a survivor list; weekly open prices from daily bars (not tradable fills); ~50-70 weeks per out-of-sample split.


Worktree: C:\Users\E-ngineers\IdeaProjects\mts-jis-nb-edge-xsec-momentum-1113  sha: d1753e144 (ship in flight, one attempt)
