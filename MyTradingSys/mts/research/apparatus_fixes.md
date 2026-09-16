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

# END