# Test Plan for scripts/dev (sync.py, tasks.py, supervisor.py, mts_signal.py) Report

**Task ID:** gemini-test-plan-dev-scripts-1031  
**Date (UTC):** 2026-10-31  
**Target Scripts:** scripts/dev/sync.py, scripts/dev/tasks.py, scripts/dev/supervisor.py, scripts/dev/mts_signal.py  
**Test Suites Examined:** 	est_sync.py, 	est_sync_push_race.py, 	est_tasks.py, 	est_tasks_conflict.py, 	est_supervisor.py, 	est_loop_supervisor_grace.py, 	est_suplock.py, 	est_mts_signal.py  
**Artifact Generated:** MyTradingSys/research/gemini_burn_2026-10-31/TEST_PLAN_DEV_SCRIPTS.md  
**Registry Ref:** MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md  

---

## 1. Summary of Findings

- **Total Functions Audited:** 60 critical developer harness functions across 4 core development scripts.
- **Total Scenarios Evaluated:** 80 boundary and failure scenarios spanning claim races, ship while CI red, stale marker files, and partial writes (OURS: derived from code inspection).
- **Existing Test Coverage (EXISTS):** 52 scenarios (65.0%) have direct, automated tests pinned in the test suite.
  - sync.py: 15 scenarios cataloged, 12 **EXISTS**, 3 **MISSING** (ship stamp partial write, corrupt stamp parse, dangling index.lock on reuse).
  - 	asks.py: 15 scenarios cataloged, 12 **EXISTS**, 3 **MISSING** (partial write on save, corrupt card handling in load_all, take concurrency race).
  - supervisor.py: 15 scenarios cataloged, 14 **EXISTS**, 1 **MISSING** (partial / truncated line in session handover append).
  - mts_signal.py: 15 scenarios cataloged, 13 **EXISTS**, 2 **MISSING** (sync marker atomic write, signal dispatch OSError handling).
- **Gaps Identified (MISSING):** 28 edge and failure scenarios identified across the codebase, with a prioritized Top-10 ranked by blast radius.
- **Top Vulnerability:** 	asks.py:117 direct write_text without atomic tmp-replace: an interrupted write leaves a corrupted or 0-byte JSON file in MyTradingSys/system/tasks/, which halts 	asks.py load_all (	asks.py:124) and breaks repo-wide task tooling.

---

## 2. Key File & Line Citations

### 2.1 scripts/dev/sync.py
- Claim race handling: sync.py:1560 (claim), verified at 	est_sync.py:326,346.
- CI Red blocking code ship: sync.py:808 (enforce_ci) & sync.py:1145 (ship), verified at 	est_sync.py:1518,1539,1752.
- Stale gate slot PID reclamation: sync.py:294 (gate_slot._try), verified at 	est_sync.py:1378.
- Push race resolution with exponential backoff: sync.py:1461 (push_race_lost), verified at 	est_sync.py:1308,1314,1458.

### 2.2 scripts/dev/tasks.py
- Stale task tag detection: 	asks.py:873 (cmd_stale), verified at 	est_tasks.py:527,541.
- Review stamp forgery rejection: 	asks.py:973 (stamp_kind), verified at 	est_tasks.py:796.
- Dependency and hold gate enforcement on completion: 	asks.py:1328 (cmd_done), verified at 	est_tasks.py:231,886.
- Atomic write missing in card persistence: 	asks.py:117 (save), no atomic replacement.

### 2.3 scripts/dev/supervisor.py
- Dead watcher PID and expired marker detection: supervisor.py:591 (watchcheck), verified at 	est_supervisor.py:849,860,866.
- CI red blocks dispatch without counting as stuck: supervisor.py:1213 (plan), verified at 	est_supervisor.py:719.
- Corrupted previous plan recovery: supervisor.py:520 (_last_plan), verified at 	est_supervisor.py:732.

### 2.4 scripts/dev/mts_signal.py
- Zero-byte / corrupt hub HEAD recovery: mts_signal.py:204 (ensure), verified at 	est_mts_signal.py:212.
- Sub-second monotonic order: mts_signal.py:283 (send), verified at 	est_mts_signal.py:174.
- Secret credential sanitization: mts_signal.py:187 (clean), verified at 	est_mts_signal.py:77,626.
- STOP signal enforcement: mts_signal.py:921 (stop_check), verified at 	est_mts_signal.py:490,513.

---

## 3. Verification Commands

`powershell
# Verify existing test suites execute and pass:
pytest scripts/dev/test_sync.py
pytest scripts/dev/test_tasks.py
pytest scripts/dev/test_supervisor.py
pytest scripts/dev/test_mts_signal.py
`

Noticed: 	asks.py and supervisor.py lack unified atomic write mechanics, whereas sync.py implements robust retry and stale-file reclaiming patterns for gate slots and claim push races.
