# PRE-REGISTRATION P4 CORRECTED - Quarter-Hour Opening Imbalance (2026-10-06)

**Supersedes:** PRE_REG_P4_QUARTER_HOUR_IMBALANCE_2026-10-06.md (ca19750)

**Reason for correction:** Original pre-reg defined "quarter-hour opens" as 00:00, 06:00, 12:00, 18:00 UTC (4 per day). Kim & Hansen's actual definition: every 15 minutes (:00, :15, :30, :45 UTC within each hour) = 96 opens per day. This specification error invalidates the original run.

**Corrected Definition:**

Quarter-hour opens = all times ending in :00, :15, :30, :45 UTC (e.g., 00:00, 00:15, 00:30, 00:45, 01:00, 01:15, ..., 23:45) = 96 opens per calendar day.

**Data:** F:/MTS/data/orderflow_1m (959,021 bars, 2024-12-02 to 2026-09-21)

**Methodology:**

For each quarter-hour open bar i:
1. Compute order flow imbalance = (buy_vol - sell_vol) / total_vol
2. Calculate gross forward returns at 4h, 8h, 12h windows
3. Group returns by calendar year (gross before fees)
4. **Sign stability test:** Gross mean sign must be consistent across all years
5. **Bootstrap CI95:** Week/day-block bootstrap (seed 12345, 2000 draws) on net returns (gross - 10 bp fee)
6. **Overlap handling:** Day-block bootstrap naturally accounts for within-day overlap
7. **Placebo control:** Shuffle imbalances; recompute returns on random imbalances

**Decision Rule:**

- **PASS:** Gross sign stable across years AND CI95 (net) excludes zero
- **FAIL / NO REPLICATION:** Sign unstable OR CI95 includes zero

**Note on apparent paradox:** If gross returns flip sign by year but CI95 (net) excludes zero, this indicates:
- Fee drag (10 bp) overcomes gross sign instability
- Net mean, while statistically significant, originates from different sign regimes per year
- Replication is NOT supported (pre-reg requires consistent gross sign across years)

**Thresholds:** Pre-registered, no tuning.

---

Result block (to be appended after computation):

**RESULT (2026-10-08): NO REPLICATION at 4h, 8h, 12h.** Gross mean +0.43 / +0.10 / -0.24 bp vs 10 bp fee; sign unstable by year. Detail and the interpretation choices this pre-reg left open: `P4_QUARTER_HOUR_IMBALANCE_CORRECTED_2026-10-08.md`.
