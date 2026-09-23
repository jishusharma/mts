# NEXT SESSION HANDOFF
# Rewritten 2026-09-23T19:30Z by MTS-2026-09-23-1730Z.

STATUS: Loop ALIVE (wrapper 9260, state-machine 4336, java 13032). Build PASS at 19:26:16Z.
Commit af7f114. Tag last-snapshot at af7f114.

## SESSION MTS-2026-09-23-1730Z - WHAT LANDED

- DSA_SESSION_PROMPT.md section 1: Independent worker role removed. One
  WORKER type only. 238 -> 233 lines.
- live_session_protocol.md: WORKER TYPES collapsed to one type; I1-I8
  removed. Stray # END and duplicate rule 15 cleaned; rule 16 added.
- Build-Check.ps1 L131 label corrected to "Cyrillic codepoints (0x0400-0x04FF)".
- B058 CLOSED. Parts C + D already on disk (start-trading-day.ps1 L211-215
  and L576-580). Receipt filled.
- B062 CLOSED. Position-aware alert gating landed at start-trading-day.ps1
  L589-612. Suppress WATCH; suppress same-direction SETUP_FORMING; elevate
  opposing SETUP_FORMING.
- B065 CLOSED. Stale-swing checks wired in two consumers:
  SetupCandidatesBuilder.extractZones L334-350, and stop selection L101-109.
- T039 CLOSED. Enforcement already on disk at Build-Check.ps1 L159-163.
- T042 PARTIAL. Producer emits structure.1w/1d/4h now. Row stays OPEN.
- T043 WONTFIX.
- B059 reverted. Consumer-side static state was wrong. Fix belongs on the
  producer side (MarketDataSnapshot.buildStructure), keyed on the funding
  window, not the session.
- Timestamp fix: start-trading-day.ps1 L130 renders ISO explicitly now.
  Was culture-dependent (rendered 09/23/2026 19:14:18 after restart).

## CRITICAL NOTE - T042 WIRING GAP

T042 added structure.1w, structure.1d, structure.4h to every snapshot.
These keys are EMITTED but NOT WIRED. No decision function reads them.

Per live_session_protocol.md rule 15: a layer is wired only when a named
decision function reads its value and two fixtures differing only in that
layer produce a different verdict or reason string. Emitted-but-unread is
exempt with a tracked reason, not done.

Current readers of structure.*:
- extractZones reads structure.1h, structure.15m, structure.5m only.
- getSwingTF maps weekly_ -> 1h, daily_/pf_/4h_ -> 15m, vwap/fvg/5m_swing_ -> 5m.
  It never asks for 1w, 1d, or 4h.

Options to close T042:
A. Wire getSwingTF to return 1d for daily_ zones, 1w for weekly_ zones,
   4h for 4h_ zones. Changes stop selection. Needs evidence that this
   improves stop quality.
B. Add a new named consumer for 1w/1d/4h structure (e.g. HTF bias gate).
C. Document as intentional emission and close T042 producer-only.

Also still open on T042: OI peak and CVD peak reference are not emitted.

## OPEN QUEUE (BUGS.md, open rows only)

- B059 : producer-side pf_vp freeze. MarketDataSnapshot.buildStructure.
- B063 : divergence wiring. Needs operator decision: restore in schema OR
         deprecate.
- T034 : blocked on Rule 33 consumer.
- T035 : T1 web pass pending.
- T037 : Java tests blocked on pom (no surefire, no JUnit).
- T038 : self-deferred until ~21000 labels.
- T040 : new rule surface needs Tom citation.
- T042 : see CRITICAL NOTE above.

## NEXT SESSION - FIRST ACTION

1. Loop health + Build-Check.
   .\scripts\Build-Check.ps1
   Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match
     "statemachine|loop-supervisor|start-trading-day" } |
     Select ProcessId, Name
2. T042 wiring decision: option A, B, or C above.
3. B059 producer-side freeze.
4. B063 operator decision, then wire.

## HARD RULES

- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row.
- Critical files: hash, edit, hash, print.
- Read the target line from disk in the same turn before composing an anchor.
- Build-Check prints to host, not stdout. Do not capture into a variable.
- MarketDataSnapshot.java is CRLF. PS source is LF. Match on write.
- Handoff 1445Z mojibake claim was wrong. Files are clean UTF-8. No fix needed.

# END