# REFLEXIVITY LOG — MTS Project
# Date: 2026-08-19
# Source: Grounded Theory Protocol Safeguard 4
# Status: Required Phase 3 output

---

## PHASE 1 REFLEXIVITY — P0, P1, P2

### Unexpected codes

- P0: ledge, dynamic concept, volume step, market speed, rotation, trading personality, what you've got you've got.
- P1: max drawdown rule, equity curve simulator, heat map criticism, newspaper counter-indicator, UX sentiment.
- P2: fair value gap nuance, pre-indicator/Mag 7, stop-loss hunting myth, 80% rule, trader DNA.

### Pre-conceptions challenged

- The 4-setup architecture (CT/TC/BO/SC) was assumed from old provisional files.
- The data shows these are context modes inside one decision process, not independent systems.
- VWAP, CVD, footprint are not always present; Tom selects tools per context.

### Assumptions needing revision

- Setup files must not be built before the architecture map is reviewed.
- Dedicated setup files may not be necessary; a decision framework may fit better.
- Cross-video contamination risk requires keeping every claim in Phase 3 tied to specific source videos.

### Fabrication risk

- LOW. Phase 1 extractions were built from verbatim quotes with tier labels.
- Remaining risk: drawing boundaries between modes without sufficient co-occurrence evidence.
- Mitigation: the architecture map labels the outcome as interpretation, not final.

---

## PHASE 3 REFLEXIVITY

### What emerged

- The four mode names appear in Tom's own words.
- They co-occur in the same videos and often describe the same trade executed differently.
- The stronger pattern is a decision tree, not isolated clusters.

### What was challenged

- The previous Phase 4 draft created four setup files because four placeholder files existed.
- That was a deductive error. Corrected before execution.

### Next assumption to test

- Can the decision process be represented as one framework without losing actionable detail?
- Can mode boundaries be defined using market state + trader DNA + proof type?

---

## LIVE-TEST-002 REFLEXIVITY — Java VP Cross-Validation
### Date: 2026-08-25
### Session: VP alignment (TASK-8) + Bug discovery (PATCH-001)

### What worked

1. **Step-by-step cross-validation protocol** — One timeframe at a time, ±2% target, clear pass/fail.
2. **Side-by-side comparison tables** — Java vs TradingView in tabular format made deltas obvious.
3. **Gap flagging (G-XX IDs)** — Every issue got a trackable ID. Nothing lost.
4. **One screenshot at a time** — Prevented cognitive overload.
5. **Python computation for deltas** — Automated % diff, reduced human error.

### What did NOT work

1. **Created downloadable file links** (`sandbox:///mnt/agents/output/...`) — User cannot use these. **RULE: Never create file links. Inline copy-paste only.**
2. **Wasted tool calls on file write failures** — ~6 attempts on permission errors. **RULE: Prefer inline output. Use shell only when necessary.**
3. **Compared VWAPs without checking anchors first** — Flagged G-24 as "VWAP stuck" when part was anchor mismatch (00:00 vs 08:00). **RULE: Always verify anchor points BEFORE comparing VWAP values.**
4. **Created verbose checkpoint files** — 200+ lines, not copy-paste friendly. **RULE: Keep checkpoints under 50 lines. Resume prompt as one clean block.**
5. **Did not adapt to user's environment** — Windows PowerShell + IntelliJ. Kept outputting Linux paths. **RULE: Windows-friendly formatting. Copy-paste ready text blocks.**
6. **Assumed updated JSON was uploaded at session start** — Searched filesystem instead of asking. **RULE: Ask the user directly.**
7. **Repeatedly referenced wrong directory** — Kept saying `/mnt/agents/upload/` when the working repo is `/mnt/agents/output/upload_mirror/`. **RULE: The project repo is `upload_mirror/`. `upload/` is NOT used in our workflow.**
8. **Said "upload" for project files** — Project files in `upload_mirror/` are already there. No "upload" happens. Only new screenshots/JSON go to `temp/`. **RULE: Stop saying "upload." Say "read from mirror repo."**

### Assumptions challenged

- **Assumption:** Java VWAP updates continuously like VP does.
- **Reality:** VWAP was cached/stuck across snapshots. VP recalculates; VWAP does not.
- **Assumption:** One VWAP is enough for crypto.
- **Reality:** Crypto has funding at 08:00 UTC. Need both session VWAP (00:00) and post-funding VWAP (08:00).
- **Assumption:** JSON schema is clean because it compiles.
- **Reality:** Band keys had corrupted sigma symbols (`+1?`). Serialization bug invisible to compiler.
- **Assumption:** `/mnt/agents/upload/` is the working repo.
- **Reality:** `/mnt/agents/output/upload_mirror/` is the working repo. `upload/` is a separate read-only copy.

### New rules for next session

1. **NO FILES. NO LINKS. INLINE ONLY.**
2. **Verify anchors before comparing VWAP.**
3. **Ask for exact numbers, not estimates.**
4. **Check JSON for `?` / unicode corruption.**
5. **Keep checkpoints under 50 lines.**
6. **Read project files from `/mnt/agents/output/upload_mirror/` — NOT `/mnt/agents/upload/`.**
7. **Never say "upload" for project files.** They are already in the mirror repo.

### Fabrication risk

- **LOW for VP numbers** — All from Java JSON or screenshot extraction.
- **MEDIUM for VWAP analysis** — G-24 was initially misdiagnosed. Corrected before escalation.
- **Mitigation:** Cross-check anchors, take multiple snapshots before flagging.

# END OF REFLEXIVITY LOG