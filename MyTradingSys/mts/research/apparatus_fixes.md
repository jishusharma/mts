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

# END
