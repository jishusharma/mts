# Apparatus Fixes
# Started 2026-09-12. Last updated 2026-09-13.
# Purpose: track issues and fixes for the trading-day apparatus.

## HOW TO PATCH (rules)

### Read before write
1. Backup to backup_YYYYMMDD_HHMMSS/ first.
2. Select-String -Context N the target region.
3. Anchor = literal string from that output.
4. Abort if match count != 1.
5. Verify syntax after write.
6. Grep for the new symbols.

### Atomic delete
Delete + backup + grep happen in ONE block. Never split across turns.
Grep uses all likely name variants (underscore, spaced, capitalized).

### Never invent names
If a term or shorthand isn't explained, ASK. Do not guess. Do not
write a fabricated expansion to any file. Do not fabricate the origin
of a name. Do not rewrite history to cover an earlier error.

### Heredoc pitfall
PowerShell @'...'@ corrupts on paste when >30 lines or contains
$(), backticks, or nested here-strings. Use a temp .py file for any
patch >20 lines.

## LIVE FIXES

| Fix | What it does | Where |
|-----|--------------|-------|
| Forming-bar read | Drop last (forming) kline before all derivations | MarketDataSnapshot.java (dropFormingBar) |
| net_rr_sanity gate | Read >= 2.0 NET, not >= 1.5 gross | math_object_builder.py |
| Candle-close alignment | Fire at :10 past boundary | start_trading_day.ps1 |
| Singleton lock | PID TS format, stale > 600s auto-clears | start_trading_day.ps1 |
| Alert cooldown | 180s between popups | start_trading_day.ps1 |
| Materiality gate | Fire on band change, not field churn | start_trading_day.ps1 |
| Actionable popup gate | Popups fire on WATCH / SETUP_FORMING / SETUP_CONFIRMED / state change. `-Popups off` disables. | start_trading_day.ps1 |
| State-code staleness | Flag state_code.json > 90s in live mode | start_trading_day.ps1 |
| Trend override | below_val + CVD falling vs LONG -> WAIT_RR (and mirror) | start_trading_day.ps1 |
| Popup behind IDE | TopMost=false, kill-prior on spawn, 5min TTL | show_alert.ps1 |
| Proof direction | pd flag in card (BUG-008) | math_object_builder.py |

## PARKED

| Fix | Why parked |
|-----|-----------|
| alignment_pass field | Not read by any engine rule. Reports "fail" on closed bars because the 1w bar is naturally older than 0.1%. |
| proof_direction_details | Empty in some cards. Cosmetic. |

## OPEN

- Trend override: 2 of 3 Rule 32 snapshots collected. Third pending.
- Event probability layer: parked until outcome labels >= 500.
  Current: 154. See event_probability_layer_DESIGN.md.

- L9 (2026-09-14): State-machine counters survive restart.
  state_code.json persists state, transition_chain_15m, seconds_in_state, and
  last_transition_utc. On restart, StateCodeEmitter.restoreStateFromDisk reads
  state_code.json and seeds currentState + transitionChain. Consequence:
  transition chain is continuous across restarts; the 15m window includes
  pre-restart transitions. If a restart occurs after prolonged silence, the
  chain may show an artificially dense transition burst that predates the
  new session. Verify by comparing state_code.json.mtime to apparatus_log
  restart line. No code change. Documentation note only.

## SESSION NOTES 2026-09-12/13

- DSA reads closed bars only (Rule 37: restores intended behavior).
- Apparatus single-instance with lock + stale clear.
- Session SSOT live: session_state.json (thesis), session_log.json (decisions).
- Outcome labeler runs per cycle, accumulates forward returns.
- 4-AI research on conditional event probability: concept sound, named
  events unground-truthable from snapshot. Redefine as forward kline
  outcomes. Parked pending data.

## SESSION NOTES (historical, post-END relocated 2026-09-15)

## RULE 32 CONFIRMED: trend override (2026-09-13)
Third evidence collected — cycle 4 of 20:00:30 session:
  price 77123.40 | B/below_val | nrr 2.02 (PASS) | p=5 | pd=aligned
  -> SETUP_FORMING would have fired (nrr + proof both pass)
  -> suppressed to WAIT_RR by broken-value override.
3/3. Behavior verified on live data. No longer provisional.

## session_log append bug (2026-09-13 20:18-20:26)
Symptom: "session_log append failed: The regular expression pattern \ is not valid."
Cause: `-replace "\\", "/"` in the here-string collapsed to `-replace "\", "/"`
       which the regex engine rejects as a lone escape.
