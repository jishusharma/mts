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
- 2026-10-01 19:40 UTC | from: MTS-2026-10-01-1916Z-CLD-BLD-two-cores-int | HANDOFF (budget stop): finish waves 1, 2, 4 and the deliverables per research/TWO_CORES_INT_HANDOFF_2026-10-01.md; wave 3 done (febe8e5); the 19:00 QUEUE note above stays until wave 1 is accepted | done when: checkpoints 1, 2, 4 committed, gates reported, handoff doc tasks 1-5 closed
- 2026-10-05 15:10 UTC | from: MTS-2026-10-05-1500Z-APP-ANA-operator-asks | T064 Tom+Fabio quote extract (TF choice, confirmation, stop runs, retrace depth) per items/T064_timeframe_selection_confirmation.md | done when: research/T064_TF_CONFIRMATION_EXTRACT.md committed, verify_extract_quotes.py green
- 2026-10-05 15:10 UTC | from: MTS-2026-10-05-1500Z-APP-ANA-operator-asks | T065 LazyBear survey per items/T065_lazybear_survey.md | done when: research/T065_LAZYBEAR_SURVEY.md committed with shortlist of 5 or fewer
- 2026-10-05 15:10 UTC | from: MTS-2026-10-05-1500Z-APP-ANA-operator-asks | T063 event study (start after runtime/oi_live backfill is pushed, or fetch public 5m openInterestHist read-only) per items/T063_stop_run_oi_flush_signature.md | done when: pre-registered report committed
- 2026-10-05 15:10 UTC | from: MTS-2026-10-05-1500Z-APP-ANA-operator-asks | G1/M1/M2 replay 10-04/05 (next node beyond nearest; sourced R:R floor) per research/MARKET_ANALYSIS_2026-10-05.md section 6 P1 | done when: replay report committed
- 2026-10-05 15:10 UTC | from: MTS-2026-10-05-1500Z-APP-ANA-operator-asks | T067 alert spec + tests, AFTER T063/T064 land | done when: spec + failing-first tests committed
