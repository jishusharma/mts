# MTS Backtest Pipeline — Complete Task Registry & Assignment

**Generated:** 2026-10-05 UTC | Cloud Session Ready  
**Branch:** cloud/work | **Status:** OPERATIONAL  
**Total Tasks:** 31 (5 in-flight, 12 queued, 8 blocked, 6 pending decision)

---

## EXECUTIVE SUMMARY

The MTS backtest system has 31 actionable tasks across 4 priority tiers. This document consolidates:
- **Staged work** (16 `.new` files, 56-79h old)
- **Worker roadmap** (15 items, T0-T4 routed)
- **Two cores integration** (4 waves, 1 complete, 2 partial, 1 waiting)
- **Cloud inbox tasks** (3 active notes)

**Cloud Session Role:** Verify, gate, and promote staged work. Do NOT edit files in place; stage all work as `.new`.

---

## 1. STAGED FILES — READY FOR GATE

All 16 files are on disk, uncommitted. **Action:** Verify against spec, gate, promote.

| # | File | Size | Age | Status | Tier | Gate | Notes |
|---|---|---|---|---|---|---|---|
| S1 | `backtest/layers/consensus/writer.py.new` | 7.5K | 3d | READY | T2 | backtest | Layer 9 output writer |
| S2 | `backtest/layers/consensus/test_writer.py.new` | 17K | 3d | READY | T2 | backtest | Tests writer; 69 new + 2 boundary |
| S3 | `backtest/layers/fabio/v3/signals.py.new` | 19K | 3d | READY | T3 | backtest+fabio | Fabio core signals |
| S4 | `backtest/layers/fabio/v3/models.py.new` | 24K | 3d | READY | T3 | backtest+fabio | Engine models; MISSING __init__.py |
| S5 | `backtest/layers/fabio/v3/engine.py.new` | 9.3K | 0h | READY | T3 | backtest+fabio | Verdict logic; NS-grid REQUIRED |
| S6 | `backtest/layers/fabio/v3/manage.py.new` | 12K | 3d | READY | T3 | backtest+fabio | Trade management |
| S7 | `backtest/layers/fabio/v3/fill.py.new` | 2.0K | 3d | READY | T3 | backtest+fabio | Fill logic |
| S8 | `backtest/layers/fabio/v3/costs.py.new` | 3.8K | 3d | READY | T3 | backtest+fabio | Cost model |
| S9 | `backtest/layers/fabio/v3/day_gates.py.new` | 7.8K | 3d | READY | T3 | backtest+fabio | Daily limits |
| S10 | `backtest/layers/fabio/v3/__init__.py.new` | 1.4K | 3d | READY | T2 | backtest | Package init |
| S11 | `backtest/layers/fabio/v3/tests/test_signals.py.new` | 8.9K | 0h | READY | T3 | backtest | Signal unit tests |
| S12 | `backtest/layers/fabio/v3/tests/test_models_engine.py.new` | 9.5K | 0h | READY | T3 | backtest | Model/engine tests |
| S13 | `backtest/layers/fabio/v3/tests/test_manage.py.new` | 7.4K | 0h | READY | T3 | backtest | Manage tests |
| S14 | `backtest/layers/fabio/v3/tests/test_costs_fill.py.new` | 4.0K | 0h | READY | T3 | backtest | Cost/fill tests |
| S15 | `backtest/layers/fabio/v3/tests/test_day_gates.py.new` | 5.3K | 0h | READY | T3 | backtest | Day gate tests |
| S16 | `backtest/layers/rsi/observation.py.new` | 7.7K | 3d | READY | T2 | backtest | RSI observation layer |

**Promotion Path:** VERIFY (S1-S2 first, then S3-S10, then S11-S16) → GATE (`run_all_tests.py --quick`) → COMMIT

---

## 2. WORKER ROADMAP ITEMS — TIER-ROUTED

Backtest items from WORKER_ROADMAP.md with routing tier and gate requirements.

