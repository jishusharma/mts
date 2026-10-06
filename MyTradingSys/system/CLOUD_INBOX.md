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
- 2026-10-06 14:50 UTC | from: CLD-BLD-cbp-trade-inputs (project thread "Wire CBP trade inputs into MTS") | CBP->MTS channel: CBP stays a separate producer (decided 2026-09-30, BUGS B112); built queue/cbp_adapter.py + cbp_contract_v1.schema.json + test_cbp_adapter.py (draft PR to fast-track). Desktop to do: (1) run `python MyTradingSys/queue/cbp_adapter.py <mts_queue>` once and check candidates/cbp_candidates.jsonl; (2) DSA to register a tracked item + BUGS row (cloud may not edit registries); (3) queue path: operator says CBP is at C:\Users\E-ngineers\IdeaProjects\CryptoScrapper (matches consumer.py default); DSA_SESSION_PROMPT's F:\CryptoScrapper is stale, DSA to correct it; (4) next step is backtesting each analyst rule before any candidate may become order-eligible | done when: item registered, adapter run on the real queue, path confirmed
