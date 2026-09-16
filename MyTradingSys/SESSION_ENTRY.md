# MTS SESSION ENTRY — READ FIRST
# MTS version: see VERSION
# Purpose: Single doc that tells any fresh AI session what to read,
# what is running, and what state we are in.
# Supersedes: manual discovery. Read this BEFORE 00_START_HERE.md.

## 1. READ ORDER

See DSA_SESSION_PROMPT.md section 3 for boot order.

Do NOT read the full 12-file dump unless asked. That was session 2026-09-12.

## 2. WHAT IS RUNNING

The apparatus is a PowerShell loop that:
- Fetches a fresh Binance snapshot every N minutes (candle-close aligned, +10s)
- Runs Python math layer (math_object_builder, mts_math)
- Runs `build_mo_cli.py` to get BUG-008 proof direction
- Computes a verdict from snapshot + rules
- Fires alerts on material change (popup + beep + log)
- Appends to session_log.json on every alert
- Runs outcome_labeler.py (labels past snapshots with forward returns)

Load aliases: `. .\scripts\load.ps1`  ->  lx ld lt lf lc lh la
Start:        `.\scripts\core\mode.ps1 -M armed`
Stop:         `.\scripts\core\stop-day.ps1`
Modes:        prep (5m) | armed (1m) | live (1m, needs -Direction -Entry -Stop -Target)

State machine is spawned as a child java process by scripts/core/start-trading-day.ps1.
It writes `mts/runtime/state_code.json` every 60s.

Scripts moved to scripts/ on 2026-09-15 (previously at root).

## 3. CURRENT STATE (update per session)

**Last live read:** BTC 76,999.60 | B/in_va | 2026-09-15T10:25:23Z
**Thesis:** neutral, low confidence. No active direction.
**Next trigger:** none set.
**Invalidates:** none set.
**Apparatus:** RUNNING. Restarted 2026-09-15 10:24 UTC (cycle 1 at 10:25:12). Prior loop died 2026-09-15 00:52:24 UTC — L18 recurrence (silent exit, no error logged).
**Open items:** see MyTradingSys/mts/research/L_ITEMS_MASTER.md. 3 held, 1 open (L8), 7 new cleanup (L13-L20).

## 4. HARD RULES

**Shorthand:** Send many commands in one block.

Read-before-write, no blind java kill, and write pattern: see DSA §8, §11, Rules 40-41.

## 5. KEY FILES

| Path | Purpose |
|---|---|
| `start_trading_day.ps1` | Apparatus loop |
| `mode.ps1` | Mode switcher (kills + starts) |
| `stop_day.ps1` | Clean stop |
| `show_alert.ps1` | Popup form |
| `MyTradingSys\mts\runtime\session_state.py` | SSOT helper |
| `MyTradingSys\mts\runtime\log_decision.py` | One-line decision logger |
| `MyTradingSys\mts\runtime\outcome_labeler.py` | Forward-return labeler |
| `MyTradingSys\mts\runtime\build_mo_cli.py` | Proof direction helper |
| `MyTradingSys\mts\research\MTS_DICTIONARY.md` | Field dictionary - every field name, source, authority |
| `MyTradingSys\mts\research\apparatus_fixes.md` | Fix log + open items |
| `MyTradingSys\mts\research\event_probability_layer_DESIGN.md` | Parked research |

## 6. RECENT SESSION ARC (2026-09-12/13)

Phase 1 — Dev cleanup: W1/W2 worker lanes closed. Main.java dead code removed.
Liquidation REST (404) removed. net_rr_sanity gate fixed (BUG-011).
MTF design doc contradiction resolved.

Phase 2 — Apparatus build: candle-close alignment (Rule 37), singleton lock,
cooldown, materiality gate, trend override, popup behind IDE.

Phase 3 — SSOT: session_state.json + session_log.json + log_decision.py
+ outcome_labeler.py + SESSION_ENTRY.md (this file).

Phase 4 — Research: 4-AI review of conditional event probability layer.
Verdict: concept sound but named events unground-truthable from snapshot.
Redefine as forward kline outcomes. Prerequisite: 5-10k labeled events.
Currently 130 labels. Design parked. Build in 3-6 months.

## 7. NEXT SESSION DEFAULT

See DSA_SESSION_PROMPT.md §3 (boot block owns this).

# END
