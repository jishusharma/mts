# Report: Layer Fact Sheet - Tom (`lf-tom-gemini-facts`)
Date: 2026-10-25 (UTC)
Task: `lf-tom-gemini-facts` [CODEX, prio 2]
Target Fact Sheet: `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/tom.md`

## Summary of Findings
- Layer family `tom` documented with 3 distinct constituent layers:
  1. `tom_core`: core setup candidate engine (`MyTradingSys/system/LAYERS.md:13`)
  2. `tom_proofs`: order flow proof flags (`MyTradingSys/system/LAYERS.md:14`)
  3. `tom_vp_pivot`: pivot-anchored volume profile touch study (`MyTradingSys/system/LAYERS.md:15`)
- Every layer fact documented with strictly sourced repository facts under the five required sections:
  - ORIGIN (analyst quotes and citations with `file:line`)
  - PARAMETERS (labelled strictly as `SOURCED` or `OURS` / `NO-SOURCE`)
  - BACKTESTS (report path, fee-net accounting, in-sample vs out-of-sample split, and trade count `n`)
  - KNOWN BUGS (open and closed rulings from `python scripts/dev/lab_query.py rulings tom`)
  - CONFLUENCE (interactions with Fabio, Pitchfork, Guidance, or `NOT_IN_DATA`)
- No verdict rendered on keeping, dropping, demoting, or parking any layer, adhering to `MyTradingSys/system/ANTIGRAVITY_LAPTOP.md:16,33`.
