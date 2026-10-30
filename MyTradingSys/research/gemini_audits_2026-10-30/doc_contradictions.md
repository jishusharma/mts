10 pairs beyond D11 section 4.

# Document Contradiction Scan (v1 Plan vs Operations vs System Rules)

This audit scans six core documentation files for rule pairs that cannot both be followed (freeze lists, worker types, lanes, caps, and lab hosts/runners), recording facts with `file:line` citations and identifying which rule is newer. D11 section 4 enumerates 9 known pairs; the 10 pairs documented below are additional direct contradictions discovered across the corpus.

## Summary Table

| pair | file:line A | file:line B | which newer |
|---|---|---|---|
| 1 | SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D7_ROADMAP.md:8-9` ("Frozen for the whole v1 (until the operator unfreezes) ... confluence between layers") | SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md:30` ("D4 slots: Levels Confluence (`lc-validation` after LC3 DEV says go)") | SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md` (2026-10-30 vs D7 2026-10-20) |
| 2 | SOURCED `MyTradingSys/system/WORKERS.md:21` ("Every worker card runs as an Agent (chained cards allowed).") | SOURCED `MyTradingSys/system/ROUTING.md:100` ("RU3 shot.py bundle (Eagle_Eyes) \| ru3-eagle-eyes-shot-py-bundle-evidence-p \| session / 25") | SOURCED `MyTradingSys/system/ROUTING.md` (2026-10-28 vs WORKERS.md 2026-10-27) |
| 3 | SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D8_OPERATIONS.md:26-28` ("Lanes collapse to three: Claude ... Codex ... Operator ... DSA/Gemini and the DeepSeek AIBridge lane are retired unless their rows drain in S0") | SOURCED `MyTradingSys/system/ROUTING.md:51` ("lane HAIKU/SONNET/OPUS: a Claude session or Agent ... lane CODEX: `codex_run.py` (GPT lab) or Gemini; lanes DSA*/JIS-NB: run cards, `desk.py assign` turns ready ones into desk rows") | SOURCED `MyTradingSys/system/ROUTING.md` (2026-10-28 vs D8 2026-10-20) |
| 4 | SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D7_ROADMAP.md:30` ("Three parallel stages, three worker sessions at most, one coordinator.") | SOURCED `MyTradingSys/system/WORKERS.md:38` ("Workers are background Agents (max 4 at once)") | SOURCED `MyTradingSys/system/WORKERS.md` (2026-10-27 vs D7 2026-10-20) |
| 5 | SOURCED `MyTradingSys/system/WORKERS.md:26-27` ("A session spawns **at most 5 Haiku Agents at a time**") | SOURCED `MyTradingSys/system/ROUTING.md:76` ("one-use Haiku Agent from the session that owns the task (max 5 at once; Pipeliner max 2)") | SOURCED `MyTradingSys/system/ROUTING.md` (2026-10-28 vs WORKERS.md 2026-10-27) |
| 6 | SOURCED `MyTradingSys/system/SUPER_SESSION.md:10` ("Any model may start any model (a Haiku coordinator may start Opus). The worker model is the card's `model` field; `opus` only when the operator names it or the card has `approved_by`.") | SOURCED `MyTradingSys/system/WORKERS.md:35-37` ("Opus is the tight exception ... (b) a session starts it only for a task card in lane OPUS with `approved_by` and `crucial` ... cited by id in the brief.") | SOURCED `MyTradingSys/system/WORKERS.md` (2026-10-27 vs SUPER_SESSION.md 2026-10-24 D1) |
| 7 | SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D8_OPERATIONS.md:29-30` ("Two pages: the decision page (questions with yes/no/change, one line per stage per week) and STATUS.md. Every other generated page stops being rebuilt; the artifacts rebuild branch is shipped once and then not maintained.") | SOURCED `MyTradingSys/system/SUPER_SESSION.md:87` ("Pages follow builds: `python scripts/dev/artifacts.py build`, then `artifacts.py stale`, then republish each STALE page over its url from the owning login (C = jishusharma1985 for its pages)") | SOURCED `MyTradingSys/system/SUPER_SESSION.md` (2026-10-26/30 vs D8 2026-10-20) |
| 8 | SOURCED `MyTradingSys/system/ANNOUNCEMENTS.md:46-48` ("DO-NOW GPT lab queue is idle; NUC keeps it busy ... Applies to: NUC super session. What: run the ready CODEX cards one at a time in this order: lab-data-pin-hash, lab-machine-checks-extra, lab-weight-enforce, lab-crossvendor-stage, lab-holdout-access-control, lab-formula-spec-text; then lab-planted-error-trial") | SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md:95-96` ("First wake, in this order: `get_usage` and `supervisor.py plan`; GPT lane (contradiction 5: claim, `codex_run.py tick`; signal b-230ce8 `ack done` once a run lands)") | SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md` (2026-10-30 vs ANNOUNCEMENTS.md A-20261018-3) |
| 9 | SOURCED `MyTradingSys/system/WORKERS.md:20-21` ("One-use Agent ... for size S or M with `est_turns` <= 30 (same cost per ship as a session; overrun p90 55, so the brief says 'stop at 40 turns and report', size S 20)") | SOURCED `MyTradingSys/system/SUPER_SESSION.md:26` ("'stop at 40 turns and report' (size S: 20)") vs SOURCED `MyTradingSys/system/WORKERS.md:26` ("Haiku for scoped work ... Brief = files + change + done check + 'stop at 15 turns and report'") | SOURCED `MyTradingSys/system/WORKERS.md:26` (2026-10-27 refinement vs WORKERS.md:20 / SUPER_SESSION:26) |
| 10 | SOURCED `MyTradingSys/system/ANNOUNCEMENTS.md:50-52` ("NUC (lab, GPT/Codex, Gemini/Antigravity, F:/MTS/data): lab cards, re-derivations, planted-error trial, retro-audit of past base results.") | SOURCED `MyTradingSys/system/ROUTING.md:74` ("CBP caption fetch for known analyst channels (`cbp_run.py`) \| any Claude machine (bug-youtube-gemini-only-rule-is-a-preference, 2026-10-27: Gemini-on-the-NUC was written as a limit, it is a preference)") | SOURCED `MyTradingSys/system/ROUTING.md` (2026-10-28 vs ANNOUNCEMENTS.md A-20261018-4) |

