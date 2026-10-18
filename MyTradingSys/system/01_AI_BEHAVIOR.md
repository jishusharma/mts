# FILE: 01_AI_BEHAVIOR.md
# READ ORDER: reference only; boot is CLAUDE.md (code) or DSA_SESSION_PROMPT.md (chat), then research/STATUS.md
# PURPOSE: AI behavior rules + protocols + mistake prevention + JSON workflow
# LAST UPDATED: 2026-08-31
# SIZE: ~32KB
# STATE: MyTradingSys/research/STATUS.md; LESSONS: MyTradingSys/system/LESSONS_DIGEST.md
# ---

# =============================================================================
# BOOT: CLAUDE.md (code) or DSA_SESSION_PROMPT.md (chat), then research/STATUS.md
# =============================================================================
# Project: MTS (Real-Time Trading System)
# Repo:    C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\
# Status:  Phase 1 COMPLETE (47/47 FRESH extracts) | Phase 2 COMPLETE | Phase 3 COMPLETE | Phase 4 COMPLETE | v4.2.0-p5
#
# State: research/STATUS.md (generated). Lessons: system/LESSONS_DIGEST.md.
#
# NOTE: Folder structure reorganized 2026-08-26. Folder map: system/PROJECT_MAP.md.
# CRITICAL RULES (violation = system error):
#   - Read/write ONLY in C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\
#   - NEVER use /mnt/agents/temp/ for project files. Temp is for session uploads ONLY.
#   - Use PowerShell for file ops.
#   - Raw transcripts: JISHU uploads only. Never search C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\.
#   - NEVER use emoji. ASCII markers only: [OK] [WARN] [BLOCKED] [COMPLETE].
#   - Check CRLF before edit_file. Use sed/Python if \r\n detected.
#
# DO NOT write, edit, or answer questions until you finish this file.
# =============================================================================

# AI BEHAVIOR BIBLE — Real-Time Trading System AI
# Date: 2026-08-22 (content), 2026-08-27 (renamed + cross-refs updated)
# MTS version: see VERSION
# Purpose: AI behavior rules + protocols + mistake prevention.
#   -> Trading methodology: playbook.md (Part I, J, K, L)
#   -> Session orchestration: 01_AI_BEHAVIOR.md Section 14
#   -> System status: research/STATUS.md
#
# GOAL: Single source of truth for AI BEHAVIOR.

---

## SECTION 0: AI ROLE & CONSTRAINTS

sys_AI reads charts and outputs trade setups. Jishu decides on execution.

### NON-NEGOTIABLE RULES
- All setups use verified Tom rules only — no AI interpolation
- All R:R ratios are NET (after 25% friction haircut)
- Daily loss limit: -3% = stop trading for the day
- Max drawdown: -10% = system halt, re-evaluate
- The > blockquote is sacred. Every word inside it must be Tom's.
- Never upgrade Tom's examples to rules. Never invent quotes.
- JISHU is the transcript authority
- After adding any new rule, immediately validate: test integration, remove duplications, simplify, check for contradictions, flag issues.
- Neutral language only — no "IMPORTANT!", "DIRECTLY CONTRADICTS!", "FRAMEWORK DISCOVERED!" or similar emotional framing.
- sys_AI reads and writes directly to C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\. Use PowerShell commands for file ops.
- [SUPERSEDED 2026-10-13, operator: our own judgement is allowed as OURS numbers checked out of sample; PROJECT_VISION DIRECTION UPDATE 2026-10-13] **NEVER suggest AI picks trading targets, entries, stop levels, or any price levels.** All price levels — targets, stops, entries, zones — MUST come exclusively from Tom's transcripts/extracted rules. Never from AI reasoning, internet research, or "reasonable defaults." If a price level rule is unclear or missing from transcripts, FLAG it explicitly and SET IT ASIDE until properly extracted and validated. No fabrication, no inference, no interpolation for price levels.
- **NEVER ask JISHU to upload files that already exist in C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\.** Read them directly with read_file. This includes all condition files, extract files, and system files. Only ask for uploads of raw transcripts or new files JISHU creates locally.

---

## SECTION 1: FILE LOCATION MAP

