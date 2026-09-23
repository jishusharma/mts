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
- start-session.ps1 manifest entry without lines (2026-09-17): any `read: tail`
  entry missing a `lines` field crashes the script with a cryptic Tail binding
  error. Should default to 60 or warn. One-line guard.
- start-session.ps1 guard CLOSED 2026-09-19: verified present at start-session.ps1 L46: $n = if ($f.lines) { [int]$f.lines } else { 60 }. Entry was phantom.

- Pre-open playbook gap (2026-09-17): London-NY handoff on 09-17 produced a
  474-point ramp (12:11-12:31 UTC) then a 510-point fade (12:31-13:24).
  Engine stayed short-biased, net reward to risk 1.75-2.15, and did not fire.
  No condition-file rule names the pattern. No session frame available until
  13:30 UTC anchor. Decide next session: build a rule or mark permanently manual.

- L9 (2026-09-14): State-machine counters survive restart.
  state_code.json persists state, transition_chain_15m, seconds_in_state, and
  last_transition_utc. On restart, StateCodeEmitter.restoreStateFromDisk reads
  state_code.json and seeds currentState + transitionChain. Consequence:
  transition chain is continuous across restarts; the 15m window includes
  pre-restart transitions. If a restart occurs after prolonged silence, the
  chain may show an artificially dense transition burst that predates the
  new session. Verify by comparing state_code.json.mtime to apparatus_log
  restart line. No code change. Documentation note only.


- 2026-09-18T17:47Z wrapper died after cycle 39 (17:02Z). No lock, no supervisor. Java orphaned (14444, 2764). Restarted.
- 2026-09-19 stage 3a: loop flag exit does not tree-kill state-machine java. Stop-Process on the intermediate powershell (StateMachinePID) leaves the mvn java child orphaned. Observed java 13928 alive after clean flag exit. Same class as B014. 3b must tree-kill (taskkill /F /T /PID) or the java orphan survives every stop.
# END
- 2026-09-20 PROOF DIRECTION RULE (learned fact): proof_direction is set in math_object_builder.py L383-407. Exactly three checks per direction. For a LONG, contradiction if any of: finished_auction.direction == 'buy', OR book_imbalance < 0.33, OR cvd.last_3_delta all 'negative'. For a SHORT, mirror: 'sell', > 3.0, all 'positive'. Downstream: start-trading-day.ps1 L166 downgrades SETUP_FORMING to non-forming when proofDir == 'contradiction'. The threshold for the book check is exactly 0.33 (long) and 3.0 (short). Observed 0.32 on 2026-09-19T22:33Z fired the long check. Feed line 'book_imbalance=0.32 ask-heavy vs LONG' is verbatim code output, not editorial.

- 2026-09-20 MONITOR CADENCE: _scratch_monitor.ps1 polls every 15s but prints only on snapshot change. Snapshot cadence is 60s (wrapper, candle close + 10s). Result: uneven output, long gaps between prints. Improvement: add a 'no change' heartbeat line every ~30s so the operator can see liveness.
- 2026-09-20 SINGLE-VALUE ERROR (operator flagged): quoted snapshot cvd=64.22 as 'flat' without comparing to the prior cycle (cvd=-77.2 at 00:09). The +141 swing over 3 minutes was the real signal. Rule: any snapshot field quoted in a read must include the prior-cycle value for comparison.
- 2026-09-20 VERIFY-BY-READ: two instances this session of asserting without reading source first. Pattern 'state machine' should have been 'statemachine'. Tape interval asserted as 70s, actual param is 30s. Rule: before issuing any wait, threshold, or regex, print the exact source value in the same block.
- 2026-09-20 SUPERVISOR COVERAGE GAP: wrapper chain is supervised (loop-supervisor.ps1). Tape sidecar (tape-watch.ps1) is not. If the sidecar dies, live_tape.md goes stale silently; MTS-TAPE prints STALE but nothing restarts it. Candidate: extend supervisor to watch the sidecar lock, or add a stale-field alarm in mts-watch.ps1.
- 2026-09-20 LIVE ANALYSIS SUPPORT BASELINE: 7 files (snapshot, state_code.json, current_market_state.md, state_code_regime.json, apparatus_log.txt, klines 15m/1h/5m, live_tape.md) and 6 processes (supervisor, wrapper, intermediate ps, mvn cmd, java, tape sidecar). Verified fresh and chained at 2026-09-20T00:12Z.
- 2026-09-20 MTS-LIVE vs LIVE = SAME SOURCE: both read the same snapshot file. They cannot disagree. Cross-checks must use state_code.json, current_market_state.md, or raw snapshot JSON, not the two rendered views.
- 2026-09-20 MONITOR PENDING: operator asked for 30s heartbeat option. Not yet implemented. Small edit to _scratch_monitor.ps1: emit '=== HH:MM:SS no change, snap age=Ns ===' when snapshot name equals lastSnap. Deferred.

- 2026-09-20 ALERT CARD FORMAT GAP (found by investigation of #607): the card's WHY line shows the verdict reason (e.g. 'price not at zone'), not the alert trigger reason. When #607 fired at 01:11:23 the trigger was 'STATE TWOPEAK/in_va -> TWOPEAK/below_val', but the card showed WAIT_TRIGGER / 'price not at zone'. Operator saw the popup moments later when price had recovered toward the zone, and the card price was from the detection instant 81143.6. Card is internally consistent but omits the trigger field. Recommendation: add TRIGGER line listing the exact change that fired the alert.
- 2026-09-20 ALERT RATE HIGH: log shows 16 alerts from 23:54 #589 to 01:16 #608 in 82 minutes. Cooldown 180s. Several are state changes or zone rotations rather than verdict changes. Confirm whether state and zone-change alerts should fire independently, or be batched.

- 2026-09-21: log tail is not a health check. Loop-state claim requires wrapper PID + lock + log mtime in the same read.

# END
- 2026-09-23 MTS-2026-09-23-0831Z: PowerShell does not escape quotes with backslash. A double-quoted string with \" parses as literal backslash then unescaped quote and breaks the whole block. Use single-quoted strings for lines containing embedded double quotes, or the create-empty-file-plus-Notepad pattern for doc bodies. Three consecutive write attempts failed on this in one session.

- 2026-09-23 verify method: PowerShell $str.Split($q) splits on every char of $q, not the substring. Verbatim checks must use [regex]::Matches($new, [regex]::Escape($q)).Count. First run of this check reported counts of 9000+ and was discarded.
- 2026-09-24: handoff MTS-2026-09-23-1445Z reported mojibake at start-trading-day.ps1 L582 and MTS_DICTIONARY.md L41. Verified on disk: both hold E2 80 94 (U+2014 EM DASH), clean UTF-8. No mojibake present. Real defect: Build-Check.ps1 L125 scans Cyrillic codepoints only (0x0400-0x04FF); the BUILD_REPORT label at L131 read "Non-ASCII files", which overstated scope. Label changed to "Cyrillic codepoints (0x0400-0x04FF)". No edits to L582 or L41.