## Detailed Breakdown of Contradictions

### 1. Freeze on Confluence vs Active Stream B Funnel Slot
- **Sentence A**: SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D7_ROADMAP.md:8-9`: "Frozen for the whole v1 (until the operator unfreezes) ... confluence between layers".
- **Sentence B**: SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md:30`: "D4 slots: Levels Confluence (`lc-validation` after LC3 DEV says go) and CryptoCred 4h/1d; then A's picks".
- **Which Newer**: SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md` (dated 2026-10-30) is newer than `D7_ROADMAP.md` (dated 2026-10-20).
- **Conflict**: D7 strictly freezes "confluence between layers" across v1, whereas D11 explicitly schedules Levels Confluence (`lc-validation`) as the primary slot in Stream B.

### 2. Mandatory Agent Workers vs Session Workers Scheduled for Non-Interactive Cards
- **Sentence A**: SOURCED `MyTradingSys/system/WORKERS.md:21`: "Every worker card runs as an Agent (chained cards allowed)."
- **Sentence B**: SOURCED `MyTradingSys/system/ROUTING.md:100`: "RU3 shot.py bundle (Eagle_Eyes) | ru3-eagle-eyes-shot-py-bundle-evidence-p | session / 25".
- **Which Newer**: SOURCED `MyTradingSys/system/ROUTING.md` (changes up to 2026-10-28) is newer than `WORKERS.md` (2026-10-27).
- **Conflict**: WORKERS rule 3 dictates that all worker cards run as background Agents (sessions reserved only for interactive roles like Eagle_Eyes), whereas ROUTING.md's routed items table explicitly assigns `session / 25` to worker card `ru3-eagle-eyes-shot-py-bundle-evidence-p` and `session / 28` to `ru6-lab-guy-content-bound-review-receipt` (ROUTING.md:103).

### 3. Lane Collapse to 3 Lanes vs Active Routing Across 6+ Distinct Lanes
- **Sentence A**: SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D8_OPERATIONS.md:26-28`: "Lanes collapse to three: Claude (Sonnet default, Haiku mechanical, Opus by name), Codex (prepaid, cross-vendor reviewer and lab runner while its queue is below 8), Operator (eye-reads, decisions, keys). DSA/Gemini and the DeepSeek AIBridge lane are retired unless their rows drain in S0".
- **Sentence B**: SOURCED `MyTradingSys/system/ROUTING.md:51`: "lane HAIKU/SONNET/OPUS: a Claude session or Agent the coordinator starts (WORKERS.md); lane CODEX: `codex_run.py` (GPT lab) or Gemini; lanes DSA*/JIS-NB: run cards, `desk.py assign` turns ready ones into desk rows".
- **Which Newer**: SOURCED `MyTradingSys/system/ROUTING.md` (2026-10-28) is newer than `D8_OPERATIONS.md` (2026-10-20).
- **Conflict**: D8 collapses lanes into three and retires DSA/Gemini lanes. In contrast, ROUTING.md maintains active channels and task cards across distinct lanes: HAIKU, SONNET, OPUS, CODEX, DSA*, and JIS-NB.

