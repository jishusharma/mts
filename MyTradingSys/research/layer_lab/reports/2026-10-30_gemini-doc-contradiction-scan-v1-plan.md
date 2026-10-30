# Layer Lab Report: Document Contradiction Scan

**Card:** `gemini-doc-contradiction-scan-v1-plan`  
**Date:** 2026-10-30 (UTC)  
**Worker:** Gemini Flash (`[GEMINI]`)  
**Lane:** CODEX  
**Output:** [doc_contradictions.md](file:///F:/MTS/gq/gemini-doc-contradiction-scan-v1-plan/MyTradingSys/research/gemini_audits_2026-10-30/doc_contradictions.md)

## Summary of Findings

D11 section 4 (`MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md:60-72`) enumerates 9 known contradiction pairs resolved on 2026-10-30.
This audit read the six designated documents:
1. `MyTradingSys/research/v1_plan_2026-10-20/D7_ROADMAP.md`
2. `MyTradingSys/research/v1_plan_2026-10-20/D8_OPERATIONS.md`
3. `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`
4. `MyTradingSys/system/ANNOUNCEMENTS.md` (ACTIVE)
5. `MyTradingSys/system/WORKERS.md`
6. `MyTradingSys/system/SUPER_SESSION.md`
7. `MyTradingSys/system/ROUTING.md`

and identified **10 contradiction pairs** beyond D11 section 4.

### The 10 Identified Contradiction Pairs

1. **Confluence Freeze vs Active Funnel Slot**:
   - SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D7_ROADMAP.md:8-9`: "Frozen for the whole v1 (until the operator unfreezes) ... confluence between layers"
   - SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md:30`: "D4 slots: Levels Confluence (`lc-validation` after LC3 DEV says go)"
   - Newer: `D11_PROGRAMME.md` (2026-10-30 vs 2026-10-20)

2. **Universal Agent Rule vs Scheduled Session Worker**:
   - SOURCED `MyTradingSys/system/WORKERS.md:21`: "Every worker card runs as an Agent (chained cards allowed)."
   - SOURCED `MyTradingSys/system/ROUTING.md:100`: "RU3 shot.py bundle (Eagle_Eyes) | ru3-eagle-eyes-shot-py-bundle-evidence-p | session / 25"
   - Newer: `ROUTING.md` (2026-10-28 vs 2026-10-27)

3. **Lanes Collapsed to Three vs Six Active Routing Lanes**:
   - SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D8_OPERATIONS.md:26-28`: "Lanes collapse to three: Claude ... Codex ... Operator ... DSA/Gemini and the DeepSeek AIBridge lane are retired unless their rows drain in S0"
   - SOURCED `MyTradingSys/system/ROUTING.md:51`: "lane HAIKU/SONNET/OPUS: a Claude session or Agent ... lane CODEX: `codex_run.py` (GPT lab) or Gemini; lanes DSA*/JIS-NB: run cards, `desk.py assign` turns ready ones into desk rows"
   - Newer: `ROUTING.md` (2026-10-28 vs 2026-10-20)

4. **Concurrent Worker Session Cap (3 vs 4)**:
   - SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D7_ROADMAP.md:30`: "Three parallel stages, three worker sessions at most, one coordinator."
   - SOURCED `MyTradingSys/system/WORKERS.md:38`: "Workers are background Agents (max 4 at once)"
   - Newer: `WORKERS.md` (2026-10-27 vs 2026-10-20)

5. **Haiku Concurrency Limit (Global 5 vs Pipeliner 2)**:
   - SOURCED `MyTradingSys/system/WORKERS.md:26-27`: "A session spawns **at most 5 Haiku Agents at a time**"
   - SOURCED `MyTradingSys/system/ROUTING.md:76`: "one-use Haiku Agent from the session that owns the task (max 5 at once; Pipeliner max 2)"
   - Newer: `ROUTING.md` (2026-10-28 vs 2026-10-27)

6. **Opus Dispatch Policy (`approved_by` vs `approved_by` AND `crucial`)**:
   - SOURCED `MyTradingSys/system/SUPER_SESSION.md:10`: "The worker model is the card's `model` field; `opus` only when the operator names it or the card has `approved_by`."
   - SOURCED `MyTradingSys/system/WORKERS.md:35-37`: "Opus is the tight exception ... (b) a session starts it only for a task card in lane OPUS with `approved_by` and `crucial` ... cited by id in the brief."
   - Newer: `WORKERS.md` (2026-10-27 vs 2026-10-24)

7. **Generated Pages Lifecycle (Stop Maintenance vs Mandatory Rebuild/Republish)**:
   - SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D8_OPERATIONS.md:29-30`: "Two pages: the decision page ... and STATUS.md. Every other generated page stops being rebuilt; the artifacts rebuild branch is shipped once and then not maintained."
   - SOURCED `MyTradingSys/system/SUPER_SESSION.md:87`: "Pages follow builds: `python scripts/dev/artifacts.py build`, then `artifacts.py stale`, then republish each STALE page over its url from the owning login"
   - Newer: `SUPER_SESSION.md` (2026-10-26/30 vs 2026-10-20)

8. **Codex Lab Execution (Fixed Sequence vs Dynamic Super Session Tick)**:
   - SOURCED `MyTradingSys/system/ANNOUNCEMENTS.md:46-48`: "DO-NOW GPT lab queue is idle; NUC keeps it busy ... run the ready CODEX cards one at a time in this order: lab-data-pin-hash, lab-machine-checks-extra, lab-weight-enforce, lab-crossvendor-stage, lab-holdout-access-control, lab-formula-spec-text; then lab-planted-error-trial"
   - SOURCED `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md:95-96`: "First wake, in this order: `get_usage` and `supervisor.py plan`; GPT lane (contradiction 5: claim, `codex_run.py tick`; signal b-230ce8 `ack done` once a run lands)"
   - Newer: `D11_PROGRAMME.md` (2026-10-30 vs 2026-10-18)

9. **Scoped Haiku Turn Cap (20 vs 15 turns)**:
   - SOURCED `MyTradingSys/system/WORKERS.md:20-21` & `SUPER_SESSION.md:26`: "the brief says 'stop at 40 turns and report', size S 20"
   - SOURCED `MyTradingSys/system/WORKERS.md:26`: "Scoped work goes to a one-use Haiku Agent ... Brief = files + change + done check + 'stop at 15 turns and report'"
   - Newer: `WORKERS.md:26` (2026-10-27 rule 3a vs 2026-10-27 rule 3 / 2026-10-24)

10. **Caption Fetch Host Pinning (NUC-Only vs Any Machine)**:
    - SOURCED `MyTradingSys/system/ANNOUNCEMENTS.md:50-52`: "Where each kind of work goes (two machines) ... NUC (lab, GPT/Codex, Gemini/Antigravity, F:/MTS/data): lab cards, re-derivations, planted-error trial, retro-audit of past base results."
    - SOURCED `MyTradingSys/system/ROUTING.md:74`: "CBP caption fetch for known analyst channels (`cbp_run.py`) | any Claude machine (bug-youtube-gemini-only-rule-is-a-preference, 2026-10-27: Gemini-on-the-NUC was written as a limit, it is a preference)"
    - Newer: `ROUTING.md` (2026-10-27/28 vs 2026-10-18)

Noticed: none