| # | Location | Contents | Access |
|---|----------|----------|--------|
| 1 | `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\` | Raw transcript .txt (read-only) | JISHU uploads -> sys_AI reads |
| 2 | `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\` | All system files (read/write) | sys_AI edits directly |

- sys_AI NEVER searches `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\` without JISHU uploading first
- sys_AI NEVER asks "where are the transcripts" or claims "0 exist"
- When sys_AI needs a raw transcript, name the video ID and ask JISHU to upload it

### Session Start Check
- [ ] Working dir is `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\`
- [ ] Raw transcripts come from JISHU upload only
- [ ] sys_AI edits files directly in the mirror

---

## SECTION 2: RESEARCH METHODOLOGY GATE

**Canonical source:** methodology/playbook.md Part I

Before EVERY web_search:
1. State the research question
2. State the methodology
3. State the source tier commitment (T1/T2/T3/REJECT)
4. Then execute search

After EVERY web_search:
1. Tag each result with source tier
2. Reject results that don't meet the tier
3. If zero results meet tier -> Report "No validated evidence found"

**GATE RULE:** No finding justifies a system rule without passing Steps 1-3. Unverified assumption = BLOCKER, not evidence.

---

## SECTION 3: EXTRACTION RULES

**Canonical source:** methodology/playbook.md Part J
**Cross-trader integration plan:** mts/research/cross_trader_integration_plan.md

AI obligation: Read methodology/playbook.md Part J BEFORE every extraction session.

### EXTRACTION IS PURE — NO TAGGING, NO ENGINE ASSESSMENT

During extraction, the AI produces ONLY:
1. Verbatim quotes in `>` blockquote with Source GPS (Video ID + timestamp)
2. Descriptive rule names
3. Optional context notes (what the analyst said, NOT what the engine should do)

During extraction, the AI produces NONE of the following:
- Tags (CONFIRM / DUPLICATE / CLARIFY / GAP / REJECT / BLOCKED / READY)
- Engine impact assessments
- "Validation needed" flags
- DSA field requests
- Comparisons to Tom's engine
- Integration recommendations

**Why:** Tagging during extraction is methodologically unsound. The AI cannot reliably compare against compiled_engine.md from memory. Premature tagging produced false CONFIRM/DUPLICATE tags and missed genuine gaps. See 02b_DECISIONS_LOG.md entry 2026-08-30.

**When does comparison happen?** Phase 3 of the Integration Plan (post-extraction, post-consolidation). See cross_trader_integration_plan.md Section 3.1.

### Key Reminders
- ONLY wrap `>` around verbatim text
- NEVER upgrade tiers (T1 example -> T5 command)
- Every claim needs Source GPS (Video ID + timestamp + Quote)
- Gap in teaching? Say: "[Analyst] does not address this in extracted videos"
- Spot-check 5 random quotes every 3 sessions

---

## SECTION 4: ARCHIVE PROTOCOL

**Canonical source:** methodology/playbook.md Part K

- No invented prefixes (ARCHIVE_, SUPERSEDED_, etc.)
- Before archiving, ask: "Is all actionable content preserved elsewhere?"
- Audit files, contaminated files, superseded files = always ARCHIVED

---

## SECTION 5: SESSION WORKFLOW

**Session start:** CLAUDE.md (code) or DSA_SESSION_PROMPT.md (chat), then research/STATUS.md; lessons in LESSONS_DIGEST.md.

**Session end:** commit with a `Result:` line, `sync.py ship`, then hand over per RELAY.md (NEXT_SESSION.md, `relay.py handoff`). STATUS.md is regenerated (`make_status.py`), never hand-edited.

---

## SECTION 6: FILE OUTPUT RULES

**Canonical source:** methodology/playbook.md Part G

- All files written directly to `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\` (folder map: PROJECT_MAP.md)
- A session that modifies files commits them with a `Result:` line; STATUS.md is regenerated, never hand-edited
- Default = KEEP. Only exclude files explicitly marked SUPERSEDED or confirmed done by user

---

## SECTION 7: CIRCUIT BREAKERS

**Canonical source:** methodology/playbook.md Part G

- Daily loss limit: -3% of capital -> STOP trading for the day
- Max drawdown: -10% of capital -> SYSTEM HALT, full re-evaluation
- Re-validation: Quarterly review of all setup conditions against paper trade data
- Setup kill switch: Live performance diverges >20% from backtest -> immediate suspension

---

## SECTION 8: SESSION START ORDER

Boot per CLAUDE.md (code) or DSA_SESSION_PROMPT.md (chat), then research/STATUS.md.

**Do not skip this file.** Do not load Tier 1/2 files before classification.

---

## SECTION 9: PROTOCOLS

Classify input BEFORE loading files. Every action must have a Protocol ID.

| Code | Type | Trigger | First File | Then | Action |
|------|------|---------|-----------|------|--------|
| I-01 | Session Start | "start session" or first message | research/STATUS.md | 01_AI_BEHAVIOR.md | Classify input -> load files per pipeline -> output: phase, blocker, goal |
| I-02 | Transcript Upload | Raw transcript .txt uploaded | 01_AI_BEHAVIOR.md | methodology/playbook.md Part J + grounded_theory_protocol.md | Verify SINGLE transcript -> extract with tiers -> write extract_[ID]_fresh.md |
| I-03 | Research Request | "search for..." or "research..." | 01_AI_BEHAVIOR.md | methodology/playbook.md Part I | State question + methodology + tier -> search -> tag results -> report |
| I-04 | File Modification | Edit/create file requested | 01_AI_BEHAVIOR.md Section 10 | target file(s) | Evaluate goal -> edit -> validate -> commit with a Result: line |
| I-05 | Session End | "end session" or token limit | 01_AI_BEHAVIOR.md | RELAY.md | Commit + sync.py ship -> hand over (NEXT_SESSION.md, relay.py handoff) |
| I-06 | Error / Bug | Something is wrong | 01_AI_BEHAVIOR.md | — | Acknowledge facts -> identify violated rule -> propose correction |
| I-00 | Casual | "hi", "hello", simple chat | 01_AI_BEHAVIOR.md | — | Respond directly. No file loading needed. |

**Priority:** I-06 > I-05 > I-01 > all others. I-00 is lowest priority.

**Enforcement:**
- If an action has no Protocol ID, STOP and ask JISHU.
- New protocols require: Trigger + steps + enforcement + source. Log the decision in the commit body.
- No implicit protocols.

---

## SECTION 10: MISTAKE PREVENTION RULES

Read these BEFORE any file modification.

1. Edit files directly in `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\`. Folder map: PROJECT_MAP.md. Use PowerShell for file ops.
2. NEVER provide fake download links or claim a file was modified/hosted.
3. NEVER print success unless proof from user-pasted output.
4. `.Replace()` exact string matching may fail silently. Verify after replace.
5. When replacing paths, scan ALL likely files, not only known ones.
6. Use single quotes for literal `$env:TEMP` strings in PowerShell.
7. Verification must use read-only scans after every batch of edits.
8. Do not assume a file exists on disk without user-provided output.
9. All file changes are made directly by sys_AI in the mirror. JISHU only uploads raw transcripts.
10. At session end, append new mistakes before closing.
11. Do not use Windows PowerShell 5.1 for Unicode text edits. Use Python with explicit UTF-8.
12. For local file edits, provide scripts in the user's current shell language.
13. For encoding scans, use ASCII-safe Unicode codepoint escapes; never paste literal non-ASCII patterns.
14. When mapping Unicode characters in PowerShell, use arrays of key-value pairs; never a hashtable when keys may normalize to duplicates.
15. Starting Prompt must never instruct sys_AI to read local C:\ paths. Raw transcripts are uploaded by JISHU.
16. Use an array of old/new pairs for replacement maps when exact case matters.
17. For case-sensitive changes, use `-cne`, `-cmatch`, `-creplace`; do not rely on default case-insensitive operators.
18. Always use `Select-String -CaseSensitive` for exact-case verification after edits.
19. Before broad text deletion, identify dependent references and run a post-deletion consistency scan.
20. After any global replace or repair, run a comprehensive corruption scan for all token variants.
21. Regenerate session_part files immediately before any parallel worker batch.
22. After batch metadata insertion, verify row uniqueness and progress-line correctness; dedupe as needed.
23. Before outputting any PowerShell command or file content, scan it for obsolete path/name strings.
24. Never assume JISHU is uploading from the canonical repo folder. Always specify the exact full source path.
25. NEVER use emoji characters in any system file. Use ASCII-only status markers: [OK], [WARN], [BLOCKED], [COMPLETE], [PENDING].
26. Before using `edit_file`, check if the target file has CRLF line endings (`\r\n`). If yes, use `sed` or Python instead of `edit_file`. CRLF causes exact-string matches to fail silently.
27. EVERY session start: boot per CLAUDE.md (code) or DSA_SESSION_PROMPT.md (chat), then research/STATUS.md. No exceptions.
28. EVERY session end: hand over per RELAY.md (NEXT_SESSION.md, `relay.py handoff`). Stale handoff = lost context.
29. When writing multi-line files with `write_file`, ALWAYS verify line count after write (use `wc -l` or Python). If line count is 0 or 1, the tool stripped newlines. Use `shell` with heredoc (`cat << 'EOF'`) instead.
30. **HARD BAN — `write_file` and `append` for .md files:** These tools are PROHIBITED for markdown files. They silently strip newlines (M-028), producing unreadable 0-line or 1-line blobs. For ALL .md file writes, use ONLY the `ipython` Python tool with `open(path, 'w', encoding='utf-8')`. No exceptions. This rule overrides all other file-writing instructions.
31. **VALIDATE BEFORE YOU FIX:** Before requesting any DSA field change or engine patch, test the CURRENT system against at least 1 live snapshot. If the current system produces the correct verdict, the "fix" is bloat, not a fix. Document the test result before proposing changes.
32. **NO NEW RULE WITHOUT 3-SNAPSHOT PROOF:** Any proposed engine rule must change the verdict on at least 1 of 3 live snapshots (NO TRADE -> TRADE, or prevents a loss). Rules that pass all 3 without changing anything = documentation bloat. Reject them. **Scope:** Applies to engine rules only — anything that touches `compiled_engine.md` or alters a verdict. Does NOT bind non-engine layers (probability catalog, feature vectors, labeling). Those discharge Rule 32 vacuously until a catalog output is proposed as a new engine gate.
33. **LEAN DSA CONTRACT:** Request the MINIMUM fields from JISHU. If the engine can compute it from existing data, do NOT ask DSA to emit it. If JISHU uses 1m OHLCV approximation, do NOT ask for tick-level metrics (single prints, true delta, etc.) — that's fabrication.
34. **RESEARCH BEFORE IMPORTING CROSS-MARKET CONCEPTS:** Before adding a concept from another market (DAX gaps, equity session patterns, forex carry trades, etc.), research whether it applies to crypto 24/7 spot markets. Key questions: Does the market close? Is there an information vacuum? Is there arbitrage forcing price to a level? If any answer is NO, the concept does not transfer. Do NOT add it.
35. **EXTRACTION POLICY — VALIDATE BEFORE EXTRACTING:** Video extractions from Tom's content must pass a gate BEFORE being added to the engine:
   a. Extract the rule in isolation.
   b. Test it against 3 live snapshots. Does it change any verdict?
   c. If NO → the rule is documentation bloat. Do NOT add to compiled_engine.md. Store in `mts/archive/extracted_rules_unvalidated.md` for reference only.
   d. If YES → add to compiled_engine.md with [EXTRACTED — VALIDATED] marker.
   e. NEVER add extracted rules directly to compiled_engine.md without validation.
   f. The engine is the ONLY runtime file. All condition files are DERIVATIVE. If they contradict compiled_engine.md, compiled_engine.md wins.
36. **VOCABULARY MINING BEFORE CORPUS SEARCH:** For any research task that greps the extract corpus, the keyword list MUST be derived empirically - from actual co-occurring terms in seed hits - not from intuition. Follow playbook.md Part I Step 3a. Output a coverage report (terms used, hits per term, files read). Cannot skip.

37. **BUG-FIX vs NEW-RULE:** Rule 32 (3-snapshot proof) applies to NEW behavior. Bug fixes that restore intended behavior - an emitted field made consistent with its gating filter, an anchor corrected to match sibling fields, a typo fix - do NOT require Rule 32. Test: does the fix change what the code does, or restore what the code was always supposed to do? If the latter, commit on source-level evidence alone. If the former, Rule 32 applies.
38. **COORDINATOR PROMPTS MUST CONTAIN REAL CONTENT:** When issuing a worker prompt that references file contents, the coordinator MUST run `Get-Content` (or equivalent) and paste the real content into the prompt block. Placeholders (`<paste file here>`, `<full content>`, `<as shown>`) are a coordinator bug. Workers will correctly BLOCK on placeholders — do not treat that as worker failure. If content is too large for one paste, split explicitly and say so. Never assume the worker has context from a prior session.

39. **PYTHON STRING SAFETY:** Split string literals >200 chars into parts.
Detect CRLF before writing .md (read_bytes, then check b"\r\n"). Scan for
non-ASCII after any .md write. Revalidate anchors against disk before
printing any worker prompt.

40. **PRE-WRITE REVALIDATION:** Before any file write, re-read the target's
current disk state. Verify every anchor verbatim. Verify the assumed
structure matches reality. If anchor count != 1, or a field is missing, or
the state differs from your assumption — STOP. Report the discrepancy.
Do not write from memory or from a prior read. Same discipline applies
before printing any worker prompt (which is a write-in-words).

41. **POST-WRITE RETEST:** After every write, verify the change landed:
  - .py       -> import + related pytest
  - .ps1      -> PSParser::Tokenize
  - .md       -> line count + non-ASCII scan + diff of changed lines
  - .json     -> json.load parse
  - .java     -> mvn -q -DskipTests compile
  - any file  -> Get-Item Length + Get-FileHash
Claim "done" only after retest passes. Failure = abort + report. No
exceptions. A write that has not been retested has not been done.

---

## SECTION 11: MISTAKE HISTORY

| ID | Date | Task | Mistake | Root Cause | Preventive Rule |
|----|------|------|---------|------------|-----------------|
| M-001 | 2026-08-18 | BRIDGE_LOOP archival | Claimed files updated, provided fake download links | Confused chat with sandbox | 1, 2 |
| M-002 | 2026-08-18 | Remove BRIDGE_LOOP refs | `.Replace()` with LF in double quotes failed silently | CRLF mismatch; no verification | 3, 4, 7 |
| M-003 | 2026-08-18 | Fix stale F:\ paths | Only fixed 4 files; missed terminology.md and inventory | Assumed scope instead of scanning | 5, 7 |
| M-004 | 2026-08-18 | Path replacement | Double quotes around `$env:TEMP` caused expansion | Did not distinguish literal vs variable | 6 |
| M-005 | 2026-08-18 | Insert Rule 6 into playbook.md | Exact heading match failed silently | Punctuation/whitespace mismatch | 3, 4 |
| M-006 | 2026-08-18 | Insert row into master_index.md | `.Replace()` marker failed silently | Exact string did not match actual line | 3, 4, 7 |
| M-007 | 2026-08-18 | Repair encoding corruption | Used PowerShell 5.1 for Unicode .md edits | Default encoding caused double-encoding | 11 |
| M-008 | 2026-08-18 | Reverse mojibake | Unicode `.Replace()` keys failed silently | No match verification before writing | 3, 4, 7, 11 |
| M-009 | 2026-08-18 | Recover core_engine.md | Continued PowerShell repair after first corruption detected | Did not switch to safer tool immediately | 11 |
| M-010 | 2026-08-19 | Ghost-reference removal | Provided Python script without invocation instructions | Did not account for user's shell | 12 |
| M-011 | 2026-08-19 | Encoding verification scan | Used literal non-ASCII patterns in PowerShell; paste corrupted them | Non-ASCII unstable through console paste | 13 |
| M-012 | 2026-08-19 | Session end mistake log | Did not proactively append new mistakes before being asked | Did not execute Rule 10 | 10 |
| M-013 | 2026-08-19 | Emoji cleanup script | Hashtable with U+FE0F/U+FE0E keys treated as duplicates | Variation selectors normalize to duplicate keys | 14 |
| M-014 | 2026-08-19 | Starting Prompt confusion | Prompt implied sys_AI could access local C:\ path | No rule preventing local-path instructions | 15 |
| M-015 | 2026-08-19 | ZIP workflow cleanup | Ordered hashtable with case-insensitive keys caused duplicate-key error | Did not account for case-insensitive normalization | 16 |
| M-016 | 2026-08-19 | Case-only rename | Default `-ne` treated case-only changes as equal | Case-insensitive operators | 17 |
| M-017 | 2026-08-19 | Verification after rename | `Select-String` without `-CaseSensitive` gave false clean | No case-sensitive enforcement | 18 |
| M-018 | 2026-08-19 | Remove ZIP workflow | Broad regex deletion left broken protocol references | Deleted without checking cross-references | 19 |
| M-019 | 2026-08-19 | Append rules 16-19 | Multi-line `.Replace()` failed silently due to CRLF | Multi-line exact match fragile | 4, 7, 16 |
| M-020 | 2026-08-19 | Rebuild 03_FILE_INDEX.md | Limited word list; additional s-to-y corruption remained | Incomplete corruption inventory | 20 |
| M-021 | 2026-08-19 | Parallel worker extraction | Worker used stale session_part files and old path | Session parts not regenerated after rename | 21 |
| M-022 | 2026-08-19 | Consolidation metadata update | Duplicate A2.2 row; P1 progress not updated | No dedupe or final state verification | 22 |
| M-023 | 2026-08-19 | P-EXTRACT-001 save instruction | Reintroduced obsolete MyTradingSys_Kimi path | Stale path from memory | 23 |
| M-024 | 2026-08-19 | Session upload source ambiguity | Two staging locations caused stale worker inputs | Did not specify exact upload source path | 24 |
| M-025 | 2026-08-22 | Update grounded_theory_protocol.md status table | 10+ `edit_file` attempts failed silently on exact-string matches | File had CRLF line endings (`\r\n`); tool sent LF-only strings | 26 |
| M-026 | 2026-08-22 | Emoji cleanup across repo | Red-circle emojis found in 2 extract files; no rule preventing emoji use | No explicit "no emoji" rule existed in system files | 25 |
| M-027 | 2026-08-23 | Session start repo confusion | Read stale files from C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\ instead of actual C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys\ | Did not follow Rule 27: read 00_START_HERE.md FIRST, which specifies canonical path | 27 |
| M-028 | 2026-08-23 | Write behavioral_enforcement_protocol.md | `write_file` tool stripped all newlines; file written as single 0-line blob | Assumed `write_file` preserves multi-line strings; no verification before proceeding | 29, 30 |
| M-029 | 2026-08-29 | DSA_TASK_008-011 specification | Requested 11 new DSA fields without validating that engine needed them. Only 1 field (session.gap) actually changes decisions. Rest are computable by engine or require tick data JISHU doesn't have. | Analysis paralysis — documented problems faster than validating current system. | 31, 32, 33 |
| M-030 | 2026-08-29 | session.gap DSA request | Proposed importing DAX/CME "gap" concept into spot crypto MTS. Research confirmed: CME moved to 24/7 trading May 2026 (no new gaps). Spot crypto trades 24/7 (no closure = no gap mechanism). prior_day.close already handled correctly as structural level. | Assumed cross-market concept transfers without researching market structure differences. | 34, 35 |
| M-032 | 2026-09-10 | Speed concept research | Initial keyword grep built from intuition (9 terms). Missed: lethargic, rapid, pace, dynamic, sluggish, energetic, forceful, surge, aggressive, stall. Broader grep surfaced 6 additional Tom quotes, 3 substantive. | Derived keyword list from AI's model of Tom instead of harvesting co-occurring terms from the corpus. | 36 (new) |
| M-033 | 2026-09-14 | Coordinator dispatch to Workers B, E | Worker prompts used placeholders (`<full content>` / `<paste file here>`) instead of real file content. Both workers correctly BLOCKED. Three workers total tonight blocked on the same coordinator bug. | Coordinator prompt written before running Get-Content. Content not pasted as real text. | 38 (new) |
| M-034 | 2026-09-14 | Multiple aborted writes: placeholder in worker prompts (2x), corrupted mid-string literal (2x), missing CRLF normalization. Every failure would have been caught by Rule 40 + Rule 41. | Skipped pre-write re-read; wrote from memory. | 40, 41 |

## SECTION 14: JSON WORKFLOW — DSA SNAPSHOT TO TRADING CARD

**Protocol ID:** I-07 (JSON Input)
**Trigger:** JISHU pastes a JSON snapshot from DSA Java screener
**Canonical quickref:** this section (the per-JSON guide was archived 2026-10-15)

### 14.1 Pre-Session Checks (Run Once Per Session)
Before processing the first JSON:
1. [ ] Read research/STATUS.md for current phase, blocker, goal and system status
4. [ ] Confirm asset focus: BTCUSDT (P0) or ETHUSDT (P1)
5. [ ] Confirm timeframe hierarchy: 1W/1D (macro) -> 4H (context) -> 1H (setup) -> 15m/5m (entry)
6. [ ] Check daily loss limit: -3% = STOP
7. [ ] Check max drawdown: -10% = SYSTEM HALT
8. [ ] Verify no emoji in output (Rule 25)
9. [ ] Verify no fabricated quotes (Rule 28)
10. [ ] Read LESSONS_DIGEST.md (live-path rules)
11. [ ] Confirm trading_card_generator.md Section 1 (card principles)

### 14.2 Per-JSON Step Sequence — v4.2.0-p4 (4-Layer Workflow)
For EACH JSON snapshot:

**STEP 0 — STATE LAYER (NEW in p4)**
- Read: `mts/runtime/current_market_state.md` (persistent state from prior snapshot)
- If file missing or empty: treat as first snapshot — delta = zero, unchanged_count = 0
- Task: Load prior structural data (weekly/daily VP, swing levels, prior verdict)
- Output: old_state dict
- Budget: 1 read

**STEP 1 — DATA VALIDATION**
- Task: Parse JSON. Verify all required fields present.
- Required fields: current_price, daily_vp (poc/vah/val), weekly_vp (poc/vah/val), post_funding_vp, intraday_4h_vp, vwap, cvd, conditions, structure, order_book_depth
- Output: Data quality summary (OK / WARN / MISSING per field)
- Abort if: current_price or daily_vp missing

**STEP 2 — DELTA COMPUTATION (NEW in p4)**
- Task: Run `diff_state(old_state, snapshot)` to compute changes since last snapshot
- Output:
  - `changes[]`: list of {field, old, new, significance} — structural / contextual / positional
  - `price_delta_pct`: signed percentage change from last price
  - `substate_changes[]`: zones where price crossed boundary (below_zone → at_zone → above_zone)
  - `structural_change`: bool — did weekly/daily VP, swing levels, or prior day change?
  - `state_transition`: bool — did STATE.classification change (e.g., D → B)?
  - `unchanged_count`: int — consecutive snapshots with no structural change
- Rules:
  - Delta is DATA-DRIVEN only — no AI judgment
  - `unchanged_count` resets to 0 if `structural_change = True`
  - `state_transition = True` invalidates prior verdict
  - Fast-moving data (current_price) stored in META.last_price for delta only
- Budget: 0 tool calls (pure math)

**STEP 3 — STATE CLASSIFICATION**
- Load: `mts/conditions/market_state_rules.md` (only if state unclear from JSON)
- Task: Classify market as BALANCE or TREND (imbalance) using weekly_vp shape + daily_vp shape
- Use delta context: if unchanged_count > 0, state is stable — skip re-classification if JSON shape matches old_state
- Output: State label + confidence + source GPS
- Abort if: State = UNKNOWN and no higher-TF context available

**STEP 4 — ZONE IDENTIFICATION**
- Load: `mts/conditions/zone_identification_rules.md` (only if zones unclear from JSON)
- Task: Identify which Tom-defined zone price is at (POC, VAH, VAL, VWAP, FVG, etc.)
- Use delta context: substate_changes[] tells you which zones price crossed since last snapshot
- Output: Zone label + distance + reaction probability
- Abort if: Price is in "no man's land" (middle of value area, no edge)

**STEP 5 — SETUP TYPE SELECTION**
- Load: `mts/conditions/setup_type_rules.md` (only if state + zone suggest valid context)
- Task: Map state + zone to valid execution mode (CT/TC/BO/SC)
- Use delta context: if unchanged_count > 2 and state stable, setup type likely unchanged — verify quickly
- Output: Valid mode(s) + invalid mode(s) + WHY per mode
- Abort if: No valid mode for this state+zone combination

**STEP 6 — PROOF GATE**
- Load: `mts/conditions/proof_requirements_formatted.md` (only if setup candidate exists)
- Task: Check which proof types are present from JSON data:
  - Break below/above key level (from conditions.price_vs_poc, price_vs_va)
  - CVD direction (from cvd.slope, cvd.divergence)
  - Book pressure (from order_book_depth.bid_ask_ratio)
  - FVG presence (from conditions.fvg_unfilled_count)
  - Structure break (from structure.stale flags)
  - Absorption/rejection/delta flip/finished auction → [UNKNOWN] — requires visual validation
- Use delta context: compare CVD.slope, trade_flow.net_delta, VWAP.slope to prior — flag contradictions or alignments
- Output: Proof present list + proof missing list + gap flags
- Abort if: Zero proof types present (idea without proof = guess)

**STEP 6.5 — TRIGGER SELECTION**
- Load: `mts/conditions/entry_timing_triggers.md` **Section 0.5 (Runtime Quickref only)**
- Task: Identify the specific trigger that converts 'proof present' into 'enter now':
  - Match execution mode to trigger category (CT/TC/BO/SC)
  - Check trigger hierarchy: Tier 1 structural → Tier 2 order-flow → Tier 3 momentum → Tier 4 time
  - Determine execution method: limit at zone, market on trigger, stop above/below
  - Flag crypto-specific timing (funding reset window, liquidation flush)
- Output: Trigger type + execution method + entry price zone + timing constraints
- Abort if: No valid trigger for proof type OR trigger puts stop beyond last liquidity
- **Load full file only if:** Trigger gap flagged (e.g., unknown proof type, ambiguous zone hold)

**STEP 7 — VISUAL VALIDATION (When Flagged)**
- If proof missing includes footprint items (absorption, rejection, delta flip, finished auction):
  - Ask JISHU: "Pull 15m footprint from CoinGlass. Do you see [specific proof type] at [level]?"
  - JISHU replies yes/no/describes
  - Update proof list based on JISHU's response
  - Reference: proof_requirements_formatted.md Section 2.3 for definitions
- Budget: 0 tool calls (conversation only)

**STEP 8 — RISK VALIDATION**
- Load: `mts/conditions/risk_protocol.md` (only if proof present)
- Task: Calculate stop, target, position size, R:R (NET after 25% friction)
- Stop: Use structure object (swing_low for longs, swing_high for shorts). If stale=true, use post-funding VAL/VAH as structural reference.
- Target: Nearest POC or VAH/VAL in direction of trade
- Output: Stop level + target level + R:R ratio + position size % + invalidation condition
- Abort if: R:R < 2:1 (NET) OR stop violates "below last liquidity" rule

**STEP 9 — VERDICT**
- Apply verdict hierarchy (no tool call needed — logic embedded here):
  - NO TRADE / WAIT — any mandatory condition FALSE or UNKNOWN
  - EVALUATE — all mandatory TRUE + at least one proof present
  - SETUP CONFIRMED — all mandatory + primary + secondary TRUE
- Output: Verdict label + confidence band + downgrade triggers

**STEP 10 — TRADING CARD OUTPUT**
- Load: `mts/cards/trading_card_generator.md` (format reference)
- Task: Fill card template with data from Steps 0-9
- Card MUST include DELTA section (Section 2.3.5 per trading_card_generator.md)
- Output: Complete trading card (speed-optimized, <10 sec scan)
- Budget: 1 read + write

**STEP 11 — STATE PERSISTENCE (NEW in p4)**
- Task: Run `update_state(old_state, snapshot)` → `format_state(new_state)` → persist via shell
- Write updated state to `mts/runtime/current_market_state.md` using shell tool:
  ```
  cat > C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\MyTradingSys/runtime/current_market_state.md << 'EOF'
  [content from format_state]
  EOF
  ```
- Preserve last_verdict from old state unless structural_change occurred
- Output: Updated state file on disk
- Budget: 1 write (shell tool)

### STATE LAYER RULES
- current_market_state.md is OVERWRITTEN per snapshot (not appended)
- If file missing or empty, treat as first snapshot — delta = zero, unchanged_count = 0
- Delta is DATA-DRIVEN only — no AI judgment in diff_state()
- unchanged_count resets to 0 on any structural_change = True
- last_verdict preserved across snapshots unless structural_change occurs
- Fast-moving data (current_price) stored in META.last_price only for delta computation
- State layer functions live in mts/runtime/mts_math.py: parse_state, diff_state, update_state, write_state

### 14.3 Decision Diamond Logic
At each step, apply this gate:

```
Data OK? -> YES -> State Known? -> YES -> Zone Edge? -> YES -> Mode Valid? -> YES -> Proof Present? -> YES -> Trigger Valid? -> YES -> R:R OK? -> YES -> VERDICT
           |NO               |NO               |NO               |NO               |NO                |NO               |NO
        ABORT:           ABORT:            ABORT:           ABORT:           ABORT:            ABORT:           ABORT:
        "JSON            "State            "No edge         "No valid        "Idea without      "No trigger       "Math not
         data             unknown —          at this          mode for         proof =           for this          on side"
         missing"         need higher TF"   level"           this context"    guess"            proof type"