Fix:   switch to `.Replace("\", "/")` - literal, not regex.
Impact: 3 alerts (221, 222, 223) fired but were NOT appended to session_log.
        Counter still incremented. Only the log write failed.

## Backup policy (2026-09-13)
One backup per session, not per patch. Create backup_<date>_session/ at session
start; overwrite files inside as they're edited, don't create new dirs.
Exception: edits to compiled_engine.md, 01_AI_BEHAVIOR.md, DSA_SESSION_PROMPT.md
get their own named dir. Retention: 1 most recent. New session backup overwrites the previous one. Older auto-deleted.
Incident: 14 backup dirs created in one session, all sequential. Wasteful.

## Backup policy — corrected 2026-09-13
One dir per session, fixed name: backup_session/.
Created once at session start. Files copied in with -Force on each edit.
Never create backup_<timestamp>. Never create a second backup dir.
Pre-action rule: BEFORE any New-Item/Directory/copy, glob for existing.
If it exists, use it. If not, create. Never default to fresh.
Same rule applies to IDs, filenames, labels: check-then-act, not create-then-dedupe.


## VVP-002 written (2026-09-13)
File: MyTradingSys/mts/research/visual_validation_protocol_vvp002.md
Extends VVP-001. Covers: heatmap protocol, footprint protocol,
field-to-visual tables per screenshot type, quad reconciliation,
order of operations, failure flags.
Two corrections applied from worker draft:
  B.3 - deprecated liquidation_clusters.* check removed
  G.2 - visual-contradicts is flag-only, no auto band downgrade (Rule 32)

## VVP-002 G.2 reconciliation (2026-09-13)
Source of truth: flag-only. No auto band downgrade.
Rationale: Rule 32 - a visual flag cannot modify a verdict without 3-snapshot evidence.
VVP-002 line 219 updated to match this policy. Footer above was already correct.
Verified by || session: VVP-002 md5 5AB58C80... prior to patch showed band-downgrade text.

# END

## SESSION 2026-09-16 BOM fix (permanent)

Root cause: PS 5.1 `Set-Content -Encoding UTF8` always writes a BOM.
BOM breaks Python `json.load`. Recurred many times.

Fix:
- `Write-NoBom` and `Write-NoBomLines` in scripts\core\shared-functions.ps1.
- `Test-HasBom` to check any .py, .json, .ps1.
- Build-Check.ps1 scans runtime *.py, *.json and scripts\*.ps1 for BOM.
- USER.md FILE WRITES rule added.

Verify: three files clean today (regime_classifier.py, state_code_regime.json, shared-functions.ps1).
## SESSION 2026-09-16 AI MISTAKES (for token saving)

1. Flagged "no .git" from a listing made without -Force. Dotfolders hidden. Always use -Force on dotfolder checks.
2. Piped after a foreach close-brace twice. Parser error both times. Capture in a variable first.
3. Set anchor count threshold to 2 when occurrences were 1. NEXT_SESSION_HANDOFF missed one turn.
4. Asked A/B on Dumps when principle ("remove kimi naming") already decided it. Apply stated principle first, ask only if ambiguous.
5. Split backup-then-purge into two turns when target was regenerable. One turn would have done.
6. Long prose where USER.md says answer first, terse.

## SESSION 2026-09-16 CLEANUP LANDED

- 10 stale DUMP_*.md moved to backup.
- 11 files renamed: kimi_*_dump.md -> dump_*.md, java_core_dump.md -> dump_java.md.
- Dump_All.ps1, Build-Check.ps1, CAPABILITIES.md, 00_START_HERE.md, NEXT_SESSION_HANDOFF.md, L_ITEMS_MASTER.md updated.
- L23 closed.
- backup_session purged (clean).
- SESSION_PASTE.txt generator extended: git state, loop health, scripts inventory, COMMANDS.md inline.

## SESSION 2026-09-16 OPEN FINDINGS

### O1 - state_code.signals.cvd_slope empty
FIXED 2026-09-16. Root cause: computeCvdSlope gated on 40 samples = 40 min warmup after every restart, and restoreStateFromDisk did not restore cvdSeries. Fix: CVD_MIN_SAMPLES=10, adaptive half-window, denom max(|older|,1.0). Java compile PASS. Live state_code.json now emits bearish/bullish/neutral. L26 closed.

### O2 - AI methodology: endpoint guessing
Before calling any external endpoint to verify a snapshot field, read MyTradingSys/data/data_schema_v1.2.0.md or MTS_DICTIONARY.md for the field definition first. Wasted two turns calling spot endpoint when snapshot current_price is futures mark.