### 4. Worker Session Capacity Limit: 3 vs 4 Concurrent Background Agents
- **Sentence A**: SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D7_ROADMAP.md:30`: "Three parallel stages, three worker sessions at most, one coordinator."
- **Sentence B**: SOURCED `MyTradingSys/system/WORKERS.md:38`: "Workers are background Agents (max 4 at once); `start_session` only for interactive roles".
- **Which Newer**: SOURCED `MyTradingSys/system/WORKERS.md` (2026-10-27) is newer than `D7_ROADMAP.md` (2026-10-20).
- **Conflict**: D7 caps capacity at "three worker sessions at most", while WORKERS.md rule 7 allows up to "max 4 at once" for background Agents.

### 5. Haiku Concurrency Cap: Universal 5 vs Pipeliner Cap of 2
- **Sentence A**: SOURCED `MyTradingSys/system/WORKERS.md:26-27`: "A session spawns **at most 5 Haiku Agents at a time**"
- **Sentence B**: SOURCED `MyTradingSys/system/ROUTING.md:76`: "one-use Haiku Agent from the session that owns the task (max 5 at once; Pipeliner max 2)".
- **Which Newer**: SOURCED `MyTradingSys/system/ROUTING.md` (2026-10-28) is newer than `WORKERS.md` (2026-10-27).
- **Conflict**: WORKERS.md rule 3a establishes a general concurrency ceiling of 5 Haiku Agents without role restrictions, whereas ROUTING.md restricts Pipeliner sessions to at most 2 concurrent Haiku Agents.

### 6. Opus Dispatch Gate: Card `approved_by` vs `approved_by` AND `crucial`
- **Sentence A**: SOURCED `MyTradingSys/system/SUPER_SESSION.md:10`: "The worker model is the card's `model` field; `opus` only when the operator names it or the card has `approved_by`."
- **Sentence B**: SOURCED `MyTradingSys/system/WORKERS.md:35-37`: "Opus is the tight exception ... (b) a session starts it only for a task card in lane OPUS with `approved_by` and `crucial` (one line: live money, irreversible data, or a no-undo design call), cited by id in the brief."
- **Which Newer**: SOURCED `MyTradingSys/system/WORKERS.md` (updated 2026-10-27) vs `SUPER_SESSION.md` D1 (2026-10-24). Note that SUPER_SESSION.md line 10 claims to replace WORKERS rule 6(b), yet WORKERS.md retained the stricter gate.
- **Conflict**: Under SUPER_SESSION.md D1, `approved_by` alone is sufficient; under WORKERS rule 6(b), the card must be in lane OPUS and have both `approved_by` AND `crucial`.

### 7. Generated Artifact Pages Maintenance: Freeze vs Mandatory Rebuild & Republish
- **Sentence A**: SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D8_OPERATIONS.md:29-30`: "Two pages: the decision page (questions with yes/no/change, one line per stage per week) and STATUS.md. Every other generated page stops being rebuilt; the artifacts rebuild branch is shipped once and then not maintained."
- **Sentence B**: SOURCED `MyTradingSys/system/SUPER_SESSION.md:87`: "Pages follow builds: `python scripts/dev/artifacts.py build`, then `artifacts.py stale`, then republish each STALE page over its url from the owning login (C = jishusharma1985 for its pages)".
- **Which Newer**: SOURCED `MyTradingSys/system/SUPER_SESSION.md` (2026-10-26/30) is newer than `D8_OPERATIONS.md` (2026-10-20).
- **Conflict**: D8 mandates halting the rebuild and maintenance of generated artifact pages (keeping only the decision page and STATUS.md), while SUPER_SESSION.md End sequence step 87 explicitly mandates running `artifacts.py build`, checking `artifacts.py stale`, and republishing stale pages.

