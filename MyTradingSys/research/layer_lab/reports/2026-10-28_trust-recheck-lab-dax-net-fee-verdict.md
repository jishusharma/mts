# Trust re-check: lab-dax-net-fee-verdict

**Tag Proposal**: `VERIFIED-C2` (Producer != Reviewer satisfied: OpenAI/COD producer vs Google/Gemini reviewer; all re-derived numbers match exactly; test suite passes; mutation fail-first bites).

**Reviewer**: Google, Gemini 2.5 Pro (Antigravity on host DESKTOP-F7IU69N).  
**Producer**: OpenAI, GPT-6.1-Sol (Codex Lab `F:\MTS\mts-codex-lab`, 2026-10-12).  
**Audited Artifact**: [`MyTradingSys/research/layer_lab/reports/2026-10-12_lab-dax-net-fee-verdict.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-lab-dax-net-fee-verdict/MyTradingSys/research/layer_lab/reports/2026-10-12_lab-dax-net-fee-verdict.md)  
**Deliverable Report**: [`MyTradingSys/research/layer_lab/reports/2026-10-28_trust-recheck-lab-dax-net-fee-verdict.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-lab-dax-net-fee-verdict/MyTradingSys/research/layer_lab/reports/2026-10-28_trust-recheck-lab-dax-net-fee-verdict.md)

---

## 1. What Was Checked

1. **Written Specification and Audited Report**:
   - Read `MyTradingSys/research/layer_lab/reports/2026-10-12_lab-dax-net-fee-verdict.md` line by line without producer code inspection.
   - Audited Report line 20: H5 primary preserves per-instrument net RR:
     $$\text{cost} = 2 \times 0.000005 \times 100 = 0.001$$
     $$\text{net\_rr} = \frac{1.25 - 0.001}{1 + 0.001} = \frac{1.249}{1.001} = 1.247752247752\dots < 1.25$$
     Old gross selection returned `SETUP_FORMING`; fixed selection returns `WAIT_RR`.
2. **Independent Mathematical Re-derivation**:
   - Implemented an independent script computing gross RR, round-trip fee costs (5 bps half-turn on GER40 index CFD / FDAX), net reward, net risk, net RR, and verdict against the frozen floor (1.25).
3. **Test Suite Verification**:
   - Executed `python -m pytest MyTradingSys/backtest/test_tom_dax_bt.py -q`.
   - Verified that all 90 tests and 132 subtests pass cleanly.
4. **Mutation Check (Fail-First)**:
   - In a scratch test run, mutated the candidate math to simulate a broken implementation where `gross_rr` (1.25) is evaluated against the floor or replaces `net_rr`.
   - Verified that the mutation changes the returned verdict from `WAIT_RR` to `SETUP_FORMING`, immediately failing `test_primary_rejects_ger40_gross_rr_at_floor` with `AssertionError: 'SETUP_FORMING' != 'WAIT_RR'`.
5. **Vendor Independence**:
   - Producer: OpenAI / GPT-6.1-Sol (Codex lab).
   - Reviewer: Google / Gemini 2.5 Pro (Antigravity).
   - Strict cross-vendor independence is fully satisfied.

---

## 2. Independent Re-derivation Numbers

| Parameter / Metric | Audited Report (2026-10-12:20) | Independent Calculation | Status |
|---|---|---|---|
| Synthetic Entry Price | 100.0 | 100.0 | MATCH |
| Synthetic Stop Price | 99.0 | 99.0 | MATCH |
| Synthetic Target Price | 101.25 | 101.25 | MATCH |
| Gross Risk | 1.000000 | 1.000000 | MATCH |
| Gross Reward | 1.250000 | 1.250000 | MATCH |
| Gross RR | 1.250000 | 1.250000 | MATCH |
| Fee Rate (half-turn) | 0.000005 (0.5 bps) | 0.000005 (0.5 bps) | MATCH |
| Round-trip Cost | 0.001000 | 0.001000 | MATCH |
| Net Risk ($1.0 + 0.001$) | 1.001000 | 1.001000 | MATCH |
| Net Reward ($1.25 - 0.001$) | 1.249000 | 1.249000 | MATCH |
| Net RR ($\frac{1.249}{1.001}$) | 1.247752247752 | 1.247752247752 | MATCH |
| Frozen Floor | 1.25 | 1.25 | MATCH |
| Net RR < Floor Gate | True ($1.247752 < 1.25$) | True ($1.247752 < 1.25$) | MATCH |
| Decision Verdict | `WAIT_RR` | `WAIT_RR` | MATCH |

---

## 3. Findings Table

| Severity | Evidence | Result | Details |
|---|---|---|---|
| SOUND | `MyTradingSys/backtest/tom_dax_bt.py:202-235`; report line 20 | MATCH | Independent formula re-derives cost = 0.001, net RR = 1.247752247752 < 1.25, and verdict WAIT_RR exactly. |
| SOUND | `MyTradingSys/backtest/test_tom_dax_bt.py:489-507` | MATCH | `python -m pytest MyTradingSys/backtest/test_tom_dax_bt.py -q`: 90 passed, 132 subtests passed. |
| SOUND | Mutation test on `cand['math']['net_rr']` | MATCH | In a scratch test run, replacing net RR with gross RR (1.25) flips verdict to `SETUP_FORMING` and fails `test_primary_rejects_ger40_gross_rr_at_floor`. The test strictly bites. |
| SOUND | Producer: OpenAI (`mts-codex-lab`); Reviewer: Google (`mts-gemini`) | MATCH | Cross-vendor independence satisfied (`Producer != Reviewer`). |

---

## 4. Tag Proposal

**`VERIFIED-C2`**

All mathematical formulas, numerical values, and test suites match the audited report. The cross-vendor condition (Google reviewing OpenAI) is satisfied, and the fail-first mutation test demonstrates that the test suite detects regressions.
