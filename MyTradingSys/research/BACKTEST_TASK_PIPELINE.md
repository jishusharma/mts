# Backtest Task Pipeline - 2026-10-05

**Generated:** 2026-10-05 16:50 UTC  
**Branch:** fast-track (never main)  
**Status source:** STATUS.md (2026-10-01), WORKER_ROADMAP.md, SUPERVISOR_LOG.md, NEXT_SESSION_PLAN.md  

---

## Executive Summary

This pipeline lists all open backtest tasks prioritized by readiness and impact. Tasks fall into three buckets:
1. **In Queue** (T1/T2/T3 workers, awaiting execution or verification)
2. **Ready to Gate** (.new files staged, awaiting promotion)
3. **Research Pending** (design phase, not yet staged)

---

## Priority Queue

### P1: T055 C1/C2/C3 Backtest (Q2, T3 Sonnet)

**Status:** Blocked, waiting on T055 Turn-of-Candle (0989) to land

**Description:** Backtest three cost models (C1=15m, C2=1h, C3=1h) for long/short entries with side-aware position sizing.

**Inputs:**
- `MyTradingSys/backtest/layers/run_t055.py.new` (driver, 22 stub tests)
- `MyTradingSys/backtest/test_run_t055.py.new` (test harness)
- 1m historical OHLCV 2022-01 to 2025-08 (already fetched, 210 MB)
- FORMULAS.md sections 13-16 (committed: T055 cost model)
- Existing test plans (T055_BT_c1.md, T055_BT_c2.md, T055_BT_c3.md)

**Critical Requirement (NEW 2026-09-29):**
- ADD FUNDING to C2/C3 net results (holds can cross 00/08/16 UTC; data available 2025-09+)
- Funding must be included before any "pass" is accepted

**Next Steps:**
1. Promote 0989 (Turn-of-Candle) when NUC reply lands (expected: today)
2. Run step 5b gate: `pytest MyTradingSys/backtest/layers/turn_of_candle/test_turn_of_candle.py`
3. Promote run_t055.py.new + test_run_t055.py.new
4. Execute: `python MyTradingSys/backtest/layers/run_t055.py --tf 1h --funding-start 2025-09-01`
5. Write T055_BT_c1/c2/c3.md reports
6. **Decision:** Any passing setup → ALERT layer only, never a Tom filter

**Owner:** T3 Sonnet subagent  
**Gate:** run_all_tests --quick (step 5b), spec-derived edge tests (4-10)  
**Expected Output:** 3 backtest reports with Sharpe/PBO/net metrics per setup

---

### P2: Fabio Layer Backtest (Q3, T3 Sonnet)

**Status:** Blocked, driver not yet validated

**Description:** Test whether core MTS + Fabio layers produce quality setups on historical data.