### 8. GPT Lab Queue Dispatch: Fixed Legacy Sequence vs Super Session Tick Loop
- **Sentence A**: SOURCED `MyTradingSys/system/ANNOUNCEMENTS.md:46-48`: "DO-NOW GPT lab queue is idle; NUC keeps it busy ... Applies to: NUC super session. What: run the ready CODEX cards one at a time in this order: lab-data-pin-hash, lab-machine-checks-extra, lab-weight-enforce, lab-crossvendor-stage, lab-holdout-access-control, lab-formula-spec-text; then lab-planted-error-trial".
- **Sentence B**: SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md:95-96`: "First wake, in this order: `get_usage` and `supervisor.py plan`; GPT lane (contradiction 5: claim, `codex_run.py tick`; signal b-230ce8 `ack done` once a run lands)".
- **Which Newer**: SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md` (2026-10-30) is newer than `ANNOUNCEMENTS.md` A-20261018-3 (2026-10-18).
- **Conflict**: Announcement A-20261018-3 instructs the NUC to execute a specific 7-card fixed pipeline sequence, whereas D11 section 7 directs the super session to run generic `codex_run.py tick` claims against whichever cards are in the ready backlog.

### 9. Scoped Agent Turn Budget Ceiling: 20/40 Turns vs 15 Turns
- **Sentence A**: SOURCED `MyTradingSys/system/WORKERS.md:20-21` & `SUPER_SESSION.md:26`: "the brief says 'stop at 40 turns and report', size S 20".
- **Sentence B**: SOURCED `MyTradingSys/system/WORKERS.md:26`: "Scoped work goes to a one-use Haiku Agent ... Brief = files + change + done check + 'stop at 15 turns and report'".
- **Which Newer**: SOURCED `MyTradingSys/system/WORKERS.md:26` (rule 3a added 2026-10-27) is a specific refinement overriding the general rule in `WORKERS.md:20` and `SUPER_SESSION.md:26`.
- **Conflict**: For size S scoped tasks dispatched to Haiku, WORKERS rule 3 / SUPER_SESSION rule 2 instructs briefs to say "stop at 20 turns and report", while WORKERS rule 3a instructs briefs to say "stop at 15 turns and report".

### 10. YouTube & Caption Extraction Channel: NUC-Exclusive vs Any Machine
- **Sentence A**: SOURCED `MyTradingSys/system/ANNOUNCEMENTS.md:50-52`: "Where each kind of work goes (two machines) ... NUC (lab, GPT/Codex, Gemini/Antigravity, F:/MTS/data): lab cards, re-derivations, planted-error trial, retro-audit of past base results."
- **Sentence B**: SOURCED `MyTradingSys/system/ROUTING.md:74`: "CBP caption fetch for known analyst channels (`cbp_run.py`) | any Claude machine (bug-youtube-gemini-only-rule-is-a-preference, 2026-10-27: Gemini-on-the-NUC was written as a limit, it is a preference)".
- **Which Newer**: SOURCED `MyTradingSys/system/ROUTING.md` (2026-10-27/28) is newer than `ANNOUNCEMENTS.md` A-20261018-4 (2026-10-18).
- **Conflict**: ANNOUNCEMENTS A-20261018-4 pinned all external data and transcript extractions to JIS-NUC, whereas ROUTING.md explicitly lifted this restriction on 2026-10-27 to permit running `cbp_run.py` caption fetches on any Claude machine.
