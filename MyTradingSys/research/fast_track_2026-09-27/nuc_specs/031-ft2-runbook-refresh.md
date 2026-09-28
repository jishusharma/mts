TASK: Refresh the stale HALT-file paragraph in FT2_RUNBOOK.md section 1 to the post-FIX3 contract, and add a new section on FIX3 changes to HALT behavior.
SCOPE: MyTradingSys/research/fast_track_2026-09-27/FT2_RUNBOOK.md, MyTradingSys/execution/executor.py, MyTradingSys/execution/kill_switch.py
OUTPUT: One FILE block, full content: MyTradingSys/research/fast_track_2026-09-27/FT2_RUNBOOK.md. Nothing else.
OUTPUT_TOKENS: 7000
EXPECT: minimum 250 lines
EXPECT: ## 1. WHAT THIS BATCH ADDS
EXPECT: ### HALT Files (Post-FIX3)
EXPECT: FIX3

Context: The previous Qwen proposal cut FT2_RUNBOOK.md from 294 to 26 lines, which discarded all critical documentation. This task must:
1. PRESERVE all existing sections and content structure (sections 0-7+ as currently written).
2. REFRESH the "HALT files (operator-relevant, not code):" paragraph in section 1 to describe the post-FIX3 behavior, citing the updated contract from executor.py.new and kill_switch.py.new.
3. ADD a new subsection titled "### HALT Files (Post-FIX3)" after the current HALT paragraph, documenting:
   - What changed in FIX3 (how HALT file behavior or kill-switch interaction was modified)
   - The new contract and guarantees
   - Any new operator workflows or edge cases to understand
4. Keep the TOTAL LINE COUNT >= 250 (the original is 294 lines; do not drop below 250).

Do not remove sections, summarize sections, or cut content. Write a 1-2 page refresh that integrates the new FIX3 HALT contract into the existing narrative.

Answer from the SOURCE blocks only. Start with the five lines TASK, STATUS, SUMMARY, FINDINGS, NEXT.