### O3 - boot paste does not inline field table
SESSION_PASTE.txt lacks the CANONICAL FIELDS table from MTS_DICTIONARY.md. Cause of O2. Fix: extend scripts/start-session.ps1 to extract and inline that table.

# END

## SESSION 2026-09-17 AI MISTAKES

1. Self-assigned WORKER role in a COORDINATOR session when the operator asked for a
   || session. || means a separate verification session per this file (VVP-002 note).
   Correct action: dispatch a fresh chat with a self-contained worker prompt.

2. Flip-flopped when challenged on the worker question. Should have owned the first
   mistake cleanly and stated the correct interpretation, not re-explained a wrong
   approach as if it had been right.

3. Handed the worker PowerShell commands expecting it to execute them. The worker has
   no shell. Operator runs all commands. Worker only analyzes pasted output.

4. Method-listing regex was too narrow: missed constructors, generic return types
   (List<, Map<, Optional<), arrays, and deeper indents. Worker caught this. Inventory
   would have been incomplete.

5. Used "jar" as shorthand for the running Java process. No jar exists in this project;
   the loop runs via mvn exec:java -Dexec.mainClass=datafeed.Main. Wrong word, dropped.

6. Overstated "compiled_engine.md self-contradicts" on L30 vs L322. Precise claim is:
   two consumers read the same field with different meanings. The file was not
   self-contradicting, the consumers were disagreeing.

All six were stated by the AI, not inferred by the operator. Each was corrected
in the same session it was made, except #1 and #2 which required a stop.

# END OF SESSION 2026-09-17 MISTAKES

## SESSION 2026-09-17 COORDINATOR WORK (MTS-2026-09-17-1037Z)

1. I36 status corrected to CLOSED 2026-09-17 in L_ITEMS_MASTER.md.
   Code fix confirmed in start-trading-day.ps1 (pendingStateFrom at L319, L419, L422).
2. L_ITEMS_MASTER.md had 3 mojibake sequences, replaced with plain hyphen. File now 0 non-ASCII.
3. Build-Check.ps1 extended: scans runtime *.py, runtime *.json, research *.md, scripts *.ps1.
   Flags BOM and the CP1251-decoded mojibake signature. STATUS FAIL on either hit.
4. Stale math test corrected: test_mts_math.py:477 asserted classification == "B", now "trend_healthy".
   Test predates the 2026-09-17 classifyState rewrite.
5. Build-Check math line reports 125 tests; direct pytest reports 130. Build-Check uses
   --ignore for docs; the direct run did not. Discrepancy flagged, not resolved.

Remaining mojibake flagged by new Build-Check: session_log.json (53), apparatus_fixes.md (4),
MTS_DICTIONARY.md (89). Not fixed this turn.

# END OF SESSION 2026-09-17 COORDINATOR WORK

# PERMANENT SAFEGUARDS (added 2026-09-17)

Two classes of file corruption are now detected at every boot by Build-Check.ps1:

1. UTF-8 BOM at file start. Breaks Python json.load.
   Scan covers: MyTradingSys\mts\runtime\*.py, runtime\*.json, research\*.md, scripts\*.ps1.
   Fix at write time: use Write-NoBom / Write-NoBomLines from scripts\core\shared-functions.ps1.

2. CP1251-decoded mojibake. Source: copy-paste through a misdecoded console.
   Signature: any codepoint in U+0400-U+04FF. This repo has no legitimate Cyrillic.
   Permitted non-ASCII: typographic characters that are not Cyrillic.
   The Build-Check Non-ASCII line counts Cyrillic (U+0400-U+04FF) only.
   Permitted today, seen in repo: U+00A7 section sign, U+2014 em-dash,
   U+2013 en-dash, U+2192 right arrow, U+00D7 multiplication sign,
   U+2260 not-equal, U+2713 check mark, U+00B1 plus-minus, U+2248 approx,
   U+00B2 squared, U+2212 minus. Do not chase these in build reports.
   Fix at write time: never write pasted text back without running Build-Check first.

Rule for every session that writes any file under the scanned roots:
  After the write, run .\scripts\Build-Check.ps1. If STATUS is FAIL, fix before commit.

Third class: stale test assertions after a behavior change.
  When a code change alters a return value or field meaning, update the matching test
  in the same turn. Example: classifyState rewrite on 2026-09-17 changed the return
  space to balance/trend_unhealthy/trend_healthy; test_mts_math.py:477 still asserted
  "B" and failed at next boot. Fixed 2026-09-17.

# END OF PERMANENT SAFEGUARDS
