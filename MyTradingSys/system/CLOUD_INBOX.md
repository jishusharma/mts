# CLOUD INBOX - tasks for Cloud sessions

Cloud sees only pushed git refs, so this file is the only way to hand it work. The desktop appends a note,
commits and pushes; the Cloud session reads it at boot, and after acting records the note in its session
record (MyTradingSys/system/sessions/) with the resulting commit, then removes the note here.
Cloud takes offline work only (SURFACE_POLICY.md section 1); anything needing local reach goes back to SUP.
Append notes below the line, one per bullet:
`- 2026-09-30 22:30 IST | from: <session ID> | <task> | done when: <observable result>`

---
- 2026-10-01 16:33 UTC | from: MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio | revalidate + extract round 2 | done when: all deliverables committed (W3 and 5.4 not done as specified, see REVALIDATION_ACTIONS_2026-10-01.md; no note addressed to this session was present, none removed)
- 2026-10-01 19:00 UTC | from: MTS-2026-10-01-1858Z-CLD-BLD-two-cores | two cores readiness + scaffold | done when: TWO_CORES_READINESS committed
- 2026-10-01 19:00 UTC | from: MTS-2026-10-01-1858Z-CLD-BLD-two-cores | QUEUE (budget gate, fix pass skipped): stage smallest fixes for top-5 in TWO_CORES_READINESS_2026-10-01.md (book_imbalance 0.0 first; fail-first test) | done when: .new files + acceptance checks committed; claim execution/ or layers/alerts/ in SUPERVISOR_LOG first
