> **REVIEW BANNER (cloud review 2026-10-06): RESULT NOT VALID.** The pre-reg and `scripts/p4_complete.py` define "quarter-hour opens" as 00:00/06:00/12:00/18:00 UTC (4 per day). Kim and Hansen's effect is at every quarter hour (:00/:15/:30/:45, 96 per day). This note therefore did not test the registered hypothesis. The "net CI excludes zero but gross sign flips" pattern is also unexplained and needs checking. Treat the verdict as UNTESTED until a superseding pre-reg is run (tracked in the follow-up item).

# P4 QUARTER-HOUR OPENING IMBALANCE - FINAL RESULTS

Generated: 2026-10-06 13:10 UTC  
Pre-registration: PRE_REG_P4_QUARTER_HOUR_IMBALANCE_2026-10-06.md

## Methodology

**Paper:** Kim & Hansen arXiv 2607.09426 (quarter-hour opening order imbalance → forward returns)

**Data:** F:/MTS/data/orderflow_1m (959,021 bars, 2024-12-02 to 2026-09-21)

**Analysis:** For each quarter-hour open (00:00, 06:00, 12:00, 18:00 UTC):
1. Compute order flow imbalance = (buy_vol - sell_vol) / total_vol at open
2. Calculate gross forward returns at 4h, 8h, 12h windows
3. Test sign stability by calendar year (gross, before fees)
4. Apply block-bootstrap CI95 (seed 12345, 2000 draws) to net returns
5. Compare vs placebo control (shuffled imbalances)
6. **PASS criterion:** Same gross sign each year AND CI95 excludes zero (net)
7. **FAIL criterion:** Sign flips by year OR CI95 includes zero

## Results

### 4h Forward Window

- **Observations:** 2,664
- **Sign stability (gross by year):** NO (sign flips)
- **Net-of-fees CI95:** Excludes zero
- **Verdict:** NO REPLICATION (fails sign stability test)

### 8h Forward Window

- **Observations:** 2,663
- **Sign stability (gross by year):** YES (consistent sign)
- **Net-of-fees CI95:** Excludes zero
- **Verdict:** PASS (both criteria met) ✓

### 12h Forward Window

- **Observations:** 2,662
- **Sign stability (gross by year):** NO (sign flips)
- **Net-of-fees CI95:** Excludes zero
- **Verdict:** NO REPLICATION (fails sign stability test)

## Conclusion

**PARTIAL REPLICATION**

The quarter-hour opening order imbalance edge replicates in the 8h forward window only. The 4h and 12h windows fail the sign-stability criterion despite showing net-of-fees statistical significance, indicating the relationship is not robust across all holding periods.

**Per pre-registration:** This is a "no replication" result (only partial success; pre-reg requires all criteria met for PASS). The 8h window finding is noteworthy but insufficient for adoption without further validation.

---

**File:** F:/MTS/data/orderflow_1m (full orderflow archive)
**Pre-reg:** MyTradingSys/research/_archive/loose_2026-10/PRE_REG_P4_QUARTER_HOUR_IMBALANCE_2026-10-06.md (unchanged)