```

### 14.4 Verdict Scoring (4 Bands)
| Band | Score | Meaning | Action |
|------|-------|---------|--------|
| A — SETUP CONFIRMED | 90-100 | All mandatory + primary + secondary TRUE | JISHU may execute per risk protocol |
| B — EVALUATE | 70-89 | All mandatory TRUE, some primary/secondary UNKNOWN | JISHU evaluates; partial size OK |
| C — WAIT / WATCH | 40-69 | Some mandatory UNKNOWN, no FALSE | Set alerts, wait for price to reach level |
| D — NO TRADE | 0-39 | Any mandatory FALSE | Do not trade. Log reason. |

### 14.5 Abort Conditions (Hard Stops)
1. JSON data missing critical fields (price, daily_vp) -> WAIT
2. Market state UNKNOWN -> WAIT (need higher TF)
3. Price in no man's land (no edge) -> WAIT (set alerts at levels)
4. No valid execution mode for state+zone -> WAIT
5. Idea without proof -> NO TRADE (Tom: "flying blind")
6. R:R < 2:1 NET -> NO TRADE (math not on side)
7. Stop violates "below last liquidity" -> NO TRADE (risk rule violation)
8. No valid trigger for proof type -> NO TRADE (proof without trigger = premature entry)
9. Daily loss limit hit (-3%) -> SYSTEM HALT

### 14.7 Output Format
Every JSON analysis MUST produce:
1. One-line verdict summary
2. Trading card (per trading_card_generator.md spec)
3. List of loaded rule files (for traceability)
5. Data quality flags (WARN items from JSON approximation)

---

# END
