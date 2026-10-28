# FILE: mts/tests/regression_log.md
# READ ORDER: After TEST_PLAN.md
# PURPOSE: History of patch smoke tests
# Date: 2026-08-29
# Status: ACTIVE
# Canonical path: /mnt/agents/output/upload_mirror/mts/tests/
# ---

# REGRESSION LOG — Patch Smoke Tests
# Rule: Append new runs at the TOP. One line per patch.

---

## 2026-08-29 — Baseline: GS-001 (v4.2.0-p2)

| Patch | JSON Used | Verdict Before | Verdict After | Match? |
|-------|-----------|---------------|---------------|--------|
| (baseline) | `runtime_data/test_snapshot_v4.2.0-p2_validation.json` | — | WAIT C (55/100) | — |

**Next:** Log smoke test result here after each engine patch. One row per patch.

---
## 2026-08-31 — p3: Cross-trader Phase 4 Integration
| Patch | JSON Used | Verdict Before | Verdict After | Match? |
|-------|-----------|---------------|---------------|--------|
| p3 | `runtime_data/test_snapshot_v4.2.0-p3_cross_trader.json` | — | C+ (60/100) | — |
**Notes:** 16 NEW entries integrated. 3 conflicts resolved. 5 GAP entries resolved.

## 2026-08-31 — p4: Bug Hunt (BUG #4/#5)
| Patch | JSON Used | Verdict Before | Verdict After | Match? |
|-------|-----------|---------------|---------------|--------|
| p4 | `runtime_data/test_snapshot_v4.2.0-p4_validation.json` | — | WAIT C (55/100) | — |
**Notes:** BUG #4 CVD/trade_flow resolution. BUG #5 order_book_depth limitation documented.

## 2026-09-01 — p5: Questionnaire Decisions
| Patch | JSON Used | Verdict Before | Verdict After | Match? |
|-------|-----------|---------------|---------------|--------|
| p5 | `runtime_data/test_snapshot_v4.2.0-p5_validation.json` | — | C+ (65/100) | — |
**Notes:** 25/25 questionnaire decisions applied. VVP-001 v1.1.0 active. Chart layout guide created.

---
# END
