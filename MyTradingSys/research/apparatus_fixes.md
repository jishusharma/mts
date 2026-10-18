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

## WINDOWS PROCESS LAUNCH (added 2026-09-25)

Loop survives IDE close only if both loop processes escape the IDE terminal job. Three failed mechanisms, one working:

| Mechanism | Result | Reason |
|---|---|---|
| Start-Process -WindowStyle Hidden from pwsh | dies with terminal | same job object |
| schtasks.exe /create /tr "..." | Invalid argument/option - '-Mode' | schtasks parses its own args first |
| WMI Win32_Process Create | return code 8 | runs as SYSTEM, cannot reach Store pwsh |
| VBS WshShell.Run + Register-ScheduledTask | works | runs as user, outside terminal job |

Working pattern for any process that must survive terminal close:
1. Write a .vbs with sh.Run "<command>", 0, False.
2. New-ScheduledTaskAction -Execute wscript.exe -Argument "//nologo <vbs>".
3. Register-ScheduledTask with a far-future trigger.
4. Start-ScheduledTask.

mode.ps1 owns this. Do not launch the supervisor or wrapper by hand.
## PARKED

| Fix | Why parked |
|-----|-----------|
| alignment_pass field | Not read by any engine rule. Reports "fail" on closed bars because the 1w bar is naturally older than 0.1%. |
| proof_direction_details | Empty in some cards. Cosmetic. |

## OPEN (fix queue, action items)

- L99 state-machine java orphan on stop: use taskkill /F /T /PID on the wrapper tree, not Stop-Process on the intermediate powershell. Target file for stage 3b: scripts\core\stop-day.ps1 (not yet verified). Classified fix-now by worker W5. Reply: Dumps/workers/CLOSE-2026-09-25/W5-apparatus-fixes/REPLY.md
- L111 alert card format gap: card missing a TRIGGER line listing the exact change that fired the alert. Target: alert card renderer (file and line not yet verified). Classified fix-now by worker W5.

## NEEDS OPERATOR

- L73 trend override: collect or confirm third Rule 32 snapshot.
- L81-85 pre-open playbook gap: build condition-file rule for London-NY handoff or mark permanently manual.
- L103/L109 monitor cadence: implement or keep deferred the 30s heartbeat edit to _scratch_monitor.ps1.
- L106 supervisor coverage gap: extend supervisor to watch tape sidecar lock, or add a stale-field alarm in mts-watch.ps1.
- L112 alert rate: state and zone-change alerts fire independently or be batched.

All five flow into the session-close operator decision block (Wave 9).

## CLOSED THIS SESSION (2026-09-25)

- L76-78 start-session missing-lines guard: already fixed at L46.
- L79 start-session guard: verified present at L46.
- L98 wrapper died 2026-09-18: restarted; supervisor chain live.
- L120 mojibake report: verified clean; Build-Check label corrected.

- 2026-10-12 d9306fe relay host=<NAME> task tag: kick lints the committed handoff for its own host and IDLEs when every open task is another host's; handoff/lint ignore host unless --host. 29 relay tests green (tests/test_relay.py).

## LEARNED FACTS (documentation, not a fix queue)

Worker W5 classified these as documentation or process rules. Kept for reference; no action expected.

- L74-75 event probability layer: parked until labels >= 500.
- L87-95 state-machine counters survive restart: documentation.
- L101 proof_direction rule: existing code, documentation.
- L104 single-value error: process rule for reads.
- L105 verify-by-read: process rule.
- L107 live-analysis support baseline: documentation.
- L108 MTS-LIVE vs LIVE: documentation.
- L114 log tail is not a health check: process rule.
- L117 PowerShell quoting lesson: process rule.
- L119 verify method lesson: process rule.

## 2026-10-14 JIS-NB build defect and paste defects

Build FAIL on JIS-NB: Maven ran under JDK 11 while pom.xml sets
maven.compiler.source/target = 17. javac refused with
'invalid target release: 17' before parsing any source. Not a code
defect; the 2026-10-14 01:29 edit to SpikeFadeDetector,
SetupCandidatesBuilder, MarketDataSnapshot and the two SpikeFade
tests is not implicated.

Fix landed on JIS-NB:
- User and Machine JAVA_HOME -> C:\Users\E-ngineers\Java\jdk-17.0.20.1+1
- Machine PATH: removed the jdk-11.0.7\bin entry
- JDK 11 unregistered through its MSI (Java SE Development Kit
  11.0.7 64-bit); folder C:\Program Files\Java\jdk-11.0.7 removed
- Proof: mvn compile exit 0 with
  C:\Users\E-ngineers\Maven\apache-maven-3.6.3\bin\mvn.cmd
- Residue: a running AIBridge agent still holds the old JAVA_HOME
  string in its inherited environment. Restart the agent, or set
  JAVA_HOME at Process scope for the turn.

Paste defects this session (boot paste carried a NUC report while
the session ran on JIS-NB):
- BUILD_REPORT.md header says host: JIS-NUC, bridge is JIS-NB.
- Boot loop health line (java_absent, supervisor_absent, snapshot
  missing) describes JIS-NUC, not JIS-NB.
- section 9 gives Maven at D:\tools\apache-maven-3.9.14; that path
  does not exist on JIS-NB. Actual Maven on JIS-NB:
  C:\Users\E-ngineers\Maven\apache-maven-3.6.3\bin\mvn.cmd.