| # | Item | Description | Tier | Status | Gate | Blocker |
|---|---|---|---|---|---|---|
| W1 | 023 PBO band test | Aggregate 20-seed PBO band; parametric study | T1 | queued NUC | backtest | - |
| W2 | 024 fix expectations | Fix 2 wrong expectations in test_ref_pbo | T1→T2 | queued NUC | backtest | after W1 |
| W3 | 025 L7 unused imports | daily_loss_guard: unused imports, missing pnl_usd | T1→T2→T4 | queued | execution | after W1,W2 |
| W4 | 026 position_manager timer | Switch to time.monotonic(); check fake clocks | T1→T2→T4 | queued | execution | after W1,W2 |
| W5 | 020/021 ref_pbo/ladder | Reference PBO / ladder reply verification | T2 | triage | backtest | - |
| W6 | bt_* promotion | Promote data/engine/ladder/stats + tests | T2→T4 | waiting | backtest | after W1,W2,W5 |
| W7 | M7 soak_report | Flag unresolved orders on closed/halted plans | T1→T3 | queued | execution | - |
| W8 | L5 executor deadline | Sleep after cancel pass in hot loop | T1 | queued | execution | - |
| W9 | M8 docstrings | Document single-plan-only in docstrings | T1 | queued | doc | - |
| W10 | M4 HALT re-check | Before every order-creating call | T3→T4 | waiting | execution+testnet | after W3,W4 |
| W11 | L1/L2 G2/sweep | Entry fills explained; sweep on OrderStateUnknown | T3→T4 | waiting | execution+testnet | - |
| W12 | M2 HALT_DAILY_LOSS | Contract decision: operator deletes or exists? | T4 | decision | execution | - |
| W13 | L3/L6 PnL counts | B079 post-fill breach; PnL deposits; breached never resets | T4 | waiting | - | deferred |
| W14 | Research stale files | 20h old BUGS.md.new, qwen_raw_*.new | T2 | diff+delete | doc | - |
| W15 | test_deadline/stop | Rewrite 021 ladder cross-check by hand | T3 | waiting | backtest | after W5 |

**Priority Order:** W1→W2→W5→W6 (backtest), then W3→W4→W10→W11 (execution+testnet).

---

## 3. TWO CORES INTEGRATION WAVES

State per wave from TWO_CORES_INT_HANDOFF_2026-10-01.md.

| Wave | Module | State | Checkpoint | Action | Blocker |
|---|---|---|---|---|---|
| 1 | Readiness fix pass | PARTIAL, unreviewed | none (WIP aa8933a) | Review W1 diffs; fail-first; gate tree+overlay | TWO_CORES_FIX_PASS missing |
| 2 | Fabio v3 core | PARTIAL, unreviewed | none (WIP aa8933a) | Finish v3/ (models, engine, __init__, tests, README); gate | S3-S10 blocked |
| 3 | Consensus writer + RSI | DONE, verified | febe8e5 | Spot-check; boundary test 81-101 | none |
| 4 | Switchability spec | DONE, spot-checked | this commit | Optional: review 21 open items D1-D6 | none |

**Wave 1 Staged Files (unreviewed):**
- `runtime/math_object_builder.py.new`
- `tests/test_book_imbalance_nodata.py.new`
- `scripts/dev/alert_rate_check.py.new` + test
- `execution/auto_trader.py.new` + test
- `runtime/test_quad_classify.py.new`
- `runtime/test_regime_classifier.py.new`
- `tests/java/MarketDataSnapshotTest.java.new`
- `tests/test_proof_direction.py.new` (UNEXPECTED — diff vs original)
- `research/core_readiness_2026-09-27/harness/proof_direction_cases.py.new` (UNEXPECTED)

**Action:** Diff each .new vs original; justify or drop unexpected files.

---

## 4. CLOUD INBOX — ACTIVE NOTES

Tasks handed to this session via CLOUD_INBOX.md.

| Date | From | Task | Done When | Status |
|---|---|---|---|---|
| 2026-10-01 16:33 UTC | revalidate-tom-fabio | Revalidate + extract round 2 | all deliverables committed | NOT addressed (no note) |
| 2026-10-01 19:00 UTC | two-cores | TWO_CORES_READINESS + scaffold | committed | IN PROGRESS |
| 2026-10-01 19:00 UTC | two-cores | QUEUE: stage smallest fixes top-5 (book_imbalance first) | .new files + acceptance checks committed | IN PROGRESS |
| 2026-10-01 19:40 UTC | two-cores-int | HANDOFF: finish waves 1,2,4 + deliverables | checkpoints 1,2,4 committed | IN PROGRESS |

