# COUNT (pre-outcome)

## Count section (no return and no A/B/C or other outcome column was computed)

1m bars missing on the DEV tape: 0 of 1313280. Prior-week low available on 903 of 912 days.
First-break events after the 60-minute cooldown (all of the previous 60 closes at/above the level, then a 1m low at least p below it):

| penetration p | round-1000 events | prior-week-low events | pooled ledger | pooled events stacked within 0.1 % / 0.25 % / 0.5 % |
|---|---|---|---|---|
| 0.0 % | 1636 | 189 | 1748 | 0.001: 10  0.0025: 23  0.005: 80 |
| 0.1 % | 1006 | 103 | 1060 | 0.001: 3  0.0025: 13  0.005: 44 |
| 0.2 % | 543 | 70 | 581 | 0.001: 1  0.0025: 8  0.005: 25 |
| 0.3 % | 332 | 56 | 365 | 0.001: 1  0.0025: 7  0.005: 20 |

Primary p = 0.1 %: pooled ledger **n = 1060** (round 1006, weekly 103). Arm sizes (reclaim within 5 minutes; first three closes below) depend on the 1m closes after the break and are printed with the outcome run, not here.
OI: NOT_IN_DATA on DEV (metrics archive starts 2025-09-01). Funding: raw_fund archive absent -> flat 1 bp per settlement crossed.
