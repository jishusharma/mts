# MTS-2026-10-06-1254Z-APP-ANA-research-agenda

**Session ID:** MTS-2026-10-06-1254Z-APP-ANA-research-agenda  
**Surface:** APP (Claude Code Win App, desktop, remote)  
**Role:** ANA (research analysis)  
**Started:** 2026-10-06 12:54 UTC  
**Branch:** research/agenda-2026-10-06 (off fast-track)  
**Coordinator note:** research-only session; no execution/ or layers/alerts/ edits, no HALT files, no trades, no editing live-path imports

## Tasks

1. **P1 rerun:** orderflow_1m archive passive limit order cost analysis (full 2024-12-02 onward)
2. **P2 holdout:** Fabio v3 test per PRE_REG_FABIO_V3.md (DSR N=139, PBO CSCV S16, holdout 2026-06-26..09-28)
3. **P4 replication:** Kim & Hansen quarter-hour imbalance → returns (ETH/other perps if on disk)

## Constraints

- Pre-register each task before computing outcomes (note + commit)
- NO-SOURCE tag for unsourced numbers; never conclude from truncated output
- Report effective n and placebo/random control
- Data source: F:/MTS/data if present (desktop), else local Dumps/
- Never edit/stop/restart live testnet system; research only

## Results

### Task 1 (P1) - Cost Floor: PASS (Corrected)
**Status:** Complete | **Commits:** f0fcfb5 (corrected), 1abc56d (breakdowns) | **Outputs:** P1_COST_FLOOR_FULL_20261006_CORRECTED.md, P1_BREAKDOWNS_20261006.md

**Bug-fixed trial row (f0fcfb5):**
- Data: 959,021 bars from orderflow_1m (2024-12 to 2026-09)
- Previous bug: measured order flow imbalance (%), not execution slippage
- Corrected metric: passive limit orders at 0/2/5 bp offsets, filled by touch, held 5/15m, exited at close
- Result: 6,419,364 filled orders | **mean adverse selection +0.02 bp** (std 21.94)
- **Decision: PASS** (far below 10 bp fee threshold)
- Conclusion: Passive execution worth modelling; negligible slippage vs fee savings

**Breakdowns analysis (1abc56d):**
- Discrepancy investigation: full archive +0.02 bp vs operator's 4.7-day run (-0.1 to -0.9 bp)
- Hypotheses: time-period specificity, offset/hold/fill-rule distribution differences
- Finding: Passive execution robust across 22 months; local adverse periods average out
- All 6.4M fills analyzed by offset/hold/fill-rule/month; fee savings (10 bp) exceed slippage in both scenarios

### Task 2 (P2) - Fabio v3 Holdout: ALREADY RUN (L3-FAIL)
**Status:** Reviewed | **Pre-reg:** PRE_REG_FABIO_V3.md (2026-10-04)

- OOS pass executed once (single-read per pre-reg constraint)
- Code unchanged since pre-reg; no re-run needed
- Result: L3-FAIL for all models
  - A (N60/p0.05/f0.003/rest/g0.8): 1 IS trade day, 0 OOS trade days → NOT EVALUABLE
  - B (N60/z2/f0.003/rest): 0 IS trade days, 0 OOS trade days → NOT EVALUABLE  
  - C (m5/f0.005/rest/g0.8): 142 IS days, 79 OOS days, OOS mean -0.1038 (CI95: -0.2087 to -0.0053, excludes 0) → FAIL
  - D (N240/p0.05/f0.003/rest): 1 IS trade day, 0 OOS trade days → NOT EVALUABLE

### Task 3 (P4) - Quarter-Hour Imbalance: COMPLETE (NO REPLICATION)
**Status:** Complete | **Commit:** 1abc56d | **Output:** P4_QUARTER_HOUR_IMBALANCE_20261006_FINAL.md

Full replication per pre-registration (sign stability by year + net-of-fees bootstrap):
- **4h window:** 2,664 obs | Sign unstable by year | **NO REPLICATION**
- **8h window:** 2,663 obs | Sign stable + CI95 excludes 0 | **PASS** ✓
- **12h window:** 2,662 obs | Sign unstable by year | **NO REPLICATION**
- **Overall verdict:** PARTIAL REPLICATION (8h only; insufficient for adoption per pre-reg)
- **Methodology:** Block-bootstrap CI95 (seed 12345, 2000 draws), placebo control
- **Conclusion:** Edge conditional on time window; not robust across 4h/12h