**Completion Criteria (per SURFACE_POLICY.md):**
- Remove note from CLOUD_INBOX.md once task is done
- Record result in session record (MyTradingSys/system/sessions/<ID>.md)
- Commit with co-author line

---

## 5. GATE REQUIREMENTS — EXACT COMMANDS

### Offline Gates (run on staged sandbox, never live tree first)

**All tests:**
```bash
python scripts/dev/run_all_tests.py --quick
# Exit 0 = green. Baseline (without W1-W2): Step 3c fails (gitignored plans/journal/halt_history)
```

**Execution layer only:**
```bash
python scripts/dev/run_staged_tests.py MyTradingSys/execution MyTradingSys/execution/testnet/offline \
  -- test_daily_loss_guard test_daily_loss_monitor test_gh_executor_offline \
     test_gh_retry_offline test_halt_preflight_offline test_kill_switch \
     test_risk_guard test_s1_cap_offline test_s3_unprotected_offline \
     test_s6_orphan_offline test_soak_report test_fix3_offline
# → 116 OK
```

**Backtest layer only:**
```bash
python -m unittest discover MyTradingSys/backtest/bt -p "test_*.py" -v
```

### Testnet Gate (T2 runs; TESTNET ONLY, never mainnet)

**Prerequisites:** HALT and HALT_DAILY_LOSS absent; account flat.

```bash
python scripts/dev/probe_account_summary.py
python scripts/dev/run_testnet_suite.py          # 6/6
python scripts/dev/run_testnet_suite_g1g2.py    # 6/6 + 4/4
python scripts/dev/run_testnet_suite_ft2.py     # + 4/4
```

### Promotion Checklist

1. **Backup:** `cp X.new .pre_<tag>_X` (all .new files in batch)
2. **Rename:** `mv X.new X` (rename .new to live)
3. **Gate:** Run exact gate command (all tests pass)
4. **Commit:** One commit per batch; include fail-first run evidence
5. **Push:** `git push -u origin cloud/work` (cloud branch only)

---

## 6. TIER ROUTING & ESCALATION

### Tier Definitions (WORKER_ROADMAP.md)

| Tier | Who | Cost | Speed | Use For | Never |
|---|---|---|---|---|---|
| T0 | Script | ~0 | - | Counts, gates, static checks | - |
| T1 | Qwen 30B NUC | free | 4.4 tok/s | Small edits, reference implementations | Being only reviewer of safety code |
| T2 | Haiku subagent | low | - | Tests, gates, triage, mechanical edits | Design decisions |
| T3 | Sonnet subagent | medium | - | Writing tests, mutation checks, medium edits | Final safety sign-off |
| T4 | Opus (cloud) | high | - | Specs, contract decisions, diffs of safety code, final gate | Reading whole files a lower tier summarised |

### Escalation Rules

- **Escalate after 2 FAILs** at current tier
- **Always escalate:** stop/flatten/HALT paths → T4 review
- **Safety code:** T3 + test that fails without change, T4 review
- **Large changes:** T3 mutation check, T4 decision

---

## 7. ASSIGNMENT LOGIC FOR CLOUD SESSION

**Role:** Haiku (T2) gate runner. Follow this order:

### Phase 1: Verify Staged Files (S1-S16)

