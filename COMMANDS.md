# COMMANDS

## LIVE ALIASES (dot-source once per session)

    . .\scripts\load.ps1

    lx  quick read (price, snap, CVD, state, last verdict)   cadence: 1-2 min
    ld  1m bar deltas                                        cadence: 1-2 min
    lt  15-cycle trend                                       cadence: 15-30 min
    lf  full snapshot fields                                 on demand
    lh  health (java, state_code, log tail)                  when suspicious
    la  recent alerts                                        on alert fire
    lc  decision combo (everything for a call)               at decision points

---
# COMMANDS — MTS / BinanceDataFeed
# Purpose: the commands actually used. Reference, not tutorial.
# Last updated: 2026-09-13.

## 0. FIRST — read these two files if context is lost
- MyTradingSys\SESSION_ENTRY.md
- MyTradingSys\mts\research\apparatus_fixes.md

## 1. DAILY LOOP — start / stop / read

Start apparatus (armed = 1min cadence):
  cd C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed
  .\scripts\core\mode.ps1 -M armed

Other modes:
  .\scripts\core\mode.ps1 -M prep
  .\scripts\core\mode.ps1 -M live -Dir short -E 77100 -S 77200 -T 76835

Stop everything:
  .\scripts\core\stop-day.ps1

Watch live verdicts (tail):
  Get-Content .\data\apparatus_log.txt -Encoding UTF8 -Tail 15

Read current thesis:
  python .\MyTradingSys\mts\runtime\session_state.py show

Read recent decisions:
  python .\MyTradingSys\mts\runtime\session_state.py log

Log a decision (one line):
  python .\MyTradingSys\mts\runtime\log_decision.py passed "reason" --alert 224

## 2. FETCH — snapshots

Single fresh snapshot (most common):
  mvn -q exec:java "-Dexec.mainClass=datafeed.Main" "-Dexec.args=snapshot BTCUSDT"

Multi-symbol:
  mvn -q exec:java "-Dexec.mainClass=datafeed.Main" "-Dexec.args=snapshot BTCUSDT ETHUSDT"

Historical (specific timestamp):
  mvn -q exec:java "-Dexec.mainClass=datafeed.Main" "-Dexec.args=historical BTCUSDT 2026-09-13T10:00:00Z"

Live state emitter (60s loop, spawns java child — used by apparatus, not manually):
  mvn -q exec:java "-Dexec.mainClass=datafeed.Main" "-Dexec.args=statemachine BTCUSDT"

Auto-snapshot daemon (00:05 UTC daily):
  mvn -q exec:java "-Dexec.mainClass=datafeed.Main" "-Dexec.args=scheduler BTCUSDT"

## 3. PROCESS — always in this order after fetch

  $R = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
  python "$R\MyTradingSys\mts\runtime\update_market_state.py"
  $latest = (Get-ChildItem "$R\data\snapshots\BTCUSDT_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
  python "$R\MyTradingSys\mts\runtime\build_mo_cli.py" $latest "$env:TEMP\mo.json"

Apparatus does these automatically each cycle.

## 4. ANALYZE

Quad classification (positioning + flow — new_longs / short_cover / etc):
  python .\MyTradingSys\mts\runtime\quad_classify.py

Backfill forward-return labels (idempotent):
  python .\MyTradingSys\mts\runtime\outcome_labeler.py

State code (Java emitter output, live flow A/S/L):
  Get-Content .\MyTradingSys\mts\runtime\state_code.json -Raw

## 5. DIAGNOSTICS — when something looks wrong

Is apparatus running?
  Get-Process java -ErrorAction SilentlyContinue | Select-Object Id, StartTime
  Get-Content .\data\apparatus.lock

How old is the state code? (should be <60s)
  $sc = Get-Content .\MyTradingSys\mts\runtime\state_code.json -Raw | ConvertFrom-Json
  [Math]::Round(((Get-Date).ToUniversalTime() - [datetime]::Parse($sc.timestamp_utc).ToUniversalTime()).TotalSeconds, 0)

How old is current_market_state.md?
  (Get-Item .\MyTradingSys\mts\runtime\current_market_state.md).LastWriteTime

Two apparatus running? (should be one)
  Get-Process powershell -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -match "start_trading" }

Two java running? (should be one — the state machine child)
  Get-Process java -ErrorAction SilentlyContinue

Kill everything cleanly:
  .\scripts\core\stop-day.ps1

Verify critical files exist and are current:
  Get-ChildItem .\MyTradingSys\SESSION_ENTRY.md, .\MyTradingSys\mts\research\apparatus_fixes.md,
                .\MyTradingSys\mts\runtime\session_state.json,
                .\MyTradingSys\mts\runtime\session_log.json,
                .\data\outcome_labels.json | Select-Object Name, Length, LastWriteTime

Counts (sanity):
  (Get-ChildItem .\data\snapshots\BTCUSDT_*.json).Count          # rolling 200
  (Get-Content .\MyTradingSys\mts\runtime\session_log.json -Raw | ConvertFrom-Json).events.Count
  (Get-Content .\data\outcome_labels.json -Raw | ConvertFrom-Json).labels.Count
  Get-Content .\data\alert_counter.txt

Last alert payload (the popup that just fired):
  Get-Content .\data\last_alert.json -Raw | ConvertFrom-Json | Select-Object title, body, card_text

Check for session_log append failures:
  Get-Content .\data\apparatus_log.txt -Encoding UTF8 | Select-String "append failed"

## 6. SNAPSHOT READ (one-off, no processing)

  $R = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
  $s = Get-ChildItem "$R\data\snapshots\BTCUSDT_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  $j = Get-Content $s.FullName -Raw | ConvertFrom-Json
  "price:   $($j.current_price)"
  "state:   $($j.conditions.vp_shape)/$($j.conditions.price_vs_va)"
  "vwap:    $($j.vwap.price) | $($j.vwap.slope)"
  "cvd:     $($j.cvd.value) | $($j.cvd.slope) | 1h $($j.cvd.cvd_recent.slope_1h)"
  "flow15m: $($j.trade_flow.net_delta_15m)"
  "oi:      $($j.open_interest.direction) ($($j.open_interest.change_1h_pct)%)"
  "book:    $($j.order_book_depth.bid_ask_ratio)"

## 7. JAVA COMPILE (after any .java edit)

  mvn -q -DskipTests compile

## 8. PYTHON TESTS (after any runtime .py edit)

  cd C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed
  python -m pytest .\MyTradingSys\mts\tests\ -q

## 9. DUMP REGEN (for AI-worker context)

  .\scripts\Dump_All.ps1
  # writes to .\Dumps\kimi_*_dump.md

## 10. FILE RESTORE — if a change must be rolled back

Backups live at project root: backup_YYYYMMDD_HHMMSS\
Retention: 1 most recent.
  Get-ChildItem .\backup_* -Directory
  # copy the file you want back FROM the backup dir TO its original path

## 11. HARD RULES — do not violate

- Do NOT run Get-Process java | Stop-Process. Java is the state machine child.
  Use .\scripts\core\stop-day.ps1 or .\scripts\core\mode.ps1. Never bare-kill java.
- Do NOT start .\scripts\core\mode.ps1 twice without stopping first. mode.ps1 kills + restarts.
- Do NOT edit critical files without hash-before / hash-after / diff.
  See DSA_SESSION_PROMPT.md "CRITICAL FILES" section.
- Do NOT read the full 12-file dump unless explicitly asked. Use SESSION_ENTRY.md.

# END