**Inputs:**
- `MyTradingSys/backtest/layers/fabio/run_backtest.py` (UNTRACKED, never run)
- Fabio v3 modules (committed: a408fa6 escalation + detectors)
- 1m OHLCV + order-flow bars (120 days downloaded to F:\MTS\data\orderflow_1m)
- FABIO_TRADE_MODEL.md (operator's trade model synthesis)

**Context:**
- Fabio L1 research (FABIO_L1_REPORT.md) found 0/64 variants net-positive OOS
- Median gross +0.13R but fees -0.66R (tight stops on Deribit)
- This backtest validates the conditional (balance/imbalance) model vs simple detector model

**Next Steps:**
1. Gate the driver: validate run_backtest.py against spec
2. Run the full suite with edge tests (tight stops, state transitions, fee scenarios)
3. Write FABIO_L1_REPORT.md / FABIO_TRADE_MODEL.md conclusions
4. Log setup recommendations per state
5. **Decision:** Any edge → ALERT layer only, never a Tom filter

**Owner:** T3 Sonnet subagent  
**Gate:** run_all_tests --quick, operator edge-case rules  
**Expected Output:** FABIO_L1_REPORT.md with setup matrix

---

### P3: Formula Audit Re-run (Q4, T2→T3)

**Status:** Blocked, 082 FAILED (verdict shows 1 unknown file, 3 missing EXPECT lines)

**Description:** Verify that all formulas in FORMULAS.md match the code; find and fix discrepancies.

**Inputs:**
- NUC task 082 (FAILED): formula_audit.py
- FORMULAS.md sections 1-16 (all MTS formulas: core, execution, indicators, backtest)
- Code paths: layers/rsi, layers/cryptocred, execution/risk_guard, backtest/bt/*

**Why It's Blocked:**
- 082 output hit 6144-token cap; need to re-split into <=5k prompt tokens per spec
- Output size must accommodate the full reply (not truncated)

**Next Steps:**
1. Repack 082 as 082r/083/084 (3 files, ~5k prompts each)
2. Set OUTPUT_TOKENS large enough for complete reply
3. Run each on qwen3-coder:30b
4. Verify output against code (one claim per formula)
5. Commit approved formula changes + test updates
6. Confirm run_all_tests --quick step 5 is green

**Owner:** T1 Qwen → T2 Haiku verification  
**Gate:** run_all_tests --quick (backtest step), formula cross-check test  
**Expected Output:** 082r/083/084 replies + FORMULAS.md corrections

---

### P4: Tick Layer Tier Computation (Q6, T3 Sonnet)

**Status:** Design done (091-093 promoted), full-history run NOT started

**Description:** Compute per-timeframe volatility tiers for tick indicators (CVD, OI, net delta) on all historical data.

**Inputs:**
- Tick modules 091-093 (promoted, live context-only flags)
- Dumps/backtest/raw_1m_2022 + recent 2025 data (complete 1m history)
- OI metrics from Deribit API

**Next Steps:**
1. Run tick_extremes on full history (Sonnet agent)
2. Compute per-15m-tier bounds for volatility percentiles
3. Write tiers.json with (timeframe, metric) → [p10, p25, p50, p75, p90]
4. Validate against recent 30 days (live check)
5. Commit tiers.json

**Owner:** T3 Sonnet  
**Gate:** Validation against recent live data (no edge should exist on stale tiers)  
**Expected Output:** tiers.json + validation report

---

## Ready-to-Promote .new Files

Files staged, passing local tests, awaiting gate verification and promotion.

| File | Status | Tests | Gate | Notes |
|------|--------|-------|------|-------|
| `layers/turn_of_candle/test_turn_of_candle.py` | PENDING NUC | stub | step 5b | Awaits 0989 reply; hourly check auto-gates |
| `backtest/layers/rsi/bt_rsi.py.new` | HOLD | 13 + 11 edge | run_all_tests | Seed bug fixed (FORMULAS s1); 24/24 PASS |
| `backtest/layers/prob_table/prob_table.py.new` | HOLD | 12 + 9 edge | run_all_tests | Log-loss fix; 21/21 PASS |
| `backtest/layers/fabio/fabio_escalation.py.new` | HOLD | 4 + 10 edge | run_all_tests | Import fixed, only first absorption counts; 14/14 PASS |
| `backtest/layers/cryptocred/cc_retest.py.new` | HOLD | 20/20 live | run_all_tests | Tests differ only in .new loader; live tests PASS |
| `backtest/layers/cryptocred/cc_structure.py.new` | HOLD | 20/20 live | run_all_tests | Same as above |
| `backtest/layers/extract_nuc_files.py.new` | HOLD | needs spec test | run_all_tests | Spec-derived test NOT written; gate blocks |
| `backtest/layers/run_t055.py.new` | HOLD | 22 stub | run_all_tests | Awaits 0989; will add funding logic |
| `backtest/layers/test_run_t055.py.new` | HOLD | 22 stub | run_all_tests | Awaits 0989 |

**Status Markers:**
- **HOLD:** Gated; passed edge tests; awaiting promotion decision
- **PENDING NUC:** Awaiting worker reply (0989)

---

## Research Pending (Not Yet Staged)

| Task | Inputs | Status | Owner | Notes |
|------|--------|--------|-------|-------|
| T058 Broken Extremes | T058_BROKEN_EXTREMES.md research | Research doc DONE, decisions OPEN | Operator | Needs: history fetch strategy, hedge timing rules |
| T054 US Session / Correlation / News | Chat research | Not started | — | Impact: understand BTC intraday volatility drivers |
| T053 Two-Account Hedge | Chat research | Not started | — | Impact: leverage sub-accounts to run more layers |

---

## In-Flight NUC Queue

**Status (as of 2026-10-05 ~04:00 IST):** 0989 running, 107-111 (Fabio extractions) queued.

When 0989 lands:
1. Hourly check auto-gates it (step 5b: turn_of_candle tests)
2. Promote if PASS
3. Gate blocks run_all_tests --quick step 5 (green once 0989 is promoted)
4. T055 backtest unblocked (Q2)

---

## Gate Status

| Gate | Status | Files | Expected |
|------|--------|-------|----------|
| `run_all_tests --quick` | ✅ PASS (except step 5b) | All non-backtest | ✅ Green once 0989 lands |
| step 5b (turn_of_candle) | ⏳ BLOCKED on 0989 | `test_turn_of_candle.py` | Awaits 0989 reply |
| Backtest (full) | ✅ PASS (L1 baseline done) | bt_*, layers/* | 🔄 Re-run after each promotion |
| Testnet chain (14/14) | ✅ PASS | execution/ + auto_trader | ✅ Green; re-run after exec changes |

---

## Key Dependencies

```
0989 (NUC Turn-of-Candle reply) 
  ↓ (promote on hourly check PASS)
Turn-of-Candle gate
  ↓
run_t055.py promotion
  ↓
T055 C1/C2/C3 backtest (Q2)
  └→ FUNDING logic required before "pass"

Fabio escalation (promoted)
  ↓
Fabio backtest driver validation
  ↓
Fabio L1 report (Q3)

082 re-split & repack
  ↓
082r/083/084 NUC queue
  ↓
Formula audit verification
  ↓
FORMULAS.md corrections + tests

Tick modules 091-093 (promoted)
  ↓
Full-history tier computation (Q6)
  ↓
tiers.json committed
  ↓
Live tick flags validated
```

---

## Handoff to Cloud Sessions

For any cloud session assigned backtest work:

1. **Read this pipeline first.** Status updates after each promotion.
2. **Do NOT edit .new files in place.** Work goes into the queue as specs (WORKER_ROADMAP.md section 2).
3. **Gate every promotion:** run_all_tests --quick + edge tests (NEXT_SESSION_PLAN.md section 5).
4. **Commit pattern:** one commit per completed task, trailer `MTS-Session: <ID>`, fast-track only.
5. **Report format:** 25 lines or fewer per task; cite spec and test results.

---

## Open Questions for Operator

(From NEXT_SESSION_PLAN.md section 9, still unanswered)

- **Q1:** Layer bracket 1% stop / 2% target / 100 USD for every layer — or per-layer from backtests?
- **Q2:** Sub-accounts per layer family (one slot/layer) — needed if layers block Tom on testnet?
- **Q3:** Layers with "no edge" (CryptoCred, RSI cross) — keep sampling or disable?
- **Q4:** Daily-loss cap 500 USD on testnet — or adjust?

---

## Metrics & Readiness

| Milestone | Status | Evidence |
|-----------|--------|----------|
| **R1 Execution math** | ✅ DONE | 08f5ea0, 61e55f3 |
| **R2 Full gate** | ✅ PASS (except step 5b) | run_all_tests --quick green |
| **R3 Testnet** | ✅ PASS 14/14 | testnet_runs/ft2_run_2026-09-29_*.log |
| **R4 L6** | ✅ DONE (part 2 deferred) | breach check still runs after re-arm |
| **R5 Layers + formula audit** | 🔄 PARTIAL | Layers done, 082 blocked, Q4 queue |
| **R6 Backtest baseline** | ✅ DONE | BACKTEST_L1_REPORT.md |
| **Alerts (live)** | ✅ LIVE (alert-only) | 085/086 promoted, runner PID 20048 |

---

## Reference Files

- `MyTradingSys/research/STATUS.md` — Current git/queue/process status
- `MyTradingSys/research/fast_track_2026-09-27/WORKER_ROADMAP.md` — Worker tier routing + full backlog
- `MyTradingSys/research/fast_track_2026-09-27/SUPERVISOR_LOG.md` — Session history + decisions
- `MyTradingSys/research/fast_track_2026-09-27/NEXT_SESSION_PLAN.md` — Active queue + context
- `MyTradingSys/system/CLOUD_INBOX.md` — Cloud session handoffs
- `MyTradingSys/backtest/layers/FORMULAS.md` — Canonical formula definitions
- `Dumps/workers/NUC-QUEUE/specs/` — Active NUC task specs
- `MyTradingSys/execution/auto_trader_config.json` — Live auto-trader config

---

**Last updated:** 2026-10-05 16:50 UTC  
**Next update:** When 0989 lands or new NUC queue status available