1. **Pair test + code** (S2 with S1, S11-S15 with S3-S9)
2. **Copy .new to sandbox** (don't edit in place)
3. **Run test on sandbox** (python -m unittest test_writer.py, etc.)
4. **Report table:** verdict | pass/fail | bug-in-impl or bug-in-test
5. **Escalate on FAIL:** report table + recommendation to cloud session (Opus)

### Phase 2: Wave 1 Diffs (TWO_CORES_INT)

1. **Diff each .new vs original** (e.g., `diff -u runtime/math_object_builder.py runtime/math_object_builder.py.new`)
2. **Check smallest change:** no unnecessary edits
3. **Justify unexpected files** (proof_direction.py.new, proof_direction_cases.py.new)
4. **Fail-first:** overlay TEST only → must FAIL; test + fix → PASS
5. **Report:** TWO_CORES_FIX_PASS_2026-10-02.md (with failing run)

### Phase 3: Full Gate

1. **Tree gate:** `python scripts/dev/run_all_tests.py --quick` (baseline state)
2. **Overlay gate:** Apply all S1-S16 + W1 staged files, re-run
3. **Testnet gate:** (after Phase 1-2 pass) run suite on testnet
4. **Report:** GATE_REPORT_2026-10-05.md (all steps, pass/fail)

### Phase 4: Promotion

1. **Backup loop:** For each batch, `cp X.new .pre_TAG_X`
2. **Rename:** `mv X.new X`
3. **Re-gate:** Run full gate on renamed tree (must PASS)
4. **Commit:** One commit per 5-file batch; include evidence
5. **Push:** `git push -u origin cloud/work`
6. **Record:** Update CLOUD_INBOX.md (remove note if done)

---

## 8. QUICK START CHECKLIST

### Before You Begin

- [ ] Clone repo (or resume on branch `cloud/work`)
- [ ] Read STATUS.md (refresh project state)
- [ ] Read SUPERVISOR_LOG.md (supervisor decisions)
- [ ] Verify `.new` files present (16 files, sizes match section 1)

### Execution Order

1. **Phase 1: Verify S1-S16** (2-3h)
   - [ ] S1-S2 (consensus writer) → report table
   - [ ] S3-S10 (Fabio v3 core) → report table
   - [ ] S11-S15 (Fabio tests) → report table
   - [ ] S16 (RSI observation) → report table

2. **Phase 2: Wave 1 Diffs** (1h)
   - [ ] Diff 9 Wave 1 .new files vs originals
   - [ ] Justify or drop unexpected files
   - [ ] Fail-first test + fix for each

3. **Phase 3: Full Gate** (2-3h)
   - [ ] Baseline gate (tree state)
   - [ ] Overlay gate (S1-S16 applied)
   - [ ] Testnet gate (if Phase 1-2 pass)

4. **Phase 4: Promotion** (1h)
   - [ ] Backup + rename S1-S5 batch
   - [ ] Re-gate on renamed tree
   - [ ] Commit checkpoint 1 (S1-S5 + evidence)
   - [ ] Backup + rename S6-S10 batch
   - [ ] Re-gate on renamed tree
   - [ ] Commit checkpoint 2 (S6-S10 + evidence)
   - [ ] (S11-S16 follow same pattern)

5. **Phase 5: Deliverables** (30min)
   - [ ] Update sessions/<ID>.md (14 fields)
   - [ ] Remove notes from CLOUD_INBOX.md
   - [ ] Update 03_FILE_INDEX.md (new files + SIZE)
   - [ ] Add entry to SUPERVISOR_INBOX.md

6. **Phase 6: Final Push**
   - [ ] `git add -f` every promoted file (*.new is gitignored)
   - [ ] `git push -u origin cloud/work`
   - [ ] Record session in system/sessions/

---

## 9. KNOWN ISSUES & DECISIONS PENDING

### Findings from TWO_CORES_INT_HANDOFF

| Issue | Impact | Action |
|---|---|---|
| Fabio cannot trade live (missing footprint/big-trade columns) | Backtest only | Supervisor decision |
| execution/ may not import backtest.layers | Design constraint | auto_trader hook owner unknown |
| snapshot_id has no owner | Missing | Add to math_object_builder.py |
| RSI block holds last alert per TF (stale between events) | 1m, 3m, 4h, 1d no source | Design decision |
| MyTradingSys/runtime/test_*.py not in run_all_tests.py | Gate gap | pytest vs unittest; gate decision needed |
| auto_trader TF_SECONDS at :48 not :47 | Timing skew | Document or fix |
| Wave 1 test expectations may need rewrite | W5 triage blocker | After ref_pbo/ladder verified |

### Deferred Tasks

- **L6 part 2** (P/L from transaction log): deferred for testnet; must build before mainnet
- **Malkan rules verbatim extract**: research/malkan_rsi_2026-09-28 only; multi-TF composition deferred
- **TF-B5 native-1d real-data gate**: not yet tested on live data

---

## 10. REFERENCE: GATE REPORT TEMPLATE

Create GATE_REPORT_2026-10-05.md after Phase 3 with this structure:

```markdown
# GATE REPORT 2026-10-05

## Phase 1: Staged Files (S1-S16)

| File | Test | Verdict | Pass/Total | Issue |
|---|---|---|---|---|
| S1 consensus/writer.py | test_writer.py | PASS | 71/71 | - |
| S2 consensus/test_writer.py | (inline) | PASS | - | - |
| S3 fabio/v3/signals.py | test_signals.py | PASS | 8/8 | - |
| ... | ... | ... | ... | ... |

## Phase 2: Wave 1 Diffs

| File | Diff Size | Issue | Verdict |
|---|---|---|---|
| runtime/math_object_builder.py.new | 12 lines | smallest change? | PASS |
| tests/test_proof_direction.py.new | (NEW) | justify? | UNEXPECTED — drop |
| ... | ... | ... | ... |

## Phase 3: Full Gate

- Baseline (tree): `run_all_tests.py --quick` → PASS (Step 3c fails, expected)
- Overlay (S1-S16 applied): → PASS
- Testnet suite (6/6): → PASS
- Testnet G1/G2 (4/4): → PASS

## Phase 4: Promotion

- Checkpoint 1 (S1-S5 + evidence): <commit-hash>
- Checkpoint 2 (S6-S10 + evidence): <commit-hash>
- Checkpoint 3 (S11-S16 + evidence): <commit-hash>

## Deliverables

- CLOUD_INBOX.md updated (notes removed)
- sessions/<ID>.md created (14 fields + commit hashes)
- 03_FILE_INDEX.md refreshed (16 new files + SIZE header)
- SUPERVISOR_INBOX.md entry added

## Blockers

None (all gates green).

```

---

## APPENDIX: FILE MANIFEST & SIZES

```
S1  backtest/layers/consensus/writer.py.new                    7.5K
S2  backtest/layers/consensus/test_writer.py.new              17.0K
S3  backtest/layers/fabio/v3/signals.py.new                   19.0K
S4  backtest/layers/fabio/v3/models.py.new                    24.0K
S5  backtest/layers/fabio/v3/engine.py.new                     9.3K
S6  backtest/layers/fabio/v3/manage.py.new                    12.0K
S7  backtest/layers/fabio/v3/fill.py.new                       2.0K
S8  backtest/layers/fabio/v3/costs.py.new                      3.8K
S9  backtest/layers/fabio/v3/day_gates.py.new                  7.8K
S10 backtest/layers/fabio/v3/__init__.py.new                   1.4K
S11 backtest/layers/fabio/v3/tests/test_signals.py.new        8.9K
S12 backtest/layers/fabio/v3/tests/test_models_engine.py.new   9.5K
S13 backtest/layers/fabio/v3/tests/test_manage.py.new         7.4K
S14 backtest/layers/fabio/v3/tests/test_costs_fill.py.new     4.0K
S15 backtest/layers/fabio/v3/tests/test_day_gates.py.new      5.3K
S16 backtest/layers/rsi/observation.py.new                     7.7K

TOTAL: 137.6K staged, ready to verify.

W1-W15: Worker roadmap items (external NUC queue or local).
Wave 1-4: Two cores integration (9 .new files + decisions).

Grand total: 31 tasks (16 staged, 15 roadmap, 4 waves).
```

---

## Next Steps (for Cloud Session)

1. Read this document fully
2. Clone/resume branch `cloud/work`
3. Start Phase 1: Verify S1-S16 (run tests in sandbox)
4. Follow phases 2-6 sequentially
5. Commit + push when each checkpoint passes gate
6. Update CLOUD_INBOX.md and session record when done

**Estimated duration:** 6-8h (with testnet gate included).

---

**Document Version:** 1.0  
**Last Update:** 2026-10-05 UTC  
**Maintainer:** Cloud Session (Haiku T2 gate runner)
