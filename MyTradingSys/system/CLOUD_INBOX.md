# CLOUD INBOX - tasks for Cloud sessions

Cloud sees only pushed git refs, so this file is the only way to hand it work. The desktop appends a note,
commits and pushes; the Cloud session reads it at boot, and after acting records the note in its session
record (MyTradingSys/system/sessions/) with the resulting commit, then removes the note here.
Cloud takes offline work only (SURFACE_POLICY.md section 1); anything needing local reach goes back to SUP.
Append notes below the line, one per bullet:
`- 2026-09-30 22:30 IST | from: <session ID> | <task> | done when: <observable result>`

---
- 2026-10-01 19:00 UTC | from: MTS-2026-10-01-1858Z-CLD-BLD-two-cores | QUEUE (budget gate, fix pass skipped): stage smallest fixes for top-5 in TWO_CORES_READINESS_2026-10-01.md (book_imbalance 0.0 first; fail-first test) | done when: .new files + acceptance checks committed; claim execution/ or layers/alerts/ in SUPERVISOR_LOG first | STATUS 2026-10-06 (MTS-2026-10-06-2122Z-APP-COO-registry-fix): OPEN. Landed: #1 book_imbalance 0.0 no-data (math_object_builder.py:449,465; 2f40ea5, 0c34a2d), #5 quad_classify/regime_classifier tests (tests/test_quad_classify.py, test_regime_classifier.py). Not landed: #2 Fabio v3 core unverified (backtest/layers/fabio/v3/, 71b9d24 UNVERIFIED), #3 consensus writer staged only (B125 OPEN), #4 mts.ps1 has no orphan_watchdog verb
- 2026-10-01 19:40 UTC | from: MTS-2026-10-01-1916Z-CLD-BLD-two-cores-int | HANDOFF (budget stop): finish waves 1, 2, 4 and the deliverables per research/TWO_CORES_INT_HANDOFF_2026-10-01.md; wave 3 done (febe8e5); the 19:00 QUEUE note above stays until wave 1 is accepted | done when: checkpoints 1, 2, 4 committed, gates reported, handoff doc tasks 1-5 closed | STATUS 2026-10-06 (MTS-2026-10-06-2122Z-APP-COO-registry-fix): OPEN. Checkpoint 4 committed (916a15e); MTS_LAUNCHER_SPEC_2026-10-02.md exists. Not done: task 1 (TWO_CORES_FIX_PASS_2026-10-02.md absent), task 2 (v3 acceptance run), tasks 4-5 not evidenced
