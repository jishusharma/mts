# Test ledger

One row per check, newest last. Plan and rules: `CRITICAL_TEST_PLAN.md`. Past audits before 2026-10-30: `research/audit_inventory/AUDIT_INVENTORY.md`.

| Date | Area | Question | Kind (U/I) | Method | Reviewer model(s) | Result | Evidence | Open |
|---|---|---|---|---|---|---|---|---|
| 2026-10-28 | T2 | Can a Pitchfork candidate send an order? | I | static code read | Opus | NO, it cannot order; it can reach the verdict, popup and dashboards when it is the only candidate | `research/pitchfork_2026-10-19/PF_ARM_TRACE.md` | rename risk noted there |
| 2026-10-28 | T2/T3 | Pitchfork layer end-to-end review | U+I | code read + tests (56 pytest, 53 mvn) | Opus | CHANGES REQUESTED: 2 rule-level defects; the cited +0.61% is in-sample, not an edge | `research/pitchfork_2026-10-19/OPUS_E2E_REVIEW_2026-10-28.md` | yes |
| 2026-10-30 | T2 | Which engine switches does the live launcher set? | I | grep of Java flag reads vs `start-trading-day.ps1` | Opus (one model only) | FINDING: `mts.pitchfork=true` set 3 times; `mts.spikeFade` (Tom family-A fade) never set, so it cannot fire on BTC | `scripts/core/start-trading-day.ps1:113,445,475`; `SpikeFadeDetector.java:35,44` | needs the decision that set each switch |
| 2026-10-30 | T3 | Does coded Krown KR-L10 see the operator's daily "last lower high"? | U | ran `krown_core.trend_state` on spot 1d (k=1,2; tol 0.01) | Opus (one model only) | FINDING: state "range" on 10-25..10-29, no dominant high; the operator's line (10-23 high, 82,061 spot / 82,035 perp) is not a fractal pivot, so the detector cannot see it | card `krown-views-via-gemini-what-krown-says-a` | yes |
